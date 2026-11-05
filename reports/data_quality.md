# Data quality log

One section per notebook, rewritten each time that notebook runs.

<!-- BEGIN 00 -->
## 00 Setup and download: source inventory

_Last run: 2026-11-04 20:41_

### Inventory

| Source | File | Rows | Columns | Date range | Notes |
|---|---|---|---|---|---|
| FIFA | fifa/male_players.csv | 180,021 | 109 | 2014-09-18 to 2023-09-22 | 10 editions (15–24), one launch snapshot each; 53,111 unique player_id |
| FIFA | fifa/male_teams.csv | 6,947 | 54 | 2014-09-18 to 2023-09-22 | Not used (CLAUDE.md: male_players.csv only) |
| FIFA | fifa/male_coaches.csv | 1,369 | 8 | DOB 1945-07-29 to 2005-01-11 | Not used (CLAUDE.md: male_players.csv only) |
| Transfermarkt | transfermarkt/appearances.csv | 1,894,350 | 13 | 2012-07-03 to 2026-06-28 |  |
| Transfermarkt | transfermarkt/club_games.csv | 177,916 | 11 |  | No date column; join to games on game_id |
| Transfermarkt | transfermarkt/clubs.csv | 796 | 17 | seasons 2012–2025 |  |
| Transfermarkt | transfermarkt/competitions.csv | 65 | 11 |  | Lookup table |
| Transfermarkt | transfermarkt/countries.csv | 124 | 8 |  | Lookup table |
| Transfermarkt | transfermarkt/game_events.csv | 1,274,469 | 11 | 2006-06-09 to 2026-07-06 |  |
| Transfermarkt | transfermarkt/game_lineups.csv | 3,179,016 | 10 | 2013-07-02 to 2026-07-06 |  |
| Transfermarkt | transfermarkt/games.csv | 88,958 | 23 | 2006-06-09 to 2026-07-06 |  |
| Transfermarkt | transfermarkt/national_teams.csv | 124 | 17 | seasons 2025–2025 |  |
| Transfermarkt | transfermarkt/player_valuations.csv | 656,301 | 6 | 2000-01-20 to 2026-06-12 |  |
| Transfermarkt | transfermarkt/players.csv | 50,149 | 26 | DOB 1968-07-31 to 2011-02-23 |  |
| Transfermarkt | transfermarkt/transfers.csv | 175,165 | 10 | 1993-07-01 to 2030-06-30 | 475 rows dated after today (max 2030-06-30) |
| FIFA ranking | fifa_ranking/fifa_mens_rank.csv | 13,130 | 8 | 1992 S2 to 2024 S2 (year + semester only) | 65 half-yearly periods; rank + points, no confederation |
| ClubElo mirror | club_elo_mirror/EloRatings.csv | 273,972 | 4 | 2000-07-01 to 2026-09-01 | ClubElo snapshots on the 1st and 15th of each month; ClubElo data through 2025-06-01 |
| ClubElo mirror | club_elo_mirror/Matches.csv | 238,858 | 6 | 2000-07-28 to 2026-09-03 | football-data.co.uk matches; used only for the level column |
| ClubElo | clubelo | 1,638 | 12 | 4 snapshots: 2014-09-18 to 2017-09-18 | one file per edition date, clubelo_YYYY-MM-DD.csv; rows summed over snapshots |
| ClubElo | clubelo/ (missing snapshots) |  |  | 2018-08-21, 2019-09-19, 2020-09-23, 2021-09-23, 2022-09-26, 2023-09-22 | NOT DOWNLOADED: ConnectionError: Could not download http://api.clubelo.com/2018-08-21. |

### ClubElo download status

| Edition | Date | Status | Clubs | Error |
|---|---|---|---|---|
| FIFA 15 | 2014-09-18 | FAILED |  | ConnectionError: Could not download http://api.clubelo.com/2014-09-18. |
| FIFA 16 | 2015-09-21 | FAILED |  | ConnectionError: Could not download http://api.clubelo.com/2015-09-21. |
| FIFA 17 | 2016-09-20 | FAILED |  | ConnectionError: Could not download http://api.clubelo.com/2016-09-20. |
| FIFA 18 | 2017-09-18 | FAILED |  | ConnectionError: Could not download http://api.clubelo.com/2017-09-18. |
| FIFA 19 | 2018-08-21 | FAILED |  | ConnectionError: Could not download http://api.clubelo.com/2018-08-21. |
| FIFA 20 | 2019-09-19 | FAILED |  | ConnectionError: Could not download http://api.clubelo.com/2019-09-19. |
| FIFA 21 | 2020-09-23 | FAILED |  | ConnectionError: Could not download http://api.clubelo.com/2020-09-23. |
| FIFA 22 | 2021-09-23 | FAILED |  | ConnectionError: Could not download http://api.clubelo.com/2021-09-23. |
| FIFA 23 | 2022-09-26 | FAILED |  | ConnectionError: Could not download http://api.clubelo.com/2022-09-26. |
| FC 24 | 2023-09-22 | FAILED |  | ConnectionError: Could not download http://api.clubelo.com/2023-09-22. |

### Checks

| Check | Result | Detail |
|---|---|---|
| All Kaggle source files present | PASS |  |
| FIFA: one snapshot date per edition | PASS |  |
| FIFA: editions are exactly 15–24 | PASS |  |
| FIFA: edition dates match CLAUDE.md section 7 | PASS |  |
| TM: required tables present (players, player_valuations, appearances, clubs, competitions) | PASS |  |
| TM players: columns ['player_id', 'date_of_birth', 'name', 'first_name', 'last_name', 'current_club_id'] | PASS |  |
| TM appearances: columns ['player_id', 'date', 'minutes_played', 'competition_id', 'player_club_id'] | PASS |  |
| TM competitions: columns ['competition_id', 'name', 'type', 'country_name'] | PASS |  |
| TM player_valuations: columns ['player_id', 'date', 'market_value_in_eur'] | PASS |  |
| TM clubs: columns ['club_id', 'name', 'domestic_competition_id'] | PASS |  |
| TM: Big-5 competition IDs (GB1, ES1, L1, IT1, FR1) all in competitions | PASS |  |
| TM players: date_of_birth parses | PASS | 99.9% of 50,149 players have a parseable DOB |
| TM appearances: minutes_played is numeric | PASS | range 0–148 |
| Ranking: covers every half-year 2014–2023 | PASS | 1992 S2 to 2024 S2 |
| Ranking: column `rank` exists | PASS |  |
| Ranking: column `team` exists | PASS |  |
| ClubElo mirror snapshots: 300+ clubs and no duplicate clubs | PASS |  |
| ClubElo: a snapshot (API or mirror) for each of the 4 cohort entry dates | PASS | 4/4; mirror used for ['2014-09-18', '2015-09-21', '2016-09-20', '2017-09-18'] |

### Flags for later notebooks

- Transfermarkt `players` has no separate short-name column (only `first_name`, `last_name`, `name`). CLAUDE.md §8 (notebook 02) mentions TM 'full and short names'; notebook 02 must decide what to compare against FIFA `short_name`.
- Transfermarkt Big-5 appearances start at ES1 2012-08-18, FR1 2012-08-10, GB1 2012-08-18, IT1 2012-08-25, L1 2012-08-24. Notebook 02 must check coverage across all leagues and record it in DECISIONS.md.
- FIFA ranking has year + semester (1 or 2) only, no exact publication dates: 65 periods, two per year. 'Latest ranking date on or before the edition date' (CLAUDE.md §6) cannot be applied literally; notebook 04 must decide how to map a semester to a date and record it in DECISIONS.md.
- FIFA ranking has no confederation column. Transfermarkt `national_teams.csv` and `countries.csv` have one, which notebook 04 could join for chart 9.
- FIFA ranking has 2,733 tied (date, semester, rank) rows across all years; 360 of them in 2014–2023.
- ClubElo API: 6 non-entry edition snapshots not downloaded (ConnectionError: Could not download http://api.clubelo.com/2018-08-21.). Not needed: club strength is only measured at the 4 cohort entry dates.
- ClubElo: the API did not return the cohort entry dates ['2014-09-18', '2015-09-21', '2016-09-20', '2017-09-18']; mirror snapshots used (Club Football Match Data (2000–2025), Kaggle, by adamgbor; Elo data from ClubElo).
<!-- END 00 -->

<!-- BEGIN 01 -->
## 01 FIFA clean

_Last run: 2026-11-04 20:14_

### Filters (cohort)

| Step | Rows before | Rows after | Dropped |
|---|---|---|---|
| FIFA panel (all editions, all ages) | 180,021 | 180,021 | 0 |
| Keep editions FIFA 15 to FIFA 18 | 180,021 | 68,438 | 111,583 |
| Keep rows with age <= 21 | 68,438 | 18,357 | 50,081 |
| Keep each player's first eligible edition only (first-entry rule) | 18,357 | 11,519 | 6,838 |

### Filters (learning cohorts)

| Step | Rows before | Rows after | Dropped |
|---|---|---|---|
| Keep editions FIFA 15 to FIFA 20 | 180,021 | 105,007 | 75,014 |
| Keep rows with age <= 21 | 105,007 | 27,463 | 77,544 |
| Keep each player's first eligible edition only (first-entry rule) | 27,463 | 15,914 | 11,549 |

### §7 regression: FIFA 15 under-21s by band

| Band | n | reached | vanished | mean_diff | n_expected | reached_expected | vanished_expected | mean_diff_expected |
|---|---|---|---|---|---|---|---|---|
| <70 | 2,634 | 1,032 | 774 | 0.81 | 2634.0 | 1032.0 | 774.0 | 0.81 |
| 70–74 | 1,064 | 301 | 132 | -2.63 | 1064.0 | 301.0 | 132.0 | -2.63 |
| 75–79 | 602 | 153 | 22 | -4.08 | 602.0 | 153.0 | 22.0 | -4.08 |
| 80–84 | 246 | 70 | 0 | -3.97 | 246.0 | 70.0 | 0.0 | -3.97 |
| 85+ | 48 | 7 | 1 | -4.15 | 48.0 | 7.0 | 1.0 | -4.15 |

### Missing values

Face stats (`pace` to `physic`) are blank for goalkeepers by design and left as NaN; GKs are excluded
from attribute analysis.

| Group | Rows | All six face stats blank | Any face stat blank |
|---|---|---|---|
| Goalkeepers | 20,025 | 20,024 | 20,024 |
| Outfield | 159,996 | 0 | 0 |

Missing rates (%) by edition. Missing counts across all editions: `value_eur` 2,153, `wage_eur` 1,848, `club_name` 1,865, `league_name` 1,865.

| Edition | value_eur missing % | wage_eur missing % | club_name missing % | league_name missing % |
|---|---|---|---|---|
| FC 24 | 0.54 | 0.47 | 0.47 | 0.47 |
| FIFA 23 | 0.48 | 0.42 | 0.42 | 0.42 |
| FIFA 22 | 0.38 | 0.32 | 0.32 | 0.32 |
| FIFA 21 | 1.25 | 1.19 | 1.24 | 1.24 |
| FIFA 20 | 1.35 | 1.3 | 1.3 | 1.3 |
| FIFA 19 | 1.33 | 1.29 | 1.29 | 1.29 |
| FIFA 18 | 1.34 | 1.31 | 1.31 | 1.31 |
| FIFA 17 | 1.76 | 1.27 | 1.27 | 1.27 |
| FIFA 16 | 1.8 | 1.34 | 1.39 | 1.39 |
| FIFA 15 | 1.92 | 1.48 | 1.48 | 1.48 |
| All editions | 1.2 | 1.03 | 1.04 | 1.04 |

### Outliers (logged, not dropped)

| Rule | Rows | Players |
|---|---|---|
| Age <= 16 | 220 | 220 |
| Age >= 40 | 234 | 157 |
| potential < overall | 0 | 0 |

### Cohort

- Cohort size: 11,519 entrants (FIFA 15 4,594, FIFA 16 2,521, FIFA 17 2,250, FIFA 18 2,154).
- Already peaked at entry (overall = potential), to be excluded from accuracy metrics: **0**.
- Status: Fell short 6,030, Vanished 2,758, Reached 2,731.
- Learning cohorts (FIFA 15 to 20): 15,914 entrants; already peaked: 1
  (FIFA 15 0, FIFA 16 0, FIFA 17 0, FIFA 18 0, FIFA 19 0, FIFA 20 1).

| Band | Fell short | Reached | Vanished | Total |
|---|---|---|---|---|
| <70 | 2,178 | 1,700 | 1,962 | 5,840 |
| 70–74 | 1,933 | 629 | 629 | 3,191 |
| 75–79 | 1,343 | 290 | 151 | 1,784 |
| 80–84 | 487 | 101 | 12 | 600 |
| 85+ | 89 | 11 | 4 | 104 |
| Total | 6,030 | 2,731 | 2,758 | 11,519 |

### Notes

- FIFA `league_name` is each club's FC 24 league repeated across editions; 26,973 rows (FIFA 15–23) carry a league name that is wrong for that edition. Added `league_name_edition` (from `league_id`) and `league_country` (from male_teams); use those.
- 1 goalkeeper row(s) have face stats filled in (Marlon Barninho FIFA 21). Left as is; GKs are excluded from attribute analysis anyway.
- 1,524 players have more than one DOB across editions (EA corrections). cohort.parquet keeps `dob` (at entry) plus `dob_variants` (all variants, '|'-separated) for notebook 02.
- 7 cohort entrants were aged over 21 in an earlier edition but 21 or under in their entry edition, because EA changed their DOB. Kept under the literal §6 rule; IDs: 228407, 235140, 225861, 214008, 224094, 221772, 220033.

### Checks

| Check | Result | Detail |
|---|---|---|
| Shape is 180,021 rows x 109 columns | PASS | got (180021, 109) |
| 53,111 unique player_id | PASS | got 53,111 |
| No duplicate (player_id, fifa_version) pairs | PASS | 0 duplicates |
| Rows per edition match | PASS |  |
| Date per edition matches (one date each) | PASS |  |
| Under-21s with potential >= 85 per edition match | PASS |  |
| FIFA 15 under-21s = 4,594 | PASS | got 4,594 |
| FIFA 15 band table: n matches | PASS |  |
| FIFA 15 band table: reached matches | PASS |  |
| FIFA 15 band table: vanished matches | PASS |  |
| FIFA 15 band table: mean_diff matches | PASS |  |
| Every primary position maps to a position group | PASS |  |
| Adding league context keeps the row count | PASS | 180,021 |
| Every league_id has an edition league name | PASS | 0 rows |
| Every club row has a league country | PASS | 0 rows |
| No outfield row is missing a face stat | PASS | 0 rows |
| No row has potential < overall | PASS | 0 rows |
| Each player appears once in the cohort | PASS |  |
| All entries are in FIFA 15 to 18 with age <= 21 | PASS |  |
| Peak later rating comes from a later edition | PASS |  |
| Peak within 4 is within entry+1..entry+4 | PASS |  |
| Peak within 4 <= peak later | PASS |  |
| Status counts sum to the cohort size | PASS | {'Fell short': 6030, 'Vanished': 2758, 'Reached': 2731} = 11,519; cohort 11,519 |
| Vanished <=> no later edition | PASS |  |
| Gap is NaN exactly for Vanished | PASS |  |
| FIFA 15 entrants = all FIFA 15 under-21s (4,594) | PASS | 4,594 |
| FIFA 15 wonderkids in cohort = 48 | PASS | 48 |
| Learning: each player appears once | PASS |  |
| Learning: every entry edition has 4 follow-up editions in the data | PASS |  |
| Learning: FIFA 15 to 18 entries identical to the cohort | PASS |  |
| Learning: status-within-4 counts sum to size | PASS | {'Fell short': 9535, 'Vanished': 4154, 'Reached': 2225} |
<!-- END 01 -->

<!-- BEGIN 02 -->
## 02 Transfermarkt match

_Last run: 2026-11-04 20:47_

### Match results

| Method | Players |
|---|---|
| auto | 6,581 |
| unmatched | 4,869 |
| pending_review | 69 |

Raw match class (before overrides): auto 6,599, no_match_below_70 4,848, review_low_score 40, no_dob_candidate 21, review_tie 11.

### Match rate by potential band (accepted matches; pending review counts as unmatched)

| Band | entrants | matched | pending_review | match_rate_% |
|---|---|---|---|---|
| <70 | 5,840 | 2,376 | 40 | 40.7 |
| 70–74 | 3,191 | 2,101 | 18 | 65.8 |
| 75–79 | 1,784 | 1,460 | 8 | 81.8 |
| 80–84 | 600 | 542 | 1 | 90.3 |
| 85+ | 104 | 102 | 2 | 98.1 |
| All | 11,519 | 6,581 | 69 | 57.1 |

### Review queue

`reports/match_review.csv`: 231 players, 612 candidate rows.

| Reason | Players |
|---|---|
| potential 85+ | 104 |
| no exact-DOB match (potential 80+) | 57 |
| score 70-84 | 40 |
| TM id matched twice | 18 |
| tie | 11 |
| GK flag differs | 5 |

### Appearance coverage

7 competition(s) have records starting after the first entry date (2014-09-18).
Big-5 seasons with fewer than half the median appearance count: none.

| competition_id | name | type | first | last | appearances |
|---|---|---|---|---|---|
| FIWC | world-cup | national_team_competition | 2026-06-11 | 2026-06-28 | 2,251 |
| EJPL | jupiler-pro-league-playoff-i | other | 2026-04-04 | 2026-05-24 | 927 |
| BPO4 | jupiler-pro-league-relegation-play-offs | other | 2026-04-04 | 2026-05-09 | 374 |
| POBE | jupiler-pro-league-europe-play-offs | other | 2026-04-03 | 2026-05-23 | 931 |
| AFCN | africa-cup-of-nations | national_team_competition | 2025-12-21 | 2026-01-18 | 776 |
| CGB |  |  | 2023-08-08 | 2026-03-22 | 2,348 |
| ECLQ | uefa-conference-league-qualifying | other | 2021-07-08 | 2025-08-28 | 9,864 |
| KLUB |  |  | 2012-12-13 | 2025-07-13 | 1,808 |
| FAC | fa-cup | domestic_cup | 2012-11-03 | 2026-04-26 | 14,028 |
| GRP | kypello-elladas | domestic_cup | 2012-10-24 | 2026-04-25 | 15,505 |
| SFA | scottish-fa-cup | domestic_cup | 2012-09-29 | 2026-04-19 | 7,439 |
| NLP | knvb-beker | domestic_cup | 2012-09-25 | 2026-04-19 | 10,574 |
| EL | uefa-europa-league | other | 2012-09-20 | 2026-05-07 | 55,834 |
| CL | uefa-champions-league | international_cup | 2012-09-18 | 2026-05-06 | 49,536 |
| USC | uefa-super-cup | international_cup | 2012-08-31 | 2025-08-13 | 407 |
| DKP | oddset-pokalen | domestic_cup | 2012-08-29 | 2026-03-08 | 9,590 |
| CDR | copa-del-rey | domestic_cup | 2012-08-29 | 2026-04-18 | 17,430 |
| IT1 | serie-a | domestic_league | 2012-08-25 | 2026-05-24 | 155,187 |
| GR1 | super-league-1 | domestic_league | 2012-08-25 | 2026-03-22 | 87,752 |
| L1 | bundesliga | domestic_league | 2012-08-24 | 2026-05-16 | 124,613 |
| SUC | supercopa | other | 2012-08-22 | 2026-01-11 | 973 |
| ES1 | laliga | domestic_league | 2012-08-18 | 2026-05-24 | 153,877 |
| GB1 | premier-league | domestic_league | 2012-08-18 | 2026-05-24 | 149,751 |
| TR1 | super-lig | domestic_league | 2012-08-17 | 2026-05-17 | 132,464 |
| PO1 | liga-portugal | domestic_league | 2012-08-17 | 2026-05-16 | 119,936 |
| DFB | dfb-pokal | domestic_cup | 2012-08-17 | 2026-04-23 | 11,370 |
| DFL | franz-beckenbauer-supercup | other | 2012-08-12 | 2025-08-16 | 411 |
| GBCS | community-shield | other | 2012-08-12 | 2025-08-10 | 415 |
| POSU | supercup-candido-de-oliveira | other | 2012-08-11 | 2025-07-31 | 393 |
| SCI | supercoppa-italiana | other | 2012-08-11 | 2025-12-22 | 597 |
| FR1 | ligue-1 | domestic_league | 2012-08-10 | 2026-05-17 | 143,395 |
| NL1 | eredivisie | domestic_league | 2012-08-10 | 2026-05-17 | 120,019 |
| NLSC | johan-cruijff-schaal | other | 2012-08-05 | 2025-08-03 | 370 |
| CIT | italy-cup | domestic_cup | 2012-08-05 | 2026-04-22 | 11,337 |
| SC1 | scottish-premiership | domestic_league | 2012-08-04 | 2026-04-12 | 81,189 |
| BE1 | jupiler-pro-league | domestic_league | 2012-07-28 | 2026-03-22 | 100,926 |
| POCP |  |  | 2012-07-28 | 2026-01-10 | 9,769 |
| FRCH | trophee-des-champions | other | 2012-07-28 | 2026-01-08 | 401 |
| UKRP | ukrainian-cup | domestic_cup | 2012-07-25 | 2026-04-22 | 6,613 |
| BESC | volkswagen-supercup | other | 2012-07-22 | 2025-07-20 | 372 |
| RU1 | premier-liga | domestic_league | 2012-07-20 | 2026-05-17 | 95,397 |
| RUSS | russian-super-cup | other | 2012-07-14 | 2025-07-12 | 407 |
| UKR1 | premier-liga | domestic_league | 2012-07-13 | 2026-05-24 | 76,312 |
| DK1 | superliga | domestic_league | 2012-07-13 | 2026-03-01 | 65,284 |
| RUP | russian-cup | domestic_cup | 2012-07-11 | 2026-05-07 | 14,883 |
| UKRS |  |  | 2012-07-09 | 2021-09-22 | 275 |
| ELQ | uefa-europa-league-qualifying | other | 2012-07-05 | 2025-08-28 | 19,460 |
| CLQ | uefa-champions-league-qualifying | international_cup | 2012-07-03 | 2025-08-27 | 10,580 |

### Real outcomes

- Matched players: 6,581. With no valuation after entry: 323.
- Latest transfer is taken on or before the data snapshot date (2026-06-28); 3322 later-dated transfers are ignored.

| Band | matched | made_it_1500_% | made_it_3000_% | made_it_5000_% |
|---|---|---|---|---|
| <70 | 2,376 | 12.5 | 9.6 | 7.4 |
| 70–74 | 2,101 | 18.5 | 14.7 | 11.6 |
| 75–79 | 1,460 | 32.7 | 27.4 | 22.0 |
| 80–84 | 542 | 58.5 | 50.7 | 44.3 |
| 85+ | 102 | 74.5 | 69.6 | 62.7 |

### Notes

- 49 Transfermarkt players have no usable date of birth and cannot be matched.

### Checks

| Check | Result | Detail |
|---|---|---|
| TM player_id is unique | PASS |  |
| Override file is valid | PASS |  |
| No TM player is accepted for two FIFA players | PASS |  |
| Match rate >= 90% in band 80–84 | PASS | 90.3% |
| Match rate >= 90% in band 85+ | PASS | 98.1% |
| Crosswalk has one row per cohort entrant | PASS |  |
| TM appearance_id is unique | PASS |  |
| Real outcomes: one row per matched player | PASS |  |
| All valuations used are after the entry date | PASS |  |
| Big-5 minutes are non-negative | PASS |  |
| made_it flags are nested (5000 ⊆ 3000 ⊆ 1500) | PASS |  |
<!-- END 02 -->

<!-- BEGIN 04 -->
## 04 FIFA ranking

_Last run: 2026-11-04 20:15_

### Ranking period used per edition (semester 1 = 30 June, semester 2 = 31 December)

| edition_label | edition_date | year | semester | ranking_date |
|---|---|---|---|---|
| FIFA 15 | 2014-09-18 | 2,014 | 1 | 2014-06-30 |
| FIFA 16 | 2015-09-21 | 2,015 | 1 | 2015-06-30 |
| FIFA 17 | 2016-09-20 | 2,016 | 1 | 2016-06-30 |
| FIFA 18 | 2017-09-18 | 2,017 | 1 | 2017-06-30 |
| FIFA 19 | 2018-08-21 | 2,018 | 1 | 2018-06-30 |
| FIFA 20 | 2019-09-19 | 2,019 | 1 | 2019-06-30 |
| FIFA 21 | 2020-09-23 | 2,020 | 1 | 2020-06-30 |
| FIFA 22 | 2021-09-23 | 2,021 | 1 | 2021-06-30 |
| FIFA 23 | 2022-09-26 | 2,022 | 1 | 2022-06-30 |
| FC 24 | 2023-09-22 | 2,023 | 1 | 2023-06-30 |

### Name mapping

- FIFA nations: 188; mapped to the ranking: 188
  (exact 180, override 8).
- Cohort entrants with a nation rank at entry: 99.97%.
- ISO3: exact 145, manual 43; England, Scotland, Wales and
  Northern Ireland → GBR.
- Confederation: TM national_teams 118, missing 65, hand lookup: CAF member 5.
  Chart-9 nations (n ≥ 15): 61, of which 0 have no confederation
  (100.0% of their entrants covered).

### Notes

- 4 duplicated (team, period) rows in the raw ranking, all outside 2014–2023: Montenegro 2007 S1, Montenegro 2007 S2. Identical copies; they are never used.

### Checks

| Check | Result | Detail |
|---|---|---|
| Ranking covers every half-year 2014–2023 | PASS | 1992-12-31 to 2024-12-31 |
| No duplicate (key, period) rows in 2014–2023 | PASS | 4 duplicate rows elsewhere (logged) |
| Ranks are positive integers | PASS |  |
| Every edition uses that year's semester 1 ranking | PASS |  |
| Override file has the expected columns | PASS |  |
| Override file lists each FIFA nation once | PASS |  |
| Every override ranking_team exists in the ranking | PASS | [] |
| Every FIFA nation with a cohort entrant maps to the ranking | PASS | 0 entrants unmapped |
| nation_rank: one row per (nation, edition) | PASS |  |
| Cohort entrants with a nation rank at entry >= 99% | PASS | 99.97% of 11,519 |
| Every FIFA nation has an ISO3 code | PASS | [] |
| nation_iso: one row per FIFA nation | PASS |  |
<!-- END 04 -->

<!-- BEGIN 03 -->
## 03 ClubElo

_Last run: 2026-11-04 20:19_

### Snapshots used

| Edition | Date | Source | Rating date | Clubs |
|---|---|---|---|---|
| FIFA 15 | 2014-09-18 | mirror: Kaggle adamgbor/club-football-match-data-2000-2025 (ClubElo ratings) | 2014-09-15 | 415.0 |
| FIFA 16 | 2015-09-21 | mirror: Kaggle adamgbor/club-football-match-data-2000-2025 (ClubElo ratings) | 2015-09-15 | 406.0 |
| FIFA 17 | 2016-09-20 | mirror: Kaggle adamgbor/club-football-match-data-2000-2025 (ClubElo ratings) | 2016-09-15 | 409.0 |
| FIFA 18 | 2017-09-18 | mirror: Kaggle adamgbor/club-football-match-data-2000-2025 (ClubElo ratings) | 2017-09-15 | 408.0 |
| FIFA 19 | 2018-08-21 | missing |  |  |
| FIFA 20 | 2019-09-19 | missing |  |  |
| FIFA 21 | 2020-09-23 | missing |  |  |
| FIFA 22 | 2021-09-23 | missing |  |  |
| FIFA 23 | 2022-09-26 | missing |  |  |
| FC 24 | 2023-09-22 | missing |  |  |

### Club mapping

| Method | FIFA clubs |
|---|---|
| subset | 421 |
| country not in snapshots | 236 |
| lower tier (not rated) | 58 |
| override | 31 |
| fuzzy | 15 |
| reserve side (not rated) | 4 |
| override: not in ClubElo | 1 |

Rule matches whose normalised names differ (129, for review): Blackburn Rovers → Blackburn; Bolton Wanderers → Bolton; Leeds United → Leeds; Newcastle United → Newcastle; Tottenham Hotspur → Tottenham; West Ham United → West Ham; Borussia Dortmund → Dortmund; Borussia Mönchengladbach → MGladbach; Bayer 04 Leverkusen → Leverkusen; Birmingham City → Birmingham; Charlton Athletic → Charlton; Derby County → Derby; Ipswich Town → Ipswich; Leicester City → Leicester; West Bromwich Albion → West Brom; Doncaster Rovers → Doncaster; DSC Arminia Bielefeld → Bielefeld; VfL Bochum 1848 → Bochum; Hertha BSC → Hertha; Hamilton Academical → Hamilton; Hellas Verona → Verona; Olympique de Marseille → Marseille; Standard Liège → Standard; Deportivo de La Coruña → La Coruna; Real Zaragoza → Zaragoza; LASK Linz → LASK; AEK Athens → AEK; Olympiakos Piraeus → Olympiakos; Yeovil Town → Yeovil; Stade de Reims → Reims; Górnik Zabrze → Gornik; Real Betis → Betis; Celta de Vigo → Celta; Espanyol → Espanol; Racing Santander → Santander; Real Sociedad → Sociedad; Real Valladolid → Valladolid; Deportivo Alavés → Alaves; Rayo Vallecano → Vallecano; Hannover 96 → Hannover; Dynamo Dresden → Dresden; Jahn Regensburg → Regensburg; VfR Aalen → Aalen; RC Recreativo de Huelva → Recreativo; Inverness Caledonian Thistle → Inverness; ADO Den Haag → Den Haag; Vitória de Setúbal → Setubal; Desportivo das Aves → Aves; Sporting Charleroi → Charleroi; Sint-Truiden → St Truiden; Norrköping → Norrkoeping; Örebro → Oerebro; Häcken → Haecken; Lech Poznań → Lech; Ruch Chorzów → Ruch; Bodø / Glimt → Bodoe Glimt; Esbjerg fB → Esbjerg; Kayseri Erciyesspor → Erciyesspor; Sogndal Fotball → Sogndal; GIF Sundsvall → Sundsvall; Partick Thistle FC → Partick; Norwich City → Norwich; Rotherham United → Rotherham; Preston North End → Preston; Stoke City → Stoke; Brighton & Hove Albion → Brighton; US Créteil-Lusitanos → Creteil; MSV Duisburg → Duisburg; Karlsruher SC → Karlsruhe; Bari 1908 → Bari; Legia Warszawa → Legia; Wisła Kraków → Wisla; Associação Académica de Coimbra → Academica; Roda JC Kerkrade → Roda; PEC Zwolle → Zwolle; Wigan Athletic → Wigan; Huddersfield Town → Huddersfield; Hull City → Hull; Swansea City → Swansea; Cardiff City → Cardiff; Sporting Lokeren → Lokeren; Zulte-Waregem → Waregem; Rheindorf Altach → Altach; Cultural Leonesa → Leonesa; Burton Albion → Burton; Gimnàstic de Tarragona → Tarragona; Heracles Almelo → Heracles; FC Anzhi Makhachkala → Anzhi; Zenit St. Petersburg → Zenit; Göztepe → Goztep; SKA Khabarovsk → Khabarovsk; FC Mordovia Saransk → Mordovia; FC Tom Tomsk → Tomsk; Eintracht Braunschweig → Braunschweig; Darmstadt 98 → Darmstadt; Football Bourg En Bresse Peronnas 01 → Bourg Peronnas; GKS Bełchatów → Belchatow; Jagiellonia Białystok → Jagiellonia; Pogoń Szczecin → Pogon; Cracovia Kraków → Cracovia; Zagłębie Lubin → Lubin; Arsenal Tula → Tula; Real Oviedo → Oviedo; Waasland-Beveren → Beveren; Arka Gdynia → Arka; Korona Kielce → Korona; Lechia Gdańsk → Lechia; Śląsk Wrocław → Slask; SC Magna Wiener Neustadt → Wiener Neustadt; Royal Excel Mouscron → Mouscron; Wolfsberger AC → Wolfsberg; AC Arles Avignon → Arles; SV Grödig → Groedig; Mjällby → Mjaellby; St. Pölten → St Poelten; Kardemir Karabükspor → Karabukspor; Falkenberg → Falkenbergs; Sarpsborg 08 → Sarpsborg; US Orléans Loiret Football → Orleans; Sandnes Ulf → Sandnes; FC Pro Vercelli 1892 → Pro Vercelli; Hobro IK → Hobro; Zawisza Bydgoszcz → Zawisza; União da Madeira → Uniao Madeira; UE Llagostera → Llagostera; Virtus Entella Chiavari → Virtus Entella; Östersunds FK → Ostersund; Yeni Malatyaspor → Malatyaspor; Sirius → IK Sirius

### Club strength status, all cohort entrants

| Status | entrants | % |
|---|---|---|
| Elo at entry | 7,326 | 63.6 |
| Outside Europe | 2,351 | 20.4 |
| Known gap: English League One/Two | 1,074 | 9.3 |
| Known gap: country not in mirror | 499 | 4.3 |
| Reserve side (not rated) | 96 | 0.8 |
| Not rated: lower tier | 88 | 0.8 |
| No club | 59 | 0.5 |
| Mapped, not rated on entry date | 26 | 0.2 |

### Coverage, potential ≥ 75

Denominator: potential-75+ entrants at clubs in countries the snapshots cover, excluding English League One/Two (known gap).
Coverage: **97.3%** of 2,036. Share of all 2,488 potential-75+ entrants with an Elo: 79.6%.

| Band | entrants | with_elo | coverage_% |
|---|---|---|---|
| 75–79 | 1,420 | 1,384 | 97.5 |
| 80–84 | 516 | 501 | 97.1 |
| 85+ | 100 | 96 | 96.0 |
| All 75+ | 2,036 | 1,981 | 97.3 |

| Status | entrants | % of potential-75+ |
|---|---|---|
| Elo at entry | 1,981 | 79.6 |
| Outside Europe | 333 | 13.4 |
| Known gap: English League One/Two | 62 | 2.5 |
| Reserve side (not rated) | 48 | 1.9 |
| Known gap: country not in mirror | 41 | 1.6 |
| No club | 16 | 0.6 |
| Not rated: lower tier | 6 | 0.2 |
| Mapped, not rated on entry date | 1 | 0.0 |

### Notes

- none

### Checks

| Check | Result | Detail |
|---|---|---|
| A snapshot exists for each of the 4 cohort entry dates | PASS | missing: [] |
| No duplicate club within a snapshot | PASS |  |
| Elo values in a plausible range (1000–2300) | PASS | 1116–2101 |
| Each FIFA club id has one name and one country | PASS | 0 duplicates |
| Override file lists each FIFA club once | PASS |  |
| Override status is 'mapped' or 'not_in_clubelo' | PASS |  |
| Every mapped override names a ClubElo club in the universe | PASS | [] |
| No ClubElo club is claimed by two FIFA clubs | PASS |  |
| Every European club with 3+ cohort players is mapped or marked not rated | PASS | 0 open: [] |
| club_strength: one row per cohort entrant | PASS |  |
| No Elo for a non-European club | PASS |  |
| Coverage >= 90% for potential-75+ entrants at clubs in mirror countries (excl. English League One/Two) | PASS | 97.3% of 2,036 |
<!-- END 03 -->

<!-- BEGIN 05 -->
## 05 Analysis master

_Last run: 2026-11-04 20:47_

- analysis.parquet: 11,519 rows (one per cohort entrant), 140 columns.
- Already-peaked entrants excluded from accuracy metrics: 0.
- Real-life "made it" counts unmatched entrants as not made it (4,938 unmatched).
- Provisional: 174 players still pending Transfermarkt match review.

### Calibration

| Band | n | reached_% | fell_short_% | vanished_% | mean_gap | matched_to_TM_% | made_it_real_% | made_it_real_matched_only_% | made_it_1500_% | made_it_5000_% |
|---|---|---|---|---|---|---|---|---|---|---|
| <70 | 5,840 | 29.1 | 37.3 | 33.6 | 1.2 | 40.7 | 3.9 | 9.6 | 5.1 | 3.0 |
| 70–74 | 3,191 | 19.7 | 60.6 | 19.7 | 4.5 | 65.8 | 9.7 | 14.7 | 12.2 | 7.6 |
| 75–79 | 1,784 | 16.3 | 75.3 | 8.5 | 6.1 | 81.8 | 22.4 | 27.4 | 26.8 | 18.0 |
| 80–84 | 600 | 16.8 | 81.2 | 2.0 | 6.4 | 90.3 | 45.8 | 50.7 | 52.8 | 40.0 |
| 85+ | 104 | 10.6 | 85.6 | 3.8 | 6.8 | 98.1 | 68.3 | 69.6 | 73.1 | 61.5 |
| All | 11,519 | 23.7 | 52.3 | 23.9 | 3.5 | 57.1 | 11.1 | 19.5 | 13.5 | 9.1 |

### Checks

| Check | Result | Detail |
|---|---|---|
| analysis: one row per cohort entrant | PASS | 11,519 |
| Status counts sum to the cohort size | PASS |  |
| Chart 2 counts match CLAUDE.md §7 | PASS |  |
| Chart 12: attribute list has no duplicates | PASS | 37 attributes |
<!-- END 05 -->
