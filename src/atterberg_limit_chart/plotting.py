from __future__ import annotations

from matplotlib import colormaps, patheffects as path_effects
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
import numpy as np
import pandas as pd

from .constants import CHART_X_LIMIT, CHART_Y_LIMIT
from .domain import a_line, u_line


PLOT_BACKGROUND = "#ffffff"
AXIS_BACKGROUND = "#ffffff"
GRID_COLOR = "#dddddd"
ACCENT_ORANGE = "#c66f2c"
ACCENT_GREEN = "#457b4e"
REFERENCE_BLUE = "#2b6cb0"
GUIDE_COLOR = "#3b3027"
CLML_FILL = "#f4f4f4"
MARKERS = ("o", "s", "^", "D", "P", "X", "v", "<", ">", "h", "*", "p", "8")


A_LINE_LEGEND = "A-Line: PI = 0.73(LL - 20)"
U_LINE_LEGEND = "U-Line: PI = 0.90(LL - 8)"
LL_PI_LEGEND = "LL = PI Line: PI = LL"
LL_40_LEGEND = "Vertical Guide: LL = 40"


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

    pi4_end = 20 + (4 / 0.73)
    pi73_end = 20 + (7.3 / 0.73)
    _draw_cl_ml_zone(axis, pi4_end, pi73_end)

    axis.plot(a_line_x, a_line_y, color=ACCENT_ORANGE, linewidth=2.0)
    axis.plot(u_line_x, u_line_y, color=ACCENT_GREEN, linewidth=2.0, linestyle=(0, (1.3, 2.0)))
    axis.plot([0, CHART_Y_LIMIT[1]], [0, CHART_Y_LIMIT[1]], color=REFERENCE_BLUE, linewidth=1.3)
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

    line_legend_items = [
        Line2D([0], [0], color=ACCENT_ORANGE, lw=2, label=A_LINE_LEGEND),
        Line2D([0], [0], color=ACCENT_GREEN, lw=2, linestyle=(0, (1.3, 2.0)), label=U_LINE_LEGEND),
        Line2D([0], [0], color=REFERENCE_BLUE, lw=1.3, label=LL_PI_LEGEND),
        Line2D([0], [0], color=GUIDE_COLOR, lw=1.0, linestyle=(0, (1.5, 2.5)), label=LL_40_LEGEND),
    ]

    borehole_legend_items = []
    if dataframe.empty:
        message = axis.text(
            63,
            30,
            "Paste from Excel or import a file to preview borehole points.",
            ha="center",
            va="center",
            fontsize=10.5,
            color="#5c5147",
            bbox=dict(facecolor="#ffffff", edgecolor="#cccccc", boxstyle="round,pad=0.45"),
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
            borehole_legend_items.append(
                Line2D(
                    [0],
                    [0],
                    marker=marker,
                    color="w",
                    label=row["Sample"],
                    markerfacecolor=color,
                    markeredgecolor="#221c17",
                    markersize=5.6,
                    linestyle="None",
                )
            )

    line_legend = axis.legend(
        handles=line_legend_items,
        title="Reference Lines",
        loc="upper left",
        bbox_to_anchor=(0.015, 0.99),
        frameon=True,
        borderaxespad=0.0,
        fontsize=6.8,
        title_fontsize=8,
        handlelength=2.2,
        labelspacing=0.32,
        borderpad=0.5,
    )
    line_legend.get_frame().set_facecolor("#ffffff")
    line_legend.get_frame().set_edgecolor("#cfcfcf")
    line_legend.get_frame().set_alpha(0.96)
    axis.add_artist(line_legend)

    if borehole_legend_items:
        borehole_columns = 2 if len(borehole_legend_items) > 12 else 1
        borehole_legend = axis.legend(
            handles=borehole_legend_items,
            title="Boreholes",
            loc="upper left",
            bbox_to_anchor=(0.015, 0.74),
            frameon=True,
            borderaxespad=0.0,
            fontsize=5.2,
            title_fontsize=6.6,
            handlelength=1.0,
            handletextpad=0.4,
            labelspacing=0.24,
            borderpad=0.45,
            ncol=borehole_columns,
        )
        borehole_legend.get_frame().set_facecolor("#ffffff")
        borehole_legend.get_frame().set_edgecolor("#cfcfcf")
        borehole_legend.get_frame().set_alpha(0.96)

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
    axis.grid(True, linestyle="--", linewidth=0.7, color=GRID_COLOR, alpha=0.85)
    for spine in axis.spines.values():
        spine.set_color("#555555")
    axis.tick_params(colors="#3f352e")


def _draw_cl_ml_zone(axis, pi4_end: float, pi73_end: float) -> None:
    polygon = Polygon(
        [(4, 4), (pi4_end, 4), (pi73_end, 7.3), (7.3, 7.3)],
        closed=True,
        facecolor=CLML_FILL,
        edgecolor="#8f8f8f",
        hatch="////",
        linewidth=0.8,
        alpha=0.85,
        zorder=1.6,
    )
    axis.add_patch(polygon)

    label = axis.text(17.5, 5.55, "CL-ML", fontsize=8.2, color="#4f4f4f", ha="center", va="center")
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
