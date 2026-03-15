from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


def a_line(liquid_limit: float) -> float:
    return 0.73 * (liquid_limit - 20)


def u_line(liquid_limit: float) -> float:
    return 0.9 * (liquid_limit - 8)


def classify_soil(liquid_limit: float, plasticity_index: float) -> str:
    """Return the chart zone for a point on the Casagrande chart."""
    if liquid_limit < 30 and 4 <= plasticity_index <= 7:
        return "CL-ML"
    if plasticity_index >= a_line(liquid_limit):
        return "CL" if liquid_limit < 50 else "CH"
    return "ML" if liquid_limit < 50 else "MH"


@dataclass(frozen=True)
class DatasetSummary:
    plotted_points: int
    average_ll: float
    average_pi: float
    high_plasticity_count: int

    @classmethod
    def from_dataframe(cls, dataframe: pd.DataFrame) -> "DatasetSummary":
        if dataframe.empty:
            return cls(plotted_points=0, average_ll=0.0, average_pi=0.0, high_plasticity_count=0)

        return cls(
            plotted_points=len(dataframe.index),
            average_ll=float(dataframe["LL"].mean()),
            average_pi=float(dataframe["PI"].mean()),
            high_plasticity_count=int((dataframe["LL"] >= 50).sum()),
        )
