import json
import os
from pathlib import Path
from typing import Any, Dict
 
APP_DIR_NAME = "ScribbleThoughts"
DATA_FILE_NAME = "todo_book_data.json"


def get_data_dir() -> Path:
    """Return directory to store app data.
    - On Windows: %APPDATA%\ScribbleThoughts
    - Else: ~/.config/ScribbleThoughts
    Ensures the directory exists.
    """
    appdata = os.getenv("APPDATA")
    if appdata:
        base = Path(appdata)
    else:
        # Fallback for non-Windows or missing APPDATA
        base = Path.home() / ".config"
    target = base / APP_DIR_NAME
    target.mkdir(parents=True, exist_ok=True)
    return target


def get_data_path() -> Path:
    """Full path to the JSON state file."""
    return get_data_dir() / DATA_FILE_NAME


def load_state() -> Dict[str, Any]:
    """Load JSON state from data path. Returns empty dict if file missing.
    Raises ValueError on decode errors so caller can handle.
    """
    path = get_data_path()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Corrupt JSON at {path}: {e}") from e


def save_state(data: Dict[str, Any]) -> None:
    """Write JSON state to data path with indentation."""
    path = get_data_path()
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
