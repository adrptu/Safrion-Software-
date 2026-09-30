import { EsquemaDadosMovimento, EsquemaPedidoComando } from '@safrion/contracts';
import type { LinhaExtrato, LoteResumo } from '@safrion/db/web';
import { describe, expect, it } from 'vitest';

import { desfechoDaResposta, pedidoDeEntrada, SEM_CONEXAO, validarEntrada } from '../src/estoque/entrada';
import { estadoDoLote, palavraDaSituacao } from '../src/estoque/estado';
import {
  contextoDoLote,
  linhaDoLote,
  linhaDoMovimento,
  linhaDoProduto,
  unidadesDoLote,
} from '../src/estoque/lista';
import { formatarData } from '../src/formato/data';

const LOTE = '0b8c6a52-1f0e-4c7a-9d51-3f2d7e6b9a10';
const LOCAL = '5d2f0a4e-8c1b-4e3a-b7f6-9a0c1d2e3f40';
const zero = '0.000000';
const saldo = (p: Partial<Parameters<typeof estadoDoLote>[1]>) => ({
  fisico: zero,
  utilizavel: zero,
  quarentena: zero,
  bloqueado: zero,
  loteVencido: false,
  ...p,
});

describe('estado do lote pela tabela 74.4.3', () => {
  it('cada situação do saldo vira a palavra e o papel fixos', () => {
    expect(estadoDoLote(0, saldo({}))).toEqual({ palavra: 'Recebido', papel: 'neutro' });
    expect(estadoDoLote(2, saldo({}))).toEqual({ palavra: 'Esgotado', papel: 'neutro' });
    expect(estadoDoLote(1, saldo({ fisico: '3.000000', loteVencido: true }))).toEqual({
      palavra: 'Bloqueado · validade vencida',
      papel: 'erro',
    });
    expect(estadoDoLote(2, saldo({ fisico: '12.5', utilizavel: '10', quarentena: '2.5' }))).toEqual({
      palavra: 'Liberado',
      papel: 'sucesso',
    });
    expect(estadoDoLote(1, saldo({ fisico: '2.5', quarentena: '2.5' }))).toEqual({
      palavra: 'Em inspeção',
      papel: 'atencao',
    });
    expect(estadoDoLote(1, saldo({ fisico: '4', bloqueado: '4' }))).toEqual({
      palavra: 'Bloqueado',
      papel: 'erro',
    });
  });

  it('DS-24: a mesma palavra nunca aparece com duas cores', () => {
    const papelPorPalavra = new Map<string, string>();
    for (const movimentos of [0, 1])
      for (const fisico of [zero, '5'])
        for (const utilizavel of [zero, '5'])
          for (const quarentena of [zero, '5'])
            for (const loteVencido of [false, true]) {
              const e = estadoDoLote(
                movimentos,
                saldo({ fisico, utilizavel, quarentena, bloqueado: '1', loteVencido }),
              );
              expect(papelPorPalavra.get(e.palavra) ?? e.papel, e.palavra).toBe(e.papel);
              papelPorPalavra.set(e.palavra, e.papel);
            }
    expect([...papelPorPalavra.keys()].sort()).toEqual([
      'Bloqueado',
      'Bloqueado · validade vencida',
      'Em inspeção',
      'Esgotado',
      'Liberado',
      'Recebido',
    ]);
  });

  it('situação do movimento com as mesmas palavras', () => {
    expect(palavraDaSituacao('quarentena_livre')).toBe('Em inspeção');
    expect(palavraDaSituacao('liberado_livre')).toBe('Liberado');
    expect(palavraDaSituacao('liberado_bloqueado')).toBe('Bloqueado');
    expect(palavraDaSituacao('quarentena_bloqueado')).toBe('Bloqueado');
    expect(palavraDaSituacao('__proto__')).toBe('__proto__');
    expect(palavraDaSituacao(null)).toBe('');
  });
});

describe('registrar entrada', () => {
  const unidades = ['L', 'mL', 'm3'];
  it('valida e monta o pedido que o contrato aceita', () => {
    const v = validarEntrada(
      { quantidade: '1.234,5', unidade: 'mL', situacao: 'liberado_livre', local: LOCAL },
      unidades,
      [LOCAL],
    );
    expect(v).toEqual({
      ok: true,
      dados: { quantidade: '1234.5', unidade: 'mL', situacao: 'liberado_livre', local: LOCAL },
    });
    if (!v.ok) return;
    const corpo = pedidoDeEntrada({ id: LOTE, versao: 3 }, v.dados, 'chave-1');
    expect(corpo).toEqual({
      idempotencyKey: 'chave-1',
      target: { type: 'lot', id: LOTE, expectedVersion: 3 },
      data: {
        lote: LOTE,
        local: LOCAL,
        movimento: {
          tipo: 'entrada',
          quantidade: { valor: '1234.5', unidade: 'mL' },
          situacao: 'liberado_livre',
        },
      },
    });
    const pedido = EsquemaPedidoComando.parse(corpo);
    expect(EsquemaDadosMovimento.safeParse(pedido.data).success).toBe(true);
  });

  it('diz o que corrigir em cada campo e não oferece situação fora da entrada', () => {
    expect(
      validarEntrada({ quantidade: '', unidade: '', situacao: '', local: '' }, unidades, [LOCAL]),
    ).toEqual({
      ok: false,
      erros: {
        quantidade: 'Informe a quantidade.',
        unidade: 'Escolha a unidade.',
        situacao: 'Escolha se a entrada vai para inspeção ou já está liberada.',
        local: 'Escolha o local.',
      },
    });
    const bloqueado = validarEntrada(
      { quantidade: '1', unidade: 'kg', situacao: 'liberado_bloqueado', local: LOCAL },
      unidades,
      [LOCAL],
    );
    expect(bloqueado.ok ? {} : bloqueado.erros).toEqual({
      unidade: 'Escolha a unidade.',
      situacao: 'Escolha se a entrada vai para inspeção ou já está liberada.',
    });
  });

  it('lê a resposta do servidor', () => {
    expect(desfechoDaResposta(200, { outcome: 'confirmed', alreadyReceived: false })).toEqual({
      tipo: 'confirmado',
      jaRecebido: false,
    });
    expect(desfechoDaResposta(200, { outcome: 'confirmed', alreadyReceived: true })).toEqual({
      tipo: 'confirmado',
      jaRecebido: true,
    });
    // 200 sem recibo confirmado é resposta inesperada: a entrada pode ter sido gravada, fica para conferir.
    expect(desfechoDaResposta(200, { outcome: 'rejected' })).toMatchObject({ tipo: 'falha', incerto: true });
    expect(desfechoDaResposta(200, null)).toMatchObject({ tipo: 'falha', incerto: true });
    expect(desfechoDaResposta(409, { outcome: 'version_conflict' })).toEqual({
      tipo: 'conflito',
      mensagem: 'O lote mudou enquanto você registrava. Confira o saldo atualizado e registre de novo.',
    });
    expect(desfechoDaResposta(422, { reasonCode: 'UNIDADE_INCOMPATIVEL' })).toEqual({
      tipo: 'recusado',
      mensagem: 'Esta unidade não serve para o produto do lote.',
      campo: 'unidade',
    });
    expect(desfechoDaResposta(422, { reasonCode: 'LOTE_NAO_ENCONTRADO' })).toEqual({
      tipo: 'recusado',
      mensagem: 'Este lote não está mais disponível.',
    });
    for (const codigo of ['OUTRO', '__proto__', 7])
      expect(desfechoDaResposta(422, { reasonCode: codigo })).toEqual({
        tipo: 'recusado',
        mensagem: 'A entrada foi recusada. Confira os dados e tente de novo.',
      });
    expect(desfechoDaResposta(401, {}).tipo).toBe('sessao');
    expect(desfechoDaResposta(403, {})).toEqual({
      tipo: 'falha',
      mensagem: 'Seu papel não permite registrar entrada.',
      incerto: false,
    });
    for (const status of [400, 413, 415])
      expect(desfechoDaResposta(status, {}).tipo === 'falha' && desfechoDaResposta(status, {})).toMatchObject(
        {
          mensagem: 'O pedido não foi aceito. Recarregue a página e tente de novo.',
          incerto: false,
        },
      );
    for (const status of [500, 502, 504])
      expect(desfechoDaResposta(status, 'x')).toEqual({
        tipo: 'falha',
        mensagem:
          'O servidor não respondeu como esperado. A entrada pode ter chegado: registre de novo para conferir, sem duplicar.',
        incerto: true,
      });
    expect(SEM_CONEXAO).toMatchObject({ tipo: 'falha', incerto: true });
  });
});

describe('linhas das listas', () => {
  const lote: LoteResumo = {
    id: LOTE,
    codigo: 'DEMO-001',
    produtoId: 'p',
    produto: 'Herbicida fictício',
    validade: '2027-06-30',
    unidade: 'L',
    movimentos: 2,
    saldo: {
      version: 2,
      fisico: '1250.500000',
      utilizavel: '1000.000000',
      quarentena: '250.500000',
      bloqueado: zero,
      vencido: zero,
      loteVencido: false,
    },
  };

  it('lote: texto em pt-BR, valor exato para ordenar e somar', () => {
    expect(linhaDoLote(lote)).toEqual({
      id: LOTE,
      href: `/estoque/${LOTE}`,
      celulas: {
        lote: { texto: 'DEMO-001', valor: 'DEMO-001' },
        produto: { texto: 'Herbicida fictício', valor: 'Herbicida fictício' },
        validade: { texto: '30/06/2027', valor: '2027-06-30' },
        estado: { texto: 'Liberado', valor: 'Liberado', papel: 'sucesso' },
        utilizavel: { texto: '1.000 L', valor: '1000.000000', unidade: 'L' },
        fisico: { texto: '1.250,5 L', valor: '1250.500000', unidade: 'L' },
      },
    });
  });

  it('lote sem validade: "Não se aplica", valor vazio (fim da ordenação) e o resto da linha igual', () => {
    const sem = linhaDoLote({ ...lote, validade: null });
    expect(sem.celulas['validade']).toEqual({ texto: 'Não se aplica', valor: '' });
    expect({ ...sem.celulas, validade: undefined }).toEqual({
      ...linhaDoLote(lote).celulas,
      validade: undefined,
    });
    expect(contextoDoLote({ produto: 'Diesel', validade: null })).toBe('Diesel · validade não se aplica');
    expect(contextoDoLote(lote)).toBe('Herbicida fictício · validade 30/06/2027');
    // O formatador geral não ganha tolerância a null: quem sabe que não há validade decide o texto.
    expect(() => formatarData(null as unknown as string)).toThrow();
  });

  it('produto e movimento', () => {
    expect(linhaDoProduto({ id: 'p1', nome: 'Adubo', unidade: 'sc60', lotes: 3 }).celulas).toEqual({
      produto: { texto: 'Adubo', valor: 'Adubo' },
      unidade: { texto: 'sc 60 kg', valor: 'sc60' },
      lotes: { texto: '3', valor: '3' },
    });
    const base: LinhaExtrato = {
      movementId: 'm1',
      locationId: LOCAL,
      kind: 'entrada',
      situacao: 'quarentena_livre',
      de: null,
      para: null,
      estornaId: null,
      lotVersion: 2,
      baseQuantity: '2.5',
      baseUnit: 'L',
      originalQuantity: '2500',
      originalUnit: 'mL',
      recordedAt: '2026-09-28T14:05:00.000Z',
    };
    const locais = new Map([[LOCAL, 'Almoxarifado central']]);
    expect(linhaDoMovimento(base, locais)).toEqual({
      id: 'm1',
      href: '',
      celulas: {
        quando: { texto: '28/09/2026 11:05', valor: '2026-09-28T14:05:00.000Z' },
        movimento: { texto: 'Entrada · Em inspeção', valor: 'Entrada · Em inspeção' },
        quantidade: { texto: '2,5 L (2.500 mL)', valor: '2.5', unidade: 'L' },
        local: { texto: 'Almoxarifado central', valor: 'Almoxarifado central' },
      },
    });
    const mudanca = linhaDoMovimento(
      {
        ...base,
        kind: 'mudanca',
        situacao: null,
        de: 'quarentena_livre',
        para: 'liberado_livre',
        originalUnit: 'L',
      },
      new Map(),
    );
    expect(mudanca.celulas['movimento']?.texto).toBe('Em inspeção → Liberado');
    expect(mudanca.celulas['quantidade']?.texto).toBe('2,5 L');
    expect(mudanca.celulas['local']).toEqual({ texto: 'Local indisponível', valor: '' });
    const estorno = linhaDoMovimento(
      {
        ...base,
        kind: 'estorno',
        baseQuantity: null,
        baseUnit: null,
        originalQuantity: null,
        originalUnit: null,
      },
      locais,
    );
    expect(estorno.celulas['movimento']?.texto).toBe('Estorno');
    expect(estorno.celulas['quantidade']).toEqual({ texto: '—', valor: '' });
  });

  it('unidades do lote: a base primeiro, só da mesma dimensão', () => {
    expect(unidadesDoLote('L')).toEqual([
      { valor: 'L', rotulo: 'L' },
      { valor: 'mL', rotulo: 'mL' },
      { valor: 'm3', rotulo: 'm³' },
    ]);
    expect(unidadesDoLote('kg').map((u) => u.valor)).toEqual(['kg', 'g', 't', 'sc60']);
    expect(unidadesDoLote('xx')).toEqual([]);
    expect(unidadesDoLote('__proto__')).toEqual([]);
  });
});
