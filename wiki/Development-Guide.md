# Development Guide

**Tags**: #development #coding-standards #best-practices #workflow #testing #git

This guide covers coding standards, development workflow, and best practices for contributing to Healthcare Auditor.

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Development Workflow](#development-workflow)
- [Adding Features](#adding-features)
- [Code Review](#code-review)
- [Documentation](#documentation)

---

## Getting Started

### Prerequisites

Before you start developing, ensure you have:

- Python 3.11+ installed
- Poetry for dependency management
- Git configured
- PostgreSQL, Neo4j, and Redis running locally or via Docker
- IDE with Python support (VS Code, PyCharm, etc.)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/calebrosario/healthcare-auditor.git
cd healthcare-auditor

# Create feature branch
git checkout -b feature/your-feature-name

# Install dependencies
cd backend
poetry install

# Activate virtual environment
poetry shell

# Run pre-commit hooks (optional)
pre-commit install

# Start development server
uvicorn app.main:app --reload --port 8000
```

---

## Project Structure

```
healthcare-auditor/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   ├── dependencies.py      # Dependency injection
│   │   │
│   │   ├── api/                # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── bills.py        # Bills endpoints
│   │   │   ├── providers.py    # Provider endpoints
│   │   │   ├── insurers.py     # Insurer endpoints
│   │   │   ├── knowledge_graph.py
│   │   │   ├── regulations.py   # Regulation endpoints
│   │   │   ├── alerts.py       # Alert endpoints
│   │   │   ├── health.py       # Health check endpoint
│   │   │   └── auth.py        # Authentication endpoints
│   │   │
│   │   ├── core/               # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── database.py     # Database connection
│   │   │   ├── neo4j.py       # Neo4j connection
│   │   │   ├── rules_engine.py # Rules engine orchestrator
│   │   │   ├── graph_builder.py # Graph data builder
│   │   │   ├── anomaly_detection.py
│   │   │   ├── ml_models.py    # ML models
│   │   │   ├── network_analysis.py
│   │   │   ├── code_legality.py
│   │   │   ├── risk_scoring.py # Risk aggregation
│   │   │   └── train_models.py # Model training
│   │   │
│   │   ├── models/             # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── bill.py
│   │   │   ├── provider.py
│   │   │   ├── insurer.py
│   │   │   ├── regulation.py
│   │   │   └── compliance_check.py
│   │   │
│   │   ├── rules/              # Rule implementations
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # Base rule class
│   │   │   ├── coding_rules.py
│   │   │   ├── medical_necessity_rules.py
│   │   │   ├── frequency_rules.py
│   │   │   └── billing_rules.py
│   │   │
│   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── bill.py
│   │   │   ├── provider.py
│   │   │   └── response.py
│   │   │
│   │   ├── security/           # Security & auth
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # JWT authentication
│   │   │   └── permissions.py # Role-based access
│   │   │
│   │   └── middleware.py       # Custom middleware
│   │
│   ├── main.py                # Application entry point
│   └── pyproject.toml        # Poetry configuration
│
├── scripts/                   # Utility scripts
│   ├── build_graph.py         # Knowledge graph builder
│   ├── validate_bills.py      # Standalone validator
│   └── train_models.py       # ML model training
│
├── tests/                     # Test suite
│   ├── conftest.py           # Pytest fixtures
│   ├── test_rules_engine.py    # Rules engine tests
│   ├── test_ml_models.py      # ML tests
│   ├── test_graph_builder.py   # Graph tests
│   └── test_api/             # API tests
│       ├── test_bills.py
│       └── test_providers.py
│
├── docs/                     # Documentation
│   ├── KNOWLEDGE_GRAPH_STATE_MACHINE.md
│   ├── RULES_ENGINE_STATE_MACHINE.md
│   └── ML_PIPELINE_STATE_MACHINE.md
│
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
├── docker-compose.yml        # Docker services
├── README.md               # Project overview
└── LICENSE                 # License file
```

---

## Coding Standards

### Python Code Style

#### PEP 8 Compliance

We follow PEP 8 style guide with these tools:

```bash
# Format code with Black
black backend/app/

# Lint with Ruff
ruff check backend/app/

# Type check with MyPy
mypy backend/app/
```

#### Code Formatting (Black)

```python
# Use 120 character line length
# Use 4 spaces indentation
# Use double quotes for strings
# Add space after commas in function calls

# Good:
def validate_bill(
    patient_id: str,
    provider_npi: str,
    procedure_code: str,
) -> ValidationResult:
    """Validate a medical bill."""
    return ValidationResult(is_valid=True)

# Bad:
def validate_bill(patient_id:str,provider_npi:str,procedure_code:str)->ValidationResult:
    return ValidationResult(is_valid=True)
```

#### Import Organization

```python
# 1. Standard library imports
import asyncio
import logging
from datetime import datetime, timedelta

# 2. Third-party imports
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# 3. Local application imports
from app.core.database import get_db
from app.models.bill import Bill
from app.rules.base import BaseRule
```

#### Type Hints

All functions must include type hints:

```python
from typing import List, Optional
from pydantic import BaseModel

class BillValidationRequest(BaseModel):
    patient_id: str
    provider_npi: str
    procedure_code: str
    billed_amount: float

async def validate_bill(
    request: BillValidationRequest
) -> BillValidationResponse:
    """Validate a medical bill against fraud detection rules."""
    result = await process_validation(request)
    return result
```

---

### Naming Conventions

| Type | Convention | Example |
|-------|-------------|----------|
| Variables | snake_case | `patient_id`, `billed_amount` |
| Functions | snake_case | `validate_bill()`, `calculate_score()` |
| Classes | PascalCase | `BillValidator`, `MLModelEngine` |
| Constants | UPPER_SNAKE_CASE | `FRAUD_THRESHOLD`, `MAX_RETRIES` |
| Modules | snake_case | `billing_rules.py`, `neo4j.py` |
| Packages | lowercase | `backend/app/api` |

---

### Docstrings

We use Google-style docstrings:

```python
def validate_bill(
    bill_id: str,
    context: dict,
) -> ValidationResult:
    """Validate a medical bill against all fraud detection rules.

    Args:
        bill_id: Unique identifier for the bill.
        context: Additional context for validation.

    Returns:
        ValidationResult object containing validation results.

    Raises:
        BillNotFoundError: If bill_id does not exist.
        DatabaseError: If database query fails.
    """
    # Implementation
    pass
```

---

### Error Handling

#### Use Custom Exceptions

```python
class FraudDetectionError(Exception):
    """Base exception for fraud detection errors."""
    pass


class RuleExecutionError(FraudDetectionError):
    """Raised when a rule fails to execute."""
    pass


class DatabaseConnectionError(FraudDetectionError):
    """Raised when database connection fails."""
    pass
```

#### Handle Errors Gracefully

```python
from fastapi import HTTPException
from app.exceptions import RuleExecutionError

@router.post("/validate")
async def validate_bill(request: BillValidationRequest):
    """Validate a bill with error handling."""
    try:
        result = await rules_engine.validate(request)
        return result
    except RuleExecutionError as e:
        logger.error(f"Rule execution failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Validation service unavailable"
        )
    except BillNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

### Async/Await Best Practices

```python
# Use async for all I/O operations
async def get_bill(bill_id: str) -> Bill:
    async with get_db() as session:
        result = await session.execute(
            select(Bill).where(Bill.claim_id == bill_id)
        )
        return result.scalar_one_or_none()

# Use asyncio.gather for parallel operations
async def validate_bill_parallel(bill_id: str):
    tasks = [
        run_rules(bill_id),
        run_ml_detection(bill_id),
        run_network_analysis(bill_id)
    ]
    results = await asyncio.gather(*tasks)
    return aggregate_results(results)
```

---

## Development Workflow

### Branching Strategy

```
master (main production branch)
  │
  ├── develop (integration branch)
  │     │
  │     ├── feature/your-feature
  │     ├── bugfix/your-fix
  │     └── hotfix/urgent-fix
```

### Git Workflow

#### Create Feature Branch

```bash
# Always start from master
git checkout master
git pull origin master

# Create feature branch
git checkout -b feature/add-new-rule
```

#### Commit Changes

```bash
# Stage changes
git add backend/app/rules/new_rule.py

# Commit with conventional commits
git commit -m "feat: add billing frequency limit rule"
```

**Commit Message Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(rules): add provider frequency limit validation

Add new rule to validate provider procedure frequency
within a 30-day window. Prevents excessive billing.

Closes #123
```

#### Push and Create PR

```bash
# Push branch
git push origin feature/add-new-rule

# Create Pull Request on GitHub
# Link to related issues
```

---

## Adding Features

### Adding a New Rule

1. Create rule class in `backend/app/rules/`:

```python
from app.rules.base import BaseRule, ValidationResult

class NewValidationRule(BaseRule):
    """New validation rule implementation."""

    def __init__(self, priority: int = 30):
        super().__init__(priority=priority)
        self.name = "New Validation Rule"

    async def validate(
        self,
        bill: Bill,
        context: dict
    ) -> ValidationResult:
        """Validate bill against this rule."""
        # Implementation
        if self._is_violated(bill):
            return ValidationResult(
                is_valid=False,
                score=0.8,
                message="Violation detected"
            )
        return ValidationResult(is_valid=True)

    def _is_violated(self, bill: Bill) -> bool:
        """Check if rule is violated."""
        # Logic
        return False
```

2. Register rule in rules engine:

```python
from app.rules.new_rule import NewValidationRule

# In rules_engine.py
self.rules = [
    ICD10ValidationRule(),
    CPTValidationRule(),
    NewValidationRule(priority=30),
    # ... other rules
]
```

3. Add tests:

```python
import pytest
from app.rules.new_rule import NewValidationRule

@pytest.mark.asyncio
async def test_new_rule_pass():
    """Test rule passes for valid bill."""
    rule = NewValidationRule()
    result = await rule.validate(valid_bill, {})
    assert result.is_valid is True

@pytest.mark.asyncio
async def test_new_rule_fail():
    """Test rule fails for invalid bill."""
    rule = NewValidationRule()
    result = await rule.validate(invalid_bill, {})
    assert result.is_valid is False
    assert result.message == "Violation detected"
```

### Adding a New API Endpoint

1. Create Pydantic schema:

```python
# backend/app/schemas/bill.py
from pydantic import BaseModel, Field

class BillValidationRequest(BaseModel):
    patient_id: str = Field(..., min_length=1)
    provider_npi: str = Field(..., regex=r'^\d{10}$')
    procedure_code: str = Field(..., min_length=5, max_length=5)
    billed_amount: float = Field(..., gt=0)

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "PATIENT-001",
                "provider_npi": "1234567890",
                "procedure_code": "99214",
                "billed_amount": 150.00
            }
        }
```

2. Create endpoint:

```python
# backend/app/api/bills.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.bill import BillValidationRequest
from app.core.rules_engine import RulesEngine

router = APIRouter()

@router.post("/validate", response_model=BillValidationResponse)
async def validate_bill(
    request: BillValidationRequest,
    rules_engine: RulesEngine = Depends(get_rules_engine)
) -> BillValidationResponse:
    """Validate a medical bill."""
    try:
        result = await rules_engine.validate(request)
        return result
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

3. Register router:

```python
# backend/app/main.py
from app.api.bills import router as bills_router

app.include_router(
    bills_router,
    prefix="/api/v1/bills",
    tags=["Bills"]
)
```

---

## Code Review

### Pull Request Guidelines

#### Before Submitting

- [ ] All tests pass locally
- [ ] Code formatted with Black
- [ ] No linting errors (Ruff)
- [ ] Type checking passes (MyPy)
- [ ] Documentation updated
- [ ] Tests added for new features
- [ ] Commit messages follow conventional format

#### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added
- [ ] All tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks**: CI runs tests, linting, type checking
2. **Code Review**: Peer review focusing on:
   - Code quality and style
   - Logic correctness
   - Performance implications
   - Security considerations
   - Test coverage
3. **Approval**: Requires at least one approval from maintainer
4. **Merge**: Squashed and merged to master

---

## Documentation

### Inline Documentation

```python
def calculate_fraud_score(
    rule_results: List[ValidationResult],
    weights: dict
) -> float:
    """Calculate composite fraud score from rule results.

    Weighted average of failed rule scores.

    Args:
        rule_results: List of validation results from all rules.
        weights: Dictionary mapping rule names to weights.

    Returns:
        Composite fraud score between 0.0 and 1.0.

    Example:
        >>> results = [ValidationResult(is_valid=False, score=0.8)]
        >>> calculate_fraud_score(results, {'rule1': 0.5})
        0.4
    """
    # Implementation
    pass
```

### README Updates

When adding significant features:
- Update feature list in README.md
- Add usage examples
- Update architecture diagrams
- Document configuration changes

---

## Best Practices

### Performance

```python
# Use connection pooling
async with get_db() as session:
    # Single connection for multiple queries
    bills = await session.execute(select(Bill))
    providers = await session.execute(select(Provider))

# Use batch operations
for batch in split_into_batches(items, 1000):
    await session.execute(insert(Table).values(batch))

# Use caching
@lru_cache(maxsize=1000)
def get_billing_code(code: str) -> BillingCode:
    # Cache frequently accessed data
    pass
```

### Security

```python
# Always validate input
def validate_npi(npi: str) -> bool:
    if not re.match(r'^\d{10}$', npi):
        raise ValueError("Invalid NPI format")
    return True

# Never log sensitive data
logger.info(f"Validating bill for patient {patient_id}")  # Good
logger.info(f"Validating bill: {bill}")  # Bad - contains PII

# Use parameterized queries
# Bad: SQL injection risk
query = f"SELECT * FROM bills WHERE claim_id = '{bill_id}'"

# Good: Safe parameterization
query = select(Bill).where(Bill.claim_id == bill_id)
```

---

## Resources

- **[PEP 8](https://peps.python.org/pep-0008/)** - Python style guide
- **[FastAPI Docs](https://fastapi.tiangolo.com/)** - FastAPI framework
- **[SQLAlchemy Docs](https://docs.sqlalchemy.org/)** - ORM documentation
- **[Pydantic Docs](https://docs.pydantic.dev/)** - Data validation
- **[Pytest Docs](https://docs.pytest.org/)** - Testing framework

---

## Next Steps

- **[Testing Guide](Testing-Guide.md)** - Write tests
- **[API Reference](API-Reference.md)** - Explore endpoints
- **[Troubleshooting](Troubleshooting.md)** - Common issues
