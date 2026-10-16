# -*- coding: utf-8 -*-
"""Revisão do Claude do PR #90, rodada 2 (HEAD b35cd0c; CRE-BANCO F1, Codex): GE-08#vis=ficha "Bens e avaliações" no navegador real (Chrome headless, CDP).
Não versionado; dados sintéticos; armazenamento limpo no início de cada largura. Cada passo roda mesmo se o anterior falhar.
Uso (de gen37/): CHROME_BIN=… CDP_GL=1 SAFRION_DADOS=sintetico python3 -B <este arquivo>   · REV_RENDER=<_render> · REV_LARG=1440,390
REV_MODO=base: só os passos de regressão que existem na base (Documentos, status, dossiê do contrato, primária)."""
import os, sys, json, time, re, urllib.request, base64
G = os.environ.get('REV_GEN') or '/tmp/claude-0/pr90b/tools/prototipo/v37/gen37'; sys.path.insert(0, G)
from comp_lib import Chrome, servir
from cdp import WS
from cadc_lib import ERRS
EV = os.path.dirname(os.path.abspath(__file__))
R = os.environ.get('REV_RENDER') or os.path.join(G, '_render')
MODO = os.environ.get('REV_MODO', 'pr')
LARGS = [int(x) for x in os.environ.get('REV_LARG', '1440,390').split(',')]
CEN_LS = 'safrion-credito-ficha-demo-grupo-v1'   # chave da ficha (nova no PR)
DOC_LS = 'safrion-credito-docs-v1'               # chave dos documentos CAD-02 (não pode mudar)
OK, FAIL = [], []
def chk(n, c, info=''):
    (OK if c else FAIL).append(n); print(('OK    ' if c else 'FALHA ') + n + ('' if c else ' · ' + str(info)[:900]), flush=True)
def info(n, v): print('INFO  ' + n + ' · ' + str(v)[:900], flush=True)
src = open(os.path.join(G, 'tab_drill_cab_test.py'), encoding='utf-8').read()
ns = {}; exec(re.search(r'SETA = r""".*?"""', src, re.S).group(0), ns); exec(re.search(r'CAB = r""".*?"""', src, re.S).group(0), ns)
SETA, CAB = ns['SETA'], ns['CAB']

class Aba:
    """segunda aba real no mesmo Chrome (mesma origem, mesmo localStorage)"""
    def __init__(self, port):
        t = json.load(urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}/json/new?about:blank', method='PUT'), timeout=30))
        self.alvo = t['id']; self.port = port; self.ws = WS(t['webSocketDebuggerUrl']); self.i = 0
        self.call('Page.enable'); self.call('Runtime.enable'); self.call('Page.addScriptToEvaluateOnNewDocument', {'source': ERRS})
    def call(self, m, p=None, timeout=60):
        self.i += 1; mid = self.i; self.ws.send(json.dumps({'id': mid, 'method': m, 'params': p or {}})); fim = time.monotonic() + timeout
        while True:
            x = json.loads(self.ws.recv(timeout=max(.1, fim - time.monotonic())))
            if x.get('id') == mid:
                if 'error' in x: raise RuntimeError(f"{m}: {x['error']}")
                return x.get('result', {})
    def js(self, e):
        r = self.call('Runtime.evaluate', {'expression': e, 'awaitPromise': True, 'returnByValue': True})
        if 'exceptionDetails' in r: raise RuntimeError(str(r['exceptionDetails'].get('exception', {}).get('description') or r['exceptionDetails'].get('text'))[:400])
        return r['result'].get('value')
    def close(self):
        try: urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json/close/{self.alvo}', timeout=10)
        except Exception: pass

p, srv = servir(R); c = Chrome(); J = c.js; U = lambda x: f'http://127.0.0.1:{p}/{x}'
SEC = "([...document.querySelectorAll('main section')].find(x=>x.getClientRects().length&&x.querySelector('h3')&&x.querySelector('h3').innerText.trim()==='Ficha do grupo · Bens e avaliações'))"
DLG = "([...document.querySelectorAll('aside[role=dialog]')].find(d=>d.getClientRects().length))"
VIS = "(e=>!!e&&e.getClientRects().length>0&&getComputedStyle(e).visibility!=='hidden')"
def espera(cond, lim=8.0, a=None):
    f = (a or c).js if a else J; t0 = time.time()
    while time.time() - t0 < lim:
        try:
            if f("(()=>{try{return !!(%s)}catch(e){return false}})()" % cond): return True
        except Exception: pass
        time.sleep(.12)
    return False
def recarrega(url='GE-08.dc.html#vis=ficha', jj=None):
    (jj or c).call('Page.navigate', {'url': 'about:blank'}); time.sleep(.2)
    (jj or c).call('Page.navigate', {'url': U(url)})
    espera("document.readyState==='complete'&&document.body&&document.body.innerText.length>50", 15, jj); time.sleep(.5)
def ls(k=CEN_LS, jj=None): return (jj.js if jj else J)("localStorage.getItem(%s)" % json.dumps(k))
def db(jj=None):
    s = ls(CEN_LS, jj)
    try: return json.loads(s) if s else None
    except Exception: return s
def linhas(jj=None):
    return (jj.js if jj else J)("(()=>{const s=%s; if(!s) return null; return [...s.querySelectorAll('[data-g2g=g_ficha] [role=row]')].filter(r=>r.getClientRects().length&&r.querySelector('[role=cell]')).map(r=>[...r.querySelectorAll('[role=cell]')].map(c=>c.innerText.replace(/\\s+/g,' ').trim()))})()" % SEC)
def cartoes():
    return J("(()=>{const s=%s; if(!s) return null; const k=s.querySelector('.g2cartoes'); return k&&k.getClientRects().length?[...k.querySelectorAll('[role=listitem]')].filter(x=>x.getClientRects().length).map(x=>x.innerText.replace(/\\s+/g,' ').trim()):null})()" % SEC)
def modo(m):
    J("(()=>{const b=document.querySelector('[data-g2md=g_ficha] [data-modo=%s]'); if(b&&b.getAttribute('aria-pressed')!=='true') b.click();})()" % m); time.sleep(.4)
def fill(fid, v, jj=None):
    return (jj.js if jj else J)("((id,v)=>{const i=document.getElementById(id); if(!i) return null; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype); Object.getOwnPropertyDescriptor(P,'value').set.call(i,v); i.dispatchEvent(new Event('input',{bubbles:true})); i.dispatchEvent(new Event('change',{bubbles:true})); return i.value;})(%s,%s)" % (json.dumps(fid), json.dumps(v)))
def campo(fid, jj=None): return (jj.js if jj else J)("(()=>{const i=document.getElementById(%s); return i?i.value:null})()" % json.dumps(fid))
def btn_dlg(rot, jj=None): return (jj.js if jj else J)("(()=>{const d=%s; if(!d) return 'sem painel'; const b=[...d.querySelectorAll('button')].find(b=>%s(b)&&b.innerText.trim()===%s); if(!b) return 'sem botão'; b.click(); return 'ok';})()" % (DLG, VIS, json.dumps(rot)))
def prim_dlg(jj=None): return (jj.js if jj else J)("(()=>{const d=%s; if(!d) return 'sem painel'; const b=[...d.querySelectorAll('button')].find(b=>%s(b)&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'); if(!b) return 'sem primária'; b.click(); return b.innerText.trim();})()" % (DLG, VIS))
def rot_prim(jj=None): return (jj.js if jj else J)("(()=>{const d=%s; if(!d) return null; const b=[...d.querySelectorAll('button')].find(b=>%s(b)&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'); return b?b.innerText.trim():null;})()" % (DLG, VIS))
def dlg_txt(jj=None): return (jj.js if jj else J)("(()=>{const d=%s; return d?d.innerText.replace(/\\s+/g,' ').trim():null})()" % DLG)
def dlg_aberto(jj=None): return bool((jj.js if jj else J)("!!%s" % DLG))
def toast(jj=None): return (jj.js if jj else J)("(()=>{const t=[...document.querySelectorAll('[role=status],[aria-live]')].filter(e=>e.getClientRects().length).map(e=>e.innerText.trim()).filter(Boolean); return t.join(' | ')})()") or ''
def incluir(jj=None):
    return (jj.js if jj else J)("(()=>{const b=[...document.querySelectorAll('header button,main button')].find(b=>b.getClientRects().length&&b.innerText.trim()==='Incluir bem'); if(!b) return 'sem'; if(b.disabled) return 'desabilitado'; b.click(); return 'ok';})()")
def abrir(nome, jj=None):
    r = (jj.js if jj else J)("(()=>{const s=%s; const r=[...s.querySelectorAll('[data-g2g=g_ficha] [role=row][data-rid], .g2cartoes [role=listitem][data-rid]')].find(r=>r.getClientRects().length&&r.innerText.indexOf(%s)>=0); if(!r) return 'sem linha'; r.click(); return 'ok';})()" % (SEC, json.dumps(nome)))
    espera("!!%s" % DLG, 4, jj); time.sleep(.25); return r
def novo(d, jj=None, salvar=True):
    r = incluir(jj); espera("!!%s" % DLG, 4, jj); time.sleep(.2)
    for k in ('nome', 'tipo', 'valor', 'data', 'responsavel', 'fonte'):
        if k in d: fill('fx_g_ficha_' + k, d[k], jj)
    time.sleep(.15)
    if salvar: r = (r, prim_dlg(jj)); time.sleep(.5)
    return r
def verdes(escopo='fora'):
    return J("(()=>{const v=%s; const g=e=>{const cs=getComputedStyle(e); return cs.backgroundColor==='rgb(30, 122, 76)'&&parseFloat(cs.borderTopLeftRadius)<30&&!e.closest('.menu-lat,[role=tablist],[role=group],[role=listbox]');}; return [...document.querySelectorAll('header button,header a,main button,main a,aside button')].filter(e=>v(e)&&g(e)&&(%s)).map(e=>e.innerText.trim().slice(0,40))})()" % (VIS, "!e.closest('aside[role=dialog]')" if escopo == 'fora' else "!!e.closest('aside[role=dialog]')"))
def shot(n):
    try: c.shot(os.path.join(EV, n + '.png'))
    except Exception as e: info('captura ' + n, e)
def passo(rot, f):
    try: f()
    except Exception as e: chk(rot + ' (exceção)', False, repr(e)[:400])

D1 = {'nome': 'Trator sintético A', 'tipo': 'Avaliação de mercado', 'valor': '850000,50', 'data': '2026-03-10', 'responsavel': 'Ana', 'fonte': 'Laudo sintético 01'}
D2 = {'nome': 'Imóvel sintético B', 'tipo': 'Valor contábil', 'valor': '12.500.000,00', 'data': '2026-01-15', 'responsavel': 'Carlos', 'fonte': 'Balanço sintético 2025'}
D3 = {'nome': 'Silo sintético C', 'tipo': 'Declaração do produtor', 'valor': '0', 'data': '2026-10-01', 'responsavel': 'Ana', 'fonte': 'Declaração sintética'}
D4 = {'nome': 'Galpão sintético D', 'tipo': 'Declaração do produtor', 'valor': ''}
def item(nome, jj=None):
    x = db(jj); return next((i for i in (x or {}).get('items', []) if i.get('nome') == nome), None) if isinstance(x, dict) else None

def regressao(w):
    # passos que também existem na base (contraprova)
    recarrega('GE-08.dc.html#vis=documentos')
    doc = J("(()=>{const s=[...document.querySelectorAll('main section')].find(x=>x.getClientRects().length&&/Documentos para crédito/.test((x.querySelector('h3')||{}).innerText||'')); if(!s) return null; const cab=s.querySelector('h3').closest('div').parentElement; const vis=%s; const vb=[...cab.querySelectorAll('a,button')].filter(e=>vis(e)&&!e.closest('[role=menu]')).map(e=>(e.innerText||e.getAttribute('aria-label')||'').trim()); const mn=[...cab.querySelectorAll('[role=menu] [role=menuitem]')].map(e=>e.innerText.trim()); return {vis:vb, menu:mn};})()" % VIS)
    info(f'R{w} cabeçalho do bloco Documentos (à vista | no ⋯)', doc)
    chk(f'R1 {w} Documentos: "Incluir documento" continua à vista no bloco (como na base)', bool(doc) and 'Incluir documento' in doc['vis'], doc)
    st = J("(()=>{const h=document.querySelector('header'); return h?h.innerText.replace(/\\s+/g,' '):''})()")
    chk(f'R2 {w} cabeçalho da GE-08 mantém o estado "CRE-0102 · condição documental pendente" (estado sempre visível)', 'condição documental pendente' in (st or ''), st)
    for vis in ('contratos', 'documentos', 'dossie', 'liberacoes'):
        recarrega('GE-08.dc.html#vis=' + vis); g = verdes()
        info(f'R3 {w} verdes fora de painel em #vis={vis}', g)
    recarrega('GE-08.dc.html#vis=contratos')
    J("(()=>{const r=[...document.querySelectorAll('[data-g2g=g_cre] [role=row]')].find(r=>r.getClientRects().length&&/CRE-0102/.test(r.innerText)&&!r.querySelector('[role=columnheader]')); const a=r&&(r.querySelector('.g2drill,.g2car')||r.querySelector('[role=cell]')); if(a) a.click();})()")
    espera("!!%s" % DLG, 4); time.sleep(.3)
    lk = J("(()=>{const d=%s; return d?[...d.querySelectorAll('a')].map(a=>[a.innerText.trim(),a.getAttribute('href')]):null})()" % DLG)
    info(f'R4 {w} links do detalhe do CRE-0102', lk)
    dos = [x for x in (lk or []) if 'Dossiê' in x[0]]
    if dos:
        J("(()=>{const d=%s; const a=[...d.querySelectorAll('a')].find(a=>/Dossiê de crédito/.test(a.innerText)); a.click();})()" % DLG)
        espera("location.href.indexOf('dossie')>=0||location.pathname.indexOf('PT-04')>=0", 6); time.sleep(.8)
        onde = J("location.pathname+location.hash"); blk = J("[...document.querySelectorAll('main h2,main h3')].filter(h=>h.getClientRects().length).map(h=>h.innerText.trim())")
        info(f'R4 {w} destino do "Dossiê de crédito"', [onde, blk, dlg_aberto()])
        if MODO == 'pr': chk(f'R4 {w} "Dossiê de crédito" do contrato abre a visão interna Dossiê e consentimento (sem ir ao portal)', 'GE-08' in onde and '#vis=dossie' in onde and 'Dossiê e consentimento' in (blk or []), [onde, blk])
    chk(f'R5 {w} sem erro de JS nas visões da GE-08', not J("(window.__errs||[]).length"), J("window.__errs"))

def ficha(w):
    recarrega('GE-08.dc.html'); J("localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Proprietário')")
    recarrega('GE-08.dc.html#vis=documentos')
    # entrada pela área de Documentos (menu de ações do bloco ou à vista)
    ent = J("(()=>{const a=[...document.querySelectorAll('main a')].find(a=>a.getAttribute('href')==='GE-08.dc.html#vis=ficha'); if(!a) return null; const vis=%s(a); const m=a.closest('[role=menu]'); if(m){ const b=m.parentElement.querySelector('.g2mais'); if(b) b.click(); } a.click(); return {vis, menu:!!m};})()" % VIS)
    espera("!!%s" % SEC, 6); time.sleep(.3)
    chk(f'F1 {w} Documentos › "Bens e avaliações" abre a ficha (#vis=ficha)', bool(ent) and J("location.hash") == '#vis=ficha' and bool(J("!!%s" % SEC)), [ent, J("location.hash")])
    info(f'F1 {w} onde fica o atalho', ent)
    outros = J("[...document.querySelectorAll('main h3')].filter(h=>h.getClientRects().length).map(h=>h.innerText.trim())")
    kp = J("[...document.querySelectorAll('main')].some(m=>/DÍVIDA ATIVA/i.test(m.innerText))")
    chk(f'F2 {w} a ficha mostra só o bloco dela, sem KPIs de contrato', outros == ['Ficha do grupo · Bens e avaliações'] and not kp, [outros, kp])
    g = verdes(); chk(f'F3 {w} BOT-01: uma só primária fora de painel, "Incluir bem"', g == ['Incluir bem'], g)
    vaz = J("(()=>{const s=%s; return s?s.innerText.replace(/\\s+/g,' '):''})()" % SEC)
    info(f'F4 {w} estado vazio (texto do bloco)', vaz)
    chk(f'F4 {w} estado vazio diz que não há bem e aponta "Incluir bem" (sem falar em filtro inexistente)', 'filtros' not in vaz.lower() and ('nenhum bem' in vaz.lower() or 'incluir bem' in vaz.lower()), vaz[-160:])
    shot(f'ficha-vazia-{w}')
    tw = J("document.documentElement.scrollWidth-document.documentElement.clientWidth")
    chk(f'F5 {w} sem rolagem lateral', tw <= 0, tw)

    # ---------- teclado: Incluir bem → Tab pelos campos → digitar → Espaço em "Salvar declaração" ----------
    J("(()=>{const b=[...document.querySelectorAll('header button')].find(b=>b.innerText.trim()==='Incluir bem'); b.focus();})()")
    c.tecla('Enter', 'Enter', 13, text='\r'); espera("!!%s" % DLG, 4); time.sleep(.3)
    ab = dlg_aberto(); tit = J("(()=>{const d=%s; return d?d.getAttribute('aria-label'):null})()" % DLG)
    seq = []
    for _ in range(14):
        c.tab(); time.sleep(.05)
        a = J("(()=>{const a=document.activeElement; return a?[a.tagName,a.id||'',(a.innerText||a.getAttribute('aria-label')||'').trim().slice(0,30),!!a.closest('aside[role=dialog]'),a.matches(':focus-visible'),getComputedStyle(a).outlineStyle+' '+getComputedStyle(a).outlineWidth+' '+getComputedStyle(a).boxShadow.slice(0,40)]:null})()")
        seq.append(a)
        if a and a[1] == 'fx_g_ficha_nome': c.call('Input.insertText', {'text': D1['nome']})
        if a and a[1] == 'fx_g_ficha_tipo':
            c.tecla('ArrowDown', 'ArrowDown', 40); c.tecla('ArrowUp', 'ArrowUp', 38)
        if a and a[1] == 'fx_g_ficha_valor': c.call('Input.insertText', {'text': D1['valor']})
        if a and a[1] == 'fx_g_ficha_data':
            for ch in '03102026': c.tecla(ch, 'Digit' + ch, 48 + int(ch), text=ch)
        if a and a[1] == 'fx_g_ficha_responsavel': c.call('Input.insertText', {'text': D1['responsavel']})
        if a and a[1] == 'fx_g_ficha_fonte': c.call('Input.insertText', {'text': D1['fonte']})
        if a and a[0] == 'BUTTON' and J("getComputedStyle(document.activeElement).backgroundColor") == 'rgb(30, 122, 76)': break
    info(f'K1 {w} sequência do Tab no painel [tag,id,texto,no painel,:focus-visible,contorno]', seq)
    dentro = []
    for s_ in seq:
        if s_ and not (dentro and dentro[-1][1] == s_[1] and s_[1] == 'fx_g_ficha_data'): dentro.append(s_)
    chk(f'K1 {w} Enter em "Incluir bem" abre o painel e o Tab percorre só o painel, com foco visível', ab and tit == 'Incluir bem' and all(s[3] for s in dentro) and all(s[4] and ('solid' in s[5] or 'rgb' in s[5].split(' ', 2)[-1]) for s in dentro), [ab, tit, dentro[:3]])
    vals = {k: campo('fx_g_ficha_' + k) for k in ('nome', 'tipo', 'valor', 'data', 'responsavel', 'fonte')}
    info(f'K2 {w} valores digitados pelo teclado', vals)
    if vals.get('data') != D1['data']: fill('fx_g_ficha_data', D1['data']); info(f'K2 {w} data pelo teclado não ficou ISO; usado setter', vals.get('data'))
    if vals.get('tipo') != D1['tipo']: fill('fx_g_ficha_tipo', D1['tipo'])
    rn = rot_prim()
    chk(f'N1 {w} o botão de gravar da inclusão diz "Salvar declaração" (como o PR declara)', rn == 'Salvar declaração', rn)
    if J("getComputedStyle(document.activeElement).backgroundColor") != 'rgb(30, 122, 76)':
        J("(()=>{const d=%s; const b=[...d.querySelectorAll('button')].find(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'); if(b) b.focus();})()" % DLG)
    c.tecla(' ', 'Space', 32, text=' '); time.sleep(.6)
    x = item(D1['nome'])
    chk(f'K2 {w} Espaço em "Salvar declaração" grava pelo teclado; painel fecha', bool(x) and not dlg_aberto(), [x, dlg_aberto(), dlg_txt()])
    fo = J("(()=>{const a=document.activeElement; return a?[a.tagName,(a.innerText||'').trim().slice(0,30)]:null})()")
    chk(f'K3 {w} ao fechar o painel o foco volta para quem abriu ("Incluir bem")', bool(fo) and fo[1] == 'Incluir bem', fo)
    t = toast(); info(f'K2 {w} aviso', t)
    chk(f'P1 {w} 850000,50 grava como texto decimal "850000.50" (sem float), com data, responsável e fonte', bool(x) and x.get('valor') == '850000.50' and x.get('data') == '2026-03-10' and x.get('responsavel') == 'Ana' and x.get('fonte') == D1['fonte'] and x.get('registradoPor') == 'Proprietário', x)
    chk(f'P2 {w} documentos CAD-02 intocados pela ficha (chave própria; {DOC_LS} ausente)', ls(DOC_LS) is None, ls(DOC_LS))
    # ---------- mouse: 12.500.000,00, zero e pendente ----------
    novo(D2); novo(D3); novo(D4)
    l = linhas() or []
    info(f'P3 {w} linhas da lista', l)
    def lin(n): return next((r for r in l if r and r[0].endswith(n) or (r and n in r[0])), None)
    a1, a2, a3, a4 = lin(D1['nome']), lin(D2['nome']), lin(D3['nome']), lin(D4['nome'])
    chk(f'P3 {w} lista mostra R$ 850.000,50, R$ 12.500.000,00, R$ 0,00 (Declarado) e "A informar" (Pendente)',
        bool(a1 and a2 and a3 and a4) and 'R$ 850.000,50' in a1 and 'R$ 12.500.000,00' in a2 and 'R$ 0,00' in a3 and 'Declarado' in a3[1] and 'A informar' in a4 and 'Pendente' in a4[1], [a1, a2, a3, a4])
    x2, x3, x4 = item(D2['nome']), item(D3['nome']), item(D4['nome'])
    chk(f'P4 {w} armazenado: 12500000.00, zero "0.00" ≠ ausente null', bool(x2 and x3 and x4) and x2['valor'] == '12500000.00' and x3['valor'] == '0.00' and x4['valor'] is None, [x2 and x2['valor'], x3 and x3['valor'], x4 and x4['valor']])
    chk(f'P5 {w} origem com tipo, data, responsável, fonte e idade (220 dias)', bool(a1) and 'Avaliação de mercado' in a1[3] and '10/03/2026' in a1[3] and 'Ana' in a1[3] and '220 dias' in a1[3], a1)
    shot(f'ficha-4itens-{w}')
    # ---------- recarregar preserva; reabrir devolve os valores ----------
    recarrega()
    l2 = linhas() or []
    chk(f'P6 {w} recarregar a página preserva os 4 bens com os mesmos valores', sorted(map(tuple, l2)) == sorted(map(tuple, l)) and len(l2) == 4, [l2, l])
    abrir(D1['nome']); v1 = campo('fx_g_ficha_valor'); J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()" % DLG); time.sleep(.3)
    abrir(D2['nome']); v2 = campo('fx_g_ficha_valor'); hist0 = campo('fx_g_ficha_hist'); J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()" % DLG); time.sleep(.3)
    info(f'P7 {w} reabrir: valor no campo', [v1, v2, hist0])
    chk(f'P7 {w} reabrir 850000,50 devolve o mesmo valor no formato pt-BR canônico "850.000,50" (r2: formato deliberado do Codex)', v1 == '850.000,50', v1)
    chk(f'P8 {w} reabrir 12.500.000,00 devolve o mesmo texto digitado', v2 == '12.500.000,00', v2)
    x0 = item(D2['nome']); abrir(D2['nome']); prim_dlg(); time.sleep(.4); x1 = item(D2['nome'])
    chk(f'P9 {w} reabrir e salvar sem mudar nada não cria versão nem muda a revisão (formato canônico ≠ alteração)', bool(x0) and x1 == x0 and not dlg_aberto(), [x0 and (x0['rev'], len(x0['historico'])), x1 and (x1['rev'], len(x1['historico'])), dlg_txt()])
    abrir(D2['nome']); fill('fx_g_ficha_valor', campo('fx_g_ficha_valor')); prim_dlg(); time.sleep(.4); x2 = item(D2['nome'])
    chk(f'P10 {w} salvar o valor reaberto "12.500.000,00" (mesmo texto) mantém 12500000.00 sem versão nova', bool(x2) and x2['valor'] == '12500000.00' and x2['rev'] == x0['rev'] and x2['historico'] == x0['historico'], x2)
    # ---------- confirmar vigência: preserva a declaração; repetir no dia não duplica ----------
    antes = item(D1['nome'])
    abrir(D1['nome']); fill('fx_g_ficha_oper', 'Confirmar vigência'); time.sleep(.3)
    rot = J("(()=>{const d=%s; return [...d.querySelectorAll('button')].filter(b=>b.getClientRects().length).map(b=>b.innerText.trim()).filter(Boolean)})()" % DLG)
    camposv = J("(()=>{const d=%s; return [...d.querySelectorAll('input,select,textarea')].filter(e=>e.getClientRects().length).map(e=>e.id)})()" % DLG)
    gd = verdes('painel')
    info(f'C1 {w} botões e campos ao confirmar', [rot, camposv, gd])
    chk(f'C1 {w} confirmar oculta os campos da declaração e tem um só verde no painel', len(gd) == 1 and 'fx_g_ficha_valor' not in camposv, [gd, camposv])
    chk(f'C1b {w} o verde do painel nomeia a ação: "Confirmar vigência"', gd == ['Confirmar vigência'], gd)
    prim_dlg(); time.sleep(.5)
    dep = item(D1['nome'])
    chk(f'C2 {w} confirmação registra quem/quando à parte e preserva valor, data, fonte, responsável e quem registrou', bool(dep) and dep['confirmacoes'] == [{'quem': 'Proprietário', 'quando': '2026-10-16'}] and all(dep[k] == antes[k] for k in ('valor', 'data', 'fonte', 'responsavel', 'registradoPor', 'registradoEm', 'tipo', 'nome')) and dep['historico'] == [], [antes, dep])
    l3 = linhas() or []; r1 = next((r for r in l3 if D1['nome'] in r[0]), None)
    chk(f'C3 {w} linha mostra "Confirmado por Proprietário em 16/10/2026" e a idade continua 220 dias', bool(r1) and 'Confirmado por Proprietário em 16/10/2026' in r1[4] and '220 dias' in r1[3], r1)
    abrir(D1['nome']); fill('fx_g_ficha_oper', 'Confirmar vigência'); time.sleep(.2); prim_dlg(); time.sleep(.5)
    dep2 = item(D1['nome']); t2 = toast()
    chk(f'C4 {w} confirmar de novo no mesmo dia não duplica nem muda a revisão', bool(dep2) and len(dep2['confirmacoes']) == 1 and dep2['rev'] == dep['rev'], [dep2, t2])
    info(f'C4 {w} aviso da 2ª confirmação', t2)
    # pendente não confirma
    abrir(D4['nome']); fill('fx_g_ficha_oper', 'Confirmar vigência'); time.sleep(.2); prim_dlg(); time.sleep(.4)
    tx = dlg_txt() or ''
    chk(f'C5 {w} pendente não aceita confirmação; motivo à vista no painel', dlg_aberto() and 'complete a declaração' in tx and (item(D4['nome']) or {}).get('confirmacoes') == [], tx[:300])
    btn_dlg('Cancelar'); time.sleep(.2); btn_dlg('Descartar alterações'); time.sleep(.3)
    if dlg_aberto(): J("(()=>{const d=%s; const b=[...d.querySelectorAll('button')].find(b=>/Descartar/.test(b.innerText)); if(b) b.click();})()" % DLG); time.sleep(.3)
    # ---------- alteração gera histórico ----------
    abrir(D1['nome']); fill('fx_g_ficha_valor', '900.000,00'); fill('fx_g_ficha_data', '2026-10-16'); time.sleep(.2); prim_dlg(); time.sleep(.5)
    h = item(D1['nome'])
    chk(f'H1 {w} alteração guarda a versão anterior com as confirmações; a nova começa sem confirmação', bool(h) and h['valor'] == '900000.00' and len(h['historico']) == 1 and h['historico'][0]['valor'] == '850000.50' and h['historico'][0]['confirmacoes'] == [{'quem': 'Proprietário', 'quando': '2026-10-16'}] and h['confirmacoes'] == [], h)
    abrir(D1['nome']); hh = campo('fx_g_ficha_hist') or ''
    chk(f'H2 {w} detalhe mostra "Versões anteriores" com R$ 850.000,50 e a confirmação', 'R$ 850.000,50' in hh and 'Proprietário em 16/10/2026' in hh, hh)
    J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()" % DLG); time.sleep(.3)
    # ---------- validação ----------
    novo({'nome': 'Teste ambíguo', 'tipo': 'Valor contábil', 'valor': '850000.50', 'data': '2026-03-10', 'responsavel': 'Ana', 'fonte': 'x'})
    e1 = dlg_txt() or ''
    chk(f'V1 {w} "850000.50" (ponto decimal ambíguo) é recusado com motivo no campo; nada gravado', dlg_aberto() and 'Informe o valor em R$' in e1 and item('Teste ambíguo') is None, e1[:300])
    fill('fx_g_ficha_valor', '850.000,50'); fill('fx_g_ficha_fonte', ''); time.sleep(.1); prim_dlg(); time.sleep(.4)
    e2 = dlg_txt() or ''
    chk(f'V2 {w} valor sem fonte é recusado', dlg_aberto() and 'Informe a fonte do valor' in e2 and item('Teste ambíguo') is None, e2[:300])
    J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()" % DLG); time.sleep(.2)
    J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>/Descartar/.test(b.innerText)); if(b) b.click();})()" % DLG); time.sleep(.3)
    # ---------- falha de gravação (quota) e recuperação sem perder a edição ----------
    J("window.__falha=true; if(!window.__orig){ window.__orig=Storage.prototype.setItem; Storage.prototype.setItem=function(k,v){ if(window.__falha&&String(k).indexOf('ficha')>=0) throw new DOMException('cota','QuotaExceededError'); return window.__orig.apply(this,arguments); }; }")
    antes2 = ls()
    abrir(D2['nome']); fill('fx_g_ficha_valor', '13.000.000,00'); time.sleep(.1); prim_dlg(); time.sleep(.5)
    tq = dlg_txt() or ''; vq = campo('fx_g_ficha_valor'); lq = linhas() or []; rq = next((r for r in lq if D2['nome'] in r[0]), None)
    chk(f'Q1 {w} cota cheia: painel continua aberto com o motivo e o rascunho "13.000.000,00"; armazenamento e lista sem mudança', dlg_aberto() and 'Não foi possível gravar' in tq and vq == '13.000.000,00' and ls() == antes2 and bool(rq) and 'R$ 12.500.000,00' in rq[2], [tq[:240], vq, rq])
    shot(f'ficha-cota-{w}')
    J("window.__falha=false"); prim_dlg(); time.sleep(.5)
    xq = item(D2['nome'])
    chk(f'Q2 {w} liberado o armazenamento, "Salvar declaração" de novo grava a edição preservada (13000000.00, histórico 1)', bool(xq) and xq['valor'] == '13000000.00' and len(xq['historico']) == 1 and not dlg_aberto(), [xq, dlg_txt()])
    J("window.__falha=true"); n0 = len((db() or {}).get('items', []))
    novo({'nome': 'Novo na cota', 'tipo': 'Valor contábil', 'valor': '1,00', 'data': '2026-10-16', 'responsavel': 'Ana', 'fonte': 'x'})
    tq2 = dlg_txt() or ''; nm = campo('fx_g_ficha_nome')
    chk(f'Q3 {w} cota cheia em inclusão: nada criado; painel reabre com o rascunho', len((db() or {}).get('items', [])) == n0 and dlg_aberto() and nm == 'Novo na cota' and 'Não foi possível gravar' in tq2 and not any('Novo na cota' in r[0] for r in (linhas() or [])), [tq2[:200], nm, linhas()])
    J("window.__falha=false"); prim_dlg(); time.sleep(.5)
    nq = [i for i in (db() or {}).get('items', []) if i['nome'] == 'Novo na cota']
    chk(f'Q4 {w} recuperação da inclusão grava uma só vez', len(nq) == 1 and sum(1 for r in (linhas() or []) if 'Novo na cota' in r[0]) == 1, [nq, linhas()])
    # ---------- Cartões, filtro rápido e ordem ----------
    modo('cartoes'); k = cartoes() or []
    info(f'M1 {w} cartões', k)
    chk(f'M1 {w} modo Cartões mostra os bens com valor e situação', len(k) == 5 and any('R$ 12.500.000,00' in x or 'R$ 13.000.000,00' in x for x in k) and any('A informar' in x for x in k), k)
    shot(f'ficha-cartoes-{w}')
    r = abrir(D3['nome']); vz = campo('fx_g_ficha_valor')
    chk(f'M2 {w} cartão abre o detalhe (zero volta "0,00")', r == 'ok' and dlg_aberto() and vz == '0,00', [r, vz])
    J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()" % DLG); time.sleep(.3)
    modo('tabela')
    J("(()=>{const s=%s; const b=[...s.querySelectorAll('button')].find(b=>b.getClientRects().length&&/^Pendente/.test(b.innerText.trim())); if(b) b.click();})()" % SEC); time.sleep(.3)
    lp = linhas() or []
    chk(f'M3 {w} filtro rápido "Pendente" mostra só o pendente', len(lp) == 1 and D4['nome'] in lp[0][0], lp)
    J("(()=>{const s=%s; const b=[...s.querySelectorAll('button')].find(b=>b.getClientRects().length&&/^Todos/.test(b.innerText.trim())); if(b) b.click();})()" % SEC); time.sleep(.3)
    J("(()=>{const b=document.querySelector('[data-g2g=g_ficha] button[aria-label=\"Ordenar por Valor declarado\"]'); if(b) b.click();})()"); time.sleep(.3)
    lo = [r[2] for r in (linhas() or [])]
    info(f'M4 {w} ordem por valor', lo)
    chk(f'M4 {w} ordenar por valor é numérico (0 < 1 < 900 mil < 13 mi; pendente no fim)', lo == ['R$ 0,00', 'R$ 1,00', 'R$ 900.000,00', 'R$ 13.000.000,00', 'A informar'], lo)
    # ---------- DS: TAB-09 e TAB-10 na ficha; alvos de toque ----------
    s9 = J(SETA) or {}; cb = [x for x in (J(CAB) or []) if 'g_ficha' in str(x.get('g'))]
    chk(f'D1 {w} TAB-09 seta de abrir na 1ª coluna da ficha', s9.get('n', 0) >= 5 and not s9.get('ruins'), s9)
    chk(f'D2 {w} TAB-10 cabeçalho da ficha com 40 px', bool(cb) and all(abs(x['h'] - 40) <= 1 for x in cb), cb)
    if w < 500:
        pq = J("(()=>{const s=%s; const vis=%s; return [...document.querySelectorAll('header button'),...s.querySelectorAll('button,a,input,select')].filter(e=>vis(e)&&!e.closest('[role=menu]')&&e.getBoundingClientRect().height<43.5).map(e=>[(e.innerText||e.getAttribute('aria-label')||e.id||e.type).trim().slice(0,24),Math.round(e.getBoundingClientRect().height)])})()" % (SEC, VIS))
        info(f'D3 {w} alvos < 44 px na ficha', pq)
        abrir(D2['nome']); time.sleep(.2)
        alc = J("(()=>{const d=%s; const b=[...d.querySelectorAll('button')].find(b=>getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)'); b.scrollIntoView({block:'center'}); const r=b.getBoundingClientRect(); const t=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2); const pr=d.getBoundingClientRect(); return {alc:!!t&&(t===b||b.contains(t)), h:Math.round(r.height), painel:[Math.round(pr.left),Math.round(pr.width)], rola:d.scrollHeight>d.clientHeight};})()" % DLG)
        chk(f'D4 {w} formulário longo: painel dentro da tela e o botão de gravar alcançável (44 px)', alc['alc'] and alc['painel'][0] >= 0 and alc['painel'][1] <= 390 and alc['h'] >= 43.5, alc)
        shot(f'ficha-form-{w}')
        J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()" % DLG); time.sleep(.3)
    # ---------- Esc fecha e devolve o foco à linha ----------
    J("(()=>{const s=%s; const r=[...s.querySelectorAll('[data-g2g=g_ficha] [role=row][data-rid]')].find(r=>r.innerText.indexOf(%s)>=0); r.focus();})()" % (SEC, json.dumps(D3['nome'])))
    op = J("(()=>{const a=document.activeElement; return [a.tagName,a.className,(a.innerText||a.getAttribute('aria-label')||'').trim().slice(0,30)]})()")
    c.tecla('Enter', 'Enter', 13, text='\r'); espera("!!%s" % DLG, 4); time.sleep(.3); ab2 = dlg_aberto()
    c.tab(); c.tecla('Escape', 'Escape', 27); time.sleep(.4)
    fe = J("(()=>{const a=document.activeElement; return [a.tagName,a.className,(a.innerText||a.getAttribute('aria-label')||'').trim().slice(0,30)]})()")
    chk(f'K4 {w} Enter na linha abre o detalhe; Tab + Esc fecha e devolve o foco à linha', ab2 and not dlg_aberto() and fe == op, [op, ab2, dlg_aberto(), fe])
    chk(f'K5 {w} sem erro de JS na ficha', not J("(window.__errs||[]).length"), J("window.__errs"))

def sem_papel(w, perfil):
    J("localStorage.setItem('safrion.perfilDemo',%s)" % json.dumps(perfil)); recarrega()
    antes = ls()
    nota = J("(()=>{const s=%s; const n=s&&s.querySelector('[role=note]'); return n&&n.getClientRects().length?n.innerText.trim():null})()" % SEC)
    b = incluir(); time.sleep(.3)
    chk(f'S1 {w} {perfil}: motivo à vista e "Incluir bem" indisponível', bool(nota) and 'somente a direção' in nota.lower() and b in ('desabilitado',) and not dlg_aberto(), [nota, b])
    abrir(D2['nome']); tx = dlg_txt() or ''
    edit = J("(()=>{const d=%s; return [...d.querySelectorAll('input,select,textarea')].filter(e=>e.getClientRects().length&&!e.disabled&&!e.readOnly).map(e=>e.id)})()" % DLG)
    gb = verdes('painel')
    chk(f'S2 {w} {perfil}: detalhe só consulta (motivo, nenhum campo editável, sem botão de gravar)', 'Consulta' in tx and not edit and not gb, [tx[:200], edit, gb])
    J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()" % DLG); time.sleep(.2)
    # papel retirado com o painel aberto (outra aba troca o perfil): item existente e inclusão
    J("localStorage.setItem('safrion.perfilDemo','Proprietário')"); recarrega(); antes = ls()
    abrir(D2['nome']); fill('fx_g_ficha_valor', '1,00'); J("localStorage.setItem('safrion.perfilDemo',%s)" % json.dumps(perfil)); prim_dlg(); time.sleep(.4)
    t3 = dlg_txt() or ''
    chk(f'S3 {w} {perfil}: papel retirado com o painel aberto: não grava e o motivo aparece no painel (item existente)', ls() == antes and 'Somente a direção' in t3, t3[:300])
    J("localStorage.setItem('safrion.perfilDemo','Proprietário')"); recarrega()
    novo({'nome': 'Sem papel', 'tipo': 'Valor contábil', 'valor': '1,00', 'data': '2026-10-16', 'responsavel': 'Ana', 'fonte': 'x'}, salvar=False)
    J("localStorage.setItem('safrion.perfilDemo',%s)" % json.dumps(perfil)); prim_dlg(); time.sleep(.4)
    t4 = dlg_txt() or ''
    info(f'S4 {w} {perfil} painel de inclusão após perder o papel', t4[:400])
    chk(f'S4 {w} {perfil}: papel retirado na inclusão: não grava e o motivo aparece no painel', ls() == antes and 'Somente a direção' in t4, t4[:300])
    J("localStorage.setItem('safrion.perfilDemo','Proprietário')"); recarrega()
    J("localStorage.setItem('safrion.perfilDemo','Proprietário')")

def leitura(w):
    boa = ls()
    J("localStorage.setItem(%s,'{quebrado')" % json.dumps(CEN_LS)); recarrega()
    al = J("(()=>{const s=%s; const a=s&&s.querySelector('[role=alert]'); return a&&a.getClientRects().length?a.innerText.trim():null})()" % SEC)
    tn = J("(()=>{const s=%s; return !!s&&[...s.querySelectorAll('button')].some(b=>b.getClientRects().length&&b.innerText.trim()==='Tentar novamente')})()" % SEC)
    chk(f'L1 {w} armazenamento ilegível: alerta com motivo e "Tentar novamente"; dado preservado', bool(al) and 'Não foi possível ler a ficha' in al and tn and ls() == '{quebrado', [al, tn, ls()])
    novo({'nome': 'Durante a falha', 'tipo': 'Valor contábil', 'valor': '1,00', 'data': '2026-10-16', 'responsavel': 'Ana', 'fonte': 'x'})
    chk(f'L2 {w} incluir com leitura quebrada não apaga o armazenamento', ls() == '{quebrado', ls())
    J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()" % DLG); time.sleep(.2)
    J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>/Descartar/.test(b.innerText)); if(b) b.click();})()" % DLG); time.sleep(.2)
    J("localStorage.removeItem(%s)" % json.dumps(CEN_LS)) if boa is None else J("localStorage.setItem(%s,%s)" % (json.dumps(CEN_LS), json.dumps(boa)))
    J("(()=>{const s=%s; const b=[...s.querySelectorAll('button')].find(b=>b.innerText.trim()==='Tentar novamente'); if(b) b.click();})()" % SEC); time.sleep(.5)
    l = linhas() or []
    al2 = J("(()=>{const s=%s; const a=s&&s.querySelector('[role=alert]'); return a&&a.getClientRects().length?a.innerText.trim():null})()" % SEC)
    chk(f'L3 {w} restaurado o armazenamento, "Tentar novamente" volta a lista sem recarregar', len(l) == 5 and not al2, [len(l), al2])

def duas_abas(w):
    recarrega()
    b = Aba(c.port)
    try:
        b.call('Emulation.setDeviceMetricsOverride', {'width': w, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False})
        b.call('Page.navigate', {'url': U('GE-08.dc.html#vis=ficha')}); espera("document.readyState==='complete'&&!!%s" % SEC, 15, b); time.sleep(.6)
        abrir(D3['nome']); fill('fx_g_ficha_valor', '111,11')           # aba A edita sem salvar
        abrir(D3['nome'], b); fill('fx_g_ficha_valor', '777,00', b); prim_dlg(b); time.sleep(.5)   # aba B salva
        xb = item(D3['nome'])
        prim_dlg(); time.sleep(.5)                     # aba A tenta salvar
        ta = dlg_txt() or ''; va = campo('fx_g_ficha_valor'); xa = item(D3['nome'])
        chk(f'A1 {w} duas abas: a edição da outra aba é detectada; rascunho preservado e a versão mais nova fica', bool(xb) and xb['valor'] == '777.00' and 'Outra edição foi salva' in ta and va == '111,11' and xa['valor'] == '777.00', [xb and xb['valor'], ta[:200], va, xa and xa['valor']])
        J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()" % DLG); time.sleep(.2)
        J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>/Descartar/.test(b.innerText)); if(b) b.click();})()" % DLG); time.sleep(.3)
        abrir(D3['nome']); vr = campo('fx_g_ficha_valor')
        chk(f'A2 {w} reabrir na aba A lê a versão da aba B (777,00)', vr == '777,00', vr)
        J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()" % DLG); time.sleep(.2)
        n0 = len(db()['items'])
        novo({'nome': 'Novo aba A', 'tipo': 'Valor contábil', 'valor': '5,00', 'data': '2026-10-16', 'responsavel': 'Ana', 'fonte': 'x'})
        novo({'nome': 'Novo aba B', 'tipo': 'Valor contábil', 'valor': '6,00', 'data': '2026-10-16', 'responsavel': 'Ana', 'fonte': 'x'}, b)
        nomes = [i['nome'] for i in db()['items']]
        chk(f'A3 {w} inclusões simultâneas nas duas abas: as duas ficam (nenhuma perdida)', len(nomes) == n0 + 2 and 'Novo aba A' in nomes and 'Novo aba B' in nomes, nomes)
        la = [r[0] for r in (linhas() or [])]
        info(f'A3 {w} lista da aba A depois da inclusão na B (sem recarregar)', la)
        # confirmação concorrente: as duas abas confirmam o mesmo item no mesmo dia
        abrir(D2['nome']); fill('fx_g_ficha_oper', 'Confirmar vigência')
        abrir(D2['nome'], b); fill('fx_g_ficha_oper', 'Confirmar vigência', b); prim_dlg(b); time.sleep(.4)
        prim_dlg(); time.sleep(.4); tc = dlg_txt() or ''
        xc = item(D2['nome'])
        chk(f'A4 {w} confirmação repetida em duas abas no mesmo dia: um só registro', bool(xc) and len(xc['confirmacoes']) == 1, [xc and xc['confirmacoes'], tc[:200]])
        info(f'A4 {w} retorno na aba A ao confirmar depois da B', tc[:240] if tc else toast())
        J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'); if(b) b.click();})()" % DLG); time.sleep(.2)
        J("(()=>{const d=%s; const b=d&&[...d.querySelectorAll('button')].find(b=>/Descartar/.test(b.innerText)); if(b) b.click();})()" % DLG); time.sleep(.2)
        chk(f'A5 {w} sem erro de JS na aba B', not b.js("(window.__errs||[]).length"), b.js("window.__errs"))
    finally:
        b.close()

try:
    for w in LARGS:
        h, e, t = (900, 1, False) if w > 500 else (844, 2, True)
        c.aparelho(w, h, e, t)
        c.goto(U('GE-08.dc.html'), .3); J("localStorage.clear(); localStorage.setItem('safrion.perfilDemo','Proprietário')")
        passo(f'regressão {w}', lambda: regressao(w))
        if MODO == 'base': continue
        passo(f'ficha {w}', lambda: ficha(w))
        passo(f'sem papel {w} Ana', lambda: sem_papel(w, 'Ana'))
        if w > 500:
            passo(f'sem papel {w} Rui', lambda: sem_papel(w, 'Rui'))
            passo(f'leitura {w}', lambda: leitura(w))
            passo(f'duas abas {w}', lambda: duas_abas(w))
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas' + (' · ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
