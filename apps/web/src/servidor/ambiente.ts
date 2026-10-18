import { criarRegistrador, type Registrador } from '@safrion/contracts';
import {
  criarConectorGoogle,
  ErroConexao,
  LIMITE_CONEXAO_MS,
  prepararConexao,
  type Conexao,
  type PrepararConexao,
} from '@safrion/db/web';
import pg from 'pg';

/**
 * Dependências do servidor web, lidas do ambiente uma vez: banco com o papel app_runtime, origem configurada da aplicação
 * (Origin e redirecionamentos nunca vêm da requisição) e registrador de uma linha JSON por evento, sem texto livre.
 */
export interface Dependencias {
  readonly banco: pg.Pool;
  readonly origem: string;
  readonly registrador: Registrador;
  readonly versao: string;
  readonly commit: string;
  readonly ambienteDoProcesso: string | undefined;
}

// Em globalThis, não numa variável do módulo: o Next compila a instrumentação e as rotas separadamente, e cada uma pode
// ter a sua cópia deste módulo. Symbol.for dá a mesma chave às duas.
const CHAVE = Symbol.for('safrion.web.dependencias');
const guardadas = globalThis as typeof globalThis & { [CHAVE]?: Dependencias };

const comInstancia = () => process.env['SAFRION_CLOUDSQL_INSTANCIA'] !== undefined;

function lerAmbiente() {
  const url = process.env['DATABASE_URL'];
  const origem = process.env['SAFRION_ORIGEM'];
  if (!url || !origem) throw new Error('DATABASE_URL e SAFRION_ORIGEM são obrigatórios no servidor web.');
  const versao = process.env['SAFRION_VERSAO'] ?? '0.0.0-dev';
  const commit = process.env['SAFRION_COMMIT'] ?? 'desconhecido';
  const registrador = criarRegistrador({
    servico: 'web',
    versao,
    escrever: (linha) => {
      process.stdout.write(`${linha}\n`);
    },
    agora: () => new Date().toISOString(),
  });
  return { url, origem, versao, commit, registrador };
}

function montar(base: ReturnType<typeof lerAmbiente>, extra: Conexao['extra']): Dependencias {
  const { url, origem, versao, commit, registrador } = base;
  // Pool pequeno por instância (plano R-006, passo 11). Erro de conexão ociosa não derruba o processo nem vai ao log
  // com mensagem do driver: só o código. Prazo por aquisição igual ao da HML em todos os ambientes, e não prazo HTTP
  // total (contrato CMD-15 §9.2); o conector da HML repete o mesmo valor no `extra`.
  const banco = new pg.Pool({
    connectionString: url,
    max: 3,
    connectionTimeoutMillis: LIMITE_CONEXAO_MS,
    ...extra,
  });
  banco.on('error', (erro: Error & { code?: unknown }) => {
    registrador.registrar('erro', 'banco.conexao_ociosa', 'sem-correlacao', {
      codigo: typeof erro.code === 'string' && /^[0-9A-Z]{5}$/.test(erro.code) ? erro.code : undefined,
    });
  });
  return { banco, origem, registrador, versao, commit, ambienteDoProcesso: process.env['SAFRION_AMBIENTE'] };
}

export function dependencias(): Dependencias {
  const prontas = guardadas[CHAVE];
  if (prontas) return prontas;
  if (comInstancia()) {
    throw new Error(
      'Com SAFRION_CLOUDSQL_INSTANCIA, a conexão com o banco é preparada na subida (instrumentation.ts) e não está pronta.',
    );
  }
  const novas = montar(lerAmbiente(), {});
  guardadas[CHAVE] = novas;
  return novas;
}

const prepararPadrao: PrepararConexao = (env) => prepararConexao(env, { criarConector: criarConectorGoogle });

/**
 * Subida com o Cloud SQL por IP privado (R-006, GCP-0017): prepara o conector, espera o banco responder à sonda (com
 * clientes dela, não do pool) e só então cria o pool, antes de o servidor atender. Sem SAFRION_CLOUDSQL_INSTANCIA, não
 * faz nada e dependencias() segue como antes. Na falha, fecha o conector, registra só o código e lança um erro sem
 * texto do conector nem do driver. A preparação é injetável para teste.
 */
export async function prepararDependencias(preparar: PrepararConexao = prepararPadrao): Promise<void> {
  if (!comInstancia() || guardadas[CHAVE]) return;
  const base = lerAmbiente();
  let conexao: Conexao | undefined;
  try {
    conexao = await preparar(process.env);
    await conexao.aguardar({ connectionString: base.url });
    guardadas[CHAVE] = montar(base, conexao.extra);
  } catch (erro) {
    conexao?.fechar();
    const codigo = erro instanceof ErroConexao ? erro.codigo : undefined;
    base.registrador.registrar('erro', 'banco.subida', 'sem-correlacao', { codigo });
    throw erro instanceof ErroConexao ? erro : new Error('Falha ao preparar a conexão com o banco.');
  }
}
