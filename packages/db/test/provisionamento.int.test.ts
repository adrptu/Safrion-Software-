// A1 da proposta da HML: provisionar os papéis com um administrador sem superusuário, igual ao postgres do Cloud SQL
// (CREATEROLE e CREATEDB, sem SUPERUSER, BYPASSRLS nem REPLICATION). A repetição falhava com 42501 (reprodução do
// Codex em work/hml-review/resultado-papeis.json). Os papéis deste arquivo têm nomes próprios: migrator e app_runtime da
// bateria não são tocados. O superusuário do servidor de teste só prepara, observa pg_authid e limpa.
import { randomUUID } from 'node:crypto';

import pg from 'pg';
import { afterAll, beforeAll, describe, expect, inject, it } from 'vitest';

import { ErroPapeis, provisionarPapeis } from '../src/papeis.js';

const sufixo = randomUUID().replaceAll('-', '').slice(0, 12);
const nomes = { migrator: `mig_${sufixo}`, appRuntime: `app_${sufixo}` };
const administrador = `adm_${sufixo}`;
let raiz: pg.Client;
let limitado: pg.Client;

const atributos = async (papel: string) =>
  (
    await raiz.query<Record<string, boolean>>(
      `SELECT rolsuper, rolbypassrls, rolreplication, rolcreaterole, rolcreatedb, rolcanlogin
         FROM pg_roles WHERE rolname = $1`,
      [papel],
    )
  ).rows[0];
const hashSenha = async (papel: string) =>
  (await raiz.query<{ h: string | null }>('SELECT rolpassword h FROM pg_authid WHERE rolname = $1', [papel]))
    .rows[0]?.h;

beforeAll(async () => {
  raiz = new pg.Client({ connectionString: inject('urlAdmin') });
  await raiz.connect();
  const senha = randomUUID();
  await raiz.query(
    `CREATE ROLE ${administrador} LOGIN CREATEROLE CREATEDB NOSUPERUSER NOBYPASSRLS NOREPLICATION
       PASSWORD ${raiz.escapeLiteral(senha)}`,
  );
  const url = new URL(inject('urlAdmin'));
  url.username = administrador;
  url.password = senha;
  limitado = new pg.Client({ connectionString: url.toString() });
  await limitado.connect();
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
    await provisionarPapeis(limitado, { migrator: randomUUID(), appRuntime: randomUUID() }, nomes);
    const antes = await hashSenha(nomes.appRuntime);
    await provisionarPapeis(limitado, { migrator: randomUUID(), appRuntime: randomUUID() }, nomes);
    expect(await hashSenha(nomes.appRuntime)).not.toBe(antes);
    expect(await atributos(nomes.migrator)).toEqual(limpo);
    expect(await atributos(nomes.appRuntime)).toEqual(limpo);
  });

  it('papel existente com atributo que o administrador não pode tirar: falha sem efeito, nem as senhas mudam', async () => {
    // Independe da ordem: garante os papéis antes de sujar um deles.
    await provisionarPapeis(limitado, { migrator: randomUUID(), appRuntime: randomUUID() }, nomes);
    await raiz.query(`ALTER ROLE ${nomes.appRuntime} BYPASSRLS`);
    try {
      const antes = [await hashSenha(nomes.migrator), await hashSenha(nomes.appRuntime)];
      const senhaNova = randomUUID();
      const erro: unknown = await provisionarPapeis(
        limitado,
        { migrator: randomUUID(), appRuntime: senhaNova },
        nomes,
      ).then(
        () => undefined,
        (e: unknown) => e,
      );
      expect(erro).toBeInstanceOf(ErroPapeis);
      expect((erro as ErroPapeis).problemas).toEqual([`${nomes.appRuntime}: BYPASSRLS`]);
      expect((erro as ErroPapeis).message).not.toContain(senhaNova);
      expect([await hashSenha(nomes.migrator), await hashSenha(nomes.appRuntime)]).toEqual(antes);
      expect((await limitado.query<{ t: string }>('SELECT now()::text t')).rows).toHaveLength(1);
    } finally {
      await raiz.query(`ALTER ROLE ${nomes.appRuntime} NOBYPASSRLS`);
    }
  });
});
