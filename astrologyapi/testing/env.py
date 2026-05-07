"""Environment loading for the reusable QA runners."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .paths import ROOT_DIR, ensure_output_dirs


def load_dotenv(path: Path | None = None) -> None:
    """Load a simple `.env` file without introducing a new dependency."""
    env_path = path or (ROOT_DIR / ".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass
class QAConfig:
    """Runtime configuration shared by all QA entrypoints."""

    api_key: str
    timeout: float = 30.0
    retries: int = 0

    @classmethod
    def from_env(cls) -> "QAConfig":
        """Load QA config from process env or the local `.env` file."""
        load_dotenv()
        ensure_output_dirs()

        api_key = os.getenv("ASTROLOGYAPI_API_KEY")
        if not api_key:
            raise ValueError(
                "ASTROLOGYAPI_API_KEY is required to run live QA. "
                "Set it in the environment or in .env."
            )

        timeout = float(os.getenv("ASTROLOGYAPI_QA_TIMEOUT", "30"))
        retries = int(os.getenv("ASTROLOGYAPI_QA_RETRIES", "0"))
        return cls(api_key=api_key, timeout=timeout, retries=retries)
