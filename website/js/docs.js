/**
 * SLIM — Docs sidebar active-section tracker
 * © 2026 Sasidhar Nagandla. MIT License.
 */
(function () {
  'use strict';

  const links    = document.querySelectorAll('.sidebar-link');
  const sections = Array.from(document.querySelectorAll('.docs-section[id]'));

  function setActive(id) {
    links.forEach(l => {
      l.classList.toggle('active', l.getAttribute('href') === '#' + id);
    });
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) setActive(e.target.id); });
  }, { rootMargin: '-60px 0px -70% 0px', threshold: 0 });

  sections.forEach(s => observer.observe(s));
})();
