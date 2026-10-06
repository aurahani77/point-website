# ==========================================================
#  pointmarkets.sa — الموقع الجديد (ثابت)
#  يحل محل ملف .htaccess الخاص بووردبريس
# ==========================================================

Options -Indexes
DirectoryIndex index.html
ErrorDocument 404 /404.html
AddDefaultCharset UTF-8
AddType font/woff2 .woff2
AddType text/plain .txt

<IfModule mod_rewrite.c>
RewriteEngine On

# 1) بدون www + HTTPS (للدومين الأساسي فقط، آمن مع Cloudflare)
RewriteCond %{HTTP_HOST} ^www\.pointmarkets\.sa$ [NC]
RewriteRule ^(.*)$ https://pointmarkets.sa/$1 [R=301,L]
RewriteCond %{HTTP_HOST} ^pointmarkets\.sa$ [NC]
RewriteCond %{HTTPS} off
RewriteCond %{HTTP:X-Forwarded-Proto} !https
RewriteCond %{HTTP:CF-Visitor} !https
RewriteRule ^(.*)$ https://pointmarkets.sa/$1 [R=301,L]

# 1b) ووردبريس يبقى شغالاً خلف الكواليس فقط: لوحة التحكم (wp-admin) + REST API لمزامنة المقالات
RewriteRule ^wp-json/?(.*)$ /index.php?rest_route=/$1 [L,QSA]
RewriteCond %{QUERY_STRING} !rest_route=
RewriteRule ^index\.php$ / [R=301,L]

# 2-3) مقالات ووردبريس القديمة -> روابط المدونة الجديدة (تتولد تلقائياً من content/posts)
{{REDIRECTS}}

# 4) صفحات وأقسام ووردبريس القديمة
RewriteRule ^المدونة/?$ /blog/ [R=301,L,NC]
RewriteRule ^category/(المدونة|m|اخبار)(/.*)?$ /blog/ [R=301,L,NC]
RewriteRule ^(feed|comments/feed)/?$ /blog/ [R=301,L,NC]
RewriteRule ^author/.*$ /blog/ [R=301,L,NC]
RewriteRule ^الفروع[ـ]?/?$ /branches/ [R=301,L,NC]
RewriteRule ^(portfolio/.*|باك|باك-ازرق|الصفحة-الرئيسية-بوينت)/?$ / [R=301,L,NC]
RewriteRule ^(wp-sitemap|sitemap_index|post-sitemap|page-sitemap|category-sitemap)\.xml$ /sitemap.xml [R=301,L,NC]
</IfModule>

# 5) ضغط وتخزين مؤقت
<Files xmlrpc.php>
Require all denied
</Files>

<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript text/javascript image/svg+xml application/xml text/plain
</IfModule>
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType text/html "access plus 0 seconds"
ExpiresByType text/css "access plus 7 days"
ExpiresByType application/javascript "access plus 7 days"
ExpiresByType text/javascript "access plus 7 days"
ExpiresByType font/woff2 "access plus 1 year"
ExpiresByType image/jpeg "access plus 30 days"
ExpiresByType image/png "access plus 30 days"
ExpiresByType image/webp "access plus 30 days"
ExpiresByType image/svg+xml "access plus 30 days"
</IfModule>
