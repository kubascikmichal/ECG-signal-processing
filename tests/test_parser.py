"""Tests for ECG record and annotation parsing."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from src import ecg_parser


@dataclass
class DummyRecord:
    """Minimal WFDB-like record stub."""

    record_name: str = "100"
    p_signal: np.ndarray | None = field(
        default_factory=lambda: np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])
    )
    d_signal: np.ndarray | None = None
    fs: float = 360.0
    n_sig: int = 2
    sig_len: int = 3
    units: list[str] | None = field(default=None)
    sig_name: list[str] | None = field(default=None)
    comments: list[str] | None = field(default=None)
    base_datetime: None = None

    def __post_init__(self) -> None:
        if self.units is None:
            self.units = ["mV", "mV"]
        if self.sig_name is None:
            self.sig_name = ["MLII", "V5"]
        if self.comments is None:
            self.comments = []


@dataclass
class DummyAnnotation:
    """Minimal WFDB-like annotation stub."""

    sample: np.ndarray = field(default_factory=lambda: np.array([1, 2, 3]))
    symbol: list[str] | None = field(default=None)

    def __post_init__(self) -> None:
        if self.symbol is None:
            self.symbol = ["N", "N", "V"]


def test_load_record_returns_signal_and_metadata(monkeypatch) -> None:
    """load_record should return a one-dimensional signal and metadata."""

    monkeypatch.setattr(ecg_parser.wfdb, "rdrecord", lambda path: DummyRecord())

    signal, fs, metadata = ecg_parser.load_record("100", "data/mitdb")

    assert signal.shape == (3,)
    assert fs == 360.0
    assert metadata["record_name"] == "100"
    assert metadata["signal_shape"] == (3, 2)


def test_load_annotations_returns_samples_and_labels(monkeypatch) -> None:
    """load_annotations should return samples and labels as arrays/lists."""

    monkeypatch.setattr(ecg_parser.wfdb, "rdann", lambda path, extension: DummyAnnotation())

    samples, labels = ecg_parser.load_annotations("100", "data/mitdb")

    assert np.array_equal(samples, np.array([1, 2, 3]))
    assert labels == ["N", "N", "V"]
