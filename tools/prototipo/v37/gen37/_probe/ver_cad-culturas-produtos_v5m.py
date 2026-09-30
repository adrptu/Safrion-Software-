# -*- coding: utf-8 -*-
"""v5 · auxiliar: clique real de mouse (CDP Input) no centro de um elemento achado por JS."""
import time, json
def mclick_xy(v,x,y):
    for t in ('mouseMoved','mousePressed','mouseReleased'):
        v.c.call('Input.dispatchMouseEvent',{'type':t,'x':x,'y':y,'button':'left','clickCount':1})
    time.sleep(.45)
def mclick(v,expr):
    """expr: expressão JS que devolve o elemento; rola até ele e clica no centro."""
    r=v.J(f"(()=>{{const e=({expr}); if(!e) return null; e.scrollIntoView({{block:'center'}}); const b=e.getBoundingClientRect(); return [b.left+b.width/2,b.top+b.height/2];}})()")
    if not r: return 'sem elemento'
    time.sleep(.2); mclick_xy(v,r[0],r[1]); return 'ok'
def cell(v,rowtxt,ci,ti=None):
    return f"(({v.ROW(rowtxt,ti)})||{{querySelectorAll:()=>[]}}).querySelectorAll('[role=cell]')[{ci}]"
