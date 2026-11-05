# The Career Mode Promise: Did FIFA Spot Football's Future Stars?

IE6600 Project 1 · Sahil, Devarshi, Sarthak

Data work for a 14-chart data story. Python notebooks clean, join and analyse four datasets and
export one chart-ready CSV per chart. The charts themselves are built by hand in Flourish and
Datawrapper. See `CLAUDE.md` for the full spec.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt   # exact versions; or requirements.txt for latest
```

Raw data goes in `data/raw/` (not committed):

| Folder | Source |
|---|---|
| `data/raw/fifa/` | Kaggle `stefanoleone992/ea-sports-fc-24-complete-player-dataset` (`male_players.csv`) |
| `data/raw/transfermarkt/` | `kaggle datasets download -d davidcariboo/player-scores -p data/raw/transfermarkt --unzip` |
| `data/raw/fifa_ranking/` | `kaggle datasets download -d lucasyukioimafuko/fifa-mens-world-ranking -p data/raw/fifa_ranking --unzip` |
| `data/raw/clubelo/` | Downloaded by notebook 00 via `soccerdata` (one snapshot per edition date). While the ClubElo API is down, the four cohort entry dates are built from the mirror below by `python -I scripts/build_clubelo_mirror.py` |
| `data/raw/club_elo_mirror/` | Club Football Match Data (2000–2025), Kaggle, by adamgbor; Elo data from ClubElo: `kaggle datasets download -d adamgbor/club-football-match-data-2000-2025 -p data/raw/club_elo_mirror --unzip` |

On first use, `soccerdata` downloads a small native TLS library from GitHub into the venv.

## Running

Run the notebooks in `notebooks/` in order (00, 01, 02, …), each top to bottom on a fresh kernel:

```bash
cd notebooks && jupyter nbconvert --to notebook --execute --inplace 00_setup_and_download.ipynb
```

Outputs: `data/clean/` (parquet), `outputs/findings.json`, `outputs/charts/`, and logs in
`reports/data_quality.md` and `DECISIONS.md`.

`data/raw/` and `data/clean/` are not committed. After cloning, download the raw data (table above) and run
notebooks 00–04 to rebuild `data/clean/` before working on later notebooks.
