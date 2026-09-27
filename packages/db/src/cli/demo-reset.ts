// pnpm run demo:reset -- --confirmar <dev|hml>
// Restaura a demonstração com dados fictícios, conferindo a identidade do ambiente (PRD 23.4). Lê DATABASE_URL (papel
// app_runtime) e SAFRION_AMBIENTE. Saída 0 = feito; 1 = recusado pelas travas, nada foi feito; 2 = uso incorreto.
import { pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';

import pg from 'pg';

import { ErroAmbiente, restaurarDemonstracao } from '../ambiente.js';

export async function executarCli(
  argv: readonly string[],
  env: Readonly<Record<string, string | undefined>>,
  escrever: (linha: string) => void,
): Promise<number> {
  let confirmar: string | undefined;
  // O pnpm 12 repassa o "--" separador ao programa: um "--" inicial não é argumento.
  const args = argv[0] === '--' ? argv.slice(1) : [...argv];
  try {
    confirmar = parseArgs({ args, options: { confirmar: { type: 'string' } }, strict: true }).values
      .confirmar;
  } catch {
    escrever('Uso: pnpm run demo:reset -- --confirmar <dev|hml>');
    return 2;
  }
  const url = env['DATABASE_URL'];
  if (!confirmar || !url) {
    escrever(
      'Uso: pnpm run demo:reset -- --confirmar <dev|hml>, com DATABASE_URL e SAFRION_AMBIENTE definidos.',
    );
    return 2;
  }
  const pool = new pg.Pool({ connectionString: url, max: 1 });
  try {
    const d = await restaurarDemonstracao(pool, { confirmar, ambienteDoProcesso: env['SAFRION_AMBIENTE'] });
    escrever(
      JSON.stringify({
        resultado: 'demonstracao_restaurada',
        ambiente: d.ambiente,
        geracao: d.geracao,
        organizacao: d.organizationId,
      }),
    );
    return 0;
  } catch (erro) {
    if (erro instanceof ErroAmbiente) {
      escrever(JSON.stringify({ resultado: 'recusado', codigo: erro.codigo, mensagem: erro.message }));
      return 1;
    }
    throw erro;
  } finally {
    await pool.end();
  }
}

// Ponto de entrada do processo; a lógica acima é testada com banco real.
if (process.argv[1] !== undefined && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.exitCode = await executarCli(process.argv.slice(2), process.env, (l) => {
    console.log(l);
  });
}
