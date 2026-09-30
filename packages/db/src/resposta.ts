import { erroContrato, erroDeValidacao, type CodigoErro, type ErroContrato } from '@safrion/contracts';
import { ErroDominio } from '@safrion/domain';
import { ZodError } from 'zod';

import { ErroComando, type CodigoErroComando } from './erros.js';

/** Cada código do envelope tem destino no contrato; o compilador recusa código sem destino. */
const DESTINO: Readonly<Record<CodigoErroComando, CodigoErro>> = {
  CONTRATO_INVALIDO: 'CONTRATO_INVALIDO',
  ORGANIZACAO_INVALIDA: 'ORGANIZACAO_INVALIDA',
  IDEMPOTENCY_KEY_REUSED: 'IDEMPOTENCY_KEY_REUSED',
  IDEMPOTENCY_IN_PROGRESS: 'IDEMPOTENCY_IN_PROGRESS',
  FALHA_TRANSITORIA: 'FALHA_TRANSITORIA',
  MIGRACAO_ALTERADA: 'FALHA_INTERNA',
};

/**
 * Só estes detalhes do envelope saem para o cliente. O erro original fica em `cause`, fora de resposta e de log; o
 * log leva só códigos seguros (ENG-015; ENG-081; F0B2-01).
 */
const DETALHE_PUBLICO: Readonly<Partial<Record<CodigoErroComando, readonly string[]>>> = {
  IDEMPOTENCY_KEY_REUSED: ['receiptId'],
  IDEMPOTENCY_IN_PROGRESS: ['repetirEmMs'],
  FALHA_TRANSITORIA: ['resultadoIncerto', 'repetirEmMs'],
};

/**
 * Converte qualquer erro na resposta do contrato. Erro inesperado vira FALHA_INTERNA com mensagem genérica: o detalhe
 * vai para o log com a mesma correlação, nunca para o cliente.
 */
export function respostaDeErro(
  erro: unknown,
  correlationId: string,
): { status: number; corpo: ErroContrato } {
  if (erro instanceof ZodError) return erroDeValidacao(erro, correlationId);
  if (erro instanceof ErroDominio) {
    return erroContrato('CONTRATO_INVALIDO', 'O conteúdo do comando não é válido.', correlationId, {
      campos: [{ caminho: 'data', problema: erro.codigo }],
    });
  }
  if (erro instanceof ErroComando) {
    const destino = DESTINO[erro.codigo];
    if (destino === 'FALHA_INTERNA') {
      return erroContrato(
        'FALHA_INTERNA',
        'Erro inesperado; use esta correlação ao falar com o suporte.',
        correlationId,
      );
    }
    const permitidos = DETALHE_PUBLICO[erro.codigo] ?? [];
    const detalhe = Object.fromEntries(Object.entries(erro.detalhe).filter(([k]) => permitidos.includes(k)));
    const campos = Array.isArray(erro.detalhe['campos'])
      ? (erro.detalhe['campos'] as unknown[]).map((c) => ({ caminho: String(c), problema: 'invalido' }))
      : undefined;
    return erroContrato(destino, erro.message, correlationId, {
      ...(Object.keys(detalhe).length > 0 ? { detalhe } : {}),
      ...(campos ? { campos } : {}),
    });
  }
  return erroContrato(
    'FALHA_INTERNA',
    'Erro inesperado; use esta correlação ao falar com o suporte.',
    correlationId,
  );
}
