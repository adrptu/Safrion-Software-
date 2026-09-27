import { createHash } from 'node:crypto';
import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

import type { ClientBase } from 'pg';

import { ErroComando } from './erros.js';

/** Pasta das migrações SQL do pacote (também quando executado a partir de dist/). */
export const PASTA_MIGRACOES = fileURLToPath(new URL('../migrations/', import.meta.url));

const NOME = /^\d{4}_[a-z0-9_]+\.sql$/;

export interface ResultadoMigracao {
  readonly aplicadas: readonly string[];
  readonly jaAplicadas: readonly string[];
}

/**
 * Aplica, em ordem, as migrações ainda não aplicadas, cada uma na sua transação, e registra o SHA-256 do arquivo.
 * Migração já aplicada com conteúdo diferente para tudo (MIGRACAO_ALTERADA): correção é migração nova. Uma trava
 * consultiva impede duas execuções ao mesmo tempo. Deve rodar com o papel migrator (dono das tabelas).
 */
export async function aplicarMigracoes(
  cliente: ClientBase,
  pasta: string = PASTA_MIGRACOES,
): Promise<ResultadoMigracao> {
  const arquivos = (await readdir(pasta)).filter((n) => NOME.test(n)).sort();
  const aplicadas: string[] = [];
  const jaAplicadas: string[] = [];
  await cliente.query("SELECT pg_advisory_lock(hashtext('safrion.migracoes'))");
  try {
    await cliente.query('CREATE SCHEMA IF NOT EXISTS migracao');
    await cliente.query(
      `CREATE TABLE IF NOT EXISTS migracao.registro (
         versao text PRIMARY KEY,
         sha256 char(64) NOT NULL,
         aplicada_em timestamptz NOT NULL DEFAULT now())`,
    );
    for (const arquivo of arquivos) {
      const sql = await readFile(join(pasta, arquivo), 'utf8');
      const sha = createHash('sha256').update(sql, 'utf8').digest('hex');
      const registro = await cliente.query<{ sha256: string }>(
        'SELECT sha256 FROM migracao.registro WHERE versao = $1',
        [arquivo],
      );
      const anterior = registro.rows[0];
      if (anterior) {
        if (anterior.sha256 !== sha) {
          throw new ErroComando(
            'MIGRACAO_ALTERADA',
            `A migração ${arquivo} já foi aplicada com outro conteúdo; crie uma migração nova.`,
            { arquivo },
          );
        }
        jaAplicadas.push(arquivo);
        continue;
      }
      await cliente.query('BEGIN');
      try {
        await cliente.query(sql);
        await cliente.query('INSERT INTO migracao.registro (versao, sha256) VALUES ($1, $2)', [arquivo, sha]);
        await cliente.query('COMMIT');
      } catch (erro) {
        await cliente.query('ROLLBACK');
        throw erro;
      }
      aplicadas.push(arquivo);
    }
  } finally {
    await cliente.query("SELECT pg_advisory_unlock(hashtext('safrion.migracoes'))");
  }
  return { aplicadas, jaAplicadas };
}
