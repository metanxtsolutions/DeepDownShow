/* Article pages: theme toggle only (the rest is static) */
(() => {
  const root = document.documentElement, toggle = document.getElementById('themeToggle');
  const light = matchMedia('(prefers-color-scheme: light)');
  const current = () => root.getAttribute('data-theme') || (light.matches ? 'light' : 'dark');
  toggle?.addEventListener('click', () => {
    const next = current() === 'light' ? 'dark' : 'light';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('dds-theme', next); } catch (_) {}
  });
})();
