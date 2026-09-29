import { EsquemaSaude } from '@safrion/contracts';
import { estadoDeSaude } from '@safrion/db/web';

import type { Dependencias } from '../servidor/ambiente';
import { json } from './resposta';

/** GET /saude (plano R-006, passo 8): versão, commit, ambiente e última migração, sem endereço, usuário nem erro do driver. */
export function criarRotaSaude(deps: () => Pick<Dependencias, 'banco' | 'versao' | 'commit'>) {
  return async function GET(): Promise<Response> {
    const { banco, versao, commit } = deps();
    const estado = EsquemaSaude.parse(await estadoDeSaude(banco, { versao, commit }));
    return json(estado.status === 'indisponivel' ? 503 : 200, estado);
  };
}
