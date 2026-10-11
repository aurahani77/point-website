#!/usr/bin/env python3
"""Mirror blog posts into WordPress admin (replaces the n8n "Sync Posts to WordPress" workflow).

Published posts -> WP status "private" (visible in wp-admin only, so Google never sees duplicate content).
Drafts and scheduled posts -> WP status "draft".
Posts that already carry `wp_id` (migrated from the old WordPress site) are skipped.

Needs env vars WP_USER and WP_APP_PASSWORD (GitHub repo secrets). Uses only the standard library + pyyaml.
"""
import base64
import datetime
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from build import load_posts  # noqa: E402

WP = 'https://pointmarkets.sa/wp-json/wp/v2/posts'
SITE = 'https://pointmarkets.sa'
PREVIEW = 'https://test.pointmarkets.sa'
STATUSES = 'publish,future,draft,pending,private'

user, pw = os.environ.get('WP_USER', ''), os.environ.get('WP_APP_PASSWORD', '')
if not user or not pw:
    print('WP_USER / WP_APP_PASSWORD not set - skipping WordPress sync')
    sys.exit(0)
AUTH = 'Basic ' + base64.b64encode(f'{user}:{pw.replace(" ", "")}'.encode()).decode()


def api(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        'Authorization': AUTH, 'Content-Type': 'application/json', 'User-Agent': 'point-wp-sync'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode() or 'null')
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'{method} {url} -> {e.code}: {e.read().decode()[:300]}')


def norm(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', str(s or '')))).strip()


def find(p):
    q = {'status': STATUSES, 'context': 'edit', '_fields': 'id,status,slug,title'}
    hits = api('GET', WP + '?' + urllib.parse.urlencode(dict(q, slug=p['slug'])))
    if hits:
        return hits[0]
    hits = api('GET', WP + '?' + urllib.parse.urlencode(dict(q, search=p['title'], per_page=20)))
    return next((h for h in hits if norm(h['title'].get('raw') or h['title'].get('rendered')) == norm(p['title'])), None)


def main():
    # fail fast with a clear message if the credentials are wrong
    me = api('GET', 'https://pointmarkets.sa/wp-json/wp/v2/users/me?context=edit&_fields=id,name,capabilities')
    if not (me.get('capabilities') or {}).get('edit_posts'):
        sys.exit(f'WordPress user "{me.get("name")}" cannot edit posts')
    print(f'Authenticated as {me.get("name")}')

    posts, errors = load_posts()
    now = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
    created = updated = skipped = failed = 0
    for p in posts:
        if p.get('wp_id'):
            continue
        live = p['status'] == 'published' and p['date'] <= now
        status = 'private' if live else 'draft'
        link = f"{SITE if live else PREVIEW}/blog/{p['slug']}/"
        cover = p['cover'] if str(p['cover']).startswith('http') else SITE + '/' + str(p['cover']).lstrip('/')
        note = ('<p style="background:#E6F6F8;padding:12px 16px;border-radius:10px"><strong>'
                + ('منشورة على الموقع' if live else 'مسودة') + '</strong> — هذه نسخة للعرض داخل ووردبريس. '
                + f'<a href="{link}" target="_blank">' + ('افتح المقالة على الموقع' if live else 'معاينة المسودة') + '</a></p>')
        img = f'<p><img src="{cover}" alt="{html.escape(str(p.get("cover_alt") or p["title"]))}"></p>'
        body = {'title': p['title'], 'slug': p['slug'], 'status': status, 'date': p['date'].replace(' ', 'T'),
                'excerpt': p.get('description', ''), 'content': note + img + p['body_raw']}
        try:
            hit = find(p)
            if not hit:
                api('POST', WP, body); created += 1; print(f'  + created  [{status}] {p["slug"]}')
            elif hit['status'] != status:
                api('POST', f'{WP}/{hit["id"]}', body); updated += 1; print(f'  ~ updated  [{status}] {p["slug"]}')
            else:
                skipped += 1
        except Exception as e:  # keep going; report at the end
            failed += 1; print(f'  ! failed   {p["slug"]}: {e}')
    print(f'WordPress sync: {created} created, {updated} updated, {skipped} unchanged, {failed} failed')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
