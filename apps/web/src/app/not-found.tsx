import Link from 'next/link';

export default function NaoEncontrado() {
  return (
    <main className="acesso">
      <div className="acesso-cartao">
        <h1>Página não encontrada</h1>
        <p>O endereço não existe ou você não tem acesso a ele.</p>
        <Link className="botao botao-primario" href="/estoque">
          Ir para o Estoque
        </Link>
      </div>
    </main>
  );
}
