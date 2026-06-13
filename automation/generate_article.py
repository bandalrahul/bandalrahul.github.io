#!/usr/bin/env python3
"""Generate a daily Swift/iOS blog article using the Google Gemini API."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    print("Missing dependency: pip install google-generativeai")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "Content" / "posts"
TOPICS_FILE = ROOT / "automation" / "topics.json"
PUBLISHED_FILE = ROOT / "automation" / "published-topics.json"
SYSTEM_INSTRUCTION = (
    "You are an expert Swift and iOS developer who writes accurate, "
    "high-quality technical blog posts. Output only markdown."
)


def load_json(path: Path) -> dict | list:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, data: dict | list) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def slugify(title: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", title)
    if not words:
        raise ValueError(f"Cannot slugify title: {title}")
    return "".join(word.capitalize() for word in words)


def existing_post_titles() -> list[str]:
    titles: list[str] = []
    for path in POSTS_DIR.glob("*.md"):
        if path.name == "index.md":
            continue
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
        if match:
            titles.append(match.group(1).strip())
    return titles


def post_exists_for_today() -> bool:
    today = datetime.now().strftime("%Y-%m-%d")
    for path in POSTS_DIR.glob("*.md"):
        if path.name == "index.md":
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(rf"^date:\s*{today}", text, re.MULTILINE):
            return True
    return False


def pick_topic() -> dict:
    topics = load_json(TOPICS_FILE)
    published = set(load_json(PUBLISHED_FILE).get("published", []))
    available = [topic for topic in topics if topic["id"] not in published]
    if not available:
        raise RuntimeError("All topics have been published. Add more topics to automation/topics.json")
    return available[0]


def build_prompt(topic: dict, avoid_titles: list[str]) -> str:
    avoid_list = "\n".join(f"- {title}" for title in avoid_titles) or "- None"
    tag_line = ", ".join(topic["tags"])
    return f"""Write a complete blog article for a Swift/iOS developer blog called "Swift By Rahul".

Topic: {topic["title"]}
Required tags: {tag_line}

Rules:
- Content must be ONLY about Swift, iOS, macOS, watchOS, or Apple platform development
- Write for intermediate iOS developers
- Include practical Swift code examples in fenced ```swift blocks
- Use clear markdown headings (## and ###)
- Length: 900-1400 words
- Tone: tutorial-style, clear, accurate, friendly
- Do NOT write about these existing topics:
{avoid_list}
- Do NOT include HTML unless necessary; prefer markdown
- Do NOT wrap the response in markdown code fences
- Verify Swift APIs you mention are real and current
- End with a short "Summary" section and sign off with "Happy Swifting!"

Return ONLY the full markdown file including YAML front matter in this exact format:

---
title: {topic["title"]}
date: {datetime.now().strftime("%Y-%m-%d %H:%M")}
description: <1-2 sentence SEO description under 200 characters>
tags: {tag_line}
---

# {topic["title"]}

<article body>
"""


def strip_code_fences(content: str) -> str:
    trimmed = content.strip()
    match = re.match(r"^```(?:markdown|md)?\s*\n(.*)\n```\s*$", trimmed, re.DOTALL)
    if match:
        return match.group(1).strip()
    return trimmed


def generate_article(topic: dict, avoid_titles: list[str]) -> str:
    configured_model = os.environ.get("GEMINI_MODEL")
    model_names = [configured_model] if configured_model else [
        "gemini-1.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
    ]
    model_names = [name for name in model_names if name]

    prompt = build_prompt(topic, avoid_titles)
    errors: list[str] = []

    for model_name in model_names:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_INSTRUCTION,
            )
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.7),
            )

            if not response.candidates:
                errors.append(f"{model_name}: no candidates returned")
                continue

            content = response.text
            if not content:
                errors.append(f"{model_name}: empty response")
                continue

            print(f"Generated article using model: {model_name}")
            return strip_code_fences(content)
        except Exception as error:
            errors.append(f"{model_name}: {error}")
            continue

    joined_errors = "\n".join(errors)
    raise RuntimeError(f"All Gemini models failed:\n{joined_errors}")


def validate_markdown(content: str) -> None:
    if not content.startswith("---"):
        raise ValueError("Generated content is missing YAML front matter")
    if "# " not in content:
        raise ValueError("Generated content is missing a title heading")
    if "```swift" not in content:
        raise ValueError("Generated content is missing Swift code examples")


def extract_title(content: str) -> str:
    match = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
    if not match:
        raise ValueError("Front matter title is missing")
    return match.group(1).strip()


def main() -> int:
    if post_exists_for_today():
        print("Article for today already exists. Skipping.")
        return 0

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable is required.")
        return 1

    genai.configure(api_key=api_key)

    topic = pick_topic()
    avoid_titles = existing_post_titles()

    print(f"Generating article for topic: {topic['title']}")
    markdown = generate_article(topic, avoid_titles)
    validate_markdown(markdown)

    title = extract_title(markdown)
    slug = slugify(title)
    output_path = POSTS_DIR / f"{slug}.md"

    if output_path.exists():
        raise RuntimeError(f"Post file already exists: {output_path.name}")

    output_path.write_text(markdown + "\n", encoding="utf-8")
    print(f"Wrote {output_path.relative_to(ROOT)}")

    published = load_json(PUBLISHED_FILE)
    published.setdefault("published", []).append(topic["id"])
    save_json(PUBLISHED_FILE, published)
    print(f"Marked topic as published: {topic['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
