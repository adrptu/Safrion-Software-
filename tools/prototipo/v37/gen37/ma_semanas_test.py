# -*- coding: utf-8 -*-
"""EX-53 D11b · semanas equivalentes no cartão "Backlog da oficina" do Painel › Manutenção (KPI-PCM-08; ESPECIFICACAO §7, l.432):
HH da especialidade ÷ capacidade semanal informada na CF-06 (capacidadeDe, PR #132). No Chrome a 1440 × 900 e 390 × 844; tudo pela tela.
  S1 sem capacidade: nenhuma especialidade com semanas; a dica diz "capacidade semanal não configurada" com as especialidades
  S2 o gestor informa, na CF-06, 30 HH/semana de Mecânico para o Zé: o cartão mostra "Mecânico <HH> (<HH ÷ 30> semana[s])" (oráculo sobre os
     dados crus da Manutenção) e a dica "Mecânico 30 HH/semana (1 pessoa)"; as outras especialidades seguem sem número
  S3 o calendário da Oficina muda na CD-04: a dedicação do Zé deixa de valer; o Mecânico volta a ficar sem número e a dica diz "capacidade a revisar"
  S4 a 1440 e a 390 px o cartão cabe na largura e a página não rola de lado
  S5 nenhum erro de JavaScript
Contraprova: o render da composição 5bc0b340 (sem o consumidor) reprova S2 (o cartão não mostra semanas) e S3.
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B ma_semanas_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:900])

# oráculo: HH por especialidade das ordens A liberar, Liberadas e Em execução, refeito sobre os dados crus (a definição do acordo, PR #47)
ORA = r"""(()=>{ const c=window.__man.manGet(), esp={};
  Object.values(c.oms).filter(o=>['A liberar','Liberadas','Em execução'].indexOf(o.etapa)>=0).forEach(o=>{ const t=Number(o.tempo); if(t>0){ const e=o.esp||'sem especialidade'; esp[e]=(esp[e]||0)+t; } });
  return esp; })()"""
CARD = r"""(()=>{ const k=[...document.querySelectorAll('[role=tabpanel] .pg-card')].filter(x=>x.getClientRects().length).find(x=>/Backlog da oficina/.test(x.innerText));
  if(!k) return null; const s=k.querySelector('.pg-sub'), t=k.querySelector('.pg-tip'), r=k.getBoundingClientRect();
  return {sub:s?s.innerText.replace(/\s+/g,' ').trim():'', dica:t?t.getAttribute('data-dica')||'':'', right:r.right, vw:innerWidth}; })()"""
F = lambda v: ('%.1f' % v).replace('.', ',').replace(',0', '') if abs(v - round(v)) < 1e-9 else ('%.1f' % v).replace('.', ',')
SETV = "((k,val)=>{ const i=document.getElementById(k); if(!i) return 'sem '+k; const P=i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:(i.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; })"
BTN = "((t)=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(a=>a.getClientRects().length); const b=a&&[...a.querySelectorAll('button')].find(b=>(b.innerText||'').trim()===t); if(!b) return false; b.click(); return true; })"
port, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda p: f'http://127.0.0.1:{port}/{p}'
erros = []
def card(w=1440, h=900):
    c.aparelho(w, h); c.goto(U('PG.dc.html#mod=man'), 2.4); erros.extend(J("window.__e") or []); return J(CARD) or {}
def semanas(sub): return [x for x in sub.replace('\u00a0', ' ').split(' — ')[0].split(' · ') if 'semana' in x]
try:
    c.aparelho(1440, 900); c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
    c.goto(U('MA.dc.html'), 1.2); esp = J(ORA) or {}; print('      oráculo HH por especialidade:', esp)
    k1 = card(); print('      S1:', k1)
    chk('S1 sem capacidade: nenhuma especialidade com semanas; a dica diz "capacidade semanal não configurada" com as especialidades',
        bool(k1) and not semanas(k1.get('sub', '')) and 'capacidade semanal não configurada: ' in k1.get('dica', '') and all(e in k1['dica'] for e in esp if e != 'sem especialidade'), k1)
    # S2 · CF-06 › Capacidade semanal da manutenção: o Zé dedica 30 HH/semana a Mecânico
    c.goto(U('CF-06.dc.html'), 1.8)
    ab = J("(()=>{ const r=[...document.querySelectorAll('[data-g2g=g_cap] [role=row][data-rid]')].find(r=>/Zé/.test(r.innerText)); if(!r) return 'sem linha'; (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); return 'ok'; })()"); time.sleep(.6)
    sets = [J(SETV + "('c6_h0','30')"), J(SETV + "('c6_motivo','teste ma_semanas: dedicação do Zé à mecânica')")]; time.sleep(.3)
    salvo = J(BTN + "('Salvar dedicação')"); time.sleep(.9)
    k2 = card(); hm = esp.get('Mecânico', 0); sm = hm / 30; esperado = 'Mecânico ' + F(hm) + ' (' + F(sm) + ' ' + ('semana' if sm < 2 else 'semanas') + ')'
    print('      S2:', ab, sets, salvo, k2)
    chk(f'S2 com 30 HH/semana de Mecânico: o cartão mostra "{esperado}" e a dica "Mecânico 30 HH/semana (1 pessoa)"; as outras sem número',
        ab == 'ok' and salvo and hm > 0 and esperado in k2.get('sub', '').replace(' ', ' ') and semanas(k2.get('sub', '').replace(' ', ' ')) == [esperado]
        and 'Mecânico 30 HH/semana (1 pessoa)' in k2.get('dica', ''), [esperado, k2])
    # S3 · CD-04: o calendário da Oficina muda; a dedicação do Zé deixa de valer até o gestor revisar
    c.goto(U('CD-04.dc.html'), 1.8)
    J("(()=>{ const t=[...document.querySelectorAll('[role=tab]')].find(t=>/^Equipes/.test(t.innerText.trim())); if(t) t.click(); })()"); time.sleep(.6)
    J("(()=>{ const r=[...document.querySelectorAll('[data-g2g=g_eq] [role=row][data-rid]')].find(r=>/Oficina/.test(r.innerText)); if(r) (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); })()"); time.sleep(.6)
    cal = J(SETV + "('fx_g_eq_cal','seg–sex · 08–18h')"); time.sleep(.3); s3 = J(BTN + "('Salvar')"); time.sleep(.9)
    k3 = card(); print('      S3:', cal, s3, k3)
    chk('S3 calendário da Oficina mudou na CD-04: o Mecânico volta a ficar sem semanas e a dica diz "capacidade a revisar"',
        cal == 'ok' and s3 and not semanas(k3.get('sub', '')) and 'capacidade a revisar' in k3.get('dica', '') and 'Mecânico' in k3.get('dica', ''), k3)
    larg = []
    for w, h in ((1440, 900), (390, 844)):
        kk = card(w, h); sw = J("document.scrollingElement.scrollWidth"); iw = J("innerWidth"); larg.append([w, bool(kk) and kk.get('right', 9e9) <= kk.get('vw', 0) + 1, sw <= iw])
    # S4 também confere a quebra: nenhuma linha do subtítulo começa com "·" (o separador fica preso à palavra anterior)
    solto = J(r"""(()=>{ const k=[...document.querySelectorAll('[role=tabpanel] .pg-card')].find(x=>/Backlog da oficina/.test(x.innerText)); const s=k&&k.querySelector('.pg-sub'); return !!s&&/(^|[^\u00a0])·/.test(s.textContent); })()""")
    chk('S4 a 1440 e 390 px o cartão cabe na largura, a página não rola de lado e nenhum "·" pode abrir linha', all(x[1] and x[2] for x in larg) and not solto, [larg, solto])
    chk('S5 nenhum erro de JavaScript', not erros, erros[:5])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK+FAIL} ok')
sys.exit(1 if FAIL else 0)
