"""Turn reports/match_review_evidence.csv into data/manual/tm_match_overrides.csv (one row per reviewed player).

Rules (each row's note says which applied):
  strong candidate = shares a club with the FIFA player's history AND the goalkeeper flag agrees AND either
                     (same DOB AND (nationality agrees OR name score >= 90)) or
                     (DOB difference looks like a typo AND nationality agrees AND name score >= 85)
  Also strong without a shared club: same DOB, exact name, same first name and nationality (club names written differently).
  Ties are broken by first-name agreement (twins with the same initial), then evidence score, then name score.
  1. Player has an accepted match: confirm it if strong; else correct to another strong candidate; else confirm only if
     name = 100, same DOB and nationality agree (club names written differently); else reject.
  2. No accepted match: one strong candidate -> confirm (top same-DOB candidate) or correct; several -> the best
     evidence score if it is unique; none -> reject.
  3. Twins: if two FIFA players end up with the same TM id, the one with the higher name score keeps it; the other
     falls back to his next strong candidate or reject. Equal scores -> left for manual decision (printed).
  4. A TM id already held by an auto match outside the review (exact DOB, unique name match) stays there; the
     conflicting review decision becomes a reject.
Usage: python -I scripts/match_review_evidence.py && python -I scripts/match_review_decide.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd  # noqa: E402

from src import config  # noqa: E402

REVIEWER = "Claude (principal DS review, 2026-11-05)"


def main(manual: dict | None = None):
    manual = manual or {}
    ev = pd.read_csv(ROOT / "reports" / "match_review_evidence.csv")
    rev = pd.read_csv(ROOT / "reports" / "match_review_round1.csv")  # frozen input of review round 1
    same = ev["dob_diff_days"] == 0
    ev["strong"] = ev["gk_agrees"] & (
        ((ev["club_overlap"] > 0) & same & (ev["nation_match"] | (ev["name_score"] >= 90))) |
        ((ev["club_overlap"] > 0) & ~same & ev["dob_typo_like"] & ev["nation_match"] & (ev["name_score"] >= 85)) |
        # club written differently in the two sources (e.g. Akhisar Belediyespor / Akhisarspor): exact identity otherwise
        (same & (ev["name_score"] == 100) & ev["first_name_match"] & ev["nation_match"]))
    accepted = rev[rev["currently_accepted"] == "yes"].set_index("fifa_player_id")["tm_player_id"].astype(int).to_dict()
    top_same = rev[(rev["candidate_type"] == "same DOB") & (rev["candidate_rank"] == 1)].set_index("fifa_player_id")["tm_player_id"].to_dict()
    reasons = rev.drop_duplicates("fifa_player_id").set_index("fifa_player_id")["review_reasons"].to_dict()
    out = {}
    for fid in rev["fifa_player_id"].unique():
        c = ev[ev["fifa_player_id"] == fid].sort_values(["strong", "first_name_match", "evidence_score", "name_score"], ascending=False)
        strong = c[c["strong"]]
        acc = accepted.get(fid)
        why = reasons.get(fid, "")
        if fid in manual:
            out[fid] = manual[fid]
            continue
        if acc is not None:
            row = c[c["tm_player_id"] == acc]
            if len(row) and row["strong"].iat[0]:
                out[fid] = (acc, "confirm", f"[{why}] shares club(s) {row['club_overlap_names'].iat[0]}; nationality {'agrees' if row['nation_match'].iat[0] else 'differs'}")
            elif len(strong):
                b = strong.iloc[0]
                out[fid] = (int(b.tm_player_id), "correct", f"[{why}] accepted match had no shared club; {b.tm_name} shares {b.club_overlap_names}")
            elif len(row) and row["name_score"].iat[0] == 100 and row["dob_diff_days"].iat[0] == 0 and row["nation_match"].iat[0] and row["gk_agrees"].iat[0]:
                out[fid] = (acc, "confirm", f"[{why}] same full name, DOB and nationality; club names written differently in the two sources")
            else:
                out[fid] = (None, "reject", f"[{why}] accepted match shares no club and fails name/nationality checks")
        else:
            if len(strong) == 0:
                out[fid] = (None, "reject", f"[{why}] no candidate shares a club with the player's FIFA history")
            else:
                if len(strong) > 1 and strong["first_name_match"].iat[0] == strong["first_name_match"].iat[1] and \
                        strong["evidence_score"].iat[0] == strong["evidence_score"].iat[1] and \
                        strong["name_score"].iat[0] == strong["name_score"].iat[1]:
                    out[fid] = (None, "manual", f"[{why}] {len(strong)} equally strong candidates: " + ", ".join(strong["tm_name"]))
                    continue
                b = strong.iloc[0]
                act = "confirm" if top_same.get(fid) == b.tm_player_id else "correct"
                dob = "same DOB" if b.dob_diff_days == 0 else f"DOB differs by {int(b.dob_diff_days)} days"
                clubs_txt = f"shares {b.club_overlap_names}" if b.club_overlap > 0 else "same full name, first name and DOB (club names written differently)"
                out[fid] = (int(b.tm_player_id), act, f"[{why}] {b.tm_name}: {dob}, {clubs_txt}, nationality {'agrees' if b.nation_match else 'differs'}")
    # Twins: one TM id per FIFA player
    claims = {}
    for fid, (tid, act, note) in out.items():
        if tid is not None and act in ("confirm", "correct"):
            claims.setdefault(tid, []).append(fid)
    for tid, fids in claims.items():
        if len(fids) < 2:
            continue
        sc = {f: tuple(ev[(ev.fifa_player_id == f) & (ev.tm_player_id == tid)][["first_name_match", "name_score"]].max()) for f in fids}
        order = sorted(fids, key=lambda f: sc[f], reverse=True)
        if sc[order[0]] == sc[order[1]]:
            for f in fids:
                out[f] = (None, "manual", f"twin conflict on TM {tid}, equal name scores")
            continue
        for f in order[1:]:
            alt = ev[(ev.fifa_player_id == f) & ev["strong"] & (ev.tm_player_id != tid)].sort_values("evidence_score", ascending=False)
            if len(alt):
                b = alt.iloc[0]
                out[f] = (int(b.tm_player_id), "correct", f"twin of the player who keeps TM {tid}; own record {b.tm_name} shares {b.club_overlap_names}")
            else:
                out[f] = (None, "reject", f"twin: TM {tid} is his brother (first name / name score); no own Transfermarkt record found")
    # 4. A TM id already held by an auto match outside the review (exact DOB, unique best name match) stays with it
    from src import matching as mm
    coh = pd.read_parquet(config.CLEAN / "cohort.parquet")
    tm = mm.prepare_tm(pd.read_csv(config.RAW_TM / "players.csv"))
    fifa = mm.prepare_fifa(coh)
    best = mm.best_matches(fifa, mm.score_candidates(fifa, tm))
    auto = best[(best["match_class"] == "auto") & ~best["fifa_player_id"].isin(list(out))]
    held = dict(zip(auto["tm_player_id"].astype(int), auto["fifa_player_id"]))
    names = coh.set_index("player_id")["long_name"]
    for fid, (tid, act, note) in list(out.items()):
        if tid is not None and act in ("confirm", "correct") and int(tid) in held:
            other = held[int(tid)]
            out[fid] = (None, "reject", f"TM {int(tid)} is {names[other]} (FIFA {other}, auto match on exact DOB and name); "
                                        f"no separate Transfermarkt record for this player. Was: {note[:120]}")
    o = pd.DataFrame([{"fifa_player_id": f, "tm_player_id": t, "action": a, "reviewer": REVIEWER, "note": n}
                      for f, (t, a, n) in out.items()])
    o["tm_player_id"] = o["tm_player_id"].astype("Int64")
    man = o[o["action"] == "manual"]
    o[o["action"] != "manual"].to_csv(config.TM_MATCH_OVERRIDES, index=False, encoding="utf-8")
    print(o["action"].value_counts().to_dict())
    if len(man):
        print("MANUAL:"); print(man.to_string())
    return o


if __name__ == "__main__":
    main()
