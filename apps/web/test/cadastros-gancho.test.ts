// DECISAO-RECUPERACAO-C2-20261003: as decisões que vivem no gancho e nas telas, com o código real de useCadastroComando,
// EditorCadastro, AreasCadastro e DetalheCadastro. Não há DOM: um executor mínimo de hooks (useState, useRef e useId)
// chama os componentes como funções; os elementos devolvidos são inspecionados e os manipuladores, chamados direto.
// Storage, Web Locks e fetch são simulados. A ordem entre "abas" vem de promessas controladas, nunca de relógio.
import { COMANDOS_CADASTRO as C, erroContrato, type ReciboContrato } from '@safrion/contracts';
import { isValidElement } from 'react';
import { afterEach, describe, expect, it, vi } from 'vitest';

const H = vi.hoisted(() => {
  interface Instancia {
    slots: unknown[];
    i: number;
    /** Atualizações feitas durante a renderização em curso. */
    mudancas: number;
  }
  let atual: Instancia | null = null;
  const emRender = (): Instancia => {
    if (!atual) throw new Error('hook fora da renderização');
    return atual;
  };
  const roteador = {
    destinos: [] as string[],
    push: (d: string) => roteador.destinos.push(d),
    refresh: () => undefined,
  };
  return {
    roteador,
    instancia: (): Instancia => ({ slots: [], i: 0, mudancas: 0 }),
    /** Renderiza até estabilizar: um setState durante a renderização a refaz, como no React. */
    renderizar<T>(x: Instancia, f: () => T): T {
      for (let n = 0; n < 20; n += 1) {
        atual = x;
        x.i = 0;
        const antes = x.mudancas;
        let r: T;
        try {
          r = f();
        } finally {
          atual = null;
        }
        if (x.mudancas === antes) return r;
      }
      throw new Error('renderização sem fim');
    },
    useState: (inicial: unknown) => {
      const x = emRender();
      const i = x.i;
      x.i += 1;
      if (i === x.slots.length)
        x.slots.push(typeof inicial === 'function' ? (inicial as () => unknown)() : inicial);
      const definir = (v: unknown) => {
        const novo = typeof v === 'function' ? (v as (a: unknown) => unknown)(x.slots[i]) : v;
        if (Object.is(novo, x.slots[i])) return;
        x.slots[i] = novo;
        if (atual === x) x.mudancas += 1;
      };
      return [x.slots[i], definir];
    },
    useRef: (inicial: unknown) => {
      const x = emRender();
      const i = x.i;
      x.i += 1;
      if (i === x.slots.length) x.slots.push({ current: inicial });
      return x.slots[i];
    },
    useId: () => {
      const x = emRender();
      const i = x.i;
      x.i += 1;
      if (i === x.slots.length) x.slots.push(`:t${String(i)}:`);
      return x.slots[i];
    },
  };
});
vi.mock('react', async (original) => ({
  ...(await original<typeof import('react')>()),
  useState: H.useState,
  useRef: H.useRef,
  useId: H.useId,
}));
vi.mock('next/navigation', () => ({ useRouter: () => H.roteador }));
vi.mock('next/link', () => ({ default: 'a' }));

import type { TalhaoDetalhe } from '@safrion/db/web';
import { AreasCadastro } from '../src/cadastros/AreasCadastro';
import { DetalheCadastro } from '../src/cadastros/DetalheCadastro';
import { EditorCadastro, type EdicaoCadastro } from '../src/cadastros/EditorCadastro';
import { EnviosCadastro } from '../src/cadastros/EnviosCadastro';
import { novaIntencao, type Intencao } from '../src/cadastros/intencao';
import { ListaAreas } from '../src/cadastros/ListaAreas';
import {
  gravarIntencao,
  guardarFalha,
  lerIntencao,
  lerIntencoes,
  prefixoDasIntencoes,
  type FalhaGuardada,
  type IntencaoGuardada,
} from '../src/cadastros/pendencias';
import { useCadastroComando } from '../src/cadastros/useCadastroComando';

const u = 'usuario',
  o = 'org';
const F1 = '11111111-1111-4111-8111-111111111111';
const X = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
const Y = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
const ids = new Map<string, string>();
function idDe(chave: string): string {
  const id = ids.get(chave) ?? `eeeeeeee-eeee-4eee-8eee-${String(ids.size + 1).padStart(12, '0')}`;
  ids.set(chave, id);
  return id;
}

// ——— Dados ———
const recusa = (correlacao = 'cl22'): FalhaGuardada => ({
  tipo: 'corrigir',
  mensagem: 'Nada foi gravado.',
  correlacao,
});
const PERMANENTE = erroContrato('FALHA_INTERNA', 'Nada foi gravado.', 'cl22', {
  detalhe: { resultadoIncerto: false, repetirMesmoConteudo: false },
});
const SEM_SESSAO = erroContrato('NAO_AUTENTICADO', 'Entre de novo.', 'c401');
const AUSENTE = erroContrato('RECIBO_NAO_LOCALIZADO', 'Ausente.', 'c404');

function talhao(chave: string, nome: string, alvo = idDe(chave)): IntencaoGuardada {
  return {
    intencao: novaIntencao(
      C.criarTalhao,
      'field',
      alvo,
      0,
      { nome, fazenda: F1, areaDeclaradaHa: '10' },
      chave,
    ),
    campos: { nome, fazenda: F1, area: '10' },
    iniciais: { nome: '', fazenda: '', area: '' },
    contexto: { tipo: 'talhao', titulo: 'Criar talhão', volta: '/cadastros/areas' },
    criadaEm: '2026-10-03T00:00:00Z',
  };
}
function fazenda(chave: string, nome: string): IntencaoGuardada {
  return {
    intencao: novaIntencao(
      C.criarFazenda,
      'farm',
      idDe(chave),
      0,
      { nome, fuso: 'America/Sao_Paulo' },
      chave,
    ),
    campos: { nome, fuso: 'America/Sao_Paulo' },
    iniciais: { nome: '', fuso: 'America/Sao_Paulo' },
    contexto: { tipo: 'fazenda', titulo: 'Criar fazenda', volta: '/cadastros/areas' },
    criadaEm: '2026-10-03T00:00:00Z',
  };
}
function edicao(chave: string, alvo: string, nome: string): IntencaoGuardada {
  return {
    intencao: novaIntencao(C.editarTalhao, 'field', alvo, 1, { nome }, chave),
    campos: { nome, fazenda: F1, area: '10' },
    iniciais: { nome: 'Original', fazenda: F1, area: '10' },
    contexto: { tipo: 'talhao', titulo: 'Salvar talhão', volta: '/cadastros/areas' },
    criadaEm: '2026-10-03T00:00:00Z',
  };
}
function situacao(chave: string, alvo = X): IntencaoGuardada {
  return {
    intencao: novaIntencao(C.alterarSituacaoTalhao, 'field', alvo, 1, { situacao: 'inativo' }, chave),
    campos: { situacao: 'inativo' },
    iniciais: { situacao: 'ativo' },
    contexto: { tipo: 'situacao', titulo: 'Inativar talhão', volta: '/cadastros/areas' },
    criadaEm: '2026-10-03T00:00:00Z',
  };
}
function recibo(i: Intencao): { status: number; corpo: ReciboContrato } {
  return {
    status: 200,
    corpo: {
      receiptId: Y,
      commandType: i.commandType,
      idempotencyKey: i.chave,
      outcome: 'confirmed',
      reasonCode: null,
      targetType: i.targetType,
      targetId: i.targetId,
      expectedVersion: i.expectedVersion,
      resultingVersion: i.expectedVersion + 1,
      effects: {},
      pending: [],
      nextAction: null,
      processedAt: '2026-10-03T12:00:00Z',
      alreadyReceived: true,
    },
  };
}
function talhaoDetalhe(id: string, nome: string): TalhaoDetalhe {
  return {
    id,
    nome,
    fazenda: { id: F1, nome: 'Sede' },
    areaReferenciaHa: '10',
    origemArea: 'declarada',
    areaDeclaradaHa: '10',
    limite: null,
    situacao: 'ativo',
    versao: 1,
    criadoEm: '2026-10-01T00:00:00Z',
    atualizadoEm: null,
  };
}

// ——— Ambiente: armazenamento, travas e rede de uma "máquina" com várias abas ———
function memoria() {
  const m = new Map<string, string>();
  const estado = { gravacoesAteFalhar: Infinity };
  return {
    m,
    estado,
    get length() {
      return m.size;
    },
    key: (n: number) => [...m.keys()][n] ?? null,
    getItem: (k: string) => m.get(k) ?? null,
    setItem: (k: string, v: string) => {
      if (estado.gravacoesAteFalhar <= 0) throw new DOMException('cheio', 'QuotaExceededError');
      estado.gravacoesAteFalhar -= 1;
      m.set(k, v);
    },
    removeItem: (k: string) => {
      m.delete(k);
    },
  };
}
type Memoria = ReturnType<typeof memoria>;
type Resposta = { status: number; corpo: unknown } | 'queda';
interface Pedido {
  readonly metodo: string;
  readonly url: string;
  readonly corpo: string | null;
  /** O que estava guardado no instante do pedido. */
  readonly guardadas: Record<string, unknown>;
}

function cenario() {
  const a = memoria();
  const prefixo = prefixoDasIntencoes(u, o);
  const guardadas = () =>
    Object.fromEntries(
      [...a.m.entries()].map(([k, v]) => [k.slice(prefixo.length), JSON.parse(v) as unknown]),
    );
  // Web Locks: fila exclusiva por nome, como o navegador; registra os nomes e acompanha o que está em curso.
  const nomes: string[] = [];
  const caudas = new Map<string, Promise<unknown>>();
  const emCurso = new Set<Promise<unknown>>();
  const request = (nome: string, fn: () => Promise<unknown>) => {
    nomes.push(nome);
    const exec = (caudas.get(nome) ?? Promise.resolve()).then(fn);
    caudas.set(
      nome,
      exec.catch(() => undefined),
    );
    emCurso.add(exec);
    exec
      .finally(() => {
        emCurso.delete(exec);
      })
      .catch(() => undefined);
    return exec;
  };
  // Rede roteirizada: cada pedido consome a próxima resposta; uma função segura a resposta até ser solta.
  const pedidos: Pedido[] = [];
  const fila: (Resposta | (() => Promise<Resposta>))[] = [];
  let semRoteiro = 0;
  const fetch = async (url: string, init?: { method?: string; body?: unknown }) => {
    pedidos.push({
      metodo: init?.method ?? 'GET',
      url,
      corpo: typeof init?.body === 'string' ? init.body : null,
      guardadas: guardadas(),
    });
    const prox = fila.shift();
    if (prox === undefined) {
      semRoteiro += 1;
      throw new TypeError('sem roteiro');
    }
    const r = typeof prox === 'function' ? await prox() : prox;
    if (r === 'queda') throw new TypeError('Failed to fetch');
    return { status: r.status, json: () => Promise.resolve(r.corpo) };
  };
  vi.stubGlobal('window', { localStorage: a, location: { search: '' } });
  vi.stubGlobal('navigator', { locks: { request } });
  vi.stubGlobal('fetch', fetch);
  return {
    a,
    nomes,
    pedidos,
    fila,
    guardadas,
    semRoteiro: () => semRoteiro,
    posts: () => pedidos.filter((p) => p.metodo === 'POST'),
    /** Espera as travas soltarem e o fim do que o gancho faz depois delas. */
    async ocioso() {
      while (emCurso.size) await Promise.allSettled([...emCurso]);
      await new Promise((r) => setImmediate(r));
    },
    async ate(condicao: () => boolean) {
      for (let n = 0; n < 200 && !condicao(); n += 1) await new Promise((r) => setImmediate(r));
      if (!condicao()) throw new Error('condição não alcançada');
    },
  };
}
afterEach(() => {
  vi.unstubAllGlobals();
  H.roteador.destinos.length = 0;
});

function guardar(a: Memoria, g: IntencaoGuardada, falha?: FalhaGuardada): IntencaoGuardada {
  if (!gravarIntencao(a, u, o, g)) throw new Error('não gravou');
  if (!falha) return g;
  const salva = guardarFalha(a, u, o, g, falha);
  if (!salva) throw new Error('falha não persistida');
  return salva;
}
/** Uma aba com o gancho montado; `ler` renderiza e devolve o estado atual. */
function aba(inicial?: IntencaoGuardada) {
  const x = H.instancia();
  const confirmados: IntencaoGuardada[] = [];
  return {
    confirmados,
    ler: () =>
      H.renderizar(x, () =>
        useCadastroComando(
          u,
          o,
          (_r, g) => {
            confirmados.push(g);
          },
          inicial,
        ),
      ),
  };
}

// ——— Árvore de elementos ———
interface Elemento {
  readonly type: unknown;
  readonly props: Record<string, unknown>;
}
function elementos(no: unknown): Elemento[] {
  const todos: Elemento[] = [];
  const visitar = (x: unknown) => {
    if (Array.isArray(x)) {
      x.forEach(visitar);
      return;
    }
    if (!isValidElement(x)) return;
    const e = x as unknown as Elemento;
    todos.push(e);
    visitar(e.props['children']);
  };
  visitar(no);
  return todos;
}
function texto(no: unknown): string {
  if (typeof no === 'string' || typeof no === 'number') return String(no);
  if (Array.isArray(no)) return no.map(texto).join('');
  return isValidElement(no) ? texto((no as unknown as Elemento).props['children']) : '';
}
const botoes = (arvore: unknown) =>
  elementos(arvore)
    .filter((e) => e.type === 'button')
    .map((e) => texto(e.props['children']));
function clicar(arvore: unknown, nome: string) {
  const b = elementos(arvore).find((e) => e.type === 'button' && texto(e.props['children']) === nome);
  if (!b) throw new Error(`botão ausente: ${nome}; há ${botoes(arvore).join(' | ')}`);
  (b.props['onClick'] as () => void)();
}
function componente(arvore: unknown, tipo: unknown): Record<string, unknown> {
  const e = elementos(arvore).find((x) => x.type === tipo);
  if (!e) throw new Error('componente ausente');
  return e.props;
}
function editor(inicial: IntencaoGuardada, edicao: EdicaoCadastro) {
  const x = H.instancia();
  return () =>
    H.renderizar(x, () =>
      EditorCadastro({
        edicao,
        fazendas: [{ id: F1, nome: 'Sede', fuso: 'America/Sao_Paulo' }],
        usuarioId: u,
        organizacaoId: o,
        volta: '/cadastros/areas',
        confirmado: () => undefined,
        cancelar: () => undefined,
        inicial,
      }),
    );
}

describe('§2 no gancho: certeza de recusa antes do envelope e tentativas', () => {
  it('401 contratual do primeiro envio marca; o reenvio retira a marca antes do POST e uma queda reabre incerteza', async () => {
    const c = cenario();
    const g = talhao('a', 'Talhão A');
    const t = aba();
    c.fila.push({ status: SEM_SESSAO.status, corpo: SEM_SESSAO.corpo });
    t.ler().enviar(g);
    await c.ocioso();
    expect(lerIntencao(c.a, u, o, 'a')).toEqual({ ...g, antesDoEnvelope: true });
    expect(t.ler()).toMatchObject({ sessao: true, pendente: { antesDoEnvelope: true } });
    c.fila.push({ status: AUSENTE.status, corpo: AUSENTE.corpo });
    await t.ler().consultar();
    expect(t.ler().naoLocalizado).toBe(true);
    c.fila.push('queda');
    t.ler().repetir();
    await c.ocioso();
    const [p1, p2] = c.posts();
    // No instante do segundo POST, a certeza já tinha saído e a nova tentativa estava gravada.
    expect(p2?.guardadas).toEqual({ a: { ...g, tentativas: 2 } });
    expect(p2?.corpo).toBe(p1?.corpo);
    const reaberta = aba(lerIntencoes(c.a, u, o)[0]);
    expect(reaberta.ler().mensagem).toBe('Há um envio sem confirmação. Consulte o recibo para continuar.');
    expect(c.semRoteiro()).toBe(0);
  });

  it('o 401 inicial permite a recuperação correta: 404, reenvio como primeiro e 500 permanente pede correção', async () => {
    const c = cenario();
    const g = talhao('a', 'Talhão A');
    const t = aba();
    c.fila.push({ status: SEM_SESSAO.status, corpo: SEM_SESSAO.corpo });
    t.ler().enviar(g);
    await c.ocioso();
    c.fila.push({ status: AUSENTE.status, corpo: AUSENTE.corpo });
    await t.ler().consultar();
    c.fila.push({ status: PERMANENTE.status, corpo: PERMANENTE.corpo });
    t.ler().repetir();
    await c.ocioso();
    expect(lerIntencao(c.a, u, o, 'a')?.falha?.tipo).toBe('corrigir');
    expect(t.ler()).toMatchObject({ corrigivel: true, correlacao: 'cl22' });
    expect(c.posts().map((p) => p.corpo)).toEqual([g.intencao.corpo, g.intencao.corpo]);
  });

  it('401 depois de incerteza não marca; o 500 seguinte só bloqueia e o recibo tardio ainda encerra (§4)', async () => {
    const c = cenario();
    const g = talhao('a', 'Talhão A');
    const t = aba();
    c.fila.push('queda', { status: AUSENTE.status, corpo: AUSENTE.corpo });
    t.ler().enviar(g);
    await c.ocioso();
    await t.ler().consultar();
    c.fila.push({ status: SEM_SESSAO.status, corpo: SEM_SESSAO.corpo });
    t.ler().repetir();
    await c.ocioso();
    expect(lerIntencao(c.a, u, o, 'a')).toEqual({ ...g, tentativas: 2 });
    expect(t.ler().sessao).toBe(true);
    c.fila.push({ status: AUSENTE.status, corpo: AUSENTE.corpo });
    await t.ler().consultar();
    c.fila.push({ status: PERMANENTE.status, corpo: PERMANENTE.corpo });
    t.ler().repetir();
    await c.ocioso();
    expect(lerIntencao(c.a, u, o, 'a')?.falha?.tipo).toBe('somente_consulta');
    expect(t.ler()).toMatchObject({ corrigivel: false, encerravel: false });
    // somente_consulta não se encerra, nem chamando o gancho direto.
    await t.ler().encerrar();
    expect(lerIntencoes(c.a, u, o)).toHaveLength(1);
    c.fila.push(recibo(g.intencao));
    await t.ler().consultar();
    expect(c.a.m.size).toBe(0);
    expect(t.confirmados).toHaveLength(1);
    expect(c.posts()).toHaveLength(3);
  });

  it('sem gravar a nova tentativa, nada é enviado: nem o reenvio marcado, nem a repetição incerta', async () => {
    const c = cenario();
    const g = talhao('a', 'Talhão A');
    const t = aba();
    c.fila.push({ status: SEM_SESSAO.status, corpo: SEM_SESSAO.corpo });
    t.ler().enviar(g);
    await c.ocioso();
    c.fila.push({ status: AUSENTE.status, corpo: AUSENTE.corpo });
    await t.ler().consultar();
    c.a.estado.gravacoesAteFalhar = 0;
    t.ler().repetir();
    await c.ocioso();
    expect(c.posts()).toHaveLength(1);
    expect(t.ler().mensagem).toContain('Não foi possível preparar o reenvio com segurança');
    expect(lerIntencao(c.a, u, o, 'a')).toEqual({ ...g, antesDoEnvelope: true });
    // Com o armazenamento de volta, o reenvio segue; caído, o seguinte é repetição e também exige a gravação.
    c.a.estado.gravacoesAteFalhar = Infinity;
    c.fila.push({ status: AUSENTE.status, corpo: AUSENTE.corpo }, 'queda', {
      status: AUSENTE.status,
      corpo: AUSENTE.corpo,
    });
    await t.ler().consultar();
    t.ler().repetir();
    await c.ocioso();
    await t.ler().consultar();
    c.a.estado.gravacoesAteFalhar = 0;
    t.ler().repetir();
    await c.ocioso();
    expect(c.posts()).toHaveLength(2);
    expect(lerIntencao(c.a, u, o, 'a')).toEqual({ ...g, tentativas: 2 });
  });
});

describe('§3 no gancho: encerrar só o que foi recusado sem gravação e sem tentativa incerta', () => {
  /** Fazenda criada com 401, 404 e reenvio com 500 permanente cuja falha a aba não consegue guardar. */
  async function recusaSoNaMemoria() {
    const c = cenario();
    const g = fazenda('q', 'Quinta');
    const abaA = aba();
    c.fila.push({ status: SEM_SESSAO.status, corpo: SEM_SESSAO.corpo });
    abaA.ler().enviar(g);
    await c.ocioso();
    c.fila.push({ status: AUSENTE.status, corpo: AUSENTE.corpo });
    await abaA.ler().consultar();
    c.a.estado.gravacoesAteFalhar = 1; // a nova tentativa grava; a falha, não
    c.fila.push({ status: PERMANENTE.status, corpo: PERMANENTE.corpo });
    abaA.ler().repetir();
    await c.ocioso();
    expect(abaA.ler()).toMatchObject({ falhaDePersistencia: true, encerravel: false, corrigivel: false });
    expect(lerIntencao(c.a, u, o, 'q')).toEqual({ ...g, tentativas: 2 });
    return { c, g, abaA };
  }

  it('"Guardar recuperação" depois da tentativa incerta de outra aba volta só como somente_consulta', async () => {
    const { c, g, abaA } = await recusaSoNaMemoria();
    // O armazenamento volta; a aba A ainda não guardou a recusa, e a aba B vê o envio sem confirmação.
    c.a.estado.gravacoesAteFalhar = Infinity;
    const abaB = aba(lerIntencoes(c.a, u, o)[0]);
    c.fila.push({ status: AUSENTE.status, corpo: AUSENTE.corpo }, 'queda');
    await abaB.ler().consultar();
    abaB.ler().repetir();
    await c.ocioso();
    expect(lerIntencao(c.a, u, o, 'q')).toEqual({ ...g, tentativas: 3 });
    c.fila.push({ status: AUSENTE.status, corpo: AUSENTE.corpo });
    await abaA.ler().consultar();
    expect(lerIntencao(c.a, u, o, 'q')?.falha).toEqual({
      tipo: 'somente_consulta',
      mensagem: 'Nada foi gravado.',
      correlacao: 'cl22',
    });
    expect(abaA.ler()).toMatchObject({ falhaDePersistencia: false, encerravel: false, corrigivel: false });
    await abaA.ler().encerrar();
    expect(lerIntencoes(c.a, u, o)).toHaveLength(1);
    expect(c.pedidos.map((p) => p.metodo)).toEqual(['POST', 'GET', 'POST', 'GET', 'POST', 'GET']);
  });

  it('sem outra tentativa, a recusa guardada depois continua corrigível e encerrável', async () => {
    const { c, abaA } = await recusaSoNaMemoria();
    c.a.estado.gravacoesAteFalhar = Infinity;
    await abaA.ler().consultar();
    expect(lerIntencao(c.a, u, o, 'q')?.falha?.tipo).toBe('corrigir');
    expect(abaA.ler()).toMatchObject({ falhaDePersistencia: false, corrigivel: true, encerravel: true });
    expect(c.pedidos).toHaveLength(3);
  });

  it('situação recusada: sem "Corrigir"; o encerramento não usa a rede e deixa a correlação à vista', async () => {
    const c = cenario();
    const s = guardar(c.a, situacao('s1'), recusa('cl22-sit'));
    const t = aba(s);
    expect(t.ler()).toMatchObject({ corrigivel: false, encerravel: true });
    await t.ler().encerrar();
    expect(c.pedidos).toHaveLength(0);
    expect(c.a.m.size).toBe(0);
    expect(t.ler()).toMatchObject({ encerrado: true, pendente: null, correlacao: 'cl22-sit' });
  });

  it('a aba velha não apaga a correção incerta que outra aba tem em voo', async () => {
    const c = cenario();
    const raiz = guardar(c.a, edicao('r', X, 'Um'), recusa('c1'));
    const abaB = aba(raiz);
    const abaA = aba(raiz);
    let soltar: (r: Resposta) => void = () => undefined;
    c.fila.push(
      () =>
        new Promise<Resposta>((r) => {
          soltar = r;
        }),
    );
    abaB.ler().enviar(edicao('r2', X, 'Dois'));
    await c.ate(() => c.posts().length === 1);
    const fim = abaA.ler().encerrar();
    expect(Object.keys(c.guardadas()).sort()).toEqual(['r', 'r2']);
    soltar('queda');
    await fim;
    await c.ocioso();
    expect(Object.keys(c.guardadas()).sort()).toEqual(['r', 'r2']);
    expect(abaA.ler().mensagem).toBe(
      'Este pedido mudou em outra aba. Nada foi encerrado; confira o envio atual.',
    );
    expect(abaA.ler().pendente?.intencao.chave).toBe('r2');
  });
});

describe('§1 no gancho: a guarda do mesmo cadastro, inclusive pela correção', () => {
  it('pedido novo equivalente a uma criação pendente não sai; outro talhão sai e a pendência fica intacta', async () => {
    const c = cenario();
    const azul = guardar(c.a, talhao('b', 'Talhão Azul'));
    const t = aba();
    t.ler().enviar(talhao('n', '  talhão   AZUL '));
    await c.ocioso();
    expect(c.posts()).toHaveLength(0);
    expect(t.ler().mensagem).toBe(
      'Já existe um envio pendente para este cadastro (Talhão Azul). Nada foi enviado. Volte e abra-o em Retomar cadastros.',
    );
    expect(c.nomes).toContain(`${prefixoDasIntencoes(u, o)}alvo:${C.criarTalhao}`);
    const verde = talhao('v', 'Talhão Verde');
    const outra = aba();
    c.fila.push(recibo(verde.intencao));
    outra.ler().enviar(verde);
    await c.ocioso();
    expect(c.posts()).toHaveLength(1);
    expect(outra.confirmados).toEqual([verde]);
    expect(lerIntencoes(c.a, u, o)).toEqual([azul]);
  });

  it('a correção para o nome de outra criação pendente não sai; para outro nome, sai', async () => {
    const c = cenario();
    guardar(c.a, talhao('b', 'Talhão Azul'));
    const verde = guardar(c.a, talhao('c', 'Talhão Verde'), recusa('c-verde'));
    const t = aba(verde);
    t.ler().enviar(talhao('c2', 'Talhão Azul', verde.intencao.targetId));
    await c.ocioso();
    expect(c.posts()).toHaveLength(0);
    expect(t.ler().mensagem).toContain('Já existe um envio pendente para este cadastro (Talhão Azul)');
    expect(Object.keys(c.guardadas()).sort()).toEqual(['b', 'c']);
    // Dentro da trava do fluxo do pedido recusado, a correção toma a trava do alvo, como um pedido novo.
    const p = prefixoDasIntencoes(u, o);
    expect(c.nomes).toEqual([`${p}c`, `${p}alvo:${C.criarTalhao}`]);
    c.fila.push('queda');
    t.ler().enviar(talhao('c3', 'Talhão Roxo', verde.intencao.targetId));
    await c.ocioso();
    expect(c.posts()).toHaveLength(1);
    expect(Object.keys(c.guardadas()).sort()).toEqual(['b', 'c', 'c3']);
  });
});

describe('telas: isolamento da pendência e ações oferecidas', () => {
  it('"Novo talhão" abre o formulário vazio com uma pendência guardada; a pendência abre pela lista', () => {
    const c = cenario();
    const a = guardar(c.a, fazenda('fa', 'Fazenda A'), {
      tipo: 'somente_consulta',
      mensagem: 'Incerto.',
      correlacao: 'cl22',
    });
    const x = H.instancia();
    const tela = () =>
      H.renderizar(x, () =>
        AreasCadastro({ fazendas: [], talhoes: [], podeEditar: true, usuarioId: u, organizacaoId: o }),
      );
    clicar(tela(), 'Novo talhão');
    let ed = componente(tela(), EditorCadastro);
    expect(ed['edicao']).toEqual({ tipo: 'talhao' });
    expect(ed['inicial']).toBeUndefined();
    (componente(tela(), ListaAreas)['onNovoTalhao'] as (f: string) => void)(F1);
    ed = componente(tela(), EditorCadastro);
    expect(ed['edicao']).toEqual({ tipo: 'talhao', fazenda: F1 });
    expect(ed['inicial']).toBeUndefined();
    (componente(tela(), EnviosCadastro)['abrir'] as (g: IntencaoGuardada) => void)(a);
    expect(componente(tela(), EditorCadastro)['inicial']).toEqual(a);
  });

  it('no detalhe, "Editar" de outro talhão abre limpo; o do talhão com pendência reabre a folha dele', () => {
    const c = cenario();
    const x1 = guardar(c.a, edicao('ex', X, 'X novo'));
    const detalhe = (id: string) => {
      const x = H.instancia();
      return () =>
        H.renderizar(x, () =>
          DetalheCadastro({
            usuarioId: u,
            organizacaoId: o,
            podeEditar: true,
            volta: '/cadastros/areas',
            fazendas: [],
            tipo: 'talhao',
            registro: talhaoDetalhe(id, id === X ? 'Talhão X' : 'Talhão Y'),
          }),
        );
    };
    const y = detalhe(Y);
    clicar(y(), 'Editar talhão');
    expect(componente(y(), EditorCadastro)['inicial']).toBeUndefined();
    expect(componente(y(), EditorCadastro)['edicao']).toMatchObject({ tipo: 'talhao', id: Y });
    const xs = detalhe(X);
    clicar(xs(), 'Inativar talhão');
    expect(componente(xs(), EditorCadastro)['inicial']).toEqual(x1);
  });

  it('o editor da situação recusada oferece só Voltar e Encerrar, com confirmação, e nunca "Corrigir"', () => {
    cenario();
    const s = situacao('s1');
    const tela = editor({ ...s, falha: recusa('cl22-sit') }, { tipo: 'situacao', id: X, versao: 1 });
    expect(botoes(tela())).toEqual(['Voltar', 'Encerrar pedido']);
    clicar(tela(), 'Encerrar pedido');
    expect(botoes(tela())).toEqual(['Manter pedido', 'Confirmar encerramento', 'Voltar']);
    expect(texto(tela())).toContain('cl22-sit');
    expect(texto(tela())).not.toMatch(/corrij|corrigir/i);
  });

  it('o editor oferece Corrigir no talhão recusado e só a consulta em somente_consulta', () => {
    cenario();
    const t = talhao('t1', 'Talhão T');
    const recusado = editor({ ...t, falha: recusa() }, { tipo: 'talhao' });
    expect(botoes(recusado())).toEqual([
      'Cadastrar fazenda',
      'Voltar',
      'Corrigir e enviar novo pedido',
      'Encerrar pedido',
    ]);
    const bloqueado = editor(
      { ...t, falha: { tipo: 'somente_consulta', mensagem: 'Incerto.', correlacao: 'cl22' } },
      { tipo: 'talhao' },
    );
    expect(botoes(bloqueado())).toEqual(['Cadastrar fazenda', 'Voltar', 'Consultar recibo']);
    const fieldset = elementos(bloqueado()).find((e) => e.type === 'fieldset');
    expect(fieldset?.props['disabled']).toBe(true);
  });
});
