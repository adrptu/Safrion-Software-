# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO-20261004 v2 (5983172395) no Planejar safra, agora com a etapa 3 única "Dimensione operações e
recursos" (05/10/2026; ESPECIFICACAO etapa-unica-3-4-5 §3.4 e §9.3): a g_op tem 8 colunas, uma variável por coluna e a unidade na célula
(ha-op na operação, ha nos demais níveis); Situação só com os valores de s.sit e chips; filtros de Situação e Conjunto (os de Modo,
Largura e Planos saíram com as colunas, que foram para o formulário); ordem numérica do Custo R$/ha; editar a largura da Adubação de
cobertura (só esta atividade) recalcula rendimento e R$/ha na mesma linha; a busca acha o talhão. Etapas 2 e 4 (demanda) como antes; 390 px
sem rolagem da página. Uso: python3 tabelas_saf_test.py [pasta de capturas]   (< 90 s)"""
import sys, os, time, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
OUT = sys.argv[1] if len(sys.argv) > 1 else None
if OUT: os.makedirs(OUT, exist_ok=True)
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ') + n + (' · ' + str(info)[:300] if info != '' else ''))

p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
URL = f'http://127.0.0.1:{p}/SAF.dc.html#saf=S2627&passo=operacoes'
# etapa única (§3.4), com as colunas essenciais (COLUNAS-1, 10/10): 6 colunas; Rendimento e Área trabalhada (base das horas) foram ao formulário
# Rendimento; a unidade fixa vai na célula ("116,7 h", "R$ 14,49/ha-op") e no formulário ("21,60" ha/h, "2.520 ha-op")
COLS = ['Operação › atividade › talhão', 'Situação', 'Data', 'Conjunto', 'Horas-conjunto', 'Custo R$/ha']
NCOL = len(COLS)
def form():   # campos do formulário aberto (id fx_<grade>_<campo> → valor)
    return J("Object.fromEntries([...document.querySelectorAll('aside[role=dialog] input,aside[role=dialog] select')].filter(x=>x.offsetParent&&/^fx_/.test(x.id)).map(x=>[x.id.replace(/^fx_g_[a-z]+_[A-Za-z0-9]+_/,''),x.value]))") or {}
def fecha(): J("(()=>{const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent); if(!a) return; const b=[...a.querySelectorAll('button')].find(b=>b.getAttribute('aria-label')==='Fechar'||b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.35)
def abre_rid(rid):
    J(f"(()=>{{const r=[...document.querySelectorAll('[role=row][data-rid]')].find(r=>r.getAttribute('data-rid')==={json.dumps(rid)}&&r.offsetParent); if(!r) return; const z=[...r.querySelectorAll('[role=cell]')].find(z=>z.innerText.trim()&&!z.querySelector('button,input,a')); (z||r).click();}})()"); time.sleep(.5)
TB = "[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&[...t.querySelectorAll('[role=columnheader]')].some(h=>/^OPERAÇÃO/i.test(h.innerText.trim())))"
def heads(): return J(f"[...({TB}).querySelectorAll('[role=columnheader]')].map(h=>h.innerText.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim().replace(/ · \\d+$/,''))") or []   # filtro ativo acrescenta ' · n'
def linhas(): return J(f"[...({TB}).querySelectorAll('[role=row]')].filter(r=>r.offsetParent&&r.querySelector('[role=cell]')).map(r=>[...r.querySelectorAll('[role=cell]')].map((x,i)=>{{const t=x.innerText.replace(/\\s+/g,' ').trim(); return i===0?t.replace(/^[▸▾]\\s*/,''):t;}}))") or []
def ix(col): return COLS.index(col)
def filtra(col, vals):
    J(f"({TB}).querySelector('button[aria-label=\"Filtrar {col}\"]').click()"); time.sleep(.4)
    J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Limpar').click()"); time.sleep(.2)
    for v in vals:
        J(f"(()=>{{const l=[...document.querySelectorAll('[role=dialog] label')].find(l=>l.innerText.replace(/\\s+\\d+$/,'').trim()==={json.dumps(v)}); l&&l.querySelector('input').click();}})()"); time.sleep(.15)
    J("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='OK').click()"); time.sleep(.5)
def limpa(): J("(()=>{const b=[...document.querySelectorAll('main button')].find(b=>b.offsetParent&&/^Limpar filtros/.test(b.innerText.trim())); b&&b.click();})()"); time.sleep(.4)
def ordena(col, desc=False):
    J(f"({TB}).querySelector('button[aria-label=\"Filtrar {col}\"]').click()"); time.sleep(.4)
    J(f"[...document.querySelectorAll('[role=dialog] button.g2fi')][{1 if desc else 0}].click()"); time.sleep(.5)
def num(t): return float(t.replace('.', '').replace(',', '.'))
def shot(n):
    if OUT: c.shot(os.path.join(OUT, n + '.png'))

try:
    c.aparelho(1440, 900, 1, False)
    c.goto(URL.split('#')[0].replace('SAF.dc.html', 'Main.dc.html'), .3); J("localStorage.clear(); sessionStorage.clear()")
    c.goto(URL, 1.6); J("window.__e=[];addEventListener('error',e=>window.__e.push(String(e.message)))")
    h = heads(); rs = linhas(); shot('saf3-1440')
    chk('§3.4 cabeçalhos: 6 colunas, uma variável por coluna, sem unidade entre parênteses (a unidade vai na célula); sem Rendimento nem Área trabalhada (COLUNAS-1)',
        [x.upper() for x in h] == [x.upper() for x in COLS] and not any(x.upper() in ('RENDIMENTO', 'ÁREA TRABALHADA') for x in h), h)
    chk('nenhuma célula junta duas medidas ("12 m × 7 km/h", "R$/kg", "Parte: …")', not any(' m × ' in x or 'R$/kg' in x or x.startswith('Parte:') for r in rs for x in r), [r for r in rs if any(' m × ' in x or 'R$/kg' in x for x in r)][:2])
    n0 = [r for r in rs if len(r) == NCOL and r[0] != 'Total']
    chk('Situação só com os valores de s.sit (S2627: "Janela não informada" nas 8 operações, sem números)', len(n0) == 8 and all(r[1] == 'Janela não informada' for r in n0), [r[1] for r in n0])
    chk('unidade por nível: operação em ha-op (custo); horas com "h"', all((r[5] == '' or r[5].endswith('/ha-op')) and r[4].endswith(' h') for r in n0), [(r[0], r[4], r[5]) for r in n0])
    # o que saiu da linha está no formulário Rendimento: rendimento efetivo (ha/h) e área trabalhada em ha-op na operação, com as horas
    abre_rid('op:Pulverização'); fp = form(); fecha()
    chk('COLUNAS-1 · Pulverização: o formulário Rendimento mostra 21,60 ha/h e a área trabalhada em ha-op com as horas-conjunto (saíram da linha)',
        fp.get('rend_c') == '21,60' and re.match(r'^[\d.]+ ha-op · [\d.]+,\d horas-conjunto$', fp.get('area_c', '')), fp)
    for _ in range(4):
        if not J(f"(()=>{{const b=[...({TB}).querySelectorAll('button[aria-label^=\"Expandir\"]')].filter(b=>b.offsetParent); b.forEach(x=>x.click()); return b.length;}})()"): break
        time.sleep(.35)
    abre_rid('at:Adubação a lanço|Adubação de cobertura'); fa = form(); fecha()
    chk('atividade em "ha" (uma passada por cultivo) no formulário Rendimento', re.match(r'^[\d.]+(,\d+)? ha · ', fa.get('area_c', '')), fa.get('area_c'))
    c.goto(URL.replace('#', '?r=2#'), 1.6)
    ordena('Custo R$/ha'); cu = [r[5] for r in linhas() if len(r) == NCOL and r[0] != 'Total']
    chk('ordenar Custo R$/ha crescente (número, não texto): R$ 3,40/ha-op primeiro, R$ 662,86/ha-op por último', cu[:1] == ['R$ 3,40/ha-op'] and cu[-1:] == ['R$ 662,86/ha-op'], cu)
    filtra('Conjunto', ['Trator 02 MF 7719 + Pulverizador PJ-3030 36 m']); r1 = [r for r in linhas() if len(r) == NCOL and r[0] != 'Total']
    chk('filtro Conjunto (valor exato da célula): só a Pulverização', r1 and all(r[0].startswith('Pulverização') for r in r1), [r[0] for r in r1])
    limpa(); filtra('Situação', ['Janela não informada']); r2 = [r for r in linhas() if len(r) == NCOL and r[0] != 'Total']
    chk('filtro Situação = "Janela não informada": as 8 operações', len(r2) == 8, len(r2))
    limpa()
    # busca: o talhão pelo nome (era o filtro da coluna Talhão da antiga etapa 4)
    J(f"""(()=>{{const t={TB}; const box=t.closest('.g2caixa')||t.parentElement.parentElement; const i=(box.querySelector('input[type=search]')||document.querySelector('input[type=search][aria-label="Buscar nesta tabela"]')); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'T2'); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"""); time.sleep(.6)
    fs = [r for r in linhas() if ' · ' in r[0] and r[0][:2] in ('T1', 'T2', 'T3', 'T4', 'T7', 'C1', 'P1', 'P2')]
    chk('busca "T2": só ocorrências do T2 (com operação e atividade que as agrupam)', fs and all(r[0].startswith('T2 ') for r in fs), [r[0] for r in fs][:5])
    # busca pelo dado que saiu da linha (COLUNAS-1): o rendimento "21,60 ha/h" acha a Pulverização
    J(f"""(()=>{{const i=document.querySelector('input[type=search][aria-label="Buscar nesta tabela"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'21,60 ha/h'); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"""); time.sleep(.6)
    br = [r[0] for r in linhas() if len(r) == NCOL and r[0] != 'Total']
    chk('COLUNAS-1 · busca "21,60 ha/h" (rendimento fora da linha) ainda acha a Pulverização', br and br[0].startswith('Pulverização'), br[:4])
    J(f"""(()=>{{const i=document.querySelector('input[type=search][aria-label="Buscar nesta tabela"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,''); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"""); time.sleep(.4)
    # Data real: operação com a faixa de meses; ocorrência com a data (dd/mm/aaaa)
    pu = next((r for r in linhas() if r[0].startswith('Pulverização')), None)
    chk('Data: Pulverização "set/26 – jan/27" (faixa real de meses da operação)', pu and pu[2] == 'set/26 – jan/27', pu)
    # TF03 na etapa única (C22): Adubação de cobertura 24 → 12 m, só esta atividade: 9,00 ha/h e R$ 25,89/ha na mesma linha; a operação "varia"
    J(f"(()=>{{const r=({TB}).querySelector('[role=row][data-rid=\"op:Adubação a lanço\"]'); const b=r&&r.querySelector('.g2car'); if(b&&b.getAttribute('aria-expanded')!=='true') b.click();}})()"); time.sleep(.4)
    J(f"(()=>{{const r=({TB}).querySelector('[role=row][data-rid=\"at:Adubação a lanço|Adubação de cobertura\"]'); [...r.querySelectorAll('[role=cell]')].find(z=>z.innerText.trim()&&!z.querySelector('button')).click();}})()"); time.sleep(.5)
    J("""(()=>{const l=document.querySelector('aside [id$="_larg"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(l,'12'); l.dispatchEvent(new Event('input',{bubbles:true}));})()"""); time.sleep(.3)
    J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); time.sleep(.8)
    ca = next((r for r in linhas() if r[0] == 'Adubação de cobertura'), None)
    abre_rid('at:Adubação a lanço|Adubação de cobertura'); fc = form(); fecha()
    abre_rid('op:Adubação a lanço'); op_form = J("!![...document.querySelectorAll('aside[role=dialog]')].find(x=>x.offsetParent)"); fecha()
    # COLUNAS-1: o rendimento saiu da linha; a atividade mostra 9,00 ha/h no formulário e o R$/ha na linha; a operação, com rendimento que varia
    # entre as atividades, não abre um formulário único (o toque só expande, como antes o "varia" na célula)
    chk('TF03 Adubação de cobertura 24 → 12 m (só esta): 9,00 ha/h no formulário e R$ 25,89/ha na linha; a operação com rendimento que varia só expande',
        ca and ca[5] == 'R$ 25,89/ha' and fc.get('rend_c') == '9,00' and not op_form, (ca, fc.get('rend_c'), op_form))
    chk('sem erro de script (1440)', not J("window.__e"), J("window.__e"))
    # ---------------- incremento 2b: etapas 2 e 4 (demanda de insumos) ----------------
    def TBF(h): return "[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&[...t.querySelectorAll('[role=columnheader]')].some(h=>h.innerText.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim().replace(/ · \\d+$/,'').toUpperCase()===%s))" % json.dumps(h)
    def dicts():
        hs = [x.upper() for x in heads()]; return [dict(zip(hs, [t.replace('▾', '').replace('▸', '').strip() for t in r])) for r in linhas()]
    def expande():
        for _ in range(4):
            if not J(f"(()=>{{const b=[...({TB}).querySelectorAll('button[aria-label^=\"Expandir\"]')].filter(b=>b.offsetParent); b.forEach(x=>x.click()); return b.length;}})()"): break
            time.sleep(.35)
    # etapa 2: cultivos
    c.goto(URL.replace('passo=operacoes', 'passo=cultivos'), 1.6); TB = TBF('TALHÃO OU PARCELA'); h2 = [x.upper() for x in heads()]; d2 = dicts(); shot('saf2-1440')
    # colunas essenciais (proprietário, 10/10; COLUNAS-1): 16 → 8; Meta, Versão, Variedade, Ajustes, Ocupa até e Fim por no formulário do cultivo,
    # Tipo sai (a árvore diz), a Safra de outra ocupação vira link na célula de identificação. A unidade continua junto do valor (05/10)
    C2 = ['TALHÃO OU PARCELA', 'SITUAÇÃO', 'ÁREA LIVRE', 'LIVRE A PARTIR DE', 'ÁREA', 'CULTURA', 'PLANO AGRONÔMICO', 'PLANTIO']
    FORA2 = ('TIPO', 'META', 'VERSÃO', 'AJUSTES LOCAIS', 'OCUPA ATÉ', 'FIM POR', 'SAFRA', 'VARIEDADE', 'UNIDADE DA META', 'PLANO E AJUSTES')
    chk('2b etapa 2: as 8 colunas essenciais, nesta ordem; nenhuma das que saíram (negativa)', h2 == C2 and not any(k in h2 for k in FORA2), h2)
    t7 = next((r for r in d2 if r.get('TALHÃO OU PARCELA', '').startswith('T7')), {})
    abre_rid(J(f"(()=>{{const r=[...({TB}).querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent).find(x=>/^T7\\b/.test(x.innerText.trim())); return r?r.getAttribute('data-rid'):'';}})()") or ''); f7 = form(); fecha()
    chk('2b T7 no formulário do cultivo: meta 45 em t/ha/ano e versão aplicada v3; o plano na linha sem a versão colada',
        f7.get('meta') == '45' and f7.get('unm_txt') == 't/ha/ano' and f7.get('ver_txt', '').startswith('v3 ') and 'v3' not in t7.get('PLANO AGRONÔMICO', 'v3'), (f7, t7))
    # filtros das colunas que saíram não existem mais (nem chip órfão); o filtro de Cultura corta as linhas
    sem = J(f"['Meta','Tipo','Versão','Safra','Variedade'].filter(k=>({TB}).querySelector('button[aria-label=\"Filtrar '+k+'\"]'))") or []
    chk('2b sem filtro de coluna para Meta, Tipo, Versão, Safra e Variedade (saíram com a coluna)', sem == [], sem)
    filtra('Cultura', ['Café']); d = [r for r in dicts() if r.get('CULTURA')]
    chk('2b filtro Cultura = Café: só o C1, menos linhas que sem filtro', [(r.get('TALHÃO OU PARCELA', '').split(' ')[0], r.get('CULTURA', '')) for r in d] == [('C1', 'Café')] and len(d) < len([r for r in d2 if r.get('CULTURA')]), [(r.get('TALHÃO OU PARCELA', ''), r.get('CULTURA', '')) for r in d])
    limpa()
    # meta decimal: o formulário guarda e mostra o valor exato ("62,5" em sc/ha), sem arredondar; a busca acha o T2 pela meta (saiu da linha)
    J(f"(()=>{{const r=[...({TB}).querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent).find(x=>/^T2\\b/.test(x.innerText.trim())); r.querySelector('[role=cell]:nth-child(2)').click();}})()"); time.sleep(.5)
    J("""(()=>{const i=document.querySelector('aside [id$="_meta"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'62,5'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"""); time.sleep(.2)
    J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); time.sleep(.6)
    rid2 = J(f"(()=>{{const r=[...({TB}).querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent).find(x=>/^T2\\b/.test(x.innerText.trim())); return r?r.getAttribute('data-rid'):'';}})()") or ''
    abre_rid(rid2); f2 = form(); fecha()
    J(f"""(()=>{{const i=({TB}).closest('.g2caixa').querySelector('input[type=search]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'62,5 sc/ha'); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"""); time.sleep(.6)
    bm = [r.get('TALHÃO OU PARCELA', '').split(' ')[0] for r in dicts() if r.get('CULTURA')]
    J(f"""(()=>{{const i=({TB}).closest('.g2caixa').querySelector('input[type=search]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,''); i.dispatchEvent(new Event('input',{{bubbles:true}}));}})()"""); time.sleep(.4)
    chk('2b meta 62,5 salva no T2: o formulário mostra "62,5" em sc/ha (sem arredondar para 63) e a busca "62,5 sc/ha" acha só o T2', f2.get('meta') == '62,5' and f2.get('unm_txt') == 'sc/ha' and bm == ['T2'], (f2.get('meta'), f2.get('unm_txt'), bm))
    # etapa 4: demanda de insumos
    c.goto(URL.replace('passo=operacoes', 'passo=demanda'), 1.6); TB = TBF('FALTA EM'); expande(); d6 = dicts(); h6 = [x.upper() for x in heads()]; shot('saf6-1440')
    mp = next((r for r in d6 if r.get('INSUMO') == 'MAP 11-52'), {})
    chk('2b etapa 4 (demanda): MAP 11-52 com necessidade "62.500 kg" | falta 18/10/2026 | Em cotação | SOL-2026-07 em colunas próprias',
        [mp.get(k) for k in ('NECESSIDADE LÍQUIDA', 'FALTA EM', 'SITUAÇÃO', 'SOLICITAÇÃO')] == ['62.500 kg', '18/10/2026', 'Em cotação', 'SOL-2026-07'], mp)
    QT6 = ('NECESSIDADE LÍQUIDA', 'DEMANDA BRUTA', 'ESTOQUE APTO', 'RECEBIMENTOS PREVISTOS', 'JÁ REALIZADO', 'USADO ANTES DA COMPRA', 'RESERVADO', 'RECEBIDO APÓS A FALTA', 'A COMPLEMENTAR')
    folhas6 = [r for r in d6 if r.get('FALTA EM') is not None and r.get('SITUAÇÃO') and r.get('INSUMO') and not r.get('INSUMO', '').endswith(('insumos', 'insumo'))]
    # cada quantidade mostrada leva a unidade; '—' só onde não há valor; o preço leva a unidade do insumo ("R$ 3,90/kg")
    sem_un = [(r.get('INSUMO'), k, r.get(k)) for r in folhas6 for k in QT6 if r.get(k, '—') != '—' and not re.match(r'^[\d.]+(,\d+)? (kg|L|un|t|sc)$', r.get(k, ''))]
    sem_un += [(r.get('INSUMO'), 'PREÇO', r.get('PREÇO')) for r in folhas6 if not re.match(r'^R\$ [\d.]+,\d{2}/(kg|L|un|t|sc)$', r.get('PREÇO', ''))]
    chk('2b etapa 4 (demanda): cada quantidade com a unidade junto ("152.500 kg", "610,0 L"), sem coluna Unidade e sem "falta em" no texto',
        folhas6 and not sem_un and 'UNIDADE' not in h6 and not any('falta em' in v for r in d6 for v in r.values()), sem_un[:3])
    filtra('Necessidade líquida', ['62.500 kg']); d = [r for r in dicts() if r.get('INSUMO') and not r.get('INSUMO', '').endswith(('insumos', 'insumo'))]
    chk('2b filtro Necessidade líquida = "62.500 kg" (o filtro usa o texto da célula, com a unidade): só o MAP 11-52', [r.get('INSUMO') for r in d] == ['MAP 11-52'], [r.get('INSUMO') for r in d])
    limpa(); expande(); filtra('Grupo', ['Herbicidas']); d = [r for r in dicts() if r.get('INSUMO') and not r.get('INSUMO', '').endswith(('insumos', 'insumo'))]
    chk('2b filtro Grupo = Herbicidas: só os herbicidas', d and all(r.get('GRUPO', '') == 'Herbicidas' for r in d), sorted({r.get('INSUMO', '') for r in d}))
    limpa(); expande(); ordena('Necessidade líquida', desc=True); fe = [r.get('NECESSIDADE LÍQUIDA', '') for r in dicts() if r.get('GRUPO') == 'Fertilizantes' and r.get('NECESSIDADE LÍQUIDA')]
    chk('2b ordenar Necessidade líquida decrescente nos fertilizantes: "62.500 kg" primeiro, "0 kg" por último (ordem pelo número)',
        fe and fe[0] == '62.500 kg' and fe[-1] == '0 kg' and [num(x.split(' ')[0]) for x in fe] == sorted([num(x.split(' ')[0]) for x in fe], reverse=True), fe)
    chk('sem erro de script (etapas 2 e 4)', not J("window.__e"), J("window.__e"))
    TB = TBF('OPERAÇÃO › ATIVIDADE › TALHÃO')
    # 390 px
    c.aparelho(390, 844, 2, True); c.goto(URL.replace('#', '?r=390#'), 1.6)
    w = J("[document.documentElement.scrollWidth, innerWidth]"); shot('saf3-390'); print('   cabeçalhos 390:', heads()[:3])
    chk('390 px: a página não rola na horizontal (a tabela rola dentro da caixa) e o cabeçalho Operação › atividade › talhão está à vista', w[0] <= w[1] + 1 and [x.upper() for x in heads()[:1]] == ['OPERAÇÃO › ATIVIDADE › TALHÃO'], w)
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
