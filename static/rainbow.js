const RAINBOW = [
  { accent: '#8E24AA', light: '#F3E5F5', hover: '#6A1B9A' },
  { accent: '#E53935', light: '#FFEBEE', hover: '#C62828' },
  { accent: '#F4511E', light: '#FBE9E7', hover: '#D84315' },
  { accent: '#F9A825', light: '#FFF8E1', hover: '#F57F17' },
  { accent: '#43A047', light: '#E8F5E9', hover: '#2E7D32' },
  { accent: '#1E88E5', light: '#E3F2FD', hover: '#1565C0' },
  { accent: '#3949AB', light: '#E8EAF6', hover: '#283593' },
];

const DAY_NAMES = ['日', '一', '二', '三', '四', '五', '六'];

(function () {
  const c = RAINBOW[new Date().getDay()];
  const root = document.documentElement;
  root.style.setProperty('--accent', c.accent);
  root.style.setProperty('--accent-light', c.light);
  root.style.setProperty('--accent-hover', c.hover);

  // Update favicon color to match today's rainbow accent
  const favicon = document.querySelector('link[rel="icon"]');
  if (favicon) {
    const a = c.accent;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="${a}"/><circle cx="16" cy="9" r="2.5" fill="#fff"/><circle cx="9" cy="22" r="2.5" fill="#fff"/><circle cx="23" cy="22" r="2.5" fill="#fff"/><line x1="16" y1="11.5" x2="9" y2="19.5" stroke="#fff" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/><line x1="16" y1="11.5" x2="23" y2="19.5" stroke="#fff" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/><line x1="9" y1="22" x2="23" y2="22" stroke="#fff" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/><path d="M25 3 L25.7 5 L28 5.5 L25.7 6 L25 8 L24.3 6 L22 5.5 L24.3 5 Z" fill="#fff" opacity="0.8"/></svg>`;
    favicon.href = 'data:image/svg+xml,' + encodeURIComponent(svg);
  }
})();
