
import tkinter as tk
from tkinter import ttk
from gui_manual_entry import launch_manual_entry
from gui_file_upload import launch_file_upload
from config import (
    SPLASH_SCREEN_DELAY_MS,
    MAIN_WINDOW_GEOMETRY,
    MAIN_WINDOW_TITLE,
    MAIN_TITLE_TEXT,
    INSTRUCTION_TEXT,
    MANUAL_ENTRY_BUTTON_TEXT,
    FILE_UPLOAD_BUTTON_TEXT,
    FONT_FAMILY,
    FONT_SIZE_SPLASH,
    FONT_SIZE_MAIN_TITLE,
    FONT_SIZE_INSTRUCTION
)

class AtterbergChartApp:
    def __init__(self, master):
        self.master = master
        self.master.withdraw()  # Hide the main window during splash
        self.show_splash()

        self.master.title(MAIN_WINDOW_TITLE)
        self.master.geometry(MAIN_WINDOW_GEOMETRY)
        self.master.resizable(False, False)
        self.master.deiconify()  # Show the main window

        self._create_widgets()

    def show_splash(self):
        splash = tk.Toplevel(self.master)
        splash.title("Loading...")
        splash.geometry("300x100")
        splash.resizable(False, False)

        ttk.Label(splash, text="Launching Atterberg Chart Tool...", font=(FONT_FAMILY, FONT_SIZE_SPLASH)).pack(pady=20)

        # Center the splash screen
        splash.update_idletasks()
        w = splash.winfo_screenwidth()
        h = splash.winfo_screenheight()
        size = tuple(int(_) for _ in splash.geometry().split("+")[0].split("x"))
        x = w // 2 - size[0] // 2
        y = h // 2 - size[1] // 2
        splash.geometry(f"+{x}+{y}")

        # After short delay, destroy splash and show main window
        self.master.after(SPLASH_SCREEN_DELAY_MS, splash.destroy)

    def _create_widgets(self):
        # --- Title ---
        title_label = ttk.Label(
            self.master, text=MAIN_TITLE_TEXT, font=(FONT_FAMILY, FONT_SIZE_MAIN_TITLE, "bold")
        )
        title_label.pack(pady=30)

        # --- Instructions ---
        instruction = ttk.Label(
            self.master, text=INSTRUCTION_TEXT, font=(FONT_FAMILY, FONT_SIZE_INSTRUCTION)
        )
        instruction.pack(pady=10)

        # --- Buttons ---
        manual_btn = ttk.Button(
            self.master, text=MANUAL_ENTRY_BUTTON_TEXT, width=25, command=lambda: launch_manual_entry(self.master)
        )
        manual_btn.pack(pady=10)

        upload_btn = ttk.Button(
            self.master, text=FILE_UPLOAD_BUTTON_TEXT, width=25, command=lambda: launch_file_upload(self.master)
        )
        upload_btn.pack(pady=10)

def main():
    root = tk.Tk()
    app = AtterbergChartApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()


