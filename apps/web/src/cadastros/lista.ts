import type { FazendaResumo, TalhaoResumo } from '@safrion/db/web';

import { formatarData, formatarInstante } from '../formato/data';
import { estadoDaUrl, urlDoEstado, type ColunaG2, type EstadoG2, type LinhaG2 } from '../tabela/logica';

export const COLUNAS_TALHAO: readonly ColunaG2[] = [
  { chave: 'talhao', rotulo: 'Talhão', tipo: 'texto' },
  { chave: 'area', rotulo: 'Área (ha)', tipo: 'numero' },
  { chave: 'limite', rotulo: 'Limite', tipo: 'texto', agrupavel: true },
  { chave: 'situacao', rotulo: 'Situação', tipo: 'estado', agrupavel: true },
];

/** Duas casas na tela, sem converter o decimal do banco em ponto flutuante. */
export function formatarAreaHa(valor: string): string {
  const partes = /^(\d+)(?:\.(\d{1,6}))?$/.exec(valor);
  if (!partes) throw new Error('Área fora do formato canônico.');
  const inteiro = partes[1] as string;
  const fracao = (partes[2] ?? '').padEnd(6, '0');
  const micros = BigInt(inteiro) * 1_000_000n + BigInt(fracao);
  const centesimos = (micros + 5_000n) / 10_000n;
  if (micros > 0n && centesimos === 0n) return '< 0,01';
  const agrupado = (centesimos / 100n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return `${agrupado},${(centesimos % 100n).toString().padStart(2, '0')}`;
}

export interface FiltrosListaAreas {
  readonly fazenda: string;
  readonly situacao: TalhaoResumo['situacao'] | '';
}

export function filtrosDaLista(parametros: URLSearchParams): FiltrosListaAreas {
  const situacao = parametros.get('situacao');
  return {
    fazenda: parametros.get('fazenda') ?? '',
    situacao: situacao === 'ativo' || situacao === 'inativo' ? situacao : '',
  };
}

/** Os totais vêm da leitura autorizada de todos os ativos; filtros da lista não os recalculam. */
export function gruposDeFazenda(
  fazendas: readonly FazendaResumo[],
  talhoes: readonly TalhaoResumo[],
  filtros: FiltrosListaAreas,
): { readonly fazenda: FazendaResumo; readonly talhoes: readonly TalhaoResumo[] }[] {
  return fazendas
    .filter((fazenda) => filtros.fazenda === '' || fazenda.id === filtros.fazenda)
    .map((fazenda) => ({
      fazenda,
      talhoes: talhoes.filter(
        (talhao) =>
          talhao.fazenda.id === fazenda.id &&
          (filtros.situacao === '' || talhao.situacao === filtros.situacao),
      ),
    }));
}

/** Troca só o estado da G2: filtros de fazenda/situação e contexto do painel permanecem. */
export function consultaComEstadoTabela(parametros: URLSearchParams, estado: EstadoG2): URLSearchParams {
  const novos = new URLSearchParams(parametros);
  for (const chave of ['ordem', 'busca', 'agrupar']) novos.delete(chave);
  for (const coluna of COLUNAS_TALHAO) {
    for (const prefixo of ['v.', 'c.', 'de.', 'ate.']) novos.delete(`${prefixo}${coluna.chave}`);
  }
  for (const [chave, valor] of urlDoEstado(estado)) novos.append(chave, valor);
  return novos;
}

/** Só a consulta navegável da listagem volta do detalhe; não reabre criação nem replica `volta`. */
export function consultaDeRetorno(parametros: URLSearchParams): string {
  const consulta = urlDoEstado(estadoDaUrl(parametros, COLUNAS_TALHAO));
  const filtros = filtrosDaLista(parametros);
  if (filtros.fazenda) consulta.set('fazenda', filtros.fazenda);
  if (filtros.situacao) consulta.set('situacao', filtros.situacao);
  return consulta.toString();
}

export function hrefComRetorno(href: string, consulta: string): string {
  return consulta === '' ? href : `${href}?${new URLSearchParams({ volta: consulta }).toString()}`;
}

export function linhaDoTalhao(talhao: TalhaoResumo, consulta = '', fuso?: string): LinhaG2 {
  const limite = talhao.limite;
  const data = limite
    ? /^\d{4}-\d{2}-\d{2}$/.test(limite.data)
      ? formatarData(limite.data)
      : formatarInstante(limite.data, fuso)
    : '';
  const textoLimite = limite ? `Versão ${String(limite.versao)} · ${data}` : 'Sem limite no mapa';
  return {
    id: talhao.id,
    href: hrefComRetorno(`/cadastros/areas/${encodeURIComponent(talhao.id)}`, consulta),
    celulas: {
      talhao: { texto: talhao.nome, valor: talhao.nome },
      area: {
        texto: `${formatarAreaHa(talhao.areaReferenciaHa)} · ${talhao.origemArea}`,
        valor: talhao.areaReferenciaHa,
        unidade: 'ha',
      },
      limite: { texto: textoLimite, valor: textoLimite },
      situacao: {
        texto: talhao.situacao === 'ativo' ? 'Ativo' : 'Inativo',
        valor: talhao.situacao,
        papel: talhao.situacao === 'ativo' ? 'sucesso' : 'neutro',
      },
    },
  };
}
