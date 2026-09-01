"""Configuration loading for reproducible MortgageLab runs.

This module intentionally has no knowledge of agency file layouts or mortgage
event codes. Those definitions require an approved, versioned source contract.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ProjectConfig:
    """Validated Stage 1 project settings and repository-relative paths."""

    repository_root: Path
    name: str
    stage: int
    random_seed: int
    raw_dir: Path
    external_dir: Path
    interim_dir: Path
    processed_dir: Path
    reports_dir: Path
    source_release: str | None
    cohort: str | None
    observation_end: str | None


def _repository_root(config_path: Path) -> Path:
    """Derive the root from a file located directly under ``configs/``."""
    return config_path.resolve().parent.parent


def _path_from_setting(value: str, repository_root: Path, data_root: Path | None) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    if data_root is not None and candidate.parts and candidate.parts[0] == "data":
        return data_root.joinpath(*candidate.parts[1:])
    return repository_root / candidate


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"Configuration section '{label}' must be a mapping.")
    return value


def load_project_config(config_path: str | Path | None = None) -> ProjectConfig:
    """Load configuration without creating directories or accessing source data."""
    default_path = Path(__file__).resolve().parents[2] / "configs" / "project.yml"
    selected_path = Path(config_path or os.environ.get("MORTGAGELAB_CONFIG_PATH", default_path))
    if not selected_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {selected_path}")

    with selected_path.open(encoding="utf-8") as file_handle:
        payload = yaml.safe_load(file_handle) or {}

    project = _require_mapping(payload.get("project"), "project")
    paths = _require_mapping(payload.get("paths"), "paths")
    analysis = _require_mapping(payload.get("analysis"), "analysis")
    root = _repository_root(selected_path)
    data_root_value = os.environ.get("MORTGAGELAB_DATA_ROOT")
    data_root = Path(data_root_value).resolve() if data_root_value else None

    required_paths = ("raw", "external", "interim", "processed", "reports")
    missing_paths = [key for key in required_paths if not isinstance(paths.get(key), str)]
    if missing_paths:
        raise ValueError(f"Configuration paths must be strings; missing/invalid: {missing_paths}")

    return ProjectConfig(
        repository_root=root,
        name=str(project["name"]),
        stage=int(project["stage"]),
        random_seed=int(project["random_seed"]),
        raw_dir=_path_from_setting(paths["raw"], root, data_root),
        external_dir=_path_from_setting(paths["external"], root, data_root),
        interim_dir=_path_from_setting(paths["interim"], root, data_root),
        processed_dir=_path_from_setting(paths["processed"], root, data_root),
        reports_dir=_path_from_setting(paths["reports"], root, data_root),
        source_release=analysis.get("source_release"),
        cohort=analysis.get("cohort"),
        observation_end=analysis.get("observation_end"),
    )
