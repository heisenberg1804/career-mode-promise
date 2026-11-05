"""ClubElo snapshots: fetch once per edition date via soccerdata, cache as CSV.

Cached files live in data/raw/clubelo/clubelo_YYYY-MM-DD.csv. Once a file is
cached it is never re-downloaded, so the analysis is frozen to what we fetched.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src import config


def cache_path(date: str, cache_dir: Path = config.RAW_CLUBELO) -> Path:
    return cache_dir / f"clubelo_{date}.csv"


def fetch_snapshot(date: str, cache_dir: Path = config.RAW_CLUBELO) -> tuple[pd.DataFrame, str]:
    """Return (snapshot, source) for one 'YYYY-MM-DD' date.

    source is "cache" if read from disk, "download" if fetched now.
    Raises ConnectionError (from soccerdata) if the ClubElo API is unreachable.
    """
    path = cache_path(date, cache_dir)
    if path.exists():
        return pd.read_csv(path), "cache"

    import logging

    import soccerdata as sd  # imported lazily: it logs a lot on import

    # soccerdata configures its own logger on import; quieten it afterwards. Failures
    # still surface as the ConnectionError raised below.
    logging.getLogger("soccerdata").setLevel(logging.CRITICAL)

    # Pass a timezone-aware UTC datetime. soccerdata converts a plain
    # 'YYYY-MM-DD' string via local time, which shifts the date back one day
    # on machines east of UTC.
    when = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    elo = sd.ClubElo(data_dir=cache_dir / "_soccerdata_cache")
    df = elo.read_by_date(when).reset_index()
    df.insert(0, "snapshot_date", date)
    df["source"] = "api"
    df.to_csv(path, index=False, encoding="utf-8")
    return df, "download"


def load_cached(dates: list[str], cache_dir: Path = config.RAW_CLUBELO) -> dict[str, pd.DataFrame]:
    """Read every cached snapshot that exists for `dates` (missing ones are skipped)."""
    out = {}
    for d in dates:
        p = cache_path(d, cache_dir)
        if p.exists():
            out[d] = pd.read_csv(p)
    return out


# ---------------------------------------------------------------- mirror (Gábor 2026, Elo from ClubElo)
MIRROR_DIR = config.RAW / "club_elo_mirror"
MIRROR_SOURCE = "mirror: Kaggle adamgbor/club-football-match-data-2000-2025 (ClubElo ratings)"

# football-data.co.uk division code -> league level (single-division country codes are top flights)
DIVISION_LEVEL = {"E0": 1, "E1": 2, "E2": 3, "E3": 4, "EC": 5, "SC0": 1, "SC1": 2, "SC2": 3, "SC3": 4,
                  "D1": 1, "D2": 2, "SP1": 1, "SP2": 2, "I1": 1, "I2": 2, "F1": 1, "F2": 2,
                  "N1": 1, "B1": 1, "P1": 1, "T1": 1, "G1": 1}


def mirror_cache_path(date: str, cache_dir: Path = config.RAW_CLUBELO) -> Path:
    """Mirror snapshots use a different file name so the API retry still treats the date as missing."""
    return cache_dir / f"clubelo_mirror_{date}.csv"


def build_mirror_snapshot(date: str, ratings: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """ClubElo-format snapshot for `date` from the mirror's EloRatings (1st/15th of each month).

    Uses the latest ratings snapshot on or before `date` (clubs are those ClubElo listed on that day).
    `level` comes from the club's most frequent league division in the July–June season containing
    `date`; NaN where the club's name differs between the mirror's two files.
    """
    when = pd.Timestamp(date)
    rdate = ratings.loc[ratings["date"] <= when, "date"].max()
    snap = ratings[ratings["date"] == rdate].copy()

    start = pd.Timestamp(year=when.year if when.month >= 7 else when.year - 1, month=7, day=1)
    season = matches[(matches["MatchDate"] >= start) & (matches["MatchDate"] < start + pd.DateOffset(years=1))]
    long = pd.concat([season[["Division", "HomeTeam"]].rename(columns={"HomeTeam": "team"}),
                      season[["Division", "AwayTeam"]].rename(columns={"AwayTeam": "team"})])
    div = long.groupby("team")["Division"].agg(lambda x: x.mode().iat[0])

    snap = snap.sort_values("elo", ascending=False).reset_index(drop=True)
    out = pd.DataFrame({
        "snapshot_date": date,
        "team": snap["club"],
        "rank": snap.index + 1.0,
        "country": snap["country"],
        "level": snap["club"].map(div).map(DIVISION_LEVEL),
        "elo": snap["elo"],
        "from": pd.NaT, "to": pd.NaT,
        "league": None,
        "source": MIRROR_SOURCE,
        "rating_date": rdate.strftime("%Y-%m-%d"),
        "division": snap["club"].map(div),
    })
    out["league"] = out["country"] + "_" + out["level"].astype("Int64").astype(str).replace("<NA>", "")
    return out


def load_best_snapshots(dates: list[str], cache_dir: Path = config.RAW_CLUBELO) -> dict[str, pd.DataFrame]:
    """For each date: the API snapshot if cached, otherwise the mirror snapshot, otherwise nothing."""
    out = {}
    for d in dates:
        for p in (cache_path(d, cache_dir), mirror_cache_path(d, cache_dir)):
            if p.exists():
                out[d] = pd.read_csv(p)
                break
    return out
