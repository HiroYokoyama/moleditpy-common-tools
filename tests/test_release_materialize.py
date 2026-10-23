import importlib.util
import json
import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / (name + ".py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load("release_common")
materialize = load("materialize_shared")
zenodo = load("update_zenodo")


def fixture_package(tmp_path):
    package = tmp_path / "plugin"
    package.mkdir()
    (package / "__init__.py").write_text('PLUGIN_VERSION = "1.2.3"\n')
    (package / "settings.json").write_text('{"private":"test"}')
    for name in ("README.md", "LICENSE", "COPYING", "LICENSING.md"):
        (tmp_path / name).write_text(name)
    return {
        "source": "plugin/__init__.py",
        "package": "plugin",
        "archive": "plugin_{version}.zip",
    }


def test_package_is_reproducible_includes_notices_and_excludes_settings(tmp_path):
    config = fixture_package(tmp_path)
    first = release.package(tmp_path, config, "1.2.3").read_bytes()
    second = release.package(tmp_path, config, "1.2.3").read_bytes()
    assert first == second
    with zipfile.ZipFile(tmp_path / "plugin_1.2.3.zip") as archive:
        assert set(archive.namelist()) == {
            "plugin/__init__.py",
            "plugin/README.md",
            "plugin/LICENSE",
            "plugin/COPYING",
            "plugin/LICENSING.md",
        }


@pytest.mark.parametrize("version", ["1.2.4", "x;bad", "../1.2.3"])
def test_version_mismatch_or_invalid_input_rejected(tmp_path, version):
    config = fixture_package(tmp_path)
    with pytest.raises(ValueError):
        release.package(tmp_path, config, version)
    assert not list(tmp_path.glob("*.zip"))


def test_publishing_requires_all_assets_and_matching_source_before_any_gh_call(
    tmp_path,
):
    config = fixture_package(tmp_path)
    config.update(title="Plugin", assets=["missing.zip"])
    with patch.object(release.subprocess, "run") as command:
        with pytest.raises(FileNotFoundError):
            release.publish(tmp_path, config, "1.2.3")
        command.assert_not_called()


def test_materialize_only_configured_files_from_pinned_submodule(tmp_path):
    (tmp_path / "scripts").mkdir()
    source = tmp_path / "_periodic_shared/periodic_shared"
    source.mkdir(parents=True)
    (source / "cell_model.py").write_text("shared = 1\n")
    (tmp_path / "plugin").mkdir()
    config = {"package": "plugin", "files": ["cell_model.py"]}
    (tmp_path / "scripts/materialize-config.json").write_text(json.dumps(config))
    materialize.materialize(tmp_path)
    assert (tmp_path / "plugin/cell_model.py").read_bytes() == (
        source / "cell_model.py"
    ).read_bytes()
    config["files"] = ["../escape.py"]
    (tmp_path / "scripts/materialize-config.json").write_text(json.dumps(config))
    with pytest.raises(ValueError):
        materialize.materialize(tmp_path)


@pytest.mark.parametrize(
    "config",
    [
        {"deposition_id": "123", "sandbox_deposition_id": "456"},
        {"deposition_id": "123"},
        {},
    ],
)
def test_zenodo_repository_configuration(tmp_path, config):
    path = tmp_path / "zenodo-config.json"
    path.write_text(json.dumps(config))
    assert zenodo.load_config(path) == config


@pytest.mark.parametrize(
    "config", [["123"], {"deposition_id": 123}, {"sandbox_deposition_id": "not-an-id"}]
)
def test_zenodo_invalid_configuration_rejected(tmp_path, config):
    path = tmp_path / "zenodo-config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError):
        zenodo.load_config(path)
