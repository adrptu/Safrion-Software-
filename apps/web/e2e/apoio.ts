import AxeBuilder from '@axe-core/playwright';
import { expect, type Page } from '@playwright/test';

/** Entra pelo provedor de DEV (usuário fictício) a partir de uma tela protegida e volta a ela. */
export async function entrarComo(page: Page, usuario: 'Almoxarife' | 'Gerente', destino = '/estoque') {
  await page.goto(destino);
  await expect(page).toHaveURL(/\/entrar\?destino=/);
  await page.getByRole('link', { name: 'Entrar' }).click();
  await expect(page.getByRole('heading', { name: 'Usuário fictício' })).toBeVisible();
  await page.getByRole('button', { name: `${usuario} (fictício)` }).click();
  await expect(page).toHaveURL(new RegExp(`${destino.replace(/[/?]/g, '\\$&')}$`));
}

/** WCAG 2.2 A/AA pelo axe, na tela como está (menus fechados ou abertos). */
export async function semViolacoes(page: Page) {
  const r = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
    .analyze();
  expect(r.violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ')).join(', ')}`)).toEqual(
    [],
  );
}

/** Erros do console (inclui violação de CSP) coletados durante o teste. */
export function errosDoConsole(page: Page): string[] {
  const erros: string[] = [];
  page.on('console', (m) => {
    if (m.type() === 'error') erros.push(m.text());
  });
  page.on('pageerror', (e) => erros.push(e.message));
  return erros;
}
