/**
 * SLIM — Tab switcher for index.html
 * © 2026 Sasidhar Nagandla. MIT License.
 */
(function () {
  'use strict';

  // Whitelist prevents DOM manipulation via unexpected tab names
  const ALLOWED_TABS = new Set(['sigils', 'example', 'schemas', 'types']);

  function showTab(name, btn) {
    if (!ALLOWED_TABS.has(name)) return;
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    const panel = document.getElementById('tab-' + name);
    if (panel) panel.classList.add('active');
    if (btn) btn.classList.add('active');
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.tab-btn[data-tab]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        showTab(btn.dataset.tab, btn);
      });
    });
  });
})();
