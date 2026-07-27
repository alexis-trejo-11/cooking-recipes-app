---
metrics:
  - label: "HTTP port"
    value: "8080"
    icon: "server"
    description: "SERVER_PORT — Uvicorn HTTP inside container"
  - label: "HTTPS port"
    value: "8443"
    icon: "lock"
    description: "SSL_PORT when SSL_ENABLED and cert files present"
  - label: "Health check"
    value: "/health"
    icon: "heart"
    description: "ALB and Docker HEALTHCHECK target"
  - label: "DB pool size"
    value: "10"
    icon: "database"
    description: "DB_POOL_SIZE in app_settings.py"

cloudServices:
  - name: "Amazon ECS (Fargate)"
    purpose: "Runs recipe-api container from ECR; auto-scaling on CPU; awsvpc networking to RDS and ElastiCache"
    icon: "aws-ecs"
    cost: "~$30–80/mo (0.5 vCPU / 1 GB task placeholder)"
  - name: "Amazon ECR"
    purpose: "Private registry for Docker images built from recipe-back-end/Dockerfile"
    icon: "aws-ecr"
    cost: "Storage + transfer (low for small teams)"
  - name: "Application Load Balancer"
    purpose: "HTTPS listener (ACM cert), forwards to ECS target group on container port 8080"
    icon: "aws-alb"
    cost: "~$18/mo + LCU"
  - name: "Amazon RDS (PostgreSQL 15)"
    purpose: "Production DATABASE_URL (postgresql+asyncpg); replaces SQLite cooking_app.db"
    icon: "aws-rds"
    cost: "~$25–60/mo (db.t4g.micro placeholder)"
  - name: "Amazon ElastiCache (Redis 7)"
    purpose: "Session store for refresh tokens; same role as docker-compose redis service locally"
    icon: "aws-elasticache"
    cost: "~$15–40/mo (cache.t4g.micro placeholder)"
  - name: "AWS Secrets Manager"
    purpose: "JWT_SECRET_KEY, DATABASE_URL credentials injected into ECS task definition"
    icon: "aws-secrets"
    cost: "~$0.40/secret/mo"
  - name: "Amazon CloudWatch"
    purpose: "ECS task logs, ALB access logs, optional alarms on 5xx rate"
    icon: "aws-cloudwatch"
    cost: "Pay per GB ingested"
  - name: "Route 53 + ACM"
    purpose: "api.recipes.example.com DNS alias to ALB; free public ACM certificate"
    icon: "aws-route53"
    cost: "Hosted zone ~$0.50/mo"

deploymentLayers:
  - name: "Clients"
    color: "#4F46E5"
    components:
      - name: "Angular SPA"
        icon: "layout"
        description: "CORS origins localhost:4200 and production domain in main.py"
      - name: "API consumers"
        icon: "smartphone"
        description: "Mobile or third-party apps using Bearer JWT"

  - name: "AWS edge & compute"
    color: "#059669"
    components:
      - name: "ALB + ACM"
        icon: "globe"
        description: "TLS at load balancer (preferred over container SSL in prod)"
      - name: "ECS Fargate service"
        icon: "docker"
        description: "Task runs ./start.sh → Alembic migrate → python main.py"
      - name: "ECR image"
        icon: "package"
        description: "Built from Dockerfile; tag recipe-api:1.0.0"

  - name: "Data plane"
    color: "#DC2626"
    components:
      - name: "RDS PostgreSQL"
        icon: "database"
        description: "Recipes, users, reviews, favorites, ingredients, steps"
      - name: "ElastiCache Redis"
        icon: "redis"
        description: "Auth sessions; port 6379 in VPC"
      - name: "EBS / logs volume"
        icon: "folder"
        description: "Optional ./logs mount; prefer CloudWatch in AWS"

  - name: "Local / CI (non-AWS)"
    color: "#D97706"
    components:
      - name: "docker-compose backend"
        icon: "docker"
        description: "Build ., ports 8080/8443, SQLite volume cooking_app.db"
      - name: "docker-compose redis"
        icon: "redis"
        description: "redis:7-alpine published as host 6378:6379"

dockerFiles:
  - service: "docker-compose.yml"
    description: "Local stack: backend + Redis; SQLite file bind-mount; healthcheck on /health."
    content: |
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

  - service: "Dockerfile"
    description: "python:3.11-slim; installs gcc+curl; copies app, optional cert.pem/key.pem/.env; HEALTHCHECK curl /health; CMD ./start.sh."
    content: |
      FROM python:3.11-slim
      WORKDIR /app
      RUN apt-get update && apt-get install -y gcc curl
      COPY requirements.txt .
      RUN pip install --no-cache-dir -r requirements.txt
      COPY . .
      EXPOSE 8080 8443
      HEALTHCHECK CMD curl -f http://localhost:8080/health
      CMD ["./start.sh"]

  - service: "start.sh"
    description: "Runs alembic upgrade head if needed, then exec python main.py (Uvicorn)."
    content: |
      # Check alembic_version table; migrate if missing
      alembic upgrade head
      exec python main.py
---

# Infrastructure

> **Production (AWS):** Push image to ECR → ECS service behind ALB → RDS + ElastiCache in private subnets → Secrets Manager for env. Do **not** COPY `.env` into production images; inject secrets at task runtime.

> **Local:** `docker compose up --build` uses SQLite on host and Redis on 6378. Set `DATABASE_URL` and Redis host in `.env` to match compose service names when testing full stack.

> **Warnings:** Dockerfile currently copies `cert.pem`, `key.pem`, and `.env`—acceptable for demos only. For AWS, terminate TLS on ALB and set `SSL_ENABLED=false` on tasks. Mounting `cooking_app.db` does not apply on Fargate; use RDS. Run `alembic upgrade head` against RDS before cutting traffic. Open only ALB security group to 443; ECS tasks need no public IP with private subnets + NAT.

> **Good:** Health endpoint and Docker HEALTHCHECK align with ECS service health checks. `docs/DEPLOYMENT.md` covers ECS task definitions, RDS parameter groups, and backup policies in detail.
