from __future__ import annotations

from matplotlib import cm
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

from .constants import CHART_X_LIMIT, CHART_Y_LIMIT
from .domain import a_line, u_line


PLOT_BACKGROUND = "#f5efe6"
AXIS_BACKGROUND = "#fffaf3"
GRID_COLOR = "#ccbba8"
ACCENT_ORANGE = "#c66f2c"
ACCENT_GREEN = "#457b4e"
CLAY_FILL = "#e8d2b4"
SILT_FILL = "#d8e7ef"
GUIDE_COLOR = "#3b3027"


def create_atterberg_figure(dataframe: pd.DataFrame) -> Figure:
    figure = Figure(figsize=(8.4, 6.3), dpi=110, facecolor=PLOT_BACKGROUND)
    draw_atterberg_chart(figure, dataframe)
    return figure


def draw_atterberg_chart(figure: Figure, dataframe: pd.DataFrame) -> None:
    figure.clear()
    figure.set_facecolor(PLOT_BACKGROUND)

    axis = figure.add_subplot(111)
    _style_axis(axis)

    ll_values = np.linspace(15, CHART_X_LIMIT[1], 1000)
    a_line_x = ll_values[a_line(ll_values) >= 4]
    a_line_y = a_line(a_line_x)
    u_line_x = ll_values[u_line(ll_values) >= 7.3]
    u_line_y = u_line(u_line_x)

    low_ll = np.linspace(20, 50, 500)
    high_ll = np.linspace(50, CHART_X_LIMIT[1], 500)
    axis.fill_between(low_ll, a_line(low_ll), CHART_Y_LIMIT[1], color=CLAY_FILL, alpha=0.45)
    axis.fill_between(high_ll, a_line(high_ll), CHART_Y_LIMIT[1], color=CLAY_FILL, alpha=0.25)
    axis.fill_between(low_ll, 0, np.clip(a_line(low_ll), 0, CHART_Y_LIMIT[1]), color=SILT_FILL, alpha=0.65)
    axis.fill_between(high_ll, 0, np.clip(a_line(high_ll), 0, CHART_Y_LIMIT[1]), color=SILT_FILL, alpha=0.4)

    axis.plot(a_line_x, a_line_y, color=ACCENT_ORANGE, linewidth=2.0, label="A-Line")
    axis.plot(u_line_x, u_line_y, color=ACCENT_GREEN, linewidth=2.0, label="U-Line")
    axis.axvline(x=50, color=GUIDE_COLOR, linewidth=1.2)

    pi4_end = 20 + (4 / 0.73)
    pi73_end = 20 + (7.3 / 0.73)
    axis.hlines(y=4, xmin=0, xmax=pi4_end, colors=GUIDE_COLOR, linewidth=1)
    axis.hlines(y=7.3, xmin=0, xmax=pi73_end, colors=GUIDE_COLOR, linewidth=1)

    label_box = dict(facecolor="#fffdf8", edgecolor="#7f6e5e", boxstyle="round,pad=0.25")
    axis.text(40, 44, "CL", fontsize=11, weight="bold", bbox=label_box)
    axis.text(67, 44, "CH", fontsize=11, weight="bold", bbox=label_box)
    axis.text(35, 8, "ML", fontsize=11, weight="bold", bbox=label_box)
    axis.text(67, 8, "MH", fontsize=11, weight="bold", bbox=label_box)
    axis.text(15, 5.5, "CL-ML", fontsize=9, bbox=label_box)

    legend_items = [
        Line2D([0], [0], color=ACCENT_ORANGE, lw=2, label="A-Line"),
        Line2D([0], [0], color=ACCENT_GREEN, lw=2, label="U-Line"),
    ]

    if dataframe.empty:
        axis.text(
            50,
            30,
            "Paste from Excel or import a file to preview borehole points.",
            ha="center",
            va="center",
            fontsize=11,
            color="#5c5147",
            bbox=dict(facecolor="#fffdf8", edgecolor="#b8aa9b", boxstyle="round,pad=0.45"),
        )
    else:
        colors = _sample_colors(len(dataframe.index))
        for color, (_, row) in zip(colors, dataframe.iterrows()):
            axis.scatter(
                row["LL"],
                row["PI"],
                color=color,
                edgecolors="#221c17",
                linewidths=0.8,
                s=70,
                zorder=5,
            )
            legend_items.append(
                Line2D(
                    [0],
                    [0],
                    marker="o",
                    color="w",
                    label=row["Sample"],
                    markerfacecolor=color,
                    markeredgecolor="#221c17",
                    markersize=8,
                )
            )

        legend = axis.legend(
            handles=legend_items,
            title="Legend",
            loc="upper left",
            bbox_to_anchor=(1.02, 1.0),
            frameon=True,
            borderaxespad=0.0,
            fontsize=8,
            title_fontsize=9,
        )
        legend.get_frame().set_facecolor("#fffdf8")
        legend.get_frame().set_edgecolor("#cabcae")

    figure.subplots_adjust(left=0.1, right=0.78, bottom=0.12, top=0.9)


def _style_axis(axis) -> None:
    axis.set_facecolor(AXIS_BACKGROUND)
    axis.set_xlim(*CHART_X_LIMIT)
    axis.set_ylim(*CHART_Y_LIMIT)
    axis.set_xlabel("Liquid Limit (LL)", fontsize=11, color="#1f1a16")
    axis.set_ylabel("Plasticity Index (PI)", fontsize=11, color="#1f1a16")
    axis.set_title("Atterberg Limits Chart", fontsize=14, weight="bold", color="#1f1a16", pad=14)
    axis.grid(True, linestyle="--", linewidth=0.7, color=GRID_COLOR, alpha=0.8)
    for spine in axis.spines.values():
        spine.set_color("#5f5144")
    axis.tick_params(colors="#3f352e")


def _sample_colors(count: int):
    color_map = np.linspace(0, 1, max(count, 1))
    return list(cm.get_cmap("tab20")(color_map))
