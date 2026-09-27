import { randomUUID } from 'node:crypto';

import { ErroDominio } from '@safrion/domain';
import type { Pool, PoolClient } from 'pg';

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
 * - qualquer outra falha: FALHA_TRANSITORIA, nada gravado; repetir com a mesma chave e o mesmo conteúdo.
 */
export async function executarComando(
  pool: Pool,
  organizationId: string,
  intencao: Intencao,
  efeito: Efeito,
  opcoes: OpcoesComando = {},
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

  const cliente = await pool.connect();
  let quebrado: Error | undefined;
  try {
    await cliente.query('BEGIN');
    await cliente.query("SELECT set_config('app.organization_id', $1, true)", [org]);
    await cliente.query(`SET LOCAL lock_timeout = ${String(espera)}`);
    let inserido;
    try {
      inserido = await cliente.query(
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
    await cliente.query('SET LOCAL lock_timeout TO DEFAULT');

    if (inserido.rowCount === 0) {
      const existente = await cliente.query<LinhaIntencao>(
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
      return recibo(r, true);
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
    await cliente.query('SAVEPOINT efeito');
    try {
      resultado = await efeito(cliente, ctx);
      resultingVersion = resultado.resultingVersion;
      nextAction = resultado.nextAction ?? null;
      const agora = new Date().toISOString();
      for (const e of eventos) {
        await cliente.query(
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
      await cliente.query('ROLLBACK TO SAVEPOINT efeito');
      eventos.length = 0;
      resultado = null;
    }

    const efeitos = resultado?.effects ?? {};
    const eventIds = eventos.map((e) => e.eventId);
    const registrado = await cliente.query<LinhaIntencao>(
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
    await cliente.query(
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
    await cliente.query('COMMIT');
    const r = registrado.rows[0];
    if (!r) throw new Error('registro da intenção não atualizado');
    return recibo(r, false);
  } catch (erro) {
    try {
      await cliente.query('ROLLBACK');
    } catch (falhaRollback) {
      quebrado = falhaRollback instanceof Error ? falhaRollback : new Error(String(falhaRollback));
    }
    if (erro instanceof ErroComando) throw erro;
    throw new ErroComando(
      'FALHA_TRANSITORIA',
      'A operação não terminou e nada foi gravado; repita com a mesma chave e o mesmo conteúdo.',
      { causa: erro instanceof Error ? erro.message : String(erro), codigoPg: codigoPg(erro) },
    );
  } finally {
    cliente.release(quebrado);
  }
}
