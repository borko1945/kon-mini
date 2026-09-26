import subprocess
import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _get_package_name() -> str:
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    if pyproject_path.exists():
        try:
            data = tomllib.loads(pyproject_path.read_text())
            return data["project"]["name"]
        except Exception:
            pass
    return "kon-coding-agent"


PACKAGE_NAME = _get_package_name()

try:
    VERSION = version(PACKAGE_NAME)
except PackageNotFoundError:
    VERSION = "0.4.3"


def _get_commit() -> str | None:
    """Return the short commit hash of the checkout this package runs from, if any."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode == 0:
        return result.stdout.strip() or None
    return None


COMMIT = _get_commit()
DISPLAY_VERSION = f"{VERSION} ({COMMIT})" if COMMIT else VERSION
