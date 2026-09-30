import { perfilDaSessao } from '@safrion/db/web';
import type { ReactNode } from 'react';

import { nomeDoPapel, podeLer } from '../../autorizacao/matriz';
import { MenuCadastros } from '../../cadastros/MenuCadastros';
import { BotaoSair } from '../../componentes/BotaoSair';
import { ItemMenu } from '../../componentes/ItemMenu';
import { ambienteAtual, consultar, NOME_DO_AMBIENTE, sessaoAtual } from '../../servidor/pagina';

/**
 * Casca da aplicação (DS-27, DS-28): menu com as áreas que o papel lê, selo do ambiente fora da produção, quem está
 * conectado e Sair. Sem sessão, só repassa: cada página manda ao /entrar com o seu destino.
 */
export default async function Casca({ children }: { readonly children: ReactNode }) {
  const sessao = await sessaoAtual();
  if (!sessao) return children;
  const [perfil, ambiente] = await Promise.all([
    consultar(sessao, (c) => perfilDaSessao(c, sessao.usuarioId)),
    ambienteAtual(),
  ]);
  const selo = ambiente ? NOME_DO_AMBIENTE[ambiente] : null;
  return (
    <div className="casca">
      <a className="pular" href="#conteudo">
        Ir para o conteúdo
      </a>
      <nav className="menu" aria-label="Menu principal">
        <span className="marca">Safrion</span>
        <ul>
          {podeLer(sessao.papel, 'estoque') ? (
            <>
              <li>
                <ItemMenu href="/estoque" rotulo="Estoque" exceto={['/estoque/recebimentos']} />
              </li>
              <li>
                <ItemMenu href="/estoque/recebimentos" rotulo="Recebimentos" />
              </li>
            </>
          ) : null}
          {podeLer(sessao.papel, 'cadastros') ? <MenuCadastros /> : null}
        </ul>
        <div className="menu-pe">
          {selo ? <span className="selo-ambiente">{selo}</span> : null}
          <p className="perfil">
            <span>{perfil?.usuario ?? 'Usuário'}</span>
            <span>
              {nomeDoPapel(sessao.papel)}
              {perfil ? ` · ${perfil.organizacao}` : ''}
            </span>
          </p>
          <BotaoSair />
        </div>
      </nav>
      <main id="conteudo" className="coluna">
        {children}
      </main>
    </div>
  );
}
