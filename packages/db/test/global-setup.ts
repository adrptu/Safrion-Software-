// Prepara o PostgreSQL dos testes de integração (ENG-034: banco real, nunca imitação):
// - na CI: contêiner PostgreSQL 17 + PostGIS 3.5 fixado por digest (Testcontainers);
// - fora dela, se SAFRION_TEST_DATABASE_URL apontar um servidor descartável com usuário administrador, usa esse servidor.
// Os papéis migrator e app_runtime são criados uma vez, com senhas geradas nesta execução.
import { randomUUID } from 'node:crypto';

import { PostgreSqlContainer, type StartedPostgreSqlContainer } from '@testcontainers/postgresql';
import pg from 'pg';
import type { TestProject } from 'vitest/node';

import { provisionarPapeis } from '../src/papeis.js';

export const IMAGEM =
  'postgis/postgis:17-3.5@sha256:01a6a70e41e6c4467c8f55f6063555ed72db2d6662cd0d571040d42eadaeb6f6';

declare module 'vitest' {
  export interface ProvidedContext {
    urlAdmin: string;
    senhaMigrator: string;
    senhaApp: string;
  }
}

export default async function setup(project: TestProject): Promise<() => Promise<void>> {
  let container: StartedPostgreSqlContainer | undefined;
  let url = process.env['SAFRION_TEST_DATABASE_URL'];
  if (!url) {
    container = await new PostgreSqlContainer(IMAGEM).start();
    url = container.getConnectionUri();
  }
  const senhas = { migrator: randomUUID(), appRuntime: randomUUID() };
  const admin = new pg.Client({ connectionString: url });
  await admin.connect();
  try {
    await provisionarPapeis(admin, senhas);
  } finally {
    await admin.end();
  }
  project.provide('urlAdmin', url);
  project.provide('senhaMigrator', senhas.migrator);
  project.provide('senhaApp', senhas.appRuntime);
  return async () => {
    await container?.stop();
  };
}
