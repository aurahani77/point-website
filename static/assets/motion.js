/* Point — scroll motion layer for the homepage (runs on top of the React bundle). */
(function () {
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var root = document.documentElement;

  function ready(fn) {
    if (document.querySelector('.hero h1')) return fn();
    var mo = new MutationObserver(function () {
      if (document.querySelector('.hero h1')) { mo.disconnect(); fn(); }
    });
    mo.observe(document.body, { childList: true, subtree: true });
  }

  /* wrap each word of an element's text nodes in <span class="w"><span>word</span></span> */
  function splitWords(el) {
    if (!el || el.dataset.split) return;
    el.dataset.split = '1';
    var i = 0;
    (function walk(node) {
      [].slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var parts = n.nodeValue.split(/(\s+)/);
          var frag = document.createDocumentFragment();
          parts.forEach(function (p) {
            if (!p) return;
            if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(p)); return; }
            var w = document.createElement('span'); w.className = 'w';
            var inner = document.createElement('span'); inner.textContent = p;
            inner.style.setProperty('--i', i++);
            w.appendChild(inner); frag.appendChild(w);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.tagName !== 'BR') walk(n);
      });
    })(el);
  }

  function countUp(el) {
    var t = el.firstChild && el.firstChild.nodeType === 3 ? el.firstChild : null;
    if (!t) return;
    var m = t.nodeValue.match(/^(\D*)([\d,]+)(\D*)$/);
    if (!m) return;
    var end = parseInt(m[2].replace(/,/g, ''), 10), dur = 1600, t0 = null;
    function fmt(n) { return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
    function step(ts) {
      if (!t0) t0 = ts;
      var k = Math.min(1, (ts - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      t.nodeValue = m[1] + fmt(Math.round(end * e)) + m[3];
      if (k < 1) requestAnimationFrame(step);
    }
    t.nodeValue = m[1] + '0' + m[3];
    requestAnimationFrame(step);
  }

  ready(function () {
    if (reduce) return;
    root.classList.add('motion');

    /* progress bar + header state */
    var bar = document.createElement('div'); bar.className = 'scroll-progress'; document.body.appendChild(bar);
    var header = document.querySelector('header');

    /* split headings */
    splitWords(document.querySelector('.hero h1'));
    document.querySelectorAll('.section-head h2, .quality-copy h2, .story-copy h2, .contact-copy h2').forEach(splitWords);
    requestAnimationFrame(function () { document.querySelector('.hero').classList.add('in'); });

    /* reveal-on-scroll for headings, images, stats */
    var targets = document.querySelectorAll('.section-head, .quality-copy, .story-copy, .contact-copy, .quality-image, .stats, .story-card, .category-card, .branch-list, .map-panel');
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('in');
        if (e.target.classList.contains('stats')) e.target.querySelectorAll('strong').forEach(countUp);
        io.unobserve(e.target);
      });
    }, { threshold: 0.18, rootMargin: '0px 0px -8% 0px' });
    targets.forEach(function (t) { io.observe(t); });

    /* stagger category cards */
    document.querySelectorAll('.category-card').forEach(function (c, i) { c.style.setProperty('--d', (i % 4) * 90 + Math.floor(i / 4) * 120 + 'ms'); });

    /* parallax */
    var px = [
      ['.hero .image-card img', 0.10, 'img'],
      ['.hero .visual-ring', -0.06, 'rot'],
      ['.hero .yellow-disc', -0.18, 'rot'],
      ['.hero .note-one', -0.12],
      ['.hero .note-two', 0.08],
      ['.hero .orb-one', 0.25],
      ['.hero .orb-two', -0.2],
      ['.quality-image img', 0.08, 'img'],
      ['.quality-seal', -0.1, 'rot'],
      ['.story-visual svg', 0.06],
      ['.categories-mark', -0.08]
    ].map(function (p) { return { el: document.querySelector(p[0]), k: p[1], mode: p[2] }; }).filter(function (p) { return p.el; });

    var wide = matchMedia('(min-width: 900px)');
    var ticking = false;
    function frame() {
      ticking = false;
      var y = window.scrollY, h = document.documentElement.scrollHeight - innerHeight;
      bar.style.transform = 'scaleX(' + (h > 0 ? y / h : 0) + ')';
      if (header) header.classList.toggle('scrolled', y > 40);
      if (!wide.matches) return;
      px.forEach(function (p) {
        var r = p.el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > innerHeight + 200) return;
        var off = (r.top + r.height / 2 - innerHeight / 2) * p.k;
        if (p.mode === 'img') p.el.style.transform = 'translate3d(0,' + off.toFixed(1) + 'px,0) scale(1.12)';
        else if (p.mode === 'rot') p.el.style.transform = 'rotate(' + (off * 0.6).toFixed(1) + 'deg)';
        else p.el.style.transform = 'translate3d(0,' + off.toFixed(1) + 'px,0)';
      });
    }
    function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll);
    frame();
  });
})();
