import { listarTalhoes, obterFazenda, opcoesFazenda } from '@safrion/db/web';
import { notFound } from 'next/navigation';
import { podeExecutar, podeLer } from '../../../../../autorizacao/matriz';
import { DetalheCadastro } from '../../../../../cadastros/DetalheCadastro';
import { Cabecalho } from '../../../../../componentes/Cabecalho';
import { consultar, exigirSessao } from '../../../../../servidor/pagina';
import { consultaDeRetorno, hrefComRetorno } from '../../../../../cadastros/lista';
export default async function Fazenda({
  params,
  searchParams,
}: {
  readonly params: Promise<{ fazenda: string }>;
  readonly searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { fazenda } = await params;
  const origem = (await searchParams)['volta'];
  const consulta = consultaDeRetorno(new URLSearchParams(typeof origem === 'string' ? origem : ''));
  const volta = `/cadastros/areas${consulta ? `?${consulta}` : ''}`;
  const sessao = await exigirSessao(hrefComRetorno(`/cadastros/fazendas/${fazenda}`, consulta));
  if (!podeLer(sessao.papel, 'cadastros')) notFound();
  const [registro, fazendas, talhoes] = await consultar(sessao, async (c) => {
    const registro = await obterFazenda(c, fazenda);
    const fazendas = await opcoesFazenda(c);
    const talhoes = await listarTalhoes(c, { fazenda });
    return [registro, fazendas, talhoes] as const;
  });
  if (!registro) notFound();
  return (
    <>
      <Cabecalho
        trilha={[
          { rotulo: 'Cadastros' },
          { rotulo: 'Fazendas e talhões', href: volta },
          { rotulo: registro.nome },
        ]}
        titulo={registro.nome}
        estado={{ palavra: 'Ativa', papel: 'sucesso' }}
        voltar={{ href: volta, rotulo: 'Fazendas e talhões' }}
      />
      <div className="conteudo">
        <DetalheCadastro
          tipo="fazenda"
          registro={registro}
          fazendas={fazendas}
          talhoes={talhoes}
          volta={volta}
          podeEditar={podeExecutar(sessao.papel, 'cadastros.editar-fazenda')}
          usuarioId={sessao.usuarioId}
          organizacaoId={sessao.organizationId}
        />
      </div>
    </>
  );
}
