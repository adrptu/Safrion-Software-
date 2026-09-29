// Rotas da casca web (ADR 0004) chamadas direto, com banco real identificado como dev e a demonstração restaurada:
// login de DEV pelo mesmo fluxo da homologação (transação → retorno → continuação → sessão), a matriz na API, as
// proteções de requisição e a trava dupla do provedor de desenvolvimento.
import { createHash, generateKeyPairSync, randomUUID, sign } from 'node:crypto';

import { criarRegistrador } from '@safrion/contracts';
import {
  concederVinculo,
  definirIdentidadeAmbiente,
  emOrganizacao,
  restaurarDemonstracao,
  type Demonstracao,
} from '@safrion/db';
import type { CustomFetch } from 'openid-client';
import pg from 'pg';
import { afterAll, beforeAll, describe, expect, inject, it } from 'vitest';

import { contagens, criarBanco, type Ambiente } from '../../../packages/db/test/ambiente';
import { criarRotaComandos } from '../src/rotas/comandos';
import { criarRotasEntrar } from '../src/rotas/entrar';
import { criarRotaSaude } from '../src/rotas/saude';
import { COOKIE_CONTINUACAO, COOKIE_LOGIN, COOKIE_PEDIDO, COOKIE_SESSAO } from '../src/seguranca/cookies';
import { criarFabricaOidc } from '../src/servidor/oidc';

const ORIGEM = 'http://localhost:3000';
let amb: Ambiente;
let demo: Demonstracao;
let local: string;
const linhas: string[] = [];
const registrador = criarRegistrador({
  servico: 'web-teste',
  versao: '0.0.0-teste',
  escrever: (l) => linhas.push(l),
  agora: () => '2026-09-28T12:00:00.000Z',
});

let ambienteDoProcesso = 'dev';
const deps = () => ({
  banco: amb.app,
  origem: ORIGEM,
  registrador,
  ambienteDoProcesso,
  versao: '0.0.0-teste',
  commit: 'abc1234',
});
const entrar = criarRotasEntrar(deps);
const comandos = criarRotaComandos(deps);
const saude = criarRotaSaude(deps);

/** Valor de um cookie definido pela resposta (Set-Cookie), ou undefined se foi apagado ou não veio. */
function cookieDe(resposta: Response, nome: string): string | undefined {
  const linha = resposta.headers.getSetCookie().find((c) => c.startsWith(`${nome}=`));
  const valor = linha?.slice(nome.length + 1).split(';')[0];
  return valor === '' ? undefined : valor;
}

const destinoDe = (r: Response) =>
  new URL(r.headers.get('location') ?? '').pathname + new URL(r.headers.get('location') ?? '').search;

function formulario(
  caminho: string,
  campos: Record<string, string>,
  cookie?: string,
  origem = ORIGEM,
): Request {
  return new Request(`${ORIGEM}${caminho}`, {
    method: 'POST',
    body: new URLSearchParams(campos).toString(),
    headers: {
      'content-type': 'application/x-www-form-urlencoded',
      origin: origem,
      ...(cookie ? { cookie } : {}),
    },
  });
}

/** Login de DEV completo; devolve o token de sessão (um vínculo e um papel: conclui sem tela de escolha). */
async function loginDev(usuario: 'demo-almoxarife' | 'demo-gerente', destino = '/estoque'): Promise<string> {
  const inicio = await entrar.iniciar(
    new Request(`${ORIGEM}/entrar/iniciar?destino=${encodeURIComponent(destino)}`),
  );
  expect(inicio.status).toBe(303);
  const ticket = cookieDe(inicio, COOKIE_LOGIN);
  const state = new URL(inicio.headers.get('location') ?? '').searchParams.get('state') ?? '';
  const autorizado = await entrar.autorizarDesenvolvimento(
    formulario('/entrar/desenvolvimento/autorizar', { state, usuario }),
  );
  expect(autorizado.status).toBe(303);
  const retorno = await entrar.retorno(
    new Request(autorizado.headers.get('location') ?? '', {
      headers: { cookie: `${COOKIE_LOGIN}=${ticket ?? ''}` },
    }),
  );
  expect(destinoDe(retorno)).toBe(destino);
  const sessao = cookieDe(retorno, COOKIE_SESSAO);
  if (!sessao) throw new Error('login de DEV não criou sessão');
  return sessao;
}

function comando(
  corpo: unknown,
  cookie?: string,
  extra: Record<string, string> = {},
  tipo = 'estoque.registrar-entrada',
) {
  const req = new Request(`${ORIGEM}/api/v1/comandos/${tipo}`, {
    method: 'POST',
    body: typeof corpo === 'string' ? corpo : JSON.stringify(corpo),
    headers: {
      'content-type': 'application/json',
      origin: ORIGEM,
      ...(cookie ? { cookie: `${COOKIE_SESSAO}=${cookie}` } : {}),
      ...extra,
    },
  });
  return comandos(req, { params: Promise.resolve({ commandType: tipo }) });
}

const entrada = (chave = randomUUID()) => ({
  idempotencyKey: chave,
  target: { type: 'lot', id: demo.loteId, expectedVersion: 0 },
  data: {
    lote: demo.loteId,
    local,
    movimento: { tipo: 'entrada', quantidade: { valor: '20', unidade: 'L' }, situacao: 'liberado_livre' },
  },
});

/** Versão atual do lote da demonstração (outros testes deste arquivo já registraram entradas). */
async function versaoDoLote(): Promise<number> {
  const r = await emOrganizacao(amb.app, demo.organizationId, (c) =>
    c.query<{ version: string }>('SELECT version FROM app.lot WHERE id = $1', [demo.loteId]),
  );
  return Number(r.rows[0]?.version);
}

beforeAll(async () => {
  amb = await criarBanco();
  const mig = new pg.Client({ connectionString: amb.url('migrator') });
  await mig.connect();
  try {
    await definirIdentidadeAmbiente(mig, 'dev');
  } finally {
    await mig.end();
  }
  demo = await restaurarDemonstracao(amb.app, { confirmar: 'dev', ambienteDoProcesso: 'dev' });
  local = await emOrganizacao(amb.app, demo.organizationId, async (c) => {
    const r = await c.query<{ id: string }>('SELECT id FROM app.stock_location');
    return r.rows[0]?.id ?? '';
  });
});

afterAll(async () => {
  await amb.encerrar();
});

describe('login de DEV pelo fluxo da homologação', () => {
  it('almoxarife entra e registra uma entrada; o reenvio devolve o mesmo recibo', async () => {
    const sessao = await loginDev('demo-almoxarife');
    const pedido = entrada();
    const r = await comando(pedido, sessao);
    expect(r.status).toBe(200);
    const recibo = (await r.json()) as { outcome: string; alreadyReceived: boolean; receiptId: string };
    expect(recibo).toMatchObject({ outcome: 'confirmed', alreadyReceived: false });
    const de_novo = (await (await comando(pedido, sessao)).json()) as {
      receiptId: string;
      alreadyReceived: boolean;
    };
    expect(de_novo).toMatchObject({ receiptId: recibo.receiptId, alreadyReceived: true });
  });

  it('gerente entra, mas a API nega o comando com 403 (matriz)', async () => {
    const sessao = await loginDev('demo-gerente');
    const r = await comando(entrada(), sessao);
    expect(r.status).toBe(403);
    expect(await r.json()).toMatchObject({ codigo: 'SEM_PERMISSAO' });
  });

  it('sair revoga a sessão: o comando seguinte é 401', async () => {
    const sessao = await loginDev('demo-almoxarife');
    const saiu = await entrar.sair(formulario('/sair', {}, `${COOKIE_SESSAO}=${sessao}`));
    expect(saiu.status).toBe(303);
    expect(cookieDe(saiu, COOKIE_SESSAO)).toBeUndefined();
    expect((await comando(entrada(), sessao)).status).toBe(401);
  });

  it('state adulterado e ticket reutilizado não entram', async () => {
    const inicio = await entrar.iniciar(new Request(`${ORIGEM}/entrar/iniciar`));
    const ticket = cookieDe(inicio, COOKIE_LOGIN) ?? '';
    const cookie = { cookie: `${COOKIE_LOGIN}=${ticket}` };
    const adulterado = await entrar.retorno(
      new Request(`${ORIGEM}/entrar/retorno?state=outro&code=demo-almoxarife`, { headers: cookie }),
    );
    expect(destinoDe(adulterado)).toBe('/entrar?erro=STATE_DIVERGENTE');
    expect(cookieDe(adulterado, COOKIE_SESSAO)).toBeUndefined();
    const state = new URL(inicio.headers.get('location') ?? '').searchParams.get('state') ?? '';
    const reuso = await entrar.retorno(
      new Request(`${ORIGEM}/entrar/retorno?state=${state}&code=demo-almoxarife`, { headers: cookie }),
    );
    expect(destinoDe(reuso)).toBe('/entrar?erro=TICKET_AUSENTE_OU_USADO');
  });

  it('destino externo pedido no início termina em "/", nunca fora da aplicação', async () => {
    for (const externo of ['//malicioso.invalid', 'https://malicioso.invalid/x']) {
      const inicio = await entrar.iniciar(
        new Request(`${ORIGEM}/entrar/iniciar?destino=${encodeURIComponent(externo)}`),
      );
      const state = new URL(inicio.headers.get('location') ?? '').searchParams.get('state') ?? '';
      const aut = await entrar.autorizarDesenvolvimento(
        formulario('/entrar/desenvolvimento/autorizar', { state, usuario: 'demo-almoxarife' }),
      );
      const ret = await entrar.retorno(
        new Request(aut.headers.get('location') ?? '', {
          headers: { cookie: `${COOKIE_LOGIN}=${cookieDe(inicio, COOKIE_LOGIN) ?? ''}` },
        }),
      );
      expect(ret.headers.get('location'), externo).toBe(`${ORIGEM}/`);
    }
  });
});

describe('escolha de organização e papel', () => {
  it('com dois papéis vai para a tela de escolha; campo de identidade no corpo é recusado; escolha válida entra', async () => {
    await emOrganizacao(amb.app, demo.organizationId, (c) =>
      c.query('INSERT INTO app.user_role (organization_id, user_id, role_code) VALUES ($1, $2, $3)', [
        demo.organizationId,
        demo.usuarios.find((u) => u.papel === 'almoxarife')?.usuarioId,
        'gerente',
      ]),
    );
    const continuar = async () => {
      const inicio = await entrar.iniciar(new Request(`${ORIGEM}/entrar/iniciar?destino=/estoque`));
      const state = new URL(inicio.headers.get('location') ?? '').searchParams.get('state') ?? '';
      const aut = await entrar.autorizarDesenvolvimento(
        formulario('/entrar/desenvolvimento/autorizar', { state, usuario: 'demo-almoxarife' }),
      );
      const ret = await entrar.retorno(
        new Request(aut.headers.get('location') ?? '', {
          headers: { cookie: `${COOKIE_LOGIN}=${cookieDe(inicio, COOKIE_LOGIN) ?? ''}` },
        }),
      );
      expect(destinoDe(ret)).toBe('/entrar/escolher');
      return cookieDe(ret, COOKIE_CONTINUACAO) ?? '';
    };
    const recusada = await entrar.confirmarEscolha(
      formulario(
        '/entrar/escolher/confirmar',
        { organizationId: demo.organizationId, papel: 'gerente', subject: 'demo-gerente' },
        `${COOKIE_CONTINUACAO}=${await continuar()}`,
      ),
    );
    expect(destinoDe(recusada)).toBe('/entrar?erro=CONTRATO_INVALIDO');
    const aceita = await entrar.confirmarEscolha(
      formulario(
        '/entrar/escolher/confirmar',
        { organizationId: demo.organizationId, papel: 'gerente' },
        `${COOKIE_CONTINUACAO}=${await continuar()}`,
      ),
    );
    expect(destinoDe(aceita)).toBe('/estoque');
    const sessao = cookieDe(aceita, COOKIE_SESSAO);
    expect((await comando(entrada(), sessao)).status).toBe(403); // escolheu gerente: a matriz nega
    // Devolve a demonstração ao estado de um papel por usuário, para os testes seguintes.
    await emOrganizacao(amb.migrator, demo.organizationId, (c) =>
      c.query("DELETE FROM app.user_role WHERE user_id = $1 AND role_code = 'gerente'", [
        demo.usuarios.find((u) => u.papel === 'almoxarife')?.usuarioId,
      ]),
    );
  });
});

describe('proteções da API de comandos', () => {
  it('sem sessão 401; Origin errado 403; não JSON 415; comando inexistente 404', async () => {
    const sessao = await loginDev('demo-almoxarife');
    expect((await comando(entrada())).status).toBe(401);
    expect((await comando(entrada(), sessao, { origin: 'http://malicioso.invalid' })).status).toBe(403);
    expect((await comando(entrada(), sessao, { 'content-type': 'text/plain' })).status).toBe(415);
    expect((await comando(entrada(), sessao, {}, 'estoque.apagar-tudo')).status).toBe(404);
  });

  it('corpo acima do limite sem Content-Length: 413 antes do parse', async () => {
    const sessao = await loginDev('demo-almoxarife');
    const grande = new ReadableStream<Uint8Array>({
      start(c) {
        for (let i = 0; i < 20; i++) c.enqueue(new TextEncoder().encode('x'.repeat(1024)));
        c.close();
      },
    });
    const req = new Request(`${ORIGEM}/api/v1/comandos/estoque.registrar-entrada`, {
      method: 'POST',
      body: grande,
      duplex: 'half',
      headers: { 'content-type': 'application/json', origin: ORIGEM, cookie: `${COOKIE_SESSAO}=${sessao}` },
    } as RequestInit);
    const r = await comandos(req, { params: Promise.resolve({ commandType: 'estoque.registrar-entrada' }) });
    expect(r.status).toBe(413);
    expect(await r.json()).toMatchObject({ codigo: 'CORPO_EXCEDE_LIMITE' });
  });

  it('B1-C01: alvo de outro tipo ou de outro lote é 400 sem efeito; o alvo lot do próprio lote passa', async () => {
    const sessao = await loginDev('demo-almoxarife');
    const antes = await contagens(amb.app, demo.organizationId);
    const base = entrada();
    for (const target of [
      { ...base.target, type: 'invoice' },
      { ...base.target, type: 'Lot' },
      { ...base.target, id: randomUUID() },
    ]) {
      const r = await comando({ ...base, idempotencyKey: randomUUID(), target }, sessao);
      expect(r.status, JSON.stringify(target)).toBe(400);
      expect(await r.json()).toMatchObject({ codigo: 'CONTRATO_INVALIDO' });
    }
    expect(await contagens(amb.app, demo.organizationId)).toEqual(antes);
    const ok = await comando(
      { ...base, target: { ...base.target, expectedVersion: await versaoDoLote() } },
      sessao,
    );
    expect(ok.status).toBe(200);
    expect(await ok.json()).toMatchObject({ outcome: 'confirmed', targetType: 'lot', targetId: demo.loteId });
    expect(await contagens(amb.app, demo.organizationId)).toEqual({
      movimentos: (antes['movimentos'] ?? 0) + 1,
      intencoes: (antes['intencoes'] ?? 0) + 1,
      auditoria: (antes['auditoria'] ?? 0) + 1,
      outbox: (antes['outbox'] ?? 0) + 1,
    });
  });

  it('organização no corpo é recusa de contrato (a organização vem da sessão); JSON inválido também', async () => {
    const sessao = await loginDev('demo-almoxarife');
    const r = await comando({ ...entrada(), organizationId: randomUUID() }, sessao);
    expect(r.status).toBe(400);
    expect(await r.json()).toMatchObject({ codigo: 'CONTRATO_INVALIDO' });
    expect((await comando('{', sessao)).status).toBe(400);
  });
});

describe('trava dupla do provedor de desenvolvimento', () => {
  it('processo que não diz dev: 404 na tela do provedor e login indisponível', async () => {
    ambienteDoProcesso = 'hml';
    try {
      const r = await entrar.autorizarDesenvolvimento(
        formulario('/entrar/desenvolvimento/autorizar', { state: 'x', usuario: 'demo-almoxarife' }),
      );
      expect(r.status).toBe(404);
      const inicio = await entrar.iniciar(new Request(`${ORIGEM}/entrar/iniciar`));
      expect(destinoDe(inicio)).toBe('/entrar?erro=LOGIN_INDISPONIVEL');
    } finally {
      ambienteDoProcesso = 'dev';
    }
  });
});

describe('login OIDC pela casca (adaptador do Codex, provedor sintético)', () => {
  const ORIGEM_HML = 'https://hml.safrion.invalid';
  const ISSUER = 'https://idp.sintetico.invalid';
  const CLIENTE = { id: 'safrion-hml', segredo: `segredo-${randomUUID()}` };
  const ENV_OIDC = {
    SAFRION_OIDC_ISSUER: ISSUER,
    SAFRION_OIDC_CLIENT_ID: CLIENTE.id,
    SAFRION_OIDC_CLIENT_SECRET: CLIENTE.segredo,
  };
  // Processo diz hml: a trava do provedor de desenvolvimento fecha e o OIDC é o único caminho.
  const depsHml = () => ({ ...deps(), origem: ORIGEM_HML, ambienteDoProcesso: 'hml' });

  /**
   * Provedor OIDC sintético atrás do transporte HTTP do adaptador: descoberta, chaves e troca do código com
   * client_secret_post e PKCE S256 conferidos de verdade, código de uso único. A "tela de autorização" é o teste:
   * autorizar() lê a URL que a casca devolveu e emite um código para o subject escolhido.
   */
  function criarIdp() {
    const chave = generateKeyPairSync('rsa', { modulusLength: 2048 });
    const jwk = { ...chave.publicKey.export({ format: 'jwk' }), kid: 'k1', alg: 'RS256', use: 'sig' };
    const pendentes = new Map<string, { subject: string; nonce: string; desafio: string; retorno: string }>();
    const chamadas = { descoberta: 0, token: 0 };
    const emitidos: string[] = [];
    let foraDoAr = false;
    const b64 = (o: unknown) => Buffer.from(JSON.stringify(o)).toString('base64url');
    const transporte: CustomFetch = (url, opcoes) => {
      const caminho = new URL(url).pathname;
      if (caminho === '/.well-known/openid-configuration') {
        chamadas.descoberta++;
        if (foraDoAr) return Promise.reject(new TypeError('fetch failed'));
        return Promise.resolve(
          Response.json({
            issuer: ISSUER,
            authorization_endpoint: `${ISSUER}/authorize`,
            token_endpoint: `${ISSUER}/token`,
            jwks_uri: `${ISSUER}/jwks`,
            response_types_supported: ['code'],
            id_token_signing_alg_values_supported: ['RS256'],
            authorization_response_iss_parameter_supported: true,
          }),
        );
      }
      if (caminho === '/jwks') return Promise.resolve(Response.json({ keys: [jwk] }));
      chamadas.token++;
      const corpo = new URLSearchParams(
        typeof opcoes.body === 'string' || opcoes.body instanceof URLSearchParams ? opcoes.body : '',
      );
      const codigo = corpo.get('code') ?? '';
      const pedido = pendentes.get(codigo);
      pendentes.delete(codigo);
      const desafio = createHash('sha256')
        .update(corpo.get('code_verifier') ?? '')
        .digest('base64url');
      if (
        !pedido ||
        corpo.get('grant_type') !== 'authorization_code' ||
        corpo.get('client_id') !== CLIENTE.id ||
        corpo.get('client_secret') !== CLIENTE.segredo ||
        corpo.get('redirect_uri') !== pedido.retorno ||
        desafio !== pedido.desafio
      ) {
        return Promise.resolve(Response.json({ error: 'invalid_grant' }, { status: 400 }));
      }
      const agora = Math.floor(Date.now() / 1000);
      const conteudo = `${b64({ alg: 'RS256', kid: 'k1', typ: 'JWT' })}.${b64({
        iss: ISSUER,
        sub: pedido.subject,
        aud: CLIENTE.id,
        iat: agora,
        exp: agora + 300,
        nonce: pedido.nonce,
      })}`;
      const idToken = `${conteudo}.${sign('RSA-SHA256', Buffer.from(conteudo), chave.privateKey).toString('base64url')}`;
      emitidos.push(idToken);
      return Promise.resolve(
        Response.json({
          access_token: randomUUID(),
          token_type: 'Bearer',
          expires_in: 300,
          id_token: idToken,
        }),
      );
    };
    return {
      transporte,
      chamadas,
      emitidos,
      ficarForaDoAr(v: boolean) {
        foraDoAr = v;
      },
      autorizar(location: string, subject: string): URLSearchParams {
        const p = new URL(location).searchParams;
        const codigo = randomUUID();
        emitidos.push(codigo);
        pendentes.set(codigo, {
          subject,
          nonce: p.get('nonce') ?? '',
          desafio: p.get('code_challenge') ?? '',
          retorno: p.get('redirect_uri') ?? '',
        });
        return new URLSearchParams({ code: codigo, state: p.get('state') ?? '', iss: ISSUER });
      },
    };
  }

  /** Vínculo explícito issuer + subject → usuário da demonstração, gravado pelo administrador do servidor de teste. */
  async function vincular(subject: string, papel: string) {
    const usuario = demo.usuarios.find((u) => u.papel === papel);
    if (!usuario) throw new Error(`papel ${papel} ausente na demonstração`);
    const url = new URL(inject('urlAdmin'));
    url.pathname = `/${amb.banco}`;
    const admin = new pg.Client({ connectionString: url.toString() });
    await admin.connect();
    try {
      await admin.query(
        'INSERT INTO app.identity_link (issuer, subject, organization_id, user_id) VALUES ($1, $2, $3, $4)',
        [ISSUER, subject, demo.organizationId, usuario.usuarioId],
      );
    } finally {
      await admin.end();
    }
  }

  async function entrarPeloIdp(
    rotas: ReturnType<typeof criarRotasEntrar>,
    idp: ReturnType<typeof criarIdp>,
    subject: string,
  ) {
    const inicio = await rotas.iniciar(new Request(`${ORIGEM_HML}/entrar/iniciar?destino=%2Festoque`));
    expect(inicio.status).toBe(303);
    const location = inicio.headers.get('location') ?? '';
    const pedido = new Request(
      `${ORIGEM_HML}/entrar/retorno?${idp.autorizar(location, subject).toString()}`,
      {
        headers: { cookie: `${COOKIE_LOGIN}=${cookieDe(inicio, COOKIE_LOGIN) ?? ''}` },
      },
    );
    return { location, pedido, retorno: await rotas.retorno(pedido.clone()) };
  }

  it('identidade vinculada entra: PKCE S256, callback fixo na origem e sessão do papel vinculado', async () => {
    const idp = criarIdp();
    const rotas = criarRotasEntrar(depsHml, criarFabricaOidc({ env: ENV_OIDC, transporte: idp.transporte }));
    await vincular('oidc-almoxarife', 'almoxarife');
    const { location, pedido, retorno } = await entrarPeloIdp(rotas, idp, 'oidc-almoxarife');
    const autorizacao = new URL(location);
    expect(`${autorizacao.origin}${autorizacao.pathname}`).toBe(`${ISSUER}/authorize`);
    expect(Object.fromEntries(autorizacao.searchParams)).toMatchObject({
      client_id: CLIENTE.id,
      redirect_uri: `${ORIGEM_HML}/entrar/retorno`,
      response_type: 'code',
      scope: 'openid',
      code_challenge_method: 'S256',
    });
    expect(location).not.toContain(CLIENTE.segredo);
    expect(destinoDe(retorno)).toBe('/estoque');
    const sessao = cookieDe(retorno, COOKIE_SESSAO);
    if (!sessao) throw new Error('login OIDC não criou sessão');
    expect(idp.chamadas).toEqual({ descoberta: 1, token: 1 });
    // A sessão é a do almoxarife vinculado: a API aceita o comando dele.
    const r = await comando(
      { ...entrada(), target: { type: 'lot', id: demo.loteId, expectedVersion: await versaoDoLote() } },
      sessao,
    );
    expect(r.status).toBe(200);
    // O mesmo retorno de novo não entra: a transação do login é de uso único.
    expect(destinoDe(await rotas.retorno(pedido))).toBe('/entrar?erro=TICKET_AUSENTE_OU_USADO');
    expect(idp.chamadas.token).toBe(1);
  });

  it('identidade sem vínculo não entra, mesmo com o provedor confirmando', async () => {
    const idp = criarIdp();
    const rotas = criarRotasEntrar(depsHml, criarFabricaOidc({ env: ENV_OIDC, transporte: idp.transporte }));
    linhas.length = 0;
    const { retorno } = await entrarPeloIdp(rotas, idp, 'oidc-sem-vinculo');
    expect(destinoDe(retorno)).toBe('/entrar?erro=SEM_VINCULO');
    // Banco de dev: nenhum pedido é registrado, e nenhum código antigo sobra no navegador.
    expect(cookieDe(retorno, COOKIE_PEDIDO)).toBeUndefined();
    expect(linhas.join('\n')).toContain('"motivo":"PEDIDO_FORA_DE_HML"');
    expect(cookieDe(retorno, COOKIE_SESSAO)).toBeUndefined();
    expect(idp.chamadas.token).toBe(1);
  });

  it('sem configuração, ou com issuer sem https: login indisponível, sem chamar o provedor', async () => {
    const idp = criarIdp();
    for (const [env, motivo] of [
      [{}, 'SEM_CONFIGURACAO'],
      [{ ...ENV_OIDC, SAFRION_OIDC_ISSUER: 'http://idp.sintetico.invalid' }, 'CONFIGURACAO_INVALIDA'],
    ] as const) {
      linhas.length = 0;
      const rotas = criarRotasEntrar(depsHml, criarFabricaOidc({ env, transporte: idp.transporte }));
      const inicio = await rotas.iniciar(new Request(`${ORIGEM_HML}/entrar/iniciar`));
      expect(destinoDe(inicio), motivo).toBe('/entrar?erro=LOGIN_INDISPONIVEL');
      expect(linhas.join('\n'), motivo).toContain(`"motivo":"${motivo}"`);
    }
    expect(idp.chamadas).toEqual({ descoberta: 0, token: 0 });
  });

  it('provedor fora do ar: indisponível agora; quando volta, entra sem reiniciar e descobre uma vez só', async () => {
    const idp = criarIdp();
    const rotas = criarRotasEntrar(depsHml, criarFabricaOidc({ env: ENV_OIDC, transporte: idp.transporte }));
    idp.ficarForaDoAr(true);
    linhas.length = 0;
    const fora = await rotas.iniciar(new Request(`${ORIGEM_HML}/entrar/iniciar`));
    expect(destinoDe(fora)).toBe('/entrar?erro=PROVEDOR_INDISPONIVEL');
    expect(linhas.join('\n')).toContain('"motivo":"DESCOBERTA_FALHOU"');
    idp.ficarForaDoAr(false);
    for (let i = 0; i < 2; i++) {
      const inicio = await rotas.iniciar(new Request(`${ORIGEM_HML}/entrar/iniciar`));
      expect(new URL(inicio.headers.get('location') ?? '').origin).toBe(ISSUER);
    }
    expect(idp.chamadas.descoberta).toBe(2);
  });

  it('nenhuma linha de log traz segredo do cliente, código, id_token ou ticket', async () => {
    const idp = criarIdp();
    const rotas = criarRotasEntrar(depsHml, criarFabricaOidc({ env: ENV_OIDC, transporte: idp.transporte }));
    await vincular('oidc-log', 'almoxarife');
    linhas.length = 0;
    const { pedido, retorno } = await entrarPeloIdp(rotas, idp, 'oidc-log');
    expect(destinoDe(retorno)).toBe('/estoque');
    const tudo = linhas.join('\n');
    expect(linhas.length).toBeGreaterThan(0);
    const ticket = (pedido.headers.get('cookie') ?? '').split('=')[1] ?? '';
    for (const segredo of [
      CLIENTE.segredo,
      ticket,
      cookieDe(retorno, COOKIE_SESSAO) ?? '',
      ...idp.emitidos,
    ]) {
      expect(segredo.length).toBeGreaterThan(8);
      expect(tudo.includes(segredo)).toBe(false);
    }
  });
  describe('pedido de acesso em HML (ADR 0004 §11)', () => {
    let ambHml: Ambiente;
    let demoHml: Demonstracao;
    let raizHml: pg.Client;
    const depsBancoHml = () => ({ ...depsHml(), banco: ambHml.app });
    const linhaDoCookie = (r: Response, nome: string) =>
      r.headers.getSetCookie().find((c) => c.startsWith(`${nome}=`)) ?? '';

    beforeAll(async () => {
      ambHml = await criarBanco();
      const mig = new pg.Client({ connectionString: ambHml.url('migrator') });
      await mig.connect();
      try {
        await definirIdentidadeAmbiente(mig, 'hml');
      } finally {
        await mig.end();
      }
      demoHml = await restaurarDemonstracao(ambHml.app, { confirmar: 'hml', ambienteDoProcesso: 'hml' });
      const url = new URL(inject('urlAdmin'));
      url.pathname = `/${ambHml.banco}`;
      raizHml = new pg.Client({ connectionString: url.toString() });
      await raizHml.connect();
    });
    afterAll(async () => {
      await raizHml.end();
      await ambHml.encerrar();
    });

    it('sem vínculo: pedido registrado, código só no cookie; o administrador concede e a pessoa entra', async () => {
      const idp = criarIdp();
      const rotas = criarRotasEntrar(
        depsBancoHml,
        criarFabricaOidc({ env: ENV_OIDC, transporte: idp.transporte }),
      );
      linhas.length = 0;
      const { retorno } = await entrarPeloIdp(rotas, idp, 'oidc-pedido');
      expect(destinoDe(retorno)).toBe('/entrar?erro=SEM_VINCULO');
      expect(cookieDe(retorno, COOKIE_SESSAO)).toBeUndefined();
      const codigo = cookieDe(retorno, COOKIE_PEDIDO) ?? '';
      expect(codigo).toMatch(/^[0-9A-HJKMNP-TV-Z]{10}$/);
      const linha = linhaDoCookie(retorno, COOKIE_PEDIDO);
      expect(linha).toContain('; Path=/;');
      expect(linha).toMatch(/; HttpOnly; Secure; SameSite=Lax$/);
      const validade = Date.parse(/Expires=([^;]+)/.exec(linha)?.[1] ?? '') - Date.now();
      expect(validade).toBeGreaterThan(9 * 60_000);
      expect(validade).toBeLessThanOrEqual(10 * 60_000);
      expect(retorno.headers.get('location')).not.toContain(codigo);
      expect(retorno.headers.get('cache-control')).toBe('no-store');
      const log = linhas.join('\n');
      expect(log).toContain('"motivo":"PEDIDO_REGISTRADO"');
      for (const segredo of [codigo, 'oidc-pedido']) expect(log.includes(segredo)).toBe(false);
      // O pedido não concede nada: entrar de novo antes da concessão continua sem vínculo.
      expect(destinoDe((await entrarPeloIdp(rotas, idp, 'oidc-pedido')).retorno)).toBe(
        '/entrar?erro=SEM_VINCULO',
      );
      // O código mostrado por último é o que vale; o administrador concede por ele.
      const atual = cookieDe((await entrarPeloIdp(rotas, idp, 'oidc-pedido')).retorno, COOKIE_PEDIDO) ?? '';
      const almoxarife = demoHml.usuarios.find((u) => u.papel === 'almoxarife')?.usuarioId ?? '';
      const mig = await ambHml.migrator.connect();
      try {
        expect(
          await concederVinculo(mig, {
            codigo: atual,
            organizacao: demoHml.organizationId,
            usuario: almoxarife,
            responsavel: 'teste de rota',
            motivo: 'pedido pela casca',
          }),
        ).toBe('concedido');
      } finally {
        mig.release();
      }
      const segunda = await entrarPeloIdp(rotas, idp, 'oidc-pedido');
      expect(destinoDe(segunda.retorno)).toBe('/estoque');
      expect(cookieDe(segunda.retorno, COOKIE_SESSAO)).toBeDefined();
      expect(linhaDoCookie(segunda.retorno, COOKIE_PEDIDO)).toContain('Max-Age=0');
    });

    it('cota cheia: sem código novo, o cookie anterior é apagado e o motivo vai para o log', async () => {
      await raizHml.query(
        `INSERT INTO app.access_request (code_hash, issuer, subject, expires_at)
         SELECT sha256(convert_to('cota-' || i, 'UTF8')), 'https://carga.invalid', 'cota-' || i,
                now() + interval '1 hour'
           FROM generate_series(1, 100) i`,
      );
      try {
        const idp = criarIdp();
        const rotas = criarRotasEntrar(
          depsBancoHml,
          criarFabricaOidc({ env: ENV_OIDC, transporte: idp.transporte }),
        );
        linhas.length = 0;
        const { retorno } = await entrarPeloIdp(rotas, idp, 'oidc-sem-cota');
        expect(destinoDe(retorno)).toBe('/entrar?erro=SEM_VINCULO');
        expect(cookieDe(retorno, COOKIE_PEDIDO)).toBeUndefined();
        expect(linhaDoCookie(retorno, COOKIE_PEDIDO)).toContain('Max-Age=0');
        expect(linhas.join('\n')).toContain('"motivo":"PEDIDOS_ESGOTADOS"');
      } finally {
        await raizHml.query("DELETE FROM app.access_request WHERE issuer = 'https://carga.invalid'");
      }
    });
  });
});

describe('/saude e log', () => {
  it('/saude responde o ambiente dev e a última migração, sem endereço do banco', async () => {
    const r = await saude();
    expect(r.status).toBe(200);
    const corpo = (await r.json()) as Record<string, unknown>;
    expect(corpo).toMatchObject({
      status: 'ok',
      ambiente: 'dev',
      migracao: '0006_vinculo_fila.sql',
      commit: 'abc1234',
    });
    expect(JSON.stringify(corpo)).not.toContain('postgres');
  });

  it('nenhuma linha de log traz token, cookie ou ticket', async () => {
    const sessao = await loginDev('demo-almoxarife');
    await comando(entrada(), sessao);
    expect(linhas.length).toBeGreaterThan(0);
    const tudo = linhas.join('\n');
    expect(tudo).not.toContain(sessao);
    expect(tudo).not.toContain(COOKIE_SESSAO);
    expect(tudo).not.toContain(COOKIE_LOGIN);
  });
});
