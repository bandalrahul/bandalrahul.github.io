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

### 1. Add your Gemini API key

Get a free key at [Google AI Studio](https://aistudio.google.com/apikey).

In GitHub repo settings:

**Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|------|-------|
| `GEMINI_API_KEY` | Your Google Gemini API key |

Optional variable (not secret):

| Name | Value |
|------|-------|
| `GEMINI_MODEL` | `gemini-1.5-flash` (default, with automatic fallbacks) |

### 2. Enable GitHub Actions

Ensure Actions are enabled for the repository:

**Settings → Actions → General → Allow all actions**

### 3. Push this code to `main`

The workflow file lives at `.github/workflows/daily-post.yml`.

### 4. Test manually

Go to **Actions → Daily Swift Blog Post → Run workflow**.

## Topic management

- **`topics.json`** — pool of Swift/iOS topics (100+ included)
- **`published-topics.json`** — tracks which topics were used

When all topics are used, add more entries to `topics.json`.

Existing manual posts are pre-marked in `published-topics.json` to reduce overlap.

## Safety checks

- Skips if a post with today's date already exists
- Validates front matter and Swift code blocks before saving
- Avoids regenerating titles already on the blog
- Only generates Swift / iOS / Apple platform content

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
