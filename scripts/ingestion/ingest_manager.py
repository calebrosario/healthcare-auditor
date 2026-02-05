"""
Main ingestion manager that coordinates all data sources.
"""
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
from .icd10_ingestor import ICD10Ingestor
from .hcpcs_ingestor import HCPCSIngestor
from .ndc_ingestor import NDCIngestor

logger = logging.getLogger(__name__)


class IngestionManager:
    """Manages all data ingestion processes."""
    
    def __init__(self):
        self.ingestors = {
            "ICD-10": ICD10Ingestor(batch_size=1000),
            "HCPCS": HCPCSIngestor(batch_size=1000),
            "NDC": NDCIngestor(batch_size=1000),
        }
        self.results = {}
    
    async def run_all(self, db_session):
        """Run all ingestion processes in parallel."""
        logger.info("Starting full data ingestion...")
        
        tasks = [
            self.ingestors["ICD-10"].ingest(db_session),
            self.ingestors["HCPCS"].ingest(db_session),
            self.ingestors["NDC"].ingest(db_session),
        ]
        
        # Run all ingestions in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (name, result) in enumerate(zip(self.ingestors.keys(), results), 1):
            if isinstance(result, Exception):
                logger.error(f"Error in {name} ingestion: {result}")
                self.results[name] = {"success": False, "error": str(result)}
            else:
                self.results[name] = result
                logger.info(f"{name} ingestion completed: processed={result.get('processed', 0)}, errors={len(result.get('errors', []))}")
        
        # Generate summary report
        self.generate_summary()
        
        return self.results
    
    def generate_summary(self):
        """Generate summary report of all ingestions."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "ingestions": self.results,
            "total_processed": sum(r.get('processed', 0) for r in self.results.values()),
            "total_errors": sum(len(r.get('errors', [])) for r in self.results.values()),
        }
        
        logger.info("Ingestion Summary:")
        logger.info(f"  Total processed: {summary['total_processed']}")
        logger.info(f"  Total errors: {summary['total_errors']}")
        
        for name, result in self.results.items():
            status = "SUCCESS" if result.get('success') else "FAILED"
            logger.info(f"  {name}: {status} - Processed: {result.get('processed', 0)}")
        
        return summary


async def main():
    """Main function to run all ingestion processes."""
    logger.info("=" * 60)
    logger.info("Healthcare Auditor - Data Ingestion")
    logger.info("=" * 60)
    
    from ..backend.app.core.database import get_db
    
    manager = IngestionManager()
    
    async with get_db() as db:
        results = await manager.run_all(db)
        
        logger.info("\n" + "=" * 60)
        logger.info("Ingestion Complete!")
        logger.info("=" * 60 + "\n")
        logger.info(f"Results: {results}")
        
        return results


if __name__ == "__main__":
    asyncio.run(main())
