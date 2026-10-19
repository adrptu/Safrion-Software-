# -*- coding: utf-8 -*-
"""AGUA-SOLO-IRR · Água no solo na Irrigação (proprietário, 18/10/2026: "agua no solo é no submenu irrigação, onde se define a capacidade de
campo do solo para os calculos, deficit e recomendações de irrigação"), no Chrome a 1440 × 1000 e 390 × 844.
  W1 IR-01 tem o bloco Água no solo com as 4 medições; o AG-02 não tem mais a grade e leva à Irrigação pelo link (#agua rola até o bloco)
  W2 coluna "No balanço": AGS-003 em uso no Pivô 2 com AFD e gatilho; AGS-004 sem PMP diz que vale o limiar
  W3 painel do setor P2: CAD 45 mm, AFD 24,8 mm (f 0,55 da FAO-56), déficit em % da CAD e gatilho do limiar
  W4 medição nova do Pivô 19 com CAD 3 mm: AFD 1,5 mm vira o gatilho e o setor passa de "Sem necessidade" a "A programar"
  W5 medição nova do P1 com CAD 6 mm: o balanço passa a ser dia a dia com o teto da CAD (FAO-56, eq. 85–86; Codex 6252809331): 8,4 → 4,5 mm,
     o mesmo do oráculo diário independente abaixo (a chuva de 20/09 cai depois que o solo chegou na CAD), e a lâmina líquida também
  W6 PMP ≥ CC é recusado junto ao campo, sem gravar
  W7 fração f do setor: 0,10 no P2 faz a AFD (4,5 mm) virar o gatilho; vazio volta à referência da cultura
  W8 F5: a medição e o efeito ficam; "Registrar medição de água no solo" do setor abre o formulário com fazenda e talhão
  W9 390 px sem rolagem horizontal; nenhum erro de JavaScript
Contraprova: o render da v133 reprova W1, W3, W4, W5 e W7.
Uso (de gen37/): env CHROME_BIN=… SAFRION_DADOS=sintetico [RENDER_DIR=…] python3 -B agua_irr_test.py"""
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
window.SEC=t=>{ const g={'Setores':'g_set','Água no solo':'g_agua','Laudos':'g_lau'}[t]; return g?document.querySelector('[data-g2g='+g+']'):null; };
window.TIT=t=>[...document.querySelectorAll('main div,main span')].some(e=>e.children.length===0&&N(e.innerText)===t&&VIS(e));
window.ROWS=t=>{ const s=SEC(t); return s?[...s.querySelectorAll('[role=row][data-rid]')].filter(VIS).map(r=>[r.getAttribute('data-rid'),N(r.innerText)]):null; };
window.ROWIN=(t,rid)=>{ const s=SEC(t); const r=s&&s.querySelector('[role=row][data-rid="'+rid+'"]'); if(!r) return 'sem '+rid; (r.querySelector('.g2pw')||r.querySelector('[role=cell]')||r).click(); return 'ok'; };
window.FV=k=>{ const i=document.querySelector('aside[role=dialog] [id$="_'+k+'"]'); return i?i.value:null; };
window.SETV=(k,val)=>{ const i=document.querySelector('aside[role=dialog] [id$="_'+k+'"]'); if(!i) return 'sem '+k; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
  Object.getOwnPropertyDescriptor(P,'value').set.call(i,val); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; };
window.BTN=t=>{ const b=[...document.querySelectorAll('aside[role=dialog] button')].filter(VIS).find(b=>N(b.innerText)===t); if(!b) return false; b.click(); return true; };
window.ALERT=()=>[...document.querySelectorAll('aside [role=alert]')].filter(VIS).map(x=>N(x.innerText)).join(' | ');
window.TOAST=()=>[...document.querySelectorAll('[role=status]')].map(x=>N(x.innerText)).filter(Boolean).join(' | ');
window.ADD=t=>{ const s=document.getElementById('ir-agua'); const b=s&&[...s.querySelectorAll('button')].filter(VIS).find(b=>/Registrar medição/.test(b.innerText)); if(!b) return false; b.click(); return true; };
'ok'"""

port, srv = servir(R); c = Chrome(); J = c.js
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))"})
U = lambda p: f'http://127.0.0.1:{port}/{p}'
def espera(js, ate=15.0):
    t0 = time.time()
    while time.time() - t0 < ate:
        try:
            if J(js): return True
        except Exception: pass
        time.sleep(.15)
    return False
def ir(pg, faz=None):
    c.goto(U(pg), 1.0); J(LIB)
    if faz:
        J("(()=>{const s=document.querySelector('select[aria-label=\"Filtrar por fazenda\"]'); if(!s) return; Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(s,%s); s.dispatchEvent(new Event('change',{bubbles:true}));})()" % json.dumps(faz))
        time.sleep(.6)
    espera("!!SEC('Setores')||!!SEC('Laudos')", 6)
def setor(rid):
    J(f"ROWIN('Setores',{json.dumps(rid)})"); espera("!!document.querySelector('aside[role=dialog]')", 4); time.sleep(.3)
def fecha():
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>/^(Cancelar|Fechar)$/.test(N(b.innerText))||b.getAttribute('aria-label')==='Fechar'); b&&b.click();})()"); time.sleep(.4)
def linha(rid): return dict(J("ROWS('Setores')") or []).get(rid, '')
def medir(faz, tal, cc, pmp, z='30', data='2026-09-22'):
    J("ADD('Água no solo')"); espera("!!document.querySelector('aside[role=dialog]')", 4); time.sleep(.3)
    J(f"SETV('faz',{json.dumps(faz)})"); time.sleep(.4)
    for k, v in (('talv', tal), ('datav', data), ('profv', '0–30'), ('z', z), ('metv', 'Curva de retenção (laboratório)'), ('un', '% volume'), ('ccv', cc), ('pmpv', pmp), ('fontev', 'Agrolab')):
        J(f"SETV({json.dumps(k)},{json.dumps(v)})"); time.sleep(.08)
    live = J("FV('cadT')"); J("BTN('Salvar')"); time.sleep(.8); return live

try:
    c.aparelho(1440, 1000)
    c.goto(U('Main.dc.html'), .3); J("localStorage.clear()")
    # ---------- W1 · lugar ----------
    ir('AG-02.dc.html')
    ag = J("(()=>({sec:TIT('Água no solo'), grade:!!document.querySelector('[data-g2g=g_agua]'), link:[...document.querySelectorAll('main a')].filter(a=>/Água no solo/.test(a.innerText)).map(a=>[N(a.innerText),a.getAttribute('href')])}))()")
    ir('IR-01.dc.html', 'Todas')
    rows = J("ROWS('Água no solo')") or []
    ids = sorted(r[0] for r in rows)
    chk('W1 IR-01 tem o bloco Água no solo com AGS-001..004; o AG-02 não tem a grade e leva à Irrigação (IR-01.dc.html#agua)',
        ids == ['AGS-001', 'AGS-002', 'AGS-003', 'AGS-004'] and ag and not ag['sec'] and not ag['grade'] and ag['link'] and ag['link'][0][1] == 'IR-01.dc.html#agua', [ids, ag])
    c.goto(U('IR-01.dc.html#agua'), 1.2); J(LIB); time.sleep(.6)
    pos = J("(()=>{const e=document.getElementById('ir-agua'); if(!e) return null; const r=e.getBoundingClientRect(); return [Math.round(r.top), innerHeight];})()")
    chk('W1b IR-01.dc.html#agua rola até o bloco Água no solo (topo do bloco à vista)', pos and 0 <= pos[0] < pos[1] - 120, pos)
    # ---------- W2 · No balanço ----------
    r = dict(rows)
    chk('W2 No balanço: AGS-003 em uso no Pivô 2 (AFD 24,8 mm · gatilho 8,0 mm); AGS-004 do Pivô 12 sem PMP: vale o limiar',
        'Em uso · Pivô 2' in r.get('AGS-003', '') and 'AFD 24,8 mm' in r.get('AGS-003', '') and 'gatilho 8,0 mm' in r.get('AGS-003', '')
        and 'Pivô 12' in r.get('AGS-004', '') and 'CAD não calculável: vale o limiar' in r.get('AGS-004', ''), [r.get('AGS-003'), r.get('AGS-004')])
    # ---------- W3 · painel do setor ----------
    ir('IR-01.dc.html', 'Santa Rita'); setor('P2'); a3 = J("FV('aguaT')") or ''; f3 = J("FV('fdep')")
    chk('W3 setor P2: CAD 45 mm · AFD 24,8 mm (f 0,55 · FAO-56, Tabela 22 (milho grão)) · déficit 11,2 mm = 25 % da CAD · gatilho 8,0 mm (limiar do setor) · AGS-003',
        a3.startswith('CAD 45 mm · AFD 24,8 mm (f 0,55 · FAO-56, Tabela 22 (milho grão))') and 'déficit 11,2 mm = 25 % da CAD' in a3 and 'gatilho 8,0 mm (limiar do setor)' in a3 and 'AGS-003' in a3 and str(f3) in ('0.55', '0,55'), [a3, f3])
    fecha()
    # ---------- W4 · gatilho pela AFD ----------
    ir('IR-01.dc.html', 'Lagoa Grande'); s0 = linha('PV19')
    live = medir('Lagoa Grande', 'Pivô 19', '21', '20')
    t4 = J("TOAST()") or ''; ir('IR-01.dc.html', 'Lagoa Grande'); s1 = linha('PV19'); setor('PV19'); a4 = J("FV('aguaT')") or ''; fecha()
    # a linha da Lagoa Grande mostra o próximo passo: "—" sem necessidade; com o gatilho pela AFD, a irrigação entra na fila (ordem proposta)
    chk('W4 Pivô 19 com CAD 3 mm (AGS-005, número novo): AFD 1,5 mm (f 0,50 a confirmar) vira o gatilho e o setor ganha próximo passo de irrigação',
        s0.endswith('— —') and 'irrigação' in s1 and 'AGS-005 registrada' in t4 and '= 3 mm' in (live or '') and 'CAD 3 mm · AFD 1,5 mm (f 0,50 · padrão sem referência para mamão' in a4
        and 'gatilho 1,5 mm (AFD do solo, menor que o limiar' in a4 and 'Déficit, gatilho e lâmina do setor já usam esta medição.' in t4, [s0, s1, live, a4, t4])
    # ---------- W5 · teto do déficit na CAD ----------
    ir('IR-01.dc.html', 'Santa Rita'); setor('P1'); d0 = J("FV('defT')") or ''; n0 = J("FV('necT')") or ''; fecha()
    medir('Santa Rita', 'P1', '20', '18')
    ir('IR-01.dc.html', 'Santa Rita'); setor('P1'); d1 = J("FV('defT')") or ''; n1 = J("FV('necT')") or ''; a5 = J("FV('aguaT')") or ''; fecha()
    # oráculo independente (balanço diário FAO-56 com 0 ≤ Dr ≤ CAD), da semente do P1: d0, ETc dos 7 dias, chuva efetiva em 20/09 (dia −3) e as voltas
    import dados_irrigacao as DI
    b = DI.seed()['setores']['P1']; ha = b['ha']; b = b['bal']; et = b['etc'] / b['dias']; D = min(6.0, max(0.0, b['d0']))
    for k in range(-b['dias'], 0):
        v = D + et - (b['pef'] if k == -3 else 0) - sum(a['vol'] / (10 * ha) * a['ef'] / 100 for a in b['ap'] if max(-b['dias'], a['q'] // 1440) == k)
        D = min(6.0, max(0.0, v))
    esp = ('%.1f' % D).replace('.', ',')
    chk(f'W5 P1 com CAD 6 mm: déficit 8,4 → {esp} mm (balanço diário com teto da CAD, oráculo independente), líquida {esp} mm e a % da CAD no painel',
        d0.lstrip('≈').startswith('8,4 mm') and d1.lstrip('≈').startswith(esp + ' mm') and f'líquida {esp} mm' in n1 and f'déficit {esp} mm = ' in a5 and '% da CAD' in a5, [esp, d0, n0, d1, n1, a5])
    # ---------- W6 · recusa ----------
    J("ADD('Água no solo')"); espera("!!document.querySelector('aside[role=dialog]')", 4); time.sleep(.3)
    J("SETV('faz','Santa Rita')"); time.sleep(.4)
    for k, v in (('talv', 'T7'), ('datav', '2026-09-21'), ('profv', '0–30'), ('z', '30'), ('metv', 'Curva de retenção (laboratório)'), ('un', '% volume'), ('ccv', '20'), ('pmpv', '25'), ('fontev', 'Agrolab')):
        J(f"SETV({json.dumps(k)},{json.dumps(v)})"); time.sleep(.08)
    J("BTN('Salvar')"); time.sleep(.6); al = J("ALERT()") or ''; aberto = J("!!document.querySelector('aside[role=dialog]')")
    n6 = len(J("ROWS('Água no solo')") or []); fecha()
    chk('W6 PMP ≥ CC é recusado junto ao campo e nada é gravado', 'Ponto de murcha deve ser menor que a capacidade de campo' in al and aberto and n6 == 4, [al, aberto, n6])
    # ---------- W7 · fração f do setor ----------
    setor('P2'); J("SETV('fdep','0.1')"); J("BTN('Salvar')"); time.sleep(.8)
    setor('P2'); a7 = J("FV('aguaT')") or ''; J("SETV('fdep','')"); J("BTN('Salvar')"); time.sleep(.8)
    setor('P2'); a7b = J("FV('aguaT')") or ''; fecha()
    chk('W7 f 0,10 no P2: AFD 4,5 mm vira o gatilho; vazio volta a 0,55 da FAO-56',
        'AFD 4,5 mm (f 0,10 · definido no setor)' in a7 and 'gatilho 4,5 mm (AFD do solo' in a7 and 'AFD 24,8 mm (f 0,55 · FAO-56' in a7b and 'gatilho 8,0 mm (limiar do setor)' in a7b, [a7, a7b])
    # ---------- W8 · F5 e atalho do setor ----------
    ir('IR-01.dc.html', 'Santa Rita'); setor('P1'); d8 = J("FV('defT')") or ''
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>N(b.innerText)==='Registrar medição de água no solo'); b&&b.click();})()"); time.sleep(.6)
    pre = [J("FV('faz')"), J("FV('talv')"), J("(document.querySelector('aside[role=dialog] h2')||{}).innerText||''")]; fecha()
    chk(f'W8 F5: o déficit do P1 segue {esp} mm; "Registrar medição de água no solo" abre o formulário com Santa Rita e P1',
        d8.lstrip('≈').startswith(esp + ' mm') and pre[0] == 'Santa Rita' and pre[1] == 'P1' and 'Registrar medição de água no solo' in pre[2], [d8, pre])
    e1 = J("window.__e") or []
    # ---------- W9 · celular ----------
    c.aparelho(390, 844, toque=True); ir('IR-01.dc.html')
    sw = J("[document.documentElement.scrollWidth, innerWidth]"); e2 = J("window.__e") or []
    chk('W9 390 px sem rolagem horizontal; nenhum erro de JavaScript', sw and sw[0] <= sw[1] + 1 and not e1 and not e2, [sw, e1, e2])
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {OK}/{OK + FAIL} ok')
sys.exit(1 if FAIL else 0)
