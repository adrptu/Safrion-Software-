import { describe, expect, it, vi } from 'vitest';

vi.mock('@safrion/domain', async (original) => ({
  ...(await original<typeof import('@safrion/domain')>()),
  dataCivil: () => {
    throw new TypeError('falha inesperada no domínio');
  },
}));

const { EsquemaDadosRecebimento } = await import('../src/recebimento.js');

describe('data civil do recebimento: erro inesperado não vira recusa de contrato silenciosa (ENG-015)', () => {
  it('o erro sobe em vez de virar DATA_INVALIDA', () => {
    expect(() => EsquemaDadosRecebimento.shape.emissao.parse('2026-09-29')).toThrow(TypeError);
  });
});
