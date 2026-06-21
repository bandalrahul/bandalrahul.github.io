# Daily Blog Automation

This folder powers fully automated daily publishing for [Swift By Rahul](https://www.swiftbyrahul.com).

## What it does

Every day at **09:00 UTC**, GitHub Actions will:

1. Pick an unused Swift/iOS topic from `topics.json`
2. Generate a new article with Google Gemini (free tier)
3. Save it to `Content/posts/`
4. Build the site with Publish
5. Deploy to the `master` branch (GitHub Pages)
6. Commit the new markdown back to `main`

## One-time setup

### 1. Add a free AI API key

Use **one or both** providers below.

#### Option A: Google Gemini (recommended)

Get a free key at [Google AI Studio](https://aistudio.google.com/apikey).

| Name | Value |
|------|-------|
| `GEMINI_API_KEY` | Your Google Gemini API key |

Optional variable:

| Name | Value |
|------|-------|
| `GEMINI_MODEL` | Override default Gemini model |

#### Option B: Groq (free backup)

If Gemini quota fails, add a free Groq key from [console.groq.com](https://console.groq.com).

| Name | Value |
|------|-------|
| `GROQ_API_KEY` | Your Groq API key |

The workflow tries **Gemini first**, then **Groq** automatically.

### 2. Social preview images

After the site build, CI runs `automation/generate_social_images.py` to create **1200×630** PNGs under `Output/images/posts/` from each article’s first inline SVG (or copy `Resources/Images/og-default.png` when there is no SVG). These images are used for Open Graph / Twitter card previews on article pages.

Local test (macOS):

```bash
brew install cairo
pip install -r automation/requirements.txt
python automation/generate_social_images.py
```

### 3. Enable GitHub Actions

Ensure Actions are enabled for the repository:

**Settings → Actions → General → Allow all actions**

### 4. Push this code to `main`

The workflow file lives at `.github/workflows/daily-post.yml`.

### 5. Test manually

Go to **Actions → Daily Swift Blog Post → Run workflow**.

## Topic management

- **`topics.json`** — pool of **1,100+** Swift/iOS topics
- **`published-topics.json`** — tracks which topics were used

When all topics are used, add more entries to `topics.json`.

Existing manual posts are pre-marked in `published-topics.json` to reduce overlap.

## Safety checks

- Skips if a post with today's date already exists
- Validates front matter, Swift code blocks, SVG diagrams, and ASCII diagrams before saving
- Avoids regenerating titles already on the blog
- Only generates Swift / iOS / Apple platform content
- Each article includes **2+ SVG diagrams** and **1+ ASCII diagram** for visual learning

## Cost

Google Gemini free tier covers daily blog generation at no cost for typical usage.

## Disable automation

Pause the schedule by deleting or disabling `.github/workflows/daily-post.yml`, or disable the workflow in the GitHub Actions UI.

## Local test

```bash
export GEMINI_API_KEY="your-key-here"
pip install -r automation/requirements.txt
python automation/generate_article.py
swift run PublishSBR
swift run PublishSBR --deploy
```
