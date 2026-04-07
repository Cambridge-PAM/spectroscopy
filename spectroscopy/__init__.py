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
    "discover_image_sequence",
    "extract_mapping_line",
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
    "preprocess_raman_mapping_line",
    "preprocess_raman_spectrum",
    "read_raman_spectrum",
]
