"""
Insurance company model for payers.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class CoverageType(str, Enum):
    """Types of insurance coverage."""
    MEDICARE = "medicare"
    MEDICAID = "medicaid"
    COMMERCIAL = "commercial"
    TRICARE = "tricare"
    CHAMPUS = "champus"
    VA = "va"


class Insurer(Base):
    """
    Insurance company for knowledge graph.
    """
    __tablename__ = "insurers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True, comment="Insurer name")
    payer_id = Column(String(50), nullable=True, index=True, unique=True, comment="Payer identifier")
    coverage_type = Column(Enum(CoverageType), nullable=False, index=True, comment="Type of coverage")
    state_license = Column(String(20), nullable=True, index=True, comment="State license number")
    license_status = Column(String(20), nullable=True, default="active", index=True, comment="License status")
    license_expiration = Column(DateTime, nullable=True, index=True, comment="License expiration")
    address = Column(Text, nullable=True, comment="Address")
    city = Column(String(100), nullable=True, index=True, comment="City")
    state = Column(String(2), nullable=False, index=True, comment="State")
    zip_code = Column(String(10), nullable=True, index=True, comment="ZIP code")
    contact_email = Column(String(255), nullable=True, index=True, comment="Contact email")
    contact_phone = Column(String(20), nullable=True, comment="Contact phone")
    
    # Network properties
    provider_networks = relationship("Provider", secondary="insurer_provider", back_populates="providers")
    claims = relationship("Claim", back_populates="insurer_claims")
    alert_subscriptions = relationship("AlertSubscription", back_populates="alert_subscriptions")
    
    # Knowledge graph properties
    graph_id = Column(String(100), nullable=True, comment="Neo4j node ID")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Insurer {self.payer_id}: {self.name} ({self.coverage_type.value})>"
