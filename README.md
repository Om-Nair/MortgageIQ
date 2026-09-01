# MortgageLab

MortgageLab is a reproducible research project on voluntary mortgage prepayment in U.S. agency fixed-rate loans. I built it as a compact, interview-ready way to discuss the plumbing behind an agency-MBS borrower-behavior question: data provenance, loan-month risk sets, refinance incentive, time-based validation, and clear limits on what a model can claim.

It is not an MBS pricing engine, a forecast, investment advice, or a representation of JPMorgan Chase methodology.

## What works now

- A guarded local adapter for downloaded Freddie Mac performance files. It requires a release-specific column map; it does not silently guess an evolving file layout.
- Public-source download helpers for FRED MORTGAGE30US and FHFA HPI.
- Leakage-aware feature construction, an interpretable discrete-time logistic hazard baseline, chronological validation, borrower-LTV segmentation helper, and rate-shock scenario scoring.
- A Streamlit explorer that displays a locally generated real-sample report when available, plus an end-to-end synthetic fallback for tests. No raw mortgage data ships with this repository.
- Aggregate EDA helpers for monthly risk-set and voluntary-prepayment incidence plots.

Freddie Mac’s General User Guide documents its pipe-delimited files, monthly performance records, and zero-balance code `01` as “Prepaid or Matured (Voluntary Payoff).” Read the [dataset page](https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset) and [user guide](https://www.freddiemac.com/fmac-resources/research/pdf/user_guide.pdf) before obtaining data. The dataset requires registration/sign-in and is subject to its terms.

## Setup

Requires Python 3.10+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the real sample analysis first (after downloading the permitted ZIPs), then use the synthetic pipeline for a no-data smoke test:

```powershell
$env:PYTHONPATH = "src"
python scripts/run_real_sample.py C:\path\sample_2020.zip C:\path\sample_2021.zip
python scripts/run_synthetic_demo.py
pytest
streamlit run app/streamlit_app.py
```

## Real-data workflow

1. Register for and download the permitted Freddie Mac release manually; do not commit it.
2. Record release, retrieval date, source URL and checksum in a local manifest.
3. Translate the exact source layout into the `columns` argument of `read_freddie_performance`; use only the documented names/positions for that release.
4. Download public rate/HPI data with the helpers, preserve their retrieval metadata, then build a normalized panel.

The adapter needs `loan_identifier`, `period`, `loan_age`, `zero_balance_code`, and `current_interest_rate` in that explicit mapping. Its event definition is documented in `docs/DATA_CONTRACTS.md`.

With local ZIPs, run:

```powershell
$env:PYTHONPATH = "src"
python scripts/run_real_sample.py C:\path\sample_2020.zip C:\path\sample_2021.zip
```

This writes an ignored, local `reports/real_sample_run.json` manifest and results file. It does not modify or copy the ZIPs.

## Layout

`src/mortgagelab/` contains reusable data, feature, model, and scenario logic. `tests/` uses synthetic fixtures only. `docs/` holds contracts, model-card scaffolding, and reproducibility notes. `PROJECT_GUIDE.md` is the study guide; `PROJECT_SPEC.md` is the governing design.

## Limits

The PMMS/FRED rate is a market proxy rather than a borrower offer; HPI is an area index rather than an appraisal. Associations are not causal effects, model probabilities are not forecasts, and the MVP does not estimate CPR/PSA, duration, OAS, or security prices.
