import { NextResponse, type NextRequest } from 'next/server';

import { CABECALHOS_DE_SEGURANCA, novoNonce, politicaDeConteudo } from './seguranca/csp';

/**
 * Proxy do Next 16 (antigo middleware): gera o nonce da CSP a cada requisição e o entrega ao Next pelo cabeçalho da
 * requisição, que o aplica aos scripts e estilos que ele mesmo emite. Não decide acesso: a sessão é conferida no banco
 * pela página ou pela rota (ADR 0004 §3).
 */
export function proxy(requisicao: NextRequest) {
  const nonce = novoNonce();
  const politica = politicaDeConteudo(nonce, {
    desenvolvimento: process.env.NODE_ENV === 'development',
    https: process.env['SAFRION_ORIGEM']?.startsWith('https://') === true,
  });
  const cabecalhos = new Headers(requisicao.headers);
  cabecalhos.set('x-nonce', nonce);
  cabecalhos.set('content-security-policy', politica);
  const resposta = NextResponse.next({ request: { headers: cabecalhos } });
  resposta.headers.set('content-security-policy', politica);
  for (const [nome, valor] of Object.entries(CABECALHOS_DE_SEGURANCA)) resposta.headers.set(nome, valor);
  return resposta;
}

export const config = {
  matcher: [
    {
      source: '/((?!_next/static|_next/image|favicon.ico).*)',
      missing: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' },
      ],
    },
  ],
};
