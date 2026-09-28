import type { Papel } from '../estoque/estado';
import { compararDecimais, somarDecimais } from '../formato/numero';

/**
 * Lógica da tabela interativa G2 (DS-40), pura e serializável: o servidor monta colunas e células, o componente só
 * guarda o estado e desenha. Ordenar, filtrar (valores, texto e intervalo), buscar, agrupar e somar ficam aqui, com teste.
 */
export type TipoColuna = 'texto' | 'numero' | 'data' | 'estado';

export interface ColunaG2 {
  readonly chave: string;
  readonly rotulo: string;
  readonly tipo: TipoColuna;
  /** Agrupar por esta coluna ajuda a decidir (produto, estado); não vale para identificador nem medida. */
  readonly agrupavel?: boolean;
  /** Medida aditiva: soma no grupo e no total, só quando as linhas somadas têm a mesma unidade (DS-40). */
  readonly somavel?: boolean;
}

export interface CelulaG2 {
  /** O que aparece na célula e na lista de valores do filtro. */
  readonly texto: string;
  /** Para ordenar e para o intervalo: decimal canônico (número), AAAA-MM-DD (data) ou o texto. Vazio é "". */
  readonly valor: string;
  readonly papel?: Papel;
  readonly unidade?: string;
}

export interface LinhaG2 {
  readonly id: string;
  readonly href: string;
  readonly celulas: Readonly<Record<string, CelulaG2>>;
}

export interface Ordem {
  readonly chave: string;
  readonly direcao: 'asc' | 'desc';
}

export interface FiltroColuna {
  /** Valores marcados; ausente é "todos". */
  readonly valores?: readonly string[];
  readonly contem?: string;
  readonly de?: string;
  readonly ate?: string;
}

export interface EstadoG2 {
  readonly ordem: readonly Ordem[];
  readonly filtros: Readonly<Record<string, FiltroColuna>>;
  readonly busca: string;
  readonly agrupar: string | null;
}

export const ESTADO_VAZIO: EstadoG2 = { ordem: [], filtros: {}, busca: '', agrupar: null };

const COLADOR = new Intl.Collator('pt-BR', { numeric: true, sensitivity: 'base' });

/** Sem acento e sem caixa, para busca e filtro textual. */
export function normalizar(texto: string): string {
  return texto.normalize('NFD').replace(/\p{M}/gu, '').toLowerCase();
}

const VAZIA: CelulaG2 = { texto: '', valor: '' };
const celula = (l: LinhaG2, chave: string): CelulaG2 => l.celulas[chave] ?? VAZIA;

function comparar(a: CelulaG2, b: CelulaG2, tipo: TipoColuna): number {
  if (tipo === 'numero') return compararDecimais(a.valor, b.valor);
  if (tipo === 'data') return a.valor < b.valor ? -1 : a.valor > b.valor ? 1 : 0;
  return COLADOR.compare(a.texto, b.texto);
}

function colunaDe(colunas: readonly ColunaG2[], chave: string): ColunaG2 | undefined {
  return colunas.find((c) => c.chave === chave);
}

/** Ordem por várias colunas; vazio vai sempre para o fim, qualquer que seja a direção. Estável. */
export function ordenar(
  linhas: readonly LinhaG2[],
  colunas: readonly ColunaG2[],
  ordem: readonly Ordem[],
): LinhaG2[] {
  const chaves = ordem.flatMap((o) => {
    const c = colunaDe(colunas, o.chave);
    return c ? [{ c, sinal: o.direcao === 'asc' ? 1 : -1 }] : [];
  });
  return linhas
    .map((l, i) => ({ l, i }))
    .sort((x, y) => {
      for (const { c, sinal } of chaves) {
        const a = celula(x.l, c.chave);
        const b = celula(y.l, c.chave);
        if (a.valor === '' || b.valor === '') {
          if (a.valor !== b.valor) return a.valor === '' ? 1 : -1;
          continue;
        }
        const r = comparar(a, b, c.tipo);
        if (r !== 0) return r * sinal;
      }
      return x.i - y.i;
    })
    .map(({ l }) => l);
}

function passa(c: CelulaG2, coluna: ColunaG2, f: FiltroColuna): boolean {
  if (f.valores && !f.valores.includes(c.texto)) return false;
  if (f.contem && !normalizar(c.texto).includes(normalizar(f.contem))) return false;
  if (f.de !== undefined || f.ate !== undefined) {
    if (c.valor === '') return false;
    // Data compara o dia: um instante (AAAA-MM-DDThh:mm) entra no intervalo do seu dia.
    const dia = c.valor.slice(0, 10);
    const cmp = (limite: string) =>
      coluna.tipo === 'numero' ? compararDecimais(c.valor, limite) : dia < limite ? -1 : dia > limite ? 1 : 0;
    if (f.de !== undefined && cmp(f.de) < 0) return false;
    if (f.ate !== undefined && cmp(f.ate) > 0) return false;
  }
  return true;
}

/** Busca em todas as colunas e filtros de coluna; `exceto` deixa uma coluna de fora (lista de valores do seu menu). */
export function filtrar(
  linhas: readonly LinhaG2[],
  colunas: readonly ColunaG2[],
  estado: EstadoG2,
  exceto?: string,
): LinhaG2[] {
  const busca = normalizar(estado.busca.trim());
  return linhas.filter((l) => {
    if (busca && !colunas.some((c) => normalizar(celula(l, c.chave).texto).includes(busca))) return false;
    return colunas.every((c) => {
      const f = estado.filtros[c.chave];
      return c.chave === exceto || !f || passa(celula(l, c.chave), c, f);
    });
  });
}

export interface ValorDaColuna {
  readonly texto: string;
  readonly contagem: number;
}

/** Valores existentes da coluna com contagem, considerando os demais filtros (como no Excel), na ordem da coluna. */
export function valoresDaColuna(
  linhas: readonly LinhaG2[],
  colunas: readonly ColunaG2[],
  estado: EstadoG2,
  chave: string,
): ValorDaColuna[] {
  const coluna = colunaDe(colunas, chave);
  if (!coluna) return [];
  const porTexto = new Map<string, { celula: CelulaG2; contagem: number }>();
  for (const l of filtrar(linhas, colunas, estado, chave)) {
    const c = celula(l, chave);
    const atual = porTexto.get(c.texto);
    if (atual) atual.contagem += 1;
    else porTexto.set(c.texto, { celula: c, contagem: 1 });
  }
  return [...porTexto.values()]
    .sort((a, b) =>
      a.celula.valor === '' || b.celula.valor === ''
        ? Number(a.celula.valor === '') - Number(b.celula.valor === '')
        : comparar(a.celula, b.celula, coluna.tipo),
    )
    .map((v) => ({ texto: v.celula.texto, contagem: v.contagem }));
}

export interface Soma {
  readonly valor: string;
  readonly unidade: string;
}

/** Soma exata das células preenchidas; null se não há o que somar ou se as unidades diferem. */
export function somar(linhas: readonly LinhaG2[], chave: string): Soma | null {
  const cheias = linhas.map((l) => celula(l, chave)).filter((c) => c.valor !== '');
  const unidade = cheias[0]?.unidade;
  if (unidade === undefined || cheias.some((c) => c.unidade !== unidade)) return null;
  return { valor: somarDecimais(cheias.map((c) => c.valor)), unidade };
}

export interface Grupo {
  readonly texto: string;
  readonly linhas: readonly LinhaG2[];
  readonly somas: Readonly<Record<string, Soma | null>>;
}

export interface Resultado {
  /** M de "N de M". */
  readonly total: number;
  readonly linhas: readonly LinhaG2[];
  readonly grupos: readonly Grupo[] | null;
  readonly totais: Readonly<Record<string, Soma | null>>;
}

function somas(linhas: readonly LinhaG2[], colunas: readonly ColunaG2[]): Record<string, Soma | null> {
  return Object.fromEntries(colunas.filter((c) => c.somavel).map((c) => [c.chave, somar(linhas, c.chave)]));
}

export function resultado(
  linhas: readonly LinhaG2[],
  colunas: readonly ColunaG2[],
  estado: EstadoG2,
): Resultado {
  const visiveis = ordenar(filtrar(linhas, colunas, estado), colunas, estado.ordem);
  const agrupar = estado.agrupar === null ? undefined : colunaDe(colunas, estado.agrupar);
  let grupos: Grupo[] | null = null;
  if (agrupar?.agrupavel) {
    const porTexto = new Map<string, LinhaG2[]>();
    for (const l of visiveis) {
      const t = celula(l, agrupar.chave).texto;
      const lista = porTexto.get(t);
      if (lista) lista.push(l);
      else porTexto.set(t, [l]);
    }
    const desc = estado.ordem[0]?.chave === agrupar.chave && estado.ordem[0].direcao === 'desc';
    grupos = [...porTexto.entries()]
      .map(([texto, ls]) => ({ texto, linhas: ls, somas: somas(ls, colunas) }))
      .sort((a, b) => {
        const ca = celula(a.linhas[0] as LinhaG2, agrupar.chave);
        const cb = celula(b.linhas[0] as LinhaG2, agrupar.chave);
        if (ca.valor === '' || cb.valor === '') return Number(ca.valor === '') - Number(cb.valor === '');
        return comparar(ca, cb, agrupar.tipo) * (desc ? -1 : 1);
      });
  }
  return { total: linhas.length, linhas: visiveis, grupos, totais: somas(visiveis, colunas) };
}

// Estado na URL (4.2: voltar e compartilhar preservam filtro, ordem e agrupamento). Chaves: ordem=validade,-fisico;
// busca; agrupar; v.{coluna} repetido (valores marcados); c.{coluna} (contém); de.{coluna} e ate.{coluna} (intervalo).

const LIMITE_TEXTO = 100;
const LIMITE_VALORES = 50;
const NUMERO = /^-?\d{1,15}(?:\.\d{1,6})?$/;
const DATA = /^\d{4}-\d{2}-\d{2}$/;

type Parametros = URLSearchParams | Readonly<Record<string, string | readonly string[] | undefined>>;

function todos(p: Parametros, nome: string): string[] {
  if (p instanceof URLSearchParams) return p.getAll(nome);
  const v = Object.hasOwn(p, nome) ? p[nome] : undefined;
  return v === undefined ? [] : typeof v === 'string' ? [v] : [...v];
}

function limite(tipo: TipoColuna, v: string | undefined): string | undefined {
  if (v === undefined) return undefined;
  if (tipo === 'numero') return NUMERO.test(v) ? v : undefined;
  if (tipo === 'data') return DATA.test(v) ? v : undefined;
  return undefined;
}

/** Lê o estado da URL, aceitando só colunas conhecidas e valores no formato; o resto é ignorado. */
export function estadoDaUrl(p: Parametros, colunas: readonly ColunaG2[]): EstadoG2 {
  const ordem: Ordem[] = [];
  for (const item of (todos(p, 'ordem')[0] ?? '').split(',')) {
    const desc = item.startsWith('-');
    const chave = desc ? item.slice(1) : item;
    if (colunaDe(colunas, chave) && !ordem.some((o) => o.chave === chave))
      ordem.push({ chave, direcao: desc ? 'desc' : 'asc' });
  }
  const filtros: Record<string, FiltroColuna> = {};
  for (const c of colunas) {
    const valores = todos(p, `v.${c.chave}`)
      .filter((v) => v.length <= LIMITE_TEXTO * 2)
      .slice(0, LIMITE_VALORES);
    const contem = todos(p, `c.${c.chave}`)[0]?.slice(0, LIMITE_TEXTO);
    const de = limite(c.tipo, todos(p, `de.${c.chave}`)[0]);
    const ate = limite(c.tipo, todos(p, `ate.${c.chave}`)[0]);
    const f: FiltroColuna = {
      ...(valores.length > 0 ? { valores } : {}),
      ...(contem ? { contem } : {}),
      ...(de !== undefined ? { de } : {}),
      ...(ate !== undefined ? { ate } : {}),
    };
    if (Object.keys(f).length > 0) filtros[c.chave] = f;
  }
  const agrupar = todos(p, 'agrupar')[0];
  return {
    ordem,
    filtros,
    busca: (todos(p, 'busca')[0] ?? '').slice(0, LIMITE_TEXTO),
    agrupar: agrupar !== undefined && colunaDe(colunas, agrupar)?.agrupavel ? agrupar : null,
  };
}

export function urlDoEstado(estado: EstadoG2): URLSearchParams {
  const p = new URLSearchParams();
  if (estado.ordem.length > 0)
    p.set('ordem', estado.ordem.map((o) => (o.direcao === 'desc' ? `-${o.chave}` : o.chave)).join(','));
  if (estado.busca.trim() !== '') p.set('busca', estado.busca);
  if (estado.agrupar !== null) p.set('agrupar', estado.agrupar);
  for (const [chave, f] of Object.entries(estado.filtros)) {
    for (const v of f.valores ?? []) p.append(`v.${chave}`, v);
    if (f.contem) p.set(`c.${chave}`, f.contem);
    if (f.de !== undefined) p.set(`de.${chave}`, f.de);
    if (f.ate !== undefined) p.set(`ate.${chave}`, f.ate);
  }
  return p;
}

/** O filtro sem um dos seus campos (desmarcar um critério). */
export function semCampo(f: FiltroColuna, campo: keyof FiltroColuna): FiltroColuna {
  return Object.fromEntries(Object.entries(f).filter(([k]) => k !== campo));
}

/** Filtros com o da coluna trocado; filtro vazio ou null tira a coluna. */
export function comFiltro(
  filtros: Readonly<Record<string, FiltroColuna>>,
  chave: string,
  f: FiltroColuna | null,
): Record<string, FiltroColuna> {
  const resto = Object.fromEntries(Object.entries(filtros).filter(([k]) => k !== chave));
  return f && filtroAtivo(f) ? { ...resto, [chave]: f } : resto;
}

/** Filtros ativos como chips: "Estado: Liberado, Em inspeção", "Produto contém herb", "Validade de 01/01/2027". */
export function filtroAtivo(f: FiltroColuna): boolean {
  return f.valores !== undefined || Boolean(f.contem) || f.de !== undefined || f.ate !== undefined;
}

/**
 * Próximo estado de ordenação ao clicar no cabeçalho: crescente → decrescente → sem ordem. Com Shift, a coluna entra
 * (ou gira) como critério seguinte, mantendo os demais.
 */
export function alternarOrdem(ordem: readonly Ordem[], chave: string, adicionar: boolean): Ordem[] {
  const atual = ordem.find((o) => o.chave === chave);
  const proxima: Ordem | null = !atual
    ? { chave, direcao: 'asc' }
    : atual.direcao === 'asc'
      ? { chave, direcao: 'desc' }
      : null;
  if (!adicionar) return proxima ? [proxima] : [];
  const resto = ordem.filter((o) => o.chave !== chave);
  if (!proxima) return resto;
  return atual ? ordem.map((o) => (o.chave === chave ? proxima : o)) : [...resto, proxima];
}

/** Link para o detalhe levando o estado da lista, para o Voltar restaurar filtro, ordem e agrupamento. */
export function hrefComVolta(href: string, estado: EstadoG2): string {
  const volta = urlDoEstado(estado).toString();
  return volta === '' ? href : `${href}?${new URLSearchParams({ volta }).toString()}`;
}

/** Caminho de volta para a lista: o caminho é fixo (quem chama informa); da URL só vem a consulta, reescrita. */
export function caminhoDeVolta(lista: string, volta: string | readonly string[] | undefined): string {
  const texto = typeof volta === 'string' ? volta : '';
  if (texto === '' || texto.length > 2048) return lista;
  const consulta = new URLSearchParams(texto).toString();
  return consulta === '' ? lista : `${lista}?${consulta}`;
}
