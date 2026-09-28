import { afterEach, describe, expect, it, vi } from 'vitest';

import {
  apagarRascunhos,
  armazemDaSessao,
  chaveDoRascunho,
  gravarRascunho,
  lerRascunho,
  type Rascunho,
} from '../src/estoque/rascunho';

/** Armazenamento em memória com a mesma interface do sessionStorage; `quebrado` imita navegador que recusa acesso. */
function memoria(quebrado = false) {
  const m = new Map<string, string>();
  const falhar = () => {
    if (quebrado) throw new Error('bloqueado');
  };
  return {
    m,
    get length() {
      return m.size;
    },
    key: (i: number) => [...m.keys()][i] ?? null,
    getItem: (k: string) => (falhar(), m.get(k) ?? null),
    setItem: (k: string, v: string) => {
      falhar();
      m.set(k, v);
    },
    removeItem: (k: string) => {
      falhar();
      m.delete(k);
    },
  };
}

const USUARIO = 'u1';
const ORG = 'o1';
const LOTE = 'l1';
const CHAVE = chaveDoRascunho(USUARIO, ORG, LOTE);
const campos = { quantidade: '7,5', unidade: 'L', situacao: 'liberado_livre', local: 'loc' };
const envio = { chave: '0b8c6a52-1f0e-4c7a-9d51-3f2d7e6b9a10', campos, versao: 3 };

describe('rascunho da entrada (B2-C02)', () => {
  it('a chave separa usuário, organização e lote', () => {
    expect(CHAVE).toBe('safrion:entrada:u1:o1:l1');
    expect(
      new Set([
        CHAVE,
        chaveDoRascunho('u2', ORG, LOTE),
        chaveDoRascunho(USUARIO, 'o2', LOTE),
        chaveDoRascunho(USUARIO, ORG, 'l2'),
      ]).size,
    ).toBe(4);
  });

  it('grava e lê o que foi digitado e o envio incerto', () => {
    const a = memoria();
    expect(gravarRascunho(a, CHAVE, { campos, incerto: null })).toBe(true);
    expect(lerRascunho(a, CHAVE)).toEqual({ campos, incerto: null });
    gravarRascunho(a, CHAVE, { campos, incerto: envio });
    expect(lerRascunho(a, CHAVE)).toEqual({ campos, incerto: envio });
    expect(lerRascunho(a, chaveDoRascunho('u2', ORG, LOTE))).toBeNull();
  });

  it('sem nada digitado e sem envio pendente, apaga', () => {
    const a = memoria();
    gravarRascunho(a, CHAVE, { campos, incerto: null });
    gravarRascunho(a, CHAVE, { campos: { ...campos, quantidade: '  ', situacao: '' }, incerto: null });
    expect(a.m.has(CHAVE)).toBe(false);
  });

  it('conteúdo corrompido ou de outro formato é ignorado', () => {
    const a = memoria();
    for (const bruto of [
      '{',
      'null',
      '"texto"',
      JSON.stringify({ campos: { ...campos, quantidade: 7 }, incerto: null }),
      JSON.stringify({ campos, incerto: { ...envio, chave: 'x' } }),
      JSON.stringify({ campos, incerto: { ...envio, versao: -1 } }),
      JSON.stringify({ campos, incerto: { ...envio, versao: 1.5 } }),
      JSON.stringify({ campos: { ...campos, local: 'x'.repeat(201) }, incerto: null }),
      JSON.stringify({ incerto: null }),
      JSON.stringify({ campos, incerto: 'x' }),
    ]) {
      a.m.set(CHAVE, bruto);
      expect(lerRascunho(a, CHAVE), bruto).toBeNull();
    }
    expect(lerRascunho(null, CHAVE)).toBeNull();
  });

  it('armazenamento bloqueado não derruba a tela', () => {
    const a = memoria(true);
    const r: Rascunho = { campos, incerto: null };
    expect(gravarRascunho(a, CHAVE, r)).toBe(false);
    expect(lerRascunho(a, CHAVE)).toBeNull();
    expect(() => {
      apagarRascunhos(a);
    }).not.toThrow();
    expect(gravarRascunho(null, CHAVE, r)).toBe(false);
    expect(() => {
      apagarRascunhos(null);
    }).not.toThrow();
  });

  it('sair apaga só os rascunhos do Safrion', () => {
    const a = memoria();
    gravarRascunho(a, CHAVE, { campos, incerto: envio });
    gravarRascunho(a, chaveDoRascunho('u2', ORG, LOTE), { campos, incerto: null });
    a.setItem('outro-site', 'x');
    apagarRascunhos(a);
    expect([...a.m.keys()]).toEqual(['outro-site']);
  });

  describe('armazemDaSessao', () => {
    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it('no servidor (sem window) não há armazenamento', () => {
      expect(armazemDaSessao()).toBeNull();
    });

    it('no navegador usa o sessionStorage; acesso bloqueado vira null', () => {
      const a = memoria();
      vi.stubGlobal('window', { sessionStorage: a });
      expect(armazemDaSessao()).toBe(a);
      vi.stubGlobal('window', {
        get sessionStorage(): Storage {
          throw new Error('SecurityError');
        },
      });
      expect(armazemDaSessao()).toBeNull();
    });
  });
});
