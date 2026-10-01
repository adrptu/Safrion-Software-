import { describe, expect, it } from 'vitest';
import { z } from 'zod';

import {
  ERROS,
  EsquemaDadosMovimento,
  EsquemaErro,
  EsquemaInstanteConfirmado,
  EsquemaPedidoComando,
  EsquemaQuantidade,
  EsquemaRecibo,
  criarRegistrador,
  erroContrato,
  erroDeValidacao,
  falhaPermanenteSemGravacao,
  statusDoRecibo,
} from '../src/index.js';

const UUID = '3f2449ee-7729-4f0a-96cc-d0f539bf7a66';
const pedido = { idempotencyKey: 'k-1', target: { type: 'lot', id: UUID, expectedVersion: 0 }, data: {} };

describe('quantidade (RN-033; PRD 10.0; ENG-014)', () => {
  it('aceita texto decimal canônico com unidade cadastrada', () => {
    expect(EsquemaQuantidade.parse({ valor: '12.5', unidade: 'L' })).toEqual({ valor: '12.5', unidade: 'L' });
  });

  it('recusa número JSON, unidade ausente ou desconhecida, texto fora do formato e mais de 34 algarismos', () => {
    for (const q of [
      { valor: 12.5, unidade: 'L' },
      { valor: '12.5' },
      { valor: '12.5', unidade: 'galão' },
      { valor: '12,5', unidade: 'L' },
      { valor: '-0', unidade: 'L' },
      { valor: '1'.repeat(35), unidade: 'L' },
      { valor: '1', unidade: 'L', extra: true },
    ]) {
      expect(EsquemaQuantidade.safeParse(q).success, JSON.stringify(q)).toBe(false);
    }
  });

  it('o problema do decimal usa o código do domínio', () => {
    const r = EsquemaQuantidade.safeParse({ valor: '1'.repeat(35), unidade: 'L' });
    expect(r.success ? '' : r.error.issues[0]?.message).toBe('DECIMAL_INVALIDO');
  });
});

describe('pedido de comando (8.2.1; ENG-021)', () => {
  it('aceita o pedido mínimo e os opcionais válidos', () => {
    expect(EsquemaPedidoComando.safeParse(pedido).success).toBe(true);
    const completo = { ...pedido, confirmedAt: '2026-09-27T10:00:00-03:00', deviceId: 'aparelho-1' };
    expect(EsquemaPedidoComando.safeParse(completo).success).toBe(true);
  });

  it('organização, ator ou iniciador no corpo são recusa de contrato: vêm da sessão', () => {
    for (const extra of [{ organizationId: UUID }, { actorId: UUID }, { initiatorKind: 'web' }]) {
      expect(EsquemaPedidoComando.safeParse({ ...pedido, ...extra }).success).toBe(false);
    }
  });

  it('recusa chave vazia ou longa, UUID fora do canônico, versão negativa ou decimal e instante sem fuso', () => {
    for (const p of [
      { ...pedido, idempotencyKey: '  ' },
      { ...pedido, idempotencyKey: 'x'.repeat(129) },
      { ...pedido, target: { ...pedido.target, id: UUID.toUpperCase() } },
      { ...pedido, target: { ...pedido.target, expectedVersion: -1 } },
      { ...pedido, target: { ...pedido.target, expectedVersion: 1.5 } },
      { ...pedido, confirmedAt: '2026-09-27T10:00:00' },
      // Formatos que o PostgreSQL recusaria no INSERT (ENV-CAD01-NUL-CL22).
      { ...pedido, confirmedAt: '0000-01-01T00:00:00Z' },
      { ...pedido, confirmedAt: '2026-02-30T10:00:00Z' },
      { ...pedido, confirmedAt: '2026-09-27T10:00:00Z\u0000' },
      { ...pedido, confirmedAt: '2026-09-27T10:00:00+16:00' },
      { ...pedido, confirmedAt: '2026-09-27T10:00:00-23:59' },
      { ...pedido, confirmedAt: '2026-09-27T10:00:00.1234567891Z' },
    ]) {
      expect(EsquemaPedidoComando.safeParse(p).success).toBe(false);
    }
  });

  it('recusa U+0000 em todo texto do envelope que vai ao banco; chave de texto livre sem NUL continua aceita', () => {
    for (const p of [
      { ...pedido, idempotencyKey: 'chave\u0000x' },
      { ...pedido, idempotencyKey: '\u0000' },
      { ...pedido, target: { ...pedido.target, type: 'lot\u0000' } },
      { ...pedido, deviceId: 'aparelho\u0000' },
    ]) {
      const r = EsquemaPedidoComando.safeParse(p);
      expect(r.success).toBe(false);
      expect(r.success ? [] : r.error.issues.map((i) => i.message)).toContain('NUL');
    }
    // O ano 0001 é o primeiro que o banco aceita; o 0000 é recusado com o motivo.
    expect(EsquemaInstanteConfirmado.safeParse('0001-01-01T00:00:00Z').success).toBe(true);
    const anoZero = EsquemaInstanteConfirmado.safeParse('0000-06-01T00:00:00-03:00');
    expect(anoZero.success ? [] : anoZero.error.issues.map((i) => i.message)).toContain('ano_zero');
    // Deslocamento até ±15:59, o limite do PostgreSQL.
    for (const v of [
      '2026-09-27T10:00:00+15:59',
      '2026-09-27T10:00:00-15:59',
      '0001-01-01T00:00:00+03:00',
      '2026-09-27T10:00:00.123456789Z',
    ])
      expect(EsquemaInstanteConfirmado.safeParse(v).success, v).toBe(true);
    const fuso16 = EsquemaInstanteConfirmado.safeParse('2026-09-27T10:00:00+16:00');
    expect(fuso16.success ? [] : fuso16.error.issues.map((i) => i.message)).toContain('fuso_fora_da_faixa');
    // A chave não precisa ser UUID: o contrato aceita texto (até 128), com acento, espaço e barra.
    expect(EsquemaPedidoComando.safeParse({ ...pedido, idempotencyKey: 'pedido 42/ação' }).success).toBe(
      true,
    );
  });

  it('dados do movimento: tipo discriminado, quantidade como objeto e situações do domínio', () => {
    const entrada = {
      lote: UUID,
      local: UUID,
      movimento: { tipo: 'entrada', quantidade: { valor: '10', unidade: 'L' }, situacao: 'quarentena_livre' },
    };
    expect(EsquemaDadosMovimento.safeParse(entrada).success).toBe(true);
    expect(
      EsquemaDadosMovimento.safeParse({ ...entrada, movimento: { tipo: 'estorno', estornaId: UUID } })
        .success,
    ).toBe(true);
    for (const m of [
      { ...entrada.movimento, quantidade: 10 },
      { ...entrada.movimento, situacao: 'vencido' },
      { tipo: 'saida', quantidade: { valor: '1', unidade: 'L' } },
    ]) {
      expect(EsquemaDadosMovimento.safeParse({ ...entrada, movimento: m }).success).toBe(false);
    }
  });
});

describe('recibo e erro (IDEM-17; ENG-015)', () => {
  const recibo = {
    receiptId: UUID,
    commandType: 'CMD-43',
    idempotencyKey: 'k',
    outcome: 'confirmed',
    reasonCode: null,
    targetType: 'lot',
    targetId: UUID,
    expectedVersion: 0,
    resultingVersion: 1,
    effects: { movements: [UUID] },
    pending: [],
    nextAction: null,
    processedAt: '2026-09-27T13:00:00.000Z',
    alreadyReceived: false,
  };

  it('recibo segue o esquema; status por resultado registrado', () => {
    expect(EsquemaRecibo.safeParse(recibo).success).toBe(true);
    expect(EsquemaRecibo.safeParse({ ...recibo, extra: 1 }).success).toBe(false);
    expect([
      statusDoRecibo('confirmed'),
      statusDoRecibo('version_conflict'),
      statusDoRecibo('rejected'),
    ]).toEqual([200, 409, 422]);
  });

  it('todo código de erro tem classe e status, e o corpo segue o esquema', () => {
    for (const codigo of Object.keys(ERROS) as (keyof typeof ERROS)[]) {
      const r = erroContrato(codigo, 'mensagem', 'corr-1');
      expect(EsquemaErro.safeParse(r.corpo).success, codigo).toBe(true);
      expect(r.status).toBe(ERROS[codigo].status);
    }
  });

  it('erro de validação aponta caminho e problema sem ecoar o valor recebido', () => {
    const segredo = 'senha-super-secreta-123';
    const r = EsquemaPedidoComando.safeParse({ ...pedido, idempotencyKey: 5, deviceId: segredo.repeat(10) });
    expect(r.success).toBe(false);
    const resposta = erroDeValidacao(r.error as z.ZodError, 'corr-2');
    expect(resposta.status).toBe(400);
    expect(resposta.corpo.campos?.map((c) => c.caminho).sort()).toEqual(['deviceId', 'idempotencyKey']);
    expect(JSON.stringify(resposta)).not.toContain(segredo);
    const raiz = erroDeValidacao(new z.ZodError([{ code: 'custom', path: [], message: 'x', input: 1 }]), 'c');
    expect(raiz.corpo.campos).toEqual([{ caminho: '(raiz)', problema: 'x' }]);
  });
});

describe('registrador (ENG-081)', () => {
  const coletar = () => {
    const linhas: string[] = [];
    const reg = criarRegistrador({
      servico: 'api',
      versao: '0.0.0',
      escrever: (l) => linhas.push(l),
      agora: () => '2026-09-27T13:00:00.000Z',
    });
    return { linhas, reg };
  };

  it('escreve uma linha JSON com correlação, serviço, versão, nível e evento', () => {
    const { linhas, reg } = coletar();
    reg.registrar('info', 'comando.processado', 'corr-3', { outcome: 'confirmed' });
    reg.registrar('aviso', 'sem.campos', 'corr-4');
    expect(JSON.parse(linhas[0] ?? '')).toEqual({
      outcome: 'confirmed',
      ts: '2026-09-27T13:00:00.000Z',
      nivel: 'info',
      evento: 'comando.processado',
      correlation_id: 'corr-3',
      servico: 'api',
      versao: '0.0.0',
    });
    expect(JSON.parse(linhas[1] ?? '')).toMatchObject({ evento: 'sem.campos', correlation_id: 'corr-4' });
  });

  it('mascara chaves sensíveis em qualquer profundidade e não deixa campo sobrescrever a correlação', () => {
    const { linhas, reg } = coletar();
    reg.registrar('erro', 'x', 'corr-5', {
      password: 'p1',
      cabecalhos: { Authorization: 'Bearer t', Cookie: 'valor-do-cookie' },
      lista: [{ api_key: 'valor-da-chave', email: 'a@b.c' }],
      correlation_id: 'forjada',
      profundo: { a: { b: { c: { d: { e: { f: { g: { h: { i: { j: 1 } } } } } } } } } },
    });
    const linha = linhas[0] ?? '';
    for (const segredo of ['p1', 'Bearer t', 'valor-do-cookie', 'valor-da-chave', 'a@b.c', 'forjada'])
      expect(linha).not.toContain(segredo);
    expect(JSON.parse(linha)).toMatchObject({ correlation_id: 'corr-5' });
    expect(linha).toContain('[profundo]');
  });

  it('recusa log sem correlação', () => {
    const { reg } = coletar();
    expect(() => {
      reg.registrar('info', 'x', '  ');
    }).toThrow(/correlation_id/);
  });
});

describe('falha permanente sem gravação (ENV-CAD01-NUL-CL22)', () => {
  it('só FALHA_INTERNA com o detalhe exato; qualquer outra forma continua incerta', () => {
    const sinal = { resultadoIncerto: false, repetirMesmoConteudo: false };
    expect(
      falhaPermanenteSemGravacao(erroContrato('FALHA_INTERNA', 'm', 'c', { detalhe: sinal }).corpo),
    ).toBe(true);
    for (const corpo of [
      erroContrato('FALHA_INTERNA', 'm', 'c').corpo,
      erroContrato('FALHA_INTERNA', 'm', 'c', { detalhe: { resultadoIncerto: false } }).corpo,
      erroContrato('FALHA_INTERNA', 'm', 'c', { detalhe: { ...sinal, resultadoIncerto: true } }).corpo,
      erroContrato('FALHA_INTERNA', 'm', 'c', { detalhe: { ...sinal, extra: 1 } }).corpo,
      erroContrato('FALHA_TRANSITORIA', 'm', 'c', { detalhe: sinal }).corpo,
    ]) {
      expect(falhaPermanenteSemGravacao(corpo), JSON.stringify(corpo.detalhe)).toBe(false);
    }
  });
});
