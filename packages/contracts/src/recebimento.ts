import {
  ErroDominio,
  MOTIVOS,
  dataCivil,
  decimal,
  identidadeDaOrigem,
  type MotivoDivergencia,
} from '@safrion/domain';
import { z } from 'zod';

import { EsquemaUuid } from './comando.js';
import { EsquemaDecimalTexto, EsquemaUnidade } from './quantidade.js';

/**
 * Dados do comando estoque.receber-documento (CMD-15; contrato CMD-15 v3.3). O documento é o alvo do envelope
 * (target.type = 'receipt_document', target.id = id do documento, versão esperada 0); aqui vêm a origem, a fazenda e as
 * linhas conferidas. Organização e ator vêm da sessão, nunca do corpo (ENG-021).
 */
const texto = (max: number) =>
  z
    .string()
    .max(max)
    .refine((v) => v.trim() !== '', { message: 'vazio' });

/** Data civil AAAA-MM-DD, pela mesma regra do domínio. */
const EsquemaDataCivil = z.string().superRefine((valor, ctx) => {
  try {
    dataCivil(valor);
  } catch (erro) {
    if (!(erro instanceof ErroDominio)) throw erro;
    ctx.addIssue({ code: 'custom', message: erro.codigo });
  }
});

const EsquemaUnidadeDaLinha = z.discriminatedUnion('tipo', [
  z.strictObject({ tipo: z.literal('medida'), unidade: EsquemaUnidade }),
  /** Embalagem pela conversão cadastrada do produto, na versão conferida (CD-06). */
  z.strictObject({
    tipo: z.literal('embalagem'),
    conversao: EsquemaUuid,
    versao: z.int().min(1).max(2147483647),
  }),
]);

/**
 * Valor unitário em BRL, na unidade do documento: o CHECK da 0007 guarda até 8 casas e nada negativo. A escala é contada
 * na forma canônica, a mesma que vai ao banco ("1.123456780" tem 8). Fora disso é recusa de contrato (400), nunca uma
 * violação de CHECK no efeito, que viraria falha transitória (contrato CMD-15 §6.2, v3.8).
 */
const EsquemaValorUnitario = EsquemaDecimalTexto.superRefine((valor, ctx) => {
  let d;
  try {
    d = decimal(valor);
  } catch {
    return; // o formato já foi recusado pelo esquema decimal
  }
  if (d.isNegative()) ctx.addIssue({ code: 'custom', message: 'VALOR_UNITARIO_NEGATIVO' });
  else if (d.decimalPlaces() > 8)
    ctx.addIssue({ code: 'custom', message: 'VALOR_UNITARIO_ACIMA_DE_8_CASAS' });
});

const EsquemaParcelas = z.strictObject({
  apto: EsquemaDecimalTexto,
  quarentena: EsquemaDecimalTexto,
  bloqueado: EsquemaDecimalTexto,
  recusado: EsquemaDecimalTexto,
});

/** Produto diferente do documento (SUBST-14): ocorrência de chegada, não estoque. */
const EsquemaOcorrencia = z.strictObject({
  produtoReal: z.union([z.strictObject({ produto: EsquemaUuid }), z.strictObject({ descricao: texto(160) })]),
  quantidade: EsquemaDecimalTexto,
  unidade: texto(40),
  destino: z.enum(['retido_para_decisao', 'devolvido_na_entrega']),
  responsavel: EsquemaUuid,
  prazo: EsquemaDataCivil.optional(),
});

const EsquemaLinha = z.strictObject({
  numero: z.int().min(1).max(50),
  produto: EsquemaUuid,
  /** Lote do fabricante informado, ou lote interno por documento (granel, produto "por documento"). */
  lote: z.union([z.strictObject({ codigo: texto(64) }), z.strictObject({ interno: z.literal(true) })]),
  /** null = "não se aplica"; nunca data fictícia (RN-032). */
  validade: EsquemaDataCivil.nullable(),
  local: EsquemaUuid,
  unidade: EsquemaUnidadeDaLinha,
  documento: EsquemaDecimalTexto,
  parcelas: EsquemaParcelas,
  motivo: z.enum(MOTIVOS as unknown as [MotivoDivergencia, ...MotivoDivergencia[]]).optional(),
  motivoTexto: texto(200).optional(),
  inspecao: z.strictObject({ responsavel: EsquemaUuid, prazo: EsquemaDataCivil }).optional(),
  pedidoLinha: texto(64).optional(),
  valorUnitario: EsquemaValorUnitario.optional(),
  ocorrencia: EsquemaOcorrencia.optional(),
});

export const EsquemaDadosRecebimento = z.strictObject({
  emitente: EsquemaUuid,
  tipo: z.enum(['nfe', 'outro']),
  serie: z.string().max(16),
  numero: texto(40),
  emissao: EsquemaDataCivil,
  recebimento: EsquemaDataCivil,
  fazenda: EsquemaUuid,
  pedido: z.strictObject({ sistema: texto(40), referencia: texto(64) }).optional(),
  linhas: z.array(EsquemaLinha).min(1).max(50),
});
export type DadosRecebimento = z.infer<typeof EsquemaDadosRecebimento>;

const canonico = (v: string) => decimal(v).toString();

/**
 * Forma canônica para o hash da intenção (IDEM-13), aplicada pela rota antes do envelope: decimais sem zero à direita
 * ("10.0" e "10" são o mesmo conteúdo), série e número normalizados como a identidade da origem, linhas em ordem de
 * número. Outra unidade continua outro conteúdo.
 */
export function canonizarRecebimento(d: DadosRecebimento): DadosRecebimento {
  const origem = identidadeDaOrigem({ tipo: d.tipo, serie: d.serie, numero: d.numero });
  return {
    ...d,
    serie: origem.serie,
    numero: origem.numero,
    linhas: [...d.linhas]
      .sort((a, b) => a.numero - b.numero)
      .map((l) => ({
        ...l,
        documento: canonico(l.documento),
        parcelas: {
          apto: canonico(l.parcelas.apto),
          quarentena: canonico(l.parcelas.quarentena),
          bloqueado: canonico(l.parcelas.bloqueado),
          recusado: canonico(l.parcelas.recusado),
        },
        ...(l.valorUnitario === undefined ? {} : { valorUnitario: canonico(l.valorUnitario) }),
        ...(l.ocorrencia === undefined
          ? {}
          : { ocorrencia: { ...l.ocorrencia, quantidade: canonico(l.ocorrencia.quantidade) } }),
      })),
  };
}
