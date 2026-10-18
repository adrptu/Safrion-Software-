'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

/**
 * Item do menu lateral (DS-28): ativo na própria tela e nos detalhes que saem dela, com aria-current. `exceto` tira as
 * subáreas que têm item próprio (Estoque não fica ativo em Recebimentos).
 */
export function ItemMenu({
  href,
  rotulo,
  exceto = [],
}: {
  readonly href: string;
  readonly rotulo: string;
  readonly exceto?: readonly string[];
}) {
  const caminho = usePathname();
  const dentro = (h: string) => caminho === h || caminho.startsWith(`${h}/`);
  const ativo = dentro(href) && !exceto.some(dentro);
  return (
    <Link href={href} aria-current={ativo ? 'page' : undefined}>
      {rotulo}
    </Link>
  );
}
