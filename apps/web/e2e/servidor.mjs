// Servidor dos testes ponta a ponta (F0-c B2): prepara um banco descartável em modo DEV pelo mesmo prepararBanco do
// comando de HML e sobe o `next start` já construído. Com SAFRION_E2E_STANDALONE=<pasta>, sobe em vez disso o
// server.js do build standalone copiado para essa pasta, como na imagem de implantação.
// Roda como webServer do Playwright porque o setup global dele só começa depois do servidor.
// Precisa de SAFRION_TEST_DATABASE_URL com um administrador de um PostgreSQL descartável, como a integração.
//
// Isolamento (HML-ISO, e2e/isolamento.spec.ts): a demonstração é restaurada duas vezes. A geração 1 fica como a
// organização B, porque restaurar nunca apaga; a geração 2 é a A, a única que o login de DEV alcança. B ganha um vínculo
// de identidade de teste e uma sessão pelas funções reais de login (continuação → sessão). IDs, nome do banco e o token
// de B vão para um JSON efêmero, criado com exclusividade (600) e apagado no fim. Sessão de fixture prova autorização
// HTTP, não autenticação OIDC.
import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { closeSync, constants, existsSync, openSync, rmSync, writeSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { setTimeout as esperar } from 'node:timers/promises';
import { fileURLToPath } from 'node:url';

import {
  abrirContinuacao,
  concluirContinuacao,
  emOrganizacao,
  prepararBanco,
  restaurarDemonstracao,
} from '@safrion/db';
import pg from 'pg';

const PREFIXO = 'safrion_e2e_';
const porta = process.env['SAFRION_E2E_PORTA'] ?? '3200';
const admin = process.env['SAFRION_TEST_DATABASE_URL'];
const app = fileURLToPath(new URL('..', import.meta.url));
const standalone = process.env['SAFRION_E2E_STANDALONE'];
if (!admin) throw new Error('Defina SAFRION_TEST_DATABASE_URL (administrador de um PostgreSQL descartável).');
if (!existsSync(new URL('../.next/BUILD_ID', import.meta.url))) throw new Error('Rode pnpm run build antes.');
if (standalone && !existsSync(`${standalone}/apps/web/server.js`))
  throw new Error('SAFRION_E2E_STANDALONE precisa conter apps/web/server.js do build standalone.');

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
  await prepararBanco(raiz, { ambiente: 'dev', banco, senhas });
} finally {
  await raiz.end();
}
// Mesmo caminho lido pelo isolamento.spec.ts.
const FIXTURE = join(tmpdir(), `safrion-e2e-isolamento-${porta}.json`);
const IDENTIDADE_B = { issuer: 'urn:safrion:e2e', subject: 'organizacao-b-almoxarife' };
let fixtureCriada = false;

/** Cria o arquivo só se ele não existir (nem como link) e só para o dono; nunca substitui nada. */
function gravarFixture(dados) {
  let fd;
  try {
    fd = openSync(
      FIXTURE,
      constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL | (constants.O_NOFOLLOW ?? 0),
      0o600,
    );
  } catch (e) {
    if (e?.code === 'EEXIST')
      throw new Error(`${FIXTURE} já existe. Apague-o se nenhum teste ponta a ponta estiver rodando.`, {
        cause: e,
      });
    throw e;
  }
  fixtureCriada = true;
  try {
    writeSync(fd, JSON.stringify(dados));
  } finally {
    closeSync(fd);
  }
}

function apagarFixture() {
  if (fixtureCriada) rmSync(FIXTURE, { force: true });
  fixtureCriada = false;
}

/** Produto e local de um lote, lidos na própria organização. */
async function doLote(pool, organizationId, loteId) {
  const r = await emOrganizacao(pool, organizationId, (c) =>
    c.query(
      `SELECT l.product_id, (SELECT s.id FROM app.stock_location s ORDER BY s.id LIMIT 1) AS local_id
         FROM app.lot l WHERE l.id = $1`,
      [loteId],
    ),
  );
  const linha = r.rows[0];
  if (!linha?.product_id || !linha.local_id)
    throw new Error('Demonstração sem produto ou local para o lote.');
  return { organizationId, loteId, produtoId: linha.product_id, localId: linha.local_id };
}

const pool = new pg.Pool({ connectionString: url('app_runtime', senhas.appRuntime), max: 2 });
const migrator = new pg.Pool({ connectionString: url('migrator', senhas.migrator), max: 1 });
try {
  const b = await restaurarDemonstracao(pool, { confirmar: 'dev', ambienteDoProcesso: 'dev' });
  const a = await restaurarDemonstracao(pool, { confirmar: 'dev', ambienteDoProcesso: 'dev' });
  const almoxarifeB = b.usuarios.find((u) => u.papel === 'almoxarife')?.usuarioId;
  await emOrganizacao(migrator, b.organizationId, (c) =>
    c.query(
      'INSERT INTO app.identity_link (issuer, subject, organization_id, user_id) VALUES ($1, $2, $3, $4)',
      [IDENTIDADE_B.issuer, IDENTIDADE_B.subject, b.organizationId, almoxarifeB],
    ),
  );
  const continuacao = await abrirContinuacao(pool, IDENTIDADE_B, '/estoque');
  const sessaoB = await concluirContinuacao(pool, continuacao.ticket, {
    organizationId: b.organizationId,
    papel: 'almoxarife',
  });
  if (!sessaoB.ok) throw new Error(`Sessão de B não criada: ${sessaoB.codigo}.`);
  gravarFixture({
    banco,
    a: await doLote(pool, a.organizationId, a.loteId),
    b: { ...(await doLote(pool, b.organizationId, b.loteId)), sessao: sessaoB.sessao.token },
  });
} catch (e) {
  apagarFixture();
  throw e;
} finally {
  await pool.end();
  await migrator.end();
}

const comando = standalone
  ? [`${standalone}/apps/web/server.js`]
  : [fileURLToPath(import.meta.resolve('next/dist/bin/next')), 'start', '-p', porta];
const next = spawn(process.execPath, comando, {
  cwd: standalone ? `${standalone}/apps/web` : app,
  stdio: 'inherit',
  env: {
    PATH: process.env['PATH'],
    NODE_ENV: 'production',
    PORT: porta,
    HOSTNAME: 'localhost',
    DATABASE_URL: url('app_runtime', senhas.appRuntime),
    SAFRION_ORIGEM: `http://localhost:${porta}`,
    SAFRION_AMBIENTE: 'dev',
    SAFRION_VERSAO: '0.0.0-e2e',
    SAFRION_COMMIT: 'e2e',
    NEXT_TELEMETRY_DISABLED: '1',
  },
});

let saindo = false;
async function encerrar(codigo) {
  if (saindo) return;
  saindo = true;
  apagarFixture();
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
