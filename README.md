# Spectroscopy
Code for spectroscopic data processing in the PAM group.

This repository has been refactored from notebook-centric scripts into reusable Python modules.

## Layout

1. **spectroscopy/** Reusable package with processing functions:
	- `raman.py`
	- `perkinelmer.py`
	- `ftir.py`
	- `power.py`
	- `camera.py`
	- `plotting.py`
	- `fluorolog.py`
2. **Spectroscopy-Examples.ipynb** Single notebook that demonstrates example usage of the module APIs.
3. **archive/notebooks/** Archived legacy notebooks retained for reference.
4. **environment.yml** Conda environment definition for the package and notebook examples.

## Install

```bash
conda env create -f environment.yml
conda activate spectroscopy
```

## Usage

Open **Spectroscopy-Examples.ipynb** and update the example file paths to your local data.

## Plotting Helpers

The `spectroscopy.plotting` module provides base plotting utilities to keep plot styling and behavior consistent across workflows.

- `create_figure`: create figures/subplots with shared defaults.
- `plot_dataframe_columns`: plot one or more DataFrame columns.
- `finalize_axis`: apply labels, limits, titles, and legends.
- `add_vertical_markers`: add guide lines for peaks or regions of interest.
- `plot_perkin_data_overview`: one-call overview plot for PerkinElmer DataFrames.
- `plot_fluorolog_overview`: one-call overview plot for Fluorolog folder imports.
- `save_figure`: save figures with tight layout and default DPI.

## Fluorolog (.dat) Workflow

Use the Fluorolog helpers to import all `.dat` files from a folder and plot them in one overview figure.

```python
from pathlib import Path
from spectroscopy import load_fluorolog_folder, plot_fluorolog_overview

folder = Path("C:/path/to/fluorolog_folder")
file_table, fluorolog_data = load_fluorolog_folder(folder)
fig, ax, selected_columns = plot_fluorolog_overview(fluorolog_data)
```

Notes:
- `load_fluorolog_folder` scans all `.dat` files in the folder.
- By default it infers x/y columns from each file header rows (`Short Name`, `Long Name`, `Units`).
- You can override column selection with `x_column=...` and `y_column=...`.
