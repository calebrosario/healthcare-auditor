# Healthcare Auditor CI/CD Quick Start

This README provides quick setup instructions for CI/CD development with LocalStack and act.

## Quick Start

### 1. Local Development with LocalStack

```bash
# Start all services including LocalStack
docker-compose -f docker-compose.localstack.yml up -d

# Check service status
docker-compose -f docker-compose.localstack.yml ps

# Access services:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - LocalStack: http://localhost:4566
# - Neo4j Browser: http://localhost:7474
```

### 2. Test GitHub Actions Locally with act

```bash
# Install act (macOS)
brew install act

# Run all workflows
act push

# Run specific workflow
act -W .github/workflows/frontend-ci-cd.yml push

# Run with environment variables
act push -e .github/workflows/.env.local
```

### 3. Stop Services

```bash
# Stop all services
docker-compose -f docker-compose.localstack.yml down

# Stop and remove volumes
docker-compose -f docker-compose.localstack.yml down -v
```

## File Structure

```
.github/workflows/
├── ci-cd.yml              # Backend CI/CD (existing)
├── frontend-ci-cd.yml      # Frontend CI/CD (new)
└── .env.local             # Local act environment (new)

docker-compose.localstack.yml  # LocalStack-enabled compose (new)

.research/
└── CI_CD_DEVELOPMENT_PLAN.md # Comprehensive guide (new)

k8s/
└── frontend-deployment.yaml    # Frontend K8s manifest (new)
```

## Key Features

### Frontend CI/CD Workflow

- **Linting**: ESLint with zero warnings
- **Type Checking**: TypeScript strict mode
- **Unit Tests**: Jest with coverage reporting
- **E2E Tests**: Playwright (99 tests)
- **Docker Build**: Multi-stage, multi-arch (amd64/arm64)
- **Security Scan**: Trivy vulnerability scanner
- **Kubernetes Deploy**: Automated on master/main push

### LocalStack Integration

Services enabled:
- S3, DynamoDB, Lambda, API Gateway
- SQS, SNS, IAM, CloudWatch
- Events, Secrets Manager, Step Functions

### Workflow Triggers

**Frontend**: Push/PR to master/main/develop with `frontend/**` changes
**Backend**: Push/PR to master/main/develop with `backend/**` or `k8s/**` changes

## Documentation

For comprehensive documentation, see:
- `.research/CI_CD_DEVELOPMENT_PLAN.md` - Full guide with examples
- `.github/workflows/frontend-ci-cd.yml` - Frontend workflow
- `docker-compose.localstack.yml` - LocalStack configuration

## Troubleshooting

```bash
# Check LocalStack health
curl http://localhost:4566/_localstack/health

# View LocalStack logs
docker-compose -f docker-compose.localstack.yml logs localstack -f

# Debug act with verbose output
act -v push

# Check Docker logs
docker-compose -f docker-compose.localstack.yml logs -f
```

## Next Steps

1. Configure GitHub Secrets: `KUBE_CONFIG`, AWS secrets
2. Test workflows locally with `act push`
3. Verify E2E tests: `cd frontend && npm run e2e`
4. Deploy to Kubernetes: `kubectl apply -f k8s/frontend-deployment.yaml`
