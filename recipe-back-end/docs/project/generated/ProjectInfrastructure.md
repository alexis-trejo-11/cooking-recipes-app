# Infrastructure

## Metrics

| Label | Value | Description |
| --- | --- | --- |
| HTTP port | 8080 | SERVER_PORT — Uvicorn HTTP inside container |
| HTTPS port | 8443 | SSL_PORT when SSL_ENABLED and cert files present |
| Health check | /health | ALB and Docker HEALTHCHECK target |
| DB pool size | 10 | DB_POOL_SIZE in app_settings.py |

## Cloud services

| Service | Purpose | Est. cost |
| --- | --- | --- |
| Amazon ECS (Fargate) | Runs recipe-api container from ECR; auto-scaling on CPU; awsvpc networking to RDS and ElastiCache | ~$30–80/mo (0.5 vCPU / 1 GB task placeholder) |
| Amazon ECR | Private registry for Docker images built from recipe-back-end/Dockerfile | Storage + transfer (low for small teams) |
| Application Load Balancer | HTTPS listener (ACM cert), forwards to ECS target group on container port 8080 | ~$18/mo + LCU |
| Amazon RDS (PostgreSQL 15) | Production DATABASE_URL (postgresql+asyncpg); replaces SQLite cooking_app.db | ~$25–60/mo (db.t4g.micro placeholder) |
| Amazon ElastiCache (Redis 7) | Session store for refresh tokens; same role as docker-compose redis service locally | ~$15–40/mo (cache.t4g.micro placeholder) |
| AWS Secrets Manager | JWT_SECRET_KEY, DATABASE_URL credentials injected into ECS task definition | ~$0.40/secret/mo |
| Amazon CloudWatch | ECS task logs, ALB access logs, optional alarms on 5xx rate | Pay per GB ingested |
| Route 53 + ACM | api.recipes.example.com DNS alias to ALB; free public ACM certificate | Hosted zone ~$0.50/mo |

## Deployment layers

### Clients

- **Angular SPA** — CORS origins localhost:4200 and production domain in main.py
- **API consumers** — Mobile or third-party apps using Bearer JWT

### AWS edge & compute

- **ALB + ACM** — TLS at load balancer (preferred over container SSL in prod)
- **ECS Fargate service** — Task runs ./start.sh → Alembic migrate → python main.py
- **ECR image** — Built from Dockerfile; tag recipe-api:1.0.0

### Data plane

- **RDS PostgreSQL** — Recipes, users, reviews, favorites, ingredients, steps
- **ElastiCache Redis** — Auth sessions; port 6379 in VPC
- **EBS / logs volume** — Optional ./logs mount; prefer CloudWatch in AWS

### Local / CI (non-AWS)

- **docker-compose backend** — Build ., ports 8080/8443, SQLite volume cooking_app.db
- **docker-compose redis** — redis:7-alpine published as host 6378:6379

## Docker configuration

### docker-compose.yml

Local stack: backend + Redis; SQLite file bind-mount; healthcheck on /health.

```yaml
services:
  backend:
    build: .
    ports:
      - "8080:8080"
      - "8443:8443"
    volumes:
      - ./cooking_app.db:/app/cooking_app.db
      - ./logs:/app/logs
    environment:
      - DEBUG=false
    restart: unless-stopped
  redis:
    image: redis:7-alpine
    ports:
      - "6378:6379"
```

### Dockerfile

python:3.11-slim; installs gcc+curl; copies app, optional cert.pem/key.pem/.env; HEALTHCHECK curl /health; CMD ./start.sh.

```yaml
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc curl
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080 8443
HEALTHCHECK CMD curl -f http://localhost:8080/health
CMD ["./start.sh"]
```

### start.sh

Runs alembic upgrade head if needed, then exec python main.py (Uvicorn).

```yaml
# Check alembic_version table; migrate if missing
alembic upgrade head
exec python main.py
```

## Additional notes

# Infrastructure

> **Production (AWS):** Push image to ECR → ECS service behind ALB → RDS + ElastiCache in private subnets → Secrets Manager for env. Do **not** COPY `.env` into production images; inject secrets at task runtime.

> **Local:** `docker compose up --build` uses SQLite on host and Redis on 6378. Set `DATABASE_URL` and Redis host in `.env` to match compose service names when testing full stack.

> **Warnings:** Dockerfile currently copies `cert.pem`, `key.pem`, and `.env`—acceptable for demos only. For AWS, terminate TLS on ALB and set `SSL_ENABLED=false` on tasks. Mounting `cooking_app.db` does not apply on Fargate; use RDS. Run `alembic upgrade head` against RDS before cutting traffic. Open only ALB security group to 443; ECS tasks need no public IP with private subnets + NAT.

> **Good:** Health endpoint and Docker HEALTHCHECK align with ECS service health checks. `docs/DEPLOYMENT.md` covers ECS task definitions, RDS parameter groups, and backup policies in detail.

