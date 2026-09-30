import { PREFIXO } from '../estoque/rascunho';
import type { CamposLinha, CamposRecebimento, Intencao } from './formulario';

/**
 * Recebimento guardado no localStorage (contrato CMD-15 §2 e §6.2, v3.10), em duas espécies de chave, as duas com usuário
 * e organização (outra sessão no mesmo navegador não vê nem reenvia o que não é seu):
 * - o rascunho, só campos, pela última gravação: até 50 linhas sobrevivem a fechar a aba;
 * - cada intenção pendente na sua própria chave (a da intenção), com o corpo imutável e os campos enviados. Nasce antes
 *   do POST e só some quando quem a resolve (recibo correspondente) a apaga, ou em Sair. Gravar o rascunho nunca toca
 *   intenção, então uma aba antiga não apaga o envio pendente de outra (CX-UI01), sem depender de atomicidade.
 * Sessão expirada não apaga nada (o mesmo usuário volta e confere). Nunca é enviado sozinho.
 */
export interface RascunhoRecebimento {
  readonly campos: CamposRecebimento;
}

export interface IntencaoGuardada {
  readonly campos: CamposRecebimento;
  readonly intencao: Intencao;
  /** Instante ISO de quando foi guardada, só para mostrar a mais antiga primeiro. */
  readonly criadaEm: string;
}

type Leitura = Pick<Storage, 'getItem'>;
type Escrita = Pick<Storage, 'setItem' | 'removeItem'>;
type Varredura = Pick<Storage, 'length' | 'key' | 'getItem'>;

export function chaveDoRecebimento(usuarioId: string, organizacaoId: string): string {
  return `${PREFIXO}recebimento:${usuarioId}:${organizacaoId}`;
}

/** Prefixo das intenções pendentes desta pessoa e organização; a chave de cada uma termina na chave da intenção. */
export function prefixoDasIntencoes(usuarioId: string, organizacaoId: string): string {
  return `${PREFIXO}recebimento-intencao:${usuarioId}:${organizacaoId}:`;
}

/** localStorage quando existe e está liberado (modo privado ou bloqueio devolvem null). */
export function armazemLocal(): Storage | null {
  try {
    return typeof window === 'undefined' ? null : window.localStorage;
  } catch {
    return null;
  }
}

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const texto = (v: unknown, max = 200): v is string => typeof v === 'string' && v.length <= max;

const CAMPOS_LINHA: readonly (keyof CamposLinha)[] = [
  'id',
  'produto',
  'lote',
  'validade',
  'local',
  'unidade',
  'documento',
  'apto',
  'quarentena',
  'bloqueado',
  'recusado',
  'motivo',
  'motivoTexto',
  'inspecaoResponsavel',
  'inspecaoPrazo',
  'ocorrenciaProduto',
  'ocorrenciaDescricao',
  'ocorrenciaQuantidade',
  'ocorrenciaUnidade',
  'ocorrenciaDestino',
  'ocorrenciaResponsavel',
  'ocorrenciaPrazo',
];
const CAMPOS_ORIGEM = ['emitente', 'tipo', 'serie', 'numero', 'emissao', 'recebimento', 'fazenda'] as const;

function linhaValida(v: unknown): v is CamposLinha {
  if (typeof v !== 'object' || v === null) return false;
  const l = v as Record<string, unknown>;
  return CAMPOS_LINHA.every((c) => texto(l[c]));
}

function camposValidos(v: unknown): v is CamposRecebimento {
  if (typeof v !== 'object' || v === null) return false;
  const c = v as Record<string, unknown>;
  const linhas = c['linhas'];
  return (
    CAMPOS_ORIGEM.every((k) => texto(c[k])) &&
    Array.isArray(linhas) &&
    linhas.length <= 50 &&
    linhas.every(linhaValida)
  );
}

function intencaoValida(v: unknown): v is Intencao {
  if (typeof v !== 'object' || v === null) return false;
  const i = v as Record<string, unknown>;
  return (
    typeof i['chave'] === 'string' &&
    UUID.test(i['chave']) &&
    typeof i['documentoId'] === 'string' &&
    UUID.test(i['documentoId']) &&
    typeof i['corpo'] === 'string' &&
    i['corpo'].length <= 64 * 1024
  );
}

/** Rascunho guardado; formato desconhecido ou corrompido é ignorado (nunca derruba a tela). */
export function lerRecebimento(armazem: Leitura | null, chave: string): RascunhoRecebimento | null {
  try {
    const bruto = armazem?.getItem(chave);
    if (!bruto) return null;
    const r: unknown = JSON.parse(bruto);
    if (typeof r !== 'object' || r === null) return null;
    const { campos } = r as Record<string, unknown>;
    return camposValidos(campos) ? { campos } : null;
  } catch {
    return null;
  }
}

function gravar(armazem: Escrita | null, chave: string, valor: unknown): boolean {
  if (!armazem) return false;
  try {
    armazem.setItem(chave, JSON.stringify(valor));
    return true;
  } catch {
    return false;
  }
}

function apagar(armazem: Escrita | null, chave: string): void {
  try {
    armazem?.removeItem(chave);
  } catch {
    // Sem armazenamento, não há o que apagar.
  }
}

/**
 * Grava o rascunho e devolve se ficou guardado. Armazenamento cheio ou bloqueado devolve false sem lançar e sem apagar o
 * que já estava lá. Só a chave do rascunho é tocada.
 */
export function gravarRecebimento(armazem: Escrita | null, chave: string, r: RascunhoRecebimento): boolean {
  return gravar(armazem, chave, r);
}

/** Depois de confirmar: o documento seguinte começa do zero (nada de quantidade, lote ou validade herdados). */
export function apagarRecebimento(armazem: Escrita | null, chave: string): void {
  apagar(armazem, chave);
}

/** Guarda a intenção na chave dela, antes do POST; false (cheio ou bloqueado) quer dizer que nada pode ser enviado. */
export function gravarIntencao(
  armazem: Escrita | null,
  usuarioId: string,
  organizacaoId: string,
  g: IntencaoGuardada,
): boolean {
  return gravar(armazem, prefixoDasIntencoes(usuarioId, organizacaoId) + g.intencao.chave, g);
}

/** Só quem resolveu a intenção (recibo correspondente ou recusa certa do primeiro envio) apaga a chave dela. */
export function apagarIntencao(
  armazem: Escrita | null,
  usuarioId: string,
  organizacaoId: string,
  chave: string,
): void {
  apagar(armazem, prefixoDasIntencoes(usuarioId, organizacaoId) + chave);
}

/** Intenções pendentes desta pessoa e organização, da mais antiga para a mais nova; formato inválido é ignorado. */
export function lerIntencoes(
  armazem: Varredura | null,
  usuarioId: string,
  organizacaoId: string,
): IntencaoGuardada[] {
  const prefixo = prefixoDasIntencoes(usuarioId, organizacaoId);
  const achadas: IntencaoGuardada[] = [];
  const chaves: string[] = [];
  try {
    if (!armazem) return [];
    for (let i = 0; i < armazem.length; i += 1) {
      const k = armazem.key(i);
      if (k?.startsWith(prefixo)) chaves.push(k);
    }
  } catch {
    return [];
  }
  for (const k of chaves) {
    // Uma chave corrompida não esconde as outras.
    try {
      const bruto = armazem.getItem(k);
      if (!bruto) continue;
      const g: unknown = JSON.parse(bruto);
      if (typeof g !== 'object' || g === null) continue;
      const { campos, intencao, criadaEm } = g as Record<string, unknown>;
      if (
        camposValidos(campos) &&
        intencaoValida(intencao) &&
        k === prefixo + intencao.chave &&
        typeof criadaEm === 'string'
      ) {
        achadas.push({ campos, intencao, criadaEm });
      }
    } catch {
      continue;
    }
  }
  return achadas.sort((x, y) =>
    x.criadaEm === y.criadaEm
      ? x.intencao.chave.localeCompare(y.intencao.chave)
      : x.criadaEm < y.criadaEm
        ? -1
        : 1,
  );
}
