"""Image sequence helpers for LWEL fabrication analysis."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


def discover_image_sequence(sample_folder: str | Path, prefix: str) -> int:
    sample_folder = Path(sample_folder)
    n = 0
    while (sample_folder / f"{prefix}-{str(n).zfill(4)}.png").exists():
        n += 1
    return n


def load_image_sequence(
    sample_folder: str | Path, prefix: str, count: int
) -> dict[int, Image.Image]:
    sample_folder = Path(sample_folder)
    return {
        i: Image.open(sample_folder / f"{prefix}-{str(i).zfill(4)}.png")
        for i in range(count)
    }


def build_grayscale_histograms(images: dict[int, Image.Image]) -> pd.DataFrame:
    arr_histogram = []
    for _, image in images.items():
        arr_histogram.append(image.convert("L").histogram())

    time_id = np.arange(len(images), dtype=int)
    histogram_x = np.arange(256, dtype=int)
    df_histogram = pd.DataFrame(data=arr_histogram, index=time_id, columns=histogram_x)
    return df_histogram.drop(columns=255)


def fft_image_sequence(images: dict[int, Image.Image]) -> dict[int, np.ndarray]:
    images_fft: dict[int, np.ndarray] = {}
    for idx, image in images.items():
        arr = np.asarray(image.convert("L"))
        images_fft[idx] = np.fft.fftshift(np.fft.fft2(arr))
    return images_fft
