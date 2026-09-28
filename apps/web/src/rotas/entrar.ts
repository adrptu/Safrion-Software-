import {
  abrirContinuacao,
  concluirContinuacao,
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
import type { ProvedorIdentidade } from '../identidade/provedor';
import {
  apagarCookie,
  COOKIE_CONTINUACAO,
  COOKIE_LOGIN,
  COOKIE_SESSAO,
  definirCookie,
  lerCookie,
} from '../seguranca/cookies';
import { correlacaoDe, ErroRequisicao, exigirOrigem, lerCorpoLimitado } from '../seguranca/requisicao';
import type { Dependencias } from '../servidor/ambiente';
import { redirecionar } from './resposta';

type Deps = Pick<Dependencias, 'banco' | 'origem' | 'registrador' | 'ambienteDoProcesso'>;

const LIMITE_FORMULARIO_BYTES = 2048;
const PAPEL = /^[a-z][a-z_]*$/;

/**
 * Provedor ativo: o de desenvolvimento só com a trava dupla (processo e banco dizem dev); fora disso, o adaptador OIDC do
 * Codex (passo 3 do R-006), que entra por `oidc`. Sem nenhum dos dois, o login fica indisponível, e não há atalho.
 */
async function provedorAtivo(
  d: Deps,
  oidc?: (d: Deps) => ProvedorIdentidade,
): Promise<ProvedorIdentidade | null> {
  if (await desenvolvimentoLiberado(d.banco, d.ambienteDoProcesso)) {
    return criarProvedorDesenvolvimento(criarArmazemTransacaoLogin(d.banco), d.origem);
  }
  return oidc ? oidc(d) : null;
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

export function criarRotasEntrar(deps: () => Deps, oidc?: (d: Deps) => ProvedorIdentidade) {
  /** Falha do fluxo de login: volta para /entrar só com o código, e registra o evento sem texto livre. */
  function recusar(
    d: Deps,
    correlationId: string,
    codigo: string,
    cookies: readonly string[] = [],
  ): Response {
    d.registrador.registrar('aviso', 'login.recusado', correlationId, { codigo });
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
    ]);
  }

  return {
    /** GET /entrar/iniciar?destino=… — abre a transação no provedor ativo e guarda o ticket no cookie. */
    async iniciar(requisicao: Request): Promise<Response> {
      const d = deps();
      const correlationId = correlacaoDe(requisicao);
      try {
        const provedor = await provedorAtivo(d, oidc);
        if (!provedor) return recusar(d, correlationId, 'LOGIN_INDISPONIVEL');
        const destino = caminhoInterno(new URL(requisicao.url).searchParams.get('destino')) ?? INICIO;
        const { redirecionarPara, ticket, expiraEm } = await provedor.iniciar(destino);
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
        const provedor = await provedorAtivo(d, oidc);
        if (!provedor) return recusar(d, correlationId, 'LOGIN_INDISPONIVEL', [semLogin]);
        const resultado = await provedor.concluir({
          ticket: lerCookie(requisicao, COOKIE_LOGIN),
          parametros: new URL(requisicao.url).searchParams,
        });
        if (!resultado.ok) return recusar(d, correlationId, resultado.codigo, [semLogin]);
        const { ticket, expiraEm } = await abrirContinuacao(d.banco, resultado.identidade, resultado.destino);
        const vinculos = await vinculosDaContinuacao(d.banco, ticket);
        const [unico] = vinculos;
        if (vinculos.length === 0 || unico === undefined)
          return recusar(d, correlationId, 'SEM_VINCULO', [semLogin]);
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
