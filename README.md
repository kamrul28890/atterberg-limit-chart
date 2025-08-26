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

*   `src/main.py`: Main application entry point, handles the splash screen and main menu.
*   `src/config.py`: Contains all configuration constants for the application, including GUI settings, font styles, and data handling parameters.
*   `src/data_handler.py`: Manages reading and saving soil data from/to files.
*   `src/chart_plotter.py`: Handles the logic for plotting the Atterberg Limit Chart.
*   `src/gui_manual_entry.py`: Handles the GUI for manual data input.
*   `src/gui_file_upload.py`: Handles the GUI for file upload.
*   `requirements.txt`: Lists all Python dependencies.

## 🚀 How to Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kamrul28890/atterberg-limit-chart.git
    cd atterberg-limit-chart
    ```
2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```
3.  **Run the application:**
    ```bash
    python src/main.py
    ```

## 🔧 Refactoring Highlights

*   **Centralized Configuration:** All configurable parameters are now in `src/config.py`, making it easier to modify and maintain.
*   **Object-Oriented GUI:** The main application logic in `src/main.py` has been refactored into a class-based structure, improving modularity and readability.
*   **Improved Data Handling:** `src/data_handler.py` now utilizes constants from `config.py` for column renaming and validation.

## 🔮 Future Enhancements

*   Implement the plotting logic in `chart_plotter.py`.
*   Add more robust error handling and user feedback.
*   Improve the visual design of the GUI.
*   Implement unit tests for core functionalities.


