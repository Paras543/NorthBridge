"""
Acts as the entry point for the evauuation of the specialiast report basically it eneures that the data has to be passed to the ml model or the rag 
"""

import logging
from app.core.ml.data_loader import load_project_dataset
from app.core.ml.schemas import MLValidationError
from app.core.ml import forecasting, segmentation, drivers

logger = logging.getLogger("app.ml")


async def get_forecast_for_project(project_id: str, **kwargs) -> dict | None:
    df = await load_project_dataset(project_id)
    if df is None:
        logger.info("forecast skipped: no structured dataset for project %s", project_id)
        return None
    try:
        return forecasting.run_forecast(df, **kwargs).model_dump()
    except MLValidationError as e:
        logger.warning("forecast validation failed for project %s: %s", project_id, e)
        return None
    except Exception:
        logger.exception("forecast raised an unexpected error for project %s", project_id)
        return None


async def get_segments_for_project(project_id: str, **kwargs) -> dict | None:
    df = await load_project_dataset(project_id)
    if df is None:
        logger.info("segmentation skipped: no structured dataset for project %s", project_id)
        return None
    try:
        return segmentation.run_segmentation(df, **kwargs).model_dump()
    except MLValidationError as e:
        logger.warning("segmentation validation failed for project %s: %s", project_id, e)
        return None
    except Exception:
        logger.exception("segmentation raised an unexpected error for project %s", project_id)
        return None


async def get_drivers_for_project(project_id: str, **kwargs) -> dict | None:
    df = await load_project_dataset(project_id)
    if df is None:
        logger.info("driver analysis skipped: no structured dataset for project %s", project_id)
        return None
    try:
        return drivers.run_driver_analysis(df, **kwargs).model_dump()
    except MLValidationError as e:
        logger.warning("driver analysis validation failed for project %s: %s", project_id, e)
        return None
    except Exception:
        logger.exception("driver analysis raised an unexpected error for project %s", project_id)
        return None
    

