# syntax=docker/dockerfile:1
# Imagem da F0-c: a aplicação web (alvo padrão) e o preparo do banco (alvo "preparo"), da mesma construção.
# Base oficial node:24.21.0-bookworm-slim fixada pelo digest do índice multiplataforma, consultado em
# registry-1.docker.io em 28/09/2026 (linux/amd64 e arm64). Para o Cloud Run: docker build --platform linux/amd64.
# Nenhum segredo entra na imagem: banco, origem, ambiente e credenciais chegam por variáveis na execução.
ARG NODE_IMAGEM=node:24.21.0-bookworm-slim@sha256:0e0ff40c39bc087845bfb27465a0df4ea419520094bc35842ff83dd8cbe6f9b6

FROM ${NODE_IMAGEM} AS construir
ENV CI=1 NEXT_TELEMETRY_DISABLED=1 COREPACK_ENABLE_DOWNLOAD_PROMPT=0
WORKDIR /repo
# pnpm na versão exata do packageManager (12.5.1), pelo corepack do próprio Node.
RUN corepack enable
COPY . .
RUN pnpm install --frozen-lockfile \
  && pnpm run build \
  && pnpm --filter @safrion/db deploy --prod /saida/preparo

# Preparo do banco: papéis, banco com dono migrator, migrações e identidade (packages/db/src/preparo.ts).
# Uso: docker run --rm -e SAFRION_ADMIN_URL -e SAFRION_SENHA_MIGRATOR -e SAFRION_SENHA_APP_RUNTIME <imagem-preparo>
#      --ambiente hml --banco <nome>
FROM ${NODE_IMAGEM} AS preparo
ENV NODE_ENV=production
WORKDIR /app
COPY --from=construir /saida/preparo ./
USER node
ENTRYPOINT ["node", "dist/cli/preparar-banco.js"]

# Aplicação web: build standalone do Next (só os arquivos rastreados) e os estáticos. Arquivos do root, somente
# leitura para o usuário node; o servidor não grava em disco (verificado na bateria ponta a ponta).
FROM ${NODE_IMAGEM} AS web
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=8080 HOSTNAME=0.0.0.0
WORKDIR /app
COPY --from=construir /repo/apps/web/.next/standalone ./
COPY --from=construir /repo/apps/web/.next/static ./apps/web/.next/static
USER node
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:'+process.env.PORT+'/saude').then(r=>process.exit(r.ok?0:1),()=>process.exit(1))"]
CMD ["node", "apps/web/server.js"]
