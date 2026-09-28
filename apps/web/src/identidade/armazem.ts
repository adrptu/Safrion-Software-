import { abrirTransacaoLogin, consumirTransacaoLogin } from '@safrion/db/web';
import type { Pool } from 'pg';

import { caminhoInterno } from './caminho';
import type { ArmazemTransacaoLogin } from './provedor';

/** Porta de armazenamento da transação de login sobre a migração 0003 (ADR 0004 §5): uso único e validade curta. */
export function criarArmazemTransacaoLogin(banco: Pool): ArmazemTransacaoLogin {
  return {
    abrir: (t) =>
      abrirTransacaoLogin(banco, {
        state: t.state,
        nonce: t.nonce,
        verificadorPkce: t.verificadorPkce,
        destino: t.destino,
      }),
    async consumir(ticket) {
      const t = await consumirTransacaoLogin(banco, ticket);
      const destino = t ? caminhoInterno(t.destino) : null;
      return t && destino
        ? { state: t.state, nonce: t.nonce, verificadorPkce: t.verificadorPkce, destino }
        : null;
    },
  };
}
