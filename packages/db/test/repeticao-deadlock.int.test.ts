import { randomUUID } from 'node:crypto';

import { canonizarRecebimento, criarRegistrador, type DadosRecebimento } from '@safrion/contracts';
import pg from 'pg';
import { afterAll, beforeAll, beforeEach, describe, expect, inject, it } from 'vitest';

import { consultarIntencao, executarComando, type Efeito, type Recibo } from '../src/comando.js';
import { ErroComando } from '../src/erros.js';
import { COMANDO_RECEBER_DOCUMENTO, receberDocumento } from '../src/recebimento.js';
import { emOrganizacao } from '../src/sessao.js';
import { contagens, criarBanco, semear, type Ambiente, type Semente } from './ambiente.js';

// Repetição por deadlock no envelope (contrato CMD-15 v3.8, §6) em PostgreSQL real, pelo app_runtime:
// - 40P01 INJETADO por gatilho na linha do documento (identificado como injeção; a sequência conta tentativas porque
//   nextval não volta no ROLLBACK), nos quatro casos da contraprova do Codex (d1dceea-retry);
// - um deadlock NATURAL entre duas transações reais, escolhido pelo detector do PostgreSQL;
// - transação encerrada e nenhum efeito tardio depois do prazo; ROLLBACK que não se confirma é incerto e não repete.
let amb: Ambiente;
let a: Semente;
let admin: pg.Client;
const fornecedor = randomUUID();
const linhasDoLog: Record<string, unknown>[] = [];
const registrador = criarRegistrador({
  servico: 'teste',
  versao: '0',
  escrever: (l) => linhasDoLog.push(JSON.parse(l) as Record<string, unknown>),
  agora: () => '2026-09-30T12:00:00.000Z',
});

beforeAll(async () => {
  amb = await criarBanco();
  a = await semear(amb.app, 'A');
  await emOrganizacao(amb.app, a.org, (c) =>
    c.query(
      "INSERT INTO app.counterparty (id, organization_id, name, identification) VALUES ($1, $2, 'Fornecedor', '11222333000181')",
      [fornecedor, a.org],
    ),
  );
  await amb.migrator.query('CREATE SEQUENCE app.teste_tentativas');
  await amb.migrator.query('GRANT USAGE, SELECT ON SEQUENCE app.teste_tentativas TO app_runtime');
  admin = new pg.Client({ connectionString: inject('urlAdmin') });
  await admin.connect();
});
afterAll(async () => {
  await admin.end();
  await amb.encerrar();
});
beforeEach(async () => {
  await amb.migrator.query('DROP TRIGGER IF EXISTS teste_falha ON app.receipt_line');
  await amb.migrator.query('DROP TRIGGER IF EXISTS teste_falha ON app.receipt_document');
  await amb.migrator.query('ALTER SEQUENCE app.teste_tentativas RESTART WITH 1');
});

/** Falha sintética na inserção da linha: as `ate` primeiras tentativas lançam `codigo`; depois, espera `dormirMs`. */
async function injetar(
  codigo: '40P01' | '23514',
  ate: number,
  dormirMs = 0,
  tabela: 'receipt_line' | 'receipt_document' = 'receipt_line',
) {
  await amb.migrator
    .query(`CREATE OR REPLACE FUNCTION app.teste_falha() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE n bigint;
    BEGIN
      n := nextval('app.teste_tentativas');
      IF n <= ${String(ate)} THEN RAISE EXCEPTION USING ERRCODE = '${codigo}', MESSAGE = 'injetado pelo teste'; END IF;
      IF ${String(dormirMs)} > 0 THEN PERFORM pg_sleep(${String(dormirMs)}::numeric / 1000); END IF;
      RETURN NEW;
    END $$`);
  await amb.migrator.query(
    `CREATE TRIGGER teste_falha BEFORE INSERT ON app.${tabela} FOR EACH ROW EXECUTE FUNCTION app.teste_falha()`,
  );
}
const tentativasNoBanco = async () =>
  Number(
    (await amb.migrator.query<{ n: string }>('SELECT last_value::text n FROM app.teste_tentativas')).rows[0]
      ?.n,
  );

async function fatos() {
  const base = await contagens(amb.app, a.org);
  const r = await emOrganizacao(amb.app, a.org, (c) =>
    c.query<{ documentos: number; linhas: number; lotes: number; versoes: string }>(
      `SELECT (SELECT count(*)::int FROM app.receipt_document) documentos,
              (SELECT count(*)::int FROM app.receipt_line) linhas,
              (SELECT count(*)::int FROM app.lot) lotes,
              (SELECT coalesce(sum(version), 0)::text FROM app.lot) versoes`,
    ),
  );
  const linha = r.rows[0];
  if (!linha) throw new Error('contagem sem linha');
  const n = (k: string) => base[k] ?? 0;
  return {
    movimentos: n('movimentos'),
    intencoes: n('intencoes'),
    auditoria: n('auditoria'),
    outbox: n('outbox'),
    ...linha,
  };
}

/** Transações abertas no banco do teste: depois de responder, nenhuma pode ter ficado pendurada. */
async function transacoesAbertas(): Promise<number> {
  const r = await admin.query<{ n: number }>(
    `SELECT count(*)::int n FROM pg_stat_activity
      WHERE datname = $1 AND pid <> pg_backend_pid() AND (state LIKE 'idle in transaction%' OR query LIKE '%pg_sleep%')`,
    [amb.banco],
  );
  return r.rows[0]?.n ?? -1;
}

const dados = (numero: string, ...lotes: string[]): DadosRecebimento => ({
  emitente: fornecedor,
  tipo: 'nfe',
  serie: '1',
  numero,
  emissao: '2026-09-29',
  recebimento: '2026-09-30',
  fazenda: a.fazenda,
  linhas: lotes.map((lote, i) => ({
    numero: i + 1,
    produto: a.produto,
    lote: { codigo: lote },
    validade: '2027-06-30',
    local: a.local,
    unidade: { tipo: 'medida', unidade: 'L' },
    documento: '10',
    parcelas: { apto: '10', quarentena: '0', bloqueado: '0', recusado: '0' },
  })),
});

async function receber(
  chave: string,
  d: DadosRecebimento,
  documentoId: string = randomUUID(),
): Promise<Recibo | ErroComando> {
  const canonico = canonizarRecebimento(d);
  try {
    return await executarComando(
      amb.app,
      a.org,
      {
        commandType: COMANDO_RECEBER_DOCUMENTO,
        idempotencyKey: chave,
        initiatorKind: 'web',
        actorId: a.usuario,
        target: { type: 'receipt_document', id: documentoId, expectedVersion: 0 },
        data: canonico,
        correlationId: `corr-${chave}`,
      },
      receberDocumento(canonico),
      { registrador },
    );
  } catch (e) {
    if (e instanceof ErroComando) return e;
    throw e;
  }
}
const logDe = (chave: string) => linhasDoLog.filter((l) => l['idempotency_key'] === chave);

describe('deadlock injetado (40P01 por gatilho): os quatro casos da contraprova', () => {
  it('na primeira tentativa: a segunda confirma uma vez, com a mesma chave, sem resíduo da primeira', async () => {
    await injetar('40P01', 1);
    const antes = await fatos();
    const r = await receber('dl-uma', dados('9101', 'DL-UMA'));
    expect(r).toMatchObject({ outcome: 'confirmed', idempotencyKey: 'dl-uma', alreadyReceived: false });
    expect(await tentativasNoBanco()).toBe(2);
    expect(await fatos()).toMatchObject({
      documentos: antes.documentos + 1,
      linhas: antes.linhas + 1,
      lotes: antes.lotes + 1,
      intencoes: antes.intencoes + 1,
      auditoria: antes.auditoria + 1,
      movimentos: antes.movimentos + 1,
    });
    const recuperado = await emOrganizacao(amb.app, a.org, (c) =>
      consultarIntencao(c, {
        commandType: COMANDO_RECEBER_DOCUMENTO,
        idempotencyKey: 'dl-uma',
        actorId: a.usuario,
      }),
    );
    expect(recuperado).toEqual({ ...(r as Recibo), alreadyReceived: true });
    expect(logDe('dl-uma')).toEqual([
      expect.objectContaining({ evento: 'comando.processado', tentativas: 2 }),
    ]);
  });

  it('persistente: exatamente três tentativas, falha transitória sem incerteza e nada gravado, dentro do prazo', async () => {
    await injetar('40P01', 999);
    const antes = await fatos();
    const inicio = performance.now();
    const e = await receber('dl-tres', dados('9102', 'DL-TRES'));
    const decorrido = performance.now() - inicio;
    expect(e).toBeInstanceOf(ErroComando);
    expect((e as ErroComando).codigo).toBe('FALHA_TRANSITORIA');
    expect((e as ErroComando).detalhe).toMatchObject({ resultadoIncerto: false, codigoPg: '40P01' });
    expect(await tentativasNoBanco()).toBe(3);
    expect(decorrido).toBeLessThan(2000);
    expect(await fatos()).toEqual(antes);
    expect(logDe('dl-tres')).toEqual([
      expect.objectContaining({
        evento: 'comando.falhou',
        tentativas: 3,
        codigo_pg: '40P01',
        resultado_incerto: false,
      }),
    ]);
  });

  it('outro SQLSTATE (23514) não repete: uma tentativa e nada gravado', async () => {
    await injetar('23514', 999);
    const antes = await fatos();
    const e = await receber('dl-nao', dados('9103', 'DL-NAO'));
    expect((e as ErroComando).detalhe).toMatchObject({ resultadoIncerto: false, codigoPg: '23514' });
    expect(await tentativasNoBanco()).toBe(1);
    expect(await fatos()).toEqual(antes);
  });

  it('a segunda tentativa passa do prazo: é cancelada e revertida; transação encerrada e nenhum efeito tardio', async () => {
    await injetar('40P01', 1, 3000);
    const antes = await fatos();
    const inicio = performance.now();
    const e = await receber('dl-prazo', dados('9104', 'DL-PRAZO'));
    const decorrido = performance.now() - inicio;
    expect((e as ErroComando).codigo).toBe('FALHA_TRANSITORIA');
    // Cancelada pelo statement_timeout do tempo restante (57014), com o ROLLBACK confirmado.
    expect((e as ErroComando).detalhe).toMatchObject({ resultadoIncerto: false, codigoPg: '57014' });
    expect(await tentativasNoBanco()).toBe(2);
    expect(decorrido).toBeGreaterThanOrEqual(1900);
    expect(decorrido).toBeLessThan(2400);
    expect(await transacoesAbertas()).toBe(0);
    expect(await fatos()).toEqual(antes);
    // Depois de passar o tempo em que o gatilho teria terminado, nada apareceu.
    await new Promise((fim) => setTimeout(fim, 3500));
    expect(await transacoesAbertas()).toBe(0);
    expect(await fatos()).toEqual(antes);
  }, 15_000);
});

describe('rejeição depois de repetir (CX-R02)', () => {
  it('40P01 na 1ª tentativa e origem já recebida na 2ª: recibo rejeitado, recuperável, idempotente e sem estoque extra', async () => {
    expect(await receber('dl-origem', dados('9106', 'DL-ORIGEM'))).toMatchObject({ outcome: 'confirmed' });
    await injetar('40P01', 1, 0, 'receipt_document');
    const antes = await fatos();
    const doc = randomUUID();
    const r = await receber('dl-duplicada', dados('9106', 'DL-ORIGEM'), doc);
    expect(r).toMatchObject({
      outcome: 'rejected',
      reasonCode: 'DOCUMENTO_JA_RECEBIDO',
      alreadyReceived: false,
    });
    expect(await tentativasNoBanco()).toBe(2);
    const depois = await fatos();
    // Só o registro da intenção e a auditoria da rejeição; nenhum documento, linha, lote, versão ou movimento.
    expect(depois).toEqual({ ...antes, intencoes: antes.intencoes + 1, auditoria: antes.auditoria + 1 });
    const recuperado = await emOrganizacao(amb.app, a.org, (c) =>
      consultarIntencao(c, {
        commandType: COMANDO_RECEBER_DOCUMENTO,
        idempotencyKey: 'dl-duplicada',
        actorId: a.usuario,
      }),
    );
    expect(recuperado).toEqual({ ...(r as Recibo), alreadyReceived: true });
    expect(await receber('dl-duplicada', dados('9106', 'DL-ORIGEM'), doc)).toEqual({
      ...(r as Recibo),
      alreadyReceived: true,
    });
    expect(await fatos()).toEqual(depois);
  });
});

describe('prazo da repetição: a soma de comandos não passa dele', () => {
  it('três comandos de 800 ms na segunda tentativa: o terceiro é cortado no prazo, sem efeito', async () => {
    await injetar('40P01', 1, 800);
    const antes = await fatos();
    const inicio = performance.now();
    const e = await receber('dl-soma', dados('9105', 'DL-SOMA-1', 'DL-SOMA-2', 'DL-SOMA-3'));
    const decorrido = performance.now() - inicio;
    expect((e as ErroComando).codigo).toBe('FALHA_TRANSITORIA');
    expect((e as ErroComando).detalhe['resultadoIncerto']).toBe(false);
    // Cortado pelo servidor (57014) ou barrado antes de começar (prazo esgotado, sem SQLSTATE).
    expect(['57014', undefined]).toContain((e as ErroComando).detalhe['codigoPg']);
    // Com um só statement_timeout por tentativa, os três terminariam (~2,5 s) e só o COMMIT seria barrado.
    expect(decorrido).toBeLessThan(2300);
    expect(await transacoesAbertas()).toBe(0);
    expect(await fatos()).toEqual(antes);
  }, 15_000);
});

describe('deadlock natural e limites da repetição', () => {
  it('duas transações reais em ordem oposta: o PostgreSQL escolhe a vítima, que repete e confirma', async () => {
    const [x, y] = [randomUUID(), randomUUID()];
    await emOrganizacao(amb.app, a.org, (c) =>
      c.query(
        `INSERT INTO app.lot (id, organization_id, product_id, code, expiry_date, base_unit)
         VALUES ($1, $3, $4, 'NAT-X', '2027-06-30', 'L'), ($2, $3, $4, 'NAT-Y', '2027-06-30', 'L')`,
        [x, y, a.org, a.produto],
      ),
    );
    let chegaram = 0;
    let liberar: () => void = () => undefined;
    const ambos = new Promise<void>((r) => {
      liberar = r;
    });
    // Primeira tentativa: trava o primeiro lote, espera a outra travar o dela e pede o segundo. Repetições seguem direto.
    const efeito =
      (primeiro: string, segundo: string): Efeito =>
      async (c) => {
        await c.query('SELECT id FROM app.lot WHERE id = $1 FOR UPDATE', [primeiro]);
        chegaram += 1;
        if (chegaram === 2) liberar();
        await ambos;
        await c.query('SELECT id FROM app.lot WHERE id = $1 FOR UPDATE', [segundo]);
        return { resultingVersion: null, effects: {} };
      };
    const intencao = (chave: string, alvo: string) => ({
      commandType: 'TESTE-DEADLOCK',
      idempotencyKey: chave,
      initiatorKind: 'web' as const,
      actorId: a.usuario,
      target: { type: 'lot', id: alvo },
      data: { chave },
      correlationId: `corr-${chave}`,
    });
    const [r1, r2] = await Promise.all([
      executarComando(amb.app, a.org, intencao('nat-xy', x), efeito(x, y), { registrador }),
      executarComando(amb.app, a.org, intencao('nat-yx', y), efeito(y, x), { registrador }),
    ]);
    expect([r1.outcome, r2.outcome]).toEqual(['confirmed', 'confirmed']);
    const tentativas = [...logDe('nat-xy'), ...logDe('nat-yx')].map((l) => l['tentativas']).sort();
    expect(tentativas).toEqual([1, 2]);
    expect(await transacoesAbertas()).toBe(0);
  }, 15_000);

  it('código 40P01 que não veio do PostgreSQL não repete', async () => {
    let chamadas = 0;
    const e = await executarComando(
      amb.app,
      a.org,
      {
        commandType: 'TESTE-DEADLOCK',
        idempotencyKey: 'falso-40p01',
        initiatorKind: 'web',
        actorId: a.usuario,
        target: { type: 'lot', id: a.lote },
        data: {},
        correlationId: 'corr-falso',
      },
      () => {
        chamadas += 1;
        throw Object.assign(new Error('não é do banco'), { code: '40P01' });
      },
    ).catch((x: unknown) => x);
    expect(e).toBeInstanceOf(ErroComando);
    expect(chamadas).toBe(1);
  });

  it('ROLLBACK que não se confirma (conexão encerrada) é incerto e não repete', async () => {
    let chamadas = 0;
    const e = await executarComando(
      amb.app,
      a.org,
      {
        commandType: 'TESTE-DEADLOCK',
        idempotencyKey: 'conexao-caiu',
        initiatorKind: 'web',
        actorId: a.usuario,
        target: { type: 'lot', id: a.lote },
        data: {},
        correlationId: 'corr-caiu',
      },
      async (c) => {
        chamadas += 1;
        await c.query('SELECT pg_terminate_backend(pg_backend_pid())');
        return { resultingVersion: null, effects: {} };
      },
    ).catch((x: unknown) => x);
    expect((e as ErroComando).codigo).toBe('FALHA_TRANSITORIA');
    expect((e as ErroComando).detalhe['resultadoIncerto']).toBe(true);
    expect((e as ErroComando).message).not.toMatch(/nada foi gravado/);
    expect(chamadas).toBe(1);
  });
});
