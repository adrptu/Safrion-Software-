import {
  ErroDominio,
  SITUACOES,
  UNIDADES,
  decimal,
  type CodigoUnidade,
  type Situacao,
} from '@safrion/domain';
import { z } from 'zod';

/**
 * Decimal em texto canônico (PRD 10.0; ENG-013), conferido pela mesma regra do domínio (ENG-011: regra num lugar só).
 * Número JSON é recusado: já chegaria como ponto flutuante binário.
 */
export const EsquemaDecimalTexto = z.string().superRefine((valor, ctx) => {
  try {
    decimal(valor);
  } catch (erro) {
    // Só a recusa do domínio vira problema de contrato; erro inesperado sobe (ENG-015: não engolir exceção).
    if (!(erro instanceof ErroDominio)) throw erro;
    ctx.addIssue({ code: 'custom', message: erro.codigo });
  }
});

const CODIGOS_UNIDADE = Object.keys(UNIDADES) as [CodigoUnidade, ...CodigoUnidade[]];
export const EsquemaUnidade = z.enum(CODIGOS_UNIDADE);

/** Toda quantidade tem valor em texto decimal e unidade (RN-033); não existe unidade implícita. */
export const EsquemaQuantidade = z.strictObject({
  valor: EsquemaDecimalTexto,
  unidade: EsquemaUnidade,
});

export const EsquemaSituacao = z.enum(SITUACOES as unknown as [Situacao, ...Situacao[]]);
