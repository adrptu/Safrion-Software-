import { defineConfig, devices } from '@playwright/test';

const PORT = Number(process.env.PORT ?? 3000);
const baseURL = process.env.BASE_URL ?? `http://localhost:${PORT}`;

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI, // falha o CI se alguém deixou test.only
  retries: 0, // flaky se corrige, não se repete
  workers: process.env.CI ? 4 : undefined,
  timeout: 30_000,
  expect: { timeout: 5_000 },
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }], ['junit', { outputFile: 'reports/e2e.xml' }]] : [['list'], ['html', { open: 'on-failure' }]],
  use: {
    baseURL,
    locale: 'pt-BR',
    timezoneId: 'America/Sao_Paulo',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ }, // login uma vez, reutiliza storageState
    { name: 'chromium', use: { ...devices['Desktop Chrome'], storageState: 'e2e/.auth/user.json' }, dependencies: ['setup'] },
    { name: 'mobile', use: { ...devices['Pixel 7'], storageState: 'e2e/.auth/user.json' }, dependencies: ['setup'] },
  ],
  webServer: {
    command: process.env.CI ? 'npm run start' : 'npm run dev',
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
