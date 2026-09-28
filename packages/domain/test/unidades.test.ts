import { Decimal } from 'decimal.js';
import { describe, expect, it } from 'vitest';

import {
  ErroDominio,
  baseParaEmbalagens,
  conversaoEmbalagem,
  converter,
  embalagensParaBase,
  paraBase,
  paraTexto,
  quantidade,
  type CodigoUnidade,
  type ConversaoEmbalagem,
  type Quantidade,
} from '../src/index.js';

const codigo = (f: () => unknown) => {
  try {
    f();
  } catch (e) {
    return e instanceof ErroDominio ? e.codigo : 'OUTRO';
  }
  return 'SEM_ERRO';
};

describe('unidades (RN-033, CD-06)', () => {
  it('forma inválida de conversão e embalagem vira erro de domínio, não TypeError (F0A-C03)', () => {
    expect(codigo(() => conversaoEmbalagem(null, '5', 'L', 1))).toBe('CONVERSAO_INVALIDA');
    expect(codigo(() => conversaoEmbalagem('galão', '5', 'L', '1'))).toBe('CONVERSAO_INVALIDA');
    const galao = conversaoEmbalagem('galão 5 L', '5', 'L', 1);
    for (const conv of [
      null,
      'galão',
      { ...galao, fator: 5 },
      { ...galao, versao: 0 },
      { ...galao, unidadeBase: 'mL' },
      { ...galao, embalagem: null },
    ]) {
      const c = conv as unknown as ConversaoEmbalagem;
      expect(codigo(() => embalagensParaBase('1', c))).toBe('CONVERSAO_INVALIDA');
      expect(codigo(() => baseParaEmbalagens(quantidade('1', 'L'), c))).toBe('CONVERSAO_INVALIDA');
    }
    expect(embalagensParaBase('2', { ...galao }).quantidade.valor.toString()).toBe('10');
  });

  it('converte dentro da mesma dimensão', () => {
    expect(paraTexto(converter(quantidade('2500', 'mL'), 'L').valor, 6)).toBe('2.500000');
    expect(paraTexto(paraBase(quantidade('3', 'sc60')).valor, 6)).toBe('180.000000');
    expect(paraTexto(converter(quantidade('1.5', 't'), 'sc60').valor, 6)).toBe('25.000000');
  });

  it('recusa converter massa em volume sem densidade', () => {
    expect(() => converter(quantidade('1', 'kg'), 'L')).toThrow(/Não dá para converter/);
  });

  it('recusa unidade não cadastrada', () => {
    expect(() => quantidade('1', 'galão')).toThrow(/não está cadastrada/);
  });

  it('galão de 5 L: 3 galões = 15 L, com a versão da conversão', () => {
    const galao = conversaoEmbalagem('galão 5 L', '5', 'L', 1);
    const r = embalagensParaBase('3', galao);
    expect(paraTexto(r.quantidade.valor, 6)).toBe('15.000000');
    expect(r.quantidade.unidade).toBe('L');
    expect(r.origem).toEqual({ embalagem: 'galão 5 L', contagem: '3', versaoConversao: 1 });
  });

  it('embalagem é indivisível: contagem fracionada ou zero é recusada', () => {
    const galao = conversaoEmbalagem('galão 5 L', '5', 'L', 1);
    expect(() => embalagensParaBase('1.5', galao)).toThrow(/inteira/);
    expect(() => embalagensParaBase('0', galao)).toThrow(/inteira/);
  });

  it('sentido inverso: 12 L em galões de 5 L = 2 galões e sobra de 2 L (achado 8)', () => {
    const galao = conversaoEmbalagem('galão 5 L', '5', 'L', 1);
    const r = baseParaEmbalagens(quantidade('12', 'L'), galao);
    expect(r.contagem.toString()).toBe('2');
    expect(paraTexto(r.resto.valor, 6)).toBe('2.000000');
    expect(baseParaEmbalagens(quantidade('10000', 'mL'), galao).contagem.toString()).toBe('2');
    expect(() => baseParaEmbalagens(quantidade('-1', 'L'), galao)).toThrow(/negativa/);
  });

  it('valida em tempo de execução unidade e decimal que chegam de fora (achado 2 e 9)', () => {
    expect(() => converter(quantidade('1', 'L'), 'galão' as CodigoUnidade)).toThrow(/não está cadastrada/);
    const estrangeira = { valor: new Decimal('1'), unidade: 'L' } as Quantidade;
    expect(() => converter(estrangeira, 'mL')).toThrow(/política decimal/);
    expect(() =>
      paraBase({ valor: quantidade('1', 'L').valor, unidade: 'litro' } as unknown as Quantidade),
    ).toThrow(/não está cadastrada/);
    expect(() => conversaoEmbalagem('galão', '5', 'galão', 1)).toThrow(/não está cadastrada/);
  });

  it('conversão precisa de fator positivo, versão e unidade-base', () => {
    expect(() => conversaoEmbalagem('galão 5 L', '0', 'L', 1)).toThrow(/fator maior que zero/);
    expect(() => conversaoEmbalagem('galão 5 L', '5', 'L', 0)).toThrow(/versão/);
    expect(() => conversaoEmbalagem(' ', '5', 'L', 1)).toThrow(/nome/);
    expect(() => conversaoEmbalagem('galão 5000 mL', '5000', 'mL', 1)).toThrow(/unidade-base/);
  });
});
