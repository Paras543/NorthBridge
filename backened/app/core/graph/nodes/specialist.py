from app.llm.client import llm
from app.core.graph.state import CaseState
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.graph.schemas import SpecialistReport
from app.services.specialist_context import get_context_for_project
from app.core.ml.ml_context import get_segments_for_project, get_forecast_for_project, get_drivers_for_project


async def market_analyst(state: CaseState) -> CaseState:
    rag_context = await get_context_for_project(
        query="market sizing, competitive landscape, demand trends",
        project_id=state['project_id'],
    )
    segments = await get_segments_for_project(project_id=state['project_id'])

    ml_summary = (
        f"Segmentation found {segments['n_clusters']} client/customer segments."
        if segments else "No structured data available for segmentation."
    )

    market_report = llm.with_structured_output(SpecialistReport)
    market_report = await market_report.ainvoke([
        SystemMessage(content=(
            "You are a market analyst at a consulting firm. Given the client's brief, "
            "any supporting documents, and any segmentation analysis provided, assess "
            "market sizing, competitive landscape, and demand trends relevant to their "
            "decision. If segmentation data is provided, reference the segment "
            "descriptions in your findings — do not invent numbers not present in the data. "
            "Return your findings, key metrics, and the assumptions your analysis relies on."
        )),
        HumanMessage(content=(
            f"Client brief:\n{state['client_brief'].model_dump_json()}\n\n"
            f"Supporting documents (may be empty if none uploaded yet):\n{rag_context}\n\n"
            f"Segmentation analysis:\n{ml_summary}"
        ))
    ])

    market_report.supporting_data = segments  
    return {'market_report': market_report}


async def Financial_analyst(state: CaseState) -> CaseState:
    rag_context = await get_context_for_project(
        query="unit economics, ROI, breakeven timeline, financial feasibility",
        project_id=state['project_id'],
    )
    forecast = await get_forecast_for_project(project_id=state['project_id'])
    driver_analysis = await get_drivers_for_project(project_id=state['project_id'])

    ml_summary_parts = []
    if forecast:
        ml_summary_parts.append(
            f"Forecast for '{forecast['metric_name']}': trend is {forecast['trend_direction']}, "
            f"based on {forecast['historical_points']} historical data points."
        )
    if driver_analysis:
        top_drivers = ", ".join(d["feature"] for d in driver_analysis["drivers"][:3])
        ml_summary_parts.append(f"Top drivers of '{driver_analysis['target_variable']}': {top_drivers}.")
    ml_summary = " ".join(ml_summary_parts) or "No structured data available for forecasting or driver analysis."

    financial_report = llm.with_structured_output(SpecialistReport)
    financial_report = await financial_report.ainvoke([
        SystemMessage(content=(
            "You are a financial analyst at a consulting firm. Given the client's brief, "
            "any supporting documents, and any forecasting or driver analysis provided, "
            "assess unit economics, ROI, breakeven timeline, and financial feasibility "
            "relevant to their decision. If forecast or driver data is provided, ground "
            "your findings in it and reference the actual trend/drivers — do not invent "
            "numbers not present in the data. Return your findings, key metrics, and the "
            "assumptions your analysis relies on."
        )),
        HumanMessage(content=(
            f"Client brief:\n{state['client_brief'].model_dump_json()}\n\n"
            f"Supporting documents (may be empty if none uploaded yet):\n{rag_context}\n\n"
            f"Quantitative analysis:\n{ml_summary}"
        ))
    ])

    financial_report.supporting_data = {
        "forecast": forecast,
        "drivers": driver_analysis,
    }
    return {'financial_report': financial_report}


async def Risk_ops(state: CaseState) -> CaseState:
    rag_context = await get_context_for_project(
        query="execution feasibility, resource and timeline constraints, regulatory or market risks",
        project_id=state['project_id'],
    )

    risk_ops = llm.with_structured_output(SpecialistReport)
    risk_ops = await risk_ops.ainvoke([
        SystemMessage(content=(
            "You are a risk and operations analyst at a consulting firm. Given the client's "
            "brief and any supporting documents provided, assess execution feasibility, "
            "resource and timeline constraints, and regulatory or market risks relevant to "
            "their decision. Return your findings, key metrics, and the assumptions your "
            "analysis relies on."
        )),
        HumanMessage(content=(
            f"Client brief:\n{state['client_brief'].model_dump_json()}\n\n"
            f"Supporting documents (may be empty if none uploaded yet):\n{rag_context}"
        ))
    ])

    risk_ops.supporting_data = None  
    return {'Risk_report': risk_ops}



