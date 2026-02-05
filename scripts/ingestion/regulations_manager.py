"""
Regulatory data ingestion manager.
"""
import asyncio
import logging
from typing import Dict
from datetime import datetime
from .regulations_ingestor import RegulationsIngestor

logger = logging.getLogger(__name__)


class RegulationsManager:
    """Manager for regulatory data ingestion."""
    
    async def ingest_all(self, db_session):
        """Ingest all regulatory data from sources."""
        logger.info("Starting regulatory data ingestion...")
        
        ingestor = RegulationsIngestor(batch_size=50)
        
        result = await ingestor.ingest(db_session)
        
        logger.info(f"Regulatory data ingestion complete: {result}")
        return result


async def update_regulations(self, db_session):
        """Check for regulation updates."""
        logger.info("Checking for regulation updates...")
        # TODO: Implement logic to check for new/updated regulations
        pass


async def main():
    """Main function."""
    logger.info("Starting regulatory data manager...")
    
    from ..backend.app.core.database import get_db
    
    manager = RegulationsManager()
    
    async with get_db() as db:
        results = {
            "ingest": await manager.ingest_all(db),
            "update": await manager.update_regulations(db),
        }
        
        logger.info("Regulatory data manager complete!")
        
        return results


if __name__ == "__main__":
    asyncio.run(main())
