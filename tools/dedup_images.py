#!/usr/bin/env python3
# ABI NEXUS — dedup_images.py (S25)
# Each image file must be used by exactly ONE page (user rule).
# For every secondary usage we rewrite ALL refs (META og_image, og:image,
# twitter:image, hero-bg url, <img src>) on that page to a dedicated new file.
# If the new file is not yet generated, the pair is reported as PENDING.
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# (page_slug, old_img_path_rel, new_img_path_rel)  — refs in src/pages use ../img/, index/404 use img/
TABLE = [
    # card-saison7 (keep on index)
    ("communaute-patch-notes",   "img/ui/card-saison7.jpg",        "img/fig/communaute-patch-notes.jpg"),
    ("cosmetiques-skins-perso",  "img/ui/card-saison7.jpg",        "img/fig/cosmetiques-skins-perso.jpg"),
    ("events-calendrier",        "img/ui/card-saison7.jpg",        "img/fig/events-calendrier.jpg"),
    ("saison7-battle-pass",      "img/ui/card-saison7.jpg",        "img/fig/saison7-battle-pass.jpg"),
    ("saison7-nouveautes",       "img/ui/card-saison7.jpg",        "img/fig/saison7-nouveautes.jpg"),
    # card-items (keep on index)
    ("equipement-rigs",          "img/ui/card-items.jpg",          "img/fig/equipement-rigs.jpg"),
    ("guide-craft",              "img/ui/card-items.jpg",          "img/fig/guide-craft.jpg"),
    ("guide-economie",           "img/ui/card-items.jpg",          "img/fig/guide-economie.jpg"),
    ("items-munitions",          "img/ui/card-items.jpg",          "img/fig/items-munitions.jpg"),
    ("meta-loadout-optimizer",   "img/ui/card-items.jpg",          "img/fig/meta-loadout-optimizer.jpg"),
    # card-communaute (keep on index)
    ("a-propos",                 "img/ui/card-communaute.jpg",     "img/fig/a-propos.jpg"),
    ("communaute-ressources",    "img/ui/card-communaute.jpg",     "img/fig/communaute-ressources.jpg"),
    ("communaute-streamers",     "img/ui/card-communaute.jpg",     "img/fig/communaute-streamers.jpg"),
    ("cosmetiques-dog-tags",     "img/ui/card-communaute.jpg",     "img/fig/cosmetiques-dog-tags.jpg"),
    ("cosmetiques-skins-perso",  "img/ui/card-communaute.jpg",     "img/fig/cosmetiques-skins-perso-2.jpg"),
    # card-armes (keep on index)
    ("armes-carbine",            "img/ui/card-armes.jpg",          "img/fig/armes-carbine.jpg"),
    ("armes-pistolets",          "img/ui/card-armes.jpg",          "img/fig/armes-pistolets.jpg"),
    ("armes-shotgun",            "img/ui/card-armes.jpg",          "img/fig/armes-shotgun.jpg"),
    ("cosmetiques-skins-armes",  "img/ui/card-armes.jpg",          "img/fig/cosmetiques-skins-armes.jpg"),
    # card-lore (keep on index)
    ("cosmetiques-dog-tags",     "img/ui/card-lore.jpg",           "img/fig/cosmetiques-dog-tags-2.jpg"),
    ("items-cles",               "img/ui/card-lore.jpg",           "img/fig/items-cles.jpg"),
    ("items-collection-room",    "img/ui/card-lore.jpg",           "img/fig/items-collection-room.jpg"),
    ("items-valeur",             "img/ui/card-lore.jpg",           "img/fig/items-valeur.jpg"),
    # hero-armes-nouveautes-s7 (keep on armes-nouveautes-s7)
    ("armes-attachements-s7",    "img/hero/hero-armes-nouveautes-s7.jpg", "img/fig/armes-attachements-s7.jpg"),
    ("cosmetiques-skins-armes",  "img/hero/hero-armes-nouveautes-s7.jpg", "img/fig/cosmetiques-skins-armes-2.jpg"),
    ("saison7-nouveautes",       "img/hero/hero-armes-nouveautes-s7.jpg", "img/fig/saison7-nouveautes-2.jpg"),
    ("saison7-utopia",           "img/hero/hero-armes-nouveautes-s7.jpg", "img/fig/saison7-utopia.jpg"),
    # card-guides (keep on index; 404 handled separately)
    ("guide-traders",            "img/ui/card-guides.jpg",         "img/fig/guide-traders.jpg"),
    ("items-medical",            "img/ui/card-guides.jpg",         "img/fig/items-medical.jpg"),
    # card-meta (keep on index)
    ("armes-builds",             "img/ui/card-meta.jpg",           "img/fig/armes-builds.jpg"),
    ("armes-lmg",                "img/ui/card-meta.jpg",           "img/fig/armes-lmg.jpg"),
    ("guide-progression",        "img/ui/card-meta.jpg",           "img/fig/guide-progression.jpg"),
    # a545-ak15sc (keep on armes-fusils-assaut)
    ("map-valley",               "img/armes/a545-ak15sc.jpg",      "img/fig/map-valley.jpg"),
    ("INDEX",                    "img/armes/a545-ak15sc.jpg",      "img/fig/index-armes.jpg"),
    # infected-farm (keep on saison7-zombie-infected-zone)
    ("map-no-mans-land",         "img/zombies/infected-farm.jpg",  "img/fig/map-no-mans-land.jpg"),
    ("INDEX",                    "img/zombies/infected-farm.jpg",  "img/fig/index-zombie.jpg"),
    # content-guide-debutant (keep on guide-debutant)
    ("armes-attachements-s7",    "img/ui/content-guide-debutant.jpg", "img/fig/armes-attachements-s7-2.jpg"),
    ("items-medical",            "img/ui/content-guide-debutant.jpg", "img/fig/items-medical-2.jpg"),
    # hero-saison7-zombie-research (keep on saison7-zombie-research)
    ("items-craft-workbench",    "img/hero/hero-saison7-zombie-research.jpg", "img/fig/items-craft-workbench.jpg"),
    ("saison7-zombie-endless",   "img/hero/hero-saison7-zombie-research.jpg", "img/fig/saison7-zombie-endless.jpg"),
    # news-guide-* (keep on index)
    ("guide-avance",             "img/ui/news-guide-avance.jpg",   "img/ui/content-guide-avance.jpg"),  # free: unused file
    ("guide-debutant",           "img/ui/news-guide-debutant.jpg", "img/fig/guide-debutant.jpg"),
    # 2-way heroes: keep on named page
    ("meta-builds-roles",        "img/hero/hero-armes-builds.jpg",           "img/fig/meta-builds-roles.jpg"),
    ("items-koen-economy",       "img/hero/hero-guide-economie.jpg",         "img/fig/items-koen-economy.jpg"),
    ("communaute-patch-notes",   "img/hero/hero-saison7-balance-changes.jpg","img/fig/communaute-patch-notes-2.jpg"),
    ("items-craft-workbench",    "img/hero/hero-guide-craft.jpg",            "img/fig/items-craft-workbench-2.jpg"),
    ("communaute-ressources",    "img/hero/hero-communaute-streamers.jpg",   "img/fig/communaute-ressources-2.jpg"),
    ("saison7-zombie-research",  "img/hero/hero-saison7-zombie-infected-zone.jpg", "img/fig/saison7-zombie-research.jpg"),
    ("events-calendrier",        "img/hero/hero-saison7-utopia.jpg",         "img/fig/events-calendrier-2.jpg"),
    ("items-collection-room",    "img/hero/hero-saison7-battle-pass.jpg",    "img/fig/items-collection-room-2.jpg"),
    ("meta-tier-list-globale",   "img/hero/hero-armes-tier-list.jpg",        "img/fig/meta-tier-list-globale.jpg"),
    ("meta-tier-list-globale",   "img/hero/hero-armes-fusils-assaut.jpg",    "img/fig/meta-tier-list-globale-2.jpg"),
]

def page_src(slug):
    return "index.html" if slug == "INDEX" else f"src/pages/{slug}.html"

applied, pending = [], []
for slug, old, new in TABLE:
    p = page_src(slug)
    if not os.path.exists(p):
        print("!! page absente:", p); continue
    s = open(p, encoding="utf-8").read()
    if old not in s:
        continue  # already applied
    if not os.path.exists(new):
        pending.append((slug, old, new)); continue
    s = s.replace(old, new)
    open(p, "w", encoding="utf-8").write(s)
    applied.append((slug, old, new))

# 404 og:image -> fig-404 (free)
p = "404.html"
s = open(p, encoding="utf-8").read()
if "img/ui/card-guides.jpg" in s:
    s = s.replace("img/ui/card-guides.jpg", "img/ui/fig-404.jpg")
    open(p, "w", encoding="utf-8").write(s)
    applied.append(("404", "card-guides", "fig-404"))

print(f"APPLIQUÉS: {len(applied)}")
for a in applied: print("  ok", a[0], a[1], "->", a[2])
print(f"EN ATTENTE (fichier à générer): {len(pending)}")
for pg, o, n in pending: print("  pending", pg, "|", n)
