import { describe, expect, it } from 'vitest';

import { caminhoInterno, INICIO } from '../src/identidade/caminho';
import { apagarCookie, COOKIE_SESSAO, definirCookie, lerCookie } from '../src/seguranca/cookies';
import {
  correlacaoDe,
  ErroRequisicao,
  exigirJson,
  exigirOrigem,
  lerCorpoLimitado,
} from '../src/seguranca/requisicao';

const URL_APP = 'http://localhost:3000/api';

function emPartes(...partes: string[]): ReadableStream<Uint8Array> {
  const codificador = new TextEncoder();
  return new ReadableStream({
    start(controle) {
      for (const p of partes) controle.enqueue(codificador.encode(p));
      controle.close();
    },
  });
}

const post = (corpo: BodyInit | null, cabecalhos: Record<string, string> = {}) =>
  new Request(URL_APP, { method: 'POST', body: corpo, headers: cabecalhos, duplex: 'half' } as RequestInit);

const codigoDe = async (p: Promise<unknown> | (() => unknown)) => {
  try {
    await (typeof p === 'function' ? p() : p);
    return 'SEM_ERRO';
  } catch (e) {
    return e instanceof ErroRequisicao ? e.codigo : 'OUTRO';
  }
};

describe('caminho interno depois do login', () => {
  it('aceita só caminho interno', () => {
    for (const ok of ['/', '/estoque', '/estoque?lote=1&aba=saldo', '/a/b#c'])
      expect(caminhoInterno(ok)).toBe(ok);
    expect(INICIO).toBe('/');
  });

  it('recusa URL externa, protocolo relativo, barra invertida, espaço, controle, vazio, longo e não texto', () => {
    for (const ruim of [
      'https://malicioso.invalid',
      '//malicioso.invalid',
      '/\\malicioso.invalid',
      'estoque',
      '/a b',
      '/a\tb',
      '/a\u0000b',
      '',
      `/${'a'.repeat(512)}`,
      undefined,
      null,
      42,
    ]) {
      expect(caminhoInterno(ruim), String(ruim)).toBeNull();
    }
  });
});

describe('corpo com limite de bytes', () => {
  it('lê o corpo em partes dentro do limite', async () => {
    expect(await lerCorpoLimitado(post(emPartes('{"a":', '1}')), 100)).toBe('{"a":1}');
    expect(await lerCorpoLimitado(post(null), 100)).toBe('');
  });

  it('recusa com 413 pelo Content-Length declarado ou contando bytes, sem Content-Length', async () => {
    expect(await codigoDe(lerCorpoLimitado(post('x'.repeat(20), { 'content-length': '20' }), 10))).toBe(
      'CORPO_EXCEDE_LIMITE',
    );
    expect(await codigoDe(lerCorpoLimitado(post(emPartes('x'.repeat(6), 'x'.repeat(6))), 10))).toBe(
      'CORPO_EXCEDE_LIMITE',
    );
  });

  it('UTF-8 inválido é recusa de contrato', async () => {
    const ruim = new ReadableStream<Uint8Array>({
      start(c) {
        c.enqueue(new Uint8Array([0xff, 0xfe]));
        c.close();
      },
    });
    expect(await codigoDe(lerCorpoLimitado(post(ruim), 10))).toBe('CONTRATO_INVALIDO');
  });
});

describe('tipo de conteúdo, origem e correlação', () => {
  it('só JSON na API', async () => {
    expect(
      await codigoDe(() => {
        exigirJson(post('{}', { 'content-type': 'application/json; charset=utf-8' }));
      }),
    ).toBe('SEM_ERRO');
    expect(
      await codigoDe(() => {
        exigirJson(post('{}', { 'content-type': 'text/plain' }));
      }),
    ).toBe('TIPO_DE_CONTEUDO_INVALIDO');
    expect(
      await codigoDe(() => {
        exigirJson(post('{}'));
      }),
    ).toBe('TIPO_DE_CONTEUDO_INVALIDO');
  });

  it('Origin igual à origem configurada; diferente ou ausente é recusado', async () => {
    const origem = 'http://localhost:3000';
    expect(
      await codigoDe(() => {
        exigirOrigem(post('{}', { origin: origem }), origem);
      }),
    ).toBe('SEM_ERRO');
    expect(
      await codigoDe(() => {
        exigirOrigem(post('{}', { origin: 'http://malicioso.invalid' }), origem);
      }),
    ).toBe('SEM_PERMISSAO');
    expect(
      await codigoDe(() => {
        exigirOrigem(post('{}'), origem);
      }),
    ).toBe('SEM_PERMISSAO');
  });

  it('correlação do cabeçalho só com formato de identificador', () => {
    expect(correlacaoDe(post(null, { 'x-correlation-id': 'corr-123' }))).toBe('corr-123');
    const gerada = correlacaoDe(post(null, { 'x-correlation-id': 'com espaço' }));
    expect(gerada).toMatch(/^[0-9a-f-]{36}$/);
    expect(correlacaoDe(post(null))).toMatch(/^[0-9a-f-]{36}$/);
  });
});

describe('cookies', () => {
  const com = (cookie?: string) => new Request(URL_APP, cookie === undefined ? {} : { headers: { cookie } });

  it('lê o cookie único; ausente, vazio ou repetido é undefined', () => {
    expect(lerCookie(com(), COOKIE_SESSAO)).toBeUndefined();
    expect(lerCookie(com(`outro=1; ${COOKIE_SESSAO}=abc`), COOKIE_SESSAO)).toBe('abc');
    expect(lerCookie(com(`${COOKIE_SESSAO}=`), COOKIE_SESSAO)).toBeUndefined();
    expect(lerCookie(com(`${COOKIE_SESSAO}=a; ${COOKIE_SESSAO}=b`), COOKIE_SESSAO)).toBeUndefined();
  });

  it('define com __Host-, HttpOnly, Secure e SameSite=Lax; recusa valor fora do formato', () => {
    const expira = new Date('2026-09-28T12:00:00Z');
    expect(definirCookie(COOKIE_SESSAO, 'abc_DEF-1', expira)).toBe(
      `${COOKIE_SESSAO}=abc_DEF-1; Path=/; Expires=${expira.toUTCString()}; HttpOnly; Secure; SameSite=Lax`,
    );
    expect(() => definirCookie(COOKIE_SESSAO, 'a;b', expira)).toThrow();
    expect(() => definirCookie('nome ruim', 'abc', expira)).toThrow();
    expect(apagarCookie(COOKIE_SESSAO)).toBe(
      `${COOKIE_SESSAO}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`,
    );
  });
});
