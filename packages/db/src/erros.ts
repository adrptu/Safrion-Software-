/**
 * Erros do envelope de comando (73.3.4). Rejeição de negócio e conflito de versão não são erros para quem chama:
 * viram recibo com o resultado registrado. Os códigos abaixo não gravam nada.
 */
export type CodigoErroComando =
  | 'CONTRATO_INVALIDO' // chave ausente ou esquema inválido: defeito do cliente
  | 'ORGANIZACAO_INVALIDA'
  | 'IDEMPOTENCY_KEY_REUSED' // mesma chave com outro conteúdo (IDEM-14)
  | 'IDEMPOTENCY_IN_PROGRESS' // mesma chave com transação em curso além do limite (IDEM-15)
  | 'FALHA_TRANSITORIA' // repetir com a mesma chave e o mesmo conteúdo
  | 'MIGRACAO_ALTERADA';

export class ErroComando extends Error {
  override readonly name = 'ErroComando';
  constructor(
    readonly codigo: CodigoErroComando,
    mensagem: string,
    readonly detalhe: Readonly<Record<string, unknown>> = {},
  ) {
    super(mensagem);
  }
}

/** Lançada pelo efeito: rejeição de negócio registrada com a chave, sem efeito (73.3.4). */
export class RejeicaoNegocio extends Error {
  override readonly name = 'RejeicaoNegocio';
  constructor(
    readonly motivo: string,
    mensagem: string,
    readonly proximaAcao: string | null = null,
  ) {
    super(mensagem);
  }
}

/** Lançada pelo efeito quando a versão esperada não é a atual (ENG-021); registrada sem efeito. */
export class ConflitoVersao extends Error {
  override readonly name = 'ConflitoVersao';
  constructor(readonly versaoAtual: number) {
    super(`A versão atual é ${String(versaoAtual)}; revise as diferenças antes de repetir.`);
  }
}
