# -*- coding: utf-8 -*-
"""Planejar safra, etapa 3 (Operações e recursos): linha Total com Área trabalhada, Custo R$/ha e a coluna nova Custo total
(pedido do proprietário, 13/10/2026: "no totais, some também as colunas de hectares e custo/ha e custo total (adicione essa coluna)").
Oráculo independente, em Decimal, das ocorrências da tela (window.__safSelf.__e3.oc):
  ha-op = Σ área das ocorrências; custo = Σ custo (máquinas e pessoas) = o "Custo de operação" do topo;
  R$/ha = custo ÷ hectares físicos (cada talhão uma vez, a conta do Resumo da safra). Somar os R$/ha das linhas daria outro número
  (operações sobre áreas diferentes): T4 mede essa diferença como contraprova.
Também: o Total segue o filtro rápido; ocorrência pendente vira "parcial" no R$/ha (contraprova direta no serviço); a célula do Total
não corta texto em 1440 e 1024.
T11–T13 (revisão Codex V58-TOTAL-FILTRO-01, S2): com a busca "T1-A ·" o Total soma só as ocorrências do T1-A (oráculo em Decimal; antes somava a
operação inteira: 5.074 ha-op e R$ 232.667,03 contra 1.280 ha-op e R$ 60.336,29); recolher e expandir não mudam o Total; limpar a busca
devolve o Total cheio. Uso: python3 saf_totais_test.py (lê _render ou RENDER_DIR)."""
import sys, os, json, re, time
from decimal import Decimal as D
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, cv_todas_sempre
import saf_nav_lib as L
from saf_nav_lib import chk, info, abre, OK, FAIL

GRADE = r"""(()=>{ const n=s=>(s||'').replace(/\s+/g,' ').trim(); const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&/HORAS-CONJUNTO/i.test(t.innerText));
  if(!t) return null; const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>n(h.innerText).replace(/[⇅▾▴▲▼]/g,'').trim().toUpperCase());
  const lin=[...t.querySelectorAll('[role=row]')].slice(1).filter(r=>!r.classList.contains('g2tot')).map(r=>({id:r.getAttribute('data-rid')||'',c:[...r.querySelectorAll('[role=cell]')].map(c=>n(c.innerText).replace(/^[▾▸] ?/,''))}));
  const tr=t.querySelector('.g2tot'); const tot=tr?[...tr.querySelectorAll('[role=cell]')].map(c=>({t:n(c.innerText),corta:c.scrollWidth>c.clientWidth+1})):[];
  let sc=t; while(sc&&sc!==document.body&&!/(auto|scroll)/.test(getComputedStyle(sc).overflowX)) sc=sc.parentElement;
  return JSON.stringify({hs,lin,tot,sw:sc?sc.scrollWidth:0,cw:sc?sc.clientWidth:0}); })()"""
OC = "JSON.stringify(window.__safSelf.__e3.oc.map(i=>({oid:'oc:'+i.c.id+'|'+i.a.id+'|'+i.dt,atv:i.a.nome,c:i.c.id,local:i.c.v.local,op:i.a.op,area:String(i.area),cop:String(Number(i.cop)||0),pend:!!i.pend,ok:!!i.rp.custoOk})))"
TOPO = r"(document.body.innerText.match(/Custo de operação\s+(R\$\s?[\d.,]+)/)||['',''])[1]"


def num(t):   # "R$ 1.234,56/ha" · "1.234 ha-op" · "880,7 h" → Decimal
    m = re.search(r'-?[\d.]+(,\d+)?', (t or '').replace(' ', ' '))
    return D(m.group(0).replace('.', '').replace(',', '.')) if m else None


def grade():
    g = json.loads(L.c.js(GRADE) or 'null') or {}
    hs = g.get('hs', []); ix = {h: i for i, h in enumerate(hs)}
    return g, ix


try:
    L.c = Chrome(); cv_todas_sempre(L.c); abre('#saf=S2627&passo=operacoes'); time.sleep(.6)
    g, ix = grade(); oc = json.loads(L.c.js(OC) or '[]')
    chk('T0 a grade da etapa 3 abriu, com ocorrências', bool(g) and len(oc) > 0, [bool(g), len(oc)])
    chk('T1 coluna nova "Custo total" ao lado do Custo R$/ha', 'CUSTO TOTAL' in ix and ix.get('CUSTO TOTAL') == ix.get('CUSTO R$/HA', -9) + 1, g.get('hs'))
    # oráculo
    cop = sum((D(i['cop']) for i in oc), D(0)); haop = sum((D(i['area']) for i in oc), D(0))
    vis = {}
    for i in oc: vis.setdefault(i['c'], D(i['area']))
    afis = sum(vis.values(), D(0)); rha = cop / afis
    parcial = any(i['pend'] or not i['ok'] for i in oc)
    info('oráculo', f'custo {cop:.2f} · {haop} ha-op · {afis} ha físicos · R$/ha {rha:.4f} · parcial={parcial}')
    tot = [x['t'] for x in g.get('tot', [])]
    T = lambda k: tot[ix[k]] if k in ix and ix[k] < len(tot) else ''
    chk('T2 Total da Área trabalhada = Σ ha-op das ocorrências, com a unidade', T('ÁREA TRABALHADA').endswith('ha-op') and num(T('ÁREA TRABALHADA')) == haop, [T('ÁREA TRABALHADA'), haop])
    topo = L.c.js(TOPO) or ''
    chk('T3 Total do Custo total = Σ custo das ocorrências = "Custo de operação" do topo', abs(num(T('CUSTO TOTAL')) - cop) <= D('0.005') and T('CUSTO TOTAL') == topo, [T('CUSTO TOTAL'), topo, cop])
    soma_linhas = sum((num(l['c'][ix['CUSTO R$/HA']]) or D(0) for l in g['lin'] if l['id'].startswith('op:')), D(0))
    chk('T4 Total do R$/ha = custo ÷ hectares físicos (Resumo da safra), não a soma dos R$/ha das linhas',
        (T('CUSTO R$/HA') == 'parcial') if parcial else (T('CUSTO R$/HA').endswith('/ha') and abs(num(T('CUSTO R$/HA')) - rha) <= D('0.005') and abs(soma_linhas - rha) > D('0.01')),
        [T('CUSTO R$/HA'), f'{rha:.2f}', f'soma das linhas {soma_linhas}'])
    # custo de cada operação (1º nível) = Σ das suas ocorrências
    ruins = []
    for l in g['lin']:
        if not l['id'].startswith('op:'): continue
        op = l['id'][3:]; esp = sum((D(i['cop']) for i in oc if i['op'] == op), D(0)); vis_ = num(l['c'][ix['CUSTO TOTAL']])
        if vis_ is None or abs(vis_ - esp) > D('0.005'): ruins.append([op, l['c'][ix['CUSTO TOTAL']], str(esp)])
    chk('T5 Custo total de cada operação = Σ custo das suas ocorrências (oráculo)', not ruins and any(l['id'].startswith('op:') for l in g['lin']), ruins[:3])
    kh = next((h for h in ix if h.startswith('HORAS-CONJUNTO')), '')
    soma_h = sum((num(l['c'][ix[kh]]) or D(0) for l in g['lin'] if l['id'].startswith('op:')), D(0)) if kh else None
    chk('T6 Horas-conjunto do Total continua a soma das operações', bool(kh) and soma_h is not None and abs(num(T(kh)) - soma_h) <= D('0.1'), [kh, T(kh), soma_h, g.get('hs')])
    # contraprova do "parcial": no serviço do Total, uma ocorrência pendente troca o R$/ha por "parcial" (como no Resumo da safra)
    r = json.loads(L.c.js("""(()=>{ const s=window.__safSelf, oc=s.__e3.oc, f=s.__opTot; const rs=[...new Set(oc.map(i=>'op:'+i.a.op))].map(id=>({id}));
        const i=oc.find(x=>!x.pend); const a=f({k:'rha'},rs); i.pend=true; const b=f({k:'rha'},rs); i.pend=false; const c2=f({k:'rha'},rs); return JSON.stringify([a,b,c2]); })()""") or '[]')
    chk('T7 contraprova: com uma ocorrência pendente o R$/ha do Total vira "parcial"; sem ela, volta o valor', len(r) == 3 and r[1] == 'parcial' and r[0] == r[2] and r[0] != 'parcial', r)
    # o Total segue o filtro da grade (busca "Colheita": só as operações de colheita ficam no 1º nível)
    L.c.js("""(()=>{ const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&/HORAS-CONJUNTO/i.test(t.innerText)); let r=t; while(r&&!r.querySelector('input[placeholder^="Buscar"]')) r=r.parentElement;
      const e=r&&r.querySelector('input[placeholder^="Buscar"]'); if(!e) return; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,'Colheita'); e.dispatchEvent(new Event('input',{bubbles:true})); })()"""); time.sleep(.8)
    g2, ix2 = grade(); tot2 = [x['t'] for x in g2.get('tot', [])]
    ops = [l['id'][3:] for l in g2.get('lin', []) if l['id'].startswith('op:')]
    # oráculo do recorte (revisão Codex V58-TOTAL-FILTRO-01): com tudo expandido, a ocorrência visível entra; a atividade ou a operação visível
    # sem nada visível abaixo dela (casou por si, ex.: o nome "Colheita") entra inteira. Antes o T8 somava a operação inteira de tudo o que
    # aparecia (inclusive "Adubação a lanço", que aparece por uma linha interna) — o mesmo erro do Total.
    L.c.js("(()=>{ const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Expandir tudo'&&b.offsetParent); if(b) b.click(); })()"); time.sleep(.6)
    gx, _ = grade(); rids = [l['id'] for l in gx.get('lin', [])]
    sel2 = {}
    for r in rids:
        if r.startswith('oc:'):
            for i in oc:
                if i['oid'] == r: sel2[i['oid']] = i
        elif r.startswith('at:') and not any(q.startswith('oc:') and any(i['oid'] == q and 'at:' + i['op'] + '|' + i['atv'] == r for i in oc) for q in rids):
            for i in oc:
                if 'at:' + i['op'] + '|' + i['atv'] == r: sel2[i['oid']] = i
        elif r.startswith('op:') and not any(q.startswith('at:' + r[3:] + '|') for q in rids):
            for i in oc:
                if i['op'] == r[3:]: sel2[i['oid']] = i
    L.c.js("(()=>{ const b=[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Recolher tudo'&&b.offsetParent); if(b) b.click(); })()"); time.sleep(.5)
    s2 = list(sel2.values()); esp2 = sum((D(i['cop']) for i in s2), D(0)); ha2 = sum((D(i['area']) for i in s2), D(0))
    v2 = {}
    for i in s2: v2.setdefault(i['c'], D(i['area']))
    rha2 = esp2 / sum(v2.values(), D(0)) if v2 else None
    chk('T8 com a busca "Colheita", o Total soma só o recorte (operações de colheita inteiras; das demais, só o que casa), custo, ha-op e R$/ha pela área dele',
        0 < len(ops) < len({i['op'] for i in oc}) and {'Colheita de grãos', 'Colheita de café'} <= set(ops) and abs(num(tot2[ix2['CUSTO TOTAL']]) - esp2) <= D('0.005')
        and num(tot2[ix2['ÁREA TRABALHADA']]) == ha2 and rha2 is not None and abs(num(tot2[ix2['CUSTO R$/HA']]) - rha2) <= D('0.005'),
        [ops, tot2, str(esp2), str(ha2), str(rha2), len(s2)])
    # T11–T13 · busca que alcança as folhas (ocorrências do T1-A): o Total soma só elas
    BUSCA = """(q=>{ const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&/HORAS-CONJUNTO/i.test(t.innerText)); let r=t; while(r&&!r.querySelector('input[placeholder^="Buscar"]')) r=r.parentElement;
      const e=r&&r.querySelector('input[placeholder^="Buscar"]'); if(!e) return; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,q); e.dispatchEvent(new Event('input',{bubbles:true})); })"""
    L.c.js(BUSCA + "('T1-A ·')"); time.sleep(.8)
    g3, ix3 = grade(); tot3 = [x['t'] for x in g3.get('tot', [])]
    sel = [i for i in oc if i['local'] == 'T1-A']; esp3 = sum((D(i['cop']) for i in sel), D(0)); ha3 = sum((D(i['area']) for i in sel), D(0))
    vis3 = {}
    for i in sel: vis3.setdefault(i['c'], D(i['area']))
    par3 = any(i['pend'] or not i['ok'] for i in sel); rha3 = esp3 / sum(vis3.values(), D(0)) if vis3 else None
    ok3 = bool(sel) and num(tot3[ix3['ÁREA TRABALHADA']]) == ha3 and abs(num(tot3[ix3['CUSTO TOTAL']]) - esp3) <= D('0.005') and (
        tot3[ix3['CUSTO R$/HA']] == 'parcial' if par3 else abs(num(tot3[ix3['CUSTO R$/HA']]) - rha3) <= D('0.005'))
    chk('T11 busca "T1-A ·": o Total soma só as ocorrências do T1-A (ha-op, custo e R$/ha pela área física delas; oráculo em Decimal)', ok3,
        [tot3, f'esperado {ha3} ha-op · R$ {esp3:.2f} · R$/ha {rha3}', len(sel)])
    L.c.js("(()=>{ const b=[...document.querySelectorAll('button')].find(b=>/^(Recolher tudo|Expandir tudo)$/.test(b.innerText.trim())&&b.offsetParent); if(b) b.click(); })()"); time.sleep(.5)
    g4, ix4 = grade(); tot4 = [x['t'] for x in g4.get('tot', [])]
    L.c.js("(()=>{ const b=[...document.querySelectorAll('button')].find(b=>/^(Recolher tudo|Expandir tudo)$/.test(b.innerText.trim())&&b.offsetParent); if(b) b.click(); })()"); time.sleep(.5)
    g5, ix5 = grade(); tot5 = [x['t'] for x in g5.get('tot', [])]
    chk('T12 recolher e expandir não mudam o Total do recorte (sem somar pai e filho)', tot4 == tot3 and tot5 == tot3, [tot3, tot4, tot5])
    L.c.js(BUSCA + "('')"); time.sleep(.8)
    g6, ix6 = grade(); tot6 = [x['t'] for x in g6.get('tot', [])]
    chk('T13 limpar a busca devolve o Total cheio (= Σ de todas as ocorrências)', num(tot6[ix6['ÁREA TRABALHADA']]) == haop and abs(num(tot6[ix6['CUSTO TOTAL']]) - cop) <= D('0.005'), [tot6, haop, cop])
    # nenhuma célula do Total corta texto, em 1440 e 1024
    cortes = []
    for w, h in ((1440, 900), (1024, 640)):
        abre('#saf=S2627&passo=operacoes', w, h); time.sleep(.5); gg, _ = grade()
        cortes += [(w, x['t']) for x in gg.get('tot', []) if x['corta']]
        info(f'largura da grade em {w}', f"{gg.get('sw')} de {gg.get('cw')} px visíveis")
    chk('T9 nenhuma célula do Total corta o texto (1440 e 1024)', not cortes, cortes)
    chk('T10 sem erro de JS', not L.erros(), L.erros())
finally:
    try: L.c.close()
    except Exception: pass
    try: L.srv.terminate()
    except Exception: pass
print(f'RESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
sys.exit(1 if FAIL else 0)
