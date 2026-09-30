import { expect, test, type Page } from '@playwright/test';

import { entrarComo, semViolacoes } from './apoio';
import { capturarCadastro, LISTA_CADASTROS, prepararTalhao, primariaAoAlcance } from './jornada-cadastros';

async function semRolagemLateral(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
}

// Pixel 7 emulado: cobre toque, Tab, largura e axe; não simula o teclado virtual físico do Android.
test('celular CAD01: cria fazenda e talhão com ação alcançável, sem perder o contexto', async ({
  page,
}, testInfo) => {
  await entrarComo(page, 'Gerente', LISTA_CADASTROS);
  await semRolagemLateral(page);
  await semViolacoes(page);
  await prepararTalhao(page, 'CAD E2E Celular', 'T1 Celular');
  await semRolagemLateral(page);
  await semViolacoes(page);
  await capturarCadastro(page, testInfo, 'cad01-celular-painel');
  const criar = await primariaAoAlcance(page);
  await criar.tap();
  await expect(page.getByRole('heading', { level: 1, name: 'T1 Celular', exact: true })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Identificação' })).toContainText('204,00 ha (declarada)');
  await capturarCadastro(page, testInfo, 'cad01-celular-detalhe');
  await semRolagemLateral(page);
  await semViolacoes(page);
  await page.getByRole('link', { name: 'Voltar para Fazendas e talhões', exact: true }).tap();
  await expect(page).toHaveURL(LISTA_CADASTROS);
  await expect(page.getByRole('dialog')).toBeHidden();
  await expect(page.getByRole('region', { name: 'CAD E2E Celular', exact: true })).toContainText(
    '1 talhão ativo',
  );
  await semRolagemLateral(page);
});
