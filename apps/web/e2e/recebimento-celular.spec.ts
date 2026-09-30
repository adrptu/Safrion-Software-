import { expect, test, type Page } from '@playwright/test';

import { entrarComo, semViolacoes } from './apoio';

// Celular (Pixel 7, toque e UA móvel; PEND-DS-06): a lista, o formulário e o detalhe do recebimento cabem na largura,
// com as mesmas ações e sem violações de acessibilidade (contrato CMD-15 §7.1). O documento passa pelo comando real.
async function semRolagemLateral(page: Page) {
  const { conteudo, janela } = await page.evaluate(() => ({
    conteudo: document.documentElement.scrollWidth,
    janela: window.innerWidth,
  }));
  expect(conteudo).toBeLessThanOrEqual(janela);
}

test('celular: recebe diesel a granel pelo formulário e confere o detalhe', async ({ page }) => {
  await entrarComo(page, 'Almoxarife', '/estoque/recebimentos');
  await semRolagemLateral(page);
  await semViolacoes(page);
  await page.getByRole('link', { name: 'Receber documento' }).tap();
  const origem = page.getByRole('region', { name: 'Documento' });
  await origem.getByRole('textbox', { name: 'Número' }).fill('CEL-001');
  await origem.getByRole('textbox', { name: 'Emissão' }).fill('29/09/2026');
  const linha = page.getByRole('region', { name: 'Linha 1' });
  await linha.getByRole('combobox', { name: 'Produto' }).selectOption({ label: 'Diesel S10' });
  await linha.getByRole('textbox', { name: 'No documento' }).fill('200');
  await linha.getByRole('textbox', { name: 'Apto' }).fill('200');
  await expect(linha).toContainText('Granel · lote do documento');
  await semRolagemLateral(page);
  await semViolacoes(page);
  const confirmar = page.getByRole('button', { name: 'Confirmar recebimento' });
  await confirmar.scrollIntoViewIfNeeded();
  await confirmar.tap();
  await expect(page.getByRole('heading', { level: 1, name: 'NF CEL-001' })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Linhas do documento' })).toContainText(
    'Granel · NF CEL-001 · Fornecedor Teste Ltda',
  );
  await semRolagemLateral(page);
  await semViolacoes(page);
});
