import sys, os, time, subprocess, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdp import Chrome
from journeys import free
R=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'_render'); p=free()
srv=subprocess.Popen(['python3','-m','http.server',str(p),'--bind','127.0.0.1','--directory',R],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(0.8)
c=Chrome(port=free()); J=c.js
CLK="""((t,root)=>{const r=root?document.querySelector(root):document; const n=s=>(s||'').replace(/\\s+/g,' ').trim(); const els=[...r.querySelectorAll('button,a')]; const e=els.find(x=>n(x.innerText)===t)||els.find(x=>n(x.innerText).startsWith(t)); if(!e) return 'NÃO ACHEI: '+t; e.click(); return 'ok';})"""
T=lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')")
def clk(t,root=None): r=J(f"({CLK})({json.dumps(t)},{json.dumps(root)})"); time.sleep(.45); return r
from comp_lib import IR_ETAPA
def ir_etapa(n): r=J(f"({IR_ETAPA})({n})"); time.sleep(.45); return r   # a faixa só informa: anda pela área de ações
try:
    c.size(1440,1000); c.goto(f'http://127.0.0.1:{p}/SAF.dc.html'); time.sleep(.5)
    print('erros JS?', J("window.__err||'nenhum'"))
    print('etapa inicial:', J("document.querySelector('[aria-current=step]') && document.querySelector('[aria-current=step]').innerText.replace(/\\s+/g,' ')"))
    print('impedimentos:', J("[...document.querySelectorAll('.etp-ind .etp-itens>li')].map(b=>b.innerText.replace(/\\s+/g,' ')).join(' | ')"))
    print('safras:', J("[...document.querySelectorAll('[role=table]')[0].querySelectorAll('[role=row]')].slice(1).map(r=>r.innerText.split('\\n')[0])"))
    print('clicar etapa 4 sem safra:', ir_etapa(4), T())
    print('abrir safra:', clk('Continuar'), T())
    print('etapa agora:', J("document.querySelector('[aria-current=step]').innerText.replace(/\\s+/g,' ')"))
    print('k2:', J("document.body.innerText.match(/\\d+ cultivos · [^\\n]+/)[0]"))
    # selecionar T4,T3,P1,P2
    sel=J("""(()=>{const rows=[...document.querySelectorAll('[role=row].g2ed')]; let n=0; rows.forEach(r=>{const t=r.innerText; if(/\\bT4\\b|\\bT3\\b|\\bP1\\b|\\bP2\\b/.test(t)){ const cb=r.querySelector('input[type=checkbox]'); if(cb){cb.click(); n++;} }}); return n;})()""")
    time.sleep(.4); print('selecionados:', sel, '· form aberto?', J("!!document.querySelector('aside[role=dialog]')"))
    print('aplicar em lote:', clk('Aplicar plano'), '· painel:', J("document.querySelector('aside[role=dialog] h2') && document.querySelector('aside[role=dialog] h2').innerText"))
    print('opções:', J("[...document.querySelectorAll('#ap_sel option')].map(o=>o.innerText)"))
    print('plano sugerido:', J("(()=>{const i=document.querySelector('#ap_sel'); return i?i.options[i.selectedIndex].text:null;})()"))   # 01/10: o plano mais usado da cultura vem sugerido
    J("""(()=>{const i=document.querySelector('#ap_sel'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,''); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.3)
    print('aplicar sem plano:', clk('Aplicar plano','aside[role=dialog]'), J("(document.querySelector('aside [role=alert]')||{}).innerText"))
    J("""(()=>{const i=document.querySelector('#ap_sel'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,'SOJA-AT'); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.3)
    print('aplicar:', clk('Aplicar plano','aside[role=dialog]'), T())
    print('k2 após:', J("document.body.innerText.match(/\\d+ cultivos · [^\\n]+/)[0]"))
    # substituição exige confirmação: aplicar individual em T1-A (tem plano) via seleção
    J("""(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/T1-A/.test(r.innerText)); r.querySelector('input[type=checkbox]').click();})()"""); time.sleep(.3)
    clk('Aplicar plano')
    J("""(()=>{const i=document.querySelector('#ap_sel'); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,'SOJA-PD'); i.dispatchEvent(new Event('change',{bubbles:true}));})()"""); time.sleep(.3)
    clk('Aplicar plano','aside[role=dialog]')
    print('confirmação:', J("(document.querySelector('aside [role=alert]')||{}).innerText"))
    print('voltar/cancelar:', clk('Voltar','aside[role=dialog]'), clk('Cancelar','aside[role=dialog]'))
    # atividades locais do T1-B: clicar no nome do plano
    r=J("""(()=>{const row=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/T1-B/.test(r.innerText)); const b=[...row.querySelectorAll('button')].find(b=>/^Ajustar insumos|Soja alta tecnologia/.test(b.innerText.trim())); b.click(); return 'ok';})()"""); time.sleep(.5)
    print('painel local:', J("document.querySelector('aside[role=dialog] h2').innerText"))
    print('grupos/gatilhos:', J("[...document.querySelectorAll('aside[role=dialog] b')].map(b=>b.innerText).slice(0,10)"))
    print('ajuste local existente:', J("document.querySelector('aside[role=dialog]').innerText.indexOf('ajuste local')>=0"))
    J("""(()=>{const i=document.querySelector('#lp_a5_0'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'0,6'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"""); time.sleep(.3)
    clk('Cancelar','aside[role=dialog]'); print('aviso não salvo:', J("document.querySelector('aside[role=dialog]').innerText.indexOf('Há alterações não salvas')>=0"))
    clk('Continuar editando','aside[role=dialog]'); clk('Salvar','aside[role=dialog]'); print('salvar local:', T())
    print('k2 ajustes:', J("document.body.innerText.match(/\\d+ cultivos · [^\\n]+/)[0]"))
    c.shot('_probe/saf_e2.png')
    # etapa 3
    ir_etapa(3); time.sleep(.3)
    print('rendimentos linhas:', J("[...document.querySelectorAll('[role=row].g2ed')].length"))
    J("""(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Colhedora/.test(r.innerText)); r.querySelector('[role=cell] span').click();})()"""); time.sleep(.4)
    J("""(()=>{const i=document.querySelector('[id$=_vel]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'5,625'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"""); time.sleep(.2)
    print('rendimento calculado no formulário:', J("document.querySelector('[id$=_rend_c]').value"))
    clk('Salvar','aside[role=dialog]'); print('rend salvo:', T(), '· linha:', J("[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Colhedora/.test(r.innerText)).innerText.replace(/\\s+/g,' ')"))
    ir_etapa(4); print('k4:', J("document.body.innerText.match(/[\\d.]+ ha trabalhados[^\\n]+/)[0]"))
    J("""(()=>{const r=[...document.querySelectorAll('[role=row].g2ed')].find(r=>/Colheita/.test(r.innerText)); r.click();})()"""); time.sleep(.4)
    print('matriz:', J("[...document.querySelectorAll('h3')].map(h=>h.innerText).filter(t=>/Detalhamento/.test(t))"))
    ir_etapa(5); print('k5:', J("(document.body.innerText.match(/([^\\n]*em vermelho na visão por mês|Capacidade atende[^\\n]+)/)||[''])[0]"))
    c.shot('_probe/saf_e5.png')
    ir_etapa(6); print('k6:', J("document.body.innerText.match(/Valor da necessidade[^\\n]+/)[0]"))
    print('enviar:', clk('Enviar para cotação'), T())
    print('enviar de novo:', clk('Enviar para cotação'), T())
    print('registro compartilhado:', J("(()=>{const o=JSON.parse(localStorage.getItem('talhao-os-compras-v1')||'null'); const s=o&&o.sols&&o.sols.S2627; return s?[s.id,s.comp,Object.keys(s.itens).length]:null;})()"))
    c.shot('_probe/saf_e6.png')
    print('abrir compra:', clk('Abrir Compra de insumos ›'), (time.sleep(2.5), J("location.pathname+location.hash"))[1], J("(document.querySelector('[aria-current=step]')||{innerText:''}).innerText.replace(/\\s+/g,' ')"))
    print('compra mostra o complemento:', J("(document.body.innerText.match(/SOL-2026-07 · Safra 2026\\/27[^\\n]+/)||[''])[0]"))
finally:
    c.close(); srv.terminate()
