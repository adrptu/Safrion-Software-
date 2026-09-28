import '../estilo/tokens.css';
import '../estilo/componentes.css';

import type { Metadata } from 'next';
import { connection } from 'next/server';
import type { ReactNode } from 'react';

export const metadata: Metadata = { title: 'Safrion', robots: { index: false, follow: false } };

/**
 * Raiz do site. Tudo renderiza por requisição: a CSP com nonce só vale em página dinâmica, e nenhuma tela do Safrion
 * pode sair de um HTML gerado no build (dado, sessão e ambiente mudam a cada acesso).
 */
export default async function RaizDoSite({ children }: { readonly children: ReactNode }) {
  await connection();
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
