import type { EstadoExibido } from '../estoque/estado';

/** Chip de estado (DS-34): palavra da tabela 74.4.3, cor pelo papel e ponto; nunca só a cor. */
export function Selo({ estado }: { readonly estado: EstadoExibido }) {
  return (
    <span className="chip" data-papel={estado.papel}>
      {estado.palavra}
    </span>
  );
}
