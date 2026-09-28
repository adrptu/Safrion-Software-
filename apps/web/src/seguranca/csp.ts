/**
 * Política de conteúdo com nonce por requisição (ADR 0004 §7; guia de CSP do Next 16): só roda script do próprio site
 * com o nonce desta resposta, e 'strict-dynamic' deixa esses scripts carregarem os pedaços da aplicação. Estilo também
 * só com nonce: atributo style em HTML fica bloqueado. 'unsafe-eval' só em desenvolvimento, que o React usa para
 * reconstruir pilhas de erro; upgrade-insecure-requests só quando a origem configurada é https.
 */
export function politicaDeConteudo(
  nonce: string,
  opcoes: { readonly desenvolvimento: boolean; readonly https: boolean },
): string {
  if (!/^[A-Za-z0-9+/]{16,}={0,2}$/.test(nonce)) throw new Error('Nonce fora do formato base64.');
  return [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${opcoes.desenvolvimento ? " 'unsafe-eval'" : ''}`,
    `style-src 'self' 'nonce-${nonce}'`,
    "img-src 'self' data:",
    "font-src 'self'",
    "connect-src 'self'",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    ...(opcoes.https ? ['upgrade-insecure-requests'] : []),
  ].join('; ');
}

/** 128 bits aleatórios em base64, novos a cada requisição. */
export function novoNonce(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  return btoa(String.fromCharCode(...bytes));
}

/**
 * Cabeçalhos fixos de todas as respostas. Referrer-Policy same-origin: nada vaza para outro site, e o POST do próprio
 * site continua levando o Origin real, que as rotas conferem (no-referrer faria o navegador mandar Origin: null).
 */
export const CABECALHOS_DE_SEGURANCA: Readonly<Record<string, string>> = {
  'x-content-type-options': 'nosniff',
  'referrer-policy': 'same-origin',
  'x-frame-options': 'DENY',
  'cross-origin-opener-policy': 'same-origin',
  'permissions-policy': 'camera=(), microphone=(), geolocation=(), payment=()',
};
