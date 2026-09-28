import {
  EsquemaDadosMovimento,
  EsquemaPedidoComando,
  erroDeValidacao,
  statusDoRecibo,
} from '@safrion/contracts';
import {
  executarComando,
  pedidoDeMovimento,
  registrarMovimento,
  resolverSessao,
  respostaDeErro,
} from '@safrion/db/web';

import { ehComando, podeExecutar } from '../autorizacao/matriz';
import { COOKIE_SESSAO, lerCookie } from '../seguranca/cookies';
import {
  correlacaoDe,
  ErroRequisicao,
  exigirJson,
  exigirOrigem,
  lerCorpoLimitado,
} from '../seguranca/requisicao';
import type { Dependencias } from '../servidor/ambiente';
import { erro, json } from './resposta';

/** O maior pedido da F0-c (entrada de estoque) tem menos de 1 KiB; a F1 revê o limite com o documento de entrada. */
export const LIMITE_CORPO_BYTES = 16 * 1024;

const MENSAGENS: Record<ErroRequisicao['codigo'], string> = {
  CORPO_EXCEDE_LIMITE: 'O pedido passou do tamanho permitido.',
  TIPO_DE_CONTEUDO_INVALIDO: 'O pedido tem de ser JSON.',
  SEM_PERMISSAO: 'Origem da requisição recusada.',
  CONTRATO_INVALIDO: 'O pedido não está em UTF-8 válido.',
};

/**
 * POST /api/v1/comandos/{commandType} (ADR 0004 §1–§7): o único caminho de mutação. A organização e o ator vêm da
 * sessão, nunca do corpo; a matriz nega por padrão; o corpo é lido com limite de bytes antes do parse; o envelope da
 * F0-b garante idempotência, recibo, auditoria e outbox. Erro inesperado responde FALHA_INTERNA com a correlação.
 */
export function criarRotaComandos(deps: () => Pick<Dependencias, 'banco' | 'origem' | 'registrador'>) {
  return async function POST(
    requisicao: Request,
    contexto: { params: Promise<{ commandType: string }> },
  ): Promise<Response> {
    const correlationId = correlacaoDe(requisicao);
    const { banco, origem, registrador } = deps();
    const { commandType } = await contexto.params;
    try {
      if (!ehComando(commandType)) return erro('NAO_ENCONTRADO', 'Comando inexistente.', correlationId);
      exigirOrigem(requisicao, origem);
      exigirJson(requisicao);
      const sessao = await resolverSessao(banco, lerCookie(requisicao, COOKIE_SESSAO));
      if (!sessao) return erro('NAO_AUTENTICADO', 'Entre de novo para continuar.', correlationId);
      if (!podeExecutar(sessao.papel, commandType)) {
        return erro('SEM_PERMISSAO', 'Seu papel não permite esta ação.', correlationId);
      }
      let bruto: unknown;
      try {
        bruto = JSON.parse(await lerCorpoLimitado(requisicao, LIMITE_CORPO_BYTES));
      } catch (e) {
        if (e instanceof ErroRequisicao) throw e;
        return erro('CONTRATO_INVALIDO', 'O corpo não é JSON válido.', correlationId);
      }
      const pedido = EsquemaPedidoComando.safeParse(bruto);
      if (!pedido.success) {
        const { status, corpo } = erroDeValidacao(pedido.error, correlationId);
        return json(status, corpo);
      }
      const dados = EsquemaDadosMovimento.safeParse(pedido.data.data);
      if (!dados.success || dados.data.movimento.tipo !== 'entrada') {
        return erro('CONTRATO_INVALIDO', 'Este comando só aceita uma entrada de estoque.', correlationId);
      }
      const recibo = await executarComando(
        banco,
        sessao.organizationId,
        {
          commandType,
          idempotencyKey: pedido.data.idempotencyKey,
          initiatorKind: 'web',
          actorId: sessao.usuarioId,
          target: pedido.data.target,
          data: pedido.data.data,
          correlationId,
          ...(pedido.data.confirmedAt ? { confirmedAt: pedido.data.confirmedAt } : {}),
          ...(pedido.data.deviceId ? { deviceId: pedido.data.deviceId } : {}),
        },
        registrarMovimento(pedidoDeMovimento(dados.data)),
        { registrador },
      );
      return json(statusDoRecibo(recibo.outcome), recibo, { 'x-correlation-id': correlationId });
    } catch (e) {
      if (e instanceof ErroRequisicao) return erro(e.codigo, MENSAGENS[e.codigo], correlationId);
      const { status, corpo } = respostaDeErro(e, correlationId);
      return json(status, corpo, { 'x-correlation-id': correlationId });
    }
  };
}
