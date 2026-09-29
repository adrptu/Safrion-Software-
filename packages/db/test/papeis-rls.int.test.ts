import pg from 'pg';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { emOrganizacao } from '../src/sessao.js';
import { criarBanco, semear, type Ambiente } from './ambiente.js';

let amb: Ambiente;
beforeAll(async () => {
  amb = await criarBanco();
});
afterAll(async () => {
  await amb.encerrar();
});

describe('papel da aplicação e RLS (ENG-025; aceite técnico da F1)', () => {
  it('app_runtime não é superusuário, não tem BYPASSRLS, CREATEROLE nem CREATEDB', async () => {
    const r = await amb.app.query<Record<string, boolean>>(
      `SELECT rolsuper, rolbypassrls, rolcreaterole, rolcreatedb FROM pg_roles WHERE rolname = current_user`,
    );
    expect(r.rows[0]).toEqual({
      rolsuper: false,
      rolbypassrls: false,
      rolcreaterole: false,
      rolcreatedb: false,
    });
    expect((await amb.app.query<{ u: string }>('SELECT current_user AS u')).rows[0]?.u).toBe('app_runtime');
  });

  it('app_runtime não é dono de nenhum objeto do esquema', async () => {
    const r = await amb.app.query<{ n: string }>(
      `SELECT count(*)::text n FROM pg_class c JOIN pg_namespace s ON s.oid = c.relnamespace
        WHERE s.nspname = 'app' AND pg_get_userbyid(c.relowner) = 'app_runtime'`,
    );
    expect(r.rows[0]?.n).toBe('0');
  });

  it('toda tabela com organização tem RLS habilitado e FORCE', async () => {
    const r = await amb.app.query<{ tabela: string; rls: boolean; force: boolean }>(
      `SELECT c.relname tabela, c.relrowsecurity rls, c.relforcerowsecurity force
         FROM pg_class c JOIN pg_namespace s ON s.oid = c.relnamespace
        WHERE s.nspname = 'app' AND c.relkind = 'r'
          AND (c.relname = 'organization' OR EXISTS (SELECT 1 FROM pg_attribute a
                 WHERE a.attrelid = c.oid AND a.attname = 'organization_id' AND NOT a.attisdropped))
        ORDER BY 1`,
    );
    // 12 da F0-b + identity_link e session (0003) + access_request e identity_link_event (0005) +
    // vinculo_pedido_recibo (0006)
    expect(r.rows.length).toBe(17);
    expect(r.rows.filter((l) => !l.rls || !l.force)).toEqual([]);
  });

  it('sem organização na sessão, nada é visível nem gravável (falha fechada)', async () => {
    await semear(amb.app, 'Fechada');
    for (const t of ['organization', 'app_user', 'farm', 'stock_location', 'product', 'lot']) {
      const r = await amb.app.query<{ n: string }>(`SELECT count(*)::text n FROM app.${t}`);
      expect(r.rows[0]?.n, t).toBe('0');
    }
    await expect(
      amb.app.query(
        "INSERT INTO app.farm (id, organization_id, name) VALUES (gen_random_uuid(), gen_random_uuid(), 'x')",
      ),
    ).rejects.toMatchObject({ code: '42501' });
  });

  it('nem o dono das tabelas lê sem organização: FORCE vale para ele também', async () => {
    const r = await amb.migrator.query<{ n: string }>('SELECT count(*)::text n FROM app.lot');
    expect(r.rows[0]?.n).toBe('0');
  });

  it('a organização não fica na conexão depois da transação, nem com pool de uma conexão só', async () => {
    const pool = new pg.Pool({ connectionString: amb.url('app_runtime'), max: 1 });
    try {
      const a = await semear(pool, 'PoolA');
      const b = await semear(pool, 'PoolB');
      for (let i = 0; i < 10; i++) {
        const s = i % 2 === 0 ? a : b;
        const lotes = await emOrganizacao(pool, s.org, async (c) =>
          (await c.query<{ id: string }>('SELECT id FROM app.lot')).rows.map((l) => l.id),
        );
        expect(lotes).toEqual([s.lote]);
        const depois = await pool.query<{ org: string | null; n: string }>(
          "SELECT current_setting('app.organization_id', true) org, (SELECT count(*)::text FROM app.lot) n",
        );
        expect(depois.rows[0]?.org ?? '').toBe('');
        expect(depois.rows[0]?.n).toBe('0');
      }
    } finally {
      await pool.end();
    }
  });
});
