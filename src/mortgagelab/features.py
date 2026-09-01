"""Leakage-aware loan-month features for normalized, approved input tables."""
from __future__ import annotations
import pandas as pd

def build_panel(performance: pd.DataFrame, rates: pd.DataFrame, originations: pd.DataFrame | None = None) -> pd.DataFrame:
    required = {"loan_identifier", "period", "loan_age", "current_interest_rate", "voluntary_prepayment"}
    if missing := required - set(performance): raise ValueError(f"Missing performance fields: {sorted(missing)}")
    out = performance.copy(); out["period"] = pd.to_datetime(out["period"]).dt.to_period("M").dt.to_timestamp()
    macro = rates.copy(); macro["period"] = pd.to_datetime(macro["period"]).dt.to_period("M").dt.to_timestamp()
    if "market_rate" not in macro: raise ValueError("rates requires market_rate")
    out = out.merge(macro[["period", "market_rate"]], on="period", how="left", validate="many_to_one")
    out["refinance_incentive_pct"] = out["current_interest_rate"] - out["market_rate"]
    out["age_squared"] = out["loan_age"] ** 2
    out["season"] = out["period"].dt.month
    if originations is not None: out = out.merge(originations, on="loan_identifier", how="left", validate="many_to_one")
    return out.sort_values(["loan_identifier", "period"]).reset_index(drop=True)

def segment_ltv(frame: pd.DataFrame) -> pd.Series:
    return pd.cut(frame["original_ltv"], [-float("inf"), 80, 90, float("inf")], labels=["≤80", "81–90", ">90"])
