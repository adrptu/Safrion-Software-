# -*- coding: utf-8 -*-
"""Troca de recurso na O.S. pelo navegador (pedido do proprietário, 14/10/2026: "ordem de serviço agrícola está faltando edição de insumos, e
recursos (pessoas e máquinas) e botão de liberar"). OS-0430 (A liberar): Caio (PCP) troca o Trator 03 pelo Trator 04; o painel, o conjunto
da atividade, a Origem e a Carga do PCP mostram a troca; substituto bloqueado ou ocupado não é escolhível; sem o papel, "Trocar" fica
indisponível com o motivo. Dados sintéticos; render em RENDER_DIR ou _render."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:400], flush=True)

p, srv = servir(R); c = Chrome(); J = c.js
def abrir(perfil, h='OS.dc.html#OS-0430', limpa=False):
    c.goto(f'http://127.0.0.1:{p}/OS.dc.html', espera=.8)
    J("(()=>{%s localStorage.setItem('safrion.perfilDemo',%s);})()" % ("localStorage.clear();" if limpa else "", json.dumps(perfil)))
    c.goto(f'http://127.0.0.1:{p}/{h}', espera=1.6)
def painel(): return J("(()=>{const r=document.querySelector('aside[role=dialog]'); return r?r.innerText:''})()") or ''
def sec(t):   # abre a seção do painel pelo título
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(x=>x.innerText.trim().toUpperCase().startsWith(%s)); if(b&&b.getAttribute('aria-expanded')!=='true') b.click();})()" % json.dumps(t.upper())); time.sleep(.4)
def btns(t): return J("[...document.querySelectorAll('aside[role=dialog] button')].filter(b=>b.innerText.trim()===%s&&b.offsetParent).map(b=>b.getAttribute('aria-disabled')==='true'?'off':'on')" % json.dumps(t)) or []
def clk(t):
    r = J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(x=>x.innerText.trim()===%s&&x.offsetParent&&x.getAttribute('aria-disabled')!=='true'&&!x.disabled); if(!b) return false; b.click(); return true;})()" % json.dumps(t)); time.sleep(.6); return r
try:
    c.aparelho(1440, 900, 1, False)
    abrir('Caio', limpa=True); sec('Recursos alocados')
    p0 = painel()
    chk('R1 OS-0430 com o Trator 03 e "Trocar" disponível para Caio (PCP)', 'Máquina · Trator 03' in p0 and 'on' in btns('Trocar'), p0[:600])
    J("(()=>{const r=[...document.querySelectorAll('aside[role=dialog] [style*=\"grid\"]')].find(x=>/Máquina · Trator 03/.test(x.innerText)); const b=r&&[...r.querySelectorAll('button')].find(y=>y.innerText.trim()==='Trocar'); if(b) b.click();})()"); time.sleep(.6)
    ops = J("[...document.querySelectorAll('aside[role=dialog] select[aria-label=Substituto] option')].map(o=>[o.value,o.disabled,o.textContent.trim()])") or []
    chk('R2 substitutos: T1 bloqueado e T02 ocupado não escolhíveis; T04 livre', [o[0] for o in ops] == ['T1', 'T02', 'T04'] and ops[0][1] and ops[1][1] and not ops[2][1]
        and 'bloqueado na Manutenção' in ops[0][2] and 'ocupado na OS-0420' in ops[1][2], ops)
    chk('R3 confirmar troca', clk('Confirmar troca'))
    toast = J("(document.querySelector('[role=status]')||{}).innerText||''")
    sec('Recursos alocados'); p1 = painel()
    chk('R4 painel: Trator 04 no lugar do Trator 03, com aviso de retorno', 'Máquina · Trator 04' in p1 and 'no lugar de Trator 03' in p1 and 'Trator 03 → Trator 04' in (toast or ''), [toast, p1[:700]])
    sec('Atividade'); p2 = painel()
    chk('R5 conjunto da atividade com o Trator 04', 'Trator 04 + Pulverizador' in p2, p2[p2.find('ATIVIDADE'):][:300])
    sec('Origem'); p3 = painel()
    chk('R6 Origem com a troca, quem e quando', 'Recurso trocado: Trator 03 → Trator 04 por Caio (PCP)' in p3, p3[p3.find('ORIGEM'):][:400])
    st = J("(()=>{const c=JSON.parse(localStorage.getItem('talhao-os-cenario-v1')||'{}'); const o=(c.ordens||{})['OS-0430']||{}; return JSON.stringify([o.rec,(o.recHist||[]).length]);})()")
    chk('R7 cenário: troca gravada uma vez', st == json.dumps([{'T03': 'T04'}, 1]).replace(' ', ''), st)
    # Carga do PCP: o bloco da OS-0430 sai da linha do Trator 03 e entra na do Trator 04
    c.goto(f'http://127.0.0.1:{p}/OS.dc.html', espera=1.6)
    J("(()=>{const b=document.querySelector('[role=toolbar] [data-visao=carga]'); if(b) b.click();})()"); time.sleep(1.0)   # visão Carga (VISOES-1: botão data-visao)
    lin = J("""(()=>{const rows=[...document.querySelectorAll('[role=table][aria-label="Alocação de recursos na semana"] [role=row]')]; const t=n=>{const r=rows.find(x=>x.firstElementChild&&x.firstElementChild.innerText.trim()===n); return r?r.innerText:'';};
        return JSON.stringify([t('Trator 03'),t('Trator 04')]);})()""")
    t03, t04 = json.loads(lin) if lin else ['', '']
    chk('R8 Carga: OS-0430 na linha do Trator 04 (no lugar do 03) e fora da linha do Trator 03', 'OS-0430' in t04 and 'no lugar de Trator 03' in t04 and 'OS-0430' not in t03, [t03[:300], t04[:300]])
    # sem o papel
    abrir('Otávio'); sec('Recursos alocados')
    chk('R9 Otávio (PCM): "Trocar" indisponível, com o motivo', btns('Trocar') and set(btns('Trocar')) == {'off'}
        and 'decisão de' in (J("[...document.querySelectorAll('aside[role=dialog] button')].filter(b=>b.innerText.trim()==='Trocar')[0].title") or ''), btns('Trocar'))
    # ordem em execução: sem troca
    abrir('Caio', 'OS.dc.html#OS-0420'); sec('Recursos alocados')
    chk('R10 OS-0420 em execução: sem "Trocar"', btns('Trocar') == [], btns('Trocar'))
    # ponte do Painel Agrícola (Codex 6166235821): #painel=IDs mostra só o grupo, sem mexer nos filtros; "Ver todas as O.S." volta
    abrir('Caio', 'OS.dc.html#painel=OS-0418,OS-0420,OS-9999')
    J("(()=>{const b=document.querySelector('[role=toolbar] [data-visao=lista]'); if(b) b.click();})()"); time.sleep(.8)   # a visão guardada (Carga, acima) fica; o teste lê a Lista
    ids = J("JSON.stringify([...new Set([...document.querySelectorAll('[data-rid]')].filter(e=>e.offsetParent).map(e=>e.getAttribute('data-rid')).filter(x=>/^OS-/.test(x||'')))])")
    nota = J("(()=>{const n=document.querySelector('[aria-label=\"Recorte do Painel Agrícola\"]'); return n?n.innerText:''})()") or ''
    chk('R12 #painel=OS-0418,OS-0420,OS-9999: só as duas O.S. que existem, com a faixa do Painel', json.loads(ids or '[]') == ['OS-0418', 'OS-0420'] and 'Do Painel Agrícola: 2 O.S.' in nota, [ids, nota])
    J("(()=>{const b=[...document.querySelectorAll('button')].find(x=>x.innerText.trim()==='Ver todas as O.S.'); if(b) b.click();})()"); time.sleep(.8)
    n2 = J("[...new Set([...document.querySelectorAll('[data-rid]')].filter(e=>e.offsetParent).map(e=>e.getAttribute('data-rid')).filter(x=>/^OS-/.test(x||'')))].length") or 0
    chk('R13 "Ver todas as O.S." encerra o recorte do Painel e limpa o endereço', n2 > 2 and 'painel=' not in (J('location.hash') or ''), n2)
    # revisão Codex 6167883199: o recorte suspende (não apaga) busca, fase e filtros da lista e do topo; "Ver todas" devolve o estado guardado
    abrir('Caio')
    J("(()=>{const b=document.querySelector('[role=toolbar] [data-visao=lista]'); if(b) b.click();})()"); time.sleep(.6)
    J("(()=>{const i=document.querySelector('input[type=search]'); const set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set; set.call(i,'OS-0430'); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true}));})()"); time.sleep(.8)
    vis_ids = lambda: json.loads(J("JSON.stringify([...new Set([...document.querySelectorAll('[data-rid]')].filter(e=>e.offsetParent).map(e=>e.getAttribute('data-rid')).filter(x=>/^O[SB]-/.test(x||'')))])") or '[]')
    antes = vis_ids()
    c.goto(f'http://127.0.0.1:{p}/OS.dc.html#painel=OS-0418,OS-0420', espera=1.6)
    J("(()=>{const b=document.querySelector('[role=toolbar] [data-visao=lista]'); if(b) b.click();})()"); time.sleep(.6)
    dur = vis_ids(); faz_dis = J("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); return s?s.disabled:null})()")
    busca_vis = J("!!(document.querySelector('input[type=search]')&&document.querySelector('input[type=search]').offsetParent)")
    nota2 = J("(()=>{const n=document.querySelector('[aria-label=\"Recorte do Painel Agrícola\"]'); return n?n.innerText:''})()") or ''
    chk('R14 busca guardada (OS-0430): o recorte mostra 0418 e 0420, com busca e Fazenda suspensas e a faixa dizendo isso',
        antes == ['OS-0430'] and dur == ['OS-0418', 'OS-0420'] and faz_dis is True and not busca_vis and 'suspensos' in nota2, [antes, dur, faz_dis, busca_vis, nota2])
    J("(()=>{const b=[...document.querySelectorAll('button')].find(x=>x.innerText.trim()==='Ver todas as O.S.'); if(b) b.click();})()"); time.sleep(.8)
    J("(()=>{const b=document.querySelector('[role=toolbar] [data-visao=lista]'); if(b) b.click();})()"); time.sleep(.5)
    depois = vis_ids(); q = J("(document.querySelector('input[type=search]')||{}).value||''"); faz = J("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); return s?[s.value,s.disabled]:null})()")
    chk('R15 "Ver todas as O.S." devolve a busca guardada (OS-0430) e a Fazenda habilitada, sem nada sobrescrito', depois == ['OS-0430'] and q == 'OS-0430' and faz == ['Santa Rita', False], [depois, q, faz])
    c.goto(f'http://127.0.0.1:{p}/OS.dc.html#painel=OS-0507', espera=1.6)
    J("(()=>{const b=document.querySelector('[role=toolbar] [data-visao=lista]'); if(b) b.click();})()"); time.sleep(.6)
    lg = vis_ids(); faz2 = J("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); return s?[s.value,s.disabled]:null})()")
    chk('R16 OS-0507 (Lagoa Grande) com Fazenda Santa Rita guardada: a O.S. aparece e o filtro de Fazenda fica suspenso, não fingindo governar o recorte', lg == ['OS-0507'] and faz2 == ['Santa Rita', True], [lg, faz2])
    errs = J("(window.__errs||[]).length") or 0
    chk('R11 sem erro de JS', not errs, errs)
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
