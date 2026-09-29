// Contrato entre o provedor de identidade e o resto da aplicação web (ADR 0004, §5 e §10). Só tipos: nenhuma
// implementação aqui. O adaptador OIDC (apps/web/src/identidade/oidc/*, autoria Codex) e o provedor de desenvolvimento
// implementam ProvedorIdentidade; a casca (autoria Claude) implementa ArmazemTransacaoLogin sobre a migração 0003, decide
// a organização pelos vínculos explícitos e cria a sessão. O provedor autentica, não autoriza: não escreve SQL, não
// escolhe organização e não cria sessão.

/** Identidade validada pelo provedor: issuer + subject (o `sub` do OIDC). O e-mail nunca identifica nem vincula. */
export interface IdentidadeValidada {
  readonly issuer: string;
  readonly subject: string;
}

/**
 * Caminho interno para onde voltar depois do login: começa com uma única "/", sem esquema, host, "//" nem "\". Só a
 * casca cria valores deste tipo, depois de validar; o provedor apenas o guarda e o devolve.
 */
export type CaminhoInterno = string & { readonly __caminhoInterno: unique symbol };

/** O que o adaptador guarda entre o início do login e o callback. Nada disto vai a log (ADR 0004, §7). */
export interface TransacaoLogin {
  readonly state: string;
  readonly nonce: string;
  readonly verificadorPkce: string;
  readonly destino: CaminhoInterno;
}

/**
 * Porta de armazenamento da transação de login, implementada pela casca sobre a migração 0003. `abrir` devolve um ticket
 * aleatório, que a casca põe num cookie HttpOnly de validade curta; `consumir` é atômico e devolve a transação uma única
 * vez: ticket inexistente, expirado ou já consumido devolve null.
 */
export interface ArmazemTransacaoLogin {
  abrir(transacao: TransacaoLogin): Promise<{ readonly ticket: string; readonly expiraEm: Date }>;
  consumir(ticket: string): Promise<TransacaoLogin | null>;
}

/** Motivo de falha do login, só como código: nenhuma mensagem do provedor, URL, code, nonce ou token (ADR 0004, §7). */
export type CodigoFalhaLogin =
  | 'TICKET_AUSENTE_OU_USADO' // sem cookie, expirado ou já consumido
  | 'RESPOSTA_INVALIDA' // parâmetros do callback ausentes ou malformados
  | 'STATE_DIVERGENTE'
  | 'NEGADO_NO_PROVEDOR' // o usuário cancelou ou o provedor devolveu erro
  | 'TOKEN_INVALIDO' // assinatura, issuer, audience, nonce ou expiração
  | 'PROVEDOR_INDISPONIVEL';

export type ResultadoLogin =
  | { readonly ok: true; readonly identidade: IdentidadeValidada; readonly destino: CaminhoInterno }
  | { readonly ok: false; readonly codigo: CodigoFalhaLogin };

/**
 * Provedor de identidade. Issuer, client id e URL de callback vêm da configuração confiável do adaptador, nunca de
 * parâmetro da requisição. Sair da aplicação revoga a sessão do Safrion (funções da casca); sair do provedor não faz
 * parte deste contrato.
 */
export interface ProvedorIdentidade {
  readonly nome: 'oidc' | 'desenvolvimento';
  /** Abre a transação pelo armazém e devolve a URL do provedor e o ticket, que a casca põe no cookie. */
  iniciar(
    destino: CaminhoInterno,
  ): Promise<{ readonly redirecionarPara: URL; readonly ticket: string; readonly expiraEm: Date }>;
  /** Trata o callback: consome o ticket e valida o protocolo; devolve só a identidade e o destino guardado. */
  concluir(callback: {
    readonly ticket: string | undefined;
    readonly parametros: URLSearchParams;
  }): Promise<ResultadoLogin>;
}
