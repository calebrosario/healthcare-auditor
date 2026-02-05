"""
Entity data ingestion manager - coordinates all entity ingestion.
"""
import asyncio
import logging
from typing import Dict, List
from .npi_ingestor import NPIIngestor

logger = logging.getLogger(__name__)


class EntityManager:
    """Manager for all entity data ingestion."""
    
    def __init__(self):
        self.ingestors = {
            "NPI": NPIIngestor(batch_size=500),
        }
        self.results = {}
    
    async def run_all(self, db_session):
        """Run all entity ingestion processes."""
        logger.info("Starting entity data ingestion...")
        
        tasks = []
        for name, ingestor in self.ingestors.items():
            task = ingestor.ingest(db_session)
            tasks.append(task)
        
        # Run all ingestions in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for (name, result) in zip(self.ingestors.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Error in {name} ingestion: {result}")
                self.results[name] = {"success": False, "error": str(result)}
            else:
                self.results[name] = = result
                logger.info(f"{name} ingestion completed: {result}")
        
        # Generate summary
        self.generate_summary()
        
        return self.results
    
    def generate_summary(self):
        """Generate summary report."""
        summary = {
            "timestamp": asyncio.get_event_loop().time().isoformat(),
            "ingestions": self.results,
            "total_processed": sum(
                r.get("processed", 0) if not isinstance(r, Exception) else 0
                for r in self.results.values()
            ),
            "total_errors": sum(
                len(r.get("errors", [])) if not isinstance(r, Exception) else 0
                for r in self.results.values()
            ),
        }
        
        logger.info("Entity Ingestion Summary:")
        logger.info(f"Total processed: {summary['total_processed']}")
        logger.info(f"Total errors: {summary['total_errors']}")
        
        for name, result in self.results.items():
            status = "SUCCESS" if result.get("success") else "FAILED"
            processed = result.get("processed", 0) if not isinstance(result, Exception) else 0)
            logger.info(f"  {name}: {status} - Processed: {processed}")
        
        return summary


async def main():
    """Main function to run all entity ingestion."""
    logger.info("=" * 60)
    logger.info("Healthcare Auditor - Entity Data Ingestion")
    logger.info("=" * 60)
    
    from ..backend.app.core.database import get_db
    
    manager = EntityManager()
    
    async with get_db() as db:
        results = await manager.run_all(db)
        
        logger.info("\n" + "=" * 60)
        logger.info("Entity Ingestion Complete!")
        logger.info("=" * 60)
        logger.info(f"Results: {results}")
        
        return results


if __name__ == "__main__":
    asyncio.run(main())
