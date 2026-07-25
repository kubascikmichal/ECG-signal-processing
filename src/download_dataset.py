"""Download the MIT-BIH Arrhythmia Database from PhysioNet."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import wfdb

LOGGER = logging.getLogger(__name__)
DEFAULT_OUTPUT_DIR = Path("data") / "mitdb"


def download_mitdb(output_dir: str | Path) -> Path:
    """Download the MIT-BIH Arrhythmia Database into ``output_dir``.

    Args:
        output_dir: Destination directory for the dataset.

    Returns:
        The resolved output directory containing the downloaded records.

    Raises:
        RuntimeError: If the download fails.
    """

    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Downloading MIT-BIH Arrhythmia Database into %s", target_dir)
    try:
        wfdb.dl_database("mitdb", dl_dir=str(target_dir), keep_subdirs=True)
    except Exception as exc:  # pragma: no cover - network and upstream dependent.
        raise RuntimeError(
            f"Failed to download MIT-BIH Arrhythmia Database into {target_dir}"
        ) from exc

    LOGGER.info("Dataset download complete")
    return target_dir


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="Download the MIT-BIH Arrhythmia Database from PhysioNet.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Destination directory for the downloaded records.",
    )
    return parser


def main() -> None:
    """Entry point for ``python -m src.download_dataset``."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    parser = build_argument_parser()
    args = parser.parse_args()
    download_mitdb(args.output_dir)


if __name__ == "__main__":
    main()
