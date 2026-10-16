# -*- coding: utf-8 -*-
"""Revisão do Claude, PR #81 (EST-ONDA0, Codex): navegador real (mouse, teclado, toque a 390 px) e cenário salvo da base.
Uso: python3 -B est_onda0_rev_test.py <gen37>   (RENDER_DIR = _render a testar; LEGADO_DIR = _render da base para o V6)
Oráculos (contrato 6220342104): E1 devolução REQ-031 sem quantidade/condição presumidas; E2 NF 4533 presa ao pedido de origem.
O cenário é lido do localStorage (talhao-os-cenario-v1), não da tela. Dados sintéticos."""
import sys, os, time, json, tempfile, shutil, subprocess
G = sys.argv[1]; sys.path.insert(0, G)
from comp_lib import Chrome
from journeys import free
R = os.path.abspath(os.environ.get('RENDER_DIR') or os.path.join(G, '_render'))
LEG = os.environ.get('LEGADO_DIR')
CEN_LS = 'talhao-os-cenario-v1'
CONDS = ['Apta · volta ao disponível', 'Bloqueada para inspeção · vai para quarentena']
PED_SEM = 'PC-090 · Semente de soja 58 W · Coop. Vale'
PED_CX = 'PC-096 · Caixa de mamão Formosa 10 kg · Embalagens Açu'
OK, FAIL, NOTAS = [], [], []
def chk(v, n, c, x=''):
    (OK if c else FAIL).append(v + ' ' + n); print(('OK   ' if c else 'FALHA'), v, n, '' if c else '· ' + str(x)[:500], flush=True)
def nota(t): NOTAS.append(t); print('     nota:', t, flush=True)

# raiz servida: o render em /novo e, para o V6, a base em /base (mesma origem = mesmo localStorage, como a troca de versão)
RAIZ = tempfile.mkdtemp(prefix='est_onda0_rev_'); os.symlink(R, os.path.join(RAIZ, 'novo'))
if LEG: os.symlink(os.path.abspath(LEG), os.path.join(RAIZ, 'base'))
PORTA = free(); SRV = subprocess.Popen(['python3', '-m', 'http.server', str(PORTA), '--bind', '127.0.0.1', '--directory', RAIZ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(.6)
c = Chrome(); J = c.js
def U(pg, raiz='novo'): return f'http://127.0.0.1:{PORTA}/{raiz}/{pg}'
DLG = "[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getBoundingClientRect().width>1)"

def ls(): return J(f"localStorage.getItem({json.dumps(CEN_LS)})")
def cen():
    t = ls(); return json.loads(t) if t else None
def mv_dev(c0, prod='MAP 11-52'): return [m for m in ((c0 or {}).get('movs') or []) if m.get('tipo') == 'devolucao' and m.get('prod') == prod]
def mv_rec(c0): return [m for m in ((c0 or {}).get('movs') or []) if m.get('tipo') == 'recebimento-nf']
def it31(c0):
    if not c0: return None
    i = c0['reqs']['REQ-031']['itens'][0]; return dict(custodia=i['custodia'], devolvido=i['devolvido'], entregue=i['entregue'])
def lote(c0, k):
    l = ((c0 or {}).get('lotes') or {}).get(k); return l and dict(fisico=l.get('fisico'), quarentena=l.get('quarentena'))
def limpar(raiz='novo'):
    c.goto(U('Main.dc.html', raiz), .3); J("localStorage.clear();sessionStorage.clear();1")
def abrir(raiz='novo'):
    c.goto(U('EST.dc.html', raiz), 1.4)
def errs(): return J("(window.__errs||[]).concat([...document.querySelectorAll('.sc-logic-error')].map(e=>e.innerText))") or []

def centro(expr):
    """expr: JS que devolve o elemento; rola até ele e devolve o centro."""
    return J(f"(()=>{{const e=({expr}); if(!e) return null; e.scrollIntoView({{block:'center',inline:'nearest'}}); const r=e.getBoundingClientRect(); return [r.left+r.width/2,r.top+r.height/2,r.width,r.height];}})()")
def clique(expr, toque=False, duplo=False):
    r = centro(expr)
    if not r: return None
    time.sleep(.2); r = centro(expr)
    if toque: c.toque(r[0], r[1])
    else:
        c.mouse(r[0], r[1]); c.mouse(r[0], r[1], 'mousePressed', 'left'); c.mouse(r[0], r[1], 'mouseReleased', 'left')
        if duplo:   # segundo clique logo em seguida (duplo clique de quem tem pressa)
            c.call('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': r[0], 'y': r[1], 'button': 'left', 'clickCount': 2})
            c.call('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': r[0], 'y': r[1], 'button': 'left', 'clickCount': 2})
    time.sleep(.7); return r
def btn(txt, raiz='document'):
    return f"[...{raiz}.querySelectorAll('button,[role=button],a')].find(b=>b.innerText.replace(/\\s+/g,' ').trim()==={json.dumps(txt)}&&b.getClientRects().length>0)"
def btn_ini(txt, raiz='document'):
    return f"[...{raiz}.querySelectorAll('button,[role=button],a')].find(b=>b.innerText.replace(/\\s+/g,' ').trim().startsWith({json.dumps(txt)})&&b.getClientRects().length>0)"
NAV = "document.querySelector('nav[aria-label=\"Seções do estoque\"]')"
def secao(i, toque=False):
    """No estreito a faixa vira "<seção atual> ▾" (label.etp-atual): abre primeiro e depois toca a seção; devolve [x, y, L, A] do último alvo."""
    b = f"{NAV}.querySelectorAll('button')[{i - 1}]"
    if not J(f"{b}.getBoundingClientRect().width>0"):
        r0 = clique(f"{NAV}.querySelector('.etp-atual')", toque); secao.compacta = r0
    return clique(b, toque)
secao.compacta = None
def dlg():
    return J(f"""(()=>{{const d={DLG}; if(!d) return null; const r=d.getBoundingClientRect(); const q=s=>d.querySelector(s);
      const sel=q('#fx_g_dev_cond')||null, ped=q('#fx_g_rec_ped'), nf=q('#fx_g_rec_nf');
      return {{txt:d.innerText.replace(/\\s+/g,' '), alertas:[...d.querySelectorAll('[role=alert]')].map(x=>x.innerText.replace(/\\s+/g,' ')).join(' | '),
        qtd:(q('#fx_g_dev_qtd')||{{}}).value, cond:sel&&sel.value, condTxt:sel&&sel.selectedIndex>=0?sel.options[sel.selectedIndex].text:null, condOpts:sel&&[...sel.options].map(o=>o.text),
        ped:ped&&ped.value, pedDis:ped&&ped.disabled, nfRO:nf&&nf.readOnly, L:r.left, R:r.right, W:innerWidth, foco:d.contains(document.activeElement)}};}})()""")
def setv(campo, val):
    return J(f"""(()=>{{const d={DLG}; const e=d&&d.querySelector('#{campo}'); if(!e) return 'sem '+{json.dumps(campo)};
      const P=e.tagName==='SELECT'?HTMLSelectElement.prototype:(e.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
      Object.getOwnPropertyDescriptor(P,'value').set.call(e,{json.dumps(val)}); e.dispatchEvent(new Event('input',{{bubbles:true}})); e.dispatchEvent(new Event('change',{{bubbles:true}})); return e.value;}})()""")
def digitar(campo, txt, toque=False):
    """foca o campo pelo ponteiro (mouse ou toque) e digita como teclado (insertText)."""
    clique(f"({DLG}).querySelector('#{campo}')", toque); J(f"(()=>{{const e=({DLG}).querySelector('#{campo}'); e.select&&e.select(); return 1;}})()")
    c.call('Input.insertText', {'text': txt}); time.sleep(.3)
    return J(f"(({DLG}).querySelector('#{campo}')||{{}}).value")
def salvar(toque=False, duplo=False): return clique(btn('Salvar', DLG), toque, duplo)
def abrir_dev31(toque=False):
    r = clique(btn('Receber devolução da REQ-031'), toque)
    if not r: r = clique("[...document.querySelectorAll('[role=row]')].find(x=>/REQ-031/.test(x.innerText))", toque)
    return r
def foco():
    return J("""(()=>{const e=document.activeElement; if(!e||e===document.body) return {tag:'BODY'}; const cs=getComputedStyle(e);
      const vis=(cs.outlineStyle!=='none'&&parseFloat(cs.outlineWidth)>0)||(cs.boxShadow&&cs.boxShadow!=='none');
      return {tag:e.tagName,id:e.id||'',txt:(e.innerText||e.getAttribute('aria-label')||'').replace(/\\s+/g,' ').trim().slice(0,60),vis,
        noDlg:!!e.closest('aside[role=dialog]'),outline:cs.outlineStyle+' '+cs.outlineWidth,sombra:(cs.boxShadow||'').slice(0,50)};})()""")
def tab_ate(cond_js, n=120, shift=False):
    for i in range(n):
        c.tab(1, shift)
        if J(f"(()=>{{const e=document.activeElement; return !!e&&({cond_js});}})()"): return i + 1
    return None

try:
    c.aparelho(1440, 900)
    # ======================= V1 · E1 com mouse =======================
    limpar(); abrir(); secao(3); ab = abrir_dev31(); d = dlg(); c0 = cen()
    print('V1 abriu:', d and {k: d[k] for k in ('qtd', 'cond', 'condTxt', 'condOpts')}, '| cenário salvo:', 'vazio (CEN0)' if c0 is None else len(c0.get('movs', [])))
    chk('V1', 'a abertura não presume quantidade (vazia)', bool(d) and d['qtd'] == '', d and d['qtd'])
    chk('V1', 'a abertura não presume condição (nenhuma condição válida escolhida)', bool(d) and d['cond'] not in CONDS, d and d['cond'])
    chk('V1', 'a custódia aparece só na dica (500 kg com Paula)', bool(d) and 'Em custódia: 500 kg' in d['txt'], d and d['txt'][:200])
    chk('V1', 'A1: a condição abre em "Escolha a condição", com as duas condições como opções', bool(d) and d['condTxt'] == 'Escolha a condição' and d['condOpts'] == ['Escolha a condição'] + CONDS, d and [d['condTxt'], d['condOpts']])
    chk('V1', 'o seletor de condição mostra um texto legível ao abrir (sem "[object Object]")', bool(d) and d['condTxt'] and 'object' not in d['condTxt'] and all('object' not in o for o in d['condOpts']), d and [d['condTxt'], d['condOpts']])
    antes = ls(); salvar(); d = dlg(); depois = ls(); c1 = cen()
    print('V1 salvar sem mexer:', d and d['alertas'], '| MV devolução:', [(m.get('id'), m.get('qtd'), m.get('apto')) for m in mv_dev(c1)], '| REQ-031:', it31(c1))
    chk('V1', 'salvar sem mexer é recusado e o formulário continua aberto', bool(d), 'formulário fechou')
    chk('V1', 'a recusa diz o que corrigir (quantidade e condição)', bool(d) and 'quantidade' in d['alertas'].lower() and 'condição' in d['alertas'].lower(), d and d['alertas'])
    chk('V1', 'cenário salvo inalterado após a recusa (sem MV, custódia 500)', depois == antes and not mv_dev(c1), [it31(c1), [(m.get('qtd'), m.get('apto')) for m in mv_dev(c1)]])
    if d:
        v = digitar('fx_g_dev_qtd', '480'); setv('fx_g_dev_cond', CONDS[0]); n0 = len((cen() or {}).get('movs') or [])
        salvar(duplo=True); d2 = dlg(); c2 = cen(); devs = mv_dev(c2)
        print('V1 480 Apta (duplo clique):', 'aberto: ' + d2['alertas'] if d2 else 'fechou', '| MV:', [(m.get('id'), m.get('qtd'), m.get('apto')) for m in devs], '| REQ-031:', it31(c2), '| M26-07:', lote(c2, 'MAP 11-52|M26-07'))
        chk('V1', '480 + Apta grava um MV de devolução de 480 apto', len(devs) == 1 and devs[0].get('qtd') == 480 and devs[0].get('apto') is True, devs)
        chk('V1', 'custódia 500 → 20 kg', (it31(c2) or {}).get('custodia') == 20, it31(c2))
        chk('V1', 'duplo clique no Salvar não duplica (um MV, um movimento novo)', len(devs) == 1 and len(c2['movs']) - n0 == 1, len(c2['movs']) - n0)
        # repetir o envio: reabrir e mandar 480 de novo (outra pessoa com a tela velha) não grava
        abrir_dev31(); digitar('fx_g_dev_qtd', '480'); setv('fx_g_dev_cond', CONDS[0]); a3 = ls(); salvar(); d3 = dlg(); c3 = cen()
        print('V1 repetir 480:', d3 and d3['alertas'])
        chk('V1', 'reenviar 480 com custódia 20 é recusado, com a correção, sem mudar o cenário', bool(d3) and '20' in d3['alertas'] and ls() == a3, d3 and d3['alertas'])
        if d3: clique(btn('Cancelar', DLG)); clique(btn('Descartar', 'document')) if J(btn('Descartar') + "!=null") else None
    else:
        nota('V1: o formulário fechou ao salvar sem mexer (gravou); passos 480/duplo clique não aplicáveis')
    e = errs(); chk('V1', 'sem erro de script', not e, e)

    # ======================= V2 · E2 com mouse =======================
    limpar(); abrir(); r = clique(btn('Conferir NF 4533')); d = dlg()
    print('V2 abriu NF 4533:', d and {k: d[k] for k in ('ped', 'pedDis', 'nfRO')})
    chk('V2', 'NF 4533 abre presa ao PC-090 (pedido só leitura)', bool(d) and d['ped'] == PED_SEM and d['pedDis'] is True, d and [d['ped'], d['pedDis']])
    chk('V2', 'número da NF de origem só leitura', bool(d) and d['nfRO'] is True, d and d['nfRO'])
    forcado = False
    if d and d['pedDis']:   # caminho de troca que ainda existe: cliente velho ou adulterado manda outro pedido (o handler é quem decide)
        J(f"({DLG}).querySelector('#fx_g_rec_ped').disabled=false"); forcado = True
    setv('fx_g_rec_ped', PED_CX); time.sleep(.3)
    digitar('fx_g_rec_conf', '1000'); digitar('fx_g_rec_apto', '1000'); setv('fx_g_rec_quar', '0')
    if J(f"!(({DLG}).querySelector('#fx_g_rec_val')||{{readOnly:true}}).readOnly"): setv('fx_g_rec_val', '12/2099')
    setv('fx_g_rec_div', 'Falta'); setv('fx_g_rec_obs', 'Entrega parcial (sintético)')
    antes = ls(); salvar(); d = dlg(); c1 = cen(); rec = mv_rec(c1)
    print('V2 troca para PC-096 (' + ('forçada no DOM' if forcado else 'pela tela') + '):', d and d['alertas'], '| movimentos de recebimento:', [(m.get('id'), m.get('qtd'), m.get('un'), m.get('prod'), m.get('lote')) for m in rec])
    al = (d or {}).get('alertas', '')
    chk('V2', 'trocar para PC-096 e salvar é recusado com "Item diferente do pedido"', bool(d) and 'Item diferente do pedido' in al, al or 'formulário fechou (gravou)')
    chk('V2', 'A4: a mensagem "Item diferente do pedido" aparece uma vez só', al.count('Item diferente do pedido') == 1, al)
    chk('V2', 'a recusa diz o que diverge (item, unidade e fornecedor)', all(x in al for x in ('Semente de soja 58 W', 'Caixa de mamão', 'kg', 'un', 'Coop. Vale', 'Embalagens Açu')), al)
    chk('V2', 'cenário salvo inalterado (nenhum MV de recebimento)', ls() == antes and not rec, [(m.get('id'), m.get('qtd'), m.get('prod')) for m in rec])
    # comando direto (outra tela/aba que não passe pelo formulário): o comando também confere
    tem = J("typeof estReceber==='function'&&typeof E2==='object'")
    if tem:
        r2 = J(f"""(()=>{{const b=E2.recs.find(r=>/4533/.test(r.nf)); const p=E2.pedidos.find(p=>p.id==='PC-096');
          const d=Object.assign({{}},b,{{ped:p.label,item:p.item,un:p.un,forn:p.forn,conf:1000,apto:1000,quar:0,val:'—',div:'Falta',obs:'x'}});
          const a=localStorage.getItem({json.dumps(CEN_LS)}); const r=window.__cen.cenMudar(null,c=>estReceber(c,d,'Rui','REV-V2C')); return [r.erro||r.msg||'',a===localStorage.getItem({json.dumps(CEN_LS)})];}})()""")
        print('V2 comando direto:', r2)
        chk('V2', 'comando direto com a NF 4533 rebatizada de caixa é recusado sem gravar', bool(r2) and 'Item diferente do pedido' in r2[0] and r2[1], r2)
    else: nota('V2: estReceber não está no escopo global da página; comando direto coberto pelo teste Node do Codex')
    if dlg(): clique(btn('Cancelar', DLG)); (clique(btn('Descartar')) if J(btn('Descartar') + "!=null") else None)
    e = errs(); chk('V2', 'sem erro de script', not e, e)

    # ======================= V3 · fluxos normais =======================
    limpar(); abrir(); clique(btn('Conferir NF 4533')); a0 = cen()
    digitar('fx_g_rec_conf', '20000'); digitar('fx_g_rec_apto', '20000'); setv('fx_g_rec_quar', '0'); setv('fx_g_rec_val', '06/2027')
    salvar(); d = dlg(); c1 = cen(); rec = mv_rec(c1)
    print('V3 NF 4533 coerente:', 'aberto: ' + d['alertas'] if d else 'fechou', '| MV:', [(m.get('id'), m.get('qtd'), m.get('un'), m.get('prod'), m.get('lote')) for m in rec], '| S58-0926:', lote(c1, 'Semente de soja 58 W|S58-0926'))
    chk('V3', 'NF 4533 coerente (PC-090, 20.000 kg) grava um recebimento de 20.000 kg no S58-0926', d is None and len(rec) == 1 and rec[0].get('qtd') == 20000 and rec[0].get('prod') == 'Semente de soja 58 W', [d and d['alertas'], rec])
    prim = J("[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&getComputedStyle(b).backgroundColor==='rgb(30, 122, 76)').map(b=>b.innerText.trim())")
    print('V3 primária depois:', prim)
    secao(3); abrir_dev31(); digitar('fx_g_dev_qtd', '480'); setv('fx_g_dev_cond', CONDS[0]); salvar(); d = dlg(); c2 = cen()
    abrir_dev31(); d0 = dlg(); digitar('fx_g_dev_qtd', '20'); setv('fx_g_dev_cond', CONDS[1]); salvar(); d1 = dlg()
    setv('fx_g_dev_obs', 'Saco rasgado (sintético)'); salvar(); d2 = dlg(); c3 = cen(); devs = mv_dev(c3)
    print('V3 devoluções:', [(m.get('qtd'), m.get('apto')) for m in devs], '| REQ-031:', it31(c3), '| M26-07:', lote(c3, 'MAP 11-52|M26-07'), '| obs exigida:', d1 and d1['alertas'])
    chk('V3', 'devolução normal: 480 apta + 20 bloqueada (com observação) → custódia 0', d2 is None and [(m.get('qtd'), m.get('apto')) for m in devs] == [(480, True), (20, False)] and (it31(c3) or {}).get('custodia') == 0, [devs, it31(c3)])
    l0, l3 = lote(a0 or {}, 'MAP 11-52|M26-07'), lote(c3, 'MAP 11-52|M26-07')
    chk('V3', 'bloqueada sem observação é recusada e a de 20 kg vai para a quarentena do M26-07', bool(d1) and 'Descreva' in (d1['alertas'] or '') and l3 and l3['quarentena'] >= 20, [d1 and d1['alertas'], l0, l3])
    e = errs(); chk('V3', 'sem erro de script', not e, e)

    # ======================= V4 · teclado (Tab, Enter, Espaço) =======================
    limpar(); abrir(); J("document.activeElement&&document.activeElement.blur&&document.activeElement.blur();1")
    n = tab_ate("e.innerText&&e.innerText.trim()==='Receba devoluções'"); f = foco(); print('V4 Tab até a seção:', n, f)
    c.tecla(' ', 'Space', 32, text=' '); time.sleep(.6)
    n2 = tab_ate("(e.innerText||'').trim()==='Receber devolução da REQ-031'"); fg = foco(); print('V4 Tab até o gatilho:', n2, fg)
    chk('V4', 'gatilho "Receber devolução da REQ-031" alcançável por Tab, com foco visível', bool(n and n2) and fg.get('vis'), [n, n2, fg])
    c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.8); d = dlg(); fi = foco(); print('V4 Enter abriu:', bool(d), '| foco:', fi)
    chk('V4', 'Enter abre o diálogo e o foco entra nele', bool(d) and fi.get('noDlg'), fi)
    c.tecla('Escape', 'Escape', 27); time.sleep(.6); fv = foco(); print('V4 Esc:', dlg() is None, fv)
    chk('V4', 'Esc fecha sem mudança e o foco volta ao gatilho', dlg() is None and fv.get('txt') == 'Receber devolução da REQ-031', fv)
    if fv.get('txt') != 'Receber devolução da REQ-031':
        tab_ate("(e.innerText||'').trim()==='Receber devolução da REQ-031'")
    c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.8)
    k = tab_ate("(e.innerText||'').trim()==='Salvar'&&!!e.closest('aside[role=dialog]')", 30); fs = foco(); a = ls()
    c.tecla('Enter', 'Enter', 13, text='\r'); time.sleep(.7); d = dlg(); fe = foco()
    print('V4 Enter no Salvar vazio:', k, d and d['alertas'], '| foco:', fe)
    chk('V4', 'Salvar vazio pelo teclado é recusado, o foco fica no diálogo e o cenário não muda', bool(d) and 'quantidade' in d['alertas'].lower() and fe.get('noDlg') and ls() == a, [d and d['alertas'], fe])
    if d:
        kq = tab_ate("e.id==='fx_g_dev_qtd'", 30); vis_q = foco().get('vis')
        for ch in '480': c.tecla(ch, 'Digit' + ch, 48 + int(ch), text=ch)
        kc = tab_ate("e.id==='fx_g_dev_cond'", 5); vis_c = foco().get('vis')
        c.tecla('ArrowDown', 'ArrowDown', 40); time.sleep(.4); cv = J("document.activeElement.value")
        if cv not in CONDS: c.tecla('ArrowDown', 'ArrowDown', 40); time.sleep(.4); cv = J("document.activeElement.value")
        ks = tab_ate("(e.innerText||'').trim()==='Salvar'", 10); vis_s = foco().get('vis'); fq = J(f"(({DLG}).querySelector('#fx_g_dev_qtd')||{{}}).value")
        print('V4 campos:', dict(qtd=[kq, fq, vis_q], cond=[kc, cv, vis_c], salvar=[ks, vis_s]))
        c.tecla(' ', 'Space', 32, text=' '); time.sleep(.9); d = dlg(); c4 = cen(); devs = mv_dev(c4); ff = foco()
        print('V4 Espaço no Salvar:', 'aberto: ' + d['alertas'] if d else 'fechou', '| MV:', [(m.get('qtd'), m.get('apto')) for m in devs], '| REQ-031:', it31(c4), '| foco depois:', ff)
        chk('V4', 'só teclado: 480 digitado, Apta pela seta, Espaço no Salvar → MV 480 e custódia 20', d is None and [(m.get('qtd'), m.get('apto')) for m in devs] == [(480, True)] and (it31(c4) or {}).get('custodia') == 20, [d and d['alertas'], devs, it31(c4)])
        chk('V4', 'foco visível nos campos e no Salvar', bool(vis_q and vis_c and vis_s), [vis_q, vis_c, vis_s])
        chk('V4', 'depois de salvar o foco volta ao gatilho (ou à linha da REQ-031)', ff.get('txt') == 'Receber devolução da REQ-031' or 'REQ-031' in ff.get('txt', ''), ff)
    else:
        c4 = cen(); print('V4 Salvar vazio fechou o formulário: REQ-031', it31(c4), '| MV:', [(m.get('qtd'), m.get('apto')) for m in mv_dev(c4)])
        chk('V4', 'só teclado: 480 digitado, Apta pela seta, Espaço no Salvar → MV 480 e custódia 20', False, 'não aplicável: o Salvar vazio já gravou ' + str([(m.get('qtd'), m.get('apto')) for m in mv_dev(c4)]))
    e = errs(); chk('V4', 'sem erro de script', not e, e)

    # ======================= V5 · 390 px com toque =======================
    c.aparelho(390, 844, 2, True); limpar(); abrir()
    lado = J("({doc:document.documentElement.scrollWidth,body:document.body.scrollWidth,w:innerWidth})"); print('V5 largura:', lado)
    chk('V5', 'EST a 390 px sem rolagem horizontal da página', lado['doc'] <= lado['w'] + 1 and lado['body'] <= lado['w'] + 1, lado)
    rs = secao(3, toque=True); rg = abrir_dev31(toque=True); d = dlg()
    alvos = J(f"""(()=>{{const d={DLG}; const m=e=>{{if(!e) return null; const r=e.getBoundingClientRect(); return [Math.round(r.width),Math.round(r.height)];}};
      return {{qtd:m(d&&d.querySelector('#fx_g_dev_qtd')),cond:m(d&&d.querySelector('#fx_g_dev_cond')),salvar:m(d&&[...d.querySelectorAll('button')].find(b=>b.innerText.trim()==='Salvar')),
        cancelar:m(d&&[...d.querySelectorAll('button')].find(b=>b.innerText.trim()==='Cancelar')),fechar:m(d&&d.querySelector('button[aria-label=Fechar]'))}};}})()""")
    sec = rs and [round(rs[2]), round(rs[3])]; gat = rg and [round(rg[2]), round(rg[3])]; comp = secao.compacta and [round(secao.compacta[2]), round(secao.compacta[3])]
    print('V5 alvos (L×A):', dict(faixa=comp, secao=sec, gatilho=gat, **(alvos or {})), '| diálogo:', d and [d['L'], d['R'], d['W']])
    chk('V5', 'toque abre o diálogo dentro da janela', bool(d) and d['L'] >= -.5 and d['R'] <= d['W'] + .5, d and [d['L'], d['R'], d['W']])
    ok44 = lambda x: bool(x) and x[0] >= 44 and x[1] >= 44
    chk('V5', 'alvos tocados do diálogo ≥ 44 px: quantidade, condição, Salvar', all(ok44(alvos.get(k)) for k in ('qtd', 'cond', 'salvar')), alvos)
    chk('V5', 'alvos tocados da tela ≥ 44 px: faixa de seções, seção, gatilho', all(ok44(x) for x in (comp, sec, gat)), dict(faixa=comp, secao=sec, gatilho=gat))
    lado2 = J("({doc:document.documentElement.scrollWidth,w:innerWidth})")
    digitar('fx_g_dev_qtd', '480', toque=True); setv('fx_g_dev_cond', CONDS[0]); salvar(toque=True); d = dlg(); c5 = cen(); devs = mv_dev(c5)
    print('V5 toque 480 Apta:', 'aberto: ' + d['alertas'] if d else 'fechou', '| MV:', [(m.get('qtd'), m.get('apto')) for m in devs], '| REQ-031:', it31(c5), '| largura com diálogo:', lado2)
    chk('V5', 'toque: 480 + Apta grava MV 480 e custódia 20; sem rolagem lateral com o diálogo aberto', d is None and [(m.get('qtd'), m.get('apto')) for m in devs] == [(480, True)] and lado2['doc'] <= lado2['w'] + 1, [devs, lado2])
    c.shot(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v5_390_' + os.environ.get('ROTULO', 'x') + '.png')) if os.environ.get('ROTULO') else None
    secao(1, toque=True); clique(btn('Conferir NF 4533'), toque=True); d = dlg()
    print('V5 NF 4533 a 390:', d and [d['ped'], d['pedDis'], d['L'], d['R'], d['W']])
    chk('V5', 'NF 4533 a 390 px: pedido só leitura e diálogo dentro da janela', bool(d) and d['pedDis'] is True and d['R'] <= d['W'] + .5, d and [d['pedDis'], d['R'], d['W']])
    e = errs(); chk('V5', 'sem erro de script', not e, e)
    c.aparelho(1440, 900)

    # ======================= V7 · linha do BEN: ajuda com a sobra (A3) e recusa da aba velha (A5) =======================
    limpar(); abrir()
    fx = J("""(()=>{ const r=window.__cen.cenMudar(null,c=>{ const o=c.ordens['OB-0110'], it=c.reqs['REQ-030'].itens[0]; o.etapa='Em execução'; o.ben.ent=[{kg:7300}]; o.ben.sai=[];
      it.entregue=869; it.consumido=0; it.devolvido=0; it.custodia=869; return {msg:'fixture'}; }); return r.erro||'ok'; })()""")
    abrir(); secao(3); r7 = clique("[...document.querySelectorAll('[role=row]')].find(x=>/REQ-030/.test(x.innerText))")
    d = dlg(); ajuda = J(f"(({DLG})||document).querySelector('#fx_g_dev_qtd').closest('div').parentElement.innerText.replace(/\\s+/g,' ')") if d else ''
    print('V7 BEN abriu:', fx, d and {k: d[k] for k in ('qtd', 'cond')}, '| ajuda:', ajuda[:400])
    chk('V7', 'A3: linha do BEN abre com quantidade e condição vazias', bool(d) and d['qtd'] == '' and d['cond'] not in CONDS, d and [d['qtd'], d['cond']])
    chk('V7', 'A3: a ajuda do campo mostra a sobra calculada (139 = 869 − 730) e a parcela desta linha (139 un), sem presumir o recebido', '139 un = 869 un em custódia − 730 un' in ajuda and 'Sobra desta linha: 139 un' in ajuda and 'Informe a quantidade e a condição' in ajuda, ajuda[:400])
    if d:
        digitar('fx_g_dev_qtd', '139'); setv('fx_g_dev_cond', CONDS[0])
        J("window.__cen.cenMudar(null,c=>{ c.ordens['OB-0110'].ben.ent=[{kg:7200}]; return {msg:'outra aba'}; })"); a7 = ls()   # outra aba: a sobra passa a 149
        salvar(); d2 = dlg(); c7 = cen(); dv = mv_dev(c7, 'Caixa de mamão Formosa 10 kg')
        print('V7 aba velha:', d2 and d2['alertas'], '| campos:', d2 and [d2['qtd'], d2['cond']], '| MV:', [(m.get('qtd'), m.get('apto')) for m in dv])
        chk('V7', 'A5: a recusa da aba velha diz o que mudou e pede de novo quantidade e condição; campos limpos; nada gravado', bool(d2) and 'sobra 139 → 149 un' in d2['alertas'] and 'quantidade e a condição' in d2['alertas'] and d2['qtd'] == '' and d2['cond'] not in CONDS and not dv and ls() == a7, [d2 and d2['alertas'], d2 and [d2['qtd'], d2['cond']], dv])
        digitar('fx_g_dev_qtd', '149'); setv('fx_g_dev_cond', CONDS[0]); salvar(); d3 = dlg(); c8 = cen(); dv = mv_dev(c8, 'Caixa de mamão Formosa 10 kg')
        print('V7 149 aptas:', 'aberto: ' + d3['alertas'] if d3 else 'fechou', '| MV:', [(m.get('qtd'), m.get('apto')) for m in dv], '| custódia:', c8['reqs']['REQ-030']['itens'][0]['custodia'])
        chk('V7', 'conferindo 149 aptas, grava um MV de 149 e a custódia cai 869 → 720', d3 is None and [(m.get('qtd'), m.get('apto')) for m in dv] == [(149, True)] and c8['reqs']['REQ-030']['itens'][0]['custodia'] == 720, [d3 and d3['alertas'], dv])
    e = errs(); chk('V7', 'sem erro de script', not e, e)

    # ======================= V6 · cenário salvo pela base abre sem perda =======================
    if LEG:
        limpar('base'); abrir('base'); secao(3); abrir_dev31(); setv('fx_g_dev_qtd', '480')
        if J(f"!!({DLG}).querySelector('#fx_g_dev_cond')") and J(f"({DLG}).querySelector('#fx_g_dev_cond').value")not in CONDS: setv('fx_g_dev_cond', CONDS[0])
        salvar(); secao(1); clique(btn('Conferir NF 4533')); setv('fx_g_rec_ped', PED_CX); time.sleep(.3)
        setv('fx_g_rec_conf', '1000'); setv('fx_g_rec_apto', '1000'); setv('fx_g_rec_quar', '0'); setv('fx_g_rec_div', 'Falta'); setv('fx_g_rec_obs', 'Entrega parcial (sintético)'); salvar()
        S = ls(); cs = json.loads(S) if S else {}
        print('V6 base gravou:', len(cs.get('movs', [])), 'movimentos ·', [(m.get('id'), m.get('tipo'), m.get('qtd'), m.get('prod')) for m in cs.get('movs', [])][-4:], '| REQ-031:', it31(cs))
        abrir('novo'); S1 = ls(); vistos = []
        for i in range(1, 7): secao(i); vistos.append(J("document.querySelector('main').innerText.length"))
        c6 = cen(); e = errs()
        print('V6 PR abriu o cenário da base:', len((c6 or {}).get('movs', [])), 'movimentos | igual ao salvo:', S1 == S, ls() == S, '| seções:', vistos, '| erros:', e)
        chk('V6', 'cenário salvo pela base abre no PR sem perda (movimentos, requisições e lotes iguais) e sem erro', bool(cs.get('movs')) and c6 and c6['movs'] == cs['movs'] and c6['reqs'] == cs['reqs'] and c6['lotes'] == cs['lotes'] and not e, [len(cs.get('movs', [])), len((c6 or {}).get('movs', [])), e])
        secao(3); txt = J("[...document.querySelectorAll('[role=row]')].filter(r=>/REQ-031/.test(r.innerText)).map(r=>r.innerText.replace(/\\s+/g,' ')).join(' | ')")
        abrir_dev31(); d = dlg(); digitar('fx_g_dev_qtd', '20'); setv('fx_g_dev_cond', CONDS[0]); salvar(); d2 = dlg(); c7 = cen()
        print('V6 continua no PR:', txt, '| após 20 apta:', it31(c7), len(c7['movs']), '| aberto:', d2 and d2['alertas'])
        chk('V6', 'no PR, a devolução dos 20 kg restantes do cenário da base grava sobre ele (prefixo preservado, custódia 0)', d2 is None and c7['movs'][:len(cs['movs'])] == cs['movs'] and len(c7['movs']) == len(cs['movs']) + 1 and it31(c7)['custodia'] == 0, [d2 and d2['alertas'], it31(c7)])
    else: nota('V6 sem LEGADO_DIR: não aplicável nesta execução')
finally:
    c.close(); SRV.terminate(); shutil.rmtree(RAIZ, ignore_errors=True)
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)}' + (' · FALHAS: ' + ' ; '.join(FAIL) if FAIL else ''))
sys.exit(0 if not FAIL else 1)
