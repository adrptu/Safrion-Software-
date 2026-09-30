import type { IntencaoGuardada } from './pendencias';
import { consultaDeRetorno, hrefComRetorno } from './lista';

/** A recuperação abre o alvo confirmado, usando o contexto original e sem aninhar `volta` em `volta`. */
export function destinoConfirmado(g: IntencaoGuardada): string {
  const contexto = new URL(g.contexto.volta, 'http://safrion.local');
  const query =
    contexto.pathname === '/cadastros/areas'
      ? contexto.searchParams
      : new URLSearchParams(contexto.searchParams.get('volta') ?? '');
  const base = g.intencao.targetType === 'farm' ? '/cadastros/fazendas/' : '/cadastros/areas/';
  return hrefComRetorno(base + encodeURIComponent(g.intencao.targetId), consultaDeRetorno(query));
}
