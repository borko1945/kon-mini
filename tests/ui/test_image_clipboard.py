from pathlib import Path

from PIL import Image

from kon.ui import image_clipboard


def test_grab_clipboard_file_writes_png_under_tmp(monkeypatch) -> None:
    monkeypatch.setattr(
        image_clipboard.ImageGrab, "grabclipboard", lambda: Image.new("RGB", (2, 2))
    )

    result = image_clipboard.grab_clipboard_file()

    assert result is not None
    path, temporary = result
    try:
        assert temporary is True
        assert path.parent == Path("/tmp/kon-clipboard")
        assert path.suffix == ".png"
        assert path.is_file()
    finally:
        path.unlink(missing_ok=True)


def test_grab_clipboard_file_returns_existing_file(monkeypatch, tmp_path) -> None:
    path = tmp_path / "image.png"
    path.write_bytes(b"image")
    monkeypatch.setattr(image_clipboard.ImageGrab, "grabclipboard", lambda: [str(path)])

    assert image_clipboard.grab_clipboard_file() == (path, False)


def test_grab_clipboard_file_returns_none_for_text(monkeypatch) -> None:
    monkeypatch.setattr(image_clipboard.ImageGrab, "grabclipboard", lambda: "just text")

    assert image_clipboard.grab_clipboard_file() is None
