import { randomUUID } from 'node:crypto';

import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { listarLocais, listarProdutos, perfilDaSessao } from '../src/cadastros.js';
import { extratoDoLote, listarLotes } from '../src/estoque.js';
import { emOrganizacao } from '../src/sessao.js';
import { criarBanco, mover, semear, type Ambiente, type Semente } from './ambiente.js';

// Leituras das telas de Estoque e Cadastros (F0-c B2). Os valores esperados são escritos à mão a partir dos movimentos
// registrados, sem usar o domínio como oráculo.
const HOJE = '2026-09-28';
let amb: Ambiente;
let a: Semente;
let b: Semente;
let vencido: string;
let vazio: string;

beforeAll(async () => {
  amb = await criarBanco();
  a = await semear(amb.app, 'A');
  b = await semear(amb.app, 'B');
  vencido = randomUUID();
  vazio = randomUUID();
  await emOrganizacao(amb.app, a.org, async (c) => {
    await c.query(
      `INSERT INTO app.lot (id, organization_id, product_id, code, expiry_date, base_unit)
       VALUES ($1, $2, $3, 'A-VENCIDO', '2026-09-27', 'L'), ($4, $2, $3, 'A-VAZIO', '2027-01-31', 'L')`,
      [vencido, a.org, a.produto, vazio],
    );
  });
  // Lote da semente: 10 L liberados e 2,5 L em inspeção (2500 mL). Lote vencido ontem: 3 L que eram utilizáveis.
  await mover(amb.app, a, 'c-1', 0, {
    tipo: 'entrada',
    quantidade: '10',
    unidade: 'L',
    situacao: 'liberado_livre',
  });
  await mover(amb.app, a, 'c-2', 1, {
    tipo: 'entrada',
    quantidade: '2500',
    unidade: 'mL',
    situacao: 'quarentena_livre',
  });
  await mover(amb.app, { ...a, lote: vencido }, 'c-3', 0, {
    tipo: 'entrada',
    quantidade: '3',
    unidade: 'L',
    situacao: 'liberado_livre',
  });
  await mover(amb.app, b, 'c-4', 0, {
    tipo: 'entrada',
    quantidade: '7',
    unidade: 'L',
    situacao: 'liberado_livre',
  });
});
afterAll(async () => {
  await amb.encerrar();
});

describe('listarLotes', () => {
  it('lista só os lotes da organização, por produto e código, com o saldo de todos os locais', async () => {
    const lotes = await emOrganizacao(amb.app, a.org, (c) => listarLotes(c, HOJE));
    expect(lotes.map((l) => l.codigo)).toEqual(['A-VAZIO', 'A-VENCIDO', 'F26-A']);
    const [semEntrada, venc, doA] = lotes;
    expect(doA).toEqual({
      id: a.lote,
      codigo: 'F26-A',
      produtoId: a.produto,
      produto: 'Herbicida',
      validade: '2027-06-30',
      unidade: 'L',
      movimentos: 2,
      saldo: {
        version: 2,
        fisico: '12.500000',
        utilizavel: '10.000000',
        quarentena: '2.500000',
        bloqueado: '0.000000',
        vencido: '0.000000',
        loteVencido: false,
      },
    });
    expect(venc?.saldo).toMatchObject({
      fisico: '3.000000',
      utilizavel: '0.000000',
      vencido: '3.000000',
      loteVencido: true,
    });
    expect(venc?.movimentos).toBe(1);
    expect(semEntrada).toMatchObject({ movimentos: 0, saldo: { version: 0, fisico: '0.000000' } });
  });

  it('no último dia da validade o lote ainda vale', async () => {
    const [venc] = await emOrganizacao(amb.app, a.org, (c) =>
      listarLotes(c, '2026-09-27', { lote: vencido }),
    );
    expect(venc?.saldo).toMatchObject({ utilizavel: '3.000000', vencido: '0.000000', loteVencido: false });
  });

  it('filtra por lote e por produto; lote de outra organização e identificador inválido dão lista vazia', async () => {
    await emOrganizacao(amb.app, a.org, async (c) => {
      expect((await listarLotes(c, HOJE, { lote: a.lote })).map((l) => l.id)).toEqual([a.lote]);
      expect(await listarLotes(c, HOJE, { produto: a.produto })).toHaveLength(3);
      expect(await listarLotes(c, HOJE, { lote: b.lote })).toEqual([]);
      expect(await listarLotes(c, HOJE, { produto: b.produto })).toEqual([]);
      expect(await listarLotes(c, HOJE, { lote: 'nao-e-uuid' })).toEqual([]);
      expect(await listarLotes(c, HOJE, { produto: "' OR 1=1 --" })).toEqual([]);
    });
    const deB = await emOrganizacao(amb.app, b.org, (c) => listarLotes(c, HOJE));
    expect(deB.map((l) => [l.codigo, l.saldo.fisico])).toEqual([['F26-B', '7.000000']]);
  });
});

describe('extratoDoLote', () => {
  it('traz a situação de cada entrada e a quantidade original, na ordem das versões', async () => {
    const extrato = await emOrganizacao(amb.app, a.org, (c) => extratoDoLote(c, a.lote));
    expect(
      extrato.map((m) => [
        m.lotVersion,
        m.kind,
        m.situacao,
        m.de,
        m.para,
        m.originalQuantity,
        m.originalUnit,
        m.baseQuantity,
      ]),
    ).toEqual([
      [1, 'entrada', 'liberado_livre', null, null, '10', 'L', '10'],
      [2, 'entrada', 'quarentena_livre', null, null, '2500', 'mL', '2.5'],
    ]);
  });
});

describe('cadastros', () => {
  it('produtos com a contagem de lotes, só da organização', async () => {
    await emOrganizacao(amb.app, a.org, async (c) => {
      expect(await listarProdutos(c)).toEqual([{ id: a.produto, nome: 'Herbicida', unidade: 'L', lotes: 3 }]);
      expect(await listarProdutos(c, a.produto)).toHaveLength(1);
      expect(await listarProdutos(c, b.produto)).toEqual([]);
      expect(await listarProdutos(c, 'x')).toEqual([]);
    });
  });

  it('locais com a fazenda, só da organização', async () => {
    const locais = await emOrganizacao(amb.app, a.org, (c) => listarLocais(c));
    expect(locais).toEqual([{ id: a.local, nome: 'Almoxarifado', fazenda: 'Sede' }]);
  });

  it('perfil do usuário da sessão; usuário de outra organização não aparece', async () => {
    await emOrganizacao(amb.app, a.org, async (c) => {
      expect(await perfilDaSessao(c, a.usuario)).toEqual({
        usuario: 'Almoxarife A',
        organizacao: 'A',
        ficticia: false,
      });
      expect(await perfilDaSessao(c, b.usuario)).toBeNull();
      expect(await perfilDaSessao(c, 'x')).toBeNull();
    });
  });
});
