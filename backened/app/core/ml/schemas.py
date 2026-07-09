from pydantic import BaseModel



class ForecastPoint(BaseModel):
    date: str
    predicted:float
    lower_bound:float
    upper_bound:float

class ForecastResult(BaseModel):
    metric_name:str
    historical_points: int
    forecast:list[ForecastPoint]
    trend_direction: str


class ClusterProfile(BaseModel):
    cluster_id:int
    size:int
    description:str
    representative_stats:dict[str,float]

class SegmentationResult(BaseModel):
    n_clusters:int
    profiles: list[ClusterProfile]

class DriverResult(BaseModel):
    feature:str
    importance:float
    direction:str

class DriverAnalysisResult(BaseModel):
    target_variable:str
    drivers:list[DriverResult]

class MLValidationError(Exception):
    """Raised when the DataFrame doesn't have what a model needs. Caught
    by ml_context.py and treated as 'no ML grounding available' — never
    bubbles up to crash a specialist node."""


