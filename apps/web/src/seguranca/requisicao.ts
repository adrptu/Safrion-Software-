import { randomUUID } from 'node:crypto';

/** Recusa de requisição antes de qualquer efeito, só com código (ADR 0004 §6 e §7). */
export class ErroRequisicao extends Error {
  override readonly name = 'ErroRequisicao';
  constructor(
    readonly codigo:
      'CORPO_EXCEDE_LIMITE' | 'TIPO_DE_CONTEUDO_INVALIDO' | 'SEM_PERMISSAO' | 'CONTRATO_INVALIDO',
  ) {
    super(codigo);
  }
}

/**
 * Lê o corpo contando os bytes recebidos e para ao passar do limite, sem acumular o resto: vale também sem
 * Content-Length ou com Content-Length menor que o corpo real (ADR 0004 §6). UTF-8 inválido é recusa de contrato.
 */
export async function lerCorpoLimitado(requisicao: Request, limiteBytes: number): Promise<string> {
  const declarado = requisicao.headers.get('content-length');
  if (declarado !== null && Number(declarado) > limiteBytes) throw new ErroRequisicao('CORPO_EXCEDE_LIMITE');
  if (!requisicao.body) return '';
  const leitor = requisicao.body.getReader();
  const partes: Uint8Array[] = [];
  let total = 0;
  for (;;) {
    const { done, value } = await leitor.read();
    if (done) break;
    total += value.byteLength;
    if (total > limiteBytes) {
      await leitor.cancel();
      throw new ErroRequisicao('CORPO_EXCEDE_LIMITE');
    }
    partes.push(value);
  }
  const bytes = new Uint8Array(total);
  let posicao = 0;
  for (const parte of partes) {
    bytes.set(parte, posicao);
    posicao += parte.byteLength;
  }
  try {
    return new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  } catch {
    throw new ErroRequisicao('CONTRATO_INVALIDO');
  }
}

/** Mutação da API só com JSON (ADR 0004 §6). */
export function exigirJson(requisicao: Request): void {
  const tipo = (requisicao.headers.get('content-type') ?? '').split(';')[0]?.trim().toLowerCase();
  if (tipo !== 'application/json') throw new ErroRequisicao('TIPO_DE_CONTEUDO_INVALIDO');
}

/** Defesa contra CSRF junto com SameSite: o Origin tem de ser exatamente a origem configurada da aplicação. */
export function exigirOrigem(requisicao: Request, origemDaAplicacao: string): void {
  if (requisicao.headers.get('origin') !== origemDaAplicacao) throw new ErroRequisicao('SEM_PERMISSAO');
}

const IDENTIFICADOR = /^[A-Za-z0-9._:-]{1,128}$/;

/** Correlação do cabeçalho X-Correlation-Id quando tem formato de identificador; senão, gerada no servidor. */
export function correlacaoDe(requisicao: Request): string {
  const recebida = requisicao.headers.get('x-correlation-id');
  return recebida !== null && IDENTIFICADOR.test(recebida) ? recebida : randomUUID();
}
