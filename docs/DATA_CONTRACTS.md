# Data contracts

The real-data path uses the official Freddie Mac SFLLD **sample** ZIP files for 2020 and 2021 supplied locally. ZIPs are read in place and remain outside the repository/Git history.

Authority: Freddie Mac [Single-Family Loan-Level Dataset General User Guide](https://www.freddiemac.com/fmac-resources/research/pdf/user_guide.pdf), accessed 2026-09-01. It states sample files are pipe-delimited, headerless files and gives the 31-column origination and 35-column performance layouts. The implementation selects only documented fields needed for this project. Its Zero Balance Code `01` is **Prepaid or Matured (Voluntary Payoff)**; this is the event definition used here. Other zero-balance codes are not treated as voluntary prepayment.

The sample is not the entire Freddie Mac population and performance can extend beyond the vintage year. FRED MORTGAGE30US is merged at month start after monthly averaging/interpolation. FHFA HPI is not yet merged in the executed 2020/2021 run; the source has a property-state field, but adding a state-HPI source, timing convention, and QA checks is a deliberate next iteration rather than an unverified merge.
