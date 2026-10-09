# -*- coding: utf-8 -*-
"""Teste de navegador · SAF-C02 (Codex, 09/10/2026): capacidade simétrica entre safras abertas da mesma fazenda.
Pela tela, no MESMO estado: Planejar safra → Editar a Safra 2026/27 e a Safrinha 2027 para o mesmo período (01/09/2026 a 12/07/2027).
A colheita da Safrinha em 14 e 15/07 (P1 e T2) fica depois do fim; em jul/27 a S2627 tem a poda do C1 (04/07). Abre a S2627 na etapa 3
(Continuar → Dimensionar operações ›), depois a S27SF (Trocar safra → Continuar → ‹ Operações e recursos) e confere que a ocupação de
jul/27 dos recursos compartilhados (Tratores e Operadores e equipe) é a mesma nas duas vistas e igual ao espelho dados2.capacidade com o
mesmo período, que a carga de fora aparece identificada (veredito, linha do filtro e aria-label da célula), que outra fazenda (LG2627) e
safra encerrada (S2526) não entram e que o custo de operação da S27SF conserva as colheitas fora da conta. Antes da correção, com a S2627
aberta, jul/27 somava a colheita de fora (Tratores 140,3 h contra 61,7 h com a S27SF aberta).
1440 × 900 e 390 × 844 (toque). Emulação no Chrome headless: não é aparelho físico. Uso: python3 saf_capacidade_simetrica_test.py"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome
import dados2 as D2
import saf_nav_lib as L
from saf_nav_lib import chk, OK, FAIL, abre, botao, fset, salvar, toast, painel, erros, PROBE
N = "(s=>(s||'').replace(/\\s+/g,' ').trim())"
INI, FIM = '2026-09-01', '2027-07-12'
def h1(x): return f'{x:,.1f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
def rs(x): return 'R$ ' + f'{x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
def na_saf(sid, lab):
    """botão da linha da safra na etapa 1 (Editar, Continuar…)"""
    r = L.c.js(f"""(()=>{{const r=document.querySelector('[role=row][data-rid="{sid}"]'); if(!r) return 'sem linha'; const n=s=>(s||'').replace(/\\s+/g,' ').trim();
      const b=[...r.querySelectorAll('button')].find(b=>n(b.innerText).indexOf({json.dumps(lab)})===0); if(!b) return 'sem botão'; b.click(); return 'ok';}})()"""); time.sleep(.7); return r
def linha_saf(sid): return L.c.js(f"(()=>{{const r=document.querySelector('[role=row][data-rid=\"{sid}\"]'); return r?{N}(r.innerText):'';}})()") or ''
def veredito(): return L.c.js(f"(()=>{{const e=document.querySelector('#saf-v3-ver [role=status]'); return e?{N}(e.innerText):'';}})()") or ''
def filtro(): return L.c.js(f"(()=>{{const e=document.getElementById('saf-cap-filtro'); return e&&e.offsetParent?{N}(e.innerText):'';}})()") or ''
def custo(): return L.c.js(f"(()=>{{const b=document.querySelector('[data-acao=resumo]'); const s=b&&b.parentElement; return s?{N}(s.innerText):'';}})()") or ''
def estado(): return L.c.js("(()=>{const s=window.__safSelf; return s?s.state.saf+' '+s.state.step:'';})()")
def cel(rid, mes, clica=False):
    """texto e aria-label da célula recurso × mês da g_cap; clica = filtra a g_op por ela"""
    return L.c.js(f"""(()=>{{const t=[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&/^RECURSO/i.test((t.querySelector('[role=columnheader]')||{{}}).innerText||'')); if(!t) return {{err:'sem g_cap'}};
      const hs=[...t.querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴]/g,'').trim().toLowerCase()); const i=hs.indexOf({json.dumps(mes)}); const r=t.querySelector('[role=row][data-rid={json.dumps(rid)}]');
      if(i<0||!r) return {{err:'sem célula',hs}}; const c=r.querySelectorAll('[role=cell]')[i]; const b=c&&c.querySelector('button'); const o={{txt:{N}(c.innerText),aria:b?b.getAttribute('aria-label'):''}};
      if({json.dumps(clica)}&&b) b.click(); return o;}})()""") or {}
def abre_cap():
    if L.c.js("[...document.querySelectorAll('button')].some(b=>b.offsetParent&&b.innerText.trim()==='Capacidade por mês ▾')"): botao('Capacidade por mês ▾'); time.sleep(.4)
def vista(nome):
    """lê a etapa 3 aberta: veredito, células de jul/27 (Tratores e Operadores), filtro de cada uma e custo"""
    abre_cap(); o = dict(ver=veredito(), custo=custo())
    for rid in ('trator', 'oper'):
        c0 = cel(rid, 'jul/27', clica=True); time.sleep(.6); o[rid] = dict(c0, filtro=filtro())
    o['rolagem'] = L.c.js("document.documentElement.scrollWidth>innerWidth+1")   # com o filtro e o veredito mais longos
    L.c.shot(os.path.join(PROBE, f'safc02_{nome}.png')); return o
# espelho com o mesmo período (o que a tela grava): os números esperados saem do dados2.capacidade
SAF = {s['id']: s for s in D2.SAFRAS}; _per = {s: (SAF[s]['ini'], SAF[s]['fim']) for s in ('S2627', 'S27SF')}
try:
    for s in ('S2627', 'S27SF'): SAF[s]['ini'], SAF[s]['fim'] = INI, FIM
    GA, GB = D2.capacidade('S2627'), D2.capacidade('S27SF'); COP = D2.plano_op('S27SF')['cop']
finally:
    for s in ('S2627', 'S27SF'): SAF[s]['ini'], SAF[s]['fim'] = _per[s]
JUL = next(i for i, (_, lab) in enumerate(D2.MESES) if lab == 'jul/27')
ESP = {k: GA[k]['cells'][JUL] for k in ('trator', 'oper')}
assert all(abs(GA[k]['cells'][JUL]['d'] - GB[k]['cells'][JUL]['d']) < 1e-9 for k in ESP), 'espelho assimétrico'
try:
    c = L.c = Chrome()
    for w, hh, toque in ((1440, 900, False), (390, 844, True)):
        tg = f'{w}px'
        abre('#saf=S2627&passo=safra', w, hh, toque)
        for sid in ('S2627', 'S27SF'):
            r1 = na_saf(sid, 'Editar'); fset('g_saf', 'ini', INI); fset('g_saf', 'fim', FIM); r2 = salvar(); time.sleep(.5); t = toast()
            chk(f'{tg} preparo: Editar {sid} e gravar o período 01/09/2026 a 12/07/2027 pela tela', r1 == 'ok' and r2 == 'ok' and 'Salvo' in t and 'set/2026 – jul/2027' in linha_saf(sid), (r1, r2, t, linha_saf(sid), painel()[:300]))
        na_saf('S2627', 'Continuar'); botao('Dimensionar operações ›'); time.sleep(.6); e1 = estado(); A = vista(f'S2627_{w}')
        botao('Trocar safra'); time.sleep(.5); na_saf('S27SF', 'Continuar'); botao('‹ Operações e recursos'); time.sleep(.6); e2 = estado(); B = vista(f'S27SF_{w}')
        chk(f'{tg} navegação: S2627 e depois S27SF abertas na etapa 3 pela tela', (e1, e2) == ('S2627 3', 'S27SF 3'), (e1, e2))
        for rid, nome in (('trator', 'Tratores'), ('oper', 'Operadores e equipe')):
            x = ESP[rid]; tot = f"{h1(x['d'])} h de {h1(x['cap'])} h ({D2.fmt_ocup(x['ocup'])})"
            chk(f'{tg} {nome} jul/27: a mesma ocupação ao alternar S2627 ↔ S27SF ({tot}), igual ao espelho',
                A[rid].get('txt') == B[rid].get('txt') == D2.fmt_ocup(x['ocup']) and tot in A[rid]['filtro'] and tot in B[rid]['filtro'] and f"{h1(x['d'])} h de {h1(x['cap'])} h" in A[rid].get('aria', '') and f"{h1(x['d'])} h de {h1(x['cap'])} h" in B[rid].get('aria', ''),
                (tot, A[rid], B[rid]))
        chk(f'{tg} Tratores jul/27 = 61,7 h nas duas vistas (era 140,3 h com a S2627 aberta)', h1(ESP['trator']['d']) == '61,7' and '61,7 h de' in A['trator']['filtro'] and '61,7 h de' in B['trator']['filtro'], (A['trator']['filtro'], B['trator']['filtro']))
        chk(f'{tg} S2627: a colheita da Safrinha de 14 e 15/07 aparece fora da conta na linha do filtro e no aria-label da célula',
            'fora da conta: Safrinha 2027 78,6 h depois do fim dela' in A['trator']['filtro'] and 'fora da conta: Safrinha 2027 78,6 h depois do fim dela' in A['trator'].get('aria', '')
            and 'fora da conta: Safrinha 2027 157,2 h depois do fim dela' in A['oper']['filtro'], (A['trator'], A['oper']['filtro']))
        chk(f'{tg} S27SF: a mesma carga aparece fora da conta como desta safra, depois do fim',
            'fora da conta: desta safra 78,6 h depois do fim' in B['trator']['filtro'] and 'fora da conta: desta safra 157,2 h depois do fim' in B['oper']['filtro'], (B['trator']['filtro'], B['oper']['filtro']))
        chk(f'{tg} veredito da S2627: "2 ocorrências da Safrinha 2027 depois do fim dela (Tratores 78,6 h e Operadores e equipe 157,2 h)", sem verde',
            '2 ocorrências da Safrinha 2027 depois do fim dela (Tratores 78,6 h e Operadores e equipe 157,2 h)' in A['ver'] and 'cabe com o que você tem' not in A['ver'], A['ver'])
        chk(f'{tg} veredito da S27SF: "Fora da conta: 2 ocorrências depois do fim da safra"', 'Fora da conta: 2 ocorrências depois do fim da safra' in B['ver'], B['ver'])
        chk(f'{tg} outra fazenda (Safra Mamão, LG2627) e encerrada (Safra 2025/26) não entram; cada vista soma só a outra aberta da Santa Rita',
            all('Mamão' not in v[r]['filtro'] and '2025/26' not in v[r]['filtro'] for v in (A, B) for r in ('trator', 'oper')) and ' · Safrinha 2027 ' in A['trator']['filtro'] and ' · Safra 2026/27 ' in B['trator']['filtro'],
            (A['trator']['filtro'], B['trator']['filtro']))
        chk(f'{tg} custo preservado: o custo de operação da S27SF ({rs(COP)}) inclui as colheitas fora da conta', rs(COP) in B['custo'], (rs(COP), B['custo']))
        chk(f'{tg} sem rolagem lateral nas duas vistas, com o filtro ativo', not A['rolagem'] and not B['rolagem'], (A['rolagem'], B['rolagem']))
        chk(f'{tg} sem erro de JS', erros() == '', erros())
finally:
    try:
        if L.c: L.c.close()
    finally: L.srv.terminate()
print(f'\nRESULTADO: {len(OK)} ok · {len(FAIL)} falhas')
for f in FAIL: print('  - ' + f)
sys.exit(1 if FAIL else 0)
