"""
How the data is being loaded and will pass out to my machine Learning algorithms
"""

import io
import uuid
import pandas as pd
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import Document

STRUCTURED_CONTENT_TYPES = {
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
STRUCTURED_EXTENSIONS = (".csv", ".xls", ".xlsx")


def _is_structured(document: Document) -> bool:
    if document.content_type in STRUCTURED_CONTENT_TYPES:
        return True
    return document.name.lower().endswith(STRUCTURED_EXTENSIONS)


async def load_project_dataset(project_id: str, document_id: str | None = None) -> pd.DataFrame | None:
    """
    Loads the most relevant structured file for a project into a DataFrame.

    If document_id is given, loads that specific document (must be
    structured). Otherwise picks the most recently uploaded structured
    file in the project — good enough for now; if a project ever has
    multiple structured datasets that need combining, that's a future
    problem for whoever calls this to solve at a higher level, not
    something this loader should silently guess at.
    """
    try:
        project_uuid = uuid.UUID(project_id)
    except (ValueError, TypeError):
        return None

    async with AsyncSessionLocal() as db:
        stmt = select(Document).where(Document.project_id == project_uuid)
        if document_id:
            try:
                stmt = stmt.where(Document.id == uuid.UUID(document_id))
            except ValueError:
                return None
        else:
            stmt = stmt.order_by(Document.uploaded_at.desc())

        result = await db.execute(stmt)
        documents = result.scalars().all()

    structured_docs = [d for d in documents if _is_structured(d)]
    if not structured_docs:
        return None

    doc = structured_docs[0] 

    try:
        buffer = io.BytesIO(doc.raw_content)
        if doc.name.lower().endswith(".csv") or doc.content_type in ("text/csv", "application/csv"):
            df = pd.read_csv(buffer)
        else:
            df = pd.read_excel(buffer)
    except Exception:
        return None  

    if df.empty:
        return None

    return df







