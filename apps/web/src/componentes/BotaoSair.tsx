'use client';

import { apagarRascunhos, armazemDaSessao } from '../estoque/rascunho';
import { armazemLocal } from '../recebimento/rascunho';

/**
 * Sair (POST /sair) apagando antes os rascunhos desta aba e os do recebimento guardados no navegador: a próxima pessoa
 * no mesmo navegador não os vê. Só este gesto apaga; sessão que expira não apaga (contrato CMD-15 §6.2).
 */
export function BotaoSair() {
  return (
    <form
      method="post"
      action="/sair"
      onSubmit={() => {
        apagarRascunhos(armazemDaSessao());
        apagarRascunhos(armazemLocal());
      }}
    >
      <button type="submit" className="sair">
        Sair
      </button>
    </form>
  );
}
