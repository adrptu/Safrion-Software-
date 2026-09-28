import { criarRegistrador, type Registrador } from '@safrion/contracts';
import pg from 'pg';

/**
 * Dependências do servidor web, lidas do ambiente uma vez: banco com o papel app_runtime, origem configurada da aplicação
 * (Origin e redirecionamentos nunca vêm da requisição) e registrador de uma linha JSON por evento, sem texto livre.
 */
export interface Dependencias {
  readonly banco: pg.Pool;
  readonly origem: string;
  readonly registrador: Registrador;
  readonly versao: string;
  readonly commit: string;
  readonly ambienteDoProcesso: string | undefined;
}

let atual: Dependencias | undefined;

export function dependencias(): Dependencias {
  if (atual) return atual;
  const url = process.env['DATABASE_URL'];
  const origem = process.env['SAFRION_ORIGEM'];
  if (!url || !origem) throw new Error('DATABASE_URL e SAFRION_ORIGEM são obrigatórios no servidor web.');
  const versao = process.env['SAFRION_VERSAO'] ?? '0.0.0-dev';
  const commit = process.env['SAFRION_COMMIT'] ?? 'desconhecido';
  const registrador = criarRegistrador({
    servico: 'web',
    versao,
    escrever: (linha) => {
      process.stdout.write(`${linha}\n`);
    },
    agora: () => new Date().toISOString(),
  });
  // Pool pequeno por instância (plano R-006, passo 11). Erro de conexão ociosa não derruba o processo nem vai ao log
  // com mensagem do driver: só o código.
  const banco = new pg.Pool({ connectionString: url, max: 3 });
  banco.on('error', (erro: Error & { code?: unknown }) => {
    registrador.registrar('erro', 'banco.conexao_ociosa', 'sem-correlacao', {
      codigo: typeof erro.code === 'string' && /^[0-9A-Z]{5}$/.test(erro.code) ? erro.code : undefined,
    });
  });
  atual = { banco, origem, registrador, versao, commit, ambienteDoProcesso: process.env['SAFRION_AMBIENTE'] };
  return atual;
}
