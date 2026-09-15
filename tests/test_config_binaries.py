from importlib import import_module
from pathlib import Path

import pytest

from kon import AVAILABLE_BINARIES, config
from kon.config import _detect_available_binaries

config_module = import_module("kon.config")


def test_available_binaries_is_set():
    assert isinstance(AVAILABLE_BINARIES, set)


def test_available_binaries_contains_valid_entries():
    valid_binaries = {"rg", "fd", "gh"}
    assert AVAILABLE_BINARIES.issubset(valid_binaries)


def test_config_binaries_property():
    binaries_config = config.binaries
    assert hasattr(binaries_config, "has")
    assert hasattr(binaries_config, "rg")
    assert hasattr(binaries_config, "fd")
    assert hasattr(binaries_config, "gh")


def test_config_binaries_has_method():
    # Test with a known available binary
    if "rg" in AVAILABLE_BINARIES:
        assert config.binaries.has("rg") is True

    # Test with a nonexistent binary
    assert config.binaries.has("nonexistent_binary") is False


def test_config_binaries_properties():
    # The properties should match the AVAILABLE_BINARIES set
    assert config.binaries.rg == ("rg" in AVAILABLE_BINARIES)
    assert config.binaries.fd == ("fd" in AVAILABLE_BINARIES)
    assert config.binaries.gh == ("gh" in AVAILABLE_BINARIES)


def test_detect_available_binaries_with_kon_fd_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    env_fd = tmp_path / "env_fd"
    env_fd.write_text("", encoding="utf-8")

    monkeypatch.setenv("KON_FD_PATH", str(env_fd))
    monkeypatch.delenv("KON_RG_PATH", raising=False)

    available = _detect_available_binaries()
    assert "fd" in available


def test_detect_available_binaries_with_kon_rg_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    env_rg = tmp_path / "env_rg"
    env_rg.write_text("", encoding="utf-8")

    monkeypatch.setenv("KON_RG_PATH", str(env_rg))
    monkeypatch.delenv("KON_FD_PATH", raising=False)

    available = _detect_available_binaries()
    assert "rg" in available


def test_detect_available_binaries_env_var_overrides_missing_system(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    env_fd = tmp_path / "env_fd"
    env_fd.write_text("", encoding="utf-8")

    def fake_which(command: str) -> str | None:
        return None

    monkeypatch.setenv("KON_FD_PATH", str(env_fd))
    monkeypatch.setattr(config_module.shutil, "which", fake_which)

    available = _detect_available_binaries()
    assert "fd" in available


def test_detect_available_binaries_env_var_ignored_if_nonexistent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    local_fd = bin_dir / "fd"
    local_fd.write_text("", encoding="utf-8")

    monkeypatch.setenv("KON_FD_PATH", "/nonexistent/path/to/fd")
    monkeypatch.setattr(config_module, "get_config_dir", lambda: tmp_path)

    available = _detect_available_binaries()
    assert "fd" in available  # Falls back to local bin dir
