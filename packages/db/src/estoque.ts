import { randomUUID } from 'node:crypto';

import {
  aplicar,
  decimal,
  estadoInicial,
  lote as loteDoDominio,
  paraBase,
  paraTexto,
  quantidade,
  saldo,
  type EstadoLote,
  type Movimento,
  type Situacao,
} from '@safrion/domain';
import type { DadosMovimento } from '@safrion/contracts';
import type { ClientBase } from 'pg';

import type { Efeito } from './comando.js';
import { ConflitoVersao, RejeicaoNegocio } from './erros.js';
import { ehUuid } from './sessao.js';

export type NovoMovimento =
  | {
      readonly tipo: 'entrada';
      readonly quantidade: string;
      readonly unidade: string;
      readonly situacao: Situacao;
    }
  | {
      readonly tipo: 'mudanca';
      readonly quantidade: string;
      readonly unidade: string;
      readonly de: Situacao;
      readonly para: Situacao;
    }
  | { readonly tipo: 'estorno'; readonly estornaId: string };

export interface PedidoMovimento {
  readonly lotId: string;
  readonly locationId: string;
  readonly movimento: NovoMovimento;
}

/** Do contrato externo (quantidade como objeto valor + unidade) para o pedido interno do efeito. */
export function pedidoDeMovimento(dados: DadosMovimento): PedidoMovimento {
  const m = dados.movimento;
  const movimento: NovoMovimento =
    m.tipo === 'estorno'
      ? { tipo: 'estorno', estornaId: m.estornaId }
      : m.tipo === 'entrada'
        ? {
            tipo: 'entrada',
            quantidade: m.quantidade.valor,
            unidade: m.quantidade.unidade,
            situacao: m.situacao,
          }
        : {
            tipo: 'mudanca',
            quantidade: m.quantidade.valor,
            unidade: m.quantidade.unidade,
            de: m.de,
            para: m.para,
          };
  return { lotId: dados.lote, locationId: dados.local, movimento };
}

/**
 * Conteúdo canônico do pedido para o hash da intenção (IDEM-13): decimal normalizado na mesma unidade ("1.0" e "1"
 * são o mesmo conteúdo); outra unidade é outro conteúdo, mesmo que fisicamente igual (1000 mL e 1 L).
 */
export function conteudoDoMovimento(pedido: PedidoMovimento): Record<string, unknown> {
  const m = pedido.movimento;
  const q = (v: string) => decimal(v).toString();
  const movimento =
    m.tipo === 'estorno'
      ? { tipo: m.tipo, estornaId: m.estornaId }
      : m.tipo === 'entrada'
        ? { tipo: m.tipo, quantidade: q(m.quantidade), unidade: m.unidade, situacao: m.situacao }
        : { tipo: m.tipo, quantidade: q(m.quantidade), unidade: m.unidade, de: m.de, para: m.para };
  return { lote: pedido.lotId, local: pedido.locationId, movimento };
}

interface LinhaLote {
  id: string;
  code: string;
  /** NULL quando a validade não se aplica ao lote (migração 0007, RN-032). */
  expiry_date: string | null;
  base_unit: string;
  version: string;
}

interface LinhaMovimento {
  id: string;
  kind: 'entrada' | 'mudanca' | 'estorno';
  situation: Situacao | null;
  from_situation: Situacao | null;
  to_situation: Situacao | null;
  reverses_id: string | null;
  base_quantity: string | null;
  base_unit: string | null;
  original_quantity: string | null;
  original_unit: string | null;
  lot_version: string;
  recorded_at: Date;
  location_id: string;
}

// A data vai como texto: o tipo date do driver viraria instante no fuso local e poderia mudar de dia (PRD 10.0).
const SELECT_LOTE = `SELECT id, code, expiry_date::text AS expiry_date, base_unit, version FROM app.lot WHERE id = $1`;
const COLUNAS_MOVIMENTO = `id, kind, situation, from_situation, to_situation, reverses_id,
    base_quantity::text AS base_quantity, base_unit, original_quantity::text AS original_quantity, original_unit,
    lot_version, recorded_at, location_id`;
const SELECT_MOVIMENTOS = `SELECT ${COLUNAS_MOVIMENTO}
  FROM app.stock_movement WHERE lot_id = $1 AND ($2::uuid IS NULL OR location_id = $2)
  ORDER BY lot_version, intent_item`;

function paraDominio(m: LinhaMovimento): Movimento {
  switch (m.kind) {
    case 'entrada':
      return {
        id: m.id,
        tipo: 'entrada',
        quantidade: quantidade(m.base_quantity, m.base_unit),
        situacao: m.situation as Situacao,
      };
    case 'mudanca':
      return {
        id: m.id,
        tipo: 'mudanca',
        quantidade: quantidade(m.base_quantity, m.base_unit),
        de: m.from_situation as Situacao,
        para: m.to_situation as Situacao,
      };
    case 'estorno':
      return { id: m.id, tipo: 'estorno', estornaId: m.reverses_id as string };
  }
}

/** Estado do lote num local, ou em todos quando local é null (saldo agregado). */
async function estadoDoLote(cliente: ClientBase, l: LinhaLote, local: string | null): Promise<EstadoLote> {
  const movs = await cliente.query<LinhaMovimento>(SELECT_MOVIMENTOS, [l.id, local]);
  return reconstruir(l, movs.rows);
}

function reconstruir(l: LinhaLote, movimentos: readonly LinhaMovimento[]): EstadoLote {
  let estado = estadoInicial(loteDoDominio(l.code, l.expiry_date, l.base_unit as 'L' | 'kg' | 'un'));
  for (const m of movimentos) estado = aplicar(estado, paraDominio(m));
  return estado;
}

/**
 * Efeito do envelope: registra um movimento no lote alvo (target.id), num local, sobre a versão esperada do lote. Lote
 * de outra organização é tratado como inexistente (RLS). O domínio (F0-a) valida quantidade, unidade, escala, item
 * indivisível, situação e saldo contra o estado DO LOCAL: um local não usa o saldo de outro, e o estorno só encontra o
 * movimento estornado no mesmo local. A violação vira rejeição registrada.
 */
export function registrarMovimento(pedido: PedidoMovimento): Efeito {
  return async (cliente, ctx) => {
    const esperada = ctx.intencao.target.expectedVersion;
    if (
      ctx.intencao.target.type !== 'lot' ||
      !ehUuid(pedido.lotId) ||
      pedido.lotId !== ctx.intencao.target.id ||
      esperada === undefined
    ) {
      throw new RejeicaoNegocio(
        'ALVO_INVALIDO',
        'O movimento precisa do lote como alvo e da versão esperada.',
      );
    }
    const loteAtual = (await cliente.query<LinhaLote>(`${SELECT_LOTE} FOR UPDATE`, [pedido.lotId])).rows[0];
    if (!loteAtual) throw new RejeicaoNegocio('LOTE_NAO_ENCONTRADO', 'Lote não encontrado.');
    const versaoAtual = Number(loteAtual.version);
    if (versaoAtual !== esperada) throw new ConflitoVersao(versaoAtual);
    const local = await cliente.query('SELECT 1 FROM app.stock_location WHERE id = $1', [
      ehUuid(pedido.locationId) ? pedido.locationId : null,
    ]);
    if (!local.rowCount)
      throw new RejeicaoNegocio('LOCAL_NAO_ENCONTRADO', 'Local de estoque não encontrado.');

    const antes = await estadoDoLote(cliente, loteAtual, pedido.locationId);
    const id = randomUUID();
    const m = pedido.movimento;
    let dominio: Movimento;
    let original: { quantidade: string; unidade: string } | null = null;
    switch (m.tipo) {
      case 'entrada':
        dominio = {
          id,
          tipo: 'entrada',
          quantidade: quantidade(m.quantidade, m.unidade),
          situacao: m.situacao,
        };
        original = { quantidade: m.quantidade, unidade: m.unidade };
        break;
      case 'mudanca':
        dominio = {
          id,
          tipo: 'mudanca',
          quantidade: quantidade(m.quantidade, m.unidade),
          de: m.de,
          para: m.para,
        };
        original = { quantidade: m.quantidade, unidade: m.unidade };
        break;
      case 'estorno':
        dominio = { id, tipo: 'estorno', estornaId: m.estornaId };
        break;
    }
    aplicar(antes, dominio); // lança ErroDominio se o movimento for inválido ou deixar saldo negativo
    const base = dominio.tipo === 'estorno' ? null : paraBase(dominio.quantidade);
    const novaVersao = versaoAtual + 1;
    await cliente.query(
      `INSERT INTO app.stock_movement (id, organization_id, lot_id, location_id, kind, situation, from_situation,
         to_situation, reverses_id, original_quantity, original_unit, base_quantity, base_unit, lot_version,
         intent_command_type, intent_key, intent_item, actor_id)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, 1, $17)`,
      [
        id,
        ctx.organizationId,
        pedido.lotId,
        pedido.locationId,
        m.tipo,
        m.tipo === 'entrada' ? m.situacao : null,
        m.tipo === 'mudanca' ? m.de : null,
        m.tipo === 'mudanca' ? m.para : null,
        m.tipo === 'estorno' ? m.estornaId : null,
        original?.quantidade ?? null,
        original?.unidade ?? null,
        base ? base.valor.toString() : null,
        base ? base.unidade : null,
        novaVersao,
        ctx.intencao.commandType,
        ctx.intencao.idempotencyKey,
        ctx.intencao.actorId,
      ],
    );
    await cliente.query('UPDATE app.lot SET version = $2 WHERE id = $1', [pedido.lotId, novaVersao]);
    const eventId = ctx.emitir({
      type: 'estoque.movimento_registrado',
      schemaVersion: 1,
      entityType: 'lot',
      entityId: pedido.lotId,
      entityVersion: novaVersao,
      previousVersion: versaoAtual,
      payload: {
        movementId: id,
        kind: m.tipo,
        baseQuantity: base?.valor.toString() ?? null,
        baseUnit: base?.unidade,
      },
    });
    return {
      resultingVersion: novaVersao,
      effects: { movements: [id] },
      before: { version: versaoAtual },
      after: { version: novaVersao, movementId: id, eventId },
    };
  };
}

export interface SaldoTexto {
  readonly version: number;
  readonly fisico: string;
  readonly utilizavel: string;
  readonly quarentena: string;
  readonly bloqueado: string;
  readonly vencido: string;
  readonly loteVencido: boolean;
}

/**
 * Saldo do lote na data civil informada, reconstruído dos movimentos (RF-SUP-003): de um local, ou agregado de todos os
 * locais quando o local não é informado. null se o lote (ou o local) não é visível ou não é um identificador válido.
 */
export async function saldoDoLote(
  cliente: ClientBase,
  lotId: string,
  hoje: string,
  local?: string,
): Promise<SaldoTexto | null> {
  if (!ehUuid(lotId) || (local !== undefined && !ehUuid(local))) return null;
  const l = (await cliente.query<LinhaLote>(SELECT_LOTE, [lotId])).rows[0];
  if (!l) return null;
  return saldoEmTexto(l, await estadoDoLote(cliente, l, local ?? null), hoje);
}

function saldoEmTexto(l: LinhaLote, estado: EstadoLote, hoje: string): SaldoTexto {
  const s = saldo(estado, hoje);
  return {
    version: Number(l.version),
    fisico: paraTexto(s.fisico, 6),
    utilizavel: paraTexto(s.utilizavel, 6),
    quarentena: paraTexto(s.quarentena, 6),
    bloqueado: paraTexto(s.bloqueado, 6),
    vencido: paraTexto(s.vencido, 6),
    loteVencido: s.loteVencido,
  };
}

/** Documento de entrada de onde veio o lote interno ou o movimento: a tela monta "NF 1/7001" a partir daqui. */
export interface OrigemDocumento {
  readonly documentoId: string;
  readonly tipo: 'nfe' | 'outro';
  readonly serie: string;
  readonly numero: string;
}

export interface LoteResumo {
  readonly id: string;
  readonly codigo: string;
  /**
   * Lote interno por documento (granel): o documento e o emitente, para a tela dar um nome legível e nunca mostrar
   * DOC:<uuid>. Lote de fabricante é null, mesmo com código parecido (contrato CMD-15 §7.1).
   */
  readonly granel: (OrigemDocumento & { readonly emitente: string }) | null;
  readonly produtoId: string;
  readonly produto: string;
  /** Data civil AAAA-MM-DD; null quando a validade não se aplica (nunca data fictícia, RN-032). */
  readonly validade: string | null;
  readonly unidade: string;
  /** Movimentos registrados em todos os locais: zero é lote ainda sem entrada. */
  readonly movimentos: number;
  readonly saldo: SaldoTexto;
}

interface LinhaLoteProduto extends LinhaLote {
  product_id: string;
  product_name: string;
  granel_documento: string | null;
  granel_tipo: 'nfe' | 'outro' | null;
  granel_serie: string | null;
  granel_numero: string | null;
  granel_emitente: string | null;
}

const SELECT_LOTES = `SELECT l.id, l.code, l.expiry_date::text AS expiry_date, l.base_unit, l.version, l.product_id,
    p.name AS product_name, g.id AS granel_documento, g.doc_type AS granel_tipo, g.series AS granel_serie,
    g.number AS granel_numero, g.issuer_name AS granel_emitente
  FROM app.lot l JOIN app.product p ON p.organization_id = l.organization_id AND p.id = l.product_id
  -- Só o lote interno ganha a origem; o de fabricante nunca, mesmo com código DOC: (contrato CMD-15 §7.1).
  LEFT JOIN LATERAL (
    SELECT d.id, d.doc_type, d.series, d.number, e.name AS issuer_name
      FROM app.receipt_line x
      JOIN app.receipt_document d ON d.organization_id = x.organization_id AND d.id = x.document_id
      JOIN app.counterparty e ON e.organization_id = d.organization_id AND e.id = d.issuer_id
     WHERE l.kind = 'agrupamento_interno' AND x.organization_id = l.organization_id AND x.lot_id = l.id
     ORDER BY x.line_number LIMIT 1) g ON true
  WHERE ($1::uuid IS NULL OR l.id = $1) AND ($2::uuid IS NULL OR l.product_id = $2)
  ORDER BY p.name, l.code, l.id`;
const SELECT_MOVIMENTOS_DOS_LOTES = `SELECT lot_id, ${COLUNAS_MOVIMENTO}
  FROM app.stock_movement WHERE lot_id = ANY($1::uuid[])
  ORDER BY lot_id, lot_version, intent_item`;

/**
 * Lotes visíveis da organização com o saldo agregado de todos os locais na data civil informada: a listagem do Estoque, o
 * detalhe (filtro por lote) e os lotes de um produto (filtro por produto). Duas consultas, qualquer que seja o número de
 * lotes; o saldo sai do mesmo domínio que valida o movimento. Filtro com identificador inválido devolve lista vazia.
 */
export async function listarLotes(
  cliente: ClientBase,
  hoje: string,
  filtro: { readonly lote?: string; readonly produto?: string } = {},
): Promise<LoteResumo[]> {
  if (
    (filtro.lote !== undefined && !ehUuid(filtro.lote)) ||
    (filtro.produto !== undefined && !ehUuid(filtro.produto))
  )
    return [];
  const lotes = (
    await cliente.query<LinhaLoteProduto>(SELECT_LOTES, [filtro.lote ?? null, filtro.produto ?? null])
  ).rows;
  if (lotes.length === 0) return [];
  const movimentos = await cliente.query<LinhaMovimento & { lot_id: string }>(SELECT_MOVIMENTOS_DOS_LOTES, [
    lotes.map((l) => l.id),
  ]);
  const porLote = new Map<string, LinhaMovimento[]>();
  for (const m of movimentos.rows) {
    const lista = porLote.get(m.lot_id);
    if (lista) lista.push(m);
    else porLote.set(m.lot_id, [m]);
  }
  return lotes.map((l) => {
    const lista = porLote.get(l.id) ?? [];
    return {
      id: l.id,
      codigo: l.code,
      granel:
        l.granel_documento !== null &&
        l.granel_tipo !== null &&
        l.granel_serie !== null &&
        l.granel_numero !== null &&
        l.granel_emitente !== null
          ? {
              documentoId: l.granel_documento,
              tipo: l.granel_tipo,
              serie: l.granel_serie,
              numero: l.granel_numero,
              emitente: l.granel_emitente,
            }
          : null,
      produtoId: l.product_id,
      produto: l.product_name,
      validade: l.expiry_date,
      unidade: l.base_unit,
      movimentos: lista.length,
      saldo: saldoEmTexto(l, reconstruir(l, lista), hoje),
    };
  });
}

export interface LinhaExtrato {
  readonly movementId: string;
  readonly locationId: string;
  readonly kind: 'entrada' | 'mudanca' | 'estorno';
  /** Situação da entrada; de e para da mudança; o movimento estornado. Nulos quando não se aplicam ao tipo. */
  readonly situacao: Situacao | null;
  readonly de: Situacao | null;
  readonly para: Situacao | null;
  readonly estornaId: string | null;
  readonly lotVersion: number;
  readonly baseQuantity: string | null;
  readonly baseUnit: string | null;
  readonly originalQuantity: string | null;
  readonly originalUnit: string | null;
  readonly recordedAt: string;
  /** Documento e linha do recebimento que gerou o movimento; null na entrada manual (estoque.registrar-entrada). */
  readonly origem: (OrigemDocumento & { readonly linha: number }) | null;
}

interface LinhaMovimentoComOrigem extends LinhaMovimento {
  documento_id: string | null;
  doc_type: 'nfe' | 'outro' | null;
  series: string | null;
  number: string | null;
  line_number: number | null;
}

const SELECT_EXTRATO = `SELECT m.id, m.kind, m.situation, m.from_situation, m.to_situation, m.reverses_id,
    m.base_quantity::text AS base_quantity, m.base_unit, m.original_quantity::text AS original_quantity,
    m.original_unit, m.lot_version, m.recorded_at, m.location_id, d.id AS documento_id, d.doc_type, d.series,
    d.number, x.line_number
  FROM app.stock_movement m
  LEFT JOIN app.receipt_line x ON x.organization_id = m.organization_id AND x.id = m.receipt_line_id
  LEFT JOIN app.receipt_document d ON d.organization_id = x.organization_id AND d.id = x.document_id
  WHERE m.lot_id = $1 AND ($2::uuid IS NULL OR m.location_id = $2)
  ORDER BY m.lot_version, m.intent_item`;

/** Extrato imutável do lote, na ordem das versões: de um local, ou de todos quando o local não é informado. */
export async function extratoDoLote(
  cliente: ClientBase,
  lotId: string,
  local?: string,
): Promise<LinhaExtrato[]> {
  if (!ehUuid(lotId) || (local !== undefined && !ehUuid(local))) return [];
  const r = await cliente.query<LinhaMovimentoComOrigem>(SELECT_EXTRATO, [lotId, local ?? null]);
  return r.rows.map((m) => ({
    movementId: m.id,
    locationId: m.location_id,
    kind: m.kind,
    situacao: m.situation,
    de: m.from_situation,
    para: m.to_situation,
    estornaId: m.reverses_id,
    lotVersion: Number(m.lot_version),
    baseQuantity: m.base_quantity,
    baseUnit: m.base_unit,
    originalQuantity: m.original_quantity,
    originalUnit: m.original_unit,
    recordedAt: m.recorded_at.toISOString(),
    origem:
      m.documento_id !== null &&
      m.doc_type !== null &&
      m.series !== null &&
      m.number !== null &&
      m.line_number !== null
        ? {
            documentoId: m.documento_id,
            tipo: m.doc_type,
            serie: m.series,
            numero: m.number,
            linha: m.line_number,
          }
        : null,
  }));
}
