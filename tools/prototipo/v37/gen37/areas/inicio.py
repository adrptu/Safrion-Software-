# -*- coding: utf-8 -*-
"""Mapa (IN-04, 1º item do menu) + módulos ocultos do Início: IN-01 Meu dia · IN-02 Aprovações · IN-03 Agenda e pendências.
O.S. não passa por revisão nem pela caixa de Aprovações: o agrônomo libera na tela O.S., onde pode ajustar antes de liberar.

Irrigação só com água NÃO passa pelo agrônomo (decisão do proprietário, igual a irrigacao.py): a lâmina vem do balanço hídrico
e a liberação da prontidão operacional. OS-0419 liberada pela necessidade do balanço (10,81 mm hoje); OS-0422 "Janela a definir"
(amarelo, dono João, atalho IR-02); OS-0423 "Conflito · parada da B3" (vermelho, dono Caio · PCP). Só a fertirrigação (OS-0418)
é liberada pelo agrônomo, que pode ajustar antes de liberar. A antiga decisão IN-02x-os0422 (exceção de água) deixou de ser gerada.
Filtro Fazenda do topo (mf_faz): Santa Rita = mapa; Boa Vista = estado vazio (sem talhão desenhado); Todas = Santa Rita + aviso.
Fase e realizado das ordens no mapa vêm do cenário compartilhado (cenario.js · cenGet/cenOuvir), iguais às telas O.S., Estoque e App.

IN-04 · Mapa: tela de trabalho sem rolagem (1440×900). Barra lateral de funcionalidades (ícone + nome) · 9 camadas canônicas ·
filtros DA CAMADA ATIVA no topo do bloco · cores dos talhões calculadas no cliente (buracos {{fl_T1}}…) e recalculadas a cada
filtro · clique no talhão abre painel lateral com informação e ações da camada · faixa fina com legenda e 4 números.

observacoes (dados locais coerentes com dados.py / dados2.py / telas vizinhas):
- Ordens no mapa = dados.ORDENS (registro canônico, menos OB-0104 que é do armazém): tipo, fase, selo, janela, saldo,
  responsável e link de detalhe vêm do registro; OS-0430 (T1-A) aparece no polígono T1.
- OS-0420: 30/100 ha, saldo 70 ha; os 30 ha realizados ficam na v2 e a v3 (KCl −12 % só no saldo) já vale, ajustada por Ana (agrônoma)
  em 23/09. Selo do registro "Impedida · ativo bloqueado", igual ao de OS.dc.html e CA-01x-os0420 (DEMO-14): o saldo está parado só pelo
  Trator T1 (OM-0233), sem pendência do agrônomo; no Mapa o próximo passo é Acompanhar OM-0233 (MA-04, estado da manutenção; Frente F). OS-0431 "Falta máquina" conta como impedida.
- Geometria (26/09): dados.GEO_TAL/GEO_PARC, fonte única com o CD-01det (polígono do T1 v3 validado em 12/09; T1-B sem polígono).
  O painel Integrado mostra a linha Geometria onde houver dado; "Próxima ocupação" marca a parcela sem polígono. A T1-B não é desenhada.
- "Programar vistoria" da barra do MIP/MID é um modo (como Medir): clique no talhão programa a vistoria com a mesma função do painel
  (mipNovaVis, dados_mip.py + mip.js), sem duplicar talhão × alvo aberto; com talhão(ões) já selecionado(s), programa direto.
  O cenário 60/40 pedido pelo defeito DEMO-14 exige mudar dados.OS (fora deste módulo) — mantido 30/70 para as telas concordarem.
- OS-0419: janela "hoje 20:00–amanhã 10:31" = 1 volta a 62 % (≈14,5 h), a mesma do IR-02/IR-03det, PL-04 e OS.dc.html.
  OS-0418: "24/09 21:00–25/09 11:15" (8,1 mm × 95 ha ÷ 150 L/s ≈ 14,3 h), a mesma do IR-02 e PL-04.
- Satélite (local): Sentinel-2 L2A 10 m, cenas 21/09 (nuvem 4 %, C1 coberto), 16/09 (0 %) e 06/09 (32 %, P2 e T7 cobertos);
  NDVI/NDRE/EVI/NDWI de P1, P2, T7 e C1; T1/T2/T4/T3 sem cultura (solo exposto/colhido). Mancha em T7: 0,4 ha (16/09) → 1,2 ha (21/09).
  A vistoria da mancha (camada Satélite) é uma "Inspeção de mancha" no mesmo estado do MIP (aparece no AG-01 e no app).
- Análises de solo (13/10/2026, pedido do proprietário: "coloque analises de solo como uma das opcoes do menu do mapa"): camada da
  barra com os laudos do AG-02 (dados_solo.py + c.solo do cenário, mesmas funções de solo.js: soloLaudos, soloLeituraTal); o talhão sem
  laudo de solo aparece "sem análise" (ausente não é zero). Os laudos locais LAU-2037…2052 (Fase 2, fora da barra) saíram: eram uma
  segunda fonte, que divergia do AG-02.
- Menos texto (13/10/2026, proprietário: "diminua essa quantidade de textos e descrições no mapa. somos minimalistas e essencialistas"):
  no topo do mapa ficam o nome da camada, os botões dos filtros (o nome do grupo vira aria-label e dica), números de rótulo curto (o
  rótulo completo na dica) e o link; a fonte técnica (fonte, resolução, aquisição, explicação do índice, "Demonstração sintética") vai
  para a dica do ⓘ ao lado do nome. Na legenda, só o selo "Demonstração sintética" quando a Lagoa Grande é sintética.
- Pragas e doenças (02/10): a MESMA base do AG-01 (dados_mip.py + mip.js, estado 'talhao-os-mip-v1'): cor, rótulo, próximo passo (mipProx) e
  "Programar vistoria" vêm de lá; Santa Rita (VIS-006…017) e Lagoa Grande (VIS-051…060). As decisões abrem AG-01.dc.html#VIS-xxx.
- Irrigação: déficits de irrigacao.py (P2 11,2 mm · P1 8,4 mm · T7 ≈10,0 mm estimado, sonda sem dado).
- Custos (local): R$/ha realizado × orçado com abertura insumos/operações/máquinas; T4 +18 % (reparo OM-0233 + substituto).
- Liberação pelo agrônomo: OS-0418 e OS-0430 (A liberar, com produto) são liberadas por Ana na tela O.S. ou no painel do Mapa
  (Liberar para execução), com "Ajustar antes de liberar" opcional na O.S.; a REQ-038 reserva a Ureia ao liberar. Mapa e O.S. leem a
  fase no cenário compartilhado: liberada, a ordem sai da contagem "A liberar (agrônomo)".
  Custo dos 30 ha preservados da OS-0420: semente 1.560 kg × R$ 9,50 + KCl 3.600 kg × R$ 2,40 = R$ 23.460.
- Sobras: "Receber sobras"/"Receber devolução" levam ao Estoque do menu (EST.dc.html · etapa Receba devoluções), que grava no cenário.
"""
import json
from engine import (grid,esc,icon,chip,btn,Pt,INK,MUTED,LINE,BG,SURF,YEL,YELS,RED,REDS,GRAYS,DISP,
                    BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, HEIGHTS37, LCOR
import dados as D
import dados2 as D2
from areas.processo_os import JS_NUCLEO, _ordens as _ordens_os
import areas.custo_dominio as _CUS   # custo das O.S.: regras únicas do Mapa e do Painel Agrícola

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
T=lambda: H('true')
def nfb(v,d=0):
    s=f'{v:,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')
    return s

# ---------------------------------------------------------------- utilitários visuais (padrão novo)
def bloco(titulo,desc,corpo,acao='',tone=None):
    desc=''   # 13/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos títulos ... somos minimalistas e essencialistas")
    bd={'yellow':YEL,'red':RED}.get(tone,LINE)
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; {"border-left: 4px solid "+bd+";" if tone else ""} border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{titulo}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>'
            f'<div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end;">{acao}</div></div>'
            f'<div style="padding: 0 12px 12px;">{corpo}</div></section>')
_IST='display: inline-flex; align-items: center; gap: 6px; text-decoration: none; '
def ilink(text,href,ico,title,primary=False):
    return f'<a href="{href}" title="{esc(title)}" aria-label="{esc(title)}" style="{_IST}{BTN_ST(primary,True)}">{icon(ico,15)}{esc(text)}</a>'
def nota(html): return f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.6; padding: 0 4px;">{html}</div>'
B=lambda t: f'<b style="color: {INK};">{t}</b>'
def R(id,ro=False,o=None,**cells):
    """linha G2: str/num → v; lista de partes → p (+ s); tupla (valor, partes) → v e p."""
    v={}; s={}; p={}
    for k,c in cells.items():
        if isinstance(c,tuple): v[k]=c[0]; p[k]=c[1]; s[k]=' '.join(x.get('t','') for x in c[1] if x.get('k')!='br')
        elif isinstance(c,list): p[k]=c; s[k]=' '.join(x.get('t','') for x in c if x.get('k')!='br')
        else: v[k]=c
    d=dict(id=id,v=v,s=s,p=p)
    if ro: d['ro']=True
    if o: d['o']=[dict(t=t) if isinstance(t,str) else t for t in o]
    return d
JS_COMUM=r'''
function GRx(id){ return GRIDS.find(g=>g.id===id); }
function chipSt(c){ const cc=G2C[c]||G2C.gray; return 'display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';'; }
function nfx(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
'''

# =====================================================================================================
# IN-04 · MAPA
# =====================================================================================================
TAL={t:dict(ha=ha,cult=c,fase=f) for t,ha,c,f,_ in D.TALHOES}
GEO=[('T1','poly','30,30 300,22 312,282 40,292'),('T2','poly','326,22 580,28 574,280 332,286'),
     ('P1','circ','700,158,104'),('P2','circ','902,158,92'),
     ('T4','poly','40,344 306,336 312,598 46,606'),('T3','poly','328,338 572,334 578,596 334,600'),
     ('T7','poly','598,344 782,338 788,598 604,602'),('C1','poly','804,338 976,334 982,596 810,600')]
TIDS=[g[0] for g in GEO]
PERIM={'T1':'7,1','T2':'6,9','T3':'3,9','T4':'5,7','P1':'3,5','P2':'3,2','T7':'2,6','C1':'2,5'}
LAYS=['Integrado','Satélite','Lavoura','MIP/MID','Irrigação','O.S./prazos','Insumos','Custos']   # Fase 1 (MIP/MID e Irrigação de volta à barra em 01/10, pedidos do proprietário)
LAYS_F2=['Colheita/produtividade']               # Fase 2: dados preservados abaixo, fora da barra
LAYS.insert(LAYS.index('Lavoura')+1,'Análises de solo')   # 13/10/2026 (proprietário): laudos do AG-02 no mapa, depois da Lavoura
LAYS.insert(LAYS.index('MIP/MID')+1,'Carência e destino')   # MAPA-CARENCIA-LMR-20261003 (motor e regras em dados_carencia.py)
LAYS.insert(LAYS.index('Carência e destino')+1,'Colheita')   # 14/10/2026 (proprietário: o que de Agrícola faltava no mapa): situação da colheita por talhão
# filtros da camada ativa (k, rótulo, opções) — o primeiro valor é o padrão
FILT={
 'Integrado':[('mostrar','Mostrar',['Todas as condições','Só pendências'])],
 'Satélite':[('idx','Índice',['NDVI','NDRE','EVI','SAVI','NDMI']),('dt','Cena',['21/09','16/09','06/09']),('ctr','Contraste',['Talhão','Fazenda','Absoluto'])],
 'O.S./prazos':[('fase','Fase',['Todas','A liberar','Liberadas','Em execução','Em conferência','Encerradas'])],
 'MIP/MID':[('per','Período',['Últimos 7 dias','Últimos 30 dias'])],
 'Irrigação':[('ver','Mostrar',['Hoje','Balanço hídrico'])],
 'Insumos':[('per','Período',['Próximos 30 dias','Safra toda'])],
 'Custos':[('most','Mostrar',['Previsto R$/ha','Realizado × previsto'])],
}
FILT['Carência e destino']=[('qd','Consultar em',['Hoje','Em 7 dias','Em 14 dias'])]   # MAPA-CARENCIA-LMR-20261003
# Análises de solo (15/10/2026): laudo, camada, indicador e contraste; Laudo e Indicador vêm dos laudos da fazenda (soloFopts)
FILT['Análises de solo']=[('lau','Laudo',['Mais recente']),('prof','Camada',['0–20 cm','20–40 cm']),('ind','Indicador',['V %']),('ctr','Contraste',['Talhão','Fazenda','Absoluto'])]
# ordens no mapa = dados.ORDENS (menos OB-0104, do armazém). Tipo, selo, janela, responsável e link de detalhe vêm do registro
# canônico; fase, realizado, saldo e custódia vêm do cenário compartilhado no navegador (cenGet), com o registro como semente.
# Aqui ficam só os campos do mapa: talhões da geometria, complemento do realizado, prazo e a próxima ação da ordem
# (rótulo, destino, tipo: 'lib' = liberação pelo agrônomo, com ajuste opcional (o primário é o "Liberar para execução" do núcleo
# da O.S.; o rótulo daqui é o ajuste) · 'op' = pendência operacional, que no painel só aparece com o próximo passo impedido;
# condição: 'ag' = só enquanto a ordem está a liberar pelo agrônomo no cenário, 'cust' = só com custódia).
_ORD_MAPA=[  # id, talhões da geometria, complemento do realizado, prazo, ação
 ('OS-0421',['T1','T2'],'','no prazo',None),
 ('OS-0420',['T4'],'','atrasada',('Acompanhar OM-0233','MA.dc.html#om=OM-0233','op',None)),   # PL-05 é oculta e fixa (Frente F): a OM-0233 viva
 ('OS-0419',['P2'],'lâmina 10,81 mm','irrigando hoje',None),
 ('OS-0424',['T1'],'T1-B','até 3 dias',None),
 ('OS-0422',['P2'],'2 passadas de 6,75 mm','até 3 dias',('Definir janela','IR-03det.dc.html#OS-0422:janela','op',None)),
 ('OS-0418',['P1'],'Ureia 12 kg/ha','vence hoje',('Ajustar antes de liberar','OS.dc.html#OS-0418','lib','ag')),
 ('OS-0417',['P1'],'','até 3 dias',('Receber sobras','EST.dc.html','op','cust')),
 ('OS-0415',['T3'],'','encerrada',None),
 ('OS-0423',['T7'],'estimativa por ET','vence hoje',('Resolver conflito','IR-03det.dc.html#OS-0423:conflito','op',None)),
 ('OS-0425',['C1'],'','no prazo',None),
 ('OS-0430',['T1'],'T1-A','até 3 dias',('Ajustar antes de liberar','OS.dc.html#OS-0430','lib','ag')),
 ('OS-0431',['T2'],'','até 3 dias',None),
]
import dados_lagoa_safra as DLS
_ORD_MAPA+=[tuple(x) for x in DLS.ORD_MAPA]   # Lagoa Grande: ordens nos pivôs (ids PVxx do mapa)
# irrigação só com água: sem agrônomo e sem "política" — o selo é a pendência operacional, com o dono dela (igual a IR-02/IR-03)
IRR_OS={'OS-0419':dict(tipo='Irrigação · água',selos=[]),
        'OS-0422':dict(tipo='Irrigação · água',selos=[['Janela a definir','yellow']],dono='João'),
        'OS-0423':dict(tipo='Irrigação · água por gotejo',selos=[['Conflito · parada da B3','red']],dono='Caio · PCP')}
def _selo_cor(t):
    if t.startswith('Impedida') or t.startswith('Falta máquina') or t.startswith('Conflito'): return 'red'
    return 'yellow'
def _ord_mapa():
    out=[]
    for oid,tal,suf,pz,act in _ORD_MAPA:
        o=D.ORDEM[oid]; ts=([o['selo']] if o['selo'] else [])+list(o.get('selos_extra') or [])
        real=f"{nfb(o.get('realizado') or 0)}/{nfb(o.get('area') or 0)} ha"+(f" · saldo {nfb(o['saldo'])} ha" if o.get('realizado') and o.get('saldo') else '')+(f' · {suf}' if suf else '')
        d=dict(id=oid,tal=tal,tipo=o['tipo'],fase=o['etapa'],selos=[[t,_selo_cor(t)] for t in ts],area=o.get('area') or 0,suf=suf,
               jan=o['janela'],real=real,saldo=o['saldo'] or 0,resp=o['resp'],pz=pz,h=o['detalhe'] or 'OS.dc.html',saf=o.get('saf') or '2026/27')
        if oid in IRR_OS: d.update(IRR_OS[oid])
        if act: d['act']=dict(t=act[0],h=act[1],k=act[2],c=act[3])
        out.append(d)
    assert {x['id'] for x in out}=={o['id'] for o in D.ORDENS+D.ORDENS_LG if o['id'].startswith('OS-')}, 'mapa fora do registro de ordens'
    assert not any('política' in json.dumps(x,ensure_ascii=False) for x in out), 'irrigação só com água não usa política/agrônomo'
    assert not any((x.get('act') or {}).get('k')=='dec' for x in out), "O.S. sem revisão: a ação do agrônomo no mapa é 'lib' (liberar)"
    assert not any(s in json.dumps(out) for s in ('IN-02det','IN-02x-os0420')), 'telas de decisão de O.S. não são mais geradas: use OS.dc.html#OS-xxxx'
    return out
ORD=_ord_mapa()
# {OS-xxxx} no rótulo = realizado atual da ordem (cenário) · {?OS-xxxx texto} = texto só enquanto a ordem está a liberar pelo agrônomo.
# Talhão sem condição pior ganha amarelo ("atenção ou a liberar") enquanto uma ordem dele está a liberar pelo agrônomo (mesma contagem do cabeçalho).
INTEG={'T1':['ok','OS-0421 · {OS-0421}'],'T2':['red','OS-0431 impedida · Trator T1'],'T4':['red','OS-0420 impedida'],'T3':['gray','OS-0415 encerrada'],
       'P1':['ok','OS-0417 · OS-0418'],'P2':['ok','milho V10'],'T7':['yellow','mancha 1,2 ha · satélite'],'C1':['yellow','OS-0425 · entrega sem saldo']}
SEMCULT={'T1':'solo exposto · pré-plantio','T2':'solo exposto · pré-plantio','T4':'semeadura · sem leitura','T3':'colhido 12/09'}
# solo: os laudos são os do AG-02 (dados_solo.py, fonte única); os locais SOLO_B/ATTR/_solo (Fase 2, nunca exibidos) saíram em 13/10
# camada Irrigação: o mesmo estado das telas IR-01..IR-04 (dados_irrigacao.py + irrigacao_estado.js), recalculado a cada desenho
# Pragas e doenças: vistorias em dados_mip.py (mesma base do AG-01 e do app); o mapa lê o estado compartilhado pelo prefixo MIP
EST={'T1':dict(c='gray',l='pré-plantio',cult='Soja',ocup='Pousio · pré-plantio',var='58 W (T1-A) · 62 X (T1-B)',est='pré-plantio',plant='previsto 15/10 e 25/10/2026',col='—'),
     'T2':dict(c='gray',l='pré-plantio',cult='Soja',ocup='Pousio · pré-plantio',var='58 W',est='pré-plantio',plant='previsto 18/10/2026',col='—'),
     'T4':dict(c='ok',l='semeadura · 30/100 ha',cult='Soja',ocup='Soja 58 W · 1ª onda (OS-0420)',var='58 W',est='semeadura em andamento',plant='real 21–22/09 (30 ha) · saldo pausado',col='prevista fev/2027'),
     'T3':dict(c='none',l='colhido 12/09',cult='Milho',ocup='Milho · colhido',var='AG 8700',est='colhido',plant='real 20/10/2025',col='real 12/09/2026'),
     'P1':dict(c='purple',l='Feijão · R5',cult='Feijão',ocup='Feijão',var='BRS Estilo',est='R5 · pré-floração',plant='real 05/07/2026',col='prevista 10/10/2026'),
     'P2':dict(c='ok',l='Milho · V10',cult='Milho',ocup='Milho',var='AG 8700',est='V10',plant='real 10/08/2026',col='prevista 15/11/2026'),
     'T7':dict(c='yellow',l='Mamão · produção',cult='Mamão',ocup='Mamão Formosa',var='Formosa',est='produção contínua',plant='real 10/03/2025',col='semanal'),
     'C1':dict(c='orange',l='Café · granação',cult='Café',ocup='Café arábica',var='Catuaí 144',est='granação',plant='real 15/01/2019',col='prevista 20/05/2027')}
COL={'2026/27':{'Realizado':{'T7':['ok','9,6 t A na semana','ritmo de 45 t/ha/ano (meta)']},
                'Previsto':{'T1':['lime','meta 64/62 sc/ha','soja · T1-A 64 e T1-B 62 sc/ha'],'T2':['lime','meta 63 sc/ha','soja 58 W'],'T3':['lime','meta 62 sc/ha','soja 62 X'],
                            'T4':['lime','meta 60 sc/ha','soja 58 W'],'P1':['lime','meta 66 sc/ha','soja após o feijão'],'P2':['lime','meta 66 sc/ha','soja após o milho'],
                            'T7':['lime','45 t/ha/ano','mamão Formosa'],'C1':['lime','38 sc/ha','café · colheita mai/27']}},
     '2025/26':{'Realizado':{'T1':['ok','63 sc/ha · meta 62','romaneios conferidos · 312 ha'],'T2':['red','57 sc/ha · meta 61','−7 % · romaneios conferidos'],'T3':['good','172 sc/ha · meta 170','milho · romaneios conferidos']},
                'Previsto':{'P1':['lime','feijão 48 sc/ha','colheita prevista 10/10'],'P2':['lime','milho 180 sc/ha','colheita prevista 15/11']}}}
CUS_B={'T1':(1250,1240),'T2':(1250,1180),'T4':(1737,2050),'T3':(3900,3960),'P1':(3680,3900),'P2':(3450,3400),'T7':(20500,21000),'C1':(10000,9800)}
def _cus():
    out={}
    for t,(orc,real) in CUS_B.items():
        dev=(real-orc)/orc; oi,oo=round(orc*.62),round(orc*.23); om=orc-oi-oo
        ri,ro_=round(oi*(1+dev*.4)),round(oo*(1+dev*.8)); rm=real-ri-ro_
        out[t]=dict(orc=orc,real=real,g={'Insumos':[oi,ri],'Operações':[oo,ro_],'Máquinas':[om,rm]})
    return out
# geometria: fonte única dados.GEO_TAL / dados.GEO_PARC (a mesma do CD-01det); polígono validado do talhão e parcelas sem polígono
GEO_TAL,GEO_PARC=D.GEO_TAL,D.GEO_PARC
def _geo():
    out={}
    for t,txt in GEO_TAL.items():
        sem=[c['local'] for c in D2.CULTIVOS['S2627'] if c['local'].split('-')[0]==t and GEO_PARC.get(c['id'])=='Sem polígono']
        out[t]=txt+''.join(f' · {p} sem polígono' for p in sem)
    return out
def _proxima():
    out={}
    for c in D2.CULTIVOS['S2627']:
        t=c['local'].split('-')[0]; y,m,d=c['plantio'].split('-')
        out.setdefault(t,[]).append(f"{c['local']} · {c['cultura']} {c['variedade']} · {nfb(c['area'])} ha · plantio {d}/{m}/{y} · meta {c['meta']} {c['un_meta']}"
                                    + (' · sem polígono' if GEO_PARC.get(c['id'])=='Sem polígono' else ''))
    return out
# ---------------------------------------------------------------- Fase 1 (plano de execução · "Mapa dinâmico em toda a Fase 1")
# Clicar no talhão → ordens dele → próximo passo da ordem escolhida, no mesmo painel; junto: lavoura (o que está plantado, idade, DAP),
# os cinco índices de satélite, insumos (necessidade × estoque/pedido da fazenda) e custos (previsto × realizado provisório × conferido).
# Solo e Colheita ficam para a Fase 2: dados preservados acima, fora da barra.
import datetime as _dt
HOJE=_dt.date(2026,9,23)
def _iso(s): y,m,d=map(int,s.split('-')); return _dt.date(y,m,d)
def _br(d): return d.strftime('%d/%m/%Y')
def _em(d): n=(d-HOJE).days; return 'hoje' if n==0 else (f'em {n} dia'+('s' if n!=1 else '') if n>0 else f'há {-n} dia'+('s' if n!=-1 else ''))
def _idade(d0):
    m=(HOJE.year-d0.year)*12+HOJE.month-d0.month-(1 if HOJE.day<d0.day else 0); a,mm=divmod(m,12)
    ms=f'{mm} '+('meses' if mm!=1 else 'mês')
    return (f'{a} ano'+('s' if a!=1 else '')+(f' e {ms}' if mm else '')) if a else ms
def _dap(s): return (HOJE-_iso(s)).days

# ---- lavoura: ocupação atual + cultivos da safra 2026/27 (parcelas com datas distintas ficam separadas; sem idade média) ----
def _lav():
    C={c['local']:c for c in D2.CULTIVOS['S2627']}
    def plan(loc):
        c=C[loc]; d=_iso(c['plantio']); pl=next((p for p in D2.PLANOS if p['id']==c['plano']),None)
        return f"Plantio previsto {_br(d)} · {_em(d)} · " + (f"plano {pl['nome']} v{pl['versao']}" if pl else 'sem plano aplicado')
    L={}
    L['T1']=dict(c='gray',l='Soja · plantio '+_em(_iso(C['T1-A']['plantio'])),cults=['Soja'],sum='Pousio · soja prevista em 2 parcelas',
        rows=[dict(t='T1-A · Soja 58 W · 160 ha',sub=plan('T1-A'),ch=[['pré-plantio','gray']]),
              dict(t='T1-B · Soja 62 X · 152 ha',sub=plan('T1-B')+' · sem polígono (área declarada)',ch=[['pré-plantio','gray']])])
    L['T2']=dict(c='gray',l='Soja · plantio '+_em(_iso(C['T2']['plantio'])),cults=['Soja'],sum='Pousio · soja prevista',
        rows=[dict(t='T2 · Soja 58 W · 298 ha',sub=plan('T2'),ch=[['pré-plantio','gray']])])
    L['T4']=dict(c='ok',l=f"Soja · 30 ha · DAP {_dap('2026-09-22')}–{_dap('2026-09-21')}",cults=['Soja'],sum=f"Soja 58 W · 30 de 204 ha plantados (DAP {_dap('2026-09-22')}–{_dap('2026-09-21')})",
        rows=[dict(t='T4 · Soja 58 W · 30 ha plantados',sub=f"Plantio real 21/09 em 18 ha (conferido) e 22/09 em 12 ha (provisório) · DAP {_dap('2026-09-21')} e DAP {_dap('2026-09-22')}, por data, sem média",ch=[['emergência','green']]),
              dict(t='T4 · Soja 58 W · 174 ha a plantar',sub='OS-0420 com 70 ha de saldo pausado (ativo bloqueado) · '+plan('T4'),ch=[['pré-plantio','gray']])])
    L['T3']=dict(c='none',l='Milho colhido 12/09',cults=['Milho','Soja'],sum='Milho colhido 12/09 · soja prevista',
        rows=[dict(t='T3 · Milho AG 8700 · 96 ha',sub='Plantio real 20/10/2025 · colhido 12/09/2026',ch=[['colhido','gray']]),
              dict(t='Próxima: Soja 62 X · 96 ha',sub=plan('T3'),ch=[['sem plano','yellow']])])
    L['P1']=dict(c='purple',l=f"Feijão · DAP {_dap('2026-07-05')} · R5",cults=['Feijão','Soja'],sum=f"Feijão BRS Estilo · DAP {_dap('2026-07-05')} · R5",
        rows=[dict(t='P1 · Feijão BRS Estilo · 95 ha',sub=f"Plantio real 05/07/2026 (apontamento conferido) · DAP {_dap('2026-07-05')} · colheita prevista 10/10/2026 ({_em(_iso('2026-10-10'))})",ch=[['R5 · pré-floração','blue']]),
              dict(t='Próxima: Soja 58 W · 95 ha',sub=plan('P1'),ch=[['sem plano','yellow']])])
    L['P2']=dict(c='ok',l=f"Milho · DAP {_dap('2026-08-10')} · V10",cults=['Milho','Soja'],sum=f"Milho AG 8700 · DAP {_dap('2026-08-10')} · V10",
        rows=[dict(t='P2 · Milho AG 8700 · 80 ha',sub=f"Plantio real 10/08/2026 (apontamento conferido) · DAP {_dap('2026-08-10')} · colheita prevista 15/11/2026 ({_em(_iso('2026-11-15'))})",ch=[['V10','green']]),
              dict(t='Próxima: Soja 62 X · 80 ha',sub=plan('P2'),ch=[['sem plano','yellow']])])
    L['T7']=dict(c='yellow',l='Mamão · '+_idade(_iso('2025-03-10')),cults=['Mamão'],sum='Mamão Formosa · '+_idade(_iso('2025-03-10'))+' · produção',
        rows=[dict(t='T7 · Mamão Formosa · 42 ha',sub='Plantio real 10/03/2025 · idade '+_idade(_iso('2025-03-10'))+' · colheita semanal',ch=[['produção','yellow']])])
    L['C1']=dict(c='orange',l='Café · '+_idade(_iso('2019-01-15')),cults=['Café'],sum='Café Catuaí 144 · '+_idade(_iso('2019-01-15'))+' · granação',
        rows=[dict(t='C1 · Café Catuaí 144 · 38 ha',sub='Plantio real 15/01/2019 · idade '+_idade(_iso('2019-01-15'))+f" · colheita prevista 20/05/2027 ({_em(_iso('2027-05-20'))})",ch=[['granação','orange']])])
    assert set(L)==set(TIDS)
    return L
LAV=_lav()

# ---- preços e custo da operação (os mesmos do plano e do rendimento da safra) ----
PRECO={x['prod']:x['preco'] for p in D2.PLANOS for a in p['atividades'] for x in a['prods']}
_GEN={'Semente de soja':'Semente de soja · variedade do cultivo','Semente de milho':'Semente de milho · híbrido do cultivo','Semente de feijão':'Semente de feijão · variedade do cultivo'}
def _preco(p):
    if p in PRECO: return PRECO[p]
    for pre,k in _GEN.items():
        if p.startswith(pre): return PRECO.get(k)
    return None
def _nome(p,c):  # nome do insumo no cultivo (a semente leva a variedade)
    for pre,k in _GEN.items():
        if p==k: return pre+' '+c['variedade']
    return p
_CJ={c['op']:c for c in D2.CONJ}
COP={op:round(D2.custo_h(c)/c['rend'],2) for op,c in _CJ.items()}   # R$/ha da operação (conjunto e rendimento da safra)
def _data_atv(c,a):
    g=a.get('g') or {}; t=g.get('tipo')
    if t=='DAP': return _iso(c['plantio'])+_dt.timedelta(days=g['dias'])
    if t=='DATA' and g.get('data'): return _iso(g['data'])
    if t in ('DAPC','DANC') and c.get('colheita'): return _iso(c['colheita'])+_dt.timedelta(days=(g['dias'] if t=='DAPC' else -g['dias']))
    return None

# ---- previsto por talhão: plano da safra (dose × preço × área + operação); sem plano, as O.S. emitidas no talhão ----
ORD_REG={o['id']:o for o in _ordens_os()}
def _prev():
    out={}
    for t in TIDS:
        cs=[c for c in D2.CULTIVOS['S2627'] if c['local'].split('-')[0]==t and c['plano']]
        P=dict(fonte='',tot=0,ins=0,op=0,base=0,orig='',pend=[],lin=[])
        if cs:
            _somar_plano(P,cs,'área dos cultivos da safra 2026/27 (declarada no planejamento)')
        else:
            os_=[o for o in _ORD_MAPA if o[1]==[t] and o[0] in ORD_REG]   # irrigação só com água (módulo Irrigação) não entra no custo das O.S.
            if os_:
                P['fonte']='os'; P['orig']='área das O.S. emitidas no talhão (sem plano aplicado no cultivo)'
                for oid,*_ in os_:
                    o=ORD_REG[oid]; ar=o.get('area') or 0; P['base']=max(P['base'],ar)
                    vi=0
                    for x in o['ins']:
                        pr=_preco(x['p'])
                        if pr is None: P['pend'].append(f"Sem preço: {x['p']} ({oid}, não somado)"); continue
                        vi+=x['dose']*pr*ar
                    op=o['atv']['op']; co=COP.get(op)
                    if co is None: P['pend'].append(f'Operação {op} sem rendimento na safra ({oid}, não somada)')
                    vo=(co or 0)*ar; P['ins']+=vi; P['op']+=vo; P['lin'].append([oid+' · '+o['atv']['nome'],'',round(vi+vo,2)])
        P['tot']=round(P['ins']+P['op'],2); P['ins']=round(P['ins'],2); P['op']=round(P['op'],2)
        P['pend']=list(dict.fromkeys(P['pend'])); out[t]=P
    return out
def _somar_plano(P,cs,orig):
    P['fonte']='plano'; P['base']=sum(c['area'] for c in cs); P['orig']=orig
    for c in cs:
        pl=next(p for p in D2.PLANOS if p['id']==c['plano'])
        for a in pl['atividades']:
            vi=0
            for x in a['prods']:
                pr=_preco(x['prod'])
                if pr is None: P['pend'].append('Sem preço: '+_nome(x['prod'],c)+' (não somado)'); continue
                vi+=x['dose']*pr*c['area']
            co=COP.get(a['op']); vo=(co*c['area']) if co is not None else 0
            if co is None: P['pend'].append('Operação '+a['op']+' sem rendimento na safra (não somada)')
            P['ins']+=vi; P['op']+=vo; d=_data_atv(c,a)
            P['lin'].append([c['local']+' · '+a['nome'],(d.isoformat() if d else ''),round(vi+vo,2)])
    return P
def _fechar(P):
    P['tot']=round(P['ins']+P['op'],2); P['ins']=round(P['ins'],2); P['op']=round(P['op'],2); P['pend']=list(dict.fromkeys(P['pend'])); return P
PREV=_prev()


# ---- satélite: cinco índices (Sentinel-2 L2A, 10 m) e grade de pixels dentro de cada polígono com cultura ----
IDXN=['NDVI','NDRE','EVI','SAVI','NDMI']
IDX={'NDVI':dict(lim=[.30,.45,.60,.72,.82],pal='v',o='vigor geral da lavoura',
                d='NDVI · vigor: quanto de folha verde e ativa cobre o solo. Use para achar falhas e manchas de praga, doença ou irrigação ruim.'),
     'NDRE':dict(lim=[.12,.20,.27,.33,.40],pal='v',o='clorofila e nitrogênio com o dossel fechado',
                d='NDRE · clorofila: o verde por dentro da folha, ligado ao nitrogênio. Mostra diferença de nutrição quando o NDVI já está alto.'),
     'EVI':dict(lim=[.15,.25,.35,.45,.55],pal='v',o='vigor sem saturar em biomassa alta',
                d='EVI · vigor corrigido para solo e atmosfera. Separa lavouras fechadas, onde o NDVI fica no máximo.'),
     'SAVI':dict(lim=[.20,.32,.44,.54,.64],pal='v',o='vigor com solo exposto entre as linhas',
                d='SAVI · vigor descontando o solo entre as plantas. Melhor para mudas e lavoura em formação.'),
     'NDMI':dict(lim=[0,.10,.20,.30,.40],pal='m',o='umidade da vegetação (não é vigor)',
                d='NDMI · água na folha. Cai antes do NDVI quando falta água: alerta cedo de irrigação.')}
SATPAL={'v1':'#E4002B','v2':'#FF6A00','v3':'#FFD500','v4':'#B5E61D','v5':'#3FBF2A','v6':'#0B7A1E',   # vigor: falha → vigor alto
        'm1':'#8C510A','m2':'#D8B365','m3':'#F6E8C3','m4':'#90CAF9','m5':'#1E88E5','m6':'#0D47A1'}   # umidade (NDMI): paleta própria
CLSN={'v':['Falha','Fraco','Atenção','Médio','Bom','Vigor alto'],'m':['Muito seco','Seco','Moderado','Adequado','Úmido','Muito úmido']}
SAT={'21/09':dict(nuvem=4,aq='21/09 10:12',proc='21/09 14:40',v={'P1':[.84,.42,.58,.63,.34],'P2':[.76,.36,.51,.57,.27],'T7':[.66,.29,.44,.49,.18],'C1':'cloud'},nt={'C1':100,'P1':0,'P2':1,'T7':2},
                  manchas=[dict(t='T7',ha=1.2,val=.38,r=40,evo='cresceu · era 0,4 ha em 16/09',coord='−15,5612 · −54,2987',tipo='reboleira arredondada (praga, doença ou nematoide)')]),
     '16/09':dict(nuvem=0,aq='16/09 10:12',proc='16/09 15:05',v={'P1':[.82,.40,.56,.61,.33],'P2':[.73,.34,.49,.55,.26],'T7':[.71,.31,.47,.53,.21],'C1':[.70,.30,.45,.52,.22]},nt={},
                  manchas=[dict(t='T7',ha=0.4,val=.52,r=24,evo='nova',coord='−15,5612 · −54,2987',tipo='reboleira arredondada (praga, doença ou nematoide)')]),
     '06/09':dict(nuvem=32,aq='06/09 10:11',proc='06/09 16:20',v={'P1':[.78,.37,.52,.58,.31],'P2':'cloud','T7':'cloud','C1':[.72,.31,.46,.54,.23]},nt={'P2':64,'T7':71},manchas=[])}
CS=16  # lado do pixel no desenho (10 m no terreno, demonstrativo)
def _pixels():
    import math
    def dentro(tid,tp,geo,x,y):
        if tp=='circ':
            cx,cy,r=map(float,geo.split(',')); return (x-cx)**2+(y-cy)**2<=r*r
        pts=[tuple(map(float,p.split(','))) for p in geo.split()]; ins=False; j=len(pts)-1
        for i in range(len(pts)):
            xi,yi=pts[i]; xj,yj=pts[j]
            if ((yi>y)!=(yj>y)) and (x<(xj-xi)*(y-yi)/(yj-yi)+xi): ins=not ins
            j=i
        return ins
    out={}
    for k,(tid,tp,geo) in enumerate(GEO):
        cel=[]
        for gy in range(0,620,CS):
            for gx in range(0,1000,CS):
                cx,cy=gx+CS/2,gy+CS/2
                if not dentro(tid,tp,geo,cx,cy): continue
                n=.55*math.sin(cx*.045+k)*math.cos(cy*.038+k*1.7)+.45*math.sin((cx+cy)*.021+k*2.3)
                n+=(((gx*73856093)^(gy*19349663))%1000)/1000*.16-.08
                d=round(math.hypot(cx-650,cy-556),1) if tid=='T7' else -1
                cel.append([gx,gy,round(max(-1,min(1,n)),3),d])
        out[tid]=cel
    return out
PX=_pixels()

# ---------------- Fazenda Lagoa Grande (real, Lagoa Grande · MG) ----------------
# 23 pivôs centrais do KML do proprietário (ponto central + hectares declarados; o círculo sai do centro e da área) sobre a imagem
# real do Sentinel-2 L2A (Copernicus/ESA, catálogo Earth Search, sem conta) com os cinco índices calculados por pixel dentro de cada
# pivô (dados_lagoa/processar.py). Reserva legal, APP, perímetros e outorgas ficam no cadastro da fazenda, fora do mapa.
import os as _os
_LGD=__import__('dados_lagoa_fonte').DIR   # real só no Mac; sintético fora dele
_LGROT=__import__('dados_lagoa_fonte').ROTULO   # '' com dado real; 'Demonstração sintética' fora do Mac (rótulo visível no mapa)
LG=json.load(open(_os.path.join(_LGD,'lagoa_s2_resumo.json'),encoding='utf-8'))
LG_GEO=json.load(open(_os.path.join(_LGD,'lagoa_pivos.geojson'),encoding='utf-8'))
LG_IDS=[p['id'] for p in LG['pivos']]
def _lg_key(c): y,m,d=c['dt'].split('-'); return f'{d}/{m}'
def _lg_hora(c): h,mi=map(int,c['hora_utc'].split(':')); return f'{(h-3)%24:02d}:{mi:02d}'
for _c in LG['cenas']:   # cenas reais entram no mesmo registro de cenas do mapa (chaves dd/mm), depois das demonstrativas
    _y,_m,_d=_c['dt'].split('-')
    SAT[_lg_key(_c)]=dict(nuvem=_c['nuvem'],aq=f"{_d}/{_m}/{_y} {_lg_hora(_c)} (Brasília)",proc=(_LGROT+' · imagem e índices gerados, sem dado real') if _LGROT else 'processamento L2A da ESA (Copernicus) · catálogo Earth Search',
        v={p:[_c['est'][p][n]['med'] for n in IDXN] for p in LG_IDS},nt={p:_c['est'][p]['nuvem'] for p in LG_IDS},manchas=[],png=_c['png'],real=True)
_LGC={DLS.PID_DE[c['local']]:c for c in DLS.CULTIVOS}
def _lav_lg(p,c):
    n=p['nome'].split()[-1]
    if not c: return dict(c='gray',l='sem cultivo cadastrado',cults=[],sum='sem cultivo na safra',rows=[dict(t=f"Pivô {n} · {nfb(p['ha'])} ha",sub='Cultivo ainda não cadastrado na safra',ch=[['sem cultivo','gray']])])
    d0=_iso(c['plantio']); dias=(HOJE-d0).days; pl=next(x for x in D2.PLANOS if x['id']==c['plano']); ren=DLS.RENOVACAO.get(int(n))
    if dias<0:
        est='renovação · preparo' if ren else 'preparo de área'; cc,ch='gray','gray'; lab='Mamão · plantio '+_em(d0)
        sub=f"Plantio previsto {_br(d0)} · {_em(d0)} · plano {pl['nome']} v{pl['versao']}"+(' · '+ren if ren else '')
    else:
        if dias<90: est,cc,ch='formação inicial','ok','green'
        elif dias<240: est,cc,ch='formação · pré-florada','purple','blue'
        elif dias<300: est,cc,ch='início da produção','orange','orange'
        else: est,cc,ch='produção','yellow','yellow'
        idade=(f'{dias} dias' if dias<60 else _idade(d0)); lab='Mamão · '+idade
        sub=f"Plantio real {_br(d0)} · idade {idade} · DAP {dias} · plano {pl['nome']} v{pl['versao']}"
    return dict(c=cc,l=lab,cults=['Mamão'],sum=f"Mamão Formosa {c['variedade']} · {est}",
                rows=[dict(t=f"Pivô {n} · Mamão Formosa {c['variedade']} · {nfb(c['area'])} ha",sub=sub,ch=[[est,ch]])])
_PV_ULT=[None]
for _p in LG['pivos']:
    _n=_p['nome'].split()[-1]; _ha=_p['ha']; _per=2*3.141592653589793*_p['r_m']/1000
    TAL[_p['id']]=dict(ha=_ha,cult='Pivô',fase='sem cultivo')
    PERIM[_p['id']]=f'{_per:.1f}'.replace('.',',')
    INTEG[_p['id']]=DLS.INTEG.get(_p['id'],['none','sem pendência'])
    _c=_LGC.get(_p['id'])
    LAV[_p['id']]=_lav_lg(_p,_c)
    PREV[_p['id']]=_fechar(dict(fonte='',tot=0,ins=0,op=0,base=0,orig='',pend=[],lin=[])) if not _c else _fechar(_somar_plano(dict(fonte='',tot=0,ins=0,op=0,base=0,orig='',pend=[],lin=[]),[_c],'área do pivô (KML) · Safra Mamão 2026/27'))
_RGB=json.load(open(_os.path.join(_LGD,'lagoa_rgb.json'),encoding='utf-8'))
_RGBK={'25/09':'lagoa_rgb_20260925.png','10/09':'lagoa_rgb_20260910.png'}
LG_DADOS=dict(rot=_LGROT,ids=LG_IDS,rgb=dict(cantos=_RGB['lagoa_rgb_20260925.png']['cantos'],png=_RGBK),pivos=LG['pivos'],cantos=LG['cantos'],geo=LG_GEO,H=LG['H'],W=LG['W'],
              cenas=[dict(k=_lg_key(c),png=c['png']) for c in LG['cenas']],
              bbox=[[min(p['lon'] for p in LG['pivos'])-0.006,min(p['lat'] for p in LG['pivos'])-0.006],[max(p['lon'] for p in LG['pivos'])+0.006,max(p['lat'] for p in LG['pivos'])+0.006]],
              ha=round(sum(p['ha'] for p in LG['pivos'])))


LCOR_OP={'ok':('#7FAE68','#FFFFFF'),'good':('#5F8F55','#FFFFFF'),'lime':('#A9C06A','#FFFFFF'),'yellow':('#D4B25A','#FFFFFF'),'orange':('#D98A4E','#FFFFFF'),'red':('#C8553D','#FFFFFF'),'gray':('#C9CFCB','#FFFFFF'),'blue':('#6E9FC6','#FFFFFF'),'navy':('#44739A','#FFFFFF'),'none':('#E4E9DF','#FFFFFF'),'cloud':('#C9CFCB','#FFFFFF'),'purple':('#9B8BC4','#FFFFFF'),'sat':('#C9CFCB','#FFFFFF')}
NOME_LAY={'MIP/MID':'Pragas e doenças','O.S./prazos':'Ordens de serviço','Colheita/produtividade':'Colheita e produtividade'}
_SEMPLANO={t:(not any(c['plano'] for c in D2.CULTIVOS['S2627'] if c['local'].split('-')[0]==t)) for t in TIDS}
_PLANT=sum(x for x in (95,80,42,38,30)); _PRE=312+298+174
_LG_ROT={p['rot'].replace('P','Pivô ',1):p['id'] for p in LG['pivos']}   # 'Pivô 1' (local do cultivo) → PV01
_SEMPLANO.update({t:(not any(c['plano'] for c in D2.CULTIVOS[DLS.SAFRA['id']] if _LG_ROT.get(c['local'])==t)) for t in LG_IDS})
# ---- insumos (CTL-4 · DEM-05): o Mapa calcula com a mesma conta do Planejar safra e da Compra (demFazenda, cal01.js) com ordens, físico apto,
# reservas e recebimentos do MESMO cenário vivo (cenDemEntradas); aqui só vão as partes fixas por fazenda: ocorrências do plano das safras abertas
# e a área dos cultivos por talhão (rateio da O.S. de vários talhões). Antes havia uma conta própria (estoque das duas fazendas, reserva contada
# duas vezes) e, depois, estoque fixo da semente ao lado das ordens vivas (revisão do CTL-4, achado 1).
def _dem_mapa():
    tid={**{t:t for t in TIDS},**_LG_ROT}; faz={}
    for f,saf in (('Santa Rita','S2627'),('Santa Rita','S27SF'),('Lagoa Grande',DLS.SAFRA['id'])):
        x=D2.dem_fixas(saf); aT={}; vistos=set()
        for o in x['occ']:
            cid=o['k'].split('|')[0]
            if o['saf']!=saf or cid in vistos: continue
            vistos.add(cid); k=tid.get(o['local'],o['local'].split('-')[0]); aT[k]=aT.get(k,0)+o['area']
        x['areaT']=aT; faz[saf]=x   # por safra (filtro Safra da faixa, 15/10/2026)
    return dict(faz=faz,b=dict(osb=D2.os_base(),est=D2.est_base()),tid=tid)
SEMCULT.update({t:'sem lavoura' for t in LG_IDS if LAV[t]['c']=='gray'})
_GEO_TXT=_geo(); _GEO_TXT.update({p['id']:f"círculo pelo centro do KML e pela área declarada · raio {nfb(p['r_m'])} m" for p in LG['pivos']})
import dados_cad as DC
def _cad0():
    import areas.cad_fazendas as CF
    pk=lambda r: dict(id=r['id'],v=r['v'])
    return dict(faz=[pk(r) for r in CF._faz_rows()],tal=[pk(r) for r in CF._tal_rows()])
MDATA=dict(cad0=_cad0(),hoje_iso=HOJE.isoformat(),motivos=DC.MOTIVOS_DIF,tal={t:dict(ha=TAL[t]['ha'],cult=TAL[t]['cult'],per=PERIM[t]) for t in TIDS+LG_IDS},lg=LG_DADOS,tids=TIDS,lays=LAYS,
           filt={k:[dict(k=a,l=b,o=c) for a,b,c in v] for k,v in FILT.items()},ord=ORD,integ=INTEG,sat=SAT,semcult=SEMCULT,
           idxn=IDXN,idx=IDX,satpal=SATPAL,clsn=CLSN,px=PX,cs=CS,lav=LAV,prev=PREV,preco=PRECO,gen=_GEN,cop=COP,dem=_dem_mapa(),
           lim30=(HOJE+_dt.timedelta(days=30)).isoformat(),hoje=_br(HOJE),semplano=_SEMPLANO,
           lavstrip=[['Com lavoura',f'{_PLANT} ha','Área com lavoura'],['Pré-plantio',f'{nfb(_PRE)} ha','Área em pré-plantio'],['Colhido','96 ha','Área colhida'],
                     ['Cultivos',str(len(D2.CULTIVOS["S2627"])),'Cultivos na safra 2026/27']],   # rótulo curto; o completo na dica (13/10)
           geo=_GEO_TXT,lcop=LCOR_OP,nome=NOME_LAY,
           # camada Análises de solo: talhão do mapa → (fazenda, talhão dos laudos do AG-02); a Lagoa Grande usa o nome do pivô ('Pivô 12')
           soloTal={**{t:['Santa Rita',t] for t in TIDS},**{pid:['Lagoa Grande',nome] for nome,pid in _LG_ROT.items()}},
           geoc={t:[tp,geo] for t,tp,geo in GEO})   # geometria do desenho da Santa Rita: pontos do laudo no polígono ou no círculo

# ---- filtros da faixa Safra e Cultura (15/10/2026, proprietário: "Falta filtro de safra e cultura"): cultivos de cada safra por talhão do
# mapa; Lavoura, Custos (previsto do plano) e "sem plano" das outras safras. A safra corrente segue com LAV/PREV (ocupação atual + plano).
_SAFK={'Santa Rita':{'2026/27':'S2627','Safrinha 2027':'S27SF','2025/26':'S2526'},'Lagoa Grande':{'2026/27':DLS.SAFRA['id']}}
_SAFN={sk:n for m in _SAFK.values() for n,sk in m.items()}
def _tid_de(loc): return DLS.PID_DE.get(loc) or loc.split('-')[0]
def _cs_saf():
    out={}
    for sk in _SAFN:
        d=out.setdefault(sk,{})
        for c in D2.CULTIVOS[sk]:
            t=_tid_de(c['local'])
            if t not in TAL: continue
            d.setdefault(t,[]).append(dict(cult=c['cultura'].split()[0],loc=c['local'],var=c.get('variedade') or '',area=c['area'],
                                           plantio=c.get('plantio') or '',colheita=c.get('colheita') or '',plano=c.get('plano') or ''))
    return out
CS_SAF=_cs_saf()
def _plano_nome(pid):
    pl=next((p for p in D2.PLANOS if p['id']==pid),None); return f"plano {pl['nome']} v{pl['versao']}" if pl else 'sem plano aplicado'
def _lav_saf(sk):
    L={}; fim=sk=='S2526'
    for t,cs in CS_SAF[sk].items():
        cults=sorted({c['cult'] for c in cs}); c0=min(cs,key=lambda c:c['plantio'] or '9')
        lab=' + '.join(cults)+((' · plantio '+_br(_iso(c0['plantio']))) if c0['plantio'] else '')
        rows=[dict(t=f"{c['loc']} · {c['cult']}{(' '+c['var']) if c['var'] else ''} · {nfb(c['area'])} ha",
                   sub=(('Plantio '+_br(_iso(c['plantio']))) if c['plantio'] else 'Plantio a definir')+((' · colheita '+_br(_iso(c['colheita']))) if c['colheita'] else '')+' · '+_plano_nome(c['plano']),
                   ch=[['safra encerrada' if fim else 'planejado','gray']]) for c in cs]
        L[t]=dict(c='none' if fim else 'gray',l=lab,cults=cults,sum=lab,rows=rows)
    return L
def _prev_saf(sk):
    out={}
    for t in CS_SAF[sk]:
        P=dict(fonte='',tot=0,ins=0,op=0,base=0,orig='',pend=[],lin=[])
        cp=[c for c in D2.CULTIVOS[sk] if _tid_de(c['local'])==t and c['plano']]
        if cp: _somar_plano(P,cp,f'área dos cultivos da safra {_SAFN[sk]} (declarada no planejamento)')
        out[t]=_fechar(P)
    return out
_OUTRAS=[sk for sk in _SAFN if sk not in ('S2627',DLS.SAFRA['id'])]
MDATA.update(safk=_SAFK,safcur={'Santa Rita':'S2627','Lagoa Grande':DLS.SAFRA['id']},csaf=CS_SAF,   # csaf: M.cs é o lado da célula do desenho
            
             lavS={sk:_lav_saf(sk) for sk in _OUTRAS},prevS={sk:_prev_saf(sk) for sk in _OUTRAS},
             semplanoS={sk:{t:not any(c['plano'] for c in cs) for t,cs in CS_SAF[sk].items()} for sk in _OUTRAS})

# ---- camada Irrigação: balanço hídrico e situação de hoje por área (IR-01..IR-04 no menu Agrícola) ----
# Fonte única: dados_irrigacao.py (semente) + irrigacao_estado.js (estado gravado 'talhao-os-irrigacao-v1'); irrMapa() no cliente.
# Santa Rita: P2 11,2 mm medido · P1 ≈8,4 mm (sonda suspeita) · T7 ≈10,0 mm (sonda sem dado). Lagoa Grande: balanço demonstrativo
# sobre os pivôs reais com as tarefas do dia geradas pelo balanço (OS-0601…); OS-0506/OS-0507 são as fertirrigações do cenário.
import dados_irrigacao as DI
MDATA['irr']={}   # preenchido por irrMapa() a cada desenho

MAP_JS=r'''
const IDXN=M.idxn;
// ===== fazenda do mapa: Lagoa Grande (real: MapLibre GL + Sentinel-2) · Santa Rita (desenho demonstrativo) =====
let FAZ='Lagoa Grande';
function TIDS(){ return FAZ==='Lagoa Grande'?M.lg.ids:M.tids; }
// ===== faixa de filtros (15/10/2026): Safra escolhe os cultivos (Lavoura, Custos, Insumos, O.S. e Colheita da safra); Cultura deixa só os
// talhões com aquela cultura (na safra corrente: a ocupação atual e o planejado); os demais ficam neutros, "fora do filtro", em toda camada.
// ALV: alvos escolhidos na camada Pragas e doenças (null = todos).
let SAF='2026/27', CULT='Todas', ALV=null;
function safOpts(){ return Object.keys(M.safk[FAZ]||{}); }
function safK(){ return (M.safk[FAZ]||{})[SAF]||''; }
function safCur(){ return safK()===M.safcur[FAZ]; }
function cultsDe(t){ const cs=((M.csaf[safK()]||{})[t]||[]).map(c=>c.cult); const a=safCur()?((M.lav[t]||{}).cults||[]).concat(cs):cs; return a.filter((x,i)=>a.indexOf(x)===i); }
function cultOpts(){ const s={}; TIDS().forEach(t=>cultsDe(t).forEach(c=>{ s[c]=1; })); return ['Todas'].concat(Object.keys(s).sort((a,b)=>a.localeCompare(b,'pt-BR'))); }
function inF(t){ return CULT==='Todas'||cultsDe(t).indexOf(CULT)>=0; }
function lavOf(t){ if(safCur()) return M.lav[t]; return ((M.lavS[safK()]||{})[t])||{c:'none',l:'sem cultivo na safra',cults:[],sum:'sem cultivo na safra '+SAF,rows:[]}; }
const PREV0={fonte:'',tot:0,ins:0,op:0,base:0,orig:'',pend:[],lin:[]};
function prevOf(t){ return safCur()?M.prev[t]:(((M.prevS[safK()]||{})[t])||PREV0); }
function semPlanoOf(t){ return safCur()?!!M.semplano[t]:!!((M.semplanoS[safK()]||{})[t]); }
// na safra corrente vale o que está no campo agora (todas as ordens e cultivos em produção, como antes do filtro); outra safra: só as dela
function osSaf(o){ return safCur()||(o.saf||'2026/27')===SAF; }
function alvOk(v){ return !ALV||ALV.indexOf((mipP(v)||{}).alvo)>=0; }
function alvTxt(){ return ALV.length===1?ALV[0].toLowerCase():ALV.length+' alvos'; }
function alvosFaz(){ const s={}; const ts=TIDS(); ts.forEach(t=>(MIPD.prots[t]||[]).forEach(p=>{ const a=(MIPD.prot[p]||{}).alvo; if(a) s[a]=1; }));
  Object.values(mipGet().vis).forEach(v=>{ if(ts.indexOf(v.tal)>=0){ const a=(mipP(v)||{}).alvo; if(a) s[a]=1; } }); return Object.keys(s).sort((a,b)=>a.localeCompare(b,'pt-BR')); }
function isLG(t){ return String(t).indexOf('PV')===0; }
function fopts(l){ const gs=M.filt[l]||[]; if(l===SOLO_L) return soloFopts(gs); if(l!=='Satélite') return gs; const ks=(FAZ==='Lagoa Grande')?M.lg.cenas.map(c=>c.k):Object.keys(M.sat).filter(k=>!M.sat[k].real);
  return gs.map(g=>g.k==='dt'?Object.assign({},g,{o:ks}):g); }
const LGI={map:null,carregando:false,pronto:false,px:null,pxP:null,el:null,markers:{},png:'',pxKey:'',lims:{},css:false,erro:''};
const LG_VAZIO='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
function lgDeq(q){ return q/125-1; }
function lgCss(){ if(LGI.css) return; LGI.css=true; const s=document.createElement('style');
  s.textContent='.maplibregl-map{position:relative;overflow:hidden;-webkit-tap-highlight-color:rgba(0,0,0,0)}.maplibregl-canvas{position:absolute;left:0;top:0}'
   +'.maplibregl-canvas-container.maplibregl-interactive{cursor:grab}.maplibregl-canvas-container.maplibregl-interactive:active{cursor:grabbing}.maplibregl-marker{position:absolute;top:0;left:0;will-change:transform}'
   +'.lg-rot{display:flex;flex-direction:column;align-items:center;pointer-events:none;text-align:center;font-family:Manrope,system-ui,sans-serif;color:#fff;text-shadow:0 0 3px #000,0 0 3px #000,0 0 7px rgba(0,0,0,.7)}'
   +'.lg-rot b{font-size:15px;font-weight:800;line-height:1.1}.lg-rot span{font-size:11px;font-weight:700;max-width:120px;line-height:1.15}.lg-rot.peq span{display:none}';

  document.head.appendChild(s); }
function lgLib(){ return new Promise((ok,er)=>{ if(window.maplibregl) return ok(); const s=document.createElement('script'); s.src='https://cdn.jsdelivr.net/npm/maplibre-gl@5.9.0/dist/maplibre-gl.js';
  s.onload=()=>ok(); s.onerror=()=>er(new Error('não foi possível carregar o mapa (MapLibre)')); document.head.appendChild(s); }); }
function lgPix(){ if(!LGI.pxP) LGI.pxP=fetch('lagoa_s2.json').then(r=>{ if(!r.ok) throw new Error('pixels '+r.status); return r.json(); }).then(j=>{ const b64=(s)=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
    const pix=new Uint16Array(b64(j.pix).buffer); const dono=b64(j.dono); const cen={};
    j.cenas.forEach(c=>{ const p=c.dt.split('-'); const k=p[2]+'/'+p[1]; cen[k]={}; j.idx.forEach(n=>{ cen[k][n]=b64(c.q[n]); }); });
    LGI.px={pix,dono,cen,H:j.H,W:j.W}; LGI.lims={}; return LGI.px; }); return LGI.pxP; }
// limites de cor no mapa real: absoluto (faixas do índice) · fazenda (P2–P98 dos pixels dos pivôs) · talhão (P2–P98 do pivô)
function lgLims(f,t){ if(f.ctr==='Absoluto'||!LGI.px) return M.idx[f.idx].lim; const key=f.dt+'|'+f.idx+'|'+f.ctr+'|'+(f.ctr==='Talhão'?t:''); if(LGI.lims[key]) return LGI.lims[key];
  const P=LGI.px; const a=P.cen[f.dt]&&P.cen[f.dt][f.idx]; if(!a) return M.idx[f.idx].lim; const ti=(f.ctr==='Talhão'&&t)?M.lg.ids.indexOf(t):-1; const vals=[];
  for(let i=0;i<a.length;i++){ if(a[i]===255) continue; if(ti>=0&&P.dono[i]!==ti) continue; vals.push(lgDeq(a[i])); }
  if(!vals.length) return M.idx[f.idx].lim; vals.sort((x,y)=>x-y); const q=(p)=>vals[Math.round(p*(vals.length-1))];
  // talhão: faixas com a mesma quantidade de pixels (sextis) → cada pivô mostra onde está melhor e pior; fazenda: P2–P98 em faixas iguais
  if(f.ctr==='Talhão') return (LGI.lims[key]=[1,2,3,4,5].map(i=>Math.round(q(i/6)*1000)/1000));
  const lo=q(.02), hi=q(.98); const st=((hi-lo)/6)||0.01;
  return (LGI.lims[key]=[1,2,3,4,5].map(i=>Math.round((lo+st*i)*1000)/1000)); }
function lgCanvas(fs){ const P=LGI.px; const q=P.cen[fs.dt][fs.idx]; const cv=LGI.cv; const ctx=cv.getContext('2d'); const img=ctx.createImageData(P.W,P.H);
  const lims={}; const LF=fs.ctr==='Talhão'?null:lgLims(fs,null); const rgb={}; const hx=(h)=>[parseInt(h.slice(1,3),16),parseInt(h.slice(3,5),16),parseInt(h.slice(5,7),16)];
  for(let i=0;i<q.length;i++){ if(q[i]===255) continue; const t=M.lg.ids[P.dono[i]]; if(M.semcult[t]) continue; const L=LF||lims[t]||(lims[t]=lgLims(fs,t)); const k=kOf(lgDeq(q[i]),L); const c=rgb[k]||(rgb[k]=hx(satCor(fs.idx,k)));
    const o=4*(P.pix[2*i]*P.W+P.pix[2*i+1]); img.data[o]=c[0]; img.data[o+1]=c[1]; img.data[o+2]=c[2]; img.data[o+3]=240; }
  ctx.putImageData(img,0,0); lgPisca(); }
function lgSoloCanvas(f){ const P=LGI.px; const cv=LGI.cv; const ctx=cv.getContext('2d'); const img=ctx.createImageData(P.W,P.H); const G=soloGrade(f); const ind=SOLO_IND[f.ind];
  const hx=(h)=>[parseInt(h.slice(1,3),16),parseInt(h.slice(3,5),16),parseInt(h.slice(5,7),16)]; const rgb={}; const LF=f.ctr==='Fazenda'?soloLims(f,null,G):null;
  const pinta=(i,c,a)=>{ const o=4*(P.pix[2*i]*P.W+P.pix[2*i+1]); img.data[o]=c[0]; img.data[o+1]=c[1]; img.data[o+2]=c[2]; img.data[o+3]=a; };
  Object.keys(G).forEach(t=>{ const o=G[t]; if(!o.ix||!o.vals.length||!inF(t)) return; const L=f.ctr==='Talhão'?soloLims(f,t,G):LF;
    o.ix.forEach((i,j)=>{ const h=soloCor(f,ind,o.vals[j],L); pinta(i,rgb[h]||(rgb[h]=hx(h)),240); }); });
  ctx.putImageData(img,0,0);
  Object.keys(G).forEach(t=>{ const o=G[t]; if(!o.ix||!inF(t)) return; o.pts.forEach(p=>{ ctx.fillStyle='#FFFFFF'; ctx.fillRect(Math.round(p.x)-2,Math.round(p.y)-2,5,5); ctx.fillStyle='#15201A'; ctx.fillRect(Math.round(p.x)-1,Math.round(p.y)-1,3,3); }); });
  lgPisca(); }
function lgLimpa(){ const cv=LGI.cv; cv.getContext('2d').clearRect(0,0,cv.width,cv.height); lgPisca(); }
// a fonte canvas reenvia a textura só enquanto toca: toca um instante depois de cada redesenho
function lgPisca(){ const src=LGI.map&&LGI.map.getSource('px'); if(!src) return; try{ src.play(); clearTimeout(LGI._pz); LGI._pz=setTimeout(()=>{ try{ src.pause(); }catch(e){} },250); }catch(e){} }
function lgLL(row,col){ const C=M.lg.cantos, P=M.lg; const u=col/P.W, w=row/P.H; return [C[0][0]+u*(C[1][0]-C[0][0])+w*(C[3][0]-C[0][0]), C[0][1]+u*(C[1][1]-C[0][1])+w*(C[3][1]-C[0][1])]; }
function lgPixelAt(ll,id){ const C=M.lg.cantos; const P=LGI.px; if(!P) return -1;
  const u=(ll.lng-C[0][0])/(C[1][0]-C[0][0]), w=(ll.lat-C[0][1])/(C[3][1]-C[0][1]); const col=Math.floor(u*P.W), row=Math.floor(w*P.H); const ti=M.lg.ids.indexOf(id);
  for(let i=0;i<P.dono.length;i++){ if(P.pix[2*i]===row&&P.pix[2*i+1]===col) return P.dono[i]===ti?i:-1; } return -1; }
function fmtLL(ll){ const f=(n)=>(n<0?'−':'')+nfx(Math.abs(n),5); return f(ll[1])+' · '+f(ll[0]); }
function lgClick(self,id,ll){ const s=self.state; if(s.dw) return;   // desenhando: o clique marca ponto (talmapa.js)
  if(s.medir){ self.setState({g2toast:'Medição · '+id.replace('PV','Pivô ').replace(' 0',' ')+': '+nfx(M.tal[id].ha)+' ha · perímetro ≈ '+M.tal[id].per+' km (círculo do KML).'}); return; }
  if(s.cvis){ criarVis(self,[id],{tsel:[id]}); return; }
  if(s.selm){ const ss=(s.tsel||[]).filter(isLG); const i=ss.indexOf(id); if(i>=0) ss.splice(i,1); else ss.push(id); self.setState({tsel:ss,px:null}); return; }
  if(lay(self)==='Satélite'&&LGI.px){ const k=lgPixelAt(ll,id); if(k>=0){ self.setState({tsel:[id],px:{t:id,lg:k,ll:[ll.lng,ll.lat]},mpa:null}); return; } }
  const ss=s.tsel||[]; self.setState({tsel:(ss.length===1&&ss[0]===id)?[]:[id],px:null,mpa:null}); }
// a imagem sempre cobre a área do mapa: limita o arraste à imagem e o afastamento ao zoom que ainda a preenche
function lgLimites(m){ const C=M.lg.rgb.cantos; const x0=Math.max(C[0][0],C[3][0]), x1=Math.min(C[1][0],C[2][0]), y0=Math.max(C[2][1],C[3][1]), y1=Math.min(C[0][1],C[1][1]);
  const el=m.getContainer(); const W=el.clientWidth||1, H=el.clientHeight||1; const my=(l)=>Math.log(Math.tan(Math.PI/4+l*Math.PI/360));
  const zw=Math.log2(W*360/(512*(x1-x0))), zh=Math.log2(H*2*Math.PI/(512*Math.abs(my(y1)-my(y0)))); const zmin=Math.max(zw,zh)+0.02;
  try{ m.setMinZoom(zmin); m.setMaxBounds([[x0,y0],[x1,y1]]); if(m.getZoom()<zmin) m.setZoom(zmin); }catch(e){} }
function lgEnsure(self){ const el=document.getElementById('mapa-real'); if(!el) return; if(LGI.map&&LGI.el===el) return; if(LGI.carregando&&LGI.el===el) return;
  if(LGI.map){ try{ LGI.map.remove(); }catch(e){} LGI.map=null; LGI.pronto=false; LGI.markers={}; LGI.png=''; LGI.pxKey=''; }
  LGI.carregando=true; LGI.el=el; lgCss(); try{ window.__LGI=LGI; }catch(e){}   // inspeção nos testes
  lgLib().then(()=>{ const m=new maplibregl.Map({container:el,style:{version:8,sources:{},layers:[{id:'bg',type:'background',paint:{'background-color':'#DDE5D6'}}]},
      bounds:M.lg.bbox,fitBoundsOptions:{padding:16},attributionControl:false,dragRotate:false,pitchWithRotate:false,maxZoom:17.5,minZoom:11,renderWorldCopies:false});
    LGI.map=m; m.touchZoomRotate.disableRotation();
    m.on('load',()=>{ const c0=M.lg.cenas[0]; const p0=M.lg.rgb.png[c0.k];
      m.addSource('rgb',{type:'image',url:p0,coordinates:M.lg.rgb.cantos}); m.addLayer({id:'rgb',type:'raster',source:'rgb',paint:{'raster-fade-duration':0}}); LGI.png=p0;
      lgLimites(m); m.on('resize',()=>lgLimites(m));
      LGI.cv=document.createElement('canvas'); LGI.cv.width=M.lg.W; LGI.cv.height=M.lg.H;
      m.addSource('px',{type:'canvas',canvas:LGI.cv,coordinates:M.lg.cantos,animate:false}); m.addLayer({id:'px',type:'raster',source:'px',paint:{'raster-resampling':'nearest','raster-fade-duration':0}}); LGI.pxKey='none';
      m.addSource('pv',{type:'geojson',data:M.lg.geo});
      m.addLayer({id:'pv-fill',type:'fill',source:'pv',paint:{'fill-color':'#ffffff','fill-opacity':0}});
      m.addLayer({id:'pv-line',type:'line',source:'pv',paint:{'line-color':'#FFFFFF','line-width':1.8}});
      m.addLayer({id:'pv-sel',type:'line',source:'pv',filter:['in',['get','id'],['literal',[]]],paint:{'line-color':'#15201A','line-width':4}});
      m.addSource('pxs',{type:'geojson',data:{type:'FeatureCollection',features:[]}}); m.addLayer({id:'pxs',type:'line',source:'pxs',paint:{'line-color':'#15201A','line-width':2.5}});
      m.on('click','pv-fill',(e)=>{ const f=e.features&&e.features[0]; if(f) lgClick(self,f.properties.id,e.lngLat); });
      m.on('mouseenter','pv-fill',()=>{ m.getCanvas().style.cursor='pointer'; }); m.on('mouseleave','pv-fill',()=>{ m.getCanvas().style.cursor=''; });
      tmCamadas(self,m);   // talhões desenhados ou importados, desenho em andamento e prévia do arquivo (talmapa.js)
      M.lg.pivos.forEach(p=>{ const d=document.createElement('div'); d.className='lg-rot'+(p.ha<20?' peq':''); d.appendChild(document.createElement('b')); d.appendChild(document.createElement('span'));
        LGI.markers[p.id]=new maplibregl.Marker({element:d,anchor:'center'}).setLngLat([p.lon,p.lat]).addTo(m); });
      LGI.pronto=true; LGI.carregando=false; self.setState({lgok:Date.now()}); });
  }).catch(e=>{ LGI.erro=String(e.message||e); LGI.carregando=false; self.setState({lgerr:LGI.erro}); }); }
function lgSync(self){ const m=LGI.map; if(!m||!LGI.pronto) return; const st=self.state; const l=lay(self); const f=flt(self,l); const sel=(st.tsel||[]).filter(isLG);
  try{ m.resize(); }catch(e){}
  const fs=flt(self,'Satélite'); const dt=(l==='Satélite')?fs.dt:M.lg.cenas[0].k; const cena=M.lg.cenas.find(c=>c.k===dt)||M.lg.cenas[0];
  const pr=M.lg.rgb.png[cena.k]||M.lg.rgb.png[M.lg.cenas[0].k]; if(LGI.png!==pr){ LGI.png=pr; m.getSource('rgb').updateImage({url:pr,coordinates:M.lg.rgb.cantos}); }
  const cor=['match',['get','id']], op=['match',['get','id']];
  M.lg.ids.forEach(t=>{ const c=cls(l,f,t); const hx=c.c==='sat'?c.hex:((M.lcop[c.c]||M.lcop.none)[0]);
    cor.push(t,hx); op.push(t,(c.c==='none')?0:(c.c==='sat'?(LGI.px?0:0.6):(c.c==='cloud'?0.35:0.55)));
    const mk=LGI.markers[t]; if(mk){ const el=mk.getElement(); const rot=(M.lg.pivos.find(p=>p.id===t)||{}).rot||t; el.children[0].textContent=rot; el.children[1].textContent=c.l; el.setAttribute('role','img'); el.setAttribute('aria-label',rot+': '+c.l); } });
  cor.push('#ffffff'); op.push(0); m.setPaintProperty('pv-fill','fill-color',cor); m.setPaintProperty('pv-fill','fill-opacity',op);
  m.setFilter('pv-sel',['in',['get','id'],['literal',sel]]);
  if(l==='Satélite'){ if(!LGI.px){ lgPix().then(()=>self.setState({lgpx:Date.now()})).catch(e=>self.setState({g2toast:'Pixels do satélite indisponíveis: '+e.message})); }
    else { const key=[fs.dt,fs.idx,fs.ctr].join('|'); if(LGI.pxKey!==key){ LGI.pxKey=key; lgCanvas(fs); } } }
  else if(l===SOLO_L){ if(!LGI.px){ lgPix().then(()=>self.setState({lgpx:Date.now()})).catch(e=>self.setState({g2toast:'Pixels do mapa indisponíveis: '+e.message})); }
    else { const key='solo|'+[f.lau,f.prof,f.ind,f.ctr,CULT,SAF].join('|')+'|'+((soloMapLs().c||{}).rev||0); if(LGI.pxKey!==key){ LGI.pxKey=key; lgSoloCanvas(f); } } }
  else if(LGI.pxKey!=='none'){ LGI.pxKey='none'; lgLimpa(); }
  const px=st.px; let feats=[];
  if(l==='Satélite'&&px&&px.lg!==undefined&&LGI.px){ const r=LGI.px.pix[2*px.lg], c=LGI.px.pix[2*px.lg+1]; feats=[{type:'Feature',properties:{},geometry:{type:'Polygon',coordinates:[[lgLL(r,c),lgLL(r,c+1),lgLL(r+1,c+1),lgLL(r+1,c),lgLL(r,c)]]}}]; }
  m.getSource('pxs').setData({type:'FeatureCollection',features:feats});
  tmSync(self); }

const SEV=['red','orange','yellow','cloud','lime','ok','good','navy','blue','purple','gray','none'];
const PZC={'atrasada':'red','vence hoje':'orange','até 3 dias':'yellow','no prazo':'ok','irrigando hoje':'blue','encerrada':'gray'};
const FCOR={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray'};
const CCH={red:'red',orange:'orange',yellow:'yellow',cloud:'gray',lime:'green',ok:'green',good:'green',navy:'blue',blue:'blue',purple:'blue',gray:'gray',none:'gray'};
function worstC(cs){ let b='none',bi=99; cs.forEach(c=>{ const i=SEV.indexOf(c); if(i>=0&&i<bi){ bi=i; b=c; } }); return b; }
function lay(self){ const l=self.state.lay||'Integrado'; return M.lays.indexOf(l)>=0?l:'Integrado'; }
function flt(self,l){ const gs=fopts(l); const d={}; gs.forEach(g=>{ d[g.k]=g.o[0]; }); const s=Object.assign(d,((self.state.flt||{})[l])||{});
  gs.forEach(g=>{ if(g.o.indexOf(s[g.k])<0) s[g.k]=g.o[0]; });   // opção de outra fazenda (ex.: cena) volta à primeira desta
  return s; }
// irrigação só com água é do módulo Irrigação (IR-03): fica fora da camada O.S. e das contagens de ordens; aparece na camada Irrigação
function irrAgua(o){ return /^Irrigação/.test(o.tipo||''); }
function ordsOf(t,fase){ return M.ord.filter(o=>!irrAgua(o) && osSaf(o) && o.tal.indexOf(t)>=0 && (!fase||fase==='Todas'||o.fase===fase)); }
function satVal(dt,t,ix){ if(M.semcult[t]) return null; const s=M.sat[dt]; const x=s.v[t]; if(x===undefined) return null; if(x==='cloud') return 'cloud'; return x[IDXN.indexOf(ix)]; }
function satPrev(dt,t,ix){ const ds=Object.keys(M.sat); const i=ds.indexOf(dt); for(let j=i+1;j<ds.length;j++){ const v=satVal(ds[j],t,ix); if(typeof v==='number') return [ds[j],v]; } return null; }
function money(n){ return 'R$ '+nfx(n,0); }
function mil(n){ return Math.abs(n)>=100000?('R$ '+nfx(n/1000,0)+' mil'):money(n); }
// ---- ordens do mapa = registro + cenário compartilhado (fase, realizado, saldo e custódia iguais às telas O.S., Estoque e App) ----
const ORD0=M.ord;
function mapSc(it){ const m=/saco (\d+) kg/.exec(it.emb||''); return (m&&it.un==='kg')?nfx(it.custodia/Number(m[1]),0)+' sc':nfx(it.custodia,it.custodia%1?1:0)+' '+it.un; }
let MAPC=null;  // cenário lido nesta renderização (liberações do agrônomo)
let OSN=[];     // ordens do núcleo da O.S. (as mesmas da tela Ordem de Serviço), lidas a cada renderização
// liberação pelo agrônomo: pendente = ordem A liberar no cenário (a ação 'lib' só existe em ordem com produto); liberada, sai da contagem
function inPendLib(c,id){ const co=c&&c.ordens?c.ordens[id]:null; return !!co&&co.etapa==='A liberar'; }
function mapItVis(co,it){ if(typeof CEN_BAIXA_NO_SINAL!=='undefined') return it;
  const q=Math.min((co.ap||[]).filter(a=>a.sinc===false).reduce((s,a)=>s+(Number((a.cons||{})[it.prod])||0),0),it.consumido||0);
  return q>1e-9?Object.assign({},it,{consumido:it.consumido-q,custodia:it.custodia+q}):it; }
function mapOrdsCen(){ let c=null; try{ c=cenGet(); }catch(e){ c=null; } MAPC=c;
  return ORD0.map(o=>{ const co=c&&c.ordens?c.ordens[o.id]:null; const x=Object.assign({},o,{selos:o.selos.slice()});
    let cust=[];
    if(co&&co.selos) x.selos=co.selos.map(s=>[s.t,s.c||'yellow']);
    if(co){ x.fase=co.etapa; x.saldo=co.saldo||0; const area=co.area||o.area;
      let real=nfx(co.realizado||0,(co.realizado||0)%1?1:0)+'/'+nfx(area)+' ha'; if(co.realizado>0&&co.saldo>0) real+=' · saldo '+nfx(co.saldo,co.saldo%1?1:0)+' ha';
      if(o.suf) real+=' · '+o.suf;
      const r=co.req&&c.reqs?c.reqs[co.req]:null; cust=r?r.itens.map(i=>mapItVis(co,i)).filter(i=>i.custodia>0.001):[];
      if(cust.length) real+=' · '+cust.map(mapSc).join(' + ')+' em custódia';
      if((co.ap||[]).some(a=>a.sinc===false)) real+=' · apontamento aguardando sinal';
      x.real=real;
      if(!cust.length) x.selos=x.selos.filter(s=>!/^Sobras a receber/i.test(s[0])); }
    let bq='';
    if(co&&co.etapa==='Em conferência'){ try{ bq=cenPodeEncerrar(c,o.id)||''; }catch(e){ bq=''; } x.selos=x.selos.filter(s=>!/^Aguardando sinal do app/.test(s[0]));
      if(/^Carga a pesar/.test(bq)){ if(!x.selos.some(s=>s[0]==='Carga a pesar')) x.selos=x.selos.concat([['Carga a pesar','yellow']]); }   /* colheita (R-18): não é sobra em custódia */
      else if(/sinal/.test(bq)) x.selos=x.selos.filter(s=>!/^Sobras a receber/i.test(s[0])).concat([['Aguardando sinal do app','yellow']]);
      else if(bq){ const t=/^Sobra em custódia/.test(bq)?'Sobras a receber':(/^Consumo em conferência/.test(bq)?'Consumo em conferência':(/duplicidade/.test(bq)?'Apontamento em conferência':''));   /* o selo do bloqueio que existe; a divergência de dose já vem do cenário (revisão DOM achado 3) */
        if(t&&!x.selos.some(s=>s[0]===t)) x.selos=x.selos.concat([[t,'yellow']]); } }
    if(x.fase!=='A liberar') x.selos=x.selos.filter(s=>!/^Aguardando(?! sinal do app)/.test(s[0]));
    if(x.fase==='Encerradas'||x.fase==='Canceladas') x.pz='encerrada';
    const a=o.act; x.act=(!a||(a.c==='ag'&&!inPendLib(c,o.id))||(a.c==='cust'&&co&&!cust.length))?null:a;
    if(bq&&!/sinal/.test(bq)&&cust.length&&!x.act) x.act={t:'Receber sobras',h:'EST.dc.html',k:'op',c:'cust'};
    return x; }); }
function realCurto(id){ const o=M.ord.find(x=>x.id===id); return o?o.real.split(' · ')[0]:''; }
// irrigação no Integrado: conflito (vermelho) e pendência de água (amarelo) vêm do estado da irrigação, não de texto fixo
function irrInteg(t,b){ const xi=(M.irr||{})[t]; if(!xi||!xi.top||!xi.top.agua) return null;
  if(xi.c==='red') return ['red','irrigação em conflito'+(b&&['ok','none','gray'].indexOf(b[0])<0&&b[1]?' · '+b[1]:'')];
  if(['A conferir','A programar'].indexOf(xi.top.sit)>=0&&b[0]!=='red') return ['yellow','irrigação · '+(xi.top.sit==='A conferir'?'conferir medição':'janela a definir')+(b&&b[0]==='yellow'&&b[1]?' · '+b[1]:'')];
  return null; }
function integ(t){ const x=M.integ[t];
  let lb=x[1].replace(/\{\?(OS-\d+)([^}]*)\}/g,(m,id,tx)=>inPendLib(MAPC,id)?tx:'').replace(/\{(OS-\d+)\}/g,(m,id)=>realCurto(id));
  const lib=M.ord.find(o=>o.tal.indexOf(t)>=0&&o.act&&o.act.k==='lib');
  const ir=irrInteg(t,[x[0],lb]); if(ir) return ir;
  if(lib&&['ok','gray','blue','none'].indexOf(x[0])>=0) return ['yellow',lib.id+' a liberar'];
  return [x[0],lb]; }
// camada Irrigação: o mesmo estado das telas IR-01..IR-04 (situação, déficit, ordens e próximo passo)
// lâmina recomendada e percentímetro (irrPerc, irrigacao_estado.js: a mesma conta da programação da Irrigação + a ficha do pivô)
function irrRecTxt(x){ const r=x&&x.rec; if(!r||!(r.br>0.05)) return ''; return (r.np>1?r.np+'× '+nfx(r.pct?r.lamP:r.por,1):nfx(r.pct?r.lamP:r.por,1))+' mm'+(r.pct?' a '+r.pct+' %':''); }
function irrRecKv(xi){ const r=xi.rec; const kv=[]; if(!r) return kv;
  if(xi.etcd) kv.push({l:'Necessidade da cultura',t:'ETc ≈ '+nfx(xi.etcd,1)+' mm/dia'+(xi.kc?' (ETo '+nfx(xi.etcd/xi.kc,1)+' mm/dia × Kc '+nfx(xi.kc,2)+')':'')});
  if(!(r.br>0.05)){ kv.push({l:'Lâmina recomendada',t:'sem reposição: déficit zerado'}); return kv; }
  kv.push({l:'Lâmina recomendada',t:nfx(r.br,1)+' mm brutos = '+nfx(r.liq,1)+' mm de déficit ÷ eficiência de '+xi.ef+' %'+(r.np>1?' · em '+r.np+' passadas (limite de '+nfx(xi.lmax,1)+' mm por passada)':'')});
  if(xi.tipo!=='pivô') kv.push({l:'Turno',t:'gotejo: '+irrH(r.dur)+' por turno pela vazão do setor'});
  else if(r.pct) kv.push({l:'Velocidade do pivô',t:'percentímetro '+r.pct+' % · '+nfx(r.lamP,1)+' mm por volta · volta de '+nfx(r.volta,1)+' h'+(r.np>1?' · '+r.np+' voltas':'')},
    {l:r.demo?'Ficha demonstrativa (sintética)':'Ficha do pivô',t:nfx(r.l100,2)+' mm e volta de '+nfx(r.v100,1)+' h a 100 % · lâmina = lâmina a 100 % × 100 ÷ percentímetro'});
  else kv.push({l:'Velocidade do pivô',t:'sem ficha do pivô: registre a ficha para calcular o percentímetro'});
  return kv; }
function irrMapa(){ let s=null; try{ s=irrGet(); }catch(e){ s=null; } const out={};
  M.tids.concat(M.lg.ids).forEach(t=>{ const x=s&&s.setores[t]; if(!x){ out[t]={c:'gray',l:isLG(t)?'preparo · sem rega':'sequeiro',d:null,est:false,hoje:'',ac:null,ords:[]}; return; }
    const si=irrSituacao(s,t); const rp=si.d!==null?irrPerc(s,t):null; out[t]={rec:rp,kc:x.kc||null,etcd:x.bal?x.bal.etc/x.bal.dias:null,tipo:x.tipo,ef:x.efic,lmax:x.lmax,c:si.c,l:si.l,d:si.d,est:si.est,hoje:si.hoje,ac:si.acao,fon:si.fon,limt:si.limt,lam:si.lam,eq:si.eq,ult:si.ult,faixa:si.faixa||'',ords:si.ords||[],top:si.top?{sit:si.top.sit,agua:!!(si.top.o&&!si.top.o.fert)}:null}; });
  return out; }
// ---- satélite: classe absoluta do índice ou contraste esticado (P2–P98) da fazenda ou do talhão; pixels dentro do polígono ----
function kOf(v,L){ let k=0; while(k<5&&v>=L[k]) k++; return k; }
function satCor(ix,k){ return M.satpal[M.idx[ix].pal+(k+1)]; }
function satNome(ix,k){ return M.clsn[M.idx[ix].pal][k]; }
function satChipSt(ix,k){ const hx=satCor(ix,k); const esc=(M.idx[ix].pal==='v')?[1,1,0,0,0,1][k]:[1,0,0,0,1,1][k];
  return 'display:inline-flex;align-items:center;padding:3px 10px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;background:'+hx+';color:'+(esc?'#FFFFFF':'#15201A')+';'; }
const PXC={};
function pxVals(dt,ix){ const key=dt+'|'+ix; if(PXC[key]) return PXC[key];
  const SD={NDVI:.035,NDRE:.02,EVI:.025,SAVI:.03,NDMI:.03}, DP={NDVI:.30,NDRE:.14,EVI:.18,SAVI:.21,NDMI:.13};
  const out={}; const mc=M.sat[dt].manchas.find(m=>m.t==='T7'); const mr=mc?mc.r:0;
  Object.keys(M.px).forEach(t=>{ const v=satVal(dt,t,ix); if(typeof v!=='number') return; const cs=M.px[t];
    const raw=cs.map(c=>v+c[2]*SD[ix]-((mr&&c[3]>=0&&c[3]<mr)?DP[ix]*(1-c[3]/mr):0)); const avg=raw.reduce((a,b)=>a+b,0)/raw.length;
    out[t]=raw.map(x=>Math.round((x-avg+v)*1000)/1000); });
  return (PXC[key]=out); }
function pctl(a,p){ const s=a.slice().sort((x,y)=>x-y); if(!s.length) return 0; return s[Math.min(s.length-1,Math.max(0,Math.round(p*(s.length-1))))]; }
function satLims(f,t){ if(FAZ==='Lagoa Grande'||isLG(t||'')) return lgLims(f,t); if(f.ctr==='Absoluto') return M.idx[f.idx].lim; const pv=pxVals(f.dt,f.idx);
  const vals=(f.ctr==='Talhão'&&t)?(pv[t]||[]):[].concat(...Object.values(pv)); if(!vals.length) return M.idx[f.idx].lim;
  if(f.ctr==='Talhão') return [1,2,3,4,5].map(i=>Math.round(pctl(vals,i/6)*1000)/1000);
  const a=pctl(vals,.02), b=pctl(vals,.98); const st=((b-a)/6)||0.01; return [1,2,3,4,5].map(i=>Math.round((a+st*i)*1000)/1000); }
function pxCoord(c){ const y=c[1]+M.cs/2, x=c[0]+M.cs/2; const la=-15.5612-(y-556)*0.000035, lo=-54.2987+(x-650)*0.00003;
  const f=(n)=>'−'+nfx(Math.abs(n),4); return f(la)+' · '+f(lo); }
// estado do talhão no satélite (5 estados): sem imagem · nuvem · normal · atenção · crítico
function satEstado(t,f){ const v=satVal(f.dt,t,f.idx); const nt=(M.sat[f.dt].nt||{})[t]||0;
  if(v===null) return ['Sem leitura · sem cultura','gray'];
  if(v==='cloud'||nt>20) return ['Nuvem · aguardar próxima cena','gray'];
  const pv=satPrev(f.dt,t,f.idx); const dv=pv?(v-pv[1])/pv[1]*100:null; const ms=M.sat[f.dt].manchas.filter(m=>m.t===t);
  if(ms.some(m=>m.ha>1)||(dv!==null&&dv<-15)) return ['Crítico','red'];
  if(ms.length||(dv!==null&&dv<-10)) return ['Atenção','yellow'];
  return ['Normal','green']; }
// ---- insumos: necessidade do talhão × situação da fazenda (estoque compartilhado não é dividido por talhão) ----
// CTL-4 (DEM-05): a mesma conta do Planejar safra e da Compra (demFazenda, cal01.js) com ordens e estoque do cenário vivo (cenDemEntradas):
// liberar, apontar, cancelar ou emitir uma O.S. muda a necessidade e a situação; entregar, devolver e receber não mudam a compra (revisão, achado 1)
function insFaz(){ const D=M.dem; const F=D.faz[safK()]; if(!F) return {nec:{},st:{}}; const X=cenDemEntradas(cenGet(),F,D.b);
  const k=safK()+'|'+JSON.stringify([X.osd,X.fisico,X.reservas,X.recebDt,X.sobra,X.quar,X.quarRep]); if(insFaz._k===k) return insFaz._v;   /* custódia sem uso e quarentena (revisão do 853a6a8) também mudam a conta */ const m=demFazenda(X); const tid=(t)=>D.tid[t]||demTal(t);
  const v={nec:demPorLocal(m,tid,F.areaT,F.hoje),st:{'Safra toda':demSituacao(m,null,F.hoje,F.viavel),'Próximos 30 dias':demSituacao(m,M.lim30,F.hoje,F.viavel)}};
  insFaz._k=k; insFaz._v=v; return v; }
function necAgg(t,per){ const m={}; (insFaz().nec[t]||[]).filter(x=>per==='Safra toda'||x.dt<=M.lim30).forEach(x=>{ const a=m[x.p]||(m[x.p]={p:x.p,q:0,un:x.un,dt:x.dt,orig:[]}); a.q+=x.q; if(x.dt<a.dt) a.dt=x.dt; a.orig.push(x.orig); });
  return Object.values(m).sort((a,b)=>a.dt<b.dt?-1:(a.dt>b.dt?1:0)); }
function brIso(s){ if(!s) return ''; const a=s.split('-'); return a[2]+'/'+a[1]; }
// ---- custos: previsto (plano ou O.S.) × realizado provisório (apontamentos aceitos) × conferido; preço ausente não vira zero ----
// custo: as regras moram em custo_dominio.py (fonte única do Mapa e do Painel Agrícola); aqui só o atalho com os dados do Mapa (M) e a projeção OSN
function precoDe(p){ return cusPreco(M,p); }
function ordCusto(o){ return cusOrdem(M,o); }
function cusReal(t){ return cusTalhao(M,t,OSN.filter(osSaf)); }
// ---- classe e rótulo de cada talhão na camada ativa ----
// ---- pragas e doenças (MIP/MID): vistorias do período; a pior situação colore o talhão ----
// mesma base do AG-01 (mip.js): vistorias do período + as abertas e as decisões pendentes, da pior para a melhor situação
function mipPer(per){ return per==='Últimos 30 dias'?30:7; }
function mipOf(t,per){ return mipDoTal(mipGet(),t,mipPer(per),MAPC).filter(x=>alvOk(x.v)); }
function mipSemProt(t){ return !(MIPD.prots[t]||[]).length; }
function mipMin(t0){ return t0.charAt(0).toLowerCase()+t0.slice(1); }
function semCultura(t){ return ['gray','none'].indexOf((lavOf(t)||{}).c)>=0; }
// fora da Cultura escolhida na faixa: neutro em toda camada
function cls(l,f,t){ if(!inF(t)) return {c:'none',l:'fora do filtro'}; return cls0(l,f,t); }
function cls0(l,f,t){
  if(l===CAR_L) return carCls(t,f);   // MAPA-CARENCIA-LMR-20261003
  if(l===SOLO_L) return soloCls(t,f);   // Análises de solo (13/10/2026; mapa de calor 15/10/2026)
  if(l===COLH_L) return colhCls(t);   // Colheita (14/10/2026)
  if(l==='Integrado'){ const x=integ(t); if(f.mostrar==='Só pendências' && ['ok','gray','blue','none'].indexOf(x[0])>=0) return {c:'none',l:'sem pendência'}; return {c:x[0],l:x[1]}; }
  if(l==='Satélite'){ const v=satVal(f.dt,t,f.idx); if(v===null) return {c:'gray',l:M.semcult[t]||'sem cultura'}; if(v==='cloud') return {c:'cloud',l:'nuvem · sem leitura'};
    const k=kOf(v,satLims(f,t)); return {c:'sat',hex:satCor(f.idx,k),k,ka:kOf(v,M.idx[f.idx].lim),l:f.idx+' '+nfx(v,2)}; }
  if(l==='Lavoura'){ const x=lavOf(t); return {c:x.c,l:x.l}; }
  if(l==='O.S./prazos'){ const os=ordsOf(t,f.fase); if(!os.length) return {c:'none',l:'sem ordem'+(f.fase==='Todas'?'':' na fase')}; const c=worstC(os.map(o=>PZC[o.pz])); const o=os.find(x=>PZC[x.pz]===c);
    return {c,l:o.id+' · '+o.pz+(os.length>1?' · +'+(os.length-1):'')}; }
  if(l==='MIP/MID'){ const vs=mipOf(t,f.per);
    if(!vs.length){ if(mipSemProt(t)) return {c:'none',l:'sem cultura'};
      if(ALV){ if(!(MIPD.prots[t]||[]).some(p=>ALV.indexOf((MIPD.prot[p]||{}).alvo)>=0)) return {c:'none',l:'sem '+alvTxt()+' no protocolo'}; return {c:'gray',l:'sem vistoria de '+alvTxt()+' em '+mipPer(f.per)+' dias'}; }
      const r=mipRitmo(mipGet(),t); return {c:'gray',l:r.atras?('vistoria atrasada '+r.atras+(r.atras>1?' dias':' dia')):'sem vistoria em '+mipPer(f.per)+' dias'}; }
    const x=vs[0]; return {c:x.S.mc,l:mipP(x.v).alvo+' · '+mipMin(x.S.t)+(vs.length>1?' · +'+(vs.length-1):'')}; }
  if(l==='Irrigação'){ const x=M.irr[t]; if(!x) return {c:'none',l:''};
    if(f.ver==='Balanço hídrico'){ if(x.d===null) return {c:'gray',l:x.l}; if(x.est){ const rt=irrRecTxt(x); return {c:'cloud',l:'≈'+nfx(x.d,1)+' mm · estimado'+(rt?' → '+rt:'')}; }
      const rt=irrRecTxt(x); return {c:x.d<5?'ok':(x.d<10?'yellow':(x.d<15?'orange':'red')),l:'déficit '+nfx(x.d,1)+' mm'+(rt?' → '+rt:'')}; }
    return {c:x.c,l:x.l}; }
  if(l==='Insumos'){ const its=necAgg(t,f.per); const st=insFaz().st[f.per]||{};
    if(!its.length) return semPlanoOf(t)?{c:'gray',l:'sem plano na safra'}:{c:'none',l:'sem necessidade'};
    const c=worstC(its.map(x=>(st[x.p]||['','none'])[1])); const fal=its.filter(x=>(st[x.p]||[])[1]==='red');
    return {c,l:fal.length?('falta '+fal[0].p+(fal.length>1?' +'+(fal.length-1):'')):(c==='yellow'?'aguardando pedido':'estoque cobre')}; }
  if(l==='Custos'){ const P=prevOf(t);
    if(f.most==='Previsto R$/ha'){ if(!P.fonte||!P.base) return {c:'gray',l:'sem previsto'}; return {c:'blue',l:money(P.tot/P.base)+'/ha'}; }
    const R=cusReal(t); if(!R.ha) return {c:'none',l:R.shared.length?('só '+R.shared.map(x=>x.o.id).join(', ')+' compartilhada'):'sem execução'}; const dv=R.prevExec?(R.rs-R.prevExec)/R.prevExec*100:0; const c=dv<=0.5?'ok':(dv<=10?'yellow':'red');
    return {c,l:mil(R.rs)+' · '+(dv>0.5?'+'+nfx(dv,1)+' %':'no previsto')}; }
  return {c:'none',l:''}; }
function Lc(l,c,t){ const pl=M.lcop[c]||M.lcop.none; return {t,st:'display:inline-flex;align-items:center;gap:5px;white-space:nowrap;',dot:'width:11px;height:11px;border-radius:3px;flex-shrink:0;'+(c==='cloud'?'background:repeating-linear-gradient(45deg,#C9CFCB 0 3px,#9E9E9E 3px 5px);':'background:'+pl[0]+';')+'border:1px solid '+pl[1]+';'}; }
function Lh(hx,t){ return {t,st:'display:inline-flex;align-items:center;gap:5px;white-space:nowrap;',dot:'width:11px;height:11px;border-radius:3px;flex-shrink:0;background:'+hx+';'}; }
function legend(self,l,f,sel){
  if(l===CAR_L) return carLegend();   // MAPA-CARENCIA-LMR-20261003
  if(l===COLH_L) return colhLegend();
  if(l===SOLO_L) return soloLegend(f);
  if(l==='Integrado') return [Lc(l,'ok','em dia'),Lc(l,'yellow','atenção ou a liberar'),Lc(l,'red','impedida ou conflito'),Lc(l,'gray','encerrada'),Lc(l,'none','sem pendência')];
  if(l==='Satélite'){ const t0=sel[0]||''; const t=(f.ctr==='Talhão'&&t0&&typeof satVal(f.dt,t0,f.idx)==='number')?t0:''; const L=satLims(f,t||null); const d=(L[4]-L[0]<0.06)?3:2; const nm=M.clsn[M.idx[f.idx].pal];
    const fx=(x)=>nfx(x,d); const out=[0,1,2,3,4,5].map(k=>Lh(satCor(f.idx,k),nm[k]+' '+(k===0?'< '+fx(L[0]):(k===5?'≥ '+fx(L[4]):fx(L[k-1])+'–'+fx(L[k])))));
    if(f.ctr==='Talhão'&&!t) out.forEach((x,k)=>{ x.t=nm[k]; });
    return out.concat([Lc(l,'gray','sem cultura'),Lc(l,'cloud','nuvem')]).concat(f.ctr==='Talhão'&&t?[{t:'limites de '+rotT(t),st:'font-weight:700;',dot:'display:none;'}]:[]); }
  if(l==='Lavoura') return [Lc(l,'gray','pré-plantio'),Lc(l,'ok','vegetativo ou emergência'),Lc(l,'purple','reprodutivo'),Lc(l,'yellow','produção contínua'),Lc(l,'orange','granação ou maturação'),Lc(l,'none','colhido ou fora do filtro')];
  if(l==='O.S./prazos') return [Lc(l,'red','atrasada'),Lc(l,'orange','vence hoje'),Lc(l,'yellow','até 3 dias'),Lc(l,'ok','no prazo'),Lc(l,'gray','encerrada'),Lc(l,'none','sem ordem')];
  if(l==='MIP/MID') return [Lc(l,'red','acima do NC'),Lc(l,'orange','foco'),Lc(l,'yellow','perto do NC ou coleta pendente'),Lc(l,'blue','em controle'),Lc(l,'lime','programada'),Lc(l,'ok','abaixo do NC'),Lc(l,'gray','vistoria atrasada ou sem vistoria no período'),Lc(l,'none','sem cultura')];
  if(l==='Irrigação') return f.ver==='Balanço hídrico'?[Lc(l,'ok','déficit < 5 mm'),Lc(l,'yellow','5–10 mm'),Lc(l,'orange','10–15 mm'),Lc(l,'red','≥ 15 mm'),Lc(l,'cloud','≈ estimado por ET (sonda sem dado ou suspeita)'),Lc(l,'gray','sequeiro ou preparo')]
    :[Lc(l,'blue','irrigando'),Lc(l,'lime','programada'),Lc(l,'yellow','pendente: janela, conferência ou liberação'),Lc(l,'red','impedida ou conflito'),Lc(l,'ok','sem necessidade hoje'),Lc(l,'cloud','sem necessidade · ≈ estimado'),Lc(l,'gray','sequeiro ou preparo')];
  if(l==='Insumos') return [Lc(l,'ok','estoque cobre'),Lc(l,'yellow','pedido a receber'),Lc(l,'red','falta comprar'),Lc(l,'gray','sem plano na safra'),Lc(l,'none','sem necessidade no período')];
  if(l==='Custos') return f.most==='Previsto R$/ha'?[Lc(l,'blue','com previsto'),Lc(l,'gray','sem previsto')]:[Lc(l,'ok','no previsto'),Lc(l,'yellow','até +10 %'),Lc(l,'red','acima de +10 %'),Lc(l,'none','sem execução')];
  return []; }
function fonte(l,f){
  if(l===CAR_L) return carFonte(f);   // MAPA-CARENCIA-LMR-20261003
  if(l===COLH_L) return colhFonte();
  if(l===SOLO_L){ const ind=SOLO_IND[f.ind]||{}; return 'pontos georreferenciados da amostragem em grade de cada laudo (Análises de solo) · camada '+f.prof+' · mapa de calor por interpolação (inverso do quadrado da distância) dentro do talhão · '+(f.ctr==='Absoluto'?'classes da tabela demonstrativa ('+SOLO0.regra.rotulo+')':(f.ctr==='Talhão'?'contraste do talhão: sextos dos valores dele':'contraste da fazenda: P2–P98 de todos os talhões'))+(ind.idx?' · '+ind.l+' calculado no ponto (soloIdx)':'')+' · laudos sintéticos'; }
  if(l==='Integrado') return FAZ==='Lagoa Grande'?(M.lg.rot?(M.lg.rot+' · pivôs, imagem e índices fictícios · O.S. e safra do cenário · cena de '+M.lg.cenas[0].k):('Pivôs do KML do proprietário · O.S. e safra do cenário · imagem Sentinel-2 de '+M.lg.cenas[0].k)):('O.S. do PCP e cenário de execução · satélite 21/09 · hoje '+M.hoje);
  if(l==='Satélite'){ const s=M.sat[f.dt]; return (s.real&&M.lg.rot?M.lg.rot+' · imagem e índices fictícios':'Sentinel-2 L2A'+(s.real?' · imagem real (Copernicus/ESA)':''))+' · 10 m · aquisição '+s.aq+' · '+f.idx+': '+M.idx[f.idx].o+' · contraste '+f.ctr.toLowerCase(); }
  if(l==='Lavoura') return (safCur()?'ocupação atual e cultivos da safra '+SAF+' · DAP e idade pela data real de plantio':'cultivos da safra '+SAF+' · plantio e colheita do planejamento')+' · hoje '+M.hoje;
  if(l==='O.S./prazos') return 'O.S. do PCP · prazo pela janela de cada ordem · fase do cenário de execução';
  if(l==='MIP/MID') return 'vistorias de Pragas e doenças · NC por alvo e fase · '+(FAZ==='Lagoa Grande'?'pivôs reais, vistorias demonstrativas':'talhões desenhados')+' · hoje '+M.hoje;
  if(l==='Irrigação') return FAZ==='Lagoa Grande'?('balanço hídrico demonstrativo sobre os pivôs reais · ETo 5,5 mm/dia × Kc do mamão por fase · tarefas do dia geradas pelo balanço · hoje '+M.hoje):'balanço hídrico 23/09 06:00 · Estação Santa Rita e sondas P1, P2 e T7 · ≈ = estimativa por ET · ordens do módulo Irrigação';
  if(l==='Insumos'){ const F=M.dem.faz[safK()]; if(!F) return 'safra '+SAF+' encerrada: sem necessidade a comprar'; return 'necessidade líquida da '+(F?F.nomes[F.saf]:'safra')+' (plano sem O.S. + O.S. abertas pelo que falta tirar do almoxarifado): a mesma do Planejar safra e da Compra · estoque apto e pedidos da fazenda, não divididos por talhão'; }
  if(l==='Custos') return 'previsto = dose × preço + operação (rendimento da safra) · realizado provisório dos apontamentos aceitos · conferido à parte';
  return ''; }
function strip(self,l,f){ const N=(k,val,d)=>({k,val,d:d||''}); const tids=TIDS().filter(inF); const ordF=M.ord.filter(o=>!irrAgua(o)&&osSaf(o)&&o.tal.some(t=>tids.indexOf(t)>=0)); const area=(ts)=>ts.reduce((a,t)=>a+M.tal[t].ha,0);
  if(l===CAR_L) return carStrip(f);   // MAPA-CARENCIA-LMR-20261003
  if(l===SOLO_L) return soloStrip(f);
  if(l===COLH_L) return colhStrip();
  if(l==='Integrado'){ const ab=ordF.filter(o=>o.fase!=='Encerradas'); return [N('',nfx(area(tids))+' ha','Área dos talhões'),N('Ordens abertas',ab.length),N('Impedidas',ordF.filter(o=>o.selos.some(s=>/^(Impedida|Falta máquina)/.test(s[0]))).length,'Ordens impedidas'),N('A liberar',ordF.filter(o=>o.act&&o.act.k==='lib').length,'A liberar pelo agrônomo')]; }
  if(l==='Satélite'){ let s=0,a=0,n=0; tids.forEach(t=>{ const v=satVal(f.dt,t,f.idx); if(typeof v==='number'){ s+=v*M.tal[t].ha; a+=M.tal[t].ha; } if(v==='cloud') n++; });
    const ms=M.sat[f.dt].manchas; const out=[N(f.idx,a?nfx(s/a,2):'—',f.idx+' médio dos talhões com cultura (ponderado pela área)')];   // manchas e talhões sob nuvem só quando há
    if(ms.length) out.push(N('Manchas',ms.length+' · '+nfx(ms.reduce((x,m)=>x+m.ha,0),1)+' ha','Manchas na cena'));
    out.push(N('Nuvem',nfx(M.sat[f.dt].nuvem,2)+' %','Nuvem na cena')); if(n) out.push(N('Sob nuvem',n,'Talhões sob nuvem na cena')); return out; }
  if(l==='Lavoura'){ if(safCur()&&CULT==='Todas') return FAZ==='Lagoa Grande'?[N('Pivôs',tids.length),N('',nfx(area(tids))+' ha','Área irrigada'),N('Com cultivo',tids.filter(t=>M.lav[t].c!=='gray').length,'Pivôs com cultivo na safra')]:M.lavstrip.map(x=>N(x[0],x[1],x[2]));
    const cs=[].concat(...tids.map(t=>(M.csaf[safK()]||{})[t]||[])).filter(c=>CULT==='Todas'||c.cult===CULT);
    return [N('Cultivos',cs.length,'Cultivos na safra '+SAF+(CULT==='Todas'?'':' · '+CULT)),N('',nfx(cs.reduce((a,c)=>a+c.area,0))+' ha','Área dos cultivos na safra'),N(FAZ==='Lagoa Grande'?'Pivôs':'Talhões',tids.length)]; }
  if(l==='O.S./prazos'){ const os=ordF.filter(o=>f.fase==='Todas'||o.fase===f.fase); return [N('Ordens',os.length),N('Atrasadas',os.filter(o=>o.pz==='atrasada').length),N('Vencem hoje',os.filter(o=>o.pz==='vence hoje').length),N('Saldo',nfx(os.reduce((a,o)=>a+(o.saldo||0),0))+' ha','Saldo a executar')]; }
  if(l==='MIP/MID'){ const cs=tids.map(t=>cls(l,f,t).c); const sm=mipGet(); const lim=mipAdd(M.hoje_iso,-mipPer(f.per));
    return [N('Vistorias',Object.values(sm.vis).filter(v=>tids.indexOf(v.tal)>=0&&v.data>=lim&&v.data<=M.hoje_iso&&alvOk(v)).length,'Vistorias no período'),N('Acima do NC',cs.filter(c=>c==='red').length,'Talhões acima do nível de controle'),N('Atenção',cs.filter(c=>c==='orange'||c==='yellow').length,'Talhões com foco ou atenção'),N('Em controle',cs.filter(c=>c==='blue').length,'Talhões em controle')]; }
  if(l==='Irrigação'){ const xs=tids.filter(t=>M.irr[t]&&M.irr[t].d!==null); const n=(c)=>xs.filter(t=>M.irr[t].c===c).length; const nest=xs.filter(t=>M.irr[t].est).length;
    if(f.ver==='Balanço hídrico'){ const a=area(xs); const dm=a?xs.reduce((q,t)=>q+M.irr[t].d*M.tal[t].ha,0)/a:0; const mx=xs.slice().sort((p,q)=>M.irr[q].d-M.irr[p].d)[0];
      return [N('',nfx(a)+' ha','Área com balanço hídrico'),N('Déficit',nfx(dm,1)+' mm','Déficit médio (ponderado pela área)'),N('Maior',mx?(rotT(mx)+' · '+nfx(M.irr[mx].d,1)+' mm'):'—','Maior déficit'),N('Estimados',nest,'Estimados por ET (sonda sem dado ou suspeita)')]; }
    return [N('Programadas',n('blue')+n('lime'),'Irrigando ou programadas'),N('Pendentes',n('yellow'),'Pendentes: janela, conferência ou liberação'),N('Impedidas',n('red'),'Impedidas ou em conflito'),N('Estimados',nest,'Estimados por ET (≈)')]; }
  if(l==='Insumos'){ const st=insFaz().st[f.per]||{}; const vs=Object.values(st); return [N('Produtos',vs.length,'Produtos no período'),N('Faltam',vs.filter(x=>x[1]==='red').length,'Faltam comprar'),N('A receber',vs.filter(x=>x[1]==='yellow').length,'Aguardando pedido a receber'),N('Estoque cobre',vs.filter(x=>x[1]==='ok').length)]; }
  if(l==='Custos'){ let p=0,r=0,c=0,sh={}; tids.forEach(t=>{ p+=prevOf(t).tot; const R=cusReal(t); r+=R.rs; c+=R.rsConf; R.shared.forEach(s=>{ sh[s.o.id]=s.c; }); });
    Object.values(sh).forEach(x=>{ r+=x.rs; c+=x.rsConf; });
    return [N('Previsto',mil(p)),N('Realizado',mil(r),'Realizado provisório (apontamentos aceitos)'),N('Conferido',mil(c)),N('Execução',p?nfx(r/p*100,1)+' %':'—','Realizado ÷ previsto')]; }
  return []; }
// ---- ações do painel (ícone + rótulo + title) ----
const ICN=['doc','alert','drop','leaf','map','trend','cash','lab','check','calendar','layers','box','cart','satelite','inseto','frasco'];
function A(t,o){ const a={t,tt:o.tt||t,isH:!!o.h,isF:!!o.fn,h:o.h||'#',fn:o.fn||(()=>{}),
  st:(o.prim?'background:#1E7A4C;color:#fff;border:1px solid #1E7A4C;':'background:#FFFFFF;color:#15201A;border:1px solid #E4E9E5;')+'display:inline-flex;align-items:center;gap:6px;padding:6px 11px;border-radius:9px;font-size:12.5px;font-weight:700;text-decoration:none;white-space:nowrap;cursor:pointer;font-family:inherit;line-height:1.25;'};
  ICN.forEach(n=>{ a['i_'+n]=(o.ic===n); }); return a; }
function CH(t,c){ return {t,st:chipSt(c)}; }
function CHs(t,st){ return {t,st}; }
// programar vistoria (mesma base e função do AG-01 · mipNovaVis): MIP/MID = alvo do protocolo da cultura (o da última vistoria do talhão);
// Satélite = inspeção da mancha. Uma vistoria aberta por talhão (outro alvo: AG-01); grava no estado compartilhado (aparece no AG-01 e no app).
function mapVisAb(t,sat){ const sm=mipGet(); const ab=Object.values(sm.vis).filter(v=>v.tal===t&&(v.est!=='concluida'||(v.pend||[]).length)&&(sat?v.prot==='inspecao':true)); return ab.length?ab[0].id:''; }
function mapMipRun(self,vid,fn){ const v=mipGet().vis[vid]; if(!v) return;
  const F={sinc:x=>mipSinc(x,vid),parcial:x=>mipParcial(x,vid),monitorar:x=>mipMonitorar(x,vid,''),pos:x=>mipPos(x,vid),programar:x=>mipNovaVis(x,v.tal,v.prot,mipAmanha(),undefined,'mapa')}[fn];
  if(F) mipMudar(self,F); }
function criarVis(self,ts,extra,pt){ const sat=lay(self)==='Satélite'; const msgs=[]; let n=0;
  const r=mipMudar(null,s0=>{ ts.forEach(t=>{ const prot=sat?'inspecao':mipProtPadrao(s0,t); const nm=rotT(t);
      if(!prot||(sat&&mipSemProt(t))){ msgs.push(nm+' sem cultura: sem protocolo de monitoramento'); return; }
      // no mapa, uma vistoria aberta por talhão (outro alvo se programa no AG-01); na mancha, uma inspeção aberta
      const ab=sat?mipAberta(s0,t,'inspecao'):Object.values(s0.vis).find(v=>v.tal===t&&v.prot!=='inspecao'&&(v.est!=='concluida'||(v.pend||[]).length));
      if(ab){ msgs.push(ab.id+' já está aberta para '+nm); return; }
      const mancha=Object.keys(M.sat).some(d=>M.sat[d].manchas.some(m=>m.t===t));
      const x=mipNovaVis(s0,t,prot,mipAmanha(),undefined,sat?'mapa · satélite':'mapa'); n++;
      msgs.push(x.id+' programada para '+nm+' × '+MIPD.prot[prot].alvo.toLowerCase()+(sat&&ts.length===1?' · ponto no '+(pt||(mancha?'centroide da mancha':'centro do talhão')):'')); });
    return {msg:msgs.join(' · ')+(n?' · aparece no AG-01 e no app.':' · nenhuma vistoria duplicada.')}; });
  self.setState(Object.assign({miprev:Date.now(),g2toast:r.msg||r.erro||''},extra||{})); }
// ---- O.S. do talhão: cartões selecionáveis e o próximo passo da escolhida (osProx e comandos osc_* do núcleo da O.S.) ----
function osMapa(t){ const mo=M.ord.filter(o=>o.tal.indexOf(t)>=0); const sv=(id)=>{ const x=mo.find(o=>o.id===id); return SEV.indexOf(PZC[x?x.pz:'no prazo']); };
  return OSN.filter(o=>mo.some(m=>m.id===o.id)&&o.etapa!=='Canceladas').sort((a,b)=>{ const fa=a.etapa==='Encerradas'?1:0, fb=b.etapa==='Encerradas'?1:0; const al=x=>x.etapa==='A liberar'?0:1; return (fa-fb)||(sv(a.id)-sv(b.id))||(al(a)-al(b)); }); }   /* empate de prazo: a decisão do agrônomo (A liberar) vem antes, como no rótulo do talhão (G1 do CTL-1: OS-0424 no T1-B) */
function mapCt(o,fn){ const insTxt=(o.ins||[]).map(x=>x.p+' '+nd(x.tot)+' '+x.un).join(', '); const vn=osVn(o.versao);  // versão: só "vN" (núcleo da O.S.)
  return {aprovar:'Aprovar '+o.id+' (versão '+vn+'): ao confirmar, '+g2ator(g2perfil(),g2alc('AL-02').papeis)+' aprova '+osEsc(o)+' (CMD-42). A ordem fica em A liberar; '+g2alcQuem('AL-01')+' libera.',
    liberar:o.agua?('Liberar '+o.id+': janela, bomba e energia confirmadas; água sem requisição no Estoque.'):('Liberar '+o.id+' (versão '+vn+'): ao confirmar, '+osLibTxt(g2perfil(),o)+'; '+(insTxt?'a requisição reserva no Estoque, por lote: '+insTxt+'.':'sem insumos a reservar.')+osUsoAtencao(cenGet(),o.id)),
    iniciar:'Iniciar '+o.id+' agora, na janela '+o.janela+'.',conferencia:'Enviar '+o.id+' para conferência: execução física concluída ('+nf(o.realizado)+' ha).',
    encerrar:'Encerrar '+o.id+': apontamentos enviados, consumo baixado e nada em custódia.'}[fn]||''; }
function nxOf(self,o,mo){ const PF=g2perfil(); const pb=osProx(o,PF); const P=pb.P, b=pb.b;   /* CTL-3: quem age (perfil) */ const pa=(self.state.mpa&&self.state.mpa.id===o.id)?self.state.mpa:null;
  const N={id:o.id,t:P.t,btn:'',isBtn:false,go:()=>{},bloq:!!b,bt:b?b.t:'',bq:b?'Quem resolve: '+b.q:'',hasBh:!!(b&&b.h),bh:(b&&b.h)||'#',bhl:(b&&b.hl)||'',
    conf:false,ct:'',cbtn:'',yes:()=>{},back:()=>self.setState({mpa:null}),ap:false,ad:'',aha:'',asub:'',setad:()=>{},setaha:()=>{},asave:()=>{},err:'',hasErr:false,dono:'',hasDono:false,
    open:'OS.dc.html#'+o.id,hasLib:false,libt:'',libh:'#',
    ins:(o.etapa==='A liberar'&&(o.ins||[]).length)?('Produtos: '+o.ins.map(x=>x.p+' '+nd(x.dose)+' '+x.un+'/ha').join(' · ')):'',hasIns:o.etapa==='A liberar'&&(o.ins||[]).length>0};
  // ação da ordem no passo: 'lib' = Ajustar antes de liberar (o primário é o Liberar do núcleo) · 'op' só com o passo impedido, quando leva a outro destino que o do impedimento
  const a=mo&&mo.act; if(a&&((a.k==='lib'&&g2papel(PF,g2alc('AL-02').papeis))||(a.k==='op'&&b&&b.h&&a.h!==b.h))){   /* ajustar antes de liberar: só o agrônomo */ N.hasLib=true; N.libt=a.t; N.libh=a.h==='OS.dc.html'?'OS.dc.html#'+o.id:a.h; if(a.k==='lib') N.libh='OS.dc.html#'+o.id+':ajustar'; }
  if(P.fn==='ajustar'){ N.hasLib=true; N.libt=P.btn; N.libh='OS.dc.html#'+o.id+':ajustar'; }   /* SOLO-01 · revisão A6: plano mudado pela análise, o ajuste abre na O.S. (o Mapa não tem o formulário) */
  else if(!b&&P.btn){ N.isBtn=true; N.btn=P.btn; N.go=()=>{ if(P.fn==='apontar'){ const prox=(o.ap||[]).find(x=>x.st==='Previsto'); const mx=Math.max(0,(o.saldo||0)-osApPend(o));
      self.setState({mpa:{id:o.id,fn:'apontar',d:CEN_DIA_OP,ha:String(Math.min(mx,prox?prox.ha:mx)).replace('.',','),chave:'W-'+o.id+'-'+Date.now(),err:''}}); } else self.setState({mpa:{id:o.id,fn:P.fn,err:''}}); }; }
  if(!b&&o.dono){ N.dono='Pendência com '+o.dono+(o.prazo?' · '+o.prazo:''); N.hasDono=true; }
  if(pa&&['liberar','aprovar','iniciar','conferencia','encerrar'].indexOf(pa.fn)>=0&&!(pa.fn==='liberar'&&b&&b.papel)&&!(pa.fn==='aprovar'&&P.fn!=='aprovar')){ N.conf=true;   /* aberta por outro perfil: não aparece (revisão do CTL-3, achado 1) */ N.ct=mapCt(o,pa.fn); N.cbtn={aprovar:'Confirmar aprovação',liberar:'Confirmar liberação',iniciar:'Confirmar início',conferencia:'Confirmar envio',encerrar:'Confirmar encerramento'}[pa.fn];
    N.yes=()=>{ const F={aprovar:c=>osc_aprovar(c,o.id,g2perfil()),liberar:c=>osc_liberar(c,o.id,o.agua,o.janela,g2perfil()),iniciar:c=>osc_iniciar(c,o.id),conferencia:c=>osc_conferencia(c,o.id,g2perfil()),encerrar:c=>osc_encerrar(c,o.id,g2perfil())}[pa.fn];
      osRun(self,F,{mpa:null},(e)=>self.setState({mpa:Object.assign({},pa,{err:e})})); }; }
  if(pa&&pa.fn==='apontar'){ N.ap=true; const apP=osApPend(o), apMax=Math.max(0,(o.saldo||0)-apP); N.ad=pa.d||''; N.aha=pa.ha||'';
    N.asub='Saldo da ordem: '+nf(o.saldo)+' ha'+(apP>0?' · '+nf(apP)+' ha no aparelho aguardando sinal':'')+'. Os insumos usados saem pela dose.';
    N.setad=(e)=>self.setState({mpa:Object.assign({},self.state.mpa,{d:e.target.value,err:''})}); N.setaha=(e)=>self.setState({mpa:Object.assign({},self.state.mpa,{ha:e.target.value,err:''})});
    N.asave=()=>{ const cur=self.state.mpa; const n=g2num(cur.ha); const er=(m)=>self.setState({mpa:Object.assign({},cur,{err:m})});
      if(!cur.d) return er('Informe a data do turno.'); if(isNaN(n)||n<=0) return er('Informe a área feita (maior que 0 ha).');
      if(n>(o.saldo||0)+0.001) return er('Máximo '+nf(o.saldo)+' ha: é o saldo da ordem.'); if(n>apMax+0.001) return er('Máximo '+nf(apMax)+' ha: '+nf(apP)+' ha do app aguardam sinal.');
      const d=cur.d.split('-'); osRun(self,c=>osc_apontar(c,o.id,d[2]+'/'+d[1],n,undefined,undefined,cur.chave),{mpa:null},(e)=>er(e)); }; }
  if(pa&&pa.err){ N.err=pa.err; N.hasErr=true; }
  N.idle=!N.conf&&!N.ap; N.semAcao=N.idle&&!N.isBtn&&!N.hasLib&&!N.bloq;
  const PR='display:inline-flex;align-items:center;padding:6px 12px;border-radius:9px;font-size:12.5px;font-weight:700;text-decoration:none;white-space:nowrap;font-family:inherit;';
  const ST_P=PR+'background:#1E7A4C;color:#FFFFFF;border:1px solid #1E7A4C;', ST_S=PR+'background:#FFFFFF;color:#15201A;border:1px solid #E4E9E5;', ST_L='font-size:12.5px;font-weight:700;color:#15201A;text-decoration:underline;text-underline-offset:3px;white-space:nowrap;';
  // sem comando (passo impedido), a ação da ordem vira o primário e o atalho do impedimento fica como link; nenhum destino se repete
  N.dst=(!N.isBtn&&N.hasLib)?ST_P:ST_S; N.bst=(!N.isBtn&&!N.hasLib)?ST_P:ST_L; N.bhl=N.bhl&&N.bst===ST_L?N.bhl+' ›':N.bhl;
  N.hasOpen=!(N.hasLib&&N.libh===N.open);
  const bam=b&&b.tone==='yellow';
  N.st='display:flex;flex-direction:column;gap:8px;padding:10px 12px;border-radius:12px;'+(b?(bam?'background:#FFF3D6;border:1px solid #F0D9A0;':'background:#FDE8E6;border:1px solid #F4C7C1;'):(P.btn?'background:#E4F3E9;border:1px solid #BFE0CB;':'background:#F4F6F3;border:1px solid #E4E9E5;'));
  N.btst='font-size:12.8px;font-weight:700;line-height:1.45;color:'+(bam?'#8A5A00':'#B42318')+';';
  return N; }
function osCard(self,t,o,mo,on){ const s=o.area?(nf(o.realizado||0)+'/'+nf(o.area)+' ha'+((o.realizado>0&&o.saldo>0)?' · saldo '+nf(o.saldo)+' ha':'')):(o.lam||'');
  const sub=[s,'janela '+o.janela,o.resp].filter(Boolean).join(' · ')+(mo&&mo.tal.length>1?' · O.S. de '+mo.tal.join(' + '):'');
  return {t:o.id+' · '+o.tipo,sub,ch:[CH(o.etapa,FCOR[o.etapa]||'gray')].concat((o.selos||[]).map(x=>CH(x.t,x.c||'yellow'))).concat(mo?[CH(mo.pz,CCH[PZC[mo.pz]])]:[]),
    on:on?'true':'false',go:()=>{ const s2=Object.assign({},self.state.osel||{}); s2[t]=o.id; self.setState({osel:s2,mpa:null}); },
    st:'display:flex;flex-direction:column;gap:5px;text-align:left;width:100%;box-sizing:border-box;padding:8px 10px;border-radius:10px;cursor:pointer;font-family:inherit;color:#15201A;'+(on?'border:2px solid #1E7A4C;background:#F4FAF6;':'border:1px solid #E4E9E5;background:#FFFFFF;')}; }
// seções do painel: uma funcionalidade por vez (a da barra), sempre aberta; sum é a linha de resumo usada no Integrado
function rotT(t){ return isLG(t)?((M.lg.pivos.find(p=>p.id===t)||{}).rot||t):t; }
function SEC(self,l,k,t,sum,b){ const s=Object.assign({k,t,sum,kv:[],items:[],note:'',lk:'',lkt:'',acts:[]},b||{});
  s.hasKv=s.kv.length>0; s.kvTop=s.hasKv&&!s.kvEnd; s.kvBot=s.hasKv&&!!s.kvEnd; s.hasNote=!!s.note; s.hasLk=!!s.lk; s.hasActs=s.acts.length>0;
  s.hasHd=!!s.hd; s.hd=s.hd||''; s.hdc=s.hdc||''; s.hdst=s.hdst||'';
  s.items=s.items.map(it=>Object.assign({cap:'',bst:''},it,{hasCap:!!it.cap})); return s; }
function panelTal(self,l,f,t){ const T=M.tal[t]; const c=cls(l,f,t); const lv=lavOf(t);
  const nomeT=isLG(t)?('Pivô '+String((M.lg.pivos.find(p=>p.id===t)||{}).rot||t).replace(/^P/,'')):t;
  const P={title:nomeT+' · '+nfx(T.ha)+' ha',sub:lv.sum.replace(/^Pivô \d+ · /,'')+' · '+(isLG(t)?'Lagoa Grande':'Santa Rita'),ch:[c.c==='sat'?CHs(c.l,c.solo?soloChipSt(c.hex):satChipSt(f.idx,c.ka)):CH(c.l,CCH[c.c]||'gray')],os:[],hasOs:false,nx:null,hasNx:false,secs:[],acts:[]};
  // ordens de serviço (cartões e próximo passo só na camada O.S.)
  const os=osMapa(t); P.os_t=os.length?('Ordens de serviço · '+os.length):'Nenhuma ordem neste talhão';
  if(os.length&&l==='O.S./prazos'){ let sel=((self.state.osel||{})[t]); if(!os.some(o=>o.id===sel)){ const ab=os.filter(o=>o.etapa!=='Encerradas'); sel=(ab[0]||os[0]).id; }
    P.os=os.map(o=>osCard(self,t,o,M.ord.find(m=>m.id===o.id),o.id===sel)); P.hasOs=true;
    const o=os.find(x=>x.id===sel); P.nx=nxOf(self,o,M.ord.find(m=>m.id===o.id)); P.hasNx=true; }
  // lavoura
  P.secs.push(SEC(self,l,'lav','Lavoura',lv.sum,{items:lv.rows.map(r=>({t:r.t,sub:r.sub,ch:r.ch.map(x=>CH(x[0],x[1])),acts:[]})),
    kv:M.geo[t]?[{l:'Geometria',t:M.geo[t]}]:[],lk:'SAF.dc.html',lkt:'Abrir no Planejar safra'}));
  // satélite (índice e cena do filtro da camada Satélite)
  { const fs=flt(self,'Satélite'); const v=satVal(fs.dt,t,fs.idx); const s=M.sat[fs.dt]; const nt=(s.nt||{})[t]||0; const es=satEstado(t,fs);
    const kv=[{l:'Cena',t:(s.real&&M.lg.rot?'Imagem sintética':'Sentinel-2 L2A')+' · aquisição '+s.aq+' · '+(s.real?s.proc:'processado '+s.proc)},{l:'Nuvem',t:nfx(nt,1)+' % no talhão · '+nfx(s.nuvem,2)+' % na cena'},{l:'Estado',t:es[0]}];
    let items=[], sum='', note='', acts=[];
    if(v===null){ sum=(M.semcult[t]||'sem cultura')+' · o índice não indica vigor'; note='Sem cultura com dossel: o índice não mede vigor aqui e não aciona compra nem prescrição.'; }
    else if(v==='cloud'){ sum='Nuvem na cena '+fs.dt+' · sem leitura'; note='Nuvem não recebe cor de condição. Escolha outra cena no filtro da camada Satélite.'; }
    else { const k=kOf(v,M.idx[fs.idx].lim); sum=fs.idx+' '+nfx(v,2)+' · '+satNome(fs.idx,k).toLowerCase()+' · cena '+fs.dt+' · '+es[0].toLowerCase();
      items=IDXN.map(ix=>{ const x=satVal(fs.dt,t,ix); const kk=kOf(x,M.idx[ix].lim); const pv=satPrev(fs.dt,t,ix); const dv=pv?(x-pv[1])/pv[1]*100:null;
        const dif=(ix==='NDMI'||Math.abs(pv?pv[1]:1)<0.1)?(pv?' · '+(x-pv[1]>=0?'+':'−')+nfx(Math.abs(x-pv[1]),2)+' vs '+pv[0]:''):(pv?' · '+(dv>=0?'+':'−')+nfx(Math.abs(dv),0)+' % vs '+pv[0]:'');
        return {t:ix+' '+nfx(x,2),sub:M.idx[ix].o+(pv?dif:' · sem cena anterior válida'),ch:[CHs(satNome(ix,kk),satChipSt(ix,kk))],acts:[],on:ix===fs.idx}; });
      const pxs=self.state.px; if(pxs&&pxs.t===t&&pxs.lg!==undefined&&LGI.px){ const q=(LGI.px.cen[fs.dt]||{})[fs.idx]; if(q&&q[pxs.lg]!==255){ const val=lgDeq(q[pxs.lg]); const kk=kOf(val,M.idx[fs.idx].lim);
        items.unshift({t:'Pixel selecionado · '+fs.idx+' '+nfx(val,2),sub:fmtLL(pxs.ll)+' · 10 m · cena '+fs.dt+(M.lg.rot?' ('+M.lg.rot+')':' (Sentinel-2 real)'),ch:[CHs(satNome(fs.idx,kk),satChipSt(fs.idx,kk))],acts:[]}); } }
      if(!s.manchas.some(m=>m.t===t)&&es[1]!=='green'){ const pq=satPrev(fs.dt,t,fs.idx); if(pq){ const dq=(v-pq[1])/Math.abs(pq[1])*100; if(dq<-10){ const vis0=mapVisAb(t,true);
        items.push({t:'Queda de '+nfx(Math.abs(dq),0)+' % no '+fs.idx+' desde '+pq[0],sub:'média do talhão '+nfx(pq[1],2)+' → '+nfx(v,2)+' · indício para inspeção, não diagnóstico',ch:[CH(es[0],es[1])],acts:[vis0?A('Abrir '+vis0,{h:'AG-01.dc.html#'+vis0,ic:'alert'}):A('Programar vistoria',{fn:()=>criarVis(self,[t]),ic:'alert',prim:es[1]==='red',tt:'Inspeção com ponto de GPS no centro do talhão; aparece no AG-01 e no app'})]}); } } }
      const px=self.state.px; if(px&&px.t===t&&M.px[t]&&M.px[t][px.i]){ const pvv=pxVals(fs.dt,fs.idx)[t]; if(pvv){ const val=pvv[px.i]; const kk=kOf(val,M.idx[fs.idx].lim);
        items.unshift({t:'Pixel selecionado · '+fs.idx+' '+nfx(val,2),sub:pxCoord(M.px[t][px.i])+' · 10 m · cena '+fs.dt+' (demonstrativo)',ch:[CHs(satNome(fs.idx,kk),satChipSt(fs.idx,kk))],acts:[]}); } }
      const vis=mapVisAb(t,true);
      s.manchas.filter(m=>m.t===t).forEach(m=>items.push({t:'Mancha · '+nfx(m.ha,1)+' ha · NDVI '+nfx(m.val,2),sub:m.evo+' · centroide '+m.coord+' · tipo provável: '+m.tipo+' · indício, não diagnóstico',
        ch:[CH(nfx(m.ha/T.ha*100,1)+' % do talhão','red')],acts:[vis?A('Abrir '+vis,{h:'AG-01.dc.html#'+vis,ic:'alert',tt:'Abrir a vistoria programada'}):A('Programar vistoria',{fn:()=>criarVis(self,[t]),ic:'alert',prim:es[1]==='red',tt:'Inspeção com ponto de GPS no centroide da mancha; aparece no AG-01 e no app'})]}));
      note=nt>0?'':''; }
    P.secs.push(SEC(self,l,'sat','Satélite',sum,{kv,items,note,lk:'AG-06.dc.html',lkt:'Ver histórico do talhão'})); }
  // insumos
  { const fi=flt(self,'Insumos'); const its=necAgg(t,fi.per); const st=insFaz().st[fi.per]||{};
    const items=its.map(x=>{ const s=st[x.p]||['—','gray','']; return {t:x.p+' · '+nfx(x.q,x.q%1?1:0)+' '+x.un,sub:'a partir de '+brIso(x.dt)+' · '+x.orig[0]+(x.orig.length>1?' +'+(x.orig.length-1):'')+' · '+s[2],ch:[CH(s[0],s[1]==='ok'?'green':s[1])].concat(s[3]?[CH(s[3],'yellow')]:[]),   /* falta firme + qualidade pendente: os dois à vista, uma ação (revisão do 16fb55e, ajuste 1) */
      acts:s[1]==='red'?[A('Comprar',{h:'CMP.dc.html',ic:'cart',tt:'Abrir Compra de insumos'})]:[]}; });
    const reqs=[]; osMapa(t).forEach(o=>{ if(!o.r||!o.r.itens||!o.r.itens.length||['Encerradas','Canceladas'].indexOf(o.etapa)>=0) return;
      o.r.itens.forEach(i=>reqs.push({t:o.r.id+' · '+o.id+' · '+i.prod,sub:'reservado '+nd(i.solicitado)+' '+i.un+' · lote '+i.lote+' · entregue '+nd(i.entregue)+' · em custódia '+nd(i.custodia)+' · consumido '+nd(i.consumido),ch:[CH(i.custodia>0.001?'em custódia':(i.entregue>0?'entregue':'reservado'),i.custodia>0.001?'yellow':'gray')],acts:[]})); });
    const fal=items.filter(x=>x.ch[0].t.indexOf('Falta')===0).length;
    const sum=its.length?(its.length+(its.length>1?' insumos':' insumo')+' · '+(fal?fal+(fal>1?' faltas':' falta'):'sem falta')+' · '+fi.per.toLowerCase()):(semPlanoOf(t)?'Sem plano na safra '+SAF:'Sem necessidade no período');
    P.secs.push(SEC(self,l,'ins','Insumos',sum,{items:items.concat(reqs),kv:[{l:'Período',t:fi.per+' (filtro da camada Insumos)'},{l:'Estoque',t:'compartilhado da fazenda · não é dividido por talhão'}],
      note:semPlanoOf(t)?'Cultivo da safra '+SAF+' sem plano: a necessidade vem só das O.S. abertas.':'',lk:'CMP.dc.html',lkt:'Abrir Compra de insumos'})); }
  // custos
  { const Pv=prevOf(t); const R=cusReal(t); const kv=[];
    if(Pv.fonte){ kv.push({l:'Previsto',t:money(Pv.tot)+' · '+money(Pv.tot/Pv.base)+'/ha'}); kv.push({l:'Área-base',t:nfx(Pv.base)+' ha · '+Pv.orig}); kv.push({l:'Composição',t:'insumos '+money(Pv.ins)+' · operação '+money(Pv.op)}); }
    else kv.push({l:'Previsto',t:'sem plano e sem O.S. no talhão'});
    kv.push({l:'Realizado provisório',t:R.ha?(money(R.rs)+' em '+nfx(R.ha,R.ha%1?1:0)+' ha executados · '+money(R.rs/R.ha)+'/ha-operação'):'sem apontamento aceito'});
    kv.push({l:'Conferido',t:R.haConf?(money(R.rsConf)+' em '+nfx(R.haConf)+' ha'):'nada conferido'});
    if(Pv.base) kv.push({l:'Cobertura',t:nfx(R.ha,R.ha%1?1:0)+' de '+nfx(Pv.base)+' ha com execução apontada'});
    const items=R.ords.map(x=>({t:x.o.id+' · '+((x.o.atv||{}).nome||x.o.tipo),sub:nfx(x.c.ha,x.c.ha%1?1:0)+' ha · insumos '+money(x.c.ins)+' · operação '+money(x.c.op)+(x.c.haConf?' · conferido '+money(x.c.rsConf):''),ch:[CH(money(x.c.rs),'gray')],acts:[A('Abrir ordem',{h:'OS.dc.html#'+x.o.id,ic:'doc'})]}))
      .concat(R.shared.map(x=>({t:x.o.id+' · compartilhada '+x.tal.join(' + '),sub:'realizado '+money(x.c.rs)+' em '+nfx(x.c.ha)+' ha · sem apontamento por talhão: não entra no R$/ha deste talhão',ch:[CH('sem rateio','yellow')],acts:[A('Abrir ordem',{h:'OS.dc.html#'+x.o.id,ic:'doc'})]})))
      .concat(Pv.pend.concat(R.pend).map(p=>({t:p,sub:'',ch:[CH('pendência','yellow')],acts:[]})));
    const sum=(Pv.fonte?'Previsto '+money(Pv.tot/Pv.base)+'/ha':'Sem previsto')+' · realizado '+(R.ha?mil(R.rs)+' ('+nfx(R.ha,R.ha%1?1:0)+' ha)':'—');
    P.secs.push(SEC(self,l,'cus','Custos',sum,{kv,items,lk:Pv.fonte==='plano'?'SAF.dc.html':'OS.dc.html',lkt:Pv.fonte==='plano'?'Abrir origem no Planejar safra':'Abrir origem nas O.S.'})); }
  // irrigação: rega de hoje, balanço hídrico e as ordens de irrigação do talhão
  const xi=M.irr[t]||{c:'none',l:'',d:null,hoje:'',ac:null};
  { const kv=[]; if(xi.d!==null){ kv.push({l:'Balanço hídrico',t:(xi.est?'≈ ':'')+'déficit '+nfx(xi.d,1)+' mm · '+xi.fon}); irrRecKv(xi).forEach(z=>kv.push(z)); if(xi.faixa) kv.push({l:'Passagem parcial',t:xi.faixa}); kv.push({l:xi.limt,t:xi.lam}); kv.push({l:'Equipamento',t:xi.eq}); kv.push({l:'Última rega',t:xi.ult}); }
    const IS=(()=>{ try{ return irrGet(); }catch(e){ return null; } })();
    const items=(xi.ords||[]).map(o=>{ const et=irrEtapa(IS,o); return {t:o.id+' · Irrigação · '+(o.fert?'v2 com produto':'água'),sub:'Janela '+irrJanO(o)+' · '+irrMm(o.lam)+' mm'+(o.passadas.length>1?' em '+o.passadas.length+' passadas':''),
        ch:[CH(et,FCOR[et]||'gray')].concat(irrSelos(IS,o).filter(z=>!z.mut).map(z=>CH(z.t,z.c))),acts:[A('Abrir ordem',{h:'IR-03det.dc.html#'+o.id,ic:'doc',tt:'Ordem de irrigação (módulo Irrigação)'})]}; })
      .concat(M.ord.filter(o=>o.tal.indexOf(t)>=0&&/irriga/i.test(o.tipo)&&!irrAgua(o)&&o.fase!=='Encerradas').map(o=>({t:o.id+' · '+o.tipo,sub:'Janela '+o.jan+' · '+o.real,
      ch:[CH(o.fase,FCOR[o.fase])].concat(o.selos.map(x=>CH(x[0],x[1]))),acts:[A('Abrir ordem',{h:'OS.dc.html#'+o.id,ic:'doc',tt:'Ordem de Serviço'})]})));
    const hdst='border-left:4px solid '+((M.lcop[xi.c]||M.lcop.none)[0])+';background:#F7F9F7;border-radius:8px;padding:7px 10px;display:flex;flex-direction:column;gap:2px;';
    P.secs.push(SEC(self,l,'irr','Irrigação',xi.l||'sem irrigação',{hd:xi.hoje||'',hdc:'Hoje',hdst,kv:xi.d!==null?kv:[],note:xi.d!==null?'':(isLG(t)?'Pivô em preparo de área: sem rega até o plantio.':'Talhão de sequeiro: sem irrigação.'),items,
      lk:xi.d!==null?'IR-01.dc.html#'+t:'',lkt:'Abrir setor na Irrigação'})); }
  // pragas e doenças (MIP/MID): a mesma base do AG-01; o próximo passo é o da pior vistoria (mipProx) e abre a vistoria no AG-01
  const fm=flt(self,'MIP/MID'); const smp=mipGet(); const vsM=mipOf(t,fm.per); const cm=cls('MIP/MID',fm,t); let mipAc=null;
  { const rit=mipRitmo(smp,t); const tm=MIPD.tal[t]||{}; const semP=mipSemProt(t);
    // o primário é o próximo passo da pior vistoria: comando sem formulário roda aqui; decidir abre a decisão no AG-01; programar, a vistoria atrasada
    const v0=vsM[0]; const prog=['Programar vistoria',{fn:()=>criarVis(self,[t]),tt:'Vistoria do protocolo da cultura; aparece no AG-01 e no app'}];
    const RUN=['sinc','parcial','monitorar','pos','programar']; let Px=null;
    if(!semP&&v0){ Px=mipProx(smp,v0.v,MAPC); if(Px.t) mipAc=[Px.t,RUN.indexOf(Px.fn)>=0?{fn:()=>mapMipRun(self,v0.v.id,Px.fn),tt:Px.txt}:((Px.h&&Px.h.indexOf('AG-01')<0)?{h:Px.h,tt:Px.txt}:{h:Px.h||('AG-01.dc.html#'+v0.v.id+(Px.fn==='decidir'?':decidir':'')),tt:Px.txt})]; }
    // a vistoria do primário de decisão não repete "Abrir" para o mesmo painel
    const dupId=(Px&&Px.fn==='decidir')?v0.v.id:'';
    const items=vsM.map(x=>{ const p=mipP(x.v); return {t:x.v.id+' · '+p.alvo,sub:mipBr(x.v.data)+' · '+x.S.R.txt+(x.S.sub&&x.S.k!=='perto'?' · '+x.S.sub:''),ch:[CH(x.S.t,x.S.c)],acts:x.v.id===dupId?[]:[A('Abrir '+x.v.id,{h:'AG-01.dc.html#'+x.v.id,ic:'alert'})]}; });
    const kv=semP?[]:[{l:'Última vistoria',t:rit.ult?(mipBr(rit.ult.data)+' · '+rit.ult.id+' · '+mipP(rit.ult).alvo):'nenhuma registrada'},
      {l:'Ritmo',t:rit.aberta?('vistoria aberta · '+rit.aberta):(rit.prox?(rit.atras?'atrasada desde '+mipBr(rit.prox):'próxima em '+mipBr(rit.prox)):'sem histórico')},
      {l:'Protocolo',t:((tm.cultura||'')+' '+(tm.fase||'')).trim()+' · '+(MIPD.prots[t]||[]).map(k=>MIPD.prot[k].alvo).join(', ')}];
    if(!semP&&!mipAc&&(!v0||rit.atras)&&!rit.aberta) mipAc=prog;
    P.secs.push(SEC(self,l,'mip','Pragas e doenças',cm.l,{kv,items,note:semP?'Sem cultura no talhão: sem protocolo de monitoramento.':'',lk:'AG-01.dc.html',lkt:'Abrir Pragas e doenças'})); }
  P.secs.push(carSec(self,l,t));   // MAPA-CARENCIA-LMR-20261003
  P.secs.push(soloSec(self,t));   // Análises de solo (13/10/2026)
  P.secs.push(colhSec(self,t));   // Colheita (14/10/2026)
  // foco: o painel mostra só a funcionalidade escolhida na barra; no Integrado, uma linha por funcionalidade que leva até ela
  const KL={'Satélite':'sat','Lavoura':'lav','MIP/MID':'mip','Irrigação':'irr','Insumos':'ins','Custos':'cus'}; const byK={}; P.secs.forEach(x=>{ byK[x.k]=x; });
  KL[CAR_L]='car';   // MAPA-CARENCIA-LMR-20261003
  KL[SOLO_L]='solo'; KL[COLH_L]='colh';
  if(l==='O.S./prazos'){ P.secs=[]; P.acts=[A('Nova O.S. neste talhão',{h:'OS.dc.html',ic:'doc',tt:'Abrir Ordem de Serviço para emitir uma ordem'})]; return P; }
  const semRep=(P0)=>{ const hs=P0.acts.filter(a=>a.isH).map(a=>a.h); P0.secs.forEach(x=>{ const lh=x.lk?[x.lk]:[];
      x.items.forEach(it=>{ it.acts=(it.acts||[]).filter(a=>!(a.isH&&(hs.indexOf(a.h)>=0||lh.indexOf(a.h)>=0))); }); if(x.lk&&hs.indexOf(x.lk)>=0){ x.lk=''; x.hasLk=false; } }); return P0; };
  if(l===SOLO_L){ P.secs=[byK.solo]; P.acts=[soloAc(t)]; return semRep(P); }
  if(l===COLH_L){ P.secs=[byK.colh]; P.acts=[colhAc(t)]; return semRep(P); }   // um próximo passo: o da tela Previsão e colheita   // um próximo passo: abrir, validar ou registrar o laudo
  if(l===CAR_L){ P.secs=[byK.car]; const ca=carAc(t,flt(self,CAR_L)); P.acts=ca?[A(ca[0],Object.assign({ic:'calendar',prim:true},ca[1]))]:[]; return semRep(P); }   // MAPA-CARENCIA-LMR-20261003
  if(KL[l]){ P.secs=[byK[KL[l]]]; P.acts=(l==='Irrigação'&&xi.ac)?[A(xi.ac[0],{h:xi.ac[1],ic:'drop',prim:true})]:((l==='MIP/MID'&&mipAc)?[A(mipAc[0],Object.assign({ic:'alert',prim:true},mipAc[1]))]:[]); return semRep(P); }
  const VER={'Satélite':['Ver satélite','satelite'],'Lavoura':['Ver lavoura','leaf'],'MIP/MID':['Ver pragas e doenças','inseto'],'O.S./prazos':['Ver ordens','doc'],'Irrigação':['Ver irrigação','drop'],'Insumos':['Ver insumos','box'],'Custos':['Ver custos','cash']};
  VER[CAR_L]=['Ver carência','calendar'];   // MAPA-CARENCIA-LMR-20261003
  VER[SOLO_L]=['Ver análises de solo','frasco'];
  VER[COLH_L]=['Ver colheita','Colheita'];
  const ab=os.filter(o=>['Encerradas','Canceladas'].indexOf(o.etapa)<0).length;
  const osRes=os.length?(os.length+(os.length>1?' ordens':' ordem')+' · '+ab+(ab===1?' aberta':' abertas')):'nenhuma ordem neste talhão';
  const hub=M.lays.filter(x=>x!=='Integrado').map(x=>{ const fx=flt(self,x); const c=cls(x,fx,t); const nm=M.nome[x]||x;
    const sb=x==='O.S./prazos'?osRes:((byK[KL[x]]||{}).sum||'');
    return {t:nm,sub:sb===c.l?'':sb,ch:[c.c==='sat'?CHs(c.l,c.solo?soloChipSt(c.hex):satChipSt(fx.idx,c.ka)):CH(c.l||'—',CCH[c.c]||'gray')],
      acts:[A(VER[x][0],{fn:()=>self.setState({lay:x,cvis:false,mpa:null}),ic:VER[x][1],tt:'Mostrar no painel só '+nm.toLowerCase()+' deste talhão'})]}; });
  P.secs=[SEC(self,l,'hub','Neste talhão','',{items:hub})]; P.acts=[]; return P; }
function panelArea(self,l,f,sel){ const ha=sel.reduce((a,t)=>a+M.tal[t].ha,0); const vs={}; sel.forEach(t=>{ const id=mapVisAb(t,l==='Satélite'); if(id) vs[t]=id; });
  const P={title:'Área selecionada · '+sel.length+' talhões',sub:sel.join(' + ')+' · '+nfx(ha)+' ha',ch:[],os:[],hasOs:false,nx:null,hasNx:false,secs:[],acts:[]};
  P.secs.push(SEC(self,'','are','Talhões',sel.length+' talhões · '+nfx(ha)+' ha',{items:sel.map(t=>{ const c=cls(l,f,t); return {t:t+' · '+lavOf(t).sum,sub:nfx(M.tal[t].ha)+' ha',ch:[c.c==='sat'?CHs(c.l,c.solo?soloChipSt(c.hex):satChipSt(f.idx,c.ka)):CH(c.l,CCH[c.c]||'gray')].concat(vs[t]?[CH(vs[t],'green')]:[]),acts:[]}; })}));
  const os=M.ord.filter(o=>!irrAgua(o)&&o.tal.some(t=>sel.indexOf(t)>=0)); if(l==='O.S./prazos') P.secs.push(SEC(self,'','aos','Ordens na área · '+os.length,os.map(o=>o.id).join(', ')||'nenhuma',{items:os.map(o=>({t:o.id+' · '+o.tipo,sub:'Janela '+o.jan+' · '+o.real,ch:[CH(o.fase,FCOR[o.fase])].concat(o.selos.map(s=>CH(s[0],s[1]))),acts:[A('Abrir ordem',{h:'OS.dc.html#'+o.id,ic:'doc'})]}))}));
  P.acts=((l==='Satélite'||l==='MIP/MID')?[A('Programar vistoria nas áreas',{fn:()=>criarVis(self,sel),ic:'alert',tt:'Programar uma vistoria por talhão: '+sel.join(', ')})]:[]).concat([A('Limpar seleção',{fn:()=>self.setState({tsel:[]}),ic:'map'})]); return P; }
function svgPt(e){ try{ const el=e&&(e.currentTarget||e.target); const svg=el&&el.ownerSVGElement; if(!svg||!svg.getScreenCTM) return null; const p=svg.createSVGPoint(); p.x=e.clientX; p.y=e.clientY;
  const q=p.matrixTransform(svg.getScreenCTM().inverse()); return [q.x,q.y]; }catch(x){ return null; } }
function MAPVALS(self,v){
  M.ord=mapOrdsCen(); OSN=ords(self); M.irr=irrMapa();
  const faz0=self.state.mf_faz||'Lagoa Grande'; FAZ=(faz0==='Lagoa Grande')?'Lagoa Grande':'Santa Rita';
  { const s0=self.state; SAF=safOpts().indexOf(s0.mf_saf)>=0?s0.mf_saf:'2026/27'; CULT=cultOpts().indexOf(s0.mf_cult)>=0?s0.mf_cult:'Todas';
    const av=alvosFaz(); const a=(s0.mipAlvos||[]).filter(x=>av.indexOf(x)>=0); ALV=a.length?a:null; }
  // contexto do mapa (camada, seleção, filtros, zoom, ordem escolhida) preservado ao voltar de outra tela
  if(!self.__ctx){ self.__ctx=1; let s=null; try{ s=JSON.parse(sessionStorage.getItem('mapa-ctx')||'null'); }catch(e){ s=null; }
    if(s){ setTimeout(()=>{ self.__ctxOk=1; self.setState(s); },0); } else self.__ctxOk=1; }
  carHash(self);   // MAPA-CARENCIA-LMR-20261003
  SOLOST=((self.state.flt||{})[SOLO_L])||{};   // camada do solo escolhida: as opções de Laudo e Indicador dependem dela
  const st=self.state; const l=lay(self); const f=flt(self,l); const sel=(st.tsel||[]).filter(t=>TIDS().indexOf(t)>=0);
  if(self.__ctxOk){ try{ sessionStorage.setItem('mapa-ctx',JSON.stringify({mf_faz:st.mf_faz||'Lagoa Grande',mf_saf:st.mf_saf||'2026/27',mf_cult:st.mf_cult||'Todas',mipAlvos:st.mipAlvos||[],lay:st.lay||'Integrado',tsel:st.tsel||[],flt:st.flt||{},zoom:st.zoom||1,osel:st.osel||{},px:st.px||null})); }catch(e){} }
  const CTRD={'Talhão':'Cores dentro de cada talhão: mostra onde ele está melhor e pior.','Fazenda':'Uma escala para a fazenda inteira: compara um talhão com o outro.','Absoluto':'Limites fixos do índice: compara cenas e safras.'};
  const VERD={'Hoje':'O que fazer hoje em cada área: irrigando, programada, a programar, impedida ou sem necessidade.','Balanço hídrico':'Falta de água no solo em mm: evapotranspiração menos chuva e irrigação desde a última reposição.'};
  VERD['Últimos 7 dias']='Vistorias da última semana: o ritmo recomendado de monitoramento.'; VERD['Últimos 30 dias']='Vistorias do último mês, inclusive as que já passaram do ritmo semanal.';
  const dica=(k,o)=>(k==='per'&&l==='MIP/MID')?(VERD[o]||''):k==='idx'?((M.idx[o]||{}).d||''):(k==='ctr'?(CTRD[o]||''):(k==='ver'?(VERD[o]||''):(k==='dt'?'Imagem de satélite de '+o:'')));
  v.flt=fopts(l).map(g=>({l:g.l,sel:!!g.sel,seg:!g.sel,val:f[g.k],sopts:g.sel?g.o.map(o=>({v:o,t:(g.t||{})[o]||o})):[],
    set:(e)=>{ const x=e.target.value; const all=Object.assign({},self.state.flt||{}); all[l]=Object.assign({},all[l]||{},{[g.k]:x}); const st0={flt:all,g2toast:g.l+': '+((g.t||{})[x]||x)};
      if(l===SOLO_L&&g.k==='lau'&&x!=='Mais recente'){ const t=soloTalDe(x); if(t) Object.assign(st0,{tsel:[t],px:null,mpa:null}); } self.setState(st0); },
    opts:g.sel?[]:g.o.map(o=>({t:o,tt:dica(g.k,o),on:(f[g.k]===o)?'true':'false',go:()=>{ const all=Object.assign({},self.state.flt||{}); all[l]=Object.assign({},all[l]||{},{[g.k]:o}); self.setState({flt:all}); },
    st:'font-family:inherit;font-size:11.8px;font-weight:700;padding:4px 9px;border:0;border-radius:7px;cursor:pointer;white-space:nowrap;'+(f[g.k]===o?'background:#1E7A4C;color:#fff;':'background:transparent;color:#15201A;')}))}));
  v.fonte=fonte(l,f); v.leg=legend(self,l,f,sel); v.nums=strip(self,l,f); v.lay_t=(M.nome[l]||l); const z=st.zoom||1;
  v.zst='transform:scale('+z+');transform-origin:50% 50%;transition:transform .2s;width:100%;height:100%;'; v.zin=()=>{ if(FAZ==='Lagoa Grande'&&LGI.map){ LGI.map.zoomIn(); return; } self.setState({zoom:Math.min(2,(self.state.zoom||1)+0.25)}); }; v.zout=()=>{ if(FAZ==='Lagoa Grande'&&LGI.map){ LGI.map.zoomOut(); return; } self.setState({zoom:Math.max(1,(self.state.zoom||1)-0.25)}); };
  const FL={'Integrado':['Abrir ordens','OS.dc.html'],'Satélite':['Ver histórico','AG-06.dc.html'],'Lavoura':['Abrir safra','SAF.dc.html'],'O.S./prazos':['Abrir ordens','OS.dc.html'],'Irrigação':['Abrir irrigação','IR-01.dc.html#faz='+encodeURIComponent(FAZ)],'MIP/MID':['Abrir Pragas e doenças','AG-01.dc.html'],'Insumos':['Abrir compras','CMP.dc.html'],'Custos':['Abrir safra','SAF.dc.html']};
  FL[CAR_L]=['Abrir qualidade dos lotes','CO-06.dc.html'];   // MAPA-CARENCIA-LMR-20261003
  v.flink=(FL[l]||['',''])[1]; v.flinkt=(FL[l]||['',''])[0]; v.hasFlink=!!FL[l]; v.hasFvis=(l==='MIP/MID');
  const lst=(on)=>'width:48px;height:48px;box-sizing:border-box;padding:0;border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0;cursor:pointer;position:relative;flex-shrink:0;font-family:inherit;border:0;'+(on?'background:#1E6B47;color:#FFFFFF;':'background:transparent;color:#4B5A51;');
  M.lays.forEach((x,i)=>{ v['ly'+i+'_st']=lst(x===l); v['ly'+i+'_on']=(x===l)?'true':'false'; v['ly'+i+'_go']=()=>self.setState({lay:x,cvis:false,mpa:null,alvAb:false}); });
  const ms=(l==='Satélite')?M.sat[f.dt].manchas:[];
  M.tids.forEach(t=>{ const c=cls(l,f,t); const on=sel.indexOf(t)>=0; const lc=M.lcop[c.c]||M.lcop.none;
    v['fl_'+t]=c.c==='cloud'?'url(#hatch)':(c.c==='sat'?c.hex:lc[0]); v['fo_'+t]=(c.c==='none'||c.c==='cloud'||c.c==='sat')?'1':'0.88';
    v['sk_'+t]=on?'#15201A':'#FFFFFF'; v['sw_'+t]=on?'6':'4'; v['sub_'+t]=M.tal[t].cult+' · '+nfx(M.tal[t].ha)+' ha'; v['lab_'+t]=c.l; v['al_'+t]=t+': '+c.l;
    const m=ms.find(x=>x.t===t); v['mo_'+t]=m?'1':'0'; v['ml_'+t]=m?(nfx(m.ha,1)+' ha'):''; v['mr_'+t]=m?String(m.r):'0';
    v['tk_'+t]=(e)=>{ const s=self.state; if(s.medir){ self.setState({g2toast:'Medição · '+t+': '+nfx(M.tal[t].ha)+' ha · perímetro ≈ '+M.tal[t].per+' km (geometria do cadastro).'}); return; }
      if(s.cvis){ criarVis(self,[t],{tsel:[t]}); return; }
      if(!s.selm&&lay(self)==='Satélite'&&M.px[t]){ const p=svgPt(e); if(p){ const cs=M.px[t]; const i=cs.findIndex(q=>p[0]>=q[0]&&p[0]<q[0]+M.cs&&p[1]>=q[1]&&p[1]<q[1]+M.cs);
        if(i>=0&&typeof satVal(flt(self,'Satélite').dt,t,flt(self,'Satélite').idx)==='number'){ self.setState({tsel:[t],px:{t,i},mpa:null}); return; } } }
      let ss=(s.tsel||[]).slice(); if(s.selm){ const i=ss.indexOf(t); if(i>=0) ss.splice(i,1); else ss.push(t); } else ss=(ss.length===1&&ss[0]===t)?[]:[t]; self.setState({tsel:ss,px:null,mpa:null}); };
    v['tkk_'+t]=(e)=>{ if(e&&(e.key==='Enter'||e.key===' ')){ e.preventDefault(); v['tk_'+t](); } }; });
  // pixels do satélite: cor por pixel na camada Satélite (índice, cena e contraste do filtro); fora dela, invisíveis
  { const fs=flt(self,'Satélite'); const on=(l==='Satélite'); const pv=on?pxVals(fs.dt,fs.idx):{}; const LF=on&&fs.ctr!=='Talhão'?satLims(fs,null):null;
    Object.keys(M.px).forEach(t=>{ const vals=pv[t]; const L=vals?(LF||satLims(fs,t)):null; v['pxo_'+t]=(on&&vals)?'1':'0';
      M.px[t].forEach((c,i)=>{ v['px_'+t+'_'+i]=vals?satCor(fs.idx,kOf(vals[i],L)):'none'; }); });
    const px=st.px; const okp=on&&px&&M.px[px.t]&&M.px[px.t][px.i]&&pv[px.t]; v.pxs_o=okp?'1':'0'; v.pxs_x=okp?String(M.px[px.t][px.i][0]):'0'; v.pxs_y=okp?String(M.px[px.t][px.i][1]):'0'; }
  // mapa de calor do solo (15/10/2026): cada célula do talhão com laudo recebe o valor interpolado dos pontos; os pontos aparecem por cima
  v.solo_pts=[];
  if(l===SOLO_L&&FAZ!=='Lagoa Grande'){ const G=soloGrade(f); const ind=SOLO_IND[f.ind]; const LF=f.ctr==='Fazenda'?soloLims(f,null,G):null;
    Object.keys(M.px).forEach(t=>{ const o=G[t]; const ok=!!(o&&o.vals.length&&inF(t)); if(!ok) return; v['pxo_'+t]='1'; const L=f.ctr==='Talhão'?soloLims(f,t,G):LF;
      M.px[t].forEach((c,i)=>{ v['px_'+t+'_'+i]=soloCor(f,ind,o.vals[i],L); }); o.pts.forEach(p=>v.solo_pts.push({x:String(Math.round(p.x*10)/10),y:String(Math.round(p.y*10)/10)})); }); }
  v.pan_open=sel.length>0; v.pan_close=()=>self.setState({tsel:[],px:null,mpa:null});
  const E0={title:'',sub:'',ch:[],os:[],hasOs:false,nx:null,hasNx:false,secs:[],acts:[],os_t:''};
  const P=sel.length===1?panelTal(self,l,f,sel[0]):(sel.length>1?panelArea(self,l,f,sel):E0);
  const pk=sel.join(',')+'|'+l; if(self.__pk!==pk){ self.__pk=pk; setTimeout(()=>{ const a=document.querySelector('aside[aria-label]'); const sc=a&&[...a.children].find(d=>getComputedStyle(d).overflowY==='auto'); if(sc) sc.scrollTop=0; },0); }
  v.pan=P; v.pan_hasos=!!P.hasOs; v.pan_hasnx=!!P.hasNx; v.nx=P.nx||nxVazio(); v.pan_ost=P.os_t||''; v.pan_hasost=sel.length===1&&l==='O.S./prazos'; v.pan_hasacts=P.acts.length>0;
  // barra de ferramentas
  const rst=(on)=>'display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:10px;cursor:pointer;font-family:inherit;font-size:12px;font-weight:700;color:#15201A;box-shadow:0 1px 3px rgba(21,32,26,.18);'+(on?'border:1px solid #1E7A4C;background:#E4F3E9;':'border:1px solid #E4E9E5;background:#FFFFFF;');
  v.r_selm_st=rst(!!st.selm); v.r_medir_st=rst(!!st.medir); v.r_full_st=rst(!!st.full); v.r_pref_st=rst(!!st.pref); v.r_link_st=rst(false);
  v.r_selm=()=>self.setState({selm:!st.selm,medir:false,cvis:false,g2toast:!st.selm?'Selecionar área: clique nos talhões para somar à seleção.':'Seleção múltipla desligada.'});
  v.r_medir=()=>self.setState({medir:!st.medir,selm:false,cvis:false,g2toast:!st.medir?'Medir: clique num talhão para ver área e perímetro.':'Medição desligada.'});
  v.r_vis_st=rst(!!st.cvis); v.r_vis_on=st.cvis?'true':'false';
  v.r_vis=()=>{ const s0=self.state; const ss=(s0.tsel||[]).filter(t=>TIDS().indexOf(t)>=0); if(ss.length&&!s0.cvis){ criarVis(self,ss); return; }
    self.setState({cvis:!s0.cvis,selm:false,medir:false,g2toast:!s0.cvis?'Programar vistoria: clique num talhão.':'Programação de vistoria desligada.'}); };
  v.r_full=()=>self.setState({full:!st.full}); v.full=!!st.full;
  v.r_pref=()=>self.setState({pref:!st.pref}); v.r_pref_t='';
  v.modo=st.selm?'Selecionar área · clique para somar talhões':(st.medir?'Medir · clique num talhão':(st.cvis?'Programar vistoria · clique num talhão':'')); v.sem_modo=!(st.selm||st.medir||st.cvis); v.has_modo=!!(st.selm||st.medir||st.cvis);
  // filtro Fazenda do topo: só a Santa Rita tem geometria; Boa Vista = estado vazio no lugar do mapa; Todas = Santa Rita + aviso
  const faz=st.mf_faz||'Lagoa Grande'; const semGeo=(faz==='Boa Vista');
  v.mf_faz=faz; v.mf_setfaz=(e)=>self.setState({mf_faz:e.target.value,tsel:[],px:null,mpa:null,g2toast:'Fazenda: '+e.target.value});
  v.mf_saf=SAF; v.mf_saf_opts=safOpts().map(x=>({v:x,t:x})); v.mf_setsaf=(e)=>self.setState({mf_saf:e.target.value,px:null,mpa:null,g2toast:'Safra: '+e.target.value});
  v.mf_cult=CULT; v.mf_cult_opts=cultOpts().map(x=>({v:x,t:x})); v.mf_setcult=(e)=>self.setState({mf_cult:e.target.value,px:null,mpa:null,g2toast:'Cultura: '+e.target.value});
  // alvos da camada Pragas e doenças (15/10/2026, proprietário: "selecionar qual alvo se deseja focar ... 1 só, todos ou mais de 1"): marcar um alvo
  // com "Todos" ligado foca só nele; marcar outros soma; desmarcar o último volta a Todos
  { const alvs=alvosFaz(); v.alv_on=(l==='MIP/MID')&&alvs.length>0; v.alv_open=v.alv_on&&!!st.alvAb; v.alv_exp=v.alv_open?'true':'false';
    v.alv_t=ALV?(ALV.length===1?ALV[0]:ALV.length+' de '+alvs.length):'Todos'; v.alv_tog=()=>self.setState({alvAb:!self.state.alvAb});
    v.alv_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); self.setState({alvAb:false}); setTimeout(()=>{ const b=document.querySelector('[aria-haspopup][data-alv]'); if(b) b.focus(); },0); } };
    const op=(t,on,go)=>({t,on:on?'true':'false',go,ck:'✓',st:'display:flex;align-items:center;gap:8px;width:100%;text-align:left;padding:7px 10px;min-height:36px;border:0;border-radius:8px;font-family:inherit;font-size:12.5px;font-weight:600;cursor:pointer;color:#15201A;background:'+(on?'#E4F3E9':'transparent')+';',
      bx:'width:16px;height:16px;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;flex-shrink:0;box-sizing:border-box;'+(on?'background:#1E7A4C;color:#FFFFFF;border:1px solid #1E7A4C;':'background:#FFFFFF;color:transparent;border:1.5px solid #9AA59E;')});
    v.alv_opts=[op('Todos',!ALV,()=>self.setState({mipAlvos:[],alvAb:false,g2toast:'Alvos: todos'}))].concat(alvs.map(a=>op(a,!!(ALV&&ALV.indexOf(a)>=0),()=>{ const cur=(ALV||[]).slice(); const i=cur.indexOf(a); if(i>=0) cur.splice(i,1); else cur.push(a);
      self.setState({mipAlvos:cur,g2toast:cur.length?('Alvos: '+cur.join(', ')):'Alvos: todos'}); }))); }
  v.map_on=!semGeo; v.map_vazio=semGeo; v.aviso_bv=(faz==='Todas');
  // Lagoa Grande: mapa real (MapLibre GL + Sentinel-2) · Santa Rita (e Todas): desenho demonstrativo
  v.map_lg=(FAZ==='Lagoa Grande')&&!semGeo; v.map_sr=!v.map_lg; v.has_full=!v.map_lg; v.lg_err=!!(v.map_lg&&LGI.erro); v.lg_errt=LGI.erro?('Mapa real indisponível: '+LGI.erro+'. Recarregue a página.'):'';
  const cena0=M.sat[(l==='Satélite')?f.dt:M.lg.cenas[0].k]||{};
  // legenda: só o selo (sintético) ou a atribuição curta da imagem real; o resto da fonte fica na dica ⓘ da camada (proprietário, 13/10/2026: menos texto)
  v.leg_nota=v.map_lg?(M.lg.rot||('Copernicus Sentinel-2 · '+(cena0.aq||'').split(' ')[0])):'Demonstrativo';
  if(v.map_lg) setTimeout(()=>{ lgEnsure(self); lgSync(self); },0);
  if(semGeo){ v.nums=[]; v.flt=[]; v.leg=[]; v.fonte='Fazenda Boa Vista · nenhum talhão com geometria'; v.hasFlink=false; v.pan_open=false; v.has_modo=false; v.sem_modo=false; }
  const ordF=M.ord.filter(o=>o.tal.some(t=>TIDS().indexOf(t)>=0));
  const imp=ordF.filter(o=>o.fase!=='Encerradas'&&o.selos.some(s=>/^(Impedida|Falta máquina)/.test(s[0]))).map(o=>o.id); const nl0=ordF.filter(o=>o.act&&o.act.k==='lib').length;
  const lista=(a)=>a.length>1?a.slice(0,-1).join(', ')+' e '+a[a.length-1]:a.join('');
  v.hs_t=semGeo?'Boa Vista sem talhões desenhados':([imp.length?lista(imp)+(imp.length>1?' impedidas':' impedida'):'',nl0?nl0+' a liberar':''].filter(Boolean).join(' · ')||'Sem pendências');
  v.hs_st=chipSt(semGeo?'gray':(imp.length?'red':(nl0?'yellow':'green')));
  tmVals(self,v); if(st.dw){ v.sem_modo=false; }   // desenho e importação de talhões (talmapa.js)
}
function nxVazio(){ return {id:'',t:'',btn:'',isBtn:false,go:()=>{},bloq:false,bt:'',bq:'',hasBh:false,bh:'#',bhl:'',conf:false,ct:'',cbtn:'',yes:()=>{},back:()=>{},ap:false,ad:'',aha:'',asub:'',setad:()=>{},setaha:()=>{},asave:()=>{},err:'',hasErr:false,dono:'',hasDono:false,open:'#',hasLib:false,libt:'',libh:'#',idle:true,semAcao:false,st:'',btst:'',dst:'',bst:'',hasOpen:false}; }
'''

# ---- camada Carência e destino (MAPA-CARENCIA-LMR-20261003): o motor (CARD, carEstado, carAvaliar…) vem do núcleo da O.S. ----
MAP_JS += r'''
const CAR_L='Carência e destino';
const CARCOR={curso:'red',insuf:'yellow',cumprida:'blue',sem:'gray'};
let CARC={k:'',m:{}};
function carQd(f){ return carAdd(CARD.hoje,({'Em 7 dias':7,'Em 14 dias':14})[(f||{}).qd]||0); }
function carCen(){ return MAPC||cenGet(); }
function carEst(t,f){ const c=carCen(); const ate=carQd(f); const k=(c.rev||0)+'|'+ate+'|'+Object.keys(c.ordens||{}).length; if(CARC.k!==k) CARC={k,m:{}}; return CARC.m[t]||(CARC.m[t]=carEstado(c,t,ate)); }
function carCls(t,f){ if(!CARD.tal[t]) return {c:'none',l:''}; if(semCultura(t)) return {c:'none',l:'sem lavoura em colheita'}; const e=carEst(t,f); return {c:CARCOR[e.k],l:carRot(e)}; }
function carLegend(){ return [Lc(CAR_L,'red','carência em curso · colheita impedida'),Lc(CAR_L,'yellow','dados insuficientes · conferir'),Lc(CAR_L,'blue','prazo cumprido · destino a avaliar por lote'),Lc(CAR_L,'gray','sem aplicação apontada'),Lc(CAR_L,'none','sem lavoura em colheita')]; }
function carAtual(){ const c=carCen(); let n=0; Object.keys(c.ordens||{}).forEach(k=>{ n+=(c.ordens[k].ap||[]).filter(a=>a.sinc===false).length; }); const d=new Date();
  return 'O.S. lidas às '+('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2)+' · revisão '+(c.rev||0)+(n?' · '+n+' aguardando sinal':' · nada aguardando sinal'); }
function carFonte(f){ const q=carQd(f); return 'consultado em '+carBr(q)+(q===CARD.hoje?' (hoje)':'')+' · aplicações apontadas nas O.S. (planejado não conta) × bula de referência (Agrofit demonstrativo) · LMR Brasil: ANVISA, extração '+carBr(CARD.lmrf.extraido)+' · destino avaliado por lote · '+carAtual(); }
function carLotesTal(t){ const c=carCen(); const L=carLotes(c); return Object.keys(L).map(k=>L[k]).filter(l=>carAncestrais(L,l.id).some(x=>x.tipo==='campo'&&x.tal===t)).sort((a,b)=>(a.d<b.d?1:(a.d>b.d?-1:(a.id<b.id?1:-1)))); }
function carStrip(f){ const N=(k,val,d)=>({k,val,d:d||''}); const ts=TIDS(); const es=ts.filter(t=>CARD.tal[t]&&!semCultura(t)).map(t=>carEst(t,f)); const c=carCen(); const L=carLotes(c);
  const ls=Object.keys(L).filter(k=>carAncestrais(L,k).some(x=>x.tipo==='campo'&&ts.indexOf(x.tal)>=0)); const av=ls.map(k=>carAvaliar(c,k));
  let sinc=0; Object.keys(c.ordens||{}).forEach(k=>{ sinc+=(c.ordens[k].ap||[]).filter(a=>a.sinc===false).length; });   // pendência de dado: à vista quando há (o resto da fonte vai para o ⓘ)
  return [N('Em carência',es.filter(e=>e.k==='curso').length,'Carência em curso · colheita impedida'),N('A conferir',es.filter(e=>e.k==='insuf').length,'Dados insuficientes · conferir'),N('Cumprido',es.filter(e=>e.k==='cumprida').length,'Prazo cumprido · destino a avaliar por lote'),N('Lotes',av.filter(a=>a.st!=='conforme').length+' de '+av.length,'Lotes a resolver')]
    .concat(sinc?[N('Aguardando sinal',sinc,'Apontamentos aguardando sinal do app')]:[]); }
// rótulo curto da pendência que impede confirmar o prazo (o detalhe fica no item da lista)
const CARPK={regra:'carência não encontrada na bula',bula:'carência não conferida na bula',exec:'aplicação sem apontamento completo',data:'apontamento sem data',sinc:'apontamento aguardando sinal',canc:'O.S. cancelada com apontamento'};
function carSec(self,l,t){ const f=flt(self,CAR_L); const e=carEst(t,f); const ate=e.ate; const T=CARD.tal[t]||{}; const c=carCen(); const items=[]; const sc=semCultura(t);
  const kv=[{l:'Consultado em',t:carBr(ate)+'/'+ate.slice(0,4)+(ate===CARD.hoje?' (hoje)':' (filtro da camada)')+' · '+(e.cult||'sem cultura')},{l:'Atualização',t:carAtual()},
            {l:'Prazo usado',t:'maior carência do produto na cultura · alvo não registrado na O.S.'}];
  e.apl.slice().sort(carOrdFim).forEach(r=>{ const at=!!(r.fim&&r.fim>ate);
    const area=r.parc?carNum(r.ha)+' ha em '+r.parc:(r.faixa?carNum(r.ha)+' de '+carNum(T.ha)+' ha · faixa não registrada: vale o talhão todo':carNum(r.ha)+' ha · talhão todo');
    const pz=r.na?'carência não se aplica':(r.dias===null?'carência desconhecida':r.dias+' dias · '+(r.conf?'bula conferida':'provisório'));
    items.push({t:r.p+' · '+r.os+' · '+carBr(r.d),sub:area,
      ch:[CH(r.fim?(at?'até '+carAte(r.fim):'cumprida em '+carBr(r.fim)):'sem prazo',r.fim?(at?'red':'blue'):'yellow'),CH(pz,(r.na||(r.dias!==null&&r.conf))?'gray':'yellow')]
        .concat(r.sinc?[]:[CH('no aparelho · aguardando sinal','yellow')]).concat(at&&e.det===r?[CH('determina o prazo','gray')]:[]),
      acts:[A('Abrir '+r.os,{h:'OS.dc.html#'+r.os,ic:'doc',tt:'Abrir a ordem com os apontamentos da aplicação'})]}); });
  e.pend.forEach(p=>items.push({t:p.t,sub:'Quem resolve: '+(p.q||CARD.quem.ag),ch:[CH('pendente','yellow')],acts:p.os?[A('Abrir '+p.os,{h:'OS.dc.html#'+p.os,ic:'doc'})]:[]}));
  e.prev.forEach(p=>items.push({t:'Previsto, não conta: '+p.os+' · '+p.ps.join(', '),sub:'janela '+p.jan+(p.fimPrev?' · se aplicada em '+carBr(p.ini)+', colheita impedida até '+carAte(p.fimPrev):''),ch:[CH(p.etapa,'gray')],acts:[]}));
  carLotesTal(t).slice(0,4).forEach((lt,i)=>{ const a=carAvaliar(c,lt.id); const x=a.motivos[0]||a.faltas[0]; const nm=a.motivos.length, nf=a.faltas.length;
    items.push({cap:i?'':'Lotes desta parcela · avaliação por destino',t:'Lote '+lt.id+' · '+(lt.tipo==='campo'?'colhido em '+carBr(lt.d):(lt.tipo==='mistura'?'mistura de ':'divisão de ')+lt.pais.join(' + ')),
      sub:x?((nm?nm+(nm>1?' impedimentos':' impedimento'):nf+(nf>1?' pendências':' pendência'))+' · resolve: '+x.q):(a.st==='conforme'?'só neste destino e escopo':''),
      ch:[CH(a.rot,a.cor)],acts:[A(a.acao,{h:'CO-06.dc.html#'+lt.id,ic:'check',tt:'Abrir a avaliação do lote para o destino'})]}); });
  const hdst='border-left:4px solid '+((M.lcop[CARCOR[e.k]]||M.lcop.none)[0])+';background:#F7F9F7;border-radius:8px;padding:7px 10px;display:flex;flex-direction:column;gap:2px;';
  const hd=sc?'Sem lavoura em colheita':({curso:'Colheita impedida até '+carAte(e.det&&e.det.fim)+(e.parcial?' em '+e.parcs.join(', '):'')+' · '+(e.det?e.det.p+' ('+e.det.os+')':''),
    insuf:'Prazo não confirmado · '+(CARPK[(e.pend[0]||{}).k]||'conferir'),cumprida:'Prazo cumprido em '+carBr(e.det&&e.det.fim)+' · venda depende da avaliação do lote',
    sem:'Nenhuma aplicação de defensivo apontada até '+carBr(ate)})[e.k];
  return SEC(self,l,'car',CAR_L,sc?'sem lavoura em colheita':carRot(e),{hd,hdc:'Situação em '+carBr(ate),hdst,kv,items,
    note:sc?'':'Prazo cumprido não é conformidade: o resíduo se avalia por lote e destino.',lk:'CO-06.dc.html',lkt:'Abrir qualidade dos lotes'}); }
function carAc(t,f){ if(semCultura(t)) return null; const e=carEst(t,f); const c=carCen();
  const hb=Object.keys(c.ordens||{}).map(k=>c.ordens[k]).find(o=>carEhColheita(o)&&(o.etapa==='A liberar'||o.etapa==='Liberadas')&&carTals(o.talhao).some(x=>x.tid===t)&&carBloqColheita(c,o,'liberar'));
  if(hb){ const b=carBloqColheita(c,hb,'liberar'); return b.fim?['Rever programação',{h:'OS.dc.html#'+hb.id,tt:'Colheita '+hb.id+' impedida pela carência: reprogramar na O.S.'}]:['Ver pendência',{h:'OS.dc.html#'+hb.id,tt:b.t}]; }
  if(e.k==='curso') return ['Ver restrição',{h:'OS.dc.html#'+e.det.os,tt:'Abrir a aplicação que determina o prazo ('+e.det.os+')'}];
  if(e.k==='insuf'){ const p=e.pend[0]; return (p.k==='regra'||p.k==='bula')?['Ver pendência',{h:'OS.dc.html#'+p.os,tt:'Conferir a carência na bula e registrar na '+p.os}]:['Conferir aplicação',{h:'OS.dc.html#'+p.os,tt:p.t}]; }
  if(e.k==='cumprida'){ const ls=carLotesTal(t); return ls.length?['Ver avaliação do destino',{h:'CO-06.dc.html#'+ls[0].id,tt:'Avaliação do lote mais recente para o destino'}]:null; }
  return null; }
// link de outra tela: #car:PV23 abre a camada com o talhão selecionado, na fazenda dele; #car só troca a camada (contexto preservado)
function carHash(self){ if(!self.__carhl){ self.__carhl=1; try{ window.addEventListener('hashchange',()=>{ self.__carh=0; self.setState({carhs:Date.now()}); }); }catch(e){} }
  if(self.__carh) return; self.__carh=1; let h=''; try{ h=decodeURIComponent(location.hash||''); }catch(e){} const m=/^#car(?::(\w+))?$/.exec(h); if(!m) return; const tid=(m[1]&&CARD.tal[m[1]])?m[1]:'';
  setTimeout(()=>{ self.setState(tid?{mf_faz:CARD.tal[tid].faz,lay:CAR_L,tsel:[tid],px:null,mpa:null,cvis:false}:{lay:CAR_L,cvis:false}); try{ history.replaceState(null,'',location.pathname+location.search); }catch(e){} },0); }
'''

# ---- camada Análises de solo (13/10/2026, proprietário: "coloque analises de solo como uma das opcoes do menu do mapa") ----
# Os laudos do AG-02 (SOLO0 de dados_solo.py + c.solo do cenário) lidos pelas funções de solo.js (soloLaudos, soloLeituraTal, soloUsoNoPlano):
# nenhuma conta nem regra própria aqui (ENG-011). Talhão sem laudo de solo = "sem análise" (ausente não é zero; vale a dose do plano).
MAP_JS += r'''
const SOLO_L='Análises de solo';
const SOLOCOR={corrigir:'orange',dia:'ok',validar:'yellow',vencida:'gray',sem:'none'};
let SOLOC={c:null,ls:[],m:{}};
function soloMapLs(){ const c=MAPC||cenGet(); if(SOLOC.c!==c) SOLOC={c,ls:soloLaudos(c,SOLO0),m:{}}; return SOLOC; }   // uma leitura por desenho
function soloLeit(t){ const S=soloMapLs(); if(S.m[t]) return S.m[t]; const ft=M.soloTal[t];
  return (S.m[t]=ft?soloLeituraTal(S.ls,SOLO0,ft[0],ft[1]):{k:'sem',l:null,sub:null,outros:[],cu:null,V:null,V2:undefined,abaixo:null}); }
function soloPct(v){ return prFmtT(v,1)+' %'; }
// ===== mapa de calor do solo (15/10/2026, proprietário: "cada indicador da análise de solo escolhido tem que gerar esse mapa de calor das manchas
// boas e ruins por todo o talhão com contraste"; "escolher as camadas de solo disponíveis no laudo, selecionar o laudo, e qual indicador"):
// os pontos georreferenciados do laudo (dados_solo.pontos) viram valor em cada célula do talhão pelo inverso do quadrado da distância; o índice
// calculado (V, CTC, SB, m) usa o soloIdx de solo.js no próprio ponto (ENG-011). Cores: Absoluto = classes da tabela demonstrativa (d '+': do
// vermelho ao verde; '-': ao contrário; textura: tons de terra); Talhão = sextos do talhão; Fazenda = P2–P98 da fazenda em 6 faixas.
const SOLO_IND={}; (SOLO0.ind||[]).forEach(i=>{ SOLO_IND[i.l]=i; });
const SOLOPAL={'+':['#E4002B','#FF6A00','#FFD500','#B5E61D','#3FBF2A','#0B7A1E'],'0':['#F3E3C3','#E0C38E','#C79A5B','#A0703A','#7A4E22','#523312']};
let SOLOST={}, SOLOG={k:'',g:null};
function soloPal(d,n){ const b=SOLOPAL[d==='0'?'0':'+']; const ix=n>=6?[0,1,2,3,4,5]:(n===5?[0,1,2,4,5]:(n===4?[0,2,4,5]:[0,2,5])); const c=ix.map(i=>b[i]); return d==='-'?c.reverse():c; }
function soloK(v,cs){ let k=0; while(k<cs.length&&v>=Number(cs[k])) k++; return k; }
function soloFmt(v,ind){ return nfx(v,ind.dec)+(ind.un==='%'?' %':(ind.un==='CaCl₂'?'':' '+ind.un)); }
function soloRuim(ind,v){ const k=soloK(v,ind.cortes), n=ind.cortes.length+1; if(ind.d==='+') return k<=(n>=5?1:0); if(ind.d==='-') return k>=n-2; return false; }
function soloChipSt(hx){ const c=[1,3,5].map(i=>parseInt(hx.slice(i,i+2),16)); const esc=(0.299*c[0]+0.587*c[1]+0.114*c[2])<150; return 'background:'+hx+';color:'+(esc?'#FFFFFF':'#15201A')+';border:1px solid rgba(21,32,26,.15);'; }
function soloLsCam(prof){ const pr=String(prof||'0–20 cm').replace(' cm',''); const fz=FAZ==='Lagoa Grande'?'Lagoa Grande':'Santa Rita';
  return soloMapLs().ls.filter(l=>l.tipo==='solo'&&l.prof===pr&&l.faz===fz&&l.sit!=='Substituído'); }
function soloTalDe(id){ const l=soloMapLs().ls.find(x=>x.id===id); if(!l) return ''; return TIDS().find(t=>{ const ft=M.soloTal[t]; return ft&&ft[0]===l.faz&&ft[1]===l.tal; })||''; }
function soloFopts(gs){ const ls=soloLsCam(SOLOST.prof); const has=(i)=>ls.some(l=>soloIndVal(l,i)!==null);
  const inds=(SOLO0.ind||[]).filter(has).map(i=>i.l); const lau=['Mais recente'].concat(ls.slice().sort((a,b)=>String(a.tal).localeCompare(String(b.tal),'pt-BR',{numeric:true})).map(l=>l.id));
  const tl={}; ls.forEach(l=>{ tl[l.id]=l.id+' · '+l.tal+' · '+soloBr(l.coleta)+(l.sit==='Validado'?'':' · '+l.sit.toLowerCase()); });
  return gs.map(g=>g.k==='lau'?Object.assign({},g,{o:lau,sel:true,t:tl}):(g.k==='ind'?Object.assign({},g,{o:inds.length?inds:['V %'],sel:true}):g)); }
function soloLaudoT(t,f){ const ft=M.soloTal[t]; if(!ft) return null; const ls=soloLsCam(f.prof).filter(l=>l.tal===ft[1]);
  if(f.lau&&f.lau!=='Mais recente') return ls.find(l=>l.id===f.lau)||null;
  return ls.slice().sort((a,b)=>((b.sit==='Validado')-(a.sit==='Validado'))||String(b.coleta).localeCompare(String(a.coleta)))[0]||null; }
function soloXY(t,u,v){ const g=M.geoc[t]; if(!g) return null; if(g[0]==='circ'){ const a=g[1].split(',').map(Number); return [a[0]+(2*u-1)*a[2],a[1]+(2*v-1)*a[2]]; }
  const p=g[1].split(' ').map(z=>z.split(',').map(Number)); const bl=(i)=>(1-u)*(1-v)*p[0][i]+u*(1-v)*p[1][i]+u*v*p[2][i]+(1-u)*v*p[3][i]; return [bl(0),bl(1)]; }
function soloIdw(xs,ys,vs,x,y){ let a=0,b=0; for(let i=0;i<xs.length;i++){ const d2=(xs[i]-x)*(xs[i]-x)+(ys[i]-y)*(ys[i]-y); if(d2<1e-6) return vs[i]; a+=vs[i]/d2; b+=1/d2; } return a/b; }
function lgPvPix(){ if(LGI.pvp) return LGI.pvp; const P=LGI.px; const o={}; for(let i=0;i<P.dono.length;i++){ const t=M.lg.ids[P.dono[i]]; if(t) (o[t]=o[t]||[]).push(i); }
  const g={}; Object.keys(o).forEach(t=>{ const ix=o[t]; let r=0,c=0; ix.forEach(i=>{ r+=P.pix[2*i]; c+=P.pix[2*i+1]; }); g[t]={ix,r:r/ix.length,c:c/ix.length,rad:Math.sqrt(ix.length/Math.PI)}; }); return (LGI.pvp=g); }
function soloGrade(f){ const ind=SOLO_IND[f.ind]; const k=[FAZ,f.prof,f.lau,f.ind,(soloMapLs().c||{}).rev||0,LGI.px?1:0].join('|'); if(SOLOG.k===k) return SOLOG.g; const g={};
  if(ind) TIDS().forEach(t=>{ const L=soloLaudoT(t,f); if(!L) return; const pts=(L.pts||[]).map(p=>({id:p.id,u:p.u,v:p.v,val:soloIndPt(L,ind,p)})).filter(p=>p.val!==null&&isFinite(p.val));
    const o={L,ind,vl:soloIndVal(L,ind),pts,vals:[],ha:M.tal[t].ha};
    if(pts.length>=3){ const vs=pts.map(p=>p.val);
      if(isLG(t)){ const G=LGI.px?lgPvPix()[t]:null; if(G){ pts.forEach(p=>{ p.x=G.c+(2*p.u-1)*G.rad; p.y=G.r+(2*p.v-1)*G.rad; p.ll=lgLL(p.y+.5,p.x+.5); });
          const xs=pts.map(p=>p.x), ys=pts.map(p=>p.y); o.ix=G.ix; o.vals=G.ix.map(i=>soloIdw(xs,ys,vs,LGI.px.pix[2*i+1],LGI.px.pix[2*i])); } }
      else if(M.px[t]){ pts.forEach(p=>{ const q=soloXY(t,p.u,p.v); p.x=q[0]; p.y=q[1]; p.lt=pxCoord([q[0]-M.cs/2,q[1]-M.cs/2]); }); const xs=pts.map(p=>p.x), ys=pts.map(p=>p.y); o.vals=M.px[t].map(c=>soloIdw(xs,ys,vs,c[0]+M.cs/2,c[1]+M.cs/2)); } }
    g[t]=o; });
  SOLOG={k,g}; return g; }
function soloLims(f,t,G){ const pega=(o)=>o.vals.length?o.vals:o.pts.map(p=>p.val);
  const vals=t?pega(G[t]):[].concat(...Object.keys(G).filter(x=>inF(x)).map(x=>pega(G[x]))); const s=vals.slice().sort((a,b)=>a-b); if(!s.length) return [0,0,0,0,0];
  const q=(p)=>s[Math.round(p*(s.length-1))]; if(t) return [1,2,3,4,5].map(i=>q(i/6)); const lo=q(.02),hi=q(.98),st=(hi-lo)/6||1e-6; return [1,2,3,4,5].map(i=>lo+st*i); }
function soloCor(f,ind,v,L){ if(f.ctr==='Absoluto'){ const n=ind.cortes.length+1; return soloPal(ind.d,n)[soloK(v,ind.cortes)]; } return soloPal(ind.d,6)[soloK(v,L)]; }
function soloCls(t,f){ const G=soloGrade(f); const o=G[t]; const ind=SOLO_IND[f.ind]||{l:f.ind};
  if(!o){ const ft=M.soloTal[t]; const tem=ft&&soloMapLs().ls.some(l=>l.tipo==='solo'&&l.faz===ft[0]&&l.tal===ft[1]);
    return {c:'none',l:(f.lau&&f.lau!=='Mais recente')?'fora do laudo escolhido':(tem?'sem laudo '+f.prof:'sem análise')}; }
  if(o.vl===null) return {c:'gray',l:ind.l+' não calculável'};
  const kk=soloK(o.vl,ind.cortes); const hx=soloPal(ind.d,ind.cortes.length+1)[kk];
  return {c:'sat',solo:true,hex:hx,l:ind.l+' '+soloFmt(o.vl,ind)+(o.L.sit==='Validado'?'':' · a validar')+(o.pts.length?'':' · sem pontos')}; }
function soloLegend(f){ const ind=SOLO_IND[f.ind]; if(!ind) return [];
  if(f.ctr==='Absoluto'){ const pal=soloPal(ind.d,ind.cortes.length+1); const c=ind.cortes.map(Number); const fx=(x)=>nfx(x,ind.dec);
    return ind.classes.map((nm,i)=>Lh(pal[i],nm+' '+(i===0?'< '+fx(c[0]):(i===c.length?'≥ '+fx(c[c.length-1]):fx(c[i-1])+'–'+fx(c[i]))))).concat([Lc(SOLO_L,'none','sem laudo na camada')]); }
  const pal=soloPal(ind.d,6); const nm=ind.d==='0'?['menor','','','','','maior']:(ind.d==='-'?['menor (melhor)','','','','','maior (pior)']:['menor (pior)','','','','','maior (melhor)']);
  return pal.map((h,i)=>Lh(h,nm[i])).concat([{t:(f.ctr==='Talhão'?'sextos de cada talhão':'escala da fazenda')+' · '+ind.l+' '+ind.un,st:'font-weight:700;',dot:'display:none;'},Lc(SOLO_L,'none','sem laudo na camada')]); }
function soloStrip(f){ const N=(k,val,d)=>({k,val,d:d||''}); const G=soloGrade(f); const ind=SOLO_IND[f.ind]; if(!ind) return [];
  const ts=Object.keys(G).filter(t=>inF(t)); let haR=0, ha=0, sm=0, sw=0, np=0;
  ts.forEach(t=>{ const o=G[t]; np+=o.pts.length; if(o.vl!==null){ sm+=o.vl*o.ha; sw+=o.ha; } const vs=o.vals.length?o.vals:o.pts.map(p=>p.val); if(!vs.length) return;
    haR+=vs.filter(v=>soloRuim(ind,v)).length/vs.length*o.ha; ha+=o.ha; });
  return [N('Laudos',ts.length,'Talhões com laudo na camada '+f.prof),N('Pontos',np,'Pontos georreferenciados da amostragem'),N(ind.l,sw?soloFmt(sm/sw,ind):'—','Média ponderada pela área')]
    .concat(ind.d==='0'?[]:[N('Manchas ruins',nfx(haR,0)+' ha'+(ha?' · '+nfx(100*haR/ha,0)+' %':''),'Área nas classes ruins da tabela demonstrativa')]); }
// painel do talhão: laudo, coleta, situação, uso no plano e 3 atributos-chave com a faixa; os outros laudos do talhão só como linha
function soloSec(self,t){ const x=soloLeit(t); const l=x.l; const R=SOLO0.regra; const kv=[], items=[];
  const lin=(q)=>({t:q.id+' · '+(q.tipo==='folha'?'foliar':q.prof+' cm'),sub:'coleta '+soloBr(q.coleta)+' · '+q.lab+(q.motivo?' · '+q.motivo:''),ch:[CH(q.sit,SOLO_SITC[q.sit]||'gray')],
    acts:[A('Abrir '+q.id,{h:'AG-02.dc.html#'+q.id,ic:'frasco',tt:'Abrir o laudo em Análises de solo'})]});
  if(!l) return SEC(self,SOLO_L,'solo','Análises de solo','sem análise de solo',{items:x.outros.map(lin),note:'Sem laudo de solo neste talhão: vale a dose do plano.'});
  const ix=l.idx||{};
  kv.push({l:'Laudo',t:l.id+' · '+l.prof+' cm'+(l.zona?' · por zona':'')});
  kv.push({l:'Coleta',t:soloBr(l.coleta)+' · '+l.lab});
  kv.push({l:'Situação',t:l.sit+(l.motivo?' · '+l.motivo:'')+(l.sit==='Validado'?' · vale até '+soloBr(l.val):'')});
  if(l.sit==='Validado') kv.push({l:'No plano',t:soloNoPlano(l,soloUsoNoPlano(soloMapLs().c,SOLO0,l)).t});
  if(ix.V){ const V=ix.V; const cmp=x.abaixo===null?null:x.abaixo;
    items.push({t:'V '+(V.v===null?'não calculável':soloPct(V.v)),sub:V.v===null?V.nc:(x.V2!==undefined?'meta '+x.V2+' % · '+x.cu.cultura:'sem cultivo com meta na safra'),
      ch:cmp===null?[]:[cmp?CH('abaixo da meta','orange'):CH('na meta','green')],acts:[]}); }
  const K=soloAn(l,'K'); if(K){ const km=soloKmg(K); const cl=(km.v!==null&&l.ext===R.k.ext)?soloClasseK(km.v,R):'';
    items.push({t:'K '+(km.v===null?'— ('+km.nc+')':prFmtT(km.v,2)+' mg/dm³'),sub:l.ext+(cl?' · classes '+R.k.cortes.join(' / ')+' mg/dm³':' · sem classe da regra para este extrator'),
      ch:cl?[CH(cl,{baixo:'orange','médio':'yellow',adequado:'green',alto:'green'}[cl]||'gray')]:[],acts:[]}); }
  if(ix.T) items.push({t:'CTC '+(ix.T.v===null?'não calculável':prFmt(ix.T.v,2)+' cmolc/dm³'),sub:ix.T.v===null?ix.T.nc:'',ch:[],acts:[]});
  { const f=flt(self,SOLO_L); const o=soloGrade(f)[t]; const ind=SOLO_IND[f.ind];
    if(o&&ind&&o.pts.length){ const vs=o.vals.length?o.vals:o.pts.map(p=>p.val); const pv=o.pts.map(p=>p.val); const n=ind.cortes.length+1; const pal=soloPal(ind.d,n);
      kv.push({l:'Mapa de calor',t:ind.l+' · '+o.L.id+' · '+o.pts.length+' pontos · '+soloFmt(Math.min.apply(null,pv),ind)+' a '+soloFmt(Math.max.apply(null,pv),ind)+' nos pontos'});
      ind.classes.forEach((nm,k)=>{ const fr=vs.filter(v=>soloK(v,ind.cortes)===k).length/vs.length; if(fr>0) items.push({t:nm+' · '+nfx(fr*o.ha,1)+' ha ('+nfx(100*fr,0)+' %)',sub:'área do talhão nesta classe ('+ind.l+')',ch:[CHs('■',soloChipSt(pal[k]))],acts:[]}); });
      o.pts.slice().sort((a,b)=>ind.d==='-'?b.val-a.val:a.val-b.val).slice(0,6).forEach(p=>items.push({t:'Ponto '+p.id+' · '+ind.l+' '+soloFmt(p.val,ind),sub:(p.ll?fmtLL(p.ll):(p.lt||'ponto da grade'))+' · '+ind.classes[soloK(p.val,ind.cortes)],ch:[],acts:[]}));
      if(o.pts.length>6) items.push({t:'+'+(o.pts.length-6)+' pontos no laudo',sub:'os 6 acima são os de pior '+ind.l,ch:[],acts:[A('Abrir '+o.L.id,{h:'AG-02.dc.html#'+o.L.id,ic:'frasco',tt:'Abrir o laudo em Análises de solo'})]}); } }
  if(x.sub) items.push(lin(x.sub)); x.outros.forEach(q=>items.push(lin(q)));
  return SEC(self,SOLO_L,'solo','Análises de solo',soloCls(t,flt(self,SOLO_L)).l,{kv,items}); }
// próximo passo (uma ação primária): o laudo aberto no AG-02; sem laudo (ou vencido), Registrar laudo com fazenda e talhão já escolhidos
function soloAc(t){ const x=soloLeit(t); const ft=M.soloTal[t]||['',t];
  if(!x.l||x.k==='vencida') return A('Registrar laudo',{h:'AG-02.dc.html#registrar='+encodeURIComponent(ft[0]+'/'+ft[1]),ic:'frasco',prim:true,tt:'Abrir Análises de solo com '+ft[1]+' no formulário'});
  const v=x.l.sit==='Aguardando validação'?'Validar laudo':(x.l.sit==='Inconsistente'?'Corrigir laudo':'Abrir laudo');
  return A(v,{h:'AG-02.dc.html#'+x.l.id,ic:'frasco',prim:true,tt:'Abrir o '+x.l.id+' em Análises de solo'}); }
/* ---------- Colheita (14/10/2026, proprietário: "veja se tem algum submenu/funcionalidade em agrícola importante que ainda não tem ícone e
   funcionalidade no mapa e adicione. O mapa é um modo de visão geográfico dos dados de tudo que acontece na fazenda") ----------
   A mesma leitura da tela Previsão e colheita (COLH): prTal (situação, previsão, produção recebida e próximo passo) e prPrevTxt, em producao.js.
   Talhão = cultivos em produção (k.prod) da fazenda naquele local (Santa Rita: T1 junta T1-A e T1-B). Sem cultivo em produção: "sem colheita". */
const COLH_L='Colheita';
const COLHCOR={'Em colheita':'ok','Programada':'blue','Prevista':'gray','Colhida':'navy','Sem previsão':'yellow'};
let COLHC={c:null,m:{}};
function colhMap(){ const c=MAPC||cenGet(); if(COLHC.c!==c||COLHC.s!==SAF) COLHC={c,s:SAF,m:{}}; return COLHC; }   // uma leitura por desenho
function colhCults(t){ const ft=M.soloTal[t]; if(!ft) return []; return Object.keys(PRDC.cult).filter(id=>{ const k=PRDC.cult[id];
  return k.prod&&k.faz===ft[0]&&(safCur()||!k.saf||((PRDC.safras[k.saf]||{}).mf||SAF)===SAF)&&(k.local===ft[1]||String(k.local).indexOf(ft[1]+'-')===0); }); }
function colhLeit(t){ const S=colhMap(); if(S.m[t]) return S.m[t];
  const xs=colhCults(t).map(id=>prTal(S.c,id)).sort((a,b)=>(PR_SITORD[a.sit]-PR_SITORD[b.sit])||String(a.k.local).localeCompare(String(b.k.local),'pt-BR',{numeric:true}));
  return (S.m[t]={xs,x:xs[0]||null,c:S.c}); }
function colhNum(L,x){ return x.R.comecou?prProdTxt(x.k.cultura,x.R):(x.sit==='Prevista'?prPrevTxt(L.c,x).t.split(' · ')[0]:''); }
function colhCls(t){ const L=colhLeit(t); const x=L.x; if(!x) return {c:'none',l:'sem colheita'}; const n=colhNum(L,x);
  return {c:COLHCOR[x.sit]||'gray',l:x.sit.toLowerCase()+(n?' · '+n:'')+(L.xs.length>1?' · +'+(L.xs.length-1):'')}; }
function colhLegend(){ return Object.keys(COLHCOR).map(k=>Lc(COLH_L,COLHCOR[k],k.toLowerCase())).concat([Lc(COLH_L,'none','sem colheita')]); }
function colhFonte(){ return 'Previsão e colheita: situação, previsão publicada, produção recebida e próximo passo de cada cultivo em produção · produtividade na unidade escolhida para a cultura'+(M.lg.rot&&FAZ==='Lagoa Grande'?' · '+M.lg.rot:''); }
function colhStrip(){ const N=(k,val,d)=>({k,val,d:d||''}); const xs=TIDS().map(t=>colhLeit(t).x); const n=(s)=>xs.filter(x=>x&&x.sit===s).length;
  const rec=TIDS().reduce((a,t)=>a+colhLeit(t).xs.reduce((q,x)=>q+x.R.aPesar.length,0),0);
  return [N('Em colheita',n('Em colheita'),'Talhões em colheita'),N('Programada',n('Programada'),'Talhões com colheita programada'),N('Prevista',n('Prevista'),'Talhões com previsão publicada'),
    N('Sem previsão',n('Sem previsão'),'Talhões em produção sem previsão publicada'),N('Colhida',n('Colhida'),'Talhões com a colheita encerrada')].concat(rec?[N('A receber',rec,'Cargas colhidas a receber na balança')]:[]); }
function colhKv(L,x){ const k=x.k, R=x.R; const op=g2unidPref(k.cultura); const mt=k.meta?prUnpMeta(k.cultura,k.meta,k.un_meta,op):null; const kv=[];
  kv.push({l:'Previsão',t:prPrevTxt(L.c,x).t});
  kv.push({l:'Colhido',t:prProdTxt(k.cultura,R)+(R.comecou?' · '+prFmtT(R.area,2)+' ha':'')});
  if(R.comecou) kv.push({l:'Produtividade',t:prPrtvResTxt(k.cultura,R,op)+(mt?' · meta '+mt.txt:'')}); else if(mt) kv.push({l:'Meta',t:mt.txt});
  if(R.aPesar.length) kv.push({l:'A receber',t:R.aPesar.length+(R.aPesar.length>1?' cargas na balança':' carga na balança')});
  kv.push({l:'Próximo passo',t:x.nx}); return kv; }
function colhSec(self,t){ const L=colhLeit(t); const x=L.x;
  if(!x) return SEC(self,COLH_L,'colh','Colheita','sem colheita',{note:'Sem cultivo em produção neste talhão.'});
  const nome=(y)=>y.k.local+' · '+y.k.cultura+(y.k.var?' '+y.k.var:'')+' · '+((PRDC.safras[y.k.saf]||{}).nome||y.k.saf);
  const items=L.xs.slice(1).map(y=>({t:nome(y),sub:prPrevTxt(L.c,y).t+' · colhido '+prProdTxt(y.k.cultura,y.R),ch:[CH(y.sit,CCH[COLHCOR[y.sit]]||'gray')],acts:[]}));
  return SEC(self,COLH_L,'colh','Colheita',x.sit.toLowerCase(),{kv:[{l:'Cultivo',t:nome(x)}].concat(colhKv(L,x)),items,lk:'COLH.dc.html#'+x.k.id,lkt:'Abrir na Previsão e colheita'}); }
function colhAc(t){ const L=colhLeit(t); const x=L.x; if(!x) return A('Abrir Previsão e colheita',{h:'COLH.dc.html',ic:'Colheita',tt:'Sem cultivo em produção neste talhão'});
  const ac=x.ac; if(ac) return A(ac.t,{h:ac.h||('COLH.dc.html#'+x.k.id),ic:'Colheita',prim:true,tt:ac.x.charAt(0).toUpperCase()+ac.x.slice(1)+' · '+ac.q});
  return A('Abrir na Previsão e colheita',{h:'COLH.dc.html#'+x.k.id,ic:'Colheita',prim:true,tt:x.nx}); }
'''

_LBL=('font-family: Manrope, sans-serif; font-size: 15px; font-weight: 800; color: #15201A; text-align: center; line-height: 1.2; '
      'text-shadow: 0 0 3px #fff, 0 0 3px #fff, 0 0 3px #fff, 0 0 5px #fff;')
_SUB=('font-family: Manrope, sans-serif; font-size: 13px; font-weight: 700; color: #15201A; text-align: center; line-height: 1.2; opacity: .85; '
      'text-shadow: 0 0 3px #fff, 0 0 3px #fff, 0 0 4px #fff;')
def _mapsvg(defs=True):
    interactive=True
    g=[]
    for tid,tp,geo in GEO:
        ev=f' onClick="{H("tk_"+tid)}" onKeyDown="{H("tkk_"+tid)}" tabIndex="0" role="button" aria-label="{H("al_"+tid)}" style="cursor: pointer;"' if interactive else ''
        at=f'fill="{H("fl_"+tid)}" fill-opacity="{H("fo_"+tid)}" stroke="{H("sk_"+tid)}" stroke-width="{H("sw_"+tid)}" stroke-linejoin="round"'
        if tp=='poly':
            pts=[tuple(map(float,p.split(','))) for p in geo.split()]
            cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
            g.append(f'<polygon points="{geo}" {at}{ev}/>')
            g.append(_cel(tid))
        else:
            cx,cy,r=map(float,geo.split(','))
            g.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" {at}{ev}/>')
            g.append(_cel(tid))
            g.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+r*0.7:.0f}" y2="{cy-r*0.7:.0f}" stroke="{H("sk_"+tid)}" stroke-width="2" style="pointer-events: none;"/>')
        if tid=='T7':
            g.append(f'<circle cx="650" cy="556" r="{H("mr_T7")}" fill="none" stroke="#15201A" stroke-width="2.5" stroke-dasharray="6 4" opacity="{H("mo_T7")}" style="pointer-events: none;"/>'
                     f'<foreignObject x="692" y="524" width="90" height="22" opacity="{H("mo_T7")}" style="pointer-events: none;"><div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; font-family: Manrope, sans-serif; font-size: 11.5px; font-weight: 800; color: #fff; background: #15201A; border-radius: 6px; padding: 1px 6px; line-height: 18px;">mancha {H("ml_T7")}</div></foreignObject>')
        g.append(f'<text x="{cx:.0f}" y="{cy+4:.0f}" text-anchor="middle" font-family="Sora, Manrope, sans-serif" font-size="40" font-weight="700" fill="#15201A" stroke="#fff" stroke-width="6" paint-order="stroke" style="pointer-events: none;">{tid}</text>')
        lw=min(260,int(max(p[0] for p in pts)-min(p[0] for p in pts))-16) if tp=='poly' else int(2*r-24)  # rótulo cabe no talhão (quebra em 2 linhas)
        g.append(f'<foreignObject x="{cx-lw/2:.0f}" y="{cy+12:.0f}" width="{lw}" height="20" style="pointer-events: none;"><div xmlns="http://www.w3.org/1999/xhtml" style="{_SUB}">{H("sub_"+tid)}</div></foreignObject>')
        g.append(f'<foreignObject x="{cx-lw/2:.0f}" y="{cy+32:.0f}" width="{lw}" height="46" style="pointer-events: none;"><div xmlns="http://www.w3.org/1999/xhtml" style="{_LBL}">{H("lab_"+tid)}</div></foreignObject>')
    clips=''.join((f'<clipPath id="cp_{t}"><polygon points="{geo}"/></clipPath>' if tp=='poly' else f'<clipPath id="cp_{t}"><circle cx="{geo.split(",")[0]}" cy="{geo.split(",")[1]}" r="{geo.split(",")[2]}"/></clipPath>') for t,tp,geo in GEO if t in PX)
    defs=('<defs>'+clips+'<pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#C9CFCB"/>'
          '<line x1="0" y1="0" x2="0" y2="10" stroke="#9E9E9E" stroke-width="4"/></pattern>'
          '<pattern id="grade" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0 L0 0 0 40" fill="none" stroke="#D3DDCB" stroke-width="1"/></pattern></defs>') if defs else ''
    return (f'<svg viewBox="0 0 1000 620" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Mapa da fazenda Santa Rita" style="display: block;">'
            + defs + '<rect width="1000" height="620" fill="url(#grade)"/><path d="M0 314 C 250 308, 520 320, 1000 314" stroke="#FFFFFF" stroke-width="10" fill="none" opacity=".9"/>'
            + '<path d="M318 0 L322 620" stroke="#FFFFFF" stroke-width="7" fill="none" opacity=".8"/>' + ''.join(g)
            + f'<sc-for list="{H("solo_pts")}" as="q" hint-placeholder-count="2"><circle cx="{H("q.x")}" cy="{H("q.y")}" r="3.4" fill="#15201A" stroke="#FFFFFF" stroke-width="1.5" style="pointer-events: none;"/></sc-for>'
            + f'<rect x="{H("pxs_x")}" y="{H("pxs_y")}" width="{CS}" height="{CS}" fill="none" stroke="#15201A" stroke-width="3" opacity="{H("pxs_o")}" style="pointer-events: none;"/></svg>')
def _cel(tid):
    if tid not in PX: return ''
    return (f'<g clip-path="url(#cp_{tid})" opacity="{H("pxo_"+tid)}" style="pointer-events: none;">'
            + ''.join(f'<rect x="{c[0]}" y="{c[1]}" width="{CS}" height="{CS}" fill="{H("px_"+tid+"_"+str(i))}"/>' for i,c in enumerate(PX[tid])) + '</g>')

def _panel_html():
    ICS=['doc','alert','drop','leaf','map','trend','cash','lab','check','calendar','layers','box','cart','satelite','inseto','frasco']
    def actions(lst,a='a'):
        ic=''.join(f'<sc-if value="{H(a+".i_"+n)}" hint-placeholder-val="{F()}">{icon(n,14)}</sc-if>' for n in ICS)
        return (f'<sc-for list="{H(lst)}" as="{a}" hint-placeholder-count="2">'
                f'<sc-if value="{H(a+".isH")}" hint-placeholder-val="{T()}"><a href="{H(a+".h")}" title="{H(a+".tt")}" style="{H(a+".st")}">{ic}{H(a+".t")}</a></sc-if>'
                f'<sc-if value="{H(a+".isF")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H(a+".fn")}" title="{H(a+".tt")}" style="{H(a+".st")}">{ic}{H(a+".t")}</button></sc-if></sc-for>')
    cap=f'font-size: 10.5px; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; color: {MUTED};'
    chips=lambda lst,a: f'<div style="display: flex; flex-wrap: wrap; gap: 4px;"><sc-for list="{H(lst)}" as="{a}" hint-placeholder-count="1"><span style="{H(a+".st")}">{H(a+".t")}</span></sc-for></div>'
    inp=f'font-family: inherit; font-size: 13px; padding: 7px 10px; border: 1px solid {LINE}; border-radius: 9px; background: #fff; width: 100%; box-sizing: border-box;'
    lk=f'font-size: 12.5px; font-weight: 700; color: {INK}; text-decoration: underline; text-underline-offset: 3px; white-space: nowrap;'
    # ordens do talhão (cartões) e o próximo passo da escolhida
    os_html=(f'<sc-if value="{H("pan_hasost")}" hint-placeholder-val="{F()}"><div style="{cap} padding-top: 2px;">{H("pan_ost")}</div></sc-if>'
      f'<sc-if value="{H("pan_hasos")}" hint-placeholder-val="{F()}"><div role="radiogroup" aria-label="Ordens do talhão" style="display: flex; flex-direction: column; gap: 6px;">'
      f'<sc-for list="{H("pan.os")}" as="o" hint-placeholder-count="2"><button type="button" role="radio" aria-checked="{H("o.on")}" onClick="{H("o.go")}" style="{H("o.st")}">'
      f'<span style="font-size: 13px; font-weight: 700; line-height: 1.3;">{H("o.t")}</span>{chips("o.ch","c")}<span style="font-size: 12px; color: {MUTED}; line-height: 1.35;">{H("o.sub")}</span></button></sc-for></div></sc-if>'
      f'<sc-if value="{H("pan_hasnx")}" hint-placeholder-val="{F()}"><div role="region" aria-label="Próximo passo" style="{H("nx.st")}">'
      f'<div style="{cap}">Próximo passo · {H("nx.id")}</div><div style="font-size: 13px; line-height: 1.45;">{H("nx.t")}</div>'
      f'<sc-if value="{H("nx.hasIns")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; font-weight: 700; line-height: 1.4;">{H("nx.ins")}</div></sc-if>'
      f'<sc-if value="{H("nx.bloq")}" hint-placeholder-val="{F()}"><div style="{H("nx.btst")}">{H("nx.bt")}</div><div style="font-size: 12.3px; color: {MUTED};">{H("nx.bq")}</div>'
      f'<sc-if value="{H("nx.hasBh")}" hint-placeholder-val="{F()}"><a href="{H("nx.bh")}" style="{H("nx.bst")}">{H("nx.bhl")}</a></sc-if></sc-if>'
      f'<sc-if value="{H("nx.hasDono")}" hint-placeholder-val="{F()}"><div style="font-size: 12.3px; color: {MUTED};">{H("nx.dono")}</div></sc-if>'
      f'<sc-if value="{H("nx.idle")}" hint-placeholder-val="{T()}"><div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px 12px;">'
      f'<sc-if value="{H("nx.isBtn")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("nx.go")}" style="{_MINIP}">{H("nx.btn")}</button></sc-if>'
      f'<sc-if value="{H("nx.hasLib")}" hint-placeholder-val="{F()}"><a href="{H("nx.libh")}" style="{H("nx.dst")}">{H("nx.libt")}</a></sc-if>'
      f'<sc-if value="{H("nx.hasOpen")}" hint-placeholder-val="{T()}"><a href="{H("nx.open")}" style="{lk}">Abrir ordem ›</a></sc-if></div></sc-if>'
      f'<sc-if value="{H("nx.conf")}" hint-placeholder-val="{F()}"><div style="font-size: 13px; font-weight: 600; line-height: 1.45;">{H("nx.ct")}</div>'
      f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("nx.yes")}" style="{_MINIP}">{H("nx.cbtn")}</button><button type="button" onClick="{H("nx.back")}" style="{_MINI}">Voltar</button></div></sc-if>'
      f'<sc-if value="{H("nx.ap")}" hint-placeholder-val="{F()}"><div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">'
      f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 700;">Data do turno<input type="date" value="{H("nx.ad")}" onChange="{H("nx.setad")}" style="{inp}"></label>'
      f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 700;">Área feita (ha)<input type="text" inputmode="decimal" aria-label="Área feita em hectares" value="{H("nx.aha")}" onChange="{H("nx.setaha")}" style="{inp}"></label></div>'
      f'<div style="font-size: 12px; color: {MUTED};">{H("nx.asub")}</div>'
      f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("nx.asave")}" style="{_MINIP}">Salvar apontamento</button><button type="button" onClick="{H("nx.back")}" style="{_MINI}">Voltar</button></div></sc-if>'
      f'<sc-if value="{H("nx.hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("nx.err")}</div></sc-if>'
      f'</div></sc-if>')
    # SEP-20261015 (proprietário, 15/10: menos linhas separadoras): pares rótulo → valor separados pelo espaço; o rodapé de ações (branco sobre
    # o painel cinza) e a barra da camada (sobre o mapa) ficam sem linha, porque a mudança de fundo já separa
    secs=(f'<sc-for list="{H("pan.secs")}" as="s" hint-placeholder-count="2"><section aria-label="{H("s.t")}" style="display: flex; flex-direction: column; gap: 6px;">'
      f'<div style="{cap} padding-top: 2px;">{H("s.t")}</div>'
      f'<sc-if value="{H("s.hasHd")}" hint-placeholder-val="{F()}"><div role="status" style="{H("s.hdst")}"><div style="{cap}">{H("s.hdc")}</div><div style="font-size: 13.5px; font-weight: 800; line-height: 1.35;">{H("s.hd")}</div></div></sc-if>'
      f'<sc-if value="{H("s.kvTop")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; border-top: 1px solid {LINE};"><sc-for list="{H("s.kv")}" as="k" hint-placeholder-count="3">'
      f'<div style="display: flex; gap: 10px; padding: 5px 0; border-bottom: 1px solid {LINE}; font-size: 12.5px;"><span style="width: 112px; flex-shrink: 0; color: {MUTED};">{H("k.l")}</span><b style="font-weight: 700; min-width: 0;">{H("k.t")}</b></div></sc-for></div></sc-if>'
      f'<sc-for list="{H("s.items")}" as="it" hint-placeholder-count="2"><sc-if value="{H("it.hasCap")}" hint-placeholder-val="{F()}"><div style="{cap} padding-top: 4px;">{H("it.cap")}</div></sc-if>'
      f'<div style="border: 1px solid {LINE}; border-radius: 10px; padding: 7px 9px; display: flex; flex-direction: column; gap: 4px; background: #fff; {H("it.bst")}">'
      f'<div style="font-size: 12.8px; font-weight: 700; line-height: 1.3;">{H("it.t")}</div>{chips("it.ch","c")}'
      f'<div style="font-size: 12px; color: {MUTED}; line-height: 1.35;">{H("it.sub")}</div><div style="display: flex; flex-wrap: wrap; gap: 6px;">'+actions('it.acts','ia')+'</div></div></sc-for>'
      f'<sc-if value="{H("s.kvBot")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; border-top: 1px solid {LINE};"><sc-for list="{H("s.kv")}" as="k" hint-placeholder-count="3">'
      f'<div style="display: flex; gap: 10px; padding: 5px 0; border-bottom: 1px solid {LINE}; font-size: 12.5px;"><span style="width: 112px; flex-shrink: 0; color: {MUTED};">{H("k.l")}</span><b style="font-weight: 700; min-width: 0;">{H("k.t")}</b></div></sc-for></div></sc-if>'
      f'<sc-if value="{H("s.hasNote")}" hint-placeholder-val="{F()}"><div style="font-size: 12.3px; color: {YEL}; background: {YELS}; border-radius: 10px; padding: 7px 9px; line-height: 1.4;">{H("s.note")}</div></sc-if>'
      f'<sc-if value="{H("s.hasLk")}" hint-placeholder-val="{F()}"><a href="{H("s.lk")}" style="{lk} align-self: flex-start;">{H("s.lkt")} ›</a></sc-if>'
      f'</section></sc-for>')
    return (f'<aside aria-label="{H("pan.title")}" style="width: 384px; flex-shrink: 0; border-left: 1px solid {LINE}; background: {BG}; display: flex; flex-direction: column; min-height: 0;">'
      f'<div style="display: flex; align-items: flex-start; gap: 8px; padding: 12px 14px 8px; background: {SURF}; border-bottom: 1px solid {LINE};"><div style="flex-grow: 1; min-width: 0;"><h2 style="margin: 0; font-family: {DISP}; font-size: 17px; font-weight: 700; letter-spacing: -.02em;">{H("pan.title")}</h2>'
      f'<div style="font-size: 12.3px; color: {MUTED}; margin-top: 2px;">{H("pan.sub")}</div><div style="margin-top: 6px;">{chips("pan.ch","c")}</div></div>'
      f'<button type="button" onClick="{H("pan_close")}" aria-label="Fechar painel" title="Fechar painel" style="border: 0; background: {BG}; width: 30px; height: 30px; border-radius: 999px; cursor: pointer; font-size: 17px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
      f'<div style="flex-grow: 1; min-height: 0; overflow-y: auto; padding: 10px 12px; display: flex; flex-direction: column; gap: 8px;">{os_html}{secs}</div>'
      f'<sc-if value="{H("pan_hasacts")}" hint-placeholder-val="{T()}"><div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 14px; background: {SURF};">{actions("pan.acts")}</div></sc-if></aside>')

def _mapcard(h,full=False):
    fgroups=(f'<sc-for list="{H("flt")}" as="g" hint-placeholder-count="2">'
             f'<sc-if value="{H("g.sel")}" hint-placeholder-val="{F()}"><label style="display: inline-flex; align-items: center; gap: 6px; font-size: 11.5px; font-weight: 700; color: {MUTED};">{H("g.l")}'
             f'<select aria-label="{H("g.l")}" value="{H("g.val")}" onChange="{H("g.set")}" style="font-family: inherit; font-size: 12px; font-weight: 700; padding: 4px 26px 4px 10px; min-height: 32px; max-width: 260px; border-radius: 999px; border: 1px solid {LINE}; background: {SURF}; color: {INK}; cursor: pointer;">'
             f'<sc-for list="{H("g.sopts")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label></sc-if>'
             f'<sc-if value="{H("g.seg")}" hint-placeholder-val="{T()}"><span style="display: inline-flex; align-items: center; gap: 6px;">'
             f'<span style="font-size: 11.5px; font-weight: 700; color: {MUTED};">{H("g.l")}</span>'
             f'<span role="group" aria-label="{H("g.l")}" style="display: inline-flex; gap: 2px; padding: 2px; border-radius: 9px; background: {GRAYS};"><sc-for list="{H("g.opts")}" as="o" hint-placeholder-count="3">'
             f'<button type="button" aria-pressed="{H("o.on")}" onClick="{H("o.go")}" title="{H("o.tt")}" style="{H("o.st")}">{H("o.t")}</button></sc-for></span></span></sc-if></sc-for>')
    fgroups+=(f'<sc-if value="{H("alv_on")}" hint-placeholder-val="{F()}"><span style="position: relative; display: inline-flex; align-items: center; gap: 6px;">'
             f'<span style="font-size: 11.5px; font-weight: 700; color: {MUTED};">Alvos</span>'
             f'<button type="button" data-alv="1" aria-haspopup="true" aria-expanded="{H("alv_exp")}" onClick="{H("alv_tog")}" title="Escolher os alvos: um, vários ou todos" '
             f'style="position: relative; font-family: inherit; font-size: 11.8px; font-weight: 700; padding: 4px 28px 4px 10px; min-height: 32px; border-radius: 999px; border: 1px solid {LINE}; background: {SURF}; color: {INK}; cursor: pointer; white-space: nowrap;">'
             f'{H("alv_t")}<span aria-hidden="true" style="position: absolute; right: 11px; top: 50%; transform: translateY(-50%); font-size: 10px;">▾</span></button>'
             f'<sc-if value="{H("alv_open")}" hint-placeholder-val="{F()}"><div role="menu" aria-label="Alvos" onKeyDown="{H("alv_key")}" style="position: absolute; top: calc(100% + 6px); left: 0; z-index: 40; min-width: 240px; '
             f'max-height: 340px; overflow-y: auto; background: {SURF}; border: 1px solid {LINE}; border-radius: 12px; box-shadow: 0 8px 24px rgba(21,32,26,.18); padding: 6px; display: flex; flex-direction: column; gap: 2px;">'
             f'<sc-for list="{H("alv_opts")}" as="o" hint-placeholder-count="4"><button type="button" role="menuitemcheckbox" aria-checked="{H("o.on")}" onClick="{H("o.go")}" style="{H("o.st")}">'
             f'<span aria-hidden="true" style="{H("o.bx")}">{H("o.ck")}</span>{H("o.t")}</button></sc-for></div></sc-if></span></sc-if>')
    nums=(f'<div role="group" aria-label="Indicadores de {H("lay_t")}" style="display: flex; gap: 14px; flex-wrap: wrap;"><sc-for list="{H("nums")}" as="n" hint-placeholder-count="4">'
          f'<span style="white-space: nowrap; font-size: 11.5px; color: {MUTED};">{H("n.k")} <b style="color: {INK}; font-size: 13.5px;">{H("n.val")}</b></span></sc-for></div>')
    tool=lambda ic,t,fn,st,tt: f'<button type="button" onClick="{H(fn)}" title="{tt}" aria-pressed="{H(st.replace("_st","_on"))}" style="{H(st)}">{icon(ic,15,INK)}{t}</button>'
    sq=lambda t,fn,lab: f'<button type="button" onClick="{H(fn)}" aria-label="{lab}" title="{lab}" style="width: 36px; height: 36px; border: 0; border-radius: 10px; background: #FFFFFF; box-shadow: 0 1px 4px rgba(21,32,26,.18); font-family: inherit; font-size: 18px; font-weight: 700; color: {INK}; cursor: pointer;">{t}</button>'
    zoom=(f'<div role="group" aria-label="Zoom" style="position: absolute; right: 12px; top: 96px; display: flex; flex-direction: column; gap: 6px;">'
          + sq('+','zin','Aproximar') + sq('−','zout','Afastar') + '</div>')
    tools=(f'<div role="toolbar" aria-label="Ferramentas do mapa" style="position: absolute; right: 12px; top: 10px; display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 6px; max-width: calc(100% - 290px);">'
           + tool('grid','Selecionar área','r_selm','r_selm_st','Selecionar vários talhões') + tool('trend','Medir','r_medir','r_medir_st','Medir área e perímetro')
           + f'<sc-if value="{H("tm_ok")}" hint-placeholder-val="{F()}">' + tool('map','Desenhar','r_des','r_des_st','Desenhar talhão: contorno de um talhão ou pivô')
           + tool('doc','Importar','r_imp','r_imp_st','Importar talhões de um arquivo KML (Google Earth) ou GeoJSON (QGIS)') + '</sc-if>'
           + (tool('map','Sair da tela cheia','r_full','r_full_st','Sair da tela cheia') if full else f'<sc-if value="{H("has_full")}" hint-placeholder-val="{T()}">'+tool('map','Tela cheia','r_full','r_full_st','Mapa em tela cheia')+'</sc-if>') + '</div>')
    alt=f'height: {h}px;' if h else 'min-height: 0; align-self: stretch;'
    caixa='' if not h else f'border: 1px solid {LINE}; border-radius: 16px;'   # embutido no bloco do mapa: sem borda própria
    return (f'<div style="{alt} min-width: 0; flex-grow: 1; display: flex; flex-direction: column; background: {SURF}; {caixa} overflow: hidden;">'
      f'<div style="display: flex; align-items: center; gap: 10px 16px; padding: 10px 12px 8px; flex-wrap: wrap;">'
      f'<b style="font-size: 14px; white-space: nowrap;">{H("lay_t")}</b>'
      f'<button type="button" class="g2-info" aria-label="Fonte e regra da camada" data-dica="{H("fonte")}" style="flex-shrink: 0; width: 24px; height: 24px; border-radius: 999px; '
      f'border: 1px solid {LINE}; background: {SURF}; color: {MUTED}; font-family: inherit; font-size: 13px; font-weight: 700; cursor: help; display: inline-flex; align-items: center; justify-content: center;">i</button>{fgroups}<span style="flex-grow: 1;"></span>{nums}'
      f'<sc-if value="{H("hasFlink")}" hint-placeholder-val="{F()}"><a href="{H("flink")}" style="{_MINI} text-decoration: none; white-space: nowrap;">{H("flinkt")} ›</a></sc-if>'
      f'<sc-if value="{H("hasFvis")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("r_vis")}" aria-pressed="{H("r_vis_on")}" title="Clique no talhão para programar a vistoria" style="{H("r_vis_st")}">{icon("alert",14,INK)}Programar vistoria</button></sc-if>'
      f'</div>'
      f'<div class="mapa-linha" style="flex-grow: 1; min-height: 0; display: flex;">'
      f'<sc-if value="{H("map_on")}" hint-placeholder-val="{T()}">'
      f'<div class="mapa-area" style="flex-grow: 1; min-width: 0; position: relative; background: #E3EADB; overflow: hidden;">'
      f'<sc-if value="{H("map_sr")}" hint-placeholder-val="{T()}"><div style="{H("zst")}">{_mapsvg(defs=not full)}</div></sc-if>'
      + ('' if full else f'<sc-if value="{H("map_lg")}" hint-placeholder-val="{F()}"><div id="mapa-real" aria-label="{("Mapa da Fazenda Lagoa Grande · "+_LGROT) if _LGROT else "Mapa real da Fazenda Lagoa Grande"}" style="position: absolute; inset: 0;"></div>'
         f'<sc-if value="{H("lg_err")}" hint-placeholder-val="{F()}"><div role="alert" style="position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%); padding: 10px 14px; border-radius: 10px; background: #fff; color: {RED}; font-size: 13px; font-weight: 700;">{H("lg_errt")}</div></sc-if></sc-if>')
      + f'{tools}{zoom}{_tm_barra()}'
      f'<sc-if value="{H("aviso_bv")}" hint-placeholder-val="{F()}"><span role="note" style="position: absolute; left: 12px; top: 50px; padding: 5px 10px; border-radius: 999px; background: {YELS}; color: {YEL}; font-size: 12px; font-weight: 700; box-shadow: 0 1px 3px rgba(21,32,26,.14);">Boa Vista sem geometria</span></sc-if>'
      f'<div style="position: absolute; left: 12px; bottom: 12px; right: 12px; display: flex; flex-wrap: wrap; align-items: center; gap: 4px 12px; padding: 8px 12px; border-radius: 10px; background: rgba(255,255,255,.94); box-shadow: 0 1px 4px rgba(21,32,26,.14); font-size: 11.5px; color: {MUTED};">'
      f'<sc-for list="{H("leg")}" as="x" hint-placeholder-count="5"><span style="{H("x.st")}"><span style="{H("x.dot")}"></span>{H("x.t")}</span></sc-for><span style="flex-grow: 1;"></span><span>{H("leg_nota")}</span></div>'
      f'<sc-if value="{H("has_modo")}" hint-placeholder-val="{F()}"><span role="status" style="position: absolute; left: 12px; top: 10px; padding: 5px 10px; border-radius: 999px; background: {INK}; color: #fff; font-size: 12px; font-weight: 700;">{H("modo")}</span></sc-if></div></sc-if>'
      f'<sc-if value="{H("map_vazio")}" hint-placeholder-val="{F()}"><section aria-label="Mapa da Boa Vista" style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; background: {BG};">'
      f'{icon("map",40,MUTED)}<b style="font-size: 16px;">Nenhum talhão desenhado na Boa Vista</b>'
      f'<a href="CD-01.dc.html" style="{_IST}{BTN_ST(True,True)}">{icon("map",15)}Cadastrar talhões</a></section></sc-if>'
      f'<sc-if value="{H("pan_open")}" hint-placeholder-val="{F()}">{_panel_html()}</sc-if><sc-if value="{H("tm_open")}" hint-placeholder-val="{F()}">{_tm_painel()}</sc-if></div>'
      f'</div>')
def _tm_barra():
    """barra do desenho sobre o mapa: forma, medida ao vivo, área do pivô e Desfazer · Cancelar · Concluir (talmapa.js)."""
    seg=(f'<span role="group" aria-label="Forma do talhão" style="display: inline-flex; padding: 2px; gap: 2px; border-radius: 999px; background: {BG}; border: 1px solid {LINE};">'
         f'<button type="button" aria-pressed="{H("tm_mpol_on")}" onClick="{H("tm_mpol")}" style="{H("tm_mpol_st")}">Polígono</button>'
         f'<button type="button" aria-pressed="{H("tm_mpiv_on")}" onClick="{H("tm_mpiv")}" style="{H("tm_mpiv_st")}">Pivô</button></span>')
    return (f'<sc-if value="{H("tm_dbar")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Desenho do talhão" style="position: absolute; left: 50%; bottom: 64px; transform: translateX(-50%); display: flex; align-items: center; gap: 10px; flex-wrap: wrap; justify-content: center; max-width: calc(100% - 24px); padding: 8px 12px; border-radius: 12px; background: #FFFFFF; box-shadow: 0 2px 10px rgba(21,32,26,.25);">'
      + seg + f'<span role="status" style="font-size: 12.5px; font-weight: 600;">{H("tm_dinfo")}</span>'
      f'<sc-if value="{H("tm_pivarea")}" hint-placeholder-val="{F()}"><label style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: {MUTED};">Área<input aria-label="Área do pivô em hectares" inputMode="decimal" value="{H("tm_pivha")}" onChange="{H("tm_setpivha")}" style="font-family: inherit; font-size: 13px; width: 70px; padding: 5px 8px; border-radius: 8px; border: 1px solid {LINE}; text-align: right;">ha</label></sc-if>'
      f'<button type="button" onClick="{H("tm_dundo")}" style="{_MINI}">Desfazer ponto</button><button type="button" onClick="{H("tm_dcancel")}" style="{_MINI}">Cancelar</button>'
      f'<button type="button" onClick="{H("tm_dok")}" style="{_MINIP}">Concluir</button></div></sc-if>')
def _tm_painel():
    """painel do desenho (salvar no cadastro), da importação (arquivo e destino de cada feição) e do talhão novo selecionado."""
    cap=f'font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;'
    lab=f'display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 700; color: {MUTED};'
    err=lambda k: f'<sc-if value="{H("tm_he_"+k)}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("tm_e_"+k)}</span></sc-if>'
    sel=lambda val,fn,lst,st,aria: (f'<select aria-label="{aria}" value="{H(val)}" onChange="{H(fn)}" style="{H(st)}"><sc-for list="{H(lst)}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>')
    form=(f'<sc-if value="{H("tm_form")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 12px;">'
      f'<label style="{lab}">Usar o desenho como'+sel('tm_alvo','tm_setalvo','tm_aopts','tm_st_sel','Usar o desenho como')+'</label>'
      f'<sc-if value="{H("tm_novo")}" hint-placeholder-val="{T()}"><label style="{lab}">Nome do talhão<input aria-label="Nome do talhão" value="{H("tm_nome")}" onChange="{H("tm_setnome")}" style="{H("tm_st_nome")}">{err("nome")}</label>'
      f'<label style="{lab}">Sistema'+sel('tm_sis','tm_setsis','tm_sopts','tm_st_sel','Sistema')+'</label></sc-if>'
      f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;"><div style="{lab}">Área do contorno<b style="font-size: 14px; color: {INK}; padding: 7px 0;">{H("tm_calc")}</b></div>'
      f'<label style="{lab}">Área cultivável (ha)<input aria-label="Área cultivável em hectares" inputMode="decimal" value="{H("tm_decl")}" onChange="{H("tm_setdecl")}" style="{H("tm_st_decl")}"></label></div>{err("decl")}'
      f'<sc-if value="{H("tm_temmot")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; color: {YEL}; background: {YELS}; padding: 7px 10px; border-radius: 8px; font-weight: 700;">{H("tm_dif")}</div>'
      f'<label style="{lab}">Motivo da diferença'+sel('tm_mot','tm_setmot','tm_mopts','tm_st_mot','Motivo da diferença')+f'{err("motivo")}</label></sc-if>'
      f'{err("geo")}</div></sc-if>')
    impa=(f'<sc-if value="{H("tm_impa")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 10px;">'
      f'<div style="font-size: 13px; line-height: 1.45;">KML do Google Earth ou GeoJSON do QGIS. Polígonos e pivôs (ponto com a área em ha) viram talhões; perímetro, reserva, APP e água ficam fora.</div>'
      f'<label style="display: inline-flex; align-self: flex-start; align-items: center; gap: 8px; cursor: pointer; {BTN_ST(True,True)}">{icon("doc",15)}Escolher arquivo'
      f'<input type="file" accept=".kml,.geojson,.json" aria-label="Arquivo KML ou GeoJSON" onChange="{H("tm_arq")}" style="position: absolute; width: 1px; height: 1px; opacity: 0; overflow: hidden;"></label>'
      f'<sc-if value="{H("tm_hasierr")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("tm_ierr")}</div></sc-if></div></sc-if>')
    impr=(f'<sc-if value="{H("tm_impr")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 8px;">'
      f'<div role="status" style="font-size: 13px; font-weight: 700;">{H("tm_isum")}</div>'
      f'<sc-if value="{H("tm_hasierr")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("tm_ierr")}</div></sc-if>'
      f'<sc-for list="{H("tm_rows")}" as="r" hint-placeholder-count="3"><div style="border: 1px solid {LINE}; border-radius: 10px; padding: 8px 10px; display: flex; flex-direction: column; gap: 5px; background: #fff; {H("r.bst")}">'
      f'<div style="display: flex; flex-direction: column; gap: 1px;"><b style="font-size: 13px;">{H("r.nome")}</b><span style="font-size: 12px; color: {MUTED};">{H("r.sub")}</span></div>'
      f'<sc-if value="{H("r.hasAv")}" hint-placeholder-val="{F()}"><span style="{H("r.avst")}">{H("r.av")}</span></sc-if>'
      f'<select aria-label="Destino de {H("r.nome")}" value="{H("r.dest")}" onChange="{H("r.set")}" style="font-family: inherit; font-size: 12.5px; padding: 6px 9px; border-radius: 8px; border: 1px solid {LINE}; background: #fff;"><sc-for list="{H("r.opts")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></div></sc-for></div></sc-if>')
    tal=(f'<sc-if value="{H("tm_tal")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; border-top: 1px solid {LINE};"><sc-for list="{H("tm_kv")}" as="k" hint-placeholder-count="3">'
      f'<div style="display: flex; gap: 10px; padding: 6px 0; border-bottom: 1px solid {LINE}; font-size: 12.5px;"><span style="width: 120px; flex-shrink: 0; color: {MUTED};">{H("k.l")}</span><b style="font-weight: 700; min-width: 0;">{H("k.t")}</b></div></sc-for></div>'
      f'<div style="font-size: 12.5px; color: {MUTED}; padding-top: 8px;">Próximo passo: planejar o cultivo deste talhão na safra.</div></sc-if>')
    rodape=(f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 10px 14px; background: {SURF};">'
      f'<sc-if value="{H("tm_form")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("tm_descartar")}" style="border: 0; background: transparent; font-family: inherit; font-size: 12.5px; font-weight: 700; color: {RED}; text-decoration: underline; cursor: pointer;">Descartar</button>'
      f'<span style="flex-grow: 1;"></span><button type="button" onClick="{H("tm_redes")}" style="{_MINI}">Voltar ao desenho</button><button type="button" onClick="{H("tm_salvar")}" style="{_MINIP}">Salvar no cadastro</button></sc-if>'
      f'<sc-if value="{H("tm_impr")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("tm_outro")}" style="{_MINI}">Escolher outro arquivo</button><span style="flex-grow: 1;"></span>'
      f'<sc-if value="{H("tm_temimp")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("tm_importar")}" style="{_MINIP}">{H("tm_ibtn")}</button></sc-if></sc-if>'
      f'<sc-if value="{H("tm_tal")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("tm_redesenhar")}" style="{_MINI}">Redesenhar contorno</button><span style="flex-grow: 1;"></span>'
      f'<a href="{H("tm_cad")}" style="{_MINI} text-decoration: none;">Abrir no cadastro ›</a><a href="SAF.dc.html" style="{_MINIP} text-decoration: none;">Planejar na safra ›</a></sc-if></div>')
    return (f'<aside aria-label="{H("tm_t")}" style="width: 384px; flex-shrink: 0; border-left: 1px solid {LINE}; background: {BG}; display: flex; flex-direction: column; min-height: 0;">'
      f'<div style="display: flex; align-items: flex-start; gap: 8px; padding: 12px 14px 10px; background: {SURF}; border-bottom: 1px solid {LINE};"><div style="flex-grow: 1; min-width: 0;"><h2 style="margin: 0; font-family: {DISP}; font-size: 17px; font-weight: 700; letter-spacing: -.02em;">{H("tm_t")}</h2>'
      f'<div style="font-size: 12.3px; color: {MUTED}; margin-top: 2px;">{H("tm_sub")}</div></div>'
      f'<button type="button" onClick="{H("tm_close")}" aria-label="Fechar painel" title="Fechar painel" style="border: 0; background: {BG}; width: 30px; height: 30px; border-radius: 999px; cursor: pointer; font-size: 17px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
      f'<div style="flex-grow: 1; min-height: 0; overflow-y: auto; padding: 12px 14px; display: flex; flex-direction: column; gap: 10px;">{form}{impa}{impr}{tal}</div>{rodape}</aside>')
def _defs_body():
    return ('<pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#C9CFCB"/>'
            '<line x1="0" y1="0" x2="0" y2="10" stroke="#9E9E9E" stroke-width="4"/></pattern>')

def _rail():
    ICON={'Integrado': 'layers', 'Satélite': 'satelite', 'Lavoura': 'leaf', 'O.S./prazos': 'doc', 'Insumos': 'box', 'Custos': 'cash',
          'Solo': 'lab', 'MIP/MID': 'inseto', 'Irrigação': 'drop', 'Colheita/produtividade': 'Colheita'}
    ICON['Análises de solo']='frasco'   # 13/10/2026: o mesmo frasco do cartão Análises de solo em Agrícola
    ICON['Colheita']='Colheita'   # 14/10/2026: o mesmo desenho do cartão Previsão e colheita
    ICON['Carência e destino']='clock'   # prazo (relógio); o triângulo fica reservado a alerta real · MAPA-CARENCIA-LMR-20261003
    # pedido do proprietário (13/10/2026): "nos ícones à esquerda na barra coloque só o ícone e tooltip". O nome fica para o leitor de tela
    # (g2sr) e aparece na dica (g2dica: hover, foco de teclado e toque longo); o título "Mostrar … no mapa" continua (a dica nativa sai no hover)
    items=[f'<button type="button" role="tab" aria-selected="{H("ly%d_on" % i)}" onClick="{H("ly%d_go" % i)}" title="Mostrar {esc(NOME_LAY.get(t,t))} no mapa" data-dica="{esc(NOME_LAY.get(t,t))}" style="{H("ly%d_st" % i)}">'
           f'{icon(ICON[t],22,"currentColor")}<span class="g2sr">{esc(NOME_LAY.get(t,t))}</span></button>'
           for i,t in enumerate(MDATA['lays'])]
    return (f'<nav role="tablist" aria-orientation="vertical" aria-label="Funcionalidades do mapa" class="mapa-trilha" style="display: flex; flex-direction: column; gap: 6px; flex-shrink: 0; '
            f'background: {SURF}; border-right: 1px solid {LINE}; padding: 8px; box-sizing: border-box;">{"".join(items)}</nav>')

def build_in04(HCARD=742):
    import cenario  # cenário compartilhado (fase e realizado das ordens iguais às telas O.S., Estoque e App)
    pref=cenario.js_prefixo()
    fname='IN-04.dc.html'; E._reset_screen(fname)
    HEIGHTS37[fname]=900
    osd=dict(ords=_ordens_os())   # as mesmas ordens da tela O.S. (o Mapa usa o núcleo dela: próximo passo, impedimentos e comandos)
    import dados_mip
    import dados_solo as DSO   # Análises de solo: a mesma semente (SOLO0) do AG-02; regras em solo.js (no prefixo do cenário)
    EXTRAJS[0]=(pref+DI.js_prefixo()+dados_mip.js_prefixo()+DSO.js_prefixo()+JS_COMUM+open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'..','cal01.js'),encoding='utf-8').read()+'\n'+'const OSD = '+json.dumps(osd,ensure_ascii=False).replace('</','<\\/')+';\n'+JS_NUCLEO+_CUS.JS
                +'const M = '+json.dumps(MDATA,ensure_ascii=False).replace('</','<\\/')+';\n'+MAP_JS
                +open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'..','talgeo.js'),encoding='utf-8').read()+'\n'
                +open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),'..','talmapa.js'),encoding='utf-8').read()+r'''
function EXTRAVALS(self,v){ self.g2perfilFecha={mpa:null}; cenOuvir(self); irrOuvir(self); mipOuvir(self); MAPVALS(self,v); v.r_selm_on=!!self.state.selm?'true':'false'; v.r_medir_on=!!self.state.medir?'true':'false'; v.r_full_on=!!self.state.full?'true':'false'; v.r_pref_on=!!self.state.pref?'true':'false'; v.r_vis_on=!!self.state.cvis?'true':'false'; }
''')
    corpo=f'<div class="mapa-corpo" style="display: flex; flex-direction: row; align-items: stretch; min-width: 0; min-height: 0; background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; overflow: hidden;">{_rail()}{_mapcard(None)}</div>'
    # IN-04 no celular/tablet/zoom 200 % (pendência de componentes 03/10): a proposta comp_in04_proposta.css, validada por injeção no
    # componentes_test (8 e 31), passa a valer de fato; decide pela largura do main e do próprio mapa (container queries)
    EXTRA.append('<style>'+'main:has(>.mapa-corpo){container:in04/inline-size} .mapa-area{container:in04mapa/inline-size} @container in04 (max-width: 760px){ .mapa-corpo{flex-direction:column!important} .mapa-trilha{flex-direction:row!important;overflow-x:auto;border-right:0!important;flex-shrink:0} .mapa-trilha>button{flex:0 0 auto;width:48px!important;min-height:48px} .mapa-corpo [role=group]{flex-wrap:wrap} } @container in04 (max-width: 919px){ .mapa-corpo{flex:1 0 auto!important} .mapa-linha{flex-direction:column} .mapa-area{min-height:max(62vh,280px)} .mapa-linha aside[aria-label]{width:auto!important;border-left:0!important;border-top:1px solid #E4E9E5} } @container in04mapa (max-width: 700px){ [role=toolbar][aria-label="Ferramentas do mapa"]{left:12px;right:12px!important;top:52px!important;max-width:none!important;flex-wrap:nowrap!important;justify-content:flex-start!important;overflow-x:auto;padding:2px;scrollbar-width:thin} [role=toolbar][aria-label="Ferramentas do mapa"] button{flex-shrink:0;white-space:nowrap} .mapa-area span[style*="top: 10px"]{max-width:calc(100% - 24px);box-sizing:border-box} .mapa-area>div[style*="bottom: 12px"]{max-height:30%;overflow-y:auto;box-sizing:border-box} }'+'</style>')
    EXTRA.append(f'<sc-if value="{H("full")}" hint-placeholder-val="{F()}"><div role="dialog" aria-label="Mapa em tela cheia" style="position: fixed; inset: 0; z-index: 55; background: {BG}; padding: 14px; box-sizing: border-box; display: flex; gap: 12px;">{_rail()}{_mapcard(872,full=True)}</div></sc-if>')
    shell37('IN-04','Mapa da fazenda',corpo,primary_html=f'<span style="{H("hs_st")}">{H("hs_t")}</span>')

# =====================================================================================================
# IN-02 · Aprovações
# =====================================================================================================
# O.S. não entra aqui: a liberação, com ajuste opcional, é do agrônomo na tela O.S.
APROV=[  # (id, objeto, tipo, solicitante, alçada, venc, efeito, conflito(t,c)|None, destino, independente)
 ('a6','Ajuste de inventário Galpão 2','Ajuste de inventário','Rui · almoxarifado','Gestor','vence hoje','−12 sc MAP · contagem cega · folha de contagem',None,'SU-09.dc.html',True),
 ('a7','Política de estoque · Diesel S10','Política de estoque','Rui · almoxarifado','Gestor','até 5 dias','mínimo do tanque 40 %',None,'SU-02.dc.html',True),
 ('a8','Orçamento revisado · safra 26/27','Orçamento','Controladoria','Direção','até 7 dias','+R$ 180 mil defensivos · 2 anexos',None,'GE-02det.dc.html',False),
 ('a9','Acesso · novo operador (Beto)','Acesso e alçada','Paula · coordenação','Gestor','até 2 dias','perfil Operador · Santa Rita · termo assinado',None,'CF-01.dc.html',True),
]
def build_in02():
    fname='IN-02.dc.html'; E._reset_screen(fname)
    PZ={'vence hoje':'red','até 2 dias':'yellow','até 3 dias':'yellow','até 5 dias':'gray','até 7 dias':'gray'}
    rows=[]
    for i,ob,tp,so,al,vc,ef,cf,dest,ind in APROV:
        rows.append(R(i,ob=[Pt.b(ob),Pt.br(),Pt.mut(tp)],sol=[Pt.txt(so),Pt.br(),Pt.mut('alçada: '+al)],venc=[Pt.chip(vc,PZ[vc])],efe=ef,
                      conf=([Pt.chip(cf[0],cf[1])] if cf else [Pt.mut('—')]),sit=[Pt.cta('Decidir',dest)],
                      o=[dict(t='Abrir a decisão no módulo de origem',h=dest),dict(t=('Independente: pode entrar em aprovação em lote' if ind else 'Exige revisão individual: não entra no lote'))]))
        rows[-1]['v']['ind']='1' if ind else '0'; rows[-1]['v']['dest']=dest; rows[-1]['s']['sit']='Pendente'; rows[-1]['v']['sol']=so; rows[-1]['v']['alc']=al
    g=grid([dict(k='ob',l='Objeto e decisão',w=220),dict(k='sol',l='Solicitante · alçada'),dict(k='venc',l='Vencimento'),
            dict(k='efe',l='Efeito · valor',w=170),dict(k='conf',l='Conflito'),dict(k='sit',l='Situação')],rows,
           edit=dict(m='ro',title='Decisão',fields=[dict(k='sol',l='Solicitante',ro=True),dict(k='alc',l='Alçada',ro=True),dict(k='efe',l='Efeito · valor',ro=True)]),
           sel=True,bulk=f'<button type="button" onClick="{H("lote")}" style="{_MINIP}">Aprovar selecionados</button>',gid='g_ap',total=False)
    assert not any(a[2]=='Ordem de serviço' for a in APROV), 'O.S. não passa pela caixa de Aprovações: o agrônomo libera na tela O.S.'
    EXTRAJS[0]=JS_COMUM+r'''
function EXTRAVALS(self,v){
  v.lote=()=>{ const sp=GRx('g_ap'); const st=g2st(self,'g_ap'); const ids=Object.keys(st.sel||{}).filter(k=>(st.sel||{})[k]); if(!ids.length){ self.setState({g2toast:'Selecione decisões na caixa à esquerda.'}); return; }
    const rows=g2clone(g2rows(self,sp)); const ok=[], ind=[], ja=[]; let n=2210+(self.state.nrec||0);
    ids.forEach(id=>{ const r=rows.find(x=>x.id===id); if(!r) return; if((r.s.sit||'Pendente')!=='Pendente'){ ja.push(r.s.ob); return; }
      if(r.v.ind==='1'){ n++; r.p.sit=[{k:'chip',t:'Aprovada · AP-'+n,c:'green'}]; r.s.sit='Aprovada'; ok.push(r.s.ob+' (AP-'+n+')'); } else ind.push(r.s.ob); });
    g2set(self,'g_ap',{rows,sel:{}});
    self.setState({nrec:n-2210,g2toast:'Resultado por item · aprovadas: '+(ok.length?ok.join('; '):'nenhuma')+(ind.length?' · exigem revisão individual (não aprovadas): '+ind.join('; '):'')+(ja.length?' · já decididas, nada duplicado: '+ja.join('; '):'')+'.'}); };
  const pr=g2rows(self,GRx('g_ap')).filter(r=>(r.s.sit||'Pendente')==='Pendente'); const pend=pr.length; const hoje=pr.filter(r=>r.s.venc==='vence hoje').length;
  v.hs_t=pend+' pendentes'+(hoje?' · '+hoje+(hoje>1?' vencem hoje':' vence hoje'):''); v.hs_st=chipSt(pend?'yellow':'green');
}
'''
    corpo=bloco('Caixa única de decisões','Decida cada objeto no seu detalhe; selecione só decisões independentes para aprovar em lote com o mesmo recibo do módulo de origem.',g)
    HEIGHTS37[fname]=900
    shell37('IN-02','Aprovações',corpo,primary_html=f'<span style="{H("hs_st")}">{H("hs_t")}</span>',search=False)

# =====================================================================================================
# IN-01 · Meu dia
# =====================================================================================================
PESSOAS=['Ana','Caio','Carlos','Rui','Paula','Marcos','João','Equipe qualidade','Equipe expedição','Sem responsável']
def build_in01():
    fname='IN-01.dc.html'; E._reset_screen(fname)
    OM=D.OM; t1=OM['ativo'].split(' · ')[0]
    FILA=[  # id, objeto, local, tarefa, prazo, resp, impedimento(t,c)|None, ação(t,h)
     ('f1','OS-0420 · plantio','Santa Rita · T4',f'Substituir {t1} bloqueado','vence hoje','Carlos',(f'Ativo bloqueado · {OM["id"]}','red'),('Reprogramar saldo','PL-05.dc.html')),
     ('f2','OS-0418 · fertirrigação','Santa Rita · P1','Liberar a fertirrigação (pode ajustar)','vence hoje','Ana',('Falta insumo · Ureia 45%','red'),('Liberar','OS.dc.html#OS-0418')),
     ('f3','OS-0430 · dessecação','Santa Rita · T1-A','Liberar a dessecação (pode ajustar)','até 3 dias','Ana',None,('Liberar','OS.dc.html#OS-0430')),
     ('f4','OS-0417 · cobertura','Santa Rita · P1',f'Receber devolução de sobras ({D.REQ["custodia"]} sc)','vence hoje','Rui',None,('Receber devolução','EST.dc.html')),
     ('f5','Fila de expedição','Sede · doca 1','Chamar o próximo apto da fila (T2)','vence hoje','Equipe expedição',('T1 atrasado · prev. 09:10','red'),('Abrir fila','LO-02.dc.html')),
     ('f6','OS-0421 · fungicida','Santa Rita · T1+T2',f'Conferir o apontamento do dia 4 ({D.OS[0]["dias"][3]} ha)','até 3 dias','Paula',None,('Conferir apontamentos','CA-02.dc.html')),
     ('f7','INSP-88 · qualidade','Armazém Sede',f'Decidir o lote {D.LOTE_BLOQ["id"]}','até 3 dias','Equipe qualidade',('Lote bloqueado','red'),('Abrir inspeção','CO-06det.dc.html')),
     # f8 (amostragem de solo do T2) saiu (SOLO-01, R01/A16): o T2 já tem o LAU-2063; a coleta é operação do plano
    ]
    PZ={'vence hoje':'red','até 3 dias':'yellow','no prazo':'green'}
    rows=[R(i,ob=[Pt.b(o),Pt.br(),Pt.mut(l)],tar=t,pz=(p,[Pt.chip(p,PZ[p])]),resp=r,imp=([Pt.chip(*im)] if im else [Pt.mut('—')]),acao=[Pt.cta(a[0],a[1])]) for i,o,l,t,p,r,im,a in FILA]
    g=grid([dict(k='ob',l='Objeto · local',w=200),dict(k='tar',l='Tarefa',w=260),dict(k='pz',l='Prazo',chips=PZ),dict(k='resp',l='Responsável'),dict(k='imp',l='Impedimento'),dict(k='acao',l='Próxima ação')],rows,
           edit=dict(m='form',title='Tarefa',sub='Atribua o responsável ou ajuste o prazo; a ordem de origem não muda.',
                     fields=[dict(k='tar',l='Tarefa',ro=True),dict(k='resp',l='Responsável',t='sel',opts=PESSOAS,req=True),dict(k='pz',l='Prazo',t='sel',opts=list(PZ),req=True)]),
           gid='g_dia',total=False)
    EXTRAJS[0]=JS_COMUM+r'''
function PREVALS(self,v){ g2rows(self,GRx('g_dia')).forEach(r=>{ if(r.v.resp==='Sem responsável'){ r.p.resp=[{k:'mut',t:'sem responsável'}]; r.s.resp='Sem responsável'; } else { delete r.p.resp; r.s.resp=r.v.resp; } }); }
function EXTRAVALS(self,v){ const rs=g2rows(self,GRx('g_dia')); const h=rs.filter(r=>r.v.pz==='vence hoje').length; const sr=rs.filter(r=>r.v.resp==='Sem responsável').length;
  v.hs_t=h+' vencem hoje'+(sr?' · '+sr+' sem responsável':''); v.hs_st=chipSt(h?'red':'green'); }
'''
    alert=(nota(f'{B(esc(OM["causa"]))} no {esc(t1)} · <b style="color:{INK};">×3 esta noite</b> → caso único {OM["id"]}<br>'
               f'Sincronização pendente do celular de João · <b style="color:{INK};">×2</b> → registros guardados no aparelho, sem conflito'))
    corpo=(bloco('Fila do dia','Resolva primeiro o que vence hoje; clique na linha para atribuir o responsável ou ajustar o prazo.',g)
           + bloco('Alertas agrupados','Trate cada caso uma vez; alertas repetidos ficam agrupados com a contagem.',alert,
                   ilink('Abrir OM-0233','MA.dc.html#om=OM-0233','wrench','Abrir a ordem de manutenção do Trator T1')+ilink('Ver app de João','MB-01.dc.html','users','Abrir o app móvel'),tone='yellow'))
    HEIGHTS37[fname]=900
    shell37('IN-01','Meu dia',corpo,primary_html=f'<span style="{H("hs_st")}">{H("hs_t")}</span>'+btn('Registrar ocorrência',True,href='CA-03.dc.html'),search=False)

# =====================================================================================================
# IN-03 · Agenda e pendências
# =====================================================================================================
DIAS=[('2026-09-23','ter · hoje'),('2026-09-24','qua'),('2026-09-25','qui'),('2026-09-26','sex'),('2026-09-27','sáb')]
def build_in03():
    fname='IN-03.dc.html'; E._reset_screen(fname)
    OM=D.OM
    AG=[ # id, data, objeto, resp, prioridade, compromisso, bloqueio(t,c)|None, prazo limite, (ação,h)
     ('g1','2026-09-23',f'Conferir apontamento dia 4 · {D.OS[0]["id"]}','Paula','Alta','conferência diária',None,'23/09 18:00',('Abrir origem','CA-02.dc.html')),
     ('g6','2026-09-23','Resolver conflito da OS-0423 com a parada da B3','Caio','Alta','irrigação do T7 hoje 14:00–16:00',('Conflito · parada da B3','red'),'23/09 14:00',('Resolver conflito','IR-03det.dc.html#OS-0423:conflito')),
     ('g2','2026-09-23',f'Receber devolução {D.REQ["id"]} ({D.REQ["custodia"]} sc)','Rui','Alta','custódia zerada para encerrar',None,'24/09',('Receber devolução','EST.dc.html')),
     ('g3','2026-09-24',f'Substituir {OM["ativo"].split(" · ")[0]} na {OM["os_afetada"]} (T4)','Carlos','Alta','início programado',(f'{OM["id"]} em execução','red'),'24/09 06:00',('Reprogramar','PL-05.dc.html')),
     ('g4','2026-09-25',f'Decidir INSP-88 · lote {D.LOTE_BLOQ["id"]}','Equipe qualidade','Normal','liberação comercial',('Lote bloqueado','red'),'25/09',('Abrir origem','CO-06det.dc.html')),
     # g5 (amostragem de solo do T2) saiu (SOLO-01, R01/A16): o T2 já tem o LAU-2063
     ('g7','2026-09-24','Definir janela da OS-0422 · Pivô 2 (2 passadas de 6,75 mm)','João','Normal','próximo ciclo de irrigação',('Janela a definir','yellow'),'25/09',('Definir janela','IR-03det.dc.html#OS-0422:janela')),
    ]
    PR={'Alta':'red','Normal':'gray','Baixa':'gray'}
    rows=[R(i,dt=d,ob=[Pt.b(o)],resp=r,pri=(p,[Pt.chip(p,PR[p])]),comp=[Pt.txt(c)]+([Pt.br(),Pt.chip(*b)] if b else []),lim=l,acao=[Pt.cta(a[0],a[1])]) for i,d,o,r,p,c,b,l,a in AG]
    for r_,a in zip(rows,AG): r_['v']['ob']=a[2]
    g=grid([dict(k='dt',l='Data',t='date'),dict(k='ob',l='Compromisso',w=280),dict(k='resp',l='Responsável'),dict(k='pri',l='Prioridade',chips=PR),dict(k='comp',l='Condição · bloqueio',w=230),
            dict(k='lim',l='Prazo limite'),dict(k='acao',l='Abrir')],rows,
           edit=dict(m='form',title='Compromisso',newTitle='Nova tarefa vinculada',sub='Mude data, responsável ou prioridade; a obrigação de origem mantém o prazo limite.',
                     fields=[dict(k='ob',l='Compromisso',req=True,help='Vincule a um registro existente (ordem, lote, requisição); a tarefa não duplica a O.S.'),dict(k='dt',l='Data',t='date',req=True),
                             dict(k='resp',l='Responsável',t='sel',opts=PESSOAS,req=True,**{'def':'Ana'}),dict(k='pri',l='Prioridade',t='sel',opts=list(PR),req=True,**{'def':'Normal'})]),
           gid='g_ag',total=False,so={'k':'dt','d':False})
    import cenario
    # compromissos de irrigação (OS-0423, OS-0422) lidos do estado da irrigação: passo, dono, condição e prazo atuais
    EXTRAJS[0]=(cenario.js_prefixo()+DI.js_prefixo()+JS_COMUM+'const DIAS='+json.dumps(DIAS,ensure_ascii=False)+';\nconst PESS='+json.dumps(PESSOAS,ensure_ascii=False)+';\n'+r'''
const IRR_AG={g6:'OS-0423',g7:'OS-0422'};
function agIrr(self){ let s=null; try{ irrOuvir(self); s=irrGet(); }catch(e){ return; }
  g2rows(self,GRx('g_ag')).forEach(r=>{ const id=IRR_AG[r.id]; const o=id&&s.ordens[id]; if(!o) return; const x=s.setores[o.setor];
    const p=irrProx(s,o); const et=irrEtapa(s,o); const sel=irrSelos(s,o).filter(z=>!z.mut);
    r.v.ob=p?(p.t+' · '+id+' · '+x.nome):(id+' · '+x.nome+' · '+et.toLowerCase());
    r.p.comp=[{k:'txt',t:'irrigação · '+irrJanO(o)},{k:'br',t:''}].concat(sel.length?[{k:'chip',t:sel[0].t,c:sel[0].c}]:[{k:'chip',t:et,c:IRR_COR[et]||'gray'}]);
    r.p.acao=[{k:'cta',t:p?p.t:'Abrir ordem',h:p?p.h:'IR-03det.dc.html#'+id,u:false}];
    const q=(o.passadas.find(z=>z.st==='Programada'&&z.ini!==null&&z.ini!==undefined)||{}).ini; r.v.lim=p&&q!==undefined?irrDdmm(irrDiaN(q))+' '+irrHm(q):'—';
    const pri=p&&p.r<=2?'Alta':'Normal'; if(r.__pa===undefined||r.v.pri===r.__pa){ r.v.pri=pri; r.__pa=pri; }
    const dn=p&&p.dono?String(p.dono).split(' ')[0]:''; if(dn&&PESS.indexOf(dn)>=0&&(r.__rs===undefined||r.v.resp===r.__rs)){ r.v.resp=dn; r.__rs=dn; } }); }
function PREVALS(self,v){ agIrr(self); g2rows(self,GRx('g_ag')).forEach(r=>{ r.p.ob=[{k:'b',t:r.v.ob||''}]; r.s.ob=r.v.ob; if(!r.p.acao) r.p.acao=[{k:'mut',t:'tarefa vinculada'}];
  r.p.pri=[{k:'chip',t:r.v.pri,c:r.v.pri==='Alta'?'red':'gray'}]; if(!r.v.lim){ r.v.lim='—'; } if(!r.p.comp && !r.v.comp) r.p.comp=[{k:'mut',t:'tarefa vinculada'}];
  if(r.v.resp==='Sem responsável'){ r.p.resp=[{k:'mut',t:'sem responsável'}]; } else delete r.p.resp; }); }
function EXTRAVALS(self,v){ const rs=g2rows(self,GRx('g_ag'));
  v.semana=DIAS.map((d,i)=>({t:d[0].slice(8,10)+'/'+d[0].slice(5,7)+' · '+d[1].toUpperCase(), st:'flex:1 1 0;min-width:0;border:1px solid #E4E9E5;border-radius:12px;padding:8px 10px;background:'+(i===0?'#E4F3E9':'#F4F6F3')+';',
    tst:'font-size:11px;font-weight:800;letter-spacing:.05em;color:'+(i===0?'#1E7A4C':'#65736A')+';',
    its:rs.filter(r=>r.v.dt===d[0]).map(r=>({t:r.v.ob, st:'margin-top:6px;font-size:12px;line-height:1.3;padding:5px 8px;border-radius:8px;background:#fff;border-left:3px solid '+(r.v.pri==='Alta'?'#B42318':'#E4E9E5')+';'}))}));
  const alta=rs.filter(r=>r.v.pri==='Alta').length; v.hs_t=rs.length+' compromissos · '+alta+' de prioridade alta'; v.hs_st=chipSt(alta?'yellow':'green'); }
''')
    semana=(f'<div style="display: flex; gap: 10px;"><sc-for list="{H("semana")}" as="d" hint-placeholder-count="5"><div style="{H("d.st")}"><div style="{H("d.tst")}">{H("d.t")}</div>'
            f'<sc-for list="{H("d.its")}" as="i" hint-placeholder-count="1"><div style="{H("i.st")}">{H("i.t")}</div></sc-for></div></sc-for></div>')
    dep=nota(f'Encerrar {B(D.REQ["os"])} depende de receber {D.REQ["custodia"]} sc em custódia {B("ou")} da destinação formal das sobras.<br>'
             f'Iniciar o saldo da {B(OM["os_afetada"])} depende só da alocação substituta ({esc(OM["substituto"])}); a v3 já vale no saldo.')
    corpo=(bloco('Semana de 23 a 27/09','Confira os compromissos da semana; adiar um alerta não muda a data da obrigação.',semana)
           + bloco('Compromissos','Clique na linha para mudar data, responsável ou prioridade; “Abrir” leva ao registro de origem.',g)
           + bloco('Dependências','Resolva estas condições para encerrar e iniciar as ordens.',dep,
                   ilink('Reprogramar no PCP','PL-05.dc.html','calendar','Abrir Impedimentos e reprogramação'),tone='yellow'))
    HEIGHTS37[fname]=1100  # 7 compromissos (conflito da OS-0423 e janela da OS-0422) + Dependências sem corte
    prim=f'<span style="{H("hs_st")}">{H("hs_t")}</span><button type="button" onClick="{H("g_ag_new")}" style="{BTN_ST(True,False)}">Criar tarefa vinculada</button>'
    shell37('IN-03','Agenda e pendências',corpo,primary_html=prim,search=False)

def build():
    build_in01(); build_in02(); build_in03(); build_in04()
