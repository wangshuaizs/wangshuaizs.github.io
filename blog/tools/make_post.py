#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrap a standalone article HTML into a blog post page with the site top bar.

Usage:
  python3 blog/tools/make_post.py \
      --src ~/Desktop/my-article.html \
      --slug rpki-rov-deployment-2026 \
      --lang en \
      --title "My post title" \
      --summary "One or two sentence summary." \
      [--date 2026-10-01]

Writes blog/posts/<slug>/<lang>.html and prints the snippet to paste into blog/posts.js.
Run it once per language. Then add the printed entry to posts.js (merge en/zh into one entry).
"""
import argparse, html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BLOG = os.path.dirname(HERE)          # .../blog
SITE = os.path.dirname(BLOG)          # repo root

BAR_CSS = """<style id="wb-post-bar-css">
  .wb-topbar{margin:-24px -12px 28px;background:#343a40;padding:0 16px;
    font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','PingFang SC','Microsoft YaHei',sans-serif;}
  .wb-topbar *{box-sizing:border-box;}
  .wb-topbar-inner{max-width:960px;margin:0 auto;display:flex;align-items:center;gap:18px;min-height:56px;flex-wrap:wrap;}
  .wb-tb-brand{color:#fff;font-weight:600;font-size:17px;text-decoration:none;letter-spacing:.2px;}
  .wb-tb-brand:hover{color:#fff;text-decoration:none;}
  .wb-tb-nav{display:flex;gap:18px;margin-left:auto;flex-wrap:wrap;}
  .wb-tb-nav a{color:rgba(255,255,255,.68);font-size:15px;text-decoration:none;}
  .wb-tb-nav a:hover{color:#fff;text-decoration:none;}
  .wb-tb-nav a.active{color:#fff;font-weight:600;}
  .wb-tb-lang{display:flex;gap:6px;align-items:center;padding-left:16px;border-left:1px solid rgba(255,255,255,.22);
    font-size:14px;}
  .wb-tb-lang a{color:rgba(255,255,255,.68);text-decoration:none;}
  .wb-tb-lang a:hover{color:#fff;}
  .wb-tb-lang a.active{color:#fff;font-weight:600;}
  .wb-tb-lang span{color:rgba(255,255,255,.32);}
  @media(max-width:640px){
    .wb-topbar{padding:6px 14px;}
    .wb-topbar-inner{gap:10px;padding:6px 0;}
    .wb-tb-nav{gap:14px;font-size:14px;}
    .wb-tb-lang{padding-left:10px;}
  }
</style>"""


def build_bar(lang):
    en_cls = ' class="active"' if lang == "en" else ""
    zh_cls = ' class="active"' if lang == "zh" else ""
    return (
        '<div class="wb-topbar"><div class="wb-topbar-inner">'
        '<a class="wb-tb-brand" href="../../index.html">Shuai Wang</a>'
        '<nav class="wb-tb-nav">'
        '<a href="../../index.html">Home</a>'
        '<a href="../../publications.html">Publications</a>'
        '<a href="../../service.html">Service</a>'
        '<a class="active" href="../index.html">Blog</a>'
        '</nav>'
        f'<div class="wb-tb-lang"><a href="en.html"{en_cls}>EN</a><span>/</span>'
        f'<a href="zh.html"{zh_cls}>中文</a></div>'
        '</div></div>'
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="path to the standalone article HTML")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--lang", required=True, choices=["en", "zh"])
    ap.add_argument("--title", required=True)
    ap.add_argument("--summary", default="")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD, default: today")
    a = ap.parse_args()

    import datetime
    date = a.date or datetime.date.today().isoformat()

    s = open(os.path.expanduser(a.src), encoding="utf-8").read()

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
        f'<link rel="canonical" href="{url}">'
    ) + s[m.end():]

    # 3. top bar
    s = s.replace("</head>", BAR_CSS + "</head>", 1)
    m = re.search(r"<body[^>]*>", s)
    if not m:
        sys.exit("could not find <body>: unexpected source layout")
    s = s[: m.end()] + build_bar(a.lang) + s[m.end():]
    s = re.sub(r"\n{3,}", "\n\n", s)

    outdir = os.path.join(SITE, "blog", "posts", a.slug)
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, a.lang + ".html")
    open(out, "w", encoding="utf-8").write(s)
    print(f"wrote {out} ({len(s)} bytes)")

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
