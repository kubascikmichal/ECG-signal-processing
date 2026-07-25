"""Visualization helpers for ECG analysis outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

DEFAULT_FIGURE_DIR = Path("outputs") / "figures"


def _prepare_output_path(output_dir: str | Path, filename: str) -> Path:
    """Create an output path for a figure."""

    directory = Path(output_dir).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    return directory / filename


def _time_axis(signal: np.ndarray, fs: float) -> np.ndarray:
    """Generate a time axis in seconds for an ECG signal."""

    return np.arange(signal.size, dtype=float) / float(fs)


def _plot_ecg(
    signal: np.ndarray | list[float],
    fs: float,
    title: str,
    output_path: Path,
    r_peaks: np.ndarray | None = None,
) -> Path:
    """Shared plotting logic for ECG traces."""

    signal_array = np.asarray(signal, dtype=float)
    time_axis = _time_axis(signal_array, fs)

    figure, axis = plt.subplots(figsize=(16, 4))
    axis.plot(time_axis, signal_array, linewidth=1.0, color="#1f77b4")
    if r_peaks is not None and np.asarray(r_peaks).size:
        peak_indices = np.asarray(r_peaks, dtype=int)
        peak_indices = peak_indices[(peak_indices >= 0) & (peak_indices < signal_array.size)]
        axis.scatter(
            time_axis[peak_indices],
            signal_array[peak_indices],
            color="#d62728",
            s=18,
            label="R-peaks",
            zorder=3,
        )
        axis.legend(loc="upper right")

    axis.set_title(title)
    axis.set_xlabel("Time (s)")
    axis.set_ylabel("Amplitude")
    axis.grid(True, alpha=0.25)
    figure.tight_layout()
    figure.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(figure)
    return output_path


def plot_raw_ecg(signal: np.ndarray | list[float], fs: float, output_dir: str | Path = DEFAULT_FIGURE_DIR, record_id: str = "record") -> Path:
    """Plot the raw ECG signal and save it as a PNG."""

    output_path = _prepare_output_path(output_dir, f"{record_id}_raw_ecg.png")
    return _plot_ecg(signal, fs, f"Raw ECG - Record {record_id}", output_path)


def plot_filtered_ecg(signal: np.ndarray | list[float], fs: float, output_dir: str | Path = DEFAULT_FIGURE_DIR, record_id: str = "record") -> Path:
    """Plot the filtered ECG signal and save it as a PNG."""

    output_path = _prepare_output_path(output_dir, f"{record_id}_filtered_ecg.png")
    return _plot_ecg(signal, fs, f"Filtered ECG - Record {record_id}", output_path)


def plot_r_peaks(
    signal: np.ndarray | list[float],
    r_peaks: np.ndarray | list[int],
    fs: float,
    output_dir: str | Path = DEFAULT_FIGURE_DIR,
    record_id: str = "record",
) -> Path:
    """Plot ECG signal with R-peaks marked and save it as a PNG."""

    output_path = _prepare_output_path(output_dir, f"{record_id}_r_peaks.png")
    return _plot_ecg(signal, fs, f"R-Peak Detection - Record {record_id}", output_path, r_peaks=np.asarray(r_peaks))
