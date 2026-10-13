# -*- coding: utf-8 -*-
"""Verificação independente: abrir e sair sem mudar não pede confirmação; o teclado abre; salvar sem mudar não dá erro. Só imprime.
CADUX (09/10/2026): reescrito sobre a seleção que abre detalhe (verif_cad_lib.py): o alvo da linha abre a consulta e "Editar …" o
formulário; Cancelar volta à consulta. A parcela do CD-01det é só consulta (muda no Planejar safra)."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verif_cad_lib import V, out
v = V(); J = v.J
try:
    v.c.size(1440, 1100)
    for f, row in [('CD-02.dc.html#aba=operacoes', 'Trator 02'), ('CD-02.dc.html#aba=operacoes', 'TSI'), ('CD-05.dc.html', 'Sementes Vale'), ('CD-01det.dc.html', 'T1-B')]:
        v.ir(f, 1.2)
        v.edita(row); ed = v.editando(); v.btn('Cancelar')
        print(f, row, '· editável:', ed, '· cancelar sem mudar pede confirmação?', J("document.body.innerText.indexOf('Há alterações não salvas')>=0"), '· painel depois:', v.painel())
        v.fecha()
        J(f"(()=>{{const r={v.ROW(row)}; const a=r&&r.querySelector('.g2alvo'); a&&a.focus();}})()")
        print('  alvo da linha recebe o foco do teclado?', J(f"(()=>{{const r={v.ROW(row)}; const a=r&&r.querySelector('.g2alvo'); return !!a&&document.activeElement===a;}})()"),
              '· a linha fora do Tab?', J(f"(()=>{{const r={v.ROW(row)}; return !!r&&r.tabIndex<0;}})()"))
        if ed:
            v.edita(row); v.btn('Salvar'); print('  salvar sem mudar → painel:', v.painel(), '· alertas:', v.alerts() or '—'); v.fecha()
        print('  linha', v.rowtxt(row))
    print('erro JS', J("(window.__errs||[]).join(' | ')"))
finally:
    v.fim()
