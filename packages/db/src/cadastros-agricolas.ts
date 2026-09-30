import type {
  DadosAlterarSituacaoTalhao,
  DadosCriarFazenda,
  DadosCriarTalhao,
  DadosEditarFazenda,
  DadosEditarTalhao,
  SituacaoTalhao,
} from '@safrion/contracts';
import type { ClientBase, PoolClient } from 'pg';

import type { ContextoEfeito, Efeito } from './comando.js';
import { ConflitoVersao, RejeicaoNegocio } from './erros.js';
import { ehUuid } from './sessao.js';

/**
 * Cadastros agrícolas, incremento 1: fazenda e talhão (contrato CAD-01 v3). Os efeitos rodam no envelope (idempotência,
 * recibo, auditoria e outbox na mesma transação); as leituras rodam dentro de emOrganizacao. O que é de outra
 * organização não é visível (RLS) e é tratado como inexistente, inclusive um id repetido na PK global.
 */

// Leituras (contrato CAD-01 §6) ------------------------------------------------------------------------------------

/** Área em ha como texto decimal com 6 casas, como no banco ("204.000000"); a tela formata em pt-BR. */
export type AreaTexto = string;
/** De onde vem a área de referência: sem limite, a declarada; com limite (incremento 2), a calculada. */
export type OrigemArea = 'declarada' | 'calculada';

export interface FazendaResumo {
  readonly id: string;
  readonly nome: string;
  readonly fuso: string;
  readonly situacao: 'ativa';
  readonly versao: number;
  /** Talhões ativos e a soma da área de referência deles; a soma não é a "área da fazenda" (contrato §6). */
  readonly talhoesAtivos: number;
  readonly areaAtivaHa: AreaTexto;
}
export type FazendaDetalhe = FazendaResumo;

export interface OpcaoFazenda {
  readonly id: string;
  readonly nome: string;
  readonly fuso: string;
}

export interface TalhaoResumo {
  readonly id: string;
  readonly nome: string;
  readonly fazenda: { readonly id: string; readonly nome: string };
  readonly areaReferenciaHa: AreaTexto;
  readonly origemArea: OrigemArea;
  readonly areaDeclaradaHa: AreaTexto;
  /** Limite vigente; sempre null no incremento 1 ("Sem limite no mapa"). */
  readonly limite: { readonly versao: number; readonly data: string } | null;
  readonly situacao: SituacaoTalhao;
  readonly versao: number;
}
export interface TalhaoDetalhe extends TalhaoResumo {
  readonly criadoEm: string;
  readonly atualizadoEm: string | null;
}

export interface FiltroTalhoes {
  readonly fazenda?: string;
  readonly situacao?: SituacaoTalhao;
}

interface LinhaFazenda {
  id: string;
  name: string;
  timezone: string;
  version: string;
  talhoes: number;
  area: string;
}

const SELECT_FAZENDAS = `
  SELECT f.id, f.name, f.timezone, f.version,
         count(t.id) FILTER (WHERE t.status = 'ativo')::int AS talhoes,
         coalesce(sum(t.declared_area_ha) FILTER (WHERE t.status = 'ativo'), 0)::numeric(20, 6)::text AS area
    FROM app.farm f
    LEFT JOIN app.field t ON t.organization_id = f.organization_id AND t.farm_id = f.id
   WHERE ($1::uuid IS NULL OR f.id = $1)
   GROUP BY f.id
   ORDER BY f.name_key, f.id`;

function fazenda(l: LinhaFazenda): FazendaResumo {
  return {
    id: l.id,
    nome: l.name,
    fuso: l.timezone,
    situacao: 'ativa',
    versao: Number(l.version),
    talhoesAtivos: l.talhoes,
    areaAtivaHa: l.area,
  };
}

/** Fazendas da organização, inclusive as sem talhão (grupo vazio na listagem, contrato §2). */
export async function listarFazendas(cliente: ClientBase): Promise<FazendaResumo[]> {
  return (await cliente.query<LinhaFazenda>(SELECT_FAZENDAS, [null])).rows.map(fazenda);
}

/** Uma fazenda; null se não existe ou é de outra organização (id inválido também é null). */
export async function obterFazenda(cliente: ClientBase, id: string): Promise<FazendaDetalhe | null> {
  if (!ehUuid(id)) return null;
  const l = (await cliente.query<LinhaFazenda>(SELECT_FAZENDAS, [id])).rows[0];
  return l ? fazenda(l) : null;
}

/** Fazendas ativas para seleção (sem inativas, contrato §6). */
export async function opcoesFazenda(cliente: ClientBase): Promise<OpcaoFazenda[]> {
  const r = await cliente.query<{ id: string; name: string; timezone: string }>(
    `SELECT id, name, timezone FROM app.farm WHERE status = 'ativa' ORDER BY name_key, id`,
  );
  return r.rows.map((f) => ({ id: f.id, nome: f.name, fuso: f.timezone }));
}

interface LinhaTalhao {
  id: string;
  name: string;
  farm_id: string;
  farm_name: string;
  declared_area_ha: string;
  status: SituacaoTalhao;
  version: string;
  created_at: Date;
  updated_at: Date | null;
}

const SELECT_TALHOES = `
  SELECT t.id, t.name, t.farm_id, f.name AS farm_name, t.declared_area_ha::text AS declared_area_ha, t.status,
         t.version, t.created_at, t.updated_at
    FROM app.field t
    JOIN app.farm f ON f.organization_id = t.organization_id AND f.id = t.farm_id`;

function talhao(l: LinhaTalhao): TalhaoResumo {
  return {
    id: l.id,
    nome: l.name,
    fazenda: { id: l.farm_id, nome: l.farm_name },
    areaReferenciaHa: l.declared_area_ha,
    origemArea: 'declarada',
    areaDeclaradaHa: l.declared_area_ha,
    limite: null,
    situacao: l.status,
    versao: Number(l.version),
  };
}

/** Talhões da organização, por fazenda e nome; filtros opcionais (fazenda inválida: lista vazia). */
export async function listarTalhoes(
  cliente: ClientBase,
  filtro: FiltroTalhoes = {},
): Promise<TalhaoResumo[]> {
  if (filtro.fazenda !== undefined && !ehUuid(filtro.fazenda)) return [];
  const r = await cliente.query<LinhaTalhao>(
    `${SELECT_TALHOES}
      WHERE ($1::uuid IS NULL OR t.farm_id = $1) AND ($2::text IS NULL OR t.status = $2)
      ORDER BY f.name_key, f.id, t.name_key, t.id`,
    [filtro.fazenda ?? null, filtro.situacao ?? null],
  );
  return r.rows.map(talhao);
}

/** Um talhão; null se não existe ou é de outra organização. */
export async function obterTalhao(cliente: ClientBase, id: string): Promise<TalhaoDetalhe | null> {
  if (!ehUuid(id)) return null;
  const l = (await cliente.query<LinhaTalhao>(`${SELECT_TALHOES} WHERE t.id = $1`, [id])).rows[0];
  return l
    ? {
        ...talhao(l),
        criadoEm: l.created_at.toISOString(),
        atualizadoEm: l.updated_at?.toISOString() ?? null,
      }
    : null;
}

// Efeitos (contrato CAD-01 §3 e §4) --------------------------------------------------------------------------------

/**
 * Recusa registrada com a chave. O motivo em pt-BR vai também no nextAction do recibo (contrato CAD-01 §4): é o que a tela
 * mostra, porque o recibo não leva a mensagem do erro.
 */
function rejeitar(motivo: string, mensagem: string): never {
  throw new RejeicaoNegocio(motivo, mensagem, mensagem);
}

function erroPg(erro: unknown): { code?: string; constraint?: string } {
  return typeof erro === 'object' && erro !== null ? erro : {};
}

/**
 * Traduz a violação que o banco decide (unicidade, tamanho do nome e FK composta) em rejeição registrada; o resto sobe.
 * A concorrência de dois nomes iguais nunca vira 500: o índice parcial recusa o segundo.
 */
function traduzir(
  erro: unknown,
  indiceNome: string,
  restricaoTamanho: string,
  entidade: 'fazenda' | 'talhão',
): never {
  const e = erroPg(erro);
  if (e.code === '23505' && e.constraint === indiceNome) {
    rejeitar(
      'NOME_EM_USO',
      entidade === 'fazenda'
        ? 'Já existe uma fazenda ativa com este nome. Use outro nome.'
        : 'Já existe um talhão ativo com este nome nesta fazenda. Use outro nome ou inative o outro talhão.',
    );
  }
  if (e.code === '23514' && e.constraint === restricaoTamanho) {
    rejeitar('NOME_INVALIDO', 'Use de 1 a 80 caracteres no nome.');
  }
  // Id repetido, inclusive de outra organização (a PK é global), ou referência que a FK composta recusa: resposta de
  // inexistente, sem revelar o dono (contrato §3, como no CMD-15).
  if (e.code === '23505' || e.code === '23503') {
    rejeitar(
      'ALVO_INVALIDO',
      'Identificador indisponível ou referência inexistente; gere outro e confira a fazenda.',
    );
  }
  throw erro;
}

function alvoNovo(ctx: ContextoEfeito, tipo: 'farm' | 'field'): string {
  const alvo = ctx.intencao.target;
  if (alvo.type !== tipo || alvo.expectedVersion !== 0 || !ehUuid(alvo.id)) {
    rejeitar('ALVO_INVALIDO', `A criação usa um alvo ${tipo} novo, na versão esperada 0.`);
  }
  return alvo.id;
}

function alvoExistente(ctx: ContextoEfeito, tipo: 'farm' | 'field'): { id: string; esperada: number } {
  const alvo = ctx.intencao.target;
  if (
    alvo.type !== tipo ||
    alvo.expectedVersion === undefined ||
    alvo.expectedVersion < 1 ||
    !ehUuid(alvo.id)
  ) {
    rejeitar('ALVO_INVALIDO', `A alteração usa um alvo ${tipo} existente, com a versão esperada.`);
  }
  return { id: alvo.id, esperada: alvo.expectedVersion };
}

async function fazendaExiste(c: PoolClient, id: string): Promise<void> {
  if (!(await c.query("SELECT 1 FROM app.farm WHERE id = $1 AND status = 'ativa'", [id])).rowCount) {
    rejeitar('FAZENDA_NAO_ENCONTRADA', 'Fazenda não encontrada. Escolha uma fazenda da lista.');
  }
}

interface EstadoFazenda {
  name: string;
  timezone: string;
  version: string;
}

/** cadastros.criar-fazenda: fazenda nova, ativa, na versão 1. */
export function criarFazenda(dados: DadosCriarFazenda): Efeito {
  return async (c, ctx) => {
    const id = alvoNovo(ctx, 'farm');
    try {
      await c.query('INSERT INTO app.farm (id, organization_id, name, timezone) VALUES ($1, $2, $3, $4)', [
        id,
        ctx.organizationId,
        dados.nome,
        dados.fuso,
      ]);
    } catch (erro) {
      traduzir(erro, 'farm_nome_ativo', 'farm_nome_tamanho', 'fazenda');
    }
    ctx.emitir({
      type: 'cadastros.fazenda_criada',
      schemaVersion: 1,
      entityType: 'farm',
      entityId: id,
      entityVersion: 1,
      previousVersion: null,
      payload: {},
    });
    return {
      resultingVersion: 1,
      effects: { farms: [id] },
      after: { name: dados.nome, timezone: dados.fuso, version: 1 },
    };
  };
}

/** cadastros.editar-fazenda: nome e/ou fuso, sobre a versão esperada. */
export function editarFazenda(dados: DadosEditarFazenda): Efeito {
  return async (c, ctx) => {
    const { id, esperada } = alvoExistente(ctx, 'farm');
    const antes = (
      await c.query<EstadoFazenda>('SELECT name, timezone, version FROM app.farm WHERE id = $1 FOR UPDATE', [
        id,
      ])
    ).rows[0];
    if (!antes)
      rejeitar('FAZENDA_NAO_ENCONTRADA', 'Fazenda não encontrada. Volte à lista de fazendas e talhões.');
    const atual = Number(antes.version);
    if (atual !== esperada) throw new ConflitoVersao(atual);
    const nova = atual + 1;
    try {
      await c.query(
        `UPDATE app.farm SET name = coalesce($2, name), timezone = coalesce($3, timezone), version = $4,
                updated_at = clock_timestamp()
          WHERE id = $1`,
        [id, dados.nome ?? null, dados.fuso ?? null, nova],
      );
    } catch (erro) {
      traduzir(erro, 'farm_nome_ativo', 'farm_nome_tamanho', 'fazenda');
    }
    ctx.emitir({
      type: 'cadastros.fazenda_alterada',
      schemaVersion: 1,
      entityType: 'farm',
      entityId: id,
      entityVersion: nova,
      previousVersion: atual,
      payload: { fields: Object.keys(dados) },
    });
    return {
      resultingVersion: nova,
      effects: { farms: [id] },
      before: { name: antes.name, timezone: antes.timezone, version: atual },
      after: { name: dados.nome ?? antes.name, timezone: dados.fuso ?? antes.timezone, version: nova },
    };
  };
}

interface EstadoTalhao {
  farm_id: string;
  name: string;
  declared_area_ha: string;
  status: SituacaoTalhao;
  version: string;
}

const SELECT_TALHAO_TRAVADO =
  'SELECT farm_id, name, declared_area_ha::text AS declared_area_ha, status, version FROM app.field WHERE id = $1 FOR UPDATE';

async function talhaoTravado(c: PoolClient, id: string, esperada: number): Promise<EstadoTalhao> {
  const antes = (await c.query<EstadoTalhao>(SELECT_TALHAO_TRAVADO, [id])).rows[0];
  if (!antes)
    rejeitar('TALHAO_NAO_ENCONTRADO', 'Talhão não encontrado. Volte à lista de fazendas e talhões.');
  const atual = Number(antes.version);
  if (atual !== esperada) throw new ConflitoVersao(atual);
  return antes;
}

function estado(t: EstadoTalhao, versao: number) {
  return {
    farmId: t.farm_id,
    name: t.name,
    declaredAreaHa: t.declared_area_ha,
    status: t.status,
    version: versao,
  };
}

/** cadastros.criar-talhao: talhão novo, ativo, na versão 1, numa fazenda ativa da organização. */
export function criarTalhao(dados: DadosCriarTalhao): Efeito {
  return async (c, ctx) => {
    const id = alvoNovo(ctx, 'field');
    await fazendaExiste(c, dados.fazenda);
    try {
      await c.query(
        `INSERT INTO app.field (id, organization_id, farm_id, name, declared_area_ha, created_by)
         VALUES ($1, $2, $3, $4, $5, $6)`,
        [id, ctx.organizationId, dados.fazenda, dados.nome, dados.areaDeclaradaHa, ctx.intencao.actorId],
      );
    } catch (erro) {
      traduzir(erro, 'field_nome_ativo', 'field_nome_tamanho', 'talhão');
    }
    ctx.emitir({
      type: 'cadastros.talhao_criado',
      schemaVersion: 1,
      entityType: 'field',
      entityId: id,
      entityVersion: 1,
      previousVersion: null,
      payload: { farmId: dados.fazenda },
    });
    return {
      resultingVersion: 1,
      effects: { fields: [id] },
      after: {
        farmId: dados.fazenda,
        name: dados.nome,
        declaredAreaHa: dados.areaDeclaradaHa,
        status: 'ativo',
        version: 1,
      },
    };
  };
}

/**
 * cadastros.editar-talhao: fazenda, nome e/ou área declarada, sobre a versão esperada. Talhão inativo não se edita
 * (reative antes). Enquanto nada o consome (até a etapa 04), trocar a fazenda ou a área não cria versão de histórico;
 * a auditoria guarda antes e depois (contrato §3).
 */
export function editarTalhao(dados: DadosEditarTalhao): Efeito {
  return async (c, ctx) => {
    const { id, esperada } = alvoExistente(ctx, 'field');
    const antes = await talhaoTravado(c, id, esperada);
    if (antes.status !== 'ativo') rejeitar('TALHAO_INATIVO', 'Reative o talhão antes de editar.');
    if (dados.fazenda !== undefined) await fazendaExiste(c, dados.fazenda);
    const nova = esperada + 1;
    try {
      await c.query(
        `UPDATE app.field SET farm_id = coalesce($2, farm_id), name = coalesce($3, name),
                declared_area_ha = coalesce($4, declared_area_ha), version = $5, updated_at = clock_timestamp()
          WHERE id = $1`,
        [id, dados.fazenda ?? null, dados.nome ?? null, dados.areaDeclaradaHa ?? null, nova],
      );
    } catch (erro) {
      traduzir(erro, 'field_nome_ativo', 'field_nome_tamanho', 'talhão');
    }
    const depois = (await c.query<EstadoTalhao>(SELECT_TALHAO_TRAVADO, [id])).rows[0];
    ctx.emitir({
      type: 'cadastros.talhao_alterado',
      schemaVersion: 1,
      entityType: 'field',
      entityId: id,
      entityVersion: nova,
      previousVersion: esperada,
      payload: { fields: Object.keys(dados) },
    });
    return {
      resultingVersion: nova,
      effects: { fields: [id] },
      before: estado(antes, esperada),
      after: depois ? estado(depois, nova) : null,
    };
  };
}

/**
 * cadastros.alterar-situacao-talhao: inativar bloqueia novos usos e conserva a consulta; reativar confere de novo o
 * nome entre os ativos (NOME_EM_USO). Pedir a situação que o talhão já tem é recusado, sem mudar a versão.
 */
export function alterarSituacaoTalhao(dados: DadosAlterarSituacaoTalhao): Efeito {
  return async (c, ctx) => {
    const { id, esperada } = alvoExistente(ctx, 'field');
    const antes = await talhaoTravado(c, id, esperada);
    if (antes.status === dados.situacao) {
      rejeitar('SITUACAO_INALTERADA', `O talhão já está ${dados.situacao}.`);
    }
    const nova = esperada + 1;
    try {
      await c.query(
        'UPDATE app.field SET status = $2, version = $3, updated_at = clock_timestamp() WHERE id = $1',
        [id, dados.situacao, nova],
      );
    } catch (erro) {
      traduzir(erro, 'field_nome_ativo', 'field_nome_tamanho', 'talhão');
    }
    ctx.emitir({
      type: 'cadastros.talhao_situacao_alterada',
      schemaVersion: 1,
      entityType: 'field',
      entityId: id,
      entityVersion: nova,
      previousVersion: esperada,
      payload: { status: dados.situacao },
    });
    return {
      resultingVersion: nova,
      effects: { fields: [id] },
      before: estado(antes, esperada),
      after: estado({ ...antes, status: dados.situacao }, nova),
    };
  };
}
