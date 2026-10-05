# -*- coding: utf-8 -*-
"""Teste real (Chrome) — TABELAS-FOCO-20261004 v2 (5983172395), incremento 2a: Planejar safra, etapa 3 (Rendimentos), uma variável por coluna.
TF03: Operação, Atividade, Modo, Largura, Velocidade, Eficiência, Rendimento, custos, Parte, Trabalha, Janela e Planos em colunas próprias;
cada uma filtra (menu da coluna, valor exato) e ordena pelo valor tipado; a árvore operação → atividade → configuração continua; R$/kg só
na colheita e fora do R$/ha; editar a largura recalcula o rendimento na mesma linha; 390 px sem rolagem da página.
Uso: python3 tabelas_saf_test.py [pasta de capturas]   (< 90 s)"""
import sys, os, time, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from comp_lib import Chrome, servir
OUT = sys.argv[1] if len(sys.argv) > 1 else None
if OUT: os.makedirs(OUT, exist_ok=True)
OK, FAIL = [], []
def chk(n, cond, info=''):
    (OK if cond else FAIL).append(n); print(('  ok  ' if cond else '  FALHOU ') + n + (' · ' + str(info)[:300] if info != '' else ''))

p, srv = servir(os.path.join(HERE, '_render')); c = Chrome(); J = c.js
URL = f'http://127.0.0.1:{p}/SAF.dc.html#saf=S2627&etapa=3'
# incremento 2d (decisão de 05/10/2026): a unidade fixa sai do cabeçalho e vai para a célula ("36 m", "R$ 109,40/ha"); custo como "Custo R$/h"
COLS = ['Operação', 'Atividade', 'Conjunto', 'Rendimento', 'Custo R$/h', 'Custo R$/ha', 'Custo R$/kg', 'Modo', 'Largura', 'Velocidade',
        'Eficiência', 'Parte da área', 'Trabalha', 'Janela por talhão', 'Planos']
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
    chk('TF03 cabeçalhos: uma variável por coluna, sem unidade entre parênteses (a unidade vai na célula)', [x.upper() for x in h] == [x.upper() for x in COLS], h)
    folhas = [r for r in rs if len(r) == 15 and r[ix('Rendimento')] not in ('',)]
    chk('TF03 nenhuma célula junta duas medidas ("12 m × 7 km/h", "R$/ha · R$/kg", "Parte: …")',
        not any(' m × ' in x or 'R$/kg' in x or x.startswith('Parte:') for r in rs for x in r), [r for r in rs if any(' m × ' in x or 'R$/kg' in x for x in r)][:2])
    pl = [r for r in rs if r[0] == 'Plantio']
    chk('árvore preservada: Plantio → Plantio e adubação de base (2 configurações) → 2 configurações com Parte "pelo rendimento" e Trabalha "Ao mesmo tempo"',
        len(pl) == 4 and '2 configurações' in pl[1][1] and all(r[ix('Parte da área')] == 'pelo rendimento' and r[ix('Trabalha')] == 'Ao mesmo tempo' for r in pl[2:]), pl)
    col = [r for r in folhas if r[1] == 'Colheita' and r[0].startswith('Colheita')]
    out = [r for r in folhas if not r[0].startswith('Colheita')]
    chk('TF03 Custo R$/kg só na colheita, em coluna própria ("R$ 0,0606/kg"); Custo R$/ha com o número e a unidade ("R$ 109,40/ha")',
        col and all(re.match(r'^(\w+ )?R\$ [\d.]+,\d+/kg', r[ix('Custo R$/kg')]) for r in col) and all(r[ix('Custo R$/kg')] == '—' for r in out) and all(re.match(r'^R\$ [\d.]+,\d{2}/ha$', r[ix('Custo R$/ha')]) for r in folhas),
        [(r[0], r[ix('Custo R$/ha')], r[ix('Custo R$/kg')]) for r in col])
    unc = [(r[1], k, r[ix(k)]) for r in folhas for k, u in (('Rendimento', 'ha/h'), ('Largura', 'm'), ('Velocidade', 'km/h'), ('Eficiência', '%'), ('Custo R$/h', 'h'))
           if r[ix(k)] not in ('—', '') and not (r[ix(k)].endswith(' ' + u) or (k == 'Custo R$/h' and re.match(r'^R\$ [\d.]+,\d{2}/h$', r[ix(k)])))]
    chk('2d cada valor com a unidade na célula ("4,80 ha/h", "36 m", "7 km/h", "75 %", "R$ 120,00/h")', folhas and not unc, unc[:3])
    inf = [r for r in folhas if r[ix('Modo')] == 'Informado']
    chk('TF03 Modo "Informado": Largura, Velocidade e Eficiência vazias (—), rendimento informado', inf and all(r[ix('Largura')] == r[ix('Velocidade')] == r[ix('Eficiência')] == '—' and r[ix('Rendimento')] != '—' for r in inf), inf[:2])
    # filtro por valor exato em cada coluna separada
    filtra('Operação', ['Plantio']); r1 = linhas()
    chk('TF03 filtro Operação = Plantio: só a árvore do Plantio (grupo, atividade e 2 configurações)', r1 and all(r[0] == 'Plantio' for r in r1) and len(r1) == 4, [r[:2] for r in r1])
    limpa(); filtra('Modo', ['Informado']); r2 = [r for r in linhas() if r[ix('Modo')] in ('Informado', 'Largura × velocidade')]
    chk('TF03 filtro Modo = Informado: só configurações informadas (TSI, café, poda, fertirrigação…)', r2 and all(r[ix('Modo')] == 'Informado' for r in r2), sorted({r[0] for r in r2}))
    limpa(); filtra('Largura', ['36 m']); r3 = [r for r in linhas() if len(r) == 15 and r[ix('Modo')]]
    chk('TF03 filtro Largura = "36 m" (o menu mostra o texto da célula): só o pulverizador de 36 m', r3 and all(r[ix('Largura')] == '36 m' and r[0] == 'Pulverização' for r in r3), len(r3))
    limpa(); filtra('Planos', ['Café arábica produção']); r4 = [r for r in linhas() if len(r) == 15 and r[ix('Modo')]]
    chk('TF03 filtro Planos (valor exato): só as atividades do plano do café', r4 and all(r[ix('Planos')] == 'Café arábica produção' for r in r4), sorted({r[1] for r in r4}))
    limpa()
    # ordenar pelo valor tipado: dentro do grupo Plantio, as configurações por largura (6 antes de 12) e por custo/ha decrescente
    ordena('Largura'); pl = [r for r in linhas() if r[0] == 'Plantio'][2:]
    chk('TF03 ordenar Largura crescente: 6 m antes de 12 m (número, não texto)', [r[ix('Largura')] for r in pl] == ['6 m', '12 m'], [r[ix('Largura')] for r in pl])
    ordena('Custo R$/ha', desc=True); fl = [r[ix('Custo R$/ha')] for r in linhas() if r[0] == 'Plantio'][2:]
    chk('TF03 ordenar Custo R$/ha decrescente: R$ 109,40/ha antes de R$ 58,20/ha (número, não texto)', fl == ['R$ 109,40/ha', 'R$ 58,20/ha'], fl)
    # editar a largura recalcula rendimento e custo na mesma linha (o formulário segue igual)
    J(f"(()=>{{const r=[...({TB}).querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent).find(x=>[...x.querySelectorAll('[role=cell]')][1].innerText.trim()==='Calagem'); r.querySelector('[role=cell] span').click();}})()"); time.sleep(.5)
    J("""(()=>{const i=document.querySelector('aside [id$="_esc"]'); if(i){ Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(i,'Só esta atividade'); i.dispatchEvent(new Event('change',{bubbles:true})); }
      const l=document.querySelector('aside [id$="_larg"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(l,'12'); l.dispatchEvent(new Event('input',{bubbles:true}));})()"""); time.sleep(.3)
    J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); time.sleep(.6)
    ca = next((r for r in linhas() if r[1].startswith('Calagem')), None); print('   painel/aviso:', (J("(document.querySelector('aside[role=dialog]')||{innerText:''}).innerText") or '')[:200].replace('\n',' | '), '|', J("[...document.querySelectorAll('[role=status]')].map(x=>x.innerText).filter(Boolean).join(' | ')"))
    chk('editar Largura 24 → 12 m na Calagem: Rendimento 9,00 ha/h e Custo 25,89 R$/ha na mesma linha, marcada "ajustado nesta safra"', ca and 'ajustado nesta safra' in ca[1] and ca[ix('Largura')] == '12 m' and ca[ix('Rendimento')] == '9,00 ha/h' and ca[ix('Custo R$/ha')] == 'R$ 25,89/ha', ca)
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
    # decisão do proprietário (05/10/2026): a unidade fica junto do valor ("45 t/ha/ano", "62.500 kg"); filtrar unidade não gera valor
    chk('2b etapa 2: Tipo, Área livre, Plano, Versão e Ajustes em colunas próprias; Meta com a unidade junto (sem coluna de unidade)',
        all(k in h2 for k in ('TALHÃO OU PARCELA', 'TIPO', 'ÁREA', 'ÁREA LIVRE', 'META', 'PLANO AGRONÔMICO', 'VERSÃO', 'AJUSTES LOCAIS')) and 'UNIDADE DA META' not in h2 and not any('PLANO E AJUSTES' == x for x in h2), h2)
    t7 = next((r for r in d2 if r.get('TALHÃO OU PARCELA', '').startswith('T7')), {})
    chk('2b T7: meta "45 t/ha/ano" (valor com a unidade); plano sem a versão colada (v3 na coluna Versão)', t7.get('META') == '45 t/ha/ano' and t7.get('VERSÃO') == 'v3' and 'v3' not in t7.get('PLANO AGRONÔMICO', ''), t7)
    filtra('Meta', ['45 t/ha/ano']); d = [r for r in dicts() if r.get('CULTURA')]
    chk('2b filtro Meta = "45 t/ha/ano" (o filtro mostra o valor com a unidade, como a célula): só o T7', d and all(r.get('META', '') == '45 t/ha/ano' for r in d) and d[0].get('TALHÃO OU PARCELA', '').startswith('T7'), [(r.get('TALHÃO OU PARCELA', ''), r.get('META', '')) for r in d])
    limpa(); filtra('Tipo', ['Parcela']); d = [r for r in dicts() if r.get('CULTURA')]
    # o filtro tem de cortar: só parcelas e o talhão que as agrupa ("2 parcelas"), nenhum "Talhão inteiro", menos linhas que sem filtro
    chk('2b filtro Tipo = Parcela: as parcelas T1-A e T1-B (com o talhão T1 que as agrupa), sem talhão inteiro',
        sorted(r.get('TALHÃO OU PARCELA', '').split(' ')[0] for r in d if r.get('TIPO', '') == 'Parcela') == ['T1-A', 'T1-B']
        and all(r.get('TIPO', '') == 'Parcela' or re.match(r'^\d+ parcelas?$', r.get('TIPO', '')) for r in d)
        and len(d) < len([r for r in d2 if r.get('CULTURA')]), [(r.get('TALHÃO OU PARCELA', ''), r.get('TIPO', '')) for r in d])
    limpa()
    # meta decimal: a célula e o filtro mostram o valor exato com a unidade ("62,5 sc/ha"), sem arredondar
    J(f"(()=>{{const r=[...({TB}).querySelectorAll('[role=row].g2ed')].filter(x=>x.offsetParent).find(x=>/^T2\\b/.test(x.innerText.trim())); r.querySelector('[role=cell]:nth-child(2)').click();}})()"); time.sleep(.5)
    J("""(()=>{const i=document.querySelector('aside [id$="_meta"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'62,5'); i.dispatchEvent(new Event('input',{bubbles:true}));})()"""); time.sleep(.2)
    J("[...document.querySelectorAll('aside[role=dialog] button')].find(b=>b.innerText.trim()==='Salvar').click()"); time.sleep(.6)
    t2 = next((r for r in dicts() if r.get('TALHÃO OU PARCELA', '').startswith('T2')), {})
    J(f"({TB}).querySelector('button[aria-label=\"Filtrar Meta\"]').click()"); time.sleep(.4)
    rot = J("[...document.querySelectorAll('[role=dialog] label')].map(l=>l.innerText.replace(/\\s+\\d+$/,'').trim())") or []
    J("(()=>{const b=[...document.querySelectorAll('[role=dialog] button')].find(b=>b.innerText.trim()==='Cancelar'); b&&b.click();})()"); time.sleep(.3)
    chk('2b meta 62,5 salva no T2: célula e filtro mostram "62,5 sc/ha" (sem arredondar para 63)', t2.get('META') == '62,5 sc/ha' and '62,5 sc/ha' in rot and '63 sc/ha' not in rot, (t2.get('META'), rot))
    # etapa 4: plano operacional
    c.goto(URL.replace('etapa=3', 'etapa=4'), 1.6); TB = TBF('GATILHO'); expande(); d4 = dicts(); shot('saf4-1440')
    des = next((r for r in d4 if r.get('OPERAÇÃO › ATIVIDADE › CULTIVO', '').startswith('Dessecação pré-plantio')), {})
    oc = [r for r in d4 if r.get('TALHÃO') == 'T2']; print('   etapa4 cabeçalhos:', heads()[-3:], 'n linhas', len(d4), 'T2:', [(r.get('GATILHO'), r.get('DATA')) for r in oc])
    chk('2b etapa 4: Gatilho (regra da atividade) e Data (da ocorrência) separados', des.get('GATILHO') == 'DAP −20' and des.get('DATA') in ('', '—') and oc and all(r.get('GATILHO', '') in ('—', '') and len(r.get('DATA', '')) == 10 for r in oc), (des, oc[:1]))
    filtra('Talhão', ['T2']); d = dicts(); folhas = [r for r in d if r.get('TALHÃO')]
    chk('2b filtro Talhão = T2: só ocorrências do T2 (com operação e atividade que as agrupam)', folhas and all(r.get('TALHÃO', '') == 'T2' for r in folhas), len(folhas))
    limpa()
    # etapa 6: demanda de insumos
    c.goto(URL.replace('etapa=3', 'etapa=6'), 1.6); TB = TBF('FALTA EM'); expande(); d6 = dicts(); h6 = [x.upper() for x in heads()]; shot('saf6-1440')
    mp = next((r for r in d6 if r.get('INSUMO') == 'MAP 11-52'), {})
    chk('2b etapa 6: MAP 11-52 com necessidade "62.500 kg" | falta 18/10/2026 | Em cotação | SOL-2026-07 em colunas próprias',
        [mp.get(k) for k in ('NECESSIDADE LÍQUIDA', 'FALTA EM', 'SITUAÇÃO', 'SOLICITAÇÃO')] == ['62.500 kg', '18/10/2026', 'Em cotação', 'SOL-2026-07'], mp)
    QT6 = ('NECESSIDADE LÍQUIDA', 'DEMANDA BRUTA', 'ESTOQUE APTO', 'RECEBIMENTOS PREVISTOS', 'JÁ REALIZADO', 'USADO ANTES DA COMPRA', 'RESERVADO', 'RECEBIDO APÓS A FALTA', 'A COMPLEMENTAR')
    folhas6 = [r for r in d6 if r.get('FALTA EM') is not None and r.get('SITUAÇÃO') and r.get('INSUMO') and not r.get('INSUMO', '').endswith(('insumos', 'insumo'))]
    # cada quantidade mostrada leva a unidade; '—' só onde não há valor; o preço leva a unidade do insumo ("R$ 3,90/kg")
    sem_un = [(r.get('INSUMO'), k, r.get(k)) for r in folhas6 for k in QT6 if r.get(k, '—') != '—' and not re.match(r'^[\d.]+(,\d+)? (kg|L|un|t|sc)$', r.get(k, ''))]
    sem_un += [(r.get('INSUMO'), 'PREÇO', r.get('PREÇO')) for r in folhas6 if not re.match(r'^R\$ [\d.]+,\d{2}/(kg|L|un|t|sc)$', r.get('PREÇO', ''))]
    chk('2b etapa 6: cada quantidade com a unidade junto ("152.500 kg", "610,0 L"), sem coluna Unidade e sem "falta em" no texto',
        folhas6 and not sem_un and 'UNIDADE' not in h6 and not any('falta em' in v for r in d6 for v in r.values()), sem_un[:3])
    filtra('Necessidade líquida', ['62.500 kg']); d = [r for r in dicts() if r.get('INSUMO') and not r.get('INSUMO', '').endswith(('insumos', 'insumo'))]
    chk('2b filtro Necessidade líquida = "62.500 kg" (o filtro usa o texto da célula, com a unidade): só o MAP 11-52', [r.get('INSUMO') for r in d] == ['MAP 11-52'], [r.get('INSUMO') for r in d])
    limpa(); expande(); filtra('Grupo', ['Herbicidas']); d = [r for r in dicts() if r.get('INSUMO') and not r.get('INSUMO', '').endswith(('insumos', 'insumo'))]
    chk('2b filtro Grupo = Herbicidas: só os herbicidas', d and all(r.get('GRUPO', '') == 'Herbicidas' for r in d), sorted({r.get('INSUMO', '') for r in d}))
    limpa(); expande(); ordena('Necessidade líquida', desc=True); fe = [r.get('NECESSIDADE LÍQUIDA', '') for r in dicts() if r.get('GRUPO') == 'Fertilizantes' and r.get('NECESSIDADE LÍQUIDA')]
    chk('2b ordenar Necessidade líquida decrescente nos fertilizantes: "62.500 kg" primeiro, "0 kg" por último (ordem pelo número)',
        fe and fe[0] == '62.500 kg' and fe[-1] == '0 kg' and [num(x.split(' ')[0]) for x in fe] == sorted([num(x.split(' ')[0]) for x in fe], reverse=True), fe)
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
