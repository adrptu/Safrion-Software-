import { vinculosDaContinuacao } from '@safrion/db/web';
import { headers } from 'next/headers';
import { redirect } from 'next/navigation';

import { nomeDoPapel } from '../../../autorizacao/matriz';
import { COOKIE_CONTINUACAO, lerCookieDoCabecalho } from '../../../seguranca/cookies';
import { dependencias } from '../../../servidor/ambiente';

/**
 * Escolha de organização e papel depois do provedor (ADR 0004 §5): a identidade já está no servidor, guardada na
 * continuação; a tela só oferece os vínculos vivos. Continuação ausente ou vencida volta ao /entrar com o motivo.
 */
export default async function Escolher() {
  const ticket = lerCookieDoCabecalho((await headers()).get('cookie'), COOKIE_CONTINUACAO);
  const vinculos = await vinculosDaContinuacao(dependencias().banco, ticket);
  if (vinculos.length === 0) redirect('/entrar?erro=CONTINUACAO_INVALIDA');
  return (
    <main className="acesso">
      <div className="acesso-cartao">
        <span className="marca">Safrion</span>
        <h1>Escolha o acesso</h1>
        <ul className="opcoes">
          {vinculos.flatMap((v) =>
            v.papeis.map((papel) => (
              <li key={`${v.organizationId}-${papel}`}>
                <form method="post" action="/entrar/escolher/confirmar">
                  <input type="hidden" name="organizationId" value={v.organizationId} />
                  <input type="hidden" name="papel" value={papel} />
                  <button type="submit" className="botao">
                    <span>{v.organizacao}</span>
                    <span className="detalhe">{nomeDoPapel(papel)}</span>
                  </button>
                </form>
              </li>
            )),
          )}
        </ul>
      </div>
    </main>
  );
}
