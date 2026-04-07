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
2. **Spectroscopy-Examples.ipynb** Single notebook that demonstrates example usage of the module APIs.
3. **archive/notebooks/** Archived legacy notebooks retained for reference.
4. **plotting_params.txt** Matplotlib style parameters.
5. **environment.yml** Conda environment definition for the package and notebook examples.

## Install

```bash
conda env create -f environment.yml
conda activate spectroscopy
```

## Usage

Open **Spectroscopy-Examples.ipynb** and update the example file paths to your local data.

## Plotting Helpers

The `spectroscopy.plotting` module provides base plotting utilities to keep plot styling and behavior consistent across workflows.

- `rc_file_context`: apply `plotting_params.txt` through a context manager.
- `create_figure`: create figures/subplots with shared defaults.
- `plot_dataframe_columns`: plot one or more DataFrame columns.
- `finalize_axis`: apply labels, limits, titles, and legends.
- `add_vertical_markers`: add guide lines for peaks or regions of interest.
- `plot_perkin_data_overview`: one-call overview plot for PerkinElmer DataFrames.
- `save_figure`: save figures with tight layout and default DPI.
