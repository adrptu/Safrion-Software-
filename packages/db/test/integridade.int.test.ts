// Regressões da revisão do Codex sobre 2801324 (achados 1 a 3), reproduzidas antes da correção.
import { randomUUID } from 'node:crypto';

import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { executarComando } from '../src/comando.js';
import { ErroComando } from '../src/erros.js';
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
let amb: Ambiente;
beforeAll(async () => {
  amb = await criarBanco();
});
afterAll(async () => {
  await amb.encerrar();
});

/** Segundo local de estoque na mesma fazenda da semente. */
async function outroLocal(s: Semente): Promise<Semente> {
  const local = randomUUID();
  await emOrganizacao(amb.app, s.org, (c) =>
    c.query(
      "INSERT INTO app.stock_location (id, organization_id, farm_id, name) VALUES ($1, $2, $3, 'Galpão B')",
      [local, s.org, s.fazenda],
    ),
  );
  return { ...s, local };
}

const saldo = (s: Semente, local?: string) =>
  emOrganizacao(amb.app, s.org, (c) => saldoDoLote(c, s.lote, HOJE, local));

describe('achado 1: saldo por local, sem quebrar o saldo agregado do lote', () => {
  it('mudança num local vazio não usa o saldo de outro local', async () => {
    const a = await semear(amb.app, 'LocalMud');
    const b = await outroLocal(a);
    await mover(amb.app, a, 'l-e', 0, {
      tipo: 'entrada',
      quantidade: '10',
      unidade: 'L',
      situacao: 'liberado_livre',
    });
    const r = await mover(amb.app, b, 'l-m', 1, {
      tipo: 'mudanca',
      quantidade: '10',
      unidade: 'L',
      de: 'liberado_livre',
      para: 'liberado_bloqueado',
    });
    expect(r).toMatchObject({ outcome: 'rejected', reasonCode: 'SALDO_INSUFICIENTE' });
    expect((await saldo(a, a.local))?.bloqueado).toBe('0.000000');
  });

  it('estorno só vale no local do movimento estornado', async () => {
    const a = await semear(amb.app, 'LocalEst');
    const b = await outroLocal(a);
    const entrada = await mover(amb.app, a, 'e-e', 0, {
      tipo: 'entrada',
      quantidade: '10',
      unidade: 'L',
      situacao: 'liberado_livre',
    });
    const estornada = entrada.effects['movements']?.[0] ?? '';
    const noOutroLocal = await mover(amb.app, b, 'e-b', 1, { tipo: 'estorno', estornaId: estornada });
    expect(noOutroLocal).toMatchObject({ outcome: 'rejected', reasonCode: 'ESTORNO_INVALIDO' });
    const noMesmoLocal = await mover(amb.app, a, 'e-a', 1, { tipo: 'estorno', estornaId: estornada });
    expect(noMesmoLocal.outcome).toBe('confirmed');
    expect((await saldo(a))?.fisico).toBe('0.000000');
  });

  it('o banco recusa estorno gravado em local diferente do original, mesmo por fora do envelope', async () => {
    const a = await semear(amb.app, 'LocalFk');
    const b = await outroLocal(a);
    const entrada = await mover(amb.app, a, 'f-e', 0, {
      tipo: 'entrada',
      quantidade: '3',
      unidade: 'L',
      situacao: 'liberado_livre',
    });
    await expect(
      emOrganizacao(amb.migrator, a.org, (c) =>
        c.query(
          `INSERT INTO app.stock_movement (id, organization_id, lot_id, location_id, kind, reverses_id, lot_version,
             intent_command_type, intent_key, actor_id)
           VALUES ($1, $2, $3, $4, 'estorno', $5, 2, 'TESTE', 'f-x', $6)`,
          [randomUUID(), a.org, a.lote, b.local, entrada.effects['movements']?.[0], a.usuario],
        ),
      ),
    ).rejects.toMatchObject({ code: '23503' });
  });

  it('saldo por local e saldo agregado do lote conferem entre si', async () => {
    const a = await semear(amb.app, 'LocalSoma');
    const b = await outroLocal(a);
    await mover(amb.app, a, 's-a', 0, {
      tipo: 'entrada',
      quantidade: '10',
      unidade: 'L',
      situacao: 'liberado_livre',
    });
    await mover(amb.app, b, 's-b', 1, {
      tipo: 'entrada',
      quantidade: '4',
      unidade: 'L',
      situacao: 'quarentena_livre',
    });
    await mover(amb.app, a, 's-m', 2, {
      tipo: 'mudanca',
      quantidade: '6',
      unidade: 'L',
      de: 'liberado_livre',
      para: 'liberado_bloqueado',
    });
    expect(await saldo(a, a.local)).toMatchObject({
      fisico: '10.000000',
      utilizavel: '4.000000',
      bloqueado: '6.000000',
    });
    expect(await saldo(b, b.local)).toMatchObject({ fisico: '4.000000', quarentena: '4.000000' });
    expect(await saldo(a)).toMatchObject({
      version: 3,
      fisico: '14.000000',
      utilizavel: '4.000000',
      quarentena: '4.000000',
      bloqueado: '6.000000',
    });
  });
});

describe('achado 2: quantidade e unidade obrigatórias no movimento, conforme o tipo', () => {
  const base = (s: Semente) => [randomUUID(), s.org, s.lote, s.local, s.usuario];
  const inserir = (s: Semente, colunas: string, valores: string) =>
    emOrganizacao(amb.migrator, s.org, (c) =>
      c.query(
        `INSERT INTO app.stock_movement (id, organization_id, lot_id, location_id, actor_id, lot_version,
           intent_command_type, intent_key, ${colunas})
         VALUES ($1, $2, $3, $4, $5, 9, 'TESTE', '${randomUUID()}', ${valores})`,
        base(s),
      ),
    );

  it('entrada e mudança sem quantidade ou sem unidade são recusadas pelo banco', async () => {
    const s = await semear(amb.app, 'Nulos');
    const casos: [string, string][] = [
      [
        'kind, situation, original_quantity, original_unit, base_quantity, base_unit',
        "'entrada', 'liberado_livre', 1, 'L', NULL, 'L'",
      ],
      [
        'kind, situation, original_quantity, original_unit, base_quantity, base_unit',
        "'entrada', 'liberado_livre', NULL, 'L', 1, 'L'",
      ],
      [
        'kind, situation, original_quantity, original_unit, base_quantity, base_unit',
        "'entrada', 'liberado_livre', 1, NULL, 1, 'L'",
      ],
      [
        'kind, situation, original_quantity, original_unit, base_quantity, base_unit',
        "'entrada', 'liberado_livre', 1, 'L', 1, NULL",
      ],
      [
        'kind, from_situation, to_situation, original_quantity, original_unit, base_quantity, base_unit',
        "'mudanca', 'liberado_livre', 'liberado_bloqueado', 1, 'L', NULL, 'L'",
      ],
      [
        'kind, from_situation, to_situation, original_quantity, original_unit, base_quantity, base_unit',
        "'mudanca', 'liberado_livre', 'liberado_bloqueado', 1, 'L', 1, NULL",
      ],
    ];
    for (const [colunas, valores] of casos) {
      await expect(inserir(s, colunas, valores), valores).rejects.toMatchObject({ code: '23514' });
    }
  });

  it('estorno não carrega quantidade nem unidade', async () => {
    const s = await semear(amb.app, 'EstornoUnidade');
    const r = await mover(amb.app, s, 'u-e', 0, {
      tipo: 'entrada',
      quantidade: '2',
      unidade: 'L',
      situacao: 'liberado_livre',
    });
    await expect(
      inserir(s, 'kind, reverses_id, base_unit', `'estorno', '${r.effects['movements']?.[0] ?? ''}', 'L'`),
    ).rejects.toMatchObject({ code: '23514' });
  });
});

describe('achado 3: falha transitória não afirma "nada gravado" quando a confirmação ficou incerta', () => {
  it('erro antes do COMMIT: nada gravado, e a resposta diz isso', async () => {
    const s = await semear(amb.app, 'AntesCommit');
    const { intencao } = intencaoMovimento(s, 't-a', 0, {
      tipo: 'entrada',
      quantidade: '1',
      unidade: 'L',
      situacao: 'liberado_livre',
    });
    const e: unknown = await executarComando(amb.app, s.org, intencao, () => {
      throw new Error('falha de infraestrutura simulada');
    }).catch((x: unknown) => x);
    expect(e).toBeInstanceOf(ErroComando);
    expect((e as ErroComando).codigo).toBe('FALHA_TRANSITORIA');
    expect((e as ErroComando).detalhe['resultadoIncerto']).toBe(false);
    expect((e as ErroComando).message).toMatch(/nada foi gravado/);
    expect(await contagens(amb.app, s.org)).toEqual({ movimentos: 0, intencoes: 0, auditoria: 0, outbox: 0 });
  });

  it('erro no próprio COMMIT: resultado incerto, sem afirmar que nada foi gravado; o reenvio resolve', async () => {
    const s = await semear(amb.app, 'NoCommit');
    // Gatilho adiado: só dispara no COMMIT, depois de toda a transação já ter sido enviada.
    await emOrganizacao(amb.migrator, s.org, async (c) => {
      await c.query(`CREATE OR REPLACE FUNCTION app.falhar_no_commit() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN IF NEW.causation_id = 't-c' AND NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'liberar_commit')
          THEN RAISE EXCEPTION 'falha simulada no commit'; END IF; RETURN NEW; END $$`);
      await c.query(`CREATE CONSTRAINT TRIGGER falhar_no_commit AFTER INSERT ON app.outbox
        DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION app.falhar_no_commit()`);
    });
    const pedido = intencaoMovimento(s, 't-c', 0, {
      tipo: 'entrada',
      quantidade: '1',
      unidade: 'L',
      situacao: 'liberado_livre',
    });
    const e: unknown = await executarComando(amb.app, s.org, pedido.intencao, pedido.efeito).catch(
      (x: unknown) => x,
    );
    expect((e as ErroComando).codigo).toBe('FALHA_TRANSITORIA');
    expect((e as ErroComando).detalhe['resultadoIncerto']).toBe(true);
    expect((e as ErroComando).message).not.toMatch(/nada foi gravado/);
    await amb.migrator.query('CREATE TABLE public.liberar_commit ()');
    const r = await executarComando(amb.app, s.org, pedido.intencao, pedido.efeito);
    expect(r.outcome).toBe('confirmed');
    expect(await contagens(amb.app, s.org)).toMatchObject({ movimentos: 1, intencoes: 1 });
  });
});
