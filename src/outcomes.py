"""Latest-club tier (chart 14 steps; also featured-five pick #4). Rule recorded in DECISIONS.md."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src import config

TIER_BIG5 = "Big-5"
TIER_EURO_TOP = "Other European top flight"
TIER_OTHER = "Other or lower league"
TIER_OUTSIDE = "Outside Europe"
TIER_NONE = "No current club"
TIER_UNMATCHED = "Not in Transfermarkt"
TIER_ORDER = [TIER_BIG5, TIER_EURO_TOP, TIER_OTHER, TIER_OUTSIDE, TIER_NONE, TIER_UNMATCHED]

# Leagues Transfermarkt covers outside its competitions table
EXTRA_OUTSIDE_EUROPE = {"COL1"}


def latest_club_tier(df: pd.DataFrame, competitions: pd.DataFrame, current_season: int) -> pd.Series:
    """Tier of each player's latest club.

    1. Not matched to Transfermarkt -> "Not in Transfermarkt".
    2. Latest transfer to "Retired" or "Without Club" -> "No current club".
    3. Active in a Transfermarkt-covered league this season (`tm_last_season == current_season`):
       Big-5 competition -> "Big-5"; other European league -> "Other European top flight";
       non-European league -> "Outside Europe".
    4. Otherwise (left the covered leagues: lower tier or an uncovered country) -> "Other or lower league".
    """
    conf = competitions.set_index("competition_id")["confederation"]
    comp = df["tm_current_club_competition_id"]
    is_europe = comp.map(conf).eq("europa")
    is_outside = comp.map(conf).isin(["amerika", "asien", "afrika"]) | comp.isin(EXTRA_OUTSIDE_EUROPE)
    matched = df["tm_player_id"].notna()
    no_club = df["latest_transfer_to_club"].isin(["Retired", "Without Club"])
    active = df["tm_last_season"] == current_season
    tier = np.select(
        [~matched, no_club, active & comp.isin(config.BIG5_COMPETITIONS), active & is_europe, active & is_outside],
        [TIER_UNMATCHED, TIER_NONE, TIER_BIG5, TIER_EURO_TOP, TIER_OUTSIDE],
        default=TIER_OTHER)
    return pd.Series(tier, index=df.index)
