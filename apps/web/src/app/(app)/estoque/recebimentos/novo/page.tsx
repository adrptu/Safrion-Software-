import { opcoesDoRecebimento } from '@safrion/db/web';
import { notFound } from 'next/navigation';

import { podeExecutar } from '../../../../../autorizacao/matriz';
import { Cabecalho } from '../../../../../componentes/Cabecalho';
import { dataCivil } from '../../../../../formato/data';
import { ReceberDocumento } from '../../../../../recebimento/ReceberDocumento';
import { consultar, exigirSessao } from '../../../../../servidor/pagina';

/**
 * Receber documento (FO-18; contrato CMD-15 §7.1): só para quem pode executar o comando; para os outros, a tela não
 * existe. As opções vêm do cadastro da organização da sessão.
 */
export default async function Receber() {
  const sessao = await exigirSessao('/estoque/recebimentos/novo');
  if (!podeExecutar(sessao.papel, 'estoque.receber-documento')) notFound();
  const opcoes = await consultar(sessao, (c) => opcoesDoRecebimento(c));
  const semCadastro =
    opcoes.emitentes.length === 0 || opcoes.produtos.length === 0 || opcoes.fazendas.length === 0;
  return (
    <>
      <Cabecalho
        trilha={[{ rotulo: 'Recebimentos', href: '/estoque/recebimentos' }, { rotulo: 'Receber documento' }]}
        voltar={{ href: '/estoque/recebimentos', rotulo: 'Recebimentos' }}
        titulo="Receber documento"
      />
      <div className="conteudo">
        {semCadastro ? (
          <section className="bloco">
            <div className="bloco-corpo">
              <p>Falta cadastro para receber: emitente, produto e fazenda com local.</p>
            </div>
          </section>
        ) : (
          <ReceberDocumento
            opcoes={opcoes}
            hoje={dataCivil(new Date())}
            usuarioId={sessao.usuarioId}
            organizacaoId={sessao.organizationId}
          />
        )}
      </div>
    </>
  );
}
