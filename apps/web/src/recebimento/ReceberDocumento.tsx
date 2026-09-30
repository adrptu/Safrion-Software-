'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useCallback, useEffect, useId, useRef, useState, type ReactNode, type SubmitEvent } from 'react';

import { formatarData } from '../formato/data';
import { formatarQuantidade } from '../formato/numero';
import {
  COMANDO,
  desfechoDaConsulta,
  desfechoDoEnvio,
  INCERTO,
  linhaVazia,
  localUnico,
  MAX_LINHAS,
  motivoDaRejeicao,
  NOMES_DOS_MOTIVOS,
  novaIntencao,
  produtoDe,
  recebimentoVazio,
  regraDaValidade,
  SEM_ERROS,
  situacaoDaLinha,
  temErro,
  unidadesDoProduto,
  validarRecebimento,
  type CampoLinha,
  type CampoOrigem,
  type CamposRecebimento,
  type Desfecho,
  type ErrosRecebimento,
  type Opcoes,
} from './formulario';
import { formatarIdentificacao } from './lista';
import {
  apagarIntencao,
  apagarRecebimento,
  armazemLocal,
  chaveDoRecebimento,
  gravarIntencao,
  gravarRecebimento,
  lerIntencoes,
  lerRecebimento,
  prefixoDasIntencoes,
  type IntencaoGuardada,
} from './rascunho';

interface Aviso {
  readonly papel: 'sucesso' | 'erro' | 'atencao';
  readonly texto: string;
  readonly entrar?: boolean;
}

const SEM_RASCUNHO =
  'O navegador não está guardando o rascunho: se a página recarregar, o que foi digitado se perde. Para confirmar, ele precisa guardar o envio.';
const SEM_ARMAZEM =
  'Para confirmar, o navegador precisa guardar o envio antes de mandá-lo (assim ele pode ser conferido se a resposta não voltar). Saia do modo privado ou libere o armazenamento do site; nada foi enviado.';

/** Com mais de um envio pendente (outras abas), cada um é conferido a seu tempo, o mais antigo primeiro. */
const outrasPendentes = (n: number) =>
  n > 1
    ? ` Há ${String(n)} envios pendentes neste navegador; eles são conferidos um de cada vez, o mais antigo primeiro.`
    : '';

const MOTIVOS_NA_ORDEM = ['avaria', 'validade', 'produto_diferente', 'falta', 'sobra', 'outro'] as const;

/**
 * Receber documento (FO-18; contrato CMD-15 §6.2 e §7.1): a origem, as linhas conferidas e um único comando explícito.
 * - Campos condicionais pelo produto (lote do fabricante ou granel; validade do lote existente, informada ou "não se
 *   aplica"; unidade de medida ou embalagem) e pela conferência (motivo com divergência, responsável e prazo com
 *   quarentena, ocorrência com produto diferente). Validação no campo e na linha; o primeiro erro recebe o foco.
 * - O rascunho fica no localStorage por usuário e organização e volta depois de recarregar.
 * - Antes de enviar, a intenção (chave, documento e corpo exatos) é guardada na chave dela; sem conseguir guardar, nada
 *   é enviado. O rascunho nunca toca intenção: uma aba antiga não apaga o envio pendente de outra (CX-UI01).
 * - Havendo intenção pendente (desta ou de outra aba), ela aparece primeiro, travada: a ação é consultar o recibo e, se
 *   ainda não localizado, reenviar o mesmo. Só um recibo correspondente a resolve. A consulta não reenvia.
 */
export function ReceberDocumento({
  opcoes,
  hoje,
  usuarioId,
  organizacaoId,
}: {
  readonly opcoes: Opcoes;
  readonly hoje: string;
  readonly usuarioId: string;
  readonly organizacaoId: string;
}) {
  const base = useId();
  const router = useRouter();
  const chaveRascunho = chaveDoRecebimento(usuarioId, organizacaoId);
  const [campos, setCampos] = useState<CamposRecebimento>(() => recebimentoVazio(opcoes, hoje, 'l1'));
  const [pendente, setPendente] = useState<IntencaoGuardada | null>(null);
  const intencao = pendente?.intencao ?? null;
  const [erros, setErros] = useState<ErrosRecebimento>(SEM_ERROS);
  const [ocupado, setOcupado] = useState<'enviando' | 'consultando' | null>(null);
  const [naoLocalizado, setNaoLocalizado] = useState(false);
  const [aviso, setAviso] = useState<Aviso | null>(null);
  const formulario = useRef<HTMLFormElement>(null);
  // Enviando ou consultando nesta aba: o aviso de outra aba espera a resposta (a resolução recarrega de novo).
  const ocupadoAgora = useRef(false);
  const travado = ocupado !== null || intencao !== null;

  /**
   * Estado vindo do navegador: a intenção pendente mais antiga manda (travada); sem nenhuma, o rascunho. Nunca envia nem
   * consulta sozinho.
   */
  const recarregar = useCallback(
    (depois: Aviso | null = null) => {
      const armazem = armazemLocal();
      const pendentes = lerIntencoes(armazem, usuarioId, organizacaoId);
      const [primeira] = pendentes;
      setNaoLocalizado(false);
      if (primeira) {
        setPendente(primeira);
        setCampos(primeira.campos);
        setAviso({
          papel: 'atencao',
          texto: `${depois ? `${depois.texto} ` : ''}${INCERTO}${outrasPendentes(pendentes.length)}`,
        });
        return;
      }
      setPendente(null);
      setCampos(lerRecebimento(armazem, chaveRascunho)?.campos ?? recebimentoVazio(opcoes, hoje, 'l1'));
      setAviso(depois ?? (armazem ? null : { papel: 'atencao', texto: SEM_ARMAZEM }));
    },
    [usuarioId, organizacaoId, chaveRascunho, opcoes, hoje],
  );

  useEffect(() => {
    // localStorage só existe no navegador, depois da hidratação.
    // eslint-disable-next-line react-hooks/set-state-in-effect -- estado inicial lido do navegador
    recarregar();
    const prefixo = prefixoDasIntencoes(usuarioId, organizacaoId);
    // Outra aba criou ou resolveu uma intenção: esta passa a mostrar a pendente mais antiga, ou volta ao rascunho.
    const ouvir = (ev: StorageEvent) => {
      if (ocupadoAgora.current) return;
      if (ev.key === null || ev.key.startsWith(prefixo)) recarregar();
    };
    window.addEventListener('storage', ouvir);
    return () => {
      window.removeEventListener('storage', ouvir);
    };
  }, [recarregar, usuarioId, organizacaoId]);

  function atualizar(proximos: CamposRecebimento) {
    setCampos(proximos);
    // Armazenamento cheio ou bloqueado não derruba a tela nem passa em silêncio (Codex 06:56Z).
    if (!gravarRecebimento(armazemLocal(), chaveRascunho, { campos: proximos }))
      setAviso((a) => a ?? { papel: 'atencao', texto: SEM_RASCUNHO });
  }

  function mudarOrigem(campo: CampoOrigem, valor: string) {
    if (travado) return;
    let proximos: CamposRecebimento = { ...campos, [campo]: valor };
    if (campo === 'fazenda') {
      // Trocar a fazenda muda os locais possíveis: o local único dela entra; o de outra fazenda sai.
      const unico = localUnico(opcoes, valor);
      const locais = opcoes.fazendas.find((f) => f.id === valor)?.locais ?? [];
      proximos = {
        ...proximos,
        linhas: proximos.linhas.map((l) => ({
          ...l,
          local: locais.some((x) => x.id === l.local) ? l.local : unico,
        })),
      };
    }
    setErros((e) => ({ ...e, origem: { ...e.origem, [campo]: undefined } }));
    atualizar(proximos);
  }

  function mudarLinha(id: string, campo: CampoLinha, valor: string) {
    if (travado) return;
    const proximos = {
      ...campos,
      linhas: campos.linhas.map((l) => {
        if (l.id !== id) return l;
        const nova = { ...l, [campo]: valor };
        // Outro produto: unidade, lote e validade do anterior não servem mais.
        return campo === 'produto'
          ? { ...nova, unidade: produtoDe(opcoes, valor)?.unidade ?? '', lote: '', validade: '' }
          : nova;
      }),
    };
    setErros((e) => ({ ...e, linhas: { ...e.linhas, [id]: { ...e.linhas[id], [campo]: undefined } } }));
    atualizar(proximos);
  }

  function adicionarLinha() {
    if (travado || campos.linhas.length >= MAX_LINHAS) return;
    const id = crypto.randomUUID();
    atualizar({
      ...campos,
      linhas: [...campos.linhas, linhaVazia(id, { local: localUnico(opcoes, campos.fazenda) })],
    });
    requestAnimationFrame(() => {
      formulario.current?.querySelector<HTMLElement>(`[data-campo="${id}:produto"]`)?.focus();
    });
  }

  function removerLinha(id: string) {
    if (travado || campos.linhas.length <= 1) return;
    atualizar({ ...campos, linhas: campos.linhas.filter((l) => l.id !== id) });
  }

  function focarPrimeiroErro(e: ErrosRecebimento) {
    const origem = (
      ['emitente', 'tipo', 'serie', 'numero', 'emissao', 'recebimento', 'fazenda'] as const
    ).find((c) => e.origem[c]);
    let alvo = origem ?? '';
    if (!origem) {
      for (const l of campos.linhas) {
        const c = Object.entries(e.linhas[l.id] ?? {}).find(([, v]) => v)?.[0];
        if (c) {
          alvo = `${l.id}:${c}`;
          break;
        }
      }
    }
    formulario.current?.querySelector<HTMLElement>(`[data-campo="${alvo}"]`)?.focus();
  }

  function aplicar(d: Desfecho, g: IntencaoGuardada) {
    const armazem = armazemLocal();
    if (d.tipo === 'incerto') {
      // A intenção continua na chave dela, travada; só o recibo correspondente a resolve.
      setPendente(g);
      setNaoLocalizado(d.naoLocalizado);
      setAviso({ papel: 'atencao', texto: d.mensagem, entrar: d.sessao });
      return;
    }
    // Resolvida (recibo correspondente) ou recusa certa do primeiro envio: só esta intenção sai do navegador.
    apagarIntencao(armazem, usuarioId, organizacaoId, g.intencao.chave);
    if (d.tipo === 'resolvido' && d.recibo.outcome === 'confirmed') {
      // O rascunho só é limpo se ainda for o que foi enviado: o que outra aba digitou depois fica.
      const rascunho = lerRecebimento(armazem, chaveRascunho);
      if (rascunho && JSON.stringify(rascunho.campos) === JSON.stringify(g.campos)) {
        apagarRecebimento(armazem, chaveRascunho);
      }
      router.push(`/estoque/recebimentos/${g.intencao.documentoId}`);
      return;
    }
    // Rejeitado, conflito ou recusa certa: o conteúdo volta para correção, e uma nova confirmação terá outra chave.
    gravarRecebimento(armazem, chaveRascunho, { campos: g.campos });
    const aviso: Aviso =
      d.tipo === 'resolvido'
        ? { papel: 'erro', texto: motivoDaRejeicao(d.recibo.reasonCode).mensagem }
        : { papel: 'erro', texto: d.mensagem, entrar: d.sessao };
    recarregar(aviso);
    if (d.tipo === 'resolvido') {
      const m = motivoDaRejeicao(d.recibo.reasonCode);
      if (m.campo) {
        const campo = m.campo;
        setErros({ ...SEM_ERROS, origem: { [campo]: m.mensagem } });
      }
    }
  }

  function ocupar(estado: 'enviando' | 'consultando' | null) {
    ocupadoAgora.current = estado !== null;
    setOcupado(estado);
  }

  async function postar(g: IntencaoGuardada, reenvio: boolean) {
    const i = g.intencao;
    ocupar('enviando');
    let d: Desfecho;
    try {
      const resposta = await fetch(`/api/v1/comandos/${COMANDO}`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        credentials: 'same-origin',
        body: i.corpo,
      });
      const corpo: unknown = await resposta.json().catch(() => null);
      d = desfechoDoEnvio(resposta.status, corpo, i, reenvio);
    } catch {
      d = { tipo: 'incerto', mensagem: INCERTO, sessao: false, naoLocalizado: false };
    }
    aplicar(d, g);
    ocupar(null);
  }

  async function confirmar(evento: SubmitEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (travado) return;
    const v = validarRecebimento(campos, opcoes);
    if (!v.ok) {
      setErros(v.erros);
      setAviso(v.erros.geral ? { papel: 'erro', texto: v.erros.geral } : null);
      focarPrimeiroErro(v.erros);
      return;
    }
    setErros(SEM_ERROS);
    const g: IntencaoGuardada = {
      campos,
      intencao: novaIntencao(v.dados, crypto.randomUUID(), crypto.randomUUID()),
      criadaEm: new Date().toISOString(),
    };
    // A intenção fica guardada na chave dela ANTES de sair; sem isso, nada é enviado (Codex 06:56Z).
    if (!gravarIntencao(armazemLocal(), usuarioId, organizacaoId, g)) {
      setAviso({ papel: 'erro', texto: SEM_ARMAZEM });
      return;
    }
    setPendente(g);
    setAviso(null);
    await postar(g, false);
  }

  async function consultar() {
    if (!pendente || ocupado) return;
    const intencao = pendente.intencao;
    ocupar('consultando');
    let d: Desfecho;
    try {
      const resposta = await fetch(`/api/v1/intencoes/${COMANDO}/${encodeURIComponent(intencao.chave)}`, {
        credentials: 'same-origin',
        cache: 'no-store',
      });
      const corpo: unknown = await resposta.json().catch(() => null);
      d = desfechoDaConsulta(resposta.status, corpo, intencao);
    } catch {
      d = desfechoDaConsulta(0, null, intencao);
    }
    aplicar(d, pendente);
    ocupar(null);
  }

  const e = (id: string) => (campo: CampoLinha) => erros.linhas[id]?.[campo];
  const idDe = (chave: string) => `${base}-${chave.replace(/[^A-Za-z0-9-]/g, '-')}`;
  const fazenda = opcoes.fazendas.find((f) => f.id === campos.fazenda);
  const locais = fazenda?.locais ?? [];
  const resumo = campos.linhas.map(situacaoDaLinha);
  const divergencias = resumo.filter((s) => s.divergente).length;
  const inspecoes = resumo.filter((s) => s.inspecao).length;
  const destinoLogin = `/entrar?${new URLSearchParams({ destino: '/estoque/recebimentos/novo' }).toString()}`;

  return (
    <form
      ref={formulario}
      className="recebimento"
      noValidate
      aria-busy={ocupado !== null}
      onSubmit={(ev) => void confirmar(ev)}
    >
      <section className="bloco" aria-labelledby={idDe('origem')}>
        <h2 id={idDe('origem')}>Documento</h2>
        <div className="bloco-corpo formulario formulario-grade">
          {opcoes.emitentes.length === 1 ? (
            <Leitura
              rotulo="Emitente"
              valor={`${opcoes.emitentes[0]?.nome ?? ''} · ${formatarIdentificacao(opcoes.emitentes[0]?.identificacao ?? '')}`}
            />
          ) : (
            <Campo id={idDe('emitente')} rotulo="Emitente" erro={erros.origem.emitente}>
              <select
                id={idDe('emitente')}
                data-campo="emitente"
                value={campos.emitente}
                disabled={travado}
                aria-invalid={erros.origem.emitente ? true : undefined}
                aria-describedby={erros.origem.emitente ? `${idDe('emitente')}-erro` : undefined}
                onChange={(ev) => {
                  mudarOrigem('emitente', ev.target.value);
                }}
              >
                <option value="">Escolha o emitente</option>
                {opcoes.emitentes.map((x) => (
                  <option key={x.id} value={x.id}>
                    {x.nome} · {formatarIdentificacao(x.identificacao)}
                  </option>
                ))}
              </select>
            </Campo>
          )}
          <fieldset className="campo">
            <legend>Tipo</legend>
            <div className="pilulas">
              {(['nfe', 'outro'] as const).map((t, i) => (
                <span key={t}>
                  <input
                    id={idDe(`tipo-${t}`)}
                    data-campo={i === 0 ? 'tipo' : undefined}
                    type="radio"
                    name={idDe('tipo')}
                    value={t}
                    checked={campos.tipo === t}
                    disabled={travado}
                    onChange={() => {
                      mudarOrigem('tipo', t);
                    }}
                  />
                  <label htmlFor={idDe(`tipo-${t}`)}>{t === 'nfe' ? 'NF-e' : 'Outro'}</label>
                </span>
              ))}
            </div>
          </fieldset>
          <Texto
            id={idDe('serie')}
            campo="serie"
            rotulo="Série"
            valor={campos.serie}
            erro={erros.origem.serie}
            travado={travado}
            mudar={(v) => {
              mudarOrigem('serie', v);
            }}
          />
          <Texto
            id={idDe('numero')}
            campo="numero"
            rotulo="Número"
            valor={campos.numero}
            erro={erros.origem.numero}
            travado={travado}
            mudar={(v) => {
              mudarOrigem('numero', v);
            }}
          />
          <Texto
            id={idDe('emissao')}
            campo="emissao"
            rotulo="Emissão"
            dica="dd/mm/aaaa"
            numerico
            valor={campos.emissao}
            erro={erros.origem.emissao}
            travado={travado}
            mudar={(v) => {
              mudarOrigem('emissao', v);
            }}
          />
          <Texto
            id={idDe('recebimento')}
            campo="recebimento"
            rotulo="Recebido em"
            dica="dd/mm/aaaa"
            numerico
            valor={campos.recebimento}
            erro={erros.origem.recebimento}
            travado={travado}
            mudar={(v) => {
              mudarOrigem('recebimento', v);
            }}
          />
          {opcoes.fazendas.length === 1 ? (
            <Leitura rotulo="Fazenda" valor={opcoes.fazendas[0]?.nome ?? ''} />
          ) : (
            <Campo id={idDe('fazenda')} rotulo="Fazenda" erro={erros.origem.fazenda}>
              <select
                id={idDe('fazenda')}
                data-campo="fazenda"
                value={campos.fazenda}
                disabled={travado}
                aria-invalid={erros.origem.fazenda ? true : undefined}
                aria-describedby={erros.origem.fazenda ? `${idDe('fazenda')}-erro` : undefined}
                onChange={(ev) => {
                  mudarOrigem('fazenda', ev.target.value);
                }}
              >
                <option value="">Escolha a fazenda</option>
                {opcoes.fazendas.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.nome}
                  </option>
                ))}
              </select>
            </Campo>
          )}
        </div>
      </section>

      {campos.linhas.map((l, indice) => {
        const erro = e(l.id);
        const p = produtoDe(opcoes, l.produto);
        const regra = regraDaValidade(p, l.lote);
        const s = resumo[indice];
        const id = (campo: string) => idDe(`${l.id}-${campo}`);
        const texto = (
          campo: CampoLinha,
          rotulo: string,
          extra: { dica?: string; numerico?: boolean; decimal?: boolean } = {},
        ) => (
          <Texto
            id={id(campo)}
            campo={`${l.id}:${campo}`}
            rotulo={rotulo}
            valor={l[campo]}
            erro={erro(campo)}
            travado={travado}
            {...extra}
            mudar={(v) => {
              mudarLinha(l.id, campo, v);
            }}
          />
        );
        const escolha = (
          campo: CampoLinha,
          rotulo: string,
          itens: readonly { valor: string; rotulo: string }[],
          vazio: string,
        ) => (
          <Campo id={id(campo)} rotulo={rotulo} erro={erro(campo)}>
            <select
              id={id(campo)}
              data-campo={`${l.id}:${campo}`}
              value={l[campo]}
              disabled={travado}
              aria-invalid={erro(campo) ? true : undefined}
              aria-describedby={erro(campo) ? `${id(campo)}-erro` : undefined}
              onChange={(ev) => {
                mudarLinha(l.id, campo, ev.target.value);
              }}
            >
              <option value="">{vazio}</option>
              {itens.map((x) => (
                <option key={x.valor} value={x.valor}>
                  {x.rotulo}
                </option>
              ))}
            </select>
          </Campo>
        );
        const unidadeDaLinha = unidadesDoProduto(p).find((u) => u.valor === l.unidade)?.rotulo ?? '';
        const responsaveis = opcoes.responsaveis.map((r) => ({ valor: r.id, rotulo: r.nome }));
        return (
          <section key={l.id} className="bloco linha-recebimento" aria-labelledby={id('titulo')}>
            <div className="bloco-cabecalho">
              <h2 id={id('titulo')}>Linha {indice + 1}</h2>
              {campos.linhas.length > 1 && !travado ? (
                <button
                  type="button"
                  className="botao botao-mini"
                  aria-label={`Remover linha ${String(indice + 1)}`}
                  onClick={() => {
                    removerLinha(l.id);
                  }}
                >
                  Remover
                </button>
              ) : null}
            </div>
            <div className="bloco-corpo formulario formulario-grade">
              {escolha(
                'produto',
                'Produto',
                opcoes.produtos.map((x) => ({ valor: x.id, rotulo: x.nome })),
                'Escolha o produto',
              )}
              {p?.lote === 'por_documento' ? (
                <Leitura rotulo="Lote" valor="Granel · lote do documento" />
              ) : (
                texto('lote', 'Lote do fabricante')
              )}
              {regra.tipo === 'do_lote' ? (
                <Leitura
                  rotulo="Validade"
                  valor={`${regra.validade === null ? 'Não se aplica' : formatarData(regra.validade)} · do lote já recebido`}
                />
              ) : regra.tipo === 'nao_se_aplica' ? (
                <Leitura rotulo="Validade" valor="Não se aplica" />
              ) : (
                texto('validade', 'Validade', { dica: 'dd/mm/aaaa', numerico: true })
              )}
              {locais.length === 1 ? (
                <Leitura rotulo="Local" valor={locais[0]?.nome ?? ''} />
              ) : (
                escolha(
                  'local',
                  'Local',
                  locais.map((x) => ({ valor: x.id, rotulo: x.nome })),
                  'Escolha o local',
                )
              )}
              <div className="campo" data-erro={erro('documento') || erro('unidade') ? '' : undefined}>
                <label htmlFor={id('documento')}>No documento</label>
                <div className="quantidade">
                  <input
                    id={id('documento')}
                    data-campo={`${l.id}:documento`}
                    type="text"
                    inputMode="decimal"
                    autoComplete="off"
                    value={l.documento}
                    readOnly={travado}
                    aria-invalid={erro('documento') ? true : undefined}
                    aria-describedby={erro('documento') ? `${id('documento')}-erro` : undefined}
                    onChange={(ev) => {
                      mudarLinha(l.id, 'documento', ev.target.value);
                    }}
                  />
                  <select
                    data-campo={`${l.id}:unidade`}
                    aria-label={`Unidade da linha ${String(indice + 1)}`}
                    value={l.unidade}
                    disabled={travado || !p}
                    aria-invalid={erro('unidade') ? true : undefined}
                    onChange={(ev) => {
                      mudarLinha(l.id, 'unidade', ev.target.value);
                    }}
                  >
                    {p ? null : <option value="">Unidade</option>}
                    {unidadesDoProduto(p).map((u) => (
                      <option key={u.valor} value={u.valor}>
                        {u.rotulo}
                      </option>
                    ))}
                  </select>
                </div>
                <Erro id={`${id('documento')}-erro`} texto={erro('documento') ?? erro('unidade')} />
              </div>
              <fieldset className="campo parcelas">
                <legend>Conferido{unidadeDaLinha ? ` (${unidadeDaLinha})` : ''}</legend>
                <div className="parcelas-grade">
                  {texto('apto', 'Apto', { decimal: true })}
                  {texto('quarentena', 'Em inspeção', { decimal: true })}
                  {texto('bloqueado', 'Bloqueado', { decimal: true })}
                  {texto('recusado', 'Recusado', { decimal: true })}
                </div>
                {s?.conferido != null && unidadeDaLinha ? (
                  <p className="situacao-linha">
                    Conferido {formatarQuantidade(s.conferido, unidadeDaLinha)}
                    {s.comparacao === -1
                      ? ' · menos que o documento'
                      : s.comparacao === 1
                        ? ' · mais que o documento'
                        : ''}
                    {s.divergente ? ' · divergência' : ' · confere'}
                  </p>
                ) : null}
              </fieldset>
              {s?.divergente ? (
                <>
                  {escolha(
                    'motivo',
                    'Motivo da divergência',
                    MOTIVOS_NA_ORDEM.map((m) => ({ valor: m, rotulo: NOMES_DOS_MOTIVOS[m] })),
                    'Escolha o motivo',
                  )}
                  {l.motivo === 'outro' ? texto('motivoTexto', 'Descreva o motivo') : null}
                </>
              ) : null}
              {s?.inspecao ? (
                <>
                  {escolha(
                    'inspecaoResponsavel',
                    'Quem decide a inspeção',
                    responsaveis,
                    'Escolha o responsável',
                  )}
                  {texto('inspecaoPrazo', 'Prazo da inspeção', { dica: 'dd/mm/aaaa', numerico: true })}
                </>
              ) : null}
              {s?.divergente && l.motivo === 'produto_diferente' ? (
                <fieldset className="campo ocorrencia">
                  <legend>O que chegou no lugar</legend>
                  <div className="formulario formulario-grade">
                    {escolha(
                      'ocorrenciaProduto',
                      'Produto cadastrado',
                      opcoes.produtos
                        .filter((x) => x.id !== l.produto)
                        .map((x) => ({ valor: x.id, rotulo: x.nome })),
                      'Não cadastrado: descrever',
                    )}
                    {l.ocorrenciaProduto === '' ? texto('ocorrenciaDescricao', 'Descrição do produto') : null}
                    {texto('ocorrenciaQuantidade', 'Quantidade contada', { decimal: true })}
                    {texto('ocorrenciaUnidade', 'Unidade contada')}
                    {escolha(
                      'ocorrenciaDestino',
                      'Destino',
                      [
                        { valor: 'retido_para_decisao', rotulo: 'Retido para decisão' },
                        { valor: 'devolvido_na_entrega', rotulo: 'Devolvido na entrega' },
                      ],
                      'Escolha o destino',
                    )}
                    {escolha('ocorrenciaResponsavel', 'Quem responde', responsaveis, 'Escolha o responsável')}
                    {texto('ocorrenciaPrazo', 'Prazo da decisão', { dica: 'dd/mm/aaaa', numerico: true })}
                  </div>
                </fieldset>
              ) : null}
            </div>
          </section>
        );
      })}

      <div className="acoes-recebimento">
        {!travado && campos.linhas.length < MAX_LINHAS ? (
          <button type="button" className="botao" onClick={adicionarLinha}>
            Adicionar linha
          </button>
        ) : null}
      </div>

      <div className="rodape-acao">
        <p>
          {campos.linhas.length} {campos.linhas.length === 1 ? 'linha' : 'linhas'}
          {divergencias > 0 ? ` · ${String(divergencias)} com divergência` : ''}
          {inspecoes > 0 ? ` · ${String(inspecoes)} em inspeção` : ''}
        </p>
        {intencao ? (
          <>
            {naoLocalizado ? (
              <button
                type="button"
                className="botao"
                disabled={ocupado !== null}
                onClick={() => {
                  if (pendente) void postar(pendente, true);
                }}
              >
                Reenviar o mesmo
              </button>
            ) : null}
            <button
              type="button"
              className="botao botao-primario"
              aria-busy={ocupado === 'consultando'}
              disabled={ocupado !== null}
              onClick={() => void consultar()}
            >
              {ocupado === 'consultando'
                ? 'Consultando'
                : ocupado === 'enviando'
                  ? 'Enviando'
                  : 'Consultar recibo'}
            </button>
          </>
        ) : (
          <button type="submit" className="botao botao-primario" aria-busy={ocupado === 'enviando'}>
            {ocupado === 'enviando' ? 'Enviando' : 'Confirmar recebimento'}
          </button>
        )}
      </div>
      <div role="status" aria-live="polite">
        {aviso ? (
          <p className="aviso" data-papel={aviso.papel}>
            {aviso.texto}
            {aviso.entrar ? (
              <>
                {' '}
                <Link href={destinoLogin}>Entrar</Link>
              </>
            ) : null}
          </p>
        ) : temErro(erros) ? (
          <p className="aviso" data-papel="erro">
            Corrija os campos indicados.
          </p>
        ) : null}
      </div>
    </form>
  );
}

function Erro({ id, texto }: { readonly id: string; readonly texto: string | undefined }) {
  return texto ? (
    <p className="erro" id={id}>
      {texto}
    </p>
  ) : null;
}

function Campo({
  id,
  rotulo,
  erro,
  children,
}: {
  readonly id: string;
  readonly rotulo: string;
  readonly erro: string | undefined;
  readonly children: ReactNode;
}) {
  return (
    <div className="campo" data-erro={erro ? '' : undefined}>
      <label htmlFor={id}>{rotulo}</label>
      {children}
      <Erro id={`${id}-erro`} texto={erro} />
    </div>
  );
}

function Leitura({ rotulo, valor }: { readonly rotulo: string; readonly valor: string }) {
  return (
    <div className="campo">
      <span className="rotulo-leitura">{rotulo}</span>
      <span className="leitura">{valor}</span>
    </div>
  );
}

function Texto({
  id,
  campo,
  rotulo,
  valor,
  erro,
  travado,
  mudar,
  dica,
  numerico,
  decimal,
}: {
  readonly id: string;
  readonly campo: string;
  readonly rotulo: string;
  readonly valor: string;
  readonly erro: string | undefined;
  readonly travado: boolean;
  readonly mudar: (valor: string) => void;
  readonly dica?: string;
  readonly numerico?: boolean;
  readonly decimal?: boolean;
}) {
  const descricao = [dica ? `${id}-dica` : '', erro ? `${id}-erro` : ''].filter(Boolean).join(' ');
  return (
    <div className="campo" data-erro={erro ? '' : undefined}>
      <label htmlFor={id}>{rotulo}</label>
      <input
        id={id}
        data-campo={campo}
        type="text"
        inputMode={decimal ? 'decimal' : numerico ? 'numeric' : undefined}
        autoComplete="off"
        value={valor}
        readOnly={travado}
        aria-invalid={erro ? true : undefined}
        aria-describedby={descricao === '' ? undefined : descricao}
        onChange={(ev) => {
          mudar(ev.target.value);
        }}
      />
      {dica ? (
        <span className="dica" id={`${id}-dica`}>
          {dica}
        </span>
      ) : null}
      <Erro id={`${id}-erro`} texto={erro} />
    </div>
  );
}
