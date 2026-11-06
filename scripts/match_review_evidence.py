"""Evidence for the Transfermarkt match review (replaces a by-eye review of reports/match_review.csv).

For every FIFA player in the review file, and every Transfermarkt candidate (the review file's candidates, plus a
name-only search for players with no exact-DOB candidate), collect:
  - club overlap: FIFA clubs (any edition) vs Transfermarkt clubs (transfers, valuations, current club)
  - nationality agreement (FIFA nationality vs TM citizenship / country of birth)
  - name score, DOB difference, goalkeeper agreement
and propose a decision with a written reason. Output: reports/match_review_evidence.csv.

Usage: python -I scripts/match_review_evidence.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src import clubs, config, matching as m  # noqa: E402
from src.names import normalise  # noqa: E402

NATION_ALIASES = {
    "Korea Republic": {"Korea, South"}, "Korea DPR": {"Korea, North"}, "Côte d'Ivoire": {"Cote d'Ivoire"},
    "Turkey": {"Turkey", "Türkiye"}, "Bosnia and Herzegovina": {"Bosnia-Herzegovina"}, "Republic of Ireland": {"Ireland"},
    "Congo DR": {"DR Congo"}, "Cape Verde Islands": {"Cape Verde"}, "Gambia": {"The Gambia"}, "China PR": {"China"},
    "Guinea Bissau": {"Guinea-Bissau"}, "FYR Macedonia": {"North Macedonia"}, "São Tomé e Príncipe": {"Sao Tome and Principe"},
    "Saint Kitts and Nevis": {"St. Kitts & Nevis"}, "Saint Lucia": {"St. Lucia"},
    "Saint Vincent and the Grenadines": {"St. Vincent & Grenadinen"}, "Hong Kong": {"Hongkong"}, "Macau": {"Macao"},
}
NOT_CLUBS = {"Without Club", "Retired", "Unknown", "Career break", "Own Youth", "Ban", "Without club"}


CITY_ALIASES = {"munchen": "munich", "koln": "cologne", "milano": "milan", "lisboa": "lisbon", "wien": "vienna",
                "praha": "prague", "torino": "turin", "napoli": "naples", "genova": "genoa", "firenze": "florence",
                "moskva": "moscow", "kobenhavn": "copenhagen", "bruxelles": "brussels", "sao": "sao"}


def club_keys(names):
    out = set()
    for n in names:
        if not isinstance(n, str) or n in NOT_CLUBS:
            continue
        k = " ".join(CITY_ALIASES.get(t, t) for t in clubs.club_key(n).split())
        if len(k) >= 4:
            out.add(k)
    return out


def overlap(fk: set, tk: set) -> list:
    """Pairs of club keys that name the same club (one's words contained in the other's)."""
    hits = []
    for a in fk:
        sa = set(a.split())
        for b in tk:
            sb = set(b.split())
            if (sa <= sb or sb <= sa) and len(" ".join(sorted(sa & sb))) >= 4:
                hits.append((a, b))
    return hits


def main():
    rev = pd.read_csv(ROOT / "reports" / "match_review_round1.csv")  # frozen input of review round 1
    coh = pd.read_parquet(config.CLEAN / "cohort.parquet")
    panel = pd.read_parquet(config.CLEAN / "fifa_panel.parquet", columns=["player_id", "club_name"])
    tm_raw = pd.read_csv(config.RAW_TM / "players.csv")
    tm = m.prepare_tm(tm_raw)
    trf = pd.read_csv(config.RAW_TM / "transfers.csv", usecols=["player_id", "from_club_name", "to_club_name"])
    val = pd.read_csv(config.RAW_TM / "player_valuations.csv", usecols=["player_id", "current_club_name"])
    fifa = m.prepare_fifa(coh).set_index("player_id")

    fifa_clubs = panel.dropna().groupby("player_id")["club_name"].apply(lambda s: club_keys(s.unique()))
    tm_club_names = pd.concat([trf[["player_id", "from_club_name"]].rename(columns={"from_club_name": "c"}),
                               trf[["player_id", "to_club_name"]].rename(columns={"to_club_name": "c"}),
                               val.rename(columns={"current_club_name": "c"}),
                               tm_raw[["player_id", "current_club_name"]].rename(columns={"current_club_name": "c"})])
    tm_clubs = tm_club_names.dropna().groupby("player_id")["c"].apply(lambda s: club_keys(s.unique()))
    tmi = tm.set_index("player_id")
    info = coh.set_index("player_id")

    # Candidates: those in the review file, plus a name-only search (any DOB) for players without an exact-DOB candidate
    cands = rev[rev["tm_player_id"].notna()][["fifa_player_id", "tm_player_id", "candidate_type"]].copy()
    no_exact = rev.loc[rev["candidate_type"] != "same DOB", "fifa_player_id"].unique()
    extra = []
    tm_names = list(zip(tm["player_id"], tm["tm_names"]))
    for fid in no_exact:
        fn = fifa.loc[fid, "fifa_names"]
        for pid, names in tm_names:
            if m.name_score(fn, names) >= 90:
                extra.append((fid, pid, "name-only search"))
    cands = pd.concat([cands, pd.DataFrame(extra, columns=cands.columns)]).drop_duplicates(["fifa_player_id", "tm_player_id"])
    cands["tm_player_id"] = cands["tm_player_id"].astype(int)

    rows = []
    for r in cands.itertuples(index=False):
        f, t = info.loc[r.fifa_player_id], tmi.loc[r.tm_player_id]
        fk, tk = fifa_clubs.get(r.fifa_player_id, set()), tm_clubs.get(r.tm_player_id, set())
        hits = overlap(fk, tk)
        nat_ok = {f["nationality_name"]} | NATION_ALIASES.get(f["nationality_name"], set())
        nation_match = t["country_of_citizenship"] in nat_ok or t["country_of_birth"] in nat_ok
        fd = [pd.Timestamp(d) for d in str(f["dob_variants"]).split("|") if d]
        td = pd.to_datetime(t["dob"], errors="coerce")
        dob_diff = min(abs((td - d).days) for d in fd) if pd.notna(td) and fd else np.nan
        gk_ok = (f["position_group"] == "GK") == (t["position"] == "Goalkeeper") or t["position"] == "Missing"
        # DOB difference that looks like a typo: same year+month, same year+day, year off by one, or day/month swapped
        typo = False
        if pd.notna(td):
            for d in fd:
                typo |= (d.year == td.year and d.month == td.month) or (d.year == td.year and d.day == td.day) \
                        or (d.month == td.month and d.day == td.day and abs(d.year - td.year) == 1) \
                        or (d.year == td.year and d.month == td.day and d.day == td.month)
        f_first = normalise(f["long_name"]).split()[0] if normalise(f["long_name"]) else ""
        t_first = normalise(t["first_name"]) if isinstance(t["first_name"], str) else normalise(t["name"]).split()[0]
        first_match = bool(f_first) and (f_first == t_first or f_first == normalise(t["name"]).split()[0])
        rows.append({"fifa_player_id": r.fifa_player_id, "tm_player_id": r.tm_player_id, "candidate_type": r.candidate_type,
                     "fifa_name": f["long_name"], "tm_name": t["name"], "name_score": round(m.name_score(fifa.loc[r.fifa_player_id, "fifa_names"], t["tm_names"]), 1),
                     "dob_diff_days": dob_diff, "club_overlap": len(hits), "club_overlap_names": "; ".join(f"{a}={b}" for a, b in hits[:4]),
                     "nation_match": nation_match, "gk_agrees": gk_ok, "dob_typo_like": typo, "first_name_match": first_match, "fifa_nation": f["nationality_name"],
                     "tm_citizenship": t["country_of_citizenship"], "fifa_entry_club": f["club_name"], "potential": f["potential"]})
    ev = pd.DataFrame(rows)
    ev["evidence_score"] = ev["club_overlap"].clip(upper=2) * 3 + ev["nation_match"] * 2 + (ev["name_score"] >= 90) * 1 \
                           + (ev["dob_diff_days"] == 0) * 1 + ev["gk_agrees"] * 1
    ev.to_csv(ROOT / "reports" / "match_review_evidence.csv", index=False, encoding="utf-8")
    print(f"evidence rows: {len(ev):,} for {ev['fifa_player_id'].nunique()} players; name-only candidates added: {len(extra):,}")


if __name__ == "__main__":
    main()
