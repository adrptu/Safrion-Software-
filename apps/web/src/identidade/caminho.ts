import type { CaminhoInterno } from './provedor';

const LIMITE = 512;

/**
 * Destino depois do login, só se for caminho interno: começa com uma única "/", sem esquema, host, "//", "\", espaço nem
 * caractere de controle, até 512 caracteres. A mesma regra está nas tabelas da migração 0003. Qualquer outra coisa é null
 * e quem chama usa "/" (nunca uma URL livre vinda da requisição; ADR 0004 §5).
 */
export function caminhoInterno(valor: unknown): CaminhoInterno | null {
  if (typeof valor !== 'string' || valor.length === 0 || valor.length > LIMITE) return null;
  if (!valor.startsWith('/') || valor.startsWith('//') || valor.includes('\\')) return null;
  if (/[\s\p{Cc}]/u.test(valor)) return null;
  return valor as CaminhoInterno;
}

export const INICIO = '/' as CaminhoInterno;
