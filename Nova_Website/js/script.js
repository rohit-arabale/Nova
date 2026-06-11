/* script.js — Nova AI Assistant Portfolio Website
   Handles: nav scroll effects, scroll reveal animations,
   mobile menu, active link highlighting, smooth UX.
*/

// ── Nav Scroll Effect ──────────────────────────────────────────────
const nav = document.querySelector('.nav');
if (nav) {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      nav.style.background = 'rgba(8, 8, 16, 0.97)';
      nav.style.boxShadow = '0 2px 24px rgba(0,0,0,0.4)';
    } else {
      nav.style.background = 'rgba(8, 8, 16, 0.85)';
      nav.style.boxShadow = 'none';
    }
  });
}

// ── Mobile Menu ────────────────────────────────────────────────────
const hamburger = document.querySelector('.nav-hamburger');
const navLinks   = document.querySelector('.nav-links');

if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    const isOpen = navLinks.style.display === 'flex';
    navLinks.style.display = isOpen ? 'none' : 'flex';
    navLinks.style.flexDirection = 'column';
    navLinks.style.position = 'absolute';
    navLinks.style.top = '70px';
    navLinks.style.left = '0';
    navLinks.style.right = '0';
    navLinks.style.background = 'rgba(8,8,16,0.98)';
    navLinks.style.padding = '16px';
    navLinks.style.borderBottom = '1px solid rgba(120,100,255,0.18)';
    hamburger.textContent = isOpen ? '☰' : '✕';
  });
}

// ── Scroll Reveal (IntersectionObserver) ──────────────────────────
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      // Optionally unobserve after first reveal:
      // revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

// ── Active Nav Link ────────────────────────────────────────────────
// Highlights the nav link that matches the current page
(function highlightActiveLink() {
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === path || (path === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
})();

// ── Counter Animation (for stats) ─────────────────────────────────
function animateCounter(el, target, duration = 1400) {
  const start = performance.now();
  const update = (time) => {
    const elapsed = time - start;
    const progress = Math.min(elapsed / duration, 1);
    // Ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(eased * target);
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

// Trigger counters when they come into view
const statObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const target = parseInt(el.dataset.count, 10);
      if (!isNaN(target)) animateCounter(el, target);
      statObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('[data-count]').forEach(el => statObserver.observe(el));

// Scroll-linked motion for the large AI bot image on the homepage.
const motionObjects = document.querySelectorAll('.ai-bot-parallax');
let motionTicking = false;

function updateMotionObjects() {
  const scrollY = window.scrollY;
  motionObjects.forEach((el, index) => {
    const speed = parseFloat(el.dataset.speed || '0');
    const drift = parseFloat(el.dataset.drift || '0');
    const y = scrollY * speed;
    const x = Math.sin((scrollY / 260) + index) * drift;
    const rotate = Math.sin((scrollY / 520) + index) * 5;
    const scale = 1 + Math.sin(scrollY / 700) * 0.025;
    el.style.transform = `translate3d(${x}px, ${y}px, 0) rotate(${rotate}deg) scale(${scale})`;
  });
  motionTicking = false;
}

if (motionObjects.length) {
  updateMotionObjects();
  window.addEventListener('scroll', () => {
    if (!motionTicking) {
      requestAnimationFrame(updateMotionObjects);
      motionTicking = true;
    }
  }, { passive: true });
}

// ── Copy Code Snippet ──────────────────────────────────────────────
document.querySelectorAll('.copy-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.target;
    const el = document.querySelector(target);
    if (!el) return;
    navigator.clipboard.writeText(el.textContent.trim()).then(() => {
      const orig = btn.textContent;
      btn.textContent = '✓ Copied!';
      btn.style.color = '#00e676';
      setTimeout(() => { btn.textContent = orig; btn.style.color = ''; }, 2000);

    });
  });
});
