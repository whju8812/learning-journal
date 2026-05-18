// ─── Constants ───
const DIRECTION_ICONS = {
  'AI / 機器學習':     '🤖',
  '雲端與基礎架構':    '☁️',
  '前端開發':          '🎨',
  '後端 / 系統設計':   '⚙️',
  '開發者工具 / DevOps': '🔧',
};
const DIRECTIONS_ORDER = [
  'AI / 機器學習', '雲端與基礎架構', '前端開發', '後端 / 系統設計', '開發者工具 / DevOps',
];

// ─── State ───
let currentDate     = null;
let currentSessions = [];
let allDates        = [];
let healthData      = null;
let healthDismissed = false;
let currentInnerTab = 'tech';

// Year-group collapse state (persisted in localStorage)
const LS_YEAR_KEY = 'lj.yearCollapsed.v1';
let collapsedYears = loadCollapsedYears();

// Search state
let searchQuery   = '';
let searchTimer   = null;
let searching     = false;

// Cached once at load — today never changes during a page session
const TODAY = todayStr();

// ─── Utils ───
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function renderInline(str) {
  return escHtml(str).replace(/\*\*(.+?)\*\*[ \t]*/g, '<strong>$1</strong><br>');
}

function renderRichText(str) {
  const parts = [];
  const re = /```(\w*)\n([\s\S]*?)```/g;
  let last = 0;
  let m;
  while ((m = re.exec(str)) !== null) {
    if (m.index > last) {
      str.slice(last, m.index).trim().split(/\n\n+/).filter(p => p.trim())
        .forEach(p => parts.push(`<p>${renderInline(p.trim())}</p>`));
    }
    const lang = escHtml(m[1] || '');
    parts.push(
      `<div class="code-block">` +
      (lang ? `<span class="code-lang">${lang}</span>` : '') +
      `<pre><code>${escHtml(m[2])}</code></pre></div>`
    );
    last = m.index + m[0].length;
  }
  if (last < str.length) {
    str.slice(last).trim().split(/\n\n+/).filter(p => p.trim())
      .forEach(p => parts.push(`<p>${renderInline(p.trim())}</p>`));
  }
  return parts.join('');
}

function todayStr() {
  const t = new Date();
  return `${t.getFullYear()}-${String(t.getMonth()+1).padStart(2,'0')}-${String(t.getDate()).padStart(2,'0')}`;
}

function formatDateFull(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return `${d.getFullYear()}年${d.getMonth()+1}月${d.getDate()}日 技術日誌`;
}

function formatDateChip(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return `${String(d.getMonth()+1).padStart(2,'0')}/${String(d.getDate()).padStart(2,'0')} (${DAY_NAMES[d.getDay()]})`;
}

function yearOf(dateStr) {
  return dateStr.slice(0, 4);
}

// ─── localStorage helpers ───
function loadCollapsedYears() {
  try {
    const raw = localStorage.getItem(LS_YEAR_KEY);
    if (!raw) return new Set();
    const arr = JSON.parse(raw);
    return new Set(Array.isArray(arr) ? arr.map(String) : []);
  } catch {
    return new Set();
  }
}

function saveCollapsedYears() {
  try {
    localStorage.setItem(LS_YEAR_KEY, JSON.stringify([...collapsedYears]));
  } catch { /* quota / private mode — ignore */ }
}

// Group dates into [{ year, items: [...] }] preserving descending order.
function groupDatesByYear(dates) {
  const groups = [];
  const idx = new Map();
  for (const entry of dates) {
    const y = yearOf(entry.entry_date);
    if (!idx.has(y)) {
      idx.set(y, groups.length);
      groups.push({ year: y, items: [] });
    }
    groups[idx.get(y)].items.push(entry);
  }
  return groups;
}

// ─── Date display ───
(function () {
  const now = new Date();
  document.getElementById('dateDisplay').textContent =
    `${now.getFullYear()}年${now.getMonth()+1}月${now.getDate()}日 (${DAY_NAMES[now.getDay()]})`;
})();

// ─── API ───
async function apiFetch(path) {
  const res = await fetch(path);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw Object.assign(new Error(err.error || res.statusText), { status: res.status });
  }
  return res.json();
}

// ─── Init ───
async function initJournal() {
  showLoadingState();
  try {
    [healthData, allDates] = await Promise.all([
      fetch('/api/entries/health').then(r => r.json()).catch(() => null),
      apiFetch('/api/entries').catch(() => []),
    ]);

    if (!allDates || allDates.length === 0) {
      renderDateSidebarEmpty();
      document.getElementById('journalContent').innerHTML = renderEmptyState();
      return;
    }

    currentDate = allDates[0].entry_date;
    renderDateSidebar();
    await loadEntry(currentDate);
  } catch {
    document.getElementById('journalContent').innerHTML = renderErrorState(initJournal);
  }
}

async function loadEntry(dateStr) {
  currentDate = dateStr;
  renderDateSidebar();
  document.getElementById('journalContent').innerHTML =
    '<div class="loading-spinner-center"><div class="accent-spinner"></div></div>';
  try {
    const sessions = await apiFetch(`/api/entries/${dateStr}`);
    // Deduplicate sources once on load, not on every render
    const seenUrls = new Set();
    currentSessions = sessions.map(s => ({
      ...s,
      sources: (s.sources || []).filter(src => {
        if (seenUrls.has(src.url)) return false;
        seenUrls.add(src.url);
        return true;
      }),
    }));
    renderEntry();
  } catch (e) {
    const html = e.status === 404
      ? renderEmptyState()
      : renderErrorState(() => loadEntry(dateStr));
    document.getElementById('journalContent').innerHTML = html;
  }
}

function selectDate(dateStr) {
  ensureYearExpanded(dateStr);
  if (dateStr === currentDate && currentSessions.length > 0) {
    renderDateSidebar();
    return;
  }
  loadEntry(dateStr);
}

// ─── Date sidebar ───
function renderDateSidebarEmpty() {
  document.getElementById('dateList').innerHTML =
    '<div style="color:var(--text-muted);font-size:var(--text-small);padding:var(--space-3);">尚無日誌</div>';
  document.getElementById('mobileStrip').innerHTML = '';
}

// Build a date chip element (shared by sidebar groups).
function buildDateChip(entry) {
  const isToday  = entry.entry_date === TODAY;
  const isActive = entry.entry_date === currentDate;
  const label    = (isToday ? '✦ ' : '') + formatDateChip(entry.entry_date);

  const chip = document.createElement('div');
  chip.className = 'date-chip' + (isActive ? ' active' : '') + (isToday ? ' today' : '');
  chip.setAttribute('role', 'tab');
  chip.setAttribute('tabindex', '0');
  chip.setAttribute('aria-selected', String(isActive));
  chip.innerHTML = `${escHtml(label)}<span class="today-badge">今天</span>`;
  chip.onclick = () => selectDate(entry.entry_date);
  chip.onkeydown = e => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      selectDate(entry.entry_date);
    }
  };
  return chip;
}

function renderDateSidebar() {
  // Sidebar (desktop): year-grouped, collapsible
  const groups = groupDatesByYear(allDates);
  const listFrag = document.createDocumentFragment();
  const newestYear = groups.length ? groups[0].year : null;

  groups.forEach(group => {
    // Default: only newest year expanded.
    // A year is collapsed if user explicitly collapsed it,
    // OR if it isn't the newest year and user hasn't expanded it.
    const userCollapsed   = collapsedYears.has(group.year);
    const userExpanded    = collapsedYears.has('!' + group.year); // explicit expand marker
    const collapsedByDefault = group.year !== newestYear;
    const isCollapsed = userCollapsed || (collapsedByDefault && !userExpanded);

    const wrap = document.createElement('div');
    wrap.className = 'year-group' + (isCollapsed ? ' collapsed' : '');
    wrap.dataset.year = group.year;

    const header = document.createElement('button');
    header.type = 'button';
    header.className = 'year-header';
    header.setAttribute('aria-expanded', String(!isCollapsed));
    header.innerHTML = `
      <span class="year-caret" aria-hidden="true">▾</span>
      <span class="year-label">${escHtml(group.year)} 年</span>
      <span class="year-count">${group.items.length}</span>
    `;
    header.onclick = () => toggleYear(group.year);
    wrap.appendChild(header);

    const body = document.createElement('div');
    body.className = 'year-body';
    group.items.forEach(entry => body.appendChild(buildDateChip(entry)));
    wrap.appendChild(body);

    listFrag.appendChild(wrap);
  });

  const list = document.getElementById('dateList');
  list.innerHTML = '';
  list.appendChild(listFrag);

  // Mobile strip: flat list (no year grouping — strip is already chronological)
  const stripFrag = document.createDocumentFragment();
  allDates.forEach(entry => {
    const isToday  = entry.entry_date === TODAY;
    const isActive = entry.entry_date === currentDate;
    const label    = (isToday ? '✦ ' : '') + formatDateChip(entry.entry_date);
    const pill = document.createElement('div');
    pill.className = 'date-pill' + (isActive ? ' active' : '') + (isToday ? ' today' : '');
    pill.setAttribute('role', 'tab');
    pill.setAttribute('tabindex', '0');
    pill.textContent = label;
    pill.onclick = () => selectDate(entry.entry_date);
    stripFrag.appendChild(pill);
  });
  const strip = document.getElementById('mobileStrip');
  strip.innerHTML = '';
  strip.appendChild(stripFrag);
}

function toggleYear(year) {
  // Tri-state model:
  //   not in set        → default behaviour (newest expanded, others collapsed)
  //   "<year>" in set   → forced collapsed
  //   "!<year>" in set  → forced expanded
  const newestYear = allDates.length ? yearOf(allDates[0].entry_date) : null;
  const isCollapsed = collapsedYears.has(year) ||
    (year !== newestYear && !collapsedYears.has('!' + year));
  collapsedYears.delete(year);
  collapsedYears.delete('!' + year);
  if (isCollapsed) {
    // expanding
    if (year !== newestYear) collapsedYears.add('!' + year);
  } else {
    // collapsing
    if (year === newestYear) collapsedYears.add(year);
  }
  saveCollapsedYears();
  renderDateSidebar();
}

// Make sure when a search result is clicked, the year containing it
// is force-expanded so the chip is visible.
function ensureYearExpanded(dateStr) {
  const year = yearOf(dateStr);
  const newestYear = allDates.length ? yearOf(allDates[0].entry_date) : null;
  if (year === newestYear) {
    collapsedYears.delete(year);
  } else {
    collapsedYears.delete(year);
    collapsedYears.add('!' + year);
  }
  saveCollapsedYears();
}

// ─── Search ───
function highlightTerm(text, term) {
  // Escape HTML first, then re-inject <mark> around the (escaped) term.
  // We work on the escaped string so we never inject raw HTML from the source.
  const escaped = escHtml(text);
  if (!term) return escaped;
  const escapedTerm = escHtml(term).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  if (!escapedTerm) return escaped;
  return escaped.replace(new RegExp(escapedTerm, 'gi'), m => `<mark>${m}</mark>`);
}

function setSearchUiActive(active) {
  document.getElementById('searchClear').hidden    = !active;
  document.getElementById('searchResults').hidden  = !active;
  document.getElementById('dateList').hidden       = active;
}

async function runSearch(q) {
  searchQuery = q;
  const resultsEl = document.getElementById('searchResults');
  if (!q) {
    setSearchUiActive(false);
    return;
  }
  setSearchUiActive(true);
  resultsEl.innerHTML =
    '<div class="search-status">搜尋中…</div>';
  searching = true;
  try {
    const data = await apiFetch(`/api/entries/search?q=${encodeURIComponent(q)}`);
    if (q !== searchQuery) return; // a newer search has started
    renderSearchResults(data);
  } catch {
    resultsEl.innerHTML =
      '<div class="search-status error">搜尋失敗，請稍後再試</div>';
  } finally {
    searching = false;
  }
}

function renderSearchResults(data) {
  const resultsEl = document.getElementById('searchResults');
  const results = data.results || [];
  if (results.length === 0) {
    resultsEl.innerHTML =
      `<div class="search-status">找不到符合 "<strong>${escHtml(data.query)}</strong>" 的日誌</div>`;
    return;
  }
  // Group by date — one entry_date may have two sessions both matching.
  const byDate = new Map();
  for (const r of results) {
    if (!byDate.has(r.entry_date)) byDate.set(r.entry_date, []);
    byDate.get(r.entry_date).push(r);
  }
  const head = `<div class="search-status">共找到 <strong>${results.length}</strong> 筆結果（${byDate.size} 天）</div>`;
  const rows = [...byDate.entries()].map(([dateStr, hits]) => {
    const fields = [...new Set(hits.map(h => h.matched_field))].join('、');
    const snippet = hits.find(h => h.snippet)?.snippet || '';
    const isActive = dateStr === currentDate;
    return `
      <button type="button" class="search-result ${isActive ? 'active' : ''}" data-date="${escHtml(dateStr)}">
        <div class="search-result-date">${escHtml(formatDateChip(dateStr))} <span class="search-result-year">${escHtml(yearOf(dateStr))}</span></div>
        <div class="search-result-field">${escHtml(fields)}</div>
        ${snippet ? `<div class="search-result-snippet">${highlightTerm(snippet, data.query)}</div>` : ''}
      </button>`;
  }).join('');
  resultsEl.innerHTML = head + rows;
  // Wire result buttons
  resultsEl.querySelectorAll('.search-result').forEach(btn => {
    btn.addEventListener('click', () => {
      const d = btn.dataset.date;
      selectDate(d);
    });
  });
}

function initSearchInput() {
  const input  = document.getElementById('searchInput');
  const clear  = document.getElementById('searchClear');
  if (!input) return;
  input.addEventListener('input', () => {
    const q = input.value.trim();
    clear.hidden = !q;
    if (searchTimer) clearTimeout(searchTimer);
    if (!q) { runSearch(''); return; }
    searchTimer = setTimeout(() => runSearch(q), 250);
  });
  input.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      input.value = '';
      clear.hidden = true;
      runSearch('');
    }
  });
  clear.addEventListener('click', () => {
    input.value = '';
    clear.hidden = true;
    input.focus();
    runSearch('');
  });
}

// ─── Health banner ───
function renderHealthBanner() {
  if (healthDismissed || !healthData) return '';
  const { last_entry_date, last_session_label, days_since_last_entry, is_overdue } = healthData;

  if (!last_entry_date) {
    return `<div class="health-banner warning" role="alert">
      <span>⚠ 尚無任何日誌 — Claude Desktop 排程尚未執行</span>
      <button class="health-dismiss" onclick="dismissHealth()" aria-label="關閉">×</button>
    </div>`;
  }
  if (!is_overdue) {
    return `<div class="health-banner success" role="alert">
      <span>▎ 上次更新：${escHtml(last_entry_date)} ${escHtml(last_session_label || '')} — 一切正常 ✓</span>
      <button class="health-dismiss" onclick="dismissHealth()" aria-label="關閉">×</button>
    </div>`;
  }
  const daysText = days_since_last_entry > 1 ? `${days_since_last_entry} 天前` : '昨天';
  return `<div class="health-banner warning" role="alert">
    <span>⚠ 上次更新：${escHtml(last_entry_date)} ${escHtml(last_session_label || '')}（${daysText}）— Claude Desktop 可能未正常執行</span>
    <button class="health-dismiss" onclick="dismissHealth()" aria-label="關閉">×</button>
  </div>`;
}

function dismissHealth() {
  healthDismissed = true;
  document.querySelector('.health-banner')?.remove();
}

// ─── Entry rendering ───
function renderEntry() {
  const content = document.getElementById('journalContent');
  if (!currentSessions || currentSessions.length === 0) {
    content.innerHTML = renderEmptyState();
    return;
  }

  const isToday = currentDate === TODAY;
  const multi   = currentSessions.length > 1;

  const techHtml = currentSessions.map((s, i) => {
    const paras = s.tech_content.split('\n\n').map(p => `<p>${renderInline(p)}</p>`).join('');
    const appHtml = s.tech_application
      ? `<div class="tech-application"><div class="tech-application-label">💡 技術應用場景</div>${renderRichText(s.tech_application)}</div>`
      : '';
    if (!multi) return `<div class="tech-content">${paras}</div>${appHtml}`;
    return `
      <div class="session-block">
        <span class="session-time-label">${escHtml(s.session_label)}</span>
        <div class="tech-content">${paras}</div>
        ${appHtml}
      </div>
      ${i < currentSessions.length - 1 ? '<hr class="session-divider">' : ''}
    `;
  }).join('');

  const lastSession = currentSessions[currentSessions.length - 1];
  // Sources already deduplicated in loadEntry
  const allSources = currentSessions.flatMap(s => s.sources || []);

  content.innerHTML = `
    ${renderHealthBanner()}
    <div class="entry-header">
      <div class="entry-date-title">
        ${escHtml(formatDateFull(currentDate))}
        ${isToday ? '<span class="today-entry-badge">🆕 今日日誌</span>' : ''}
      </div>
      ${multi ? `<div class="session-count-note">共 ${currentSessions.length} 個 session（${currentSessions.map(s => escHtml(s.session_label)).join('、')}）</div>` : ''}
    </div>
    <div class="inner-tabs" role="tablist" aria-label="日誌內容切換">
      <div class="inner-tab ${currentInnerTab === 'tech' ? 'active' : ''}" role="tab" tabindex="0" data-tab="tech" aria-selected="${currentInnerTab === 'tech'}" onclick="switchInnerTab('tech')">技術內容</div>
      <div class="inner-tab ${currentInnerTab === 'analysis' ? 'active' : ''}" role="tab" tabindex="0" data-tab="analysis" aria-selected="${currentInnerTab === 'analysis'}" onclick="switchInnerTab('analysis')">學習方向分析</div>
    </div>
    <div id="inner-tech" class="inner-section ${currentInnerTab === 'tech' ? 'active' : ''}" role="tabpanel">${techHtml}</div>
    <div id="inner-analysis" class="inner-section ${currentInnerTab === 'analysis' ? 'active' : ''}" role="tabpanel">${renderDirections(lastSession.learning_analysis)}</div>
    ${renderSources(allSources)}
  `;
}

// Uses data-tab attribute — not fragile index-based matching
function switchInnerTab(tab) {
  currentInnerTab = tab;
  document.querySelectorAll('.inner-tab').forEach(t => {
    const isActive = t.dataset.tab === tab;
    t.classList.toggle('active', isActive);
    t.setAttribute('aria-selected', String(isActive));
  });
  document.querySelectorAll('.inner-section').forEach(s => s.classList.remove('active'));
  document.getElementById('inner-' + tab).classList.add('active');
}

function renderDirections(analysis) {
  return DIRECTIONS_ORDER.map(dir => {
    const data = analysis && analysis[dir];
    if (!data) return '';
    const icon     = DIRECTION_ICONS[dir] || '📌';
    const hasItems = data.items && data.items.length > 0;
    return `
      <div class="direction-section">
        <div class="direction-header" onclick="toggleDirection(this)" aria-expanded="true">
          <div class="direction-title">${icon} ${escHtml(dir)}</div>
          <span class="direction-toggle">▼</span>
        </div>
        <div class="direction-body">
          <p class="direction-summary">${escHtml(data.summary)}</p>
          ${hasItems ? `<ul class="direction-items">${data.items.map(item => `<li>${escHtml(item)}</li>`).join('')}</ul>` : ''}
        </div>
      </div>`;
  }).join('');
}

function toggleDirection(header) {
  const body    = header.nextElementSibling;
  const toggle  = header.querySelector('.direction-toggle');
  const expanded = header.getAttribute('aria-expanded') === 'true';
  body.classList.toggle('collapsed', expanded);
  toggle.classList.toggle('collapsed', expanded);
  header.setAttribute('aria-expanded', String(!expanded));
}

function renderSources(sources) {
  if (!sources || sources.length === 0) return '';
  return `
    <div class="sources-section">
      <div class="sources-toggle" onclick="toggleSources()">
        <span class="sources-toggle-icon" id="sourcesIcon">▶</span>
        📎 參考來源 (${sources.length})
      </div>
      <div class="sources-list" id="sourcesList">
        ${sources.map(s => `<a class="source-link" href="${escHtml(s.url)}" target="_blank" rel="noopener noreferrer">${escHtml(s.title)} <span>↗</span></a>`).join('')}
      </div>
    </div>`;
}

function toggleSources() {
  document.getElementById('sourcesList').classList.toggle('expanded');
  document.getElementById('sourcesIcon').classList.toggle('expanded');
}

// ─── Static states ───
function renderEmptyState() {
  return `
    <div class="empty-state">
      <div class="empty-icon">📖</div>
      <div class="empty-title">學習日誌即將開始</div>
      <div class="empty-desc">
        Claude 每日自動研究軟體技術趨勢，撰寫你的專屬學習日誌。<br>
        第一篇日誌將在排程執行後自動產生。
      </div>
      <button class="empty-cta" onclick="location.reload()">🔄 重新整理 →</button>
    </div>`;
}

function renderErrorState(retryFn) {
  // Store retry in a closure via data attribute to avoid window global pollution
  const id = `retry-${Date.now()}`;
  requestAnimationFrame(() => {
    const btn = document.getElementById(id);
    if (btn) btn.addEventListener('click', retryFn);
  });
  return `
    <div class="error-state">
      <div class="error-icon">⚠</div>
      <div class="error-text">載入失敗，請稍後再試</div>
      <button id="${id}" class="retry-btn">重試</button>
    </div>`;
}

function showLoadingState() {
  document.getElementById('dateList').innerHTML = `
    <div class="shimmer shimmer-chip"></div>
    <div class="shimmer shimmer-chip"></div>
    <div class="shimmer shimmer-chip"></div>`;
  document.getElementById('journalContent').innerHTML = `
    <div class="shimmer-container">
      <div class="shimmer shimmer-line long"></div>
      <div class="shimmer shimmer-line medium"></div>
      <div class="shimmer shimmer-line short"></div>
      <div class="shimmer-cards-group">
        <div class="shimmer shimmer-card"></div>
        <div class="shimmer shimmer-card"></div>
        <div class="shimmer shimmer-card"></div>
      </div>
    </div>`;
}

// ─── Boot ───
initSearchInput();
initJournal();
