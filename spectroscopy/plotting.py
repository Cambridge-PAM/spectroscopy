"""Base plotting utilities shared across spectroscopy workflows."""

from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.pyplot import rc_context


def rc_file_context(rc_file: str | Path | None = None):
    """Return a context manager that applies a matplotlib rc file when provided."""
    if rc_file is None:
        return nullcontext()
    return rc_context(fname=str(rc_file))


def create_figure(
    figsize: tuple[float, float] = (6, 4),
    nrows: int = 1,
    ncols: int = 1,
    sharex: bool = False,
) -> tuple[Figure, Axes | list[Axes]]:
    """Create a matplotlib figure and axes with common defaults."""
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, sharex=sharex)
    if hasattr(axes, "flatten"):
        return fig, list(axes.flatten())
    return fig, axes


def plot_series(
    ax: Axes,
    x: Iterable[float],
    y: Iterable[float],
    *,
    label: str | None = None,
    color: str | None = None,
    linewidth: float = 1.5,
) -> Axes:
    """Plot one line on the provided axis and return the same axis."""
    ax.plot(list(x), list(y), label=label, color=color, lw=linewidth)
    return ax


def plot_dataframe_columns(
    ax: Axes,
    data: pd.DataFrame,
    columns: Iterable[str] | None = None,
    *,
    x_values: Iterable[float] | None = None,
) -> Axes:
    """Plot selected DataFrame columns against index or explicit x values."""
    selected = list(columns) if columns is not None else list(data.columns)
    x = list(x_values) if x_values is not None else data.index.to_list()
    for column in selected:
        ax.plot(x, data[column], label=column)
    return ax


def finalize_axis(
    ax: Axes,
    *,
    xlabel: str | None = None,
    ylabel: str | None = None,
    title: str | None = None,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    legend: bool = True,
) -> Axes:
    """Apply common axis labels, limits, and optional legend."""
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    if legend:
        handles, _ = ax.get_legend_handles_labels()
        if handles:
            ax.legend()
    return ax


def add_vertical_markers(
    ax: Axes,
    x_positions: Iterable[float],
    *,
    color: str = "red",
    linestyle: str = ":",
    linewidth: float = 1.0,
) -> Axes:
    """Add vertical guide lines to an axis."""
    for x_pos in x_positions:
        ax.axvline(x_pos, color=color, ls=linestyle, lw=linewidth)
    return ax


def save_figure(fig: Figure, file_path: str | Path, dpi: int = 300) -> None:
    """Save a figure with tight layout and consistent default DPI."""
    fig.tight_layout()
    fig.savefig(file_path, dpi=dpi)


def plot_perkin_data_overview(
    perkin_data: pd.DataFrame,
    *,
    rc_file: str | Path | None = "plotting_params.txt",
    max_columns: int | None = None,
    figsize: tuple[float, float] = (8, 4.5),
) -> tuple[Figure, Axes, list[str]]:
    """Plot a quick overview of PerkinElmer data using shared plotting defaults."""
    if max_columns is None:
        selected_columns = list(perkin_data.columns)
    else:
        selected_columns = list(
            perkin_data.columns[: min(max_columns, len(perkin_data.columns))]
        )

    x_values: list[float] | list[int]
    x_label: str
    try:
        x_values = perkin_data.index.astype(float).to_list()
        x_label = "Wavelength / nm"
    except (TypeError, ValueError):
        x_values = list(range(len(perkin_data.index)))
        x_label = "Index"

    source_y_label = str(perkin_data.attrs.get("y_column_label", "")).strip().upper()
    source_y_labels = {
        str(label).strip().upper()
        for label in perkin_data.attrs.get("y_column_labels", [])
    }
    has_absorbance_column = (
        source_y_label == "A"
        or "A" in source_y_labels
        or "A" in {str(col).strip().upper() for col in perkin_data.columns}
    )
    y_label = "Absorbance" if has_absorbance_column else "Signal / a.u."
    y_limits = (0, 3) if has_absorbance_column else None
    x_limits = (min(x_values), max(x_values)) if x_values else None

    with rc_file_context(rc_file):
        fig, ax = create_figure(figsize=figsize)
        if isinstance(ax, list):
            ax = ax[0]
        plot_dataframe_columns(
            ax, perkin_data, columns=selected_columns, x_values=x_values
        )
        finalize_axis(
            ax,
            xlabel=x_label,
            ylabel=y_label,
            xlim=x_limits,
            ylim=y_limits,
            legend=True,
        )

    return fig, ax, selected_columns
