import { createHash, randomInt } from 'node:crypto';

import type { ClientBase, Pool } from 'pg';

import { ehUuid } from './sessao.js';

/**
 * Vínculo de identidade real em HML (ADR 0004 §11; migração 0005).
 * - Pedido de acesso: a casca registra, depois de um login OIDC validado sem vínculo, e mostra o código de referência. O
 *   pedido não concede nada; o código só localiza o pedido, não prova quem é a pessoa ao administrador.
 * - Concessão e revogação: caminho do administrador (migrator), só em banco hml, com responsável e motivo.
 * Código, subject e hash nunca saem daqui em mensagem, log ou recibo.
 */
type Banco = ClientBase | Pool;

/** Crockford base32: sem I, L, O e U. 10 caracteres = 50 bits. */
const ALFABETO = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
const TAMANHO_CODIGO = 10;
const FORMATO_CODIGO = /^[0-9A-HJKMNP-TV-Z]{10}$/;

/** Código digitado ou colado: maiúsculas, sem espaço e hífen, O→0 e I/L→1 (Crockford); null fora do formato. */
export function normalizarCodigo(texto: string): string | null {
  const limpo = texto.toUpperCase().replace(/[\s-]/g, '').replace(/O/g, '0').replace(/[IL]/g, '1');
  return FORMATO_CODIGO.test(limpo) ? limpo : null;
}

function hashDoCodigo(codigo: string): Buffer {
  return createHash('sha256').update(codigo).digest();
}

function novoCodigo(): string {
  let codigo = '';
  for (let i = 0; i < TAMANHO_CODIGO; i++) codigo += ALFABETO.charAt(randomInt(ALFABETO.length));
  return codigo;
}

export type PedidoAcesso =
  | { readonly resultado: 'registrado'; readonly codigo: string }
  | { readonly resultado: 'cota_esgotada' | 'fora_de_hml' | 'recusado' };

/**
 * Pedido de acesso de uma identidade validada pelo provedor e sem vínculo. Um pedido vivo por identidade: um novo login
 * troca o código. Fora de hml, ou com a cota de HML cheia, não há código.
 */
export async function registrarPedidoAcesso(
  banco: Banco,
  identidade: { readonly issuer: string; readonly subject: string },
): Promise<PedidoAcesso> {
  const codigo = novoCodigo();
  const r = await banco.query<{ resultado: string }>(
    'SELECT app.registrar_pedido_acesso($1, $2, $3) AS resultado',
    [identidade.issuer, identidade.subject, hashDoCodigo(codigo)],
  );
  const resultado = r.rows[0]?.resultado;
  if (resultado === 'registrado') return { resultado, codigo };
  if (resultado === 'cota_esgotada' || resultado === 'fora_de_hml') return { resultado };
  return { resultado: 'recusado' };
}

export type CodigoErroVinculo =
  | 'AMBIENTE_PROIBIDO'
  | 'OPCAO_INVALIDA'
  | 'CODIGO_INVALIDO'
  | 'PEDIDO_INEXISTENTE'
  | 'PEDIDO_VENCIDO'
  | 'PEDIDO_CONSUMIDO'
  | 'VINCULO_CONFLITANTE'
  | 'USUARIO_INVALIDO';

const MENSAGENS: ReadonlyMap<CodigoErroVinculo, string> = new Map([
  ['AMBIENTE_PROIBIDO', 'Vínculo de identidade real só em banco identificado como hml; nada foi alterado.'],
  ['OPCAO_INVALIDA', 'Organização, usuário, responsável ou motivo fora do formato; nada foi alterado.'],
  ['CODIGO_INVALIDO', 'O código tem 10 caracteres (letras e números); nada foi alterado.'],
  ['PEDIDO_INEXISTENTE', 'Não há pedido de acesso com esse código; nada foi alterado.'],
  [
    'PEDIDO_VENCIDO',
    'O pedido venceu (24 h). A pessoa entra de novo para gerar outro código; nada foi alterado.',
  ],
  [
    'PEDIDO_CONSUMIDO',
    'Esse pedido já foi usado e o acesso foi revogado depois. Um acesso novo pede um pedido novo; nada foi alterado.',
  ],
  [
    'VINCULO_CONFLITANTE',
    'O pedido ou a identidade já estão ligados a outro usuário nesta organização; nada foi alterado.',
  ],
  [
    'USUARIO_INVALIDO',
    'O usuário não existe nesta organização, está inativo ou não tem papel; nada foi alterado.',
  ],
]);

export class ErroVinculo extends Error {
  override readonly name = 'ErroVinculo';
  constructor(readonly codigo: CodigoErroVinculo) {
    super(MENSAGENS.get(codigo));
  }
}

const TEXTO_LIVRE = /^[^\p{Cc}]+$/u;

/** Confere as opções do administrador antes de qualquer consulta; o banco confere de novo. */
export function validarDestino(o: {
  readonly organizacao: string;
  readonly usuario: string;
  readonly responsavel: string;
  readonly motivo: string;
}): void {
  const cabe = (t: string, max: number) =>
    TEXTO_LIVRE.test(t) && t.trim().length >= 1 && t.trim().length <= max;
  if (!ehUuid(o.organizacao) || !ehUuid(o.usuario) || !cabe(o.responsavel, 120) || !cabe(o.motivo, 200)) {
    throw new ErroVinculo('OPCAO_INVALIDA');
  }
}

function comoErro(resultado: string | undefined): ErroVinculo {
  const codigo = [...MENSAGENS.keys()].find((c) => c === resultado);
  // Resultado desconhecido do banco não é recusa de negócio: vira falha de infraestrutura para quem chama.
  if (!codigo) throw new Error('RESULTADO_INESPERADO');
  return new ErroVinculo(codigo);
}

/**
 * Concede o vínculo da identidade do pedido ao usuário da organização. 'mantido' quando o mesmo pedido já concedeu o
 * mesmo destino e o vínculo segue vigente. Qualquer recusa lança ErroVinculo, e nada muda.
 */
export async function concederVinculo(
  migrator: ClientBase,
  o: {
    readonly codigo: string;
    readonly organizacao: string;
    readonly usuario: string;
    readonly responsavel: string;
    readonly motivo: string;
  },
): Promise<'concedido' | 'mantido'> {
  validarDestino(o);
  const codigo = normalizarCodigo(o.codigo);
  if (!codigo) throw new ErroVinculo('CODIGO_INVALIDO');
  const r = await migrator.query<{ resultado: string }>(
    'SELECT app.conceder_vinculo($1, $2, $3, $4, $5) AS resultado',
    [hashDoCodigo(codigo), o.organizacao, o.usuario, o.responsavel, o.motivo],
  );
  const resultado = r.rows[0]?.resultado;
  if (resultado === 'concedido' || resultado === 'mantido') return resultado;
  throw comoErro(resultado);
}

/**
 * Revoga todos os vínculos do usuário nesta organização (um evento por vínculo) e as sessões dele aqui. Outras
 * organizações não mudam. Sem vínculo, 'sem_vinculo' e nada muda.
 */
export async function revogarVinculos(
  migrator: ClientBase,
  o: {
    readonly organizacao: string;
    readonly usuario: string;
    readonly responsavel: string;
    readonly motivo: string;
  },
): Promise<{ readonly resultado: 'revogado' | 'sem_vinculo'; readonly revogados: number }> {
  validarDestino(o);
  const r = await migrator.query<{ resultado: string; revogados: number }>(
    'SELECT resultado, revogados FROM app.revogar_vinculos($1, $2, $3, $4)',
    [o.organizacao, o.usuario, o.responsavel, o.motivo],
  );
  const linha = r.rows[0];
  if (linha?.resultado === 'revogado' || linha?.resultado === 'sem_vinculo') {
    return { resultado: linha.resultado, revogados: linha.revogados };
  }
  throw comoErro(linha?.resultado);
}
