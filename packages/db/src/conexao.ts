import type { Duplex } from 'node:stream';

import type pg from 'pg';

/**
 * Conexão com o Cloud SQL por IP privado (R-006, GCP-0017, opção A). Sem IP público, a web e os jobs chegam ao banco
 * pela VPC com o conector oficial em `ipType` PRIVATE, que faz o TLS mútuo exigido por `connector_enforcement =
 * REQUIRED`. Só entra com SAFRION_CLOUDSQL_INSTANCIA; sem ela (desenvolvimento, CI e testes), nada muda: a URL comum
 * segue sozinha e o conector nem é criado. Com o conector, a URL não leva sslmode, porque o TLS é dele.
 *
 * Há retentativa limitada em dois pontos, ambos sem efeito no banco: obter as opções do conector e o `SELECT 1` da
 * primeira conexão, porque o Direct VPC pode levar 1 min ou mais na subida. Cada tentativa tem prazo, e as duas fases
 * somadas cabem na sonda de inicialização da web. Nenhuma outra consulta nem transação é repetida: um commit incerto
 * nunca é reexecutado.
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

const dormir = (ms: number) =>
  new Promise<void>((resolve) => {
    setTimeout(resolve, ms);
  });

/**
 * A promessa, ou rejeição depois de `ms`. Ela não é cancelada: se resolver depois do prazo, o valor vai para `tardio`
 * (o conector aberto tarde é fechado ali); se rejeitar depois, a rejeição fica tratada aqui e não vira rejeição solta.
 */
function comPrazo<T>(promessa: Promise<T>, ms: number, tardio: (valor: T) => void): Promise<T> {
  let relogio: ReturnType<typeof setTimeout> | undefined;
  const prazo = new Promise<never>((_, rejeitar) => {
    relogio = setTimeout(() => {
      promessa.then(tardio, () => undefined);
      rejeitar(new Error('prazo da tentativa esgotado'));
    }, ms);
  });
  return Promise.race([promessa, prazo]).finally(() => {
    clearTimeout(relogio);
  });
}

async function comRetentativa<T>(
  acao: () => Promise<T>,
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
      return await comPrazo(acao(), politica.prazo, tardio);
    } catch (erro) {
      // Erro já classificado (pacote do conector que não carrega) não é passageiro: sem nova tentativa.
      if (erro instanceof ErroConexao) throw erro;
      // O erro original fica para trás: traz host, instância ou texto do driver.
      if (tentativa >= total) throw new ErroConexao(falha);
      await esperar(Math.min(politica.primeiraEspera * 2 ** (tentativa - 1), politica.teto));
    }
  }
}

/** O que responde a uma consulta: pg.Pool, pg.Client já conectado ou sondaPorCliente. */
export interface Consultavel {
  query(texto: string): Promise<unknown>;
}

/**
 * Espera o banco responder a `SELECT 1`, com retentativa limitada; esgotada, BANCO_INDISPONIVEL. Só essa consulta é
 * repetida, e ela não muda nada.
 */
export async function aguardarBanco(alvo: Consultavel, opcoes: Retentativa = {}): Promise<void> {
  await comRetentativa(() => alvo.query('SELECT 1'), POLITICA_BANCO, opcoes, 'BANCO_INDISPONIVEL');
}

interface ClienteDeSonda {
  on(evento: 'error', ouvinte: () => void): unknown;
  connect(): Promise<unknown>;
  query(texto: string): Promise<unknown>;
  end(): Promise<unknown>;
}

/**
 * Cada consulta abre um cliente novo e o fecha em seguida: o pg não reaproveita um cliente que falhou ao conectar.
 * Serve para os comandos, que trabalham com pg.Client, esperarem o banco antes da primeira conexão de verdade.
 */
export function sondaPorCliente(abrir: () => ClienteDeSonda): Consultavel {
  return {
    async query(texto) {
      const cliente = abrir();
      cliente.on('error', () => undefined);
      try {
        await cliente.connect();
        return await cliente.query(texto);
      } finally {
        await cliente.end().catch(() => undefined);
      }
    },
  };
}

export interface Conexao {
  /** Somar a todo cliente e pool do processo; vazio sem a instância. */
  readonly extra: Partial<pg.ClientConfig>;
  /** Com a instância, aguardarBanco; sem ela, não consulta nada. */
  aguardar(alvo: Consultavel, opcoes?: Retentativa): Promise<void>;
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
    () => abrir(opcoes.criarConector, instancia),
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
    aguardar: aguardarBanco,
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
