import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

# --- Custom Dataset ---
data = {
    'Sample': ['B-1', 'B-2', 'B-3', 'B-4', 'B-5', 'C-1', 'C-2', 'C-3',
               'UST-1', 'P-1', 'P-2', 'P-3', 'P-4', 'P-5', 'S-1'],
    'LL':     [47, 47, 53, 59, 55, 50, 50, 49, 51, 47, 43, 50, 48, 48, 52],
    'PL':     [25, 26, 20, 21, 23, 20, 21, 19, 19, 19, 21, 25, 21, 26, 24]
}
df = pd.DataFrame(data)
df['PI'] = df['LL'] - df['PL']

# --- Define A-line and U-line Equations ---
def a_line(ll): return 0.73 * (ll - 20)
def u_line(ll): return 0.9 * (ll - 8)

# Compute points for A-line and U-line
ll_vals = np.linspace(15, 100, 1000)
A_ll = ll_vals[a_line(ll_vals) >= 4]
A_pi = a_line(A_ll)

U_ll = ll_vals[u_line(ll_vals) >= 7]
U_pi = u_line(U_ll)

# Find where A-line crosses PI = 4 and 7.3
ll_range = np.linspace(10, 60, 1000)
pi4_end_ll = ll_range[np.argmin(np.abs(a_line(ll_range) - 4))]
pi7_end_ll = ll_range[np.argmin(np.abs(a_line(ll_range) - 7.3))]

# --- Plot Setup ---
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, 100)
ax.set_ylim(0, 60)
ax.set_xlabel("Liquid Limit (LL)", fontsize=12)
ax.set_ylabel("Plasticity Index (PI)", fontsize=12)
ax.set_title("Atterberg Limits Chart", fontsize=14)

# Plot A-line and U-line
ax.plot(A_ll, A_pi, color='darkorange', linestyle='-', linewidth=1.5, label="A-Line")
ax.plot(U_ll, U_pi, color='green', linestyle='-', linewidth=1.5, label="U-Line")
ax.axvline(x=50, color='black', linestyle='-', linewidth=1.2)

# Horizontal lines at PI = 4 and PI = 7.3
ax.hlines(y=4, xmin=0, xmax=pi4_end_ll, colors='black', linewidth=1)
ax.hlines(y=7.3, xmin=0, xmax=pi7_end_ll, colors='black', linewidth=1)

# CL-ML Zone Label
center_ll = (0 + pi4_end_ll) / 2
center_pi = (4 + 7) / 2
ax.text(center_ll, center_pi, "CL-ML", fontsize=9, color='black',
        ha='center', va='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.2'))

# Soil Classification Zone Labels
ax.text(45, 55, "CL", fontsize=12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle'))
ax.text(55, 55, "CH", fontsize=12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle'))
ax.text(45, 5,  "ML", fontsize=12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle'))
ax.text(55, 5,  "MH", fontsize=12, bbox=dict(facecolor='white', edgecolor='black', boxstyle='circle'))

# Plot sample points with distinct colors
colors = plt.cm.tab20(np.linspace(0, 1, len(df)))
for i, row in df.iterrows():
    ax.scatter(row['LL'], row['PI'], color=colors[i], edgecolors='black', s=60, zorder=5)

# Custom Legend
legend_elements = [
    Line2D([0], [0], color='darkorange', lw=2, label='A-Line'),
    Line2D([0], [0], color='green', lw=2, label='U-Line'),
    Line2D([0], [0], color='black', lw=2, label='PI = 4 and 7.3')
]
for i, row in df.iterrows():
    legend_elements.append(Line2D([0], [0], marker='o', color='w', label=row['Sample'],
                                  markerfacecolor=colors[i], markeredgecolor='black', markersize=8))

ax.legend(handles=legend_elements, loc='upper left', fontsize=9, title='Legend', frameon=True)

# Grid and layout
ax.grid(True, linestyle='--', linewidth=0.5)
plt.tight_layout()

# Optional: Save to file
# plt.savefig("atterberg_limits_chart.png", dpi=300)

# Show plot
plt.show()
