"""Chart-ready tables for the 14 charts (CLAUDE.md §9, chart plan v2) and their spec entries.

Each `chart_NN(ctx)` returns (DataFrame, facts). `facts` holds every number the chart's title or notes use;
export notebooks write them to findings.json, and spec titles are built from them (never typed by hand).
Formatting follows §9.1: ratings as integers, gaps/shortfalls to 1 decimal, money in € millions to 1 decimal,
shares as whole percentages, edition labels as text, a `Featured` column wherever players are shown.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src import config, findings as fd, outcomes, stats as st

R, FS, V = config.STATUS_REACHED, config.STATUS_FELL_SHORT, config.STATUS_VANISHED
UK = ["England", "Scotland", "Wales", "Northern Ireland"]
P = config.PALETTE


@dataclass
class Ctx:
    a: pd.DataFrame            # analysis.parquet
    acc: pd.DataFrame          # accuracy sample (not already peaked)
    g: pd.DataFrame            # acc with a later edition, plus peak/shortfall columns
    line: tuple[float, float]  # calibration line (intercept, slope)
    featured_ids: list[int]
    featured_names: dict[int, str]
    findings: dict


def load_ctx() -> Ctx:
    a = pd.read_parquet(config.CLEAN / "analysis.parquet")
    acc = a[~a["already_peaked"]].copy()
    g = acc[acc["peak_later"].notna()].copy()
    g["peak"] = g["peak_later"].astype(float)
    line = st.calibration_line(g)
    g["shortfall"] = st.shortfall(g, line)
    f = fd.load()
    picks = f["featured_five"]["picks"]
    ids = [int(v["player_id"]) for v in picks.values()]
    names = {int(v["player_id"]): v["player"] for v in picks.values()}
    return Ctx(a, acc, g, line, ids, names, f)


def _featured(ctx: Ctx, ids: pd.Series) -> pd.Series:
    return ids.isin(ctx.featured_ids).map({True: "Yes", False: ""})


def _int(s):
    return s.round().astype("Int64")


def _ci_rows(df, by, value, min_n, reps=config.BOOTSTRAP_REPS):
    rows = []
    for k, d in df.groupby(by, observed=True):
        if len(d) < min_n:
            continue
        est, lo, hi = st.boot_ci(d, lambda x: x[value].mean(), reps=reps)
        rows.append({by: k, "n": len(d), "est": est, "lo": lo, "hi": hi})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- Act 1: the promise
def chart_01(ctx: Ctx):
    w = ctx.a[(ctx.a["entry_edition"] == 15) & ctx.a["is_wonderkid"]].copy()
    w = w.sort_values(["potential", "peak_later"], ascending=False)
    df = pd.DataFrame({
        "Player": w["short_name"], "Club (2014)": w["club_name"], "Nation": w["nationality_name"], "Age": w["age"],
        "Overall": w["overall"], "Potential": w["potential"], "Peak later rating": _int(w["peak_later"].astype(float)),
        "Gap": _int(w["gap"].astype(float)), "Status": w["status"],
        "Big-5 minutes": _int(w["big5_minutes"].astype(float)),
        "Made it (3,000+ Big-5 min)": w["made_it"].map({True: "Yes", False: "No"}),
        "Peak market value (€m)": (w["peak_market_value_eur"] / 1e6).round(1),
        "Latest club": w["tm_current_club_name"], "Featured": _featured(ctx, w["player_id"]),
    })
    facts = {"n": len(w), "reached": int((w["status"] == R).sum()), "made_it": int(w["made_it"].sum()),
             "made_it_pct": fd.pct(w["made_it"].mean()), "fell_short": int((w["status"] == FS).sum()),
             "vanished": int((w["status"] == V).sum())}
    return df, facts


def chart_02(ctx: Ctx):
    r = ctx.findings["robust_inflation"]["by_edition"]
    df = pd.DataFrame([{"Edition": k, "Under-21s in game": v["u21"],
                        "Wonderkids (under-21, potential 85+)": int(round(v["wonderkids_per_1000"] * v["u21"] / 1000)),
                        "Wonderkids per 1,000 under-21s": round(v["wonderkids_per_1000"], 1),
                        "Average headroom (potential − overall)": round(v["headroom"], 1),
                        "Average under-21 potential": round(v["mean_potential"], 1),
                        "Average under-21 overall": round(v["mean_overall"], 1)} for k, v in r.items()])
    i = ctx.findings["robust_inflation"]
    facts = {k: i[k] for k in ["wk_per_1000_first", "wk_per_1000_max", "wk_per_1000_max_edition", "wk_per_1000_last",
                               "headroom_first", "headroom_max", "mean_potential_change_first_to_max",
                               "mean_overall_change_first_to_max"]}
    facts["multiple"] = round(i["wk_per_1000_max"] / i["wk_per_1000_first"], 1)
    return df, facts


def chart_03(ctx: Ctx, panel: pd.DataFrame):
    labels = [config.EDITION_LABELS[e] for e in config.EDITIONS]
    df = pd.DataFrame({"Edition": labels})
    for pid in ctx.featured_ids:
        s = panel[panel["player_id"] == pid].set_index("edition")["overall"]
        df[ctx.featured_names[pid]] = [s.get(e) for e in config.EDITIONS]
    wk = ctx.a[(ctx.a["entry_edition"] == 15) & ctx.a["is_wonderkid"]]["player_id"]
    med = panel[panel["player_id"].isin(wk)].groupby("edition")["overall"].median()
    df["FIFA 15 wonderkids (median)"] = [med.get(e) for e in config.EDITIONS]
    for c in df.columns[1:]:
        df[c] = pd.to_numeric(df[c]).round().astype("Int64")
    facts = {"players": [ctx.featured_names[p] for p in ctx.featured_ids]}
    return df, facts


# ---------------------------------------------------------------- Act 2: the reckoning
def chart_04(ctx: Ctx):
    d = ctx.g[ctx.g["potential"] >= 75].sort_values("potential")
    df = pd.DataFrame({
        "Player": d["short_name"], "Entry edition": d["entry_edition_label"], "Position group": d["position_group"],
        "Potential": d["potential"], "Peak later rating": _int(d["peak"]), "Status": d["status"],
        "Club": d["club_name"], "Nation": d["nationality_name"], "Featured": _featured(ctx, d["player_id"]),
    })
    b0, b1 = ctx.line
    cal = ctx.findings["robust_calibration"]
    facts = {"n": len(d), "below_diagonal_pct": fd.pct((d["peak"] < d["potential"]).mean()),
             "slope": cal["slope"]["value"], "slope_ci": [cal["slope"]["ci_low"], cal["slope"]["ci_high"]],
             "points_per_10": cal["points_of_peak_per_10_points_potential"],
             "line_intercept": round(b0, 2), "line_slope": round(b1, 3),
             "line_at_75": round(b0 + b1 * 75, 1), "line_at_95": round(b0 + b1 * 95, 1),
             "survivor_slope_range": [ctx.findings["self_review"]["survivorship"]["slope_full_survivors"]["value"],
                                      ctx.findings["self_review"]["survivorship"]["slope_vanished_as_no_growth"]["value"]]}
    return df, facts


def chart_05(ctx: Ctx):
    cb = ctx.findings["calibration_by_band"]
    df = pd.DataFrame([{"Potential band": b, "Reached potential in the game (%)": cb[b]["reached_pct"],
                        "Made it in real life (%)": cb[b]["made_it_pct"], "Fell short in the game (%)": cb[b]["fell_short_pct"],
                        "Vanished from the game (%)": cb[b]["vanished_pct"], "Players": cb[b]["n"]} for b in config.BAND_ORDER])
    facts = {"top_band_reached_pct": cb["85+"]["reached_pct"], "top_band_made_it_pct": cb["85+"]["made_it_pct"],
             "bottom_band_reached_pct": cb["<70"]["reached_pct"], "bottom_band_made_it_pct": cb["<70"]["made_it_pct"]}
    return df, facts


def chart_06(ctx: Ctx):
    f6 = ctx.findings["chart_06"]
    rows = []
    for grp, key in [("Bust", "busts"), ("Bloomer", "bloomers")]:
        for p in f6[key]:
            r = ctx.a[ctx.a["player_id"] == p["player_id"]].iloc[0]
            rows.append({"Player": f"{p['player']} ({grp.lower()})", "Potential at entry": p["potential"],
                         "Peak later rating": p["peak_later"], "Gap": p["gap"], "Group": grp,
                         "Entry edition": p["entry_edition"], "Club at entry": r["club_name"],
                         "Featured": "Yes" if p["player_id"] in ctx.featured_ids else ""})
    df = pd.DataFrame(rows)
    facts = {"biggest_bust": f6["biggest_bust"], "biggest_bloomer": f6["biggest_bloomer"]}
    return df, facts


def chart_07(ctx: Ctx):
    allc = ctx.findings["chart_07"]["by_entry_edition"]
    surv = ctx.findings["self_review"]["chart07_full_survivors"]
    df = pd.DataFrame([{"Entry edition": k, "Reached potential within 4 editions (%)": v["reached_within_4_pct"],
                        "Same, players present in all 4 editions (%)": surv[k]["reached_within_4_pct"],
                        "Mean gap within 4 editions": v["mean_gap_within_4"], "Players": v["n"]} for k, v in allc.items()])
    facts = {"first": df.iloc[0, 1], "last": df.iloc[-1, 1], "first_surv": df.iloc[0, 2], "last_surv": df.iloc[-1, 2],
             "gap_first": df.iloc[0, 3], "gap_last": df.iloc[-1, 3]}
    return df, facts


# ---------------------------------------------------------------- Act 3: who the game misjudged
def chart_08(ctx: Ctx, nation_iso: pd.DataFrame):
    g = ctx.g.copy()
    g["map_nation"] = np.where(g["nationality_name"].isin(UK), "United Kingdom", g["nationality_name"])
    ci = _ci_rows(g, "map_nation", "shortfall", config.CHART_MIN_NATION_N)
    reach = g.groupby("map_nation")["status"].apply(lambda s: (s == R).mean())
    iso = dict(zip(nation_iso["fifa_nation"], nation_iso["iso3"]))
    iso["United Kingdom"] = "GBR"
    ci["verdict"] = np.select([ci["lo"] > 0, ci["hi"] < 0], ["Fell short of similar prospects", "Beat similar prospects"],
                              default="In line with similar prospects")
    df = pd.DataFrame({"ISO3": ci["map_nation"].map(iso), "Nation": ci["map_nation"],
                       "Shortfall vs similar prospects": ci["est"].round(1), "CI low": ci["lo"].round(1), "CI high": ci["hi"].round(1),
                       "Verdict": ci["verdict"], "Share reached potential (%)": (ci["map_nation"].map(reach) * 100).round().astype(int),
                       "Players": ci["n"]}).sort_values("Shortfall vs similar prospects")
    assert df["ISO3"].notna().all() and df["ISO3"].is_unique
    top_short = df[df["Verdict"].str.startswith("Fell")].sort_values("Shortfall vs similar prospects", ascending=False)
    beat = df[df["Verdict"].str.startswith("Beat")].sort_values("Shortfall vs similar prospects")
    big = df[df["Players"] >= 100]
    facts = {"nations": len(df), "fell_short": int((df["Verdict"].str.startswith("Fell")).sum()),
             "beat": int((df["Verdict"].str.startswith("Beat")).sum()),
             "most_short_100plus": big.sort_values("Shortfall vs similar prospects").iloc[-1][["Nation", "Shortfall vs similar prospects", "Players"]].to_dict(),
             "most_beat_100plus": big.sort_values("Shortfall vs similar prospects").iloc[0][["Nation", "Shortfall vs similar prospects", "Players"]].to_dict(),
             "uk": df[df["Nation"] == "United Kingdom"].iloc[0][["Shortfall vs similar prospects", "CI low", "CI high", "Players"]].to_dict(),
             "top_fell_short": top_short["Nation"].head(5).tolist(), "top_beat": beat["Nation"].head(5).tolist(),
             "top3_fell_short_100plus": big[big["Verdict"].str.startswith("Fell")].sort_values("Shortfall vs similar prospects", ascending=False)["Nation"].head(3).tolist(),
             "top3_beat_100plus": big[big["Verdict"].str.startswith("Beat")].sort_values("Shortfall vs similar prospects")["Nation"].head(3).tolist()}
    return df, facts


def chart_09(ctx: Ctx):
    g = ctx.g
    ci = _ci_rows(g, "age", "shortfall", 15)
    made = ctx.acc.groupby("age")["made_it"].mean()
    head = ctx.acc.assign(h=ctx.acc["potential"] - ctx.acc["overall"]).groupby("age")["h"].mean()
    df = pd.DataFrame({"Age at entry": ci["age"].astype(int), "Headroom given (potential − overall)": ci["age"].map(head).round(1),
                       "Shortfall vs similar prospects": ci["est"].round(1), "CI low": ci["lo"].round(1), "CI high": ci["hi"].round(1),
                       "Made it in real life (%)": (ci["age"].map(made) * 100).round().astype(int), "Players": ci["n"]})
    sr = ctx.findings["self_review"]["age_shortfall"]["age17_minus_21"]
    row = lambda a_: df[df["Age at entry"] == a_].iloc[0]
    facts = {"headroom_17": float(row(17)["Headroom given (potential − overall)"]), "headroom_21": float(row(21)["Headroom given (potential − overall)"]),
             "shortfall_17_minus_21": sr["value"], "ci": [sr["ci_low"], sr["ci_high"]],
             "made_it_17": int(row(17)["Made it in real life (%)"]), "made_it_21": int(row(21)["Made it in real life (%)"])}
    return df, facts


def chart_10(ctx: Ctx):
    g = ctx.g[ctx.g["club_elo_at_entry"].notna()].copy()
    e = ctx.acc[ctx.acc["club_elo_at_entry"].notna()].copy()
    X = np.column_stack([np.ones(len(e)), e["overall"], e["age"]])
    coef = np.linalg.lstsq(X, e["potential"].astype(float), rcond=None)[0]
    e["extra_potential"] = e["potential"] - X @ coef
    by = g.groupby("club_name").agg(n=("player_id", "size"), elo=("club_elo_at_entry", "mean"), shortfall=("shortfall", "mean"),
                                    league=("league_name_edition", lambda s: s.mode().iat[0]), country=("league_country", "first"))
    by["extra"] = e.groupby("club_name")["extra_potential"].mean()
    by = by[by["n"] >= config.CHART_MIN_CLUB_N].reset_index().sort_values("elo", ascending=False)
    df = pd.DataFrame({"Club": by["club_name"], "League": by["league"], "Country": by["country"],
                       "Mean club Elo at entry": by["elo"].round().astype(int),
                       "Shortfall vs similar prospects": by["shortfall"].round(1),
                       "Extra potential vs same rating and age": by["extra"].round(1), "Players": by["n"]})
    cr = ctx.findings["self_review"]["club"]
    p10, p90 = e["club_elo_at_entry"].quantile([0.1, 0.9])
    prem = cr["badge_premium_potential_per_100_elo"]
    facts = {"clubs": len(df), "badge_premium_per_100_elo": prem,
             "elo_p10": int(round(p10)), "elo_p90": int(round(p90)),
             "premium_p10_to_p90": round(prem["value"] * (p90 - p10) / 100, 1),
             "spearman_club_elo_vs_shortfall": round(st.spearman(by["elo"], by["shortfall"]), 2),
             "spearman_club_elo_vs_extra_potential": round(st.spearman(by["elo"], by["extra"]), 2),
             "real_outcome_confirms_club_effect": cr["real_outcome_confirms_club_effect"]}
    return df, facts


def chart_11(ctx: Ctx):
    ci = _ci_rows(ctx.g, "primary_position", "shortfall", 30)
    pos = ctx.g.groupby("primary_position").agg(pot=("potential", "mean"), peak=("peak", "mean"))
    df = pd.DataFrame({"Primary position": ci["primary_position"], "Position group": ci["primary_position"].map(config.POSITION_TO_GROUP),
                       "Shortfall vs similar prospects": ci["est"].round(1), "CI low": ci["lo"].round(1), "CI high": ci["hi"].round(1),
                       "Mean potential at entry": ci["primary_position"].map(pos["pot"]).round().astype(int),
                       "Mean peak later rating": ci["primary_position"].map(pos["peak"]).round().astype(int),
                       "Players": ci["n"]}).sort_values("Shortfall vs similar prospects", ascending=False)
    short = df[df["CI low"] > 0]; beat = df[df["CI high"] < 0]
    facts = {"fell_short": short["Primary position"].tolist(), "beat": beat["Primary position"].tolist(),
             "worst": df.iloc[0][["Primary position", "Shortfall vs similar prospects"]].to_dict(),
             "best": df.iloc[-1][["Primary position", "Shortfall vs similar prospects"]].to_dict()}
    return df, facts


# ---------------------------------------------------------------- Act 4: what actually mattered
def chart_12(ctx: Ctx):
    acc = ctx.acc.copy()
    acc["benchmark"] = st.loeo_benchmark(acc)
    acc["log_value"] = np.log1p(acc["market_value_at_entry_eur"])
    mv = acc[acc["is_matched"] & acc["log_value"].notna()]
    g = acc[acc["peak_later"].notna()]
    preds = [("EA potential rating", "potential", "The game's promise for the player"),
             ("Transfermarkt market value at entry", "log_value", "What the transfer market paid for"),
             ("Simple formula: overall + age", "benchmark", "Out-of-sample fit on the other editions"),
             ("EA overall rating (current ability)", "overall", "The game's rating today, no promise")]
    rows = []
    for name, col, desc in preds:
        a_, lo, hi = st.boot_ci(mv, lambda d, c=col: st.auc(d[c], d["made_it"]))
        sp = st.spearman(g[col], g["peak_later"].astype(float)) if col != "log_value" else np.nan
        rows.append({"Predictor": name, "AUC: who made it": round(a_, 3), "CI low": round(lo, 3), "CI high": round(hi, 3),
                     "Correlation with peak later rating": round(sp, 2) if pd.notna(sp) else None, "What it is": desc})
    df = pd.DataFrame(rows)
    b = ctx.findings["robust_benchmark"]
    facts = {"n": len(mv), "potential_auc": df.iloc[0, 1], "market_auc": df.iloc[1, 1], "benchmark_auc": df.iloc[2, 1],
             "overall_auc": df.iloc[3, 1], "potential_minus_market": b["potential_minus_market_auc"],
             "potential_within_value_quintiles": b["potential_auc_within_value_quintiles_mean"],
             "spearman_potential": df.iloc[0, 4], "spearman_overall": df.iloc[3, 4]}
    return df, facts


def chart_13(ctx: Ctx, panel: pd.DataFrame, valuations: pd.DataFrame, n_more: int = 10):
    extra = (ctx.a[ctx.a["is_matched"] & ~ctx.a["player_id"].isin(ctx.featured_ids)]
             .sort_values("peak_market_value_eur", ascending=False).head(n_more))
    people = ctx.a[ctx.a["player_id"].isin(ctx.featured_ids + extra["player_id"].tolist())]
    rows = []
    for r in people.itertuples():
        pr = panel[panel["player_id"] == r.player_id]
        peak_r = pr["overall"].max()
        for e, ov, dt in zip(pr["edition"], pr["overall"], pr["edition_date"]):
            rows.append({"Date": dt.strftime("%Y-%m-%d"), "Player": r.short_name, "Game rating (% of own peak)": round(ov / peak_r * 100),
                         "Market value (% of own peak)": None})
        v = valuations[valuations["player_id"] == r.tm_player_id]
        v = v[v["date"] >= pd.Timestamp("2014-07-01")]
        if len(v):
            peak_v = v["market_value_in_eur"].max()
            for dt, mvv in zip(v["date"], v["market_value_in_eur"]):
                rows.append({"Date": dt.strftime("%Y-%m-%d"), "Player": r.short_name, "Game rating (% of own peak)": None,
                             "Market value (% of own peak)": round(mvv / peak_v * 100)})
    df = pd.DataFrame(rows).sort_values(["Player", "Date"])
    df["Featured"] = df["Player"].isin([ctx.featured_names[p] for p in ctx.featured_ids]).map({True: "Yes", False: ""})
    for c in ["Game rating (% of own peak)", "Market value (% of own peak)"]:
        df[c] = df[c].astype("Int64")
    facts = {"players": sorted(df["Player"].unique().tolist()), "n_more": n_more}
    return df, facts


# ---------------------------------------------------------------- Act 5: where they are now
def chart_14(ctx: Ctx):
    d = ctx.acc[ctx.acc["potential"] >= 75].copy()
    d["band"] = "Potential " + d["potential_band"].astype(str)
    d["status_node"] = "Game: " + d["status"].str.lower()
    s1 = d.groupby(["band", "status_node"]).size().reset_index(name="Value").rename(columns={"band": "Source", "status_node": "Target"})
    s2 = d.groupby(["status_node", "latest_club_tier"]).size().reset_index(name="Value").rename(
        columns={"status_node": "Source", "latest_club_tier": "Target"})
    s1["Step"], s2["Step"] = "1: band to game status", "2: game status to latest club"
    df = pd.concat([s1, s2], ignore_index=True)
    tiers = d["latest_club_tier"].value_counts(normalize=True)
    wk = d[d["potential"] >= config.WONDERKID_POTENTIAL]["latest_club_tier"].value_counts()
    facts = {"n": len(d), "tier_pct": {k: fd.pct(tiers.get(k, 0)) for k in outcomes.TIER_ORDER},
             "wonderkids_big5": int(wk.get(outcomes.TIER_BIG5, 0)), "wonderkids": int(len(d[d["potential"] >= 85])),
             "provisional_tier_rule": True}
    return df, facts


# ---------------------------------------------------------------- spec writing (CLAUDE.md §9.3)
def source_line(chart: int) -> str:
    keys = config.CHART_SOURCES.get(chart, ["fifa", "transfermarkt"])
    return "; ".join(f"[{config.SOURCES[k][0]}]({config.SOURCES[k][1]})" for k in keys)


def spec_entry(n: int, short: str, tool: str, title: str, subtitle: str, mapping: str, colours: str, tooltip: str,
               notes: str) -> str:
    return (f"## Chart {n:02d}: {short}\n"
            f"- File: outputs/charts/{n:02d}_{short}.csv\n"
            f"- Tool / template: {tool}\n"
            f"- Title (states the finding, numbers from findings.json): {title}\n"
            f"- Subtitle (what is measured, units): {subtitle}\n"
            f"- Column → role mapping: {mapping}\n"
            f"- Colours: {colours}\n"
            f"- Tooltip (HTML): {tooltip}\n"
            f"- Source line: {source_line(n)}\n"
            f"- Notes for the builder: {notes}\n")


def write_spec(n: int, text: str) -> None:
    """Create or replace chart n's entry in chart_specs.md (idempotent, kept in chart order)."""
    path = config.CHART_SPECS
    begin, end = f"<!-- BEGIN CHART {n:02d} -->", f"<!-- END CHART {n:02d} -->"
    block = f"{begin}\n{text.strip()}\n{end}"
    cur = path.read_text(encoding="utf-8") if path.exists() else "# Chart specs\n\nOne entry per chart, written by export notebooks 10–12.\n"
    if begin in cur:
        pre, rest = cur.split(begin, 1)
        _, post = rest.split(end, 1)
        cur = pre + block + post
    else:
        cur = cur.rstrip() + "\n\n" + block + "\n"
    # keep chart order
    head = cur.split("<!-- BEGIN CHART", 1)[0]
    blocks = {}
    for part in cur.split("<!-- BEGIN CHART ")[1:]:
        k = int(part[:2]); blocks[k] = "<!-- BEGIN CHART " + part.split(f"<!-- END CHART {part[:2]} -->")[0] + f"<!-- END CHART {part[:2]} -->"
    path.write_text(head.rstrip() + "\n\n" + "\n\n".join(blocks[k] for k in sorted(blocks)) + "\n", encoding="utf-8")


def save_csv(n: int, short: str, df: pd.DataFrame) -> None:
    assert len(df) <= config.CHART_MAX_ROWS, f"chart {n}: {len(df)} rows > {config.CHART_MAX_ROWS}"
    config.CHARTS.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.CHARTS / f"{n:02d}_{short}.csv", index=False, encoding="utf-8")
