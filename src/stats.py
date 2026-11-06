"""Shared statistics: bootstrap CIs, AUC, Spearman, calibration line and 'shortfall vs similar prospects'."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src import config


def rng():
    return np.random.default_rng(config.RANDOM_SEED)


def boot_ci(df: pd.DataFrame, stat, reps: int = config.BOOTSTRAP_REPS, seed: int = config.RANDOM_SEED):
    """(estimate, 2.5th, 97.5th percentile) of stat(df) over row-resampled bootstraps."""
    r = np.random.default_rng(seed)
    n = len(df)
    vals = np.array([stat(df.iloc[r.integers(0, n, n)]) for _ in range(reps)], dtype=float)
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    return float(stat(df)), float(lo), float(hi)


def spearman(x: pd.Series, y: pd.Series) -> float:
    """Spearman rank correlation on pairwise-complete rows (Pearson on ranks)."""
    m = x.notna() & y.notna()
    return float(x[m].rank().corr(y[m].rank()))


def auc(score: pd.Series, y: pd.Series) -> float:
    """ROC AUC via ranks (Mann-Whitney). 0.5 = coin flip."""
    m = score.notna() & y.notna()
    s, t = score[m], y[m].astype(bool)
    n1, n0 = int(t.sum()), int((~t).sum())
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = s.rank()
    return float((r[t].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def loeo_benchmark(df: pd.DataFrame) -> pd.Series:
    """Out-of-sample benchmark: OLS peak later ~ 1 + overall + age, fitted on the other entry editions."""
    pred = pd.Series(np.nan, index=df.index)
    for e in df["entry_edition"].unique():
        tr = df[(df["entry_edition"] != e) & df["peak_later"].notna()]
        X = np.column_stack([np.ones(len(tr)), tr["overall"], tr["age"]])
        coef, *_ = np.linalg.lstsq(X, tr["peak_later"].astype(float), rcond=None)
        te = df["entry_edition"] == e
        pred[te] = coef[0] + coef[1] * df.loc[te, "overall"] + coef[2] * df.loc[te, "age"]
    return pred


def calibration_line(g: pd.DataFrame) -> tuple[float, float]:
    """OLS of peak later rating on potential (players with a later edition): (intercept, slope)."""
    slope, intercept = np.polyfit(g["potential"].astype(float), g["peak_later"].astype(float), 1)
    return float(intercept), float(slope)


def shortfall(df: pd.DataFrame, line: tuple[float, float]) -> pd.Series:
    """Shortfall vs similar prospects = typical peak for that potential − actual peak.

    Positive = fell further short than players given the same potential (overrated relative to peers);
    negative = beat them. Removes the mechanical effect that higher potentials show bigger raw gaps.
    """
    b0, b1 = line
    return (b0 + b1 * df["potential"].astype(float)) - df["peak_later"].astype(float)
