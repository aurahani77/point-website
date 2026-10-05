# Point Market website — handoff (updated 2026-10-05)

Read this first in any new session. Owner: Hala (Arabic replies, concise).

## What this is
- Static site replacing the WordPress site at pointmarkets.sa. No CMS, no database.
- Repo: github.com/aurahani77/point-website (public). Push needs a GitHub token from Hala, used only as an `http.extraHeader` at push time. Never write it into a file.
- Preview: https://test.pointmarkets.sa. Live root domain is NOT switched yet.

## How it works
- `static/index.html` + `static/assets/app.js`: homepage. It's a minified React/Vite bundle, so edit its strings directly (`f.jsx` / `f.jsxs`). Branch data lives in this bundle (`gt=[["الرياض","حي","map url"],...]`) and is the single source of truth.
- `static/assets/site.css`: homepage styles. The Norsal font is at `/assets/fonts/Norsal.woff2`. The edit blocks are at the end of the file. Global rule: `letter-spacing:0` (Arabic letters must stay joined).
- `static/assets/blog.css`: styles for every generated page: blog, legal, branches.
- `tools/build.py`: builds `public/` (published only) and `preview/` (with drafts, noindex). It generates:
  - blog index
  - category pages `/blog/category/tips|news/`
  - articles
  - `/privacy-policy/`, `/terms/` (text in `tools/legal.py`)
  - `/branches/`
  - sitemap, `llms.txt`, `posts.json`, `.htaccess` (301s from old WordPress URLs)
  - cache-busting `?v=hash` on CSS/JS
  - Jahez banner link (`https://jahez.go.link/1YlM4`)
- `tools/theme.py`: shared header/footer/icons for the generated pages.
- `content/posts/*.md`: YAML front matter (`status: draft|published`, `category: نصائح وأدلة تسوق | أخبار بوينت`) plus an HTML body.
- `.github/workflows/build.yml` builds on push. A cPanel cron job every 5 minutes runs `deploy/deploy.sh`, which copies `preview/` to the test subdomain. Check the deployed commit at `/version.txt`.
- n8n:
  - "Article Writer" (wCaiER8YRHVtIozw) commits drafts to GitHub.
  - "Publish Link" (zDP2goeXwQFVnxti) flips a draft to published.
  - Credential: "GitHub point-website".
- Images stay on `https://pointmarkets.sa/wp-content/uploads/`. Never delete wp-content.

## Done
- Homepage design edits:
  - header CTA «ابحث عن أقرب فرع», marquee, footer (blue + yellow, SVG social icons)
  - categories title on one line
  - 37 branches (33 Riyadh, 4 Jeddah; النزهة 1 + النزهة 2)
- Blog with categories, 7 published posts + 7 drafts.
- Privacy + terms pages, linked in the footers.
- `/branches/` v1: city tabs, search, map buttons, GroceryStore + FAQ schema.

## In progress / next
1. **Homepage scroll motion** (Hala chose "حركة مع السكرول"):
   - `static/assets/motion.js` is written but NOT wired yet.
   - To wire it: add `<script defer src="/assets/motion.js">` to `static/index.html`, add motion.js to `bust_cache`, and write the CSS:
     - `html.motion .w` word reveal (padding so Arabic marks aren't clipped)
     - `.scroll-progress` bar (yellow, fixed top, origin right)
     - `header.scrolled`
     - curtain reveal on `.quality-image`
   - Respect prefers-reduced-motion. Test with Playwright screenshots (desktop + 390px mobile).
2. **Redesign `/branches/` from scratch**: Hala doesn't like v1. She wants a region filter like trolley.com.sa/locations.
   - Filter: city → Riyadh region (شمال/شرق/غرب/وسط/جنوب) + search.
   - The sandbox can't resolve the map short links, so regions are assigned by district knowledge. Proposed:
     - شمال: الرحمانية, المحمدية, الربيع, النفل, النزهة 1, النزهة 2, النرجس, العارض, يو ووك, الورود, الملك سلمان, أبو بكر, الياسمين, أنس بن مالك, الندى, الملقا
     - شرق: خريص, الملك عبدالله, الروضة, النهضة, غرناطة, النسيم, الرمال 1, الرمال 2, المونسية, السلي, الجنادرية
     - غرب: لبن, نجم الدين, المزاحمية
     - وسط: التحلية
     - جنوب: الرفيعة
   - **Ask Hala to confirm** «التواصل» (unknown; maybe التعاون in Jeddah?) and «التحلية» (Riyadh or Jeddah?).
3. Open items for Hala:
   - company legal name + CR number for the legal pages
   - the footer newsletter field doesn't submit anywhere (connect it or remove it)
   - legal review of the privacy/terms text
   - the snacks draft says «ميني ماركت» (n8n banned-word table wlJuGhBQLqeBcIJc)
4. Later: launch on the root domain.
   - Back up first.
   - Move the WordPress core to `_old-wordpress`, keeping wp-content.
   - Set `LIVE_DIR=$HOME/public_html` in the cron job.
   - Submit the sitemap in Search Console.

## Working rules
- Batch Hala's edits when she says so. Screenshot-verify before every push. Changes show on test within 5–10 minutes. If she sees no change, tell her Ctrl+Shift+R.
- Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
