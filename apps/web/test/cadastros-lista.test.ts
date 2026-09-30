import type { FazendaResumo, TalhaoResumo } from '@safrion/db/web';
import { describe, expect, it } from 'vitest';

import {
  COLUNAS_TALHAO,
  consultaComEstadoTabela,
  consultaDeRetorno,
  filtrosDaLista,
  formatarAreaHa,
  gruposDeFazenda,
  hrefComRetorno,
  linhaDoTalhao,
} from '../src/cadastros/lista';
import { caminhoDeVolta, estadoDaUrl, ESTADO_VAZIO, ordenar } from '../src/tabela/logica';

const FAZENDAS: readonly FazendaResumo[] = [
  {
    id: 'boa-vista',
    nome: 'Boa Vista',
    fuso: 'America/Sao_Paulo',
    situacao: 'ativa',
    versao: 1,
    talhoesAtivos: 1,
    areaAtivaHa: '204.000000',
  },
  {
    id: 'nova',
    nome: 'Nova',
    fuso: 'America/Manaus',
    situacao: 'ativa',
    versao: 1,
    talhoesAtivos: 0,
    areaAtivaHa: '0.000000',
  },
];
const ATIVO: TalhaoResumo = {
  id: 't1',
  nome: 'T1',
  fazenda: { id: 'boa-vista', nome: 'Boa Vista' },
  areaReferenciaHa: '204.000000',
  origemArea: 'declarada',
  areaDeclaradaHa: '204.000000',
  limite: null,
  situacao: 'ativo',
  versao: 1,
};
const INATIVO: TalhaoResumo = {
  ...ATIVO,
  id: 't2',
  nome: 'T2',
  areaReferenciaHa: '2000.000000',
  situacao: 'inativo',
};

describe('listagem CAD01 · contexto e totais', () => {
  it('mantém a fazenda vazia e os totais dos ativos ao consultar somente inativos', () => {
    const grupos = gruposDeFazenda(FAZENDAS, [ATIVO, INATIVO], { fazenda: '', situacao: 'inativo' });
    expect(grupos.map((g) => [g.fazenda.id, g.talhoes.map((t) => t.id)])).toEqual([
      ['boa-vista', ['t2']],
      ['nova', []],
    ]);
    expect(grupos[0]?.fazenda.areaAtivaHa).toBe('204.000000');
    expect(grupos[0]?.fazenda.talhoesAtivos).toBe(1);
  });

  it('fazenda selecionada e inexistente não misturam grupos nem talhões', () => {
    const consulta = filtrosDaLista(new URLSearchParams('fazenda=nova&situacao=ativo'));
    expect(gruposDeFazenda(FAZENDAS, [ATIVO, INATIVO], consulta).map((g) => g.talhoes)).toEqual([[]]);
    expect(gruposDeFazenda(FAZENDAS, [ATIVO], { fazenda: 'desconhecida', situacao: '' })).toEqual([]);
    expect(filtrosDaLista(new URLSearchParams('situacao=desconhecida'))).toEqual({
      fazenda: '',
      situacao: '',
    });
  });

  it('ordenar e limpar a tabela conserva o recorte de fazenda e situação', () => {
    const inicial = new URLSearchParams(
      'fazenda=boa-vista&situacao=ativo&novo=talhao&busca=antiga&c.talhao=antigo',
    );
    const ordenado = consultaComEstadoTabela(inicial, {
      ...ESTADO_VAZIO,
      ordem: [{ chave: 'area', direcao: 'desc' }],
    });
    expect(ordenado.get('fazenda')).toBe('boa-vista');
    expect(ordenado.get('situacao')).toBe('ativo');
    expect(ordenado.get('novo')).toBe('talhao');
    expect(ordenado.has('busca')).toBe(false);
    expect(ordenado.has('c.talhao')).toBe(false);
    expect(estadoDaUrl(ordenado, COLUNAS_TALHAO).ordem).toEqual([{ chave: 'area', direcao: 'desc' }]);
    const limpo = consultaComEstadoTabela(ordenado, ESTADO_VAZIO);
    expect(limpo.get('fazenda')).toBe('boa-vista');
    expect(limpo.has('ordem')).toBe(false);
  });

  it('voltar do detalhe recupera filtros e ordem sem reabrir criação', () => {
    const inicial = new URLSearchParams(
      'fazenda=boa-vista&situacao=ativo&ordem=-area&c.talhao=T&novo=talhao&volta=externa',
    );
    const volta = consultaDeRetorno(inicial);
    const href = linhaDoTalhao(ATIVO, volta).href;
    const detalhe = new URL(href, 'https://safrion.test');
    const retorno = caminhoDeVolta('/cadastros/areas', detalhe.searchParams.get('volta') ?? undefined);
    const restaurada = new URL(retorno, 'https://safrion.test');
    expect(restaurada.pathname).toBe('/cadastros/areas');
    expect(restaurada.searchParams.get('fazenda')).toBe('boa-vista');
    expect(restaurada.searchParams.get('situacao')).toBe('ativo');
    expect(restaurada.searchParams.get('ordem')).toBe('-area');
    expect(restaurada.searchParams.get('c.talhao')).toBe('T');
    expect(restaurada.searchParams.has('novo')).toBe(false);
    expect(restaurada.searchParams.has('volta')).toBe(false);
    expect(hrefComRetorno('/cadastros/fazendas/boa-vista', '')).toBe('/cadastros/fazendas/boa-vista');
  });
});

describe('área e origem na lista', () => {
  it('exibe duas casas sem ponto flutuante, arredonda transporte de dígito e não chama área pequena de zero', () => {
    expect(formatarAreaHa('204.000000')).toBe('204,00');
    expect(formatarAreaHa('1204.505000')).toBe('1.204,51');
    expect(formatarAreaHa('99999999999999.999999')).toBe('100.000.000.000.000,00');
    expect(formatarAreaHa('0.000001')).toBe('< 0,01');
    expect(formatarAreaHa('0')).toBe('0,00');
    expect(() => formatarAreaHa('-1.000000')).toThrow();
    expect(() => formatarAreaHa('204,5')).toThrow();
  });

  it('ordena por valor decimal apesar de texto pt-BR/origem e conserva situação sem depender de cor', () => {
    const linhas = [linhaDoTalhao(INATIVO), linhaDoTalhao(ATIVO)];
    expect(ordenar(linhas, COLUNAS_TALHAO, [{ chave: 'area', direcao: 'asc' }]).map((l) => l.id)).toEqual([
      't1',
      't2',
    ]);
    expect(linhas[1]?.celulas['area']).toEqual({
      texto: '204,00 · declarada',
      valor: '204.000000',
      unidade: 'ha',
    });
    expect(linhas[1]?.celulas['limite']?.texto).toBe('Sem limite no mapa');
    expect(linhas[0]?.celulas['situacao']?.texto).toBe('Inativo');
    expect(COLUNAS_TALHAO.find((c) => c.chave === 'area')?.somavel).toBeUndefined();
  });

  it('origem calculada e data do limite usam a fazenda, sem confundir a declarada preservada', () => {
    const linha = linhaDoTalhao(
      {
        ...ATIVO,
        origemArea: 'calculada',
        areaReferenciaHa: '203.504000',
        limite: { versao: 2, data: '2026-10-01T02:30:00.000Z' },
      },
      '',
      'America/Manaus',
    );
    expect(linha.celulas['area']?.texto).toBe('203,50 · calculada');
    expect(linha.celulas['limite']?.texto).toBe('Versão 2 · 30/09/2026 22:30');
    expect(
      linhaDoTalhao({ ...ATIVO, limite: { versao: 1, data: '2026-09-30' } }).celulas['limite']?.texto,
    ).toBe('Versão 1 · 30/09/2026');
  });
});
