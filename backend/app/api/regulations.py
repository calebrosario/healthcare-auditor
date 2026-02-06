"""
Healthcare regulations API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..models.regulation import Regulation, RegulationCategory, RegulationType


router = APIRouter()


class RegulationResponse(BaseModel):
    """Regulation response."""
    id: int
    code: str
    name: str
    regulation_type: str
    category: str
    description: Optional[str]
    effective_date: str
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("", response_model=List[RegulationResponse])
async def get_regulations(
    regulation_type: Optional[RegulationType] = None,
    category: Optional[RegulationCategory] = None,
    is_active: Optional[bool] = True,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get healthcare regulations with optional filters.
    """
    return []


@router.get("/{code}", response_model=RegulationResponse)
async def get_regulation(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific regulation by code.
    """
    raise HTTPException(status_code=404, detail="Regulation not found - TODO: Implement database")


@router.get("/categories")
async def get_regulation_categories():
    """
    Get available regulation categories.
    """
    return {
        "categories": [
            {"value": "billing", "label": "Billing"},
            {"value": "privacy", "label": "Privacy"},
            {"value": "security", "label": "Security"},
            {"value": "anti_kickback", "label": "Anti-Kickback"},
            {"value": "stark_law", "label": "Stark Law"},
            {"value": "hipaa", "label": "HIPAA"},
            {"value": "aca", "label": "ACA"},
            {"value": "no_surprises", "label": "No Surprises Act"}
        ]
    }
