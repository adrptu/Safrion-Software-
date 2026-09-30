import { describe, expect, it } from 'vitest';
import { COMANDOS_CADASTRO } from '@safrion/contracts';
import { novaIntencao } from '../src/cadastros/intencao';
import { destinoConfirmado } from '../src/cadastros/retorno';
const id = 'a1111111-1111-4111-8111-111111111111';
const intencao = novaIntencao(COMANDOS_CADASTRO.editarTalhao, 'field', id, 1, { nome: 'T1' }, 'intencao-1');
const guardada = (volta: string) => ({
  intencao,
  campos: { nome: 'T1' },
  contexto: { tipo: 'talhao' as const, titulo: 'Salvar talhão', volta },
  criadaEm: '2026-09-30T20:00:00Z',
});
describe('retorno de cadastro confirmado', () => {
  it('abre o alvo do recibo e preserva filtros da listagem sem reabrir painel', () => {
    const destino = new URL(
      destinoConfirmado(guardada('/cadastros/areas?situacao=ativo&novo=talhao')),
      'http://local',
    );
    expect(destino.pathname).toBe('/cadastros/areas/' + id);
    expect(destino.searchParams.get('volta')).toBe('situacao=ativo');
  });
  it('recuperação a partir de outro detalhe não aninha a consulta', () => {
    const contexto = '/cadastros/areas/' + id + '?volta=' + encodeURIComponent('situacao=inativo&c.talhao=T');
    const destino = new URL(destinoConfirmado(guardada(contexto)), 'http://local');
    const volta = new URLSearchParams(destino.searchParams.get('volta') ?? '');
    expect(volta.get('situacao')).toBe('inativo');
    expect(volta.get('c.talhao')).toBe('T');
    expect(volta.has('volta')).toBe(false);
  });
});
