"""
Neo4j connection and session management.
"""
import logging
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from ..config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create async driver
driver: AsyncDriver = AsyncGraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)


async def get_neo4j() -> AsyncSession:
    """
    Dependency for getting Neo4j sessions.
    Follows the same pattern as PostgreSQL get_db().
    """
    session = driver.session(database=settings.NEO4J_DATABASE)
    try:
        yield session
    except Exception:
        await session.close()
        raise
    finally:
        await session.close()


async def init_graph():
    """
    Initialize Neo4j graph - create constraints and indexes.
    """
    async with driver.session(database=settings.NEO4J_DATABASE) as session:
        try:
            # Create unique constraints for entity identifiers
            constraints = [
                # Provider constraints
                "CREATE CONSTRAINT provider_npi_unique IF NOT EXISTS FOR (p:Provider) REQUIRE p.npi IS UNIQUE",
                # Hospital constraints
                "CREATE CONSTRAINT hospital_npi_unique IF NOT EXISTS FOR (h:Hospital) REQUIRE h.npi IS UNIQUE",
                "CREATE CONSTRAINT hospital_id_unique IF NOT EXISTS FOR (h:Hospital) REQUIRE h.id IS UNIQUE",
                # Insurer constraints
                "CREATE CONSTRAINT insurer_payer_id_unique IF NOT EXISTS FOR (i:Insurer) REQUIRE i.payer_id IS UNIQUE",
                "CREATE CONSTRAINT insurer_id_unique IF NOT EXISTS FOR (i:Insurer) REQUIRE i.id IS UNIQUE",
                # Regulation constraints
                "CREATE CONSTRAINT regulation_code_unique IF NOT EXISTS FOR (r:Regulation) REQUIRE r.code IS UNIQUE",
                # Bill constraints
                "CREATE CONSTRAINT bill_claim_id_unique IF NOT EXISTS FOR (b:Bill) REQUIRE b.claim_id IS UNIQUE",
                # Patient constraints
                "CREATE CONSTRAINT patient_id_unique IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE",
                # Billing code constraints
                "CREATE CONSTRAINT billing_code_code_unique IF NOT EXISTS FOR (c:BillingCode) REQUIRE c.code IS UNIQUE",
            ]

            for constraint in constraints:
                try:
                    await session.run(constraint)
                    logger.info(f"Created constraint: {constraint[:50]}...")
                except Exception as e:
                    if "already exists" not in str(e):
                        logger.warning(f"Failed to create constraint: {e}")

            # Create indexes for common queries
            indexes = [
                # Provider indexes
                "CREATE INDEX provider_name_idx IF NOT EXISTS FOR (p:Provider) ON (p.name)",
                "CREATE INDEX provider_type_idx IF NOT EXISTS FOR (p:Provider) ON (p.provider_type)",
                "CREATE INDEX provider_specialty_idx IF NOT EXISTS FOR (p:Provider) ON (p.specialty)",
                "CREATE INDEX provider_state_idx IF NOT EXISTS FOR (p:Provider) ON (p.state)",
                "CREATE INDEX provider_city_idx IF NOT EXISTS FOR (p:Provider) ON (p.city)",
                # Hospital indexes
                "CREATE INDEX hospital_name_idx IF NOT EXISTS FOR (h:Hospital) ON (h.name)",
                "CREATE INDEX hospital_type_idx IF NOT EXISTS FOR (h:Hospital) ON (h.hospital_type)",
                "CREATE INDEX hospital_state_idx IF NOT EXISTS FOR (h:Hospital) ON (h.state)",
                # Insurer indexes
                "CREATE INDEX insurer_name_idx IF NOT EXISTS FOR (i:Insurer) ON (i.name)",
                "CREATE INDEX insurer_coverage_type_idx IF NOT EXISTS FOR (i:Insurer) ON (i.coverage_type)",
                "CREATE INDEX insurer_state_idx IF NOT EXISTS FOR (i:Insurer) ON (i.state)",
                # Regulation indexes
                "CREATE INDEX regulation_name_idx IF NOT EXISTS FOR (r:Regulation) ON (r.name)",
                "CREATE INDEX regulation_category_idx IF NOT EXISTS FOR (r:Regulation) ON (r.category)",
                "CREATE INDEX regulation_type_idx IF NOT EXISTS FOR (r:Regulation) ON (r.regulation_type)",
                # Bill indexes
                "CREATE INDEX bill_date_idx IF NOT EXISTS FOR (b:Bill) ON (b.bill_date)",
                "CREATE INDEX bill_amount_idx IF NOT EXISTS FOR (b:Bill) ON (b.billed_amount)",
                "CREATE INDEX bill_status_idx IF NOT EXISTS FOR (b:Bill) ON (b.status)",
                # Full-text search indexes
                "CREATE FULLTEXT INDEX provider_name_fulltext IF NOT EXISTS FOR (p:Provider) OPTIONS {indexConfig: {`fulltext.analyzer`: 'english'}} ON EACH [p.name, p.specialty]",
                "CREATE FULLTEXT INDEX hospital_name_fulltext IF NOT EXISTS FOR (h:Hospital) OPTIONS {indexConfig: {`fulltext.analyzer`: 'english'}} ON EACH [h.name, h.specialty]",
            ]

            for index in indexes:
                try:
                    await session.run(index)
                    logger.info(f"Created index: {index[:50]}...")
                except Exception as e:
                    if "already exists" not in str(e):
                        logger.warning(f"Failed to create index: {e}")

            logger.info("Neo4j graph initialized with constraints and indexes")

        except Exception as e:
            logger.error(f"Failed to initialize Neo4j graph: {e}")
            raise


async def close_graph():
    """Close Neo4j driver connections."""
    await driver.close()
    logger.info("Neo4j driver closed")
