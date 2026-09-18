#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Put the GoatCounter page-view snippet on every page of the site.

The site code is kept in `blog/analytics.json`:

    { "goatcounter": "yourcode" }     -> https://yourcode.goatcounter.com/count

Usage:
    python3 blog/tools/add_analytics.py                    # apply to all pages
    python3 blog/tools/add_analytics.py --code yourcode    # set the code, then apply
    python3 blog/tools/add_analytics.py --remove           # strip it from all pages
    python3 blog/tools/add_analytics.py --status           # show what is there now

Covers the three hand-written pages, the blog index, and every
`blog/posts/<slug>/<lang>.html`. The snippet is wrapped in markers, so re-running
replaces it instead of stacking copies.

Nothing is drawn on the page: no badge, no counter, no map. The numbers live behind
the GoatCounter login, so only the site owner sees them. No cookies, no personal
data, so no consent banner is needed either.
"""
import argparse
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BLOG = os.path.dirname(HERE)
SITE = os.path.dirname(BLOG)
CONFIG = os.path.join(BLOG, "analytics.json")

START, END = "<!--WB-ANALYTICS-->", "<!--/WB-ANALYTICS-->"
MARK = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\s*", re.S)


def load_code():
    if not os.path.exists(CONFIG):
        return ""
    with open(CONFIG, encoding="utf-8") as fh:
        return (json.load(fh).get("goatcounter") or "").strip()


def save_code(code):
    data = {}
    if os.path.exists(CONFIG):
        with open(CONFIG, encoding="utf-8") as fh:
            data = json.load(fh)
    data["goatcounter"] = code
    with open(CONFIG, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def snippet(code):
    """The official GoatCounter snippet. No visible counter, no cookies."""
    return (f'{START}<script data-goatcounter="https://{code}.goatcounter.com/count"'
            f' async src="//gc.zgo.at/count.js"></script>{END}\n')


def pages():
    out = [os.path.join(SITE, p) for p in
           ("index.html", "publications.html", "service.html", "blog/index.html")]
    posts = os.path.join(BLOG, "posts")
    if os.path.isdir(posts):
        for slug in sorted(os.listdir(posts)):
            d = os.path.join(posts, slug)
            if os.path.isdir(d):
                out += [os.path.join(d, f) for f in sorted(os.listdir(d))
                        if f.endswith(".html")]
    return [p for p in out if os.path.exists(p)]


def apply_to(path, code):
    """Returns 'added' / 'updated' / 'unchanged' / 'removed'."""
    s = open(path, encoding="utf-8").read()
    had = START in s
    s = MARK.sub("", s)
    if code:
        if "</body>" not in s:
            raise SystemExit(f"{path}: no </body>, refusing to touch it")
        s = s.replace("</body>", snippet(code) + "</body>", 1)
    open(path, "w", encoding="utf-8").write(s)
    if not code:
        return "removed" if had else "unchanged"
    return "updated" if had else "added"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", help="your GoatCounter site code (the <code> in <code>.goatcounter.com)")
    ap.add_argument("--remove", action="store_true", help="strip the snippet from every page")
    ap.add_argument("--status", action="store_true", help="just report the current state")
    a = ap.parse_args()

    targets = pages()

    if a.status:
        for p in targets:
            s = open(p, encoding="utf-8").read()
            m = re.search(re.escape(START) + r".*?" + re.escape(END), s, re.S)
            tag = m.group(0)[len(START):-len(END)] if m else "-- none --"
            print(f"  {os.path.relpath(p, SITE):56s} {tag}")
        print(f"\nconfig: {load_code()!r}  ({len(targets)} pages)")
        return

    if a.remove:
        code = ""
        save_code(code)
        print("analytics.json: goatcounter = ''")
    elif a.code is not None:
        code = a.code.strip()
        save_code(code)
        print(f"analytics.json: goatcounter = {code!r}")
    else:
        code = load_code()
        if not code:
            print("blog/analytics.json has no goatcounter code yet - nothing to insert.\n")
            print("  1. sign up at https://www.goatcounter.com/signup  (free for personal use)")
            print("  2. pick a code, e.g. 'wangshuaizs' for wangshuaizs.github.io")
            print("  3. run:  python3 blog/tools/add_analytics.py --code wangshuaizs")
            print(f"\n{len(targets)} pages are already wired up and waiting:")
            for p in targets:
                print(f"  {os.path.relpath(p, SITE)}")
            return

    for p in targets:
        print(f"  {apply_to(p, code):9s} {os.path.relpath(p, SITE)}")
    print("\ndone - " + (f"snippet points at https://{code}.goatcounter.com/count"
                        if code else "snippet removed from every page"))


if __name__ == "__main__":
    main()
