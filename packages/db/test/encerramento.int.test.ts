// Encerramento do banco descartável sem erro não tratado (achado do Codex na revisão de 38131a8: 57P01 no pool do
// migrator depois de todas as asserções verdes). A corrida depende da carga da máquina; aqui o fechamento lento é
// simulado atrasando o fim de cada conexão, para a prova não depender do relógio.
import pg from 'pg';
import { describe, expect, it } from 'vitest';

import { criarBanco, fecharPool } from './ambiente.js';

const ATRASO_MS = 300;

/** Atrasa o fim de toda conexão que o pool abrir daqui em diante, como numa máquina carregada. */
function fechamentoLento(pool: pg.Pool): void {
  pool.on('connect', (cliente) => {
    const fim = cliente.end.bind(cliente) as (cb?: (erro?: Error) => void) => void;
    (cliente as unknown as { end: (cb?: (erro?: Error) => void) => void }).end = (cb) => {
      setTimeout(() => {
        fim(cb);
      }, ATRASO_MS);
    };
  });
}

describe('encerramento do banco descartável', () => {
  it('fecharPool só resolve depois que cada conexão fechou (pool.end sozinho resolve antes)', async () => {
    const amb = await criarBanco();
    const pool = new pg.Pool({ connectionString: amb.url('migrator'), max: 2 });
    try {
      await Promise.all([pool.query('SELECT pg_sleep(0.01)'), pool.query('SELECT pg_sleep(0.01)')]);
      const abertas = pool.totalCount;
      let fechadas = 0;
      pool.on('remove', () => {
        fechadas += 1;
      });
      await fecharPool(pool);
      expect(abertas).toBe(2);
      expect(fechadas).toBe(abertas);
    } finally {
      await amb.encerrar();
    }
  });

  it('com fechamento lento, encerrar não derruba conexão viva: nenhum 57P01 chega aos pools', async () => {
    const amb = await criarBanco();
    const erros: unknown[] = [];
    // O ouvinte só registra; se algum erro chegar, a asserção abaixo falha (nada é engolido).
    for (const pool of [amb.app, amb.migrator]) {
      fechamentoLento(pool);
      pool.on('error', (erro) => erros.push((erro as { code?: string }).code ?? erro.message));
    }
    await amb.migrator.query('SELECT 1');
    await amb.app.query('SELECT 1');
    await amb.encerrar();
    await new Promise((r) => setTimeout(r, ATRASO_MS + 200));
    expect(erros).toEqual([]);
  });
});
