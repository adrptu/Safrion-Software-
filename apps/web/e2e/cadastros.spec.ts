import { randomUUID } from 'node:crypto';
import { expect, test } from '@playwright/test';

import { entrarComo, errosDoConsole, semViolacoes } from './apoio';
import {
  capturarCadastro,
  criarTalhao,
  LISTA_CADASTROS,
  prepararTalhao,
  primariaAoAlcance,
} from './jornada-cadastros';

const CRIAR = '**/api/v1/comandos/cadastros.criar-talhao';
const EDITAR = '**/api/v1/comandos/cadastros.editar-talhao';

// Dados fictícios e comandos reais; cada jornada cria a própria fazenda e não depende de ordem entre os testes.
test('CAD01: gerente cria fazenda e talhão pelo teclado e volta aos filtros sem reabrir o painel', async ({
  page,
}, testInfo) => {
  const erros = errosDoConsole(page);
  await entrarComo(page, 'Gerente', LISTA_CADASTROS);
  await expect(page.getByRole('heading', { level: 1, name: 'Fazendas e talhões' })).toBeVisible();
  await semViolacoes(page);
  await prepararTalhao(page, 'CAD E2E Principal', 'T1 Principal');
  await semViolacoes(page);
  await capturarCadastro(page, testInfo, 'cad01-desktop-painel');
  const primaria = await primariaAoAlcance(page);
  await primaria.press('Enter');
  await expect(page.getByRole('heading', { level: 1, name: 'T1 Principal', exact: true })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Identificação' })).toContainText('204,00 ha (declarada)');
  await expect(page.getByRole('region', { name: 'Limite', exact: true })).toContainText('Sem limite no mapa');
  await capturarCadastro(page, testInfo, 'cad01-desktop-detalhe');
  await semViolacoes(page);
  await page.getByRole('link', { name: 'Voltar para Fazendas e talhões', exact: true }).click();
  await expect(page).toHaveURL(LISTA_CADASTROS);
  await expect(page.getByRole('dialog')).toBeHidden();
  const grupo = page.getByRole('region', { name: 'CAD E2E Principal', exact: true });
  await expect(grupo).toContainText('1 talhão ativo');
  await expect(grupo.getByRole('link', { name: 'T1 Principal', exact: true })).toHaveCount(1);
  // Voltar no histórico após detalhe também não pode ressuscitar o painel de criação.
  await page.goBack();
  await expect(page.getByRole('heading', { level: 1, name: 'T1 Principal', exact: true })).toBeVisible();
  await page.goBack();
  await expect(page).toHaveURL(LISTA_CADASTROS);
  await expect(page.getByRole('dialog')).toBeHidden();
  expect(erros).toEqual([]);
});

test('CAD01: cancelar o talhão preserva a fazenda criada e o almoxarife só consulta', async ({
  page,
  browser,
}) => {
  await entrarComo(page, 'Gerente', LISTA_CADASTROS);
  const painel = await prepararTalhao(page, 'CAD E2E Sem talhão', 'Não confirmado');
  await painel.getByRole('button', { name: 'Voltar', exact: true }).click();
  await expect(painel).toBeHidden();
  const grupo = page.getByRole('region', { name: 'CAD E2E Sem talhão', exact: true });
  await expect(grupo).toContainText('0 talhões ativos');
  await expect(grupo).toContainText('Nenhum talhão ativo.');
  await grupo.getByRole('link', { name: 'CAD E2E Sem talhão', exact: true }).click();
  await expect(
    page.getByRole('heading', { level: 1, name: 'CAD E2E Sem talhão', exact: true }),
  ).toBeVisible();
  const caminhoFazenda = new URL(page.url()).pathname;
  await expect(page.getByRole('region', { name: 'Talhões da fazenda' })).toContainText(
    'Nenhum talhão nesta fazenda.',
  );

  const consulta = await browser.newContext({ baseURL: new URL(page.url()).origin, locale: 'pt-BR' });
  try {
    const almoxarife = await consulta.newPage();
    await entrarComo(almoxarife, 'Almoxarife', caminhoFazenda);
    await expect(
      almoxarife.getByText('Somente consulta · quem cadastra: Gerente', { exact: true }),
    ).toBeVisible();
    await expect(almoxarife.getByRole('button', { name: 'Editar nome e fuso' })).toHaveCount(0);
    await expect(almoxarife.getByRole('button', { name: /Novo talhão/ })).toHaveCount(0);
    await almoxarife.goto(LISTA_CADASTROS);
    await expect(almoxarife.getByRole('region', { name: 'CAD E2E Sem talhão', exact: true })).toBeVisible();
    await expect(
      almoxarife.getByRole('button', { name: /Novo talhão|Criar fazenda|Criar talhão/ }),
    ).toHaveCount(0);
    await semViolacoes(almoxarife);
  } finally {
    await consulta.close();
  }
});

test('CAD01: conflito real de edição preserva campos e só reaplica com gesto e chave novos', async ({
  page,
}) => {
  await entrarComo(page, 'Gerente', LISTA_CADASTROS);
  const id = await criarTalhao(page, 'CAD E2E Conflito', 'T1 Conflito');
  await page.getByRole('button', { name: 'Editar talhão', exact: true }).click();
  const painel = page.getByRole('dialog', { name: 'Talhão', exact: true });
  await painel.getByRole('textbox', { name: 'Nome', exact: true }).fill('T1 Minha edição');
  const areaAntesDoConflito = await painel
    .getByRole('textbox', { name: 'Área declarada (ha)', exact: true })
    .inputValue();

  // Outra edição usa a mesma sessão/autorização e o endpoint real, enquanto o formulário mantém a versão 1.
  const concorrente = await page.request.post('/api/v1/comandos/cadastros.editar-talhao', {
    headers: { Origin: new URL(page.url()).origin },
    data: {
      idempotencyKey: randomUUID(),
      target: { type: 'field', id, expectedVersion: 1 },
      data: { nome: 'T1 Outra edição' },
    },
  });
  expect(concorrente.status()).toBe(200);
  expect(await concorrente.json()).toMatchObject({ outcome: 'confirmed', resultingVersion: 2 });
  const pedidos: { idempotencyKey: string; target: { expectedVersion: number }; data: unknown }[] = [];
  await page.route(EDITAR, async (route) => {
    pedidos.push(route.request().postDataJSON() as (typeof pedidos)[number]);
    await route.continue();
  });
  const conflito = page.waitForResponse((r) => r.url().endsWith('/comandos/cadastros.editar-talhao'));
  await painel.getByRole('button', { name: 'Salvar talhão', exact: true }).click();
  expect((await conflito).status()).toBe(409);
  await expect(painel.getByRole('status')).toContainText('Versão atual: 2. Seus campos foram preservados.');
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toHaveValue('T1 Minha edição');
  await expect(painel.getByRole('textbox', { name: 'Área declarada (ha)', exact: true })).toHaveValue(
    areaAntesDoConflito,
  );
  await expect(
    painel.getByRole('button', { name: 'Reaplicar minhas alterações', exact: true }),
  ).toBeEnabled();
  expect(pedidos).toHaveLength(1);
  await painel.getByRole('button', { name: 'Reaplicar minhas alterações', exact: true }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'T1 Minha edição', exact: true })).toBeVisible();
  expect(pedidos).toHaveLength(2);
  expect(pedidos.map((p) => p.target.expectedVersion)).toEqual([1, 2]);
  expect(pedidos[0]?.idempotencyKey).not.toBe(pedidos[1]?.idempotencyKey);
  expect(pedidos[1]?.data).toEqual(pedidos[0]?.data);
  await expect(
    page
      .getByRole('region', { name: 'Identificação' })
      .locator('dl > div')
      .filter({ has: page.locator('dt').filter({ hasText: /^Versão$/ }) })
      .locator('dd'),
  ).toHaveText('3');
});

test('CAD01: resposta perdida após gravar recupera recibo ao reabrir, sem criar outro talhão', async ({
  page,
}) => {
  await entrarComo(page, 'Gerente', LISTA_CADASTROS);
  const painel = await prepararTalhao(page, 'CAD E2E Recibo', 'T1 Recibo');
  let envios = 0;
  let consultas = 0;
  page.on('request', (r) => {
    if (r.method() === 'POST' && r.url().endsWith('/comandos/cadastros.criar-talhao')) envios += 1;
    if (r.method() === 'GET' && r.url().includes('/intencoes/cadastros.criar-talhao/')) consultas += 1;
  });
  await page.route(
    CRIAR,
    async (route) => {
      const recebido = await route.fetch();
      expect(recebido.status()).toBe(200);
      expect(await recebido.json()).toMatchObject({ outcome: 'confirmed', resultingVersion: 1 });
      // O efeito foi confirmado no servidor; somente a resposta ao navegador é perdida.
      await route.abort('failed');
    },
    { times: 1 },
  );
  await painel.getByRole('button', { name: 'Criar talhão', exact: true }).click();
  await expect(painel.getByRole('button', { name: 'Consultar recibo', exact: true })).toBeEnabled();
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toBeDisabled();
  await page.reload();
  const enviosPendentes = page.getByRole('region', { name: 'Envios sem confirmação' });
  await enviosPendentes.getByRole('button', { name: 'Criar talhão · T1 Recibo', exact: true }).click();
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toHaveValue('T1 Recibo');
  expect(consultas).toBe(0);
  expect(envios).toBe(1);
  await painel.getByRole('button', { name: 'Consultar recibo', exact: true }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'T1 Recibo', exact: true })).toBeVisible();
  expect(consultas).toBe(1);
  expect(envios).toBe(1);
  await page.getByRole('link', { name: 'Voltar para Fazendas e talhões', exact: true }).click();
  await expect(page.getByRole('region', { name: 'Envios sem confirmação' })).toHaveCount(0);
  const grupo = page.getByRole('region', { name: 'CAD E2E Recibo', exact: true });
  await expect(grupo).toContainText('1 talhão ativo');
  await expect(grupo.getByRole('link', { name: 'T1 Recibo', exact: true })).toHaveCount(1);
});

test('CAD01: editar apenas o nome preserva a área de mil hectares após reabrir', async ({ page }) => {
  await entrarComo(page, 'Gerente', LISTA_CADASTROS);
  await criarTalhao(page, 'CAD E2E Área mil', 'T1 Área mil');
  await page.getByRole('button', { name: 'Editar talhão', exact: true }).click();
  const painel = page.getByRole('dialog', { name: 'Talhão', exact: true });
  await painel.getByRole('textbox', { name: 'Área declarada (ha)', exact: true }).fill('1000');
  const gravouArea = page.waitForResponse((r) => r.url().endsWith('/comandos/cadastros.editar-talhao'));
  await painel.getByRole('button', { name: 'Salvar talhão', exact: true }).click();
  expect((await gravouArea).status()).toBe(200);
  await expect(painel).toBeHidden();
  await expect(page.getByRole('region', { name: 'Identificação' })).toContainText('1.000,00 ha (declarada)');
  await page.getByRole('button', { name: 'Editar talhão', exact: true }).click();
  // Um preload "1.000" seria ambíguo e impediria salvar até quem alterou somente o nome.
  await expect(painel.getByRole('textbox', { name: 'Área declarada (ha)', exact: true })).toHaveValue(
    /^1000(?:,0{1,6})?$/,
  );
  await painel.getByRole('textbox', { name: 'Nome', exact: true }).fill('T1 Mil hectares preservados');
  const pedidoNome = page.waitForRequest(
    (r) => r.method() === 'POST' && r.url().endsWith('/comandos/cadastros.editar-talhao'),
  );
  const gravouNome = page.waitForResponse((r) => r.url().endsWith('/comandos/cadastros.editar-talhao'));
  await painel.getByRole('button', { name: 'Salvar talhão', exact: true }).click();
  const corpoNome = (await pedidoNome).postDataJSON() as EdicaoObservada;
  expect(corpoNome.target.expectedVersion).toBe(2);
  expect(corpoNome.data).toEqual({ nome: 'T1 Mil hectares preservados' });
  expect((await gravouNome).status()).toBe(200);
  await expect(
    page.getByRole('heading', { level: 1, name: 'T1 Mil hectares preservados', exact: true }),
  ).toBeVisible();
  await expect(page.getByRole('region', { name: 'Identificação' })).toContainText('1.000,00 ha (declarada)');
});

test('CAD01: primeiro envio sem sessão conserva dados e retoma após login com o mesmo corpo e chave', async ({
  page,
}) => {
  await entrarComo(page, 'Gerente', LISTA_CADASTROS);
  const painel = await prepararTalhao(page, 'CAD E2E Sessão', 'T1 Sessão');
  const fazendaEscolhida = await painel.getByRole('combobox', { name: 'Fazenda', exact: true }).inputValue();
  const envios: string[] = [];
  let consultas = 0;
  page.on('request', (r) => {
    if (r.method() === 'POST' && r.url().endsWith('/comandos/cadastros.criar-talhao'))
      envios.push(r.postData() ?? '');
    if (r.method() === 'GET' && r.url().includes('/intencoes/cadastros.criar-talhao/')) consultas += 1;
  });
  // Sessão ausente no servidor, mantendo apenas o formulário e o armazenamento locais do navegador.
  await page.context().clearCookies();
  const recusado = page.waitForResponse((r) => r.url().endsWith('/comandos/cadastros.criar-talhao'));
  await painel.getByRole('button', { name: 'Criar talhão', exact: true }).click();
  const resposta401 = await recusado;
  expect(resposta401.status()).toBe(401);
  expect(await resposta401.json()).toMatchObject({ codigo: 'NAO_AUTENTICADO' });
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toHaveValue('T1 Sessão');
  await painel.getByRole('link', { name: 'Entrar novamente', exact: true }).click();
  await expect(page).toHaveURL(/\/entrar\?destino=/);
  await page.getByRole('link', { name: 'Entrar', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Usuário fictício' })).toBeVisible();
  await page.getByRole('button', { name: 'Gerente (fictício)', exact: true }).click();
  await expect(page).toHaveURL(LISTA_CADASTROS);
  await page.reload();
  await page
    .getByRole('region', { name: 'Envios sem confirmação' })
    .getByRole('button', { name: 'Criar talhão · T1 Sessão', exact: true })
    .click();
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toHaveValue('T1 Sessão');
  await expect(painel.getByRole('textbox', { name: 'Área declarada (ha)', exact: true })).toHaveValue('204');
  await expect(painel.getByRole('combobox', { name: 'Fazenda', exact: true })).toHaveValue(fazendaEscolhida);
  expect(envios).toHaveLength(1);
  expect(consultas).toBe(0);
  const consulta = page.waitForResponse((r) => r.url().includes('/intencoes/cadastros.criar-talhao/'));
  await painel.getByRole('button', { name: 'Consultar recibo', exact: true }).click();
  const resposta404 = await consulta;
  expect(resposta404.status()).toBe(404);
  expect(await resposta404.json()).toMatchObject({ codigo: 'RECIBO_NAO_LOCALIZADO' });
  await expect(painel.getByRole('button', { name: 'Reenviar mesmo cadastro', exact: true })).toBeEnabled();
  expect(envios).toHaveLength(1);
  await painel.getByRole('button', { name: 'Reenviar mesmo cadastro', exact: true }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'T1 Sessão', exact: true })).toBeVisible();
  expect(envios).toHaveLength(2);
  expect(envios[0]).not.toBe('');
  expect(envios[1]).toBe(envios[0]);
  expect(consultas).toBe(1);
  await page.getByRole('link', { name: 'Voltar para Fazendas e talhões', exact: true }).click();
  await expect(page.getByRole('region', { name: 'CAD E2E Sessão', exact: true })).toContainText(
    '1 talhão ativo',
  );
  await expect(page.getByRole('region', { name: 'Envios sem confirmação' })).toHaveCount(0);
});

test('CAD01: recuperar edição do talhão A no detalhe B navega ao alvo A e preserva B', async ({ page }) => {
  await entrarComo(page, 'Gerente', LISTA_CADASTROS);
  const idA = await criarTalhao(page, 'CAD E2E Alvo A', 'Talhão A original');
  const caminhoA = new URL(page.url()).pathname;
  await page.goto(LISTA_CADASTROS);
  await criarTalhao(page, 'CAD E2E Alvo B', 'Talhão B preservado');
  const caminhoB = new URL(page.url()).pathname;
  await page.goto(caminhoA);
  await page.getByRole('button', { name: 'Editar talhão', exact: true }).click();
  const painel = page.getByRole('dialog', { name: 'Talhão', exact: true });
  await painel.getByRole('textbox', { name: 'Nome', exact: true }).fill('Talhão A recuperado');
  let edicoes = 0;
  page.on('request', (r) => {
    if (r.method() === 'POST' && r.url().endsWith('/comandos/cadastros.editar-talhao')) edicoes += 1;
  });
  await page.route(
    EDITAR,
    async (route) => {
      const resposta = await route.fetch();
      expect(resposta.status()).toBe(200);
      expect(await resposta.json()).toMatchObject({
        outcome: 'confirmed',
        targetId: idA,
        resultingVersion: 2,
      });
      await route.abort('failed');
    },
    { times: 1 },
  );
  await painel.getByRole('button', { name: 'Salvar talhão', exact: true }).click();
  await expect(painel.getByRole('button', { name: 'Consultar recibo', exact: true })).toBeEnabled();
  await page.goto(caminhoB);
  await expect(
    page.getByRole('heading', { level: 1, name: 'Talhão B preservado', exact: true }),
  ).toBeVisible();
  await page
    .getByRole('region', { name: 'Envios sem confirmação' })
    .getByRole('button', { name: 'Salvar talhão · Talhão A recuperado', exact: true })
    .click();
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toHaveValue('Talhão A recuperado');
  await painel.getByRole('button', { name: 'Consultar recibo', exact: true }).click();
  await expect(page).toHaveURL((url) => url.pathname === caminhoA);
  await expect(
    page.getByRole('heading', { level: 1, name: 'Talhão A recuperado', exact: true }),
  ).toBeVisible();
  expect(edicoes).toBe(1);
  await page.goto(caminhoB);
  await expect(
    page.getByRole('heading', { level: 1, name: 'Talhão B preservado', exact: true }),
  ).toBeVisible();
  await expect(
    page
      .getByRole('region', { name: 'Identificação' })
      .locator('dl > div')
      .filter({ has: page.locator('dt').filter({ hasText: /^Versão$/ }) })
      .locator('dd'),
  ).toHaveText('1');
  await expect(page.getByRole('region', { name: 'Envios sem confirmação' })).toHaveCount(0);
});

interface EdicaoObservada {
  idempotencyKey: string;
  target: { expectedVersion: number };
  data: Record<string, string>;
}

async function alterarAreaConcorrente(page: import('@playwright/test').Page, id: string) {
  const resposta = await page.request.post('/api/v1/comandos/cadastros.editar-talhao', {
    headers: { Origin: new URL(page.url()).origin },
    data: {
      idempotencyKey: randomUUID(),
      target: { type: 'field', id, expectedVersion: 1 },
      data: { areaDeclaradaHa: '210' },
    },
  });
  expect(resposta.status()).toBe(200);
  expect(await resposta.json()).toMatchObject({ outcome: 'confirmed', resultingVersion: 2 });
}

// Origem: P1 Claude, revisão de 30/09/2026 20:58 UTC. Executor: Codex/Playwright + API e banco reais.
test('CAD01 P1 Claude: reaplicar somente o nome preserva a área concorrente de 210 ha', async ({ page }) => {
  await entrarComo(page, 'Gerente', LISTA_CADASTROS);
  const id = await criarTalhao(page, 'CAD P1 Campos distintos', 'T1 Inicial C1');
  await page.getByRole('button', { name: 'Editar talhão', exact: true }).click();
  const painel = page.getByRole('dialog', { name: 'Talhão', exact: true });
  await painel.getByRole('textbox', { name: 'Nome', exact: true }).fill('T1 Nome C1');
  const areaInicial = await painel
    .getByRole('textbox', { name: 'Área declarada (ha)', exact: true })
    .inputValue();
  await alterarAreaConcorrente(page, id);
  const pedidos: EdicaoObservada[] = [];
  page.on('request', (r) => {
    if (r.method() === 'POST' && r.url().endsWith('/comandos/cadastros.editar-talhao'))
      pedidos.push(r.postDataJSON() as EdicaoObservada);
  });
  const conflito = page.waitForResponse((r) => r.url().endsWith('/comandos/cadastros.editar-talhao'));
  await painel.getByRole('button', { name: 'Salvar talhão', exact: true }).click();
  expect((await conflito).status()).toBe(409);
  await expect(painel.getByText(/Versão atual: 2\. Seus campos foram preservados\./)).toBeVisible();
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toHaveValue('T1 Nome C1');
  await expect(painel.getByRole('textbox', { name: 'Área declarada (ha)', exact: true })).toHaveValue(
    areaInicial,
  );
  expect(pedidos).toHaveLength(1);
  expect(pedidos[0]?.data).toEqual({ nome: 'T1 Nome C1' });
  await painel.getByRole('button', { name: 'Reaplicar minhas alterações', exact: true }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'T1 Nome C1', exact: true })).toBeVisible();
  expect(pedidos).toHaveLength(2);
  expect(pedidos.map((p) => p.target.expectedVersion)).toEqual([1, 2]);
  expect(pedidos[1]?.idempotencyKey).not.toBe(pedidos[0]?.idempotencyKey);
  expect(pedidos[1]?.data).toEqual({ nome: 'T1 Nome C1' });
  await page.reload();
  await expect(page.getByRole('heading', { level: 1, name: 'T1 Nome C1', exact: true })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Identificação' })).toContainText('210,00 ha (declarada)');
  await expect(
    page
      .getByRole('region', { name: 'Identificação' })
      .locator('dl > div')
      .filter({ has: page.locator('dt').filter({ hasText: /^Versão$/ }) })
      .locator('dd'),
  ).toHaveText('3');
});

test('CAD01 P1 Claude: salvar sem alterações informa o estado e não envia comando', async ({ page }) => {
  await entrarComo(page, 'Gerente', LISTA_CADASTROS);
  await criarTalhao(page, 'CAD P1 Sem alteração', 'T1 Sem alteração');
  await page.getByRole('button', { name: 'Editar talhão', exact: true }).click();
  const painel = page.getByRole('dialog', { name: 'Talhão', exact: true });
  let postagens = 0;
  page.on('request', (r) => {
    if (r.method() === 'POST' && r.url().endsWith('/comandos/cadastros.editar-talhao')) postagens += 1;
  });
  await painel.getByRole('button', { name: 'Salvar talhão', exact: true }).click();
  await expect(painel.getByText('Nada a alterar.', { exact: true })).toBeVisible();
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toHaveValue('T1 Sem alteração');
  await painel.getByRole('button', { name: 'Voltar', exact: true }).click();
  await page.reload();
  await expect(
    page
      .getByRole('region', { name: 'Identificação' })
      .locator('dl > div')
      .filter({ has: page.locator('dt').filter({ hasText: /^Versão$/ }) })
      .locator('dd'),
  ).toHaveText('1');
  expect(postagens).toBe(0);
  await expect(page.getByRole('region', { name: 'Envios sem confirmação' })).toHaveCount(0);
});

/** Perde só a resposta de um conflito real; o recibo e o cadastro concorrente permanecem no servidor. */
async function prepararPendenciaDeConflito(page: import('@playwright/test').Page, sufixo: string) {
  await entrarComo(page, 'Gerente', LISTA_CADASTROS);
  const id = await criarTalhao(page, `CAD P1 ${sufixo}`, `T1 Inicial ${sufixo}`);
  await page.getByRole('button', { name: 'Editar talhão', exact: true }).click();
  const painel = page.getByRole('dialog', { name: 'Talhão', exact: true });
  const areaInicial = await painel
    .getByRole('textbox', { name: 'Área declarada (ha)', exact: true })
    .inputValue();
  const nome = `T1 Nome ${sufixo}`;
  await painel.getByRole('textbox', { name: 'Nome', exact: true }).fill(nome);
  await alterarAreaConcorrente(page, id);
  const pedidos: EdicaoObservada[] = [];
  page.on('request', (r) => {
    if (r.method() === 'POST' && r.url().endsWith('/comandos/cadastros.editar-talhao'))
      pedidos.push(r.postDataJSON() as EdicaoObservada);
  });
  await page.route(
    EDITAR,
    async (route) => {
      const resposta = await route.fetch();
      expect(resposta.status()).toBe(409);
      expect(await resposta.json()).toMatchObject({ outcome: 'version_conflict', resultingVersion: 2 });
      await route.abort('failed');
    },
    { times: 1 },
  );
  await painel.getByRole('button', { name: 'Salvar talhão', exact: true }).click();
  await expect(painel.getByRole('button', { name: 'Consultar recibo', exact: true })).toBeEnabled();
  expect(pedidos).toHaveLength(1);
  return { painel, nome, areaInicial, pedidos, chave: pedidos[0]?.idempotencyKey ?? '' };
}

test('CAD01 P1 Claude: recuperar pendência com valores iniciais reaplica só o nome após consultar 409', async ({
  page,
}) => {
  const { painel, nome, areaInicial, pedidos } = await prepararPendenciaDeConflito(page, 'Recuperação');
  await page.reload();
  await page
    .getByRole('region', { name: 'Envios sem confirmação' })
    .getByRole('button', { name: `Salvar talhão · ${nome}`, exact: true })
    .click();
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toHaveValue(nome);
  await expect(painel.getByRole('textbox', { name: 'Área declarada (ha)', exact: true })).toHaveValue(
    areaInicial,
  );
  const consulta = page.waitForResponse((r) => r.url().includes('/intencoes/cadastros.editar-talhao/'));
  await painel.getByRole('button', { name: 'Consultar recibo', exact: true }).click();
  expect((await consulta).status()).toBe(409);
  await expect(
    painel.getByRole('button', { name: 'Reaplicar minhas alterações', exact: true }),
  ).toBeEnabled();
  expect(pedidos).toHaveLength(1);
  await painel.getByRole('button', { name: 'Reaplicar minhas alterações', exact: true }).click();
  await expect(page.getByRole('heading', { level: 1, name: nome, exact: true })).toBeVisible();
  expect(pedidos).toHaveLength(2);
  expect(pedidos.map((p) => p.data)).toEqual([{ nome }, { nome }]);
  expect(pedidos.map((p) => p.target.expectedVersion)).toEqual([1, 2]);
  expect(pedidos[1]?.idempotencyKey).not.toBe(pedidos[0]?.idempotencyKey);
  await page.reload();
  await expect(page.getByRole('region', { name: 'Identificação' })).toContainText('210,00 ha (declarada)');
  await expect(
    page
      .getByRole('region', { name: 'Identificação' })
      .locator('dl > div')
      .filter({ has: page.locator('dt').filter({ hasText: /^Versão$/ }) })
      .locator('dd'),
  ).toHaveText('3');
  await expect(page.getByRole('region', { name: 'Envios sem confirmação' })).toHaveCount(0);
});

test('CAD01 P1 Claude: pendência legada consulta 409 e preserva campos sem permitir reaplicação sem base', async ({
  page,
}) => {
  const { painel, nome, areaInicial, pedidos, chave } = await prepararPendenciaDeConflito(page, 'Legado');
  // Fixture de migração: somente a fotografia inicial é retirada deste envio sintético identificado por chave.
  // Corpo, alvo e chave continuam sendo os que o navegador enviou ao servidor real.
  await page.evaluate((chaveDaIntencao) => {
    const chaves = Object.keys(localStorage).filter(
      (k) => k.startsWith('safrion:cadastro-intencao:') && k.endsWith(`:${chaveDaIntencao}`),
    );
    if (chaves.length !== 1 || !chaves[0]) throw new Error('Esperada uma única intenção sintética guardada');
    const k = chaves[0];
    const guardada = JSON.parse(localStorage.getItem(k) ?? '{}') as Record<string, unknown>;
    if (!guardada['iniciais']) throw new Error('A intenção nova deveria ter valores iniciais');
    delete guardada['iniciais'];
    localStorage.setItem(k, JSON.stringify(guardada));
  }, chave);
  await page.reload();
  await page
    .getByRole('region', { name: 'Envios sem confirmação' })
    .getByRole('button', { name: `Salvar talhão · ${nome}`, exact: true })
    .click();
  const consulta = page.waitForResponse((r) => r.url().includes('/intencoes/cadastros.editar-talhao/'));
  await painel.getByRole('button', { name: 'Consultar recibo', exact: true }).click();
  expect((await consulta).status()).toBe(409);
  await expect(painel.getByText(/Este envio antigo não guardou os valores iniciais\./)).toBeVisible();
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toHaveValue(nome);
  await expect(painel.getByRole('textbox', { name: 'Área declarada (ha)', exact: true })).toHaveValue(
    areaInicial,
  );
  await expect(
    painel.getByRole('button', { name: 'Reaplicar minhas alterações', exact: true }),
  ).toBeDisabled();
  await painel.getByRole('textbox', { name: 'Nome', exact: true }).press('Enter');
  await expect(painel.getByText(/Este envio antigo não guardou os valores iniciais\./)).toBeVisible();
  expect(pedidos).toHaveLength(1);
  await painel.getByRole('button', { name: 'Voltar', exact: true }).click();
  await page.reload();
  await expect(page.getByRole('heading', { level: 1, name: 'T1 Inicial Legado', exact: true })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Identificação' })).toContainText('210,00 ha (declarada)');
  await expect(
    page
      .getByRole('region', { name: 'Identificação' })
      .locator('dl > div')
      .filter({ has: page.locator('dt').filter({ hasText: /^Versão$/ }) })
      .locator('dd'),
  ).toHaveText('2');
  expect(pedidos).toHaveLength(1);
});
