import { randomUUID } from 'node:crypto';

import type { ClientBase, Pool } from 'pg';

import { emOrganizacao } from './sessao.js';

export type NomeAmbiente = 'dev' | 'hml' | 'prod';
const NOMES: readonly NomeAmbiente[] = ['dev', 'hml', 'prod'];

export type CodigoErroAmbiente =
  | 'IDENTIDADE_AUSENTE' // banco sem identidade gravada
  | 'IDENTIDADE_DIVERGENTE' // processo e banco dizem ambientes diferentes, ou tentativa de trocar a identidade
  | 'AMBIENTE_PROIBIDO' // demonstração em produção
  | 'CONFIRMACAO_DIVERGENTE'; // o nome confirmado no comando não é o do banco

export class ErroAmbiente extends Error {
  override readonly name = 'ErroAmbiente';
  constructor(
    readonly codigo: CodigoErroAmbiente,
    mensagem: string,
  ) {
    super(mensagem);
  }
}

export function ehNomeAmbiente(v: unknown): v is NomeAmbiente {
  return NOMES.some((n) => n === v);
}

/** Identidade gravada no banco, ou null se o banco ainda não foi identificado. */
export async function lerIdentidadeAmbiente(cliente: ClientBase | Pool): Promise<NomeAmbiente | null> {
  const r = await cliente.query<{ name: string }>('SELECT name FROM app.environment_identity');
  const nome = r.rows[0]?.name;
  return ehNomeAmbiente(nome) ? nome : null;
}

/**
 * Grava a identidade do ambiente no provisionamento, com o papel dono (migrator). Repetir o mesmo nome não faz nada;
 * outro nome é recusado: um banco não troca de identidade, é recriado.
 */
export async function definirIdentidadeAmbiente(migrator: ClientBase, nome: NomeAmbiente): Promise<void> {
  if (!ehNomeAmbiente(nome)) throw new ErroAmbiente('IDENTIDADE_DIVERGENTE', 'Nome de ambiente inválido.');
  await migrator.query(
    'INSERT INTO app.environment_identity (name) VALUES ($1) ON CONFLICT (singleton) DO NOTHING',
    [nome],
  );
  const atual = await lerIdentidadeAmbiente(migrator);
  if (atual !== nome) {
    throw new ErroAmbiente(
      'IDENTIDADE_DIVERGENTE',
      `Este banco já é "${String(atual)}"; não vira "${nome}". Recrie o banco para outro ambiente.`,
    );
  }
}

export interface EstadoSaude {
  readonly status: 'ok' | 'sem_identidade' | 'indisponivel';
  readonly ambiente: NomeAmbiente | null;
  readonly versao: string;
  readonly commit: string;
  readonly migracao: string | null;
  readonly verificadoEm: string;
}

/**
 * Estado para /saude (plano R-006, passo 8): versão, commit, ambiente e última migração. Nunca devolve endereço do banco,
 * usuário ou mensagem de erro do driver; banco fora do ar vira status "indisponivel", sem exceção.
 */
export async function estadoDeSaude(
  pool: Pool,
  info: { readonly versao: string; readonly commit: string },
  agora: () => Date = () => new Date(),
): Promise<EstadoSaude> {
  const base = { versao: info.versao, commit: info.commit };
  try {
    const ambiente = await lerIdentidadeAmbiente(pool);
    const m = await pool.query<{ versao: string }>(
      'SELECT versao FROM migracao.registro ORDER BY versao DESC LIMIT 1',
    );
    return {
      ...base,
      status: ambiente ? 'ok' : 'sem_identidade',
      ambiente,
      migracao: m.rows[0]?.versao ?? null,
      verificadoEm: agora().toISOString(),
    };
  } catch {
    return {
      ...base,
      status: 'indisponivel',
      ambiente: null,
      migracao: null,
      verificadoEm: agora().toISOString(),
    };
  }
}

export interface Demonstracao {
  readonly ambiente: 'dev' | 'hml';
  readonly organizationId: string;
  readonly geracao: number;
  /** Usuários fictícios e o subject de desenvolvimento vinculado a cada um (issuer urn:safrion:desenvolvimento). */
  readonly usuarios: readonly {
    readonly papel: string;
    readonly usuarioId: string;
    readonly subject: string;
  }[];
  readonly loteId: string;
}

/**
 * Restaura a demonstração (PRD 23.4): só com o banco identificado como dev ou hml, o processo dizendo o mesmo ambiente e
 * o nome repetido no comando. Cria uma geração nova de organização fictícia e aponta a demonstração para ela; nada é
 * apagado, porque movimento e auditoria são imutáveis. Nunca toca em organização existente.
 */
export async function restaurarDemonstracao(
  pool: Pool,
  opcoes: { readonly confirmar: string; readonly ambienteDoProcesso: string | undefined },
): Promise<Demonstracao> {
  const identidade = await lerIdentidadeAmbiente(pool);
  if (identidade === null) {
    throw new ErroAmbiente('IDENTIDADE_AUSENTE', 'O banco não tem identidade de ambiente; nada foi feito.');
  }
  if (identidade === 'prod') {
    throw new ErroAmbiente('AMBIENTE_PROIBIDO', 'Demonstração não roda em produção; nada foi feito.');
  }
  if (opcoes.ambienteDoProcesso !== identidade) {
    // O valor da variável só é repetido se for um nome de ambiente; texto livre do processo não sai na mensagem.
    const doProcesso = ehNomeAmbiente(opcoes.ambienteDoProcesso)
      ? `"${opcoes.ambienteDoProcesso}"`
      : 'outro valor (nem dev, nem hml, nem prod)';
    throw new ErroAmbiente(
      'IDENTIDADE_DIVERGENTE',
      `O processo diz ${doProcesso} e o banco é "${identidade}"; nada foi feito.`,
    );
  }
  if (opcoes.confirmar !== identidade) {
    throw new ErroAmbiente(
      'CONFIRMACAO_DIVERGENTE',
      `Confirme com o nome do ambiente deste banco ("${identidade}"); nada foi feito.`,
    );
  }
  const ambiente = identidade;
  const org = randomUUID();
  const almoxarife = randomUUID();
  const gerente = randomUUID();
  const fazenda = randomUUID();
  const local = randomUUID();
  const produto = randomUUID();
  const lote = randomUUID();
  const geracao = await emOrganizacao(pool, org, async (c) => {
    const g = await c.query<{ generation: number }>(
      `INSERT INTO app.demo_state (current_organization, generation) VALUES ($1, 1)
       ON CONFLICT (singleton) DO UPDATE
         SET current_organization = EXCLUDED.current_organization, generation = app.demo_state.generation + 1,
             generated_at = clock_timestamp()
       RETURNING generation`,
      [org],
    );
    const n = g.rows[0]?.generation ?? 1;
    await c.query('INSERT INTO app.organization (id, name, fictitious) VALUES ($1, $2, true)', [
      org,
      `Demonstração · geração ${String(n)}`,
    ]);
    for (const [id, nome, email, papel] of [
      [almoxarife, 'Almoxarife (fictício)', 'almoxarife@demonstracao.invalid', 'almoxarife'],
      [gerente, 'Gerente (fictício)', 'gerente@demonstracao.invalid', 'gerente'],
    ] as const) {
      await c.query('INSERT INTO app.app_user (id, organization_id, name, email) VALUES ($1, $2, $3, $4)', [
        id,
        org,
        nome,
        email,
      ]);
      await c.query('INSERT INTO app.user_role (organization_id, user_id, role_code) VALUES ($1, $2, $3)', [
        org,
        id,
        papel,
      ]);
      // Login de DEV: a identidade fictícia passa a apontar só para esta geração (migração 0004).
      await c.query('SELECT app.vincular_demonstracao($1, $2, $3)', [org, id, `demo-${papel}`]);
    }
    await c.query(
      "INSERT INTO app.farm (id, organization_id, name) VALUES ($1, $2, 'Fazenda Demonstração')",
      [fazenda, org],
    );
    await c.query(
      "INSERT INTO app.stock_location (id, organization_id, farm_id, name) VALUES ($1, $2, $3, 'Almoxarifado central')",
      [local, org, fazenda],
    );
    await c.query(
      "INSERT INTO app.product (id, organization_id, name, base_unit) VALUES ($1, $2, 'Herbicida fictício', 'L')",
      [produto, org],
    );
    await c.query(
      `INSERT INTO app.lot (id, organization_id, product_id, code, expiry_date, base_unit)
       VALUES ($1, $2, $3, 'DEMO-001', '2027-06-30', 'L')`,
      [lote, org, produto],
    );
    // Em hml, acesso real concedido a gerações anteriores cai aqui, com evento e sessões revogadas, na mesma transação;
    // nada passa para a geração nova sem concessão explícita (ADR 0004 §11). Em dev, a função não faz nada.
    await c.query('SELECT app.revogar_vinculos_demonstracao($1)', [org]);
    return n;
  });
  return {
    ambiente,
    organizationId: org,
    geracao,
    usuarios: [
      { papel: 'almoxarife', usuarioId: almoxarife, subject: 'demo-almoxarife' },
      { papel: 'gerente', usuarioId: gerente, subject: 'demo-gerente' },
    ],
    loteId: lote,
  };
}
