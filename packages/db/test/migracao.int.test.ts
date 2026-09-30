import { randomUUID } from 'node:crypto';
import { cp, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import pg from 'pg';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { ErroComando } from '../src/erros.js';
import { PASTA_MIGRACOES, aplicarMigracoes } from '../src/migrar.js';
import { emOrganizacao } from '../src/sessao.js';
import { criarBanco, semear, type Ambiente } from './ambiente.js';

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
      '0004_vinculo_demonstracao.sql',
      '0005_vinculo_hml.sql',
      '0006_vinculo_fila.sql',
      '0007_recebimento_documento.sql',
    ]);
    expect(r.rows[0]?.sha256).toMatch(/^[0-9a-f]{64}$/);
  });

  it('0007: validade coerente no lote, lote interno só DOC:<uuid>, NF confirmada única e fatos imutáveis', async () => {
    const s = await semear(amb.app, 'M7');
    const naOrg = (sql: string, params: unknown[], pool = amb.app) =>
      emOrganizacao(pool, s.org, (c) => c.query(sql, params));
    const lote = (codigo: string, validade: string | null, aplica: boolean, tipo = 'fabricante') =>
      naOrg(
        `INSERT INTO app.lot (id, organization_id, product_id, code, expiry_date, base_unit, expiry_applies, kind)
         VALUES ($1, $2, $3, $4, $5, 'L', $6, $7)`,
        [randomUUID(), s.org, s.produto, codigo, validade, aplica, tipo],
      );
    // "Não se aplica" é NULL com expiry_applies falso; data fictícia ou ausência sem marcação são recusadas.
    await expect(lote('SEM', null, false)).resolves.toBeDefined();
    await expect(lote('NULO-SEM-MARCA', null, true)).rejects.toMatchObject({ code: '23514' });
    await expect(lote('DATA-SEM-VALIDADE', '2027-01-01', false)).rejects.toMatchObject({ code: '23514' });
    const doc = randomUUID();
    await expect(lote(`DOC:${doc}`, null, false, 'agrupamento_interno')).resolves.toBeDefined();
    await expect(lote('NF-1-123', null, false, 'agrupamento_interno')).rejects.toMatchObject({
      code: '23514',
    });
    await expect(lote(`DOC:${randomUUID()}`, '2027-01-01', true)).rejects.toMatchObject({ code: '23514' });

    const fornecedor = randomUUID();
    await naOrg(
      "INSERT INTO app.counterparty (id, organization_id, name, identification) VALUES ($1, $2, 'F', '1')",
      [fornecedor, s.org],
    );
    const documento = (id: string, chave: string) =>
      naOrg(
        `INSERT INTO app.receipt_document (id, organization_id, issuer_id, doc_type, series, number, issued_on, received_on,
           farm_id, actor_id, intent_command_type, intent_key)
         VALUES ($1, $2, $3, 'nfe', '1', '123', '2026-09-29', '2026-09-30', $4, $5, 'estoque.receber-documento', $6)`,
        [id, s.org, fornecedor, s.fazenda, s.usuario, chave],
      );
    await documento(doc, 'k1');
    // A mesma NF confirmada não entra de novo, nem com outra chave de intenção.
    await expect(documento(randomUUID(), 'k2')).rejects.toMatchObject({ code: '23505' });
    // Série e número chegam normalizados: zero à esquerda é recusado pelo banco.
    await expect(
      naOrg(
        `INSERT INTO app.receipt_document (id, organization_id, issuer_id, doc_type, series, number, issued_on, received_on,
           farm_id, actor_id, intent_command_type, intent_key)
         VALUES ($1, $2, $3, 'nfe', '1', '0123', '2026-09-29', '2026-09-30', $4, $5, 'estoque.receber-documento', 'k3')`,
        [randomUUID(), s.org, fornecedor, s.fazenda, s.usuario],
      ),
    ).rejects.toMatchObject({ code: '23514' });
    const linha = randomUUID();
    await naOrg(
      `INSERT INTO app.receipt_line (id, organization_id, document_id, farm_id, line_number, product_id, lot_id,
         location_id, document_quantity, unit, qty_apto, qty_quarentena, qty_bloqueado, qty_recusado)
       VALUES ($1, $2, $3, $4, 1, $5, $6, $7, 20, 'L', 20, 0, 0, 0)`,
      [linha, s.org, doc, s.fazenda, s.produto, s.lote, s.local],
    );
    // app_runtime não altera; e nem o dono muda o fato: só status e versão do documento mudam (estorno, incremento 3).
    await expect(
      naOrg('UPDATE app.receipt_line SET qty_apto = 19 WHERE id = $1', [linha]),
    ).rejects.toMatchObject({
      code: '42501',
    });
    await expect(
      naOrg('UPDATE app.receipt_line SET qty_apto = 19 WHERE id = $1', [linha], amb.migrator),
    ).rejects.toMatchObject({ code: 'P0001' });
    await expect(
      naOrg("UPDATE app.receipt_document SET number = '124' WHERE id = $1", [doc], amb.migrator),
    ).rejects.toMatchObject({ code: 'P0001' });
    await expect(
      naOrg(
        "UPDATE app.receipt_document SET status = 'estornado', version = 2 WHERE id = $1",
        [doc],
        amb.migrator,
      ),
    ).resolves.toBeDefined();
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
          '0004_vinculo_demonstracao.sql',
          '0005_vinculo_hml.sql',
          '0006_vinculo_fila.sql',
          '0007_recebimento_documento.sql',
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
