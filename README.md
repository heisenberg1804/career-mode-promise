# The Career Mode Promise: Did FIFA Spot Football's Future Stars?

IE6600 Project 1 · Sahil, Devarshi, Sarthak

Data work for a 14-chart data story. Python notebooks clean, join and analyse four datasets and
export one chart-ready CSV per chart. The charts themselves are built by hand in Flourish and
Datawrapper. See `CLAUDE.md` for the full spec.

## Status (5 Nov 2026)

Data work done and frozen; what remains is building the 14 charts and the story site. Start here:

| You want to… | Open |
|---|---|
| Understand the project rules and current status | `CLAUDE.md` (section 0 first) |
| See the story and why each chart exists | `reports/chart_plan_v2.md` |
| Build a chart | `outputs/build_guide.html` (how-to), `outputs/chart_previews.html` (preview + exact title, colours, tooltip, notes per chart), `outputs/charts/NN_*.csv` (upload these) |
| Embed charts in the site | `website/embeds.json` → `python -I scripts/build_story_site.py` → `website/index.html` |
| Check a number or a method choice | `outputs/findings.json`, `DECISIONS.md`, `reports/data_quality.md` |

Building charts needs no Python setup and no raw data: the CSVs are committed. Python is only needed to rebuild the site.

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

## Charts and the story site

- `outputs/charts/` – the 14 upload-ready CSVs and `chart_specs.md` (written by notebooks 10–12).
- `outputs/chart_previews.html` – previews of all 14 charts with build notes (`python -I scripts/render_chart_previews.py`).
- `outputs/build_guide.html` – step-by-step guide for building the charts in Datawrapper/Flourish and embedding them.
- `website/` – the story site. Paste each published chart's ID into `website/embeds.json`, then run
  `python -I scripts/build_story_site.py` to regenerate `website/index.html`.
