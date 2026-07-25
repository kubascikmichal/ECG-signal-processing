"""Tests for RR interval and BPM calculations."""

from __future__ import annotations

import numpy as np

from src.bpm_analysis import calculate_average_bpm, calculate_bpm, calculate_rr_intervals


def test_rr_interval_and_bpm_calculation() -> None:
    """RR intervals and BPM should be computed from sample indices."""

    fs = 360.0
    r_peaks = np.array([0, 360, 720], dtype=int)

    rr_intervals = calculate_rr_intervals(r_peaks, fs)
    bpm = calculate_bpm(rr_intervals)
    average_bpm = calculate_average_bpm(rr_intervals)

    assert np.allclose(rr_intervals, np.array([1.0, 1.0]))
    assert np.allclose(bpm, np.array([60.0, 60.0]))
    assert average_bpm == 60.0
