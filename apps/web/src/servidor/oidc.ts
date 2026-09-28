import type { CustomFetch } from 'openid-client';

import { criarArmazemTransacaoLogin } from '../identidade/armazem';
import { criarProvedorOidc, type ConfiguracaoOidc } from '../identidade/oidc/provedor';
import type { ProvedorIdentidade } from '../identidade/provedor';
import type { Dependencias } from './ambiente';

/**
 * Provedor OIDC para a casca: null quando o ambiente não configura o OIDC (login indisponível, sem atalho); rejeita com
 * o erro do adaptador quando a configuração é inválida ou a descoberta falha.
 */
export type FabricaOidc = (d: Pick<Dependencias, 'banco' | 'origem'>) => Promise<ProvedorIdentidade | null>;

type Variaveis = Readonly<Record<string, string | undefined>>;

/**
 * Configuração do OIDC pelo ambiente do processo (ADR 0004): issuer, client id e segredo chegam por variável, vindos do
 * cofre; o callback é a rota fixa na origem configurada da aplicação, nunca algo da requisição. Faltando qualquer uma
 * das três variáveis, null.
 */
export function configuracaoOidc(env: Variaveis, origem: string): ConfiguracaoOidc | null {
  const issuer = env['SAFRION_OIDC_ISSUER'];
  const clientId = env['SAFRION_OIDC_CLIENT_ID'];
  const clientSecret = env['SAFRION_OIDC_CLIENT_SECRET'];
  if (!issuer || !clientId || !clientSecret) return null;
  return { issuer, clientId, clientSecret, callback: new URL('/entrar/retorno', origem).href };
}

/**
 * Fábrica com a descoberta memorizada por processo: a primeira requisição de login descobre o provedor e as seguintes,
 * inclusive as simultâneas, reusam a mesma promessa. Falha não fica guardada: a próxima tentativa descobre de novo, e
 * um provedor que volta a responder volta a servir sem reiniciar o processo. O transporte só existe para os testes.
 */
export function criarFabricaOidc(
  opcoes: {
    readonly env?: Variaveis;
    readonly transporte?: CustomFetch;
    readonly criar?: typeof criarProvedorOidc;
  } = {},
): FabricaOidc {
  const { env = process.env, transporte, criar = criarProvedorOidc } = opcoes;
  let emCurso: Promise<ProvedorIdentidade> | undefined;
  return async (d) => {
    const configuracao = configuracaoOidc(env, d.origem);
    if (!configuracao) return null;
    if (!emCurso) {
      const tentativa = criar(configuracao, criarArmazemTransacaoLogin(d.banco), transporte);
      emCurso = tentativa;
      tentativa.catch(() => {
        if (emCurso === tentativa) emCurso = undefined;
      });
    }
    return emCurso;
  };
}
