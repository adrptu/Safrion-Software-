'use client';
import { useEffect, useState } from 'react';
import { COMANDOS_CADASTRO as C } from '@safrion/contracts';
import {
  acaoDoPendente,
  armazemLocal,
  lerIntencoes,
  prefixoDasIntencoes,
  type IntencaoGuardada,
} from './pendencias';
import type { EdicaoCadastro } from './EditorCadastro';
import s from './cadastro.module.css';

export function edicaoDaIntencao(g: IntencaoGuardada): EdicaoCadastro {
  const tipo =
    g.intencao.commandType === C.alterarSituacaoTalhao
      ? 'situacao'
      : g.intencao.targetType === 'farm'
        ? 'fazenda'
        : 'talhao';
  return {
    tipo,
    ...(g.intencao.expectedVersion > 0
      ? { id: g.intencao.targetId, versao: g.intencao.expectedVersion }
      : {}),
    nome: g.campos['nome'] ?? '',
    fuso: g.campos['fuso'] ?? '',
    fazenda: g.campos['fazenda'] ?? '',
    situacao: g.campos['situacao'] === 'inativo' ? 'inativo' : 'ativo',
  };
}
export function EnviosCadastro({
  usuarioId,
  organizacaoId,
  abrir,
  revisao,
}: {
  readonly usuarioId: string;
  readonly organizacaoId: string;
  readonly abrir: (g: IntencaoGuardada) => void;
  readonly revisao: number;
}) {
  const [pendentes, setPendentes] = useState<IntencaoGuardada[]>([]);
  useEffect(() => {
    const ler = () => {
      setPendentes(lerIntencoes(armazemLocal(), usuarioId, organizacaoId));
    };
    ler();
    const ouvir = (e: StorageEvent) => {
      if (e.key === null || e.key.startsWith(prefixoDasIntencoes(usuarioId, organizacaoId))) ler();
    };
    window.addEventListener('storage', ouvir);
    return () => {
      window.removeEventListener('storage', ouvir);
    };
  }, [usuarioId, organizacaoId, revisao]);
  return pendentes.length ? (
    <section className={s.aviso} aria-label="Retomar cadastros">
      <h2>Retomar cadastros</h2>
      <p>Corrija ou encerre os pedidos recusados e consulte os envios sem confirmação.</p>
      <ul>
        {pendentes.map((g) => (
          <li key={g.intencao.chave}>
            <button
              type="button"
              className="link-acao"
              onClick={() => {
                abrir(g);
              }}
            >
              {acaoDoPendente(g)} · {g.campos['nome'] || 'Talhão'}
            </button>
          </li>
        ))}
      </ul>
    </section>
  ) : null;
}
