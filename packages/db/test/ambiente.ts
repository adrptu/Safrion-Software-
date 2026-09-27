// Banco descartável por arquivo de teste: criado com dono migrator, migrado do zero e usado pelo app_runtime.
import { randomUUID } from 'node:crypto';

import pg from 'pg';
import { inject } from 'vitest';

import { executarComando, type Intencao, type Recibo } from '../src/comando.js';
import { conteudoDoMovimento, registrarMovimento, type NovoMovimento } from '../src/estoque.js';
import { aplicarMigracoes } from '../src/migrar.js';
import { emOrganizacao } from '../src/sessao.js';

export interface Ambiente {
  readonly banco: string;
  /** Pool com o papel da aplicação (app_runtime), o mesmo que a aplicação usa (ENG-025). */
  readonly app: pg.Pool;
  /** Pool com o papel dono das tabelas, só para provar o que nem o dono consegue. */
  readonly migrator: pg.Pool;
  url(papel: 'migrator' | 'app_runtime'): string;
  encerrar(): Promise<void>;
}

export async function criarBanco(opcoes: { maxApp?: number } = {}): Promise<Ambiente> {
  const base = new URL(inject('urlAdmin'));
  const admin = new pg.Client({ connectionString: base.toString() });
  await admin.connect();
  const banco = `safrion_${randomUUID().replaceAll('-', '').slice(0, 16)}`;
  await admin.query(`CREATE DATABASE ${banco} OWNER migrator`);
  const url = (papel: 'migrator' | 'app_runtime') => {
    const u = new URL(base.toString());
    u.username = papel;
    u.password = papel === 'migrator' ? inject('senhaMigrator') : inject('senhaApp');
    u.pathname = `/${banco}`;
    return u.toString();
  };
  const mig = new pg.Client({ connectionString: url('migrator') });
  await mig.connect();
  try {
    await aplicarMigracoes(mig);
  } finally {
    await mig.end();
  }
  const app = new pg.Pool({ connectionString: url('app_runtime'), max: opcoes.maxApp ?? 12 });
  const migrator = new pg.Pool({ connectionString: url('migrator'), max: 2 });
  return {
    banco,
    app,
    migrator,
    url,
    async encerrar() {
      await app.end();
      await migrator.end();
      await admin.query(`DROP DATABASE ${banco} WITH (FORCE)`);
      await admin.end();
    },
  };
}

export interface Semente {
  readonly org: string;
  readonly usuario: string;
  readonly fazenda: string;
  readonly local: string;
  readonly produto: string;
  readonly lote: string;
}

/** Organização fictícia com usuário, fazenda, local, produto em litros e um lote vazio, criada pelo app_runtime. */
export async function semear(pool: pg.Pool, nome: string, validade = '2027-06-30'): Promise<Semente> {
  const s: Semente = {
    org: randomUUID(),
    usuario: randomUUID(),
    fazenda: randomUUID(),
    local: randomUUID(),
    produto: randomUUID(),
    lote: randomUUID(),
  };
  await emOrganizacao(pool, s.org, async (c) => {
    await c.query('INSERT INTO app.organization (id, name) VALUES ($1, $2)', [s.org, nome]);
    await c.query('INSERT INTO app.app_user (id, organization_id, name, email) VALUES ($1, $2, $3, $4)', [
      s.usuario,
      s.org,
      `Almoxarife ${nome}`,
      `almox@${nome.toLowerCase()}.invalid`,
    ]);
    await c.query('INSERT INTO app.farm (id, organization_id, name) VALUES ($1, $2, $3)', [
      s.fazenda,
      s.org,
      'Sede',
    ]);
    await c.query(
      'INSERT INTO app.stock_location (id, organization_id, farm_id, name) VALUES ($1, $2, $3, $4)',
      [s.local, s.org, s.fazenda, 'Almoxarifado'],
    );
    await c.query('INSERT INTO app.product (id, organization_id, name, base_unit) VALUES ($1, $2, $3, $4)', [
      s.produto,
      s.org,
      'Herbicida',
      'L',
    ]);
    await c.query(
      `INSERT INTO app.lot (id, organization_id, product_id, code, expiry_date, base_unit)
       VALUES ($1, $2, $3, $4, $5, 'L')`,
      [s.lote, s.org, s.produto, `F26-${nome}`, validade],
    );
  });
  return s;
}

/** Intenção de movimento no lote da semente, com chave e versão esperada informadas. */
export function intencaoMovimento(
  s: Semente,
  chave: string,
  versao: number,
  movimento: NovoMovimento,
): { intencao: Intencao; efeito: ReturnType<typeof registrarMovimento> } {
  const pedido = { lotId: s.lote, locationId: s.local, movimento };
  return {
    intencao: {
      commandType: 'TESTE-MOV',
      idempotencyKey: chave,
      initiatorKind: 'web',
      actorId: s.usuario,
      target: { type: 'lot', id: s.lote, expectedVersion: versao },
      data: conteudoDoMovimento(pedido),
      correlationId: `corr-${chave}`,
    },
    efeito: registrarMovimento(pedido),
  };
}

export async function mover(
  pool: pg.Pool,
  s: Semente,
  chave: string,
  versao: number,
  movimento: NovoMovimento,
): Promise<Recibo> {
  const { intencao, efeito } = intencaoMovimento(s, chave, versao, movimento);
  return executarComando(pool, s.org, intencao, efeito);
}

/** Contagens por tabela na organização, para provar que nada mudou. */
export async function contagens(pool: pg.Pool, org: string): Promise<Record<string, number>> {
  return emOrganizacao(pool, org, async (c) => {
    const r = await c.query<{ t: string; n: string }>(
      `SELECT 'movimentos' t, count(*)::text n FROM app.stock_movement
       UNION ALL SELECT 'intencoes', count(*)::text FROM app.intent_record
       UNION ALL SELECT 'auditoria', count(*)::text FROM app.audit_log
       UNION ALL SELECT 'outbox', count(*)::text FROM app.outbox`,
    );
    return Object.fromEntries(r.rows.map((l) => [l.t, Number(l.n)]));
  });
}
