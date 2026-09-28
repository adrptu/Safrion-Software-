import { rotasEntrar } from '../rotas';

export const GET = (requisicao: Request) => rotasEntrar.iniciar(requisicao);
