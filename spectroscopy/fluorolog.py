"""Fluorolog .dat import and plotting helpers."""

from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.signal import find_peaks


def _normalize_label(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.strip().lower())


def load_fluorolog_dat(
    file_path: str | Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load one Fluorolog .dat file and return numeric data plus column metadata."""
    file_path = Path(file_path)
    raw = pd.read_csv(file_path, sep="\t", header=None, dtype=str).fillna("")

    if len(raw) < 2:
        raise ValueError(f"File {file_path} does not contain enough header rows.")

    first_cell = str(raw.iloc[0, 0]).strip().lower()

    if first_cell == "short name":
        # Legacy format: row0=short names, row1=long names, row2=units, then data.
        if len(raw) < 4:
            raise ValueError(
                f"Legacy-format file {file_path} does not contain expected header rows."
            )
        columns = [str(value).strip() for value in raw.iloc[0].tolist()]
        long_names = pd.Series(raw.iloc[1].tolist(), dtype="string").str.strip()
        units = pd.Series(raw.iloc[2].tolist(), dtype="string").str.strip()
        data = raw.iloc[3:].copy()
    else:
        # New format: row0=short names, row1=units, then data.
        columns = [str(value).strip() for value in raw.iloc[0].tolist()]
        long_names = pd.Series(columns, dtype="string")
        units = pd.Series(raw.iloc[1].tolist(), dtype="string").str.strip()
        data = raw.iloc[2:].copy()

    # Make duplicate column headers unique while preserving readable names.
    seen: dict[str, int] = {}
    unique_columns: list[str] = []
    for name in columns:
        count = seen.get(name, 0)
        unique_name = name if count == 0 else f"{name}_{count}"
        unique_columns.append(unique_name)
        seen[name] = count + 1

    metadata = pd.DataFrame(
        {
            "short_name": unique_columns,
            "long_name": long_names.values,
            "units": units.values,
        }
    )

    data.columns = unique_columns
    for column in data.columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(how="all").reset_index(drop=True)
    return data, metadata


def _infer_xy_columns(
    data: pd.DataFrame,
    metadata: pd.DataFrame,
    x_column: str | None,
    y_column: str | None,
    preferred_y: str | None = None,
) -> tuple[str, str, str, str]:
    non_index_columns = [col for col in data.columns if col.lower() != "short name"]
    if not non_index_columns:
        raise ValueError("No numeric data columns found in Fluorolog file.")

    if x_column is None:
        wavelength_columns = metadata.loc[
            metadata["long_name"].str.lower() == "wavelength", "short_name"
        ].tolist()
        wavelength_columns = [
            col for col in wavelength_columns if col in non_index_columns
        ]
        x_column = wavelength_columns[0] if wavelength_columns else non_index_columns[0]

    if y_column is None:
        if preferred_y is not None:
            preferred_norm = _normalize_label(preferred_y)
            preferred_matches = [
                col
                for col in non_index_columns
                if _normalize_label(col) == preferred_norm
            ]
            if preferred_matches:
                y_column = preferred_matches[0]

    if y_column is None:
        ordered = [col for col in non_index_columns if col != x_column]
        if x_column in non_index_columns:
            x_idx = non_index_columns.index(x_column)
            if x_idx + 1 < len(non_index_columns):
                y_column = non_index_columns[x_idx + 1]
            elif ordered:
                y_column = ordered[0]
        elif ordered:
            y_column = ordered[0]

    if y_column is None:
        raise ValueError("Could not infer y column from Fluorolog data.")

    if x_column is None:
        raise ValueError("Could not infer x column from Fluorolog data.")

    x_meta = metadata.loc[metadata["short_name"] == x_column].iloc[0]
    y_meta = metadata.loc[metadata["short_name"] == y_column].iloc[0]

    x_label = f"{x_meta['long_name']} / {x_meta['units']}"
    y_label = f"{y_meta['long_name']} / {y_meta['units']}"
    return x_column, y_column, x_label, y_label


def load_fluorolog_folder(
    folder: str | Path,
    x_column: str | None = None,
    y_column: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load all .dat files in a folder into one DataFrame indexed by x values."""
    folder = Path(folder)
    dat_files = sorted(folder.glob("*.dat"))
    if not dat_files:
        raise FileNotFoundError(f"No .dat files were found in {folder}.")

    file_rows: list[dict[str, str]] = []
    series_dict: dict[str, pd.Series] = {}

    inferred_x_label = "X"
    inferred_x_name = "Wavelength"
    inferred_y_label = "Signal"
    inferred_y_names_by_suffix: dict[str, str] = {}
    inferred_y_labels_by_suffix: dict[str, str] = {}

    for dat_file in dat_files:
        suffix_flag = dat_file.stem[-1].lower() if dat_file.stem else ""
        if suffix_flag == "x":
            file_priority_y = "S1cR1c"
            print(
                f"Loading {dat_file.name}: filename ends with 'x', prioritizing y column 'S1cR1c'."
            )
        elif suffix_flag == "m":
            file_priority_y = "S1c"
            print(
                f"Loading {dat_file.name}: filename ends with 'm', prioritizing y column 'S1c'."
            )
        else:
            print(f"Skipping {dat_file.name}: filename does not end with 'm' or 'x'.")
            continue

        data, metadata = load_fluorolog_dat(dat_file)
        x_col, y_col, x_label, y_label = _infer_xy_columns(
            data,
            metadata,
            x_column,
            y_column,
            preferred_y=file_priority_y,
        )
        x_meta = metadata.loc[metadata["short_name"] == x_col].iloc[0]
        y_meta = metadata.loc[metadata["short_name"] == y_col].iloc[0]

        print(f"Using columns for {dat_file.name}: x='{x_col}', y='{y_col}'.")

        series = pd.Series(
            data[y_col].values,
            index=data[x_col].values,
            name=dat_file.stem,
        )
        series_dict[dat_file.stem] = series
        inferred_x_label = x_label
        inferred_x_name = str(x_meta["long_name"])
        inferred_y_label = y_label
        inferred_y_names_by_suffix[suffix_flag] = str(y_meta["long_name"])
        inferred_y_labels_by_suffix[suffix_flag] = y_label

        file_rows.append(
            {
                "file": dat_file.name,
                "sample": dat_file.stem,
                "x_column": x_col,
                "y_column": y_col,
            }
        )

    if not series_dict:
        raise FileNotFoundError(
            "No Fluorolog .dat files matched the naming rule (ending in 'm' or 'x')."
        )

    fluorolog_data = pd.concat(series_dict, axis=1).sort_index()
    fluorolog_data.attrs["x_label"] = inferred_x_label
    fluorolog_data.attrs["x_name"] = inferred_x_name
    fluorolog_data.attrs["y_label"] = inferred_y_label
    fluorolog_data.attrs["y_name_m"] = inferred_y_names_by_suffix.get("m", "Signal")
    fluorolog_data.attrs["y_name_x"] = inferred_y_names_by_suffix.get("x", "Signal")
    fluorolog_data.attrs["y_label_m"] = inferred_y_labels_by_suffix.get(
        "m", "Signal / a.u."
    )
    fluorolog_data.attrs["y_label_x"] = inferred_y_labels_by_suffix.get(
        "x", "Signal / a.u."
    )

    file_table = pd.DataFrame(file_rows).set_index("sample")
    return file_table, fluorolog_data


def _gaussian_with_offset(
    x_values: np.ndarray,
    amplitude: float,
    center: float,
    sigma: float,
    offset: float,
) -> np.ndarray:
    return amplitude * np.exp(-0.5 * ((x_values - center) / sigma) ** 2) + offset


def fit_fluorolog_peaks(
    fluorolog_data: pd.DataFrame,
    columns: list[str] | None = None,
    *,
    prominence: float | None = None,
    max_peaks_per_trace: int | None = None,
    fit_window_points: int = 9,
    normalize: bool = True,
) -> pd.DataFrame:
    """Detect and fit fluorescence peaks for selected Fluorolog traces.

    The function detects candidate peaks with ``scipy.signal.find_peaks`` and then
    refines each candidate using a local Gaussian + constant-offset fit. Set
    ``max_peaks_per_trace=None`` to fit all detected peaks in each trace.
    """
    if fit_window_points < 5:
        raise ValueError("fit_window_points must be at least 5.")

    half_window = fit_window_points // 2
    selected_columns = list(columns) if columns is not None else list(fluorolog_data)
    rows: list[dict[str, float | str | bool]] = []

    for column in selected_columns:
        if column not in fluorolog_data:
            continue

        series = fluorolog_data[column].dropna()
        if series.empty:
            continue

        x_series = pd.to_numeric(series.index.to_series(), errors="coerce")
        y_series = pd.to_numeric(series, errors="coerce")
        valid = x_series.notna() & y_series.notna()
        x_values = x_series[valid].to_numpy(dtype=float)
        y_values = y_series[valid].to_numpy(dtype=float)

        if len(x_values) < 5:
            continue

        if normalize:
            max_value = np.nanmax(y_values)
            if np.isfinite(max_value) and max_value != 0:
                y_values = y_values / max_value

        dynamic_prominence = (
            prominence
            if prominence is not None
            else max(0.05 * float(np.nanmax(y_values) - np.nanmin(y_values)), 1e-8)
        )
        peak_indices, peak_props = find_peaks(y_values, prominence=dynamic_prominence)
        if len(peak_indices) == 0:
            continue

        prominences = peak_props.get("prominences", np.zeros(len(peak_indices)))
        order = np.argsort(prominences)[::-1]
        if max_peaks_per_trace is None:
            keep_count = len(order)
        else:
            keep_count = max(1, min(int(max_peaks_per_trace), len(order)))

        for rank, order_index in enumerate(order[:keep_count], start=1):
            peak_idx = int(peak_indices[order_index])
            start = max(0, peak_idx - half_window)
            end = min(len(x_values), peak_idx + half_window + 1)
            if end - start < 5:
                continue

            x_fit = x_values[start:end]
            y_fit = y_values[start:end]

            initial_amplitude = float(
                max(y_values[peak_idx] - np.nanmedian(y_fit), 1e-8)
            )
            initial_center = float(x_values[peak_idx])
            x_span = float(max(x_fit) - min(x_fit))
            initial_sigma = max(x_span / 6.0, 1e-6)
            initial_offset = float(np.nanmedian(y_fit))

            lower_bounds = [0.0, float(min(x_fit)), 1e-9, -np.inf]
            upper_bounds = [
                float(max(y_fit) * 2.0 + 1.0),
                float(max(x_fit)),
                max(x_span, 1e-6),
                np.inf,
            ]

            try:
                params, _ = curve_fit(
                    _gaussian_with_offset,
                    x_fit,
                    y_fit,
                    p0=[
                        initial_amplitude,
                        initial_center,
                        initial_sigma,
                        initial_offset,
                    ],
                    bounds=(lower_bounds, upper_bounds),
                    maxfev=5000,
                )
                amplitude, center, sigma, offset = [float(p) for p in params]
                success = True
            except Exception:
                amplitude = float(y_values[peak_idx] - np.nanmin(y_fit))
                center = float(x_values[peak_idx])
                sigma = np.nan
                offset = float(np.nanmin(y_fit))
                success = False

            fitted_height = amplitude + offset
            fwhm = float(2.354820045 * sigma) if np.isfinite(sigma) else np.nan

            rows.append(
                {
                    "column": str(column),
                    "peak_rank": rank,
                    "peak_wavelength": float(center),
                    "peak_height": float(fitted_height),
                    "amplitude": float(amplitude),
                    "offset": float(offset),
                    "sigma": float(sigma) if np.isfinite(sigma) else np.nan,
                    "fwhm": fwhm,
                    "success": success,
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=[
                "column",
                "peak_rank",
                "peak_wavelength",
                "peak_height",
                "amplitude",
                "offset",
                "sigma",
                "fwhm",
                "success",
            ]
        )

    peaks = pd.DataFrame(rows)
    peaks = peaks.sort_values(["column", "peak_rank"]).reset_index(drop=True)
    return peaks
