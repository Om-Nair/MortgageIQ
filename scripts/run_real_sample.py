"""Run the documented 2020/2021 Freddie Mac sample analysis without modifying ZIPs."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from mortgagelab.data import FRED_MORTGAGE30US_URL, read_freddie_sample, sha256
from mortgagelab.features import build_panel
from mortgagelab.features import segment_ltv
from mortgagelab.modeling import chronological_split, fit_hazard_model, evaluate

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("zips",nargs="+"); parser.add_argument("--cutoff",default="2025-01-01"); parser.add_argument("--output",default="reports/real_sample_run.json"); args=parser.parse_args()
    origins=[]; performance=[]; manifest=[]
    for file in map(Path,args.zips):
        origin, perf=read_freddie_sample(file); origins.append(origin); performance.append(perf); manifest.append({"file":file.name,"sha256":sha256(file),"loans":int(origin.loan_identifier.nunique()),"loan_months":int(len(perf))})
    origin=pd.concat(origins,ignore_index=True).drop_duplicates("loan_identifier")
    perf=pd.concat(performance,ignore_index=True).drop_duplicates(["loan_identifier","period"])
    rates=pd.read_csv(FRED_MORTGAGE30US_URL); rates.columns=["period","market_rate"]; rates["period"]=pd.to_datetime(rates.period); rates["market_rate"]=pd.to_numeric(rates.market_rate,errors="coerce")
    monthly=rates.set_index("period").resample("MS").mean().interpolate().reset_index()
    panel=build_panel(perf,monthly,origin[["loan_identifier","original_ltv","original_upb","original_interest_rate"]]).dropna(subset=["market_rate","current_interest_rate"])
    train,test=chronological_split(panel,args.cutoff)
    features=["refinance_incentive_pct","loan_age","age_squared","season","original_ltv"]
    model=fit_hazard_model(train,features); metrics=evaluate(model,test,features)
    segments=panel.assign(ltv_segment=segment_ltv(panel)).groupby("ltv_segment",observed=True).agg(loan_months=("loan_identifier","size"),prepayments=("voluntary_prepayment","sum"),rate=("voluntary_prepayment","mean")).reset_index()
    result={"source":"Freddie Mac SFLLD sample ZIPs supplied locally", "manifest":manifest,"combined_loans":int(origin.loan_identifier.nunique()),"combined_loan_months":int(len(panel)),"prepayments":int(panel.voluntary_prepayment.sum()),"train_rows":int(len(train)),"test_rows":int(len(test)),"cutoff":args.cutoff,"model_features":features,"metrics":metrics,"ltv_segments":segments.to_dict(orient="records")}
    Path(args.output).parent.mkdir(exist_ok=True); Path(args.output).write_text(json.dumps(result,indent=2),encoding="utf-8"); print(json.dumps(result,indent=2))
if __name__ == "__main__": main()
