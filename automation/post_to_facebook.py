#!/usr/bin/env python3
"""Share the latest blog article on the Swift By Rahul Facebook Page."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "Content" / "posts"
OUTPUT_IMAGES_DIR = ROOT / "Output" / "images" / "posts"
FACEBOOK_PUBLISHED_FILE = ROOT / "automation" / "facebook-published.json"
SITE_URL = "https://www.swiftbyrahul.com"
GRAPH_API_VERSION = "v21.0"
URL_VERIFY_ATTEMPTS = 6
URL_VERIFY_DELAY_SECONDS = 10
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

DEFAULT_OG_IMAGE = ROOT / "Resources" / "Images" / "og-default.png"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


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


def post_url_for_slug(slug: str) -> str:
    return f"{SITE_URL}/posts/{slug}/"


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


def social_image_for_slug(slug: str) -> tuple[Path | None, str]:
    local_path = OUTPUT_IMAGES_DIR / f"{slug}.png"
    remote_url = f"{SITE_URL}/images/posts/{slug}.png"
    if local_path.exists():
        return local_path, remote_url
    return None, remote_url


def build_post_payload(post_path: Path) -> dict[str, str]:
    text = post_path.read_text(encoding="utf-8")
    meta = parse_front_matter(text)
    title = extract_title(text, meta)
    description = meta.get("description", "")
    slug = post_path.stem
    url = post_url_for_slug(slug)
    image_path, image_url = social_image_for_slug(slug)
    message = (
        f"🚀 New on Swift By Rahul: {title}\n\n"
        f"{description}\n\n"
        f"Read more: {url}"
    )
    return {
        "message": message,
        "link": url,
        "title": title,
        "slug": slug,
        "image_path": str(image_path) if image_path else "",
        "image_url": image_url,
    }


def facebook_credentials() -> tuple[str, str]:
    page_id = os.environ.get("FACEBOOK_PAGE_ID", "").strip()
    access_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
    if not page_id or not access_token:
        raise RuntimeError(
            "Set FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN environment variables."
        )
    return page_id, access_token


def facebook_configured() -> bool:
    return bool(
        os.environ.get("FACEBOOK_PAGE_ID", "").strip()
        and os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
    )


def already_posted(slug: str) -> bool:
    published = load_json(FACEBOOK_PUBLISHED_FILE).get("published", {})
    return slug in published


def record_publication(slug: str, post_id: str) -> None:
    data = load_json(FACEBOOK_PUBLISHED_FILE)
    published = data.setdefault("published", {})
    published[slug] = {
        "post_id": post_id,
        "posted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_json(FACEBOOK_PUBLISHED_FILE, data)


def verify_page_access(page_id: str, access_token: str) -> None:
    api_url = (
        f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}"
        f"?fields=id,name&{urllib.parse.urlencode({'access_token': access_token})}"
    )
    request = urllib.request.Request(api_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            "Facebook Page token validation failed. "
            "Use a Page access token from GET /me/accounts with "
            "pages_manage_posts and pages_read_engagement permissions. "
            f"API response ({error.code}): {detail}"
        ) from error

    if str(result.get("id")) != str(page_id):
        raise RuntimeError(
            f"Token is not valid for Page ID {page_id}. "
            "Copy the access_token for your Page from GET /me/accounts."
        )
    print(f"Verified Facebook Page access: {result.get('name', page_id)}")


def parse_facebook_response(raw: bytes) -> dict:
    result = json.loads(raw.decode("utf-8"))
    if "error" in result:
        raise RuntimeError(f"Facebook API error: {result['error']}")
    return result


def post_photo_with_message(
    page_id: str,
    access_token: str,
    message: str,
    image_path: Path,
) -> str:
    boundary = f"----CursorFormBoundary{uuid.uuid4().hex}"
    mime_type = mimetypes.guess_type(image_path.name)[0] or "image/png"
    file_bytes = image_path.read_bytes()

    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="message"\r\n\r\n',
            message.encode("utf-8"),
            b"\r\n",
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="published"\r\n\r\n'.encode(),
            b"true\r\n",
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="source"; '
                f'filename="{image_path.name}"\r\n'
            ).encode(),
            f"Content-Type: {mime_type}\r\n\r\n".encode(),
            file_bytes,
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )

    api_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}/photos"
    query = urllib.parse.urlencode({"access_token": access_token})
    request = urllib.request.Request(
        f"{api_url}?{query}",
        data=body,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = parse_facebook_response(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Facebook photo upload failed ({error.code}): {detail}") from error

    post_id = result.get("post_id") or result.get("id")
    if not post_id:
        raise RuntimeError(f"Unexpected Facebook photo response: {result}")
    return str(post_id)


def post_link(
    page_id: str,
    access_token: str,
    message: str,
    link: str,
) -> str:
    body = urllib.parse.urlencode(
        {
            "message": message,
            "link": link,
            "access_token": access_token,
        }
    ).encode("utf-8")
    api_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}/feed"
    request = urllib.request.Request(api_url, data=body, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = parse_facebook_response(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Facebook link post failed ({error.code}): {detail}") from error

    post_id = result.get("id")
    if not post_id:
        raise RuntimeError(f"Unexpected Facebook response: {result}")
    return str(post_id)


def delete_facebook_post(post_id: str) -> None:
    _, access_token = facebook_credentials()
    query = urllib.parse.urlencode({"access_token": access_token})
    api_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{post_id}?{query}"
    request = urllib.request.Request(api_url, method="DELETE")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = parse_facebook_response(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Facebook delete failed ({error.code}): {detail}") from error
    if not result.get("success"):
        raise RuntimeError(f"Could not delete Facebook post {post_id}: {result}")
    print(f"Deleted Facebook post {post_id}")


def post_to_facebook(payload: dict[str, str]) -> str:
    page_id, access_token = facebook_credentials()
    verify_page_access(page_id, access_token)
    verify_live_url(payload["link"])

    image_path = Path(payload["image_path"]) if payload["image_path"] else None
    if not image_path or not image_path.exists():
        if DEFAULT_OG_IMAGE.exists():
            image_path = DEFAULT_OG_IMAGE

    if image_path and image_path.exists():
        print(f"Posting with image upload: {image_path.name}")
        try:
            return post_photo_with_message(
                page_id,
                access_token,
                payload["message"],
                image_path,
            )
        except RuntimeError as error:
            print(f"Image upload failed, falling back to link post: {error}")

    print(f"Posting link preview: {payload['link']}")
    return post_link(
        page_id,
        access_token,
        payload["message"],
        payload["link"],
    )


def share_latest_to_facebook() -> str:
    post_path = latest_post_path()
    payload = build_post_payload(post_path)
    slug = payload["slug"]

    if already_posted(slug):
        print(f"Already shared on Facebook: {slug}")
        return payload["link"]

    post_id = post_to_facebook(payload)
    record_publication(slug, post_id)
    print(f"Posted '{payload['title']}' to Facebook (post id: {post_id})")
    print(f"Link: {payload['link']}")
    return payload["link"]


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--delete":
        if len(sys.argv) != 3:
            print("Usage: post_to_facebook.py --delete POST_ID")
            return 1
        delete_facebook_post(sys.argv[2])
        return 0

    if not facebook_configured():
        print("Facebook credentials not set. Skipping Facebook share.")
        return 0

    share_latest_to_facebook()
    return 0


if __name__ == "__main__":
    sys.exit(main())
