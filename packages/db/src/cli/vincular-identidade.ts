// node packages/db/dist/cli/vincular-identidade.js conceder --ambiente hml --banco <nome> --organizacao <id>
//      --usuario <id> --responsavel <quem autorizou> --motivo <texto curto>
// node packages/db/dist/cli/vincular-identidade.js revogar --ambiente hml --banco <nome> --organizacao <id>
//      --usuario <id> --responsavel <quem autorizou> --motivo <texto curto>
// node packages/db/dist/cli/vincular-identidade.js fila --ambiente hml --banco <nome>
// Vínculo de identidade real em HML (ADR 0004 §11), com o administrador do servidor em SAFRION_ADMIN_URL, que assume o
// papel migrator no banco-alvo; com SAFRION_CLOUDSQL_INSTANCIA, pelo conector em IP privado (conexao.ts). Na
// concessão, o código de referência entra pela entrada padrão (sem eco no terminal), nunca por argumento, que ficaria
// no histórico e no ps. Saída 0 = concedido, mantido, revogado ou sem vínculo;
// 1 = recusado, nada mudou; 2 = uso incorreto; 3 = falha de infraestrutura, só com códigos. Nenhuma saída traz código,
// subject, hash, senha ou host.
// Em modo fila (job safrion-vinculo; R-006, GCP-0017, §3c), cada pedido é uma versão do segredo em
// SAFRION_PEDIDO_SEGREDO (projects/<projeto>/secrets/hml-vinculo-pedido), lida pela API com o token do servidor de
// metadados; a saída segue vinculo-fila.ts: 0 = tudo aplicado, 1 = OCUPADO ou algum pedido recusado, 3 = a fila parou.
import { pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';

import pg from 'pg';

import { lerIdentidadeAmbiente } from '../ambiente.js';
import { criarConectorGoogle } from '../conector-google.js';
import {
  ErroConexao,
  prepararConexao,
  sairNaRejeicaoSolta,
  type Conexao,
  type PrepararConexao,
} from '../conexao.js';
import { conexaoNoBanco, ErroPreparo } from '../preparo.js';
import { criarSegredoPedido, ErroSegredo, type SegredoPedido } from '../segredo-pedido.js';
import { concederVinculo, ErroVinculo, revogarVinculos, validarDestino } from '../vinculo.js';
import { processarFila } from '../vinculo-fila.js';

const USO =
  'Uso: node packages/db/dist/cli/vincular-identidade.js <conceder|revogar> --ambiente hml --banco <nome> ' +
  '--organizacao <id> --usuario <id> --responsavel <quem autorizou> --motivo <texto curto>, com SAFRION_ADMIN_URL ' +
  'definido. Na concessão, o código vem pela entrada padrão. Em modo fila: fila --ambiente hml --banco <nome>, com ' +
  'SAFRION_ADMIN_URL e SAFRION_PEDIDO_SEGREDO definidos.';
const BANCO = /^[a-z][a-z0-9_]{0,62}$/;
const se = (v: unknown, formato: RegExp) => (typeof v === 'string' && formato.test(v) ? v : undefined);

function recusado(codigo: string, mensagem: string) {
  return JSON.stringify({ resultado: 'recusado', codigo, mensagem });
}

/** Lê uma linha da entrada padrão. No terminal, pergunta no stderr e não ecoa o que é digitado. */
export function lerDaEntrada(entrada: NodeJS.ReadStream = process.stdin): Promise<string> {
  return new Promise((resolve, reject) => {
    let texto = '';
    const terminal = entrada.isTTY;
    if (terminal) {
      process.stderr.write('Código de referência (não aparece na tela): ');
      entrada.setRawMode(true);
    }
    entrada.setEncoding('utf8');
    const fim = (valor: string | Error) => {
      entrada.off('data', aoLer);
      entrada.off('end', aoTerminar);
      if (terminal) {
        entrada.setRawMode(false);
        process.stderr.write('\n');
      }
      entrada.pause();
      if (valor instanceof Error) reject(valor);
      else resolve(valor);
    };
    const aoLer = (parte: string) => {
      for (const c of parte) {
        if (c === '\u0003') {
          fim(new Error('INTERROMPIDO'));
          return;
        }
        if (c === '\r' || c === '\n') {
          fim(texto);
          return;
        }
        if (c === '\u007f' || c === '\b') texto = texto.slice(0, -1);
        else texto += c;
      }
    };
    const aoTerminar = () => {
      fim(texto);
    };
    entrada.on('data', aoLer);
    entrada.on('end', aoTerminar);
    entrada.resume();
  });
}

export async function executarCli(
  argv: readonly string[],
  env: Readonly<Record<string, string | undefined>>,
  escrever: (linha: string) => void,
  lerCodigo: () => Promise<string> = () => lerDaEntrada(),
  conectar: (config: pg.ClientConfig) => pg.Client = (config) => new pg.Client(config),
  preparar: PrepararConexao = (e) => prepararConexao(e, { criarConector: criarConectorGoogle }),
  criarSegredo: (nome: string) => SegredoPedido = (nome) => criarSegredoPedido(nome),
): Promise<number> {
  const args = argv[0] === '--' ? argv.slice(1) : [...argv];
  let lidos: { values: Record<string, string | undefined>; positionals: string[] };
  try {
    lidos = parseArgs({
      args,
      allowPositionals: true,
      strict: true,
      options: {
        ambiente: { type: 'string' },
        banco: { type: 'string' },
        organizacao: { type: 'string' },
        usuario: { type: 'string' },
        responsavel: { type: 'string' },
        motivo: { type: 'string' },
      },
    });
  } catch {
    escrever(USO);
    return 2;
  }
  const [acao, ...sobra] = lidos.positionals;
  const { ambiente, banco, organizacao, usuario, responsavel, motivo } = lidos.values;
  const url = env['SAFRION_ADMIN_URL'];
  if (acao === 'fila') {
    const segredo = env['SAFRION_PEDIDO_SEGREDO'];
    // Na fila, o destino vem de cada pedido: opção de destino é uso incorreto.
    if (
      sobra.length > 0 ||
      !ambiente ||
      !banco ||
      !url ||
      !segredo ||
      organizacao ||
      usuario ||
      responsavel ||
      motivo
    ) {
      escrever(USO);
      return 2;
    }
    return executarFila({ ambiente, banco, url, segredo }, env, escrever, conectar, preparar, criarSegredo);
  }
  if (
    (acao !== 'conceder' && acao !== 'revogar') ||
    sobra.length > 0 ||
    !ambiente ||
    !banco ||
    !organizacao ||
    !usuario ||
    !responsavel ||
    !motivo ||
    !url
  ) {
    escrever(USO);
    return 2;
  }
  // Tudo conferido antes de ler o código e de abrir conexão.
  if (ambiente !== 'hml') {
    escrever(recusado('AMBIENTE_PROIBIDO', 'Vínculo de identidade real só em hml; nada foi alterado.'));
    return 1;
  }
  const destino = { organizacao, usuario, responsavel, motivo };
  try {
    if (!BANCO.test(banco)) throw new ErroVinculo('OPCAO_INVALIDA');
    validarDestino(destino);
  } catch (erro) {
    if (!(erro instanceof ErroVinculo)) throw erro;
    escrever(recusado(erro.codigo, erro.message));
    return 1;
  }
  let codigo = '';
  if (acao === 'conceder') {
    try {
      codigo = await lerCodigo();
    } catch {
      escrever(recusado('CODIGO_INVALIDO', 'O código não foi lido; nada foi alterado.'));
      return 1;
    }
  }
  return comoMigrator(url, banco, env, escrever, conectar, preparar, async (cliente) => {
    if (acao === 'conceder') {
      const resultado = await concederVinculo(cliente, { ...destino, codigo });
      escrever(JSON.stringify({ resultado }));
    } else {
      escrever(JSON.stringify(await revogarVinculos(cliente, destino)));
    }
    return 0;
  });
}

/**
 * Modo fila: tudo conferido antes de abrir conexão; a conexão é dedicada (um pg.Client) e a fila decide a saída. O
 * segredo só é lido depois da trava da fila (vinculo-fila.ts).
 */
async function executarFila(
  o: { readonly ambiente: string; readonly banco: string; readonly url: string; readonly segredo: string },
  env: Readonly<Record<string, string | undefined>>,
  escrever: (linha: string) => void,
  conectar: (config: pg.ClientConfig) => pg.Client,
  preparar: PrepararConexao,
  criarSegredo: (nome: string) => SegredoPedido,
): Promise<number> {
  if (o.ambiente !== 'hml') {
    escrever(recusado('AMBIENTE_PROIBIDO', 'Vínculo de identidade real só em hml; nada foi alterado.'));
    return 1;
  }
  let segredo: SegredoPedido;
  try {
    if (!BANCO.test(o.banco)) throw new ErroVinculo('OPCAO_INVALIDA');
    segredo = criarSegredo(o.segredo);
  } catch (erro) {
    if (!(erro instanceof ErroVinculo || erro instanceof ErroSegredo)) throw erro;
    escrever(recusado(erro.codigo, erro.message));
    return 1;
  }
  return comoMigrator(o.url, o.banco, env, escrever, conectar, preparar, (cliente) =>
    processarFila({ cliente, segredo, registrar: escrever }),
  );
}

/**
 * Conexão dedicada no banco-alvo, como migrator, só em banco identificado como hml; recusa de negócio sai com 1 e
 * falha de infraestrutura com 3, só com códigos. Encerra o cliente e o conector no fim.
 */
async function comoMigrator(
  url: string,
  banco: string,
  env: Readonly<Record<string, string | undefined>>,
  escrever: (linha: string) => void,
  conectar: (config: pg.ClientConfig) => pg.Client,
  preparar: PrepararConexao,
  trabalho: (cliente: pg.Client) => Promise<number>,
): Promise<number> {
  let cliente: pg.Client | undefined;
  let conexao: Conexao | undefined;
  try {
    conexao = await preparar(env);
    const { extra } = conexao;
    // Mesmo servidor, porta e TLS do administrador, no banco-alvo; o modelo nunca conecta.
    const alvo = conexaoNoBanco(new pg.Client({ connectionString: url }), banco);
    await conexao.aguardar(alvo, { abrir: conectar });
    cliente = conectar({ ...alvo, ...extra });
    cliente.on('error', () => undefined);
    await cliente.connect();
    await cliente.query('SET ROLE migrator');
    if ((await lerIdentidadeAmbiente(cliente)) !== 'hml') throw new ErroVinculo('AMBIENTE_PROIBIDO');
    return await trabalho(cliente);
  } catch (erro) {
    if (erro instanceof ErroVinculo || erro instanceof ErroPreparo) {
      escrever(recusado(erro.codigo, erro.message));
      return 1;
    }
    const code =
      erro instanceof ErroConexao
        ? erro.codigo
        : typeof erro === 'object' && erro !== null && 'code' in erro
          ? erro.code
          : undefined;
    escrever(
      JSON.stringify({
        resultado: 'falha',
        codigo: 'FALHA_INFRAESTRUTURA',
        erro_tipo: erro instanceof Error ? se(erro.name, /^[A-Za-z]{1,64}$/) : typeof erro,
        codigo_tecnico: se(code, /^[0-9A-Z_]{5,40}$/),
      }),
    );
    return 3;
  } finally {
    await cliente?.end().catch(() => undefined);
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
