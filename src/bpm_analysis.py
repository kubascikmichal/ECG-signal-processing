"""RR interval and BPM calculations."""

from __future__ import annotations

import numpy as np


def calculate_rr_intervals(r_peaks: np.ndarray | list[int], fs: float) -> np.ndarray:
    """Calculate RR intervals in seconds from R-peak sample locations."""

    peaks = np.asarray(r_peaks, dtype=float)
    if peaks.ndim != 1:
        raise ValueError("r_peaks must be one-dimensional")
    if fs <= 0:
        raise ValueError("Sampling frequency must be positive")
    if peaks.size < 2:
        return np.asarray([], dtype=float)

    return np.diff(peaks) / float(fs)


def calculate_bpm(rr_intervals: np.ndarray | list[float]) -> np.ndarray:
    """Calculate instantaneous BPM values from RR intervals in seconds."""

    rr_array = np.asarray(rr_intervals, dtype=float)
    if rr_array.ndim != 1:
        raise ValueError("rr_intervals must be one-dimensional")
    if rr_array.size == 0:
        return np.asarray([], dtype=float)

    with np.errstate(divide="ignore", invalid="ignore"):
        bpm = np.where(rr_array > 0, 60.0 / rr_array, np.nan)
    return bpm


def calculate_average_bpm(rr_intervals: np.ndarray | list[float]) -> float:
    """Calculate the average BPM from RR intervals in seconds."""

    bpm = calculate_bpm(rr_intervals)
    if bpm.size == 0:
        return float("nan")
    return float(np.nanmean(bpm))
