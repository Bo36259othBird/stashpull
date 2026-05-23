"""User configuration loading and defaults for stashpull."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_DEFAULT_CONFIG: dict[str, Any] = {
    "max_history_entries": 50,
    "default_export_dir": ".",
    "colour": True,
    "preview_context_lines": 3,
    "default_restore_mode": "apply",
    "date_format": "%Y-%m-%d %H:%M",
}


def _config_path() -> Path:
    """Return the path to the user config file."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME", "")
    base = Path(xdg_config) if xdg_config else Path.home() / ".config"
    return base / "stashpull" / "config.json"


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Load config from *path* (or the default location), merging with defaults.

    Unknown keys in the file are ignored; missing keys fall back to defaults.
    """
    config = dict(_DEFAULT_CONFIG)
    target = path or _config_path()
    if not target.exists():
        return config
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            for key in _DEFAULT_CONFIG:
                if key in raw:
                    config[key] = raw[key]
    except (json.JSONDecodeError, OSError):
        pass
    return config


def save_config(config: dict[str, Any], path: Path | None = None) -> None:
    """Persist *config* to *path* (or the default location)."""
    target = path or _config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(config, indent=2), encoding="utf-8")


def get(key: str, path: Path | None = None) -> Any:
    """Convenience helper – return a single config value by *key*."""
    return load_config(path).get(key, _DEFAULT_CONFIG.get(key))
