// F0B2-01 (revisão do Codex sobre 24bef1c): o log do envelope não carrega texto livre de infraestrutura nem do
// cliente; só códigos seguros e a correlação. O erro original sobe intacto. Sem banco: a conexão é simulada.
import { criarRegistrador } from '@safrion/contracts';
import pg from 'pg';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { executarComando, type Intencao } from '../src/comando.js';
import { ErroComando } from '../src/erros.js';

const CANARIO = 'CANARIO_FICTICIO_F0B2_01';
const intencao: Intencao = {
  commandType: 'TESTE-MOV',
  idempotencyKey: 'k-privacidade',
  initiatorKind: 'web',
  actorId: '22222222-2222-4222-8222-222222222222',
  target: { type: 'lot', id: '33333333-3333-4333-8333-333333333333', expectedVersion: 0 },
  data: {},
  correlationId: 'corr-privacidade',
};
const ORG = '11111111-1111-4111-8111-111111111111';

const pools: pg.Pool[] = [];
afterEach(async () => {
  vi.restoreAllMocks();
  for (const p of pools.splice(0)) await p.end();
});

async function executarComFalha(falha: unknown, i: Intencao = intencao) {
  const linhas: string[] = [];
  const pool = new pg.Pool();
  pools.push(pool);
  vi.spyOn(pool, 'connect').mockRejectedValueOnce(falha);
  const registrador = criarRegistrador({
    servico: 'teste',
    versao: '0',
    escrever: (l) => linhas.push(l),
    agora: () => '2026-09-27T23:40:00.000Z',
  });
  const erro: unknown = await executarComando(pool, ORG, i, () => Promise.reject(new Error('não executa')), {
    registrador,
  }).catch((e: unknown) => e);
  return { erro, linhas };
}

describe('log sem texto livre (F0B2-01)', () => {
  it('conexão que falha com URL e canário na mensagem: erro original sobe, log só com códigos e correlação', async () => {
    const falha = Object.assign(new Error(`Falha: postgresql://qa:${CANARIO}@exemplo.invalid/db`), {
      code: 'ECONNREFUSED',
    });
    const { erro, linhas } = await executarComFalha(falha);
    expect(erro).toBe(falha);
    expect(linhas).toHaveLength(1);
    expect(JSON.parse(linhas[0] ?? '')).toMatchObject({
      evento: 'comando.falhou',
      correlation_id: 'corr-privacidade',
      erro_codigo: 'NAO_CLASSIFICADO',
      erro_tipo: 'Error',
      command_type: 'TESTE-MOV',
      target_id: intencao.target.id,
    });
    expect(linhas.join('\n')).not.toContain(CANARIO);
    expect(linhas.join('\n')).not.toContain('postgresql://');
    expect(JSON.parse(linhas[0] ?? '')).not.toHaveProperty('codigo_pg');
  });

  it('ErroComando com texto livre no detalhe: nada dele vai ao log; SQLSTATE e resultado incerto vão', async () => {
    const falha = new ErroComando('FALHA_TRANSITORIA', 'Mensagem pública.', {
      causa: `valor inválido contém ${CANARIO}`,
      codigoPg: '22P02',
      resultadoIncerto: false,
    });
    const { erro, linhas } = await executarComFalha(falha);
    expect(erro).toBe(falha);
    expect(JSON.parse(linhas[0] ?? '')).toMatchObject({
      erro_codigo: 'FALHA_TRANSITORIA',
      erro_tipo: 'ErroComando',
      codigo_pg: '22P02',
      resultado_incerto: false,
    });
    expect(linhas.join('\n')).not.toContain(CANARIO);
  });

  it('SQLSTATE fora do formato e resultado incerto que não é booleano ficam de fora', async () => {
    const falha = new ErroComando('FALHA_TRANSITORIA', 'm', {
      codigoPg: `22P02 ${CANARIO}`,
      resultadoIncerto: CANARIO,
    });
    const { linhas } = await executarComFalha(falha);
    const linha = JSON.parse(linhas[0] ?? '') as Record<string, unknown>;
    expect(linha).not.toHaveProperty('codigo_pg');
    expect(linha).not.toHaveProperty('resultado_incerto');
    expect(linhas.join('\n')).not.toContain(CANARIO);
  });

  it('identificadores do cliente com texto livre ficam de fora do log', async () => {
    const livre = `chave com espaço ${CANARIO}`;
    const { linhas } = await executarComFalha(new Error('x'), {
      ...intencao,
      idempotencyKey: livre,
      commandType: `CMD ${CANARIO}`,
      correlationId: `corr ${CANARIO}`,
      target: { ...intencao.target, type: `lote ${CANARIO}`, id: CANARIO },
    });
    const linha = JSON.parse(linhas[0] ?? '') as Record<string, unknown>;
    expect(linha).toMatchObject({ correlation_id: 'sem-correlacao' });
    for (const campo of ['idempotency_key', 'command_type', 'target_type', 'target_id']) {
      expect(linha, campo).not.toHaveProperty(campo);
    }
    expect(linhas.join('\n')).not.toContain(CANARIO);
  });

  it('valor lançado que nem é Error: tipo registrado, sem conteúdo', async () => {
    const { erro, linhas } = await executarComFalha(`texto solto ${CANARIO}`);
    expect(erro).toBe(`texto solto ${CANARIO}`);
    expect(JSON.parse(linhas[0] ?? '')).toMatchObject({ erro_tipo: 'string' });
    expect(linhas.join('\n')).not.toContain(CANARIO);
  });
});
