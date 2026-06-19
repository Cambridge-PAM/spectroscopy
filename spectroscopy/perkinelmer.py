"""PerkinElmer absorbance and reflectance helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from scipy import interpolate


def _to_float(value: Any) -> float:
    return float(pd.to_numeric([value], errors="coerce")[0])


def load_perkinelmer_results(
    sample_folder: str | Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    sample_folder = Path(sample_folder)
    sample_names = pd.read_csv(
        sample_folder / "Results Table.csv", index_col=0, usecols=[0]
    )

    for sample in sample_names.index:
        sample_names.loc[sample, "File"] = str(
            sample_folder / f"{sample}.Sample.Raw.csv"
        )

    data = pd.DataFrame()
    y_column_labels: list[str] = []
    last_index = None
    for sample in sample_names.index:
        sample_file = str(sample_names.loc[sample, "File"])
        temp = pd.read_csv(sample_file, index_col=0)
        y_column_labels.extend([str(col) for col in temp.columns])
        data[sample] = np.concatenate(temp.values).ravel()
        last_index = temp.index

    if last_index is not None:
        data.index = last_index
    data = data.apply(pd.to_numeric, errors="coerce")
    if y_column_labels:
        data.attrs["y_column_labels"] = sorted(set(y_column_labels))
        data.attrs["y_column_label"] = y_column_labels[0]
    return sample_names, data


def _extract_reference_xy(reference: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    numeric = reference.apply(pd.to_numeric, errors="coerce")
    valid_columns = [col for col in numeric.columns if numeric[col].notna().any()]

    if len(valid_columns) >= 2:
        x = numeric[valid_columns[0]].to_numpy(dtype=float)
        y = numeric[valid_columns[1]].to_numpy(dtype=float)
    elif len(valid_columns) == 1:
        x = pd.to_numeric(pd.Series(reference.index), errors="coerce").to_numpy(
            dtype=float
        )
        y = numeric[valid_columns[0]].to_numpy(dtype=float)
    else:
        raise ValueError("Reference file does not contain numeric data.")

    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]

    if x.size < 2:
        raise ValueError("Reference file must contain at least two numeric points.")

    order = np.argsort(x)
    return x[order], y[order]


def load_reflectance_reference(
    reference_path: str | Path,
) -> tuple[np.ndarray, np.ndarray]:
    reference_path = Path(reference_path)
    suffix = reference_path.suffix.lower()

    if suffix == ".csv":
        reference = pd.read_csv(
            reference_path, sep=";", skiprows=1, index_col=0, decimal=","
        )
        x = pd.to_numeric(pd.Series(reference.index), errors="coerce").to_numpy(
            dtype=float
        )
        y = pd.to_numeric(reference.iloc[:, 0], errors="coerce").to_numpy(dtype=float)
        mask = np.isfinite(x) & np.isfinite(y)
        x = x[mask]
        y = y[mask]
        if x.size < 2:
            raise ValueError("Reference file must contain at least two numeric points.")
        order = np.argsort(x)
        return x[order], y[order]

    if suffix in {".xlsx", ".xls", ".xlsm"}:
        reference = pd.read_excel(reference_path)
        return _extract_reference_xy(reference)

    raise ValueError(
        f"Unsupported reference file format '{suffix}'. Use .csv, .xlsx, .xls, or .xlsm."
    )


def calibrate_reflectance(
    data: pd.DataFrame,
    dark_standard_column: str,
    white_standard_column: str,
    dark_reference_csv: str | Path,
    white_reference_csv: str | Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dark_x, dark_y = load_reflectance_reference(dark_reference_csv)
    white_x, white_y = load_reflectance_reference(white_reference_csv)

    dark_func = interpolate.interp1d(dark_x, dark_y)
    white_func = interpolate.interp1d(white_x, white_y)

    calibration = pd.DataFrame(index=["m", "c"])
    for wav in data.index:
        dark_measured = _to_float(data.loc[wav, dark_standard_column])
        white_measured = _to_float(data.loc[wav, white_standard_column])
        m = (white_func(wav) - dark_func(wav)) / (white_measured - dark_measured)
        c = white_func(wav) - (m * white_measured)
        calibration[wav] = [float(m), float(c)]

    calibrated = pd.DataFrame(index=data.index)
    for column in data.columns:
        calibrated[column] = [
            _to_float(calibration.loc["m", wav]) * _to_float(data.loc[wav, column])
            + _to_float(calibration.loc["c", wav])
            for wav in data.index
        ]

    return calibrated, calibration


def export_and_plot_calibrated_reflectance(
    calibrated: pd.DataFrame,
    output_csv_path: str | Path,
    *,
    columns: list[str] | None = None,
    figsize: tuple[float, float] = (8, 4.5),
    ax: Axes | None = None,
) -> tuple[Path, Figure, Axes]:
    """Export calibrated reflectance data to CSV and plot calibrated %R traces."""
    output_csv = Path(output_csv_path)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    export_df = calibrated.copy()
    if export_df.index.name is None:
        export_df.index.name = "Wavelength (nm)"
    export_df.to_csv(output_csv)

    selected_columns = columns if columns is not None else list(calibrated.columns)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = cast(Figure, ax.figure)

    try:
        x_values = pd.to_numeric(pd.Series(calibrated.index), errors="coerce").to_numpy(
            dtype=float
        )
        x_mask = np.isfinite(x_values)
        x_label = "Wavelength / nm"
    except (TypeError, ValueError):
        x_values = np.arange(len(calibrated.index), dtype=float)
        x_mask = np.ones_like(x_values, dtype=bool)
        x_label = "Index"

    for column in selected_columns:
        y_values = pd.to_numeric(calibrated[column], errors="coerce").to_numpy(
            dtype=float
        )
        valid = x_mask & np.isfinite(y_values)
        ax.plot(x_values[valid], y_values[valid], label=column)

    ax.set_xlabel(x_label)
    ax.set_ylabel("Reflectance / %R")
    ax.set_title("Calibrated Reflectance")
    handles, _ = ax.get_legend_handles_labels()
    if handles:
        ax.legend()
    fig.tight_layout()

    return output_csv, fig, ax
