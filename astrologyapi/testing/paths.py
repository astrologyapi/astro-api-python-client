"""Filesystem paths used by the reusable QA framework."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
TESTING_DIR = ROOT_DIR / "testing"
POSTMAN_DIR = TESTING_DIR / "postman"
TEST_DATA_DIR = TESTING_DIR / "test-data"
CATALOG_DIR = TESTING_DIR / "catalog"
RESULTS_DIR = TESTING_DIR / "results"


def ensure_output_dirs() -> None:
    """Create generated QA artifact directories when missing."""
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
