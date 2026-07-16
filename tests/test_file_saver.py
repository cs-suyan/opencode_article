from src.file_saver import FileSaver
import tempfile


def test_already_exists():
    with tempfile.TemporaryDirectory() as tmp:
        saver = FileSaver(base_dir=tmp)
        assert not saver.already_exists("测试标题")
        saver.mark_generated("测试标题")
        assert saver.already_exists("测试标题")


def test_save():
    with tempfile.TemporaryDirectory() as tmp:
        saver = FileSaver(base_dir=tmp)
        path = saver.save("# Test Content", "TestTitle")
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert content == "# Test Content"
