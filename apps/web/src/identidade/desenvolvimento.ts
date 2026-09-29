import { randomBytes, timingSafeEqual } from 'node:crypto';

import { lerIdentidadeAmbiente } from '@safrion/db/web';
import type { Pool } from 'pg';

import type { ArmazemTransacaoLogin, ProvedorIdentidade } from './provedor';

/**
 * Provedor de desenvolvimento (ADR 0004 §5): usuários fictícios, para DEV e para os testes ponta a ponta locais. Só liga
 * com trava dupla e falha fechada: o processo diz SAFRION_AMBIENTE=dev E o banco está identificado como dev. Não é atalho
 * de login na homologação: lá a trava nega e a rota responde 404. O issuer é um URN que nenhum provedor real emite.
 */
export const ISSUER_DESENVOLVIMENTO = 'urn:safrion:desenvolvimento';

/** Subjects fictícios que o demo:reset vincula aos usuários da organização de demonstração. */
export const USUARIOS_DESENVOLVIMENTO: Readonly<Record<string, string>> = {
  'demo-almoxarife': 'Almoxarife (fictício)',
  'demo-gerente': 'Gerente (fictício)',
};

export async function desenvolvimentoLiberado(
  banco: Pool,
  ambienteDoProcesso: string | undefined = process.env['SAFRION_AMBIENTE'],
): Promise<boolean> {
  if (ambienteDoProcesso !== 'dev') return false;
  try {
    return (await lerIdentidadeAmbiente(banco)) === 'dev';
  } catch {
    return false;
  }
}

const aleatorio = () => randomBytes(32).toString('base64url');

function iguais(a: string, b: string): boolean {
  const x = Buffer.from(a);
  const y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}

/**
 * O "provedor" de DEV imita o protocolo: iniciar guarda state/nonce/verificador pela mesma porta do OIDC e manda para a
 * tela local de escolha do usuário fictício; concluir consome o ticket, confere o state e devolve a identidade. Assim o
 * login de DEV passa pelas mesmas rotas, pela mesma continuação e pela mesma criação de sessão da homologação.
 */
export function criarProvedorDesenvolvimento(
  armazem: ArmazemTransacaoLogin,
  origem: string,
): ProvedorIdentidade {
  return {
    nome: 'desenvolvimento',
    async iniciar(destino) {
      const state = aleatorio();
      const { ticket, expiraEm } = await armazem.abrir({
        state,
        nonce: aleatorio(),
        verificadorPkce: aleatorio(),
        destino,
      });
      const redirecionarPara = new URL('/entrar/desenvolvimento', origem);
      redirecionarPara.searchParams.set('state', state);
      return { redirecionarPara, ticket, expiraEm };
    },
    async concluir({ ticket, parametros }) {
      const transacao = await armazem.consumir(ticket ?? '');
      if (!transacao) return { ok: false, codigo: 'TICKET_AUSENTE_OU_USADO' };
      const state = parametros.get('state');
      const subject = parametros.get('code');
      if (state === null || subject === null) return { ok: false, codigo: 'RESPOSTA_INVALIDA' };
      if (!iguais(state, transacao.state)) return { ok: false, codigo: 'STATE_DIVERGENTE' };
      if (!Object.hasOwn(USUARIOS_DESENVOLVIMENTO, subject))
        return { ok: false, codigo: 'RESPOSTA_INVALIDA' };
      return {
        ok: true,
        identidade: { issuer: ISSUER_DESENVOLVIMENTO, subject },
        destino: transacao.destino,
      };
    },
  };
}
