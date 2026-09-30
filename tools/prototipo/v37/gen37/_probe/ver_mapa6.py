# -*- coding: utf-8 -*-
"""Verificador 6: IN-02 (linhas, destinos, lote e estado do cabeçalho), IN-03 (Caio no Responsável, semana, cabeçalho), IN-01."""
import json, time
from ver_mapa_lib import Sess
s=Sess(1440,900)
try:
    s.go('IN-02.dc.html')
    rows=s.js("[...document.querySelectorAll('[role=row].g2ed')].map(r=>[r.getAttribute('data-id')||'',r.innerText.replace(/\\n/g,' | ').slice(0,160),[...r.querySelectorAll('a')].map(a=>a.getAttribute('href'))])")
    for r in rows: print('IN-02 linha:',r)
    print('HEAD:',s.head().split(' | ')[-1])
    # seleciona todas as linhas e aprova em lote
    cb=s.js("[...document.querySelectorAll('[role=row].g2ed input[type=checkbox]')].length"); print('checkboxes:',cb)
    s.js("[...document.querySelectorAll('[role=row].g2ed input[type=checkbox]')].forEach(i=>i.click())"); time.sleep(.4)
    print('lote:',s.click('Aprovar selecionados')); time.sleep(.3)
    print('HEAD após lote:',s.head().split(' | ')[-1])
    print('situação:',s.js("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0]+' → '+r.innerText.split('\\n').slice(-1)[0])"))
    print('erros:',[e for e in s.errs() if 'g2toast' not in e])
    s.c.size(1440,1100); s.go('IN-03.dc.html')
    print('IN-03 HEAD:',s.head().split(' | ')[-2:])
    print('semana:',s.js("[...document.querySelectorAll('div')].filter(d=>/^\\d\\d\\/09 · /.test(d.innerText)&&d.children.length>1&&d.firstElementChild.innerText.match(/^\\d\\d\\/09/)).slice(0,5).map(d=>d.innerText.replace(/\\n/g,' / '))"))
    rows=s.js("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\n/g,' | ').slice(0,200))")
    for r in rows: print('IN-03 linha:',r)
    # abre a linha do conflito e confere o Responsável
    s.js("[...document.querySelectorAll('[role=row].g2ed')].find(r=>r.innerText.includes('OS-0423')).click()"); time.sleep(.5)
    print('form resp:',s.js("(()=>{const sel=[...document.querySelectorAll('select')].find(x=>[...x.options].some(o=>o.text==='Caio')); return sel?[sel.value,[...sel.options].map(o=>o.text)]:null;})()"))
    s.shot('ver_in03_form.png')
    print('erros:',[e for e in s.errs() if 'g2toast' not in e])
    s.c.size(1440,930); s.go('IN-01.dc.html')
    for r in s.js("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.replace(/\\n/g,' | ').slice(0,200))"): print('IN-01 linha:',r)
finally:
    s.close()
