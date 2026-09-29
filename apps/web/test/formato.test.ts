import { describe, expect, it } from 'vitest';

import { dataCivil, dataDoCampo, formatarData, formatarInstante } from '../src/formato/data';
import {
  compararDecimais,
  decimalDoCampo,
  formatarDecimal,
  formatarQuantidade,
  leituraDoFiltro,
  positivo,
  somarDecimais,
} from '../src/formato/numero';

// Valores esperados escritos à mão (pt-BR: milhar com ponto, decimal com vírgula), sem usar as funções como oráculo.
describe('números em pt-BR', () => {
  it('formata o decimal canônico sem zeros à direita e com milhar', () => {
    expect(formatarDecimal('1234.500000')).toBe('1.234,5');
    expect(formatarDecimal('1000000')).toBe('1.000.000');
    expect(formatarDecimal('12.345678')).toBe('12,345678');
    expect(formatarDecimal('007.10')).toBe('7,1');
    expect(formatarDecimal('0.000000')).toBe('0');
    expect(formatarDecimal('-0.000000')).toBe('0');
    expect(formatarDecimal('-2.000000')).toBe('-2');
    expect(() => formatarDecimal('1e3')).toThrow();
    expect(() => formatarDecimal('abc')).toThrow();
  });

  it('quantidade sempre com unidade', () => {
    expect(formatarQuantidade('2.500000', 'L')).toBe('2,5 L');
    expect(formatarQuantidade('60', 'sc60')).toBe('60 sc 60 kg');
    expect(formatarQuantidade('1.5', 'm3')).toBe('1,5 m³');
    expect(formatarQuantidade('1', 'xx')).toBe('1 xx');
    expect(formatarQuantidade('1', '__proto__')).toBe('1 __proto__');
  });

  it('positivo lê o texto', () => {
    expect(positivo('0.000001')).toBe(true);
    expect(positivo('0.000000')).toBe(false);
    expect(positivo('-1')).toBe(false);
    expect(positivo('')).toBe(false);
    expect(positivo('abc')).toBe(false);
  });

  it('campo de quantidade: vírgula decimal, ponto só como milhar, nada adivinhado', () => {
    expect(decimalDoCampo('12,5')).toEqual({ ok: true, valor: '12.5' });
    expect(decimalDoCampo('1.234,5')).toEqual({ ok: true, valor: '1234.5' });
    expect(decimalDoCampo('1.234')).toEqual({ ok: true, valor: '1234' });
    expect(decimalDoCampo(' 1 234 ')).toEqual({ ok: true, valor: '1234' });
    const formato = { ok: false, erro: 'Use só números, com vírgula para decimais. Exemplo: 12,5' };
    expect(decimalDoCampo('1.5')).toEqual(formato);
    expect(decimalDoCampo('1.23')).toEqual(formato);
    expect(decimalDoCampo('12,')).toEqual(formato);
    expect(decimalDoCampo('-3')).toEqual(formato);
    expect(decimalDoCampo('')).toEqual({ ok: false, erro: 'Informe a quantidade.' });
    expect(decimalDoCampo('0,000')).toEqual({ ok: false, erro: 'Informe uma quantidade maior que zero.' });
  });

  it('limite de filtro aceita zero e recusa mais de seis casas', () => {
    expect(leituraDoFiltro('0')).toBe('0');
    expect(leituraDoFiltro('1.234,5')).toBe('1234.5');
    expect(leituraDoFiltro('1,1234567')).toBeNull();
    expect(leituraDoFiltro('x')).toBeNull();
  });

  it('soma e compara sem ponto flutuante', () => {
    expect(somarDecimais(['0.1', '0.2'])).toBe('0.300000');
    expect(somarDecimais(['12.500000', '2.500000'])).toBe('15.000000');
    expect(somarDecimais(['1', '-3.5'])).toBe('-2.500000');
    expect(somarDecimais([])).toBe('0.000000');
    expect(() => somarDecimais(['0.0000001'])).toThrow();
    expect(() => somarDecimais(['x'])).toThrow();
    expect(compararDecimais('10', '9.999999')).toBe(1);
    expect(compararDecimais('2.5', '2.500000')).toBe(0);
    expect(compararDecimais('-1', '0')).toBe(-1);
    expect(compararDecimais('1', '-1')).toBe(1);
  });
});

describe('datas', () => {
  it('data civil no fuso de Brasília: 02:30 UTC ainda é o dia anterior', () => {
    expect(dataCivil(new Date('2026-09-28T02:30:00Z'))).toBe('2026-09-27');
    expect(dataCivil(new Date('2026-09-28T03:00:00Z'))).toBe('2026-09-28');
    expect(dataCivil(new Date('2026-09-28T02:30:00Z'), 'UTC')).toBe('2026-09-28');
  });

  it('formata e lê datas sem passar por fuso', () => {
    expect(formatarData('2027-06-30')).toBe('30/06/2027');
    expect(() => formatarData('30/06/2027')).toThrow();
    expect(dataDoCampo('31/12/2026')).toBe('2026-12-31');
    expect(dataDoCampo(' 01/01/2027 ')).toBe('2027-01-01');
    expect(dataDoCampo('31/02/2026')).toBeNull();
    expect(dataDoCampo('2026-12-31')).toBeNull();
  });

  it('instante em dd/mm/aaaa hh:mm no horário de Brasília', () => {
    expect(formatarInstante('2026-09-28T14:05:00Z')).toBe('28/09/2026 11:05');
    expect(formatarInstante('2026-09-28T02:59:00Z')).toBe('27/09/2026 23:59');
  });
});
