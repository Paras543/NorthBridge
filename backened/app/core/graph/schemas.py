"""
Here in the Schemas.py file we write the pydantic Objects in the file for getting the strcutured output
"""

from pydantic import BaseModel, Field
from typing import Literal,Annotated,Optional

class ClientBrief(BaseModel):
    core_question: str = Field(...,description="Enter the Cases that you are being faced and wants to be resolved")
    problem_type:Literal[
        "growth_expansion",
        "cost_reduction",
        "customer_retention",
        "pricing",
        "operational_efficiency",
        "market_entry",
        "risk_assessment",
        "other"
    ]
    has_data:bool
    urgency:Literal["low","medium","high"] = "medium"
    data_description: str | None = None
    constraints: list[str] = Field(default_factory=list)
    

class SpecialistReport(BaseModel):
    specialist: Literal['market','financial','risk','operation']
    key_metrics:dict[str,float] = Field(default_factory=dict)
    assumptions: str
    findings: list[str]
    confidence: Literal['high','low','moderate']
    supporting_data: dict | None = None
    


class ChallengeCritique(BaseModel):
    target_specialist: Literal['market','financial','risk','operation']
    target_assumption : str
    critique: str
    severity : Literal['minor','moderate','major']


class FinalRecommendation(BaseModel):
    recommendations: str
    supporting_points: list[str]
    disagreements: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)

class HumanFeedback(BaseModel):
    approved:bool
    requested_changes: list[str] = Field(default_factory=list)
    target_sections: Literal['market','financial','risk','operation'] | None = None

class RevisionDecision(BaseModel):
    changed_meaningfully: bool
    reasoning: str
    continue_loop: bool
    round_number: int


