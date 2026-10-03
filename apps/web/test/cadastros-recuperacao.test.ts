// DECISAO-RECUPERACAO-C2-20261003 (Codex/Claude/Gemini): uma regressão por decisão, só com Storage e LockManager
// simulados. Sem relógio, rede ou navegador; a jornada com React e Web Locks reais fica na contraprova de navegador.
import { COMANDOS_CADASTRO as C, erroContrato, type ReciboContrato } from '@safrion/contracts';
import { describe, expect, it } from 'vitest';

import {
  desfechoDaConsulta,
  desfechoDoEnvio,
  mesmoCadastro,
  novaIntencao,
  type Intencao,
} from '../src/cadastros/intencao';
import {
  acaoDoPendente,
  comTravaDoAlvo,
  encerrarPedido,
  gravarIntencao,
  guardarFalha,
  lerIntencao,
  lerIntencoes,
  marcarRecusaAntesDoEnvelope,
  pendenteDoAlvo,
  pendenteEquivalente,
  prefixoDasIntencoes,
  prepararCorrecao,
  prepararNovoEnvio,
  registrarNovoPedido,
  type FalhaGuardada,
  type IntencaoGuardada,
} from '../src/cadastros/pendencias';

const u = 'usuario',
  o = 'org';
const F1 = '11111111-1111-4111-8111-111111111111';
const F2 = '22222222-2222-4222-8222-222222222222';
const X = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
const Y = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
/** Alvo novo de cada criação, estável por chave: duas criações só coincidem pelo conteúdo, nunca pelo id. */
const ids = new Map<string, string>();
function idDe(chave: string): string {
  const id = ids.get(chave) ?? `dddddddd-dddd-4ddd-8ddd-${String(ids.size + 1).padStart(12, '0')}`;
  ids.set(chave, id);
  return id;
}
const recusa = (correlacao = 'cl22'): FalhaGuardada => ({
  tipo: 'corrigir',
  mensagem: 'Nada foi gravado.',
  correlacao,
});
const incerta = (correlacao = 'cl22'): FalhaGuardada => ({
  tipo: 'somente_consulta',
  mensagem: 'Resultado anterior incerto.',
  correlacao,
});
const PERMANENTE = erroContrato('FALHA_INTERNA', 'Nada foi gravado.', 'cl22', {
  detalhe: { resultadoIncerto: false, repetirMesmoConteudo: false },
});
const SEM_SESSAO = erroContrato('NAO_AUTENTICADO', 'Entre de novo.', 'c401');

function memoria() {
  const m = new Map<string, string>();
  return {
    m,
    get length() {
      return m.size;
    },
    key: (n: number) => [...m.keys()][n] ?? null,
    getItem: (k: string) => m.get(k) ?? null,
    setItem: (k: string, v: string) => {
      m.set(k, v);
    },
    removeItem: (k: string) => {
      m.delete(k);
    },
  };
}
type Memoria = ReturnType<typeof memoria>;

function talhao(chave: string, nome: string, fazenda = F1, area = '10'): IntencaoGuardada {
  return {
    intencao: novaIntencao(
      C.criarTalhao,
      'field',
      idDe(chave),
      0,
      { nome, fazenda, areaDeclaradaHa: area },
      chave,
    ),
    campos: { nome, fazenda, area },
    iniciais: { nome: '', fazenda: '', area: '' },
    contexto: { tipo: 'talhao', titulo: 'Criar talhão', volta: '/cadastros/areas' },
    criadaEm: '2026-10-03T00:00:00Z',
  };
}
function fazenda(chave: string, nome: string, id = idDe(chave)): IntencaoGuardada {
  return {
    intencao: novaIntencao(C.criarFazenda, 'farm', id, 0, { nome, fuso: 'America/Sao_Paulo' }, chave),
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
function guardar(a: Memoria, g: IntencaoGuardada, falha?: FalhaGuardada): IntencaoGuardada {
  if (!gravarIntencao(a, u, o, g)) throw new Error('não gravou');
  if (!falha) return g;
  const salva = guardarFalha(a, u, o, g, falha);
  if (!salva) throw new Error('falha não persistida');
  return salva;
}
function recibo(i: Intencao): ReciboContrato {
  return {
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
  };
}
/** LockManager simulado: fila por nome, como em cadastros-permanente.test.ts; registra os nomes pedidos. */
function travas() {
  const nomes: string[] = [];
  const caudas = new Map<string, Promise<unknown>>();
  const lock = {
    request: ((nome: string, fn: () => Promise<unknown>) => {
      nomes.push(nome);
      const exec = (caudas.get(nome) ?? Promise.resolve()).then(fn);
      caudas.set(
        nome,
        exec.catch(() => undefined),
      );
      return exec;
    }) as LockManager['request'],
  };
  return { lock, nomes };
}
const chaves = (a: Memoria) => [...a.m.keys()].map((k) => k.slice(prefixoDasIntencoes(u, o).length)).sort();

describe('DECISAO-RECUPERACAO-C2-20261003 §1: pendência isolada no próprio alvo', () => {
  it('a pendência de outro alvo não é reaberta; a do mesmo registro é, já como a folha do fluxo', () => {
    const a = memoria();
    guardar(a, fazenda('fazenda-a', 'Fazenda incerta'), incerta());
    const original = guardar(a, edicao('edicao-x', X, 'X novo'), recusa());
    expect(pendenteDoAlvo(a, u, o, 'field', Y)).toBeNull();
    expect(pendenteDoAlvo(a, u, o, 'farm', F1)).toBeNull();
    expect(pendenteDoAlvo(a, u, o, 'field', X)).toEqual(original);
    const p = prepararCorrecao(a, u, o, original, edicao('edicao-x-2', X, 'X corrigido'));
    if (p.tipo !== 'nova') throw new Error(p.tipo);
    expect(pendenteDoAlvo(a, u, o, 'field', X)).toEqual(p.guardada);
  });

  it('mesmo cadastro: mesmo registro, ou criação com o mesmo nome (chave do banco) no mesmo escopo', () => {
    const azul = talhao('a', 'Talhão Azul').intencao;
    expect(mesmoCadastro(azul, talhao('b', '  talhão   AZUL ', F1, '7').intencao)).toBe(true);
    expect(mesmoCadastro(azul, talhao('c', 'Talhão Verde').intencao)).toBe(false);
    expect(mesmoCadastro(azul, talhao('d', 'Talhão Azul', F2).intencao)).toBe(false);
    expect(mesmoCadastro(azul, fazenda('e', 'Talhão Azul').intencao)).toBe(false);
    expect(mesmoCadastro(fazenda('f', 'Sede').intencao, fazenda('g', 'SEDE', F2).intencao)).toBe(true);
    expect(mesmoCadastro(edicao('h', X, 'Um').intencao, situacao('i', X).intencao)).toBe(true);
    expect(mesmoCadastro(edicao('j', X, 'Um').intencao, edicao('k', Y, 'Um').intencao)).toBe(false);
  });

  it('pedido novo grava só dentro da trava do alvo; equivalente pendente impede e nada é gravado', async () => {
    const a = memoria();
    const { lock, nomes } = travas();
    const azul = guardar(a, talhao('azul', 'Talhão Azul'));
    expect(await registrarNovoPedido(lock, a, u, o, talhao('outra', 'TALHÃO azul', F1, '7'))).toEqual({
      tipo: 'pendente',
      guardada: azul,
    });
    expect(chaves(a)).toEqual(['azul']);
    expect(await registrarNovoPedido(lock, a, u, o, talhao('verde', 'Talhão Verde'))).toEqual({
      tipo: 'gravado',
    });
    expect(chaves(a)).toEqual(['azul', 'verde']);
    await registrarNovoPedido(lock, a, u, o, edicao('e1', X, 'Um'));
    expect(await registrarNovoPedido(lock, a, u, o, situacao('s1', X))).toMatchObject({ tipo: 'pendente' });
    expect(await registrarNovoPedido(lock, a, u, o, situacao('s2', Y))).toEqual({ tipo: 'gravado' });
    const p = prefixoDasIntencoes(u, o);
    expect(nomes).toEqual([
      `${p}alvo:${C.criarTalhao}`,
      `${p}alvo:${C.criarTalhao}`,
      `${p}alvo:field:${X}`,
      `${p}alvo:field:${X}`,
      `${p}alvo:field:${Y}`,
    ]);
    const semEspaco = {
      ...a,
      setItem: () => {
        throw new Error('quota');
      },
    };
    expect(await registrarNovoPedido(lock, semEspaco, u, o, talhao('vermelho', 'Vermelho'))).toEqual({
      tipo: 'falhou',
    });
    await expect(registrarNovoPedido(undefined, a, u, o, talhao('roxo', 'Roxo'))).rejects.toThrow('trava');
    expect(chaves(a)).toEqual(['azul', 'e1', 's2', 'verde']);
  });

  it('duas abas com a mesma criação na trava do alvo: só a primeira é gravada', async () => {
    const a = memoria();
    const { lock } = travas();
    const resultado = await Promise.all([
      registrarNovoPedido(lock, a, u, o, talhao('aba-1', 'Talhão Azul')),
      registrarNovoPedido(lock, a, u, o, talhao('aba-2', 'Talhão Azul')),
    ]);
    expect(resultado.map((r) => r.tipo)).toEqual(['gravado', 'pendente']);
    expect(chaves(a)).toEqual(['aba-1']);
    expect(pendenteEquivalente(a, u, o, talhao('aba-1', 'Talhão Azul').intencao)).toBeNull();
  });

  it('a trava do alvo exige Web Locks e não executa nada sem ela', async () => {
    let executou = false;
    await expect(
      comTravaDoAlvo(undefined, u, o, talhao('x', 'X').intencao, () => {
        executou = true;
        return Promise.resolve();
      }),
    ).rejects.toThrow('trava');
    expect(executou).toBe(false);
  });
});

describe('DECISAO-RECUPERACAO-C2-20261003 §2: recusa antes do envelope sem rebaixar incerteza', () => {
  it('401 contratual do primeiro envio vira certeza persistida, que sobrevive à releitura', () => {
    const a = memoria();
    const g = guardar(a, fazenda('f1', 'Primeira'));
    for (const e of [SEM_SESSAO, erroContrato('ORGANIZACAO_INVALIDA', 'Organização.', 'c401')])
      expect(desfechoDoEnvio(e.status, e.corpo, g.intencao, false)).toMatchObject({
        tipo: 'nao_gravado',
        sessao: true,
      });
    const marcada = marcarRecusaAntesDoEnvelope(a, u, o, g);
    expect(marcada).toEqual({ ...g, antesDoEnvelope: true });
    expect(lerIntencao(a, u, o, 'f1')).toEqual(marcada);
    expect(lerIntencoes(a, u, o)).toEqual([marcada]);
    expect(marcarRecusaAntesDoEnvelope(a, u, o, g)).toEqual(marcada);
  });

  it('a certeza é retirada e conferida antes do novo POST; sem queda, 500 permanente é corrigível', () => {
    const a = memoria();
    const g = guardar(a, fazenda('f1', 'Primeira'));
    marcarRecusaAntesDoEnvelope(a, u, o, g);
    const preparo = prepararNovoEnvio(a, u, o, g);
    expect(preparo).toEqual({ tipo: 'primeiro', guardada: g });
    expect(lerIntencao(a, u, o, 'f1')).toEqual(g);
    expect(desfechoDoEnvio(PERMANENTE.status, PERMANENTE.corpo, g.intencao, false)).toMatchObject({
      tipo: 'corrigir',
      correlacao: 'cl22',
    });
  });

  it('queda durante ou depois do POST reabre incerteza: o próximo envio é repetição e o 500 bloqueia', () => {
    const a = memoria();
    const g = guardar(a, fazenda('f1', 'Primeira'));
    marcarRecusaAntesDoEnvelope(a, u, o, g);
    expect(prepararNovoEnvio(a, u, o, g).tipo).toBe('primeiro');
    // A aba cai com o POST em voo: só o que está guardado volta.
    const reaberta = lerIntencoes(a, u, o)[0];
    if (!reaberta) throw new Error('pendência perdida');
    expect(reaberta).not.toHaveProperty('antesDoEnvelope');
    expect(reaberta).not.toHaveProperty('falha');
    expect(prepararNovoEnvio(a, u, o, reaberta)).toEqual({ tipo: 'repeticao', guardada: reaberta });
    expect(desfechoDoEnvio(PERMANENTE.status, PERMANENTE.corpo, reaberta.intencao, true)).toMatchObject({
      tipo: 'incerto',
      bloqueioPermanente: { correlacao: 'cl22' },
    });
  });

  it('falha ao retirar a certeza impede o POST e conserva o registro', () => {
    const a = memoria();
    const g = guardar(a, fazenda('f1', 'Primeira'));
    const marcada = marcarRecusaAntesDoEnvelope(a, u, o, g);
    const quota = {
      ...a,
      setItem: () => {
        throw new Error('quota');
      },
    };
    const mudo = { ...a, setItem: () => undefined };
    for (const armazem of [quota, mudo, null])
      expect(prepararNovoEnvio(armazem, u, o, g)).toMatchObject({ tipo: 'impedido' });
    expect(lerIntencao(a, u, o, 'f1')).toEqual(marcada);
  });

  it('401 depois de uma tentativa incerta continua incerto e não marca certeza alguma', () => {
    const a = memoria();
    const g = guardar(a, fazenda('f1', 'Primeira'));
    // Sem certeza guardada, o envio seguinte é repetição: a primeira tentativa pode ter gravado.
    expect(prepararNovoEnvio(a, u, o, g)).toEqual({ tipo: 'repeticao', guardada: g });
    expect(desfechoDoEnvio(SEM_SESSAO.status, SEM_SESSAO.corpo, g.intencao, true)).toMatchObject({
      tipo: 'incerto',
      sessao: true,
    });
    const bloqueada = guardar(a, fazenda('f2', 'Segunda'), incerta());
    expect(marcarRecusaAntesDoEnvelope(a, u, o, bloqueada)).toBeNull();
    expect(lerIntencao(a, u, o, 'f2')).toEqual(bloqueada);
  });

  it('só a resposta contratual prova a recusa: 401 sem corpo, classe trocada ou rede continuam incertos', () => {
    const i = fazenda('f1', 'Primeira').intencao;
    for (const [status, corpo] of [
      [401, null],
      [401, { ...SEM_SESSAO.corpo, classe: 'validacao' }],
      [401, erroContrato('SEM_PERMISSAO', 'Papel.', 'c403').corpo],
      [0, null],
    ] as const)
      expect(desfechoDoEnvio(status, corpo, i, false).tipo).toBe('incerto');
  });

  it('formato: certeza só como true e nunca junto de falha; gravar antes do POST a recusa; falha a retira', () => {
    const a = memoria();
    const g = fazenda('f1', 'Primeira');
    const k = prefixoDasIntencoes(u, o) + 'f1';
    for (const invalido of [
      { ...g, antesDoEnvelope: 'sim' },
      { ...g, antesDoEnvelope: false },
      { ...g, antesDoEnvelope: true, falha: recusa() },
    ]) {
      a.m.set(k, JSON.stringify(invalido));
      expect(lerIntencoes(a, u, o)).toEqual([]);
      expect(a.m.get(k)).toBe(JSON.stringify(invalido));
    }
    a.m.clear();
    expect(gravarIntencao(a, u, o, { ...g, antesDoEnvelope: true })).toBe(false);
    expect(a.m.size).toBe(0);
    guardar(a, g);
    marcarRecusaAntesDoEnvelope(a, u, o, g);
    expect(guardarFalha(a, u, o, g, recusa())).toEqual({ ...g, falha: recusa() });
    expect(lerIntencao(a, u, o, 'f1')).toEqual({ ...g, falha: recusa() });
  });
});

describe('DECISAO-RECUPERACAO-C2-20261003 §3: encerrar o pedido recusado sem gravação', () => {
  it('situação recusada não promete correção e é encerrada sem rede, devolvendo a correlação', () => {
    const a = memoria();
    const g = guardar(a, situacao('s1'), recusa());
    expect(acaoDoPendente(g)).toBe('Encerrar pedido');
    expect(acaoDoPendente(guardar(a, fazenda('f1', 'Sede'), recusa('c-f1')))).toBe('Corrigir cadastro');
    expect(acaoDoPendente(guardar(a, fazenda('f2', 'Outra')))).toBe('Consultar envio');
    expect(encerrarPedido(a, u, o, g)).toEqual({ tipo: 'encerrado', correlacoes: ['cl22'] });
    expect(chaves(a)).toEqual(['f1', 'f2']);
  });

  it('cadeia de correções recusadas é encerrada inteira, com as correlações da raiz à folha', () => {
    const a = memoria();
    const raiz = guardar(a, fazenda('r', 'Sede'), recusa('c1'));
    const p = prepararCorrecao(a, u, o, raiz, fazenda('s', 'Sede Nova', raiz.intencao.targetId));
    if (p.tipo !== 'nova') throw new Error(p.tipo);
    const folha = guardarFalha(a, u, o, p.guardada, recusa('c2'));
    if (!folha) throw new Error('falha');
    expect(encerrarPedido(a, u, o, folha)).toEqual({ tipo: 'encerrado', correlacoes: ['c1', 'c2'] });
    expect(a.m.size).toBe(0);
  });

  it('a aba velha não apaga a sucessora incerta preparada em outra aba', () => {
    const a = memoria();
    const raiz = guardar(a, fazenda('r', 'Sede'), recusa());
    const p = prepararCorrecao(a, u, o, raiz, fazenda('s', 'Sede Nova', raiz.intencao.targetId));
    if (p.tipo !== 'nova') throw new Error(p.tipo);
    expect(encerrarPedido(a, u, o, raiz)).toEqual({ tipo: 'mudou', guardada: p.guardada });
    expect(chaves(a)).toEqual(['r', 's']);
  });

  it('incerto, somente_consulta e certeza antes do envelope nunca são encerrados', () => {
    const a = memoria();
    const sem = guardar(a, fazenda('f1', 'Um'));
    const bloqueada = guardar(a, fazenda('f2', 'Dois'), incerta());
    const marcada = marcarRecusaAntesDoEnvelope(a, u, o, guardar(a, fazenda('f3', 'Três')));
    if (!marcada) throw new Error('marca');
    const antes = new Map(a.m);
    for (const g of [sem, bloqueada, marcada])
      expect(encerrarPedido(a, u, o, g)).toMatchObject({ tipo: 'impedido' });
    expect(a.m).toEqual(antes);
  });

  it('limpeza interrompida deixa a folha recusada consultável e o encerramento pode ser repetido', () => {
    const a = memoria();
    const raiz = guardar(a, fazenda('r', 'Sede'), recusa('c1'));
    const p = prepararCorrecao(a, u, o, raiz, fazenda('s', 'Sede Nova', raiz.intencao.targetId));
    if (p.tipo !== 'nova') throw new Error(p.tipo);
    const folha = guardarFalha(a, u, o, p.guardada, recusa('c2'));
    if (!folha) throw new Error('falha');
    const interrompido = {
      ...a,
      removeItem: (k: string) => {
        if (k.endsWith(':s')) throw new Error('interrupção');
        a.removeItem(k);
      },
    };
    expect(encerrarPedido(interrompido, u, o, folha)).toMatchObject({ tipo: 'impedido' });
    expect(lerIntencoes(a, u, o)).toEqual([folha]);
    expect(encerrarPedido(a, u, o, folha)).toEqual({ tipo: 'encerrado', correlacoes: ['c2'] });
    expect(a.m.size).toBe(0);
  });

  it('na trava do fluxo, encerrar e corrigir em abas diferentes nunca deixam sucessora órfã', async () => {
    for (const encerrarPrimeiro of [true, false]) {
      const a = memoria();
      const { lock } = travas();
      const raiz = guardar(a, fazenda('r', 'Sede'), recusa());
      const encerrar = () =>
        lock.request(prefixoDasIntencoes(u, o) + 'r', () => Promise.resolve(encerrarPedido(a, u, o, raiz)));
      const corrigir = () =>
        lock.request(prefixoDasIntencoes(u, o) + 'r', () =>
          Promise.resolve(prepararCorrecao(a, u, o, raiz, fazenda('s', 'Sede Nova', raiz.intencao.targetId))),
        );
      const [x, y] = await Promise.all(
        encerrarPrimeiro ? [encerrar(), corrigir()] : [corrigir(), encerrar()],
      );
      if (encerrarPrimeiro) {
        expect([x.tipo, y.tipo]).toEqual(['encerrado', 'impedido']);
        expect(a.m.size).toBe(0);
      } else {
        expect([x.tipo, y.tipo]).toEqual(['nova', 'mudou']);
        expect(chaves(a)).toEqual(['r', 's']);
      }
    }
  });
});

describe('DECISAO-RECUPERACAO-C2-20261003 §4: somente_consulta só sai com prova terminal', () => {
  it('500 permanente posterior + 404 não encerra nem libera envio; o recibo tardio ainda resolve', () => {
    const a = memoria();
    const g = guardar(a, fazenda('f1', 'Incerta'));
    const d = desfechoDoEnvio(PERMANENTE.status, PERMANENTE.corpo, g.intencao, true);
    if (d.tipo !== 'incerto' || !d.bloqueioPermanente) throw new Error(d.tipo);
    const bloqueada = guardarFalha(a, u, o, g, { tipo: 'somente_consulta', ...d.bloqueioPermanente });
    if (!bloqueada) throw new Error('bloqueio');
    const ausente = erroContrato('RECIBO_NAO_LOCALIZADO', 'Ausente.', 'c404');
    expect(desfechoDaConsulta(ausente.status, ausente.corpo, g.intencao)).toMatchObject({ tipo: 'incerto' });
    expect(encerrarPedido(a, u, o, bloqueada)).toMatchObject({ tipo: 'impedido' });
    expect(prepararNovoEnvio(a, u, o, bloqueada)).toMatchObject({ tipo: 'impedido' });
    expect(acaoDoPendente(bloqueada)).toBe('Consultar envio');
    expect(lerIntencoes(a, u, o)).toEqual([bloqueada]);
    const r = recibo(g.intencao);
    expect(desfechoDaConsulta(200, r, g.intencao)).toEqual({ tipo: 'resolvido', recibo: r });
  });
});
