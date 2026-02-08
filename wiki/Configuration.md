# Configuration Guide

**Tags**: #configuration #environment #settings #database #security #logging

Complete guide to configuring Healthcare Auditor for development, staging, and production environments.

## Table of Contents

- [Overview](#overview)
- [Configuration File](#configuration-file)
- [Environment Variables](#environment-variables)
- [Database Configuration](#database-configuration)
- [ML Configuration](#ml-configuration)
- [API Configuration](#api-configuration)
- [Security Configuration](#security-configuration)
- [Logging Configuration](#logging-configuration)
- [Environment-Specific Settings](#environment-specific-settings)

---

## Overview

Healthcare Auditor uses environment variables for configuration. All sensitive information should be stored in environment variables and never committed to version control.

### Configuration Priority

Configuration is loaded in this order:

1. Environment variables (highest priority)
2. `.env` file
3. Default values in code (lowest priority)

---

## Configuration File

### Creating .env File

```bash
# Copy the example file
cp .env.example .env

# Edit with your settings
nano .env
```

### .env File Structure

```env
# Application
APP_NAME=Healthcare Auditor
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1
WORKERS=4

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://auditor:password@localhost:5432/healthcare_auditor
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_ECHO=false

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600
REDIS_MAX_CONNECTIONS=100

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]

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
NCCI_API_ENABLED=false
NCCI_API_KEY=
NCCI_API_URL=https://api.ncci.org/v1

FEE_SCHEDULE_ENABLED=false
FEE_SCHEDULE_API_KEY=
FEE_SCHEDULE_API_URL=https://api.feeschedule.org/v1

LCD_NCD_API_ENABLED=false
LCD_NCD_API_KEY=
LCD_NCD_API_URL=https://api.cms.gov/v1

# Task Queue (Celery)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_TIMEZONE=UTC

# Monitoring
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
PROMETHEUS_ENABLED=false
PROMETHEUS_PORT=9090
```

---

## Environment Variables

### Application Settings

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `APP_NAME` | string | "Healthcare Auditor" | Application name |
| `ENVIRONMENT` | string | "development" | Environment (development/staging/production) |
| `DEBUG` | boolean | false | Enable debug mode |
| `LOG_LEVEL` | string | "INFO" | Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL) |

---

### Database Configuration

#### PostgreSQL

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `DATABASE_URL` | string | Required | PostgreSQL connection URL |
| `DATABASE_POOL_SIZE` | integer | 10 | Connection pool size |
| `DATABASE_MAX_OVERFLOW` | integer | 20 | Max overflow connections |
| `DATABASE_ECHO` | boolean | false | Log SQL queries |

**Connection URL Format**:
```
postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]
```

**Example**:
```
postgresql+asyncpg://auditor:secure_password@localhost:5432/healthcare_auditor
```

#### PostgreSQL Pool Sizing

```
Total connections = pool_size + max_overflow
Recommended: pool_size = (2 * CPU cores) + 1
For 4 cores: pool_size = 10, max_overflow = 20
```

---

#### Neo4j

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `NEO4J_URI` | string | "bolt://localhost:7687" | Neo4j Bolt protocol URL |
| `NEO4J_USER` | string | "neo4j" | Neo4j username |
| `NEO4J_PASSWORD` | string | Required | Neo4j password |
| `NEO4J_DATABASE` | string | "neo4j" | Neo4j database name |

**Connection URL Format**:
```
bolt://[user]:[password]@[host]:[port]
```

**Example**:
```
bolt://neo4j:secure_password@localhost:7687
```

#### Neo4j Memory Settings

For datasets of different sizes:

| Dataset Size | Heap Size | Page Cache |
|--------------|-----------|-------------|
| < 1M nodes | 2G | 1G |
| 1M-10M nodes | 4G | 4G |
| 10M-100M nodes | 8G | 16G |
| > 100M nodes | 16G | 32G |

Set in Neo4j configuration:
```conf
dbms.memory.heap.initial_size=4G
dbms.memory.heap.max_size=4G
dbms.memory.pagecache.size=4G
```

---

#### Redis

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `REDIS_URL` | string | "redis://localhost:6379/0" | Redis connection URL |
| `REDIS_CACHE_TTL` | integer | 3600 | Cache time-to-live (seconds) |
| `REDIS_MAX_CONNECTIONS` | integer | 100 | Max connection pool size |

**Connection URL Format**:
```
redis://[host]:[port]/[db]
```

**Example**:
```
redis://localhost:6379/0
```

---

### API Configuration

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `API_HOST` | string | "0.0.0.0" | API host address |
| `API_PORT` | integer | 8000 | API port |
| `API_PREFIX` | string | "/api/v1" | API path prefix |
| `WORKERS` | integer | 4 | Number of uvicorn workers |

**Worker Count Calculation**:
```
workers = (2 * CPU cores) + 1
For 4 cores: workers = 9
```

---

### Security Configuration

#### JWT Authentication

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `SECRET_KEY` | string | Required | JWT signing secret |
| `ALGORITHM` | string | "HS256" | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | integer | 30 | Access token lifetime (minutes) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | integer | 7 | Refresh token lifetime (days) |

**Secret Key Generation**:
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -hex 32
```

**Security Best Practices**:
- Use minimum 32-character secret keys
- Rotate secret keys regularly
- Store in secure vault (AWS Secrets Manager, HashiCorp Vault)
- Never commit to version control

---

#### CORS Configuration

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `CORS_ORIGINS` | list | ["http://localhost:3000"] | Allowed origins |
| `CORS_ALLOW_CREDENTIALS` | boolean | true | Allow credentials |
| `CORS_ALLOW_METHODS` | list | ["*"] | Allowed HTTP methods |
| `CORS_ALLOW_HEADERS` | list | ["*"] | Allowed headers |

**Example**:
```env
CORS_ORIGINS=["https://app.healthcare-auditor.com","https://admin.healthcare-auditor.com"]
```

---

### Fraud Detection Configuration

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `FRAUD_SCORE_THRESHOLD` | decimal | 0.65 | Fraud detection threshold |
| `ALERT_PRIORITY_HIGH` | decimal | 0.95 | High priority alert threshold |
| `ALERT_PRIORITY_MEDIUM` | decimal | 0.80 | Medium priority alert threshold |

**Threshold Tuning**:

| Environment | Threshold | Precision | Recall |
|-------------|-----------|-----------|--------|
| Development | 0.65 | 80% | 95% |
| Staging | 0.70 | 85% | 90% |
| Production | 0.75 | 90% | 85% |

Adjust based on your use case:
- **Higher threshold**: Fewer false positives, more false negatives
- **Lower threshold**: More false positives, fewer false negatives

---

### ML Configuration

#### Model Storage

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `ML_MODEL_PATH` | string | "/tmp/ml_models" | ML models directory |
| `MODEL_VERSION` | string | "1.0" | Current model version |
| `RETRAIN_INTERVAL_DAYS` | integer | 7 | Retraining interval (days) |

#### Risk Thresholds

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `HIGH_RISK_THRESHOLD` | decimal | 0.7 | High risk threshold |
| `MEDIUM_RISK_THRESHOLD` | decimal | 0.4 | Medium risk threshold |

**Risk Level Classification**:
```
Score >= HIGH_RISK_THRESHOLD:      HIGH
MEDIUM_RISK_THRESHOLD <= Score < HIGH: MEDIUM
Score < MEDIUM_RISK_THRESHOLD:      LOW
```

#### Model Retraining

**Automatic Retraining**:
```python
# Triggered when:
# 1. RETRAIN_INTERVAL_DAYS elapsed
# 2. New labeled data available
# 3. Model drift detected

# Retraining flow:
# 1. Load historical data from PostgreSQL
# 2. Feature engineering
# 3. Train models (RF + Isolation Forest)
# 4. Evaluate on validation set
# 5. Save to ML_MODEL_PATH
# 6. Update MODEL_VERSION
# 7. Reload in production
```

---

### External API Configuration

#### NCCI (National Correct Coding Initiative)

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `NCCI_API_ENABLED` | boolean | false | Enable NCCI API |
| `NCCI_API_KEY` | string | Required | NCCI API key |
| `NCCI_API_URL` | string | "https://api.ncci.org/v1" | NCCI API endpoint |

#### Fee Schedule

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `FEE_SCHEDULE_ENABLED` | boolean | false | Enable fee schedule API |
| `FEE_SCHEDULE_API_KEY` | string | Required | API key |
| `FEE_SCHEDULE_API_URL` | string | "https://api.feeschedule.org/v1" | API endpoint |

#### LCD/NCD (Local/National Coverage Determinations)

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `LCD_NCD_API_ENABLED` | boolean | false | Enable LCD/NCD API |
| `LCD_NCD_API_KEY` | string | Required | CMS API key |
| `LCD_NCD_API_URL` | string | "https://api.cms.gov/v1" | CMS API endpoint |

**API Keys Security**:
- Store in environment variables
- Use API key management service
- Rotate keys regularly
- Monitor API usage and quotas
- Implement rate limiting and retries

---

### Task Queue Configuration (Celery)

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `CELERY_BROKER_URL` | string | Required | Redis broker URL |
| `CELERY_RESULT_BACKEND` | string | Required | Redis result backend |
| `CELERY_TASK_SERIALIZER` | string | "json" | Task serialization format |
| `CELERY_RESULT_SERIALIZER` | string | "json" | Result serialization format |
| `CELERY_TIMEZONE` | string | "UTC" | Task timezone |

**Broker URL Format**:
```
redis://[host]:[port]/[db]
```

**Example**:
```
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

---

### Monitoring Configuration

#### Sentry (Error Tracking)

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `SENTRY_DSN` | string | Required | Sentry DSN |
| `SENTRY_ENVIRONMENT` | string | "development" | Environment name |

**Example**:
```env
SENTRY_DSN=https://xxxx@sentry.io/xxxxx
SENTRY_ENVIRONMENT=production
```

#### Prometheus (Metrics)

| Variable | Type | Default | Description |
|-----------|-------|---------|-------------|
| `PROMETHEUS_ENABLED` | boolean | false | Enable Prometheus metrics |
| `PROMETHEUS_PORT` | integer | 9090 | Metrics port |

**Access Metrics**:
```
http://localhost:9090/metrics
```

---

## Logging Configuration

### Log Levels

| Level | Description |
|-------|-------------|
| DEBUG | Detailed diagnostic information |
| INFO | General informational messages |
| WARNING | Warning messages for potentially harmful situations |
| ERROR | Error events that might still allow application to continue |
| CRITICAL | Very severe error events |

### Log Configuration

```python
# In backend/app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Structured Logging (JSON)

```env
LOG_FORMAT=json
LOG_DATE_FORMAT=%Y-%m-%dT%H:%M:%S%z
```

**Output**:
```json
{
  "timestamp": "2026-02-08T13:02:30Z",
  "level": "INFO",
  "logger": "app.main",
  "message": "Bill validated successfully",
  "context": {
    "claim_id": "CLAIM-001",
    "fraud_score": 0.15
  }
}
```

---

## Environment-Specific Settings

### Development

```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Use local databases
DATABASE_URL=postgresql+asyncpg://auditor:dev_password@localhost:5432/healthcare_auditor_dev
NEO4J_URI=bolt://localhost:7687
REDIS_URL=redis://localhost:6379/0

# Disable external APIs
NCCI_API_ENABLED=false
FEE_SCHEDULE_ENABLED=false
```

### Staging

```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Use staging databases
DATABASE_URL=postgresql+asyncpg://auditor:staging_password@staging-db.example.com:5432/healthcare_auditor_staging
NEO4J_URI=bolt://staging-neo4j.example.com:7687
REDIS_URL=redis://staging-redis.example.com:6379/0

# Enable monitoring
SENTRY_DSN=https://xxxx@sentry.io/xxxxx
SENTRY_ENVIRONMENT=staging
PROMETHEUS_ENABLED=true
```

### Production

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Use production databases with connection pooling
DATABASE_URL=postgresql+asyncpg://auditor:prod_password@prod-db.example.com:5432/healthcare_auditor
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

NEO4J_URI=bolt://prod-neo4j.example.com:7687
REDIS_URL=redis://prod-redis.example.com:6379/0

# Strong security
SECRET_KEY=production-secret-key-change-regularly
ACCESS_TOKEN_EXPIRE_MINUTES=15
CORS_ORIGINS=["https://app.healthcare-auditor.com"]

# Enable all features
NCCI_API_ENABLED=true
FEE_SCHEDULE_ENABLED=true
LCD_NCD_API_ENABLED=true

# Production monitoring
SENTRY_DSN=https://xxxx@sentry.io/xxxxx
SENTRY_ENVIRONMENT=production
PROMETHEUS_ENABLED=true
```

---

## Best Practices

### Security

1. **Never commit `.env` files** to version control
2. **Use strong secrets** - minimum 32 characters
3. **Rotate secrets regularly** - every 90 days
4. **Use vaults** - AWS Secrets Manager, HashiCorp Vault
5. **Limit permissions** - Principle of least privilege
6. **Enable encryption** - TLS for all connections
7. **Audit access** - Log all configuration changes

### Performance

1. **Connection pooling** - Optimize pool sizes based on load
2. **Caching** - Use Redis for frequently accessed data
3. **Async I/O** - Leverage async for high throughput
4. **Batch operations** - Process in batches (1000 records)
5. **Indexes** - Create indexes on frequently queried fields
6. **Query optimization** - Use `EXPLAIN ANALYZE` for slow queries

### Monitoring

1. **Log important events** - Validations, errors, configuration changes
2. **Track metrics** - Request latency, throughput, error rates
3. **Set up alerts** - For critical thresholds
4. **Monitor resources** - CPU, memory, disk, network
5. **Review logs regularly** - Look for anomalies and patterns

---

## Configuration Validation

Validate your configuration before starting:

```bash
# Run configuration validation
python scripts/validate_config.py

# Check database connections
python scripts/check_databases.py

# Verify API settings
python scripts/verify_api_config.py
```

---

## Next Steps

- **[Installation Guide](Installation.md)** - Setup your environment
- **[Development Guide](Development-Guide.md)** - Start developing
- **[Deployment Guide](Deployment-Guide.md)** - Deploy to production
