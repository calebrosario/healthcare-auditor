# Healthcare Auditor CI/CD Development Plan

## Overview

This document provides a comprehensive guide for setting up CI/CD development for the Healthcare Auditor project, including GitHub Actions workflows, LocalStack for local AWS development, and deployment strategies.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [LocalStack Configuration](#localstack-configuration)
4. [GitHub Actions Workflows](#github-actions-workflows)
5. [Deployment Strategy](#deployment-strategy)
6. [Testing Strategy](#testing-strategy)
7. [Monitoring and Observability](#monitoring-and-observability)
8. [Troubleshooting](#troubleshooting)
9. [Resources and Documentation](#resources-and-documentation)

---

## Prerequisites

### Required Tools

- **Docker & Docker Compose**: For container orchestration
- **Git**: For version control
- **act**: For local GitHub Actions testing
- **AWS CLI**: For AWS resource management (optional, for production)
- **kubectl**: For Kubernetes management

### Installation

```bash
# Install Docker
# macOS: https://docs.docker.com/desktop/install/mac-install/
# Linux: https://docs.docker.com/engine/install/
# Windows: https://docs.docker.com/desktop/install/windows-install/

# Install act (for local GitHub Actions testing)
brew install act  # macOS
# or download from https://github.com/nektos/act/releases

# Install AWS CLI (for production)
brew install awscli  # macOS
pip install awscli  # Python
# or from https://aws.amazon.com/cli/

# Install kubectl
brew install kubectl  # macOS
# or from https://kubernetes.io/docs/tasks/tools/
```

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/calebrosario/healthcare-auditor.git
cd healthcare-auditor
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your local settings
# DATABASE_URL, NEO4J_URI, REDIS_URL, etc.
```

### 3. Start Services

```bash
# Start all services with LocalStack
docker-compose -f docker-compose.localstack.yml up -d

# Check service status
docker-compose -f docker-compose.localstack.yml ps

# View logs
docker-compose -f docker-compose.localstack.yml logs -f
```

### 4. Access Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (neo4j/healthcare)
- **LocalStack**: http://localhost:4566

---

## LocalStack Configuration

### What is LocalStack?

LocalStack provides a fully functional local AWS cloud stack for development and testing. It mimics AWS services locally, allowing you to test cloud integrations without incurring AWS costs.

### Services Enabled

The following AWS services are configured in `docker-compose.localstack.yml`:

- **S3**: Object storage for file uploads and static assets
- **DynamoDB**: NoSQL database for logs and event storage
- **Lambda**: Serverless function execution
- **API Gateway**: REST API management
- **SQS**: Message queuing for async processing
- **SNS**: Pub/sub messaging for notifications
- **IAM**: Identity and Access Management
- **CloudWatch**: Monitoring and logging
- **Events (EventBridge)**: Event-driven architecture
- **Secrets Manager**: Secure secret storage
- **Step Functions**: Workflow orchestration

### LocalStack CLI Commands

```bash
# List all LocalStack services
curl http://localhost:4566/_localstack/health

# Create S3 bucket
aws --endpoint-url=http://localhost:4566 s3 mb s3://healthcare-auditor-uploads

# List S3 buckets
aws --endpoint-url=http://localhost:4566 s3 ls

# Create DynamoDB table
aws --endpoint-url=http://localhost:4566 dynamodb create-table \
  --table-name healthcare-auditor-logs \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# List DynamoDB tables
aws --endpoint-url=http://localhost:4566 dynamodb list-tables

# Upload file to S3
aws --endpoint-url=http://localhost:4566 s3 cp localfile.txt s3://healthcare-auditor-uploads/

# List S3 objects
aws --endpoint-url=http://localhost:4566 s3 ls s3://healthcare-auditor-uploads/
```

### Testing AWS Integrations Locally

```python
# Example: Upload to S3 using LocalStack
import boto3

s3_client = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',
    aws_secret_access_key='test',
    region_name='us-east-1'
)

s3_client.upload_file('localfile.txt', 'healthcare-auditor-uploads', 'remotefile.txt')
```

### LocalStack Web UI

LocalStack provides a web UI for visualizing resources:
- Access at: http://localhost:4566/_localstack/dashboard
- Requires LocalStack Pro (optional)

---

## GitHub Actions Workflows

### Workflow Architecture

The Healthcare Auditor uses two GitHub Actions workflows:

1. **`.github/workflows/ci-cd.yml`**: Backend CI/CD (existing)
2. **`.github/workflows/frontend-ci-cd.yml`**: Frontend CI/CD (new)

### Local Testing with act

**act** allows you to run GitHub Actions workflows locally, mimicking the GitHub Actions environment.

#### Installation

```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Windows (via Chocolatey)
choco install act-cli
```

#### Usage

```bash
# List all workflows
act -l

# Run all workflows for push event
act push

# Run specific workflow
act -W .github/workflows/frontend-ci-cd.yml push

# Run specific job
act -j frontend-lint-and-test

# Run with verbose output
act -v push

# Run with specific environment variables
act push -e .github/workflows/.env.local

# Run in dry-run mode (no actual execution)
act -n push
```

#### Environment File for act

Create `.github/workflows/.env.local`:

```env
# LocalStack configuration for CI
AWS_ENDPOINT_URL=http://host.docker.internal:4566
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=us-east-1
S3_BUCKET_NAME=healthcare-auditor-uploads
DYNAMODB_TABLE=healthcare-auditor-logs
```

#### Running act with LocalStack

```bash
# Start LocalStack first
docker-compose -f docker-compose.localstack.yml up -d localstack

# Run workflow with LocalStack
act push -e .github/workflows/.env.local

# Stop LocalStack when done
docker-compose -f docker-compose.localstack.yml down
```

### Workflow Triggers

#### Frontend CI/CD Workflow

```yaml
on:
  push:
    branches: [master, main, develop]
    paths:
      - 'frontend/**'
  pull_request:
    branches: [master, main]
    paths:
      - 'frontend/**'
```

**Trigger Conditions:**
- Push to master/main/develop with frontend changes
- Pull request to master/main with frontend changes

#### Backend CI/CD Workflow

```yaml
on:
  push:
    branches: [master, main, develop]
    paths:
      - 'backend/**'
      - 'k8s/**'
  pull_request:
    branches: [master, main]
    paths:
      - 'backend/**'
      - 'k8s/**'
```

**Trigger Conditions:**
- Push to master/main/develop with backend or k8s changes
- Pull request to master/main with backend or k8s changes

### Job Flow

#### Frontend CI/CD Workflow

```
┌─────────────────────┐
│ frontend-lint-and- │
│      test          │
│  (always runs)     │
└─────────┬───────────┘
          │
          ├──────────────────────────────┐
          │                              │
          ▼                              ▼
┌─────────────────┐         ┌─────────────────────┐
│ frontend-build  │         │ frontend-security-  │
│  (needs lint)   │         │      scan           │
└─────────┬───────┘         │   (push only)       │
          │                 └─────────────────────┘
          │
          ▼
┌─────────────────┐
│ frontend-e2e    │
│  (push only)    │
└─────────┬───────┘
          │
          ▼
┌─────────────────────┐
│ frontend-build-and- │
│        push         │
│   (push only)       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────────────┐
│ deploy-frontend-to-kubernetes│
│ (push to master/main only)  │
└─────────────────────────────┘
```

#### Backend CI/CD Workflow

```
┌─────────────────┐
│ build-and-test  │
│  (always runs)  │
└─────────┬───────┘
          │
          ├──────────────────────────────┐
          │                              │
          ▼                              ▼
┌─────────────────┐         ┌─────────────────────┐
│ build-and-push  │         │  security-scan      │
│  (push only)    │         │   (push only)       │
└─────────┬───────┘         └─────────────────────┘
          │
          ▼
┌─────────────────────────────┐
│ deploy-to-kubernetes       │
│ (push to master/main only)  │
└─────────────────────────────┘
```

### Secrets Management

Configure the following GitHub Secrets:

#### Required Secrets

| Secret Name | Description | Example |
|------------|-------------|---------|
| `KUBE_CONFIG` | Base64-encoded Kubernetes config | `cat ~/.kube/config \| base64` |
| `GITHUB_TOKEN` | GitHub PAT (auto-provided) | Automatic |

#### AWS Secrets (for production)

| Secret Name | Description |
|------------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS access key for production |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for production |
| `S3_BUCKET_NAME` | Production S3 bucket name |
| `DYNAMODB_TABLE` | Production DynamoDB table name |

#### Setting Secrets via CLI

```bash
# Using GitHub CLI
gh secret set KUBE_CONFIG --body "$(cat ~/.kube/config | base64)"

# Or via GitHub web interface
# Repository → Settings → Secrets and variables → Actions
```

---

## Deployment Strategy

### Environments

The project uses three deployment environments:

1. **Development**: Feature branch deployments
2. **Staging**: Pull request previews / develop branch
3. **Production**: master/main branch

### Deployment Flow

```
┌──────────────┐
│ Feature Branch│
│  (PR created) │
└───────┬───────┘
        │
        ▼
┌──────────────┐
│   Staging    │
│ (develop)    │
└───────┬───────┘
        │
        ▼
┌──────────────┐
│  Production  │
│ (master/main)│
└──────────────┘
```

### Kubernetes Deployment

#### Frontend Deployment Manifest

Create `k8s/frontend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: healthcare-auditor
  labels:
    app: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: ghcr.io/calebrosario/healthcare-auditor-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://backend.healthcare-auditor.svc.cluster.local:8000"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: healthcare-auditor
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 3000
```

#### Backend Deployment Manifest

Create `k8s/backend-deployment.yaml` (already exists):

```yaml
# Existing manifest in k8s/backend-deployment.yaml
```

### Rollback Strategy

```bash
# View deployment history
kubectl rollout history deployment/frontend -n healthcare-auditor

# Rollback to previous revision
kubectl rollout undo deployment/frontend -n healthcare-auditor

# Rollback to specific revision
kubectl rollout undo deployment/frontend -n healthcare-auditor --to-revision=2

# View rollout status
kubectl rollout status deployment/frontend -n healthcare-auditor
```

---

## Testing Strategy

### Test Pyramid

```
        ┌─────────┐
        │   E2E   │  Playwright (99 tests)
        │  Tests  │
        └─────────┘
       ┌───────────────┐
       │  Integration  │  API tests
       │    Tests      │
       └───────────────┘
      ┌─────────────────┐
      │   Unit Tests    │  Jest (backend + frontend)
      └─────────────────┘
```

### Running Tests

#### Local Development

```bash
# Frontend unit tests
cd frontend
npm run test:ci

# Frontend linting
npm run lint

# Frontend type checking
npm run type-check

# Frontend E2E tests
npm run e2e

# Backend tests
cd backend
pytest tests/ -v

# Backend with coverage
pytest tests/ --cov=app --cov-report=html
```

#### CI Testing

Tests run automatically on push/PR:
- Frontend: `.github/workflows/frontend-ci-cd.yml`
- Backend: `.github/workflows/ci-cd.yml`

### Test Coverage Goals

| Layer | Target Coverage | Current |
|-------|---------------|---------|
| Frontend Unit | 80% | TBD |
| Backend Unit | 80% | 67% (ML models) |
| E2E | Critical paths | 99 tests |
| Integration | API endpoints | TBD |

---

## Monitoring and Observability

### LocalStack Monitoring

```bash
# View LocalStack logs
docker-compose -f docker-compose.localstack.yml logs localstack -f

# Check service health
curl http://localhost:4566/_localstack/health

# LocalStack logs directory
docker-compose -f docker-compose.localstack.yml exec localstack ls -la /tmp/localstack/logs/
```

### Kubernetes Monitoring

```bash
# View pod logs
kubectl logs -f deployment/frontend -n healthcare-auditor
kubectl logs -f deployment/backend -n healthcare-auditor

# View pod status
kubectl get pods -n healthcare-auditor

# Describe pod for details
kubectl describe pod <pod-name> -n healthcare-auditor

# View events
kubectl get events -n healthcare-auditor --sort-by='.lastTimestamp'
```

### Application Monitoring

Consider integrating:
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **Loki**: Log aggregation
- **Jaeger**: Distributed tracing

---

## Troubleshooting

### Common Issues

#### 1. act fails to run workflows

**Problem**: `act push` fails with errors

**Solutions**:
```bash
# Check Docker is running
docker ps

# Update act to latest version
brew upgrade act  # macOS

# Use verbose mode for debugging
act -v push

# Check workflow syntax
act -n push  # dry-run mode
```

#### 2. LocalStack services unreachable

**Problem**: Cannot access AWS services via localhost:4566

**Solutions**:
```bash
# Check LocalStack is running
docker-compose -f docker-compose.localstack.yml ps localstack

# Restart LocalStack
docker-compose -f docker-compose.localstack.yml restart localstack

# Check logs for errors
docker-compose -f docker-compose.localstack.yml logs localstack

# Verify health endpoint
curl http://localhost:4566/_localstack/health
```

#### 3. GitHub Actions workflow fails

**Problem**: Workflow fails in CI but passes locally

**Solutions**:
```bash
# Replicate locally with act
act push -e .github/workflows/.env.local

# Check GitHub Actions logs
# Repository → Actions → Select workflow run → View logs

# Verify secrets are set
gh secret list

# Check for environment-specific issues
# (e.g., NODE_ENV, database URLs)
```

#### 4. E2E tests fail in CI

**Problem**: Playwright tests pass locally but fail in CI

**Solutions**:
```bash
# Check if browsers are installed
npx playwright install --with-deps

# Review test artifacts from GitHub Actions
# Playwright report: playwright-report/
# Screenshots: test-results/
# Traces: test-results/

# Increase timeout in tests if needed
// page.waitForTimeout(5000)

# Run tests in headed mode for debugging
npm run e2e:debug
```

#### 5. Kubernetes deployment fails

**Problem**: `kubectl apply` fails

**Solutions**:
```bash
# Check kubeconfig is set
kubectl config current-context

# Verify secrets are configured
gh secret list

# Check cluster connectivity
kubectl cluster-info

# Apply manifests manually to see errors
kubectl apply -f k8s/namespace.yaml --dry-run=server
kubectl apply -f k8s/frontend-deployment.yaml --dry-run=server
```

### Debug Mode

```bash
# act with verbose output
act -v push

# Docker Compose with verbose output
docker-compose -f docker-compose.localstack.yml up --build

# kubectl with verbose output
kubectl apply -f k8s/frontend-deployment.yaml -v=9
```

---

## Resources and Documentation

### LocalStack Resources

- **Official Documentation**: https://docs.localstack.cloud/
- **GitHub Repository**: https://github.com/localstack/localstack
- **AWS CLI Integration**: https://docs.localstack.cloud/user-guide/aws-cli/
- **Services Supported**: https://docs.localstack.cloud/aws/feature-coverage/

### act Resources

- **GitHub Repository**: https://github.com/nektos/act
- **Documentation**: https://nektosact.com/
- **Installation Guide**: https://nektosact.com/installation/
- **Configuration**: https://nektosact.com/usage/

### GitHub Actions Resources

- **Official Documentation**: https://docs.github.com/en/actions
- **Workflow Syntax**: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- **Marketplace**: https://github.com/marketplace?type=actions
- **Best Practices**: https://docs.github.com/en/actions/learn-github-actions/best-practices-for-github-actions

### Kubernetes Resources

- **Official Documentation**: https://kubernetes.io/docs/
- **kubectl Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- **Deployment Guide**: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/

### Next.js Resources

- **Deployment Documentation**: https://nextjs.org/docs/deployment
- **Docker Deployment**: https://nextjs.org/docs/deployment#docker-image
- **Environment Variables**: https://nextjs.org/docs/basic-features/environment-variables

### Playwright Resources

- **Official Documentation**: https://playwright.dev/docs/intro
- **CI Integration**: https://playwright.dev/docs/ci
- **Debugging Tests**: https://playwright.dev/docs/debug
- **Best Practices**: https://playwright.dev/docs/best-practices

---

## Next Steps

1. **Set up LocalStack development environment**
   - Start services: `docker-compose -f docker-compose.localstack.yml up -d`
   - Configure AWS CLI to use LocalStack endpoint

2. **Test GitHub Actions locally with act**
   - Install act: `brew install act`
   - Run workflows: `act push`

3. **Configure GitHub Secrets**
   - Add `KUBE_CONFIG` secret for Kubernetes deployment
   - Add AWS secrets for production (if needed)

4. **Create Kubernetes manifests for frontend**
   - `k8s/frontend-deployment.yaml`
   - `k8s/frontend-service.yaml`

5. **Implement monitoring and observability**
   - Consider Prometheus/Grafana setup
   - Implement centralized logging

6. **Document production deployment procedures**
   - Create runbooks for common operations
   - Document rollback procedures

---

## Appendix

### A. Complete act Configuration

Create `.actrc` file in project root:

```bash
# .actrc
-P ubuntu-latest=catthehacker/ubuntu:act-latest
-P ubuntu-22.04=catthehacker/ubuntu:act-22.04
-P ubuntu-20.04=catthehacker/ubuntu:act-20.04
-s
-v
```

### B. Docker Compose Quick Reference

```bash
# Start all services
docker-compose -f docker-compose.localstack.yml up -d

# Stop all services
docker-compose -f docker-compose.localstack.yml down

# View logs
docker-compose -f docker-compose.localstack.yml logs -f

# Rebuild services
docker-compose -f docker-compose.localstack.yml up -d --build

# Execute command in container
docker-compose -f docker-compose.localstack.yml exec backend bash

# Remove all volumes
docker-compose -f docker-compose.localstack.yml down -v
```

### C. kubectl Quick Reference

```bash
# Get all resources
kubectl get all -n healthcare-auditor

# Describe resource
kubectl describe deployment backend -n healthcare-auditor

# Get logs
kubectl logs deployment/backend -n healthcare-auditor -f

# Execute command in pod
kubectl exec -it <pod-name> -n healthcare-auditor -- bash

# Apply manifest
kubectl apply -f k8s/backend-deployment.yaml

# Delete resource
kubectl delete deployment backend -n healthcare-auditor

# Scale deployment
kubectl scale deployment backend -n healthcare-auditor --replicas=5
```

---

**Document Version**: 1.0
**Last Updated**: 2026-02-12
**Maintained By**: Healthcare Auditor Team
