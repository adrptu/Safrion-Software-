import { decimal } from '@safrion/domain';
import { z } from 'zod';

import { EsquemaUuid } from './comando.js';
import { EsquemaDecimalTexto } from './quantidade.js';

/**
 * Cadastros agrícolas, incremento 1: fazenda e talhão (contrato CAD-01 v3, §3 e §4). Organização e ator vêm da sessão,
 * nunca do corpo (ENG-021). Os esquemas devolvem a forma canônica (nome normalizado, área sem zeros à direita), que é a
 * que entra no hash da intenção: " T1 " e "T1" com a mesma chave são o mesmo conteúdo.
 */

/** commandType de cada comando do incremento 1 (contrato CAD-01 §4). */
export const COMANDOS_CADASTRO = {
  criarFazenda: 'cadastros.criar-fazenda',
  editarFazenda: 'cadastros.editar-fazenda',
  criarTalhao: 'cadastros.criar-talhao',
  editarTalhao: 'cadastros.editar-talhao',
  alterarSituacaoTalhao: 'cadastros.alterar-situacao-talhao',
} as const;
export type ComandoCadastro = (typeof COMANDOS_CADASTRO)[keyof typeof COMANDOS_CADASTRO];

// Nome ------------------------------------------------------------------------------------------------------------

/** A mesma classe de espaços de app.normalizar_nome (migração 0008), enumerada para não depender do locale. */
const ESPACOS = /[\t\n\v\f\r \u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]+/gu;
export const NOME_MAX = 80;

/**
 * NFC, espaços colapsados e pontas aparadas, como no banco. Serve à tela e ao hash; quem decide a unicidade é o índice
 * do banco sobre a mesma regra.
 */
export function normalizarNome(texto: string): string {
  return texto.normalize('NFC').replace(ESPACOS, ' ').replace(/^ | $/g, '');
}

/** Tamanho em caracteres (pontos de código), como o char_length do banco; emoji conta 1, não 2. */
function caracteres(texto: string): number {
  // Pontos de código, não grafemas: é o que o banco conta; um emoji composto conta mais de 1 lá e aqui.
  return Array.from(texto).length;
}

export const EsquemaNomeCadastro = z
  .string()
  .max(1000)
  .transform(normalizarNome)
  .refine((v) => caracteres(v) >= 1, { message: 'NOME_VAZIO' })
  .refine((v) => caracteres(v) <= NOME_MAX, { message: 'NOME_LONGO' });

// Área ------------------------------------------------------------------------------------------------------------

const AREA_INTEIROS = 8;
const AREA_CASAS = 6;

/** Recusa da área, com a instrução para a tela. */
export const MENSAGENS_AREA = {
  AREA_AMBIGUA: 'Use vírgula nos decimais: 1204 ou 1,204.',
  AREA_INVALIDA: 'Informe a área em hectares, por exemplo 204 ou 204,5.',
  AREA_NAO_POSITIVA: 'A área tem de ser maior que zero.',
  AREA_CASAS: 'Use no máximo 6 casas decimais.',
  AREA_GRANDE: 'Use no máximo 8 dígitos antes da vírgula.',
} as const;
export type CodigoArea = keyof typeof MENSAGENS_AREA;

/** Confere uma área já em texto canônico ("204.5"); devolve a forma canônica ou o código da recusa. */
function conferirArea(canonico: string): { valor: string } | { erro: CodigoArea } {
  let d;
  try {
    d = decimal(canonico);
  } catch {
    return { erro: 'AREA_INVALIDA' };
  }
  if (!d.isPositive() || d.isZero()) return { erro: 'AREA_NAO_POSITIVA' };
  if (d.decimalPlaces() > AREA_CASAS) return { erro: 'AREA_CASAS' };
  if (d.trunc().toFixed().length > AREA_INTEIROS) return { erro: 'AREA_GRANDE' };
  return { valor: d.toFixed() };
}

/**
 * Área declarada em ha no comando: texto decimal canônico, maior que zero, até 8 dígitos inteiros e 6 casas (numeric
 * 14,6). Fora disso é recusa de contrato (400), nunca violação de CHECK no efeito. Sai sem zeros à direita.
 */
export const EsquemaAreaHa = EsquemaDecimalTexto.transform((valor, ctx) => {
  const r = conferirArea(valor);
  if ('erro' in r) {
    ctx.addIssue({ code: 'custom', message: r.erro });
    return z.NEVER;
  }
  return r.valor;
});

/**
 * Lê a área digitada em pt-BR para a forma canônica do comando: "204", "204,5", "1.204,50", "1.204.500". Recusa "1.204"
 * (decisão técnica do contrato CAD-01 §3): pode ser mil duzentos e quatro ou 1,204 digitado com ponto, e errar a área por
 * mil vezes é o dano. Ponto decimal sem ambiguidade ("204.5") é aceito.
 */
export function lerAreaPtBr(
  texto: string,
): { ok: true; valor: string } | { ok: false; erro: CodigoArea; mensagem: string } {
  const falha = (erro: CodigoArea) => ({ ok: false as const, erro, mensagem: MENSAGENS_AREA[erro] });
  const t = texto.replace(/[\s\u00a0]/g, '');
  let canonico: string;
  if (/^\d{1,3}(\.\d{3})*,\d+$/.test(t) || /^\d+,\d+$/.test(t))
    canonico = t.replace(/\./g, '').replace(',', '.');
  else if (/^\d{1,3}\.\d{3}$/.test(t)) return falha('AREA_AMBIGUA');
  else if (/^\d{1,3}(\.\d{3}){2,}$/.test(t)) canonico = t.replace(/\./g, '');
  else if (/^\d+(\.\d+)?$/.test(t)) canonico = t;
  else return falha('AREA_INVALIDA');
  const semZeros = canonico.replace(/^0+(?=\d)/, '');
  const r = conferirArea(semZeros);
  return 'erro' in r ? falha(r.erro) : { ok: true, valor: r.valor };
}

// Fuso ------------------------------------------------------------------------------------------------------------

export const FUSO_PADRAO = 'America/Sao_Paulo';
/** Zonas IANA do Brasil, para o topo da lista (a de Brasília primeiro). */
export const FUSOS_BRASIL = [
  'America/Sao_Paulo',
  'America/Bahia',
  'America/Fortaleza',
  'America/Recife',
  'America/Maceio',
  'America/Belem',
  'America/Araguaina',
  'America/Santarem',
  'America/Noronha',
  'America/Campo_Grande',
  'America/Cuiaba',
  'America/Manaus',
  'America/Porto_Velho',
  'America/Boa_Vista',
  'America/Rio_Branco',
  'America/Eirunepe',
] as const;

const FUSOS_VALIDOS: ReadonlySet<string> = new Set(Intl.supportedValuesOf('timeZone'));

/** Nome IANA válido no runtime (decisão técnica do contrato CAD-01 §3). */
export const EsquemaFuso = z.string().refine((v) => FUSOS_VALIDOS.has(v), { message: 'FUSO_INVALIDO' });

// Dados dos comandos (contrato CAD-01 §4) --------------------------------------------------------------------------

const peloMenosUm = (campos: readonly string[]) => (v: Record<string, unknown>) =>
  campos.some((c) => v[c] !== undefined);

export const EsquemaDadosCriarFazenda = z.strictObject({ nome: EsquemaNomeCadastro, fuso: EsquemaFuso });
export type DadosCriarFazenda = z.output<typeof EsquemaDadosCriarFazenda>;

export const EsquemaDadosEditarFazenda = z
  .strictObject({ nome: EsquemaNomeCadastro.optional(), fuso: EsquemaFuso.optional() })
  .refine(peloMenosUm(['nome', 'fuso']), { message: 'NADA_A_ALTERAR' });
export type DadosEditarFazenda = z.output<typeof EsquemaDadosEditarFazenda>;

export const EsquemaDadosCriarTalhao = z.strictObject({
  fazenda: EsquemaUuid,
  nome: EsquemaNomeCadastro,
  areaDeclaradaHa: EsquemaAreaHa,
});
export type DadosCriarTalhao = z.output<typeof EsquemaDadosCriarTalhao>;

export const EsquemaDadosEditarTalhao = z
  .strictObject({
    fazenda: EsquemaUuid.optional(),
    nome: EsquemaNomeCadastro.optional(),
    areaDeclaradaHa: EsquemaAreaHa.optional(),
  })
  .refine(peloMenosUm(['fazenda', 'nome', 'areaDeclaradaHa']), { message: 'NADA_A_ALTERAR' });
export type DadosEditarTalhao = z.output<typeof EsquemaDadosEditarTalhao>;

export const SITUACOES_TALHAO = ['ativo', 'inativo'] as const;
export type SituacaoTalhao = (typeof SITUACOES_TALHAO)[number];

export const EsquemaDadosAlterarSituacaoTalhao = z.strictObject({ situacao: z.enum(SITUACOES_TALHAO) });
export type DadosAlterarSituacaoTalhao = z.output<typeof EsquemaDadosAlterarSituacaoTalhao>;

/** Tipo do alvo de cada comando no envelope (target.type). */
export const ALVOS_CADASTRO = {
  [COMANDOS_CADASTRO.criarFazenda]: 'farm',
  [COMANDOS_CADASTRO.editarFazenda]: 'farm',
  [COMANDOS_CADASTRO.criarTalhao]: 'field',
  [COMANDOS_CADASTRO.editarTalhao]: 'field',
  [COMANDOS_CADASTRO.alterarSituacaoTalhao]: 'field',
} as const satisfies Record<ComandoCadastro, 'farm' | 'field'>;
