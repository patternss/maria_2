from __future__ import annotations

import sys


def pytest_configure() -> None:
    # Ensure `import app.*` works when running pytest from different CWDs.
    backend_root = "/Users/home/omat/maria_2/backend"
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)
