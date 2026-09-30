import { COMANDOS_CADASTRO } from '@safrion/contracts';
import { describe, expect, it } from 'vitest';

import { novaIntencao } from '../src/cadastros/intencao';
import {
  apagarIntencao,
  armazemLocal,
  gravarIntencao,
  lerIntencoes,
  prefixoDasIntencoes,
  type IntencaoGuardada,
} from '../src/cadastros/pendencias';
import { apagarRascunhos } from '../src/estoque/rascunho';

const ID = '00000000-0000-4000-8000-000000000001';
const USUARIO = 'usuario-1';
const ORG = 'org-1';

function memoria() {
  const dados = new Map<string, string>();
  return {
    dados,
    get length() {
      return dados.size;
    },
    key: (i: number) => [...dados.keys()][i] ?? null,
    getItem: (chave: string) => dados.get(chave) ?? null,
    setItem: (chave: string, valor: string) => {
      dados.set(chave, valor);
    },
    removeItem: (chave: string) => {
      dados.delete(chave);
    },
  };
}

function guardada(chave = 'chave-1', criadaEm = '2026-09-30T20:00:00Z'): IntencaoGuardada {
  return {
    campos: { nome: 'Talhão 1', area: '204,5', fazenda: ID },
    intencao: novaIntencao(
      COMANDOS_CADASTRO.criarTalhao,
      'field',
      ID,
      0,
      { nome: 'Talhão 1', areaDeclaradaHa: '204.5', fazenda: ID },
      chave,
    ),
    contexto: { tipo: 'talhao', titulo: 'Novo talhão', volta: '/cadastros/areas?fazenda=1' },
    criadaEm,
  };
}

const chaveLocal = (chave: string) => prefixoDasIntencoes(USUARIO, ORG) + chave;

describe('pendências de cadastro, uma chave por intenção', () => {
  it('mantém dois envios simultâneos, separados por usuário e organização, sem apagar o mais antigo', () => {
    const a = memoria();
    const antiga = guardada('chave-1');
    const nova = guardada('chave-2', '2026-09-30T20:01:00Z');
    expect(gravarIntencao(a, USUARIO, ORG, nova)).toBe(true);
    expect(gravarIntencao(a, USUARIO, ORG, antiga)).toBe(true);
    expect(gravarIntencao(a, 'outro-usuario', ORG, guardada('outra-pessoa'))).toBe(true);
    expect(gravarIntencao(a, USUARIO, 'outra-org', guardada('outra-org'))).toBe(true);
    expect(lerIntencoes(a, USUARIO, ORG)).toEqual([antiga, nova]);
    apagarIntencao(a, USUARIO, ORG, antiga.intencao.chave);
    expect(lerIntencoes(a, USUARIO, ORG)).toEqual([nova]);
    expect(a.dados.size).toBe(3);
    expect(lerIntencoes(a, 'ausente', ORG)).toEqual([]);
    expect(prefixoDasIntencoes('a:b', 'c')).not.toBe(prefixoDasIntencoes('a', 'b:c'));
  });

  it('a mesma chave conserva o corpo original e seus campos; outro corpo é recusado', () => {
    const a = memoria();
    const g = guardada();
    expect(gravarIntencao(a, USUARIO, ORG, g)).toBe(true);
    expect(
      gravarIntencao(a, USUARIO, ORG, {
        ...g,
        campos: { nome: 'Outra aba' },
        criadaEm: '2026-09-30T21:00:00Z',
      }),
    ).toBe(true);
    expect(lerIntencoes(a, USUARIO, ORG)).toEqual([g]);
    const outro = {
      ...g,
      intencao: novaIntencao(
        COMANDOS_CADASTRO.criarTalhao,
        'field',
        ID,
        0,
        { nome: 'Outro', areaDeclaradaHa: '1', fazenda: ID },
        g.intencao.chave,
      ),
    };
    expect(gravarIntencao(a, USUARIO, ORG, outro)).toBe(false);
    expect(lerIntencoes(a, USUARIO, ORG)).toEqual([g]);
  });

  it('valida corpo, metadados, contexto e chave do armazenamento sem executar ou apagar registros estranhos', () => {
    const a = memoria();
    const g = guardada();
    expect(gravarIntencao(a, USUARIO, ORG, g)).toBe(true);
    const invalidos = [
      '{',
      JSON.stringify({ ...g, campos: ['x'] }),
      JSON.stringify({ ...g, campos: { nome: 42 } }),
      JSON.stringify({ ...g, intencao: { ...g.intencao, expectedVersion: 1 } }),
      JSON.stringify({ ...g, contexto: { ...g.contexto, tipo: 'fazenda' } }),
      JSON.stringify({ ...g, contexto: { ...g.contexto, tipo: 'situacao' } }),
      JSON.stringify({ ...g, contexto: { ...g.contexto, volta: 'https://externo.example/' } }),
      JSON.stringify({ ...g, contexto: { ...g.contexto, volta: '//externo.example/' } }),
      JSON.stringify({ ...g, contexto: { ...g.contexto, volta: '/cadastros/areas/../../sair' } }),
      JSON.stringify({ ...g, contexto: { ...g.contexto, volta: '/cadastros/areas?x=1\\externo' } }),
      JSON.stringify({ ...g, criadaEm: 'inválida' }),
      JSON.stringify(g),
    ];
    invalidos.forEach((valor, i) => a.dados.set(chaveLocal(`corrompida-${String(i)}`), valor));
    const antes = [...a.dados];
    expect(lerIntencoes(a, USUARIO, ORG)).toEqual([g]);
    expect([...a.dados]).toEqual(antes);
    expect(gravarIntencao(a, USUARIO, ORG, { ...g, contexto: { ...g.contexto, volta: '/sair' } })).toBe(
      false,
    );
  });

  it('recupera edição de fazenda e mudança de situação sem trocar o tipo de formulário', () => {
    const a = memoria();
    const fazenda: IntencaoGuardada = {
      campos: { nome: 'Fazenda 1' },
      intencao: novaIntencao(COMANDOS_CADASTRO.editarFazenda, 'farm', ID, 3, { nome: 'Fazenda 1' }, 'farm-1'),
      contexto: { tipo: 'fazenda', titulo: 'Editar fazenda', volta: `/cadastros/fazendas/${ID}` },
      criadaEm: '2026-09-30T20:00:00Z',
    };
    const situacao: IntencaoGuardada = {
      campos: { situacao: 'inativo' },
      intencao: novaIntencao(
        COMANDOS_CADASTRO.alterarSituacaoTalhao,
        'field',
        ID,
        1,
        { situacao: 'inativo' },
        'situacao-1',
      ),
      contexto: {
        tipo: 'situacao',
        titulo: 'Inativar talhão',
        volta: `/cadastros/areas/${ID}?volta=%2Fcadastros%2Fareas`,
      },
      criadaEm: '2026-09-30T20:00:00Z',
    };
    expect(gravarIntencao(a, USUARIO, ORG, situacao)).toBe(true);
    expect(gravarIntencao(a, USUARIO, ORG, fazenda)).toBe(true);
    expect(lerIntencoes(a, USUARIO, ORG)).toEqual([fazenda, situacao]);
  });

  it('preserva os campos iniciais separados dos editados e nunca os substitui na mesma intenção', () => {
    const a = memoria();
    const g: IntencaoGuardada = {
      ...guardada(),
      iniciais: { nome: 'Talhão original', area: '204,000000', fazenda: ID },
    };
    expect(gravarIntencao(a, USUARIO, ORG, g)).toBe(true);
    const [recuperada] = lerIntencoes(a, USUARIO, ORG);
    expect(recuperada).toEqual(g);
    expect(recuperada?.campos.nome).toBe('Talhão 1');
    expect(recuperada?.iniciais?.nome).toBe('Talhão original');
    expect(gravarIntencao(a, USUARIO, ORG, { ...g, iniciais: { nome: 'Outra aba', area: '210' } })).toBe(
      true,
    );
    expect(lerIntencoes(a, USUARIO, ORG)).toEqual([g]);
    expect(lerIntencoes(a, USUARIO, ORG)[0]?.intencao).toEqual(g.intencao);
  });

  it('não recupera baseline inválido, nem inventa um para a intenção legada', () => {
    const a = memoria();
    const g = guardada();
    for (const iniciais of [null, [], '204', { area: 204 }, { nome: null }]) {
      const invalida = JSON.stringify({ ...g, iniciais });
      a.dados.set(chaveLocal(g.intencao.chave), invalida);
      expect(lerIntencoes(a, USUARIO, ORG)).toEqual([]);
      expect(a.getItem(chaveLocal(g.intencao.chave))).toBe(invalida);
    }
    a.dados.delete(chaveLocal(g.intencao.chave));
    expect(gravarIntencao(a, USUARIO, ORG, g)).toBe(true);
    const [legada] = lerIntencoes(a, USUARIO, ORG);
    expect(legada).toEqual(g);
    expect(legada).not.toHaveProperty('iniciais');
    expect(legada?.intencao.corpo).toBe(g.intencao.corpo);
    expect(legada?.intencao.chave).toBe(g.intencao.chave);
  });

  it('falha de armazenamento bloqueia o POST; corrupção existente não é sobrescrita', () => {
    const a = memoria();
    const g = guardada();
    expect(gravarIntencao(null, USUARIO, ORG, g)).toBe(false);
    expect(
      gravarIntencao(
        {
          getItem: () => null,
          setItem: () => {
            throw new Error('quota');
          },
        },
        USUARIO,
        ORG,
        g,
      ),
    ).toBe(false);
    expect(gravarIntencao({ getItem: () => null, setItem: () => undefined }, USUARIO, ORG, g)).toBe(false);
    a.dados.set(chaveLocal(g.intencao.chave), '{');
    expect(gravarIntencao(a, USUARIO, ORG, g)).toBe(false);
    expect(a.getItem(chaveLocal(g.intencao.chave))).toBe('{');
    expect(lerIntencoes(null, USUARIO, ORG)).toEqual([]);
    expect(armazemLocal()).toBeNull();
    expect(() => {
      apagarIntencao(
        {
          removeItem: () => {
            throw new Error('bloqueado');
          },
        },
        USUARIO,
        ORG,
        'x',
      );
    }).not.toThrow();
  });

  it('a falha de uma entrada não esconde as demais; sair limpa pelo prefixo já existente', () => {
    const a = memoria();
    const g = guardada();
    a.dados.set(chaveLocal('quebrada'), 'x');
    expect(gravarIntencao(a, USUARIO, ORG, g)).toBe(true);
    a.dados.set('outro-produto', 'preservar');
    expect(
      lerIntencoes(
        {
          ...a,
          getItem: (chave) => {
            if (chave.endsWith('quebrada')) throw new Error('bloqueada');
            return a.getItem(chave);
          },
        },
        USUARIO,
        ORG,
      ),
    ).toEqual([g]);
    expect(
      lerIntencoes(
        {
          length: 1,
          key: () => {
            throw new Error('bloqueado');
          },
          getItem: () => null,
        },
        USUARIO,
        ORG,
      ),
    ).toEqual([]);
    apagarRascunhos(a);
    expect([...a.dados]).toEqual([['outro-produto', 'preservar']]);
  });
});
