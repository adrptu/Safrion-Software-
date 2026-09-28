import { criarRotasEntrar } from '../../rotas/entrar';
import { dependencias } from '../../servidor/ambiente';

/** Uma instância das rotas de login para as pastas de /entrar e /sair. O adaptador OIDC do Codex entra aqui. */
export const rotasEntrar = criarRotasEntrar(dependencias);
