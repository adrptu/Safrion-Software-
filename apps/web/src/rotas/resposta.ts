import { erroContrato, type CodigoErro } from '@safrion/contracts';

const SEM_CACHE = { 'cache-control': 'no-store' };

/** Retry-After só em 503 com `detalhe.repetirEmMs` finito e positivo, em segundos inteiros (contrato CMD-15 §9.2). */
function repetirDepois(status: number, corpo: unknown): Record<string, string> {
  if (status !== 503 || typeof corpo !== 'object' || corpo === null) return {};
  const detalhe: unknown = (corpo as { detalhe?: unknown }).detalhe;
  if (typeof detalhe !== 'object' || detalhe === null) return {};
  const ms: unknown = (detalhe as { repetirEmMs?: unknown }).repetirEmMs;
  return typeof ms === 'number' && Number.isFinite(ms) && ms > 0
    ? { 'retry-after': String(Math.ceil(ms / 1000)) }
    : {};
}

export function json(status: number, corpo: unknown, cabecalhos: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      ...SEM_CACHE,
      ...repetirDepois(status, corpo),
      ...cabecalhos,
    },
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
