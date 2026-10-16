# -*- coding: utf-8 -*-
"""SAF-TAB (proprietário, 14/10: "essa tabela está horrível… muitas colunas… mais minimalistas"), no navegador, dados sintéticos:
T1 a 1440 a etapa 2 abre só com Talhão, Cultura, Plano agronômico, Área e Plantio; as outras 11 em "Colunas +11".
T2 sem coluna Situação: só o talhão que pede atenção (A conferir, Sobreposição) ganha ícone, com o estado no nome acessível; Planejado não.
T3 a célula do plano mostra só o plano (sem "Ajustar insumos"); o ajuste segue no painel da linha ("Ajustar insumos e doses de T7").
T4 o seletor "Unidade de produtividade" só aparece com a Meta à vista; mostrar a Meta pelo seletor de colunas traz o seletor.
T5 (15/10) linha sem botão solto: Dividir, Aplicar plano e Excluir no ⋯ da linha, com ícone.
T6 talhão com um só cultivo abre recolhido; com parcelas ou pendência, aberto.
T7 nota da área de ações sem a frase repetida ("sem plano não entram…") e sem referência técnica ("CD-02").
T8 a 390 as 3 primeiras (Talhão, Cultura, Plano agronômico). T11 a 390 o "Dividir" sai da linha e fica no painel do talhão.
T9 sem erro de JS.
Uso: python3 saf_tab_test.py (RENDER_DIR=<dir> serve outro _render)."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
ok_n = 0; falhas = []
def chk(nome, cond, det=''):
    global ok_n
    if cond: ok_n += 1; print('OK  ' + nome, flush=True)
    else: falhas.append(nome); print('FALHA ' + nome + ' · ' + str(det)[:500], flush=True)

p, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda x: f'http://127.0.0.1:{p}/{x}'
G = "[data-g2g=g_cult_S2627]"
def espera(cond, lim=8.0):
    t0 = time.time()
    while time.time() - t0 < lim:
        if J("(()=>{try{return !!(%s)}catch(e){return false}})()" % cond): return True
        time.sleep(.15)
    return False
def abre(w):
    c.aparelho(w, 1000 if w > 400 else 844, 1 if w > 400 else 2, w < 400)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear();sessionStorage.clear()")
    c.goto(U('SAF.dc.html#saf=S2627&etapa=2'), .6)
    espera("document.querySelectorAll('%s [role=row].g2ed').length>=5" % G)
def head(): return J("[...document.querySelectorAll('%s [role=columnheader]')].filter(h=>h.getClientRects().length).map(h=>h.innerText.replace(/[⇅▾▴▲▼]/g,'').replace(/\\s+/g,' ').trim()).filter(Boolean)" % G) or []
def linha(t): return J("(()=>{const r=[...document.querySelectorAll('%s [role=row].g2ed')].find(r=>{const c=r.querySelector('.g2c0'); return c&&c.innerText.replace(/[▾▸]/g,'').trim().split(/\\s+/)[0]===%s;}); return r||null;})()" % (G, json.dumps(t)))
def txt_linha(t): return J("(()=>{const r=[...document.querySelectorAll('%s [role=row].g2ed')].find(r=>{const c=r.querySelector('.g2c0'); return c&&c.innerText.replace(/[▾▸]/g,'').trim().split(/\\s+/)[0]===%s;}); return r?r.innerText.replace(/\\s+/g,' ').trim():'';})()" % (G, json.dumps(t))) or ''
def ico_de(t): return J("(()=>{const r=[...document.querySelectorAll('%s [role=row].g2ed')].find(r=>{const c=r.querySelector('.g2c0'); return c&&c.innerText.replace(/[▾▸]/g,'').trim().split(/\\s+/)[0]===%s;}); const i=r&&r.querySelector('.g2c0 [role=img]'); return i?i.getAttribute('aria-label'):'';})()" % (G, json.dumps(t))) or ''
def colunas_btn(): return J("(()=>{const b=document.querySelector('[data-g2cvb=g_cult_S2627]'); return b&&b.getClientRects().length?b.innerText.replace(/\\s+/g,' ').trim():'';})()") or ''
def seletor_un(): return J("[...document.querySelectorAll('main select, main [role=combobox]')].some(s=>s.getClientRects().length&&/Unidade de produtividade/i.test((s.getAttribute('aria-label')||'')+' '+((s.closest('label,span,div')||{}).innerText||'')))")
try:
    abre(1440)
    h = head()
    chk('T1 1440: abre com Talhão, Cultura, Plano agronômico, Área e Plantio', h == ['TALHÃO OU PARCELA', 'CULTURA', 'PLANO AGRONÔMICO', 'ÁREA', 'PLANTIO'], h)
    chk('T1b "Colunas +11" com as outras colunas', colunas_btn() == 'Colunas +11', colunas_btn())
    i_p1, i_t3 = ico_de('P1'), ico_de('T3')
    chk('T2 sem coluna Situação; P1 (a conferir) com ícone e o estado no nome acessível; T3 (planejado) sem ícone',
        'SITUAÇÃO' not in h and i_p1.startswith('Situação: A conferir') and i_t3 == '', [i_p1, i_t3])
    t7 = txt_linha('T7')
    chk('T3 plano só com o nome, sem "Ajustar insumos" na célula', 'Mamão Formosa produção' in t7 and 'Ajustar insumos' not in t7, t7)
    J("(()=>{const r=[...document.querySelectorAll('%s [role=row].g2ed')].find(r=>{const c=r.querySelector('.g2c0'); return c&&c.innerText.trim().split(/\\s+/)[0]==='T7';}); const x=r&&[...r.querySelectorAll('[role=cell]')].find(z=>!z.querySelector('button,input')&&z.innerText.trim()&&!z.classList.contains('g2c0')); if(x) x.click();})()" % G)
    espera("document.querySelector('aside[role=dialog]')")
    pn = J("(document.querySelector('aside[role=dialog]')||{}).innerText||''") or ''
    chk('T3b o painel da linha T7 oferece "Ajustar insumos e doses de T7"', 'Ajustar insumos e doses de T7' in pn, pn[:300])
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>/^(Cancelar|Fechar)$/.test(b.innerText.trim())||b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()"); time.sleep(.4)
    chk('T4 sem a Meta à vista, sem o seletor "Unidade de produtividade"', not seletor_un(), seletor_un())
    J("(document.querySelector('[data-g2cvb=g_cult_S2627]')||{click(){}}).click()"); espera("document.querySelector('[data-g2cv=g_cult_S2627]')")
    J("(()=>{const l=[...document.querySelectorAll('[data-g2cv=g_cult_S2627] label')].find(x=>x.innerText.trim()==='Meta'); if(l) l.querySelector('input').click();})()"); time.sleep(.5)
    h2 = head()
    chk('T4b mostrar a Meta pelo seletor de colunas traz a coluna e o seletor de unidade', 'META' in h2 and seletor_un(), [h2, seletor_un()])
    J("(()=>{const b=[...document.querySelectorAll('[data-g2cv=g_cult_S2627] button')].find(b=>/Restaurar padrão/.test(b.innerText)); if(b) b.click();})()"); time.sleep(.4)
    J("(()=>{const b=[...document.querySelectorAll('[data-g2cv=g_cult_S2627] button')].find(b=>/^Fechar$/.test(b.innerText.trim())); if(b) b.click();})()"); time.sleep(.3)
    # 15/10/2026 (proprietário: "coloque os 3 pontinhos e coloque todos botões de ação ali com ícones"): Dividir, Aplicar plano e Excluir no ⋯ da linha
    sec = J("(()=>{const r=[...document.querySelectorAll('%s [role=row].g2ed')].find(r=>/^T3/.test((r.querySelector('.g2c0')||{}).innerText||'')); if(!r) return null; const m=r.querySelector('.g2mais'); const its=m?[...m.nextElementSibling.querySelectorAll('[role=menuitem]')]:[]; return {solto:[...r.querySelectorAll('button')].filter(b=>b.offsetParent&&!b.classList.contains('g2mais')&&!b.classList.contains('g2car')).map(b=>b.innerText.trim()), menu:its.map(i=>[i.textContent.trim(),!!i.querySelector('svg')])};})()" % G) or {}
    chk('T5 linha T3: nenhum botão solto; o ⋯ tem Dividir, Aplicar plano e Excluir, cada um com ícone', sec.get('solto') == [] and [x[0] for x in sec.get('menu', [])] == ['Dividir', 'Aplicar plano', 'Excluir'] and all(x[1] for x in sec.get('menu', [])), sec)
    exp = J("(()=>{const ex=t=>{const r=[...document.querySelectorAll('%s [role=row].g2ed')].find(r=>{const c=r.querySelector('.g2c0'); return c&&c.innerText.replace(/[▾▸]/g,'').trim().split(/\\s+/)[0]===t;}); const b=r&&r.querySelector('[aria-expanded]'); return b?b.getAttribute('aria-expanded'):null;}; return [ex('T1'),ex('T2'),ex('P1'),ex('P2')];})()" % G)
    chk('T6 T1 (parcelas) e P1 (a conferir) abertos; T2 e P2 (um cultivo) recolhidos', exp == ['true', 'false', 'true', 'false'], exp)
    nota = J("(()=>{const a=document.querySelector('[data-acoes]'); return a?(a.innerText+' '+[...a.querySelectorAll('.acoes-menu [role=menuitem]')].map(b=>b.textContent).join(' ')).replace(/\\s+/g,' '):''})()") or ''
    tro = J("[...document.querySelectorAll('[data-acoes] button')].filter(b=>b.getClientRects().length).map(b=>b.innerText.replace(/\\s+/g,' ').trim()).filter(t=>/Trocar safra/.test(t))") or []
    chk('T10 "‹ Trocar safra" embaixo, com a seta de voltar (14/10: "faltou setinha pra trás")', tro == ['‹ Trocar safra'], tro)
    # 15/10 ("retire essas descrições"): a área de ações não descreve; fica o atalho que resolve e os botões
    chk('T7 área de ações sem descrição: só "Informar colheita de P1 ›" e os botões ("Aplicar plano em 4 cultivos")', 'sem plano agronômico' not in nota and 'começa em' not in nota and 'CD-02' not in nota and 'Informar colheita de P1 ›' in nota and 'Aplicar plano em 4 cultivos' in nota, nota[:300])
    c.shot(os.path.join(HERE, '_probe_saf_tab_1440.png')) if os.environ.get('SAF_TAB_SHOT') else None
    abre(390)
    h3 = head()
    chk('T8 390: as 3 primeiras (Talhão, Cultura, Plano agronômico)', h3 == ['TALHÃO OU PARCELA', 'CULTURA', 'PLANO AGRONÔMICO'], h3)
    # print do proprietário (14/10, celular): "Dividir" em toda linha ocupa a coluna; no celular sai da linha e fica no painel do talhão
    dv = J("[...document.querySelectorAll('%s [role=row] button')].filter(b=>b.getClientRects().length&&b.innerText.trim()==='Dividir').length" % G)
    J("(()=>{const r=[...document.querySelectorAll('%s [role=row].g2ed')].find(r=>{const c=r.querySelector('.g2c0'); return c&&c.innerText.trim().split(/\\s+/)[0]==='T7';}); const x=r&&[...r.querySelectorAll('[role=cell]')].find(z=>!z.querySelector('button,input')&&z.innerText.trim()&&!z.classList.contains('g2c0')); if(x) x.click();})()" % G)
    espera("document.querySelector('aside[role=dialog]')")
    ok_b = J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Dividir T7 em parcelas'); if(!b) return false; b.click(); return true;})()")
    espera("/Dividir T7 em parcelas/.test((document.querySelector('aside[role=dialog]')||{}).innerText||'')")
    tit = J("(document.querySelector('aside[role=dialog] h2')||{}).innerText||''") or ''
    chk('T11 390: sem "Dividir" nas linhas; o toque no T7 abre o painel com "Dividir T7 em parcelas", que abre a divisão', dv == 0 and ok_b and 'Dividir T7 em parcelas' in tit, [dv, ok_b, tit])
    chk('T9 sem erro de JS', not J("(window.__e||[]).length"), J("window.__e"))
finally:
    c.close() if hasattr(c, 'close') else None
print(f'RESULTADO: {ok_n}/{ok_n + len(falhas)}' + (' · FALHAS: ' + '; '.join(falhas) if falhas else ''))
sys.exit(1 if falhas else 0)
