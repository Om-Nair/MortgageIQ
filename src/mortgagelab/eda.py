"""Descriptive, aggregate-only EDA helpers."""
from __future__ import annotations
import matplotlib.pyplot as plt
import pandas as pd

def monthly_prepayment_summary(panel: pd.DataFrame) -> pd.DataFrame:
    """Return risk-set count and observed event share by reporting month."""
    return panel.groupby("period", as_index=False).agg(loans_at_risk=("loan_identifier", "nunique"), voluntary_prepayment_rate=("voluntary_prepayment", "mean"))

def plot_monthly_prepayment(panel: pd.DataFrame):
    summary = monthly_prepayment_summary(panel)
    figure, axis = plt.subplots(figsize=(8, 4))
    axis.plot(summary["period"], summary["voluntary_prepayment_rate"], marker="o")
    axis.set(title="Observed monthly voluntary-prepayment incidence", ylabel="Share of loan-months", xlabel="Reporting month")
    return figure
