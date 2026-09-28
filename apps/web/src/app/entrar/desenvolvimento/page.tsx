import { notFound } from 'next/navigation';

import { desenvolvimentoLiberado, USUARIOS_DESENVOLVIMENTO } from '../../../identidade/desenvolvimento';
import { dependencias } from '../../../servidor/ambiente';

type Busca = Promise<Record<string, string | string[] | undefined>>;

/**
 * "Tela do provedor" de DEV (ADR 0004 §5): escolher o usuário fictício e voltar ao callback com o state. Só existe com
 * a trava dupla (processo e banco em dev); fora disso é 404, como rota inexistente.
 */
export default async function EntrarDesenvolvimento({ searchParams }: { readonly searchParams: Busca }) {
  const d = dependencias();
  if (!(await desenvolvimentoLiberado(d.banco, d.ambienteDoProcesso))) notFound();
  const state = (await searchParams)['state'];
  if (typeof state !== 'string' || !/^[A-Za-z0-9_-]{16,128}$/.test(state)) notFound();
  return (
    <main className="acesso">
      <div className="acesso-cartao">
        <span className="marca">Safrion</span>
        <span className="selo-ambiente">Desenvolvimento</span>
        <h1>Usuário fictício</h1>
        <ul className="opcoes">
          {Object.entries(USUARIOS_DESENVOLVIMENTO).map(([subject, nome]) => (
            <li key={subject}>
              <form method="post" action="/entrar/desenvolvimento/autorizar">
                <input type="hidden" name="state" value={state} />
                <button type="submit" className="botao" name="usuario" value={subject}>
                  {nome}
                </button>
              </form>
            </li>
          ))}
        </ul>
      </div>
    </main>
  );
}
