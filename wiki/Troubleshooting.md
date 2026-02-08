# Troubleshooting

Common issues and solutions for Healthcare Auditor setup and operation.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Database Issues](#database-issues)
- [API Issues](#api-issues)
- [Performance Issues](#performance-issues)
- [ML Issues](#ml-issues)
- [Deployment Issues](#deployment-issues)
- [Getting Help](#getting-help)

---

## Installation Issues

### Issue: Python Version Error

**Error**: `SyntaxError: invalid syntax` or module import errors

**Cause**: Python version < 3.11

**Solution**:
```bash
# Check Python version
python --version

# Install Python 3.11+
# macOS:
brew install python@3.11

# Ubuntu:
sudo apt install python3.11

# Windows: Download from python.org

# Create virtual environment with correct Python
python3.11 -m venv venv
source venv/bin/activate
```

---

### Issue: Poetry Installation Fails

**Error**: `poetry: command not found`

**Cause**: Poetry not installed or not in PATH

**Solution**:
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify
poetry --version

# If still not found, add to shell profile
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

### Issue: Dependencies Fail to Install

**Error**: `ERROR: Could not find a version that satisfies the requirement`

**Cause**: System dependencies missing or outdated pip

**Solution**:
```bash
# Update pip
pip install --upgrade pip

# Install system dependencies (Ubuntu/Debian)
sudo apt install -y build-essential python3-dev libpq-dev

# Install system dependencies (macOS)
brew install postgresql libpq

# Reinstall dependencies
poetry install --no-root
```

---

## Database Issues

### Issue: PostgreSQL Connection Refused

**Error**: `psycopg2.OperationalError: could not connect to server`

**Cause**: PostgreSQL not running or wrong credentials

**Solution**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS

# Check connection
psql -U auditor -d healthcare_auditor

# Verify .env configuration
# DATABASE_URL=postgresql+asyncpg://auditor:password@localhost:5432/healthcare_auditor
```

---

### Issue: Database Migration Fails

**Error**: `alembic.util.exc.CommandError: Target database is not up to date`

**Cause**: Database schema out of sync with migrations

**Solution**:
```bash
# Check migration status
alembic current

# View migration history
alembic history

# Reset database (development only!)
# WARNING: Deletes all data
alembic downgrade base
alembic upgrade head

# Or create new migration
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

### Issue: Neo4j Connection Failed

**Error**: `neo4j.exceptions.ServiceUnavailable: Unable to connect`

**Cause**: Neo4j not running or wrong credentials

**Solution**:
```bash
# Check Neo4j status
sudo systemctl status neo4j  # Linux
neo4j status  # macOS

# Start Neo4j
sudo systemctl start neo4j  # Linux
neo4j start  # macOS

# Check logs
tail -f /var/log/neo4j/neo4j.log  # Linux
tail -f ~/Library/Application\ Support/Neo4j/neo4j.log  # macOS

# Test connection
curl http://localhost:7474
# Visit http://localhost:7474 in browser

# Verify .env configuration
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=your_password
```

---

### Issue: Redis Connection Refused

**Error**: `redis.exceptions.ConnectionError: Error connecting to Redis`

**Cause**: Redis not running or wrong port

**Solution**:
```bash
# Check Redis status
sudo systemctl status redis  # Linux
brew services list | grep redis  # macOS

# Start Redis
sudo systemctl start redis  # Linux
brew services start redis  # macOS

# Test connection
redis-cli ping
# Should return: PONG

# Check Redis logs
tail -f /var/log/redis/redis.log
```

---

## API Issues

### Issue: Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Cause**: Another process using port 8000

**Solution**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

---

### Issue: CORS Errors

**Error**: Browser shows CORS policy error

**Cause**: Frontend origin not in CORS allow list

**Solution**:
```env
# In .env
CORS_ORIGINS=["https://your-frontend.com"]
```

```python
# In backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Issue: JWT Authentication Failed

**Error**: `401 Unauthorized: Could not validate credentials`

**Cause**: Invalid or expired token

**Solution**:
```bash
# Check token expiration
# Access tokens expire after ACCESS_TOKEN_EXPIRE_MINUTES (default: 30)

# Generate new token
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_username&password=your_password"

# Verify SECRET_KEY in .env
# Must be same across all instances
```

---

## Performance Issues

### Issue: Slow API Response Times

**Symptoms**: API requests take >1 second

**Cause**: Missing indexes, large datasets, or unoptimized queries

**Solution**:
```bash
# Check PostgreSQL query performance
EXPLAIN ANALYZE SELECT * FROM bills WHERE claim_id = 'xxx';

# Create indexes
CREATE INDEX idx_bills_claim_id ON bills(claim_id);
CREATE INDEX idx_bills_provider_id ON bills(provider_id);
CREATE INDEX idx_bills_bill_date ON bills(bill_date);

# Check connection pool size
# DATABASE_POOL_SIZE=20 (recommended for production)
# DATABASE_MAX_OVERFLOW=40

# Enable caching
# REDIS_CACHE_TTL=3600 (1 hour)
```

---

### Issue: High Memory Usage

**Symptoms**: Process using >8GB RAM

**Cause**: Memory leaks or inefficient queries

**Solution**:
```python
# Optimize database queries
# Use select() with limit
await session.execute(
    select(Bill).limit(100)
)

# Use async properly
# Don't block event loop with sync operations

# Profile memory usage
import memory_profiler

@profile
async def validate_bill(bill_id):
    # Implementation
    pass
```

---

### Issue: Neo4j Slow Queries

**Symptoms**: Graph queries taking >200ms

**Cause**: Missing indexes or inefficient Cypher queries

**Solution**:
```cypher
# Create indexes
CREATE INDEX provider_name_idx FOR (p:Provider) ON (p.name);
CREATE INDEX provider_specialty_idx FOR (p:Provider) ON (p.specialty);

# Use PROFILE to analyze queries
PROFILE MATCH (p:Provider)-[:PROVIDES_AT]->(h:Hospital)
RETURN p, h;

# Use batch operations
UNWIND $providers AS provider
MERGE (p:Provider {npi: provider.npi})
ON CREATE SET p.name = provider.name
```

---

## ML Issues

### Issue: Model Training Fails

**Error**: `ValueError: Input contains NaN`

**Cause**: Missing or invalid training data

**Solution**:
```python
# Clean data before training
import pandas as pd
import numpy as np

# Remove NaN values
df = df.dropna()

# Replace infinite values
df = df.replace([np.inf, -np.inf], np.nan)
df = df.dropna()

# Ensure numeric types
df['billed_amount'] = pd.to_numeric(df['billed_amount'], errors='coerce')

# Validate data shape
print(f"Training data shape: {df.shape}")
print(f"Feature columns: {df.columns.tolist()}")
```

---

### Issue: Model Prediction Very Slow

**Symptoms**: ML prediction takes >100ms per bill

**Cause**: Model not loaded in memory or inefficient feature extraction

**Solution**:
```python
# Load model once (not per request)
class MLModelEngine:
    def __init__(self):
        self.model = joblib.load('ml_models/random_forest.pkl')

    async def predict(self, features):
        # Fast inference
        return self.model.predict([features])

# Cache feature extraction
@lru_cache(maxsize=1000)
def extract_features(bill_id):
    # Cache expensive feature extraction
    pass
```

---

### Issue: Outdated ML Models

**Symptoms**: Prediction accuracy declining over time

**Cause**: Model drift from changing fraud patterns

**Solution**:
```bash
# Retrain models regularly
python scripts/train_models.py --labeled-data-path /data/recent_labels.csv

# Update MODEL_VERSION in .env
MODEL_VERSION=2.0

# Schedule retraining (cron)
# Daily/weekly depending on data volume
0 2 * * * python /app/scripts/train_models.py
```

---

## Deployment Issues

### Issue: Docker Container Crashes Immediately

**Error**: Container exits with code 1

**Cause**: Missing environment variables or configuration errors

**Solution**:
```bash
# Check container logs
docker-compose logs api

# Run container in interactive mode
docker-compose run api /bin/bash

# Verify .env is mounted correctly
env | grep DATABASE_URL

# Check Python syntax
python -m py_compile backend/app/main.py
```

---

### Issue: Kubernetes Pod Not Starting

**Symptoms**: Pod stuck in `CrashLoopBackOff`

**Cause**: Resource limits too low or health check failing

**Solution**:
```bash
# Describe pod for details
kubectl describe pod api-xxx -n healthcare-auditor

# Check pod logs
kubectl logs api-xxx -n healthcare-auditor

# Increase resource limits
resources:
  requests:
    cpu: 1000m      # Increase
    memory: 1Gi      # Increase
  limits:
    cpu: 4000m
    memory: 4Gi

# Check health probe configuration
livenessProbe:
  httpGet:
    path: /api/v1/health
    port: 8000
  initialDelaySeconds: 30  # Increase if slow startup
```

---

### Issue: SSL Certificate Errors

**Error**: `SSL: CERTIFICATE_VERIFY_FAILED`

**Cause**: Invalid or expired SSL certificate

**Solution**:
```bash
# Check certificate expiration
openssl x509 -enddate -noout -in /etc/ssl/cert.pem

# Renew certificate with Let's Encrypt
certbot renew --nginx

# Verify certificate chain
openssl s_client -connect api.healthcare-auditor.com:443 -servername api.healthcare-auditor.com
```

---

## Getting Help

### Before Asking for Help

1. **Check logs** - Look for error messages
2. **Search issues** - Check [GitHub Issues](https://github.com/calebrosario/healthcare-auditor/issues)
3. **Read documentation** - Review related wiki pages
4. **Minimal reproduction** - Create minimal example showing the issue

### Issue Template

When reporting issues, include:

```markdown
## Environment
- OS: [e.g., Ubuntu 22.04, macOS 13, Windows 11]
- Python version: [e.g., 3.11.5]
- Healthcare Auditor version: [e.g., 1.0.0]

## Description
[Clear description of what you're trying to do]

## Expected Behavior
[What you expect to happen]

## Actual Behavior
[What actually happens]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [And so on...]

## Error Messages
```
[Paste error messages here]
```

## Log Files
[Paste relevant log excerpts]

## Configuration
[Relevant .env variables, excluding secrets]
```

---

### Support Channels

- **GitHub Issues**: https://github.com/calebrosario/healthcare-auditor/issues
- **GitHub Discussions**: https://github.com/calebrosario/healthcare-auditor/discussions
- **Email**: support@healthcare-auditor.com
- **Documentation**: This wiki

---

## Resources

- **[Installation Guide](Installation.md)** - Setup instructions
- **[Configuration Guide](Configuration.md)** - Environment variables
- **[Deployment Guide](Deployment-Guide.md)** - Production setup
