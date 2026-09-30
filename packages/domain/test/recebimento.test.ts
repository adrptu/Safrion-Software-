import fc from 'fast-check';
import { describe, expect, it } from 'vitest';

import {
  aplicar,
  codigoLoteInterno,
  conferirLinha,
  conversaoEmbalagem,
  ErroDominio,
  estadoInicial,
  identidadeDaOrigem,
  lote,
  movimentosDaLinha,
  numerarMovimentos,
  ocorrenciaDeChegada,
  paraTexto,
  proximaAcao,
  saldo,
  validadeNoRecebimento,
  type LinhaConferida,
  type Parcela,
} from '../src/index.js';

// Recebimento por documento e inspeção (SU-06, CMD-15, AC-14; contrato CMD-15 v3.1).
const HOJE = '2026-09-30';
const galao = conversaoEmbalagem('galão 5 L', '5', 'L', 1);
const codigo = (f: () => unknown) => {
  try {
    f();
  } catch (e) {
    return e instanceof ErroDominio ? e.codigo : 'OUTRO';
  }
  return 'SEM_ERRO';
};
const parcelas = (
  apto: string,
  quarentena = '0',
  bloqueado = '0',
  recusado = '0',
): Record<Parcela, string> => ({
  apto,
  quarentena,
  bloqueado,
  recusado,
});
const emL = (
  documento: string,
  p: Record<Parcela, string>,
  extra: Partial<LinhaConferida> = {},
): LinhaConferida => ({
  numero: 1,
  unidade: { tipo: 'medida', unidade: 'L' },
  documento,
  parcelas: p,
  ...extra,
});
const emGalao = (
  documento: string,
  p: Record<Parcela, string>,
  extra: Partial<LinhaConferida> = {},
): LinhaConferida => ({
  numero: 1,
  unidade: { tipo: 'embalagem', conversao: galao },
  documento,
  parcelas: p,
  ...extra,
});
const ids = () => {
  let n = 0;
  return () => `m${String(++n)}`;
};
const inspecao = { responsavel: 'almoxarife-a', prazo: '2026-10-03' };

describe('conferência da linha', () => {
  it('AC-14: 60 recebidos com 10 em quarentena → físico 60, utilizável 50, sem divergência e com inspeção pendente', () => {
    const linha = emL('60', parcelas('50', '10'), { inspecao });
    expect(conferirLinha(linha)).toMatchObject({ divergente: false, inspecaoPendente: true });
    let e = estadoInicial(lote('F26-02', '2027-06-30', 'L'));
    for (const m of movimentosDaLinha(linha, ids())) e = aplicar(e, m.movimento);
    const s = saldo(e, HOJE);
    expect([paraTexto(s.fisico, 6), paraTexto(s.utilizavel, 6), paraTexto(s.quarentena, 6)]).toEqual([
      '60.000000',
      '50.000000',
      '10.000000',
    ]);
  });

  it('quarentena exige responsável e prazo; sem quarentena, inspeção é recusada', () => {
    expect(codigo(() => conferirLinha(emL('60', parcelas('50', '10'))))).toBe('RECEBIMENTO_INVALIDO');
    expect(
      codigo(() => conferirLinha(emL('60', parcelas('50', '10'), { inspecao: { ...inspecao, prazo: 'x' } }))),
    ).toBe('DATA_INVALIDA');
    expect(codigo(() => conferirLinha(emL('60', parcelas('60'), { inspecao })))).toBe('RECEBIMENTO_INVALIDO');
  });

  it('3 galões de 5 L = 15 L; o movimento guarda a origem "3 galão 5 L", v1', () => {
    const [m] = movimentosDaLinha(emGalao('3', parcelas('3')), ids());
    expect(m?.movimento.situacao).toBe('liberado_livre');
    expect(m?.movimento.quantidade.valor.toString()).toBe('15');
    expect(m?.movimento.quantidade.unidade).toBe('L');
    expect(m?.movimento.origem).toEqual({ embalagem: 'galão 5 L', contagem: '3', versaoConversao: 1 });
  });

  it('NF-TESTE-002: 2 galões, 1 apto e 1 bloqueado por avaria → 2 movimentos no mesmo lote, divergência aberta', () => {
    const linha = emGalao('2', parcelas('1', '0', '1'), { motivo: 'avaria' });
    expect(conferirLinha(linha)).toMatchObject({ divergente: true, inspecaoPendente: false });
    const movs = movimentosDaLinha(linha, ids());
    expect(
      movs.map((m) => [m.parcela, m.movimento.situacao, m.movimento.quantidade.valor.toString()]),
    ).toEqual([
      ['apto', 'liberado_livre', '5'],
      ['bloqueado', 'liberado_bloqueado', '5'],
    ]);
    let e = estadoInicial(lote('F26-03', '2027-08-31', 'L'));
    for (const m of movs) e = aplicar(e, m.movimento);
    const s = saldo(e, HOJE);
    expect([paraTexto(s.fisico, 6), paraTexto(s.bloqueado, 6), paraTexto(s.utilizavel, 6)]).toEqual([
      '10.000000',
      '5.000000',
      '5.000000',
    ]);
  });

  it('recusado não entra no físico nem gera movimento; parcela zero também não', () => {
    const linha = emL('10', parcelas('8', '0', '0', '2'), { motivo: 'avaria' });
    const r = conferirLinha(linha);
    expect([r.conferido.toString(), r.fisico.toString(), r.divergente]).toEqual(['10', '8', true]);
    const movs = movimentosDaLinha(linha, ids());
    expect(movs.map((m) => m.parcela)).toEqual(['apto']);
  });

  it('divergência deriva do conferido: falta e sobra com o motivo coerente; motivo sem divergência é recusado', () => {
    expect(conferirLinha(emL('10', parcelas('7'), { motivo: 'falta' })).divergente).toBe(true);
    expect(conferirLinha(emL('10', parcelas('12'), { motivo: 'sobra' })).divergente).toBe(true);
    expect(codigo(() => conferirLinha(emL('10', parcelas('7'))))).toBe('RECEBIMENTO_INVALIDO');
    expect(codigo(() => conferirLinha(emL('10', parcelas('7'), { motivo: 'sobra' })))).toBe(
      'RECEBIMENTO_INVALIDO',
    );
    expect(codigo(() => conferirLinha(emL('10', parcelas('12'), { motivo: 'falta' })))).toBe(
      'RECEBIMENTO_INVALIDO',
    );
    expect(codigo(() => conferirLinha(emL('10', parcelas('10'), { motivo: 'avaria' })))).toBe(
      'RECEBIMENTO_INVALIDO',
    );
    expect(codigo(() => conferirLinha(emL('10', parcelas('7'), { motivo: 'outro' })))).toBe(
      'RECEBIMENTO_INVALIDO',
    );
    expect(
      conferirLinha(emL('10', parcelas('7'), { motivo: 'outro', motivoTexto: 'caixa aberta' })).divergente,
    ).toBe(true);
  });

  it('formas inválidas são erro de domínio, não TypeError', () => {
    expect(codigo(() => conferirLinha(emL('10', parcelas('-1', '0', '0', '11'), { motivo: 'avaria' })))).toBe(
      'RECEBIMENTO_INVALIDO',
    );
    expect(codigo(() => conferirLinha(emGalao('2', parcelas('1.5', '0.5'), { inspecao })))).toBe(
      'RECEBIMENTO_INVALIDO',
    );
    expect(codigo(() => conferirLinha(emL('0', parcelas('0'))))).toBe('RECEBIMENTO_INVALIDO');
    expect(codigo(() => conferirLinha(emL('10', parcelas(10 as unknown as string))))).toBe(
      'NUMERO_BINARIO_RECUSADO',
    );
    expect(codigo(() => conferirLinha({ ...emL('10', parcelas('10')), numero: 51 }))).toBe(
      'RECEBIMENTO_INVALIDO',
    );
    expect(
      codigo(() =>
        conferirLinha({ ...emL('10', parcelas('10')), unidade: { tipo: 'medida', unidade: 'balde' } }),
      ),
    ).toBe('RECEBIMENTO_INVALIDO');
    expect(codigo(() => conferirLinha(null as unknown as LinhaConferida))).toBe('RECEBIMENTO_INVALIDO');
    expect(
      codigo(() =>
        conferirLinha({ ...emL('10', parcelas('10')), inspecao: null } as unknown as LinhaConferida),
      ),
    ).toBe('RECEBIMENTO_INVALIDO');
  });
});

describe('produto diferente: ocorrência de chegada, não estoque', () => {
  it('a linha do produto do documento fica com conferido 0 e nenhum movimento', () => {
    const linha = emL('20', parcelas('0'), { motivo: 'produto_diferente' });
    expect(conferirLinha(linha)).toMatchObject({ divergente: true });
    expect(movimentosDaLinha(linha, ids())).toEqual([]);
  });

  it('retido para decisão fica aberto com responsável e prazo; devolvido na entrega fica registrado', () => {
    const base = {
      produtoReal: { descricao: 'Fungicida B, tambor' },
      quantidade: '1',
      unidade: 'tambor 200 L',
      responsavel: 'almoxarife-a',
    } as const;
    expect(ocorrenciaDeChegada({ ...base, destino: 'retido_para_decisao', prazo: '2026-10-02' }).status).toBe(
      'aberta',
    );
    expect(ocorrenciaDeChegada({ ...base, destino: 'devolvido_na_entrega' }).status).toBe('registrada');
    expect(codigo(() => ocorrenciaDeChegada({ ...base, destino: 'retido_para_decisao' }))).toBe(
      'DATA_INVALIDA',
    );
    expect(
      codigo(() =>
        ocorrenciaDeChegada({ ...base, produtoReal: { descricao: ' ' }, destino: 'devolvido_na_entrega' }),
      ),
    ).toBe('RECEBIMENTO_INVALIDO');
    expect(
      codigo(() => ocorrenciaDeChegada({ ...base, quantidade: '0', destino: 'devolvido_na_entrega' })),
    ).toBe('RECEBIMENTO_INVALIDO');
    expect(
      codigo(() => ocorrenciaDeChegada({ ...base, destino: 'descartado' as 'devolvido_na_entrega' })),
    ).toBe('RECEBIMENTO_INVALIDO');
  });
});

describe('validade no recebimento (RN-032): nunca data fictícia', () => {
  it('lote novo segue a política vigente do produto', () => {
    expect(validadeNoRecebimento({ politicaProduto: 'nao_se_aplica', informada: null })).toBeNull();
    expect(validadeNoRecebimento({ politicaProduto: 'controla', informada: '2027-06-30' })).toBe(
      '2027-06-30',
    );
    expect(codigo(() => validadeNoRecebimento({ politicaProduto: 'controla', informada: null }))).toBe(
      'VALIDADE_OBRIGATORIA',
    );
    expect(
      codigo(() => validadeNoRecebimento({ politicaProduto: 'nao_se_aplica', informada: '2027-06-30' })),
    ).toBe('VALIDADE_NAO_SE_APLICA');
  });

  it('lote existente: a validade congelada no lote prevalece sobre a política atual do produto', () => {
    // O produto passou a "não se aplica", mas o lote nasceu com validade: o novo recebimento no lote exige a mesma data.
    const antigo = { validade: '2027-06-30' };
    expect(
      validadeNoRecebimento({
        politicaProduto: 'nao_se_aplica',
        loteExistente: antigo,
        informada: '2027-06-30',
      }),
    ).toBe('2027-06-30');
    expect(
      codigo(() =>
        validadeNoRecebimento({ politicaProduto: 'nao_se_aplica', loteExistente: antigo, informada: null }),
      ),
    ).toBe('VALIDADE_OBRIGATORIA');
    expect(
      codigo(() =>
        validadeNoRecebimento({
          politicaProduto: 'controla',
          loteExistente: antigo,
          informada: '2027-07-01',
        }),
      ),
    ).toBe('VALIDADE_DIFERENTE_DO_LOTE');
    // E o inverso: lote sem validade continua sem, mesmo que o produto passe a controlar.
    const semValidade = { validade: null };
    expect(
      validadeNoRecebimento({ politicaProduto: 'controla', loteExistente: semValidade, informada: null }),
    ).toBeNull();
    expect(
      codigo(() =>
        validadeNoRecebimento({
          politicaProduto: 'controla',
          loteExistente: semValidade,
          informada: '2027-06-30',
        }),
      ),
    ).toBe('VALIDADE_NAO_SE_APLICA');
  });
});

describe('lote interno de granel e identidade da origem', () => {
  const doc1 = 'aaaaaaaa-1111-4111-8111-bbbbbbbbbbbb';
  const doc2 = 'cccccccc-2222-4222-8222-dddddddddddd';

  it('DOC:<id do documento>: documentos diferentes nunca dividem lote; o mesmo documento reusa', () => {
    expect(codigoLoteInterno(doc1)).toBe(`DOC:${doc1}`);
    expect(codigoLoteInterno(doc1)).toBe(codigoLoteInterno(doc1));
    expect(codigoLoteInterno(doc2)).not.toBe(codigoLoteInterno(doc1));
    expect(codigo(() => codigoLoteInterno('NF-1-123'))).toBe('LOTE_INTERNO_INVALIDO');
    expect(codigo(() => codigoLoteInterno(doc1.toUpperCase()))).toBe('LOTE_INTERNO_INVALIDO');
  });

  it('série e número sem espaços nas pontas, NFC e sem zeros à esquerda quando numéricos', () => {
    expect(identidadeDaOrigem({ tipo: 'nfe', serie: ' 001 ', numero: '000123' })).toEqual({
      tipo: 'nfe',
      serie: '1',
      numero: '123',
    });
    expect(identidadeDaOrigem({ tipo: 'nfe', serie: '0', numero: '0' })).toEqual({
      tipo: 'nfe',
      serie: '0',
      numero: '0',
    });
    expect(identidadeDaOrigem({ tipo: 'outro', serie: '', numero: 'Á-7' }).numero).toBe('Á-7');
    expect(identidadeDaOrigem({ tipo: 'outro', serie: 'A1', numero: '007B' }).numero).toBe('007B');
    expect(codigo(() => identidadeDaOrigem({ tipo: 'boleto', serie: '1', numero: '1' }))).toBe(
      'RECEBIMENTO_INVALIDO',
    );
    expect(codigo(() => identidadeDaOrigem({ tipo: 'nfe', serie: '1', numero: '  ' }))).toBe(
      'RECEBIMENTO_INVALIDO',
    );
  });
});

describe('numeração e próxima ação', () => {
  it('movimentos numerados de 1 a M na intenção, na ordem das linhas e das parcelas', () => {
    const gerador = ids();
    const l1 = emL('10', parcelas('6', '4'), { numero: 1, inspecao });
    const l2 = emGalao('2', parcelas('1', '0', '1'), { numero: 2, motivo: 'avaria' });
    const numerados = numerarMovimentos([
      { numero: 2, movimentos: movimentosDaLinha(l2, gerador) },
      { numero: 1, movimentos: movimentosDaLinha(l1, gerador) },
    ]);
    expect(numerados.map((n) => [n.linha, n.item, n.movimento.parcela])).toEqual([
      [1, 1, 'apto'],
      [1, 2, 'quarentena'],
      [2, 3, 'apto'],
      [2, 4, 'bloqueado'],
    ]);
    expect(
      codigo(() =>
        numerarMovimentos([
          { numero: 1, movimentos: [] },
          { numero: 1, movimentos: [] },
        ]),
      ),
    ).toBe('RECEBIMENTO_INVALIDO');
  });

  it('só ações que existem no incremento 1, com a inspeção pendente primeiro', () => {
    expect(proximaAcao({ inspecaoPendente: true, divergente: true, ocorrenciaAberta: true })).toBe(
      'Ver inspeção pendente',
    );
    expect(proximaAcao({ inspecaoPendente: false, divergente: true, ocorrenciaAberta: false })).toBe(
      'Ver divergência',
    );
    expect(proximaAcao({ inspecaoPendente: false, divergente: false, ocorrenciaAberta: true })).toBe(
      'Ver divergência',
    );
    expect(proximaAcao({ inspecaoPendente: false, divergente: false, ocorrenciaAberta: false })).toBe(
      'Receber documento',
    );
  });
});

describe('propriedades da conferência (fast-check)', () => {
  const parcela = fc.integer({ min: 0, max: 500 }).map(String);

  it('físico = conferido − recusado; movimentos só das parcelas físicas não nulas, somando o físico', () => {
    fc.assert(
      fc.property(fc.integer({ min: 1, max: 500 }), parcela, parcela, parcela, parcela, (doc, a, q, b, r) => {
        const p = parcelas(a, q, b, r);
        const conferido = Number(a) + Number(q) + Number(b) + Number(r);
        const divergente = conferido !== doc || Number(b) > 0 || Number(r) > 0;
        const motivo = !divergente
          ? undefined
          : conferido < doc
            ? ('falta' as const)
            : conferido > doc
              ? ('sobra' as const)
              : ('avaria' as const);
        const linha = emL(String(doc), p, {
          ...(motivo ? { motivo } : {}),
          ...(Number(q) > 0 ? { inspecao } : {}),
        });
        const resultado = conferirLinha(linha);
        expect(resultado.divergente).toBe(divergente);
        expect(resultado.fisico.toString()).toBe(String(conferido - Number(r)));
        const movs = movimentosDaLinha(linha, ids());
        expect(movs.length).toBe([a, q, b].filter((v) => v !== '0').length);
        const soma = movs.reduce((s, m) => s + Number(m.movimento.quantidade.valor.toString()), 0);
        expect(soma).toBe(conferido - Number(r));
      }),
      { numRuns: 200 },
    );
  });
});
