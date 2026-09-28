import { rotasEntrar } from '../../rotas';

export const POST = (requisicao: Request) => rotasEntrar.autorizarDesenvolvimento(requisicao);
