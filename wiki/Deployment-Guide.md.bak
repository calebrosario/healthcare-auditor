# Deployment Guide

This guide covers deploying Healthcare Auditor to production environments, including infrastructure setup, configuration, and best practices.

## Table of Contents

- [Overview](#overview)
- [Deployment Options](#deployment-options)
- [Infrastructure Setup](#infrastructure-setup)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Monitoring & Logging](#monitoring--logging)
- [Security Hardening](#security-hardening)
- [Backup & Recovery](#backup--recovery)

---

## Overview

Healthcare Auditor can be deployed in several ways:

1. **Docker Compose** - Simplest for small deployments
2. **Kubernetes** - Scalable for production
3. **Cloud Services** - AWS, GCP, Azure managed services

### Deployment Requirements

- **Minimum**: 2 vCPU, 4GB RAM
- **Recommended**: 4+ vCPU, 16GB RAM
- **High Availability**: Multiple instances with load balancer

---

## Infrastructure Setup

### Server Requirements

| Component | Minimum | Recommended | Production |
|-----------|----------|-------------|-------------|
| CPU | 2 cores | 4 cores | 8+ cores |
| RAM | 4 GB | 8 GB | 16+ GB |
| Storage | 50 GB SSD | 100 GB SSD | 200 GB SSD |
| Network | 100 Mbps | 1 Gbps | 10 Gbps |

### Required Services

- **PostgreSQL 14+** - Primary database
- **Neo4j 5.x** - Knowledge graph
- **Redis 7+** - Caching and queue
- **Load Balancer** - Nginx or cloud LB
- **SSL/TLS** - HTTPS termination

---

## Docker Deployment

### Docker Compose (Simple)

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://auditor:${DB_PASSWORD}@postgres:5432/healthcare_auditor
      - NEO4J_URI=bolt://neo4j:${NEO4J_PASSWORD}@neo4j:7687
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - neo4j
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=healthcare_auditor
      - POSTGRES_USER=auditor
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  neo4j:
    image: neo4j:5.20
    environment:
      - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j_data:/data
    ports:
      - "7474:7474"
      - "7687:7687"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  neo4j_data:
  redis_data:
```

### Deployment Steps

```bash
# Clone repository
git clone https://github.com/calebrosario/healthcare-auditor.git
cd healthcare-auditor

# Create .env with production values
cp .env.example .env
nano .env

# Update environment variables
# - Set strong passwords
# - Set production database URLs
# - Set CORS origins
# - Configure fraud detection thresholds

# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head
```

---

## Kubernetes Deployment

### Namespace and ConfigMaps

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: healthcare-auditor
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: healthcare-auditor
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  DATABASE_POOL_SIZE: "20"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: healthcare-auditor
type: Opaque
data:
  db-password: <base64-encoded-password>
  neo4j-password: <base64-encoded-password>
  secret-key: <base64-encoded-secret>
```

### PostgreSQL Deployment

```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: healthcare-auditor
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: "healthcare_auditor"
        - name: POSTGRES_USER
          value: "auditor"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: db-password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 100Gi
```

### API Deployment

```yaml
# k8s/api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: healthcare-auditor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: healthcare-auditor:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: db-url
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 2000m
            memory: 2Gi
---
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: healthcare-auditor
spec:
  selector:
    app: api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  namespace: healthcare-auditor
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.healthcare-auditor.com
    secretName: api-tls
  rules:
  - host: api.healthcare-auditor.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply namespace and config
kubectl apply -f k8s/namespace.yaml

# Create secrets (from environment variables)
kubectl create secret generic app-secrets \
  --from-literal=db-password=$DB_PASSWORD \
  --from-literal=neo4j-password=$NEO4J_PASSWORD \
  --from-literal=secret-key=$SECRET_KEY

# Deploy databases
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/neo4j.yaml
kubectl apply -f k8s/redis.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n healthcare-auditor --timeout=300s

# Deploy API
kubectl apply -f k8s/api.yaml

# Deploy ingress
kubectl apply -f k8s/ingress.yaml

# Check deployment status
kubectl get pods -n healthcare-auditor
kubectl get services -n healthcare-auditor
kubectl get ingress -n healthcare-auditor

# Run migrations
kubectl exec -it deployment/api -n healthcare-auditor -- alembic upgrade head
```

---

## Cloud Deployment

### AWS ECS/Fargate

**Task Definition**:

```json
{
  "family": "healthcare-auditor-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "healthcare-auditor",
      "image": "your-registry/healthcare-auditor:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql+asyncpg://..."
        },
        {
          "name": "NEO4J_URI",
          "value": "bolt://..."
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:SecretKey-xxxx"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/healthcare-auditor",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "api"
        }
      }
    }
  ]
}
```

### GCP Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy healthcare-auditor-api \
  --image gcr.io/your-project/healthcare-auditor:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql+asyncpg://... \
  --set-secrets SECRET_KEY=SECRET_KEY:latest
```

### Azure Container Instances

```bash
# Deploy to Azure Container Instances
az container create \
  --resource-group healthcare-auditor-rg \
  --name healthcare-auditor-api \
  --image your-registry/healthcare-auditor:latest \
  --dns-name-label healthcare-auditor \
  --ports 8000 \
  --environment-variables DATABASE_URL=postgresql+asyncpg://... \
  --secrets SECRET_KEY@/subscriptions/.../keyVaults/.../secrets/SECRET_KEY
```

---

## Monitoring & Logging

### Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'healthcare-auditor'
    static_configs:
      - targets: ['api:9090']
```

### Grafana Dashboard

Import dashboard for:

- Request rate and latency
- Error rate by endpoint
- Database query performance
- Cache hit ratio
- CPU and memory usage
- Fraud detection metrics

### Log Aggregation

```yaml
# filebeat.yml
filebeat.inputs:
  - type: container
    paths:
      - '/var/log/containers/*.log'
    processors:
      - add_kubernetes_metadata:
      - add_cloud_metadata:

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

---

## Security Hardening

### SSL/TLS Configuration

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name api.healthcare-auditor.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name api.healthcare-auditor.com;
    return 301 https://$server_name$request_uri;
}
```

### Firewall Rules

```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw deny 5432/tcp   # PostgreSQL (internal only)
ufw deny 7687/tcp   # Neo4j (internal only)
ufw deny 6379/tcp   # Redis (internal only)
ufw enable
```

### Security Headers

```python
# backend/app/middleware.py
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.healthcare-auditor.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.healthcare-auditor.com", "*.healthcare-auditor.com"]
)

app.add_middleware(HTTPSRedirectMiddleware)
```

---

## Backup & Recovery

### PostgreSQL Backup

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"

mkdir -p $BACKUP_DIR
pg_dump -U auditor -h localhost -d healthcare_auditor | gzip > $BACKUP_DIR/healthcare_auditor_$DATE.sql.gz

# Keep last 7 days
find $BACKUP_DIR -name "healthcare_auditor_*.sql.gz" -mtime +7 -delete
```

### Neo4j Backup

```bash
# Backup Neo4j database
neo4j-admin dump \
  --database=neo4j \
  --to=/backups/neo4j/backup_$(date +%Y%m%d)

# Incremental backup
neo4j-admin incremental-backup \
  --from=/backups/neo4j/full_backup \
  --to=/backups/neo4j/incremental_$(date +%Y%m%d)
```

### Disaster Recovery

```bash
# Restore PostgreSQL
gunzip < /backups/postgres/healthcare_auditor_20260208.sql.gz | \
  psql -U auditor -h localhost -d healthcare_auditor

# Restore Neo4j
neo4j-admin load \
  --from=/backups/neo4j/backup_20260208 \
  --database=neo4j \
  --force
```

---

## Next Steps

- **[Installation Guide](Installation.md)** - Initial setup
- **[Configuration Guide](Configuration.md)** - Environment variables
- **[Monitoring](#monitoring--logging)** - Set up observability
