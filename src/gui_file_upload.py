import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from chart_plotter import plot_chart
import os

class FileUploadScreen(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Upload Excel or CSV File")
        self.geometry("800x600")
        self.resizable(False, False)

        self.df = None
        self.table_entries = []

        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Upload and Review Your Data", font=("Segoe UI", 12)).pack(pady=10)

        browse_btn = tk.Button(self, text="Browse File", command=self._load_file)
        browse_btn.pack(pady=5)

        self.canvas = tk.Canvas(self)
        self.table_frame = ttk.Frame(self.canvas)
        self.scroll_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        self.table_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.scroll_y.pack(side="right", fill="y")

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Generate Plot", command=self._generate_plot).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Back", command=self.destroy).pack(side="left", padx=5)

    def _load_file(self):
        filetypes = [("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        filepath = filedialog.askopenfilename(filetypes=filetypes)

        if not filepath:
            return

        try:
            if filepath.endswith(".xlsx"):
                df = pd.read_excel(filepath)
            else:
                df = pd.read_csv(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{e}")
            return

        # Standardize column names
        df.columns = [c.strip() for c in df.columns]
        try:
            df = df.rename(columns={
                "Boring Name": "Sample",
                "LL (Liquid Limit)": "LL",
                "PL (Plastic Limit)": "PL"
            })
        except:
            pass

        required = {"Sample", "LL", "PL"}
        if not required.issubset(set(df.columns)):
            messagebox.showerror("Invalid File", f"Missing required columns: {required}")
            return

        self.df = df
        self._display_table()

    def _display_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.table_entries.clear()

        headers = ["Sample", "LL", "PL"]
        for i, col in enumerate(headers):
            ttk.Label(self.table_frame, text=col, font=("Segoe UI", 10, "bold")).grid(row=0, column=i, padx=10, pady=5)

        for r_idx, row in self.df.iterrows():
            row_widgets = []
            for c_idx, col in enumerate(headers):
                val = row[col]
                e = ttk.Entry(self.table_frame, width=20)
                e.insert(0, str(val))
                e.grid(row=r_idx + 1, column=c_idx, padx=10, pady=2)
                row_widgets.append(e)
            self.table_entries.append(row_widgets)

    def _generate_plot(self):
        data = []
        for row in self.table_entries:
            values = [e.get().strip() for e in row]
            if any(values):
                try:
                    sample, ll, pl = values[0], float(values[1]), float(values[2])
                    data.append({"Sample": sample, "LL": ll, "PL": pl})
                except ValueError:
                    messagebox.showerror("Invalid Data", "LL and PL must be numeric.")
                    return

        if not data:
            messagebox.showwarning("No Data", "No data found to plot.")
            return

        df = pd.DataFrame(data)
        df["PI"] = df["LL"] - df["PL"]

        plot_chart(df)


def launch_file_upload(master):
    FileUploadScreen(master)
