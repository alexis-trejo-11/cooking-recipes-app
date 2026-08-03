# Dockerfile - VERSIÓN MEJORADA
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación (excluyendo lo que está en .dockerignore)
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs alembic/versions

# Runtime config (.env, TLS certs) is injected at deploy time via compose /
# secrets — do NOT bake them into the image (they are gitignored and would
# break CI builds).

# Default develop ports; production overrides SERVER_PORT via compose.
EXPOSE 8080 8443

# Salud de la aplicación ($$ so SERVER_PORT expands at runtime, not build)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$${SERVER_PORT:-8080}/health || exit 1

COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
