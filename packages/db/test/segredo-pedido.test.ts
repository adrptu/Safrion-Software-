// Cliente REST do Secret Manager da fila de vínculo (R-006, GCP-0017, §3c), com fetch simulado: nomes de campos,
// paginação, etag no corpo, token do servidor de metadados e erros só com códigos. Nenhuma chamada sai da máquina.
import { describe, expect, it } from 'vitest';

import { criarSegredoPedido, ErroSegredo } from '../src/segredo-pedido.js';

const NOME = 'projects/projeto-ficticio/secrets/hml-vinculo-pedido';
const API = 'https://secretmanager.googleapis.com/v1/';
const METADADOS =
  'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token';

interface Chamada {
  readonly url: string;
  readonly metodo: string;
  readonly cabecalhos: Record<string, string>;
  readonly corpo: string | undefined;
}

const json = (corpo: unknown, status = 200) =>
  new Response(JSON.stringify(corpo), { status, headers: { 'Content-Type': 'application/json' } });

/** fetch simulado: o token responde sempre; o resto sai de `api`, na ordem. */
function simulado(
  api: (Response | Error)[],
  token: () => Response | Error = () => json({ access_token: 'token-ficticio', expires_in: 3599 }),
) {
  const chamadas: Chamada[] = [];
  const buscar = (url: string, init: RequestInit) => {
    const c: Chamada = {
      url,
      metodo: init.method ?? 'GET',
      cabecalhos: init.headers as Record<string, string>,
      corpo: typeof init.body === 'string' ? init.body : undefined,
    };
    chamadas.push(c);
    const r = url === METADADOS ? token() : api.shift();
    if (!r) throw new Error('chamada inesperada');
    return r instanceof Error ? Promise.reject(r) : Promise.resolve(r);
  };
  return { buscar, chamadas, doApi: () => chamadas.filter((c) => c.url !== METADADOS) };
}

const codigoDe = (p: Promise<unknown>) =>
  p.then(
    () => 'sem erro',
    (e: unknown) => (e instanceof ErroSegredo ? e.codigo : `outro: ${String(e)}`),
  );

describe('configuração', () => {
  it('nome fora de projects/<projeto>/secrets/<nome>: SEGREDO_INVALIDO, sem rede', () => {
    for (const nome of [
      '',
      'hml-vinculo-pedido',
      'projects/p/secrets/hml-vinculo-pedido/versions/1',
      'projects/P_MAIUSCULO/secrets/x',
      'projects/p/secrets/com espaço',
    ]) {
      let erro: unknown;
      try {
        criarSegredoPedido(nome, () => Promise.reject(new Error('não deveria chamar')));
      } catch (e) {
        erro = e;
      }
      expect(erro, nome).toBeInstanceOf(ErroSegredo);
      expect((erro as ErroSegredo).codigo).toBe('SEGREDO_INVALIDO');
      expect((erro as ErroSegredo).message).toContain('SAFRION_PEDIDO_SEGREDO');
    }
  });
});

describe('listagem', () => {
  it('lê todas as páginas com filter=state:ENABLED e pageToken, com o token do servidor de metadados', async () => {
    const { buscar, chamadas, doApi } = simulado([
      json({
        versions: [
          {
            name: 'projects/123456789/secrets/hml-vinculo-pedido/versions/3',
            createTime: '2026-09-28T21:52:00.123456789Z',
            state: 'ENABLED',
            etag: '"e3"',
          },
        ],
        nextPageToken: 'pagina-2',
      }),
      json({
        versions: [
          {
            name: 'projects/projeto-ficticio/secrets/hml-vinculo-pedido/versions/10',
            createTime: '2026-09-28T21:50:00Z',
          },
        ],
        nextPageToken: '',
      }),
    ]);
    const s = criarSegredoPedido(NOME, buscar);
    expect(await s.listarAtivas()).toEqual([
      { versao: '3', createTime: '2026-09-28T21:52:00.123456789Z' },
      { versao: '10', createTime: '2026-09-28T21:50:00Z' },
    ]);
    const [p1, p2] = doApi();
    expect(p1?.url).toBe(`${API}${NOME}/versions?filter=state%3AENABLED`);
    expect(p2?.url).toBe(`${API}${NOME}/versions?filter=state%3AENABLED&pageToken=pagina-2`);
    expect(p1?.metodo).toBe('GET');
    expect(p1?.cabecalhos).toEqual({ Authorization: 'Bearer token-ficticio' });
    const tokens = chamadas.filter((c) => c.url === METADADOS);
    expect(tokens).toHaveLength(2);
    expect(tokens[0]?.cabecalhos).toEqual({ 'Metadata-Flavor': 'Google' });
  });

  it('lista vazia vem sem "versions"', async () => {
    const { buscar } = simulado([json({})]);
    expect(await criarSegredoPedido(NOME, buscar).listarAtivas()).toEqual([]);
  });

  it('resposta fora do formato: RESPOSTA_INVALIDA', async () => {
    const casos: unknown[] = [
      { versions: 'x' },
      { nextPageToken: 5 },
      { versions: [null] },
      { versions: [{ name: 5, createTime: '2026-09-28T21:50:00Z' }] },
      // Outro segredo, versão com zero à esquerda e nome sem número.
      { versions: [{ name: 'projects/p/secrets/outro/versions/1', createTime: '2026-09-28T21:50:00Z' }] },
      { versions: [{ name: `${NOME}/versions/01`, createTime: '2026-09-28T21:50:00Z' }] },
      { versions: [{ name: `${NOME}/versions/latest`, createTime: '2026-09-28T21:50:00Z' }] },
      { versions: [{ name: `${NOME}/versions/1` }] },
      { versions: [{ name: `${NOME}/versions/1`, createTime: '2026-09-28 21:50:00Z' }] },
      { versions: [{ name: `${NOME}/versions/1`, createTime: '2026-09-28T21:50:00.1234567890Z' }] },
      { versions: [{ name: `${NOME}/versions/1`, createTime: '2026-09-28T21:50:00+00:00' }] },
      [],
    ];
    for (const corpo of casos) {
      const { buscar } = simulado([json(corpo)]);
      expect(await codigoDe(criarSegredoPedido(NOME, buscar).listarAtivas()), JSON.stringify(corpo)).toBe(
        'RESPOSTA_INVALIDA',
      );
    }
  });
});

describe('versão', () => {
  it('obter devolve estado e etag como vieram; acessar decodifica payload.data em base64', async () => {
    const pedido = '{"pedido_id":"x"}';
    const { buscar, doApi } = simulado([
      json({ name: `${NOME}/versions/2`, state: 'DISABLED', etag: '"etag-opaco"' }),
      json({ name: `${NOME}/versions/2`, payload: { data: Buffer.from(pedido).toString('base64') } }),
      // Dado vazio sai do JSON (proto3): pedido vazio, que a validação recusa.
      json({ name: `${NOME}/versions/3`, payload: {} }),
      json({ name: `${NOME}/versions/4` }),
    ]);
    const s = criarSegredoPedido(NOME, buscar);
    expect(await s.obter('2')).toEqual({ estado: 'DISABLED', etag: '"etag-opaco"' });
    expect((await s.acessar('2')).toString('utf8')).toBe(pedido);
    expect((await s.acessar('3')).length).toBe(0);
    expect((await s.acessar('4')).length).toBe(0);
    expect(doApi().map((c) => [c.metodo, c.url])).toEqual([
      ['GET', `${API}${NOME}/versions/2`],
      ['GET', `${API}${NOME}/versions/2:access`],
      ['GET', `${API}${NOME}/versions/3:access`],
      ['GET', `${API}${NOME}/versions/4:access`],
    ]);
  });

  it('desativar e destruir mandam o etag lido no corpo, por POST no nome exato', async () => {
    const { buscar, doApi } = simulado([json({ state: 'DISABLED' }), json({ state: 'DESTROYED' })]);
    const s = criarSegredoPedido(NOME, buscar);
    await s.desativar('7', '"e7"');
    await s.destruir('8', '"e8"');
    expect(doApi().map((c) => [c.metodo, c.url, c.corpo, c.cabecalhos['Content-Type']])).toEqual([
      ['POST', `${API}${NOME}/versions/7:disable`, '{"etag":"\\"e7\\""}', 'application/json'],
      ['POST', `${API}${NOME}/versions/8:destroy`, '{"etag":"\\"e8\\""}', 'application/json'],
    ]);
  });

  it('formato inesperado: RESPOSTA_INVALIDA', async () => {
    const casos: [Response, (s: ReturnType<typeof criarSegredoPedido>) => Promise<unknown>][] = [
      [json({ state: 'ENABLED' }), (s) => s.obter('1')],
      [json({ etag: 'e' }), (s) => s.obter('1')],
      [json({ payload: { data: 5 } }), (s) => s.acessar('1')],
      [new Response('não é json', { status: 200 }), (s) => s.obter('1')],
      [json('texto'), (s) => s.obter('1')],
    ];
    for (const [resposta, chamar] of casos) {
      const { buscar } = simulado([resposta]);
      expect(await codigoDe(chamar(criarSegredoPedido(NOME, buscar)))).toBe('RESPOSTA_INVALIDA');
    }
  });
});

describe('falhas viram códigos, sem URL, projeto, token nem corpo', () => {
  it('etag recusado e outros HTTP: SEGREDO_HTTP_<status>', async () => {
    const corpoComSegredo = { error: { message: `falhou em ${NOME} com token-ficticio` } };
    const { buscar } = simulado([json(corpoComSegredo, 409), json(corpoComSegredo, 403)]);
    const s = criarSegredoPedido(NOME, buscar);
    const erro = await s.destruir('1', 'velho').catch((e: unknown) => e);
    expect(erro).toBeInstanceOf(ErroSegredo);
    expect((erro as ErroSegredo).codigo).toBe('SEGREDO_HTTP_409');
    expect(await codigoDe(s.listarAtivas())).toBe('SEGREDO_HTTP_403');
    const texto = `${(erro as Error).message} ${JSON.stringify(erro)}`;
    for (const proibido of ['projeto-ficticio', 'secretmanager', 'token-ficticio', 'falhou']) {
      expect(texto).not.toContain(proibido);
    }
  });

  it('API fora do ar: SEGREDO_INDISPONIVEL', async () => {
    const { buscar } = simulado([new Error(`connect ECONNREFUSED ${API}`)]);
    expect(await codigoDe(criarSegredoPedido(NOME, buscar).obter('1'))).toBe('SEGREDO_INDISPONIVEL');
  });

  it('servidor de metadados: indisponível, HTTP e resposta sem token', async () => {
    const casos: [() => Response | Error, string][] = [
      [() => new Error('getaddrinfo ENOTFOUND metadata.google.internal'), 'METADADOS_INDISPONIVEL'],
      [() => json({}, 500), 'METADADOS_HTTP_500'],
      [() => json({ access_token: '' }), 'RESPOSTA_INVALIDA'],
      [() => json({ token_type: 'Bearer' }), 'RESPOSTA_INVALIDA'],
    ];
    for (const [token, codigo] of casos) {
      const { buscar, doApi } = simulado([], token);
      expect(await codigoDe(criarSegredoPedido(NOME, buscar).listarAtivas())).toBe(codigo);
      expect(doApi()).toEqual([]);
    }
  });
});
