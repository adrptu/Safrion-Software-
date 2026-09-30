import { randomUUID } from 'node:crypto';

import { canonizarRecebimento, type DadosRecebimento } from '@safrion/contracts';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { consultarIntencao, executarComando, type Efeito, type Recibo } from '../src/comando.js';
import {
  COMANDO_RECEBER_DOCUMENTO,
  documento,
  listarDocumentos,
  receberDocumento,
} from '../src/recebimento.js';
import { emOrganizacao } from '../src/sessao.js';
import { contagens, criarBanco, semear, type Ambiente, type Semente } from './ambiente.js';

// Leitura do documento de entrada e consulta do recibo por chave (contrato CMD-15 v3.5, §6.1) em PostgreSQL real, pelo
// app_runtime sem BYPASSRLS. Os documentos são gravados pelo efeito já fechado; os valores esperados vêm do que foi
// enviado, escritos à mão.
let amb: Ambiente;
let a: Semente;
let b: Semente;
const ref = {
  fornecedor: randomUUID(),
  fungicida: randomUUID(),
  galao: randomUUID(),
  diesel: randomUUID(),
  colega: randomUUID(),
};

beforeAll(async () => {
  amb = await criarBanco();
  a = await semear(amb.app, 'A');
  b = await semear(amb.app, 'B');
  await emOrganizacao(amb.app, a.org, async (c) => {
    await c.query(
      "INSERT INTO app.counterparty (id, organization_id, name, identification) VALUES ($1, $2, 'Fornecedor Teste Ltda', '11222333000181')",
      [ref.fornecedor, a.org],
    );
    await c.query(
      "INSERT INTO app.product (id, organization_id, name, base_unit) VALUES ($1, $2, 'Fungicida A', 'L')",
      [ref.fungicida, a.org],
    );
    await c.query(
      "INSERT INTO app.packaging_conversion (id, organization_id, product_id, packaging, factor, version) VALUES ($1, $2, $3, 'galão 5 L', 5, 1)",
      [ref.galao, a.org, ref.fungicida],
    );
    await c.query(
      `INSERT INTO app.product (id, organization_id, name, base_unit, expiry_policy, lot_policy)
       VALUES ($1, $2, 'Diesel S10', 'L', 'nao_se_aplica', 'por_documento')`,
      [ref.diesel, a.org],
    );
    await c.query(
      "INSERT INTO app.app_user (id, organization_id, name, email) VALUES ($1, $2, 'Colega A', 'colega@a.invalid')",
      [ref.colega, a.org],
    );
  });
});
afterAll(async () => {
  await amb.encerrar();
});

type LinhaDados = DadosRecebimento['linhas'][number];
const dados = (
  numero: string,
  linhas: LinhaDados[],
  extra: Partial<DadosRecebimento> = {},
): DadosRecebimento => ({
  emitente: ref.fornecedor,
  tipo: 'nfe',
  serie: '1',
  numero,
  emissao: '2026-09-29',
  recebimento: '2026-09-30',
  fazenda: a.fazenda,
  linhas,
  ...extra,
});

/** Linhas: avaria em embalagem, inspeção em litros, diesel a granel sem validade e produto diferente. */
const quatroLinhas = (): LinhaDados[] => [
  {
    numero: 1,
    produto: ref.fungicida,
    lote: { codigo: 'F26-L1' },
    validade: '2027-06-30',
    local: a.local,
    unidade: { tipo: 'embalagem', conversao: ref.galao, versao: 1 },
    documento: '3',
    parcelas: { apto: '2', quarentena: '0', bloqueado: '1', recusado: '0' },
    motivo: 'avaria',
    pedidoLinha: 'PC-1/1',
    valorUnitario: '152.5',
  },
  {
    numero: 2,
    produto: ref.fungicida,
    lote: { codigo: 'F26-L2' },
    validade: '2027-06-30',
    local: a.local,
    unidade: { tipo: 'medida', unidade: 'L' },
    documento: '10',
    parcelas: { apto: '8', quarentena: '2', bloqueado: '0', recusado: '0' },
    inspecao: { responsavel: ref.colega, prazo: '2026-10-03' },
  },
  {
    numero: 3,
    produto: ref.diesel,
    lote: { interno: true },
    validade: null,
    local: a.local,
    unidade: { tipo: 'medida', unidade: 'L' },
    documento: '500',
    parcelas: { apto: '500', quarentena: '0', bloqueado: '0', recusado: '0' },
  },
  {
    numero: 4,
    produto: ref.fungicida,
    lote: { codigo: 'F26-L4' },
    validade: '2027-06-30',
    local: a.local,
    unidade: { tipo: 'medida', unidade: 'L' },
    documento: '2',
    parcelas: { apto: '0', quarentena: '0', bloqueado: '0', recusado: '0' },
    motivo: 'produto_diferente',
    ocorrencia: {
      produtoReal: { descricao: 'Fungicida B, tambor' },
      quantidade: '1',
      unidade: 'tambor 200 L',
      destino: 'retido_para_decisao',
      responsavel: a.usuario,
      prazo: '2026-10-02',
    },
  },
];

function receber(
  s: Semente,
  chave: string,
  docId: string,
  d: DadosRecebimento,
  envolver: (e: Efeito) => Efeito = (e) => e,
): Promise<Recibo> {
  const canonico = canonizarRecebimento(d);
  return executarComando(
    amb.app,
    s.org,
    {
      commandType: COMANDO_RECEBER_DOCUMENTO,
      idempotencyKey: chave,
      initiatorKind: 'web',
      actorId: s.usuario,
      target: { type: 'receipt_document', id: docId, expectedVersion: 0 },
      data: canonico,
      correlationId: `corr-${chave}`,
    },
    envolver(receberDocumento(canonico)),
  );
}

const consulta = (s: Semente, chave: string, actorId: string | null = s.usuario) =>
  emOrganizacao(amb.app, s.org, (c) =>
    consultarIntencao(c, { commandType: COMANDO_RECEBER_DOCUMENTO, idempotencyKey: chave, actorId }),
  );

describe('leitura do documento de entrada', () => {
  let doc: string;
  let original: Recibo;

  beforeAll(async () => {
    doc = randomUUID();
    original = await receber(
      a,
      'leitura-1',
      doc,
      dados('5001', quatroLinhas(), { pedido: { sistema: 'erp', referencia: 'PC-1' } }),
    );
    expect(original.outcome).toBe('confirmed');
  });

  it('lista com origem, fazenda e contagens de linhas, divergências, inspeções e ocorrências abertas', async () => {
    const lista = await emOrganizacao(amb.app, a.org, (c) => listarDocumentos(c));
    expect(lista).toHaveLength(1);
    expect(lista[0]?.registradoEm).toMatch(/^\d{4}-\d{2}-\d{2}T/);
    expect(lista[0]).toMatchObject({
      id: doc,
      emitente: { id: ref.fornecedor, nome: 'Fornecedor Teste Ltda', identificacao: '11222333000181' },
      tipo: 'nfe',
      serie: '1',
      numero: '5001',
      emissao: '2026-09-29',
      recebimento: '2026-09-30',
      fazenda: { id: a.fazenda, nome: 'Sede' },
      status: 'confirmado',
      versao: 1,
      contagens: { linhas: 4, divergencias: 2, inspecoes: 1, ocorrenciasAbertas: 1 },
    });
  });

  it('detalhe com parcelas, divergência, inspeção, granel sem validade, ocorrência, movimentos e o mesmo recibo', async () => {
    const d = await emOrganizacao(amb.app, a.org, (c) => documento(c, doc));
    expect(d).not.toBeNull();
    if (!d) return;
    expect(d.pedido).toEqual({ sistema: 'erp', referencia: 'PC-1' });
    expect(d.autor).toEqual({ id: a.usuario, nome: 'Almoxarife A' });
    // O recibo do detalhe é o do envelope, igual ao original exceto alreadyReceived.
    expect(d.recibo).toEqual({ ...original, alreadyReceived: true });
    expect(d.linhas.map((l) => l.numero)).toEqual([1, 2, 3, 4]);
    const [l1, l2, l3, l4] = d.linhas;
    expect(l1).toMatchObject({
      produto: { id: ref.fungicida, nome: 'Fungicida A' },
      lote: { codigo: 'F26-L1', tipo: 'fabricante', validade: '2027-06-30' },
      local: { id: a.local, nome: 'Almoxarifado' },
      documento: '3',
      unidade: 'galão 5 L',
      conversao: { id: ref.galao, versao: 1 },
      parcelas: { apto: '2', quarentena: '0', bloqueado: '1', recusado: '0' },
      divergencia: { motivo: 'avaria', texto: null },
      inspecao: null,
      pedidoLinha: 'PC-1/1',
      valorUnitario: '152.5',
    });
    expect(l2).toMatchObject({
      unidade: 'L',
      conversao: null,
      parcelas: { apto: '8', quarentena: '2', bloqueado: '0', recusado: '0' },
      divergencia: null,
      inspecao: { responsavel: { id: ref.colega, nome: 'Colega A' }, prazo: '2026-10-03' },
      pedidoLinha: null,
      valorUnitario: null,
    });
    expect(l3).toMatchObject({
      produto: { id: ref.diesel, nome: 'Diesel S10' },
      lote: { codigo: `DOC:${doc}`, tipo: 'agrupamento_interno', validade: null },
      documento: '500',
      parcelas: { apto: '500', quarentena: '0', bloqueado: '0', recusado: '0' },
    });
    expect(l4).toMatchObject({ divergencia: { motivo: 'produto_diferente', texto: null }, movimentos: [] });
    // Vínculo com o extrato: os movimentos de cada linha, na ordem das versões do lote.
    const gravados = await emOrganizacao(amb.app, a.org, (c) =>
      c.query<{ receipt_line_id: string; id: string }>(
        'SELECT receipt_line_id, id::text AS id FROM app.stock_movement WHERE receipt_line_id IS NOT NULL ORDER BY lot_version, intent_item',
      ),
    );
    for (const l of d.linhas) {
      expect(l.movimentos).toEqual(gravados.rows.filter((m) => m.receipt_line_id === l.id).map((m) => m.id));
    }
    expect(d.linhas.map((l) => l.movimentos.length)).toEqual([2, 2, 1, 0]);
    expect(d.ocorrencias).toHaveLength(1);
    expect(d.ocorrencias[0]?.registradaEm).toMatch(/^\d{4}-\d{2}-\d{2}T/);
    expect(d.ocorrencias).toMatchObject([
      {
        linha: { id: l4?.id, numero: 4 },
        produtoReal: { descricao: 'Fungicida B, tambor' },
        quantidade: '1',
        unidade: 'tambor 200 L',
        destino: 'retido_para_decisao',
        status: 'aberta',
        responsavel: { id: a.usuario, nome: 'Almoxarife A' },
        prazo: '2026-10-02',
      },
    ]);
  });

  it('outra organização não vê lista, detalhe nem recibo; id ou chave fora do formato dão vazio, sem erro do banco', async () => {
    await emOrganizacao(amb.app, b.org, async (c) => {
      expect(await listarDocumentos(c)).toEqual([]);
      expect(await documento(c, doc)).toBeNull();
      const chaveDeA = { commandType: COMANDO_RECEBER_DOCUMENTO, idempotencyKey: 'leitura-1' };
      expect(await consultarIntencao(c, { ...chaveDeA, actorId: b.usuario })).toBeNull();
      expect(await consultarIntencao(c, { ...chaveDeA, actorId: null })).toBeNull();
    });
    await emOrganizacao(amb.app, a.org, async (c) => {
      expect(await documento(c, randomUUID())).toBeNull();
      expect(await documento(c, 'nao-e-uuid')).toBeNull();
      expect(await documento(c, "' OR 1=1 --")).toBeNull();
      const base = {
        commandType: COMANDO_RECEBER_DOCUMENTO,
        idempotencyKey: 'leitura-1',
        actorId: a.usuario,
      };
      expect(await consultarIntencao(c, { ...base, actorId: 'x' })).toBeNull();
      expect(await consultarIntencao(c, { ...base, idempotencyKey: '' })).toBeNull();
      expect(await consultarIntencao(c, { ...base, idempotencyKey: 'k'.repeat(129) })).toBeNull();
      expect(await consultarIntencao(c, { ...base, commandType: 'estoque.outro' })).toBeNull();
    });
  });

  it('a consulta devolve o recibo só a quem enviou; de outro autor da organização é igual a ausente', async () => {
    expect(await consulta(a, 'leitura-1')).toEqual({ ...original, alreadyReceived: true });
    expect(await consulta(a, 'leitura-1', ref.colega)).toBeNull();
    expect(await consulta(a, 'chave-que-nunca-existiu')).toBeNull();
  });

  it('ler e consultar não grava intenção, auditoria, outbox nem movimento', async () => {
    const antes = await contagens(amb.app, a.org);
    await emOrganizacao(amb.app, a.org, async (c) => {
      await listarDocumentos(c);
      await documento(c, doc);
      await consultarIntencao(c, {
        commandType: COMANDO_RECEBER_DOCUMENTO,
        idempotencyKey: 'leitura-1',
        actorId: a.usuario,
      });
    });
    expect(await contagens(amb.app, a.org)).toEqual(antes);
  });

  it('recibo de rejeição também é recuperado pela chave, igual ao original', async () => {
    const rejeitado = await receber(a, 'leitura-dup', randomUUID(), dados('5001', quatroLinhas()));
    expect(rejeitado).toMatchObject({ outcome: 'rejected', reasonCode: 'DOCUMENTO_JA_RECEBIDO' });
    expect(await consulta(a, 'leitura-dup')).toEqual({ ...rejeitado, alreadyReceived: true });
  });
});

describe('consulta por chave com a intenção ainda na transação de outra conexão', () => {
  it('"ainda não localizado" antes do COMMIT; depois dele, o recibo gravado', async () => {
    let liberar: () => void = () => undefined;
    const retido = new Promise<void>((r) => {
      liberar = r;
    });
    let noEfeito: () => void = () => undefined;
    const chegou = new Promise<void>((r) => {
      noEfeito = r;
    });
    const envio = receber(
      a,
      'leitura-retida',
      randomUUID(),
      dados('5002', [quatroLinhas()[1] as LinhaDados]),
      (e) => async (c, ctx) => {
        const r = await e(c, ctx);
        noEfeito();
        await retido;
        return r;
      },
    );
    await chegou;
    expect(await consulta(a, 'leitura-retida')).toBeNull();
    liberar();
    const recibo = await envio;
    expect(recibo.outcome).toBe('confirmed');
    expect(await consulta(a, 'leitura-retida')).toEqual({ ...recibo, alreadyReceived: true });
  });
});
