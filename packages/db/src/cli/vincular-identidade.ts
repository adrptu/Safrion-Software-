// node packages/db/dist/cli/vincular-identidade.js conceder --ambiente hml --banco <nome> --organizacao <id>
//      --usuario <id> --responsavel <quem autorizou> --motivo <texto curto>
// node packages/db/dist/cli/vincular-identidade.js revogar --ambiente hml --banco <nome> --organizacao <id>
//      --usuario <id> --responsavel <quem autorizou> --motivo <texto curto>
// Vínculo de identidade real em HML (ADR 0004 §11), com o administrador do servidor em SAFRION_ADMIN_URL, que assume o
// papel migrator no banco-alvo. Na concessão, o código de referência entra pela entrada padrão (sem eco no terminal),
// nunca por argumento, que ficaria no histórico e no ps. Saída 0 = concedido, mantido, revogado ou sem vínculo;
// 1 = recusado, nada mudou; 2 = uso incorreto; 3 = falha de infraestrutura, só com códigos. Nenhuma saída traz código,
// subject, hash, senha ou host.
import { pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';

import pg from 'pg';

import { lerIdentidadeAmbiente } from '../ambiente.js';
import { conexaoNoBanco, ErroPreparo } from '../preparo.js';
import { concederVinculo, ErroVinculo, revogarVinculos, validarDestino } from '../vinculo.js';

const USO =
  'Uso: node packages/db/dist/cli/vincular-identidade.js <conceder|revogar> --ambiente hml --banco <nome> ' +
  '--organizacao <id> --usuario <id> --responsavel <quem autorizou> --motivo <texto curto>, com SAFRION_ADMIN_URL ' +
  'definido. Na concessão, o código vem pela entrada padrão.';
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
  let cliente: pg.Client | undefined;
  try {
    // Mesmo servidor, porta e TLS do administrador, no banco-alvo; o modelo nunca conecta.
    cliente = conectar(conexaoNoBanco(new pg.Client({ connectionString: url }), banco));
    cliente.on('error', () => undefined);
    await cliente.connect();
    await cliente.query('SET ROLE migrator');
    if ((await lerIdentidadeAmbiente(cliente)) !== 'hml') throw new ErroVinculo('AMBIENTE_PROIBIDO');
    if (acao === 'conceder') {
      const resultado = await concederVinculo(cliente, { ...destino, codigo });
      escrever(JSON.stringify({ resultado }));
    } else {
      escrever(JSON.stringify(await revogarVinculos(cliente, destino)));
    }
    return 0;
  } catch (erro) {
    if (erro instanceof ErroVinculo || erro instanceof ErroPreparo) {
      escrever(recusado(erro.codigo, erro.message));
      return 1;
    }
    const code = typeof erro === 'object' && erro !== null && 'code' in erro ? erro.code : undefined;
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
  }
}

// Ponto de entrada do processo; a lógica acima é testada com banco real.
if (process.argv[1] !== undefined && import.meta.url === pathToFileURL(process.argv[1]).href) {
  process.exitCode = await executarCli(process.argv.slice(2), process.env, (l) => {
    console.log(l);
  });
}
