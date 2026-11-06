"""Verify data/manual/club_name_overrides.csv against the mirror's own match data.

1. Trajectory test: for each overridden ClubElo name, find the football-data team (Matches.csv) whose pre-match Elo
   follows that club's rating series most closely (median absolute difference). A near-zero difference with a
   recognisable team name confirms the mapping.
2. Results test (for names with no match-Elo link, e.g. "Sverdlovsk"): correlate the club's Elo change between
   snapshots with a candidate team's results (win +1, draw 0, loss -1) in the same interval, against every other team
   in the league as a placebo.
Usage: python -I scripts/club_override_evidence.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src import clubelo, config  # noqa: E402

COUNTRY_DIV = {"BEL": ["B1"], "DEN": ["DEN"], "ENG": ["E0", "E1"], "ESP": ["SP1", "SP2"], "FIN": ["FIN"], "FRA": ["F1", "F2"],
               "GER": ["D1", "D2"], "NED": ["N1"], "NOR": ["NOR"], "POL": ["POL"], "POR": ["P1"], "RUS": ["RUS"],
               "SWE": ["SWE"], "TUR": ["T1"]}


def main():
    ov = pd.read_csv(config.CLUB_NAME_OVERRIDES)
    er = pd.read_csv(clubelo.MIRROR_DIR / "EloRatings.csv", parse_dates=["date"])
    er = er[er["date"].between("2013-07-01", "2018-12-31")]
    mt = pd.read_csv(clubelo.MIRROR_DIR / "Matches.csv", parse_dates=["MatchDate"],
                     usecols=["Division", "MatchDate", "HomeTeam", "AwayTeam", "HomeElo", "AwayElo", "FTResult"])
    mt = mt[mt["MatchDate"].between("2013-07-01", "2018-12-31")]
    long = pd.concat([
        mt.assign(team=mt["HomeTeam"], elo=mt["HomeElo"], res=mt["FTResult"].map({"H": 1, "D": 0, "A": -1}))[["Division", "MatchDate", "team", "elo", "res"]],
        mt.assign(team=mt["AwayTeam"], elo=mt["AwayElo"], res=mt["FTResult"].map({"H": -1, "D": 0, "A": 1}))[["Division", "MatchDate", "team", "elo", "res"]],
    ])
    rows = []
    for o in ov[ov["status"] == "mapped"].itertuples():
        s = er[(er["club"] == o.clubelo_club) & (er["country"] == o.clubelo_country)].sort_values("date")
        divs = COUNTRY_DIV.get(o.clubelo_country, [])
        lg = long[long["Division"].isin(divs)]
        # 1. trajectory test
        best = (None, np.nan)
        for team, g in lg.dropna(subset=["elo"]).groupby("team"):
            x = pd.merge_asof(g.sort_values("MatchDate"), s[["date", "elo"]].rename(columns={"elo": "snap"}),
                              left_on="MatchDate", right_on="date", direction="backward").dropna(subset=["snap"])
            if len(x) >= 10:
                d = (x["elo"] - x["snap"]).abs().median()
                if np.isnan(best[1]) or d < best[1]:
                    best = (team, d)
        # 2. results test: Elo change per snapshot interval vs each team's results in that interval
        s = s.assign(delta=s["elo"].diff(), start=s["date"].shift())
        res_corr = {}
        for team, g in lg.groupby("team"):
            pts = [g[(g["MatchDate"] > a) & (g["MatchDate"] <= b)]["res"].sum() if pd.notna(a) else np.nan
                   for a, b in zip(s["start"], s["date"])]
            v = pd.DataFrame({"d": s["delta"].values, "p": pts}).dropna()
            v = v[(v["p"] != 0) | (v["d"].abs() > 0)]
            if len(v) >= 15:
                res_corr[team] = v["d"].corr(v["p"])
        rc = pd.Series(res_corr).sort_values(ascending=False)
        rows.append({"fifa_club": o.fifa_club, "clubelo_club": o.clubelo_club, "country": o.clubelo_country,
                     "trajectory_match_team": best[0], "trajectory_median_abs_diff": round(best[1], 1) if pd.notna(best[1]) else None,
                     "results_best_team": rc.index[0] if len(rc) else None, "results_best_corr": round(rc.iloc[0], 2) if len(rc) else None,
                     "results_second_corr": round(rc.iloc[1], 2) if len(rc) > 1 else None})
    out = pd.DataFrame(rows)
    out.to_csv(ROOT / "reports" / "club_override_evidence.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 220)
    print(out.to_string())


if __name__ == "__main__":
    main()
