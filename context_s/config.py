"""Configuration utilities for ContextS."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

CONFIG_DIR_ENV = "CONTEXT_S_HOME"
DEFAULT_CONFIG_DIR_NAME = ".context-s"
CONFIG_FILE_NAME = "config.json"
CONTEXT7_KEY_FIELD = "context7_api_key"


def get_config_dir() -> Path:
    """Return the directory where ContextS stores configuration."""
    override = os.getenv(CONFIG_DIR_ENV)
    if override:
        return Path(override).expanduser()
    return Path.home() / DEFAULT_CONFIG_DIR_NAME


def get_config_path() -> Path:
    """Return the full path to the configuration file."""
    return get_config_dir() / CONFIG_FILE_NAME


def load_config() -> Dict[str, Any]:
    """Load the ContextS configuration file if it exists."""
    path = get_config_path()
    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return {}

    if not isinstance(data, dict):
        return {}
    return data


def save_config(data: Dict[str, Any]) -> Path:
    """Persist configuration data to disk.

    Returns:
        Path to the configuration file.
    """
    path = get_config_path()
    directory = path.parent
    directory.mkdir(parents=True, exist_ok=True)

    # Remove keys with falsy values to keep the file tidy
    cleaned: Dict[str, Any] = {key: value for key, value in data.items() if value}

    with path.open("w", encoding="utf-8") as handle:
        json.dump(cleaned, handle, indent=2, sort_keys=True)
        handle.write("\n")

    try:
        os.chmod(path, 0o600)
    except OSError:
        # Ignore permission errors on systems that do not support chmod
        pass

    return path


def delete_config_file() -> None:
    """Delete the configuration file if it exists."""
    path = get_config_path()
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def get_context7_api_key() -> Tuple[Optional[str], str]:
    """Return the configured Context7 API key and where it was sourced from."""
    env_key = os.getenv("CONTEXT7_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip(), "environment"

    config = load_config()
    config_key = config.get(CONTEXT7_KEY_FIELD)
    if isinstance(config_key, str) and config_key.strip():
        return config_key.strip(), "config"

    return None, "unset"


def set_context7_api_key(key: Optional[str]) -> Path | None:
    """Persist or remove the stored Context7 API key.

    Args:
        key: The API key to store. If ``None`` or empty, the key is removed.

    Returns:
        Path to the configuration file if it exists after the operation, otherwise ``None``.
    """
    cleaned_key = key.strip() if isinstance(key, str) else None
    if not cleaned_key:
        config = load_config()
        if CONTEXT7_KEY_FIELD in config:
            config.pop(CONTEXT7_KEY_FIELD, None)
            if config:
                return save_config(config)
            delete_config_file()
        return None

    config = load_config()
    config[CONTEXT7_KEY_FIELD] = cleaned_key
    return save_config(config)


def mask_secret(value: Optional[str], reveal: int = 4) -> str:
    """Mask a secret value, showing only the last ``reveal`` characters."""
    if not value:
        return "<not set>"

    trimmed = value.strip()
    if len(trimmed) <= reveal:
        return "*" * len(trimmed)

    hidden_length = max(len(trimmed) - reveal, 0)
    return f"{'*' * hidden_length}{trimmed[-reveal:]}"
