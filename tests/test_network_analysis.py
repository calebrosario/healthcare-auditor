# tests/test_network_analysis.py
import pytest
import sys

sys.path.insert(0, "/Users/calebrosario/Documents/sandbox/healthcare-auditor/backend")

from app.core.network_analysis import NetworkAnalyzer
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_pagerank_calculation():
    analyzer = NetworkAnalyzer(neo4j_session=AsyncMock())
    result = await analyzer.calculate_pagerank(provider_npi="1234567890")
    assert "provider_npi" in result
    assert "pagerank_score" in result


@pytest.mark.asyncio
async def test_louvain_communities():
    analyzer = NetworkAnalyzer(neo4j_session=AsyncMock())
    result = await analyzer.detect_communities()
    assert "communities" in result
    assert "community_count" in result


@pytest.mark.asyncio
async def test_analyze_connectivity():
    analyzer = NetworkAnalyzer(neo4j_session=AsyncMock())
    result = await analyzer.analyze_connectivity()
    assert "weakly_connected_components" in result
    assert "strongly_connected_components" in result
