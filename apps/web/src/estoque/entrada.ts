import { decimalDoCampo } from '../formato/numero';
import { SITUACOES_DE_ENTRADA } from './estado';

/**
 * Registrar entrada no lote (comando estoque.registrar-entrada da F0-c): validação do formulário, corpo do pedido e
 * leitura da resposta. Puro, para o teste cobrir cada caminho; o componente só liga isto à tela.
 */
export interface CamposEntrada {
  readonly quantidade: string;
  readonly unidade: string;
  readonly situacao: string;
  readonly local: string;
}

export type CampoEntrada = keyof CamposEntrada;
export type ErrosEntrada = Partial<Record<CampoEntrada, string>>;

export interface DadosEntrada {
  readonly quantidade: string;
  readonly unidade: string;
  readonly situacao: (typeof SITUACOES_DE_ENTRADA)[number];
  readonly local: string;
}

export function validarEntrada(
  campos: CamposEntrada,
  unidades: readonly string[],
  locais: readonly string[],
):
  { readonly ok: true; readonly dados: DadosEntrada } | { readonly ok: false; readonly erros: ErrosEntrada } {
  const erros: ErrosEntrada = {};
  const q = decimalDoCampo(campos.quantidade);
  if (!q.ok) erros.quantidade = q.erro;
  if (!unidades.includes(campos.unidade)) erros.unidade = 'Escolha a unidade.';
  const situacao = SITUACOES_DE_ENTRADA.find((s) => s === campos.situacao);
  if (!situacao) erros.situacao = 'Escolha se a entrada vai para inspeção ou já está liberada.';
  if (!locais.includes(campos.local)) erros.local = 'Escolha o local.';
  if (!q.ok || !situacao || Object.keys(erros).length > 0) return { ok: false, erros };
  return { ok: true, dados: { quantidade: q.valor, unidade: campos.unidade, situacao, local: campos.local } };
}

/** Corpo do comando: a organização e o ator vêm da sessão no servidor, nunca daqui. */
export function pedidoDeEntrada(
  lote: { readonly id: string; readonly versao: number },
  dados: DadosEntrada,
  chave: string,
) {
  return {
    idempotencyKey: chave,
    target: { type: 'lot', id: lote.id, expectedVersion: lote.versao },
    data: {
      lote: lote.id,
      local: dados.local,
      movimento: {
        tipo: 'entrada',
        quantidade: { valor: dados.quantidade, unidade: dados.unidade },
        situacao: dados.situacao,
      },
    },
  };
}

export type Desfecho =
  | { readonly tipo: 'confirmado' }
  | { readonly tipo: 'conflito'; readonly mensagem: string }
  | { readonly tipo: 'recusado'; readonly mensagem: string; readonly campo?: CampoEntrada }
  | { readonly tipo: 'sessao'; readonly mensagem: string }
  | { readonly tipo: 'falha'; readonly mensagem: string };

const MOTIVOS: Readonly<Record<string, { readonly mensagem: string; readonly campo?: CampoEntrada }>> = {
  UNIDADE_INCOMPATIVEL: { mensagem: 'Esta unidade não serve para o produto do lote.', campo: 'unidade' },
  UNIDADE_DESCONHECIDA: { mensagem: 'Escolha uma unidade da lista.', campo: 'unidade' },
  QUANTIDADE_INVALIDA: { mensagem: 'Informe uma quantidade maior que zero.', campo: 'quantidade' },
  DECIMAL_INVALIDO: {
    mensagem: 'Use só números, com vírgula para decimais. Exemplo: 12,5',
    campo: 'quantidade',
  },
  QUANTIDADE_FORA_DA_ESCALA: {
    mensagem: 'A quantidade tem casas decimais demais para esta unidade.',
    campo: 'quantidade',
  },
  LOCAL_NAO_ENCONTRADO: { mensagem: 'Este local não existe mais. Recarregue a página.', campo: 'local' },
  LOTE_NAO_ENCONTRADO: { mensagem: 'Este lote não está mais disponível.' },
};

function codigo(corpo: unknown, campo: 'reasonCode' | 'codigo'): string | null {
  if (typeof corpo !== 'object' || corpo === null) return null;
  const v = (corpo as Record<string, unknown>)[campo];
  return typeof v === 'string' ? v : null;
}

/**
 * Resposta do servidor para o que a tela mostra. Recibo confirmado (200) e reenvio já recebido são sucesso; conflito de
 * versão (409) pede conferir os dados atualizados; rejeição registrada (422) diz o motivo; 401 volta ao login; o resto é
 * falha com os dados mantidos no formulário.
 */
export function desfechoDaResposta(status: number, corpo: unknown): Desfecho {
  const resultado = codigo(corpo, 'reasonCode');
  if (status === 200 && (corpo as { outcome?: unknown } | null)?.outcome === 'confirmed')
    return { tipo: 'confirmado' };
  if (status === 409) {
    return {
      tipo: 'conflito',
      mensagem: 'O lote mudou enquanto você registrava. Confira o saldo atualizado e registre de novo.',
    };
  }
  if (status === 422) {
    const motivo = resultado !== null && Object.hasOwn(MOTIVOS, resultado) ? MOTIVOS[resultado] : undefined;
    return motivo
      ? { tipo: 'recusado', ...motivo }
      : { tipo: 'recusado', mensagem: 'A entrada foi recusada. Confira os dados e tente de novo.' };
  }
  if (status === 401)
    return { tipo: 'sessao', mensagem: 'Sua sessão terminou. Entre de novo para registrar.' };
  if (status === 403) return { tipo: 'falha', mensagem: 'Seu papel não permite registrar entrada.' };
  if (status === 400 || status === 413 || status === 415) {
    return { tipo: 'falha', mensagem: 'O pedido não foi aceito. Recarregue a página e tente de novo.' };
  }
  return {
    tipo: 'falha',
    mensagem: 'O servidor não respondeu como esperado. Seus dados continuam aqui; tente de novo.',
  };
}
