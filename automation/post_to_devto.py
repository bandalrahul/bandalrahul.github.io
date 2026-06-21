#!/usr/bin/env python3
"""Cross-post the latest blog article to Dev.to after site deploy."""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "Content" / "posts"
DEVTO_PUBLISHED_FILE = ROOT / "automation" / "devto-published.json"
SITE_URL = "https://www.swiftbyrahul.com"
DEVTO_API_URL = "https://dev.to/api/articles"
URL_VERIFY_ATTEMPTS = 6
URL_VERIFY_DELAY_SECONDS = 10
DEFAULT_TAGS = ["swift", "ios", "programming"]
MAX_TAGS = 4


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    trimmed = text.lstrip()
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", trimmed, re.DOTALL)
    if not match:
        raise ValueError("Missing YAML front matter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    body = trimmed[match.end() :].lstrip("\n")
    return fields, body


def extract_title(text: str, meta: dict[str, str]) -> str:
    if meta.get("title"):
        return meta["title"]
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    raise ValueError("Post missing title in front matter or heading")


def parse_post_date(date_str: str) -> datetime:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {date_str}")


def latest_post_path() -> Path:
    candidates: list[tuple[datetime, Path]] = []
    for path in POSTS_DIR.glob("*.md"):
        if path.name == "index.md":
            continue
        text = path.read_text(encoding="utf-8")
        try:
            meta, _ = parse_front_matter(text)
        except ValueError:
            continue
        if "date" not in meta:
            continue
        try:
            candidates.append((parse_post_date(meta["date"]), path))
        except ValueError:
            continue
    if not candidates:
        raise RuntimeError("No blog posts found in Content/posts/")
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def post_url_for_slug(slug: str) -> str:
    return f"{SITE_URL}/posts/{slug}/"


def cover_image_url(slug: str) -> str:
    return f"{SITE_URL}/images/posts/{slug}.png"


def verify_live_url(url: str) -> None:
    for attempt in range(1, URL_VERIFY_ATTEMPTS + 1):
        request = urllib.request.Request(url, method="HEAD")
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                if response.status == 200:
                    print(f"Verified live URL: {url}")
                    return
        except urllib.error.HTTPError as error:
            if error.code == 200:
                return
            print(f"URL check attempt {attempt}/{URL_VERIFY_ATTEMPTS} failed ({error.code})")
        except urllib.error.URLError as error:
            print(f"URL check attempt {attempt}/{URL_VERIFY_ATTEMPTS} failed ({error.reason})")

        if attempt < URL_VERIFY_ATTEMPTS:
            time.sleep(URL_VERIFY_DELAY_SECONDS)

    raise RuntimeError(f"Article URL is not live yet: {url}")


def normalize_devto_tag(tag: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]", "", tag.strip().lower())
    return cleaned[:30]


def devto_tags(meta: dict[str, str]) -> list[str]:
    raw = meta.get("tags", "")
    tags = [normalize_devto_tag(part) for part in re.split(r"[,;]", raw)]
    tags = [tag for tag in tags if tag]
    if not tags:
        tags = DEFAULT_TAGS.copy()
    deduped: list[str] = []
    for tag in tags:
        if tag not in deduped:
            deduped.append(tag)
    return deduped[:MAX_TAGS]


def strip_duplicate_title(body: str, title: str) -> str:
    lines = body.splitlines()
    if not lines:
        return body
    first = lines[0].strip()
    if first == f"# {title}":
        return "\n".join(lines[1:]).lstrip("\n")
    return body


def build_body_markdown(body: str, title: str, canonical_url: str) -> str:
    trimmed = strip_duplicate_title(body, title)
    footer = (
        f"\n\n---\n\n"
        f"*Originally published at [{canonical_url}]({canonical_url}) "
        f"on [Swift By Rahul]({SITE_URL}).*"
    )
    return trimmed + footer


def already_posted(slug: str) -> bool:
    published = load_json(DEVTO_PUBLISHED_FILE).get("published", {})
    return slug in published


def record_publication(slug: str, article: dict) -> None:
    data = load_json(DEVTO_PUBLISHED_FILE)
    published = data.setdefault("published", {})
    published[slug] = {
        "devto_id": article.get("id"),
        "url": article.get("url"),
        "posted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_json(DEVTO_PUBLISHED_FILE, data)


def devto_api_key() -> str:
    api_key = os.environ.get("DEVTO_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Set DEVTO_API_KEY environment variable.")
    return api_key


def create_devto_article(payload: dict) -> dict:
    api_key = devto_api_key()

    body = json.dumps({"article": payload}).encode("utf-8")
    request = urllib.request.Request(
        DEVTO_API_URL,
        data=body,
        method="POST",
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Dev.to API failed ({error.code}): {detail}") from error

    if "error" in result:
        raise RuntimeError(f"Dev.to API error: {result['error']}")
    if not result.get("url"):
        raise RuntimeError(f"Unexpected Dev.to response: {result}")
    return result


def build_article_payload(post_path: Path) -> dict[str, object]:
    text = post_path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(text)
    title = extract_title(text, meta)
    slug = post_path.stem
    canonical_url = post_url_for_slug(slug)
    description = meta.get("description", "")

    return {
        "title": title,
        "body_markdown": build_body_markdown(body, title, canonical_url),
        "published": True,
        "canonical_url": canonical_url,
        "description": description,
        "main_image": cover_image_url(slug),
        "tags": devto_tags(meta),
        "slug": slug,
    }


def post_latest_to_devto() -> str:
    post_path = latest_post_path()
    payload = build_article_payload(post_path)
    slug = str(payload.pop("slug"))
    url = post_url_for_slug(slug)

    if already_posted(slug):
        print(f"Already posted to Dev.to: {slug}")
        return url

    verify_live_url(url)
    print(f"Cross-posting to Dev.to: {payload['title']}")
    article = create_devto_article(payload)
    record_publication(slug, article)
    print(f"Published to Dev.to: {article['url']}")
    return article["url"]


def main() -> int:
    if not os.environ.get("DEVTO_API_KEY", "").strip():
        print("DEVTO_API_KEY is not set. Skipping Dev.to cross-post.")
        return 0

    post_latest_to_devto()
    return 0


if __name__ == "__main__":
    sys.exit(main())
