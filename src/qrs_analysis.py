"""QRS feature extraction utilities."""

from __future__ import annotations

from typing import Any

import numpy as np

try:
    import neurokit2 as nk
except ImportError as exc:  # pragma: no cover - dependency availability.
    nk = None
    _NEUROKIT_IMPORT_ERROR = exc
else:
    _NEUROKIT_IMPORT_ERROR = None


def _estimate_qrs_duration_fallback(signal: np.ndarray, r_peaks: np.ndarray, fs: float) -> np.ndarray:
    """Estimate QRS duration with a local width heuristic."""

    durations: list[float] = []
    half_window = max(int(0.12 * fs), 1)

    for peak in r_peaks:
        left = max(int(peak) - half_window, 0)
        right = min(int(peak) + half_window, signal.size - 1)
        segment = signal[left : right + 1]
        if segment.size < 3:
            continue

        baseline = float(np.median(segment))
        amplitude = float(signal[int(peak)] - baseline)
        threshold = baseline + 0.5 * amplitude

        left_candidates = np.where(segment[: int(peak) - left + 1] <= threshold)[0]
        right_candidates = np.where(segment[int(peak) - left :] <= threshold)[0]
        if left_candidates.size == 0 or right_candidates.size == 0:
            continue

        q_index = left + int(left_candidates[-1])
        s_index = left + int(peak - left) + int(right_candidates[0])
        if s_index <= q_index:
            continue

        durations.append((s_index - q_index) / float(fs) * 1000.0)

    return np.asarray(durations, dtype=float)


def _estimate_qrs_duration_neurokit(signal: np.ndarray, r_peaks: np.ndarray, fs: float) -> np.ndarray:
    """Estimate QRS duration using NeuroKit delineation when available."""

    if nk is None:
        raise ImportError("neurokit2 is required for NeuroKit-based QRS analysis") from _NEUROKIT_IMPORT_ERROR

    _, waves = nk.ecg_delineate(signal, r_peaks, sampling_rate=fs, method="dwt", show=False)
    onsets = waves.get("ECG_QRS_Onsets")
    offsets = waves.get("ECG_QRS_Offsets")
    if onsets is None or offsets is None:
        return np.asarray([], dtype=float)

    durations: list[float] = []
    onsets_array = np.asarray(onsets, dtype=float)
    offsets_array = np.asarray(offsets, dtype=float)
    for onset, offset in zip(onsets_array, offsets_array, strict=False):
        if np.isnan(onset) or np.isnan(offset):
            continue
        if offset <= onset:
            continue
        durations.append((offset - onset) / float(fs) * 1000.0)
    return np.asarray(durations, dtype=float)


def analyze_qrs(signal: np.ndarray | list[float], r_peaks: np.ndarray | list[int], fs: float) -> dict[str, Any]:
    """Extract QRS-related summary statistics from an ECG signal.

    Args:
        signal: Filtered ECG signal.
        r_peaks: R-peak sample locations.
        fs: Sampling frequency in Hertz.

    Returns:
        A dictionary containing amplitudes, durations, and counts.
    """

    signal_array = np.asarray(signal, dtype=float)
    peaks = np.asarray(r_peaks, dtype=int)
    if signal_array.ndim != 1:
        raise ValueError("signal must be one-dimensional")
    if peaks.ndim != 1:
        raise ValueError("r_peaks must be one-dimensional")
    if fs <= 0:
        raise ValueError("Sampling frequency must be positive")
    if signal_array.size == 0 or peaks.size == 0:
        return {
            "r_wave_amplitudes": np.asarray([], dtype=float),
            "average_r_wave_amplitude": float("nan"),
            "qrs_durations_ms": np.asarray([], dtype=float),
            "estimated_qrs_duration_ms": float("nan"),
            "beat_count": int(peaks.size),
        }

    valid_peaks = peaks[(peaks >= 0) & (peaks < signal_array.size)]
    r_wave_amplitudes = signal_array[valid_peaks]

    qrs_durations = np.asarray([], dtype=float)
    if nk is not None:
        try:
            qrs_durations = _estimate_qrs_duration_neurokit(signal_array, valid_peaks, fs)
        except Exception:
            qrs_durations = np.asarray([], dtype=float)

    if qrs_durations.size == 0:
        qrs_durations = _estimate_qrs_duration_fallback(signal_array, valid_peaks, fs)

    average_duration = float(np.nanmean(qrs_durations)) if qrs_durations.size else float("nan")

    return {
        "r_wave_amplitudes": r_wave_amplitudes,
        "average_r_wave_amplitude": float(np.nanmean(r_wave_amplitudes)),
        "qrs_durations_ms": qrs_durations,
        "estimated_qrs_duration_ms": average_duration,
        "beat_count": int(valid_peaks.size),
    }
