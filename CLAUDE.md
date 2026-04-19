# 軟體技術學習日誌 — Project Context

## What This Is

A personal tech learning journal web app. Each execution is a standalone learning session. Because Vercel blocks direct HTTP requests from cloud IPs, Claude does not post to the journal API directly; it researches the current software landscape, creates a one-time GitHub Actions workflow, and pushes that workflow so a GitHub-hosted runner can write the entry.

**Design doc (approved):** `docs/design.md`

## Tech Stack

| Layer          | Technology                                                  |
| -------------- | ----------------------------------------------------------- |
| Backend        | Python / Flask                                              |
| Frontend       | Vanilla JS + HTML (single template: `templates/index.html`) |
| Database       | Supabase (PostgreSQL via supabase-py HTTP client)           |
| Deployment     | Vercel (serverless)                                         |
| Session writer | Claude + GitHub Actions one-time workflows                  |

## Project Structure

```
learning-journal/
├── app.py                  # Flask app — all routes and data fetching
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment config
├── templates/
│   └── index.html          # Single-page frontend (CSS + JS inline)
├── docs/
│   └── design.md           # Approved architecture design (read this first)
└── CLAUDE.md               # This file
```

## Current State

The app is deployed on Vercel and the journal endpoints use Supabase. It also fetches live tech feeds from:

- Hacker News, The Verge, InfoQ, Dev.to (via RSS)
- GitHub Trending (via GitHub API)

And displays them alongside 5 learning directions (defined in `LEARNING_DIRECTIONS` in `app.py`).

## Session Workflow

Every run should follow this workflow:

1. Compute Taiwan time (`UTC+8`) and derive:
    - `ENTRY_DATE` in `YYYY-MM-DD`
    - `SESSION_LABEL` as one of `18:00`, `21:00`, `00:00`, `03:00`
    - `HHMM` without a colon
    - `YYYYMMDD` without separators
2. Check whether `.github/workflows/write-journal-entry-{YYYYMMDD}-{HHMM}.yml` already exists. If it does, the session is already handled.
3. Search today's latest software content, prioritizing the last 3-4 hours and same-day high-engagement Threads posts.
4. Read existing `.github/workflows/write-journal-entry-{YYYYMMDD}-*.yml` files to avoid repeating themes covered by earlier sessions on the same date.
5. Write Traditional Chinese content:
    - `tech_content`: 2-3 plain-text paragraphs
    - `learning_analysis`: all 5 directions required, `summary` cannot be blank
    - `sources`: array of `{ "title": str, "url": str }`
6. Create `.github/workflows/write-journal-entry-{YYYYMMDD}-{HHMM}.yml` with a single-line UTF-8 JSON payload and push it.
7. After pushing, immediately create a PR from `{CURRENT_BRANCH}` to `main` and merge it (squash). This is required because GitHub Actions only reliably triggers `push` events from `main`. Do this automatically without asking the user.
8. GitHub Actions performs the actual `POST /api/entries` call using the repo secret `JOURNAL_API_KEY`.

## Key Conventions

- Language: Traditional Chinese (繁體中文) for all user-facing text
- The 5 learning directions are hardcoded (v1). Do not make them configurable.
- All API responses: `Content-Type: application/json; charset=utf-8`
- Auth header for write endpoints: `X-Journal-Key` (matches `JOURNAL_API_KEY` env var)
- `entry_date` format everywhere: `YYYY-MM-DD`
- Valid `session_label` values are only `18:00`, `21:00`, `00:00`, `03:00`
- One workflow file represents exactly one session: `.github/workflows/write-journal-entry-{YYYYMMDD}-{HHMM}.yml`
- Do not use direct `curl` from the Claude environment to write journal entries; the GitHub Actions runner is the supported write path
- `tech_content` paragraphs must be separated with escaped `\n\n` inside the JSON payload
- The embedded workflow JSON must stay on one line and must not contain single quotes

## Secrets and Environment Variables

| Variable          | Purpose                                                            |
| ----------------- | ------------------------------------------------------------------ |
| `SUPABASE_URL`    | Supabase project URL (e.g. https://xxx.supabase.co)                |
| `SUPABASE_KEY`    | Supabase service role key (not anon key — needs INSERT permission) |
| `JOURNAL_API_KEY` | Shared secret used by GitHub Actions to authenticate POST /api/entries |

Keep `JOURNAL_API_KEY` synchronized between Vercel environment variables and GitHub repository secrets.

## Learning Directions (hardcoded in app.py)

```python
LEARNING_DIRECTIONS = [
    "AI / 機器學習",
    "雲端與基礎架構",
    "前端開發",
    "後端 / 系統設計",
    "開發者工具 / DevOps",
]
```

Each journal entry's `learning_analysis` field must contain all 5 keys with `{ "summary": str, "items": [str] }`.

## Design System

Always read DESIGN.md before making any visual or UI decisions.
All font choices, colors, spacing, and aesthetic direction are defined there.
Do not deviate without explicit user approval.
In QA mode, flag any code that doesn't match DESIGN.md.

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

Key routing rules:

- Product ideas, "is this worth building", brainstorming → invoke office-hours
- Bugs, errors, "why is this broken", 500 errors → invoke investigate
- Ship, deploy, push, create PR → invoke ship
- QA, test the site, find bugs → invoke qa
- Code review, check my diff → invoke review
- Update docs after shipping → invoke document-release
- Weekly retro → invoke retro
- Design system, brand → invoke design-consultation
- Visual audit, design polish → invoke design-review
- Architecture review → invoke plan-eng-review
- Save progress, checkpoint, resume → invoke checkpoint
- Code quality, health check → invoke health
