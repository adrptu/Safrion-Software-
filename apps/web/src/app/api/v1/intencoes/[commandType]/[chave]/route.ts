import { criarRotaIntencoes } from '../../../../../../rotas/intencoes';
import { dependencias } from '../../../../../../servidor/ambiente';

export const GET = criarRotaIntencoes(dependencias);
