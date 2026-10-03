import { COMANDOS_CADASTRO } from '@safrion/contracts';

import { PREFIXO } from '../estoque/rascunho';
import { intencaoValida, mesmoCadastro, mesmoConteudoDeDominio, type Intencao } from './intencao';

export interface FalhaGuardada {
  readonly tipo: 'corrigir' | 'somente_consulta';
  readonly mensagem: string;
  readonly correlacao: string;
}
export interface IntencaoGuardada {
  /** Ausência é o formato legado: envio sem confirmação, nunca prova de não gravação. */
  readonly falha?: FalhaGuardada;
  /**
   * Todas as tentativas desta chave foram recusadas antes do envelope, com a resposta contratual de sessão (401) de um
   * envio sem incerteza anterior (DECISAO-RECUPERACAO-C2-20261003 §2). É retirado e conferido antes de cada novo POST:
   * ausente, o envio volta a ser incerto.
   */
  readonly antesDoEnvelope?: true;
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
    // A certeza só vale sozinha; com qualquer outro valor ou junto de uma falha, o registro não é reaberto.
    if (v['antesDoEnvelope'] !== undefined && (v['antesDoEnvelope'] !== true || v['falha'] !== undefined))
      return null;
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
      ...(v['antesDoEnvelope'] === true ? { antesDoEnvelope: true as const } : {}),
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

/** Cópia sem a certeza de recusa anterior ao envelope; o restante do registro não muda. */
function semCerteza(g: IntencaoGuardada): IntencaoGuardada {
  const copia: { -readonly [K in keyof IntencaoGuardada]: IntencaoGuardada[K] } = { ...g };
  delete copia.antesDoEnvelope;
  return copia;
}

/** Guarda antes do POST. Falha deixa o envio bloqueado; a mesma chave nunca substitui outro pedido. */
export function gravarIntencao(
  armazem: Escrita | null,
  usuarioId: string,
  organizacaoId: string,
  guardada: IntencaoGuardada,
): boolean {
  // Guardar antes do POST registra um envio incerto; a certeza de recusa só nasce da resposta.
  if (!armazem || guardada.antesDoEnvelope) return false;
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
/** O próximo passo de cada pedido na lista: sem campo alterável (situação), uma recusa só pode ser encerrada. */
export function acaoDoPendente(g: IntencaoGuardada): string {
  if (g.falha?.tipo !== 'corrigir') return 'Consultar envio';
  return g.contexto.tipo === 'situacao' ? 'Encerrar pedido' : 'Corrigir cadastro';
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
    // Uma falha só chega depois de um POST: a certeza anterior ao envelope já não descreve esta chave.
    const nova = { ...semCerteza(atual), falha };
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

/**
 * Trava do cadastro alvo (DECISAO-RECUPERACAO-C2-20261003 §1): serializa entre abas a conferência "já há pedido deste
 * cadastro?" e a gravação do pedido novo. Edição e situação do mesmo registro dividem a trava; as criações de um tipo
 * também, porque o alvo delas só se conhece pelo conteúdo. É tomada dentro da trava do fluxo, nunca o contrário.
 */
export async function comTravaDoAlvo<T>(
  travas: Pick<LockManager, 'request'> | undefined,
  usuarioId: string,
  organizacaoId: string,
  intencao: Intencao,
  executar: () => Promise<T>,
): Promise<T> {
  if (!travas)
    throw new Error(
      'Este navegador não oferece a trava necessária para enviar com segurança. Use um navegador compatível.',
    );
  const alvo =
    intencao.expectedVersion === 0 ? intencao.commandType : `${intencao.targetType}:${intencao.targetId}`;
  return travas.request(`${prefixoDasIntencoes(usuarioId, organizacaoId)}alvo:${alvo}`, executar);
}

/** Pendência do mesmo registro (edição ou situação); a de outro alvo não impede abrir este. */
export function pendenteDoAlvo(
  armazem: Varredura | null,
  usuarioId: string,
  organizacaoId: string,
  targetType: Intencao['targetType'],
  targetId: string,
): IntencaoGuardada | null {
  return (
    lerIntencoes(armazem, usuarioId, organizacaoId).find(
      (g) => g.intencao.targetType === targetType && g.intencao.targetId === targetId,
    ) ?? null
  );
}

/** Pedido guardado do mesmo cadastro, inclusive uma criação equivalente; deve ser lido dentro de `comTravaDoAlvo`. */
export function pendenteEquivalente(
  armazem: Varredura | null,
  usuarioId: string,
  organizacaoId: string,
  intencao: Intencao,
): IntencaoGuardada | null {
  return (
    lerIntencoes(armazem, usuarioId, organizacaoId).find(
      (g) => g.intencao.chave !== intencao.chave && mesmoCadastro(g.intencao, intencao),
    ) ?? null
  );
}

export type RegistroNovo =
  | { readonly tipo: 'gravado' }
  | { readonly tipo: 'pendente'; readonly guardada: IntencaoGuardada }
  | { readonly tipo: 'falhou' };
/** Conferência e gravação do pedido novo na trava do alvo; outro pedido do mesmo cadastro impede a gravação. */
export function registrarNovoPedido(
  travas: Pick<LockManager, 'request'> | undefined,
  armazem: (Escrita & Varredura) | null,
  usuarioId: string,
  organizacaoId: string,
  g: IntencaoGuardada,
): Promise<RegistroNovo> {
  return comTravaDoAlvo(travas, usuarioId, organizacaoId, g.intencao, (): Promise<RegistroNovo> => {
    const outro = pendenteEquivalente(armazem, usuarioId, organizacaoId, g.intencao);
    if (outro) return Promise.resolve({ tipo: 'pendente', guardada: outro });
    return Promise.resolve({
      tipo: gravarIntencao(armazem, usuarioId, organizacaoId, g) ? 'gravado' : 'falhou',
    });
  });
}

/**
 * Deve executar na trava do fluxo, logo após a resposta contratual de sessão (401) a um envio sem incerteza anterior.
 * Falha de gravação ou leitura deixa o registro como estava: incerto, que é o lado seguro.
 */
export function marcarRecusaAntesDoEnvelope(
  armazem: Escrita | null,
  usuarioId: string,
  organizacaoId: string,
  g: IntencaoGuardada,
): IntencaoGuardada | null {
  if (!armazem) return null;
  const atual = lerIntencao(armazem, usuarioId, organizacaoId, g.intencao.chave);
  if (
    !atual ||
    atual.falha ||
    atual.intencao.corpo !== g.intencao.corpo ||
    atual.intencao.commandType !== g.intencao.commandType
  )
    return null;
  if (atual.antesDoEnvelope) return atual;
  try {
    const nova: IntencaoGuardada = { ...atual, antesDoEnvelope: true };
    const chave = prefixoDasIntencoes(usuarioId, organizacaoId) + g.intencao.chave;
    const bruto = JSON.stringify(nova);
    armazem.setItem(chave, bruto);
    return armazem.getItem(chave) === bruto ? nova : null;
  } catch {
    return null;
  }
}

export type PreparoEnvio =
  | { readonly tipo: 'primeiro' | 'repeticao'; readonly guardada: IntencaoGuardada }
  | { readonly tipo: 'impedido'; readonly mensagem: string };
/**
 * Antes de cada novo POST da mesma chave, na trava do fluxo. Com a certeza de recusa anterior, ela é retirada e
 * conferida por releitura ANTES do envio: uma queda durante ou depois do POST reabre incerteza, nunca a recusa antiga.
 * Se a gravação falha, nada é enviado.
 */
export function prepararNovoEnvio(
  armazem: Escrita | null,
  usuarioId: string,
  organizacaoId: string,
  g: IntencaoGuardada,
): PreparoEnvio {
  const atual = armazem ? lerIntencao(armazem, usuarioId, organizacaoId, g.intencao.chave) : null;
  if (
    !armazem ||
    !atual ||
    atual.intencao.corpo !== g.intencao.corpo ||
    atual.intencao.commandType !== g.intencao.commandType
  )
    return {
      tipo: 'impedido',
      mensagem: 'Este envio mudou em outra aba ou não está disponível. Reabra a lista de cadastros.',
    };
  if (atual.falha)
    return { tipo: 'impedido', mensagem: 'Este conteúdo não pode ser reenviado; consulte o recibo.' };
  if (!atual.antesDoEnvelope) return { tipo: 'repeticao', guardada: atual };
  const incerta = semCerteza(atual);
  try {
    const chave = prefixoDasIntencoes(usuarioId, organizacaoId) + g.intencao.chave;
    const bruto = JSON.stringify(incerta);
    armazem.setItem(chave, bruto);
    if (armazem.getItem(chave) === bruto) return { tipo: 'primeiro', guardada: incerta };
  } catch {
    // Cai no impedimento abaixo: sem a certeza retirada, não há POST.
  }
  return {
    tipo: 'impedido',
    mensagem:
      'Não foi possível preparar o reenvio com segurança. Nada foi enviado; libere armazenamento e tente de novo.',
  };
}

export type Encerramento =
  | { readonly tipo: 'encerrado'; readonly correlacoes: readonly string[] }
  | { readonly tipo: 'mudou'; readonly guardada: IntencaoGuardada }
  | { readonly tipo: 'impedido'; readonly mensagem: string };
/**
 * Encerra o pedido local (DECISAO-RECUPERACAO-C2-20261003 §3), na trava do fluxo e sem rede. Só quando a folha relida
 * é a mesma que a tela mostra e todo o fluxo foi recusado com certeza sem gravação ("corrigir", que só nasce de um envio
 * sem incerteza anterior). Uma sucessora preparada em outra aba, uma pendência incerta ou "somente_consulta" (§4) nunca
 * são removidas. A remoção reaproveita a limpeza causal de C2: interrompida, deixa a folha consultável.
 */
export function encerrarPedido(
  armazem: (Varredura & Pick<Storage, 'removeItem'>) | null,
  usuarioId: string,
  organizacaoId: string,
  g: IntencaoGuardada,
): Encerramento {
  const atual = atualDoFluxo(armazem, usuarioId, organizacaoId, g);
  if (!atual)
    return {
      tipo: 'impedido',
      mensagem: 'Não foi possível recuperar este pedido. Reabra a lista de cadastros.',
    };
  if (atual.intencao.chave !== g.intencao.chave) return { tipo: 'mudou', guardada: atual };
  const fluxo = lerTodasIntencoes(armazem, usuarioId, organizacaoId).filter(
    (x) => raizDaIntencao(x) === raizDaIntencao(atual),
  );
  if (atual.falha?.tipo !== 'corrigir' || fluxo.some((x) => x.falha?.tipo !== 'corrigir'))
    return {
      tipo: 'impedido',
      mensagem: 'Só um pedido recusado sem gravação pode ser encerrado. Consulte o recibo deste envio.',
    };
  // Raiz → folha, para o suporte; um ciclo corrompido para aqui e a limpeza abaixo o recusa.
  const correlacoes: string[] = [];
  const vistas = new Set<string>();
  for (let x: IntencaoGuardada | undefined = atual; x && !vistas.has(x.intencao.chave);) {
    vistas.add(x.intencao.chave);
    if (x.falha) correlacoes.unshift(x.falha.correlacao);
    const origem: string | undefined = x.origem?.chave;
    x = origem === undefined ? undefined : fluxo.find((y) => y.intencao.chave === origem);
  }
  if (!apagarFluxo(armazem, usuarioId, organizacaoId, atual))
    return {
      tipo: 'impedido',
      mensagem: 'Não foi possível encerrar agora. O pedido continua guardado; tente de novo.',
    };
  return { tipo: 'encerrado', correlacoes };
}
