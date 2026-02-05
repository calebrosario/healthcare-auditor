"""
Base ingestion module with common utilities.
"""
import asyncio
import logging
from typing import Optional
from datetime import datetime
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..backend.app.core.database import get_db
from ..backend.app.models.billing_code import BillingCode, CodeType, CodeRelationship

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaseIngestor:
    """Base class for all data ingestors."""
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.processed = 0
        self.errors = []
    
    async def fetch_data(self, session: httpx.AsyncClient) -> list:
        """Fetch data from API. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement fetch_data()")
    
    async def process_item(self, item: dict, db: AsyncSession) -> Optional[BillingCode]:
        """Process a single item. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement process_item()")
    
    async def ingest(self, db: AsyncSession):
        """
        Main ingestion loop.
        Fetch data in batches, process items, and insert into database.
        """
        logger.info("Starting ingestion...")
        
        async with httpx.AsyncClient() as session:
            while True:
                try:
                    # Fetch batch of data
                    data = await self.fetch_data(session)
                    
                    if not data:
                        logger.info("No more data to process")
                        break
                    
                    logger.info(f"Processing batch of {len(data)} items")
                    
                    # Process and insert each item
                    for item in data:
                        try:
                            billing_code = await self.process_item(item, db)
                            if billing_code:
                                await db.add(billing_code)
                                self.processed += 1
                        except Exception as e:
                            logger.error(f"Error processing item {item}: {e}")
                            self.errors.append(str(e))
                    
                    # Commit batch
                    await db.commit()
                    logger.info(f"Committed batch. Total processed: {self.processed}")
                    
                except Exception as e:
                    logger.error(f"Error during ingestion: {e}")
                    break
        
        logger.info(f"Ingestion complete. Processed: {self.processed}, Errors: {len(self.errors)}")
        
        return {
            "processed": self.processed,
            "errors": self.errors,
            "success": len(self.errors) == 0
        }


async def create_code_relationships(
    db: AsyncSession,
    source_code_id: int,
    related_codes: list[tuple[str, str]]
):
    """Create code relationships (bundling, mutually exclusive, etc.)."""
    relationship_map = {
        "bundles": "bundled_from",
        "unbundled_from": "unbundled_from",
        "mutually_exclusive": "mutually_exclusive",
        "required_together": "required_together"
    }
    
    for target_code, relationship_type in related_codes:
        # Check if target code exists
        result = await db.execute(
            select(BillingCode).where(BillingCode.code == target_code)
        )
        target = result.scalar_one_or_none()
        
        if target:
            # Create relationship
            rel = CodeRelationship(
                source_code_id=source_code_id,
                target_code_id=target.id,
                relationship_type=relationship_type,
                condition=f"NCCI edit validation"
            )
            await db.add(rel)
    
    await db.commit()
