from __future__ import annotations
import pandas as pd
from .modeling import DEFAULT_FEATURES
def rate_shock(model, panel: pd.DataFrame, shock_bps: float) -> pd.DataFrame:
    out=panel.copy(); out["market_rate"] += shock_bps/100; out["refinance_incentive_pct"] -= shock_bps/100
    out["scenario_probability"] = model.predict_proba(out[DEFAULT_FEATURES])[:,1]; return out
