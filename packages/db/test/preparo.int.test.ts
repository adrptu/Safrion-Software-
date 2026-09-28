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
import {
  conexaoDoMigrator,
  ErroPreparo,
  prepararBanco,
  validarOpcoes,
  type OpcoesPreparo,
} from '../src/preparo.js';

const sufixo = randomUUID().replaceAll('-', '').slice(0, 10);
const bancos = {
  hml: `prep_hml_${sufixo}`,
  outro: `prep_outro_${sufixo}`,
  limitado: `prep_lim_${sufixo}`,
  cli: `prep_cli_${sufixo}`,
  semCredencial: `prep_semcred_${sufixo}`,
  vazio: `prep_vazio_${sufixo}`,
};
const administrador = `adm_prep_${sufixo}`;
const semSet = `adm_semset_${sufixo}`;
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
  for (const papel of [administrador, semSet]) {
    await raiz.query(`DROP OWNED BY ${papel}`).catch(() => undefined);
    await raiz.query(`DROP ROLE IF EXISTS ${papel}`);
  }
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

describe('nada muda antes de conferir identidade e senhas (HML-PREP-01/03)', () => {
  const novas = () => ({ migrator: randomUUID(), appRuntime: randomUUID() });
  const ALTERA = /^(ALTER|CREATE|GRANT|REVOKE|DROP|INSERT|UPDATE|DELETE|TRUNCATE|COMMENT|SECURITY)\b/i;

  /**
   * "Nada mudou" é conferido pelo que a própria chamada enviou ao servidor, pelo administrador e pelas conexões que
   * abriu, e não pelo estado global dos papéis: outros arquivos da bateria rodam em paralelo e podem regravar as mesmas
   * senhas. Só as duas primeiras palavras de cada comando são guardadas, para nenhuma senha ir ao relatório.
   */
  function anotado(c: pg.Client, comandos: string[]): pg.Client {
    const consultar: (...a: unknown[]) => unknown = c.query.bind(c);
    const query = (...a: unknown[]) => {
      const [q] = a;
      const texto =
        typeof q === 'string' ? q : typeof q === 'object' && q && 'text' in q ? String(q.text) : '';
      comandos.push(texto.trim().split(/\s+/).slice(0, 2).join(' '));
      return consultar(...a);
    };
    return Object.assign(c, { query });
  }

  async function recusa(admin: pg.Client, opcoes: OpcoesPreparo) {
    const comandos: string[] = [];
    const erro = await falhaDe(
      prepararBanco(anotado(admin, comandos), opcoes, (config) => anotado(new pg.Client(config), comandos)),
    );
    return { erro, comandos, alteracoes: comandos.filter((c) => ALTERA.test(c)) };
  }

  async function comAdministrador<T>(usuario: string | undefined, f: (c: pg.Client) => Promise<T>) {
    const c = usuario ? await conectar(usuario, senhaAdministrador) : await conectar();
    try {
      return await f(c);
    } finally {
      await c.end();
    }
  }

  const servidorConfereSenha = async () => {
    try {
      await (await conectar('app_runtime', randomUUID())).end();
      return false;
    } catch (e) {
      if ((e as { code?: unknown }).code === '28P01') return true;
      throw e;
    }
  };

  it('ambiente divergente com senhas novas: recusa sem enviar alteração nenhuma', async () => {
    const r = await comAdministrador(undefined, (c) =>
      recusa(c, { ambiente: 'dev', banco: bancos.hml, senhas: novas() }),
    );
    expect(r.erro).toMatchObject({ codigo: 'IDENTIDADE_DIVERGENTE' });
    expect(r.alteracoes).toEqual([]);
    expect(r.comandos, 'a identidade foi lida').toContain('SET ROLE');
  });

  it('administrador sem poder assumir o migrator num banco existente: não verificável, nada muda', async () => {
    await raiz.query(
      `CREATE ROLE ${semSet} LOGIN CREATEROLE CREATEDB NOSUPERUSER NOBYPASSRLS NOREPLICATION PASSWORD '${senhaAdministrador}'`,
    );
    await raiz.query(
      `GRANT migrator, app_runtime, app_sessao TO ${semSet} WITH ADMIN TRUE, INHERIT FALSE, SET FALSE`,
    );
    const r = await comAdministrador(semSet, (c) =>
      recusa(c, { ambiente: 'hml', banco: bancos.hml, senhas: novas() }),
    );
    expect(r.erro).toMatchObject({ codigo: 'IDENTIDADE_NAO_VERIFICAVEL' });
    expect(r.alteracoes).toEqual([]);
    expect(r.comandos).toContain('SET ROLE');
    const assumir = await raiz.query(
      `SELECT 1 FROM pg_auth_members m JOIN pg_roles u ON u.oid = m.member WHERE u.rolname = $1 AND m.set_option`,
      [semSet],
    );
    expect(assumir.rowCount, 'nenhum papel concedido para verificar').toBe(0);
    expect(await noBanco(bancos.hml, (c) => lerIdentidadeAmbiente(c))).toBe('hml');
  });

  it('banco criado e interrompido antes da primeira migração: retoma; sem SET no migrator, recusa sem efeito (HML-PREP-03)', async () => {
    await raiz.query(`CREATE DATABASE ${bancos.vazio} OWNER migrator`);
    const r = await comAdministrador(semSet, (c) =>
      recusa(c, { ambiente: 'hml', banco: bancos.vazio, senhas: senhas() }),
    );
    expect(r.erro).toMatchObject({ codigo: 'IDENTIDADE_NAO_VERIFICAVEL' });
    expect(r.alteracoes).toEqual([]);
    const esquema = await noBanco(bancos.vazio, (c) =>
      c.query("SELECT 1 FROM pg_namespace WHERE nspname IN ('app', 'migracao')"),
    );
    expect(esquema.rowCount, 'recusa sem migrar').toBe(0);
    expect(await prepararBanco(raiz, { ambiente: 'hml', banco: bancos.vazio, senhas: senhas() })).toEqual({
      ambiente: 'hml',
      banco: 'existente',
      migracoes: { aplicadas: migracoes, jaAplicadas: [] },
      identidade: 'definida',
    });
    expect(await noBanco(bancos.vazio, (c) => lerIdentidadeAmbiente(c))).toBe('hml');
  });

  it('senha informada que não é a atual: recusa sem alterar nem criar banco', async (ctx) => {
    // Servidor em trust aceita qualquer senha: a conferência só é medida com autenticação por senha (SCRAM).
    if (!(await servidorConfereSenha())) return ctx.skip();
    const novo = await comAdministrador(undefined, (c) =>
      recusa(c, { ambiente: 'hml', banco: bancos.semCredencial, senhas: novas() }),
    );
    expect(novo.erro).toMatchObject({ codigo: 'CREDENCIAL_DIVERGENTE' });
    expect(novo.alteracoes).toEqual([]);
    const existente = await comAdministrador(undefined, (c) =>
      recusa(c, { ambiente: 'hml', banco: bancos.hml, senhas: { ...senhas(), appRuntime: randomUUID() } }),
    );
    expect(existente.erro).toMatchObject({ codigo: 'CREDENCIAL_DIVERGENTE' });
    expect(existente.alteracoes).toEqual([]);
    const criado = await raiz.query('SELECT 1 FROM pg_database WHERE datname = $1', [bancos.semCredencial]);
    expect(criado.rowCount).toBe(0);
  });
});

describe('comando preparar-banco', () => {
  const linhas: string[] = [];
  const env = () => ({
    SAFRION_ADMIN_URL: inject('urlAdmin'),
    SAFRION_SENHA_MIGRATOR: inject('senhaMigrator'),
    SAFRION_SENHA_APP_RUNTIME: inject('senhaApp'),
  });
  const rodar = async (
    args: string[],
    e: Record<string, string | undefined>,
    conectar?: (config: pg.ClientConfig) => pg.Client,
  ) => {
    linhas.length = 0;
    return executarCli(args, e, (l) => linhas.push(l), conectar);
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

  it('opção recusada: 1 sem criar nem conectar cliente (HML-PREP-02)', async () => {
    let clientes = 0;
    const contar = (): pg.Client => {
      clientes++;
      throw new Error('cliente que não deveria existir');
    };
    const casos = [
      [['--ambiente', 'prod', '--banco', bancos.cli], 'AMBIENTE_PROIBIDO'],
      [['--ambiente', 'hml', '--banco', 'postgres'], 'OPCAO_INVALIDA'],
    ] as const;
    for (const [args, codigo] of casos) {
      expect(await rodar([...args], env(), contar), codigo).toBe(1);
      expect(JSON.parse(linhas[0] ?? '{}')).toMatchObject({ resultado: 'recusado', codigo });
    }
    expect(clientes).toBe(0);
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
