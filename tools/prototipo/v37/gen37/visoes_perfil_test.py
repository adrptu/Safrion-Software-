# -*- coding: utf-8 -*-
"""V2-3-PERFIL-01 (Codex 6179592748) · trocar o perfil sem recarregar relê a preferência do novo perfil (dados sintéticos).
CD-05 (g_forn): Ana agrupa por Papéis e acrescenta uma coluna; recarrega com o endereço limpo; troca para Caio pela UI → Caio sem
agrupamento, colunas padrão e endereço sem ?ag=; volta para Ana sem recarregar → agrupamento e colunas de Ana; recarregar mantém o de cada um.
Uso: python3 visoes_perfil_test.py (RENDER_DIR=<dir> serve outro _render; contraprova na versão sem a correção)."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
PG, G = 'CD-05.dc.html', 'g_forn'
SEL = '[aria-label="Trocar perfil de demonstração"]'
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:400], flush=True)

p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = f'http://127.0.0.1:{p}/{PG}'
def espera(cond, lim=6.0):
    t0 = time.time()
    while time.time() - t0 < lim:
        if J("(()=>{try{return !!(%s)}catch(e){return false}})()" % cond): return True
        time.sleep(.1)
    return False
def abre(): c.goto(U, .4); espera(f"document.querySelector('[data-g2g=\"{G}\"]')")
def grupos(): return J(f"document.querySelectorAll('[data-g2g=\"{G}\"] [role=row][data-rid^=\"grp@\"]').length")
def cabec(): return J(f"[...document.querySelectorAll('[data-g2g=\"{G}\"] [role=columnheader]')].filter(h=>h.getClientRects().length).map(h=>h.innerText.replace(/[⇅▾▴▲▼]/g,'').trim()).filter(Boolean)")
def busca(): return J("location.search")
def perfil(k):   # o seletor do menu lateral, como a pessoa troca
    J(f"""(()=>{{const i=document.querySelector({json.dumps(SEL)}); Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,{json.dumps(k)});
      i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()"""); time.sleep(.4)
def perfil_atual(): return J(f"(document.querySelector({json.dumps(SEL)})||{{value:''}}).value")
def agrupa(l):
    J(f"document.querySelector('[data-g2agb=\"{G}\"]').click()"); time.sleep(.25)
    return J("(()=>{const m=document.querySelector('[data-g2agm=\"%s\"]'); const i=m&&[...m.querySelectorAll('[role=menuitemradio]')].find(x=>x.innerText.trim().split('\\n')[0].trim()===%s); if(!i) return false; i.click(); return true;})()" % (G, json.dumps(l)))
def mais_coluna():   # marca a 1ª coluna oculta no painel "Colunas" e fecha
    J(f"document.querySelector('[data-g2cvb=\"{G}\"]').click()"); time.sleep(.3)
    l = J("(()=>{const i=[...document.querySelectorAll('[data-g2cv=\"%s\"] input[type=checkbox]')].find(i=>!i.checked&&!i.disabled); if(!i) return ''; const t=(i.closest('label')||i.parentElement).innerText.trim(); i.click(); return t;})()" % G); time.sleep(.3)
    J("(()=>{const b=[...document.querySelectorAll('[data-g2cv=\"%s\"] button')].find(b=>/^Fechar$/.test(b.innerText.trim())); if(b) b.click();})()" % G); time.sleep(.3)
    return l
try:
    c.aparelho(1440, 900, 1, False)
    c.goto(f'http://127.0.0.1:{p}/Main.dc.html', .2); J("localStorage.clear();sessionStorage.clear()")
    abre()
    if perfil_atual() != 'Ana': perfil('Ana')
    padrao = cabec()
    chk('P0 Ana abre sem agrupamento e com as colunas padrão', grupos() == 0 and perfil_atual() == 'Ana', [grupos(), perfil_atual(), padrao])
    chk('P1 Ana agrupa por Papéis: grupos aparecem e o endereço leva ?ag=', agrupa('Papéis') and (time.sleep(.4) or grupos()) > 0 and 'ag=' in busca(), [grupos(), busca()])
    n_ana = grupos()
    col = mais_coluna(); cols_ana = cabec()
    chk('P2 Ana acrescenta uma coluna', bool(col) and len(cols_ana) == len(padrao) + 1, [col, cols_ana, padrao])
    abre()   # endereço limpo, como no roteiro do Codex
    chk('P3 recarregar limpo como Ana mantém o agrupamento e as colunas dela', grupos() == n_ana and cabec() == cols_ana, [grupos(), n_ana, cabec()])
    perfil('Caio')
    chk('P4 trocar para Caio pela UI (sem recarregar): sem agrupamento, colunas padrão, endereço sem ?ag=',
        perfil_atual() == 'Caio' and grupos() == 0 and cabec() == padrao and 'ag=' not in busca(), [perfil_atual(), grupos(), cabec(), busca()])
    perfil('Ana')
    chk('P5 voltar para Ana sem recarregar: agrupamento e colunas de Ana, endereço com ?ag=',
        perfil_atual() == 'Ana' and grupos() == n_ana and cabec() == cols_ana and 'ag=' in busca(), [grupos(), n_ana, cabec(), busca()])
    perfil('Caio'); abre()
    chk('P6 recarregar como Caio: sem agrupamento e colunas padrão', perfil_atual() == 'Caio' and grupos() == 0 and cabec() == padrao, [perfil_atual(), grupos(), cabec()])
    perfil('Ana'); abre()
    chk('P7 recarregar como Ana: agrupamento e colunas de Ana', grupos() == n_ana and cabec() == cols_ana, [grupos(), cabec()])
    # endereço com ?ag= na chegada é contexto legítimo (link): vale para quem abre; a troca seguinte segue o perfil novo
    perfil('Caio'); c.goto(U + '?ag=quem', .4); espera(f"document.querySelector('[data-g2g=\"{G}\"]')")
    chk('P8 Caio chega por link com ?ag=: o link vale', perfil_atual() == 'Caio' and grupos() > 0, [perfil_atual(), grupos(), busca()])
    c.goto(U + '?ag=quem', .4); espera(f"document.querySelector('[data-g2g=\"{G}\"]')"); perfil('Ana'); perfil('Caio')
    chk('P9 depois do link, trocar de perfil segue a preferência do novo perfil (Caio: sem agrupamento)', grupos() == 0 and 'ag=' not in busca(), [grupos(), busca()])
    # colunas escolhidas e troca imediata, sem recarregar (o estado em memória da escolha não pode passar ao outro perfil)
    perfil('Ana'); abre(); col2 = mais_coluna(); cols_ana2 = cabec(); perfil('Caio')
    chk('P10 Ana acrescenta outra coluna e troca para Caio sem recarregar: Caio vê as colunas dele', bool(col2) and cabec() == padrao, [col2, cols_ana2, cabec()])
    perfil('Ana'); chk('P11 volta para Ana sem recarregar: as colunas que ela acabou de escolher', cabec() == cols_ana2, [cabec(), cols_ana2])
    chk('J sem erro de JS', not J("(window.__e||[]).length"), J("window.__e"))
finally:
    c.close() if hasattr(c, 'close') else None
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
