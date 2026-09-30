import type { Decimal } from 'decimal.js';

import { Dec, ESCALA, POLITICA_PRECISAO, decimal } from './decimal.js';
import { ErroDominio } from './erros.js';
import {
  UNIDADES,
  converter,
  ehUnidade,
  ehUnidadeBase,
  quantidadeValida,
  type CodigoUnidade,
  type OrigemEmbalagem,
  type Quantidade,
} from './unidades.js';

/**
 * Saldo de um lote calculado só a partir de movimentos imutáveis (ENG-026, RF-SUP-003): não existe saldo editável.
 *
 * Restrições independentes (RN-015; glossário 21.1): cada unidade física tem uma situação em duas dimensões —
 * inspeção (quarentena ou liberado) e bloqueio (livre ou bloqueado). O vencimento vale para o lote inteiro.
 * Utilizável = liberado, livre e dentro da validade: o físico menos a UNIÃO das restrições, sem descontar duas vezes a
 * mesma unidade. Levantar um bloqueio não libera uma quarentena, e vice-versa.
 */
export type Inspecao = 'quarentena' | 'liberado';
export type Bloqueio = 'livre' | 'bloqueado';
export type Situacao = `${Inspecao}_${Bloqueio}`;
export const SITUACOES: readonly Situacao[] = [
  'quarentena_livre',
  'quarentena_bloqueado',
  'liberado_livre',
  'liberado_bloqueado',
];

/** Data civil no formato AAAA-MM-DD, sem fuso (PRD 10.0: datas civis não mudam de dia por conversão). */
export type DataCivil = string;

export interface Lote {
  readonly codigo: string;
  /** Data civil de validade, ou null quando a validade não se aplica ao produto (combustível, por exemplo; RN-032). */
  readonly validade: DataCivil | null;
  readonly unidadeBase: CodigoUnidade;
}

export type Movimento =
  | {
      readonly id: string;
      readonly tipo: 'entrada';
      readonly quantidade: Quantidade;
      readonly situacao: Situacao;
      readonly origem?: OrigemEmbalagem;
    }
  | {
      readonly id: string;
      readonly tipo: 'mudanca';
      readonly quantidade: Quantidade;
      readonly de: Situacao;
      readonly para: Situacao;
    }
  | { readonly id: string; readonly tipo: 'estorno'; readonly estornaId: string };

type PorSituacao = Readonly<Record<Situacao, Decimal>>;

export interface RegistroMovimento {
  readonly efeito: PorSituacao;
  readonly estorno: boolean;
  /** Conteúdo canônico: reenvio idêntico não tem efeito; mesmo id com outro conteúdo é conflito. */
  readonly assinatura: string;
  readonly origem?: OrigemEmbalagem;
}

export interface EstadoLote {
  readonly lote: Lote;
  readonly porSituacao: PorSituacao;
  readonly registros: ReadonlyMap<string, RegistroMovimento>;
  readonly estornados: ReadonlySet<string>;
}

/** Saldo sem sobreposição (SU-03): físico = utilizável + quarentena + bloqueado + vencido. */
export interface SaldoLote {
  readonly fisico: Decimal;
  readonly utilizavel: Decimal;
  /** Em quarentena e não bloqueado. */
  readonly quarentena: Decimal;
  /** Todo o bloqueado, com ou sem quarentena. */
  readonly bloqueado: Decimal;
  /** Liberado e livre, mas com o lote vencido. */
  readonly vencido: Decimal;
  /** Físico fora do utilizável: a união das restrições. */
  readonly restrito: Decimal;
  readonly loteVencido: boolean;
  readonly porSituacao: PorSituacao;
  readonly politica: typeof POLITICA_PRECISAO.id;
}

/** Limite de grandeza por movimento na unidade-base: mantém exatas as somas dentro de 34 algarismos. */
const LIMITE = new Dec('1e15');
const DATA = /^(\d{4})-(\d{2})-(\d{2})$/;

export function dataCivil(texto: unknown): DataCivil {
  const t = typeof texto === 'string' ? texto : '';
  const m = DATA.exec(t);
  const [ano, mes, dia] = m ? [Number(m[1]), Number(m[2]), Number(m[3])] : [0, 0, 0];
  const d = new Date(Date.UTC(ano, mes - 1, dia));
  if (!m || d.getUTCFullYear() !== ano || d.getUTCMonth() !== mes - 1 || d.getUTCDate() !== dia) {
    throw new ErroDominio('DATA_INVALIDA', `"${String(texto)}" não é uma data válida no formato AAAA-MM-DD.`);
  }
  return t;
}

/** validade null = "não se aplica" (explícito); texto vazio ou fora do formato continua sendo DATA_INVALIDA. */
export function lote(codigo: string, validade: string | null, unidadeBase: CodigoUnidade): Lote {
  if (typeof codigo !== 'string' || codigo.trim() === '') {
    throw new ErroDominio('LOTE_INVALIDO', 'O lote precisa de código.');
  }
  if (!ehUnidade(unidadeBase) || !ehUnidadeBase(unidadeBase)) {
    throw new ErroDominio(
      'UNIDADE_INCOMPATIVEL',
      `O saldo do lote é guardado na unidade-base, não em ${unidadeBase}.`,
    );
  }
  return { codigo, validade: validade === null ? null : dataCivil(validade), unidadeBase };
}

const zeros = (): Record<Situacao, Decimal> => ({
  quarentena_livre: new Dec(0),
  quarentena_bloqueado: new Dec(0),
  liberado_livre: new Dec(0),
  liberado_bloqueado: new Dec(0),
});

export function estadoInicial(l: Lote): EstadoLote {
  return { lote: l, porSituacao: zeros(), registros: new Map(), estornados: new Set() };
}

function ehSituacao(s: unknown): s is Situacao {
  return typeof s === 'string' && (SITUACOES as readonly string[]).includes(s);
}

function situacao(s: unknown): Situacao {
  if (!ehSituacao(s)) throw new ErroDominio('MOVIMENTO_INVALIDO', `Situação "${String(s)}" não existe.`);
  return s;
}

function naBase(l: Lote, q: unknown): Decimal {
  const v = converter(quantidadeValida(q), l.unidadeBase).valor;
  if (!v.greaterThan(0) || v.greaterThanOrEqualTo(LIMITE)) {
    throw new ErroDominio(
      'QUANTIDADE_INVALIDA',
      'A quantidade do movimento deve ser maior que zero e realista.',
    );
  }
  if (UNIDADES[l.unidadeBase].dimensao === 'contagem' && !v.isInteger()) {
    throw new ErroDominio(
      'QUANTIDADE_FORA_DA_ESCALA',
      `O lote é contado em ${l.unidadeBase}, item indivisível: a quantidade deve ser inteira, sem arredondar (PRD 10.0).`,
    );
  }
  if (v.decimalPlaces() > ESCALA.quantidade) {
    throw new ErroDominio(
      'QUANTIDADE_FORA_DA_ESCALA',
      `A quantidade em ${l.unidadeBase} passa de ${String(ESCALA.quantidade)} casas decimais; arredonde antes, por regra explícita (PRD 10.0).`,
    );
  }
  return v;
}

/** Origem da embalagem conferida e reescrita por campos explícitos, com a contagem em texto canônico. */
function origemCanonica(o: unknown): OrigemEmbalagem {
  const x = o as Partial<Record<keyof OrigemEmbalagem, unknown>> | null;
  if (
    typeof x !== 'object' ||
    x === null ||
    typeof x.embalagem !== 'string' ||
    x.embalagem.trim() === '' ||
    typeof x.versaoConversao !== 'number' ||
    !Number.isInteger(x.versaoConversao) ||
    x.versaoConversao < 1
  ) {
    throw new ErroDominio(
      'MOVIMENTO_INVALIDO',
      'A origem da embalagem precisa de nome, contagem inteira e versão da conversão a partir de 1.',
    );
  }
  const contagem = decimal(x.contagem);
  if (!contagem.isInteger() || !contagem.greaterThan(0)) {
    throw new ErroDominio(
      'MOVIMENTO_INVALIDO',
      'A contagem de embalagens da origem deve ser inteira e maior que zero.',
    );
  }
  return { embalagem: x.embalagem, contagem: contagem.toFixed(0), versaoConversao: x.versaoConversao };
}

/**
 * Conteúdo canônico por campos explícitos, em ordem fixa: a ordem das propriedades do objeto recebido não muda a
 * assinatura. Decimais iguais na mesma unidade ("1" e "1.0") coincidem; outra unidade é outro conteúdo (IDEM-13).
 */
function assinaturaDe(m: Movimento, origem: OrigemEmbalagem | undefined): string {
  const q = (x: Quantidade) => [x.valor.toString(), x.unidade];
  switch (m.tipo) {
    case 'entrada':
      return JSON.stringify([
        m.tipo,
        q(m.quantidade),
        m.situacao,
        origem ? [origem.embalagem, origem.contagem, origem.versaoConversao] : null,
      ]);
    case 'mudanca':
      return JSON.stringify([m.tipo, q(m.quantidade), m.de, m.para]);
    case 'estorno':
      return JSON.stringify([m.tipo, m.estornaId]);
  }
}

interface Acumulador {
  readonly lote: Lote;
  porSituacao: Record<Situacao, Decimal>;
  readonly registros: Map<string, RegistroMovimento>;
  readonly estornados: Set<string>;
}

/**
 * Ordem da validação: forma do movimento (sem estado) → reenvio (mesmo id) → regras que dependem do estado. Assim um
 * reenvio idêntico nunca é recusado por uma regra que ele mesmo já cumpriu. O acumulador só muda no fim.
 */
function aplicarEm(acc: Acumulador, m: Movimento): void {
  const bruto: unknown = m;
  if (typeof bruto !== 'object' || bruto === null) {
    throw new ErroDominio(
      'MOVIMENTO_INVALIDO',
      'O movimento precisa ser um objeto com identificador e tipo.',
    );
  }
  const mov = bruto as Partial<Record<string, unknown>>;
  if (typeof mov.id !== 'string' || mov.id.trim() === '') {
    throw new ErroDominio('MOVIMENTO_INVALIDO', 'O movimento precisa de identificador.');
  }
  const efeito = zeros();
  let origem: OrigemEmbalagem | undefined;
  switch (m.tipo) {
    case 'entrada':
      efeito[situacao(m.situacao)] = naBase(acc.lote, m.quantidade);
      origem = m.origem === undefined ? undefined : origemCanonica(m.origem);
      break;
    case 'mudanca': {
      const [de, para] = [situacao(m.de), situacao(m.para)];
      const [ide, bde] = de.split('_');
      const [ipara, bpara] = para.split('_');
      if ((ide === ipara) === (bde === bpara)) {
        throw new ErroDominio(
          'MOVIMENTO_INVALIDO',
          'A mudança altera exatamente uma dimensão: a inspeção ou o bloqueio, não as duas nem nenhuma.',
        );
      }
      const v = naBase(acc.lote, m.quantidade);
      efeito[de] = v.negated();
      efeito[para] = v;
      break;
    }
    case 'estorno':
      if (typeof m.estornaId !== 'string' || m.estornaId.trim() === '') {
        throw new ErroDominio(
          'MOVIMENTO_INVALIDO',
          'O estorno precisa do identificador do movimento estornado.',
        );
      }
      break;
    default:
      throw new ErroDominio('MOVIMENTO_INVALIDO', `Tipo de movimento "${String(mov.tipo)}" não existe.`);
  }
  const assinatura = assinaturaDe(m, origem);
  const anterior = acc.registros.get(m.id);
  if (anterior) {
    if (anterior.assinatura === assinatura) return; // reenvio idêntico: sem efeito novo (idempotente)
    throw new ErroDominio('MOVIMENTO_CONFLITANTE', `O movimento ${m.id} já existe com outro conteúdo.`);
  }
  if (m.tipo === 'estorno') {
    const original = acc.registros.get(m.estornaId);
    if (!original || original.estorno || acc.estornados.has(m.estornaId)) {
      throw new ErroDominio(
        'ESTORNO_INVALIDO',
        `O movimento ${m.estornaId} não existe, já foi estornado ou é ele mesmo um estorno.`,
      );
    }
    for (const s of SITUACOES) efeito[s] = original.efeito[s].negated();
  }
  const novo = zeros();
  for (const s of SITUACOES) {
    novo[s] = acc.porSituacao[s].plus(efeito[s]);
    if (novo[s].isNegative()) {
      throw new ErroDominio(
        'SALDO_INSUFICIENTE',
        `O lote ${acc.lote.codigo} não tem quantidade suficiente em "${s}" para este movimento.`,
      );
    }
  }
  acc.porSituacao = novo;
  const estorno = m.tipo === 'estorno';
  acc.registros.set(m.id, origem ? { efeito, estorno, assinatura, origem } : { efeito, estorno, assinatura });
  if (m.tipo === 'estorno') acc.estornados.add(m.estornaId);
}

/** Aplica um movimento e devolve o novo estado; o estado recebido continua valendo e não muda. */
export function aplicar(estado: EstadoLote, m: Movimento): EstadoLote {
  const acc: Acumulador = {
    lote: estado.lote,
    porSituacao: { ...estado.porSituacao },
    registros: new Map(estado.registros),
    estornados: new Set(estado.estornados),
  };
  aplicarEm(acc, m);
  return acc;
}

/**
 * Saldo na data informada: o lote vence depois do dia da validade (o próprio dia ainda vale). Lote sem validade nunca
 * vence.
 */
export function saldo(estado: EstadoLote, hoje: DataCivil): SaldoLote {
  const p = estado.porSituacao;
  const dia = dataCivil(hoje);
  const loteVencido = estado.lote.validade !== null && dia > estado.lote.validade;
  const zero = new Dec(0);
  const utilizavel = loteVencido ? zero : p.liberado_livre;
  const vencido = loteVencido ? p.liberado_livre : zero;
  const quarentena = p.quarentena_livre;
  const bloqueado = p.quarentena_bloqueado.plus(p.liberado_bloqueado);
  const fisico = utilizavel.plus(quarentena).plus(bloqueado).plus(vencido);
  return {
    fisico,
    utilizavel,
    quarentena,
    bloqueado,
    vencido,
    restrito: fisico.minus(utilizavel),
    loteVencido,
    porSituacao: p,
    politica: POLITICA_PRECISAO.id,
  };
}

/** Um lote candidato ao consumo: validade (ou null), instante da primeira entrada (ISO 8601) e o saldo no dia. */
export interface CandidatoFefo {
  readonly chave: string;
  readonly validade: DataCivil | null;
  readonly primeiraEntrada: string;
  readonly saldo: SaldoLote;
}

/**
 * Ordem FEFO dos lotes com utilizável maior que zero; quarentena, bloqueio e vencido já estão fora do utilizável.
 * Primeiro os lotes com validade, do vencimento mais próximo; depois os sem validade, que não saem da fila: ficam
 * elegíveis pela primeira entrada. Empate pela chave: a ordem é a mesma em qualquer execução.
 */
export function ordemFefo(candidatos: readonly CandidatoFefo[]): string[] {
  const lista: unknown = candidatos;
  if (!Array.isArray(lista)) {
    throw new ErroDominio('MOVIMENTO_INVALIDO', 'Os lotes candidatos precisam vir numa lista.');
  }
  const itens = candidatos.map((c) => {
    const entrada = typeof c.primeiraEntrada === 'string' ? Date.parse(c.primeiraEntrada) : Number.NaN;
    if (typeof c.chave !== 'string' || c.chave === '' || Number.isNaN(entrada)) {
      throw new ErroDominio(
        'MOVIMENTO_INVALIDO',
        'Lote candidato sem chave ou sem instante da primeira entrada.',
      );
    }
    return { ...c, validade: c.validade === null ? null : dataCivil(c.validade), entrada };
  });
  return itens
    .filter((c) => c.saldo.utilizavel.greaterThan(0))
    .sort((x, y) => {
      if (x.validade !== y.validade) {
        if (x.validade === null) return 1;
        if (y.validade === null) return -1;
        return x.validade < y.validade ? -1 : 1;
      }
      if (x.entrada !== y.entrada) return x.entrada - y.entrada;
      return x.chave < y.chave ? -1 : x.chave > y.chave ? 1 : 0;
    })
    .map((c) => c.chave);
}

/** Reconstrói o saldo a partir do histórico com um único acumulador: tempo linear no número de movimentos. */
export function calcularSaldo(l: Lote, movimentos: readonly Movimento[], hoje: DataCivil): SaldoLote {
  const lista: unknown = movimentos;
  if (!Array.isArray(lista)) {
    throw new ErroDominio('MOVIMENTO_INVALIDO', 'O histórico de movimentos precisa ser uma lista.');
  }
  const acc: Acumulador = { lote: l, porSituacao: zeros(), registros: new Map(), estornados: new Set() };
  for (const m of movimentos) aplicarEm(acc, m);
  return saldo(acc, hoje);
}
