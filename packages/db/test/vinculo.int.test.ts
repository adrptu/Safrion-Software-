// Vínculo de identidade real em HML (ADR 0004 §11; migração 0005), com banco real identificado como hml e a demonstração
// restaurada: pedido de acesso pela casca (app_runtime), concessão e revogação pelo administrador (migrator), cota,
// concorrência com login e troca de papel, rollback, demo:reset e o comando. O superusuário do servidor de teste só
// prepara usuários e confere o estado.
import { createHash, randomUUID } from 'node:crypto';
import { PassThrough } from 'node:stream';

import pg from 'pg';
import { afterAll, beforeAll, describe, expect, inject, it } from 'vitest';

import { definirIdentidadeAmbiente, restaurarDemonstracao, type Demonstracao } from '../src/ambiente.js';
import { executarCli, lerDaEntrada } from '../src/cli/vincular-identidade.js';
import { abrirContinuacao, concluirContinuacao, resolverSessao, trocarPapel } from '../src/sessao-web.js';
import { concederVinculo, normalizarCodigo, registrarPedidoAcesso, revogarVinculos } from '../src/vinculo.js';
import { criarBanco, type Ambiente } from './ambiente.js';

const ISSUER = 'https://idp.sintetico.invalid';
const DEV = 'urn:safrion:desenvolvimento';
let hml: Ambiente;
let dev: Ambiente;
let demo: Demonstracao;
let raiz: pg.Client;

const falhaDe = (p: Promise<unknown>) =>
  p.then(
    () => undefined,
    (e: unknown) => e,
  );
const identidade = () => ({ issuer: ISSUER, subject: `sub-${randomUUID()}` });
const papelDe = (papel: string) => {
  const u = demo.usuarios.find((x) => x.papel === papel);
  if (!u) throw new Error(`papel ${papel} ausente`);
  return u.usuarioId;
};
const hashHex = (codigo: string) => createHash('sha256').update(codigo).digest('hex');

async function identificar(amb: Ambiente, nome: 'dev' | 'hml') {
  const mig = new pg.Client({ connectionString: amb.url('migrator') });
  await mig.connect();
  try {
    await definirIdentidadeAmbiente(mig, nome);
  } finally {
    await mig.end();
  }
}

async function pedir(id: { issuer: string; subject: string }): Promise<string> {
  const p = await registrarPedidoAcesso(hml.app, id);
  if (p.resultado !== 'registrado') throw new Error(`pedido não registrado: ${p.resultado}`);
  return p.codigo;
}

async function comMigrator<T>(f: (c: pg.PoolClient) => Promise<T>, amb = hml): Promise<T> {
  const c = await amb.migrator.connect();
  try {
    return await f(c);
  } finally {
    c.release();
  }
}

const destino = (usuario: string, organizacao = demo.organizationId) => ({
  organizacao,
  usuario,
  responsavel: 'Adrianus (proprietário)',
  motivo: 'acesso de homologação',
});

const conceder = (codigo: string, usuario: string, organizacao?: string) =>
  comMigrator((c) => concederVinculo(c, { ...destino(usuario, organizacao), codigo }));

const revogar = (usuario: string, organizacao?: string) =>
  comMigrator((c) => revogarVinculos(c, destino(usuario, organizacao)));

async function vinculos(subject: string) {
  return (
    await raiz.query<{ organization_id: string; user_id: string }>(
      'SELECT organization_id, user_id FROM app.identity_link WHERE issuer = $1 AND subject = $2 ORDER BY 1',
      [ISSUER, subject],
    )
  ).rows;
}

async function eventos(subject: string) {
  return (
    await raiz.query<{
      action: string;
      user_id: string;
      responsible: string;
      reason: string;
      database_user: string;
    }>(
      `SELECT action, user_id, responsible, reason, database_user FROM app.identity_link_event
        WHERE issuer = $1 AND subject = $2 ORDER BY occurred_at`,
      [ISSUER, subject],
    )
  ).rows;
}

/** Login pelas funções da casca; devolve o token da sessão, ou null se não entrou. */
async function entrar(
  id: { issuer: string; subject: string },
  papel: string,
  organizacao = demo.organizationId,
) {
  const cont = await abrirContinuacao(hml.app, id, '/estoque');
  const r = await concluirContinuacao(hml.app, cont.ticket, { organizationId: organizacao, papel });
  return r.ok ? r.sessao.token : null;
}

/** Usuário novo na organização, com os papéis dados, criado pelo superusuário do teste. */
async function novoUsuario(papeis: readonly string[], organizacao = demo.organizationId, ativo = true) {
  const id = randomUUID();
  await raiz.query(
    'INSERT INTO app.app_user (id, organization_id, name, email, active) VALUES ($1, $2, $3, $4, $5)',
    [id, organizacao, 'Pessoa de teste', `${id}@teste.invalid`, ativo],
  );
  for (const p of papeis) {
    await raiz.query('INSERT INTO app.user_role (organization_id, user_id, role_code) VALUES ($1, $2, $3)', [
      organizacao,
      id,
      p,
    ]);
  }
  return id;
}

beforeAll(async () => {
  hml = await criarBanco();
  dev = await criarBanco();
  await identificar(hml, 'hml');
  await identificar(dev, 'dev');
  demo = await restaurarDemonstracao(hml.app, { confirmar: 'hml', ambienteDoProcesso: 'hml' });
  const url = new URL(inject('urlAdmin'));
  url.pathname = `/${hml.banco}`;
  raiz = new pg.Client({ connectionString: url.toString() });
  await raiz.connect();
});

afterAll(async () => {
  await raiz.end();
  await hml.encerrar();
  await dev.encerrar();
});

describe('pedido de acesso (casca, app_runtime): não concede nada', () => {
  it('guarda só o hash, troca o código num novo login e não dá acesso', async () => {
    const id = identidade();
    const primeiro = await pedir(id);
    const linhas = await raiz.query<{ h: string }>(
      "SELECT encode(code_hash, 'hex') AS h, row_to_json(r)::text AS tudo FROM app.access_request r WHERE subject = $1",
      [id.subject],
    );
    expect(linhas.rows.map((l) => l.h)).toEqual([hashHex(primeiro)]);
    expect(JSON.stringify(linhas.rows)).not.toContain(primeiro);
    const segundo = await pedir(id);
    expect(segundo).not.toBe(primeiro);
    const vivos = await raiz.query('SELECT 1 FROM app.access_request WHERE subject = $1', [id.subject]);
    expect(vivos.rowCount).toBe(1);
    expect(await falhaDe(conceder(primeiro, papelDe('almoxarife')))).toMatchObject({
      codigo: 'PEDIDO_INEXISTENTE',
    });
    expect(await vinculos(id.subject)).toEqual([]);
    expect(await entrar(id, 'almoxarife')).toBeNull();
  });

  it('issuer de desenvolvimento e banco fora de hml não registram pedido', async () => {
    expect(await registrarPedidoAcesso(hml.app, { issuer: DEV, subject: 'demo-almoxarife' })).toEqual({
      resultado: 'recusado',
    });
    expect(await registrarPedidoAcesso(dev.app, identidade())).toEqual({ resultado: 'fora_de_hml' });
  });

  it('o código aceita o que a pessoa digita ou cola', () => {
    expect(normalizarCodigo('abcde-fghjk')).toBe('ABCDEFGHJK');
    expect(normalizarCodigo(' 0o1il 23456 ')).toBe('0011123456');
    for (const errado of ['', 'ABCDEFGHJ', 'ABCDEFGHJKM', 'ABCDEFGHJU', 'ABCDE*GHJK']) {
      expect(normalizarCodigo(errado), errado).toBeNull();
    }
  });
});

describe('concessão pelo administrador (migrator), só em hml', () => {
  it('concede, consome o pedido, audita quem estava conectado e a pessoa entra; repetir mantém', async () => {
    const id = identidade();
    const codigo = await pedir(id);
    const almoxarife = papelDe('almoxarife');
    expect(await conceder(codigo, almoxarife)).toBe('concedido');
    expect(await vinculos(id.subject)).toEqual([
      { organization_id: demo.organizationId, user_id: almoxarife },
    ]);
    expect(await eventos(id.subject)).toEqual([
      {
        action: 'concedido',
        user_id: almoxarife,
        responsible: 'Adrianus (proprietário)',
        reason: 'acesso de homologação',
        database_user: 'migrator',
      },
    ]);
    const token = await entrar(id, 'almoxarife');
    expect(await resolverSessao(hml.app, token ?? undefined)).toMatchObject({ usuarioId: almoxarife });
    expect(await conceder(codigo, almoxarife)).toBe('mantido');
    expect(await eventos(id.subject)).toHaveLength(1);
  });

  it('recusas não mudam nada: código, prazo, usuário, conflito e opções', async () => {
    const almoxarife = papelDe('almoxarife');
    const gerente = papelDe('gerente');
    const codigoDe = (e: unknown) => (e as { codigo?: string } | undefined)?.codigo;
    // Código que não existe, e fora do formato.
    expect(codigoDe(await falhaDe(conceder('ABCDEFGHJK', almoxarife)))).toBe('PEDIDO_INEXISTENTE');
    expect(codigoDe(await falhaDe(conceder('curto', almoxarife)))).toBe('CODIGO_INVALIDO');
    // Vencido.
    const vencido = identidade();
    const cv = await pedir(vencido);
    await raiz.query(
      "UPDATE app.access_request SET expires_at = now() - interval '1 second' WHERE subject = $1",
      [vencido.subject],
    );
    expect(codigoDe(await falhaDe(conceder(cv, almoxarife)))).toBe('PEDIDO_VENCIDO');
    // Usuário de fora, inativo ou sem papel.
    const x = identidade();
    const cx = await pedir(x);
    for (const u of [
      randomUUID(),
      await novoUsuario(['almoxarife'], demo.organizationId, false),
      await novoUsuario([]),
    ]) {
      expect(codigoDe(await falhaDe(conceder(cx, u)))).toBe('USUARIO_INVALIDO');
    }
    // Pedido já consumido para outro destino, e identidade já ligada a outro usuário nesta organização.
    const y = identidade();
    const cy = await pedir(y);
    expect(await conceder(cy, almoxarife)).toBe('concedido');
    expect(codigoDe(await falhaDe(conceder(cy, gerente)))).toBe('VINCULO_CONFLITANTE');
    const cy2 = await pedir(y);
    expect(codigoDe(await falhaDe(conceder(cy2, gerente)))).toBe('VINCULO_CONFLITANTE');
    // Opções: conferidas antes do banco, e de novo pela função.
    expect(
      codigoDe(
        await falhaDe(
          comMigrator((c) => concederVinculo(c, { ...destino(gerente), responsavel: 'a\nb', codigo: cx })),
        ),
      ),
    ).toBe('OPCAO_INVALIDA');
    const direto = await comMigrator((c) =>
      c.query<{ r: string }>('SELECT app.conceder_vinculo($1, $2, $3, $4, $5) AS r', [
        Buffer.from(hashHex(cx), 'hex'),
        demo.organizationId,
        gerente,
        'a\u0007b',
        'motivo',
      ]),
    );
    expect(direto.rows[0]?.r).toBe('OPCAO_INVALIDA');
    // Nada mudou: nenhum vínculo novo além do de y, pedidos de x e o segundo de y sem consumo, um evento só. O pedido
    // vencido não foi consumido: saiu na limpeza do registro seguinte, por ter vencido.
    for (const s of [vencido.subject, x.subject]) expect(await vinculos(s)).toEqual([]);
    expect(await vinculos(y.subject)).toEqual([
      { organization_id: demo.organizationId, user_id: almoxarife },
    ]);
    expect(await eventos(y.subject)).toHaveLength(1);
    const pendentes = await raiz.query<{ subject: string }>(
      'SELECT subject FROM app.access_request WHERE subject = ANY($1) AND consumed_at IS NULL ORDER BY subject',
      [[vencido.subject, x.subject, y.subject]],
    );
    expect(pendentes.rows.map((r) => r.subject)).toEqual([x.subject, y.subject].sort());
    const vencidos = await raiz.query('SELECT 1 FROM app.access_request WHERE subject = $1', [
      vencido.subject,
    ]);
    expect(vencidos.rowCount).toBe(0);
  });

  it('o app_runtime não concede, não revoga e não toca nas tabelas do vínculo; a auditoria não muda', async () => {
    const codigoPg = async (sql: string, params: unknown[] = []) =>
      ((await falhaDe(hml.app.query(sql, params))) as { code?: string } | undefined)?.code;
    const u = papelDe('almoxarife');
    expect(
      await codigoPg('SELECT app.conceder_vinculo($1, $2, $3, $4, $5)', [
        Buffer.alloc(32),
        demo.organizationId,
        u,
        'r',
        'm',
      ]),
    ).toBe('42501');
    expect(
      await codigoPg('SELECT * FROM app.revogar_vinculos($1, $2, $3, $4)', [
        demo.organizationId,
        u,
        'r',
        'm',
      ]),
    ).toBe('42501');
    expect(await codigoPg('SELECT count(*) FROM app.access_request')).toBe('42501');
    expect(await codigoPg('SELECT count(*) FROM app.identity_link_event')).toBe('42501');
    expect(
      await codigoPg(
        'INSERT INTO app.identity_link (issuer, subject, organization_id, user_id) VALUES ($1, $2, $3, $4)',
        [ISSUER, 'invasor', demo.organizationId, u],
      ),
    ).toBe('42501');
    const alterar = await falhaDe(raiz.query("UPDATE app.identity_link_event SET reason = 'outro'"));
    expect(alterar).toBeInstanceOf(Error);
    expect(await falhaDe(raiz.query('DELETE FROM app.identity_link_event'))).toBeInstanceOf(Error);
  });

  it('fora de hml, concessão e revogação são recusadas', async () => {
    const u = randomUUID();
    const o = randomUUID();
    await comMigrator(async (c) => {
      expect(await falhaDe(concederVinculo(c, { ...destino(u, o), codigo: 'ABCDEFGHJK' }))).toMatchObject({
        codigo: 'AMBIENTE_PROIBIDO',
      });
      expect(await falhaDe(revogarVinculos(c, destino(u, o)))).toMatchObject({ codigo: 'AMBIENTE_PROIBIDO' });
    }, dev);
  });
});

describe('revogação: todos os vínculos do usuário na organização', () => {
  it('um evento por vínculo, sessões revogadas, outra organização intacta; código antigo não reabre; sem ressuscitar sessão', async () => {
    const usuario = await novoUsuario(['gerente']);
    const outraOrg = randomUUID();
    await raiz.query('INSERT INTO app.organization (id, name) VALUES ($1, $2)', [
      outraOrg,
      'Outra organização',
    ]);
    const naOutra = await novoUsuario(['gerente'], outraOrg);
    const a = identidade();
    const b = identidade();
    const codigoA = await pedir(a);
    expect(await conceder(codigoA, usuario)).toBe('concedido');
    expect(await conceder(await pedir(b), usuario)).toBe('concedido');
    expect(await conceder(await pedir(a), naOutra, outraOrg)).toBe('concedido');
    const sessaoA = await entrar(a, 'gerente');
    const sessaoB = await entrar(b, 'gerente');
    const sessaoOutra = await entrar(a, 'gerente', outraOrg);
    expect(await revogar(usuario)).toEqual({ resultado: 'revogado', revogados: 2 });
    for (const s of [sessaoA, sessaoB]) expect(await resolverSessao(hml.app, s ?? undefined)).toBeNull();
    expect(await resolverSessao(hml.app, sessaoOutra ?? undefined)).toMatchObject({
      organizationId: outraOrg,
    });
    expect(await vinculos(a.subject)).toEqual([{ organization_id: outraOrg, user_id: naOutra }]);
    expect((await eventos(a.subject)).map((e) => e.action)).toEqual(['concedido', 'concedido', 'revogado']);
    expect((await eventos(b.subject)).map((e) => e.action)).toEqual(['concedido', 'revogado']);
    // Repetir não muda nada.
    expect(await revogar(usuario)).toEqual({ resultado: 'sem_vinculo', revogados: 0 });
    expect(await eventos(b.subject)).toHaveLength(2);
    // O código antigo não reabre o acesso; um pedido novo concede, e a sessão antiga continua morta.
    expect(await falhaDe(conceder(codigoA, usuario))).toMatchObject({ codigo: 'PEDIDO_CONSUMIDO' });
    expect(await conceder(await pedir(a), usuario)).toBe('concedido');
    expect(await resolverSessao(hml.app, sessaoA ?? undefined)).toBeNull();
    expect(await entrar(a, 'gerente')).not.toBeNull();
  });
});

describe('concorrência', () => {
  it('revogação ao mesmo tempo que a conclusão do login nunca deixa sessão válida, nem depois de nova concessão', async () => {
    const desfechos = { entrou: 0, barrado: 0 };
    for (let i = 0; i < 12; i++) {
      const usuario = await novoUsuario(['almoxarife']);
      const id = identidade();
      expect(await conceder(await pedir(id), usuario)).toBe('concedido');
      const cont = await abrirContinuacao(hml.app, id, '/estoque');
      const [conclusao] = await Promise.all([
        concluirContinuacao(hml.app, cont.ticket, {
          organizationId: demo.organizationId,
          papel: 'almoxarife',
        }),
        revogar(usuario),
      ]);
      if (conclusao.ok) {
        desfechos.entrou++;
        expect(await resolverSessao(hml.app, conclusao.sessao.token)).toBeNull();
        expect(await conceder(await pedir(id), usuario)).toBe('concedido');
        expect(await resolverSessao(hml.app, conclusao.sessao.token)).toBeNull();
      } else {
        desfechos.barrado++;
      }
    }
    expect(desfechos.entrou + desfechos.barrado).toBe(12);
  });

  it('troca de papel ao mesmo tempo que a revogação também não deixa sessão válida', async () => {
    for (let i = 0; i < 8; i++) {
      const usuario = await novoUsuario(['almoxarife', 'gerente']);
      const id = identidade();
      expect(await conceder(await pedir(id), usuario)).toBe('concedido');
      const token = await entrar(id, 'almoxarife');
      const [troca] = await Promise.all([
        trocarPapel(hml.app, token ?? undefined, 'gerente'),
        revogar(usuario),
      ]);
      if (troca.ok) {
        expect(await resolverSessao(hml.app, troca.sessao.token)).toBeNull();
        expect(await conceder(await pedir(id), usuario)).toBe('concedido');
        expect(await resolverSessao(hml.app, troca.sessao.token)).toBeNull();
      }
      expect(await resolverSessao(hml.app, token ?? undefined)).toBeNull();
    }
  });

  it('duas concessões simultâneas do mesmo pedido: uma concede, a outra mantém, um evento', async () => {
    const usuario = await novoUsuario(['almoxarife']);
    const id = identidade();
    const codigo = await pedir(id);
    const resultados = await Promise.all([conceder(codigo, usuario), conceder(codigo, usuario)]);
    expect(resultados.sort()).toEqual(['concedido', 'mantido']);
    expect(await eventos(id.subject)).toHaveLength(1);
  });
});

/** Espera a sessão do pid entrar em espera de trava (a ordem entre duas transações fica determinada, sem sleep). */
async function esperandoTrava(pid: number) {
  const limite = Date.now() + 5000;
  while (Date.now() < limite) {
    const r = await raiz.query<{ espera: string | null }>(
      'SELECT wait_event_type AS espera FROM pg_stat_activity WHERE pid = $1',
      [pid],
    );
    if (r.rows[0]?.espera === 'Lock') return;
    await new Promise<void>((resolve) => setImmediate(resolve));
  }
  throw new Error('NAO_ENTROU_NA_ESPERA_ESPERADA');
}

// HML-VINC-01 (prova do Codex, 28/09): a renovação que chega enquanto a concessão consome o mesmo pedido esperava só o
// índice e inseria depois do COMMIT, passando de 1000 retidos. Agora espera a trava da cota e conta sobre estado firme.
describe('HML-VINC-01: renovação durante a concessão do mesmo pedido', () => {
  it('não ultrapassa 1000 retidos e recusa pela cota, sem apagar retidos recentes', async () => {
    await raiz.query('DELETE FROM app.access_request');
    const usuario = await novoUsuario(['almoxarife']);
    const id = identidade();
    const codigo = await pedir(id);
    await raiz.query(
      `INSERT INTO app.access_request (code_hash, issuer, subject, expires_at, consumed_at, organization_id, user_id)
       SELECT sha256(convert_to('retido-' || i, 'UTF8')), 'https://retido.invalid', 'retido-' || i,
              now() + interval '1 day', now(), $1, $2
         FROM generate_series(1, 999) i`,
      [demo.organizationId, usuario],
    );
    const admin = await hml.migrator.connect();
    const solicitante = await hml.app.connect();
    let renovacao: ReturnType<typeof registrarPedidoAcesso> | undefined;
    try {
      await admin.query('BEGIN');
      expect(await concederVinculo(admin, { ...destino(usuario), codigo })).toBe('concedido');
      const pid =
        (await solicitante.query<{ pid: number }>('SELECT pg_backend_pid() AS pid')).rows[0]?.pid ?? 0;
      renovacao = registrarPedidoAcesso(solicitante, id);
      await esperandoTrava(pid);
      await admin.query('COMMIT');
      const resultado = await renovacao;
      const total = (await raiz.query<{ n: number }>('SELECT count(*)::int AS n FROM app.access_request'))
        .rows[0]?.n;
      expect({ resultado: resultado.resultado, total }).toEqual({ resultado: 'cota_esgotada', total: 1000 });
      const retidos = await raiz.query(
        "SELECT 1 FROM app.access_request WHERE issuer = 'https://retido.invalid'",
      );
      expect(retidos.rowCount).toBe(999);
    } finally {
      await admin.query('ROLLBACK');
      await renovacao?.catch(() => undefined);
      admin.release();
      solicitante.release();
      await raiz.query('DELETE FROM app.access_request');
    }
  });
});

describe('cota de pedidos em HML', () => {
  it('até 100 vivos, inclusive com registros simultâneos; 1000 retidos; limpeza de vencidos e de consumidos antigos', async () => {
    await raiz.query('DELETE FROM app.access_request');
    const carga = (n: number, extra: string) =>
      raiz.query(
        `INSERT INTO app.access_request (code_hash, issuer, subject, expires_at, consumed_at, organization_id, user_id)
         SELECT sha256(convert_to($2 || i, 'UTF8')), 'https://carga.invalid', $2 || i, now() + interval '1 hour', ${extra}
           FROM generate_series(1, $1) i`,
        [n, `carga-${randomUUID()}-`],
      );
    await carga(99, 'NULL, NULL, NULL');
    const simultaneos = await Promise.all(
      Array.from({ length: 5 }, () => identidade()).map((id) => registrarPedidoAcesso(hml.app, id)),
    );
    expect(simultaneos.filter((p) => p.resultado === 'registrado')).toHaveLength(1);
    expect(simultaneos.filter((p) => p.resultado === 'cota_esgotada')).toHaveLength(4);
    const vivos = async () =>
      Number(
        (
          await raiz.query<{ n: string }>(
            'SELECT count(*) AS n FROM app.access_request WHERE consumed_at IS NULL',
          )
        ).rows[0]?.n,
      );
    expect(await vivos()).toBe(100);
    // Quem já tem pedido vivo renova mesmo com a cota cheia.
    const renovar = await raiz.query<{ issuer: string; subject: string }>(
      'SELECT issuer, subject FROM app.access_request WHERE issuer = $1 AND consumed_at IS NULL',
      [ISSUER],
    );
    const [dono] = renovar.rows;
    if (!dono) throw new Error('pedido vivo ausente');
    expect((await registrarPedidoAcesso(hml.app, dono)).resultado).toBe('registrado');
    // Vencidos saem na próxima gravação e liberam lugar.
    await raiz.query(
      "UPDATE app.access_request SET expires_at = now() - interval '1 second' WHERE issuer = 'https://carga.invalid' AND ctid IN (SELECT ctid FROM app.access_request WHERE issuer = 'https://carga.invalid' LIMIT 10)",
    );
    expect((await registrarPedidoAcesso(hml.app, identidade())).resultado).toBe('registrado');
    expect(await vivos()).toBe(91);
    // Retidos: consumidos há menos de 30 dias contam e não são apagados para abrir espaço.
    const total = async () =>
      Number((await raiz.query<{ n: string }>('SELECT count(*) AS n FROM app.access_request')).rows[0]?.n);
    await carga(1000 - (await total()), `now(), '${demo.organizationId}', '${papelDe('almoxarife')}'`);
    expect(await total()).toBe(1000);
    expect((await registrarPedidoAcesso(hml.app, identidade())).resultado).toBe('cota_esgotada');
    expect(await total()).toBe(1000);
    await raiz.query(
      "UPDATE app.access_request SET consumed_at = now() - interval '31 days' WHERE consumed_at IS NOT NULL",
    );
    expect((await registrarPedidoAcesso(hml.app, identidade())).resultado).toBe('registrado');
    expect(await total()).toBe(92);
    await raiz.query('DELETE FROM app.access_request');
  });
});

describe('rollback', () => {
  it('falha na mesma transação desfaz concessão, consumo e evento', async () => {
    const usuario = await novoUsuario(['almoxarife']);
    const id = identidade();
    const codigo = await pedir(id);
    await comMigrator(async (c) => {
      await c.query('BEGIN');
      try {
        expect(await concederVinculo(c, { ...destino(usuario), codigo })).toBe('concedido');
        await c.query('SELECT 1 / 0');
      } catch {
        await c.query('ROLLBACK');
      }
    });
    expect(await vinculos(id.subject)).toEqual([]);
    expect(await eventos(id.subject)).toEqual([]);
    expect(await conceder(codigo, usuario)).toBe('concedido');
  });

  it('falha no meio do demo:reset desfaz a revogação e os eventos', async () => {
    const id = identidade();
    expect(await conceder(await pedir(id), papelDe('gerente'))).toBe('concedido');
    const c = await hml.app.connect();
    try {
      await c.query('BEGIN');
      const r = await c.query<{ n: number }>('SELECT app.revogar_vinculos_demonstracao($1) AS n', [
        randomUUID(),
      ]);
      expect(r.rows[0]?.n).toBeGreaterThan(0);
      expect(await falhaDe(c.query('SELECT 1 / 0'))).toBeInstanceOf(Error);
      await c.query('ROLLBACK');
    } finally {
      c.release();
    }
    expect(await vinculos(id.subject)).toHaveLength(1);
    expect((await eventos(id.subject)).map((e) => e.action)).toEqual(['concedido']);
  });
});

describe('comando vincular-identidade', () => {
  const linhas: string[] = [];
  const env = () => ({ SAFRION_ADMIN_URL: inject('urlAdmin') });
  const args = (acao: string, usuario: string, extra: string[] = []) => [
    acao,
    '--ambiente',
    'hml',
    '--banco',
    hml.banco,
    '--organizacao',
    demo.organizationId,
    '--usuario',
    usuario,
    '--responsavel',
    'Adrianus (proprietário)',
    '--motivo',
    'acesso de homologação',
    ...extra,
  ];
  const rodar = async (
    argv: string[],
    codigo = '',
    e: Record<string, string | undefined> = env(),
    conectar?: (config: pg.ClientConfig) => pg.Client,
  ) => {
    linhas.length = 0;
    return executarCli(
      argv,
      e,
      (l) => linhas.push(l),
      () => Promise.resolve(codigo),
      conectar,
    );
  };
  const ultima = () => JSON.parse(linhas.at(-1) ?? '{}') as Record<string, unknown>;

  it('uso incorreto: 2; o código nunca entra por argumento', async () => {
    const u = randomUUID();
    expect(await rodar(['--ambiente', 'hml'])).toBe(2);
    expect(await rodar(args('conceder', u, ['--codigo', 'ABCDEFGHJK']))).toBe(2);
    expect(await rodar([...args('conceder', u), 'sobra'])).toBe(2);
    expect(await rodar(args('apagar', u))).toBe(2);
    expect(linhas[0]).toContain('Uso:');
  });

  it('dev, prod e opção inválida: 1 sem ler código nem criar cliente', async () => {
    let lidos = 0;
    let clientes = 0;
    for (const [argv, codigo] of [
      [args('conceder', randomUUID()).map((a) => (a === 'hml' ? 'prod' : a)), 'AMBIENTE_PROIBIDO'],
      [args('conceder', randomUUID()).map((a) => (a === 'hml' ? 'dev' : a)), 'AMBIENTE_PROIBIDO'],
      [args('conceder', 'nao-e-uuid'), 'OPCAO_INVALIDA'],
    ] as const) {
      linhas.length = 0;
      const saida = await executarCli(
        [...argv],
        env(),
        (l) => linhas.push(l),
        () => {
          lidos++;
          return Promise.resolve('ABCDEFGHJK');
        },
        () => {
          clientes++;
          throw new Error('cliente que não deveria existir');
        },
      );
      expect(saida, codigo).toBe(1);
      expect(ultima()).toMatchObject({ resultado: 'recusado', codigo });
    }
    expect(lidos).toBe(0);
    expect(clientes).toBe(0);
  });

  it('concede, mantém, revoga e repete sem efeito; saída sem código, subject nem hash', async () => {
    const usuario = await novoUsuario(['almoxarife']);
    const id = identidade();
    const codigo = await pedir(id);
    const digitado = `${codigo.slice(0, 5).toLowerCase()}-${codigo.slice(5)}`;
    expect(await rodar(args('conceder', usuario), digitado)).toBe(0);
    expect(ultima()).toEqual({ resultado: 'concedido' });
    const tudo: string[] = [...linhas];
    expect(await rodar(args('conceder', usuario), codigo)).toBe(0);
    expect(ultima()).toEqual({ resultado: 'mantido' });
    tudo.push(...linhas);
    expect(await rodar(args('revogar', usuario))).toBe(0);
    expect(ultima()).toEqual({ resultado: 'revogado', revogados: 1 });
    tudo.push(...linhas);
    expect(await rodar(args('revogar', usuario))).toBe(0);
    expect(ultima()).toEqual({ resultado: 'sem_vinculo', revogados: 0 });
    tudo.push(...linhas);
    expect(await rodar(args('conceder', usuario), 'ABCDEFGHJK')).toBe(1);
    expect(ultima()).toMatchObject({ resultado: 'recusado', codigo: 'PEDIDO_INEXISTENTE' });
    tudo.push(...linhas);
    const saida = tudo.join('\n');
    for (const segredo of [codigo, id.subject, hashHex(codigo)]) expect(saida.includes(segredo)).toBe(false);
    const admin = new URL(inject('urlAdmin')).username;
    expect((await eventos(id.subject)).map((e) => [e.action, e.database_user])).toEqual([
      ['concedido', admin],
      ['revogado', admin],
    ]);
  });

  it('banco que não é hml: 1; infraestrutura fora do ar: 3 só com códigos', async () => {
    expect(await rodar(args('revogar', randomUUID()).map((a) => (a === hml.banco ? dev.banco : a)))).toBe(1);
    expect(ultima()).toMatchObject({ resultado: 'recusado', codigo: 'AMBIENTE_PROIBIDO' });
    const url = new URL(inject('urlAdmin'));
    url.password = 'SenhaQueNaoPodeVazar123';
    url.port = '1';
    expect(await rodar(args('revogar', randomUUID()), '', { SAFRION_ADMIN_URL: url.toString() })).toBe(3);
    expect(ultima()).toMatchObject({ resultado: 'falha', codigo: 'FALHA_INFRAESTRUTURA' });
    expect(linhas.join('\n')).not.toContain('SenhaQueNaoPodeVazar123');
  });

  it('lê o código de uma entrada que não é terminal (pipe), até o fim da linha ou da entrada', async () => {
    const comLinha = new PassThrough();
    const lido = lerDaEntrada(comLinha as unknown as NodeJS.ReadStream);
    comLinha.write('abcde-fghjk\nresto');
    expect(await lido).toBe('abcde-fghjk');
    const semLinha = new PassThrough();
    const lido2 = lerDaEntrada(semLinha as unknown as NodeJS.ReadStream);
    semLinha.end('ABCDEFGHJK');
    expect(await lido2).toBe('ABCDEFGHJK');
  });
});

describe('demo:reset em hml', () => {
  it('revoga o acesso real da geração anterior, com evento e sessões; nada passa para a geração nova', async () => {
    const id = identidade();
    expect(await conceder(await pedir(id), papelDe('almoxarife'))).toBe('concedido');
    const token = await entrar(id, 'almoxarife');
    expect(await resolverSessao(hml.app, token ?? undefined)).not.toBeNull();
    const anterior = demo.organizationId;
    demo = await restaurarDemonstracao(hml.app, { confirmar: 'hml', ambienteDoProcesso: 'hml' });
    expect(demo.organizationId).not.toBe(anterior);
    expect(await vinculos(id.subject)).toEqual([]);
    expect((await eventos(id.subject)).at(-1)).toMatchObject({
      action: 'revogado',
      responsible: 'demo:reset',
      reason: 'demo_reset',
    });
    expect(await resolverSessao(hml.app, token ?? undefined)).toBeNull();
    expect(await entrar(id, 'almoxarife')).toBeNull();
    // O login sintético de DEV segue na geração nova, e em dev a função não faz nada.
    const sintetico = await raiz.query('SELECT organization_id FROM app.identity_link WHERE issuer = $1', [
      DEV,
    ]);
    expect(
      sintetico.rows.every((r: { organization_id: string }) => r.organization_id === demo.organizationId),
    ).toBe(true);
    const emDev = await dev.app.query<{ n: number }>('SELECT app.revogar_vinculos_demonstracao($1) AS n', [
      randomUUID(),
    ]);
    expect(emDev.rows[0]?.n).toBe(0);
  });
});
