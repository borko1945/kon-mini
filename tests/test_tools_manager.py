import zipfile
from pathlib import Path

import pytest

from kon.tools_manager import _extract_binary, get_tool_path


def test_extract_binary_rejects_zip_path_traversal(tmp_path: Path):
    archive = tmp_path / "malicious.zip"
    dest = tmp_path / "dest"
    dest.mkdir()

    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("../../evil.txt", "pwned")

    with pytest.raises(ValueError, match="escapes target directory"):
        _extract_binary(archive, "evil.txt", dest)


def test_get_tool_path_returns_config_bin_fd(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fd_path = bin_dir / "fd"
    fd_path.write_text("", encoding="utf-8")

    monkeypatch.setattr("kon.tools_manager._BIN_DIR", bin_dir)
    monkeypatch.setattr("kon.tools_manager._get_platform", lambda: "linux")

    assert get_tool_path("fd") == str(fd_path)


def test_get_tool_path_supports_system_fdfind(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setattr("kon.tools_manager._BIN_DIR", tmp_path / "missing")

    def fake_which(command: str) -> str | None:
        if command == "fdfind":
            return "/usr/bin/fdfind"
        return None

    monkeypatch.setattr("kon.tools_manager.shutil.which", fake_which)

    assert get_tool_path("fd") == "/usr/bin/fdfind"


def test_get_tool_path_prefers_env_var_over_bin_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    local_fd = bin_dir / "fd"
    local_fd.write_text("", encoding="utf-8")

    env_fd = tmp_path / "env_fd"
    env_fd.write_text("", encoding="utf-8")

    monkeypatch.setattr("kon.tools_manager._BIN_DIR", bin_dir)
    monkeypatch.setattr("kon.tools_manager._get_platform", lambda: "linux")
    monkeypatch.setenv("KON_FD_PATH", str(env_fd))

    assert get_tool_path("fd") == str(env_fd)


def test_get_tool_path_prefers_env_var_over_system_which(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    env_fd = tmp_path / "env_fd"
    env_fd.write_text("", encoding="utf-8")

    def fake_which(command: str) -> str | None:
        if command == "fdfind":
            return "/usr/bin/fdfind"
        return None

    monkeypatch.setenv("KON_FD_PATH", str(env_fd))
    monkeypatch.setattr("kon.tools_manager.shutil.which", fake_which)

    assert get_tool_path("fd") == str(env_fd)


def test_get_tool_path_env_var_ignored_if_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fd_path = bin_dir / "fd"
    fd_path.write_text("", encoding="utf-8")

    monkeypatch.delenv("KON_FD_PATH", raising=False)
    monkeypatch.setattr("kon.tools_manager._BIN_DIR", bin_dir)
    monkeypatch.setattr("kon.tools_manager._get_platform", lambda: "linux")

    assert get_tool_path("fd") == str(fd_path)


def test_get_tool_path_env_var_ignored_if_nonexistent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fd_path = bin_dir / "fd"
    fd_path.write_text("", encoding="utf-8")

    monkeypatch.setenv("KON_FD_PATH", "/nonexistent/path/to/fd")
    monkeypatch.setattr("kon.tools_manager._BIN_DIR", bin_dir)
    monkeypatch.setattr("kon.tools_manager._get_platform", lambda: "linux")

    assert get_tool_path("fd") == str(fd_path)


def test_get_tool_path_rg_env_var(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    env_rg = tmp_path / "env_rg"
    env_rg.write_text("", encoding="utf-8")

    monkeypatch.setenv("KON_RG_PATH", str(env_rg))
    monkeypatch.setattr("kon.tools_manager._get_platform", lambda: "linux")

    assert get_tool_path("rg") == str(env_rg)
