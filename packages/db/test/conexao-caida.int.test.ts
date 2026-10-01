import { randomUUID } from 'node:crypto';

import { falhaPermanenteSemGravacao } from '@safrion/contracts';
import pg from 'pg';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { executarComando } from '../src/comando.js';
import { ErroComando } from '../src/erros.js';
import { respostaDeErro } from '../src/resposta.js';
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

  /**
   * Segura a única conexão do pool. A devolução é única: cedo no caminho feliz ou no finally, para uma asserção que falha
   * antes dela não deixar o pool.end() pendurado nem prender o banco do teste.
   */
  async function segurar(pool: pg.Pool): Promise<{ soltar(): void }> {
    const cliente = await pool.connect();
    let solta = false;
    return {
      soltar() {
        if (solta) return;
        solta = true;
        cliente.release();
      },
    };
  }

  it('fila esgotada: comando, leitura e sessão respondem FALHA_TRANSITORIA legível; nada vaza nem roda depois', async () => {
    const pool = poolComPrazo();
    const chave = randomUUID();
    const segurada = await segurar(pool);
    try {
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
      segurada.soltar();
      // Quem esperou demais não recebe a conexão depois: nada da tentativa roda, e a conexão volta ociosa.
      await new Promise((fim) => setTimeout(fim, 2 * PRAZO_MS));
      expect(await intencoesDa(chave)).toBe(0);
      expect([pool.totalCount, pool.idleCount, pool.waitingCount]).toEqual([1, 1, 0]);
      expect((await executarComando(pool, a.org, intencao(chave), semEfeito)).outcome).toBe('confirmed');
      expect(await intencoesDa(chave)).toBe(1);
    } finally {
      segurada.soltar();
      await pool.end();
    }
  });

  it('resposta perdida, reenvio barrado na aquisição, a mesma chave com o pool livre devolve o recibo original', async () => {
    const pool = poolComPrazo();
    const chave = randomUUID();
    let segurada: { soltar(): void } | undefined;
    try {
      const original = await executarComando(pool, a.org, intencao(chave), semEfeito);
      segurada = await segurar(pool);
      const barrado: unknown = await executarComando(pool, a.org, intencao(chave), semEfeito).catch(
        (e: unknown) => e,
      );
      expect(barrado).toBeInstanceOf(ErroComando);
      expect((barrado as ErroComando).detalhe).toMatchObject({ resultadoIncerto: false });
      segurada.soltar();
      const recuperado = await executarComando(pool, a.org, intencao(chave), semEfeito);
      expect(recuperado.receiptId).toBe(original.receiptId);
      expect(recuperado.alreadyReceived).toBe(true);
      expect(await intencoesDa(chave)).toBe(1);
    } finally {
      segurada?.soltar();
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

// Trava do efeito com prazo (contrato CMD-15 §9.3): o lock_timeout da espera pela chave segue valendo no efeito. Limita
// cada espera por trava, não o comando; 55P03 com ROLLBACK confirmado vira FALHA_TRANSITORIA com repetirEmMs, sem
// repetição automática. Cada teste tem vigia com prazo e solta as travas no finally, para uma regressão falhar pela
// asserção e não pendurar.
describe('trava do efeito com prazo', () => {
  const ESPERA_MS = 800;
  const TIPO = 'TESTE-TRAVA';
  const intencao = (chave: string) => ({
    commandType: TIPO,
    idempotencyKey: chave,
    initiatorKind: 'web' as const,
    actorId: a.usuario,
    target: { type: 'lot', id: a.lote },
    data: { chave },
    correlationId: `corr-${chave}`,
  });
  const nada = { resultingVersion: null, effects: {} };
  const travarLote = async (c: pg.ClientBase) => {
    await c.query('SELECT id FROM app.lot WHERE id = $1 FOR UPDATE', [a.lote]);
    return nada;
  };
  const contar = (sql: string, parametro: string) =>
    emOrganizacao(amb.app, a.org, async (c) =>
      Number((await c.query<{ n: number }>(sql, [parametro])).rows[0]?.n),
    );
  const residuo = async (chave: string) => ({
    intencoes: await contar(
      'SELECT count(*)::int AS n FROM app.intent_record WHERE idempotency_key = $1',
      chave,
    ),
    auditoria: await contar('SELECT count(*)::int AS n FROM app.audit_log WHERE idempotency_key = $1', chave),
    outbox: await contar('SELECT count(*)::int AS n FROM app.outbox WHERE causation_command_type = $1', TIPO),
  });
  /** Espera a promessa no máximo `ms`; o resultado marcado continua disponível para ser aguardado no finally. */
  async function comVigia<T>(promessa: Promise<T>, ms: number) {
    const marcado = promessa.then(
      (valor) => ({ ok: true as const, valor }),
      (erro: unknown) => ({ ok: false as const, erro }),
    );
    const vigia = new Promise<'sem-prazo'>((fim) => {
      setTimeout(() => {
        fim('sem-prazo');
      }, ms);
    });
    return { resultado: await Promise.race([marcado, vigia]), marcado };
  }
  async function travarNoLote(): Promise<pg.PoolClient> {
    const trava = await amb.app.connect();
    await trava.query('BEGIN');
    await trava.query("SELECT set_config('app.organization_id', $1, true)", [a.org]);
    await trava.query('SELECT id FROM app.lot WHERE id = $1 FOR UPDATE', [a.lote]);
    return trava;
  }

  it('lote ocupado além da espera: FALHA_TRANSITORIA com repetirEmMs, sem resíduo; liberado, a mesma chave confirma uma vez', async () => {
    const pool = new pg.Pool({ connectionString: amb.url('app_runtime'), max: 1 });
    const chave = randomUUID();
    const antes = await residuo(chave);
    const trava = await travarNoLote();
    let pendente: Promise<unknown> | undefined;
    try {
      const inicio = performance.now();
      const r = await comVigia(
        executarComando(pool, a.org, intencao(chave), travarLote, { esperaChaveMs: ESPERA_MS }),
        10 * ESPERA_MS,
      );
      pendente = r.marcado;
      expect(r.resultado, 'a trava do efeito esperou sem prazo').not.toBe('sem-prazo');
      expect(r.resultado).toMatchObject({ ok: false });
      const erro = (r.resultado as { erro: unknown }).erro;
      expect(erro).toBeInstanceOf(ErroComando);
      expect((erro as ErroComando).codigo).toBe('FALHA_TRANSITORIA');
      expect((erro as ErroComando).detalhe).toEqual({
        resultadoIncerto: false,
        codigoPg: '55P03',
        repetirEmMs: ESPERA_MS,
      });
      expect(performance.now() - inicio).toBeGreaterThanOrEqual(0.9 * ESPERA_MS);
      expect(await residuo(chave)).toEqual(antes);
      expect([pool.totalCount, pool.idleCount, pool.waitingCount]).toEqual([1, 1, 0]);
      await trava.query('ROLLBACK');
      const r2 = await executarComando(pool, a.org, intencao(chave), travarLote, {
        esperaChaveMs: ESPERA_MS,
      });
      expect(r2.outcome).toBe('confirmed');
      expect((await residuo(chave)).intencoes).toBe(1);
    } finally {
      await trava.query('ROLLBACK').catch(() => undefined);
      trava.release();
      await pendente;
      await pool.end();
    }
  });

  it('disputa curta no mesmo lote: espera e confirma, sem falha', async () => {
    const pool = new pg.Pool({ connectionString: amb.url('app_runtime'), max: 1 });
    const trava = await travarNoLote();
    let pendente: Promise<unknown> | undefined;
    try {
      const solta = setTimeout(() => void trava.query('ROLLBACK'), 0.3 * ESPERA_MS);
      const r = await comVigia(
        executarComando(pool, a.org, intencao(randomUUID()), travarLote, { esperaChaveMs: ESPERA_MS }),
        10 * ESPERA_MS,
      );
      clearTimeout(solta);
      pendente = r.marcado;
      expect(r.resultado).toMatchObject({ ok: true, valor: { outcome: 'confirmed' } });
    } finally {
      await trava.query('ROLLBACK').catch(() => undefined);
      trava.release();
      await pendente;
      await pool.end();
    }
  });

  it('duas travas seguidas, cada uma liberada antes da espera: confirma, e a duração passa da espera', async () => {
    // O limite é por espera de trava, não do comando: duas esperas curtas somadas passam do valor da espera.
    const pool = new pg.Pool({ connectionString: amb.url('app_runtime'), max: 1 });
    const [h1, h2] = [await amb.app.connect(), await amb.app.connect()];
    const [k1, k2] = [Math.floor(Math.random() * 2 ** 30), 2 ** 30 + Math.floor(Math.random() * 2 ** 30)];
    let pendente: Promise<unknown> | undefined;
    try {
      await h1.query('SELECT pg_advisory_lock($1)', [k1]);
      await h2.query('SELECT pg_advisory_lock($1)', [k2]);
      const inicio = performance.now();
      setTimeout(() => void h1.query('SELECT pg_advisory_unlock($1)', [k1]), 0.7 * ESPERA_MS);
      setTimeout(() => void h2.query('SELECT pg_advisory_unlock($1)', [k2]), 1.4 * ESPERA_MS);
      const r = await comVigia(
        executarComando(
          pool,
          a.org,
          intencao(randomUUID()),
          async (c) => {
            await c.query('SELECT pg_advisory_xact_lock($1)', [k1]);
            await c.query('SELECT pg_advisory_xact_lock($1)', [k2]);
            return nada;
          },
          { esperaChaveMs: ESPERA_MS },
        ),
        10 * ESPERA_MS,
      );
      pendente = r.marcado;
      expect(r.resultado).toMatchObject({ ok: true, valor: { outcome: 'confirmed' } });
      expect(performance.now() - inicio).toBeGreaterThan(ESPERA_MS);
    } finally {
      await h1.query('SELECT pg_advisory_unlock_all()').catch(() => undefined);
      await h2.query('SELECT pg_advisory_unlock_all()').catch(() => undefined);
      h1.release();
      h2.release();
      await pendente;
      await pool.end();
    }
  });

  it('ROLLBACK que falha depois do 55P03: resultado incerto, sem repetirEmMs, conexão fora do pool e sem resíduo', async () => {
    // Contraprova do Codex (work/hml-review/cmd15-0c74bad-codex, 12:41Z), reduzida: depois do 55P03 real, o backend da
    // própria tentativa é encerrado antes de o erro voltar ao envelope, e o ROLLBACK não se confirma.
    const pool = new pg.Pool({ connectionString: amb.url('app_runtime'), max: 1 });
    const chave = randomUUID();
    const antes = await residuo(chave);
    const trava = await travarNoLote();
    let chamadas = 0;
    let pendente: Promise<unknown> | undefined;
    try {
      const r = await comVigia(
        executarComando(
          pool,
          a.org,
          intencao(chave),
          async (c) => {
            chamadas += 1;
            const pid = (await c.query<{ pid: number }>('SELECT pg_backend_pid() AS pid')).rows[0]?.pid;
            try {
              await c.query('SELECT id FROM app.lot WHERE id = $1 FOR UPDATE', [a.lote]);
            } catch (falha) {
              let relogio: ReturnType<typeof setTimeout> | undefined;
              const caiu = new Promise<void>((fim, falhou) => {
                c.once('end', () => {
                  fim();
                });
                relogio = setTimeout(() => {
                  falhou(new Error('o backend não encerrou'));
                }, 3000);
              });
              await amb.app.query('SELECT pg_terminate_backend($1)', [pid]);
              await caiu.finally(() => {
                clearTimeout(relogio);
              });
              throw falha;
            }
            return nada;
          },
          { esperaChaveMs: ESPERA_MS },
        ),
        10 * ESPERA_MS,
      );
      pendente = r.marcado;
      expect(r.resultado).toMatchObject({ ok: false });
      const erro = (r.resultado as { erro: unknown }).erro;
      expect(chamadas).toBe(1);
      expect(erro).toBeInstanceOf(ErroComando);
      expect((erro as ErroComando).detalhe).toEqual({ resultadoIncerto: true, codigoPg: '55P03' });
      // Sem repetirEmMs no detalhe público, a web não põe Retry-After (rotas/resposta.ts).
      expect(respostaDeErro(erro, 'corr-rollback').corpo.detalhe).toEqual({ resultadoIncerto: true });
      expect([pool.totalCount, pool.idleCount, pool.waitingCount]).toEqual([0, 0, 0]);
      expect(await residuo(chave)).toEqual(antes);
    } finally {
      await trava.query('ROLLBACK').catch(() => undefined);
      trava.release();
      await pendente;
      await pool.end();
    }
  });

  it('outra falha do efeito com ROLLBACK confirmado (fora das classes 22, 40P01 e 55P03) segue transitória, sem repetirEmMs', async () => {
    const pool = new pg.Pool({ connectionString: amb.url('app_runtime'), max: 1 });
    try {
      const erro: unknown = await executarComando(pool, a.org, intencao(randomUUID()), async (c) => {
        await c.query('SELECT 1 FROM app.tabela_que_nao_existe');
        return nada;
      }).catch((e: unknown) => e);
      expect(erro).toBeInstanceOf(ErroComando);
      expect((erro as ErroComando).codigo).toBe('FALHA_TRANSITORIA');
      expect((erro as ErroComando).detalhe).toEqual({ resultadoIncerto: false, codigoPg: '42P01' });
      const resposta = respostaDeErro(erro, 'corr-42');
      expect(resposta.corpo.detalhe).toEqual({ resultadoIncerto: false });
      expect(falhaPermanenteSemGravacao(resposta.corpo)).toBe(false);
    } finally {
      await pool.end();
    }
  });

  it('classe 22 com ROLLBACK confirmado (1/0, 22012) é falha interna com o sinal, não transitória (CAD-01 §11.1)', async () => {
    const pool = new pg.Pool({ connectionString: amb.url('app_runtime'), max: 1 });
    try {
      const erro: unknown = await executarComando(pool, a.org, intencao(randomUUID()), async (c) => {
        await c.query('SELECT 1 / 0');
        return nada;
      }).catch((e: unknown) => e);
      expect(erro).toBeInstanceOf(ErroComando);
      expect((erro as ErroComando).codigo).toBe('FALHA_INTERNA');
      expect((erro as ErroComando).detalhe).toEqual({ resultadoIncerto: false, codigoPg: '22012' });
      expect(falhaPermanenteSemGravacao(respostaDeErro(erro, 'corr-22012').corpo)).toBe(true);
    } finally {
      await pool.end();
    }
  });

  it('classe 22 com ROLLBACK que não se confirma: resultado incerto, transitória, sem o sinal de falha permanente', async () => {
    // A guarda !incerto do ramo da classe 22: depois do 22P02 real, o backend da própria tentativa é encerrado antes de
    // o erro voltar ao envelope, e o ROLLBACK não se confirma. Nada pode ser dito sobre a gravação.
    const pool = new pg.Pool({ connectionString: amb.url('app_runtime'), max: 1 });
    const chave = randomUUID();
    const antes = await residuo(chave);
    let pendente: Promise<unknown> | undefined;
    try {
      const r = await comVigia(
        executarComando(pool, a.org, intencao(chave), async (c) => {
          const pid = (await c.query<{ pid: number }>('SELECT pg_backend_pid() AS pid')).rows[0]?.pid;
          try {
            await c.query("SELECT 'nao-e-numero'::int");
          } catch (falha) {
            let relogio: ReturnType<typeof setTimeout> | undefined;
            const caiu = new Promise<void>((fim, falhou) => {
              c.once('end', () => {
                fim();
              });
              relogio = setTimeout(() => {
                falhou(new Error('o backend não encerrou'));
              }, 3000);
            });
            await amb.app.query('SELECT pg_terminate_backend($1)', [pid]);
            await caiu.finally(() => {
              clearTimeout(relogio);
            });
            throw falha;
          }
          return nada;
        }),
        10 * ESPERA_MS,
      );
      pendente = r.marcado;
      expect(r.resultado).toMatchObject({ ok: false });
      const erro = (r.resultado as { erro: unknown }).erro;
      expect(erro).toBeInstanceOf(ErroComando);
      expect((erro as ErroComando).codigo).toBe('FALHA_TRANSITORIA');
      expect((erro as ErroComando).detalhe).toEqual({ resultadoIncerto: true, codigoPg: '22P02' });
      expect(falhaPermanenteSemGravacao(respostaDeErro(erro, 'corr-22-incerto').corpo)).toBe(false);
      expect([pool.totalCount, pool.idleCount, pool.waitingCount]).toEqual([0, 0, 0]);
      expect(await residuo(chave)).toEqual(antes);
    } finally {
      await pendente;
      await pool.end();
    }
  });
});
