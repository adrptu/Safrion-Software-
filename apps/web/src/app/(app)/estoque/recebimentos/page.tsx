import { listarDocumentos } from '@safrion/db/web';
import { notFound } from 'next/navigation';

import { podeExecutar, podeLer } from '../../../../autorizacao/matriz';
import { Cabecalho } from '../../../../componentes/Cabecalho';
import { COLUNAS_DOCUMENTO, linhaDoDocumento } from '../../../../recebimento/lista';
import { consultar, exigirSessao } from '../../../../servidor/pagina';
import { Tabela } from '../../../../tabela/Tabela';
import { estadoDaUrl } from '../../../../tabela/logica';

type Busca = Promise<Record<string, string | string[] | undefined>>;

/**
 * Recebimentos (SU-06; contrato CMD-15 §7.1): localizar o documento e ver o estado. A única ação primária é Receber
 * documento, só para quem recebe; o gerente consulta.
 */
export default async function Recebimentos({ searchParams }: { readonly searchParams: Busca }) {
  const sessao = await exigirSessao('/estoque/recebimentos');
  if (!podeLer(sessao.papel, 'estoque')) notFound();
  const documentos = await consultar(sessao, (c) => listarDocumentos(c));
  const recebe = podeExecutar(sessao.papel, 'estoque.receber-documento');
  return (
    <>
      <Cabecalho
        trilha={[{ rotulo: 'Recebimentos' }]}
        titulo="Recebimentos"
        {...(recebe ? { acao: { href: '/estoque/recebimentos/novo', rotulo: 'Receber documento' } } : {})}
      />
      <div className="conteudo">
        <Tabela
          rotulo="Documentos recebidos"
          colunas={COLUNAS_DOCUMENTO}
          linhas={documentos.map(linhaDoDocumento)}
          estadoInicial={estadoDaUrl(await searchParams, COLUNAS_DOCUMENTO)}
          nome={{ singular: 'documento', plural: 'documentos' }}
          vazio="Nenhum documento recebido."
          naUrl
        />
      </div>
    </>
  );
}
