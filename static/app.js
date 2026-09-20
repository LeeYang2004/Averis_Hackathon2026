const navToggle = document.querySelector('[data-nav-toggle]');
const sidebar = document.querySelector('#sidebar');
const navClosers = document.querySelectorAll('[data-nav-close]');

if (navToggle && sidebar) {
  const closeNav = () => {
    if (!document.body.classList.contains('nav-open')) return;
    document.body.classList.remove('nav-open');
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Open navigation');
    navToggle.focus();
  };

  navToggle.addEventListener('click', () => {
    document.body.classList.add('nav-open');
    navToggle.setAttribute('aria-expanded', 'true');
    navToggle.setAttribute('aria-label', 'Close navigation');
    sidebar.querySelector('a')?.focus();
  });
  navClosers.forEach((closer) => closer.addEventListener('click', closeNav));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeNav();
  });
}
