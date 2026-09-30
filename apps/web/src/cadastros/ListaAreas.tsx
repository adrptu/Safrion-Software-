'use client';

import type { FazendaResumo, TalhaoResumo } from '@safrion/db/web';
import Link from 'next/link';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useId, useTransition } from 'react';

import { Tabela } from '../tabela/Tabela';
import { estadoDaUrl, type EstadoG2 } from '../tabela/logica';
import {
  COLUNAS_TALHAO,
  consultaComEstadoTabela,
  consultaDeRetorno,
  filtrosDaLista,
  formatarAreaHa,
  gruposDeFazenda,
  hrefComRetorno,
  linhaDoTalhao,
} from './lista';
import estilos from './lista.module.css';

export interface PropsListaAreas {
  readonly fazendas: readonly FazendaResumo[];
  readonly talhoes: readonly TalhaoResumo[];
  readonly podeEditar: boolean;
  readonly onNovoTalhao: (fazenda?: string) => void;
}

/** Lista de entidades CAD01: o cabeçalho da página contém a única ação primária. */
export function ListaAreas({ fazendas, talhoes, podeEditar, onNovoTalhao }: PropsListaAreas) {
  const id = useId();
  const router = useRouter();
  const pathname = usePathname();
  const busca = useSearchParams();
  const [atualizando, iniciarTransicao] = useTransition();
  const consulta = new URLSearchParams(busca.toString());
  const filtros = filtrosDaLista(consulta);
  const estado = estadoDaUrl(consulta, COLUNAS_TALHAO);
  const volta = consultaDeRetorno(consulta);
  const grupos = gruposDeFazenda(fazendas, talhoes, filtros);
  const temFiltro =
    filtros.fazenda !== '' ||
    filtros.situacao !== '' ||
    estado.busca !== '' ||
    Object.keys(estado.filtros).length > 0;

  function navegar(nova: URLSearchParams) {
    const texto = nova.toString();
    iniciarTransicao(() => {
      router.replace(texto === '' ? pathname : `${pathname}?${texto}`, { scroll: false });
    });
  }

  function mudarFiltro(chave: 'fazenda' | 'situacao', valor: string) {
    const nova = new URLSearchParams(consulta);
    if (valor === '') nova.delete(chave);
    else nova.set(chave, valor);
    navegar(nova);
  }

  function mudarTabela(novo: EstadoG2) {
    const texto = consultaComEstadoTabela(consulta, novo).toString();
    window.history.replaceState(null, '', texto === '' ? pathname : `${pathname}?${texto}`);
  }

  return (
    <div className={estilos['lista']} aria-busy={atualizando}>
      <div className={estilos['filtros']} aria-label="Filtros de fazendas e talhões">
        <div className="campo">
          <label htmlFor={`${id}-fazenda`}>Fazenda</label>
          <select
            id={`${id}-fazenda`}
            value={filtros.fazenda}
            onChange={(e) => {
              mudarFiltro('fazenda', e.target.value);
            }}
          >
            <option value="">Todas as fazendas</option>
            {filtros.fazenda && !fazendas.some((f) => f.id === filtros.fazenda) ? (
              <option value={filtros.fazenda}>Fazenda não encontrada</option>
            ) : null}
            {fazendas.map((f) => (
              <option key={f.id} value={f.id}>
                {f.nome}
              </option>
            ))}
          </select>
        </div>
        <div className="campo">
          <label htmlFor={`${id}-situacao`}>Situação do talhão</label>
          <select
            id={`${id}-situacao`}
            value={filtros.situacao}
            onChange={(e) => {
              mudarFiltro('situacao', e.target.value);
            }}
          >
            <option value="">Todas as situações</option>
            <option value="ativo">Ativos</option>
            <option value="inativo">Inativos</option>
          </select>
        </div>
        {temFiltro ? (
          <button
            type="button"
            className="link-acao"
            onClick={() => {
              navegar(new URLSearchParams());
            }}
          >
            Limpar filtros
          </button>
        ) : null}
      </div>
      {!podeEditar ? <p className={estilos['ajuda']}>Somente consulta · quem cadastra: Gerente</p> : null}
      <p className={estilos['ajuda']} role="status">
        {atualizando
          ? 'Atualizando talhões…'
          : 'Totais por fazenda: talhões ativos e sua área de referência, independentemente dos filtros.'}
      </p>
      {grupos.length === 0 ? (
        <div className={estilos['vazio']}>
          <p>{temFiltro ? 'Nenhuma fazenda corresponde aos filtros.' : 'Nenhum talhão cadastrado.'}</p>
          {podeEditar && !temFiltro ? (
            <button
              type="button"
              className="link-acao"
              onClick={() => {
                onNovoTalhao();
              }}
            >
              Novo talhão
            </button>
          ) : null}
        </div>
      ) : (
        grupos.map(({ fazenda, talhoes: doGrupo }) => (
          <section
            key={fazenda.id}
            className={['bloco', estilos['grupo']].join(' ')}
            aria-labelledby={`${id}-${fazenda.id}`}
          >
            <header className={estilos['cabecalho']}>
              <h2 id={`${id}-${fazenda.id}`}>
                <Link href={hrefComRetorno(`/cadastros/fazendas/${encodeURIComponent(fazenda.id)}`, volta)}>
                  {fazenda.nome}
                </Link>
              </h2>
              <p className={estilos['resumo']}>
                {fazenda.talhoesAtivos} {fazenda.talhoesAtivos === 1 ? 'talhão ativo' : 'talhões ativos'}
                {' · '}
                {formatarAreaHa(fazenda.areaAtivaHa)} ha de referência
              </p>
            </header>
            {doGrupo.length === 0 ? (
              <div className={estilos['vazio']}>
                <p>
                  {filtros.situacao === ''
                    ? 'Nenhum talhão cadastrado.'
                    : `Nenhum talhão ${filtros.situacao}.`}
                </p>
                {podeEditar ? (
                  <button
                    type="button"
                    className="link-acao"
                    onClick={() => {
                      onNovoTalhao(fazenda.id);
                    }}
                  >
                    Novo talhão nesta fazenda
                  </button>
                ) : null}
              </div>
            ) : (
              <Tabela
                rotulo={`Talhões de ${fazenda.nome}`}
                colunas={COLUNAS_TALHAO}
                linhas={doGrupo.map((t) => linhaDoTalhao(t, volta, fazenda.fuso))}
                estadoInicial={estado}
                estado={estado}
                aoMudarEstado={mudarTabela}
                nome={{ singular: 'talhão', plural: 'talhões' }}
                vazio="Nenhum talhão cadastrado."
              />
            )}
          </section>
        ))
      )}
    </div>
  );
}
