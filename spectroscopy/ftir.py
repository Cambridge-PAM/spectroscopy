"""FTIR helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.signal import find_peaks, savgol_filter


def load_ftir_spectra(
    sample_folder: str | Path, filenames: Iterable[str]
) -> dict[str, pd.DataFrame]:
    sample_folder = Path(sample_folder)
    data: dict[str, pd.DataFrame] = {}
    for filename in filenames:
        data[filename] = pd.read_csv(
            sample_folder / f"{filename}.csv", names=["Wavenumber", "Intensity"]
        )
    return data


def normalize_and_filter_ftir(
    spectra: dict[str, pd.DataFrame],
    savgol_window: int = 7,
    savgol_order: int = 2,
) -> dict[str, pd.Series]:
    processed: dict[str, pd.Series] = {}
    for name, spectrum in spectra.items():
        intensity = spectrum["Intensity"].to_numpy()
        norm = np.linalg.norm(intensity)
        normed = intensity / norm if norm != 0 else intensity
        filtered = savgol_filter(normed, savgol_window, savgol_order)
        processed[name] = pd.Series(filtered, index=spectrum["Wavenumber"], name=name)
    return processed


def find_peak_wavenumbers(series: pd.Series, prominence: float = 0.01) -> list[float]:
    peaks, _ = find_peaks(series.values, prominence=prominence)
    return [float(series.index[p]) for p in peaks]
