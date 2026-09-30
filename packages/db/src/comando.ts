import { randomUUID } from 'node:crypto';

import type { Registrador } from '@safrion/contracts';
import { ErroDominio } from '@safrion/domain';
import pg, { type ClientBase, type Pool, type PoolClient } from 'pg';

import { VERSAO_CANONICA, hashCanonico } from './canonico.js';
import { ConflitoVersao, ErroComando, RejeicaoNegocio } from './erros.js';
import { ehUuid, organizacaoValida } from './sessao.js';

export type TipoIniciador = 'app' | 'web' | 'integracao' | 'ia' | 'job';
export type ResultadoIntencao = 'confirmed' | 'rejected' | 'version_conflict';

/** Uma intenção de alteração (IDEM-02). A organização não vem aqui: vem da sessão validada (ENG-021). */
export interface Intencao {
  readonly commandType: string;
  readonly idempotencyKey: string;
  readonly initiatorKind: TipoIniciador;
  readonly actorId: string;
  readonly transportActorId?: string;
  readonly deviceId?: string;
  readonly target: { readonly type: string; readonly id: string; readonly expectedVersion?: number };
  /** Dados de negócio já em forma canônica: decimais em texto normalizado, datas ISO 8601 (24.1). */
  readonly data: unknown;
  /** Instante informado pelo iniciador: dado, não autoridade; não entra no hash. */
  readonly confirmedAt?: string;
  readonly correlationId: string;
}

export interface EventoEmitido {
  readonly type: string;
  readonly schemaVersion: number;
  readonly entityType: string;
  readonly entityId: string;
  readonly entityVersion: number;
  readonly previousVersion: number | null;
  readonly payload: Readonly<Record<string, unknown>>;
}

export interface ContextoEfeito {
  readonly organizationId: string;
  readonly intencao: Intencao;
  /** Registra um evento na outbox, na mesma transação do efeito (ENG-022); devolve o event_id. */
  emitir(evento: EventoEmitido): string;
}

export interface ResultadoEfeito {
  readonly resultingVersion: number | null;
  readonly effects: Readonly<Record<string, readonly string[]>>;
  readonly pending?: readonly string[];
  readonly nextAction?: string;
  readonly before?: unknown;
  readonly after?: unknown;
  readonly reason?: string;
}

export type Efeito = (cliente: PoolClient, ctx: ContextoEfeito) => Promise<ResultadoEfeito>;

/** Recibo imutável (IDEM-17): igual no original e no reenvio, exceto alreadyReceived. */
export interface Recibo {
  readonly receiptId: string;
  readonly commandType: string;
  readonly idempotencyKey: string;
  readonly outcome: ResultadoIntencao;
  readonly reasonCode: string | null;
  readonly targetType: string;
  readonly targetId: string;
  readonly expectedVersion: number | null;
  readonly resultingVersion: number | null;
  readonly effects: Readonly<Record<string, readonly string[]>>;
  readonly pending: readonly string[];
  readonly nextAction: string | null;
  readonly processedAt: string;
  readonly alreadyReceived: boolean;
}

export interface OpcoesComando {
  /** Espera pela inserção da mesma chave em outra transação (IDEM-15; valor inicial 2 s). */
  readonly esperaChaveMs?: number;
  /** Uma linha por comando, com a correlação (ENG-081); nunca o conteúdo do comando. */
  readonly registrador?: Registrador;
}

interface LinhaIntencao {
  receipt_id: string;
  command_type: string;
  idempotency_key: string;
  payload_hash: string;
  outcome: ResultadoIntencao;
  reason_code: string | null;
  target_type: string;
  target_id: string;
  expected_version: string | null;
  resulting_version: string | null;
  effects: Record<string, string[]>;
  pending: string[];
  next_action: string | null;
  processed_at: Date;
}

const INICIADORES: readonly TipoIniciador[] = ['app', 'web', 'integracao', 'ia', 'job'];

function texto(v: unknown, max: number): v is string {
  return typeof v === 'string' && v.trim() !== '' && v.length <= max;
}

function versao(v: unknown): v is number {
  return typeof v === 'number' && Number.isSafeInteger(v) && v >= 0;
}

/** Recusa de contrato (73.3.4): nada é gravado; é defeito do cliente, não situação do usuário. */
function validarIntencao(i: Intencao): void {
  const bruto: unknown = i;
  if (typeof bruto !== 'object' || bruto === null) {
    throw new ErroComando('CONTRATO_INVALIDO', 'Comando fora do contrato: intenção.', {
      campos: ['intenção'],
    });
  }
  const x = bruto as Record<string, unknown>;
  const alvo = x['target'];
  const falhas: string[] = [];
  if (!texto(x['commandType'], 64)) falhas.push('commandType');
  if (!texto(x['idempotencyKey'], 128)) falhas.push('idempotencyKey');
  if (!INICIADORES.some((k) => k === x['initiatorKind'])) falhas.push('initiatorKind');
  if (!ehUuid(x['actorId'])) falhas.push('actorId');
  if (x['transportActorId'] !== undefined && !ehUuid(x['transportActorId'])) falhas.push('transportActorId');
  if (x['deviceId'] !== undefined && !texto(x['deviceId'], 128)) falhas.push('deviceId');
  if (typeof alvo !== 'object' || alvo === null) falhas.push('target');
  else {
    const t = alvo as Record<string, unknown>;
    if (!texto(t['type'], 64)) falhas.push('target.type');
    if (!ehUuid(t['id'])) falhas.push('target.id');
    if (t['expectedVersion'] !== undefined && !versao(t['expectedVersion']))
      falhas.push('target.expectedVersion');
  }
  const confirmado = x['confirmedAt'];
  if (confirmado !== undefined && (typeof confirmado !== 'string' || Number.isNaN(Date.parse(confirmado))))
    falhas.push('confirmedAt');
  if (!texto(x['correlationId'], 128)) falhas.push('correlationId');
  if (falhas.length > 0) {
    throw new ErroComando('CONTRATO_INVALIDO', `Comando fora do contrato: ${falhas.join(', ')}.`, {
      campos: falhas,
    });
  }
}

function inteiro(v: string | null): number | null {
  return v === null ? null : Number(v);
}

function recibo(r: LinhaIntencao, alreadyReceived: boolean): Recibo {
  return {
    receiptId: r.receipt_id,
    commandType: r.command_type,
    idempotencyKey: r.idempotency_key,
    outcome: r.outcome,
    reasonCode: r.reason_code,
    targetType: r.target_type,
    targetId: r.target_id,
    expectedVersion: inteiro(r.expected_version),
    resultingVersion: inteiro(r.resulting_version),
    effects: r.effects,
    pending: r.pending,
    nextAction: r.next_action,
    processedAt: r.processed_at.toISOString(),
    alreadyReceived,
  };
}

function codigoPg(erro: unknown): string | undefined {
  return typeof erro === 'object' && erro !== null && 'code' in erro && typeof erro.code === 'string'
    ? erro.code
    : undefined;
}

const COLUNAS_RECIBO = `receipt_id, command_type, idempotency_key, payload_hash, outcome, reason_code, target_type,
  target_id, expected_version, resulting_version, effects, pending, next_action, processed_at`;

/**
 * Executa um comando com a proteção contra efeito repetido de 73.3 (IDEM-12 a IDEM-17; ENG-021, ENG-022):
 * - chave nova: registra a intenção e aplica o efeito, o recibo, a auditoria e a outbox na mesma transação;
 * - rejeição de negócio ou conflito de versão: desfaz o efeito (savepoint) e registra o resultado com a chave, sem
 *   efeito; o reenvio devolve o mesmo resultado;
 * - mesma chave e mesmo conteúdo: devolve o recibo registrado, marcado como já recebido, sem reavaliar;
 * - mesma chave com outro conteúdo: IDEMPOTENCY_KEY_REUSED, nada gravado;
 * - mesma chave em transação em curso por mais que o limite: IDEMPOTENCY_IN_PROGRESS;
 * - deadlock (40P01) com o ROLLBACK confirmado antes de qualquer COMMIT: a transação inteira repete com a mesma
 *   intenção, até 3 tentativas e pausas de 50 e 150 ms, numa janela de repetição de 2 s desde o início (contrato
 *   CMD-15 §6, v3.9). A janela limita a repetição, não a duração de qualquer comando: a primeira tentativa não tem
 *   prazo novo, e a resposta ainda depende do ROLLBACK e do transporte;
 * - qualquer outra falha: FALHA_TRANSITORIA; repetir com a mesma chave e o mesmo conteúdo. Com o ROLLBACK confirmado
 *   antes do COMMIT, nada foi gravado; se a falha chega no COMMIT ou depois dele (conexão perdida), ou se o ROLLBACK
 *   não se confirma, o resultado é incerto (resultadoIncerto) e o reenvio devolve o recibo, se a transação confirmou.
 */
export async function executarComando(
  pool: Pool,
  organizationId: string,
  intencao: Intencao,
  efeito: Efeito,
  opcoes: OpcoesComando = {},
): Promise<Recibo> {
  const inicio = performance.now();
  const contagem = { tentativas: 0 };
  // A intenção pode chegar fora do contrato: os campos do log são lidos sem confiar no formato.
  const objeto = (v: unknown): Record<string, unknown> =>
    typeof v === 'object' && v !== null ? (v as Record<string, unknown>) : {};
  const bruto = objeto(intencao);
  const alvo = objeto(bruto['target']);
  // Só entra no log o que tem formato de identificador; texto livre do cliente fica de fora (F0B2-01).
  const se = (v: unknown, formato: RegExp) => (typeof v === 'string' && formato.test(v) ? v : undefined);
  const IDENTIFICADOR = /^[A-Za-z0-9._:-]{1,128}$/;
  const correlacao = se(bruto['correlationId'], IDENTIFICADOR) ?? 'sem-correlacao';
  const campos = () => ({
    organization_id: ehUuid(organizationId) ? organizationId : undefined,
    command_type: se(bruto['commandType'], /^[A-Za-z0-9._-]{1,64}$/),
    idempotency_key: se(bruto['idempotencyKey'], IDENTIFICADOR),
    target_type: se(alvo['type'], /^[A-Za-z0-9._-]{1,64}$/),
    target_id: ehUuid(alvo['id']) ? alvo['id'] : undefined,
    duracao_ms: Math.round(performance.now() - inicio),
    tentativas: contagem.tentativas > 0 ? contagem.tentativas : undefined,
  });
  // O registro nunca muda o resultado: falha do log depois de um COMMIT não pode virar erro para quem enviou.
  const registrar = (...args: Parameters<Registrador['registrar']>) => {
    try {
      opcoes.registrador?.registrar(...args);
    } catch {
      /* o log é acessório ao resultado do comando */
    }
  };
  try {
    const r = await processarComando(pool, organizationId, intencao, efeito, opcoes, contagem);
    registrar('info', 'comando.processado', correlacao, {
      ...campos(),
      outcome: r.outcome,
      reason_code: r.reasonCode,
      receipt_id: r.receiptId,
      already_received: r.alreadyReceived,
    });
    return r;
  } catch (erro) {
    // Diagnóstico só por códigos seguros e pela correlação; nenhuma mensagem, causa ou stack de infraestrutura vai ao
    // log (F0B2-01). O erro original sobe intacto para quem chamou.
    const codigo = erro instanceof ErroComando ? erro.codigo : 'NAO_CLASSIFICADO';
    const incerto = erro instanceof ErroComando ? erro.detalhe['resultadoIncerto'] : undefined;
    const sqlstate = erro instanceof ErroComando ? erro.detalhe['codigoPg'] : codigoPg(erro);
    registrar(
      codigo === 'FALHA_TRANSITORIA' || codigo === 'NAO_CLASSIFICADO' ? 'erro' : 'aviso',
      'comando.falhou',
      correlacao,
      {
        ...campos(),
        erro_codigo: codigo,
        erro_tipo: erro instanceof Error ? se(erro.name, /^[A-Za-z]{1,64}$/) : typeof erro,
        resultado_incerto: typeof incerto === 'boolean' ? incerto : undefined,
        codigo_pg: se(sqlstate, /^[0-9A-Z]{5}$/),
      },
    );
    throw erro;
  }
}

/**
 * Deadlock (40P01): pausas antes da 2ª e da 3ª tentativa e a janela de repetição, contada do início do comando; só as
 * tentativas repetidas ficam sujeitas a ela (contrato CMD-15 §6, v3.9).
 */
const PAUSAS_DEADLOCK_MS: readonly number[] = [50, 150];
const PRAZO_REPETICAO_MS = 2000;

/** Deadlock só pelo erro do próprio PostgreSQL (DatabaseError com SQLSTATE 40P01), nunca por um `code` qualquer. */
function ehDeadlock(erro: unknown): boolean {
  return erro instanceof pg.DatabaseError && erro.code === '40P01';
}

/** Prazo das tentativas repetidas esgotado antes do COMMIT: a tentativa é revertida e o COMMIT não sai. */
class PrazoEsgotado extends Error {
  override readonly name = 'PrazoEsgotado';
}

/**
 * Conexão que cai com o cliente emprestado: o pg aborta a consulta em curso (a falha chega ao envelope por ela) e ainda
 * emite 'error' no cliente; sem ouvinte, isso vira exceção não tratada e derruba o processo. O pool só ouve os ociosos.
 */
const ignorarErroDaConexao = (): void => undefined;

/**
 * O cliente da tentativa repetida: antes de cada comando SQL, confere o prazo (depois dele, nenhum comando começa) e
 * aplica `SET LOCAL statement_timeout` com o tempo que falta, para o servidor cortar o comando no prazo. Um só
 * statement_timeout por tentativa não limitaria a soma de vários comandos (Codex 07:52Z).
 */
function comPrazo(cliente: PoolClient, prazo: number): PoolClient {
  const original = cliente.query.bind(cliente) as (...args: unknown[]) => Promise<unknown>;
  const query = async (...args: unknown[]) => {
    const restante = Math.ceil(prazo - performance.now());
    if (restante <= 0) throw new PrazoEsgotado('prazo das tentativas esgotado');
    await original(`SET LOCAL statement_timeout = ${String(restante)}`);
    return original(...args);
  };
  return new Proxy(cliente, {
    get(alvo, chave) {
      if (chave === 'query') return query;
      const valor: unknown = Reflect.get(alvo, chave);
      return typeof valor === 'function' ? (valor as (...a: unknown[]) => unknown).bind(alvo) : valor;
    },
  });
}

async function processarComando(
  pool: Pool,
  organizationId: string,
  intencao: Intencao,
  efeito: Efeito,
  opcoes: OpcoesComando,
  contagem: { tentativas: number },
): Promise<Recibo> {
  const org = organizacaoValida(organizationId);
  validarIntencao(intencao);
  const espera = opcoes.esperaChaveMs ?? 2000;
  if (!Number.isSafeInteger(espera) || espera < 1) {
    throw new ErroComando(
      'CONTRATO_INVALIDO',
      'A espera pela chave deve ser um inteiro positivo de milissegundos.',
    );
  }
  const i = intencao;
  const hash = hashCanonico({
    organizationId: org,
    commandType: i.commandType,
    actorId: i.actorId,
    target: { type: i.target.type, id: i.target.id, expectedVersion: i.target.expectedVersion },
    data: i.data,
  });
  const prazo = performance.now() + PRAZO_REPETICAO_MS;
  for (let n = 1; ; n += 1) {
    contagem.tentativas = n;
    // A mesma intenção e o mesmo hash em toda tentativa; a primeira segue sem prazo novo, como sempre.
    const r = await tentarComando(pool, org, i, hash, efeito, espera, n === 1 ? null : prazo);
    if ('recibo' in r) return r.recibo;
    const pausa = PAUSAS_DEADLOCK_MS[n - 1];
    if (pausa === undefined || performance.now() + pausa >= prazo) throw r.deadlock;
    await new Promise((fim) => setTimeout(fim, pausa));
  }
}

/**
 * Uma tentativa, numa transação. Devolve o recibo, ou `deadlock` quando o PostgreSQL escolheu esta transação como vítima
 * (SQLSTATE efetivo 40P01) e o ROLLBACK foi confirmado antes de qualquer COMMIT: só assim repetir é seguro. Com `prazo`,
 * nenhum comando SQL passa do tempo restante (statement_timeout) e o COMMIT não é enviado depois dele: não há efeito
 * tardio. Uma sequência de comandos, cada um abaixo do restante, ainda pode passar do relógio antes do COMMIT; aí a
 * tentativa é revertida (limite declarado no contrato).
 */
async function tentarComando(
  pool: Pool,
  org: string,
  i: Intencao,
  hash: string,
  efeito: Efeito,
  espera: number,
  prazo: number | null,
): Promise<{ readonly recibo: Recibo } | { readonly deadlock: ErroComando }> {
  const cliente = await pool.connect();
  cliente.on('error', ignorarErroDaConexao);
  // Tentativa repetida: todo comando SQL (os do envelope e os do efeito) passa pelo prazo; BEGIN, COMMIT e ROLLBACK não.
  const c = prazo === null ? cliente : comPrazo(cliente, prazo);
  let quebrado: Error | undefined;
  let commitEnviado = false;
  try {
    await cliente.query('BEGIN');
    await c.query("SELECT set_config('app.organization_id', $1, true)", [org]);
    await c.query(`SET LOCAL lock_timeout = ${String(espera)}`);
    let inserido;
    try {
      inserido = await c.query(
        `INSERT INTO app.intent_record (organization_id, command_type, idempotency_key, payload_hash, canonical_version,
           initiator_kind, actor_id, transport_actor_id, device_id, target_type, target_id, expected_version, outcome,
           receipt_id, confirmed_at, correlation_id)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, 'processing', $13, $14, $15)
         ON CONFLICT (organization_id, command_type, idempotency_key) DO NOTHING`,
        [
          org,
          i.commandType,
          i.idempotencyKey,
          hash,
          VERSAO_CANONICA,
          i.initiatorKind,
          i.actorId,
          i.transportActorId ?? null,
          i.deviceId ?? null,
          i.target.type,
          i.target.id,
          i.target.expectedVersion ?? null,
          randomUUID(),
          i.confirmedAt ?? null,
          i.correlationId,
        ],
      );
    } catch (erro) {
      if (codigoPg(erro) === '55P03') {
        throw new ErroComando(
          'IDEMPOTENCY_IN_PROGRESS',
          'Esta intenção ainda está em processamento; repita depois.',
          {
            repetirEmMs: espera,
          },
        );
      }
      throw erro;
    }
    await c.query('SET LOCAL lock_timeout TO DEFAULT');

    if (inserido.rowCount === 0) {
      const existente = await c.query<LinhaIntencao>(
        `SELECT ${COLUNAS_RECIBO} FROM app.intent_record
          WHERE organization_id = $1 AND command_type = $2 AND idempotency_key = $3`,
        [org, i.commandType, i.idempotencyKey],
      );
      await cliente.query('COMMIT');
      const r = existente.rows[0];
      if (!r) throw new Error('registro da intenção não encontrado depois do conflito de chave');
      if (r.payload_hash !== hash) {
        throw new ErroComando('IDEMPOTENCY_KEY_REUSED', 'Esta chave já foi usada com outro conteúdo.', {
          receiptId: r.receipt_id,
        });
      }
      return { recibo: recibo(r, true) };
    }

    const eventos: (EventoEmitido & { eventId: string })[] = [];
    const ctx: ContextoEfeito = {
      organizationId: org,
      intencao: i,
      emitir(evento) {
        const eventId = randomUUID();
        eventos.push({ ...evento, eventId });
        return eventId;
      },
    };

    let outcome: ResultadoIntencao = 'confirmed';
    let reasonCode: string | null = null;
    let nextAction: string | null = null;
    let resultado: ResultadoEfeito | null = null;
    let resultingVersion: number | null = null;
    await c.query('SAVEPOINT efeito');
    try {
      resultado = await efeito(c, ctx);
      resultingVersion = resultado.resultingVersion;
      nextAction = resultado.nextAction ?? null;
      const agora = new Date().toISOString();
      for (const e of eventos) {
        await c.query(
          `INSERT INTO app.outbox (event_id, organization_id, type, schema_version, entity_type, entity_id,
             entity_version, previous_version, causation_command_type, causation_id, actor_id, occurred_at, payload)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)`,
          [
            e.eventId,
            org,
            e.type,
            e.schemaVersion,
            e.entityType,
            e.entityId,
            e.entityVersion,
            e.previousVersion,
            i.commandType,
            i.idempotencyKey,
            i.actorId,
            agora,
            JSON.stringify(e.payload),
          ],
        );
      }
    } catch (erro) {
      if (erro instanceof ConflitoVersao) {
        outcome = 'version_conflict';
        reasonCode = 'VERSAO_DESATUALIZADA';
        resultingVersion = erro.versaoAtual;
        nextAction = 'Revisar diferenças';
      } else if (erro instanceof RejeicaoNegocio) {
        outcome = 'rejected';
        reasonCode = erro.motivo;
        nextAction = erro.proximaAcao;
      } else if (erro instanceof ErroDominio) {
        outcome = 'rejected';
        reasonCode = erro.codigo;
      } else {
        throw erro;
      }
      await c.query('ROLLBACK TO SAVEPOINT efeito');
      eventos.length = 0;
      resultado = null;
    }

    const efeitos = resultado?.effects ?? {};
    const eventIds = eventos.map((e) => e.eventId);
    const registrado = await c.query<LinhaIntencao>(
      `UPDATE app.intent_record
          SET outcome = $4, reason_code = $5, resulting_version = $6, effects = $7, pending = $8, next_action = $9,
              processed_at = clock_timestamp()
        WHERE organization_id = $1 AND command_type = $2 AND idempotency_key = $3
        RETURNING ${COLUNAS_RECIBO}`,
      [
        org,
        i.commandType,
        i.idempotencyKey,
        outcome,
        reasonCode,
        resultingVersion,
        JSON.stringify(eventIds.length > 0 ? { ...efeitos, events: eventIds } : efeitos),
        JSON.stringify(resultado?.pending ?? []),
        nextAction,
      ],
    );
    await c.query(
      `INSERT INTO app.audit_log (id, organization_id, actor_id, command_type, idempotency_key, outcome, target_type,
         target_id, before_state, after_state, resulting_version, reason, correlation_id)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)`,
      [
        randomUUID(),
        org,
        i.actorId,
        i.commandType,
        i.idempotencyKey,
        outcome,
        i.target.type,
        i.target.id,
        resultado?.before === undefined ? null : JSON.stringify(resultado.before),
        resultado?.after === undefined ? null : JSON.stringify(resultado.after),
        resultingVersion,
        resultado?.reason ?? reasonCode,
        i.correlationId,
      ],
    );
    if (prazo !== null && performance.now() >= prazo) {
      throw new PrazoEsgotado('prazo das tentativas esgotado antes do COMMIT');
    }
    commitEnviado = true;
    await cliente.query('COMMIT');
    const r = registrado.rows[0];
    if (!r) throw new Error('registro da intenção não atualizado');
    return { recibo: recibo(r, false) };
  } catch (erro) {
    try {
      await cliente.query('ROLLBACK');
    } catch (falhaRollback) {
      quebrado = falhaRollback instanceof Error ? falhaRollback : new Error(String(falhaRollback));
    }
    if (erro instanceof ErroComando) throw erro;
    // "Nada gravado" só com o ROLLBACK confirmado antes de qualquer COMMIT; o resto é incerto e nunca repete aqui.
    const incerto = commitEnviado || quebrado !== undefined;
    const sqlstate = codigoPg(erro);
    const falha = new ErroComando(
      'FALHA_TRANSITORIA',
      incerto
        ? 'A confirmação não voltou e o resultado é incerto; repita com a mesma chave e o mesmo conteúdo: se já foi gravado, volta o recibo registrado.'
        : 'A operação não terminou e nada foi gravado; repita com a mesma chave e o mesmo conteúdo.',
      { resultadoIncerto: incerto, codigoPg: sqlstate },
      { cause: erro },
    );
    if (!incerto && ehDeadlock(erro)) return { deadlock: falha };
    throw falha;
  } finally {
    cliente.off('error', ignorarErroDaConexao);
    cliente.release(quebrado);
  }
}

/**
 * Consulta sem efeito por (commandType, chave) (IDEM-09; contrato CMD-15 §6.1): o recibo da intenção registrada, isto é,
 * com resultado terminal gravado por COMMIT (confirmed, rejected ou version_conflict), visível na organização da sessão
 * (RLS). `processing` nunca aparece: só existe dentro da transação que o insere. null é "recibo ainda não localizado",
 * nunca "não recebido". Com actorId, só a intenção do próprio autor (quem enviou recupera a resposta perdida); null só
 * para leitura interna cujo alvo já se mostrou visível. Tipo, chave ou autor fora do formato: null, sem consultar.
 */
export async function consultarIntencao(
  cliente: ClientBase,
  consulta: {
    readonly commandType: string;
    readonly idempotencyKey: string;
    readonly actorId: string | null;
  },
): Promise<Recibo | null> {
  const { commandType, idempotencyKey, actorId } = consulta;
  if (!texto(commandType, 64) || !texto(idempotencyKey, 128) || (actorId !== null && !ehUuid(actorId)))
    return null;
  const r = await cliente.query<LinhaIntencao>(
    `SELECT ${COLUNAS_RECIBO} FROM app.intent_record
      WHERE command_type = $1 AND idempotency_key = $2 AND ($3::uuid IS NULL OR actor_id = $3)
        AND outcome <> 'processing'`,
    [commandType, idempotencyKey, actorId],
  );
  const linha = r.rows[0];
  return linha ? recibo(linha, true) : null;
}
