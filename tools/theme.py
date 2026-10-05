import json, html
from urllib.parse import quote

SITE = 'https://pointmarkets.sa'

MONTHS = ['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر']

def ar_date(d):
    y, m, dd = d[:10].split('-')
    return f'{int(dd)} {MONTHS[int(m)-1]} {y}'

ICON = {
 'arrow': '<path d="M5 12h14"></path><path d="m13 6 6 6-6 6"></path>',
 'cal': '<rect x="3" y="5" width="18" height="16" rx="2"></rect><path d="M16 3v4M8 3v4M3 10h18"></path>',
 'clock': '<circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path>',
 'menu': '<path d="M4 7h16M4 12h16M4 17h16"></path>',
 'wa': '<path d="M3 21l1.7-5A8.5 8.5 0 1 1 8 19.3L3 21Z"></path><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 .8a4 4 0 0 1-1.8-1.8l.8-1-1-2L9 9.5Z"></path>',
}
def icon(n, s=18):
    return f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[n]}</svg>'

WA = 'https://wa.me/966599232857'
PHONE = '⁦+966 59 923 2857⁩'

HEADER = f'''<header><div class="container nav"><a class="logo" href="/" aria-label="بوينت - الصفحة الرئيسية"><img src="/assets/img/logo.png" alt="شعار بوينت" width="52" height="52"><span class="logo-slogan">أفضل جودة بأفضل سعر</span></a><nav id="mainnav"><a href="/#about">عن بوينت</a><a href="/#why">لماذا بوينت؟</a><a href="/#categories">الأقسام</a><a href="/#branches">الفروع</a><a href="/blog/" class="active" aria-current="page">المدونة</a><a href="/#contact">تواصل معنا</a></nav><a class="nav-cta" href="/#branches">ابحث عن أقرب فرع {icon('arrow',17)}</a><button class="menu-button" aria-label="القائمة" aria-controls="mainnav" aria-expanded="false">{icon('menu',24)}</button></div></header>'''

FOOTER = f'''<footer><div class="container footer-top"><div><a class="logo logo-light" href="/" aria-label="بوينت - الصفحة الرئيسية"><img src="/assets/img/logo-light.svg" alt="شعار بوينت" width="58" height="58"><span class="logo-slogan">أفضل جودة بأفضل سعر</span></a><p>أفضل خدمة، أفضل جودة، أفضل سعر.</p></div><div><b>روابط سريعة</b><a href="/#about">عن بوينت</a><a href="/#categories">الأقسام</a><a href="/#branches">الفروع</a><a href="/blog/">المدونة</a></div><div><b>تواصل معنا</b><a href="{WA}" target="_blank" rel="noopener">{PHONE}</a><a href="mailto:info@pointmarkets.sa">info@pointmarkets.sa</a><span>المملكة العربية السعودية</span></div><div class="footer-news"><b>ابق على اطلاع</b><p>أخبار بوينت، مباشرة إلى بريدك.</p><form class="news-form"><label><input placeholder="بريدك الإلكتروني" type="email" required><button aria-label="اشترك">{icon('arrow')}</button></label></form></div></div><div class="container footer-bottom"><span>© 2026 بوينت. جميع الحقوق محفوظة.</span><div><a href="#">سياسة الخصوصية</a><a href="#">الشروط والأحكام</a></div><span class="socials"><a href="https://www.instagram.com/point_marketsa/" target="_blank" rel="noopener" aria-label="انستغرام">ig</a><a href="https://www.linkedin.com/company/point-marketsa/" target="_blank" rel="noopener" aria-label="لينكدإن">in</a><a href="https://www.tiktok.com/@marketspoint" target="_blank" rel="noopener" aria-label="تيك توك">tk</a></span></div></footer>'''

SCRIPT = '''<script>
(function(){var b=document.querySelector('.menu-button'),n=document.getElementById('mainnav');if(b&&n)b.addEventListener('click',function(){var o=n.classList.toggle('nav-open');b.setAttribute('aria-expanded',o)});
document.querySelectorAll('.news-form').forEach(function(f){f.addEventListener('submit',function(e){e.preventDefault();var v=f.querySelector('input').value;location.href='mailto:info@pointmarkets.sa?subject='+encodeURIComponent('اشتراك في نشرة بوينت')+'&body='+encodeURIComponent('أرغب بالاشتراك في نشرة بوينت: '+v)})});
var c=document.querySelector('[data-copy]');if(c)c.addEventListener('click',function(){navigator.clipboard&&navigator.clipboard.writeText(location.href);c.textContent='تم نسخ الرابط'});
var links=[].slice.call(document.querySelectorAll('.toc a'));if(links.length&&'IntersectionObserver'in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){links.forEach(function(l){l.classList.toggle('on',l.getAttribute('href')==='#'+e.target.id)})}})},{rootMargin:'-20% 0px -70% 0px'});links.forEach(function(l){var t=document.getElementById(l.getAttribute('href').slice(1));t&&io.observe(t)})}
})();
</script>'''

def page(title, desc, canonical, body, schema, og_image, og_type='website', extra_head=''):
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#11A9C3">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="ar_SA">
<meta property="og:site_name" content="بوينت ماركت">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
{extra_head}<link rel="icon" href="/assets/img/logo.png">
<link rel="preload" href="/assets/fonts/Norsal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/blog.css">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head>
<body class="blog">
{HEADER}
<main>
{body}
</main>
{FOOTER}
{SCRIPT}
</body>
</html>
'''

