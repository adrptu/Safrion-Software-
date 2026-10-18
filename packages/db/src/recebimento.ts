import { randomUUID } from 'node:crypto';

import type { DadosRecebimento } from '@safrion/contracts';
import {
  ErroDominio,
  aplicar,
  codigoLoteInterno,
  conferirLinha,
  conversaoEmbalagem,
  converter,
  estadoInicial,
  identidadeDaOrigem,
  lote as loteDoDominio,
  movimentosDaLinha,
  numerarMovimentos,
  ocorrenciaDeChegada,
  paraBase,
  proximaAcao,
  quantidade,
  validadeNoRecebimento,
  type CodigoUnidade,
  type DataCivil,
  type DestinoOcorrencia,
  type LinhaConferida,
  type MotivoDivergencia,
  type MovimentoDaParcela,
  type PoliticaValidade,
  type UnidadeDaLinha,
} from '@safrion/domain';
import type { ClientBase, PoolClient } from 'pg';

import { consultarIntencao, type Efeito, type Recibo } from './comando.js';
import { RejeicaoNegocio } from './erros.js';
import { saldoDoLote, type SaldoTexto } from './estoque.js';
import { ehUuid } from './sessao.js';

export const COMANDO_RECEBER_DOCUMENTO = 'estoque.receber-documento';

interface Produto {
  id: string;
  base_unit: CodigoUnidade;
  expiry_policy: PoliticaValidade;
  lot_policy: 'informado' | 'por_documento';
}
interface Conversao {
  id: string;
  product_id: string;
  packaging: string;
  factor: string;
  version: number;
}
interface LoteLido {
  id: string;
  kind: 'fabricante' | 'agrupamento_interno';
  expiry_date: string | null;
  version: string;
}

type Dados = DadosRecebimento;
type Linha = Dados['linhas'][number];

/** Linha já conferida contra o cadastro da organização da sessão. */
interface LinhaPreparada {
  readonly dados: Linha;
  readonly produto: Produto;
  readonly unidade: UnidadeDaLinha;
  readonly conversao: Conversao | null;
  readonly dominio: LinhaConferida;
  readonly divergente: boolean;
  readonly codigoLote: string;
  readonly tipoLote: LoteLido['kind'];
  readonly ocorrencia: ReturnType<typeof ocorrenciaDeChegada> | null;
}

function rejeitar(motivo: string, mensagem: string): never {
  throw new RejeicaoNegocio(motivo, mensagem);
}

function erroPg(erro: unknown): { code?: string; constraint?: string } {
  return typeof erro === 'object' && erro !== null ? erro : {};
}

async function porId<T extends { id: string }>(c: PoolClient, sql: string, ids: readonly string[]) {
  const r = await c.query<T>(sql, [[...new Set(ids)]]);
  return new Map(r.rows.map((l) => [l.id, l]));
}

/**
 * Efeito do envelope para estoque.receber-documento (CMD-15; contrato CMD-15 v3.3, §1–§6). Tudo ou nada (IDEM-16):
 * cabeçalho, linhas, lotes novos, movimentos, versões, ocorrências e outbox na transação do envelope; qualquer rejeição
 * desfaz o efeito pelo savepoint do envelope e fica registrada com a chave. O que é de outra organização não é visível
 * (RLS) e é tratado como inexistente.
 */
export function receberDocumento(dados: Dados): Efeito {
  return async (c, ctx) => {
    const alvo = ctx.intencao.target;
    const documentoId = alvo.id;
    if (alvo.type !== 'receipt_document' || alvo.expectedVersion !== 0 || !ehUuid(documentoId)) {
      rejeitar(
        'ALVO_INVALIDO',
        'O recebimento cria um documento novo: alvo receipt_document, versão esperada 0.',
      );
    }
    const origem = identidadeDaOrigem({ tipo: dados.tipo, serie: dados.serie, numero: dados.numero });
    const numeros = new Set(dados.linhas.map((l) => l.numero));
    if (numeros.size !== dados.linhas.length) rejeitar('RECEBIMENTO_INVALIDO', 'Número de linha repetido.');

    // Cadastro da organização da sessão: o que não aparece é inexistente, inclusive o que é de outra organização.
    if (!(await c.query('SELECT 1 FROM app.counterparty WHERE id = $1', [dados.emitente])).rowCount) {
      rejeitar('EMITENTE_NAO_ENCONTRADO', 'Emitente do documento não encontrado.');
    }
    if (!(await c.query('SELECT 1 FROM app.farm WHERE id = $1', [dados.fazenda])).rowCount) {
      rejeitar('FAZENDA_NAO_ENCONTRADA', 'Fazenda não encontrada.');
    }
    // Pendência só para pessoa ativa da própria organização: responsável de fora ou inexistente não recebe tarefa.
    const responsaveis = [
      ...new Set(
        dados.linhas
          .flatMap((l) => [l.inspecao?.responsavel, l.ocorrencia?.responsavel])
          .filter((x) => x !== undefined),
      ),
    ];
    if (responsaveis.length > 0) {
      const ativos = await c.query('SELECT 1 FROM app.app_user WHERE id = ANY($1::uuid[]) AND active', [
        responsaveis,
      ]);
      if (ativos.rowCount !== responsaveis.length) {
        rejeitar(
          'RESPONSAVEL_NAO_ENCONTRADO',
          'Responsável pela inspeção ou pela ocorrência não encontrado na organização.',
        );
      }
    }
    const idsProduto = dados.linhas.flatMap((l) => {
      const real = l.ocorrencia?.produtoReal;
      return real && 'produto' in real ? [l.produto, real.produto] : [l.produto];
    });
    const produtos = await porId<Produto>(
      c,
      'SELECT id, base_unit, expiry_policy, lot_policy FROM app.product WHERE id = ANY($1::uuid[])',
      idsProduto,
    );
    const locais = await porId<{ id: string; farm_id: string }>(
      c,
      'SELECT id, farm_id FROM app.stock_location WHERE id = ANY($1::uuid[])',
      dados.linhas.map((l) => l.local),
    );
    const conversoes = await porId<Conversao>(
      c,
      `SELECT id, product_id, packaging, factor::text AS factor, version FROM app.packaging_conversion
        WHERE id = ANY($1::uuid[])`,
      dados.linhas.flatMap((l) => (l.unidade.tipo === 'embalagem' ? [l.unidade.conversao] : [])),
    );

    // Conferência de cada linha pelo domínio, antes de gravar qualquer coisa.
    const linhas: LinhaPreparada[] = [...dados.linhas]
      .sort((a, b) => a.numero - b.numero)
      .map((l) => {
        const produto =
          produtos.get(l.produto) ??
          rejeitar('PRODUTO_NAO_ENCONTRADO', `Linha ${String(l.numero)}: produto não encontrado.`);
        const local =
          locais.get(l.local) ??
          rejeitar('LOCAL_NAO_ENCONTRADO', `Linha ${String(l.numero)}: local não encontrado.`);
        if (local.farm_id !== dados.fazenda) {
          rejeitar(
            'LOCAL_FORA_DA_FAZENDA',
            `Linha ${String(l.numero)}: o local não é da fazenda do documento.`,
          );
        }
        let unidade: UnidadeDaLinha;
        let conversao: Conversao | null = null;
        if (l.unidade.tipo === 'embalagem') {
          const cv = conversoes.get(l.unidade.conversao);
          if (!cv || cv.product_id !== l.produto || cv.version !== l.unidade.versao) {
            rejeitar(
              'CONVERSAO_NAO_ENCONTRADA',
              `Linha ${String(l.numero)}: conversão do produto nessa versão não encontrada.`,
            );
          }
          conversao = cv;
          unidade = {
            tipo: 'embalagem',
            conversao: conversaoEmbalagem(cv.packaging, cv.factor, produto.base_unit, cv.version),
          };
        } else {
          // A unidade da linha é da dimensão do produto mesmo sem movimento (linha toda recusada, por exemplo).
          converter(quantidade('1', l.unidade.unidade), produto.base_unit);
          unidade = { tipo: 'medida', unidade: l.unidade.unidade };
        }
        const dominio: LinhaConferida = {
          numero: l.numero,
          unidade,
          documento: l.documento,
          parcelas: l.parcelas,
          ...(l.motivo === undefined ? {} : { motivo: l.motivo }),
          ...(l.motivoTexto === undefined ? {} : { motivoTexto: l.motivoTexto }),
          ...(l.inspecao === undefined ? {} : { inspecao: l.inspecao }),
        };
        const { divergente } = conferirLinha(dominio);
        // Lote: granel ("por documento") ganha lote interno DOC:<id do documento>; o resto informa o do fabricante.
        let codigoLote: string;
        let tipoLote: LoteLido['kind'];
        if (produto.lot_policy === 'por_documento') {
          if (!('interno' in l.lote)) {
            rejeitar(
              'LOTE_POR_DOCUMENTO',
              `Linha ${String(l.numero)}: este produto recebe lote interno por documento.`,
            );
          }
          codigoLote = codigoLoteInterno(documentoId);
          tipoLote = 'agrupamento_interno';
        } else {
          if (!('codigo' in l.lote)) {
            rejeitar('LOTE_OBRIGATORIO', `Linha ${String(l.numero)}: informe o lote do fabricante.`);
          }
          codigoLote = l.lote.codigo.trim();
          tipoLote = 'fabricante';
        }
        // Produto diferente (SUBST-14): ocorrência de chegada, só com o motivo e com produto real diferente.
        let ocorrencia: LinhaPreparada['ocorrencia'] = null;
        if ((l.motivo === 'produto_diferente') !== (l.ocorrencia !== undefined)) {
          rejeitar(
            'RECEBIMENTO_INVALIDO',
            `Linha ${String(l.numero)}: produto diferente exige a ocorrência de chegada, e vice-versa.`,
          );
        }
        if (l.ocorrencia) {
          const real = l.ocorrencia.produtoReal;
          if ('produto' in real) {
            if (real.produto === l.produto) {
              rejeitar(
                'RECEBIMENTO_INVALIDO',
                `Linha ${String(l.numero)}: o produto real é o próprio produto da linha.`,
              );
            }
            if (!produtos.has(real.produto)) {
              rejeitar('PRODUTO_NAO_ENCONTRADO', `Linha ${String(l.numero)}: produto real não encontrado.`);
            }
          }
          ocorrencia = ocorrenciaDeChegada({
            produtoReal: 'produto' in real ? { produtoId: real.produto } : { descricao: real.descricao },
            quantidade: l.ocorrencia.quantidade,
            unidade: l.ocorrencia.unidade,
            destino: l.ocorrencia.destino,
            responsavel: l.ocorrencia.responsavel,
            ...(l.ocorrencia.prazo === undefined ? {} : { prazo: l.ocorrencia.prazo }),
          });
        }
        return {
          dados: l,
          produto,
          unidade,
          conversao,
          dominio,
          divergente,
          codigoLote,
          tipoLote,
          ocorrencia,
        };
      });

    // Cabeçalho primeiro: o índice da origem serializa a mesma NF. Depois do erro não há consulta; o savepoint desfaz.
    try {
      await c.query(
        `INSERT INTO app.receipt_document (id, organization_id, issuer_id, doc_type, series, number, issued_on,
           received_on, farm_id, external_system, external_order_ref, actor_id, intent_command_type, intent_key)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)`,
        [
          documentoId,
          ctx.organizationId,
          dados.emitente,
          origem.tipo,
          origem.serie,
          origem.numero,
          dados.emissao,
          dados.recebimento,
          dados.fazenda,
          dados.pedido?.sistema ?? null,
          dados.pedido?.referencia ?? null,
          ctx.intencao.actorId,
          ctx.intencao.commandType,
          ctx.intencao.idempotencyKey,
        ],
      );
    } catch (erro) {
      const e = erroPg(erro);
      if (e.code === '23505' && e.constraint === 'receipt_document_origem') {
        rejeitar('DOCUMENTO_JA_RECEBIDO', 'Este documento do emitente já foi recebido.');
      }
      // Id repetido, inclusive de outra organização (a PK é global): resposta de inexistente, sem revelar o dono.
      if (e.code === '23505')
        rejeitar('ALVO_INVALIDO', 'Identificador do documento indisponível; gere outro.');
      throw erro;
    }

    // Lotes: primeiro inserir ou obter em ordem de (produto, código) — lote novo tem id aleatório —, depois travar em
    // ordem de id. A validade segue a do lote existente; lote novo segue a política vigente do produto.
    const grupos = new Map<
      string,
      { produto: Produto; codigo: string; tipo: LoteLido['kind']; linhas: LinhaPreparada[] }
    >();
    for (const l of linhas) {
      const chave = `${l.produto.id}\u0000${l.codigoLote}`;
      const g = grupos.get(chave) ?? {
        produto: l.produto,
        codigo: l.codigoLote,
        tipo: l.tipoLote,
        linhas: [],
      };
      g.linhas.push(l);
      grupos.set(chave, g);
    }
    const ordem = [...grupos.values()].sort((a, b) =>
      a.produto.id !== b.produto.id
        ? a.produto.id < b.produto.id
          ? -1
          : 1
        : a.codigo < b.codigo
          ? -1
          : a.codigo > b.codigo
            ? 1
            : 0,
    );
    const loteDaLinha = new Map<
      number,
      { id: string; validade: DataCivil | null; codigo: string; base: CodigoUnidade }
    >();
    for (const g of ordem) {
      const lido = async () =>
        (
          await c.query<LoteLido>(
            `SELECT id, kind, expiry_date::text AS expiry_date, version FROM app.lot WHERE product_id = $1 AND code = $2`,
            [g.produto.id, g.codigo],
          )
        ).rows[0];
      const validadeDoGrupo = (existente: LoteLido | undefined): DataCivil | null => {
        const validades = new Set(
          g.linhas.map((l) =>
            validadeNoRecebimento({
              politicaProduto: g.produto.expiry_policy,
              ...(existente ? { loteExistente: { validade: existente.expiry_date } } : {}),
              informada: l.dados.validade,
            }),
          ),
        );
        if (validades.size !== 1) {
          rejeitar(
            'VALIDADE_DIFERENTE_DO_LOTE',
            `O lote ${g.codigo} aparece com validades diferentes no documento.`,
          );
        }
        return [...validades][0] ?? null;
      };
      let existente = await lido();
      if (!existente) {
        const validade = validadeDoGrupo(undefined);
        await c.query(
          `INSERT INTO app.lot (id, organization_id, product_id, code, expiry_date, base_unit, expiry_applies, kind)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
           ON CONFLICT (organization_id, product_id, code) DO NOTHING`,
          [
            randomUUID(),
            ctx.organizationId,
            g.produto.id,
            g.codigo,
            validade,
            g.produto.base_unit,
            validade !== null,
            g.tipo,
          ],
        );
        existente = await lido();
        if (!existente) throw new Error('lote não encontrado depois da inserção');
      }
      // Um código de lote nunca troca de tipo: lote de fabricante não vira interno, nem o contrário (CMD15-CX03).
      if (existente.kind !== g.tipo) {
        rejeitar(
          g.tipo === 'agrupamento_interno' ? 'LOTE_INTERNO_COLIDE' : 'LOTE_TIPO_DIFERENTE',
          `O código de lote ${g.codigo} já pertence a um lote de outro tipo.`,
        );
      }
      const validade = validadeDoGrupo(existente);
      for (const l of g.linhas) {
        loteDaLinha.set(l.dados.numero, {
          id: existente.id,
          validade,
          codigo: g.codigo,
          base: g.produto.base_unit,
        });
      }
    }
    const idsLote = [...new Set([...loteDaLinha.values()].map((l) => l.id))].sort();
    const travados = await c.query<{ id: string; version: string }>(
      'SELECT id, version FROM app.lot WHERE id = ANY($1::uuid[]) ORDER BY id FOR UPDATE',
      [idsLote],
    );
    const versaoAntes = new Map(travados.rows.map((l) => [l.id, Number(l.version)]));
    // Auditoria (NFR-04; contrato §6): saldo de cada lote afetado antes e depois, na data civil do recebimento.
    const saldos = async () => {
      const r: Record<string, SaldoTexto | null> = {};
      for (const id of idsLote) r[id] = await saldoDoLote(c, id, dados.recebimento);
      return r;
    };
    const saldoAntes = await saldos();

    // Linhas, movimentos de cada parcela física (validados pelo saldo do domínio na unidade do lote) e ocorrências.
    const idsLinha = new Map<number, string>();
    const porLinha: { numero: number; movimentos: readonly MovimentoDaParcela[] }[] = [];
    const idsOcorrencia: string[] = [];
    for (const l of linhas) {
      const lt = loteDaLinha.get(l.dados.numero);
      if (!lt) throw new Error('linha sem lote');
      const id = randomUUID();
      idsLinha.set(l.dados.numero, id);
      const p = l.dados.parcelas;
      await c.query(
        `INSERT INTO app.receipt_line (id, organization_id, document_id, farm_id, line_number, product_id, lot_id,
           location_id, document_quantity, unit, conversion_id, conversion_version, qty_apto, qty_quarentena,
           qty_bloqueado, qty_recusado, divergence_reason, divergence_note, inspection_owner_id, inspection_due_on,
           external_order_line_ref, unit_price)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)`,
        [
          id,
          ctx.organizationId,
          documentoId,
          dados.fazenda,
          l.dados.numero,
          l.produto.id,
          lt.id,
          l.dados.local,
          l.dados.documento,
          l.unidade.tipo === 'embalagem' ? l.unidade.conversao.embalagem : l.unidade.unidade,
          l.conversao?.id ?? null,
          l.conversao?.version ?? null,
          p.apto,
          p.quarentena,
          p.bloqueado,
          p.recusado,
          l.dados.motivo ?? null,
          l.dados.motivoTexto ?? null,
          l.dados.inspecao?.responsavel ?? null,
          l.dados.inspecao?.prazo ?? null,
          l.dados.pedidoLinha ?? null,
          l.dados.valorUnitario ?? null,
        ],
      );
      const movimentos = movimentosDaLinha(l.dominio, () => randomUUID());
      const estado = estadoInicial(loteDoDominio(lt.codigo, lt.validade, lt.base));
      for (const m of movimentos) aplicar(estado, m.movimento); // unidade do lote, escala e item indivisível
      porLinha.push({ numero: l.dados.numero, movimentos });
      if (l.ocorrencia) {
        const o = l.ocorrencia;
        const oid = randomUUID();
        idsOcorrencia.push(oid);
        await c.query(
          `INSERT INTO app.receipt_occurrence (id, organization_id, document_id, line_id, real_product_id,
             real_product_description, counted_quantity, counted_unit, destination, owner_id, due_on, status)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)`,
          [
            oid,
            ctx.organizationId,
            documentoId,
            id,
            'produtoId' in o.produtoReal ? o.produtoReal.produtoId : null,
            'descricao' in o.produtoReal ? o.produtoReal.descricao : null,
            o.quantidade,
            o.unidade,
            o.destino,
            o.responsavel,
            o.prazo ?? null,
            o.status,
          ],
        );
      }
    }

    // Cada lote com entrada sobe uma versão por comando; os movimentos do mesmo lote dividem a versão (0001:147-148).
    const numerados = numerarMovimentos(porLinha);
    const versaoNova = new Map<string, number>();
    for (const n of numerados) {
      const lt = loteDaLinha.get(n.linha);
      const linha = linhas.find((l) => l.dados.numero === n.linha);
      if (!lt || !linha) throw new Error('movimento sem lote');
      const versao = (versaoAntes.get(lt.id) ?? 0) + 1;
      versaoNova.set(lt.id, versao);
      const m = n.movimento.movimento;
      const base = paraBase(m.quantidade);
      const original =
        linha.unidade.tipo === 'embalagem' && m.origem
          ? { quantidade: m.origem.contagem, unidade: m.origem.embalagem }
          : { quantidade: m.quantidade.valor.toString(), unidade: m.quantidade.unidade };
      await c.query(
        `INSERT INTO app.stock_movement (id, organization_id, lot_id, location_id, kind, situation, original_quantity,
           original_unit, base_quantity, base_unit, conversion_id, conversion_version, lot_version, intent_command_type,
           intent_key, intent_item, actor_id, receipt_line_id)
         VALUES ($1, $2, $3, $4, 'entrada', $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)`,
        [
          m.id,
          ctx.organizationId,
          lt.id,
          linha.dados.local,
          m.situacao,
          original.quantidade,
          original.unidade,
          base.valor.toString(),
          base.unidade,
          linha.conversao?.id ?? null,
          linha.conversao?.version ?? null,
          versao,
          ctx.intencao.commandType,
          ctx.intencao.idempotencyKey,
          n.item,
          ctx.intencao.actorId,
          idsLinha.get(n.linha),
        ],
      );
    }
    for (const [id, versao] of versaoNova) {
      await c.query('UPDATE app.lot SET version = $2 WHERE id = $1', [id, versao]);
      ctx.emitir({
        type: 'estoque.movimento_registrado',
        schemaVersion: 1,
        entityType: 'lot',
        entityId: id,
        entityVersion: versao,
        previousVersion: versaoAntes.get(id) ?? 0,
        payload: {
          movements: numerados
            .filter((n) => loteDaLinha.get(n.linha)?.id === id)
            .map((n) => n.movimento.movimento.id),
          receiptDocumentId: documentoId,
        },
      });
    }
    ctx.emitir({
      type: 'estoque.recebimento_confirmado',
      schemaVersion: 1,
      entityType: 'receipt_document',
      entityId: documentoId,
      entityVersion: 1,
      previousVersion: null,
      payload: { lines: linhas.length, movements: numerados.length, occurrences: idsOcorrencia.length },
    });

    // Pendências e próxima ação só com ações que existem no incremento 1 (contrato §6).
    const pendentes: string[] = [];
    for (const l of linhas) {
      const n = String(l.dados.numero);
      if (l.dados.inspecao) {
        pendentes.push(
          `Inspeção pendente: linha ${n}, ${l.dados.inspecao.responsavel} até ${l.dados.inspecao.prazo}`,
        );
      }
      // Responsável contextual e verificável: quem registrou o recebimento (a sessão), sem campo manual a mais.
      if (l.divergente) pendentes.push(`Divergência aberta: linha ${n}, ${ctx.intencao.actorId}`);
      if (l.ocorrencia?.status === 'aberta') {
        pendentes.push(
          `Produto divergente retido: linha ${n}, ${l.ocorrencia.responsavel} até ${l.ocorrencia.prazo ?? ''}`,
        );
      }
    }
    if (!dados.pedido) pendentes.push('Sem pedido');
    const nextAction = proximaAcao({
      inspecaoPendente: linhas.some((l) => l.dados.inspecao !== undefined),
      divergente: linhas.some((l) => l.divergente),
      ocorrenciaAberta: linhas.some((l) => l.ocorrencia?.status === 'aberta'),
    });
    const motivoAuditoria = linhas
      .filter((l) => l.divergente)
      .map((l) => {
        const texto = l.dados.motivoTexto ? ` (${l.dados.motivoTexto})` : '';
        return `linha ${String(l.dados.numero)}: ${l.dados.motivo ?? ''}${texto}`;
      })
      .join('; ');
    return {
      resultingVersion: 1,
      effects: {
        documents: [documentoId],
        lines: [...idsLinha.values()],
        lots: idsLote,
        movements: numerados.map((n) => n.movimento.movimento.id),
        occurrences: idsOcorrencia,
      },
      pending: pendentes,
      nextAction,
      before: { lots: saldoAntes },
      after: {
        document: documentoId,
        lots: await saldos(),
        lines: linhas.map((l) => ({
          id: idsLinha.get(l.dados.numero),
          numero: l.dados.numero,
          motivo: l.dados.motivo ?? null,
        })),
      },
      // Motivo na auditoria, ligado às linhas divergentes (NFR-04; contrato §6).
      ...(motivoAuditoria ? { reason: motivoAuditoria } : {}),
    };
  };
}

// Leitura do documento (contrato CMD-15 §6.1) ----------------------------------------------------------------------------
// Dentro de emOrganizacao (sessão + RLS), sem gravar nada. Quantidades em texto decimal como gravadas, datas civis
// AAAA-MM-DD, validade ausente como null explícito (nunca data fictícia). Outra organização é igual a inexistente.

export interface Referencia {
  readonly id: string;
  readonly nome: string;
}

export interface DocumentoResumo {
  readonly id: string;
  readonly emitente: Referencia & { readonly identificacao: string };
  readonly tipo: 'nfe' | 'outro';
  readonly serie: string;
  readonly numero: string;
  readonly emissao: string;
  readonly recebimento: string;
  readonly fazenda: Referencia;
  readonly status: 'confirmado' | 'estornado';
  readonly versao: number;
  /** Instante ISO 8601 do registro. */
  readonly registradoEm: string;
  /** Divergência = linha com motivo gravado (no incremento 1, toda aberta); inspeção = linha com quarentena. */
  readonly contagens: {
    readonly linhas: number;
    readonly divergencias: number;
    readonly inspecoes: number;
    readonly ocorrenciasAbertas: number;
  };
}

export interface LinhaDoDocumento {
  readonly id: string;
  readonly numero: number;
  readonly produto: Referencia;
  readonly lote: {
    readonly id: string;
    readonly codigo: string;
    readonly tipo: 'fabricante' | 'agrupamento_interno';
    readonly validade: string | null;
  };
  readonly local: Referencia;
  readonly documento: string;
  readonly unidade: string;
  readonly conversao: { readonly id: string; readonly versao: number } | null;
  readonly parcelas: {
    readonly apto: string;
    readonly quarentena: string;
    readonly bloqueado: string;
    readonly recusado: string;
  };
  readonly divergencia: { readonly motivo: MotivoDivergencia; readonly texto: string | null } | null;
  readonly inspecao: { readonly responsavel: Referencia; readonly prazo: string } | null;
  readonly pedidoLinha: string | null;
  readonly valorUnitario: string | null;
  /** Movimentos que a linha gerou, na ordem das versões do lote: o vínculo com o extrato. */
  readonly movimentos: readonly string[];
}

export interface OcorrenciaDoDocumento {
  readonly id: string;
  readonly linha: { readonly id: string; readonly numero: number };
  readonly produtoReal: Referencia | { readonly descricao: string };
  readonly quantidade: string;
  readonly unidade: string;
  readonly destino: DestinoOcorrencia;
  readonly status: 'aberta' | 'registrada';
  readonly responsavel: Referencia;
  readonly prazo: string | null;
  readonly registradaEm: string;
}

export interface DocumentoDetalhe extends DocumentoResumo {
  readonly pedido: { readonly sistema: string | null; readonly referencia: string } | null;
  /** O nome falta quando o autor não é usuário da organização (integração). */
  readonly autor: { readonly id: string; readonly nome: string | null };
  /** O recibo do envelope pela chave gravada no documento: pendência e próxima ação vêm dele. */
  readonly recibo: Recibo | null;
  readonly linhas: readonly LinhaDoDocumento[];
  readonly ocorrencias: readonly OcorrenciaDoDocumento[];
}

interface LinhaDocumentoLido {
  id: string;
  doc_type: 'nfe' | 'outro';
  series: string;
  number: string;
  issued_on: string;
  received_on: string;
  status: 'confirmado' | 'estornado';
  version: string;
  recorded_at: Date;
  issuer_id: string;
  issuer_name: string;
  issuer_identification: string;
  farm_id: string;
  farm_name: string;
  external_system: string | null;
  external_order_ref: string | null;
  actor_id: string;
  actor_name: string | null;
  intent_command_type: string;
  intent_key: string;
  linhas: number;
  divergencias: number;
  inspecoes: number;
  ocorrencias_abertas: number;
}

interface LinhaDaLinhaLida {
  id: string;
  line_number: number;
  product_id: string;
  product_name: string;
  lot_id: string;
  lot_code: string;
  lot_kind: 'fabricante' | 'agrupamento_interno';
  lot_expiry: string | null;
  location_id: string;
  location_name: string;
  document_quantity: string;
  unit: string;
  conversion_id: string | null;
  conversion_version: number | null;
  qty_apto: string;
  qty_quarentena: string;
  qty_bloqueado: string;
  qty_recusado: string;
  divergence_reason: MotivoDivergencia | null;
  divergence_note: string | null;
  inspection_owner_id: string | null;
  inspection_owner_name: string | null;
  inspection_due_on: string | null;
  external_order_line_ref: string | null;
  unit_price: string | null;
  movimentos: string[];
}

interface LinhaOcorrenciaLida {
  id: string;
  line_id: string;
  line_number: number;
  real_product_id: string | null;
  real_product_name: string | null;
  real_product_description: string | null;
  counted_quantity: string;
  counted_unit: string;
  destination: DestinoOcorrencia;
  status: 'aberta' | 'registrada';
  owner_id: string;
  owner_name: string;
  due_on: string | null;
  recorded_at: Date;
}

// Datas civis como texto: o tipo date do driver viraria instante no fuso local (PRD 10.0).
const PROJECAO_DOCUMENTOS = `SELECT d.id, d.doc_type, d.series, d.number, d.issued_on::text AS issued_on,
    d.received_on::text AS received_on, d.status, d.version::text AS version, d.recorded_at,
    e.id AS issuer_id, e.name AS issuer_name, e.identification AS issuer_identification, f.id AS farm_id,
    f.name AS farm_name, d.external_system, d.external_order_ref, d.actor_id, u.name AS actor_name,
    d.intent_command_type, d.intent_key, l.linhas, l.divergencias, l.inspecoes, o.ocorrencias_abertas
  FROM app.receipt_document d
  JOIN app.counterparty e ON e.organization_id = d.organization_id AND e.id = d.issuer_id
  JOIN app.farm f ON f.organization_id = d.organization_id AND f.id = d.farm_id
  LEFT JOIN app.app_user u ON u.organization_id = d.organization_id AND u.id = d.actor_id
  CROSS JOIN LATERAL (
    SELECT count(*)::int AS linhas,
           count(*) FILTER (WHERE x.divergence_reason IS NOT NULL)::int AS divergencias,
           count(*) FILTER (WHERE x.qty_quarentena > 0)::int AS inspecoes
      FROM app.receipt_line x WHERE x.organization_id = d.organization_id AND x.document_id = d.id) l
  CROSS JOIN LATERAL (
    SELECT count(*)::int AS ocorrencias_abertas
      FROM app.receipt_occurrence y
     WHERE y.organization_id = d.organization_id AND y.document_id = d.id AND y.status = 'aberta') o`;

const SELECT_DOCUMENTOS = `${PROJECAO_DOCUMENTOS}
  WHERE ($1::uuid IS NULL OR d.id = $1)
  ORDER BY d.received_on DESC, d.recorded_at DESC, d.id`;

// A mesma chave do índice parcial receipt_document_origem: só entre os confirmados.
const SELECT_DOCUMENTO_POR_ORIGEM = `${PROJECAO_DOCUMENTOS}
  WHERE d.issuer_id = $1 AND d.doc_type = $2 AND d.series = $3 AND d.number = $4 AND d.status = 'confirmado'`;

const SELECT_LINHAS_DO_DOCUMENTO = `SELECT l.id, l.line_number, l.product_id, p.name AS product_name, l.lot_id,
    t.code AS lot_code, t.kind AS lot_kind, t.expiry_date::text AS lot_expiry, l.location_id, s.name AS location_name,
    l.document_quantity::text AS document_quantity, l.unit, l.conversion_id, l.conversion_version,
    l.qty_apto::text AS qty_apto, l.qty_quarentena::text AS qty_quarentena, l.qty_bloqueado::text AS qty_bloqueado,
    l.qty_recusado::text AS qty_recusado, l.divergence_reason, l.divergence_note, l.inspection_owner_id,
    u.name AS inspection_owner_name, l.inspection_due_on::text AS inspection_due_on, l.external_order_line_ref,
    l.unit_price::text AS unit_price,
    coalesce((SELECT array_agg(m.id::text ORDER BY m.lot_version, m.intent_item) FROM app.stock_movement m
               WHERE m.organization_id = l.organization_id AND m.receipt_line_id = l.id), '{}') AS movimentos
  FROM app.receipt_line l
  JOIN app.product p ON p.organization_id = l.organization_id AND p.id = l.product_id
  JOIN app.lot t ON t.organization_id = l.organization_id AND t.id = l.lot_id
  JOIN app.stock_location s ON s.organization_id = l.organization_id AND s.id = l.location_id
  LEFT JOIN app.app_user u ON u.organization_id = l.organization_id AND u.id = l.inspection_owner_id
  WHERE l.document_id = $1
  ORDER BY l.line_number`;

const SELECT_OCORRENCIAS_DO_DOCUMENTO = `SELECT o.id, o.line_id, l.line_number, o.real_product_id,
    p.name AS real_product_name, o.real_product_description, o.counted_quantity::text AS counted_quantity,
    o.counted_unit, o.destination, o.status, o.owner_id, u.name AS owner_name, o.due_on::text AS due_on, o.recorded_at
  FROM app.receipt_occurrence o
  JOIN app.receipt_line l ON l.organization_id = o.organization_id AND l.id = o.line_id
  JOIN app.app_user u ON u.organization_id = o.organization_id AND u.id = o.owner_id
  LEFT JOIN app.product p ON p.organization_id = o.organization_id AND p.id = o.real_product_id
  WHERE o.document_id = $1
  ORDER BY l.line_number, o.recorded_at, o.id`;

function resumoDoDocumento(d: LinhaDocumentoLido): DocumentoResumo {
  return {
    id: d.id,
    emitente: { id: d.issuer_id, nome: d.issuer_name, identificacao: d.issuer_identification },
    tipo: d.doc_type,
    serie: d.series,
    numero: d.number,
    emissao: d.issued_on,
    recebimento: d.received_on,
    fazenda: { id: d.farm_id, nome: d.farm_name },
    status: d.status,
    versao: Number(d.version),
    registradoEm: d.recorded_at.toISOString(),
    contagens: {
      linhas: d.linhas,
      divergencias: d.divergencias,
      inspecoes: d.inspecoes,
      ocorrenciasAbertas: d.ocorrencias_abertas,
    },
  };
}

function linhaDoDocumento(l: LinhaDaLinhaLida): LinhaDoDocumento {
  return {
    id: l.id,
    numero: l.line_number,
    produto: { id: l.product_id, nome: l.product_name },
    lote: { id: l.lot_id, codigo: l.lot_code, tipo: l.lot_kind, validade: l.lot_expiry },
    local: { id: l.location_id, nome: l.location_name },
    documento: l.document_quantity,
    unidade: l.unit,
    conversao:
      l.conversion_id !== null && l.conversion_version !== null
        ? { id: l.conversion_id, versao: l.conversion_version }
        : null,
    parcelas: {
      apto: l.qty_apto,
      quarentena: l.qty_quarentena,
      bloqueado: l.qty_bloqueado,
      recusado: l.qty_recusado,
    },
    divergencia:
      l.divergence_reason === null ? null : { motivo: l.divergence_reason, texto: l.divergence_note },
    inspecao:
      l.inspection_owner_id !== null && l.inspection_owner_name !== null && l.inspection_due_on !== null
        ? {
            responsavel: { id: l.inspection_owner_id, nome: l.inspection_owner_name },
            prazo: l.inspection_due_on,
          }
        : null,
    pedidoLinha: l.external_order_line_ref,
    valorUnitario: l.unit_price,
    movimentos: l.movimentos,
  };
}

function ocorrenciaDoDocumento(o: LinhaOcorrenciaLida): OcorrenciaDoDocumento {
  return {
    id: o.id,
    linha: { id: o.line_id, numero: o.line_number },
    produtoReal:
      o.real_product_id !== null && o.real_product_name !== null
        ? { id: o.real_product_id, nome: o.real_product_name }
        : { descricao: o.real_product_description ?? '' },
    quantidade: o.counted_quantity,
    unidade: o.counted_unit,
    destino: o.destination,
    status: o.status,
    responsavel: { id: o.owner_id, nome: o.owner_name },
    prazo: o.due_on,
    registradaEm: o.recorded_at.toISOString(),
  };
}

/** Documentos de entrada visíveis na organização, do recebimento mais recente para o mais antigo. */
export async function listarDocumentos(cliente: ClientBase): Promise<DocumentoResumo[]> {
  const r = await cliente.query<LinhaDocumentoLido>(SELECT_DOCUMENTOS, [null]);
  return r.rows.map(resumoDoDocumento);
}

/**
 * Documento confirmado com a mesma origem fiscal (emitente, tipo, série e número), para avisar antes de confirmar (FO-18,
 * "Duplicidade"; contrato CMD-15 §6.3). Normaliza como o comando e o índice (identidadeDaOrigem). É auxiliar: o índice e
 * o recibo continuam a autoridade contra a duplicidade. Emitente fora do formato ou origem inválida: null, sem consultar.
 */
export async function documentoPorOrigem(
  cliente: ClientBase,
  origem: {
    readonly emitente: string;
    readonly tipo: string;
    readonly serie: string;
    readonly numero: string;
  },
): Promise<DocumentoResumo | null> {
  if (!ehUuid(origem.emitente)) return null;
  let id: ReturnType<typeof identidadeDaOrigem>;
  try {
    id = identidadeDaOrigem({ tipo: origem.tipo, serie: origem.serie, numero: origem.numero });
  } catch (erro) {
    if (erro instanceof ErroDominio) return null;
    throw erro;
  }
  const d = (
    await cliente.query<LinhaDocumentoLido>(SELECT_DOCUMENTO_POR_ORIGEM, [
      origem.emitente,
      id.tipo,
      id.serie,
      id.numero,
    ])
  ).rows[0];
  return d ? resumoDoDocumento(d) : null;
}

/**
 * Detalhe do documento: origem, linhas com parcelas, divergência, inspeção e vínculos com os movimentos, ocorrências e o
 * recibo do envelope. Id fora do formato, inexistente ou de outra organização: null, sem distinguir.
 */
export async function documento(cliente: ClientBase, id: string): Promise<DocumentoDetalhe | null> {
  if (!ehUuid(id)) return null;
  const d = (await cliente.query<LinhaDocumentoLido>(SELECT_DOCUMENTOS, [id])).rows[0];
  if (!d) return null;
  const linhas = await cliente.query<LinhaDaLinhaLida>(SELECT_LINHAS_DO_DOCUMENTO, [id]);
  const ocorrencias = await cliente.query<LinhaOcorrenciaLida>(SELECT_OCORRENCIAS_DO_DOCUMENTO, [id]);
  return {
    ...resumoDoDocumento(d),
    pedido:
      d.external_order_ref === null ? null : { sistema: d.external_system, referencia: d.external_order_ref },
    autor: { id: d.actor_id, nome: d.actor_name },
    recibo: await consultarIntencao(cliente, {
      commandType: d.intent_command_type,
      idempotencyKey: d.intent_key,
      actorId: null,
    }),
    linhas: linhas.rows.map(linhaDoDocumento),
    ocorrencias: ocorrencias.rows.map(ocorrenciaDoDocumento),
  };
}

// Opções do formulário de recebimento (FO-18; contrato CMD-15 §7.1) --------------------------------------------------
// O que a tela precisa para conferir sem digitar identificador: emitentes, fazendas com locais, produtos com a política
// de validade e de lote, embalagens na versão vigente e lotes de fabricante já existentes (a validade deles prevalece), e
// quem pode responder por inspeção ou ocorrência (usuários ativos). Tudo pela organização da sessão (RLS).

export interface ProdutoDoRecebimento extends Referencia {
  readonly unidade: string;
  readonly validade: PoliticaValidade;
  readonly lote: 'informado' | 'por_documento';
  /** Embalagens na versão mais recente, com o fator para a unidade-base em texto decimal. */
  readonly embalagens: readonly {
    readonly id: string;
    readonly nome: string;
    readonly fator: string;
    readonly versao: number;
  }[];
  /** Lotes de fabricante do produto, com a validade que um novo recebimento no mesmo lote tem de repetir. */
  readonly lotes: readonly { readonly codigo: string; readonly validade: string | null }[];
}

export interface OpcoesRecebimento {
  readonly emitentes: readonly (Referencia & { readonly identificacao: string })[];
  readonly fazendas: readonly (Referencia & { readonly locais: readonly Referencia[] })[];
  readonly produtos: readonly ProdutoDoRecebimento[];
  readonly responsaveis: readonly Referencia[];
}

export async function opcoesDoRecebimento(cliente: ClientBase): Promise<OpcoesRecebimento> {
  const emitentes = await cliente.query<{ id: string; name: string; identification: string }>(
    'SELECT id, name, identification FROM app.counterparty ORDER BY name, id',
  );
  const locais = await cliente.query<{ farm_id: string; farm_name: string; id: string; name: string }>(
    `SELECT f.id AS farm_id, f.name AS farm_name, s.id, s.name
       FROM app.farm f JOIN app.stock_location s ON s.organization_id = f.organization_id AND s.farm_id = f.id
      ORDER BY f.name, f.id, s.name, s.id`,
  );
  const produtos = await cliente.query<{
    id: string;
    name: string;
    base_unit: string;
    expiry_policy: PoliticaValidade;
    lot_policy: 'informado' | 'por_documento';
  }>('SELECT id, name, base_unit, expiry_policy, lot_policy FROM app.product ORDER BY name, id');
  const embalagens = await cliente.query<{
    id: string;
    product_id: string;
    packaging: string;
    factor: string;
    version: number;
  }>(
    `SELECT DISTINCT ON (product_id, packaging) id, product_id, packaging, factor::text AS factor, version
       FROM app.packaging_conversion WHERE valid_from <= now()
      ORDER BY product_id, packaging, version DESC`,
  );
  const lotes = await cliente.query<{ product_id: string; code: string; expiry_date: string | null }>(
    `SELECT product_id, code, expiry_date::text AS expiry_date FROM app.lot
      WHERE kind = 'fabricante' ORDER BY product_id, code`,
  );
  const responsaveis = await cliente.query<{ id: string; name: string }>(
    'SELECT id, name FROM app.app_user WHERE active ORDER BY name, id',
  );
  const fazendas = new Map<string, { id: string; nome: string; locais: Referencia[] }>();
  for (const l of locais.rows) {
    const f = fazendas.get(l.farm_id) ?? { id: l.farm_id, nome: l.farm_name, locais: [] };
    f.locais.push({ id: l.id, nome: l.name });
    fazendas.set(l.farm_id, f);
  }
  return {
    emitentes: emitentes.rows.map((e) => ({ id: e.id, nome: e.name, identificacao: e.identification })),
    fazendas: [...fazendas.values()],
    produtos: produtos.rows.map((p) => ({
      id: p.id,
      nome: p.name,
      unidade: p.base_unit,
      validade: p.expiry_policy,
      lote: p.lot_policy,
      embalagens: embalagens.rows
        .filter((c) => c.product_id === p.id)
        .map((c) => ({ id: c.id, nome: c.packaging, fator: c.factor, versao: c.version })),
      lotes: lotes.rows
        .filter((l) => l.product_id === p.id)
        .map((l) => ({ codigo: l.code, validade: l.expiry_date })),
    })),
    responsaveis: responsaveis.rows.map((u) => ({ id: u.id, nome: u.name })),
  };
}
