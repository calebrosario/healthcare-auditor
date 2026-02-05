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

    async def create_provides_at_edges(
        self,
        provider_npis: List[str],
        hospital_npis: List[str]
    ) -> int:
        """
        Create PROVIDES_AT relationships between providers and hospitals.

        Args:
            provider_npis: List of provider NPIs
            hospital_npis: List of hospital NPIs (same length)

        Returns:
            Number of relationships created
        """
        if not provider_npis or len(provider_npis) != len(hospital_npis):
            return 0

        total_created = 0
        for i in range(0, len(provider_npis), self.batch_size):
            provider_batch = provider_npis[i:i + self.batch_size]
            hospital_batch = hospital_npis[i:i + self.batch_size]

            # Pair providers with hospitals
            pairs = [
                {"provider_npi": p, "hospital_npi": h}
                for p, h in zip(provider_batch, hospital_batch)
            ]

            try:
                query = """
                UNWIND $pairs AS pair
                MATCH (p:Provider {npi: pair.provider_npi})
                MATCH (h:Hospital {npi: pair.hospital_npi})
                MERGE (p)-[r:PROVIDES_AT]->(h)
                ON CREATE SET r.created_at = $timestamp
                RETURN count(r) AS created
                """

                result = await self.session.run(
                    query,
                    pairs=pairs,
                    timestamp=datetime.utcnow().isoformat()
                )
                record = await result.single()
                batch_created = record["created"]
                total_created += batch_created
                self.stats["relationships"] += batch_created

                logger.info(f"Created {batch_created} PROVIDES_AT edges (batch {i//self.batch_size + 1})")

            except Exception as e:
                logger.error(f"Error creating PROVIDES_AT edges batch {i}: {e}")
                self.stats["errors"] += 1

        return total_created

    async def create_insures_edges(
        self,
        provider_npis: List[str],
        insurer_payer_ids: List[str]
    ) -> int:
        """
        Create INSURES relationships between providers and insurers.

        Args:
            provider_npis: List of provider NPIs
            insurer_payer_ids: List of insurer payer IDs (same length)

        Returns:
            Number of relationships created
        """
        if not provider_npis or len(provider_npis) != len(insurer_payer_ids):
            return 0

        total_created = 0
        for i in range(0, len(provider_npis), self.batch_size):
            provider_batch = provider_npis[i:i + self.batch_size]
            insurer_batch = insurer_payer_ids[i:i + self.batch_size]

            pairs = [
                {"provider_npi": p, "payer_id": i}
                for p, i in zip(provider_batch, insurer_batch)
            ]

            try:
                query = """
                UNWIND $pairs AS pair
                MATCH (p:Provider {npi: pair.provider_npi})
                MATCH (i:Insurer {payer_id: pair.payer_id})
                MERGE (p)-[r:INSURES]->(i)
                ON CREATE SET r.created_at = $timestamp
                RETURN count(r) AS created
                """

                result = await self.session.run(
                    query,
                    pairs=pairs,
                    timestamp=datetime.utcnow().isoformat()
                )
                record = await result.single()
                batch_created = record["created"]
                total_created += batch_created
                self.stats["relationships"] += batch_created

                logger.info(f"Created {batch_created} INSURES edges (batch {i//self.batch_size + 1})")

            except Exception as e:
                logger.error(f"Error creating INSURES edges batch {i}: {e}")
                self.stats["errors"] += 1

        return total_created

    async def create_applies_to_edges(
        self,
        claim_ids: List[str],
        regulation_codes: List[str]
    ) -> int:
        """
        Create APPLIES_TO relationships between bills and regulations.

        Args:
            claim_ids: List of bill claim IDs
            regulation_codes: List of regulation codes (same length)

        Returns:
            Number of relationships created
        """
        if not claim_ids or len(claim_ids) != len(regulation_codes):
            return 0

        total_created = 0
        for i in range(0, len(claim_ids), self.batch_size):
            claim_batch = claim_ids[i:i + self.batch_size]
            regulation_batch = regulation_codes[i:i + self.batch_size]

            pairs = [
                {"claim_id": c, "regulation_code": r}
                for c, r in zip(claim_batch, regulation_batch)
            ]

            try:
                query = """
                UNWIND $pairs AS pair
                MATCH (b:Bill {claim_id: pair.claim_id})
                MATCH (r:Regulation {code: pair.regulation_code})
                MERGE (r)-[rel:APPLIES_TO]->(b)
                ON CREATE SET rel.created_at = $timestamp
                RETURN count(rel) AS created
                """

                result = await self.session.run(
                    query,
                    pairs=pairs,
                    timestamp=datetime.utcnow().isoformat()
                )
                record = await result.single()
                batch_created = record["created"]
                total_created += batch_created
                self.stats["relationships"] += batch_created

                logger.info(f"Created {batch_created} APPLIES_TO edges (batch {i//self.batch_size + 1})")

            except Exception as e:
                logger.error(f"Error creating APPLIES_TO edges batch {i}: {e}")
                self.stats["errors"] += 1

        return total_created

    async def create_flagged_for_fraud_edges(
        self,
        claim_ids: List[str],
        alert_ids: List[int]
    ) -> int:
        """
        Create FLAGGED_FOR_FRAUD relationships between bills and alerts.

        Args:
            claim_ids: List of bill claim IDs
            alert_ids: List of alert IDs (same length)

        Returns:
            Number of relationships created
        """
        if not claim_ids or len(claim_ids) != len(alert_ids):
            return 0

        total_created = 0
        for i in range(0, len(claim_ids), self.batch_size):
            claim_batch = claim_ids[i:i + self.batch_size]
            alert_batch = alert_ids[i:i + self.batch_size]

            pairs = [
                {"claim_id": c, "alert_id": a}
                for c, a in zip(claim_batch, alert_batch)
            ]

            try:
                query = """
                UNWIND $pairs AS pair
                MATCH (b:Bill {claim_id: pair.claim_id})
                MATCH (a:Alert {id: pair.alert_id})
                MERGE (b)-[rel:FLAGGED_FOR_FRAUD]->(a)
                ON CREATE SET rel.created_at = $timestamp
                RETURN count(rel) AS created
                """

                result = await self.session.run(
                    query,
                    pairs=pairs,
                    timestamp=datetime.utcnow().isoformat()
                )
                record = await result.single()
                batch_created = record["created"]
                total_created += batch_created
                self.stats["relationships"] += batch_created

                logger.info(f"Created {batch_created} FLAGGED_FOR_FRAUD edges (batch {i//self.batch_size + 1})")

            except Exception as e:
                logger.error(f"Error creating FLAGGED_FOR_FRAUD edges batch {i}: {e}")
                self.stats["errors"] += 1

        return total_created


    async def create_contract_with_edges(
        self,
        provider_npis: List[str],
        hospital_npis: List[str],
        contract_types: Optional[List[str]] = None
    ) -> int:
        """
        Create CONTRACT_WITH relationships between providers and hospitals.

        Args:
            provider_npis: List of provider NPIs
            hospital_npis: List of hospital NPIs (same length)
            contract_types: List of contract types (optional, e.g., staff, admitting)

        Returns:
            Number of relationships created
        """
        if not provider_npis or len(provider_npis) != len(hospital_npis):
            return 0

        if contract_types is None:
            contract_types = ["staff"] * len(provider_npis)

        total_created = 0
        for i in range(0, len(provider_npis), self.batch_size):
            provider_batch = provider_npis[i:i + self.batch_size]
            hospital_batch = hospital_npis[i:i + self.batch_size]
            type_batch = contract_types[i:i + self.batch_size]

            pairs = [
                {"provider_npi": p, "hospital_npi": h, "contract_type": t}
                for p, h, t in zip(provider_batch, hospital_batch, type_batch)
            ]

            try:
                query = """
                UNWIND $pairs AS pair
                MATCH (p:Provider {npi: pair.provider_npi})
                MATCH (h:Hospital {npi: pair.hospital_npi})
                MERGE (p)-[r:CONTRACT_WITH {contract_type: pair.contract_type}]->(h)
                ON CREATE SET r.created_at = $timestamp
                RETURN count(r) AS created
                """

                result = await self.session.run(
                    query,
                    pairs=pairs,
                    timestamp=datetime.utcnow().isoformat()
                )
                record = await result.single()
                batch_created = record["created"]
                total_created += batch_created
                self.stats["relationships"] += batch_created

                logger.info(f"Created {batch_created} CONTRACT_WITH edges (batch {i//self.batch_size + 1})")

            except Exception as e:
                logger.error(f"Error creating CONTRACT_WITH edges batch {i}: {e}")
                self.stats["errors"] += 1

        return total_created

    async def create_owns_facility_edges(
        self,
        owner_npis: List[str],
        hospital_npis: List[str],
        ownership_percentages: Optional[List[float]] = None
    ) -> int:
        """
        Create OWNS_FACILITY relationships between provider owners and hospitals.

        Args:
            owner_npis: List of owner Provider NPIs
            hospital_npis: List of hospital NPIs (same length)
            ownership_percentages: List of ownership percentages (optional)

        Returns:
            Number of relationships created
        """
        if not owner_npis or len(owner_npis) != len(hospital_npis):
            return 0

        if ownership_percentages is None:
            ownership_percentages = [100.0] * len(owner_npis)

        total_created = 0
        for i in range(0, len(owner_npis), self.batch_size):
            owner_batch = owner_npis[i:i + self.batch_size]
            hospital_batch = hospital_npis[i:i + self.batch_size]
            percent_batch = ownership_percentages[i:i + self.batch_size]

            pairs = [
                {"owner_npi": o, "hospital_npi": h, "ownership_pct": p}
                for o, h, p in zip(owner_batch, hospital_batch, percent_batch)
            ]

            try:
                query = """
                UNWIND $pairs AS pair
                MATCH (o:Provider {npi: pair.owner_npi})
                MATCH (h:Hospital {npi: pair.hospital_npi})
                MERGE (o)-[r:OWNS_FACILITY {ownership_pct: pair.ownership_pct}]->(h)
                ON CREATE SET r.created_at = $timestamp
                RETURN count(r) AS created
                """

                result = await self.session.run(
                    query,
                    pairs=pairs,
                    timestamp=datetime.utcnow().isoformat()
                )
                record = await result.single()
                batch_created = record["created"]
                total_created += batch_created
                self.stats["relationships"] += batch_created

                logger.info(f"Created {batch_created} OWNS_FACILITY edges (batch {i//self.batch_size + 1})")

            except Exception as e:
                logger.error(f"Error creating OWNS_FACILITY edges batch {i}: {e}")
                self.stats["errors"] += 1

        return total_created

    async def create_affiliated_with_edges(
        self,
        hospital_npis_a: List[str],
        hospital_npis_b: List[str],
        affiliation_types: Optional[List[str]] = None
    ) -> int:
        """
        Create AFFILIATED_WITH relationships between hospitals (hospital systems).

        Args:
            hospital_npis_a: List of hospital NPIs (first side)
            hospital_npis_b: List of hospital NPIs (second side, same length)
            affiliation_types: List of affiliation types (optional, e.g., parent_system, sister_hospital)

        Returns:
            Number of relationships created
        """
        if not hospital_npis_a or len(hospital_npis_a) != len(hospital_npis_b):
            return 0

        if affiliation_types is None:
            affiliation_types = ["system"] * len(hospital_npis_a)

        total_created = 0
        for i in range(0, len(hospital_npis_a), self.batch_size):
            hospital_batch_a = hospital_npis_a[i:i + self.batch_size]
            hospital_batch_b = hospital_npis_b[i:i + self.batch_size]
            type_batch = affiliation_types[i:i + self.batch_size]

            pairs = [
                {"hospital_npi_a": a, "hospital_npi_b": b, "affiliation_type": t}
                for a, b, t in zip(hospital_batch_a, hospital_batch_b, type_batch)
            ]

            try:
                query = """
                UNWIND $pairs AS pair
                MATCH (h1:Hospital {npi: pair.hospital_npi_a})
                MATCH (h2:Hospital {npi: pair.hospital_npi_b})
                MERGE (h1)-[r:AFFILIATED_WITH {affiliation_type: pair.affiliation_type}]->(h2)
                ON CREATE SET r.created_at = $timestamp
                RETURN count(r) AS created
                """

                result = await self.session.run(
                    query,
                    pairs=pairs,
                    timestamp=datetime.utcnow().isoformat()
                )
                record = await result.single()
                batch_created = record["created"]
                total_created += batch_created
                self.stats["relationships"] += batch_created

                logger.info(f"Created {batch_created} AFFILIATED_WITH edges (batch {i//self.batch_size + 1})")

            except Exception as e:
                logger.error(f"Error creating AFFILIATED_WITH edges batch {i}: {e}")
                self.stats["errors"] += 1

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
