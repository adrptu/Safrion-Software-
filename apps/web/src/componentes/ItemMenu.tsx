'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

/** Item do menu lateral (DS-28): ativo na própria tela e nos detalhes que saem dela, com aria-current. */
export function ItemMenu({ href, rotulo }: { readonly href: string; readonly rotulo: string }) {
  const caminho = usePathname();
  const ativo = caminho === href || caminho.startsWith(`${href}/`);
  return (
    <Link href={href} aria-current={ativo ? 'page' : undefined}>
      {rotulo}
    </Link>
  );
}
