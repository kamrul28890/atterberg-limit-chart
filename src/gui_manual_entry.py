import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from chart_plotter import plot_chart

MAX_ROWS = 20

class ManualEntryScreen(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Manual Data Entry")
        self.geometry("700x600")
        self.resizable(False, False)

        self.entries = []
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Enter Sample Data (max 20 rows)", font=("Segoe UI", 12)).pack(pady=10)

        self.canvas = tk.Canvas(self)
        self.frame = ttk.Frame(self.canvas)
        self.scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        headers = ["Sample", "LL", "PL"]
        for col, text in enumerate(headers):
            ttk.Label(self.frame, text=text, font=("Segoe UI", 10, "bold")).grid(row=0, column=col, padx=10, pady=5)

        for i in range(5):  # Start with 5 rows
            self._add_row()

        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.scroll_y.pack(side="right", fill="y")

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Row", command=self._add_row).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove Row", command=self._remove_row).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Generate Plot", command=self._generate_plot).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Back", command=self.destroy).pack(side="left", padx=5)

        # Bind Ctrl+V for pasting from clipboard
        self.bind_all("<Control-v>", self._paste_from_clipboard)

    def _add_row(self):
        if len(self.entries) >= MAX_ROWS:
            messagebox.showwarning("Limit Reached", f"Maximum {MAX_ROWS} rows allowed.")
            return
        row = len(self.entries) + 1
        row_entries = []
        for col in range(3):
            e = ttk.Entry(self.frame, width=20)
            e.grid(row=row, column=col, padx=10, pady=3)
            row_entries.append(e)
        self.entries.append(row_entries)

    def _remove_row(self):
        if not self.entries:
            return
        row_widgets = self.entries.pop()
        for widget in row_widgets:
            widget.destroy()

    def _paste_from_clipboard(self, event=None):
        try:
            clipboard = self.clipboard_get()
            rows = clipboard.strip().split('\n')
            for r_idx, row in enumerate(rows):
                if r_idx >= len(self.entries):
                    self._add_row()
                values = row.split('\t')
                for c_idx, value in enumerate(values):
                    if c_idx < 3:  # Only fill Sample, LL, PL
                        self.entries[r_idx][c_idx].delete(0, tk.END)
                        self.entries[r_idx][c_idx].insert(0, value.strip())
        except Exception as e:
            messagebox.showerror("Paste Error", f"Failed to paste data:\n{str(e)}")

    def _generate_plot(self):
        data = []
        for row in self.entries:
            values = [entry.get().strip() for entry in row]
            if any(values):  # Skip blank lines
                try:
                    sample, ll, pl = values[0], float(values[1]), float(values[2])
                    data.append({"Sample": sample, "LL": ll, "PL": pl})
                except ValueError:
                    messagebox.showerror("Invalid Input", "LL and PL must be numbers.")
                    return

        if not data:
            messagebox.showwarning("No Data", "Please enter at least one valid row.")
            return

        df = pd.DataFrame(data)
        df["PI"] = df["LL"] - df["PL"]

        plot_chart(df)

def launch_manual_entry(master):
    ManualEntryScreen(master)
