# -*- coding: utf-8 -*-
"""Teste CDP · Ficha do pivô (pedido do proprietário, 09/10/2026: "na irrigação onde colocamos os dados da ficha do pivô, lâmina 21 h etc.")
e as correções da revisão de 10/10 (A2 vazão em um lugar, A3 limite do setor na nota, A4 registrar e editar a ficha, A7 nome do cadastro).
A ficha (capacidade do equipamento) fica no detalhe do equipamento (CD-03 › Bomba do Pivô 2 › "Ficha do pivô ›") e abre pela Irrigação
(IR-01 › setor P2 › "Ficha do pivô", ou #P2:ficha) com o mesmo conteúdo; fechar volta ao detalhe de onde veio. Sem ficha, o pivô oferece
"Registrar ficha do pivô" (CD-03 e IR-01); a ficha aberta tem "Editar ficha". A vazão da ficha é a do cadastro (campo só leitura) e a do setor.
Fluxos: normal (1440 e 390 px), recusa (equipamento sem pivô, setor com alteração não salva, registro inválido), repetição (salvar sem mudar,
recarregar, ir e voltar entre as telas), conflito (cancelar com alteração pergunta antes). Capturas em _probe/ficha_pivo_*.png.
Uso: python3 ficha_pivo_test.py"""
import time, json
from cada_lib import T, SETV
import dados as D
F = D.FICHA_PIVO['a11']
KV = {'Identificação': 'Pivô 2 · setor P2 · Bomba do Pivô 2', 'Fabricante e modelo': 'Fabricante demonstrativo (sintético) · pivô central fixo · 8 torres · motobomba + hidrômetro novo',
      'Raio': '505 m', 'Área irrigada': '80 ha', 'Vazão': '166 L/s · 597,6 m³/h', 'Pressão': '32 mca', 'Tempo de volta a 100 %': '9,0 h', 'Lâmina a 100 %': '6,7 mm',
      'Regime de operação': '21 h/dia · fora do horário de ponta', 'Talhão': 'P2 · Santa Rita · 80 ha no cadastro'}
COLS = ['Percentímetro', 'Tempo de volta', 'Lâmina', 'Lâmina pela conta', 'Conferência']
t = T(); J = t.J
FX = 'aside[aria-label^="Ficha do pivô"]'
ficha = lambda: J(f"(document.querySelector('{FX}')||{{}}).innerText||''") or ''
aberta = lambda: bool(J(f"!!document.querySelector('{FX}')"))
kvs = lambda: dict((J(f"[...document.querySelectorAll('{FX} [style*=\"grid-template-columns: repeat(2\"] > div')].filter(d=>d.children.length===2&&!d.querySelector('input')).map(d=>[d.children[0].textContent.trim(),d.children[1].textContent.trim()])") or []))
cab = lambda: [x.replace('⇅', '').replace('▾', '').replace('▲', '').replace('▼', '').strip() for x in (J(f"[...document.querySelectorAll('{FX} [role=columnheader]')].map(h=>h.textContent.replace(/\\s+/g,' '))") or [])]
lin = lambda: J(f"[...document.querySelectorAll('{FX} [role=table] [role=row]')].slice(1).map(r=>[...r.querySelectorAll('[role=cell]')].map(c=>c.innerText.trim()))") or []
botao = lambda txt, raiz='aside[role=dialog]': J(f"(()=>{{const b=[...document.querySelectorAll('{raiz} button')].find(x=>x.innerText.replace(/\\s+/g,' ').trim()==={json.dumps(txt)}); if(!b) return false; b.click(); return true;}})()")
tem_botao = lambda txt: bool(J(f"!![...document.querySelectorAll('aside[role=dialog] button')].find(x=>x.innerText.replace(/\\s+/g,' ').trim()==={json.dumps(txt)})"))
esc = lambda: (J(f"(()=>{{const a=document.querySelector('{FX}'); if(a) a.dispatchEvent(new KeyboardEvent('keydown',{{key:'Escape',bubbles:true}}));}})()"), time.sleep(.6))
nota = lambda: J(f"(document.querySelector('{FX} [role=note]')||{{}}).innerText||''") or ''
def campo(k, val=None):   # campo do registro na gaveta (id fpv_f_<k>)
    if val is not None: J(f"({SETV})('{FX} #fpv_f_{k}',{json.dumps(val)})"); time.sleep(.15)
    return J(f"(document.querySelector('{FX} #fpv_f_{k}')||{{}}).value")
def linha(n, rot, val):   # célula da tabela do registro (aria-label "<rot> da linha n")
    J(f"({SETV})('{FX} input[aria-label=\"{rot} da linha {n}\"]',{json.dumps(val)})"); time.sleep(.15)
alertas = lambda: J(f"[...document.querySelectorAll('{FX} [role=alert]')].map(x=>x.innerText.trim()).join(' | ')") or ''
gravada = lambda: J("localStorage.getItem('talhao-os-ficha-pivo-v1')")
try:
    t.goto('CD-03.dc.html'); J("localStorage.removeItem('talhao-os-ficha-pivo-v1'); localStorage.removeItem('talhao-os-irrigacao-v1')"); t.goto('CD-03.dc.html')
    # ---------- 1 · CD-03: a vazão da bomba é a da ficha; o detalhe do equipamento abre a ficha ----------
    cap = t.rowtxt(0, 'Bomba do Pivô 2') or ''
    t.openrow(0, 'Bomba do Pivô 2'); temB = tem_botao('Ficha do pivô ›'); ro = [t.fdis('vazao_ir'), t.fv('vazao_ir')]
    hv = J("(()=>{const i=document.querySelector('aside[role=dialog] [id$=\"_vazao_ir\"]'); return i?i.closest('div').parentElement.innerText:'';})()") or ''
    t.fset('vazao_ir', '400'); ro.append(t.fv('vazao_ir'))
    t.chk('1 A2 · CD-03 › Bomba do Pivô 2: capacidade 597,6 m³/h (a vazão da ficha, 166 L/s); o campo Vazão fica só leitura ("vem da ficha do pivô") e digitar 400 não muda',
          '597,6 m³/h' in cap and temB and ro[0] is True and str(ro[1]).replace(',', '.') == '597.6' and str(ro[2]).replace(',', '.') == '597.6' and 'Vem da ficha do pivô' in hv, [cap, temB, ro, hv[-160:]])
    botao('Ficha do pivô ›'); time.sleep(.6)
    f1 = ficha(); k1 = kvs(); c1 = cab(); L1 = lin(); st1 = J(f"(document.querySelector('{FX} [role=status]')||{{}}).innerText||''") or ''
    lk1 = J(f"(()=>{{const a=[...document.querySelectorAll('{FX} a')].pop(); return a?[a.innerText.trim(),a.getAttribute('href')]:null;}})()")
    by = {r[0]: r for r in L1}
    t.chk('2 A7 · campos da ficha com a unidade no valor; identificação e modelo do cadastro (Bomba do Pivô 2 · pivô central fixo · 8 torres · motobomba), talhão e fazenda do cadastro',
          f1.startswith('Ficha do pivô · Pivô 2') and k1 == KV, [f1[:60], {k: (k1.get(k), v) for k, v in KV.items() if k1.get(k) != v}])
    t.chk('3 tabela percentímetro × tempo × lâmina como está na ficha, 10 linhas (a de 100 % vem dos campos); a conta confere e o 60 % diverge (11,0 × 11,17 mm), dito no resumo',
          c1 == COLS and len(L1) == 10 and by.get('60 %') == ['60 %', '15,0 h', '11,0 mm', '11,17 mm', 'Diverge −0,17 mm'] and by.get('100 %') == ['100 %', '9,0 h', '6,7 mm', '6,70 mm', 'Confere']
          and sum(1 for r in L1 if r[4] == 'Confere') == 9 and '60 % · 11,0 mm na ficha × 11,17 mm pela conta' in st1 and '0,05 mm × 100 ÷ percentímetro' in f1, [c1, L1[:2], by.get('60 %'), st1])
    n4 = nota()
    t.chk('4 A3 · a ficha não prescreve lâmina: no cadastro aponta para o limite por passada do setor P2 na Irrigação (sem número de outra fonte) e o responsável técnico; CAD diz onde ler; link para o setor',
          'não prescreve lâmina' in n4 and 'limite por passada do setor P2, na Irrigação,' in n4 and '(Ana, agrônoma)' in n4 and 'PA-07' not in f1 and '12,0' not in n4
          and 'lida no setor P2 da Irrigação (vem de Análises de solo)' in f1 and lk1 == ['Ver o setor P2 na Irrigação ›', 'IR-01.dc.html#P2'], [n4, lk1])
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
    # A2 · renomear no cadastro: a ficha aberta no mesmo detalhe mostra o nome novo
    t.fset('nome', 'Bomba P2 nova'); t.btn('Salvar'); time.sleep(.4); t.cancel(); time.sleep(.2)
    t.openrow(0, 'Bomba P2 nova'); botao('Ficha do pivô ›'); time.sleep(.6); k6 = kvs()
    t.chk('6b A2 · renomear a bomba no cadastro: a ficha do mesmo detalhe passa a dizer "Bomba P2 nova"', (k6.get('Identificação') or '').endswith('Bomba P2 nova'), k6.get('Identificação'))
    esc(); t.fset('nome', 'Bomba do Pivô 2'); t.btn('Salvar'); time.sleep(.4); t.cancel(); time.sleep(.2)
    # ---------- 7 · RECUSA: sem pivô, nada; pivô sem ficha registra; #ficha= sem ficha não abre ----------
    t.openrow(0, 'Trator T1'); semT1 = not tem_botao('Ficha do pivô ›') and not tem_botao('Registrar ficha do pivô ›'); t.cancel()
    t.openrow(0, 'Gotejo T7'); semT7 = not tem_botao('Ficha do pivô ›') and not tem_botao('Registrar ficha do pivô ›'); t.cancel()
    t.openrow(0, 'Bomba do Pivô 1'); regP1 = tem_botao('Registrar ficha do pivô ›') and not tem_botao('Ficha do pivô ›'); vz1 = [t.fdis('vazao_ir'), t.fv('vazao_ir')]; t.cancel()
    t.goto('CD-03.dc.html#ficha=a15'); s7 = aberta()
    t.chk('7 RECUSA: Trator T1 e Gotejo T7 (não são pivô) não oferecem ficha; a Bomba do Pivô 1 (sem ficha) oferece "Registrar ficha do pivô ›" e a vazão (540 m³/h, a do setor P1) fica só leitura até registrar a ficha; CD-03#ficha=a15 não abre',
          semT1 and semT7 and regP1 and vz1 == [True, '540'] and s7 is False, [semT1, semT7, regP1, vz1, s7])
    # ---------- 8 · A4 · registrar a ficha da Bomba do Pivô 1 ----------
    t.openrow(0, 'Bomba do Pivô 1'); botao('Registrar ficha do pivô ›'); time.sleep(.6)
    f8 = ficha(); pre = [campo('vazao_ls'), campo('area_ha'), campo('fabricante')]
    botao('Salvar ficha', FX); time.sleep(.4); a8 = alertas(); g8 = gravada()
    t.chk('8 A4 · "Registrar ficha do pivô · Pivô 1": vazão (150 L/s) e área (95 ha) do setor já vêm, corrigíveis; salvar em branco aponta os campos e não grava nada',
          f8.startswith('Registrar ficha do pivô · Pivô 1') and pre == ['150', '95', ''] and 'Corrija os campos destacados' in a8 and 'fabricante' in a8.lower() and g8 is None, [f8[:60], pre, a8[:200], g8])
    for k, val in (('fabricante', 'Fabricante B (sintético)'), ('raio_m', '550'), ('vazao_ls', '155'), ('pressao_mca', '30'), ('volta_100_h', '10,0'), ('lamina_100_mm', '6,1'), ('regime_h', '21')):
        campo(k, val)
    linha(1, 'Tempo de volta', '11,1'); linha(1, 'Lâmina', '6,8'); linha(2, 'Percentímetro', '100'); linha(2, 'Tempo de volta', '10'); linha(2, 'Lâmina', '6,1')
    botao('Salvar ficha', FX); time.sleep(.4); a9 = alertas(); g9 = gravada()
    J(f"document.querySelector('{FX} button[aria-label=\"Remover a linha 2\"]').click()"); time.sleep(.3)
    botao('Salvar ficha', FX); time.sleep(.7); f9 = ficha(); k9 = kvs(); L9 = lin(); toast9 = t.toast()
    t.chk('9 A4 · RECUSA da linha de 100 % (vem do tempo de volta e da lâmina a 100 %); removida, salva: a ficha abre com vazão 155 L/s · 558,0 m³/h e 2 linhas (100 % e 90 %); o aviso diz que o cadastro e a Irrigação usam esta vazão',
          'linha de 100 %' in a9 and g9 is None and f9.startswith('Ficha do pivô · Pivô 1') and k9.get('Vazão') == '155 L/s · 558,0 m³/h' and sorted(r[0] for r in L9) == ['100 %', '90 %']
          and 'Fabricante B (sintético)' in (k9.get('Fabricante e modelo') or '') and 'o cadastro e a Irrigação usam esta vazão' in toast9 and '(dados sintéticos)' not in f9, [a9[:160], g9, k9.get('Vazão'), L9, toast9[-200:]])
    t.shot('ficha_pivo_registro_p1.png')
    esc(); cap10 = t.rowtxt(0, 'Bomba do Pivô 1') or ''; ro10 = [t.isopen(), t.fdis('vazao_ir'), t.fv('vazao_ir')]
    t.chk('10 A2 · fechar volta à Bomba do Pivô 1: a capacidade passa a 558 m³/h (a da ficha) e o campo Vazão fica só leitura',
          '558 m³/h' in cap10 and ro10[0] is True and ro10[1] is True and str(ro10[2]).replace(',', '.') == '558', [cap10, ro10])
    t.cancel()
    # ---------- 11 · IR-01: o setor P1 lê a vazão da ficha registrada e abre a mesma ficha ----------
    t.goto('IR-01.dc.html#P1'); time.sleep(.9); eq11 = J("(()=>{const i=document.querySelector('aside[role=dialog] [id$=\"_eqT\"]'); return i?i.value:'';})()") or ''
    temI = tem_botao('Ficha do pivô'); botao('Ficha do pivô'); time.sleep(.6); k11 = kvs()
    t.chk('11 A2/A4 · IR-01 › setor P1: equipamento "155 L/s · Bomba do Pivô 1" (a vazão da ficha) e "Ficha do pivô" abre o mesmo registro',
          '155 L/s' in eq11 and 'Bomba do Pivô 1' in eq11 and temI and k11 == k9, [eq11, temI, k11 == k9])
    esc()
    # ---------- 12 · IR-01 P2: a mesma ficha do CD-03; a nota lê o limite do setor (A3) ----------
    t.goto('IR-01.dc.html#P2'); time.sleep(.9); eqP2 = J("(()=>{const i=document.querySelector('aside[role=dialog] [id$=\"_eqT\"]'); return i?i.value:'';})()") or ''
    botao('Ficha do pivô'); time.sleep(.6); f12 = ficha(); k12 = kvs(); L12 = lin(); n12 = nota()
    lk12 = J(f"(()=>{{const a=[...document.querySelectorAll('{FX} a')].pop(); return a?[a.innerText.trim(),a.getAttribute('href')]:null;}})()")
    t.chk('12 IR-01 › setor P2 ("Bomba do Pivô 2", o nome do cadastro): os mesmos campos e a mesma tabela do CD-03; a nota diz o limite do setor (até 12,0 mm por passada); CAD como leitura; link para o cadastro',
          'Bomba do Pivô 2' in eqP2 and 'Bomba B2' not in eqP2 and k12 == KV and L12 == L1 and 'limite por passada do setor P2 (até 12,0 mm por passada)' in n12
          and lk12 == ['Abrir no cadastro do equipamento ›', 'CD-03.dc.html#ficha=a11'] and 'sem medição de água no solo neste talhão' in f12, [eqP2, k12 == KV, len(L12), n12, lk12])
    esc(); v12 = [aberta(), t.isopen(), t.title()]
    t.fset('lmax', '10'); t.btn('Salvar'); time.sleep(.6); t.cancel(); time.sleep(.3)
    t.goto('IR-01.dc.html#P2:ficha'); time.sleep(1.0); n13 = nota()
    t.chk('13 A3 · Esc volta ao setor P2; limite do setor 10 mm salvo → a nota da ficha diz "até 10,0 mm por passada" (o que a programação aplica)',
          v12[0] is False and v12[1] is True and 'Setor' in (v12[2] or '') and '(até 10,0 mm por passada)' in n13 and '12,0' not in n13, [v12, n13])
    esc(); t.fset('lmax', '12'); t.btn('Salvar'); time.sleep(.5); t.cancel(); time.sleep(.2)
    # RECUSA: alteração não salva no setor → a ficha não abre e o painel pede para salvar ou descartar (nada se perde)
    t.goto('IR-01.dc.html#P2'); time.sleep(.9); t.fset('lmax', '11'); botao('Ficha do pivô'); time.sleep(.4); w14 = t.dlg()
    t.chk('14 RECUSA com alteração não salva no setor: a ficha não abre e aparece "Há alterações não salvas" (o 11 digitado continua)',
          not aberta() and 'Há alterações não salvas' in w14 and t.fv('lmax') == '11', [aberta(), w14[-200:], t.fv('lmax')])
    botao('Descartar alterações'); time.sleep(.3)
    t.goto('IR-01.dc.html#T7'); time.sleep(.8); semT7i = not tem_botao('Ficha do pivô') and not tem_botao('Registrar ficha do pivô')
    t.chk('15 RECUSA: setor T7 (gotejo) não oferece ficha do pivô', semT7i, semT7i)
    # ---------- 16 · A2 · editar a vazão da ficha do P2 (170 L/s): cadastro e Irrigação acompanham; cancelar com alteração pergunta ----------
    t.goto('IR-01.dc.html#P2:ficha'); time.sleep(1.0); botao('Editar ficha', FX); time.sleep(.4); e16 = [ficha().split('\n')[0], campo('vazao_ls'), campo('lamina_100_mm')]
    campo('vazao_ls', '170'); botao('Cancelar', FX); time.sleep(.3); w16 = alertas()
    botao('Continuar editando', FX); time.sleep(.2); botao('Salvar ficha', FX); toast16 = ''
    for _ in range(30):
        time.sleep(.1); toast16 = t.toast()
        if 'salva' in toast16: break
    time.sleep(.3); k16 = kvs()
    esc(); eq16 = J("(()=>{const i=document.querySelector('aside[role=dialog] [id$=\"_eqT\"]'); return i?i.value:'';})()") or ''
    t.chk('16 A2 · "Editar ficha" abre o registro como está (166 · 6,7); cancelar com alteração pergunta antes; salvar 170 L/s: a ficha e o setor P2 passam a 170 L/s',
          e16 == ['Editar ficha do pivô · Pivô 2', '166', '6,7'] and 'Há alterações não salvas' in w16 and k16.get('Vazão') == '170 L/s · 612,0 m³/h' and '170 L/s' in eq16 and 'salva' in toast16,
          [e16, w16[:80], k16.get('Vazão'), eq16, toast16[-200:]])
    t.goto('CD-03.dc.html'); cap16 = t.rowtxt(0, 'Bomba do Pivô 2') or ''
    t.chk('16b A2 · no cadastro, a Bomba do Pivô 2 passa a 612 m³/h (a vazão da ficha editada na Irrigação)', '612 m³/h' in cap16, cap16)
    # ---------- 17 · REPETIÇÃO: salvar sem mudar não grava de novo; recarregar mantém; ida ao cadastro e volta ----------
    t.openrow(0, 'Bomba do Pivô 2'); botao('Ficha do pivô ›'); time.sleep(.6); g0 = gravada(); botao('Editar ficha', FX); time.sleep(.3); botao('Salvar ficha', FX); time.sleep(.5)
    r17 = [gravada() == g0, 'sem alteração' in t.toast(), aberta(), kvs().get('Vazão')]
    J(f"[...document.querySelectorAll('{FX} a')].pop().click()"); time.sleep(1.6)
    r17b = [J("location.pathname.split('/').pop()"), t.isopen(), J("(()=>{const i=document.querySelector('aside[role=dialog] [id$=\"_eqT\"]'); return i?i.value:'';})()") or '']
    t.chk('17 REPETIÇÃO: salvar sem mudar não grava ("sem alteração"); recarregado, o registro continua (170 L/s); o link leva ao setor P2 na Irrigação com a mesma vazão',
          r17 == [True, True, True, '170 L/s · 612,0 m³/h'] and r17b[0] == 'IR-01.dc.html' and r17b[1] is True and '170 L/s' in r17b[2], [r17, r17b])
    # ---------- 18 · 390 px: leitura e registro cabem sem rolagem lateral ----------
    t.c.size(390, 844); t.goto('IR-01.dc.html#P2:ficha'); time.sleep(1.0)
    medir = lambda: J(f"(()=>{{const a=document.querySelector('{FX}'); if(!a) return null; return [a.scrollWidth,a.clientWidth,document.scrollingElement.scrollWidth,innerWidth];}})()")
    g18 = medir(); t.shot('ficha_pivo_ir01_390.png'); botao('Editar ficha', FX); time.sleep(.4); g18b = medir(); t.shot('ficha_pivo_registro_390.png')
    t.chk('18 390 px: a gaveta (leitura e registro) cabe sem rolagem lateral e a página não rola de lado',
          bool(g18) and bool(g18b) and all(x[0] <= x[1] and x[2] <= x[3] for x in (g18, g18b)), [g18, g18b])
    botao('Cancelar', FX); t.c.size(1440, 1100)
    e = t.errs(); t.chk('19 nenhum erro de execução nas páginas', not e, e)
finally:
    t.fim()
