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
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
DEVTO_HEADERS = {
    "Accept": "application/vnd.forem.api-v1+json",
    "Content-Type": "application/json",
    "User-Agent": USER_AGENT,
}


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
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
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


def strip_non_prose_blocks(text: str) -> str:
    without_html = re.sub(r"<div[\s\S]*?</div>", "", text, flags=re.IGNORECASE)
    without_html = re.sub(r"<svg[\s\S]*?</svg>", "", without_html, flags=re.IGNORECASE)
    without_code = re.sub(r"```[\s\S]*?```", "", without_html)
    without_headings = re.sub(r"^#+\s+.+$", "", without_code, flags=re.MULTILINE)
    return without_headings.strip()


def extract_teaser_excerpt(body: str, title: str, max_paragraphs: int = 2, max_chars: int = 550) -> str:
    trimmed = strip_duplicate_title(body, title)
    cleaned = strip_non_prose_blocks(trimmed)
    paragraphs: list[str] = []

    for block in re.split(r"\n\s*\n", cleaned):
        block = block.strip()
        if not block:
            continue
        if block.startswith(("- ", "* ", "|", "!", "[")):
            continue
        if block.startswith("```"):
            continue
        paragraphs.append(block)
        if len(paragraphs) >= max_paragraphs:
            break

    excerpt = "\n\n".join(paragraphs)
    if len(excerpt) > max_chars:
        excerpt = excerpt[:max_chars].rsplit(" ", 1)[0] + "…"
    return excerpt


def build_teaser_markdown(
    excerpt: str,
    canonical_url: str,
) -> str:
    sections: list[str] = []
    if excerpt:
        sections.append(excerpt)

    sections.append(
        "---\n\n"
        "**Read the full article on Swift By Rahul** → "
        f"[Continue reading]({canonical_url})\n\n"
        "The complete tutorial includes Swift code examples, SVG diagrams, "
        "and step-by-step explanations on our website."
    )
    return "\n\n".join(sections)


def build_body_markdown(
    body: str,
    title: str,
    description: str,
    canonical_url: str,
) -> str:
    excerpt = extract_teaser_excerpt(body, title)
    if not excerpt:
        excerpt = description
    return build_teaser_markdown(excerpt, canonical_url)


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
    headers = {**DEVTO_HEADERS, "api-key": api_key}
    request = urllib.request.Request(
        DEVTO_API_URL,
        data=body,
        method="POST",
        headers=headers,
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


def update_devto_article(article_id: int, payload: dict) -> dict:
    api_key = devto_api_key()
    url = f"{DEVTO_API_URL}/{article_id}"

    body = json.dumps({"article": payload}).encode("utf-8")
    headers = {**DEVTO_HEADERS, "api-key": api_key}
    request = urllib.request.Request(
        url,
        data=body,
        method="PUT",
        headers=headers,
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
        "body_markdown": build_body_markdown(body, title, description, canonical_url),
        "published": True,
        "canonical_url": canonical_url,
        "description": description,
        "main_image": cover_image_url(slug),
        "tags": devto_tags(meta),
        "slug": slug,
    }


def publish_payload_for_devto(payload: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in payload.items() if key != "slug"}


def post_latest_to_devto() -> str:
    post_path = latest_post_path()
    payload = build_article_payload(post_path)
    slug = str(payload.pop("slug"))
    url = post_url_for_slug(slug)
    devto_payload = publish_payload_for_devto(payload)

    verify_live_url(url)

    if already_posted(slug):
        record = load_json(DEVTO_PUBLISHED_FILE).get("published", {}).get(slug, {})
        devto_id = record.get("devto_id")
        if devto_id:
            print(f"Updating Dev.to teaser for: {payload['title']}")
            article = update_devto_article(int(devto_id), devto_payload)
            record_publication(slug, article)
            print(f"Updated Dev.to teaser: {article['url']}")
            return article["url"]
        print(f"Already posted to Dev.to: {slug}")
        return url

    print(f"Cross-posting teaser to Dev.to: {payload['title']}")
    article = create_devto_article(devto_payload)
    record_publication(slug, article)
    print(f"Published Dev.to teaser: {article['url']}")
    return article["url"]


def main() -> int:
    if not os.environ.get("DEVTO_API_KEY", "").strip():
        print("DEVTO_API_KEY is not set. Skipping Dev.to cross-post.")
        return 0

    post_latest_to_devto()
    return 0


if __name__ == "__main__":
    sys.exit(main())
