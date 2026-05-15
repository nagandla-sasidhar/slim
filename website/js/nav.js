/**
 * SLIM — Mobile nav hamburger toggle
 * © 2026 Sasidhar Nagandla. MIT License.
 */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    const nav       = document.getElementById('main-nav');
    const hamburger = document.getElementById('nav-hamburger');
    if (!nav || !hamburger) return;

    hamburger.addEventListener('click', function () {
      const open = nav.classList.toggle('nav-open');
      hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    // Close menu when any nav link is clicked
    nav.querySelectorAll('.nav-link, .nav-cta').forEach(function (link) {
      link.addEventListener('click', function () {
        nav.classList.remove('nav-open');
        hamburger.setAttribute('aria-expanded', 'false');
      });
    });

    // Close menu on outside click
    document.addEventListener('click', function (e) {
      if (!nav.contains(e.target)) {
        nav.classList.remove('nav-open');
        hamburger.setAttribute('aria-expanded', 'false');
      }
    });
  });
})();
