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

   It writes `blog/posts/<slug>/<lang>.html`, injects the site navbar, strips editor
   comments, and fixes up `<title>` / `og:` / canonical. Run again with `--lang zh` for the
   Chinese version. (Doing it by hand is fine too: copy the `<nav>` + the
   `<style id="wb-post-css">` block from an existing post. Remember a post sits three
   levels below the site root, so site links need `../../../` and the blog index needs
   `../../index.html`.)

   The navbar is the *same Bootstrap markup* the hand-written pages use, so brand position,
   font size and the mobile hamburger match `index.html` exactly; `body.wb-post` just adds
   80px of top padding so the `fixed-top` bar doesn't cover the article title. Bootstrap's CSS
   does not touch the article body — every block in these articles carries its own inline
   styles (verified: 78/78 elements render at identical geometry with and without Bootstrap).

2. Each post file is self-contained — images embedded as base64 `data:` URIs — so it can be
   opened directly in a browser and needs no asset folder.

3. **Language switch is per post.** The site top bar never shows a language toggle; instead
   each page gets a small `English / 中文` switch of its own, right above the title. Every run
   of `make_post.py` resyncs that switch across all pages of the post, so:
   - a post with only `en.html` (or only `zh.html`) shows **no switch at all**;
   - as soon as the second language is generated, the switch appears in both pages
     automatically — no manual editing, no ordering requirement.

4. Add one entry to `blog/posts.js` (the script prints a ready-to-paste snippet). Include only
   the languages that exist:

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
   shareable `?topic=…` deep links are all generated from the registry — nothing else to
   update. If a post has only one language, that language's title becomes the card title.

## Page-level wiring

- New posts should also be added to `../sitemap.xml`.
- The `Blog` item is in the navbar of `index.html`, `publications.html`, `service.html`.

## Notes

- Do not rename `posts.js` or `index.html` unless you update the relative paths.
- Keep article images embedded (base64) so a post stays a single portable file.
