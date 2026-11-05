"""Name normalisation for FIFA ↔ Transfermarkt matching."""
from __future__ import annotations

import re

import pandas as pd
from unidecode import unidecode

SUFFIXES = {"jr", "jnr", "junior", "sr", "snr", "ii", "iii", "iv"}
_APOSTROPHES = re.compile(r"['’`´]")
_NON_ALNUM = re.compile(r"[^a-z0-9 ]+")
_SPACES = re.compile(r"\s+")


def normalise(name) -> str:
    """unidecode → lowercase → drop apostrophes → other punctuation to spaces →
    drop suffix tokens (jr, junior, sr, ii, iii, iv) → collapse spaces.

    "N'Golo Kanté" -> "ngolo kante";  "Vinícius Jr." -> "vinicius";  "K. Mbappé" -> "k mbappe".
    If removing suffixes would leave nothing (a player called "Júnior"), they are kept.
    """
    if name is None or (isinstance(name, float) and pd.isna(name)) or name is pd.NA:
        return ""
    s = unidecode(str(name)).lower()
    s = _APOSTROPHES.sub("", s)
    s = _NON_ALNUM.sub(" ", s)
    tokens = s.split()
    kept = [t for t in tokens if t not in SUFFIXES]
    return " ".join(kept or tokens)


def initial_surname(first, last) -> str:
    """Transfermarkt has no short-name column; build one in FIFA's style ("Kylian", "Mbappé" -> "k mbappe")."""
    f, l = normalise(first), normalise(last)
    if not f or not l:
        return ""
    return f"{f[0]} {l}"


def collapse(s: str) -> str:
    return _SPACES.sub(" ", s).strip()
