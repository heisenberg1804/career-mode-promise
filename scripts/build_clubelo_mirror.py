"""Build ClubElo-format snapshots for the four cohort entry dates from the Kaggle mirror.

Usage: python -I scripts/build_clubelo_mirror.py
Writes data/raw/clubelo/clubelo_mirror_YYYY-MM-DD.csv and prints QA for each snapshot.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd  # noqa: E402

from src import config, clubelo  # noqa: E402

ENTRY_DATES = [config.EXPECTED_EDITION_DATES[e] for e in config.COHORT_EDITIONS]

ratings = pd.read_csv(clubelo.MIRROR_DIR / "EloRatings.csv", parse_dates=["date"])
matches = pd.read_csv(clubelo.MIRROR_DIR / "Matches.csv", parse_dates=["MatchDate"],
                      usecols=["Division", "MatchDate", "HomeTeam", "AwayTeam", "HomeElo", "AwayElo"])

for d in ENTRY_DATES:
    snap = clubelo.build_mirror_snapshot(d, ratings, matches)
    when = pd.Timestamp(d)
    # QA: compare with each club's pre-match Elo in its last match before the entry date
    long = pd.concat([matches[["MatchDate", "HomeTeam", "HomeElo"]].set_axis(["date", "team", "elo"], axis=1),
                      matches[["MatchDate", "AwayTeam", "AwayElo"]].set_axis(["date", "team", "elo"], axis=1)])
    last = (long[(long["date"] < when) & (long["date"] >= when - pd.Timedelta(days=60))].dropna()
            .sort_values("date").drop_duplicates("team", keep="last").set_index("team")["elo"])
    cmp = snap.set_index("team")["elo"].to_frame("snapshot").join(last.rename("last_match"), how="inner")
    diff = (cmp["snapshot"] - cmp["last_match"]).abs()
    checks = {
        "clubs": len(snap), "duplicate clubs": int(snap["team"].duplicated().sum()),
        "countries": snap["country"].nunique(), "rating date": snap["rating_date"].iat[0],
        "level known %": round(snap["level"].notna().mean() * 100, 1),
        "vs last match: clubs": len(cmp), "median |diff|": round(diff.median(), 1), "max |diff|": round(diff.max(), 1),
    }
    print(d, checks)
    print("   top 10:", ", ".join(f"{t} {e:.0f}" for t, e in snap.head(10)[["team", "elo"]].itertuples(index=False)))
    assert checks["duplicate clubs"] == 0 and checks["clubs"] >= 300, "snapshot failed QA"
    snap.to_csv(clubelo.mirror_cache_path(d), index=False, encoding="utf-8")
print("saved to", config.RAW_CLUBELO.relative_to(config.ROOT))
