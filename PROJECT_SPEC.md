# MortgageLab — Project Specification

## Status and scope

**Status:** proposed; no analytical code, downloaded loan data, empirical result, model metric, or financial conclusion is included in this repository at this stage.

MortgageLab will be a reproducible quantitative research project on borrower prepayment behavior in U.S. agency fixed-rate mortgages. The first build will deliberately be a compact, transparent research pipeline—not a production prepayment model, trading system, or investment recommendation.

## 1. Project objective

Build a loan-month panel from public agency mortgage performance data and public macro/housing series to:

1. describe voluntary prepayment behavior;
2. estimate an interpretable, conditional monthly prepayment model; and
3. compare predicted behavior across clearly stated rate and housing scenarios.

The primary unit of analysis will be an active loan observed in a reporting month. The primary outcome will be a documented indicator for **voluntary prepayment**, as defined by the chosen agency file layout. All definitions will be versioned from the source documentation before implementation.

## 2. Financial motivation

Agency MBS investors receive principal back as borrowers pay down or prepay their loans. Prepayment changes the timing of cash flows and is therefore central to MBS duration, convexity, and reinvestment risk. Refinancing incentive is an important driver, but borrower credit, loan age, burnout, seasonality, geographic house-price dynamics, and competing terminal outcomes also matter.

This project focuses on the borrower-behavior layer. It will not claim to price an MBS, estimate option-adjusted spreads, or forecast desk P&L. Those require security- and pool-level cash-flow, market-volatility, and valuation infrastructure outside this early-career scope.

## 3. Research questions

1. How does observed monthly voluntary-prepayment incidence vary with estimated refinancing incentive?
2. After controlling for loan age and origination characteristics, are rate incentive, borrower/loan attributes, and local house-price changes associated with prepayment?
3. Do those relationships vary across transparent borrower segments?
4. How stable are model estimates and out-of-sample calibration across time vintages?
5. Under explicitly hypothetical rate and house-price shocks, how does the model-implied conditional prepayment probability change?

These are association and prediction questions. The project will not make causal claims from observational data.

## 4. Dataset options and recommended dataset

### Candidate sources

| Source | Role | Benefits | Constraints |
| --- | --- | --- | --- |
| [Freddie Mac Single-Family Loan-Level Dataset](https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset) | Primary loan-level source | Long history; origination and monthly performance; voluntary-prepayment information; free for eligible non-commercial research use | Registration/terms required; large files; data are unaudited and can change; agency population only |
| [Fannie Mae Single-Family Loan Performance Data](https://capitalmarkets.fanniemae.com/credit-risk-transfer/single-family-credit-risk-transfer/fannie-mae-single-family-loan-performance-data) | Alternative / robustness source | Loan-level acquisition and monthly performance data; documented fixed-rate conventional population | Access/terms; a disclosed subset; field definitions and coverage differ from Freddie Mac |
| [FHFA House Price Index](https://www.fhfa.gov/house-price-index) | Housing covariate | Public repeat-sales HPI at national, state, and metro geographies | Geography/timing alignment; index is not an individual-property valuation |
| [FRED: 30-Year Fixed Rate Mortgage Average (MORTGAGE30US)](https://fred.stlouisfed.org/series/MORTGAGE30US) | Market-rate covariate | Public weekly series sourced from Freddie Mac PMMS; easy reproducible retrieval | Survey rate is a proxy, not a borrower-specific refinance offer; PMMS methodology changed in November 2022 |

### Recommendation

Use the **Freddie Mac Single-Family Loan-Level Dataset Standard Dataset** as the primary source, subject to its then-current terms and registration. It is the best fit because the research question needs loan-level monthly performance and a voluntary-prepayment event. Start with a deliberately bounded cohort—for example, a small set of disclosed origination quarters and a fixed observation end date—to keep storage, runtime, and reviewability manageable.

Fannie Mae will remain a documented future robustness option, not a data source to silently mix with Freddie Mac. The implementation must use the file layout and user guide applicable to the downloaded release; source fields and event codes will never be guessed.

## 5. Data architecture

Raw source files are immutable, excluded from Git, and retained only locally after the user has lawfully obtained them. A manifest records source URL, retrieval date, source release/layout version, checksum where practical, selected cohort, and any access note. The pipeline will be deterministic from raw files plus a versioned configuration.

```text
Agency acquisition files ─┐
                         ├─> normalized loan table ─┐
Agency monthly files ────┘                           │
                                                     ├─> active loan-month research panel
FHFA HPI ───────────────> dated geography features ──┤
FRED/PMMS ──────────────> monthly market-rate features┘
                                                          └─> features / model inputs / reports
```

Proposed layers:

- `data/raw/`: ignored source archives and downloads; never edited in place.
- `data/external/`: ignored normalized copies of public macro/HPI downloads with provenance.
- `data/interim/`: ignored, schema-checked staging outputs.
- `data/processed/`: ignored research panels, preferably Parquet, with a data dictionary and run manifest.
- `reports/`: small, reproducible figures/tables and narrative outputs; no loan-level personally sensitive outputs.

Loan identifiers will be treated as sensitive research keys: never displayed in the app, committed, or published. Analysis will use configured data roots (environment variable or local config) rather than hard-coded personal paths.

## 6. Feature engineering strategy

All feature formulas, availability dates, and missing-value rules will be in a versioned feature registry. Features must use information available as of the loan-month observation, preventing look-ahead leakage.

- **Outcome and risk set:** voluntary-prepayment indicator in month *t*; only loans active at the start of *t* enter the risk set. Non-voluntary liquidations, delinquency transitions, and administrative statuses will be handled explicitly and documented.
- **Refinancing incentive:** baseline spread = borrower note rate minus a matched-period proxy mortgage rate. A more finance-aware alternative may approximate a rate threshold that accounts for refinancing frictions; it will be labeled as a sensitivity, not observed borrower economics.
- **Seasoning / amortization:** loan age in months, nonlinear age terms or bins, remaining term if reliably available, and scheduled balance/amortization proxies where source definitions permit.
- **Origination attributes:** note rate, original UPB, original LTV, DTI, credit score, occupancy, purpose, property type, number of units, and geography only when present and documented in the release.
- **Housing context:** lagged FHFA HPI level/growth mapped at the coarsest reliable geography; proxy current LTV based on original LTV and HPI change, clearly labeled as an approximation.
- **Time controls:** calendar month/year effects and a documented monthly aggregation rule for the weekly PMMS/FRED series.
- **Data quality:** preserve missingness indicators; do not impute target/event codes; use train-only fitted imputers for model features.

The MVP will avoid potentially fragile borrower-level demographic inference and will not attempt to identify individual refinances from the public data.

## 7. Statistical/modeling strategy

The primary model will be a discrete-time hazard model: logistic regression of monthly voluntary prepayment among loans in the active risk set. It is interpretable, naturally accommodates time-varying covariates, and aligns with monthly performance reporting.

Model ladder:

1. descriptive rates by age, calendar time, and broad incentive bins;
2. baseline logistic model with age, calendar controls, and refinance-incentive features;
3. expanded regularized logistic model including documented origination and housing features;
4. optional benchmark gradient-boosted trees only if cross-validation shows a material, reproducible improvement and interpretation artifacts (calibration, permutation importance/partial-dependence caveats) are included.

Coefficients will be framed as conditional associations, not structural borrower preferences. Class weights, sampling, or downsampling—if used—must be fitted only on training data and probability calibration must be checked on untouched data.

## 8. Validation strategy

Validation respects time and grouping:

- Train on earlier reporting periods, validate on a later contiguous period, and reserve a final later out-of-time test period.
- Never randomly split loan-month rows across train/test, which would leak the same loan’s trajectory.
- Assess the active risk-set construction and event-code mapping with unit tests and manual reconciliation on documented samples.
- Report event prevalence, calibration curve/intercept/slope, Brier score, log loss, and ROC-AUC or PR-AUC only after they are actually computed. Do not pre-populate results.
- Compare calibration and key error metrics by reporting period, age/incentive bands, and chosen borrower segments, subject to minimum-count rules.
- Conduct sensitivity checks for cohort choice, macro-rate aggregation, HPI geography, and treatment of competing outcomes.

The model should be judged first on calibration and stability, not headline discrimination alone.

## 9. Scenario analysis

Scenario analysis will score the held-out/reference loan-month population under counterfactual covariate changes while holding non-scenario features fixed. It will show differences in **model-implied conditional monthly prepayment probability**, not realized market forecasts.

Initial scenarios:

1. parallel market mortgage-rate changes (e.g., stated basis-point shocks);
2. alternative local HPI growth shocks; and
3. combined rate/HPI scenarios.

Each chart/table will display the exact shock, reference population/date, model version, and the fact that it is conditional rather than a full equilibrium forecast. No conversion to PSA, CPR, duration, or MBS price will be made in the MVP unless later approved with a separately validated cash-flow framework.

## 10. Borrower segmentation

Segments will be formed from origination attributes available in the released data, with labels chosen for clarity rather than marketing value. Candidate cuts include:

- original LTV bands;
- credit-score bands;
- loan balance bands;
- occupancy / purpose / property-type categories; and
- geography only at the data’s supported aggregation level.

Rules: use documented bins, show segment sample/event counts, suppress unstable tiny groups, avoid demographic proxies, and distinguish heterogeneous predictive performance from causal or fairness conclusions.

## 11. Streamlit application

The future app is a local research explorer, not a prediction service. It will load only a prebuilt aggregated/model-ready artifact, never raw loan files, and will include:

- data/cohort and source-release summary;
- descriptive prepayment plots;
- model-card summary with actual validation outputs;
- segment comparison views with counts;
- controlled rate/HPI scenario inputs; and
- downloadable aggregated tables/figures where permitted by data terms.

The interface will display limitations, source links, as-of date, and a “not investment advice / not a production model” notice. Default inputs will be descriptive rather than implying a forecast.

## 12. Repository structure

```text
MortgageLab/
├── README.md
├── PROJECT_SPEC.md
├── PROJECT_GUIDE.md
├── requirements.txt
├── .gitignore
├── notebooks/          # numbered, exploratory/reproducible narratives
├── src/
│   └── mortgagelab/    # ingest, schemas, features, modeling, evaluation, scenarios
├── data/
│   ├── raw/            # ignored
│   ├── external/       # ignored
│   ├── interim/        # ignored
│   └── processed/      # ignored
├── app/                # Streamlit entry point and display helpers
├── reports/            # reproducible aggregate outputs and figures
├── tests/              # unit/integration tests using synthetic fixtures
├── configs/            # cohort, paths, feature/model settings
└── docs/               # source notes, data dictionary, model card
```

Only this specification is created now. The eventual `README.md` will be concise, personal in voice, and candid about scope; `PROJECT_GUIDE.md` will be the detailed study companion.

## 13. Testing strategy

Use `pytest` and synthetic miniature acquisition/performance fixtures. Tests will cover parsing against versioned schemas, date alignment, active-risk-set eligibility, event classification, no duplicate loan-month keys, feature availability/lagging, train-only transformations, deterministic configurations, and scenario transformations. Integration tests will run a tiny end-to-end pipeline without downloading or exposing licensed loan data.

## 14. Documentation strategy

Documentation will include source URLs and access dates, source-layout version, a field-level data dictionary, transformation lineage, feature definitions/formulas, cohort exclusions, model card, validation protocol, scenario assumptions, known limitations, and commands to reproduce every published output. Notebooks will be explanatory; reusable logic belongs in `src/` and is tested.

## 15. Reproducibility requirements

- Pin Python dependencies and record Python version.
- Use a single configuration file for cohort bounds, paths, seeds, and feature/model choices.
- Persist run metadata: Git commit (when available), configuration hash, data manifest, timestamps, and library versions.
- Seed stochastic steps; make ordering deterministic.
- Keep raw data and secrets out of Git; provide a sample `.env.example` later, never credentials.
- Use public source retrieval scripts where allowed, with checksum/file-size validation and respectful manual-access fallback.
- Generate all reported charts/tables from commands or notebooks; no manually edited results.

## 16. JPMorgan interview relevance

The project demonstrates a desk-strategy workflow: defining a mortgage behavior question, constructing a loan-level panel, modeling competing borrower incentives with careful time alignment, validating out of time, and communicating scenario sensitivity. It creates space to discuss agency MBS prepayment risk, refinancing incentive, seasoning, burnout, geographic housing conditions, model risk, data licensing, and the difference between a behavioral model and security valuation.

It will not represent JPMorgan views, methodology, data, or investment recommendations.

## 17. Potential limitations

- Agency conventional fixed-rate loans are not the entire U.S. mortgage market.
- Public data are delayed, subject to revisions, and governed by terms of use.
- Event coding and reporting conventions must be verified per source release.
- PMMS/FRED mortgage rates are a proxy for an individual borrower’s refinance offer and frictions.
- HPI is an area-level index, not a property appraisal; proxy CLTV is measurement error.
- Prepayment is affected by unobserved borrower liquidity, mobility, servicing, fees, capacity, and macro conditions.
- Static loan samples, survivorship/risk-set choices, competing exits, and policy-regime changes can affect estimates.
- Statistical association and scenario sensitivity are not causal inference, realized forecasts, or MBS valuation.
- Disclosure rules/terms may constrain sharing granular data or derived artifacts.

## Proposed implementation sequence after approval

1. Scaffold the repository, environment, configuration, and synthetic fixtures.
2. Add source notes, download/manifest conventions, and schema validation for the selected Freddie Mac release.
3. Build a small-cohort ingestion and quality-report pipeline.
4. Construct the loan-month risk set and descriptive analysis.
5. Add baseline model, out-of-time evaluation, and model card.
6. Add scenarios, then a small Streamlit research app.

## Source notes (accessed 2026-09-01)

- Freddie Mac describes its Single-Family Loan-Level Dataset, access requirements, historical coverage, and voluntary-prepayment performance information: [source page](https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset).
- Fannie Mae describes its Single-Family Loan Performance Data, covered fixed-rate loan population, monthly performance files, and access: [source page](https://capitalmarkets.fanniemae.com/credit-risk-transfer/single-family-credit-risk-transfer/fannie-mae-single-family-loan-performance-data).
- FHFA documents HPI availability and geography coverage: [HPI datasets](https://www.fhfa.gov/house-price-index) and [HPI overview/methodology context](https://www.fhfa.gov/fhfa-house-price-index).
- FRED documents the weekly MORTGAGE30US series and its Freddie Mac PMMS source/methodology note: [series page](https://fred.stlouisfed.org/series/MORTGAGE30US).
