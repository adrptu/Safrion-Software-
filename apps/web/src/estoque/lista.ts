import { UNIDADES, type CodigoUnidade } from '@safrion/domain';
import type { LinhaExtrato, LoteResumo, ProdutoResumo } from '@safrion/db/web';

import { formatarData, formatarInstante } from '../formato/data';
import { formatarQuantidade, rotuloUnidade } from '../formato/numero';
import { nomeDoGranel, rotuloDoDocumento } from '../recebimento/lista';
import type { ColunaG2, LinhaG2 } from '../tabela/logica';
import { estadoDoLote, palavraDaSituacao } from './estado';

/**
 * Do dado do banco para as linhas da G2, nas telas de Estoque e Cadastros. Até sete colunas úteis (4.3): o que decide
 * qual lote abrir. Utilizável e físico somam no grupo e no total quando a unidade é a mesma.
 */
export const COLUNAS_LOTE: readonly ColunaG2[] = [
  { chave: 'lote', rotulo: 'Lote', tipo: 'texto' },
  { chave: 'produto', rotulo: 'Produto', tipo: 'texto', agrupavel: true },
  { chave: 'validade', rotulo: 'Validade', tipo: 'data' },
  { chave: 'estado', rotulo: 'Estado', tipo: 'estado', agrupavel: true },
  { chave: 'utilizavel', rotulo: 'Utilizável', tipo: 'numero', somavel: true },
  { chave: 'fisico', rotulo: 'Físico', tipo: 'numero', somavel: true },
];

/** Os lotes de um produto: a coluna Produto sai porque é a mesma em todas as linhas. */
export const COLUNAS_LOTE_DO_PRODUTO: readonly ColunaG2[] = COLUNAS_LOTE.filter((c) => c.chave !== 'produto');

/** Validade na tela: a data em pt-BR, ou "Não se aplica" quando o lote não tem validade (RN-032). */
function textoDaValidade(validade: string | null): string {
  return validade === null ? 'Não se aplica' : formatarData(validade);
}

/** Nome do lote para quem lê: o código do fabricante, ou "Granel · NF 1/7001 · emitente" no lote interno. */
export function nomeDoLote(l: Pick<LoteResumo, 'codigo' | 'granel'>): string {
  return l.granel ? nomeDoGranel(l.granel) : l.codigo;
}

/** Linha de contexto do cabeçalho do detalhe do lote: produto e validade. */
export function contextoDoLote(l: Pick<LoteResumo, 'produto' | 'validade'>): string {
  return `${l.produto} · validade ${l.validade === null ? 'não se aplica' : formatarData(l.validade)}`;
}

export function linhaDoLote(l: LoteResumo): LinhaG2 {
  const estado = estadoDoLote(l.movimentos, l.saldo);
  const medida = (valor: string) => ({
    texto: formatarQuantidade(valor, l.unidade),
    valor,
    unidade: l.unidade,
  });
  return {
    id: l.id,
    href: `/estoque/${l.id}`,
    celulas: {
      lote: { texto: nomeDoLote(l), valor: nomeDoLote(l) },
      produto: { texto: l.produto, valor: l.produto },
      // Sem validade o valor é vazio: vai para o fim em qualquer direção e o filtro ∅ o encontra.
      validade: { texto: textoDaValidade(l.validade), valor: l.validade ?? '' },
      estado: { texto: estado.palavra, valor: estado.palavra, papel: estado.papel },
      utilizavel: medida(l.saldo.utilizavel),
      fisico: medida(l.saldo.fisico),
    },
  };
}

export const COLUNAS_PRODUTO: readonly ColunaG2[] = [
  { chave: 'produto', rotulo: 'Produto', tipo: 'texto' },
  { chave: 'unidade', rotulo: 'Unidade', tipo: 'texto', agrupavel: true },
  { chave: 'lotes', rotulo: 'Lotes', tipo: 'numero' },
];

export function linhaDoProduto(p: ProdutoResumo): LinhaG2 {
  return {
    id: p.id,
    href: `/cadastros/produtos/${p.id}`,
    celulas: {
      produto: { texto: p.nome, valor: p.nome },
      unidade: { texto: rotuloUnidade(p.unidade), valor: p.unidade },
      lotes: { texto: String(p.lotes), valor: String(p.lotes) },
    },
  };
}

export const COLUNAS_EXTRATO: readonly ColunaG2[] = [
  { chave: 'quando', rotulo: 'Registrado em', tipo: 'data' },
  { chave: 'movimento', rotulo: 'Movimento', tipo: 'texto', agrupavel: true },
  { chave: 'quantidade', rotulo: 'Quantidade', tipo: 'numero', somavel: true },
  { chave: 'local', rotulo: 'Local', tipo: 'texto', agrupavel: true },
  { chave: 'origem', rotulo: 'Origem', tipo: 'texto', agrupavel: true },
];

function nomeDoMovimento(m: LinhaExtrato): string {
  if (m.kind === 'entrada') return `Entrada · ${palavraDaSituacao(m.situacao)}`;
  if (m.kind === 'mudanca') return `${palavraDaSituacao(m.de)} → ${palavraDaSituacao(m.para)}`;
  return 'Estorno';
}

/**
 * Linha do extrato: a quantidade na unidade-base do lote (a que soma) e, quando o registro foi em outra unidade, a
 * original entre parênteses, para conferir com o documento.
 */
export function linhaDoMovimento(m: LinhaExtrato, locais: ReadonlyMap<string, string>): LinhaG2 {
  const base =
    m.baseQuantity !== null && m.baseUnit !== null ? formatarQuantidade(m.baseQuantity, m.baseUnit) : '';
  const original =
    m.originalQuantity !== null && m.originalUnit !== null && m.originalUnit !== m.baseUnit
      ? ` (${formatarQuantidade(m.originalQuantity, m.originalUnit)})`
      : '';
  // O movimento de um recebimento abre o documento de origem (trilha lote → linha → documento, contrato CMD-15 §7).
  const origem = m.origem
    ? `${rotuloDoDocumento(m.origem)} · linha ${String(m.origem.linha)}`
    : 'Entrada manual';
  return {
    id: m.movementId,
    href: m.origem ? `/estoque/recebimentos/${m.origem.documentoId}` : '',
    celulas: {
      quando: { texto: formatarInstante(m.recordedAt), valor: m.recordedAt },
      movimento: { texto: nomeDoMovimento(m), valor: nomeDoMovimento(m) },
      quantidade:
        m.baseQuantity !== null && m.baseUnit !== null
          ? { texto: `${base}${original}`, valor: m.baseQuantity, unidade: m.baseUnit }
          : { texto: '—', valor: '' },
      local: {
        texto: locais.get(m.locationId) ?? 'Local indisponível',
        valor: locais.get(m.locationId) ?? '',
      },
      origem: { texto: origem, valor: origem },
    },
  };
}

/** Unidades da mesma dimensão da unidade-base do lote, a base primeiro (a sugestão vem do cadastro do produto). */
export function unidadesDoLote(base: string): { readonly valor: string; readonly rotulo: string }[] {
  if (!Object.hasOwn(UNIDADES, base)) return [];
  const dimensao = UNIDADES[base as CodigoUnidade].dimensao;
  return (Object.keys(UNIDADES) as CodigoUnidade[])
    .filter((u) => UNIDADES[u].dimensao === dimensao)
    .sort((a, b) => Number(b === base) - Number(a === base))
    .map((u) => ({ valor: u, rotulo: rotuloUnidade(u) }));
}
