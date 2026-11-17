#!/usr/bin/env python3
"""ABI NEXUS — gen_sitemap.py (S16)
Génère sitemap.xml depuis src/pages/*.html + index.html.
Usage : python3 tools/gen_sitemap.py"""
import glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://abi-nexus.fr"
LASTMOD = "2026-11-17"
META_RE = re.compile(r"<!--META\s*(\{.*?\})\s*-->", re.S)

urls = [("/", "1.0")]  # 404 exclu (pas de page 404 dans un sitemap SEO)
priority = {
    "guide-": "0.9", "meta-": "0.9", "saison7-": "0.8",
    "armes-": "0.8", "map-": "0.8", "equipement-": "0.7",
    "items-": "0.7", "events-": "0.7", "communaute-": "0.6",
    "univers-": "0.6", "cosmetiques-": "0.6",
}
for src in sorted(glob.glob(os.path.join(ROOT, "src", "pages", "*.html"))):
    raw = open(src, encoding="utf-8").read()
    m = META_RE.match(raw)
    if not m:
        continue
    meta = json.loads(m.group(1))
    f = meta["file"]
    if f == "404.html":
        continue
    pr = "0.6"
    for pre, p in priority.items():
        if f.startswith(pre):
            pr = p
            break
    urls.append(("/pages/" + f, pr))

entries = "\n".join(
    f"  <url>\n    <loc>{DOMAIN}{u}</loc>\n    <lastmod>{LASTMOD}</lastmod>\n"
    f"    <changefreq>weekly</changefreq>\n    <priority>{p}</priority>\n  </url>"
    for u, p in urls
)
xml = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + entries
    + "\n</urlset>\n"
)
out = os.path.join(ROOT, "sitemap.xml")
with open(out, "w", encoding="utf-8") as fh:
    fh.write(xml)
print(f"✔ sitemap.xml — {len(urls)} URLs")
