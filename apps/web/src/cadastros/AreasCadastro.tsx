'use client';
import type { FazendaResumo, TalhaoResumo } from '@safrion/db/web';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { EditorCadastro, type EdicaoCadastro } from './EditorCadastro';
import { EnviosCadastro, edicaoDaIntencao } from './EnviosCadastro';
import { ListaAreas } from './ListaAreas';
import { PainelCadastro } from './PainelCadastro';
import { armazemLocal, lerIntencoes, type IntencaoGuardada } from './pendencias';
import { destinoConfirmado } from './retorno';
import s from './cadastro.module.css';

export function AreasCadastro({
  fazendas,
  talhoes,
  podeEditar,
  usuarioId,
  organizacaoId,
}: {
  readonly fazendas: readonly FazendaResumo[];
  readonly talhoes: readonly TalhaoResumo[];
  readonly podeEditar: boolean;
  readonly usuarioId: string;
  readonly organizacaoId: string;
}) {
  const router = useRouter();
  const [painel, setPainel] = useState<{
    edicao: EdicaoCadastro;
    inicial?: IntencaoGuardada;
    volta: string;
    chave: number;
  } | null>(null);
  const [aberto, setAberto] = useState(false);
  const [revisao, setRevisao] = useState(0);
  const [aviso, setAviso] = useState('');
  function abrir(g: IntencaoGuardada) {
    setPainel({ edicao: edicaoDaIntencao(g), inicial: g, volta: g.contexto.volta, chave: Date.now() });
    setAberto(true);
  }
  function novo(fazenda?: string) {
    const [g] = lerIntencoes(armazemLocal(), usuarioId, organizacaoId);
    if (g) {
      setAviso('Confira o envio pendente antes de começar outro cadastro.');
      abrir(g);
      return;
    }
    // O estado da tabela está na URL; abrir painel não cria uma entrada de histórico.
    const volta = `/cadastros/areas${window.location.search}`;
    setPainel({ edicao: { tipo: 'talhao', ...(fazenda ? { fazenda } : {}) }, volta, chave: Date.now() });
    setAberto(true);
  }
  function fechar() {
    setAberto(false);
    setRevisao((n) => n + 1);
    router.refresh();
  }
  return (
    <>
      {podeEditar ? (
        <div className={s.primaria}>
          <button
            type="button"
            className="botao botao-primario"
            onClick={() => {
              novo();
            }}
          >
            Novo talhão
          </button>
        </div>
      ) : null}
      {aviso ? <p role="status">{aviso}</p> : null}
      {podeEditar ? (
        <EnviosCadastro usuarioId={usuarioId} organizacaoId={organizacaoId} abrir={abrir} revisao={revisao} />
      ) : null}
      <ListaAreas fazendas={fazendas} talhoes={talhoes} podeEditar={podeEditar} onNovoTalhao={novo} />
      <PainelCadastro
        aberto={aberto}
        titulo={painel?.edicao.tipo === 'fazenda' ? 'Fazenda' : 'Talhão'}
        fechar={fechar}
      >
        {painel ? (
          <EditorCadastro
            key={painel.chave}
            edicao={painel.edicao}
            fazendas={fazendas}
            usuarioId={usuarioId}
            organizacaoId={organizacaoId}
            volta={painel.volta}
            {...(painel.inicial ? { inicial: painel.inicial } : {})}
            cancelar={fechar}
            confirmado={(_, g) => {
              setAberto(false);
              setRevisao((n) => n + 1);
              router.push(destinoConfirmado(g));
              router.refresh();
            }}
          />
        ) : null}
      </PainelCadastro>
    </>
  );
}
