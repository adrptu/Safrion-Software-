'use client';

/** Falha ao carregar a tela: a casca e o menu continuam, e a pessoa tenta de novo sem perder o caminho. */
export default function FalhaAoCarregar({ retry }: { readonly retry: () => void }) {
  return (
    <div className="conteudo">
      <p className="aviso" data-papel="erro" role="alert">
        Não foi possível carregar esta tela.{' '}
        <button
          type="button"
          className="link-acao"
          onClick={() => {
            retry();
          }}
        >
          Tentar de novo
        </button>
      </p>
    </div>
  );
}
