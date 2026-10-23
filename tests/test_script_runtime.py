import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_checker_supports_consumer_importlib_loader():
    spec = importlib.util.spec_from_file_location(
        "checker_probe", ROOT / "scripts/plugin_api_checker.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.Issue("x.py", 1, "CODE", "message").line == 1
    assert module.APIInfo().mw_members == {}


@pytest.mark.parametrize("path", sorted((ROOT / "scripts").glob("*.py")))
def test_scripts_parse_as_python39(path):
    ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 9))


@pytest.mark.parametrize(
    "name", ["plugin_api_checker.py", "update_zenodo.py", "release_common.py"]
)
def test_script_cli_help(name):
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / name), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
