from pathlib import Path

APP_TITLE = "Atterberg Limit Chart Tool"
WINDOW_SIZE = "1380x860"
MIN_WINDOW_SIZE = (1160, 720)

RAW_COLUMNS = ("Sample", "LL", "PL")
TABLE_COLUMNS = ("Sample", "LL", "PL", "PI", "Zone", "Status")
EDITABLE_COLUMNS = ("Sample", "LL", "PL")
OUTPUT_COLUMNS = ("Sample", "LL", "PL", "PI", "Zone")

DATA_FILE_TYPES = [
    ("Excel Workbook", "*.xlsx"),
    ("CSV File", "*.csv"),
]
PLOT_FILE_TYPES = [("PNG Image", "*.png")]

CHART_X_LIMIT = (0, 100)
CHART_Y_LIMIT = (0, 60)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SAMPLE_FILE = PROJECT_ROOT / "data" / "boring_data.xlsx"

EXAMPLE_ROWS = [
    {"Sample": "B-1", "LL": "48", "PL": "25"},
    {"Sample": "B-2", "LL": "55", "PL": "31"},
    {"Sample": "B-3", "LL": "43", "PL": "20"},
    {"Sample": "B-4", "LL": "61", "PL": "28"},
    {"Sample": "B-5", "LL": "39", "PL": "18"},
]
