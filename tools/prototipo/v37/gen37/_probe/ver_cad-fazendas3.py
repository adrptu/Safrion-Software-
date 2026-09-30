# -*- coding: utf-8 -*-
"""Verificador 3 · CD-01 · formulário do talhão: campos, pivô/setor, duplicado, motivo, mudar de fazenda, mapa, "Cadastrar fazenda…" cancelado."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess(); chk=L.chk
try:
    s.go('CD-01.dc.html')
    # 1 primária abre talhão novo
    s.click('Cadastrar talhão','header'); lb=s.labels(); a=s.aside()
    chk('1 primária abre "Cadastrar talhão" com fazenda da lista + Cadastrar fazenda…', s.aberto() and s.fopts('faz')==['Santa Rita','Boa Vista','Cadastrar fazenda…'] and 'Pivô ou setor de irrigação' not in lb, [a[:200], lb, s.fopts('faz'), s.fv('faz'), s.fv('sit')])
    # 2 pivô exige setor e coerência
    s.fset('t','t1'); s.fset('sis','Pivô central'); lb=s.labels(); s.fset('decl','50'); s.btn('Salvar'); al=s.alerts()
    chk('2 irrigado mostra e exige pivô/setor; ID repetido barrado', 'Pivô ou setor de irrigação' in lb and 'Escolha o pivô ou setor' in al and 'Já existe t1 na Santa Rita' in al, [lb, al])
    s.fset('setor','Gotejo T7'); s.btn('Salvar'); al=s.alerts()
    chk('3 pivô com setor de gotejo barrado', 'Escolha a bomba de um pivô' in al, al)
    s.fset('sis','Sequeiro'); lb=s.labels()
    chk('3b volta a Sequeiro esconde o setor', 'Pivô ou setor de irrigação' not in lb, lb)
    # 4 "Cadastrar fazenda…" e cancelar volta ao talhão com o preenchido
    s.fset('t','Z5'); s.fset('decl','33'); s.fset('faz','Cadastrar fazenda…'); a=s.aside()
    s.fset('nome','Rascunho'); s.btn('Cancelar'); w=s.alerts(); s.btn('Descartar alterações'); time.sleep(.2)
    chk('4 cancelar o cadastro de fazenda volta ao talhão sem perder nada', s.aberto() and s.fv('t')=='Z5' and s.fv('decl')=='33' and s.fv('faz')=='Santa Rita', [a[:120], w, s.aside()[:120], s.fv('t'), s.fv('decl'), s.fv('faz')])
    s.btn('Cancelar'); s.btn('Descartar alterações')
    # 5 editar T2: cultivável 310 → motivo pedido; salvar com motivo
    s.openrow(1,'T2 Sequeiro'); s.fset('decl','310'); lb=s.labels(); s.btn('Salvar'); al=s.alerts()
    chk('5 diferença > 1 % mostra e exige motivo', 'Motivo da diferença' in lb and 'informe o motivo' in al, [lb, al])
    s.fset('motivo','Carreador ou estrada'); s.btn('Salvar'); time.sleep(.3)
    t2=s.rowtxt(1,'T2 Sequeiro'); sr=s.rowtxt(1,'Santa Rita 8'); fz=s.rowtxt(0,'Santa Rita')
    chk('6 T2 salvo: diferença com motivo, subtotal e área cultivável da fazenda', not s.aberto() and 'Carreador ou estrada' in (t2 or '') and '1.177,0 ha' in (sr or '') and '1.177,0 ha' in (fz or ''), [t2, sr, fz])
    # 7 mapa: clicar no T3 abre o formulário do T3
    s.js("(()=>{const p=[...document.querySelectorAll('svg polygon')][3]; p.dispatchEvent(new MouseEvent('click',{bubbles:true}));})()"); time.sleep(.4)
    a=s.aside(); chk('7 clique no mapa (T3) abre o formulário do T3', s.aberto() and s.fv('t')=='T3', [a[:80], s.fv('t')])
    # 8 mudar T3 de fazenda com parcelas na safra aberta da Santa Rita
    s.fset('faz','Boa Vista'); s.btn('Salvar'); time.sleep(.3); al=s.alerts()
    bv=s.rowtxt(1,'Boa Vista'); t3=s.rowtxt(1,'T3 Sequeiro'); rows=s.rows(1)
    chk('8 T3 (com parcela na Safra 2026/27 da Santa Rita) não deveria mudar de fazenda sem aviso', s.aberto() and al, [al, s.toast(), bv, t3, rows])
    fill=s.js("(()=>{const p=[...document.querySelectorAll('svg polygon')][3]; return p.getAttribute('fill');})()")
    print('mapa T3 fill', fill, 'título mapa', s.js("[...document.querySelectorAll('main h2, main h3')].map(e=>e.innerText)"))
    s.shot('ver_cadf_t3_movido.png',full=True)
    print('ERRS', s.errs(), 'OVF', s.overflow())
finally: s.close()
print('RES', sum(L.res), '/', len(L.res))
