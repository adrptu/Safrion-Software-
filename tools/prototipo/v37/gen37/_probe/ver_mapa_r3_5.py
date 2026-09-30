# -*- coding: utf-8 -*-
"""Verificador r3-5: IN-03 · largura da tabela de Compromissos, botões da coluna Abrir, Responsável (Caio), atalhos, fim da tela."""
import time, json, base64, os
from ver_mapa_lib import Sess, HERE
s=Sess(1440,1100)
try:
    s.go('IN-03.dc.html')
    r=s.J("""(()=>{const g=document.querySelector('[role=grid],[role=table],table'); const p=g.parentElement; const cs=getComputedStyle(p);
      const pr=p.getBoundingClientRect(), gr=g.getBoundingClientRect();
      const bts=[...g.querySelectorAll('a,button')].filter(b=>b.getClientRects().length).map(b=>{const r=b.getBoundingClientRect(); return b.innerText.trim()+' ['+Math.round(r.left)+'-'+Math.round(r.right)+'] '+(b.getAttribute('href')||'');});
      return {p_ovx:cs.overflowX, p_rect:[Math.round(pr.left),Math.round(pr.right)], g_rect:[Math.round(gr.left),Math.round(gr.right)], g_sw:g.scrollWidth, p_cw:p.clientWidth, p_sw:p.scrollWidth, bts};})()""")
    print(json.dumps(r,ensure_ascii=False,indent=0))
    d=s.c.call('Page.captureScreenshot',{'format':'png','clip':{'x':1100,'y':520,'width':340,'height':420,'scale':2}})
    open(os.path.join(HERE,'ver_mapa_r3_in03_borda.png'),'wb').write(base64.b64decode(d['data']))
    # fim da tela
    last=s.J("""(()=>{const secs=[...document.querySelectorAll('section,[role=region]')].filter(e=>e.getClientRects().length); const r=secs.map(e=>[ (e.innerText||'').trim().slice(0,30), Math.round(e.getBoundingClientRect().bottom)]); return r.slice(-4);})()""")
    print('últimos blocos:',last,'sh',s.J("document.documentElement.scrollHeight"))
    # linha do conflito: abre formulário, Responsável tem Caio?
    print(s.J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(x=>/Resolver conflito da OS-0423/.test(x.innerText)); if(!r) return 'sem linha'; r.click(); return 'ok';})()""")); time.sleep(.5)
    print('form:',s.J("(()=>{const f=document.querySelector('[role=dialog],aside,form'); return f?f.innerText.replace(/\\n/g,' / ').slice(0,600):'sem form';})()"))
    print('opções responsável:',s.J("[...document.querySelectorAll('select')].map(x=>(x.getAttribute('aria-label')||x.name||'?')+'='+x.value+' ['+[...x.options].map(o=>o.value).join('|')+']')"))
    s.shot('r3_in03_form')
    print('errs',s.errs())
finally:
    s.close()
