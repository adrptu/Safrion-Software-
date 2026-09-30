// Borda HTTP dos cadastros agrícolas, incremento 1 (contrato CAD-01 v3, §4 e §9): Request real, banco real
// identificado como dev, demonstração restaurada e login de DEV pelo mesmo fluxo da homologação.
import { randomUUID } from 'node:crypto';

import { COMANDOS_CADASTRO, EsquemaErro, EsquemaRecibo, criarRegistrador } from '@safrion/contracts';
import { definirIdentidadeAmbiente, restaurarDemonstracao, type Demonstracao } from '@safrion/db';
import pg from 'pg';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { criarBanco, type Ambiente } from '../../../packages/db/test/ambiente';
import { criarRotaComandos } from '../src/rotas/comandos';
import { criarRotasEntrar } from '../src/rotas/entrar';
import { COOKIE_LOGIN, COOKIE_SESSAO } from '../src/seguranca/cookies';

const ORIGEM = 'http://localhost:3000';
let amb: Ambiente;
let demo: Demonstracao;
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

function cookieDe(resposta: Response, nome: string): string | undefined {
  const linha = resposta.headers.getSetCookie().find((c) => c.startsWith(`${nome}=`));
  const valor = linha?.slice(nome.length + 1).split(';')[0];
  return valor === '' ? undefined : valor;
}

async function loginDev(usuario: 'demo-almoxarife' | 'demo-gerente'): Promise<string> {
  const inicio = await entrar.iniciar(new Request(`${ORIGEM}/entrar/iniciar?destino=%2Fcadastros%2Fareas`));
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

function post(tipo: string, corpo: unknown, sessao: string) {
  return comandos(
    new Request(`${ORIGEM}/api/v1/comandos/${tipo}`, {
      method: 'POST',
      body: typeof corpo === 'string' ? corpo : JSON.stringify(corpo),
      headers: { 'content-type': 'application/json', origin: ORIGEM, cookie: `${COOKIE_SESSAO}=${sessao}` },
    }),
    { params: Promise.resolve({ commandType: tipo }) },
  );
}

const pedido = (
  type: 'farm' | 'field',
  data: unknown,
  alvo: { id?: string; expectedVersion?: number } = {},
) => ({
  idempotencyKey: randomUUID(),
  target: { type, id: alvo.id ?? randomUUID(), expectedVersion: alvo.expectedVersion ?? 0 },
  data,
});
const reciboDe = async (r: Response) => EsquemaRecibo.parse(await r.json());
const erroDe = async (r: Response) => EsquemaErro.parse(await r.json());

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
  expect(demo.organizationId).toBeTruthy();
  almoxarife = await loginDev('demo-almoxarife');
  gerente = await loginDev('demo-gerente');
});
afterAll(async () => {
  await amb.encerrar();
});

describe('POST cadastros.* (contrato CAD-01 §4)', () => {
  it('o gerente cria a fazenda e o talhão nela (AC-72-12); o reenvio devolve o mesmo recibo', async () => {
    const fazenda = pedido('farm', { nome: 'Fazenda Boa Vista', fuso: 'America/Sao_Paulo' });
    const f = await post(COMANDOS_CADASTRO.criarFazenda, fazenda, gerente);
    expect(f.status).toBe(200);
    expect(await reciboDe(f)).toMatchObject({ outcome: 'confirmed', resultingVersion: 1 });

    const talhao = pedido('field', { fazenda: fazenda.target.id, nome: 'T1', areaDeclaradaHa: '204' });
    const t = await post(COMANDOS_CADASTRO.criarTalhao, talhao, gerente);
    expect(t.status).toBe(200);
    const recibo = await reciboDe(t);
    expect(recibo).toMatchObject({ outcome: 'confirmed', resultingVersion: 1 });
    // "204.0" e " T1 " são o mesmo conteúdo canônico: a mesma chave devolve o mesmo recibo.
    const reenvio = await post(
      COMANDOS_CADASTRO.criarTalhao,
      { ...talhao, data: { fazenda: fazenda.target.id, nome: ' T1 ', areaDeclaradaHa: '204.0' } },
      gerente,
    );
    expect(await reciboDe(reenvio)).toMatchObject({ receiptId: recibo.receiptId, alreadyReceived: true });

    const dup = await post(
      COMANDOS_CADASTRO.criarTalhao,
      pedido('field', { fazenda: fazenda.target.id, nome: 't1', areaDeclaradaHa: '1' }),
      gerente,
    );
    expect(dup.status).toBe(422);
    expect(await reciboDe(dup)).toMatchObject({ outcome: 'rejected', reasonCode: 'NOME_EM_USO' });

    const velho = await post(
      COMANDOS_CADASTRO.editarTalhao,
      pedido('field', { nome: 'T1 editado' }, { id: talhao.target.id, expectedVersion: 2 }),
      gerente,
    );
    expect(velho.status).toBe(409);
  });

  it('o almoxarife só consulta: 403 em todos os cadastros', async () => {
    for (const tipo of Object.values(COMANDOS_CADASTRO)) {
      const r = await post(tipo, pedido('farm', { nome: 'X', fuso: 'America/Sao_Paulo' }), almoxarife);
      expect(r.status, tipo).toBe(403);
      expect((await erroDe(r)).codigo, tipo).toBe('SEM_PERMISSAO');
    }
  });

  it('alvo ou dados fora do contrato são 400, sem gravar; corpo acima de 16 KiB é 413', async () => {
    const casos: [string, unknown][] = [
      [COMANDOS_CADASTRO.criarFazenda, pedido('field', { nome: 'Tipo errado', fuso: 'America/Sao_Paulo' })],
      [
        COMANDOS_CADASTRO.criarFazenda,
        pedido('farm', { nome: 'Versão 1', fuso: 'America/Sao_Paulo' }, { expectedVersion: 1 }),
      ],
      [COMANDOS_CADASTRO.editarTalhao, pedido('field', { nome: 'Versão 0' }, { expectedVersion: 0 })],
      [
        COMANDOS_CADASTRO.criarTalhao,
        pedido('field', { fazenda: randomUUID(), nome: 'pt-BR', areaDeclaradaHa: '1.204,5' }),
      ],
      [
        COMANDOS_CADASTRO.criarTalhao,
        pedido('field', { fazenda: randomUUID(), nome: 'Número', areaDeclaradaHa: 204 }),
      ],
      [COMANDOS_CADASTRO.criarFazenda, pedido('farm', { nome: 'Fuso', fuso: 'Brasil/Brasilia' })],
      [
        COMANDOS_CADASTRO.criarFazenda,
        pedido('farm', { nome: 'Extra', fuso: 'America/Sao_Paulo', organizationId: randomUUID() }),
      ],
      [COMANDOS_CADASTRO.editarTalhao, pedido('field', {}, { expectedVersion: 1 })],
    ];
    for (const [tipo, corpo] of casos) {
      const r = await post(tipo, corpo, gerente);
      expect(r.status, JSON.stringify(corpo)).toBe(400);
    }
    // Nome com NUL (achado do Codex, 30/09): 400 antes do envelope, sem recibo nem efeito; a mesma chave serve depois
    // para o pedido válido, porque a recusa de contrato não consome a chave.
    const nul = pedido('farm', { nome: 'Fazenda\u0000Nula', fuso: 'America/Sao_Paulo' });
    const recusada = await post(COMANDOS_CADASTRO.criarFazenda, nul, gerente);
    expect(recusada.status).toBe(400);
    expect((await erroDe(recusada)).codigo).toBe('CONTRATO_INVALIDO');
    const valida = await post(
      COMANDOS_CADASTRO.criarFazenda,
      { ...nul, data: { nome: 'Fazenda Nula Corrigida', fuso: 'America/Sao_Paulo' } },
      gerente,
    );
    expect(valida.status).toBe(200);
    expect(await reciboDe(valida)).toMatchObject({ outcome: 'confirmed', alreadyReceived: false });

    const grande = await post(COMANDOS_CADASTRO.criarFazenda, `{"x":"${'a'.repeat(17 * 1024)}"}`, gerente);
    expect(grande.status).toBe(413);
  });
});
