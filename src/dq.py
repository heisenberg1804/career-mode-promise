"""Helpers for reports/data_quality.md.

Each notebook owns one section of the report, fenced by HTML comment markers.
Re-running a notebook replaces its own section instead of appending a
duplicate, so the report always reflects the latest run of every notebook.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from src import config

_HEADER = "# Data quality log\n\nOne section per notebook, rewritten each time that notebook runs.\n"


def df_to_md(df: pd.DataFrame) -> str:
    """Render a DataFrame as a GitHub markdown table (no tabulate dependency)."""
    def fmt(v):
        if pd.api.types.is_scalar(v) and pd.isna(v):
            return ""
        if isinstance(v, (int, np.integer)) and not isinstance(v, (bool, np.bool_)):
            return f"{v:,}"
        return str(v).replace("|", "\\|")
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(fmt(v) for v in row) + " |")
    return "\n".join(lines)


def _markers(key: str) -> tuple[str, str]:
    return f"<!-- BEGIN {key} -->", f"<!-- END {key} -->"


def write_section(key: str, title: str, body: str, path: Path = config.DATA_QUALITY) -> None:
    """Create or replace the section `key` in the data-quality report."""
    begin, end = _markers(key)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = f"{begin}\n## {title}\n\n_Last run: {stamp}_\n\n{body.strip()}\n{end}"

    text = path.read_text(encoding="utf-8") if path.exists() else _HEADER
    if begin in text and end in text:
        pre, rest = text.split(begin, 1)
        _, post = rest.split(end, 1)
        text = pre + block + post
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(text, encoding="utf-8")


class FilterLog:
    """Collects row counts for every filter so nothing is dropped silently.

    Usage:
        log = FilterLog()
        df = log.apply(df, df["age"] <= 21, "Keep players aged 21 or under")
        ...
        dq.write_section("01", "01 FIFA clean", log.to_markdown())
    """

    def __init__(self) -> None:
        self.rows: list[dict] = []

    def record(self, step: str, before: int, after: int) -> None:
        self.rows.append({"Step": step, "Rows before": before, "Rows after": after,
                          "Dropped": before - after})
        print(f"[filter] {step}: {before:,} -> {after:,} (dropped {before - after:,})")

    def apply(self, df: pd.DataFrame, mask: pd.Series, step: str) -> pd.DataFrame:
        out = df[mask]
        self.record(step, len(df), len(out))
        return out

    def to_markdown(self) -> str:
        if not self.rows:
            return "_No filters applied._"
        return df_to_md(pd.DataFrame(self.rows))
