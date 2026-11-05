"""FIFA ↔ Transfermarkt matching (CLAUDE.md section 8, notebook 02).

Rule: date of birth must match exactly (any of the player's FIFA DOB variants). Among same-DOB
Transfermarkt candidates, score names with rapidfuzz token_set_ratio and take the best.
Accept if >= 85; 70–84 and ties go to human review; every potential-85+ player is reviewed.
"""
from __future__ import annotations

import pandas as pd
from rapidfuzz import fuzz

from src import config
from src.names import initial_surname, normalise

OVERRIDE_COLUMNS = ["fifa_player_id", "tm_player_id", "action", "reviewer", "note"]
OVERRIDE_ACTIONS = {"confirm", "correct", "reject"}


def prepare_fifa(cohort: pd.DataFrame) -> pd.DataFrame:
    f = cohort[["player_id", "long_name", "short_name", "dob", "dob_variants"]].copy()
    f["fifa_names"] = [sorted({n for n in (normalise(a), normalise(b)) if n})
                       for a, b in zip(f["long_name"], f["short_name"])]
    f["dob_list"] = f["dob_variants"].fillna("").str.split("|")
    return f


def prepare_tm(players: pd.DataFrame) -> pd.DataFrame:
    t = players.copy()
    t["dob"] = pd.to_datetime(t["date_of_birth"], errors="coerce").dt.strftime("%Y-%m-%d")
    full = t["name"].map(normalise)
    first_last = (t["first_name"].fillna("") + " " + t["last_name"].fillna("")).map(normalise)
    short = [initial_surname(a, b) for a, b in zip(t["first_name"], t["last_name"])]
    t["tm_names"] = [sorted({n for n in names if n}) for names in zip(full, first_last, short)]
    t["tm_name_norm"] = full
    return t


def name_score(fifa_names: list[str], tm_names: list[str]) -> float:
    """Best token_set_ratio over every FIFA name × Transfermarkt name pair."""
    if not fifa_names or not tm_names:
        return 0.0
    return max(fuzz.token_set_ratio(a, b) for a in fifa_names for b in tm_names)


def score_candidates(fifa: pd.DataFrame, tm: pd.DataFrame) -> pd.DataFrame:
    """Every (FIFA player, same-DOB TM player) pair with its name score."""
    by_dob = tm.dropna(subset=["dob"]).groupby("dob")
    groups = {d: g for d, g in by_dob}
    rows = []
    for r in fifa.itertuples(index=False):
        seen = set()
        for d in r.dob_list:
            g = groups.get(d)
            if g is None:
                continue
            for c in g.itertuples(index=False):
                if c.player_id in seen:
                    continue
                seen.add(c.player_id)
                rows.append((r.player_id, c.player_id, d, name_score(r.fifa_names, c.tm_names)))
    return pd.DataFrame(rows, columns=["fifa_player_id", "tm_player_id", "matched_dob", "score"])


def best_matches(fifa: pd.DataFrame, cands: pd.DataFrame) -> pd.DataFrame:
    """One row per FIFA player: best candidate, runner-up score, n candidates, raw match class."""
    c = cands.sort_values(["fifa_player_id", "score"], ascending=[True, False])
    c["rank"] = c.groupby("fifa_player_id").cumcount() + 1
    top = c[c["rank"] == 1].set_index("fifa_player_id")
    second = c[c["rank"] == 2].set_index("fifa_player_id")["score"].rename("second_score")
    n = c.groupby("fifa_player_id").size().rename("n_dob_candidates")
    out = (fifa[["player_id"]].rename(columns={"player_id": "fifa_player_id"})
           .join(top[["tm_player_id", "matched_dob", "score"]], on="fifa_player_id")
           .join(second, on="fifa_player_id").join(n, on="fifa_player_id"))
    out["n_dob_candidates"] = out["n_dob_candidates"].fillna(0).astype(int)
    tie = out["second_score"].notna() & (out["second_score"] == out["score"])
    out["match_class"] = "auto"
    out.loc[out["score"] < config.MATCH_ACCEPT, "match_class"] = "review_low_score"
    out.loc[out["score"] < config.MATCH_REVIEW_LOW, "match_class"] = "no_match_below_70"
    out.loc[tie & (out["score"] >= config.MATCH_REVIEW_LOW), "match_class"] = "review_tie"
    out.loc[out["n_dob_candidates"] == 0, "match_class"] = "no_dob_candidate"
    out["tm_player_id"] = out["tm_player_id"].astype("Int64")
    return out


def near_dob_suggestions(fifa_rows: pd.DataFrame, tm: pd.DataFrame, window_days: int = 366,
                         min_score: float = config.MATCH_ACCEPT, limit: int = 3) -> pd.DataFrame:
    """For players with no exact-DOB match: Transfermarkt players born within `window_days`
    of any FIFA DOB variant whose name scores >= min_score.

    These catch DOB typos in one source (e.g. 2 Nov vs 22 Nov). Suggestions for a human only;
    they are never accepted automatically (the match rule requires an exact DOB).
    """
    tm_dob = pd.to_datetime(tm["dob"], errors="coerce")
    rows = []
    for r in fifa_rows.itertuples(index=False):
        dobs = pd.to_datetime(pd.Series([d for d in r.dob_list if d]), errors="coerce").dropna()
        if dobs.empty:
            continue
        diff = pd.concat([(tm_dob - d).abs().dt.days for d in dobs], axis=1).min(axis=1)
        near = tm[diff <= window_days]
        scored = [(c.player_id, name_score(r.fifa_names, c.tm_names), int(diff[i]))
                  for i, c in zip(near.index, near.itertuples(index=False))]
        scored = [s for s in scored if s[1] >= min_score]
        for pid, score, days in sorted(scored, key=lambda s: (-s[1], s[2]))[:limit]:
            rows.append((r.player_id, pid, score, days))
    return pd.DataFrame(rows, columns=["fifa_player_id", "tm_player_id", "score", "dob_diff_days"])


def load_overrides(path=config.TM_MATCH_OVERRIDES) -> pd.DataFrame:
    """Read the manual override file, creating it (header only) if missing."""
    if not path.exists():
        pd.DataFrame(columns=OVERRIDE_COLUMNS).to_csv(path, index=False)
    ov = pd.read_csv(path, dtype={"note": "str", "reviewer": "str", "action": "str"})
    missing = [c for c in OVERRIDE_COLUMNS if c not in ov.columns]
    if missing:
        raise ValueError(f"{path.name} is missing columns {missing}")
    ov["action"] = ov["action"].str.strip().str.lower()
    ov["fifa_player_id"] = ov["fifa_player_id"].astype("Int64")
    ov["tm_player_id"] = ov["tm_player_id"].astype("Int64")
    return ov


def validate_overrides(ov: pd.DataFrame, cohort_ids: set, tm_ids: set) -> list[str]:
    """Return a list of problems (empty if the file is valid)."""
    problems = []
    bad_action = ov[~ov["action"].isin(OVERRIDE_ACTIONS)]
    if len(bad_action):
        problems.append(f"unknown action in rows {bad_action.index.tolist()} (use confirm/correct/reject)")
    dup = ov[ov["fifa_player_id"].duplicated(keep=False)]
    if len(dup):
        problems.append(f"fifa_player_id listed more than once: {sorted(dup['fifa_player_id'].unique().tolist())}")
    not_cohort = ov[~ov["fifa_player_id"].isin(cohort_ids)]
    if len(not_cohort):
        problems.append(f"fifa_player_id not in cohort: {not_cohort['fifa_player_id'].tolist()}")
    needs_tm = ov[ov["action"].isin({"confirm", "correct"})]
    no_tm = needs_tm[needs_tm["tm_player_id"].isna() | ~needs_tm["tm_player_id"].isin(tm_ids)]
    if len(no_tm):
        problems.append(f"confirm/correct rows without a valid tm_player_id: {no_tm['fifa_player_id'].tolist()}")
    return problems
