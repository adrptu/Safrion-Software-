import type { Decimal } from 'decimal.js';

import { Dec, decimal, ehDecimalDoDominio } from './decimal.js';
import { ErroDominio } from './erros.js';

/** Toda quantidade tem unidade e base (RN-033). A unidade-base de cada dimensão é a do saldo. */
export type Dimensao = 'volume' | 'massa' | 'contagem';
export type CodigoUnidade = 'mL' | 'L' | 'm3' | 'g' | 'kg' | 't' | 'sc60' | 'un';

interface DefinicaoUnidade {
  readonly dimensao: Dimensao;
  /** Quanto 1 desta unidade vale na unidade-base da dimensão. */
  readonly fatorParaBase: string;
}

export const UNIDADES: Readonly<Record<CodigoUnidade, DefinicaoUnidade>> = {
  mL: { dimensao: 'volume', fatorParaBase: '0.001' },
  L: { dimensao: 'volume', fatorParaBase: '1' },
  m3: { dimensao: 'volume', fatorParaBase: '1000' },
  g: { dimensao: 'massa', fatorParaBase: '0.001' },
  kg: { dimensao: 'massa', fatorParaBase: '1' },
  t: { dimensao: 'massa', fatorParaBase: '1000' },
  sc60: { dimensao: 'massa', fatorParaBase: '60' },
  un: { dimensao: 'contagem', fatorParaBase: '1' },
};

export const UNIDADE_BASE: Readonly<Record<Dimensao, CodigoUnidade>> = {
  volume: 'L',
  massa: 'kg',
  contagem: 'un',
};

export interface Quantidade {
  readonly valor: Decimal;
  readonly unidade: CodigoUnidade;
}

export function ehUnidade(codigo: unknown): codigo is CodigoUnidade {
  return typeof codigo === 'string' && Object.hasOwn(UNIDADES, codigo);
}

function unidadeValida(codigo: unknown): CodigoUnidade {
  if (!ehUnidade(codigo)) {
    throw new ErroDominio('UNIDADE_DESCONHECIDA', `Unidade "${String(codigo)}" não está cadastrada.`);
  }
  return codigo;
}

export function ehUnidadeBase(codigo: CodigoUnidade): boolean {
  return UNIDADE_BASE[UNIDADES[codigo].dimensao] === codigo;
}

/** Cria uma quantidade a partir de texto decimal e do código da unidade; não existe unidade implícita. */
export function quantidade(valor: unknown, unidade: unknown): Quantidade {
  return { valor: decimal(valor), unidade: unidadeValida(unidade) };
}

/** Confere em tempo de execução uma quantidade que chegou de fora (JSON, fila offline): ENG-014. */
export function quantidadeValida(q: unknown): Quantidade {
  const x = q as Partial<Quantidade> | null;
  if (typeof x !== 'object' || x === null || !ehDecimalDoDominio(x.valor)) {
    throw new ErroDominio(
      'DECIMAL_INVALIDO',
      'A quantidade precisa de um valor criado pela política decimal do domínio.',
    );
  }
  return { valor: x.valor, unidade: unidadeValida(x.unidade) };
}

/** Converte entre unidades da mesma dimensão; massa em volume exige densidade e é recusada. */
export function converter(q: Quantidade, destino: CodigoUnidade): Quantidade {
  const origem = quantidadeValida(q);
  const de = UNIDADES[origem.unidade];
  const para = UNIDADES[unidadeValida(destino)];
  if (de.dimensao !== para.dimensao) {
    throw new ErroDominio(
      'UNIDADE_INCOMPATIVEL',
      `Não dá para converter ${origem.unidade} (${de.dimensao}) em ${destino} (${para.dimensao}).`,
    );
  }
  return { valor: origem.valor.times(de.fatorParaBase).div(para.fatorParaBase), unidade: destino };
}

export function paraBase(q: Quantidade): Quantidade {
  const origem = quantidadeValida(q);
  return converter(origem, UNIDADE_BASE[UNIDADES[origem.unidade].dimensao]);
}

/** Conversão de embalagem versionada (CD-06, FO-25): por exemplo, 1 galão de 5 L = 5 L, versão 1. */
export interface ConversaoEmbalagem {
  readonly embalagem: string;
  readonly unidadeBase: CodigoUnidade;
  readonly fator: Decimal;
  readonly versao: number;
}

/** Origem de uma quantidade contada em embalagens: o movimento guarda a unidade original e a versão (PRD 11). */
export interface OrigemEmbalagem {
  readonly embalagem: string;
  readonly contagem: string;
  readonly versaoConversao: number;
}

export function conversaoEmbalagem(
  embalagem: unknown,
  fator: unknown,
  unidadeBase: unknown,
  versao: unknown,
): ConversaoEmbalagem {
  const f = decimal(fator);
  const base = unidadeValida(unidadeBase);
  if (
    typeof embalagem !== 'string' ||
    embalagem.trim() === '' ||
    !f.greaterThan(0) ||
    typeof versao !== 'number' ||
    !Number.isInteger(versao) ||
    versao < 1
  ) {
    throw new ErroDominio(
      'CONVERSAO_INVALIDA',
      'A embalagem precisa de nome, fator maior que zero e versão inteira a partir de 1.',
    );
  }
  if (!ehUnidadeBase(base)) {
    throw new ErroDominio(
      'CONVERSAO_INVALIDA',
      `A conversão de embalagem aponta para a unidade-base, não para ${base}.`,
    );
  }
  return { embalagem, unidadeBase: base, fator: f, versao };
}

/** Confere uma conversão que chegou de fora refazendo-a pelas mesmas regras de conversaoEmbalagem (ENG-014). */
function conversaoValida(c: unknown): ConversaoEmbalagem {
  const x = c as Partial<Record<keyof ConversaoEmbalagem, unknown>> | null;
  if (typeof x !== 'object' || x === null || !ehDecimalDoDominio(x.fator)) {
    throw new ErroDominio(
      'CONVERSAO_INVALIDA',
      'A conversão de embalagem precisa ser criada por conversaoEmbalagem.',
    );
  }
  return conversaoEmbalagem(x.embalagem, x.fator.toFixed(), x.unidadeBase, x.versao);
}

/** Embalagens são itens indivisíveis (PRD 10.0): a contagem é inteira e maior que zero. */
export function embalagensParaBase(
  contagem: unknown,
  conv: ConversaoEmbalagem,
): { readonly quantidade: Quantidade; readonly origem: OrigemEmbalagem } {
  const conversao = conversaoValida(conv);
  const n = decimal(contagem);
  if (!n.isInteger() || !n.greaterThan(0)) {
    throw new ErroDominio(
      'QUANTIDADE_INVALIDA',
      `A contagem de ${conversao.embalagem} deve ser inteira e maior que zero.`,
    );
  }
  return {
    quantidade: { valor: new Dec(n).times(conversao.fator), unidade: conversao.unidadeBase },
    origem: { embalagem: conversao.embalagem, contagem: n.toFixed(0), versaoConversao: conversao.versao },
  };
}

/** Sentido inverso: quantas embalagens inteiras cabem na quantidade e quanto sobra na unidade-base. */
export function baseParaEmbalagens(
  q: Quantidade,
  conv: ConversaoEmbalagem,
): { readonly contagem: Decimal; readonly resto: Quantidade } {
  const conversao = conversaoValida(conv);
  const base = converter(q, conversao.unidadeBase);
  if (base.valor.isNegative()) {
    throw new ErroDominio(
      'QUANTIDADE_INVALIDA',
      'A quantidade para contar embalagens não pode ser negativa.',
    );
  }
  const contagem = base.valor.div(conversao.fator).floor();
  return {
    contagem,
    resto: { valor: base.valor.minus(contagem.times(conversao.fator)), unidade: conversao.unidadeBase },
  };
}
