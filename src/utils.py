import re
import hashlib
from datetime import datetime
from pathlib import Path


def sanitize_filename(title: str, max_length: int = 50) -> str:
    cleaned = re.sub(r'[\\/:*?"<>|]', '', title).strip()
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    return cleaned or "untitled"


def generate_today_path(base_dir: str = "output") -> Path:
    today_str = datetime.now().strftime("%Y-%m-%d")
    path = Path(base_dir) / today_str
    path.mkdir(parents=True, exist_ok=True)
    return path


def normalize_title(title: str) -> str:
    cleaned = re.sub(r'[\s#\u200b]+', '', title).lower()
    cleaned = re.sub(r'[^\w\u4e00-\u9fff]', '', cleaned)
    return cleaned
