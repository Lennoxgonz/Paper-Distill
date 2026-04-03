"""Project paths shared across pages."""

from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAPERS_DIR = _PROJECT_ROOT / "data" / "papers"


def ensure_papers_dir() -> Path:
    """Ensure the downloaded-PDF directory exists and return it."""
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    return PAPERS_DIR
