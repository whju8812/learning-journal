# TODOS

## Deferred from /plan-eng-review (2026-04-16)

### [ ] Add pytest smoke tests for journal API endpoints

**What:** Create `tests/test_api.py` with Flask test client. Cover each endpoint's happy path + auth rejection + 400 edge cases.

**Why:** Zero tests exist. When the DB schema or validation logic changes, nothing catches regressions. Auth bugs (401 vs 400 confusion) and route ordering mistakes are the most likely first failures.

**Where to start:**
- Add `pytest`, `pytest-flask` to a `requirements-dev.txt`
- Mock the `supabase` client in tests (don't hit real DB)
- Test matrix: valid POST → 201, bad key → 401, duplicate date → 409, missing field → 400, GET health empty DB → 200 with is_overdue true

**Depends on:** Journal endpoints must be implemented first.

---

### [ ] Create `db/schema.sql` — idempotent DB setup script

**What:** A `db/schema.sql` file with the `CREATE TABLE IF NOT EXISTS journal_entries (...)` statement. Commit it to the repo.

**Why:** Currently, "set up the database" means copying SQL from `docs/design.md` into Supabase UI. If the Supabase project needs to be recreated (or a new one created), there's no authoritative script.

**Where to start:**
```sql
CREATE TABLE IF NOT EXISTS journal_entries (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  entry_date  date NOT NULL UNIQUE,
  tech_content     text NOT NULL,
  learning_analysis jsonb NOT NULL,
  sources     jsonb DEFAULT '[]'::jsonb,
  created_at  timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_journal_entries_date ON journal_entries (entry_date DESC);
```

**Depends on:** Nothing. Can be done anytime.
