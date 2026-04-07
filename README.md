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
