# -*- coding: utf-8 -*-
"""EX-26 · procura cada indicador nos textos capturados por p10_ex26.py (executado sobre a saída do navegador; sem navegador aqui).
Saída: out/p11_ex26_busca.txt (indicador → tela [menu|oculta] → linhas que casam)."""
import os, re, json
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'ex26')
idx = json.load(open(os.path.join(D, '_indice.json'), encoding='utf-8'))
IND = {
 'AGR % aplicações acima do NC e na janela': r'acima do NC|aplicar até|% do NC',
 'AGR eficácia produto × alvo': r'efic[áa]cia|redução observada|Controle \d+ ?%|Redução \d+ ?%',
 'AGR custo de controle R$/ha': r'R\$ ?[\d.,]+ ?/ ?ha|custo de controle|R\$/ha',
 'AGR % recomendações com registro válido': r'sem registro|registro (válido|vencido)|registrado para|não registrado',
 'AGR % vistorias no prazo': r'[Vv]istoria atrasada|atrasad[ao]s?\b.*vistori|vistorias? (no prazo|atrasad)',
 'PCP % área na janela': r'(fora|dentro) da janela|na janela|janela (vencida|perdida)',
 'PCP aderência plano × executado': r'[Pp]lanejado ?[×x] ?realizado|[Pp]revisto ?[×x] ?realizado|aderência|[Pp]lano ?[×x] ?(executado|real)',
 'PCP déficit de capacidade antecipado': r'[Dd]éficit [\d.,]+ ?h|capacidade líquida|[Oo]ciosidade',
 'PCP tempo impedimento → liberação': r'impedid[ao]s? h[áa]|desde \d|dias impedid|tempo (até|de) libera',
 'EXE ha/h real × padrão': r'ha/h',
 'EXE horas paradas por causa': r'[Hh]oras? parad|parada[s]? por|[Pp]aradas?\b.*(causa|motivo)',
 'EXE custo por ha da operação': r'[Cc]usto (R\$/ha|por ha|/ha)|R\$ ?[\d.,]+/ha',
 'EXE % área dentro das condições': r'Delta ?T|condições de aplicação|vento|inversão',
 'IRR lâmina aplicada × necessidade': r'[Ll]âmina|[Nn]ecessidade (bruta|líquida)|mm líquidos',
 'IRR horas em ponta': r'[Pp]onta',
 'IRR % da outorga usada': r'[Oo]utorga',
 'SUP % demanda coberta antes da janela': r'[Ff]alta a partir|coberto|[Cc]obertura|chega depois da falta',
 'SUP ruptura que parou O.S.': r'[Rr]uptura|aguarda a compra|[Ii]nsumo no [Ee]stoque|falta de insumo|saldo insuficiente',
 'SUP economia realizada': r'[Ee]conomia',
 'SUP capital parado': r'[Cc]apital (parado|sem demanda|empatado)|sem demanda',
 'SUP perda por validade': r'[Vv]encid[oa]|[Vv]alidade|[Vv]encendo',
 'SUP acuracidade de inventário': r'[Aa]curacidade|[Ii]nventário|[Cc]ontagem|[Aa]juste de inventário',
 'MAN disponibilidade da frota': r'[Dd]isponibilidade',
 'MAN MTBF/MTTR': r'MTBF|MTTR',
 'MAN % preventiva': r'[Cc]umprimento de preventiva|% (de )?preventiva|[Pp]reventiva',
 'MAN backlog em horas': r'[Bb]acklog|horas? de backlog|carga da oficina',
 'MAN custo por hora': r'[Cc]usto (por hora|R\$/h|/h)|R\$ ?[\d.,]+/h',
 'COL perda na colheita': r'[Pp]erda (na colheita|de colheita)|[Pp]erdas?',
 'COL erro da previsão (WAPE)': r'WAPE|[Ee]rro da previsão|[Vv]iés',
 'COL % classe A': r'[Cc]lasse A|[Tt]ipo (1|7|6)|[Cc]lassifica',
 'COL % lotes aprovados': r'[Ll]otes? (aprovad|liberad|bloquead|reprovad)|[Aa]pto',
 'COL quebra': r'[Qq]uebra',
 'COM % vendido × custo coberto': r'[Vv]endido|[Ll]ivre para vender|custo coberto',
 'COM preço contra referência': r'[Rr]eferência de mercado|[Pp]reço médio',
 'COM basis': r'[Bb]asis',
 'COM OTIF': r'OTIF',
 'COM frete por tonelada': r'[Ff]rete|R\$ ?[\d.,]+/t\b',
 'GES custo por saca e margem/ha por talhão': r'R\$ ?[\d.,]+ ?/ ?sc|[Cc]usto (por saca|unitário|/sc)|[Mm]argem',
 'GES desvio decomposto': r'[Dd]esvio|[Vv]ariação (de preço|de consumo)|preço ?[×x] ?quantidade',
 'GES caixa de 13 semanas': r'13 semanas|[Ff]luxo de caixa|[Cc]aixa',
}
out = []
for ind, rx in IND.items():
    out.append(f'\n## {ind}   /{rx}/')
    for fn in sorted(os.listdir(D)):
        if not fn.endswith('.txt'): continue
        k = fn[:-4]; t = open(os.path.join(D, fn), encoding='utf-8').read()
        ls = [l.strip() for l in t.split('\n') if re.search(rx, l)]
        if not ls: continue
        oc = idx.get(k, idx.get(k.split('_')[0] + ('_' + k.split('_')[1] if k.startswith('IN-04') else ''), {})).get('oculta')
        if k.startswith('MA_') or k.startswith('IN-04'): oc = False
        uniq = []
        for l in ls:
            if l not in uniq: uniq.append(l)
        out.append(f"  [{'oculta' if oc else 'menu'}] {k}: " + ' ‖ '.join(x[:150] for x in uniq[:4]) + (f' ‖ (+{len(uniq)-4})' if len(uniq) > 4 else ''))
open(os.path.join(os.path.dirname(D), 'p11_ex26_busca.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
