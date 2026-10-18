# -*- coding: utf-8 -*-
"""C-3/C-4 no navegador (PR #114, revisão do Claude; roteiro em c34_revisao.md): Compras aprovada pela tela → recebimento parcial por linha no
Estoque → de volta à linha em Compras (etapa 6: Recebido, Em quarentena (agora), A entregar por linha) → laudo libera a quarentena →
recarregar mantém → falha de gravação (cota) não grava nada e a repetição grava uma vez → teclado e celular (390 px).
A compra da Safra 2026/27 anda pela própria tela (convites simulados, Enviar à Direção, Registrar aprovação da Direção), sem gravação direta.
No Estoque, as duas notas da demonstração (NF 4533 e NF 7731) são conferidas antes, porque "Registrar recebimento" só aparece sem nota pendente.
Uso: python3 c34_fluxo_test.py   (≈ 90 s; Chrome em CHROME_BIN; capturas q_c34_*.png em _probe/)"""
import sys, os, time, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from cdp import Chrome
from journeys import free
from comp_lib import IR_ETAPA
R = os.path.join(HERE, '_render'); OUT = os.path.join(HERE, '_probe'); os.makedirs(OUT, exist_ok=True)
p = free(); srv = subprocess.Popen(['python3', '-m', 'http.server', str(p), '--bind', '127.0.0.1', '--directory', R], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
c = Chrome(port=free()); J = c.js; B = f'http://127.0.0.1:{p}/'
c.call('Page.addScriptToEvaluateOnNewDocument', {'source': "window.__g2cvTodasSempre=true;window.__err=[];addEventListener('error',e=>window.__err.push(String(e.message)));addEventListener('unhandledrejection',e=>window.__err.push(String(e.reason)));"})
OK, FAIL, ERR = [], [], []
def chk(nome, cond, det=''):
    (OK if cond else FAIL).append(nome); print(('OK    · ' if cond else 'FALHA · ') + nome + ('' if cond else f' · {str(det)[:500]}'), flush=True)
def col():
    try: ERR.extend(J("location.href==='about:blank'?[]:(window.__err||[])") or [])
    except Exception as e: ERR.append('coleta: ' + str(e))
def ir(f, w=1.5): col(); c.goto('about:blank', wait=.1); c.goto(B + f, wait=w)
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
def clk(t, root=None, w=.5):
    r = J(f"""(()=>{{const n={N}; const R=({json.dumps(root)}?document.querySelector({json.dumps(root)}):document); if(!R) return 'SEM RAIZ';
      const b=[...R.querySelectorAll('button,a,[role=menuitem]')].find(x=>(x.offsetParent||x.getAttribute('role')==='menuitem')&&n(x.innerText)==={json.dumps(t)}); if(!b) return 'SEM '+{json.dumps(t)}; b.click(); return 'ok';}})()"""); time.sleep(w); return r
def setv(i, val):
    r = J(f"""(()=>{{const i=document.querySelector('#{i}'); if(!i) return 'sem campo {i}'; const P=i.tagName==='SELECT'?HTMLSelectElement.prototype:(i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype);
      Object.getOwnPropertyDescriptor(P,'value').set.call(i,{json.dumps(val)}); i.dispatchEvent(new Event('input',{{bubbles:true}})); i.dispatchEvent(new Event('change',{{bubbles:true}})); return i.value;}})()"""); time.sleep(.2); return r
toast = lambda: J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')") or ''
aside = lambda: J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText.replace(/\\s+/g,' ')") or ''
alerta = lambda: J("[...document.querySelectorAll('aside[role=dialog] [role=alert]')].map(x=>x.innerText).join(' | ')") or ''
cen = lambda expr: J(f"(()=>{{const c=window.__cen.cenGet(); return ({expr});}})()")
def etapa(i): J(f"({IR_ETAPA})({i})"); time.sleep(.6)
def expandir(): J("[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&b.innerText.trim()==='Expandir tudo').forEach(b=>b.click())"); time.sleep(.5)
def cel(linha, coluna):
    """Valor da coluna (pelo cabeçalho) na linha visível cuja 1ª célula começa com linha (grade visível da etapa)."""
    return J(f"""(()=>{{const n={N}; const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&[...t.querySelectorAll('[role=columnheader]')].some(h=>/A ENTREGAR/i.test(h.innerText)));
      if(!t) return 'sem grade'; const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>n(h.innerText.replace(/[⇅▾▴]/g,'')).toUpperCase()); const i=hs.indexOf({json.dumps(coluna.upper())});
      const r=[...t.querySelectorAll('[role=row]')].filter(x=>x.offsetParent).find(x=>{{const cs=x.querySelectorAll('[role=cell]'); return cs[0]&&n(cs[0].innerText).startsWith({json.dumps(linha)});}});
      if(!r) return 'sem linha'; const cs=[...r.querySelectorAll('[role=cell]')]; return cs[i]?n(cs[i].innerText):'sem coluna';}})()""") or ''
def linha6(item): return [cel(item, k) for k in ('Pedido', 'Recebido', 'Em quarentena (agora)', 'A entregar')]
def cmp6(): ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627', w=1.8); etapa(6); expandir()
MAP = 'PC-101 · Fertisul · MAP 11-52 · kg · linha 1'
NPK = 'PC-101 · Fertisul · NPK 20-05-20 · kg · linha 4'
def receber(ped, nf, qnf, conf, apto, quar, lote, obs=''):
    r0 = clk('Registrar recebimento'); vals = [setv('fx_g_rec_ped', ped), setv('fx_g_rec_nf', nf), setv('fx_g_rec_qtd_nf', qnf), setv('fx_g_rec_conf', conf),
            setv('fx_g_rec_apto', apto), setv('fx_g_rec_quar', quar), setv('fx_g_rec_lote', lote), setv('fx_g_rec_local', 'Galpão 1'), setv('fx_g_rec_obs', obs)]
    return r0, vals
def recs(): return cen("(c.movs||[]).filter(m=>m.tipo==='recebimento-nf'&&m.estRec&&/^PC-101/.test(String(m.estRec.pedido||m.estRec.ped||''))).map(m=>[m.estRec.nf,m.estRec.item,m.estRec.linha,m.estRec.apto,m.estRec.quar])") or []
try:
    c.size(1440, 1000); ir('CMP.dc.html'); J("localStorage.clear()")
    # ---------------- 1 · Compras: a Safra 2026/27 anda até a aprovação pela tela ----------------
    ir('CMP.dc.html#sol=SOL-2026-07&saf=S2627', w=1.8); etapa(3); r = clk('Enviar convites (simulado)'); time.sleep(5)
    etapa(5); r1 = clk('Enviar à Direção'); r2 = clk('Registrar aprovação da Direção'); t = toast()
    leg = J("localStorage.getItem('talhao-os-compras-v1')")
    # ---------------- 2 · Estoque: pedidos por linha e recebimento parcial ----------------
    ir('EST.dc.html', w=1.8)   # o Estoque expõe o cenário (window.__cen); a Compra não
    st = cen("[c.compras&&c.compras.v,c.compras&&c.compras.proc.S2627&&c.compras.proc.S2627.aprov.estado,(c.compras.proc.S2627.aprov.pcs||[]).map(p=>p.id)]")
    chk('C1 Compras pela tela: convites → Enviar à Direção → Registrar aprovação da Direção emite PC-101 a PC-104 e grava no cenário (compras.v1, aprovada)',
        (r, r1, r2) == ('ok', 'ok', 'ok') and 'emitidos PC-101 a PC-104' in t and st == [1, 'aprovada', ['PC-101', 'PC-102', 'PC-103', 'PC-104']], (r, r1, r2, t, st))
    chk('C2 a compra aprovada não volta para a chave antiga de Compras (fonte única: cenário)', leg is None, leg)
    # o Planejar safra lê o andamento da Compra no cenário: "Pedidos emitidos" impede a redução de insumo já comprado (DEM-09)
    ir('SAF.dc.html#saf=S2627&passo=demanda', w=1.8); k6 = J("(document.body.innerText.match(/Valor da necessidade[^\\n]+/)||[''])[0]") or ''
    chk('C16 Planejar safra (demanda de insumos da 2026/27) mostra a compra no estado gravado pela Compra: Pedidos emitidos · PC-101 a PC-104',
        'Pedidos emitidos' in k6 and 'PC-101' in k6, k6)
    ir('EST.dc.html', w=1.8)
    clk('Conferir NF 4533'); setv('fx_g_rec_conf', '20000'); setv('fx_g_rec_apto', '20000'); setv('fx_g_rec_quar', '0'); setv('fx_g_rec_val', '05/2027'); clk('Salvar', 'aside[role=dialog]')
    clk('Conferir NF 7731'); setv('fx_g_rec_conf', '1200'); setv('fx_g_rec_apto', '1200'); setv('fx_g_rec_quar', '0'); clk('Salvar', 'aside[role=dialog]')
    clk('Registrar recebimento'); ops = J("[...(document.querySelector('#fx_g_rec_ped')||{options:[]}).options].map(o=>o.value)") or []
    chk('C3 EST: o pedido aprovado aparece por linha (PC-101 MAP linha 1, NPK linha 4; PC-104 com 5 linhas), sem perder os pedidos anteriores',
        MAP in ops and NPK in ops and sum(1 for o in ops if o.startswith('PC-104 · ')) == 5 and any(o.startswith('PC-088') for o in ops), ops)
    clk('Cancelar', 'aside[role=dialog]')
    # falha de gravação (cota): nada gravado, formulário mantido; liberado o armazenamento, a repetição grava uma vez
    receber(MAP, 'NF 9101', '30000', '30000', '25000', '5000', 'M26-01', 'Laudo de garantia pendente')
    J("window.__setItem0=Storage.prototype.setItem; Storage.prototype.setItem=function(){ throw new DOMException('cota','QuotaExceededError'); }")
    clk('Salvar', 'aside[role=dialog]'); tq = toast() + ' ' + alerta(); n0 = len(recs()); aberto = bool(J("!!document.querySelector('aside[role=dialog]')")); v0 = J("(document.querySelector('#fx_g_rec_apto')||{}).value")
    J("Storage.prototype.setItem=window.__setItem0")
    chk('C4 cota esgotada ao gravar a nota: aviso de que nada foi gravado, nenhum recebimento no cenário e o formulário segue aberto com os valores',
        n0 == 0 and aberto and v0 == '25000' and ('gravar' in tq.lower() or 'armazen' in tq.lower()), (tq, n0, aberto, v0))
    s = clk('Salvar', 'aside[role=dialog]'); t = toast(); rr = recs()
    chk('C5 repetição depois de liberar o armazenamento: NF 9101 grava uma vez a linha 1 (25.000 kg aptos + 5.000 kg em quarentena)',
        s == 'ok' and rr == [['NF 9101', 'MAP 11-52', 1, 25000, 5000]], (s, t, rr))
    # mesma nota, outra linha do mesmo pedido (nota com vários itens)
    receber(NPK, 'NF 9101', '4000', '4000', '4000', '0', 'N26-07'); clk('Salvar', 'aside[role=dialog]'); t2 = toast() + ' ' + alerta(); rr2 = recs()
    chk('C6 a mesma NF 9101 traz outra linha do PC-101 (NPK, linha 4): grava a linha 4 sem confundir com a linha 1',
        len(rr2) == 2 and ['NF 9101', 'NPK 20-05-20', 4, 4000, 0] in rr2, (t2, rr2))
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); if(b) b.click();})()"); time.sleep(.3)
    receber(MAP, 'NF 9101', '1000', '1000', '1000', '0', 'M26-02'); clk('Salvar', 'aside[role=dialog]'); t2c = toast() + ' ' + alerta(); rr2c = recs()
    chk('C6c a mesma NF 9101 de novo na linha 1 do PC-101 é recusada como documento duplicado e nada é gravado',
        'já foi lançada nesta linha do PC-101' in t2c and rr2c == rr2, (t2c, rr2c))
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); if(b) b.click();})()"); time.sleep(.3)
    if len(rr2) < 2:   # a linha 4 chega em nota própria (segunda entrega do fornecedor): o resto do roteiro segue medindo por linha
        receber(NPK, 'NF 9102', '4000', '4000', '4000', '0', 'N26-07'); clk('Salvar', 'aside[role=dialog]'); t2b = toast(); rr2 = recs()
        chk('C6b a linha 4 do PC-101 em nota própria (NF 9102) grava só a linha 4', ['NF 9102', 'NPK 20-05-20', 4, 4000, 0] in rr2 and len(rr2) == 2, (t2b, rr2))
        J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); if(b) b.click();})()"); time.sleep(.3)
    # outra nota com o mesmo número em outro pedido continua recusada (identidade da NF)
    F103 = next((o for o in ops if o.startswith('PC-103 · ') and ' · Fungicida C · ' in o), 'sem PC-103')
    receber(F103, 'NF 9101', '10', '10', '10', '0', 'FC-1'); setv('fx_g_rec_val', '06/2027'); clk('Salvar', 'aside[role=dialog]'); t3 = toast() + ' ' + alerta(); rr3 = len(recs())
    chk('C7 NF 9101 já vinculada ao PC-101 é recusada no PC-103 e nada é gravado', 'já está vinculada ao PC-101' in t3 and rr3 == len(rr2), (t3, rr3))
    J("(()=>{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); if(b) b.click();})()"); time.sleep(.3)
    k = J("document.querySelector('main').innerText.replace(/\\s+/g,' ')") or ''
    chk('C8 faixa do Estoque: saldo a entregar por linha (MAP 79.500 → 49.500 kg; NPK 14.800 → 10.800 kg)', 'PC-101 49.500 kg' in k and 'PC-101 10.800 kg' in k and 'PC-101 79.500 kg' not in k, k[:900])
    c.shot(os.path.join(OUT, 'q_c34_est.png'))
    # ---------------- 3 · de volta à linha em Compras ----------------
    cmp6(); m1, n1, x1 = linha6('MAP 11-52'), linha6('NPK 20-05-20'), linha6('Nitrato de potássio')
    chk('C9 Compras etapa 6, linha MAP: pedido 79.500 · recebido 30.000 · em quarentena agora 5.000 · a entregar 49.500 kg', m1 == ['79.500 kg', '30.000 kg', '5.000 kg', '49.500 kg'], m1)
    chk('C10 linha NPK: 14.800 · 4.000 · 0 · 10.800 kg; linha sem nota (Nitrato de potássio) intacta: 870 · 0 · 0 · 870 kg',
        n1 == ['14.800 kg', '4.000 kg', '0 kg', '10.800 kg'] and x1 == ['870 kg', '0 kg', '0 kg', '870 kg'], (n1, x1))
    c.shot(os.path.join(OUT, 'q_c34_cmp6.png'))
    # ---------------- 4 · laudo libera a quarentena; Compras mostra a quarentena de agora ----------------
    ir('EST.dc.html', w=1.8); J("document.querySelectorAll('nav[aria-label=\"Seções do estoque\"] button')[3].click()"); time.sleep(.5)
    expandir(); rb = J("""(()=>{const r=[...document.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('M26-01')>=0); if(!r) return 'sem linha'; const b=[...r.querySelectorAll('button')].find(b=>b.textContent.trim().startsWith('Liberar após inspeção')); if(!b) return 'sem botão'; b.click(); return 'ok';})()"""); time.sleep(.5)
    setv('est-laudo', 'INSP-0911'); lb = clk('Liberar com o laudo'); t4 = toast()
    cmp6(); m2 = linha6('MAP 11-52')
    chk('C11 laudo INSP-0911 libera o lote M26-01: na Compra a linha MAP fica 30.000 recebido · 0 em quarentena agora · 49.500 a entregar (recebido não muda)',
        rb == 'ok' and lb == 'ok' and m2 == ['79.500 kg', '30.000 kg', '0 kg', '49.500 kg'], (rb, lb, t4, m2))
    # ---------------- 5 · recarregar mantém ----------------
    J("location.reload()"); time.sleep(2.0); etapa(6); expandir(); m3, n3 = linha6('MAP 11-52'), linha6('NPK 20-05-20')
    chk('C12 recarregar a Compra mantém as linhas (MAP 30.000/0/49.500; NPK 4.000/0/10.800)', m3 == m2 and n3 == n1, (m3, n3))
    # ---------------- 6 · teclado e celular ----------------
    foco = J("""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&/A ENTREGAR/i.test(t.innerText)); const r=[...t.querySelectorAll('[role=row]')].find(r=>r.innerText.indexOf('PC-101')>=0&&r.innerText.indexOf('3 insumos')>=0);
      const b=r&&[...r.querySelectorAll('button,[tabindex]')].find(x=>x.tabIndex>=0); if(!b) return 'sem foco'; b.focus(); return document.activeElement===b?(b.getAttribute('aria-expanded')||b.innerText.trim().slice(0,20)||'ok'):'não focou';})()""")
    chk('C13 teclado: o pedido PC-101 (3 insumos) tem controle focável na própria linha', foco not in ('sem foco', 'não focou', None), foco)
    c.size(390, 844); cmp6(); c.shot(os.path.join(OUT, 'q_c34_cmp6_390.png'))
    pg = J("[document.documentElement.scrollWidth, innerWidth]"); m4 = linha6('MAP 11-52')
    vis = J("""(()=>{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&/A ENTREGAR/i.test(t.innerText)); const box=t.parentElement; const h=[...t.querySelectorAll('[role=columnheader]')].find(h=>/A ENTREGAR/i.test(h.innerText));
      h.scrollIntoView({block:'nearest',inline:'nearest'}); const R=box.getBoundingClientRect(), H=h.getBoundingClientRect(); return H.width>0&&H.left>=R.left-0.5&&H.right<=R.right+0.5;})()""")
    chk('C14 celular 390 px: a página não rola na horizontal; a coluna A entregar é alcançável na grade e a linha MAP traz os mesmos números',
        pg[0] <= pg[1] + 1 and vis is True and m4 == m2, (pg, vis, m4))
    c.size(1440, 1000)
    col()
    chk('C15 nenhum erro de JavaScript nas páginas visitadas', not ERR, ERR[:5])
finally:
    try: c.close()
    except Exception: pass
    srv.terminate()
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas' + (' · ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
