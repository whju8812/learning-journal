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

// Cached once at load — today never changes during a page session
const TODAY = todayStr();

// ─── Utils ───
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
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
  if (dateStr === currentDate && currentSessions.length > 0) return;
  loadEntry(dateStr);
}

// ─── Date sidebar ───
function renderDateSidebarEmpty() {
  document.getElementById('dateList').innerHTML =
    '<div style="color:var(--text-muted);font-size:var(--text-small);padding:var(--space-3);">尚無日誌</div>';
  document.getElementById('mobileStrip').innerHTML = '';
}

function renderDateSidebar() {
  const listFrag  = document.createDocumentFragment();
  const stripFrag = document.createDocumentFragment();

  allDates.forEach(entry => {
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
    chip.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selectDate(entry.entry_date); } };
    listFrag.appendChild(chip);

    const pill = document.createElement('div');
    pill.className = 'date-pill' + (isActive ? ' active' : '') + (isToday ? ' today' : '');
    pill.setAttribute('role', 'tab');
    pill.setAttribute('tabindex', '0');
    pill.textContent = label;
    pill.onclick = () => selectDate(entry.entry_date);
    stripFrag.appendChild(pill);
  });

  const list  = document.getElementById('dateList');
  const strip = document.getElementById('mobileStrip');
  list.innerHTML  = '';
  strip.innerHTML = '';
  list.appendChild(listFrag);
  strip.appendChild(stripFrag);
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
    const paras = s.tech_content.split('\n\n').map(p => `<p>${escHtml(p)}</p>`).join('');
    if (!multi) return `<div class="tech-content">${paras}</div>`;
    return `
      <div class="session-block">
        <span class="session-time-label">${escHtml(s.session_label)}</span>
        <div class="tech-content">${paras}</div>
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
initJournal();
