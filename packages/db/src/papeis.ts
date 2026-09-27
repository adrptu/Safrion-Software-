import type { ClientBase } from 'pg';

/**
 * Cria ou corrige os dois papéis de banco (plano R-006, passo 7): migrator, dono das tabelas e usado só pela migração;
 * app_runtime, usado pela aplicação, sem SUPERUSER, CREATEDB, CREATEROLE nem BYPASSRLS. Os atributos são reafirmados a
 * cada chamada, para que um papel criado antes com privilégio a mais não passe despercebido. Roda com um papel
 * administrativo; as senhas vêm do cofre de segredos do ambiente, nunca do repositório.
 */
export async function provisionarPapeis(
  admin: ClientBase,
  senhas: { readonly migrator: string; readonly appRuntime: string },
): Promise<void> {
  const atributos = 'LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOREPLICATION';
  await admin.query("SELECT pg_advisory_lock(hashtext('safrion.papeis'))");
  try {
    for (const [papel, senha] of [
      ['migrator', senhas.migrator],
      ['app_runtime', senhas.appRuntime],
    ] as const) {
      const existe = await admin.query('SELECT 1 FROM pg_roles WHERE rolname = $1', [papel]);
      const verbo = existe.rowCount ? 'ALTER' : 'CREATE';
      await admin.query(
        `${verbo} ROLE ${admin.escapeIdentifier(papel)} ${atributos} PASSWORD ${admin.escapeLiteral(senha)}`,
      );
    }
  } finally {
    await admin.query("SELECT pg_advisory_unlock(hashtext('safrion.papeis'))");
  }
}
