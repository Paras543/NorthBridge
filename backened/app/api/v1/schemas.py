from pydantic import BaseModel
class StartCase(BaseModel):
    raw_brief:str
    project_id:str

class ResumeCase(BaseModel):
    approved:bool
    request_changes:list[str] | None = None

class CaseState(BaseModel):
    thread_id:str
    status:str
    data:dict | None = None

