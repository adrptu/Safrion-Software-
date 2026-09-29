import { createHash } from 'node:crypto';

import type { ClientBase } from 'pg';

import { hashCanonico } from './canonico.js';
import type { SegredoPedido, VersaoAtiva } from './segredo-pedido.js';
import { ehUuid } from './sessao.js';
import { normalizarCodigo, validarDestino } from './vinculo.js';

/**
 * Fila de pedidos de vínculo em HML (R-006, GCP-0017, §3c; migração 0006). Cada versão ENABLED do segredo
 * hml-vinculo-pedido é um pedido; o banco guarda um recibo por pedido_id, na transação do efeito, e repetir devolve o
 * recibo sem reaplicar. Nenhuma linha de log traz código, subject, hash ou conteúdo do pedido.
 */

export const PEDIDO_INVALIDO = 'PEDIDO_INVALIDO';
const TAMANHO_MAXIMO = 4096;

interface Destino {
  readonly pedido_id: string;
  readonly organizacao: string;
  readonly usuario: string;
  readonly responsavel: string;
  readonly motivo: string;
}

export type Pedido =
  | (Destino & { readonly acao: 'conceder'; readonly codigo: string })
  | (Destino & { readonly acao: 'revogar' });

const CHAVES_REVOGAR = ['acao', 'motivo', 'organizacao', 'pedido_id', 'responsavel', 'usuario'];
const CHAVES_CONCEDER = [...CHAVES_REVOGAR, 'codigo'].sort();
const UTF8 = new TextDecoder('utf-8', { fatal: true });
// Uma string JSON no texto bruto; só vale sobre texto que o JSON.parse já aceitou (sem controle cru dentro de string).
const STRING_JSON = /"(?:[^"\\]|\\.)*"/g;

/**
 * Conteúdo de uma versão: objeto JSON com exatamente as chaves do contrato (codigo só em conceder), cada uma uma vez, até
 * 4 KiB, com as validações de validarDestino e o código normalizado. Qualquer outra forma é PEDIDO_INVALIDO, sem chamar
 * o banco.
 */
export function validarPedido(conteudo: string | Uint8Array): Pedido | typeof PEDIDO_INVALIDO {
  const bytes = typeof conteudo === 'string' ? Buffer.byteLength(conteudo, 'utf8') : conteudo.byteLength;
  if (bytes > TAMANHO_MAXIMO) return PEDIDO_INVALIDO;
  let texto: string;
  let valor: unknown;
  try {
    texto = typeof conteudo === 'string' ? conteudo : UTF8.decode(conteudo);
    valor = JSON.parse(texto);
  } catch {
    return PEDIDO_INVALIDO;
  }
  if (typeof valor !== 'object' || valor === null || Array.isArray(valor)) return PEDIDO_INVALIDO;
  const o = valor as Record<string, unknown>;
  const esperadas =
    o['acao'] === 'conceder' ? CHAVES_CONCEDER : o['acao'] === 'revogar' ? CHAVES_REVOGAR : undefined;
  const chaves = Object.keys(o).sort();
  if (!esperadas || chaves.length !== esperadas.length || chaves.some((k, i) => k !== esperadas[i])) {
    return PEDIDO_INVALIDO;
  }
  if (!chaves.every((k) => typeof o[k] === 'string')) return PEDIDO_INVALIDO;
  // O JSON.parse fica com o último valor de uma chave repetida, e um responsavel ou motivo com aspas trocaria usuario ou
  // acao sem aviso. Objeto plano só de strings: no texto bruto, as strings alternam chave e valor, então o número de
  // chaves escritas tem de ser o das esperadas.
  if ([...texto.matchAll(STRING_JSON)].length !== 2 * esperadas.length) return PEDIDO_INVALIDO;
  const t = o as Record<string, string>;
  const destino: Destino = {
    pedido_id: String(t['pedido_id']),
    organizacao: String(t['organizacao']),
    usuario: String(t['usuario']),
    responsavel: String(t['responsavel']),
    motivo: String(t['motivo']),
  };
  if (!ehUuid(destino.pedido_id)) return PEDIDO_INVALIDO;
  try {
    validarDestino(destino);
  } catch {
    return PEDIDO_INVALIDO;
  }
  if (t['acao'] === 'revogar') return { ...destino, acao: 'revogar' };
  const codigo = normalizarCodigo(String(t['codigo']));
  return codigo ? { ...destino, acao: 'conceder', codigo } : PEDIDO_INVALIDO;
}

const sha256 = (texto: string) => createHash('sha256').update(texto).digest();

/**
 * Identidade do conteúdo (§3c, item 2): hashCanonico dos campos fixos, UUIDs em minúsculas, texto como vai à função (a
 * canonização só o põe em NFC) e SHA-256 hexadecimal do código normalizado (null explícito em revogar). Substitui a
 * concatenação com "|", ambígua (CEN-08).
 */
export function conteudoHash(p: Pedido): string {
  return hashCanonico({
    formato: 'VINCULO-PEDIDO-1',
    pedido_id: p.pedido_id.toLowerCase(),
    acao: p.acao,
    organizacao: p.organizacao.toLowerCase(),
    usuario: p.usuario.toLowerCase(),
    responsavel: p.responsavel,
    motivo: p.motivo,
    codigo_hash: p.acao === 'conceder' ? sha256(p.codigo).toString('hex') : null,
  });
}

// Com recibo; os quatro primeiros são aplicação (saída 0), o resto é recusa final (saída 1).
const APLICADOS = new Set(['concedido', 'mantido', 'revogado', 'sem_vinculo']);
const RESULTADOS = new Set([
  ...APLICADOS,
  'PEDIDO_ATRASADO',
  'OPCAO_INVALIDA',
  'PEDIDO_INEXISTENTE',
  'PEDIDO_VENCIDO',
  'PEDIDO_CONSUMIDO',
  'VINCULO_CONFLITANTE',
  'USUARIO_INVALIDO',
  // Sem recibo novo: a versão é desativada, não destruída.
  'PEDIDO_ID_REUTILIZADO',
]);

// Trava de sessão da fila, na mesma forma das outras travas de sessão do pacote (migrar.ts, preparo.ts, papeis.ts): uma
// execução por banco. As travas por transação da 0005 e da 0006 usam a forma de duas chaves e não colidem com esta.
export const TRAVA_FILA = "hashtext('safrion.vinculo_fila')";

type CodigoErroFila = 'CONEXAO_PERDIDA' | 'RESULTADO_INESPERADO';

class ErroFila extends Error {
  override readonly name = 'ErroFila';
  constructor(readonly codigo: CodigoErroFila) {
    super('A fila parou; veja o código.');
  }
}

const se = (v: unknown, formato: RegExp) => (typeof v === 'string' && formato.test(v) ? v : undefined);

/** Linha de falha só com códigos: SQLSTATE, código do Node, do segredo ou da fila; nunca a mensagem. */
function falhaSemTextoLivre(erro: unknown) {
  const o = typeof erro === 'object' && erro !== null ? (erro as { codigo?: unknown; code?: unknown }) : {};
  return {
    resultado: 'falha',
    codigo: 'FALHA_INFRAESTRUTURA',
    erro_tipo: erro instanceof Error ? se(erro.name, /^[A-Za-z]{1,64}$/) : typeof erro,
    codigo_tecnico: se(o.codigo ?? o.code, /^[0-9A-Z_]{5,40}$/),
  };
}

// createTime em RFC 3339 UTC com 0 a 9 casas (conferido em segredo-pedido.ts): com a fração completa, a ordem do texto é
// a do instante. No empate, o número da versão (sem zeros à esquerda: menor comprimento, menor número).
const instante = (t: string) => {
  const [base, fracao = ''] = t.slice(0, -1).split('.');
  return `${String(base)}.${fracao.padEnd(9, '0')}`;
};
function ordem(a: VersaoAtiva, b: VersaoAtiva): number {
  const ta = instante(a.createTime);
  const tb = instante(b.createTime);
  if (ta !== tb) return ta < tb ? -1 : 1;
  return a.versao.length - b.versao.length || (a.versao < b.versao ? -1 : 1);
}

/** Uma transação curta por pedido (§3c, item 5); desfeita em qualquer falha antes do COMMIT. */
async function aplicar(
  cliente: ClientBase,
  pedido: Pedido,
  v: VersaoAtiva,
): Promise<{ resultado: string; repetido: boolean }> {
  let aberta = false;
  try {
    await cliente.query('BEGIN');
    aberta = true;
    await cliente.query("SET LOCAL lock_timeout = '5s'");
    await cliente.query("SET LOCAL statement_timeout = '30s'");
    const r = await cliente.query<{ resultado: unknown; repetido: unknown }>(
      'SELECT resultado, repetido FROM app.processar_pedido_vinculo($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)',
      [
        pedido.pedido_id,
        Buffer.from(conteudoHash(pedido), 'hex'),
        v.versao,
        pedido.acao,
        pedido.acao === 'conceder' ? sha256(pedido.codigo) : null,
        pedido.organizacao,
        pedido.usuario,
        pedido.responsavel,
        pedido.motivo,
        v.createTime,
      ],
    );
    const { resultado, repetido } = r.rows[0] ?? {};
    // Resultado desconhecido (AMBIENTE_PROIBIDO inclusive, que não grava recibo) não é recusa: a fila para.
    if (typeof resultado !== 'string' || !RESULTADOS.has(resultado) || typeof repetido !== 'boolean') {
      throw new ErroFila('RESULTADO_INESPERADO');
    }
    // Enviado o COMMIT, não há o que desfazer daqui: se a resposta se perde, o recibo decide na próxima execução.
    aberta = false;
    await cliente.query('COMMIT');
    return { resultado, repetido };
  } catch (erro) {
    if (aberta) await cliente.query('ROLLBACK').catch(() => undefined);
    throw erro;
  }
}

export interface OpcoesFila {
  /**
   * Conexão dedicada, já com o papel migrator; nenhum outro uso dela durante a fila. Depois de uma falha (saída 3), a
   * trava da fila fica com ela: encerre a conexão, como o comando faz, e o servidor a solta.
   */
  readonly cliente: ClientBase;
  readonly segredo: SegredoPedido;
  readonly registrar: (linha: string) => void;
}

/**
 * Processa a fila (§3c, item 6) e devolve a saída do comando: 3 se parou numa falha de infraestrutura (banco, API, etag
 * recusado, desativar ou destruir, conexão que caiu), senão 1 se houve OCUPADO, inválido, reutilizado, atrasado ou
 * recusa de negócio, senão 0. Nenhuma consulta direta ao recibo: tudo passa pela função do banco.
 */
export async function processarFila({ cliente, segredo, registrar }: OpcoesFila): Promise<0 | 1 | 3> {
  const escrever = (linha: object) => {
    registrar(JSON.stringify(linha));
  };
  const conexao = { perdida: false };
  const perder = () => {
    conexao.perdida = true;
  };
  // Sem a conexão, a trava de sessão foi junto e outra execução pode já ter a versão: a fila para antes da próxima
  // chamada à API ou ao banco. Conferido depois de cada espera, porque o evento chega no meio de qualquer uma.
  const conferirConexao = () => {
    if (conexao.perdida) throw new ErroFila('CONEXAO_PERDIDA');
  };
  cliente.on('error', perder);
  cliente.on('end', perder);
  let recusas = false;
  try {
    const trava = await cliente.query<{ livre: boolean }>(
      `SELECT pg_try_advisory_lock(${TRAVA_FILA}) AS livre`,
    );
    if (trava.rows[0]?.livre !== true) {
      escrever({ resultado: 'OCUPADO' });
      return 1;
    }
    const versoes = (await segredo.listarAtivas()).sort(ordem);
    for (const v of versoes) {
      conferirConexao();
      // O etag desta leitura é o que vale para desativar ou destruir.
      const { estado, etag } = await segredo.obter(v.versao);
      conferirConexao();
      if (estado !== 'ENABLED') {
        escrever({ versao: v.versao, resultado: 'VERSAO_INATIVA' });
        continue;
      }
      const conteudo = await segredo.acessar(v.versao);
      conferirConexao();
      const pedido = validarPedido(conteudo);
      if (pedido === PEDIDO_INVALIDO) {
        recusas = true;
        escrever({ versao: v.versao, resultado: PEDIDO_INVALIDO });
        // Desativar é reversível; destruir fica com o dono.
        await segredo.desativar(v.versao, etag);
        continue;
      }
      const { resultado, repetido } = await aplicar(cliente, pedido, v);
      if (!APLICADOS.has(resultado)) recusas = true;
      escrever({ pedido_id: pedido.pedido_id, versao: v.versao, resultado, repetido });
      // Parar aqui deixa a versão para a próxima execução, que relê o recibo (ou a reutilização) sem reaplicar.
      conferirConexao();
      if (resultado === 'PEDIDO_ID_REUTILIZADO') await segredo.desativar(v.versao, etag);
      else await segredo.destruir(v.versao, etag);
    }
    conferirConexao();
    // Só no fim sem falha: numa conexão com problema, soltar poderia prender o comando, e encerrá-la já solta.
    await cliente.query(`SELECT pg_advisory_unlock(${TRAVA_FILA})`).catch(() => undefined);
    return recusas ? 1 : 0;
  } catch (erro) {
    escrever(falhaSemTextoLivre(erro));
    return 3;
  } finally {
    cliente.off('error', perder);
    cliente.off('end', perder);
  }
}
