import { describe, expect, it } from 'vitest';

import { MENSAGEM_GENERICA, mensagemDeLogin } from '../src/entrar/mensagens';
import { CABECALHOS_DE_SEGURANCA, novoNonce, politicaDeConteudo } from '../src/seguranca/csp';
import { lerCookieDoCabecalho } from '../src/seguranca/cookies';

describe('mensagens do /entrar', () => {
  it('código conhecido tem frase; desconhecido não é ecoado', () => {
    expect(mensagemDeLogin('CONTINUACAO_INVALIDA')).toBe(
      'O tempo para escolher o acesso terminou. Entre de novo.',
    );
    expect(mensagemDeLogin('SEM_VINCULO')).toBe(
      'Sua conta ainda não tem acesso a nenhuma organização. Peça acesso ao gestor.',
    );
    for (const c of ['<script>', '__proto__', 'constructor'])
      expect(mensagemDeLogin(c)).toBe(MENSAGEM_GENERICA);
    expect(mensagemDeLogin(undefined)).toBeNull();
    expect(mensagemDeLogin('')).toBeNull();
  });
});

describe('política de conteúdo', () => {
  const nonce = 'AAECAwQFBgcICQoLDA0ODw==';
  it('nonce em script e estilo, nada inline sem ele, sem moldura e sem base externa', () => {
    expect(politicaDeConteudo(nonce, { desenvolvimento: false, https: false })).toBe(
      "default-src 'self'; script-src 'self' 'nonce-AAECAwQFBgcICQoLDA0ODw==' 'strict-dynamic'; " +
        "style-src 'self' 'nonce-AAECAwQFBgcICQoLDA0ODw=='; img-src 'self' data:; font-src 'self'; " +
        "connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
    );
  });

  it("'unsafe-eval' só em desenvolvimento; upgrade só com origem https", () => {
    const dev = politicaDeConteudo(nonce, { desenvolvimento: true, https: false });
    expect(dev).toContain(`'nonce-${nonce}' 'strict-dynamic' 'unsafe-eval';`);
    expect(dev).not.toContain('upgrade-insecure-requests');
    expect(
      politicaDeConteudo(nonce, { desenvolvimento: false, https: true }).endsWith(
        '; upgrade-insecure-requests',
      ),
    ).toBe(true);
  });

  it('nonce fora do formato não entra na política', () => {
    expect(() => politicaDeConteudo("x' 'unsafe-inline", { desenvolvimento: false, https: false })).toThrow();
  });

  it('nonce novo de 128 bits a cada chamada', () => {
    const a = novoNonce();
    expect(a).toMatch(/^[A-Za-z0-9+/]{22}==$/);
    expect(novoNonce()).not.toBe(a);
  });

  it('Referrer-Policy same-origin mantém o Origin nos POSTs do próprio site', () => {
    expect(CABECALHOS_DE_SEGURANCA).toEqual({
      'x-content-type-options': 'nosniff',
      'referrer-policy': 'same-origin',
      'x-frame-options': 'DENY',
      'cross-origin-opener-policy': 'same-origin',
      'permissions-policy': 'camera=(), microphone=(), geolocation=(), payment=()',
    });
  });
});

describe('cookie pelo cabeçalho bruto', () => {
  it('valor único; ausente, vazio ou repetido é undefined', () => {
    expect(lerCookieDoCabecalho('a=1; __Host-x=tok', '__Host-x')).toBe('tok');
    expect(lerCookieDoCabecalho('__Host-x=tok; __Host-x=outro', '__Host-x')).toBeUndefined();
    expect(lerCookieDoCabecalho('__Host-x=', '__Host-x')).toBeUndefined();
    expect(lerCookieDoCabecalho(null, '__Host-x')).toBeUndefined();
  });
});
