import { PREFIXO } from '../estoque/rascunho';
import type { CampoOrigem, CamposLinha, CamposRecebimento, Intencao } from './formulario';

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

/** Valores das chaves com o prefixo, já lidos como objeto; uma chave corrompida não esconde as outras. */
function varrer(
  armazem: Varredura | null,
  prefixo: string,
): { chave: string; valor: Record<string, unknown> }[] {
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
  const lidos: { chave: string; valor: Record<string, unknown> }[] = [];
  for (const k of chaves) {
    try {
      const bruto = armazem.getItem(k);
      if (!bruto) continue;
      const v: unknown = JSON.parse(bruto);
      if (typeof v === 'object' && v !== null) lidos.push({ chave: k, valor: v as Record<string, unknown> });
    } catch {
      continue;
    }
  }
  return lidos;
}

/** Intenções pendentes desta pessoa e organização, da mais antiga para a mais nova; formato inválido é ignorado. */
export function lerIntencoes(
  armazem: Varredura | null,
  usuarioId: string,
  organizacaoId: string,
): IntencaoGuardada[] {
  const prefixo = prefixoDasIntencoes(usuarioId, organizacaoId);
  const achadas: IntencaoGuardada[] = [];
  for (const { chave: k, valor } of varrer(armazem, prefixo)) {
    const { campos, intencao, criadaEm } = valor;
    if (
      camposValidos(campos) &&
      intencaoValida(intencao) &&
      k === prefixo + intencao.chave &&
      typeof criadaEm === 'string'
    ) {
      achadas.push({ campos, intencao, criadaEm });
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

/**
 * Formulário guardado para corrigir depois (CX-UI04): a intenção resolvida sem confirmar quando já havia outro rascunho,
 * ou o rascunho que saiu da tela para dar lugar a um guardado. Nenhum preenchimento é descartado sem gesto explícito.
 */
export interface FormularioGuardado {
  readonly id: string;
  readonly campos: CamposRecebimento;
  /** Motivo da recusa, mostrado só quando este formulário é aberto; null no rascunho guardado. */
  readonly motivo: { readonly mensagem: string; readonly campo?: CampoOrigem } | null;
  readonly guardadoEm: string;
}

export function prefixoDosGuardados(usuarioId: string, organizacaoId: string): string {
  return `${PREFIXO}recebimento-guardado:${usuarioId}:${organizacaoId}:`;
}

const CAMPOS_DE_ORIGEM: readonly string[] = CAMPOS_ORIGEM;

function motivoValido(v: unknown): v is FormularioGuardado['motivo'] {
  if (v === null) return true;
  if (typeof v !== 'object') return false;
  const m = v as Record<string, unknown>;
  return (
    texto(m['mensagem'], 300) &&
    (m['campo'] === undefined || (typeof m['campo'] === 'string' && CAMPOS_DE_ORIGEM.includes(m['campo'])))
  );
}

export function guardarFormulario(
  armazem: Escrita | null,
  usuarioId: string,
  organizacaoId: string,
  f: FormularioGuardado,
): boolean {
  return gravar(armazem, prefixoDosGuardados(usuarioId, organizacaoId) + f.id, f);
}

export function apagarGuardado(
  armazem: Escrita | null,
  usuarioId: string,
  organizacaoId: string,
  id: string,
): void {
  apagar(armazem, prefixoDosGuardados(usuarioId, organizacaoId) + id);
}

/** Formulários guardados, do mais antigo para o mais novo; formato inválido é ignorado. */
export function lerGuardados(
  armazem: Varredura | null,
  usuarioId: string,
  organizacaoId: string,
): FormularioGuardado[] {
  const prefixo = prefixoDosGuardados(usuarioId, organizacaoId);
  const achados: FormularioGuardado[] = [];
  for (const { chave: k, valor } of varrer(armazem, prefixo)) {
    const { id, campos, motivo, guardadoEm } = valor;
    if (
      typeof id === 'string' &&
      UUID.test(id) &&
      k === prefixo + id &&
      camposValidos(campos) &&
      motivoValido(motivo) &&
      typeof guardadoEm === 'string'
    ) {
      achados.push({ id, campos, motivo, guardadoEm });
    }
  }
  return achados.sort((x, y) =>
    x.guardadoEm === y.guardadoEm ? x.id.localeCompare(y.id) : x.guardadoEm < y.guardadoEm ? -1 : 1,
  );
}

/** Há algo digitado (origem ou alguma linha)? Formulário só com o contexto não conta como rascunho a preservar. */
export function temConteudo(c: CamposRecebimento): boolean {
  const cheio = (v: string) => v.trim() !== '';
  return (
    cheio(c.serie) ||
    cheio(c.numero) ||
    cheio(c.emissao) ||
    c.linhas.some((l) =>
      CAMPOS_LINHA.some((k) => k !== 'id' && k !== 'local' && k !== 'unidade' && cheio(l[k])),
    )
  );
}
