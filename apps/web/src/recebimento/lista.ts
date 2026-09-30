import type { DocumentoDetalhe, DocumentoResumo, LinhaDoDocumento, OrigemDocumento } from '@safrion/db/web';

import type { EstadoExibido } from '../estoque/estado';
import { formatarData } from '../formato/data';
import { formatarQuantidade, positivo } from '../formato/numero';
import type { ColunaG2, LinhaG2 } from '../tabela/logica';
import { NOMES_DOS_MOTIVOS } from './formulario';

/**
 * Do dado do banco para a tela de Recebimentos (contrato CMD-15 §7.1): nome do documento, estado com palavra, linhas da
 * G2 e pendências com quem resolve e o prazo. A cor sai do papel, nunca sozinha (DS-24).
 */
/** CNPJ (14 dígitos) e CPF (11) com a máscara de costume; outra identificação cadastral aparece como veio. */
export function formatarIdentificacao(id: string): string {
  if (/^\d{14}$/.test(id)) return id.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5');
  if (/^\d{11}$/.test(id)) return id.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4');
  return id;
}

export function rotuloDoDocumento(d: Pick<OrigemDocumento, 'tipo' | 'serie' | 'numero'>): string {
  const sigla = d.tipo === 'nfe' ? 'NF' : 'Doc';
  return d.serie === '' ? `${sigla} ${d.numero}` : `${sigla} ${d.serie}/${d.numero}`;
}

/** Lote interno do granel com nome legível; nunca DOC:<uuid> para quem lê (contrato CMD-15 §1 e §7.1). */
export function nomeDoGranel(
  g: Pick<OrigemDocumento, 'tipo' | 'serie' | 'numero'> & { readonly emitente: string },
) {
  return `Granel · ${rotuloDoDocumento(g)} · ${g.emitente}`;
}

/** Estado do documento: pendência primeiro, pela mesma ordem da próxima ação do recibo (inspeção, depois divergência). */
export function estadoDoDocumento(d: Pick<DocumentoResumo, 'status' | 'contagens'>): EstadoExibido {
  if (d.status === 'estornado') return { palavra: 'Estornado', papel: 'neutro' };
  if (d.contagens.inspecoes > 0) return { palavra: 'Inspeção pendente', papel: 'atencao' };
  if (d.contagens.divergencias > 0 || d.contagens.ocorrenciasAbertas > 0)
    return { palavra: 'Divergência aberta', papel: 'atencao' };
  return { palavra: 'Conforme', papel: 'sucesso' };
}

export const COLUNAS_DOCUMENTO: readonly ColunaG2[] = [
  { chave: 'documento', rotulo: 'Documento', tipo: 'texto' },
  { chave: 'emitente', rotulo: 'Emitente', tipo: 'texto', agrupavel: true },
  { chave: 'recebido', rotulo: 'Recebido em', tipo: 'data' },
  { chave: 'estado', rotulo: 'Estado', tipo: 'estado', agrupavel: true },
  { chave: 'linhas', rotulo: 'Linhas', tipo: 'numero' },
  { chave: 'pendencias', rotulo: 'Pendências', tipo: 'texto' },
];

const plural = (n: number, um: string, varios: string) => `${String(n)} ${n === 1 ? um : varios}`;

function textoDasPendencias(c: DocumentoResumo['contagens']): string {
  const partes = [
    c.divergencias > 0 ? plural(c.divergencias, 'divergência', 'divergências') : '',
    c.inspecoes > 0 ? plural(c.inspecoes, 'inspeção', 'inspeções') : '',
    c.ocorrenciasAbertas > 0 ? plural(c.ocorrenciasAbertas, 'ocorrência', 'ocorrências') : '',
  ].filter(Boolean);
  return partes.length === 0 ? 'Nenhuma' : partes.join(' · ');
}

export function linhaDoDocumento(d: DocumentoResumo): LinhaG2 {
  const estado = estadoDoDocumento(d);
  const nome = rotuloDoDocumento(d);
  const pendencias = textoDasPendencias(d.contagens);
  return {
    id: d.id,
    href: `/estoque/recebimentos/${d.id}`,
    celulas: {
      documento: { texto: nome, valor: nome },
      emitente: { texto: d.emitente.nome, valor: d.emitente.nome },
      recebido: { texto: formatarData(d.recebimento), valor: d.recebimento },
      estado: { texto: estado.palavra, valor: estado.palavra, papel: estado.papel },
      linhas: { texto: String(d.contagens.linhas), valor: String(d.contagens.linhas) },
      pendencias: { texto: pendencias, valor: pendencias === 'Nenhuma' ? '' : pendencias },
    },
  };
}

/** Linha conferida: divergência aberta, em inspeção ou conforme. */
export function estadoDaLinha(l: LinhaDoDocumento): EstadoExibido {
  if (l.divergencia) return { palavra: 'Divergência aberta', papel: 'atencao' };
  if (l.inspecao) return { palavra: 'Em inspeção', papel: 'atencao' };
  return { palavra: 'Conforme', papel: 'sucesso' };
}

/** "2 apto · 1 bloqueado", na unidade da linha; sem parcela, "Nada conferido". */
export function textoDaConferencia(l: Pick<LinhaDoDocumento, 'parcelas' | 'unidade'>): string {
  const q = (v: string) => formatarQuantidade(v, l.unidade);
  const partes = [
    positivo(l.parcelas.apto) ? `${q(l.parcelas.apto)} apto` : '',
    positivo(l.parcelas.quarentena) ? `${q(l.parcelas.quarentena)} em inspeção` : '',
    positivo(l.parcelas.bloqueado) ? `${q(l.parcelas.bloqueado)} bloqueado` : '',
    positivo(l.parcelas.recusado) ? `${q(l.parcelas.recusado)} recusado` : '',
  ].filter(Boolean);
  return partes.length === 0 ? 'Nada conferido' : partes.join(' · ');
}

export const COLUNAS_LINHA_DO_DOCUMENTO: readonly ColunaG2[] = [
  { chave: 'numero', rotulo: 'Linha', tipo: 'numero' },
  { chave: 'produto', rotulo: 'Produto', tipo: 'texto', agrupavel: true },
  { chave: 'lote', rotulo: 'Lote', tipo: 'texto' },
  { chave: 'documento', rotulo: 'No documento', tipo: 'texto' },
  { chave: 'conferido', rotulo: 'Conferido', tipo: 'texto' },
  { chave: 'estado', rotulo: 'Situação', tipo: 'estado', agrupavel: true },
];

/** A linha abre o lote, onde estão o saldo e o extrato; o lote do granel aparece pelo nome legível. */
export function linhaDaLinhaDoDocumento(
  l: LinhaDoDocumento,
  documento: Pick<DocumentoDetalhe, 'tipo' | 'serie' | 'numero' | 'emitente'>,
): LinhaG2 {
  const estado = estadoDaLinha(l);
  const lote =
    l.lote.tipo === 'agrupamento_interno'
      ? nomeDoGranel({ ...documento, emitente: documento.emitente.nome })
      : `${l.lote.codigo} · ${l.lote.validade === null ? 'validade não se aplica' : `validade ${formatarData(l.lote.validade)}`}`;
  const noDocumento = formatarQuantidade(l.documento, l.unidade);
  const conferido = textoDaConferencia(l);
  return {
    id: l.id,
    href: `/estoque/${l.lote.id}`,
    celulas: {
      numero: { texto: String(l.numero), valor: String(l.numero) },
      produto: { texto: l.produto.nome, valor: l.produto.nome },
      lote: { texto: lote, valor: lote },
      documento: { texto: noDocumento, valor: noDocumento },
      conferido: { texto: conferido, valor: conferido },
      estado: { texto: estado.palavra, valor: estado.palavra, papel: estado.papel },
    },
  };
}

export interface Pendencia {
  readonly tipo: 'Inspeção pendente' | 'Divergência aberta' | 'Ocorrência aberta';
  readonly linha: number;
  readonly descricao: string;
  /** Quem resolve: o responsável escolhido, ou quem registrou o recebimento (responsável contextual, §6). */
  readonly responsavel: string;
  readonly prazo: string | null;
}

/** Pendências do documento, na ordem da próxima ação do recibo: inspeções, divergências e ocorrências abertas. */
export function pendenciasDoDocumento(d: DocumentoDetalhe): Pendencia[] {
  const autor = d.autor.nome ?? 'Quem registrou o recebimento';
  const inspecoes: Pendencia[] = d.linhas.flatMap((l) =>
    l.inspecao
      ? [
          {
            tipo: 'Inspeção pendente' as const,
            linha: l.numero,
            descricao: `${formatarQuantidade(l.parcelas.quarentena, l.unidade)} de ${l.produto.nome} em inspeção`,
            responsavel: l.inspecao.responsavel.nome,
            prazo: l.inspecao.prazo,
          },
        ]
      : [],
  );
  const divergencias: Pendencia[] = d.linhas.flatMap((l) =>
    l.divergencia
      ? [
          {
            tipo: 'Divergência aberta' as const,
            linha: l.numero,
            descricao: `${NOMES_DOS_MOTIVOS[l.divergencia.motivo]}${l.divergencia.texto ? `: ${l.divergencia.texto}` : ''} · ${l.produto.nome}`,
            responsavel: autor,
            prazo: null,
          },
        ]
      : [],
  );
  const ocorrencias: Pendencia[] = d.ocorrencias
    .filter((o) => o.status === 'aberta')
    .map((o) => ({
      tipo: 'Ocorrência aberta' as const,
      linha: o.linha.numero,
      descricao: `Chegou ${'nome' in o.produtoReal ? o.produtoReal.nome : o.produtoReal.descricao} · ${formatarQuantidade(o.quantidade, o.unidade)} · retido para decisão`,
      responsavel: o.responsavel.nome,
      prazo: o.prazo,
    }));
  return [...inspecoes, ...divergencias, ...ocorrencias];
}
