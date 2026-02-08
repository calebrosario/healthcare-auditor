# Testing Guide

Comprehensive guide to testing Healthcare Auditor, including unit tests, integration tests, and test practices.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Best Practices](#test-best-practices)
- [Coverage](#coverage)
- [CI/CD](#cicd)

---

## Overview

Healthcare Auditor uses pytest for testing with a focus on:

- **Unit tests**: Test individual functions and classes in isolation
- **Integration tests**: Test component interactions
- **API tests**: Test HTTP endpoints
- **E2E tests**: Test complete workflows

### Test Goals

- 80%+ code coverage
- All public APIs tested
- All rules tested with valid and invalid inputs
- ML models tested with known datasets

---

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── __init__.py
│
├── unit/                   # Unit tests
│   ├── test_rules_engine.py
│   ├── test_ml_models.py
│   ├── test_graph_builder.py
│   ├── test_anomaly_detection.py
│   └── test_code_legality.py
│
├── integration/             # Integration tests
│   ├── test_database.py
│   ├── test_neo4j.py
│   └── test_redis.py
│
├── api/                    # API tests
│   ├── test_bills.py
│   ├── test_providers.py
│   ├── test_insurers.py
│   └── test_auth.py
│
└── e2e/                    # End-to-end tests
    └── test_validation_workflow.py
```

---

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_rules_engine.py

# Run specific test function
pytest tests/unit/test_rules_engine.py::TestICD10ValidationRule::test_valid_icd10_code
```

### Test Discovery

```bash
# Run tests matching pattern
pytest -k "icd10"

# Run tests in directory
pytest tests/unit/

# Run tests with marker
pytest -m "slow"
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (uses all CPU cores)
pytest -n auto

# Specify number of workers
pytest -n 4
```

### Coverage

```bash
# Generate coverage report
pytest --cov=backend/app --cov-report=html

# View HTML report
open htmlcov/index.html  # macOS
# or open in browser

# Coverage to terminal
pytest --cov=backend/app --cov-report=term-missing

# Coverage with minimum threshold (fail if below 80%)
pytest --cov=backend/app --cov-fail-under=80
```

---

## Writing Tests

### Test Fixtures (conftest.py)

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db
from app.models.base import Base

@pytest.fixture
async def db():
    """Create a test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

@pytest.fixture
async def client(db: AsyncSession):
    """Create a test client with database."""
    def override_get_db():
        return db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
```

### Unit Tests

#### Test Simple Function

```python
import pytest
from app.rules.coding_rules import ICD10ValidationRule

@pytest.mark.asyncio
async def test_valid_icd10_code():
    """Test valid ICD-10 code passes validation."""
    rule = ICD10ValidationRule()

    result = await rule.validate(
        bill=MockBill(diagnosis_code="I10"),
        context={}
    )

    assert result.is_valid is True
    assert result.message is None

@pytest.mark.asyncio
async def test_invalid_icd10_code():
    """Test invalid ICD-10 code fails validation."""
    rule = ICD10ValidationRule()

    result = await rule.validate(
        bill=MockBill(diagnosis_code="INVALID"),
        context={}
    )

    assert result.is_valid is False
    assert "Invalid ICD-10 format" in result.message
```

#### Test with Parametrization

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("code,is_valid", [
    ("I10", True),
    ("E11.9", True),
    ("J45.909", True),
    ("INVALID", False),
    ("123", False),
    (None, False),
])
async def test_icd10_validation(code, is_valid):
    """Test ICD-10 validation with various codes."""
    rule = ICD10ValidationRule()

    result = await rule.validate(
        bill=MockBill(diagnosis_code=code),
        context={}
    )

    assert result.is_valid == is_valid
```

### Integration Tests

#### Database Integration Test

```python
import pytest
from sqlalchemy import select
from app.models.bill import Bill

@pytest.mark.asyncio
async def test_create_and_retrieve_bill(db: AsyncSession):
    """Test creating and retrieving a bill from database."""
    # Create bill
    bill = Bill(
        claim_id="TEST-001",
        patient_id="PATIENT-001",
        provider_id=1,
        procedure_code="99214",
        diagnosis_code="I10",
        billed_amount=150.00
    )

    db.add(bill)
    await db.commit()
    await db.refresh(bill)

    # Retrieve bill
    result = await db.execute(
        select(Bill).where(Bill.claim_id == "TEST-001")
    )
    retrieved = result.scalar_one_or_none()

    assert retrieved is not None
    assert retrieved.claim_id == "TEST-001"
    assert retrieved.billed_amount == 150.00
```

### API Tests

#### Test API Endpoint

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_validate_bill_endpoint(client: AsyncClient):
    """Test bill validation endpoint."""
    response = await client.post(
        "/api/v1/bills/validate",
        json={
            "patient_id": "PATIENT-001",
            "provider_npi": "1234567890",
            "insurer_id": 1,
            "procedure_code": "99214",
            "diagnosis_code": "I10",
            "billed_amount": 150.00
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert "fraud_score" in data
    assert "compliance_score" in data
    assert "fraud_risk_level" in data

@pytest.mark.asyncio
async def test_validate_bill_invalid_input(client: AsyncClient):
    """Test validation with invalid input."""
    response = await client.post(
        "/api/v1/bills/validate",
        json={
            "patient_id": "PATIENT-001",
            "provider_npi": "123",  # Invalid NPI
            "procedure_code": "99214",
            "diagnosis_code": "I10",
            "billed_amount": 150.00
        }
    )

    assert response.status_code == 422  # Validation error
```

### Mocking Tests

#### Mock External Dependencies

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_rule_with_mocked_neo4j():
    """Test rule with mocked Neo4j connection."""
    # Mock Neo4j driver
    mock_neo4j = AsyncMock()
    mock_neo4j.run.return_value.data = []

    rule = MedicalNecessityRule(neo4j_driver=mock_neo4j)

    result = await rule.validate(
        bill=MockBill(),
        context={}
    )

    # Verify mock was called
    mock_neo4j.run.assert_called_once()

    # Assertions
    assert result.is_valid is True
```

---

## Test Best Practices

### AAA Pattern (Arrange-Act-Assert)

```python
# Good: Clear separation
def test_calculate_score():
    """Test score calculation."""
    # Arrange
    rule_results = [
        ValidationResult(is_valid=False, score=0.8),
        ValidationResult(is_valid=True, score=0.0)
    ]
    weights = {'rule1': 0.5, 'rule2': 0.5}

    # Act
    score = calculate_fraud_score(rule_results, weights)

    # Assert
    assert score == 0.4

# Bad: Mixed responsibilities
def test_calculate_score():
    score = calculate_fraud_score([
        ValidationResult(False, 0.8),
        ValidationResult(True, 0.0)
    ], {'rule1': 0.5})
    assert score == 0.4
```

### Descriptive Test Names

```python
# Good: Clear what's being tested
def test_icd10_validation_with_valid_code_returns_true():
    """Test that valid ICD-10 code passes validation."""
    pass

def test_icd10_validation_with_invalid_code_returns_false():
    """Test that invalid ICD-10 code fails validation."""
    pass

# Bad: Vague test name
def test_validation():
    pass
```

### One Assertion Per Test

```python
# Good: Focused test
def test_bill_validation_returns_correct_fraud_score():
    """Test fraud score calculation."""
    result = validate_bill(test_bill)
    assert result.fraud_score == 0.75

def test_bill_validation_returns_correct_risk_level():
    """Test risk level classification."""
    result = validate_bill(test_bill)
    assert result.risk_level == "high"

# Bad: Multiple assertions
def test_bill_validation():
    result = validate_bill(test_bill)
    assert result.fraud_score == 0.75
    assert result.risk_level == "high"
    assert result.compliance_score == 0.85
```

### Test Edge Cases

```python
@pytest.mark.parametrize("value,expected", [
    (0, False),        # Minimum value
    (1.50, True),     # Valid range
    (10000.00, False), # Maximum value
    (-1.00, False),    # Negative
    (None, False),     # Null
    ("abc", False),     # Wrong type
])
def test_billed_amount_validation(value, expected):
    """Test billed amount validation with edge cases."""
    result = validate_amount(value)
    assert result.is_valid == expected
```

### Test Isolation

```python
# Each test should be independent
@pytest.mark.asyncio
async def test_create_bill(db: AsyncSession):
    bill = Bill(claim_id="TEST-001", ...)
    db.add(bill)
    await db.commit()
    # Test passes or fails independently

@pytest.mark.asyncio
async def test_create_another_bill(db: AsyncSession):
    # This test doesn't depend on previous test
    bill = Bill(claim_id="TEST-002", ...)
    db.add(bill)
    await db.commit()
    # Test passes or fails independently
```

---

## Coverage

### Coverage Goals

| Component | Target | Current |
|-----------|---------|---------|
| Rules Engine | 90% | 85% |
| ML Models | 85% | 80% |
| API Endpoints | 95% | 90% |
| Core Logic | 90% | 85% |
| **Overall** | **80%** | **83%** |

### Generate Coverage Report

```bash
# Full coverage report
pytest --cov=backend/app --cov-report=html --cov-report=xml

# View in browser
open htmlcov/index.html

# For CI/CD (XML format for coverage badge)
pytest --cov=backend/app --cov-report=xml
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = backend/app
omit =
    */tests/*
    */venv/*
    */migrations/*

[report]
precision = 2
show_missing = True
skip_covered = False
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

---

## CI/CD

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

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
          pip install poetry
          poetry install

      - name: Run linters
        run: |
          poetry run black --check backend/app
          poetry run ruff check backend/app
          poetry run mypy backend/app

      - name: Run tests
        run: |
          poetry run pytest tests/ --cov=backend/app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-requests
```

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

---

## Testing ML Components

### Mock ML Predictions

```python
import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_ml_prediction_with_mocked_model():
    """Test ML prediction with mocked model."""
    with patch('app.core.ml_models.RandomForest.predict') as mock_predict:
        # Set up mock return value
        mock_predict.return_value = [0.85]

        # Test code that uses ML model
        result = await predict_fraud(bill_data)

        # Verify mock was called
        mock_predict.assert_called_once()

        # Assertions
        assert result.fraud_probability == 0.85
```

### Test with Known Datasets

```python
import pytest
import pandas as pd

@pytest.mark.asyncio
async def test_ml_model_accuracy():
    """Test ML model accuracy with known dataset."""
    # Load known test data
    test_data = pd.read_csv('tests/data/known_fraud.csv')

    predictions = []
    actuals = test_data['is_fraud'].tolist()

    for _, row in test_data.iterrows():
        pred = await ml_model.predict(row.to_dict())
        predictions.append(pred > 0.5)

    # Calculate accuracy
    accuracy = sum(p == a for p, a in zip(predictions, actuals)) / len(actuals)

    # Assert minimum accuracy
    assert accuracy > 0.85, f"Model accuracy {accuracy} below threshold 0.85"
```

---

## Resources

- **[Pytest Documentation](https://docs.pytest.org/)** - Testing framework
- **[AsyncIO Testing](https://pytest-asyncio.readthedocs.io/)** - Async test support
- **[Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)** - Mocking and patching
- **[Coverage.py](https://coverage.readthedocs.io/)** - Code coverage tool

---

## Next Steps

- **[Development Guide](Development-Guide.md)** - Coding standards
- **[API Reference](API-Reference.md)** - Endpoint documentation
- **[Troubleshooting](Troubleshooting.md)** - Common issues
