"""Copy a clean, pinned common-tools checkout into sibling consumer repositories."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalized(data):
    return data.replace(b"\r\n", b"\n")


def revision():
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True
    )
    if dirty:
        raise RuntimeError(
            "Commit common-tools changes before synchronizing consumers."
        )
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def sync(workspace, name, config, commit, write=False):
    if Path(name).name != name:
        raise ValueError("Consumer name must be one repository directory.")
    target_root = workspace / name
    if not (target_root / ".git").exists():
        raise FileNotFoundError(target_root / ".git")
    lock = {
        "repository": "HiroYokoyama/moleditpy-common-tools",
        "version": (ROOT / "VERSION").read_text().strip(),
        "commit": commit,
        "files": {},
    }
    desired = {}
    for source_name, relative in config["files"].items():
        source = (ROOT / "scripts" / source_name).resolve()
        source.relative_to((ROOT / "scripts").resolve())
        target = (target_root / relative).resolve()
        target.relative_to(target_root.resolve())
        data = normalized(source.read_bytes())
        desired[target] = data
        lock["files"][relative] = {
            "source": "scripts/" + source_name,
            "sha256_lf": hashlib.sha256(data).hexdigest(),
        }
    for key in ("zenodo", "release", "materialize"):
        if key + "_config" in config:
            desired[target_root / "scripts" / (key + "-config.json")] = (
                json.dumps(config[key + "_config"], indent=2) + "\n"
            ).encode()
    desired[target_root / "scripts/common-tools.lock.json"] = (
        json.dumps(lock, indent=2) + "\n"
    ).encode()
    different = []
    for path, data in desired.items():
        current = path.read_bytes() if path.exists() else b""
        if normalized(current) != data:
            different.append(str(path.relative_to(target_root)))
            if write:
                path.parent.mkdir(parents=True, exist_ok=True)
                # The collection preserves existing file endings because it ships raw files.
                if name == "moleditpy-plugins" and b"\r\n" in current:
                    data = data.replace(b"\n", b"\r\n")
                path.write_bytes(data)
    return different


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=ROOT.parent)
    parser.add_argument(
        "--repo", action="append", help="Limit synchronization to these consumer names."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write updates; default only reports differences.",
    )
    args = parser.parse_args()
    commit = revision()
    consumers = json.loads((ROOT / "consumers.json").read_text(encoding="utf-8"))
    if args.repo and set(args.repo) - consumers.keys():
        parser.error("Unknown consumer repository")
    dirty = False
    for name, config in sorted(consumers.items()):
        if args.repo and name not in args.repo:
            continue
        differences = sync(args.workspace.resolve(), name, config, commit, args.write)
        print(name + ": " + (", ".join(differences) if differences else "current"))
        dirty |= bool(differences)
    return int(dirty and not args.write)


if __name__ == "__main__":
    raise SystemExit(main())
