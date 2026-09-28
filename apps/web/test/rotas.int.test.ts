// Rotas da casca web (ADR 0004) chamadas direto, com banco real identificado como dev e a demonstração restaurada:
// login de DEV pelo mesmo fluxo da homologação (transação → retorno → continuação → sessão), a matriz na API, as
// proteções de requisição e a trava dupla do provedor de desenvolvimento.
import { randomUUID } from 'node:crypto';

import { criarRegistrador } from '@safrion/contracts';
import {
  definirIdentidadeAmbiente,
  emOrganizacao,
  restaurarDemonstracao,
  type Demonstracao,
} from '@safrion/db';
import pg from 'pg';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { contagens, criarBanco, type Ambiente } from '../../../packages/db/test/ambiente';
import { criarRotaComandos } from '../src/rotas/comandos';
import { criarRotasEntrar } from '../src/rotas/entrar';
import { criarRotaSaude } from '../src/rotas/saude';
import { COOKIE_CONTINUACAO, COOKIE_LOGIN, COOKIE_SESSAO } from '../src/seguranca/cookies';

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

describe('/saude e log', () => {
  it('/saude responde o ambiente dev e a última migração, sem endereço do banco', async () => {
    const r = await saude();
    expect(r.status).toBe(200);
    const corpo = (await r.json()) as Record<string, unknown>;
    expect(corpo).toMatchObject({
      status: 'ok',
      ambiente: 'dev',
      migracao: '0004_vinculo_demonstracao.sql',
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
