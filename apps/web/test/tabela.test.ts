import { describe, expect, it } from 'vitest';

import {
  alternarOrdem,
  caminhoDeVolta,
  comFiltro,
  ESTADO_VAZIO,
  estadoDaUrl,
  filtrar,
  hrefComVolta,
  normalizar,
  ordenar,
  resultado,
  semCampo,
  somar,
  urlDoEstado,
  valoresDaColuna,
  type ColunaG2,
  type EstadoG2,
  type LinhaG2,
} from '../src/tabela/logica';

const COLUNAS: readonly ColunaG2[] = [
  { chave: 'lote', rotulo: 'Lote', tipo: 'texto' },
  { chave: 'produto', rotulo: 'Produto', tipo: 'texto', agrupavel: true },
  { chave: 'validade', rotulo: 'Validade', tipo: 'data' },
  { chave: 'estado', rotulo: 'Estado', tipo: 'estado', agrupavel: true },
  { chave: 'utilizavel', rotulo: 'Utilizável', tipo: 'numero', somavel: true },
];

function linha(
  id: string,
  lote: string,
  produto: string,
  validade: string,
  estado: string,
  qtd: string,
  u: string,
) {
  return {
    id,
    href: `/estoque/${id}`,
    celulas: {
      lote: { texto: lote, valor: lote },
      produto: { texto: produto, valor: produto },
      validade: { texto: validade, valor: validade },
      estado: { texto: estado, valor: estado },
      utilizavel: { texto: `${qtd} ${u}`, valor: qtd, unidade: u },
    },
  } satisfies LinhaG2;
}

const A = linha('A', 'L-10', 'Herbicida', '2027-06-30', 'Liberado', '10.000000', 'L');
const B = linha('B', 'L-9', 'Fungicida', '2026-12-01', 'Em inspeção', '0.000000', 'L');
const C = linha('C', 'L-2', 'Herbicida', '', 'Recebido', '2.500000', 'L');
const D = linha('D', 'l-1', 'Adubo', '2027-01-15', 'Liberado', '1000.000000', 'kg');
const LINHAS = [A, B, C, D];
const ids = (ls: readonly LinhaG2[]) => ls.map((l) => l.id);
const com = (p: Partial<EstadoG2>): EstadoG2 => ({ ...ESTADO_VAZIO, ...p });

describe('ordenar', () => {
  it('texto em ordem natural pt-BR, sem caixa', () => {
    expect(ids(ordenar(LINHAS, COLUNAS, [{ chave: 'lote', direcao: 'asc' }]))).toEqual(['D', 'C', 'B', 'A']);
  });

  it('vazio fica no fim nas duas direções', () => {
    expect(ids(ordenar(LINHAS, COLUNAS, [{ chave: 'validade', direcao: 'desc' }]))).toEqual([
      'A',
      'D',
      'B',
      'C',
    ]);
    expect(ids(ordenar(LINHAS, COLUNAS, [{ chave: 'validade', direcao: 'asc' }]))).toEqual([
      'B',
      'D',
      'A',
      'C',
    ]);
  });

  it('vários critérios e número pelo valor exato', () => {
    const ordem = [
      { chave: 'produto', direcao: 'asc' },
      { chave: 'utilizavel', direcao: 'desc' },
    ] as const;
    expect(ids(ordenar(LINHAS, COLUNAS, ordem))).toEqual(['D', 'B', 'A', 'C']);
    expect(ids(ordenar(LINHAS, COLUNAS, [{ chave: 'utilizavel', direcao: 'asc' }]))).toEqual([
      'B',
      'C',
      'A',
      'D',
    ]);
    expect(ids(ordenar(LINHAS, COLUNAS, [{ chave: 'inexistente', direcao: 'asc' }]))).toEqual([
      'A',
      'B',
      'C',
      'D',
    ]);
  });
});

describe('filtrar', () => {
  it('busca em todas as colunas, sem acento e sem caixa', () => {
    expect(ids(filtrar(LINHAS, COLUNAS, com({ busca: 'ÍNSPE' })))).toEqual(['B']);
    expect(ids(filtrar(LINHAS, COLUNAS, com({ busca: '  herbi ' })))).toEqual(['A', 'C']);
    expect(normalizar('Inspeção')).toBe('inspecao');
  });

  it('valores, texto e intervalo por coluna', () => {
    expect(ids(filtrar(LINHAS, COLUNAS, com({ filtros: { estado: { valores: ['Liberado'] } } })))).toEqual([
      'A',
      'D',
    ]);
    expect(ids(filtrar(LINHAS, COLUNAS, com({ filtros: { estado: { valores: [] } } })))).toEqual([]);
    expect(ids(filtrar(LINHAS, COLUNAS, com({ filtros: { produto: { contem: 'CIDA' } } })))).toEqual([
      'A',
      'B',
      'C',
    ]);
    expect(ids(filtrar(LINHAS, COLUNAS, com({ filtros: { utilizavel: { de: '2.5', ate: '10' } } })))).toEqual(
      ['A', 'C'],
    );
    expect(ids(filtrar(LINHAS, COLUNAS, com({ filtros: { validade: { de: '2027-01-01' } } })))).toEqual([
      'A',
      'D',
    ]);
    expect(ids(filtrar(LINHAS, COLUNAS, com({ filtros: { validade: { ate: '2026-12-01' } } })))).toEqual([
      'B',
    ]);
  });

  it('intervalo de data inclui o dia inteiro de um instante', () => {
    const col: ColunaG2[] = [{ chave: 'q', rotulo: 'Quando', tipo: 'data' }];
    const l: LinhaG2 = {
      id: 'x',
      href: '',
      celulas: { q: { texto: '', valor: '2026-09-28T14:05:00.000Z' } },
    };
    expect(filtrar([l], col, com({ filtros: { q: { de: '2026-09-28', ate: '2026-09-28' } } }))).toHaveLength(
      1,
    );
  });

  it('valores da coluna com contagem, considerando só os outros filtros', () => {
    const estado = com({
      filtros: { produto: { valores: ['Herbicida'] }, estado: { valores: ['Liberado'] } },
    });
    expect(valoresDaColuna(LINHAS, COLUNAS, estado, 'estado')).toEqual([
      { texto: 'Liberado', contagem: 1 },
      { texto: 'Recebido', contagem: 1 },
    ]);
    expect(valoresDaColuna(LINHAS, COLUNAS, ESTADO_VAZIO, 'estado')).toEqual([
      { texto: 'Em inspeção', contagem: 1 },
      { texto: 'Liberado', contagem: 2 },
      { texto: 'Recebido', contagem: 1 },
    ]);
    expect(valoresDaColuna(LINHAS, COLUNAS, ESTADO_VAZIO, 'validade').at(-1)).toEqual({
      texto: '',
      contagem: 1,
    });
    expect(valoresDaColuna(LINHAS, COLUNAS, ESTADO_VAZIO, 'nada')).toEqual([]);
  });
});

describe('somar e agrupar', () => {
  it('soma exata só com a mesma unidade', () => {
    expect(somar([A, C], 'utilizavel')).toEqual({ valor: '12.500000', unidade: 'L' });
    expect(somar([A, D], 'utilizavel')).toBeNull();
    expect(somar([], 'utilizavel')).toBeNull();
    expect(somar([A], 'lote')).toBeNull();
  });

  it('grupos na ordem da coluna, com contagem e soma; total só se a unidade bate', () => {
    const r = resultado(LINHAS, COLUNAS, com({ agrupar: 'produto' }));
    expect(r.total).toBe(4);
    expect(r.grupos?.map((g) => [g.texto, ids(g.linhas), g.somas['utilizavel']])).toEqual([
      ['Adubo', ['D'], { valor: '1000.000000', unidade: 'kg' }],
      ['Fungicida', ['B'], { valor: '0.000000', unidade: 'L' }],
      ['Herbicida', ['A', 'C'], { valor: '12.500000', unidade: 'L' }],
    ]);
    expect(r.totais).toEqual({ utilizavel: null });
    const desc = resultado(
      LINHAS,
      COLUNAS,
      com({ agrupar: 'produto', ordem: [{ chave: 'produto', direcao: 'desc' }] }),
    );
    expect(desc.grupos?.map((g) => g.texto)).toEqual(['Herbicida', 'Fungicida', 'Adubo']);
    const soL = resultado(LINHAS, COLUNAS, com({ filtros: { produto: { valores: ['Herbicida'] } } }));
    expect(soL.totais).toEqual({ utilizavel: { valor: '12.500000', unidade: 'L' } });
    expect(resultado(LINHAS, COLUNAS, com({ agrupar: 'lote' })).grupos).toBeNull();
  });

  it('grupo de valor vazio vai para o fim', () => {
    const col: ColunaG2[] = [{ chave: 'p', rotulo: 'P', tipo: 'texto', agrupavel: true }];
    const l = (id: string, v: string): LinhaG2 => ({ id, href: '', celulas: { p: { texto: v, valor: v } } });
    const r = resultado([l('1', ''), l('2', 'b'), l('3', 'a')], col, com({ agrupar: 'p' }));
    expect(r.grupos?.map((g) => g.texto)).toEqual(['a', 'b', '']);
  });
});

describe('estado na URL e volta do detalhe', () => {
  const estado: EstadoG2 = {
    ordem: [
      { chave: 'validade', direcao: 'desc' },
      { chave: 'lote', direcao: 'asc' },
    ],
    filtros: {
      estado: { valores: ['Liberado', 'Em inspeção'] },
      utilizavel: { de: '2.5' },
      lote: { contem: 'L-' },
    },
    busca: 'herb',
    agrupar: 'produto',
  };

  it('ida e volta sem perda', () => {
    const url = urlDoEstado(estado).toString();
    expect(url).toBe(
      'ordem=-validade%2Clote&busca=herb&agrupar=produto&v.estado=Liberado&v.estado=Em+inspe%C3%A7%C3%A3o' +
        '&de.utilizavel=2.5&c.lote=L-',
    );
    expect(estadoDaUrl(new URLSearchParams(url), COLUNAS)).toEqual({
      ...estado,
      filtros: { lote: { contem: 'L-' }, estado: estado.filtros['estado'], utilizavel: { de: '2.5' } },
    });
    expect(urlDoEstado(ESTADO_VAZIO).toString()).toBe('');
  });

  it('ignora coluna desconhecida, formato inválido e agrupamento não permitido', () => {
    expect(
      estadoDaUrl(
        {
          ordem: 'x,-lote,lote',
          agrupar: 'lote',
          'de.utilizavel': '1e9',
          'ate.validade': '31/12/2026',
          'de.validade': '2026-01-01',
          'de.lote': '1',
          'v.nada': 'a',
          'v.produto': ['Herbicida', 'Adubo'],
          busca: 'x'.repeat(300),
        },
        COLUNAS,
      ),
    ).toEqual({
      ordem: [{ chave: 'lote', direcao: 'desc' }],
      filtros: { produto: { valores: ['Herbicida', 'Adubo'] }, validade: { de: '2026-01-01' } },
      busca: 'x'.repeat(100),
      agrupar: null,
    });
    expect(estadoDaUrl({}, COLUNAS)).toEqual(ESTADO_VAZIO);
  });

  it('link do detalhe leva o estado; a volta reescreve só a consulta, com o caminho fixo', () => {
    expect(hrefComVolta('/estoque/x', ESTADO_VAZIO)).toBe('/estoque/x');
    expect(hrefComVolta('/estoque/x', com({ ordem: [{ chave: 'validade', direcao: 'desc' }] }))).toBe(
      '/estoque/x?volta=ordem%3D-validade',
    );
    expect(caminhoDeVolta('/estoque', 'ordem=-validade&busca=a b')).toBe(
      '/estoque?ordem=-validade&busca=a+b',
    );
    expect(caminhoDeVolta('/estoque', 'https://evil.example/x')).toBe(
      '/estoque?https%3A%2F%2Fevil.example%2Fx=',
    );
    expect(caminhoDeVolta('/estoque', undefined)).toBe('/estoque');
    expect(caminhoDeVolta('/estoque', ['a=1'])).toBe('/estoque');
    expect(caminhoDeVolta('/estoque', 'a='.repeat(1100))).toBe('/estoque');
  });
});

describe('interação', () => {
  it('clique gira crescente, decrescente e sem ordem; Shift soma critério', () => {
    expect(alternarOrdem([], 'lote', false)).toEqual([{ chave: 'lote', direcao: 'asc' }]);
    expect(alternarOrdem([{ chave: 'lote', direcao: 'asc' }], 'lote', false)).toEqual([
      { chave: 'lote', direcao: 'desc' },
    ]);
    expect(alternarOrdem([{ chave: 'lote', direcao: 'desc' }], 'lote', false)).toEqual([]);
    const um = [{ chave: 'produto', direcao: 'asc' }] as const;
    expect(alternarOrdem(um, 'lote', true)).toEqual([...um, { chave: 'lote', direcao: 'asc' }]);
    expect(alternarOrdem([...um, { chave: 'lote', direcao: 'asc' }], 'lote', true)).toEqual([
      ...um,
      { chave: 'lote', direcao: 'desc' },
    ]);
    expect(alternarOrdem([...um, { chave: 'lote', direcao: 'desc' }], 'lote', true)).toEqual(um);
    expect(alternarOrdem(um, 'lote', false)).toEqual([{ chave: 'lote', direcao: 'asc' }]);
  });

  it('trocar e tirar filtros sem mutar o estado anterior', () => {
    const antes = { a: { contem: 'x' }, b: { valores: ['1'] } };
    expect(comFiltro(antes, 'a', null)).toEqual({ b: { valores: ['1'] } });
    expect(comFiltro(antes, 'a', {})).toEqual({ b: { valores: ['1'] } });
    expect(comFiltro(antes, 'c', { de: '1' })).toEqual({ ...antes, c: { de: '1' } });
    expect(antes).toEqual({ a: { contem: 'x' }, b: { valores: ['1'] } });
    expect(semCampo({ valores: ['1'], contem: 'x' }, 'valores')).toEqual({ contem: 'x' });
  });
});
