"""
Billing code models (CPT, ICD-10, HCPCS, DRG, NDC).
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import Base


class CodeType(str, Enum):
    """Types of medical billing codes."""
    CPT = "CPT"
    ICD10 = "ICD-10"
    HCPCS = "HCPCS"
    DRG = "DRG"
    NDC = "NDC"


class BillingCode(Base):
    """
    Medical billing codes for procedures, diagnoses, and products.
    """
    __tablename__ = "billing_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), nullable=False, index=True, unique=True)
    code_type = Column(Enum(CodeType), nullable=False, index=True)
    description = Column(Text, nullable=True)
    effective_date = Column(DateTime, nullable=False, index=True)
    termination_date = Column(DateTime, nullable=True, index=True)
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True, index=True)
    status = Column(String(50), nullable=False, default="active", index=True)
    
    # Relationships
    relationships = relationship("CodeRelationship", back_populates="source_code")
    related_to = relationship("CodeRelationship", foreign_keys=[ "target_code_id"], back_populates="target_code")
    claims = relationship("Claim", back_populates="claims")
    
    def __repr__(self):
        return f"<BillingCode {self.code_type.value} {self.code} ({self.status})>"


class CodeRelationship(Base):
    """
    Relationships between billing codes (bundling, mutually exclusive, required together).
    """
    __tablename__ = "code_relationships"

    id = Column(Integer, primary_key=True)
    source_code_id = Column(Integer, ForeignKey("billing_codes.id"), nullable=False, index=True)
    target_code_id = Column(Integer, ForeignKey("billing_codes.id"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False, index=True)
    condition = Column(String(255), nullable=True)
    
    # Relationships
    source_code = relationship("BillingCode", foreign_keys=[source_code_id])
    target_code = relationship("BillingCode", foreign_keys=[target_code_id])
    
    def __repr__(self):
        return f"<{self.source_code.code} {self.relationship_type} {self.target_code.code}>"
