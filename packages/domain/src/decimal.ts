import { Decimal } from 'decimal.js';

import { ErroDominio } from './erros.js';

/**
 * Política de precisão do domínio (PRD 10.0, ENG-013): 34 algarismos significativos nas contas intermediárias e
 * ROUND_HALF_UP só no marco final. Nenhum valor passa por ponto flutuante binário. O identificador vai junto dos
 * resultados, para que uma mudança de política seja rastreável.
 */
export const POLITICA_PRECISAO = {
  id: 'PREC-1',
  algarismos: 34,
  modo: 'ROUND_HALF_UP',
} as const;

export const Dec = Decimal.clone({
  precision: POLITICA_PRECISAO.algarismos,
  rounding: Decimal.ROUND_HALF_UP,
  toExpNeg: -60,
  toExpPos: 60,
});

/** Escalas internas de referência por grandeza (PRD 10.0). */
export const ESCALA = { quantidade: 6, area: 6, monetario: 8, taxa: 12 } as const;

const CANONICO = /^-?(0|[1-9]\d*)(\.\d+)?$/;

function algarismosSignificativos(texto: string): number {
  return texto.replace(/[-.]/g, '').replace(/^0+/, '').length;
}

/**
 * Lê um decimal em texto canônico ("1234.5"). Recusa número JSON (já chega como ponto flutuante binário), zero com
 * sinal e mais algarismos significativos do que a política guarda.
 */
export function decimal(valor: unknown): Decimal {
  if (typeof valor !== 'string') {
    throw new ErroDominio(
      'NUMERO_BINARIO_RECUSADO',
      'O valor deve vir como texto decimal (por exemplo, "12.5"), não como número.',
    );
  }
  if (!CANONICO.test(valor)) {
    throw new ErroDominio(
      'DECIMAL_INVALIDO',
      `"${valor}" não é um decimal no formato canônico (ex.: "1234.5").`,
    );
  }
  const d = new Dec(valor);
  if (valor.startsWith('-') && d.isZero()) {
    throw new ErroDominio('DECIMAL_INVALIDO', `"${valor}" é zero com sinal; use "0".`);
  }
  if (algarismosSignificativos(valor) > POLITICA_PRECISAO.algarismos) {
    throw new ErroDominio(
      'DECIMAL_INVALIDO',
      `"${valor}" tem mais de ${String(POLITICA_PRECISAO.algarismos)} algarismos significativos.`,
    );
  }
  return d;
}

/**
 * Verdadeiro só para decimais criados pela política do domínio (não por outro construtor com outra precisão). Os
 * clones do decimal.js compartilham o protótipo, então `instanceof` não distingue; cada instância guarda o próprio
 * construtor, que passa adiante para os resultados das contas.
 */
export function ehDecimalDoDominio(valor: unknown): valor is Decimal {
  return valor instanceof Dec && Object.hasOwn(valor, 'constructor') && valor.constructor === Dec;
}

function casasValidas(casas: number): number {
  if (!Number.isInteger(casas) || casas < 0 || casas > POLITICA_PRECISAO.algarismos) {
    throw new ErroDominio('DECIMAL_INVALIDO', `Escala inválida: ${String(casas)} casas.`);
  }
  return casas;
}

/** Quantiza na escala pedida com ROUND_HALF_UP (metade para longe do zero). Zero sai sem sinal. */
export function quantizar(valor: Decimal, casas: number): Decimal {
  const q = new Dec(valor).toDecimalPlaces(casasValidas(casas), Decimal.ROUND_HALF_UP);
  return q.isZero() ? new Dec(0) : q;
}

/** Texto canônico na escala pedida, igual em backend, protótipo e auditoria (PRD 10.0). */
export function paraTexto(valor: Decimal, casas: number): string {
  return quantizar(valor, casas).toFixed(casas);
}
