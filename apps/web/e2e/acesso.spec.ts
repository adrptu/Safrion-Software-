import { expect, test } from '@playwright/test';

import { errosDoConsole, semViolacoes } from './apoio';

// Sem vínculo depois de um login OIDC (ADR 0004 §11): /entrar mostra o código de referência do pedido que o servidor
// entregou no cookie HttpOnly. O navegador não aceita plantar cookie Secure num http://localhost; como a página só lê o
// cabeçalho Cookie da requisição, o teste o envia direto. O fluxo OIDC que grava o cookie está nos testes de rota.
test('sem vínculo: /entrar mostra o código do pedido só vindo do cookie, sem cache', async ({ page }) => {
  const erros = errosDoConsole(page);
  await page.setExtraHTTPHeaders({ cookie: '__Host-safrion-pedido=ABCDE12345' });
  const resposta = await page.goto('/entrar?erro=SEM_VINCULO');
  expect(resposta?.headers()['cache-control']).toContain('no-store');
  await expect(page.getByText('Sua conta ainda não tem acesso a nenhuma organização.')).toBeVisible();
  await expect(page.getByText('ABCDE-12345')).toBeVisible();
  await semViolacoes(page);
  // O código não é lido da URL nem aparece com outro motivo de volta.
  await page.goto('/entrar?erro=TOKEN_INVALIDO&codigo=ZZZZZ99999');
  await expect(page.getByText('ABCDE-12345')).toHaveCount(0);
  await expect(page.getByText('ZZZZZ-99999')).toHaveCount(0);
  // Cookie repetido (tentativa de plantar outro) ou ausente: nenhum código.
  for (const cookie of ['__Host-safrion-pedido=ABCDE12345; __Host-safrion-pedido=FGHJK67890', '']) {
    await page.setExtraHTTPHeaders(cookie ? { cookie } : {});
    await page.goto('/entrar?erro=SEM_VINCULO');
    await expect(page.getByText('Sua conta ainda não tem acesso a nenhuma organização.')).toBeVisible();
    await expect(page.getByText(/[0-9A-Z]{5}-[0-9A-Z]{5}/)).toHaveCount(0);
  }
  expect(erros).toEqual([]);
});
