'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useId, useRef, useState, useTransition, type SubmitEvent } from 'react';

import {
  desfechoDaResposta,
  pedidoDeEntrada,
  validarEntrada,
  type CampoEntrada,
  type CamposEntrada,
  type ErrosEntrada,
} from './entrada';
import { palavraDaSituacao, SITUACOES_DE_ENTRADA } from './estado';

export interface Opcao {
  readonly valor: string;
  readonly rotulo: string;
}

interface Aviso {
  readonly papel: 'sucesso' | 'erro' | 'atencao';
  readonly texto: string;
  readonly entrar?: boolean;
}

/**
 * Próximo passo do lote para quem registra entrada: quantidade com unidade, situação e local, e um único comando
 * explícito. A chave de idempotência nasce no primeiro envio e é reaproveitada no reenvio do mesmo conteúdo (falha de
 * rede não duplica a entrada); mudar um campo ou a versão do lote gera outra. Erro nunca apaga o que foi digitado.
 */
export function RegistrarEntrada({
  lote,
  unidades,
  unidadePadrao,
  locais,
  destino,
}: {
  readonly lote: { readonly id: string; readonly versao: number };
  readonly unidades: readonly Opcao[];
  readonly unidadePadrao: string;
  readonly locais: readonly Opcao[];
  readonly destino: string;
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
  const [campos, setCampos] = useState<CamposEntrada>({
    quantidade: '',
    unidade: unidadePadrao,
    situacao: '',
    local: locais.length === 1 ? (locais[0]?.valor ?? '') : '',
  });
  const [erros, setErros] = useState<ErrosEntrada>({});
  const [enviando, setEnviando] = useState(false);
  const [aviso, setAviso] = useState<Aviso | null>(null);
  const chave = useRef<string | null>(null);
  const formulario = useRef<HTMLFormElement>(null);

  // Nova versão do lote (depois de salvar ou de um conflito) é outro pedido: outra chave.
  useEffect(() => {
    chave.current = null;
  }, [lote.versao]);

  function mudar(campo: CampoEntrada, valor: string) {
    setCampos((c) => ({ ...c, [campo]: valor }));
    setErros((e) => ({ ...e, [campo]: undefined }));
    chave.current = null;
  }

  async function enviar(evento: SubmitEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (enviando) return;
    const v = validarEntrada(
      campos,
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
    chave.current ??= crypto.randomUUID();
    try {
      const resposta = await fetch('/api/v1/comandos/estoque.registrar-entrada', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify(pedidoDeEntrada(lote, v.dados, chave.current)),
      });
      const corpo: unknown = await resposta.json().catch(() => null);
      const d = desfechoDaResposta(resposta.status, corpo);
      if (d.tipo === 'confirmado') {
        chave.current = null;
        setCampos((c) => ({ ...c, quantidade: '', situacao: '' }));
        setAviso({ papel: 'sucesso', texto: 'Entrada registrada' });
        atualizar();
      } else if (d.tipo === 'conflito') {
        chave.current = null;
        setAviso({ papel: 'atencao', texto: d.mensagem });
        atualizar();
      } else if (d.tipo === 'recusado') {
        setAviso({ papel: 'erro', texto: d.mensagem });
        if (d.campo) setErros({ [d.campo]: d.mensagem });
      } else {
        setAviso({ papel: 'erro', texto: d.mensagem, entrar: d.tipo === 'sessao' });
      }
    } catch {
      setAviso({
        papel: 'erro',
        texto: 'Sem conexão com o servidor. Seus dados continuam aqui; tente de novo.',
      });
    } finally {
      setEnviando(false);
    }
  }

  const erroDe = (campo: CampoEntrada) =>
    erros[campo] ? (
      <p className="erro" id={`${id}-${campo}-erro`}>
        {erros[campo]}
      </p>
    ) : null;
  const descrito = (campo: CampoEntrada) => (erros[campo] ? `${id}-${campo}-erro` : undefined);

  return (
    <form ref={formulario} className="bloco-corpo" noValidate onSubmit={(e) => void enviar(e)}>
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
