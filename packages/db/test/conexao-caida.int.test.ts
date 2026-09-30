import { randomUUID } from 'node:crypto';

import pg from 'pg';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { executarComando } from '../src/comando.js';
import { ErroComando } from '../src/erros.js';
import { emOrganizacao } from '../src/sessao.js';
import { criarBanco, semear, type Ambiente, type Semente } from './ambiente.js';

// Conexão que cai com o cliente emprestado do pool (CX-R03; contrato CMD-15 §6, v3.11): o próprio backend é encerrado
// no meio da transação. Sem ouvinte de 'error' no cliente emprestado, o pg transforma isso em exceção não tratada e o
// processo cai (o Vitest acusa como erro não tratado e falha a execução). O critério: processo vivo, falha controlada
// para quem chamou, conexão fora do pool e a próxima sessão isolada, sem organização herdada.
let amb: Ambiente;
let a: Semente;

beforeAll(async () => {
  amb = await criarBanco();
  a = await semear(amb.app, 'A');
});
afterAll(async () => {
  await amb.encerrar();
});

/** Pool de uma conexão só: a próxima sessão ou reaproveita a morta (defeito) ou abre outra (correto). */
function poolDeUma(): pg.Pool {
  return new pg.Pool({ connectionString: amb.url('app_runtime'), max: 1 });
}

const organizacaoNaConexao = async (c: pg.ClientBase) =>
  (await c.query<{ o: string | null }>("SELECT current_setting('app.organization_id', true) AS o")).rows[0]
    ?.o ?? '';

describe('conexão que cai com o cliente emprestado', () => {
  it('emOrganizacao: falha para quem chamou, a conexão sai do pool e a próxima sessão é limpa', async () => {
    const pool = poolDeUma();
    try {
      const erro: unknown = await emOrganizacao(pool, a.org, (c) =>
        c.query('SELECT pg_terminate_backend(pg_backend_pid())'),
      ).catch((e: unknown) => e);
      expect(erro).toBeInstanceOf(Error);
      // O evento de erro do socket chega depois da consulta rejeitada.
      await new Promise((fim) => setTimeout(fim, 200));
      expect(pool.totalCount).toBe(0);
      expect(await emOrganizacao(pool, a.org, organizacaoNaConexao)).toBe(a.org);
      const fora = await pool.query<{ o: string | null }>(
        "SELECT current_setting('app.organization_id', true) AS o",
      );
      expect(fora.rows[0]?.o ?? '').toBe('');
    } finally {
      await pool.end();
    }
  });

  it('envelope: resultado incerto para quem chamou, a conexão sai do pool e o comando seguinte funciona', async () => {
    const pool = poolDeUma();
    const intencao = (chave: string) => ({
      commandType: 'TESTE-CONEXAO',
      idempotencyKey: chave,
      initiatorKind: 'web' as const,
      actorId: a.usuario,
      target: { type: 'lot', id: a.lote },
      data: { chave },
      correlationId: `corr-${chave}`,
    });
    try {
      const erro: unknown = await executarComando(pool, a.org, intencao(randomUUID()), async (c) => {
        await c.query('SELECT pg_terminate_backend(pg_backend_pid())');
        return { resultingVersion: null, effects: {} };
      }).catch((e: unknown) => e);
      expect(erro).toBeInstanceOf(ErroComando);
      expect((erro as ErroComando).detalhe['resultadoIncerto']).toBe(true);
      await new Promise((fim) => setTimeout(fim, 200));
      expect(pool.totalCount).toBe(0);
      const r = await executarComando(pool, a.org, intencao(randomUUID()), () =>
        Promise.resolve({ resultingVersion: null, effects: {} }),
      );
      expect(r.outcome).toBe('confirmed');
    } finally {
      await pool.end();
    }
  });
});
