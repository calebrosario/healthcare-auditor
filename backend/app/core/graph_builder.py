"""
Knowledge graph node and edge builders.
Handles batch loading of entities and relationships into Neo4j.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from neo4j import AsyncSession

# Configure logging
logger = logging.getLogger(__name__)


class GraphBuilder:
    """Builder class for creating knowledge graph nodes and edges."""

    def __init__(self, neo4j_session: AsyncSession, batch_size: int = 1000):
        """
        Initialize graph builder.

        Args:
            neo4j_session: Neo4j async session
            batch_size: Number of records to batch in UNWIND queries
        """
        self.session = neo4j_session
        self.batch_size = batch_size
        self.stats = {
            "providers": 0,
            "hospitals": 0,
            "insurers": 0,
            "regulations": 0,
            "bills": 0,
            "relationships": 0,
            "errors": 0
        }

    # ========== NODE BUILDERS ==========

    async def create_provider_nodes(self, providers: List[Dict[str, Any]]) -> int:
        """
        Create Provider nodes in batches using UNWIND for performance.

        Args:
            providers: List of provider dictionaries with fields:
                - npi: National Provider Identifier (required)
                - name: Provider name (required)
                - provider_type: Type (required)
                - specialty: Medical specialty (optional)
                - tax_id: Tax identifier (optional)
                - address: Full address (optional)
                - city: City (optional)
                - state: State code (optional)
                - zip_code: ZIP code (optional)
                - phone: Phone number (optional)
                - email: Email address (optional)
                - license_number: State license number (optional)
                - license_status: License status (optional)
                - license_expiration: License expiration date (optional)
                - pg_id: PostgreSQL ID for reference

        Returns:
            Number of provider nodes created
        """
        if not providers:
            return 0

        total_created = 0
        for i in range(0, len(providers), self.batch_size):
            batch = providers[i:i + self.batch_size]

            try:
                query = """
                UNWIND $providers AS provider
                MERGE (p:Provider {npi: provider.npi})
                ON CREATE SET
                    p.name = provider.name,
                    p.provider_type = provider.provider_type,
                    p.specialty = provider.specialty,
                    p.tax_id = provider.tax_id,
                    p.address = provider.address,
                    p.city = provider.city,
                    p.state = provider.state,
                    p.zip_code = provider.zip_code,
                    p.phone = provider.phone,
                    p.email = provider.email,
                    p.license_number = provider.license_number,
                    p.license_status = provider.license_status,
                    p.license_expiration = provider.license_expiration,
                    p.pg_id = provider.pg_id,
                    p.created_at = provider.created_at,
                    p.updated_at = provider.updated_at
                ON MATCH SET
                    p.name = provider.name,
                    p.provider_type = provider.provider_type,
                    p.specialty = provider.specialty,
                    p.updated_at = provider.updated_at
                RETURN count(p) AS created
                """

                result = await self.session.run(query, providers=batch)
                record = await result.single()
                batch_created = record["created"]
                total_created += batch_created
                self.stats["providers"] += batch_created

                logger.info(f"Created {batch_created} provider nodes (batch {i//self.batch_size + 1})")

            except Exception as e:
                logger.error(f"Error creating provider nodes batch {i}: {e}")
                self.stats["errors"] += 1

        return total_created

    async def create_hospital_nodes(self, hospitals: List[Dict[str, Any]]) -> int:
        """
        Create Hospital nodes in batches.

        Args:
            hospitals: List of hospital dictionaries with fields:
                - npi: National Provider Identifier (required)
                - id: PostgreSQL ID (required)
                - name: Hospital name (required)
                - hospital_type: Type (required)
                - address: Full address (optional)
                - city: City (optional)
                - state: State code (optional)
                - zip_code: ZIP code (optional)
                - phone: Phone number (optional)
                - bed_count: Number of beds (optional)
                - specialty: Hospital specialty (optional)
                - accreditation: Accreditation status (optional)
                - accreditation_expiration: Accreditation expiration (optional)
                - ownership_type: Ownership type (optional)
                - tax_id: Tax identifier (optional)
                - created_at: Creation timestamp
                - updated_at: Update timestamp

        Returns:
            Number of hospital nodes created
        """
        if not hospitals:
            return 0

        total_created = 0
        for i in range(0, len(hospitals), self.batch_size):
            batch = hospitals[i:i + self.batch_size]

            try:
                query = """
                UNWIND $hospitals AS hospital
                MERGE (h:Hospital {npi: hospital.npi})
                ON CREATE SET
                    h.id = hospital.id,
                    h.name = hospital.name,
                    h.hospital_type = hospital.hospital_type,
                    h.address = hospital.address,
                    h.city = hospital.city,
                    h.state = hospital.state,
                    h.zip_code = hospital.zip_code,
                    h.phone = hospital.phone,
                    h.bed_count = hospital.bed_count,
                    h.specialty = hospital.specialty,
                    h.accreditation = hospital.accreditation,
                    h.accreditation_expiration = hospital.accreditation_expiration,
                    h.ownership_type = hospital.ownership_type,
                    h.tax_id = hospital.tax_id,
                    h.created_at = hospital.created_at,
                    h.updated_at = hospital.updated_at
                ON MATCH SET
                    h.name = hospital.name,
                    h.hospital_type = hospital.hospital_type,
                    h.specialty = hospital.specialty,
                    h.bed_count = hospital.bed_count,
                    h.accreditation = hospital.accreditation,
                    h.updated_at = hospital.updated_at
                RETURN count(h) AS created
                """

                result = await self.session.run(query, hospitals=batch)
                record = await result.single()
                batch_created = record["created"]
                total_created += batch_created
                self.stats["hospitals"] += batch_created

                logger.info(f"Created {batch_created} hospital nodes (batch {i//self.batch_size + 1})")

            except Exception as e:
                logger.error(f"Error creating hospital nodes batch {i}: {e}")
                self.stats["errors"] += 1

        return total_created

    async def create_insurer_nodes(self, insurers: List[Dict[str, Any]]) -> int:
        """
        Create Insurer nodes in batches.

        Args:
            insurers: List of insurer dictionaries with fields:
                - payer_id: Payer identifier (required)
                - id: PostgreSQL ID (required)
                - name: Insurer name (required)
                - coverage_type: Type (required)
                - state_license: State license number (optional)
                - license_status: License status (optional)
                - license_expiration: License expiration (optional)
                - address: Address (optional)
                - city: City (optional)
                - state: State (optional)
                - zip_code: ZIP code (optional)
                - contact_email: Contact email (optional)
                - contact_phone: Contact phone (optional)
                - created_at: Creation timestamp
                - updated_at: Update timestamp

        Returns:
            Number of insurer nodes created
        """
        if not insurers:
            return 0

        total_created = 0
        for i in range(0, len(insurers), self.batch_size):
            batch = insurers[i:i + self.batch_size]

            try:
                query = """
                UNWIND $insurers AS insurer
                MERGE (i:Insurer {payer_id: insurer.payer_id})
                ON CREATE SET
                    i.id = insurer.id,
                    i.name = insurer.name,
                    i.coverage_type = insurer.coverage_type,
                    i.state_license = insurer.state_license,
                    i.license_status = insurer.license_status,
                    i.license_expiration = insurer.license_expiration,
                    i.address = insurer.address,
                    i.city = insurer.city,
                    i.state = insurer.state,
                    i.zip_code = insurer.zip_code,
                    i.contact_email = insurer.contact_email,
                    i.contact_phone = insurer.contact_phone,
                    i.created_at = insurer.created_at,
                    i.updated_at = insurer.updated_at
                ON MATCH SET
                    i.name = insurer.name,
                    i.coverage_type = insurer.coverage_type,
                    i.license_status = insurer.license_status,
                    i.updated_at = insurer.updated_at
                RETURN count(i) AS created
                """

                result = await self.session.run(query, insurers=batch)
                record = await result.single()
                batch_created = record["created"]
                total_created += batch_created
                self.stats["insurers"] += batch_created

                logger.info(f"Created {batch_created} insurer nodes (batch {i//self.batch_size + 1})")

            except Exception as e:
                logger.error(f"Error creating insurer nodes batch {i}: {e}")
                self.stats["errors"] += 1

        return total_created

    async def create_regulation_nodes(self, regulations: List[Dict[str, Any]]) -> int:
        """
        Create Regulation nodes in batches.

        Args:
            regulations: List of regulation dictionaries with fields:
                - code: Regulation code (required)
                - name: Regulation name (required)
                - regulation_type: Type (required)
                - category: Category (required)
                - description: Description (optional)
                - requirements: Requirements (optional)
                - effective_date: Effective date (required)
                - expiration_date: Expiration date (optional)
                - is_active: Active status (required)
                - source_url: Source URL (optional)
                - created_at: Creation timestamp
                - updated_at: Update timestamp

        Returns:
            Number of regulation nodes created
        """
        if not regulations:
            return 0

        total_created = 0
        for i in range(0, len(regulations), self.batch_size):
            batch = regulations[i:i + self.batch_size]

            try:
                query = """
                UNWIND $regulations AS regulation
                MERGE (r:Regulation {code: regulation.code})
                ON CREATE SET
                    r.name = regulation.name,
                    r.regulation_type = regulation.regulation_type,
                    r.category = regulation.category,
                    r.description = regulation.description,
                    r.requirements = regulation.requirements,
                    r.effective_date = regulation.effective_date,
                    r.expiration_date = regulation.expiration_date,
                    r.is_active = regulation.is_active,
                    r.source_url = regulation.source_url,
                    r.created_at = regulation.created_at,
                    r.updated_at = regulation.updated_at
                ON MATCH SET
                    r.name = regulation.name,
                    r.is_active = regulation.is_active,
                    r.updated_at = regulation.updated_at
                RETURN count(r) AS created
                """

                result = await self.session.run(query, regulations=batch)
                record = await result.single()
                batch_created = record["created"]
                total_created += batch_created
                self.stats["regulations"] += batch_created

                logger.info(f"Created {batch_created} regulation nodes (batch {i//self.batch_size + 1})")

            except Exception as e:
                logger.error(f"Error creating regulation nodes batch {i}: {e}")
                self.stats["errors"] += 1

        return total_created

    async def create_bill_nodes(self, bills: List[Dict[str, Any]]) -> int:
        """
        Create Bill and Patient nodes in batches.

        Args:
            bills: List of bill dictionaries with fields:
                - claim_id: Unique claim identifier (required)
                - patient_id: Patient identifier (required)
                - bill_date: Date of service (required)
                - provider_npi: Provider NPI (required)
                - insurer_id: Insurer ID (required)
                - hospital_id: Hospital ID (optional)
                - procedure_code: CPT procedure code (required)
                - diagnosis_code: ICD-10 diagnosis code (optional)
                - hcpcs_code: HCPCS code (optional)
                - ndc_code: NDC drug code (optional)
                - billed_amount: Amount billed (required)
                - allowed_amount: Allowed amount (optional)
                - paid_amount: Paid amount (optional)
                - status: Bill status (required)
                - status_date: Status change date (optional)
                - fraud_score: Fraud probability score (optional)
                - fraud_indicators: JSON of fraud patterns (optional)
                - compliance_issues: JSON of violations (optional)
                - medical_necessity_score: Medical necessity score (optional)
                - documentation_text: Clinical documentation (optional)
                - created_at: Creation timestamp
                - updated_at: Update timestamp

        Returns:
            Number of bill nodes created
        """
        if not bills:
            return 0

        total_created = 0
        for i in range(0, len(bills), self.batch_size):
            batch = bills[i:i + self.batch_size]

            try:
                # Create Patient nodes first (MERGE to avoid duplicates)
                patient_query = """
                UNWIND $bills AS bill
                MERGE (pat:Patient {id: bill.patient_id})
                RETURN count(pat) AS created
                """
                await self.session.run(patient_query, bills=batch)

                # Create Bill nodes
                query = """
                UNWIND $bills AS bill
                MATCH (pat:Patient {id: bill.patient_id})
                MERGE (b:Bill {claim_id: bill.claim_id})
                ON CREATE SET
                    b.patient_id = bill.patient_id,
                    b.bill_date = bill.bill_date,
                    b.provider_npi = bill.provider_npi,
                    b.insurer_id = bill.insurer_id,
                    b.hospital_id = bill.hospital_id,
                    b.procedure_code = bill.procedure_code,
                    b.diagnosis_code = bill.diagnosis_code,
                    b.hcpcs_code = bill.hcpcs_code,
                    b.ndc_code = bill.ndc_code,
                    b.billed_amount = bill.billed_amount,
                    b.allowed_amount = bill.allowed_amount,
                    b.paid_amount = bill.paid_amount,
                    b.status = bill.status,
                    b.status_date = bill.status_date,
                    b.fraud_score = bill.fraud_score,
                    b.fraud_indicators = bill.fraud_indicators,
                    b.compliance_issues = bill.compliance_issues,
                    b.medical_necessity_score = bill.medical_necessity_score,
                    b.documentation_text = bill.documentation_text,
                    b.created_at = bill.created_at,
                    b.updated_at = bill.updated_at
                ON MATCH SET
                    b.status = bill.status,
                    b.status_date = bill.status_date,
                    b.fraud_score = bill.fraud_score,
                    b.updated_at = bill.updated_at
                CREATE (pat)-[:HAS_BILL]->(b)
                RETURN count(b) AS created
                """

                result = await self.session.run(query, bills=batch)
                record = await result.single()
                batch_created = record["created"]
                total_created += batch_created
                self.stats["bills"] += batch_created

                logger.info(f"Created {batch_created} bill nodes (batch {i//self.batch_size + 1})")

            except Exception as e:
                logger.error(f"Error creating bill nodes batch {i}: {e}")
                self.stats["errors"] += 1

        return total_created

    # ========== RELATIONSHIP BUILDERS ==========

    async def create_provides_at_edges(self, edges: List[Dict[str, Any]]) -> int:
        """
        Create PROVIDES_AT relationships between providers and hospitals.

        Args:
            edges: List of edge dictionaries with fields:
                - provider_npi: Provider NPI (required)
                - hospital_npi: Hospital NPI (required)
                - start_date: Relationship start date (optional)

        Returns:
            Number of relationships created
        """
        if not edges:
            return 0

        total_created = 0
        for i in range(0, len(edges), self.batch_size):
            batch = edges[i:i + self.batch_size]

            try:
                query = """
                    UNWIND $edges AS edge
                    MATCH (p:Provider {npi: edge.provider_npi})
                    MATCH (h:Hospital {npi: edge.hospital_npi})
                    MERGE (p)-[r:PROVIDES_AT]->(h)
                    ON CREATE SET r.created_at = edge.start_date
                    RETURN count(r) AS created
                """

                result = await self.session.run(query, edges=batch)
                batch_created = await result.single()
                total_created += batch_created["created"]

            except Exception as e:
                logger.error(f"Error creating PROVIDES_AT edges batch {i}: {e}")
                self.stats["errors"] += 1

        self.stats["relationships"] += total_created
        return total_created

    async def create_insures_edges(self, edges: List[Dict[str, Any]]) -> int:
        """
        Create INSURES relationships between providers and insurers.

        Args:
            edges: List of edge dictionaries with fields:
                - provider_npi: Provider NPI (required)
                - payer_id: Insurer payer ID (required)
                - start_date: Relationship start date (optional)

        Returns:
            Number of relationships created
        """
        if not edges:
            return 0

        total_created = 0
        for i in range(0, len(edges), self.batch_size):
            batch = edges[i:i + self.batch_size]

            try:
                query = """
                UNWIND $edges AS edge
                MATCH (p:Provider {npi: edge.provider_npi})
                MATCH (i:Insurer {payer_id: edge.payer_id})
                MERGE (p)-[r:INSURES]->(i)
                ON CREATE SET r.created_at = edge.start_date
                RETURN count(r) AS created
                """

                result = await self.session.run(query, edges=batch)
                batch_created = await result.single()
                total_created += batch_created["created"]

            except Exception as e:
                logger.error(f"Error creating INSURES edges batch {i}: {e}")
                self.stats["errors"] += 1

        self.stats["relationships"] += total_created
        return total_created

    async def create_applies_to_edges(self, edges: List[Dict[str, Any]]) -> int:
        """
        Create APPLIES_TO relationships between regulations and bills.

        Args:
            edges: List of edge dictionaries with fields:
                - regulation_code: Regulation code (required)
                - bill_id: Bill claim ID (required)
                - start_date: Relationship start date (optional)

        Returns:
            Number of relationships created
        """
        if not edges:
            return 0

        total_created = 0
        for i in range(0, len(edges), self.batch_size):
            batch = edges[i:i + self.batch_size]

            try:
                query = """
                UNWIND $edges AS edge
                MATCH (r:Regulation {code: edge.regulation_code})
                MATCH (b:Bill {claim_id: edge.bill_id})
                MERGE (r)-[rel:APPLIES_TO]->(b)
                ON CREATE SET rel.created_at = edge.start_date
                RETURN count(rel) AS created
                """

                result = await self.session.run(query, edges=batch)
                batch_created = await result.single()
                total_created += batch_created["created"]

            except Exception as e:
                logger.error(f"Error creating APPLIES_TO edges batch {i}: {e}")
                self.stats["errors"] += 1

        self.stats["relationships"] += total_created
        return total_created

    async def create_flagged_for_fraud_edges(self, edges: List[Dict[str, Any]]) -> int:
        """
        Create FLAGGED_FOR_FRAUD relationships between bills and alerts.

        Args:
            edges: List of edge dictionaries with fields:
                - bill_id: Bill claim ID (required)
                - alert_id: Alert ID (required)
                - fraud_score: Fraud score (optional)
                - flag_date: Flag date (optional)

        Returns:
            Number of relationships created
        """
        if not edges:
            return 0

        total_created = 0
        for i in range(0, len(edges), self.batch_size):
            batch = edges[i:i + self.batch_size]

            try:
                query = """
                UNWIND $edges AS edge
                MATCH (b:Bill {claim_id: edge.bill_id})
                MATCH (a:Alert {id: edge.alert_id})
                MERGE (b)-[rel:FLAGGED_FOR_FRAUD]->(a)
                ON CREATE SET rel.created_at = edge.flag_date, rel.fraud_score = edge.fraud_score
                RETURN count(rel) AS created
                """

                result = await self.session.run(query, edges=batch)
                batch_created = await result.single()
                total_created += batch_created["created"]

            except Exception as e:
                logger.error(f"Error creating FLAGGED_FOR_FRAUD edges batch {i}: {e}")
                self.stats["errors"] += 1

        self.stats["relationships"] += total_created
        return total_created


    async def create_contract_with_edges(self, edges: List[Dict[str, Any]]) -> int:
        """
        Create CONTRACT_WITH relationships between providers and hospitals.

        Args:
            edges: List of edge dictionaries with fields:
                - provider_npi: Provider NPI (required)
                - hospital_npi: Hospital NPI (required)
                - start_date: Relationship start date (optional)

        Returns:
            Number of relationships created
        """
        if not edges:
            return 0

        total_created = 0
        for i in range(0, len(edges), self.batch_size):
            batch = edges[i:i + self.batch_size]

            try:
                query = """
                UNWIND $edges AS edge
                MATCH (p:Provider {npi: edge.provider_npi})
                MATCH (h:Hospital {npi: edge.hospital_npi})
                MERGE (p)-[r:CONTRACT_WITH]->(h)
                ON CREATE SET r.created_at = edge.start_date
                RETURN count(r) AS created
                """

                result = await self.session.run(query, edges=batch)
                batch_created = await result.single()
                total_created += batch_created["created"]

            except Exception as e:
                logger.error(f"Error creating CONTRACT_WITH edges batch {i}: {e}")
                self.stats["errors"] += 1

        self.stats["relationships"] += total_created
        return total_created

    async def create_owns_facility_edges(self, edges: List[Dict[str, Any]]) -> int:
        """
        Create OWNS_FACILITY relationships between provider owners and hospitals.

        Args:
            edges: List of edge dictionaries with fields:
                - provider_npi: Owner Provider NPI (required)
                - hospital_npi: Hospital NPI (required)
                - ownership_percentage: Ownership percentage (optional)
                - start_date: Relationship start date (optional)

        Returns:
            Number of relationships created
        """
        if not edges:
            return 0

        total_created = 0
        for i in range(0, len(edges), self.batch_size):
            batch = edges[i:i + self.batch_size]

            try:
                query = """
                    UNWIND $edges AS edge
                    MATCH (p:Provider {npi: edge.provider_npi})
                    MATCH (h:Hospital {npi: edge.hospital_npi})
                    MERGE (p)-[r:OWNS_FACILITY {ownership_pct: edge.ownership_percentage}]->(h)
                    ON CREATE SET r.created_at = edge.start_date
                    RETURN count(r) AS created
                """

                result = await self.session.run(query, edges=batch)
                batch_created = await result.single()
                total_created += batch_created["created"]

            except Exception as e:
                logger.error(f"Error creating OWNS_FACILITY edges batch {i}: {e}")
                self.stats["errors"] += 1

        self.stats["relationships"] += total_created
        return total_created

    async def create_affiliated_with_edges(self, edges: List[Dict[str, Any]]) -> int:
        """
        Create AFFILIATED_WITH relationships between hospitals (hospital systems).

        Args:
            edges: List of edge dictionaries with fields:
                - hospital_npi: Child/member hospital NPI (required)
                - parent_hospital_npi: Parent/system hospital NPI (required)
                - affiliation_type: Type of affiliation (optional, e.g., parent_system, sister_hospital)
                - start_date: Relationship start date (optional)

        Returns:
            Number of relationships created
        """
        if not edges:
            return 0

        total_created = 0
        for i in range(0, len(edges), self.batch_size):
            batch = edges[i:i + self.batch_size]

            try:
                query = """
                UNWIND $edges AS edge
                MATCH (h1:Hospital {npi: edge.hospital_npi})
                MATCH (h2:Hospital {npi: edge.parent_hospital_npi})
                MERGE (h1)-[r:AFFILIATED_WITH {affiliation_type: edge.affiliation_type}]->(h2)
                ON CREATE SET r.created_at = edge.start_date
                RETURN count(r) AS created
                """

                result = await self.session.run(query, edges=batch)
                batch_created = await result.single()
                total_created += batch_created["created"]

            except Exception as e:
                logger.error(f"Error creating AFFILIATED_WITH edges batch {i}: {e}")
                self.stats["errors"] += 1

        self.stats["relationships"] += total_created
        return total_created

    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about graph construction.

        Returns:
            Dictionary with counts of nodes, edges, and errors
        """
        return self.stats

    def reset_stats(self):
        """Reset statistics counters."""
        self.stats = {
            "providers": 0,
            "hospitals": 0,
            "insurers": 0,
            "regulations": 0,
            "bills": 0,
            "relationships": 0,
            "errors": 0
        }
