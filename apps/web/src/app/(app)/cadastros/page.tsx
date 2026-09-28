import { redirect } from 'next/navigation';

/** Cadastros da F0-c: só produtos. */
export default function Cadastros() {
  redirect('/cadastros/produtos');
}
