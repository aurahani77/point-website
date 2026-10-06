/* Footer newsletter: sends the email to n8n (Point — Newsletter Signup) */
(function () {
  var URL = 'https://aurash77.app.n8n.cloud/webhook/point-newsletter';
  function box(el) { return el && el.closest && el.closest('.footer-news'); }
  function msg(b, text, ok) {
    var m = b.querySelector('.news-msg');
    if (!m) { m = document.createElement('p'); m.className = 'news-msg'; m.setAttribute('role', 'status'); b.appendChild(m); }
    m.textContent = text; m.classList.toggle('err', !ok);
  }
  function send(b) {
    var input = b.querySelector('input[type=email]'), btn = b.querySelector('button');
    var email = (input.value || '').trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) { msg(b, 'اكتب بريد إلكتروني صحيح.', false); input.focus(); return; }
    btn.disabled = true; msg(b, 'جاري الاشتراك…', true);
    fetch(URL, { method: 'POST', body: new URLSearchParams({ email: email, source: location.pathname }) })
      .then(function (r) { if (!r.ok) throw 0; input.value = ''; msg(b, 'تم اشتراكك ✓ رح توصلك أخبار وعروض بوينت.', true); })
      .catch(function () { msg(b, 'صار خطأ بسيط، جرّب مرة ثانية.', false); })
      .then(function () { btn.disabled = false; });
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('.footer-news button'); if (!btn) return;
    e.preventDefault(); send(box(btn));
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Enter' || !box(e.target) || e.target.tagName !== 'INPUT') return;
    e.preventDefault(); send(box(e.target));
  });
  document.addEventListener('submit', function (e) { if (box(e.target)) e.preventDefault(); });
})();
