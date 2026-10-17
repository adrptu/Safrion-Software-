import { defineConfig } from 'vitest/config';

// Suíte unitária + integração. E2E fica no Playwright.
export default defineConfig({
  test: {
    globals: false,
    environment: 'node', // 'jsdom' em projetos React (ou usar `// @vitest-environment jsdom` por arquivo)
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    exclude: ['node_modules', 'dist', 'e2e/**'],
    setupFiles: ['./src/test/setup.ts'],
    restoreMocks: true,
    clearMocks: true,
    testTimeout: 10_000,
    // Integração com banco real: uma instância por worker evita colisão de dados
    poolOptions: { threads: { singleThread: false } },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov', 'json-summary'],
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/**/*.{test,spec,stories}.{ts,tsx}', 'src/test/**', 'src/**/*.d.ts', 'src/**/index.ts'],
      thresholds: {
        lines: 80,
        branches: 80,
        functions: 80,
        statements: 80,
        // Núcleo de domínio: 100 %
        'src/domain/**': { lines: 100, branches: 100, functions: 100, statements: 100 },
      },
    },
    reporters: process.env.CI ? ['default', 'junit'] : ['default'],
    outputFile: { junit: './reports/junit.xml' },
  },
});
