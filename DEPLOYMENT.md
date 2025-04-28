# Climbup Backend Deployment Runbook

## Prerequisites
- Kubernetes cluster access
- kubectl configured
- Docker registry access
- GitHub repository access
- Required secrets and configurations

## Environment Setup

### 1. Namespace Creation
```bash
# Create staging namespace
kubectl create namespace climbup-staging

# Create production namespace
kubectl create namespace climbup-prod
```

### 2. Secret Management
```bash
# Create staging secrets
kubectl apply -f k8s/staging/secrets.yaml

# Create production secrets (requires actual values)
kubectl apply -f k8s/production/secrets.yaml
```

### 3. ConfigMap Setup
```bash
# Apply staging config
kubectl apply -f k8s/staging/configmap.yaml

# Apply production config
kubectl apply -f k8s/production/configmap.yaml
```

## Deployment Process

### Staging Deployment
1. Update GitHub secrets for staging
2. Push to staging branch
3. Monitor GitHub Actions
4. Verify deployment
```bash
kubectl get pods -n climbup-staging
kubectl get svc -n climbup-staging
```

### Production Deployment
1. Update GitHub secrets for production
2. Create release tag
3. Monitor GitHub Actions
4. Verify deployment
```bash
kubectl get pods -n climbup-prod
kubectl get svc -n climbup-prod
```

## Monitoring Setup

### 1. Prometheus Configuration
```bash
# Apply monitoring config
kubectl apply -f k8s/monitoring.yaml
```

### 2. Grafana Setup
1. Access Grafana dashboard
2. Import predefined dashboards
3. Configure alert channels

## Backup Procedures

### 1. Database Backups
```bash
# Verify backup jobs
kubectl get cronjobs -n climbup-prod

# Manual backup trigger
kubectl create job --from=cronjob/postgres-backup manual-backup -n climbup-prod
```

### 2. Backup Verification
```bash
# List available backups
kubectl exec -it postgres-pod -n climbup-prod -- ls /backup
```

## Recovery Procedures

### 1. Database Recovery
```bash
# PostgreSQL recovery
kubectl exec -it postgres-pod -n climbup-prod -- \
  pg_restore -h postgres-service -U climbup_user -d climbup /backup/latest_backup.sql.gz

# MongoDB recovery
kubectl exec -it mongodb-pod -n climbup-prod -- \
  mongorestore --host=mongodb-service --archive=/backup/latest_backup.archive
```

### 2. Rollback Procedure
```bash
# Rollback deployment
kubectl rollout undo deployment/climbup-backend -n climbup-prod
```

## Monitoring and Alerts

### 1. Key Metrics to Monitor
- API response times
- Error rates
- Database connection status
- Memory usage
- CPU utilization

### 2. Alert Thresholds
- Error rate > 1%
- Response time > 1s
- Memory usage > 80%
- CPU usage > 70%

## Troubleshooting

### 1. Common Issues
- Database connection failures
- High latency
- Memory leaks
- Rate limiting issues

### 2. Resolution Steps
1. Check pod logs
2. Verify database connections
3. Check resource utilization
4. Review recent deployments

## Contact Information
- DevOps Team: devops@climbup.com
- Emergency Contact: +1-XXX-XXX-XXXX 