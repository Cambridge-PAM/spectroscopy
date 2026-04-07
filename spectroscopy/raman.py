"""Raman spectrum and mapping helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from BaselineRemoval import BaselineRemoval
from scipy.signal import find_peaks, savgol_filter


@dataclass
class MappingLine:
    x_points: np.ndarray
    wavenumbers: np.ndarray
    baseline_corrected: np.ndarray
    filtered: np.ndarray


def find_nearest_wavenumber(wavenumbers: Iterable[float], target: float) -> float:
    arr = np.asarray(list(wavenumbers), dtype=float)
    idx = np.searchsorted(arr, target, side="left")
    if idx > 0 and (
        idx == len(arr) or abs(target - arr[idx - 1]) < abs(target - arr[idx])
    ):
        return float(arr[idx - 1])
    return float(arr[idx])


def read_raman_spectrum(file_path: str | Path) -> pd.DataFrame:
    data = pd.read_csv(
        file_path, sep="\t", skiprows=1, names=["Wavenumber", "Intensity"], index_col=0
    )
    return data.sort_index()


def preprocess_raman_spectrum(
    spectrum: pd.DataFrame,
    wav_lower_limit: float,
    wav_upper_limit: float,
    baseline_order: int = 3,
    savgol_window: int = 25,
    savgol_order: int = 3,
) -> tuple[pd.Series, pd.Series]:
    lower = find_nearest_wavenumber(spectrum.index, wav_lower_limit)
    upper = find_nearest_wavenumber(spectrum.index, wav_upper_limit)
    windowed = spectrum.loc[(spectrum.index > lower) & (spectrum.index < upper)]

    baseline = BaselineRemoval(windowed["Intensity"]).ModPoly(baseline_order)
    norm = np.linalg.norm(baseline)
    normed = baseline / norm if norm != 0 else baseline
    filtered = savgol_filter(normed, savgol_window, savgol_order)

    baseline_series = pd.Series(normed, index=windowed.index, name="baseline_corrected")
    filtered_series = pd.Series(
        filtered, index=windowed.index, name="baseline_corrected_savgol"
    )
    return baseline_series, filtered_series


def extract_mapping_line(
    file_path: str | Path,
    y_value: float,
    x_min: float | None = None,
    wav_lower_limit: float = 1100,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    data = pd.read_csv(
        file_path, sep="\t", skiprows=1, names=["X", "Y", "Wavenumber", "Intensity"]
    )
    x_points = np.sort(data["X"].unique())
    wav_points = np.sort(data["Wavenumber"].unique())

    if x_min is not None:
        x_points = x_points[x_points > x_min]
    wav_points = wav_points[wav_points > wav_lower_limit]

    return data, x_points, wav_points


def preprocess_raman_mapping_line(
    data: pd.DataFrame,
    x_points: np.ndarray,
    y_value: float,
    wav_points: np.ndarray,
    wav_lower_limit: float = 1100,
    baseline_order: int = 2,
    savgol_window: int = 25,
    savgol_order: int = 3,
) -> MappingLine:
    baseline_corrected = []
    filtered = []

    for x_point in x_points:
        line = data.loc[
            (data["X"] == x_point)
            & (data["Y"] == y_value)
            & (data["Wavenumber"] > wav_lower_limit)
        ]
        baseline = BaselineRemoval(line["Intensity"]).ModPoly(baseline_order)
        smoothed = savgol_filter(baseline, savgol_window, savgol_order)
        baseline_corrected.append(baseline)
        filtered.append(smoothed)

    baseline_arr = np.concatenate(baseline_corrected).reshape(
        len(x_points), len(wav_points)
    )
    filtered_arr = np.concatenate(filtered).reshape(len(x_points), len(wav_points))

    return MappingLine(
        x_points=x_points,
        wavenumbers=wav_points,
        baseline_corrected=baseline_arr,
        filtered=filtered_arr,
    )


def find_peak_wavenumbers(spectrum: pd.Series, prominence: float) -> list[float]:
    peaks, _ = find_peaks(spectrum.values, prominence=prominence)
    return [float(spectrum.index[p]) for p in peaks]
