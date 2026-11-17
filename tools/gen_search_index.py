#!/usr/bin/env python3
"""ABI NEXUS — gen_search_index.py
Construit js/data-search-index.json depuis les META de src/pages/*.html
+ index.html + 404.html. Usage : python3 tools/gen_search_index.py"""
import json, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META_RE = re.compile(r"<!--META\s*(\{.*?\})\s*-->", re.S)

def heading_of(content):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.S)
    if m:
        return re.sub(r"<[^>]+>", " ", m.group(1)).strip()
    return ""

items = []
for src in sorted(glob.glob(os.path.join(ROOT, "src", "pages", "*.html"))):
    raw = open(src, encoding="utf-8").read()
    m = META_RE.match(raw)
    if not m:
        continue
    meta = json.loads(m.group(1))
    content = raw[m.end():]
    # Section headings (h2) for deeper matching
    h2s = [re.sub(r"<[^>]+>", " ", h).strip() for h in re.findall(r"<h2[^>]*>(.*?)</h2>", content, re.S)]
    items.append({
        "file": meta["file"],
        "title": meta["title"].replace(" | NEXUS", ""),
        "desc": meta.get("description", ""),
        "kw": meta.get("keywords", ""),
        "h": heading_of(content),
        "sections": " ".join(h2s)[:400],
    })

# Pages racine
for extra in ("index.html", "404.html"):
    p = os.path.join(ROOT, extra)
    if os.path.exists(p):
        raw = open(p, encoding="utf-8").read()
        t = re.search(r"<title>(.*?)</title>", raw)
        d = re.search(r'name="description" content="(.*?)"', raw)
        items.append({
            "file": "../" + extra if extra != "index.html" else "../index.html",
            "title": (t.group(1) if t else "ABI NEXUS").replace(" | ABI NEXUS", "").replace(" — ABI NEXUS", ""),
            "desc": d.group(1) if d else "",
            "kw": "accueil arena breakout infinite guide",
            "h": "", "sections": "",
        })

# catégories depuis le préfixe de fichier
def cat(f):
    if f.startswith("guide-"): return "Guide"
    if f.startswith("armes-"): return "Armes"
    if f.startswith("equipement-"): return "Équipement"
    if f.startswith("map-"): return "Carte"
    if f.startswith("saison7-"): return "Saison 7"
    if f.startswith("items-"): return "Objets"
    if f.startswith("cosmetiques-"): return "Cosmétiques"
    if f.startswith("meta-"): return "Méta"
    if f.startswith("events-"): return "Événements"
    if f.startswith("communaute-"): return "Communauté"
    if f.startswith("univers-"): return "Univers"
    return "Site"

for it in items:
    it["cat"] = cat(it["file"])

out = os.path.join(ROOT, "js", "data-search-index.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, separators=(",", ":"))
print(f"✔ {len(items)} entrées → js/data-search-index.json ({os.path.getsize(out)//1024} KB)")
