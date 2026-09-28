/**
 * Registrador estruturado (ENG-081; NFR-12): uma linha JSON por evento, sempre com correlation_id, para seguir uma
 * requisição do aparelho ao efeito persistido. Não registra segredo nem conteúdo pessoal desnecessário: chaves
 * sensíveis são mascaradas em qualquer profundidade, e quem registra escolhe campos, não despeja o conteúdo do comando.
 * Puro: a saída e o relógio são injetados (servidor, worker ou teste).
 */
export type NivelLog = 'info' | 'aviso' | 'erro';

export interface Registrador {
  registrar(
    nivel: NivelLog,
    evento: string,
    correlationId: string,
    campos?: Readonly<Record<string, unknown>>,
  ): void;
}

const SENSIVEL =
  /senha|password|passwd|token|secret|segredo|authorization|cookie|api[_-]?key|credencial|cpf|cnpj|e-?mail|telefone/i;
const MASCARA = '[removido]';

function mascarar(valor: unknown, profundidade = 0): unknown {
  if (profundidade > 8) return '[profundo]';
  if (Array.isArray(valor)) return valor.map((v) => mascarar(v, profundidade + 1));
  if (typeof valor === 'object' && valor !== null) {
    return Object.fromEntries(
      Object.entries(valor).map(([k, v]) => [k, SENSIVEL.test(k) ? MASCARA : mascarar(v, profundidade + 1)]),
    );
  }
  return valor;
}

export function criarRegistrador(opcoes: {
  readonly servico: string;
  readonly versao: string;
  readonly escrever: (linha: string) => void;
  readonly agora: () => string;
}): Registrador {
  return {
    registrar(nivel, evento, correlationId, campos = {}) {
      if (correlationId.trim() === '') throw new Error('log sem correlation_id (ENG-081)');
      const linha = {
        ...(mascarar(campos) as Record<string, unknown>),
        ts: opcoes.agora(),
        nivel,
        evento,
        correlation_id: correlationId,
        servico: opcoes.servico,
        versao: opcoes.versao,
      };
      opcoes.escrever(JSON.stringify(linha));
    },
  };
}
