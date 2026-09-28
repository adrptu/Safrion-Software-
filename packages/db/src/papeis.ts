import type { ClientBase } from 'pg';

const PROIBIDOS = ['rolsuper', 'rolbypassrls', 'rolreplication', 'rolcreaterole', 'rolcreatedb'] as const;

/** Papel com atributo proibido depois do provisionamento; a transação foi desfeita e nada mudou. */
export class ErroPapeis extends Error {
  override readonly name = 'ErroPapeis';
  constructor(readonly problemas: readonly string[]) {
    super(
      `Papel com atributo proibido (${problemas.join('; ')}); nada foi alterado. Corrija o papel e repita.`,
    );
  }
}

/**
 * Cria ou atualiza os dois papéis de banco (plano R-006, passo 7): migrator, dono das tabelas e usado só pela migração;
 * app_runtime, usado pela aplicação. Nenhum dos dois pode ter SUPERUSER, BYPASSRLS, REPLICATION, CREATEROLE nem CREATEDB.
 * Roda com um papel administrativo que, no Cloud SQL, não é superusuário: ele cria o papel com todos os atributos, mas
 * não pode reafirmar NOSUPERUSER, NOBYPASSRLS nem NOREPLICATION num papel existente (42501). Por isso a repetição só
 * reafirma LOGIN, NOCREATEDB, NOCREATEROLE e a senha, e em seguida confere todos os atributos em pg_roles: se algum
 * estiver ligado, a transação é desfeita e a chamada falha, sem efeito. As senhas vêm do cofre de segredos do ambiente.
 * Os nomes só mudam nos testes, que não podem mexer nos papéis compartilhados pela bateria.
 */
export async function provisionarPapeis(
  admin: ClientBase,
  senhas: { readonly migrator: string; readonly appRuntime: string },
  nomes: { readonly migrator: string; readonly appRuntime: string } = {
    migrator: 'migrator',
    appRuntime: 'app_runtime',
  },
): Promise<void> {
  const papeis = [
    [nomes.migrator, senhas.migrator],
    [nomes.appRuntime, senhas.appRuntime],
  ] as const;
  await admin.query("SELECT pg_advisory_lock(hashtext('safrion.papeis'))");
  try {
    await admin.query('BEGIN');
    try {
      for (const [papel, senha] of papeis) {
        const existe = await admin.query('SELECT 1 FROM pg_roles WHERE rolname = $1', [papel]);
        const [verbo, atributos] = existe.rowCount
          ? ['ALTER', 'LOGIN NOCREATEDB NOCREATEROLE']
          : ['CREATE', 'LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOREPLICATION'];
        await admin.query(
          `${verbo} ROLE ${admin.escapeIdentifier(papel)} ${atributos} PASSWORD ${admin.escapeLiteral(senha)}`,
        );
      }
      const r = await admin.query<
        Record<(typeof PROIBIDOS)[number] | 'rolcanlogin', boolean> & { rolname: string }
      >(
        `SELECT rolname, ${PROIBIDOS.join(', ')}, rolcanlogin FROM pg_roles WHERE rolname = ANY($1::text[])`,
        [papeis.map(([papel]) => papel)],
      );
      const problemas = r.rows.flatMap((l) => {
        const ligados = PROIBIDOS.filter((a) => l[a]).map((a) => a.slice(3).toUpperCase());
        return [...ligados, ...(l.rolcanlogin ? [] : ['NOLOGIN'])].map((a) => `${l.rolname}: ${a}`);
      });
      if (r.rowCount !== papeis.length) problemas.push('papel ausente depois do provisionamento');
      if (problemas.length > 0) throw new ErroPapeis(problemas);
      await admin.query('COMMIT');
    } catch (erro) {
      await admin.query('ROLLBACK');
      throw erro;
    }
  } finally {
    await admin.query("SELECT pg_advisory_unlock(hashtext('safrion.papeis'))");
  }
}
