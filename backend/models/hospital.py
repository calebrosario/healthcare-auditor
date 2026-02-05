"""
Hospital model for healthcare facilities.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .provider import Provider


class HospitalType(str, Enum):
    """Types of hospitals."""
    ACUTE_CARE = "acute_care"
    GENERAL_ACUTE = "general_acute"
    PSYCHIATRIC = "psychiatric"
    REHABILITATION = "rehabilitation"
    LONG_TERM_CARE = "long_term_care"
    CRITICAL_ACCESS = "critical_access"
    CHILDREN = "children"
    SPECIALTY = "specialty"


class Hospital(Base):
    """
    Hospital facility for knowledge graph.
    """
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    npi = Column(String(20), nullable=False, unique=True, index=True, comment="National Provider Identifier")
    name = Column(String(255), nullable=False, index=True, comment="Hospital name")
    hospital_type = Column(Enum(HospitalType), nullable=False, index=True, comment="Type of hospital")
    address = Column(Text, nullable=True, comment="Full address")
    city = Column(String(100), nullable=True, index=True, comment="City")
    state = Column(String(2), nullable=False, index=True, comment="State code")
    zip_code = Column(String(10), nullable=True, index=True, comment="ZIP code")
    phone = Column(String(20), nullable=True, comment="Phone number")
    bed_count = Column(Integer, nullable=True, comment="Number of beds")
    specialty = Column(String(100), nullable=True, index=True, comment="Hospital specialty")
    accreditation = Column(String(100), nullable=True, index=True, comment="Accreditation status")
    accreditation_expiration = Column(DateTime, nullable=True, comment="Accreditation expiration")
    ownership_type = Column(String(50), nullable=True, index=True, comment="For-profit, non-profit, government")
    tax_id = Column(String(50), nullable=True, index=True, comment="Tax identifier")
    
    # Knowledge graph properties
    graph_id = Column(String(100), nullable=True, comment="Neo4j node ID")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # Relationships
    providers = relationship("Provider", secondary="hospital_provider", back_populates="providers")
    claims = relationship("Claim", back_populates="hospital_claims")
    alerts = relationship("Alert", back_populates="hospital_alerts")
    
    def __repr__(self):
        return f"<Hospital {self.npi}: {self.name} ({self.hospital_type})>"
