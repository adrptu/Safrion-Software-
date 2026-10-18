import Link from 'next/link';

import type { EstadoExibido } from '../estoque/estado';
import { Selo } from './Selo';

export interface Migalha {
  readonly rotulo: string;
  readonly href?: string;
}

/**
 * Cabeçalho da tela (DS-27) com trilha (DS-29): Voltar só no detalhe, um h1, o selo de estado e, quando ajuda a decidir,
 * uma linha de contexto. A ação primária do detalhe fica no Próximo passo, não aqui (DS-58); a da listagem (criar) fica
 * aqui, à direita do título, só para quem pode executá-la.
 */
export function Cabecalho({
  trilha,
  titulo,
  estado,
  voltar,
  contexto,
  acao,
}: {
  readonly trilha: readonly Migalha[];
  readonly titulo: string;
  readonly estado?: EstadoExibido;
  readonly voltar?: { readonly href: string; readonly rotulo: string };
  readonly contexto?: string;
  readonly acao?: { readonly href: string; readonly rotulo: string };
}) {
  return (
    <header className="cabecalho">
      {trilha.length > 1 ? (
        <nav className="trilha" aria-label="Trilha">
          <ol>
            {trilha.map((m, i) =>
              m.href !== undefined && i < trilha.length - 1 ? (
                <li key={m.rotulo}>
                  <Link href={m.href}>{m.rotulo}</Link>
                </li>
              ) : (
                <li key={m.rotulo} aria-current="page">
                  {m.rotulo}
                </li>
              ),
            )}
          </ol>
        </nav>
      ) : null}
      <div className="titulo">
        {voltar ? (
          <Link className="voltar" href={voltar.href} aria-label={`Voltar para ${voltar.rotulo}`}>
            <span aria-hidden="true">‹</span>
          </Link>
        ) : null}
        <h1>{titulo}</h1>
        {estado ? <Selo estado={estado} /> : null}
        {acao ? (
          <Link className="botao botao-primario acao-da-lista" href={acao.href}>
            {acao.rotulo}
          </Link>
        ) : null}
      </div>
      {contexto ? <p className="subtitulo">{contexto}</p> : null}
    </header>
  );
}
