# Chart plan v2: proposal for team approval

**Status:** adopted 5 Nov 2026 after the self-review (see DECISIONS.md, "Final story and chart decisions"); CLAUDE.md §9.2 updated. Changes from the draft below: chart 10 is now the badge-premium myth-bust (the elite-club effect did not survive a club-neutral outcome), charts 8–11 use shortfall vs similar prospects, chart 4 moved to Datawrapper and chart 11 to Flourish, chart 9 uses two panels instead of a second axis.
Numbers come from `outputs/findings.json` (notebook 05). They are provisional until the Transfermarkt match review and
club-override check are done.

## The revised story

> EA's potential rating ranks young talent about as well as the transfer market does, but it is **overconfident**:
> it over-promises at the top, most of all for the youngest players and for prospects at weaker clubs. And EA handed
> out more promise over time.

The structure stays at 5 acts and 14 charts, with 7 Flourish and 7 Datawrapper. Seven charts are kept, and seven are
reframed or replaced. The reason is that the original versions show no effect (charts 9, 10 and 12) or tell a weaker
version of the same point.

Title placeholders `{…}` are `findings.json` keys. The "Now" column shows today's value, for discussion only.

## Charts

| # | Act | Change | Chart | Draft title (placeholders) | Now |
|---|---|---|---|---|---|
| 1 | Promise | keep + column | FIFA 15 wonderkid table (DW table); add **Made it (real life)** | "Only {chart_01.reached} of FIFA 15's {chart_01.fifa15_wonderkids} wonderkids reached their potential, but {chart_01.made_it} became Big-5 regulars" | 7 of 48; 40 |
| 2 | Promise | **reframe** | Wonderkids per 1,000 under-21s by edition, with headroom (potential − overall) in the tooltip (DW column) | "EA handed out {robust_inflation.wk_per_1000_max}/1,000 wonderkid ratings by {robust_inflation.wk_per_1000_max_edition}, up from {robust_inflation.wk_per_1000_first}" | 10.4 → 37.2 (FIFA 20) → 23.5 |
| 3 | Promise | keep | Rating trajectories of the featured five + 85+ median (Flourish line) | (featured five once approved) | |
| 4 | Reckoning | **add line** | Promise vs reality scatter, potential ≥ 75 (Flourish scatter). Add a y = x line and the fitted calibration line; if Flourish can't draw them, move to a Datawrapper scatter and swap with chart 12's tool | "Every 10 points of potential bought only {robust_calibration.points_of_peak_per_10_points_potential} points of real rating" | 6.1 (slope 0.61, CI 0.59–0.63) |
| 5 | Reckoning | **reframe** | Game vs reality by band: "reached in game %" next to "made it in real life %" (DW range/dot plot); keep reached / fell short / vanished in the tooltip | "The higher the promise, the less often it came true in the game, and the more often in real life" | 85+: 11% vs 68%; <70: 29% vs 4% |
| 6 | Reckoning | keep | Busts (wonderkids) and bloomers (peak 80+) (DW range plot) | "{chart_06.biggest_bust.player} dropped {chart_06.biggest_bust.gap} points short of his promise" | |
| 7 | Reckoning | **reframe title** | Share reaching potential within 4 editions by entry edition, with mean gap (Flourish line) | "As wonderkid ratings multiplied, fewer reached them: {chart_07.first_reached_pct}% → {chart_07.last_reached_pct}%" | 25% → 6% |
| 8 | Misjudged | keep + CI | Nation map, mean gap (DW choropleth). Add a CI column and "above / below / not distinguishable from average" to the tooltip | "English, Scottish and Irish prospects were among the most overrated" (only if the CIs hold after review) | 20 of 56 nations distinguishable |
| 9 | Misjudged | **replace** (was nation rank vs gap, ρ = 0.04) | **Age at entry**: mean gap and made-it % for ages 16–21, with CIs (Flourish column/line) | "EA gave 17-year-olds {age headroom} points of headroom; their careers didn't justify it" | gap +3.9 (CI 3.3–4.5) vs age 21; made-it difference +1.3 pts (CI −1.3 to +4.0) |
| 10 | Misjudged | **replace** (was club Elo vs gap scatter, ρ = 0.02) | **Elite prospects (potential 80+) by club Elo quartile**: mean gap and made-it %, with CIs (Flourish column) | "Elite prospects at weaker clubs were the most overrated" | gap 8.0 vs 4.9; made it 39% vs 65%; −0.78 gap per +100 Elo (CI −1.09 to −0.47) |
| 11 | Misjudged | keep | Position gap dot plot (DW dot) | "Attackers were overrated most" | ST/RW/CF about +4.5 vs full-backs and CDM about +2.5 |
| 12 | Mattered | **replace** (was attribute correlations, all ≤ 0.11) | **Who predicted careers best?** AUC for "made it" with CIs: potential, overall + age benchmark, market value at entry (DW bar/range). A second panel or tooltip shows Spearman with peak later rating | "EA's potential predicted careers about as well as the transfer market, and its own current rating predicted future ratings better" | AUC 0.71 vs 0.72 (market) vs 0.70 (benchmark); Spearman 0.50 (potential) vs 0.57 (overall) |
| 13 | Mattered | keep | Game rating vs market value over time, featured five + 10 more (Flourish line) | | |
| 14 | Where now | keep | Sankey: band → status → latest club tier (Flourish). The tier rule is provisional (`src/outcomes.py`) | | |

Tools: Flourish 3, 4, 7, 9, 10, 13, 14; Datawrapper 1, 2, 5, 6, 8, 11, 12 (still 7 each).

## What the robustness tests say, and what they don't

- **Holds up:** calibration slope < 1; promise inflation 2015–2020 (mean under-21 potential +5.2, mean overall only +1.7,
  top-300 scale drift +2.3); age effect on gap; elite-club effect (holds with potential and age held constant); overall
  beats potential at predicting later ratings.
- **Weaker than first stated:** in a quick check on 4 Nov I wrote that a one-line "overall + youth" formula beat potential.
  Fitted properly and tested out-of-sample, the benchmark is slightly *worse* than potential at predicting real careers
  (AUC 0.700 vs 0.713; difference +0.013, CI +0.001 to +0.024). Potential is level with market value (−0.002, CI −0.020 to
  +0.016), and it carries information the market lacks (AUC within market-value quintiles 0.62, CI 0.59–0.64). So the fair
  framing is "as good as the market, not better than the scouts' consensus", not "a formula beats EA".
- **No effect:** national-team rank (ρ = 0.04), club Elo across the whole cohort (ρ = 0.02), attributes (|ρ| ≤ 0.11).
  These are worth a sentence in the text ("the badge and the flag didn't fool EA overall"), not a chart.
- **Age and real careers:** younger entrants did *not* make it more often (difference not distinguishable from 0), so their
  extra headroom wasn't earned.
- **"Vanished" is mostly real exits:** only 0.1% of vanished players' leagues left the game; 8.8% kept playing in a covered
  top flight, and 0.1% made it. Keep vanished as its own category (§6), but the text can say most vanished players left
  top-level football.
- **Follow-up time:** FIFA 15 entrants made it more often than later cohorts even within an equal 5-year window
  (9.7% vs 5–6%). So the difference isn't only follow-up time; part of it is composition (FIFA 15 entrants are the whole
  under-21 stock, later cohorts mostly young newcomers).
- **Every success measure** (Big-5 minutes, within 5 years, any covered top flight, peak value ≥ €10m) rises with the
  potential band (AUC 0.75–0.81).

## Decisions needed from the team

1. Approve the revised story and the seven chart changes (2, 4, 5, 7, 9, 10, 12).
2. Approve the featured five (candidates in notebook 05 §5).
3. Devarshi: finish the match review and club-override check, then re-run 02 → 05 so the numbers stop being provisional.
