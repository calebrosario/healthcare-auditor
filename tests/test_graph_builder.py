"""
Unit tests for GraphBuilder module.
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from datetime import datetime

import sys
sys.path.insert(0, '/Users/calebrosario/Documents/sandbox/healthcare-auditor/backend')

from app.core.graph_builder import GraphBuilder


class TestGraphBuilder:
    """Test cases for GraphBuilder class."""

    @pytest.fixture
    async def neo4j_session(self):
        """Create a mock Neo4j session for testing."""
        session = AsyncMock()
        
        # Mock session.run to return results
        async def mock_run(query, **kwargs):
            result = AsyncMock()
            if "MERGE (p:Provider" in query:
                await result.single.return_value({"created": 1})
            elif "MERGE (h:Hospital" in query:
                await result.single.return_value({"created": 1})
            elif "MERGE (i:Insurer" in query:
                await result.single.return_value({"created": 1})
            elif "MERGE (r:Regulation" in query:
                await result.single.return_value({"created": 1})
            elif "MERGE (b:Bill" in query:
                await result.single.return_value({"created": 1})
            elif "PROVIDES_AT" in query:
                await result.single.return_value({"created": 1})
            elif "INSURES" in query:
                await result.single.return_value({"created": 1})
            elif "APPLIES_TO" in query:
                await result.single.return_value({"created": 1})
            elif "FLAGGED_FOR_FRAUD" in query:
                await result.single.return_value({"created": 1})
            elif "CONTRACT_WITH" in query:
                await result.single.return_value({"created": 1})
            elif "OWNS_FACILITY" in query:
                await result.single.return_value({"created": 1})
            elif "AFFILIATED_WITH" in query:
                await result.single.return_value({"created": 1})
            else:
                await result.single.return_value({"created": 0})
            return result
        
        session.run = mock_run
        return session

    def test_init(self):
        """Test GraphBuilder initialization."""
        session = AsyncMock()
        builder = GraphBuilder(session, batch_size=100)
        
        assert builder.session == session
        assert builder.batch_size == 100
        assert builder.stats["providers"] == 0
        assert builder.stats["hospitals"] == 0

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
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            },
            {
                "npi": "1234567891",
                "name": "Dr. Jane Smith",
                "provider_type": "individual",
                "specialty": "Dermatology",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94102",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        ]
        
        count = await builder.create_provider_nodes(providers)
        
        assert count == 2
        assert builder.stats["providers"] == 2
        assert builder.stats["errors"] == 0

    @pytest.mark.asyncio
    async def test_create_provider_nodes_empty(self, neo4j_session):
        """Test creating provider nodes with empty list."""
        builder = GraphBuilder(neo4j_session)
        count = await builder.create_provider_nodes([])
        assert count == 0
        assert builder.stats["providers"] == 0

    @pytest.mark.asyncio
    async def test_create_provider_nodes_batching(self, neo4j_session):
        """Test batch processing with more providers than batch size."""
        builder = GraphBuilder(neo4j_session, batch_size=2)
        
        providers = [
            {
                "npi": f"{i}",
                "name": f"Provider {i}",
                "provider_type": "individual",
                "city": "City",
                "state": "CA",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            for i in range(5)
        ]
        
        count = await builder.create_provider_nodes(providers)
        
        assert count == 5
        assert builder.stats["providers"] == 5

    @pytest.mark.asyncio
    async def test_create_hospital_nodes(self, neo4j_session):
        """Test creating hospital nodes."""
        builder = GraphBuilder(neo4j_session)
        
        hospitals = [
            {
                "npi": "0987654321",
                "id": 1,
                "name": "City Hospital",
                "hospital_type": "acute_care",
                "city": "Los Angeles",
                "state": "CA",
                "bed_count": 500,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        ]
        
        count = await builder.create_hospital_nodes(hospitals)
        
        assert count == 1
        assert builder.stats["hospitals"] == 1

    @pytest.mark.asyncio
    async def test_create_insurer_nodes(self, neo4j_session):
        """Test creating insurer nodes."""
        builder = GraphBuilder(neo4j_session)
        
        insurers = [
            {
                "payer_id": "BCBS",
                "id": 1,
                "name": "Blue Cross Blue Shield",
                "coverage_type": "commercial",
                "state": "CA",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        ]
        
        count = await builder.create_insurer_nodes(insurers)
        
        assert count == 1
        assert builder.stats["insurers"] == 1

    @pytest.mark.asyncio
    async def test_create_regulation_nodes(self, neo4j_session):
        """Test creating regulation nodes."""
        builder = GraphBuilder(neo4j_session)
        
        regulations = [
            {
                "code": "HIPAA_2003_164",
                "name": "HIPAA Privacy Rule",
                "regulation_type": "federal",
                "category": "privacy",
                "description": "Health Insurance Portability and Accountability Act",
                "is_active": True,
                "effective_date": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        ]
        
        count = await builder.create_regulation_nodes(regulations)
        
        assert count == 1
        assert builder.stats["regulations"] == 1

    @pytest.mark.asyncio
    async def test_create_bill_nodes(self, neo4j_session):
        """Test creating bill nodes."""
        builder = GraphBuilder(neo4j_session)
        
        bills = [
            {
                "claim_id": "CLAIM001",
                "patient_id": "PATIENT001",
                "bill_date": datetime.utcnow().isoformat(),
                "provider_npi": "1234567890",
                "insurer_id": 1,
                "hospital_id": None,
                "procedure_code": "99213",
                "diagnosis_code": "I10",
                "billed_amount": 150.00,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        ]
        
        count = await builder.create_bill_nodes(bills)
        
        assert count == 1
        assert builder.stats["bills"] == 1

    @pytest.mark.asyncio
    async def test_create_provides_at_edges(self, neo4j_session):
        """Test creating PROVIDES_AT relationships."""
        builder = GraphBuilder(neo4j_session)
        
        provider_npis = ["1234567890"]
        hospital_npis = ["0987654321"]
        
        count = await builder.create_provides_at_edges(provider_npis, hospital_npis)
        
        assert count == 1
        assert builder.stats["relationships"] == 1

    @pytest.mark.asyncio
    async def test_create_insures_edges(self, neo4j_session):
        """Test creating INSURES relationships."""
        builder = GraphBuilder(neo4j_session)
        
        provider_npis = ["1234567890"]
        insurer_payer_ids = ["BCBS"]
        
        count = await builder.create_insures_edges(provider_npis, insurer_payer_ids)
        
        assert count == 1
        assert builder.stats["relationships"] == 1

    @pytest.mark.asyncio
    async def test_create_applies_to_edges(self, neo4j_session):
        """Test creating APPLIES_TO relationships."""
        builder = GraphBuilder(neo4j_session)
        
        claim_ids = ["CLAIM001"]
        regulation_codes = ["HIPAA_2003_164"]
        
        count = await builder.create_applies_to_edges(claim_ids, regulation_codes)
        
        assert count == 1
        assert builder.stats["relationships"] == 1

    @pytest.mark.asyncio
    async def test_create_flagged_for_fraud_edges(self, neo4j_session):
        """Test creating FLAGGED_FOR_FRAUD relationships."""
        builder = GraphBuilder(neo4j_session)
        
        claim_ids = ["CLAIM001"]
        alert_ids = [1]
        
        count = await builder.create_flagged_for_fraud_edges(claim_ids, alert_ids)
        
        assert count == 1
        assert builder.stats["relationships"] == 1

    @pytest.mark.asyncio
    async def test_create_contract_with_edges(self, neo4j_session):
        """Test creating CONTRACT_WITH relationships."""
        builder = GraphBuilder(neo4j_session)
        
        provider_npis = ["1234567890"]
        hospital_npis = ["0987654321"]
        contract_types = ["staff"]
        
        count = await builder.create_contract_with_edges(provider_npis, hospital_npis, contract_types)
        
        assert count == 1
        assert builder.stats["relationships"] == 1

    @pytest.mark.asyncio
    async def test_create_owns_facility_edges(self, neo4j_session):
        """Test creating OWNS_FACILITY relationships."""
        builder = GraphBuilder(neo4j_session)
        
        owner_npis = ["1234567890"]
        hospital_npis = ["0987654321"]
        ownership_percentages = [100.0]
        
        count = await builder.create_owns_facility_edges(owner_npis, hospital_npis, ownership_percentages)
        
        assert count == 1
        assert builder.stats["relationships"] == 1

    @pytest.mark.asyncio
    async def test_create_affiliated_with_edges(self, neo4j_session):
        """Test creating AFFILIATED_WITH relationships."""
        builder = GraphBuilder(neo4j_session)
        
        hospital_npis_a = ["0987654321"]
        hospital_npis_b = ["0987654322"]
        affiliation_types = ["system"]
        
        count = await builder.create_affiliated_with_edges(hospital_npis_a, hospital_npis_b, affiliation_types)
        
        assert count == 1
        assert builder.stats["relationships"] == 1

    def test_get_stats(self):
        """Test getting statistics."""
        session = AsyncMock()
        builder = GraphBuilder(session)
        builder.stats["providers"] = 10
        builder.stats["relationships"] = 5
        builder.stats["errors"] = 2
        
        stats = builder.get_stats()
        
        assert stats["providers"] == 10
        assert stats["relationships"] == 5
        assert stats["errors"] == 2

    def test_reset_stats(self):
        """Test resetting statistics."""
        session = AsyncMock()
        builder = GraphBuilder(session)
        builder.stats["providers"] = 10
        
        builder.reset_stats()
        
        assert builder.stats["providers"] == 0
        assert builder.stats["hospitals"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
