import re

from kon.version import COMMIT, DISPLAY_VERSION, VERSION


def test_display_version_includes_commit_in_repo() -> None:
    # Tests run inside the kon checkout, so a commit hash must be available.
    assert COMMIT is not None
    assert re.fullmatch(r"[0-9a-f]{7,}", COMMIT)


def test_display_version_format() -> None:
    assert f"{VERSION} ({COMMIT})" == DISPLAY_VERSION
