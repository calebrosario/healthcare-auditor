# Knowledge Graph Construction Tests

This directory contains unit tests for the knowledge graph construction module.

## Running Tests

### Prerequisites:
1. Install pytest:
   ```bash
   pip install pytest pytest-asyncio
   ```

2. Install dependencies:
   ```bash
   pip install neo4j sqlalchemy
   ```

### Running All Tests:
```bash
cd /Users/calebrosario/Documents/sandbox/healthcare-auditor
pytest tests/test_graph_builder.py -v
```

### Running Specific Tests:
```bash
# Test only provider node creation
pytest tests/test_graph_builder.py::TestGraphBuilder::test_create_provider_nodes -v

# Test only relationship builders
pytest tests/test_graph_builder.py::TestGraphBuilder::test_create_provides_at_edges -v
```

## Test Coverage

- `test_init`: GraphBuilder initialization
- `test_create_provider_nodes`: Provider node creation
- `test_create_provider_nodes_empty`: Empty list handling
- `test_create_provider_nodes_batching`: Batch processing
- `test_create_hospital_nodes`: Hospital node creation
- `test_create_insurer_nodes`: Insurer node creation
- `test_create_regulation_nodes`: Regulation node creation
- `test_create_bill_nodes`: Bill node creation
- `test_create_provides_at_edges`: PROVIDES_AT relationships
- `test_create_insures_edges`: INSURES relationships
- `test_create_applies_to_edges`: APPLIES_TO relationships
- `test_create_flagged_for_fraud_edges`: FLAGGED_FOR_FRAUD relationships
- `test_create_contract_with_edges`: CONTRACT_WITH relationships
- `test_create_owns_facility_edges`: OWNS_FACILITY relationships
- `test_create_affiliated_with_edges`: AFFILIATED_WITH relationships
- `test_get_stats`: Statistics retrieval
- `test_reset_stats`: Statistics reset

## Test Data

All tests use mock data that represents:
- Providers with NPI, name, type, specialty, location
- Hospitals with NPI, name, type, bed count
- Insurers with payer_id, name, coverage type
- Regulations with code, name, type, category
- Bills with claim_id, amounts, status
- Relationships with proper entity references

## Integration Testing

For full integration testing with actual Neo4j:

1. Start Neo4j instance:
   ```bash
   docker run -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:latest
   ```

2. Create sample PostgreSQL database:
   ```bash
   # Create tables first
   python -c "from backend.app.core.database import init_db; import asyncio; asyncio.run(init_db())"
   
   # Run full graph construction
   python scripts/build_graph.py
   ```

3. Verify graph:
   ```cypher
   // In Neo4j browser at http://localhost:7474
   MATCH (p:Provider) RETURN count(p) AS provider_count;
   MATCH (h:Hospital) RETURN count(h) AS hospital_count;
   MATCH (p:Provider)-[:PROVIDES_AT]->(h:Hospital) RETURN count(*) AS relationship_count;
   ```

## Known Limitations

1. **Mock Session**: Tests use AsyncMock for Neo4j session, so actual Cypher queries are not executed.
2. **No Real Database**: Tests don't require PostgreSQL to be running.
3. **Unit Scope**: Tests verify method signatures, batch processing, and statistics tracking.
4. **Integration Tests**: Require full Neo4j and PostgreSQL setup (see Integration Testing above).

## Future Test Enhancements

1. Add integration tests with real Neo4j instance
2. Add performance benchmarks for batch sizes
3. Add error handling tests (network failures, constraint violations)
4. Add data validation tests (invalid NPI formats, missing required fields)
5. Add concurrent load tests (multiple builders running in parallel)

## CI/CD Integration

For GitHub Actions or other CI:

```yaml
name: Run Knowledge Graph Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install pytest pytest-asyncio neo4j sqlalchemy
      - name: Run tests
        run: |
          pytest tests/test_graph_builder.py -v --cov=backend/app/core --cov-report=html
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```
