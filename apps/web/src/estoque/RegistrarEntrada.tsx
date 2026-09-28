'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useId, useRef, useState, useTransition, type SubmitEvent } from 'react';

import {
  desfechoDaResposta,
  pedidoDeEntrada,
  SEM_CONEXAO,
  validarEntrada,
  type CampoEntrada,
  type CamposEntrada,
  type Desfecho,
  type ErrosEntrada,
} from './entrada';
import { palavraDaSituacao, SITUACOES_DE_ENTRADA } from './estado';
import { armazemDaSessao, chaveDoRascunho, gravarRascunho, lerRascunho, type EnvioIncerto } from './rascunho';

export interface Opcao {
  readonly valor: string;
  readonly rotulo: string;
}

interface Aviso {
  readonly papel: 'sucesso' | 'erro' | 'atencao';
  readonly texto: string;
  readonly entrar?: boolean;
}

const AVISO_INCERTO =
  'A última entrada foi enviada, mas a resposta não chegou. Registre de novo para conferir, sem duplicar.';
const SEM_GUARDA =
  ' Não feche nem recarregue esta página: o navegador não deixou guardar o envio para conferir depois.';

/**
 * Próximo passo do lote para quem registra entrada: quantidade com unidade, situação e local, e um único comando
 * explícito. Cada envio tem a sua chave de idempotência.
 * - Enquanto envia, os campos ficam só leitura (B2-C01): a resposta nunca apaga o que foi digitado depois dela.
 * - O rascunho fica na sessão do navegador, por usuário, organização e lote (B2-C02), e volta depois de recarregar.
 * - Todo envio é guardado com a chave, o conteúdo e a versão antes de sair (B2-C03). Sem resposta certa, ou depois de
 *   uma recarga no meio do envio, os campos ficam travados e "Registrar entrada" reenvia exatamente o mesmo pedido,
 *   que o servidor não duplica. Sem armazenamento no navegador, a tela diz que não dá para conferir depois.
 * - Erro nunca apaga o que foi digitado.
 */
export function RegistrarEntrada({
  lote,
  unidades,
  unidadePadrao,
  locais,
  destino,
  usuarioId,
  organizacaoId,
}: {
  readonly lote: { readonly id: string; readonly versao: number };
  readonly unidades: readonly Opcao[];
  readonly unidadePadrao: string;
  readonly locais: readonly Opcao[];
  readonly destino: string;
  readonly usuarioId: string;
  readonly organizacaoId: string;
}) {
  const id = useId();
  const router = useRouter();
  // Depois do recibo, a tela busca o saldo e o extrato de novo; enquanto isso, o aviso diz que está atualizando (DS-38).
  const [atualizando, iniciarAtualizacao] = useTransition();
  const atualizar = () => {
    iniciarAtualizacao(() => {
      router.refresh();
    });
  };
  const vazio: CamposEntrada = {
    quantidade: '',
    unidade: unidadePadrao,
    situacao: '',
    local: locais.length === 1 ? (locais[0]?.valor ?? '') : '',
  };
  const [campos, setCampos] = useState<CamposEntrada>(vazio);
  const [incerto, setIncerto] = useState<EnvioIncerto | null>(null);
  const [erros, setErros] = useState<ErrosEntrada>({});
  const [enviando, setEnviando] = useState(false);
  const [aviso, setAviso] = useState<Aviso | null>(null);
  const formulario = useRef<HTMLFormElement>(null);
  const chaveRascunho = chaveDoRascunho(usuarioId, organizacaoId, lote.id);
  const travado = enviando || incerto !== null;

  // Recupera o rascunho desta pessoa, organização e lote depois de recarregar; nunca envia sozinho.
  useEffect(() => {
    const r = lerRascunho(armazemDaSessao(), chaveRascunho);
    if (!r) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- sessionStorage só existe no navegador, depois da hidratação
    setCampos(r.campos);
    setIncerto(r.incerto);
    if (r.incerto) setAviso({ papel: 'atencao', texto: AVISO_INCERTO });
  }, [chaveRascunho]);

  function guardar(proximos: CamposEntrada, envio: EnvioIncerto | null): boolean {
    return gravarRascunho(armazemDaSessao(), chaveRascunho, { campos: proximos, incerto: envio });
  }

  function mudar(campo: CampoEntrada, valor: string) {
    if (travado) return;
    const proximos = { ...campos, [campo]: valor };
    setCampos(proximos);
    setErros((e) => ({ ...e, [campo]: undefined }));
    guardar(proximos, null);
  }

  function aplicar(d: Desfecho, envio: EnvioIncerto, duravel: boolean) {
    if (d.tipo === 'falha' && d.incerto) {
      // O envio já está guardado desde antes da requisição; sem armazenamento, o limite fica dito na tela.
      setIncerto(envio);
      setAviso({ papel: 'erro', texto: duravel ? d.mensagem : d.mensagem + SEM_GUARDA });
      return;
    }
    // Daqui em diante a resposta é certa: o envio não está mais pendente.
    setIncerto(null);
    if (d.tipo === 'confirmado') {
      const limpos = { ...envio.campos, quantidade: '', situacao: '' };
      setCampos(limpos);
      guardar(limpos, null);
      setAviso({
        papel: 'sucesso',
        texto: d.jaRecebido ? 'Entrada registrada · o envio anterior já tinha chegado' : 'Entrada registrada',
      });
      atualizar();
      return;
    }
    guardar(envio.campos, null);
    if (d.tipo === 'conflito') {
      setAviso({ papel: 'atencao', texto: d.mensagem });
      atualizar();
    } else if (d.tipo === 'recusado') {
      setAviso({ papel: 'erro', texto: d.mensagem });
      if (d.campo) setErros({ [d.campo]: d.mensagem });
    } else {
      setAviso({ papel: 'erro', texto: d.mensagem, entrar: d.tipo === 'sessao' });
    }
  }

  async function enviar(evento: SubmitEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (enviando) return;
    // Com envio incerto, reenvia exatamente o mesmo pedido (chave, conteúdo e versão); senão, um pedido novo.
    const envio: EnvioIncerto = incerto ?? { chave: crypto.randomUUID(), campos, versao: lote.versao };
    const v = validarEntrada(
      envio.campos,
      unidades.map((u) => u.valor),
      locais.map((l) => l.valor),
    );
    if (!v.ok) {
      setErros(v.erros);
      setAviso(null);
      const primeiro = (['quantidade', 'unidade', 'situacao', 'local'] as const).find((c) => v.erros[c]);
      formulario.current?.querySelector<HTMLElement>(`[data-campo="${primeiro ?? ''}"]`)?.focus();
      return;
    }
    setErros({});
    setAviso(null);
    setEnviando(true);
    // B2-C03: o envio fica guardado ANTES de sair (chave, conteúdo e versão), para uma recarga ou uma aba fechada no
    // meio do caminho ainda poder conferir o mesmo pedido. A resposta conclusiva limpa isso em `aplicar`.
    const duravel = guardar(envio.campos, envio);
    let d: Desfecho;
    try {
      const resposta = await fetch('/api/v1/comandos/estoque.registrar-entrada', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(pedidoDeEntrada({ id: lote.id, versao: envio.versao }, v.dados, envio.chave)),
      });
      const corpo: unknown = await resposta.json().catch(() => null);
      d = desfechoDaResposta(resposta.status, corpo);
    } catch {
      d = SEM_CONEXAO;
    }
    aplicar(d, envio, duravel);
    setEnviando(false);
  }

  const erroDe = (campo: CampoEntrada) =>
    erros[campo] ? (
      <p className="erro" id={`${id}-${campo}-erro`}>
        {erros[campo]}
      </p>
    ) : null;
  const descrito = (campo: CampoEntrada) => (erros[campo] ? `${id}-${campo}-erro` : undefined);

  return (
    <form
      ref={formulario}
      className="bloco-corpo"
      noValidate
      aria-busy={enviando}
      onSubmit={(e) => void enviar(e)}
    >
      <div className="formulario">
        <div className="campo" data-erro={erros.quantidade || erros.unidade ? '' : undefined}>
          <label htmlFor={`${id}-quantidade`}>Quantidade</label>
          <div className="quantidade">
            <input
              id={`${id}-quantidade`}
              data-campo="quantidade"
              type="text"
              inputMode="decimal"
              autoComplete="off"
              value={campos.quantidade}
              readOnly={travado}
              aria-invalid={erros.quantidade ? true : undefined}
              aria-describedby={descrito('quantidade')}
              onChange={(e) => {
                mudar('quantidade', e.target.value);
              }}
            />
            <select
              data-campo="unidade"
              aria-label="Unidade"
              value={campos.unidade}
              disabled={travado}
              aria-invalid={erros.unidade ? true : undefined}
              aria-describedby={descrito('unidade')}
              onChange={(e) => {
                mudar('unidade', e.target.value);
              }}
            >
              {unidades.map((u) => (
                <option key={u.valor} value={u.valor}>
                  {u.rotulo}
                </option>
              ))}
            </select>
          </div>
          {erroDe('quantidade')}
          {erroDe('unidade')}
        </div>
        <fieldset
          className="campo"
          data-erro={erros.situacao ? '' : undefined}
          aria-describedby={descrito('situacao')}
        >
          <legend>Situação</legend>
          <div className="pilulas">
            {SITUACOES_DE_ENTRADA.map((s, i) => (
              <span key={s}>
                <input
                  id={`${id}-${s}`}
                  data-campo={i === 0 ? 'situacao' : undefined}
                  type="radio"
                  name={`${id}-situacao`}
                  value={s}
                  checked={campos.situacao === s}
                  disabled={travado}
                  onChange={() => {
                    mudar('situacao', s);
                  }}
                />
                <label htmlFor={`${id}-${s}`}>{palavraDaSituacao(s)}</label>
              </span>
            ))}
          </div>
          {erroDe('situacao')}
        </fieldset>
        {locais.length === 1 ? (
          <div className="campo">
            <span className="rotulo-leitura">Local</span>
            <span className="leitura">{locais[0]?.rotulo}</span>
          </div>
        ) : (
          <div className="campo" data-erro={erros.local ? '' : undefined}>
            <label htmlFor={`${id}-local`}>Local</label>
            <select
              id={`${id}-local`}
              data-campo="local"
              value={campos.local}
              disabled={travado}
              aria-invalid={erros.local ? true : undefined}
              aria-describedby={descrito('local')}
              onChange={(e) => {
                mudar('local', e.target.value);
              }}
            >
              <option value="">Escolha o local</option>
              {locais.map((l) => (
                <option key={l.valor} value={l.valor}>
                  {l.rotulo}
                </option>
              ))}
            </select>
            {erroDe('local')}
          </div>
        )}
        <button type="submit" className="botao botao-primario" aria-busy={enviando}>
          {enviando ? 'Enviando' : 'Registrar entrada'}
        </button>
      </div>
      <div role="status" aria-live="polite">
        {aviso ? (
          <p className="aviso" data-papel={aviso.papel}>
            {aviso.texto}
            {atualizando ? ' · atualizando o saldo' : ''}
            {aviso.entrar ? (
              <>
                {' '}
                <Link href={`/entrar?${new URLSearchParams({ destino }).toString()}`}>Entrar</Link>
              </>
            ) : null}
          </p>
        ) : null}
      </div>
    </form>
  );
}
