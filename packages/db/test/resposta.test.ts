import { EsquemaErro, EsquemaUuid, falhaPermanenteSemGravacao } from '@safrion/contracts';
import { ErroDominio } from '@safrion/domain';
import { describe, expect, it } from 'vitest';
import { z } from 'zod';

import { ErroComando, type CodigoErroComando } from '../src/erros.js';
import { respostaDeErro } from '../src/resposta.js';
import { ehUuid } from '../src/sessao.js';

describe('resposta de erro do envelope (ENG-015)', () => {
  it('cada código do envelope vira um erro do contrato; detalhe interno não sai', () => {
    const casos: [CodigoErroComando, Record<string, unknown>, string, number][] = [
      ['CONTRATO_INVALIDO', { campos: ['actorId'] }, 'CONTRATO_INVALIDO', 400],
      ['ORGANIZACAO_INVALIDA', {}, 'ORGANIZACAO_INVALIDA', 401],
      ['IDEMPOTENCY_KEY_REUSED', { receiptId: 'r' }, 'IDEMPOTENCY_KEY_REUSED', 409],
      ['IDEMPOTENCY_IN_PROGRESS', { repetirEmMs: 2000 }, 'IDEMPOTENCY_IN_PROGRESS', 409],
      [
        'FALHA_TRANSITORIA',
        { resultadoIncerto: true, causa: 'senha do banco', codigoPg: '57P01' },
        'FALHA_TRANSITORIA',
        503,
      ],
      ['MIGRACAO_ALTERADA', { arquivo: '0001.sql' }, 'FALHA_INTERNA', 500],
      // Classe 22 com o ROLLBACK confirmado (ENV-CAD01-NUL-CL22): 500 com o sinal de falha permanente, sem SQLSTATE nem
      // "repita".
      ['FALHA_INTERNA', { resultadoIncerto: false, codigoPg: '22P02' }, 'FALHA_INTERNA', 500],
    ];
    for (const [codigo, detalhe, esperado, status] of casos) {
      const r = respostaDeErro(new ErroComando(codigo, `mensagem ${codigo}`, detalhe), 'corr');
      expect(EsquemaErro.safeParse(r.corpo).success, codigo).toBe(true);
      expect([r.corpo.codigo, r.status]).toEqual([esperado, status]);
      const texto = JSON.stringify(r);
      for (const interno of ['senha do banco', '57P01', '0001.sql', '22P02', 'repita'])
        expect(texto).not.toContain(interno);
    }
    expect(
      respostaDeErro(new ErroComando('FALHA_TRANSITORIA', 'm', { resultadoIncerto: true }), 'c').corpo
        .detalhe,
    ).toEqual({
      resultadoIncerto: true,
    });
    expect(
      respostaDeErro(new ErroComando('CONTRATO_INVALIDO', 'm', { campos: ['actorId'] }), 'c').corpo.campos,
    ).toEqual([{ caminho: 'actorId', problema: 'invalido' }]);
  });

  it('falha permanente sem gravação: sinal público só para FALHA_INTERNA com o ROLLBACK confirmado (ENV-CAD01-NUL-CL22)', () => {
    const permanente = respostaDeErro(
      new ErroComando('FALHA_INTERNA', 'm', { resultadoIncerto: false, codigoPg: '22021' }),
      'c',
    );
    expect(permanente.status).toBe(500);
    expect(permanente.corpo.detalhe).toEqual({ resultadoIncerto: false, repetirMesmoConteudo: false });
    expect(falhaPermanenteSemGravacao(permanente.corpo)).toBe(true);
    expect(permanente.corpo.mensagem).toContain('nada foi gravado');
    expect(JSON.stringify(permanente)).not.toMatch(/22021|repita/i);
    for (const outro of [
      new ErroComando('FALHA_INTERNA', 'm', { resultadoIncerto: true }),
      new ErroComando('FALHA_INTERNA', 'm', {}),
      new ErroComando('MIGRACAO_ALTERADA', 'm', { resultadoIncerto: false }),
      new ErroComando('FALHA_TRANSITORIA', 'm', { resultadoIncerto: false }),
      new TypeError('x'),
    ]) {
      const r = respostaDeErro(outro, 'c');
      expect(EsquemaErro.safeParse(r.corpo).success).toBe(true);
      expect(falhaPermanenteSemGravacao(r.corpo), String(outro)).toBe(false);
    }
  });

  it('validação, domínio e erro inesperado', () => {
    const zod = z.string().safeParse(1);
    expect(respostaDeErro(zod.error, 'c').corpo.codigo).toBe('CONTRATO_INVALIDO');
    const dominio = respostaDeErro(new ErroDominio('DECIMAL_INVALIDO', 'x'), 'c');
    expect(dominio.corpo).toMatchObject({
      codigo: 'CONTRATO_INVALIDO',
      campos: [{ caminho: 'data', problema: 'DECIMAL_INVALIDO' }],
    });
    const inesperado = respostaDeErro(new TypeError('Cannot read properties of undefined (reading x)'), 'c');
    expect(inesperado).toMatchObject({
      status: 500,
      corpo: { codigo: 'FALHA_INTERNA', classe: 'infraestrutura' },
    });
    expect(JSON.stringify(inesperado)).not.toContain('Cannot read');
    expect(respostaDeErro('texto solto', 'c').corpo.codigo).toBe('FALHA_INTERNA');
  });

  it('o contrato e o envelope aceitam os mesmos UUIDs', () => {
    for (const v of [
      '3f2449ee-7729-4f0a-96cc-d0f539bf7a66',
      '3F2449EE-7729-4F0A-96CC-D0F539BF7A66',
      '3f2449ee-7729-0f0a-96cc-d0f539bf7a66',
      '3f2449ee-7729-4f0a-c6cc-d0f539bf7a66',
      '3f2449ee77294f0a96ccd0f539bf7a66',
      '',
    ]) {
      expect(EsquemaUuid.safeParse(v).success, v).toBe(ehUuid(v));
    }
  });
});
