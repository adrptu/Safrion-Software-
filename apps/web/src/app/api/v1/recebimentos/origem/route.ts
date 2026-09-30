import { criarRotaOrigem } from '../../../../../rotas/recebimentos';
import { dependencias } from '../../../../../servidor/ambiente';

export const GET = criarRotaOrigem(dependencias);
