# Estrutura de backend modular (TypeScript — equivalente em Python/Go)

```
src/
├── main.ts                    # boot: valida config, conecta, registra módulos, graceful shutdown
├── config/
│   └── env.ts                 # schema (zod) das variáveis; falha rápido se faltar
├── shared/                    # sem regra de negócio
│   ├── http/                  # servidor, plugins (auth, cors, helmet, rate-limit), error handler problem+json
│   ├── db/                    # cliente/ORM, transação, migrações
│   ├── queue/                 # fila + workers + dead-letter
│   ├── cache/
│   ├── observability/         # logger, métricas, tracing, sentry
│   └── errors.ts              # AppError, NotFoundError, ForbiddenError, ConflictError, ValidationError
├── modules/
│   ├── pedidos/
│   │   ├── pedidos.routes.ts      # HTTP: schema de entrada/saída, auth, chama o service
│   │   ├── pedidos.service.ts     # regras de negócio, transações, emite eventos
│   │   ├── pedidos.repository.ts  # SQL/ORM; único lugar que toca a tabela `pedidos`
│   │   ├── pedidos.schema.ts      # zod: DTOs e tipos derivados
│   │   ├── pedidos.events.ts      # PedidoCriado, PedidoCancelado
│   │   ├── pedidos.policy.ts      # quem pode o quê
│   │   └── pedidos.test.ts        # unit (service) + integração (routes + banco real)
│   ├── clientes/
│   └── faturamento/           # consome eventos de pedidos; nunca lê a tabela `pedidos`
├── jobs/                      # cron e workers (importam services dos módulos)
└── test/
    ├── setup.ts               # Testcontainers Postgres, migrações, truncate por teste
    └── factories/             # buildPedido(), buildCliente()

migrations/                    # versionadas, reversíveis, no repositório
docs/adr/                      # decisões
openapi.json                   # gerado no build a partir dos schemas
```

## Erro padrão (problem+json)

```ts
// shared/errors.ts
export class AppError extends Error {
  constructor(public readonly status: number, public readonly title: string, message: string, public readonly errors?: { field: string; message: string }[]) {
    super(message);
  }
}
export class NotFoundError extends AppError { constructor(what = 'Recurso') { super(404, 'Não encontrado', `${what} não encontrado`); } }
export class ForbiddenError extends AppError { constructor() { super(403, 'Sem permissão', 'Você não tem permissão para esta ação'); } }
export class ConflictError extends AppError { constructor(msg: string) { super(409, 'Conflito', msg); } }

// shared/http/error-handler.ts — único lugar que converte erro em resposta
app.setErrorHandler((err, req, reply) => {
  if (err instanceof AppError) {
    return reply.code(err.status).type('application/problem+json')
      .send({ type: 'about:blank', title: err.title, status: err.status, detail: err.message, instance: req.url, errors: err.errors });
  }
  if (err.validation) {
    return reply.code(400).type('application/problem+json')
      .send({ title: 'Dados inválidos', status: 400, detail: 'Corrija os campos indicados', instance: req.url, errors: mapValidation(err.validation) });
  }
  req.log.error({ err, requestId: req.id }, 'unhandled');
  Sentry.captureException(err);
  return reply.code(500).type('application/problem+json')
    .send({ title: 'Erro interno', status: 500, detail: 'Algo deu errado. Tente novamente; se persistir, informe o código ' + req.id, instance: req.url });
});
```

## Regras de dependência entre pastas
- `modules/*` → `shared/*` ✔ · `shared/*` → `modules/*` ✘
- `modules/a` → `modules/b` só via `b.service` (público) ou eventos; nunca `b.repository`
- `routes` → `service` → `repository`; nunca pular camada; `service` não conhece HTTP
