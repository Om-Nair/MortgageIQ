from __future__ import annotations

from pathlib import Path

import pytest

from mortgagelab import load_project_config


def test_default_configuration_resolves_repository_paths() -> None:
    config = load_project_config()

    assert config.name == "MortgageLab"
    assert config.stage == 1
    assert config.source_release is None
    assert config.cohort is None
    assert config.raw_dir == config.repository_root / "data" / "raw"
    assert config.reports_dir == config.repository_root / "reports"


def test_data_root_override_redirects_only_data_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MORTGAGELAB_DATA_ROOT", str(tmp_path / "local-data"))

    config = load_project_config()

    assert config.raw_dir == tmp_path / "local-data" / "raw"
    assert config.processed_dir == tmp_path / "local-data" / "processed"
    assert config.reports_dir == config.repository_root / "reports"


def test_missing_configuration_raises_clear_error(tmp_path: Path) -> None:
    missing_path = tmp_path / "absent.yml"

    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        load_project_config(missing_path)
