-- Learning Journal: Supabase schema
-- Run in: Supabase Dashboard → SQL Editor
-- Idempotent: safe to re-run

CREATE TABLE IF NOT EXISTS journal_entries (
  id            uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  entry_date    date NOT NULL,
  session_label varchar(5) NOT NULL,          -- "18:00" | "21:00" | "00:00" | "03:00"
  tech_content  text NOT NULL,                -- prose summary for this session
  learning_analysis jsonb NOT NULL,           -- per-direction breakdown
  sources       jsonb DEFAULT '[]'::jsonb,    -- [{title, url}, ...]
  created_at    timestamptz DEFAULT now(),
  UNIQUE (entry_date, session_label)
);

CREATE INDEX IF NOT EXISTS idx_journal_entries_date
  ON journal_entries (entry_date DESC, session_label);

-- learning_analysis shape:
-- {
--   "AI / 機器學習":         { "summary": "...", "items": ["item1", ...] },
--   "雲端與基礎架構":         { "summary": "...", "items": [...] },
--   "前端開發":              { "summary": "...", "items": [...] },
--   "後端 / 系統設計":        { "summary": "...", "items": [...] },
--   "開發者工具 / DevOps":    { "summary": "...", "items": [...] }
-- }
