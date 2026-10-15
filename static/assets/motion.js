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

/* Point — "journey" layer (2026-10): hand-drawn yellow doodle that draws itself between homepage sections,
   and a delivery route (branch -> home) animated on the branches map. Pure SVG, no libraries. */
(function () {
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var NS = 'http://www.w3.org/2000/svg';
  var DOODLES = [
    'M 980 60 C 900 20, 820 20, 760 70 C 700 120, 640 150, 580 110 C 540 80, 580 40, 620 60 C 670 85, 600 160, 500 150 C 400 140, 340 60, 250 60 C 170 60, 120 110, 60 90',
    'M 980 110 C 880 160, 800 150, 720 100 C 650 55, 560 40, 480 80 C 420 110, 380 150, 300 120 C 240 96, 270 50, 320 62 C 380 76, 340 140, 250 140 C 160 140, 100 70, 40 60',
    'M 980 90 C 900 40, 840 40, 780 80 C 720 120, 650 140, 590 100 C 530 60, 450 50, 390 90 C 330 130, 250 150, 190 110 C 150 84, 190 40, 230 60 C 280 84, 200 150, 120 130 C 80 120, 50 100, 30 80',
    'M 980 70 C 900 110, 820 150, 740 110 C 680 80, 700 30, 750 50 C 810 75, 730 150, 620 140 C 500 128, 460 50, 340 70 C 240 86, 200 140, 110 130'
  ];

  function el(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function waitFor(sel, cb) {
    if (document.querySelector(sel)) return cb();
    var mo = new MutationObserver(function () {
      if (document.querySelector(sel)) { mo.disconnect(); cb(); }
    });
    mo.observe(document.body, { childList: true, subtree: true });
  }
  var clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };
  var ease = function (k) { return k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2; };

  /* ---------- A) doodle between sections ---------- */
  function initDoodles() {
    var secs = ['.why-section', '.categories-section', '.quality', '.experience', '.branches']
      .map(function (q) { return document.querySelector(q); }).filter(Boolean);
    if (secs.length < 2) return;
    var bands = [];
    for (var i = 1; i < secs.length; i++) {
      var svg = el('svg', { viewBox: '0 0 1000 180', class: 'journey-doodle', 'aria-hidden': 'true', focusable: 'false' }, document.body);
      var g = el('g', {}, svg);
      if (i % 2 === 0) g.setAttribute('transform', 'translate(1000 0) scale(-1 1)');
      var p = el('path', { d: DOODLES[(i - 1) % DOODLES.length], pathLength: '1' }, g);
      p.style.strokeDasharray = '1'; p.style.strokeDashoffset = '1';
      var arrow = null;
      if (i === secs.length - 1) { arrow = el('path', { d: 'M 84 112 L 108 134 L 76 150', class: 'arrow' }, g); arrow.style.opacity = 0; }
      bands.push({ svg: svg, p: p, arrow: arrow, next: secs[i] });
    }
    function update() {
      bands.forEach(function (b) {
        var r = b.svg.getBoundingClientRect();
        var k = clamp((innerHeight * 0.92 - (r.top + r.height * 0.3)) / (innerHeight * 0.6), 0, 1);
        b.p.style.strokeDashoffset = (1 - k).toFixed(4);
        if (b.arrow) b.arrow.style.opacity = k > 0.97 ? 1 : 0;
      });
    }
    function place() {
      var vw = document.documentElement.clientWidth;
      bands.forEach(function (b) {
        b.svg.style.width = vw + 'px';
        var h = b.svg.getBoundingClientRect().height;
        b.svg.style.top = (b.next.getBoundingClientRect().top + window.scrollY - h / 2) + 'px';
      });
      update();
    }
    var t = false;
    addEventListener('scroll', function () { if (!t) { t = true; requestAnimationFrame(function () { t = false; update(); }); } }, { passive: true });
    addEventListener('resize', place);
    addEventListener('load', place);
    if (window.ResizeObserver) new ResizeObserver(place).observe(document.querySelector('.app') || document.body);
    place(); setTimeout(place, 1200);
  }

  /* ---------- B) delivery route on the branches map ---------- */
  function rounded(pts, r) {
    var d = 'M ' + pts[0][0] + ' ' + pts[0][1];
    for (var i = 1; i < pts.length - 1; i++) {
      var a = pts[i - 1], b = pts[i], c = pts[i + 1];
      var l1 = Math.hypot(b[0] - a[0], b[1] - a[1]), l2 = Math.hypot(c[0] - b[0], c[1] - b[1]);
      var rr = Math.min(r, l1 / 2, l2 / 2);
      var p1 = [b[0] - (b[0] - a[0]) / l1 * rr, b[1] - (b[1] - a[1]) / l1 * rr];
      var p2 = [b[0] + (c[0] - b[0]) / l2 * rr, b[1] + (c[1] - b[1]) / l2 * rr];
      d += ' L ' + p1[0].toFixed(1) + ' ' + p1[1].toFixed(1) + ' Q ' + b[0] + ' ' + b[1] + ' ' + p2[0].toFixed(1) + ' ' + p2[1].toFixed(1);
    }
    var e = pts[pts.length - 1];
    return d + ' L ' + e[0].toFixed(1) + ' ' + e[1].toFixed(1);
  }

  function initRoute() {
    var panel = document.querySelector('.branches .map-panel');
    if (!panel || panel.querySelector('.route-layer')) return;
    var svg = el('svg', { class: 'route-layer', 'aria-hidden': 'true', focusable: 'false' }, panel);
    var base = el('path', { class: 'route-base' }, svg);
    var home = el('g', { class: 'route-home' }, svg);
    el('circle', { r: 21, class: 'rh-bg' }, home);
    el('path', { d: 'M -9 1 L 0 -8 L 9 1 M -6.5 -1 V 8 H 6.5 V -1', class: 'rh-icon' }, home);
    var label = el('text', { class: 'rh-label', y: 40, 'text-anchor': 'middle' }, home);
    label.textContent = 'بيتك';
    var courier = el('circle', { r: 8, class: 'route-courier' }, svg);

    var len = 0, t0 = null, raf = null, visible = false, sig = '';
    var DRAW = 1200, TRAVEL = 3000, HOLD = 1600;

    function layout() {
      var pr = panel.getBoundingClientRect();
      if (pr.width < 50) return false;
      svg.setAttribute('viewBox', '0 0 ' + pr.width + ' ' + pr.height);
      var pins = [].slice.call(panel.querySelectorAll('.map-pin'));
      var act = panel.querySelector('.map-pin.active') || pins[0];
      if (!act) return false;
      var ar = act.getBoundingClientRect();
      var s = [ar.left + ar.width / 2 - pr.left, ar.bottom - pr.top - 2];
      var cands = [[.12, .84], [.88, .16], [.12, .16], [.88, .84], [.5, .88], [.5, .14]].map(function (c) { return [c[0] * pr.width, c[1] * pr.height]; });
      var centers = pins.map(function (p) { var r = p.getBoundingClientRect(); return [r.left + r.width / 2 - pr.left, r.top + r.height / 2 - pr.top]; });
      var best = null, bs = -1;
      cands.forEach(function (c) {
        var near = Math.min.apply(null, centers.map(function (q) { return Math.hypot(c[0] - q[0], c[1] - q[1]); }).concat([999]));
        if (near < 70) return;
        var dx = Math.abs(c[0] - s[0]), dy = Math.abs(c[1] - s[1]);
        var sc = Math.hypot(dx, dy) * (dx > pr.width * .22 && dy > pr.height * .3 ? 2 : 1);  /* prefer routes with a real bend */
        if (sc > bs) { bs = sc; best = c; }
      });
      if (!best) best = cands[0];
      var ym = (s[1] + best[1]) / 2;
      var d = rounded([s, [s[0], ym], [best[0], ym], best], 22);
      base.setAttribute('d', d);
      len = base.getTotalLength();
      base.style.strokeDasharray = len; base.style.strokeDashoffset = len;
      home.setAttribute('transform', 'translate(' + best[0] + ' ' + best[1] + ')');
      home.classList.remove('on');
      courier.style.opacity = 0;
      sig = pins.indexOf(act) + '|' + s[0].toFixed(0) + '|' + s[1].toFixed(0) + '|' + pr.width.toFixed(0);
      return true;
    }
    function tick(ts) {
      if (!visible) { raf = null; return; }
      if (t0 === null) t0 = ts;
      var t = ts - t0;
      if (t >= DRAW + TRAVEL + HOLD) { t0 = ts - DRAW; t = DRAW; }
      if (t < DRAW) {
        base.style.strokeDashoffset = (len * (1 - ease(t / DRAW))).toFixed(1);
        courier.style.opacity = 0; home.classList.remove('on');
      } else {
        base.style.strokeDashoffset = 0; home.classList.add('on');
        var k = clamp((t - DRAW) / TRAVEL, 0, 1), pt = base.getPointAtLength(len * ease(k));
        courier.setAttribute('cx', pt.x); courier.setAttribute('cy', pt.y); courier.style.opacity = 1;
      }
      raf = requestAnimationFrame(tick);
    }
    function restart() {
      if (raf) { cancelAnimationFrame(raf); raf = null; }
      if (!layout()) return;
      t0 = null;
      if (visible) raf = requestAnimationFrame(tick);
    }
    new IntersectionObserver(function (es) {
      visible = es[0].isIntersecting;
      if (visible && !raf) { t0 = null; raf = requestAnimationFrame(tick); }
    }, { threshold: 0.35 }).observe(panel);

    var deb;
    new MutationObserver(function (ms) {
      if (ms.every(function (m) { return svg.contains(m.target); })) return;
      clearTimeout(deb);
      deb = setTimeout(function () {
        var cur = panel.querySelector('.map-pin.active');
        var pr = panel.getBoundingClientRect(), ar = cur && cur.getBoundingClientRect();
        var s2 = cur ? [ar.left + ar.width / 2 - pr.left, ar.bottom - pr.top - 2] : [0, 0];
        var pins = [].slice.call(panel.querySelectorAll('.map-pin'));
        var now = pins.indexOf(cur) + '|' + s2[0].toFixed(0) + '|' + s2[1].toFixed(0) + '|' + pr.width.toFixed(0);
        if (now !== sig) restart();
      }, 60);
    }).observe(panel, { subtree: true, childList: true, attributes: true, attributeFilter: ['class', 'style'] });
    addEventListener('resize', function () { clearTimeout(deb); deb = setTimeout(restart, 150); });
    restart();
  }

  waitFor('.hero h1', function () {
    waitFor('.branches .map-panel', function () {
      document.documentElement.classList.add('journey');
      initDoodles();
      initRoute();
    });
  });
})();
