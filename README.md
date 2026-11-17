# ABI NEXUS — Guide Ultime Arena Breakout Infinite

Site statique complet (français, Saison 7 : Utopia) — **69 pages, 5 outils interactifs, PWA hors-ligne**.
Guide communautaire non officiel · Arena Breakout: Infinite © MoreFun Studios / Level Infinite.

---

## 📦 Contenu du dépôt

| Élément | Détail |
|---|---|
| `index.html` / `404.html` | Accueil + page 404 (écrits à la main) |
| `pages/` | 69 pages générées (le site) |
| `css/` | 6 feuilles (design system Orbitron/Rajdhani/Exo 2, dark/light, responsive) |
| `js/` | main, navigation, search, interactivity, map-explorer + 7 JSON de données + Leaflet vendor |
| `img/` | 62 illustrations **JPG** photoréalistes (aucun SVG/PNG) |
| `audio/` | 10 MP3 (4 ambiances + 6 SFX) |
| `sw.js` + `manifest.json` | PWA installable + cache hors-ligne |
| `robots.txt` + `sitemap.xml` | SEO machine (70 URLs) |
| `src/pages/` | Sources HTML des pages (`<!--META …-->` + contenu) |
| `tools/` | Générateur de pages, index de recherche, sitemap, audio |
| `workflow.yaml` | Journal du développement (S0→S23) |

## 🚀 Publier

### Option A — Vercel (recommandé)
```bash
npm i -g vercel
vercel --prod        # à la racine du dépôt : site 100% statique, zéro build
```
Aucune configuration requise. Le domaine par défaut du projet est `abi-nexus.fr` (voir ci-dessous).

### Option B — Any static host (Netlify, Cloudflare Pages, GitHub Pages)
Glisser-déposer le dossier, ou `git push` — **racine du site = racine du dépôt** (index.html au top).

### Option C — Local
```bash
python3 -m http.server 8000
# → http://localhost:8000
```
> Ouvrir `index.html` en `file://` fonctionne aussi (tous les chemins sont relatifs), mais la recherche et les JSON passent mieux via un serveur HTTP.

## 🔁 Changer de domaine

Les URLs absolues (`canonical`, `og:url`, `sitemap.xml`, JSON-LD, `sw.js` hors-ligne) utilisent `https://abi-nexus.fr` :
1. Remplacer dans tout le dépôt : `grep -rl 'abi-nexus.fr' --include='*.html' --include='*.xml' --include='*.txt' --include='*.js' . | xargs sed -i 's/abi-nexus.fr/TON-DOMAINE.fr/g'`
2. Adapter aussi `start_url` dans `manifest.json` si besoin.

## 🛠️ Régénérer après édition de `src/pages/`
```bash
python3 tools/build_site.py            # reconstruit pages/*.html
python3 tools/gen_search_index.py      # met à jour Ctrl+K
python3 tools/gen_sitemap.py           # met à jour sitemap.xml
node --check js/*.js                   # sanity check
```

## ✅ Audit de publication (17/11/2026 — S25 final)
- 71 fichiers HTML (69 pages + index + 404) · **0 lien mort, 0 ancre cassée, 0 page orpheline**
- **227 JPG** (0 SVG/PNG) dont **86 vraies icônes d'objets du jeu** (fandom/abibuilder, converties JPG) et **6 vraies cartes top-down officielles** · 10 MP3 valides
- **0 doublon d'image** : chaque visuel décoratif n'apparaît que sur une seule page (favicon et icônes d'objets = identité, exemptés)
- 58 POI calés sur les vraies cartes (`js/data-maps.json`), explorateur Leaflet par carte
- titres uniques, canonical, OG, JSON-LD (FAQ/Breadcrumb/Article) sur toutes les pages
- titres uniques, canonical, OG, JSON-LD (FAQ/Breadcrumb/Article) sur toutes les pages
- WCAG 2.2 AA de base : skip-links, focus-visible, clavier, reduced-motion, cibles ≥24px
- PWA : manifest + service worker (cache-first assets, network-first pages)

## 📌 Notes
- Le favicon est l'icône JPG `img/icon-app.jpg` (1254×1254) — aucun SVG/PNG dans le projet.
- `hero-armes-attachements.jpg` pointe volontairement vers `card-armes.jpg` (placeholder documenté).
- Aucun traceur, aucune donnée collectée, aucun compte requis.
