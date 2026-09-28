/**
 * Matriz de autorização da F0-c (ADR 0004 §4): papel → comandos e leituras. Nega por padrão: papel desconhecido, ação
 * fora da lista ou recurso inexistente dão não. A mesma matriz decide a tela (esconder botão é conveniência) e a API
 * (403). O RLS da F0-b é a segunda barreira. Na F1, "receber insumo" (CMD-15) substitui o comando de entrada da F0-c.
 */
export const COMANDOS = ['estoque.registrar-entrada'] as const;
export type Comando = (typeof COMANDOS)[number];

export const LEITURAS = ['estoque', 'cadastros'] as const;
export type Leitura = (typeof LEITURAS)[number];

const MATRIZ: Readonly<
  Record<string, { readonly comandos: readonly Comando[]; readonly leituras: readonly Leitura[] }>
> = {
  almoxarife: { comandos: ['estoque.registrar-entrada'], leituras: ['estoque', 'cadastros'] },
  gerente: { comandos: [], leituras: ['estoque', 'cadastros'] },
};

export function ehComando(valor: string): valor is Comando {
  return (COMANDOS as readonly string[]).includes(valor);
}

export function podeExecutar(papel: string, comando: string): boolean {
  const regras = Object.hasOwn(MATRIZ, papel) ? MATRIZ[papel] : undefined;
  return regras !== undefined && ehComando(comando) && regras.comandos.includes(comando);
}

export function podeLer(papel: string, leitura: string): boolean {
  const regras = Object.hasOwn(MATRIZ, papel) ? MATRIZ[papel] : undefined;
  return regras !== undefined && (regras.leituras as readonly string[]).includes(leitura);
}

const NOMES: ReadonlyMap<string, string> = new Map([
  ['almoxarife', 'Almoxarife'],
  ['gerente', 'Gerente'],
]);

/** Nome do papel para a tela; papel fora da matriz aparece como veio, sem ganhar permissão por isso. */
export function nomeDoPapel(papel: string): string {
  return NOMES.get(papel) ?? papel;
}

/** Papéis que a matriz conhece, para o teste papel × comando. */
export const PAPEIS = Object.keys(MATRIZ);
