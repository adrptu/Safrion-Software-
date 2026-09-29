import {
  emOrganizacao,
  lerIdentidadeAmbiente,
  resolverSessao,
  type NomeAmbiente,
  type SessaoResolvida,
} from '@safrion/db/web';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';
import type { ClientBase } from 'pg';
import { cache } from 'react';

import { COOKIE_SESSAO, lerCookieDoCabecalho } from '../seguranca/cookies';
import { dependencias } from './ambiente';

/**
 * Sessão das páginas (ADR 0004 §3): o mesmo resolverSessao das rotas, que confere no banco vínculo, usuário ativo e papel
 * a cada requisição. Uma consulta por requisição (cache do React); a página que exige sessão manda ao /entrar com o
 * destino, e a organização de toda leitura vem da sessão, nunca da URL.
 */
export const sessaoAtual = cache(async (): Promise<SessaoResolvida | null> => {
  const token = lerCookieDoCabecalho((await headers()).get('cookie'), COOKIE_SESSAO);
  return resolverSessao(dependencias().banco, token);
});

export async function exigirSessao(destino: string): Promise<SessaoResolvida> {
  const sessao = await sessaoAtual();
  if (!sessao) redirect(`/entrar?${new URLSearchParams({ destino }).toString()}`);
  return sessao;
}

/** Leitura dentro da organização da sessão: o RLS limita tudo a ela. */
export function consultar<T>(
  sessao: SessaoResolvida,
  leitura: (cliente: ClientBase) => Promise<T>,
): Promise<T> {
  return emOrganizacao(dependencias().banco, sessao.organizationId, leitura);
}

/** Ambiente declarado no banco, para o selo permanente; indisponível não derruba a tela. */
export const ambienteAtual = cache(async (): Promise<NomeAmbiente | null> => {
  try {
    return await lerIdentidadeAmbiente(dependencias().banco);
  } catch {
    return null;
  }
});

export const NOME_DO_AMBIENTE: Readonly<Record<NomeAmbiente, string | null>> = {
  dev: 'Desenvolvimento',
  hml: 'Homologação',
  prod: null,
};
