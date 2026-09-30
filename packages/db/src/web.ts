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
// Cadastros agrícolas, incremento 1 (contrato CAD-01 §4 e §6): fazenda e talhão, comandos e leituras.
export {
  alterarSituacaoTalhao,
  criarFazenda,
  criarTalhao,
  editarFazenda,
  editarTalhao,
  listarFazendas,
  listarTalhoes,
  obterFazenda,
  obterTalhao,
  opcoesFazenda,
  type AreaTexto,
  type FazendaDetalhe,
  type FazendaResumo,
  type FiltroTalhoes,
  type OpcaoFazenda,
  type OrigemArea,
  type TalhaoDetalhe,
  type TalhaoResumo,
} from './cadastros-agricolas.js';
export { consultarIntencao, executarComando, type Efeito, type Intencao, type Recibo } from './comando.js';
// Conexão por IP privado na subida do servidor (instrumentation.ts), só com SAFRION_CLOUDSQL_INSTANCIA.
export { criarConectorGoogle } from './conector-google.js';
export {
  ErroConexao,
  LIMITE_CONEXAO_MS,
  prepararConexao,
  type Conector,
  type Conexao,
  type PrepararConexao,
} from './conexao.js';
export { ErroComando, type CodigoErroComando } from './erros.js';
export {
  extratoDoLote,
  listarLotes,
  pedidoDeMovimento,
  registrarMovimento,
  saldoDoLote,
  type LinhaExtrato,
  type LoteResumo,
  type OrigemDocumento,
  type SaldoTexto,
} from './estoque.js';
// Documento de entrada (contrato CMD-15 §6.1 e §6.2): o comando e a leitura.
export {
  COMANDO_RECEBER_DOCUMENTO,
  documento,
  documentoPorOrigem,
  listarDocumentos,
  opcoesDoRecebimento,
  receberDocumento,
  type DocumentoDetalhe,
  type DocumentoResumo,
  type LinhaDoDocumento,
  type OcorrenciaDoDocumento,
  type OpcoesRecebimento,
  type ProdutoDoRecebimento,
  type Referencia,
} from './recebimento.js';
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
// Só o pedido de acesso: concessão e revogação são do administrador (CLI), nunca da aplicação web.
export { registrarPedidoAcesso, type PedidoAcesso } from './vinculo.js';
