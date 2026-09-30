import {
  EsquemaDadosMovimento,
  EsquemaDadosRecebimento,
  EsquemaPedidoComando,
  canonizarRecebimento,
  erroDeValidacao,
  statusDoRecibo,
  type PedidoComando,
} from '@safrion/contracts';
import {
  executarComando,
  pedidoDeMovimento,
  receberDocumento,
  registrarMovimento,
  resolverSessao,
  respostaDeErro,
  type Efeito,
} from '@safrion/db/web';

import { ehComando, podeExecutar, type Comando } from '../autorizacao/matriz';
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

/** O maior pedido da F0-c (entrada de estoque) tem menos de 1 KiB; o limite dele não muda. */
export const LIMITE_CORPO_BYTES = 16 * 1024;

/**
 * Limite de bytes por comando, lido antes do parse (ADR 0004 §6). O documento de entrada vai até 50 linhas (contrato
 * CMD-15 §6.2): 64 KiB só para ele, sem aumentar o do comando legado.
 */
export const LIMITES_CORPO: Readonly<Record<Comando, number>> = {
  'estoque.registrar-entrada': LIMITE_CORPO_BYTES,
  'estoque.receber-documento': 64 * 1024,
};

/** Dados e alvo conferidos pelo comando: o conteúdo que entra no hash e o efeito; ou a recusa de contrato, sem gravar. */
type Preparo = { readonly data: unknown; readonly efeito: Efeito } | { readonly recusa: Response };

function prepararEntrada(pedido: PedidoComando, correlationId: string): Preparo {
  const dados = EsquemaDadosMovimento.safeParse(pedido.data);
  if (!dados.success || dados.data.movimento.tipo !== 'entrada') {
    return {
      recusa: erro('CONTRATO_INVALIDO', 'Este comando só aceita uma entrada de estoque.', correlationId),
    };
  }
  // B1-C01: o alvo é o próprio lote da entrada. Tipo de outra entidade ou outro ID é recusa de contrato, antes do
  // envelope: nada é gravado, e recibo e auditoria nunca levam o tipo errado.
  if (pedido.target.type !== 'lot' || pedido.target.id !== dados.data.lote) {
    return {
      recusa: erro('CONTRATO_INVALIDO', 'O alvo da entrada tem de ser o lote informado.', correlationId),
    };
  }
  return { data: pedido.data, efeito: registrarMovimento(pedidoDeMovimento(dados.data)) };
}

/**
 * Documento de entrada (CMD-15; contrato §6.2): o alvo é o documento novo (versão 0) e os dados passam pelo esquema
 * estrito; a forma canônica vai para o hash e para o efeito ("10" e "10.0" são o mesmo conteúdo).
 */
function prepararRecebimento(pedido: PedidoComando, correlationId: string): Preparo {
  if (pedido.target.type !== 'receipt_document' || pedido.target.expectedVersion !== 0) {
    return {
      recusa: erro(
        'CONTRATO_INVALIDO',
        'O alvo do recebimento é um documento novo, na versão 0.',
        correlationId,
      ),
    };
  }
  const dados = EsquemaDadosRecebimento.safeParse(pedido.data);
  if (!dados.success) {
    const { status, corpo } = erroDeValidacao(dados.error, correlationId);
    return { recusa: json(status, corpo, { 'x-correlation-id': correlationId }) };
  }
  const canonico = canonizarRecebimento(dados.data);
  return { data: canonico, efeito: receberDocumento(canonico) };
}

const PREPARO: Readonly<Record<Comando, (pedido: PedidoComando, correlationId: string) => Preparo>> = {
  'estoque.registrar-entrada': prepararEntrada,
  'estoque.receber-documento': prepararRecebimento,
};

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
        bruto = JSON.parse(await lerCorpoLimitado(requisicao, LIMITES_CORPO[commandType]));
      } catch (e) {
        if (e instanceof ErroRequisicao) throw e;
        return erro('CONTRATO_INVALIDO', 'O corpo não é JSON válido.', correlationId);
      }
      const pedido = EsquemaPedidoComando.safeParse(bruto);
      if (!pedido.success) {
        const { status, corpo } = erroDeValidacao(pedido.error, correlationId);
        return json(status, corpo);
      }
      const preparo = PREPARO[commandType](pedido.data, correlationId);
      if ('recusa' in preparo) return preparo.recusa;
      const recibo = await executarComando(
        banco,
        sessao.organizationId,
        {
          commandType,
          idempotencyKey: pedido.data.idempotencyKey,
          initiatorKind: 'web',
          actorId: sessao.usuarioId,
          target: pedido.data.target,
          data: preparo.data,
          correlationId,
          ...(pedido.data.confirmedAt ? { confirmedAt: pedido.data.confirmedAt } : {}),
          ...(pedido.data.deviceId ? { deviceId: pedido.data.deviceId } : {}),
        },
        preparo.efeito,
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
