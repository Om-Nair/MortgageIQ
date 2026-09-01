from __future__ import annotations

import csv

from conftest import FIXTURES_DIR


def test_synthetic_fixtures_are_explicitly_non_production_and_readable() -> None:
    fixture_path = FIXTURES_DIR / "synthetic_loan_month_panel.csv"
    with fixture_path.open(newline="", encoding="utf-8") as file_handle:
        rows = list(csv.DictReader(file_handle))

    assert len(rows) == 4
    assert {row["fixture_note"] for row in rows} == {"synthetic_only"}
    assert {row["synthetic_loan_id"] for row in rows} == {"SYN-001", "SYN-002"}
    assert all(row["agency_event_code"] == "NOT_DEFINED" for row in rows)
