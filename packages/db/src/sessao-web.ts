import { createHash, randomBytes } from 'node:crypto';

import type { ClientBase, Pool } from 'pg';

import { ehUuid } from './sessao.js';

/**
 * Sessão da web e login em duas etapas (ADR 0004 rev. 2, §3 e §5; migração 0003). Cada função é uma chamada a uma função
 * SECURITY DEFINER do banco, atômica por si. O token sai daqui para o cookie e nunca vai ao banco: só o SHA-256 dele.
 * Token com formato inválido é tratado como inexistente, sem consulta.
 */
type Banco = ClientBase | Pool;

const FORMATO_TOKEN = /^[A-Za-z0-9_-]{43}$/;
const CODIGO_PAPEL = /^[a-z][a-z_]*$/;

/** SHA-256 do token do cookie, ou null se o formato não for o de um token gerado por novoToken. */
export function hashDoToken(token: string | undefined): Buffer | null {
  return token !== undefined && FORMATO_TOKEN.test(token)
    ? createHash('sha256').update(token).digest()
    : null;
}

/** 256 bits aleatórios em base64url (43 caracteres) e o hash que vai ao banco. */
export function novoToken(): { readonly token: string; readonly hash: Buffer } {
  const token = randomBytes(32).toString('base64url');
  return { token, hash: createHash('sha256').update(token).digest() };
}

export interface TransacaoLoginGuardada {
  readonly state: string;
  readonly nonce: string;
  readonly verificadorPkce: string;
  readonly destino: string;
}

export async function abrirTransacaoLogin(
  banco: Banco,
  transacao: TransacaoLoginGuardada,
  validadeSegundos = 600,
): Promise<{ readonly ticket: string; readonly expiraEm: Date }> {
  const { token, hash } = novoToken();
  const r = await banco.query<{ expira: Date }>(
    'SELECT app.abrir_transacao_login($1, $2, $3, $4, $5, $6) AS expira',
    [hash, transacao.state, transacao.nonce, transacao.verificadorPkce, transacao.destino, validadeSegundos],
  );
  return { ticket: token, expiraEm: primeira(r.rows).expira };
}

/** Uso único: devolve a transação uma vez só; ticket inexistente, vencido ou já usado devolve null. */
export async function consumirTransacaoLogin(
  banco: Banco,
  ticket: string | undefined,
): Promise<TransacaoLoginGuardada | null> {
  const hash = hashDoToken(ticket);
  if (!hash) return null;
  const r = await banco.query<{ state: string; nonce: string; verificador: string; destino: string }>(
    'SELECT state, nonce, verificador, destino FROM app.consumir_transacao_login($1)',
    [hash],
  );
  const l = r.rows[0];
  return l ? { state: l.state, nonce: l.nonce, verificadorPkce: l.verificador, destino: l.destino } : null;
}

/** Guarda no servidor a identidade validada pelo provedor e o destino; o ticket vai para o cookie do navegador. */
export async function abrirContinuacao(
  banco: Banco,
  identidade: { readonly issuer: string; readonly subject: string },
  destino: string,
  validadeSegundos = 600,
): Promise<{ readonly ticket: string; readonly expiraEm: Date }> {
  const { token, hash } = novoToken();
  const r = await banco.query<{ expira: Date }>(
    'SELECT app.abrir_continuacao($1, $2, $3, $4, $5) AS expira',
    [hash, identidade.issuer, identidade.subject, destino, validadeSegundos],
  );
  return { ticket: token, expiraEm: primeira(r.rows).expira };
}

export interface VinculoDisponivel {
  readonly organizationId: string;
  readonly organizacao: string;
  readonly papeis: readonly string[];
}

/** Organizações e papéis vivos da identidade guardada na continuação, sem consumi-la (tela de escolha). */
export async function vinculosDaContinuacao(
  banco: Banco,
  ticket: string | undefined,
): Promise<readonly VinculoDisponivel[]> {
  const hash = hashDoToken(ticket);
  if (!hash) return [];
  const r = await banco.query<{ organization_id: string; organization_name: string; role_code: string }>(
    'SELECT organization_id, organization_name, role_code FROM app.vinculos_da_continuacao($1)',
    [hash],
  );
  const porOrganizacao = new Map<string, { organizacao: string; papeis: string[] }>();
  for (const l of r.rows) {
    const atual = porOrganizacao.get(l.organization_id) ?? { organizacao: l.organization_name, papeis: [] };
    atual.papeis.push(l.role_code);
    porOrganizacao.set(l.organization_id, atual);
  }
  return [...porOrganizacao].map(([organizationId, v]) => ({ organizationId, ...v }));
}

export type ResultadoConclusao =
  | {
      readonly ok: true;
      readonly sessao: { readonly token: string; readonly expiraEm: Date };
      readonly usuarioId: string;
      readonly destino: string;
    }
  | { readonly ok: false; readonly codigo: 'CONTINUACAO_INVALIDA' | 'VINCULO_AUSENTE' };

/**
 * Único caminho que cria sessão: consome a continuação (uso único, também quando a escolha é recusada), revalida o
 * vínculo vivo e grava a sessão, numa transação. A escolha traz só organização e papel; a identidade está no servidor.
 */
export async function concluirContinuacao(
  banco: Banco,
  ticket: string | undefined,
  escolha: { readonly organizationId: string; readonly papel: string },
  validadeSegundos = 43200,
): Promise<ResultadoConclusao> {
  const hash = hashDoToken(ticket);
  if (!hash) return { ok: false, codigo: 'CONTINUACAO_INVALIDA' };
  // Escolha malformada não chega ao banco como texto livre; a continuação continua intacta para nova tentativa válida.
  if (!ehUuid(escolha.organizationId) || !CODIGO_PAPEL.test(escolha.papel)) {
    return { ok: false, codigo: 'VINCULO_AUSENTE' };
  }
  const sessao = novoToken();
  const r = await banco.query<{
    resultado: string;
    user_id: string | null;
    destino: string | null;
    expira_em: Date | null;
  }>('SELECT resultado, user_id, destino, expira_em FROM app.concluir_continuacao($1, $2, $3, $4, $5)', [
    hash,
    escolha.organizationId,
    escolha.papel,
    sessao.hash,
    validadeSegundos,
  ]);
  const l = primeira(r.rows);
  if (l.resultado === 'SESSAO_CRIADA' && l.user_id && l.destino && l.expira_em) {
    return {
      ok: true,
      sessao: { token: sessao.token, expiraEm: l.expira_em },
      usuarioId: l.user_id,
      destino: l.destino,
    };
  }
  return {
    ok: false,
    codigo: l.resultado === 'VINCULO_AUSENTE' ? 'VINCULO_AUSENTE' : 'CONTINUACAO_INVALIDA',
  };
}

export interface SessaoResolvida {
  readonly usuarioId: string;
  readonly organizationId: string;
  readonly papel: string;
  readonly expiraEm: Date;
}

/** Sessão válida com vínculo vivo, ou null. Não fixa organização na conexão: isso é de emOrganizacao, depois. */
export async function resolverSessao(
  banco: Banco,
  token: string | undefined,
): Promise<SessaoResolvida | null> {
  const hash = hashDoToken(token);
  if (!hash) return null;
  const r = await banco.query<{
    user_id: string;
    organization_id: string;
    role_code: string;
    expira_em: Date;
  }>('SELECT user_id, organization_id, role_code, expira_em FROM app.resolver_sessao($1)', [hash]);
  const l = r.rows[0];
  return l
    ? { usuarioId: l.user_id, organizationId: l.organization_id, papel: l.role_code, expiraEm: l.expira_em }
    : null;
}

/** Revoga a sessão; devolve false se ela já estava revogada ou não existe. */
export async function revogarSessao(banco: Banco, token: string | undefined): Promise<boolean> {
  const hash = hashDoToken(token);
  if (!hash) return false;
  const r = await banco.query<{ revogada: boolean }>('SELECT app.revogar_sessao($1) AS revogada', [hash]);
  return primeira(r.rows).revogada;
}

export type ResultadoTroca =
  | { readonly ok: true; readonly sessao: { readonly token: string; readonly expiraEm: Date } }
  | { readonly ok: false; readonly codigo: 'SESSAO_INVALIDA' | 'PAPEL_NAO_VINCULADO' };

/** Troca de papel só para papel atribuído; revoga a sessão atual e devolve outra, com a mesma expiração. */
export async function trocarPapel(
  banco: Banco,
  token: string | undefined,
  papel: string,
): Promise<ResultadoTroca> {
  const hash = hashDoToken(token);
  if (!hash) return { ok: false, codigo: 'SESSAO_INVALIDA' };
  if (!CODIGO_PAPEL.test(papel)) return { ok: false, codigo: 'PAPEL_NAO_VINCULADO' };
  const nova = novoToken();
  const r = await banco.query<{ resultado: string; expira_em: Date | null }>(
    'SELECT resultado, expira_em FROM app.trocar_papel($1, $2, $3)',
    [hash, papel, nova.hash],
  );
  const l = primeira(r.rows);
  if (l.resultado === 'SESSAO_CRIADA' && l.expira_em) {
    return { ok: true, sessao: { token: nova.token, expiraEm: l.expira_em } };
  }
  return {
    ok: false,
    codigo: l.resultado === 'PAPEL_NAO_VINCULADO' ? 'PAPEL_NAO_VINCULADO' : 'SESSAO_INVALIDA',
  };
}

function primeira<T>(linhas: readonly T[]): T {
  const l = linhas[0];
  if (l === undefined) throw new Error('A função do banco não devolveu linha.');
  return l;
}
