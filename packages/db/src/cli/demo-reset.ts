// pnpm run demo:reset -- --confirmar <dev|hml>
// Restaura a demonstração com dados fictícios, conferindo a identidade do ambiente (PRD 23.4). Lê DATABASE_URL (papel
// app_runtime) e SAFRION_AMBIENTE; com SAFRION_CLOUDSQL_INSTANCIA, conecta pelo conector em IP privado (conexao.ts).
// Saída 0 = feito; 1 = recusado pelas travas, nada foi feito; 2 = uso incorreto; 3 = falha de infraestrutura (banco
// fora do ar, endereço, banco ou senha inválidos, conector ou banco privado indisponível), relatada só por códigos
// (F0B2-01): mensagem, stack e propriedades do erro do driver trazem host, usuário ou nome do banco e não vão à tela nem
// ao log da CI.
// No sucesso, a saída traz a organização e o id e o papel de cada usuário fictício da geração nova: é o que o operador
// passa ao vincular-identidade em HML. Nunca o subject de desenvolvimento.
import { pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';

import pg from 'pg';

import { ErroAmbiente, restaurarDemonstracao } from '../ambiente.js';
import { criarConectorGoogle } from '../conector-google.js';
import {
  ErroConexao,
  prepararConexao,
  sairNaRejeicaoSolta,
  type Conexao,
  type PrepararConexao,
} from '../conexao.js';

const se = (v: unknown, formato: RegExp) => (typeof v === 'string' && formato.test(v) ? v : undefined);

function falhaSemTextoLivre(erro: unknown) {
  const code =
    erro instanceof ErroConexao
      ? erro.codigo
      : typeof erro === 'object' && erro !== null && 'code' in erro
        ? erro.code
        : undefined;
  return {
    resultado: 'falha',
    codigo: 'FALHA_INFRAESTRUTURA',
    erro_tipo: erro instanceof Error ? se(erro.name, /^[A-Za-z]{1,64}$/) : typeof erro,
    // SQLSTATE do PostgreSQL (3D000, 28P01), código do Node (ENOTFOUND, ECONNREFUSED, ERR_INVALID_URL) ou da conexão
    // privada (CONECTOR_INDISPONIVEL, BANCO_INDISPONIVEL).
    codigo_tecnico: se(code, /^[0-9A-Z_]{5,40}$/),
  };
}

export async function executarCli(
  argv: readonly string[],
  env: Readonly<Record<string, string | undefined>>,
  escrever: (linha: string) => void,
  preparar: PrepararConexao = (e) => prepararConexao(e, { criarConector: criarConectorGoogle }),
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
  let conexao: Conexao | undefined;
  let pool: pg.Pool | undefined;
  try {
    conexao = await preparar(env);
    pool = new pg.Pool({ connectionString: url, max: 1, ...conexao.extra });
    await conexao.aguardar(pool);
    const d = await restaurarDemonstracao(pool, { confirmar, ambienteDoProcesso: env['SAFRION_AMBIENTE'] });
    escrever(
      JSON.stringify({
        resultado: 'demonstracao_restaurada',
        ambiente: d.ambiente,
        geracao: d.geracao,
        organizacao: d.organizationId,
        usuarios: d.usuarios.map((u) => ({ papel: u.papel, usuario: u.usuarioId })),
      }),
    );
    return 0;
  } catch (erro) {
    if (erro instanceof ErroAmbiente) {
      escrever(JSON.stringify({ resultado: 'recusado', codigo: erro.codigo, mensagem: erro.message }));
      return 1;
    }
    escrever(JSON.stringify(falhaSemTextoLivre(erro)));
    return 3;
  } finally {
    await pool?.end().catch(() => undefined);
    conexao?.fechar();
  }
}

// Ponto de entrada do processo; a lógica acima é testada com banco real. Rejeição solta sai com 3, só com códigos.
if (process.argv[1] !== undefined && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const escrever = (l: string) => {
    console.log(l);
  };
  sairNaRejeicaoSolta(escrever);
  process.exitCode = await executarCli(process.argv.slice(2), process.env, escrever);
}
