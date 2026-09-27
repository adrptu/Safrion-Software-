import { fileURLToPath } from 'node:url';

import { defineConfig } from 'vitest/config';

// Integração com PostgreSQL real (ENG-034): contêiner fixado por digest na CI, ou servidor descartável indicado em
// SAFRION_TEST_DATABASE_URL. Cada arquivo cria e apaga o seu banco.
export default defineConfig({
  resolve: {
    alias: { '@safrion/domain': fileURLToPath(new URL('./packages/domain/src/index.ts', import.meta.url)) },
  },
  test: {
    include: ['packages/*/test/**/*.int.test.ts'],
    globalSetup: ['packages/db/test/global-setup.ts'],
    testTimeout: 60_000,
    hookTimeout: 300_000,
  },
});
