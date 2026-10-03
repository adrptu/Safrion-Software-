---
name: dev-backend
description: Implemente e revise APIs, serviços, dados, integrações e jobs com validação, isolamento, transações, idempotência e recuperação. Use quando mudar comportamento de backend ou persistência.
---

# Backend — meta: correto, seguro, rápido e pronto para escalar

## Arquitetura
- **Monólito modular por domínio**: `src/modules/<dominio>/{routes,service,repository,schema,events}`; módulo só fala com outro via interface pública (service) ou evento — nunca acessa a tabela alheia. Estrutura em [assets/estrutura-modular.md](assets/estrutura-modular.md).
- **Camadas**: rota (HTTP, validação, auth) → serviço (regra de negócio, transação) → repositório (SQL/ORM). Domínio não importa framework nem infra. Sem "hexagonal completo" onde não há necessidade; sem lógica de negócio em controller.
- Estado durável e autoritativo não depende de memória do processo. Cache em memória pode ser descartável e limitado; Redis/objetos/filas entram por necessidade, não por padrão.
- Trabalho assíncrono ou demorado usa fila quando melhora prazo de resposta/recuperação. Retry limitado, idempotência e tratamento de falha conforme o comando. **Outbox** quando é necessário garantir evento junto da transação.
- **Multi-tenant**: `tenant_id` em toda tabela de negócio, filtro obrigatório no repositório (ou RLS no Postgres), teste que prova isolamento.

## API
- **REST previsível**: substantivos no plural (`/pedidos/{id}/itens`), verbos HTTP corretos, códigos certos (200/201/204/400/401/403/404/409/422/429/500). Versionar na URL (`/v1`) só quando quebrar compatibilidade.
- **Validação na borda com schema** (zod / pydantic / class-validator): tipos derivados do schema; nada entra sem validar; `additionalProperties: false`.
- **Erros padronizados** — RFC 9457 `application/problem+json`: `{ type, title, status, detail, instance, errors: [{ field, message }] }`. Mensagem para o usuário em pt-BR e acionável; sem stack trace, sem detalhe interno.
- **Paginação por cursor** (não offset) em listas que crescem; limite máximo; ordenação estável (`created_at, id`).
- **Idempotência**: comandos com efeito financeiro/estoque ou sujeitos a repetição exigem deduplicação atômica. Escopar chave por empresa/ator/comando, vincular ao conteúdo e devolver resultado consistente. PUT/DELETE devem implementar sua semântica idempotente também nos efeitos colaterais; o verbo sozinho não a garante.
- **Rate limiting** por usuário/IP/token; **CORS** restrito; **compressão**; **ETag/Cache-Control** em GET cacheável.
- **OpenAPI gerado do código** (não escrito à mão), publicado em `/docs`; cliente tipado gerado para o frontend (openapi-typescript/orval).
- **Webhooks recebidos**: verificar assinatura, responder 2xx rápido, processar na fila, deduplicar por id do evento. **Enviados**: assinar, retry com backoff, log de entregas.
- Tempo real: SSE para notificações simples, WebSocket só com necessidade bidirecional.

## Dados
- **PostgreSQL** por padrão quando não houver decisão vigente. Migrações versionadas com compatibilidade, ensaio com dados e estratégia de recuperação; **expand → migrate → contract**. Não prometer reversibilidade sem perda de dados nem executar migração destrutiva para reverter código.
- **Constraints no banco**: NOT NULL, UNIQUE, FK, CHECK — o banco é a última defesa. Enum como tabela ou CHECK.
- Índices para padrões reais de acesso, conferidos com plano e carga representativa; considerar custo de escrita e armazenamento. `EXPLAIN ANALYZE` executa a consulta: em mutações, usar ambiente de teste apropriado.
- **Transações** curtas envolvendo o que precisa ser atômico; nível de isolamento consciente; lock otimista (`version`) em edição concorrente; `SELECT … FOR UPDATE SKIP LOCKED` para filas em tabela.
- **Sem N+1** (joins, `include`, dataloader); **paginar sempre**; streams para exportação.
- Tipos: instantes com fuso, datas civis como datas; valores monetários, preços unitários, doses e taxas com precisão/escala explícitas por domínio (não arredondar tudo a centavos). IDs conforme contrato; JSONB para dados semi-estruturados justificados.
- Colunas padrão: `id, created_at, updated_at`, `deleted_at` se soft delete (e índice parcial `WHERE deleted_at IS NULL`). Auditoria (quem/quando/o quê) em entidades de negócio.
- Pool de conexões (PgBouncer em escala); **backups automáticos + PITR + restauração testada** (`dev-infra`).
- **Seeds** realistas para dev/teste; nunca dado de produção em ambiente inferior sem anonimizar.

## Segurança (OWASP Top 10 sempre)
- **Autenticação**: OIDC/OAuth2 com provedor (Google, Auth0, Keycloak) ou senha com **Argon2id**; tokens de acesso curtos (≤ 15 min) + refresh rotativo em cookie `HttpOnly; Secure; SameSite`; MFA disponível; bloqueio progressivo de tentativas.
- **Autorização centralizada** (política/policy por recurso e ação) verificada em **todo** endpoint, incluindo "esse objeto é do usuário/tenant?". Testes de 401/403/404 cruzado.
- Queries parametrizadas; saída escapada; upload validado (tipo real, tamanho, nome sanitizado, armazenado fora do webroot, antivírus se público).
- Cabeçalhos: HSTS, CSP, X-Content-Type-Options, Referrer-Policy (helmet/secure headers).
- **Segredos** só em cofre/variáveis de ambiente, rotacionáveis; `.env.example` sem valores; gitleaks no CI.
- Logs **sem PII/segredos** (mascarar CPF, e-mail, token); LGPD: base legal, minimização, exclusão sob pedido, criptografia em repouso para dados sensíveis.
- Dependências auditadas no CI (osv-scanner/pip-audit) e atualizadas semanalmente.

## Resiliência
- **Timeout em tudo** (HTTP client, banco, fila, cache) — padrão 5 s, nunca infinito.
- **Retry** só para falha transitória (5xx, timeout, rede), com backoff exponencial + jitter e limite; nunca em operação não idempotente sem chave.
- **Circuit breaker** e **bulkhead** para dependências externas; fallback definido (cache, degradação graciosa).
- **Graceful shutdown**: parar de aceitar, terminar em andamento, fechar pool. Health: `/health` (vivo) e `/ready` (banco/fila ok).
- Config validada no boot (schema das env vars); processo falha rápido se faltar algo.

## Observabilidade
- **Logs estruturados JSON** (pino/structlog) com `request_id`, `user_id`, `tenant_id`, duração, nível correto; um log por requisição, sem log em loop.
- **Métricas RED** por rota (taxa, erros, duração p50/p95/p99) + saturação (pool, fila, memória) — Prometheus/OpenTelemetry.
- **Tracing distribuído** (OpenTelemetry) propagado para banco, fila e chamadas externas.
- Rastreador de erros adotado (ex.: Sentry) com contexto seguro (usuário, request, release); alerta em taxa de erro e p95 acima do SLO.

## Desempenho
- Metas do projeto por classe de consulta prevalecem; na ausência, usar p95 < 300 ms em leitura e < 1 s em escrita como metas iniciais a validar. Medir antes de otimizar.
- Cache quando justificado por medição, com TTL/invalidação e isolamento por empresa, recurso e permissões. Mudança de acesso não pode continuar servindo conteúdo indevido de cache.
- Teste de carga (k6) nos endpoints críticos antes de lançar; perfil de CPU/memória em suspeita.

## Checklist de endpoint
- [ ] Schema de entrada e saída; erro problem+json; códigos HTTP corretos
- [ ] Autenticação + autorização (inclusive dono/tenant) com testes 401/403/404
- [ ] Paginação por cursor, limite máximo, ordenação estável
- [ ] Transação onde precisa; idempotência em criação/cobrança
- [ ] Índices para as queries; sem N+1 (verificado com log de queries)
- [ ] Timeout/retry nas chamadas externas; trabalho lento na fila
- [ ] Log estruturado, métrica e trace; sem PII
- [ ] Testes: unit (regra), integração (banco real), contrato (OpenAPI)
- [ ] OpenAPI atualizado; cliente tipado regenerado
