/**
 * Cliente REST do Secret Manager para a fila de vínculo (R-006, GCP-0017, §3c), sem dependência nova: `fetch` do Node e
 * o token do servidor de metadados do Cloud Run. Só as cinco chamadas que a fila usa, todas por nome exato de versão.
 * Erros viram códigos: nunca URL, projeto, token, corpo da resposta nem conteúdo do pedido.
 *
 * Campos conferidos na referência oficial (28/09/2026):
 * - https://cloud.google.com/secret-manager/docs/reference/rest/v1/projects.secrets.versions (name, createTime em RFC
 *   3339 UTC com até 9 casas, state, etag como texto opaco);
 * - …/projects.secrets.versions/list (filter, pageToken; versions e nextPageToken na resposta);
 * - …/projects.secrets.versions/access e …/SecretPayload (payload.data em base64);
 * - …/projects.secrets.versions/disable e …/destroy (etag no corpo; vale só se for o etag guardado);
 * - https://docs.cloud.google.com/run/docs/container-contract (token em access_token, com Metadata-Flavor: Google).
 */

export interface VersaoAtiva {
  /** Número da versão, como no fim do nome (projects/…/versions/<número>). */
  readonly versao: string;
  readonly createTime: string;
}

export interface EstadoVersao {
  readonly estado: string;
  readonly etag: string;
}

/** O que a fila usa do segredo; injetável (os testes usam uma API falsa em memória). */
export interface SegredoPedido {
  /** Todas as versões ENABLED, de todas as páginas, na ordem que a API der. */
  listarAtivas(): Promise<VersaoAtiva[]>;
  obter(versao: string): Promise<EstadoVersao>;
  acessar(versao: string): Promise<Buffer>;
  desativar(versao: string, etag: string): Promise<void>;
  destruir(versao: string, etag: string): Promise<void>;
}

export type CodigoErroSegredo =
  | 'SEGREDO_INVALIDO'
  | 'METADADOS_INDISPONIVEL'
  | `METADADOS_HTTP_${string}`
  | 'SEGREDO_INDISPONIVEL'
  | `SEGREDO_HTTP_${string}`
  | 'RESPOSTA_INVALIDA';

export class ErroSegredo extends Error {
  override readonly name = 'ErroSegredo';
  constructor(readonly codigo: CodigoErroSegredo) {
    super(
      codigo === 'SEGREDO_INVALIDO'
        ? 'SAFRION_PEDIDO_SEGREDO fora do formato projects/<projeto>/secrets/<nome>; nada foi lido.'
        : 'O Secret Manager não atendeu a chamada; veja o código.',
    );
  }
}

const NOME_DO_SEGREDO = /^projects\/[a-z0-9-]{1,63}\/secrets\/([A-Za-z0-9_-]{1,255})$/;
const INSTANTE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?Z$/;
const API = 'https://secretmanager.googleapis.com/v1/';
const TOKEN = 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token';
// Chamada presa não segura o job até o limite da tarefa.
const PRAZO_MS = 30_000;

type Buscar = (url: string, init: RequestInit) => Promise<Response>;

const objeto = (v: unknown): Record<string, unknown> | undefined =>
  typeof v === 'object' && v !== null && !Array.isArray(v) ? (v as Record<string, unknown>) : undefined;

/**
 * Cliente do segredo `nome` (projects/<projeto>/secrets/<nome>). Nome fora do formato: SEGREDO_INVALIDO, sem rede.
 * O `fetch` é injetável para teste.
 */
export function criarSegredoPedido(nome: string, buscar: Buscar = fetch): SegredoPedido {
  const casou = NOME_DO_SEGREDO.exec(nome);
  if (!casou) throw new ErroSegredo('SEGREDO_INVALIDO');
  // A API devolve o projeto pelo número, e a configuração pode trazer o id: confere-se só o nome do segredo.
  const nomeDaVersao = new RegExp(`^projects/[^/]+/secrets/${String(casou[1])}/versions/([1-9][0-9]{0,18})$`);

  async function lerJson(r: Response): Promise<Record<string, unknown>> {
    const corpo = objeto(await r.json().catch(() => undefined));
    if (!corpo) throw new ErroSegredo('RESPOSTA_INVALIDA');
    return corpo;
  }

  // O servidor de metadados guarda o token e o renova; pedir a cada chamada evita guardar validade aqui.
  async function token(): Promise<string> {
    const r = await buscar(TOKEN, {
      headers: { 'Metadata-Flavor': 'Google' },
      signal: AbortSignal.timeout(PRAZO_MS),
    }).catch(() => {
      throw new ErroSegredo('METADADOS_INDISPONIVEL');
    });
    if (!r.ok) throw new ErroSegredo(`METADADOS_HTTP_${r.status.toString()}`);
    const t = (await lerJson(r))['access_token'];
    if (typeof t !== 'string' || t === '') throw new ErroSegredo('RESPOSTA_INVALIDA');
    return t;
  }

  async function chamar(
    caminho: string,
    corpo?: { readonly etag: string },
  ): Promise<Record<string, unknown>> {
    const t = await token();
    const r = await buscar(API + caminho, {
      method: corpo ? 'POST' : 'GET',
      headers: corpo
        ? { Authorization: `Bearer ${t}`, 'Content-Type': 'application/json' }
        : { Authorization: `Bearer ${t}` },
      ...(corpo ? { body: JSON.stringify(corpo) } : {}),
      signal: AbortSignal.timeout(PRAZO_MS),
    }).catch(() => {
      throw new ErroSegredo('SEGREDO_INDISPONIVEL');
    });
    if (!r.ok) throw new ErroSegredo(`SEGREDO_HTTP_${r.status.toString()}`);
    return lerJson(r);
  }

  const daVersao = (versao: string) => `${nome}/versions/${versao}`;

  return {
    async listarAtivas() {
      const ativas: VersaoAtiva[] = [];
      let pagina = '';
      do {
        const q = new URLSearchParams({ filter: 'state:ENABLED' });
        if (pagina) q.set('pageToken', pagina);
        const r = await chamar(`${nome}/versions?${q.toString()}`);
        // Lista vazia vem sem "versions"; última página, sem "nextPageToken".
        const versoes = r['versions'] ?? [];
        const proxima = r['nextPageToken'] ?? '';
        if (!Array.isArray(versoes) || typeof proxima !== 'string') {
          throw new ErroSegredo('RESPOSTA_INVALIDA');
        }
        for (const v of versoes) {
          const o = objeto(v);
          const numero = typeof o?.['name'] === 'string' ? nomeDaVersao.exec(o['name'])?.[1] : undefined;
          const createTime = o?.['createTime'];
          if (!numero || typeof createTime !== 'string' || !INSTANTE.test(createTime)) {
            throw new ErroSegredo('RESPOSTA_INVALIDA');
          }
          ativas.push({ versao: numero, createTime });
        }
        pagina = proxima;
      } while (pagina);
      return ativas;
    },
    async obter(versao) {
      const r = await chamar(daVersao(versao));
      const estado = r['state'];
      const etag = r['etag'];
      if (typeof estado !== 'string' || typeof etag !== 'string') throw new ErroSegredo('RESPOSTA_INVALIDA');
      return { estado, etag };
    },
    async acessar(versao) {
      const r = await chamar(`${daVersao(versao)}:access`);
      // Dado vazio sai do JSON (proto3): vira pedido vazio, que a validação recusa, e não falha da API.
      const dados = objeto(r['payload'])?.['data'] ?? '';
      if (typeof dados !== 'string') throw new ErroSegredo('RESPOSTA_INVALIDA');
      return Buffer.from(dados, 'base64');
    },
    async desativar(versao, etag) {
      await chamar(`${daVersao(versao)}:disable`, { etag });
    },
    async destruir(versao, etag) {
      await chamar(`${daVersao(versao)}:destroy`, { etag });
    },
  };
}
