/**
 * Números e quantidades em pt-BR (4.2; DS-05), sem ponto flutuante: o valor chega como decimal canônico em texto
 * ("1234.500000") e sai com milhar em ponto, decimal em vírgula e sem zeros à direita ("1.234,5").
 */
const DECIMAL = /^(-?)(\d+)(?:\.(\d+))?$/;

/** Sinal, parte inteira e fração (ausente quando não há ponto) do decimal canônico; null fora do formato. */
function partes(texto: string): [sinal: string, inteiro: string, fracao: string | undefined] | null {
  const m = DECIMAL.exec(texto);
  return m ? (m.slice(1) as [string, string, string | undefined]) : null;
}

export function formatarDecimal(texto: string): string {
  const p = partes(texto);
  if (!p) throw new Error('Decimal fora do formato canônico.');
  const inteiro = p[1].replace(/^0+(?=\d)/, '');
  const fracao = (p[2] ?? '').replace(/0+$/, '');
  const negativo = p[0] === '-' && (/[1-9]/.test(inteiro) || fracao !== '');
  const agrupado = inteiro.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return `${negativo ? '-' : ''}${agrupado}${fracao === '' ? '' : `,${fracao}`}`;
}

/** Rótulo de exibição da unidade; o código continua sendo o do contrato. */
const ROTULO_UNIDADE: ReadonlyMap<string, string> = new Map([
  ['m3', 'm³'],
  ['sc60', 'sc 60 kg'],
]);

export function rotuloUnidade(codigo: string): string {
  return ROTULO_UNIDADE.get(codigo) ?? codigo;
}

export function formatarQuantidade(texto: string, unidade: string): string {
  return `${formatarDecimal(texto)} ${rotuloUnidade(unidade)}`;
}

/** Maior que zero, lido do texto: nenhum dígito diferente de zero é zero, e o sinal de menos é negativo. */
export function positivo(texto: string): boolean {
  return DECIMAL.test(texto) && !texto.startsWith('-') && /[1-9]/.test(texto);
}

export type LeituraCampo =
  { readonly ok: true; readonly valor: string } | { readonly ok: false; readonly erro: string };

const COM_MILHAR = /^\d{1,3}(?:\.\d{3})+(?:,\d+)?$/;
const SIMPLES = /^\d+(?:,\d+)?$/;

/**
 * Quantidade digitada em pt-BR para o decimal do contrato. Vírgula é decimal e ponto só separa milhar em grupos de três;
 * "1.5" é recusado em vez de adivinhado (quantidade errada é pior que pedir de novo). Zero e negativo não entram.
 */
export function decimalDoCampo(entrada: string): LeituraCampo {
  const t = entrada.replace(/\s/g, '');
  if (t === '') return { ok: false, erro: 'Informe a quantidade.' };
  if (!COM_MILHAR.test(t) && !SIMPLES.test(t)) {
    return { ok: false, erro: 'Use só números, com vírgula para decimais. Exemplo: 12,5' };
  }
  const valor = t.replace(/\./g, '').replace(',', '.');
  if (!/[1-9]/.test(valor)) return { ok: false, erro: 'Informe uma quantidade maior que zero.' };
  return { ok: true, valor };
}

/** Limite de intervalo digitado no filtro da tabela: aceita zero; até 15 dígitos inteiros e 6 casas. */
export function leituraDoFiltro(texto: string): string | null {
  const t = texto.replace(/\s/g, '');
  if (!COM_MILHAR.test(t) && !SIMPLES.test(t)) return null;
  const valor = t.replace(/\./g, '').replace(',', '.');
  return /^\d{1,15}(?:\.\d{1,6})?$/.test(valor) ? valor : null;
}

/**
 * Soma exata de decimais em texto (até 6 casas, a escala do saldo), para o total da tabela. Sem casas, nada a somar.
 */
export function somarDecimais(valores: readonly string[]): string {
  const ESCALA = 6;
  let total = 0n;
  for (const v of valores) {
    const p = partes(v);
    const fracao = p?.[2] ?? '';
    if (!p || fracao.length > ESCALA) throw new Error('Decimal fora do formato canônico.');
    const inteiro = BigInt(`${p[1]}${fracao.padEnd(ESCALA, '0')}`);
    total += p[0] === '-' ? -inteiro : inteiro;
  }
  const negativo = total < 0n;
  const abs = (negativo ? -total : total).toString().padStart(ESCALA + 1, '0');
  return `${negativo ? '-' : ''}${abs.slice(0, -ESCALA)}.${abs.slice(-ESCALA)}`;
}

/** Compara decimais canônicos sem ponto flutuante: negativo, zero ou positivo. */
export function compararDecimais(a: string, b: string): number {
  const d = somarDecimais([a, `-${b}`.replace(/^--/, '')]);
  return d.startsWith('-') ? -1 : /[1-9]/.test(d) ? 1 : 0;
}
