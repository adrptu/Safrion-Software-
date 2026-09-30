import type { Decimal } from 'decimal.js';

import { decimal } from './decimal.js';
import { ErroDominio } from './erros.js';
import { dataCivil, type DataCivil, type Movimento, type Situacao } from './saldo.js';
import {
  embalagensParaBase,
  ehUnidade,
  quantidade,
  type ConversaoEmbalagem,
  type OrigemEmbalagem,
  type Quantidade,
} from './unidades.js';

/**
 * Recebimento de insumos por documento e inspeção (SU-06, CMD-15, AC-14; contrato CMD-15 v3.1). Regras puras: o que foi
 * conferido em cada linha vira parcelas; só as parcelas físicas viram movimento; divergência, validade, lote interno de
 * granel e ocorrência de produto diferente são decididos aqui, sem banco.
 */

/** Parcelas da conferência, na unidade da linha. O recusado não entra no físico nem gera movimento. */
export type Parcela = 'apto' | 'quarentena' | 'bloqueado' | 'recusado';
export const PARCELAS: readonly Parcela[] = ['apto', 'quarentena', 'bloqueado', 'recusado'];

/** Situação do movimento de cada parcela física (RN-015). Recusado: nenhum movimento. */
export const SITUACAO_DA_PARCELA: Readonly<Record<Parcela, Situacao | null>> = {
  apto: 'liberado_livre',
  quarentena: 'quarentena_livre',
  bloqueado: 'liberado_bloqueado',
  recusado: null,
};

export type MotivoDivergencia = 'avaria' | 'validade' | 'produto_diferente' | 'falta' | 'sobra' | 'outro';
export const MOTIVOS: readonly MotivoDivergencia[] = [
  'avaria',
  'validade',
  'produto_diferente',
  'falta',
  'sobra',
  'outro',
];

/** Unidade da linha: de medida (L, kg, un…) ou embalagem com conversão versionada (galão de 5 L, v1). */
export type UnidadeDaLinha =
  | { readonly tipo: 'medida'; readonly unidade: string }
  | { readonly tipo: 'embalagem'; readonly conversao: ConversaoEmbalagem };

export interface LinhaConferida {
  readonly numero: number;
  readonly unidade: UnidadeDaLinha;
  /** Quantidade do documento, em texto decimal canônico. */
  readonly documento: string;
  readonly parcelas: Readonly<Record<Parcela, string>>;
  readonly motivo?: MotivoDivergencia;
  readonly motivoTexto?: string;
  /** Responsável e prazo (data civil) da decisão da quarentena: obrigatórios só com quarentena. */
  readonly inspecao?: { readonly responsavel: string; readonly prazo: string };
}

export interface ResultadoLinha {
  readonly conferido: Decimal;
  readonly fisico: Decimal;
  readonly divergente: boolean;
  readonly inspecaoPendente: boolean;
}

const MAX_LINHAS = 50;

function invalido(mensagem: string): never {
  throw new ErroDominio('RECEBIMENTO_INVALIDO', mensagem);
}

/** Decimal ≥ 0 na unidade da linha; embalagem e unidade de contagem só inteiros. */
function parcela(valor: unknown, u: UnidadeDaLinha, nome: string): Decimal {
  const d = decimal(valor);
  if (d.isNegative()) invalido(`A parcela "${nome}" não pode ser negativa.`);
  if (u.tipo === 'embalagem' && !d.isInteger()) invalido(`A parcela "${nome}" conta embalagens inteiras.`);
  return d;
}

function unidadeValida(u: unknown): UnidadeDaLinha {
  const x = u as Partial<Record<string, unknown>> | null;
  if (typeof x === 'object' && x !== null && x['tipo'] === 'medida' && ehUnidade(x['unidade'])) {
    return { tipo: 'medida', unidade: x['unidade'] };
  }
  if (
    typeof x === 'object' &&
    x !== null &&
    x['tipo'] === 'embalagem' &&
    typeof x['conversao'] === 'object'
  ) {
    return { tipo: 'embalagem', conversao: x['conversao'] as ConversaoEmbalagem };
  }
  return invalido('A linha precisa de unidade de medida cadastrada ou de embalagem com conversão.');
}

/**
 * Confere uma linha: parcelas não negativas; conferido = soma das quatro; físico = apto + quarentena + bloqueado.
 * Divergente quando o conferido difere do documento, ou quando há bloqueado ou recusado; divergência exige motivo da
 * lista fechada ("outro" com texto), e motivo sem divergência é recusado. Quarentena sozinha não é divergência: é
 * inspeção pendente, com responsável e prazo.
 */
export function conferirLinha(l: LinhaConferida): ResultadoLinha {
  const bruto: unknown = l;
  if (typeof bruto !== 'object' || bruto === null) invalido('A linha precisa ser um objeto.');
  if (!Number.isInteger(l.numero) || l.numero < 1 || l.numero > MAX_LINHAS) {
    invalido(`O número da linha vai de 1 a ${String(MAX_LINHAS)}.`);
  }
  const u = unidadeValida(l.unidade);
  const doc = decimal(l.documento);
  if (!doc.greaterThan(0)) invalido('A quantidade do documento deve ser maior que zero.');
  if (u.tipo === 'embalagem' && !doc.isInteger()) invalido('O documento conta embalagens inteiras.');
  const partes = l.parcelas as Partial<Record<Parcela, unknown>> | null;
  if (typeof partes !== 'object' || partes === null) invalido('A linha precisa das quatro parcelas.');
  const [apto, quarentena, bloqueado, recusado] = PARCELAS.map((p) => parcela(partes[p], u, p)) as [
    Decimal,
    Decimal,
    Decimal,
    Decimal,
  ];
  const fisico = apto.plus(quarentena).plus(bloqueado);
  const conferido = fisico.plus(recusado);
  const divergente = !conferido.equals(doc) || bloqueado.greaterThan(0) || recusado.greaterThan(0);

  if (divergente) {
    if (l.motivo === undefined || !MOTIVOS.includes(l.motivo)) {
      invalido('Divergência (falta, sobra, bloqueio ou recusa) exige motivo da lista.');
    }
    if (l.motivo === 'outro' && (typeof l.motivoTexto !== 'string' || l.motivoTexto.trim() === '')) {
      invalido('Motivo "outro" exige texto.');
    }
    if (l.motivo === 'falta' && !conferido.lessThan(doc))
      invalido('"Falta" só quando o conferido é menor que o documento.');
    if (l.motivo === 'sobra' && !conferido.greaterThan(doc))
      invalido('"Sobra" só quando o conferido é maior que o documento.');
  } else if (l.motivo !== undefined || l.motivoTexto !== undefined) {
    invalido('Sem divergência, a linha não leva motivo.');
  }

  const inspecaoPendente = quarentena.greaterThan(0);
  if (inspecaoPendente) {
    const i: unknown = l.inspecao;
    const x = typeof i === 'object' && i !== null ? (i as Partial<Record<string, unknown>>) : null;
    const responsavel = x?.['responsavel'];
    if (typeof responsavel !== 'string' || responsavel.trim() === '') {
      invalido('Quarentena exige responsável e prazo da decisão.');
    }
    dataCivil(x?.['prazo']);
  } else if (l.inspecao !== undefined) {
    invalido('Responsável e prazo de inspeção só com quarentena.');
  }
  return { conferido, fisico, divergente, inspecaoPendente };
}

/** Movimento de uma parcela física, pronto para o saldo do lote (o recusado e as parcelas zero ficam de fora). */
export interface MovimentoDaParcela {
  readonly parcela: Exclude<Parcela, 'recusado'>;
  readonly movimento: Movimento & { readonly tipo: 'entrada' };
}

/**
 * Entradas de uma linha já conferida, na ordem apto → quarentena → bloqueado, só para parcelas maiores que zero. Com
 * embalagem, cada parcela vira base pela conversão da linha e guarda a origem ("3 galão 5 L", v1). Os ids vêm de fora
 * (quem grava decide), um por movimento, na ordem.
 */
export function movimentosDaLinha(l: LinhaConferida, ids: () => string): MovimentoDaParcela[] {
  conferirLinha(l);
  const u = unidadeValida(l.unidade);
  const saida: MovimentoDaParcela[] = [];
  for (const p of ['apto', 'quarentena', 'bloqueado'] as const) {
    const v = parcela(l.parcelas[p], u, p);
    if (v.isZero()) continue;
    const situacao = SITUACAO_DA_PARCELA[p] as Situacao;
    let q: Quantidade;
    let origem: OrigemEmbalagem | undefined;
    if (u.tipo === 'embalagem') {
      const r = embalagensParaBase(v.toFixed(0), u.conversao);
      q = r.quantidade;
      origem = r.origem;
    } else {
      q = quantidade(v.toString(), u.unidade);
    }
    const movimento = origem
      ? { id: ids(), tipo: 'entrada' as const, quantidade: q, situacao, origem }
      : { id: ids(), tipo: 'entrada' as const, quantidade: q, situacao };
    saida.push({ parcela: p, movimento });
  }
  return saida;
}

/** Numeração dos movimentos na intenção inteira (intent_item 1..M), na ordem das linhas e das parcelas. */
export function numerarMovimentos(
  linhas: readonly { readonly numero: number; readonly movimentos: readonly MovimentoDaParcela[] }[],
): { readonly linha: number; readonly item: number; readonly movimento: MovimentoDaParcela }[] {
  const ordenadas = [...linhas].sort((a, b) => a.numero - b.numero);
  const numeros = new Set(ordenadas.map((l) => l.numero));
  if (numeros.size !== ordenadas.length) invalido('Número de linha repetido no documento.');
  let item = 0;
  return ordenadas.flatMap((l) => l.movimentos.map((m) => ({ linha: l.numero, item: ++item, movimento: m })));
}

export type PoliticaValidade = 'controla' | 'nao_se_aplica';

/**
 * Validade da linha (RN-032, contrato §5). Lote existente: vale a validade congelada no lote, mesmo que a política do
 * produto tenha mudado depois. Lote novo: vale a política vigente do produto. "Não se aplica" é null, nunca data
 * fictícia.
 */
export function validadeNoRecebimento(p: {
  readonly politicaProduto: PoliticaValidade;
  readonly loteExistente?: { readonly validade: DataCivil | null };
  readonly informada: string | null;
}): DataCivil | null {
  const informada = p.informada === null ? null : dataCivil(p.informada);
  if (p.loteExistente !== undefined) {
    const doLote = p.loteExistente.validade;
    if (doLote === null) {
      if (informada !== null) {
        throw new ErroDominio('VALIDADE_NAO_SE_APLICA', 'Este lote não tem validade; não informe data.');
      }
      return null;
    }
    if (informada === null) {
      throw new ErroDominio('VALIDADE_OBRIGATORIA', 'Este lote tem validade; informe a mesma data do lote.');
    }
    if (informada !== doLote) {
      throw new ErroDominio('VALIDADE_DIFERENTE_DO_LOTE', 'A validade informada difere da validade do lote.');
    }
    return doLote;
  }
  const politica: unknown = p.politicaProduto;
  if (politica === 'nao_se_aplica') {
    if (informada !== null) {
      throw new ErroDominio(
        'VALIDADE_NAO_SE_APLICA',
        'A validade não se aplica a este produto; não informe data.',
      );
    }
    return null;
  }
  if (politica !== 'controla') invalido('Política de validade do produto desconhecida.');
  if (informada === null) {
    throw new ErroDominio('VALIDADE_OBRIGATORIA', 'Este produto controla validade; informe a data.');
  }
  return informada;
}

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

/**
 * Código do lote interno de granel (produto "por documento"): DOC:<id do documento>. O id é o UUID persistido do
 * documento, então duas NF de emitentes diferentes com o mesmo número não se misturam, e o reenvio da mesma intenção
 * reusa o mesmo lote. Não é lote do fabricante.
 */
export function codigoLoteInterno(documentoId: string): string {
  if (typeof documentoId !== 'string' || !UUID.test(documentoId)) {
    throw new ErroDominio(
      'LOTE_INTERNO_INVALIDO',
      'O lote interno precisa do id do documento (UUID em minúsculas).',
    );
  }
  return `DOC:${documentoId}`;
}

/** Série e número normalizados para a identidade da origem: sem espaços nas pontas, NFC, sem zeros à esquerda. */
export function identidadeDaOrigem(o: {
  readonly tipo: string;
  readonly serie: string;
  readonly numero: string;
}): {
  readonly tipo: 'nfe' | 'outro';
  readonly serie: string;
  readonly numero: string;
} {
  if (o.tipo !== 'nfe' && o.tipo !== 'outro') invalido('Tipo de documento: nfe ou outro.');
  if (typeof o.serie !== 'string' || typeof o.numero !== 'string') invalido('Série e número em texto.');
  const norm = (s: string) => {
    const t = s.normalize('NFC').trim();
    return /^[0-9]+$/.test(t) ? t.replace(/^0+(?=[0-9])/, '') : t;
  };
  const serie = norm(o.serie);
  const numero = norm(o.numero);
  if (numero === '' || numero.length > 20 || serie.length > 8)
    invalido('Número de 1 a 20 caracteres; série até 8.');
  return { tipo: o.tipo, serie, numero };
}

export type DestinoOcorrencia = 'retido_para_decisao' | 'devolvido_na_entrega';

export interface OcorrenciaDeChegada {
  readonly produtoReal: { readonly produtoId: string } | { readonly descricao: string };
  /** Como foi contado: quantidade e unidade reais, sem converter pelo cadastro do produto do documento. */
  readonly quantidade: string;
  readonly unidade: string;
  readonly destino: DestinoOcorrencia;
  readonly responsavel: string;
  readonly prazo?: string;
}

/**
 * Ocorrência de chegada (SUBST-14): produto diferente do documento. Não é estoque e não gera movimento; retido para
 * decisão fica aberto, com responsável e prazo; devolvido na entrega fica só registrado.
 */
export function ocorrenciaDeChegada(o: OcorrenciaDeChegada): OcorrenciaDeChegada & {
  readonly status: 'aberta' | 'registrada';
} {
  const bruto: unknown = o;
  if (typeof bruto !== 'object' || bruto === null) invalido('A ocorrência precisa ser um objeto.');
  const real = o.produtoReal as Partial<Record<string, unknown>> | null;
  const temId =
    typeof real === 'object' &&
    real !== null &&
    typeof real['produtoId'] === 'string' &&
    UUID.test(real['produtoId']);
  const temDescricao =
    typeof real === 'object' &&
    real !== null &&
    typeof real['descricao'] === 'string' &&
    real['descricao'].trim() !== '';
  if (!temId && !temDescricao) invalido('A ocorrência identifica o produto real: cadastro ou descrição.');
  if (!decimal(o.quantidade).greaterThan(0)) invalido('A quantidade contada deve ser maior que zero.');
  if (typeof o.unidade !== 'string' || o.unidade.trim() === '' || o.unidade.length > 40) {
    invalido('Informe a unidade como foi contada (até 40 caracteres).');
  }
  if (typeof o.responsavel !== 'string' || o.responsavel.trim() === '')
    invalido('A ocorrência precisa de responsável.');
  const destino: unknown = o.destino;
  if (destino === 'retido_para_decisao') {
    dataCivil(o.prazo);
    return { ...o, status: 'aberta' };
  }
  if (destino !== 'devolvido_na_entrega') invalido('Destino: retido para decisão ou devolvido na entrega.');
  if (o.prazo !== undefined) dataCivil(o.prazo);
  return { ...o, status: 'registrada' };
}

export type ProximaAcao = 'Ver inspeção pendente' | 'Ver divergência' | 'Receber documento';

/**
 * Próxima ação do documento, só com ações que existem no incremento 1: inspeção pendente primeiro, depois divergência ou
 * ocorrência aberta; sem pendência, receber o próximo documento. Liberar entra no incremento 2.
 */
export function proximaAcao(resumo: {
  readonly inspecaoPendente: boolean;
  readonly divergente: boolean;
  readonly ocorrenciaAberta: boolean;
}): ProximaAcao {
  if (resumo.inspecaoPendente) return 'Ver inspeção pendente';
  if (resumo.divergente || resumo.ocorrenciaAberta) return 'Ver divergência';
  return 'Receber documento';
}
