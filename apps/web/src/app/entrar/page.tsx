import { redirect } from 'next/navigation';

import { mensagemDeLogin } from '../../entrar/mensagens';
import { caminhoInterno, INICIO } from '../../identidade/caminho';
import { ambienteAtual, NOME_DO_AMBIENTE, sessaoAtual } from '../../servidor/pagina';

type Busca = Promise<Record<string, string | string[] | undefined>>;
const primeiro = (v: string | string[] | undefined) => (typeof v === 'string' ? v : undefined);

/**
 * Entrar (fora do master-detail: é uma porta, não uma entidade). Uma ação: seguir para o provedor de identidade. O
 * motivo da volta vem só por código; o destino só se for caminho interno. Com sessão válida, segue direto.
 */
export default async function Entrar({ searchParams }: { readonly searchParams: Busca }) {
  const busca = await searchParams;
  const destino = caminhoInterno(primeiro(busca['destino'])) ?? INICIO;
  if (await sessaoAtual()) redirect(destino);
  const erro = mensagemDeLogin(primeiro(busca['erro']));
  const ambiente = await ambienteAtual();
  const selo = ambiente ? NOME_DO_AMBIENTE[ambiente] : null;
  return (
    <main className="acesso">
      <div className="acesso-cartao">
        <h1 className="marca">Safrion</h1>
        {selo ? <span className="selo-ambiente">{selo}</span> : null}
        {erro ? (
          <p className="aviso" data-papel="erro" role="alert">
            {erro}
          </p>
        ) : null}
        {/* Âncora comum: /entrar/iniciar é rota de servidor que redireciona ao provedor, não página do app. */}
        <a
          className="botao botao-primario"
          href={`/entrar/iniciar?${new URLSearchParams({ destino }).toString()}`}
        >
          Entrar
        </a>
      </div>
    </main>
  );
}
