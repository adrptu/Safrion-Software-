'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ItemMenu } from '../componentes/ItemMenu';
import s from './cadastro.module.css';
export function MenuCadastros() {
  const path = usePathname();
  const ativo =
    path === '/cadastros/areas' ||
    path.startsWith('/cadastros/areas/') ||
    path.startsWith('/cadastros/fazendas/');
  return (
    <li>
      <span className={s.menuTitulo}>Cadastros</span>
      <ul aria-label="Cadastros">
        <li>
          <ItemMenu href="/cadastros/produtos" rotulo="Produtos" />
        </li>
        <li>
          <Link href="/cadastros/areas" aria-current={ativo ? 'page' : undefined}>
            Fazendas e talhões
          </Link>
        </li>
      </ul>
    </li>
  );
}
