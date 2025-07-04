from pathlib import Path
import sys

# Ensure the parent directory (project root) is in the path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import Config, config  # type: ignore

__all__ = ["Config", "config"]
