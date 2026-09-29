import fc from 'fast-check';
import { describe, expect, it } from 'vitest';

import { Decimal } from 'decimal.js';

import {
  decimal,
  ehDecimalDoDominio,
  ErroDominio,
  paraTexto,
  POLITICA_PRECISAO,
  quantizar,
} from '../src/index.js';

describe('decimal (PRD 10.0, ENG-013)', () => {
  it('casos de referência do PRD 10.0 com ROUND_HALF_UP', () => {
    expect(paraTexto(decimal('1.005'), 2)).toBe('1.01');
    expect(paraTexto(decimal('-1.005'), 2)).toBe('-1.01');
    expect(paraTexto(decimal('0.0000005'), 6)).toBe('0.000001');
  });

  it('não tem erro de ponto flutuante binário', () => {
    expect(paraTexto(decimal('0.1').plus(decimal('0.2')), 6)).toBe('0.300000');
  });

  it('guarda 34 algarismos significativos e só arredonda no marco final', () => {
    const terco = decimal('1').div(decimal('3'));
    expect(terco.toString()).toBe('0.' + '3'.repeat(34));
    expect(paraTexto(terco.times(3), 6)).toBe('1.000000');
  });

  it('zero não leva sinal no texto', () => {
    expect(paraTexto(decimal('-0.0000001'), 6)).toBe('0.000000');
  });

  it('recusa número JSON (ponto flutuante binário) com código estável', () => {
    expect(() => decimal(0.1)).toThrow(ErroDominio);
    try {
      decimal(12);
    } catch (e) {
      expect((e as ErroDominio).codigo).toBe('NUMERO_BINARIO_RECUSADO');
    }
  });

  it.each(['1e3', '1,5', ' 1', '01', '.5', '5.', '', '--1', 'NaN', 'Infinity'])('recusa "%s"', (t) => {
    expect(() => decimal(t)).toThrow(/formato canônico/);
  });

  it('recusa zero com sinal e mais de 34 algarismos significativos (revisão adversarial, achado 9)', () => {
    expect(() => decimal('-0')).toThrow(/zero com sinal/);
    expect(() => decimal('-0.000')).toThrow(/zero com sinal/);
    expect(decimal('0.' + '0'.repeat(10) + '9'.repeat(34)).toString()).toBe(
      '0.' + '0'.repeat(10) + '9'.repeat(34),
    );
    expect(() => decimal('9'.repeat(35))).toThrow(/34 algarismos/);
  });

  it('escala inválida em quantizar ou paraTexto tem código estável', () => {
    expect(() => paraTexto(decimal('1'), -1)).toThrow(ErroDominio);
    expect(() => quantizar(decimal('1'), 1.5)).toThrow(/Escala inválida/);
    expect(() => quantizar(decimal('1'), 35)).toThrow(/Escala inválida/);
  });

  it('distingue o decimal da política de outro construtor com outra precisão', () => {
    expect(ehDecimalDoDominio(decimal('1'))).toBe(true);
    expect(ehDecimalDoDominio(new Decimal('1'))).toBe(false);
    expect(POLITICA_PRECISAO).toEqual({ id: 'PREC-1', algarismos: 34, modo: 'ROUND_HALF_UP' });
  });

  it('propriedade: somar e subtrair o mesmo valor devolve o original, sem resíduo', () => {
    const texto = fc
      .tuple(fc.bigInt({ min: -(10n ** 12n), max: 10n ** 12n }), fc.integer({ min: 0, max: 6 }))
      .map(([n, casas]) => {
        const s = (n < 0n ? -n : n).toString().padStart(casas + 1, '0');
        const inteiro = s.slice(0, s.length - casas).replace(/^0+(?=\d)/, '');
        const frac = casas > 0 ? '.' + s.slice(s.length - casas) : '';
        return (n < 0n && n !== 0n ? '-' : '') + inteiro + frac;
      });
    fc.assert(
      fc.property(texto, texto, (a, b) => {
        expect(decimal(a).plus(decimal(b)).minus(decimal(b)).equals(decimal(a))).toBe(true);
      }),
    );
  });
});
