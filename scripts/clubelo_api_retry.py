"""Retry the ClubElo API every 30 minutes until a deadline, skipping cached dates.

Usage: python scripts/clubelo_api_retry.py 2026-11-05T10:00
Prints one line per attempt round; exits 0 when all 10 dates are cached, 1 at the deadline.
"""
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import config, clubelo  # noqa: E402

logging.getLogger("soccerdata").setLevel(logging.CRITICAL)
deadline = datetime.fromisoformat(sys.argv[1])
dates = list(config.EXPECTED_EDITION_DATES.values())

while True:
    todo = [d for d in dates if not clubelo.cache_path(d).exists()]
    if not todo:
        print(f"{datetime.now():%m-%d %H:%M} all {len(dates)} snapshots cached", flush=True)
        sys.exit(0)
    got = []
    for d in todo:
        try:
            clubelo.fetch_snapshot(d)
            got.append(d)
        except Exception as e:
            err = type(e).__name__
    left = len(todo) - len(got)
    print(f"{datetime.now():%m-%d %H:%M} fetched {len(got)} ({', '.join(got)}); {left} still missing"
          + (f" [{err}]" if left else ""), flush=True)
    if left == 0:
        continue
    if datetime.now() >= deadline:
        print("deadline reached", flush=True)
        sys.exit(1)
    time.sleep(30 * 60)
