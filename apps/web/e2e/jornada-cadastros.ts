import { expect, type Page, type TestInfo } from '@playwright/test';

export const LISTA_CADASTROS = '/cadastros/areas?situacao=ativo';

/** Cria só a fazenda pelo comando real, sem perder os campos já digitados do talhão. */
export async function prepararTalhao(page: Page, fazenda: string, talhao: string) {
  await page.getByRole('button', { name: 'Novo talhão', exact: true }).click();
  const painel = page.getByRole('dialog', { name: 'Talhão', exact: true });
  await expect(painel).toBeVisible();
  await painel.getByRole('textbox', { name: 'Nome', exact: true }).fill(talhao);
  await painel.getByRole('textbox', { name: 'Área declarada (ha)', exact: true }).fill('204');
  await painel.getByRole('button', { name: 'Cadastrar fazenda', exact: true }).click();
  const cadastroFazenda = painel.getByRole('region', { name: 'Cadastrar fazenda', exact: true });
  await cadastroFazenda.getByRole('textbox', { name: 'Nome', exact: true }).fill(fazenda);
  await expect(cadastroFazenda.getByRole('combobox', { name: 'Fuso horário' })).toHaveValue(
    'America/Sao_Paulo',
  );
  await cadastroFazenda.getByRole('button', { name: 'Criar fazenda', exact: true }).click();
  await expect(cadastroFazenda).toBeHidden();
  await expect(
    painel.getByRole('combobox', { name: 'Fazenda', exact: true }).locator('option:checked'),
  ).toHaveText(fazenda);
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toHaveValue(talhao);
  await expect(painel.getByRole('textbox', { name: 'Área declarada (ha)', exact: true })).toHaveValue('204');
  return painel;
}

export async function criarTalhao(page: Page, fazenda: string, talhao: string) {
  const painel = await prepararTalhao(page, fazenda, talhao);
  await painel.getByRole('button', { name: 'Criar talhão', exact: true }).click();
  await expect(page.getByRole('heading', { level: 1, name: talhao, exact: true })).toBeVisible();
  return new URL(page.url()).pathname.split('/').at(-1) ?? '';
}

/** A navegação de teclado deve deixar o botão visível e desobstruído, inclusive com viewport móvel. */
export async function primariaAoAlcance(page: Page) {
  const painel = page.getByRole('dialog', { name: 'Talhão', exact: true });
  await painel.getByRole('textbox', { name: 'Área declarada (ha)', exact: true }).focus();
  await page.keyboard.press('Tab');
  await expect(painel.getByRole('button', { name: 'Voltar', exact: true })).toBeFocused();
  await page.keyboard.press('Tab');
  const primaria = painel.getByRole('button', { name: 'Criar talhão', exact: true });
  await expect(primaria).toBeFocused();
  await expect(primaria).toBeInViewport({ ratio: 1 });
  expect(
    await primaria.evaluate((el) => {
      const b = el.getBoundingClientRect();
      const noCentro = document.elementFromPoint(b.x + b.width / 2, b.y + b.height / 2);
      return noCentro !== null && el.contains(noCentro);
    }),
  ).toBe(true);
  return primaria;
}

/** Arquivo explícito permanece no output da jornada, mesmo quando o reporter exibe só texto. */
export async function capturarCadastro(page: Page, testInfo: TestInfo, nome: string) {
  const path = testInfo.outputPath(`${nome}.png`);
  await page.screenshot({ path });
  await testInfo.attach(nome, { path, contentType: 'image/png' });
}
