import {
  ALVOS_CADASTRO,
  COMANDOS_CADASTRO,
  ERROS,
  EsquemaErro,
  EsquemaPedidoComando,
  EsquemaRecibo,
  statusDoRecibo,
  type ComandoCadastro,
  type ErroContrato,
  type ReciboContrato,
} from '@safrion/contracts';

/** O corpo fica congelado em texto: reenviar preserva alvo, versão, dados e chave. */
export interface Intencao {
  readonly commandType: ComandoCadastro;
  readonly chave: string;
  readonly targetType: 'farm' | 'field';
  readonly targetId: string;
  readonly expectedVersion: number;
  readonly corpo: string;
}

/** Reabre apenas intenções CAD01 cujo envelope e metadados coincidem. Não executa nem revalida regras de negócio. */
export function intencaoValida(valor: unknown): valor is Intencao {
  if (typeof valor !== 'object' || valor === null) return false;
  const i = valor as Record<string, unknown>;
  const comando = i['commandType'];
  if (typeof comando !== 'string' || !Object.hasOwn(ALVOS_CADASTRO, comando)) return false;
  const alvo = ALVOS_CADASTRO[comando as ComandoCadastro];
  const criacao = comando === COMANDOS_CADASTRO.criarFazenda || comando === COMANDOS_CADASTRO.criarTalhao;
  if (i['targetType'] !== alvo || typeof i['corpo'] !== 'string') return false;
  // O mesmo teto de corpo dos comandos CAD01 Inc1; dados grandes/corrompidos nunca são restaurados para envio.
  if (new TextEncoder().encode(i['corpo']).length > 16 * 1024) return false;
  try {
    const bruto: unknown = JSON.parse(i['corpo']);
    const p = EsquemaPedidoComando.safeParse(bruto);
    return (
      p.success &&
      p.data.idempotencyKey === i['chave'] &&
      p.data.target.type === i['targetType'] &&
      p.data.target.id === i['targetId'] &&
      p.data.target.expectedVersion === i['expectedVersion'] &&
      (criacao ? p.data.target.expectedVersion === 0 : p.data.target.expectedVersion >= 1)
    );
  } catch {
    return false;
  }
}

/** Os dados já vêm do esquema de cadastro correspondente, mantido em @safrion/contracts. */
export function novaIntencao(
  commandType: ComandoCadastro,
  targetType: Intencao['targetType'],
  targetId: string,
  expectedVersion: number,
  data: unknown,
  chave: string,
): Intencao {
  const pedido = EsquemaPedidoComando.parse({
    idempotencyKey: chave,
    target: { type: targetType, id: targetId, expectedVersion },
    data,
  });
  const intencao: Intencao = {
    commandType,
    chave,
    targetType,
    targetId,
    expectedVersion,
    corpo: JSON.stringify(pedido),
  };
  if (!intencaoValida(intencao)) throw new Error('Intenção de cadastro inválida.');
  return Object.freeze(intencao);
}

export type Desfecho =
  | { readonly tipo: 'resolvido'; readonly recibo: ReciboContrato }
  | { readonly tipo: 'nao_gravado'; readonly mensagem: string; readonly sessao: boolean }
  | {
      readonly tipo: 'incerto';
      readonly mensagem: string;
      readonly sessao: boolean;
      /** Habilita somente o reenvio do mesmo corpo e chave, nunca uma nova intenção. */
      readonly naoLocalizado: boolean;
    };

/** Um recibo válido de outra intenção ou versão não prova o resultado deste envio. */
export function reciboDaIntencao(corpo: unknown, intencao: Intencao): ReciboContrato | null {
  const r = EsquemaRecibo.safeParse(corpo);
  if (!r.success) return null;
  const x = r.data;
  return x.commandType === intencao.commandType &&
    x.idempotencyKey === intencao.chave &&
    x.targetType === intencao.targetType &&
    x.targetId === intencao.targetId &&
    x.expectedVersion === intencao.expectedVersion
    ? x
    : null;
}

function erroDaResposta(status: number, corpo: unknown): ErroContrato | null {
  const e = EsquemaErro.safeParse(corpo);
  if (!e.success) return null;
  const esperado = ERROS[e.data.codigo];
  return esperado.status === status && esperado.classe === e.data.classe ? e.data : null;
}

export const INCERTO =
  'Ainda não foi possível confirmar o resultado. Consulte o recibo antes de alterar ou enviar novamente.';
const SESSAO_INCERTA = 'Sua sessão terminou. Entre de novo para conferir o envio pendente.';
// Origem: revisão Gemini J3i9…; informar o impedimento não resolve o efeito de um envio anterior.
const SEM_PERMISSAO_INCERTA =
  'Seu papel não permite conferir ou reenviar este cadastro. O envio anterior continua sem confirmação. Solicite acesso ao gerente.';

function incerto(status: number, mensagem = INCERTO): Desfecho {
  return {
    tipo: 'incerto',
    mensagem: status === 401 ? SESSAO_INCERTA : mensagem,
    sessao: status === 401,
    naoLocalizado: false,
  };
}

/** Só a recusa validada de um primeiro envio libera uma nova intenção. Reenvios conservam a incerteza. */
export function desfechoDoEnvio(
  status: number,
  corpo: unknown,
  intencao: Intencao,
  reenvio: boolean,
): Desfecho {
  const recibo = reciboDaIntencao(corpo, intencao);
  if (recibo && status === statusDoRecibo(recibo.outcome)) return { tipo: 'resolvido', recibo };
  const erro = erroDaResposta(status, corpo);
  if (!reenvio && erro) {
    switch (erro.codigo) {
      case 'NAO_AUTENTICADO':
      case 'ORGANIZACAO_INVALIDA':
        return {
          tipo: 'nao_gravado',
          mensagem: 'Sua sessão terminou. Entre de novo e confirme o cadastro.',
          sessao: true,
        };
      case 'SEM_PERMISSAO':
        return {
          tipo: 'nao_gravado',
          mensagem: 'Seu papel não permite alterar este cadastro.',
          sessao: false,
        };
      case 'CONTRATO_INVALIDO':
      case 'CORPO_EXCEDE_LIMITE':
      case 'TIPO_DE_CONTEUDO_INVALIDO':
      case 'IDEMPOTENCY_KEY_REUSED':
        return {
          tipo: 'nao_gravado',
          mensagem: 'O servidor não aceitou o pedido. Confira os dados e confirme de novo.',
          sessao: false,
        };
    }
  }
  return incerto(status, erro?.codigo === 'SEM_PERMISSAO' ? SEM_PERMISSAO_INCERTA : INCERTO);
}

/** Ausência de recibo não prova ausência de efeito; só libera o mesmo reenvio (CMD-15 §6.2). */
export function desfechoDaConsulta(status: number, corpo: unknown, intencao: Intencao): Desfecho {
  const recibo = reciboDaIntencao(corpo, intencao);
  if (recibo && status === statusDoRecibo(recibo.outcome)) return { tipo: 'resolvido', recibo };
  const erro = erroDaResposta(status, corpo);
  if (erro?.codigo === 'SEM_PERMISSAO') return incerto(status, SEM_PERMISSAO_INCERTA);
  if (erro?.codigo === 'RECIBO_NAO_LOCALIZADO') {
    return {
      tipo: 'incerto',
      mensagem: 'Recibo ainda não localizado. Reenvie o mesmo pedido, sem alterar os dados.',
      sessao: false,
      naoLocalizado: true,
    };
  }
  return incerto(status, 'Não deu para consultar agora. Consulte o recibo de novo em instantes.');
}
