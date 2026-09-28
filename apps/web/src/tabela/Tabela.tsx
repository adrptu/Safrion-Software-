'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  useEffect,
  useId,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
  type MouseEvent,
  type RefObject,
  type ToggleEvent,
} from 'react';

import { Selo } from '../componentes/Selo';
import { formatarDecimal, formatarQuantidade, leituraDoFiltro } from '../formato/numero';
import { formatarData } from '../formato/data';
import {
  alternarOrdem,
  comFiltro,
  filtroAtivo,
  hrefComVolta,
  resultado,
  semCampo,
  urlDoEstado,
  valoresDaColuna,
  type CelulaG2,
  type ColunaG2,
  type EstadoG2,
  type FiltroColuna,
  type LinhaG2,
  type Soma,
} from './logica';

/**
 * Tabela interativa G2 (DS-40), o componente de lista de todas as telas: ordenar no cabeçalho (Shift soma critério),
 * menu ▾ da coluna com texto, intervalo, valores com contagem e "Agrupar por", busca, "N de M", chips de filtro, grupos
 * com soma e total. O menu usa o popover nativo: Esc e clique fora fecham e o foco volta ao botão, sem biblioteca.
 */
export interface PropsTabela {
  readonly rotulo: string;
  readonly colunas: readonly ColunaG2[];
  readonly linhas: readonly LinhaG2[];
  readonly estadoInicial: EstadoG2;
  readonly nome: { readonly singular: string; readonly plural: string };
  readonly vazio: string;
  /** Lista principal da tela: o estado vai para a URL e segue no link do detalhe. */
  readonly naUrl?: boolean;
}

const VAZIA: CelulaG2 = { texto: '', valor: '' };

function textoDaSoma(s: Soma | null | undefined): string {
  return s ? formatarQuantidade(s.valor, s.unidade) : '';
}

function descreverFiltro(coluna: ColunaG2, f: FiltroColuna): string {
  const partes: string[] = [];
  if (f.valores)
    partes.push(f.valores.length === 0 ? 'nenhum' : f.valores.map((v) => v || '(vazio)').join(', '));
  if (f.contem) partes.push(`contém "${f.contem}"`);
  const fmt = (v: string) => (coluna.tipo === 'data' ? formatarData(v) : formatarDecimal(v));
  if (f.de !== undefined) partes.push(`de ${fmt(f.de)}`);
  if (f.ate !== undefined) partes.push(`até ${fmt(f.ate)}`);
  return `${coluna.rotulo}: ${partes.join(' · ')}`;
}

export function Tabela({ rotulo, colunas, linhas, estadoInicial, nome, vazio, naUrl = false }: PropsTabela) {
  const base = useId();
  const [estado, setEstado] = useState(estadoInicial);
  const [recolhidos, setRecolhidos] = useState<ReadonlySet<string>>(new Set());
  const r = useMemo(() => resultado(linhas, colunas, estado), [linhas, colunas, estado]);

  function mudar(novo: EstadoG2) {
    setEstado(novo);
    if (naUrl) {
      const consulta = urlDoEstado(novo).toString();
      window.history.replaceState(null, '', consulta === '' ? window.location.pathname : `?${consulta}`);
    }
  }
  const mudarFiltro = (chave: string, f: FiltroColuna | null) => {
    mudar({ ...estado, filtros: comFiltro(estado.filtros, chave, f) });
  };
  const limparTudo = () => {
    mudar({ ...estado, filtros: {}, busca: '' });
  };
  const algumFiltro = Object.keys(estado.filtros).length > 0 || estado.busca.trim() !== '';
  const hrefDe = (l: LinhaG2) => (l.href === '' ? '' : naUrl ? hrefComVolta(l.href, estado) : l.href);
  const totalVisivel = r.linhas.length >= 2 && Object.values(r.totais).some((s) => s !== null);

  return (
    <section className="g2" aria-label={rotulo}>
      {r.total === 0 ? null : (
        <div className="g2-barra">
          <input
            type="search"
            className="g2-busca"
            aria-label={`Buscar ${nome.plural}`}
            placeholder="Buscar"
            value={estado.busca}
            onChange={(e) => {
              mudar({ ...estado, busca: e.target.value });
            }}
          />
          <span className="g2-contador" aria-live="polite">
            {r.linhas.length} de {r.total}
          </span>
          {Object.entries(estado.filtros).map(([chave, f]) => {
            const coluna = colunas.find((c) => c.chave === chave);
            return coluna ? (
              <button
                key={chave}
                type="button"
                className="g2-chip"
                aria-label={`Remover filtro ${descreverFiltro(coluna, f)}`}
                onClick={() => {
                  mudarFiltro(chave, null);
                }}
              >
                {descreverFiltro(coluna, f)} <span aria-hidden="true">×</span>
              </button>
            ) : null;
          })}
          {estado.agrupar !== null ? (
            <button
              type="button"
              className="g2-chip"
              aria-label="Remover agrupamento"
              onClick={() => {
                mudar({ ...estado, agrupar: null });
              }}
            >
              Agrupado por {colunas.find((c) => c.chave === estado.agrupar)?.rotulo}{' '}
              <span aria-hidden="true">×</span>
            </button>
          ) : null}
          {/* Com a lista vazia pelo filtro, o "Limpar filtros" fica só na mensagem, junto do motivo. */}
          {algumFiltro && r.linhas.length > 0 ? (
            <button type="button" className="link-acao" onClick={limparTudo}>
              Limpar filtros
            </button>
          ) : null}
          {r.grupos ? (
            <>
              <span className="espaco" />
              <button
                type="button"
                className="link-acao"
                onClick={() => {
                  setRecolhidos(new Set());
                }}
              >
                Expandir tudo
              </button>
              <button
                type="button"
                className="link-acao"
                onClick={() => {
                  setRecolhidos(new Set(r.grupos?.map((g) => g.texto)));
                }}
              >
                Recolher tudo
              </button>
            </>
          ) : null}
        </div>
      )}
      {r.total === 0 ? (
        <p className="g2-vazio">{vazio}</p>
      ) : (
        <div className="g2-rolagem">
          <table>
            <thead>
              <tr>
                {colunas.map((c) => (
                  <Cabeca
                    key={c.chave}
                    id={`${base}-${c.chave}`}
                    coluna={c}
                    colunas={colunas}
                    linhas={linhas}
                    estado={estado}
                    mudar={mudar}
                    mudarFiltro={mudarFiltro}
                  />
                ))}
              </tr>
            </thead>
            <tbody>
              {r.grupos
                ? r.grupos.flatMap((g) => {
                    const aberto = !recolhidos.has(g.texto);
                    const colunaGrupo = colunas.find((c) => c.chave === estado.agrupar);
                    return [
                      <tr key={`g-${g.texto}`} className="g2-grupo">
                        {colunas.map((c, i) => (
                          <td key={c.chave} data-tipo={c.tipo} data-rotulo={i === 0 ? '' : c.rotulo}>
                            {i === 0 ? (
                              <button
                                type="button"
                                className="g2-alternar"
                                aria-expanded={aberto}
                                onClick={() => {
                                  const s = new Set(recolhidos);
                                  if (aberto) s.add(g.texto);
                                  else s.delete(g.texto);
                                  setRecolhidos(s);
                                }}
                              >
                                <span className="g2-marca" aria-hidden="true">
                                  ▾
                                </span>
                                {colunaGrupo?.rotulo}: {g.texto || '(vazio)'}
                                <span className="g2-contagem">{g.linhas.length}</span>
                              </button>
                            ) : (
                              textoDaSoma(g.somas[c.chave])
                            )}
                          </td>
                        ))}
                      </tr>,
                      ...(aberto
                        ? g.linhas.map((l) => (
                            <Linha key={l.id} linha={l} colunas={colunas} href={hrefDe(l)} />
                          ))
                        : []),
                    ];
                  })
                : r.linhas.map((l) => <Linha key={l.id} linha={l} colunas={colunas} href={hrefDe(l)} />)}
            </tbody>
            {totalVisivel ? (
              <tfoot>
                <tr>
                  {colunas.map((c, i) => (
                    <td key={c.chave} data-tipo={c.tipo} data-rotulo={i === 0 ? '' : c.rotulo}>
                      {i === 0 ? 'Total' : textoDaSoma(r.totais[c.chave])}
                    </td>
                  ))}
                </tr>
              </tfoot>
            ) : null}
          </table>
          {r.linhas.length === 0 ? (
            <p className="g2-vazio">
              Nenhum {nome.singular} corresponde aos filtros.
              <button type="button" className="link-acao" onClick={limparTudo}>
                Limpar filtros
              </button>
            </p>
          ) : null}
        </div>
      )}
    </section>
  );
}

function Linha({
  linha,
  colunas,
  href,
}: {
  readonly linha: LinhaG2;
  readonly colunas: readonly ColunaG2[];
  readonly href: string;
}) {
  const router = useRouter();
  const abrir = (e: MouseEvent<HTMLTableRowElement>) => {
    if (href === '' || (e.target as HTMLElement).closest('a, button, input, select, label')) return;
    router.push(href);
  };
  const espaco = (e: KeyboardEvent<HTMLAnchorElement>) => {
    if (e.key === ' ') {
      e.preventDefault();
      router.push(href);
    }
  };
  return (
    <tr data-abre={href === '' ? undefined : ''} onClick={abrir}>
      {colunas.map((c, i) => {
        const cel = linha.celulas[c.chave] ?? VAZIA;
        const conteudo =
          c.tipo === 'estado' && cel.papel ? (
            <Selo estado={{ palavra: cel.texto, papel: cel.papel }} />
          ) : (
            cel.texto
          );
        return (
          <td key={c.chave} data-tipo={c.tipo} data-rotulo={c.rotulo}>
            {i === 0 && href !== '' ? (
              <Link href={href} onKeyDown={espaco}>
                {conteudo}
              </Link>
            ) : (
              conteudo
            )}
          </td>
        );
      })}
    </tr>
  );
}

interface PropsCabeca {
  readonly id: string;
  readonly coluna: ColunaG2;
  readonly colunas: readonly ColunaG2[];
  readonly linhas: readonly LinhaG2[];
  readonly estado: EstadoG2;
  readonly mudar: (e: EstadoG2) => void;
  readonly mudarFiltro: (chave: string, f: FiltroColuna | null) => void;
}

function Cabeca(p: PropsCabeca) {
  const { coluna, estado } = p;
  const botao = useRef<HTMLButtonElement>(null);
  const posicao = estado.ordem.findIndex((o) => o.chave === coluna.chave);
  const direcao = posicao >= 0 ? estado.ordem[posicao]?.direcao : undefined;
  const filtro = estado.filtros[coluna.chave];
  const ativo = filtro !== undefined && filtroAtivo(filtro);
  const idMenu = `${p.id}-menu`;
  return (
    <th
      scope="col"
      data-tipo={coluna.tipo}
      aria-sort={posicao === 0 ? (direcao === 'asc' ? 'ascending' : 'descending') : undefined}
    >
      <span className="g2-cabeca">
        <button
          type="button"
          className="g2-ordenar"
          data-ativa={direcao ? '' : undefined}
          title="Ordenar. Shift+clique soma este critério."
          onClick={(e) => {
            p.mudar({ ...estado, ordem: alternarOrdem(estado.ordem, coluna.chave, e.shiftKey) });
          }}
        >
          {coluna.rotulo}
          <span className="g2-seta" aria-hidden="true">
            {direcao === 'asc' ? '▲' : direcao === 'desc' ? '▼' : '⇅'}
            {estado.ordem.length > 1 && posicao >= 0 ? posicao + 1 : ''}
          </span>
        </button>
        <button
          ref={botao}
          type="button"
          className="g2-filtrar"
          data-ativo={ativo ? '' : undefined}
          popoverTarget={idMenu}
          aria-label={`Filtrar e agrupar ${coluna.rotulo}${ativo ? ' (filtro ativo)' : ''}`}
        >
          <span aria-hidden="true">▾</span>
        </button>
      </span>
      <MenuColuna {...p} idMenu={idMenu} botao={botao} />
    </th>
  );
}

function MenuColuna(
  p: PropsCabeca & { readonly idMenu: string; readonly botao: RefObject<HTMLButtonElement | null> },
) {
  const { coluna, estado } = p;
  const menu = useRef<HTMLDivElement>(null);
  const [aberto, setAberto] = useState(false);
  const [buscaValores, setBuscaValores] = useState('');
  const filtro = estado.filtros[coluna.chave] ?? {};

  // O popover fica na camada superior; a posição vem do botão e é escrita pelo CSSOM, que a CSP permite. Ela é
  // calculada antes de aparecer (beforetoggle), para o menu não piscar fora do lugar, e ajustada com a altura real.
  const posicionar = () => {
    const el = menu.current;
    const b = p.botao.current;
    if (!el || !b) return;
    const r = b.getBoundingClientRect();
    const largura = el.offsetWidth || 260;
    const altura = el.offsetHeight;
    el.style.top = `${String(Math.max(8, Math.min(r.bottom + 4, window.innerHeight - altura - 8)))}px`;
    el.style.left = `${String(Math.max(8, Math.min(r.left, window.innerWidth - largura - 8)))}px`;
  };
  useLayoutEffect(() => {
    if (aberto) posicionar();
  });
  // Ao abrir, o foco vai para o primeiro controle do menu; Esc fecha e o navegador devolve o foco ao botão.
  useEffect(() => {
    if (aberto) menu.current?.querySelector<HTMLElement>('button, input')?.focus();
  }, [aberto]);

  const valores = valoresDaColuna(p.linhas, p.colunas, estado, coluna.chave);
  const visiveis =
    buscaValores.trim() === ''
      ? valores
      : valores.filter((v) => v.texto.toLowerCase().includes(buscaValores.trim().toLowerCase()));
  const marcado = (t: string) => filtro.valores === undefined || filtro.valores.includes(t);
  const alternar = (t: string) => {
    const atuais = filtro.valores ?? valores.map((v) => v.texto);
    const novos = atuais.includes(t) ? atuais.filter((v) => v !== t) : [...atuais, t];
    const todos = valores.every((v) => novos.includes(v.texto));
    const resto = semCampo(filtro, 'valores');
    p.mudarFiltro(coluna.chave, todos ? resto : { ...resto, valores: novos });
  };
  const ordenar = (direcao: 'asc' | 'desc') => {
    p.mudar({ ...estado, ordem: [{ chave: coluna.chave, direcao }] });
  };
  const intervalo = (campo: 'de' | 'ate', texto: string) => {
    const resto = semCampo(filtro, campo);
    const valor =
      coluna.tipo === 'data' ? (/^\d{4}-\d{2}-\d{2}$/.test(texto) ? texto : null) : leituraDoFiltro(texto);
    p.mudarFiltro(coluna.chave, valor === null ? resto : { ...resto, [campo]: valor });
  };
  const fechar = () => {
    menu.current?.hidePopover();
  };

  return (
    <div
      ref={menu}
      id={p.idMenu}
      popover="auto"
      className="g2-menu"
      role="dialog"
      aria-label={`Coluna ${coluna.rotulo}`}
      onBeforeToggle={(e: ToggleEvent<HTMLDivElement>) => {
        if (e.newState === 'open') posicionar();
      }}
      onToggle={(e: ToggleEvent<HTMLDivElement>) => {
        setAberto(e.newState === 'open');
      }}
    >
      <>
        <div className="linha">
          <button
            type="button"
            className="botao botao-mini"
            onClick={() => {
              ordenar('asc');
            }}
          >
            Ordenar crescente
          </button>
          <button
            type="button"
            className="botao botao-mini"
            onClick={() => {
              ordenar('desc');
            }}
          >
            Ordenar decrescente
          </button>
        </div>
        {coluna.tipo === 'texto' || coluna.tipo === 'estado' ? (
          <div className="campo">
            <label htmlFor={`${p.idMenu}-contem`}>Contém</label>
            <input
              id={`${p.idMenu}-contem`}
              type="search"
              value={filtro.contem ?? ''}
              onChange={(e) => {
                const resto = semCampo(filtro, 'contem');
                p.mudarFiltro(
                  coluna.chave,
                  e.target.value === '' ? resto : { ...resto, contem: e.target.value },
                );
              }}
            />
          </div>
        ) : (
          <div className="linha">
            {(['de', 'ate'] as const).map((campo) => (
              <div className="campo" key={campo}>
                <label htmlFor={`${p.idMenu}-${campo}`}>{campo === 'de' ? 'De' : 'Até'}</label>
                <input
                  id={`${p.idMenu}-${campo}`}
                  type={coluna.tipo === 'data' ? 'date' : 'text'}
                  inputMode={coluna.tipo === 'data' ? undefined : 'decimal'}
                  defaultValue={
                    filtro[campo] === undefined
                      ? ''
                      : coluna.tipo === 'data'
                        ? filtro[campo]
                        : formatarDecimal(filtro[campo])
                  }
                  onChange={(e) => {
                    intervalo(campo, e.target.value);
                  }}
                />
              </div>
            ))}
          </div>
        )}
        <fieldset className="g2-valores">
          <legend>Valores</legend>
          {valores.length > 8 ? (
            <input
              type="search"
              className="g2-busca"
              aria-label="Buscar valores"
              placeholder="Buscar valores"
              value={buscaValores}
              onChange={(e) => {
                setBuscaValores(e.target.value);
              }}
            />
          ) : null}
          <label>
            <input
              type="checkbox"
              checked={filtro.valores === undefined}
              onChange={() => {
                const resto = semCampo(filtro, 'valores');
                p.mudarFiltro(coluna.chave, filtro.valores === undefined ? { ...resto, valores: [] } : resto);
              }}
            />
            Selecionar tudo
          </label>
          {visiveis.map((v) => (
            <label key={v.texto}>
              <input
                type="checkbox"
                checked={marcado(v.texto)}
                onChange={() => {
                  alternar(v.texto);
                }}
              />
              {v.texto || '(vazio)'}
              <span className="qtd">{v.contagem}</span>
            </label>
          ))}
        </fieldset>
        {coluna.agrupavel ? (
          <button
            type="button"
            className="botao botao-mini"
            onClick={() => {
              p.mudar({ ...estado, agrupar: estado.agrupar === coluna.chave ? null : coluna.chave });
              fechar();
            }}
          >
            {estado.agrupar === coluna.chave ? 'Desagrupar' : 'Agrupar por esta coluna'}
          </button>
        ) : null}
        {filtroAtivo(filtro) ? (
          <button
            type="button"
            className="link-acao"
            onClick={() => {
              p.mudarFiltro(coluna.chave, null);
            }}
          >
            Limpar filtro
          </button>
        ) : null}
      </>
    </div>
  );
}
