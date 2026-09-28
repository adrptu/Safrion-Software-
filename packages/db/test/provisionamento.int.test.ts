// A1 da proposta da HML: provisionar os papéis com um administrador sem superusuário, igual ao postgres do Cloud SQL
// (CREATEROLE e CREATEDB, sem SUPERUSER, BYPASSRLS nem REPLICATION). A repetição falhava com 42501 (reprodução do
// Codex em work/hml-review/resultado-papeis.json), e uma falha na limpeza substituía a causa original (HML-A1-02,
// resultado-limpeza-a1-296a190.json). Os papéis deste arquivo têm nomes próprios: migrator e app_runtime da bateria não
// são tocados. O superusuário do servidor de teste só prepara, derruba conexões, observa pg_authid e limpa.
import { randomUUID } from 'node:crypto';

import pg from 'pg';
import { afterAll, beforeAll, describe, expect, inject, it } from 'vitest';

import { ErroPapeis, provisionarPapeis } from '../src/papeis.js';

const sufixo = randomUUID().replaceAll('-', '').slice(0, 12);
const nomes = { migrator: `mig_${sufixo}`, appRuntime: `app_${sufixo}` };
const administrador = `adm_${sufixo}`;
const senhaAdministrador = randomUUID();
let raiz: pg.Client;
let limitado: pg.Client;

const novasSenhas = () => ({ migrator: randomUUID(), appRuntime: randomUUID() });
const atributos = async (papel: string) =>
  (
    await raiz.query<Record<string, boolean>>(
      `SELECT rolsuper, rolbypassrls, rolreplication, rolcreaterole, rolcreatedb, rolcanlogin
         FROM pg_roles WHERE rolname = $1`,
      [papel],
    )
  ).rows[0];
const hashes = async () =>
  (
    await raiz.query<{ h: string | null }>(
      'SELECT rolpassword h FROM pg_authid WHERE rolname = ANY($1::text[]) ORDER BY rolname',
      [[nomes.migrator, nomes.appRuntime]],
    )
  ).rows.map((l) => l.h);
const falhaDe = (p: Promise<unknown>) =>
  p.then(
    () => undefined,
    (e: unknown) => e,
  );

async function conectarLimitado(): Promise<pg.Client> {
  const url = new URL(inject('urlAdmin'));
  url.username = administrador;
  url.password = senhaAdministrador;
  const cliente = new pg.Client({ connectionString: url.toString() });
  await cliente.connect();
  return cliente;
}

type Consulta = (...args: unknown[]) => Promise<unknown>;

/** Derruba a própria conexão no servidor, e espera ela sumir, logo antes de `gatilho` ser enviado: como uma queda de rede. */
async function derrubarAntesDe(cliente: pg.Client, gatilho: string): Promise<void> {
  const pid = (await cliente.query<{ pid: number }>('SELECT pg_backend_pid() AS pid')).rows[0]?.pid;
  cliente.on('error', () => undefined); // a queda é o cenário; o que importa é o que provisionarPapeis devolve
  const original = cliente.query.bind(cliente) as Consulta;
  let derrubado = false;
  (cliente as unknown as { query: Consulta }).query = async (...args) => {
    if (!derrubado && typeof args[0] === 'string' && args[0].startsWith(gatilho)) {
      derrubado = true;
      await raiz.query('SELECT pg_terminate_backend($1, 5000)', [pid]);
    }
    return original(...args);
  };
}

async function travaLivre(): Promise<boolean> {
  const r = await raiz.query<{ ok: boolean }>(
    "SELECT pg_try_advisory_lock(hashtext('safrion.papeis')) AS ok",
  );
  if (r.rows[0]?.ok) await raiz.query("SELECT pg_advisory_unlock(hashtext('safrion.papeis'))");
  return r.rows[0]?.ok === true;
}

beforeAll(async () => {
  raiz = new pg.Client({ connectionString: inject('urlAdmin') });
  await raiz.connect();
  await raiz.query(
    `CREATE ROLE ${administrador} LOGIN CREATEROLE CREATEDB NOSUPERUSER NOBYPASSRLS NOREPLICATION
       PASSWORD ${raiz.escapeLiteral(senhaAdministrador)}`,
  );
  limitado = await conectarLimitado();
});

afterAll(async () => {
  await limitado.end();
  for (const papel of [nomes.migrator, nomes.appRuntime, administrador]) {
    await raiz.query(`DROP ROLE IF EXISTS ${papel}`);
  }
  await raiz.end();
});

describe('provisionamento dos papéis por administrador sem superusuário (Cloud SQL)', () => {
  it('cria os papéis e repete a chamada sem erro, trocando a senha e mantendo os atributos proibidos desligados', async () => {
    const limpo = {
      rolsuper: false,
      rolbypassrls: false,
      rolreplication: false,
      rolcreaterole: false,
      rolcreatedb: false,
      rolcanlogin: true,
    };
    await provisionarPapeis(limitado, novasSenhas(), nomes);
    const antes = await hashes();
    await provisionarPapeis(limitado, novasSenhas(), nomes);
    expect(await hashes()).not.toEqual(antes);
    expect(await atributos(nomes.migrator)).toEqual(limpo);
    expect(await atributos(nomes.appRuntime)).toEqual(limpo);
  });

  it('papel existente com atributo que o administrador não pode tirar: falha sem efeito, nem as senhas mudam', async () => {
    // Independe da ordem: garante os papéis antes de sujar um deles.
    await provisionarPapeis(limitado, novasSenhas(), nomes);
    await raiz.query(`ALTER ROLE ${nomes.appRuntime} BYPASSRLS`);
    try {
      const antes = await hashes();
      const senhas = novasSenhas();
      const erro = await falhaDe(provisionarPapeis(limitado, senhas, nomes));
      expect(erro).toBeInstanceOf(ErroPapeis);
      expect(erro).toMatchObject({
        codigo: 'ATRIBUTO_PROIBIDO',
        detalhe: { efeito: 'nenhum', limpezaFalhou: [], problemas: [`${nomes.appRuntime}: BYPASSRLS`] },
      });
      expect((erro as Error).message).not.toContain(senhas.appRuntime);
      expect(await hashes()).toEqual(antes);
      expect((await limitado.query('SELECT 1')).rowCount).toBe(1);
    } finally {
      await raiz.query(`ALTER ROLE ${nomes.appRuntime} NOBYPASSRLS`);
    }
  });

  it('recusa do banco seguida de queda antes do ROLLBACK: a causa 42501 fica, a limpeza aparece à parte e a trava volta', async () => {
    await provisionarPapeis(limitado, novasSenhas(), nomes);
    // Papel existente elevado: o administrador limitado não pode alterá-lo (42501), como na reprodução do Codex.
    await raiz.query(`ALTER ROLE ${nomes.migrator} SUPERUSER`);
    const cliente = await conectarLimitado();
    try {
      const antes = await hashes();
      await derrubarAntesDe(cliente, 'ROLLBACK');
      const senhas = novasSenhas();
      const erro = await falhaDe(provisionarPapeis(cliente, senhas, nomes));
      expect(erro).toMatchObject({
        codigo: 'FALHA_NO_BANCO',
        detalhe: { efeito: 'nenhum', codigoPg: '42501', limpezaFalhou: ['ROLLBACK', 'DESBLOQUEIO'] },
      });
      expect((erro as Error).cause).toMatchObject({ code: '42501' });
      expect((erro as Error).message).not.toContain(senhas.migrator);
      expect(await hashes()).toEqual(antes);
      expect(await travaLivre()).toBe(true);
    } finally {
      await raiz.query(`ALTER ROLE ${nomes.migrator} NOSUPERUSER`);
      await cliente.end();
    }
  });

  it('queda no COMMIT: o resultado é incerto, nunca sucesso', async () => {
    const cliente = await conectarLimitado();
    try {
      await derrubarAntesDe(cliente, 'COMMIT');
      const erro = await falhaDe(provisionarPapeis(cliente, novasSenhas(), nomes));
      expect(erro).toMatchObject({
        codigo: 'FALHA_NO_BANCO',
        detalhe: { efeito: 'incerto', limpezaFalhou: ['DESBLOQUEIO'] },
      });
      expect(await travaLivre()).toBe(true);
    } finally {
      await cliente.end();
    }
  });

  it('queda só na liberação da trava: papéis gravados e a falha de limpeza informada', async () => {
    const cliente = await conectarLimitado();
    try {
      const antes = await hashes();
      await derrubarAntesDe(cliente, 'SELECT pg_advisory_unlock');
      const erro = await falhaDe(provisionarPapeis(cliente, novasSenhas(), nomes));
      expect(erro).toMatchObject({
        codigo: 'LIMPEZA_FALHOU',
        detalhe: { efeito: 'gravado', limpezaFalhou: ['DESBLOQUEIO'] },
      });
      expect(await hashes()).not.toEqual(antes);
      expect(await travaLivre()).toBe(true);
    } finally {
      await cliente.end();
    }
  });
});
