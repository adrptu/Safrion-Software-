# -*- coding: utf-8 -*-
"""Apoio dos testes MUX-F0, MUX-F1 e MUX-F2 do Mapa (IN-04): abrir a tela, esperar a condição observável (AGENTS §3.6), trocar fazenda e camada
como a pessoa (filtro do topo e barra das funções), achar o talhão na tela e ler o cartão. Só leitura do DOM; nenhum atalho de estado."""
import json, time

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)

def espera(J, js, ate=8.0):
    """Espera a condição observável com limite explícito; devolve True/False (a falha no limite vira FALHA no teste que a usa)."""
    t0 = time.time()
    while time.time() - t0 < ate:
        try:
            if J(js): return True
        except Exception: pass
        time.sleep(.1)
    return False

LG_PRONTO = "!!(window.__LGI&&window.__LGI.pronto&&document.querySelectorAll('[data-mux-grupo=LG] [data-talhao]').length===23&&document.querySelector('[data-mux-grupo=LG] [data-talhao]').getAttribute('aria-label').length>20)"
SR_PRONTO = "document.querySelectorAll('svg[data-mux-grupo=SR] [data-talhao]').length===8"

def abre(c, url, larg=1440, alt=900, toque=False, faz=None, espera_mapa=True):
    c.aparelho(larg, alt, 2 if toque else 1, toque); c.goto(url, 1.2)
    J = c.js
    if faz: fazenda(J, faz)
    if espera_mapa:
        f = J("(document.querySelector('select[aria-label=\"Filtrar por fazenda\"]')||{}).value") or 'Lagoa Grande'
        espera(J, LG_PRONTO if f == 'Lagoa Grande' else SR_PRONTO, 25 if f == 'Lagoa Grande' else 8)
        time.sleep(.3)

def fazenda(J, nome):
    J("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); s.value=%s; s.dispatchEvent(new Event('change',{bubbles:true}));})()" % json.dumps(nome))
    espera(J, LG_PRONTO if nome == 'Lagoa Grande' else (SR_PRONTO if nome in ('Santa Rita', 'Todas') else 'true'), 25); time.sleep(.3)

TRI = "[...document.querySelectorAll('nav[aria-label=\"Funcionalidades do mapa\"] [role=tab]')]"
def camada(J, nome):
    J(f"(()=>{{const b={TRI}.find(x=>x.textContent.trim()==={json.dumps(nome)}); b&&b.click();}})()")
    espera(J, f"(()=>{{const b={TRI}.find(x=>x.textContent.trim()==={json.dumps(nome)}); return b&&b.getAttribute('aria-selected')==='true';}})()", 4); time.sleep(.35)

def filtro(J, grupo, opcao):
    """Botão de um grupo segmentado da faixa (ex.: Mostrar › Balanço hídrico; Cena › 06/09)."""
    J(f"(()=>{{const g=[...document.querySelectorAll('main [role=group]')].find(x=>x.getAttribute('aria-label')==={json.dumps(grupo)}); const b=g&&[...g.querySelectorAll('button')].find(x=>x.innerText.trim()==={json.dumps(opcao)}); b&&b.click();}})()")
    time.sleep(.45)

def caixa(J, tid):
    """Retângulo do talhão na tela: polígono da Santa Rita ou botão (marcador, no centro) do pivô da Lagoa Grande."""
    # a base (antes da MUX) não tem data-talhao: acha pelo rótulo antigo ("T4: …") ou pelo marcador do MapLibre, para a contraprova reprovar pelo
    # que o item mede e não por não achar o talhão
    return json.loads(J("JSON.stringify((()=>{const id=%s; const b=document.querySelector('[data-mux-grupo] [data-talhao='+id+']')||[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith(id+':'))"
                        "||(window.__LGI&&__LGI.markers[id]?__LGI.markers[id].getElement():null); if(!b) return null; const r=b.getBoundingClientRect(); return {x:r.left+r.width/2,y:r.top+r.height/2,l:r.left,t:r.top,r:r.right,b:r.bottom};})())" % json.dumps(tid)) or 'null')

CARTAO = """JSON.stringify((()=>{const d=document.getElementById('mux-cartao'); if(!d) return {on:false};
  const r=d.getBoundingClientRect(); return {on:!d.hidden&&r.width>0, txt:d.innerText.replace(/\\s+/g,' ').trim(), r:[r.left,r.top,r.right,r.bottom], acoes:d.querySelectorAll('button,a,input,select,[tabindex]').length,
  tal:d.dataset.talhao||'', modo:d.dataset.modo||'', livre:d.dataset.livre||'', role:d.getAttribute('role'), vw:innerWidth, vh:innerHeight};})())"""
def cartao(J): return json.loads(J(CARTAO) or '{}')

def tal_el(tid):
    """Expressão JS do elemento do talhão (com a contraprova na base: rótulo antigo "T4: …")."""
    return "(document.querySelector('[data-mux-grupo] [data-talhao=%s]')||[...document.querySelectorAll('svg [role=button]')].find(x=>(x.getAttribute('aria-label')||'').startsWith(%s)))" % (json.dumps(tid), json.dumps(tid + ':'))

def pivo_livre(J):
    """Pivô da Lagoa Grande cujo centro está livre na tela (o toque cai no mapa, não na legenda nem na barra), o mais perto do centro do mapa."""
    # espera o mapa parar (o MapLibre reajusta o tamanho depois do primeiro desenho a 390 px) e devolve {id, x, y} já medidos
    pos = "JSON.stringify(Object.keys(__LGI.markers).map(id=>{const r=__LGI.markers[id].getElement().getBoundingClientRect(); return [Math.round(r.left),Math.round(r.top)];}))"
    ant = None
    for _ in range(30):
        cur = J(pos)
        if cur == ant: break
        ant = cur; time.sleep(.25)
    return json.loads(J("""JSON.stringify((()=>{const a=document.querySelector('.mapa-area').getBoundingClientRect(); const cx=(a.left+a.right)/2, cy=(a.top+a.bottom)/2; let m=null, d=1e9;
      Object.keys(__LGI.markers).forEach(id=>{ const r=__LGI.markers[id].getElement().getBoundingClientRect(); const x=r.left+r.width/2, y=r.top+r.height/2;
        if(x<0||y<0||x>innerWidth||y>innerHeight) return; const e=document.elementFromPoint(x,y);
        if(!e||!e.closest('.maplibregl-canvas-container')) return; const q=Math.hypot(x-cx,y-cy); if(q<d){ d=q; m={id,x,y}; } }); return m;})())""") or 'null')

def painel(J):
    return J("(()=>{const a=document.querySelector('main aside[data-mux-painel]'); return a?a.innerText.replace(/\\s+/g,' ').trim():'';})()") or ''

def ativo(J):
    return J("(()=>{const a=document.activeElement; return a?(a.getAttribute('data-talhao')||a.id||a.tagName):'';})()") or ''

def erros(J):
    return [e for e in (J("window.__errs||[]") or []) if "reading 'g2toast'" not in e]
