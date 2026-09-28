/**
 * Cookies da sessão e do login (ADR 0004 §3 e §5). Prefixo __Host-: exige Secure e Path=/ e proíbe Domain, então um
 * subdomínio não consegue plantar o cookie. HttpOnly e SameSite=Lax; nenhum dado pessoal, só o token opaco.
 */
export const COOKIE_SESSAO = '__Host-safrion-sessao';
export const COOKIE_LOGIN = '__Host-safrion-login';
export const COOKIE_CONTINUACAO = '__Host-safrion-continuacao';

const NOME = /^[A-Za-z0-9_-]+$/;

/** Valor do cookie; ausente, vazio ou repetido na requisição (tentativa de plantar outro) devolve undefined. */
export function lerCookie(requisicao: Request, nome: string): string | undefined {
  const cabecalho = requisicao.headers.get('cookie');
  if (cabecalho === null) return undefined;
  const valores = cabecalho
    .split(';')
    .map((par) => par.trim())
    .filter((par) => par.startsWith(`${nome}=`))
    .map((par) => par.slice(nome.length + 1));
  return valores.length === 1 && valores[0] !== '' ? valores[0] : undefined;
}

export function definirCookie(nome: string, valor: string, expiraEm: Date): string {
  if (!NOME.test(nome.replace('__Host-', '')) || !/^[A-Za-z0-9_-]+$/.test(valor)) {
    throw new Error('Cookie com nome ou valor fora do formato de token.');
  }
  return `${nome}=${valor}; Path=/; Expires=${expiraEm.toUTCString()}; HttpOnly; Secure; SameSite=Lax`;
}

export function apagarCookie(nome: string): string {
  return `${nome}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`;
}
