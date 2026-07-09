import pandas as pd
# pyrefly: ignore [missing-import]
from prophet import Prophet
from app.core.ml.schemas import ForecastPoint,ForecastResult,MLValidationError


MIN_ROWS_FOR_FORECAST = 10

def _detect_date_coloumn(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower() or "period" in col.lower():
            return col
        
    try:
        pd.to_datetime(df.iloc[:,0])
        return df.columns[0]
    except Exception:
        return None 
    

def _detect_value_coloumn(df:pd.DataFrame,exclude:str) -> str | None:
    numeric_cols = [
        c for c in df.select_dtypes(include="number").columns if c != exclude
    ]
    if not numeric_cols:
        return None
    
    for keyword in ['revenue','sales','value','amount']:
        for col in numeric_cols:
            if keyword in col.lower():
                return col
    return numeric_cols[-1]


def run_forecast(
        df:pd.DataFrame,
        date_col: str | None = None,
        value_col: str | None = None,
        period: int = 6
) -> ForecastResult:
    
    date_col = date_col or _detect_date_coloumn(df)
    if date_col is None:
        raise MLValidationError("No usable date/time column found in dataset.")
    value_col = value_col or _detect_value_coloumn(df,exclude=date_col)
    if value_col is None:
        raise MLValidationError("No usable numeric column found for forecasting.")
    


    working  = df[[date_col,value_col]].dropna()
    working.columns = ['ds','y']

    try:
        working["ds"] = pd.to_datetime(working["ds"])
    except Exception:
        raise MLValidationError(f"Column '{date_col}' could not be parsed as dates.")

    if len(working) < MIN_ROWS_FOR_FORECAST:
        raise MLValidationError(
            f"Only {len(working)} usable rows found; need at least {MIN_ROWS_FOR_FORECAST} for a reliable forecast."
        )
    
    model = Prophet()
    model.fit(working)

    future = model.make_future_dataframe(periods=period,freq="M")
    forecast_df = model.predict(future)
    forecast_only = forecast_df.tail(period)

    points = [
        ForecastPoint(
            date=row["ds"].strftime("%Y-%m-%d"),
            predicted=round(row["yhat"], 2),
            lower_bound=round(row["yhat_lower"], 2),
            upper_bound=round(row["yhat_upper"], 2),
        )
        for _, row in forecast_only.iterrows()
    ]

    first_val, last_val = working["y"].iloc[0], working["y"].iloc[-1]
    if last_val > first_val * 1.05:
        trend = "increasing"
    elif last_val < first_val * 0.95:
        trend = "decreasing"
    else:
        trend = "flat"


    return ForecastResult(
        metric_name=value_col,
        historical_points=len(working),
        forecast=points,
        trend_direction=trend,
    )

    








    
    
    
    