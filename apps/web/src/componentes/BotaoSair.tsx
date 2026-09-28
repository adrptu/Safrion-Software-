'use client';

import { apagarRascunhos, armazemDaSessao } from '../estoque/rascunho';

/** Sair (POST /sair) apagando antes os rascunhos desta aba: a próxima pessoa no mesmo navegador não os vê. */
export function BotaoSair() {
  return (
    <form
      method="post"
      action="/sair"
      onSubmit={() => {
        apagarRascunhos(armazemDaSessao());
      }}
    >
      <button type="submit" className="sair">
        Sair
      </button>
    </form>
  );
}
