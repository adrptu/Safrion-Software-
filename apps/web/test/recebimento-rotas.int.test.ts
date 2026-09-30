// Borda HTTP do recebimento por documento e do GET de recibo (contrato CMD-15 v3.6, §6.2), chamada por Request real
// com banco real identificado como dev, demonstração restaurada e login de DEV pelo mesmo fluxo da homologação.
import { randomUUID } from 'node:crypto';

import {
  EsquemaErro,
  EsquemaRecibo,
  canonizarRecebimento,
  criarRegistrador,
  type DadosRecebimento,
} from '@safrion/contracts';
import {
  COMANDO_RECEBER_DOCUMENTO,
  definirIdentidadeAmbiente,
  emOrganizacao,
  executarComando,
  receberDocumento,
  restaurarDemonstracao,
  type Demonstracao,
} from '@safrion/db';
import pg from 'pg';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import {
  contagens,
  criarBanco,
  semear,
  type Ambiente,
  type Semente,
} from '../../../packages/db/test/ambiente';
import { criarRotaComandos } from '../src/rotas/comandos';
import { criarRotasEntrar } from '../src/rotas/entrar';
import { criarRotaIntencoes } from '../src/rotas/intencoes';
import { COOKIE_LOGIN, COOKIE_SESSAO } from '../src/seguranca/cookies';

const ORIGEM = 'http://localhost:3000';
const TIPO = COMANDO_RECEBER_DOCUMENTO;
let amb: Ambiente;
let demo: Demonstracao;
let b: Semente;
const ids = { produto: '', fazenda: '', local: '', fornecedor: randomUUID(), fornecedorB: randomUUID() };
let almoxarife: string;
let gerente: string;

const registrador = criarRegistrador({
  servico: 'web-teste',
  versao: '0.0.0-teste',
  escrever: () => undefined,
  agora: () => '2026-09-30T12:00:00.000Z',
});
const deps = () => ({
  banco: amb.app,
  origem: ORIGEM,
  registrador,
  ambienteDoProcesso: 'dev',
  versao: '0.0.0-teste',
  commit: 'abc1234',
});
const entrar = criarRotasEntrar(deps);
const comandos = criarRotaComandos(deps);
const intencoes = criarRotaIntencoes(deps);

function cookieDe(resposta: Response, nome: string): string | undefined {
  const linha = resposta.headers.getSetCookie().find((c) => c.startsWith(`${nome}=`));
  const valor = linha?.slice(nome.length + 1).split(';')[0];
  return valor === '' ? undefined : valor;
}

/** Login de DEV completo pelo fluxo da homologação; devolve o token da sessão. */
async function loginDev(usuario: 'demo-almoxarife' | 'demo-gerente'): Promise<string> {
  const inicio = await entrar.iniciar(new Request(`${ORIGEM}/entrar/iniciar?destino=%2Festoque`));
  const state = new URL(inicio.headers.get('location') ?? '').searchParams.get('state') ?? '';
  const autorizado = await entrar.autorizarDesenvolvimento(
    new Request(`${ORIGEM}/entrar/desenvolvimento/autorizar`, {
      method: 'POST',
      body: new URLSearchParams({ state, usuario }).toString(),
      headers: { 'content-type': 'application/x-www-form-urlencoded', origin: ORIGEM },
    }),
  );
  const retorno = await entrar.retorno(
    new Request(autorizado.headers.get('location') ?? '', {
      headers: { cookie: `${COOKIE_LOGIN}=${cookieDe(inicio, COOKIE_LOGIN) ?? ''}` },
    }),
  );
  const sessao = cookieDe(retorno, COOKIE_SESSAO);
  if (!sessao) throw new Error('login de DEV não criou sessão');
  return sessao;
}

function post(corpo: unknown, sessao?: string, extra: Record<string, string> = {}, tipo: string = TIPO) {
  return comandos(
    new Request(`${ORIGEM}/api/v1/comandos/${tipo}`, {
      method: 'POST',
      body: typeof corpo === 'string' ? corpo : JSON.stringify(corpo),
      headers: {
        'content-type': 'application/json',
        origin: ORIGEM,
        ...(sessao ? { cookie: `${COOKIE_SESSAO}=${sessao}` } : {}),
        ...extra,
      },
    }),
    { params: Promise.resolve({ commandType: tipo }) },
  );
}

function get(
  chave: string,
  sessao?: string,
  extra: Record<string, string> = {},
  tipo: string = TIPO,
  query = '',
) {
  return intencoes(
    new Request(`${ORIGEM}/api/v1/intencoes/${tipo}/${encodeURIComponent(chave)}${query}`, {
      headers: { ...(sessao ? { cookie: `${COOKIE_SESSAO}=${sessao}` } : {}), ...extra },
    }),
    { params: Promise.resolve({ commandType: tipo, chave }) },
  );
}

const reciboDe = async (r: Response) => EsquemaRecibo.parse(await r.json());
const erroDe = async (r: Response) => EsquemaErro.parse(await r.json());

type LinhaDados = DadosRecebimento['linhas'][number];
const linha = (numero: number, extra: Partial<LinhaDados> = {}): LinhaDados => ({
  numero,
  produto: ids.produto,
  lote: { codigo: 'NF-HTTP-1' },
  validade: '2027-06-30',
  local: ids.local,
  unidade: { tipo: 'medida', unidade: 'L' },
  documento: '10',
  parcelas: { apto: '10', quarentena: '0', bloqueado: '0', recusado: '0' },
  ...extra,
});
const dados = (numero: string, linhas: LinhaDados[] = [linha(1)]): DadosRecebimento => ({
  emitente: ids.fornecedor,
  tipo: 'nfe',
  serie: '1',
  numero,
  emissao: '2026-09-29',
  recebimento: '2026-09-30',
  fazenda: ids.fazenda,
  linhas,
});
const pedido = (chave: string, d: unknown, alvo: Record<string, unknown> = {}) => ({
  idempotencyKey: chave,
  target: { type: 'receipt_document', id: randomUUID(), expectedVersion: 0, ...alvo },
  data: d,
});

beforeAll(async () => {
  amb = await criarBanco();
  const mig = new pg.Client({ connectionString: amb.url('migrator') });
  await mig.connect();
  try {
    await definirIdentidadeAmbiente(mig, 'dev');
  } finally {
    await mig.end();
  }
  demo = await restaurarDemonstracao(amb.app, { confirmar: 'dev', ambienteDoProcesso: 'dev' });
  b = await semear(amb.app, 'B');
  await emOrganizacao(amb.app, demo.organizationId, async (c) => {
    const lote = await c.query<{ product_id: string }>('SELECT product_id FROM app.lot WHERE id = $1', [
      demo.loteId,
    ]);
    const local = await c.query<{ id: string; farm_id: string }>(
      'SELECT id, farm_id FROM app.stock_location',
    );
    ids.produto = lote.rows[0]?.product_id ?? '';
    ids.local = local.rows[0]?.id ?? '';
    ids.fazenda = local.rows[0]?.farm_id ?? '';
    await c.query(
      "INSERT INTO app.counterparty (id, organization_id, name, identification) VALUES ($1, $2, 'Fornecedor fictício', '11222333000181')",
      [ids.fornecedor, demo.organizationId],
    );
  });
  await emOrganizacao(amb.app, b.org, (c) =>
    c.query(
      "INSERT INTO app.counterparty (id, organization_id, name, identification) VALUES ($1, $2, 'Fornecedor B', '99')",
      [ids.fornecedorB, b.org],
    ),
  );
  almoxarife = await loginDev('demo-almoxarife');
  gerente = await loginDev('demo-gerente');
});
afterAll(async () => {
  await amb.encerrar();
});

describe('POST estoque.receber-documento pela fábrica de comandos', () => {
  it('almoxarife recebe; o GET da chave devolve o mesmo recibo; "10" e "10.0" são o mesmo conteúdo', async () => {
    const corpo = pedido('http-1', dados('7001'));
    const r = await post(corpo, almoxarife);
    expect(r.status).toBe(200);
    expect(r.headers.get('cache-control')).toBe('no-store');
    const recibo = await reciboDe(r);
    expect(recibo).toMatchObject({
      outcome: 'confirmed',
      targetType: 'receipt_document',
      alreadyReceived: false,
    });

    const consulta = await get('http-1', almoxarife);
    expect(consulta.status).toBe(200);
    expect(consulta.headers.get('cache-control')).toBe('no-store');
    expect(await reciboDe(consulta)).toEqual({ ...recibo, alreadyReceived: true });

    const decimalOutro = {
      ...corpo,
      data: dados('7001', [
        linha(1, {
          documento: '10.0',
          parcelas: { apto: '10.00', quarentena: '0', bloqueado: '0', recusado: '0' },
        }),
      ]),
    };
    const reenvio = await post(decimalOutro, almoxarife);
    expect(reenvio.status).toBe(200);
    expect(await reciboDe(reenvio)).toEqual({ ...recibo, alreadyReceived: true });

    const outroConteudo = await post(
      {
        ...corpo,
        data: dados('7001', [
          linha(1, {
            documento: '11',
            parcelas: { apto: '11', quarentena: '0', bloqueado: '0', recusado: '0' },
          }),
        ]),
      },
      almoxarife,
    );
    expect(outroConteudo.status).toBe(409);
    expect((await erroDe(outroConteudo)).codigo).toBe('IDEMPOTENCY_KEY_REUSED');
  });

  it('rejeição registrada volta 422 e o GET da chave devolve a mesma rejeição', async () => {
    const r = await post(pedido('http-dup', dados('7001')), almoxarife);
    expect(r.status).toBe(422);
    const recibo = await reciboDe(r);
    expect(recibo).toMatchObject({ outcome: 'rejected', reasonCode: 'DOCUMENTO_JA_RECEBIDO' });
    const consulta = await get('http-dup', almoxarife);
    expect(consulta.status).toBe(422);
    expect(await reciboDe(consulta)).toEqual({ ...recibo, alreadyReceived: true });
  });

  it('cadastro de outra organização no corpo é rejeitado como inexistente', async () => {
    const r = await post(pedido('http-b', dados('7002', [linha(1, { produto: b.produto })])), almoxarife);
    expect(r.status).toBe(422);
    expect(await reciboDe(r)).toMatchObject({ outcome: 'rejected', reasonCode: 'PRODUTO_NAO_ENCONTRADO' });
  });

  it('contrato: alvo, versão, campos de ator/organização e dados inválidos são 400 sem gravar nada', async () => {
    const antes = await contagens(amb.app, demo.organizationId);
    const casos: [string, unknown][] = [
      ['alvo de outro tipo', pedido(randomUUID(), dados('7003'), { type: 'lot' })],
      ['versão diferente de 0', pedido(randomUUID(), dados('7003'), { expectedVersion: 1 })],
      ['ator no pedido', { ...pedido(randomUUID(), dados('7003')), actorId: randomUUID() }],
      ['organização no pedido', { ...pedido(randomUUID(), dados('7003')), organizationId: b.org }],
      ['organização nos dados', pedido(randomUUID(), { ...dados('7003'), organizationId: b.org })],
      [
        'movimento livre nos dados',
        pedido(randomUUID(), { lote: demo.loteId, local: ids.local, movimento: {} }),
      ],
      ['sem linhas', pedido(randomUUID(), dados('7003', []))],
    ];
    for (const [nome, corpo] of casos) {
      const r = await post(corpo, almoxarife);
      expect(r.status, nome).toBe(400);
      expect((await erroDe(r)).codigo, nome).toBe('CONTRATO_INVALIDO');
    }
    expect(await contagens(amb.app, demo.organizationId)).toEqual(antes);
  });

  it('limite por comando antes do parse: documento aceita mais de 16 KiB e recusa mais de 64 KiB; o legado segue em 16 KiB', async () => {
    const cinquenta = Array.from({ length: 50 }, (_, i) =>
      linha(i + 1, {
        lote: { codigo: 'NF-HTTP-50' },
        pedidoLinha: `PEDIDO-${String(i + 1).padStart(56, '0')}`,
      }),
    );
    const grande = JSON.stringify(pedido('http-50', dados('7004', cinquenta)));
    expect(new TextEncoder().encode(grande).byteLength).toBeGreaterThan(16 * 1024);
    const aceito = await post(grande, almoxarife);
    expect(aceito.status).toBe(200);

    const demais = await post(`{"x":"${'a'.repeat(64 * 1024)}"}`, almoxarife);
    expect(demais.status).toBe(413);
    const legado = await post(
      `{"x":"${'a'.repeat(17 * 1024)}"}`,
      almoxarife,
      {},
      'estoque.registrar-entrada',
    );
    expect(legado.status).toBe(413);
  });

  it('gerente não recebe documento (403) e nada é gravado; sem sessão é 401; Origin de fora é 403', async () => {
    const antes = await contagens(amb.app, demo.organizationId);
    const r = await post(pedido(randomUUID(), dados('7005')), gerente);
    expect(r.status).toBe(403);
    expect((await erroDe(r)).codigo).toBe('SEM_PERMISSAO');
    expect((await post(pedido(randomUUID(), dados('7005')))).status).toBe(401);
    expect(
      (await post(pedido(randomUUID(), dados('7005')), almoxarife, { origin: 'https://evil.example' }))
        .status,
    ).toBe(403);
    expect(await contagens(amb.app, demo.organizationId)).toEqual(antes);
  });
});

describe('GET /api/v1/intencoes/{commandType}/{chave}', () => {
  it('sem recibo visível: 404 RECIBO_NAO_LOCALIZADO, "ainda não localizado", nunca "não recebido", sem gravar', async () => {
    const antes = await contagens(amb.app, demo.organizationId);
    const r = await get('chave-que-nunca-existiu', almoxarife);
    expect(r.status).toBe(404);
    expect(r.headers.get('cache-control')).toBe('no-store');
    expect(r.headers.get('x-correlation-id')).toBeTruthy();
    const e = await erroDe(r);
    expect(e.codigo).toBe('RECIBO_NAO_LOCALIZADO');
    expect(e.mensagem).toContain('ainda não localizado');
    expect(e.mensagem).not.toMatch(/não recebido|em processamento/);
    expect(await contagens(amb.app, demo.organizationId)).toEqual(antes);
  });

  it('chave de outra organização não aparece; a mesma chave na própria organização é outro recibo', async () => {
    const canonico = canonizarRecebimento({
      ...dados('8001', [linha(1, { produto: b.produto, local: b.local })]),
      emitente: ids.fornecedorB,
      fazenda: b.fazenda,
    });
    const deB = await executarComando(
      amb.app,
      b.org,
      {
        commandType: TIPO,
        idempotencyKey: 'chave-cruzada',
        initiatorKind: 'web',
        actorId: b.usuario,
        target: { type: 'receipt_document', id: randomUUID(), expectedVersion: 0 },
        data: canonico,
        correlationId: 'corr-cruzada',
      },
      receberDocumento(canonico),
    );
    expect(deB.outcome).toBe('confirmed');
    expect((await get('chave-cruzada', almoxarife)).status).toBe(404);
    const propria = await post(pedido('chave-cruzada', dados('7006')), almoxarife);
    expect(propria.status).toBe(200);
    const recibo = await reciboDe(propria);
    expect(recibo.receiptId).not.toBe(deB.receiptId);
    expect(await reciboDe(await get('chave-cruzada', almoxarife))).toEqual({
      ...recibo,
      alreadyReceived: true,
    });
  });

  it('o autor vem da sessão: a chave de outro usuário da mesma organização é igual a ausente', async () => {
    const outro = demo.usuarios.find((u) => u.papel === 'gerente')?.usuarioId ?? '';
    const canonico = canonizarRecebimento(dados('7007'));
    const deOutro = await executarComando(
      amb.app,
      demo.organizationId,
      {
        commandType: TIPO,
        idempotencyKey: 'chave-de-outro-autor',
        initiatorKind: 'web',
        actorId: outro,
        target: { type: 'receipt_document', id: randomUUID(), expectedVersion: 0 },
        data: canonico,
        correlationId: 'corr-outro-autor',
      },
      receberDocumento(canonico),
    );
    expect(deOutro.outcome).toBe('confirmed');
    const r = await get('chave-de-outro-autor', almoxarife);
    expect(r.status).toBe(404);
    expect((await erroDe(r)).codigo).toBe('RECIBO_NAO_LOCALIZADO');
  });

  it('gerente não consulta chave de comando que não executa; sem sessão 401; comando desconhecido 404', async () => {
    const g = await get('http-1', gerente);
    expect(g.status).toBe(403);
    expect((await erroDe(g)).codigo).toBe('SEM_PERMISSAO');
    expect((await get('http-1')).status).toBe(401);
    const desconhecido = await get('http-1', almoxarife, {}, 'estoque.apagar-tudo');
    expect(desconhecido.status).toBe(404);
    expect((await erroDe(desconhecido)).codigo).toBe('NAO_ENCONTRADO');
  });

  it('autor e organização nunca vêm da requisição: query recusada; chave fora do limite recusada', async () => {
    for (const query of ['?actorId=', `?actorId=${randomUUID()}`, `?organizationId=${b.org}`, '?x=1']) {
      const r = await get('http-1', almoxarife, {}, TIPO, query);
      expect(r.status, query).toBe(400);
      expect((await erroDe(r)).codigo, query).toBe('CONTRATO_INVALIDO');
    }
    expect((await get('k'.repeat(129), almoxarife)).status).toBe(400);
    expect((await get('   ', almoxarife)).status).toBe(400);
  });

  it('requisição de outro site é recusada: Origin diferente ou Sec-Fetch-Site cross-site', async () => {
    expect((await get('http-1', almoxarife, { origin: 'https://evil.example' })).status).toBe(403);
    expect((await get('http-1', almoxarife, { 'sec-fetch-site': 'cross-site' })).status).toBe(403);
    expect((await get('http-1', almoxarife, { 'sec-fetch-site': 'same-site' })).status).toBe(403);
    expect(
      (await get('http-1', almoxarife, { origin: ORIGEM, 'sec-fetch-site': 'same-origin' })).status,
    ).toBe(200);
  });
});
