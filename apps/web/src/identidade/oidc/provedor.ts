import * as oidc from 'openid-client';

import type { ArmazemTransacaoLogin, CodigoFalhaLogin, ProvedorIdentidade } from '../provedor';

export interface ConfiguracaoOidc {
  readonly issuer: string;
  readonly clientId: string;
  readonly clientSecret: string;
  readonly callback: string;
}

function urlSegura(valor: string): URL {
  const url = new URL(valor);
  if (url.protocol !== 'https:' || url.username || url.password || url.hash || url.search) {
    throw new Error('CONFIGURACAO_OIDC_INVALIDA');
  }
  return url;
}

function falhaDoProvedor(erro: unknown): CodigoFalhaLogin {
  if (erro instanceof TypeError || (erro instanceof Error && erro.name === 'TimeoutError')) {
    return 'PROVEDOR_INDISPONIVEL';
  }
  return 'TOKEN_INVALIDO';
}

/**
 * ADR0004: autentica issuer+sub, sem SQL, sessão, escolha de organização ou vínculo por e-mail.
 * O transporte injetável é só uma fronteira HTTP para testes; a configuração continua exigindo HTTPS.
 */
export async function criarProvedorOidc(
  opcoes: ConfiguracaoOidc,
  armazem: ArmazemTransacaoLogin,
  transporte?: oidc.CustomFetch,
): Promise<ProvedorIdentidade> {
  let issuer: URL;
  let callback: URL;
  try {
    issuer = urlSegura(opcoes.issuer);
    callback = urlSegura(opcoes.callback);
    if (!opcoes.clientId.trim() || !opcoes.clientSecret.trim() || issuer.pathname.includes('.well-known')) {
      throw new Error('CONFIGURACAO_OIDC_INVALIDA');
    }
  } catch {
    throw new Error('CONFIGURACAO_OIDC_INVALIDA');
  }
  let config: oidc.Configuration;
  try {
    config = await oidc.discovery(
      issuer,
      opcoes.clientId,
      { client_secret: opcoes.clientSecret, id_token_signed_response_alg: 'RS256', [oidc.clockTolerance]: 0 },
      oidc.ClientSecretPost(opcoes.clientSecret),
      {
        timeout: 5,
        execute: [oidc.enableNonRepudiationChecks],
        ...(transporte ? { [oidc.customFetch]: transporte } : {}),
      },
    );
    // A metadata descoberta é entrada externa: não permitir endpoint de troca/chaves sem HTTPS.
    const metadata = config.serverMetadata();
    for (const endpoint of [metadata.authorization_endpoint, metadata.token_endpoint, metadata.jwks_uri]) {
      if (!endpoint) throw new Error('CONFIGURACAO_OIDC_INVALIDA');
      urlSegura(endpoint);
    }
  } catch {
    throw new Error('PROVEDOR_INDISPONIVEL');
  }

  return {
    nome: 'oidc',
    async iniciar(destino) {
      const transacao = {
        state: oidc.randomState(),
        nonce: oidc.randomNonce(),
        verificadorPkce: oidc.randomPKCECodeVerifier(),
        destino,
      };
      const redirecionarPara = oidc.buildAuthorizationUrl(config, {
        redirect_uri: callback.href,
        scope: 'openid',
        response_type: 'code',
        state: transacao.state,
        nonce: transacao.nonce,
        code_challenge: await oidc.calculatePKCECodeChallenge(transacao.verificadorPkce),
        code_challenge_method: 'S256',
      });
      const ticket = await armazem.abrir(transacao);
      return { ...ticket, redirecionarPara };
    },
    async concluir({ ticket, parametros }) {
      if (!ticket) return { ok: false, codigo: 'TICKET_AUSENTE_OU_USADO' };
      // Consumir antes de qualquer tentativa: sucesso, erro e callback inválido são de uso único.
      const transacao = await armazem.consumir(ticket);
      if (!transacao) return { ok: false, codigo: 'TICKET_AUSENTE_OU_USADO' };
      if (
        parametros.getAll('state').length !== 1 ||
        parametros.getAll('iss').length > 1 ||
        parametros.getAll('code').length > 1 ||
        parametros.getAll('error').length > 1 ||
        (parametros.has('code') && parametros.has('error'))
      ) {
        return { ok: false, codigo: 'RESPOSTA_INVALIDA' };
      }
      if (parametros.get('state') !== transacao.state) return { ok: false, codigo: 'STATE_DIVERGENTE' };
      if (parametros.has('error')) return { ok: false, codigo: 'NEGADO_NO_PROVEDOR' };
      if (!parametros.get('code')) return { ok: false, codigo: 'RESPOSTA_INVALIDA' };
      const retorno = new URL(callback);
      retorno.search = parametros.toString();
      try {
        const tokens = await oidc.authorizationCodeGrant(config, retorno, {
          expectedState: transacao.state,
          expectedNonce: transacao.nonce,
          pkceCodeVerifier: transacao.verificadorPkce,
          idTokenExpected: true,
        });
        const identidade = tokens.claims();
        if (!identidade?.sub) return { ok: false, codigo: 'TOKEN_INVALIDO' };
        return {
          ok: true,
          identidade: { issuer: identidade.iss, subject: identidade.sub },
          destino: transacao.destino,
        };
      } catch (erro) {
        return { ok: false, codigo: falhaDoProvedor(erro) };
      }
    },
  };
}
