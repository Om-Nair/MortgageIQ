# MortgageLab

MortgageLab is a personal quantitative research project on mortgage borrower prepayment behavior. It uses Freddie Mac’s public Single-Family Loan-Level Dataset sample files to build a loan-month panel and study how documented voluntary payoffs relate to refinancing incentive, loan seasoning, calendar effects, and original loan-to-value ratio (LTV).

It is a borrower-behavior study, not an MBS pricing engine, investment recommendation, or production model. The aim is to make the data choices, event definition, time alignment, validation, and limitations explicit.

## Why prepayment matters

When a borrower prepays, principal returns earlier than scheduled. In agency mortgage-backed securities, this changes cash-flow timing and contributes to extension and contraction risk. A loan’s rate relative to prevailing mortgage rates is important, but so are seasoning, collateral, credit, housing conditions, transaction costs, servicing, and borrower circumstances.

MortgageLab asks a narrower question: given the information represented in a public loan-level sample, how well can a transparent monthly model characterize the probability of a documented voluntary payoff?

## Research questions

- How common are documented voluntary payoffs in the 2020 and 2021 Freddie Mac sample vintages?
- How is a loan’s current rate relative to a market-rate proxy associated with monthly voluntary payoff?
- What role do loan age, seasonality, and original LTV play in a simple conditional model?
- Does a model trained on earlier reporting periods remain informative on later periods?
- How do observed payoff rates vary across broad original-LTV segments?

These are descriptive and predictive questions, not causal claims.

## Data

### Freddie Mac sample files

The executed analysis uses the official Freddie Mac Single-Family Loan-Level Dataset sample ZIPs for 2020 and 2021. Each ZIP contains a headerless, pipe-delimited origination file and its monthly performance file. The pipeline reads ZIP members in place; it does not alter or extract the original archives into the repository.

| Vintage | Loans | Loan-month observations |
| --- | ---: | ---: |
| 2020 sample | 50,000 | 2,517,857 |
| 2021 sample | 50,000 | 2,537,054 |
| **Combined** | **100,000** | **5,054,911** |

The Freddie Mac guide documents 31 origination columns and 35 performance columns for the sample format. MortgageLab selects documented fields needed for this analysis: loan identifier, reporting period, loan age, current interest rate, zero-balance code, original LTV, original UPB, and original interest rate.

### Market-rate proxy

The project downloads [FRED series MORTGAGE30US](https://fred.stlouisfed.org/series/MORTGAGE30US), Freddie Mac’s weekly 30-year fixed-rate mortgage average. It is converted to a monthly series through monthly averaging and interpolation, then joined to each loan-month by reporting month.

This is a public market proxy, not an observed refinance offer. It does not include an individual borrower’s fees, closing costs, eligibility, or lender terms.

### Data access

Raw ZIPs are not distributed with this repository. Freddie Mac requires users to register and accept its access terms. Raw and derived data are excluded from Git to respect those terms and keep the repository manageable. Tests use only small, explicitly fictional fixtures.

FHFA house-price data is identified in the specification as a future covariate. It is not merged into the executed run: the source includes property state, but a defensible state-HPI timing and quality-control convention has not yet been implemented.

## Event definition and loan-month panel

The unit of analysis is a loan-month: one loan in one Freddie Mac monthly performance record. The panel includes loan-months with an available current interest rate and market-rate proxy.

Freddie Mac documents Zero Balance Code `01` as **“Prepaid or Matured (Voluntary Payoff).”** MortgageLab labels only that code as `voluntary_prepayment = 1`; it does not relabel other termination codes as prepayments. A voluntary payoff is not proof that a borrower refinanced: it can include other voluntary payoff or maturity outcomes.

The combined panel contains 28,968 records labelled as voluntary payoffs under this definition.

## Feature engineering

The executed baseline uses:

- **Refinancing incentive:** current loan interest rate minus the monthly market-rate proxy. A positive value means the current loan rate is above the proxy.
- **Loan age:** disclosed months since origination/acquisition.
- **Loan age squared:** a simple nonlinear seasoning term.
- **Calendar month:** a seasonal control.
- **Original LTV:** the disclosed origination LTV.

Period data are aligned to calendar months before joining. Numeric preprocessing is contained in the model pipeline: median imputation and standardization are learned from training data, not the holdout set.

## Model and validation

MortgageLab fits a discrete-time logistic hazard model. Each row is the probability of a documented voluntary payoff in that month, conditional on the loan appearing in the monthly performance data. Logistic regression is a useful first baseline because it is transparent, works with time-varying rate features, and is practical at this panel size.

Voluntary payoffs are relatively rare, so the model uses class weighting. Validation is chronological rather than random:

| Split | Rule | Loan-months |
| --- | --- | ---: |
| Training | Before 2025-01-01 | 3,959,824 |
| Test | 2025-01-01 and later | 1,095,087 |

A random loan-month split could leak later portions of the same loan trajectory into training. The chronological split is a tougher check of temporal stability.

## Executed real-data results

The following values were produced by `scripts/run_real_sample.py` using the supplied 2020 and 2021 sample ZIPs and FRED MORTGAGE30US. They are written locally to ignored `reports/real_sample_run.json` when the script runs.

| Held-out metric | Result |
| --- | ---: |
| Brier score | 0.0854341 |
| ROC-AUC | 0.520245 |
| Average precision | 0.004589 |
| Test observations | 1,095,087 |

The ROC-AUC is modest. That is informative rather than a result to hide: this small feature set and broad rate proxy do not sharply rank later voluntary payoff events in this sample. Many borrower-specific and institutional drivers are unobserved, and the operating environment changes through time. The result supports further calibration work, richer time-valid features, and explicit competing-exit treatment; it does not support overstating the model’s forecasting ability.

The Brier score and average precision should also be read in the context of a rare event and a class-weighted classifier. They are reported exactly as produced, and the repository does not claim the current model is calibrated for decision-making.

### Borrower segmentation

Original LTV is used for descriptive segmentation, not causal comparison.

| Original LTV | Loan-months | Voluntary payoffs | Observed monthly rate |
| --- | ---: | ---: | ---: |
| ≤80 | 3,953,651 | 22,649 | 0.5729% |
| 81–90 | 509,329 | 3,124 | 0.6134% |
| >90 | 591,931 | 3,195 | 0.5398% |

The 81–90 segment has the highest observed rate in this sample and period. That is descriptive only: the segments differ in many ways beyond LTV.

## Scenario analysis

`mortgagelab.scenarios.rate_shock` applies a stated basis-point shock to the market-rate proxy, recomputes refinancing incentive, holds other features fixed, and scores model-implied conditional monthly probabilities.

This is sensitivity analysis, not a realized forecast. It excludes borrower refinance costs, lender capacity, market equilibrium, and changes in other economic variables. The Streamlit app exposes this capability in its synthetic fallback; the real-data run currently reports aggregate metrics and LTV segments.

## Repository layout

```text
MortgageLab/
├── README.md
├── PROJECT_SPEC.md          # Research design and scope
├── PROJECT_GUIDE.md         # Concepts and implementation notes
├── configs/                 # Checked-in configuration
├── data/                    # Ignored raw/interim/processed data directories
├── docs/                    # Data contract, model card, reproducibility notes
├── src/mortgagelab/         # Ingestion, features, EDA, model, scenarios
├── scripts/                 # Real-sample and synthetic entry points
├── app/                     # Streamlit explorer
├── tests/                   # Tests and synthetic fixtures only
└── reports/                 # Ignored local outputs
```

## Installation

Python 3.10+ is required.

```powershell
git clone https://github.com/Om-Nair/MortgageIQ.git
cd MortgageIQ
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Reproduce the analysis

1. Register for Freddie Mac SFLLD and download permitted 2020 and 2021 sample ZIPs.
2. Keep the ZIPs outside the repository or in an ignored data directory.
3. Run:

```powershell
$env:PYTHONPATH = "src"
python scripts/run_real_sample.py C:\path\to\sample_2020.zip C:\path\to\sample_2021.zip
```

The script validates ZIP member naming, reads the files in place, downloads the FRED rate series, prints a manifest and metrics, and writes the ignored local result to `reports/real_sample_run.json`.

Launch the explorer:

```powershell
$env:PYTHONPATH = "src"
streamlit run app/streamlit_app.py
```

With a local report present, the app displays real-sample results. Otherwise it clearly states that it is showing synthetic fallback data.

## Testing

```powershell
python -m pytest -q
```

Tests cover configuration, the explicit synthetic fixture contract, loan-month feature construction, the synthetic end-to-end pipeline, and rate-shock probability bounds. They do not require Freddie Mac data or network access.

For a no-data smoke test:

```powershell
$env:PYTHONPATH = "src"
python scripts/run_synthetic_demo.py
```

Synthetic outputs are plumbing tests only and are not the real-data results above.

## Limitations and next steps

- The data cover Freddie Mac’s disclosed fixed-rate agency sample, not the full U.S. mortgage market.
- Voluntary payoff is broader than observed refinancing.
- The market-rate proxy omits borrower-specific offers, fees, liquidity, and capacity constraints.
- Competing termination outcomes are not yet explicitly modeled.
- The current feature set is intentionally small and has limited out-of-time discrimination.
- HPI enrichment, detailed delinquency treatment, calibration analysis, and a real-data scenario artifact require documented timing and validation before inclusion.

## Primary sources

- [Freddie Mac Single-Family Loan-Level Dataset](https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset)
- [Freddie Mac Single-Family Loan-Level Dataset General User Guide](https://www.freddiemac.com/fmac-resources/research/pdf/user_guide.pdf)
- [FRED: 30-Year Fixed Rate Mortgage Average in the United States (MORTGAGE30US)](https://fred.stlouisfed.org/series/MORTGAGE30US)
- [FHFA House Price Index datasets](https://www.fhfa.gov/house-price-index)

See [PROJECT_SPEC.md](PROJECT_SPEC.md) for the governing research specification and [PROJECT_GUIDE.md](PROJECT_GUIDE.md) for the accompanying concepts and implementation guide.
