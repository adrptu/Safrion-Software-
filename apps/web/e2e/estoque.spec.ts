import { randomUUID } from 'node:crypto';

import { expect, test } from '@playwright/test';

import { entrarComo, errosDoConsole, semViolacoes } from './apoio';

// Jornadas da F0-c (B2) contra o servidor real e o banco de DEV da demonstração: um lote DEMO-001 sem entrada, de
// "Herbicida fictício" em litros. Os testes rodam em sequência sobre o mesmo banco.

test('almoxarife: lista, filtra, abre o lote, registra entradas e volta com o contexto', async ({ page }) => {
  const erros = errosDoConsole(page);
  await page.goto('/estoque');
  await expect(page).toHaveURL('/entrar?destino=%2Festoque');
  await semViolacoes(page);
  await page.getByRole('link', { name: 'Entrar' }).click();
  await semViolacoes(page);
  await page.getByRole('button', { name: 'Almoxarife (fictício)' }).click();
  await expect(page).toHaveURL('/estoque');

  // Listagem: estado com palavra, "N de M", menu ativo e casca com ambiente e perfil.
  await expect(page.getByRole('heading', { level: 1, name: 'Estoque' })).toBeVisible();
  const lista = page.getByRole('region', { name: 'Lotes' });
  const linha = lista.getByRole('row', { name: /DEMO-001/ });
  await expect(linha).toContainText('Herbicida fictício');
  await expect(linha).toContainText('30/06/2027');
  await expect(linha).toContainText('Recebido');
  await expect(lista.getByText('1 de 1')).toBeVisible();
  await expect(page.getByRole('link', { name: 'Estoque', exact: true })).toHaveAttribute(
    'aria-current',
    'page',
  );
  await expect(page.getByText('Desenvolvimento', { exact: true })).toBeVisible();
  await expect(page.getByText(/Almoxarife · /)).toBeVisible();
  await semViolacoes(page);

  // Menu da coluna: popover nativo com valores e contagem; Esc fecha e devolve o foco ao botão.
  const filtrarEstado = page.getByRole('button', { name: 'Filtrar e agrupar Estado' });
  await filtrarEstado.click();
  const menu = page.getByRole('dialog', { name: 'Coluna Estado' });
  await expect(menu).toBeVisible();
  await expect(menu.getByRole('checkbox', { name: /Recebido/ })).toBeChecked();
  await semViolacoes(page);
  await menu.getByRole('checkbox', { name: /Recebido/ }).uncheck();
  await expect(lista.getByText('0 de 1')).toBeVisible();
  await expect(lista.getByText('Nenhum lote corresponde aos filtros.')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(menu).toBeHidden();
  await lista.getByRole('button', { name: 'Limpar filtros' }).click();
  await expect(lista.getByText('1 de 1')).toBeVisible();

  // Ordenar vai para a URL e segue no link do detalhe.
  await lista.getByRole('button', { name: /^Validade/ }).click();
  await expect(page).toHaveURL('/estoque?ordem=validade');
  await expect(lista.getByRole('columnheader', { name: /Validade/ })).toHaveAttribute(
    'aria-sort',
    'ascending',
  );
  await linha.getByRole('link', { name: 'DEMO-001' }).click();

  // Detalhe: trilha, Voltar, estado e o Próximo passo com a única ação primária.
  await expect(page.getByRole('heading', { level: 1, name: 'Lote DEMO-001' })).toBeVisible();
  await expect(page.getByText('Herbicida fictício · validade 30/06/2027')).toBeVisible();
  const proximo = page.getByRole('region', { name: 'Próximo passo' });
  await expect(proximo.getByRole('button', { name: 'Registrar entrada' })).toBeVisible();
  await semViolacoes(page);

  // Validação no campo, dizendo como corrigir; nada é enviado.
  await proximo.getByRole('button', { name: 'Registrar entrada' }).click();
  await expect(proximo.getByText('Informe a quantidade.')).toBeVisible();
  await expect(
    proximo.getByText('Escolha se a entrada vai para inspeção ou já está liberada.'),
  ).toBeVisible();
  await expect(proximo.getByRole('textbox', { name: 'Quantidade' })).toBeFocused();
  await proximo.getByRole('textbox', { name: 'Quantidade' }).fill('1.5');
  await proximo.locator('label', { hasText: 'Liberado' }).click();
  await expect(proximo.getByRole('radio', { name: 'Liberado' })).toBeChecked();
  await proximo.getByRole('button', { name: 'Registrar entrada' }).click();
  await expect(proximo.getByText('Use só números, com vírgula para decimais. Exemplo: 12,5')).toBeVisible();
  await semViolacoes(page);

  // Primeira entrada: 12,5 L liberados.
  await proximo.getByRole('textbox', { name: 'Quantidade' }).fill('12,5');
  await proximo.getByRole('button', { name: 'Registrar entrada' }).click();
  await expect(proximo.getByText('Entrada registrada')).toBeVisible();
  const cabecalho = page.locator('header.cabecalho');
  await expect(cabecalho.getByText('Liberado', { exact: true })).toBeVisible();
  const saldo = page.getByRole('region', { name: 'Saldo' });
  await expect(saldo).toContainText('Utilizável12,5 L');
  await expect(saldo).toContainText('Físico12,5 L');
  const extrato = page.getByRole('region', { name: 'Movimentos do lote' });
  await expect(extrato.getByRole('row', { name: /Entrada · Liberado/ })).toContainText('12,5 L');

  // Segunda entrada pelo teclado, em outra unidade: 2.500 mL para inspeção.
  await proximo.getByRole('textbox', { name: 'Quantidade' }).focus();
  await page.keyboard.type('2.500');
  const unidade = proximo.getByRole('combobox', { name: 'Unidade' });
  await unidade.selectOption('mL');
  await unidade.focus();
  await page.keyboard.press('Tab');
  await page.keyboard.press('Space');
  await expect(proximo.getByRole('radio', { name: 'Em inspeção' })).toBeChecked();
  await page.keyboard.press('Tab');
  await expect(proximo.getByRole('button', { name: 'Registrar entrada' })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(proximo.getByText('Entrada registrada')).toBeVisible();
  await expect(saldo).toContainText('Em inspeção2,5 L');
  await expect(saldo).toContainText('Físico15 L');
  await expect(extrato.getByRole('row', { name: /Entrada · Em inspeção/ })).toContainText('2,5 L (2.500 mL)');
  await expect(extrato.getByRole('row', { name: /Total/ })).toContainText('15 L');
  await semViolacoes(page);

  // Voltar restaura a ordenação da lista.
  await page.getByRole('link', { name: 'Voltar para Estoque' }).click();
  await expect(page).toHaveURL('/estoque?ordem=validade');
  await expect(lista.getByRole('columnheader', { name: /Validade/ })).toHaveAttribute(
    'aria-sort',
    'ascending',
  );
  await expect(linha).toContainText('Liberado');
  await expect(linha).toContainText('12,5 L');
  await expect(linha).toContainText('15 L');

  // Sair revoga a sessão.
  await page.getByRole('button', { name: 'Sair' }).click();
  await expect(page).toHaveURL('/entrar');
  await page.goto('/estoque');
  await expect(page).toHaveURL('/entrar?destino=%2Festoque');
  expect(erros).toEqual([]);
});

test('gerente: consulta o lote sem ação de registrar', async ({ page }) => {
  await entrarComo(page, 'Gerente');
  await page.getByRole('link', { name: 'DEMO-001' }).click();
  const proximo = page.getByRole('region', { name: 'Próximo passo' });
  await expect(proximo).toContainText('Somente consulta. Quem registra entrada é o almoxarife.');
  await expect(page.getByRole('button', { name: 'Registrar entrada' })).toHaveCount(0);
  await expect(page.getByText(/Gerente · /)).toBeVisible();
  await semViolacoes(page);
});

test('cadastros: produto com os seus lotes, que levam ao detalhe do lote', async ({ page }) => {
  await entrarComo(page, 'Almoxarife', '/cadastros/produtos');
  await expect(page.getByRole('heading', { level: 1, name: 'Produtos' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Cadastros', exact: true })).toHaveAttribute(
    'aria-current',
    'page',
  );
  await semViolacoes(page);
  await page.getByRole('link', { name: 'Herbicida fictício' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Herbicida fictício' })).toBeVisible();
  await expect(page.getByText('Unidade-base L · 1 lote')).toBeVisible();
  await semViolacoes(page);
  await page.getByRole('link', { name: 'DEMO-001' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Lote DEMO-001' })).toBeVisible();
});

test('lote inexistente ou de outra organização é 404; segurança nos cabeçalhos', async ({ page }) => {
  const erros = errosDoConsole(page);
  await entrarComo(page, 'Almoxarife');
  const resposta = await page.goto(`/estoque/${randomUUID()}`);
  expect(resposta?.status()).toBe(404);
  await expect(page.getByRole('heading', { name: 'Página não encontrada' })).toBeVisible();
  await semViolacoes(page);
  const lista = await page.goto('/estoque');
  const csp = lista?.headers()['content-security-policy'] ?? '';
  expect(csp).toMatch(/script-src 'self' 'nonce-[A-Za-z0-9+/]{22}==' 'strict-dynamic'/);
  expect(csp).not.toContain('unsafe-inline');
  expect(csp).toContain("frame-ancestors 'none'");
  expect(lista?.headers()['x-content-type-options']).toBe('nosniff');
  expect(lista?.headers()['referrer-policy']).toBe('same-origin');
  expect(lista?.headers()['x-powered-by']).toBeUndefined();
  expect(erros.filter((e) => !e.includes('404'))).toEqual([]);
});
