from __future__ import annotations

from matplotlib import colormaps, patheffects as path_effects
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
import numpy as np
import pandas as pd

from .constants import CHART_X_LIMIT, CHART_Y_LIMIT
from .domain import a_line, u_line


PLOT_BACKGROUND = "#f5efe6"
AXIS_BACKGROUND = "#fffaf3"
GRID_COLOR = "#ccbba8"
ACCENT_ORANGE = "#c66f2c"
ACCENT_GREEN = "#457b4e"
REFERENCE_BROWN = "#7a6251"
CLAY_FILL = "#e8d2b4"
SILT_FILL = "#d8e7ef"
GUIDE_COLOR = "#3b3027"
CLML_FILL = "#f6f0e4"
MARKERS = ("o", "s", "^", "D", "P", "X", "v", "<", ">", "h", "*", "p", "8")


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

    pi4_end = 20 + (4 / 0.73)
    pi73_end = 20 + (7.3 / 0.73)
    _draw_cl_ml_zone(axis, pi4_end, pi73_end)

    axis.plot(a_line_x, a_line_y, color=ACCENT_ORANGE, linewidth=2.0, label="A-Line")
    axis.plot(u_line_x, u_line_y, color=ACCENT_GREEN, linewidth=2.0, label="U-Line")
    axis.plot([0, CHART_Y_LIMIT[1]], [0, CHART_Y_LIMIT[1]], color=REFERENCE_BROWN, linewidth=1.0, linestyle=(0, (4, 2, 1.2, 2)))
    axis.axvline(x=50, color=GUIDE_COLOR, linewidth=1.2)
    axis.axvline(x=40, color=GUIDE_COLOR, linewidth=1.0, linestyle=(0, (1.5, 2.5)), alpha=0.85)
    axis.hlines(y=4, xmin=4, xmax=pi4_end, colors=GUIDE_COLOR, linewidth=1)
    axis.hlines(y=7.3, xmin=7.3, xmax=pi73_end, colors=GUIDE_COLOR, linewidth=1)

    trend_text = axis.text(
        40.8,
        39,
        "Trending to fat clay",
        rotation=90,
        fontsize=8,
        color="#5d5044",
        va="center",
        ha="left",
    )
    _outline_text(trend_text)

    _add_zone_labels(axis)

    legend_items = [
        Line2D([0], [0], color=ACCENT_ORANGE, lw=2, label="A-Line"),
        Line2D([0], [0], color=ACCENT_GREEN, lw=2, label="U-Line"),
        Line2D([0], [0], color=REFERENCE_BROWN, lw=1.0, linestyle=(0, (4, 2, 1.2, 2)), label="LL = PI"),
        Line2D([0], [0], color=GUIDE_COLOR, lw=1.0, linestyle=(0, (1.5, 2.5)), label="LL = 40"),
    ]

    if dataframe.empty:
        message = axis.text(
            63,
            30,
            "Paste from Excel or import a file to preview borehole points.",
            ha="center",
            va="center",
            fontsize=10.5,
            color="#5c5147",
            bbox=dict(facecolor="#fffdf8", edgecolor="#b8aa9b", boxstyle="round,pad=0.45"),
        )
        _outline_text(message)
    else:
        colors = _sample_colors(len(dataframe.index))
        markers = _sample_markers(len(dataframe.index))
        for color, marker, (_, row) in zip(colors, markers, dataframe.iterrows()):
            axis.scatter(
                row["LL"],
                row["PI"],
                color=color,
                marker=marker,
                edgecolors="#221c17",
                linewidths=0.8,
                s=72,
                zorder=5,
            )
            legend_items.append(
                Line2D(
                    [0],
                    [0],
                    marker=marker,
                    color="w",
                    label=row["Sample"],
                    markerfacecolor=color,
                    markeredgecolor="#221c17",
                    markersize=7.5,
                    linestyle="None",
                )
            )

    legend_columns = 2 if len(legend_items) > 14 else 1
    legend = axis.legend(
        handles=legend_items,
        title="Legend",
        loc="upper left",
        bbox_to_anchor=(0.015, 0.99),
        frameon=True,
        borderaxespad=0.0,
        fontsize=7.0,
        title_fontsize=8,
        handlelength=1.8,
        labelspacing=0.32,
        borderpad=0.5,
        ncol=legend_columns,
    )
    legend.get_frame().set_facecolor("#fffdf8")
    legend.get_frame().set_edgecolor("#cabcae")
    legend.get_frame().set_alpha(0.94)

    figure.subplots_adjust(left=0.09, right=0.98, bottom=0.12, top=0.9)


def _style_axis(axis) -> None:
    axis.set_facecolor(AXIS_BACKGROUND)
    axis.set_xlim(*CHART_X_LIMIT)
    axis.set_ylim(*CHART_Y_LIMIT)
    axis.set_xticks(np.arange(CHART_X_LIMIT[0], CHART_X_LIMIT[1] + 10, 10))
    axis.set_yticks(np.arange(CHART_Y_LIMIT[0], CHART_Y_LIMIT[1] + 10, 10))
    axis.set_xlabel("Liquid Limit (LL)", fontsize=11, color="#1f1a16")
    axis.set_ylabel("Plasticity Index (PI)", fontsize=11, color="#1f1a16")
    axis.set_title("Atterberg Limits Chart", fontsize=14, weight="bold", color="#1f1a16", pad=14)
    axis.grid(True, linestyle="--", linewidth=0.7, color=GRID_COLOR, alpha=0.8)
    for spine in axis.spines.values():
        spine.set_color("#5f5144")
    axis.tick_params(colors="#3f352e")


def _draw_cl_ml_zone(axis, pi4_end: float, pi73_end: float) -> None:
    polygon = Polygon(
        [(4, 4), (pi4_end, 4), (pi73_end, 7.3), (7.3, 7.3)],
        closed=True,
        facecolor=CLML_FILL,
        edgecolor="#88796b",
        hatch="////",
        linewidth=0.8,
        alpha=0.65,
        zorder=1.6,
    )
    axis.add_patch(polygon)

    label = axis.text(17.5, 5.55, "CL-ML", fontsize=8.2, color="#52463c", ha="center", va="center")
    _outline_text(label)


def _add_zone_labels(axis) -> None:
    zone_labels = [
        ("CL or OL", 25, 11.5),
        ("CL or OL", 35, 22.5),
        ("ML or OL", 38.5, 5.55),
        ("CL or OL", 45, 37.5),
        ("CH or OH", 55, 50),
        ("CH or OH", 85, 50),
        ("MH or OH", 75, 16.5),
    ]

    for text, x_value, y_value in zone_labels:
        artist = axis.text(
            x_value,
            y_value,
            text,
            fontsize=7.9,
            weight="semibold",
            color="#5c5045",
            ha="center",
            va="center",
        )
        _outline_text(artist)


def _outline_text(text_artist) -> None:
    text_artist.set_path_effects([
        path_effects.Stroke(linewidth=2.4, foreground=AXIS_BACKGROUND),
        path_effects.Normal(),
    ])


def _sample_colors(count: int):
    color_map = np.linspace(0, 1, max(count, 1))
    return list(colormaps["tab20"](color_map))


def _sample_markers(count: int):
    return [MARKERS[index % len(MARKERS)] for index in range(count)]
