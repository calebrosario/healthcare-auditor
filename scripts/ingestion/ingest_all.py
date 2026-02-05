"""
Main script to run all data ingestion processes.
"""
import asyncio
import logging
from datetime import datetime

from .ingestion_manager import IngestionManager
from ..ingestion.entities.entity_manager import EntityManager

logger = logging.getLogger(__name__)


async def main():
    """Run all ingestion processes in coordinated manner."""
    logger.info("=" * 60)
    logger.info("Healthcare Auditor - Data Ingestion System")
    logger.info("=" * 60)
    logger.info(f"Started at: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    # Check database connection first
    from ..backend.app.core.database import get_db
    from ..backend.app.models.base import Base
    
    try:
        # Test database connection
        async with get_db() as db:
            await db.execute("SELECT 1")
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return
    
    # Run all ingestion phases
    phases = [
        "Billing Codes (CPT, ICD-10, HCPCS, DRG, NDC)",
        "Entity Data (NPI Registry, Providers, Hospitals)",
        "Regulatory Data (HIPAA, ACA, Stark Law, Anti-Kickback)",
    ]
    
    logger.info(f"Running ingestion phases: {', '.join(phases)}")
    logger.info("=" * 60)
    
    ingestion_manager = IngestionManager()
    entity_manager = EntityManager()
    
    # Run all ingestions
    results = await ingestion_manager.run_all(None)  # No db session, manager creates its own
    entity_results = await entity_manager.run_all(None)  # Same
    
    logger.info("=" * 60)
    logger.info("All Data Ingestion Complete!")
    logger.info("=" * 60)
    logger.info(f"Completed at: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    # Generate summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "billing_codes": results.get("ingest", {}),
        "entity_data": entity_results.get("ingest", {}),
        "regulations": results.get("ingest", {}),
        "total_processed": sum([
            results.get("ingest", {}).get("processed", 0),
            entity_results.get("ingest", {}).get("processed", 0),
            results.get("regulations", {}).get("processed", 0),
        ]),
        "total_errors": sum([
            len(results.get("ingest", {}).get("errors", []),
            entity_results.get("ingest", {}).get("errors", []),
            results.get("regulations", {}).get("errors", []),
        ]),
    }
    
    logger.info("Summary:")
    logger.info(f"  Total processed: {summary['total_processed']}")
    logger.info(f"  Total errors: {summary['total_errors']}")
    
    logger.info("=" * 60)
    logger.info("Data ingestion complete. Ready for next phases:")
    logger.info("  - Knowledge Graph Construction")
    logger.info("  - Rules Engine Implementation")
    logger.info("  - Fraud Detection Algorithms")
    logger.info("  - Network Analysis")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
