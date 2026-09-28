import type { ClientBase } from 'pg';

import { ehUuid } from './sessao.js';

/**
 * Leituras de cadastro para a aplicação web (F0-c): produtos, locais de estoque e o perfil da sessão. Rodam dentro de
 * emOrganizacao, então o RLS limita tudo à organização da sessão; o que é de outra organização simplesmente não aparece.
 */

export interface ProdutoResumo {
  readonly id: string;
  readonly nome: string;
  readonly unidade: string;
  readonly lotes: number;
}

/** Produtos da organização com a contagem de lotes; com id, só aquele produto (id inválido: lista vazia). */
export async function listarProdutos(cliente: ClientBase, id?: string): Promise<ProdutoResumo[]> {
  if (id !== undefined && !ehUuid(id)) return [];
  const r = await cliente.query<{ id: string; name: string; base_unit: string; lotes: number }>(
    `SELECT p.id, p.name, p.base_unit, count(l.id)::int AS lotes
       FROM app.product p
       LEFT JOIN app.lot l ON l.organization_id = p.organization_id AND l.product_id = p.id
      WHERE ($1::uuid IS NULL OR p.id = $1)
      GROUP BY p.id
      ORDER BY p.name, p.id`,
    [id ?? null],
  );
  return r.rows.map((p) => ({ id: p.id, nome: p.name, unidade: p.base_unit, lotes: p.lotes }));
}

export interface LocalResumo {
  readonly id: string;
  readonly nome: string;
  readonly fazenda: string;
}

export async function listarLocais(cliente: ClientBase): Promise<LocalResumo[]> {
  const r = await cliente.query<{ id: string; name: string; farm_name: string }>(
    `SELECT s.id, s.name, f.name AS farm_name
       FROM app.stock_location s
       JOIN app.farm f ON f.organization_id = s.organization_id AND f.id = s.farm_id
      ORDER BY f.name, s.name, s.id`,
  );
  return r.rows.map((l) => ({ id: l.id, nome: l.name, fazenda: l.farm_name }));
}

export interface Perfil {
  readonly usuario: string;
  readonly organizacao: string;
  readonly ficticia: boolean;
}

/** Nome do usuário e da organização da sessão, para o rodapé do menu. null se o usuário não é visível. */
export async function perfilDaSessao(cliente: ClientBase, usuarioId: string): Promise<Perfil | null> {
  if (!ehUuid(usuarioId)) return null;
  const r = await cliente.query<{ user_name: string; org_name: string; fictitious: boolean }>(
    `SELECT u.name AS user_name, o.name AS org_name, o.fictitious
       FROM app.app_user u JOIN app.organization o ON o.id = u.organization_id
      WHERE u.id = $1`,
    [usuarioId],
  );
  const p = r.rows[0];
  return p ? { usuario: p.user_name, organizacao: p.org_name, ficticia: p.fictitious } : null;
}
