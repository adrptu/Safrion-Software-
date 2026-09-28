import { defineConfig, devices } from '@playwright/test';

const porta = process.env['SAFRION_E2E_PORTA'] ?? '3200';

/**
 * Ponta a ponta da F0-c (B2): jornadas por papel, teclado, celular, CSP e acessibilidade com axe. Chrome do sistema
 * (channel), sem baixar navegador. O servidor sobe pelo e2e/servidor.mjs, que prepara o banco de DEV descartável.
 */
export default defineConfig({
  testDir: 'e2e',
  fullyParallel: false,
  workers: 1,
  forbidOnly: Boolean(process.env['CI']),
  retries: 0,
  reporter: [['list']],
  use: {
    baseURL: `http://localhost:${porta}`,
    channel: 'chrome',
    locale: 'pt-BR',
    timezoneId: 'America/Sao_Paulo',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], channel: 'chrome' }, testIgnore: /celular/ },
    { name: 'celular', use: { ...devices['Pixel 7'], channel: 'chrome' }, testMatch: /celular/ },
  ],
  webServer: {
    command: 'node e2e/servidor.mjs',
    url: `http://localhost:${porta}/saude`,
    timeout: 120_000,
    reuseExistingServer: false,
    stdout: 'pipe',
    gracefulShutdown: { signal: 'SIGTERM', timeout: 10_000 },
  },
});
