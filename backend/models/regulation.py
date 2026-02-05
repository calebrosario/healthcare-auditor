"""
Regulation model for healthcare laws and policies.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class RegulationType(str, Enum):
    """Types of healthcare regulations."""
    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"
    INDUSTRY_STANDARD = "industry_standard"


class RegulationCategory(str, Enum):
    """Categories of regulations."""
    BILLING = "billing"
    PRIVACY = "privacy"
    SECURITY = "security"
    ANTI_KICKBACK = "anti_kickback"
    STARK_LAW = "stark_law"
    HIPAA = "hipaa"
    ACA = "aca"
    NO_SURPRISES = "no_surprises"


class Regulation(Base):
    """
    Healthcare regulations for compliance verification.
    """
    __tablename__ = "regulations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, index=True, comment="Regulation code (e.g., HIPAA_2003_164)")
    name = Column(String(255), nullable=False, index=True, comment="Regulation name")
    regulation_type = Column(Enum(RegulationType), nullable=False, index=True, comment="Federal, state, local, or industry")
    category = Column(Enum(RegulationCategory), nullable=False, index=True, comment="Category of regulation")
    description = Column(Text, nullable=True, comment="Full description")
    requirements = Column(Text, nullable=True, comment="Compliance requirements")
    effective_date = Column(DateTime, nullable=False, index=True, comment="Effective date")
    expiration_date = Column(DateTime, nullable=True, index=True, comment="Expiration date if applicable")
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="Whether regulation is currently active")
    source_url = Column(String(500), nullable=True, comment="URL to official source")
    
    # Relationships
    bill_checks = relationship("ComplianceCheck", back_populates="bill_compliance_checks")
    provider_requirements = relationship("ComplianceCheck", back_populates="provider_compliance_checks")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Regulation {self.code}: {self.name} ({self.category})>"
