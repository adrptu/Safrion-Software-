import { obterTalhao, opcoesFazenda } from '@safrion/db/web';
import { notFound } from 'next/navigation';
import { podeExecutar, podeLer } from '../../../../../autorizacao/matriz';
import { DetalheCadastro } from '../../../../../cadastros/DetalheCadastro';
import { Cabecalho } from '../../../../../componentes/Cabecalho';
import { consultar, exigirSessao } from '../../../../../servidor/pagina';
import { consultaDeRetorno, hrefComRetorno } from '../../../../../cadastros/lista';
export default async function Talhao({
  params,
  searchParams,
}: {
  readonly params: Promise<{ talhao: string }>;
  readonly searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { talhao } = await params;
  const origem = (await searchParams)['volta'];
  const consulta = consultaDeRetorno(new URLSearchParams(typeof origem === 'string' ? origem : ''));
  const volta = `/cadastros/areas${consulta ? `?${consulta}` : ''}`;
  const sessao = await exigirSessao(hrefComRetorno(`/cadastros/areas/${talhao}`, consulta));
  if (!podeLer(sessao.papel, 'cadastros')) notFound();
  const [registro, fazendas] = await consultar(sessao, async (c) => {
    const registro = await obterTalhao(c, talhao);
    const fazendas = await opcoesFazenda(c);
    return [registro, fazendas] as const;
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
        estado={{
          palavra: registro.situacao === 'ativo' ? 'Ativo' : 'Inativo',
          papel: registro.situacao === 'ativo' ? 'sucesso' : 'neutro',
        }}
        contexto={registro.fazenda.nome}
        voltar={{ href: volta, rotulo: 'Fazendas e talhões' }}
      />
      <div className="conteudo">
        <DetalheCadastro
          tipo="talhao"
          registro={registro}
          fazendas={fazendas}
          volta={volta}
          podeEditar={podeExecutar(sessao.papel, 'cadastros.editar-talhao')}
          usuarioId={sessao.usuarioId}
          organizacaoId={sessao.organizationId}
        />
      </div>
    </>
  );
}
