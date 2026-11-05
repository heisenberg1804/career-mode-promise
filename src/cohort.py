"""Edition labels, positions, cohort entry and outcome logic (CLAUDE.md section 6)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src import config

# FIFA per-position rating strings ("89+3"), kept in the panel, dropped from the cohort.
POSITION_RATING_COLS = ["ls", "st", "rs", "lw", "lf", "cf", "rf", "rw", "lam", "cam", "ram",
                        "lm", "lcm", "cm", "rcm", "rm", "lwb", "ldm", "cdm", "rdm", "rwb",
                        "lb", "lcb", "cb", "rcb", "rb", "gk"]


def add_edition_and_position(df: pd.DataFrame) -> pd.DataFrame:
    """Edition, edition label, edition date, primary position, position group."""
    out = df.copy()
    out["edition"] = out["fifa_version"].astype(int)
    out["fifa_update"] = out["fifa_update"].astype(int)
    out["edition_label"] = out["edition"].map(config.EDITION_LABELS)
    out["edition_date"] = pd.to_datetime(out["update_as_of"])
    out["dob"] = pd.to_datetime(out["dob"])
    out["primary_position"] = out["player_positions"].str.split(",").str[0].str.strip()
    out["position_group"] = out["primary_position"].map(config.POSITION_TO_GROUP)
    out["is_gk"] = out["position_group"].eq("GK")
    return out


def potential_band(potential: pd.Series) -> pd.Series:
    """Potential band label ('<70', '70–74', ...) as an ordered categorical."""
    edges = [-np.inf] + [hi for _, hi in config.POTENTIAL_BANDS.values()]
    return pd.cut(potential, bins=edges, labels=config.BAND_ORDER, right=True, ordered=True)


def first_entries(panel: pd.DataFrame, editions: list[int],
                  max_age: int = config.MAX_ENTRY_AGE) -> pd.DataFrame:
    """One row per player: his first edition within `editions` in which age <= max_age."""
    eligible = panel[panel["edition"].isin(editions) & (panel["age"] <= max_age)]
    return (eligible.sort_values(["player_id", "edition"])
                    .drop_duplicates("player_id", keep="first")
                    .reset_index(drop=True))


def _status(peak: pd.Series, potential: pd.Series) -> pd.Series:
    return pd.Series(np.select([peak.isna(), peak >= potential],
                               [config.STATUS_VANISHED, config.STATUS_REACHED],
                               default=config.STATUS_FELL_SHORT), index=peak.index)


def add_outcomes(entries: pd.DataFrame, panel: pd.DataFrame,
                 within_n: int = config.PEAK_WITHIN_N) -> pd.DataFrame:
    """Peak later rating, peak within N editions, status, gap, already-peaked flag.

    "Later" means any edition strictly after the entry edition. "Within N" means
    editions entry+1 .. entry+N by edition number (a skipped edition does not
    extend the window). Ties for the peak take the earliest edition.
    """
    e = entries.copy()
    hist = panel[["player_id", "edition", "overall"]].merge(
        e[["player_id", "edition"]].rename(columns={"edition": "entry_edition"}), on="player_id")
    later = hist[hist["edition"] > hist["entry_edition"]]
    within = later[later["edition"] <= later["entry_edition"] + within_n]

    def peak(h: pd.DataFrame, prefix: str) -> pd.DataFrame:
        idx = h.sort_values(["player_id", "overall", "edition"], ascending=[True, False, True]) \
               .drop_duplicates("player_id")
        return idx.set_index("player_id")[["overall", "edition"]].rename(
            columns={"overall": f"{prefix}", "edition": f"{prefix}_edition"})

    pk = peak(later, "peak_later")
    pw = peak(within, f"peak_within_{within_n}")
    n_later = later.groupby("player_id").size().rename("n_later_editions")
    last_seen = panel.groupby("player_id")["edition"].max().rename("last_edition_seen")

    e = (e.join(pk, on="player_id").join(pw, on="player_id")
          .join(n_later, on="player_id").join(last_seen, on="player_id"))
    e["n_later_editions"] = e["n_later_editions"].fillna(0).astype(int)
    for c in ["peak_later", "peak_later_edition", f"peak_within_{within_n}",
              f"peak_within_{within_n}_edition"]:
        e[c] = e[c].astype("Int64")

    e["entry_edition"] = e["edition"]
    e["entry_edition_label"] = e["edition_label"]
    e["entry_date"] = e["edition_date"]
    e["potential_band"] = potential_band(e["potential"])
    e["is_wonderkid"] = e["potential"] >= config.WONDERKID_POTENTIAL
    e["already_peaked"] = e["overall"] == e["potential"]

    e["status"] = _status(e["peak_later"].astype(float), e["potential"])
    e["gap"] = e["potential"] - e["peak_later"]
    e[f"status_within_{within_n}"] = _status(e[f"peak_within_{within_n}"].astype(float), e["potential"])
    e[f"gap_within_{within_n}"] = e["potential"] - e[f"peak_within_{within_n}"]
    return e


def dob_variants(panel: pd.DataFrame) -> pd.Series:
    """Every distinct DOB a player has across editions, as 'YYYY-MM-DD|YYYY-MM-DD'."""
    return (panel.dropna(subset=["dob"])
                 .assign(d=lambda x: x["dob"].dt.strftime("%Y-%m-%d"))
                 .groupby("player_id")["d"].agg(lambda s: "|".join(sorted(set(s))))
                 .rename("dob_variants"))


def add_league_context(panel: pd.DataFrame, teams: pd.DataFrame) -> pd.DataFrame:
    """Add `league_name_edition` (the league's name in that edition) and `league_country`.

    FIFA's `league_name` is each club's FC 24 league repeated across all editions, so it is wrong
    for clubs that moved division. `league_id` is correct per edition; its name is taken from FC 24
    rows (where the label is correct by construction), else from config.LEAGUE_ID_MANUAL.
    `league_country` is the club's league country from male_teams (`nationality_name`).
    """
    out = panel.copy()
    fc24 = (out[out["edition"] == max(config.EDITIONS)].dropna(subset=["league_id"])
            .groupby("league_id")["league_name"].agg(lambda s: s.mode().iat[0]))
    names = {**fc24.to_dict(), **{float(k): v for k, v in config.LEAGUE_ID_MANUAL.items()}}
    out["league_name_edition"] = out["league_id"].map(names)
    t = teams.assign(edition=teams["fifa_version"].astype(int))[["team_id", "edition", "nationality_name"]] \
             .rename(columns={"team_id": "club_team_id", "nationality_name": "league_country"})
    t = t.drop_duplicates(["club_team_id", "edition"])
    return out.merge(t, on=["club_team_id", "edition"], how="left")
