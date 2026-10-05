from pathlib import Path
import tempfile

import pytest


@pytest.fixture
def tmp_path() -> Path:
    base_dir = Path(__file__).resolve().parent / ".tmp"
    base_dir.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(dir=base_dir))
