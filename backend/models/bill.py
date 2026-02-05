"""
Medical bill model for claims processing.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .billing_code import BillingCode
from .provider import Provider
from .insurer import Insurer


class BillStatus(str, Enum):
    """Status of bill processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    VERIFIED = "verified"
    FLAGGED = "flagged"
    INVESTIGATED = "investigated"
    REJECTED = "rejected"
    PAID = "paid"


class Bill(Base):
    """
    Medical bill for fraud detection and compliance verification.
    """
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), nullable=False, index=True, comment="Patient identifier")
    claim_id = Column(String(100), nullable=False, index=True, unique=True, comment="Unique claim identifier")
    bill_date = Column(DateTime, nullable=False, index=True, comment="Date of service")
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False, index=True, comment="Provider NPI")
    insurer_id = Column(Integer, ForeignKey("insurers.id"), nullable=False, index=True, comment="Insurer ID")
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True, index=True, comment="Hospital ID if applicable")
    
    # Billing codes
    procedure_code = Column(String(20), nullable=False, index=True, comment="CPT procedure code")
    diagnosis_code = Column(String(10), nullable=True, index=True, comment="ICD-10 diagnosis code")
    hcpcs_code = Column(String(10), nullable=True, index=True, comment="HCPCS code")
    ndc_code = Column(String(15), nullable=True, comment="NDC drug code")
    
    # Financial
    billed_amount = Column(Float, nullable=False, comment="Amount billed")
    allowed_amount = Column(Float, nullable=True, comment="Allowed amount per payer")
    paid_amount = Column(Float, nullable=True, comment="Actual paid amount")
    
    # Status
    status = Column(Enum(BillStatus), nullable=False, default=BillStatus.PENDING, index=True, comment="Bill status")
    status_date = Column(DateTime, nullable=True, index=True, comment="Date of last status change")
    
    # Fraud and compliance
    fraud_score = Column(Float, nullable=True, comment="Fraud probability score (0-1)")
    fraud_indicators = Column(Text, nullable=True, comment="JSON of detected fraud patterns")
    compliance_issues = Column(Text, nullable=True, comment="JSON of compliance violations")
    medical_necessity_score = Column(Float, nullable=True, comment="Medical necessity score")
    
    # Documentation
    documentation_text = Column(Text, nullable=True, comment="Clinical documentation")
    
    # Relationships
    provider = relationship("Provider", foreign_keys=[provider_id])
    insurer = relationship("Insurer", foreign_keys=[insurer_id])
    hospital = relationship("Hospital", foreign_keys=[hospital_id])
    
    # Knowledge graph
    graph_id = Column(String(100), nullable=True, comment="Neo4j node ID")
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Bill {self.claim_id}: ${self.billed_amount} ({self.status})>"
