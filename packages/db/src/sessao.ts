import type { Pool, PoolClient } from 'pg';

import { ErroComando } from './erros.js';

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

/** UUID em minúsculas, no formato canônico. */
export function ehUuid(valor: unknown): valor is string {
  return typeof valor === 'string' && UUID.test(valor);
}

/** A organização vem da sessão ou da credencial validada, nunca do conteúdo do comando (ENG-021; IDEM-12). */
export function organizacaoValida(valor: unknown): string {
  if (!ehUuid(valor)) {
    throw new ErroComando('ORGANIZACAO_INVALIDA', 'A sessão não tem uma organização válida.');
  }
  return valor;
}

/**
 * Abre uma transação com a organização fixada só nela (set_config com is_local): ao terminar, a conexão volta ao pool
 * sem organização, e a próxima transação que esquecer de fixá-la não vê nenhuma linha (falha fechada, ENG-025).
 */
export async function emOrganizacao<T>(
  pool: Pool,
  organizationId: string,
  fn: (cliente: PoolClient) => Promise<T>,
): Promise<T> {
  const org = organizacaoValida(organizationId);
  const cliente = await pool.connect();
  let quebrado: Error | undefined;
  try {
    await cliente.query('BEGIN');
    await cliente.query("SELECT set_config('app.organization_id', $1, true)", [org]);
    const resultado = await fn(cliente);
    await cliente.query('COMMIT');
    return resultado;
  } catch (erro) {
    try {
      await cliente.query('ROLLBACK');
    } catch (falhaRollback) {
      quebrado = falhaRollback instanceof Error ? falhaRollback : new Error(String(falhaRollback));
    }
    throw erro;
  } finally {
    cliente.release(quebrado);
  }
}
