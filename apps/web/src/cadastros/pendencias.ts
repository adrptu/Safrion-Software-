import { COMANDOS_CADASTRO } from '@safrion/contracts';

import { PREFIXO } from '../estoque/rascunho';
import { intencaoValida, type Intencao } from './intencao';

export interface IntencaoGuardada {
  readonly campos: Record<string, string>;
  /** Fotografia anterior à edição; ausente em intenções legadas. Nunca é reconstruída a partir do pedido. */
  readonly iniciais?: Record<string, string>;
  readonly intencao: Intencao;
  readonly contexto: {
    readonly tipo: 'fazenda' | 'talhao' | 'situacao';
    readonly titulo: string;
    readonly volta: string;
  };
  /** Apenas ordenação/apresentação. Não é prova de quando o servidor recebeu. */
  readonly criadaEm: string;
}

type Escrita = Pick<Storage, 'getItem' | 'setItem'>;
type Varredura = Pick<Storage, 'length' | 'key' | 'getItem'>;

export function prefixoDasIntencoes(usuarioId: string, organizacaoId: string): string {
  return `${PREFIXO}cadastro-intencao:${encodeURIComponent(usuarioId)}:${encodeURIComponent(organizacaoId)}:`;
}

export function armazemLocal(): Storage | null {
  try {
    return typeof window === 'undefined' ? null : window.localStorage;
  } catch {
    return null;
  }
}

function objeto(valor: unknown): valor is Record<string, unknown> {
  return typeof valor === 'object' && valor !== null && !Array.isArray(valor);
}

function camposValidos(valor: unknown): valor is Record<string, string> {
  return objeto(valor) && Object.values(valor).every((campo) => typeof campo === 'string');
}

function contextoValido(valor: unknown): valor is IntencaoGuardada['contexto'] {
  if (!objeto(valor)) return false;
  const { tipo, titulo, volta } = valor;
  return (
    (tipo === 'fazenda' || tipo === 'talhao' || tipo === 'situacao') &&
    typeof titulo === 'string' &&
    titulo.trim() !== '' &&
    typeof volta === 'string' &&
    /^\/cadastros\/(?:areas(?:\/[0-9a-f-]{36})?|fazendas\/[0-9a-f-]{36})(?:\?[^#\\]*)?$/.test(volta)
  );
}

function lerGuardada(bruto: string): IntencaoGuardada | null {
  try {
    const v: unknown = JSON.parse(bruto);
    if (!objeto(v) || !camposValidos(v['campos'])) return null;
    if (v['iniciais'] !== undefined && !camposValidos(v['iniciais'])) return null;
    if (!intencaoValida(v['intencao']) || !contextoValido(v['contexto'])) return null;
    const { intencao, contexto } = v;
    if ((contexto.tipo === 'fazenda') !== (intencao.targetType === 'farm')) return null;
    if ((contexto.tipo === 'situacao') !== (intencao.commandType === COMANDOS_CADASTRO.alterarSituacaoTalhao))
      return null;
    if (typeof v['criadaEm'] !== 'string' || !Number.isFinite(Date.parse(v['criadaEm']))) return null;
    return {
      campos: v['campos'],
      ...(v['iniciais'] === undefined ? {} : { iniciais: v['iniciais'] }),
      intencao,
      contexto,
      criadaEm: v['criadaEm'],
    };
  } catch {
    return null;
  }
}

/** Guarda antes do POST. Falha deixa o envio bloqueado; a mesma chave nunca substitui outro pedido. */
export function gravarIntencao(
  armazem: Escrita | null,
  usuarioId: string,
  organizacaoId: string,
  guardada: IntencaoGuardada,
): boolean {
  if (!armazem) return false;
  try {
    const bruto = JSON.stringify(guardada);
    if (!lerGuardada(bruto)) return false;
    const chave = prefixoDasIntencoes(usuarioId, organizacaoId) + guardada.intencao.chave;
    const anterior = armazem.getItem(chave);
    if (anterior !== null) {
      const existente = lerGuardada(anterior);
      // Mantém inclusive os campos/horário/contexto originais da intenção já guardada.
      return (
        existente !== null &&
        existente.intencao.commandType === guardada.intencao.commandType &&
        existente.intencao.corpo === guardada.intencao.corpo
      );
    }
    armazem.setItem(chave, bruto);
    return armazem.getItem(chave) === bruto;
  } catch {
    return false;
  }
}

/** O chamador apaga somente depois de resolver esta intenção; outras pendências permanecem. */
export function apagarIntencao(
  armazem: Pick<Storage, 'removeItem'> | null,
  usuarioId: string,
  organizacaoId: string,
  chave: string,
): void {
  try {
    armazem?.removeItem(prefixoDasIntencoes(usuarioId, organizacaoId) + chave);
  } catch {
    // Conservar uma pendência é seguro: o recibo pode ser consultado de novo.
  }
}

/** Só lê este escopo; formato inválido não derruba a tela nem apaga evidência. Nada é enviado automaticamente. */
export function lerIntencoes(
  armazem: Varredura | null,
  usuarioId: string,
  organizacaoId: string,
): IntencaoGuardada[] {
  const prefixo = prefixoDasIntencoes(usuarioId, organizacaoId);
  const chaves: string[] = [];
  try {
    if (!armazem) return [];
    for (let i = 0; i < armazem.length; i += 1) {
      const chave = armazem.key(i);
      if (chave?.startsWith(prefixo)) chaves.push(chave);
    }
  } catch {
    return [];
  }
  const achadas: IntencaoGuardada[] = [];
  for (const chave of chaves) {
    try {
      const bruto = armazem.getItem(chave);
      if (!bruto) continue;
      const g = lerGuardada(bruto);
      if (g && chave === prefixo + g.intencao.chave) achadas.push(g);
    } catch {
      // Uma entrada corrompida/bloqueada não esconde outras intenções válidas.
    }
  }
  return achadas.sort(
    (a, b) =>
      Date.parse(a.criadaEm) - Date.parse(b.criadaEm) || a.intencao.chave.localeCompare(b.intencao.chave),
  );
}
