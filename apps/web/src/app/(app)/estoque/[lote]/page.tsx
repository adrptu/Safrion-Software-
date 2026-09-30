import { extratoDoLote, listarLocais, listarLotes } from '@safrion/db/web';
import { notFound } from 'next/navigation';

import { podeExecutar, podeLer } from '../../../../autorizacao/matriz';
import { Cabecalho } from '../../../../componentes/Cabecalho';
import { estadoDoLote } from '../../../../estoque/estado';
import {
  COLUNAS_EXTRATO,
  contextoDoLote,
  linhaDoMovimento,
  nomeDoLote,
  unidadesDoLote,
} from '../../../../estoque/lista';
import { RegistrarEntrada } from '../../../../estoque/RegistrarEntrada';
import { dataCivil } from '../../../../formato/data';
import { formatarQuantidade, positivo } from '../../../../formato/numero';
import { consultar, exigirSessao } from '../../../../servidor/pagina';
import { Tabela } from '../../../../tabela/Tabela';
import { caminhoDeVolta, ESTADO_VAZIO } from '../../../../tabela/logica';

type Parametros = Promise<{ lote: string }>;
type Busca = Promise<Record<string, string | string[] | undefined>>;

/**
 * Detalhe do lote (DS-58): o que é e em que estado está, o Próximo passo com a única ação primária, o saldo por situação
 * e o extrato. Lote de outra organização ou inexistente é 404, sem dizer qual dos dois.
 */
export default async function Lote({
  params,
  searchParams,
}: {
  readonly params: Parametros;
  readonly searchParams: Busca;
}) {
  const { lote: id } = await params;
  const sessao = await exigirSessao(`/estoque/${encodeURIComponent(id)}`);
  if (!podeLer(sessao.papel, 'estoque')) notFound();
  const dados = await consultar(sessao, async (c) => {
    const [lote] = await listarLotes(c, dataCivil(new Date()), { lote: id });
    if (!lote) return null;
    return { lote, extrato: await extratoDoLote(c, lote.id), locais: await listarLocais(c) };
  });
  if (!dados) notFound();
  const { lote, extrato, locais } = dados;
  const estado = estadoDoLote(lote.movimentos, lote.saldo);
  const volta = caminhoDeVolta('/estoque', (await searchParams)['volta']);
  const nomesDosLocais = new Map(locais.map((l) => [l.id, l.nome]));
  const registra = podeExecutar(sessao.papel, 'estoque.registrar-entrada');
  const q = (valor: string) => formatarQuantidade(valor, lote.unidade);
  const saldo = [
    { rotulo: 'Utilizável', valor: lote.saldo.utilizavel, sempre: true },
    { rotulo: 'Em inspeção', valor: lote.saldo.quarentena, sempre: false },
    { rotulo: 'Bloqueado', valor: lote.saldo.bloqueado, sempre: false },
    { rotulo: 'Vencido', valor: lote.saldo.vencido, sempre: false },
  ].filter((s) => s.sempre || positivo(s.valor));

  return (
    <>
      <Cabecalho
        trilha={[{ rotulo: 'Estoque', href: volta }, { rotulo: nomeDoLote(lote) }]}
        voltar={{ href: volta, rotulo: 'Estoque' }}
        titulo={lote.granel ? nomeDoLote(lote) : `Lote ${lote.codigo}`}
        estado={estado}
        contexto={contextoDoLote(lote)}
      />
      <div className="conteudo">
        <section
          className="bloco proximo-passo"
          data-tom={registra ? undefined : 'neutro'}
          aria-labelledby="proximo-passo"
        >
          <h2 id="proximo-passo">Próximo passo</h2>
          {registra ? (
            <RegistrarEntrada
              lote={{ id: lote.id, versao: lote.saldo.version }}
              unidades={unidadesDoLote(lote.unidade)}
              unidadePadrao={lote.unidade}
              locais={locais.map((l) => ({ valor: l.id, rotulo: `${l.nome} · ${l.fazenda}` }))}
              destino={`/estoque/${lote.id}`}
              usuarioId={sessao.usuarioId}
              organizacaoId={sessao.organizationId}
            />
          ) : (
            <div className="bloco-corpo">
              <p>Somente consulta. Quem registra entrada é o almoxarife.</p>
            </div>
          )}
        </section>
        <section className="bloco" aria-labelledby="saldo">
          <h2 id="saldo">Saldo</h2>
          <div className="bloco-corpo">
            <dl className="saldo">
              {saldo.map((s) => (
                <div key={s.rotulo}>
                  <dt>{s.rotulo}</dt>
                  <dd>{q(s.valor)}</dd>
                </div>
              ))}
              <div>
                <dt className="total">Físico</dt>
                <dd className="total">{q(lote.saldo.fisico)}</dd>
              </div>
            </dl>
          </div>
        </section>
        <section className="bloco" aria-labelledby="extrato">
          <h2 id="extrato">Extrato</h2>
          <div className="bloco-corpo">
            <Tabela
              rotulo="Movimentos do lote"
              colunas={COLUNAS_EXTRATO}
              linhas={extrato.map((m) => linhaDoMovimento(m, nomesDosLocais))}
              estadoInicial={ESTADO_VAZIO}
              nome={{ singular: 'movimento', plural: 'movimentos' }}
              vazio="Nenhum movimento registrado."
            />
          </div>
        </section>
      </div>
    </>
  );
}
