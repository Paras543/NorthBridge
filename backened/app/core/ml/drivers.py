"""
Regression + SHAP driver analysis, fit fresh per project. Validates a
target column exists and there's enough signal before running.
"""

import pandas as pd
import shap
from sklearn.ensemble import RandomForestRegressor
from app.core.ml.schemas import DriverAnalysisResult, DriverResult, MLValidationError

MIN_ROWS_FOR_DRIVERS = 15


def _detect_target_column(df: pd.DataFrame) -> str | None:
    numeric_cols = list(df.select_dtypes(include="number").columns)
    for keyword in ("revenue", "sales", "profit", "churn", "conversion"):
        for col in numeric_cols:
            if keyword in col.lower():
                return col
    return numeric_cols[-1] if numeric_cols else None


def run_driver_analysis(df: pd.DataFrame, target_col: str | None = None) -> DriverAnalysisResult:
    target_col = target_col or _detect_target_column(df)
    if target_col is None:
        raise MLValidationError("No numeric target column found or specified for driver analysis.")
    if target_col not in df.columns:
        raise MLValidationError(f"Specified target column '{target_col}' not found in dataset.")

    numeric_df = df.select_dtypes(include="number").dropna()
    if target_col not in numeric_df.columns:
        raise MLValidationError(f"Target column '{target_col}' is not numeric.")

    if len(numeric_df) < MIN_ROWS_FOR_DRIVERS:
        raise MLValidationError(
            f"Only {len(numeric_df)} usable rows found; need at least {MIN_ROWS_FOR_DRIVERS} for driver analysis."
        )

    feature_cols = [c for c in numeric_df.columns if c != target_col]
    if not feature_cols:
        raise MLValidationError("No feature columns available besides the target.")

    X = numeric_df[feature_cols]
    y = numeric_df[target_col]

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    mean_abs_shap = pd.Series(
        abs(shap_values).mean(axis=0), index=feature_cols
    ).sort_values(ascending=False)

    correlations = X.corrwith(y)

    drivers = [
        DriverResult(
            feature=feature,
            importance=round(float(importance), 4),
            direction="increases" if correlations.get(feature, 0) >= 0 else "decreases",
        )
        for feature, importance in mean_abs_shap.items()
    ]

    return DriverAnalysisResult(target_variable=target_col, drivers=drivers)


