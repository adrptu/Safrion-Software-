'use client';
import { useEffect, useId, useRef, type ReactNode } from 'react';
import s from './cadastro.module.css';

/** Dialog nativo: foco preso no painel, Escape fecha e devolve foco ao disparador. */
export function PainelCadastro({
  aberto,
  titulo,
  fechar,
  children,
}: {
  readonly aberto: boolean;
  readonly titulo: string;
  readonly fechar: () => void;
  readonly children: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const id = useId();
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (aberto && !el.open) el.showModal();
    else if (!aberto && el.open) el.close();
  }, [aberto]);
  return (
    <dialog
      ref={ref}
      className={s.painel}
      aria-labelledby={id}
      onCancel={(e) => {
        e.preventDefault();
        fechar();
      }}
    >
      <header className={s.cabeca}>
        <h2 id={id}>{titulo}</h2>
        <button type="button" className="botao" onClick={fechar} aria-label="Fechar painel">
          Fechar
        </button>
      </header>
      <div className={s.corpo}>{children}</div>
    </dialog>
  );
}
