import { criarRotaSaude } from '../../rotas/saude';
import { dependencias } from '../../servidor/ambiente';

export const GET = criarRotaSaude(dependencias);
