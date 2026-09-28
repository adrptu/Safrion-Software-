import { expect, test } from '@playwright/test';

import { entrarComo, semViolacoes } from './apoio';

// Celular (abaixo de 768 px, PEND-DS-06): a lista vira cartões com os mesmos filtros, sem rolagem lateral da página.
test('celular: lista em cartões, filtros acessíveis e sem rolagem lateral', async ({ page }) => {
  await entrarComo(page, 'Almoxarife');
  const lista = page.getByRole('region', { name: 'Lotes' });
  await expect(lista.getByRole('link', { name: 'DEMO-001' })).toBeVisible();
  await expect(lista.getByRole('button', { name: 'Filtrar e agrupar Estado' })).toBeVisible();
  const largura = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
  expect(largura[0]).toBeLessThanOrEqual(largura[1] ?? 0);
  await semViolacoes(page);
  await lista.getByRole('link', { name: 'DEMO-001' }).click();
  await expect(page.getByRole('heading', { level: 1, name: 'Lote DEMO-001' })).toBeVisible();
  const detalhe = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
  expect(detalhe[0]).toBeLessThanOrEqual(detalhe[1] ?? 0);
  await semViolacoes(page);
});
