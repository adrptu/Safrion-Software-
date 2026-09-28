import { criarRotasEntrar } from '../../rotas/entrar';
import { dependencias } from '../../servidor/ambiente';
import { criarFabricaOidc } from '../../servidor/oidc';

/**
 * Uma instância das rotas de login para as pastas de /entrar e /sair, com o adaptador OIDC do Codex configurado pelo
 * ambiente (SAFRION_OIDC_ISSUER, SAFRION_OIDC_CLIENT_ID e SAFRION_OIDC_CLIENT_SECRET) e descoberto uma vez por processo.
 */
export const rotasEntrar = criarRotasEntrar(dependencias, criarFabricaOidc());
