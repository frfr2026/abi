#!/usr/bin/env python3
"""ABI NEXUS — générateur de pages : assemble head + nav + footer
depuis des sources partielles (src/pages/*.html).
Chaque source commence par un bloc META JSON, puis du HTML <main>.
Usage : python3 tools/build_site.py [nom_page ...]   (sans args = tout)"""
import json, os, re, sys, glob

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT_DIR, "src", "pages")
OUT = os.path.join(ROOT_DIR, "pages")

# ── NAV (préfixe {R} = "../") ──────────────────────────────
NAV = r'''<header class="nav" role="banner">
    <div class="nav-inner">
      <a class="logo" href="{R}index.html" aria-label="ABI NEXUS — Accueil">
        <svg viewBox="0 0 64 64" aria-hidden="true"><path d="M32 4 58 18v28L32 60 6 46V18z" fill="none" stroke="#C8A84B" stroke-width="3"/><circle cx="32" cy="32" r="10" fill="none" stroke="#2EFF8F" stroke-width="2.5"/><path d="M32 16v8M32 40v8M16 32h8M40 32h8" stroke="#2EFF8F" stroke-width="2.5"/></svg>
        <span>ABI<span class="logo-nexus">NEXUS</span><span class="logo-sub">SEASON 7 · UTOPIA</span></span>
      </a>
      <nav class="nav-links" aria-label="Navigation principale">
        <div class="nav-item has-mega">
          <a class="nav-link" data-sfx="sfx-transition" href="{R}pages/guide-debutant.html">Guides <svg class="caret" width="10" height="10"><use href="#ico-chevron"/></svg></a>
          <div class="mega-menu" role="menu">
            <a class="mega-link" href="{R}pages/guide-debutant.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-book"/></svg></span><span><span class="m-title">Guide du débutant</span><span class="m-desc">Premières raids, bases du jeu, survivre sa première semaine</span></span></a>
            <a class="mega-link" href="{R}pages/guide-avance.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-crosshair"/></svg></span><span><span class="m-title">Guide avancé</span><span class="m-desc">Pénétration, audio, risque/récompense, tactics expertes</span></span></a>
            <a class="mega-link" href="{R}pages/guide-extraction.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-map"/></svg></span><span><span class="m-title">Extraction</span><span class="m-desc">Points d'exfil, routes, survie sous pression</span></span></a>
            <a class="mega-link" href="{R}pages/guide-economie.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-box"/></svg></span><span><span class="m-title">Économie Koen</span><span class="m-desc">Devenir riche : market, ventes, ratio valeur/slot</span></span></a>
            <a class="mega-link" href="{R}pages/guide-craft.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-tool"/></svg></span><span><span class="m-title">Craft & Workbench</span><span class="m-desc">Formules, Recherche S7, optimisation de bench</span></span></a>
            <a class="mega-link" href="{R}pages/guide-traders.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-users"/></svg></span><span><span class="m-title">Marchands</span><span class="m-desc">Deke, Rodriguez & co — offres, barters, astuces</span></span></a>
            <a class="mega-link" href="{R}pages/guide-progression.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-star"/></svg></span><span><span class="m-title">Progression</span><span class="m-desc">Niveaux, masteries, Battle Pass S7</span></span></a>
            <a class="mega-link" href="{R}pages/performances-reglages.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-tool"/></svg></span><span><span class="m-title">Performances ★</span><span class="m-desc">FPS, réglages, DLSS — gagne +60% de FPS</span></span></a>
          </div>
        </div>
        <div class="nav-item has-mega">
          <a class="nav-link" data-sfx="sfx-transition" href="{R}pages/armes-fusils-assaut.html">Armes <svg class="caret" width="10" height="10"><use href="#ico-chevron"/></svg></a>
          <div class="mega-menu" role="menu">
            <a class="mega-link" href="{R}pages/armes-fusils-assaut.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-gun"/></svg></span><span><span class="m-title">Fusils d'assaut</span><span class="m-desc">H416, A545, AK-15SC, AEK, FAL… stats & builds</span></span></a>
            <a class="mega-link" href="{R}pages/armes-dmr.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-crosshair"/></svg></span><span><span class="m-title">DMR</span><span class="m-desc">M110, MK14, SKS, VSS — demi-auto de précision</span></span></a>
            <a class="mega-link" href="{R}pages/armes-smg.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-gun"/></svg></span><span><span class="m-title">SMG</span><span class="m-desc">P90, MPX, Vector, PCC-9 — rois du CQB</span></span></a>
            <a class="mega-link" href="{R}pages/armes-sniper.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-crosshair"/></svg></span><span><span class="m-title">Snipers</span><span class="m-desc">M24, Mosin — un coup, une extraction</span></span></a>
            <a class="mega-link" href="{R}pages/armes-shotgun.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-gun"/></svg></span><span><span class="m-title">Shotguns</span><span class="m-desc">M870, USAS-12 — destruction rapprochée</span></span></a>
            <a class="mega-link" href="{R}pages/armes-pistolets.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-gun"/></svg></span><span><span class="m-title">Pistolets</span><span class="m-desc">Sidesarms & backups économiques</span></span></a>
            <a class="mega-link" href="{R}pages/armes-nouveautes-s7.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-star"/></svg></span><span><span class="m-title">Nouveautés S7 ★</span><span class="m-desc">A545 & AK-15SC — les nouvelles tueuses</span></span></a>
            <a class="mega-link" href="{R}pages/armes-tier-list.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-star"/></svg></span><span><span class="m-title">Tier list armes</span><span class="m-desc">Classement complet S7 par catégorie</span></span></a>
            <a class="mega-link" href="{R}pages/armes-attachements.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-tool"/></svg></span><span><span class="m-title">Attachements</span><span class="m-desc">1 175 mods — optiques, canons, chargeurs</span></span></a>
            <a class="mega-link" href="{R}pages/armes-builds.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-box"/></svg></span><span><span class="m-title">Builds</span><span class="m-desc">Meta & budget — configs de la communauté</span></span></a>
          </div>
        </div>
        <div class="nav-item has-mega">
          <a class="nav-link" data-sfx="sfx-transition" href="{R}pages/equipement-armures.html">Équipement <svg class="caret" width="10" height="10"><use href="#ico-chevron"/></svg></a>
          <div class="mega-menu" role="menu">
            <a class="mega-link" href="{R}pages/equipement-armures.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-shield"/></svg></span><span><span class="m-title">Armures T1–T6</span><span class="m-desc">BT101, 926 Composite — durabilité & pen</span></span></a>
            <a class="mega-link" href="{R}pages/equipement-casques.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-shield"/></svg></span><span><span class="m-title">Casques</span><span class="m-desc">51 casques — plus de ricochet en S7 !</span></span></a>
            <a class="mega-link" href="{R}pages/equipement-rigs.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-box"/></svg></span><span><span class="m-title">Rigs</span><span class="m-desc">57 rigs — slots, poids, pénalités</span></span></a>
            <a class="mega-link" href="{R}pages/equipement-sacs.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-box"/></svg></span><span><span class="m-title">Sacs à dos</span><span class="m-desc">28 sacs — volume de butin maximal</span></span></a>
            <a class="mega-link" href="{R}pages/equipement-headsets.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-star"/></svg></span><span><span class="m-title">Casques audio</span><span class="m-desc">Commander, GS2 — dominer l'oreille</span></span></a>
            <a class="mega-link" href="{R}pages/equipement-tier-list.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-star"/></svg></span><span><span class="m-title">Tier list équipement</span><span class="m-desc">Les meilleures protections du meta S7</span></span></a>
          </div>
        </div>
        <div class="nav-item has-mega">
          <a class="nav-link" data-sfx="sfx-transition" href="{R}pages/map-farm.html">Cartes <svg class="caret" width="10" height="10"><use href="#ico-chevron"/></svg></a>
          <div class="mega-menu" role="menu">
            <a class="mega-link" href="{R}pages/map-farm.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-map"/></svg></span><span><span class="m-title">Farm ★</span><span class="m-desc">Fermes & champs — Heavy Infected Zone S7</span></span></a>
            <a class="mega-link" href="{R}pages/map-valley.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-map"/></svg></span><span><span class="m-title">Valley ★</span><span class="m-desc">Barrage & vallée — Infected Zone S7</span></span></a>
            <a class="mega-link" href="{R}pages/map-northridge.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-map"/></svg></span><span><span class="m-title">Northridge</span><span class="m-desc">Villas côteuses & hôtel de luxe</span></span></a>
            <a class="mega-link" href="{R}pages/map-armory.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-map"/></svg></span><span><span class="m-title">Armory</span><span class="m-desc">Base militaire — loot et tension</span></span></a>
            <a class="mega-link" href="{R}pages/map-tv-station.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-map"/></svg></span><span><span class="m-title">TV Station</span><span class="m-desc">CQB brutal — le cimetière des squads</span></span></a>
            <a class="mega-link" href="{R}pages/map-airport.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-map"/></svg></span><span><span class="m-title">Airport ★</span><span class="m-desc">Piste & hangars — Heavy Infected + Endless</span></span></a>
            <a class="mega-link" href="{R}pages/map-no-mans-land.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-virus"/></svg></span><span><span class="m-title">No Man's Land</span><span class="m-desc">PvE sans joueurs — version Zombies S7</span></span></a>
            <span class="mega-sep" aria-hidden="true"></span>
            <a class="mega-link" href="https://maps.tcno.co/abi" target="_blank" rel="noopener"><span class="m-ico"><svg width="16" height="16"><use href="#ico-map"/></svg></span><span><span class="m-title">↗ maps.tcno.co/abi</span><span class="m-desc">Cartes interactives live — spawns, loot, exfils</span></span></a>
            <a class="mega-link" href="https://abibuilder.com/maps" target="_blank" rel="noopener"><span class="m-ico"><svg width="16" height="16"><use href="#ico-map"/></svg></span><span><span class="m-title">↗ abibuilder.com/maps</span><span class="m-desc">Calques de loot & clés communautaires</span></span></a>
            <a class="mega-link" href="https://arena-breakout-infinite.fandom.com/wiki/Special:AllMaps" target="_blank" rel="noopener"><span class="m-ico"><svg width="16" height="16"><use href="#ico-map"/></svg></span><span><span class="m-title">↗ Fandom — toutes les cartes</span><span class="m-desc">Galerie officielle des layouts</span></span></a>
            <a class="mega-link" href="https://arenabreakout-infinite.com/fr/maps/" target="_blank" rel="noopener"><span class="m-ico"><svg width="16" height="16"><use href="#ico-map"/></svg></span><span><span class="m-title">↗ ABI Database — cartes</span><span class="m-desc">Exfils, clés, boss par secteur</span></span></a>
          </div>
        </div>
        <div class="nav-item has-mega">
          <a class="nav-link" data-sfx="sfx-transition" href="{R}pages/saison7-utopia.html" style="color:var(--color-accent-orange)">Saison 7 <svg class="caret" width="10" height="10"><use href="#ico-chevron"/></svg></a>
          <div class="mega-menu" role="menu">
            <a class="mega-link" href="{R}pages/saison7-utopia.html"><span class="m-ico" style="color:var(--color-accent-orange)"><svg width="16" height="16"><use href="#ico-virus"/></svg></span><span><span class="m-title">Utopia — Hub ★</span><span class="m-desc">TOUTES les nouveautés de la saison</span></span></a>
            <a class="mega-link" href="{R}pages/saison7-zombie-infected-zone.html"><span class="m-ico" style="color:var(--color-accent-orange)"><svg width="16" height="16"><use href="#ico-virus"/></svg></span><span><span class="m-title">Infected Zone</span><span class="m-desc">PvPvE zombies — 6 mutants, marchand in-raid</span></span></a>
            <a class="mega-link" href="{R}pages/saison7-zombie-endless.html"><span class="m-ico" style="color:var(--color-accent-orange)"><svg width="16" height="16"><use href="#ico-virus"/></svg></span><span><span class="m-title">Zombie Endless</span><span class="m-desc">PvE vagues infinies — niveau 8+, Airport</span></span></a>
            <a class="mega-link" href="{R}pages/saison7-zombie-research.html"><span class="m-ico" style="color:var(--color-accent-orange)"><svg width="16" height="16"><use href="#ico-star"/></svg></span><span><span class="m-title">Zombie Research</span><span class="m-desc">Arbre de perks permanent hors-raid</span></span></a>
            <a class="mega-link" href="{R}pages/saison7-balance-changes.html"><span class="m-ico" style="color:var(--color-accent-orange)"><svg width="16" height="16"><use href="#ico-crosshair"/></svg></span><span><span class="m-title">Balance changes</span><span class="m-desc">Portées, headshots, fin du RNG T5/T6</span></span></a>
            <a class="mega-link" href="{R}pages/saison7-battle-pass.html"><span class="m-ico" style="color:var(--color-accent-orange)"><svg width="16" height="16"><use href="#ico-star"/></svg></span><span><span class="m-title">Battle Pass</span><span class="m-desc">Récompenses complètes du pass S7</span></span></a>
            <a class="mega-link" href="{R}pages/saison7-nouveautes.html"><span class="m-ico" style="color:var(--color-accent-orange)"><svg width="16" height="16"><use href="#ico-box"/></svg></span><span><span class="m-title">Toutes les nouveautés</span><span class="m-desc">A545, AK-15SC, kits saisonniers, Elysium</span></span></a>
            <a class="mega-link" href="{R}pages/items-valeur.html"><span class="m-ico" style="color:var(--color-rarity-red)"><svg width="16" height="16"><use href="#ico-box"/></svg></span><span><span class="m-title">Loot rouge S7</span><span class="m-desc">Elysium (~4,5M) & nouveaux collectibles</span></span></a>
          </div>
        </div>
        <div class="nav-item has-mega">
          <a class="nav-link" data-sfx="sfx-transition" href="{R}pages/meta-tier-list-globale.html">Plus <svg class="caret" width="10" height="10"><use href="#ico-chevron"/></svg></a>
          <div class="mega-menu" role="menu" style="min-width:640px; grid-template-columns:repeat(3,1fr)">
            <a class="mega-link" href="{R}pages/items-munitions.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-box"/></svg></span><span><span class="m-title">Munitions</span><span class="m-desc">70 munitions, pénétration, caps S7</span></span></a>
            <a class="mega-link" href="{R}pages/items-medical.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-shield"/></svg></span><span><span class="m-title">Médical</span><span class="m-desc">49 items — soins & stims</span></span></a>
            <a class="mega-link" href="{R}pages/items-cles.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-tool"/></svg></span><span><span class="m-title">Clés</span><span class="m-desc">117 clés & leurs emplacements</span></span></a>
            <a class="mega-link" href="{R}pages/items-valeur.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-star"/></svg></span><span><span class="m-title">Objets de valeur</span><span class="m-desc">Rouges, collectibles, Elysium</span></span></a>
            <a class="mega-link" href="{R}pages/items-craft-workbench.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-tool"/></svg></span><span><span class="m-title">Workbench</span><span class="m-desc">Craft & Recherche de formules S7</span></span></a>
            <a class="mega-link" href="{R}pages/items-koen-economy.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-box"/></svg></span><span><span class="m-title">Économie Koen</span><span class="m-desc">Marché, astuces de vente, fortune</span></span></a>
            <a class="mega-link" href="{R}pages/cosmetiques-skins-perso.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-star"/></svg></span><span><span class="m-title">Cosmétiques</span><span class="m-desc">Skins persos dont Emerald Arachnid</span></span></a>
            <a class="mega-link" href="{R}pages/meta-loadout-optimizer.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-tool"/></svg></span><span><span class="m-title">Loadout Optimizer</span><span class="m-desc">Construis ton meilleur équipement</span></span></a>
            <a class="mega-link" href="{R}pages/univers-lore.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-book"/></svg></span><span><span class="m-title">Lore & Univers</span><span class="m-desc">Kamona, factions, Dark Zone</span></span></a>
            <a class="mega-link" href="{R}pages/events-calendrier.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-calendar"/></svg></span><span><span class="m-title">Événements</span><span class="m-desc">Halloween, Warlord III, calendrier</span></span></a>
            <a class="mega-link" href="{R}pages/events-dim-dou-duk.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-box"/></svg></span><span><span class="m-title">Dim Dou Duk ★</span><span class="m-desc">Collab Gourmet Market — vouchers → 06/12</span></span></a>
            <a class="mega-link" href="{R}pages/modes-secure-ops.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-shield"/></svg></span><span><span class="m-title">Secure Ops ★</span><span class="m-desc">Mode sans perte de gear — cap 600k</span></span></a>
            <a class="mega-link" href="{R}pages/communaute-ressources.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-users"/></svg></span><span><span class="m-title">Communauté</span><span class="m-desc">Reddit, YouTube, outils, streamers</span></span></a>
            <a class="mega-link" href="{R}pages/communaute-patch-notes.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-book"/></svg></span><span><span class="m-title">Patch notes</span><span class="m-desc">Historique complet des updates</span></span></a>
            <a class="mega-link" href="{R}pages/communaute-saisons.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-calendar"/></svg></span><span><span class="m-title">Saisons ★</span><span class="m-desc">Historique complet S0 → S7</span></span></a>
            <a class="mega-link" href="{R}pages/plan-site.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-book"/></svg></span><span><span class="m-title">Plan du site</span><span class="m-desc">Les 68 pages, famille par famille</span></span></a>
            <a class="mega-link" href="{R}pages/a-propos.html"><span class="m-ico"><svg width="16" height="16"><use href="#ico-users"/></svg></span><span><span class="m-title">À propos</span><span class="m-desc">Méthodologie &amp; sources du guide</span></span></a>
          </div>
        </div>
      </nav>
      <div class="nav-actions">
        <button class="nav-search" data-search-open aria-label="Ouvrir la recherche globale">
          <svg width="15" height="15"><use href="#ico-search"/></svg>
          <span>Rechercher…</span>
          <kbd>Ctrl K</kbd>
        </button>
        <button class="icon-btn" data-theme-toggle aria-label="Basculer le thème clair/obscur"><span class="theme-icon">☀️</span></button>
        <button class="hamburger" aria-label="Menu" aria-expanded="false">
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>
  </header>'''

SPRITE = r'''<svg width="0" height="0" style="position:absolute" aria-hidden="true">
    <defs>
      <symbol id="ico-book" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></symbol>
      <symbol id="ico-gun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12h13l4-4h3v5l-4 2-2 4H8l-2-4H2z"/><path d="M7 12v4"/></symbol>
      <symbol id="ico-shield" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></symbol>
      <symbol id="ico-map" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></symbol>
      <symbol id="ico-virus" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="6"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M19.1 4.9l-2.8 2.8M7.7 16.3l-2.8 2.8"/></symbol>
      <symbol id="ico-box" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.3 7 12 12 20.7 7"/><line x1="12" y1="22" x2="12" y2="12"/></symbol>
      <symbol id="ico-star" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></symbol>
      <symbol id="ico-users" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></symbol>
      <symbol id="ico-search" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></symbol>
      <symbol id="ico-crosshair" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 3v5M12 16v5M3 12h5M16 12h5"/></symbol>
      <symbol id="ico-calendar" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></symbol>
      <symbol id="ico-tool" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18v3h3l6.3-6.3a4 4 0 0 0 5.4-5.4l-2.8 2.8-2.1-2.1 2.9-2.7z"/></symbol>
      <symbol id="ico-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></symbol>
      <symbol id="ico-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></symbol>
    </defs>
  </svg>'''

FOOTER = r'''<footer class="footer" role="contentinfo">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a class="logo" href="{R}index.html">
            <svg viewBox="0 0 64 64" aria-hidden="true"><path d="M32 4 58 18v28L32 60 6 46V18z" fill="none" stroke="#C8A84B" stroke-width="3"/><circle cx="32" cy="32" r="10" fill="none" stroke="#2EFF8F" stroke-width="2.5"/><path d="M32 16v8M32 40v8M16 32h8M40 32h8" stroke="#2EFF8F" stroke-width="2.5"/></svg>
            <span>ABI<span class="logo-nexus">NEXUS</span></span>
          </a>
          <p>Le guide de référence ultime d'Arena Breakout Infinite — armes, armures, cartes, stratégies et Saison 7 : Utopia. Contenu 100 % français, basé sur les patch notes officielles et la communauté.</p>
          <div class="footer-social">
            <a class="icon-btn" href="https://www.reddit.com/r/ArenaBreakoutInfinite/" target="_blank" rel="noopener" aria-label="Reddit"><svg width="16" height="16"><use href="#ico-users"/></svg></a>
            <a class="icon-btn" href="https://www.youtube.com/@ArenaBreakoutInfinite" target="_blank" rel="noopener" aria-label="YouTube"><svg width="16" height="16"><use href="#ico-star"/></svg></a>
            <a class="icon-btn" href="https://x.com/ArenaBreakoutPC" target="_blank" rel="noopener" aria-label="X / Twitter"><svg width="16" height="16"><use href="#ico-crosshair"/></svg></a>
            <a class="icon-btn" href="https://www.arenabreakoutinfinite.com/" target="_blank" rel="noopener" aria-label="Site officiel"><svg width="16" height="16"><use href="#ico-gun"/></svg></a>
          </div>
        </div>
        <div class="footer-col">
          <h4>Guides</h4>
          <a href="{R}pages/guide-debutant.html">Guide débutant</a>
          <a href="{R}pages/guide-avance.html">Guide avancé</a>
          <a href="{R}pages/guide-extraction.html">Extraction</a>
          <a href="{R}pages/guide-economie.html">Économie</a>
          <a href="{R}pages/guide-craft.html">Craft</a>
          <a href="{R}pages/guide-traders.html">Marchands</a>
          <a href="{R}pages/guide-progression.html">Progression</a>
          <a href="{R}pages/performances-reglages.html">Performances &amp; FPS</a>
        </div>
        <div class="footer-col">
          <h4>Jeu</h4>
          <a href="{R}pages/armes-fusils-assaut.html">Armes</a>
          <a href="{R}pages/armes-tier-list.html">Tier list armes</a>
          <a href="{R}pages/equipement-armures.html">Armures</a>
          <a href="{R}pages/map-farm.html">Cartes</a>
          <a href="{R}pages/items-munitions.html">Munitions</a>
          <a href="{R}pages/items-valeur.html">Objets de valeur</a>
          <a href="{R}pages/meta-loadout-optimizer.html">Loadout optimizer</a>
        </div>
        <div class="footer-col">
          <h4>Saison 7 & Communauté</h4>
          <a href="{R}pages/saison7-utopia.html">Hub Utopia</a>
          <a href="{R}pages/saison7-zombie-infected-zone.html">Infected Zone</a>
          <a href="{R}pages/saison7-battle-pass.html">Battle Pass</a>
          <a href="{R}pages/events-calendrier.html">Événements</a>
          <a href="{R}pages/events-dim-dou-duk.html">Dim Dou Duk</a>
          <a href="{R}pages/communaute-ressources.html">Ressources</a>
          <a href="{R}pages/communaute-patch-notes.html">Patch notes</a>
          <a href="{R}pages/communaute-saisons.html">Saisons</a>
          <a href="{R}pages/plan-site.html">Plan du site</a>
          <a href="{R}pages/a-propos.html">À propos</a>
          <a href="{R}pages/univers-lore.html">Lore</a>
        </div>
      </div>
      <div class="footer-bottom">
        <span>© <span data-year>2026</span> ABI NEXUS — Guide communautaire non officiel. Arena Breakout: Infinite © MoreFun Studios / Level Infinite.</span>
        <span>Dernière mise à jour : <time datetime="2026-11-17">17 novembre 2026</time> · Patch cible 1.0.0.142.19+</span>
      </div>
    </div>
  </footer>'''

MODAL = r'''<div class="search-modal" role="dialog" aria-modal="true" aria-label="Recherche globale">
    <div class="search-box">
      <input type="search" placeholder="Rechercher une arme, une carte, un guide…" aria-label="Rechercher">
      <div class="search-results">
        <div class="search-empty">Tape ta requête — résultats instantanés sur les armes, armures, cartes et guides.</div>
      </div>
    </div>
  </div>'''

PLAYER = r'''<div class="audio-player" aria-label="Lecteur d'ambiance">
    <button class="ap-btn" aria-label="Lecture / pause de l'ambiance">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
    </button>
    <div class="ap-info">
      <div class="ap-title">Ambiance</div>
      <div class="ap-state">Pause</div>
    </div>
    <input type="range" min="0" max="100" value="50" aria-label="Volume">
  </div>'''

TEMPLATE = r'''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="keywords" content="{keywords}">
  <link rel="canonical" href="https://abi-nexus.fr/pages/{file}">
  <link rel="alternate" hreflang="fr" href="https://abi-nexus.fr/pages/{file}">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:site_name" content="ABI NEXUS">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="../{og_image}">
  <meta property="og:url" content="https://abi-nexus.fr/pages/{file}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="../{og_image}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@400;500;600;700&family=Exo+2:wght@300;400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{R}css/variables.css">
  <link rel="stylesheet" href="{R}css/main.css">
  <link rel="stylesheet" href="{R}css/animations.css">
  <link rel="stylesheet" href="{R}css/components.css">
  <link rel="stylesheet" href="{R}css/responsive.css">
  <link rel="stylesheet" href="{R}css/interactivity.css">
  <link rel="icon" type="image/jpeg" href="{R}img/icon-app.jpg">
<link rel="manifest" href="{R}manifest.json">
  <meta name="theme-color" content="#0A0C0F">
{jsonld}
</head>
<body data-root="../" data-ambiance="{ambiance}">

  <a class="skip-link" href="#contenu">Aller au contenu principal</a>
  <div class="reading-progress" aria-hidden="true"></div>
  <div class="page-transition" aria-hidden="true"></div>

  {sprite}

  {nav}

  <main id="contenu">
{content}
  </main>

  {footer}

  {modal}

  {player}

  <script src="{R}js/main.js" defer></script>
  <script src="{R}js/navigation.js" defer></script>
</body>
</html>
'''

META_RE = re.compile(r"^\s*<!--META\s*(\{.*?\})\s*-->", re.S)


def build_jsonld(meta: dict) -> str:
    """Génère FAQPage / BreadcrumbList / Article JSON-LD depuis le META."""
    parts = []
    faq = meta.get("faq") or []
    if faq:
        parts.append(json.dumps({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]
        }, ensure_ascii=False))
    bc = meta.get("breadcrumb")
    if bc:
        items = []
        for i, (label, slug) in enumerate(bc):
            url = "https://abi-nexus.fr/" if slug == "index.html" else f"https://abi-nexus.fr/pages/{slug}"
            items.append({"@type": "ListItem", "position": i + 1, "name": label, "item": url})
        parts.append(json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                                 "itemListElement": items}, ensure_ascii=False))
    if meta.get("article"):
        parts.append(json.dumps({
            "@context": "https://schema.org", "@type": "Article",
            "headline": meta["title"], "description": meta["description"],
            "datePublished": "2026-11-17", "dateModified": "2026-11-17",
            "author": {"@type": "Organization", "name": "ABI NEXUS"},
            "publisher": {"@type": "Organization", "name": "ABI NEXUS"},
            "image": f"https://abi-nexus.fr/{meta.get('og_image', 'img/hero/hero-accueil.jpg')}",
            "inLanguage": "fr-FR"
        }, ensure_ascii=False))
    return "\n".join(f'<script type="application/ld+json">{p}</script>' for p in parts)


def build(src_path: str) -> str:
    raw = open(src_path, encoding="utf-8").read()
    m = META_RE.match(raw)
    if not m:
        raise ValueError(f"Pas de bloc META dans {src_path}")
    meta = json.loads(m.group(1))
    content = raw[m.end():].strip()
    out = TEMPLATE.format(
        title=meta["title"],
        desc=meta["description"],
        keywords=meta.get("keywords", "Arena Breakout Infinite, ABI, guide"),
        file=meta["file"],
        og_image=meta.get("og_image", "img/hero/hero-accueil.jpg"),
        jsonld=build_jsonld(meta),
        ambiance=meta.get("ambiance", "guides"),
        sprite=SPRITE,
        nav=NAV,
        content=content,
        footer=FOOTER,
        modal=MODAL,
        player=PLAYER,
        R="../",
    )
    # NAV/FOOTER/SHEET passées comme valeurs : leurs propres {R} ne sont
    # pas substitués récursivement par str.format — on les remplace ici.
    out = out.replace("{R}", "../")
    # Scripts d'interactivité (S15) : search + widgets partout,
    # Leaflet + map-explorer uniquement sur les pages map-*.
    extra_head = ""
    extra_tail = ('  <script src="../js/search.js" defer></script>\n'
                  '  <script src="../js/interactivity.js" defer></script>\n')
    if meta["file"].startswith("map-"):
        extra_head = '  <link rel="stylesheet" href="../js/vendor/leaflet.css">\n'
        extra_tail = ('  <script src="../js/vendor/leaflet.js" defer></script>\n'
                      '  <script src="../js/map-explorer.js" defer></script>\n' + extra_tail)
    if extra_head:
        out = out.replace("</head>", extra_head + "</head>", 1)
    out = out.replace("</body>", "  " + extra_tail + "</body>", 1)
    dest = os.path.join(OUT, meta["file"])
    with open(dest, "w", encoding="utf-8") as f:
        f.write(out)
    return dest


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    targets = sys.argv[1:] or sorted(glob.glob(os.path.join(SRC, "*.html")))
    for t in targets:
        src = t if t.endswith(".html") and os.path.exists(t) else os.path.join(SRC, t if t.endswith(".html") else t + ".html")
        print("✔", os.path.relpath(build(src), ROOT_DIR))
    print(f"{len(targets)} page(s) générée(s).")
