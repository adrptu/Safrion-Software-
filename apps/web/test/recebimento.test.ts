import type { DocumentoDetalhe, DocumentoResumo } from '@safrion/db/web';
import { describe, expect, it } from 'vitest';

import {
  desfechoDaConsulta,
  desfechoDoEnvio,
  linhaVazia,
  novaIntencao,
  parcelaDoCampo,
  recebimentoVazio,
  regraDaValidade,
  situacaoDaLinha,
  validarRecebimento,
  type CamposLinha,
  type CamposRecebimento,
  type Intencao,
  type Opcoes,
  type ProdutoOpcao,
} from '../src/recebimento/formulario';
import {
  estadoDoDocumento,
  formatarIdentificacao,
  linhaDaOcorrencia,
  linhaDoDocumento,
  pendenciasDoDocumento,
  rotuloDoDocumento,
  textoDaConferencia,
} from '../src/recebimento/lista';
import {
  apagarGuardado,
  apagarIntencao,
  chaveDoRecebimento,
  gravarIntencao,
  gravarRecebimento,
  guardarFormulario,
  lerGuardados,
  lerIntencoes,
  lerRecebimento,
  prefixoDosGuardados,
  prefixoDasIntencoes,
  temConteudo,
} from '../src/recebimento/rascunho';

// Formulário de recebimento (contrato CMD-15 v3.7, §6.2 e §7.1): validação da tela, corpo do comando, a regra da
// incerteza nas respostas do POST e do GET, o rascunho por usuário e organização e o que a lista e o detalhe mostram.
const U = {
  emitente: '11111111-1111-4111-8111-111111111111',
  fazenda: '22222222-2222-4222-8222-222222222222',
  local: '33333333-3333-4333-8333-333333333333',
  fungicida: '44444444-4444-4444-8444-444444444444',
  galao: '55555555-5555-4555-8555-555555555555',
  diesel: '66666666-6666-4666-8666-666666666666',
  semente: '77777777-7777-4777-8777-777777777777',
  pessoa: '88888888-8888-4888-8888-888888888888',
  doc: '99999999-9999-4999-8999-999999999999',
  chave: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
  recibo: 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
};
const fungicida: ProdutoOpcao = {
  id: U.fungicida,
  nome: 'Fungicida A',
  unidade: 'L',
  validade: 'controla',
  lote: 'informado',
  embalagens: [{ id: U.galao, nome: 'galão 5 L', fator: '5', versao: 2 }],
  lotes: [{ codigo: 'F26-02', validade: '2027-06-30' }],
};
const opcoes: Opcoes = {
  emitentes: [{ id: U.emitente, nome: 'Fornecedor Teste Ltda', identificacao: '11222333000181' }],
  fazendas: [
    { id: U.fazenda, nome: 'Fazenda Demonstração', locais: [{ id: U.local, nome: 'Almoxarifado central' }] },
  ],
  produtos: [
    fungicida,
    {
      id: U.diesel,
      nome: 'Diesel S10',
      unidade: 'L',
      validade: 'nao_se_aplica',
      lote: 'por_documento',
      embalagens: [],
      lotes: [],
    },
    {
      id: U.semente,
      nome: 'Semente',
      unidade: 'un',
      validade: 'controla',
      lote: 'informado',
      embalagens: [],
      lotes: [],
    },
  ],
  responsaveis: [{ id: U.pessoa, nome: 'Almoxarife (fictício)' }],
};

const linha = (id: string, extra: Partial<CamposLinha> = {}): CamposLinha => ({
  ...linhaVazia(id, { local: U.local }),
  produto: U.fungicida,
  lote: 'F26-03',
  validade: '30/06/2027',
  unidade: 'L',
  documento: '10',
  apto: '10',
  ...extra,
});
const formulario = (linhas: CamposLinha[], extra: Partial<CamposRecebimento> = {}): CamposRecebimento => ({
  ...recebimentoVazio(opcoes, '2026-09-30', 'l1'),
  numero: '7001',
  serie: '1',
  emissao: '29/09/2026',
  linhas,
  ...extra,
});

describe('formulário: contexto, validação e corpo', () => {
  it('documento novo traz só o contexto: emitente, fazenda e local únicos, recebido hoje; nada de quantidade ou lote', () => {
    const v = recebimentoVazio(opcoes, '2026-09-30', 'l1');
    expect(v).toMatchObject({
      emitente: U.emitente,
      fazenda: U.fazenda,
      recebimento: '30/09/2026',
      tipo: 'nfe',
    });
    expect(v.linhas).toEqual([linhaVazia('l1', { local: U.local })]);
    expect(v.linhas[0]).toMatchObject({ produto: '', lote: '', validade: '', documento: '', apto: '' });
  });

  it('NF-TESTE-002: 2 galões, 1 apto e 1 bloqueado por avaria, mais diesel a granel; decimais pt-BR viram texto', () => {
    const r = validarRecebimento(
      formulario([
        linha('a', {
          unidade: `emb:${U.galao}`,
          documento: '2',
          apto: '1',
          bloqueado: '1',
          motivo: 'avaria',
        }),
        linha('b', { produto: U.diesel, lote: '', validade: '', documento: '1.234,5', apto: '1.234,5' }),
      ]),
      opcoes,
    );
    expect(r.ok).toBe(true);
    if (!r.ok) return;
    expect(r.dados).toEqual({
      emitente: U.emitente,
      tipo: 'nfe',
      serie: '1',
      numero: '7001',
      emissao: '2026-09-29',
      recebimento: '2026-09-30',
      fazenda: U.fazenda,
      linhas: [
        {
          numero: 1,
          produto: U.fungicida,
          lote: { codigo: 'F26-03' },
          validade: '2027-06-30',
          local: U.local,
          unidade: { tipo: 'embalagem', conversao: U.galao, versao: 2 },
          documento: '2',
          parcelas: { apto: '1', quarentena: '0', bloqueado: '1', recusado: '0' },
          motivo: 'avaria',
        },
        {
          numero: 2,
          produto: U.diesel,
          lote: { interno: true },
          validade: null,
          local: U.local,
          unidade: { tipo: 'medida', unidade: 'L' },
          documento: '1234.5',
          parcelas: { apto: '1234.5', quarentena: '0', bloqueado: '0', recusado: '0' },
        },
      ],
    });
  });

  it('erros junto ao campo e à linha: origem, produto, lote, validade e quantidade', () => {
    const r = validarRecebimento(
      formulario([linhaVazia('x', { local: U.local })], { numero: '', emissao: '31/02/2026' }),
      opcoes,
    );
    expect(r.ok).toBe(false);
    if (r.ok) return;
    expect(r.erros.origem).toMatchObject({
      numero: 'Informe o número do documento.',
      emissao: 'Informe a emissão como dd/mm/aaaa.',
    });
    expect(r.erros.linhas['x']).toMatchObject({
      produto: 'Escolha o produto.',
      documento: 'Informe a quantidade.',
    });
    const semLote = validarRecebimento(formulario([linha('y', { lote: ' ', validade: '' })]), opcoes);
    expect(semLote.ok ? null : semLote.erros.linhas['y']).toMatchObject({
      lote: 'Informe o lote do fabricante.',
      validade: 'Informe a validade como dd/mm/aaaa.',
    });
  });

  it('divergência exige motivo coerente; "outro" exige texto; conferir nada é falta', () => {
    const erroDe = (l: CamposLinha) => {
      const r = validarRecebimento(formulario([l]), opcoes);
      return r.ok ? {} : (r.erros.linhas[l.id] ?? {});
    };
    expect(erroDe(linha('a', { apto: '8' }))).toEqual({ motivo: 'Escolha o motivo da divergência.' });
    expect(erroDe(linha('a', { apto: '8', motivo: 'sobra' }))).toEqual({
      motivo: '"Sobra" só quando o conferido é maior que o documento.',
    });
    expect(erroDe(linha('a', { apto: '12', motivo: 'falta' }))).toEqual({
      motivo: '"Falta" só quando o conferido é menor que o documento.',
    });
    expect(erroDe(linha('a', { apto: '8', recusado: '2', motivo: 'outro' }))).toEqual({
      motivoTexto: 'Descreva o motivo.',
    });
    expect(erroDe(linha('a', { apto: '', motivo: 'falta' }))).toEqual({});
    // Sem divergência, motivo esquecido na tela não vai ao servidor.
    const r = validarRecebimento(formulario([linha('a', { motivo: 'avaria' })]), opcoes);
    expect(r.ok ? r.dados.linhas[0]?.motivo : 'erro').toBeUndefined();
  });

  it('quarentena exige quem decide e prazo; produto diferente exige a ocorrência, e retido exige prazo', () => {
    const r1 = validarRecebimento(formulario([linha('a', { apto: '8', quarentena: '2' })]), opcoes);
    expect(r1.ok ? null : r1.erros.linhas['a']).toEqual({
      inspecaoResponsavel: 'Escolha quem decide a inspeção.',
      inspecaoPrazo: 'Informe o prazo como dd/mm/aaaa.',
    });
    const r2 = validarRecebimento(
      formulario([
        linha('a', {
          apto: '',
          motivo: 'produto_diferente',
          ocorrenciaQuantidade: '1',
          ocorrenciaUnidade: 'tambor 200 L',
          ocorrenciaDestino: 'retido_para_decisao',
          ocorrenciaResponsavel: U.pessoa,
        }),
      ]),
      opcoes,
    );
    expect(r2.ok ? null : r2.erros.linhas['a']).toEqual({
      ocorrenciaDescricao: 'Escolha o produto que chegou ou descreva.',
      ocorrenciaPrazo: 'Retido para decisão precisa de prazo.',
    });
    const r3 = validarRecebimento(
      formulario([
        linha('a', {
          apto: '',
          motivo: 'produto_diferente',
          ocorrenciaDescricao: 'Fungicida B, tambor',
          ocorrenciaQuantidade: '1',
          ocorrenciaUnidade: 'tambor 200 L',
          ocorrenciaDestino: 'devolvido_na_entrega',
          ocorrenciaResponsavel: U.pessoa,
        }),
      ]),
      opcoes,
    );
    expect(r3.ok && r3.dados.linhas[0]?.ocorrencia).toEqual({
      produtoReal: { descricao: 'Fungicida B, tambor' },
      quantidade: '1',
      unidade: 'tambor 200 L',
      destino: 'devolvido_na_entrega',
      responsavel: U.pessoa,
    });
  });

  it('lote existente manda na validade, mesmo com a política do produto mudada; lote novo segue a política', () => {
    expect(regraDaValidade(fungicida, 'F26-02')).toEqual({ tipo: 'do_lote', validade: '2027-06-30' });
    expect(regraDaValidade(fungicida, 'NOVO')).toEqual({ tipo: 'informar' });
    const mudou: ProdutoOpcao = { ...fungicida, validade: 'nao_se_aplica' };
    expect(regraDaValidade(mudou, 'F26-02')).toEqual({ tipo: 'do_lote', validade: '2027-06-30' });
    expect(regraDaValidade(mudou, 'NOVO')).toEqual({ tipo: 'nao_se_aplica' });
    const semData: ProdutoOpcao = { ...fungicida, lotes: [{ codigo: 'VELHO', validade: null }] };
    expect(regraDaValidade(semData, 'VELHO')).toEqual({ tipo: 'do_lote', validade: null });
    // A data do lote vai no corpo, sem pedir e sem inventar, mesmo que o campo tenha outra coisa digitada.
    const r = validarRecebimento(formulario([linha('a', { lote: 'F26-02', validade: '01/01/2030' })]), {
      ...opcoes,
      produtos: [mudou],
    });
    expect(r.ok && r.dados.linhas[0]?.validade).toBe('2027-06-30');
  });

  it('item indivisível: unidade de contagem e embalagem só aceitam inteiros', () => {
    const r1 = validarRecebimento(
      formulario([linha('a', { produto: U.semente, unidade: 'un', documento: '1,5', apto: '1,5' })]),
      opcoes,
    );
    expect(r1.ok ? null : r1.erros.linhas['a']).toMatchObject({
      documento: 'Esta unidade conta itens inteiros.',
    });
    const r2 = validarRecebimento(
      formulario([linha('a', { unidade: `emb:${U.galao}`, documento: '2', apto: '1,5', recusado: '0,5' })]),
      opcoes,
    );
    expect(r2.ok ? null : r2.erros.linhas['a']).toMatchObject({ apto: 'Esta unidade conta itens inteiros.' });
  });

  it('parcela: vazio é zero, zero vale, negativo e ponto ambíguo não', () => {
    expect(parcelaDoCampo('')).toEqual({ ok: true, valor: '0' });
    expect(parcelaDoCampo('0,00')).toEqual({ ok: true, valor: '0' });
    expect(parcelaDoCampo('2,5')).toEqual({ ok: true, valor: '2.5' });
    expect(parcelaDoCampo('-1').ok).toBe(false);
    expect(parcelaDoCampo('1.5').ok).toBe(false);
    expect(situacaoDaLinha(linha('a', { apto: '8', quarentena: '2' }))).toEqual({
      divergente: false,
      inspecao: true,
      conferido: '10.000000',
      comparacao: 0,
    });
    expect(situacaoDaLinha(linha('a', { bloqueado: '1', apto: '9' })).divergente).toBe(true);
  });

  it('intenção imutável: chave, documento e corpo exatos do comando', () => {
    const r = validarRecebimento(formulario([linha('a')]), opcoes);
    if (!r.ok) throw new Error('esperava válido');
    const i = novaIntencao(r.dados, U.chave, U.doc);
    expect(JSON.parse(i.corpo)).toEqual({
      idempotencyKey: U.chave,
      target: { type: 'receipt_document', id: U.doc, expectedVersion: 0 },
      data: r.dados,
    });
  });
});

describe('incerteza: só recibo terminal correspondente resolve (contrato CMD-15 §6.2)', () => {
  const intencao: Intencao = { chave: U.chave, documentoId: U.doc, corpo: '{}' };
  const recibo = (extra: Record<string, unknown> = {}) => ({
    receiptId: U.recibo,
    commandType: 'estoque.receber-documento',
    idempotencyKey: U.chave,
    outcome: 'confirmed',
    reasonCode: null,
    targetType: 'receipt_document',
    targetId: U.doc,
    expectedVersion: 0,
    resultingVersion: 1,
    effects: {},
    pending: [],
    nextAction: 'Receber documento',
    processedAt: '2026-09-30T12:00:00.000Z',
    alreadyReceived: false,
    ...extra,
  });
  const erro = (codigo: string) => ({ codigo, classe: 'acesso', mensagem: 'x', correlationId: 'c' });

  it('POST: recibo correspondente resolve (confirmado, rejeitado ou conflito); de outra intenção, não', () => {
    expect(desfechoDoEnvio(200, recibo(), intencao, false).tipo).toBe('resolvido');
    expect(
      desfechoDoEnvio(
        422,
        recibo({ outcome: 'rejected', reasonCode: 'DOCUMENTO_JA_RECEBIDO' }),
        intencao,
        true,
      ).tipo,
    ).toBe('resolvido');
    for (const outro of [
      { idempotencyKey: 'outra' },
      { targetId: U.recibo },
      { commandType: 'estoque.registrar-entrada' },
    ]) {
      expect(desfechoDoEnvio(200, recibo(outro), intencao, false).tipo).toBe('incerto');
    }
    expect(desfechoDoEnvio(200, { outcome: 'confirmed' }, intencao, false).tipo).toBe('incerto');
  });

  it('POST: no primeiro envio, 400/401/403/413/415 e chave reutilizada são certezas; no reenvio, não', () => {
    for (const [status, corpo] of [
      [400, erro('CONTRATO_INVALIDO')],
      [401, erro('NAO_AUTENTICADO')],
      [403, erro('SEM_PERMISSAO')],
      [413, erro('CORPO_EXCEDE_LIMITE')],
      [415, erro('TIPO_DE_CONTEUDO_INVALIDO')],
      [409, erro('IDEMPOTENCY_KEY_REUSED')],
    ] as const) {
      expect(desfechoDoEnvio(status, corpo, intencao, false).tipo, String(status)).toBe('nao_gravado');
      expect(desfechoDoEnvio(status, corpo, intencao, true).tipo, `reenvio ${String(status)}`).toBe(
        'incerto',
      );
    }
    expect(desfechoDoEnvio(401, erro('NAO_AUTENTICADO'), intencao, true)).toMatchObject({
      tipo: 'incerto',
      sessao: true,
    });
    expect(desfechoDoEnvio(409, erro('IDEMPOTENCY_IN_PROGRESS'), intencao, false).tipo).toBe('incerto');
    expect(desfechoDoEnvio(503, erro('FALHA_TRANSITORIA'), intencao, false).tipo).toBe('incerto');
    expect(desfechoDoEnvio(500, null, intencao, false).tipo).toBe('incerto');
  });

  it('GET: recibo correspondente resolve; "ainda não localizado" libera reenviar o mesmo; nenhuma falha encerra', () => {
    expect(desfechoDaConsulta(200, recibo({ alreadyReceived: true }), intencao).tipo).toBe('resolvido');
    expect(desfechoDaConsulta(409, recibo({ outcome: 'version_conflict' }), intencao).tipo).toBe('resolvido');
    expect(desfechoDaConsulta(404, erro('RECIBO_NAO_LOCALIZADO'), intencao)).toMatchObject({
      tipo: 'incerto',
      naoLocalizado: true,
    });
    for (const [status, corpo] of [
      [400, erro('CONTRATO_INVALIDO')],
      [401, erro('NAO_AUTENTICADO')],
      [403, erro('SEM_PERMISSAO')],
      [404, erro('NAO_ENCONTRADO')],
      [503, erro('FALHA_TRANSITORIA')],
      [0, null],
    ] as const) {
      expect(desfechoDaConsulta(status, corpo, intencao), String(status)).toMatchObject({
        tipo: 'incerto',
        naoLocalizado: false,
      });
    }
    expect(desfechoDaConsulta(401, erro('NAO_AUTENTICADO'), intencao)).toMatchObject({ sessao: true });
    expect(desfechoDaConsulta(200, recibo({ targetId: U.recibo }), intencao).tipo).toBe('incerto');
  });
});

describe('rascunho e intenções no localStorage por usuário e organização (CX-UI01)', () => {
  function memoria(falhaAoGravar = false) {
    const dados = new Map<string, string>();
    return {
      dados,
      get length() {
        return dados.size;
      },
      key: (n: number) => [...dados.keys()][n] ?? null,
      getItem: (k: string) => dados.get(k) ?? null,
      setItem: (k: string, v: string) => {
        if (falhaAoGravar) throw new DOMException('cheio', 'QuotaExceededError');
        dados.set(k, v);
      },
      removeItem: (k: string) => {
        dados.delete(k);
      },
    };
  }
  const campos = formulario([linha('a')]);
  const intencao = (chave: string): Intencao => ({ chave, documentoId: U.doc, corpo: '{"x":1}' });
  const K1 = 'aaaaaaaa-aaaa-4aaa-8aaa-000000000001';
  const K2 = 'aaaaaaaa-aaaa-4aaa-8aaa-000000000002';

  it('rascunho: guarda e devolve os campos; outra pessoa ou organização não vê', () => {
    const m = memoria();
    const minha = chaveDoRecebimento('u1', 'o1');
    expect(gravarRecebimento(m, minha, { campos })).toBe(true);
    expect(lerRecebimento(m, minha)).toEqual({ campos });
    expect(lerRecebimento(m, chaveDoRecebimento('u2', 'o1'))).toBeNull();
    expect(lerRecebimento(m, chaveDoRecebimento('u1', 'o2'))).toBeNull();
    expect(minha.startsWith('safrion:')).toBe(true);
  });

  it('gravar o rascunho (outra aba digitando) nunca apaga nem troca intenção pendente', () => {
    const m = memoria();
    expect(
      gravarIntencao(m, 'u1', 'o1', { campos, intencao: intencao(K1), criadaEm: '2026-09-30T10:00:00.000Z' }),
    ).toBe(true);
    const outra = formulario([linha('a')], { numero: 'CX-OUTRO' });
    gravarRecebimento(m, chaveDoRecebimento('u1', 'o1'), { campos: outra });
    expect(lerIntencoes(m, 'u1', 'o1')).toEqual([
      { campos, intencao: intencao(K1), criadaEm: '2026-09-30T10:00:00.000Z' },
    ]);
    expect(lerRecebimento(m, chaveDoRecebimento('u1', 'o1'))?.campos.numero).toBe('CX-OUTRO');
  });

  it('várias intenções: cada uma na sua chave, a mais antiga primeiro; apagar uma não toca as outras', () => {
    const m = memoria();
    gravarIntencao(m, 'u1', 'o1', { campos, intencao: intencao(K2), criadaEm: '2026-09-30T10:05:00.000Z' });
    gravarIntencao(m, 'u1', 'o1', { campos, intencao: intencao(K1), criadaEm: '2026-09-30T10:00:00.000Z' });
    gravarIntencao(m, 'u2', 'o1', { campos, intencao: intencao(K1), criadaEm: '2026-09-30T09:00:00.000Z' });
    expect(lerIntencoes(m, 'u1', 'o1').map((g) => g.intencao.chave)).toEqual([K1, K2]);
    apagarIntencao(m, 'u1', 'o1', K1);
    expect(lerIntencoes(m, 'u1', 'o1').map((g) => g.intencao.chave)).toEqual([K2]);
    expect(lerIntencoes(m, 'u2', 'o1').map((g) => g.intencao.chave)).toEqual([K1]);
    expect(lerIntencoes(m, 'u1', 'o2')).toEqual([]);
  });

  it('armazenamento cheio: gravar intenção devolve false, sem lançar e sem apagar o que já estava', () => {
    const m = memoria();
    gravarIntencao(m, 'u1', 'o1', { campos, intencao: intencao(K1), criadaEm: '2026-09-30T10:00:00.000Z' });
    const cheio = { ...memoria(true), getItem: m.getItem, removeItem: m.removeItem };
    expect(gravarIntencao(cheio, 'u1', 'o1', { campos, intencao: intencao(K2), criadaEm: 'x' })).toBe(false);
    expect(gravarRecebimento(cheio, chaveDoRecebimento('u1', 'o1'), { campos })).toBe(false);
    expect(lerIntencoes(m, 'u1', 'o1')).toHaveLength(1);
    expect(gravarIntencao(null, 'u1', 'o1', { campos, intencao: intencao(K2), criadaEm: 'x' })).toBe(false);
  });

  it('guardados (CX-UI04): um por chave, o mais antigo primeiro, com motivo só quando recusado; apagar tira só o próprio', () => {
    const m = memoria();
    const recusada = formulario([linha('a')], { numero: 'CX-MULTI-A' });
    expect(
      guardarFormulario(m, 'u1', 'o1', {
        id: K2,
        campos: recusada,
        motivo: { mensagem: 'Este documento do emitente já foi recebido.', campo: 'numero' },
        guardadoEm: '2026-09-30T10:05:00.000Z',
      }),
    ).toBe(true);
    guardarFormulario(m, 'u1', 'o1', {
      id: K1,
      campos,
      motivo: null,
      guardadoEm: '2026-09-30T10:00:00.000Z',
    });
    // Rascunho e intenções não se misturam com guardados.
    gravarRecebimento(m, chaveDoRecebimento('u1', 'o1'), { campos });
    expect(lerGuardados(m, 'u1', 'o1').map((g) => [g.id, g.motivo?.campo ?? null])).toEqual([
      [K1, null],
      [K2, 'numero'],
    ]);
    expect(lerIntencoes(m, 'u1', 'o1')).toEqual([]);
    expect(lerGuardados(m, 'u2', 'o1')).toEqual([]);
    apagarGuardado(m, 'u1', 'o1', K1);
    expect(lerGuardados(m, 'u1', 'o1').map((g) => g.id)).toEqual([K2]);
    // Motivo com campo fora da origem é formato inválido: ignorado.
    m.dados.set(
      `${prefixoDosGuardados('u1', 'o1')}${K1}`,
      JSON.stringify({ id: K1, campos, motivo: { mensagem: 'x', campo: 'senha' }, guardadoEm: 'x' }),
    );
    expect(lerGuardados(m, 'u1', 'o1').map((g) => g.id)).toEqual([K2]);
  });

  it('só o contexto (emitente, fazenda, local, hoje) não é conteúdo a preservar; qualquer coisa digitada é', () => {
    expect(temConteudo(recebimentoVazio(opcoes, '2026-09-30', 'l1'))).toBe(false);
    expect(
      temConteudo(formulario([linhaVazia('x', { local: U.local })], { numero: '', serie: '', emissao: '' })),
    ).toBe(false);
    expect(temConteudo({ ...recebimentoVazio(opcoes, '2026-09-30', 'l1'), numero: 'CX-PROXIMO' })).toBe(true);
    expect(temConteudo(formulario([linha('a')], { numero: '', serie: '', emissao: '' }))).toBe(true);
  });

  it('formato corrompido é ignorado sem esconder as outras; intenção fora da própria chave não vale', () => {
    const m = memoria();
    const prefixo = prefixoDasIntencoes('u1', 'o1');
    m.dados.set(chaveDoRecebimento('u1', 'o1'), '{nao json');
    expect(lerRecebimento(m, chaveDoRecebimento('u1', 'o1'))).toBeNull();
    m.dados.set(`${prefixo}${K1}`, '{nao json');
    m.dados.set(`${prefixo}${K2}`, JSON.stringify({ campos, intencao: intencao(K1), criadaEm: 'x' }));
    gravarIntencao(m, 'u1', 'o1', {
      campos,
      intencao: intencao('aaaaaaaa-aaaa-4aaa-8aaa-000000000003'),
      criadaEm: '2026-09-30T10:00:00.000Z',
    });
    expect(lerIntencoes(m, 'u1', 'o1').map((g) => g.intencao.chave)).toEqual([
      'aaaaaaaa-aaaa-4aaa-8aaa-000000000003',
    ]);
  });
});

describe('lista e detalhe', () => {
  const resumo: DocumentoResumo = {
    id: U.doc,
    emitente: { id: U.emitente, nome: 'Fornecedor Teste Ltda', identificacao: '11222333000181' },
    tipo: 'nfe',
    serie: '1',
    numero: '7001',
    emissao: '2026-09-29',
    recebimento: '2026-09-30',
    fazenda: { id: U.fazenda, nome: 'Fazenda Demonstração' },
    status: 'confirmado',
    versao: 1,
    registradoEm: '2026-09-30T12:00:00.000Z',
    contagens: { linhas: 2, divergencias: 1, inspecoes: 0, ocorrenciasAbertas: 0 },
  };

  it('ocorrência devolvida aparece registrada, com o que chegou, destino e quem responde; retida é aberta com prazo', () => {
    const base = {
      id: 'o1',
      linha: { id: 'l1', numero: 4 },
      produtoReal: { id: U.diesel, nome: 'Diesel S10' },
      quantidade: '10',
      unidade: 'L',
      destino: 'devolvido_na_entrega' as const,
      status: 'registrada' as const,
      responsavel: { id: U.pessoa, nome: 'Gerente (fictício)' },
      prazo: null,
      registradaEm: '2026-09-30T12:00:00.000Z',
    };
    expect(linhaDaOcorrencia(base).celulas).toEqual({
      linha: { texto: '4', valor: '4' },
      chegou: { texto: 'Diesel S10', valor: 'Diesel S10' },
      quantidade: { texto: '10 L', valor: '10 L' },
      destino: { texto: 'Devolvido na entrega', valor: 'Devolvido na entrega' },
      responsavel: { texto: 'Gerente (fictício)', valor: 'Gerente (fictício)' },
      situacao: { texto: 'Registrada', valor: 'Registrada', papel: 'neutro' },
    });
    const retida = linhaDaOcorrencia({
      ...base,
      produtoReal: { descricao: 'Fungicida B, tambor' },
      unidade: 'tambor 200 L',
      quantidade: '1',
      destino: 'retido_para_decisao',
      status: 'aberta',
      prazo: '2026-10-02',
    }).celulas;
    expect(retida['chegou']?.texto).toBe('Fungicida B, tambor');
    expect(retida['responsavel']?.texto).toBe('Gerente (fictício) · até 02/10/2026');
    expect(retida['situacao']).toEqual({ texto: 'Aberta', valor: 'Aberta', papel: 'atencao' });
  });

  it('identificação do emitente com a máscara de costume', () => {
    expect(formatarIdentificacao('11222333000181')).toBe('11.222.333/0001-81');
    expect(formatarIdentificacao('12345678909')).toBe('123.456.789-09');
    expect(formatarIdentificacao('99')).toBe('99');
  });

  it('documento: nome, estado com palavra e pendências na linha da lista', () => {
    expect(rotuloDoDocumento({ tipo: 'nfe', serie: '', numero: '88' })).toBe('NF 88');
    expect(rotuloDoDocumento({ tipo: 'outro', serie: 'A', numero: '5' })).toBe('Doc A/5');
    expect(estadoDoDocumento(resumo)).toEqual({ palavra: 'Divergência aberta', papel: 'atencao' });
    expect(estadoDoDocumento({ ...resumo, contagens: { ...resumo.contagens, inspecoes: 1 } }).palavra).toBe(
      'Inspeção pendente',
    );
    expect(
      estadoDoDocumento({
        ...resumo,
        contagens: { linhas: 1, divergencias: 0, inspecoes: 0, ocorrenciasAbertas: 0 },
      }),
    ).toEqual({
      palavra: 'Conforme',
      papel: 'sucesso',
    });
    expect(linhaDoDocumento(resumo)).toEqual({
      id: U.doc,
      href: `/estoque/recebimentos/${U.doc}`,
      celulas: {
        documento: { texto: 'NF 1/7001', valor: 'NF 1/7001' },
        emitente: { texto: 'Fornecedor Teste Ltda', valor: 'Fornecedor Teste Ltda' },
        recebido: { texto: '30/09/2026', valor: '2026-09-30' },
        estado: { texto: 'Divergência aberta', valor: 'Divergência aberta', papel: 'atencao' },
        linhas: { texto: '2', valor: '2' },
        pendencias: { texto: '1 divergência', valor: '1 divergência' },
      },
    });
  });

  it('pendências dizem o que é, a linha, quem resolve e o prazo; divergência cai em quem registrou', () => {
    const linhaBase = {
      produto: { id: U.fungicida, nome: 'Fungicida A' },
      lote: { id: U.doc, codigo: 'F26-03', tipo: 'fabricante' as const, validade: '2027-06-30' },
      local: { id: U.local, nome: 'Almoxarifado central' },
      conversao: null,
      pedidoLinha: null,
      valorUnitario: null,
      movimentos: [],
    };
    const d: DocumentoDetalhe = {
      ...resumo,
      pedido: null,
      autor: { id: U.pessoa, nome: 'Almoxarife (fictício)' },
      recibo: null,
      linhas: [
        {
          ...linhaBase,
          id: 'l1',
          numero: 1,
          documento: '2',
          unidade: 'galão 5 L',
          parcelas: { apto: '1', quarentena: '0', bloqueado: '1', recusado: '0' },
          divergencia: { motivo: 'avaria', texto: null },
          inspecao: null,
        },
        {
          ...linhaBase,
          id: 'l2',
          numero: 2,
          documento: '60',
          unidade: 'L',
          parcelas: { apto: '50', quarentena: '10', bloqueado: '0', recusado: '0' },
          divergencia: null,
          inspecao: { responsavel: { id: U.pessoa, nome: 'Colega' }, prazo: '2026-10-03' },
        },
      ],
      ocorrencias: [],
    };
    expect(pendenciasDoDocumento(d)).toEqual([
      {
        tipo: 'Inspeção pendente',
        linha: 2,
        descricao: '10 L de Fungicida A em inspeção',
        responsavel: 'Colega',
        prazo: '2026-10-03',
      },
      {
        tipo: 'Divergência aberta',
        linha: 1,
        descricao: 'Avaria · Fungicida A',
        responsavel: 'Almoxarife (fictício)',
        prazo: null,
      },
    ]);
    const [primeira] = d.linhas;
    expect(primeira && textoDaConferencia(primeira)).toBe('1 galão 5 L apto · 1 galão 5 L bloqueado');
  });
});
