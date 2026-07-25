"""Tests for ECG filtering helpers."""

from __future__ import annotations

import numpy as np

from src.filters import bandpass_filter


def test_bandpass_filter_preserves_signal_length() -> None:
    """The filtered output should match the input length."""

    fs = 360.0
    time = np.arange(0, 5, 1 / fs)
    signal = np.sin(2 * np.pi * 1.0 * time) + 0.2 * np.sin(2 * np.pi * 50.0 * time)

    filtered = bandpass_filter(signal, fs)

    assert filtered.shape == signal.shape
    assert np.isfinite(filtered).all()
