(function () {
  var d = document, h = d.documentElement;

  // preloader: drop it after its fade-out (and never let it block longer than 3s)
  var pl = d.getElementById('preloader');
  function plDone() { h.classList.remove('pl'); if (pl && pl.parentNode) pl.parentNode.removeChild(pl); }
  if (pl) {
    if (h.classList.contains('pl')) { pl.addEventListener('animationend', function (e) { if (e.target === pl) plDone(); }); setTimeout(plDone, 3000); }
    else plDone();
  }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  // sticky header shadow
  var hdr = d.getElementById('hdr');
  function onScroll() { if (hdr) hdr.classList.toggle('scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // mobile menu
  var mnav = d.getElementById('mnav'), burger = d.getElementById('burger'), mclose = d.getElementById('mclose');
  function menu(open) {
    if (!mnav) return;
    mnav.classList.toggle('open', open);
    burger && burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    d.body.style.overflow = open ? 'hidden' : '';
  }
  burger && burger.addEventListener('click', function () { menu(true); });
  mclose && mclose.addEventListener('click', function () { menu(false); });
  mnav && mnav.addEventListener('click', function (e) { if (e.target.closest('a')) menu(false); });
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape') menu(false); });

  // версия для слабовидящих
  var a11y = d.getElementById('a11y');
  if (store('a11y') === '1') h.classList.add('a11y');
  a11y && a11y.addEventListener('click', function () {
    var on = h.classList.toggle('a11y');
    store('a11y', on ? '1' : '0');
    a11y.lastChild.textContent = on ? 'Обычная версия' : 'Версия для слабовидящих';
  });
  if (a11y && h.classList.contains('a11y')) a11y.lastChild.textContent = 'Обычная версия';

  // reveal on scroll
  var rv = d.querySelectorAll('.rv');
  if (/[?&]shot\b/.test(location.search)) rv.forEach(function (el) { el.classList.add('in'); });
  else if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    rv.forEach(function (el, i) { el.style.transitionDelay = (i % 4) * 60 + 'ms'; io.observe(el); });
  } else rv.forEach(function (el) { el.classList.add('in'); });

  // demo form: nothing is sent
  d.querySelectorAll('form[data-demo]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = f.querySelector('.form-ok');
      Array.prototype.forEach.call(f.children, function (c) { if (c !== ok) c.hidden = true; });
      ok.hidden = false;
    });
  });

  // price search
  var q = d.getElementById('psearch');
  if (q) {
    var rows = d.querySelectorAll('.ptable tr[data-q]'), cats = d.querySelectorAll('.pcat'), empty = d.getElementById('pempty');
    q.addEventListener('input', function () {
      var v = q.value.trim().toLowerCase().replace(/ё/g, 'е'), any = false;
      rows.forEach(function (r) {
        var hit = !v || r.getAttribute('data-q').replace(/ё/g, 'е').indexOf(v) > -1;
        r.hidden = !hit;
      });
      cats.forEach(function (c) {
        var vis = c.querySelectorAll('tr[data-q]:not([hidden])').length;
        c.hidden = !vis; if (vis) any = true;
      });
      empty.hidden = any;
    });
  }
})();
