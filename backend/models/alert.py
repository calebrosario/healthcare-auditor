"""
Alert model for fraud detection and compliance notifications.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .bill import Bill
from .provider import Provider


class AlertType(str, Enum):
    """Types of alerts."""
    FRAUD_HIGH = "fraud_high"
    FRAUD_MEDIUM = "fraud_medium"
    FRAUD_LOW = "fraud_low"
    COMPLIANCE_HIGH = "compliance_high"
    COMPLIANCE_MEDIUM = "compliance_medium"
    COMPLIANCE_LOW = "compliance_low"
    DATA_ISSUE = "data_issue"
    SYSTEM_ERROR = "system_error"


class AlertStatus(str, Enum):
    """Status of alert lifecycle."""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class Alert(Base):
    """
    Fraud and compliance alerts.
    """
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(Enum(AlertType), nullable=False, index=True, comment="Type of alert")
    alert_name = Column(String(255), nullable=False, index=True, comment="Alert name/description")
    description = Column(Text, nullable=True, comment="Detailed description")
    priority = Column(String(20), nullable=False, index=True, comment="Priority level")
    score = Column(Float, nullable=False, index=True, comment="Risk or compliance score (0-1)")
    
    # Associated entities
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=True, index=True, comment="Associated bill")
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True, index=True, comment="Associated provider")
    
    # Status tracking
    status = Column(Enum(AlertStatus), nullable=False, default=AlertStatus.NEW, index=True, comment="Alert status")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True, comment="When alert was created")
    acknowledged_at = Column(DateTime, nullable=True, index=True, comment="When alert was acknowledged")
    investigated_at = Column(DateTime, nullable=True, index=True, comment="When investigation started")
    resolved_at = Column(DateTime, nullable=True, index=True, comment="When alert was resolved")
    dismissed_at = Column(DateTime, nullable=True, index=True, comment="When alert was dismissed")
    
    # Resolution
    resolution_notes = Column(Text, nullable=True, comment="Investigation findings")
    resolved_by = Column(String(100), nullable=True, comment="Who resolved the alert")
    
    # Notification
    notification_sent = Column(Boolean, nullable=False, default=False, comment="Whether notification was sent")
    notification_channel = Column(String(50), nullable=True, comment="Email, SMS, in-app")
    
    # Relationships
    bill = relationship("Bill", foreign_keys=[bill_id])
    provider = relationship("Provider", foreign_keys=[provider_id])
    
    # Knowledge graph
    graph_id = Column(String(100), nullable=True, comment="Neo4j node ID")
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Alert {self.alert_name}: {self.priority} (score: {self.score})>"
