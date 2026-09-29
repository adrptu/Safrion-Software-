// Fila de vínculo em HML (R-006, GCP-0017, §3c; migração 0006) com PostgreSQL real. Os 15 cenários da fixture
// (fixtures/vinculo-fila-cenarios.json, lida daqui) rodam cada um num banco hml próprio, como a fixture pede; depois,
// concorrência, imutabilidade, permissões, paginação, versão desativada, conexão perdida e a contraprova sem recibo.
// A API do Secret Manager é falsa, em memória, na altura do fetch: o cliente REST de verdade (segredo-pedido.ts) roda
// contra ela, com estado, etag que muda a cada operação e recusa de etag velho. O superusuário do servidor de teste só
// prepara o estado, derruba conexões e confere.
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

import pg from 'pg';
import { describe, expect, inject, it } from 'vitest';

import { definirIdentidadeAmbiente } from '../src/ambiente.js';
import { executarCli } from '../src/cli/vincular-identidade.js';
import { criarSegredoPedido } from '../src/segredo-pedido.js';
import { normalizarCodigo } from '../src/vinculo.js';
import {
  conteudoHash,
  PEDIDO_INVALIDO,
  TRAVA_FILA,
  validarPedido,
  type Pedido,
} from '../src/vinculo-fila.js';
import { criarBanco, type Ambiente } from './ambiente.js';

// Fixture ----------------------------------------------------------------------------------------------------------

interface PedidoFixture {
  readonly ref: string;
  readonly versao: string;
  readonly createTime: string;
  readonly etag: string;
  readonly payload: Record<string, unknown>;
}

interface AcessoFixture {
  readonly codigo: string;
  readonly issuer: string;
  readonly subject: string;
  readonly criado_em: string;
  readonly expira_em: string;
  readonly consumido: boolean;
}

interface Cenario {
  readonly id: string;
  readonly nivel: string;
  readonly estado_inicial: {
    readonly organizacao_ativa: boolean;
    readonly usuario_ativo_com_papel_valido: boolean;
    readonly vinculo_alvo: string;
    readonly recibos: readonly {
      readonly pedido_ref: string;
      readonly resultado: string;
      readonly revogados?: number;
      readonly processado_em: string;
    }[];
    readonly pedidos_acesso: readonly AcessoFixture[];
  };
  readonly pedidos: readonly PedidoFixture[];
  readonly esperado: unknown;
}

interface Retorno {
  readonly pedido_ref: string;
  readonly resultado: string;
  readonly revogados?: number;
  readonly repetido: boolean;
}

const BRUTO = readFileSync(new URL('./fixtures/vinculo-fila-cenarios.json', import.meta.url));
const FIXTURE = JSON.parse(BRUTO.toString('utf8')) as {
  readonly parametros_ensaio: { readonly agora: string; readonly validade_segundos: number };
  readonly cenarios: readonly Cenario[];
};
const AGORA = Date.parse(FIXTURE.parametros_ensaio.agora);
const ORG = '22222222-2222-4222-8222-222222222222';
const USUARIO = '33333333-3333-4333-8333-333333333333';
const ISSUER = 'https://idp.sintetico.invalid';
const SEGREDO = 'projects/projeto-ficticio/secrets/hml-vinculo-pedido';

const cenario = (prefixo: string): Cenario => {
  const c = FIXTURE.cenarios.find((x) => x.id.startsWith(prefixo));
  if (!c) throw new Error(`cenário ${prefixo} ausente`);
  return c;
};
/** Idade em segundos em relação ao "agora" da fixture (negativa no futuro): o teste roda no relógio real. */
const idade = (instante: string) => (AGORA - Date.parse(instante)) / 1000;
const sha256 = (t: string) => createHash('sha256').update(t).digest();
const hashDoCodigo = (codigo: string) => sha256(normalizarCodigo(codigo) ?? codigo);
const pedidoDe = (ped: PedidoFixture): Pedido => {
  const p = validarPedido(JSON.stringify(ped.payload));
  if (p === PEDIDO_INVALIDO) throw new Error(`pedido ${ped.ref} inválido na fixture`);
  return p;
};
const falhaDe = (p: Promise<unknown>) =>
  p.then(
    () => undefined,
    (e: unknown) => e,
  );

// API falsa do Secret Manager ---------------------------------------------------------------------------------------

const METADADOS =
  'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token';
const ROTA =
  /^\/v1\/projects\/projeto-ficticio\/secrets\/hml-vinculo-pedido\/versions(?:\/([1-9][0-9]*)(?::(access|disable|destroy))?)?$/;

interface VersaoFalsa {
  estado: 'ENABLED' | 'DISABLED' | 'DESTROYED';
  etag: string;
  readonly createTime: string;
  dados: Buffer;
}

type Operacao = 'listar' | 'obter' | 'access' | 'disable' | 'destroy';

class ApiFalsa {
  readonly versoes = new Map<string, VersaoFalsa>();
  readonly chamadas: { readonly op: Operacao | 'token'; readonly versao?: string; readonly etag?: string }[] =
    [];
  tamanhoPagina = 100;
  /** A API lista da mais nova para a mais antiga; os testes embaralham. */
  ordemDaListagem: (versoes: string[]) => string[] = (vs) => vs.reverse();
  antes: (op: Operacao, versao?: string) => Promise<void> | void = () => undefined;
  depois: (op: Operacao, versao?: string) => Promise<void> | void = () => undefined;
  private operacoes = 0;

  adicionar(versao: string, createTime: string, conteudo: unknown, etag = `etag-${versao}`): void {
    this.versoes.set(versao, {
      estado: 'ENABLED',
      etag,
      // O Secret Manager dá o createTime no relógio real; a idade é a da fixture.
      createTime: new Date(Date.now() - idade(createTime) * 1000).toISOString(),
      dados: Buffer.from(typeof conteudo === 'string' ? conteudo : JSON.stringify(conteudo)),
    });
  }

  /** Etag novo a cada mudança de estado, como o serviço real; `etag` fixa um valor (CEN-12). */
  trocarEtag(v: VersaoFalsa, etag?: string): void {
    v.etag = etag ?? `${v.etag}~${String(++this.operacoes)}`;
  }

  estados(): Record<string, string> {
    return Object.fromEntries([...this.versoes].map(([k, v]) => [k, v.estado]));
  }

  daVersao(versao: string): string[] {
    return this.chamadas.filter((c) => c.versao === versao).map((c) => c.op);
  }

  readonly buscar = async (url: string, init: RequestInit): Promise<Response> => {
    const cabecalhos = new Headers(init.headers);
    if (url === METADADOS) {
      this.chamadas.push({ op: 'token' });
      if (cabecalhos.get('Metadata-Flavor') !== 'Google') return resposta({}, 403);
      return resposta({ access_token: 'token-ficticio', expires_in: 3599, token_type: 'Bearer' });
    }
    if (cabecalhos.get('Authorization') !== 'Bearer token-ficticio') return resposta({}, 401);
    const u = new URL(url);
    const rota = ROTA.exec(u.pathname);
    if (!rota || u.origin !== 'https://secretmanager.googleapis.com') return resposta({}, 404);
    const [, versao, sufixo] = rota;
    if (!versao) {
      this.chamadas.push({ op: 'listar' });
      await this.antes('listar');
      if (u.searchParams.get('filter') !== 'state:ENABLED') return resposta({}, 400);
      const ativas = this.ordemDaListagem(
        [...this.versoes].filter(([, v]) => v.estado === 'ENABLED').map(([k]) => k),
      );
      const inicio = Number(u.searchParams.get('pageToken') ?? '0');
      const pagina = ativas.slice(inicio, inicio + this.tamanhoPagina);
      const proxima = inicio + this.tamanhoPagina < ativas.length ? String(inicio + this.tamanhoPagina) : '';
      await this.depois('listar');
      return resposta({
        versions: pagina.map((k) => this.recurso(k)),
        ...(proxima ? { nextPageToken: proxima } : {}),
      });
    }
    const op: Operacao =
      sufixo === 'access' || sufixo === 'disable' || sufixo === 'destroy' ? sufixo : 'obter';
    const etag =
      typeof init.body === 'string' ? (JSON.parse(init.body) as { etag?: string }).etag : undefined;
    this.chamadas.push({ op, versao, ...(etag === undefined ? {} : { etag }) });
    await this.antes(op, versao);
    const v = this.versoes.get(versao);
    if (!v) return resposta({}, 404);
    if (op === 'access' && v.estado !== 'ENABLED') {
      return resposta({ error: { status: 'FAILED_PRECONDITION' } }, 400);
    }
    if (op === 'disable' || op === 'destroy') {
      if (etag !== v.etag) return resposta({ error: { status: 'ABORTED' } }, 409);
      if (v.estado === 'DESTROYED') return resposta({ error: { status: 'FAILED_PRECONDITION' } }, 400);
      v.estado = op === 'disable' ? 'DISABLED' : 'DESTROYED';
      if (op === 'destroy') v.dados = Buffer.alloc(0);
      this.trocarEtag(v);
    }
    // A resposta é a do momento da operação; `depois` muda o estado para a chamada seguinte.
    const corpo =
      op === 'access'
        ? { name: this.nome(versao), payload: { data: v.dados.toString('base64') } }
        : this.recurso(versao);
    await this.depois(op, versao);
    return resposta(corpo);
  };

  private nome(versao: string) {
    // A API devolve o projeto pelo número.
    return `projects/123456789/secrets/hml-vinculo-pedido/versions/${versao}`;
  }

  private recurso(versao: string) {
    const v = this.versoes.get(versao);
    return { name: this.nome(versao), createTime: v?.createTime, state: v?.estado, etag: v?.etag };
  }
}

const resposta = (corpo: unknown, status = 200) =>
  new Response(JSON.stringify(corpo), { status, headers: { 'Content-Type': 'application/json' } });

// Palco: um banco hml por cenário ----------------------------------------------------------------------------------

interface Palco {
  readonly c: Cenario;
  readonly amb: Ambiente;
  readonly raiz: pg.Client;
  readonly api: ApiFalsa;
  pedido(ref: string): PedidoFixture;
}

async function criarUsuario(raiz: pg.Client) {
  await raiz.query('INSERT INTO app.app_user (id, organization_id, name, email) VALUES ($1, $2, $3, $4)', [
    USUARIO,
    ORG,
    'Pessoa sintética',
    'pessoa@sintetico.invalid',
  ]);
  await raiz.query(
    "INSERT INTO app.user_role (organization_id, user_id, role_code) VALUES ($1, $2, 'almoxarife')",
    [ORG, USUARIO],
  );
}

async function montar(c: Cenario, ambiente: 'hml' | 'dev' = 'hml'): Promise<Palco> {
  const amb = await criarBanco();
  const mig = new pg.Client({ connectionString: amb.url('migrator') });
  await mig.connect();
  try {
    await definirIdentidadeAmbiente(mig, ambiente);
  } finally {
    await mig.end();
  }
  const url = new URL(inject('urlAdmin'));
  url.pathname = `/${amb.banco}`;
  const raiz = new pg.Client({ connectionString: url.toString() });
  await raiz.connect();
  const e = c.estado_inicial;
  const pedido = (ref: string) => {
    const p = c.pedidos.find((x) => x.ref === ref);
    if (!p) throw new Error(`pedido ${ref} ausente em ${c.id}`);
    return p;
  };
  if (e.organizacao_ativa) {
    await raiz.query('INSERT INTO app.organization (id, name) VALUES ($1, $2)', [
      ORG,
      'Organização sintética',
    ]);
  }
  if (e.usuario_ativo_com_papel_valido) await criarUsuario(raiz);
  for (const a of e.pedidos_acesso) {
    await raiz.query(
      `INSERT INTO app.access_request (code_hash, issuer, subject, created_at, expires_at, consumed_at, organization_id,
                                       user_id)
       VALUES ($1, $2, $3, now() - make_interval(secs => $4), now() - make_interval(secs => $5),
               CASE WHEN $6 THEN now() - interval '3 hours' END, CASE WHEN $6 THEN $7::uuid END,
               CASE WHEN $6 THEN $8::uuid END)`,
      [
        hashDoCodigo(a.codigo),
        a.issuer,
        a.subject,
        idade(a.criado_em),
        idade(a.expira_em),
        a.consumido,
        ORG,
        USUARIO,
      ],
    );
  }
  const alvo = e.vinculo_alvo;
  if (alvo === 'presente' || alvo === 'presente_uma_identidade_anterior') {
    const subject = alvo === 'presente' ? String(e.pedidos_acesso[0]?.subject) : 'subject-sintetico-anterior';
    await raiz.query(
      'INSERT INTO app.identity_link (issuer, subject, organization_id, user_id) VALUES ($1, $2, $3, $4)',
      [ISSUER, subject, ORG, USUARIO],
    );
  }
  for (const r of e.recibos) {
    const ped = pedido(r.pedido_ref);
    const p = pedidoDe(ped);
    await raiz.query(
      `INSERT INTO app.vinculo_pedido_recibo (pedido_id, conteudo_hash, acao, organization_id, user_id, resultado,
                                              revogados, versao_segredo, processado_em)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, now() - make_interval(secs => $9))`,
      [
        p.pedido_id,
        Buffer.from(conteudoHash(p), 'hex'),
        p.acao,
        p.organizacao,
        p.usuario,
        r.resultado,
        r.revogados ?? null,
        ped.versao,
        idade(r.processado_em),
      ],
    );
  }
  const api = new ApiFalsa();
  if (c.nivel === 'cli')
    for (const ped of c.pedidos) api.adicionar(ped.versao, ped.createTime, ped.payload, ped.etag);
  return { c, amb, raiz, api, pedido };
}

async function comPalco(c: Cenario, trabalho: (p: Palco) => Promise<void>, ambiente?: 'hml' | 'dev') {
  const p = await montar(c, ambiente);
  try {
    await trabalho(p);
  } finally {
    await p.raiz.end();
    await p.amb.encerrar();
  }
}

/** Um pedido direto na função, como o comando o chama, com criado_em = now() − idade na mesma transação. */
async function processarNoBanco(p: Palco, ref: string, cliente?: pg.PoolClient) {
  const ped = p.pedido(ref);
  const pedido = pedidoDe(ped);
  const c = cliente ?? (await p.amb.migrator.connect());
  try {
    await c.query('BEGIN');
    const r = await c.query<{ resultado: string; revogados: number | null; repetido: boolean }>(
      `SELECT resultado, revogados, repetido
         FROM app.processar_pedido_vinculo($1, $2, $3, $4, $5, $6, $7, $8, $9, now() - make_interval(secs => $10))`,
      [
        pedido.pedido_id,
        Buffer.from(conteudoHash(pedido), 'hex'),
        ped.versao,
        pedido.acao,
        pedido.acao === 'conceder' ? sha256(pedido.codigo) : null,
        pedido.organizacao,
        pedido.usuario,
        pedido.responsavel,
        pedido.motivo,
        idade(ped.createTime),
      ],
    );
    await c.query('COMMIT');
    const linha = r.rows[0];
    if (!linha) throw new Error('função sem linha');
    return { pedido_ref: ref, ...linha };
  } catch (erro) {
    await c.query('ROLLBACK');
    throw erro;
  } finally {
    if (!cliente) c.release();
  }
}

const numero = async (p: Palco, sql: string) =>
  Number((await p.raiz.query<{ n: number }>(`SELECT (${sql})::int AS n`)).rows[0]?.n);
const recibos = (p: Palco) => numero(p, 'SELECT count(*) FROM app.vinculo_pedido_recibo');
const eventos = (p: Palco) => numero(p, 'SELECT count(*) FROM app.identity_link_event');
const vinculos = async (p: Palco) =>
  (
    await p.raiz.query<{ subject: string }>(
      'SELECT subject FROM app.identity_link WHERE organization_id = $1 AND user_id = $2 ORDER BY subject',
      [ORG, USUARIO],
    )
  ).rows.map((l) => l.subject);
const recibo = async (p: Palco, pedidoId: string) =>
  (
    await p.raiz.query<Record<string, unknown>>(
      `SELECT pedido_id, encode(conteudo_hash, 'hex') AS conteudo_hash, acao, organization_id, user_id, resultado,
              revogados, versao_segredo::text AS versao_segredo, processado_em, database_user
         FROM app.vinculo_pedido_recibo WHERE pedido_id = $1`,
      [pedidoId],
    )
  ).rows[0];

// Comando em modo fila ------------------------------------------------------------------------------------------------

const todasAsLinhas: string[] = [];
type Consulta = (texto: string, valores?: unknown[]) => Promise<pg.QueryResult>;
type Conectar = (config: pg.ClientConfig) => pg.Client;

async function rodarFila(p: Palco, conectar?: Conectar, env: Record<string, string> = {}) {
  const brutas: string[] = [];
  const saida = await executarCli(
    ['fila', '--ambiente', 'hml', '--banco', p.amb.banco],
    { SAFRION_ADMIN_URL: inject('urlAdmin'), SAFRION_PEDIDO_SEGREDO: SEGREDO, ...env },
    (l) => brutas.push(l),
    () => Promise.reject(new Error('a fila não lê código da entrada')),
    conectar,
    undefined,
    (nome) => criarSegredoPedido(nome, p.api.buscar),
  );
  todasAsLinhas.push(...brutas);
  return { saida, linhas: brutas.map((l) => JSON.parse(l) as Record<string, unknown>), brutas };
}

/**
 * Cliente do comando com a conexão derrubada no primeiro COMMIT: depois dele (a confirmação chega ao banco e a
 * resposta se perde) ou antes dele (o servidor encerra a sessão e desfaz a transação; o COMMIT nunca é enviado).
 */
function conectarComQueda(
  p: Palco,
  momento: 'depois' | 'antes',
  registro: { encerrado?: boolean },
): Conectar {
  return (config) => {
    const c = new pg.Client(config);
    const original = c.query.bind(c) as Consulta;
    let armada = true;
    (c as unknown as { query: Consulta }).query = async (texto, valores) => {
      if (!armada || texto !== 'COMMIT') return original(texto, valores);
      armada = false;
      if (momento === 'depois') {
        await original('COMMIT');
        c.connection.stream.destroy();
      } else {
        const pid = (await original('SELECT pg_backend_pid() AS pid')).rows[0] as { pid: number };
        // Com prazo, a função espera o processo do servidor terminar: a transação já foi desfeita.
        const r = await p.raiz.query<{ ok: boolean }>('SELECT pg_terminate_backend($1, 5000) AS ok', [
          pid.pid,
        ]);
        registro.encerrado = r.rows[0]?.ok === true;
      }
      throw new Error('Connection terminated unexpectedly');
    };
    return c;
  };
}

// Cenários da fixture ------------------------------------------------------------------------------------------------

describe('fixture de cenários', () => {
  it('é a revisada (sha256 e2f0ed82…), com 15 cenários e TTL de 3600 s', () => {
    expect(createHash('sha256').update(BRUTO).digest('hex')).toBe(
      'e2f0ed8210d75d5b4adc8a8240c770019c245df45f627ce6d7306a667cee85ba',
    );
    expect(FIXTURE.cenarios.map((c) => c.id.slice(0, 6))).toEqual(
      Array.from({ length: 15 }, (_, i) => `CEN-${String(i + 1).padStart(2, '0')}`),
    );
    expect(FIXTURE.parametros_ensaio.validade_segundos).toBe(3600);
  });
});

describe('cenários de banco', () => {
  it('CEN-01: A(revogar), B(conceder), A repetido devolve o recibo de A e B fica', async () => {
    const c = cenario('CEN-01');
    const e = c.esperado as {
      retornos: Retorno[];
      recibos_finais: number;
      efeitos_aplicados: number;
    };
    await comPalco(c, async (p) => {
      const a = await processarNoBanco(p, 'A');
      const reciboA = await recibo(p, String(p.pedido('A').payload['pedido_id']));
      const b = await processarNoBanco(p, 'B');
      const aDuplicado = await processarNoBanco(p, 'A-duplicado');
      expect([a, b, aDuplicado]).toMatchObject(e.retornos);
      expect(await recibos(p)).toBe(e.recibos_finais);
      expect(await eventos(p)).toBe(e.efeitos_aplicados);
      // criado_por_B: só o vínculo da identidade do pedido de B.
      expect(await vinculos(p)).toEqual([c.estado_inicial.pedidos_acesso[0]?.subject]);
      expect(await recibo(p, String(p.pedido('A').payload['pedido_id']))).toEqual(reciboA);
    });
  });

  it('CEN-03: repetição depois do prazo devolve o resultado gravado, não PEDIDO_ATRASADO', async () => {
    const c = cenario('CEN-03');
    const e = c.esperado as {
      resultado: string;
      repetido: boolean;
      resultado_proibido: string;
      recibos_finais: number;
    };
    await comPalco(c, async (p) => {
      expect(idade(p.pedido('P').createTime)).toBeGreaterThan(FIXTURE.parametros_ensaio.validade_segundos);
      const r = await processarNoBanco(p, 'P');
      expect(r).toMatchObject({ resultado: e.resultado, repetido: e.repetido });
      expect(r.resultado).not.toBe(e.resultado_proibido);
      expect(await eventos(p)).toBe(0);
      expect(await recibos(p)).toBe(e.recibos_finais);
    });
  });

  for (const prefixo of ['CEN-04', 'CEN-05', 'CEN-06']) {
    it(`${prefixo}: prazo de 60 min com now() da transação (60:00 exatos ainda vale)`, async () => {
      const c = cenario(prefixo);
      const e = c.esperado as {
        idade_segundos: number;
        resultado: string;
        repetido: boolean;
        efeitos_aplicados: number;
        recibos_finais: number;
      };
      await comPalco(c, async (p) => {
        expect(idade(p.pedido('P').createTime)).toBe(e.idade_segundos);
        expect(await processarNoBanco(p, 'P')).toMatchObject({
          resultado: e.resultado,
          repetido: e.repetido,
        });
        expect(await eventos(p)).toBe(e.efeitos_aplicados);
        expect(await recibos(p)).toBe(e.recibos_finais);
      });
    });
  }

  it('CEN-07: mesmo pedido_id com outro conteúdo é PEDIDO_ID_REUTILIZADO, sem efeito e sem recibo novo', async () => {
    const c = cenario('CEN-07');
    const e = c.esperado as { resultado: string; recibos_finais: number };
    await comPalco(c, async (p) => {
      const id = String(p.pedido('original').payload['pedido_id']);
      const antes = await recibo(p, id);
      expect(await processarNoBanco(p, 'alterado')).toMatchObject({
        resultado: e.resultado,
        repetido: false,
      });
      expect(await recibos(p)).toBe(e.recibos_finais);
      expect(await recibo(p, id)).toEqual(antes);
      expect(await eventos(p)).toBe(0);
    });
  });

  it('CEN-08: a concatenação com "|" era ambígua; o hashCanonico separa, e a 2ª submissão é reutilização', async () => {
    const c = cenario('CEN-08');
    const e = c.esperado as {
      contrato_b3e17ed: { hash_esperado: string };
      criterio_correcao: { segunda_submissao_sql_futura: string };
    };
    const [a, b] = c.pedidos.map(pedidoDe);
    if (!a || !b || a.acao !== 'conceder' || b.acao !== 'conceder') throw new Error('pedidos de CEN-08');
    const comSeparador = (x: Pedido & { acao: 'conceder' }) =>
      createHash('sha256')
        .update(
          [
            x.pedido_id,
            x.acao,
            x.organizacao,
            x.usuario,
            x.responsavel,
            x.motivo,
            sha256(x.codigo).toString('hex'),
          ].join('|'),
        )
        .digest('hex');
    expect(comSeparador(a)).toBe(e.contrato_b3e17ed.hash_esperado);
    expect(comSeparador(b)).toBe(e.contrato_b3e17ed.hash_esperado);
    expect(conteudoHash(a)).not.toBe(conteudoHash(b));
    await comPalco(c, async (p) => {
      expect(await processarNoBanco(p, 'A')).toMatchObject({ resultado: 'concedido', repetido: false });
      expect(await processarNoBanco(p, 'B')).toMatchObject({
        resultado: e.criterio_correcao.segunda_submissao_sql_futura,
      });
      expect(await recibos(p)).toBe(1);
    });
  });

  it('CEN-14: recusa de negócio grava recibo final; o replay não reavalia depois do usuário existir', async () => {
    const c = cenario('CEN-14');
    const e = c.esperado as { retornos: Retorno[]; recibos_finais: number; efeitos_aplicados: number };
    await comPalco(c, async (p) => {
      const primeiro = await processarNoBanco(p, 'P');
      const gravado = await recibo(p, String(p.pedido('P').payload['pedido_id']));
      await criarUsuario(p.raiz);
      const segundo = await processarNoBanco(p, 'P');
      expect([primeiro, segundo]).toMatchObject(e.retornos);
      expect(await recibos(p)).toBe(e.recibos_finais);
      expect(await recibo(p, String(p.pedido('P').payload['pedido_id']))).toEqual(gravado);
      expect(await eventos(p)).toBe(e.efeitos_aplicados);
      expect(await vinculos(p)).toEqual([]);
    });
  });

  it('CEN-15: app_runtime com erro de privilégio; a função é do app_sessao, sem BYPASSRLS, só com as políticas dela', async () => {
    const c = cenario('CEN-15');
    const e = c.esperado as {
      invariantes_runtime: {
        pode_ler_recibos: boolean;
        pode_inserir_recibos: boolean;
        pode_executar_funcao: boolean;
      };
      invariantes_funcao_interna: { dono: string; bypassrls: boolean };
    };
    expect(e.invariantes_runtime).toMatchObject({
      pode_ler_recibos: false,
      pode_inserir_recibos: false,
      pode_executar_funcao: false,
    });
    await comPalco(c, async (p) => {
      const pedido = pedidoDe(p.pedido('P'));
      const argumentos = [
        pedido.pedido_id,
        Buffer.from(conteudoHash(pedido), 'hex'),
        1,
        'conceder',
        hashDoCodigo('0123456789'),
        ORG,
        USUARIO,
        'r',
        'm',
        new Date(),
      ];
      const sqlstate = async (sql: string, valores: unknown[] = []) =>
        ((await falhaDe(p.amb.app.query(sql, valores))) as { code?: string } | undefined)?.code;
      // Erro de privilégio, não zero linhas.
      expect(await sqlstate('SELECT count(*) FROM app.vinculo_pedido_recibo')).toBe('42501');
      expect(
        await sqlstate(
          `INSERT INTO app.vinculo_pedido_recibo (pedido_id, conteudo_hash, acao, organization_id, user_id, resultado,
                                                  versao_segredo)
           VALUES ($1, $2, 'conceder', $3, $4, 'concedido', 1)`,
          [pedido.pedido_id, Buffer.alloc(32), ORG, USUARIO],
        ),
      ).toBe('42501');
      expect(
        await sqlstate(
          'SELECT * FROM app.processar_pedido_vinculo($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)',
          argumentos,
        ),
      ).toBe('42501');
      const funcao = await p.raiz.query<{ dono: string; definer: boolean; config: string[]; acl: string[] }>(
        `SELECT pg_get_userbyid(proowner) AS dono, prosecdef AS definer, proconfig AS config, proacl::text[] AS acl
           FROM pg_proc WHERE oid = 'app.processar_pedido_vinculo'::regproc`,
      );
      expect(funcao.rows[0]).toMatchObject({
        dono: e.invariantes_funcao_interna.dono,
        definer: true,
        config: ['search_path=pg_catalog, pg_temp'],
      });
      // Só o dono e o migrator; nada para PUBLIC ("=X/...") nem para o app_runtime.
      expect([...(funcao.rows[0]?.acl ?? [])].sort()).toEqual([
        'app_sessao=X/app_sessao',
        'migrator=X/app_sessao',
      ]);
      const papel = await p.raiz.query<{ bypass: boolean }>(
        "SELECT rolbypassrls AS bypass FROM pg_roles WHERE rolname = 'app_sessao'",
      );
      expect(papel.rows[0]?.bypass).toBe(e.invariantes_funcao_interna.bypassrls);
      const tabela = await p.raiz.query<{ rls: boolean; force: boolean }>(
        "SELECT relrowsecurity AS rls, relforcerowsecurity AS force FROM pg_class WHERE oid = 'app.vinculo_pedido_recibo'::regclass",
      );
      expect(tabela.rows[0]).toEqual({ rls: true, force: true });
      const politicas = await p.raiz.query<{ nome: string; cmd: string; papeis: string[] }>(
        `SELECT policyname AS nome, cmd, roles::text[] AS papeis FROM pg_policies
          WHERE schemaname = 'app' AND tablename = 'vinculo_pedido_recibo' ORDER BY policyname`,
      );
      expect(politicas.rows).toEqual([
        { nome: 'leitura_auditoria', cmd: 'SELECT', papeis: ['migrator'] },
        { nome: 'recibo_sessao_insert', cmd: 'INSERT', papeis: ['app_sessao'] },
        { nome: 'recibo_sessao_select', cmd: 'SELECT', papeis: ['app_sessao'] },
      ]);
      const privilegios = await p.raiz.query<{ tipo: string; sessao: boolean; runtime: boolean }>(
        `SELECT t AS tipo, has_table_privilege('app_sessao', 'app.vinculo_pedido_recibo', t) AS sessao,
                has_table_privilege('app_runtime', 'app.vinculo_pedido_recibo', t) AS runtime
           FROM unnest(ARRAY['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE']) t`,
      );
      expect(privilegios.rows).toEqual([
        { tipo: 'SELECT', sessao: true, runtime: false },
        { tipo: 'INSERT', sessao: true, runtime: false },
        { tipo: 'UPDATE', sessao: false, runtime: false },
        { tipo: 'DELETE', sessao: false, runtime: false },
        { tipo: 'TRUNCATE', sessao: false, runtime: false },
      ]);
      // O migrator invoca, e o recibo nasce na transação do efeito: desfeita a transação, não sobra nem um nem outro.
      const mig = await p.amb.migrator.connect();
      try {
        await mig.query('BEGIN');
        const r = await mig.query<{ resultado: string }>(
          'SELECT resultado FROM app.processar_pedido_vinculo($1, $2, $3, $4, $5, $6, $7, $8, $9, now())',
          argumentos.slice(0, 9),
        );
        expect(r.rows[0]?.resultado).toBe('concedido');
        await mig.query('ROLLBACK');
      } finally {
        mig.release();
      }
      expect([await recibos(p), await eventos(p), (await vinculos(p)).length]).toEqual([0, 0, 0]);
      expect(await processarNoBanco(p, 'P')).toMatchObject({ resultado: 'concedido', repetido: false });
      const gravado = await recibo(p, pedido.pedido_id);
      expect(gravado).toMatchObject({ acao: 'conceder', versao_segredo: '1', database_user: 'migrator' });
      // O migrator lê o recibo pela política dele; nenhuma coluna traz o código.
      const lido = await p.amb.migrator.query('SELECT * FROM app.vinculo_pedido_recibo');
      expect(lido.rowCount).toBe(1);
      expect(JSON.stringify(lido.rows)).not.toContain('0123456789');
    });
  });
});

describe('cenários do comando (fila)', () => {
  it('CEN-02: conexão cai depois do COMMIT: 3, recibo gravado, versão fica; a repetição recebe repetido e destrói', async () => {
    const c = cenario('CEN-02');
    const [e1, e2] = (c.esperado as { execucoes: Record<string, unknown>[] }).execucoes;
    await comPalco(c, async (p) => {
      const primeira = await rodarFila(p, conectarComQueda(p, 'depois', {}));
      expect(primeira.saida).toBe(e1?.['exit_code']);
      expect(await recibos(p)).toBe(e1?.['recibos_apos']);
      expect(await eventos(p)).toBe(e1?.['efeitos_acumulados']);
      expect(p.api.estados()).toEqual({ '1': e1?.['estado_segredo'] });
      expect(p.api.daVersao('1')).not.toContain('destroy');
      const etagLido = p.api.versoes.get('1')?.etag;
      const segunda = await rodarFila(p);
      expect(segunda.saida).toBe(e2?.['exit_code']);
      expect(segunda.linhas).toEqual([
        {
          pedido_id: p.pedido('P').payload['pedido_id'],
          versao: e2?.['destruir_versao_exata'],
          resultado: e2?.['resultado'],
          repetido: e2?.['repetido'],
        },
      ]);
      expect(p.api.chamadas.filter((x) => x.op === 'destroy')).toEqual([
        { op: 'destroy', versao: '1', etag: etagLido },
      ]);
      expect(p.api.estados()).toEqual({ '1': 'DESTROYED' });
      expect(await recibos(p)).toBe(e2?.['recibos_apos']);
      expect(await eventos(p)).toBe(e2?.['efeitos_acumulados']);
      expect(await vinculos(p)).toHaveLength(1);
    });
  });

  it('CEN-09: UUID inválido é PEDIDO_INVALIDO sem SQL: versão desativada (reversível), log sem conteúdo, fila segue', async () => {
    const c = cenario('CEN-09');
    const e = c.esperado as { proposta_Claude_22_07: { log: Record<string, string> } };
    await comPalco(c, async (p) => {
      const r = await rodarFila(p);
      expect(r.saida).toBe(1);
      expect(r.linhas).toEqual([
        e.proposta_Claude_22_07.log,
        {
          pedido_id: p.pedido('seguinte').payload['pedido_id'],
          versao: '2',
          resultado: 'concedido',
          repetido: false,
        },
      ]);
      expect(p.api.estados()).toEqual({ '1': 'DISABLED', '2': 'DESTROYED' });
      expect(p.api.daVersao('1')).toEqual(['obter', 'access', 'disable']);
      expect(await recibos(p)).toBe(1);
      expect(r.brutas.join('\n')).not.toContain('invalid-uuid-format');
    });
  });

  it('CEN-10: trava da fila com outra conexão: OCUPADO, saída 1, sem ler segredo nem chamar a função', async () => {
    const c = cenario('CEN-10');
    const e = c.esperado as {
      resultado: string;
      exit_code: number;
      leituras_de_segredo: number;
      novos_recibos: number;
    };
    await comPalco(c, async (p) => {
      // A trava é por banco: a outra execução está no mesmo banco, numa conexão viva.
      await p.raiz.query(`SELECT pg_advisory_lock(${TRAVA_FILA})`);
      try {
        const r = await rodarFila(p);
        expect(r.saida).toBe(e.exit_code);
        expect(r.linhas).toEqual([{ resultado: e.resultado }]);
      } finally {
        await p.raiz.query(`SELECT pg_advisory_unlock(${TRAVA_FILA})`);
      }
      expect(p.api.chamadas).toHaveLength(e.leituras_de_segredo);
      expect(await recibos(p)).toBe(e.novos_recibos);
      expect(await eventos(p)).toBe(0);
    });
  });

  it('CEN-11: conexão encerrada com a transação aberta, antes do COMMIT: 3, nada gravado; a repetição aplica', async () => {
    const c = cenario('CEN-11');
    const [e1, e2] = (c.esperado as { execucoes: Record<string, unknown>[] }).execucoes;
    await comPalco(c, async (p) => {
      const registro: { encerrado?: boolean } = {};
      const primeira = await rodarFila(p, conectarComQueda(p, 'antes', registro));
      expect(primeira.saida).toBe(e1?.['exit_code']);
      // pg_terminate_backend com prazo devolve true só depois que o processo do servidor terminou.
      expect(registro.encerrado).toBe(e1?.['rollback_confirmado']);
      expect(await recibos(p)).toBe(e1?.['recibos_apos']);
      expect(await eventos(p)).toBe(e1?.['efeitos_persistidos_acumulados']);
      expect(p.api.estados()).toEqual({ '1': e1?.['estado_segredo'] });
      const segunda = await rodarFila(p);
      expect(segunda.saida).toBe(e2?.['exit_code']);
      expect(segunda.linhas).toMatchObject([{ resultado: e2?.['resultado'], repetido: e2?.['repetido'] }]);
      expect(await recibos(p)).toBe(e2?.['recibos_apos']);
      expect(await eventos(p)).toBe(e2?.['efeitos_persistidos_acumulados']);
      expect(p.api.estados()).toEqual({ '1': 'DESTROYED' });
    });
  });

  it('CEN-12: etag trocado antes de destruir: 3, recibo de A mantido e B intocado; a repetição relê o etag', async () => {
    const c = cenario('CEN-12');
    const [e1, e2] = (
      c.esperado as {
        execucoes: [
          Record<string, unknown>,
          {
            exit_code: number;
            retornos: Retorno[];
            destruicoes_em_ordem: { versao: string; etag: string }[];
            recibos_apos: number;
            efeitos_acumulados: number;
          },
        ];
      }
    ).execucoes;
    await comPalco(c, async (p) => {
      let trocado = false;
      p.api.antes = (op, versao) => {
        const a = p.api.versoes.get('1');
        if (!trocado && op === 'destroy' && versao === '1' && a) {
          trocado = true;
          p.api.trocarEtag(a, 'etag-sintetico-1-novo');
        }
      };
      const primeira = await rodarFila(p);
      expect(primeira.saida).toBe(e1['exit_code']);
      expect(primeira.linhas.at(-1)).toEqual({
        resultado: 'falha',
        codigo: 'FALHA_INFRAESTRUTURA',
        erro_tipo: 'ErroSegredo',
        codigo_tecnico: 'SEGREDO_HTTP_409',
      });
      expect(await recibos(p)).toBe(e1['recibos_apos']);
      expect(await eventos(p)).toBe(e1['efeitos_acumulados']);
      expect(p.api.estados()).toEqual({ '1': 'ENABLED', '2': 'ENABLED' });
      expect(p.api.daVersao('2')).toEqual([]);
      p.api.chamadas.length = 0;
      const segunda = await rodarFila(p);
      expect(segunda.saida).toBe(e2.exit_code);
      expect(segunda.linhas.map((l) => ({ resultado: l['resultado'], repetido: l['repetido'] }))).toEqual(
        e2.retornos.map((r) => ({ resultado: r.resultado, repetido: r.repetido })),
      );
      expect(
        p.api.chamadas.filter((x) => x.op === 'destroy').map((x) => ({ versao: x.versao, etag: x.etag })),
      ).toEqual(e2.destruicoes_em_ordem);
      const b = await recibo(p, String(p.pedido('B').payload['pedido_id']));
      expect(b).toMatchObject({ resultado: 'revogado', revogados: e2.retornos[1]?.revogados });
      expect(await recibos(p)).toBe(e2.recibos_apos);
      // Revisão: único campo de `esperado` que ficou sem asserção direta.
      expect(await eventos(p)).toBe(e2.efeitos_acumulados);
      expect(await vinculos(p)).toEqual([]);
    });
  });

  it('CEN-13: log do pedido com exatamente pedido_id, versao, resultado e repetido; nunca código, subject ou hash', async () => {
    const c = cenario('CEN-13');
    const e = c.esperado as {
      exit_code: number;
      campos_exatos_log_de_pedido: string[];
      log_esperado: object;
    };
    await comPalco(c, async (p) => {
      const r = await rodarFila(p);
      expect(r.saida).toBe(e.exit_code);
      expect(r.linhas).toEqual([e.log_esperado]);
      expect(Object.keys(r.linhas[0] ?? {})).toEqual(e.campos_exatos_log_de_pedido);
      const codigo = String(p.pedido('P').payload['codigo']);
      const pedido = pedidoDe(p.pedido('P'));
      const proibidos = [
        codigo,
        sha256(codigo).toString('hex'),
        conteudoHash(pedido),
        String(c.estado_inicial.pedidos_acesso[0]?.subject),
      ];
      for (const x of proibidos) expect(r.brutas.join('\n')).not.toContain(x);
    });
  });
});

// Além da fixture (§3c, item 8) --------------------------------------------------------------------------------------

/** Cenário de apoio: estado do CEN-04 com outros pedidos. */
const comPedidos = (pedidos: PedidoFixture[], nivel = 'cli'): Cenario => ({
  ...cenario('CEN-04'),
  nivel,
  pedidos,
});
const revogacao = (n: number, createTime: string, extra: Record<string, unknown> = {}): PedidoFixture => ({
  ref: `R${String(n)}`,
  versao: String(n),
  createTime,
  etag: `etag-${String(n)}`,
  payload: {
    pedido_id: `00000000-0000-4000-8000-0000000001${String(n).padStart(2, '0')}`,
    acao: 'revogar',
    organizacao: ORG,
    usuario: USUARIO,
    responsavel: 'Operador sintético',
    motivo: 'Teste de contrato da fila',
    ...extra,
  },
});

/** Espera a sessão do pid entrar em espera de trava (sem sleep). */
async function esperandoTrava(raiz: pg.Client, pid: number) {
  const limite = Date.now() + 5000;
  while (Date.now() < limite) {
    const r = await raiz.query<{ espera: string | null }>(
      'SELECT wait_event_type AS espera FROM pg_stat_activity WHERE pid = $1',
      [pid],
    );
    if (r.rows[0]?.espera === 'Lock') return;
    await new Promise<void>((resolve) => setImmediate(resolve));
  }
  throw new Error('NAO_ENTROU_NA_ESPERA_ESPERADA');
}

describe('banco: concorrência, imutabilidade e contraprova', () => {
  it('mesmo pedido_id por duas conexões: um efeito, um recibo, o outro repetido', async () => {
    await comPalco({ ...cenario('CEN-04'), nivel: 'banco' }, async (p) => {
      const primeira = await p.amb.migrator.connect();
      const segunda = await p.amb.migrator.connect();
      try {
        await primeira.query('BEGIN');
        await primeira.query(
          `SELECT * FROM app.processar_pedido_vinculo($1, $2, 1, 'conceder', $3, $4, $5, 'r', 'm', now())`,
          [
            pedidoDe(p.pedido('P')).pedido_id,
            Buffer.from(conteudoHash(pedidoDe(p.pedido('P'))), 'hex'),
            hashDoCodigo('0123456789'),
            ORG,
            USUARIO,
          ],
        );
        // O mesmo pedido, pelo caminho normal, noutra conexão: espera a trava do pedido.
        const pid =
          (await segunda.query<{ pid: number }>('SELECT pg_backend_pid() AS pid')).rows[0]?.pid ?? 0;
        const concorrente = processarNoBanco(p, 'P', segunda);
        await esperandoTrava(p.raiz, pid);
        await primeira.query('COMMIT');
        expect(await concorrente).toMatchObject({ resultado: 'concedido', repetido: true });
      } finally {
        primeira.release();
        segunda.release();
      }
      expect([await recibos(p), await eventos(p)]).toEqual([1, 1]);
    });
  });

  it('recibo imutável: UPDATE, DELETE e TRUNCATE recusados até para o superusuário; o migrator não muda nada', async () => {
    await comPalco({ ...cenario('CEN-06'), nivel: 'banco' }, async (p) => {
      await processarNoBanco(p, 'P');
      const id = String(p.pedido('P').payload['pedido_id']);
      const antes = await recibo(p, id);
      for (const sql of [
        "UPDATE app.vinculo_pedido_recibo SET resultado = 'concedido'",
        'DELETE FROM app.vinculo_pedido_recibo',
      ]) {
        expect(await falhaDe(p.raiz.query(sql))).toMatchObject({ code: 'P0001' });
        const r = await p.amb.migrator.query(sql);
        expect(r.rowCount, sql).toBe(0);
      }
      // Revisão: TRUNCATE não passa por RLS nem pelo gatilho de linha, e o dono (migrator) apagava todos os recibos.
      expect(await falhaDe(p.raiz.query('TRUNCATE app.vinculo_pedido_recibo'))).toMatchObject({
        code: 'P0001',
      });
      expect(await falhaDe(p.amb.migrator.query('TRUNCATE app.vinculo_pedido_recibo'))).toMatchObject({
        code: 'P0001',
      });
      expect(await recibo(p, id)).toEqual(antes);
    });
  });

  it('contraprova: sem recibo (funções da 0005 chamadas direto), A, B, A repetido remove o vínculo de B', async () => {
    const c = cenario('CEN-01');
    await comPalco({ ...c, estado_inicial: { ...c.estado_inicial, vinculo_alvo: 'ausente' } }, async (p) => {
      const revogar = () =>
        p.amb.migrator.query('SELECT resultado FROM app.revogar_vinculos($1, $2, $3, $4)', [
          ORG,
          USUARIO,
          'r',
          'm',
        ]);
      await revogar();
      const concessao = await p.amb.migrator.query<{ r: string }>(
        'SELECT app.conceder_vinculo($1, $2, $3, $4, $5) AS r',
        [hashDoCodigo('0123456789'), ORG, USUARIO, 'r', 'm'],
      );
      expect(concessao.rows[0]?.r).toBe('concedido');
      expect(await vinculos(p)).toHaveLength(1);
      await revogar();
      expect(await vinculos(p)).toEqual([]);
    });
  });
});

describe('comando: paginação, versão desativada, conexão perdida e pedido inválido', () => {
  it('lê todas as páginas e ordena por createTime e número, não pela ordem da API', async () => {
    const pedidos = [
      revogacao(5, '2026-09-28T21:50:00Z'),
      revogacao(3, '2026-09-28T21:52:00Z'),
      revogacao(1, '2026-09-28T21:53:00Z'),
      revogacao(4, '2026-09-28T21:51:00Z'),
      revogacao(2, '2026-09-28T21:51:00Z'),
    ];
    await comPalco(comPedidos(pedidos), async (p) => {
      p.api.tamanhoPagina = 2;
      p.api.ordemDaListagem = (vs) => [vs[2], vs[0], vs[4], vs[1], vs[3]].filter((v) => v !== undefined);
      const r = await rodarFila(p);
      expect(r.saida).toBe(0);
      expect(r.linhas.map((l) => l['versao'])).toEqual(['5', '2', '4', '3', '1']);
      expect(r.linhas.every((l) => l['resultado'] === 'sem_vinculo' && l['repetido'] === false)).toBe(true);
      expect(p.api.chamadas.filter((x) => x.op === 'listar')).toHaveLength(3);
      const ordem = await p.raiz.query<{ v: string }>(
        'SELECT versao_segredo::text AS v FROM app.vinculo_pedido_recibo ORDER BY processado_em, versao_segredo',
      );
      expect(ordem.rows.map((l) => l.v)).toEqual(['5', '2', '4', '3', '1']);
      expect(Object.values(p.api.estados()).every((s) => s === 'DESTROYED')).toBe(true);
    });
  });

  it('versão desativada depois da listagem fica de fora (VERSAO_INATIVA); desativada entre a leitura e o acesso para a fila', async () => {
    const pedidos = [
      revogacao(1, '2026-09-28T21:50:00Z'),
      revogacao(2, '2026-09-28T21:51:00Z'),
      revogacao(3, '2026-09-28T21:52:00Z'),
    ];
    await comPalco(comPedidos(pedidos), async (p) => {
      p.api.depois = (op) => {
        const v = p.api.versoes.get('2');
        if (op === 'listar' && v) v.estado = 'DISABLED';
      };
      const r = await rodarFila(p);
      expect(r.saida).toBe(0);
      expect(r.linhas.map((l) => [l['versao'], l['resultado']])).toEqual([
        ['1', 'sem_vinculo'],
        ['2', 'VERSAO_INATIVA'],
        ['3', 'sem_vinculo'],
      ]);
      expect(p.api.daVersao('2')).toEqual(['obter']);
      expect(p.api.estados()).toEqual({ '1': 'DESTROYED', '2': 'DISABLED', '3': 'DESTROYED' });
    });
    await comPalco(comPedidos(pedidos), async (p) => {
      p.api.depois = (op, versao) => {
        const v = p.api.versoes.get('2');
        if (op === 'obter' && versao === '2' && v) v.estado = 'DISABLED';
      };
      const r = await rodarFila(p);
      expect(r.saida).toBe(3);
      expect(r.linhas.at(-1)).toMatchObject({ resultado: 'falha', codigo_tecnico: 'SEGREDO_HTTP_400' });
      expect(p.api.daVersao('3')).toEqual([]);
      expect(await recibos(p)).toBe(1);
    });
  });

  it('conexão perdida depois do 1º pedido: saída 3 sem ler a versão seguinte', async () => {
    const pedidos = [revogacao(1, '2026-09-28T21:50:00Z'), revogacao(2, '2026-09-28T21:51:00Z')];
    await comPalco(comPedidos(pedidos), async (p) => {
      const clientes: pg.Client[] = [];
      p.api.depois = async (op, versao) => {
        const cliente = clientes[0];
        if (op !== 'destroy' || versao !== '1' || !cliente) return;
        const fim = new Promise((resolve) => cliente.once('end', resolve));
        const pid = await p.raiz.query<{ pid: number }>(
          'SELECT pid FROM pg_stat_activity WHERE datname = $1 AND pid <> pg_backend_pid() AND usename = current_user',
          [p.amb.banco],
        );
        for (const l of pid.rows) await p.raiz.query('SELECT pg_terminate_backend($1, 5000)', [l.pid]);
        await fim;
      };
      const r = await rodarFila(p, (config) => {
        const c = new pg.Client(config);
        clientes.push(c);
        return c;
      });
      expect(r.saida).toBe(3);
      expect(r.linhas).toEqual([
        {
          pedido_id: pedidos[0]?.payload['pedido_id'],
          versao: '1',
          resultado: 'sem_vinculo',
          repetido: false,
        },
        {
          resultado: 'falha',
          codigo: 'FALHA_INFRAESTRUTURA',
          erro_tipo: 'ErroFila',
          codigo_tecnico: 'CONEXAO_PERDIDA',
        },
      ]);
      expect(p.api.daVersao('2')).toEqual([]);
      expect(p.api.estados()).toEqual({ '1': 'DESTROYED', '2': 'ENABLED' });
      expect(await recibos(p)).toBe(1);
    });
  });

  it('conexão encerrada durante versions.get ou :access: para ali, sem :access, :disable nem transação (revisão)', async () => {
    // Antes: o inválido era desativado e o válido mandava BEGIN na conexão caída, tudo sem a trava da fila.
    const casos: [Operacao, PedidoFixture, Operacao[]][] = [
      ['obter', revogacao(1, '2026-09-28T21:50:00Z', { observacao: 'x' }), ['obter']],
      ['access', revogacao(1, '2026-09-28T21:50:00Z'), ['obter', 'access']],
    ];
    for (const [momento, pedido, chamadas] of casos) {
      await comPalco(comPedidos([pedido]), async (p) => {
        const clientes: pg.Client[] = [];
        p.api.antes = async (op) => {
          const cliente = clientes[0];
          if (op !== momento || !cliente) return;
          const fim = new Promise((resolve) => cliente.once('end', resolve));
          const pid = await p.raiz.query<{ pid: number }>(
            'SELECT pid FROM pg_stat_activity WHERE datname = $1 AND pid <> pg_backend_pid() AND usename = current_user',
            [p.amb.banco],
          );
          for (const l of pid.rows) await p.raiz.query('SELECT pg_terminate_backend($1, 5000)', [l.pid]);
          await fim;
        };
        const r = await rodarFila(p, (config) => {
          const c = new pg.Client(config);
          clientes.push(c);
          return c;
        });
        expect(r.saida, momento).toBe(3);
        expect(r.linhas, momento).toEqual([
          {
            resultado: 'falha',
            codigo: 'FALHA_INFRAESTRUTURA',
            erro_tipo: 'ErroFila',
            codigo_tecnico: 'CONEXAO_PERDIDA',
          },
        ]);
        expect(p.api.daVersao('1'), momento).toEqual(chamadas);
        expect(p.api.estados(), momento).toEqual({ '1': 'ENABLED' });
        expect(await recibos(p), momento).toBe(0);
      });
    }
  });

  it('campo desconhecido: PEDIDO_INVALIDO, versão desativada, sem recibo, saída 1', async () => {
    await comPalco(comPedidos([revogacao(1, '2026-09-28T21:50:00Z', { observacao: 'x' })]), async (p) => {
      const r = await rodarFila(p);
      expect(r.saida).toBe(1);
      expect(r.linhas).toEqual([{ versao: '1', resultado: 'PEDIDO_INVALIDO' }]);
      expect(p.api.estados()).toEqual({ '1': 'DISABLED' });
      expect(await recibos(p)).toBe(0);
    });
  });

  it('uso e recusas antes de abrir conexão ou ler o segredo', async () => {
    await comPalco(comPedidos([revogacao(1, '2026-09-28T21:50:00Z')]), async (p) => {
      const linhas: string[] = [];
      let clientes = 0;
      const rodar = (argv: string[], env: Record<string, string | undefined>) =>
        executarCli(
          argv,
          env,
          (l) => linhas.push(l),
          () => Promise.reject(new Error('não lê código')),
          () => {
            clientes++;
            throw new Error('cliente que não deveria existir');
          },
          undefined,
          (nome) => criarSegredoPedido(nome, p.api.buscar),
        );
      const base = { SAFRION_ADMIN_URL: inject('urlAdmin'), SAFRION_PEDIDO_SEGREDO: SEGREDO };
      const fila = ['fila', '--ambiente', 'hml', '--banco', p.amb.banco];
      expect(await rodar(fila, { ...base, SAFRION_PEDIDO_SEGREDO: undefined })).toBe(2);
      expect(await rodar([...fila, '--organizacao', ORG], base)).toBe(2);
      expect(await rodar([...fila, 'sobra'], base)).toBe(2);
      expect(
        await rodar(
          fila.map((a) => (a === 'hml' ? 'dev' : a)),
          base,
        ),
      ).toBe(1);
      expect(JSON.parse(linhas.at(-1) ?? '{}')).toMatchObject({ codigo: 'AMBIENTE_PROIBIDO' });
      expect(
        await rodar(
          fila.map((a) => (a === p.amb.banco ? 'Banco-Invalido' : a)),
          base,
        ),
      ).toBe(1);
      expect(JSON.parse(linhas.at(-1) ?? '{}')).toMatchObject({ codigo: 'OPCAO_INVALIDA' });
      expect(await rodar(fila, { ...base, SAFRION_PEDIDO_SEGREDO: 'hml-vinculo-pedido' })).toBe(1);
      expect(JSON.parse(linhas.at(-1) ?? '{}')).toMatchObject({ codigo: 'SEGREDO_INVALIDO' });
      expect(clientes).toBe(0);
      expect(p.api.chamadas).toEqual([]);
      todasAsLinhas.push(...linhas);
    });
    // Banco que não é hml: recusa depois de conectar, antes da trava e do segredo.
    await comPalco(
      comPedidos([revogacao(1, '2026-09-28T21:50:00Z')]),
      async (p) => {
        const r = await rodarFila(p);
        expect(r.saida).toBe(1);
        expect(r.linhas.at(-1)).toMatchObject({ resultado: 'recusado', codigo: 'AMBIENTE_PROIBIDO' });
        expect(p.api.chamadas).toEqual([]);
      },
      'dev',
    );
  });

  it('nenhuma linha do comando, em todo o arquivo, trouxe código, subject ou hash', () => {
    const saida = todasAsLinhas.join('\n');
    expect(todasAsLinhas.length).toBeGreaterThan(10);
    for (const c of FIXTURE.cenarios) {
      for (const a of c.estado_inicial.pedidos_acesso) {
        for (const x of [a.codigo, a.subject, hashDoCodigo(a.codigo).toString('hex')]) {
          expect(saida).not.toContain(x);
        }
      }
      for (const ped of c.pedidos) {
        const p = validarPedido(JSON.stringify(ped.payload));
        if (p !== PEDIDO_INVALIDO) expect(saida).not.toContain(conteudoHash(p));
      }
    }
  });
});
