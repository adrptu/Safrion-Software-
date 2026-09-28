/** Códigos estáveis de erro do domínio (ENG-015): a mensagem pode mudar, o código não. */
export type CodigoErroDominio =
  | 'NUMERO_BINARIO_RECUSADO'
  | 'DECIMAL_INVALIDO'
  | 'UNIDADE_DESCONHECIDA'
  | 'UNIDADE_INCOMPATIVEL'
  | 'CONVERSAO_INVALIDA'
  | 'QUANTIDADE_INVALIDA'
  | 'QUANTIDADE_FORA_DA_ESCALA'
  | 'SALDO_INSUFICIENTE'
  | 'MOVIMENTO_INVALIDO'
  | 'LOTE_INVALIDO'
  | 'MOVIMENTO_CONFLITANTE'
  | 'ESTORNO_INVALIDO'
  | 'DATA_INVALIDA';

export class ErroDominio extends Error {
  constructor(
    readonly codigo: CodigoErroDominio,
    mensagem: string,
  ) {
    super(mensagem);
    this.name = 'ErroDominio';
  }
}
