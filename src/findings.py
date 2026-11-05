"""outputs/findings.json: every number used in a chart title, caption or website text.

Notebooks call `update(section, values)`; a section is replaced as a whole, other sections are kept,
so notebook 05 and the export notebooks can each own their sections.
Formatting follows CLAUDE.md §9.1: shares as whole percentages, gaps to 1 decimal, money in € millions to 1 decimal.
"""
from __future__ import annotations

import json
import math
from datetime import datetime

import numpy as np
import pandas as pd

from src import config


def pct(x) -> int | None:
    """Fraction -> whole percentage."""
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else int(round(float(x) * 100))


def gap1(x) -> float | None:
    return None if x is None or pd.isna(x) else round(float(x), 1)


def eur_m(x) -> float | None:
    return None if x is None or pd.isna(x) else round(float(x) / 1e6, 1)


def _clean(v):
    if isinstance(v, dict):
        return {str(k): _clean(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_clean(x) for x in v]
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return None if math.isnan(float(v)) else float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if v is pd.NA or v is pd.NaT:
        return None
    if isinstance(v, (pd.Timestamp, datetime)):
        return v.strftime("%Y-%m-%d")
    return v


def load() -> dict:
    if config.FINDINGS.exists():
        return json.loads(config.FINDINGS.read_text(encoding="utf-8"))
    return {}


def update(section: str, values: dict, source_notebook: str) -> None:
    data = load()
    data[section] = _clean(values)
    meta = data.setdefault("_meta", {})
    meta.setdefault("sections", {})[section] = {"notebook": source_notebook,
                                                "updated": datetime.now().strftime("%Y-%m-%d %H:%M")}
    config.FINDINGS.parent.mkdir(parents=True, exist_ok=True)
    config.FINDINGS.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
