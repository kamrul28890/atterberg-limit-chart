# 🧪 Atterberg Limit Chart Generator

A full-featured Python desktop application to plot Atterberg Limits using soil sample data. Built with Tkinter and Matplotlib.  

## 💡 Features

- Enter data manually or upload `.xlsx` / `.csv` files
- Calculates Plasticity Index (PI)
- Plots A-Line, U-Line, PI threshold zones
- Auto-labels soil classification zones (CL, CH, ML, MH, CL-ML)
- Custom color for up to 20 soil samples
- Export charts as high-resolution PNG
- Standalone `.exe` version available

## 📂 Directory Structure
atterberg-limit-chart/
│
├── src/                            # Source Python files
│   ├── main.py                     # App launcher (entry point)
│   ├── chart_plotter.py            # Plotting logic (A-line, U-line, PI zones)
│   ├── gui_manual_entry.py         # Manual data input screen (max 20 samples)
│   ├── gui_file_upload.py          # Upload and preview .xlsx/.csv
│   ├── data_handler.py             # File read/write, validation
│   └── __init__.py                 # (Optional) treat as package
│
├── data/                           # Sample or user input data
│   └── boring_data.xlsx            # Example Excel data file
│
├── dist/                           # Final executable output
│   └── AtterbergPlotTool.exe       # One-file Windows app built via PyInstaller
│
├── build/                          # Auto-generated PyInstaller build (can delete after packaging)
│
├── .gitignore                      # Ignore cache, build files, logs
├── LICENSE                         # MIT License or your choice
├── README.md                       # Full project description, setup, usage
├── requirements.txt                # Python dependencies
└── AtterbergPlotTool.spec          # PyInstaller build config (auto-generated)

