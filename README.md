# Spectroscopy

Code for spectroscopic data processing in the PAM group.

This repository is organized as a reusable Python package with one example notebook that demonstrates end-to-end usage.

## Repository Layout

1. `spectroscopy/`: reusable processing and plotting modules.
2. `Spectroscopy-Examples.ipynb`: worked examples for all major workflows.
3. `archive/notebooks/`: archived legacy notebooks.
4. `environment.yml`: environment definition for Conda.

## Create the Environment

This project uses an environment file named `environment.yml`.

```bash
conda env create -f environment.yml
conda activate spectroscopy
```

To update the environment after dependency changes:

```bash
conda env update -f environment.yml --prune
```

To remove the environment:

```bash
conda env remove -n spectroscopy
```

Note: `.env` files are typically for runtime environment variables, not Conda package environments. For this project, use `environment.yml` to create the Python environment.

## Quick Start

```python
from pathlib import Path
from spectroscopy import load_perkinelmer_results, calibrate_reflectance

sample_folder = Path(r"C:/path/to/perkin_folder")
sample_names, perkin_data = load_perkinelmer_results(sample_folder)
calibrated, calibration = calibrate_reflectance(
	perkin_data,
	dark_standard_column="2p5R_standard",
	white_standard_column="99R_standard",
	dark_reference_csv=Path(r"C:/path/to/dark_reference.xlsx"),
	white_reference_csv=Path(r"C:/path/to/white_reference.xlsx"),
)
```

Open `Spectroscopy-Examples.ipynb` to run complete examples and update file paths to your local data.

## Full Functionality

Import everything from the public API:

```python
from spectroscopy import *
```

### Raman

- `read_raman_spectrum(file_path)`: read single Raman spectrum text file.
- `preprocess_raman_spectrum(spectrum, wav_lower_limit, wav_upper_limit, ...)`: baseline-correct and filter spectrum.
- `extract_mapping_line(file_path, y_value, x_min, wav_lower_limit, ...)`: extract one mapping line from mapping export.
- `preprocess_raman_mapping_line(raw_data, x_points, y_value, wav_points, ...)`: process extracted mapping line.
- `find_nearest_wavenumber(wavenumbers, target)`: find nearest available wavenumber.

### PerkinElmer Reflectance

- `load_perkinelmer_results(sample_folder)`: load PerkinElmer result table and sample raw files.
- `load_reflectance_reference(reference_path)`: load dark/white reference from `.csv`, `.xlsx`, `.xls`, or `.xlsm`.
- `calibrate_reflectance(data, dark_standard_column, white_standard_column, dark_reference_csv, white_reference_csv)`: apply calibration to measured spectra.
- `export_and_plot_calibrated_reflectance(calibrated, output_csv_path, ...)`: export calibrated data to CSV and plot calibrated `%R`.

### FTIR

- `load_ftir_spectra(folder, file_stems)`: load FTIR spectra files into a DataFrame.
- `normalize_and_filter_ftir(data, ...)`: normalize and smooth FTIR spectra.
- `find_peak_wavenumbers(series, prominence=0.01)`: identify prominent FTIR peak positions.

### Fluorolog

- `load_fluorolog_dat(file_path, ...)`: load one Fluorolog `.dat` file.
- `load_fluorolog_folder(folder, ...)`: load all Fluorolog `.dat` files in a folder.
- `fit_fluorolog_peaks(x, y, ...)`: fit Gaussian-like peaks to a Fluorolog trace.

### Power / Lux Conversion

- `load_light_spectrum(light_file)`: load spectral irradiance data.
- `load_luminous_efficacy(csv_file)`: load photopic luminous efficacy table.
- `apply_luminous_efficacy(spectrum, efficacy)`: map spectral power to lumen contribution.
- `compute_irradiance_and_lux(with_lumen)`: compute integrated irradiance and lux.

### Camera Image Sequences

- `discover_image_sequence(sample_folder, prefix)`: count images in a sequence.
- `load_image_sequence(sample_folder, prefix, count, ...)`: load image series.
- `build_grayscale_histograms(images)`: create grayscale histograms.
- `fft_image_sequence(images)`: compute FFT for each image.

### Plotting Utilities

- `create_figure(...)`: create figure and axes with shared defaults.
- `plot_series(ax, x, y, ...)`: plot one trace on an axis.
- `plot_dataframe_columns(ax, data, ...)`: plot selected DataFrame columns.
- `finalize_axis(ax, ...)`: apply labels, limits, title, legend.
- `add_vertical_markers(ax, x_positions, ...)`: draw vertical guides.
- `plot_perkin_data_overview(perkin_data, ...)`: quick PerkinElmer overview plot.
- `plot_fluorolog_overview(fluorolog_data, ...)`: quick Fluorolog overview plot.
- `save_figure(fig, file_path, dpi=300)`: save figure with tight layout.

## Common Usage Examples

### Export and Plot Calibrated Reflectance

```python
from pathlib import Path
from spectroscopy import (
	calibrate_reflectance,
	export_and_plot_calibrated_reflectance,
	load_perkinelmer_results,
)

sample_folder = Path(r"C:/path/to/perkin_folder")
_, perkin_data = load_perkinelmer_results(sample_folder)

calibrated, calibration = calibrate_reflectance(
	perkin_data,
	dark_standard_column="2p5R_standard",
	white_standard_column="99R_standard",
	dark_reference_csv=Path(r"C:/path/to/dark_reference.xlsx"),
	white_reference_csv=Path(r"C:/path/to/white_reference.xlsx"),
)

output_csv, fig, ax = export_and_plot_calibrated_reflectance(
	calibrated,
	sample_folder / "calibrated_reflectance.csv",
	columns=[c for c in calibrated.columns if "standard" not in c.lower()],
)
```

### Fluorolog Folder Overview

```python
from pathlib import Path
from spectroscopy import load_fluorolog_folder, plot_fluorolog_overview

folder = Path(r"C:/path/to/fluorolog_folder")
file_table, fluorolog_data = load_fluorolog_folder(folder)
fig, ax, selected = plot_fluorolog_overview(
	fluorolog_data,
	normalize=True,
	peak_prominence=0.05,
	peak_fit_window_points=11,
)
```
