/* ═══════════════════════════════════════════════════════════
   ABI NEXUS — interactivity.js (S15)
   · Loadout Builder   → mount [data-widget="loadout-builder"]
   · Weapon Compare    → mount [data-widget="weapon-compare"]
   · Filtres de tier   → auto sur les pages tier list
   Données : js/data-weapons.json · js/data-armors.json
   ═══════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  const $ = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));
  const ROOT = document.body.dataset.root || "../";
  const fmt = (n) => Number(n).toLocaleString("fr-FR");

  let WEAPONS = [];
  let ARMORS = [];
  let HELMETS = [];

  const MODES = {
    normal: { label: "Normal", ammoCap: 4, armorCap: 4, valueCap: null },
    lockdown: { label: "Lockdown", ammoCap: 5, armorCap: 5, valueCap: 900000 },
    forbidden: { label: "Forbidden", ammoCap: 6, armorCap: 6, valueCap: null },
  };

  /* ════════════ LOADOUT BUILDER ════════════ */
  function buildLoadout(mount) {
    mount.innerHTML =
      '<h3 class="widget-title">⬢ Loadout Builder — test de cap</h3>' +
      '<div class="lb">' +
      '<div class="lb-select"><label for="lb-mode">Mode</label><select id="lb-mode">' +
      '<option value="normal">Normal (T4 max)</option>' +
      '<option value="lockdown">Lockdown (T5 max · 900k)</option>' +
      '<option value="forbidden">Forbidden (libre)</option>' +
      "</select></div>" +
      '<div class="lb-select"><label for="lb-weapon">Arme</label><select id="lb-weapon"></select></div>' +
      '<div class="lb-select"><label for="lb-armor">Armure</label><select id="lb-armor"></select></div>' +
      '<div class="lb-select"><label for="lb-helmet">Casque</label><select id="lb-helmet"></select></div>' +
      '<div class="lb-card" id="lb-card"></div>' +
      "</div>";

    const selWeapon = $("#lb-weapon", mount);
    const selArmor = $("#lb-armor", mount);
    const selHelmet = $("#lb-helmet", mount);
    const selMode = $("#lb-mode", mount);

    WEAPONS.slice()
      .sort((a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name))
      .forEach((w) => {
        const o = document.createElement("option");
        o.value = w.id;
        o.textContent = w.name + " (" + w.category.toUpperCase() + " · " + fmt(w.price_koen) + " K)";
        selWeapon.appendChild(o);
      });
    ARMORS.forEach((a) => {
      const o = document.createElement("option");
      o.value = a.id;
      o.textContent = a.name + " · T" + a.tier + " · " + fmt(a.price_koen) + " K";
      selArmor.appendChild(o);
    });
    HELMETS.forEach((h) => {
      const o = document.createElement("option");
      o.value = h.id;
      o.textContent = h.name + " · T" + h.tier + " · " + fmt(h.price_koen) + " K";
      selHelmet.appendChild(o);
    });

    const bar = (label, val, max, suffix) =>
      '<div class="lb-stat"><div class="lb-stat-name">' +
      label +
      '</div><div class="lb-bar"><i style="width:' +
      Math.max(4, Math.min(100, Math.round((val / max) * 100))) +
      '%"></i></div><div class="lb-stat-val">' +
      val +
      (suffix || "") +
      "</div></div>";

    function render() {
      const mode = MODES[selMode.value];
      const w = WEAPONS.find((x) => x.id === selWeapon.value) || WEAPONS[0];
      const ar = ARMORS.find((x) => x.id === selArmor.value) || ARMORS[0];
      const he = HELMETS.find((x) => x.id === selHelmet.value) || HELMETS[0];
      const total = w.price_koen + ar.price_koen + he.price_koen;

      // Verdict caps S7
      let cls = "", msg = "";
      if (ar.tier > mode.armorCap || he.tier > mode.armorCap) {
        cls = "bad";
        msg =
          "⛔ Cap violé — armure/casque T" +
          Math.max(ar.tier, he.tier) +
          " > T" +
          mode.armorCap +
          " autorisé en " +
          mode.label +
          ".";
      } else if (mode.valueCap && total > mode.valueCap) {
        cls = "bad";
        msg =
          "⛔ Valeur " +
          fmt(total) +
          " K > plafond " +
          fmt(mode.valueCap) +
          " K de " +
          mode.label +
          ".";
      } else if (ar.tier < mode.armorCap - 1 || he.tier < mode.armorCap - 1) {
        cls = "warn";
        msg =
          "⚠ Sous-optimal — T" +
          ar.tier +
          " en " +
          mode.label +
          " (cap T" +
          mode.armorCap +
          ") : tu paies la protection avec du skill.";
      } else {
        cls = "";
        msg =
          "✅ Kit conforme — " +
          mode.label +
          " · cap T" +
          mode.armorCap +
          (mode.valueCap ? " · " + fmt(mode.valueCap) + " K max" : "") +
          " respecté.";
      }

      $("#lb-card", mount).innerHTML =
        '<div class="lb-verdict ' +
        cls +
        '"><span>' +
        msg +
        '</span><span class="lb-total">' +
        fmt(total) +
        " K · kit partiel</span></div>" +
        bar("Cadence (rpm)", w.rpm, 1100) +
        bar("Vélocité (m/s)", w.velocity, 1000) +
        bar("Recul V (plus bas = mieux)", 100 - w.recoil_v, 100) +
        bar("Ergonomie", w.ergo, 100) +
        bar("Portée (m)", w.range, 100) +
        '<div class="lb-stat"><div class="lb-stat-name">Tier méta</div><div class="lb-stat-val" style="color:var(--color-gold,#C8A84B)">' +
        w.meta_tier +
        " · " +
        (w.role || w.category) +
        '</div></div>' +
        '<div class="lb-stat"><div class="lb-stat-name">Meilleure munition</div><div class="lb-stat-val">' +
        (w.best_ammo || "—") +
        "</div></div>";
    }

    [selWeapon, selArmor, selHelmet, selMode].forEach((s) =>
      s.addEventListener("change", render)
    );
    render();
  }

  /* ════════════ WEAPON COMPARE ════════════ */
  function buildCompare(mount) {
    mount.innerHTML =
      '<h3 class="widget-title">⚔ Comparateur d\'armes — duel de stats</h3>' +
      '<div class="wc">' +
      '<div class="wc-picks">' +
      '<div class="lb-select"><label for="wc-a">Arme A</label><select id="wc-a"></select></div>' +
      '<div class="wc-vs">VS</div>' +
      '<div class="lb-select"><label for="wc-b">Arme B</label><select id="wc-b"></select></div>' +
      "</div>" +
      '<div class="wc-names"><span id="wc-na"></span><span></span><span id="wc-nb"></span></div>' +
      '<div class="wc-table" id="wc-table"></div>' +
      "</div>";

    const selA = $("#wc-a", mount);
    const selB = $("#wc-b", mount);
    const sorted = WEAPONS.slice().sort((a, b) => a.name.localeCompare(b.name));
    sorted.forEach((w) => {
      const o1 = document.createElement("option");
      o1.value = w.id;
      o1.textContent = w.name;
      selA.appendChild(o1);
      const o2 = o1.cloneNode(true);
      selB.appendChild(o2);
    });
    // Défauts parlants
    const a545 = WEAPONS.find((w) => w.id === "a545");
    const ak15 = WEAPONS.find((w) => w.id === "ak15sc") || WEAPONS[1];
    if (a545) selA.value = a545.id;
    if (ak15) selB.value = ak15.id;

    const ROWS = [
      { key: "rpm", label: "Cadence (rpm)", max: 1100, better: "high" },
      { key: "velocity", label: "Vélocité (m/s)", max: 1000, better: "high" },
      { key: "recoil_v", label: "Recul vertical", max: 100, better: "low" },
      { key: "recoil_h", label: "Recul horizontal", max: 100, better: "low" },
      { key: "ergo", label: "Ergonomie", max: 100, better: "high" },
      { key: "range", label: "Portée (m)", max: 100, better: "high" },
      { key: "price_koen", label: "Prix (Koen)", max: 500000, better: "low" },
    ];

    function render() {
      const A = WEAPONS.find((w) => w.id === selA.value) || WEAPONS[0];
      const B = WEAPONS.find((w) => w.id === selB.value) || WEAPONS[1];
      $("#wc-na", mount).textContent = A.name;
      $("#wc-nb", mount).textContent = B.name;

      const rows = ROWS.map((r) => {
        const va = A[r.key] || 0;
        const vb = B[r.key] || 0;
        let aWin = false, bWin = false;
        if (va !== vb) {
          if (r.better === "high") { aWin = va > vb; bWin = vb > va; }
          else { aWin = va < vb; bWin = vb < va; }
        }
        const pa = Math.max(3, Math.min(100, Math.round((va / r.max) * 100)));
        const pb = Math.max(3, Math.min(100, Math.round((vb / r.max) * 100)));
        const show = (v) => (r.key === "price_koen" ? fmt(v) : v);
        return (
          '<div class="wc-row">' +
          '<div class="wc-cell"><span class="wc-num' + (aWin ? " win" : "") + '">' + show(va) + "</span>" +
          '<div class="wc-mini"><i style="width:' + pa + '%"></i></div></div>' +
          '<div class="wc-label">' + r.label + "</div>" +
          '<div class="wc-cell right"><span class="wc-num' + (bWin ? " win" : "") + '">' + show(vb) + "</span>" +
          '<div class="wc-mini"><i style="width:' + pb + '%"></i></div></div>' +
          "</div>"
        );
      }).join("");

      // Verdict synthétique (tier méta + role)
      const tierOrder = { S: 4, A: 3, B: 2, C: 1, D: 0 };
      const ta = tierOrder[A.meta_tier] || 0;
      const tb = tierOrder[B.meta_tier] || 0;
      let verdict;
      if (ta === tb) verdict = "Égalité de tier — le scénario tranche (carte, mode, rôle).";
      else verdict = "Avantage global : <b>" + (ta > tb ? A.name : B.name) + "</b> (tier " + (ta > tb ? A.meta_tier : B.meta_tier) + " vs " + (ta > tb ? B.meta_tier : A.meta_tier) + ").";

      $("#wc-table", mount).innerHTML = rows +
        '<div class="lb-verdict"><span>' + verdict + "</span></div>";
    }

    [selA, selB].forEach((s) => s.addEventListener("change", render));
    render();
  }

  /* ════════════ FILTRES DE TIER ════════════ */
  function initTierFilters() {
    const page = decodeURIComponent(location.pathname.split("/").pop() || "");
    const ALLOWED = ["armes-tier-list.html", "equipement-tier-list.html", "meta-tier-list-globale.html"];
    if (!ALLOWED.includes(page)) return;

    $$("table.data-table").forEach((table) => {
      if (!$(".tier-badge", table)) return;
      // Ne pas doubler si déjà filtré
      if (table.previousElementSibling && table.previousElementSibling.classList.contains("tier-filter")) return;

      const tiers = new Set();
      $$(".tier-badge", table).forEach((b) => {
        const m = (b.className.match(/tier-([scab])/) || [])[1];
        if (m) tiers.add(m.toUpperCase());
      });
      if (tiers.size < 2) return;

      const bar = document.createElement("div");
      bar.className = "tier-filter";
      bar.innerHTML =
        '<button class="active" data-t="all">Tous</button>' +
        Array.from(tiers)
          .sort()
          .map((t) => '<button data-t="' + t.toLowerCase() + '">' + t + "</button>")
          .join("");
      table.parentNode.insertBefore(bar, table);

      bar.addEventListener("click", (e) => {
        const btn = e.target.closest("button");
        if (!btn) return;
        $$("button", bar).forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        if (window.ABINexus && ABINexus.sfx) ABINexus.sfx.play("sfx-weapon-equip");
        const t = btn.dataset.t;
        $$("tbody tr", table).forEach((tr) => {
          if (t === "all") { tr.classList.remove("row-hidden"); return; }
          const has = !!$(".tier-badge.tier-" + t, tr);
          tr.classList.toggle("row-hidden", !has);
        });
      });
    });
  }

  /* ════════════ STK / TTK CALCULATOR (S19) ════════════
     Modèle communautaire (abi-helper / qrts / abibuilder) :
     pierce = floor(pen/10) · >classe → 100% dmg plein
     ==classe → 80–100% (dmg×0.8) · <classe → 1/2^x (dmg×0.6)
     S7 : armure corps T5/T6, sous-tier = 0% tant que durabilité > seuil (~50%, non publié)
  ══════════════════════════════════════════════════════ */
  let ROUNDS = [];

  function penChance(pen, cls, dur) {
    const pierce = Math.floor(pen / 10);
    let chance, mult;
    if (pierce > cls) {
      chance = 100;
      mult = 1;
    } else if (pierce === cls) {
      chance = Math.min(100, 80 + (pen - cls * 10) * 2.22);
      mult = 0.8;
    } else {
      const x = (cls * 10 + 5 - pen) / 10;
      chance = 100 / Math.pow(2, x);
      mult = 0.6;
    }
    // Règle S7 : corps T5/T6 — pas de pén' sous-tier neuve (seuil approximatif 50%)
    if (cls >= 5 && pierce < cls && dur > 50) chance = 0;
    // Durabilité usée = plus facile à percer
    if (chance > 0 && chance < 100) chance = Math.min(100, chance + (100 - dur) * 0.15);
    return { chance, mult };
  }

  function buildStk(mount) {
    mount.innerHTML =
      '<h3 class="widget-title">⬢ Calculateur STK / TTK — munition vs armure</h3>' +
      '<div class="stk">' +
      '<div class="stk-select"><label for="stk-weapon">Arme (cadence)</label><select id="stk-weapon"></select></div>' +
      '<div class="stk-select"><label for="stk-ammo">Munition</label><select id="stk-ammo"></select></div>' +
      '<div class="stk-select"><label for="stk-class">Classe armure (torse)</label><select id="stk-class">' +
      [1, 2, 3, 4, 5, 6].map((c) => '<option value="' + c + '"' + (c === 4 ? " selected" : "") + ">T" + c + "</option>").join("") +
      "</select></div>" +
      '<div class="stk-select"><label for="stk-dur">Durabilité <span id="stk-dur-v">100%</span></label>' +
      '<input type="range" id="stk-dur" min="0" max="100" value="100" step="5"></div>' +
      '<div class="stk-cards" id="stk-cards"></div>' +
      '<p class="stk-note">Modèle communautaire (pierce = pen÷10) : égalité → 80–100% &amp; dégâts ×0.8 · dessous → 1/2<sup>x</sup> &amp; dégâts ×0.6 · règle S7 : sous-tier = 0% sur corps T5/T6 tant que durabilité &gt;~50% (seuil non publié). Poitrine 85 PV · dégâts contondants non modélisés.</p>' +
      "</div>";

    const ws = $("#stk-weapon", mount),
      as = $("#stk-ammo", mount),
      cs = $("#stk-class", mount),
      ds = $("#stk-dur", mount),
      dv = $("#stk-dur-v", mount),
      cards = $("#stk-cards", mount);

    ws.innerHTML = WEAPONS.slice()
      .sort((a, b) => a.name.localeCompare(b.name))
      .map((w) => '<option value="' + w.id + '">' + w.name + " · " + w.caliber + " · " + w.rpm + " rpm</option>")
      .join("");

    function fillAmmo() {
      const w = WEAPONS.find((x) => x.id === ws.value) || WEAPONS[0];
      let list = ROUNDS.filter((r) => r.caliber === w.caliber);
      if (!list.length) list = ROUNDS; // calibre sans data → toutes les munitions
      as.innerHTML = list
        .map((r) => '<option value="' + r.name + '">' + r.name + " · pen " + r.pen + " · chair " + r.flesh + "</option>")
        .join("");
      calc();
    }

    function calc() {
      const w = WEAPONS.find((x) => x.id === ws.value) || WEAPONS[0];
      const r = ROUNDS.find((x) => x.name === as.value) || ROUNDS[0];
      if (!w || !r) return;
      const cls = +cs.value,
        dur = +ds.value;
      dv.textContent = dur + "%";
      const { chance, mult } = penChance(r.pen, cls, dur);
      const dmg = Math.round(r.flesh * mult);
      const stk = dmg > 0 ? Math.ceil(85 / dmg) : "—";
      const ttk = typeof stk === "number" && stk > 0 ? (((stk - 1) * 60) / w.rpm).toFixed(2) : "—";
      const verdict =
        chance >= 99.5
          ? '<span class="tier-badge tier-s">PÉNÉTRATION GARANTIE</span>'
          : chance >= 50
          ? '<span class="tier-badge tier-a">Pén' + chance.toFixed(0) + "%</span>"
          : chance > 0
          ? '<span class="tier-badge tier-b">Pén ' + chance.toFixed(0) + "%</span>"
          : '<span class="tier-badge tier-d">0% — pénètre après usure</span>';
      cards.innerHTML =
        '<div class="stk-card"><span class="stk-k">Chance de pénétration</span><span class="stk-v">' + chance.toFixed(0) + "%</span>" + verdict + "</div>" +
        '<div class="stk-card"><span class="stk-k">Dégâts / coup (torse)</span><span class="stk-v">' + dmg + "</span><span class=\"stk-sub\">base " + r.flesh + " × " + mult.toFixed(1) + "</span></div>" +
        '<div class="stk-card"><span class="stk-k">STK (85 PV)</span><span class="stk-v">' + stk + " coup" + (stk > 1 ? "s" : "") + "</span><span class=\"stk-sub\">torse, tous coups pénétrants</span></div>" +
        '<div class="stk-card"><span class="stk-k">TTK estimé</span><span class="stk-v">' + ttk + " s</span><span class=\"stk-sub\">" + w.rpm + " rpm · hors rechargement</span></div>";
    }

    ws.addEventListener("change", fillAmmo);
    [as, cs, ds].forEach((el) => el.addEventListener("input", calc));
    fillAmmo();
  }

  /* ════════════ BOOT ════════════ */
  function boot() {
    Promise.all([
      fetch(ROOT + "js/data-weapons.json").then((r) => r.json()),
      fetch(ROOT + "js/data-armors.json").then((r) => r.json()),
      fetch(ROOT + "js/data-ballistics.json")
        .then((r) => r.json())
        .catch(() => ({ rounds: [] })),
    ])
      .then(([w, a, b]) => {
        WEAPONS = w.weapons || [];
        ARMORS = a.armors || [];
        HELMETS = a.helmets || [];
        ROUNDS = b.rounds || [];

        const lb = $('[data-widget="loadout-builder"]');
        if (lb) buildLoadout(lb);
        const wc = $('[data-widget="weapon-compare"]');
        if (wc) buildCompare(wc);
        const stk = $('[data-widget="stk-calc"]');
        if (stk) buildStk(stk);
        initTierFilters();
      })
      .catch(() => {
        // Repli : filtres même sans données
        initTierFilters();
      });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
