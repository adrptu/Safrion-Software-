# -*- coding: utf-8 -*-
"""rev95 · sonda de navegador do PR #95 (AGRO-06) no AG-02 real: registrar um laudo com os 15 analitos (um 0, um vazio, LD = 0) a 1440 e
a 390 (toque) e conferir no estado do domínio (c.solo.laudos) o que foi gravado; erro do domínio com o painel aberto; repetido; teclado
(Tab/Enter/Esc), foco e alvo de toque do summary; nomes acessíveis. Dados sintéticos.
Uso (de gen37/): env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B rev95_sonda.py <RENDER_DIR> [1440|390]"""
import os, sys, json, time
GEN = os.getcwd(); sys.path.insert(0, GEN)
from comp_lib import Chrome, servir
R = os.path.abspath(sys.argv[1]); LARGS = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else '1440,390').split(',')]
OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)
LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.DLG=()=>[...document.querySelectorAll('aside[role=dialog]')].filter(VIS).pop()||null;
window.SETV=(el,val)=>{ const P=el.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(el,val);
  el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; };
window.Q=(lab)=>{ const d=DLG(); return d?d.querySelector('[aria-label="'+lab+'"]'):null; };
window.BTN=(t,root)=>{ const r=root||document; return [...r.querySelectorAll('button,summary,a')].filter(VIS).find(b=>N(b.innerText)===t)||null; };
'ok'"""
VALS = [('pH', '5,4', 'CaCl₂'), ('P', '14', 'mg/dm³'), ('MO', '28', 'g/dm³'), ('Ca', '3,90', 'cmolc/dm³'), ('Mg', '1,40', 'cmolc/dm³'), ('K', '0,08', 'cmolc/dm³'),
        ('H+Al', '3,82', 'cmolc/dm³'), ('Al', '0', 'cmolc/dm³'), ('S', '9', 'mg/dm³'), ('B', '0,32', 'mg/dm³'), ('Cu', '1,1', 'mg/dm³'), ('Fe', '38', 'mg/dm³'),
        ('Mn', '6,5', 'mg/dm³'), ('Zn', '', 'mg/dm³'), ('Argila', '380', 'g/kg')]
p, srv = servir(R); c = Chrome(); J = c.js
try:
    for W in LARGS:
        toque = W < 800; H = 844 if toque else 1000; tag = f'[{W}]'
        c.aparelho(W, H, toque=toque)
        c.goto(f'http://127.0.0.1:{p}/Main.dc.html'); J("localStorage.clear(); sessionStorage.clear(); localStorage.setItem('safrion.perfilDemo','\"Ana\"')")
        c.goto(f'http://127.0.0.1:{p}/AG-02.dc.html'); J(LIB)
        J("(()=>{ const b=[...document.querySelectorAll('header button')].find(b=>N(b.innerText)==='Registrar laudo'); b.click(); })()"); time.sleep(.5)
        nomes = J("(()=>{ const d=DLG(); return d?[...d.querySelectorAll('input[aria-label^=\"Valor de \"]')].map(i=>i.getAttribute('aria-label').slice(9)):null; })()") or []
        chk(f'{tag} formulário com os 15 analitos na ordem do laudo', nomes == [v[0] for v in VALS], nomes)
        # leitor de tela: nome de cada campo (valor e unidade) e dos detalhes
        an = J("(()=>{ const d=DLG(); if(!d) return null; return [...d.querySelectorAll('input[aria-label^=\"Valor de \"]')].map(i=>{ const row=i.closest('div').parentElement; const s=row.querySelector('select'); const det=row.querySelector('details');"
               " return [i.getAttribute('aria-label'), s&&s.getAttribute('aria-label'), s&&s.value, det?[...det.querySelectorAll('input')].map(x=>x.getAttribute('aria-label')):null, i.getAttribute('inputmode')||i.inputMode]; }); })()") or []
        chk(f'{tag} leitor de tela: valor, unidade e os três detalhes com nome próprio por analito', len(an) == 15 and all(x[0] == 'Valor de ' + v[0] and x[1] == 'Unidade de ' + v[0] and x[3] == ['Método de ' + v[0], 'Limite de detecção de ' + v[0], 'Qualificador de ' + v[0]] and x[4] == 'decimal' for x, v in zip(an, VALS)), an[:3])
        # contexto e valores (setter nativo + input/change, como os testes do solo)
        J("(()=>{ const d=DLG(); SETV(d.querySelector('#rl_tal'),'T3'); })()"); time.sleep(.2)
        J("(()=>{ const d=DLG(); BTN('Ontem',d).click(); })()"); time.sleep(.2)
        for a, v, u in VALS:
            J(f"(()=>{{ const i=Q('Valor de {a}'); SETV(i,{json.dumps(v)}); }})()"); time.sleep(.05)
            J(f"(()=>{{ const s=Q('Unidade de {a}'); if(s.value!=={json.dumps(u)}) SETV(s,{json.dumps(u)}); }})()"); time.sleep(.05)
        # teclado: foco no summary do Cu, Enter abre; Tab vai ao Método; o LD 0 é digitado; os detalhes continuam abertos depois das atualizações
        J("(()=>{ const s=[...DLG().querySelectorAll('summary')].find(x=>/· Cu$/.test(N(x.innerText))); s.focus(); })()")
        foco0 = J("N(document.activeElement.innerText)")
        c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.25)   # Enter real (keyDown com texto \r, como patest/pa_lista_test); sem o texto o Chrome não ativa o summary
        aberto = J("(()=>{ const s=[...DLG().querySelectorAll('summary')].find(x=>/· Cu$/.test(N(x.innerText))); return s.parentElement.open; })()")
        anel = J("(()=>{ const e=document.activeElement; const cs=getComputedStyle(e); return [e.tagName, cs.outlineStyle, cs.outlineWidth, cs.outlineColor, e.matches(':focus-visible')]; })()")
        c.tab(1); time.sleep(.1); f1 = J("document.activeElement.getAttribute('aria-label')")
        c.tab(1); time.sleep(.1); f2 = J("document.activeElement.getAttribute('aria-label')")
        c.call('Input.insertText', {'text': '0'}); time.sleep(.1); c.tab(1); time.sleep(.3)
        f3 = J("document.activeElement.getAttribute('aria-label')")
        ainda = J("(()=>{ const s=[...DLG().querySelectorAll('summary')].find(x=>/· Cu$/.test(N(x.innerText))); return [s.parentElement.open, Q('Limite de detecção de Cu').value]; })()")
        chk(f'{tag} teclado: Enter no summary abre os detalhes do Cu; Tab segue Método → Limite; o LD 0 digitado fica e os detalhes continuam abertos',
            foco0 == 'Método e limites · Cu' and aberto and f1 == 'Método de Cu' and f2 == 'Limite de detecção de Cu' and f3 == 'Qualificador de Cu' and ainda == [True, '0'], [foco0, aberto, f1, f2, f3, ainda])
        chk(f'{tag} foco visível no summary (anel)', anel and anel[4] and anel[1] != 'none' and anel[2] not in ('0px', ''), anel)
        # digitação real (Input.insertText) no valor do B: foco e valor ficam depois do re-render
        J("Q('Valor de B').focus(); Q('Valor de B').select();"); c.call('Input.insertText', {'text': '0,32'}); time.sleep(.2)
        fb = J("[document.activeElement.getAttribute('aria-label'), Q('Valor de B').value]")
        chk(f'{tag} digitação real no valor de B: foco e texto mantidos', fb == ['Valor de B', '0,32'], fb)
        # erro do domínio (sem laboratório): painel aberto, valores, unidades e detalhes preservados
        J("(()=>{ const d=DLG(); [...d.querySelectorAll('.so-pe button')].filter(VIS).find(b=>N(b.innerText)==='Registrar laudo').click(); })()"); time.sleep(.5)
        e1 = J("(()=>{ const d=DLG(); if(!d) return null; const al=[...d.querySelectorAll('[role=alert]')].filter(VIS).map(x=>N(x.innerText)).join(' | ');"
               " const det=[...d.querySelectorAll('summary')].find(x=>/· Cu$/.test(N(x.innerText))).parentElement.open; return [al, Q('Valor de Al').value, Q('Unidade de K').value, Q('Limite de detecção de Cu').value, det, Q('Valor de Zn').value]; })()")
        chk(f'{tag} erro do domínio (sem laboratório): painel aberto com a mensagem; Al 0, K em cmolc/dm³, LD do Cu 0 e detalhes abertos preservados; Zn vazio',
            e1 and 'Informe o laboratório' in e1[0] and e1[1:] == ['0', 'cmolc/dm³', '0', True, ''], e1)
        J("(()=>{ const d=DLG(); SETV(d.querySelector('#rl_lab'),'Agrolab'); })()"); time.sleep(.2)
        n0 = J("Object.keys(__solo.get().laudos||{}).length")
        J("(()=>{ const d=DLG(); [...d.querySelectorAll('.so-pe button')].filter(VIS).find(b=>N(b.innerText)==='Registrar laudo').click(); })()"); time.sleep(.6)
        st = J("(()=>{ const L=__solo.get().laudos||{}; const ks=Object.keys(L); const l=L[ks[ks.length-1]]; return l?{n:ks.length,id:l.id,sit:l.sit,tal:l.tal,lab:l.lab,ext:l.ext,an:l.an}:null; })()")
        g = {x['a']: x for x in (st or {}).get('an', [])}
        esperado = [v[0] for v in VALS if v[1] != '']
        chk(f'{tag} domínio: 1 laudo novo, Aguardando validação, T3 · Agrolab · Mehlich-1, 14 analitos (Zn vazio omitido)',
            st and st['n'] == n0 + 1 and st['sit'] == 'Aguardando validação' and st['tal'] == 'T3' and st['lab'] == 'Agrolab' and st['ext'] == 'Mehlich-1' and [x['a'] for x in st['an']] == esperado, st)
        chk(f'{tag} domínio: Al 0 explícito (não ausente), Cu com LD "0", vírgula → ponto (pH 5.4, Ca 3.90), unidades trocadas preservadas (K cmolc/dm³, Argila g/kg)',
            g.get('Al', {}).get('v') == '0' and g.get('Cu', {}).get('ld') == '0' and g.get('pH', {}).get('v') == '5.4' and g.get('Ca', {}).get('v') == '3.90'
            and g.get('K', {}).get('un') == 'cmolc/dm³' and g.get('Argila', {}).get('un') == 'g/kg' and 'Zn' not in g, [g.get(k) for k in ('Al', 'Cu', 'pH', 'Ca', 'K', 'Argila', 'Zn')])
        chk(f'{tag} domínio: P e K sem método herdam o extrator (Mehlich-1); MO sem método fica vazio',
            g.get('P', {}).get('met') == 'Mehlich-1' and g.get('K', {}).get('met') == 'Mehlich-1' and g.get('MO', {}).get('met') == '', [g.get('P'), g.get('K'), g.get('MO')])
        pan = J("(()=>{ const d=DLG(); return d?N(d.innerText).slice(0,160):''; })()") or ''
        chk(f'{tag} depois de gravar: painel do laudo novo aberto (Aguardando validação)', st and (st['id'] + ' · T3') in pan and 'Aguardando validação' in pan, pan)
        # repetido: mesma amostra de novo → recusa, painel aberto, nada gravado
        J("(()=>{ const d=DLG(); [...d.querySelectorAll('button')].filter(VIS).find(b=>N(b.innerText)==='Fechar').click(); })()"); time.sleep(.3)
        J("(()=>{ const b=[...document.querySelectorAll('header button')].find(b=>N(b.innerText)==='Registrar laudo'); b.click(); })()"); time.sleep(.4)
        J("(()=>{ const d=DLG(); SETV(d.querySelector('#rl_tal'),'T3'); })()"); time.sleep(.15); J("BTN('Ontem',DLG()).click()"); time.sleep(.15); J("SETV(DLG().querySelector('#rl_lab'),'Agrolab')"); time.sleep(.15)
        J("SETV(Q('Valor de K'),'40')"); time.sleep(.15)
        J("(()=>{ const d=DLG(); [...d.querySelectorAll('.so-pe button')].filter(VIS).find(b=>N(b.innerText)==='Registrar laudo').click(); })()"); time.sleep(.5)
        rp = J("(()=>{ const d=DLG(); return [d?[...d.querySelectorAll('[role=alert]')].filter(VIS).map(x=>N(x.innerText)).join(' | '):'', Object.keys(__solo.get().laudos||{}).length, d?N(d.querySelector('h2').innerText):'']; })()")
        chk(f'{tag} repetido (mesmo talhão, profundidade, coleta e laboratório): recusa no painel aberto e nada gravado', rp and 'já está registrada como' in rp[0] and rp[1] == n0 + 1 and rp[2] == 'Registrar laudo de solo', rp)
        # Esc com alterações: avisa; Esc de novo fecha
        J("Q('Valor de K').focus()"); c.tecla('Escape', 'Escape', 27); time.sleep(.3)
        e_1 = J("(()=>{ const d=DLG(); return d?[N(d.querySelector('h2').innerText), [...d.querySelectorAll('[role=alert]')].filter(VIS).map(x=>N(x.innerText)).join(' | ')]:null; })()")
        chk(f'{tag} Esc com alterações: o painel fica e avisa "Há alterações não salvas"', e_1 and e_1[0] == 'Registrar laudo de solo' and 'Há alterações não salvas' in e_1[1], e_1)
        J("BTN('Continuar editando',DLG()).click()"); time.sleep(.2)
        # alvo de toque e largura
        geo = J("(()=>{ const d=DLG(); const ss=[...d.querySelectorAll('summary')].filter(VIS); const h=ss.map(s=>Math.round(s.getBoundingClientRect().height)); const w=ss.map(s=>Math.round(s.getBoundingClientRect().width));"
                " const ins=[...d.querySelectorAll('input[aria-label^=\"Valor de \"],select[aria-label^=\"Unidade de \"]')].map(e=>Math.round(e.getBoundingClientRect().height));"
                " const seta=ss.filter(s=>[...s.children].some(x=>x.classList.contains('g2seta'))).length; const mk=getComputedStyle(ss[0]).display;"
                " return {n:ss.length,hMin:Math.min(...h),hMax:Math.max(...h),wMin:Math.min(...w),inMin:Math.min(...ins),seta,display:mk,lado:d.scrollWidth<=d.clientWidth+1,pag:document.documentElement.scrollWidth<=innerWidth+1,fonteSum:getComputedStyle(ss[0]).fontSize}; })()")
        print('INFO', tag, 'geometria', json.dumps(geo, ensure_ascii=False), flush=True)
        chk(f'{tag} sem estouro lateral no formulário e na página', geo and geo['lado'] and geo['pag'], geo)
        alvo = 44 if toque else 24
        chk(f'{tag} summary "Método e limites" com alvo ≥ {alvo} px de altura', geo and geo['hMin'] >= alvo, geo)
        if toque:
            r_ = J("(()=>{ const s=[...DLG().querySelectorAll('summary')].find(x=>/· P$/.test(N(x.innerText))); s.scrollIntoView({block:'center'}); const r=s.getBoundingClientRect(); return [r.left+Math.min(r.width/2,40), r.top+r.height/2]; })()")
            c.toque(r_[0], r_[1]); time.sleep(.3)
            tp = J("(()=>{ const s=[...DLG().querySelectorAll('summary')].find(x=>/· P$/.test(N(x.innerText))); return s.parentElement.open; })()")
            chk(f'{tag} toque no summary do P abre os detalhes', tp is True, tp)
        # paradas de Tab reais: do × (Fechar) até o botão Registrar laudo do rodapé, com os detalhes fechados
        J("(()=>{ [...DLG().querySelectorAll('details')].forEach(d=>d.open=false); DLG().querySelector('#rl_x').focus(); })()"); time.sleep(.2)
        n_tab = 0; fim_tab = ''
        for _ in range(200):
            c.tab(1); n_tab += 1; fim_tab = J("(()=>{ const e=document.activeElement; return (e&&N(e.innerText||e.getAttribute('aria-label')||e.id||e.tagName)).slice(0,40); })()")
            if fim_tab == 'Registrar laudo' and J("!!document.activeElement.closest('.so-pe')"): break
        print('INFO', tag, 'paradas de Tab reais do × até Registrar laudo (detalhes fechados):', n_tab, fim_tab, flush=True)
        c.shot(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'rev95_{W}_{os.path.basename(R)}.png'))
        er = J("(window.__errs||[]).filter(e=>e.indexOf(\"reading 'g2toast'\")<0).join(' | ')") or ''
        chk(f'{tag} nenhum erro de JS', not er, er)
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {"OK" if not FAIL else "FALHA"} {len(OK)}/{len(OK) + len(FAIL)}' + ('' if not FAIL else ' · falhas: ' + ' || '.join(FAIL)))
sys.exit(1 if FAIL else 0)
