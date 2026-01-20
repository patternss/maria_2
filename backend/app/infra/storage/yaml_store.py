from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import yaml


class YamlStore:
    """YAML persistence helper.

    Purpose:
        Centralize reading/writing YAML with atomic writes.

    Notes:
        - This is intentionally minimal. We can add file locking later if needed.
        - Callers should treat the file contents as the source of truth.
    """

    def __init__(self, data_dir: str | Path) -> None:
        self._data_dir = Path(data_dir)

    def path_for(self, filename: str) -> Path:
        """Return the absolute path to a data file under the data dir."""

        return self._data_dir / filename

    def read(self, filename: str, default: Any) -> Any:
        """Read YAML file and return parsed content.

        Args:
            filename: YAML filename under the data directory.
            default: Value returned if the file doesn't exist.

        Returns:
            Parsed YAML content.
        """

        path = self.path_for(filename)
        if not path.exists():
            return default

        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or default

    def write_atomic(self, filename: str, data: Any) -> None:
        """Write YAML file atomically.

        Atomic write strategy:
            Write to a temporary file in the same directory and then replace.

        Args:
            filename: YAML filename under the data directory.
            data: Data to serialize.

        Side effects:
            Creates directories as needed and writes files to disk.
        """

        self._data_dir.mkdir(parents=True, exist_ok=True)

        destination = self.path_for(filename)
        destination.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(destination.parent),
            delete=False,
        ) as tmp:
            yaml.safe_dump(data, tmp, sort_keys=False, allow_unicode=True)
            tmp_path = Path(tmp.name)

        os.replace(tmp_path, destination)
