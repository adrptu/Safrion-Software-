// Contrato do encerramento do banco descartável: não matar conexão ainda fechando e falhar de forma explícita se
// alguma não fechar. Achados do Codex: 57P01 sem ouvinte depois das asserções verdes (38131a8) e conexão retirada por
// release(erro) ainda fechando, que a correção anterior (1259888) não esperava. O fim das conexões é atrasado ou
// bloqueado de propósito, para a prova não depender da carga da máquina.
import { once } from 'node:events';

import pg from 'pg';
import { describe, expect, inject, it } from 'vitest';

import { criarBanco } from './ambiente.js';

type Fim = (cb?: (erro?: Error) => void) => void;

/** Troca o fim da conexão por um que só roda quando a função devolvida for chamada. */
function prenderFim(cliente: pg.Client | pg.PoolClient): () => void {
  let soltar = (): void => undefined;
  const solto = new Promise<void>((resolve) => {
    soltar = resolve;
  });
  const fim = cliente.end.bind(cliente) as Fim;
  (cliente as unknown as { end: Fim }).end = (cb) => {
    void solto.then(() => {
      fim(cb);
    });
  };
  return soltar;
}

describe('encerramento do banco descartável', () => {
  it('conexão retirada por release(erro) e ainda fechando: encerrar espera o fim real e não a derruba', async () => {
    const amb = await criarBanco();
    const pool = new pg.Pool({ connectionString: amb.url('app_runtime'), max: 1 });
    const cliente = await pool.connect();
    const erros: unknown[] = [];
    cliente.on('error', (erro: Error & { code?: string }) => erros.push(erro.code ?? erro.message));
    const terminou = once(cliente, 'end');
    const soltar = prenderFim(cliente);
    cliente.release(new Error('descartar esta conexão'));
    expect(pool.totalCount).toBe(0);
    let concluiu = false;
    const encerrando = amb.encerrar().then(() => {
      concluiu = true;
    });
    await Promise.race([encerrando, new Promise((resolve) => setTimeout(resolve, 100))]);
    const concluiuAntes = concluiu;
    soltar();
    await terminou;
    await encerrando;
    await pool.end();
    expect(concluiuAntes, 'encerrar concluiu antes do fim real da conexão retirada').toBe(false);
    expect(erros).toEqual([]);
  });

  it('com fechamento lento nos pools do helper, nenhum 57P01 chega a eles', async () => {
    const amb = await criarBanco();
    const erros: unknown[] = [];
    for (const pool of [amb.app, amb.migrator]) {
      pool.on('connect', (cliente) => {
        const fim = cliente.end.bind(cliente) as Fim;
        (cliente as unknown as { end: Fim }).end = (cb) => {
          setTimeout(() => {
            fim(cb);
          }, 300);
        };
      });
      // O ouvinte só registra; se algum erro chegar, a asserção abaixo falha (nada é engolido).
      pool.on('error', (erro: Error & { code?: string }) => erros.push(erro.code ?? erro.message));
    }
    await amb.migrator.query('SELECT 1');
    await amb.app.query('SELECT 1');
    await amb.encerrar();
    expect(erros).toEqual([]);
  });

  it('conexão que não fecha: encerrar falha com 55006 em vez de derrubá-la', async () => {
    const amb = await criarBanco();
    const cliente = new pg.Client({ connectionString: amb.url('app_runtime') });
    const erros: unknown[] = [];
    cliente.on('error', (erro: Error & { code?: string }) => erros.push(erro.code ?? erro.message));
    await cliente.connect();
    try {
      await expect(amb.encerrar()).rejects.toMatchObject({ code: '55006' });
      expect((await cliente.query<{ ok: number }>('SELECT 1 AS ok')).rows).toEqual([{ ok: 1 }]);
      expect(erros).toEqual([]);
    } finally {
      await cliente.end();
      const admin = new pg.Client({ connectionString: inject('urlAdmin') });
      await admin.connect();
      try {
        await admin.query(`DROP DATABASE ${amb.banco}`);
      } finally {
        await admin.end();
      }
    }
  });
});
