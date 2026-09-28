import { listarLotes } from '@safrion/db/web';
import { notFound } from 'next/navigation';

import { podeLer } from '../../../autorizacao/matriz';
import { Cabecalho } from '../../../componentes/Cabecalho';
import { COLUNAS_LOTE, linhaDoLote } from '../../../estoque/lista';
import { dataCivil } from '../../../formato/data';
import { consultar, exigirSessao } from '../../../servidor/pagina';
import { Tabela } from '../../../tabela/Tabela';
import { estadoDaUrl } from '../../../tabela/logica';

type Busca = Promise<Record<string, string | string[] | undefined>>;

/** Listagem de lotes (DS-57): localizar e decidir qual abrir. Sem primário de criação: a F0-c não cria lote. */
export default async function Estoque({ searchParams }: { readonly searchParams: Busca }) {
  const sessao = await exigirSessao('/estoque');
  if (!podeLer(sessao.papel, 'estoque')) notFound();
  const lotes = await consultar(sessao, (c) => listarLotes(c, dataCivil(new Date())));
  return (
    <>
      <Cabecalho trilha={[{ rotulo: 'Estoque' }]} titulo="Estoque" />
      <div className="conteudo">
        <Tabela
          rotulo="Lotes"
          colunas={COLUNAS_LOTE}
          linhas={lotes.map(linhaDoLote)}
          estadoInicial={estadoDaUrl(await searchParams, COLUNAS_LOTE)}
          nome={{ singular: 'lote', plural: 'lotes' }}
          vazio="Nenhum lote cadastrado."
          naUrl
        />
      </div>
    </>
  );
}
