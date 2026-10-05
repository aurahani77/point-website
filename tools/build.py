#!/usr/bin/env python3
"""
Point Market static site builder.

  content/posts/*.md   -> one article each (YAML front matter + HTML or Markdown body)
  static/              -> homepage, assets, .htaccess template (copied as-is)

Outputs:
  public/   live site (status: published only)      -> pointmarkets.sa
  preview/  published + drafts, noindex             -> test.pointmarkets.sa

Run:  python3 tools/build.py
"""
import os, re, sys, json, html, shutil, datetime
from urllib.parse import quote, unquote

import yaml
try:
    import markdown as md
except ImportError:
    md = None

sys.path.insert(0, os.path.dirname(__file__))
from theme import SITE, ar_date, icon, page  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONTENT = os.path.join(ROOT, 'content', 'posts')
STATIC = os.path.join(ROOT, 'static')
REQUIRED = ['title', 'slug', 'status', 'date', 'description', 'cover']


# ---------- helpers ----------
def plain(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def trunc(t, n=155):
    if len(t) <= n:
        return t
    return t[:n].rsplit(' ', 1)[0].rstrip('،,.:؛') + '…'


def load_posts():
    posts, errors = [], []
    for fn in sorted(os.listdir(CONTENT)):
        if not fn.endswith(('.md', '.html')) or fn.startswith('_'):
            continue
        raw = open(os.path.join(CONTENT, fn), encoding='utf-8').read()
        m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw, re.S)
        if not m:
            errors.append(f'{fn}: missing front matter'); continue
        fm = yaml.safe_load(m.group(1)) or {}
        body = m.group(2).strip()
        miss = [k for k in REQUIRED if not fm.get(k)]
        if miss:
            errors.append(f'{fn}: missing {", ".join(miss)}'); continue
        fm['status'] = str(fm['status']).strip().lower()
        if fm['status'] not in ('draft', 'published'):
            errors.append(f'{fn}: status must be draft or published'); continue
        fm['slug'] = re.sub(r'[^a-z0-9-]+', '-', str(fm['slug']).lower()).strip('-')
        fm['date'] = str(fm['date'])
        fm['modified'] = str(fm.get('modified') or fm['date'])
        if not body.lstrip().startswith('<'):
            if md is None:
                errors.append(f'{fn}: Markdown body but python-markdown not installed'); continue
            body = md.markdown(body, extensions=['tables', 'sane_lists'])
        fm['body_raw'] = body
        posts.append(fm)
    slugs = [p['slug'] for p in posts]
    for s in set(slugs):
        if slugs.count(s) > 1:
            errors.append(f'duplicate slug: {s}')
    return posts, errors


def process(body):
    toc = []

    def h2id(m):
        i = len(toc) + 1
        toc.append((f's{i}', plain(m.group(2))))
        return f'<h2{m.group(1)} id="s{i}">{m.group(2)}</h2>'
    body = re.sub(r'<h2([^>]*)>(.*?)</h2>', h2id, body, flags=re.S)
    body = re.sub(r'(<table.*?</table>)', r'<div class="table-scroll">\1</div>', body, flags=re.S)
    body = re.sub(r'<img (?![^>]*loading=)', '<img loading="lazy" ', body)
    body = re.sub(r'<a href="(https?://(?!(www\.)?pointmarkets\.sa)[^"]+)"(?![^>]*target=)',
                  r'<a href="\1" target="_blank" rel="noopener"', body)
    return body, toc


def faq_from(body):
    m = re.search(r'<h2[^>]*>[^<]*(?:الأسئلة الشائعة|أسئلة شائعة)[^<]*</h2>(.*?)(?=<h2 |$)', body, re.S)
    if not m:
        return []
    qa = re.findall(r'<h3[^>]*>(.*?)</h3>\s*(.*?)(?=<h3|$)', m.group(1), re.S)
    return [(plain(q), plain(a)) for q, a in qa if plain(a)]


ORG = {'@type': 'Organization', '@id': SITE + '/#org', 'name': 'بوينت ماركت', 'url': SITE + '/',
       'logo': {'@type': 'ImageObject', 'url': SITE + '/assets/img/logo.png'}}

DRAFT_BANNER = ('<div style="position:fixed;bottom:16px;left:16px;z-index:99;background:#f5c400;color:#053947;'
                'font-weight:800;padding:10px 16px;border-radius:12px;box-shadow:0 10px 30px #0003;font-size:14px">'
                'مسودة — غير منشورة على الموقع</div>')


def enrich(p):
    body, toc = process(p['body_raw'])
    text = plain(body)
    words = len(text.split())
    p.update(body=body, toc=toc, words=words, faq=faq_from(body),
             mins=int(p.get('reading_minutes') or max(2, round(words / 200))),
             excerpt=trunc(p.get('excerpt') or p['description'], 140),
             cat=p.get('category') or 'نصائح وأدلة تسوق',
             cover_alt=p.get('cover_alt') or p['title'])
    return p


def card(p, featured=False):
    badge = '<span class="tag" style="background:#fff7d1"><i></i>مسودة</span>' if p['status'] == 'draft' else ''
    return (f'<a class="post-card{" featured" if featured else ""}" href="/blog/{p["slug"]}/">'
            f'<div class="thumb"><img src="{p["cover"]}" alt="{html.escape(p["cover_alt"])}" loading="{"eager" if featured else "lazy"}"></div>'
            f'<div class="body"><span class="tag"><i></i>{html.escape(p["cat"])}</span>{badge}<h2>{html.escape(p["title"])}</h2>'
            f'<p>{html.escape(p["excerpt"])}</p><div class="foot"><span>{ar_date(p["date"])} · {p["mins"]} دقائق قراءة</span>'
            f'<span class="more">اقرأ المقال {icon("arrow", 15)}</span></div></div></a>')


def iso(d):
    return d.replace(' ', 'T') + ('+03:00' if len(d) > 10 else '')


def article(p, all_posts, preview):
    others = [o for o in all_posts if o['slug'] != p['slug']][:3]
    url = f"{SITE}/blog/{p['slug']}/"
    toc_html = ''
    if len(p['toc']) >= 3:
        toc_html = ('<nav class="toc" aria-label="محتويات المقال"><b>في هذا المقال</b><ol>'
                    + ''.join(f'<li><a href="#{i}">{html.escape(t)}</a></li>' for i, t in p['toc']) + '</ol></nav>')
    art = {'@type': 'BlogPosting', '@id': url + '#article', 'mainEntityOfPage': url, 'headline': p['title'],
           'description': p['description'], 'image': [p['cover']], 'datePublished': iso(p['date']),
           'dateModified': iso(p['modified']), 'inLanguage': 'ar', 'author': {'@id': SITE + '/#org'},
           'publisher': {'@id': SITE + '/#org'}, 'articleSection': p['cat'], 'wordCount': p['words']}
    if p.get('focus_keyword'):
        art['keywords'] = p['focus_keyword']
    graph = [art, {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'الرئيسية', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'المدونة', 'item': SITE + '/blog/'},
        {'@type': 'ListItem', 'position': 3, 'name': p['title'], 'item': url}]}, ORG]
    if p['faq']:
        graph.append({'@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in p['faq']]})
    share = quote(p['title'] + ' ' + url)
    body = f'''<section class="page-hero"><div class="container">
<ol class="crumbs"><li><a href="/">الرئيسية</a></li><li><a href="/blog/">المدونة</a></li><li aria-current="page">{html.escape(trunc(p['title'], 48))}</li></ol>
<span class="tag"><i></i>{html.escape(p['cat'])}</span>
<h1 style="margin-top:16px">{html.escape(p['title'])}</h1>
<div class="meta-row"><span>{icon('cal', 17)}<time datetime="{p['date'][:10]}">{ar_date(p['date'])}</time></span><span>{icon('clock', 17)}{p['mins']} دقائق قراءة</span><span>فريق بوينت ماركت</span></div>
</div></section>
<div class="article-wrap"><div class="container">
<figure class="article-cover"><img src="{p['cover']}" alt="{html.escape(p['cover_alt'])}" fetchpriority="high"></figure>
<div class="article-grid">
<article class="prose">
{p['body']}
<div class="share"><span>شارك المقال:</span><a href="https://wa.me/?text={share}" target="_blank" rel="noopener">واتساب</a><a href="https://x.com/intent/post?text={share}" target="_blank" rel="noopener">X</a><a href="https://www.linkedin.com/sharing/share-offsite/?url={quote(url)}" target="_blank" rel="noopener">لينكدإن</a><button type="button" data-copy>نسخ الرابط</button></div>
</article>
<aside class="aside">{toc_html}<div class="cta-card"><b>كل احتياجاتك في مكان واحد</b><p>أكثر من 35 فرعاً في الرياض وجدة، بأفضل جودة وأفضل سعر.</p><a class="button yellow" href="/#branches">اعثر على أقرب فرع {icon('arrow', 17)}</a></div></aside>
</div></div></div>
<section class="related"><div class="container"><div class="head"><div><span class="kicker">من المدونة</span><h2>مقالات قد تهمك</h2></div><a class="all" href="/blog/">كل المقالات {icon('arrow', 16)}</a></div><div class="post-grid">{''.join(card(o) for o in others)}</div></div></section>'''
    head = (f'<meta property="article:published_time" content="{iso(p["date"])}">\n'
            f'<meta property="article:modified_time" content="{iso(p["modified"])}">\n')
    out = page(f"{p['title']} | بوينت ماركت", p['description'], url, body,
               {'@context': 'https://schema.org', '@graph': graph}, p['cover'], 'article', head)
    if p['status'] == 'draft':
        out = out.replace('</body>', DRAFT_BANNER + '\n</body>')
    return out


def blog_index(posts):
    schema = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'Blog', '@id': SITE + '/blog/#blog', 'url': SITE + '/blog/', 'name': 'مدونة بوينت ماركت',
         'inLanguage': 'ar', 'publisher': {'@id': SITE + '/#org'},
         'blogPost': [{'@type': 'BlogPosting', 'headline': p['title'], 'url': f"{SITE}/blog/{p['slug']}/",
                       'datePublished': p['date'][:10], 'image': p['cover']} for p in posts]},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'الرئيسية', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'المدونة', 'item': SITE + '/blog/'}]}, ORG]}
    grid = (card(posts[0], True) + ''.join(card(p) for p in posts[1:])) if posts else '<p>لا توجد مقالات بعد.</p>'
    body = f'''<section class="page-hero"><div class="container">
<ol class="crumbs"><li><a href="/">الرئيسية</a></li><li aria-current="page">المدونة</li></ol>
<span class="kicker">مدونة بوينت</span>
<h1 style="margin-top:14px">أفكار ونصائح<br>لتسوّق <em>أذكى</em></h1>
<p class="lead">قوائم مقاضي جاهزة، أدلة مواسم، ونصائح عملية لبيت سعودي مرتب، مع آخر أخبار بوينت ماركت.</p>
</div></section>
<section class="blog-list"><div class="container"><div class="post-grid">{grid}</div></div></section>'''
    return page('مدونة بوينت ماركت | نصائح تسوق وقوائم مقاضي وأخبار بوينت',
                'مدونة بوينت ماركت: قوائم مقاضي جاهزة، أدلة تسوق للمواسم، ونصائح عملية لتجهيز بيتك بأفضل جودة وأفضل سعر، مع آخر أخبار بوينت.',
                SITE + '/blog/', body, schema, posts[0]['cover'] if posts else SITE + '/assets/img/hero.jpg')


def not_found():
    body = f'''<section class="page-hero" style="min-height:70vh"><div class="container">
<span class="kicker">خطأ 404</span>
<h1 style="margin-top:14px">الصفحة غير <em>موجودة</em></h1>
<p class="lead">يبدو أن الرابط تغيّر أو لم يعد متاحاً. جرّب العودة للرئيسية أو تصفّح أحدث مقالات المدونة.</p>
<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:28px"><a class="button yellow" href="/">الصفحة الرئيسية {icon('arrow')}</a><a class="button" style="background:#fff;border:1px solid var(--line);color:var(--ink)" href="/blog/">المدونة</a></div>
</div></section>'''
    return page('الصفحة غير موجودة | بوينت ماركت', 'الصفحة المطلوبة غير موجودة.', SITE + '/404', body,
                {'@context': 'https://schema.org', '@type': 'WebPage', 'name': '404'},
                SITE + '/assets/img/hero.jpg').replace('index, follow, max-image-preview:large', 'noindex')


def redirects(posts):
    lines = []
    for p in posts:
        old = unquote(str(p.get('old_url') or '')).strip('/')
        if old:
            lines.append(f'RewriteRule ^{re.escape(old).replace(chr(92) + "-", "-")}/?$ /blog/{p["slug"]}/ [R=301,L,NC]')
    for p in posts:
        if p.get('wp_id'):
            lines.append(f'RewriteCond %{{QUERY_STRING}} (^|&)p={int(p["wp_id"])}(&|$)\nRewriteRule ^$ /blog/{p["slug"]}/? [R=301,L]')
    return '\n'.join(lines)


def llms(posts):
    s = f'''# بوينت ماركت (Point Market)

> سلسلة سوبرماركت سعودية بشعار "أفضل جودة بأفضل سعر"، بأكثر من 35 فرعاً في الرياض وجدة. توفر المنتجات الغذائية والمنزلية اليومية، والخضار والفواكه الطازجة، والمنتجات الصحية والعضوية، مع خدمة توصيل عبر تطبيق جاهز.

- الموقع: {SITE}/
- البريد: info@pointmarkets.sa
- واتساب: +966599232857
- انستغرام: https://www.instagram.com/point_marketsa/
- لينكدإن: https://www.linkedin.com/company/point-marketsa/
- تيك توك: https://www.tiktok.com/@marketspoint

## الصفحات الرئيسية

- [الصفحة الرئيسية]({SITE}/): من نحن، الأقسام، الفروع، والتواصل
- [المدونة]({SITE}/blog/): أدلة تسوق وقوائم مقاضي وأخبار بوينت

## المدونة

'''
    return s + ''.join(f"- [{p['title']}]({SITE}/blog/{p['slug']}/): {p['description']}\n" for p in posts)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def build(out, posts, preview):
    if os.path.isdir(out):
        shutil.rmtree(out)
    shutil.copytree(STATIC, out, ignore=shutil.ignore_patterns('htaccess.tpl', '.DS_Store'))
    for p in posts:
        write(f'{out}/blog/{p["slug"]}/index.html', article(p, posts, preview))
    write(f'{out}/blog/index.html', blog_index(posts))
    write(f'{out}/404.html', not_found())
    if preview:
        idx = open(f'{out}/index.html', encoding='utf-8').read()
        write(f'{out}/index.html', idx.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"'))
        write(f'{out}/robots.txt', 'User-agent: *\nDisallow: /\n')
        write(f'{out}/.htaccess', 'Options -Indexes\nDirectoryIndex index.html\nErrorDocument 404 /404.html\n'
              'AddDefaultCharset UTF-8\nAddType font/woff2 .woff2\n<IfModule mod_headers.c>\nHeader set X-Robots-Tag "noindex, nofollow"\n</IfModule>\n')
        return
    pub = [p for p in posts if p['status'] == 'published']
    today = datetime.date.today().isoformat()
    urls = [(SITE + '/', today), (SITE + '/blog/', max([p['modified'][:10] for p in pub] or [today]))] + \
           [(f"{SITE}/blog/{p['slug']}/", p['modified'][:10]) for p in pub]
    write(f'{out}/sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join(f'  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n' for u, d in urls) + '</urlset>\n')
    write(f'{out}/robots.txt', f'User-agent: *\nAllow: /\nDisallow: /wp-admin/\n\nSitemap: {SITE}/sitemap.xml\n')
    write(f'{out}/llms.txt', llms(pub))
    tpl = open(os.path.join(STATIC, 'htaccess.tpl'), encoding='utf-8').read()
    write(f'{out}/.htaccess', tpl.replace('{{REDIRECTS}}', redirects(pub)))


def main():
    posts, errors = load_posts()
    if errors:
        print('Content errors:\n  ' + '\n  '.join(errors))
        sys.exit(1)
    posts = [enrich(p) for p in posts]
    posts.sort(key=lambda p: p['date'], reverse=True)
    published = [p for p in posts if p['status'] == 'published']
    build(os.path.join(ROOT, 'public'), published, preview=False)
    build(os.path.join(ROOT, 'preview'), posts, preview=True)
    print(f'Built {len(published)} published + {len(posts) - len(published)} draft posts')
    for p in posts:
        print(f"  [{p['status']:9}] {p['slug']}  (toc {len(p['toc'])}, faq {len(p['faq'])})")


if __name__ == '__main__':
    main()
