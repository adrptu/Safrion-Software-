# -*- coding: utf-8 -*-
"""ATIVO-UNICO · um cadastro de ativos (proprietário, 18/10/2026: "Tem cadastro de ativos no módulo manutenção e cadastros, resolva com códex a
melhor maneira de resolver isso"). Cadastros › Máquinas e instalações (CD-03) é a fonte única da identidade; a Manutenção (MA) é a visão
operacional do mesmo ativo. No Chrome a 1440 × 1000.
  U1 o Comboio CB-01 está no CD-03 (classe Veículo, carga 6.000 L), não só na Manutenção
  U2 máquina cadastrada no CD-03 aparece na Manutenção › Ativos com "Sem plano", sem condição nem leitura inventadas
  U3 renomear no CD-03 muda o nome na Manutenção
  U4 inativar no CD-03 deixa o ativo Inativo na Manutenção
  U5 Manutenção › ativo › "Editar cadastro ›" abre o CD-03 no formulário daquele ativo
  U6 a entrada da Manutenção abre com "Planejamento" (não "Cadastro")
  U7 F5: o cadastro novo continua no CD-03 e na Manutenção; nenhum erro de JavaScript
Contraprova: o render da v133 reprova U1, U2, U3, U4, U5 e U6.
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B ativo_unico_test.py"""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir

R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
OK = FAIL = 0
def chk(nome, cond, info=''):
    global OK, FAIL
    if cond: OK += 1; print('OK   ', nome)
    else: FAIL += 1; print('FALHA', nome, '·', str(info)[:600])

LIB = r"""
window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.ROWS=g=>{ const s=document.querySelector('[data-g2g='+g+']'); return s?[...s.querySelectorAll('[role=row][data-rid]')].map(r=>[r.getAttribute('data-rid'),N(r.innerText)]):null; };
window.OPEN=(g,txt)=>{ const s=document.querySelector('[data-g2g='+g+']'); const r=s&&[...s.querySelectorAll('[role=row][data-rid]')].find(r=>N(r.innerText).indexOf(txt)>=0); if(!r) return 'sem '+txt; (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); return 'ok'; };
window.FV=k=>{ const i=document.querySelector('aside[role=dialog] [id$="_'+k+'"]'); return i?i.value:null; };
window.SETV=(k,val)=>{ const i=document.querySelector('aside[role=dialog] [id$="_'+k+'"]'); if(!i) return 'sem '+k; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
  Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; };
window.BTN=t=>{ const b=[...document.querySelectorAll('aside[role=dialog] button')].filter(VIS).find(b=>N(b.innerText)===t); if(!b) return false; b.click(); return true; };
window.ADD=g=>{ const b=[...document.querySelectorAll('header button,main button')].filter(VIS).find(b=>/^(Criar|Cadastrar) máquina/.test(N(b.innerText))); if(!b) return false; b.click(); return N(b.innerText); };
'ok'"""

port, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda p: f'http://127.0.0.1:{port}/{p}'
def ir(pg, w=1.3):
    c.goto(U(pg), w); J(LIB); time.sleep(.3)
def dlg(): return J("(document.querySelector('aside[role=dialog]')||{}).innerText||''") or ''
def salvar(): J("BTN('Salvar')"); time.sleep(.8)
def ma_rows(): ir('MA.dc.html#vis=ativos', 1.6); return J("ROWS('g_at')") or []
def acha(rows, txt): return next((r for r in rows if txt in r[1]), None)

try:
    c.aparelho(1440, 1000)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear()")
    # ---------- U1 ----------
    ir('CD-03.dc.html'); r1 = acha(J("ROWS('g_atv')") or [], 'Comboio CB-01')
    if r1: J("OPEN('g_atv','Comboio CB-01')"); time.sleep(.5)
    f1 = [J("FV('classe')"), J("FV('carga_ve')"), J("FV('cont_ve')")]
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>/^(Cancelar|Fechar)$/.test(N(b.innerText))); b&&b.click();})()"); time.sleep(.3)
    chk('U1 Comboio CB-01 no CD-03: classe Veículo, carga 6.000 L e hodômetro de 48.200 km (só leitura, da Manutenção)',
        bool(r1) and f1[0] == 'Veículo' and str(f1[1]).replace('.', '') in ('6000',) and str(f1[2]).replace('.', '') in ('48200',), [r1, f1])
    # ---------- U2 ----------
    m0 = ma_rows(); n0 = len(m0)
    ir('CD-03.dc.html'); a2 = J("ADD('g_atv')"); time.sleep(.5)
    J("SETV('classe','Trator')"); time.sleep(.3); J("SETV('nome','Trator 09')"); J("SETV('pot_tr','120')"); J("SETV('custo_h','185')"); salvar()
    al2 = J("[...document.querySelectorAll('aside [role=alert]')].map(x=>N(x.innerText)).join(' | ')") or ''
    m1 = ma_rows(); t9 = acha(m1, 'Trator 09')
    chk('U2 "Trator 09" cadastrado no CD-03 aparece na Manutenção › Ativos com "Sem plano", sem condição nem leitura inventadas',
        a2 and len(m1) == n0 + 1 and t9 and 'Sem plano' in t9[1] and 'sem contador' in t9[1], [a2, al2, n0, len(m1), t9])
    # ---------- U3 ----------
    ir('CD-03.dc.html'); J("OPEN('g_atv','Trator 09')"); time.sleep(.5); J("SETV('nome','Trator 09 Ruivo')"); salvar()
    m2 = ma_rows(); t9b = acha(m2, 'Trator 09 Ruivo')
    chk('U3 renomear no CD-03 ("Trator 09 Ruivo") muda o nome na Manutenção', t9b is not None and not acha([r for r in m2 if r is not t9b], 'Trator 09'), [t9b])
    # ---------- U4 ----------
    ir('CD-03.dc.html'); J("OPEN('g_atv','Trator 09 Ruivo')"); time.sleep(.5); J("SETV('sit','Inativo')"); salvar()
    m3 = ma_rows(); t9c = acha(m3, 'Trator 09 Ruivo')
    chk('U4 inativar no CD-03 deixa o ativo inativo na Manutenção ("Ativo inativo", fora de Sem plano)', t9c and 'Ativo inativo' in t9c[1] and 'Sem plano' not in t9c[1], [t9c])
    # ---------- U5 ----------
    ir('MA.dc.html#vis=ativos', 1.6); J("OPEN('g_at','Pulverizador')"); time.sleep(.7)
    lk = J("(()=>{const a=[...document.querySelectorAll('a')].filter(VIS).find(a=>N(a.innerText)==='Editar cadastro ›'); return a?a.getAttribute('href'):null;})()")
    rid = (lk or '').split('#maq=')[-1]
    if lk: ir(lk, 1.6); time.sleep(.4)
    nome5 = J("FV('nome')"); t5 = J("(document.querySelector('aside[role=dialog] h2')||{}).innerText||''")
    chk('U5 Manutenção › ativo › "Editar cadastro ›" (CD-03.dc.html#maq=<id>) abre o formulário daquele ativo no CD-03',
        bool(lk) and lk.startswith('CD-03.dc.html#maq=') and nome5 and t5, [lk, nome5, t5])
    # ---------- U6 ----------
    ir('MOD-MAN.dc.html', 1.2); txt = J("N((document.querySelector('main')||document.body).innerText)") or ''
    chk('U6 a entrada da Manutenção abre com o bloco "Planejamento" (Ativos, Planos), sem "Cadastro"', 'Planejamento' in txt and 'Cadastro' not in txt.split('Execução')[0], txt[:300])
    # ---------- U7 ----------
    ir('CD-03.dc.html'); r7 = acha(J("ROWS('g_atv')") or [], 'Trator 09 Ruivo'); m4 = ma_rows(); e = J("window.__e") or []
    chk('U7 F5: "Trator 09 Ruivo" segue no CD-03 e na Manutenção; nenhum erro de JavaScript', bool(r7) and acha(m4, 'Trator 09 Ruivo') is not None and not e, [r7, e])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK + FAIL} ok')
sys.exit(1 if FAIL else 0)
