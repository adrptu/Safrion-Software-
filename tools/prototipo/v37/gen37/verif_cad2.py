# -*- coding: utf-8 -*-
"""Verificação independente (CD-02, CD-01det): cenários além dos testes do implementador. Só imprime; quem lê confere.
CADUX (09/10/2026): reescrito sobre a seleção que abre detalhe (verif_cad_lib.py): o rendimento abre em consulta e "Editar rendimento"
abre o formulário; "+ Criar rendimento" no cabeçalho, com a operação escolhida no mestre (em "Todas", vazia). No CD-01det as parcelas
são só consulta desde antes da CADUX (mudam no Planejar safra): a parte que editava a área e cadastrava parcela virou a conferência
de que o painel da parcela não tem campo editável e diz a origem."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verif_cad_lib import V, out
PROBE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_probe')
v = V(); J = v.J
try:
    v.c.size(1440, 1100)
    # ===================== CD-02 =====================
    v.ir('CD-02.dc.html#aba=operacoes')
    out('CD-02 erro JS', J("(window.__errs||[]).join(' | ')"))
    out('altura necessária', v.altura())
    out('cabeçalhos g_rend', v.cabecalhos())
    out('linhas g_rend', v.linhas())
    v.c.shot(os.path.join(PROBE, 'verif_cd02_lista.png'))
    # Informado → Largura × velocidade (rendimento do tratamento de sementes, conjunto escrito à mão)
    v.edita('TSI'); out('TS painel', v.painel()); out('TS modo', v.fv('modo')); out('TS rend', v.fv('rend'))
    v.fset('modo', 'Largura × velocidade'); out('rend_c ao trocar', v.fv('rend_c')); v.btn('Salvar'); out('TS sem L/V/E', v.alerts())
    v.fset('larg', '2'); v.fset('vel', '3'); v.fset('efic', '50'); out('rend_c 2×3÷10×50%', v.fv('rend_c')); v.btn('Salvar')
    out('TS salvo: painel', v.painel()); out('  toast', v.toast()); v.fecha(); out('  linha', v.rowtxt('TSI'))
    # Informado vazio
    v.edita('Colhedora'); v.fset('modo', 'Informado'); v.fset('rend', ''); v.btn('Salvar'); out('Informado vazio', v.alerts()); v.fecha()
    # novo rendimento em "Todas as operações": a operação vem vazia (X01)
    r = v.clk('+ Criar rendimento'); out('novo rendimento', r); out('  rótulos', v.labels())
    out('  operação', v.fv('op')); out('  modo padrão', v.fv('modo')); out('  rend_c vazio', v.fv('rend_c')); out('  custo_c vazio', v.fv('custo_c'))
    v.btn('Salvar'); out('  vazio', v.alerts())
    ops = J("[...document.querySelector('aside[role=dialog] select[id$=\"_op\"]').options].map(o=>o.value)") or ['']; out('  ops', ops)
    v.fset('op', ops[1] if len(ops) > 1 else ops[0]); v.fset('cjid', 'Outro (descrever)'); v.fset('conj', 'Trator X + Grade 20'); v.fset('larg', '4'); v.fset('vel', '7'); v.fset('efic', '80')
    v.fset('maq', '150'); v.fset('pess', '1'); v.fset('pess_rs', '35'); v.fset('fonte', 'Medição local'); v.fset('vig', '2027-06-30')
    out('  rend_c', v.fv('rend_c')); out('  custo_c', v.fv('custo_c'))
    v.btn('Salvar'); out('  painel', v.painel()); out('  alertas', v.alerts()); out('  toast', v.toast()); v.fecha(); out('  linha', v.rowtxt('Trator X + Grade 20'))
    # ===================== CD-01det =====================
    v.ir('CD-01det.dc.html')
    out('CD-01det erro JS', J("(window.__errs||[]).join(' | ')"))
    out('linhas', v.linhas())
    v.abre('T1-A'); out('T1-A painel', v.painel()); out('  editável?', v.editando()); out('  origem', (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '').replace('\n', ' ')[:300]); v.fecha()
    out('"Planejar T1 na safra"', J("(()=>{const a=[...document.querySelectorAll('main a')].find(a=>a.innerText.trim().startsWith('Planejar T1')); return a?a.getAttribute('href'):null;})()"))
finally:
    v.fim()
