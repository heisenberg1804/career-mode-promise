# Decisions

Every judgement call: date, decision, reason, alternatives considered.

---

### 2026-11-04 · Environment: unpinned requirements plus a lockfile
- **Decision:** `requirements.txt` lists the packages from CLAUDE.md §4 without versions (as specified, plus the optional `datawrapper`). The exact versions installed on Python 3.11.13 are frozen in `requirements-lock.txt` (`pip install -r requirements-lock.txt` reproduces the environment).
- **Reason:** Keep the spec's list readable while making runs reproducible across the three laptops. Note pandas is 3.x (copy-on-write, `str` dtype by default).
- **Alternatives:** Pin versions directly in `requirements.txt` (harder to read and update).

### 2026-11-04 · Two helper modules added to `src/`
- **Decision:** Added `src/dq.py` (writes `reports/data_quality.md`, logs filters) and `src/clubelo.py` (ClubElo fetch and cache) alongside the four modules in CLAUDE.md §3.
- **Reason:** Rule 4 (reusable logic in `src/`). Every notebook logs to the data-quality report, and notebook 03 reads the same cache notebook 00 writes.
- **Alternatives:** Inline the code in each notebook (duplicated, and it would drift).

### 2026-11-04 · data_quality.md sections are replaced, not appended
- **Decision:** Each notebook owns a section of `reports/data_quality.md` between `<!-- BEGIN NN -->` / `<!-- END NN -->` markers, and re-running the notebook replaces that section.
- **Reason:** Notebooks are re-run many times; appending would pile up stale, contradictory counts.
- **Alternatives:** Append-only log with timestamps (complete history, but hard to read as the current state).

### 2026-11-04 · ClubElo snapshot dates and caching
- **Decision:** Fetch one snapshot per edition, using the `update_as_of` date read from `male_players.csv` (checked against CLAUDE.md §7). Pass each date to soccerdata as a timezone-aware UTC datetime. Cache to `data/raw/clubelo/clubelo_YYYY-MM-DD.csv` (soccerdata's own raw cache sits in `data/raw/clubelo/_soccerdata_cache/`). A date that is already cached is never re-downloaded.
- **Reason:** soccerdata 2026.43 turns a `'YYYY-MM-DD'` string into a date via local time and then UTC, which shifts the date back one day on machines east of UTC. Caching freezes the data so teammates get identical inputs.
- **Alternatives:** Pass plain strings (date depends on the machine's timezone); call `api.clubelo.com` directly without soccerdata (CLAUDE.md names soccerdata, and the API is the same).

### 2026-11-04 · Inventory row counts from parsed CSVs
- **Decision:** Inventory rows are `len(DataFrame)` after `pd.read_csv`, not `wc -l` minus 1.
- **Reason:** Quoted fields can contain line breaks; the parsed count is what the notebooks actually use. (For these files the two counts agree.)
- **Alternatives:** Line counts (faster, but wrong for multi-line records).

### 2026-11-04 · Cohort: DOB corrections and the first-entry rule
- **Decision:** Apply the §6 entry rule literally (first edition 15–18 with `age <= 21`). 7 players were over 21 in an earlier edition but 21 or under later, because EA corrected their DOB; they are kept (IDs logged in `reports/data_quality.md`).
- **Reason:** The rule is defined on the game's own `age` field, and the effect is tiny (7 of 11,519).
- **Alternatives:** Exclude anyone ever recorded as over 21 before entry; recompute age from the latest DOB.

### 2026-11-04 · Keep every DOB variant for matching
- **Decision:** `cohort.parquet` carries `dob` (as at entry) and `dob_variants` (every DOB the player has across editions, `|`-separated). 1,524 of 53,111 players have more than one.
- **Reason:** Notebook 02 requires an exact DOB match, and a single DOB would miss players whose DOB EA corrected.
- **Alternatives:** Use the entry DOB only, or the latest DOB only.

### 2026-11-04 · Peak definitions
- **Decision:** "Later" = editions strictly after entry. "Within 4" = editions entry+1 to entry+4 by edition number; a skipped edition does not extend the window. Ties for the peak record the earliest edition.
- **Reason:** Gives every cohort the same calendar follow-up (chart 7) and makes peak timing deterministic.
- **Alternatives:** The next 4 editions the player actually appears in (unequal follow-up time).

### 2026-11-04 · Learning cohorts use the same first-entry rule over FIFA 15–20
- **Decision:** `learning_cohorts.parquet` applies first entry over FIFA 15–20, so its FIFA 15–18 entries are identical to the cohort.
- **Reason:** §6 says never to count a player in two cohorts. Sensitivity check: computing "reached within 4" for *all* under-21s in each edition (players can repeat) gives the same downward trend (25.0% → 16.2% → 9.7% → 8.4% → 7.7% → 5.8% for FIFA 15–20, vs 25.0% → 5.9% under the first-entry rule), so the chart 7 result does not depend on this choice.
- **Alternatives:** Per-edition snapshots of all under-21s.

### 2026-11-04 · Cohort columns
- **Decision:** In `cohort.parquet`, the original FIFA columns hold values at the entry edition; the 27 per-position rating strings (`ls` … `gk`) are dropped (kept in `fifa_panel.parquet`). Outliers (ages ≤ 16 and ≥ 40) are logged and kept.
- **Reason:** The position strings ("89+3") aren't used by any chart; the extreme ages are plausible real players.
- **Alternatives:** Prefix every entry column with `entry_` (80+ renames, harder to read).

### 2026-11-04 · FIFA ranking: semester → date (decided by Sahil, for notebook 04)
- **Decision:** Treat ranking semester 1 as 30 June and semester 2 as 31 December of the `date` year. "Latest ranking on or before the edition date" then means each September (or August, FIFA 19) edition uses that year's semester 1 ranking.
- **Reason:** The ranking file has only year + semester, with no exact dates. End-of-half-year dates are the conservative reading: a ranking is never used before it could have been published.
- **Alternatives:** Use semester 2 of the previous year; interpolate between semesters.

### 2026-11-04 · FIFA ranking: confederation from Transfermarkt (decided by Sahil, for notebook 04)
- **Decision:** The ranking file has no confederation column; take it from Transfermarkt's `countries.csv` or `national_teams.csv` (both have one).
- **Reason:** Chart 9 colours nations by confederation.
- **Alternatives:** Hand-coded lookup; drop the colour encoding.

### 2026-11-04 · ClubElo: routes tried while api.clubelo.com is down
- **Status:** No route has produced the 10 edition snapshots yet. No other data source has been substituted (instruction from Sahil: ask before substituting).
- **API:** every `api.clubelo.com` endpoint returned HTTP 502 (Cloudflare) from 18:35 on 4 Nov. `scripts/clubelo_api_retry.py` retries every 30 minutes until Thu 5 Nov 10:00, skipping dates already cached; snapshots it fetches carry `source = "api"`.
- **Website (clubelo.com):** not usable. Every page, including `robots.txt`, returns HTTP 403 with a Cloudflare JavaScript challenge ("Just a moment…"). Getting past it would mean circumventing their bot protection, so it was not attempted.
- **Wayback Machine:** checked the CDX index for (a) the 10 `api.clubelo.com/YYYY-MM-DD` URLs: none archived (the only archived API dates are 2008-02-02, 2008-03-29, 2017-01-01, 2024-09-02, 2025-01-23); and (b) `clubelo.com/YYYY-MM-DD…` website pages for the 10 dates: only a few single-club, head-to-head or single-country pages (e.g. `/2014-09-18/Sevilla`, `/2014-09-18/FIN`), no full ranking for any date.
- **Alternatives (not taken, need approval):** use the nearest archived API date (only 2017-01-01 falls in range, and it is not an edition date); per-club history from another mirror; a different club-strength source.

### 2026-11-04 · Transfermarkt match: names and DOB
- **Decision:** DOB must equal *any* of the player's FIFA DOB variants exactly. Transfermarkt has no short-name column, so a FIFA-style short name (first initial + `last_name`) is built. Score = best `token_set_ratio` over FIFA {`long_name`, `short_name`} × TM {`name`, `first_name last_name`, initial + `last_name`}, after `src/names.normalise`.
- **Reason:** 1,524 players have DOB corrections in FIFA; without the derived short name, FIFA short names like "K. Mbappé" score only ~86 against "Kylian Mbappé".
- **Alternatives:** Entry DOB only; compare long names only.

### 2026-11-04 · Transfermarkt match: extra review triggers
- **Decision:** Besides the §8 triggers (score 70–84, ties, potential 85+), an auto match also goes to review if (a) the goalkeeper flag disagrees between FIFA and TM (5 players; match kept), or (b) one TM player is the best auto match for two FIFA players (18 players; neither accepted until reviewed). Potential-85+ auto matches stay accepted but carry `needs_review = True` until confirmed.
- **Reason:** Case (b) is almost always twins with the same DOB (Eryüksel, McKay, San Emeterio, O'Sullivan, Manquillo…), where only a human can tell which twin TM has. GK disagreement is a cheap signal of a wrong person.
- **Alternatives:** Give a contested TM id to the higher-scoring FIFA player automatically.

### 2026-11-04 · Transfermarkt match: near-DOB suggestions
- **Decision:** For potential-80+ players with no exact-DOB match, the review file lists up to 3 TM players born within a year with name score ≥ 85. They are never accepted automatically; a reviewer must add a `correct` override.
- **Reason:** DOB typos between the sources are the main cause of missed real players (e.g. Carles Gil 1992-11-02 in FIFA vs 1992-11-22 in TM; Godfred Donsah, Alexis Araujo, Domingos Duarte, Aleix Febas, Alessandro Plizzari).
- **Alternatives:** Relax the DOB rule automatically (breaks the §8 rule); no suggestions (reviewers would search by hand).

### 2026-11-04 · Real outcomes: definitions
- **Decision:** "After entry" = dated strictly after the entry edition date. Big-5 minutes = sum of `minutes_played` in GB1/ES1/L1/IT1/FR1 appearances (league matches only, no cups). Latest club = TM `current_club_*` (the last club TM tracked) plus `last_season`, and separately the most recent transfer dated on or before today (475 future-dated transfer rows are ignored). Unmatched players get no outcome row; notebook 05 decides how to treat them.
- **Reason:** TM's `current_club` is stale for players who moved to leagues TM doesn't cover; the transfer record still names the new club.
- **Alternatives:** Count cup and European minutes too (not "league matches" per §6).

### 2026-11-04 · Appearance coverage
- **Finding:** Big-5 appearance records start in Aug 2012 (before FIFA 15) and every Big-5 season from 2012/13 to 2025/26 is present, with no season below half the median count. 7 competitions start after 18 Sept 2014 (2026 World Cup, AFCON 2025, Belgian play-offs from 2026, Conference League qualifying from 2021, `CGB` from 2023), none of which feed the "made it" flag. Every player with a Big-5 appearance is in `players.csv`, so an unmatched entrant has no Big-5 minutes unless his match was missed (e.g. by a DOB typo).

### 2026-11-04 · "Made it" thresholds: sensitivity (matched players only, before manual review)
- Share with ≥ 1,500 / 3,000 / 5,000 Big-5 minutes after entry, by potential band: <70: 12.5 / 9.6 / 7.4%; 70–74: 18.5 / 14.7 / 11.6%; 75–79: 32.7 / 27.4 / 22.0%; 80–84: 58.5 / 50.7 / 44.3%; 85+: 74.5 / 69.6 / 62.7%. The ordering of the bands is the same at every threshold. Default stays at 3,000. Final figures come from notebook 05 after review.
- **Open for notebook 05:** match rates differ by band (40.7% for <70 vs 98.1% for 85+), largely because TM only covers top-flight leagues. A "matched only" denominator overstates "made it" for low bands; counting unmatched entrants as not made it is defensible given the Big-5 coverage finding above.

### 2026-11-04 · ClubElo: mirror dataset for the four entry dates (approved by Sahil)
- **Decision:** While api.clubelo.com is down, club strength at entry comes from the Kaggle dataset `adamgbor/club-football-match-data-2000-2025` (Adam Gábor, MIT licence; GitHub `xgabora/Club-Football-Match-Data`), file `EloRatings.csv`. Its README says "Elo data are sourced from ClubElo" and that records through 1 June 2025 come from ClubElo (later snapshots are the author's extrapolation, not used here). Only the four cohort entry dates are needed (2014-09-18, 2015-09-21, 2016-09-20, 2017-09-18).
- **Method:** the mirror keeps ClubElo snapshots on the 1st and 15th of each month. Each entry date uses the latest snapshot on or before it (the 15th of the same month, 3–6 days earlier). `level` is derived from the club's league division that season in the mirror's `Matches.csv` (NaN for ~27% of clubs whose names differ between the two files; Elo is unaffected). Saved as `data/raw/clubelo/clubelo_mirror_YYYY-MM-DD.csv` with `source` = mirror and `rating_date` = the snapshot actually used. `src/clubelo.load_best_snapshots` prefers an API snapshot for a date if one is cached.
- **QA:** 406–415 clubs per snapshot, 0 duplicate clubs, 19 countries, plausible top 10 (Real Madrid, Barcelona, Bayern, Atlético …). Agrees with each club's pre-match Elo in its last game before the entry date (median absolute difference 0–5.5 points, max 30).
- **Coverage limits:** the mirror holds 19 countries (ENG, ESP, ITA, FRA, GER, TUR, NED, POR, ROM, BEL, POL, RUS, GRE, SWE, NOR, SCO, DEN, AUT, FIN): the top two tiers in the big countries and mostly the top tier elsewhere. Clubs in Switzerland, Ireland, Ukraine and Czechia have no Elo in the mirror, although the full ClubElo API would rate them; English League One/Two clubs are not rated by ClubElo either way. Provisional coverage (fuzzy club-name match, before notebook 03 overrides): 78.1% of the 2,488 entrants with potential ≥ 75 (75–79: 76.1%, 80–84: 81.5%, 85+: 91.3%); 90.8% of those at European clubs.
- **API:** the retry loop keeps running until Thu 5 Nov 10:00. If it succeeds before notebook 03 runs, notebook 03 uses the API snapshots instead, and that is recorded here.
- **Alternatives:** EUfootball R package `Matches` (Elo from clubelo.com, 7 leagues from 2010/11): not needed, as the mirror covers more leagues.

### 2026-11-04 · FIFA ranking: what "semester 1" contains (finding, no change)
- **Finding:** The world number 1 in each semester-1 list matches FIFA's **July** release, not the June one: Germany in 2014 (took over in July, after the World Cup), Argentina in 2015 (from July 2015) and Germany in 2017 (took back the lead from Brazil in July 2017). In 2018, when there was no July release, it matches the June list (Germany). So semester 1 is probably the mid-year list in force in July.
- **Effect:** None. Every edition launched in August or September, after any July release, so each edition still uses that year's semester-1 list under the approved 30 June rule. The ranking date is stored as 30 June as decided. (The 2007 Montenegro rows that appear twice in the raw file are outside the window and never used.)

### 2026-11-04 · Nations: ISO3, home nations, ranking key, confederation
- **ISO3:** from `pycountry` exact lookup (145 nations) or a hand-checked list in `src/nations.py` (43); no fuzzy guesses. FIFA trigrams are not reused as ISO codes. England, Scotland, Wales and Northern Ireland all map to **GBR** on the world map (CLAUDE.md §8), so chart 8 must combine them into one GBR row (or show them as a note); notebook 11 decides how. Kosovo uses `XKX` (not an official ISO code); check that the Datawrapper world map recognises it when building chart 8.
- **Ranking key:** FIFA nationality names are joined to the ranking through its trigram (`acronym`; LIB is aliased to LBN), because team names change over the years (Turkey/Türkiye, Czech Republic/Czechia, FYR/North Macedonia). Eight FIFA names needed a seeded override (e.g. United States → USA, Iran → IR Iran). Kosovo (not ranked before 2016) and Gibraltar (before 2017) have no rank in early editions; 3 cohort entrants lack a nation rank at entry (99.97% coverage).
- **Confederation:** from Transfermarkt `national_teams.csv`; `countries.csv` only has continents and lumps CONMEBOL and CONCACAF together as "amerika", so it is not used for the Americas. Four TM spellings were seeded (Ireland, Türkiye, "Korea, South", Bosnia-Herzegovina). Five chart-9 nations are in neither TM table: Cameroon, Congo DR, Côte d'Ivoire, Guinea, Mali (all CAF). Left blank pending approval of a hand lookup via the `confederation` column in `data/manual/nation_name_overrides.csv`.

### 2026-11-04 · Confederation: hand lookup for five CAF nations (approved by Sahil)
- **Decision:** Cameroon, Congo DR, Côte d'Ivoire, Guinea and Mali are set to **CAF** in `data/manual/nation_name_overrides.csv`, with source "hand lookup: CAF member". `nation_iso.parquet` records that text in `confederation_source`. All 61 chart-9 nations now have a confederation.
- **Reason:** None of the five is in Transfermarkt's `national_teams.csv` or `countries.csv`; CAF membership is a stable public fact.
- **Alternatives:** Leave blank and colour them "unknown" in chart 9.

### 2026-11-04 · FIFA `league_name` is anachronistic: use `league_name_edition`
- **Finding:** In `male_players.csv` (and `male_teams.csv`), `league_name` is each club's **FC 24** league repeated across all editions. Luton Town shows as "Premier League" in FIFA 15–17 (they were in League Two; league_id 61, level 4). 26,973 rows in FIFA 15–23 carry a league name that is wrong for their edition. `league_id` and `league_level` are correct per edition, and `club_name` is constant per club id.
- **Decision:** Notebook 01 adds `league_name_edition` (the FC 24 name of each `league_id`, plus 8 hand-identified ids missing from FC 24 in `config.LEAGUE_ID_MANUAL`, e.g. 51 = Scottish Championship, 2025 = Brasileiro Série B) and `league_country` (from `male_teams.nationality_name`). All per-edition logic uses these; `league_name` is kept for reference only. Notebooks 02 and 04 were re-run on the updated cohort; their results are unchanged (6,581 matches), except notebook 02's diagnostic league table.
- **Alternatives:** Modal league name per league_id (fragile); drop league names entirely.

### 2026-11-04 · Club mapping to ClubElo (notebook 03)
- **Method:** within the same country, in this order: (1) reserve/B sides (`B`, `II`, `Castilla`, `Jong`, `Sevilla Atlético`…) are never mapped, as ClubElo doesn't rate them; (2) `data/manual/club_name_overrides.csv`; (3) a **unique** ClubElo name whose expanded words all appear in the FIFA name ("West Brom" ⊂ "West Bromwich Albion", "Man United" ⊂ "Manchester United"); (4) fuzzy (mean of token-set and token-sort ratio) ≥ 90 with a 5-point lead. Plain fuzzy matching was rejected after it produced Colchester → "Man United" and Sporting CP → "Sp Braga". A check rejects any ClubElo club claimed by two FIFA clubs; it caught Fortuna Köln → "FC Koln" and GFC Ajaccio → "Ajaccio", both fixed by overrides.
- **Overrides:** 32 rows seeded by Claude for top-two-tier clubs the rules can't resolve (Lyon, PSV, Bayern, Sporting CP, Athletic Club, Wolves, QPR, Malmö, İstanbul Başakşehir → "Buyuksehyr"…), each with a note; Devarshi to check. FC Ural Yekaterinburg → "Sverdlovsk" is by elimination (the only unassigned Russian name rated in all four seasons 2014–18) and is flagged "please verify".
- **Result:** every European club with 3+ cohort players in a mirror country is mapped or explicitly not rated. Clubs that map to nothing and played below the second tier at entry are "not rated: lower tier" (e.g. German 3. Liga). Elo is taken from the entry-date snapshot only; a mapped club absent from that snapshot (relegated that season) gets no Elo ("mapped, not rated on entry date", 26 entrants).
- **Coverage, potential ≥ 75:** 97.3% of 2,036 entrants at clubs in mirror countries (excluding English League One/Two) have an Elo at entry (75–79: 97.5%, 80–84: 97.1%, 85+: 96.0%); target was ≥ 90%. Of all 2,488 potential-75+ entrants, 79.6% have an Elo; the rest are outside Europe (13.4%), known gaps (4.1%), reserve sides (1.9%), no club (0.6%) or lower tier (0.2%).

### 2026-11-04 · Limitation: club strength known gaps (left blank, never estimated)
- **Not in the mirror** (the full ClubElo API would rate them): clubs in **Switzerland, Republic of Ireland, Ukraine and Czechia**: 499 cohort entrants, 41 of them with potential ≥ 75 (Switzerland 32, Ukraine 5, Ireland 2, Czechia 2).
- **Not rated by ClubElo:** **English League One and League Two** (identified by `league_name_edition` + England): 1,074 entrants, 62 with potential ≥ 75.
- Also unrated by design: reserve/B sides (96 entrants; FC Barcelona B, Athletic Club B, Sevilla Atlético, Werder Bremen II) and other third-tier clubs (88 entrants). Non-European clubs (2,351 entrants) get NaN and `non_european_club = True` (§6).
- **Effect on chart 10:** per-club means use only clubs with an Elo; the chart notes should say that Swiss, Irish, Ukrainian, Czech and English third/fourth-tier clubs are absent.

### 2026-11-04 · Sources list: ClubElo mirror credit
- **Decision:** Added "Club Football Match Data (2000–2025), Kaggle, by adamgbor; Elo data from ClubElo" to the CLAUDE.md §5 sources table (row 3b), the README and `config.SOURCES`; `config.CHART_SOURCES[10]` credits FIFA, the mirror and ClubElo, so chart 10's source line credits both, as the mirror's author asks.

### 2026-11-04 · Notebook 00: ClubElo mirror fallback built in
- **Decision:** Notebook 00 now tries the API for all 10 edition dates, then builds a mirror snapshot for any of the 4 cohort entry dates the API didn't return (`src.clubelo.build_mirror_snapshot`, same as `scripts/build_clubelo_mirror.py`). It checks that all 4 entry dates are covered. The other 6 dates are reported as a note, not a failure. The mirror dataset is part of the source check and the inventory.
- **Reason:** The earlier "all 10 snapshots cached" check failed by design while the API is down, so a teammate's fresh run stopped at notebook 00. Only the entry dates are used (§6 club strength at entry).
- **Alternatives:** Keep the failing check and tell teammates to ignore it (breaks "run top to bottom").

### 2026-11-04 · Latest transfer: as of the data snapshot date, not today (notebook 02)
- **Decision:** A player's latest transfer is the most recent one dated on or before the Transfermarkt snapshot date (its last recorded appearance, 2026-06-28). 3,322 later-dated rows are ignored.
- **Reason:** Transfermarkt pre-records contract expiries as moves to "Without Club" on 1 July (719 rows in July 2026). Against "today", players such as Goretzka (Bayern) and Sterling (Feyenoord) were wrongly read as having no club.
- **Alternatives:** Today's date (previous rule).

### 2026-11-04 · Notebook 05: analysis choices
- **Real-life "made it" denominator:** all cohort entrants; unmatched entrants count as not made it (every player with a Big-5 appearance is in TM `players.csv`). The matched-only share is reported alongside in `findings.json` (`made_it_matched_only_pct`). They differ most in the low bands (<70: 3.9% vs 9.6%) and little at 80+ (45.8% vs 50.7%; 68.3% vs 69.6%).
- **Busts (chart 6):** the 10 largest gaps among **wonderkids** (potential ≥ 85) with a later edition. Ranked by raw gap, the top busts would be obscure lower-league players (E. Simonsen 77 → 51). **Bloomers:** the 10 most negative gaps among entrants whose peak later rating reached 80+. Ties: higher potential (busts) or higher peak (bloomers), then name.
- **Chart 12 attributes:** the 37 in-game rated attributes at entry (6 face stats, 29 detailed ones without goalkeeping, plus weak foot and skill moves), outfield players only, against peak later − potential. Age, height and weight are not FIFA attributes; they are reported separately (age is the strongest correlate, ρ = 0.20: older entrants beat their potential more). All attribute correlations are weak (|ρ| ≤ 0.11), so chart 12's title should say so.
- **Spearman:** computed as Pearson on ranks over pairwise-complete rows (identical to Spearman; avoids adding `scipy`).
- **Latest-club tier (chart 14, provisional; notebook 12 owns it):** `src/outcomes.latest_club_tier`: unmatched → "Not in Transfermarkt"; latest transfer to Retired/Without Club → "No current club"; active in a TM-covered league in 2025/26 → Big-5 / Other European top flight / Outside Europe (by TM competition continent); otherwise → "Other or lower league". Known limit: moves TM doesn't record (Verratti to Qatar) stay "Other or lower league".
- **Already peaked:** 0 cohort entrants and 1 learning-cohort entrant, excluded from accuracy metrics.
- **Provisional:** 174 players are still pending Transfermarkt match review, and the club overrides are seeded but not yet checked. `findings.json` has a `provisional` section; re-run 02 → 05 after the reviews.

### 2026-11-05 · ClubElo API: retry deadline passed
- The retry loop ended at its Thu 5 Nov 10:00 deadline without a single successful call (5 rounds ran; the laptop slept overnight). api.clubelo.com still returned 502 at 13:47. The approved mirror stays the source for the four entry dates; no further retries are scheduled.

### 2026-11-05 · Robustness tests in notebook 05 (story revision)
- **Method:** 95% percentile bootstrap over players (`BOOTSTRAP_REPS` = 1,000, `RANDOM_SEED` = 6600 in config). A finding counts only if its interval excludes "no effect".
- **New outcome measures (notebook 02):** Big-5 minutes within 5 years of entry (`made_it_5y`; equal follow-up for every cohort, FIFA 18 + 5 years = Sept 2022, inside the data) and 3,000+ minutes in any Transfermarkt-covered top flight (`made_it_top_flight`). Peak market value ≥ €10m is a fourth measure.
- **Benchmark:** OLS of peak later rating on overall + age, fitted leave-one-entry-edition-out (trained on the other three editions). It replaces the ad hoc "overall + 2.5 × (21 − age)" rule from the 4 Nov quick check. That rule was in-sample and hand-weighted, and it overstated the case against potential.
- **Club effect among elite prospects:** OLS of gap on club Elo/100 + potential + age, players with potential ≥ 80 and an Elo at entry.
- **Vanished check:** whether the entry league disappears from the next edition (licensing), and whether the player kept playing in a covered top flight.
- **Results:** all in `findings.json` sections `robust_*`; summary and proposed chart changes in `reports/chart_plan_v2.md` (awaiting team approval; CLAUDE.md §9.2 unchanged).

### 2026-11-05 · Final story and chart decisions (principal data scientist self-review)
- **Story:** "An inflated promise, but a useful ranking." EA multiplied wonderkid ratings 3.6× in five years while ability barely moved. Each 10 points of potential delivered about 6 points of real rating, and the hit rate fell from FIFA 15 to FIFA 20 entrants. The overrated were the youngest, strikers, goalkeepers and lower-league prospects; the club badge was not. As a ranking, potential predicted careers as well as the transfer market.
- **Self-review tests** (notebook 05 §4.9, `findings.json → self_review`):
  - *Survivorship:* calibration slope 0.61 baseline; 0.46 for players present in all 4 following editions; 0.78 if vanished players are treated as never improving. Never near 1. Chart 7's decline holds for full survivors (46% → 16%).
  - *Mechanical group effects:* with slope < 1, groups with higher potential show bigger raw gaps. Group charts use **shortfall vs similar prospects** (typical peak for that potential − actual). The age effect survives (≤17 vs 21: +3.5, CI excludes 0). The position story changes: after adjustment goalkeepers (+1.1) and strikers (+0.9) fall short most, and defensive midfielders (−1.0) and full-backs beat their promise.
  - *Club bias in the outcome:* the elite weak-club effect (−0.78 shortfall per +100 Elo) shows up in EA's own later ratings but not in a club-neutral real outcome (any-top-flight made it: +1.7 pts per +100 Elo, CI −1.0 to +4.2). **Dropped as a headline.** Chart 10 instead shows the badge premium at entry: +0.29 potential per +100 Elo for the same overall and age (about 1 point from a weak to an elite club), and big-club prospects beat their promise. A myth-bust.
  - *League mix:* England's shortfall shrinks but persists without League One/Two (+0.6, CI +0.1 to +1.1) vs Spain+France −1.8. Prospects in third and fourth tiers fall short by about 2.1. Chart 8's notes warn that nationality overlaps with league.
- **Benchmark correction:** the 4 Nov "one-line formula beats potential" claim was wrong (hand-weighted and in-sample). Out-of-sample, potential is slightly better than an overall + age model (AUC 0.713 vs 0.700) and level with market value (0.716).
- **Featured five** (all FIFA 15 entrants): Sterling (reached: 86 → 88, €160m peak), Živković (biggest bust: 86 → 70), Kane (late bloomer: 78 → 90), Depay (latest club outside Europe: Corinthians), Werner (peak = potential: 85 = 85). Recorded in `findings.json → featured_five`; the team may still override.
- **Chart changes vs CLAUDE.md v1:** 2 → promise inflation; 4 → Datawrapper scatter with y = x and calibration lines; 5 → game vs reality arrow plot; 7 → adds survivors-only line; 8 → shortfall map with CIs (UK pooled as GBR); 9 → age at entry (two panels, no dual axis); 10 → badge premium; 11 → position shortfall with CIs (Flourish); 12 → who predicted best (AUC with CIs). Tools stay 7 Flourish / 7 Datawrapper.
- **Palette check:** the §11 palette fails two accessibility checks (gold has 1.96:1 contrast on white; red vs teal ΔE 7.6 for deuteranopia). Kept as the team's palette with relief: gold marks always get a dark outline and a text label, and red/teal comparisons always carry direct labels or a second encoding. These rules are written into the chart specs.
- **Exports:** notebooks 10 (charts 1–7), 11 (8–11), 12 (12–14) write `outputs/charts/NN_*.csv` and `chart_specs.md` through `src/exports.py`; titles are built from `findings.json`, not typed. Previews: `outputs/chart_previews.html` via `scripts/render_chart_previews.py`.
