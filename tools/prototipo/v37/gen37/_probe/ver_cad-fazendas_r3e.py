# -*- coding: utf-8 -*-
"""Verificador r3e · CD-01 · formulário do talhão: campos, irrigação, "Cadastrar fazenda…" (salvar e cancelar), motivo, regras."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_r3lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess()
def P(*a): print(*a, flush=True)
try:
    s.go('CD-01.dc.html'); s.clear_ls(); s.go('CD-01.dc.html')
    P('prim', s.click('Cadastrar talhão','header'))
    P('ASIDE', s.aside()[:260]); P('LABELS', s.labels(), 'faz', s.fv('faz'), s.fopts('faz'), 'sis', s.fopts('sis'))
    s.fset('t','T9'); s.fset('sis','Pivô central'); P('LABELS pivo', s.labels(), 'setor opts', s.fopts('setor'))
    s.fset('decl','50'); s.btn('Salvar'); P('ALERT sem setor', s.alerts())
    s.fset('setor','Gotejo T7'); s.btn('Salvar'); P('ALERT setor gotejo p/ pivo', s.alerts())
    s.fset('sis','Gotejo'); s.fset('setor','Bomba do Pivô 2'); s.btn('Salvar'); P('ALERT pivo p/ gotejo', s.alerts())
    s.fset('sis','Sequeiro'); P('LABELS seq', s.labels(), 'setor val', s.fv('setor'))
    s.fset('t','T1'); s.btn('Salvar'); P('ALERT T1 dup', s.alerts())
    s.fset('t','T9')
    # Cadastrar fazenda… e cancelar
    s.fset('faz','Cadastrar fazenda…'); P('ASIDE faz', s.aside()[:260])
    s.fset('nome','Lixo'); s.btn('Cancelar'); P('após cancelar sujo', s.aside()[:200])
    s.btn('Descartar alterações'); time.sleep(.3); P('após descartar', s.aside()[:120], '| t', s.fv('t'), 'decl', s.fv('decl'), 'faz', s.fv('faz'))
    s.fset('faz','Cadastrar fazenda…'); s.js("document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.3)
    P('após Esc (limpo)', s.aside()[:120], '| t', s.fv('t'))
    if 'Cadastrar fazenda' in s.aside()[:30]:
        s.js("(document.querySelector('aside[role=dialog]')).dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.3); P('após Esc no aside', s.aside()[:120], '| t', s.fv('t'))
    if 'Cadastrar fazenda' in s.aside()[:30]:
        s.click('×','aside[role=dialog]'); time.sleep(.3); P('após ×', s.aside()[:120], '| t', s.fv('t'))
    s.btn('Cancelar'); time.sleep(.3); P('cancelar talhão sujo', s.aside()[:200]); s.btn('Descartar alterações'); time.sleep(.3)
    P('aberto?', s.aberto())
    # editar T4: motivo
    s.openrow(1,'T4 Sequeiro'); P('ASIDE T4', s.aside()[:120]); P('LABELS T4', s.labels(), 'calc', s.fv('calc'))
    s.fset('decl','190'); P('LABELS T4 190', s.labels()); s.btn('Salvar'); P('ALERT motivo', s.alerts())
    P('motivos', s.fopts('motivo')); s.fset('motivo', s.fopts('motivo')[-1]); s.btn('Salvar'); time.sleep(.3)
    P('toast', s.toast()); P('T4 row', s.rowtxt(1,'T4 Sequeiro')); P('SR group', s.rowtxt(1,'Santa Rita 8'))
    # T1 abaixo do alocado; T3 muda de fazenda
    s.openrow(1,'T1 Sequeiro'); s.fset('decl','200'); s.btn('Salvar'); P('ALERT T1 200', s.alerts()); s.btn('Cancelar'); s.btn('Descartar alterações')
    s.openrow(1,'T3 Sequeiro'); s.fset('faz','Boa Vista'); s.btn('Salvar'); P('ALERT T3 BV', s.alerts()); s.btn('Cancelar'); s.btn('Descartar alterações')
    P('ERRS', [e for e in s.errs() if 'g2toast' not in e])
finally: s.close()
