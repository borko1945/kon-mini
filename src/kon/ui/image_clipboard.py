from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageGrab

_CLIPBOARD_IMAGE_DIR = Path("/tmp/kon-clipboard")


def grab_clipboard_file() -> tuple[Path, bool] | None:
    """Return the first file referenced by the clipboard, saving image data as a PNG."""
    clipboard = ImageGrab.grabclipboard()
    if isinstance(clipboard, list):
        for item in clipboard:
            path = Path(item)
            if path.is_file():
                return path, False
        return None
    if not isinstance(clipboard, Image.Image):
        return None

    _CLIPBOARD_IMAGE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = _CLIPBOARD_IMAGE_DIR / f"clipboard-{os.getpid()}-{uuid4().hex[:8]}.png"
    clipboard.save(path, format="PNG")
    return path, True


def read_clipboard_text() -> str | None:
    """Return system clipboard text, or None when unavailable."""
    if sys.platform == "darwin":
        commands: list[list[str]] = [["pbpaste"]]
    elif sys.platform == "win32":
        commands = [["powershell", "-NoProfile", "-Command", "Get-Clipboard"]]
    else:
        commands = [
            ["wl-paste", "--no-newline"],
            ["xclip", "-selection", "clipboard", "-o"],
            ["xsel", "--clipboard", "--output"],
        ]
    for command in commands:
        if shutil.which(command[0]) is None:
            continue
        try:
            result = subprocess.run(command, capture_output=True, check=False, timeout=2)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode == 0:
            text = result.stdout.decode("utf-8", errors="replace").rstrip("\r\n")
            return text or None
    return None
