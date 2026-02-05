# Healthcare Auditor

A comprehensive healthcare billing fraud detection and compliance verification system.

## Overview

Healthcare Auditor is a production-ready system for detecting fraudulent medical claims and ensuring billing compliance. It combines rule-based validation, knowledge graph analysis, and (in Phase 4) machine learning to identify suspicious billing patterns.

## Architecture

### Technology Stack

- **Language**: Python 3.11+
- **Backend**: FastAPI with async PostgreSQL
- **Knowledge Graph**: Neo4j for entity relationships
- **Caching**: Redis 7
- **Task Queue**: Celery for async processing
- **Testing**: Pytest with pytest-asyncio

### Database Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                │
│                      │                              │
│         ┌────────────┴────────────┐           │
│         │   PostgreSQL (Primary)     │           │
│         │   Bills, Providers, etc.     │           │
│         └───────────────────────────────┘           │
│                      │                              │
│         ┌────────────┴────────────┐            │
│         │   Neo4j (Graph)          │            │
│         │   Provider Networks              │            │
│         │   Regulation Relationships    │            │
│         └─────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
healthcare-auditor/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI endpoints
│   │   ├── core/             # Core components (rules_engine.py, neo4j.py)
│   │   ├── models/           # SQLAlchemy models
│   │   ├── rules/            # Rule validators (NEW - Phase 3)
│   │   ├── security/          # Authentication and authorization
│   │   └── config.py         # Configuration management
│   └── main.py              # FastAPI application
├── scripts/                   # Standalone scripts
│   ├── validate_bills.py      # Rules engine executor (NEW - Phase 3)
│   └── ingestion/            # Data ingestion scripts
├── tests/                     # Test suite
│   └── test_rules_engine.py   # Rules engine tests (NEW - Phase 3)
├── docs/
│   ├── KNOWLEDGE_GRAPH_STATE_MACHINE.md
│   └── RULES_ENGINE_STATE_MACHINE.md  # NEW - Phase 3
├── .research/                  # Research and session handoffs
└── .env.example              # Environment configuration template
```

## Features

### Knowledge Graph (Phase 2 - Complete)
- ✅ Neo4j integration for provider networks
- ✅ Batch node and edge creation
- ✅ 7 relationship types
- ✅ UNWIND pattern for 900x performance improvement
- ✅ MERGE operations for idempotency

### Rules Engine (Phase 3 - Complete)
- ✅ 9 rule implementations across 4 categories
- ✅ Rule chain with prioritization and early termination
- ✅ Composite fraud and compliance scoring
- ✅ Neo4j context enrichment
- ✅ Batch evaluation support
- ✅ Comprehensive error handling and logging
- ✅ 25+ unit tests

#### Rule Types

**Coding Rules** (`backend/app/rules/coding_rules.py`):
- ICD-10 format validation
- CPT code existence and status
- CPT-ICD pair validation

**Medical Necessity Rules** (`backend/app/rules/medical_necessity_rules.py`):
- Documentation completeness check
- Medical necessity score validation

**Frequency Rules** (`backend/app/rules/frequency_rules.py`):
- Provider procedure frequency limits
- Patient procedure frequency limits

**Billing Rules** (`backend/app/rules/billing_rules.py`):
- Billing amount limit checks
- Exact and near-duplicate detection

## API Endpoints

### Bills API

#### `POST /api/v1/bills/validate`
Validate a single medical bill against all rules.

**Request**:
```json
{
  "patient_id": "PATIENT-001",
  "provider_npi": "1234567890",
  "insurer_id": 1,
  "procedure_code": "99214",
  "diagnosis_code": "I10",
  "billed_amount": 150.00,
  "bill_date": "2026-02-05T10:00:00Z"
}
```

**Response**:
```json
{
  "claim_id": "CLAIM-001",
  "fraud_score": 0.15,
  "fraud_risk_level": "low",
  "compliance_score": 0.85,
  "issues": ["Near-duplicate bill found"],
  "warnings": ["Documentation is brief"]
}
```

### Standalone Script

```bash
# Validate single bill
python scripts/validate_bills.py --claim-id CLAIM-001

# Batch validate bills
python scripts/validate_bills.py --batch --input claims.json
```

## Configuration

Environment variables (see `.env.example`):

```env
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/healthcare_auditor
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# Fraud Detection
FRAUD_SCORE_THRESHOLD=0.65
ALERT_PRIORITY_HIGH=0.95
ALERT_PRIORITY_MEDIUM=0.80
```

## Installation

```bash
# Clone repository
git clone <repository-url>
cd healthcare-auditor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize databases
# PostgreSQL: Create database and run migrations
# Neo4j: Start Neo4j service

# Run tests
pytest tests/ -v
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_rules_engine.py -v

# Run specific test
pytest tests/test_rules_engine.py::TestICD10ValidationRule::test_valid_icd10_code -v

# With coverage
pytest tests/ --cov=backend/app --cov-report=html
```

### Running API

```bash
# Start development server
uvicorn backend.app.main:app --reload --port 8000

# API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Using Knowledge Graph Builder

```bash
# Build knowledge graph from PostgreSQL data
python scripts/build_graph.py
```

## Phase Progress

- ✅ **Phase 1**: Foundation & Setup
- ✅ **Phase 2**: Knowledge Graph Construction (Complete)
- ✅ **Phase 3**: Rules Engine (Complete)
- 🔄 **Phase 4**: Fraud Detection & ML (Next)

## Documentation

- [Knowledge Graph State Machine](docs/KNOWLEDGE_GRAPH_STATE_MACHINE.md)
- [Rules Engine State Machine](docs/RULES_ENGINE_STATE_MACHINE.md)
- [Session Handoffs](.research/SESSION_HANDOFF.md)

## License

[Specify your license here]

## Contributing

[Specify contribution guidelines here]
