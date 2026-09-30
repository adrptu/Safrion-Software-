import { randomUUID } from 'node:crypto';

import { canonizarRecebimento, type DadosRecebimento } from '@safrion/contracts';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { executarComando, type Recibo } from '../src/comando.js';
import { COMANDO_RECEBER_DOCUMENTO, receberDocumento } from '../src/recebimento.js';
import { emOrganizacao } from '../src/sessao.js';
import { criarBanco, semear, type Ambiente, type Semente } from './ambiente.js';

// Efeito estoque.receber-documento (CMD-15, incremento 1; contrato CMD-15 v3.3) em PostgreSQL real, com app_runtime
// sem BYPASSRLS. Os caminhos recusados mostram que nada foi gravado além do registro da intenção.
let amb: Ambiente;
let a: Semente;
let b: Semente;
const ref = {
  fornecedor: randomUUID(),
  fungicida: randomUUID(),
  galao: randomUUID(),
  diesel: randomUUID(),
  semente: randomUUID(),
  outraFazenda: randomUUID(),
  localOutraFazenda: randomUUID(),
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
      "INSERT INTO app.product (id, organization_id, name, base_unit) VALUES ($1, $2, 'Semente', 'un')",
      [ref.semente, a.org],
    );
    await c.query("INSERT INTO app.farm (id, organization_id, name) VALUES ($1, $2, 'Outra fazenda')", [
      ref.outraFazenda,
      a.org,
    ]);
    await c.query(
      "INSERT INTO app.stock_location (id, organization_id, farm_id, name) VALUES ($1, $2, $3, 'Galpão')",
      [ref.localOutraFazenda, a.org, ref.outraFazenda],
    );
  });
});
afterAll(async () => {
  await amb.encerrar();
});

type LinhaDados = DadosRecebimento['linhas'][number];
const linha = (numero: number, extra: Partial<LinhaDados> = {}): LinhaDados => ({
  numero,
  produto: ref.fungicida,
  lote: { codigo: 'F26-10' },
  validade: '2027-06-30',
  local: a.local,
  unidade: { tipo: 'embalagem', conversao: ref.galao, versao: 1 },
  documento: '3',
  parcelas: { apto: '3', quarentena: '0', bloqueado: '0', recusado: '0' },
  ...extra,
});
const documento = (
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

function receber(s: Semente, chave: string, docId: string, dados: DadosRecebimento): Promise<Recibo> {
  const canonico = canonizarRecebimento(dados);
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
    receberDocumento(canonico),
  );
}

/** Contagem do que o recebimento grava, na organização. */
async function fatos(org: string): Promise<Record<string, number>> {
  return emOrganizacao(amb.app, org, async (c) => {
    const r = await c.query<{ t: string; n: string }>(
      `SELECT 'documentos' t, count(*)::text n FROM app.receipt_document
       UNION ALL SELECT 'linhas', count(*)::text FROM app.receipt_line
       UNION ALL SELECT 'ocorrencias', count(*)::text FROM app.receipt_occurrence
       UNION ALL SELECT 'lotes', count(*)::text FROM app.lot
       UNION ALL SELECT 'movimentos', count(*)::text FROM app.stock_movement
       UNION ALL SELECT 'outbox', count(*)::text FROM app.outbox`,
    );
    return Object.fromEntries(r.rows.map((l) => [l.t, Number(l.n)]));
  });
}

describe('receber documento: gravação atômica pelo envelope', () => {
  it('NF-TESTE-001: 3 galões de 5 L entram como 15 L, com trilha movimento → linha → documento', async () => {
    const doc = randomUUID();
    const r = await receber(
      a,
      'nf-001',
      doc,
      documento('1001', [linha(1)], { pedido: { sistema: 'erp', referencia: 'PC-1' } }),
    );
    expect(r).toMatchObject({
      outcome: 'confirmed',
      resultingVersion: 1,
      nextAction: 'Receber documento',
      pending: [],
    });
    await emOrganizacao(amb.app, a.org, async (c) => {
      const m = await c.query<Record<string, unknown>>(
        `SELECT m.original_quantity::text AS oq, m.original_unit AS ou, m.base_quantity::text AS bq, m.base_unit AS bu,
                m.conversion_id AS conv, m.conversion_version AS cv, m.lot_version AS lv, m.intent_item AS item,
                l.line_number AS linha, d.id AS doc, lt.code AS lote, lt.kind AS tipo, lt.version::text AS versao
           FROM app.stock_movement m JOIN app.receipt_line l ON l.id = m.receipt_line_id
           JOIN app.receipt_document d ON d.id = l.document_id JOIN app.lot lt ON lt.id = m.lot_id
          WHERE d.id = $1`,
        [doc],
      );
      expect(m.rows).toEqual([
        {
          oq: '3',
          ou: 'galão 5 L',
          bq: '15',
          bu: 'L',
          conv: ref.galao,
          cv: 1,
          lv: '1',
          item: 1,
          linha: 1,
          doc,
          lote: 'F26-10',
          tipo: 'fabricante',
          versao: '1',
        },
      ]);
      const eventos = await c.query<{ type: string }>(
        'SELECT type FROM app.outbox WHERE causation_id = $1 ORDER BY type',
        ['nf-001'],
      );
      expect(eventos.rows.map((e) => e.type)).toEqual([
        'estoque.movimento_registrado',
        'estoque.recebimento_confirmado',
      ]);
    });
  });

  it('a mesma intenção devolve o mesmo recibo, sem efeito novo; "3" e "3.0" são o mesmo conteúdo', async () => {
    const doc = randomUUID();
    const primeiro = await receber(
      a,
      'nf-002',
      doc,
      documento('1002', [linha(1, { lote: { codigo: 'F26-11' } })]),
    );
    const antes = await fatos(a.org);
    const de_novo = await receber(
      a,
      'nf-002',
      doc,
      documento('1002', [
        linha(1, {
          lote: { codigo: 'F26-11' },
          documento: '3.0',
          parcelas: { apto: '3.0', quarentena: '0', bloqueado: '0', recusado: '0' },
        }),
      ]),
    );
    expect(de_novo).toMatchObject({
      receiptId: primeiro.receiptId,
      alreadyReceived: true,
      outcome: 'confirmed',
    });
    expect(await fatos(a.org)).toEqual(antes);
  });

  it('outra chave com a mesma origem (NF relançada) é recusada sem efeito; série e número normalizados contam', async () => {
    await receber(a, 'nf-003', randomUUID(), documento('1003', [linha(1, { lote: { codigo: 'F26-12' } })]));
    const antes = await fatos(a.org);
    const r = await receber(
      a,
      'nf-003-outra',
      randomUUID(),
      documento('0001003', [linha(1, { lote: { codigo: 'F26-12' } })], { serie: ' 01 ' }),
    );
    expect(r).toMatchObject({ outcome: 'rejected', reasonCode: 'DOCUMENTO_JA_RECEBIDO' });
    expect(await fatos(a.org)).toEqual(antes);
  });

  it('falha numa linha posterior desfaz a intenção inteira: nem documento, nem lote novo da linha 1', async () => {
    const antes = await fatos(a.org);
    const r = await receber(
      a,
      'nf-004',
      randomUUID(),
      documento('1004', [
        linha(1, { lote: { codigo: 'NOVO-1004' } }),
        linha(2, { lote: { codigo: 'NOVO-1004B' }, local: ref.localOutraFazenda }),
      ]),
    );
    expect(r).toMatchObject({ outcome: 'rejected', reasonCode: 'LOCAL_FORA_DA_FAZENDA' });
    expect(await fatos(a.org)).toEqual(antes);
    // Falha que só aparece no banco depois da linha 1 gravada: unidade incompatível com o lote (kg num produto em L).
    const r2 = await receber(
      a,
      'nf-004b',
      randomUUID(),
      documento('1004', [
        linha(1, { lote: { codigo: 'NOVO-1004' } }),
        linha(2, {
          lote: { codigo: 'NOVO-1004B' },
          unidade: { tipo: 'medida', unidade: 'kg' },
          documento: '5',
          parcelas: { apto: '5', quarentena: '0', bloqueado: '0', recusado: '0' },
        }),
      ]),
    );
    expect(r2).toMatchObject({ outcome: 'rejected', reasonCode: 'UNIDADE_INCOMPATIVEL' });
    expect(await fatos(a.org)).toEqual(antes);
  });

  it('produto, conversão, local e emitente de outra organização não passam, como inexistentes', async () => {
    const antes = await fatos(b.org);
    const deB = (extra: Partial<LinhaDados>, docExtra: Partial<DadosRecebimento> = {}) =>
      receber(b, `b-${randomUUID()}`, randomUUID(), {
        ...documento('2001', [linha(1, { local: b.local, lote: { codigo: 'X' }, ...extra })], docExtra),
        fazenda: b.fazenda,
      });
    expect(await deB({}, { emitente: ref.fornecedor })).toMatchObject({
      reasonCode: 'EMITENTE_NAO_ENCONTRADO',
    });
    await emOrganizacao(amb.app, b.org, (c) =>
      c.query(
        "INSERT INTO app.counterparty (id, organization_id, name, identification) VALUES ($1, $2, 'F B', '1')",
        [randomUUID(), b.org],
      ),
    );
    const fornecedorB = (
      await emOrganizacao(amb.app, b.org, (c) => c.query<{ id: string }>('SELECT id FROM app.counterparty'))
    ).rows[0]?.id as string;
    const comB = (extra: Partial<LinhaDados>) =>
      receber(b, `b-${randomUUID()}`, randomUUID(), {
        ...documento('2002', [linha(1, { local: b.local, lote: { codigo: 'X' }, ...extra })]),
        emitente: fornecedorB,
        fazenda: b.fazenda,
      });
    expect(await comB({ produto: ref.fungicida })).toMatchObject({ reasonCode: 'PRODUTO_NAO_ENCONTRADO' });
    expect(
      await comB({ produto: b.produto, unidade: { tipo: 'embalagem', conversao: ref.galao, versao: 1 } }),
    ).toMatchObject({
      reasonCode: 'CONVERSAO_NAO_ENCONTRADA',
    });
    expect(
      await comB({ produto: b.produto, local: a.local, unidade: { tipo: 'medida', unidade: 'L' } }),
    ).toMatchObject({
      reasonCode: 'LOCAL_NAO_ENCONTRADO',
    });
    expect(await fatos(b.org)).toEqual(antes);
  });

  it('duas linhas do mesmo lote sobem a versão uma única vez; movimentos com itens 1 e 2', async () => {
    const doc = randomUUID();
    const r = await receber(
      a,
      'nf-005',
      doc,
      documento('1005', [
        linha(1, { lote: { codigo: 'F26-13' } }),
        linha(2, {
          lote: { codigo: 'F26-13' },
          unidade: { tipo: 'medida', unidade: 'L' },
          documento: '2.5',
          parcelas: { apto: '2.5', quarentena: '0', bloqueado: '0', recusado: '0' },
        }),
      ]),
    );
    expect(r.outcome).toBe('confirmed');
    await emOrganizacao(amb.app, a.org, async (c) => {
      const m = await c.query<{ lv: string; item: number }>(
        `SELECT m.lot_version::text AS lv, m.intent_item AS item FROM app.stock_movement m
          JOIN app.receipt_line l ON l.id = m.receipt_line_id WHERE l.document_id = $1 ORDER BY m.intent_item`,
        [doc],
      );
      expect(m.rows).toEqual([
        { lv: '1', item: 1 },
        { lv: '1', item: 2 },
      ]);
      const v = await c.query<{ version: string }>("SELECT version::text FROM app.lot WHERE code = 'F26-13'");
      expect(v.rows[0]?.version).toBe('1');
    });
  });

  it('granel: Diesel entra em lote interno DOC:<documento> sem validade; lote de fabricante com esse código não é reusado', async () => {
    const doc = randomUUID();
    const diesel = (extra: Partial<LinhaDados> = {}) =>
      linha(1, {
        produto: ref.diesel,
        lote: { interno: true },
        validade: null,
        unidade: { tipo: 'medida', unidade: 'L' },
        documento: '500',
        parcelas: { apto: '500', quarentena: '0', bloqueado: '0', recusado: '0' },
        ...extra,
      });
    expect((await receber(a, 'nf-006', doc, documento('1006', [diesel()]))).outcome).toBe('confirmed');
    const lote = await emOrganizacao(amb.app, a.org, (c) =>
      c.query('SELECT code, kind, expiry_date, expiry_applies FROM app.lot WHERE code = $1', [`DOC:${doc}`]),
    );
    expect(lote.rows).toEqual([
      { code: `DOC:${doc}`, kind: 'agrupamento_interno', expiry_date: null, expiry_applies: false },
    ]);
    // Data num produto sem validade é recusada.
    expect(
      await receber(a, 'nf-007', randomUUID(), documento('1007', [diesel({ validade: '2027-01-01' })])),
    ).toMatchObject({
      reasonCode: 'VALIDADE_NAO_SE_APLICA',
    });
    // Um lote de fabricante do Diesel com o código DOC:<id> (anterior, por exemplo) nunca vira o lote interno.
    const colide = randomUUID();
    await emOrganizacao(amb.app, a.org, (c) =>
      c.query(
        `INSERT INTO app.lot (id, organization_id, product_id, code, expiry_date, base_unit, expiry_applies, kind)
         VALUES ($1, $2, $3, $4, NULL, 'L', false, 'fabricante')`,
        [randomUUID(), a.org, ref.diesel, `DOC:${colide}`],
      ),
    );
    const antes = await fatos(a.org);
    expect(await receber(a, 'nf-008', colide, documento('1008', [diesel()]))).toMatchObject({
      reasonCode: 'LOTE_INTERNO_COLIDE',
    });
    expect(await fatos(a.org)).toEqual(antes);
  });

  it('produto diferente: ocorrência retida aberta, sem movimento; pendências e próxima ação', async () => {
    const doc = randomUUID();
    const antes = await fatos(a.org);
    const r = await receber(
      a,
      'nf-009',
      doc,
      documento('1009', [
        linha(1, {
          lote: { codigo: 'F26-14' },
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
        }),
      ]),
    );
    expect(r).toMatchObject({ outcome: 'confirmed', nextAction: 'Ver divergência' });
    expect(r.pending).toEqual([
      'Divergência aberta: linha 1',
      `Produto divergente retido: linha 1, ${a.usuario} até 2026-10-02`,
      'Sem pedido',
    ]);
    const depois = await fatos(a.org);
    expect(depois.movimentos).toBe(antes.movimentos);
    expect(depois.ocorrencias).toBe((antes.ocorrencias ?? 0) + 1);
    // Ocorrência exige o motivo, e o produto real não pode ser o da linha.
    expect(
      await receber(
        a,
        'nf-010',
        randomUUID(),
        documento('1010', [
          linha(1, {
            lote: { codigo: 'F26-15' },
            motivo: 'produto_diferente',
            documento: '3',
            parcelas: { apto: '0', quarentena: '0', bloqueado: '0', recusado: '0' },
          }),
        ]),
      ),
    ).toMatchObject({ reasonCode: 'RECEBIMENTO_INVALIDO' });
  });

  it('quarentena: inspeção pendente com responsável e prazo, próxima ação "Ver inspeção pendente"; recusado sem movimento', async () => {
    const doc = randomUUID();
    const r = await receber(
      a,
      'nf-011',
      doc,
      documento('1011', [
        linha(1, {
          lote: { codigo: 'F26-16' },
          documento: '12',
          parcelas: { apto: '8', quarentena: '2', bloqueado: '0', recusado: '2' },
          motivo: 'avaria',
          inspecao: { responsavel: a.usuario, prazo: '2026-10-03' },
        }),
      ]),
    );
    expect(r).toMatchObject({ outcome: 'confirmed', nextAction: 'Ver inspeção pendente' });
    expect(r.pending[0]).toBe(`Inspeção pendente: linha 1, ${a.usuario} até 2026-10-03`);
    const m = await emOrganizacao(amb.app, a.org, (c) =>
      c.query<{ situation: string; bq: string }>(
        `SELECT m.situation, m.base_quantity::text AS bq FROM app.stock_movement m
           JOIN app.receipt_line l ON l.id = m.receipt_line_id WHERE l.document_id = $1 ORDER BY m.intent_item`,
        [doc],
      ),
    );
    expect(m.rows).toEqual([
      { situation: 'liberado_livre', bq: '40' },
      { situation: 'quarentena_livre', bq: '10' },
    ]);
  });

  it('contagem em un recusa fração; alvo que não é documento novo é recusado', async () => {
    expect(
      await receber(
        a,
        'nf-012',
        randomUUID(),
        documento('1012', [
          linha(1, {
            produto: ref.semente,
            lote: { codigo: 'S-1' },
            unidade: { tipo: 'medida', unidade: 'un' },
            documento: '1.5',
            parcelas: { apto: '1.5', quarentena: '0', bloqueado: '0', recusado: '0' },
          }),
        ]),
      ),
    ).toMatchObject({ reasonCode: 'RECEBIMENTO_INVALIDO' });
    const canonico = canonizarRecebimento(documento('1013', [linha(1, { lote: { codigo: 'F26-17' } })]));
    const r = await executarComando(
      amb.app,
      a.org,
      {
        commandType: COMANDO_RECEBER_DOCUMENTO,
        idempotencyKey: 'nf-013',
        initiatorKind: 'web',
        actorId: a.usuario,
        target: { type: 'lot', id: a.lote, expectedVersion: 0 },
        data: canonico,
        correlationId: 'corr-nf-013',
      },
      receberDocumento(canonico),
    );
    expect(r).toMatchObject({ outcome: 'rejected', reasonCode: 'ALVO_INVALIDO' });
  });
});
