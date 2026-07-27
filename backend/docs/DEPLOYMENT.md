# Deployment Guide

Comprehensive guide for deploying the Cooking Recipe API to production environments.

## Table of Contents

- [Deployment Options](#deployment-options)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Production Configuration](#production-configuration)
- [Database Setup](#database-setup)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Performance Tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)

## Deployment Options

### 1. Docker (Recommended)

- **Pros:** Easy deployment, consistent environments, scalability
- **Best For:** Most production environments
- **Requirements:** Docker, Docker Compose

### 2. Traditional Server

- **Pros:** Direct control, simple setup
- **Best For:** Single server deployments
- **Requirements:** Linux server, Python 3.11+

### 3. Cloud Platforms

- **AWS:** Elastic Beanstalk, ECS, Lambda
- **Google Cloud:** Cloud Run, App Engine, GKE
- **Azure:** App Service, Container Instances, AKS
- **Heroku:** Simple deployment with Procfile

### 4. Kubernetes

- **Pros:** High scalability, orchestration
- **Best For:** Large-scale production
- **Requirements:** Kubernetes cluster, Helm charts

## Pre-Deployment Checklist

### Security

- [ ] Change default JWT_SECRET_KEY to a strong random key
- [ ] Enable SSL/TLS certificates (not self-signed)
- [ ] Configure CORS for production domains
- [ ] Set DEBUG=False
- [ ] Review and restrict database access
- [ ] Set up rate limiting
- [ ] Configure firewall rules
- [ ] Implement proper logging (no sensitive data)

### Database

- [ ] Migrate to PostgreSQL (recommended over SQLite)
- [ ] Run all database migrations
- [ ] Set up automated backups
- [ ] Configure connection pooling
- [ ] Create database indexes
- [ ] Test database performance

### Performance

- [ ] Set up Redis for caching and rate limiting
- [ ] Configure proper connection pool sizes
- [ ] Enable gzip compression
- [ ] Optimize static file serving (if any)
- [ ] Test under load (load testing)

### Monitoring

- [ ] Set up application monitoring
- [ ] Configure error tracking (Sentry)
- [ ] Set up health check endpoints
- [ ] Configure log aggregation
- [ ] Set up alerting

### Documentation

- [ ] Update API documentation
- [ ] Document environment variables
- [ ] Create runbook for common issues
- [ ] Document backup/restore procedures

## Docker Deployment

### 1. Build Docker Image

```bash
# Navigate to project directory
cd recipe-back-end

# Build the image
docker build -t recipe-api:1.0.0 .

# Tag for registry
docker tag recipe-api:1.0.0 your-registry/recipe-api:1.0.0

# Push to registry
docker push your-registry/recipe-api:1.0.0
```

### 2. Docker Compose Setup

**Production docker-compose.yml:**

```yaml
version: "3.8"

services:
  backend:
    image: recipe-api:1.0.0
    container_name: recipe-api-backend
    restart: always
    ports:
      - "8080:8080"
      - "8443:8443"
    environment:
      - DEBUG=false
      - DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/recipes
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - RATE_LIMIT_ENABLED=true
      - SSL_ENABLED=true
      - SSL_KEYFILE=/certs/key.pem
      - SSL_CERTFILE=/certs/cert.pem
    volumes:
      - ./logs:/app/logs
      - ./certs:/app/certs:ro
    depends_on:
      - postgres
      - redis
    networks:
      - recipe-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    container_name: recipe-api-postgres
    restart: always
    environment:
      - POSTGRES_DB=recipes
      - POSTGRES_USER=recipe_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - recipe-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U recipe_user -d recipes"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: recipe-api-redis
    restart: always
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    networks:
      - recipe-network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: recipe-api-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
      - nginx-logs:/var/log/nginx
    depends_on:
      - backend
    networks:
      - recipe-network

volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local
  nginx-logs:
    driver: local

networks:
  recipe-network:
    driver: bridge
```

### 3. Nginx Reverse Proxy Configuration

**nginx.conf:**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        least_conn;
        server backend:8080;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/s;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    server {
        listen 80;
        server_name api.yourdomain.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        # SSL certificates
        ssl_certificate /etc/nginx/certs/cert.pem;
        ssl_certificate_key /etc/nginx/certs/key.pem;

        # SSL configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API endpoints
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;

            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Auth endpoints (stricter rate limiting)
        location /api/v1/auth/ {
            limit_req zone=auth_limit burst=5 nodelay;

            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check (no rate limiting)
        location /health {
            proxy_pass http://backend;
            access_log off;
        }

        # API documentation
        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }
    }
}
```

### 4. Deploy with Docker Compose

```bash
# Create .env file for secrets
cat > .env << EOF
JWT_SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)
EOF

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Check status
docker-compose ps

# Run migrations
docker-compose exec backend alembic upgrade head

# Restart services
docker-compose restart backend

# Stop services
docker-compose down
```

## Cloud Deployment

### AWS Deployment (Elastic Container Service)

#### 1. Prerequisites

```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure
```

#### 2. Create ECR Repository

```bash
# Create repository
aws ecr create-repository --repository-name recipe-api

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker tag recipe-api:1.0.0 <account-id>.dkr.ecr.us-east-1.amazonaws.com/recipe-api:1.0.0
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/recipe-api:1.0.0
```

#### 3. RDS Database Setup

```bash
# Create PostgreSQL RDS instance
aws rds create-db-instance \
  --db-instance-identifier recipe-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password ${DB_PASSWORD} \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx
```

#### 4. ElastiCache Redis

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id recipe-cache \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

#### 5. ECS Task Definition

```json
{
  "family": "recipe-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "recipe-api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/recipe-api:1.0.0",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "DEBUG", "value": "false" },
        { "name": "DATABASE_URL", "value": "postgresql+asyncpg://..." }
      ],
      "secrets": [
        {
          "name": "JWT_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account-id:secret:jwt-secret"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/recipe-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run Deployment

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/recipe-api

# Deploy to Cloud Run
gcloud run deploy recipe-api \
  --image gcr.io/PROJECT_ID/recipe-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DEBUG=false \
  --set-secrets JWT_SECRET_KEY=jwt-secret:latest
```

### Heroku Deployment

```bash
# Create Heroku app
heroku create recipe-api-prod

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis addon
heroku addons:create heroku-redis:hobby-dev

# Set environment variables
heroku config:set DEBUG=false
heroku config:set JWT_SECRET_KEY=$(openssl rand -hex 32)

# Deploy
git push heroku main

# Run migrations
heroku run alembic upgrade head

# View logs
heroku logs --tail
```

## Production Configuration

### Environment Variables

**Required:**

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Security
JWT_SECRET_KEY=<strong-random-32-char-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRES_DAYS=90

# Application
DEBUG=False

# Rate Limiting
RATE_LIMIT_ENABLED=True

# SSL (if using)
SSL_ENABLED=True
SSL_KEYFILE=/path/to/key.pem
SSL_CERTFILE=/path/to/cert.pem
SERVER_PORT=8080
SSL_PORT=8443
```

**Optional:**

```bash
# Database Pool
DB_ECHO=False
DB_POOL_SIZE=20
DB_TIMEOUT=30.0

# Redis (if separate from rate limiting)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<password>
```

### Generate Secure Keys

```bash
# JWT Secret Key (32+ characters)
openssl rand -hex 32

# Or using Python
python -c "import secrets; print(secrets.token_hex(32))"

# SSL Certificates (Let's Encrypt - recommended)
certbot certonly --standalone -d api.yourdomain.com
```

## Database Setup

### PostgreSQL Production Setup

#### 1. Create Database

```sql
-- Create database
CREATE DATABASE recipes;

-- Create user
CREATE USER recipe_user WITH ENCRYPTED PASSWORD 'strong_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE recipes TO recipe_user;

-- Connect to recipes database
\c recipes

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO recipe_user;
```

#### 2. Run Migrations

```bash
# Export database URL
export DATABASE_URL="postgresql+asyncpg://recipe_user:password@localhost:5432/recipes"

# Run migrations
alembic upgrade head

# Verify
alembic current
```

#### 3. Database Tuning

```sql
-- Increase connection limit
ALTER SYSTEM SET max_connections = 200;

-- Increase shared buffers (25% of RAM)
ALTER SYSTEM SET shared_buffers = '2GB';

-- Increase effective cache size (50-75% of RAM)
ALTER SYSTEM SET effective_cache_size = '6GB';

-- Reload configuration
SELECT pg_reload_conf();
```

### Migration Best Practices

```bash
# Always backup before migrations
pg_dump -U recipe_user recipes > backup_$(date +%Y%m%d_%H%M%S).sql

# Test migrations on staging first
alembic upgrade head --sql > migration.sql
# Review migration.sql

# Run migration
alembic upgrade head

# If issues, rollback
alembic downgrade -1
```

## SSL/TLS Configuration

### Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt-get install certbot

# Obtain certificate
sudo certbot certonly --standalone -d api.yourdomain.com

# Certificates will be in:
# /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/api.yourdomain.com/privkey.pem

# Auto-renewal (add to crontab)
0 0 * * * certbot renew --quiet
```

### Application SSL Configuration

```python
# .env
SSL_ENABLED=True
SSL_KEYFILE=/etc/letsencrypt/live/api.yourdomain.com/privkey.pem
SSL_CERTFILE=/etc/letsencrypt/live/api.yourdomain.com/fullchain.pem
SSL_PORT=8443
```

## Monitoring & Logging

### Application Monitoring

#### Sentry Integration

```bash
# Install Sentry SDK
pip install sentry-sdk[fastapi]
```

```python
# main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxxxx@sentry.io/xxxxx",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)
```

#### Prometheus Metrics

```bash
# Install prometheus client
pip install prometheus-fastapi-instrumentator
```

```python
# main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
# Metrics available at /metrics
```

### Logging Configuration

**Production logging:**

```python
# config/logging_config.py
LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
            "formatter": "detailed",
            "level": "INFO"
        }
    },
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}
```

### Log Aggregation (ELK Stack)

```yaml
# docker-compose with ELK
services:
  elasticsearch:
    image: elasticsearch:8.9.0
    environment:
      - discovery.type=single-node

  logstash:
    image: logstash:8.9.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: kibana:8.9.0
    ports:
      - "5601:5601"
```

## Backup & Recovery

### Automated Backups

**PostgreSQL backup script:**

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="recipe_db_$DATE.sql"

# Create backup
pg_dump -U recipe_user -h localhost recipes > "$BACKUP_DIR/$FILENAME"

# Compress
gzip "$BACKUP_DIR/$FILENAME"

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $FILENAME.gz"
```

**Crontab:**

```bash
# Daily backup at 2 AM
0 2 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1
```

### Restore Procedure

```bash
# Restore from backup
gunzip backup_file.sql.gz
psql -U recipe_user -h localhost recipes < backup_file.sql

# Or with Docker
docker exec -i recipe-api-postgres psql -U recipe_user recipes < backup_file.sql
```

## Performance Tuning

### Database Optimization

```python
# Increase connection pool
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30.0

# Enable query logging (temporarily)
DB_ECHO=True  # Only for debugging
```

### Redis Configuration

```redis
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### Application Optimization

```python
# Use async operations
# Batch database operations
# Implement caching
# Optimize queries with proper indexes
```

### Load Balancing

```nginx
upstream backend {
    least_conn;
    server backend1:8080 weight=3;
    server backend2:8080 weight=2;
    server backend3:8080 weight=1;
}
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Symptom:** `asyncpg.exceptions.ConnectionDoesNotExistError`

**Solution:**

```bash
# Check database is running
docker ps | grep postgres

# Check connection string
echo $DATABASE_URL

# Test connection
psql -U recipe_user -h localhost -d recipes

# Check connection pool size
# Increase DB_POOL_SIZE if needed
```

#### 2. High Memory Usage

**Solution:**

```bash
# Check container stats
docker stats

# Limit memory in docker-compose.yml
services:
  backend:
    mem_limit: 1g
    mem_reservation: 512m
```

#### 3. Slow API Responses

**Solution:**

```bash
# Check database query performance
# Enable DB_ECHO temporarily

# Check for N+1 queries
# Add proper indexes

# Monitor with:
docker-compose exec backend python -m cProfile main.py
```

#### 4. SSL Certificate Errors

**Solution:**

```bash
# Verify certificate files exist
ls -l /path/to/certs/

# Check certificate validity
openssl x509 -in cert.pem -text -noout

# Renew Let's Encrypt certificates
certbot renew
```

### Health Checks

```bash
# Application health
curl http://localhost:8080/health

# Database health
docker-compose exec postgres pg_isready

# Redis health
docker-compose exec redis redis-cli ping

# View all service status
docker-compose ps
```

### Log Analysis

```bash
# View application logs
docker-compose logs -f backend | grep ERROR

# View database logs
docker-compose logs postgres

# View nginx logs
docker-compose exec nginx tail -f /var/log/nginx/access.log
```

---

## Post-Deployment

### Smoke Tests

```bash
# Test health endpoint
curl https://api.yourdomain.com/health

# Test signup
curl -X POST https://api.yourdomain.com/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Test","last_name":"User","email":"test@example.com","password":"Test123!@#","gender":"male"}'

# Test search
curl https://api.yourdomain.com/api/v1/recipes?page=1&size=10
```

### Performance Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Load test
ab -n 1000 -c 10 https://api.yourdomain.com/health

# Or use wrk
wrk -t12 -c400 -d30s https://api.yourdomain.com/api/v1/recipes
```

---

**Last Updated:** November 2025
**Deployment Guide Version:** 1.0.0
