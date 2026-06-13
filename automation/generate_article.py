#!/usr/bin/env python3
"""Generate a daily Swift/iOS blog article using free AI APIs."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "Content" / "posts"
TOPICS_FILE = ROOT / "automation" / "topics.json"
PUBLISHED_FILE = ROOT / "automation" / "published-topics.json"
SYSTEM_INSTRUCTION = (
    "You are an expert Swift and iOS developer who writes accurate, "
    "high-quality technical blog posts with clear inline SVG diagrams. "
    "Output markdown with embedded HTML/SVG visuals where specified."
)

VISUAL_GUIDELINES = """
Visual content requirements (VERY IMPORTANT):
- Include at least 2 inline SVG diagrams and 1 ASCII diagram
- SVG diagrams must be wrapped exactly like this:

<div style="text-align: center; margin: 2em 0;">
<svg viewBox="0 0 600 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Short description">
  <title>Short description</title>
  <!-- simple shapes, labels, arrows; use blog colors #2A8367 green, #F04B3E red, #1565c0 blue -->
</svg>
</div>

- SVG rules:
  - Self-contained (no external images or scripts)
  - Use viewBox for responsive scaling
  - Include role="img", aria-label, and <title>
  - Label all boxes/text clearly
  - Prefer flowcharts, comparison diagrams, architecture boxes, before/after visuals
  - Use simple rects, circles, lines, and text only

- ASCII diagram example (put in a plain fenced code block, not swift):

```
┌─────────────┐     ┌─────────────┐
│   View      │ ──► │  ViewModel  │
└─────────────┘     └─────────────┘
```

- Place one SVG after the introduction and one SVG in the middle of the article
- Add a comparison or flow diagram before the Summary section when helpful
- Do NOT use external image URLs (no hotlinked photos)
- Do NOT use Mermaid — use SVG or ASCII only
"""
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash",
]
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]


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
- Length: 900-1300 words (excluding SVG/ASCII diagrams)
- Tone: tutorial-style, clear, accurate, friendly
- Do NOT write about these existing topics:
{avoid_list}
- Use markdown for text; use inline HTML only for SVG diagram wrappers
- Do NOT wrap the entire response in markdown code fences
- Verify Swift APIs you mention are real and current
- End with a short "Summary" section and sign off with "Happy Swifting!"

{VISUAL_GUIDELINES}

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


def generate_with_gemini(prompt: str) -> str:
    import google.generativeai as genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    genai.configure(api_key=api_key)
    configured_model = os.environ.get("GEMINI_MODEL")
    model_names = [configured_model] if configured_model else GEMINI_MODELS
    model_names = [name for name in model_names if name]
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
            print(f"Generated article using Gemini model: {model_name}")
            return strip_code_fences(content)
        except Exception as error:
            errors.append(f"{model_name}: {error}")

    raise RuntimeError("Gemini failed:\n" + "\n".join(errors))


def generate_with_groq(prompt: str) -> str:
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    configured_model = os.environ.get("GROQ_MODEL")
    model_names = [configured_model] if configured_model else GROQ_MODELS
    model_names = [name for name in model_names if name]
    client = Groq(api_key=api_key)
    errors: list[str] = []

    for model_name in model_names:
        try:
            response = client.chat.completions.create(
                model=model_name,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content
            if not content:
                errors.append(f"{model_name}: empty response")
                continue
            print(f"Generated article using Groq model: {model_name}")
            return strip_code_fences(content)
        except Exception as error:
            errors.append(f"{model_name}: {error}")

    raise RuntimeError("Groq failed:\n" + "\n".join(errors))


def generate_article(topic: dict, avoid_titles: list[str]) -> str:
    prompt = build_prompt(topic, avoid_titles)
    errors: list[str] = []

    if os.environ.get("GEMINI_API_KEY"):
        try:
            return generate_with_gemini(prompt)
        except Exception as error:
            errors.append(str(error))

    if os.environ.get("GROQ_API_KEY"):
        try:
            return generate_with_groq(prompt)
        except Exception as error:
            errors.append(str(error))

    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GROQ_API_KEY"):
        raise RuntimeError("Set GEMINI_API_KEY and/or GROQ_API_KEY")

    raise RuntimeError("All AI providers failed:\n\n" + "\n\n".join(errors))


def validate_markdown(content: str) -> None:
    if not content.startswith("---"):
        raise ValueError("Generated content is missing YAML front matter")
    if "# " not in content:
        raise ValueError("Generated content is missing a title heading")
    if "```swift" not in content:
        raise ValueError("Generated content is missing Swift code examples")
    if content.count("<svg") < 2:
        raise ValueError("Generated content must include at least 2 SVG diagrams")
    if "aria-label=" not in content:
        raise ValueError("SVG diagrams must include aria-label for accessibility")
    if "┌" not in content and "->" not in content and "──" not in content:
        raise ValueError("Generated content must include at least 1 ASCII diagram")


def extract_title(content: str) -> str:
    match = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
    if not match:
        raise ValueError("Front matter title is missing")
    return match.group(1).strip()


def main() -> int:
    if post_exists_for_today():
        print("Article for today already exists. Skipping.")
        return 0

    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GROQ_API_KEY"):
        print("Set GEMINI_API_KEY and/or GROQ_API_KEY.")
        return 1

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
