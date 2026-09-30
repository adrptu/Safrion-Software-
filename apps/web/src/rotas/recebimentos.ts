import { erroContrato } from '@safrion/contracts';
import { documentoPorOrigem, emOrganizacao, resolverSessao, respostaDeErro } from '@safrion/db/web';
import { ErroDominio, identidadeDaOrigem } from '@safrion/domain';

import { podeExecutar } from '../autorizacao/matriz';
import { COOKIE_SESSAO, lerCookie } from '../seguranca/cookies';
import { correlacaoDe } from '../seguranca/requisicao';
import type { Dependencias } from '../servidor/ambiente';
import { deOutroSite } from './intencoes';
import { erro, json } from './resposta';

const PARAMETROS: readonly string[] = ['emitente', 'tipo', 'serie', 'numero'];
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

/**
 * GET /api/v1/recebimentos/origem?emitente&tipo&serie&numero (FO-18, "Duplicidade"; contrato CMD-15 §6.3): avisa, antes de
 * confirmar, que a NF desse emitente já entrou. Sem efeito e sem cache compartilhado. Organização e autor vêm da sessão;
 * a consulta aceita só os quatro campos da origem, uma vez cada. É ajuda de quem recebe (permissão de executar o
 * comando). Outra organização é igual a inexistente. O índice e o recibo continuam a autoridade.
 */
export function criarRotaOrigem(deps: () => Pick<Dependencias, 'banco' | 'origem'>) {
  return async function GET(requisicao: Request): Promise<Response> {
    const correlationId = correlacaoDe(requisicao);
    const { banco, origem } = deps();
    try {
      const busca = new URL(requisicao.url).searchParams;
      const chaves = [...busca.keys()];
      if (chaves.some((k) => !PARAMETROS.includes(k)) || new Set(chaves).size !== chaves.length) {
        return erro(
          'CONTRATO_INVALIDO',
          'A consulta aceita só emitente, tipo, série e número, uma vez cada.',
          correlationId,
        );
      }
      if (deOutroSite(requisicao, origem)) {
        return erro('SEM_PERMISSAO', 'Origem da requisição recusada.', correlationId);
      }
      const sessao = await resolverSessao(banco, lerCookie(requisicao, COOKIE_SESSAO));
      if (!sessao) return erro('NAO_AUTENTICADO', 'Entre de novo para continuar.', correlationId);
      if (!podeExecutar(sessao.papel, 'estoque.receber-documento')) {
        return erro('SEM_PERMISSAO', 'Seu papel não permite esta ação.', correlationId);
      }
      const pedido = {
        emitente: busca.get('emitente') ?? '',
        tipo: busca.get('tipo') ?? '',
        serie: busca.get('serie') ?? '',
        numero: busca.get('numero') ?? '',
      };
      const campos: { caminho: string; problema: string }[] = [];
      if (!UUID.test(pedido.emitente)) campos.push({ caminho: 'emitente', problema: 'UUID_INVALIDO' });
      try {
        identidadeDaOrigem({ tipo: pedido.tipo, serie: pedido.serie, numero: pedido.numero });
      } catch (e) {
        if (!(e instanceof ErroDominio)) throw e;
        campos.push({ caminho: 'tipo, serie, numero', problema: e.codigo });
      }
      if (campos.length > 0) {
        const { status, corpo } = erroContrato(
          'CONTRATO_INVALIDO',
          'A origem não segue o contrato; corrija os campos indicados.',
          correlationId,
          { campos },
        );
        return json(status, corpo, { 'x-correlation-id': correlationId });
      }
      const d = await emOrganizacao(banco, sessao.organizationId, (c) => documentoPorOrigem(c, pedido));
      const corpo = d
        ? {
            encontrado: true,
            documento: {
              id: d.id,
              tipo: d.tipo,
              serie: d.serie,
              numero: d.numero,
              emitente: { id: d.emitente.id, nome: d.emitente.nome },
              recebimento: d.recebimento,
              status: d.status,
            },
          }
        : { encontrado: false };
      return json(200, corpo, { 'x-correlation-id': correlationId });
    } catch (e) {
      const { status, corpo } = respostaDeErro(e, correlationId);
      return json(status, corpo, { 'x-correlation-id': correlationId });
    }
  };
}
