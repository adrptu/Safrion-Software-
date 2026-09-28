// Subida da web com o Cloud SQL por IP privado (R-006, GCP-0017), sem rede nem banco: a conexão preparada é falsa e o
// pool nunca conecta, fora um teste com o driver pg real sobre um transporte PostgreSQL em memória (CONEXAO-01). Sem a
// instância, dependencias() segue como antes da conexão privada.
import { Duplex } from 'node:stream';

import { ErroConexao, prepararConexao, type Conector, type Conexao } from '@safrion/db/web';
import pg from 'pg';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { register } from '../src/instrumentation';
import { dependencias, prepararDependencias, type Dependencias } from '../src/servidor/ambiente';

const CHAVE = Symbol.for('safrion.web.dependencias');
const guardadas = globalThis as Record<symbol, Dependencias | undefined>;
const INSTANCIA = 'projeto-teste:southamerica-east1:safrion-hml';
const IP = '10.20.0.3';
const SENHA = 'SenhaQueNaoPodeVazar123';
const URL_BANCO = `postgresql://app_runtime:${SENHA}@${IP}:5432/safrion_hml`;

let linhas: string[] = [];

beforeEach(() => {
  linhas = [];
  vi.spyOn(process.stdout, 'write').mockImplementation((texto: string | Uint8Array) => {
    linhas.push(String(texto));
    return true;
  });
  vi.stubEnv('DATABASE_URL', URL_BANCO);
  vi.stubEnv('SAFRION_ORIGEM', 'http://localhost:3000');
  vi.stubEnv('SAFRION_CLOUDSQL_INSTANCIA', undefined);
});

afterEach(async () => {
  await guardadas[CHAVE]?.banco.end();
  guardadas[CHAVE] = undefined;
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

/** Conexão preparada falsa: guarda a configuração da sonda e registra se já havia pool ao aguardar e ao fechar. */
function conexaoFalsa(aguardar: () => Promise<void> = () => Promise.resolve()) {
  const eventos: string[] = [];
  let config: pg.ClientConfig | undefined;
  const stream = () => undefined;
  const conexao: Conexao = {
    extra: { stream, connectionTimeoutMillis: 10_000 },
    aguardar: (c) => {
      config = c;
      eventos.push(`aguardar (pool: ${String(guardadas[CHAVE] !== undefined)})`);
      return aguardar();
    },
    fechar: () => {
      eventos.push(`fechar (pool: ${String(guardadas[CHAVE] !== undefined)})`);
    },
  };
  return { conexao, eventos, stream, config: () => config };
}

/** Mensagem do protocolo do PostgreSQL: tipo, tamanho (com ele mesmo) e corpo. */
function quadro(tipo: string, corpo: Buffer): Buffer {
  const b = Buffer.alloc(corpo.length + 5);
  b.write(tipo, 0);
  b.writeInt32BE(corpo.length + 4, 1);
  corpo.copy(b, 5);
  return b;
}

/**
 * Transporte PostgreSQL em memória que autentica e nunca responde a consulta (a perda de resposta da revisão do Codex,
 * CONEXAO-01); só termina quando alguém o destrói.
 */
class TransporteMudo extends Duplex {
  private inicio = true;
  consultas = 0;
  setNoDelay() {
    return this;
  }
  setKeepAlive() {
    return this;
  }
  connect() {
    queueMicrotask(() => this.emit('connect'));
    return this;
  }
  override _read() {
    // As respostas entram por push.
  }
  override _write(bytes: Buffer, _codificacao: BufferEncoding, pronto: (erro?: Error | null) => void) {
    if (this.inicio) {
      this.inicio = false;
      queueMicrotask(() =>
        this.push(Buffer.concat([quadro('R', Buffer.alloc(4)), quadro('Z', Buffer.from('I'))])),
      );
    } else if (bytes[0] === 0x51) {
      this.consultas++;
    } else if (bytes[0] === 0x58) {
      queueMicrotask(() => this.destroy());
    }
    pronto();
  }
}

function registros() {
  return linhas.map((l) => JSON.parse(l) as Record<string, unknown>);
}

function semSegredos(texto: string) {
  for (const segredo of [INSTANCIA, 'projeto-teste', IP, SENHA]) expect(texto).not.toContain(segredo);
}

async function erroDe(promessa: Promise<unknown>): Promise<Error> {
  try {
    await promessa;
  } catch (erro) {
    return erro as Error;
  }
  throw new Error('deveria ter falhado');
}

describe('sem SAFRION_CLOUDSQL_INSTANCIA (desenvolvimento e CI)', () => {
  it('prepararDependencias não faz nada; dependencias() cria o mesmo pool de antes, uma vez só', async () => {
    const preparar = vi.fn();
    await prepararDependencias(preparar);
    expect(preparar).not.toHaveBeenCalled();
    expect(guardadas[CHAVE]).toBeUndefined();
    const deps = dependencias();
    expect(deps.banco.options).toMatchObject({ connectionString: URL_BANCO, max: 3 });
    expect(deps.banco.options).not.toHaveProperty('stream');
    expect(deps.banco.options).not.toHaveProperty('connectionTimeoutMillis');
    expect(deps).toMatchObject({
      origem: 'http://localhost:3000',
      versao: '0.0.0-dev',
      commit: 'desconhecido',
    });
    expect(dependencias()).toBe(deps);
  });

  it('sem DATABASE_URL ou SAFRION_ORIGEM, recusa', () => {
    vi.stubEnv('SAFRION_ORIGEM', undefined);
    expect(() => dependencias()).toThrow('DATABASE_URL e SAFRION_ORIGEM são obrigatórios no servidor web.');
  });

  it('register: fora do runtime nodejs e sem instância, nada acontece', async () => {
    vi.stubEnv('NEXT_RUNTIME', 'edge');
    vi.stubEnv('SAFRION_CLOUDSQL_INSTANCIA', INSTANCIA);
    await register();
    expect(guardadas[CHAVE]).toBeUndefined();
    vi.stubEnv('NEXT_RUNTIME', 'nodejs');
    vi.stubEnv('SAFRION_CLOUDSQL_INSTANCIA', undefined);
    await register();
    expect(guardadas[CHAVE]).toBeUndefined();
    expect(linhas).toEqual([]);
  });
});

describe('com SAFRION_CLOUDSQL_INSTANCIA', () => {
  beforeEach(() => {
    vi.stubEnv('SAFRION_CLOUDSQL_INSTANCIA', INSTANCIA);
  });

  it('antes da subida, dependencias() recusa com texto fixo, sem a instância', () => {
    const erro = (() => {
      try {
        dependencias();
      } catch (e) {
        return e as Error;
      }
      throw new Error('deveria ter recusado');
    })();
    expect(erro.message).toBe(
      'Com SAFRION_CLOUDSQL_INSTANCIA, a conexão com o banco é preparada na subida (instrumentation.ts) e não está pronta.',
    );
    semSegredos(erro.message);
  });

  it('sucesso: a sonda vem antes do pool; o pool recebe o stream e o limite e fica guardado; fechar não é chamado', async () => {
    vi.stubEnv('SAFRION_VERSAO', '1.2.3');
    vi.stubEnv('SAFRION_COMMIT', 'abc1234');
    const f = conexaoFalsa();
    const preparar = vi.fn(() => Promise.resolve(f.conexao));
    await prepararDependencias(preparar);
    expect(preparar).toHaveBeenCalledTimes(1);
    expect(f.config()).toEqual({ connectionString: URL_BANCO });
    const deps = dependencias();
    expect(deps.banco.options).toMatchObject({
      connectionString: URL_BANCO,
      max: 3,
      stream: f.stream,
      connectionTimeoutMillis: 10_000,
    });
    expect(deps).toMatchObject({ versao: '1.2.3', commit: 'abc1234' });
    expect(f.eventos).toEqual(['aguardar (pool: false)']);
    // Já pronta: uma segunda subida não prepara de novo.
    await prepararDependencias(preparar);
    expect(preparar).toHaveBeenCalledTimes(1);
    expect(linhas).toEqual([]);
  });

  it('banco indisponível: nenhum pool criado, conector fechado, registro só com o código, erro de texto fixo', async () => {
    const f = conexaoFalsa(() => Promise.reject(new ErroConexao('BANCO_INDISPONIVEL')));
    const erro = await erroDe(prepararDependencias(() => Promise.resolve(f.conexao)));
    expect(erro).toBeInstanceOf(ErroConexao);
    expect(erro).toMatchObject({
      codigo: 'BANCO_INDISPONIVEL',
      message: 'O banco não respondeu depois das tentativas.',
    });
    expect(f.eventos).toEqual(['aguardar (pool: false)', 'fechar (pool: false)']);
    expect(guardadas[CHAVE]).toBeUndefined();
    expect(() => dependencias()).toThrow('não está pronta');
    expect(registros()).toEqual([
      expect.objectContaining({ nivel: 'erro', evento: 'banco.subida', codigo: 'BANCO_INDISPONIVEL' }),
    ]);
    semSegredos(linhas.join('\n'));
  });

  it('erro com texto do driver: relançado com mensagem fixa, registro sem código', async () => {
    const f = conexaoFalsa(() =>
      Promise.reject(new Error(`connect ECONNREFUSED ${IP}:5432 senha ${SENHA} em ${INSTANCIA}`)),
    );
    const erro = await erroDe(prepararDependencias(() => Promise.resolve(f.conexao)));
    expect(erro).not.toBeInstanceOf(ErroConexao);
    expect(erro.message).toBe('Falha ao preparar a conexão com o banco.');
    expect(erro.cause).toBeUndefined();
    expect(f.eventos).toEqual(['aguardar (pool: false)', 'fechar (pool: false)']);
    const [registro] = registros();
    expect(registro).toMatchObject({ evento: 'banco.subida' });
    expect(registro).not.toHaveProperty('codigo');
    semSegredos(`${erro.message} ${erro.stack ?? ''} ${linhas.join('\n')}`);
  });

  it('driver real, banco que autentica e não responde: BANCO_INDISPONIVEL aos 120 s, sem cliente nem transporte vivo', async () => {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout'] });
    try {
      const transportes: TransporteMudo[] = [];
      let fechados = 0;
      const conector: Conector = {
        getOptions: () =>
          Promise.resolve({
            stream: () => {
              const t = new TransporteMudo();
              transportes.push(t);
              return t;
            },
          }),
        close: () => {
          fechados++;
        },
      };
      const preparar = (env: Record<string, string | undefined>) =>
        prepararConexao(env, { criarConector: () => Promise.resolve(conector) });
      let erro: unknown;
      let terminou = false;
      const subida = prepararDependencias(preparar).then(
        () => {
          terminou = true;
        },
        (e: unknown) => {
          erro = e;
          terminou = true;
        },
      );
      await vi.advanceTimersByTimeAsync(119_999);
      expect(terminou).toBe(false);
      await vi.advanceTimersByTimeAsync(1);
      await subida;
      expect(erro).toMatchObject({ codigo: 'BANCO_INDISPONIVEL' });
      expect(transportes).toHaveLength(6);
      expect(transportes.map((t) => t.consultas)).toEqual([1, 1, 1, 1, 1, 1]);
      expect(transportes.every((t) => t.destroyed)).toBe(true);
      expect(fechados).toBe(1);
      expect(guardadas[CHAVE]).toBeUndefined();
      expect(registros()).toEqual([
        expect.objectContaining({ evento: 'banco.subida', codigo: 'BANCO_INDISPONIVEL' }),
      ]);
      semSegredos(linhas.join('\n'));
      expect(vi.getTimerCount()).toBe(0);
    } finally {
      vi.useRealTimers();
    }
  });

  it('preparação que falha: nada a encerrar nem a fechar, só o código no registro', async () => {
    const erro = await erroDe(
      prepararDependencias(() => Promise.reject(new ErroConexao('CONECTOR_INDISPONIVEL'))),
    );
    expect(erro).toMatchObject({ codigo: 'CONECTOR_INDISPONIVEL' });
    expect(registros()).toEqual([expect.objectContaining({ codigo: 'CONECTOR_INDISPONIVEL' })]);
    expect(guardadas[CHAVE]).toBeUndefined();
  });

  it('caminho padrão com nome inválido: CONFIGURACAO_INVALIDA antes de qualquer rede', async () => {
    vi.stubEnv('SAFRION_CLOUDSQL_INSTANCIA', 'projeto-teste/safrion-hml');
    const erro = await erroDe(prepararDependencias());
    expect(erro).toMatchObject({ codigo: 'CONFIGURACAO_INVALIDA' });
    expect(registros()).toEqual([expect.objectContaining({ codigo: 'CONFIGURACAO_INVALIDA' })]);
  });

  it('register no runtime nodejs chama a subida: a falha derruba a subida', async () => {
    vi.stubEnv('NEXT_RUNTIME', 'nodejs');
    vi.stubEnv('SAFRION_CLOUDSQL_INSTANCIA', 'invalida');
    await expect(register()).rejects.toMatchObject({ codigo: 'CONFIGURACAO_INVALIDA' });
  });

  it('erro de conexão ociosa: registra só o SQLSTATE, nunca a mensagem do driver', async () => {
    await prepararDependencias(() => Promise.resolve(conexaoFalsa().conexao));
    const { banco } = dependencias();
    banco.emit('error', Object.assign(new Error(`terminating connection em ${IP}`), { code: '57P01' }));
    banco.emit('error', Object.assign(new Error(`senha ${SENHA}`), { code: 'ECONNRESET' }));
    const [primeiro, segundo] = registros();
    expect(primeiro).toMatchObject({ evento: 'banco.conexao_ociosa', codigo: '57P01' });
    expect(segundo).toMatchObject({ evento: 'banco.conexao_ociosa' });
    expect(segundo).not.toHaveProperty('codigo');
    semSegredos(linhas.join('\n'));
  });
});
