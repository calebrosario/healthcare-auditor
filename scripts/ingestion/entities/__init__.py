"""
Entity data ingestion package.
"""
from .npi_ingestor import NPIIngestor
from .entity_manager import EntityManager

__all__ = [
    "NPIIngestor",
    "EntityManager",
]
