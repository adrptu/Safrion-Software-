# -*- coding: utf-8 -*-
"""MA-VINCULO · medição de cliques e digitação (AGENTS §3.3), o mesmo cenário antes (base) e depois, no navegador, com o resultado conferido.
Cada ação da pessoa conta 1 clique (lista nativa: abrir + escolher = 2); digitação = caracteres digitados. Perfil Otávio, estado zerado.
  M1 achar os ativos sem plano, a partir da entrada do módulo Manutenção (resultado: a lista só com os 4 sem plano)
  M2 vincular 3 tratores a um plano (PM-11, posto no estado igual nas duas versões), sem execução registrada: contar de agora
  M3 vincular 1 ativo sem plano (Gotejo T7) ao plano do mesmo grupo (PM-07), a partir da visão Ativos
Detecta a versão pela página (painel vl = depois; painel vk = base). Uso: python3 ma_vinculo_medida.py [saida.json]"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from ma_lib import MA
from ma_vinculo_test import PM11
CONT = {'cliques': 0, 'digitos': 0}
def zera(): CONT.update(cliques=0, digitos=0)
m = MA(1440, 1000); J = m.J
def clk(t, root='', n=1):
    r = m.clk(t, root, w=.6); CONT['cliques'] += n
    if r != 'ok': raise RuntimeError(f'não achei "{t}": {r}')
def sel(css, val):   # lista nativa: abrir + escolher
    if not m.setv(css, val): raise RuntimeError('sem ' + css)
    CONT['cliques'] += 2; time.sleep(.3)
def chk_label(txt, root):
    r = J(f"(()=>{{const l=[...document.querySelectorAll('{root} label')].find(l=>l.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(txt)})); if(!l) return false; l.querySelector('input').click(); return true;}})()")
    if not r: raise RuntimeError('sem ' + txt)
    CONT['cliques'] += 1; time.sleep(.3)
def js_clk(expr):
    if not J(expr): raise RuntimeError('falhou: ' + expr[:80])
    CONT['cliques'] += 1; time.sleep(.8)
RES = {}
try:
    m.ir('vis=ativos', perfil='Otávio', limpa=True); novo = bool(J("!!(window.__man&&window.__man.manVincular)")); RES['versao'] = 'depois' if novo else 'base'
    # M1
    m.ir('', perfil='Otávio', limpa=True, pagina='MOD-MAN.dc.html'); zera()
    if novo:
        js_clk("(()=>{const a=document.querySelector('a.mod-aviso'); if(!a) return false; a.click(); return true;})()"); time.sleep(1)
    else:
        js_clk("(()=>{const a=[...document.querySelectorAll('a.mod-cartao')].find(a=>a.innerText.trim()==='Ativos'); if(!a) return false; a.click(); return true;})()"); time.sleep(1)
        sel('main select[aria-label="Filtrar por pendência"]', 'Sem plano')
    rows = sorted(m.linhas(0)); RES['M1'] = dict(CONT, ok=rows == ['a07', 'a09', 'a10', 'a12'], linhas=rows)
    # M2
    m.ir('vis=ativos', perfil='Otávio', limpa=True); J(PM11); m.ir('plano=PM-11'); zera()
    if novo:
        clk('Vincular ativos', 'main'); clk('Contar de agora', '#vl-painel'); clk('Vincular 3 ativos ao PM-11', '#vl-painel'); time.sleep(.6)
    else:
        for i, aid in enumerate(('a02', 'a03', 'a04')):
            clk('Vincular ativo', 'main')
            if i: sel('#vk_aid', aid)
            chk_label('Sem histórico', '#vk-painel'); clk('Salvar', '#vk-painel'); time.sleep(.5)
    v = m.man("['a02','a03','a04'].map(a=>{ const x=m.vinc['PM-11|'+a]; return x&&!x.fim?x.marco.leit:null; })")
    RES['M2'] = dict(CONT, ok=v == [2988, 5120, 3410], bases=v)
    # M3
    m.ir('vis=ativos', perfil='Otávio', limpa=True); zera()
    if novo:
        js_clk("(()=>{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==='a12'&&r.getClientRects().length); const a=r&&[...r.querySelectorAll('a')].find(a=>/^Vincular ao PM-07/.test(a.innerText.trim())); if(!a) return false; a.click(); return true;})()")
        clk('Contar de agora', '#vl-painel'); clk('Vincular ao PM-07', '#vl-painel'); time.sleep(.6)
    else:
        js_clk("(()=>{const b=[...document.querySelectorAll('main button[aria-pressed]')].find(b=>b.innerText.trim().startsWith('Planos')); if(!b) return false; b.click(); return true;})()")
        js_clk("(()=>{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==='PM-07'&&r.getClientRects().length); if(!r) return false; (r.querySelector('.g2pw')||r).click(); return true;})()")
        clk('Editar plano', 'main'); chk_label('Gotejo T7', '#np-painel'); clk('Salvar', '#np-painel'); time.sleep(.5)
        clk('Vincular ativo', 'main'); chk_label('Sem histórico', '#vk-painel'); clk('Salvar', '#vk-painel'); time.sleep(.5)
    x = m.man("(()=>{ const v=m.vinc['PM-07|a12']; return v&&!v.fim?v.marco.leit:null; })()")
    RES['M3'] = dict(CONT, ok=x == 5210, base=x)
    RES['erros_js'] = m.errs()
finally:
    m.fim()
print(json.dumps(RES, ensure_ascii=False))
if len(sys.argv) > 1: open(sys.argv[1], 'w', encoding='utf-8').write(json.dumps(RES, ensure_ascii=False, indent=1))
