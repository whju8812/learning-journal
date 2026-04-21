# 軟體技術學習日誌 — Project Context

## What This Is

A personal tech learning journal web app. Claude Code CLI runs a daily script at 08:00 and 20:00 (Taiwan time) that researches today's software tech landscape, writes a structured entry, and pushes a GitHub Actions workflow that POSTs the entry to this app. The site displays entries chronologically with tabs: **技術內容** (Tech Content) and **學習方向分析** (Learning Direction Analysis).

**Design doc (approved):** `docs/design.md`

## Tech Stack

| Layer       | Technology                                                  |
| ----------- | ----------------------------------------------------------- |
| Backend     | Python / Flask                                              |
| Frontend    | Vanilla JS + HTML (single template: `templates/index.html`) |
| Database    | Supabase (PostgreSQL) — **not yet wired up, next step**     |
| Deployment  | Vercel (serverless)                                         |
| Daily agent | Claude Code CLI + GitHub Actions (每天 08:00 / 20:00 台灣時間) |

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

The app **already works** and is deployed on Vercel. It fetches RSS feeds from:

- Hacker News, The Verge, InfoQ, Dev.to (via RSS)
- GitHub Trending (via GitHub API)

And displays them alongside 5 learning directions (defined in `LEARNING_DIRECTIONS` in `app.py`).

## What Needs to Be Built Next

The journal entry feature — see `docs/design.md` for full spec. Summary:

1. **Supabase connection** — add `supabase` to `requirements.txt`, connect via `SUPABASE_URL` + `SUPABASE_KEY` env vars (use supabase-py, NOT psycopg2 — Vercel serverless exhausts Postgres direct connections)
2. **4 new Flask endpoints** in `app.py`:
   - `POST /api/entries` — Claude writes a daily entry (auth via `X-Journal-Key` header)
   - `GET /api/entries` — list of dates for navigation
   - `GET /api/entries/<date>` — full entry for a date (format: YYYY-MM-DD)
   - `GET /api/entries/health` — last entry date + is_overdue flag
3. **Frontend update** — date navigation sidebar + two-tab entry view in `templates/index.html`

## Key Conventions

- Language: Traditional Chinese (繁體中文) for all user-facing text
- The 5 learning directions are hardcoded (v1). Do not make them configurable.
- All API responses: `Content-Type: application/json; charset=utf-8`
- Auth header for write endpoints: `X-Journal-Key` (matches `JOURNAL_API_KEY` env var)
- `entry_date` format everywhere: `YYYY-MM-DD`
- Valid `session_label` values: `"08:00"` (morning), `"20:00"` (evening) — Taiwan time UTC+8
- `tech_application` field: 1–2 application scenarios (tool name + who/context + how to start)

## Environment Variables (Vercel)

| Variable          | Purpose                                                            |
| ----------------- | ------------------------------------------------------------------ |
| `SUPABASE_URL`    | Supabase project URL (e.g. https://xxx.supabase.co)                |
| `SUPABASE_KEY`    | Supabase service role key (not anon key — needs INSERT permission) |
| `JOURNAL_API_KEY` | Secret for Claude Desktop to authenticate POST /api/entries        |

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
