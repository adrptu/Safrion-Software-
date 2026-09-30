# -*- coding: utf-8 -*-
"""Verificação independente (Chrome) · planos-safra-03/04/06: busca, safra nova, safra encerrada, ordenação de datas."""
import sys, os, time, subprocess, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
import verif_lib as L
from verif_lib import say, clk, toast, panel, etapa, abrir, row, rowclick, fset, LARG, CUSTOH, total_oper, num
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(HERE, '_render')
SHOT = sys.argv[1] if len(sys.argv) > 1 else HERE
p = free(); srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = Chrome(port=free()); J = c.js; L.setup(c)
def busca(q):
    J(f"""(()=>{{const i=[...document.querySelectorAll('input[aria-label="Buscar nesta tabela"]')].find(x=>x.offsetParent); const P=HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(q)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.5)
    return J("[...[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent).querySelectorAll('[role=row]')].slice(1).map(r=>r.innerText.replace(/\\s+/g,' ').slice(0,50))")
try:
    c.size(1440, 1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html', wait=1.3)
    J("window.__errs=[]; window.addEventListener('error',e=>window.__errs.push(String(e.message)));")
    abrir('Safrinha 2027'); etapa(3)
    say('1 busca Colhedora:', busca('Colhedora'))
    say('1 busca Milho:', busca('Milho'))
    say('1 busca Feijão:', busca('Feijão'))
    busca('')
    J("""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const b=[...t.querySelectorAll('[role=columnheader] button')].find(b=>/Filtrar Custo \\(R\\$\\/kg\\)/.test(b.getAttribute('aria-label')||'')); if(b) b.click(); return !!b;})()"""); time.sleep(.4)
    say('1 menu de filtro R$/kg:', J("(()=>{const m=[...document.querySelectorAll('[role=dialog],[role=menu],div')].filter(d=>/Ordenar A→Z|Crescente|Limpar/.test(d.innerText)&&d.offsetParent).sort((a,b)=>a.innerText.length-b.innerText.length)[0]; return m?m.innerText.replace(/\\s+/g,' ').slice(0,200):'sem menu';})()"))
    J("document.body.click()"); time.sleep(.3)
    c.shot(os.path.join(SHOT, 'verif_safrinha_e3.png'))
    # 2 · pré-existente: ordenação de data no Plantio (etapa 2)
    abrir('Safra 2026/27'); etapa(2); clk('Expandir tudo')
    J("""(()=>{const b=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent).querySelector('button[aria-label="Ordenar por Plantio"]'); b.click();})()"""); time.sleep(.5)
    say('2 etapa 2 ordenada por Plantio:', J(r"""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent); const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.trim().toUpperCase()); const ci=hs.findIndex(h=>h.startsWith('PLANTIO')); return [...t.querySelectorAll('[role=row]')].slice(1).map(r=>{const cs=r.querySelectorAll('[role=cell]'); return cs[ci]?cs[ci].innerText.trim():'';});})()"""))
    # 3 · S2526 em consulta: campos calculados aparecem
    abrir('Safra 2025/26'); etapa(3); rowclick('Colhedora')
    say('3 painel 2025/26:', panel()[:400])
    say('3 valores:', J("[...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select')].map(i=>(i.labels&&i.labels[0]?i.labels[0].innerText:'')+'='+i.value+(i.readOnly||i.disabled?'(ro)':''))"))
    J("document.querySelector('aside[role=dialog]').dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.3)
    say('3 Esc fecha:', not J("!!document.querySelector('aside[role=dialog]')"))
    etapa(6); say('3 2025/26 etapa 6 · linha Herbicidas:', row('Herbicidas'))
    # 4 · safra nova: etapa 3 editável e isolada
    etapa(1); say('4 nova safra:', clk('Nova safra')); fset('Nome da safra', 'Safra teste 27/28'); fset('Período', 'set/2027 – ago/2028'); clk('Salvar', 'aside[role=dialog]'); say('4 toast:', toast())
    etapa(3); say('4 etapa 3 nova:', row('Plantadeira')); rowclick('Plantadeira'); say('4 painel:', panel()[:160])
    fset('Pessoas na equipe', '4'); clk('Salvar', 'aside[role=dialog]'); say('4 salvar:', toast(), '|', row('Plantadeira'))
    say('4 colheita sem cultivos:', row('Colhedora'))
    abrir('Safra 2026/27'); etapa(3); say('4 2026/27 depois:', row('Plantadeira'))
    abrir('Safrinha 2027'); etapa(3); say('4 Safrinha depois:', row('Plantadeira'))
    say('erros JS:', J("window.__errs"))
finally:
    c.close(); srv.terminate()
