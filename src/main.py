import tkinter as tk
from tkinter import ttk
from gui_manual_entry import launch_manual_entry
from gui_file_upload import launch_file_upload

def show_splash(root):
    splash = tk.Toplevel()
    splash.title("Loading...")
    splash.geometry("300x100")
    splash.resizable(False, False)

    ttk.Label(splash, text="Launching Atterberg Chart Tool...", font=("Helvetica", 12)).pack(pady=20)

    # Center the splash screen
    splash.update_idletasks()
    w = splash.winfo_screenwidth()
    h = splash.winfo_screenheight()
    size = tuple(int(_) for _ in splash.geometry().split('+')[0].split('x'))
    x = w//2 - size[0]//2
    y = h//2 - size[1]//2
    splash.geometry("+{}+{}".format(x, y))

    # After short delay, destroy splash and show main window
    root.after(1500, splash.destroy)

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window during splash
    show_splash(root)

    root.title("Atterberg Limit Chart Tool")
    root.geometry("500x300")
    root.resizable(False, False)
    root.deiconify()  # Show the main window

    # --- Title ---
    title_label = ttk.Label(
        root, text="Atterberg Limit Chart Generator", font=("Helvetica", 16, "bold")
    )
    title_label.pack(pady=30)

    # --- Instructions ---
    instruction = ttk.Label(
        root, text="Select an option to input your soil data:", font=("Helvetica", 12)
    )
    instruction.pack(pady=10)

    # --- Buttons ---
    manual_btn = ttk.Button(
        root, text="Enter Data Manually", width=25, command=lambda: launch_manual_entry(root)
    )
    manual_btn.pack(pady=10)

    upload_btn = ttk.Button(
        root, text="Upload Excel/CSV File", width=25, command=lambda: launch_file_upload(root)
    )
    upload_btn.pack(pady=10)

    # --- Run the GUI ---
    root.mainloop()

if __name__ == '__main__':
    main()
