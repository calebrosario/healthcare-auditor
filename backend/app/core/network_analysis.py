"""
Network analysis using Neo4j graph algorithms.
"""
import logging
from typing import Dict, Any, List, Optional
from neo4j import AsyncSession

logger = logging.getLogger(__name__)


class NetworkAnalyzer:
    """Neo4j graph algorithms for provider network analysis."""

    def __init__(self, neo4j_session: AsyncSession):
        """
        Initialize network analyzer.

        Args:
            neo4j_session: Async Neo4j session
        """
        self.neo4j = neo4j_session
        self.stats = {
            'pagerank_queries': 0,
            'louvain_queries': 0,
            'wcc_queries': 0
        }

    async def calculate_pagerank(
        self,
        provider_npi: str,
        max_iterations: int = 20
    ) -> Dict[str, Any]:
        """
        Calculate PageRank centrality for provider.

        Args:
            provider_npi: Provider NPI
            max_iterations: PageRank max iterations

        Returns:
            Dictionary with pagerank_score and network_position
        """
        try:
            query = """
            MATCH (p:Provider {npi: $npi})
            CALL gds.pageRank.stream({
                nodeProjection: 'Provider',
                relationshipProjection: {
                    PROVIDES_AT: {orientation: 'NATURAL'},
                    CONTRACT_WITH: {orientation: 'NATURAL'}
                },
                maxIterations: $maxIterations,
                dampingFactor: 0.85
            })
            YIELD nodeId, score
            WITH gds.util.asNode(nodeId) AS provider, score
            WHERE provider.npi = $npi
            RETURN provider.npi AS provider_npi,
                   score AS pagerank_score,
                   CASE
                       WHEN score > 0.8 THEN 'high_centrality'
                       WHEN score > 0.5 THEN 'medium_centrality'
                       ELSE 'low_centrality'
                   END AS network_position
            """

            result = await self.neo4j.run(
                query,
                parameters={'npi': provider_npi, 'maxIterations': max_iterations}
            )
            record = await result.single()

            if not record:
                logger.warning(f"PageRank: Provider {provider_npi} not found")
                return {'provider_npi': provider_npi, 'pagerank_score': 0.0, 'network_position': 'unknown'}

            self.stats['pagerank_queries'] += 1
            result_data = {
                'provider_npi': provider_npi,
                'pagerank_score': float(record['pagerank_score']),
                'network_position': record['network_position']
            }

            logger.debug(f"PageRank: {provider_npi} score={result_data['pagerank_score']:.4f}")
            return result_data

        except Exception as e:
            logger.error(f"PageRank calculation failed: {e}")
            return {'provider_npi': provider_npi, 'pagerank_score': 0.0, 'network_position': 'error'}

    async def detect_communities(
        self,
        max_levels: int = 10
    ) -> Dict[str, Any]:
        """
        Detect provider communities using Louvain algorithm.

        Args:
            max_levels: Louvain max hierarchy levels

        Returns:
            Dictionary with communities and modularity score
        """
        try:
            project_query = """
            CALL gds.graph.project('provider_network', {
                Provider: {
                    label: 'Provider',
                    properties: ['name', 'specialty']
                },
                PROVIDES_AT: {
                    type: 'PROVIDES_AT',
                    orientation: 'UNDIRECTED'
                },
                CONTRACT_WITH: {
                    type: 'CONTRACT_WITH',
                    orientation: 'UNDIRECTED'
                }
            })
            YIELD graphName, nodeCount, relationshipCount
            """

            await self.neo4j.run(project_query)

            louvain_query = """
            CALL gds.louvain.stream('provider_network', {
                includeIntermediateCommunities: false,
                maxLevels: $maxLevels
            })
            YIELD nodeId, communityId
            WITH communityId, count(*) AS community_size
            RETURN communityId, community_size
            ORDER BY community_size DESC
            """

            result = await self.neo4j.run(louvain_query, parameters={'maxLevels': max_levels})
            communities = [record.data() async for record in result]

            self.stats['louvain_queries'] += 1

            return {
                'communities': communities,
                'community_count': len(communities),
                'modularity': 0.0
            }

        except Exception as e:
            logger.error(f"Community detection failed: {e}")
            return {'communities': [], 'community_count': 0, 'modularity': 0.0}

    async def analyze_connectivity(
        self,
        provider_npi: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze weakly and strongly connected components.

        Args:
            provider_npi: Optional provider to analyze

        Returns:
            Dictionary with WCC/SCC statistics
        """
        try:
            wcc_query = """
            CALL gds.wcc.stream('provider_network')
            YIELD nodeId, componentId
            WITH componentId, count(*) AS component_size
            RETURN componentId, component_size
            ORDER BY component_size DESC
            LIMIT 10
            """

            wcc_result = await self.neo4j.run(wcc_query)
            wcc_components = [record.data() async for record in wcc_result]

            scc_query = """
            CALL gds.scc.stream('provider_network')
            YIELD nodeId, componentId
            WITH componentId, count(*) AS component_size
            RETURN componentId, component_size
            ORDER BY component_size DESC
            LIMIT 10
            """

            scc_result = await self.neo4j.run(scc_query)
            scc_components = [record.data() async for record in scc_result]

            self.stats['wcc_queries'] += 1

            return {
                'weakly_connected_components': wcc_components,
                'strongly_connected_components': scc_components,
                'wcc_count': len(wcc_components),
                'scc_count': len(scc_components)
            }

        except Exception as e:
            logger.error(f"Connectivity analysis failed: {e}")
            return {'weakly_connected_components': [], 'strongly_connected_components': []}

    async def analyze_provider_network(
        self,
        provider_npi: str
    ) -> Dict[str, Any]:
        """
        Run full network analysis for a provider.

        Args:
            provider_npi: Provider NPI

        Returns:
            Dictionary with all network analysis results
        """
        import asyncio

        pagerank_task = self.calculate_pagerank(provider_npi)
        connectivity_task = self.analyze_connectivity(provider_npi)

        results = await asyncio.gather(pagerank_task, connectivity_task, return_exceptions=True)

        return {
            'pagerank': results[0] if not isinstance(results[0], Exception) else {},
            'connectivity': results[1] if not isinstance(results[1], Exception) else {},
            'network_risk_score': self._calculate_network_risk(results)
        }

    def _calculate_network_risk(self, results: List[Any]) -> float:
        """Calculate network risk score (0-1, higher = more risk)."""
        risk = 0.0

        pagerank = results[0] if not isinstance(results[0], Exception) else {}
        if pagerank and pagerank.get('pagerank_score', 0) > 0.8:
            risk += 0.3

        connectivity = results[1] if not isinstance(results[1], Exception) else {}
        if connectivity and connectivity.get('wcc_count', 0) > 100:
            risk += 0.2

        return min(risk, 1.0)

    def get_stats(self) -> Dict[str, int]:
        """Get query statistics."""
        return self.stats.copy()
