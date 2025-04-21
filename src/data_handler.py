import pandas as pd
import os

REQUIRED_COLUMNS = {"Sample", "LL", "PL"}

def read_file(filepath):
    """
    Reads Excel or CSV file and standardizes column names.
    Returns a cleaned DataFrame.
    """
    try:
        if filepath.endswith(".xlsx"):
            df = pd.read_excel(filepath)
        else:
            df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")

    # Standardize column names
    df.columns = [col.strip() for col in df.columns]
    df = df.rename(columns={
        "Boring Name": "Sample",
        "LL (Liquid Limit)": "LL",
        "PL (Plastic Limit)": "PL"
    })

    if not REQUIRED_COLUMNS.issubset(df.columns):
        missing = REQUIRED_COLUMNS - set(df.columns)
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    df = df[list(REQUIRED_COLUMNS)]  # Only keep required columns
    df["PI"] = df["LL"] - df["PL"]

    return df

def save_dataframe(df, filepath):
    """
    Saves a DataFrame to Excel or CSV based on file extension.
    """
    try:
        if filepath.endswith(".xlsx"):
            df.to_excel(filepath, index=False)
        else:
            df.to_csv(filepath, index=False)
    except Exception as e:
        raise ValueError(f"Error saving file: {e}")
