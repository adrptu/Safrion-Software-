// F0-c (parte independente do login): identidade do ambiente, /saude e demonstração (PRD 23.4; plano R-006, passo 8).
import { EsquemaSaude } from '@safrion/contracts';
import pg from 'pg';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import {
  ErroAmbiente,
  definirIdentidadeAmbiente,
  type Demonstracao,
  estadoDeSaude,
  lerIdentidadeAmbiente,
  restaurarDemonstracao,
} from '../src/ambiente.js';
import { executarCli } from '../src/cli/demo-reset.js';
import { emOrganizacao } from '../src/sessao.js';
import { contagens, criarBanco, semear, type Ambiente } from './ambiente.js';

let hml: Ambiente;
let prod: Ambiente;
let primeira: Demonstracao;
beforeAll(async () => {
  hml = await criarBanco();
  prod = await criarBanco();
});
afterAll(async () => {
  await hml.encerrar();
  await prod.encerrar();
});

const INFO = { versao: '0.0.0-teste', commit: 'abc1234' };
const codigo = async (p: Promise<unknown>) => {
  const e: unknown = await p.then(
    () => undefined,
    (x: unknown) => x,
  );
  return e instanceof ErroAmbiente ? e.codigo : 'OUTRO';
};
const comMigrator = async <T>(amb: Ambiente, fn: (c: pg.Client) => Promise<T>) => {
  const c = new pg.Client({ connectionString: amb.url('migrator') });
  await c.connect();
  try {
    return await fn(c);
  } finally {
    await c.end();
  }
};

describe('identidade do ambiente e saúde', () => {
  it('banco sem identidade: /saude diz sem_identidade e a demonstração recusa sem tocar em nada', async () => {
    expect(await lerIdentidadeAmbiente(hml.app)).toBeNull();
    const saude = await estadoDeSaude(hml.app, INFO);
    expect(saude).toMatchObject({
      status: 'sem_identidade',
      ambiente: null,
      migracao: '0002_ambiente_e_demonstracao.sql',
    });
    expect(
      await codigo(restaurarDemonstracao(hml.app, { confirmar: 'hml', ambienteDoProcesso: 'hml' })),
    ).toBe('IDENTIDADE_AUSENTE');
  });

  it('a identidade é gravada uma vez: repetir o mesmo nome não faz nada, outro nome é recusado', async () => {
    await comMigrator(hml, (c) => definirIdentidadeAmbiente(c, 'hml'));
    await comMigrator(hml, (c) => definirIdentidadeAmbiente(c, 'hml'));
    expect(await codigo(comMigrator(hml, (c) => definirIdentidadeAmbiente(c, 'prod')))).toBe(
      'IDENTIDADE_DIVERGENTE',
    );
    expect(await lerIdentidadeAmbiente(hml.app)).toBe('hml');
  });

  it('nem o dono altera ou apaga a identidade; a aplicação não grava nela', async () => {
    for (const sql of [
      "UPDATE app.environment_identity SET name = 'prod'",
      'DELETE FROM app.environment_identity',
    ]) {
      await expect(hml.migrator.query(sql), sql).rejects.toMatchObject({ code: 'P0001' });
    }
    await expect(
      hml.app.query("INSERT INTO app.environment_identity (name) VALUES ('dev')"),
    ).rejects.toMatchObject({
      code: '42501',
    });
  });

  it('/saude segue o contrato e não expõe endereço, usuário nem senha do banco', async () => {
    const saude = await estadoDeSaude(hml.app, INFO, () => new Date('2026-09-27T20:00:00Z'));
    expect(EsquemaSaude.parse(saude)).toEqual({
      status: 'ok',
      ambiente: 'hml',
      versao: '0.0.0-teste',
      commit: 'abc1234',
      migracao: '0002_ambiente_e_demonstracao.sql',
      verificadoEm: '2026-09-27T20:00:00.000Z',
    });
    const texto = JSON.stringify(saude);
    for (const sigilo of ['postgres', 'app_runtime', '127.0.0.1', 'password'])
      expect(texto).not.toContain(sigilo);
  });

  it('banco fora do ar: /saude responde indisponivel, sem exceção e sem detalhe do driver', async () => {
    const fora = new pg.Pool({
      connectionString: 'postgresql://ninguem@127.0.0.1:1/nada',
      connectionTimeoutMillis: 2000,
    });
    try {
      const saude = await estadoDeSaude(fora, INFO);
      expect(EsquemaSaude.safeParse(saude).success).toBe(true);
      expect(saude).toMatchObject({ status: 'indisponivel', ambiente: null, migracao: null });
      expect(JSON.stringify(saude)).not.toMatch(/ECONNREFUSED|ninguem|127\.0\.0\.1/);
    } finally {
      await fora.end();
    }
  });
});

describe('demonstração com dados fictícios (pnpm demo:reset)', () => {
  it('as travas recusam: processo de outro ambiente e confirmação com outro nome', async () => {
    expect(
      await codigo(restaurarDemonstracao(hml.app, { confirmar: 'hml', ambienteDoProcesso: 'dev' })),
    ).toBe('IDENTIDADE_DIVERGENTE');
    expect(
      await codigo(restaurarDemonstracao(hml.app, { confirmar: 'hml', ambienteDoProcesso: undefined })),
    ).toBe('IDENTIDADE_DIVERGENTE');
    expect(
      await codigo(restaurarDemonstracao(hml.app, { confirmar: 'dev', ambienteDoProcesso: 'hml' })),
    ).toBe('CONFIRMACAO_DIVERGENTE');
    const vazio = await hml.migrator.query('SELECT count(*)::int n FROM app.demo_state');
    expect(vazio.rows[0]).toEqual({ n: 0 });
  });

  it('cria uma organização fictícia com almoxarife, gerente e lote, sem tocar na organização real', async () => {
    const real = await semear(hml.app, 'Real');
    const antes = await contagens(hml.app, real.org);
    const d = await restaurarDemonstracao(hml.app, { confirmar: 'hml', ambienteDoProcesso: 'hml' });
    expect(d).toMatchObject({ ambiente: 'hml', geracao: 1 });
    primeira = d;
    const visto = await emOrganizacao(hml.app, d.organizationId, async (c) => ({
      org: (await c.query('SELECT name, fictitious FROM app.organization')).rows,
      papeis: (await c.query('SELECT role_code FROM app.user_role ORDER BY 1')).rows.map(
        (r: { role_code: string }) => r.role_code,
      ),
      lotes: (await c.query('SELECT id FROM app.lot')).rows.length,
    }));
    expect(visto).toEqual({
      org: [{ name: 'Demonstração · geração 1', fictitious: true }],
      papeis: ['almoxarife', 'gerente'],
      lotes: 1,
    });
    expect(await contagens(hml.app, real.org)).toEqual(antes);
  });

  it('restaurar de novo cria a geração 2 e mantém a anterior intacta (nada é apagado)', async () => {
    const d2 = await restaurarDemonstracao(hml.app, { confirmar: 'hml', ambienteDoProcesso: 'hml' });
    expect(d2.geracao).toBe(2);
    const estado = await hml.migrator.query<{ current_organization: string; generation: number }>(
      'SELECT current_organization, generation FROM app.demo_state',
    );
    expect(estado.rows[0]).toEqual({ current_organization: d2.organizationId, generation: 2 });
    const anterior = await emOrganizacao(hml.app, primeira.organizationId, async (c) => ({
      org: (await c.query<{ name: string }>('SELECT name FROM app.organization')).rows,
      lote: (await c.query<{ id: string }>('SELECT id FROM app.lot')).rows.map((r) => r.id),
    }));
    expect(anterior).toEqual({ org: [{ name: 'Demonstração · geração 1' }], lote: [primeira.loteId] });
  });

  it('em produção a demonstração é recusada, e nem escrita direta no ponteiro passa', async () => {
    await comMigrator(prod, (c) => definirIdentidadeAmbiente(c, 'prod'));
    expect(
      await codigo(restaurarDemonstracao(prod.app, { confirmar: 'prod', ambienteDoProcesso: 'prod' })),
    ).toBe('AMBIENTE_PROIBIDO');
    await expect(
      prod.app.query(
        'INSERT INTO app.demo_state (current_organization, generation) VALUES (gen_random_uuid(), 1)',
      ),
    ).rejects.toMatchObject({ code: 'P0001' });
  });

  it('o comando de linha: uso incorreto sai 2, recusa sai 1 sem efeito, sucesso sai 0', async () => {
    const linhas: string[] = [];
    const escrever = (l: string) => linhas.push(l);
    expect(await executarCli([], { DATABASE_URL: hml.url('app_runtime') }, escrever)).toBe(2);
    expect(await executarCli(['--desconhecido'], {}, escrever)).toBe(2);
    expect(
      await executarCli(
        ['--confirmar', 'prod'],
        { DATABASE_URL: prod.url('app_runtime'), SAFRION_AMBIENTE: 'prod' },
        escrever,
      ),
    ).toBe(1);
    expect(JSON.parse(linhas.at(-1) ?? '')).toMatchObject({
      resultado: 'recusado',
      codigo: 'AMBIENTE_PROIBIDO',
    });
    expect(
      await executarCli(
        ['--confirmar', 'hml'],
        { DATABASE_URL: hml.url('app_runtime'), SAFRION_AMBIENTE: 'hml' },
        escrever,
      ),
    ).toBe(0);
    expect(JSON.parse(linhas.at(-1) ?? '')).toMatchObject({
      resultado: 'demonstracao_restaurada',
      ambiente: 'hml',
      geracao: 3,
    });
    // Formato exato que o pnpm 12 entrega ao programa: o "--" separador vem junto (achado na prova com o comando real).
    expect(
      await executarCli(
        ['--', '--confirmar', 'hml'],
        { DATABASE_URL: hml.url('app_runtime'), SAFRION_AMBIENTE: 'hml' },
        escrever,
      ),
    ).toBe(0);
    expect(JSON.parse(linhas.at(-1) ?? '')).toMatchObject({
      resultado: 'demonstracao_restaurada',
      geracao: 4,
    });
    expect(linhas.join('\n')).not.toContain(hml.url('app_runtime'));
  });
});
