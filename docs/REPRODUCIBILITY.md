# Reproducibility notes

Stage 1 uses `configs/project.yml` as the checked-in baseline configuration and supports optional environment overrides documented in `.env.example`.

The repository intentionally ignores all raw and derived data directories. Later stages must add a data manifest containing source URLs, release versions, retrieval dates, permitted checksums, and the exact cohort configuration. Tests must continue to use only synthetic fixtures.
