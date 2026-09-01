"""Interpretable discrete-time prepayment model and chronological validation."""
from __future__ import annotations
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DEFAULT_FEATURES = ["refinance_incentive_pct", "loan_age", "age_squared", "season"]
def chronological_split(panel: pd.DataFrame, cutoff: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    point = pd.Timestamp(cutoff); return panel[panel.period < point].copy(), panel[panel.period >= point].copy()
def fit_hazard_model(train: pd.DataFrame, features: list[str] = DEFAULT_FEATURES) -> Pipeline:
    numeric=[x for x in features if pd.api.types.is_numeric_dtype(train[x])]; categorical=[x for x in features if x not in numeric]
    prep=ColumnTransformer([("num", Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())]),numeric),("cat",Pipeline([("impute",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),categorical)])
    return Pipeline([("prep",prep),("model",LogisticRegression(max_iter=1000, class_weight="balanced"))]).fit(train[features],train["voluntary_prepayment"].astype(int))
def evaluate(model: Pipeline, test: pd.DataFrame, features: list[str] = DEFAULT_FEATURES) -> dict[str,float]:
    y=test.voluntary_prepayment.astype(int); p=model.predict_proba(test[features])[:,1]
    return {"brier":float(brier_score_loss(y,p)),"roc_auc":float(roc_auc_score(y,p)),"average_precision":float(average_precision_score(y,p)),"n":float(len(test))}
