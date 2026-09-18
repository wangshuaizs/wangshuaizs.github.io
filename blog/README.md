# Blog

Static blog for `wangshuaizs.github.io`. No build step, no framework — just plain HTML.

```
blog/
├── index.html                  # blog list page (topics filter + search)
├── posts.js                    # post registry  ← the only file you edit per post
├── tools/
│   └── make_post.py            # wraps a standalone article HTML into a post page
└── posts/
    └── <slug>/
        ├── en.html             # English version (optional)
        └── zh.html             # Chinese version (optional)
```

## Adding a post

1. Put the article HTML somewhere and run the wrapper once per language:

   ```bash
   python3 blog/tools/make_post.py \
       --src ~/Desktop/my-article.html \
       --slug rpki-rov-deployment-2026 \
       --lang en \
       --title "My post title" \
       --summary "One or two sentence summary."
   ```

   It writes `blog/posts/<slug>/<lang>.html`, injects the site top bar, strips editor
   comments, and fixes up `<title>` / `og:` / canonical. Run again with `--lang zh` for the
   Chinese version. (Doing it by hand is fine too: copy the top bar +
   `<style id="wb-post-bar-css">` block from an existing post and fix the EN · 中文 links.)

2. Each post file is self-contained — images embedded as base64 `data:` URIs — so it can be
   opened directly in a browser and needs no asset folder.

3. Add one entry to `blog/posts.js` (the script prints a ready-to-paste snippet):

```js
{
  slug: "rpki-rov-deployment-2026",
  date: "2026-10-01",
  topics: ["RPKI", "ROV"],           // free-form; filter chips build themselves
  en: { title: "…", summary: "…" },
  zh: { title: "…", summary: "…" }   // omit en/zh entirely if that language is absent
}
```

The list sorts by `date` descending. Topic chips and their counts, the search box, and the
shareable `?topic=…` deep links are all generated from the registry — nothing else to update.
If a post has only one language, use that language's title as the card title.

## Page-level wiring

- New posts should also be added to `../sitemap.xml`.
- The `Blog` item is in the navbar of `index.html`, `publications.html`, `service.html`.

## Notes

- Do not rename `posts.js` or `index.html` unless you update the relative paths.
- Keep article images embedded (base64) so a post stays a single portable file.
