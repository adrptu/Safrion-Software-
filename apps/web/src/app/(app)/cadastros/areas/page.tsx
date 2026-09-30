import { listarFazendas, listarTalhoes } from '@safrion/db/web';
import { notFound } from 'next/navigation';
import { podeExecutar, podeLer } from '../../../../autorizacao/matriz';
import { consultaDeRetorno } from '../../../../cadastros/lista';
import { AreasCadastro } from '../../../../cadastros/AreasCadastro';
import { Cabecalho } from '../../../../componentes/Cabecalho';
import { consultar, exigirSessao } from '../../../../servidor/pagina';

export default async function Areas({
  searchParams,
}: {
  readonly searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const query = new URLSearchParams();
  for (const [chave, valor] of Object.entries(await searchParams)) {
    for (const item of typeof valor === 'string' ? [valor] : (valor ?? [])) query.append(chave, item);
  }
  const consulta = consultaDeRetorno(query);
  const sessao = await exigirSessao(`/cadastros/areas${consulta ? `?${consulta}` : ''}`);
  if (!podeLer(sessao.papel, 'cadastros')) notFound();
  const [fazendas, talhoes] = await consultar(sessao, async (c) => {
    const fazendas = await listarFazendas(c);
    const talhoes = await listarTalhoes(c);
    return [fazendas, talhoes] as const;
  });
  return (
    <>
      <Cabecalho
        trilha={[{ rotulo: 'Cadastros' }, { rotulo: 'Fazendas e talhões' }]}
        titulo="Fazendas e talhões"
      />
      <div className="conteudo">
        <AreasCadastro
          fazendas={fazendas}
          talhoes={talhoes}
          podeEditar={podeExecutar(sessao.papel, 'cadastros.criar-talhao')}
          usuarioId={sessao.usuarioId}
          organizacaoId={sessao.organizationId}
        />
      </div>
    </>
  );
}
