import { criarRotaComandos } from '../../../../../rotas/comandos';
import { dependencias } from '../../../../../servidor/ambiente';

export const POST = criarRotaComandos(dependencias);
