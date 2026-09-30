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
  expect((await pedidoNome).postDataJSON()).toMatchObject({
    target: { expectedVersion: 2 },
    data: { areaDeclaradaHa: '1000' },
  });
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
