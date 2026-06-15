#!/usr/bin/env python3
"""Post the latest blog article to the Swift By Rahul Facebook Page."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "Content" / "posts"
SITE_URL = "https://www.swiftbyrahul.com"
GRAPH_API_VERSION = "v21.0"


def slugify(title: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", title)
    if not words:
        raise ValueError(f"Cannot slugify title: {title}")
    return "".join(word.capitalize() for word in words)


def parse_front_matter(text: str) -> dict[str, str]:
    trimmed = text.lstrip()
    match = re.match(r"^---\s*\n(.*?)\n---", trimmed, re.DOTALL)
    if not match:
        raise ValueError("Missing YAML front matter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


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
            meta = parse_front_matter(text)
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


def build_post_payload(post_path: Path) -> dict[str, str]:
    text = post_path.read_text(encoding="utf-8")
    meta = parse_front_matter(text)
    title = extract_title(text, meta)
    description = meta.get("description", "")

    slug = slugify(title)
    url = f"{SITE_URL}/posts/{slug}/"
    message = f"🚀 New on Swift By Rahul: {title}\n\n{description}"
    return {"message": message, "link": url, "title": title}


def post_to_facebook(payload: dict[str, str]) -> str:
    page_id = os.environ.get("FACEBOOK_PAGE_ID")
    access_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
    if not page_id or not access_token:
        raise RuntimeError(
            "Set FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN environment variables."
        )

    body = urllib.parse.urlencode(
        {
            "message": payload["message"],
            "link": payload["link"],
            "access_token": access_token,
        }
    ).encode("utf-8")
    api_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}/feed"
    request = urllib.request.Request(api_url, data=body, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Facebook API error ({error.code}): {detail}") from error

    post_id = result.get("id")
    if not post_id:
        raise RuntimeError(f"Unexpected Facebook response: {result}")
    return post_id


def main() -> int:
    post_path = latest_post_path()
    payload = build_post_payload(post_path)
    post_id = post_to_facebook(payload)
    print(f"Posted '{payload['title']}' to Facebook (post id: {post_id})")
    print(f"Link: {payload['link']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
