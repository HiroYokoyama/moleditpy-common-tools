# Changelog

## 1.0.0

- Establish versioned canonical API checker, Zenodo, plugin release and materialization tools with pinned consumer provenance.
- Move common engine tests into one lightweight CI job instead of repeating them in consumers.
- API checker 1.1.3: preserve Python 3.9 compatibility while supporting consumer importlib loaders without `sys.modules` registration.
- Preserve Zenodo native metadata, DOI, checksums, existing record IDs and same-family unassigned-draft recovery.
- Separate repository configuration from common code; keep native/platform-specific release build steps local.
