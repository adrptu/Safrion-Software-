import { listarLotes, listarProdutos } from '@safrion/db/web';
import { notFound } from 'next/navigation';

import { podeLer } from '../../../../../autorizacao/matriz';
import { Cabecalho } from '../../../../../componentes/Cabecalho';
import { COLUNAS_LOTE_DO_PRODUTO, linhaDoLote } from '../../../../../estoque/lista';
import { dataCivil } from '../../../../../formato/data';
import { rotuloUnidade } from '../../../../../formato/numero';
import { consultar, exigirSessao } from '../../../../../servidor/pagina';
import { Tabela } from '../../../../../tabela/Tabela';
import { caminhoDeVolta, ESTADO_VAZIO } from '../../../../../tabela/logica';

type Parametros = Promise<{ produto: string }>;
type Busca = Promise<Record<string, string | string[] | undefined>>;

/**
 * Detalhe do produto: unidade-base e os lotes, cada um levando ao detalhe do lote. Sem Próximo passo porque a F0-c não
 * tem comando de cadastro (a edição chega com a F1).
 */
export default async function Produto({
  params,
  searchParams,
}: {
  readonly params: Parametros;
  readonly searchParams: Busca;
}) {
  const { produto: id } = await params;
  const sessao = await exigirSessao(`/cadastros/produtos/${encodeURIComponent(id)}`);
  if (!podeLer(sessao.papel, 'cadastros')) notFound();
  const dados = await consultar(sessao, async (c) => {
    const [produto] = await listarProdutos(c, id);
    if (!produto) return null;
    return { produto, lotes: await listarLotes(c, dataCivil(new Date()), { produto: produto.id }) };
  });
  if (!dados) notFound();
  const { produto, lotes } = dados;
  const volta = caminhoDeVolta('/cadastros/produtos', (await searchParams)['volta']);
  return (
    <>
      <Cabecalho
        trilha={[{ rotulo: 'Cadastros' }, { rotulo: 'Produtos', href: volta }, { rotulo: produto.nome }]}
        voltar={{ href: volta, rotulo: 'Produtos' }}
        titulo={produto.nome}
        contexto={`Unidade-base ${rotuloUnidade(produto.unidade)} · ${String(produto.lotes)} ${produto.lotes === 1 ? 'lote' : 'lotes'}`}
      />
      <div className="conteudo">
        <section className="bloco" aria-labelledby="lotes">
          <h2 id="lotes">Lotes</h2>
          <div className="bloco-corpo">
            <Tabela
              rotulo="Lotes do produto"
              colunas={COLUNAS_LOTE_DO_PRODUTO}
              linhas={lotes.map(linhaDoLote)}
              estadoInicial={ESTADO_VAZIO}
              nome={{ singular: 'lote', plural: 'lotes' }}
              vazio="Nenhum lote deste produto."
            />
          </div>
        </section>
      </div>
    </>
  );
}
