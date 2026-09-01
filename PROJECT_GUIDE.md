# MortgageLab study guide

## Status

MortgageLab treats prepayment as a monthly discrete-time event among loans still active at the start of a month. Agency MBS cash flows change when borrowers return principal early; refinancing incentive, age/seasoning, credit, collateral and local housing conditions can all matter. This repository models conditional borrower behavior, not the value of an MBS.

## Planned sections

1. Agency MBS and borrower prepayment concepts
2. Public-data provenance and limitations
3. Loan-month panel construction and risk sets
4. Feature definitions and information timing
5. Discrete-time hazard modeling
6. Time-based validation and calibration
7. Scenario analysis boundaries
8. Code architecture and reproducibility
9. Assumptions, limitations, and interview questions

## Method and architecture

The pipeline separates raw gated agency files, public macro downloads, normalized data, feature panels, models, and reports. Raw/derived data are ignored by Git. `data.read_freddie_performance` accepts only a caller-supplied release-specific map, parses the pipe-delimited file, and identifies the documented voluntary-payoff code `01`. The source guide says performance is monthly and runs until termination or cutoff; that is why row-level random splitting is inappropriate.

`features.build_panel` merges a month-aligned market-rate proxy and creates note-rate minus market-rate incentive, age squared, and month seasonality. Inputs must be known by the reporting month. The baseline logistic regression is a discrete-time hazard model; it is deliberately interpretable, but coefficient associations are not causal.

`modeling.chronological_split` keeps later observations out of training. Evaluation reports Brier score, ROC-AUC and average precision only when executed; synthetic outputs are demonstration outputs, never research findings. Segment cuts use documented original-LTV values when a normalized input supplies them. `scenarios.rate_shock` holds other covariates fixed and reports model-implied conditional probabilities under a stated rate shock.

## Assumptions and limitations

FRED/PMMS is not a borrower-specific refinance quote; FHFA HPI is not a property appraisal. Agency data exclude much of the broader market and can be revised. Competing exits and source timing matter. No current code identifies actual refinances, prices MBS pools, forecasts CPR, or makes investment recommendations.

## Interview prompts

- Why use a discrete-time hazard? Monthly reporting and a clearly defined risk set make it transparent.
- Why time splits? Loan-month random splits leak trajectories and future regimes.
- Why calibration? A prepayment probability is more useful only if its level is credible, not merely rank ordered.
- What is missing? Borrower refinance offers, fees, liquidity, mobility, servicing and market capacity.
