import pg from 'pg';

import {
  definirIdentidadeAmbiente,
  ErroAmbiente,
  lerIdentidadeAmbiente,
  type NomeAmbiente,
} from './ambiente.js';
import { aplicarMigracoes, type ResultadoMigracao } from './migrar.js';
import { provisionarPapeis } from './papeis.js';

/**
 * Preparo do banco de um ambiente (HML da F0-c), com o administrador do servidor, que no Cloud SQL não é superusuário:
 * papéis → banco com dono migrator → migrações → identidade do ambiente. Idempotente: repetir não muda nada. Falha
 * segura: o ambiente é explícito, produção fica fora da F0, banco de outro dono e identidade divergente param antes de
 * qualquer migração. Uma trava consultiva no servidor impede dois preparos ao mesmo tempo.
 */
export type CodigoErroPreparo = 'OPCAO_INVALIDA' | 'AMBIENTE_PROIBIDO' | 'BANCO_DE_OUTRO_DONO';

export class ErroPreparo extends Error {
  override readonly name = 'ErroPreparo';
  constructor(
    readonly codigo: CodigoErroPreparo,
    mensagem: string,
  ) {
    super(mensagem);
  }
}

export interface OpcoesPreparo {
  readonly ambiente: string;
  readonly banco: string;
  readonly senhas: { readonly migrator: string; readonly appRuntime: string };
}

export interface ResultadoPreparo {
  readonly ambiente: NomeAmbiente;
  readonly banco: 'criado' | 'existente';
  readonly migracoes: ResultadoMigracao;
  readonly identidade: 'definida' | 'mantida';
}

const BANCO = /^[a-z][a-z0-9_]{0,62}$/;
const RESERVADOS = new Set(['postgres', 'template0', 'template1', 'cloudsqladmin']);

/** Confere as opções antes de conectar: nada é tocado com opção errada. */
export function validarOpcoes(o: OpcoesPreparo): NomeAmbiente {
  if (o.ambiente === 'prod') {
    throw new ErroPreparo('AMBIENTE_PROIBIDO', 'A F0 não prepara produção; use dev ou hml.');
  }
  if (o.ambiente !== 'dev' && o.ambiente !== 'hml') {
    throw new ErroPreparo('OPCAO_INVALIDA', 'Ambiente tem de ser dev ou hml.');
  }
  if (!BANCO.test(o.banco) || RESERVADOS.has(o.banco)) {
    throw new ErroPreparo(
      'OPCAO_INVALIDA',
      'Nome de banco inválido: minúsculas, dígitos e _, até 63, sem os reservados.',
    );
  }
  for (const senha of [o.senhas.migrator, o.senhas.appRuntime]) {
    if (senha.length < 16 || senha.length > 200) {
      throw new ErroPreparo('OPCAO_INVALIDA', 'Cada senha dos papéis precisa ter de 16 a 200 caracteres.');
    }
  }
  return o.ambiente;
}

interface ParametrosConexao {
  readonly host: string;
  readonly port: number;
  readonly ssl: unknown;
}

function ehParametros(v: unknown): v is ParametrosConexao {
  if (typeof v !== 'object' || v === null) return false;
  const p = v as Record<string, unknown>;
  return typeof p['host'] === 'string' && typeof p['port'] === 'number';
}

/**
 * Conexão do migrator no banco-alvo, com o mesmo servidor, porta e TLS do administrador. Usa os parâmetros que o próprio
 * pg já interpretou da conexão do administrador: vale para host:porta e para o socket do Cloud SQL (?host=/cloudsql/…),
 * sem remontar a URL à mão. Nenhuma senha sai daqui para log.
 */
export function conexaoDoMigrator(admin: pg.Client, banco: string, senha: string): pg.ClientConfig {
  const p: unknown = (admin as unknown as { connectionParameters?: unknown }).connectionParameters;
  if (!ehParametros(p))
    throw new ErroPreparo('OPCAO_INVALIDA', 'Conexão do administrador sem servidor e porta.');
  return {
    host: p.host,
    port: p.port,
    database: banco,
    user: 'migrator',
    password: senha,
    ...(typeof p.ssl === 'boolean' || (typeof p.ssl === 'object' && p.ssl !== null) ? { ssl: p.ssl } : {}),
  };
}

async function identidadeSeExistir(migrator: pg.Client): Promise<NomeAmbiente | null> {
  const r = await migrator.query<{ existe: boolean }>(
    "SELECT to_regclass('app.environment_identity') IS NOT NULL AS existe",
  );
  return r.rows[0]?.existe ? lerIdentidadeAmbiente(migrator) : null;
}

export async function prepararBanco(
  admin: pg.Client,
  opcoes: OpcoesPreparo,
  conectar: (config: pg.ClientConfig) => pg.Client = (config) => new pg.Client(config),
): Promise<ResultadoPreparo> {
  const ambiente = validarOpcoes(opcoes);
  const { banco, senhas } = opcoes;
  await admin.query("SELECT pg_advisory_lock(hashtext('safrion.preparo'))");
  try {
    const dono = await admin.query<{ dono: string }>(
      'SELECT pg_get_userbyid(datdba) AS dono FROM pg_database WHERE datname = $1',
      [banco],
    );
    const existia = (dono.rowCount ?? 0) > 0;
    if (existia && dono.rows[0]?.dono !== 'migrator') {
      throw new ErroPreparo('BANCO_DE_OUTRO_DONO', 'O banco existe com outro dono; nada foi alterado.');
    }
    await provisionarPapeis(admin, senhas);
    if (!existia) {
      // Sem superusuário (Cloud SQL), criar com dono migrator exige poder assumir o papel; herança continua desligada.
      await admin.query('GRANT migrator TO CURRENT_USER WITH INHERIT FALSE, SET TRUE');
      await admin.query(`CREATE DATABASE ${admin.escapeIdentifier(banco)} OWNER migrator`);
    }
    const migrator = conectar(conexaoDoMigrator(admin, banco, senhas.migrator));
    await migrator.connect();
    try {
      const antes = await identidadeSeExistir(migrator);
      if (antes !== null && antes !== ambiente) {
        throw new ErroAmbiente(
          'IDENTIDADE_DIVERGENTE',
          `Este banco é "${antes}", não "${ambiente}"; nenhuma migração foi aplicada.`,
        );
      }
      const migracoes = await aplicarMigracoes(migrator);
      await definirIdentidadeAmbiente(migrator, ambiente);
      return {
        ambiente,
        banco: existia ? 'existente' : 'criado',
        migracoes,
        identidade: antes === null ? 'definida' : 'mantida',
      };
    } finally {
      // Fechar ou destravar nunca substitui a causa de uma falha (HML-A1-02); a trava cai sozinha com a sessão.
      await migrator.end().catch(() => undefined);
    }
  } finally {
    await admin.query("SELECT pg_advisory_unlock(hashtext('safrion.preparo'))").catch(() => undefined);
  }
}
