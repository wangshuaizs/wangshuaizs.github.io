#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrap a standalone article HTML into a blog post page with the site navbar.

Usage:
  python3 blog/tools/make_post.py \
      --src ~/Desktop/my-article.html \
      --slug rpki-rov-deployment-2026 \
      --lang en \
      --title "My post title" \
      --summary "One or two sentence summary." \
      [--date 2026-10-01]

Writes blog/posts/<slug>/<lang>.html, then resyncs the in-page language switch across
every page of that post. Run it once per language; a post with a single language simply
has no switch.
"""
import argparse, html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BLOG = os.path.dirname(HERE)          # .../blog
SITE = os.path.dirname(BLOG)          # repo root

sys.path.insert(0, HERE)
from add_analytics import MARK as ANALYTICS_MARK, load_code, snippet as analytics_snippet  # noqa: E402

LANGS = ["en", "zh"]
LANG_LABEL = {"en": "English", "zh": "中文"}

BOOTSTRAP_CSS = "https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"
JQUERY = "https://code.jquery.com/jquery-3.5.1.slim.min.js"
BOOTSTRAP_JS = "https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.bundle.min.js"

# A post lives at blog/posts/<slug>/<lang>.html, so the site root is three levels up
# and the blog index is two levels up.
UP_ROOT = "../../../"
UP_BLOG = "../../"

POST_CSS = """<style id="wb-post-css">
  /* reserve the scrollbar gutter so the fixed-top navbar (and the article's own
     centred column) sits at exactly the same x on every page of the site,
     whether or not that page happens to be tall enough to scroll */
  html{scrollbar-gutter:stable;}
  /* the site navbar is fixed-top, so reserve room for it (56px) on top of the
     article's own 24px top padding */
  body.wb-post{padding-top:80px !important;}
  /* per-post language switch — only present when the post has >1 language */
  .wb-langbar{display:flex;align-items:center;justify-content:flex-end;gap:8px;margin:-2px 0 14px;
    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','PingFang SC','Microsoft YaHei',sans-serif;}
  .wb-langbar a{font-size:12.5px;line-height:1.6;padding:2px 11px;border-radius:999px;border:1px solid #dcdfe3;
    color:#6b737b;text-decoration:none;transition:all .12s ease;}
  .wb-langbar a:hover{border-color:#9aa3ac;color:#1f2328;text-decoration:none;}
  .wb-langbar a.active{background:#2f3337;border-color:#2f3337;color:#fff;}
</style>"""


def build_nav():
    """Byte-for-byte the same navbar the hand-written pages use, with paths adjusted."""
    return (
        '<nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">'
        f'<a class="navbar-brand" href="{UP_ROOT}index.html">Shuai Wang</a>'
        '<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav"'
        ' aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">'
        '<span class="navbar-toggler-icon"></span>'
        '</button>'
        '<div class="collapse navbar-collapse" id="navbarNav">'
        '<ul class="navbar-nav ml-auto">'
        f'<li class="nav-item"><a class="nav-link" href="{UP_ROOT}index.html">Home</a></li>'
        f'<li class="nav-item"><a class="nav-link" href="{UP_ROOT}publications.html">Publications</a></li>'
        f'<li class="nav-item"><a class="nav-link" href="{UP_ROOT}service.html">Service</a></li>'
        f'<li class="nav-item active"><a class="nav-link" href="{UP_BLOG}index.html">Blog</a></li>'
        '</ul></div></nav>'
    )


BARMARK = re.compile(r"<!--WB-LANGBAR-->.*?<!--/WB-LANGBAR-->\s*", re.S)


def build_langbar(langs, current):
    pills = "".join(
        f'<a href="{l}.html"{" class=\"active\"" if l == current else ""}>{LANG_LABEL[l]}</a>'
        for l in langs
    )
    return f'<!--WB-LANGBAR--><div class="wb-langbar">{pills}</div><!--/WB-LANGBAR-->\n'


def sync_langbars(slug):
    """Rebuild the in-page language switch for every page of a post.

    Runs after each write, so a post that only has en.html shows no switch at all,
    and the switch appears (in both pages) as soon as the second language lands."""
    d = os.path.join(SITE, "blog", "posts", slug)
    have = [l for l in LANGS if os.path.exists(os.path.join(d, l + ".html"))]
    for lang in have:
        p = os.path.join(d, lang + ".html")
        s = open(p, encoding="utf-8").read()
        s = BARMARK.sub("", s)
        if len(have) > 1:
            m = re.search(r"<h1\b", s)
            if not m:
                print(f"  ! {lang}.html: no <h1>, language switch not inserted")
                continue
            s = s[: m.start()] + build_langbar(have, lang) + s[m.start():]
        open(p, "w", encoding="utf-8").write(s)
    return have


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="path to the standalone article HTML")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--lang", required=True, choices=LANGS)
    ap.add_argument("--title", required=True)
    ap.add_argument("--summary", default="")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD, default: today")
    a = ap.parse_args()

    import datetime
    date = a.date or datetime.date.today().isoformat()

    s = open(os.path.expanduser(a.src), encoding="utf-8").read()

    # 0. make re-runs idempotent
    s = BARMARK.sub("", s)

    # 1. editor comments out
    s = re.sub(r"<!--(?!\[if).*?-->", "", s, flags=re.S)

    # 2. one clean <title> + social meta, right after the charset declaration
    s = re.sub(r"<title\b[^>]*>.*?</title>", "", s, flags=re.S)
    m = re.search(r'<meta charset="utf-8"[^>]*>', s)
    if not m:
        sys.exit("could not find <meta charset>: unexpected source layout")
    esc_t = html.escape(a.title, quote=True)
    esc_d = html.escape(a.summary, quote=True)
    url = f"https://wangshuaizs.github.io/blog/posts/{a.slug}/{a.lang}.html"
    s = s[: m.end()] + (
        f"<title>{esc_t}</title>"
        f'<meta name="description" content="{esc_d}">'
        f'<meta property="og:type" content="article">'
        f'<meta property="og:title" content="{esc_t}">'
        f'<meta property="og:description" content="{esc_d}">'
        f'<meta property="og:locale" content="{"en_US" if a.lang == "en" else "zh_CN"}">'
        f'<link rel="canonical" href="{url}">'
        f'<link href="{BOOTSTRAP_CSS}" rel="stylesheet">'
    ) + s[m.end():]

    # 3. site navbar + styles; the article body itself is left untouched
    s = s.replace("</head>", POST_CSS + "</head>", 1)
    m = re.search(r"<body[^>]*>", s)
    if not m:
        sys.exit("could not find <body>: unexpected source layout")
    body_tag = m.group(0)
    if "class=" in body_tag:
        body_tag = re.sub(r'class="([^"]*)"', r'class="\1 wb-post"', body_tag, count=1)
    else:
        body_tag = body_tag[:-1] + ' class="wb-post">'
    s = s[: m.start()] + body_tag + build_nav() + s[m.end():]

    # 4. jQuery + Bootstrap so the collapsed mobile menu behaves like the other pages,
    #    then the page-view snippet (a no-op until blog/analytics.json has a code)
    s = ANALYTICS_MARK.sub("", s)
    tail = f'<script src="{JQUERY}"></script>\n<script src="{BOOTSTRAP_JS}"></script>\n'
    gc = load_code()
    if gc:
        tail += analytics_snippet(gc)
    s = s.replace("</body>", tail + "</body>", 1)
    s = re.sub(r"\n{3,}", "\n\n", s)

    outdir = os.path.join(SITE, "blog", "posts", a.slug)
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, a.lang + ".html")
    open(out, "w", encoding="utf-8").write(s)
    print(f"wrote {out} ({len(s)} bytes)")

    have = sync_langbars(a.slug)
    print(f"languages present: {', '.join(have)}"
          + ("" if len(have) > 1 else "  (no in-page switch — single language)"))

    print("\nNow add this to blog/posts.js (merge with the other language's entry if any):\n")
    print("  {")
    print(f'    slug: "{a.slug}",')
    print(f'    date: "{date}",')
    print(f'    topics: ["RPKI", "BGP Security"],')
    print(f'    {a.lang}: {{')
    print(f'      title: {a.title!r},')
    print(f'      summary: {a.summary!r}')
    print("    }")
    print("  }")
    print("\nAlso add the post URL to sitemap.xml.")


if __name__ == "__main__":
    main()
