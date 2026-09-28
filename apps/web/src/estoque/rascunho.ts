import type { CamposEntrada } from './entrada';

/**
 * Rascunho da entrada no armazenamento da sessão do navegador (B2-C02): o que foi digitado volta depois de recarregar,
 * e o envio cuja resposta se perdeu guarda a chave, o conteúdo e a versão originais para ser conferido antes de outra
 * entrada. Separado por usuário, organização e lote; sair apaga tudo o que tem o prefixo. Nunca é enviado sozinho.
 */
export const PREFIXO = 'safrion:';

/** Envio já feito cujo resultado não se sabe (rede caiu ou resposta inesperada): reenviar igual não duplica. */
export interface EnvioIncerto {
  readonly chave: string;
  readonly campos: CamposEntrada;
  readonly versao: number;
}

export interface Rascunho {
  readonly campos: CamposEntrada;
  readonly incerto: EnvioIncerto | null;
}

type Leitura = Pick<Storage, 'getItem'>;
type Escrita = Pick<Storage, 'setItem' | 'removeItem'>;

export function chaveDoRascunho(usuarioId: string, organizacaoId: string, loteId: string): string {
  return `${PREFIXO}entrada:${usuarioId}:${organizacaoId}:${loteId}`;
}

/** sessionStorage quando existe e está liberado (modo privado ou bloqueio devolvem null). */
export function armazemDaSessao(): Storage | null {
  try {
    return typeof window === 'undefined' ? null : window.sessionStorage;
  } catch {
    return null;
  }
}

const texto = (v: unknown): v is string => typeof v === 'string' && v.length <= 200;

function camposValidos(v: unknown): v is CamposEntrada {
  if (typeof v !== 'object' || v === null) return false;
  const c = v as Record<string, unknown>;
  return texto(c['quantidade']) && texto(c['unidade']) && texto(c['situacao']) && texto(c['local']);
}

function incertoValido(v: unknown): v is EnvioIncerto {
  if (typeof v !== 'object' || v === null) return false;
  const e = v as Record<string, unknown>;
  return (
    typeof e['chave'] === 'string' &&
    /^[0-9a-f-]{36}$/.test(e['chave']) &&
    camposValidos(e['campos']) &&
    Number.isSafeInteger(e['versao']) &&
    (e['versao'] as number) >= 0
  );
}

/** Rascunho guardado; formato desconhecido ou corrompido é ignorado (nunca derruba a tela). */
export function lerRascunho(armazem: Leitura | null, chave: string): Rascunho | null {
  try {
    const bruto = armazem?.getItem(chave);
    if (!bruto) return null;
    const r: unknown = JSON.parse(bruto);
    if (typeof r !== 'object' || r === null) return null;
    const { campos, incerto } = r as Record<string, unknown>;
    if (!camposValidos(campos) || (incerto !== null && !incertoValido(incerto))) return null;
    return { campos, incerto };
  } catch {
    return null;
  }
}

/**
 * Grava o rascunho; sem nada digitado e sem envio incerto, apaga. Devolve se ficou guardado: sem armazenamento, o
 * trabalho continua, mas a tela não pode prometer recuperar depois de recarregar (B2-C03).
 */
export function gravarRascunho(armazem: Escrita | null, chave: string, r: Rascunho): boolean {
  if (!armazem) return false;
  try {
    if (r.incerto === null && r.campos.quantidade.trim() === '' && r.campos.situacao === '')
      armazem.removeItem(chave);
    else armazem.setItem(chave, JSON.stringify(r));
    return true;
  } catch {
    return false;
  }
}

/** Ao sair: apaga os rascunhos do Safrion nesta aba, para a próxima pessoa não ver o que foi digitado. */
export function apagarRascunhos(armazem: Pick<Storage, 'length' | 'key' | 'removeItem'> | null): void {
  try {
    if (!armazem) return;
    const chaves: string[] = [];
    for (let i = 0; i < armazem.length; i += 1) {
      const k = armazem.key(i);
      if (k?.startsWith(PREFIXO)) chaves.push(k);
    }
    for (const k of chaves) armazem.removeItem(k);
  } catch {
    // Idem: sem armazenamento, não há o que apagar.
  }
}
