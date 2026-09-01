"""Public-data helpers and a guarded Freddie Mac performance-file adapter."""
from __future__ import annotations
import hashlib
from pathlib import Path
import pandas as pd
from zipfile import ZipFile

FRED_MORTGAGE30US_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
FHFA_HPI_URL = "https://www.fhfa.gov/hpi/download/hpi_master.csv"
# Verified in Freddie Mac's July 2026 General User Guide. It means prepaid or matured.
FREDDIE_VOLUNTARY_PAYOFF_CODE = "01"
# Freddie Mac SFLLD General User Guide (effective July 2026), positions 1–31/1–35.
FREDDIE_ORIGINATION_COLUMNS = ["credit_score","first_payment_date","first_time_homebuyer_flag","maturity_date","msa","mortgage_insurance_pct","number_of_units","occupancy_status","original_cltv","original_dti","original_upb","original_ltv","original_interest_rate","channel","prepayment_penalty_flag","product_type","property_state","property_type","postal_code","loan_identifier","loan_purpose","original_loan_term","number_of_borrowers","seller_name","super_conforming_flag","pre_harp_loan_identifier","program_indicator","harp_indicator","property_valuation_method","interest_only_indicator","mortgage_insurance_cancellation_indicator"]
FREDDIE_PERFORMANCE_COLUMNS = ["loan_identifier","period","current_actual_upb","current_delinquency_status","loan_age","remaining_months_to_legal_maturity","defect_settlement_date","modification_flag","zero_balance_code","zero_balance_effective_date","current_interest_rate","current_non_interest_bearing_upb","due_date_last_paid_installment","mi_recoveries","net_sales_proceeds","non_mi_recoveries","total_expenses","legal_costs","maintenance_and_preservation_costs","taxes_and_insurance","miscellaneous_expenses","actual_loss","cumulative_modification_costs","interest_rate_step_indicator","payment_deferral_flag","estimated_ltv","zero_balance_removal_upb","delinquent_accrued_interest","delinquency_due_to_disaster","borrower_assistance_plan","current_period_modification_costs","current_interest_bearing_upb","mortgage_insurance_cancellation_indicator","servicer_name","bankruptcy_cramdown_costs"]

def download_public_csv(url: str, destination: str | Path) -> Path:
    """Download a public CSV with pandas; never use this for gated loan files."""
    destination = Path(destination); destination.parent.mkdir(parents=True, exist_ok=True)
    pd.read_csv(url).to_csv(destination, index=False)
    return destination

def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_freddie_performance(path: str | Path, columns: list[str]) -> pd.DataFrame:
    """Read a downloaded pipe-delimited performance file using an approved release layout.

    Caller must obtain ``columns`` from the exact Freddie Mac release's layout;
    the code deliberately does not assume the full evolving positional schema.
    """
    frame = pd.read_csv(path, sep="|", header=None, names=columns, dtype=str, na_values=["", " "])
    required = {"loan_identifier", "period", "loan_age", "zero_balance_code", "current_interest_rate"}
    missing = required - set(frame.columns)
    if missing: raise ValueError(f"Approved layout must map required fields: {sorted(missing)}")
    frame["period"] = pd.to_datetime(frame["period"], format="%Y%m", errors="raise")
    for field in ("loan_age", "current_interest_rate"):
        frame[field] = pd.to_numeric(frame[field], errors="coerce")
    frame["voluntary_prepayment"] = frame["zero_balance_code"].fillna("").str.zfill(2).eq(FREDDIE_VOLUNTARY_PAYOFF_CODE)
    return frame

def _member(zip_path: str | Path, prefix: str) -> str:
    with ZipFile(zip_path) as archive:
        matches=[item.filename for item in archive.infolist() if Path(item.filename).name.startswith(prefix)]
    if len(matches) != 1: raise ValueError(f"Expected one {prefix} member in {zip_path}; found {matches}")
    return matches[0]

def read_freddie_sample(zip_path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read an official sample ZIP immutably, selecting only analysis fields."""
    origin_member, performance_member = _member(zip_path,"sample_orig_"), _member(zip_path,"sample_perf_")
    with ZipFile(zip_path) as archive:
        origin=pd.read_csv(archive.open(origin_member),sep="|",header=None,names=FREDDIE_ORIGINATION_COLUMNS,usecols=[0,8,10,11,12,19],dtype={"loan_identifier":"string"})
        performance=pd.read_csv(archive.open(performance_member),sep="|",header=None,names=FREDDIE_PERFORMANCE_COLUMNS,usecols=[0,1,4,8,10],dtype={"loan_identifier":"string","zero_balance_code":"string"})
    performance["period"]=pd.to_datetime(performance["period"],format="%Y%m",errors="raise")
    for col in ["loan_age","current_interest_rate"]: performance[col]=pd.to_numeric(performance[col],errors="coerce")
    for col in ["original_ltv","original_upb","original_interest_rate"]: origin[col]=pd.to_numeric(origin[col],errors="coerce")
    performance["voluntary_prepayment"]=performance["zero_balance_code"].fillna("").str.zfill(2).eq(FREDDIE_VOLUNTARY_PAYOFF_CODE)
    return origin, performance
