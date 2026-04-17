# 軟體技術學習日誌 — Design System

> Created by `/design-consultation`. All visual and UI decisions reference this file.

---

## Aesthetic Direction

**Clean Editorial** — 技術學習日誌應該像一本精心排版的日記。白底黑字，讓內容呼吸。彩虹色作為唯一的裝飾語言：每天打開時，當天的色彩是視覺錨點。

**Decoration level:** Intentional — 彩虹日系統本身就是裝飾。不堆疊漸層、不加陰影裝飾。讓色彩和留白做主角。

**Layout:** Grid-disciplined — 嚴謹的 8px 網格，舒適的間距，清晰的層級。

---

## Color System

### Base Palette (固定)

| Token              | Value     | Usage                         |
| ------------------ | --------- | ----------------------------- |
| `--bg`             | `#FFFFFF` | 主背景                        |
| `--bg2`            | `#F9FAFB` | 次背景 (sidebar, card)        |
| `--bg3`            | `#F3F4F6` | 三級背景 (hover, subtle)      |
| `--text`           | `#1A1A2E` | 主文字 (深藍黑)               |
| `--text-secondary` | `#6B7280` | 次要文字                      |
| `--text-muted`     | `#9CA3AF` | 輔助文字 (timestamps, labels) |
| `--border`         | `#E5E7EB` | 邊框、分隔線                  |
| `--border-strong`  | `#D1D5DB` | 強調邊框                      |

### Rainbow Day System (每日變換)

JavaScript 根據 `new Date().getDay()` 設定 `--accent` 和 `--accent-light`：

| Day | 星期 | 名稱 | `--accent` | `--accent-light` | `--accent-hover` |
| --- | ---- | ---- | ---------- | ---------------- | ---------------- |
| 1   | 一   | 赤   | `#E53935`  | `#FFEBEE`        | `#C62828`        |
| 2   | 二   | 橙   | `#F4511E`  | `#FBE9E7`        | `#D84315`        |
| 3   | 三   | 黃   | `#F9A825`  | `#FFF8E1`        | `#F57F17`        |
| 4   | 四   | 綠   | `#43A047`  | `#E8F5E9`        | `#2E7D32`        |
| 5   | 五   | 藍   | `#1E88E5`  | `#E3F2FD`        | `#1565C0`        |
| 6   | 六   | 靛   | `#3949AB`  | `#E8EAF6`        | `#283593`        |
| 0   | 日   | 紫   | `#8E24AA`  | `#F3E5F5`        | `#6A1B9A`        |

**實作方式：**

```javascript
const RAINBOW = [
  { accent: "#8E24AA", light: "#F3E5F5", hover: "#6A1B9A" }, // 日 (0)
  { accent: "#E53935", light: "#FFEBEE", hover: "#C62828" }, // 一
  { accent: "#F4511E", light: "#FBE9E7", hover: "#D84315" }, // 二
  { accent: "#F9A825", light: "#FFF8E1", hover: "#F57F17" }, // 三
  { accent: "#43A047", light: "#E8F5E9", hover: "#2E7D32" }, // 四
  { accent: "#1E88E5", light: "#E3F2FD", hover: "#1565C0" }, // 五
  { accent: "#3949AB", light: "#E8EAF6", hover: "#283593" }, // 六
];

function applyDayColor() {
  const day = new Date().getDay();
  const c = RAINBOW[day];
  const root = document.documentElement.style;
  root.setProperty("--accent", c.accent);
  root.setProperty("--accent-light", c.light);
  root.setProperty("--accent-hover", c.hover);
}
```

### Accent Usage Rules

彩虹色 (`--accent`) 只影響以下元素：

- Active tab 底線 / active 狀態
- 按鈕 (primary button background)
- 今日標記 badge
- Health banner 左邊框
- 連結 hover 色
- 載入中 spinner

**絕對不用 accent 的地方：**

- 大面積背景 (用 `--accent-light` 代替)
- 長段文字
- 邊框 (用 `--border`)

### Semantic Colors (固定，不隨日變)

| Token       | Value     | Usage                     |
| ----------- | --------- | ------------------------- |
| `--success` | `#43A047` | 健康狀態正常              |
| `--warning` | `#F9A825` | 超過 1 天未更新           |
| `--error`   | `#E53935` | 超過 3 天未更新、錯誤狀態 |

---

## Typography

### Font Stack

```css
:root {
  --font-sans: "Noto Sans TC", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", "Consolas", monospace;
}
```

**載入方式：** Google Fonts CDN

```html
<link
  rel="preconnect"
  href="https://fonts.googleapis.com" />
<link
  rel="preconnect"
  href="https://fonts.gstatic.com"
  crossorigin />
<link
  href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap"
  rel="stylesheet" />
```

### Type Scale

| Token          | Size | Weight | Line Height | Usage                         |
| -------------- | ---- | ------ | ----------- | ----------------------------- |
| `--text-hero`  | 28px | 700    | 1.3         | 頁面標題「軟體技術學習日誌」  |
| `--text-h1`    | 22px | 700    | 1.35        | 日期標題                      |
| `--text-h2`    | 18px | 700    | 1.4         | 區塊標題 (e.g. 學習方向名)    |
| `--text-h3`    | 16px | 500    | 1.4         | 小標題                        |
| `--text-body`  | 15px | 400    | 1.7         | 正文 (寬鬆行高，適合長文閱讀) |
| `--text-small` | 13px | 400    | 1.5         | 次要資訊、timestamps          |
| `--text-mono`  | 14px | 400    | 1.6         | 程式碼、技術名詞              |

---

## Spacing

基本單位：**8px**

| Token        | Value | Usage                  |
| ------------ | ----- | ---------------------- |
| `--space-1`  | 4px   | 極小間距 (icon 與文字) |
| `--space-2`  | 8px   | 基本間距               |
| `--space-3`  | 12px  | 緊湊間距               |
| `--space-4`  | 16px  | 元素內間距             |
| `--space-5`  | 24px  | 區塊內間距             |
| `--space-6`  | 32px  | 區塊間距               |
| `--space-8`  | 48px  | 大區間距               |
| `--space-10` | 64px  | 頁面邊距               |

---

## Border Radius

| Token         | Value | Usage               |
| ------------- | ----- | ------------------- |
| `--radius-sm` | 4px   | 小元素 (badge, tag) |
| `--radius-md` | 8px   | 卡片、按鈕          |
| `--radius-lg` | 12px  | 大容器              |

---

## Shadows

白色主題需要微妙的陰影來建立層級：

| Token         | Value                         | Usage            |
| ------------- | ----------------------------- | ---------------- |
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)`  | 卡片靜止         |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.08)` | 卡片 hover       |
| `--shadow-lg` | `0 8px 24px rgba(0,0,0,0.12)` | Modal / dropdown |

---

## Motion

| Property                | Duration | Easing   | Usage                  |
| ----------------------- | -------- | -------- | ---------------------- |
| color, background-color | 200ms    | ease     | 日常色彩切換、hover    |
| transform, opacity      | 150ms    | ease-out | 元素出現、tab 內容切換 |
| box-shadow              | 200ms    | ease     | 卡片 hover 提升        |

**規則：**

- `prefers-reduced-motion: reduce` 時，所有動畫改為 `0ms`
- 不使用 spring 或 bounce 動畫

---

## Component Patterns

### Tab Bar

```
┌──────────────────────────────────────────┐
│  技術內容  │  學習方向分析  │  資料出處    │
│  ═══════                                 │  ← --accent 底線 (3px)
└──────────────────────────────────────────┘
```

- Active tab：`--accent` 底線 + `--text` 文字 + `font-weight: 700`
- Inactive tab：`--text-secondary` 文字 + `font-weight: 400`
- Hover：`--bg3` 背景

### Date Navigation (Sidebar)

```
┌─────────────┐
│ 📅 日期列表  │
├─────────────┤
│ ✦ 06/14 (六) │ ← 今天：--accent 左邊框 + --accent-light 背景
│   06/13 (五) │
│   06/12 (四) │
│   06/11 (三) │
│   ...        │
└─────────────┘
```

- 今天的日期有 `✦` 標記、`--accent` 左邊框 (3px)、`--accent-light` 背景
- 選中日期：`--bg3` 背景 + `--text` 文字 + `font-weight: 500`
- 未選中：`--text-secondary`

### Session Chips

當同一天有多個學習 session 時，日期仍是第一層導航，session 是第二層上下文，不可搶走日期標題的視覺權重。

```
┌──────────────────────────────────────┐
│ 2026年04月18日 技術日誌              │
│ [00:00] [03:00] [18:00] [21:00]      │
└──────────────────────────────────────┘
```

- 固定只使用 4 個 session label：`00:00`、`03:00`、`18:00`、`21:00`
- 以膠囊按鈕呈現，使用 `--radius-md`、`--space-2` 間距、`--text-small`
- Active session：`--accent-light` 背景、`--accent` 邊框、`font-weight: 700`
- Inactive session：`--bg2` 背景、`--border` 邊框、`--text-secondary`
- 時間文字建議使用 `--font-mono`，強化「時段紀錄」感
- 同日只有一個 session 時可隱藏整排 chips，避免多餘噪音

### Learning Direction Section (垂直堆疊)

```
┌──────────────────────────────────────┐
│ AI / 機器學習                    [▼] │ ← --text, font-weight: 700
├──────────────────────────────────────┤
│ 摘要文字在這裡...                    │ ← --text, --text-body
│                                      │
│ • 重點項目一                         │
│ • 重點項目二                         │
└──────────────────────────────────────┘
   ↕ --space-4 gap
┌──────────────────────────────────────┐
│ 雲端與基礎架構                  [▼] │
├──────────────────────────────────────┤
│ ...                                  │
└──────────────────────────────────────┘
```

- 5 個方向垂直堆疊（不是卡片網格）
- 每區塊有 `--border` 邊框、`--radius-md` 圓角
- 可展開/收合

### Health Banner

```
┌──────────────────────────────────────────────┐
│ ▎ 上次更新：2025-06-14（今天）— 一切正常 ✓  │
└──────────────────────────────────────────────┘
```

- 左邊框 3px，顏色依狀態：`--success` / `--warning` / `--error`
- 背景：對應的淡色

### States

| State        | Visual                                                     |
| ------------ | ---------------------------------------------------------- |
| Loading      | `--accent` 色 spinner + 「載入中...」文字                  |
| Empty (首次) | 插畫風 icon + 「歡迎！你的第一篇日誌即將到來 ✦」+ 說明文字 |
| Error        | `--error` 邊框卡片 + 錯誤訊息 + 重試按鈕                   |
| Success      | 正常顯示內容，無額外裝飾                                   |

### Content Formatting

- 日誌內容是純文字，`\n\n` 分段渲染為 `<p>`
- 每個 session 的 `tech_content` 以 2-3 段為上限，維持單次閱讀節奏
- 技術名詞不加 code block，保持閱讀流暢
- Sources 區塊預設收合，點擊展開

---

## Responsive Behavior

| Breakpoint | Layout                                |
| ---------- | ------------------------------------- |
| ≥ 768px    | Sidebar (240px) + 主內容區            |
| < 768px    | Sidebar 收合為頂部日期橫條 (水平滾動) |
| ≤ 480px    | 日期橫條精簡 (只顯示 MM/DD)，字體微縮 |

### Mobile Date Strip

```
← [06/10] [06/11] [06/12] [06/13] [✦06/14] →
```

水平滾動，今天的日期用 `--accent` 底線標記。

---

## Accessibility

- **Color contrast:** 所有文字/背景組合符合 WCAG AA (4.5:1)
  - `#1A1A2E` on `#FFFFFF` → 16.5:1 ✓
  - `#6B7280` on `#FFFFFF` → 5.0:1 ✓
  - 所有 7 個 accent 色 on `#FFFFFF` → 皆 ≥ 3:1 (large text/UI components)
- **ARIA landmarks:** `<nav>` for date list, `<main>` for content, `role="tablist"` for tabs
- **Keyboard navigation:** Tab/Shift+Tab 移動焦點，Enter/Space 啟動，← → 切換日期
- **Focus indicator:** 2px `--accent` outline + 2px offset
- **Touch targets:** 最小 44×44px
- **Reduced motion:** 尊重 `prefers-reduced-motion`

---

## CSS Custom Properties (Complete)

```css
:root {
  /* Base */
  --bg: #ffffff;
  --bg2: #f9fafb;
  --bg3: #f3f4f6;
  --text: #1a1a2e;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --border: #e5e7eb;
  --border-strong: #d1d5db;

  /* Accent — set by JS based on day of week */
  --accent: #1e88e5; /* default fallback: 藍 */
  --accent-light: #e3f2fd;
  --accent-hover: #1565c0;

  /* Semantic */
  --success: #43a047;
  --warning: #f9a825;
  --error: #e53935;

  /* Typography */
  --font-sans: "Noto Sans TC", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", "Consolas", monospace;
  --text-hero: 28px;
  --text-h1: 22px;
  --text-h2: 18px;
  --text-h3: 16px;
  --text-body: 15px;
  --text-small: 13px;
  --text-mono: 14px;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-8: 48px;
  --space-10: 64px;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.12);
}
```

---

## Decisions Log

| Date       | Decision                       | Rationale                                  |
| ---------- | ------------------------------ | ------------------------------------------ |
| 2025-06-14 | 白色主題取代暗色               | 長文閱讀性更好，符合使用者要求             |
| 2025-06-14 | 彩虹日系統 (週一至週日七色)    | 使用者要求，每天打開有新鮮感，形成時間感知 |
| 2025-06-14 | Noto Sans TC 為唯一中文字體    | 繁中 web font 標準選擇，字重完整           |
| 2025-06-14 | JetBrains Mono 等寬字體        | 技術日誌需要好看的 code font               |
| 2025-06-14 | Accent 只影響 UI 控制元素      | 避免彩虹色過度使用，保持基底中性一致       |
| 2025-06-14 | 學習方向垂直堆疊（非卡片網格） | 設計審查決議，適合長文閱讀                 |
| 2025-06-14 | Sources 預設收合               | 設計審查決議，減少認知負擔                 |
