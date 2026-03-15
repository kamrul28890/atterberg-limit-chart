# Atterberg Limit Chart Tool

A refactored desktop workbench for preparing borehole Atterberg limit data, pasting tables from Excel, validating rows, and generating a ready-to-export plasticity chart.

## What it does

- Pastes directly from Excel with `Ctrl+V` or the clipboard button.
- Imports `.xlsx` and `.csv` files with flexible header mapping.
- Lets you review and edit rows in one table.
- Calculates `PI = LL - PL` automatically.
- Tags each valid point by chart zone (`CL`, `CH`, `ML`, `MH`, `CL-ML`).
- Shows validation notes for bad rows instead of silently failing.
- Exports the cleaned dataset to Excel or CSV.
- Saves the chart preview as a PNG.
- Builds into a Windows executable with PyInstaller.

## Expected columns

The app accepts these common names when importing files or pasted headers:

- `Sample`, `Sample ID`, `Boring Name`, `Borehole`
- `LL`, `Liquid Limit`, `LL (Liquid Limit)`
- `PL`, `Plastic Limit`, `PL (Plastic Limit)`

If you paste plain Excel cells without headers, the app treats the first three columns as `Sample`, `LL`, and `PL`.

## Run from source

```powershell
.\.venv\Scripts\activate
$env:PYTHONPATH = 'src'
python src\main.py
```

## Run tests

```powershell
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
```

## Build the executable

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_exe.ps1
```

That produces a standalone executable at `dist\AtterbergLimitChart.exe`.

## Project layout

- `src/main.py`: desktop entrypoint.
- `src/atterberg_limit_chart/data.py`: import, paste parsing, validation, export.
- `src/atterberg_limit_chart/domain.py`: A-line, U-line, and zone logic.
- `src/atterberg_limit_chart/plotting.py`: Matplotlib chart rendering.
- `src/atterberg_limit_chart/app.py`: Tkinter workbench UI.
- `tests/test_data_pipeline.py`: parsing and validation smoke tests.
