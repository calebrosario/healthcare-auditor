"""
Compliance check model for validating bills against regulations.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .regulation import Regulation
from .bill import Bill


class ComplianceStatus(str, Enum):
    """Status of compliance check."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"
    REVIEW_REQUIRED = "review_required"


class ComplianceCheck(Base):
    """
    Validation of bills against healthcare regulations.
    """
    __tablename__ = "compliance_checks"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False, index=True, comment="Associated bill")
    regulation_id = Column(Integer, ForeignKey("regulations.id"), nullable=False, index=True, comment="Associated regulation")
    check_type = Column(String(100), nullable=False, index=True, comment="Type of compliance check")
    description = Column(Text, nullable=True, comment="Check description")
    status = Column(Enum(ComplianceStatus), nullable=False, default=ComplianceStatus.PENDING, index=True, comment="Compliance status")
    details = Column(Text, nullable=True, comment="Detailed findings")
    checked_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True, comment="When check was performed")
    checked_by = Column(String(100), nullable=True, comment="System or user who performed check")
    
    # Relationships
    bill = relationship("Bill", foreign_keys=[bill_id])
    regulation = relationship("Regulation", foreign_keys=[regulation_id])
    
    def __repr__(self):
        return f"<ComplianceCheck {self.check_type}: {self.status}>"
