"""Run the full ECG analysis pipeline for a given MIT-BIH record."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.bpm_analysis import calculate_average_bpm, calculate_bpm, calculate_rr_intervals
from src.ecg_parser import load_annotations, load_record
from src.filters import bandpass_filter
from src.qrs_analysis import analyze_qrs
from src.rpeak_detection import detect_r_peaks
from src.visualization import plot_filtered_ecg, plot_raw_ecg, plot_r_peaks

LOGGER = logging.getLogger(__name__)
DEFAULT_DATASET_DIR = PROJECT_ROOT / "data" / "mitdb"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "figures"


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""

    parser = argparse.ArgumentParser(description="Run an end-to-end ECG analysis workflow.")
    parser.add_argument("--record", default="100", help="MIT-BIH record identifier to analyze.")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=DEFAULT_DATASET_DIR,
        help="Path to the downloaded MIT-BIH dataset root.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where figures should be saved.",
    )
    return parser


def _format_summary(record_id: str, fs: float, beat_count: int, average_bpm: float, mean_rr: float, mean_qrs_ms: float) -> str:
    """Format the printed analysis summary."""

    return (
        "------------------------------------------------\n"
        f"Record: {record_id}\n"
        f"Sampling frequency: {fs:.0f} Hz\n"
        f"Detected beats: {beat_count}\n"
        f"Average BPM: {average_bpm:.1f}\n"
        f"Mean RR interval: {mean_rr:.2f} s\n"
        f"Mean QRS duration: {mean_qrs_ms:.0f} ms\n"
        "------------------------------------------------"
    )


def run_analysis(record_id: str, dataset_dir: Path, output_dir: Path) -> dict[str, object]:
    """Execute the ECG analysis workflow and return a result dictionary."""

    signal, fs, metadata = load_record(record_id, dataset_dir)
    annotations, labels = load_annotations(record_id, dataset_dir)
    filtered_signal = bandpass_filter(signal, fs)
    r_peaks, peak_count = detect_r_peaks(filtered_signal, fs)
    rr_intervals = calculate_rr_intervals(r_peaks, fs)
    instantaneous_bpm = calculate_bpm(rr_intervals)
    average_bpm = calculate_average_bpm(rr_intervals)
    qrs_metrics = analyze_qrs(filtered_signal, r_peaks, fs)

    plot_raw_ecg(signal, fs, output_dir, record_id=record_id)
    plot_filtered_ecg(filtered_signal, fs, output_dir, record_id=record_id)
    plot_r_peaks(filtered_signal, r_peaks, fs, output_dir, record_id=record_id)

    result = {
        "record_id": record_id,
        "sampling_frequency": fs,
        "signal": signal,
        "filtered_signal": filtered_signal,
        "metadata": metadata,
        "annotations": annotations,
        "annotation_labels": labels,
        "r_peaks": r_peaks,
        "peak_count": peak_count,
        "rr_intervals": rr_intervals,
        "instantaneous_bpm": instantaneous_bpm,
        "average_bpm": average_bpm,
        "qrs_metrics": qrs_metrics,
    }
    LOGGER.info("%s", _format_summary(
        record_id,
        fs,
        peak_count,
        average_bpm,
        float(rr_intervals.mean()) if rr_intervals.size else float("nan"),
        float(qrs_metrics["estimated_qrs_duration_ms"]),
    ))
    return result


def main() -> None:
    """Command-line entry point."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    parser = build_argument_parser()
    args = parser.parse_args()

    result = run_analysis(args.record, args.dataset_dir, args.output_dir)
    print(
        _format_summary(
            str(result["record_id"]),
            float(result["sampling_frequency"]),
            int(result["peak_count"]),
            float(result["average_bpm"]),
            float(result["rr_intervals"].mean()) if result["rr_intervals"].size else float("nan"),
            float(result["qrs_metrics"]["estimated_qrs_duration_ms"]),
        )
    )


if __name__ == "__main__":
    main()
