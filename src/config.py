"""Project-wide paths, definitions and style constants.

Every notebook reads paths from here. All paths are built relative to the
repo root (the parent of this file's folder), so nothing is machine-specific.
"""
from pathlib import Path

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data"
RAW = DATA / "raw"
RAW_FIFA = RAW / "fifa"
RAW_TM = RAW / "transfermarkt"
RAW_CLUBELO = RAW / "clubelo"
RAW_RANKING = RAW / "fifa_ranking"
MANUAL = DATA / "manual"
CLEAN = DATA / "clean"

NOTEBOOKS = ROOT / "notebooks"
OUTPUTS = ROOT / "outputs"
CHARTS = OUTPUTS / "charts"
FINDINGS = OUTPUTS / "findings.json"
CHART_SPECS = CHARTS / "chart_specs.md"

REPORTS = ROOT / "reports"
DATA_QUALITY = REPORTS / "data_quality.md"
MATCH_REVIEW = REPORTS / "match_review.csv"
DECISIONS = ROOT / "DECISIONS.md"

ALL_DIRS = [RAW_FIFA, RAW_TM, RAW_CLUBELO, RAW_RANKING, MANUAL, CLEAN,
            NOTEBOOKS, CHARTS, REPORTS]

# Raw files
FIFA_PLAYERS = RAW_FIFA / "male_players.csv"
FIFA_TEAMS = RAW_FIFA / "male_teams.csv"   # used only for each club's league country

# FIFA's `league_name` holds each club's FC 24 league for every edition (e.g. Luton Town shows as
# "Premier League" in FIFA 15, when they were in League Two). `league_id` and `league_level` are correct
# per edition, so the edition's league name comes from the FC 24 name of that league_id. These ids don't
# exist in FC 24 and were identified by hand from their clubs and level:
LEAGUE_ID_MANUAL = {
    51: "Scottish Championship",        # Rangers, FIFA 15, level 2
    62: "National League",              # Wrexham, FIFA 22–23, level 5
    67: "Russian Premier League",
    76: "Rest of World",                # FIFA 20 catch-all league (clubs from several countries)
    341: "Liga MX",
    347: "South African Premier Division",
    349: "J1 League",
    2025: "Campeonato Brasileiro Série B",  # FIFA 17, level 2
}
RANKING_FILE = RAW_RANKING / "fifa_mens_rank.csv"
TM_REQUIRED_TABLES = ["players", "player_valuations", "appearances", "clubs", "competitions"]

# Manual override files
TM_MATCH_OVERRIDES = MANUAL / "tm_match_overrides.csv"
CLUB_NAME_OVERRIDES = MANUAL / "club_name_overrides.csv"
NATION_NAME_OVERRIDES = MANUAL / "nation_name_overrides.csv"

# Download commands (shown if a source is missing)
KAGGLE_COMMANDS = {
    "fifa": "kaggle datasets download -d stefanoleone992/ea-sports-fc-24-complete-player-dataset "
            "-p data/raw/fifa --unzip",
    "transfermarkt": "kaggle datasets download -d davidcariboo/player-scores "
                     "-p data/raw/transfermarkt --unzip",
    "fifa_ranking": "kaggle datasets download -d lucasyukioimafuko/fifa-mens-world-ranking "
                    "-p data/raw/fifa_ranking --unzip",
    "club_elo_mirror": "kaggle datasets download -d adamgbor/club-football-match-data-2000-2025 "
                       "-p data/raw/club_elo_mirror --unzip",
}
RAW_CLUBELO_MIRROR = RAW / "club_elo_mirror"

# Source credits for chart spec source lines (CLAUDE.md §9.3). Export notebooks build each
# chart's source line from these keys.
SOURCES = {
    "fifa": ("EA Sports FC 24 Complete Player Dataset (Kaggle, stefanoleone992)",
             "https://www.kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset"),
    "transfermarkt": ("Transfermarkt Football Data (Kaggle, davidcariboo)",
                      "https://www.kaggle.com/datasets/davidcariboo/player-scores"),
    "clubelo": ("ClubElo", "http://clubelo.com"),
    "clubelo_mirror": ("Club Football Match Data (2000–2025), Kaggle, by adamgbor; Elo data from ClubElo",
                       "https://www.kaggle.com/datasets/adamgbor/club-football-match-data-2000-2025"),
    "fifa_ranking": ("FIFA Men's World Ranking (Kaggle, lucasyukioimafuko)",
                     "https://www.kaggle.com/datasets/lucasyukioimafuko/fifa-mens-world-ranking"),
}
# Chart 10 credits both the mirror and ClubElo, as the mirror's author asks.
CHART_SOURCES = {10: ["fifa", "clubelo_mirror", "clubelo"]}

# ---------------------------------------------------------------- editions
EDITIONS = list(range(15, 25))
EDITION_LABELS = {v: (f"FC {v}" if v == 24 else f"FIFA {v}") for v in EDITIONS}

# Expected launch-snapshot dates (CLAUDE.md section 7). Used as a regression
# check only; the working dates are always read from `update_as_of`.
EXPECTED_EDITION_DATES = {
    15: "2014-09-18", 16: "2015-09-21", 17: "2016-09-20", 18: "2017-09-18",
    19: "2018-08-21", 20: "2019-09-19", 21: "2020-09-23", 22: "2021-09-23",
    23: "2022-09-26", 24: "2023-09-22",
}

# Regression values for male_players.csv (CLAUDE.md section 7). Checks only.
EXPECTED_SHAPE = (180_021, 109)
EXPECTED_UNIQUE_PLAYERS = 53_111
EXPECTED_ROWS_PER_EDITION = {15: 16_182, 16: 16_706, 17: 17_596, 18: 17_954, 19: 18_086,
                             20: 18_483, 21: 18_892, 22: 19_239, 23: 18_533, 24: 18_350}
EXPECTED_U21_POT85_PER_EDITION = {15: 48, 16: 82, 17: 106, 18: 137, 19: 144,
                                  20: 170, 21: 145, 22: 120, 23: 127, 24: 108}
EXPECTED_FIFA15_U21 = 4_594
# band -> (n, reached, vanished, mean(peak later - potential) to 2 dp)
EXPECTED_FIFA15_BANDS = {
    "<70": (2_634, 1_032, 774, 0.81),
    "70–74": (1_064, 301, 132, -2.63),
    "75–79": (602, 153, 22, -4.08),
    "80–84": (246, 70, 0, -3.97),
    "85+": (48, 7, 1, -4.15),
}

# ---------------------------------------------------------------- definitions (CLAUDE.md section 6)
COHORT_EDITIONS = [15, 16, 17, 18]          # cohort entry window
LEARNING_EDITIONS = [15, 16, 17, 18, 19, 20]  # chart 7 entry window
MAX_ENTRY_AGE = 21
WONDERKID_POTENTIAL = 85
PEAK_WITHIN_N = 4

# Potential bands: label -> inclusive [low, high]
POTENTIAL_BANDS = {
    "<70": (0, 69),
    "70–74": (70, 74),
    "75–79": (75, 79),
    "80–84": (80, 84),
    "85+": (85, 99),
}
BAND_ORDER = list(POTENTIAL_BANDS)

POSITION_GROUPS = {
    "GK": ["GK"],
    "DEF": ["CB", "LB", "RB", "LWB", "RWB"],
    "MID": ["CDM", "CM", "CAM", "LM", "RM"],
    "FWD": ["LW", "RW", "CF", "ST"],
}
POSITION_TO_GROUP = {pos: grp for grp, poss in POSITION_GROUPS.items() for pos in poss}

FACE_STATS = ["pace", "shooting", "passing", "dribbling", "defending", "physic"]

STATUS_REACHED = "Reached"
STATUS_FELL_SHORT = "Fell short"
STATUS_VANISHED = "Vanished"

# Real-world outcomes
BIG5_COMPETITIONS = ["GB1", "ES1", "L1", "IT1", "FR1"]
MADE_IT_MINUTES_DEFAULT = 3000
MADE_IT_MINUTES_SENSITIVITY = [1500, 3000, 5000]
FOLLOWUP_YEARS = 5            # equal-window "made it": Big-5 minutes within 5 years of entry
PEAK_VALUE_STAR_EUR = 10_000_000   # alternative success measure: peak market value >= €10m

# Robustness
BOOTSTRAP_REPS = 1000
RANDOM_SEED = 6600

# Thresholds used by later notebooks
MATCH_ACCEPT = 85
MATCH_REVIEW_LOW = 70
MATCH_TARGET_RATE_80PLUS = 0.90
CLUB_MIN_COHORT_PLAYERS = 3
CHART_MIN_NATION_N = 15
CHART_MIN_CLUB_N = 5
CHART_MAX_ROWS = 3000

# ---------------------------------------------------------------- style (CLAUDE.md section 11)
PALETTE = {
    "promise": "#F2A900",      # the game's promise (potential); featured players
    "reality": "#1B998B",      # actual outcome
    "fell_short": "#D1495B",   # fell short / overrated
    "beat": "#2E86AB",         # beat potential / underrated
    "text": "#1D2433",
    "context": "#C5CAD3",      # background context data
}
