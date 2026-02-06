"""
Medical bills/claims API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..core.neo4j import get_neo4j
from ...models.bill import Bill, BillStatus
from ..security import require_auth


router = APIRouter()


class BillResponse(BaseModel):
    """Bill/Claim response."""
    id: int
    claim_id: str
    bill_date: datetime
    billed_amount: float
    status: str
    fraud_score: Optional[float]
    
    class Config:
        from_attributes = True


class BillValidationRequest(BaseModel):
    """Request to validate a bill."""
    patient_id: str
    provider_npi: str
    insurer_id: int
    procedure_code: str
    diagnosis_code: Optional[str] = None
    billed_amount: float
    bill_date: datetime


class BillValidationResponse(BaseModel):
    """Response with validation results."""
    claim_id: str
    fraud_score: float
    fraud_risk_level: str
    compliance_score: float
    issues: List[str]
    warnings: List[str]


@router.post("", response_model=BillResponse)
async def create_bill(
    bill_data: dict,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_auth)
):
    """
    Create a new medical bill/claim.
    """
    # TODO: Implement bill creation
    # 1. Validate bill data
    # 2. Insert into database
    # 3. Trigger fraud detection analysis
    # 4. Create compliance checks
    raise HTTPException(status_code=501, detail="Not implemented - TODO")


@router.get("", response_model=List[BillResponse])
async def get_bills(
    patient_id: Optional[str] = None,
    provider_npi: Optional[str] = None,
    status: Optional[BillStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get bills/claims with optional filters.
    """
    return []


@router.get("/{claim_id}", response_model=BillResponse)
async def get_bill(
    claim_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific bill by claim ID.
    """
    raise HTTPException(status_code=404, detail="Bill not found - TODO: Implement database")


@router.post("/validate", response_model=BillValidationResponse)
async def validate_bill(
    bill: BillValidationRequest,
    db: AsyncSession = Depends(get_db),
    neo4j: AsyncSession = Depends(get_neo4j),
    user_id: str = Depends(require_auth)
):
    """
    Validate a bill against fraud detection and compliance rules.
    
    This triggers the full analysis pipeline:
    1. Rule-based validation
    2. Statistical anomaly detection
    3. ML-based fraud scoring
    4. Network analysis
    5. Compliance checks
    """
    from ..core.rules_engine import RuleEngine
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    # Find bill by claim ID (or patient_id + provider_id + date)
    stmt = select(Bill).where(
        (Bill.patient_id == bill.patient_id) &
        (Bill.provider_id == bill.provider_id) &
        (Bill.bill_date == bill.bill_date)
    ).options(selectinload(Bill.provider))
    
    result = await db.execute(stmt)
    bill_record = result.scalar_one_or_none()

    if not bill_record:
        raise HTTPException(status_code=404, detail=f"Bill not found: patient_id={bill.patient_id}")

    # Create rules engine and evaluate
    engine = RuleEngine(db, neo4j)
    evaluation_result = await engine.evaluate_bill(bill_record.claim_id)

    # Determine risk level
    if evaluation_result.chain_result.fraud_score >= 0.8:
        risk_level = "high"
    elif evaluation_result.chain_result.fraud_score >= 0.5:
        risk_level = "medium"
    else:
        risk_level = "low"

    return BillValidationResponse(
        claim_id=evaluation_result.chain_result.claim_id,
        fraud_score=evaluation_result.chain_result.fraud_score,
        fraud_risk_level=risk_level,
        compliance_score=evaluation_result.chain_result.compliance_score,
        issues=evaluation_result.chain_result.issues,
        warnings=evaluation_result.chain_result.warnings
    )


@router.get("/{claim_id}/compliance")
async def get_bill_compliance(
    claim_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get compliance status for a bill.
    """
    return {
        "claim_id": claim_id,
        "compliance_checks": [],
        "violations": [],
        "compliance_score": 1.0
    }
