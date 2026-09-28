import type { ClientBase } from 'pg';

const PROIBIDOS = ['rolsuper', 'rolbypassrls', 'rolreplication', 'rolcreaterole', 'rolcreatedb'] as const;
const TRAVAR = "SELECT pg_advisory_lock(hashtext('safrion.papeis'))";
const DESTRAVAR = "SELECT pg_advisory_unlock(hashtext('safrion.papeis'))";

export type CodigoErroPapeis =
  | 'ATRIBUTO_PROIBIDO' // papel com atributo que nenhum dos dois pode ter; nada foi gravado
  | 'FALHA_NO_BANCO' // o banco recusou ou a conexão caiu; a causa original fica em `cause`
  | 'LIMPEZA_FALHOU'; // os papéis foram gravados, mas a trava não pôde ser liberada nesta conexão

/**
 * Falha do provisionamento, só com códigos e nomes de papel: nunca senha nem mensagem do driver. `efeito` diz o que ficou
 * no banco: nada, gravado, ou incerto (a confirmação foi enviada e a resposta não chegou). Se `limpezaFalhou` não estiver
 * vazio, encerre esta conexão: o servidor desfaz a transação aberta e libera a trava.
 */
export class ErroPapeis extends Error {
  override readonly name = 'ErroPapeis';
  constructor(
    readonly codigo: CodigoErroPapeis,
    readonly detalhe: {
      readonly efeito: 'nenhum' | 'gravado' | 'incerto';
      readonly limpezaFalhou: readonly ('ROLLBACK' | 'DESBLOQUEIO')[];
      readonly problemas?: readonly string[];
      readonly codigoPg?: string | undefined;
    },
    opcoes: { readonly cause?: unknown } = {},
  ) {
    const principal = {
      ATRIBUTO_PROIBIDO: `Papel com atributo proibido (${(detalhe.problemas ?? []).join('; ')}); nada foi alterado. Corrija o papel e repita.`,
      FALHA_NO_BANCO:
        detalhe.efeito === 'incerto'
          ? 'A confirmação foi enviada e a resposta não chegou; o resultado é incerto. Confira os papéis antes de repetir.'
          : `O banco recusou o provisionamento (SQLSTATE ${detalhe.codigoPg ?? 'ausente'}); nada foi alterado.`,
      LIMPEZA_FALHOU: 'Papéis gravados, mas a trava não foi liberada nesta conexão.',
    }[codigo];
    const limpeza = detalhe.limpezaFalhou.length
      ? ` Limpeza que falhou: ${detalhe.limpezaFalhou.join(', ')}; encerre esta conexão.`
      : '';
    super(principal + limpeza, opcoes);
  }
}

function sqlstate(erro: unknown): string | undefined {
  const code = typeof erro === 'object' && erro !== null && 'code' in erro ? erro.code : undefined;
  return typeof code === 'string' && /^[0-9A-Z]{5}$/.test(code) ? code : undefined;
}

/**
 * Cria ou atualiza os dois papéis de banco (plano R-006, passo 7): migrator, dono das tabelas e usado só pela migração;
 * app_runtime, usado pela aplicação. Nenhum dos dois pode ter SUPERUSER, BYPASSRLS, REPLICATION, CREATEROLE nem CREATEDB.
 * Roda com um papel administrativo que, no Cloud SQL, não é superusuário: ele cria o papel com todos os atributos, mas
 * não pode reafirmar NOSUPERUSER, NOBYPASSRLS nem NOREPLICATION num papel existente (42501). Por isso a repetição só
 * reafirma LOGIN, NOCREATEDB, NOCREATEROLE e a senha, e em seguida confere todos os atributos em pg_roles: se algum
 * estiver ligado, a transação é desfeita e a chamada falha, sem efeito. Uma falha na limpeza (ROLLBACK, liberação da
 * trava) nunca substitui a causa original; ela é informada à parte (HML-A1-02). As senhas vêm do cofre de segredos do
 * ambiente. Os nomes só mudam nos testes, que não podem mexer nos papéis compartilhados pela bateria.
 *
 * Cria também o papel das funções de sessão (app_sessao, migração 0003; ADR 0004 §3): NOLOGIN, sem atributo
 * privilegiado, dono das funções SECURITY DEFINER. O migrator recebe esse papel sem herança e com SET, só para poder
 * entregar a posse das funções; o app_runtime não pode ter filiação a papel algum (aceite A5), e isso é conferido aqui.
 */
export async function provisionarPapeis(
  admin: ClientBase,
  senhas: { readonly migrator: string; readonly appRuntime: string },
  nomes: { readonly migrator: string; readonly appRuntime: string; readonly sessao: string } = {
    migrator: 'migrator',
    appRuntime: 'app_runtime',
    sessao: 'app_sessao',
  },
): Promise<void> {
  const papeis = [
    [nomes.migrator, senhas.migrator],
    [nomes.appRuntime, senhas.appRuntime],
  ] as const;
  const limpezaFalhou: ('ROLLBACK' | 'DESBLOQUEIO')[] = [];
  let travado = false;
  let commitEnviado = false;
  let falha: { readonly erro: unknown } | undefined;
  let problemas: string[] = [];
  try {
    await admin.query(TRAVAR);
    travado = true;
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
      const sessao = admin.escapeIdentifier(nomes.sessao);
      const existeSessao = await admin.query('SELECT 1 FROM pg_roles WHERE rolname = $1', [nomes.sessao]);
      await admin.query(
        existeSessao.rowCount
          ? `ALTER ROLE ${sessao} NOLOGIN NOCREATEDB NOCREATEROLE`
          : `CREATE ROLE ${sessao} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOREPLICATION`,
      );
      await admin.query(
        `GRANT ${sessao} TO ${admin.escapeIdentifier(nomes.migrator)} WITH INHERIT FALSE, SET TRUE`,
      );
      const todos = [...papeis.map(([papel]) => papel), nomes.sessao];
      const r = await admin.query<
        Record<(typeof PROIBIDOS)[number] | 'rolcanlogin' | 'filiado', boolean> & { rolname: string }
      >(
        `SELECT r.rolname, ${PROIBIDOS.map((a) => `r.${a}`).join(', ')}, r.rolcanlogin,
                EXISTS (SELECT 1 FROM pg_auth_members m WHERE m.member = r.oid) AS filiado
           FROM pg_roles r WHERE r.rolname = ANY($1::text[])`,
        [todos],
      );
      problemas = r.rows.flatMap((l) => {
        const ligados = PROIBIDOS.filter((a) => l[a]).map((a) => a.slice(3).toUpperCase());
        const eSessao = l.rolname === nomes.sessao;
        // O papel das funções não faz login; os outros dois fazem. Só o app_runtime não pode ter filiação alguma.
        const login = eSessao ? (l.rolcanlogin ? ['LOGIN'] : []) : l.rolcanlogin ? [] : ['NOLOGIN'];
        const filiacao = l.rolname === nomes.appRuntime && l.filiado ? ['FILIACAO'] : [];
        return [...ligados, ...login, ...filiacao].map((a) => `${l.rolname}: ${a}`);
      });
      if (r.rowCount !== todos.length) problemas.push('papel ausente depois do provisionamento');
      if (problemas.length === 0) {
        commitEnviado = true;
        await admin.query('COMMIT');
      }
    } finally {
      if (!commitEnviado) {
        try {
          await admin.query('ROLLBACK');
        } catch {
          limpezaFalhou.push('ROLLBACK');
        }
      }
    }
  } catch (erro) {
    falha = { erro };
  }
  if (travado) {
    try {
      await admin.query(DESTRAVAR);
    } catch {
      limpezaFalhou.push('DESBLOQUEIO');
    }
  }
  if (falha) {
    // Antes do COMMIT, nada foi gravado: a transação sem confirmação é descartada, mesmo que a conexão tenha caído.
    throw new ErroPapeis(
      'FALHA_NO_BANCO',
      { efeito: commitEnviado ? 'incerto' : 'nenhum', limpezaFalhou, codigoPg: sqlstate(falha.erro) },
      { cause: falha.erro },
    );
  }
  if (problemas.length > 0) {
    throw new ErroPapeis('ATRIBUTO_PROIBIDO', { efeito: 'nenhum', limpezaFalhou, problemas });
  }
  if (limpezaFalhou.length > 0) {
    throw new ErroPapeis('LIMPEZA_FALHOU', { efeito: 'gravado', limpezaFalhou });
  }
}
