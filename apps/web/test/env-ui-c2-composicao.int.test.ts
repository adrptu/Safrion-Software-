// Contraprova complementar ENV-UI-01-C2 sobre a composição PR33 (3af0cee) + envelope ENV-CAD01-NUL-CL22 (c036bef) +
// consumidor (e65255c). Rota real (POST /api/v1/comandos e GET /api/v1/intencoes), envelope real e PostgreSQL real
// (SAFRION_TEST_DATABASE_URL; banco descartável por arquivo), com o mesmo preparo de cadastros-rotas.int.test.ts:
// identidade dev, demonstração restaurada e login de DEV do gerente. O corpo enviado é o corpo congelado da intenção do
// consumidor (novaIntencao().corpo), como o gancho faz no fetch, e cada resposta HTTP real passa pelo classificador do
// consumidor (desfechoDoEnvio / desfechoDaConsulta, apps/web/src/cadastros/intencao.ts).
//
// O que prova:
// 1. Nome com U+0000: 400 CONTRATO_INVALIDO (campo nome, NOME_COM_NUL) antes do envelope; o consumidor dá nao_gravado
//    (não é o sinal permanente de classe 22); nada em farm, intent_record, audit_log e outbox.
// 2. Classe 22 pela rota real, sem efeito de teste: nome com surrogate isolado (U+D800) passa por EsquemaNomeCadastro,
//    o INSERT da fazenda o aceita (o driver grava U+FFFD) e a auditoria o recusa no jsonb (after_state com "\ud800":
//    22P02 no PostgreSQL). Resposta 500 FALHA_INTERNA com detalhe exato {resultadoIncerto:false,
//    repetirMesmoConteudo:false}; log comando.falhou em nível erro com codigo_pg de classe 22; consumidor: corrigir no
//    primeiro envio e incerto com bloqueioPermanente no reenvio; o mesmo conteúdo falha igual; nada gravado; a chave não
//    fica consumida (a mesma chave com o nome corrigido confirma uma vez).
// 3. Sucesso: recibo 200; o reenvio do mesmo corpo e a consulta devolvem o mesmo recibo (só alreadyReceived muda); o
//    consumidor resolve os três; uma linha em farm, intent_record, audit_log e outbox.
// 4. Mesma chave com outro conteúdo: 409 IDEMPOTENCY_KEY_REUSED com o receiptId original; consumidor nao_gravado;
//    fazenda, registro da intenção (recibo, hash, correlação) e contagens inalterados; o outro nome não existe.
//
// O que NÃO prova:
// - O gancho useCadastroComando, a persistência de pendencias.ts e as telas (EditorCadastro, EnviosCadastro). Quem
//   impede o reenvio depois de "corrigir" ou "somente_consulta" é o gancho, pela falha guardada; isso não roda aqui. O
//   classificador puro da consulta devolve naoLocalizado para o 404 do caso 2, por desenho.
// - Rede, Next e navegador: a Request é montada no processo e entregue ao handler da rota.
// - Falhas incertas (COMMIT enviado, conexão caída, ROLLBACK sem confirmação): ficam em conexao-caida.int.test.ts.
// - Outros caminhos de classe 22. O do caso 2 é o único alcançável pela rota de cadastro achado na leitura do código:
//   U+0000, confirmedAt, área e versão são recusados no esquema (400) ou cabem nas colunas. Se o esquema passar a recusar
//   o surrogate isolado (400), o caso 2 deixa de ser alcançável pela rota e deve passar ao mecanismo de
//   packages/db/test/comando.int.test.ts (efeito com SELECT 'nao-e-numero'::int e respostaDeErro).
// - Que o surrogate isolado deva chegar ao banco: o caso 2 registra o comportamento atual da composição.
import { randomUUID } from 'node:crypto';

import {
  COMANDOS_CADASTRO,
  EsquemaDadosCriarFazenda,
  EsquemaErro,
  EsquemaRecibo,
  criarRegistrador,
  falhaPermanenteSemGravacao,
  statusDoRecibo,
} from '@safrion/contracts';
import {
  definirIdentidadeAmbiente,
  emOrganizacao,
  restaurarDemonstracao,
  type Demonstracao,
} from '@safrion/db';
import pg from 'pg';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

import { criarBanco, type Ambiente } from '../../../packages/db/test/ambiente';
import { desfechoDaConsulta, desfechoDoEnvio, novaIntencao, type Intencao } from '../src/cadastros/intencao';
import { criarRotaComandos } from '../src/rotas/comandos';
import { criarRotasEntrar } from '../src/rotas/entrar';
import { criarRotaIntencoes } from '../src/rotas/intencoes';
import { COOKIE_LOGIN, COOKIE_SESSAO } from '../src/seguranca/cookies';

const ORIGEM = 'http://localhost:3000';
const CRIAR = COMANDOS_CADASTRO.criarFazenda;
const FUSO = 'America/Sao_Paulo';
const NAO_ACEITO = 'O servidor não aceitou o pedido. Confira os dados e confirme de novo.';
let amb: Ambiente;
let demo: Demonstracao;
let gerente: string;

/** Linhas de log do envelope, para conferir o SQLSTATE que não sai na resposta. */
const linhasDeLog: string[] = [];
const registrador = criarRegistrador({
  servico: 'web-teste',
  versao: '0.0.0-teste',
  escrever: (linha) => {
    linhasDeLog.push(linha);
  },
  agora: () => '2026-10-01T12:00:00.000Z',
});
const deps = () => ({
  banco: amb.app,
  origem: ORIGEM,
  registrador,
  ambienteDoProcesso: 'dev',
  versao: '0.0.0-teste',
  commit: 'abc1234',
});
const entrar = criarRotasEntrar(deps);
const comandos = criarRotaComandos(deps);
const intencoes = criarRotaIntencoes(deps);

function cookieDe(resposta: Response, nome: string): string | undefined {
  const linha = resposta.headers.getSetCookie().find((c) => c.startsWith(`${nome}=`));
  const valor = linha?.slice(nome.length + 1).split(';')[0];
  return valor === '' ? undefined : valor;
}

async function loginDev(usuario: 'demo-gerente'): Promise<string> {
  const inicio = await entrar.iniciar(new Request(`${ORIGEM}/entrar/iniciar?destino=%2Fcadastros%2Fareas`));
  const state = new URL(inicio.headers.get('location') ?? '').searchParams.get('state') ?? '';
  const autorizado = await entrar.autorizarDesenvolvimento(
    new Request(`${ORIGEM}/entrar/desenvolvimento/autorizar`, {
      method: 'POST',
      body: new URLSearchParams({ state, usuario }).toString(),
      headers: { 'content-type': 'application/x-www-form-urlencoded', origin: ORIGEM },
    }),
  );
  const retorno = await entrar.retorno(
    new Request(autorizado.headers.get('location') ?? '', {
      headers: { cookie: `${COOKIE_LOGIN}=${cookieDe(inicio, COOKIE_LOGIN) ?? ''}` },
    }),
  );
  const sessao = cookieDe(retorno, COOKIE_SESSAO);
  if (!sessao) throw new Error('login de DEV não criou sessão');
  return sessao;
}

/** Como o gancho (useCadastroComando, postar): POST do corpo congelado da intenção, com a correlação conhecida. */
async function enviar(intencao: Intencao, correlacao: string) {
  const r = await comandos(
    new Request(`${ORIGEM}/api/v1/comandos/${intencao.commandType}`, {
      method: 'POST',
      body: intencao.corpo,
      headers: {
        'content-type': 'application/json',
        origin: ORIGEM,
        cookie: `${COOKIE_SESSAO}=${gerente}`,
        'x-correlation-id': correlacao,
      },
    }),
    { params: Promise.resolve({ commandType: intencao.commandType }) },
  );
  const corpo: unknown = await r.json();
  return { status: r.status, corpo, correlacao: r.headers.get('x-correlation-id') };
}

/** Como o gancho (useCadastroComando, consulta): GET do recibo pela chave. */
async function consultar(intencao: Intencao) {
  const r = await intencoes(
    new Request(`${ORIGEM}/api/v1/intencoes/${intencao.commandType}/${encodeURIComponent(intencao.chave)}`, {
      headers: { cookie: `${COOKIE_SESSAO}=${gerente}` },
    }),
    { params: Promise.resolve({ commandType: intencao.commandType, chave: intencao.chave }) },
  );
  const corpo: unknown = await r.json();
  return { status: r.status, corpo };
}

/** Linhas da chave e do alvo, pelo papel da aplicação sob a RLS da organização de demonstração. */
async function linhas(chave: string, alvo: string) {
  return emOrganizacao(amb.app, demo.organizationId, async (c) => {
    const n = async (sql: string, p: unknown[]) => (await c.query<{ n: string }>(sql, p)).rows[0]?.n;
    return {
      fazendas: await n('SELECT count(*)::text n FROM app.farm WHERE id = $1', [alvo]),
      intencoes: await n(
        'SELECT count(*)::text n FROM app.intent_record WHERE command_type = $1 AND idempotency_key = $2',
        [CRIAR, chave],
      ),
      auditoria: await n(
        'SELECT count(*)::text n FROM app.audit_log WHERE command_type = $1 AND idempotency_key = $2',
        [CRIAR, chave],
      ),
      outbox: await n(
        'SELECT count(*)::text n FROM app.outbox WHERE causation_command_type = $1 AND causation_id = $2',
        [CRIAR, chave],
      ),
    };
  });
}
const NADA = { fazendas: '0', intencoes: '0', auditoria: '0', outbox: '0' };
const UMA = { fazendas: '1', intencoes: '1', auditoria: '1', outbox: '1' };

async function registroDaIntencao(chave: string) {
  return emOrganizacao(
    amb.app,
    demo.organizationId,
    async (c) =>
      (
        await c.query<{ receipt_id: string; payload_hash: string; outcome: string; correlation_id: string }>(
          `SELECT receipt_id, payload_hash, outcome, correlation_id FROM app.intent_record
          WHERE command_type = $1 AND idempotency_key = $2`,
          [CRIAR, chave],
        )
      ).rows,
  );
}

async function fazenda(alvo: string) {
  return emOrganizacao(
    amb.app,
    demo.organizationId,
    async (c) =>
      (
        await c.query<{ name: string; version: string }>('SELECT name, version FROM app.farm WHERE id = $1', [
          alvo,
        ])
      ).rows,
  );
}

const sufixo = () => randomUUID().slice(0, 8);

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
  expect(demo.organizationId).toBeTruthy();
  gerente = await loginDev('demo-gerente');
});
afterAll(async () => {
  await amb.encerrar();
});

describe('ENV-UI-01-C2 na composição: rota, recibo e PostgreSQL pelo classificador do consumidor', () => {
  it('1. nome com U+0000: 400 de contrato antes do envelope; consumidor nao_gravado; nada gravado', async () => {
    const chave = randomUUID();
    const alvo = randomUUID();
    const intencao = novaIntencao(
      CRIAR,
      'farm',
      alvo,
      0,
      { nome: `Fazenda\u0000C2 ${sufixo()}`, fuso: FUSO },
      chave,
    );
    const correlacao = `c2-nul-${chave}`;

    const r = await enviar(intencao, correlacao);
    expect(r.status).toBe(400);
    expect(r.correlacao).toBe(correlacao);
    const erro = EsquemaErro.parse(r.corpo);
    expect(erro).toMatchObject({
      codigo: 'CONTRATO_INVALIDO',
      classe: 'validacao',
      correlationId: correlacao,
    });
    expect(erro.campos).toContainEqual({ caminho: 'nome', problema: 'NOME_COM_NUL' });
    expect(erro.detalhe).toBeUndefined();
    expect(falhaPermanenteSemGravacao(erro)).toBe(false);

    expect(desfechoDoEnvio(r.status, r.corpo, intencao, false)).toEqual({
      tipo: 'nao_gravado',
      mensagem: NAO_ACEITO,
      sessao: false,
    });
    expect(await linhas(chave, alvo)).toEqual(NADA);
  });

  it('2. classe 22 pela rota real: 500 FALHA_INTERNA permanente; consumidor corrigir e bloqueio; nada gravado; chave livre', async () => {
    const chave = randomUUID();
    const alvo = randomUUID();
    const dados = { nome: `Fazenda C2 \uD800 ${sufixo()}`, fuso: FUSO };
    // Pré-condição do caminho: o esquema do cadastro aceita o surrogate isolado; a recusa vem do banco, não do 400.
    expect(EsquemaDadosCriarFazenda.safeParse(dados).success).toBe(true);
    const intencao = novaIntencao(CRIAR, 'farm', alvo, 0, dados, chave);
    expect(intencao.corpo).toContain('\\ud800');

    // Primeiro envio.
    const correlacao = `c2-cl22-${chave}`;
    const r = await enviar(intencao, correlacao);
    expect(r.status).toBe(500);
    expect(r.correlacao).toBe(correlacao);
    const erro = EsquemaErro.parse(r.corpo);
    expect(erro.codigo).toBe('FALHA_INTERNA');
    expect(erro.classe).toBe('infraestrutura');
    expect(erro.correlationId).toBe(correlacao);
    expect(erro.detalhe).toEqual({ resultadoIncerto: false, repetirMesmoConteudo: false });
    expect(erro.campos).toBeUndefined();
    expect(falhaPermanenteSemGravacao(erro)).toBe(true);
    expect(JSON.stringify(r.corpo)).not.toMatch(/22P02|surrogate|repita/i);
    // O SQLSTATE fica só no log do envelope: uma linha comando.falhou, nível erro, classe 22, resultado não incerto.
    const falhou = linhasDeLog
      .map((l) => JSON.parse(l) as Record<string, unknown>)
      .filter((l) => l['correlation_id'] === correlacao && l['evento'] === 'comando.falhou');
    expect(falhou).toHaveLength(1);
    expect(falhou[0]).toMatchObject({
      nivel: 'erro',
      erro_codigo: 'FALHA_INTERNA',
      resultado_incerto: false,
    });
    expect(String(falhou[0]?.['codigo_pg'])).toMatch(/^22[0-9A-Z]{3}$/);

    expect(desfechoDoEnvio(r.status, r.corpo, intencao, false)).toEqual({
      tipo: 'corrigir',
      mensagem: erro.mensagem,
      correlacao,
      sessao: false,
    });
    expect(await linhas(chave, alvo)).toEqual(NADA);

    // Consulta: nada registrado, 404 "ainda não localizado". O classificador puro não conhece o bloqueio (fica no gancho).
    const consulta = await consultar(intencao);
    expect(consulta.status).toBe(404);
    expect(EsquemaErro.parse(consulta.corpo).codigo).toBe('RECIBO_NAO_LOCALIZADO');
    expect(desfechoDaConsulta(consulta.status, consulta.corpo, intencao)).toMatchObject({
      tipo: 'incerto',
      naoLocalizado: true,
    });

    // Reenvio do mesmo corpo e da mesma chave: falha igual (repetirMesmoConteudo: false é verdade) e nada é gravado.
    const correlacao2 = `c2-cl22-reenvio-${chave}`;
    const r2 = await enviar(intencao, correlacao2);
    expect(r2.status).toBe(500);
    const erro2 = EsquemaErro.parse(r2.corpo);
    expect(erro2.correlationId).toBe(correlacao2);
    expect(erro2.detalhe).toEqual({ resultadoIncerto: false, repetirMesmoConteudo: false });
    expect(falhaPermanenteSemGravacao(erro2)).toBe(true);
    expect(desfechoDoEnvio(r2.status, r2.corpo, intencao, true)).toEqual({
      tipo: 'incerto',
      mensagem:
        'Este conteúdo não pode ser reenviado. O resultado anterior continua incerto; consulte o recibo.',
      sessao: false,
      naoLocalizado: false,
      bloqueioPermanente: { mensagem: erro2.mensagem, correlacao: correlacao2 },
    });
    expect(await linhas(chave, alvo)).toEqual(NADA);

    // A chave não ficou consumida: a mesma chave e o mesmo alvo com o nome corrigido confirmam uma vez.
    const nomeCorrigido = `Fazenda C2 corrigida ${sufixo()}`;
    const corrigida = novaIntencao(CRIAR, 'farm', alvo, 0, { nome: nomeCorrigido, fuso: FUSO }, chave);
    const r3 = await enviar(corrigida, `c2-cl22-corrigida-${chave}`);
    expect(r3.status).toBe(200);
    const recibo = EsquemaRecibo.parse(r3.corpo);
    expect(recibo).toMatchObject({
      commandType: CRIAR,
      idempotencyKey: chave,
      outcome: 'confirmed',
      targetType: 'farm',
      targetId: alvo,
      expectedVersion: 0,
      resultingVersion: 1,
      alreadyReceived: false,
    });
    expect(desfechoDoEnvio(r3.status, r3.corpo, corrigida, false)).toEqual({ tipo: 'resolvido', recibo });
    expect(await linhas(chave, alvo)).toEqual(UMA);
    expect(await fazenda(alvo)).toEqual([{ name: nomeCorrigido, version: '1' }]);
  });

  it('3. sucesso: recibo; o reenvio do mesmo pedido e a consulta devolvem o mesmo recibo; uma linha', async () => {
    const chave = randomUUID();
    const alvo = randomUUID();
    const nome = `Fazenda C2 recibo ${sufixo()}`;
    const intencao = novaIntencao(CRIAR, 'farm', alvo, 0, { nome, fuso: FUSO }, chave);

    const r1 = await enviar(intencao, `c2-ok-${chave}`);
    expect(r1.status).toBe(statusDoRecibo('confirmed'));
    const recibo = EsquemaRecibo.parse(r1.corpo);
    expect(recibo).toMatchObject({
      commandType: CRIAR,
      idempotencyKey: chave,
      outcome: 'confirmed',
      reasonCode: null,
      targetType: 'farm',
      targetId: alvo,
      expectedVersion: 0,
      resultingVersion: 1,
      alreadyReceived: false,
    });
    expect(recibo.effects['farms']).toEqual([alvo]);
    expect(desfechoDoEnvio(r1.status, r1.corpo, intencao, false)).toEqual({ tipo: 'resolvido', recibo });
    expect(await linhas(chave, alvo)).toEqual(UMA);

    // Reenvio do MESMO corpo (mesma chave): o mesmo recibo, só com alreadyReceived; nenhuma linha nova.
    const r2 = await enviar(intencao, `c2-ok-reenvio-${chave}`);
    expect(r2.status).toBe(200);
    const reenvio = EsquemaRecibo.parse(r2.corpo);
    expect(reenvio).toEqual({ ...recibo, alreadyReceived: true });
    expect(desfechoDoEnvio(r2.status, r2.corpo, intencao, true)).toEqual({
      tipo: 'resolvido',
      recibo: reenvio,
    });

    // Consulta pela chave: o mesmo recibo do reenvio.
    const consulta = await consultar(intencao);
    expect(consulta.status).toBe(200);
    expect(EsquemaRecibo.parse(consulta.corpo)).toEqual(reenvio);
    expect(desfechoDaConsulta(consulta.status, consulta.corpo, intencao)).toEqual({
      tipo: 'resolvido',
      recibo: reenvio,
    });

    expect(await linhas(chave, alvo)).toEqual(UMA);
    expect(await fazenda(alvo)).toEqual([{ name: nome, version: '1' }]);
  });

  it('4. mesma chave com outro conteúdo: 409 IDEMPOTENCY_KEY_REUSED; consumidor nao_gravado; banco inalterado', async () => {
    const chave = randomUUID();
    const alvo = randomUUID();
    const nome = `Fazenda C2 original ${sufixo()}`;
    const original = novaIntencao(CRIAR, 'farm', alvo, 0, { nome, fuso: FUSO }, chave);
    const r1 = await enviar(original, `c2-reuso-${chave}`);
    expect(r1.status).toBe(200);
    const recibo = EsquemaRecibo.parse(r1.corpo);
    const antes = {
      linhas: await linhas(chave, alvo),
      registro: await registroDaIntencao(chave),
      fazenda: await fazenda(alvo),
    };
    expect(antes.linhas).toEqual(UMA);
    expect(antes.registro).toHaveLength(1);
    expect(antes.registro[0]).toMatchObject({ receipt_id: recibo.receiptId, outcome: 'confirmed' });
    expect(antes.fazenda).toEqual([{ name: nome, version: '1' }]);

    const outroNome = `Fazenda C2 outro conteudo ${sufixo()}`;
    const outra = novaIntencao(CRIAR, 'farm', alvo, 0, { nome: outroNome, fuso: FUSO }, chave);
    expect(outra.chave).toBe(original.chave);
    expect(outra.corpo).not.toBe(original.corpo);
    const correlacao = `c2-reuso-outro-${chave}`;
    const r2 = await enviar(outra, correlacao);
    expect(r2.status).toBe(409);
    expect(r2.correlacao).toBe(correlacao);
    const erro = EsquemaErro.parse(r2.corpo);
    expect(erro).toMatchObject({
      codigo: 'IDEMPOTENCY_KEY_REUSED',
      classe: 'conflito',
      correlationId: correlacao,
    });
    expect(erro.detalhe).toEqual({ receiptId: recibo.receiptId });
    expect(falhaPermanenteSemGravacao(erro)).toBe(false);
    expect(desfechoDoEnvio(r2.status, r2.corpo, outra, false)).toEqual({
      tipo: 'nao_gravado',
      mensagem: NAO_ACEITO,
      sessao: false,
    });

    expect(await linhas(chave, alvo)).toEqual(antes.linhas);
    expect(await registroDaIntencao(chave)).toEqual(antes.registro);
    expect(await fazenda(alvo)).toEqual(antes.fazenda);
    const outros = await emOrganizacao(amb.app, demo.organizationId, (c) =>
      c.query<{ n: string }>('SELECT count(*)::text n FROM app.farm WHERE name = $1', [outroNome]),
    );
    expect(outros.rows[0]?.n).toBe('0');
  });
});
