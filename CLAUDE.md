# CLAUDE.md: The Career Mode Promise (IE6600 Project 1)

## 1. What this project is

**Title:** The Career Mode Promise: Did FIFA Spot Football's Future Stars?
**Team:** Sahil, Devarshi, Sarthak
**Deadline:** internal Friday 6 Nov 2026; hard deadline Sunday 8 Nov 2026 (no edits after submission)

This is a business and technology data story. EA Sports' FIFA/FC games rate every young player's
"potential", a talent prediction seen by millions of players. We test how accurate those predictions
were, who they misjudged, and what actually predicted a career.

The final product is a website with 14 interactive charts that the team builds **by hand** in
Flourish and Datawrapper (7 each). **Your job in this repo is the data work only:** Python notebooks
that clean, join and analyse four datasets, then export one chart-ready CSV per chart plus a written
spec for each chart. You do not draw the final charts.

Story structure (the charts follow this order):
1. The Promise: the game crowns its wonderkids
2. The Reckoning: most of them never get there
3. Who the Game Misjudged: club badge, nationality, position
4. What Actually Mattered: teenage attributes, real playing time
5. Where They Are Now: where the wonderkids ended up

---

## 2. Rules for working in this repo

1. **One notebook at a time, in the order in section 8.** When a notebook is finished, stop and
   print a summary: rows in and out, every check passed or failed, and every decision made. Wait for
   approval before starting the next one.
2. **Inspect before you assume.** Print the columns, dtypes and first rows of every raw file before
   writing logic. If a column named in this file doesn't exist, stop and report it. Don't guess a
   substitute.
3. **Notebooks must run top to bottom on a fresh kernel.** Read all paths from `src/config.py`.
   No absolute paths.
4. **Reusable logic goes in `src/`** (name normalisation, matching, cohort logic). Notebooks import it.
5. **Never type a computed number into a title, caption or text.** Compute it, write it to
   `outputs/findings.json`, and have the chart specs read it from there.
6. **Never drop rows silently.** Every filter logs the row count before and after, plus the reason,
   to `reports/data_quality.md`.
7. **Record every judgement call in `DECISIONS.md`:** date, decision, reason, alternatives considered.
8. **If a check fails, stop and explain.** Never adjust logic just to make a check pass.
9. Plots inside notebooks are for QA only (small matplotlib figures). Final charts are built in
   Flourish and Datawrapper.
10. Never commit `data/raw/`, `kaggle.json`, `.env` or any API token. Add them to `.gitignore`.

---

## 3. Repo layout

```
career-mode-promise/
├── CLAUDE.md
├── DECISIONS.md
├── README.md
├── requirements.txt
├── .gitignore              # data/raw/, .env, kaggle.json, __pycache__, .ipynb_checkpoints
├── data/
│   ├── raw/                # untouched downloads (not committed)
│   │   ├── fifa/           # male_players.csv, male_teams.csv, male_coaches.csv
│   │   ├── transfermarkt/
│   │   ├── clubelo/
│   │   └── fifa_ranking/
│   ├── manual/             # hand-maintained override files (committed)
│   │   ├── tm_match_overrides.csv
│   │   ├── club_name_overrides.csv
│   │   └── nation_name_overrides.csv
│   └── clean/              # parquet outputs of the cleaning notebooks
├── notebooks/
├── src/
│   ├── config.py           # paths, constants, palette, edition labels
│   ├── names.py            # name normalisation
│   ├── matching.py         # FIFA ↔ Transfermarkt matching
│   └── cohort.py           # cohort and outcome logic
├── outputs/
│   ├── findings.json       # every number used in titles or website text
│   └── charts/             # one CSV per chart + chart_specs.md
└── reports/
    ├── data_quality.md
    └── match_review.csv    # ambiguous matches for a human to check
```

---

## 4. Environment

- Python 3.11
- `requirements.txt`: `pandas`, `numpy`, `pyarrow`, `jupyter`, `matplotlib`, `rapidfuzz`,
  `unidecode`, `pycountry`, `soccerdata`, `kaggle`, `python-dotenv`, and optionally `datawrapper`
- Kaggle downloads need `~/.kaggle/kaggle.json`
- Optional: `DATAWRAPPER_ACCESS_TOKEN` in `.env` (see section 10)

---

## 5. Data sources

| # | Dataset | Put in | How to get it |
|---|---|---|---|
| 1 | EA Sports FC 24 Complete Player Dataset (FIFA 15 to FC 24) | `data/raw/fifa/` | Already downloaded. Use `male_players.csv` only. Kaggle: `stefanoleone992/ea-sports-fc-24-complete-player-dataset` |
| 2 | Transfermarkt Football Data | `data/raw/transfermarkt/` | `kaggle datasets download -d davidcariboo/player-scores -p data/raw/transfermarkt --unzip` |
| 3 | ClubElo club ratings | `data/raw/clubelo/` | `soccerdata.ClubElo().read_by_date(date)`, one call per edition date; cache each result as CSV |
| 3b | Club Football Match Data (2000–2025), Kaggle, by adamgbor; Elo data from ClubElo (mirror used while the ClubElo API is down; see `DECISIONS.md`) | `data/raw/club_elo_mirror/` | `kaggle datasets download -d adamgbor/club-football-match-data-2000-2025 -p data/raw/club_elo_mirror --unzip`, then `python -I scripts/build_clubelo_mirror.py`. Chart 10's source line credits both this dataset and ClubElo |
| 4 | FIFA Men's World Ranking | `data/raw/fifa_ranking/` | `kaggle datasets download -d lucasyukioimafuko/fifa-mens-world-ranking -p data/raw/fifa_ranking --unzip` |

Notes:
- The FIFA file has **one snapshot per edition** (launch-week ratings), not every in-season update.
  The FIFA 15 snapshot is dated **18 Sept 2014**, not 2015.
- For the FIFA Ranking, check the date coverage first. It must cover Sept 2014 to Sept 2023. If it
  doesn't, stop and report.
- Use the ranking **position**, never the points. FIFA changed its formula in 2018, so points before
  and after aren't comparable.

---

## 6. Definitions (use exactly these)

| Term | Definition |
|---|---|
| Edition | `fifa_version` 15 to 24. Labels: 15 → "FIFA 15" … 23 → "FIFA 23", 24 → "FC 24" |
| Edition date | `update_as_of` for that edition |
| Primary position | First item in the comma-separated `player_positions` string |
| Position group | GK; DEF = CB, LB, RB, LWB, RWB; MID = CDM, CM, CAM, LM, RM; FWD = LW, RW, CF, ST |
| Cohort entry | A player's **first** edition from FIFA 15 to FIFA 18 in which he is aged 21 or under. Each player enters once. Never count the same player in two cohorts |
| Wonderkid | Cohort entrant with potential ≥ 85 at entry |
| Potential band | Potential at entry: <70, 70–74, 75–79, 80–84, 85+ |
| Peak later rating | Highest `overall` in any edition **after** entry |
| Peak within 4 | Highest `overall` in the 4 editions after entry (used only for chart 7, so every cohort gets the same follow-up time) |
| Status (game) | **Reached**: peak later rating ≥ potential at entry. **Fell short**: below it. **Vanished**: no later edition |
| Gap | Potential at entry minus peak later rating. Positive = overrated, negative = underrated |
| Already peaked | `overall` = `potential` at entry. Exclude these from accuracy metrics and log how many |
| Real-world "made it" | Default: ≥ 3,000 minutes in Big-5 league matches after the entry date (Transfermarkt competition IDs GB1, ES1, L1, IT1, FR1). Also report results at 1,500 and 5,000 minutes in `DECISIONS.md` |
| Club strength at entry | ClubElo rating of the player's FIFA club on the edition date. Missing = non-European club; flag it, don't impute |
| Nation rank at entry | FIFA ranking position on the latest ranking date on or before the edition date |

Vanished players are **not** failures by default. Keep them as their own category in every count.

---

## 7. Regression checks for `male_players.csv`

Assert these in notebook 01. If any check fails, stop.

- 180,021 rows, 109 columns, 53,111 unique `player_id`s
- No duplicate (`player_id`, `fifa_version`) pairs
- Rows and dates per edition:

| Edition | Rows | Date | Under-21s with potential ≥ 85 |
|---|---|---|---|
| 15 | 16,182 | 2014-09-18 | 48 |
| 16 | 16,706 | 2015-09-21 | 82 |
| 17 | 17,596 | 2016-09-20 | 106 |
| 18 | 17,954 | 2017-09-18 | 137 |
| 19 | 18,086 | 2018-08-21 | 144 |
| 20 | 18,483 | 2019-09-19 | 170 |
| 21 | 18,892 | 2020-09-23 | 145 |
| 22 | 19,239 | 2021-09-23 | 120 |
| 23 | 18,533 | 2022-09-26 | 127 |
| 24 | 18,350 | 2023-09-22 | 108 |

- FIFA 15 players aged 21 or under: 4,594. By potential band, with peak later rating measured
  across all later editions:

| Band | n | Reached | Vanished | Mean (peak later − potential) |
|---|---|---|---|---|
| <70 | 2,634 | 1,032 | 774 | +0.81 |
| 70–74 | 1,064 | 301 | 132 | −2.63 |
| 75–79 | 602 | 153 | 22 | −4.08 |
| 80–84 | 246 | 70 | 0 | −3.97 |
| 85+ | 48 | 7 | 1 | −4.15 |

These numbers use FIFA 15 under-21s only, before the "first entry only" and "already peaked" rules.
Reproduce them first as a check, then apply the full cohort rules.

---

## 8. Notebooks (build in this order)

The owner reviews the outputs and fills in the manual override files. Anyone can run the notebook.

### 00_setup_and_download.ipynb (owner: Sahil)
- Create the folder structure, `src/config.py` (paths, edition labels, palette from section 11)
  and an empty `DECISIONS.md` and `reports/data_quality.md`.
- Download or locate all four sources. Print the schema and 5 sample rows of every file.
- Transfermarkt: list every table and its columns. Expect at least `players`, `player_valuations`,
  `appearances`, `clubs`, `competitions`. Confirm the date-of-birth, name, minutes and competition
  columns exist before going further.
- ClubElo: fetch one snapshot per edition date (10 calls) and cache them.
- **Output:** a short inventory table (file, rows, columns, date range) in `reports/data_quality.md`.

### 01_fifa_clean.ipynb (owner: Sahil)
- Load `male_players.csv`, run every check in section 7.
- Add: edition label, edition date, primary position, position group.
- Missing values: the six face stats (`pace` to `physic`) are blank for goalkeepers by design, so
  leave them as NaN and exclude GKs from attribute analysis. Log missing rates for `value_eur`,
  `wage_eur`, `club_name`, `league_name`.
- Outliers: log ages ≤ 16 and ≥ 40 and any `potential` < `overall` (should be none).
- Build `data/clean/fifa_panel.parquet` (all rows, cleaned) and `data/clean/cohort.parquet`
  (one row per cohort entrant, using the section 6 rules) with entry attributes, peak later rating,
  peak within 4, status, gap, already-peaked flag, and last edition seen.
- Also build `data/clean/learning_cohorts.parquet`: entries from FIFA 15 to FIFA 20 with peak within 4
  (for chart 7).
- **Checks:** each player appears once in the cohort; logged counts of excluded already-peaked players;
  status counts sum to the cohort size.

### 02_transfermarkt_match.ipynb (owner: Devarshi)
- Goal: a crosswalk `fifa player_id ↔ transfermarkt player_id` for every cohort entrant.
- Normalise names in `src/names.py`: unidecode, lowercase, strip punctuation and suffixes, collapse
  spaces. Compare FIFA `long_name` and `short_name` with Transfermarkt's full and short names.
- Match rule: date of birth must match exactly. Among same-DOB candidates, take the best
  `rapidfuzz` `token_set_ratio`. Accept if ≥ 85. Send 70–84, ties, and every 85+ potential player
  to `reports/match_review.csv` for a human to confirm. Read confirmed or corrected pairs back from
  `data/manual/tm_match_overrides.csv`.
- Report the match rate overall and by potential band. Target ≥ 90% for the 80+ bands. If lower,
  stop and report examples of misses.
- Real-world outcomes per matched player: peak market value after entry (from `player_valuations`),
  Big-5 league minutes after entry (from `appearances`), the "made it" flag at 1,500 / 3,000 / 5,000
  minutes, latest club and its competition.
- Transfermarkt's appearance records don't go back as far as FIFA 15 for every league. Check the
  earliest appearance date per competition and note any gap in `DECISIONS.md`.
- **Output:** `data/clean/tm_crosswalk.parquet`, `data/clean/real_outcomes.parquet`.

### 03_clubelo.ipynb (owner: Devarshi)
- Combine the 10 cached snapshots into `data/clean/clubelo_by_edition.parquet` (club, country,
  level, elo, edition).
- Map FIFA `club_name` to ClubElo club names with `rapidfuzz`, then apply
  `data/manual/club_name_overrides.csv`. Prioritise clubs with 3+ cohort players; every such
  European club must be mapped or explicitly marked as not in ClubElo.
- Join club strength at entry onto the cohort. Non-European clubs get NaN plus a flag.
- **Output:** `data/clean/club_strength.parquet`, mapping coverage stats in `reports/data_quality.md`.

### 04_fifa_ranking.ipynb (owner: Sarthak)
- Load the ranking, check the date coverage, keep rank (not points).
- Map FIFA `nationality_name` to ranking country names, then apply
  `data/manual/nation_name_overrides.csv` (e.g. "Korea Republic", "Côte d'Ivoire", "IR Iran").
- Nation rank at entry = rank on the latest ranking date ≤ edition date.
- Add ISO3 codes with `pycountry` for the Datawrapper map. FIFA trigrams are not ISO codes
  (GER ≠ DEU, NED ≠ NLD), so don't reuse them. England, Scotland, Wales and Northern Ireland map to
  GBR on the world map; record this in `DECISIONS.md`.
- Keep the confederation column if the dataset has one.
- **Output:** `data/clean/nation_rank.parquet`, `data/clean/nation_iso.parquet`.

### 05_analysis_master.ipynb (owner: Sahil)
- Join cohort + real outcomes + club strength + nation rank into `data/clean/analysis.parquet`
  (one row per cohort entrant).
- Compute and write to `outputs/findings.json` at least: wonderkid counts per edition, share
  reached per band, mean gap per band, number vanished, match rate, share "made it" in real life by
  band, the biggest busts and bloomers, and any number a chart title will use.
- Propose the **featured five** for the team to approve. Pick from FIFA 15 entrants where
  possible: (1) a star who reached his potential, (2) the biggest bust, (3) a late bloomer whose
  potential was under 80 but whose peak later rating reached 85+, (4) a player whose latest club is
  outside Europe, (5) a player whose peak later rating equals his potential exactly. Show the
  candidates; don't finalise without approval.
- **This notebook decides the story's ending.** Print the calibration result clearly: what share
  of each band reached its potential, in the game and in real life.

### 10_export_act1_2.ipynb (owner: Sahil) → charts 1–7
### 11_export_act3.ipynb (owner: Sarthak) → charts 8–11
### 12_export_act4_5.ipynb (owner: Devarshi) → charts 12–14

Each export notebook writes the CSVs in section 9 and appends its charts to
`outputs/charts/chart_specs.md` (format in section 9.3).

---

## 9. Chart exports

### 9.1 Format rules (Flourish and Datawrapper upload)
- UTF-8 CSV, comma separated, one header row, human-readable column names (these become labels
  and tooltip fields).
- Round ratings to integers, gaps to 1 decimal, money to € millions with 1 decimal, shares to
  whole percentages.
- Edition labels as text ("FIFA 15", "FC 24"), not numbers, so the tools treat them as categories.
- Include a `Featured` column (Yes/blank) wherever a chart shows individual players.
- Keep each file under 3,000 rows.
- File name pattern: `outputs/charts/NN_short_name.csv`.

### 9.2 The 14 charts

| # | File | Tool & chart type | Shape and columns |
|---|---|---|---|
| 1 | `01_wonderkid_table.csv` | Datawrapper table (search on) | One row per FIFA 15 wonderkid: Player, Club (2014), Nation, Age, Overall, Potential, Peak later rating, Gap, Status, Peak market value (€m), Latest club |
| 2 | `02_wonderkids_per_edition.csv` | Datawrapper column chart | Edition, Wonderkids (under-21s with potential ≥ 85, per edition) |
| 3 | `03_rating_trajectories.csv` | Flourish line chart | Wide: Edition, then one column per featured player (overall rating), plus "85+ cohort median" |
| 4 | `04_promise_vs_reality.csv` | Flourish scatter | One row per cohort entrant with potential ≥ 75: Player, Entry edition, Position group, Potential (x), Peak later rating (y), Status (colour), Club, Nation, Featured |
| 5 | `05_calibration_ladder.csv` | Datawrapper stacked bar (100%) | Band, Reached %, Fell short %, Vanished %, n |
| 6 | `06_busts_and_bloomers.csv` | Datawrapper range plot | Top 10 busts and top 10 bloomers: Player (label incl. group), Potential at entry, Peak later rating, Group |
| 7 | `07_did_ea_learn.csv` | Flourish line chart | Entry edition (FIFA 15–20), Share reached within 4 editions %, Mean gap within 4 |
| 8 | `08_nation_map.csv` | Datawrapper choropleth (world) | ISO3, Nation, Mean gap, Share reached %, n (only nations with n ≥ 15; others blank) |
| 9 | `09_nation_rank_vs_gap.csv` | Flourish scatter | One row per nation (n ≥ 15): Nation, Mean nation rank at entry (x), Mean gap (y), n (size), Confederation (colour, if available) |
| 10 | `10_club_strength_vs_gap.csv` | Flourish scatter | One row per club (n ≥ 5): Club, League, Mean club Elo at entry (x), Mean gap (y), n (size) |
| 11 | `11_position_gap.csv` | Datawrapper dot plot | Primary position, Mean potential at entry, Mean peak later rating, n |
| 12 | `12_attributes_that_mattered.csv` | Datawrapper bar chart | Outfield players only. Attribute, Correlation (Spearman) between the attribute at entry and (peak later rating − potential). Top 8 positive and top 8 negative |
| 13 | `13_game_vs_market.csv` | Flourish line chart with player filter | Long: Date, Player (filter), Game rating (% of own peak), Market value (% of own peak). Featured five plus 10 more well-known entrants |
| 14 | `14_where_they_ended_up.csv` | Flourish Sankey | Source, Target, Value, plus step columns if the template asks. Steps: potential band (75+ only) → game status → latest club tier (Big-5 / other European top flight / other or lower league / outside Europe / no current club) |

For chart 4: if Flourish can't draw a y = x reference line cleanly, rely on the Status colour; say
so in the spec notes.

### 9.3 Chart spec entry (append one per chart to `chart_specs.md`)

```
## Chart NN: <short name>
- File: outputs/charts/NN_short_name.csv
- Tool / template: <Datawrapper column chart | Flourish scatter | …>
- Title (states the finding, numbers from findings.json): …
- Subtitle (what is measured, units): …
- Column → role mapping: x = …, y = …, colour = …, label = …, filter = …
- Colours: <hex codes from section 11 with their meaning>
- Tooltip (HTML): <b>{{Player}}</b><br>Potential: {{Potential}}<br>Best later rating: {{Peak later rating}}
- Source line: EA Sports FC 24 Complete Player Dataset (Kaggle); Transfermarkt (Kaggle); … with links
- Notes for the builder: sort order, axis ranges, which points to label, caveats
```

Write titles as findings, e.g. "Only 7 of FIFA 15's 48 wonderkids reached their potential", with
numbers pulled from `findings.json`.

---

## 10. Optional: Datawrapper refresh script

`src/push_datawrapper.py`, only after the charts exist. Reads `outputs/charts/dw_chart_ids.json`
(chart number → Datawrapper chart ID, filled in by hand), uploads the latest CSV to each chart and
republishes it, using `DATAWRAPPER_ACCESS_TOKEN` from `.env`. Never create charts or change styling
with it; it only refreshes data. Flourish has no free API, so Flourish data is re-uploaded by hand.

---

## 11. Style constants (put in `src/config.py`)

| Meaning | Hex |
|---|---|
| The game's promise (potential) | `#F2A900` |
| Reality (actual outcome) | `#1B998B` |
| Fell short / overrated | `#D1495B` |
| Beat potential / underrated | `#2E86AB` |
| Text | `#1D2433` |
| Background context data | `#C5CAD3` |

Featured players always use the promise gold `#F2A900` with a name label.

---

## 12. Timeline

| Day | Work | Done when |
|---|---|---|
| Tue 3 Nov | Notebooks 00 and 01; Transfermarkt and ranking downloads | Section 7 checks pass |
| Wed 4 Nov | Notebooks 02–05; manual review files filled in; **data frozen at 6 pm**; story locked in the evening | `findings.json` and featured five approved |
| Thu 5 Nov | Export notebooks 10–12 in the morning; all 14 charts built by the afternoon; website skeleton in parallel | Every chart published in its tool and reviewed by a teammate |
| Fri 6 Nov | Embed charts, captions, proofreading against `findings.json`, final QA, publish | Site submitted |
| Sat–Sun | Buffer only | |
