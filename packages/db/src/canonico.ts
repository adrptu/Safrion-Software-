import { createHash } from 'node:crypto';

import { ErroComando } from './erros.js';

/** Versão da regra de canonização gravada em cada registro (IDEM-13: canonical_version). */
export const VERSAO_CANONICA = 'CANON-1';

/**
 * Texto canônico do conteúdo de um comando (IDEM-13): chaves de objeto em ordem fixa, sem campos indefinidos, texto em
 * NFC, só inteiros seguros como número. Decimal chega como texto normalizado (24.1); ponto flutuante é recusado para não
 * virar hash diferente do mesmo valor. Data e decimal de biblioteca precisam ser convertidos antes, por quem monta o
 * conteúdo; objetos que não sejam simples são recusados.
 */
export function canonizar(valor: unknown): string {
  if (valor === null) return 'null';
  switch (typeof valor) {
    case 'string':
      return JSON.stringify(valor.normalize('NFC'));
    case 'boolean':
      return valor ? 'true' : 'false';
    case 'number':
      if (!Number.isSafeInteger(valor)) {
        throw new ErroComando(
          'CONTRATO_INVALIDO',
          'Número no conteúdo do comando só como inteiro; decimal vai como texto normalizado (24.1).',
        );
      }
      return String(valor);
    case 'object': {
      if (Array.isArray(valor)) return `[${valor.map(canonizar).join(',')}]`;
      const proto: unknown = Object.getPrototypeOf(valor);
      if (proto !== Object.prototype && proto !== null) {
        throw new ErroComando(
          'CONTRATO_INVALIDO',
          'O conteúdo do comando aceita só objetos simples; converta datas e decimais para texto.',
        );
      }
      const obj = valor as Record<string, unknown>;
      const chaves = Object.keys(obj)
        .filter((k) => obj[k] !== undefined)
        .sort();
      return `{${chaves.map((k) => `${JSON.stringify(k.normalize('NFC'))}:${canonizar(obj[k])}`).join(',')}}`;
    }
    default:
      throw new ErroComando(
        'CONTRATO_INVALIDO',
        `Valor do tipo ${typeof valor} não entra no conteúdo do comando.`,
      );
  }
}

/** SHA-256, em hexadecimal, do texto canônico. */
export function hashCanonico(valor: unknown): string {
  return createHash('sha256').update(canonizar(valor), 'utf8').digest('hex');
}
