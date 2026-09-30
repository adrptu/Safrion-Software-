import {
  EsquemaDadosCriarFazenda,
  EsquemaDadosCriarTalhao,
  lerAreaPtBr,
  normalizarNome,
} from '@safrion/contracts';

function canonicos(tipo: 'fazenda' | 'talhao', campos: Readonly<Record<string, string>>) {
  if (tipo === 'fazenda') {
    const r = EsquemaDadosCriarFazenda.safeParse({ nome: campos['nome'], fuso: campos['fuso'] });
    return r.success ? r.data : null;
  }
  const area = lerAreaPtBr(campos['area'] ?? '');
  if (!area.ok) return null;
  const r = EsquemaDadosCriarTalhao.safeParse({
    nome: campos['nome'],
    fazenda: campos['fazenda'],
    areaDeclaradaHa: area.valor,
  });
  return r.success ? r.data : null;
}

/**
 * Achado P1 do Claude: reaplicar nome não pode desfazer a área/fazenda alterada por outra pessoa.
 * A base é a que o usuário abriu, preservada na intenção; nunca o registro atual após um 409.
 * null indica base/campos não recuperáveis. {} é um formulário sem alteração material, não um comando.
 */
export function alteracoesCadastro(
  tipo: 'fazenda' | 'talhao',
  campos: Readonly<Record<string, string>>,
  iniciais: Readonly<Record<string, string>> | undefined,
): Record<string, string> | null {
  if (!iniciais) return null;
  // A migração preserva texto legado bruto; sua identidade é o nome normalizado.
  // O limite de transporte do formulário não deve tornar a fotografia legada impossível de editar.
  const antes: Record<string, string> | null = canonicos(tipo, {
    ...iniciais,
    nome: normalizarNome(iniciais['nome'] ?? ''),
  });
  const depois = canonicos(tipo, campos);
  if (!antes || !depois) return null;
  return Object.fromEntries(Object.entries(depois).filter(([chave, valor]) => valor !== antes[chave]));
}
