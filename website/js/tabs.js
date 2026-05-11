/**
 * SLIM — Tab switcher for index.html
 * © 2026 Sasidhar Nagandla. MIT License.
 */
(function () {
  'use strict';

  // Whitelist prevents DOM manipulation via unexpected tab names (Finding 8 & 13)
  const ALLOWED_TABS = new Set(['sigils', 'example', 'schemas', 'types']);

  window.showTab = function showTab(name, evt) {
    if (!ALLOWED_TABS.has(name)) return;
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    const panel = document.getElementById('tab-' + name);
    if (panel) panel.classList.add('active');
    // Use the passed event object — never the deprecated window.event global (Finding 8)
    if (evt && evt.currentTarget) evt.currentTarget.classList.add('active');
  };
})();
