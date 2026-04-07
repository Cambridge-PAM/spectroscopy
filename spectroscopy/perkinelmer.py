"""PerkinElmer absorbance and reflectance helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
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


def load_reflectance_reference(csv_path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    reference = pd.read_csv(csv_path, sep=";", skiprows=1, index_col=0, decimal=",")
    return reference.index.values, reference.values.ravel()


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
