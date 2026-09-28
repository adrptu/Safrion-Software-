import { describe, expect, it } from 'vitest';

import {
  COMANDOS,
  ehComando,
  LEITURAS,
  nomeDoPapel,
  PAPEIS,
  podeExecutar,
  podeLer,
} from '../src/autorizacao/matriz';

describe('matriz de autorização (ADR 0004 §4)', () => {
  it('cada papel × cada comando: só o almoxarife registra entrada', () => {
    const permitido = Object.fromEntries(PAPEIS.map((p) => [p, COMANDOS.filter((c) => podeExecutar(p, c))]));
    expect(permitido).toEqual({ almoxarife: ['estoque.registrar-entrada'], gerente: [] });
  });

  it('nega por padrão: papel desconhecido, comando fora da matriz e nome herdado de objeto', () => {
    for (const papel of ['motorista', '', '__proto__', 'constructor', 'toString']) {
      expect(podeExecutar(papel, 'estoque.registrar-entrada'), papel).toBe(false);
      expect(podeLer(papel, 'estoque'), papel).toBe(false);
    }
    expect(podeExecutar('almoxarife', 'estoque.apagar-tudo')).toBe(false);
    expect(ehComando('estoque.apagar-tudo')).toBe(false);
  });

  it('leituras: os dois papéis leem estoque e cadastros; recurso desconhecido é negado', () => {
    for (const papel of PAPEIS) {
      expect(
        LEITURAS.filter((l) => podeLer(papel, l)),
        papel,
      ).toEqual(['estoque', 'cadastros']);
      expect(podeLer(papel, 'financeiro'), papel).toBe(false);
    }
  });

  it('nome do papel para a tela; papel desconhecido aparece como veio', () => {
    expect(nomeDoPapel('almoxarife')).toBe('Almoxarife');
    expect(nomeDoPapel('gerente')).toBe('Gerente');
    expect(nomeDoPapel('motorista')).toBe('motorista');
    expect(nomeDoPapel('__proto__')).toBe('__proto__');
  });
});
