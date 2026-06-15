#!/usr/bin/env python3
"""Convert the first inline SVG in each post to a PNG for social sharing."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "Content" / "posts"
OUTPUT_DIR = ROOT / "Output" / "images" / "posts"
DEFAULT_IMAGE = ROOT / "Resources" / "Images" / "og-default.png"
SVG_PATTERN = re.compile(r"<svg[\s\S]*?</svg>", re.IGNORECASE)


def ensure_default_image() -> None:
    DEFAULT_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    if DEFAULT_IMAGE.exists():
        return

    from PIL import Image, ImageDraw, ImageFont

    width, height = 1200, 630
    image = Image.new("RGB", (width, height), "#2A8367")
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 40, width - 40, height - 40), outline="#1565c0", width=4)
    draw.text((80, 220), "Swift By Rahul", fill="white")
    draw.text((80, 300), "Swift & iOS Development", fill="#E8F5E9")
    draw.text((80, 380), "swiftbyrahul.com", fill="#B2DFDB")
    image.save(DEFAULT_IMAGE, format="PNG")
    print(f"Created default social image at {DEFAULT_IMAGE.relative_to(ROOT)}")


def extract_first_svg(markdown: str) -> str | None:
    match = SVG_PATTERN.search(markdown)
    if not match:
        return None
    svg = match.group(0)
    if 'xmlns="http://www.w3.org/2000/svg"' not in svg:
        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    return svg


def svg_to_png(svg: str, output_path: Path) -> None:
    import cairosvg

    cairosvg.svg2png(
        bytestring=svg.encode("utf-8"),
        write_to=str(output_path),
        output_width=1200,
        output_height=630,
    )


def generate_for_post(post_path: Path) -> Path:
    slug = post_path.stem
    output_path = OUTPUT_DIR / f"{slug}.png"
    markdown = post_path.read_text(encoding="utf-8")
    svg = extract_first_svg(markdown)

    if svg:
        try:
            svg_to_png(svg, output_path)
            print(f"Generated social image for {slug}")
            return output_path
        except Exception as error:
            print(f"SVG conversion failed for {slug}: {error}")

    shutil.copy2(DEFAULT_IMAGE, output_path)
    print(f"Used default social image for {slug}")
    return output_path


def main() -> int:
    ensure_default_image()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    posts = sorted(
        path for path in POSTS_DIR.glob("*.md") if path.name != "index.md"
    )
    if not posts:
        print("No posts found.")
        return 0

    for post_path in posts:
        generate_for_post(post_path)

    default_output = ROOT / "Output" / "images" / "og-default.png"
    default_output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DEFAULT_IMAGE, default_output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
