import { fileURLToPath } from 'node:url';

import { defineConfig } from 'vitest/config';

// ENG-032/033: domínio com cobertura ≥ 95 % em linhas, instruções, funções e desvios, conferida POR ARQUIVO
// (um arquivo novo sem teste não se esconde na média).
export default defineConfig({
  resolve: {
    alias: {
      '@safrion/domain': fileURLToPath(new URL('./packages/domain/src/index.ts', import.meta.url)),
      '@safrion/contracts': fileURLToPath(new URL('./packages/contracts/src/index.ts', import.meta.url)),
    },
  },
  test: {
    include: ['packages/*/test/**/*.test.ts', 'tools/dev/test/**/*.test.ts'],
    // Integração com banco real roda em pnpm run test:integration (vitest.integration.config.ts).
    exclude: ['**/node_modules/**', '**/*.int.test.ts'],
    // O limite pega travamento, não mede desempenho: testes que abrem processos e propriedades do fast-check passam
    // dos 5 s padrão numa máquina carregada ou num executor de CI com 2 núcleos.
    testTimeout: 30_000,
    coverage: {
      provider: 'v8',
      include: [
        'packages/domain/src/**/*.ts',
        'packages/contracts/src/**/*.ts',
        'packages/db/src/canonico.ts',
        'packages/db/src/resposta.ts',
      ],
      reporter: ['text', 'json-summary'],
      thresholds: { perFile: true, lines: 95, statements: 95, functions: 95, branches: 95 },
    },
  },
});
