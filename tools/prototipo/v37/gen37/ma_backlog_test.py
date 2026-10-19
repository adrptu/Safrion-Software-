# -*- coding: utf-8 -*-
"""EX-53 M7a · backlog por especialidade (KPI-PCM-08) no Painel › Manutenção e na carga do Kanban da MA, pela soma única manHH.
No Chrome a 1440 × 900 e 390 × 844.
  K1 o cartão "Backlog da oficina" mostra o total de HH previstas das ordens A liberar, Liberadas e Em execução (oráculo refeito no teste
     sobre os dados crus), as especialidades da maior para a menor carga e, na dica, "capacidade semanal não configurada"; leva a MA.dc.html#vis=ordens
  K2 a 1440 e a 390 px o cartão cabe na largura e a página não rola de lado
  K3 a carga das colunas do Kanban da MA bate com o oráculo da coluna
  K4 uma ordem Liberada sem tempo previsto não vira 0: o cartão e a coluna avisam "1 sem estimativa" e o total não muda
  K5 nenhum erro de JavaScript
Contraprova: o render da v141 reprova K1, K2 e K4 (não há cartão e a coluna não avisa).
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B ma_backlog_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:900])

# oráculo independente: a definição do acordo (PR #47, 6259217691) sobre os dados crus da Manutenção
ORA = r"""(etapas=>{ const c=window.__man.manGet(), f=n=>Number(n).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:1});
  const os=Object.values(c.oms).filter(o=>etapas.indexOf(o.etapa)>=0); let hh=0, sem=0; const esp={};
  os.forEach(o=>{ const t=Number(o.tempo); if(t>0){ hh+=t; const e=o.esp||'sem especialidade'; esp[e]=(esp[e]||0)+t; } else sem++; });
  return {n:os.length, hh, sem, v:os.length>sem?f(hh)+' HH':(os.length?'Sem estimativa':'0 HH'), esp:Object.keys(esp).sort((a,b)=>esp[b]-esp[a]||(a<b?-1:1)).map(k=>k+' '+f(esp[k]))}; })"""
CARD = r"""(()=>{ const k=[...document.querySelectorAll('[role=tabpanel] .pg-card')].filter(x=>x.getClientRects().length).find(x=>/Backlog da oficina/.test(x.innerText));
  if(!k) return null; const s=k.querySelector('.pg-sub'), a=k.querySelector('a.pg-cl'), t=k.querySelector('.pg-tip'), r=k.getBoundingClientRect();
  return {v:((k.querySelector('.pg-v')||{}).innerText||'').trim(), sub:s?s.innerText.replace(/\s+/g,' ').trim():'', dica:t?t.getAttribute('data-dica')||'':'', href:a?a.getAttribute('href'):'', right:r.right, vw:innerWidth}; })()"""
KB = r"""(()=>{ const out={}; [...document.querySelectorAll('[aria-label="Kanban das ordens"] .os-kbcol')].forEach(col=>{ const t=col.querySelector('[data-dica-de]');
  if(t) out[t.textContent.trim()]=(col.children[1]&&col.children[1].textContent||'').replace(/\s+/g,' ').trim(); }); return out; })()"""
port, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda p: f'http://127.0.0.1:{port}/{p}'
erros = []
def card(w, h):
    c.aparelho(w, h); c.goto(U('PG.dc.html#mod=man'), 2.4); return J(CARD)
try:
    c.aparelho(1440, 900); c.goto(U('Main.dc.html'), .3); J("localStorage.clear()")
    c.goto(U('MA.dc.html'), 1.2); o = J(ORA + "(['A liberar','Liberadas','Em execução'])"); k = card(1440, 900)
    print('      oráculo:', o); print('      cartão :', k)
    chk('K1 cartão "Backlog da oficina": total e especialidades do oráculo, "capacidade semanal não configurada" na dica e destino MA › Ordens',
        bool(k) and k['v'] == o['v'] and k['sub'].replace('\u00a0',' ').split(' — ')[0] == ' · '.join(o['esp']) and 'capacidade semanal não configurada' in k['dica'] and k['href'] == 'MA.dc.html#vis=ordens', [k, o])
    larg = []
    for w, h in ((1440, 900), (390, 844)):
        kk = card(w, h); sw = J("document.scrollingElement.scrollWidth"); iw = J("innerWidth"); larg.append([w, bool(kk) and kk['right'] <= kk['vw'] + 1, sw <= iw])
        erros += J("window.__e") or []
    chk('K2 a 1440 e 390 px o cartão cabe na largura e a página não rola de lado', all(x[1] and x[2] for x in larg), larg)
    # K3 · Kanban da MA: carga de cada coluna = oráculo da coluna
    c.aparelho(1440, 900); c.goto(U('MA.dc.html#vis=ordens'), 1.6)
    J("(()=>{ const b=document.querySelector('[data-visao=kanban]')||[...document.querySelectorAll('button')].find(x=>/Ver em kanban/.test(x.getAttribute('aria-label')||x.title||'')); b&&b.click(); })()"); time.sleep(.8)
    kb = J(KB) or {}
    res = []
    for et in ('Liberadas', 'Em execução'):
        oc = J(ORA + "(" + json.dumps([et]) + ")"); txt = kb.get(et, '')
        res.append([et, oc['v'], oc['n'] == 0 or txt == oc['v'], txt[:120]])
    chk('K3 a carga das colunas Liberadas e Em execução do Kanban bate com o oráculo da coluna', bool(kb) and all(x[2] for x in res), [res, list(kb)[:6]])
    erros += J("window.__e") or []
    # K4 · ordem Liberada sem tempo: o aviso aparece no cartão e na coluna; o total não muda
    alvo = J("(()=>{ const c=window.__man.manGet(); const o=Object.values(c.oms).find(o=>o.etapa==='Liberadas'&&Number(o.tempo)>0); return o?o.id:null; })()")
    J("(id=>window.__man.manMudar(null,(m)=>{ m.oms[id].tempo=undefined; return {msg:''}; }))(" + json.dumps(alvo) + ")")
    c.goto(U('MA.dc.html#vis=ordens'), 1.4); o2 = J(ORA + "(['A liberar','Liberadas','Em execução'])")
    J("(()=>{ const b=document.querySelector('[data-visao=kanban]')||[...document.querySelectorAll('button')].find(x=>/Ver em kanban/.test(x.getAttribute('aria-label')||x.title||'')); b&&b.click(); })()"); time.sleep(.8)
    kb2 = J(KB) or {}; col = kb2.get('Liberadas', '')
    k4 = card(1440, 900)
    chk('K4 ordem Liberada sem tempo não vira 0: "1 sem estimativa" no cartão e na coluna Liberadas; o total segue o oráculo',
        bool(alvo) and bool(k4) and '1 sem estimativa' in k4['sub'] and k4['v'] == o2['v'] and o2['sem'] == 1 and 'sem estimativa' in col, [alvo, k4, o2, col])
    erros += J("window.__e") or []
    chk('K5 nenhum erro de JavaScript', not erros, erros[:5])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK+FAIL} ok')
sys.exit(1 if FAIL else 0)
