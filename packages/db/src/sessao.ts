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
 * Mensagens com que o pg-pool fixado (3.14.0) rejeita a aquisição quando `connectionTimeoutMillis` acaba: na fila do
 * pool cheio e ao abrir uma conexão nova. A detecção depende delas; o teste de integração falha se mudarem.
 */
const PRAZO_DE_AQUISICAO = new Set([
  'timeout exceeded when trying to connect',
  'Connection terminated due to connection timeout',
]);
/** Sugestão de espera antes de repetir (Retry-After de 1 s). Decisão técnica, ainda sem medição que a sustente. */
export const REPETIR_AQUISICAO_MS = 1000;

/**
 * Empresta uma conexão do pool. Só a rejeição por prazo de aquisição vira FALHA_TRANSITORIA legível (contrato CMD-15
 * §9.2): nenhum comando SQL desta tentativa rodou. Num comando, `resultadoIncerto: false` descreve só esta tentativa,
 * nunca uma intenção anterior com a mesma chave; na leitura o campo não aparece. Qualquer outra falha passa intacta.
 */
export async function emprestarConexao(pool: Pool, uso: 'comando' | 'leitura'): Promise<PoolClient> {
  try {
    return await pool.connect();
  } catch (erro) {
    if (!(erro instanceof Error) || !PRAZO_DE_AQUISICAO.has(erro.message)) throw erro;
    throw new ErroComando(
      'FALHA_TRANSITORIA',
      uso === 'comando'
        ? 'Não houve conexão livre com o banco a tempo e esta tentativa não começou; repita com a mesma chave e o mesmo conteúdo.'
        : 'Não houve conexão livre com o banco a tempo; tente de novo em instantes.',
      uso === 'comando'
        ? { resultadoIncerto: false, repetirEmMs: REPETIR_AQUISICAO_MS }
        : { repetirEmMs: REPETIR_AQUISICAO_MS },
      { cause: erro },
    );
  }
}

/**
 * Cliente emprestado do pool com ouvinte de 'error' até ser devolvido (CX-R03). Quando a conexão cai, o pg aborta a
 * consulta em curso (a falha chega a quem chamou por ela) e ainda emite 'error' no cliente; sem ouvinte, isso vira
 * exceção não tratada e derruba o processo, porque o pool só ouve os clientes ociosos. O erro ouvido não é engolido:
 * retira a conexão do pool na devolução, para a próxima sessão não receber uma conexão morta.
 */
export function ouvirConexao(cliente: PoolClient): { soltar(erro?: Error): void } {
  let caiu: Error | undefined;
  const ouvir = (erro: Error) => {
    caiu ??= erro;
  };
  cliente.on('error', ouvir);
  return {
    soltar(erro?: Error) {
      cliente.off('error', ouvir);
      cliente.release(erro ?? caiu);
    },
  };
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
  const cliente = await emprestarConexao(pool, 'leitura');
  const conexao = ouvirConexao(cliente);
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
    conexao.soltar(quebrado);
  }
}
