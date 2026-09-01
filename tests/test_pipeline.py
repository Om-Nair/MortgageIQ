import pandas as pd
from mortgagelab.demo import synthetic_demo
from mortgagelab.eda import monthly_prepayment_summary
from mortgagelab.features import build_panel
from mortgagelab.scenarios import rate_shock

def test_synthetic_pipeline_runs_end_to_end():
    panel, model, metrics = synthetic_demo()
    assert len(panel) == 1440
    assert set(metrics) == {"brier","roc_auc","average_precision","n"}
    assert 0 <= metrics["brier"] <= 1
    assert rate_shock(model, panel, -100).scenario_probability.between(0,1).all()
    assert len(monthly_prepayment_summary(panel)) == 12

def test_panel_incentive_is_rate_minus_market_rate():
    perf=pd.DataFrame({"loan_identifier":["x"],"period":["2020-01-01"],"loan_age":[1],"current_interest_rate":[6.0],"voluntary_prepayment":[False]})
    rates=pd.DataFrame({"period":["2020-01-01"],"market_rate":[5.0]})
    assert build_panel(perf,rates).loc[0,"refinance_incentive_pct"] == 1.0
