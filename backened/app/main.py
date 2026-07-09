from fastapi import FastAPI, Depends

from app.api.v1.consultations import router as consultations_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.clients import router as clients_router
from app.api.v1.projects import router as projects_router
from app.api.v1.documents import router as documents_router
from app.api.v1.retrieval import router as retrieval_router
from app.auth.dependencies import get_current_user

app = FastAPI(title="AI Consulting Platform API")

_auth = [Depends(get_current_user)]

app.include_router(consultations_router, prefix="/api/v1", dependencies=_auth)
app.include_router(organizations_router, prefix="/api/v1", dependencies=_auth)
app.include_router(clients_router,       prefix="/api/v1", dependencies=_auth)
app.include_router(projects_router,      prefix="/api/v1", dependencies=_auth)
app.include_router(documents_router,     prefix="/api/v1", dependencies=_auth)
app.include_router(retrieval_router,     prefix="/api/v1", dependencies=_auth)


@app.get("/health")
def health():
    return {"status": "ok"}
