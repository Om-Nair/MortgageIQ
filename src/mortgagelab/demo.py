"""Runnable synthetic demonstration; not empirical research."""
from __future__ import annotations
import numpy as np, pandas as pd
from .features import build_panel
from .modeling import chronological_split, fit_hazard_model, evaluate
def synthetic_demo(seed: int=42):
    rng=np.random.default_rng(seed); loans=np.repeat([f"S{i:03}" for i in range(120)], 12); periods=np.tile(pd.date_range("2021-01-01",periods=12,freq="MS"),120); age=np.tile(np.arange(1,13),120); rate=rng.normal(5.5,.65,len(loans)); market=np.linspace(4.0,6.0,12); inc=rate-np.tile(market,120); prob=1/(1+np.exp(-(-3+1.3*inc+.03*age))); event=rng.binomial(1,prob)
    perf=pd.DataFrame({"loan_identifier":loans,"period":periods,"loan_age":age,"current_interest_rate":rate,"voluntary_prepayment":event}); macro=pd.DataFrame({"period":pd.date_range("2021-01-01",periods=12,freq="MS"),"market_rate":market})
    panel=build_panel(perf,macro); train,test=chronological_split(panel,"2021-09-01"); model=fit_hazard_model(train); return panel, model, evaluate(model,test)
