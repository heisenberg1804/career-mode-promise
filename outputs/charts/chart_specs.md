# Chart specs

One entry per chart, written by export notebooks 10–12.

<!-- BEGIN CHART 01 -->
## Chart 01: wonderkid_table
- File: outputs/charts/01_wonderkid_table.csv
- Tool / template: Datawrapper table (search on)
- Title (states the finding, numbers from findings.json): Only 7 of FIFA 15's 48 wonderkids reached their potential in the game, but 40 became Big-5 regulars
- Subtitle (what is measured, units): Under-21s rated potential 85+ in FIFA 15 (Sept 2014). Peak later rating = best overall in FIFA 16 to FC 24. Made it = 3,000+ Big-5 league minutes after Sept 2014
- Column → role mapping: columns in file order; Player bold; sort by Potential (desc); search on; 15 rows per page
- Colours: Status text colours: Reached #1B998B, Fell short #D1495B, Vanished #C5CAD3; Featured rows: background tint of #F2A900 at 15% opacity; Gap as a bar column (red #D1495B for positive)
- Tooltip (HTML): (tables have no tooltip)
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: Use Datawrapper's 'Highlight rows' for Featured = Yes. Make 'Made it' a coloured text column (Yes = reality green). Hide the Featured column after highlighting. Peak market value in € millions.
<!-- END CHART 01 -->

<!-- BEGIN CHART 02 -->
## Chart 02: promise_inflation
- File: outputs/charts/02_promise_inflation.csv
- Tool / template: Datawrapper column chart
- Title (states the finding, numbers from findings.json): The game handed out 3.6× more wonderkid ratings in five years: from 10.4 to 37.2 per 1,000 under-21s by FIFA 20
- Subtitle (what is measured, units): Under-21s rated potential 85+ per 1,000 under-21s in each edition. Over the same years average under-21 potential rose 5.2 points and average overall only 1.7
- Column → role mapping: x = Edition; y = Wonderkids per 1,000 under-21s; other columns tooltip only
- Colours: bars #F2A900; highlight the peak edition bar with a darker outline; axis/text #1D2433
- Tooltip (HTML): <b>{{ Edition }}</b><br>{{ Wonderkids per 1,000 under-21s }} per 1,000 under-21s<br>{{ Wonderkids (under-21, potential 85+) }} wonderkids of {{ Under-21s in game }} under-21s<br>Average headroom: {{ Average headroom (potential − overall) }} points
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: Keep editions as text categories in order. Add an annotation on the peak bar. Optional second panel: line of 'Average headroom (potential − overall)'. Population counts, not a sample, so no error bars.
<!-- END CHART 02 -->

<!-- BEGIN CHART 03 -->
## Chart 03: rating_trajectories
- File: outputs/charts/03_rating_trajectories.csv
- Tool / template: Flourish line chart
- Title (states the finding, numbers from findings.json): Five FIFA 15 prospects, five different endings
- Subtitle (what is measured, units): Overall rating in each edition, FIFA 15 (2014) to FC 24 (2023). Grey: median of FIFA 15's wonderkids
- Column → role mapping: x = Edition (category); one line per player column; 'FIFA 15 wonderkids (median)' as a context line
- Colours: featured players #F2A900 with end-of-line name labels (vary weight or dash so they stay distinguishable); median line #C5CAD3 dashed
- Tooltip (HTML): <b>{{ series }}</b> · {{ Edition }}<br>Overall rating: {{ value }}
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: Blank cells mean the player isn't in that edition: turn off 'Connect gaps' so Živković's line visibly stops. y axis 60–95. Label each line at its last point.
<!-- END CHART 03 -->

<!-- BEGIN CHART 04 -->
## Chart 04: promise_vs_reality
- File: outputs/charts/04_promise_vs_reality.csv
- Tool / template: Datawrapper scatter plot (moved from Flourish: needs reference lines)
- Title (states the finding, numbers from findings.json): Every 10 points of potential delivered only 6.1 points of real rating
- Subtitle (what is measured, units): 2,321 prospects with potential 75+ (FIFA 15–18 entrants). x = potential at entry, y = best later overall. 83% sit below the dashed line, where the promise was met
- Column → role mapping: x = Potential; y = Peak later rating; colour = Status; label = Player where Featured = Yes; tooltip = all columns
- Colours: Reached #1B998B, Fell short #D1495B (dots at 40% opacity, size 4); Featured dots #F2A900, size 8, labelled
- Tooltip (HTML): <b>{{ Player }}</b> ({{ Entry edition }}, {{ Position group }})<br>Potential: {{ Potential }}<br>Best later rating: {{ Peak later rating }}<br>{{ Club }} · {{ Nation }}
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: Add two custom lines (Annotate > Custom lines): 'Promise met' y = x from (75,75) to (95,95), dashed #1D2433; 'What potential actually delivered' from (75,69.7) to (95,82.0), solid #1B998B (calibration line: peak = 23.94 + 0.611 × potential, fitted on all entrants with a later edition). Slope 0.61 (95% CI 0.59–0.63); under alternative survivorship treatments it ranges 0.46–0.78, never near 1. Axes 60–95 (y) and 75–95 (x). Many dots share integer coordinates: use low opacity or Datawrapper's jitter.
<!-- END CHART 04 -->

<!-- BEGIN CHART 05 -->
## Chart 05: game_vs_reality
- File: outputs/charts/05_game_vs_reality.csv
- Tool / template: Datawrapper range plot (arrow)
- Title (states the finding, numbers from findings.json): The bigger the promise, the less often the number came true, and the more often the career did
- Subtitle (what is measured, units): Share of each potential band (FIFA 15–18 entrants aged 21 or under) that reached its potential in the game vs made it in real life (3,000+ Big-5 league minutes). 85+: 11% vs 68%; under 70: 29% vs 4%
- Column → role mapping: rows = Potential band (keep order <70 … 85+); range start = Reached potential in the game (%); range end = Made it in real life (%); arrows on
- Colours: start dot #F2A900 (the game's promise), end dot #1B998B (reality); arrow colour by direction (up = reality green, down = #D1495B)
- Tooltip (HTML): <b>Potential {{ Potential band }}</b> ({{ Players }} players)<br>Reached potential in the game: {{ Reached potential in the game (%) }}%<br>Made it in real life: {{ Made it in real life (%) }}%<br>Fell short: {{ Fell short in the game (%) }}% · Vanished: {{ Vanished from the game (%) }}%
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: x axis 0–100%. Label both ends with values. The crossing point (between 70–74 and 75–79) is the story: say so in an annotation.
<!-- END CHART 05 -->

<!-- BEGIN CHART 06 -->
## Chart 06: busts_and_bloomers
- File: outputs/charts/06_busts_and_bloomers.csv
- Tool / template: Datawrapper range plot
- Title (states the finding, numbers from findings.json): E. Abouchabaka fell 22 points short of his promise; Borja Iglesias beat his by 28
- Subtitle (what is measured, units): Busts: the 10 wonderkids (potential 85+) who fell furthest short. Bloomers: the 10 biggest overachievers among players who reached a peak of 80+
- Column → role mapping: rows = Player; range start = Potential at entry; range end = Peak later rating; group by Group (Bust / Bloomer)
- Colours: Potential dot #F2A900; peak dot #D1495B for busts, #2E86AB for bloomers
- Tooltip (HTML): <b>{{ Player }}</b> · {{ Entry edition }}, {{ Club at entry }}<br>Potential: {{ Potential at entry }} → best later: {{ Peak later rating }} ({{ Gap }})
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: Sort busts by gap (largest first), then bloomers by gap. Use Datawrapper's row grouping (a 'Group' column split) or two stacked charts. x axis 50–95.
<!-- END CHART 06 -->

<!-- BEGIN CHART 07 -->
## Chart 07: did_ea_learn
- File: outputs/charts/07_did_ea_learn.csv
- Tool / template: Flourish line chart
- Title (states the finding, numbers from findings.json): As the promises grew, fewer came true: 25% of FIFA 15 entrants reached theirs within four editions, 6% by FIFA 20
- Subtitle (what is measured, units): Share of each entry cohort reaching its potential within the next 4 editions. Dashed: only players present in all 4 editions (46% → 16%), so drop-outs don't drive the trend
- Column → role mapping: x = Entry edition; lines = 'Reached potential within 4 editions (%)' and 'Same, players present in all 4 editions (%)'; tooltip adds Mean gap within 4 editions
- Colours: main line #1B998B; survivors-only line #1B998B dashed; annotate the inflation peak (FIFA 20) in #F2A900
- Tooltip (HTML): <b>{{ Entry edition }}</b><br>Reached within 4 editions: {{ value }}%<br>Mean gap: {{ Mean gap within 4 editions }} points
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: y axis 0–50%. Pair with chart 2 in the text: the promise inflated while the hit rate fell.
<!-- END CHART 07 -->

<!-- BEGIN CHART 08 -->
## Chart 08: nation_map
- File: outputs/charts/08_nation_map.csv
- Tool / template: Datawrapper choropleth map (World)
- Title (states the finding, numbers from findings.json): Prospects from Brazil, Spain and France beat their promise; those from Ireland, Japan and Russia fell short
- Subtitle (what is measured, units): Shortfall vs similar prospects: how many rating points a nation's entrants peaked below (+) or above (−) players given the same potential. Nations with 15+ entrants (named in the title: 100+ and 95% CI excluding 0); others blank
- Column → role mapping: match key = ISO3 (ISO 3166-1 alpha-3); value = Shortfall vs similar prospects; tooltip = all columns
- Colours: diverging scale centred on 0: negative (beat) #2E86AB, positive (fell short) #D1495B, 0 white; no data #C5CAD3 at 40%
- Tooltip (HTML): <b>{{ Nation }}</b> ({{ Players }} players)<br>Shortfall vs similar prospects: {{ Shortfall vs similar prospects }} points<br>95% CI {{ CI low }} to {{ CI high }}<br>{{ Verdict }}<br>Reached potential: {{ Share reached potential (%) }}%
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: Caveat for the text: nationality overlaps with where players play (many British and Irish entrants were in English League One/Two, where all prospects fell short), so say 'prospects from', not 'EA is biased against'. England, Scotland, Wales and Northern Ireland are pooled as 'United Kingdom' (GBR) because the world map has one shape for the UK (DECISIONS.md). Use 5 classes, symmetric around 0 (e.g. −3, −1, 1, 3). Only nations whose 95% CI excludes 0 are distinguishable: mention that in the notes and show the Verdict in the tooltip. Kosovo (XKX) has fewer than 15 entrants, so it's not in the file.
<!-- END CHART 08 -->

<!-- BEGIN CHART 09 -->
## Chart 09: age_at_entry
- File: outputs/charts/09_age_at_entry.csv
- Tool / template: Flourish column chart, two stacked panels (no second axis)
- Title (states the finding, numbers from findings.json): 17-year-olds were promised 15.1 points of growth, nearly twice a 21-year-old's, and fell 3.5 points further short
- Subtitle (what is measured, units): Columns: shortfall vs similar prospects by age at entry (rating points; + = fell short of players given the same potential). Line: share who made it in real life, 12% at 17 vs 11% at 21: the extra promise wasn't earned
- Column → role mapping: Panel 1: x = Age at entry, columns = Shortfall vs similar prospects, error bars = CI low / CI high. Panel 2 (small, below, same x): columns = Made it in real life (%). Never put the two measures on one plot with two y-axes
- Colours: columns positive #D1495B, negative #2E86AB; made-it line #1B998B; headroom shown in the tooltip
- Tooltip (HTML): <b>Age {{ Age at entry }}</b> ({{ Players }} players)<br>Headroom given: {{ Headroom given (potential − overall) }} points<br>Shortfall vs similar prospects: {{ Shortfall vs similar prospects }} (95% CI {{ CI low }} to {{ CI high }})<br>Made it in real life: {{ Made it in real life (%) }}%
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: Build panel 2 as a second Flourish column chart (or a Flourish 'small multiples' grid) placed directly under panel 1. Flourish 'Column chart' with error bars (Data > Error bars: CI low / CI high). If error bars are awkward, use a Datawrapper range plot instead and say so. The age-16 bar is based on only 72 players (wide CI). The difference between ages ≤17 and 21 is 3.52 points (95% CI 3.03–4.08).
<!-- END CHART 09 -->

<!-- BEGIN CHART 10 -->
## Chart 10: club_badge
- File: outputs/charts/10_club_badge.csv
- Tool / template: Flourish scatter
- Title (states the finding, numbers from findings.json): A big badge bought almost no extra promise (1.1 potential points from a weak to an elite club), and big-club prospects lived up to it
- Subtitle (what is measured, units): One dot per club with 5+ entrants rated by ClubElo at entry. x = mean club Elo when the player entered the game; y = shortfall vs similar prospects (+ = fell short)
- Column → role mapping: x = Mean club Elo at entry; y = Shortfall vs similar prospects; size = Players; label = Club (top clubs only); tooltip adds Extra potential and League
- Colours: dots #C5CAD3, clubs with |shortfall| ≥ 3 in #D1495B (positive) or #2E86AB (negative); y = 0 reference line in #1D2433
- Tooltip (HTML): <b>{{ Club }}</b> ({{ League }}, {{ Country }})<br>{{ Players }} entrants · mean Elo {{ Mean club Elo at entry }}<br>Shortfall vs similar prospects: {{ Shortfall vs similar prospects }}<br>Extra potential vs same rating and age: {{ Extra potential vs same rating and age }}
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Club Football Match Data (2000–2025), Kaggle, by adamgbor; Elo data from ClubElo](https://www.kaggle.com/datasets/adamgbor/club-football-match-data-2000-2025); [ClubElo](http://clubelo.com)
- Notes for the builder: Weak vs elite club = 10th vs 90th percentile entry Elo (1313 vs 1705). Badge premium: 0.29 potential points per +100 Elo for the same overall and age (95% CI 0.24–0.35). Club-level Spearman(Elo, shortfall) = -0.33. Known gaps (no Elo): Swiss, Irish, Ukrainian and Czech clubs, English League One/Two and reserve sides (DECISIONS.md). Source line credits the ClubElo mirror and ClubElo.
<!-- END CHART 10 -->

<!-- BEGIN CHART 11 -->
## Chart 11: position_gap
- File: outputs/charts/11_position_gap.csv
- Tool / template: Flourish bar chart (horizontal, with error bars)
- Title (states the finding, numbers from findings.json): Goalkeepers fell furthest short of their promise; defensive midfielders beat theirs
- Subtitle (what is measured, units): Shortfall vs similar prospects by primary position at entry (rating points; + = peaked below players given the same potential). Positions with 30+ entrants
- Column → role mapping: y = Primary position (sorted); x = Shortfall vs similar prospects; error bars = CI low / CI high; colour = sign
- Colours: positive #D1495B, negative #2E86AB; positions whose CI crosses 0 in #C5CAD3
- Tooltip (HTML): <b>{{ Primary position }}</b> ({{ Players }} players)<br>Shortfall vs similar prospects: {{ Shortfall vs similar prospects }} (95% CI {{ CI low }} to {{ CI high }})<br>Mean potential {{ Mean potential at entry }} → mean peak {{ Mean peak later rating }}
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: Positions clearly short of their promise: GK, ST; clearly beating it: CB, LB, RB, LW, CDM. If Flourish error bars are awkward, use a Datawrapper dot plot with a range and swap tools with chart 12.
<!-- END CHART 11 -->

<!-- BEGIN CHART 12 -->
## Chart 12: who_predicted_best
- File: outputs/charts/12_who_predicted_best.csv
- Tool / template: Datawrapper range plot (AUC with 95% CI)
- Title (states the finding, numbers from findings.json): The game's potential predicted who would make it as well as the transfer market did
- Subtitle (what is measured, units): AUC 0.71 for EA potential vs 0.72 for market value at entry. AUC: the chance a predictor ranks a player who made it (3,000+ Big-5 minutes) above one who didn't; 0.5 = coin flip, 1 = perfect. 4,674 matched entrants with a market value at entry
- Column → role mapping: rows = Predictor; range start = CI low; range end = CI high; dot = AUC: who made it; tooltip adds 'Correlation with peak later rating' and 'What it is'
- Colours: EA potential #F2A900; market value #1B998B; the two benchmarks #C5CAD3
- Tooltip (HTML): <b>{{ Predictor }}</b><br>AUC: {{ AUC: who made it }} (95% CI {{ CI low }}–{{ CI high }})<br>Correlation with the game's own later rating: {{ Correlation with peak later rating }}<br>{{ What it is }}
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: x axis 0.5–0.8. Potential vs market: difference -0.002 (95% CI -0.02 to 0.016), not distinguishable. Potential still adds information beyond market value (AUC 0.617 within value quintiles). The game's own current rating predicts its future rating better than potential does (0.57 vs 0.5): put that in the text or the notes.
<!-- END CHART 12 -->

<!-- BEGIN CHART 13 -->
## Chart 13: game_vs_market
- File: outputs/charts/13_game_vs_market.csv
- Tool / template: Flourish line chart with player filter
- Title (states the finding, numbers from findings.json): Two verdicts on the same careers: the game's rating and the market's price
- Subtitle (what is measured, units): Each player's game rating and market value as a % of his own peak, 2014–2026. Featured five plus the ten most valuable other entrants
- Column → role mapping: x = Date; lines = 'Game rating (% of own peak)' and 'Market value (% of own peak)'; filter = Player (default: first featured player)
- Colours: game rating #F2A900; market value #1B998B
- Tooltip (HTML): <b>{{ Player }}</b> · {{ Date }}<br>{{ series }}: {{ value }}% of his peak
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: Rows have a value in one series or the other (game ratings at edition dates, valuations at Transfermarkt dates): turn ON 'Connect gaps' / interpolation. y axis 0–100%. Set the filter to a dropdown; Featured players first.
<!-- END CHART 13 -->

<!-- BEGIN CHART 14 -->
## Chart 14: where_they_ended_up
- File: outputs/charts/14_where_they_ended_up.csv
- Tool / template: Flourish Sankey
- Title (states the finding, numbers from findings.json): Of 2,488 prospects rated potential 75+, 17% play in the Big-5 today
- Subtitle (what is measured, units): Potential band at entry → status in the game → latest club (Transfermarkt, 2025/26 season)
- Column → role mapping: Source = Source; Target = Target; Value = Value; Step column optional (Flourish infers steps from the node names)
- Colours: bands #F2A900 shades; statuses Reached #1B998B, Fell short #D1495B, Vanished #C5CAD3; tiers: Big-5 #2E86AB, others in greys
- Tooltip (HTML): <b>{{ source }} → {{ target }}</b><br>{{ value }} players
- Source line: [EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)](https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset); [Transfermarkt Football Data (Kaggle, davidcariboo)](https://www.kaggle.com/datasets/davidcariboo/player-scores)
- Notes for the builder: Latest-club tier rule is provisional (src/outcomes.py, DECISIONS.md): moves Transfermarkt never recorded (e.g. to Qatar) count as 'Other or lower league'. 'Not in Transfermarkt' = never matched (mostly never reached a covered league).
<!-- END CHART 14 -->
