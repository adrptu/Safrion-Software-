import { describe, expect, it } from 'vitest';

import { EsquemaDadosRecebimento, canonizarRecebimento } from '../src/index.js';

// Contrato do comando estoque.receber-documento (CMD-15; contrato CMD-15 v3.3, §3 e §6).
const U = (n: number) => `00000000-0000-4000-8000-${String(n).padStart(12, '0')}`;
const linha = (numero: number, extra: Record<string, unknown> = {}) => ({
  numero,
  produto: U(1),
  lote: { codigo: 'F26-01' },
  validade: '2027-06-30',
  local: U(2),
  unidade: { tipo: 'medida', unidade: 'L' },
  documento: '10.0',
  parcelas: { apto: '10.00', quarentena: '0', bloqueado: '0', recusado: '0.0' },
  ...extra,
});
const dados = (extra: Record<string, unknown> = {}) => ({
  emitente: U(3),
  tipo: 'nfe',
  serie: ' 001 ',
  numero: '000123',
  emissao: '2026-09-29',
  recebimento: '2026-09-30',
  fazenda: U(4),
  linhas: [linha(2), linha(1)],
  ...extra,
});

describe('valor unitário (contrato CMD-15 v3.8, §6.2)', () => {
  const problemas = (valorUnitario: string) => {
    const r = EsquemaDadosRecebimento.safeParse(dados({ linhas: [linha(1, { valorUnitario })] }));
    return r.success ? [] : r.error.issues.map((i) => [i.path.join('.'), i.message]);
  };

  it('até 8 casas na forma canônica passa; 9 casas e negativo são recusa de contrato com o campo', () => {
    expect(problemas('152.12345678')).toEqual([]);
    expect(problemas('0')).toEqual([]);
    // Zeros à direita não contam: vai ao banco como 152.12345678.
    expect(problemas('152.123456780')).toEqual([]);
    const canonico = canonizarRecebimento(
      EsquemaDadosRecebimento.parse(dados({ linhas: [linha(1, { valorUnitario: '152.123456780' })] })),
    );
    expect(canonico.linhas[0]?.valorUnitario).toBe('152.12345678');
    expect(problemas('152.123456789')).toEqual([
      ['linhas.0.valorUnitario', 'VALOR_UNITARIO_ACIMA_DE_8_CASAS'],
    ]);
    expect(problemas('-1')).toEqual([['linhas.0.valorUnitario', 'VALOR_UNITARIO_NEGATIVO']]);
    expect(problemas('1,5')).toEqual([['linhas.0.valorUnitario', 'DECIMAL_INVALIDO']]);
  });
});

describe('dados do recebimento', () => {
  it('aceita o documento completo e recusa campo a mais, número JSON e data inválida', () => {
    expect(EsquemaDadosRecebimento.safeParse(dados()).success).toBe(true);
    expect(EsquemaDadosRecebimento.safeParse(dados({ organizationId: U(9) })).success).toBe(false);
    expect(EsquemaDadosRecebimento.safeParse(dados({ linhas: [linha(1, { documento: 10 })] })).success).toBe(
      false,
    );
    expect(EsquemaDadosRecebimento.safeParse(dados({ emissao: '2026-02-30' })).success).toBe(false);
    expect(EsquemaDadosRecebimento.safeParse(dados({ linhas: [] })).success).toBe(false);
    expect(EsquemaDadosRecebimento.safeParse(dados({ linhas: [linha(51)] })).success).toBe(false);
  });

  it('"não se aplica" é null explícito; texto vazio não vira ausência', () => {
    expect(EsquemaDadosRecebimento.safeParse(dados({ linhas: [linha(1, { validade: null })] })).success).toBe(
      true,
    );
    expect(EsquemaDadosRecebimento.safeParse(dados({ linhas: [linha(1, { validade: '' })] })).success).toBe(
      false,
    );
  });

  it('forma canônica: "10.0" e "10" são o mesmo conteúdo, série e número normalizados, linhas em ordem', () => {
    const a = canonizarRecebimento(EsquemaDadosRecebimento.parse(dados()));
    const b = canonizarRecebimento(
      EsquemaDadosRecebimento.parse(
        dados({
          serie: '1',
          numero: '123',
          linhas: [
            linha(1, {
              documento: '10',
              parcelas: { apto: '10', quarentena: '0', bloqueado: '0', recusado: '0' },
            }),
            linha(2, {
              documento: '10',
              parcelas: { apto: '10', quarentena: '0', bloqueado: '0', recusado: '0' },
            }),
          ],
        }),
      ),
    );
    expect(a).toEqual(b);
    expect(a.linhas.map((l) => l.numero)).toEqual([1, 2]);
    expect([a.serie, a.numero]).toEqual(['1', '123']);
    // Outra unidade continua outro conteúdo.
    const mL = canonizarRecebimento(
      EsquemaDadosRecebimento.parse(
        dados({ linhas: [linha(1, { unidade: { tipo: 'medida', unidade: 'mL' } })] }),
      ),
    );
    expect(mL.linhas[0]?.unidade).toEqual({ tipo: 'medida', unidade: 'mL' });
  });
});
