import fc from 'fast-check';
import { describe, expect, it } from 'vitest';

import {
  aplicar,
  calcularSaldo,
  conversaoEmbalagem,
  dataCivil,
  embalagensParaBase,
  ErroDominio,
  estadoInicial,
  lote,
  ordemFefo,
  paraTexto,
  quantidade,
  saldo,
  SITUACOES,
  type CodigoUnidade,
  type EstadoLote,
  type Movimento,
  type SaldoLote,
  type Situacao,
} from '../src/index.js';

const HOJE = '2026-09-27';
const q = (v: string, u = 'L') => quantidade(v, u);
const txt = (s: SaldoLote) => ({
  fisico: paraTexto(s.fisico, 6),
  utilizavel: paraTexto(s.utilizavel, 6),
  quarentena: paraTexto(s.quarentena, 6),
  bloqueado: paraTexto(s.bloqueado, 6),
  vencido: paraTexto(s.vencido, 6),
  restrito: paraTexto(s.restrito, 6),
  loteVencido: s.loteVencido,
});
const codigo = (f: () => unknown) => {
  try {
    f();
  } catch (e) {
    return e instanceof ErroDominio ? e.codigo : 'OUTRO';
  }
  return 'SEM_ERRO';
};
const entrada = (id: string, v: string, situacao: Situacao, u = 'L'): Movimento => ({
  id,
  tipo: 'entrada',
  quantidade: q(v, u),
  situacao,
});
const mudanca = (id: string, v: string, de: Situacao, para: Situacao): Movimento => ({
  id,
  tipo: 'mudanca',
  quantidade: q(v),
  de,
  para,
});

describe('saldo por lote (RF-SUP-003, RN-015, ENG-026)', () => {
  const l = lote('F26-02', '2027-06-30', 'L');

  it('AC-14 e RF-SUP-007: recebe 60 com 10 em quarentena → físico 60, utilizável 50', () => {
    const s = calcularSaldo(
      l,
      [entrada('m1', '50', 'liberado_livre'), entrada('m2', '10', 'quarentena_livre')],
      HOJE,
    );
    expect(txt(s)).toMatchObject({ fisico: '60.000000', utilizavel: '50.000000', quarentena: '10.000000' });
    expect(s.politica).toBe('PREC-1');
  });

  it('DEMO-02: liberar a quarentena soma uma única vez; reenvio idêntico não soma; outro conteúdo é conflito', () => {
    let e = estadoInicial(l);
    e = aplicar(e, entrada('m1', '50', 'liberado_livre'));
    e = aplicar(e, entrada('m2', '10', 'quarentena_livre'));
    const liberar = mudanca('m3', '10', 'quarentena_livre', 'liberado_livre');
    e = aplicar(e, liberar);
    expect(txt(saldo(e, HOJE)).utilizavel).toBe('60.000000');
    expect(txt(saldo(aplicar(e, liberar), HOJE)).utilizavel).toBe('60.000000');
    expect(codigo(() => aplicar(e, { ...liberar, id: 'm4' }))).toBe('SALDO_INSUFICIENTE');
    expect(codigo(() => aplicar(e, mudanca('m3', '5', 'quarentena_livre', 'liberado_livre')))).toBe(
      'MOVIMENTO_CONFLITANTE',
    );
  });

  it('tarefa do Adrianus: 2 galões de 5 L do F26-03, 1 apto e 1 avariado; a origem da embalagem fica registrada', () => {
    const galao = conversaoEmbalagem('galão 5 L', '5', 'L', 1);
    const um = embalagensParaBase('1', galao);
    const lt = lote('F26-03', '2027-08-31', 'L');
    let e = estadoInicial(lt);
    e = aplicar(e, {
      id: 'r1',
      tipo: 'entrada',
      quantidade: um.quantidade,
      situacao: 'liberado_livre',
      origem: um.origem,
    });
    e = aplicar(e, { id: 'r2', tipo: 'entrada', quantidade: um.quantidade, situacao: 'liberado_bloqueado' });
    expect(txt(saldo(e, HOJE))).toMatchObject({
      fisico: '10.000000',
      bloqueado: '5.000000',
      utilizavel: '5.000000',
    });
    expect(e.registros.get('r1')?.origem).toEqual({
      embalagem: 'galão 5 L',
      contagem: '1',
      versaoConversao: 1,
    });
  });

  it('reenvio com a origem em outra ordem é o mesmo movimento; outro dado de negócio é conflito (F0A-C01)', () => {
    const um = embalagensParaBase('1', conversaoEmbalagem('galão 5 L', '5', 'L', 1));
    const lt = lote('F26-03', '2027-08-31', 'L');
    const com = (origem: unknown) =>
      ({
        id: 'r1',
        tipo: 'entrada',
        quantidade: um.quantidade,
        situacao: 'liberado_livre',
        origem,
      }) as Movimento;
    let e = aplicar(estadoInicial(lt), com({ embalagem: 'galão 5 L', contagem: '1', versaoConversao: 1 }));
    e = aplicar(e, com({ versaoConversao: 1, contagem: '1', embalagem: 'galão 5 L' }));
    e = aplicar(e, com({ contagem: '1.0', versaoConversao: 1, embalagem: 'galão 5 L' }));
    expect(txt(saldo(e, HOJE)).fisico).toBe('5.000000');
    expect(e.registros.get('r1')?.origem).toEqual({
      embalagem: 'galão 5 L',
      contagem: '1',
      versaoConversao: 1,
    });
    for (const outra of [
      { embalagem: 'galão 5 L', contagem: '2', versaoConversao: 1 },
      { embalagem: 'galão 5 L', contagem: '1', versaoConversao: 2 },
      { embalagem: 'balde 5 L', contagem: '1', versaoConversao: 1 },
      undefined,
    ]) {
      expect(codigo(() => aplicar(e, com(outra)))).toBe('MOVIMENTO_CONFLITANTE');
    }
    const fora = (origem: unknown) => codigo(() => aplicar(estadoInicial(lt), com(origem)));
    for (const invalida of [
      null,
      'galão 5 L',
      { embalagem: 5, contagem: '1', versaoConversao: 1 },
      { embalagem: ' ', contagem: '1', versaoConversao: 1 },
      { embalagem: 'galão', contagem: '1.5', versaoConversao: 1 },
      { embalagem: 'galão', contagem: '0', versaoConversao: 1 },
      { embalagem: 'galão', contagem: '1', versaoConversao: '1' },
      { embalagem: 'galão', contagem: '1', versaoConversao: 1.5 },
      { embalagem: 'galão', contagem: '1', versaoConversao: 0 },
    ]) {
      expect(fora(invalida)).toBe('MOVIMENTO_INVALIDO');
    }
    expect(fora({ embalagem: 'galão', contagem: 1, versaoConversao: 1 })).toBe('NUMERO_BINARIO_RECUSADO');
  });

  it('item indivisível: lote em un recusa fração, sem arredondar; massa e volume mantêm 6 casas (F0A-C02)', () => {
    const pecas = lote('P-01', '2027-01-01', 'un');
    const emUn = (id: string, v: string, situacao: Situacao) => entrada(id, v, situacao, 'un');
    expect(codigo(() => calcularSaldo(pecas, [emUn('m', '0.5', 'liberado_livre')], HOJE))).toBe(
      'QUANTIDADE_FORA_DA_ESCALA',
    );
    expect(codigo(() => calcularSaldo(pecas, [emUn('m', '1.000001', 'liberado_livre')], HOJE))).toBe(
      'QUANTIDADE_FORA_DA_ESCALA',
    );
    const fracao: Movimento = {
      id: 'x',
      tipo: 'mudanca',
      quantidade: q('0.5', 'un'),
      de: 'liberado_livre',
      para: 'liberado_bloqueado',
    };
    expect(codigo(() => calcularSaldo(pecas, [emUn('m', '3', 'liberado_livre'), fracao], HOJE))).toBe(
      'QUANTIDADE_FORA_DA_ESCALA',
    );
    const s = calcularSaldo(
      pecas,
      [emUn('m', '3', 'liberado_livre'), emUn('n', '2.0', 'quarentena_livre')],
      HOJE,
    );
    expect(txt(s)).toMatchObject({ fisico: '5.000000', utilizavel: '3.000000', quarentena: '2.000000' });
    expect(txt(calcularSaldo(l, [entrada('m', '0.5', 'liberado_livre')], HOJE)).fisico).toBe('0.500000');
  });

  it('forma inválida vira erro de domínio, não TypeError, e o estado recebido não muda (F0A-C03)', () => {
    const e = aplicar(estadoInicial(l), entrada('m1', '5', 'liberado_livre'));
    for (const m of [null, undefined, 'entrada', 42, []]) {
      expect(codigo(() => aplicar(e, m as unknown as Movimento))).toBe('MOVIMENTO_INVALIDO');
    }
    expect(txt(saldo(e, HOJE)).fisico).toBe('5.000000');
    expect(codigo(() => calcularSaldo(l, null as unknown as Movimento[], HOJE))).toBe('MOVIMENTO_INVALIDO');
    expect(codigo(() => calcularSaldo(l, [null] as unknown as Movimento[], HOJE))).toBe('MOVIMENTO_INVALIDO');
  });

  it('restrições independentes: bloquear e desbloquear não libera a quarentena (achado 5)', () => {
    const s = calcularSaldo(
      l,
      [
        entrada('m1', '10', 'quarentena_livre'),
        mudanca('m2', '10', 'quarentena_livre', 'quarentena_bloqueado'),
        mudanca('m3', '10', 'quarentena_bloqueado', 'quarentena_livre'),
      ],
      HOJE,
    );
    expect(txt(s)).toMatchObject({ utilizavel: '0.000000', quarentena: '10.000000' });
    expect(
      codigo(() => calcularSaldo(l, [mudanca('x', '1', 'quarentena_livre', 'liberado_bloqueado')], HOJE)),
    ).toBe('MOVIMENTO_INVALIDO');
  });

  it('lote vencido: sem sobreposição, físico = utilizável + quarentena + bloqueado + vencido (achado 4)', () => {
    const vencendo = lote('F26-01', '2026-09-26', 'L');
    const movs = [
      entrada('a', '20', 'liberado_livre'),
      entrada('b', '5', 'liberado_bloqueado'),
      entrada('c', '3', 'quarentena_livre'),
      entrada('d', '2', 'quarentena_bloqueado'),
    ];
    expect(txt(calcularSaldo(vencendo, movs, HOJE))).toEqual({
      fisico: '30.000000',
      utilizavel: '0.000000',
      quarentena: '3.000000',
      bloqueado: '7.000000',
      vencido: '20.000000',
      restrito: '30.000000',
      loteVencido: true,
    });
    expect(calcularSaldo(vencendo, movs, '2026-09-26').loteVencido).toBe(false);
  });

  it('estorno desfaz o movimento vinculado; reenvio do estorno é idempotente; não se estorna duas vezes', () => {
    let e = estadoInicial(l);
    e = aplicar(e, entrada('m1', '15', 'liberado_livre'));
    const est: Movimento = { id: 'e1', tipo: 'estorno', estornaId: 'm1' };
    e = aplicar(e, est);
    expect(txt(saldo(e, HOJE)).fisico).toBe('0.000000');
    expect(txt(saldo(aplicar(e, est), HOJE)).fisico).toBe('0.000000');
    expect(codigo(() => aplicar(e, { id: 'e2', tipo: 'estorno', estornaId: 'm1' }))).toBe('ESTORNO_INVALIDO');
    expect(codigo(() => aplicar(e, { id: 'e3', tipo: 'estorno', estornaId: 'e1' }))).toBe('ESTORNO_INVALIDO');
    expect(codigo(() => aplicar(e, { id: 'e4', tipo: 'estorno', estornaId: 'nao-existe' }))).toBe(
      'ESTORNO_INVALIDO',
    );
    expect(codigo(() => aplicar(e, { id: 'e5', tipo: 'estorno', estornaId: ' ' }))).toBe(
      'MOVIMENTO_INVALIDO',
    );
  });

  it('estorno que deixaria saldo negativo é recusado', () => {
    let e = estadoInicial(l);
    e = aplicar(e, entrada('m1', '10', 'quarentena_livre'));
    e = aplicar(e, mudanca('m2', '10', 'quarentena_livre', 'liberado_livre'));
    expect(codigo(() => aplicar(e, { id: 'e1', tipo: 'estorno', estornaId: 'm1' }))).toBe(
      'SALDO_INSUFICIENTE',
    );
  });

  it('escala de 6 casas na unidade-base: o que aparece é o que decide (achado 1)', () => {
    expect(codigo(() => calcularSaldo(l, [entrada('m', '0.0000008', 'liberado_livre')], HOJE))).toBe(
      'QUANTIDADE_FORA_DA_ESCALA',
    );
    expect(codigo(() => calcularSaldo(l, [entrada('m', '0.0001', 'liberado_livre', 'mL')], HOJE))).toBe(
      'QUANTIDADE_FORA_DA_ESCALA',
    );
    const s = calcularSaldo(l, [entrada('m', '2500', 'liberado_livre', 'mL')], HOJE);
    expect(txt(s).fisico).toBe('2.500000');
  });

  it('valida em tempo de execução o que chega de fora (achado 2)', () => {
    const e = estadoInicial(l);
    const fora = (m: unknown) => codigo(() => aplicar(e, m as Movimento));
    expect(
      fora({ id: 'x', tipo: 'mudanca', quantidade: q('4'), de: 'Apto', para: 'liberado_bloqueado' }),
    ).toBe('MOVIMENTO_INVALIDO');
    expect(fora({ id: 'x', tipo: 'entrada', quantidade: q('4'), situacao: 'vencido' })).toBe(
      'MOVIMENTO_INVALIDO',
    );
    expect(fora({ id: 'x', tipo: 'saida', quantidade: q('4') })).toBe('MOVIMENTO_INVALIDO');
    expect(fora({ id: '', tipo: 'entrada', quantidade: q('4'), situacao: 'liberado_livre' })).toBe(
      'MOVIMENTO_INVALIDO',
    );
    expect(
      fora({ id: 'x', tipo: 'entrada', quantidade: { valor: 4, unidade: 'L' }, situacao: 'liberado_livre' }),
    ).toBe('DECIMAL_INVALIDO');
    expect(fora(entrada('x', '0', 'liberado_livre'))).toBe('QUANTIDADE_INVALIDA');
    expect(fora(entrada('x', '-1', 'liberado_livre'))).toBe('QUANTIDADE_INVALIDA');
    expect(fora(entrada('x', '1000000000000000', 'liberado_livre'))).toBe('QUANTIDADE_INVALIDA');
    expect(fora(entrada('x', '1', 'liberado_livre', 'kg'))).toBe('UNIDADE_INCOMPATIVEL');
    expect(fora(mudanca('x', '1', 'liberado_livre', 'liberado_livre'))).toBe('MOVIMENTO_INVALIDO');
  });

  it('valida lote e datas civis', () => {
    expect(codigo(() => lote(' ', '2027-01-01', 'L'))).toBe('LOTE_INVALIDO');
    expect(codigo(() => lote('X', '2027-02-30', 'L'))).toBe('DATA_INVALIDA');
    expect(codigo(() => lote('X', '27/09/2026', 'L'))).toBe('DATA_INVALIDA');
    expect(codigo(() => lote('X', '2027-01-01', 'mL'))).toBe('UNIDADE_INCOMPATIVEL');
    expect(codigo(() => lote('X', '2027-01-01', 'galão' as CodigoUnidade))).toBe('UNIDADE_INCOMPATIVEL');
    expect(codigo(() => dataCivil(20270101))).toBe('DATA_INVALIDA');
    expect(dataCivil('2028-02-29')).toBe('2028-02-29');
  });

  it('lote sem validade (RN-032): null explícito, nunca vence; texto vazio continua inválido', () => {
    const diesel = lote('DIESEL', null, 'L');
    expect(diesel.validade).toBeNull();
    const s = calcularSaldo(diesel, [entrada('d1', '500', 'liberado_livre')], '2099-12-31');
    expect(txt(s)).toMatchObject({ utilizavel: '500.000000', vencido: '0.000000', loteVencido: false });
    expect(codigo(() => lote('X', '', 'L'))).toBe('DATA_INVALIDA');
    expect(codigo(() => saldo(estadoInicial(diesel), 'hoje'))).toBe('DATA_INVALIDA');
  });

  it('regressão: lote com validade vence no dia seguinte ao da validade, como antes', () => {
    const e = aplicar(estadoInicial(l), entrada('v1', '5', 'liberado_livre'));
    expect(saldo(e, '2027-06-30').loteVencido).toBe(false);
    expect(txt(saldo(e, '2027-07-01'))).toMatchObject({
      utilizavel: '0.000000',
      vencido: '5.000000',
      loteVencido: true,
    });
  });

  it('reconstrução em tempo linear: um acumulador só, sem copiar o estado a cada movimento (achado 3)', () => {
    // Prova determinística: tempo de relógio oscila com a carga da máquina e da CI; a contagem de cópias, não.
    const movs: Movimento[] = [];
    for (let i = 0; i < 5000; i++) {
      movs.push(entrada(`e${String(i)}`, '1.5', 'quarentena_livre'));
      movs.push(mudanca(`m${String(i)}`, '1.5', 'quarentena_livre', 'liberado_livre'));
    }
    const MapOriginal = globalThis.Map;
    let mapasCriados = 0;
    class MapContado<K, V> extends MapOriginal<K, V> {
      constructor(entradas?: Iterable<readonly [K, V]> | null) {
        super(entradas);
        mapasCriados++;
      }
    }
    globalThis.Map = MapContado;
    let s: SaldoLote;
    try {
      s = calcularSaldo(l, movs, HOJE);
    } finally {
      globalThis.Map = MapOriginal;
    }
    expect(mapasCriados).toBe(1);
    expect(txt(s).utilizavel).toBe('7500.000000');
  });
});

describe('ordem FEFO: lote sem validade continua elegível, depois dos datados', () => {
  const candidato = (
    chave: string,
    validade: string | null,
    primeiraEntrada: string,
    situacao: Situacao,
  ) => ({
    chave,
    validade,
    primeiraEntrada,
    saldo: calcularSaldo(lote(chave, validade, 'L'), [entrada('e', '1', situacao)], HOJE),
  });
  const lista = [
    candidato('sem-2', null, '2026-09-02T10:00:00.000Z', 'liberado_livre'),
    candidato('dez', '2026-12-31', '2026-09-05T10:00:00.000Z', 'liberado_livre'),
    candidato('sem-1', null, '2026-09-01T10:00:00.000Z', 'liberado_livre'),
    candidato('out', '2026-10-31', '2026-09-09T10:00:00.000Z', 'liberado_livre'),
    candidato('quar', '2026-10-01', '2026-09-01T10:00:00.000Z', 'quarentena_livre'),
    candidato('bloq', '2026-10-01', '2026-09-01T10:00:00.000Z', 'liberado_bloqueado'),
    candidato('venc', '2026-09-01', '2026-08-01T10:00:00.000Z', 'liberado_livre'),
  ];

  it('datados pelo vencimento; sem validade pela primeira entrada; quarentena, bloqueio e vencido fora', () => {
    expect(ordemFefo(lista)).toEqual(['out', 'dez', 'sem-1', 'sem-2']);
    expect(ordemFefo([...lista].reverse())).toEqual(['out', 'dez', 'sem-1', 'sem-2']);
  });

  it('empate de validade e de entrada sai pela chave; entrada ilegível é erro de domínio', () => {
    const iguais = [
      candidato('b', '2026-12-31', '2026-09-01T10:00:00.000Z', 'liberado_livre'),
      candidato('a', '2026-12-31', '2026-09-01T10:00:00.000Z', 'liberado_livre'),
    ];
    expect(ordemFefo(iguais)).toEqual(['a', 'b']);
    const ilegivel = candidato('c', '2026-12-31', 'ontem', 'liberado_livre');
    expect(codigo(() => ordemFefo([ilegivel]))).toBe('MOVIMENTO_INVALIDO');
  });
});

describe('propriedades do saldo (fast-check)', () => {
  const situacao = fc.constantFrom<Situacao>(...SITUACOES);
  const quantidadeAleatoria = fc.oneof(
    fc.integer({ min: -2_000_000, max: 40_000_000 }).map((n) => q((n / 1_000_000).toFixed(6))),
    fc.integer({ min: -5, max: 40_000 }).map((n) => q(String(n), 'mL')),
  );
  const passo = fc.oneof(
    fc.record({ tipo: fc.constant('entrada' as const), quantidade: quantidadeAleatoria, situacao }),
    fc.record({
      tipo: fc.constant('mudanca' as const),
      quantidade: quantidadeAleatoria,
      de: situacao,
      para: situacao,
    }),
    fc.record({ tipo: fc.constant('estorno' as const), alvo: fc.nat({ max: 30 }) }),
  );
  const dia = fc.constantFrom('2026-09-27', '2027-07-01');
  const paraMovimento = (p: typeof passo extends fc.Arbitrary<infer T> ? T : never, i: number): Movimento => {
    const id = `m${String(i)}`;
    return p.tipo === 'estorno' ? { id, tipo: 'estorno', estornaId: `m${String(p.alvo)}` } : { ...p, id };
  };

  it('invariantes valem depois de qualquer sequência; movimento recusado não muda o estado', () => {
    fc.assert(
      fc.property(fc.array(passo, { maxLength: 30 }), dia, (passos, hoje) => {
        let e: EstadoLote = estadoInicial(lote('P', '2027-06-30', 'L'));
        passos.forEach((p, i) => {
          const antes = txt(saldo(e, hoje));
          try {
            e = aplicar(e, paraMovimento(p, i));
          } catch (err) {
            expect(err).toBeInstanceOf(ErroDominio);
            expect(txt(saldo(e, hoje))).toEqual(antes);
          }
          const s = saldo(e, hoje);
          for (const sit of SITUACOES) {
            expect(s.porSituacao[sit].isNegative()).toBe(false);
            expect(s.porSituacao[sit].decimalPlaces()).toBeLessThanOrEqual(6);
          }
          expect(s.fisico.equals(s.utilizavel.plus(s.quarentena).plus(s.bloqueado).plus(s.vencido))).toBe(
            true,
          );
          expect(s.utilizavel.lessThanOrEqualTo(s.fisico)).toBe(true);
          expect(s.restrito.equals(s.fisico.minus(s.utilizavel))).toBe(true);
          if (s.loteVencido) expect(s.utilizavel.isZero()).toBe(true);
        });
      }),
    );
  });

  it('aplicar um a um e reconstruir o histórico dão o mesmo saldo (reconstruível, determinístico)', () => {
    fc.assert(
      fc.property(fc.array(passo, { maxLength: 20 }), (passos) => {
        const aceitos: Movimento[] = [];
        let e = estadoInicial(lote('P', '2027-06-30', 'L'));
        passos.forEach((p, i) => {
          const m = paraMovimento(p, i);
          try {
            e = aplicar(e, m);
            aceitos.push(m);
          } catch {
            // recusado: não entra no histórico
          }
        });
        expect(txt(calcularSaldo(lote('P', '2027-06-30', 'L'), aceitos, HOJE))).toEqual(txt(saldo(e, HOJE)));
      }),
    );
  });
});
