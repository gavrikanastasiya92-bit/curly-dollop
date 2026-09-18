// floating ember particles — one set per .particles container (hero, founder, ...)
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!prefersReducedMotion) {
  document.querySelectorAll('.particles').forEach((container) => {
    const count = container.id === 'particles' ? 14 : 9;
    for (let i = 0; i < count; i++) {
      const p = document.createElement('div');
      p.className = 'particle';
      p.style.left = (Math.random() * 100) + '%';
      p.style.animationDelay = (Math.random() * 9) + 's';
      p.style.animationDuration = (7 + Math.random() * 5) + 's';
      p.style.setProperty('--dx', (Math.random() * 60 - 30) + 'px');
      container.appendChild(p);
    }
  });
}

// nav background on scroll
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 60);
});

// reveal-on-scroll for text blocks and cards
const revealObs = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('in'), i * 70);
      revealObs.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });

document
  .querySelectorAll('#about .about-text, #directions .card, #stay .room-card')
  .forEach((el) => revealObs.observe(el));
