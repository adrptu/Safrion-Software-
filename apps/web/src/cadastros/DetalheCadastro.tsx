'use client';
import type { FazendaDetalhe, OpcaoFazenda, TalhaoDetalhe, TalhaoResumo } from '@safrion/db/web';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { EditorCadastro, type EdicaoCadastro } from './EditorCadastro';
import { EnviosCadastro, edicaoDaIntencao } from './EnviosCadastro';
import { PainelCadastro } from './PainelCadastro';
import { armazemLocal, lerIntencoes, type IntencaoGuardada } from './pendencias';
import { COLUNAS_TALHAO, linhaDoTalhao, formatarAreaHa } from './lista';
import { Tabela } from '../tabela/Tabela';
import { ESTADO_VAZIO } from '../tabela/logica';
import { destinoConfirmado } from './retorno';
import s from './cadastro.module.css';

type Props = {
  readonly usuarioId: string;
  readonly organizacaoId: string;
  readonly podeEditar: boolean;
  readonly volta: string;
  readonly fazendas: readonly OpcaoFazenda[];
} & (
  | { readonly tipo: 'fazenda'; readonly registro: FazendaDetalhe; readonly talhoes: readonly TalhaoResumo[] }
  | { readonly tipo: 'talhao'; readonly registro: TalhaoDetalhe }
);
export function DetalheCadastro(p: Props) {
  const router = useRouter();
  const [editor, setEditor] = useState<{
    edicao: EdicaoCadastro;
    inicial?: IntencaoGuardada;
    chave: number;
  } | null>(null);
  const [aberto, setAberto] = useState(false);
  const [revisao, setRevisao] = useState(0);
  const [mensagem, setMensagem] = useState('');
  const volta = p.volta;
  const caminho = `${p.tipo === 'fazenda' ? '/cadastros/fazendas/' : '/cadastros/areas/'}${p.registro.id}`;
  function abrirPendente(g: IntencaoGuardada) {
    setEditor({ edicao: edicaoDaIntencao(g), inicial: g, chave: Date.now() });
    setAberto(true);
  }
  function abrir(edicao: EdicaoCadastro) {
    const [g] = lerIntencoes(armazemLocal(), p.usuarioId, p.organizacaoId);
    if (g) {
      abrirPendente(g);
      return;
    }
    setEditor({ edicao, chave: Date.now() });
    setAberto(true);
  }
  function editar() {
    abrir(
      p.tipo === 'fazenda'
        ? {
            tipo: 'fazenda',
            id: p.registro.id,
            versao: p.registro.versao,
            nome: p.registro.nome,
            fuso: p.registro.fuso,
          }
        : {
            tipo: 'talhao',
            id: p.registro.id,
            versao: p.registro.versao,
            nome: p.registro.nome,
            fazenda: p.registro.fazenda.id,
            areaDeclaradaHa: p.registro.areaDeclaradaHa,
          },
    );
  }
  function fechar() {
    setAberto(false);
    setRevisao((n) => n + 1);
    router.refresh();
  }
  const edicaoFazendaNaLinha =
    p.tipo === 'fazenda' && editor?.edicao.tipo === 'fazenda' && editor.edicao.id === p.registro.id;
  const formulario = editor ? (
    <EditorCadastro
      key={editor.chave}
      edicao={editor.edicao}
      fazendas={p.fazendas}
      usuarioId={p.usuarioId}
      organizacaoId={p.organizacaoId}
      volta={
        editor.inicial?.contexto.volta ??
        caminho +
          (volta.includes('?')
            ? `?${new URLSearchParams({ volta: volta.split('?')[1] ?? '' }).toString()}`
            : '')
      }
      {...(editor.inicial ? { inicial: editor.inicial } : {})}
      cancelar={fechar}
      confirmado={(_, g) => {
        setAberto(false);
        setRevisao((n) => n + 1);
        setMensagem('Cadastro atualizado.');
        if (
          g.intencao.targetId !== p.registro.id ||
          g.intencao.targetType !== (p.tipo === 'fazenda' ? 'farm' : 'field')
        ) {
          router.push(destinoConfirmado(g));
        }
        router.refresh();
      }}
    />
  ) : null;
  return (
    <div className={s.detalhe}>
      {!p.podeEditar ? (
        <p className={s.leitura}>Somente consulta · quem cadastra: Gerente</p>
      ) : (
        <>
          <div className={s.acoes}>
            {p.tipo === 'fazenda' ? (
              <button
                className="botao botao-primario"
                type="button"
                onClick={() => {
                  abrir({ tipo: 'talhao', fazenda: p.registro.id });
                }}
              >
                Novo talhão nesta fazenda
              </button>
            ) : p.registro.situacao === 'ativo' ? (
              <button className="botao botao-primario" type="button" onClick={editar}>
                Editar talhão
              </button>
            ) : (
              <button
                className="botao botao-primario"
                type="button"
                onClick={() => {
                  abrir({
                    tipo: 'situacao',
                    id: p.registro.id,
                    versao: p.registro.versao,
                    nome: p.registro.nome,
                    situacao: 'ativo',
                  });
                }}
              >
                Reativar talhão
              </button>
            )}
            {p.tipo === 'talhao' && p.registro.situacao === 'ativo' ? (
              <details>
                <summary>Mais ações</summary>
                <button
                  className="link-acao"
                  type="button"
                  onClick={() => {
                    abrir({
                      tipo: 'situacao',
                      id: p.registro.id,
                      versao: p.registro.versao,
                      nome: p.registro.nome,
                      situacao: 'inativo',
                    });
                  }}
                >
                  Inativar talhão
                </button>
              </details>
            ) : null}
          </div>
          <EnviosCadastro
            usuarioId={p.usuarioId}
            organizacaoId={p.organizacaoId}
            abrir={abrirPendente}
            revisao={revisao}
          />
        </>
      )}
      {mensagem ? <p role="status">{mensagem}</p> : null}
      <section className="bloco" aria-labelledby="identificacao">
        <div className="bloco-cabecalho">
          <h2 id="identificacao">Identificação</h2>
          {p.tipo === 'fazenda' && p.podeEditar && !(aberto && edicaoFazendaNaLinha) ? (
            <button type="button" className="link-acao" onClick={editar}>
              Editar nome e fuso
            </button>
          ) : null}
        </div>
        <div className="bloco-corpo">
          {aberto && edicaoFazendaNaLinha ? (
            formulario
          ) : (
            <dl className="dados">
              <div>
                <dt>Nome</dt>
                <dd>{p.registro.nome}</dd>
              </div>
              {p.tipo === 'fazenda' ? (
                <div>
                  <dt>Fuso horário</dt>
                  <dd>{p.registro.fuso}</dd>
                </div>
              ) : (
                <>
                  <div>
                    <dt>Fazenda</dt>
                    <dd>
                      <Link
                        href={`/cadastros/fazendas/${p.registro.fazenda.id}?${new URLSearchParams({ volta: new URLSearchParams(volta.split('?')[1] ?? '').toString() }).toString()}`}
                      >
                        {p.registro.fazenda.nome}
                      </Link>
                    </dd>
                  </div>
                  <div>
                    <dt>Área de referência</dt>
                    <dd>
                      {formatarAreaHa(p.registro.areaReferenciaHa)} ha ({p.registro.origemArea})
                    </dd>
                  </div>
                </>
              )}
              <div>
                <dt>Versão</dt>
                <dd>{p.registro.versao}</dd>
              </div>
            </dl>
          )}
        </div>
      </section>
      {p.tipo === 'talhao' ? (
        <section className="bloco" aria-labelledby="limite">
          <h2 id="limite">Limite</h2>
          <div className="bloco-corpo">
            <p>Sem limite no mapa</p>
          </div>
        </section>
      ) : (
        <section aria-label="Talhões da fazenda">
          <h2>Talhões</h2>
          <p>
            {p.registro.talhoesAtivos} ativos · {formatarAreaHa(p.registro.areaAtivaHa)} ha de referência dos
            talhões ativos
          </p>
          <Tabela
            rotulo="Talhões"
            colunas={COLUNAS_TALHAO}
            linhas={p.talhoes.map((t) => linhaDoTalhao(t, `fazenda=${p.registro.id}`, p.registro.fuso))}
            estadoInicial={ESTADO_VAZIO}
            nome={{ singular: 'talhão', plural: 'talhões' }}
            vazio="Nenhum talhão nesta fazenda."
          />
        </section>
      )}
      <PainelCadastro
        aberto={aberto && !edicaoFazendaNaLinha}
        titulo={editor?.edicao.tipo === 'fazenda' ? 'Fazenda' : 'Talhão'}
        fechar={fechar}
      >
        {!edicaoFazendaNaLinha ? formulario : null}
      </PainelCadastro>
    </div>
  );
}
