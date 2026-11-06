"""Build the story website: website/index.html from findings.json, chart_specs.md and website/embeds.json.

Teammates paste each published chart's ID (or its full embed code) into website/embeds.json, then run:
    python -I scripts/build_story_site.py
Every number in the narrative comes from outputs/findings.json (CLAUDE.md rule 5). Chart titles live inside the
Datawrapper/Flourish charts themselves; the page only adds act headings and connecting text.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import config  # noqa: E402

SITE = ROOT / "website"
EMBEDS = SITE / "embeds.json"
TOOLS = {1: "datawrapper", 2: "datawrapper", 3: "flourish", 4: "datawrapper", 5: "datawrapper", 6: "datawrapper",
         7: "flourish", 8: "datawrapper", 9: "flourish", 10: "flourish", 11: "flourish", 12: "datawrapper",
         13: "flourish", 14: "flourish"}
HEIGHTS = {1: 620, 2: 420, 3: 480, 4: 560, 5: 420, 6: 600, 7: 420, 8: 520, 9: 560, 10: 520, 11: 520, 12: 380, 13: 520, 14: 620}


def spec_titles():
    text = config.CHART_SPECS.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"<!-- BEGIN CHART (\d\d) -->(.*?)<!-- END CHART \1 -->", text, re.S):
        t = re.search(r"- Title[^:]*: (.*)", m.group(2)).group(1).strip()
        out[int(m.group(1))] = t
    return out


def ensure_embeds():
    if EMBEDS.exists():
        return json.loads(EMBEDS.read_text(encoding="utf-8"))
    SITE.mkdir(exist_ok=True)
    data = {f"{n:02d}": {"tool": TOOLS[n], "id": "", "embed_html": "", "height": HEIGHTS[n],
                         "csv": next(str(p.relative_to(ROOT)) for p in config.CHARTS.glob(f"{n:02d}_*.csv"))} for n in TOOLS}
    EMBEDS.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def embed(n, e, title):
    t = html.escape(title, quote=True)
    if e.get("embed_html"):
        return e["embed_html"]
    if e.get("id"):
        cid = html.escape(e["id"].strip())
        if e["tool"] == "datawrapper":
            return (f'<iframe title="{t}" aria-label="{t}" id="datawrapper-chart-{cid}" src="https://datawrapper.dwcdn.net/{cid}/" '
                    f'scrolling="no" frameborder="0" style="width:0;min-width:100%!important;border:none;" height="{e.get("height", 450)}" data-external="1"></iframe>')
        return (f'<div class="flourish-embed flourish-chart" data-src="visualisation/{cid}" aria-label="{t}"></div>'
                f'<noscript><iframe src="https://flo.uri.sh/visualisation/{cid}/embed" title="{t}" frameborder="0" scrolling="no" '
                f'style="width:100%;height:{e.get("height", 500)}px"></iframe></noscript>')
    return (f'<div class="placeholder" style="min-height:{min(e.get("height", 400), 360)}px"><b>Chart {n:02d} not embedded yet</b>'
            f'<span>{t}</span><span>Build it in {e["tool"].title()} from <code>{html.escape(e["csv"])}</code>, then paste its ID into '
            f'<code>website/embeds.json</code> and re-run <code>python -I scripts/build_story_site.py</code>.</span></div>')


def main():
    F = json.loads(config.FINDINGS.read_text(encoding="utf-8"))
    T, E = spec_titles(), ensure_embeds()
    if "09b" not in E:   # chart 9's second panel (made it % by age): its own Flourish chart, no dual axis
        E["09b"] = {"tool": "flourish", "id": "", "embed_html": "", "height": 280, "csv": E["09"]["csv"]}
        EMBEDS.write_text(json.dumps(E, indent=2), encoding="utf-8")
    c1, c2, c4, c7, c9, c10, c11, c12, c14 = (F[f"export_chart_{k}"] for k in ["01", "02", "04", "07", "09", "10", "11", "12", "14"])
    cal, sr = F["calibration_by_band"], F["self_review"]
    pos = {"GK": "goalkeepers", "ST": "strikers", "CDM": "defensive midfielders", "LW": "left wingers", "CB": "centre-backs",
           "LB": "left-backs", "RB": "right-backs", "CF": "centre-forwards", "RW": "right wingers"}
    feat = F["featured_five"]["picks"]
    fp = {k: v["player"] for k, v in feat.items()}
    def and_join(xs):
        xs = list(xs)
        return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
    acts = [
        ("The promise", [
            f"Every autumn, EA Sports rates the world's young footballers and gives each a <em>potential</em>: the rating the game "
            f"says he can grow into. Millions of Career Mode players build squads around those numbers. In FIFA 15 (September 2014), "
            f"{c1['n']} under-21s were rated 85 or higher: the game's wonderkids.",
            f"Over the next five editions EA handed out far more of them. By {c2['wk_per_1000_max_edition']} there were "
            f"{c2['wk_per_1000_max']} wonderkid ratings per 1,000 under-21s, {c2['multiple']}× the FIFA 15 rate, while the average "
            f"under-21's current ability rose only {c2['mean_overall_change_first_to_max']} points.",
        ], [1, 2, 3]),
        ("The reckoning", [
            f"We followed {F['cohort']['entrants']:,} young entrants from FIFA 15 to FIFA 18 through every later edition up to FC 24. "
            f"Most promises weren't kept: among prospects rated 75+, {c4['below_diagonal_pct']}% peaked below their potential, and every "
            f"10 points of promise delivered only {c4['points_per_10']} points of real rating.",
            f"Yet the promise still meant something. Only {cal['85+']['reached_pct']}% of 85+ prospects reached their number in the game, "
            f"but {cal['85+']['made_it_pct']}% built real Big-5 careers (3,000+ league minutes), against {cal['<70']['made_it_pct']}% "
            f"of those rated under 70. And as the wonderkid ratings multiplied, fewer came true: {c7['first']}% of FIFA 15 entrants "
            f"reached their potential within four editions, {c7['last']}% of FIFA 20's.",
        ], [4, 5, 6, 7]),
        ("Who the game misjudged", [
            f"To compare groups fairly we measure each player against others given the same potential. By that yardstick EA "
            f"over-promised most for the youngest: 17-year-olds got {c9['headroom_17']} points of headroom, nearly twice a "
            f"21-year-old's, and fell {c9['shortfall_17_minus_21']:.1f} points further short.",
            f"The big-club badge, a common fan suspicion, barely mattered: an elite club added about {c10['premium_p10_to_p90']} "
            f"potential points compared with a weak one, and those players lived up to it. Among positions, "
            f"{and_join(pos.get(p, p) for p in c11['fell_short'])} fell short most.",
        ], [8, 9, 10, 11]),
        ("What actually mattered", [
            f"As a ranking, the game's potential worked about as well as the transfer market. Measured by AUC (the chance of ranking a "
            f"player who made it above one who didn't, where 0.5 is a coin flip), EA potential scored {c12['potential_auc']:.2f} and "
            f"Transfermarkt market value at the same moment {c12['market_auc']:.2f}. The number overstated the size of the gap between "
            f"players, but the order was largely right.",
        ], [12, 13]),
        ("Where they are now", [
            f"Of {c14['n']:,} prospects rated potential 75+, {c14['tier_pct']['Big-5']}% play in a Big-5 league today. "
            f"{fp['Late bloomer']} outgrew a modest promise; {fp['Biggest bust']} never came close to his; "
            f"{fp['Latest club outside Europe']} now plays for {feat['Latest club outside Europe']['latest_club']}.",
        ], [14]),
    ]
    nav = "".join(f'<a href="#act-{i}">{html.escape(a[0])}</a>' for i, a in enumerate(acts, 1))
    body = []
    for i, (name, paras, charts) in enumerate(acts, 1):
        body.append(f'<section class="act" id="act-{i}"><p class="act-n">Act {i}</p><h2>{html.escape(name)}</h2>')
        body.extend(f"<p>{p}</p>" for p in paras)
        for n in charts:
            body.append(f'<figure id="chart-{n:02d}">{embed(n, E[f"{n:02d}"], T[n])}</figure>')
            if n == 9:
                body.append(f'<figure id="chart-09b">{embed(9, E["09b"], "Made it in real life by age at entry (panel 2 of chart 9)")}</figure>')
        body.append("</section>")
    sources = " · ".join(f'<a href="{u}">{html.escape(t)}</a>' for t, u in config.SOURCES.values())
    uses_dw = any(E[k]["tool"] == "datawrapper" and (E[k]["id"] or E[k]["embed_html"]) for k in E)
    uses_fl = any(E[k]["tool"] == "flourish" and E[k]["id"] and not E[k]["embed_html"] for k in E)
    dw_js = ('<script>!function(){"use strict";window.addEventListener("message",function(a){if(void 0!==a.data["datawrapper-height"])'
             '{var e=document.querySelectorAll("iframe");for(var t in a.data["datawrapper-height"])for(var r=0;r<e.length;r++)'
             'if(e[r].contentWindow===a.source){e[r].style.height=a.data["datawrapper-height"][t]+"px"}}})}();</script>') if uses_dw else ""
    fl_js = '<script src="https://public.flourish.studio/resources/embed.js"></script>' if uses_fl else ""
    page = TEMPLATE.format(nav=nav, body="\n".join(body), sources=sources, dw_js=dw_js, fl_js=fl_js,
                           wk=c1["n"], entrants=f"{F['cohort']['entrants']:,}")
    (SITE / "index.html").write_text(page, encoding="utf-8")
    done = sum(bool(e["id"] or e["embed_html"]) for e in E.values())
    print(f"wrote website/index.html ({done}/{len(E)} chart slots embedded; chart 9 has two slots, 09 and 09b)")


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Career Mode Promise</title>
<meta name="description" content="Did FIFA spot football's future stars? A data story testing EA Sports' potential ratings against real careers.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
/* Light-only by design: Flourish embeds do not follow dark mode, so the page matches the charts. */
:root {{ --bg:#ffffff; --ink:#1D2433; --ink-2:#4a5466; --muted:#7b8496; --rule:#dde1e8; --promise:#F2A900; --promise-ink:#7a5700;
  --display:"Saira Condensed","Arial Narrow",sans-serif; --body:"IBM Plex Sans","Segoe UI",system-ui,sans-serif; --mono:"IBM Plex Mono",ui-monospace,monospace; color-scheme: light }}
* {{ box-sizing: border-box }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:17px/1.65 var(--body) }}
.wrap {{ max-width: 760px; margin: 0 auto; padding: 32px max(16px, env(safe-area-inset-left)) 80px max(16px, env(safe-area-inset-right)) }}
header {{ border-bottom: 3px solid var(--ink); padding-bottom: 24px }}
.kicker, .act-n {{ font: 500 12px/1 var(--mono); letter-spacing:.12em; text-transform:uppercase; color:var(--muted) }}
h1 {{ font: 800 clamp(44px, 9vw, 76px)/.95 var(--display); margin: 12px 0; text-wrap: balance }}
h1 em {{ font-style: normal; color: var(--promise-ink) }}
.dek {{ font-size: 20px; color: var(--ink-2); margin: 0 }}
.byline {{ font-size: 14px; color: var(--muted); margin-top: 14px }}
nav {{ display:flex; flex-wrap:wrap; gap: 6px 18px; margin: 18px 0 0; font: 500 13px var(--mono) }}
nav a {{ color: var(--ink-2); text-decoration:none; border-bottom:1px solid var(--rule) }}
section.act {{ margin-top: 56px }}
h2 {{ font: 700 40px/1 var(--display); margin: 6px 0 16px }}
p {{ max-width: 66ch }}
figure {{ margin: 28px 0 36px; width: 100% }}
.placeholder {{ display:grid; gap:6px; align-content:center; justify-items:start; border:2px dashed var(--rule); border-radius:8px; padding:20px; color:var(--ink-2); font-size:14px }}
.placeholder b {{ font: 700 20px var(--display); color: var(--ink) }}
code {{ font: 13px var(--mono); background:#f3f4f7; padding: 1px 5px; border-radius: 4px }}
footer {{ margin-top: 64px; border-top: 1px solid var(--rule); padding-top: 16px; font-size: 14px; color: var(--ink-2) }}
footer a {{ color: var(--ink) }}
</style>
</head>
<body>
<div class="wrap">
<header>
  <p class="kicker">A data story · IE6600 Project 1</p>
  <h1>The Career Mode <em>Promise</em></h1>
  <p class="dek">EA Sports rates every young footballer's potential. We followed {wk} FIFA 15 wonderkids and {entrants} young players into real careers to see how often the game was right.</p>
  <p class="byline">By Sahil Mohanty, Devarshi Mahajan and Sarthak Sonawane</p>
  <nav aria-label="Acts">{nav}</nav>
</header>
<main>
{body}
</main>
<footer>
  <p><b>Method.</b> Cohort: each player's first FIFA 15–18 edition at age 21 or under (11,519 players). Peak later rating: best overall in any later edition up to FC 24. Made it: 3,000+ Big-5 league minutes after entry (Transfermarkt). Shortfall vs similar prospects: typical peak for a given potential minus the player's actual peak. Full method and every judgement call: the project's DECISIONS.md.</p>
  <p><b>Sources.</b> {sources}.</p>
</footer>
</div>
{dw_js}
{fl_js}
</body>
</html>
"""

if __name__ == "__main__":
    main()
