# Healthcare Auditor - Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the Healthcare Auditor system to production.

## Components

- **Namespace**: `namespace.yaml` - Dedicated namespace for Healthcare Auditor
- **Secrets**: `secrets.yaml` - Sensitive credentials (passwords, API keys)
- **ConfigMaps**: `configmaps.yaml` - Non-sensitive configuration
- **PostgreSQL**: `postgres-deployment.yaml` - Structured data store
- **Neo4j**: `neo4j-deployment.yaml` - Knowledge graph database
- **Backend**: `backend-deployment.yaml` - FastAPI application with HPA
- **Ingress**: `ingress.yaml` - External access routing

## Prerequisites

1. **Kubernetes Cluster**: v1.20+ with LoadBalancer support
2. **Storage Class**: `standard` storage class for persistent volumes
3. **Ingress Controller**: nginx ingress controller with TLS support
4. **Cert Manager**: For automatic SSL certificate provisioning (optional)

## Quick Start

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (IMPORTANT: Base64 encode your values!)
kubectl create secret generic postgres-secret \
  --from-literal=postgres-password=$(echo -n 'your-password' | base64) \
  --from-literal=postgres-user=$(echo -n 'healthcare_user' | base64) \
  -n healthcare-auditor

kubectl create secret generic neo4j-secret \
  --from-literal=neo4j-password=$(echo -n 'your-neo4j-password' | base64) \
  --from-literal=neo4j-user=$(echo -n 'neo4j' | base64) \
  -n healthcare-auditor

kubectl create secret generic backend-secret \
  --from-literal=secret-key=$(echo -n 'production-secret-key' | base64) \
  --from-literal=database-url=$(echo -n 'postgresql+asyncpg://healthcare_user:your-password@postgres:5432/healthcare_auditor' | base64) \
  --from-literal=neo4j-uri=$(echo -n 'bolt://neo4j:your-neo4j-password@neo4j:7687' | base64) \
  --from-literal=redis-url=$(echo -n 'redis://redis:6379/0' | base64) \
  -n healthcare-auditor

# Deploy configmaps
kubectl apply -f k8s/configmaps.yaml

# Deploy applications
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/neo4j-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml

# Deploy ingress (optional, for external access)
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get all -n healthcare-auditor
```

## Resource Requirements

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|---------------|------------|-----------------|---------------|
| PostgreSQL | 250m | 500m | 512Mi | 1Gi |
| Neo4j | 500m | 1000m | 1Gi | 2Gi |
| Backend | 200m | 500m | 256Mi | 512Mi |
| **Total** | **950m** | **2000m** | **1.75Gi** | **3.5Gi** |

## Storage Requirements

- PostgreSQL: 10Gi persistent volume
- Neo4j: 10Gi persistent volume

## Scaling

Backend is configured with HorizontalPodAutoscaler (HPA):
- **Min Replicas**: 2 pods
- **Max Replicas**: 10 pods
- **Scale Up**: When CPU > 70% or memory > 80%
- **Scale Down**: Stabilized over 5 minutes, scale down 50%
- **Scale Up**: Stabilized over 1 minute, scale up to target

## Access

- **Internal Services**:
  - PostgreSQL: `postgres.healthcare-auditor.svc.cluster.local:5432`
  - Neo4j: `neo4j.healthcare-auditor.svc.cluster.local:7474`
  - Backend API: `backend.healthcare-auditor.svc.cluster.local:8000`

- **External Access** (with Ingress):
  - API: `https://api.healthcare-auditor.example.com`
  - Health Check: `https://api.healthcare-auditor.example.com/health`

## Monitoring

Pods have configured health and readiness probes:

- **Liveness**: Detects unresponsive pods and restarts them
- **Readiness**: Ensures pods receive traffic only when ready
- **Probe Intervals**: Every 10 seconds for liveness, 5 seconds for readiness

## Security

1. **Secrets**: All sensitive data stored in Kubernetes secrets, not configmaps
2. **Network Policies**: Consider adding network policies to restrict pod-to-pod communication
3. **RBAC**: Consider adding role-based access control for tighter security

## Rolling Updates

All deployments use RollingUpdate strategy:
- **Max Surge**: 1 extra pod during update
- **Max Unavailable**: 1 pod max unavailable during update
- Ensures zero-downtime deployments

## Troubleshooting

```bash
# Check pod status
kubectl get pods -n healthcare-auditor

# View pod logs
kubectl logs -f deployment/backend -n healthcare-auditor

# Describe pod for issues
kubectl describe pod <pod-name> -n healthcare-auditor

# Scale backend manually
kubectl scale deployment backend --replicas=5 -n healthcare-auditor

# Check HPA status
kubectl get hpa backend-hpa -n healthcare-auditor
```
