/* ═══════════════════════════════════════════════════════════
   ABI NEXUS — search.js (S15)
   Recherche globale instantanée (Ctrl+K / "/" / bouton).
   Index : js/data-search-index.json (généré par tools/gen_search_index.py)
   API exposée : ABINexusSearch.query(q) · ABINexusSearch.gotoFirst()
   ═══════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  const ROOT = (document.body.dataset.root || "") + "pages/";
  const INDEX_URL = (document.body.dataset.root || "") + "js/data-search-index.json";

  let INDEX = [];
  let current = [];          // résultats courants (objets)
  let firstHref = null;

  const norm = (s) =>
    (s || "")
      .toString()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, ""); // retire les accents

  function score(item, terms) {
    const fields = [
      [norm(item.title), 6],
      [norm(item.kw), 4],
      [norm(item.sections), 2],
      [norm(item.h), 3],
      [norm(item.desc), 1],
      [norm(item.cat), 3],
    ];
    let total = 0;
    for (const t of terms) {
      let best = 0;
      for (const [text, w] of fields) {
        if (!text) continue;
        if (text === t) best = Math.max(best, w * 3);
        else if (text.startsWith(t)) best = Math.max(best, w * 2);
        else if (text.includes(t)) best = Math.max(best, w);
      }
      if (!best) return 0; // tous les termes doivent matcher
      total += best;
    }
    return total;
  }

  function highlight(text, terms) {
    if (!text) return "";
    let out = text.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
    for (const t of terms) {
      if (t.length < 2) continue;
      const re = new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
      out = out.replace(re, "<mark>$1</mark>");
    }
    return out;
  }

  function render(results, terms, q) {
    const box = document.querySelector(".search-results");
    const modal = document.querySelector(".search-modal");
    if (!box) return;
    current = results;
    firstHref = results.length ? results[0].href : null;

    if (!q) {
      box.innerHTML =
        '<div class="search-empty">Tape ta requête — résultats instantanés sur les armes, armures, cartes et guides.</div>';
      return;
    }
    if (!results.length) {
      box.innerHTML =
        '<div class="search-empty">Aucun résultat pour « ' +
        q.replace(/[&<>]/g, "") +
        " » — essaie « A545 », « Valley », « extraction » ou « Warlord ».</div>";
      return;
    }
    const count = document.createElement("div");
    count.className = "search-count";
    count.textContent = results.length + " résultat" + (results.length > 1 ? "s" : "");
    const html = results
      .slice(0, 12)
      .map((r) => {
        const href = r.file.startsWith("../") ? r.file : ROOT + r.file;
        return (
          '<a class="sr-item" href="' +
          href +
          '"><span class="sr-tag">' +
          r.cat +
          '</span><span class="sr-title">' +
          highlight(r.title, terms) +
          '</span><span class="sr-meta">' +
          highlight(r.desc.slice(0, 110), terms) +
          "…</span></a>"
        );
      })
      .join("");
    box.innerHTML = "";
    box.appendChild(count);
    box.insertAdjacentHTML("beforeend", html);

    // Fermeture au clic sur un résultat
    box.querySelectorAll("a.sr-item").forEach((a) =>
      a.addEventListener("click", () => modal && modal.classList.remove("open"))
    );
  }

  function query(q) {
    q = (q || "").trim();
    const terms = norm(q).split(/\s+/).filter(Boolean);
    if (!terms.length) {
      render([], terms, "");
      return;
    }
    const scored = [];
    for (const item of INDEX) {
      const s = score(item, terms);
      if (s > 0) scored.push({ s, item });
    }
    scored.sort((a, b) => b.s - a.s);
    render(
      scored.map((x) => x.item),
      terms,
      q
    );
  }

  function gotoFirst() {
    if (firstHref) location.href = firstHref;
  }

  window.ABINexusSearch = { query, gotoFirst, get index() { return INDEX; } };

  // Prise en charge de ?q= (SearchAction JSON-LD)
  function bootFromQuery() {
    const q = new URLSearchParams(location.search).get("q");
    if (!q) return;
    const modal = document.querySelector(".search-modal");
    const input = modal && modal.querySelector("input");
    if (modal) modal.classList.add("open");
    if (input) {
      input.value = q;
      setTimeout(() => query(q), 120);
      setTimeout(() => input.focus(), 160);
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootFromQuery);
  } else {
    bootFromQuery();
  }

  // Chargement de l'index
  fetch(INDEX_URL)
    .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
    .then((data) => {
      INDEX = data;
    })
    .catch(() => {
      // Repli : index minimal embarqué (pages clés) si le fetch échoue
      INDEX = [
        { file: "guide-debutant.html", title: "Guide du débutant", desc: "Premières raids et survie", kw: "debutant eco", cat: "Guide", h: "", sections: "" },
        { file: "armes-tier-list.html", title: "Tier list armes", desc: "Classement des armes", kw: "tier meta s a b", cat: "Armes", h: "", sections: "" },
        { file: "map-farm.html", title: "Carte Farm", desc: "Exfils et hotspots", kw: "ferme ajax motel", cat: "Carte", h: "", sections: "" },
        { file: "saison7-utopia.html", title: "Saison 7 Utopia", desc: "Contenu complet du patch", kw: "s7 zombie", cat: "Saison 7", h: "", sections: "" },
      ];
    });
})();
