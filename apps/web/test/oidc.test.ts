import { createHash, generateKeyPairSync, randomUUID, sign } from 'node:crypto';

import { describe, expect, it } from 'vitest';

import { INICIO } from '../src/identidade/caminho';
import { criarProvedorOidc, type ConfiguracaoOidc } from '../src/identidade/oidc/provedor';
import type { ArmazemTransacaoLogin, TransacaoLogin } from '../src/identidade/provedor';

const configuracao: ConfiguracaoOidc = {
  issuer: 'https://identidade.invalid',
  callback: 'https://safrion.invalid/entrar/retorno',
  clientId: 'cliente-sintetico',
  clientSecret: 'segredo-sintetico',
};
const chave = generateKeyPairSync('rsa', { modulusLength: 2048 });
const falsa = generateKeyPairSync('rsa', { modulusLength: 2048 });
const jwk = { ...chave.publicKey.export({ format: 'jwk' }), kid: 'teste', alg: 'RS256', use: 'sig' };

function jwt(claims: Record<string, unknown>, assinaturaInvalida: boolean): string {
  const header = Buffer.from(JSON.stringify({ alg: 'RS256', kid: 'teste' })).toString('base64url');
  const payload = Buffer.from(JSON.stringify(claims)).toString('base64url');
  const conteudo = `${header}.${payload}`;
  return `${conteudo}.${sign('RSA-SHA256', Buffer.from(conteudo), assinaturaInvalida ? falsa.privateKey : chave.privateKey).toString('base64url')}`;
}

async function cenario(
  opcoes: {
    claims?: Record<string, unknown>;
    assinaturaInvalida?: boolean;
    falhaRede?: boolean;
    semToken?: boolean;
    metadata?: Record<string, unknown>;
  } = {},
) {
  const pendentes = new Map<string, TransacaoLogin>();
  let tokenRequests = 0;
  let jwksRequests = 0;
  let codeChallenge = '';
  let nonce = '';
  const armazem: ArmazemTransacaoLogin = {
    abrir(transacao) {
      const ticket = randomUUID();
      pendentes.set(ticket, transacao);
      return Promise.resolve({ ticket, expiraEm: new Date(Date.now() + 60_000) });
    },
    consumir(ticket) {
      const transacao = pendentes.get(ticket) ?? null;
      pendentes.delete(ticket);
      return Promise.resolve(transacao);
    },
  };
  const provedor = await criarProvedorOidc(configuracao, armazem, async (url, init) => {
    const caminho = new URL(url).pathname;
    if (caminho === '/.well-known/openid-configuration') {
      return Response.json({
        issuer: configuracao.issuer,
        authorization_endpoint: `${configuracao.issuer}/authorize`,
        token_endpoint: `${configuracao.issuer}/token`,
        jwks_uri: `${configuracao.issuer}/jwks`,
        response_types_supported: ['code'],
        subject_types_supported: ['public'],
        id_token_signing_alg_values_supported: ['RS256'],
        code_challenge_methods_supported: ['S256'],
        ...opcoes.metadata,
      });
    }
    if (caminho === '/jwks') {
      jwksRequests++;
      return Response.json({ keys: [jwk] });
    }
    if (caminho !== '/token') throw new Error('Rota fictícia inesperada');
    tokenRequests++;
    if (opcoes.falhaRede) throw new TypeError('CANARIO_NUNCA_RETORNAR_TOKEN_SECRETO');
    if (typeof init.body !== 'string' && !(init.body instanceof URLSearchParams)) {
      throw new Error('Esperado formulário OAuth codificado');
    }
    const body = new URLSearchParams(await new Response(init.body).text());
    expect(body.get('redirect_uri')).toBe(configuracao.callback);
    expect(body.get('grant_type')).toBe('authorization_code');
    expect(body.get('client_id')).toBe(configuracao.clientId);
    const verifier = body.get('code_verifier');
    expect(verifier).toBeTruthy();
    expect(
      createHash('sha256')
        .update(verifier ?? '')
        .digest('base64url'),
    ).toBe(codeChallenge);
    const agora = Math.floor(Date.now() / 1000);
    return Response.json({
      access_token: 'access-token-sintetico',
      token_type: 'Bearer',
      ...(opcoes.semToken
        ? {}
        : {
            id_token: jwt(
              {
                iss: configuracao.issuer,
                sub: 'subject-original',
                aud: configuracao.clientId,
                iat: agora,
                exp: agora + 120,
                nonce,
                ...opcoes.claims,
              },
              opcoes.assinaturaInvalida ?? false,
            ),
          }),
    });
  });
  const inicio = await provedor.iniciar(INICIO);
  nonce = inicio.redirecionarPara.searchParams.get('nonce') ?? '';
  codeChallenge = inicio.redirecionarPara.searchParams.get('code_challenge') ?? '';
  const params = new URLSearchParams({
    state: inicio.redirecionarPara.searchParams.get('state') ?? '',
    code: 'codigo-sintetico',
  });
  return { provedor, inicio, params, pendentes, chamadas: () => ({ tokenRequests, jwksRequests }) };
}

describe('adaptador OIDC: protocolo real, transporte e armazenamento sintéticos', () => {
  it('envia PKCE S256, verifica assinatura e retorna só issuer+sub e destino', async () => {
    const c = await cenario({ claims: { email: 'email-nao-e-identidade@example.invalid' } });
    expect(c.inicio.redirecionarPara.searchParams.get('code_challenge_method')).toBe('S256');
    expect(c.inicio.redirecionarPara.searchParams.get('scope')).toBe('openid');
    const r = await c.provedor.concluir({ ticket: c.inicio.ticket, parametros: c.params });
    expect(r).toEqual({
      ok: true,
      identidade: { issuer: configuracao.issuer, subject: 'subject-original' },
      destino: '/',
    });
    expect(c.chamadas()).toEqual({ tokenRequests: 1, jwksRequests: 1 });
  });

  it.each([
    ['nonce divergente', { nonce: 'outro' }],
    ['issuer divergente', { iss: 'https://invasor.invalid' }],
    ['audience divergente', { aud: 'outro-cliente' }],
    ['token expirado', { exp: 1 }],
    ['subject vazio', { sub: '' }],
    ['nonce ausente', { nonce: undefined }],
    ['issuer ausente', { iss: undefined }],
    ['token sem expiração', { exp: undefined }],
    ['subject de tipo inválido', { sub: 42 }],
    ['audience múltipla sem azp', { aud: [configuracao.clientId, 'outro'] }],
  ])('recusa %s sem devolver identidade', async (_nome, claims) => {
    const c = await cenario({ claims });
    expect(await c.provedor.concluir({ ticket: c.inicio.ticket, parametros: c.params })).toEqual({
      ok: false,
      codigo: 'TOKEN_INVALIDO',
    });
  });

  it('recusa assinatura de outra chave mesmo com claims corretos', async () => {
    const c = await cenario({ assinaturaInvalida: true });
    expect(await c.provedor.concluir({ ticket: c.inicio.ticket, parametros: c.params })).toEqual({
      ok: false,
      codigo: 'TOKEN_INVALIDO',
    });
  });

  it('recusa ausência de ID token e falha de rede sem mensagem ou credenciais', async () => {
    for (const opcoes of [{ semToken: true }, { falhaRede: true }]) {
      const c = await cenario(opcoes);
      const r = await c.provedor.concluir({ ticket: c.inicio.ticket, parametros: c.params });
      expect(r.ok).toBe(false);
      expect(JSON.stringify(r)).not.toMatch(/CANARIO|access-token|segredo/);
    }
  });

  it('consome ticket antes da rede e admite apenas um callback concorrente', async () => {
    const c = await cenario();
    const rs = await Promise.all(
      [1, 2].map(() => c.provedor.concluir({ ticket: c.inicio.ticket, parametros: c.params })),
    );
    expect(rs.filter((r) => r.ok)).toHaveLength(1);
    expect(rs).toContainEqual({ ok: false, codigo: 'TICKET_AUSENTE_OU_USADO' });
    expect(c.chamadas().tokenRequests).toBe(1);
  });

  it.each([
    'ausente',
    'state',
    'duplicado',
    'erro',
    'ambos',
    'sem-code',
    'state-ausente',
    'state-duplo',
    'iss-duplo',
    'erro-duplo',
    'ticket-vencido',
  ])('recusa callback %s antes de consultar token', async (tipo) => {
    const c = await cenario();
    if (tipo === 'state') c.params.set('state', 'outro');
    if (tipo === 'state-ausente') c.params.delete('state');
    if (tipo === 'state-duplo') c.params.append('state', 'outro');
    if (tipo === 'iss-duplo') {
      c.params.append('iss', configuracao.issuer);
      c.params.append('iss', configuracao.issuer);
    }
    if (tipo === 'erro-duplo') {
      c.params.append('error', 'access_denied');
      c.params.append('error', 'outro');
    }
    // A validade/atomicidade é responsabilidade da porta PostgreSQL; expirado equivale a não encontrado.
    if (tipo === 'ticket-vencido') c.pendentes.clear();
    if (tipo === 'duplicado') c.params.append('code', 'outro');
    if (tipo === 'erro' || tipo === 'ambos') c.params.set('error', 'access_denied');
    if (tipo === 'erro' || tipo === 'sem-code') c.params.delete('code');
    const r = await c.provedor.concluir({
      ticket: tipo === 'ausente' ? undefined : c.inicio.ticket,
      parametros: c.params,
    });
    expect(r.ok).toBe(false);
    expect(c.chamadas().tokenRequests).toBe(0);
  });

  it('o mesmo e-mail não substitui o subject autenticado', async () => {
    const c = await cenario({ claims: { sub: 'subject-diferente', email: 'igual@example.invalid' } });
    expect(await c.provedor.concluir({ ticket: c.inicio.ticket, parametros: c.params })).toMatchObject({
      ok: true,
      identidade: { subject: 'subject-diferente' },
    });
  });

  it('recusa discovery de outro issuer ou com endpoint HTTP', async () => {
    await expect(cenario({ metadata: { issuer: 'https://invasor.invalid' } })).rejects.toThrow(
      'PROVEDOR_INDISPONIVEL',
    );
    await expect(
      cenario({ metadata: { token_endpoint: 'http://identidade.invalid/token' } }),
    ).rejects.toThrow('PROVEDOR_INDISPONIVEL');
  });
  it.each([
    { issuer: 'http://identidade.invalid' },
    { issuer: 'https://identidade.invalid/.well-known/openid-configuration' },
    { callback: 'https://usuario:senha@safrion.invalid/retorno' },
    { callback: 'https://safrion.invalid/retorno?destino=https://invasor.invalid' },
    { callback: 'https://safrion.invalid/retorno#fragmento' },
    { callback: 'nao-url' },
    { clientId: ' ' },
    { clientSecret: '' },
  ])('recusa configuração insegura antes de acessar rede', async (delta) => {
    let acessou = false;
    const armazenamento: ArmazemTransacaoLogin = {
      abrir: () => Promise.reject(new Error('Não deve armazenar')),
      consumir: () => Promise.resolve(null),
    };
    await expect(
      criarProvedorOidc({ ...configuracao, ...delta }, armazenamento, () => {
        acessou = true;
        return Promise.reject(new Error('Não deve acessar rede'));
      }),
    ).rejects.toThrow('CONFIGURACAO_OIDC_INVALIDA');
    expect(acessou).toBe(false);
  });

  it('recusa discovery sem chaves verificáveis', async () => {
    await expect(cenario({ metadata: { jwks_uri: undefined } })).rejects.toThrow('PROVEDOR_INDISPONIVEL');
  });
});
