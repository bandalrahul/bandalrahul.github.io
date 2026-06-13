# Daily Blog Automation

This folder powers fully automated daily publishing for [Swift By Rahul](https://www.swiftbyrahul.com).

## What it does

Every day at **09:00 UTC**, GitHub Actions will:

1. Pick an unused Swift/iOS topic from `topics.json`
2. Generate a new article with OpenAI
3. Save it to `Content/posts/`
4. Build the site with Publish
5. Deploy to the `master` branch (GitHub Pages)
6. Commit the new markdown back to `main`

## One-time setup

### 1. Add your OpenAI API key

In GitHub repo settings:

**Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|------|-------|
| `OPENAI_API_KEY` | Your OpenAI API key |

Optional variable (not secret):

| Name | Value |
|------|-------|
| `OPENAI_MODEL` | `gpt-4o-mini` (default) or `gpt-4o` for higher quality |

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

## Cost estimate

Using `gpt-4o-mini` at ~1 article/day:

- Roughly **$0.05–0.20 per day** depending on article length

## Disable automation

Pause the schedule by deleting or disabling `.github/workflows/daily-post.yml`, or disable the workflow in the GitHub Actions UI.

## Local test

```bash
export OPENAI_API_KEY="your-key-here"
pip install -r automation/requirements.txt
python automation/generate_article.py
swift run PublishSBR
swift run PublishSBR --deploy
```
