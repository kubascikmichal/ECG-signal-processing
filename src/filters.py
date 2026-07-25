"""Signal filtering helpers for ECG analysis."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import butter, filtfilt


def bandpass_filter(
    signal: np.ndarray | list[float],
    fs: float,
    lowcut: float = 0.5,
    highcut: float = 40.0,
    order: int = 4,
) -> np.ndarray:
    """Apply a Butterworth band-pass filter to an ECG signal.

    Args:
        signal: Input ECG signal.
        fs: Sampling frequency in Hertz.
        lowcut: Lower cutoff frequency in Hertz.
        highcut: Upper cutoff frequency in Hertz.
        order: Butterworth filter order.

    Returns:
        The filtered ECG signal.

    Raises:
        ValueError: If the filter configuration is invalid.
    """

    if fs <= 0:
        raise ValueError("Sampling frequency must be positive")
    if lowcut <= 0:
        raise ValueError("Lowcut must be positive")
    if highcut <= lowcut:
        raise ValueError("Highcut must be greater than lowcut")

    signal_array = np.asarray(signal, dtype=float)
    if signal_array.ndim != 1:
        raise ValueError("bandpass_filter expects a one-dimensional ECG signal")
    if signal_array.size == 0:
        return signal_array.copy()

    nyquist = 0.5 * fs
    if highcut >= nyquist:
        raise ValueError("Highcut must be below the Nyquist frequency")

    normalized_band = [lowcut / nyquist, highcut / nyquist]
    b_coefficients, a_coefficients = butter(order, normalized_band, btype="bandpass")
    return filtfilt(b_coefficients, a_coefficients, signal_array)
