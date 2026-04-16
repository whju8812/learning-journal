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

---

## Deferred from /plan-design-review (2026-04-16)

### [ ] Run /design-consultation to create DESIGN.md

**What:** Execute `/design-consultation` to formalize the implicit CSS variable design system into a proper DESIGN.md file.

**Why:** The current design system is implicit (12 CSS variables in `index.html`). No reference document exists for future features. New components risk drifting from the established palette and spacing.

**Pros:** Unified design language, faster future feature work, consistency guarantee.
**Cons:** Extra work, not blocking v1.
**Context:** The plan-design-review mapped all new components to existing CSS variables, but this is a one-time mapping. A DESIGN.md makes it systematic.

**Depends on:** Nothing. Can be done anytime.

---

### [ ] Screen reader test for journal tab after implementation

**What:** After the journal tab is implemented, test with a screen reader (NVDA on Windows) to verify ARIA landmarks, tab navigation, and date selection work correctly.

**Why:** ARIA specs were added to the plan (role="navigation", role="tablist", role="alert") but need real-world validation. Keyboard navigation for date sidebar ↑↓ and inner tabs ←→ must be verified.

**Pros:** Ensures accessibility is real, not just documented.
**Cons:** Requires extra testing time.
**Context:** Plan specifies: sidebar `role="navigation" aria-label="日期導航"`, inner tabs use WAI-ARIA tabs pattern, health banner `role="alert"`. Touch targets ≥ 44px.

**Depends on:** Journal tab must be implemented first.
