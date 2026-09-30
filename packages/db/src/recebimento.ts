import { randomUUID } from 'node:crypto';

import type { DadosRecebimento } from '@safrion/contracts';
import {
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
  type LinhaConferida,
  type MovimentoDaParcela,
  type PoliticaValidade,
  type UnidadeDaLinha,
} from '@safrion/domain';
import type { PoolClient } from 'pg';

import type { Efeito } from './comando.js';
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
