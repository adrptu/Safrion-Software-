# -*- coding: utf-8 -*-
"""SAF-MAPA F1 · Planejar safra no mapa (proprietário, 18/10/2026: "Em planejar safra coloque o modo de visão mapa para ver geograficamente como
está o plano da safra e permita clicar nos talhões e fazer o todo o trabalho"). A visão Mapa é a segunda visão do mesmo estado do "Editar
talhões…" (EDL-01, safra_lote.js): mesma seleção, mesma aplicação com as mesmas recusas e mesma gravação. No Chrome a 1440 × 1000 e 390 × 844.
  M1  "Planejar no mapa ›" na faixa da fazenda abre o Editar talhões na visão Mapa (seletor pelo ícone), com os 8 talhões da Santa Rita e a legenda
  M2  tocar em 3 talhões marca os 3: contagem com área, painel "Planejar 3 talhões" e o mesmo número na visão Tabela
  M3  aplicar cultura e plano aos 3: o rótulo de cada talhão muda ao vivo, com a marca de alterado, e "Salvar alterações (n)" conta as mudanças
  M4  "Colorir por" Plano muda a legenda
  M5  um talhão só: o painel traz as ações da linha da tabela (Ajustar insumos, Dividir, Ver na tabela)
  M6  Esc limpa a seleção antes de fechar; Enter num talhão com foco marca o talhão (teclado)
  M7  salvar e reabrir (F5): os 3 talhões mostram a cultura gravada, sem marca de alterado
  M8  390 px sem rolagem horizontal da página; nenhum erro de JavaScript
  M9  seleção parcial (Codex 6252809331, S2): T1-A marcada na Tabela (T1-B não) e um talhão inteiro → no Mapa o T1 aparece "em parte"
      (aria-pressed=mixed, "Em parte · 1 de 2"), a contagem diz "(1 em parte)" com a área só das linhas marcadas, a lista diz qual parcela;
      "Aplicar" a Meta muda exatamente as 2 linhas anunciadas e a T1-B fica como estava
Contraprova: o render da v133 reprova M1 (não existe "Planejar no mapa"); o da v134 (e0c47a00) reprova M9.
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B saf_mapa_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:700])

LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.PN=()=>document.getElementById('sl-painel');
// EX-55 F1: a 2ª linha do rótulo vem da camada HTML ligada ao talhão (data-t) e só conta desenhada (largura > 0); o texto ligado dentro
// do <text> não aparecia na tela (o motor o envolve em <span>), e o teste o lia mesmo assim
window.TS=()=>[...(PN()||document).querySelectorAll('.sm-svg .sm-t')].filter(g=>VIS(g)).map(g=>({t:g.getAttribute('data-t'),sel:g.getAttribute('aria-pressed'),l:[...g.querySelectorAll('text')].map(x=>N(x.textContent)).concat([...(PN()||document).querySelectorAll('.sm-l2')].filter(x=>x.getAttribute('data-t')===g.getAttribute('data-t')&&x.getBoundingClientRect().width>0).map(x=>N(x.textContent))),mud:(g.querySelector('circle')||{getAttribute:()=>'0'}).getAttribute('opacity')}));
window.TAP=t=>{ const g=[...(PN()||document).querySelectorAll('.sm-svg .sm-t')].find(g=>g.getAttribute('data-t')===t&&VIS(g)); if(!g) return 'sem '+t; g.dispatchEvent(new MouseEvent('click',{bubbles:true})); return 'ok'; };
window.TXT=s=>N(((PN()||document).querySelector(s)||{}).innerText||'');
window.BT=t=>{ const b=[...(PN()||document).querySelectorAll('button')].filter(VIS).find(b=>N(b.innerText)===t||N(b.innerText).startsWith(t)); if(!b) return 'sem '+t; b.click(); return 'ok'; };
window.SEL=(lab,val)=>{ const i=[...(PN()||document).querySelectorAll('select,input')].find(x=>x.getAttribute('aria-label')===lab); if(!i) return 'sem '+lab; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; };
window.OPTS=lab=>{ const i=[...(PN()||document).querySelectorAll('select')].find(x=>x.getAttribute('aria-label')===lab); return i?[...i.options].map(o=>[o.value,N(o.textContent)]):null; };
'ok'"""

port, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda p: f'http://127.0.0.1:{port}/{p}'
def espera(js, ate=12.0):
    t0 = time.time()
    while time.time() - t0 < ate:
        try:
            if J(js): return True
        except Exception: pass
        time.sleep(.15)
    return False
def abrir_mapa():
    c.goto(U('SAF.dc.html#saf=S2627&passo=cultivos'), 2.0); J(LIB)
    acts = J("[...document.querySelectorAll('button,a')].filter(x=>VIS(x)&&/Planejar no mapa/.test(x.innerText)).map(x=>N(x.innerText))") or []
    J("(()=>{const b=[...document.querySelectorAll('button,a')].find(x=>VIS(x)&&/Planejar no mapa/.test(x.innerText)); b&&b.click();})()")
    ok = espera("!!document.querySelector('#sl-painel .sm-svg')", 8); J(LIB); time.sleep(.3); return acts, ok

try:
    c.aparelho(1440, 1000)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear()")
    # ---------- M1 ----------
    acts, ok = abrir_mapa()
    # VIS-08 (18/10): o seletor é o da VISOES-1, só ícone (svg, sem texto visível), com o nome "Ver em …" no aria-label
    ts = J("TS()") or []; vis = J("[...document.querySelectorAll('#sl-painel [data-visoes-local=sl].g2visoes button')].map(b=>[b.dataset.visao,b.getAttribute('aria-pressed'),b.getAttribute('aria-label'),!!b.querySelector('svg')&&!N(b.innerText)])") or []
    leg = J("TXT('.sm-leg')")
    chk('M1 "Planejar no mapa ›" abre a visão Mapa (seletor pelo ícone: Ver em tabela · Ver em mapa) com os 8 talhões da Santa Rita e a legenda',
        acts and ok and len(ts) == 8 and vis == [['lista', 'false', 'Ver em tabela', True], ['mapa', 'true', 'Ver em mapa', True]] and leg, [acts, ok, len(ts), vis, leg])
    # ---------- M2 ----------
    # talhões de um cultivo só (sem parcelas) e disponíveis: a cultura nova é escolhida diferente da atual de cada um, para todos mudarem
    cand = [x for x in ts if not any(k in ' '.join(x['l']) for k in ('Indisponível', 'parcelas'))]
    alvo = [x['t'] for x in cand][:3]; atual = {x['t']: (x['l'][1] if len(x['l']) > 1 else '') for x in cand}
    for t in alvo: J(f"TAP({json.dumps(t)})"); time.sleep(.25)
    J(LIB); cont = J("TXT('.sm-cont')"); tit = J("TXT('.sm-pn h3')"); sel = [x['t'] for x in (J("TS()") or []) if x['sel'] == 'true']
    chk('M2 tocar em 3 talhões marca os 3: contagem com área e painel "Planejar 3 talhões"', len(alvo) == 3 and sorted(sel) == sorted(alvo) and cont.startswith('3 talhões ·') and cont.endswith('ha') and tit == 'Planejar 3 talhões', [alvo, sel, cont, tit])
    # ---------- M3 ----------
    cults = [o for o in (J("OPTS('Cultura para os talhões marcados')") or []) if o[0]]
    cult = next((o[0] for o in cults if not any(atual[t].startswith(o[1]) or atual[t].startswith(o[0]) for t in alvo)), cults[0][0] if cults else '')
    J(f"SEL('Cultura para os talhões marcados',{json.dumps(cult)})"); time.sleep(.4); J(LIB)
    pls = [o for o in (J("OPTS('Plano para os talhões marcados')") or []) if o[0]]
    if pls: J(f"SEL('Plano para os talhões marcados',{json.dumps(pls[0][0])})"); time.sleep(.3)
    J("(()=>{const b=document.getElementById('sm-aplicar'); b&&b.click();})()"); time.sleep(.6); J(LIB)
    st3 = ' '.join(J("[...PN().querySelectorAll('[role=status]')].map(x=>N(x.innerText))") or [])
    import re
    recus = sorted(set(re.findall(r'\b([A-Z]\d{1,2}) · (?:Cultura|Plano agronômico)', st3)))
    mudou = [t for t in alvo if t not in recus]
    ts3 = {x['t']: x for x in (J("TS()") or [])}
    chk(f'M3 aplicar {cult} e plano aos 3: os que podem mudar mudam ao vivo (marca de alterado); o que tem O.S. em execução é recusado com o motivo',
        cult and mudou and all(any(cult in z for z in ts3[t]['l']) and ts3[t]['mud'] == '1' for t in mudou)
        and all(ts3[t]['mud'] == '0' and 'em execução' in st3 for t in recus), [cult, alvo, recus, mudou, {t: ts3.get(t) for t in alvo}, st3[:300]])
    # M3b (defeito achado em 18/10 e corrigido): a recusa do "Salvar alterações" aparece no mapa, talhão a talhão, e não só na Tabela
    J("(()=>{const b=document.getElementById('sl-salvar'); b&&b.click();})()"); time.sleep(.8); J(LIB)
    al = J("TXT('.sm-err')"); ts3b = {x['t']: x for x in (J("TS()") or [])}
    chk('M3b salvar sem variedade: o mapa mostra "A corrigir antes de salvar" com cada talhão e o motivo, e o rótulo do talhão vira "A corrigir"',
        al.startswith('A corrigir antes de salvar') and all((t + ' · Variedade') in al for t in mudou) and all('A corrigir' in ts3b[t]['l'] for t in mudou), [al, {t: ts3b[t]['l'] for t in mudou}])
    vari = J("(()=>{const i=[...PN().querySelectorAll('input')].find(x=>x.getAttribute('aria-label')==='Variedade para os talhões marcados'); const d=i&&document.getElementById(i.getAttribute('list')); return d&&d.options.length?d.options[0].value:'';})()")
    J(f"SEL('Variedade para os talhões marcados',{json.dumps(vari)})"); time.sleep(.3)
    J("(()=>{const b=document.getElementById('sm-aplicar'); b&&b.click();})()"); time.sleep(.6); J(LIB)
    salvarT = J("N((document.getElementById('sl-salvar')||{}).innerText||'')") or ''
    # ---------- M4 ----------
    leg0 = J("TXT('.sm-leg')"); J("(()=>{const b=[...document.querySelectorAll('#sl-painel [aria-label=\"Colorir por\"] button')].find(b=>N(b.innerText)==='Plano'); b&&b.click();})()"); time.sleep(.4); J(LIB)
    leg1 = J("TXT('.sm-leg')"); pr = J("[...document.querySelectorAll('#sl-painel [aria-label=\"Colorir por\"] button')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>N(b.innerText))")
    chk('M4 "Colorir por" Plano muda a legenda', leg1 and leg1 != leg0 and pr == ['Plano'], [leg0, leg1, pr])
    # ---------- M6 (Esc) e M5 ----------
    J("PN().dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}))"); time.sleep(.4); J(LIB)
    s6 = [x['t'] for x in (J("TS()") or []) if x['sel'] == 'true']; aberto = J("!!document.querySelector('#sl-painel .sm-svg')")
    J(f"TAP({json.dumps(alvo[0])})"); time.sleep(.4); J(LIB)
    um = J("[...document.querySelectorAll('#sl-painel .sm-pn button.sl-lk')].filter(VIS).map(b=>N(b.innerText))") or []
    chk('M5 um talhão só: o painel traz as ações da linha (Ajustar insumos, Dividir, Ver na tabela)',
        any('Ajustar insumos' in x for x in um) and any('Dividir' in x for x in um) and any('Ver na tabela' in x for x in um), um)
    J("(()=>{const g=[...document.querySelectorAll('#sl-painel .sm-svg .sm-t')].find(g=>g.getAttribute('data-t')===%s); g&&g.focus(); g&&g.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));})()" % json.dumps(alvo[1])); time.sleep(.4); J(LIB)
    s6b = [x['t'] for x in (J("TS()") or []) if x['sel'] == 'true']
    chk('M6 Esc limpa a seleção sem fechar o mapa; Enter no talhão com foco marca o talhão', s6 == [] and aberto and alvo[1] in s6b, [s6, aberto, s6b])
    # ---------- M7 ----------
    J("(()=>{const b=document.getElementById('sl-salvar'); b&&b.click();})()"); time.sleep(1.0)
    acts2, ok2 = abrir_mapa(); ts7 = {x['t']: x for x in (J("TS()") or [])}
    lab7 = {t: ts7.get(t, {}).get('l', []) for t in alvo}; mud7 = [ts7.get(t, {}).get('mud') for t in alvo]
    chk(f'M7 com a variedade ({vari}) e salvar: ao reabrir, os que mudaram mostram {cult} e os recusados seguem como estavam, sem marca de alterado',
        ok2 and vari and salvarT.startswith('Salvar alterações (') and all(any(cult in z for z in lab7[t]) for t in mudou) and all(not any(cult in z for z in lab7[t]) for t in recus) and mud7 == ['0'] * len(alvo), [vari, salvarT, lab7, mud7])
    e1 = J("window.__e") or []
    # ---------- M9 ----------
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear()"); acts9, ok9 = abrir_mapa()
    J("(()=>{const b=document.querySelector('#sl-painel [data-visoes-local=sl] [data-visao=lista]'); b&&b.click();})()"); time.sleep(.5); J(LIB)
    labs = J("[...document.querySelectorAll('#sl-painel input[type=checkbox]')].map(i=>i.getAttribute('aria-label')||'')") or []
    par = sorted(x[7:] for x in labs if re.match(r'^Marcar T1-[A-Z]$', x)); inteiro = next((x[7:] for x in labs if re.match(r'^Marcar T[2-9]$', x)), '')
    pa, pb = (par + ['', ''])[:2]
    META = "(rot=>{const i=[...document.querySelectorAll('#sl-painel input')].find(x=>x.getAttribute('aria-label')==='Meta de '+rot); return i?i.value:null;})"
    AREA = "(rot=>{const i=[...document.querySelectorAll('#sl-painel input')].find(x=>{const l=x.getAttribute('aria-label')||''; return l==='Área de '+rot||l.startsWith('Área de '+rot+' (');}); return i?Number(String(i.value).replace(/\\./g,'').replace(',','.')):null;})"
    m0 = {r: J(f"{META}({json.dumps(r)})") for r in (pa, pb, inteiro)}; a9 = {r: J(f"{AREA}({json.dumps(r)})") for r in (pa, inteiro)}
    for r in (pa, inteiro): J("(()=>{const i=[...document.querySelectorAll('#sl-painel input[type=checkbox]')].find(i=>i.getAttribute('aria-label')==='Marcar '+%s); i&&i.click();})()" % json.dumps(r)); time.sleep(.3)
    J("(()=>{const b=document.querySelector('#sl-painel [data-visoes-local=sl] [data-visao=mapa]'); b&&b.click();})()"); time.sleep(.6); J(LIB)
    t1 = next((x for x in (J("TS()") or []) if x['t'] == 'T1'), {}); cont9 = J("TXT('.sm-cont')"); lst9 = J("TXT('.sm-pn')"); apT9 = J("N((document.getElementById('sm-aplicar')||{}).innerText||'')")
    ha9 = sum(v for v in a9.values() if v); ha_txt = ('%.2f' % ha9).rstrip('0').rstrip('.').replace('.', ',')
    novo = '71' if m0.get(pa) != '71' else '72'
    J(f"SEL('Meta para os talhões marcados',{json.dumps(novo)})"); time.sleep(.3)
    J("(()=>{const b=document.getElementById('sm-aplicar'); b&&b.click();})()"); time.sleep(.6); J(LIB)
    st9 = ' '.join(J("[...PN().querySelectorAll('[role=status]')].map(x=>N(x.innerText))") or [])
    J("(()=>{const b=document.querySelector('#sl-painel [data-visoes-local=sl] [data-visao=lista]'); b&&b.click();})()"); time.sleep(.5); J(LIB)
    m1 = {r: J(f"{META}({json.dumps(r)})") for r in (pa, pb, inteiro)}
    chk('M9 seleção parcial da Tabela no Mapa: T1 "em parte" (mixed, 1 de 2), contagem "(1 em parte)" com a área só das linhas marcadas e a parcela na lista; "Aplicar" muda só as 2 linhas anunciadas',
        ok9 and pa and pb and inteiro and t1.get('sel') == 'mixed' and any('Em parte · 1 de 2' in z for z in t1.get('l', [])) and '(1 em parte)' in cont9 and cont9.startswith('2 talhões')
        and ha_txt in cont9 and ('em parte: ' + pa) in lst9 and '(1 em parte)' in apT9 and 'de 2 linhas' in st9
        and m1.get(pa) == novo and m1.get(inteiro) == novo and m1.get(pb) == m0.get(pb),
        [pa, pb, inteiro, t1, cont9, ha_txt, apT9, st9[:200], m0, m1, lst9[:300]])
    e1 = e1 + (J("window.__e") or [])
    # ---------- M8 ----------
    c.aparelho(390, 844, toque=True); acts3, ok3 = abrir_mapa()
    sw = J("[document.documentElement.scrollWidth, innerWidth]"); e2 = J("window.__e") or []
    chk('M8 390 px sem rolagem horizontal; nenhum erro de JavaScript', ok3 and sw and sw[0] <= sw[1] + 1 and not e1 and not e2, [ok3, sw, e1, e2])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK + FAIL} ok')
sys.exit(1 if FAIL else 0)
