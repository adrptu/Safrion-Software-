/**
 * Motivo de volta ao /entrar, pelo código que a rota põe na URL (nunca texto livre da requisição). Código desconhecido
 * não aparece: a tela mostra a mensagem genérica, sem ecoar o parâmetro.
 */
const MENSAGENS: ReadonlyMap<string, string> = new Map(
  Object.entries({
    LOGIN_INDISPONIVEL: 'O acesso está indisponível neste ambiente. Avise o responsável pelo sistema.',
    TICKET_AUSENTE_OU_USADO: 'O tempo para entrar terminou. Entre de novo.',
    STATE_DIVERGENTE: 'Não foi possível confirmar o acesso. Entre de novo.',
    RESPOSTA_INVALIDA: 'Não foi possível confirmar o acesso. Entre de novo.',
    NEGADO_NO_PROVEDOR: 'O acesso foi cancelado. Entre de novo quando quiser.',
    TOKEN_INVALIDO: 'Não foi possível confirmar o acesso. Entre de novo.',
    PROVEDOR_INDISPONIVEL: 'O serviço de acesso não respondeu. Tente de novo em alguns minutos.',
    SEM_VINCULO: 'Sua conta ainda não tem acesso a nenhuma organização. Peça acesso ao gestor.',
    VINCULO_AUSENTE: 'Esse acesso não está mais disponível para a sua conta. Entre de novo.',
    CONTINUACAO_INVALIDA: 'O tempo para escolher o acesso terminou. Entre de novo.',
    SEM_PERMISSAO: 'O pedido veio de outra origem e foi recusado. Entre de novo por esta página.',
    CONTRATO_INVALIDO: 'Não foi possível confirmar o acesso. Entre de novo.',
    TIPO_DE_CONTEUDO_INVALIDO: 'Não foi possível confirmar o acesso. Entre de novo.',
    CORPO_EXCEDE_LIMITE: 'Não foi possível confirmar o acesso. Entre de novo.',
    FALHA_INTERNA: 'Algo falhou do nosso lado. Tente de novo em alguns minutos.',
  }),
);

export const MENSAGEM_GENERICA = 'Não foi possível entrar. Tente de novo.';

export function mensagemDeLogin(codigo: string | undefined): string | null {
  if (codigo === undefined || codigo === '') return null;
  return MENSAGENS.get(codigo) ?? MENSAGEM_GENERICA;
}
