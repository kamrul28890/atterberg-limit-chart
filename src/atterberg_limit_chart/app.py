from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from .constants import (
    APP_TITLE,
    DATA_FILE_TYPES,
    DEFAULT_SAMPLE_FILE,
    EDITABLE_COLUMNS,
    EXAMPLE_ROWS,
    MIN_WINDOW_SIZE,
    OUTPUT_COLUMNS,
    PLOT_FILE_TYPES,
    TABLE_COLUMNS,
    WINDOW_SIZE,
)
from .data import (
    DataValidationError,
    blank_row,
    evaluate_rows,
    load_rows_from_file,
    parse_clipboard_rows,
    save_dataframe,
)
from .domain import DatasetSummary
from .plotting import create_atterberg_figure, draw_atterberg_chart


class AtterbergApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(*MIN_WINDOW_SIZE)
        self.configure(bg="#efe5d8")

        self.style = ttk.Style(self)
        self._configure_styles()

        self.raw_rows: list[dict[str, str]] = [blank_row()]
        self.current_dataframe = evaluate_rows(self.raw_rows).dataframe
        self._item_row_map: dict[str, int] = {}
        self._active_editor: ttk.Entry | None = None

        self.status_var = tk.StringVar(value="Paste data from Excel or import an .xlsx/.csv file to begin.")
        self.summary_vars = {
            "rows": tk.StringVar(value="0"),
            "valid": tk.StringVar(value="0"),
            "avg_ll": tk.StringVar(value="0.0"),
            "avg_pi": tk.StringVar(value="0.0"),
            "high_ll": tk.StringVar(value="0"),
        }

        self.figure = create_atterberg_figure(self.current_dataframe)

        self._build_layout()
        self.bind_all("<Control-v>", self._handle_clipboard_shortcut, add="+")
        self.bind_all("<Delete>", self._handle_delete_shortcut, add="+")
        self._refresh_view()

    def _configure_styles(self) -> None:
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#efe5d8")
        self.style.configure("Panel.TFrame", background="#f7f1e7")
        self.style.configure("Header.TFrame", background="#47392d")
        self.style.configure("HeaderTitle.TLabel", background="#47392d", foreground="#fff8ef", font=("Segoe UI", 20, "bold"))
        self.style.configure("HeaderBody.TLabel", background="#47392d", foreground="#e8dccd", font=("Segoe UI", 10))
        self.style.configure("Toolbar.TFrame", background="#e9ddce")
        self.style.configure("Card.TFrame", background="#fffaf3", relief="solid", borderwidth=1)
        self.style.configure("CardValue.TLabel", background="#fffaf3", foreground="#2d241d", font=("Segoe UI", 18, "bold"))
        self.style.configure("CardLabel.TLabel", background="#fffaf3", foreground="#6a5a4a", font=("Segoe UI", 9))
        self.style.configure("Section.TLabelframe", background="#f7f1e7", foreground="#2d241d")
        self.style.configure("Section.TLabelframe.Label", background="#f7f1e7", foreground="#2d241d", font=("Segoe UI", 10, "bold"))
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(10, 6))
        self.style.configure("TButton", font=("Segoe UI", 9), padding=(10, 6))
        self.style.configure("Treeview", rowheight=28, font=("Segoe UI", 9), background="#fffdf9", fieldbackground="#fffdf9")
        self.style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        self.style.map("Treeview", background=[("selected", "#d9cab7")], foreground=[("selected", "#1d1813")])

    def _build_layout(self) -> None:
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill="x")

        ttk.Label(header, text="Atterberg Limit Workbench", style="HeaderTitle.TLabel").pack(anchor="w", padx=24, pady=(18, 2))
        ttk.Label(
            header,
            text="Prepare borehole data, paste directly from Excel, review rows, and generate a chart-ready plasticity plot in one place.",
            style="HeaderBody.TLabel",
        ).pack(anchor="w", padx=24, pady=(0, 18))

        toolbar = ttk.Frame(self, style="Toolbar.TFrame")
        toolbar.pack(fill="x", padx=14, pady=(12, 0))

        buttons = [
            ("Import Excel / CSV", self._import_file, "Accent.TButton"),
            ("Paste from Clipboard", self._paste_from_clipboard, "Accent.TButton"),
            ("Load Example", self._load_example_rows, "TButton"),
            ("Add Row", self._add_blank_row, "TButton"),
            ("Delete Selected", self._delete_selected_rows, "TButton"),
            ("Clear All", self._clear_rows, "TButton"),
            ("Export Cleaned Data", self._export_cleaned_data, "TButton"),
            ("Save Chart PNG", self._save_chart_png, "TButton"),
        ]
        for text, command, style in buttons:
            ttk.Button(toolbar, text=text, command=command, style=style).pack(side="left", padx=(0, 8), pady=10)

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=14, pady=14)

        left_panel = ttk.Frame(body, style="Panel.TFrame", padding=14)
        right_panel = ttk.Frame(body, style="Panel.TFrame", padding=14)
        body.add(left_panel, weight=7)
        body.add(right_panel, weight=6)

        self._build_table_panel(left_panel)
        self._build_plot_panel(right_panel)

        status_frame = ttk.Frame(self, style="Toolbar.TFrame")
        status_frame.pack(fill="x", side="bottom")
        ttk.Label(status_frame, textvariable=self.status_var, background="#e9ddce", foreground="#3a2f26", font=("Segoe UI", 9)).pack(
            anchor="w",
            padx=18,
            pady=8,
        )

    def _build_table_panel(self, parent: ttk.Frame) -> None:
        hint_frame = ttk.LabelFrame(parent, text="Data Intake", style="Section.TLabelframe", padding=10)
        hint_frame.pack(fill="x")
        ttk.Label(
            hint_frame,
            text="Accepted headers: Sample / Boring Name, LL / Liquid Limit, PL / Plastic Limit. You can also paste three plain columns directly from Excel.",
            background="#f7f1e7",
            foreground="#5d4f43",
            wraplength=560,
            justify="left",
        ).pack(anchor="w")

        table_frame = ttk.LabelFrame(parent, text="Borehole Table", style="Section.TLabelframe", padding=10)
        table_frame.pack(fill="both", expand=True, pady=(12, 12))

        self.tree = ttk.Treeview(table_frame, columns=TABLE_COLUMNS, show="headings", selectmode="extended")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<Double-1>", self._begin_edit)

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        y_scroll.pack(side="right", fill="y")
        x_scroll = ttk.Scrollbar(parent, orient="horizontal", command=self.tree.xview)
        x_scroll.pack(fill="x")

        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        column_widths = {
            "Sample": 160,
            "LL": 80,
            "PL": 80,
            "PI": 80,
            "Zone": 90,
            "Status": 220,
        }
        for column in TABLE_COLUMNS:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=column_widths[column], anchor="center")
        self.tree.column("Sample", anchor="w")
        self.tree.column("Status", anchor="w")

        self.tree.tag_configure("valid", background="#fffdf9", foreground="#1d1813")
        self.tree.tag_configure("invalid", background="#fff1f1", foreground="#8c1d40")
        self.tree.tag_configure("blank", background="#f3ede4", foreground="#8a7c6d")

        issues_frame = ttk.LabelFrame(parent, text="Validation Notes", style="Section.TLabelframe", padding=10)
        issues_frame.pack(fill="both")

        self.issue_box = tk.Text(
            issues_frame,
            height=8,
            wrap="word",
            borderwidth=0,
            relief="flat",
            background="#fffaf3",
            foreground="#4a4037",
            font=("Consolas", 10),
        )
        self.issue_box.pack(fill="both", expand=True)
        self.issue_box.configure(state="disabled")

    def _build_plot_panel(self, parent: ttk.Frame) -> None:
        summary_frame = ttk.Frame(parent, style="Panel.TFrame")
        summary_frame.pack(fill="x")

        cards = [
            ("Rows Entered", self.summary_vars["rows"]),
            ("Valid Points", self.summary_vars["valid"]),
            ("Average LL", self.summary_vars["avg_ll"]),
            ("Average PI", self.summary_vars["avg_pi"]),
            ("LL >= 50", self.summary_vars["high_ll"]),
        ]

        for index, (label, variable) in enumerate(cards):
            card = ttk.Frame(summary_frame, style="Card.TFrame", padding=12)
            card.pack(side="left", fill="both", expand=True, padx=(0, 8 if index < len(cards) - 1 else 0))
            ttk.Label(card, textvariable=variable, style="CardValue.TLabel").pack(anchor="w")
            ttk.Label(card, text=label, style="CardLabel.TLabel").pack(anchor="w")

        plot_frame = ttk.LabelFrame(parent, text="Chart Preview", style="Section.TLabelframe", padding=10)
        plot_frame.pack(fill="both", expand=True, pady=(12, 0))

        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(fill="x")

    def _handle_clipboard_shortcut(self, event: tk.Event | None = None) -> str | None:
        focused = self.focus_get()
        if isinstance(focused, (tk.Entry, ttk.Entry)):
            return None
        self._paste_from_clipboard()
        return "break"

    def _handle_delete_shortcut(self, event: tk.Event | None = None) -> str | None:
        focused = self.focus_get()
        if focused is self.tree:
            self._delete_selected_rows()
            return "break"
        return None

    def _import_file(self) -> None:
        filepath = filedialog.askopenfilename(
            title="Select borehole data file",
            filetypes=DATA_FILE_TYPES,
            initialdir=str(DEFAULT_SAMPLE_FILE.parent if DEFAULT_SAMPLE_FILE.exists() else Path.cwd()),
        )
        if not filepath:
            return

        try:
            rows = load_rows_from_file(filepath)
        except Exception as error:
            messagebox.showerror("Import Failed", str(error))
            return

        self.raw_rows = rows or [blank_row()]
        self.status_var.set(f"Loaded {len(rows)} row(s) from {Path(filepath).name}.")
        self._refresh_view()

    def _paste_from_clipboard(self) -> None:
        try:
            clipboard_text = self.clipboard_get()
            rows = parse_clipboard_rows(clipboard_text)
        except tk.TclError:
            messagebox.showerror("Clipboard Error", "The clipboard does not contain text data.")
            return
        except DataValidationError as error:
            messagebox.showerror("Clipboard Error", str(error))
            return

        existing_non_blank = any(any(value.strip() for value in row.values()) for row in self.raw_rows)
        if existing_non_blank:
            self.raw_rows = [row for row in self.raw_rows if any(value.strip() for value in row.values())] + rows
            self.status_var.set(f"Appended {len(rows)} row(s) from the clipboard.")
        else:
            self.raw_rows = rows or [blank_row()]
            self.status_var.set(f"Pasted {len(rows)} row(s) from the clipboard.")
        self._refresh_view()

    def _load_example_rows(self) -> None:
        self.raw_rows = [row.copy() for row in EXAMPLE_ROWS]
        self.status_var.set("Loaded the built-in example dataset.")
        self._refresh_view()

    def _add_blank_row(self) -> None:
        self.raw_rows.append(blank_row())
        self.status_var.set("Added a new blank row.")
        self._refresh_view()

    def _delete_selected_rows(self) -> None:
        selected_items = list(self.tree.selection())
        if not selected_items:
            messagebox.showinfo("Delete Rows", "Select one or more rows in the table first.")
            return

        indices = sorted((self._item_row_map[item_id] for item_id in selected_items), reverse=True)
        for index in indices:
            self.raw_rows.pop(index)

        if not self.raw_rows:
            self.raw_rows = [blank_row()]

        self.status_var.set(f"Deleted {len(indices)} row(s).")
        self._refresh_view()

    def _clear_rows(self) -> None:
        if not any(any(value.strip() for value in row.values()) for row in self.raw_rows):
            return

        if not messagebox.askyesno("Clear Data", "Remove every row from the workspace?"):
            return

        self.raw_rows = [blank_row()]
        self.status_var.set("Cleared the workspace.")
        self._refresh_view()

    def _export_cleaned_data(self) -> None:
        if self.current_dataframe.empty:
            messagebox.showwarning("No Data", "There are no valid rows to export yet.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Export cleaned dataset",
            defaultextension=".xlsx",
            filetypes=DATA_FILE_TYPES,
        )
        if not filepath:
            return

        try:
            save_dataframe(self.current_dataframe.loc[:, list(OUTPUT_COLUMNS)], filepath)
        except Exception as error:
            messagebox.showerror("Export Failed", str(error))
            return

        self.status_var.set(f"Exported {len(self.current_dataframe)} clean row(s) to {Path(filepath).name}.")

    def _save_chart_png(self) -> None:
        if self.current_dataframe.empty:
            messagebox.showwarning("No Chart Data", "Add at least one valid row before saving the chart.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Save chart as PNG",
            defaultextension=".png",
            filetypes=PLOT_FILE_TYPES,
        )
        if not filepath:
            return

        self.figure.savefig(filepath, dpi=300, facecolor=self.figure.get_facecolor(), bbox_inches="tight")
        self.status_var.set(f"Saved chart to {Path(filepath).name}.")

    def _begin_edit(self, event: tk.Event) -> None:
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        item_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        if not item_id or not column_id:
            return

        column_index = int(column_id.replace("#", "")) - 1
        column_name = TABLE_COLUMNS[column_index]
        if column_name not in EDITABLE_COLUMNS:
            return

        if self._active_editor is not None:
            self._active_editor.destroy()
            self._active_editor = None

        x, y, width, height = self.tree.bbox(item_id, column_id)
        value = self.tree.set(item_id, column_name)

        editor = ttk.Entry(self.tree)
        editor.place(x=x, y=y, width=width, height=height)
        editor.insert(0, value)
        editor.select_range(0, tk.END)
        editor.focus_set()

        editor.bind(
            "<Return>",
            lambda _event, item=item_id, column=column_name, widget=editor: self._commit_edit(item, column, widget.get()),
        )
        editor.bind("<Escape>", lambda _event, widget=editor: self._cancel_edit(widget))
        editor.bind(
            "<FocusOut>",
            lambda _event, item=item_id, column=column_name, widget=editor: self._commit_edit(item, column, widget.get()),
        )
        self._active_editor = editor

    def _cancel_edit(self, editor: ttk.Entry) -> None:
        if self._active_editor is editor:
            self._active_editor = None
        editor.destroy()

    def _commit_edit(self, item_id: str, column_name: str, value: str) -> None:
        editor = self._active_editor
        if editor is not None:
            self._active_editor = None
            editor.destroy()

        row_index = self._item_row_map.get(item_id)
        if row_index is None:
            return

        self.raw_rows[row_index][column_name] = value.strip()
        self.status_var.set(f"Updated row {row_index + 1}.")
        self._refresh_view()

    def _refresh_view(self) -> None:
        evaluation = evaluate_rows(self.raw_rows)
        self.current_dataframe = evaluation.dataframe

        self.tree.delete(*self.tree.get_children())
        self._item_row_map.clear()

        for index, preview in enumerate(evaluation.previews):
            item_id = f"row-{index}"
            if preview.is_blank:
                tag = "blank"
            elif preview.is_valid:
                tag = "valid"
            else:
                tag = "invalid"

            self.tree.insert(
                "",
                "end",
                iid=item_id,
                values=(
                    preview.sample,
                    preview.liquid_limit,
                    preview.plastic_limit,
                    preview.plasticity_index,
                    preview.zone,
                    preview.status,
                ),
                tags=(tag,),
            )
            self._item_row_map[item_id] = index

        summary = DatasetSummary.from_dataframe(self.current_dataframe)
        self.summary_vars["rows"].set(str(evaluation.total_non_blank_rows))
        self.summary_vars["valid"].set(str(evaluation.valid_row_count))
        self.summary_vars["avg_ll"].set(f"{summary.average_ll:.1f}" if summary.plotted_points else "0.0")
        self.summary_vars["avg_pi"].set(f"{summary.average_pi:.1f}" if summary.plotted_points else "0.0")
        self.summary_vars["high_ll"].set(str(summary.high_plasticity_count))

        self._update_issue_box(evaluation)
        self._update_status_text(evaluation)
        draw_atterberg_chart(self.figure, self.current_dataframe)
        self.canvas.draw_idle()

    def _update_issue_box(self, evaluation) -> None:
        if evaluation.issues:
            text = "\n".join(evaluation.issues)
        elif evaluation.total_non_blank_rows:
            text = "All non-blank rows are valid and ready to plot."
        else:
            text = "No data loaded yet. Paste a three-column table from Excel or import an .xlsx/.csv file."

        self.issue_box.configure(state="normal")
        self.issue_box.delete("1.0", tk.END)
        self.issue_box.insert("1.0", text)
        self.issue_box.configure(state="disabled")

    def _update_status_text(self, evaluation) -> None:
        if not evaluation.total_non_blank_rows:
            self.status_var.set("Paste data from Excel or import an .xlsx/.csv file to begin.")
            return

        if evaluation.issues:
            self.status_var.set(
                f"Plotted {evaluation.valid_row_count} of {evaluation.total_non_blank_rows} row(s). {len(evaluation.issues)} row(s) still need attention."
            )
            return

        self.status_var.set(f"All {evaluation.valid_row_count} row(s) are valid and chart-ready.")


def main() -> None:
    app = AtterbergApp()
    app.mainloop()


if __name__ == "__main__":
    main()
