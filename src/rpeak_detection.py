"""R-peak detection utilities."""

from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.signal import find_peaks

try:
    import neurokit2 as nk
except ImportError as exc:  # pragma: no cover - dependency availability.
    nk = None
    _NEUROKIT_IMPORT_ERROR = exc
else:
    _NEUROKIT_IMPORT_ERROR = None

DetectionStrategy = Callable[[np.ndarray, float], np.ndarray]


def _detect_with_neurokit(signal: np.ndarray, fs: float) -> np.ndarray:
    """Detect R-peaks with NeuroKit2."""

    if nk is None:
        raise ImportError("neurokit2 is required for NeuroKit-based detection") from _NEUROKIT_IMPORT_ERROR

    _, info = nk.ecg_peaks(signal, sampling_rate=fs)
    peaks = np.asarray(info.get("ECG_R_Peaks", []), dtype=int)
    return peaks


def _detect_with_fallback(signal: np.ndarray, fs: float) -> np.ndarray:
    """Fallback detector using scipy.signal.find_peaks."""

    minimum_distance = max(int(0.25 * fs), 1)
    prominence = float(np.nanstd(signal) * 0.5) if signal.size else 0.0
    peaks, _ = find_peaks(signal, distance=minimum_distance, prominence=prominence)
    return np.asarray(peaks, dtype=int)


def detect_r_peaks(signal: np.ndarray | list[float], fs: float) -> tuple[np.ndarray, int]:
    """Detect R-peaks in an ECG signal.

    NeuroKit2 is used as the primary backend, with a deterministic SciPy-based
    fallback for environments where the NeuroKit pipeline fails.

    Args:
        signal: ECG signal, ideally filtered.
        fs: Sampling frequency in Hertz.

    Returns:
        A tuple containing detected R-peak sample locations and the peak count.
    """

    signal_array = np.asarray(signal, dtype=float)
    if signal_array.ndim != 1:
        raise ValueError("detect_r_peaks expects a one-dimensional ECG signal")
    if signal_array.size == 0:
        return np.asarray([], dtype=int), 0

    peaks = np.asarray([], dtype=int)
    if nk is not None:
        try:
            peaks = _detect_with_neurokit(signal_array, fs)
        except Exception:
            peaks = np.asarray([], dtype=int)

    if peaks.size == 0:
        peaks = _detect_with_fallback(signal_array, fs)

    peaks = np.unique(peaks.astype(int, copy=False))
    peaks = peaks[(peaks >= 0) & (peaks < signal_array.size)]
    return peaks, int(peaks.size)
