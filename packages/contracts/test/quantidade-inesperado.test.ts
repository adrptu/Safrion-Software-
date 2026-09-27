import { describe, expect, it, vi } from 'vitest';

vi.mock('@safrion/domain', async (original) => ({
  ...(await original<typeof import('@safrion/domain')>()),
  decimal: () => {
    throw new TypeError('falha inesperada no domínio');
  },
}));

const { EsquemaDecimalTexto } = await import('../src/quantidade.js');

describe('decimal: erro inesperado não vira recusa de contrato silenciosa (ENG-015)', () => {
  it('o erro sobe em vez de virar DECIMAL_INVALIDO', () => {
    expect(() => EsquemaDecimalTexto.parse('1')).toThrow(TypeError);
  });
});
