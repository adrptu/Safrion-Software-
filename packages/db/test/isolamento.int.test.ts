import { randomUUID } from 'node:crypto';

import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { extratoDoLote, saldoDoLote } from '../src/estoque.js';
import { emOrganizacao } from '../src/sessao.js';
import { contagens, criarBanco, mover, semear, type Ambiente, type Semente } from './ambiente.js';

const HOJE = '2026-09-27';
let amb: Ambiente;
let a: Semente;
let b: Semente;

beforeAll(async () => {
  amb = await criarBanco();
  a = await semear(amb.app, 'A');
  b = await semear(amb.app, 'B');
  await mover(amb.app, a, 'a-1', 0, {
    tipo: 'entrada',
    quantidade: '60',
    unidade: 'L',
    situacao: 'quarentena_livre',
  });
  await mover(amb.app, a, 'a-2', 1, {
    tipo: 'mudanca',
    quantidade: '50',
    unidade: 'L',
    de: 'quarentena_livre',
    para: 'liberado_livre',
  });
});
afterAll(async () => {
  await amb.encerrar();
});

const estadoDeA = () =>
  emOrganizacao(amb.app, a.org, async (c) => ({
    saldo: await saldoDoLote(c, a.lote, HOJE),
    extrato: await extratoDoLote(c, a.lote),
  }));

describe('isolamento entre organizações (aceite técnico da F1)', () => {
  it('A vê o próprio saldo: 60 físicos, 50 utilizáveis e 10 em quarentena', async () => {
    const { saldo } = await estadoDeA();
    expect(saldo).toMatchObject({
      version: 2,
      fisico: '60.000000',
      utilizavel: '50.000000',
      quarentena: '10.000000',
    });
  });

  it('B não lê o lote de A pelo ID, na lista nem no extrato', async () => {
    await emOrganizacao(amb.app, b.org, async (c) => {
      expect(await saldoDoLote(c, a.lote, HOJE)).toBeNull();
      expect(await extratoDoLote(c, a.lote)).toEqual([]);
      const lotes = (await c.query<{ id: string }>('SELECT id FROM app.lot')).rows.map((l) => l.id);
      expect(lotes).toEqual([b.lote]);
      const busca = await c.query('SELECT 1 FROM app.lot WHERE code = $1', ['F26-A']);
      expect(busca.rowCount).toBe(0);
    });
  });

  it('movimento de B no lote de A é recusado como lote inexistente, sem alterar nada de A', async () => {
    const antes = await estadoDeA();
    const contagemA = await contagens(amb.app, a.org);
    const alheio = await mover(amb.app, { ...b, lote: a.lote }, 'b-invasao', 2, {
      tipo: 'entrada',
      quantidade: '5',
      unidade: 'L',
      situacao: 'liberado_livre',
    });
    const inexistente = await mover(amb.app, { ...b, lote: randomUUID() }, 'b-inexistente', 0, {
      tipo: 'entrada',
      quantidade: '5',
      unidade: 'L',
      situacao: 'liberado_livre',
    });
    expect(alheio.outcome).toBe('rejected');
    expect(alheio.reasonCode).toBe(inexistente.reasonCode);
    expect(alheio.reasonCode).toBe('LOTE_NAO_ENCONTRADO');
    expect(JSON.stringify(alheio)).not.toContain('F26-A');
    expect(await estadoDeA()).toEqual(antes);
    expect(await contagens(amb.app, a.org)).toEqual(contagemA);
  });

  it('B não cria lote apontando para produto de A: a chave composta impede', async () => {
    await expect(
      emOrganizacao(amb.app, b.org, (c) =>
        c.query(
          `INSERT INTO app.lot (id, organization_id, product_id, code, expiry_date, base_unit)
           VALUES ($1, $2, $3, 'X', '2027-01-01', 'L')`,
          [randomUUID(), b.org, a.produto],
        ),
      ),
    ).rejects.toMatchObject({ code: '23503' });
  });

  it('B não grava linha com a organização de A no conteúdo', async () => {
    await expect(
      emOrganizacao(amb.app, b.org, (c) =>
        c.query("INSERT INTO app.farm (id, organization_id, name) VALUES ($1, $2, 'Fazenda falsa')", [
          randomUUID(),
          a.org,
        ]),
      ),
    ).rejects.toMatchObject({ code: '42501' });
  });

  it('a mesma chave em organizações diferentes não compartilha recibo nem efeito', async () => {
    const ra = await mover(amb.app, a, 'mesma-chave', 2, {
      tipo: 'entrada',
      quantidade: '1',
      unidade: 'L',
      situacao: 'liberado_livre',
    });
    const rb = await mover(amb.app, b, 'mesma-chave', 0, {
      tipo: 'entrada',
      quantidade: '1',
      unidade: 'L',
      situacao: 'liberado_livre',
    });
    expect(ra.outcome).toBe('confirmed');
    expect(rb.outcome).toBe('confirmed');
    expect(rb.alreadyReceived).toBe(false);
    expect(rb.receiptId).not.toBe(ra.receiptId);
    expect(rb.effects['movements']).not.toEqual(ra.effects['movements']);
    const saldoB = await emOrganizacao(amb.app, b.org, (c) => saldoDoLote(c, b.lote, HOJE));
    expect(saldoB?.fisico).toBe('1.000000');
  });
});
