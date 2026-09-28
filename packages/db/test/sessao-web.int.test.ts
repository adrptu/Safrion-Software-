// Sessão da web e login em duas etapas (ADR 0004 rev. 2, §3 e §5; migração 0003), com os aceites do Codex de 28/09:
// sem continuação válida não há sessão; organização sem vínculo é recusada; ticket vencido ou reutilizado e escolhas
// simultâneas não geram duas sessões; revogação entre o callback e a escolha impede o acesso. Banco real, app_runtime.
import { randomUUID } from 'node:crypto';

import pg from 'pg';
import { afterAll, beforeAll, describe, expect, inject, it } from 'vitest';

import {
  abrirContinuacao,
  abrirTransacaoLogin,
  concluirContinuacao,
  consumirTransacaoLogin,
  novoToken,
  resolverSessao,
  revogarSessao,
  trocarPapel,
  vinculosDaContinuacao,
} from '../src/sessao-web.js';
import { emOrganizacao } from '../src/sessao.js';
import { criarBanco, semear, type Ambiente, type Semente } from './ambiente.js';

const ISSUER = 'https://login.exemplo.invalid';
const TABELAS = ['identity_link', 'session', 'login_transaction', 'login_continuation'];
const FUNCOES = [
  'abrir_transacao_login',
  'consumir_transacao_login',
  'abrir_continuacao',
  'vinculos_da_continuacao',
  'concluir_continuacao',
  'resolver_sessao',
  'revogar_sessao',
  'trocar_papel',
  'vincular_demonstracao',
];

let amb: Ambiente;
let raiz: pg.Client; // superusuário no banco deste arquivo: só observa e simula o que o administrador faria
let a: Semente;
let b: Semente;
let c: Semente;

const esperar = (ms: number) => new Promise((r) => setTimeout(r, ms));
const transacao = (destino = '/estoque') => ({
  state: randomUUID() + randomUUID(),
  nonce: randomUUID() + randomUUID(),
  verificadorPkce: novoToken().token + 'abcdefgh',
  destino,
});

async function atribuir(s: Semente, papel: string): Promise<void> {
  await emOrganizacao(amb.app, s.org, (cl) =>
    cl.query('INSERT INTO app.user_role (organization_id, user_id, role_code) VALUES ($1, $2, $3)', [
      s.org,
      s.usuario,
      papel,
    ]),
  );
}

/** Vínculo da identidade com o usuário da semente, como o administrador fará: o app_runtime não escreve vínculo. */
async function vincular(subject: string, s: Semente): Promise<void> {
  await emOrganizacao(amb.migrator, s.org, (cl) =>
    cl.query(
      'INSERT INTO app.identity_link (issuer, subject, organization_id, user_id) VALUES ($1, $2, $3, $4)',
      [ISSUER, subject, s.org, s.usuario],
    ),
  );
}

async function desvincular(subject: string, s: Semente): Promise<void> {
  await emOrganizacao(amb.migrator, s.org, (cl) =>
    cl.query('DELETE FROM app.identity_link WHERE issuer = $1 AND subject = $2 AND organization_id = $3', [
      ISSUER,
      subject,
      s.org,
    ]),
  );
}

async function ativar(s: Semente, ativo: boolean): Promise<void> {
  await emOrganizacao(amb.migrator, s.org, (cl) =>
    cl.query('UPDATE app.app_user SET active = $1 WHERE id = $2', [ativo, s.usuario]),
  );
}

async function tirarPapel(s: Semente, papel: string): Promise<void> {
  await emOrganizacao(amb.migrator, s.org, (cl) =>
    cl.query('DELETE FROM app.user_role WHERE user_id = $1 AND role_code = $2', [s.usuario, papel]),
  );
}

/** Identidade nova, vinculada à semente A com os dois papéis, pronta para abrir continuação. */
async function identidadeEmA(): Promise<string> {
  const subject = `sub-${randomUUID()}`;
  await vincular(subject, a);
  return subject;
}

async function entrar(subject: string, s: Semente = a, papel = 'gerente', validade?: number) {
  const { ticket } = await abrirContinuacao(amb.app, { issuer: ISSUER, subject }, '/estoque');
  const r = await concluirContinuacao(amb.app, ticket, { organizationId: s.org, papel }, validade);
  if (!r.ok) throw new Error(`login de teste recusado: ${r.codigo}`);
  return r.sessao.token;
}

beforeAll(async () => {
  amb = await criarBanco();
  const url = new URL(inject('urlAdmin'));
  url.pathname = `/${amb.banco}`;
  raiz = new pg.Client({ connectionString: url.toString() });
  await raiz.connect();
  a = await semear(amb.app, 'A');
  b = await semear(amb.app, 'B');
  c = await semear(amb.app, 'C');
  await atribuir(a, 'almoxarife');
  await atribuir(a, 'gerente');
  await atribuir(b, 'almoxarife');
  await atribuir(c, 'almoxarife');
});

afterAll(async () => {
  await raiz.end();
  await amb.encerrar();
});

describe('privilégios: o app_runtime só chega às tabelas pelas funções', () => {
  it('nenhum privilégio do app_runtime nas quatro tabelas, e leitura direta é recusada', async () => {
    for (const t of TABELAS) {
      for (const p of ['SELECT', 'INSERT', 'UPDATE', 'DELETE']) {
        const r = await raiz.query<{ ok: boolean }>('SELECT has_table_privilege($1, $2, $3) AS ok', [
          'app_runtime',
          `app.${t}`,
          p,
        ]);
        expect(r.rows[0]?.ok, `${p} em ${t}`).toBe(false);
      }
      await expect(amb.app.query(`SELECT count(*) FROM app.${t}`)).rejects.toMatchObject({ code: '42501' });
    }
  });

  it('funções SECURITY DEFINER do app_sessao (NOLOGIN), search_path fixo, sem EXECUTE para PUBLIC', async () => {
    const r = await raiz.query<{
      nome: string;
      definer: boolean;
      dono: string;
      dono_loga: boolean;
      config: string[] | null;
      publico: boolean;
      runtime: boolean;
    }>(
      `SELECT p.proname AS nome, p.prosecdef AS definer, o.rolname AS dono, o.rolcanlogin AS dono_loga,
              p.proconfig AS config,
              EXISTS (SELECT 1 FROM aclexplode(p.proacl) x WHERE x.grantee = 0 AND x.privilege_type = 'EXECUTE')
                AS publico,
              has_function_privilege('app_runtime', p.oid, 'EXECUTE') AS runtime
         FROM pg_proc p JOIN pg_roles o ON o.oid = p.proowner
        WHERE p.pronamespace = 'app'::regnamespace AND p.proname = ANY($1::text[])
        ORDER BY 1`,
      [FUNCOES],
    );
    expect(r.rows.map((l) => l.nome)).toEqual([...FUNCOES].sort());
    for (const l of r.rows) {
      expect(l, l.nome).toMatchObject({
        definer: true,
        dono: 'app_sessao',
        dono_loga: false,
        config: ['search_path=pg_catalog, pg_temp'],
        publico: false,
        runtime: true,
      });
    }
  });
});

describe('transação de login (antes do callback)', () => {
  it('devolve a transação uma única vez; ticket inexistente ou malformado não devolve nada', async () => {
    const t = transacao('/estoque?lote=1');
    const { ticket } = await abrirTransacaoLogin(amb.app, t);
    expect(await consumirTransacaoLogin(amb.app, ticket)).toEqual(t);
    expect(await consumirTransacaoLogin(amb.app, ticket)).toBeNull();
    expect(await consumirTransacaoLogin(amb.app, novoToken().token)).toBeNull();
    expect(await consumirTransacaoLogin(amb.app, 'curto')).toBeNull();
    expect(await consumirTransacaoLogin(amb.app, undefined)).toBeNull();
  });

  it('vencida não devolve nada', async () => {
    const { ticket } = await abrirTransacaoLogin(amb.app, transacao(), 1);
    await esperar(1200);
    expect(await consumirTransacaoLogin(amb.app, ticket)).toBeNull();
  });

  it('duas tentativas simultâneas com o mesmo ticket: só uma consome', async () => {
    const { ticket } = await abrirTransacaoLogin(amb.app, transacao());
    const r = await Promise.all(Array.from({ length: 5 }, () => consumirTransacaoLogin(amb.app, ticket)));
    expect(r.filter((x) => x !== null)).toHaveLength(1);
  });

  it('destino que não é caminho interno é recusado pelo banco', async () => {
    for (const destino of ['//malicioso.invalid', 'https://malicioso.invalid', '/a b', '/a\\b', '']) {
      await expect(abrirTransacaoLogin(amb.app, transacao(destino)), destino).rejects.toMatchObject({
        code: '23514',
      });
    }
  });
});

describe('continuação depois do callback: o único caminho que cria sessão', () => {
  it('lista só organizações e papéis vivos da identidade guardada no servidor', async () => {
    const subject = await identidadeEmA();
    await vincular(subject, b);
    const { ticket } = await abrirContinuacao(amb.app, { issuer: ISSUER, subject }, '/estoque');
    const vinculos = await vinculosDaContinuacao(amb.app, ticket);
    expect(vinculos.map((v) => [v.organizationId, v.papeis])).toEqual(
      expect.arrayContaining([
        [a.org, ['almoxarife', 'gerente']],
        [b.org, ['almoxarife']],
      ]),
    );
    expect(vinculos.map((v) => v.organizationId)).not.toContain(c.org);
    expect(await vinculosDaContinuacao(amb.app, novoToken().token)).toEqual([]);
  });

  it('escolha válida cria a sessão; o mesmo ticket não serve de novo', async () => {
    const subject = await identidadeEmA();
    const { ticket } = await abrirContinuacao(amb.app, { issuer: ISSUER, subject }, '/estoque?aba=saldo');
    const r = await concluirContinuacao(amb.app, ticket, { organizationId: a.org, papel: 'gerente' });
    expect(r).toMatchObject({ ok: true, usuarioId: a.usuario, destino: '/estoque?aba=saldo' });
    if (!r.ok) return;
    expect(await resolverSessao(amb.app, r.sessao.token)).toMatchObject({
      usuarioId: a.usuario,
      organizationId: a.org,
      papel: 'gerente',
    });
    expect(await concluirContinuacao(amb.app, ticket, { organizationId: a.org, papel: 'gerente' })).toEqual({
      ok: false,
      codigo: 'CONTINUACAO_INVALIDA',
    });
  });

  it('organização sem vínculo ou papel não atribuído: recusado, e o ticket foi consumido', async () => {
    const subject = await identidadeEmA();
    for (const escolha of [
      { organizationId: c.org, papel: 'almoxarife' }, // organização sem vínculo com essa identidade
      { organizationId: a.org, papel: 'motorista' }, // papel inexistente
    ]) {
      const { ticket } = await abrirContinuacao(amb.app, { issuer: ISSUER, subject }, '/');
      expect(await concluirContinuacao(amb.app, ticket, escolha)).toEqual({
        ok: false,
        codigo: 'VINCULO_AUSENTE',
      });
      expect(await concluirContinuacao(amb.app, ticket, { organizationId: a.org, papel: 'gerente' })).toEqual(
        {
          ok: false,
          codigo: 'CONTINUACAO_INVALIDA',
        },
      );
    }
  });

  it('sem continuação válida não há sessão: ticket inexistente, malformado ou vencido', async () => {
    const subject = await identidadeEmA();
    const antes = await raiz.query('SELECT count(*)::int n FROM app.session WHERE subject = $1', [subject]);
    for (const ticket of [novoToken().token, 'nao-e-token', undefined]) {
      expect(await concluirContinuacao(amb.app, ticket, { organizationId: a.org, papel: 'gerente' })).toEqual(
        {
          ok: false,
          codigo: 'CONTINUACAO_INVALIDA',
        },
      );
    }
    const { ticket } = await abrirContinuacao(amb.app, { issuer: ISSUER, subject }, '/', 1);
    await esperar(1200);
    expect(await concluirContinuacao(amb.app, ticket, { organizationId: a.org, papel: 'gerente' })).toEqual({
      ok: false,
      codigo: 'CONTINUACAO_INVALIDA',
    });
    const depois = await raiz.query('SELECT count(*)::int n FROM app.session WHERE subject = $1', [subject]);
    expect(depois.rows).toEqual(antes.rows);
  });

  it('cinco escolhas simultâneas com o mesmo ticket criam uma sessão só', async () => {
    const subject = await identidadeEmA();
    const { ticket } = await abrirContinuacao(amb.app, { issuer: ISSUER, subject }, '/');
    const r = await Promise.all(
      Array.from({ length: 5 }, () =>
        concluirContinuacao(amb.app, ticket, { organizationId: a.org, papel: 'almoxarife' }),
      ),
    );
    expect(r.filter((x) => x.ok)).toHaveLength(1);
    const n = await raiz.query('SELECT count(*)::int n FROM app.session WHERE subject = $1', [subject]);
    expect(n.rows).toEqual([{ n: 1 }]);
  });

  it('vínculo revogado, usuário desativado ou papel removido entre o callback e a escolha impedem o acesso', async () => {
    const subject = await identidadeEmA();
    const casos: [string, () => Promise<void>, () => Promise<void>][] = [
      ['vínculo revogado', () => desvincular(subject, a), () => vincular(subject, a)],
      ['usuário desativado', () => ativar(a, false), () => ativar(a, true)],
      ['papel removido', () => tirarPapel(a, 'gerente'), () => atribuir(a, 'gerente')],
    ];
    for (const [nome, revogar, restaurar] of casos) {
      const { ticket } = await abrirContinuacao(amb.app, { issuer: ISSUER, subject }, '/');
      await revogar();
      try {
        expect(
          await concluirContinuacao(amb.app, ticket, { organizationId: a.org, papel: 'gerente' }),
          nome,
        ).toEqual({ ok: false, codigo: 'VINCULO_AUSENTE' });
      } finally {
        await restaurar();
      }
    }
  });
});

describe('sessão resolvida com vínculo vivo', () => {
  it('token inexistente, malformado, revogado ou vencido não resolve', async () => {
    const subject = await identidadeEmA();
    expect(await resolverSessao(amb.app, novoToken().token)).toBeNull();
    expect(await resolverSessao(amb.app, 'x')).toBeNull();
    const token = await entrar(subject);
    expect(await revogarSessao(amb.app, token)).toBe(true);
    expect(await resolverSessao(amb.app, token)).toBeNull();
    expect(await revogarSessao(amb.app, token)).toBe(false);
    const curta = await entrar(subject, a, 'gerente', 1);
    await esperar(1200);
    expect(await resolverSessao(amb.app, curta)).toBeNull();
  });

  it('usuário desativado, papel removido ou vínculo revogado bloqueiam a requisição seguinte', async () => {
    const subject = await identidadeEmA();
    const casos: [string, () => Promise<void>, () => Promise<void>][] = [
      ['usuário desativado', () => ativar(a, false), () => ativar(a, true)],
      ['papel removido', () => tirarPapel(a, 'gerente'), () => atribuir(a, 'gerente')],
      ['vínculo revogado', () => desvincular(subject, a), () => vincular(subject, a)],
    ];
    for (const [nome, revogar, restaurar] of casos) {
      const token = await entrar(subject);
      expect(await resolverSessao(amb.app, token), nome).not.toBeNull();
      await revogar();
      try {
        expect(await resolverSessao(amb.app, token), nome).toBeNull();
      } finally {
        await restaurar();
      }
    }
  });

  it('resolver não fixa organização na transação de quem chama', async () => {
    const token = await entrar(await identidadeEmA());
    const cl = await amb.app.connect();
    try {
      await cl.query('BEGIN');
      expect(await resolverSessao(cl, token)).not.toBeNull();
      const r = await cl.query<{ org: string | null }>(
        "SELECT current_setting('app.organization_id', true) AS org",
      );
      expect(r.rows[0]?.org ?? '').toBe('');
      await cl.query('COMMIT');
    } finally {
      cl.release();
    }
  });

  it('troca de papel só para papel atribuído; a sessão antiga deixa de valer e a expiração não aumenta', async () => {
    const subject = await identidadeEmA();
    const token = await entrar(subject, a, 'gerente');
    const antes = await resolverSessao(amb.app, token);
    expect(await trocarPapel(amb.app, token, 'motorista')).toEqual({
      ok: false,
      codigo: 'PAPEL_NAO_VINCULADO',
    });
    expect(await resolverSessao(amb.app, token)).not.toBeNull();
    const r = await trocarPapel(amb.app, token, 'almoxarife');
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(await resolverSessao(amb.app, token)).toBeNull();
    expect(await resolverSessao(amb.app, r.sessao.token)).toMatchObject({ papel: 'almoxarife' });
    expect(r.sessao.expiraEm.getTime()).toBe(antes?.expiraEm.getTime());
    expect(await trocarPapel(amb.app, token, 'gerente')).toEqual({ ok: false, codigo: 'SESSAO_INVALIDA' });
  });

  it('trocas simultâneas da mesma sessão: só uma cria sessão nova', async () => {
    const token = await entrar(await identidadeEmA());
    const r = await Promise.all(Array.from({ length: 5 }, () => trocarPapel(amb.app, token, 'almoxarife')));
    expect(r.filter((x) => x.ok)).toHaveLength(1);
  });
});
