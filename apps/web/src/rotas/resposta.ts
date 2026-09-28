import { erroContrato, type CodigoErro } from '@safrion/contracts';

const SEM_CACHE = { 'cache-control': 'no-store' };

export function json(status: number, corpo: unknown, cabecalhos: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', ...SEM_CACHE, ...cabecalhos },
  });
}

export function erro(codigo: CodigoErro, mensagem: string, correlationId: string): Response {
  const { status, corpo } = erroContrato(codigo, mensagem, correlationId);
  return json(status, corpo, { 'x-correlation-id': correlationId });
}

/** Redirecionamento 303 para um caminho interno da aplicação, com cookies opcionais. */
export function redirecionar(origem: string, caminho: string, cookies: readonly string[] = []): Response {
  const cabecalhos = new Headers({ location: new URL(caminho, origem).toString(), ...SEM_CACHE });
  for (const c of cookies) cabecalhos.append('set-cookie', c);
  return new Response(null, { status: 303, headers: cabecalhos });
}
