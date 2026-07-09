import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models import Client, Organization
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy import select

router = APIRouter(prefix="/clients", tags=["clients"])
class ClientCreate(BaseModel):
    org_id: uuid.UUID
    company_name:str
    email: str
    industry:str
    notes: str | None = None

class ClientOut(BaseModel):
    org_id: uuid.UUID
    id: uuid.UUID
    company_name: str
    industry: str
    notes: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("",response_model=ClientOut)
async def create_client(payload: ClientCreate,db:AsyncSession = Depends(get_db)):
    org = await db.get(Organization,payload.org_id)
    if org is None:
        raise HTTPException(status_code=404,detail='Organization not found')
    
    client = Client(
        org_id = payload.org_id,
        company_name = payload.company_name,
        email = payload.email,
        industry = payload.industry,
        notes = payload.notes

    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client



@router.get("",response_model=list[ClientOut])
async def list_clients(org_id: uuid.UUID | None = Query(default=None),db:AsyncSession = Depends(get_db)):
    query = select(Client)
    if org_id is not None:
        query = query.where(Client.org_id == org_id)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{client_id}",response_model=ClientOut)
async def get_clients(client_id:uuid.UUID,db:AsyncSession = Depends(get_db)):
    client = await db.get(Client,client_id)
    if client is None:
        raise HTTPException(status_code=404,detail="Not able to find the Client")
    return client



    






