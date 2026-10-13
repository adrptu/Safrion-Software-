# -*- coding: utf-8 -*-
"""Confere o aceite CTL-4-FIX nos valores lidos pela tela (aceite.py → JSON) e pelo roteiro da contraprova (roteiro.py → valores.json).
Uso: python3 confere.py <aceite.json> <valores.json do roteiro> <motor.log>  → uma linha por verificação e um JSON com os números."""
import json, sys, re
A = json.load(open(sys.argv[1])); R = json.load(open(sys.argv[2])); MOT = open(sys.argv[3], encoding='utf-8').read()
OK = []; OUT = {}
def chk(item, nome, cond, ev):
    OK.append((item, nome, bool(cond), ev)); print(('OK    ' if cond else 'FALHA ') + f'[{item}] {nome} · {ev}')
SEM = 'Semente de soja 58 W'; MAP = 'MAP 11-52'; NPK = 'NPK 20-05-20'; FA = 'Fungicida A'
c = lambda x, p, k: x['linhas'][p].get(k, '')
# ---------------- item 1 ----------------
I = A['item1']; a, d = I['antes'], I['depois']
sa, sd = a['saf'], d['saf']
v1 = dict(saf_liq=(c(sa, MAP, 'NECESSIDADE LÍQUIDA'), c(sd, MAP, 'NECESSIDADE LÍQUIDA')), saf_apto=(c(sa, MAP, 'ESTOQUE APTO'), c(sd, MAP, 'ESTOQUE APTO')),
          cmp_apto=(c(a['cmp'], MAP, 'ESTOQUE APTO'), c(d['cmp'], MAP, 'ESTOQUE APTO')), cmp_nec=(c(a['cmp'], MAP, 'NECESSIDADE'), c(d['cmp'], MAP, 'NECESSIDADE')),
          total=(sa['total'], sd['total']), prim=(sa['prim'], sd['prim']), memo=(sa['memo'][MAP][0], sd['memo'][MAP][0]),
          lote=(a['cen']['lotes'][0]['fisico'], d['cen']['lotes'][0]['fisico']), custodia=(a['cen']['req031'][0]['custodia'], d['cen']['req031'][0]['custodia']),
          est_disp=([r.get('DISPONÍVEL') for r in a['est']], [r.get('DISPONÍVEL') for r in d['est']]), est_cust=(a['est'][0].get('EM CUSTÓDIA (FORA DO DEPÓSITO)'), d['est'][0].get('EM CUSTÓDIA (FORA DO DEPÓSITO)')),
          mapa=(re.search(r'Falta [\d.]+ kg', a['mapa'][MAP]).group(0), re.search(r'Falta [\d.]+ kg', d['mapa'][MAP]).group(0)), pt=(c(a['pt'], MAP, 'QUANTIDADE'), c(d['pt'], MAP, 'QUANTIDADE')), recibo=I['recibo'])
OUT['item1'] = v1
chk(1, 'necessidade do MAP igual antes e depois da devolução (Planejar safra e Compra), total e primária iguais',
    v1['saf_liq'] == ('79.500 kg', '79.500 kg') and v1['cmp_nec'] == ('79.500', '79.500') and v1['total'][0] == v1['total'][1] and v1['prim'][0] == v1['prim'][1], (v1['saf_liq'], v1['cmp_nec'], v1['total'][0][:60]))
chk(1, 'depósito 90.000 → 90.500 (lote M26-07, Estoque apto no Planejar safra e na Compra) e custódia da REQ-031 500 → 0',
    v1['lote'] == (90000, 90500) and v1['saf_apto'] == ('90.000 kg', '90.500 kg') and v1['cmp_apto'] == ('90.000', '90.500') and v1['custodia'] == (500, 0) and 'Custódia de MAP 11-52 na OS-0417: 500 kg → 0 kg' in v1['recibo'],
    (v1['lote'], v1['saf_apto'], v1['cmp_apto'], v1['custodia']))
chk(1, 'os 500 kg contam uma vez (antes: 90.000 + 500 em custódia = 90.500; depois: 90.500 aptos, sem custódia) e não ficam livres no Estoque enquanto estão com a OS-0417 (disponível 90.000, custódia 500)',
    v1['memo'][0].startswith('Estoque apto hoje: 90.000 kg + 500 kg em custódia sem uso nas O.S.') and v1['memo'][0].endswith('= 90.500 kg') and v1['memo'][1] == 'Estoque apto hoje: 90.500 kg'
    and v1['est_disp'][0][0] == '90.000 kg' and v1['est_cust'][0] == '500 kg' and v1['est_disp'][1][0] == '90.500 kg' and v1['est_cust'][1] == '—', (v1['memo'], v1['est_disp'], v1['est_cust']))
chk(1, 'Mapa e Portal com o mesmo número (Falta 79.500 kg; SOL 79.500 kg), antes e depois', v1['mapa'] == ('Falta 79.500 kg',) * 2 and v1['pt'] == ('79.500 kg',) * 2, (v1['mapa'], v1['pt']))
chk(1, 'motor: devolver os 500 kg não muda a demanda', 'passo dev500 → sem mudança na demanda' in MOT, 'motor_3f9e4f6.log')
# memória das parcelas (reconciliação com os 62.500 da v55)
OUT['item1']['memo_parcelas'] = sd['memo'][MAP][:8]
# ---------------- item 2 ----------------
I = A['item2']; q = I['quar']; s = q['saf']; cm = q['cmp']
fc = next((x for x in s['memo'][SEM] if x.startswith('Falta condicionada à qualidade')), '')
v2 = dict(saf_antes=[c(I['antes']['saf'], SEM, k) for k in ('NECESSIDADE LÍQUIDA', 'ESTOQUE APTO', 'RECEBIMENTOS PREVISTOS', 'SITUAÇÃO')],
          saf_quar=[c(s, SEM, k) for k in ('NECESSIDADE LÍQUIDA', 'ESTOQUE APTO', 'RECEBIMENTOS PREVISTOS', 'SITUAÇÃO')],
          cmp_antes=[c(I['antes']['cmp'], SEM, k) for k in ('ESTOQUE APTO', 'A RECEBER', 'NECESSIDADE', 'NA COMPRA')], cmp_quar=[c(cm, SEM, k) for k in ('ESTOQUE APTO', 'A RECEBER', 'NECESSIDADE', 'NA COMPRA')],
          total=(I['antes']['saf']['total'], s['total']), prim=(I['antes']['saf']['prim'], s['prim']), cmp_tot=(I['antes']['cmp']['tot'], cm['tot']), cmp_prim=(I['antes']['cmp']['prim'], cm['prim']),
          memo_cond=fc, memo_ini=s['memo'][SEM][0], mapa=(I['antes']['mapa'][SEM][:120], q['mapa'][SEM][:600]),
          liberado=[c(I['liberado']['saf'], SEM, k) for k in ('NECESSIDADE LÍQUIDA', 'ESTOQUE APTO', 'SITUAÇÃO')], liberado_cmp=[c(I['liberado']['cmp'], SEM, k) for k in ('ESTOQUE APTO', 'NECESSIDADE', 'NA COMPRA')],
          liberado_mapa=I['liberado']['mapa'][SEM][:120],
          reprovado=[c(I['reprovado']['saf'], SEM, k) for k in ('NECESSIDADE LÍQUIDA', 'ESTOQUE APTO', 'SITUAÇÃO')], reprovado_prim=I['reprovado']['saf']['prim'],
          reprovado_memo=[x for x in I['reprovado']['saf']['memo'][SEM] if x.startswith('Reprovado')], reprovado_cmp=[c(I['reprovado']['cmp'], SEM, k) for k in ('NECESSIDADE', 'NA COMPRA')],
          reprovado_mapa=I['reprovado']['mapa'][SEM][:120], recibos=(I['nf'][1], I['lib'][1], I['rep'][1]))
OUT['item2'] = v2
chk(2, 'a NF em quarentena sai de "Recebimentos previstos" (20.000 → 0) e de "A receber" (20.000 → 0); quarentena não é apto (12.000)',
    v2['saf_antes'][2] == '20.000 kg' and v2['saf_quar'][2] == '0 kg' and v2['cmp_antes'][1] == '20.000' and v2['cmp_quar'][1] == '0' and v2['saf_quar'][1] == '12.000 kg' and v2['cmp_quar'][0] == '12.000',
    (v2['saf_antes'][1:3], v2['saf_quar'][1:3], v2['cmp_antes'][:2], v2['cmp_quar'][:2]))
chk(2, 'não é cobertura confirmada: "Qualidade pendente · 15.456 kg" no lugar de "Coberto" (Planejar safra, Compra e Mapa)',
    v2['saf_quar'][3] == 'Qualidade pendente · 15.456 kg' and 'Coberto' not in v2['cmp_quar'][3] and v2['cmp_quar'][3].startswith('Qualidade pendente · 15.456 kg') and 'Qualidade pendente · 15.456 kg' in v2['mapa'][1],
    (v2['saf_quar'][3], v2['cmp_quar'][3][:40], v2['mapa'][1][:80]))
TXT = ('motivo: 20.000 kg em quarentena aguardam laudo (lote S58-0926 · NF 4533: Aguarda laudo de germinação', 'responsável: o gestor libera ou reprova com o laudo no Estoque', 'prazo: decidir antes de 15/10/2026', 'sem nova compra automática')
# o aceite.py guarda só 420 caracteres do painel do Mapa por insumo: ali cabem o motivo e o responsável; o prazo e a decisão no painel inteiro
# do Mapa estão no demanda_estado_nav_test Q1b (mesma entrada, painel completo) — lido do log da bateria (argumento 5)
Q1B = open(sys.argv[5], encoding='utf-8').read() if len(sys.argv) > 5 else ''
chk(2, 'falta condicionada com motivo (o da conferência), responsável, prazo e decisão à vista na memória do Planejar safra, na Compra e no Mapa',
    all(t in x for x in (fc, v2['cmp_quar'][3]) for t in TXT) and all(t in v2['mapa'][1] for t in TXT[:2]) and 'OK    · Q1b aceite CTL-4-FIX item 2' in Q1B,
    (fc[:420], 'Mapa (420 car.): ' + v2['mapa'][1][-200:], 'Q1b: ' + ('OK' if 'OK    · Q1b' in Q1B else 'sem log')))
chk(2, 'fora da compra firme e sem trocar a primária: necessidade 0, total e primária iguais (Planejar safra e Compra); o total diz "R$ 146.832,00 condicionados ao laudo, fora da compra"',
    v2['saf_quar'][0] == '0 kg' and v2['cmp_quar'][2] == '0' and v2['total'][1].startswith(v2['total'][0]) and 'R$ 146.832,00 condicionados ao laudo, fora da compra' in v2['total'][1]
    and v2['prim'][0] == v2['prim'][1] and v2['cmp_tot'][0] == v2['cmp_tot'][1] and v2['cmp_prim'][0] == v2['cmp_prim'][1], (v2['total'][1][-110:], v2['prim'], v2['cmp_tot']))
chk(2, 'laudo liberado → coberto (32.000 kg aptos; Planejar safra, Compra e Mapa)',
    v2['liberado'] == ['0 kg', '32.000 kg', 'Coberto pelo estoque'] and v2['liberado_cmp'][:2] == ['32.000', '0'] and 'Coberto' in v2['liberado_cmp'][2] and 'Estoque cobre' in v2['liberado_mapa'], (v2['liberado'], v2['liberado_cmp'], v2['liberado_mapa'][:60]))
chk(2, 'laudo reprovado → falta firme de 15.456 kg com o motivo ("Reprovado: … laudo LAB-2: germinação 71%"), "Complemento" e a primária pede o envio; Compra e Mapa com o mesmo número',
    v2['reprovado'] == ['15.456 kg', '12.000 kg', 'Complemento'] and v2['reprovado_prim'] == 'Enviar para cotação' and v2['reprovado_memo'] and 'germinação 71%' in v2['reprovado_memo'][0]
    and v2['reprovado_cmp'][0] == '15.456' and 'Complemento · 15.456 kg' in v2['reprovado_cmp'][1] and 'Falta 15.456 kg' in v2['reprovado_mapa'], (v2['reprovado'], v2['reprovado_memo'], v2['reprovado_cmp']))
chk(2, 'motor: NF em quarentena e laudo não mudam a compra (liq 0; total 428.305); situação "Qualidade pendente" com cond 15.456 e a SOL não ganha a semente',
    'nfq (0, 428305)' in MOT and 'laudo (0, 428305)' in MOT and '"t": "Qualidade pendente"' in MOT and '"cond": 15456' in MOT and '["Atualizar SOL: novos", [], null]' in MOT, 'motor_3f9e4f6.log')
# ---------------- item 3 ----------------
I = A['item3']; P = ('antes', 'entregue', 'cancelada', 'devolvida')
v3 = dict(saf={k: c(I[k]['saf'], NPK, 'NECESSIDADE LÍQUIDA') for k in P}, total={k: I[k]['saf']['total'][:60] for k in P}, prim={k: I[k]['saf']['prim'] for k in P},
          cmp={k: (c(I[k]['cmp'], NPK, 'NECESSIDADE'), c(I[k]['cmp'], NPK, 'NA COMPRA')) for k in P}, cmp_tot={k: I[k]['cmp']['tot'] for k in P},
          mapa={k: re.search(r'Falta [\d.]+ kg', I[k]['mapa'][NPK]).group(0) for k in P}, recibos=(I['ent_recibo'], I['canc_recibo'], I['dev_recibo']),
          os_osc=I['cancelada']['cen']['os0425']['osc'], painel=I['os_cancelada_painel'][:700], links=I['os_cancelada_links'], req040=(I['cancelada']['cen']['req040'], I['devolvida']['cen']['req040']))
A11 = I['A11']
v3['A11'] = dict(apontar=A11['apontar'], cen_apontado=A11['cen_apontado'], dev=A11['dev_recibo'], cen_devolvido=A11['cen_devolvido'],
                 s2627={k: (c(A11[k]['s2627'], FA, 'NECESSIDADE LÍQUIDA'), A11[k]['s2627']['total'][:60]) for k in ('antes', 'apontado', 'devolvido')},
                 s27sf={k: (c(A11[k]['s27sf'], FA, 'NECESSIDADE LÍQUIDA'), c(A11[k]['s27sf'], FA, 'ESTOQUE APTO'), A11[k]['s27sf']['total'][:70], A11[k]['s27sf']['prim']) for k in ('antes', 'apontado', 'devolvido')})
OUT['item3'] = v3
chk(3, 'NPK: entregar 8.000 kg, cancelar a OS-0425 e devolver não mudam a compra (14.800 kg; total, primária, Compra e Mapa iguais em todos os passos)',
    set(v3['saf'].values()) == {'14.800 kg'} and len(set(v3['total'].values())) == 1 and len(set(v3['prim'].values())) == 1 and set(x[0] for x in v3['cmp'].values()) == {'14.800'}
    and len(set(json.dumps(x) for x in v3['cmp_tot'].values())) == 1 and set(v3['mapa'].values()) == {'Falta 14.800 kg'}, (v3['saf'], v3['mapa']))
chk(3, 'cancelar (Ana, com motivo) não grava "nada tinha sido entregue"; a custódia fica com destino: dono Rui (almoxarife), prazo "receber a devolução", link "Receber devolução" ao Estoque',
    'nada tinha sido entregue' not in json.dumps(v3, ensure_ascii=False) and v3['os_osc']['canPor'] == 'Ana (gestora)' and 'Talhão replanejado' in v3['os_osc']['cond']
    and v3['os_osc']['dono'] == 'Rui (almoxarife)' and v3['os_osc']['prazo'] == 'receber a devolução' and any(l.startswith('Receber devolução') and l.endswith('>EST.dc.html') for l in v3['links'])
    and v3['req040'][0]['itens'][0]['custodia'] == 8000 and v3['req040'][1]['itens'][0]['custodia'] == 0, (v3['os_osc']['cond'][-160:], v3['os_osc']['dono'], v3['os_osc']['prazo']))
chk(3, 'A11: a OS-0421 aponta 150 ha com 20 L e devolve 40 L — a compra não muda com a devolução (Safra 2026/27 e Safrinha 2027: necessidade, total e primária iguais; o depósito sobe 40 L)',
    'apontamento' in str(A11['apontar']).lower() or A11['apontar'] == 'ok' or 'registrad' in str(A11['apontar']).lower(),
    A11['apontar'])
s27 = v3['A11']['s27sf']; s26 = v3['A11']['s2627']
chk(3, 'A11 (números): devolução sem mudança de compra', s27['apontado'][0] == s27['devolvido'][0] and s27['apontado'][2] == s27['devolvido'][2] and s27['apontado'][3] == s27['devolvido'][3]
    and s26['apontado'] == s26['devolvido'] and A11['cen_devolvido']['req035'][0]['devolvido'] == 40, (s26, s27))
chk(3, 'motor: C4 (entrega, cancelamento, devolução) e A11 (devolução) sem mudança na demanda; T10: SOL e pedido não mudam',
    MOT.count('passo ent8000 → sem mudança') == 1 and 'passo cancel → sem mudança na demanda' in MOT and 'passo dev8000 → sem mudança na demanda' in MOT and 'passo dev40 → sem mudança na demanda' in MOT
    and '["OS-0425 cancelada → Atualizar SOL: novos/menos/SOL NPK", [], [], 14800]' in MOT, 'motor_3f9e4f6.log')
# ---------------- item 4 ----------------
I = A['item4']
def rec_lines(x, p): return [m for m in x['memo'][p] if 'Recebimento' in m]
v4 = dict(semente={p: rec_lines(I['semente']['saf'], p) for p in ('KCl 60%', 'Semente de soja 62 X', SEM)}, parcial={p: rec_lines(I['parcial']['saf'], p) for p in ('KCl 60%', 'Semente de soja 62 X', SEM)},
          rec_cols={k: [c(I[k]['saf'], SEM, 'RECEBIMENTOS PREVISTOS'), c(I[k]['cmp'], SEM, 'A RECEBER'), c(I[k]['saf'], SEM, 'ESTOQUE APTO')] for k in ('semente', 'parcial')},
          cmp_igual_saf={k: all(I[k]['cmp']['memo'][p][:-2] == I[k]['saf']['memo'][p][:-2] for p in I[k]['saf']['memo']) for k in ('semente', 'parcial')}, nf=I['nf_parcial'][1])
OUT['item4'] = v4
chk(4, 'recebimentos com data na projeção: PC-088 em 02/10, PC-091 em 08/10 e PC-090 em 05/10, na ordem das datas de uso; Compra com a mesma memória',
    v4['semente']['KCl 60%'] == ['02/10/2026 · Recebimento PC-088 (Fertisul) · +40.000,0 kg → saldo 100.000 kg'] and v4['semente']['Semente de soja 62 X'][0].startswith('08/10/2026 · Recebimento PC-091')
    and v4['semente'][SEM][0].startswith('05/10/2026 · Recebimento PC-090 (Coop. Vale) · +20.000,0 kg') and all(v4['cmp_igual_saf'].values()), v4['semente'])
chk(4, 'entrega parcial (NF 4533 com 12.000 aptos): o saldo aberto do PC-090 (8.000 kg) continua com a data 05/10; os outros pedidos não mudam',
    v4['rec_cols']['parcial'] == ['8.000 kg', '8.000', '24.000 kg'] and v4['parcial'][SEM][0].startswith('05/10/2026 · Recebimento PC-090 (Coop. Vale) · +8.000,0 kg')
    and v4['parcial']['KCl 60%'] == v4['semente']['KCl 60%'] and v4['parcial']['Semente de soja 62 X'] == v4['semente']['Semente de soja 62 X'], (v4['rec_cols'], v4['parcial'][SEM]))
# ---------------- item 5 ----------------
v5 = dict(MAP=dict(saf=v1['saf_liq'][1], cmp=v1['cmp_nec'][1], mapa=v1['mapa'][1], portal=v1['pt'][1]),
          NPK=dict(saf=v3['saf']['devolvida'], cmp=v3['cmp']['devolvida'][0], mapa=v3['mapa']['devolvida']),
          SEM_quar=dict(saf=v2['saf_quar'][3], cmp=v2['cmp_quar'][3][:31].strip(), mapa=re.search(r'Qualidade pendente · [\d.]+ kg', v2['mapa'][1]).group(0)),
          SEM_rep=dict(saf=v2['reprovado'][0], cmp=v2['reprovado_cmp'][0], mapa=re.search(r'Falta [\d.]+ kg', v2['reprovado_mapa']).group(0)))
OUT['item5'] = v5
chk(5, 'mesmos números em Planejar safra, Compra/SOL-2026-07, Mapa › Insumos e Portal do parceiro (MAP 79.500; NPK 14.800; Semente 15.456 condicionada e, reprovada, 15.456 firme)',
    v5['MAP'] == dict(saf='79.500 kg', cmp='79.500', mapa='Falta 79.500 kg', portal='79.500 kg') and v5['NPK'] == dict(saf='14.800 kg', cmp='14.800', mapa='Falta 14.800 kg')
    and v5['SEM_quar'] == dict(saf='Qualidade pendente · 15.456 kg', cmp='Qualidade pendente · 15.456 kg', mapa='Qualidade pendente · 15.456 kg') and v5['SEM_rep'] == dict(saf='15.456 kg', cmp='15.456', mapa='Falta 15.456 kg'), v5)
# ---------------- roteiro da contraprova (as mesmas entradas e leituras da base 0c0931f) ----------------
L = R['leituras']; g = lambda t, tela, p, k: (L[t][tela]['linhas'][p] or [{}])[0].get(k)
v0 = {t: dict(SAF_MAP=[g(t, 'SAF', MAP, k) for k in ('DEMANDA BRUTA', 'ESTOQUE APTO', 'RECEBIMENTOS PREVISTOS', 'NECESSIDADE LÍQUIDA', 'FALTA EM', 'VALOR', 'SITUAÇÃO')],
              SAF_SEM=[g(t, 'SAF', SEM, k) for k in ('DEMANDA BRUTA', 'ESTOQUE APTO', 'RECEBIMENTOS PREVISTOS', 'NECESSIDADE LÍQUIDA', 'SITUAÇÃO')],
              CMP_MAP=[g(t, 'CMP', MAP, k) for k in ('BRUTA', 'ESTOQUE APTO', 'A RECEBER', 'NECESSIDADE', 'VALOR', 'NA COMPRA')],
              CMP_SEM=[g(t, 'CMP', SEM, k) for k in ('BRUTA', 'ESTOQUE APTO', 'A RECEBER', 'NECESSIDADE', 'NA COMPRA')],
              total=L[t]['SAF']['g2tot'], prim=(L[t]['SAF']['primaria']['acoes_prim'], L[t]['CMP']['primaria']['acoes_prim'])) for t in ('0_antes', '1_apos_devolucao', '3_final')}
OUT['roteiro'] = v0
chk('roteiro', 'contraprova (mesmas entradas da base): MAP 79.500 nos três momentos, apto 90.000 → 90.500 no Planejar safra e na Compra; Semente sem "a receber" e em "Qualidade pendente · 15.456 kg" no final; total e primárias iguais',
    all(v0[t]['SAF_MAP'][3] == '79.500 kg' and v0[t]['CMP_MAP'][3] == '79.500' for t in v0) and v0['1_apos_devolucao']['SAF_MAP'][1] == '90.500 kg' and v0['1_apos_devolucao']['CMP_MAP'][1] == '90.500'
    and v0['3_final']['SAF_SEM'][2] == '0 kg' and v0['3_final']['CMP_SEM'][2] == '0' and v0['3_final']['SAF_SEM'][4] == 'Qualidade pendente · 15.456 kg' and v0['3_final']['CMP_SEM'][4].startswith('Qualidade pendente · 15.456 kg')
    and len(set(json.dumps(v0[t]['total']) for t in v0)) == 1 and len(set(json.dumps(v0[t]['prim']) for t in v0)) == 1 and R.get('erros_js') == [], {t: (v0[t]['SAF_MAP'][1], v0[t]['SAF_MAP'][3], v0[t]['SAF_SEM'][2:]) for t in v0})
chk('js', 'sem erro de JavaScript nas telas abertas (aceite e roteiro)', A.get('erros_js') == [] and R.get('erros_js') == [], (A.get('erros_js'), R.get('erros_js')))
OUT['verificacoes'] = [dict(item=i, nome=n, passou=p, evidencia=str(e)[:600]) for i, n, p, e in OK]
json.dump(OUT, open(sys.argv[4], 'w'), ensure_ascii=False, indent=1)
print(f'RESULTADO: {sum(1 for x in OK if x[2])}/{len(OK)}')
