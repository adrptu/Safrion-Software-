import { redirect } from 'next/navigation';

/** A primeira tela é o trabalho: o Estoque (sem início decorativo). */
export default function Inicio() {
  redirect('/estoque');
}
