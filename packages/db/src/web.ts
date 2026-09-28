/**
 * Superfície do banco para a aplicação web (ADR 0004): sessão e login, comandos, estoque, saúde e contrato de erro.
 * Fica de fora o que é de operação (migração, provisionamento de papéis, demonstração e CLI), que lê arquivos do pacote
 * e não deve entrar no servidor web nem no seu empacotamento.
 */
export { estadoDeSaude, lerIdentidadeAmbiente, type EstadoSaude, type NomeAmbiente } from './ambiente.js';
export {
  listarLocais,
  listarProdutos,
  perfilDaSessao,
  type LocalResumo,
  type Perfil,
  type ProdutoResumo,
} from './cadastros.js';
export { executarComando, type Intencao, type Recibo } from './comando.js';
export { ErroComando, type CodigoErroComando } from './erros.js';
export {
  extratoDoLote,
  listarLotes,
  pedidoDeMovimento,
  registrarMovimento,
  saldoDoLote,
  type LinhaExtrato,
  type LoteResumo,
  type SaldoTexto,
} from './estoque.js';
export { respostaDeErro } from './resposta.js';
export { emOrganizacao, ehUuid } from './sessao.js';
export {
  abrirContinuacao,
  abrirTransacaoLogin,
  concluirContinuacao,
  consumirTransacaoLogin,
  resolverSessao,
  revogarSessao,
  trocarPapel,
  vinculosDaContinuacao,
  type ResultadoConclusao,
  type ResultadoTroca,
  type SessaoResolvida,
  type VinculoDisponivel,
} from './sessao-web.js';
