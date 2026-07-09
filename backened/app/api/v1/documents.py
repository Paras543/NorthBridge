"""
This endpoint will help in Uploading the file and getting from the endpoint
"""

import uuid
from pydantic import BaseModel
from fastapi import UploadFile, HTTPException, Depends, APIRouter, File, Form, Query
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import Project, Document, DocumentChunk
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.extraction import extract_text, ExtractionError
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts, EmbeddingError



router = APIRouter(prefix="/documents", tags=['documents'])


class DocumentOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    description: str | None
    embedding_status: str
    content_type: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=DocumentOut)
async def upload_document(
    project_id: uuid.UUID = Form(...),
    description: str | None = Form(default=None),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail='Project not found')

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail='Uploaded file is empty')

    content_type = file.content_type or "application/octet-stream"

    
    try:
        extracted_text = extract_text(raw_bytes, content_type, file.filename)
        embedding_status = "extracted"
    except ExtractionError:
        extracted_text = None
        embedding_status = "extraction_failed"

    document = Document(
        project_id=project_id,
        description=description,
        name=file.filename,
        content_type=content_type,
        raw_content=raw_bytes,
        extracted_text=extracted_text,
        embedding_status=embedding_status,
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    
    if extracted_text:
        chunks = chunk_text(extracted_text)

        if chunks:
            try:
                vectors = embed_texts(chunks)

                for idx, (chunk_content, vector) in enumerate(zip(chunks, vectors)):
                    db_chunk = DocumentChunk(
                        document_id=document.id,
                        chunk_index=idx,
                        content=chunk_content,
                        embedding=vector,
                    )
                    db.add(db_chunk)

                document.embedding_status = "embedded"

            except EmbeddingError:
                document.embedding_status = "embedding_failed"

        else:
            document.embedding_status = "no_chunks"

        await db.commit()
        await db.refresh(document)

    return document


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    project_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Document)
    if project_id is not None:
        query = query.where(Document.project_id == project_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


