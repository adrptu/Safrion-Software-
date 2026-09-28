import { createHash } from 'node:crypto';

import { describe, expect, it } from 'vitest';

import { VERSAO_CANONICA, canonizar, hashCanonico } from '../src/canonico.js';
import { ErroComando } from '../src/erros.js';

const codigo = (f: () => unknown) => {
  try {
    f();
  } catch (e) {
    return e instanceof ErroComando ? e.codigo : 'OUTRO';
  }
  return 'SEM_ERRO';
};

describe('conteúdo canônico da intenção (IDEM-13)', () => {
  it('a ordem dos campos e os campos indefinidos não mudam o texto nem o hash', () => {
    const a = { b: 1, a: { d: 'x', c: [1, 2] }, z: undefined };
    const b = { a: { c: [1, 2], d: 'x' }, b: 1 };
    expect(canonizar(a)).toBe('{"a":{"c":[1,2],"d":"x"},"b":1}');
    expect(hashCanonico(a)).toBe(hashCanonico(b));
    expect(VERSAO_CANONICA).toBe('CANON-1');
  });

  it('o hash é o SHA-256 do texto canônico', () => {
    expect(hashCanonico({ a: 1 })).toBe(createHash('sha256').update('{"a":1}').digest('hex'));
  });

  it('a ordem das listas conta; texto é normalizado em NFC, também nas chaves', () => {
    expect(hashCanonico([1, 2])).not.toBe(hashCanonico([2, 1]));
    expect(canonizar({ ['café']: 'á' })).toBe(canonizar({ ['café']: 'á' }));
  });

  it('aceita nulo, booleano e inteiro seguro; zero negativo vira zero', () => {
    expect(canonizar([null, true, false, -0, 42])).toBe('[null,true,false,0,42]');
  });

  it('recusa ponto flutuante, inteiro além do seguro e o que não é objeto simples', () => {
    for (const v of [
      10.5,
      Number.NaN,
      Number.MAX_SAFE_INTEGER + 1,
      new Date(0),
      new Map(),
      undefined,
      () => 1,
      1n,
    ]) {
      expect(codigo(() => canonizar(v))).toBe('CONTRATO_INVALIDO');
    }
    expect(canonizar(Object.create(null) as object)).toBe('{}');
  });
});
