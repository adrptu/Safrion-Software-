import { statusDoRecibo } from '@safrion/contracts';
import { consultarIntencao, emOrganizacao, resolverSessao, respostaDeErro } from '@safrion/db/web';

import { ehComando, podeExecutar } from '../autorizacao/matriz';
import { COOKIE_SESSAO, lerCookie } from '../seguranca/cookies';
import { correlacaoDe } from '../seguranca/requisicao';
import type { Dependencias } from '../servidor/ambiente';
import { erro, json } from './resposta';

/** Chegada de outro site: Origin diferente da aplicação, ou o navegador dizendo que a requisição veio de fora. */
export function deOutroSite(requisicao: Request, origem: string): boolean {
  const recebida = requisicao.headers.get('origin');
  const sitio = requisicao.headers.get('sec-fetch-site');
  return (
    (recebida !== null && recebida !== origem) ||
    (sitio !== null && sitio !== 'same-origin' && sitio !== 'none')
  );
}

/**
 * GET /api/v1/intencoes/{commandType}/{chave} (IDEM-09; contrato CMD-15 §6.2): recupera, sem efeito, o recibo de uma
 * intenção que o próprio usuário enviou. Organização e autor vêm da sessão, nunca da requisição; quem não pode executar
 * o comando não consulta a chave dele. Recibo registrado volta com o mesmo status e corpo do reenvio do POST; sem recibo
 * visível, "ainda não localizado" (404 RECIBO_NAO_LOCALIZADO), nunca "não recebido".
 */
export function criarRotaIntencoes(deps: () => Pick<Dependencias, 'banco' | 'origem'>) {
  return async function GET(
    requisicao: Request,
    contexto: { params: Promise<{ commandType: string; chave: string }> },
  ): Promise<Response> {
    const correlationId = correlacaoDe(requisicao);
    const { banco, origem } = deps();
    const { commandType, chave } = await contexto.params;
    try {
      if (!ehComando(commandType)) return erro('NAO_ENCONTRADO', 'Comando inexistente.', correlationId);
      if (new URL(requisicao.url).search !== '') {
        return erro('CONTRATO_INVALIDO', 'A consulta do recibo não aceita parâmetros.', correlationId);
      }
      if (deOutroSite(requisicao, origem)) {
        return erro('SEM_PERMISSAO', 'Origem da requisição recusada.', correlationId);
      }
      const sessao = await resolverSessao(banco, lerCookie(requisicao, COOKIE_SESSAO));
      if (!sessao) return erro('NAO_AUTENTICADO', 'Entre de novo para continuar.', correlationId);
      if (!podeExecutar(sessao.papel, commandType)) {
        return erro('SEM_PERMISSAO', 'Seu papel não permite esta ação.', correlationId);
      }
      if (chave.trim() === '' || chave.length > 128) {
        return erro('CONTRATO_INVALIDO', 'A chave da intenção tem de 1 a 128 caracteres.', correlationId);
      }
      const recibo = await emOrganizacao(banco, sessao.organizationId, (c) =>
        consultarIntencao(c, { commandType, idempotencyKey: chave, actorId: sessao.usuarioId }),
      );
      if (!recibo) {
        return erro(
          'RECIBO_NAO_LOCALIZADO',
          'Recibo ainda não localizado: reenvie o mesmo pedido com a mesma chave; ele não é gravado duas vezes.',
          correlationId,
        );
      }
      return json(statusDoRecibo(recibo.outcome), recibo, { 'x-correlation-id': correlationId });
    } catch (e) {
      const { status, corpo } = respostaDeErro(e, correlationId);
      return json(status, corpo, { 'x-correlation-id': correlationId });
    }
  };
}
