# Dockerfile — Node/TypeScript multi-stage, produção mínima e não-root.
# Python: troque por python:3.12-slim + uv; Go: build estático + distroless/static.

# ---- dependências ----
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts

# ---- build ----
FROM deps AS build
COPY . .
RUN npm run build && npm prune --omit=dev

# ---- produção ----
FROM node:22-alpine AS runner
ENV NODE_ENV=production \
    PORT=3000
WORKDIR /app
RUN apk add --no-cache curl tini && addgroup -S app && adduser -S app -G app
COPY --from=build --chown=app:app /app/node_modules ./node_modules
COPY --from=build --chown=app:app /app/dist ./dist
COPY --from=build --chown=app:app /app/package.json ./
COPY --from=build --chown=app:app /app/migrations ./migrations
USER app
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD curl -fsS http://localhost:${PORT}/health || exit 1
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "dist/main.js"]

# .dockerignore: node_modules, dist, coverage, .git, .env*, *.md, e2e, test-results
