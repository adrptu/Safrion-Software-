import { randomUUID } from 'node:crypto';

import {
  COMANDOS_CADASTRO,
  EsquemaDadosAlterarSituacaoTalhao,
  EsquemaDadosCriarFazenda,
  EsquemaDadosCriarTalhao,
  EsquemaDadosEditarFazenda,
  EsquemaDadosEditarTalhao,
} from '@safrion/contracts';
import type { PoolClient } from 'pg';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import {
  alterarSituacaoTalhao,
  criarFazenda,
  criarTalhao,
  editarFazenda,
  editarTalhao,
  listarFazendas,
  listarTalhoes,
  obterFazenda,
  obterTalhao,
  opcoesFazenda,
} from '../src/cadastros-agricolas.js';
import { executarComando, type Efeito, type Recibo } from '../src/comando.js';
import { ErroComando } from '../src/erros.js';
import { emOrganizacao } from '../src/sessao.js';
import { criarBanco, semear, type Ambiente, type Semente } from './ambiente.js';

// Cadastros agrícolas, incremento 1 (contrato CAD-01 v3, §3, §4 e §9), em PostgreSQL real com app_runtime sem
// BYPASSRLS: comandos pelo envelope, leituras por emOrganizacao, recusas registradas sem efeito.
let amb: Ambiente;
let a: Semente;
let b: Semente;

beforeAll(async () => {
  amb = await criarBanco();
  a = await semear(amb.app, 'CadA');
  b = await semear(amb.app, 'CadB');
});
afterAll(async () => {
  await amb.encerrar();
});

type Alvo = { type: 'farm' | 'field'; id: string; expectedVersion: number };

function rodar(
  s: Semente,
  commandType: string,
  target: Alvo,
  data: unknown,
  efeito: Efeito,
  chave: string = randomUUID(),
) {
  return executarComando(
    amb.app,
    s.org,
    {
      commandType,
      idempotencyKey: chave,
      initiatorKind: 'web',
      actorId: s.usuario,
      target,
      data,
      correlationId: `corr-${chave}`,
    },
    efeito,
  );
}

async function novaFazenda(
  s: Semente,
  nome: string,
  chave?: string,
): Promise<{ id: string; recibo: Recibo }> {
  const id = randomUUID();
  const dados = EsquemaDadosCriarFazenda.parse({ nome, fuso: 'America/Sao_Paulo' });
  const recibo = await rodar(
    s,
    COMANDOS_CADASTRO.criarFazenda,
    { type: 'farm', id, expectedVersion: 0 },
    dados,
    criarFazenda(dados),
    chave,
  );
  return { id, recibo };
}

async function novoTalhao(
  s: Semente,
  fazenda: string,
  nome: string,
  area = '204',
  opcoes: { id?: string; chave?: string } = {},
): Promise<{ id: string; recibo: Recibo }> {
  const id = opcoes.id ?? randomUUID();
  const dados = EsquemaDadosCriarTalhao.parse({ fazenda, nome, areaDeclaradaHa: area });
  const recibo = await rodar(
    s,
    COMANDOS_CADASTRO.criarTalhao,
    { type: 'field', id, expectedVersion: 0 },
    dados,
    criarTalhao(dados),
    opcoes.chave,
  );
  return { id, recibo };
}

function editar(s: Semente, id: string, versao: number, bruto: unknown) {
  const dados = EsquemaDadosEditarTalhao.parse(bruto);
  return rodar(
    s,
    COMANDOS_CADASTRO.editarTalhao,
    { type: 'field', id, expectedVersion: versao },
    dados,
    editarTalhao(dados),
  );
}

function situacao(s: Semente, id: string, versao: number, valor: 'ativo' | 'inativo') {
  const dados = EsquemaDadosAlterarSituacaoTalhao.parse({ situacao: valor });
  return rodar(
    s,
    COMANDOS_CADASTRO.alterarSituacaoTalhao,
    { type: 'field', id, expectedVersion: versao },
    dados,
    alterarSituacaoTalhao(dados),
  );
}

const naOrg = <T>(s: Semente, f: (c: PoolClient) => Promise<T>) => emOrganizacao(amb.app, s.org, f);

async function contar(s: Semente, sql: string, params: unknown[] = []): Promise<number> {
  const r = await naOrg(s, (c) => c.query<{ n: string }>(sql, params));
  return Number(r.rows[0]?.n);
}

describe('criar fazenda e talhão (jornada AC-72-12)', () => {
  it('cria, emite outbox e auditoria, e as leituras mostram a área declarada como referência', async () => {
    const f = await novaFazenda(a, ' Fazenda  Boa Vista ');
    expect(f.recibo).toMatchObject({ outcome: 'confirmed', resultingVersion: 1, alreadyReceived: false });
    const t = await novoTalhao(a, f.id, 'T1', '204.50');
    expect(t.recibo).toMatchObject({
      outcome: 'confirmed',
      resultingVersion: 1,
      effects: { fields: [t.id] },
    });

    expect(await contar(a, 'SELECT count(*)::text n FROM app.outbox WHERE entity_id = $1', [t.id])).toBe(1);
    expect(await contar(a, 'SELECT count(*)::text n FROM app.audit_log WHERE target_id = $1', [t.id])).toBe(
      1,
    );

    const talhao = await naOrg(a, (c) => obterTalhao(c, t.id));
    expect(talhao).toMatchObject({
      nome: 'T1',
      fazenda: { id: f.id, nome: 'Fazenda Boa Vista' },
      areaReferenciaHa: '204.500000',
      origemArea: 'declarada',
      areaDeclaradaHa: '204.500000',
      limite: null,
      situacao: 'ativo',
      versao: 1,
      atualizadoEm: null,
    });
    const fazendas = await naOrg(a, (c) => listarFazendas(c));
    // A fazenda da semente ("Sede") não tem talhão e aparece como grupo vazio (contrato §2).
    expect(fazendas.map((x) => [x.nome, x.talhoesAtivos, x.areaAtivaHa, x.fuso, x.versao])).toEqual([
      ['Fazenda Boa Vista', 1, '204.500000', 'America/Sao_Paulo', 1],
      ['Sede', 0, '0.000000', 'America/Sao_Paulo', 1],
    ]);
    expect((await naOrg(a, (c) => opcoesFazenda(c))).map((x) => x.nome)).toEqual([
      'Fazenda Boa Vista',
      'Sede',
    ]);
    expect((await naOrg(a, (c) => listarTalhoes(c, { fazenda: f.id }))).map((x) => x.id)).toEqual([t.id]);
    expect(await naOrg(a, (c) => listarTalhoes(c, { fazenda: 'nao-e-uuid' }))).toEqual([]);
  });

  it('repetir a chave devolve o recibo sem duplicar; mesma chave com outro conteúdo é recusada', async () => {
    const chave = randomUUID();
    const id = randomUUID();
    const primeiro = await novoTalhao(a, a.fazenda, 'Repetido', '10', { id, chave });
    const segundo = await novoTalhao(a, a.fazenda, 'Repetido', '10.0', { id, chave });
    expect(primeiro.recibo.outcome).toBe('confirmed');
    expect(segundo.recibo).toMatchObject({
      outcome: 'confirmed',
      alreadyReceived: true,
      receiptId: primeiro.recibo.receiptId,
    });
    expect(await contar(a, 'SELECT count(*)::text n FROM app.field WHERE id = $1', [id])).toBe(1);
    const erro: unknown = await novoTalhao(a, a.fazenda, 'Outro nome', '10', { id, chave }).catch(
      (e: unknown) => e,
    );
    expect(erro).toBeInstanceOf(ErroComando);
    expect((erro as ErroComando).codigo).toBe('IDEMPOTENCY_KEY_REUSED');
  });
});

describe('recusas pelo banco, nunca 500 (contrato §3)', () => {
  it('nome ativo repetido na mesma fazenda, inclusive por caixa e espaço Unicode, é NOME_EM_USO; em outra fazenda passa', async () => {
    await novoTalhao(a, a.fazenda, 'Talhão Norte');
    const dup = await novoTalhao(a, a.fazenda, '  TALHÃO norte ');
    expect(dup.recibo).toMatchObject({
      outcome: 'rejected',
      reasonCode: 'NOME_EM_USO',
      // O motivo em pt-BR vai no nextAction: é o que a tela mostra (contrato §4).
      nextAction:
        'Já existe um talhão ativo com este nome nesta fazenda. Use outro nome ou inative o outro talhão.',
    });
    expect(await contar(a, 'SELECT count(*)::text n FROM app.field WHERE id = $1', [dup.id])).toBe(0);
    const outra = await novaFazenda(a, 'Fazenda Sul');
    expect((await novoTalhao(a, outra.id, 'Talhão Norte')).recibo.outcome).toBe('confirmed');
  });

  it('duas criações concorrentes com o mesmo nome: uma confirma, a outra é NOME_EM_USO', async () => {
    const [x, y] = await Promise.all([
      novoTalhao(a, a.fazenda, 'Concorrente'),
      novoTalhao(a, a.fazenda, 'Concorrente'),
    ]);
    expect([x.recibo.outcome, y.recibo.outcome].sort()).toEqual(['confirmed', 'rejected']);
    expect([x.recibo.reasonCode, y.recibo.reasonCode]).toContain('NOME_EM_USO');
  });

  it('nome de fazenda repetido na organização é NOME_EM_USO; o mesmo nome em outra organização passa', async () => {
    expect((await novaFazenda(a, 'Fazenda Unica')).recibo.outcome).toBe('confirmed');
    expect((await novaFazenda(a, 'fazenda  UNICA')).recibo).toMatchObject({
      outcome: 'rejected',
      reasonCode: 'NOME_EM_USO',
    });
    expect((await novaFazenda(b, 'Fazenda Unica')).recibo.outcome).toBe('confirmed');
  });

  it('id já usado por outra organização é ALVO_INVALIDO, com a resposta de inexistente', async () => {
    const deB = await novoTalhao(b, b.fazenda, 'De B');
    const colisao = await novoTalhao(a, a.fazenda, 'Colide', '1', { id: deB.id });
    expect(colisao.recibo).toMatchObject({ outcome: 'rejected', reasonCode: 'ALVO_INVALIDO' });
    expect(await naOrg(a, (c) => obterTalhao(c, deB.id))).toBeNull();
  });

  it('fazenda de outra organização é FAZENDA_NAO_ENCONTRADA', async () => {
    const r = await novoTalhao(a, b.fazenda, 'Na fazenda de B');
    expect(r.recibo).toMatchObject({ outcome: 'rejected', reasonCode: 'FAZENDA_NAO_ENCONTRADA' });
  });
});

describe('editar e alterar a situação (contrato §3 e §4)', () => {
  it('editar sobe a versão; versão velha é conflito; a auditoria guarda antes e depois', async () => {
    const t = await novoTalhao(a, a.fazenda, 'Editavel', '10');
    const r = await editar(a, t.id, 1, { nome: 'Editado', areaDeclaradaHa: '12.5' });
    expect(r).toMatchObject({ outcome: 'confirmed', resultingVersion: 2 });
    expect(await naOrg(a, (c) => obterTalhao(c, t.id))).toMatchObject({
      nome: 'Editado',
      areaDeclaradaHa: '12.500000',
      versao: 2,
    });
    expect((await editar(a, t.id, 1, { nome: 'Velho' })).outcome).toBe('version_conflict');
    const aud = await naOrg(a, (c) =>
      c.query<{ before: { name: string }; after: { name: string } }>(
        "SELECT before_state AS before, after_state AS after FROM app.audit_log WHERE target_id = $1 AND command_type = 'cadastros.editar-talhao' AND outcome = 'confirmed'",
        [t.id],
      ),
    );
    expect(aud.rows[0]).toMatchObject({ before: { name: 'Editavel' }, after: { name: 'Editado' } });
  });

  it('trocar a fazenda confere o nome de novo na fazenda de destino', async () => {
    const destino = await novaFazenda(a, 'Destino');
    await novoTalhao(a, destino.id, 'Movido');
    const t = await novoTalhao(a, a.fazenda, 'Movido');
    expect(await editar(a, t.id, 1, { fazenda: destino.id })).toMatchObject({
      outcome: 'rejected',
      reasonCode: 'NOME_EM_USO',
    });
    const livre = await novaFazenda(a, 'Livre');
    expect(await editar(a, t.id, 1, { fazenda: livre.id })).toMatchObject({
      outcome: 'confirmed',
      resultingVersion: 2,
    });
    expect((await naOrg(a, (c) => obterTalhao(c, t.id)))?.fazenda.id).toBe(livre.id);
  });

  it('inativo não se edita; reativar com o nome tomado é NOME_EM_USO; pedir a mesma situação é recusado', async () => {
    const t = await novoTalhao(a, a.fazenda, 'Ciclo');
    expect(await situacao(a, t.id, 1, 'inativo')).toMatchObject({
      outcome: 'confirmed',
      resultingVersion: 2,
    });
    expect(await editar(a, t.id, 2, { nome: 'Nada' })).toMatchObject({
      outcome: 'rejected',
      reasonCode: 'TALHAO_INATIVO',
    });
    expect(await situacao(a, t.id, 2, 'inativo')).toMatchObject({
      outcome: 'rejected',
      reasonCode: 'SITUACAO_INALTERADA',
    });
    await novoTalhao(a, a.fazenda, 'Ciclo');
    expect(await situacao(a, t.id, 2, 'ativo')).toMatchObject({
      outcome: 'rejected',
      reasonCode: 'NOME_EM_USO',
    });
    expect((await naOrg(a, (c) => listarTalhoes(c, { situacao: 'inativo' }))).map((x) => x.id)).toContain(
      t.id,
    );
  });

  it('editar a fazenda: nome e fuso, versão e conflito', async () => {
    const f = await novaFazenda(a, 'Com Fuso');
    const dados = EsquemaDadosEditarFazenda.parse({ fuso: 'America/Cuiaba' });
    const r = await rodar(
      a,
      COMANDOS_CADASTRO.editarFazenda,
      { type: 'farm', id: f.id, expectedVersion: 1 },
      dados,
      editarFazenda(dados),
    );
    expect(r).toMatchObject({ outcome: 'confirmed', resultingVersion: 2 });
    expect(await naOrg(a, (c) => obterFazenda(c, f.id))).toMatchObject({ fuso: 'America/Cuiaba', versao: 2 });
    const velho = await rodar(
      a,
      COMANDOS_CADASTRO.editarFazenda,
      { type: 'farm', id: f.id, expectedVersion: 1 },
      dados,
      editarFazenda(dados),
    );
    expect(velho.outcome).toBe('version_conflict');
  });

  it('outra organização não enxerga nem altera', async () => {
    const t = await novoTalhao(a, a.fazenda, 'Privado');
    expect(await emOrganizacao(amb.app, b.org, (c) => obterTalhao(c, t.id))).toBeNull();
    expect(await emOrganizacao(amb.app, b.org, (c) => obterFazenda(c, a.fazenda))).toBeNull();
    expect(await editar(b, t.id, 1, { nome: 'Invasão' })).toMatchObject({
      outcome: 'rejected',
      reasonCode: 'TALHAO_NAO_ENCONTRADO',
    });
  });
});

describe('permissões do app_runtime (contrato §1)', () => {
  it('sem DELETE; UPDATE só nas colunas dos comandos', async () => {
    const t = await novoTalhao(a, a.fazenda, 'Grants');
    await expect(
      naOrg(a, (c) => c.query('DELETE FROM app.field WHERE id = $1', [t.id])),
    ).rejects.toMatchObject({ code: '42501' });
    await expect(
      naOrg(a, (c) => c.query('UPDATE app.field SET created_by = $2 WHERE id = $1', [t.id, a.usuario])),
    ).rejects.toMatchObject({ code: '42501' });
    await expect(
      naOrg(a, (c) => c.query('DELETE FROM app.farm WHERE id = $1', [a.fazenda])),
    ).rejects.toMatchObject({ code: '42501' });
    await expect(
      naOrg(a, (c) => c.query("UPDATE app.farm SET status = 'ativa' WHERE id = $1", [a.fazenda])),
    ).rejects.toMatchObject({ code: '42501' });
  });
});
