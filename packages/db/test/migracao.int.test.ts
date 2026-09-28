import { cp, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import pg from 'pg';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { ErroComando } from '../src/erros.js';
import { PASTA_MIGRACOES, aplicarMigracoes } from '../src/migrar.js';
import { criarBanco, type Ambiente } from './ambiente.js';

let amb: Ambiente;
beforeAll(async () => {
  amb = await criarBanco();
});
afterAll(async () => {
  await amb.encerrar();
});

describe('migrações (plano R-006, passo 7)', () => {
  it('aplicam do zero e registram o SHA-256 de cada arquivo', async () => {
    const r = await amb.migrator.query<{ versao: string; sha256: string }>(
      'SELECT versao, sha256 FROM migracao.registro ORDER BY versao',
    );
    expect(r.rows.map((l) => l.versao)).toEqual([
      '0001_fundacao.sql',
      '0002_ambiente_e_demonstracao.sql',
      '0003_sessao_e_identidade.sql',
    ]);
    expect(r.rows[0]?.sha256).toMatch(/^[0-9a-f]{64}$/);
  });

  it('reaplicar não muda nada', async () => {
    const c = new pg.Client({ connectionString: amb.url('migrator') });
    await c.connect();
    try {
      expect(await aplicarMigracoes(c)).toEqual({
        aplicadas: [],
        jaAplicadas: [
          '0001_fundacao.sql',
          '0002_ambiente_e_demonstracao.sql',
          '0003_sessao_e_identidade.sql',
        ],
      });
    } finally {
      await c.end();
    }
  });

  it('migração já aplicada e alterada depois é recusada: correção é migração nova', async () => {
    const pasta = await mkdtemp(join(tmpdir(), 'migracoes-'));
    const c = new pg.Client({ connectionString: amb.url('migrator') });
    await c.connect();
    try {
      await cp(PASTA_MIGRACOES, pasta, { recursive: true });
      const arq = join(pasta, '0001_fundacao.sql');
      await writeFile(arq, `${await readFile(arq, 'utf8')}\n-- alteração depois de aplicada\n`);
      const erro: unknown = await aplicarMigracoes(c, pasta).catch((e: unknown) => e);
      expect(erro).toBeInstanceOf(ErroComando);
      expect((erro as ErroComando).codigo).toBe('MIGRACAO_ALTERADA');
    } finally {
      await c.end();
      await rm(pasta, { recursive: true, force: true });
    }
  });
});
