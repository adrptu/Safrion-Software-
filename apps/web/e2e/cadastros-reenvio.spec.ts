import { writeFile } from 'node:fs/promises';
import { expect, test } from '@playwright/test';

import { entrarComo } from './apoio';
import { capturarCadastro, LISTA_CADASTROS, prepararTalhao } from './jornada-cadastros';

const COMANDO = '/comandos/cadastros.criar-talhao';
const CONSULTA = '/intencoes/cadastros.criar-talhao/';

// Contraprova solicitada pelo Gemini real aHa9aqGlKYykn_APhuKU0AQ, item 2, sobre a candidata 86d4a99.
// Harness e execução: Codex, Playwright/Chrome e servidor/banco reais do runner identificado no recibo.
// A ausência de recibo ANTES de um novo POST não prova o resultado DESSE POST. O teste verifica o comportamento
// público equivalente ao estado naoLocalizado: novo resultado incerto exige consultar, mantendo corpo e chave.
test('CAD01 Gemini: 404 anterior não libera repetir depois de nova tentativa offline ou resposta perdida', async ({
  page,
}, testInfo) => {
  await entrarComo(page, 'Gerente', LISTA_CADASTROS);
  const painel = await prepararTalhao(page, 'CAD E2E Reenvio Gemini', 'T1 Reenvio Gemini');
  const observadosNoNavegador: string[] = [];
  let interceptadosAntesDoServidor = 0;
  let encaminhadosPeloInterceptador = 0;
  let respostasPostConfirmadas = 0;
  const statusConsultas: number[] = [];
  page.on('request', (r) => {
    if (r.method() === 'POST' && r.url().endsWith(COMANDO)) observadosNoNavegador.push(r.postData() ?? '');
  });

  // Primeira tentativa interceptada sem forward: cria pendência local, mas nenhum efeito no servidor.
  await page.route(
    `**/api/v1${COMANDO}`,
    async (route) => {
      interceptadosAntesDoServidor += 1;
      await route.abort('failed');
    },
    { times: 1 },
  );
  await painel.getByRole('button', { name: 'Criar talhão', exact: true }).click();
  await expect(painel.getByRole('button', { name: 'Consultar recibo', exact: true })).toBeEnabled();

  async function consultar404() {
    const resposta = page.waitForResponse((r) => r.url().includes(CONSULTA));
    await painel.getByRole('button', { name: 'Consultar recibo', exact: true }).click();
    const r = await resposta;
    statusConsultas.push(r.status());
    expect(r.status()).toBe(404);
    expect(await r.json()).toMatchObject({ codigo: 'RECIBO_NAO_LOCALIZADO' });
    await expect(painel.getByRole('button', { name: 'Reenviar mesmo cadastro', exact: true })).toBeEnabled();
  }
  await consultar404();
  expect(observadosNoNavegador).toHaveLength(1);

  // Etapa literal solicitada: a segunda tentativa ocorre com o navegador realmente offline, sem route.fetch.
  await page.context().setOffline(true);
  const falhaOffline = page.waitForEvent('requestfailed', {
    predicate: (r) => r.method() === 'POST' && r.url().endsWith(COMANDO),
  });
  await painel.getByRole('button', { name: 'Reenviar mesmo cadastro', exact: true }).click();
  const pedidoOffline = await falhaOffline;
  expect(await pedidoOffline.response()).toBeNull();
  await expect(painel.getByRole('button', { name: 'Consultar recibo', exact: true })).toBeEnabled();
  await expect(painel.getByRole('button', { name: 'Reenviar mesmo cadastro', exact: true })).toHaveCount(0);
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toBeDisabled();
  await expect(painel.getByRole('textbox', { name: 'Nome', exact: true })).toHaveValue('T1 Reenvio Gemini');
  expect(observadosNoNavegador).toHaveLength(2);
  await capturarCadastro(page, testInfo, 'cad01-gemini-apos-offline');
  await page.context().setOffline(false);
  await consultar404();

  // Terceira tentativa: servidor confirma de verdade, mas a resposta não chega à UI. O 404 anterior ficou obsoleto.
  await page.route(
    `**/api/v1${COMANDO}`,
    async (route) => {
      encaminhadosPeloInterceptador += 1;
      const r = await route.fetch();
      expect(r.status()).toBe(200);
      expect(await r.json()).toMatchObject({ outcome: 'confirmed', resultingVersion: 1 });
      respostasPostConfirmadas += 1;
      await route.abort('failed');
    },
    { times: 1 },
  );
  await painel.getByRole('button', { name: 'Reenviar mesmo cadastro', exact: true }).click();
  await expect(painel.getByRole('button', { name: 'Consultar recibo', exact: true })).toBeEnabled();
  await expect(painel.getByRole('button', { name: 'Reenviar mesmo cadastro', exact: true })).toHaveCount(0);
  expect(observadosNoNavegador).toHaveLength(3);
  const recibo = page.waitForResponse((r) => r.url().includes(CONSULTA));
  await painel.getByRole('button', { name: 'Consultar recibo', exact: true }).click();
  const confirmado = await recibo;
  statusConsultas.push(confirmado.status());
  expect(confirmado.status()).toBe(200);
  expect(await confirmado.json()).toMatchObject({ outcome: 'confirmed', resultingVersion: 1 });
  await expect(page.getByRole('heading', { level: 1, name: 'T1 Reenvio Gemini', exact: true })).toBeVisible();
  expect(observadosNoNavegador).toHaveLength(3);
  expect(observadosNoNavegador[0]).not.toBe('');
  expect(new Set(observadosNoNavegador).size).toBe(1);
  expect(interceptadosAntesDoServidor).toBe(1);
  expect(encaminhadosPeloInterceptador).toBe(1);
  expect(respostasPostConfirmadas).toBe(1);
  expect(statusConsultas).toEqual([404, 404, 200]);
  await page.getByRole('link', { name: 'Voltar para Fazendas e talhões', exact: true }).click();
  const grupo = page.getByRole('region', { name: 'CAD E2E Reenvio Gemini', exact: true });
  await expect(grupo).toContainText('1 talhão ativo');
  await expect(grupo.getByRole('link', { name: 'T1 Reenvio Gemini', exact: true })).toHaveCount(1);
  await expect(page.getByRole('region', { name: 'Retomar cadastros' })).toHaveCount(0);

  // Contadores de observação não são apresentados como contagem total de recebimentos HTTP pelo servidor.
  const path = testInfo.outputPath('recibo-contraprova-reenvio.json');
  await writeFile(
    path,
    JSON.stringify(
      {
        solicitante: 'Gemini / aHa9aqGlKYykn_APhuKU0AQ',
        executor: 'Codex / Playwright Chrome / servidor e PostgreSQL reais do runner',
        requestsPostObservadosNoNavegador: observadosNoNavegador.length,
        interceptadosAbortadosAntesDoServidor: interceptadosAntesDoServidor,
        postsEncaminhadosPeloInterceptador: encaminhadosPeloInterceptador,
        respostasPostConfirmadasObservadas: respostasPostConfirmadas,
        falhaOffline: pedidoOffline.failure()?.errorText ?? null,
        statusConsultas,
        corposIdenticos: new Set(observadosNoNavegador).size === 1,
        talhoesEncontradosNaListagem: 1,
      },
      null,
      2,
    ),
  );
  await testInfo.attach('recibo-contraprova-reenvio', { path, contentType: 'application/json' });
});
