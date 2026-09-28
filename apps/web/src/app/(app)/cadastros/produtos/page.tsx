import { listarProdutos } from '@safrion/db/web';
import { notFound } from 'next/navigation';

import { podeLer } from '../../../../autorizacao/matriz';
import { Cabecalho } from '../../../../componentes/Cabecalho';
import { COLUNAS_PRODUTO, linhaDoProduto } from '../../../../estoque/lista';
import { consultar, exigirSessao } from '../../../../servidor/pagina';
import { Tabela } from '../../../../tabela/Tabela';
import { estadoDaUrl } from '../../../../tabela/logica';

type Busca = Promise<Record<string, string | string[] | undefined>>;

/** Listagem de produtos (DS-57). Sem "Novo produto": o cadastro com comando é da F1. */
export default async function Produtos({ searchParams }: { readonly searchParams: Busca }) {
  const sessao = await exigirSessao('/cadastros/produtos');
  if (!podeLer(sessao.papel, 'cadastros')) notFound();
  const produtos = await consultar(sessao, (c) => listarProdutos(c));
  return (
    <>
      <Cabecalho trilha={[{ rotulo: 'Cadastros' }, { rotulo: 'Produtos' }]} titulo="Produtos" />
      <div className="conteudo">
        <Tabela
          rotulo="Produtos"
          colunas={COLUNAS_PRODUTO}
          linhas={produtos.map(linhaDoProduto)}
          estadoInicial={estadoDaUrl(await searchParams, COLUNAS_PRODUTO)}
          nome={{ singular: 'produto', plural: 'produtos' }}
          vazio="Nenhum produto cadastrado."
          naUrl
        />
      </div>
    </>
  );
}
