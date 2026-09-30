import { describe, expect, it } from 'vitest';
import { alteracoesCadastro } from '../src/cadastros/alteracoes';

const fazenda = 'a1111111-1111-4111-8111-111111111111';
const outra = 'b2222222-2222-4222-8222-222222222222';
const base = { nome: 'T1', fazenda, area: '204,000000' };

describe('alterações materiais de cadastro (P1 Claude)', () => {
  it('reaplica só nome e não inclui área/fazenda que a outra pessoa pode ter alterado', () => {
    expect(alteracoesCadastro('talhao', { ...base, nome: 'T1 Norte' }, base)).toEqual({ nome: 'T1 Norte' });
    expect(base).toEqual({ nome: 'T1', fazenda, area: '204,000000' });
  });
  it('normaliza área, espaços e NFC antes de decidir se há alteração', () => {
    const inicial = { ...base, nome: 'Café  Norte', area: '1000,000000' };
    expect(
      alteracoesCadastro('talhao', { ...inicial, nome: '  Café\u00a0Norte ', area: '1.000,00' }, inicial),
    ).toEqual({});
  });
  it('aceita fotografia legada com espaços brutos além do limite de transporte', () => {
    const inicial = { ...base, nome: ' '.repeat(1001) + 'Boa Vista' };
    expect(alteracoesCadastro('talhao', { ...base, nome: 'Boa Vista' }, inicial)).toEqual({});
    expect(alteracoesCadastro('talhao', { ...base, nome: 'Vista Sul' }, inicial)).toEqual({
      nome: 'Vista Sul',
    });
    // A entrada nova continua sujeita ao limite do esquema oficial.
    expect(alteracoesCadastro('talhao', inicial, base)).toBeNull();
  });
  it('inclui todos e somente os campos realmente editados', () => {
    expect(alteracoesCadastro('talhao', { ...base, fazenda: outra, area: '210,500' }, base)).toEqual({
      fazenda: outra,
      areaDeclaradaHa: '210.5',
    });
  });
  it('alterar e depois restaurar o valor inicial não é uma edição', () => {
    expect(alteracoesCadastro('talhao', { ...base, area: '204' }, base)).toEqual({});
  });
  it('edição de nome da fazenda não sobrescreve seu fuso', () => {
    const inicial = { nome: 'Norte', fuso: 'America/Sao_Paulo' };
    expect(alteracoesCadastro('fazenda', { ...inicial, nome: 'Sul' }, inicial)).toEqual({ nome: 'Sul' });
    expect(alteracoesCadastro('fazenda', { ...inicial, fuso: 'America/Manaus' }, inicial)).toEqual({
      fuso: 'America/Manaus',
    });
  });
  it('não inventa base em intenção antiga ou corrompida', () => {
    expect(alteracoesCadastro('talhao', base, undefined)).toBeNull();
    expect(alteracoesCadastro('talhao', base, { nome: 'T1' })).toBeNull();
    expect(alteracoesCadastro('talhao', base, { ...base, area: '1.204' })).toBeNull();
    expect(
      alteracoesCadastro(
        'fazenda',
        { nome: 'Sul', fuso: 'America/Sao_Paulo' },
        { nome: 'Norte', fuso: 'incorreto' },
      ),
    ).toBeNull();
  });
  it('não transforma entrada inválida em patch válido', () => {
    expect(alteracoesCadastro('talhao', { ...base, area: '0' }, base)).toBeNull();
    expect(alteracoesCadastro('talhao', { ...base, nome: 'T\u0000' }, base)).toBeNull();
  });
});
