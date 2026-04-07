"""Power-spectrum to illuminance helpers."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter


def load_light_spectrum(light_file: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    metadata = pd.read_csv(light_file, sep="\t", nrows=10, index_col=0, names=["value"])
    spectrum = pd.read_csv(
        light_file, sep="\t", skiprows=10, index_col=0, names=["power"]
    )
    return metadata, spectrum


def load_luminous_efficacy(csv_file: str | Path) -> pd.DataFrame:
    return pd.read_csv(
        csv_file,
        skiprows=1,
        index_col=0,
        names=["photopic", "photopic_f", "scotopic", "scotopic_f"],
    )


def apply_luminous_efficacy(
    spectrum: pd.DataFrame,
    luminous_efficacy: pd.DataFrame,
    savgol_window: int = 9,
    savgol_order: int = 2,
) -> pd.DataFrame:
    result = spectrum.copy()
    result["power_clean"] = savgol_filter(result["power"], savgol_window, savgol_order)

    interp = interp1d(
        luminous_efficacy.index,
        luminous_efficacy["photopic_f"],
        bounds_error=False,
        fill_value=0,
    )
    conversion = interp(result.index)
    result["lumen"] = result["power_clean"] * conversion * 1e-6
    return result


def compute_irradiance_and_lux(
    spectrum: pd.DataFrame,
    radius_m: float = 1e-2,
    integration_min_nm: int = 380,
    integration_max_nm: int = 770,
) -> tuple[pd.DataFrame, float, float]:
    result = spectrum.copy()
    area_m2 = math.pi * radius_m**2
    result["irr"] = (result["power_clean"] * 1e-3) / (area_m2 * 1e4)
    result["lux"] = result["lumen"] / area_m2

    int_lux = float(np.trapz(result["lux"].values, x=result.index))
    visible = result.truncate(before=integration_min_nm, after=integration_max_nm)
    int_irr = float(np.trapz(visible["irr"].values, x=visible.index))

    return result, int_lux, int_irr
