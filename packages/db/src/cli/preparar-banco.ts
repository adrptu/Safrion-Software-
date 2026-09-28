// node packages/db/dist/cli/preparar-banco.js --ambiente <dev|hml> --banco <nome>
// Prepara o banco de um ambiente com o administrador do servidor (PRD 27; ADR 0004): papéis, banco com dono migrator,
// migrações e identidade do ambiente. Idempotente. Lê SAFRION_ADMIN_URL (administrador, banco postgres),
// SAFRION_SENHA_MIGRATOR e SAFRION_SENHA_APP_RUNTIME (as mesmas senhas que a aplicação e o migrator usam, vindas do
// cofre de segredos). Com SAFRION_CLOUDSQL_INSTANCIA, toda conexão passa pelo conector em IP privado (conexao.ts).
// Saída 0 = preparado; 1 = recusado pelas travas, nada além do já relatado mudou; 2 = uso incorreto; 3 = falha de
// infraestrutura, relatada só por códigos (F0B2-01): nenhuma senha, host ou mensagem do driver sai daqui.
import { pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';

import pg from 'pg';

import { ErroAmbiente } from '../ambiente.js';
import { criarConectorGoogle } from '../conector-google.js';
import {
  ErroConexao,
  prepararConexao,
  sairNaRejeicaoSolta,
  sondaPorCliente,
  type Conexao,
  type PrepararConexao,
} from '../conexao.js';
import { ErroPapeis } from '../papeis.js';
import { ErroPreparo, prepararBanco, validarOpcoes } from '../preparo.js';

const se = (v: unknown, formato: RegExp) => (typeof v === 'string' && formato.test(v) ? v : undefined);
const USO =
  'Uso: node packages/db/dist/cli/preparar-banco.js --ambiente <dev|hml> --banco <nome>, com SAFRION_ADMIN_URL, ' +
  'SAFRION_SENHA_MIGRATOR e SAFRION_SENHA_APP_RUNTIME definidos.';

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
    codigo_tecnico: se(code, /^[0-9A-Z_]{5,40}$/),
  };
}

export async function executarCli(
  argv: readonly string[],
  env: Readonly<Record<string, string | undefined>>,
  escrever: (linha: string) => void,
  conectar: (config: pg.ClientConfig) => pg.Client = (config) => new pg.Client(config),
  preparar: PrepararConexao = (e) => prepararConexao(e, { criarConector: criarConectorGoogle }),
): Promise<number> {
  const args = argv[0] === '--' ? argv.slice(1) : [...argv];
  let valores: { ambiente?: string | undefined; banco?: string | undefined };
  try {
    valores = parseArgs({
      args,
      options: { ambiente: { type: 'string' }, banco: { type: 'string' } },
      strict: true,
    }).values;
  } catch {
    escrever(USO);
    return 2;
  }
  const url = env['SAFRION_ADMIN_URL'];
  const senhaMigrator = env['SAFRION_SENHA_MIGRATOR'];
  const senhaApp = env['SAFRION_SENHA_APP_RUNTIME'];
  if (!valores.ambiente || !valores.banco || !url || !senhaMigrator || !senhaApp) {
    escrever(USO);
    return 2;
  }
  const opcoes = {
    ambiente: valores.ambiente,
    banco: valores.banco,
    senhas: { migrator: senhaMigrator, appRuntime: senhaApp },
  };
  // Opção recusada não abre conexão nenhuma (HML-PREP-02): produção e nome inválido param aqui.
  try {
    validarOpcoes(opcoes);
  } catch (erro) {
    if (!(erro instanceof ErroPreparo)) throw erro;
    escrever(JSON.stringify({ resultado: 'recusado', codigo: erro.codigo, mensagem: erro.message }));
    return 1;
  }
  let admin: pg.Client | undefined;
  let conexao: Conexao | undefined;
  try {
    conexao = await preparar(env);
    const { extra } = conexao;
    // O preparo abre clientes no banco-alvo com o mesmo conectar: todos recebem o conector, não só o do administrador.
    const conectarComExtra = (config: pg.ClientConfig) => conectar({ ...config, ...extra });
    await conexao.aguardar(sondaPorCliente(() => conectarComExtra({ connectionString: url })));
    admin = conectarComExtra({ connectionString: url });
    admin.on('error', () => undefined);
    await admin.connect();
    const r = await prepararBanco(admin, opcoes, conectarComExtra);
    escrever(
      JSON.stringify({
        resultado: 'preparado',
        ambiente: r.ambiente,
        banco: r.banco,
        migracoes_aplicadas: r.migracoes.aplicadas,
        migracoes_ja_aplicadas: r.migracoes.jaAplicadas.length,
        identidade: r.identidade,
      }),
    );
    return 0;
  } catch (erro) {
    if (erro instanceof ErroPreparo || erro instanceof ErroAmbiente) {
      escrever(JSON.stringify({ resultado: 'recusado', codigo: erro.codigo, mensagem: erro.message }));
      return 1;
    }
    if (erro instanceof ErroPapeis && erro.codigo === 'ATRIBUTO_PROIBIDO') {
      escrever(JSON.stringify({ resultado: 'recusado', codigo: erro.codigo, efeito: erro.detalhe.efeito }));
      return 1;
    }
    escrever(JSON.stringify(falhaSemTextoLivre(erro)));
    return 3;
  } finally {
    await admin?.end().catch(() => undefined);
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
