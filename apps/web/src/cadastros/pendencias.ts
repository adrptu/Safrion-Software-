import { COMANDOS_CADASTRO } from '@safrion/contracts';

import { PREFIXO } from '../estoque/rascunho';
import { intencaoValida, mesmoConteudoDeDominio, type Intencao } from './intencao';

export interface FalhaGuardada {
  readonly tipo: 'corrigir' | 'somente_consulta';
  readonly mensagem: string;
  readonly correlacao: string;
}
export interface IntencaoGuardada {
  /** Ausência é o formato legado: envio sem confirmação, nunca prova de não gravação. */
  readonly falha?: FalhaGuardada;
  /** A correção não substitui o registro recusado antes de haver recibo do novo pedido. */
  readonly origem?: {
    readonly chave: string;
    readonly raiz: string;
    readonly correlacao: string;
  };
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

function texto(valor: unknown): valor is string {
  return typeof valor === 'string' && valor.trim().length > 0;
}
function falhaValida(v: unknown): v is FalhaGuardada {
  return (
    objeto(v) &&
    Object.keys(v).length === 3 &&
    (v['tipo'] === 'corrigir' || v['tipo'] === 'somente_consulta') &&
    texto(v['mensagem']) &&
    texto(v['correlacao'])
  );
}
function origemValida(v: unknown): v is NonNullable<IntencaoGuardada['origem']> {
  return (
    objeto(v) &&
    Object.keys(v).length === 3 &&
    texto(v['chave']) &&
    texto(v['raiz']) &&
    texto(v['correlacao'])
  );
}
function lerGuardada(bruto: string): IntencaoGuardada | null {
  try {
    const v: unknown = JSON.parse(bruto);
    if (!objeto(v) || !camposValidos(v['campos'])) return null;
    if (v['falha'] !== undefined && !falhaValida(v['falha'])) return null;
    if (v['origem'] !== undefined && !origemValida(v['origem'])) return null;
    if (v['iniciais'] !== undefined && !camposValidos(v['iniciais'])) return null;
    if (!intencaoValida(v['intencao']) || !contextoValido(v['contexto'])) return null;
    const { intencao, contexto } = v;
    if ((contexto.tipo === 'fazenda') !== (intencao.targetType === 'farm')) return null;
    if ((contexto.tipo === 'situacao') !== (intencao.commandType === COMANDOS_CADASTRO.alterarSituacaoTalhao))
      return null;
    if (typeof v['criadaEm'] !== 'string' || !Number.isFinite(Date.parse(v['criadaEm']))) return null;
    return {
      campos: v['campos'],
      ...(v['falha'] === undefined ? {} : { falha: v['falha'] }),
      ...(v['origem'] === undefined ? {} : { origem: v['origem'] }),
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
function lerTodasIntencoes(
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

/** Leitura específica antes de qualquer transição: estado de outra aba tem precedência sobre a fotografia da UI. */
export function lerIntencao(
  armazem: Pick<Storage, 'getItem'> | null,
  usuarioId: string,
  organizacaoId: string,
  chave: string,
): IntencaoGuardada | null {
  try {
    const bruto = armazem?.getItem(prefixoDasIntencoes(usuarioId, organizacaoId) + chave);
    const g = bruto ? lerGuardada(bruto) : null;
    return g?.intencao.chave === chave ? g : null;
  } catch {
    return null;
  }
}
export function raizDaIntencao(g: IntencaoGuardada): string {
  return g.origem?.raiz ?? g.intencao.chave;
}
export function lerIntencoes(
  armazem: Varredura | null,
  usuarioId: string,
  organizacaoId: string,
): IntencaoGuardada[] {
  const todas = lerTodasIntencoes(armazem, usuarioId, organizacaoId);
  // Uma correção já preparada passa a ser a retomada do fluxo, mesmo se o navegador fechou antes do POST.
  return todas.filter(
    (g) =>
      !todas.some(
        (filha) =>
          filha.origem?.chave === g.intencao.chave &&
          filha.origem.correlacao === g.falha?.correlacao &&
          raizDaIntencao(filha) === raizDaIntencao(g),
      ),
  );
}
export function atualDoFluxo(
  armazem: Varredura | null,
  usuarioId: string,
  organizacaoId: string,
  g: IntencaoGuardada,
): IntencaoGuardada | null {
  const atuais = lerIntencoes(armazem, usuarioId, organizacaoId).filter(
    (x) => raizDaIntencao(x) === raizDaIntencao(g),
  );
  // Mais de uma folha indica conflito local: não escolher arbitrariamente qual pedido enviar.
  return atuais.length === 1 ? (atuais[0] ?? null) : null;
}

/** Deve executar na trava desta intenção. Nunca altera corpo, rascunho, base ou correlação já registrados. */
export function guardarFalha(
  armazem: Escrita | null,
  usuarioId: string,
  organizacaoId: string,
  g: IntencaoGuardada,
  falha: FalhaGuardada,
): IntencaoGuardada | null {
  if (!armazem || !falhaValida(falha)) return null;
  const atual = lerIntencao(armazem, usuarioId, organizacaoId, g.intencao.chave);
  if (
    !atual ||
    atual.intencao.corpo !== g.intencao.corpo ||
    atual.intencao.commandType !== g.intencao.commandType
  )
    return null;
  if (atual.falha) return atual;
  try {
    const nova = { ...atual, falha };
    const chave = prefixoDasIntencoes(usuarioId, organizacaoId) + g.intencao.chave;
    const bruto = JSON.stringify(nova);
    armazem.setItem(chave, bruto);
    return armazem.getItem(chave) === bruto ? nova : null;
  } catch {
    return null;
  }
}

export type PreparoCorrecao =
  | { readonly tipo: 'nova' | 'existente'; readonly guardada: IntencaoGuardada }
  | { readonly tipo: 'impedido'; readonly mensagem: string };
/** Trava por origem protege duas abas que tentem criar chaves diferentes para a mesma correção. */
export function prepararCorrecao(
  armazem: (Escrita & Varredura) | null,
  usuarioId: string,
  organizacaoId: string,
  origem: IntencaoGuardada,
  candidata: IntencaoGuardada,
): PreparoCorrecao {
  const atual = atualDoFluxo(armazem, usuarioId, organizacaoId, origem);
  const impedido = (mensagem: string): PreparoCorrecao => ({
    tipo: 'impedido',
    mensagem,
  });
  if (!atual) return impedido('Não foi possível recuperar este envio. Reabra a lista de cadastros.');
  if (atual.intencao.chave !== origem.intencao.chave) return { tipo: 'existente', guardada: atual };
  if (atual.falha?.tipo !== 'corrigir') return impedido('Consulte o recibo antes de alterar este envio.');
  if (
    candidata.intencao.commandType !== atual.intencao.commandType ||
    candidata.intencao.targetType !== atual.intencao.targetType ||
    candidata.intencao.targetId !== atual.intencao.targetId ||
    candidata.intencao.expectedVersion !== atual.intencao.expectedVersion ||
    candidata.intencao.chave === atual.intencao.chave ||
    JSON.stringify(candidata.iniciais) !== JSON.stringify(atual.iniciais)
  )
    return impedido('A correção deve preservar o cadastro e sua versão de origem.');
  if (mesmoConteudoDeDominio(atual.intencao, candidata.intencao))
    return impedido(
      'Altere os dados recusados antes de enviar a correção. Uma chave nova não corrige o conteúdo.',
    );
  const guardada: IntencaoGuardada = {
    ...candidata,
    origem: {
      chave: atual.intencao.chave,
      raiz: raizDaIntencao(atual),
      correlacao: atual.falha.correlacao,
    },
  };
  if (
    lerIntencao(armazem, usuarioId, organizacaoId, guardada.intencao.chave) ||
    !gravarIntencao(armazem, usuarioId, organizacaoId, guardada)
  )
    return impedido(
      'Não foi possível guardar a correção. Nada foi enviado; o pedido anterior permanece guardado.',
    );
  return { tipo: 'nova', guardada };
}

/** Ancestros são retirados primeiro; interrupção deixa o pedido mais recente consultável, nunca reabre o recusado. */
export function apagarFluxo(
  armazem: (Varredura & Pick<Storage, 'removeItem'>) | null,
  usuarioId: string,
  organizacaoId: string,
  g: IntencaoGuardada,
): boolean {
  if (!armazem) return false;
  const fluxo = lerTodasIntencoes(armazem, usuarioId, organizacaoId).filter(
    (x) => raizDaIntencao(x) === raizDaIntencao(g),
  );
  // O relógio serve só à apresentação. Remover um elo antes de seu ancestral faria o ancestral
  // reaparecer como outra folha se a limpeza fosse interrompida (ENV-UI-01-LIMPEZA, Codex).
  const porChave = new Map(fluxo.map((x) => [x.intencao.chave, x]));
  const visitadas = new Set<string>();
  const ordem: IntencaoGuardada[] = [];
  let atual: IntencaoGuardada | undefined = porChave.get(g.intencao.chave) ?? g;
  while (atual) {
    if (visitadas.has(atual.intencao.chave)) return false;
    visitadas.add(atual.intencao.chave);
    ordem.push(atual);
    atual = atual.origem ? porChave.get(atual.origem.chave) : undefined;
  }
  if (fluxo.some((x) => !visitadas.has(x.intencao.chave))) return false;
  try {
    for (const x of ordem.reverse()) {
      const chave = prefixoDasIntencoes(usuarioId, organizacaoId) + x.intencao.chave;
      armazem.removeItem(chave);
      if (armazem.getItem(chave) !== null) return false;
    }
    return true;
  } catch {
    return false;
  }
}

/** Web Locks é específico deste fluxo CAD; sem ele não há garantia contra duas correções com chaves novas. */
export async function comTravaCadastro<T>(
  travas: Pick<LockManager, 'request'> | undefined,
  usuarioId: string,
  organizacaoId: string,
  g: IntencaoGuardada,
  executar: () => Promise<T>,
): Promise<T> {
  if (!travas)
    throw new Error(
      'Este navegador não oferece a trava necessária para enviar com segurança. Use um navegador compatível.',
    );
  return travas.request(prefixoDasIntencoes(usuarioId, organizacaoId) + raizDaIntencao(g), executar);
}
