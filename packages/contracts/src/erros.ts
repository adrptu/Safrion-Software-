import { z } from 'zod';

/**
 * Contrato de erro (ENG-015): código estável, classe, mensagem útil e correlação. A classe distingue o que o usuário
 * corrige (validação), o que a sessão não permite (acesso), a situação do negócio (conflito) e a falha do sistema
 * (infraestrutura). Rejeição de negócio registrada não é erro: volta como recibo (73.3.4).
 */
export const ERROS = {
  CONTRATO_INVALIDO: { classe: 'validacao', status: 400 },
  CORPO_EXCEDE_LIMITE: { classe: 'validacao', status: 413 },
  TIPO_DE_CONTEUDO_INVALIDO: { classe: 'validacao', status: 415 },
  NAO_AUTENTICADO: { classe: 'acesso', status: 401 },
  ORGANIZACAO_INVALIDA: { classe: 'acesso', status: 401 },
  SEM_PERMISSAO: { classe: 'acesso', status: 403 },
  NAO_ENCONTRADO: { classe: 'acesso', status: 404 },
  IDEMPOTENCY_KEY_REUSED: { classe: 'conflito', status: 409 },
  IDEMPOTENCY_IN_PROGRESS: { classe: 'conflito', status: 409 },
  FALHA_TRANSITORIA: { classe: 'infraestrutura', status: 503 },
  FALHA_INTERNA: { classe: 'infraestrutura', status: 500 },
} as const;

export type CodigoErro = keyof typeof ERROS;
export type ClasseErro = (typeof ERROS)[CodigoErro]['classe'];

const CODIGOS = Object.keys(ERROS) as [CodigoErro, ...CodigoErro[]];

export const EsquemaErro = z.strictObject({
  codigo: z.enum(CODIGOS),
  classe: z.enum(['validacao', 'acesso', 'conflito', 'infraestrutura']),
  mensagem: z.string().min(1),
  correlationId: z.string().min(1),
  detalhe: z.record(z.string(), z.unknown()).optional(),
  campos: z.array(z.strictObject({ caminho: z.string(), problema: z.string() })).optional(),
});
export type ErroContrato = z.infer<typeof EsquemaErro>;

export function erroContrato(
  codigo: CodigoErro,
  mensagem: string,
  correlationId: string,
  extra: { detalhe?: Record<string, unknown>; campos?: { caminho: string; problema: string }[] } = {},
): { status: number; corpo: ErroContrato } {
  const { classe, status } = ERROS[codigo];
  return { status, corpo: { codigo, classe, mensagem, correlationId, ...extra } };
}

/**
 * Recusa de contrato a partir da validação: diz o caminho e o problema de cada campo, sem ecoar o valor recebido
 * (pode ser dado pessoal ou segredo colado por engano).
 */
export function erroDeValidacao(
  erro: z.ZodError,
  correlationId: string,
): { status: number; corpo: ErroContrato } {
  const campos = erro.issues.map((i) => ({
    caminho: i.path.map(String).join('.') || '(raiz)',
    problema: i.code === 'custom' ? i.message : i.code,
  }));
  return erroContrato(
    'CONTRATO_INVALIDO',
    'O pedido não segue o contrato; corrija os campos indicados.',
    correlationId,
    {
      campos,
    },
  );
}
