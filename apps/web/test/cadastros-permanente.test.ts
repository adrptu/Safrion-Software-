import { describe, expect, it } from 'vitest';
import { COMANDOS_CADASTRO as C, erroContrato } from '@safrion/contracts';
import {
  novaIntencao,
  desfechoDoEnvio,
  desfechoDaConsulta,
  mesmoConteudoDeDominio,
} from '../src/cadastros/intencao';
import {
  gravarIntencao,
  guardarFalha,
  lerIntencoes,
  lerIntencao,
  atualDoFluxo,
  prepararCorrecao,
  apagarFluxo,
  comTravaCadastro,
  prefixoDasIntencoes,
  type IntencaoGuardada,
  type FalhaGuardada,
} from '../src/cadastros/pendencias';
const ID = '00000000-0000-4000-8000-000000000001';
const u = 'usuario',
  o = 'org';
const falha: FalhaGuardada = {
  tipo: 'corrigir',
  mensagem: 'Corrija o dado recusado.',
  correlacao: 'correlacao-1',
};
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
function g(chave = 'pedido-1', nome = 'Talhão Azul', area = '204.5'): IntencaoGuardada {
  return {
    intencao: novaIntencao(
      C.criarTalhao,
      'field',
      ID,
      0,
      { nome, areaDeclaradaHa: area, fazenda: ID },
      chave,
    ),
    campos: { nome, area: area.replace('.', ','), fazenda: ID },
    iniciais: { nome: '', area: '', fazenda: ID },
    contexto: {
      tipo: 'talhao',
      titulo: 'Criar talhão',
      volta: '/cadastros/areas?fazenda=1',
    },
    criadaEm: '2026-10-01T03:00:00Z',
  };
}
function recusada(a: ReturnType<typeof memoria>) {
  const inicial = g();
  expect(gravarIntencao(a, u, o, inicial)).toBe(true);
  const guardada = guardarFalha(a, u, o, inicial, falha);
  expect(guardada).not.toBeNull();
  if (!guardada) throw new Error('falha não persistida');
  return guardada;
}
// Executor de LockManager simulado: testa concorrência do protocolo puro, não a implementação Web Locks do navegador.
function travas(): Pick<LockManager, 'request'> {
  const caudas = new Map<string, Promise<unknown>>();
  return {
    request: ((nome: string, fn: () => Promise<unknown>) => {
      const exec = (caudas.get(nome) ?? Promise.resolve()).then(fn);
      caudas.set(
        nome,
        exec.catch(() => undefined),
      );
      return exec;
    }) as LockManager['request'],
  };
}
describe('ENV-UI-01: recuperação persistida de falha permanente', () => {
  it('primeiro sinal exato guarda recusa e recarga preserva campos, base e correlação', () => {
    const a = memoria(),
      inicial = g();
    gravarIntencao(a, u, o, inicial);
    const e = erroContrato('FALHA_INTERNA', 'Corrija o dado recusado.', 'correlacao-1', {
      detalhe: { resultadoIncerto: false, repetirMesmoConteudo: false },
    });
    const d = desfechoDoEnvio(e.status, e.corpo, inicial.intencao, false);
    expect(d.tipo).toBe('corrigir');
    if (d.tipo !== 'corrigir') throw new Error('desfecho');
    guardarFalha(a, u, o, inicial, {
      tipo: 'corrigir',
      mensagem: d.mensagem,
      correlacao: d.correlacao,
    });
    expect(lerIntencoes(a, u, o)).toEqual([{ ...inicial, falha }]);
  });
  it('reenvio incerto conserva bloqueio depois de 404 e releitura, sem liberar nova intenção', () => {
    const a = memoria(),
      inicial = g();
    gravarIntencao(a, u, o, inicial);
    const e = erroContrato('FALHA_INTERNA', 'Corrija o dado recusado.', 'correlacao-1', {
      detalhe: { resultadoIncerto: false, repetirMesmoConteudo: false },
    });
    const d = desfechoDoEnvio(e.status, e.corpo, inicial.intencao, true);
    expect(d.tipo).toBe('incerto');
    if (d.tipo !== 'incerto' || !d.bloqueioPermanente) throw new Error('desfecho');
    guardarFalha(a, u, o, inicial, {
      tipo: 'somente_consulta',
      ...d.bloqueioPermanente,
    });
    const ausente = erroContrato('RECIBO_NAO_LOCALIZADO', 'Ausente.', 'consulta-2');
    expect(desfechoDaConsulta(ausente.status, ausente.corpo, inicial.intencao)).toMatchObject({
      tipo: 'incerto',
      naoLocalizado: true,
    });
    const reaberta = lerIntencoes(a, u, o)[0];
    if (!reaberta) throw new Error('recuperação ausente');
    expect(reaberta.falha).toMatchObject({
      tipo: 'somente_consulta',
      correlacao: 'correlacao-1',
    });
    expect(prepararCorrecao(a, u, o, reaberta, g('nova', 'Talhão Verde')).tipo).toBe('impedido');
    // Nem uma classificação tardia de primeiro envio substitui a prova conservada.
    expect(guardarFalha(a, u, o, inicial, falha)?.falha?.tipo).toBe('somente_consulta');
  });
  it('falha de escrita ou readback não autoriza correção nem apaga original', () => {
    const a = memoria(),
      inicial = g();
    gravarIntencao(a, u, o, inicial);
    const semEscrita = {
      ...a,
      setItem: () => {
        throw new Error('quota');
      },
    };
    expect(guardarFalha(semEscrita, u, o, inicial, falha)).toBeNull();
    expect(prepararCorrecao(a, u, o, { ...inicial, falha }, g('nova', 'Verde')).tipo).toBe('impedido');
    expect(lerIntencao(a, u, o, inicial.intencao.chave)).toEqual(inicial);
    expect(guardarFalha({ ...a, setItem: () => undefined }, u, o, inicial, falha)).toBeNull();
  });
  it('chave, id ou versão novos e formatação equivalente não corrigem o conteúdo', () => {
    const a = memoria(),
      inicial = recusada(a);
    expect(mesmoConteudoDeDominio(inicial.intencao, g('nova', '  Talhão   Azul  ', '204.500').intencao)).toBe(
      true,
    );
    expect(prepararCorrecao(a, u, o, inicial, g('nova', '  Talhão   Azul  ', '204.500')).tipo).toBe(
      'impedido',
    );
    for (const metadados of [{ targetId: '00000000-0000-4000-8000-000000000002' }, { expectedVersion: 2 }]) {
      const candidata = g('nova', 'Verde');
      expect(
        prepararCorrecao(a, u, o, inicial, {
          ...candidata,
          intencao: { ...candidata.intencao, ...metadados },
        }).tipo,
      ).toBe('impedido');
    }
    expect(lerIntencoes(a, u, o)).toEqual([inicial]);
  });
  it('correção preparada conserva a origem e é retomada com a mesma chave após crash antes ou depois do POST', () => {
    const a = memoria(),
      inicial = recusada(a),
      candidata = g('corrigida-1', 'Verde');
    const p = prepararCorrecao(a, u, o, inicial, candidata);
    expect(p.tipo).toBe('nova');
    if (p.tipo === 'impedido') throw new Error('preparo');
    expect(p.guardada.origem).toEqual({
      chave: 'pedido-1',
      raiz: 'pedido-1',
      correlacao: 'correlacao-1',
    });
    expect(lerIntencao(a, u, o, 'pedido-1')).toEqual(inicial);
    expect(lerIntencoes(a, u, o)).toEqual([p.guardada]);
    expect(atualDoFluxo(a, u, o, inicial)).toEqual(p.guardada);
    expect(prepararCorrecao(a, u, o, inicial, g('corrigida-2', 'Vermelho'))).toEqual({
      tipo: 'existente',
      guardada: p.guardada,
    });
    expect(a.m.size).toBe(2);
  });
  it('duas abas serializadas não criam duas chaves para a mesma correção', async () => {
    const a = memoria(),
      inicial = recusada(a),
      lock = travas();
    const executar = (chave: string) =>
      comTravaCadastro(lock, u, o, inicial, () =>
        Promise.resolve(prepararCorrecao(a, u, o, inicial, g(chave, 'Verde'))),
      );
    const resultados = await Promise.all([executar('aba-a'), executar('aba-b')]);
    expect(resultados.map((x) => x.tipo)).toEqual(['nova', 'existente']);
    expect(lerIntencoes(a, u, o)[0]?.intencao.chave).toBe('aba-a');
    expect(a.m.size).toBe(2);
  });
  it('segunda correção conserva as duas correlações até o recibo; limpeza interrompida não reabre ancestral', () => {
    const a = memoria(),
      inicial = recusada(a);
    const p = prepararCorrecao(a, u, o, inicial, g('corrigida-1', 'Verde'));
    if (p.tipo === 'impedido') throw new Error('preparo');
    const segundaFalha = guardarFalha(a, u, o, p.guardada, {
      ...falha,
      correlacao: 'correlacao-2',
    });
    if (!segundaFalha) throw new Error('segunda falha ausente');
    const p2 = prepararCorrecao(a, u, o, segundaFalha, g('corrigida-2', 'Amarelo'));
    if (p2.tipo === 'impedido') throw new Error('preparo');
    expect(p2.guardada.origem).toEqual({
      chave: 'corrigida-1',
      raiz: 'pedido-1',
      correlacao: 'correlacao-2',
    });
    const parcial = {
      ...a,
      removeItem: (k: string) => {
        if (k.endsWith('corrigida-2')) throw new Error('interrupção');
        a.removeItem(k);
      },
    };
    expect(apagarFluxo(parcial, u, o, p2.guardada)).toBe(false);
    expect(lerIntencoes(a, u, o)).toEqual([p2.guardada]);
    expect(apagarFluxo(a, u, o, p2.guardada)).toBe(true);
    expect(a.m.size).toBe(0);
  });
  it('persistir sucessora falha sem consumir rascunho ou correlação do pedido recusado', () => {
    const a = memoria(),
      inicial = recusada(a);
    expect(
      prepararCorrecao(
        {
          ...a,
          setItem: () => {
            throw new Error('quota');
          },
        },
        u,
        o,
        inicial,
        g('nova', 'Verde'),
      ).tipo,
    ).toBe('impedido');
    expect(lerIntencoes(a, u, o)).toEqual([inicial]);
  });
  it('legado não vira prova, marcador malformado não desaparece fisicamente e escopos não se misturam', () => {
    const a = memoria(),
      inicial = g();
    gravarIntencao(a, u, o, inicial);
    expect(lerIntencoes(a, u, o)[0]?.falha).toBeUndefined();
    const k = prefixoDasIntencoes(u, o) + 'pedido-1';
    a.m.set(k, JSON.stringify({ ...inicial, falha: { ...falha, tipo: 'confirmado' } }));
    expect(lerIntencoes(a, u, o)).toEqual([]);
    expect(a.m.has(k)).toBe(true);
    expect(guardarFalha(a, 'outro', o, inicial, falha)).toBeNull();
  });
  it('sem trava entre abas nenhuma operação fornecida é executada', async () => {
    let executou = false;
    await expect(
      comTravaCadastro(undefined, u, o, g(), () => {
        executou = true;
        return Promise.resolve();
      }),
    ).rejects.toThrow('trava');
    expect(executou).toBe(false);
  });
  it('comparação respeita os esquemas próprios de editar fazenda, editar talhão e situação', () => {
    const i = (c: (typeof C)[keyof typeof C], data: Record<string, string>, chave: string) =>
      novaIntencao(c, c === C.editarFazenda ? 'farm' : 'field', ID, 1, data, chave);
    for (const [comando, a, b] of [
      [C.editarFazenda, { nome: 'Fazenda  Azul' }, { nome: ' Fazenda Azul ' }],
      [C.editarTalhao, { areaDeclaradaHa: '204.500' }, { areaDeclaradaHa: '204.5' }],
      [C.alterarSituacaoTalhao, { situacao: 'ativo' }, { situacao: 'ativo' }],
    ] as const)
      expect(mesmoConteudoDeDominio(i(comando, a, 'a'), i(comando, b, 'b'))).toBe(true);
    expect(
      mesmoConteudoDeDominio(
        i(C.alterarSituacaoTalhao, { situacao: 'ativo' }, 'a'),
        i(C.alterarSituacaoTalhao, { situacao: 'inativo' }, 'b'),
      ),
    ).toBe(false);
  });
});

describe('ENV-UI-01-LIMPEZA: ancestralidade independe do relógio', () => {
  it.each([2, 3, 5])('retoma a última de %i intenções quando há interrupção em cada remoção', (tamanho) => {
    for (const depoisDeRemover of [false, true]) {
      for (let interromper = 1; interromper <= tamanho; interromper += 1) {
        const a = memoria();
        let ultima = recusada(a);
        const chaves = [ultima.intencao.chave];
        for (let i = 1; i < tamanho; i += 1) {
          // Datas regressivas e chaves fora da ordem: nenhuma delas pode ordenar a limpeza.
          const candidata = {
            ...g(`correcao-${String(tamanho - i)}`, `Nome ${String(i)}`),
            criadaEm: new Date(Date.parse(ultima.criadaEm) - 60_000).toISOString(),
          };
          const preparo = prepararCorrecao(a, u, o, ultima, candidata);
          if (preparo.tipo === 'impedido') throw new Error(preparo.mensagem);
          ultima = preparo.guardada;
          chaves.push(ultima.intencao.chave);
          if (i < tamanho - 1) {
            const salva = guardarFalha(a, u, o, ultima, {
              ...falha,
              correlacao: `correlacao-${String(i + 1)}`,
            });
            if (!salva) throw new Error('Falha intermediária não guardada.');
            ultima = salva;
          }
        }
        let tentativa = 0;
        const removidas: string[] = [];
        const parcial = {
          get length() {
            return a.length;
          },
          key: a.key,
          getItem: a.getItem,
          removeItem: (chave: string) => {
            tentativa += 1;
            if (!depoisDeRemover && tentativa === interromper) throw new Error('interrupção antes');
            a.removeItem(chave);
            removidas.push(chave.slice(prefixoDasIntencoes(u, o).length));
            if (depoisDeRemover && tentativa === interromper) throw new Error('interrupção depois');
          },
        };
        expect(apagarFluxo(parcial, u, o, ultima)).toBe(false);
        expect(removidas).toEqual(chaves.slice(0, removidas.length));
        if (removidas.length === tamanho) {
          expect(lerIntencoes(a, u, o)).toEqual([]);
        } else {
          expect(lerIntencoes(a, u, o)).toEqual([ultima]);
          expect(atualDoFluxo(a, u, o, ultima)).toEqual(ultima);
        }
        // Reinício da limpeza após cada corte usa o que restou, sem precisar dos ancestrais já retirados.
        expect(apagarFluxo(a, u, o, ultima)).toBe(true);
        expect(a.m.size).toBe(0);
      }
    }
  });
});
