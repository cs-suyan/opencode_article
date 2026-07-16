from src.utils import sanitize_filename, normalize_title, generate_today_path
from pathlib import Path
import tempfile


def test_sanitize_filename():
    assert sanitize_filename("hello/world:test") == "helloworldtest"
    assert sanitize_filename("abc") == "abc"
    assert sanitize_filename("") == "untitled"


def test_normalize_title():
    assert normalize_title("Hello World") == "helloworld"
    assert normalize_title("  ") == ""


def test_generate_today_path():
    with tempfile.TemporaryDirectory() as tmp:
        path = generate_today_path(tmp)
        assert path.exists()
        assert path.name.startswith("20")
