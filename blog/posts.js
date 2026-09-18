/* ------------------------------------------------------------------
 * Blog post registry  —  blog/posts.js
 *
 * Adding a post:
 *   1. create  blog/posts/<slug>/en.html  (and zh.html if there is a
 *      Chinese version; either language may be omitted)
 *   2. add one entry below, newest first (the list also sorts by date)
 *
 * Entry fields
 *   slug     folder name under blog/posts/
 *   date     ISO date, used for sorting and display
 *   topics   free-form tags; the filter bar on the blog index is
 *            generated automatically from whatever appears here
 *   en / zh  title + summary for each available language.
 *            Leave a language out entirely if that version does not exist.
 * ------------------------------------------------------------------ */
window.BLOG_POSTS = [
  {
    slug: "rpki-valid-hijacks-2026",
    date: "2026-09-18",
    topics: ["RPKI", "BGP Security", "Internet Measurement"],
    en: {
      title: "Hetzner Impersonated, 23,000 China Mobile Prefixes Hijacked: Why Didn't RPKI Stop It?",
      summary: "Between June and August 2026 the routing system recorded two large-scale BGP hijacks. Both attack routes passed origin validation — and both still won. A close look at prefix length, AS_PATH length, and what origin validation can and cannot prove."
    },
    zh: {
      title: "Hetzner 被冒名、中国移动 2.3 万前缀被劫：RPKI 为什么没拦住？",
      summary: "2026 年 6–8 月，路由系统记录了两起大规模 BGP 劫持。两条攻击路由都通过了 origin 验证，却都赢了。本文拆解前缀长度与 AS_PATH 长度这两条独立的攻击路径，以及 origin 验证能证明什么、不能证明什么。"
    }
  }
];
