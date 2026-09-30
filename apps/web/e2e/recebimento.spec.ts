import { expect, test, type Page } from '@playwright/test';

import { entrarComo, errosDoConsole, semViolacoes } from './apoio';

// Recebimento por documento (contrato CMD-15 v3.7, §6.2 e §7.1) contra o servidor real e o banco de DEV da
// demonstração, que traz Fornecedor Teste Ltda, Fungicida A (galão 5 L v1), Diesel S10 e o Almoxarifado central.
// Todo documento aqui passa pelo comando real, pela tela; nenhum é fixture. Os testes rodam em sequência.
test.describe.configure({ mode: 'serial' });

const COMANDO = '**/api/v1/comandos/estoque.receber-documento';

async function preencherOrigem(page: Page, numero: string) {
  const origem = page.getByRole('region', { name: 'Documento' });
  await origem.getByRole('textbox', { name: 'Número' }).fill(numero);
  await origem.getByRole('textbox', { name: 'Emissão' }).fill('29/09/2026');
}

async function preencherLinha(
  page: Page,
  n: number,
  l: {
    produto: string;
    lote?: string;
    validade?: string;
    unidade?: string;
    documento: string;
    apto?: string;
    bloqueado?: string;
    motivo?: string;
  },
) {
  const linha = page.getByRole('region', { name: `Linha ${String(n)}` });
  await linha.getByRole('combobox', { name: 'Produto' }).selectOption({ label: l.produto });
  if (l.lote !== undefined) await linha.getByRole('textbox', { name: 'Lote do fabricante' }).fill(l.lote);
  if (l.validade !== undefined) await linha.getByRole('textbox', { name: 'Validade' }).fill(l.validade);
  if (l.unidade !== undefined)
    await linha
      .getByRole('combobox', { name: `Unidade da linha ${String(n)}` })
      .selectOption({ label: l.unidade });
  await linha.getByRole('textbox', { name: 'No documento' }).fill(l.documento);
  if (l.apto !== undefined) await linha.getByRole('textbox', { name: 'Apto' }).fill(l.apto);
  if (l.bloqueado !== undefined) await linha.getByRole('textbox', { name: 'Bloqueado' }).fill(l.bloqueado);
  if (l.motivo !== undefined)
    await linha.getByRole('combobox', { name: 'Motivo da divergência' }).selectOption({ label: l.motivo });
  return linha;
}

test('almoxarife: R-006 §5 — recebe NF-TESTE-001 e 002, confere saldos, trilha e duplicidade', async ({
  page,
}) => {
  const erros = errosDoConsole(page);
  await entrarComo(page, 'Almoxarife', '/estoque/recebimentos');
  await expect(page.getByRole('heading', { level: 1, name: 'Recebimentos' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Recebimentos', exact: true })).toHaveAttribute(
    'aria-current',
    'page',
  );
  await expect(page.getByRole('link', { name: 'Estoque', exact: true })).not.toHaveAttribute(
    'aria-current',
    'page',
  );
  await expect(page.getByText('Nenhum documento recebido.')).toBeVisible();
  await semViolacoes(page);

  // Formulário: contexto visível (emitente, fazenda, local e hoje), validação no campo, foco no primeiro erro.
  await page.getByRole('link', { name: 'Receber documento' }).click();
  await expect(page).toHaveURL('/estoque/recebimentos/novo');
  const origem = page.getByRole('region', { name: 'Documento' });
  await expect(origem).toContainText('Fornecedor Teste Ltda');
  await expect(origem).toContainText('Fazenda Demonstração');
  await semViolacoes(page);
  await page.getByRole('button', { name: 'Confirmar recebimento' }).click();
  await expect(origem.getByText('Informe o número do documento.')).toBeVisible();
  await expect(origem.getByRole('textbox', { name: 'Número' })).toBeFocused();
  await expect(page.getByRole('region', { name: 'Linha 1' }).getByText('Escolha o produto.')).toBeVisible();

  // NF-TESTE-001: 3 galões de 5 L de Fungicida A, lote F26-02, tudo apto; confirmado pelo teclado (Enter).
  await preencherOrigem(page, 'TESTE-001');
  const l1 = await preencherLinha(page, 1, {
    produto: 'Fungicida A',
    lote: 'F26-02',
    validade: '30/06/2027',
    unidade: 'galão 5 L',
    documento: '3',
    apto: '3',
  });
  await expect(l1.getByText('Conferido 3 galão 5 L · confere')).toBeVisible();
  await expect(l1).toContainText('Almoxarifado central');
  await semViolacoes(page);
  await l1.getByRole('textbox', { name: 'Apto' }).press('Enter');
  await expect(page.getByRole('heading', { level: 1, name: 'NF TESTE-001' })).toBeVisible();
  const detalhe1 = page.url();
  await expect(page.locator('header.cabecalho').getByText('Conforme', { exact: true })).toBeVisible();
  await expect(
    page.getByRole('region', { name: 'Próximo passo' }).getByRole('link', { name: 'Receber documento' }),
  ).toBeVisible();
  const linhas1 = page.getByRole('region', { name: 'Linhas do documento' });
  await expect(linhas1.getByRole('row', { name: /Fungicida A/ })).toContainText('3 galão 5 L apto');
  await semViolacoes(page);

  // A linha abre o lote: físico 15 L, apto 15 L; o extrato leva de volta ao documento.
  await linhas1.getByRole('link', { name: '1' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Lote F26-02' })).toBeVisible();
  const saldo = page.getByRole('region', { name: 'Saldo' });
  await expect(saldo).toContainText('Utilizável15 L');
  await expect(saldo).toContainText('Físico15 L');
  const extrato = page.getByRole('region', { name: 'Movimentos do lote' });
  await expect(extrato.getByRole('row', { name: /Entrada · Liberado/ })).toContainText(
    'NF TESTE-001 · linha 1',
  );
  await semViolacoes(page);
  await page.goto(detalhe1);

  // NF-TESTE-002: 2 galões do lote F26-03, 1 apto e 1 bloqueado por avaria. Nada do documento anterior é herdado.
  await page
    .getByRole('region', { name: 'Próximo passo' })
    .getByRole('link', { name: 'Receber documento' })
    .click();
  await expect(origem.getByRole('textbox', { name: 'Número' })).toHaveValue('');
  const nova = page.getByRole('region', { name: 'Linha 1' });
  await expect(nova.getByRole('combobox', { name: 'Produto' })).toHaveValue('');
  await expect(nova.getByRole('textbox', { name: 'No documento' })).toHaveValue('');
  await preencherOrigem(page, 'TESTE-002');
  await preencherLinha(page, 1, {
    produto: 'Fungicida A',
    lote: 'F26-03',
    validade: '30/06/2027',
    unidade: 'galão 5 L',
    documento: '2',
    apto: '1',
    bloqueado: '1',
  });
  await page.getByRole('button', { name: 'Confirmar recebimento' }).click();
  await expect(nova.getByText('Escolha o motivo da divergência.')).toBeVisible();
  await nova.getByRole('combobox', { name: 'Motivo da divergência' }).selectOption({ label: 'Avaria' });
  await page.getByRole('button', { name: 'Confirmar recebimento' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'NF TESTE-002' })).toBeVisible();
  await expect(
    page.locator('header.cabecalho').getByText('Divergência aberta', { exact: true }),
  ).toBeVisible();
  const proximo = page.getByRole('region', { name: 'Próximo passo' });
  await expect(proximo.getByRole('link', { name: 'Ver divergência' })).toBeVisible();
  const pendencias = page.getByRole('region', { name: 'Pendências' });
  await expect(pendencias).toContainText('Divergência aberta · linha 1: Avaria · Fungicida A');
  await expect(pendencias).toContainText('Resolve: Almoxarife (fictício)');
  await semViolacoes(page);
  await page.getByRole('region', { name: 'Linhas do documento' }).getByRole('link', { name: '1' }).click();
  await expect(saldo).toContainText('Utilizável5 L');
  await expect(saldo).toContainText('Bloqueado5 L');
  await expect(saldo).toContainText('Físico10 L');

  // Lista: 2 documentos, a divergência como estado com palavra; filtro vai para a URL e volta com ela.
  await page.goto('/estoque/recebimentos');
  const lista = page.getByRole('region', { name: 'Documentos recebidos' });
  await expect(lista.getByText('2 de 2')).toBeVisible();
  await expect(lista.getByRole('row', { name: /NF TESTE-002/ })).toContainText('Divergência aberta');
  await expect(lista.getByRole('row', { name: /NF TESTE-001/ })).toContainText('Conforme');
  await lista.getByRole('button', { name: /^Documento/ }).click();
  await expect(page).toHaveURL('/estoque/recebimentos?ordem=documento');
  await lista.getByRole('link', { name: 'NF TESTE-002' }).click();
  await page.getByRole('link', { name: 'Voltar para Recebimentos' }).click();
  await expect(page).toHaveURL('/estoque/recebimentos?ordem=documento');

  // Duplicidade: NF-TESTE-001 de novo mostra que já foi recebida, mantém o rascunho e não soma.
  await page.getByRole('link', { name: 'Receber documento' }).click();
  await preencherOrigem(page, 'TESTE-001');
  await preencherLinha(page, 1, {
    produto: 'Fungicida A',
    lote: 'F26-02',
    unidade: 'galão 5 L',
    documento: '3',
    apto: '3',
  });
  await expect(page.getByRole('region', { name: 'Linha 1' })).toContainText(
    '30/06/2027 · do lote já recebido',
  );
  await page.getByRole('button', { name: 'Confirmar recebimento' }).click();
  await expect(
    origem.getByText('Este documento do emitente já foi recebido. Confira em Recebimentos.'),
  ).toBeVisible();
  await expect(origem.getByRole('textbox', { name: 'Número' })).toHaveValue('TESTE-001');
  await page.goto('/estoque/recebimentos');
  await expect(lista.getByText('2 de 2')).toBeVisible();
  // O navegador registra a resposta 422 da duplicidade, que é o resultado esperado; nenhum outro erro.
  expect(erros.filter((e) => !e.includes('status of 422'))).toEqual([]);
});

test('granel: diesel sem validade vira lote legível, nunca DOC:<uuid>', async ({ page }) => {
  await entrarComo(page, 'Almoxarife', '/estoque/recebimentos/novo');
  await preencherOrigem(page, 'TESTE-003');
  const linha = await preencherLinha(page, 1, { produto: 'Diesel S10', documento: '500', apto: '500' });
  await expect(linha).toContainText('Granel · lote do documento');
  await expect(linha).toContainText('Não se aplica');
  await page.getByRole('button', { name: 'Confirmar recebimento' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'NF TESTE-003' })).toBeVisible();
  const nome = 'Granel · NF TESTE-003 · Fornecedor Teste Ltda';
  await expect(page.getByRole('region', { name: 'Linhas do documento' })).toContainText(nome);
  await page.goto('/estoque');
  const lotes = page.getByRole('region', { name: 'Lotes' });
  await expect(lotes.getByRole('row', { name: new RegExp(nome) })).toContainText('Não se aplica');
  await expect(lotes).not.toContainText('DOC:');
  await lotes.getByRole('link', { name: nome }).click();
  await expect(page.getByRole('heading', { level: 1, name: nome })).toBeVisible();
  await expect(page.locator('main')).not.toContainText('DOC:');
  await semViolacoes(page);
});

test('resposta perdida depois de gravar: a consulta recupera o recibo, sem reenviar', async ({ page }) => {
  await entrarComo(page, 'Almoxarife', '/estoque/recebimentos/novo');
  let posts = 0;
  // O pedido chega ao servidor e grava; a resposta é que se perde.
  await page.route(COMANDO, async (route) => {
    posts += 1;
    await route.fetch();
    await route.abort('connectionreset');
  });
  await preencherOrigem(page, 'TESTE-004');
  await preencherLinha(page, 1, { produto: 'Diesel S10', documento: '100', apto: '100' });
  await page.getByRole('button', { name: 'Confirmar recebimento' }).click();
  await expect(page.getByText(/O envio pode ter chegado ao servidor/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Confirmar recebimento' })).toHaveCount(0);
  await expect(
    page.getByRole('region', { name: 'Linha 1' }).getByRole('textbox', { name: 'No documento' }),
  ).toHaveAttribute('readonly', '');
  // Recarregar mantém a intenção travada; a consulta é gesto explícito e não reenvia.
  await page.reload();
  await expect(page.getByText(/O envio pode ter chegado ao servidor/)).toBeVisible();
  await expect(
    page.getByRole('region', { name: 'Documento' }).getByRole('textbox', { name: 'Número' }),
  ).toHaveValue('TESTE-004');
  await semViolacoes(page);
  await page.getByRole('button', { name: 'Consultar recibo' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'NF TESTE-004' })).toBeVisible();
  expect(posts).toBe(1);
});

test('nada gravado: "ainda não localizado" libera reenviar o mesmo; sessão expirada não apaga a intenção', async ({
  page,
  context,
}) => {
  await entrarComo(page, 'Almoxarife', '/estoque/recebimentos/novo');
  // A rede cai antes de chegar: nada é gravado.
  await page.route(COMANDO, (route) => route.abort('internetdisconnected'));
  await preencherOrigem(page, 'TESTE-005');
  await preencherLinha(page, 1, { produto: 'Diesel S10', documento: '50', apto: '50' });
  await page.getByRole('button', { name: 'Confirmar recebimento' }).click();
  await expect(page.getByText(/O envio pode ter chegado ao servidor/)).toBeVisible();
  await page.unroute(COMANDO);

  // Sessão expirada: a consulta pede para entrar de novo e a intenção continua guardada para a mesma pessoa.
  await context.clearCookies();
  await page.getByRole('button', { name: 'Consultar recibo' }).click();
  await expect(
    page.getByText(/Sua sessão terminou. Entre de novo para conferir o envio pendente/),
  ).toBeVisible();
  await expect(page.getByRole('button', { name: 'Consultar recibo' })).toBeVisible();
  await entrarComo(page, 'Almoxarife', '/estoque/recebimentos/novo');
  await expect(page.getByText(/O envio pode ter chegado ao servidor/)).toBeVisible();

  await page.getByRole('button', { name: 'Consultar recibo' }).click();
  await expect(page.getByText(/Recibo ainda não localizado/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'Confirmar recebimento' })).toHaveCount(0);
  await page.getByRole('button', { name: 'Reenviar o mesmo' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'NF TESTE-005' })).toBeVisible();

  // Sair apaga o rascunho: quem entrar depois no mesmo navegador começa do zero.
  await page.goto('/estoque/recebimentos/novo');
  await preencherOrigem(page, 'TESTE-RASCUNHO');
  await page.getByRole('button', { name: 'Sair' }).click();
  await entrarComo(page, 'Almoxarife', '/estoque/recebimentos/novo');
  await expect(
    page.getByRole('region', { name: 'Documento' }).getByRole('textbox', { name: 'Número' }),
  ).toHaveValue('');
});

test('sem armazenamento no navegador, nada é enviado', async ({ page }) => {
  await entrarComo(page, 'Almoxarife', '/estoque/recebimentos');
  await page.addInitScript(() => {
    Storage.prototype.setItem = () => {
      throw new DOMException('cheio', 'QuotaExceededError');
    };
  });
  let posts = 0;
  page.on('request', (r) => {
    if (r.method() === 'POST' && r.url().includes('/api/v1/comandos/')) posts += 1;
  });
  await page.goto('/estoque/recebimentos/novo');
  await preencherOrigem(page, 'TESTE-006');
  await preencherLinha(page, 1, { produto: 'Diesel S10', documento: '10', apto: '10' });
  await page.getByRole('button', { name: 'Confirmar recebimento' }).click();
  await expect(page.getByText(/o navegador precisa guardar o envio antes de mandá-lo/)).toBeVisible();
  expect(posts).toBe(0);
});

test('gerente: consulta recebimentos e detalhe sem ação de receber; o formulário não existe para ele', async ({
  page,
}) => {
  await entrarComo(page, 'Gerente', '/estoque/recebimentos');
  const lista = page.getByRole('region', { name: 'Documentos recebidos' });
  await expect(lista.getByRole('row', { name: /NF TESTE-002/ })).toContainText('Divergência aberta');
  await expect(page.getByRole('link', { name: 'Receber documento' })).toHaveCount(0);
  await lista.getByRole('link', { name: 'NF TESTE-001' }).click();
  await expect(page.getByRole('region', { name: 'Próximo passo' })).toContainText(
    'Somente consulta. Quem recebe documento é o almoxarife.',
  );
  await semViolacoes(page);
  const r = await page.goto('/estoque/recebimentos/novo');
  expect(r?.status()).toBe(404);
});
