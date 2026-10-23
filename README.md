# MoleditPy Common Tools

Version **1.0.0**. Canonical development and release scripts for the MoleditPy ecosystem.
These tools are copied into consumer repositories; installed plugins require no new dependency.

- `scripts/plugin_api_checker.py`: standalone API scanning engine, version 1.1.3. It retains Python 3.9 support without breaking existing importlib loaders.
- `scripts/check_api.py`: registry-aware collection runner that imports that engine.
- `scripts/update_zenodo.py`: native RDM metadata, version history, checksums and draft recovery. Consumer `scripts/zenodo-config.json` supplies published record IDs. Sandbox uses a separate configured ID or explicit CLI override.
- `scripts/release_common.py`: source-version validation, deterministic plugin ZIPs, GitHub publication and registry notification. Consumer `scripts/release-config.json` retains its package layout, license notices and assets.
- `scripts/materialize_shared.py`: copies configured modules from the consumer's pinned periodic submodule. Consumer `scripts/materialize-config.json` specifies package and filenames.

## Version and distribution policy

Use SemVer in `VERSION`: patch for compatible fixes, minor for compatible new capabilities, major for breaking CLI/configuration changes. Never silently update consumer code from `main`.

After the common-tools CI passes, check out its tested commit and run:

```bash
python tools/sync_consumers.py --workspace /path/to/DEV_MAIN --write
```

`--repo NAME` limits the selection. Without `--write`, the command reports drift and exits nonzero when updates are needed. `consumers.json` declares copied files and public repository configuration. Each consumer receives `scripts/common-tools.lock.json` with the tool version, immutable source commit and SHA-256 of LF-normalized script contents. Commit those copies and configuration together; do not edit vendored scripts independently. The template repository receives the same versioned copies.

Keep all common-engine unit tests here. Consumer repositories retain their own API compatibility/integration checks, not duplicate tests of the engine or mocked Zenodo service. CI runs once on Python 3.9 / Ubuntu 24.04 when tool code, tests or CI changes; it never contacts Zenodo or creates releases. Local formatting and tests:

```bash
ruff check .
ruff format --check .
python -m pytest tests -q
```

Native Rust builds, main-application wheels/executables, Job Server bundles and collection registry/archive orchestration remain repository-specific. PMEFF retains its independent PyPI build/publish jobs. Ordinary plugin version verification, packaging, publication and registry notification use the common helper.

## Licensing

First-party code is LGPL-3.0-or-later, inherited from its originating MoleditPy repositories. See `LICENSE` and `COPYING`. Copyright Hiromichi Yokoyama / HiroYokoyama and the original contributors. Preserve existing notices; third-party code and data retain their own terms.
