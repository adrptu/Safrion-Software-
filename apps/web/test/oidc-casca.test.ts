// Ligação do adaptador OIDC do Codex à casca: configuração pelo ambiente e descoberta memorizada por processo, sem
// guardar falha. O fluxo HTTP completo, com banco real, está em rotas.int.test.ts.
import type pg from 'pg';
import { describe, expect, it } from 'vitest';

import type { ProvedorIdentidade } from '../src/identidade/provedor';
import { configuracaoOidc, criarFabricaOidc } from '../src/servidor/oidc';

const ENV = {
  SAFRION_OIDC_ISSUER: 'https://idp.sintetico.invalid',
  SAFRION_OIDC_CLIENT_ID: 'cliente',
  SAFRION_OIDC_CLIENT_SECRET: 'segredo-sintetico',
};
const D = { banco: {} as pg.Pool, origem: 'https://hml.safrion.invalid' };
const provedor = { nome: 'oidc' } as ProvedorIdentidade;

describe('configuração do OIDC pelo ambiente', () => {
  it('callback é a rota fixa na origem configurada; faltando qualquer variável, não há configuração', () => {
    expect(configuracaoOidc(ENV, D.origem)).toEqual({
      issuer: ENV.SAFRION_OIDC_ISSUER,
      clientId: 'cliente',
      clientSecret: 'segredo-sintetico',
      callback: 'https://hml.safrion.invalid/entrar/retorno',
    });
    expect(configuracaoOidc(ENV, `${D.origem}/`)?.callback).toBe(
      'https://hml.safrion.invalid/entrar/retorno',
    );
    for (const falta of Object.keys(ENV)) {
      expect(configuracaoOidc({ ...ENV, [falta]: undefined }, D.origem), falta).toBeNull();
      expect(configuracaoOidc({ ...ENV, [falta]: '' }, D.origem), falta).toBeNull();
    }
  });
});

describe('fábrica do provedor', () => {
  it('sem configuração devolve null e não tenta descobrir', async () => {
    let chamadas = 0;
    const fabrica = criarFabricaOidc({
      env: {},
      criar: () => {
        chamadas++;
        return Promise.resolve(provedor);
      },
    });
    expect(await fabrica(D)).toBeNull();
    expect(chamadas).toBe(0);
  });

  it('descobre uma vez por processo, inclusive com pedidos simultâneos', async () => {
    let chamadas = 0;
    const fabrica = criarFabricaOidc({
      env: ENV,
      criar: (configuracao) => {
        chamadas++;
        expect(configuracao.callback).toBe('https://hml.safrion.invalid/entrar/retorno');
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve(provedor);
          }, 10);
        });
      },
    });
    const simultaneos = await Promise.all([fabrica(D), fabrica(D), fabrica(D)]);
    expect(simultaneos).toEqual([provedor, provedor, provedor]);
    expect(await fabrica(D)).toBe(provedor);
    expect(chamadas).toBe(1);
  });

  it('falha não fica guardada: o provedor que volta a responder serve sem reiniciar', async () => {
    let chamadas = 0;
    const fabrica = criarFabricaOidc({
      env: ENV,
      criar: () => {
        chamadas++;
        return chamadas === 1
          ? Promise.reject(new Error('PROVEDOR_INDISPONIVEL'))
          : Promise.resolve(provedor);
      },
    });
    await expect(fabrica(D)).rejects.toThrow('PROVEDOR_INDISPONIVEL');
    expect(await fabrica(D)).toBe(provedor);
    expect(await fabrica(D)).toBe(provedor);
    expect(chamadas).toBe(2);
  });
});
