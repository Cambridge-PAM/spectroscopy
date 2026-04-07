"""Reusable utilities for spectroscopy data processing."""

from .camera import (
    build_grayscale_histograms,
    discover_image_sequence,
    fft_image_sequence,
    load_image_sequence,
)
from .ftir import find_peak_wavenumbers, load_ftir_spectra, normalize_and_filter_ftir
from .perkinelmer import (
    calibrate_reflectance,
    load_perkinelmer_results,
    load_reflectance_reference,
)
from .power import (
    apply_luminous_efficacy,
    compute_irradiance_and_lux,
    load_light_spectrum,
    load_luminous_efficacy,
)
from .plotting import (
    add_vertical_markers,
    create_figure,
    finalize_axis,
    plot_dataframe_columns,
    plot_perkin_data_overview,
    plot_series,
    rc_file_context,
    save_figure,
)
from .raman import (
    extract_mapping_line,
    find_nearest_wavenumber,
    preprocess_raman_mapping_line,
    preprocess_raman_spectrum,
    read_raman_spectrum,
)

__all__ = [
    "apply_luminous_efficacy",
    "build_grayscale_histograms",
    "calibrate_reflectance",
    "compute_irradiance_and_lux",
    "create_figure",
    "discover_image_sequence",
    "extract_mapping_line",
    "finalize_axis",
    "fft_image_sequence",
    "find_nearest_wavenumber",
    "find_peak_wavenumbers",
    "load_ftir_spectra",
    "load_image_sequence",
    "load_light_spectrum",
    "load_luminous_efficacy",
    "load_perkinelmer_results",
    "load_reflectance_reference",
    "normalize_and_filter_ftir",
    "plot_dataframe_columns",
    "plot_perkin_data_overview",
    "plot_series",
    "preprocess_raman_mapping_line",
    "preprocess_raman_spectrum",
    "rc_file_context",
    "read_raman_spectrum",
    "save_figure",
    "add_vertical_markers",
]
