// Preparo do banco de um ambiente (artefato de HML): papéis, banco com dono migrator, migrações e identidade. Usa as
// mesmas senhas da bateria (os papéis padrão são compartilhados pelos outros arquivos), bancos com nome próprio e um
// administrador sem superusuário, como o postgres do Cloud SQL. O superusuário do servidor de teste só prepara e limpa.
import { readdir } from 'node:fs/promises';
import { randomUUID } from 'node:crypto';

import pg from 'pg';
import { afterAll, beforeAll, describe, expect, inject, it } from 'vitest';

import { ErroAmbiente, lerIdentidadeAmbiente } from '../src/ambiente.js';
import { executarCli } from '../src/cli/preparar-banco.js';
import { PASTA_MIGRACOES } from '../src/migrar.js';
import { conexaoDoMigrator, ErroPreparo, prepararBanco, validarOpcoes } from '../src/preparo.js';

const sufixo = randomUUID().replaceAll('-', '').slice(0, 10);
const bancos = {
  hml: `prep_hml_${sufixo}`,
  outro: `prep_outro_${sufixo}`,
  limitado: `prep_lim_${sufixo}`,
  cli: `prep_cli_${sufixo}`,
};
const administrador = `adm_prep_${sufixo}`;
const senhaAdministrador = randomUUID();
const senhas = () => ({ migrator: inject('senhaMigrator'), appRuntime: inject('senhaApp') });
let raiz: pg.Client;
let migracoes: string[];

const falhaDe = (p: Promise<unknown>) =>
  p.then(
    () => undefined,
    (e: unknown) => e,
  );

async function conectar(usuario?: string, senha?: string): Promise<pg.Client> {
  const url = new URL(inject('urlAdmin'));
  if (usuario) {
    url.username = usuario;
    url.password = senha ?? '';
  }
  const c = new pg.Client({ connectionString: url.toString() });
  await c.connect();
  return c;
}

async function noBanco<T>(banco: string, f: (c: pg.Client) => Promise<T>): Promise<T> {
  const url = new URL(inject('urlAdmin'));
  url.pathname = `/${banco}`;
  const c = new pg.Client({ connectionString: url.toString() });
  await c.connect();
  try {
    return await f(c);
  } finally {
    await c.end();
  }
}

beforeAll(async () => {
  raiz = await conectar();
  migracoes = (await readdir(PASTA_MIGRACOES)).filter((n) => n.endsWith('.sql')).sort();
});
afterAll(async () => {
  for (const b of Object.values(bancos)) await raiz.query(`DROP DATABASE IF EXISTS ${b}`);
  await raiz.query(`DROP OWNED BY ${administrador}`).catch(() => undefined);
  await raiz.query(`DROP ROLE IF EXISTS ${administrador}`);
  await raiz.end();
});

describe('opções: recusadas antes de conectar', () => {
  const base = {
    ambiente: 'hml',
    banco: 'safrion_hml',
    senhas: { migrator: 'x'.repeat(16), appRuntime: 'y'.repeat(16) },
  };

  it('produção fica fora da F0; ambiente, banco e senha fora do formato são recusados', () => {
    expect(validarOpcoes(base)).toBe('hml');
    expect(validarOpcoes({ ...base, ambiente: 'dev' })).toBe('dev');
    const codigo = (o: typeof base) => {
      try {
        validarOpcoes(o);
        return 'aceito';
      } catch (e) {
        return e instanceof ErroPreparo ? e.codigo : 'outro';
      }
    };
    expect(codigo({ ...base, ambiente: 'prod' })).toBe('AMBIENTE_PROIBIDO');
    for (const ambiente of ['', 'HML', 'homologacao'])
      expect(codigo({ ...base, ambiente }), ambiente).toBe('OPCAO_INVALIDA');
    for (const banco of [
      'postgres',
      'template1',
      'Safrion',
      '1banco',
      'a-b',
      `a${'b'.repeat(63)}`,
      'x; DROP',
    ])
      expect(codigo({ ...base, banco }), banco).toBe('OPCAO_INVALIDA');
    expect(codigo({ ...base, senhas: { ...base.senhas, migrator: 'curta' } })).toBe('OPCAO_INVALIDA');
  });

  it('produção não chega a consultar o servidor', async () => {
    const consultas: unknown[] = [];
    const falso = {
      query: (...a: unknown[]) => (consultas.push(a), Promise.resolve({ rows: [] })),
    } as unknown as pg.Client;
    const erro = await falhaDe(prepararBanco(falso, { ...base, ambiente: 'prod' }));
    expect(erro).toMatchObject({ codigo: 'AMBIENTE_PROIBIDO' });
    expect(consultas).toEqual([]);
  });

  it('a conexão do migrator herda servidor, porta e TLS do administrador, inclusive por socket', () => {
    const tcp = new pg.Client({
      connectionString: 'postgresql://adm:s@10.0.0.5:5433/postgres?sslmode=require',
    });
    expect(conexaoDoMigrator(tcp, 'safrion_hml', 'senha')).toMatchObject({
      host: '10.0.0.5',
      port: 5433,
      database: 'safrion_hml',
      user: 'migrator',
      password: 'senha',
    });
    expect(conexaoDoMigrator(tcp, 'b', 's').ssl).toBeTruthy();
    const socket = new pg.Client({ connectionString: 'postgresql://adm:s@/postgres?host=/cloudsql/p:r:i' });
    expect(conexaoDoMigrator(socket, 'b', 's')).toMatchObject({
      host: '/cloudsql/p:r:i',
      port: 5432,
      database: 'b',
    });
  });
});

describe('preparo com banco real', () => {
  it('banco novo: cria com dono migrator, aplica todas as migrações e grava a identidade', async () => {
    const r = await prepararBanco(raiz, { ambiente: 'hml', banco: bancos.hml, senhas: senhas() });
    expect(r).toEqual({
      ambiente: 'hml',
      banco: 'criado',
      migracoes: { aplicadas: migracoes, jaAplicadas: [] },
      identidade: 'definida',
    });
    const dono = await raiz.query<{ d: string }>(
      'SELECT pg_get_userbyid(datdba) d FROM pg_database WHERE datname = $1',
      [bancos.hml],
    );
    expect(dono.rows[0]?.d).toBe('migrator');
    expect(await noBanco(bancos.hml, (c) => lerIdentidadeAmbiente(c))).toBe('hml');
  });

  it('repetir não muda nada', async () => {
    expect(await prepararBanco(raiz, { ambiente: 'hml', banco: bancos.hml, senhas: senhas() })).toEqual({
      ambiente: 'hml',
      banco: 'existente',
      migracoes: { aplicadas: [], jaAplicadas: migracoes },
      identidade: 'mantida',
    });
  });

  it('identidade divergente para antes das migrações e não troca o ambiente', async () => {
    const erro = await falhaDe(prepararBanco(raiz, { ambiente: 'dev', banco: bancos.hml, senhas: senhas() }));
    expect(erro).toBeInstanceOf(ErroAmbiente);
    expect(erro).toMatchObject({ codigo: 'IDENTIDADE_DIVERGENTE' });
    expect(await noBanco(bancos.hml, (c) => lerIdentidadeAmbiente(c))).toBe('hml');
  });

  it('banco existente de outro dono é recusado sem migrar nada', async () => {
    await raiz.query(`CREATE DATABASE ${bancos.outro}`);
    const erro = await falhaDe(
      prepararBanco(raiz, { ambiente: 'hml', banco: bancos.outro, senhas: senhas() }),
    );
    expect(erro).toMatchObject({ codigo: 'BANCO_DE_OUTRO_DONO' });
    const esquema = await noBanco(bancos.outro, (c) =>
      c.query("SELECT 1 FROM pg_namespace WHERE nspname IN ('app', 'migracao')"),
    );
    expect(esquema.rowCount).toBe(0);
  });

  it('administrador sem superusuário (Cloud SQL) cria o banco com dono migrator e herança desligada', async () => {
    await raiz.query(
      `CREATE ROLE ${administrador} LOGIN CREATEROLE CREATEDB NOSUPERUSER NOBYPASSRLS NOREPLICATION PASSWORD '${senhaAdministrador}'`,
    );
    // Como no Cloud SQL, onde o próprio administrador criou os papéis e por isso os administra.
    await raiz.query(
      `GRANT migrator, app_runtime, app_sessao TO ${administrador} WITH ADMIN TRUE, INHERIT FALSE, SET FALSE`,
    );
    const limitado = await conectar(administrador, senhaAdministrador);
    try {
      const r = await prepararBanco(limitado, { ambiente: 'hml', banco: bancos.limitado, senhas: senhas() });
      expect(r).toMatchObject({ banco: 'criado', identidade: 'definida' });
    } finally {
      await limitado.end();
    }
    const filiacao = await raiz.query<{ inherit_option: boolean; set_option: boolean }>(
      `SELECT m.inherit_option, m.set_option FROM pg_auth_members m
         JOIN pg_roles r ON r.oid = m.roleid JOIN pg_roles u ON u.oid = m.member
        WHERE r.rolname = 'migrator' AND u.rolname = $1 AND m.set_option`,
      [administrador],
    );
    expect(filiacao.rows).toEqual([{ inherit_option: false, set_option: true }]);
  });
});

describe('comando preparar-banco', () => {
  const linhas: string[] = [];
  const env = () => ({
    SAFRION_ADMIN_URL: inject('urlAdmin'),
    SAFRION_SENHA_MIGRATOR: inject('senhaMigrator'),
    SAFRION_SENHA_APP_RUNTIME: inject('senhaApp'),
  });
  const rodar = async (args: string[], e: Record<string, string | undefined>) => {
    linhas.length = 0;
    return executarCli(args, e, (l) => linhas.push(l));
  };

  it('uso incorreto: 2, sem tocar no servidor', async () => {
    expect(await rodar(['--ambiente', 'hml'], env())).toBe(2);
    expect(
      await rodar(['--ambiente', 'hml', '--banco', bancos.cli], {
        ...env(),
        SAFRION_SENHA_APP_RUNTIME: undefined,
      }),
    ).toBe(2);
    expect(await rodar(['--desconhecida'], env())).toBe(2);
    expect(linhas[0]).toContain('Uso:');
  });

  it('preparado: 0 com o resumo; recusado: 1 com o código', async () => {
    expect(await rodar(['--', '--ambiente', 'hml', '--banco', bancos.cli], env())).toBe(0);
    expect(JSON.parse(linhas[0] ?? '{}')).toEqual({
      resultado: 'preparado',
      ambiente: 'hml',
      banco: 'criado',
      migracoes_aplicadas: migracoes,
      migracoes_ja_aplicadas: 0,
      identidade: 'definida',
    });
    expect(await rodar(['--ambiente', 'prod', '--banco', bancos.cli], env())).toBe(1);
    expect(JSON.parse(linhas[0] ?? '{}')).toMatchObject({
      resultado: 'recusado',
      codigo: 'AMBIENTE_PROIBIDO',
    });
    expect(await rodar(['--ambiente', 'dev', '--banco', bancos.cli], env())).toBe(1);
    expect(JSON.parse(linhas[0] ?? '{}')).toMatchObject({
      resultado: 'recusado',
      codigo: 'IDENTIDADE_DIVERGENTE',
    });
  });

  it('falha de infraestrutura: 3 só com códigos, sem senha, host ou mensagem do driver', async () => {
    const url = new URL(inject('urlAdmin'));
    url.password = 'SenhaQueNaoPodeVazar123';
    url.port = '1';
    expect(
      await rodar(['--ambiente', 'hml', '--banco', bancos.cli], {
        ...env(),
        SAFRION_ADMIN_URL: url.toString(),
      }),
    ).toBe(3);
    const saida = linhas.join('\n');
    expect(JSON.parse(linhas[0] ?? '{}')).toMatchObject({
      resultado: 'falha',
      codigo: 'FALHA_INFRAESTRUTURA',
    });
    for (const segredo of [
      'SenhaQueNaoPodeVazar123',
      inject('senhaMigrator'),
      inject('senhaApp'),
      url.hostname,
    ])
      expect(saida).not.toContain(segredo);
  });
});
