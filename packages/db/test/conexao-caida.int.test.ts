import { randomUUID } from 'node:crypto';

import pg from 'pg';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { executarComando } from '../src/comando.js';
import { ErroComando } from '../src/erros.js';
import { REPETIR_AQUISICAO_MS, emOrganizacao, emprestarConexao } from '../src/sessao.js';
import { novoToken, resolverSessao } from '../src/sessao-web.js';
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

// Espera controlada na aquisição (contrato CMD-15 §9.2): o prazo do pg-pool vale por aquisição e só a rejeição dele
// vira FALHA_TRANSITORIA legível, porque nenhum comando SQL da tentativa rodou. Travas, consultas, commit e outras
// falhas de conexão continuam como antes.
describe('aquisição de conexão com prazo', () => {
  const PRAZO_MS = 200;
  /** Pool de uma conexão com prazo curto; o teste segura a única conexão para esgotar a fila. */
  const poolComPrazo = () =>
    new pg.Pool({ connectionString: amb.url('app_runtime'), max: 1, connectionTimeoutMillis: PRAZO_MS });
  const intencao = (chave: string) => ({
    commandType: 'TESTE-AQUISICAO',
    idempotencyKey: chave,
    initiatorKind: 'web' as const,
    actorId: a.usuario,
    target: { type: 'lot', id: a.lote },
    data: { chave },
    correlationId: `corr-${chave}`,
  });
  const semEfeito = () => Promise.resolve({ resultingVersion: null, effects: {} });
  const intencoesDa = (chave: string) =>
    emOrganizacao(amb.app, a.org, async (c) =>
      Number(
        (
          await c.query<{ n: number }>(
            'SELECT count(*)::int AS n FROM app.intent_record WHERE idempotency_key = $1',
            [chave],
          )
        ).rows[0]?.n,
      ),
    );

  it('fila esgotada: comando, leitura e sessão respondem FALHA_TRANSITORIA legível; nada vaza nem roda depois', async () => {
    const pool = poolComPrazo();
    const chave = randomUUID();
    try {
      const segurada = await pool.connect();
      const [comando, leitura, sessao] = await Promise.all([
        executarComando(pool, a.org, intencao(chave), semEfeito).catch((e: unknown) => e),
        emOrganizacao(pool, a.org, (c) => c.query('SELECT 1')).catch((e: unknown) => e),
        resolverSessao(pool, novoToken().token).catch((e: unknown) => e),
      ]);
      for (const erro of [comando, leitura, sessao]) {
        expect(erro).toBeInstanceOf(ErroComando);
        expect((erro as ErroComando).codigo).toBe('FALHA_TRANSITORIA');
        expect((erro as ErroComando).detalhe['repetirEmMs']).toBe(REPETIR_AQUISICAO_MS);
      }
      // Só o comando fala de resultado, e só desta tentativa; a leitura não tem o campo.
      expect((comando as ErroComando).detalhe['resultadoIncerto']).toBe(false);
      expect('resultadoIncerto' in (leitura as ErroComando).detalhe).toBe(false);
      expect('resultadoIncerto' in (sessao as ErroComando).detalhe).toBe(false);
      expect(pool.waitingCount).toBe(0);
      segurada.release();
      // Quem esperou demais não recebe a conexão depois: nada da tentativa roda, e a conexão volta ociosa.
      await new Promise((fim) => setTimeout(fim, 2 * PRAZO_MS));
      expect(await intencoesDa(chave)).toBe(0);
      expect([pool.totalCount, pool.idleCount, pool.waitingCount]).toEqual([1, 1, 0]);
      expect((await executarComando(pool, a.org, intencao(chave), semEfeito)).outcome).toBe('confirmed');
      expect(await intencoesDa(chave)).toBe(1);
    } finally {
      await pool.end();
    }
  });

  it('resposta perdida, reenvio barrado na aquisição, a mesma chave com o pool livre devolve o recibo original', async () => {
    const pool = poolComPrazo();
    const chave = randomUUID();
    try {
      const original = await executarComando(pool, a.org, intencao(chave), semEfeito);
      const segurada = await pool.connect();
      const barrado: unknown = await executarComando(pool, a.org, intencao(chave), semEfeito).catch(
        (e: unknown) => e,
      );
      expect(barrado).toBeInstanceOf(ErroComando);
      expect((barrado as ErroComando).detalhe).toMatchObject({ resultadoIncerto: false });
      segurada.release();
      const recuperado = await executarComando(pool, a.org, intencao(chave), semEfeito);
      expect(recuperado.receiptId).toBe(original.receiptId);
      expect(recuperado.alreadyReceived).toBe(true);
      expect(await intencoesDa(chave)).toBe(1);
    } finally {
      await pool.end();
    }
  });

  it('sessão com cliente em transação: não readquire nem libera, e erro de consulta não é reclassificado', async () => {
    const pool = poolComPrazo();
    const cliente = await pool.connect();
    try {
      await cliente.query('BEGIN');
      // O pool está esgotado pelo próprio cliente: readquirir esperaria o prazo e falharia.
      expect(await resolverSessao(cliente, novoToken().token)).toBeNull();
      expect([pool.totalCount, pool.idleCount]).toEqual([1, 0]);
      expect((await cliente.query<{ um: number }>('SELECT 1 AS um')).rows[0]?.um).toBe(1);
      await cliente.query('SELECT 1 / 0').catch(() => undefined);
      const erro: unknown = await resolverSessao(cliente, novoToken().token).catch((e: unknown) => e);
      expect(erro).toBeInstanceOf(pg.DatabaseError);
      expect((erro as pg.DatabaseError).code).toBe('25P02');
      await cliente.query('ROLLBACK');
    } finally {
      cliente.release();
      await pool.end();
    }
  });

  it('prazo de aquisição não interrompe quem já tem conexão e espera trava; o próximo recebe a falha legível', async () => {
    const pool = poolComPrazo();
    const trava = await amb.app.connect();
    const chave = randomUUID();
    try {
      await trava.query('BEGIN');
      await trava.query("SELECT set_config('app.organization_id', $1, true)", [a.org]);
      await trava.query('SELECT id FROM app.lot WHERE id = $1 FOR UPDATE', [a.lote]);
      // O envelope só limita a espera pela chave da intenção; a trava do efeito espera sem prazo (fora da §9.2).
      const esperando = executarComando(pool, a.org, intencao(chave), async (c) => {
        await c.query('SELECT id FROM app.lot WHERE id = $1 FOR UPDATE', [a.lote]);
        return { resultingVersion: null, effects: {} };
      });
      let terminou = false;
      void esperando.then(
        () => (terminou = true),
        () => (terminou = true),
      );
      await new Promise((fim) => setTimeout(fim, 3 * PRAZO_MS));
      expect(terminou).toBe(false);
      // A única conexão está presa na trava: o próximo comando falha na aquisição, sem começar.
      const barrado: unknown = await executarComando(pool, a.org, intencao(randomUUID()), semEfeito).catch(
        (e: unknown) => e,
      );
      expect(barrado).toBeInstanceOf(ErroComando);
      expect((barrado as ErroComando).detalhe).toEqual({
        resultadoIncerto: false,
        repetirEmMs: REPETIR_AQUISICAO_MS,
      });
      await trava.query('ROLLBACK');
      expect((await esperando).outcome).toBe('confirmed');
      expect(await intencoesDa(chave)).toBe(1);
    } finally {
      await trava.query('ROLLBACK').catch(() => undefined);
      trava.release();
      await pool.end();
    }
  });

  it('outra falha de conexão passa intacta; só as duas mensagens de prazo do pg-pool viram FALHA_TRANSITORIA', async () => {
    const recusada = new Error('connect ECONNREFUSED 127.0.0.1:1');
    const falso = (erro: Error) => ({ connect: () => Promise.reject(erro) }) as unknown as pg.Pool;
    expect(await emprestarConexao(falso(recusada), 'comando').catch((e: unknown) => e)).toBe(recusada);
    for (const mensagem of [
      'timeout exceeded when trying to connect',
      'Connection terminated due to connection timeout',
    ]) {
      const erro: unknown = await emprestarConexao(falso(new Error(mensagem)), 'comando').catch(
        (e: unknown) => e,
      );
      expect(erro).toBeInstanceOf(ErroComando);
      expect((erro as ErroComando).detalhe).toEqual({
        resultadoIncerto: false,
        repetirEmMs: REPETIR_AQUISICAO_MS,
      });
    }
  });
});
