"""MortgageLab local research explorer."""
from pathlib import Path
import json
import streamlit as st
from mortgagelab.demo import synthetic_demo
from mortgagelab.scenarios import rate_shock
st.set_page_config(page_title="MortgageLab", layout="wide")
st.title("MortgageLab")
st.caption("Local research explorer. Synthetic demonstration by default; not investment advice or a production model.")
report_path=Path("reports/real_sample_run.json")
if report_path.exists():
    report=json.loads(report_path.read_text(encoding="utf-8"))
    st.success("Displaying results from the locally run Freddie Mac sample analysis.")
    st.subheader("Real sample: chronological holdout metrics")
    st.json(report["metrics"])
    st.caption(f"{report['combined_loans']:,} loans; {report['combined_loan_months']:,} loan-months; cutoff {report['cutoff']}. The JSON is local and ignored by Git.")
    st.dataframe(report.get("ltv_segments", []), use_container_width=True)
else:
    panel, model, metrics = synthetic_demo()
    st.info("No local real-data run found. Displaying explicitly synthetic data.")
    st.subheader("Chronological holdout metrics (synthetic demonstration)")
    st.json(metrics)
if not report_path.exists():
    shock=st.slider("Market-rate shock (basis points)",-200,200,0,25)
    scenario=rate_shock(model,panel,shock)
    st.metric("Mean model-implied conditional monthly probability", f"{scenario.scenario_probability.mean():.2%}")
    st.line_chart(scenario.groupby("period").scenario_probability.mean())
with st.expander("Data and scope"):
    st.markdown("Freddie Mac data require registration and must be processed locally under its terms. See PROJECT_SPEC.md and docs/DATA_CONTRACTS.md.")
