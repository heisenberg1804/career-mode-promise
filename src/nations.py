"""Nation helpers: FIFA nationality names -> FIFA ranking key, ISO3, confederation."""
from __future__ import annotations

import pandas as pd
import pycountry

from src import config

# Ranking trigram aliases (same team, two codes over time)
ACRONYM_ALIASES = {"LIB": "LBN"}

# Home nations share the UK on a world map (decision in DECISIONS.md)
UK_HOME_NATIONS = {"England", "Scotland", "Wales", "Northern Ireland"}

# FIFA names pycountry can't resolve exactly. Each was checked by hand.
ISO3_MANUAL = {
    "England": "GBR", "Scotland": "GBR", "Wales": "GBR", "Northern Ireland": "GBR",
    "Korea Republic": "KOR", "Korea DPR": "PRK", "China PR": "CHN", "Chinese Taipei": "TWN",
    "Congo DR": "COD", "Congo": "COG", "Côte d'Ivoire": "CIV", "Republic of Ireland": "IRL",
    "Kosovo": "XKX", "Cape Verde Islands": "CPV", "Curacao": "CUW", "Guinea Bissau": "GNB",
    "Iran": "IRN", "Russia": "RUS", "Syria": "SYR", "Tanzania": "TZA", "Venezuela": "VEN",
    "Bolivia": "BOL", "Moldova": "MDA", "North Macedonia": "MKD", "FYR Macedonia": "MKD",
    "Czech Republic": "CZE", "United States": "USA", "Turkey": "TUR", "Vietnam": "VNM",
    "Laos": "LAO", "São Tomé e Príncipe": "STP", "Saint Kitts and Nevis": "KNA",
    "Saint Lucia": "LCA", "Saint Vincent and the Grenadines": "VCT", "Palestine": "PSE",
    "Gambia": "GMB", "Holland": "NLD", "Netherlands": "NLD", "Bosnia and Herzegovina": "BIH",
    "Antigua and Barbuda": "ATG", "Trinidad and Tobago": "TTO", "Brunei Darussalam": "BRN",
    "Macau": "MAC", "Hong Kong": "HKG", "Kyrgyzstan": "KGZ", "Swaziland": "SWZ", "Eswatini": "SWZ",
}

TM_CONTINENT_TO_CONFED = {"europa": "UEFA", "afrika": "CAF", "asien": "AFC"}  # "amerika" is ambiguous


def iso3(name: str) -> tuple[str | None, str]:
    """Return (ISO3, method). method is 'manual', 'exact' or 'unresolved' (never a fuzzy guess)."""
    if name in ISO3_MANUAL:
        return ISO3_MANUAL[name], "manual"
    try:
        return pycountry.countries.lookup(name).alpha_3, "exact"
    except LookupError:
        return None, "unresolved"


def ranking_semester_date(year: int, semester: int) -> pd.Timestamp:
    """Semester 1 -> 30 June, semester 2 -> 31 December (decision by Sahil, DECISIONS.md)."""
    return pd.Timestamp(year=int(year), month=6, day=30) if int(semester) == 1 else \
        pd.Timestamp(year=int(year), month=12, day=31)
