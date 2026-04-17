# 軟體技術學習日誌

A personal tech learning journal where **Claude is the author**. Every day, a Claude Desktop scheduled task researches the software tech landscape, synthesizes what matters, and writes a structured entry organized around 5 learning directions. The site displays entries chronologically with date navigation and two reading tabs per entry.

---

## How It Works

```
Claude Desktop (daily scheduled task)
  ↓  web search + synthesis
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

The core idea: instead of raw RSS headlines, the journal contains Claude's actual analysis and synthesis of what matters today — organized around the 5 learning directions the user cares about. Zero manual effort after initial setup.

---

## Tech Stack

| Layer       | Technology                                        |
|-------------|---------------------------------------------------|
| Backend     | Python / Flask 3.x                                |
| Frontend    | Vanilla JS + HTML (single template)               |
| Database    | Supabase (PostgreSQL via supabase-py HTTP client) |
| Deployment  | Vercel (serverless Python)                        |
| Daily agent | Claude Desktop scheduled task                     |

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
  "last_session_label": "08:00",
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
    "session_label": "08:00",
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
  "session_label": "08:00",
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
| `JOURNAL_API_KEY` | Secret used by Claude Desktop to authenticate `POST /api/entries`        |

Generate a new API key: `python -c "import secrets; print(secrets.token_hex(32))"`

Rotate `JOURNAL_API_KEY` monthly: update in Vercel env vars, then update the Claude Desktop task prompt.

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

## Claude Desktop Scheduled Task

Configure in Claude Desktop as a daily scheduled task (e.g., 8:00 AM). Requires **web_search** and **bash** tools enabled.

```
你是我的軟體技術學習助理。今天是 {TODAY_DATE}（格式：YYYY-MM-DD）。

步驟一：先確認今天是否已有日誌
使用 bash 工具執行：
curl https://your-app.vercel.app/api/entries/health -H "X-Journal-Key: {YOUR_API_KEY}"

如果回傳的 last_entry_date 等於今天日期，代表今天已有日誌，任務完成。

步驟二：研究今日軟體界最新動態
使用 web_search 工具查詢最新技術發布、Hacker News、GitHub 社群趨勢。

步驟三：POST 到學習日誌
curl -X POST https://your-app.vercel.app/api/entries \
  -H "X-Journal-Key: {YOUR_API_KEY}" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "entry_date": "{TODAY_DATE}",
    "session_label": "08:00",
    "tech_content": "今日技術摘要（2-3段，繁體中文）",
    "learning_analysis": {
      "AI / 機器學習":      { "summary": "非空摘要", "items": [] },
      "雲端與基礎架構":      { "summary": "非空摘要", "items": [] },
      "前端開發":            { "summary": "非空摘要", "items": [] },
      "後端 / 系統設計":     { "summary": "非空摘要", "items": [] },
      "開發者工具 / DevOps": { "summary": "非空摘要", "items": [] }
    },
    "sources": [{ "title": "來源標題", "url": "https://..." }]
  }'

201 → 完成。409 → 今天已有日誌。其他狀態碼 → 重試最多 3 次。
```

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
