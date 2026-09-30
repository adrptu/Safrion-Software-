import { documento } from '@safrion/db/web';
import Link from 'next/link';
import { notFound } from 'next/navigation';

import { podeExecutar, podeLer } from '../../../../../autorizacao/matriz';
import { Cabecalho } from '../../../../../componentes/Cabecalho';
import { formatarData, formatarInstante } from '../../../../../formato/data';
import {
  COLUNAS_LINHA_DO_DOCUMENTO,
  estadoDoDocumento,
  formatarIdentificacao,
  linhaDaLinhaDoDocumento,
  pendenciasDoDocumento,
  rotuloDoDocumento,
} from '../../../../../recebimento/lista';
import { consultar, exigirSessao } from '../../../../../servidor/pagina';
import { Tabela } from '../../../../../tabela/Tabela';
import { caminhoDeVolta, ESTADO_VAZIO } from '../../../../../tabela/logica';

type Parametros = Promise<{ documento: string }>;
type Busca = Promise<Record<string, string | string[] | undefined>>;

/**
 * Detalhe do documento recebido (contrato CMD-15 §7.1): estado, a próxima ação do recibo, pendências com quem resolve e
 * o prazo, as linhas conferidas (cada uma abre o lote e o extrato) e a origem. De outra organização ou inexistente é
 * 404, sem dizer qual dos dois.
 */
export default async function Documento({
  params,
  searchParams,
}: {
  readonly params: Parametros;
  readonly searchParams: Busca;
}) {
  const { documento: id } = await params;
  const sessao = await exigirSessao(`/estoque/recebimentos/${encodeURIComponent(id)}`);
  if (!podeLer(sessao.papel, 'estoque')) notFound();
  const d = await consultar(sessao, (c) => documento(c, id));
  if (!d) notFound();
  const volta = caminhoDeVolta('/estoque/recebimentos', (await searchParams)['volta']);
  const nome = rotuloDoDocumento(d);
  const pendencias = pendenciasDoDocumento(d);
  const recebe = podeExecutar(sessao.papel, 'estoque.receber-documento');
  const proxima = d.recibo?.nextAction ?? null;
  const verPendencias =
    pendencias.length > 0 && (proxima === 'Ver inspeção pendente' || proxima === 'Ver divergência');

  return (
    <>
      <Cabecalho
        trilha={[{ rotulo: 'Recebimentos', href: volta }, { rotulo: nome }]}
        voltar={{ href: volta, rotulo: 'Recebimentos' }}
        titulo={nome}
        estado={estadoDoDocumento(d)}
        contexto={`${d.emitente.nome} · recebido em ${formatarData(d.recebimento)} · ${d.fazenda.nome}`}
      />
      <div className="conteudo">
        <section className="bloco proximo-passo" aria-labelledby="proximo-passo">
          <h2 id="proximo-passo">Próximo passo</h2>
          <div className="bloco-corpo">
            {verPendencias ? (
              <>
                <p>
                  {pendencias.length === 1 ? '1 pendência' : `${String(pendencias.length)} pendências`}{' '}
                  aguardando quem resolve.
                </p>
                <a className="botao botao-primario" href="#pendencias">
                  {proxima}
                </a>
              </>
            ) : recebe ? (
              <>
                <p>Documento conferido, sem pendência.</p>
                <Link className="botao botao-primario" href="/estoque/recebimentos/novo">
                  Receber documento
                </Link>
              </>
            ) : (
              <p>Somente consulta. Quem recebe documento é o almoxarife.</p>
            )}
          </div>
        </section>
        {pendencias.length > 0 ? (
          <section className="bloco" id="pendencias" aria-labelledby="pendencias-titulo" tabIndex={-1}>
            <h2 id="pendencias-titulo">Pendências</h2>
            <ul className="bloco-corpo pendencias">
              {pendencias.map((p) => (
                <li key={`${p.tipo}-${String(p.linha)}`}>
                  <strong>{p.tipo}</strong> · linha {p.linha}: {p.descricao}
                  <span className="quem">
                    Resolve: {p.responsavel}
                    {p.prazo ? ` · até ${formatarData(p.prazo)}` : ''}
                  </span>
                </li>
              ))}
            </ul>
          </section>
        ) : null}
        <section className="bloco" aria-labelledby="linhas">
          <h2 id="linhas">Linhas</h2>
          <div className="bloco-corpo">
            <Tabela
              rotulo="Linhas do documento"
              colunas={COLUNAS_LINHA_DO_DOCUMENTO}
              linhas={d.linhas.map((l) => linhaDaLinhaDoDocumento(l, d))}
              estadoInicial={ESTADO_VAZIO}
              nome={{ singular: 'linha', plural: 'linhas' }}
              vazio="Nenhuma linha."
            />
          </div>
        </section>
        <section className="bloco" aria-labelledby="origem">
          <h2 id="origem">Origem</h2>
          <div className="bloco-corpo">
            <dl className="dados">
              <div>
                <dt>Emitente</dt>
                <dd>
                  {d.emitente.nome} · {formatarIdentificacao(d.emitente.identificacao)}
                </dd>
              </div>
              <div>
                <dt>Documento</dt>
                <dd>
                  {d.tipo === 'nfe' ? 'NF-e' : 'Outro'} · série {d.serie === '' ? 'sem série' : d.serie} ·
                  número {d.numero}
                </dd>
              </div>
              <div>
                <dt>Emissão</dt>
                <dd>{formatarData(d.emissao)}</dd>
              </div>
              <div>
                <dt>Recebido em</dt>
                <dd>{formatarData(d.recebimento)}</dd>
              </div>
              {d.pedido ? (
                <div>
                  <dt>Pedido</dt>
                  <dd>
                    {d.pedido.referencia}
                    {d.pedido.sistema ? ` · ${d.pedido.sistema}` : ''}
                  </dd>
                </div>
              ) : null}
              <div>
                <dt>Registrado</dt>
                <dd>
                  {d.autor.nome ?? 'Integração'} · {formatarInstante(d.registradoEm)}
                </dd>
              </div>
            </dl>
          </div>
        </section>
      </div>
    </>
  );
}
