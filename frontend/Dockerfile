# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Build stage: compile the Angular SSR app.
# ---------------------------------------------------------------------------
FROM node:22-alpine AS build
WORKDIR /app

# package-lock.json is git-ignored in this repo, so use npm install (it still
# honors a lockfile when one happens to be present in the build context).
COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

# ---------------------------------------------------------------------------
# Runtime stage: serve with the Node/Express SSR server only.
# ---------------------------------------------------------------------------
FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production

# Runtime configuration (override with compose / -e; no rebuild needed).
# API_BASE_URL and BASE_URL are public (injected into the browser HTML).
ENV API_BASE_URL=http://localhost:8080/api/v1
ENV BASE_URL=http://localhost:4200
ENV ALLOWED_HOSTS=localhost
ENV PORT=4000

COPY --from=build /app/dist ./dist

EXPOSE 4000

# Run unprivileged.
USER node

CMD ["node", "dist/recipe-front-end/server/server.mjs"]
