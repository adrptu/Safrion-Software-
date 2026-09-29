import type { Duplex } from 'node:stream';

import pg from 'pg';

/**
 * Conexão com o Cloud SQL por IP privado (R-006, GCP-0017, opção A). Sem IP público, a web e os jobs chegam ao banco
 * pela VPC com o conector oficial em `ipType` PRIVATE, que faz o TLS mútuo exigido por `connector_enforcement =
 * REQUIRED`. Só entra com SAFRION_CLOUDSQL_INSTANCIA; sem ela (desenvolvimento, CI e testes), nada muda: a URL comum
 * segue sozinha e o conector nem é criado. Com o conector, a URL não leva sslmode, porque o TLS é dele.
 *
 * Há retentativa limitada em dois pontos, ambos sem efeito no banco: obter as opções do conector e o `SELECT 1` da
 * primeira conexão, porque o Direct VPC pode levar 1 min ou mais na subida. Cada tentativa tem prazo, e as duas fases
 * somadas cabem na sonda de inicialização da web. A sonda usa clientes só dela, nunca o pool nem o cliente de trabalho,
 * e destrói o transporte de cada tentativa no fim ou no prazo. Nenhuma outra consulta nem transação é repetida nem ganha
 * prazo novo: um commit incerto nunca é reexecutado.
 */

/** O mínimo do Connector de @google-cloud/cloud-sql-connector usado aqui (o pacote é carregado em conector-google.ts). */
export interface Conector {
  getOptions(opcoes: {
    readonly instanceConnectionName: string;
    readonly ipType: 'PRIVATE';
  }): Promise<{ readonly stream: unknown }>;
  close(): void;
}

export type CriarConector = () => Promise<Conector>;

export type Ambiente = Readonly<Record<string, string | undefined>>;

export type CodigoErroConexao = 'CONFIGURACAO_INVALIDA' | 'CONECTOR_INDISPONIVEL' | 'BANCO_INDISPONIVEL';

// Mensagens fixas: nada da instância, do host nem do texto do conector ou do driver.
const MENSAGEM: Readonly<Record<CodigoErroConexao, string>> = {
  CONFIGURACAO_INVALIDA: 'Nome de conexão da instância do banco inválido; nenhuma conexão foi aberta.',
  CONECTOR_INDISPONIVEL: 'O conector do banco não ficou disponível depois das tentativas.',
  BANCO_INDISPONIVEL: 'O banco não respondeu depois das tentativas.',
};

export class ErroConexao extends Error {
  override readonly name = 'ErroConexao';
  constructor(readonly codigo: CodigoErroConexao) {
    super(MENSAGEM[codigo]);
  }
}

export interface Retentativa {
  /** Total de tentativas, a primeira inclusa. */
  readonly tentativas?: number;
  /** Espera entre tentativas, em milissegundos; injetável para teste. */
  readonly esperar?: (ms: number) => Promise<void>;
}

interface Politica {
  readonly tentativas: number;
  readonly primeiraEspera: number;
  readonly teto: number;
  /** Prazo de cada tentativa, em milissegundos. */
  readonly prazo: number;
}

// Conector: 4 tentativas de até 10 s, com esperas de 1, 2 e 4 s; no pior caso, 47 s. As opções vêm da API do Cloud
// SQL, pela internet e não pela VPC: falha que dura mais que isso é de permissão ou de configuração, não da subida. O
// prazo corta também as repetições internas do pacote (gaxios), que não têm prazo próprio.
const POLITICA_CONECTOR: Politica = { tentativas: 4, primeiraEspera: 1_000, teto: 8_000, prazo: 10_000 };
// Banco: 6 tentativas de até 10 s (abrir a conexão e o SELECT 1), com esperas de 2, 4, 8, 16 e 30 s; no pior caso,
// 120 s. Somadas às do conector, 167 s, dentro da sonda de inicialização da web (18 × 10 s = 180 s, R-006).
const POLITICA_BANCO: Politica = { tentativas: 6, primeiraEspera: 2_000, teto: 30_000, prazo: 10_000 };
// Sem limite, um pacote perdido na VPC prende a abertura da conexão por minutos. No pg.Pool, o mesmo valor limita também
// a espera por uma conexão livre: na HML, a requisição que espera mais de 10 s por uma vaga do pool falha, em vez de
// esperar sem fim como em desenvolvimento e na CI (ADR 0006).
const LIMITE_CONEXAO_MS = 10_000;
// Encerrar a sonda com o Terminate do protocolo tem este limite; depois, o transporte é destruído de qualquer jeito.
const LIMITE_ENCERRAR_MS = 1_000;

const dormir = (ms: number) =>
  new Promise<void>((resolve) => {
    setTimeout(resolve, ms);
  });

/** Uma tentativa em curso e, se houver, o que ela segura e precisa ser liberado quando o prazo vence. */
interface Tentativa<T> {
  readonly resultado: Promise<T>;
  readonly descartar?: () => void;
}

/**
 * O resultado da tentativa, ou rejeição depois de `ms`. No prazo, `descartar` libera o que a tentativa segura (a sonda
 * destrói o transporte, e a consulta pendente termina com erro). Se ainda assim resolver depois, o valor vai para
 * `tardio` (o conector aberto tarde é fechado ali); se rejeitar depois, a rejeição fica tratada aqui, sem ficar solta.
 */
function comPrazo<T>(tentativa: Tentativa<T>, ms: number, tardio: (valor: T) => void): Promise<T> {
  const { resultado, descartar } = tentativa;
  let relogio: ReturnType<typeof setTimeout> | undefined;
  const prazo = new Promise<never>((_, rejeitar) => {
    relogio = setTimeout(() => {
      resultado.then(tardio, () => undefined);
      descartar?.();
      rejeitar(new Error('prazo da tentativa esgotado'));
    }, ms);
  });
  return Promise.race([resultado, prazo]).finally(() => {
    clearTimeout(relogio);
  });
}

async function comRetentativa<T>(
  iniciar: () => Tentativa<T>,
  politica: Politica,
  opcoes: Retentativa,
  falha: CodigoErroConexao,
  tardio: (valor: T) => void = () => undefined,
): Promise<T> {
  const total = opcoes.tentativas ?? politica.tentativas;
  if (!Number.isInteger(total) || total < 1) throw new RangeError('tentativas precisa ser inteiro ≥ 1');
  const esperar = opcoes.esperar ?? dormir;
  for (let tentativa = 1; ; tentativa++) {
    try {
      return await comPrazo(iniciar(), politica.prazo, tardio);
    } catch (erro) {
      // Erro já classificado (pacote do conector que não carrega) não é passageiro: sem nova tentativa.
      if (erro instanceof ErroConexao) throw erro;
      // O erro original fica para trás: traz host, instância ou texto do driver.
      if (tentativa >= total) throw new ErroConexao(falha);
      await esperar(Math.min(politica.primeiraEspera * 2 ** (tentativa - 1), politica.teto));
    }
  }
}

/** O mínimo do pg.Client que a sonda usa; injetável para teste. */
export interface ClienteDeSonda {
  on(evento: 'error', ouvinte: () => void): unknown;
  connect(): Promise<unknown>;
  query(texto: string): Promise<unknown>;
  end(): Promise<unknown>;
}

export type AbrirCliente = (config: pg.ClientConfig) => ClienteDeSonda;

export type OpcoesSonda = Retentativa & {
  /** Cria o cliente de cada tentativa; o padrão é pg.Client. */
  readonly abrir?: AbrirCliente;
};

const abrirPadrao: AbrirCliente = (config) => new pg.Client(config);

/** end() do cliente, sem esperar mais que LIMITE_ENCERRAR_MS e sem lançar. */
async function encerrar(cliente: ClienteDeSonda): Promise<void> {
  let relogio: ReturnType<typeof setTimeout> | undefined;
  const limite = new Promise<void>((resolve) => {
    relogio = setTimeout(resolve, LIMITE_ENCERRAR_MS);
  });
  await Promise.race([cliente.end().catch(() => undefined), limite]);
  clearTimeout(relogio);
}

/**
 * Uma tentativa da sonda: cliente novo, só desta tentativa, com o transporte do conector registrado ao ser criado. O pg
 * não reaproveita um cliente que falhou ao conectar, e um SELECT 1 sem resposta prenderia o cliente (e o pool.end() de
 * quem o emprestasse) para sempre; por isso, no fim ou no prazo, o transporte é destruído (revisão do Codex,
 * CONEXAO-01).
 */
function tentativaDeSonda(
  config: pg.ClientConfig,
  stream: () => Duplex,
  abrir: AbrirCliente,
): Tentativa<void> {
  const transportes: Duplex[] = [];
  const destruir = () => {
    for (const t of transportes) t.destroy();
  };
  const cliente = abrir({
    ...config,
    stream: () => {
      const t = stream();
      transportes.push(t);
      return t;
    },
  });
  cliente.on('error', () => undefined);
  const resultado = (async () => {
    try {
      await cliente.connect();
      await cliente.query('SELECT 1');
    } finally {
      await encerrar(cliente);
      destruir();
    }
  })();
  return { resultado, descartar: destruir };
}

/**
 * Espera o banco responder a `SELECT 1` por clientes próprios, pelo transporte `stream` do conector, com retentativa
 * limitada; esgotada, BANCO_INDISPONIVEL. Só essa consulta é repetida, e ela não muda nada. Ao terminar, por sucesso ou
 * falha, nenhum cliente nem transporte da sonda continua aberto.
 */
export async function aguardarBanco(
  config: pg.ClientConfig,
  stream: () => Duplex,
  opcoes: OpcoesSonda = {},
): Promise<void> {
  const abrir = opcoes.abrir ?? abrirPadrao;
  await comRetentativa(
    () => tentativaDeSonda(config, stream, abrir),
    POLITICA_BANCO,
    opcoes,
    'BANCO_INDISPONIVEL',
  );
}

export interface Conexao {
  /** Somar a todo cliente e pool do processo; vazio sem a instância. */
  readonly extra: Partial<pg.ClientConfig>;
  /**
   * Com a instância, aguardarBanco com clientes da sonda na `config` (sem o extra, que a sonda põe); sem ela, não
   * consulta nada. Chamar antes de criar o pool ou o cliente de trabalho.
   */
  aguardar(config: pg.ClientConfig, opcoes?: OpcoesSonda): Promise<void>;
  /** Encerra o conector; chamar depois de encerrar os clientes e pools. */
  fechar(): void;
}

export type OpcoesConexao = Retentativa & { readonly criarConector: CriarConector };

export type PrepararConexao = (env: Ambiente) => Promise<Conexao>;

// projeto:regiao:instancia, cada parte com minúsculas, dígitos e hífen, começando por letra e sem hífen no fim.
// Projeto com domínio (exemplo.com:projeto) fica de fora: não é o caso aqui.
const PARTE = '[a-z](?:[a-z0-9-]{0,98}[a-z0-9])?';
const NOME_DE_CONEXAO = new RegExp(`^${PARTE}:${PARTE}:${PARTE}$`);

const SEM_CONECTOR: Conexao = {
  extra: {},
  aguardar: () => Promise.resolve(),
  fechar: () => undefined,
};

interface Aberto {
  readonly conector: Conector;
  readonly stream: () => Duplex;
}

/**
 * Uma tentativa, com um conector novo. Na 1.12.0, o conector guarda a carga que falhou: reusado, a tentativa seguinte
 * devolveria o mesmo erro sem chamar a API, e o close() dele vira rejeição solta com o erro do Google (a URL da API traz
 * projeto e instância). Por isso, nada de close() quando getOptions falha: a carga que falhou não deixa temporizador.
 */
async function abrir(criar: CriarConector, instancia: string): Promise<Aberto> {
  let conector: Conector;
  try {
    conector = await criar();
  } catch {
    throw new ErroConexao('CONECTOR_INDISPONIVEL');
  }
  const { stream } = await conector.getOptions({ instanceConnectionName: instancia, ipType: 'PRIVATE' });
  // O pacote é carregado sem tipos: o formato é conferido aqui, não no primeiro connect.
  if (typeof stream !== 'function') {
    conector.close();
    throw new TypeError('opções do conector sem stream');
  }
  return { conector, stream: stream as () => Duplex };
}

/**
 * Opções de conexão do processo. Sem SAFRION_CLOUDSQL_INSTANCIA, extra vazio e nada a fechar. Com ela, confere o
 * formato antes de qualquer rede e obtém as opções em IP privado, com retentativa limitada; esgotada,
 * CONECTOR_INDISPONIVEL. Pacote que não carrega também dá CONECTOR_INDISPONIVEL, sem nova tentativa. O conector vem de
 * fora (conector-google.ts nos comandos e na web).
 */
export async function prepararConexao(env: Ambiente, opcoes: OpcoesConexao): Promise<Conexao> {
  const instancia = env['SAFRION_CLOUDSQL_INSTANCIA'];
  if (instancia === undefined) return SEM_CONECTOR;
  if (!NOME_DE_CONEXAO.test(instancia)) throw new ErroConexao('CONFIGURACAO_INVALIDA');
  const { conector, stream } = await comRetentativa(
    () => ({ resultado: abrir(opcoes.criarConector, instancia) }),
    POLITICA_CONECTOR,
    opcoes,
    'CONECTOR_INDISPONIVEL',
    // Aberto depois do prazo: fechado na hora, porque o conector aberto renova o certificado por temporizador.
    (tarde) => {
      tarde.conector.close();
    },
  );
  return {
    extra: { stream, connectionTimeoutMillis: LIMITE_CONEXAO_MS },
    aguardar: (config, sonda) =>
      aguardarBanco({ ...config, connectionTimeoutMillis: LIMITE_CONEXAO_MS }, stream, sonda),
    fechar: () => {
      conector.close();
    },
  };
}

/** O mínimo do process que sairNaRejeicaoSolta usa; injetável para teste. */
export interface ProcessoDoComando {
  on(evento: 'unhandledRejection', ouvinte: (motivo: unknown) => void): unknown;
  exit(codigo: number): void;
}

/**
 * Nos comandos de linha. Uma rejeição solta (a do conector 1.12.0 fechado com uma renovação pendente, por exemplo)
 * derrubaria o processo com saída 1, que no contrato deles é "recusado, nada foi feito", e poria no stderr o erro do
 * Google, com a URL da API. Aqui o processo sai no mesmo momento, com 3 (falha de infraestrutura) e uma linha só com
 * códigos; o motivo nunca é escrito.
 */
export function sairNaRejeicaoSolta(
  escrever: (linha: string) => void,
  processo: ProcessoDoComando = process,
): void {
  let saindo = false;
  processo.on('unhandledRejection', (motivo) => {
    if (saindo) return;
    saindo = true;
    escrever(
      JSON.stringify({
        resultado: 'falha',
        codigo: 'FALHA_INFRAESTRUTURA',
        erro_tipo:
          motivo instanceof Error && /^[A-Za-z]{1,64}$/.test(motivo.name) ? motivo.name : typeof motivo,
        codigo_tecnico: 'REJEICAO_SOLTA',
      }),
    );
    processo.exit(3);
  });
}
