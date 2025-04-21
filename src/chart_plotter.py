import matplotlib.pyplot as plt
import numpy as np
from tkinter import filedialog, messagebox
from matplotlib.lines import Line2D

def a_line(ll): return 0.73 * (ll - 20)
def u_line(ll): return 0.9 * (ll - 8)

def plot_chart(df):
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        # A-line
        ll_vals = np.linspace(15, 100, 1000)
        A_ll = ll_vals[a_line(ll_vals) >= 4]
        A_pi = a_line(A_ll)
        ax.plot(A_ll, A_pi, color='darkorange', linestyle='-', linewidth=1.5, label="A-Line")

        # U-line
        U_ll = ll_vals[u_line(ll_vals) >= 7]
        U_pi = u_line(U_ll)
        ax.plot(U_ll, U_pi, color='green', linestyle='-', linewidth=1.5, label="U-Line")

        # Reference lines
        ax.axvline(x=50, color='black', linestyle='-', linewidth=1.2)
        ll_range = np.linspace(10, 60, 1000)
        pi4_end_ll = ll_range[np.argmin(np.abs(a_line(ll_range) - 4))]
        pi7_end_ll = ll_range[np.argmin(np.abs(a_line(ll_range) - 7.3))]
        ax.hlines(y=4, xmin=0, xmax=pi4_end_ll, colors='black', linewidth=1)
        ax.hlines(y=7.3, xmin=0, xmax=pi7_end_ll, colors='black', linewidth=1)

        # Zone labels
        ax.text(45, 55, "CL", fontsize=12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle'))
        ax.text(55, 55, "CH", fontsize=12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle'))
        ax.text(45, 5,  "ML", fontsize=12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle'))
        ax.text(55, 5,  "MH", fontsize=12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle'))
        ax.text(pi4_end_ll / 2, 5.5, "CL-ML", fontsize=9, color='black',
                ha='center', va='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'))

        # Plot points
        cmap = plt.cm.tab20.colors
        colors = [cmap[i % len(cmap)] for i in range(len(df))]
        for i, row in df.iterrows():
            ax.scatter(row['LL'], row['PI'], color=colors[i], edgecolors='black', s=60, zorder=5)
            ax.text(row['LL'] + 0.5, row['PI'] + 0.5, row['Sample'], fontsize=8)

        # Custom legend
        legend_elements = [
            Line2D([0], [0], color='darkorange', lw=2, label='A-Line'),
            Line2D([0], [0], color='green', lw=2, label='U-Line'),
            Line2D([0], [0], color='black', lw=2, label='PI = 4 & 7.3')
        ]
        for i, row in df.iterrows():
            legend_elements.append(Line2D([0], [0], marker='o', color='w',
                                          label=row['Sample'],
                                          markerfacecolor=colors[i],
                                          markeredgecolor='black', markersize=8))

        ax.legend(handles=legend_elements, loc='upper left', fontsize=8, title='Legend')

        # Axes styling
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 60)
        ax.set_xlabel("Liquid Limit (LL)", fontsize=12)
        ax.set_ylabel("Plasticity Index (PI)", fontsize=12)
        ax.set_title("Atterberg Limits Chart", fontsize=14)
        ax.grid(True, linestyle='--', linewidth=0.5)

        plt.tight_layout()
        plt.show()

        # Save prompt
        save_prompt = messagebox.askyesno("Save Plot", "Do you want to save this chart as PNG?")
        if save_prompt:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png")],
                                                     title="Save Chart As")
            if file_path:
                fig.savefig(file_path, dpi=300)
                messagebox.showinfo("Saved", f"Chart saved to:\n{file_path}")

    except Exception as e:
        messagebox.showerror("Plot Error", f"Something went wrong while plotting:\n{str(e)}")
