# -*- coding: utf-8 -*-
"""Teste CDP · Ficha do pivô (pedido do proprietário, 09/10/2026: "na irrigação onde colocamos os dados da ficha do pivô, lâmina 21 h etc.").
A ficha (capacidade do equipamento, dados sintéticos) fica no detalhe do equipamento (CD-03 › Bomba do Pivô 2 › "Ficha do pivô ›") e abre
pela Irrigação (IR-01 › setor P2 › "Ficha do pivô", ou #P2:ficha) com o mesmo conteúdo; fechar volta ao detalhe de onde veio.
Tabela da ficha com filtro e ordenação (uma variável por coluna, unidade na célula), conferência pela conta (60 % diverge), CAD do talhão
como leitura (ponto nomeado) e a nota de que a ficha não prescreve lâmina. Fluxos: normal (1440 e 390 px), recusa (equipamento ou
setor sem ficha; painel com alteração não salva), repetição (abrir de novo, recarregar, ir e voltar entre as telas).
Esperados de ficha_pivo.dados_pagina() (a mesma fonte da página). Capturas em _probe/ficha_pivo_*.png. Uso: python3 ficha_pivo_test.py"""
import time, json, unicodedata
from cada_lib import T
import ficha_pivo as FP
FPD = FP.dados_pagina()['a11']; KV = {x['l']: x['v'] for x in FPD['kv']}
COLS = ['Percentímetro', 'Tempo de volta', 'Lâmina', 'Lâmina pela conta', 'Conferência']
def nz(t): return ''.join(ch for ch in unicodedata.normalize('NFD', str(t)) if not unicodedata.combining(ch)).lower()
t = T(); J = t.J
FX = 'aside[aria-label^="Ficha do pivô"]'
ficha = lambda: J(f"(document.querySelector('{FX}')||{{}}).innerText||''") or ''
aberta = lambda: bool(J(f"!!document.querySelector('{FX}')"))
kvs = lambda: dict((J(f"[...document.querySelectorAll('{FX} [style*=\"grid-template-columns: repeat(2\"] > div')].map(d=>[d.children[0].textContent.trim(),d.children[1].textContent.trim()])") or []))   # textContent: o rótulo sem o maiúsculo do CSS
cab = lambda: [x.replace('⇅', '').replace('▾', '').replace('▲', '').replace('▼', '').strip() for x in (J(f"[...document.querySelectorAll('{FX} [role=columnheader]')].map(h=>h.textContent.replace(/\\s+/g,' '))") or [])]
lin = lambda: J(f"[...document.querySelectorAll('{FX} [role=table] [role=row]')].slice(1).map(r=>[...r.querySelectorAll('[role=cell]')].map(c=>c.innerText.trim()))") or []
botao = lambda txt: J(f"(()=>{{const b=[...document.querySelectorAll('aside[role=dialog] button')].find(x=>x.innerText.replace(/\\s+/g,' ').trim()==={json.dumps(txt)}); if(!b) return false; b.click(); return true;}})()")
tem_botao = lambda txt: bool(J(f"!![...document.querySelectorAll('aside[role=dialog] button')].find(x=>x.innerText.replace(/\\s+/g,' ').trim()==={json.dumps(txt)})"))
esc = lambda: (J(f"(()=>{{const a=document.querySelector('{FX}'); if(a) a.dispatchEvent(new KeyboardEvent('keydown',{{key:'Escape',bubbles:true}}));}})()"), time.sleep(.6))
try:
    # ---------- 1 · CD-03: a vazão da bomba é a da ficha; o detalhe do equipamento abre a ficha ----------
    t.goto('CD-03.dc.html'); cap = t.rowtxt(0, 'Bomba do Pivô 2') or ''
    t.openrow(0, 'Bomba do Pivô 2'); temB = tem_botao('Ficha do pivô ›'); botao('Ficha do pivô ›'); time.sleep(.6)
    f1 = ficha(); k1 = kvs(); c1 = cab(); L1 = lin(); st1 = J(f"(document.querySelector('{FX} [role=status]')||{{}}).innerText||''") or ''
    lk1 = J(f"(()=>{{const a=[...document.querySelectorAll('{FX} a')].pop(); return a?[a.innerText.trim(),a.getAttribute('href')]:null;}})()")
    by = {r[0]: r for r in L1}
    t.chk('1 CD-03 › Bomba do Pivô 2: capacidade 597,6 m³/h (a vazão da ficha, 166 L/s) e "Ficha do pivô ›" no detalhe abre a gaveta "Ficha do pivô · Pivô 2"',
          '597,6 m³/h' in cap and temB and aberta() and f1.startswith('Ficha do pivô · Pivô 2'), [cap, temB, f1[:80]])
    t.chk('2 campos da ficha com a unidade no valor (raio, área, vazão, pressão, volta e lâmina a 100 %, regime "21 h/dia · fora do horário de ponta", talhão P2)',
          k1 == KV and k1.get('Regime de operação') == '21 h/dia · fora do horário de ponta' and k1.get('Vazão') == '166 L/s · 597,6 m³/h', [k1, KV])
    t.chk('3 tabela percentímetro × tempo × lâmina como está na ficha, 10 linhas, uma variável por coluna; a conta confere e o 60 % diverge (11,0 × 11,17 mm), dito no resumo',
          c1 == COLS and len(L1) == 10 and by.get('60 %') == ['60 %', '15,0 h', '11,0 mm', '11,17 mm', 'Diverge −0,17 mm'] and by.get('100 %') == ['100 %', '9,0 h', '6,7 mm', '6,70 mm', 'Confere']
          and sum(1 for r in L1 if r[4] == 'Confere') == 9 and '60 % · 11,0 mm na ficha × 11,17 mm pela conta' in st1, [c1, L1[:2], by.get('60 %'), st1])
    t.chk('4 a ficha não prescreve lâmina (política de água PA-07 v3 e responsável técnico); CAD do talhão P2: no cadastro diz onde ler (setor P2 da Irrigação); link para o setor na Irrigação',
          'não prescreve lâmina' in f1 and 'PA-07 v3' in f1 and 'responsável técnico' in f1 and 'Água disponível no solo (CAD) · talhão P2' in f1 and 'lida no setor P2 da Irrigação (vem de Análises de solo)' in f1 and 'sem medição' not in f1
          and lk1 == ['Ver o setor P2 na Irrigação ›', 'IR-01.dc.html#P2'], [f1[-500:], lk1])
    t.shot('ficha_pivo_cd03_1440.png')
    # ---------- 5 · ordenar e filtrar a tabela da ficha ----------
    J(f"document.querySelector('{FX} button[aria-label=\"Ordenar por Lâmina\"]').click()"); time.sleep(.3)
    J(f"document.querySelector('{FX} button[aria-label=\"Ordenar por Lâmina\"]').click()"); time.sleep(.4)
    o5 = [r[0] for r in lin()]
    J(f"document.querySelector('{FX} button[aria-label=\"Filtrar Conferência\"]').click()"); time.sleep(.4)
    J("[...document.querySelectorAll('[role=dialog][aria-label=\"Filtrar Conferência\"] button')].find(b=>b.innerText.trim()==='Limpar').click()"); time.sleep(.3)
    J("(()=>{const l=[...document.querySelectorAll('[role=dialog][aria-label=\"Filtrar Conferência\"] label')].find(x=>x.innerText.trim().startsWith('Diverge')); if(l) l.querySelector('input').click();})()"); time.sleep(.3)
    J("[...document.querySelectorAll('[role=dialog][aria-label=\"Filtrar Conferência\"] button')].find(b=>b.innerText.trim()==='OK').click()"); time.sleep(.5)
    L5 = lin()
    t.chk('5 ordenar por Lâmina (maior → menor: 10 % primeiro) e filtrar Conferência = "Diverge" deixa só a linha 60 %',
          o5[:2] == ['10 %', '20 %'] and o5[-1] == '100 %' and [r[0] for r in L5] == ['60 %'], [o5, L5])
    J(f"[...document.querySelectorAll('{FX} button')].find(b=>b.innerText.trim()==='Limpar filtros').click()"); time.sleep(.3)
    # ---------- 6 · Esc fecha a ficha e volta ao detalhe do equipamento ----------
    esc(); v6 = [aberta(), t.isopen(), t.fv('nome')]
    t.chk('6 Esc fecha a ficha e volta ao detalhe da Bomba do Pivô 2', v6 == [False, True, 'Bomba do Pivô 2'], v6)
    t.cancel()
    # ---------- 7 · RECUSA: equipamento sem ficha não oferece a ficha; #ficha= de equipamento sem ficha não abre nada ----------
    t.openrow(0, 'Trator T1'); semT1 = not tem_botao('Ficha do pivô ›'); t.cancel()
    t.goto('CD-03.dc.html#ficha=a15'); s7 = aberta()
    t.chk('7 RECUSA: Trator T1 (e Bomba do Pivô 1, sem ficha registrada) não oferecem "Ficha do pivô"; CD-03#ficha=a15 não abre gaveta', semT1 and s7 is False, [semT1, s7])
    # ---------- 8 · IR-01: o setor P2 abre a mesma ficha; fechar volta ao setor ----------
    t.goto('IR-01.dc.html#P2'); time.sleep(.8); temI = tem_botao('Ficha do pivô'); botao('Ficha do pivô'); time.sleep(.6)
    f8 = ficha(); k8 = kvs(); L8 = lin(); lk8 = J(f"(()=>{{const a=[...document.querySelectorAll('{FX} a')].pop(); return a?[a.innerText.trim(),a.getAttribute('href')]:null;}})()")
    t.chk('8 IR-01 › setor P2 › "Ficha do pivô": os mesmos campos e a mesma tabela do CD-03 (um componente, uma fonte), a CAD do talhão como leitura e o link para o cadastro do equipamento',
          temI and k8 == k1 and L8 == L1 and lk8 == ['Abrir no cadastro do equipamento ›', 'CD-03.dc.html#ficha=a11']
          and 'Água disponível no solo (CAD) · talhão P2' in f8 and 'sem medição de água no solo neste talhão' in f8, [temI, k8 == k1, len(L8), lk8, f8[-400:]])
    esc(); v8 = [aberta(), t.isopen(), t.title()]
    t.chk('8b Esc fecha a ficha e volta ao painel do setor P2', v8[0] is False and v8[1] is True and 'Setor' in (v8[2] or ''), v8)
    # RECUSA: alteração não salva no setor → a ficha não abre e o painel pede para salvar ou descartar (nada se perde)
    t.fset('lmax', '11'); botao('Ficha do pivô'); time.sleep(.4); w9 = t.dlg()
    t.chk('9 RECUSA com alteração não salva no setor: a ficha não abre e aparece "Há alterações não salvas" (o 11 digitado continua)',
          not aberta() and 'Há alterações não salvas' in w9 and t.fv('lmax') == '11', [aberta(), w9[-200:], t.fv('lmax')])
    botao('Descartar alterações'); time.sleep(.3)
    t.goto('IR-01.dc.html#P1'); time.sleep(.8); semP1 = not tem_botao('Ficha do pivô')
    t.goto('IR-01.dc.html#P1:ficha'); time.sleep(.8); s10 = [aberta(), t.isopen()]
    t.chk('10 RECUSA: setor P1 (sem ficha) não oferece "Ficha do pivô"; IR-01#P1:ficha abre só o setor', semP1 and s10 == [False, True], [semP1, s10])
    # ---------- 11 · REPETIÇÃO: link direto, ida ao cadastro e volta, abrir de novo ----------
    t.goto('IR-01.dc.html#P2:ficha'); time.sleep(.9); r1 = [aberta(), kvs() == k1]
    J(f"[...document.querySelectorAll('{FX} a')].pop().click()"); time.sleep(1.6)
    r2 = [J("location.pathname.split('/').pop()"), aberta(), kvs() == k1]
    esc(); r3 = [aberta(), t.fv('nome')]; botao('Ficha do pivô ›'); time.sleep(.6); r4 = [aberta(), lin() == L1]
    t.chk('11 REPETIÇÃO: IR-01#P2:ficha abre a ficha; "Abrir no cadastro do equipamento" leva ao CD-03 com a mesma ficha; fechar volta à bomba e reabrir mostra o mesmo',
          r1 == [True, True] and r2 == ['CD-03.dc.html', True, True] and r3 == [False, 'Bomba do Pivô 2'] and r4 == [True, True], [r1, r2, r3, r4])
    esc(); t.cancel()
    # ---------- 12 · 390 px ----------
    t.c.size(390, 844); t.goto('IR-01.dc.html#P2:ficha'); time.sleep(1.0)
    g12 = J(f"(()=>{{const a=document.querySelector('{FX}'); if(!a) return null; const r=a.querySelector('.g2rola'); const h=a.querySelector('[role=columnheader]');"
            f" return [a.scrollWidth,a.clientWidth,document.scrollingElement.scrollWidth,innerWidth,r?Math.round(r.getBoundingClientRect().right):9999,Math.round(a.getBoundingClientRect().right),getComputedStyle(h).position];}})()")
    t.shot('ficha_pivo_ir01_390.png')
    J(f"(()=>{{const t=document.querySelector('{FX} [role=table]'); if(t) t.scrollIntoView({{block:'start'}});}})()"); time.sleep(.3); t.shot('ficha_pivo_ir01_390_tabela.png')
    t.chk('12 390 px: a gaveta cabe sem rolagem lateral (a tabela rola só dentro da caixa, 1ª coluna presa) e a página não rola de lado',
          bool(g12) and g12[0] <= g12[1] and g12[2] <= g12[3] and g12[4] <= g12[5] and g12[6] == 'sticky', g12)
    t.c.size(1440, 1100)
    e = t.errs(); t.chk('13 nenhum erro de execução nas páginas', not e, e)
finally:
    t.fim()
