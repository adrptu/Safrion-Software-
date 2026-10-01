import { z } from 'zod';

import { EsquemaQuantidade, EsquemaSituacao } from './quantidade.js';

/**
 * Texto do envelope que vai para o PostgreSQL. O banco recusa U+0000 em texto (22021); aqui isso é recusa de contrato
 * (400), antes de qualquer acesso, e nunca remoção silenciosa (ENV-CAD01-NUL-CL22).
 */
const texto = (max: number) =>
  z
    .string()
    .max(max)
    .refine((v) => v.trim() !== '', { message: 'vazio' })
    .refine((v) => !v.includes('\u0000'), { message: 'NUL' });
/** UUID canônico em minúsculas, a mesma regra do envelope (@safrion/db ehUuid). */
export const EsquemaUuid = z
  .string()
  .regex(/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/, 'uuid_canonico');
const uuid = EsquemaUuid;

/**
 * Instante informado pelo iniciador, ISO 8601 com fuso: dado, não autoridade (73.3.5). O envelope (@safrion/db
 * validarIntencao) usa este mesmo esquema. O ano 0000, o deslocamento de 16 h ou mais e a fração de segundo muito longa
 * cabem no formato, mas o PostgreSQL os recusa (22008, 22009 e 22007): aqui são recusa de contrato, antes de qualquer
 * acesso (ENV-CAD01-NUL-CL22). A fração vai até 9 casas; o banco guarda microssegundos.
 */
export const EsquemaInstanteConfirmado = z.iso
  .datetime({ offset: true })
  .refine((v) => !v.startsWith('0000'), { message: 'ano_zero' })
  .refine((v) => !/[+-](1[6-9]|2[0-3]):[0-5]\d$/.test(v), { message: 'fuso_fora_da_faixa' })
  .refine((v) => !/\.\d{10,}/.test(v), { message: 'fracao_longa' });

/**
 * O que o cliente envia num comando (8.2.1; 73.3). Organização, ator e tipo de iniciador NÃO vêm aqui: vêm da sessão ou
 * da credencial validada (ENG-021). O esquema é estrito: um campo a mais, como organizationId, é recusa de contrato, e
 * trocar a organização no corpo não amplia acesso.
 */
export const EsquemaPedidoComando = z.strictObject({
  idempotencyKey: texto(128),
  target: z.strictObject({
    type: texto(64),
    id: uuid,
    expectedVersion: z.int().min(0).max(Number.MAX_SAFE_INTEGER),
  }),
  data: z.unknown(),
  confirmedAt: EsquemaInstanteConfirmado.optional(),
  deviceId: texto(128).optional(),
});
export type PedidoComando = z.infer<typeof EsquemaPedidoComando>;

/** Dados do comando de movimento de estoque (F0-b), já com quantidade em texto e unidade explícita. */
export const EsquemaDadosMovimento = z.strictObject({
  lote: uuid,
  local: uuid,
  movimento: z.discriminatedUnion('tipo', [
    z.strictObject({ tipo: z.literal('entrada'), quantidade: EsquemaQuantidade, situacao: EsquemaSituacao }),
    z.strictObject({
      tipo: z.literal('mudanca'),
      quantidade: EsquemaQuantidade,
      de: EsquemaSituacao,
      para: EsquemaSituacao,
    }),
    z.strictObject({ tipo: z.literal('estorno'), estornaId: uuid }),
  ]),
});
export type DadosMovimento = z.infer<typeof EsquemaDadosMovimento>;

/** Recibo imutável (IDEM-17), igual no original e no reenvio, exceto alreadyReceived. */
export const EsquemaRecibo = z.strictObject({
  receiptId: uuid,
  commandType: texto(64),
  idempotencyKey: texto(128),
  outcome: z.enum(['confirmed', 'rejected', 'version_conflict']),
  reasonCode: z.string().nullable(),
  targetType: texto(64),
  targetId: uuid,
  expectedVersion: z.int().min(0).nullable(),
  resultingVersion: z.int().min(0).nullable(),
  effects: z.record(z.string(), z.array(z.string())),
  pending: z.array(z.string()),
  nextAction: z.string().nullable(),
  processedAt: z.iso.datetime({ offset: true }),
  alreadyReceived: z.boolean(),
});
export type ReciboContrato = z.infer<typeof EsquemaRecibo>;

/** Status HTTP do recibo: rejeição de negócio e conflito de versão são resultados registrados, não falhas. */
export function statusDoRecibo(outcome: ReciboContrato['outcome']): 200 | 409 | 422 {
  return outcome === 'confirmed' ? 200 : outcome === 'version_conflict' ? 409 : 422;
}

/** Resposta de /saude (plano R-006, passo 8): sem endereço do banco, usuário ou detalhe de erro do driver. */
export const EsquemaSaude = z.strictObject({
  status: z.enum(['ok', 'sem_identidade', 'indisponivel']),
  ambiente: z.enum(['dev', 'hml', 'prod']).nullable(),
  versao: z.string().min(1),
  commit: z.string().min(1),
  migracao: z.string().nullable(),
  verificadoEm: z.iso.datetime({ offset: true }),
});
export type SaudeContrato = z.infer<typeof EsquemaSaude>;
