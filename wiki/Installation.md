# Installation Guide

**Tags**: #installation #setup #dependencies #python #postgresql #neo4j #redis #docker

This guide will help you set up Healthcare Auditor on your local machine for development or production use.

## Table of Contents

- [System Requirements](#system-requirements)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Docker Setup](#docker-setup)
- [Manual Setup](#manual-setup)
- [Database Setup](#database-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements

| Component | Minimum | Recommended |
|-----------|----------|-------------|
| OS | Linux/macOS/Windows | Linux (Ubuntu 22.04+) |
| CPU | 2 cores | 4+ cores |
| RAM | 8 GB | 16 GB |
| Storage | 20 GB | 50 GB SSD |

### Software Versions

| Software | Minimum Version | Recommended Version |
|----------|----------------|-------------------|
| Python | 3.11 | 3.11+ |
| PostgreSQL | 14 | 15+ |
| Neo4j | 5.0 | 5.20+ |
| Redis | 7.0 | 7.2+ |
| Docker | 20.10 | 24.0+ (optional) |

---

## Prerequisites

### 1. Python and pip

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11

# Verify installation
python3.11 --version
pip3.11 --version
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Verify installation
python3.11 --version
pip3.11 --version
```

#### Windows
```bash
# Download Python 3.11+ from https://www.python.org/downloads/
# During installation, check "Add Python to PATH"

# Verify installation
python --version
pip --version
```

### 2. Poetry (Python Dependency Manager)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH (add to your ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
poetry --version
```

### 3. PostgreSQL

#### macOS
```bash
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb healthcare_auditor
```

#### Ubuntu/Debian
```bash
sudo apt install -y postgresql-15 postgresql-contrib-15
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql -c "CREATE DATABASE healthcare_auditor;"
sudo -u postgres psql -c "CREATE USER auditor WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE healthcare_auditor TO auditor;"
```

#### Windows
Download and install from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)

#### Using Docker
```bash
docker run --name healthcare-postgres \
  -e POSTGRES_DB=healthcare_auditor \
  -e POSTGRES_USER=auditor \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -d postgres:15
```

### 4. Neo4j

#### macOS
```bash
# Install Neo4j Desktop
brew install --cask neo4j

# Or use Neo4j Community Edition
brew install neo4j
neo4j start

# Set initial password
# Visit http://localhost:7474 and follow setup wizard
```

#### Ubuntu/Debian
```bash
# Install Java 11+ (required for Neo4j)
sudo apt install -y openjdk-17-jre-headless

# Import Neo4j GPG key
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -

# Add Neo4j repository
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list

# Install Neo4j
sudo apt update
sudo apt install -y neo4j

# Start Neo4j
sudo systemctl start neo4j
sudo systemctl enable neo4j

# Set initial password at http://localhost:7474
```

#### Using Docker
```bash
docker run --name healthcare-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_neo4j_password \
  -e NEO4J_PLUGINS='["apoc"]' \
  -d neo4j:5.20
```

### 5. Redis

#### macOS
```bash
brew install redis
brew services start redis
```

#### Ubuntu/Debian
```bash
sudo apt install -y redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

#### Using Docker
```bash
docker run --name healthcare-redis \
  -p 6379:6379 \
  -d redis:7-alpine
```

---

## Installation Methods

### Option 1: Docker (Recommended for Quick Start)

Docker provides an isolated environment with all dependencies pre-configured.

```bash
# Clone repository
git clone https://github.com/calebrosario/healthcare-auditor.git
cd healthcare-auditor

# Create .env file from template
cp .env.example .env

# Edit .env with your database credentials
# See Configuration Guide for details

# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Manual Installation (Recommended for Development)

For development and detailed customization, manual installation provides more control.

---

## Manual Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/calebrosario/healthcare-auditor.git
cd healthcare-auditor
```

### Step 2: Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment using Python 3.11
python3.11 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
which python
```

### Step 3: Install Dependencies

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 4: Configure Environment

```bash
# Go to project root
cd ..

# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

### Essential Environment Variables

```env
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://auditor:your_password@localhost:5432/healthcare_auditor
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

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Fraud Detection
FRAUD_SCORE_THRESHOLD=0.65
ALERT_PRIORITY_HIGH=0.95
ALERT_PRIORITY_MEDIUM=0.80

# ML Model Settings
ML_MODEL_PATH=/tmp/ml_models
MODEL_VERSION=1.0
RETRAIN_INTERVAL_DAYS=7
HIGH_RISK_THRESHOLD=0.7
MEDIUM_RISK_THRESHOLD=0.4

# External APIs
NCCI_API_ENABLED=False
FEE_SCHEDULE_ENABLED=False
```

[See full configuration guide →](Configuration.md)

---

## Database Setup

### PostgreSQL Initialization

```bash
# Run database migrations
cd backend

# Using Alembic
alembic upgrade head

# Or create tables directly
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Neo4j Initialization

```bash
# Start Neo4j (if not already running)
neo4j start  # macOS/Linux
# or via service:
sudo systemctl start neo4j  # Linux

# Verify connection
curl http://localhost:7474

# Initialize graph schema
python scripts/build_graph.py --init-schema
```

The graph initialization will:
- Create unique constraints (NPI, payer_id, claim_id, etc.)
- Create performance indexes (name, type, state, etc.)
- Create full-text search indexes

---

## Verification

### 1. Check Database Connections

```bash
# Test PostgreSQL
psql -U auditor -d healthcare_auditor -c "SELECT version();"

# Test Neo4j
curl http://localhost:7474/db/neo4j/tx/commit \
  -u neo4j:your_password \
  -H "Content-Type: application/json" \
  -d '{"statements":[{"statement":"RETURN 1 as result"}]}'

# Test Redis
redis-cli ping
# Should return: PONG
```

### 2. Run Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_rules_engine.py -v

# Run with coverage
pytest tests/ --cov=backend/app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
# or open in browser
```

### 3. Start API Server

```bash
cd backend

# Start development server with auto-reload
uvicorn app.main:app --reload --port 8000

# The API will be available at:
# - http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - ReDoc docs: http://localhost:8000/redoc
```

### 4. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Validate a bill
curl -X POST http://localhost:8000/api/v1/bills/validate \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PATIENT-001",
    "provider_npi": "1234567890",
    "insurer_id": 1,
    "procedure_code": "99214",
    "diagnosis_code": "I10",
    "billed_amount": 150.00,
    "bill_date": "2026-02-05T10:00:00Z"
  }'
```

---

## Troubleshooting

### Common Issues

#### Issue: PostgreSQL connection refused
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS

# Check connection
psql -U auditor -d healthcare_auditor
```

#### Issue: Neo4j connection failed
```bash
# Check Neo4j status
sudo systemctl status neo4j  # Linux
neo4j status  # macOS

# Check logs
tail -f /var/log/neo4j/neo4j.log  # Linux
tail -f ~/Library/Application\ Support/Neo4j/neo4j.log  # macOS

# Restart Neo4j
sudo systemctl restart neo4j  # Linux
neo4j restart  # macOS
```

#### Issue: Python import errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
```

#### Issue: Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

#### Issue: Redis connection failed
```bash
# Check Redis status
redis-cli ping

# Start Redis
sudo systemctl start redis  # Linux
brew services start redis  # macOS

# Check Redis logs
tail -f /var/log/redis/redis.log
```

### Getting Help

If you encounter issues not covered here:

1. Check the [Troubleshooting Guide](Troubleshooting.md) for detailed solutions
2. Search [GitHub Issues](https://github.com/calebrosario/healthcare-auditor/issues)
3. Open a new issue with:
   - System information (OS, Python version, etc.)
   - Error messages
   - Steps to reproduce
   - Expected vs actual behavior

---

## Next Steps

- **[Architecture Guide](Architecture.md)** - Understand the system design
- **[API Reference](API-Reference.md)** - Explore available endpoints
- **[Development Guide](Development-Guide.md)** - Start contributing
- **[Testing Guide](Testing-Guide.md)** - Write and run tests

---

## Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Poetry Documentation](https://python-poetry.org/docs/)
