# API Reference

**Tags**: #api #rest #fastapi #endpoints #authentication #documentation

Complete documentation for all Healthcare Auditor API endpoints.

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Codes](#error-codes)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Bills API](#bills-api)
  - [Providers API](#providers-api)
  - [Insurers API](#insurers-api)
  - [Knowledge Graph API](#knowledge-graph-api)
  - [Regulations API](#regulations-api)
  - [Alerts API](#alerts-api)

---

## Base URL

```
Development: http://localhost:8000
Staging: https://staging-api.healthcare-auditor.com
Production: https://api.healthcare-auditor.com
```

All endpoints are prefixed with `/api/v1`

---

## Authentication

### JWT Token Authentication

Most endpoints require a valid JWT token in the `Authorization` header:

```http
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

**Endpoint**: `POST /api/v1/auth/token`

**Request**:
```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## Response Format

### Standard Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2026-02-08T13:02:30Z"
}
```

### Paginated Response

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid provider NPI format",
    "details": {
      "field": "provider_npi",
      "value": "123",
      "constraint": "Must be 10 digits"
    }
  }
}
```

---

## Endpoints

### Health Check

#### Get System Health

Check if API and all dependencies are healthy.

```http
GET /api/v1/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-08T13:02:30Z",
  "dependencies": {
    "postgresql": "healthy",
    "neo4j": "healthy",
    "redis": "healthy"
  },
  "uptime": 1234567
}
```

---

### Bills API

#### Validate a Bill

Validate a medical bill against all fraud detection rules and ML models.

```http
POST /api/v1/bills/validate
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body**:
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

**Fields**:

| Field | Type | Required | Description |
|-------|-------|----------|-------------|
| patient_id | string | Yes | Unique patient identifier |
| provider_npi | string | Yes | 10-digit NPI number |
| insurer_id | integer | Yes | Insurer ID |
| procedure_code | string | Yes | CPT/HCPCS code (5 chars) |
| diagnosis_code | string | Yes | ICD-10 code |
| billed_amount | decimal | Yes | Amount billed (USD) |
| bill_date | datetime | Yes | ISO 8601 timestamp |

**Response** (200 OK):
```json
{
  "claim_id": "CLAIM-001",
  "fraud_score": 0.15,
  "fraud_risk_level": "low",
  "compliance_score": 0.85,
  "issues": [
    "Near-duplicate bill found",
    "Documentation is brief"
  ],
  "warnings": [
    "Provider frequency approaching limit"
  ],
  "code_legality_score": 0.9,
  "ml_fraud_probability": 0.25,
  "network_risk_score": 0.3,
  "anomaly_flags": ["z_score_outlier"],
  "code_violations": [],
  "phase4_stats": {
    "anomaly_score": 0.7,
    "ml_predictions": {
      "random_forest": 0.2,
      "isolation_forest": 0.3
    },
    "network_metrics": {
      "pagerank": 0.05,
      "community_size": 12,
      "wcc": 1
    }
  },
  "rule_results": {
    "coding_rules": {
      "passed": 3,
      "failed": 0,
      "skipped": 0
    },
    "medical_necessity": {
      "passed": 1,
      "failed": 1,
      "skipped": 0
    },
    "frequency_rules": {
      "passed": 2,
      "failed": 0,
      "skipped": 0
    },
    "billing_rules": {
      "passed": 1,
      "failed": 1,
      "skipped": 0
    }
  }
}
```

**Score Interpretation**:

| Score | Risk Level | Action |
|--------|------------|--------|
| ≥0.70 | High | Immediate investigation |
| 0.40-0.69 | Medium | Priority review |
| <0.40 | Low | Normal processing |

---

#### Get Bill Details

Retrieve detailed information about a specific bill.

```http
GET /api/v1/bills/{claim_id}
Authorization: Bearer <token>
```

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|-------|----------|-------------|
| claim_id | string | Yes | Unique claim identifier |

**Response** (200 OK):
```json
{
  "claim_id": "CLAIM-001",
  "patient_id": "PATIENT-001",
  "provider": {
    "npi": "1234567890",
    "name": "Dr. John Smith",
    "specialty": "Internal Medicine"
  },
  "insurer": {
    "id": 1,
    "name": "Blue Cross"
  },
  "procedure_code": "99214",
  "procedure_description": "Established Office Visit",
  "diagnosis_code": "I10",
  "diagnosis_description": "Essential (primary) hypertension",
  "billed_amount": 150.00,
  "allowed_amount": 120.00,
  "bill_date": "2026-02-05T10:00:00Z",
  "fraud_score": 0.15,
  "compliance_score": 0.85,
  "status": "review_required",
  "created_at": "2026-02-05T10:05:00Z",
  "updated_at": "2026-02-05T10:10:00Z"
}
```

---

#### List Bills

Retrieve a paginated list of bills with filtering.

```http
GET /api/v1/bills?page=1&page_size=20&provider_npi=1234567890&fraud_score_min=0.7
Authorization: Bearer <token>
```

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|-------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| page_size | integer | No | 20 | Items per page (max 100) |
| provider_npi | string | No | - | Filter by provider NPI |
| insurer_id | integer | No | - | Filter by insurer |
| patient_id | string | No | - | Filter by patient |
| fraud_score_min | decimal | No | - | Min fraud score |
| fraud_score_max | decimal | No | - | Max fraud score |
| date_from | date | No | - | Filter bills from date |
| date_to | date | No | - | Filter bills to date |
| status | string | No | - | Filter by status |
| sort_by | string | No | bill_date | Sort field |
| sort_order | string | No | desc | Sort direction (asc/desc) |

**Response** (200 OK):
```json
{
  "bills": [
    {
      "claim_id": "CLAIM-001",
      "patient_id": "PATIENT-001",
      "provider_npi": "1234567890",
      "insurer_id": 1,
      "billed_amount": 150.00,
      "fraud_score": 0.75,
      "status": "investigation_required",
      "bill_date": "2026-02-05T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

#### Batch Validate Bills

Validate multiple bills in a single request.

```http
POST /api/v1/bills/validate/batch
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "bills": [
    {
      "patient_id": "PATIENT-001",
      "provider_npi": "1234567890",
      "insurer_id": 1,
      "procedure_code": "99214",
      "diagnosis_code": "I10",
      "billed_amount": 150.00,
      "bill_date": "2026-02-05T10:00:00Z"
    },
    {
      "patient_id": "PATIENT-002",
      "provider_npi": "1234567890",
      "insurer_id": 1,
      "procedure_code": "99213",
      "diagnosis_code": "J45",
      "billed_amount": 100.00,
      "bill_date": "2026-02-05T11:00:00Z"
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "results": [
    {
      "claim_id": "CLAIM-001",
      "fraud_score": 0.15,
      "fraud_risk_level": "low",
      "compliance_score": 0.85,
      "status": "passed"
    },
    {
      "claim_id": "CLAIM-002",
      "fraud_score": 0.85,
      "fraud_risk_level": "high",
      "compliance_score": 0.45,
      "status": "investigation_required"
    }
  ],
  "summary": {
    "total": 2,
    "high_risk": 1,
    "medium_risk": 0,
    "low_risk": 1,
    "processing_time_ms": 250
  }
}
```

---

### Providers API

#### Get Provider Details

Retrieve detailed provider information.

```http
GET /api/v1/providers/{npi}
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "npi": "1234567890",
  "name": "Dr. John Smith",
  "provider_type": "Individual",
  "specialty": "Internal Medicine",
  "state": "CA",
  "city": "San Francisco",
  "license": "123456",
  "hospitals": [
    {
      "npi": "0987654321",
      "name": "City General Hospital",
      "type": "General",
      "relationship": "PROVIDES_AT"
    }
  ],
  "insurers": [
    {
      "payer_id": 1,
      "name": "Blue Cross",
      "coverage_type": "PPO"
    }
  ],
  "statistics": {
    "total_claims": 150,
    "avg_fraud_score": 0.25,
    "high_risk_claims": 5,
    "compliance_rate": 0.85
  },
  "network_metrics": {
    "pagerank": 0.05,
    "community_id": 12,
    "connections": 8
  }
}
```

---

#### List Providers

Retrieve paginated list of providers.

```http
GET /api/v1/providers?page=1&page_size=20&specialty=Cardiology&state=CA
Authorization: Bearer <token>
```

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|-------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| page_size | integer | No | 20 | Items per page |
| name | string | No | - | Search by name |
| specialty | string | No | - | Filter by specialty |
| state | string | No | - | Filter by state (2-char) |
| city | string | No | - | Filter by city |
| provider_type | string | No | - | Filter by type |

---

### Insurers API

#### Get Insurer Details

```http
GET /api/v1/insurers/{insurer_id}
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "payer_id": "00001",
  "name": "Blue Cross",
  "coverage_type": "PPO",
  "state": "CA",
  "providers_count": 1500,
  "total_claims": 50000,
  "statistics": {
    "avg_fraud_score": 0.18,
    "high_risk_rate": 0.05,
    "compliance_rate": 0.92
  }
}
```

---

#### List Insurers

```http
GET /api/v1/insurers?page=1&page_size=20&coverage_type=PPO
Authorization: Bearer <token>
```

---

### Knowledge Graph API

#### Query Provider Network

Execute Cypher queries on the knowledge graph.

```http
POST /api/v1/knowledge-graph/query
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "cypher": "MATCH (p:Provider {npi: $npi})-[:PROVIDES_AT]->(h:Hospital) RETURN p.name, h.name",
  "parameters": {
    "npi": "1234567890"
  }
}
```

**Response** (200 OK):
```json
{
  "results": [
    {
      "p.name": "Dr. John Smith",
      "h.name": "City General Hospital"
    }
  ],
  "stats": {
    "nodes_visited": 15,
    "relationships_created": 0,
    "execution_time_ms": 45
  }
}
```

---

#### Get Provider Network Visualization

Get network data for visualization.

```http
GET /api/v1/knowledge-graph/providers/{npi}/network
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "nodes": [
    {
      "id": "1234567890",
      "label": "Dr. John Smith",
      "type": "Provider",
      "properties": {
        "specialty": "Internal Medicine",
        "state": "CA"
      }
    }
  ],
  "edges": [
    {
      "source": "1234567890",
      "target": "0987654321",
      "label": "PROVIDES_AT",
      "weight": 1
    }
  ]
}
```

---

### Regulations API

#### List Regulations

```http
GET /api/v1/regulations?page=1&page_size=20&category=Coding&type=Bundling
Authorization: Bearer <token>
```

**Query Parameters**:

| Parameter | Type | Description |
|-----------|-------|-------------|
| category | string | Filter by category (Coding, Billing, Medical Necessity) |
| type | string | Filter by type |
| is_active | boolean | Filter active/inactive regulations |

---

#### Get Regulation Details

```http
GET /api/v1/regulations/{code}
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "code": "NCCI-123",
  "name": "CPT Bundling Rule",
  "category": "Coding",
  "type": "Bundling",
  "description": "Bundling of CPT codes 99213 and 99214",
  "severity": "High",
  "penalty_description": "Code unbundling detected",
  "requirements": [
    "Both codes must be billed together",
    "Modifier usage restrictions apply"
  ],
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2026-01-15T00:00:00Z"
}
```

---

### Alerts API

#### Get Alerts

```http
GET /api/v1/alerts?page=1&page_size=20&severity=high&status=open
Authorization: Bearer <token>
```

**Query Parameters**:

| Parameter | Type | Description |
|-----------|-------|-------------|
| severity | string | Filter by severity (high, medium, low) |
| status | string | Filter by status (open, investigating, resolved) |
| bill_id | string | Filter by bill |
| created_from | date | Filter alerts from date |

---

#### Update Alert Status

```http
PATCH /api/v1/alerts/{alert_id}/status
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "status": "investigating",
  "notes": "Assigned to investigator John Doe",
  "assigned_to": "johndoe"
}
```

---

## Rate Limiting

API requests are rate-limited to prevent abuse:

| Tier | Requests | Time Window |
|-------|-----------|-------------|
| Free | 100 | 1 hour |
| Standard | 1,000 | 1 hour |
| Premium | 10,000 | 1 hour |

Rate limit headers are included in every response:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1707384150
```

---

## Webhooks

Configure webhooks to receive real-time notifications.

### Create Webhook

```http
POST /api/v1/webhooks
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "url": "https://your-domain.com/webhooks",
  "events": ["bill.validated", "alert.created"],
  "secret": "your-webhook-secret"
}
```

### Webhook Payload

```json
{
  "event": "bill.validated",
  "timestamp": "2026-02-08T13:02:30Z",
  "data": {
    "claim_id": "CLAIM-001",
    "fraud_score": 0.85,
    "fraud_risk_level": "high"
  }
}
```

---

## Interactive Documentation

- **Swagger UI**: https://api.healthcare-auditor.com/docs
- **ReDoc**: https://api.healthcare-auditor.com/redoc

---

## SDKs and Libraries

### Python SDK

```python
from healthcare_auditor import Client

client = Client(api_key="your-api-key")

# Validate a bill
result = client.bills.validate({
    "patient_id": "PATIENT-001",
    "provider_npi": "1234567890",
    "insurer_id": 1,
    "procedure_code": "99214",
    "diagnosis_code": "I10",
    "billed_amount": 150.00
})

print(result.fraud_score)  # 0.15
```

### JavaScript SDK

```javascript
const { Client } = require('@healthcare-auditor/sdk');

const client = new Client({ apiKey: 'your-api-key' });

const result = await client.bills.validate({
  patientId: 'PATIENT-001',
  providerNpi: '1234567890',
  insurerId: 1,
  procedureCode: '99214',
  diagnosisCode: 'I10',
  billedAmount: 150.00
});

console.log(result.fraudScore);  // 0.15
```

---

## Support

- **API Documentation**: This wiki and `/docs` endpoint
- **GitHub Issues**: https://github.com/calebrosario/healthcare-auditor/issues
- **Email Support**: api-support@healthcare-auditor.com
