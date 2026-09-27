import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { executarComando, type Recibo } from '../src/comando.js';
import { ErroComando, RejeicaoNegocio } from '../src/erros.js';
import { saldoDoLote } from '../src/estoque.js';
import { emOrganizacao } from '../src/sessao.js';
import {
  contagens,
  criarBanco,
  intencaoMovimento,
  mover,
  semear,
  type Ambiente,
  type Semente,
} from './ambiente.js';

const HOJE = '2026-09-27';
const ENTRADA = { tipo: 'entrada', quantidade: '10', unidade: 'L', situacao: 'liberado_livre' } as const;
let amb: Ambiente;

beforeAll(async () => {
  amb = await criarBanco({ maxApp: 14 });
});
afterAll(async () => {
  await amb.encerrar();
});

const versaoDoLote = async (s: Semente) =>
  (await emOrganizacao(amb.app, s.org, (c) => saldoDoLote(c, s.lote, HOJE)))?.version;

const erroDe = async (p: Promise<unknown>): Promise<ErroComando> => {
  const e: unknown = await p.then(
    () => undefined,
    (x: unknown) => x,
  );
  expect(e).toBeInstanceOf(ErroComando);
  return e as ErroComando;
};

const semIndicador = (r: Recibo) =>
  Object.fromEntries(Object.entries(r).filter(([k]) => k !== 'alreadyReceived'));

describe('envelope de comando (73.3; IDEM-12 a IDEM-17; ENG-022)', () => {
  it('chave nova: efeito, registro, recibo, auditoria e outbox na mesma transação', async () => {
    const s = await semear(amb.app, 'Novo');
    const r = await mover(amb.app, s, 'k-1', 0, ENTRADA);
    expect(r).toMatchObject({
      outcome: 'confirmed',
      alreadyReceived: false,
      expectedVersion: 0,
      resultingVersion: 1,
    });
    expect(r.effects['movements']).toHaveLength(1);
    expect(r.effects['events']).toHaveLength(1);
    expect(await contagens(amb.app, s.org)).toEqual({ movimentos: 1, intencoes: 1, auditoria: 1, outbox: 1 });
    const auditoria = await emOrganizacao(amb.app, s.org, (c) =>
      c.query<{ actor_id: string; correlation_id: string; before_state: unknown; after_state: unknown }>(
        'SELECT actor_id, correlation_id, before_state, after_state FROM app.audit_log',
      ),
    );
    expect(auditoria.rows[0]).toMatchObject({
      actor_id: s.usuario,
      correlation_id: 'corr-k-1',
      before_state: { version: 0 },
    });
    const outbox = await emOrganizacao(amb.app, s.org, (c) =>
      c.query<{ causation_id: string; entity_version: string; previous_version: string }>(
        'SELECT causation_id, entity_version, previous_version FROM app.outbox',
      ),
    );
    expect(outbox.rows[0]).toEqual({ causation_id: 'k-1', entity_version: '1', previous_version: '0' });
  });

  it('reenvio equivalente devolve o mesmo recibo, marcado como já recebido, sem novo efeito', async () => {
    const s = await semear(amb.app, 'Reenvio');
    const original = await mover(amb.app, s, 'k-r', 0, ENTRADA);
    const reenvio = await mover(amb.app, s, 'k-r', 0, { ...ENTRADA, quantidade: '10.0' });
    expect(reenvio.alreadyReceived).toBe(true);
    expect(semIndicador(reenvio)).toEqual(semIndicador(original));
    expect(await contagens(amb.app, s.org)).toMatchObject({ movimentos: 1, intencoes: 1 });
    expect(await versaoDoLote(s)).toBe(1);
  });

  it('mesma chave com outro conteúdo: IDEMPOTENCY_KEY_REUSED e nada gravado; 1000 mL não é 1 L', async () => {
    const s = await semear(amb.app, 'Reuso');
    const original = await mover(amb.app, s, 'k-u', 0, { ...ENTRADA, quantidade: '1', unidade: 'L' });
    const antes = await contagens(amb.app, s.org);
    const e = await erroDe(mover(amb.app, s, 'k-u', 0, { ...ENTRADA, quantidade: '1000', unidade: 'mL' }));
    expect(e.codigo).toBe('IDEMPOTENCY_KEY_REUSED');
    expect(e.detalhe['receiptId']).toBe(original.receiptId);
    expect(await contagens(amb.app, s.org)).toEqual(antes);
  });

  it('chaves distintas com o mesmo conteúdo são dois recebimentos legítimos', async () => {
    const s = await semear(amb.app, 'Distintas');
    await mover(amb.app, s, 'k-d1', 0, ENTRADA);
    await mover(amb.app, s, 'k-d2', 1, ENTRADA);
    const saldo = await emOrganizacao(amb.app, s.org, (c) => saldoDoLote(c, s.lote, HOJE));
    expect(saldo?.fisico).toBe('20.000000');
  });

  it('10 envios simultâneos da mesma intenção, sobrepostos de fato, têm um único efeito', async () => {
    const s = await semear(amb.app, 'Concorrencia');
    const { intencao, efeito } = intencaoMovimento(s, 'k-c', 0, ENTRADA);
    let execucoes = 0;
    let maiorFila = 0;
    const lento: typeof efeito = async (c, ctx) => {
      execucoes++;
      // Prova de sobreposição pelo próprio banco: enquanto esta transação segura a chave, as outras 9 ficam
      // esperando o fim dela na inserção da mesma chave (trava não concedida sobre o ID desta transação).
      const xid = (await c.query<{ x: string }>('SELECT xid(pg_current_xact_id())::text AS x')).rows[0]?.x;
      const observar = (async () => {
        for (let i = 0; i < 40 && maiorFila < 9; i++) {
          const r = await amb.migrator.query<{ n: number }>(
            `SELECT count(*)::int n FROM pg_locks
              WHERE locktype = 'transactionid' AND NOT granted AND transactionid::text = $1`,
            [xid],
          );
          maiorFila = Math.max(maiorFila, r.rows[0]?.n ?? 0);
          await new Promise((ok) => setTimeout(ok, 25));
        }
      })();
      await observar;
      return efeito(c, ctx);
    };
    const recibos = await Promise.all(
      Array.from({ length: 10 }, () =>
        executarComando(amb.app, s.org, intencao, lento, { esperaChaveMs: 5000 }),
      ),
    );
    expect(maiorFila).toBe(9);
    expect(execucoes).toBe(1);
    expect(recibos.filter((r) => !r.alreadyReceived)).toHaveLength(1);
    expect(new Set(recibos.map((r) => r.receiptId)).size).toBe(1);
    expect(await contagens(amb.app, s.org)).toMatchObject({ movimentos: 1, intencoes: 1, outbox: 1 });
  });

  it('mesma chave com transação em curso além do limite: IDEMPOTENCY_IN_PROGRESS; depois, o recibo', async () => {
    const s = await semear(amb.app, 'Andamento');
    const { intencao, efeito } = intencaoMovimento(s, 'k-p', 0, ENTRADA);
    let liberar: () => void = () => undefined;
    const trava = new Promise<void>((ok) => (liberar = ok));
    let comecou: () => void = () => undefined;
    const iniciado = new Promise<void>((ok) => (comecou = ok));
    const primeiro = executarComando(amb.app, s.org, intencao, async (c, ctx) => {
      comecou();
      await trava;
      return efeito(c, ctx);
    });
    await iniciado;
    const e = await erroDe(executarComando(amb.app, s.org, intencao, efeito, { esperaChaveMs: 200 }));
    expect(e.codigo).toBe('IDEMPOTENCY_IN_PROGRESS');
    liberar();
    const r1 = await primeiro;
    const r2 = await executarComando(amb.app, s.org, intencao, efeito);
    expect(r2.alreadyReceived).toBe(true);
    expect(r2.receiptId).toBe(r1.receiptId);
  });

  it('conflito de versão é registrado sem efeito; o reenvio devolve o mesmo conflito sem reavaliar', async () => {
    const s = await semear(amb.app, 'Versao');
    await mover(amb.app, s, 'k-v1', 0, ENTRADA);
    const antes = await contagens(amb.app, s.org);
    const conflito = await mover(amb.app, s, 'k-v2', 0, ENTRADA);
    expect(conflito).toMatchObject({
      outcome: 'version_conflict',
      reasonCode: 'VERSAO_DESATUALIZADA',
      resultingVersion: 1,
      nextAction: 'Revisar diferenças',
    });
    expect(conflito.effects).toEqual({});
    const depois = await contagens(amb.app, s.org);
    expect(depois).toEqual({
      ...antes,
      intencoes: (antes['intencoes'] ?? 0) + 1,
      auditoria: (antes['auditoria'] ?? 0) + 1,
    });
    const reenvio = await mover(amb.app, s, 'k-v2', 0, ENTRADA);
    expect(semIndicador(reenvio)).toEqual(semIndicador(conflito));
    expect(reenvio.alreadyReceived).toBe(true);
    expect(await versaoDoLote(s)).toBe(1);
  });

  it('rejeição de negócio (saldo insuficiente, validação do domínio) é registrada sem efeito', async () => {
    const s = await semear(amb.app, 'Rejeicao');
    await mover(amb.app, s, 'k-j1', 0, ENTRADA);
    const r = await mover(amb.app, s, 'k-j2', 1, {
      tipo: 'mudanca',
      quantidade: '11',
      unidade: 'L',
      de: 'liberado_livre',
      para: 'liberado_bloqueado',
    });
    expect(r).toMatchObject({ outcome: 'rejected', reasonCode: 'SALDO_INSUFICIENTE' });
    const escala = await mover(amb.app, s, 'k-j3', 1, { ...ENTRADA, quantidade: '0.0000001' });
    expect(escala.reasonCode).toBe('QUANTIDADE_FORA_DA_ESCALA');
    expect(await contagens(amb.app, s.org)).toMatchObject({ movimentos: 1, outbox: 1 });
    expect(await versaoDoLote(s)).toBe(1);
  });

  it('rejeição depois de o efeito já ter gravado desfaz o que ele gravou (savepoint) e registra só o resultado', async () => {
    const s = await semear(amb.app, 'Parcial');
    const { intencao, efeito } = intencaoMovimento(s, 'k-parcial', 0, ENTRADA);
    const r = await executarComando(amb.app, s.org, intencao, async (c, ctx) => {
      await efeito(c, ctx);
      throw new RejeicaoNegocio(
        'ORDEM_REVOGADA',
        'A ordem foi revogada durante o processamento.',
        'Consultar a ordem',
      );
    });
    expect(r).toMatchObject({
      outcome: 'rejected',
      reasonCode: 'ORDEM_REVOGADA',
      nextAction: 'Consultar a ordem',
    });
    expect(r.effects).toEqual({});
    expect(await contagens(amb.app, s.org)).toEqual({ movimentos: 0, intencoes: 1, auditoria: 1, outbox: 0 });
    expect(await versaoDoLote(s)).toBe(0);
  });

  it('falha no meio (outbox recusada) desfaz tudo; nada fica registrado e o reenvio processa uma vez', async () => {
    const s = await semear(amb.app, 'Falha');
    const { intencao, efeito } = intencaoMovimento(s, 'k-f', 0, ENTRADA);
    const quebrado: typeof efeito = async (c, ctx) => {
      const r = await efeito(c, ctx);
      ctx.emitir({
        type: 'evento.invalido',
        schemaVersion: 0,
        entityType: 'lot',
        entityId: s.lote,
        entityVersion: 1,
        previousVersion: 0,
        payload: {},
      });
      return r;
    };
    const e = await erroDe(executarComando(amb.app, s.org, intencao, quebrado));
    expect(e.codigo).toBe('FALHA_TRANSITORIA');
    expect(await contagens(amb.app, s.org)).toEqual({ movimentos: 0, intencoes: 0, auditoria: 0, outbox: 0 });
    expect(await versaoDoLote(s)).toBe(0);
    const r = await executarComando(amb.app, s.org, intencao, efeito);
    expect(r.outcome).toBe('confirmed');
    expect(await contagens(amb.app, s.org)).toMatchObject({ movimentos: 1, intencoes: 1, outbox: 1 });
  });

  it('comando fora do contrato é recusado e nada é gravado', async () => {
    const s = await semear(amb.app, 'Contrato');
    const { intencao, efeito } = intencaoMovimento(s, 'k-x', 0, ENTRADA);
    const casos = [
      { ...intencao, idempotencyKey: '' },
      { ...intencao, idempotencyKey: 'x'.repeat(129) },
      { ...intencao, actorId: 'nao-e-uuid' },
      { ...intencao, data: { quantidade: 10.5 } },
      { ...intencao, target: { ...intencao.target, expectedVersion: -1 } },
    ];
    for (const caso of casos) {
      const e = await erroDe(executarComando(amb.app, s.org, caso, efeito));
      expect(e.codigo).toBe('CONTRATO_INVALIDO');
    }
    const semOrg = await erroDe(executarComando(amb.app, 'org-falsa', intencao, efeito));
    expect(semOrg.codigo).toBe('ORGANIZACAO_INVALIDA');
    expect(await contagens(amb.app, s.org)).toEqual({ movimentos: 0, intencoes: 0, auditoria: 0, outbox: 0 });
  });
});
