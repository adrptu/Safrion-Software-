# -*- coding: utf-8 -*-
"""Verificador 7 · CD-01det: hash direto, seletor e URL, voltar, editar no detalhe, painel do polígono (Esc, desenho com motivo), inativar, volta à lista."""
import importlib.util, os, sys, time, json
H=os.path.dirname(os.path.abspath(__file__)); sp=importlib.util.spec_from_file_location('vl',os.path.join(H,'ver_cad-fazendas_lib.py')); L=importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
s=L.Sess(); chk=L.chk
def hd(): return s.head()
try:
    s.go('CD-01det.dc.html#talhao=P1')
    chk('1 #talhao=P1 abre o P1 (seletor, crumb, estado, primária)', s.js("document.querySelector('header select').value")=='P1' and 'P1 · 95 ha' in hd() and 'Planejar P1 na safra' in hd() and 'Polígono validado' in hd(), hd())
    print('   P1 parcelas', s.rows(1)); print('   P1 talhão', s.rows(0))
    # 2 seletor muda URL e sobrevive a recarregar
    s.js(f"({L.SETV})('header select','T4')"); time.sleep(.4); h=s.js("location.hash")
    s.go('CD-01det.dc.html'+h); chk('2 seletor grava #talhao e recarregar mantém o T4', h=='#talhao=T4' and s.js("document.querySelector('header select').value")=='T4', [h, hd()[:120]])
    # 3 voltar
    back=s.js("(()=>{const a=[...document.querySelectorAll('header a')].map(a=>[a.innerText.trim(),a.getAttribute('aria-label'),a.getAttribute('href')]); return a;})()")
    chk('3 voltar e crumb levam ao CD-01', any((x[2] or '').startswith('CD-01.dc.html') for x in back), back)
    # 4 editar T2 no detalhe
    s.js(f"({L.SETV})('header select','T2')"); time.sleep(.4); s.openrow(0,'Santa Rita'); t=s.aside()[:40]
    s.fset('decl','310'); s.fset('motivo','APP ou reserva'); s.btn('Salvar'); time.sleep(.3)
    chk('4 editar no detalhe: crumb e resumo da safra atualizam', 'T2 · 310 ha' in hd() and '298 de 310 ha' in ' '.join(s.rows(1) or []) and '12 ha livres' in ' '.join(s.rows(1) or []), [t, hd()[:80], s.rows(1)])
    # 5 painel do polígono: desenho do B1 com diferença > 1 %, Esc avisa
    s.js(f"({L.SETV})('header select','B1')"); time.sleep(.4)
    print('   B1 corpo', s.js("document.querySelector('main').innerText.replace(/\\s+/g,' ').slice(0,700)"))
    s.click('Definir polígono do B1','header'); s.click('Desenhar no mapa','aside'); s.click('Gerar prévia','aside'); a=s.aside()
    s.js("document.querySelector('aside[role=dialog]').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.3); a2=s.aside()
    chk('5 prévia do desenho pede motivo e Esc avisa alterações não salvas', 'Motivo da diferença' in a and 'Há alterações não salvas' in a2, [a[:400], a2[-120:]])
    s.click('Continuar editando','aside'); s.js(f"({L.SETV})('#pg_mot','Carreador ou estrada')"); time.sleep(.2); s.click('Salvar polígono','aside'); time.sleep(.3)
    chk('6 B1 salvo com motivo: v1, diferença com motivo, primária muda', not s.aberto() and 'v1' in ' '.join(s.rows(0) or []) and 'Carreador ou estrada' in ' '.join(s.rows(0) or []), [s.rows(0), hd(), s.toast()])
    # 7 inativar B1 no detalhe
    s.openrow(0,'Boa Vista'); s.fset('sit','Inativo'); s.btn('Salvar'); time.sleep(.3)
    chk('7 inativo: chip no cabeçalho, sem "Dividir em parcelas"', 'Inativo desde' in hd() and 'Dividir em parcelas' not in s.body(), [hd(), s.errs()])
    print('   primária com inativo:', s.js("[...document.querySelectorAll('header button, header a')].map(e=>e.innerText.trim()).filter(Boolean)"))
    # 8 volta à lista: T2 e B1 como salvos no detalhe
    s.go('CD-01.dc.html'); t2=s.rowtxt(1,'T2 Sequeiro'); b1=s.rowtxt(1,'B1')
    chk('8 lista reflete o detalhe (T2 310 ha com motivo; B1 inativo com polígono v1)', '310,0 ha' in (t2 or '') and 'APP ou reserva' in (t2 or '') and 'Inativo' in (b1 or '') and 'v1' in (b1 or ''), [t2, b1, hd()])
    s.click('Importar geometrias'); print('   toast importar:', s.toast())
    print('ERRS', [e for e in s.errs() if 'g2toast' not in e], 'OVF', s.overflow())
finally: s.close()
print('RES', sum(L.res), '/', len(L.res))
