# -*- coding: utf-8 -*-
"""Verificador · Estoque 7: fotos das tabelas que rolam (e1 após conferir NF 4533, e4), reserva nova usando lote vencido, sinal do app."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ver_estoque_lib import V

K = "(document.querySelector('main').innerText.split('\\n').find(l=>/·/.test(l)||/custódia/.test(l))||'')"
SCR = """(()=>{const o=[]; document.querySelectorAll('[role=table],[role=grid],table').forEach(t=>{ let p=t.parentElement; while(p&&p!==document.body){ const cs=getComputedStyle(p); if(/auto|scroll/.test(cs.overflowX)&&p.scrollWidth>p.clientWidth+1){ const r=p.getBoundingClientRect(); o.push([p.scrollWidth,p.clientWidth,Math.round(r.right)]); break;} p=p.parentElement; } }); return o;})()"""
v = V()
try:
    v.abrir()
    v.etapa(1); print('e1 inicial:', v.J(SCR))
    v.clk(v.prim())
    for k, val in [('conf', '20000'), ('apto', '20000'), ('quar', '0'), ('val', '05/2027')]:
        v.setv('fx_g_rec_' + k, val)
    v.clk('Salvar', 'aside[role=dialog]'); time.sleep(3.2)
    print('e1 após NF 4533:', v.J(SCR)); v.shot('ver_est_e1_rola.png')
    # botões/links fora da área visível da tabela
    print('fora:', v.J("""(()=>{const out=[]; document.querySelectorAll('[role=row]').forEach(r=>{ const sc=r.closest('[style*=overflow]')||r.parentElement; }); const box=[...document.querySelectorAll('*')].find(p=>{const cs=getComputedStyle(p); return /auto|scroll/.test(cs.overflowX)&&p.scrollWidth>p.clientWidth+1&&p.querySelector('[role=row]');}); if(!box) return 'nenhum'; const R=box.getBoundingClientRect(); [...box.querySelectorAll('[role=columnheader],[role=cell]')].forEach(c=>{const b=c.getBoundingClientRect(); if(b.right>R.right+1) out.push(c.innerText.replace(/\\s+/g,' ').slice(0,40)+' ['+Math.round(b.left)+'-'+Math.round(b.right)+' > '+Math.round(R.right)+']');}); return out.slice(0,8);})()"""))
    v.etapa(4); print('e4:', v.J(SCR)); v.J("window.scrollTo(0,0)"); v.shot('ver_est_e4_rola.png')
    print('fora e4:', v.J("""(()=>{const box=[...document.querySelectorAll('*')].find(p=>{const cs=getComputedStyle(p); return /auto|scroll/.test(cs.overflowX)&&p.scrollWidth>p.clientWidth+1&&p.querySelector('[role=row]');}); if(!box) return 'nenhum'; const R=box.getBoundingClientRect(); const out=[]; [...box.querySelectorAll('[role=columnheader],[role=cell]')].forEach(c=>{const b=c.getBoundingClientRect(); if(b.right>R.right+1) out.push(c.innerText.replace(/\\s+/g,' ').slice(0,30)+' ['+Math.round(b.right)+'>'+Math.round(R.right)+']');}); return out.slice(0,6);})()"""))
    print('larguras colunas e4:', v.J("[...document.querySelectorAll('[role=columnheader]')].filter(h=>h.offsetParent).map(h=>h.innerText.replace(/\\s+/g,' ').slice(0,14)+':'+Math.round(h.getBoundingClientRect().width))"))
    # app sem sinal com os 3 itens entregues; sinal volta; recarrega
    print(v.mudar("c.ordens['OS-0430'].aprov=true; cenLiberar(c,'OS-0430'); const rid=c.ordens['OS-0430'].req; c.reqs[rid].itens.forEach(i=>cenEntregar(c,rid,i.prod,i.solicitado,'Marcos')); cenSinal(c,false); cenConfirmarRecebimento(c,rid); cenIniciarTurno(c,'OS-0430'); return cenFecharTurno(c,5,1);"))
    print('sinal:', v.mudar("return cenSinal(c,true);"))
    v.abrir(); v.etapa(6); print('k6:', v.J(K)); print('consumo:', v.rowtxt('Consumo apontado no app'))
    print('ap:', v.cen("JSON.stringify(c.ordens['OS-0430'].ap.map(a=>[a.dia,a.ha,a.sinc]))"), '| fila:', v.cen("JSON.stringify(c.app.fila)"), '| movs app:', v.cen("JSON.stringify(c.movs.filter(m=>m.origem==='app').map(m=>[m.id,m.tipo,m.sinc]))"))
    v.shot('ver_est_e6_sinal.png')
    print('erros:', v.erros())
finally:
    v.fim()
