import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { afterEach, describe, expect, it } from 'vitest';

const SCRIPT = join(dirname(fileURLToPath(import.meta.url)), '..', 'fronteiras.mjs');
const RAIZ_REAL = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const pastas: string[] = [];

function repositorio(arquivos: Record<string, string>): string {
  const raiz = mkdtempSync(join(tmpdir(), 'fronteiras-'));
  pastas.push(raiz);
  for (const [caminho, conteudo] of Object.entries(arquivos)) {
    mkdirSync(dirname(join(raiz, caminho)), { recursive: true });
    writeFileSync(join(raiz, caminho), conteudo);
  }
  return raiz;
}

function rodar(raiz: string) {
  const p = spawnSync(process.execPath, [SCRIPT, raiz], { encoding: 'utf8' });
  return { codigo: p.status, saida: p.stdout + p.stderr };
}

const MANIFESTO = JSON.stringify({ name: '@x/a', dependencies: { 'decimal.js': '10.6.0' } });

afterEach(() => {
  for (const p of pastas.splice(0)) rmSync(p, { recursive: true, force: true });
});

describe('fronteiras entre pacotes (ENG-012)', () => {
  it('pacote limpo passa', () => {
    const raiz = repositorio({
      'packages/a/package.json': MANIFESTO,
      'packages/a/src/x.ts':
        "import { Decimal } from 'decimal.js';\nimport { y } from './y.js';\nexport const x = [Decimal, y];\n",
      'packages/a/src/y.ts': 'export const y = 1;\n',
    });
    expect(rodar(raiz)).toMatchObject({ codigo: 0 });
  });

  it('ciclo de imports falha', () => {
    const raiz = repositorio({
      'packages/a/package.json': MANIFESTO,
      'packages/a/src/c1.ts': "import { c2 } from './c2.js';\nexport const c1 = c2;\n",
      'packages/a/src/c2.ts': "import { c1 } from './c1.js';\nexport const c2 = c1;\n",
    });
    const r = rodar(raiz);
    expect(r.codigo).toBe(1);
    expect(r.saida).toMatch(/ciclo de imports: .*c1\.ts → .*c2\.ts → .*c1\.ts/);
  });

  it('pacote não declarado falha, inclusive por import dinâmico e reexportação', () => {
    const raiz = repositorio({
      'packages/a/package.json': MANIFESTO,
      'packages/a/src/x.ts':
        "import fc from 'fast-check';\nexport * from 'zod';\nexport const f = () => import('lodash');\nexport { fc };\n",
    });
    const r = rodar(raiz);
    expect(r.codigo).toBe(1);
    for (const p of ['fast-check', 'zod', 'lodash']) expect(r.saida).toContain(`"${p}" não está declarado`);
  });

  it('import relativo que sai do src ou aponta para arquivo inexistente falha', () => {
    const raiz = repositorio({
      'packages/a/package.json': MANIFESTO,
      'packages/a/src/x.ts':
        "import { t } from '../test/helper.js';\nimport { z } from './nao-existe.js';\nexport const x = [t, z];\n",
      'packages/a/test/helper.ts': 'export const t = 1;\n',
    });
    const r = rodar(raiz);
    expect(r.codigo).toBe(1);
    expect(r.saida).toContain('sai de packages/a/src');
    expect(r.saida).toContain('aponta para arquivo inexistente');
  });

  it('o repositório real passa', () => {
    expect(rodar(RAIZ_REAL)).toMatchObject({ codigo: 0 });
  });
});
