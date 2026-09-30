import { COMANDOS_CADASTRO, erroContrato, type ReciboContrato } from '@safrion/contracts';
import { describe, expect, it } from 'vitest';

import {
  desfechoDaConsulta,
  desfechoDoEnvio,
  intencaoValida,
  novaIntencao,
  reciboDaIntencao,
} from '../src/cadastros/intencao';

const ID = '00000000-0000-4000-8000-000000000001';
const OUTRO_ID = '00000000-0000-4000-8000-000000000002';
const intencao = novaIntencao(COMANDOS_CADASTRO.editarTalhao, 'field', ID, 7, { nome: 'T1' }, 'chave-1');
const recibo = (extra: Partial<ReciboContrato> = {}): ReciboContrato => ({
  receiptId: OUTRO_ID,
  commandType: intencao.commandType,
  idempotencyKey: intencao.chave,
  outcome: 'confirmed',
  reasonCode: null,
  targetType: 'field',
  targetId: ID,
  expectedVersion: 7,
  resultingVersion: 8,
  effects: {},
  pending: [],
  nextAction: null,
  processedAt: '2026-09-30T20:00:00Z',
  alreadyReceived: false,
  ...extra,
});

describe('intenção de cadastro imutável e recuperável', () => {
  it('serializa a fotografia do pedido, sem organização/ator no envelope', () => {
    const dados = { nome: 'Fazenda 1', fuso: 'America/Sao_Paulo' };
    const i = novaIntencao(COMANDOS_CADASTRO.criarFazenda, 'farm', ID, 0, dados, 'chave-2');
    dados.nome = 'Alterado depois';
    expect(JSON.parse(i.corpo)).toEqual({
      idempotencyKey: 'chave-2',
      target: { type: 'farm', id: ID, expectedVersion: 0 },
      data: { nome: 'Fazenda 1', fuso: 'America/Sao_Paulo' },
    });
    expect(Object.isFrozen(i)).toBe(true);
    expect(intencaoValida(i)).toBe(true);
  });

  it('aceita os cinco comandos com seu alvo e versão, e recusa alvo/versão trocados', () => {
    for (const [comando, alvo, versao] of [
      [COMANDOS_CADASTRO.criarFazenda, 'farm', 0],
      [COMANDOS_CADASTRO.editarFazenda, 'farm', 1],
      [COMANDOS_CADASTRO.criarTalhao, 'field', 0],
      [COMANDOS_CADASTRO.editarTalhao, 'field', 1],
      [COMANDOS_CADASTRO.alterarSituacaoTalhao, 'field', 1],
    ] as const) {
      expect(intencaoValida(novaIntencao(comando, alvo, ID, versao, {}, 'chave'))).toBe(true);
      expect(() =>
        novaIntencao(comando, alvo === 'farm' ? 'field' : 'farm', ID, versao, {}, 'chave'),
      ).toThrow();
      expect(() => novaIntencao(comando, alvo, ID, versao === 0 ? 1 : 0, {}, 'chave')).toThrow();
    }
    expect(() => novaIntencao(COMANDOS_CADASTRO.editarTalhao, 'field', ID, -1, {}, 'chave')).toThrow();
    expect(() => novaIntencao(COMANDOS_CADASTRO.editarTalhao, 'field', 'inválido', 1, {}, 'chave')).toThrow();
  });

  it('não restaura metadados diferentes do corpo, outro comando ou envelope corrompido', () => {
    for (const alteracao of [
      { chave: 'outra' },
      { targetId: OUTRO_ID },
      { expectedVersion: 8 },
      { targetType: 'farm' },
      { commandType: 'estoque.receber-documento' },
      { commandType: 'toString' },
      { corpo: '{' },
      { corpo: JSON.stringify({ ...JSON.parse(intencao.corpo), organizationId: OUTRO_ID }) },
      { corpo: JSON.stringify({ idempotencyKey: 'chave-1' }) },
      { corpo: JSON.stringify({ data: 'ç'.repeat(16384) }) },
    ])
      expect(intencaoValida({ ...intencao, ...alteracao })).toBe(false);
    expect(intencaoValida(null)).toBe(false);
  });
});

describe('a resposta só resolve a intenção que ela prova', () => {
  it('conserva conflito/rejeição e suas informações para o formulário manter os campos', () => {
    for (const [status, r] of [
      [200, recibo({ alreadyReceived: true })],
      [409, recibo({ outcome: 'version_conflict', resultingVersion: 9, reasonCode: 'VERSION_CONFLICT' })],
      [422, recibo({ outcome: 'rejected', reasonCode: 'NOME_EM_USO', nextAction: 'Escolha outro nome.' })],
    ] as const) {
      expect(desfechoDoEnvio(status, r, intencao, false)).toEqual({ tipo: 'resolvido', recibo: r });
      expect(desfechoDoEnvio(status, r, intencao, true)).toEqual({ tipo: 'resolvido', recibo: r });
      expect(desfechoDaConsulta(status, r, intencao)).toEqual({ tipo: 'resolvido', recibo: r });
    }
  });

  it('recibo alheio por comando, chave, alvo ou versão, e corpo incompleto, ficam incertos', () => {
    for (const corpo of [
      recibo({ commandType: COMANDOS_CADASTRO.criarTalhao }),
      recibo({ idempotencyKey: 'outra' }),
      recibo({ targetType: 'farm' }),
      recibo({ targetId: OUTRO_ID }),
      recibo({ expectedVersion: 8 }),
      recibo({ expectedVersion: null }),
      { outcome: 'confirmed' },
      null,
    ]) {
      expect(reciboDaIntencao(corpo, intencao)).toBeNull();
      expect(desfechoDoEnvio(200, corpo, intencao, false).tipo).toBe('incerto');
      expect(desfechoDaConsulta(200, corpo, intencao).tipo).toBe('incerto');
    }
  });

  it('não confia em recibo cujo status contradiz o resultado', () => {
    expect(desfechoDoEnvio(200, recibo({ outcome: 'version_conflict' }), intencao, false).tipo).toBe(
      'incerto',
    );
    expect(desfechoDaConsulta(422, recibo(), intencao).tipo).toBe('incerto');
    expect(desfechoDoEnvio(400, recibo(), intencao, false).tipo).toBe('incerto');
  });

  it('recusa certa do primeiro envio permite corrigir, mas a mesma resposta no reenvio não resolve envio anterior', () => {
    for (const codigo of [
      'CONTRATO_INVALIDO',
      'NAO_AUTENTICADO',
      'ORGANIZACAO_INVALIDA',
      'SEM_PERMISSAO',
      'CORPO_EXCEDE_LIMITE',
      'TIPO_DE_CONTEUDO_INVALIDO',
      'IDEMPOTENCY_KEY_REUSED',
    ] as const) {
      const e = erroContrato(codigo, 'Mensagem sintética.', 'c1');
      expect(desfechoDoEnvio(e.status, e.corpo, intencao, false).tipo).toBe('nao_gravado');
      expect(desfechoDoEnvio(e.status, e.corpo, intencao, true).tipo).toBe('incerto');
    }
    const e = erroContrato('NAO_AUTENTICADO', 'Entre novamente.', 'c2');
    expect(desfechoDoEnvio(401, e.corpo, intencao, true)).toMatchObject({ tipo: 'incerto', sessao: true });
  });

  it('403 no reenvio ou consulta informa a falta de permissão sem resolver o efeito anterior (Gemini)', () => {
    const e = erroContrato('SEM_PERMISSAO', 'Papel sem acesso.', 'gemini-403');
    const esperado = {
      tipo: 'incerto',
      mensagem:
        'Seu papel não permite conferir ou reenviar este cadastro. O envio anterior continua sem confirmação. Solicite acesso ao gerente.',
      sessao: false,
      naoLocalizado: false,
    };
    expect(desfechoDoEnvio(403, e.corpo, intencao, true)).toEqual(esperado);
    expect(desfechoDaConsulta(403, e.corpo, intencao)).toEqual(esperado);
    expect(desfechoDoEnvio(403, e.corpo, intencao, false)).toMatchObject({ tipo: 'nao_gravado' });
    expect(desfechoDoEnvio(403, { ...e.corpo, classe: 'validacao' }, intencao, true)).not.toEqual(esperado);
    expect(desfechoDaConsulta(500, e.corpo, intencao)).not.toEqual(esperado);
    expect(desfechoDaConsulta(403, null, intencao)).toMatchObject({ tipo: 'incerto', naoLocalizado: false });
  });

  it('503 transitório, intenção em processamento e respostas inesperadas nunca liberam nova chave', () => {
    for (const codigo of ['FALHA_TRANSITORIA', 'FALHA_INTERNA', 'IDEMPOTENCY_IN_PROGRESS'] as const) {
      const e = erroContrato(codigo, 'Tente consultar.', 'c3', { detalhe: { repetirEmMs: 3000 } });
      expect(desfechoDoEnvio(e.status, e.corpo, intencao, false)).toMatchObject({
        tipo: 'incerto',
        naoLocalizado: false,
      });
    }
    const e = erroContrato('IDEMPOTENCY_KEY_REUSED', 'x', 'c4');
    for (const [status, corpo] of [
      [0, null],
      [400, null],
      [200, e.corpo],
      [409, { ...e.corpo, classe: 'acesso' }],
    ] as const)
      expect(desfechoDoEnvio(status, corpo, intencao, false).tipo).toBe('incerto');
  });

  it('só o 404 específico da consulta habilita reenviar exatamente o mesmo pedido', () => {
    const e = erroContrato('RECIBO_NAO_LOCALIZADO', 'Ainda não localizado.', 'c5');
    expect(desfechoDaConsulta(e.status, e.corpo, intencao)).toMatchObject({
      tipo: 'incerto',
      naoLocalizado: true,
    });
    expect(desfechoDoEnvio(e.status, e.corpo, intencao, false)).toMatchObject({
      tipo: 'incerto',
      naoLocalizado: false,
    });
    for (const codigo of [
      'NAO_ENCONTRADO',
      'NAO_AUTENTICADO',
      'SEM_PERMISSAO',
      'FALHA_TRANSITORIA',
    ] as const) {
      const falha = erroContrato(codigo, 'x', 'c6');
      expect(desfechoDaConsulta(falha.status, falha.corpo, intencao)).toMatchObject({
        tipo: 'incerto',
        naoLocalizado: false,
      });
    }
    expect(desfechoDaConsulta(404, null, intencao)).toMatchObject({ tipo: 'incerto', naoLocalizado: false });
    expect(desfechoDaConsulta(401, null, intencao)).toMatchObject({ tipo: 'incerto', sessao: true });
  });
});
