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
})();
