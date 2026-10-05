# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO-20261004 v2 (5983172395), incremento 2a: Planejar safra, etapa 3 (Rendimentos), uma variável por coluna.
TF03: Operação, Atividade, Modo, Largura, Velocidade, Eficiência, Rendimento, custos, Parte, Trabalha, Janela e Planos em colunas próprias;
cada uma filtra (menu da coluna, valor exato) e ordena pelo valor tipado; a árvore operação → atividade → configuração continua; R$/kg só
na colheita e fora do R$/ha; editar a largura recalcula o rendimento na mesma linha; 390 px sem rolagem da página.
Uso: python3 tabelas_saf_test.py [pasta de capturas]   (< 90 s)"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
OUT = sys.argv[1] if len(sys.argv) > 1 else None
if OUT: os.makedirs(OUT, exist_ok=True)
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ') + n + (' · ' + str(info)[:300] if info != '' else ''))

p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
URL = f'http://127.0.0.1:{p}/SAF.dc.html#saf=S2627&etapa=3'
COLS = ['Operação', 'Atividade', 'Conjunto', 'Rendimento (ha/h)', 'Custo (R$/h)', 'Custo (R$/ha)', 'Custo (R$/kg)', 'Modo', 'Largura (m)', 'Velocidade (km/h)',
        'Eficiência (%)', 'Parte da área (%)', 'Trabalha', 'Janela (h por talhão)', 'Planos']
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
    chk('TF03 cabeçalhos: uma variável por coluna, unidade no cabeçalho', [x.upper() for x in h] == [x.upper() for x in COLS], h)
    folhas = [r for r in rs if len(r) == 15 and r[ix('Rendimento (ha/h)')] not in ('',)]
    chk('TF03 nenhuma célula junta duas medidas ("12 m × 7 km/h", "R$/ha · R$/kg", "Parte: …")',
        not any(' m × ' in x or 'R$/kg' in x or x.startswith('Parte:') for r in rs for x in r), [r for r in rs if any(' m × ' in x or 'R$/kg' in x for x in r)][:2])
    pl = [r for r in rs if r[0] == 'Plantio']
    chk('árvore preservada: Plantio → Plantio e adubação de base (2 configurações) → 2 configurações com Parte "pelo rendimento" e Trabalha "Ao mesmo tempo"',
        len(pl) == 4 and '2 configurações' in pl[1][1] and all(r[ix('Parte da área (%)')] == 'pelo rendimento' and r[ix('Trabalha')] == 'Ao mesmo tempo' for r in pl[2:]), pl)
    col = [r for r in folhas if r[1] == 'Colheita' and r[0].startswith('Colheita')]
    out = [r for r in folhas if not r[0].startswith('Colheita')]
    chk('TF03 Custo (R$/kg) só na colheita, em coluna própria; o R$/ha fica só com o número',
        col and all(r[ix('Custo (R$/kg)')] not in ('—', '') for r in col) and all(r[ix('Custo (R$/kg)')] == '—' for r in out) and all(r[ix('Custo (R$/ha)')].replace('.', '').replace(',', '').isdigit() for r in folhas),
        [(r[0], r[ix('Custo (R$/ha)')], r[ix('Custo (R$/kg)')]) for r in col])
    inf = [r for r in folhas if r[ix('Modo')] == 'Informado']
    chk('TF03 Modo "Informado": Largura, Velocidade e Eficiência vazias (—), rendimento informado', inf and all(r[ix('Largura (m)')] == r[ix('Velocidade (km/h)')] == r[ix('Eficiência (%)')] == '—' and r[ix('Rendimento (ha/h)')] != '—' for r in inf), inf[:2])
    # filtro por valor exato em cada coluna separada
    filtra('Operação', ['Plantio']); r1 = linhas()
    chk('TF03 filtro Operação = Plantio: só a árvore do Plantio (grupo, atividade e 2 configurações)', r1 and all(r[0] == 'Plantio' for r in r1) and len(r1) == 4, [r[:2] for r in r1])
    limpa(); filtra('Modo', ['Informado']); r2 = [r for r in linhas() if r[ix('Modo')] in ('Informado', 'Largura × velocidade')]
    chk('TF03 filtro Modo = Informado: só configurações informadas (TSI, café, poda, fertirrigação…)', r2 and all(r[ix('Modo')] == 'Informado' for r in r2), sorted({r[0] for r in r2}))
    limpa(); filtra('Largura (m)', ['36']); r3 = [r for r in linhas() if len(r) == 15 and r[ix('Modo')]]
    chk('TF03 filtro Largura (m) = 36: só o pulverizador de 36 m', r3 and all(r[ix('Largura (m)')] == '36' and r[0] == 'Pulverização' for r in r3), len(r3))
    limpa(); filtra('Planos', ['Café arábica produção']); r4 = [r for r in linhas() if len(r) == 15 and r[ix('Modo')]]
    chk('TF03 filtro Planos (valor exato): só as atividades do plano do café', r4 and all(r[ix('Planos')] == 'Café arábica produção' for r in r4), sorted({r[1] for r in r4}))
    limpa()
    # ordenar pelo valor tipado: dentro do grupo Plantio, as configurações por largura (6 antes de 12) e por custo/ha decrescente
    ordena('Largura (m)'); pl = [r for r in linhas() if r[0] == 'Plantio'][2:]
    chk('TF03 ordenar Largura (m) crescente: 6 antes de 12 (número, não texto)', [r[ix('Largura (m)')] for r in pl] == ['6', '12'], [r[ix('Largura (m)')] for r in pl])
    ordena('Custo (R$/ha)', desc=True); fl = [r[ix('Custo (R$/ha)')] for r in linhas() if r[0] == 'Plantio'][2:]
    chk('TF03 ordenar Custo (R$/ha) decrescente: 109,40 antes de 58,20 (número, não texto)', fl == ['109,40', '58,20'], fl)
    # editar a largura recalcula rendimento e custo na mesma linha (o formulário segue igual)
    J(f"(()=>{{const r=[...({TB}).querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent).find(x=>[...x.querySelectorAll('[role=cell]')][1].innerText.trim()==='Calagem'); r.querySelector('[role=cell] span').click();}})()"); time.sleep(.5)
    J("""(()=>{const i=document.querySelector('aside [id$="_esc"]'); if(i){ Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,'Só esta atividade'); i.dispatchEvent(new Event('change',{bubbles:true})); }
      const l=document.querySelector('aside [id$="_larg"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(l,'12'); l.dispatchEvent(new Event('input',{bubbles:true}));})()"""); time.sleep(.3)
    J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); time.sleep(.6)
    ca = next((r for r in linhas() if r[1].startswith('Calagem')), None); print('   painel/aviso:', (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '')[:200].replace('\n',' | '), '|', J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')"))
    chk('editar Largura 24 → 12 m na Calagem: Rendimento 9,00 ha/h e Custo 25,89 R$/ha na mesma linha, marcada "ajustado nesta safra"', ca and 'ajustado nesta safra' in ca[1] and ca[ix('Largura (m)')] == '12' and ca[ix('Rendimento (ha/h)')] == '9,00' and ca[ix('Custo (R$/ha)')] == '25,89', ca)
    chk('sem erro de script (1440)', not J("window.__e"), J("window.__e"))
    # ---------------- incremento 2b: etapas 2, 4 e 6 ----------------
    def TBF(h): return "[...document.querySelectorAll('[role=table]')].find(t=>t.offsetParent&&[...t.querySelectorAll('[role=columnheader]')].some(h=>h.innerText.replace(/[⇅▾▴▼▲]/g,'').replace(/\\s+/g,' ').trim().replace(/ · \\d+$/,'').toUpperCase()===%s))" % json.dumps(h)
    def dicts():
        hs = [x.upper() for x in heads()]; return [dict(zip(hs, [t.replace('▾', '').replace('▸', '').strip() for t in r])) for r in linhas()]
    def expande():
        for _ in range(4):
            if not J(f"(()=>{{const b=[...({TB}).querySelectorAll('button[aria-label^=\"Expandir\"]')].filter(b=>b.offsetParent); b.forEach(x=>x.click()); return b.length;}})()"): break
            time.sleep(.35)
    # etapa 2: cultivos
    c.goto(URL.replace('etapa=3', 'etapa=2'), 1.6); TB = TBF('TIPO'); h2 = [x.upper() for x in heads()]; d2 = dicts(); shot('saf2-1440')
    chk('2b etapa 2: Tipo, Área livre, Unidade da meta, Plano, Versão e Ajustes em colunas próprias',
        all(k in h2 for k in ('TALHÃO OU PARCELA', 'TIPO', 'ÁREA (HA)', 'ÁREA LIVRE (HA)', 'META', 'UNIDADE DA META', 'PLANO AGRONÔMICO', 'VERSÃO', 'AJUSTES LOCAIS')) and not any('PLANO E AJUSTES' == x for x in h2), h2)
    t7 = next((r for r in d2 if r.get('TALHÃO OU PARCELA', '').startswith('T7')), {})
    chk('2b T7: meta 45 e unidade t/ha/ano separadas; plano sem a versão colada (v3 na coluna Versão)', t7.get('META') == '45' and t7.get('UNIDADE DA META') == 't/ha/ano' and t7.get('VERSÃO') == 'v3' and 'v3' not in t7.get('PLANO AGRONÔMICO', ''), t7)
    filtra('Unidade da meta', ['t/ha/ano']); d = [r for r in dicts() if r.get('CULTURA')]
    chk('2b filtro Unidade da meta = t/ha/ano: só cultivos com meta em t/ha/ano (mamão)', d and all(r.get('UNIDADE DA META', '') == 't/ha/ano' for r in d), [(r.get('TALHÃO OU PARCELA', ''), r.get('UNIDADE DA META', '')) for r in d])
    limpa(); filtra('Tipo', ['Parcela']); d = [r for r in dicts() if r.get('CULTURA')]
    chk('2b filtro Tipo = Parcela: as parcelas T1-A e T1-B (com o talhão T1 que as agrupa)', sorted(r.get('TALHÃO OU PARCELA', '').split(' ')[0] for r in d if r.get('TIPO', '') == 'Parcela') == ['T1-A', 'T1-B'], [(r.get('TALHÃO OU PARCELA', ''), r.get('TIPO', '')) for r in d])
    limpa()
    # etapa 4: plano operacional
    c.goto(URL.replace('etapa=3', 'etapa=4'), 1.6); TB = TBF('GATILHO'); expande(); d4 = dicts(); shot('saf4-1440')
    des = next((r for r in d4 if r.get('OPERAÇÃO › ATIVIDADE › CULTIVO', '').startswith('Dessecação pré-plantio')), {})
    oc = [r for r in d4 if r.get('TALHÃO') == 'T2']; print('   etapa4 cabeçalhos:', heads()[-3:], 'n linhas', len(d4), 'T2:', [(r.get('GATILHO'), r.get('DATA')) for r in oc])
    chk('2b etapa 4: Gatilho (regra da atividade) e Data (da ocorrência) separados', des.get('GATILHO') == 'DAP −20' and des.get('DATA') in ('', '—') and oc and all(r.get('GATILHO', '') in ('—', '') and len(r.get('DATA', '')) == 10 for r in oc), (des, oc[:1]))
    filtra('Talhão', ['T2']); d = dicts(); folhas = [r for r in d if r.get('TALHÃO')]
    chk('2b filtro Talhão = T2: só ocorrências do T2 (com operação e atividade que as agrupam)', folhas and all(r.get('TALHÃO', '') == 'T2' for r in folhas), len(folhas))
    limpa()
    # etapa 6: demanda de insumos
    c.goto(URL.replace('etapa=3', 'etapa=6'), 1.6); TB = TBF('UNIDADE'); expande(); d6 = dicts(); shot('saf6-1440')
    mp = next((r for r in d6 if r.get('INSUMO') == 'MAP 11-52'), {})
    chk('2b etapa 6: MAP 11-52 com necessidade 62.500 | kg | falta 18/10/2026 | Em cotação | SOL-2026-07 em colunas próprias',
        [mp.get(k) for k in ('NECESSIDADE LÍQUIDA', 'UNIDADE', 'FALTA EM', 'SITUAÇÃO', 'SOLICITAÇÃO')] == ['62.500', 'kg', '18/10/2026', 'Em cotação', 'SOL-2026-07'], mp)
    chk('2b etapa 6: nenhuma quantidade com unidade colada nem "falta em" no texto', not any(' kg' in v or ' L' == v[-2:] or 'falta em' in v for r in d6 for k, v in r.items() if k not in ('UNIDADE', 'INSUMO', 'SITUAÇÃO')), [r for r in d6 if any(' kg' in v for v in r.values())][:1])
    filtra('Unidade', ['L']); d = [r for r in dicts() if r.get('UNIDADE') in ('L', 'kg')]
    chk('2b filtro Unidade = L: só insumos em litros', d and all(r.get('UNIDADE', '') == 'L' for r in d), sorted({r.get('INSUMO', '') for r in d}))
    limpa(); expande(); ordena('Necessidade líquida', desc=True); print('   etapa6 cabeçalhos:', heads()[:6], dicts()[:2]); fe = [r.get('NECESSIDADE LÍQUIDA', '') for r in dicts() if r.get('GRUPO') == 'Fertilizantes' and r.get('UNIDADE')]
    chk('2b ordenar Necessidade líquida decrescente nos fertilizantes: 62.500 primeiro, 0 por último (número)', fe and fe[0] == '62.500' and fe[-1] == '0' and [num(x) for x in fe] == sorted([num(x) for x in fe], reverse=True), fe)
    chk('sem erro de script (etapas 2, 4 e 6)', not J("window.__e"), J("window.__e"))
    TB = TBF('OPERAÇÃO')
    # 390 px
    c.aparelho(390, 844, 2, True); c.goto(URL, 1.6)
    w = J("[document.documentElement.scrollWidth, innerWidth]"); shot('saf3-390'); print('   cabeçalhos 390:', heads()[:3])
    chk('390 px: a página não rola na horizontal (a tabela rola dentro da caixa) e o cabeçalho Operação está à vista', w[0] <= w[1] + 1 and [x.upper() for x in heads()[:1]] == ['OPERAÇÃO'], w)
finally:
    c.close(); srv.terminate()
print(f'RESULTADO: {len(OK)}/{len(OK) + len(FAIL)} ok' + (' · FALHAS: ' + '; '.join(FAIL) if FAIL else ''))
sys.exit(1 if FAIL else 0)
