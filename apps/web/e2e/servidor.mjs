// Servidor dos testes ponta a ponta (F0-c B2): prepara um banco descartável em modo DEV e sobe o `next start` já
// construído. Roda como webServer do Playwright porque o setup global dele só começa depois do servidor.
// Precisa de SAFRION_TEST_DATABASE_URL com um administrador de um PostgreSQL descartável, como a integração.
import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { existsSync } from 'node:fs';
import { setTimeout as esperar } from 'node:timers/promises';
import { fileURLToPath } from 'node:url';

import {
  aplicarMigracoes,
  definirIdentidadeAmbiente,
  provisionarPapeis,
  restaurarDemonstracao,
} from '@safrion/db';
import pg from 'pg';

const PREFIXO = 'safrion_e2e_';
const porta = process.env['SAFRION_E2E_PORTA'] ?? '3200';
const admin = process.env['SAFRION_TEST_DATABASE_URL'];
const app = fileURLToPath(new URL('..', import.meta.url));
if (!admin) throw new Error('Defina SAFRION_TEST_DATABASE_URL (administrador de um PostgreSQL descartável).');
if (!existsSync(new URL('../.next/BUILD_ID', import.meta.url))) throw new Error('Rode pnpm run build antes.');

const senhas = { migrator: randomUUID(), appRuntime: randomUUID() };
const banco = `${PREFIXO}${randomUUID().replaceAll('-', '').slice(0, 12)}`;
const url = (papel, senha) => {
  const u = new URL(admin);
  u.username = papel;
  u.password = senha;
  u.pathname = `/${banco}`;
  return u.toString();
};

const raiz = new pg.Client({ connectionString: admin });
await raiz.connect();
try {
  // Sobras de execuções interrompidas: só bancos com o prefixo deste script, neste servidor descartável.
  const velhos = await raiz.query('SELECT datname FROM pg_database WHERE datname LIKE $1', [`${PREFIXO}%`]);
  for (const { datname } of velhos.rows)
    await raiz.query(`DROP DATABASE IF EXISTS ${pg.escapeIdentifier(datname)}`);
  await provisionarPapeis(raiz, senhas);
  await raiz.query(`CREATE DATABASE ${pg.escapeIdentifier(banco)} OWNER migrator`);
} finally {
  await raiz.end();
}

const migrator = new pg.Client({ connectionString: url('migrator', senhas.migrator) });
await migrator.connect();
try {
  await aplicarMigracoes(migrator);
  await definirIdentidadeAmbiente(migrator, 'dev');
} finally {
  await migrator.end();
}
const pool = new pg.Pool({ connectionString: url('app_runtime', senhas.appRuntime), max: 2 });
try {
  await restaurarDemonstracao(pool, { confirmar: 'dev', ambienteDoProcesso: 'dev' });
} finally {
  await pool.end();
}

const next = spawn(
  process.execPath,
  [fileURLToPath(import.meta.resolve('next/dist/bin/next')), 'start', '-p', porta],
  {
    cwd: app,
    stdio: 'inherit',
    env: {
      PATH: process.env['PATH'],
      NODE_ENV: 'production',
      DATABASE_URL: url('app_runtime', senhas.appRuntime),
      SAFRION_ORIGEM: `http://localhost:${porta}`,
      SAFRION_AMBIENTE: 'dev',
      SAFRION_VERSAO: '0.0.0-e2e',
      SAFRION_COMMIT: 'e2e',
      NEXT_TELEMETRY_DISABLED: '1',
    },
  },
);

let saindo = false;
async function encerrar(codigo) {
  if (saindo) return;
  saindo = true;
  next.kill('SIGTERM');
  await esperar(500);
  const fim = new pg.Client({ connectionString: admin });
  await fim.connect();
  try {
    await fim.query(`DROP DATABASE IF EXISTS ${pg.escapeIdentifier(banco)} WITH (FORCE)`);
  } finally {
    await fim.end();
  }
  process.exit(codigo);
}
process.on('SIGTERM', () => void encerrar(0));
process.on('SIGINT', () => void encerrar(0));
next.on('exit', (codigo) => void encerrar(codigo ?? 1));
