# موقع بوينت ماركت — pointmarkets.sa

موقع ثابت (HTML) مع مدونة تُبنى تلقائياً من ملفات المحتوى.

## كيف يعمل

```
content/posts/*.md  ──►  GitHub Action (tools/build.py)  ──►  public/  (المنشور فقط)
static/ (الرئيسية + الأصول)                                └─►  preview/ (المنشور + المسودات، noindex)
                                                                     │
                       cPanel Cron كل 5 دقائق (deploy/deploy.sh) ◄───┘
                       preview/ → test.pointmarkets.sa
                       public/  → pointmarkets.sa (بعد الإطلاق)
```

## إضافة مقال

1. انسخ `content/posts/_template.md` إلى ملف جديد باسم الـ slug، مثل `content/posts/winter-groceries.md`.
2. اترك `status: draft` لتظهر المسودة على `test.pointmarkets.sa` فقط (مع شارة "مسودة").
3. للنشر غيّر السطر إلى `status: published` واحفظ.
4. خلال دقائق: يُبنى الموقع، وتتحدث المدونة و`sitemap.xml` و`llms.txt`، وينزل على السيرفر.

المحتوى يمكن أن يكون Markdown أو HTML. قسم "الأسئلة الشائعة" (H2) مع أسئلة H3 يتحول تلقائياً إلى FAQ Schema.

## المجلدات

| المجلد | المحتوى |
|---|---|
| `content/posts/` | المقالات (front matter + المحتوى) — **هذا ما يُعدَّل** |
| `static/` | الصفحة الرئيسية، CSS، JS، الخط، الصور، قالب `.htaccess` |
| `tools/` | سكربت البناء والقالب |
| `public/`, `preview/` | **مُولَّدة تلقائياً — لا تعدّلها يدوياً** |
| `deploy/deploy.sh` | سكربت السحب على السيرفر (Cron) |

## ملاحظات

- صور المقالات القديمة على `https://pointmarkets.sa/wp-content/uploads/` — لا تحذفوا مجلد `wp-content`.
- لا تعدّلوا ملفات الموقع من File Manager مباشرة؛ أي تعديل يمر عبر هذا المستودع حتى لا يُستبدل.
- البناء محلياً: `pip install pyyaml markdown && python3 tools/build.py`
