import { randomUUID } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { expect, test, type APIRequestContext, type Page, type PlaywrightWorkerArgs } from '@playwright/test';
import pg from 'pg';

import { entrarComo } from './apoio';

// Isolamento entre organizações pelo HTTP do Next (HML-ISO), com entidades que existem dos dois lados. A é a demonstração
// atual, pelo login de DEV real; B é a geração anterior, que o e2e/servidor.mjs deixa com uma sessão criada pelas funções
// reais de login. A sessão de B é fixture do banco: prova autorização HTTP, não autenticação OIDC. Nenhum caso escreve no
// lote de A, para não mexer nos saldos que o estoque.spec.ts confere em sequência.

interface Lado {
  readonly organizationId: string;
  readonly loteId: string;
  readonly produtoId: string;
  readonly localId: string;
}
interface Fixture {
  readonly banco: string;
  readonly a: Lado;
  readonly b: Lado & { readonly sessao: string };
}

const porta = process.env['SAFRION_E2E_PORTA'] ?? '3200';
const ORIGEM = `http://localhost:${porta}`;
const COOKIE_SESSAO = '__Host-safrion-sessao';
const COMANDO = '/api/v1/comandos/estoque.registrar-entrada';

const fixture = (): Fixture =>
  JSON.parse(readFileSync(join(tmpdir(), `safrion-e2e-isolamento-${porta}.json`), 'utf8')) as Fixture;

/** Cliente HTTP sem navegador, com o cookie de sessão dado explicitamente (ou nenhum). */
function clienteHttp(playwright: PlaywrightWorkerArgs['playwright'], sessao?: string) {
  return playwright.request.newContext({
    baseURL: ORIGEM,
    extraHTTPHeaders: sessao ? { cookie: `${COOKIE_SESSAO}=${sessao}` } : {},
  });
}

/** Token da sessão que o login de DEV gravou no navegador. */
async function sessaoDoNavegador(page: Page): Promise<string> {
  const cookie = (await page.context().cookies()).find((c) => c.name === COOKIE_SESSAO);
  expect(cookie, 'o login de DEV grava o cookie de sessão').toBeDefined();
  return cookie?.value ?? '';
}

const entrada = (lado: Lado, versao: number, local = lado.localId) => ({
  idempotencyKey: randomUUID(),
  target: { type: 'lot', id: lado.loteId, expectedVersion: versao },
  data: {
    lote: lado.loteId,
    local,
    movimento: { tipo: 'entrada', quantidade: { valor: '5', unidade: 'L' }, situacao: 'liberado_livre' },
  },
});

const enviar = (cliente: APIRequestContext, corpo: unknown) =>
  cliente.post(COMANDO, { data: corpo, headers: { origin: ORIGEM } });

/** Versão, movimentos e soma na unidade-base do lote, lidos no banco pelo administrador (fora da RLS). */
async function estadoNoBanco(f: Fixture, loteId: string) {
  const url = new URL(process.env['SAFRION_TEST_DATABASE_URL'] ?? '');
  url.pathname = `/${f.banco}`;
  const c = new pg.Client({ connectionString: url.toString() });
  await c.connect();
  try {
    const r = await c.query<{ versao: string; movimentos: string; soma: string }>(
      `SELECT l.version::text AS versao, count(m.id)::text AS movimentos, coalesce(sum(m.base_quantity), 0)::text AS soma
         FROM app.lot l LEFT JOIN app.stock_movement m ON m.lot_id = l.id WHERE l.id = $1 GROUP BY l.version`,
      [loteId],
    );
    const linha = r.rows[0];
    if (!linha) throw new Error('lote da fixture ausente no banco');
    return { versao: Number(linha.versao), movimentos: Number(linha.movimentos), soma: linha.soma };
  } finally {
    await c.end();
  }
}

test('HML-ISO-01: listas e detalhes de outra organização ficam fora; cada lado vê os seus', async ({
  page,
  playwright,
}) => {
  const f = fixture();
  const b = await clienteHttp(playwright, f.b.sessao);
  try {
    // Controle positivo de B: os IDs usados abaixo existem e abrem para quem é de B.
    expect((await b.get(`/estoque/${f.b.loteId}`)).status()).toBe(200);
    expect((await b.get(`/cadastros/produtos/${f.b.produtoId}`)).status()).toBe(200);
    const listasB =
      (await (await b.get('/estoque')).text()) + (await (await b.get('/cadastros/produtos')).text());
    // Comparação por ID, com mensagem curta: a página inteira não vai para o log.
    expect(listasB.includes(`/estoque/${f.b.loteId}`), 'lote de B na lista de B').toBe(true);
    expect(listasB.includes(`/cadastros/produtos/${f.b.produtoId}`), 'produto de B na lista de B').toBe(true);
    for (const id of [f.a.loteId, f.a.produtoId])
      expect(listasB.includes(id), 'ID de A nas listas de B').toBe(false);
    // B também não abre os de A.
    expect((await b.get(`/estoque/${f.a.loteId}`)).status()).toBe(404);
    expect((await b.get(`/cadastros/produtos/${f.a.produtoId}`)).status()).toBe(404);
  } finally {
    await b.dispose();
  }

  // A pelo login de DEV: vê o próprio lote e produto; os de B não aparecem nas listas nem abrem.
  await entrarComo(page, 'Almoxarife');
  await expect(page.locator(`a[href^="/estoque/${f.a.loteId}"]`)).toBeVisible();
  let html = await page.content();
  for (const id of [f.b.loteId, f.b.produtoId])
    expect(html.includes(id), 'ID de B nas listas de A').toBe(false);
  await page.goto('/cadastros/produtos');
  await expect(page.locator(`a[href^="/cadastros/produtos/${f.a.produtoId}"]`)).toBeVisible();
  html = await page.content();
  for (const id of [f.b.loteId, f.b.produtoId])
    expect(html.includes(id), 'ID de B nas listas de A').toBe(false);
  for (const caminho of [`/estoque/${f.b.loteId}`, `/cadastros/produtos/${f.b.produtoId}`]) {
    expect((await page.goto(caminho))?.status(), caminho).toBe(404);
    await expect(page.getByRole('heading', { name: 'Página não encontrada' })).toBeVisible();
  }
});

test('HML-ISO-02: comando de A no lote de B é recusado e B não muda', async ({ page, playwright }) => {
  const f = fixture();
  await entrarComo(page, 'Almoxarife');
  const a = await clienteHttp(playwright, await sessaoDoNavegador(page));
  const b = await clienteHttp(playwright, f.b.sessao);
  try {
    const antes = await estadoNoBanco(f, f.b.loteId);
    // Pedido coerente (alvo = lote informado) com o lote de B, com o local de B e com o de A.
    for (const local of [f.b.localId, f.a.localId]) {
      const r = await enviar(a, entrada(f.b, antes.versao, local));
      expect(r.status()).toBe(422);
      expect(await r.json()).toMatchObject({ outcome: 'rejected', reasonCode: 'LOTE_NAO_ENCONTRADO' });
    }
    expect(await estadoNoBanco(f, f.b.loteId)).toEqual(antes);

    // Contracontrole: o mesmo pedido, pela sessão de B, entra; a leitura acima enxerga a mudança quando ela existe.
    const propria = await enviar(b, entrada(f.b, antes.versao));
    expect(propria.status()).toBe(200);
    expect(await propria.json()).toMatchObject({ outcome: 'confirmed' });
    const depois = await estadoNoBanco(f, f.b.loteId);
    expect(depois.versao).toBeGreaterThan(antes.versao);
    expect(depois.movimentos).toBe(antes.movimentos + 1);
  } finally {
    await a.dispose();
    await b.dispose();
  }
});

test('HML-ISO-03: API de comandos pelo HTTP recusa sem sessão (401) e o gerente (403)', async ({
  page,
  playwright,
}) => {
  const f = fixture();
  const antes = await estadoNoBanco(f, f.a.loteId);
  const anonimo = await clienteHttp(playwright);
  try {
    // Origin e JSON corretos: a recusa é pela falta de sessão.
    const r = await enviar(anonimo, entrada(f.a, antes.versao));
    expect(r.status()).toBe(401);
    expect(await r.json()).toMatchObject({ codigo: 'NAO_AUTENTICADO' });
  } finally {
    await anonimo.dispose();
  }
  await entrarComo(page, 'Gerente');
  const gerente = await clienteHttp(playwright, await sessaoDoNavegador(page));
  try {
    const r = await enviar(gerente, entrada(f.a, antes.versao));
    expect(r.status()).toBe(403);
    expect(await r.json()).toMatchObject({ codigo: 'SEM_PERMISSAO' });
  } finally {
    await gerente.dispose();
  }
  expect(await estadoNoBanco(f, f.a.loteId)).toEqual(antes);
});
