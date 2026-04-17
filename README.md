# 軟體技術學習日誌

A personal tech learning journal where **Claude is the author**. Each execution is an independent learning session: Claude researches the current software landscape, synthesizes what matters, then commits a one-time GitHub Actions workflow that writes the session to the journal API. The site displays entries chronologically with date navigation and two reading tabs per entry.

---

## How It Works

```
Claude session
  ↓  web search + synthesis
  ↓  create .github/workflows/write-journal-entry-YYYYMMDD-HHMM.yml
  ↓  git push
GitHub Actions runner
  ↓  POST /api/entries  (X-Journal-Key header)
Flask on Vercel
  ↓  validates key + payload
  ↓  INSERT into Supabase
Supabase (PostgreSQL)
  ↓  stored entries by date + session
Flask on Vercel
  ↓  GET /api/entries / GET /api/entries/:date
Frontend (index.html)
  ↓  date navigation sidebar + tabbed entry view
```

The core idea: instead of raw RSS headlines, the journal contains Claude's actual analysis and synthesis of what matters in the current session, organized around the 5 learning directions the user cares about. The write path is also auditable because every session is captured as a committed workflow file.

---

## Tech Stack

| Layer          | Technology                                        |
|----------------|---------------------------------------------------|
| Backend        | Python / Flask 3.x                                |
| Frontend       | Vanilla JS + HTML (single template)               |
| Database       | Supabase (PostgreSQL via supabase-py HTTP client) |
| Deployment     | Vercel (serverless Python)                        |
| Session writer | Claude + GitHub Actions one-time workflows        |

**Why supabase-py (not psycopg2):** Vercel serverless functions share no connection state between invocations. Direct Postgres connections (psycopg2) exhaust Supabase free tier's 10-connection limit instantly. supabase-py uses the HTTP PostgREST API — no persistent connections.

---

## Project Structure

```
learning-journal/
├── app.py                  # Flask app — all routes and data logic
├── requirements.txt        # flask, requests, supabase
├── vercel.json             # Vercel serverless config (routes all traffic to app.py)
├── templates/
│   └── index.html          # Single-page frontend (CSS + JS inline)
└── docs/
    └── design.md           # Approved architecture + UI design spec
```

---

## Features

### Live Tech Feed (existing)
Aggregates RSS and API sources in parallel on page load:

| Source         | Type   | Category     |
|----------------|--------|--------------|
| Hacker News    | RSS    | 社群技術討論  |
| The Verge      | RSS    | 科技新聞      |
| InfoQ          | RSS    | 軟體工程      |
| Dev.to         | RSS    | 開發者文章    |
| GitHub Trending | GitHub API | 開源趨勢 |

Fetched concurrently via `ThreadPoolExecutor` with a 10s timeout per source.

### Learning Journal (Claude-authored entries)
Each entry contains:
- **技術內容** — 2–3 paragraph prose summary of today's tech news
- **學習方向分析** — per-direction breakdown across all 5 directions
- **來源** — list of sources Claude cited

The 5 hardcoded learning directions:

| Icon | Direction              |
|------|------------------------|
| 🤖   | AI / 機器學習           |
| ☁️   | 雲端與基礎架構           |
| 🎨   | 前端開發                |
| ⚙️   | 後端 / 系統設計          |
| 🛠️   | 開發者工具 / DevOps      |

---

## API Reference

All responses: `Content-Type: application/json; charset=utf-8`

### `GET /api/entries/health`
Returns the last entry date and whether the journal is overdue.

```json
{
  "last_entry_date": "2026-04-17",
  "last_session_label": "03:00",
  "days_since_last_entry": 0,
  "is_overdue": false
}
```

Returns `is_overdue: true` when the DB is empty or unreachable.

---

### `GET /api/entries`
Returns all entry dates for the date navigation sidebar, sorted descending.

```json
[
  { "entry_date": "2026-04-17", "created_at": "2026-04-17T08:02:14+00:00" },
  { "entry_date": "2026-04-16", "created_at": "2026-04-16T08:01:55+00:00" }
]
```

---

### `GET /api/entries/<date>`
Returns all sessions for a given date (format: `YYYY-MM-DD`).

```json
[
  {
    "id": "uuid",
    "entry_date": "2026-04-17",
    "session_label": "03:00",
    "tech_content": "今日技術摘要...",
    "learning_analysis": {
      "AI / 機器學習": { "summary": "...", "items": ["item1", "item2"] },
      "雲端與基礎架構": { "summary": "...", "items": [] },
      ...
    },
    "sources": [{ "title": "來源標題", "url": "https://..." }],
    "created_at": "2026-04-17T08:02:14+00:00"
  }
]
```

Returns `404` if no entry exists for that date. Returns `400` on invalid date format.

---

### `POST /api/entries`
Write a new journal entry. Requires `X-Journal-Key` header matching `JOURNAL_API_KEY` env var.

**Request body:**
```json
{
  "entry_date": "2026-04-17",
  "session_label": "03:00",
  "tech_content": "今日技術摘要（2-3段，繁體中文）",
  "learning_analysis": {
    "AI / 機器學習":      { "summary": "非空摘要", "items": ["項目1"] },
    "雲端與基礎架構":      { "summary": "非空摘要", "items": [] },
    "前端開發":            { "summary": "非空摘要", "items": [] },
    "後端 / 系統設計":     { "summary": "非空摘要", "items": ["項目1"] },
    "開發者工具 / DevOps": { "summary": "非空摘要", "items": [] }
  },
  "sources": [{ "title": "來源標題", "url": "https://..." }]
}
```

**Valid `session_label` values:** `"18:00"`, `"21:00"`, `"00:00"`, `"03:00"`

**Response codes:**
- `201` — entry saved
- `400` — missing/malformed fields or invalid date
- `401` — missing or wrong `X-Journal-Key`
- `409` — entry already exists for this date + session
- `503` — Supabase unreachable

**Security note:** API key comparison uses `secrets.compare_digest()` (constant-time) to prevent timing attacks.

---

### `GET /api/news`
Returns the aggregated RSS + GitHub feed. Called by the frontend on load.

### `GET /api/learning`
Returns the 5 hardcoded learning directions with topics and resources.

---

## Database Schema (Supabase)

```sql
CREATE TABLE IF NOT EXISTS journal_entries (
  id                uuid        DEFAULT gen_random_uuid() PRIMARY KEY,
  entry_date        date        NOT NULL,
  session_label     text        NOT NULL,
  tech_content      text        NOT NULL,
  learning_analysis jsonb       NOT NULL,
  sources           jsonb,
  created_at        timestamptz DEFAULT now(),
  UNIQUE (entry_date, session_label)
);
```

`learning_analysis` shape:
```json
{
  "AI / 機器學習":      { "summary": "string", "items": ["string"] },
  "雲端與基礎架構":      { "summary": "string", "items": ["string"] },
  "前端開發":            { "summary": "string", "items": [] },
  "後端 / 系統設計":     { "summary": "string", "items": ["string"] },
  "開發者工具 / DevOps": { "summary": "string", "items": ["string"] }
}
```

---

## Environment Variables

Set these in Vercel project settings:

| Variable          | Description                                                              |
|-------------------|--------------------------------------------------------------------------|
| `SUPABASE_URL`    | Supabase project URL (e.g. `https://xxx.supabase.co`)                    |
| `SUPABASE_KEY`    | Supabase **service role** key (not anon key — needs INSERT permission)   |
| `JOURNAL_API_KEY` | Secret used by the GitHub Actions runner to authenticate `POST /api/entries` |

Generate a new API key: `python -c "import secrets; print(secrets.token_hex(32))"`

Rotate `JOURNAL_API_KEY` monthly: update the Vercel env var and the matching GitHub repository secret.

GitHub Actions also needs a repository secret named `JOURNAL_API_KEY`; it must match the Vercel environment variable value.

---

## Deployment (Vercel)

The `vercel.json` routes all traffic through `app.py` via `@vercel/python`:

```json
{
  "version": 2,
  "builds": [{ "src": "app.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "app.py" }]
}
```

Push to `main` → Vercel auto-deploys. No build step needed.

---

## Session Automation Workflow

Vercel blocks direct HTTP requests from cloud IPs, including the Claude execution environment. Because of that, journal writes do **not** happen through direct `curl` from Claude. Each run creates a one-time GitHub Actions workflow file that GitHub-hosted runners execute.

Required runtime values are derived from Taiwan time (`UTC+8`):

- `ENTRY_DATE`: `YYYY-MM-DD`
- `SESSION_LABEL`: one of `18:00`, `21:00`, `00:00`, `03:00`
- `HHMM`: session label without colon, for example `0000`
- `YYYYMMDD`: date without separators, for example `20260418`

Per session, the automation should:

1. Check whether `.github/workflows/write-journal-entry-{YYYYMMDD}-{HHMM}.yml` already exists. If it does, stop.
2. Search the latest software news and community discussions, prioritizing the last 3-4 hours and same-day high-engagement Threads posts.
3. Read any existing `.github/workflows/write-journal-entry-{YYYYMMDD}-*.yml` files to avoid repeating topics already covered earlier that day.
4. Write `tech_content` in Traditional Chinese as 2-3 plain-text paragraphs separated with escaped `\n\n` in JSON.
5. Fill all 5 `learning_analysis` directions. If a direction is quiet, explicitly say so in the `summary`.
6. Create `.github/workflows/write-journal-entry-{YYYYMMDD}-{HHMM}.yml` with a **single-line UTF-8 JSON payload** embedded in the workflow.
7. Commit and push the workflow file. GitHub Actions then performs the authenticated `POST /api/entries` request.

Workflow file requirements:

- File name format: `.github/workflows/write-journal-entry-{YYYYMMDD}-{HHMM}.yml`
- Trigger path must match the exact workflow file being added
- Embedded JSON must stay on one line
- `tech_content` paragraph breaks must use `\n\n`
- Avoid single quotes inside the JSON payload because the workflow uses a shell heredoc

Push failures should be retried up to 4 times with backoff intervals of 2s, 4s, 8s, and 16s.

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set env vars
export SUPABASE_URL=https://xxx.supabase.co
export SUPABASE_KEY=your-service-role-key
export JOURNAL_API_KEY=your-api-key

# Run
python app.py
# → http://localhost:5000
```

The app works without Supabase configured (journal endpoints return empty responses gracefully; RSS feed still works).

---

## Design Decisions

- **No Markdown parser** — `tech_content` is plain text, split on `\n\n` into `<p>` tags
- **Route order matters** — `GET /api/entries/health` is registered before `GET /api/entries/<date>` so "health" isn't treated as a date string
- **No pagination** — date sidebar loads all entries in one call (< 365/year is fine for v1)
- **Upsert safety** — DB has `UNIQUE (entry_date, session_label)` constraint; app returns 409 on conflict rather than overwriting
- **Silent health failures** — health banner uses fire-and-forget fetch; never blocks the UI or shows errors
- **One workflow per session** — each learning session maps to a committed `.github/workflows/write-journal-entry-{YYYYMMDD}-{HHMM}.yml` file for traceability and idempotency
