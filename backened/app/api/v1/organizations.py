"""
When in the onboarding form we will tell to create the organization thus this the 

"""
from pydantic import BaseModel
import uuid
from datetime import datetime
from fastapi import APIRouter , HTTPException,Depends

from app.db.models import Organization
from sqlalchemy import select
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

class OrganizationCreate(BaseModel):
    name: str

class OrganizationOut(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime

    class Config:
        from_attributes = True



router = APIRouter(prefix="/organizations",tags=['organizations'])

@router.post("/",response_model=OrganizationOut)
async def create_organization(payload:OrganizationCreate,db:AsyncSession=Depends(get_db)):
    org = Organization(name=payload.name)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@router.get("",response_model=list[OrganizationOut])
async def list_organizations(db:AsyncSession=Depends(get_db)):
    result = await db.execute(select(Organization))
    return result.scalars().all()

@router.get("/{org_id}",response_model=OrganizationOut)
async def get_organization(org_id:uuid.UUID,db:AsyncSession=Depends(get_db)):
    org = await db.get(Organization,org_id)
    if not org:
        raise HTTPException(status_code=404,detail="Organization not found")
    return org 







