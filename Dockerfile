# Imagem da F0-c: a aplicação web (alvo padrão) e o preparo do banco (alvo "preparo"), da mesma construção.
# Construção: node:24.21.0-bookworm-slim oficial, fixada pelo digest do índice multiplataforma consultado em
# registry-1.docker.io em 28/09/2026. Execução (HML-IMG-01): distroless cc-debian13 nonroot, fixada pelo digest do
# índice multiplataforma consultado em gcr.io em 28/09/2026: glibc, libstdc++ e certificados, mais o binário node da
# construção. Sem shell, sem gerenciador de pacotes e sem npm, corepack ou yarn, que o runtime não usa.
# Para o Cloud Run: docker build --platform linux/amd64.
# Nenhum segredo entra na imagem: banco, origem, ambiente e credenciais chegam por variáveis na execução.
# Sem diretiva syntax: o frontend do Dockerfile embutido no BuildKit basta, e nada é baixado por etiqueta móvel.
ARG NODE_IMAGEM=node:24.21.0-bookworm-slim@sha256:0e0ff40c39bc087845bfb27465a0df4ea419520094bc35842ff83dd8cbe6f9b6
ARG EXECUCAO_IMAGEM=gcr.io/distroless/cc-debian13:nonroot@sha256:54df941ed0d06a1bd95ef5e0ce391fd8d9f94b64782dc9a60062727849ee3f97

FROM ${NODE_IMAGEM} AS construir
ENV CI=1 NEXT_TELEMETRY_DISABLED=1 COREPACK_ENABLE_DOWNLOAD_PROMPT=0
WORKDIR /repo
# pnpm na versão exata do packageManager (12.5.1), pelo corepack do próprio Node.
RUN corepack enable
COPY . .
RUN pnpm install --frozen-lockfile \
  && pnpm run build \
  && pnpm --filter @safrion/db deploy --prod /saida/preparo

# Base de execução dos dois alvos: o mesmo Node 24.21.0 da construção e nada mais da imagem do Node. A base já roda
# como 65532 (nonroot); /app é criado como root para que pasta e arquivos fiquem somente leitura para o processo, e
# nenhum dos dois grava em disco.
FROM ${EXECUCAO_IMAGEM} AS execucao
USER 0:0
WORKDIR /app
COPY --from=construir /usr/local/bin/node /usr/local/bin/node
USER 65532:65532

# Preparo do banco: papéis, banco com dono migrator, migrações e identidade (packages/db/src/preparo.ts).
# Uso: docker run --rm -e SAFRION_ADMIN_URL -e SAFRION_SENHA_MIGRATOR -e SAFRION_SENHA_APP_RUNTIME <imagem-preparo>
#      --ambiente hml --banco <nome>
FROM execucao AS preparo
ENV NODE_ENV=production
COPY --from=construir /saida/preparo ./
ENTRYPOINT ["node", "dist/cli/preparar-banco.js"]

# Aplicação web: build standalone do Next (só os arquivos rastreados) e os estáticos. O servidor não
# grava em disco (verificado na bateria ponta a ponta e com o sistema de arquivos somente leitura na CI).
FROM execucao AS web
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=8080 HOSTNAME=0.0.0.0
COPY --from=construir /repo/apps/web/.next/standalone ./
COPY --from=construir /repo/apps/web/.next/static ./apps/web/.next/static
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD ["node", "-e", "fetch('http://127.0.0.1:'+process.env.PORT+'/saude').then(r=>process.exit(r.ok?0:1),()=>process.exit(1))"]
CMD ["node", "apps/web/server.js"]
