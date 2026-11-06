"""Render outputs/chart_previews.html: a preview of all 14 charts plus build notes for Flourish / Datawrapper.

Usage: python -I scripts/render_chart_previews.py
Reads only outputs/charts/*.csv, outputs/charts/chart_specs.md, outputs/findings.json and
scripts/assets/countries-110m.json (world-atlas 2.0.2, Natural Earth). Previews are approximations of the final
Flourish/Datawrapper charts; the CSVs are the files to upload.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd  # noqa: E402
import pycountry  # noqa: E402

from src import config  # noqa: E402

CH = config.CHARTS
ACTS = {1: "The promise", 2: "The reckoning", 3: "Who the game misjudged", 4: "What actually mattered", 5: "Where they are now"}
ACT_OF = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 2, 8: 3, 9: 3, 10: 3, 11: 3, 12: 4, 13: 4, 14: 5}


def specs():
    text = config.CHART_SPECS.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"<!-- BEGIN CHART (\d\d) -->(.*?)<!-- END CHART \1 -->", text, re.S):
        n, body = int(m.group(1)), m.group(2)
        d = {}
        for line in body.splitlines():
            mm = re.match(r"- ([^:]+?)(?: \([^)]*\))?: (.*)", line.strip())
            if mm:
                d[mm.group(1).strip()] = mm.group(2).strip()
        d["short"] = re.search(r"## Chart \d\d: (\S+)", body).group(1)
        out[n] = d
    return out


def data():
    out = {}
    for f in sorted(CH.glob("[0-9][0-9]_*.csv")):
        n = int(f.name[:2])
        df = pd.read_csv(f, keep_default_na=True)
        out[n] = {"file": f"outputs/charts/{f.name}", "columns": list(df.columns),
                  "rows": json.loads(df.to_json(orient="records", force_ascii=False))}
    return out


def main():
    F = json.loads(config.FINDINGS.read_text(encoding="utf-8"))
    S, D = specs(), data()
    iso_num = {}
    for r in D[8]["rows"]:
        c = pycountry.countries.get(alpha_3=r["ISO3"])
        if c:
            iso_num[r["ISO3"]] = c.numeric
    world = json.loads((ROOT / "scripts/assets/countries-110m.json").read_text())
    head = {
        "inflation": F["export_chart_02"]["multiple"], "wk_first": F["export_chart_02"]["wk_per_1000_first"],
        "wk_max": F["export_chart_02"]["wk_per_1000_max"], "wk_max_ed": F["export_chart_02"]["wk_per_1000_max_edition"],
        "per10": F["export_chart_04"]["points_per_10"], "first": F["export_chart_07"]["first"], "last": F["export_chart_07"]["last"],
        "auc_pot": round(F["export_chart_12"]["potential_auc"], 2), "auc_mkt": round(F["export_chart_12"]["market_auc"], 2),
        "wk15": F["export_chart_01"]["n"], "wk15_reached": F["export_chart_01"]["reached"], "wk15_made": F["export_chart_01"]["made_it"],
        "pending": F["provisional"]["match_review_pending_players"],
        "fit75": F["export_chart_04"]["line_at_75"], "fit95": F["export_chart_04"]["line_at_95"],
    }
    featured = [{"role": k, **v} for k, v in F["featured_five"]["picks"].items()]
    payload = {"specs": {str(k): v for k, v in S.items()}, "data": {str(k): v for k, v in D.items()}, "head": head,
               "featured": featured, "isoNum": iso_num, "world": world, "acts": ACTS, "actOf": ACT_OF,
               "palette": config.PALETTE, "sources": {k: v for k, v in config.SOURCES.items()}}
    html = TEMPLATE.replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"))
    out = ROOT / "outputs" / "chart_previews.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size / 1024:.0f} KB)")


TEMPLATE = r"""<title>Career Mode Chart Book</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: a match-programme chart book. Narrow reading column, each chart a "fixture" card with its build sheet beneath. */
:root {
  --bg: #f4f5f7; --surface: #ffffff; --ink: #1D2433; --ink-2: #4a5466; --muted: #7b8496; --rule: #dde1e8; --rule-2: #eceef2;
  --promise: #F2A900; --reality: #1B998B; --short: #D1495B; --beat: #2E86AB; --context: #C5CAD3; --neutral-mid: #eef0f3;
  --promise-ink: #7a5700; --chip-dw: #e7f0f5; --chip-fl: #f3ecfb;
  --display: "Saira Condensed", "Arial Narrow", "Roboto Condensed", sans-serif;
  --body: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0f131b; --surface: #161b26; --ink: #e8ebf1; --ink-2: #b4bbc8; --muted: #828b9b; --rule: #2a3140; --rule-2: #1f2531;
  --context: #5b6372; --neutral-mid: #252b37; --promise-ink: #f2c14e; --chip-dw: #16293a; --chip-fl: #2a2140; color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: #0f131b; --surface: #161b26; --ink: #e8ebf1; --ink-2: #b4bbc8; --muted: #828b9b; --rule: #2a3140; --rule-2: #1f2531;
  --context: #5b6372; --neutral-mid: #252b37; --promise-ink: #f2c14e; --chip-dw: #16293a; --chip-fl: #2a2140; color-scheme: dark }
* { box-sizing: border-box }
body { background: var(--bg); color: var(--ink); font: 15px/1.55 var(--body); margin: 0 }
.wrap { max-width: 1040px; margin: 0 auto; padding-block: 28px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)) }
header.mast { display: grid; gap: 14px; padding-block: 8px 24px; border-bottom: 3px solid var(--ink) }
.kicker { font: 600 12px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--muted) }
h1 { font: 800 clamp(40px, 7vw, 68px)/.95 var(--display); letter-spacing: -.01em; margin: 0; text-wrap: balance }
h1 em { font-style: normal; color: var(--promise-ink) }
.lede { font-size: 17px; max-width: 64ch; color: var(--ink-2); margin: 0 }
.notice { font: 500 13px/1.45 var(--body); color: var(--ink-2); border-left: 3px solid var(--promise); padding: 6px 12px; background: var(--surface); max-width: 80ch }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; margin-top: 20px }
.tile { background: var(--surface); border: 1px solid var(--rule); border-radius: 6px; padding: 14px 16px; display: grid; gap: 4px; min-width: 0 }
.tile .num { font: 700 34px/1 var(--display); font-variant-numeric: tabular-nums }
.tile .lab { font-size: 13px; color: var(--ink-2) }
nav.acts { display: flex; flex-wrap: wrap; gap: 8px 18px; margin: 22px 0 6px; font: 600 13px/1.2 var(--mono) }
nav.acts a { color: var(--ink-2); text-decoration: none; border-bottom: 1px solid var(--rule) }
nav.acts a:hover, nav.acts a:focus-visible { color: var(--ink); border-color: var(--ink); outline: none }
.legend-key { display: flex; flex-wrap: wrap; gap: 10px 18px; font-size: 13px; color: var(--ink-2); margin: 10px 0 0 }
.legend-key span { display: inline-flex; align-items: center; gap: 6px }
.sw { width: 12px; height: 12px; border-radius: 3px; display: inline-block; border: 1px solid var(--ink) }
section.act { margin-top: 44px }
.act-head { display: flex; align-items: baseline; gap: 12px; border-bottom: 1px solid var(--rule); padding-bottom: 6px; margin-bottom: 18px }
.act-head h2 { font: 700 30px/1 var(--display); margin: 0 }
.act-head .kicker { white-space: nowrap }
.players { display: grid; grid-template-columns: repeat(auto-fit, minmax(176px, 1fr)); gap: 10px; margin: 8px 0 18px }
.card { background: var(--surface); border: 1px solid var(--rule); border-top: 4px solid var(--promise); border-radius: 6px; padding: 10px 12px; display: grid; gap: 6px; min-width: 0 }
.card .role { font: 600 11px/1.2 var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted) }
.card .name { font: 700 20px/1.05 var(--display) }
.card .club { font-size: 12px; color: var(--ink-2) }
.ratings { display: flex; gap: 8px; align-items: stretch; font-variant-numeric: tabular-nums }
.rt { display: grid; justify-items: center; border: 1px solid var(--rule); border-radius: 4px; padding: 3px 7px; min-width: 44px }
.rt b { font: 700 20px/1 var(--display) }
.rt i { font: 500 10px/1.2 var(--mono); font-style: normal; color: var(--muted); letter-spacing: .06em }
.fig { background: var(--surface); border: 1px solid var(--rule); border-radius: 8px; padding: 18px 18px 14px; margin-bottom: 22px; display: grid; gap: 10px; min-width: 0 }
.fig-meta { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font: 500 12px/1 var(--mono); color: var(--muted) }
.chip { font: 600 11px/1 var(--mono); letter-spacing: .04em; padding: 5px 7px; border-radius: 4px; color: var(--ink) }
.chip.dw { background: var(--chip-dw) } .chip.fl { background: var(--chip-fl) }
.fig h3 { font: 700 24px/1.1 var(--display); margin: 0; text-wrap: balance; max-width: 34ch }
.fig .sub { margin: 0; color: var(--ink-2); font-size: 14px; max-width: 80ch }
.plot { width: 100%; min-height: 360px }
.plot.tall { min-height: 520px } .plot.short { min-height: 200px }
.controls { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-size: 13px; color: var(--ink-2) }
select, input[type=search] { font: 14px var(--body); color: var(--ink); background: var(--bg); border: 1px solid var(--rule); border-radius: 5px; padding: 6px 8px; min-width: 0 }
select:focus-visible, input:focus-visible { outline: 2px solid var(--beat); outline-offset: 1px }
.build { border-top: 1px dashed var(--rule); padding-top: 10px; display: grid; grid-template-columns: 150px 1fr; gap: 6px 14px; font-size: 13px }
.build dt { font: 600 11px/1.6 var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted) }
.build dd { margin: 0; color: var(--ink-2); min-width: 0; overflow-wrap: anywhere }
.build code { font: 12px/1.5 var(--mono); background: var(--bg); border: 1px solid var(--rule-2); border-radius: 4px; padding: 1px 5px; color: var(--ink) }
.build a { color: var(--ink) }
details.data { font-size: 13px } details.data summary { cursor: pointer; color: var(--ink-2); font: 500 12px var(--mono) }
.tbl { overflow: auto; max-height: 420px; border: 1px solid var(--rule); border-radius: 6px }
table { border-collapse: collapse; width: 100%; font-size: 13px; font-variant-numeric: tabular-nums }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--rule-2); white-space: nowrap }
th { position: sticky; top: 0; background: var(--surface); font: 600 11px/1.3 var(--mono); color: var(--muted); letter-spacing: .03em; z-index: 1 }
td.num { text-align: right }
tr.feat td { background: color-mix(in srgb, var(--promise) 16%, transparent) }
.st { font-weight: 600 } .st.Reached { color: var(--reality) } .st.Fell { color: var(--short) } .st.Vanished { color: var(--muted) }
.gapbar { display: inline-block; height: 8px; border-radius: 0 4px 4px 0; background: var(--short); vertical-align: middle; margin-left: 6px }
.map-wrap { display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 1fr); gap: 16px; align-items: start }
.map-lists { display: grid; gap: 12px; font-size: 13px }
.map-lists h4 { font: 600 11px/1.3 var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); margin: 0 0 4px }
.map-lists ol { margin: 0; padding-left: 18px; color: var(--ink-2) }
#map svg { width: 100%; height: auto; display: block }
.maplegend { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--ink-2); margin-top: 6px; flex-wrap: wrap }
.maplegend .bar { height: 10px; width: 200px; max-width: 50vw; border-radius: 3px; border: 1px solid var(--rule) }
.tip { position: fixed; pointer-events: none; background: var(--surface); color: var(--ink); border: 1px solid var(--rule); border-radius: 6px; padding: 8px 10px; font-size: 12px; line-height: 1.45; box-shadow: 0 4px 16px rgb(0 0 0 / .15); max-width: 260px; z-index: 20 }
footer { margin-top: 40px; font-size: 12px; color: var(--muted); border-top: 1px solid var(--rule); padding-top: 12px }
@media (max-width: 720px) { .build { grid-template-columns: 1fr } .build dt { margin-top: 6px } .map-wrap { grid-template-columns: 1fr } }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important } }
</style>

<div class="wrap">
  <header class="mast">
    <div class="kicker">IE6600 Project 1 · Chart book · previews for Flourish &amp; Datawrapper</div>
    <h1>The Career Mode <em>Promise</em></h1>
    <p class="lede" id="lede"></p>
    <div class="notice" id="notice"></div>
    <div class="tiles" id="tiles"></div>
    <div class="legend-key" aria-label="Colour key">
      <span><i class="sw" style="background:var(--promise)"></i>The game's promise (potential) · featured players</span>
      <span><i class="sw" style="background:var(--reality)"></i>Reality (actual outcome)</span>
      <span><i class="sw" style="background:var(--short)"></i>Fell short / overrated</span>
      <span><i class="sw" style="background:var(--beat)"></i>Beat potential / underrated</span>
      <span><i class="sw" style="background:var(--context)"></i>Context</span>
    </div>
  </header>
  <nav class="acts" id="nav" aria-label="Acts"></nav>
  <main id="main"></main>
  <footer id="foot"></footer>
</div>
<div class="tip" id="tip" hidden></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.27.0/plotly.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"></script>
<script>
const P = __PAYLOAD__;
const $ = (s, el = document) => el.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]));
const tok = n => getComputedStyle(document.documentElement).getPropertyValue("--" + n).trim();
const rows = n => P.data[n].rows;
const spec = n => P.specs[n];
const H = P.head;

// ---------------------------------------------------------------- header
$("#lede").textContent = `EA rated every young player's "potential". We followed ${H.wk15} FIFA 15 wonderkids and 11,519 young entrants to FC 24 and into real careers. The verdict: an inflated promise, but a useful ranking.`;
$("#notice").textContent = `Previews only: build the real charts in Flourish and Datawrapper from the CSVs named under each chart. Numbers are provisional until the Transfermarkt match review (${H.pending} players pending) and the club-override check are done; re-run notebooks 02 → 12 and this page afterwards.`;
const tiles = [
  [`${H.inflation}×`, `more wonderkid ratings per 1,000 under-21s, FIFA 15 → ${H.wk_max_ed} (${H.wk_first} → ${H.wk_max})`],
  [`${H.per10}`, "points of real rating delivered per 10 points of promised potential"],
  [`${H.first}% → ${H.last}%`, "reached their potential within four editions, FIFA 15 vs FIFA 20 entrants"],
  [`${H.auc_pot} vs ${H.auc_mkt}`, "AUC: EA potential vs transfer-market value at predicting who made it"],
];
$("#tiles").innerHTML = tiles.map(([n, l]) => `<div class="tile"><span class="num">${esc(n)}</span><span class="lab">${esc(l)}</span></div>`).join("");
$("#nav").innerHTML = Object.entries(P.acts).map(([k, v]) => `<a href="#act-${k}">Act ${k} · ${esc(v)}</a>`).join("");

// ---------------------------------------------------------------- sections
const TALL = new Set([4, 6, 10, 14]);
function buildSheet(n) {
  const s = spec(n), file = P.data[n].file;
  const rowsHtml = [
    ["Template", esc(s["Tool / template"])], ["Upload", `<code>${esc(file)}</code>`],
    ["Columns", esc(s["Column → role mapping"])], ["Colours", esc(s["Colours"])],
    ["Tooltip", `<code>${esc(s["Tooltip"])}</code>`], ["Source line", s["Source line"].replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, t, u) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(t)}</a>`)],
    ["Notes", esc(s["Notes for the builder"])],
  ];
  return `<dl class="build">${rowsHtml.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join("")}</dl>`;
}
function dataTable(n, limit = 400) {
  const d = P.data[n], cols = d.columns;
  const body = d.rows.slice(0, limit).map(r => `<tr>${cols.map(c => `<td class="${typeof r[c] === "number" ? "num" : ""}">${esc(r[c] ?? "")}</td>`).join("")}</tr>`).join("");
  return `<details class="data"><summary>Data table (${d.rows.length.toLocaleString()} rows${d.rows.length > limit ? `, first ${limit} shown` : ""})</summary><div class="tbl"><table><thead><tr>${cols.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>${body}</tbody></table></div></details>`;
}
const main = $("#main");
for (const [act, name] of Object.entries(P.acts)) {
  const sec = document.createElement("section");
  sec.className = "act"; sec.id = `act-${act}`;
  sec.innerHTML = `<div class="act-head"><span class="kicker">Act ${act}</span><h2>${esc(name)}</h2></div>`;
  if (act === "1") {
    sec.innerHTML += `<div class="players">${P.featured.map(f => `<div class="card"><span class="role">${esc(f.role)}</span><span class="name">${esc(f.player)}</span><span class="club">${esc(f.club_2014)} (2014) → ${esc(f.latest_club ?? "—")}</span><div class="ratings"><span class="rt"><b>${f.potential}</b><i>POT</i></span><span class="rt"><b>${f.peak_later}</b><i>PEAK</i></span><span class="rt"><b>${f.peak_market_value_eur_m ?? "—"}</b><i>€M PEAK</i></span></div></div>`).join("")}</div>`;
  }
  for (const n of Object.keys(P.actOf).map(Number).filter(n => String(P.actOf[n]) === act)) {
    const s = spec(n), tool = s["Tool / template"].startsWith("Datawrapper") ? ["dw", "Datawrapper"] : ["fl", "Flourish"];
    const fig = document.createElement("article");
    fig.className = "fig"; fig.id = `chart-${String(n).padStart(2, "0")}`;
    let body = `<div class="plot${TALL.has(n) ? " tall" : ""}" id="p${n}" role="img" aria-label="${esc(s["Title"])}"></div>`;
    if (n === 1) body = `<div class="controls"><label for="q1">Search players</label><input type="search" id="q1" placeholder="e.g. Pogba, Ajax, France"></div><div class="tbl" id="t1"></div>`;
    if (n === 8) body = `<div class="map-wrap"><div><div id="map" role="img" aria-label="${esc(s["Title"])}"></div><div class="maplegend" id="maplegend"></div></div><div class="map-lists" id="maplists"></div></div>`;
    if (n === 9) body = `<div class="plot" id="p9"></div><div class="plot short" id="p9b"></div>`;
    if (n === 13) body = `<div class="controls"><label for="pick13">Player</label><select id="pick13"></select></div>` + body;
    fig.innerHTML = `<div class="fig-meta"><span>Chart ${String(n).padStart(2, "0")}</span><span class="chip ${tool[0]}">${tool[1]}</span><span>${esc(s["short"])}</span></div>
      <h3>${esc(s["Title"])}</h3><p class="sub">${esc(s["Subtitle"])}</p>${body}${n === 1 ? "" : dataTable(n)}${buildSheet(n)}`;
    sec.appendChild(fig);
  }
  main.appendChild(sec);
}
$("#foot").innerHTML = "Sources: " + Object.values(P.sources).map(([t, u]) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(t)}</a>`).join(" · ") + ". Generated by <code>scripts/render_chart_previews.py</code> from the chart CSVs, <code>chart_specs.md</code> and <code>findings.json</code>.";

// ---------------------------------------------------------------- plot helpers
const CFG = { displayModeBar: false, responsive: true };
function base(extra = {}) {
  const ink2 = tok("ink-2"), rule = tok("rule");
  const ax = { gridcolor: tok("rule-2"), zerolinecolor: rule, linecolor: rule, tickfont: { color: ink2, size: 12 }, title: { font: { color: ink2, size: 12 } }, automargin: true };
  return Object.assign({
    paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)", margin: { l: 56, r: 24, t: 16, b: 48 },
    font: { family: "IBM Plex Sans, system-ui, sans-serif", color: ink2, size: 12 },
    hoverlabel: { bgcolor: tok("surface"), bordercolor: rule, font: { color: tok("ink"), family: "IBM Plex Sans, system-ui, sans-serif" } },
    legend: { orientation: "h", y: -0.18, font: { color: ink2 } }, xaxis: { ...ax }, yaxis: { ...ax },
  }, extra, { xaxis: { ...ax, ...(extra.xaxis || {}) }, yaxis: { ...ax, ...(extra.yaxis || {}) } });
}
const hexA = (hex, a) => { const h = hex.replace("#", ""); const n = parseInt(h.length === 3 ? h.split("").map(c => c + c).join("") : h, 16); return `rgba(${n >> 16 & 255},${n >> 8 & 255},${n & 255},${a})`; };
function jitter(i, k) { const x = Math.sin(i * 12.9898 + k * 78.233) * 43758.5453; return (x - Math.floor(x) - 0.5) * 0.55; }

// ---------------------------------------------------------------- charts
const R = {};
R[1] = () => {
  const cols = ["Player", "Club (2014)", "Nation", "Age", "Overall", "Potential", "Peak later rating", "Gap", "Status", "Made it (3,000+ Big-5 min)", "Peak market value (€m)", "Latest club"];
  const draw = q => {
    const t = q.trim().toLowerCase();
    const rs = rows(1).filter(r => !t || cols.some(c => String(r[c] ?? "").toLowerCase().includes(t)));
    $("#t1").innerHTML = `<table><thead><tr>${cols.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>${rs.map(r => `<tr class="${r.Featured === "Yes" ? "feat" : ""}">${cols.map(c => {
      const v = r[c];
      if (c === "Player") return `<td><b>${esc(v)}</b>${r.Featured === "Yes" ? " ★" : ""}</td>`;
      if (c === "Status") return `<td class="st ${esc(String(v).split(" ")[0])}">${esc(v)}</td>`;
      if (c === "Gap") return `<td class="num">${v ?? ""}${v > 0 ? `<span class="gapbar" style="width:${v * 4}px"></span>` : ""}</td>`;
      if (c.startsWith("Made it")) return `<td class="st ${v === "Yes" ? "Reached" : "Vanished"}">${esc(v)}</td>`;
      return `<td class="${typeof v === "number" ? "num" : ""}">${esc(v ?? "")}</td>`;
    }).join("")}</tr>`).join("")}</tbody></table>`;
  };
  draw(""); $("#q1").addEventListener("input", e => draw(e.target.value));
};
R[2] = () => {
  const r = rows(2), y = r.map(d => d["Wonderkids per 1,000 under-21s"]), mx = Math.max(...y);
  Plotly.react("p2", [{ type: "bar", x: r.map(d => d.Edition), y, marker: { color: r.map(d => d["Wonderkids per 1,000 under-21s"] === mx ? tok("promise") : hexA(tok("promise"), .55)), line: { color: tok("ink"), width: 1 } },
    customdata: r.map(d => [d["Wonderkids (under-21, potential 85+)"], d["Under-21s in game"], d["Average headroom (potential − overall)"]]),
    hovertemplate: "<b>%{x}</b><br>%{y} per 1,000 under-21s<br>%{customdata[0]} wonderkids of %{customdata[1]}<br>Average headroom %{customdata[2]} points<extra></extra>",
    text: r.map((d, i) => (i === 0 || d["Wonderkids per 1,000 under-21s"] === mx || i === r.length - 1) ? d["Wonderkids per 1,000 under-21s"] : ""), textposition: "outside", textfont: { color: tok("ink") }, cliponaxis: false }],
    base({ yaxis: { title: { text: "Wonderkids per 1,000 under-21s" }, rangemode: "tozero" }, bargap: .25, showlegend: false }), CFG);
};
R[3] = () => {
  const r = rows(3), cols = P.data[3].columns.slice(1), dashes = ["solid", "dash", "dot", "dashdot", "longdash"];
  const traces = cols.map((c, i) => {
    const med = c.includes("median");
    return { type: "scatter", mode: "lines+markers", name: c, x: r.map(d => d.Edition), y: r.map(d => d[c]), connectgaps: false,
      line: { color: med ? tok("context") : tok("promise"), width: med ? 2 : 2.5, dash: med ? "dash" : dashes[i % 5] },
      marker: { size: med ? 5 : 7, color: med ? tok("context") : tok("promise"), line: { color: tok("ink"), width: med ? 0 : 1 } },
      hovertemplate: `<b>${c}</b> · %{x}<br>Overall %{y}<extra></extra>` };
  });
  const ann = cols.map(c => { let i = r.length - 1; while (i >= 0 && r[i][c] == null) i--; return { x: r[i].Edition, y: r[i][c], text: c, xanchor: "left", xshift: 8, showarrow: false, font: { color: tok("ink"), size: 12 } }; });
  Plotly.react("p3", traces, base({ yaxis: { title: { text: "Overall rating" }, range: [60, 93] }, margin: { l: 56, r: 150, t: 16, b: 60 }, annotations: ann }), CFG);
};
R[4] = () => {
  const r = rows(4);
  const mk = (st, color, op) => { const d = r.filter(x => x.Status === st && x.Featured !== "Yes"); return { type: "scatter", mode: "markers", name: st,
    x: d.map((x, i) => x.Potential + jitter(i, 1)), y: d.map((x, i) => x["Peak later rating"] + jitter(i, 2)), marker: { color: hexA(color, op), size: 5 },
    customdata: d.map(x => [x.Player, x["Entry edition"], x["Position group"], x.Club, x.Nation, x.Potential, x["Peak later rating"]]),
    hovertemplate: "<b>%{customdata[0]}</b> (%{customdata[1]}, %{customdata[2]})<br>Potential %{customdata[5]} → best later %{customdata[6]}<br>%{customdata[3]} · %{customdata[4]}<extra></extra>" }; };
  const fe = r.filter(x => x.Featured === "Yes");
  const traces = [mk("Fell short", tok("short"), .32), mk("Reached", tok("reality"), .45),
    { type: "scatter", mode: "markers+text", name: "Featured", x: fe.map(x => x.Potential), y: fe.map(x => x["Peak later rating"]), text: fe.map(x => x.Player), textposition: "top center", textfont: { color: tok("ink"), size: 12 },
      marker: { color: tok("promise"), size: 11, line: { color: tok("ink"), width: 1.5 } }, hovertemplate: "<b>%{text}</b><br>Potential %{x} → best later %{y}<extra></extra>" },
    { type: "scatter", mode: "lines", name: "Promise met (y = x)", x: [75, 95], y: [75, 95], line: { color: tok("ink"), dash: "dash", width: 1.5 }, hoverinfo: "skip" },
    { type: "scatter", mode: "lines", name: "What potential delivered (fit)", x: [75, 95], y: [H.fit75, H.fit95], line: { color: tok("reality"), width: 2.5 }, hoverinfo: "skip" }];
  Plotly.react("p4", traces, base({ xaxis: { title: { text: "Potential at entry" }, range: [74, 96] }, yaxis: { title: { text: "Best later overall rating" }, range: [50, 96] } }), CFG);
};
R[5] = () => {
  const r = rows(5).slice().reverse(), y = r.map(d => "Potential " + d["Potential band"]);
  const a = r.map(d => d["Reached potential in the game (%)"]), b = r.map(d => d["Made it in real life (%)"]);
  const ann = r.map((d, i) => ({ x: b[i], y: y[i], ax: a[i], ay: y[i], xref: "x", yref: "y", axref: "x", ayref: "y", showarrow: true, arrowhead: 2, arrowsize: 1.2, arrowwidth: 2, arrowcolor: b[i] >= a[i] ? tok("reality") : tok("short"), text: "" }));
  const cd = r.map(d => [d.Players, d["Fell short in the game (%)"], d["Vanished from the game (%)"]]);
  Plotly.react("p5", [
    { type: "scatter", mode: "markers+text", name: "Reached potential in the game", x: a, y, text: a.map(v => v + "%"), textposition: a.map((v, i) => v > b[i] ? "middle right" : "middle left"), textfont: { color: tok("ink") }, marker: { size: 13, color: tok("promise"), line: { color: tok("ink"), width: 1.5 } }, customdata: cd, hovertemplate: "<b>%{y}</b> (%{customdata[0]} players)<br>Reached in the game: %{x}%<br>Fell short %{customdata[1]}% · vanished %{customdata[2]}%<extra></extra>" },
    { type: "scatter", mode: "markers+text", name: "Made it in real life", x: b, y, text: b.map(v => v + "%"), textposition: b.map((v, i) => v >= a[i] ? "middle right" : "middle left"), textfont: { color: tok("ink") }, marker: { size: 13, color: tok("reality"), line: { color: tok("surface"), width: 2 } }, hovertemplate: "<b>%{y}</b><br>Made it in real life: %{x}%<extra></extra>" },
  ], base({ xaxis: { title: { text: "Share of the band (%)" }, range: [-4, 80], ticksuffix: "%" }, yaxis: { automargin: true }, annotations: ann, margin: { l: 120, r: 30, t: 10, b: 70 } }), CFG);
};
R[6] = () => {
  const r = rows(6), y = r.map(d => d.Player).reverse(), rr = r.slice().reverse();
  const lines = { type: "scatter", mode: "lines", x: rr.flatMap(d => [d["Potential at entry"], d["Peak later rating"], null]), y: rr.flatMap(d => [d.Player, d.Player, null]), line: { color: tok("context"), width: 3 }, hoverinfo: "skip", showlegend: false };
  Plotly.react("p6", [lines,
    { type: "scatter", mode: "markers", name: "Potential at entry", x: rr.map(d => d["Potential at entry"]), y, marker: { size: 11, color: tok("promise"), line: { color: tok("ink"), width: 1.5 } }, customdata: rr.map(d => [d["Entry edition"], d["Club at entry"], d.Gap]), hovertemplate: "<b>%{y}</b> · %{customdata[0]}, %{customdata[1]}<br>Potential %{x}<extra></extra>" },
    { type: "scatter", mode: "markers", name: "Peak later rating", x: rr.map(d => d["Peak later rating"]), y, marker: { size: 11, color: rr.map(d => d.Group === "Bust" ? tok("short") : tok("beat")), line: { color: tok("surface"), width: 2 } }, customdata: rr.map(d => [d.Gap]), hovertemplate: "<b>%{y}</b><br>Best later rating %{x} (gap %{customdata[0]})<extra></extra>" },
  ], base({ xaxis: { title: { text: "Rating" }, range: [50, 92] }, yaxis: { automargin: true, tickfont: { size: 11 } }, margin: { l: 170, r: 24, t: 10, b: 70 },
    shapes: [{ type: "line", xref: "paper", x0: 0, x1: 1, yref: "y", y0: 9.5, y1: 9.5, line: { color: tok("rule"), width: 1, dash: "dot" } }],
    annotations: [{ xref: "paper", x: 1, y: 19.4, yref: "y", text: "Busts (wonderkids)", showarrow: false, xanchor: "right", font: { color: tok("ink"), size: 12 } }, { xref: "paper", x: 1, y: 9.1, yref: "y", text: "Bloomers (peak 80+)", showarrow: false, xanchor: "right", font: { color: tok("ink"), size: 12 } }] }), CFG);
};
R[7] = () => {
  const r = rows(7), x = r.map(d => d["Entry edition"]);
  const c1 = "Reached potential within 4 editions (%)", c2 = "Same, players present in all 4 editions (%)";
  const tr = (c, dash, name) => ({ type: "scatter", mode: "lines+markers+text", name, x, y: r.map(d => d[c]), text: r.map((d, i) => i === 0 || i === r.length - 1 ? d[c] + "%" : ""), textposition: "top center", textfont: { color: tok("ink") },
    line: { color: tok("reality"), width: 2.5, dash }, marker: { size: 8, color: tok("reality"), line: { color: tok("surface"), width: 2 } }, customdata: r.map(d => [d["Mean gap within 4 editions"], d.Players]),
    hovertemplate: `<b>%{x}</b> · ${name}<br>%{y}% reached within 4 editions<br>Mean gap %{customdata[0]} points (%{customdata[1]} players)<extra></extra>` });
  Plotly.react("p7", [tr(c1, "solid", "All entrants"), tr(c2, "dash", "Players present in all 4 editions")],
    base({ yaxis: { title: { text: "Reached potential within 4 editions" }, range: [0, 55], ticksuffix: "%" },
      annotations: [{ x: "FIFA 20", y: 3, text: "Wonderkid inflation peaks", showarrow: false, yanchor: "bottom", font: { color: tok("promise-ink"), size: 12 } }] }), CFG);
};
R[8] = () => {
  const r = rows(8), by = Object.fromEntries(r.map(d => [P.isoNum[d.ISO3], d]));
  const el = $("#map"), W = el.clientWidth || 700, Hh = Math.round(W * 0.5);
  const geo = topojson.feature(P.world, P.world.objects.countries).features.filter(f => f.properties.name !== "Antarctica");
  const proj = d3.geoNaturalEarth1().fitSize([W, Hh], { type: "FeatureCollection", features: geo }), path = d3.geoPath(proj);
  const col = d3.scaleDiverging([-4, 0, 4], t => d3.interpolateRgbBasis([tok("beat"), tok("neutral-mid"), tok("short")])(t)).clamp(true);
  const tip = $("#tip");
  el.innerHTML = "";
  const svg = d3.select(el).append("svg").attr("viewBox", `0 0 ${W} ${Hh}`);
  svg.selectAll("path").data(geo).join("path").attr("d", path)
    .attr("fill", f => by[f.id] ? col(by[f.id]["Shortfall vs similar prospects"]) : tok("surface"))
    .attr("stroke", f => by[f.id] ? tok("surface") : tok("muted")).attr("stroke-width", f => by[f.id] ? .6 : .5)
    .on("mousemove", (ev, f) => { const d = by[f.id]; tip.hidden = false; tip.style.left = Math.min(ev.clientX + 12, innerWidth - 270) + "px"; tip.style.top = ev.clientY + 12 + "px";
      tip.innerHTML = d ? `<b>${esc(d.Nation)}</b> (${d.Players} players)<br>Shortfall vs similar prospects: ${d["Shortfall vs similar prospects"]} points<br>95% CI ${d["CI low"]} to ${d["CI high"]}<br>${esc(d.Verdict)}<br>Reached potential: ${d["Share reached potential (%)"]}%` : `<b>${esc(f.properties.name)}</b><br>Fewer than 15 entrants`; })
    .on("mouseleave", () => { tip.hidden = true; });
  const stops = d3.range(0, 1.01, .1).map(t => col(-4 + 8 * t));
  $("#maplegend").innerHTML = `<span>Beat similar prospects</span><span class="bar" style="background:linear-gradient(90deg,${stops.join(",")})"></span><span>Fell short</span><span style="color:var(--muted)">(−4 to +4 rating points; outline only = fewer than 15 entrants)</span>`;
  const sig = r.filter(d => d.Players >= 100 && d.Verdict !== "In line with similar prospects");
  const fs = sig.filter(d => d["Shortfall vs similar prospects"] > 0).sort((a, b) => b["Shortfall vs similar prospects"] - a["Shortfall vs similar prospects"]).slice(0, 6);
  const bt = sig.filter(d => d["Shortfall vs similar prospects"] < 0).sort((a, b) => a["Shortfall vs similar prospects"] - b["Shortfall vs similar prospects"]).slice(0, 6);
  const li = d => `<li>${esc(d.Nation)} <span style="color:var(--muted)">${d["Shortfall vs similar prospects"] > 0 ? "+" : ""}${d["Shortfall vs similar prospects"]} (n=${d.Players})</span></li>`;
  $("#maplists").innerHTML = `<div><h4>Fell short most (100+ players)</h4><ol>${fs.map(li).join("")}</ol></div><div><h4>Beat their promise most</h4><ol>${bt.map(li).join("")}</ol></div>`;
};
R[9] = () => {
  const r = rows(9), x = r.map(d => "Age " + d["Age at entry"]), y = r.map(d => d["Shortfall vs similar prospects"]);
  Plotly.react("p9", [{ type: "bar", x, y, marker: { color: y.map(v => v > 0 ? tok("short") : tok("beat")) },
    error_y: { type: "data", array: r.map(d => d["CI high"] - d["Shortfall vs similar prospects"]), arrayminus: r.map(d => d["Shortfall vs similar prospects"] - d["CI low"]), color: tok("ink"), thickness: 1.2, width: 5 },
    customdata: r.map(d => [d["Headroom given (potential − overall)"], d["CI low"], d["CI high"], d.Players]),
    hovertemplate: "<b>%{x}</b> (%{customdata[3]} players)<br>Headroom given: %{customdata[0]} points<br>Shortfall vs similar prospects: %{y} (95% CI %{customdata[1]} to %{customdata[2]})<extra></extra>" }],
    base({ yaxis: { title: { text: "Shortfall vs similar prospects (points)" }, zeroline: true }, showlegend: false, margin: { l: 64, r: 24, t: 10, b: 30 } }), CFG);
  Plotly.react("p9b", [{ type: "bar", x, y: r.map(d => d["Made it in real life (%)"]), marker: { color: tok("reality") }, text: r.map(d => d["Made it in real life (%)"] + "%"), textposition: "outside", textfont: { color: tok("ink") }, cliponaxis: false,
    hovertemplate: "<b>%{x}</b><br>Made it in real life: %{y}%<extra></extra>" }],
    base({ yaxis: { title: { text: "Made it (%)" }, range: [0, 25], ticksuffix: "%" }, showlegend: false, margin: { l: 64, r: 24, t: 6, b: 40 } }), CFG);
};
R[10] = () => {
  const r = rows(10), sh = d => d["Shortfall vs similar prospects"];
  const lab = new Set(r.slice().sort((a, b) => b["Mean club Elo at entry"] - a["Mean club Elo at entry"]).slice(0, 7).map(d => d.Club));
  r.filter(d => d.Players >= 10).sort((a, b) => Math.abs(sh(b)) - Math.abs(sh(a))).slice(0, 4).forEach(d => lab.add(d.Club));
  const colr = d => sh(d) >= 3 ? tok("short") : sh(d) <= -3 ? tok("beat") : tok("context");
  Plotly.react("p10", [{ type: "scatter", mode: "markers+text", x: r.map(d => d["Mean club Elo at entry"]), y: r.map(sh),
    text: r.map(d => lab.has(d.Club) ? d.Club : ""), textposition: "top center", textfont: { color: tok("ink"), size: 11 },
    marker: { size: r.map(d => 5 + Math.sqrt(d.Players) * 2.2), color: r.map(d => hexA(colr(d), .75)), line: { color: tok("surface"), width: 1 } },
    customdata: r.map(d => [d.Club, d.League, d.Country, d.Players, d["Extra potential vs same rating and age"]]),
    hovertemplate: "<b>%{customdata[0]}</b> (%{customdata[1]}, %{customdata[2]})<br>%{customdata[3]} entrants · mean Elo %{x}<br>Shortfall vs similar prospects: %{y}<br>Extra potential vs same rating and age: %{customdata[4]}<extra></extra>" }],
    base({ xaxis: { title: { text: "Mean club Elo when the player entered the game" } }, yaxis: { title: { text: "Shortfall vs similar prospects (points)" }, zeroline: true, zerolinewidth: 1.5 }, showlegend: false }), CFG);
};
R[11] = () => {
  const r = rows(11).slice().reverse(), x = r.map(d => d["Shortfall vs similar prospects"]);
  const colr = d => (d["CI low"] <= 0 && d["CI high"] >= 0) ? tok("context") : d["Shortfall vs similar prospects"] > 0 ? tok("short") : tok("beat");
  Plotly.react("p11", [{ type: "bar", orientation: "h", y: r.map(d => d["Primary position"]), x, marker: { color: r.map(colr) },
    error_x: { type: "data", array: r.map(d => d["CI high"] - d["Shortfall vs similar prospects"]), arrayminus: r.map(d => d["Shortfall vs similar prospects"] - d["CI low"]), color: tok("ink"), thickness: 1.2, width: 4 },
    customdata: r.map(d => [d.Players, d["CI low"], d["CI high"], d["Mean potential at entry"], d["Mean peak later rating"]]),
    hovertemplate: "<b>%{y}</b> (%{customdata[0]} players)<br>Shortfall vs similar prospects: %{x} (95% CI %{customdata[1]} to %{customdata[2]})<br>Mean potential %{customdata[3]} → mean peak %{customdata[4]}<extra></extra>" }],
    base({ xaxis: { title: { text: "Shortfall vs similar prospects (points; + = fell short)" }, zeroline: true, zerolinewidth: 1.5 }, showlegend: false, margin: { l: 56, r: 24, t: 10, b: 50 } }), CFG);
};
R[12] = () => {
  const r = rows(12).slice().reverse(), y = r.map(d => d.Predictor), x = r.map(d => d["AUC: who made it"]);
  const colr = d => d.Predictor.startsWith("EA potential") ? tok("promise") : d.Predictor.startsWith("Transfermarkt") ? tok("reality") : tok("context");
  Plotly.react("p12", [{ type: "scatter", mode: "markers+text", y, x, text: x.map(v => v.toFixed(2)), textposition: "top center", textfont: { color: tok("ink") },
    marker: { size: 14, color: r.map(colr), line: { color: tok("ink"), width: 1.5 } },
    error_x: { type: "data", array: r.map(d => d["CI high"] - d["AUC: who made it"]), arrayminus: r.map(d => d["AUC: who made it"] - d["CI low"]), color: tok("ink"), thickness: 1.5, width: 6 },
    customdata: r.map(d => [d["CI low"], d["CI high"], d["Correlation with peak later rating"] ?? "n/a", d["What it is"]]),
    hovertemplate: "<b>%{y}</b><br>AUC %{x:.3f} (95% CI %{customdata[0]}–%{customdata[1]})<br>Correlation with the game's own later rating: %{customdata[2]}<br>%{customdata[3]}<extra></extra>" }],
    base({ xaxis: { title: { text: "AUC for 'made it' (0.5 = coin flip)" }, range: [0.6, 0.78] }, yaxis: { automargin: true }, showlegend: false, margin: { l: 250, r: 24, t: 10, b: 50 } }), CFG);
};
R[13] = () => {
  const r = rows(13), feat = [...new Set(r.filter(d => d.Featured === "Yes").map(d => d.Player))], rest = [...new Set(r.filter(d => d.Featured !== "Yes").map(d => d.Player))].sort();
  const sel = $("#pick13");
  if (!sel.options.length) {
    sel.innerHTML = `<optgroup label="Featured five">${feat.map(p => `<option>${esc(p)}</option>`).join("")}</optgroup><optgroup label="Ten more well-known entrants">${rest.map(p => `<option>${esc(p)}</option>`).join("")}</optgroup>`;
    sel.addEventListener("change", () => R[13]());
  }
  const d = r.filter(x => x.Player === sel.value);
  const tr = (c, color, name) => ({ type: "scatter", mode: "lines+markers", connectgaps: true, name, x: d.filter(x => x[c] != null).map(x => x.Date), y: d.filter(x => x[c] != null).map(x => x[c]),
    line: { color, width: 2.5 }, marker: { size: 6, color, line: { color: tok("surface"), width: 1 } }, hovertemplate: `<b>${esc(sel.value)}</b> · %{x}<br>${name}: %{y}% of his peak<extra></extra>` });
  Plotly.react("p13", [tr("Game rating (% of own peak)", tok("promise"), "Game rating"), tr("Market value (% of own peak)", tok("reality"), "Market value")],
    base({ yaxis: { title: { text: "% of his own peak" }, range: [0, 106], ticksuffix: "%" }, xaxis: { type: "date" } }), CFG);
};
R[14] = () => {
  const r = rows(14), names = [...new Set(r.flatMap(d => [d.Source, d.Target]))], idx = Object.fromEntries(names.map((n, i) => [n, i]));
  const nodeCol = n => n.startsWith("Potential") ? tok("promise") : n === "Game: reached" ? tok("reality") : n === "Game: fell short" ? tok("short") : n === "Game: vanished" ? tok("context") : n === "Big-5" ? tok("beat") : tok("context");
  Plotly.react("p14", [{ type: "sankey", arrangement: "snap", valueformat: ",d",
    node: { label: names, color: names.map(nodeCol), pad: 14, thickness: 16, line: { color: tok("surface"), width: 1 }, hovertemplate: "<b>%{label}</b><br>%{value} players<extra></extra>" },
    link: { source: r.map(d => idx[d.Source]), target: r.map(d => idx[d.Target]), value: r.map(d => d.Value), color: r.map(d => hexA(nodeCol(d.Source), .28)), hovertemplate: "%{source.label} → %{target.label}<br>%{value} players<extra></extra>" },
    textfont: { color: tok("ink"), size: 12, family: "IBM Plex Sans, system-ui, sans-serif" } }],
    base({ margin: { l: 10, r: 10, t: 10, b: 10 } }), CFG);
};

function renderAll() { for (const k of Object.keys(R)) { try { R[k](); } catch (e) { console.error("chart", k, e); } } }
renderAll();
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", renderAll);
new MutationObserver(renderAll).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
let rz; addEventListener("resize", () => { clearTimeout(rz); rz = setTimeout(() => R[8](), 200); });
</script>
"""

if __name__ == "__main__":
    main()
