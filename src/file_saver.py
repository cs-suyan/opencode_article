import json
from pathlib import Path
from src.utils import sanitize_filename, generate_today_path, normalize_title


class FileSaver:
    def __init__(self, base_dir: str = "output"):
        self.base_dir = base_dir

    def _registry_path(self) -> Path:
        return generate_today_path(self.base_dir) / ".registry.json"

    def _load_registry(self) -> set:
        path = self._registry_path()
        if path.exists():
            return set(json.loads(path.read_text(encoding="utf-8")))
        return set()

    def _save_registry(self, titles: set):
        path = self._registry_path()
        path.write_text(json.dumps(sorted(titles), ensure_ascii=False), encoding="utf-8")

    def already_exists(self, title: str) -> bool:
        key = normalize_title(title)
        if not key:
            return False
        return key in self._load_registry()

    def mark_generated(self, title: str):
        key = normalize_title(title)
        if not key:
            return
        reg = self._load_registry()
        reg.add(key)
        self._save_registry(reg)

    def save(self, content: str, filename: str) -> Path:
        today_path = generate_today_path(self.base_dir)
        safe_name = sanitize_filename(filename)
        filepath = today_path / f"{safe_name}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath
