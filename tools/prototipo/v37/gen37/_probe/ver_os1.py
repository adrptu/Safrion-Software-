# -*- coding: utf-8 -*-
"""Verificador independente (frente os) · 1: layout, cabeçalho, filtros e textos na OS.dc.html (1440×1000)."""
import sys, os, time, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
from os_lib import Os
T = Os(copiar=False); J = T.J
def filtro(lab, val):
    J(f"""(()=>{{const i=document.querySelector('select[aria-label={json.dumps(lab)}]'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(val)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.4)
OVF = r"""(()=>{const out=[]; const W=document.documentElement.clientWidth;
  out.push('doc '+document.documentElement.scrollWidth+'/'+W);
  document.querySelectorAll('[role=table],[role=grid],[aria-label="Kanban das ordens"],section').forEach(e=>{ if(e.scrollWidth>e.clientWidth+2) out.push('ovf '+(e.getAttribute('aria-label')||e.tagName)+' '+e.scrollWidth+'>'+e.clientWidth); });
  // texto cortado: elemento com overflow hidden e scrollWidth maior
  [...document.querySelectorAll('span,div,b,a,button')].forEach(e=>{ const cs=getComputedStyle(e); if(e.offsetParent===null) return;
     if((cs.overflow==='hidden'||cs.textOverflow==='ellipsis'||cs.overflowX==='hidden') && e.scrollWidth>e.clientWidth+1 && e.innerText.trim().length>2 && e.children.length<3) out.push('corte: '+e.innerText.trim().slice(0,80)+' '+e.scrollWidth+'>'+e.clientWidth); });
  // elementos que saem da janela à direita
  [...document.querySelectorAll('button,a,span,b')].forEach(e=>{ const r=e.getBoundingClientRect(); if(r.width>0&&r.right>W+1&&e.offsetParent!==null) out.push('fora: '+e.innerText.trim().slice(0,50)+' right='+Math.round(r.right)); });
  return out.slice(0,30);})()"""
try:
    T.abrir(wait=1.3)
    print('ERROS', T.erros())
    print('LAYOUT lista', J(OVF))
    hdr = J("(()=>{const h=document.querySelector('header h1'); const s=h&&h.nextElementSibling; return s?[s.innerText.trim(), getComputedStyle(s).color, getComputedStyle(s).backgroundColor, s.outerHTML.slice(0,300)]:null;})()")
    print('HDR', hdr)
    T.shot('ver_os1_lista.png')
    # linhas: altura e textos
    rows = J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>[r.innerText.split('\\n')[0], Math.round(r.getBoundingClientRect().height)])")
    print('ROWS', rows)
    # Kanban
    J("(()=>{const b=[...document.querySelectorAll('button,[role=tab]')].find(b=>b.innerText.trim()==='Kanban'); b&&b.click();})()"); time.sleep(.5)
    print('LAYOUT kanban', J(OVF))
    print('KB', J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > div')].map(d=>d.innerText.split('\\n').slice(0,3).join(' | '))"))
    T.shot('ver_os1_kanban.png')
    J("(()=>{const b=[...document.querySelectorAll('button,[role=tab]')].find(b=>b.innerText.trim()==='Recursos'); b&&b.click();})()"); time.sleep(.5)
    print('LAYOUT recursos', J(OVF))
    J("(()=>{const b=[...document.querySelectorAll('button,[role=tab]')].find(b=>b.innerText.trim()==='Lista'); b&&b.click();})()"); time.sleep(.4)
    # filtro 2025/26 → cabeçalho
    filtro('Filtrar por safra', '2025/26')
    hdr2 = J("(()=>{const h=document.querySelector('header h1'); const s=h&&h.nextElementSibling; return s?[s.innerText.trim(), getComputedStyle(s).color, getComputedStyle(s).backgroundColor]:null;})()")
    print('HDR 2025/26', hdr2)
    T.shot('ver_os1_2526.png')
    # Kanban na safra 2025/26: carga da coluna Encerradas
    J("(()=>{const b=[...document.querySelectorAll('button,[role=tab]')].find(b=>b.innerText.trim()==='Kanban'); b&&b.click();})()"); time.sleep(.4)
    print('KB 2025/26', J("[...document.querySelectorAll('[aria-label=\"Kanban das ordens\"] > div')].map(d=>d.innerText.split('\\n').slice(0,3).join(' | '))"))
    J("(()=>{const b=[...document.querySelectorAll('button,[role=tab]')].find(b=>b.innerText.trim()==='Lista'); b&&b.click();})()"); time.sleep(.4)
    # Boa Vista + 2025/26
    filtro('Filtrar por fazenda', 'Boa Vista')
    print('VAZIO BV', J("(()=>{const d=document.querySelector('[aria-label=\"Sem ordens no filtro\"]'); return d?d.innerText.replace(/\\s+/g,' '):'';})()"),
          '| abas?', J("!!document.querySelector('[aria-label=\"Visão das ordens\"]')"), '| rst', J("[...document.querySelectorAll('button')].some(b=>b.innerText.trim()==='Restaurar demonstração')"))
    T.shot('ver_os1_bv.png')
    J("(()=>{const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Ver Santa Rita'); b&&b.click();})()"); time.sleep(.4)
    print('APOS Ver Santa Rita', J("document.querySelector('select[aria-label=\"Filtrar por fazenda\"]').value"), J("document.querySelector('select[aria-label=\"Filtrar por safra\"]').value"),
          J("[...document.querySelectorAll('[role=row].g2ed')].map(r=>r.innerText.split('\\n')[0])"), T.toast())
    # Busca/contador da grade no recorte
    print('CONTADOR', J("[...document.querySelectorAll('section *')].filter(e=>/\\d+ de \\d+/.test(e.innerText||'')&&e.children.length===0).map(e=>e.innerText).slice(0,4)"))
    print('ERROS fim', T.erros())
finally:
    T.fim()
