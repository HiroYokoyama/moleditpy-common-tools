# Changelog

## 1.0.0

- Establish versioned canonical Zenodo, plugin release and materialization tools with pinned consumer provenance.
- Move common engine tests into one lightweight CI job instead of repeating them in consumers.
- Preserve Zenodo native metadata, DOI, checksums, existing record IDs and same-family unassigned-draft recovery.
- Separate repository configuration from common code; keep native/platform-specific release build steps local.
