"""Unit tests for GraphBuilder module."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import pytest
import pytest_asyncio

import sys

sys.path.insert(0, "/Users/calebrosario/Documents/sandbox/healthcare-auditor/backend")

from app.core.graph_builder import GraphBuilder


@pytest_asyncio.fixture
async def neo4j_session():
    """Create a mock Neo4j session for testing."""
    session = AsyncMock()

    async def mock_run(query, **kwargs):
        result = AsyncMock()
        batch = kwargs.get(
            "providers",
            kwargs.get(
                "hospitals",
                kwargs.get(
                    "insurers",
                    kwargs.get(
                        "regulations", kwargs.get("bills", kwargs.get("edges", []))
                    ),
                ),
            ),
        )
        result.single.return_value = {"created": len(batch)}
        return result

    session.run = mock_run
    return session


class TestGraphBuilder:
    """Test cases for GraphBuilder class."""

    @pytest.mark.asyncio
    async def test_create_provider_nodes(self, neo4j_session):
        """Test creating provider nodes."""
        builder = GraphBuilder(neo4j_session, batch_size=2)

        providers = [
            {
                "npi": "1234567890",
                "name": "Dr. John Doe",
                "provider_type": "individual",
                "specialty": "Cardiology",
                "city": "Los Angeles",
                "state": "CA",
                "zip_code": "90001",
            },
            {
                "npi": "9876543210",
                "name": "Dr. Jane Smith",
                "provider_type": "individual",
                "specialty": "Dermatology",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
            },
        ]

        count = await builder.create_provider_nodes(providers)

        assert count == 2

    @pytest.mark.asyncio
    async def test_create_provider_nodes_batching(self, neo4j_session):
        """Test batching behavior with more providers than batch_size."""
        builder = GraphBuilder(neo4j_session, batch_size=2)

        providers = [
            {"npi": str(i), "name": f"Provider {i}", "provider_type": "individual"}
            for i in range(1, 6)
        ]

        count = await builder.create_provider_nodes(providers)

        assert count == 5

    @pytest.mark.asyncio
    async def test_create_provider_nodes_empty(self, neo4j_session):
        """Test creating provider nodes with empty list."""
        builder = GraphBuilder(neo4j_session)

        count = await builder.create_provider_nodes([])

        assert count == 0

    @pytest.mark.asyncio
    async def test_create_hospital_nodes(self, neo4j_session):
        """Test creating hospital nodes."""
        builder = GraphBuilder(neo4j_session, batch_size=2)

        hospitals = [
            {
                "npi": "1234567890",
                "name": "City General Hospital",
                "type": "General Acute Care",
                "beds": 500,
                "accreditation": "Joint Commission",
            },
            {
                "npi": "9876543210",
                "name": "Mount Sinai Hospital",
                "type": "Acute Care",
                "beds": 800,
                "accreditation": "Joint Commission",
            },
        ]

        count = await builder.create_hospital_nodes(hospitals)

        assert count == 2

    @pytest.mark.asyncio
    async def test_create_insurer_nodes(self, neo4j_session):
        """Test creating insurer nodes."""
        builder = GraphBuilder(neo4j_session, batch_size=2)

        insurers = [
            {
                "payer_id": "001",
                "name": "Blue Cross Blue Shield",
                "coverage_type": "PPO",
                "state": "CA",
            },
            {
                "payer_id": "002",
                "name": "Aetna",
                "coverage_type": "HMO",
                "state": "NY",
            },
        ]

        count = await builder.create_insurer_nodes(insurers)

        assert count == 2

    @pytest.mark.asyncio
    async def test_create_regulation_nodes(self, neo4j_session):
        """Test creating regulation nodes."""
        builder = GraphBuilder(neo4j_session, batch_size=2)

        regulations = [
            {
                "code": "42CFR410.110",
                "name": "Privacy Rule",
                "type": "privacy",
                "category": "HIPAA",
                "requirements": "Patient consent required",
                "effective_date": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
            {
                "code": "42CFR410.120",
                "name": "Security Rule",
                "type": "security",
                "category": "HIPAA",
                "requirements": "Encryption required",
                "effective_date": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        ]

        count = await builder.create_regulation_nodes(regulations)

        assert count == 2

    @pytest.mark.asyncio
    async def test_create_bill_nodes(self, neo4j_session):
        """Test creating bill nodes."""
        builder = GraphBuilder(neo4j_session)

        bills = [
            {
                "claim_id": "CLAIM-001",
                "patient_id": "PATIENT-001",
                "provider_npi": "1234567890",
                "procedure_code": "99214",
                "diagnosis_code": "I10",
                "billed_amount": 150.00,
                "bill_date": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
            {
                "claim_id": "CLAIM-002",
                "patient_id": "PATIENT-002",
                "provider_npi": "9876543210",
                "procedure_code": "99213",
                "diagnosis_code": "J01",
                "billed_amount": 200.00,
                "bill_date": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
        ]

        count = await builder.create_bill_nodes(bills)

        assert count == 2

    @pytest.mark.asyncio
    async def test_create_provides_at_edges(self, neo4j_session):
        """Test creating PROVIDES_AT relationships."""
        builder = GraphBuilder(neo4j_session)

        edges = [
            {
                "provider_npi": "1234567890",
                "hospital_npi": "1234567890",
                "start_date": datetime.utcnow().isoformat(),
            },
            {
                "provider_npi": "9876543210",
                "hospital_npi": "9876543210",
                "start_date": datetime.utcnow().isoformat(),
            },
        ]

        count = await builder.create_provides_at_edges(edges)

        assert count == 2

    @pytest.mark.asyncio
    async def test_create_insures_edges(self, neo4j_session):
        """Test creating INSURES relationships."""
        builder = GraphBuilder(neo4j_session)

        edges = [
            {
                "provider_npi": "1234567890",
                "payer_id": "001",
                "start_date": datetime.utcnow().isoformat(),
            },
            {
                "provider_npi": "9876543210",
                "payer_id": "002",
                "start_date": datetime.utcnow().isoformat(),
            },
        ]

        count = await builder.create_insures_edges(edges)

        assert count == 2

    @pytest.mark.asyncio
    async def test_create_applies_to_edges(self, neo4j_session):
        """Test creating APPLIES_TO relationships."""
        builder = GraphBuilder(neo4j_session)

        edges = [
            {
                "regulation_code": "42CFR410.110",
                "bill_id": "CLAIM-001",
                "start_date": datetime.utcnow().isoformat(),
            },
            {
                "regulation_code": "42CFR410.120",
                "bill_id": "CLAIM-002",
                "start_date": datetime.utcnow().isoformat(),
            },
        ]

        count = await builder.create_applies_to_edges(edges)

        assert count == 2

    @pytest.mark.asyncio
    async def test_create_flagged_for_fraud_edges(self, neo4j_session):
        """Test creating FLAGGED_FOR_FRAUD relationships."""
        builder = GraphBuilder(neo4j_session)

        edges = [
            {
                "bill_id": "CLAIM-001",
                "alert_id": "ALERT-001",
                "fraud_score": 0.95,
                "flag_date": datetime.utcnow().isoformat(),
            },
            {
                "bill_id": "CLAIM-002",
                "alert_id": "ALERT-002",
                "fraud_score": 0.85,
                "flag_date": datetime.utcnow().isoformat(),
            },
        ]

        count = await builder.create_flagged_for_fraud_edges(edges)

        assert count == 2

    @pytest.mark.asyncio
    async def test_create_contract_with_edges(self, neo4j_session):
        """Test creating CONTRACT_WITH relationships."""
        builder = GraphBuilder(neo4j_session)

        edges = [
            {
                "provider_npi": "1234567890",
                "hospital_npi": "1234567890",
                "start_date": datetime.utcnow().isoformat(),
            },
            {
                "provider_npi": "9876543210",
                "hospital_npi": "9876543210",
                "start_date": datetime.utcnow().isoformat(),
            },
        ]

        count = await builder.create_contract_with_edges(edges)

        assert count == 2

    @pytest.mark.asyncio
    async def test_create_owns_facility_edges(self, neo4j_session):
        """Test creating OWNS_FACILITY relationships."""
        builder = GraphBuilder(neo4j_session)

        edges = [
            {
                "provider_npi": "1234567890",
                "hospital_npi": "1234567890",
                "ownership_percentage": 100,
                "start_date": datetime.utcnow().isoformat(),
            },
            {
                "provider_npi": "9876543210",
                "hospital_npi": "9876543210",
                "ownership_percentage": 100,
                "start_date": datetime.utcnow().isoformat(),
            },
        ]

        count = await builder.create_owns_facility_edges(edges)

        assert count == 2

    @pytest.mark.asyncio
    async def test_create_affiliated_with_edges(self, neo4j_session):
        """Test creating AFFILIATED_WITH relationships."""
        builder = GraphBuilder(neo4j_session)

        edges = [
            {
                "hospital_npi": "1234567890",
                "parent_hospital_npi": "9876543210",
                "affiliation_type": "system",
                "start_date": datetime.utcnow().isoformat(),
            },
            {
                "hospital_npi": "9998887777",
                "parent_hospital_npi": "9876543210",
                "affiliation_type": "network",
                "start_date": datetime.utcnow().isoformat(),
            },
        ]

        count = await builder.create_affiliated_with_edges(edges)

        assert count == 2

    @pytest.mark.asyncio
    async def test_get_stats(self, neo4j_session):
        """Test statistics retrieval."""
        builder = GraphBuilder(neo4j_session)

        # Create some nodes
        await builder.create_provider_nodes(
            [{"npi": "1234567890", "name": "Dr. Test", "provider_type": "individual"}]
        )

        await builder.create_hospital_nodes(
            [
                {
                    "npi": "1234567890",
                    "name": "Test Hospital",
                    "type": "General Acute Care",
                }
            ]
        )

        stats = builder.get_stats()

        assert stats["providers"] == 1
        assert stats["hospitals"] == 1

    @pytest.mark.asyncio
    async def test_reset_stats(self, neo4j_session):
        """Test statistics reset."""
        builder = GraphBuilder(neo4j_session)

        # Add some nodes
        await builder.create_provider_nodes(
            [{"npi": "1234567890", "name": "Dr. Test", "provider_type": "individual"}]
        )

        # Reset
        builder.reset_stats()

        stats = builder.get_stats()

        assert stats["providers"] == 0
        assert stats["hospitals"] == 0
