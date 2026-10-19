# -*- coding: utf-8 -*-
"""COLH-APONT F1 · apontar a colheita na web (docs/gestao/GESTAO-1810.md §2 e §6, aceite C1–C3; pedido do proprietário de 18/10/2026:
"nao encontrei no sistema onde faz apontamento da colheita").
  U   regras no node (colh_apont_unit.js): comando web pelo cenApontar, mesma chave, recusas, R-02, duplicidade com o app, fonte única prTal
  C1  Colheita › Pivô 19 (OS-0505 em execução): uma primária verde, "Apontar colheita"; o painel abre com a data de hoje e a área vazia;
      20 ha e um clique em "Apontar" → 26/09 provisório na lista, com quem registrou; saldo 25,11 → 5,11 ha; passe 36,42 t ÷ 70 ha = 0,52 t/ha;
      o app (MB-10) mostra o mesmo: "Feito 70 de 75,11 ha · saldo 5,11 ha"
  C2  duplo clique em "Apontar" grava uma vez (mesma chave); clicar de novo com a área já limpa não grava
  C3  T1-A Soja (sem O.S. de colheita): sem a primária "Apontar colheita" e sem formulário; o motivo e "Programar colheita ›" para a O.S. nova
  L   O.S. só Liberada: "Apontar colheita" abre o painel com o próximo passo "Iniciar a OS-0505" (leva à O.S.), sem formulário mudo
  R   "Registrar carga ›" abre o Recebimento com a pesagem nova da OS-0505 e o dia 26/09 preenchidos
  M   390 × 844: painel do apontamento sem rolagem lateral e "Apontar" alcançável
  E   sem erro de JS em nenhuma etapa
Oráculos da semente sintética (dados_lagoa_safra: OS-0505 com 75,11 ha, 50 ha feitos; dados_producao: passe S39 com 36.420 kg; HOJE 26/09).
Uso: env CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B colh_apont_test.py (lê _render ou RENDER_DIR; COLH_SHOTS=<pasta> grava fotos).
Contraprova: RENDER_DIR=<render da base bf84dcf8> reprova (sem a primária de apontar)."""
import os, sys, json, time, subprocess
os.environ.setdefault('SAFRION_DADOS', 'sintetico')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CDP_GL', '1')
import dados_producao as DP

OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)

# ---------- U · regras no node (o mesmo prefixo do producao_unit_test.py), sem arquivo intermediário ----------
def unidade():
    import producao_unit_test as PU
    src = PU.fonte().replace(open(os.path.join(HERE, 'producao_unit.js'), encoding='utf-8').read(), open(os.path.join(HERE, 'colh_apont_unit.js'), encoding='utf-8').read())
    r = subprocess.run(['node', '-'], input=src, capture_output=True, text=True, timeout=180); out = r.stdout.strip().splitlines()
    chk('U motor JS (node) executou sem erro', r.returncode == 0 and out, r.stderr[-800:])
    for x in (json.loads(out[-1]) if out else []): chk(x['n'], x['ok'], x['info'])
unidade()

from comp_lib import Chrome, servir
R = os.environ.get('RENDER_DIR') or os.path.join(HERE, '_render')
FOTOS = os.environ.get('COLH_SHOTS', '')
HJ = DP.HOJE[8:10] + '/' + DP.HOJE[5:7]   # 26/09 (CEN_DIA_OP)
p, srv = servir(R); c = Chrome(); J = c.js
U = lambda pg: f'http://127.0.0.1:{p}/{pg}'
LIB = r"""window.N=s=>(s||'').replace(/\s+/g,' ').trim();
window.VIS=e=>{ if(!e) return false; const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>1&&r.height>1&&cs.visibility!=='hidden'&&cs.display!=='none'; };
window.PRIM=()=>[...document.querySelectorAll('header button, header a')].filter(e=>VIS(e)&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)').map(e=>N(e.innerText));
window.PAN=()=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); return a?N(a.innerText):''; };
window.BTN=(t)=>{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(VIS); return a?[...a.querySelectorAll('button,a')].filter(VIS).find(b=>N(b.innerText)===t)||null:null; };
window.SETV=(sel,val)=>{ const i=document.querySelector(sel); if(!i) return 'sem '+sel; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,val);
  i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return 'ok'; };
window.OS5=()=>{ const o=window.__car.cenGet().ordens['OS-0505']; return {saldo:o.saldo,real:o.realizado,etapa:o.etapa,ap:(o.ap||[]).filter(a=>a.st!=='Previsto').map(a=>[a.d,a.ha,a.st,a.origem,a.chave])}; };
'ok'"""
def espera(e, s=20.0):
    f = time.time() + s
    while time.time() < f:
        try:
            if J(e): return True
        except Exception: pass
        time.sleep(.15)
    return False
def abre(pg, cond="document.querySelector('main') && document.querySelector('main').innerText.trim().length>50"):
    c.goto(U(pg), .4); espera(f"document.readyState==='complete' && ({cond})"); J(LIB)
def limpa(): c.goto(U('Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear(); 1")
def clica(expr, n=1):
    """clique real (mouse do CDP) no centro do elemento; n=2 é o duplo clique (detail 1 e 2), como a pessoa faz"""
    xy = json.loads(J(f"JSON.stringify((()=>{{const e={expr}; if(!e) return null; e.scrollIntoView({{block:'center'}}); const q=e.getBoundingClientRect(); return [q.left+q.width/2,q.top+q.height/2];}})())") or 'null')
    if not xy: return False
    for i in range(1, n + 1):
        c.call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': xy[0], 'y': xy[1], 'button': 'left', 'clickCount': i})
        c.call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': xy[0], 'y': xy[1], 'button': 'left', 'clickCount': i})
    return True
def foto(nome):
    if FOTOS: os.makedirs(FOTOS, exist_ok=True); c.shot(os.path.join(FOTOS, nome + '.png'))
def os5(): return json.loads(J("JSON.stringify(OS5())") or '{}')
ERR = []
def erros(tag): e = J("window.__err||''") or ''; ERR.append(f'{tag}: {e}') if e else None

try:
    c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__err='';addEventListener('error',e=>{window.__err+=(e.message||'erro')+' | ';});"})
    c.aparelho(1440, 900, 1, False)
    # ---------- C1 ----------
    limpa(); abre('COLH.dc.html'); pr0 = J("PRIM()") or []; s0 = os5()
    chk('C1 sem seleção, uma primária verde no cabeçalho: "Apontar colheita do Pivô 19" (OS-0505 em execução)', pr0 == ['Apontar colheita do Pivô 19'], pr0)
    clica("[...document.querySelectorAll('header button')].find(b=>N(b.innerText)==='Apontar colheita do Pivô 19')"); espera("!!BTN('Apontar')", 8)
    pan = J("PAN()") or ''; d0 = J("(document.querySelector('#pf_d')||{}).value"); h0 = J("(document.querySelector('#pf_ha')||{}).value")
    chk(f'C1 o painel do Pivô 19 abre no apontamento: data já com hoje ({HJ}), área vazia (nunca o último valor), saldo à vista 25,11 ha, "Apontar"',
        d0 == HJ and h0 == '' and 'Saldo a colher: 25,11 ha' in pan and 'APONTAR COLHEITA · OS-0505' in pan.upper() and bool(J("!!BTN('Apontar')")), [d0, h0, pan[:600]])
    chk('C1 o passo da previsão fica como secundária do painel ("Publicar previsão"), sem segunda primária verde',
        bool(J("!!BTN('Publicar previsão')")) and J("[...document.querySelectorAll('aside[role=dialog] button, aside[role=dialog] a')].filter(e=>VIS(e)&&getComputedStyle(e).backgroundColor==='rgb(30, 122, 76)').length") == 1, pan[-300:])
    J("SETV('#pf_ha','20')"); foto('colh_1440_painel')
    clica("BTN('Apontar')"); espera("OS5().ap.length===%d" % (len(s0.get('ap', [])) + 1), 8); time.sleep(.3); J(LIB)
    s1 = os5(); novo = [a for a in s1.get('ap', []) if a not in s0.get('ap', [])]; pan = J("PAN()") or ''
    chk('C1 um apontamento novo: 26/09, 20 ha, Provisório, origem web, chave do formulário (W-COLH-…); saldo 25,11 → 5,11 ha; realizado 70 ha',
        len(novo) == 1 and novo[0][:4] == [HJ, 20, 'Provisório', 'web'] and str(novo[0][4]).startswith('W-COLH-') and abs(s1['saldo'] - 5.11) < 1e-9 and s1['real'] == 70, [novo, s1.get('saldo'), s1.get('real')])
    lin = J("(()=>{ const s=[...document.querySelectorAll('aside[role=dialog] section')].find(x=>/Apontamentos da colheita/i.test(x.getAttribute('aria-label')||'')); return s?N(s.innerText):''; })()") or ''
    chk('C1 a lista de apontamentos mostra 26/09 no topo, provisório, pela web com quem registrou', '26/09 OS-0505 · dia 3 20 ha Provisório pela web ·' in lin and lin.index('26/09') < lin.index('22/09'), lin[:400])
    chk('C1 na hora: saldo 5,11 ha no formulário, área limpa para o próximo, passe S39 com 70 ha e 0,52 t/ha (36,42 t ÷ 70 ha, R-02)',
        'Saldo a colher: 5,11 ha' in pan and J("(document.querySelector('#pf_ha')||{}).value") == '' and 'OS-0505 S39 Em execução 70 ha 36,42 t 0,52 t/ha parcial' in pan, pan[:1500])
    foto('colh_1440_lista'); erros('C1 COLH')
    abre('MB-10.dc.html', "document.body.innerText.indexOf('OS-0505')>=0"); mb = J("N(document.body.innerText)") or ''
    chk('C1 o app (MB-10 › Colheita) vê o mesmo: OS-0505 "Feito 70 de 75,11 ha · saldo 5,11 ha"; a ação do app tem o mesmo nome ("Apontar colheita · OS-0505")',
        'Feito 70 de 75,11 ha · saldo 5,11 ha' in mb and 'Apontar colheita · OS-0505' in mb and 'Apontar área' not in mb, mb[:600])
    erros('C1 MB-10')
    # ---------- C2 ----------
    limpa(); abre('COLH.dc.html#lg19', "!!document.querySelector('#pf_ha')"); J(LIB); n0 = len(os5().get('ap', []))
    J("SETV('#pf_ha','10')"); clica("BTN('Apontar')", n=2); time.sleep(.8); J(LIB); n1 = len(os5().get('ap', []))
    clica("BTN('Apontar')"); time.sleep(.6); J(LIB); n2 = len(os5().get('ap', [])); al = J("N([...document.querySelectorAll('aside[role=dialog] [role=alert]')].filter(VIS).map(x=>x.innerText).join(' | '))") or ''
    chk('C2 duplo clique em "Apontar" grava uma vez (mesma chave); outro clique com a área já limpa não grava e diz o campo', n1 == n0 + 1 and n2 == n1 and 'Informe a área colhida' in al, [n0, n1, n2, al])
    erros('C2')
    # ---------- C3 ----------
    limpa(); abre('COLH.dc.html#c1', "!!document.querySelector('aside[role=dialog]')"); J(LIB); time.sleep(.3)
    pan = J("PAN()") or ''; pr3 = J("PRIM()") or []
    lk = J("(()=>{ const a=[...document.querySelectorAll('aside[role=dialog] a')].find(x=>N(x.innerText)==='Programar colheita ›'); return a?a.getAttribute('href'):''; })()") or ''
    foto('colh_1440_c3')
    chk('C3 T1-A Soja sem O.S. de colheita: sem a primária "Apontar colheita" e sem formulário de apontar; o motivo e "Programar colheita ›" para a O.S. nova do cultivo',
        not any('Apontar' in x for x in pr3) and not J("!!document.querySelector('#pf_ha')") and not J("!!BTN('Apontar')") and 'Sem O.S. de colheita liberada ou em execução neste talhão' in pan
        and lk == 'OS.dc.html#nova:c1:a8:2027-02-12', [pr3, lk, pan[:500]])
    erros('C3')
    # ---------- L · O.S. só liberada ----------
    limpa(); abre('COLH.dc.html'); J("window.__car.cenMudar(null,c=>{ c.ordens['OS-0505'].etapa='Liberadas'; return {msg:''}; })"); abre('COLH.dc.html')
    prl = J("PRIM()") or []; clica("[...document.querySelectorAll('header button')].find(b=>N(b.innerText)==='Apontar colheita do Pivô 19')"); espera("!!document.querySelector('aside[role=dialog]')", 8); J(LIB)
    pan = J("PAN()") or ''; ini = J("(()=>{ const b=BTN('Iniciar a OS-0505'); return b?[b.tagName,b.getAttribute('href'),getComputedStyle(b).backgroundColor]:null; })()")
    foto('colh_1440_liberada')
    chk('L O.S. só Liberada: a primária "Apontar colheita" abre o painel com o próximo passo "Iniciar a OS-0505" (verde, leva à O.S.) e sem formulário de apontar',
        prl == ['Apontar colheita do Pivô 19'] and ini == ['A', 'OS.dc.html#OS-0505', 'rgb(30, 122, 76)'] and 'inicie a execução para apontar' in pan and not J("!!document.querySelector('#pf_ha')"), [prl, ini, pan[:400]])
    erros('L')
    # ---------- R · Registrar carga ----------
    limpa(); abre('COLH.dc.html#lg19', "!!document.querySelector('#pf_ha')"); J(LIB)
    rc = J("(()=>{ const a=[...document.querySelectorAll('aside[role=dialog] a')].find(x=>N(x.innerText)==='Registrar carga ›'); return a?a.getAttribute('href'):''; })()") or ''
    cg = ''
    if rc:
        clica("[...document.querySelectorAll('aside[role=dialog] a')].find(x=>N(x.innerText)==='Registrar carga ›')")
        espera("location.pathname.endsWith('/CARGA.dc.html') && !!document.querySelector('#pf_dcol')", 15); J(LIB)
        cg = json.loads(J("JSON.stringify({dcol:(document.querySelector('#pf_dcol')||{}).value, os:[...document.querySelectorAll('aside[role=dialog] [aria-pressed=true]')].map(b=>N(b.innerText)), t:PAN().slice(0,80), h:location.hash})") or '{}')
    chk(f'R "Registrar carga ›" leva ao Recebimento com a pesagem nova da OS-0505 e o dia {HJ} preenchidos (corrigíveis); o endereço é consumido',
        rc == 'CARGA.dc.html#nova:OS-0505:' + DP.HOJE and cg.get('dcol') == HJ and any(x.startswith('OS-0505') for x in cg.get('os', [])) and cg.get('t', '').startswith('Registrar pesagem') and cg.get('h') == '', [rc, cg])
    erros('R')
    # ---------- M · 390 px ----------
    c.aparelho(390, 844, 2, True); limpa(); abre('COLH.dc.html#lg19', "!!document.querySelector('#pf_ha')"); J(LIB); time.sleep(.3)
    m = json.loads(J("JSON.stringify((()=>{ const b=BTN('Apontar'); const q=b?b.getBoundingClientRect():null; const t=q?document.elementFromPoint(q.left+q.width/2,q.top+q.height/2):null;"
                     " return {lado:document.documentElement.scrollWidth>innerWidth+1, ok:!!t&&(t===b||b.contains(t)), dentro:!!q&&q.right<=innerWidth+1&&q.left>=-1}; })())") or '{}')
    foto('colh_390_painel')
    n0 = len(os5().get('ap', [])); J("SETV('#pf_ha','5')"); J("(BTN('Apontar')||{click(){}}).click()"); espera("OS5().ap.length===%d" % (n0 + 1), 8); J(LIB); n1 = len(os5().get('ap', []))
    J("(()=>{ const s=[...document.querySelectorAll('aside[role=dialog] section')].find(x=>/Apontamentos da colheita/i.test(x.getAttribute('aria-label')||'')); if(s) s.scrollIntoView({block:'start'}); })()"); time.sleep(.3); foto('colh_390_lista')
    lin = J("(()=>{ const s=[...document.querySelectorAll('aside[role=dialog] section')].find(x=>/Apontamentos da colheita/i.test(x.getAttribute('aria-label')||'')); return s?N(s.innerText):''; })()") or ''
    chk('M 390 px: apontar 5 ha pelo toque grava uma vez e a lista mostra 26/09 provisório no topo', n1 == n0 + 1 and lin.find('26/09') >= 0 and lin.find('26/09') < lin.find('22/09'), [n0, n1, lin[:200]])
    chk('M 390 × 844: painel do apontamento sem rolagem lateral; "Apontar" visível e alcançável dentro da tela', m.get('lado') is False and m.get('ok') and m.get('dentro'), m)
    erros('M')
    chk('E sem erro de JS (COLH, MB-10, CARGA, 1440 e 390 px)', not ERR, ERR)
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
