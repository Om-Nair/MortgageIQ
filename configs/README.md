# Configuration

`project.yml` is the single checked-in baseline configuration for Stage 1. It contains repository paths and deliberately leaves data-source and cohort settings unset.

Future stages may add tracked, non-secret configuration files. Machine-specific locations belong in environment variables or an ignored `.env` file, not in Git.
