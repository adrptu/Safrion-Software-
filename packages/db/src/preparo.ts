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
 * papéis → banco com dono migrator → migrações → identidade do ambiente. Idempotente: repetir não muda nada.
 *
 * Nada muda antes de tudo ser conferido (HML-PREP-01/02): opções sem rede; dono do banco; identidade do banco
 * existente, lida pelo administrador assumindo o papel migrator só para ler (SET ROLE); e as senhas informadas dos
 * papéis que já existem, que precisam autenticar. O preparo nunca troca senha: rotação é outro procedimento. Se uma
 * conferência não puder ser feita com o acesso disponível, recusa sem alterar nada. Produção fica fora da F0. Uma
 * trava consultiva no servidor impede dois preparos ao mesmo tempo.
 */
export type CodigoErroPreparo =
  | 'OPCAO_INVALIDA'
  | 'AMBIENTE_PROIBIDO'
  | 'BANCO_DE_OUTRO_DONO'
  | 'IDENTIDADE_NAO_VERIFICAVEL'
  | 'CREDENCIAL_DIVERGENTE';

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
  readonly user: string;
  readonly password: unknown;
  readonly ssl: unknown;
}

function ehParametros(v: unknown): v is ParametrosConexao {
  if (typeof v !== 'object' || v === null) return false;
  const p = v as Record<string, unknown>;
  return typeof p['host'] === 'string' && typeof p['port'] === 'number' && typeof p['user'] === 'string';
}

/**
 * Conexão no banco-alvo com o mesmo servidor, porta e TLS do administrador, como outro papel (senha informada) ou
 * como o próprio administrador. Usa os parâmetros que o pg já interpretou da conexão do administrador: vale para
 * host:porta e para o socket do Cloud SQL (?host=/cloudsql/…), sem remontar a URL à mão. Nenhuma senha vai para log.
 */
function conexaoNoBanco(
  admin: pg.Client,
  banco: string,
  credencial?: { readonly usuario: string; readonly senha: string },
): pg.ClientConfig {
  const p: unknown = (admin as unknown as { connectionParameters?: unknown }).connectionParameters;
  if (!ehParametros(p))
    throw new ErroPreparo('OPCAO_INVALIDA', 'Conexão do administrador sem servidor e porta.');
  const senhaAdmin = typeof p.password === 'string' ? p.password : undefined;
  return {
    host: p.host,
    port: p.port,
    database: banco,
    user: credencial?.usuario ?? p.user,
    ...(credencial
      ? { password: credencial.senha }
      : senhaAdmin !== undefined
        ? { password: senhaAdmin }
        : {}),
    ...(typeof p.ssl === 'boolean' || (typeof p.ssl === 'object' && p.ssl !== null) ? { ssl: p.ssl } : {}),
  };
}

/** Conexão do migrator no banco-alvo, com a senha informada. */
export function conexaoDoMigrator(admin: pg.Client, banco: string, senha: string): pg.ClientConfig {
  return conexaoNoBanco(admin, banco, { usuario: 'migrator', senha });
}

const codigoPg = (e: unknown) => (typeof e === 'object' && e !== null && 'code' in e ? e.code : undefined);

type Conectar = (config: pg.ClientConfig) => pg.Client;

/**
 * Identidade do banco existente, lida pelo administrador assumindo o migrator (dono das tabelas) só nesta sessão e só
 * para ler. Sem poder assumir o papel, a conferência não acontece: IDENTIDADE_NAO_VERIFICAVEL, nada alterado.
 */
async function identidadeDoBanco(
  admin: pg.Client,
  banco: string,
  conectar: Conectar,
): Promise<NomeAmbiente | null> {
  const c = conectar(conexaoNoBanco(admin, banco));
  c.on('error', () => undefined);
  await c.connect();
  try {
    try {
      await c.query('SET ROLE migrator');
    } catch (e) {
      if (codigoPg(e) === '42501') {
        throw new ErroPreparo(
          'IDENTIDADE_NAO_VERIFICAVEL',
          'O administrador não pode assumir o papel migrator para ler a identidade do banco; nada foi alterado.',
        );
      }
      throw e;
    }
    // Existência numa consulta à parte (HML-PREP-03): o PostgreSQL resolve toda tabela citada ao analisar a consulta,
    // mesmo num ramo que não roda, e o banco criado por um preparo interrompido antes da primeira migração não a tem.
    const tabela = await c.query<{ existe: boolean }>(
      "SELECT to_regclass('app.environment_identity') IS NOT NULL AS existe",
    );
    return tabela.rows[0]?.existe ? await lerIdentidadeAmbiente(c) : null;
  } finally {
    await c.end().catch(() => undefined);
  }
}

/**
 * A senha informada autentica o papel que já existe com login? Papel inexistente ou sem login não tem senha em uso a
 * conferir. Senha recusada pelo servidor (28P01) recusa o preparo sem alterar nada: provisionar trocaria a senha de
 * quem já usa o papel. Qualquer outra falha também para antes das mudanças, como falha de infraestrutura.
 */
async function conferirCredencial(
  admin: pg.Client,
  papel: 'migrator' | 'app_runtime',
  senha: string,
  banco: string,
  conectar: Conectar,
): Promise<void> {
  const existe = await admin.query('SELECT 1 FROM pg_roles WHERE rolname = $1 AND rolcanlogin', [papel]);
  if (!existe.rowCount) return;
  const c = conectar(conexaoNoBanco(admin, banco, { usuario: papel, senha }));
  c.on('error', () => undefined);
  try {
    await c.connect();
  } catch (e) {
    if (codigoPg(e) === '28P01') {
      throw new ErroPreparo(
        'CREDENCIAL_DIVERGENTE',
        `A senha informada para ${papel} não é a atual; nada foi alterado. Rotação de senha é um procedimento à parte.`,
      );
    }
    throw e;
  } finally {
    await c.end().catch(() => undefined);
  }
}

export async function prepararBanco(
  admin: pg.Client,
  opcoes: OpcoesPreparo,
  conectar: Conectar = (config) => new pg.Client(config),
): Promise<ResultadoPreparo> {
  const ambiente = validarOpcoes(opcoes);
  const { banco, senhas } = opcoes;
  await admin.query("SELECT pg_advisory_lock(hashtext('safrion.preparo'))");
  try {
    // 1. Conferências, sem alterar nada.
    const dono = await admin.query<{ dono: string }>(
      'SELECT pg_get_userbyid(datdba) AS dono FROM pg_database WHERE datname = $1',
      [banco],
    );
    const existia = (dono.rowCount ?? 0) > 0;
    if (existia && dono.rows[0]?.dono !== 'migrator') {
      throw new ErroPreparo('BANCO_DE_OUTRO_DONO', 'O banco existe com outro dono; nada foi alterado.');
    }
    const antes = existia ? await identidadeDoBanco(admin, banco, conectar) : null;
    if (antes !== null && antes !== ambiente) {
      throw new ErroAmbiente(
        'IDENTIDADE_DIVERGENTE',
        `Este banco é "${antes}", não "${ambiente}"; nada foi alterado.`,
      );
    }
    const bancoDaConferencia = existia ? banco : (admin.database ?? 'postgres');
    await conferirCredencial(admin, 'migrator', senhas.migrator, bancoDaConferencia, conectar);
    await conferirCredencial(admin, 'app_runtime', senhas.appRuntime, bancoDaConferencia, conectar);

    // 2. Mudanças: papéis (as senhas já conferidas não mudam), banco, migrações e identidade.
    await provisionarPapeis(admin, senhas);
    if (!existia) {
      // Sem superusuário (Cloud SQL), criar com dono migrator exige poder assumir o papel; herança continua desligada.
      await admin.query('GRANT migrator TO CURRENT_USER WITH INHERIT FALSE, SET TRUE');
      await admin.query(`CREATE DATABASE ${admin.escapeIdentifier(banco)} OWNER migrator`);
    }
    const migrator = conectar(conexaoDoMigrator(admin, banco, senhas.migrator));
    migrator.on('error', () => undefined);
    await migrator.connect();
    try {
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
