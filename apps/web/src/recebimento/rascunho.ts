import { PREFIXO } from '../estoque/rascunho';
import type { CamposLinha, CamposRecebimento, Intencao } from './formulario';

/**
 * Rascunho do recebimento no localStorage (contrato CMD-15 §2 e §6.2): até 50 linhas sobrevivem a fechar a aba. A chave
 * leva usuário e organização, então outra sessão no mesmo navegador não vê nem reenvia o que não é seu. Sessão expirada
 * não apaga nada (o mesmo usuário volta e confere); só Sair apaga, pelo prefixo comum. Nunca é enviado sozinho.
 */
export interface RascunhoRecebimento {
  readonly campos: CamposRecebimento;
  /** Envio feito cujo resultado não se sabe: chave, documento e corpo exatos, imutáveis até um recibo resolver. */
  readonly intencao: Intencao | null;
}

type Leitura = Pick<Storage, 'getItem'>;
type Escrita = Pick<Storage, 'setItem' | 'removeItem'>;

export function chaveDoRecebimento(usuarioId: string, organizacaoId: string): string {
  return `${PREFIXO}recebimento:${usuarioId}:${organizacaoId}`;
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
    const { campos, intencao } = r as Record<string, unknown>;
    if (!camposValidos(campos) || (intencao !== null && !intencaoValida(intencao))) return null;
    return { campos, intencao };
  } catch {
    return null;
  }
}

/**
 * Grava o rascunho e devolve se ficou guardado. Armazenamento cheio ou bloqueado devolve false sem lançar e sem apagar o
 * que já estava lá: com intenção, a tela não envia (a recuperação do envio precisa estar assegurada antes; Codex 06:56Z).
 */
export function gravarRecebimento(armazem: Escrita | null, chave: string, r: RascunhoRecebimento): boolean {
  if (!armazem) return false;
  try {
    armazem.setItem(chave, JSON.stringify(r));
    return true;
  } catch {
    return false;
  }
}

/** Depois de um recibo confirmado: o documento seguinte começa do zero (nada de quantidade, lote ou validade herdados). */
export function apagarRecebimento(armazem: Escrita | null, chave: string): void {
  try {
    armazem?.removeItem(chave);
  } catch {
    // Sem armazenamento, não há o que apagar.
  }
}
