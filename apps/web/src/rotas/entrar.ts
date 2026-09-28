import {
  abrirContinuacao,
  concluirContinuacao,
  registrarPedidoAcesso,
  revogarSessao,
  vinculosDaContinuacao,
  type ResultadoConclusao,
} from '@safrion/db/web';

import { criarArmazemTransacaoLogin } from '../identidade/armazem';
import { caminhoInterno, INICIO } from '../identidade/caminho';
import {
  criarProvedorDesenvolvimento,
  desenvolvimentoLiberado,
  USUARIOS_DESENVOLVIMENTO,
} from '../identidade/desenvolvimento';
import type { IdentidadeValidada, ProvedorIdentidade } from '../identidade/provedor';
import {
  apagarCookie,
  COOKIE_CONTINUACAO,
  COOKIE_LOGIN,
  COOKIE_PEDIDO,
  COOKIE_SESSAO,
  definirCookie,
  lerCookie,
} from '../seguranca/cookies';
import { correlacaoDe, ErroRequisicao, exigirOrigem, lerCorpoLimitado } from '../seguranca/requisicao';
import type { Dependencias } from '../servidor/ambiente';
import type { FabricaOidc } from '../servidor/oidc';
import { redirecionar } from './resposta';

type Deps = Pick<Dependencias, 'banco' | 'origem' | 'registrador' | 'ambienteDoProcesso'>;

const LIMITE_FORMULARIO_BYTES = 2048;
const CODIGO_NA_TELA_MS = 10 * 60_000;
const MOTIVO_DO_PEDIDO = {
  registrado: 'PEDIDO_REGISTRADO',
  cota_esgotada: 'PEDIDOS_ESGOTADOS',
  fora_de_hml: 'PEDIDO_FORA_DE_HML',
  recusado: 'PEDIDO_RECUSADO',
} as const;

/**
 * Login OIDC validado e sem vínculo (ADR 0004 §11): registra o pedido de acesso, que não concede nada, e entrega o
 * código de referência num cookie HttpOnly de 10 minutos para a tela de /entrar mostrar; nunca na URL nem no log. Sem
 * código novo (fora de hml, cota cheia ou falha), o cookie anterior é apagado: a tela nunca mostra código de outra
 * pessoa que usou o mesmo navegador. Falha ao registrar não muda a resposta: a pessoa vê "sem acesso", sem código.
 */
async function pedidoDeAcesso(
  d: Deps,
  identidade: IdentidadeValidada,
): Promise<{ readonly cookie: string; readonly motivo: string }> {
  try {
    const p = await registrarPedidoAcesso(d.banco, identidade);
    return p.resultado === 'registrado'
      ? {
          cookie: definirCookie(COOKIE_PEDIDO, p.codigo, new Date(Date.now() + CODIGO_NA_TELA_MS)),
          motivo: MOTIVO_DO_PEDIDO.registrado,
        }
      : { cookie: apagarCookie(COOKIE_PEDIDO), motivo: MOTIVO_DO_PEDIDO[p.resultado] };
  } catch {
    return { cookie: apagarCookie(COOKIE_PEDIDO), motivo: 'PEDIDO_FALHOU' };
  }
}
const PAPEL = /^[a-z][a-z_]*$/;

type Ativo =
  | { readonly provedor: ProvedorIdentidade }
  | {
      readonly codigo: 'LOGIN_INDISPONIVEL' | 'PROVEDOR_INDISPONIVEL';
      readonly motivo: 'SEM_CONFIGURACAO' | 'CONFIGURACAO_INVALIDA' | 'DESCOBERTA_FALHOU';
    };

/**
 * Provedor ativo: o de desenvolvimento só com a trava dupla (processo e banco dizem dev); fora disso, o adaptador OIDC do
 * Codex (passo 3 do R-006), pela fábrica da casca. Sem configuração, o login fica indisponível, e não há atalho. O
 * adaptador só informa o código: descoberta que falhou é provedor indisponível (tentar de novo em alguns minutos);
 * configuração inválida é login indisponível (avisar o responsável). O motivo vai só para o log.
 */
async function provedorAtivo(d: Deps, oidc?: FabricaOidc): Promise<Ativo> {
  if (await desenvolvimentoLiberado(d.banco, d.ambienteDoProcesso)) {
    return { provedor: criarProvedorDesenvolvimento(criarArmazemTransacaoLogin(d.banco), d.origem) };
  }
  try {
    const provedor = oidc ? await oidc(d) : null;
    return provedor ? { provedor } : { codigo: 'LOGIN_INDISPONIVEL', motivo: 'SEM_CONFIGURACAO' };
  } catch (e) {
    return e instanceof Error && e.message === 'PROVEDOR_INDISPONIVEL'
      ? { codigo: 'PROVEDOR_INDISPONIVEL', motivo: 'DESCOBERTA_FALHOU' }
      : { codigo: 'LOGIN_INDISPONIVEL', motivo: 'CONFIGURACAO_INVALIDA' };
  }
}

/** Formulário urlencoded estrito: só os campos permitidos, sem repetição; qualquer outro campo é recusa de contrato. */
async function formulario(requisicao: Request, permitidos: readonly string[]): Promise<Map<string, string>> {
  const tipo = (requisicao.headers.get('content-type') ?? '').split(';')[0]?.trim().toLowerCase();
  if (tipo !== 'application/x-www-form-urlencoded') throw new ErroRequisicao('TIPO_DE_CONTEUDO_INVALIDO');
  const campos = new Map<string, string>();
  for (const [chave, valor] of new URLSearchParams(
    await lerCorpoLimitado(requisicao, LIMITE_FORMULARIO_BYTES),
  )) {
    if (!permitidos.includes(chave) || campos.has(chave)) throw new ErroRequisicao('CONTRATO_INVALIDO');
    campos.set(chave, valor);
  }
  return campos;
}

export function criarRotasEntrar(deps: () => Deps, oidc?: FabricaOidc) {
  /** Falha do fluxo de login: volta para /entrar só com o código, e registra o evento sem texto livre. */
  function recusar(
    d: Deps,
    correlationId: string,
    codigo: string,
    cookies: readonly string[] = [],
    motivo?: string,
  ): Response {
    d.registrador.registrar('aviso', 'login.recusado', correlationId, {
      codigo,
      ...(motivo ? { motivo } : {}),
    });
    return redirecionar(d.origem, `/entrar?erro=${codigo}`, cookies);
  }

  function falhaInterna(
    d: Deps,
    correlationId: string,
    e: unknown,
    cookies: readonly string[] = [],
  ): Response {
    const tipo = e instanceof Error && /^[A-Za-z]{1,64}$/.test(e.name) ? e.name : typeof e;
    d.registrador.registrar('erro', 'login.falhou', correlationId, { erro_tipo: tipo });
    return redirecionar(d.origem, '/entrar?erro=FALHA_INTERNA', cookies);
  }

  function aposConclusao(
    d: Deps,
    correlationId: string,
    r: ResultadoConclusao,
    cookies: readonly string[],
  ): Response {
    if (!r.ok) return recusar(d, correlationId, r.codigo, cookies);
    d.registrador.registrar('info', 'login.concluido', correlationId, { usuario_id: r.usuarioId });
    return redirecionar(d.origem, caminhoInterno(r.destino) ?? INICIO, [
      ...cookies,
      definirCookie(COOKIE_SESSAO, r.sessao.token, r.sessao.expiraEm),
      apagarCookie(COOKIE_PEDIDO),
    ]);
  }

  return {
    /** GET /entrar/iniciar?destino=… — abre a transação no provedor ativo e guarda o ticket no cookie. */
    async iniciar(requisicao: Request): Promise<Response> {
      const d = deps();
      const correlationId = correlacaoDe(requisicao);
      try {
        const ativo = await provedorAtivo(d, oidc);
        if (!('provedor' in ativo)) return recusar(d, correlationId, ativo.codigo, [], ativo.motivo);
        const destino = caminhoInterno(new URL(requisicao.url).searchParams.get('destino')) ?? INICIO;
        const { redirecionarPara, ticket, expiraEm } = await ativo.provedor.iniciar(destino);
        const cabecalhos = new Headers({
          location: redirecionarPara.toString(),
          'cache-control': 'no-store',
        });
        cabecalhos.append('set-cookie', definirCookie(COOKIE_LOGIN, ticket, expiraEm));
        return new Response(null, { status: 303, headers: cabecalhos });
      } catch (e) {
        return falhaInterna(d, correlationId, e);
      }
    },

    /**
     * GET /entrar/retorno — o provedor valida o protocolo e devolve só a identidade; a casca guarda a identidade no
     * servidor (continuação) e, com um único vínculo e papel, conclui direto pela mesma função que cria sessão.
     */
    async retorno(requisicao: Request): Promise<Response> {
      const d = deps();
      const correlationId = correlacaoDe(requisicao);
      const semLogin = apagarCookie(COOKIE_LOGIN);
      try {
        const ativo = await provedorAtivo(d, oidc);
        if (!('provedor' in ativo)) return recusar(d, correlationId, ativo.codigo, [semLogin], ativo.motivo);
        const resultado = await ativo.provedor.concluir({
          ticket: lerCookie(requisicao, COOKIE_LOGIN),
          parametros: new URL(requisicao.url).searchParams,
        });
        if (!resultado.ok) return recusar(d, correlationId, resultado.codigo, [semLogin]);
        const { ticket, expiraEm } = await abrirContinuacao(d.banco, resultado.identidade, resultado.destino);
        const vinculos = await vinculosDaContinuacao(d.banco, ticket);
        const [unico] = vinculos;
        if (vinculos.length === 0 || unico === undefined) {
          if (ativo.provedor.nome !== 'oidc') return recusar(d, correlationId, 'SEM_VINCULO', [semLogin]);
          const pedido = await pedidoDeAcesso(d, resultado.identidade);
          return recusar(d, correlationId, 'SEM_VINCULO', [semLogin, pedido.cookie], pedido.motivo);
        }
        const [papel] = unico.papeis;
        if (vinculos.length === 1 && unico.papeis.length === 1 && papel !== undefined) {
          const r = await concluirContinuacao(d.banco, ticket, {
            organizationId: unico.organizationId,
            papel,
          });
          return aposConclusao(d, correlationId, r, [semLogin]);
        }
        return redirecionar(d.origem, '/entrar/escolher', [
          semLogin,
          definirCookie(COOKIE_CONTINUACAO, ticket, expiraEm),
        ]);
      } catch (e) {
        return falhaInterna(d, correlationId, e, [semLogin]);
      }
    },

    /** POST /entrar/escolher/confirmar — só organização e papel; a identidade está no servidor. */
    async confirmarEscolha(requisicao: Request): Promise<Response> {
      const d = deps();
      const correlationId = correlacaoDe(requisicao);
      const semContinuacao = apagarCookie(COOKIE_CONTINUACAO);
      try {
        exigirOrigem(requisicao, d.origem);
        const campos = await formulario(requisicao, ['organizationId', 'papel']);
        const organizationId = campos.get('organizationId') ?? '';
        const papel = campos.get('papel') ?? '';
        if (!PAPEL.test(papel)) return recusar(d, correlationId, 'VINCULO_AUSENTE', [semContinuacao]);
        const r = await concluirContinuacao(d.banco, lerCookie(requisicao, COOKIE_CONTINUACAO), {
          organizationId,
          papel,
        });
        return aposConclusao(d, correlationId, r, [semContinuacao]);
      } catch (e) {
        if (e instanceof ErroRequisicao) return recusar(d, correlationId, e.codigo, [semContinuacao]);
        return falhaInterna(d, correlationId, e, [semContinuacao]);
      }
    },

    /** POST /sair — revoga a sessão do Safrion e apaga o cookie. */
    async sair(requisicao: Request): Promise<Response> {
      const d = deps();
      const correlationId = correlacaoDe(requisicao);
      try {
        exigirOrigem(requisicao, d.origem);
        await revogarSessao(d.banco, lerCookie(requisicao, COOKIE_SESSAO));
        return redirecionar(d.origem, '/entrar', [apagarCookie(COOKIE_SESSAO)]);
      } catch (e) {
        if (e instanceof ErroRequisicao) return recusar(d, correlationId, e.codigo);
        return falhaInterna(d, correlationId, e);
      }
    },

    /**
     * POST /entrar/desenvolvimento/autorizar — a "tela do provedor" de DEV: escolhe o usuário fictício e volta ao
     * callback com state e code. Com a trava fechada, 404 como rota inexistente.
     */
    async autorizarDesenvolvimento(requisicao: Request): Promise<Response> {
      const d = deps();
      const correlationId = correlacaoDe(requisicao);
      if (!(await desenvolvimentoLiberado(d.banco, d.ambienteDoProcesso)))
        return new Response(null, { status: 404 });
      try {
        exigirOrigem(requisicao, d.origem);
        const campos = await formulario(requisicao, ['state', 'usuario']);
        const usuario = campos.get('usuario') ?? '';
        const state = campos.get('state') ?? '';
        if (!Object.hasOwn(USUARIOS_DESENVOLVIMENTO, usuario)) {
          return recusar(d, correlationId, 'RESPOSTA_INVALIDA');
        }
        const retorno = new URLSearchParams({ state, code: usuario });
        return redirecionar(d.origem, `/entrar/retorno?${retorno.toString()}`);
      } catch (e) {
        if (e instanceof ErroRequisicao) return recusar(d, correlationId, e.codigo);
        return falhaInterna(d, correlationId, e);
      }
    },
  };
}
