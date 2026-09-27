// F0-b2: recibo real conferido pelo contrato e uma linha de log correlacionada por comando (ENG-014, ENG-015, ENG-081).
import { EsquemaDadosMovimento, EsquemaRecibo, criarRegistrador } from '@safrion/contracts';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { executarComando } from '../src/comando.js';
import { ErroComando } from '../src/erros.js';
import { conteudoDoMovimento, pedidoDeMovimento, registrarMovimento } from '../src/estoque.js';
import { respostaDeErro } from '../src/resposta.js';
import { criarBanco, semear, type Ambiente, type Semente } from './ambiente.js';

let amb: Ambiente;
let s: Semente;
const linhas: string[] = [];
const registrador = criarRegistrador({
  servico: 'teste',
  versao: '0',
  escrever: (l) => linhas.push(l),
  agora: () => '2026-09-27T13:00:00.000Z',
});
const logs = () => linhas.map((l) => JSON.parse(l) as Record<string, unknown>);

beforeAll(async () => {
  amb = await criarBanco();
  s = await semear(amb.app, 'Contrato');
});
afterAll(async () => {
  await amb.encerrar();
});

/** Do corpo externo (contrato) até o envelope, como a rota da F0-c fará. */
function comando(chave: string, versao: number, valor: string, unidade = 'L') {
  const dados = EsquemaDadosMovimento.parse({
    lote: s.lote,
    local: s.local,
    movimento: { tipo: 'entrada', quantidade: { valor, unidade }, situacao: 'liberado_livre' },
  });
  const pedido = pedidoDeMovimento(dados);
  return {
    intencao: {
      commandType: 'TESTE-MOV',
      idempotencyKey: chave,
      initiatorKind: 'web' as const,
      actorId: s.usuario,
      target: { type: 'lot', id: s.lote, expectedVersion: versao },
      data: conteudoDoMovimento(pedido),
      correlationId: `corr-${chave}`,
    },
    efeito: registrarMovimento(pedido),
  };
}

describe('contrato e log do envelope (F0-b2)', () => {
  it('o recibo real, original e reenvio, segue o esquema do contrato', async () => {
    const { intencao, efeito } = comando('c-1', 0, '12.345');
    const original = await executarComando(amb.app, s.org, intencao, efeito, { registrador });
    const reenvio = await executarComando(amb.app, s.org, intencao, efeito, { registrador });
    expect(EsquemaRecibo.safeParse(original).success).toBe(true);
    expect(EsquemaRecibo.safeParse(reenvio).success).toBe(true);
  });

  it('uma linha por comando, com a correlação, sem o conteúdo do comando', () => {
    const doC1 = logs().filter((l) => l['correlation_id'] === 'corr-c-1');
    expect(doC1).toHaveLength(2);
    expect(doC1.map((l) => [l['evento'], l['outcome'], l['already_received']])).toEqual([
      ['comando.processado', 'confirmed', false],
      ['comando.processado', 'confirmed', true],
    ]);
    expect(doC1[0]).toMatchObject({ organization_id: s.org, command_type: 'TESTE-MOV', target_id: s.lote });
    expect(typeof doC1[0]?.['duracao_ms']).toBe('number');
    const texto = linhas.join('\n');
    expect(texto).not.toContain('12.345');
    expect(texto).not.toContain(s.usuario);
  });

  it('chave reusada e rejeição também ficam registradas, com nível e código', async () => {
    const { intencao, efeito } = comando('c-1', 0, '99');
    await expect(executarComando(amb.app, s.org, intencao, efeito, { registrador })).rejects.toBeInstanceOf(
      ErroComando,
    );
    const conflito = comando('c-2', 0, '1');
    await executarComando(amb.app, s.org, conflito.intencao, conflito.efeito, { registrador });
    const ultimos = logs().slice(-2);
    expect(ultimos[0]).toMatchObject({
      nivel: 'aviso',
      evento: 'comando.falhou',
      erro_codigo: 'IDEMPOTENCY_KEY_REUSED',
    });
    expect(ultimos[1]).toMatchObject({
      nivel: 'info',
      outcome: 'version_conflict',
      reason_code: 'VERSAO_DESATUALIZADA',
    });
  });

  it('log quebrado não muda o resultado do comando', async () => {
    const quebrado = criarRegistrador({
      servico: 'teste',
      versao: '0',
      escrever: () => {
        throw new Error('disco cheio');
      },
      agora: () => '',
    });
    const { intencao, efeito } = comando('c-3', 1, '1');
    const r = await executarComando(amb.app, s.org, intencao, efeito, { registrador: quebrado });
    expect(r.outcome).toBe('confirmed');
  });

  it('falha real de transação com canário na mensagem do banco: fora do log e da resposta, preservada em cause', async () => {
    const canario = 'CANARIO_FICTICIO_TRANSACAO_7f31';
    const { intencao } = comando('c-5', 3, '1');
    const erro: unknown = await executarComando(
      amb.app,
      s.org,
      intencao,
      async (c) => {
        await c.query('SELECT $1::int', [canario]); // o PostgreSQL recusa e repete o valor na mensagem
        return { resultingVersion: null, effects: {} };
      },
      { registrador },
    ).catch((e: unknown) => e);
    expect(erro).toBeInstanceOf(ErroComando);
    expect((erro as ErroComando).codigo).toBe('FALHA_TRANSITORIA');
    expect(String((erro as Error).cause instanceof Error ? (erro as Error).cause : '')).toContain(canario);
    expect(JSON.stringify((erro as ErroComando).detalhe)).not.toContain(canario);
    const linha = logs().at(-1);
    expect(linha).toMatchObject({
      correlation_id: 'corr-c-5',
      erro_codigo: 'FALHA_TRANSITORIA',
      codigo_pg: '22P02',
    });
    expect(linhas.join('\n')).not.toContain(canario);
    expect(JSON.stringify(respostaDeErro(erro, 'corr-c-5'))).not.toContain(canario);
  });

  it('pedido fora do contrato é registrado com a correlação que houver', async () => {
    const { intencao, efeito } = comando('c-4', 2, '1');
    await expect(
      executarComando(amb.app, s.org, { ...intencao, actorId: 'nao-uuid' }, efeito, { registrador }),
    ).rejects.toMatchObject({ codigo: 'CONTRATO_INVALIDO' });
    await expect(
      executarComando(amb.app, s.org, { ...intencao, correlationId: '' }, efeito, { registrador }),
    ).rejects.toMatchObject({ codigo: 'CONTRATO_INVALIDO' });
    const ultimos = logs().slice(-2);
    expect(ultimos.map((l) => [l['correlation_id'], l['erro_codigo']])).toEqual([
      ['corr-c-4', 'CONTRATO_INVALIDO'],
      ['sem-correlacao', 'CONTRATO_INVALIDO'],
    ]);
  });
});
