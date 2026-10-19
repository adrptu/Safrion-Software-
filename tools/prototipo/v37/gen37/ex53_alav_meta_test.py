# -*- coding: utf-8 -*-
"""EX-53 D11 no Painel (Claude): as Alavancas do resultado e os cartões de custo e de preço médio leem a meta vigente da CF-06.
No Chrome a 1440 × 900; a meta é gravada pela tela, como o gestor faria.
  L1 sem meta: chips cinza e um aviso só, "Meta não configurada", no título do bloco
  L2 meta de custo 5 % / atenção 10 % (menor é melhor): a cor de cada chip de custo segue o oráculo refeito no teste sobre os dados
     crus (window.__pg.pgDados); parcial ou sem desvio fica cinza; o título passa a "Meta de preço não configurada"
  L3 meta de venda 0 % / atenção −2 % (maior é melhor): a cor do chip de preço segue o oráculo (preço médio × referência); venda em
     saca a conferir ou sem referência fica cinza; com as duas metas, o aviso some
  L4 o cartão de custo (Agrícola) e o de preço médio (Comercial) mostram o mesmo resultado da meta que a Alavanca
  L5 nenhum erro de JavaScript
Contraprova: o render sem a ligação (composição 1cf11a81) reprova L2, L3 e L4 (tudo continua cinza).
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B ex53_alav_meta_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:900])

BG = {'rgb(228, 243, 233)': 'green', 'rgb(255, 243, 214)': 'yellow', 'rgb(253, 232, 230)': 'red', 'rgb(238, 241, 238)': 'gray'}
TXT = {'green': 'Meta atendida', 'yellow': 'Atenção à meta', 'red': 'Fora da meta'}
def classe(v, meta, aten, maior):   # a regra do acordo D11, refeita aqui: alvo incluso no verde, limiar incluso no amarelo
    if maior: return 'green' if v >= meta else 'yellow' if v >= aten else 'red'
    return 'green' if v <= meta else 'yellow' if v <= aten else 'red'
CRU = r"""(()=>{ const P=window.__pg, D=P.pgDados(P.cenGet());
  return {cus:(D.custos||[]).map(g=>({id:g.id,cult:g.cultura,d:g.desvio_exec_pct,parcial:!!g.parcial,nome:g.cultura+' · '+g.faz+' '+g.saf})),
          pre:(D.precos||[]).map(x=>({cu:x.cu,prod:x.prod,medC:x.medC===null?null:Number(x.medC),ref:x.ref?Number(x.ref.p):null,amb:(x.amb||[]).length}))}; })()"""
ALAV = r"""(()=>[...document.querySelectorAll('tr[data-pg-alav]')].map(r=>{ const td=r.querySelectorAll('td'), ch=[td[1],td[2]].map(t=>t.querySelector('a.pg-chip'));
  return {id:r.getAttribute('data-pg-alav'), cus:getComputedStyle(ch[0]).backgroundColor, pre:getComputedStyle(ch[1]).backgroundColor,
          cons:td[1].querySelector('small').innerText.replace(/\s+/g,' ').trim(), prer:td[2].querySelector('small').innerText.replace(/\s+/g,' ').trim()}; }))()"""
AVISO = "(()=>{ const s=[...document.querySelectorAll('.pg-semmeta')].find(x=>x.getClientRects().length); return s?s.innerText.trim():''; })()"
CARD = r"""(nome=>{ const k=[...document.querySelectorAll('[role=tabpanel] .pg-card')].filter(x=>x.getClientRects().length).find(x=>x.innerText.indexOf(nome)>=0);
  return k?k.innerText.replace(/\s+/g,' ').trim():null; })"""
# CF-06 pela tela (as funções da página não são globais)
ABRE = "((id)=>{ const r=[...document.querySelectorAll('[data-g2g=g_metas] [role=row][data-rid]')].find(r=>r.getAttribute('data-rid')===id); if(!r) return 'sem linha '+id; (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); return 'ok'; })"
SETV = "((k,val)=>{ const i=document.getElementById(k); if(!i) return 'sem '+k; const P=i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype; Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; })"
BTN = "((t)=>{ const b=[...document.querySelectorAll('aside[role=dialog] button')].filter(b=>b.getClientRects().length).find(b=>(b.innerText||'').trim()===t); if(!b) return false; b.click(); return true; })"
LINHA = "((id)=>{ const r=[...document.querySelectorAll('[data-g2g=g_metas] [role=row][data-rid]')].find(r=>r.getAttribute('data-rid')===id); return r?r.innerText.replace(/\\s+/g,' ').trim():null; })"

port, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda p: f'http://127.0.0.1:{port}/{p}'
erros = []
def grava(id, valor, aten):
    c.goto(U('CF-06.dc.html'), 1.8); J(ABRE + "(" + json.dumps(id) + ")"); time.sleep(.5)
    for k, x in (('m6_valor', valor), ('m6_atencao', aten), ('m6_motivo', 'teste ex53_alav_meta')): J(SETV + "(" + json.dumps(k) + "," + json.dumps(str(x)) + ")")
    time.sleep(.3); J(BTN + "('Salvar meta')"); time.sleep(.8); return J(LINHA + "(" + json.dumps(id) + ")") or ''
def painel(h=''):
    c.goto(U('PG.dc.html' + h), 2.4); erros.extend(J("window.__e") or [])
def esperado(cru):
    """cor esperada de cada linha das Alavancas pelo oráculo; mc/mv = (meta, atenção) de custo e de venda, ou None"""
    pre = {}
    for x in cru['pre']: pre.setdefault(x['cu'], x)
    def cus(g): return 'gray' if (MC is None or g['parcial'] or g['d'] is None) else classe(float(g['d']), MC[0], MC[1], False)
    def ven(g):
        p = pre.get(g['cult'])
        if MV is None or not p or p['medC'] is None or not p['ref'] or p['amb']: return 'gray'
        return classe((p['medC'] - p['ref']) / p['ref'] * 100, MV[0], MV[1], True)
    return {g['id']: (cus(g), ven(g)) for g in cru['cus']}
def confere(rot):
    cru = J(CRU); al = J(ALAV) or []; exp = esperado(cru); res = []
    for a in al:
        e = exp.get(a['id']); vis = (BG.get(a['cus']), BG.get(a['pre']))
        txt_ok = all((TXT[k] in t) if k != 'gray' else not any(v in t for v in TXT.values()) for k, t in ((e[0], a['cons']), (e[1], a['prer']))) if e else False
        res.append([a['id'], e, vis, e == vis and txt_ok, a['cons'], a['prer']])
    return res, cru
try:
    c.aparelho(1440, 900); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); 1")
    MC = MV = None
    painel(); r0, cru = confere('L1'); av0 = J(AVISO)
    print('      dados crus:', json.dumps(cru, ensure_ascii=False)[:600])
    chk('L1 sem meta: chips cinza e um aviso só, "Meta não configurada", no título do bloco',
        bool(r0) and all(x[3] for x in r0) and all(x[2] == ('gray', 'gray') for x in r0) and av0 == 'Meta não configurada', [r0, av0])
    MC = (5, 10); g1 = grava('custo-desvio', 5, 10)
    painel(); r1, _ = confere('L2'); av1 = J(AVISO)
    chk('L2 meta de custo 5/10: a cor e o texto de cada chip de custo seguem o oráculo; o título passa a "Meta de preço não configurada"',
        '5' in g1 and bool(r1) and all(x[3] for x in r1) and any(x[1][0] != 'gray' for x in r1) and av1 == 'Meta de preço não configurada', [g1, r1, av1])
    MV = (0, -2); g2 = grava('venda-referencia', 0, -2)
    painel(); r2, _ = confere('L3'); av2 = J(AVISO)
    chk('L3 meta de venda 0/−2: a cor e o texto de cada chip de preço seguem o oráculo; com as duas metas, o aviso some',
        '0' in g2 and bool(r2) and all(x[3] for x in r2) and any(x[1][1] != 'gray' for x in r2) and av2 == '', [g2, r2, av2])
    # L4 · os cartões dos módulos dizem o mesmo que a Alavanca
    exp = esperado(cru); alvo = next((g for g in cru['cus'] if exp[g['id']][0] != 'gray'), None)
    painel('#mod=agr'); ca = J(CARD + "(" + json.dumps(alvo['nome'] if alvo else '#') + ")") or ''
    pv = next((p for p in cru['pre'] if p['medC'] is not None and p['ref'] and not p['amb']), None)
    cv_exp = classe((pv['medC'] - pv['ref']) / pv['ref'] * 100, MV[0], MV[1], True) if pv else None
    painel('#mod=com'); cvt = J(CARD + "(" + json.dumps('Preço médio · ' + (pv['prod'] if pv else '#')) + ")") or ''
    chk('L4 o cartão de custo (Agrícola) e o de preço médio (Comercial) mostram o resultado da meta igual ao da Alavanca',
        bool(alvo) and TXT[exp[alvo['id']][0]] in ca and bool(cv_exp) and TXT[cv_exp] in cvt and 'Meta não configurada' not in ca + cvt, [alvo and alvo['nome'], ca, pv, cv_exp, cvt])
    chk('L5 nenhum erro de JavaScript', not erros, erros[:5])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK+FAIL} ok')
sys.exit(1 if FAIL else 0)
