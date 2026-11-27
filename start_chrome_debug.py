"""Arranca o Chrome com remote debugging (Windows, macOS e Linux).

Equivalente ao antigo `start_chrome_debug.bat`, mas portátil. A lógica vive em
`data-pipeline/chrome_debug.py`, para ser partilhada com os scrapers.

Uso:
    python start_chrome_debug.py
    python start_chrome_debug.py --check
"""

from __future__ import annotations

import sys
from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parent / "data-pipeline"
if str(PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_ROOT))

from chrome_debug import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
