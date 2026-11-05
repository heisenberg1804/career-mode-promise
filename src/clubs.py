"""FIFA club ↔ ClubElo club mapping (notebook 03)."""
from __future__ import annotations

import re

import pandas as pd
from rapidfuzz import fuzz

from src.names import normalise

# FIFA league country -> ClubElo country code (all of Europe ClubElo rates; the mirror has a subset)
CLUBELO_COUNTRY = {
    "England": "ENG", "Scotland": "SCO", "Wales": "WAL", "Northern Ireland": "NIR", "Republic of Ireland": "IRL",
    "Spain": "ESP", "Italy": "ITA", "France": "FRA", "Germany": "GER", "Netherlands": "NED", "Portugal": "POR",
    "Belgium": "BEL", "Turkey": "TUR", "Russia": "RUS", "Greece": "GRE", "Austria": "AUT", "Switzerland": "SUI",
    "Denmark": "DEN", "Sweden": "SWE", "Norway": "NOR", "Poland": "POL", "Romania": "ROM", "Ukraine": "UKR",
    "Czech Republic": "CZE", "Croatia": "CRO", "Finland": "FIN", "Cyprus": "CYP", "Israel": "ISR", "Serbia": "SRB",
    "Hungary": "HUN", "Bulgaria": "BUL", "Slovakia": "SVK", "Slovenia": "SVN",
}
EUROPEAN_LEAGUE_COUNTRIES = set(CLUBELO_COUNTRY)

# Reserve / B / youth sides: ClubElo does not rate them, so never map them to the first team.
RESERVE_PATTERN = re.compile(r"(\bB\b|\bII\b|\bCastilla\b|\bJong\b|\bU-?2[13]\b|\bU-?19\b|\bAtl[eè]tic\b"
                             r"|\bSub-?2\d\b|\bReserves?\b)", re.IGNORECASE)
# "Willem II" is a first team, not a reserve side.
RESERVE_EXCEPTIONS = {"Willem II"}
# Spanish B sides named "<club> Atlético" / "<club> Athletic" (but not "Atlético Madrid", "Athletic Club")
RESERVE_SUFFIX = re.compile(r"^\S.*\s(Atl[eé]tico|Athletic)$")
SPAIN_B_SIDES = {"Sevilla Atlético", "Bilbao Athletic"}

_STOP = {"fc", "cf", "afc", "sc", "ac", "as", "ss", "us", "ssc", "club", "de", "sv", "vfl", "vfb", "tsg", "rc",
         "cd", "ud", "sd", "ca", "rcd", "sk", "fk", "if", "bk", "kv", "krc", "rsc", "ogc", "losc", "1", "04", "05",
         "1899", "1846", "1860", "fsv", "spvgg", "bv", "hsc", "sco", "esbjerg_", "calcio", "football", "futbol",
         "the", "of", "and", "fk.", "aik_", "cp", "sad", "cfc", "jk"}
_EXPAND = {"man": "manchester", "ath": "atletico", "utd": "united", "nottm": "nottingham", "weds": "wednesday",
           "brom": "bromwich", "mgladbach": "monchengladbach", "ein": "eintracht", "sp": "sporting",
           "sg": "saint germain", "st": "saint", "dyn": "dynamo"}


def is_reserve(name: str) -> bool:
    if not name or name in RESERVE_EXCEPTIONS:
        return False
    return bool(RESERVE_PATTERN.search(name)) or name in SPAIN_B_SIDES


def club_key(name: str) -> str:
    """Normalised club name for fuzzy matching: expand ClubElo abbreviations, drop legal-form tokens."""
    toks = [_EXPAND.get(t, t) for t in normalise(name).split()]
    kept = [t for t in toks if t not in _STOP]
    return " ".join(kept or toks)


def score(a: str, b: str) -> float:
    """Mean of token_set and token_sort ratios: token_set alone scores 100 for any subset
    ("madrid" vs "atletico madrid"), token_sort penalises the extra words."""
    ka, kb = club_key(a), club_key(b)
    return (fuzz.token_set_ratio(ka, kb) + fuzz.token_sort_ratio(ka, kb)) / 2


def subset_candidates(fifa_name: str, elo_names: list[str]) -> list[str]:
    """ClubElo names whose (expanded) words all appear in the FIFA name, e.g. "West Brom" in
    "West Bromwich Albion", "Man United" in "Manchester United"."""
    f = set(club_key(fifa_name).split())
    return [t for t in elo_names if set(club_key(t).split()) <= f]


def resolve(fifa_name: str, elo_names: list[str], fuzzy_accept: float = 90, margin: float = 5):
    """Return (clubelo_team or None, method, score, n_subset).

    1. Exactly one subset candidate -> 'subset'. Several -> the one with the most words if unique,
       else 'ambiguous'.
    2. No subset candidate -> fuzzy best if score >= fuzzy_accept and ahead of the runner-up by
       >= margin -> 'fuzzy'; else 'unmapped'.
    """
    subs = subset_candidates(fifa_name, elo_names)
    if len(subs) == 1:
        return subs[0], "subset", score(fifa_name, subs[0]), 1
    if len(subs) > 1:
        lens = sorted(((len(club_key(t).split()), t) for t in subs), reverse=True)
        if lens[0][0] > lens[1][0]:
            return lens[0][1], "subset", score(fifa_name, lens[0][1]), len(subs)
        return None, "ambiguous", None, len(subs)
    scored = sorted(((score(fifa_name, t), t) for t in elo_names), reverse=True)
    if scored and scored[0][0] >= fuzzy_accept and (len(scored) == 1 or scored[0][0] - scored[1][0] >= margin):
        return scored[0][1], "fuzzy", scored[0][0], 0
    return None, "unmapped", (scored[0][0] if scored else None), 0


def best_club_matches(fifa_clubs: pd.DataFrame, elo_names: pd.DataFrame) -> pd.DataFrame:
    """fifa_clubs: club_team_id, club_name, clubelo_country. elo_names: team, country.

    Returns one row per FIFA club with the best and second-best ClubElo candidate in the same country.
    """
    by_country = {c: g["team"].tolist() for c, g in elo_names.groupby("country")}
    rows = []
    for r in fifa_clubs.itertuples(index=False):
        cands = by_country.get(r.clubelo_country, [])
        scored = sorted(((score(r.club_name, t), t) for t in cands), reverse=True)
        best = scored[0] if scored else (None, None)
        second = scored[1][0] if len(scored) > 1 else None
        rows.append((r.club_team_id, best[1], best[0], second))
    return pd.DataFrame(rows, columns=["club_team_id", "clubelo_candidate", "match_score", "second_score"])
