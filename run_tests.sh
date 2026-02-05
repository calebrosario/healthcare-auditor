#!/bin/bash

# Script to run knowledge graph tests

set -e

echo "========================================="
echo "Knowledge Graph Construction Tests"
echo "========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Error: pytest is not installed"
    echo "Run: pip install pytest pytest-asyncio"
    exit 1
fi

# Check required dependencies
echo "Checking dependencies..."
python3 -c "
import sys
try:
    import neo4j
    import pytest
    import pytest_asyncio
    print('✓ All dependencies installed')
except ImportError as e:
    print(f'✗ Missing: {e}')
    sys.exit(1)
"

echo ""
echo "Running unit tests..."
echo "========================================="
pytest tests/test_graph_builder.py -v --tb=short

echo ""
echo "========================================="
echo "Test Summary"
echo "========================================="
echo "All tests completed"
echo ""
echo "Note: These are unit tests with mocked Neo4j sessions."
echo "For integration testing, start Neo4j and run:"
echo "  python scripts/build_graph.py"
