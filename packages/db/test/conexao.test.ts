// Conexão por IP privado (R-006, GCP-0017), sem rede externa nem banco: o conector e os clientes são falsos, fora um
// teste do conector real contra uma API falsa em 127.0.0.1. Sem a instância é o caminho de desenvolvimento e da CI; nos
// comandos, confere o repasse das opções, a ordem de fechamento e a saída só com códigos.
import { randomUUID } from 'node:crypto';
import { EventEmitter } from 'node:events';
import { createServer } from 'node:http';
import type { AddressInfo } from 'node:net';
import { createRequire } from 'node:module';
import { PassThrough } from 'node:stream';

import pg from 'pg';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { executarCli as demoReset } from '../src/cli/demo-reset.js';
import { executarCli as prepararBanco } from '../src/cli/preparar-banco.js';
import { executarCli as vincularIdentidade } from '../src/cli/vincular-identidade.js';
import {
  aguardarBanco,
  ErroConexao,
  prepararConexao,
  sairNaRejeicaoSolta,
  sondaPorCliente,
  type Conector,
  type Conexao,
} from '../src/conexao.js';

const INSTANCIA = 'projeto-teste:southamerica-east1:safrion-hml';
const IP = '10.20.0.3';
const COM_INSTANCIA = { SAFRION_CLOUDSQL_INSTANCIA: INSTANCIA };
const SENHA = 'SenhaQueNaoPodeVazar123';

/**
 * Conectores falsos, um novo a cada criação, como no código. getOptions falha nas primeiras `falhas` chamadas (contadas
 * entre todos os conectores), com a instância e o IP na mensagem; `fechados` guarda, em ordem, quais foram fechados.
 */
function conectorFalso(
  falhas = 0,
  opcoes: { readonly stream: unknown } = { stream: () => new PassThrough() },
) {
  const pedidos: unknown[] = [];
  const fechados: number[] = [];
  let criados = 0;
  const criarConector = vi.fn(() => {
    const id = ++criados;
    const conector: Conector = {
      getOptions(o) {
        pedidos.push(o);
        return pedidos.length <= falhas
          ? Promise.reject(new Error(`sem rota para ${INSTANCIA} em ${IP}`))
          : Promise.resolve(opcoes);
      },
      close() {
        fechados.push(id);
      },
    };
    return Promise.resolve(conector);
  });
  return { pedidos, fechados, criarConector };
}

function esperas() {
  const feitas: number[] = [];
  return {
    feitas,
    esperar: (ms: number) => {
      feitas.push(ms);
      return Promise.resolve();
    },
  };
}

/** Consulta falsa que falha nas primeiras `falhas` vezes com texto de driver (host e senha). */
function bancoFalso(falhas: number) {
  const consultas: string[] = [];
  return {
    consultas,
    query: (texto: string) => {
      consultas.push(texto);
      return consultas.length <= falhas
        ? Promise.reject(new Error(`connect ETIMEDOUT ${IP}:5432 senha ${SENHA}`))
        : Promise.resolve({ rows: [{ '?column?': 1 }] });
    },
  };
}

async function erroDe(promessa: Promise<unknown>): Promise<unknown> {
  try {
    await promessa;
  } catch (erro) {
    return erro;
  }
  throw new Error('deveria ter falhado');
}

/** Estado de uma promessa sem esperar por ela: serve com o relógio falso. */
function acompanhar(promessa: Promise<unknown>) {
  const estado: { resultado?: unknown; erro?: unknown; pronto: boolean } = { pronto: false };
  promessa.then(
    (r: unknown) => {
      Object.assign(estado, { resultado: r, pronto: true });
    },
    (e: unknown) => {
      Object.assign(estado, { erro: e, pronto: true });
    },
  );
  return estado;
}

function semSegredos(texto: string) {
  for (const segredo of [INSTANCIA, 'projeto-teste', 'safrion-hml', IP, SENHA])
    expect(texto).not.toContain(segredo);
}

afterEach(() => {
  vi.useRealTimers();
});

describe('prepararConexao', () => {
  it('sem SAFRION_CLOUDSQL_INSTANCIA: extra vazio, conector nem criado, aguardar e fechar sem efeito', async () => {
    const { criarConector } = conectorFalso();
    const conexao = await prepararConexao({ DATABASE_URL: 'postgresql://x@localhost/db' }, { criarConector });
    expect(conexao.extra).toEqual({});
    const banco = bancoFalso(0);
    await conexao.aguardar(banco);
    expect(banco.consultas).toEqual([]);
    conexao.fechar();
    expect(criarConector).not.toHaveBeenCalled();
  });

  it('nome fora de projeto:regiao:instancia: CONFIGURACAO_INVALIDA antes de criar o conector', async () => {
    const { criarConector } = conectorFalso();
    const invalidos = [
      '',
      'safrion-hml',
      'projeto-teste:southamerica-east1',
      'a:b:c:d',
      'exemplo.com:projeto:southamerica-east1:safrion-hml',
      'Projeto:southamerica-east1:safrion-hml',
      '1projeto:southamerica-east1:safrion-hml',
      'projeto-teste:southamerica-east1:safrion-hml-',
      'projeto-teste:southamerica-east1:safrion_hml',
      'projeto-teste::safrion-hml',
      ' projeto-teste:southamerica-east1:safrion-hml',
      'projeto-teste:southamerica-east1:safrion-hml\n',
      `projeto-teste:southamerica-east1:a${'b'.repeat(100)}`,
    ];
    for (const instancia of invalidos) {
      const erro = await erroDe(
        prepararConexao({ SAFRION_CLOUDSQL_INSTANCIA: instancia }, { criarConector }),
      );
      expect(erro, JSON.stringify(instancia)).toBeInstanceOf(ErroConexao);
      expect(erro).toMatchObject({ name: 'ErroConexao', codigo: 'CONFIGURACAO_INVALIDA' });
    }
    expect(criarConector).not.toHaveBeenCalled();
    for (const valido of ['a:b:c', INSTANCIA, `p:r:a${'b'.repeat(99)}`]) {
      const f = conectorFalso();
      await prepararConexao({ SAFRION_CLOUDSQL_INSTANCIA: valido }, { criarConector: f.criarConector });
      expect(f.pedidos, valido).toEqual([{ instanceConnectionName: valido, ipType: 'PRIVATE' }]);
    }
  });

  it('IP privado: repassa o nome e ipType PRIVATE; extra com o stream do conector; fechar fecha o conector', async () => {
    const stream = () => new PassThrough();
    const f = conectorFalso(0, { stream });
    const { esperar, feitas } = esperas();
    const conexao = await prepararConexao(COM_INSTANCIA, { criarConector: f.criarConector, esperar });
    expect(f.criarConector).toHaveBeenCalledTimes(1);
    expect(f.pedidos).toEqual([{ instanceConnectionName: INSTANCIA, ipType: 'PRIVATE' }]);
    expect(conexao.extra).toEqual({ stream, connectionTimeoutMillis: 10_000 });
    expect(conexao.extra.stream).toBe(stream);
    expect(feitas).toEqual([]);
    expect(f.fechados).toEqual([]);
    conexao.fechar();
    expect(f.fechados).toEqual([1]);
  });

  it('getOptions falha 2 vezes e passa na 3ª: um conector novo por tentativa; só o que abriu é fechado', async () => {
    const f = conectorFalso(2);
    const { esperar, feitas } = esperas();
    const conexao = await prepararConexao(COM_INSTANCIA, { criarConector: f.criarConector, esperar });
    expect(f.criarConector).toHaveBeenCalledTimes(3);
    expect(f.pedidos).toHaveLength(3);
    expect(feitas).toEqual([1_000, 2_000]);
    expect(conexao.extra).toHaveProperty('stream');
    // Os que falharam nunca recebem close(): no conector real, isso vira rejeição solta.
    expect(f.fechados).toEqual([]);
    conexao.fechar();
    expect(f.fechados).toEqual([3]);
  });

  it('getOptions sempre falha: 4 tentativas, esperas de 1, 2 e 4 s, nenhum close(), CONECTOR_INDISPONIVEL', async () => {
    const f = conectorFalso(Infinity);
    const { esperar, feitas } = esperas();
    const erro = await erroDe(prepararConexao(COM_INSTANCIA, { criarConector: f.criarConector, esperar }));
    expect(erro).toBeInstanceOf(ErroConexao);
    expect(erro).toMatchObject({ codigo: 'CONECTOR_INDISPONIVEL' });
    expect(f.criarConector).toHaveBeenCalledTimes(4);
    expect(f.pedidos).toHaveLength(4);
    expect(feitas).toEqual([1_000, 2_000, 4_000]);
    expect(f.fechados).toEqual([]);
    semSegredos(`${(erro as Error).message} ${(erro as Error).stack ?? ''} ${JSON.stringify(erro)}`);
    expect((erro as Error).cause).toBeUndefined();
  });

  it('tentativas injetáveis; tentativas que não são inteiro ≥ 1 são recusadas antes de criar conector', async () => {
    const f = conectorFalso(Infinity);
    const { esperar, feitas } = esperas();
    await expect(
      prepararConexao(COM_INSTANCIA, { criarConector: f.criarConector, esperar, tentativas: 2 }),
    ).rejects.toMatchObject({ codigo: 'CONECTOR_INDISPONIVEL' });
    expect(f.pedidos).toHaveLength(2);
    expect(feitas).toEqual([1_000]);
    for (const tentativas of [0, -1, 1.5, Number.NaN]) {
      const g = conectorFalso();
      await expect(
        prepararConexao(COM_INSTANCIA, { criarConector: g.criarConector, esperar, tentativas }),
      ).rejects.toBeInstanceOf(RangeError);
      expect(g.criarConector).not.toHaveBeenCalled();
    }
  });

  it('opções sem stream contam como falha; cada conector que abriu é fechado', async () => {
    const f = conectorFalso(0, { stream: undefined });
    const { esperar } = esperas();
    await expect(
      prepararConexao(COM_INSTANCIA, { criarConector: f.criarConector, esperar }),
    ).rejects.toMatchObject({ codigo: 'CONECTOR_INDISPONIVEL' });
    expect(f.pedidos).toHaveLength(4);
    expect(f.fechados).toEqual([1, 2, 3, 4]);
  });

  it('conector que não carrega (pacote ausente): CONECTOR_INDISPONIVEL sem nova tentativa', async () => {
    const criarConector = vi.fn(() => Promise.reject(new Error(`Cannot find package em ${INSTANCIA}`)));
    const { esperar, feitas } = esperas();
    const erro = await erroDe(prepararConexao(COM_INSTANCIA, { criarConector, esperar }));
    expect(erro).toMatchObject({ codigo: 'CONECTOR_INDISPONIVEL' });
    expect(criarConector).toHaveBeenCalledTimes(1);
    expect(feitas).toEqual([]);
    semSegredos((erro as Error).message);
  });

  it('getOptions que não responde: cada tentativa para em 10 s, CONECTOR_INDISPONIVEL aos 47 s; o que abrir tarde é fechado', async () => {
    vi.useFakeTimers();
    const pendentes: { abrir: (o: { stream: unknown }) => void; recusar: (e: Error) => void }[] = [];
    const fechados: number[] = [];
    const criarConector = vi.fn(() => {
      const id = pendentes.length + 1;
      return Promise.resolve<Conector>({
        getOptions: () =>
          new Promise((abrir, recusar) => {
            pendentes.push({ abrir, recusar });
          }),
        close: () => {
          fechados.push(id);
        },
      });
    });
    const estado = acompanhar(prepararConexao(COM_INSTANCIA, { criarConector }));
    await vi.advanceTimersByTimeAsync(46_999);
    expect(estado.pronto).toBe(false);
    expect(criarConector).toHaveBeenCalledTimes(4);
    await vi.advanceTimersByTimeAsync(1);
    expect(estado.erro).toMatchObject({ codigo: 'CONECTOR_INDISPONIVEL' });
    // A 2ª tentativa abre depois de desistida: o conector dela é fechado na hora. A 3ª falha depois: nada a fechar, e
    // a rejeição tardia não fica solta (o vitest acusaria).
    pendentes[1]?.abrir({ stream: () => new PassThrough() });
    pendentes[2]?.recusar(new Error(`sem rota para ${INSTANCIA}`));
    await vi.advanceTimersByTimeAsync(0);
    expect(fechados).toEqual([2]);
    expect(vi.getTimerCount()).toBe(0);
  });

  it('com a instância, aguardar espera o banco com SELECT 1', async () => {
    const f = conectorFalso();
    const conexao = await prepararConexao(COM_INSTANCIA, { criarConector: f.criarConector });
    const banco = bancoFalso(1);
    const { esperar, feitas } = esperas();
    await conexao.aguardar(banco, { esperar });
    expect(banco.consultas).toEqual(['SELECT 1', 'SELECT 1']);
    expect(feitas).toEqual([2_000]);
  });
});

describe('conector real 1.12.0 contra uma API falsa em 127.0.0.1 (sem rede externa)', () => {
  it('API recusa: 4 chamadas reais, CONECTOR_INDISPONIVEL sem texto do Google e nenhuma rejeição solta', async () => {
    // O pacote real: prova que cada tentativa chama a API (sem o erro guardado) e que nada fica solto depois.
    const { Connector } = await import('@google-cloud/cloud-sql-connector');
    const doConector = createRequire(
      createRequire(import.meta.url).resolve('@google-cloud/cloud-sql-connector'),
    );
    const { OAuth2Client } = doConector('google-auth-library') as {
      OAuth2Client: new () => { setCredentials(c: { access_token: string; expiry_date: number }): void };
    };
    const auth = new OAuth2Client();
    auth.setCredentials({ access_token: 'falso', expiry_date: Date.now() + 3_600_000 });
    const caminhos: string[] = [];
    const api = createServer((req, res) => {
      caminhos.push(req.url ?? '');
      res.writeHead(403, { 'content-type': 'application/json' });
      res.end('{"error":{"code":403,"message":"negado"}}');
    });
    await new Promise<void>((resolve) => api.listen(0, '127.0.0.1', resolve));
    const soltas: unknown[] = [];
    const aoSoltar = (motivo: unknown) => soltas.push(motivo);
    process.on('unhandledRejection', aoSoltar);
    try {
      const endereco = `http://127.0.0.1:${String((api.address() as AddressInfo).port)}`;
      const criarConector = () =>
        Promise.resolve(
          new Connector({ auth: auth as never, sqlAdminAPIEndpoint: endereco }) as unknown as Conector,
        );
      const { esperar } = esperas();
      const erro = await erroDe(prepararConexao(COM_INSTANCIA, { criarConector, esperar }));
      expect(erro).toMatchObject({ name: 'ErroConexao', codigo: 'CONECTOR_INDISPONIVEL' });
      semSegredos(`${(erro as Error).message} ${JSON.stringify(erro)}`);
      expect(caminhos).toHaveLength(4);
      for (const c of caminhos) expect(c).toContain('/projects/projeto-teste/instances/safrion-hml/');
      // Rejeição solta chega no próximo giro do laço de eventos: dá tempo a ela antes de conferir.
      await new Promise((resolve) => setTimeout(resolve, 200));
      expect(soltas).toEqual([]);
    } finally {
      process.off('unhandledRejection', aoSoltar);
      await new Promise((resolve) => api.close(resolve));
    }
  });
});

describe('sairNaRejeicaoSolta', () => {
  function processoFalso() {
    const emissor = new EventEmitter();
    const saidas: number[] = [];
    return {
      emissor,
      saidas,
      processo: {
        on: (evento: 'unhandledRejection', ouvinte: (motivo: unknown) => void) => emissor.on(evento, ouvinte),
        exit: (codigo: number) => {
          saidas.push(codigo);
        },
      },
    };
  }

  it('rejeição solta: uma linha só com códigos e saída 3; o motivo nunca é escrito; a segunda é ignorada', () => {
    const { emissor, saidas, processo } = processoFalso();
    const linhas: string[] = [];
    sairNaRejeicaoSolta((l) => linhas.push(l), processo);
    const google = Object.assign(
      new Error(
        `request to https://sqladmin.googleapis.com/sql/v1beta4/projects/projeto-teste/instances/safrion-hml failed ${IP}`,
      ),
      { name: 'GaxiosError' },
    );
    emissor.emit('unhandledRejection', google);
    emissor.emit('unhandledRejection', 'closed');
    expect(linhas.map((l) => JSON.parse(l) as unknown)).toEqual([
      {
        resultado: 'falha',
        codigo: 'FALHA_INFRAESTRUTURA',
        erro_tipo: 'GaxiosError',
        codigo_tecnico: 'REJEICAO_SOLTA',
      },
    ]);
    expect(saidas).toEqual([3]);
    semSegredos(linhas.join('\n'));
  });

  it('motivo que não é Error, ou nome fora do formato: só o tipo', () => {
    for (const [motivo, tipo] of [
      ['closed', 'string'],
      [Object.assign(new Error('x'), { name: `Erro ${INSTANCIA}` }), 'object'],
    ] as const) {
      const { emissor, saidas, processo } = processoFalso();
      const linhas: string[] = [];
      sairNaRejeicaoSolta((l) => linhas.push(l), processo);
      emissor.emit('unhandledRejection', motivo);
      expect(JSON.parse(linhas[0] ?? '')).toMatchObject({
        erro_tipo: tipo,
        codigo_tecnico: 'REJEICAO_SOLTA',
      });
      expect(saidas).toEqual([3]);
      semSegredos(linhas.join('\n'));
    }
  });
});

describe('aguardarBanco', () => {
  it('falha 2 vezes e passa: só SELECT 1, esperas de 2 e 4 s', async () => {
    const banco = bancoFalso(2);
    const { esperar, feitas } = esperas();
    await aguardarBanco(banco, { esperar });
    expect(banco.consultas).toEqual(['SELECT 1', 'SELECT 1', 'SELECT 1']);
    expect(feitas).toEqual([2_000, 4_000]);
  });

  it('sempre falha: 6 tentativas, esperas de 2, 4, 8, 16 e 30 s, BANCO_INDISPONIVEL sem texto do driver', async () => {
    const banco = bancoFalso(Infinity);
    const { esperar, feitas } = esperas();
    const erro = await erroDe(aguardarBanco(banco, { esperar }));
    expect(erro).toBeInstanceOf(ErroConexao);
    expect(erro).toMatchObject({ name: 'ErroConexao', codigo: 'BANCO_INDISPONIVEL' });
    expect(banco.consultas).toEqual(Array<string>(6).fill('SELECT 1'));
    expect(feitas).toEqual([2_000, 4_000, 8_000, 16_000, 30_000]);
    semSegredos(`${(erro as Error).message} ${JSON.stringify(erro)}`);
  });

  it('sem opções: banco que responde não espera; a espera padrão usa o relógio', async () => {
    const pronto = bancoFalso(0);
    await aguardarBanco(pronto);
    expect(pronto.consultas).toEqual(['SELECT 1']);
    vi.useFakeTimers();
    const banco = bancoFalso(1);
    const aguardando = aguardarBanco(banco, { tentativas: 2 });
    await vi.advanceTimersByTimeAsync(1_999);
    expect(banco.consultas).toHaveLength(1);
    await vi.advanceTimersByTimeAsync(1);
    await aguardando;
    expect(banco.consultas).toHaveLength(2);
  });

  it('SELECT 1 que não responde: cada tentativa para em 10 s, BANCO_INDISPONIVEL aos 120 s (com o conector, 167 s < 180 s)', async () => {
    vi.useFakeTimers();
    const consultas: string[] = [];
    const responder: (() => void)[] = [];
    const banco = {
      query: (texto: string) => {
        consultas.push(texto);
        return new Promise<void>((resolve) => {
          responder.push(resolve);
        });
      },
    };
    const estado = acompanhar(aguardarBanco(banco));
    await vi.advanceTimersByTimeAsync(119_999);
    expect(estado.pronto).toBe(false);
    expect(consultas).toHaveLength(6);
    await vi.advanceTimersByTimeAsync(1);
    expect(estado.erro).toMatchObject({ codigo: 'BANCO_INDISPONIVEL' });
    // Resposta depois do prazo não muda o resultado.
    responder[0]?.();
    await vi.advanceTimersByTimeAsync(0);
    expect(estado.erro).toMatchObject({ codigo: 'BANCO_INDISPONIVEL' });
    expect(vi.getTimerCount()).toBe(0);
  });

  it('sondaPorCliente: cada tentativa abre e fecha um cliente novo; o que falhou ao conectar não volta', async () => {
    const eventos: string[] = [];
    let abertos = 0;
    const abrir = () => {
      const id = ++abertos;
      return {
        on: (evento: 'error', ouvinte: () => void) => {
          eventos.push(`${String(id)}:on:${evento}`);
          ouvinte();
        },
        connect: () => {
          eventos.push(`${String(id)}:connect`);
          return id === 1 ? Promise.reject(new Error(`connect ECONNREFUSED ${IP}`)) : Promise.resolve();
        },
        query: (texto: string) => {
          eventos.push(`${String(id)}:${texto}`);
          return Promise.resolve({ rows: [] });
        },
        end: () => {
          eventos.push(`${String(id)}:end`);
          // Falha ao encerrar não esconde o resultado da consulta.
          return id === 2 ? Promise.reject(new Error('fim')) : Promise.resolve();
        },
      };
    };
    const { esperar, feitas } = esperas();
    await aguardarBanco(sondaPorCliente(abrir), { esperar });
    expect(eventos).toEqual([
      '1:on:error',
      '1:connect',
      '1:end',
      '2:on:error',
      '2:connect',
      '2:SELECT 1',
      '2:end',
    ]);
    expect(feitas).toEqual([2_000]);
  });
});

describe('comandos de linha com a conexão privada', () => {
  const URL_ADMIN = `postgresql://admin:${SENHA}@${IP}:5432/postgres`;
  const ENV_PREPARO = {
    ...COM_INSTANCIA,
    SAFRION_ADMIN_URL: URL_ADMIN,
    SAFRION_SENHA_MIGRATOR: 'senha-migrator-ficticia-16',
    SAFRION_SENHA_APP_RUNTIME: 'senha-app-runtime-ficticia-16',
  };
  const ARGS_PREPARO = ['--ambiente', 'hml', '--banco', 'safrion_hml'];
  const ARGS_VINCULO = [
    'revogar',
    '--ambiente',
    'hml',
    '--banco',
    'safrion_hml',
    '--organizacao',
    randomUUID(),
    '--usuario',
    randomUUID(),
    '--responsavel',
    'Adrianus (proprietário)',
    '--motivo',
    'teste da conexão privada',
  ];
  const falha = (codigoTecnico: string, erroTipo = 'ErroConexao') => ({
    resultado: 'falha',
    codigo: 'FALHA_INFRAESTRUTURA',
    erro_tipo: erroTipo,
    codigo_tecnico: codigoTecnico,
  });

  /** Conexão preparada falsa: registra a sonda e o fechamento, com uma marca no extra. */
  function conexaoFalsa(eventos: string[]): Conexao {
    return {
      extra: { application_name: 'marca-conexao-privada' },
      aguardar: async (alvo) => {
        eventos.push('aguardar');
        await alvo.query('SELECT 1');
      },
      fechar: () => {
        eventos.push('fechar');
      },
    };
  }

  /**
   * Clientes falsos: os `conectam` primeiros conectam e respondem (o banco-alvo já existe, com dono migrator); os
   * seguintes falham ao conectar com texto de driver.
   */
  function clientesFalsos(eventos: string[], conectam = 1) {
    const configs: pg.ClientConfig[] = [];
    const conectar = (config: pg.ClientConfig) => {
      configs.push(config);
      const id = String(configs.length);
      return {
        connectionParameters: { host: IP, port: 5432, user: 'admin', password: SENHA, ssl: false },
        on: () => undefined,
        connect: () => {
          eventos.push(`${id}:connect`);
          return Number(id) <= conectam
            ? Promise.resolve()
            : Promise.reject(
                Object.assign(new Error(`connect ECONNREFUSED ${IP}`), { code: 'ECONNREFUSED' }),
              );
        },
        query: (texto: string) => {
          eventos.push(`${id}:${texto}`);
          return Promise.resolve(
            texto.includes('pg_get_userbyid')
              ? { rowCount: 1, rows: [{ dono: 'migrator' }] }
              : { rowCount: 0, rows: [] },
          );
        },
        end: () => {
          eventos.push(`${id}:end`);
          return Promise.resolve();
        },
      } as unknown as pg.Client;
    };
    return { configs, conectar };
  }

  const recusaPreparo = () => Promise.reject(new ErroConexao('CONECTOR_INDISPONIVEL'));
  const nenhumCliente = (): pg.Client => {
    throw new Error('cliente que não deveria existir');
  };

  it('conector indisponível: saída 3 só com o código, sem abrir cliente, nos três comandos', async () => {
    const linhas: string[] = [];
    const escrever = (l: string) => linhas.push(l);
    expect(await prepararBanco(ARGS_PREPARO, ENV_PREPARO, escrever, nenhumCliente, recusaPreparo)).toBe(3);
    expect(
      await vincularIdentidade(
        ARGS_VINCULO,
        { ...COM_INSTANCIA, SAFRION_ADMIN_URL: URL_ADMIN },
        escrever,
        () => Promise.resolve(''),
        nenhumCliente,
        recusaPreparo,
      ),
    ).toBe(3);
    expect(
      await demoReset(
        ['--confirmar', 'hml'],
        { ...COM_INSTANCIA, DATABASE_URL: URL_ADMIN, SAFRION_AMBIENTE: 'hml' },
        escrever,
        recusaPreparo,
      ),
    ).toBe(3);
    expect(linhas.map((l) => JSON.parse(l) as unknown)).toEqual(
      Array.from({ length: 3 }, () => falha('CONECTOR_INDISPONIVEL')),
    );
    semSegredos(linhas.join('\n'));
  });

  it('nome da instância inválido pelo caminho padrão: saída 3 CONFIGURACAO_INVALIDA, sem rede nem cliente', async () => {
    const linhas: string[] = [];
    const escrever = (l: string) => linhas.push(l);
    const invalida = { SAFRION_CLOUDSQL_INSTANCIA: 'projeto-teste/safrion-hml' };
    expect(await prepararBanco(ARGS_PREPARO, { ...ENV_PREPARO, ...invalida }, escrever, nenhumCliente)).toBe(
      3,
    );
    expect(
      await vincularIdentidade(
        ARGS_VINCULO,
        { ...invalida, SAFRION_ADMIN_URL: URL_ADMIN },
        escrever,
        () => Promise.resolve(''),
        nenhumCliente,
      ),
    ).toBe(3);
    expect(
      await demoReset(
        ['--confirmar', 'hml'],
        { ...invalida, DATABASE_URL: URL_ADMIN, SAFRION_AMBIENTE: 'hml' },
        escrever,
      ),
    ).toBe(3);
    expect(linhas.map((l) => JSON.parse(l) as unknown)).toEqual(
      Array.from({ length: 3 }, () => falha('CONFIGURACAO_INVALIDA')),
    );
    semSegredos(linhas.join('\n'));
  });

  it('preparar-banco: a sonda, o administrador e o cliente do banco-alvo recebem o extra; fechar por último', async () => {
    const eventos: string[] = [];
    const linhas: string[] = [];
    const { configs, conectar } = clientesFalsos(eventos, 2);
    const conexao = conexaoFalsa(eventos);
    const saida = await prepararBanco(
      ARGS_PREPARO,
      ENV_PREPARO,
      (l) => linhas.push(l),
      conectar,
      () => Promise.resolve(conexao),
    );
    expect(saida).toBe(3);
    expect(linhas.map((l) => JSON.parse(l) as unknown)).toEqual([falha('ECONNREFUSED', 'Error')]);
    // O 3º cliente é o que o preparo abre no banco-alvo para ler a identidade: também passa pelo conector.
    expect(configs).toEqual([
      { connectionString: URL_ADMIN, ...conexao.extra },
      { connectionString: URL_ADMIN, ...conexao.extra },
      {
        host: IP,
        port: 5432,
        user: 'admin',
        password: SENHA,
        ssl: false,
        database: 'safrion_hml',
        ...conexao.extra,
      },
    ]);
    expect(eventos.filter((e) => !e.startsWith('2:SELECT'))).toEqual([
      'aguardar',
      '1:connect',
      '1:SELECT 1',
      '1:end',
      '2:connect',
      '3:connect',
      '2:end',
      'fechar',
    ]);
    semSegredos(linhas.join('\n'));
  });

  it('vincular-identidade: a sonda e o cliente do banco-alvo recebem o extra; fechar vem depois de encerrar', async () => {
    const eventos: string[] = [];
    const linhas: string[] = [];
    const { configs, conectar } = clientesFalsos(eventos);
    const conexao = conexaoFalsa(eventos);
    const saida = await vincularIdentidade(
      ARGS_VINCULO,
      { ...COM_INSTANCIA, SAFRION_ADMIN_URL: URL_ADMIN },
      (l) => linhas.push(l),
      () => Promise.resolve(''),
      conectar,
      () => Promise.resolve(conexao),
    );
    expect(saida).toBe(3);
    expect(linhas.map((l) => JSON.parse(l) as unknown)).toEqual([falha('ECONNREFUSED', 'Error')]);
    expect(configs).toHaveLength(2);
    for (const config of configs) {
      expect(config).toMatchObject({
        host: IP,
        port: 5432,
        database: 'safrion_hml',
        user: 'admin',
        ...conexao.extra,
      });
    }
    expect(eventos).toEqual(['aguardar', '1:connect', '1:SELECT 1', '1:end', '2:connect', '2:end', 'fechar']);
    semSegredos(linhas.join('\n'));
  });

  it('demo-reset: o pool recebe o extra; banco indisponível sai 3 com o código; fechar depois de encerrar o pool', async () => {
    const linhas: string[] = [];
    let recebido: unknown;
    let poolEncerradoAoFechar: boolean | undefined;
    const conexao: Conexao = {
      extra: { application_name: 'marca-conexao-privada' },
      aguardar: (alvo) => {
        recebido = alvo;
        return Promise.reject(new ErroConexao('BANCO_INDISPONIVEL'));
      },
      fechar: () => {
        poolEncerradoAoFechar = (recebido as pg.Pool).ended;
      },
    };
    const saida = await demoReset(
      ['--confirmar', 'hml'],
      { ...COM_INSTANCIA, DATABASE_URL: URL_ADMIN, SAFRION_AMBIENTE: 'hml' },
      (l) => linhas.push(l),
      () => Promise.resolve(conexao),
    );
    expect(saida).toBe(3);
    expect(linhas.map((l) => JSON.parse(l) as unknown)).toEqual([falha('BANCO_INDISPONIVEL')]);
    expect(recebido).toBeInstanceOf(pg.Pool);
    expect((recebido as pg.Pool).options).toMatchObject({
      connectionString: URL_ADMIN,
      max: 1,
      application_name: 'marca-conexao-privada',
    });
    expect(poolEncerradoAoFechar).toBe(true);
    semSegredos(linhas.join('\n'));
  });
});
