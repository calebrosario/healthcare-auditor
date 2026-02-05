"""
Healthcare provider model (doctors, clinics, hospitals, imaging centers).
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, Enum, Index
from sqlalchemy.orm import relationship
from .base import Base


class ProviderType(str, Enum):
    """Types of healthcare providers."""
    INDIVIDUAL = "individual"
    HOSPITAL = "hospital"
    IMAGING_CENTER = "imaging_center"
    LABORATORY = "laboratory"
    CLINIC = "clinic"
    NURSING_FACILITY = "nursing_facility"
    URGENT_CARE = "urgent_care"


class Provider(Base):
    """
    Healthcare provider entities for knowledge graph.
    """
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    npi = Column(String(20), nullable=False, unique=True, index=True, comment="National Provider Identifier")
    name = Column(String(255), nullable=False, index=True, comment="Provider or facility name")
    provider_type = Column(Enum(ProviderType), nullable=False, index=True, comment="Type of provider")
    specialty = Column(String(100), nullable=True, index=True, comment="Medical specialty")
    tax_id = Column(String(50), nullable=True, index=True, comment="Tax identifier")
    address = Column(Text, nullable=True, comment="Full address")
    city = Column(String(100), nullable=True, index=True, comment="City")
    state = Column(String(2), nullable=False, index=True, comment="State code")
    zip_code = Column(String(10), nullable=True, index=True, comment="ZIP code")
    phone = Column(String(20), nullable=True, comment="Phone number")
    email = Column(String(255), nullable=True, index=True, comment="Email address")
    license_number = Column(String(50), nullable=True, index=True, comment="State license number")
    license_status = Column(String(20), nullable=True, default="active", index=True, comment="License status")
    license_expiration = Column(DateTime, nullable=True, comment="License expiration date")
    hospital_affiliations = relationship("Hospital", secondary="hospital_provider", back_populates="hospitals")
    insurer_networks = relationship("Insurer", secondary="provider_insurer", back_populates="insurers")
    claims = relationship("Claim", back_populates="provider_claims")
    alerts = relationship("Alert", back_populates="provider_alerts")
    
    # Knowledge graph properties
    graph_id = Column(String(100), nullable=True, comment="Neo4j node ID")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Provider {self.npi}: {self.name} ({self.provider_type})>"
