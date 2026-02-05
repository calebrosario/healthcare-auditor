"""
Knowledge graph construction script.
Loads PostgreSQL data into Neo4j knowledge graph.
"""
import asyncio
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, '/Users/calebrosario/Documents/sandbox/healthcare-auditor/backend')

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, init_db, close_db
from app.core.neo4j import get_neo4j, init_graph, close_graph
from app.core.graph_builder import GraphBuilder
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """Orchestrates knowledge graph construction from PostgreSQL to Neo4j."""

    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.stats = {
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0,
            "total_nodes": 0,
            "total_edges": 0,
            "errors": 0
        }

    async def build(self):
        """
        Main build orchestration method.
        Loads all entities and relationships from PostgreSQL to Neo4j.
        """
        self.stats["start_time"] = datetime.utcnow()
        logger.info("=" * 80)
        logger.info("Starting Knowledge Graph Construction")
        logger.info("=" * 80)

        try:
            # Initialize databases
            logger.info("Initializing databases...")
            await init_db()
            await init_graph()
            logger.info("Databases initialized")

            # Get database sessions
            async with get_db() as pg_db, get_neo4j() as neo_db:
                graph_builder = GraphBuilder(neo_db, batch_size=self.batch_size)

                # Phase 1: Load entity nodes
                logger.info("\n" + "-" * 80)
                logger.info("PHASE 1: Loading Entity Nodes")
                logger.info("-" * 80)

                await self._load_providers(pg_db, graph_builder)
                await self._load_hospitals(pg_db, graph_builder)
                await self._load_insurers(pg_db, graph_builder)
                await self._load_regulations(pg_db, graph_builder)
                await self._load_bills(pg_db, graph_builder)

                # Phase 2 (now 7 steps):: Load relationships
                logger.info("\n" + "-" * 80)
                logger.info("PHASE 2: Loading Relationships")
                logger.info("-" * 80)

                await self._load_provider_hospital_relationships(pg_db, graph_builder)
                await self._load_provider_insurer_relationships(pg_db, graph_builder)
                await self._load_bill_regulation_relationships(pg_db, graph_builder)
                await self._load_bill_alert_relationships(pg_db, graph_builder)

                await self._load_provider_contract_relationships(pg_db, graph_builder)
                await self._load_provider_ownership_relationships(pg_db, graph_builder)
                await self._load_hospital_affiliation_relationships(pg_db, graph_builder)

                await self._load_bill_alert_relationships(pg_db, graph_builder)

                # Get final statistics
                graph_stats = graph_builder.get_stats()
                self.stats["total_nodes"] = (
                    graph_stats["providers"] +
                    graph_stats["hospitals"] +
                    graph_stats["insurers"] +
                    graph_stats["regulations"] +
                    graph_stats["bills"]
                )
                self.stats["total_edges"] = graph_stats["relationships"]
                self.stats["errors"] = graph_stats["errors"]

            # Print summary
            await self._print_summary()

        except Exception as e:
            logger.error(f"Failed to build knowledge graph: {e}")
            raise
        finally:
            # Close database connections
            await close_db()
            await close_graph()

    async def _load_providers(
        self,
        pg_db: AsyncSession,
        graph_builder: GraphBuilder
    ):
        """Load provider nodes from PostgreSQL."""
        logger.info("\n[1/5] Loading Providers...")

        try:
            result = await pg_db.execute(
                text("""
                SELECT
                    id,
                    npi,
                    name,
                    provider_type,
                    specialty,
                    tax_id,
                    address,
                    city,
                    state,
                    zip_code,
                    phone,
                    email,
                    license_number,
                    license_status,
                    license_expiration,
                    created_at,
                    updated_at
                FROM providers
                ORDER BY id
                """)
            )

            providers = []
            async for row in result.mappings():
                providers.append(dict(row))
                if len(providers) >= self.batch_size:
                    await graph_builder.create_provider_nodes(providers)
                    providers = []

            # Process remaining
            if providers:
                await graph_builder.create_provider_nodes(providers)

            stats = graph_builder.get_stats()
            logger.info(f"✓ Loaded {stats['providers']} Provider nodes")

        except Exception as e:
            logger.error(f"✗ Failed to load providers: {e}")
            raise

    async def _load_hospitals(
        self,
        pg_db: AsyncSession,
        graph_builder: GraphBuilder
    ):
        """Load hospital nodes from PostgreSQL."""
        logger.info("\n[2/5] Loading Hospitals...")

        try:
            result = await pg_db.execute(
                text("""
                SELECT
                    id,
                    npi,
                    name,
                    hospital_type,
                    address,
                    city,
                    state,
                    zip_code,
                    phone,
                    bed_count,
                    specialty,
                    accreditation,
                    accreditation_expiration,
                    ownership_type,
                    tax_id,
                    created_at,
                    updated_at
                FROM hospitals
                ORDER BY id
                """)
            )

            hospitals = []
            async for row in result.mappings():
                hospitals.append(dict(row))
                if len(hospitals) >= self.batch_size:
                    await graph_builder.create_hospital_nodes(hospitals)
                    hospitals = []

            if hospitals:
                await graph_builder.create_hospital_nodes(hospitals)

            stats = graph_builder.get_stats()
            logger.info(f"✓ Loaded {stats['hospitals']} Hospital nodes")

        except Exception as e:
            logger.error(f"✗ Failed to load hospitals: {e}")
            raise

    async def _load_insurers(
        self,
        pg_db: AsyncSession,
        graph_builder: GraphBuilder
    ):
        """Load insurer nodes from PostgreSQL."""
        logger.info("\n[3/5] Loading Insurers...")

        try:
            result = await pg_db.execute(
                text("""
                SELECT
                    id,
                    name,
                    payer_id,
                    coverage_type,
                    state_license,
                    license_status,
                    license_expiration,
                    address,
                    city,
                    state,
                    zip_code,
                    contact_email,
                    contact_phone,
                    created_at,
                    updated_at
                FROM insurers
                ORDER BY id
                """)
            )

            insurers = []
            async for row in result.mappings():
                insurers.append(dict(row))
                if len(insurers) >= self.batch_size:
                    await graph_builder.create_insurer_nodes(insurers)
                    insurers = []

            if insurers:
                await graph_builder.create_insurer_nodes(insurers)

            stats = graph_builder.get_stats()
            logger.info(f"✓ Loaded {stats['insurers']} Insurer nodes")

        except Exception as e:
            logger.error(f"✗ Failed to load insurers: {e}")
            raise

    async def _load_regulations(
        self,
        pg_db: AsyncSession,
        graph_builder: GraphBuilder
    ):
        """Load regulation nodes from PostgreSQL."""
        logger.info("\n[4/5] Loading Regulations...")

        try:
            result = await pg_db.execute(
                text("""
                SELECT
                    id,
                    code,
                    name,
                    regulation_type,
                    category,
                    description,
                    requirements,
                    effective_date,
                    expiration_date,
                    is_active,
                    source_url,
                    created_at,
                    updated_at
                FROM regulations
                WHERE is_active = true
                ORDER BY effective_date DESC
                """)
            )

            regulations = []
            async for row in result.mappings():
                regulations.append(dict(row))
                if len(regulations) >= self.batch_size:
                    await graph_builder.create_regulation_nodes(regulations)
                    regulations = []

            if regulations:
                await graph_builder.create_regulation_nodes(regulations)

            stats = graph_builder.get_stats()
            logger.info(f"✓ Loaded {stats['regulations']} Regulation nodes")

        except Exception as e:
            logger.error(f"✗ Failed to load regulations: {e}")
            raise

    async def _load_bills(
        self,
        pg_db: AsyncSession,
        graph_builder: GraphBuilder
    ):
        """Load bill nodes from PostgreSQL."""
        logger.info("\n[5/5] Loading Bills...")

        try:
            result = await pg_db.execute(
                text("""
                SELECT
                    id,
                    claim_id,
                    patient_id,
                    bill_date,
                    provider_id,
                    insurer_id,
                    hospital_id,
                    procedure_code,
                    diagnosis_code,
                    hcpcs_code,
                    ndc_code,
                    billed_amount,
                    allowed_amount,
                    paid_amount,
                    status,
                    status_date,
                    fraud_score,
                    fraud_indicators,
                    compliance_issues,
                    medical_necessity_score,
                    documentation_text,
                    created_at,
                    updated_at
                FROM bills
                ORDER BY bill_date DESC
                LIMIT 1000000
                """)
            )

            # Get provider NPI mapping
            provider_map = {}
            provider_result = await pg_db.execute(text("SELECT id, npi FROM providers"))
            async for row in provider_result.mappings():
                provider_map[row['id']] = row['npi']

            bills = []
            async for row in result.mappings():
                bill = dict(row)
                # Map provider_id to provider_npi
                if row['provider_id'] in provider_map:
                    bill['provider_npi'] = provider_map[row['provider_id']]
                else:
                    logger.warning(f"Provider ID {row['provider_id']} not found for claim {row['claim_id']}")
                    continue

                bills.append(bill)
                if len(bills) >= self.batch_size:
                    await graph_builder.create_bill_nodes(bills)
                    bills = []

            if bills:
                await graph_builder.create_bill_nodes(bills)

            stats = graph_builder.get_stats()
            logger.info(f"✓ Loaded {stats['bills']} Bill nodes")

        except Exception as e:
            logger.error(f"✗ Failed to load bills: {e}")
            raise

    async def _load_provider_hospital_relationships(
        self,
        pg_db: AsyncSession,
        graph_builder: GraphBuilder
    ):
        """Load PROVIDES_AT relationships."""
        logger.info("\n[1/4] Loading Provider-Hospital relationships (PROVIDES_AT)...")

        try:
            result = await pg_db.execute(
                text("""
                SELECT
                    p.npi AS provider_npi,
                    h.npi AS hospital_npi
                FROM hospital_provider hp
                JOIN providers p ON hp.provider_id = p.id
                JOIN hospitals h ON hp.hospital_id = h.id
                ORDER BY p.npi
                """)
            )

            provider_npis = []
            hospital_npis = []

            async for row in result.mappings():
                provider_npis.append(row['provider_npi'])
                hospital_npis.append(row['hospital_npi'])

                if len(provider_npis) >= self.batch_size:
                    await graph_builder.create_provides_at_edges(provider_npis, hospital_npis)
                    provider_npis = []
                    hospital_npis = []

            if provider_npis:
                await graph_builder.create_provides_at_edges(provider_npis, hospital_npis)

            stats = graph_builder.get_stats()
            logger.info(f"✓ Loaded PROVIDES_AT relationships")

        except Exception as e:
            logger.warning(f"Warning: Failed to load provider-hospital relationships: {e}")

    async def _load_provider_insurer_relationships(
        self,
        pg_db: AsyncSession,
        graph_builder: GraphBuilder
    ):
        """Load INSURES relationships."""
        logger.info("\n[2/4] Loading Provider-Insurer relationships (INSURES)...")

        try:
            result = await pg_db.execute(
                text("""
                SELECT
                    p.npi AS provider_npi,
                    i.payer_id AS payer_id
                FROM provider_insurer pi
                JOIN providers p ON pi.provider_id = p.id
                JOIN insurers i ON pi.insurer_id = i.id
                ORDER BY p.npi
                """)
            )

            provider_npis = []
            insurer_payer_ids = []

            async for row in result.mappings():
                provider_npis.append(row['provider_npi'])
                insurer_payer_ids.append(row['payer_id'])

                if len(provider_npis) >= self.batch_size:
                    await graph_builder.create_insures_edges(provider_npis, insurer_payer_ids)
                    provider_npis = []
                    insurer_payer_ids = []

            if provider_npis:
                await graph_builder.create_insures_edges(provider_npis, insurer_payer_ids)

            stats = graph_builder.get_stats()
            logger.info(f"✓ Loaded INSURES relationships")

        except Exception as e:
            logger.warning(f"Warning: Failed to load provider-insurer relationships: {e}")

    async def _load_bill_regulation_relationships(
        self,
        pg_db: AsyncSession,
        graph_builder: GraphBuilder
    ):
        """Load APPLIES_TO relationships between bills and regulations."""
        logger.info("\n[3/4] Loading Bill-Regulation relationships (APPLIES_TO)...")

        try:
            result = await pg_db.execute(
                text("""
                SELECT
                    b.claim_id,
                    r.code AS regulation_code
                FROM compliance_check cc
                JOIN bills b ON cc.bill_id = b.id
                JOIN regulations r ON cc.regulation_id = r.id
                WHERE cc.is_compliant = false OR cc.severity = 'high'
                ORDER BY b.claim_id
                LIMIT 100000
                """)
            )

            claim_ids = []
            regulation_codes = []

            async for row in result.mappings():
                claim_ids.append(row['claim_id'])
                regulation_codes.append(row['regulation_code'])

                if len(claim_ids) >= self.batch_size:
                    await graph_builder.create_applies_to_edges(claim_ids, regulation_codes)
                    claim_ids = []
                    regulation_codes = []

            if claim_ids:
                await graph_builder.create_applies_to_edges(claim_ids, regulation_codes)

            stats = graph_builder.get_stats()
            logger.info(f"✓ Loaded APPLIES_TO relationships")

        except Exception as e:
            logger.warning(f"Warning: Failed to load bill-regulation relationships: {e}")

    async def _load_bill_alert_relationships(
        self,
        pg_db: AsyncSession,
        graph_builder: GraphBuilder
    ):
        """Load FLAGGED_FOR_FRAUD relationships between bills and alerts."""
        logger.info("\n[4/4] Loading Bill-Alert relationships (FLAGGED_FOR_FRAUD)...")

        try:
            result = await pg_db.execute(
                text("""
                SELECT
                    b.claim_id,
                    a.id AS alert_id
                FROM alerts a
                JOIN bills b ON a.bill_id = b.id
                WHERE a.alert_type = 'fraud' OR a.severity = 'high'
                ORDER BY b.claim_id
                LIMIT 100000
                """)
            )

            claim_ids = []
            alert_ids = []

            async for row in result.mappings():
                claim_ids.append(row['claim_id'])
                alert_ids.append(row['alert_id'])

                if len(claim_ids) >= self.batch_size:
                    await graph_builder.create_flagged_for_fraud_edges(claim_ids, alert_ids)
                    claim_ids = []
                    alert_ids = []

            if claim_ids:
                await graph_builder.create_flagged_for_fraud_edges(claim_ids, alert_ids)

            stats = graph_builder.get_stats()
            logger.info(f"✓ Loaded FLAGGED_FOR_FRAUD relationships")

        except Exception as e:
            logger.warning(f"Warning: Failed to load bill-alert relationships: {e}")

    async def _print_summary(self):
        """Print construction summary."""
        self.stats["end_time"] = datetime.utcnow()
        self.stats["duration_seconds"] = (
            (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        )

        logger.info("\n" + "=" * 80)
        logger.info("KNOWLEDGE GRAPH CONSTRUCTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Duration: {self.stats['duration_seconds']:.2f} seconds")
        logger.info(f"Total Nodes: {self.stats['total_nodes']:,}")
        logger.info(f"Total Edges: {self.stats['total_edges']:,}")
        logger.info(f"Total Errors: {self.stats['errors']:,}")
        logger.info("\nNeo4j Configuration:")
        logger.info(f"  URI: {settings.NEO4J_URI}")
        logger.info(f"  Database: {settings.NEO4J_DATABASE}")
        logger.info(f"  Batch Size: {self.batch_size}")
        logger.info("=" * 80 + "\n")


async def main():
    """Main entry point."""
    builder = KnowledgeGraphBuilder(batch_size=settings.INGEST_BATCH_SIZE)
    await builder.build()


if __name__ == "__main__":
    asyncio.run(main())
