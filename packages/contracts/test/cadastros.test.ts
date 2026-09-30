import { describe, expect, it } from 'vitest';

import {
  ALVOS_CADASTRO,
  COMANDOS_CADASTRO,
  EsquemaAreaHa,
  EsquemaDadosAlterarSituacaoTalhao,
  EsquemaDadosCriarFazenda,
  EsquemaDadosCriarTalhao,
  EsquemaDadosEditarFazenda,
  EsquemaDadosEditarTalhao,
  EsquemaFuso,
  EsquemaNomeCadastro,
  FUSOS_BRASIL,
  FUSO_PADRAO,
  MENSAGENS_AREA,
  lerAreaPtBr,
  normalizarNome,
} from '../src/index.js';

const FAZENDA = '0f5c1d9e-2b7a-4c3d-8e1f-6a5b4c3d2e1f';

function recusa(
  esquema: { safeParse(v: unknown): { success: boolean; error?: { issues: { message: string }[] } } },
  v: unknown,
) {
  const r = esquema.safeParse(v);
  expect(r.success, JSON.stringify(v)).toBe(false);
  return r.error?.issues.map((i) => i.message) ?? [];
}

describe('nome de cadastro (contrato CAD-01 §3)', () => {
  it('normaliza como o banco: NFC, espaços Unicode colapsados e pontas aparadas', () => {
    expect(normalizarNome('  Boa\u00a0 Vista\t')).toBe('Boa Vista');
    expect(normalizarNome('\u2003Boa\u3000Vista\u00a0')).toBe('Boa Vista');
    expect(normalizarNome('Cafe\u0301')).toBe('Café');
    expect(normalizarNome('T1')).toBe('T1');
  });

  it('entra no comando já normalizado; vazio e mais de 80 caracteres são recusados', () => {
    expect(EsquemaNomeCadastro.parse('  T1 ')).toBe('T1');
    expect(recusa(EsquemaNomeCadastro, ' \u00a0 ')).toContain('NOME_VAZIO');
    expect(recusa(EsquemaNomeCadastro, 'x'.repeat(81))).toContain('NOME_LONGO');
    expect(EsquemaNomeCadastro.parse('x'.repeat(80))).toHaveLength(80);
    // Conta caracteres como o char_length do banco: emoji vale 1.
    expect(EsquemaNomeCadastro.parse('🌱'.repeat(80))).toBe('🌱'.repeat(80));
    expect(recusa(EsquemaNomeCadastro, 42)).not.toHaveLength(0);
  });
});

describe('área declarada no comando', () => {
  it('aceita decimal canônico maior que zero e devolve sem zeros à direita', () => {
    expect(EsquemaAreaHa.parse('204')).toBe('204');
    expect(EsquemaAreaHa.parse('204.500000')).toBe('204.5');
    expect(EsquemaAreaHa.parse('0.000001')).toBe('0.000001');
    expect(EsquemaAreaHa.parse('99999999.999999')).toBe('99999999.999999');
  });

  it('recusa zero, negativo, mais de 6 casas, mais de 8 dígitos inteiros e número JSON', () => {
    expect(recusa(EsquemaAreaHa, '0')).toContain('AREA_NAO_POSITIVA');
    expect(recusa(EsquemaAreaHa, '-1')).toContain('AREA_NAO_POSITIVA');
    expect(recusa(EsquemaAreaHa, '1.0000001')).toContain('AREA_CASAS');
    expect(recusa(EsquemaAreaHa, '100000000')).toContain('AREA_GRANDE');
    expect(recusa(EsquemaAreaHa, 204)).not.toHaveLength(0);
    expect(recusa(EsquemaAreaHa, '204,5')).not.toHaveLength(0);
  });
});

describe('área digitada em pt-BR', () => {
  it.each([
    ['204', '204'],
    ['204,5', '204.5'],
    ['1.204,50', '1204.5'],
    ['1.204.500', '1204500'],
    ['1.204.500,25', '1204500.25'],
    ['204.5', '204.5'],
    ['1.2345', '1.2345'],
    [' 0,5 ', '0.5'],
    ['00204', '204'],
    ['1 204,5', '1204.5'],
  ])('%s → %s', (digitado, canonico) => {
    expect(lerAreaPtBr(digitado)).toEqual({ ok: true, valor: canonico });
  });

  it('"1.204" é ambíguo e recusado com a instrução (decisão técnica do contrato §3)', () => {
    expect(lerAreaPtBr('1.204')).toEqual({
      ok: false,
      erro: 'AREA_AMBIGUA',
      mensagem: MENSAGENS_AREA.AREA_AMBIGUA,
    });
    expect(lerAreaPtBr('12.345')).toMatchObject({ ok: false, erro: 'AREA_AMBIGUA' });
  });

  it.each([
    ['', 'AREA_INVALIDA'],
    ['abc', 'AREA_INVALIDA'],
    [',5', 'AREA_INVALIDA'],
    ['1,2,3', 'AREA_INVALIDA'],
    ['0', 'AREA_NAO_POSITIVA'],
    ['0,0000001', 'AREA_CASAS'],
    ['123.456.789', 'AREA_GRANDE'],
  ])('%s → recusa %s', (digitado, erro) => {
    expect(lerAreaPtBr(digitado)).toMatchObject({ ok: false, erro });
  });
});

describe('fuso', () => {
  it('padrão de Brasília, zonas do Brasil válidas e nome fora do IANA recusado', () => {
    expect(FUSO_PADRAO).toBe('America/Sao_Paulo');
    expect(FUSOS_BRASIL[0]).toBe(FUSO_PADRAO);
    for (const f of FUSOS_BRASIL) expect(EsquemaFuso.parse(f), f).toBe(f);
    expect(recusa(EsquemaFuso, 'Brasil/Brasilia')).toContain('FUSO_INVALIDO');
    expect(recusa(EsquemaFuso, '')).toContain('FUSO_INVALIDO');
  });
});

describe('dados dos comandos (contrato CAD-01 §4)', () => {
  it('criar fazenda e talhão: estritos e na forma canônica', () => {
    expect(EsquemaDadosCriarFazenda.parse({ nome: ' Boa  Vista ', fuso: FUSO_PADRAO })).toEqual({
      nome: 'Boa Vista',
      fuso: FUSO_PADRAO,
    });
    expect(EsquemaDadosCriarTalhao.parse({ fazenda: FAZENDA, nome: 'T1', areaDeclaradaHa: '204.0' })).toEqual(
      {
        fazenda: FAZENDA,
        nome: 'T1',
        areaDeclaradaHa: '204',
      },
    );
    recusa(EsquemaDadosCriarFazenda, { nome: 'Boa Vista', fuso: FUSO_PADRAO, organizationId: FAZENDA });
    recusa(EsquemaDadosCriarTalhao, { fazenda: 'nao-e-uuid', nome: 'T1', areaDeclaradaHa: '1' });
  });

  it('editar exige pelo menos um campo', () => {
    expect(recusa(EsquemaDadosEditarFazenda, {})).toContain('NADA_A_ALTERAR');
    expect(recusa(EsquemaDadosEditarTalhao, {})).toContain('NADA_A_ALTERAR');
    expect(EsquemaDadosEditarFazenda.parse({ fuso: 'America/Cuiaba' })).toEqual({ fuso: 'America/Cuiaba' });
    expect(EsquemaDadosEditarTalhao.parse({ areaDeclaradaHa: '10.50' })).toEqual({ areaDeclaradaHa: '10.5' });
    expect(EsquemaDadosEditarTalhao.parse({ fazenda: FAZENDA })).toEqual({ fazenda: FAZENDA });
  });

  it('situação só ativo ou inativo', () => {
    expect(EsquemaDadosAlterarSituacaoTalhao.parse({ situacao: 'inativo' })).toEqual({ situacao: 'inativo' });
    recusa(EsquemaDadosAlterarSituacaoTalhao, { situacao: 'excluido' });
  });

  it('cada comando tem o seu tipo de alvo', () => {
    expect(Object.keys(ALVOS_CADASTRO).sort()).toEqual(Object.values(COMANDOS_CADASTRO).sort());
    expect(ALVOS_CADASTRO[COMANDOS_CADASTRO.criarFazenda]).toBe('farm');
    expect(ALVOS_CADASTRO[COMANDOS_CADASTRO.alterarSituacaoTalhao]).toBe('field');
  });
});
