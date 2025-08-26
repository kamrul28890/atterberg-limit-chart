# Configuration Constants for Atterberg Limit Chart Tool

# GUI Settings
SPLASH_SCREEN_DELAY_MS = 1500
MAIN_WINDOW_GEOMETRY = "500x300"
MAIN_WINDOW_TITLE = "Atterberg Limit Chart Tool"
MAIN_TITLE_TEXT = "Atterberg Limit Chart Generator"
INSTRUCTION_TEXT = "Select an option to input your soil data:"
MANUAL_ENTRY_BUTTON_TEXT = "Enter Data Manually"
FILE_UPLOAD_BUTTON_TEXT = "Upload Excel/CSV File"

# Font Settings
FONT_FAMILY = "Helvetica"
FONT_SIZE_SPLASH = 12
FONT_SIZE_MAIN_TITLE = 16
FONT_SIZE_INSTRUCTION = 12

# Data Handling Settings
REQUIRED_COLUMNS = {"Sample", "LL", "PL"}
COLUMN_RENAMES = {
    "Boring Name": "Sample",
    "LL (Liquid Limit)": "LL",
    "PL (Plastic Limit)": "PL"
}

# Plotting Settings (Placeholder for now, can be expanded)
PLOT_TITLE = "Atterberg Limit Chart"
PLASTICITY_INDEX_LABEL = "Plasticity Index (PI)"
LIQUID_LIMIT_LABEL = "Liquid Limit (LL)"

# Colors (if needed for plotting or GUI elements)
COLOR_A_LINE = "red"
COLOR_U_LINE = "blue"
COLOR_DATA_POINTS = "black"


