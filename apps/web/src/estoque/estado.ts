import { positivo } from '../formato/numero';

/** Papéis de cor da tabela 74.4.2; a cor sai do papel, nunca da palavra (DS-24). */
export type Papel = 'sucesso' | 'atencao' | 'erro' | 'neutro' | 'informacao';

export interface EstadoExibido {
  readonly palavra: string;
  readonly papel: Papel;
}

export interface SaldoDoLote {
  readonly fisico: string;
  readonly utilizavel: string;
  readonly quarentena: string;
  readonly bloqueado: string;
  readonly loteVencido: boolean;
}

/**
 * Estado do lote pela linha "Lote" da tabela 74.4.3 (palavras e papéis fixos), derivado do saldo agregado. A ordem decide
 * quando há mais de uma situação: sem movimento é Recebido; sem físico é Esgotado; vencido bloqueia tudo; havendo
 * utilizável, o lote está Liberado (o resto aparece no saldo); só em inspeção é Em inspeção; senão, Bloqueado. A causa do
 * bloqueio só aparece quando existe (validade); a F0 não registra outra causa.
 */
export function estadoDoLote(movimentos: number, s: SaldoDoLote): EstadoExibido {
  if (movimentos === 0) return { palavra: 'Recebido', papel: 'neutro' };
  if (!positivo(s.fisico)) return { palavra: 'Esgotado', papel: 'neutro' };
  if (s.loteVencido) return { palavra: 'Bloqueado · validade vencida', papel: 'erro' };
  if (positivo(s.utilizavel)) return { palavra: 'Liberado', papel: 'sucesso' };
  if (positivo(s.quarentena)) return { palavra: 'Em inspeção', papel: 'atencao' };
  return { palavra: 'Bloqueado', papel: 'erro' };
}

/** Situação do movimento com as mesmas palavras do estado (Em inspeção, Liberado, Bloqueado). */
const SITUACAO: ReadonlyMap<string, string> = new Map([
  ['quarentena_livre', 'Em inspeção'],
  ['quarentena_bloqueado', 'Bloqueado'],
  ['liberado_livre', 'Liberado'],
  ['liberado_bloqueado', 'Bloqueado'],
]);

/** Sem situação (null) é texto vazio: o tipo de movimento não tem aquele lado. */
export function palavraDaSituacao(situacao: string | null): string {
  if (situacao === null) return '';
  return SITUACAO.get(situacao) ?? situacao;
}

/** As situações que a entrada da F0-c oferece: receber para inspeção ou já liberado. */
export const SITUACOES_DE_ENTRADA = ['quarentena_livre', 'liberado_livre'] as const;
