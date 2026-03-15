from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd

from .constants import OUTPUT_COLUMNS, RAW_COLUMNS
from .domain import classify_soil


class DataValidationError(ValueError):
    """Raised when imported data cannot be understood."""


@dataclass(frozen=True)
class RowPreview:
    sample: str
    liquid_limit: str
    plastic_limit: str
    plasticity_index: str
    zone: str
    status: str
    is_valid: bool
    is_blank: bool


@dataclass(frozen=True)
class DatasetEvaluation:
    previews: list[RowPreview]
    dataframe: pd.DataFrame
    issues: list[str]
    total_non_blank_rows: int
    valid_row_count: int


HEADER_ALIASES = {
    "sample": "Sample",
    "samplename": "Sample",
    "sampleid": "Sample",
    "id": "Sample",
    "borehole": "Sample",
    "boreholename": "Sample",
    "boreholeid": "Sample",
    "boring": "Sample",
    "boringname": "Sample",
    "hole": "Sample",
    "holeid": "Sample",
    "bh": "Sample",
    "ll": "LL",
    "liquidlimit": "LL",
    "llliquidlimit": "LL",
    "liquidlimitll": "LL",
    "pl": "PL",
    "plasticlimit": "PL",
    "plplasticlimit": "PL",
    "plasticlimitpl": "PL",
}


def blank_row() -> dict[str, str]:
    return {column: "" for column in RAW_COLUMNS}


def empty_output_dataframe() -> pd.DataFrame:
    return pd.DataFrame(columns=OUTPUT_COLUMNS)


def load_rows_from_file(filepath: str | Path) -> list[dict[str, str]]:
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".xlsx":
        dataframe = pd.read_excel(path)
    elif suffix == ".csv":
        dataframe = pd.read_csv(path)
    else:
        raise DataValidationError("Only .xlsx and .csv files are supported.")

    return dataframe_to_rows(dataframe)


def dataframe_to_rows(dataframe: pd.DataFrame) -> list[dict[str, str]]:
    if dataframe.empty and not list(dataframe.columns):
        return []

    mapping = _build_column_mapping(dataframe.columns)
    missing = [column for column in RAW_COLUMNS if column not in mapping.values()]
    if missing:
        joined = ", ".join(missing)
        raise DataValidationError(f"Missing required column(s): {joined}")

    renamed = dataframe.rename(columns=mapping)
    selected = renamed.loc[:, list(RAW_COLUMNS)]

    rows = []
    for _, series in selected.iterrows():
        row = {column: _stringify_cell(series[column]) for column in RAW_COLUMNS}
        if any(value for value in row.values()):
            rows.append(row)
    return rows


def parse_clipboard_rows(text: str) -> list[dict[str, str]]:
    if not text or not text.strip():
        raise DataValidationError("Clipboard is empty.")

    parsed_rows = _parse_tabular_text(text)
    if not parsed_rows:
        raise DataValidationError("No tabular data was found in the clipboard.")

    header = parsed_rows[0]
    if _looks_like_header(header):
        body = parsed_rows[1:]
        if not body:
            raise DataValidationError("The clipboard only contains headers.")
        width = max(len(row) for row in body + [header])
        normalized_header = [_make_unique_header_name(cell or f"Column {index + 1}", index) for index, cell in enumerate(header)]
        padded_rows = [row + [""] * (width - len(row)) for row in body]
        padded_header = normalized_header + [f"Column {index + 1}" for index in range(len(normalized_header), width)]
        dataframe = pd.DataFrame(padded_rows, columns=padded_header, dtype=str)
        return dataframe_to_rows(dataframe)

    rows = []
    for raw_row in parsed_rows:
        cells = raw_row + [""] * (len(RAW_COLUMNS) - len(raw_row))
        sample, liquid_limit, plastic_limit = cells[: len(RAW_COLUMNS)]
        rows.append({"Sample": sample, "LL": liquid_limit, "PL": plastic_limit})

    rows = [row for row in rows if any(value.strip() for value in row.values())]
    if not rows:
        raise DataValidationError("No Atterberg rows were found in the clipboard.")
    return rows


def evaluate_rows(rows: Iterable[Mapping[str, object]]) -> DatasetEvaluation:
    previews: list[RowPreview] = []
    records: list[dict[str, object]] = []
    issues: list[str] = []
    generated_name_index = 1
    total_non_blank_rows = 0

    for row_number, row in enumerate(rows, start=1):
        sample_text = _stringify_cell(row.get("Sample", ""))
        ll_text = _stringify_cell(row.get("LL", ""))
        pl_text = _stringify_cell(row.get("PL", ""))

        if not any((sample_text, ll_text, pl_text)):
            previews.append(
                RowPreview(
                    sample="",
                    liquid_limit="",
                    plastic_limit="",
                    plasticity_index="",
                    zone="",
                    status="Blank row",
                    is_valid=False,
                    is_blank=True,
                )
            )
            continue

        total_non_blank_rows += 1
        display_name = sample_text or f"Sample {generated_name_index}"
        ll_value = _parse_float(ll_text)
        pl_value = _parse_float(pl_text)

        if ll_value is None:
            issue = "Liquid Limit must be numeric."
            issues.append(f"Row {row_number}: {issue}")
            previews.append(
                RowPreview(display_name, ll_text, pl_text, "", "", issue, is_valid=False, is_blank=False)
            )
            continue

        if pl_value is None:
            issue = "Plastic Limit must be numeric."
            issues.append(f"Row {row_number}: {issue}")
            previews.append(
                RowPreview(display_name, ll_text, pl_text, "", "", issue, is_valid=False, is_blank=False)
            )
            continue

        if ll_value < 0 or pl_value < 0:
            issue = "LL and PL must be zero or greater."
            issues.append(f"Row {row_number}: {issue}")
            previews.append(
                RowPreview(display_name, ll_text, pl_text, "", "", issue, is_valid=False, is_blank=False)
            )
            continue

        if ll_value < pl_value:
            issue = "Liquid Limit must be greater than or equal to Plastic Limit."
            issues.append(f"Row {row_number}: {issue}")
            previews.append(
                RowPreview(display_name, ll_text, pl_text, "", "", issue, is_valid=False, is_blank=False)
            )
            continue

        plasticity_index = ll_value - pl_value
        zone = classify_soil(ll_value, plasticity_index)
        status = "Auto-named" if not sample_text else "Ready"

        records.append(
            {
                "Sample": display_name,
                "LL": ll_value,
                "PL": pl_value,
                "PI": plasticity_index,
                "Zone": zone,
            }
        )
        previews.append(
            RowPreview(
                sample=display_name,
                liquid_limit=_format_number(ll_value),
                plastic_limit=_format_number(pl_value),
                plasticity_index=_format_number(plasticity_index),
                zone=zone,
                status=status,
                is_valid=True,
                is_blank=False,
            )
        )
        if not sample_text:
            generated_name_index += 1

    dataframe = pd.DataFrame.from_records(records, columns=OUTPUT_COLUMNS)
    if dataframe.empty:
        dataframe = empty_output_dataframe()

    return DatasetEvaluation(
        previews=previews,
        dataframe=dataframe,
        issues=issues,
        total_non_blank_rows=total_non_blank_rows,
        valid_row_count=len(records),
    )


def save_dataframe(dataframe: pd.DataFrame, filepath: str | Path) -> None:
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".xlsx":
        dataframe.to_excel(path, index=False)
        return

    if suffix == ".csv":
        dataframe.to_csv(path, index=False)
        return

    raise DataValidationError("Export path must end with .xlsx or .csv.")


def _build_column_mapping(columns: Iterable[object]) -> dict[object, str]:
    columns = list(columns)
    mapping: dict[object, str] = {}
    matched: set[str] = set()

    for column in columns:
        normalized = _normalize_header(column)
        canonical = HEADER_ALIASES.get(normalized)
        if canonical and canonical not in matched:
            mapping[column] = canonical
            matched.add(canonical)

    remaining_targets = [target for target in RAW_COLUMNS if target not in matched]
    remaining_columns = [column for column in columns if column not in mapping]
    for target, column in zip(remaining_targets, remaining_columns):
        mapping[column] = target

    return mapping


def _normalize_header(value: object) -> str:
    text = _stringify_cell(value).casefold()
    return re.sub(r"[^a-z0-9]+", "", text)


def _stringify_cell(value: object) -> str:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _parse_tabular_text(text: str) -> list[list[str]]:
    stripped = text.strip()
    if "\t" in stripped:
        return [
            [cell.strip() for cell in line.split("\t")]
            for line in stripped.splitlines()
            if line.strip()
        ]

    reader = csv.reader(io.StringIO(stripped))
    rows = []
    for row in reader:
        if any(cell.strip() for cell in row):
            rows.append([cell.strip() for cell in row])
    return rows


def _looks_like_header(row: list[str]) -> bool:
    if not row:
        return False

    matches = sum(1 for cell in row if _normalize_header(cell) in HEADER_ALIASES)
    numeric_cells = sum(1 for cell in row[:3] if _parse_float(cell) is not None)
    return matches >= 2 and numeric_cells < 2


def _make_unique_header_name(value: str, index: int) -> str:
    text = value.strip()
    if text:
        return text
    return f"Column {index + 1}"


def _parse_float(value: str) -> float | None:
    if not value:
        return None

    sanitized = value.replace(",", "")
    try:
        return float(sanitized)
    except ValueError:
        return None


def _format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")
