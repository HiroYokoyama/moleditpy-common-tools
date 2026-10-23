import ast
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("path", sorted((ROOT / "scripts").glob("*.py")))
def test_scripts_parse_as_python39(path):
    ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 9))


@pytest.mark.parametrize("name", ["update_zenodo.py", "release_common.py"])
def test_script_cli_help(name):
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / name), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
