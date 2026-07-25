"""Utilities for loading ECG records and annotations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import wfdb


def _record_base_path(dataset_path: str | Path, record_id: str) -> Path:
    """Return the base path used by WFDB for a record."""

    base_path = Path(dataset_path).expanduser().resolve() / str(record_id).strip()
    if not base_path.parent.exists():
        raise FileNotFoundError(f"Dataset path does not exist: {base_path.parent}")
    return base_path


def load_record(record_id: str, dataset_path: str | Path) -> tuple[np.ndarray, float, dict[str, Any]]:
    """Load an ECG record from the MIT-BIH database.

    Args:
        record_id: MIT-BIH record identifier, for example ``"100"``.
        dataset_path: Path to the downloaded dataset root.

    Returns:
        A tuple containing the ECG signal, sampling frequency, and metadata.

    Raises:
        FileNotFoundError: If the requested record is missing.
        ValueError: If the record does not contain usable signal data.
    """

    base_path = _record_base_path(dataset_path, record_id)
    try:
        record = wfdb.rdrecord(str(base_path))
    except Exception as exc:
        raise FileNotFoundError(f"Unable to load record {record_id} from {base_path}") from exc

    if record.p_signal is None and record.d_signal is None:
        raise ValueError(f"Record {record_id} does not contain a signal")

    signal_matrix = record.p_signal if record.p_signal is not None else record.d_signal
    signal_array = np.asarray(signal_matrix, dtype=float)
    if signal_array.ndim == 1:
        primary_signal = signal_array
    else:
        primary_signal = signal_array[:, 0]

    metadata: dict[str, Any] = {
        "record_name": record.record_name,
        "n_sig": record.n_sig,
        "sig_len": record.sig_len,
        "units": record.units,
        "channel_names": record.sig_name,
        "comments": record.comments,
        "base_datetime": record.base_datetime,
        "selected_channel": 0,
        "signal_shape": tuple(signal_array.shape),
    }
    return primary_signal.astype(float, copy=False), float(record.fs), metadata


def load_annotations(record_id: str, dataset_path: str | Path) -> tuple[np.ndarray, list[str]]:
    """Load the expert annotations for a record.

    Args:
        record_id: MIT-BIH record identifier.
        dataset_path: Path to the downloaded dataset root.

    Returns:
        A tuple containing annotation sample indices and annotation labels.

    Raises:
        FileNotFoundError: If the requested annotations are missing.
    """

    base_path = _record_base_path(dataset_path, record_id)
    try:
        annotation = wfdb.rdann(str(base_path), "atr")
    except Exception as exc:
        raise FileNotFoundError(
            f"Unable to load annotations for record {record_id} from {base_path}"
        ) from exc

    return np.asarray(annotation.sample, dtype=int), list(annotation.symbol)
