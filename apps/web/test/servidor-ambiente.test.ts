// Subida da web com o Cloud SQL por IP privado (R-006, GCP-0017), sem rede nem banco: a conexão preparada é falsa e o
// pool nunca conecta. Sem a instância, dependencias() segue como antes da conexão privada.
import { ErroConexao, type Conexao } from '@safrion/db/web';
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

/** Conexão preparada falsa: guarda o alvo da sonda e registra a ordem entre o fim do pool e o fechamento. */
function conexaoFalsa(aguardar: (alvo: pg.Pool) => Promise<void> = () => Promise.resolve()) {
  const eventos: string[] = [];
  let alvo: pg.Pool | undefined;
  const stream = () => undefined;
  const conexao: Conexao = {
    extra: { stream, connectionTimeoutMillis: 10_000 },
    aguardar: (a) => {
      alvo = a as pg.Pool;
      eventos.push('aguardar');
      return aguardar(alvo);
    },
    fechar: () => {
      eventos.push(`fechar (pool encerrado: ${String(alvo?.ended)})`);
    },
  };
  return { conexao, eventos, stream, alvo: () => alvo };
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

  it('sucesso: o pool recebe o stream e o limite, espera o banco e fica guardado; fechar não é chamado', async () => {
    vi.stubEnv('SAFRION_VERSAO', '1.2.3');
    vi.stubEnv('SAFRION_COMMIT', 'abc1234');
    const f = conexaoFalsa();
    const preparar = vi.fn(() => Promise.resolve(f.conexao));
    await prepararDependencias(preparar);
    expect(preparar).toHaveBeenCalledTimes(1);
    const deps = dependencias();
    expect(deps.banco).toBe(f.alvo());
    expect(deps.banco.options).toMatchObject({
      connectionString: URL_BANCO,
      max: 3,
      stream: f.stream,
      connectionTimeoutMillis: 10_000,
    });
    expect(deps).toMatchObject({ versao: '1.2.3', commit: 'abc1234' });
    expect(f.eventos).toEqual(['aguardar']);
    // Já pronta: uma segunda subida não prepara de novo.
    await prepararDependencias(preparar);
    expect(preparar).toHaveBeenCalledTimes(1);
    expect(linhas).toEqual([]);
  });

  it('banco indisponível: pool encerrado antes do conector, registro só com o código, erro de texto fixo', async () => {
    const f = conexaoFalsa(() => Promise.reject(new ErroConexao('BANCO_INDISPONIVEL')));
    const erro = await erroDe(prepararDependencias(() => Promise.resolve(f.conexao)));
    expect(erro).toBeInstanceOf(ErroConexao);
    expect(erro).toMatchObject({
      codigo: 'BANCO_INDISPONIVEL',
      message: 'O banco não respondeu depois das tentativas.',
    });
    expect(f.eventos).toEqual(['aguardar', 'fechar (pool encerrado: true)']);
    expect(guardadas[CHAVE]).toBeUndefined();
    expect(() => dependencias()).toThrow('não está pronta');
    expect(registros()).toEqual([
      expect.objectContaining({ nivel: 'erro', evento: 'banco.subida', codigo: 'BANCO_INDISPONIVEL' }),
    ]);
    semSegredos(linhas.join('\n'));
  });

  it('erro com texto do driver: relançado com mensagem fixa, registro sem código; pool que falha ao encerrar não esconde', async () => {
    const f = conexaoFalsa(async (pool) => {
      await pool.end();
      throw new Error(`connect ECONNREFUSED ${IP}:5432 senha ${SENHA} em ${INSTANCIA}`);
    });
    const erro = await erroDe(prepararDependencias(() => Promise.resolve(f.conexao)));
    expect(erro).not.toBeInstanceOf(ErroConexao);
    expect(erro.message).toBe('Falha ao preparar a conexão com o banco.');
    expect(erro.cause).toBeUndefined();
    expect(f.eventos).toEqual(['aguardar', 'fechar (pool encerrado: true)']);
    const [registro] = registros();
    expect(registro).toMatchObject({ evento: 'banco.subida' });
    expect(registro).not.toHaveProperty('codigo');
    semSegredos(`${erro.message} ${erro.stack ?? ''} ${linhas.join('\n')}`);
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
