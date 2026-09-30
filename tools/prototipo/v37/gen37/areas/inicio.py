# -*- coding: utf-8 -*-
"""Mapa (IN-04, 1º item do menu) + módulos ocultos do Início: IN-01 Meu dia · IN-02 Aprovações (+ decisões IN-02det OS-0418 e
IN-02x-os0420 revisão de saldo) · IN-03 Agenda e pendências.

Irrigação só com água NÃO passa pelo agrônomo (decisão do proprietário, igual a irrigacao.py): a lâmina vem do balanço hídrico
e a liberação da prontidão operacional. OS-0419 liberada pela necessidade do balanço (10,81 mm hoje); OS-0422 "Janela a definir"
(amarelo, dono João, atalho IR-02); OS-0423 "Conflito · parada da B3" (vermelho, dono Caio · PCP). Só a fertirrigação (OS-0418)
vai ao agrônomo. A antiga decisão IN-02x-os0422 (exceção de água) deixou de ser gerada.
Filtro Fazenda do topo (mf_faz): Santa Rita = mapa; Boa Vista = estado vazio (sem talhão desenhado); Todas = Santa Rita + aviso.
Fase e realizado das ordens no mapa vêm do cenário compartilhado (cenario.js · cenGet/cenOuvir), iguais às telas O.S., Estoque e App.

IN-04 · Mapa: tela de trabalho sem rolagem (1440×900). Barra lateral de funcionalidades (ícone + nome) · 9 camadas canônicas ·
filtros DA CAMADA ATIVA no topo do bloco · cores dos talhões calculadas no cliente (buracos {{fl_T1}}…) e recalculadas a cada
filtro · clique no talhão abre painel lateral com informação e ações da camada · faixa fina com legenda e 4 números.

observacoes (dados locais coerentes com dados.py / dados2.py / telas vizinhas):
- Ordens no mapa = dados.ORDENS (registro canônico, menos OB-0104 que é do armazém): tipo, fase, selo, janela, saldo,
  responsável e link de detalhe vêm do registro; OS-0430 (T1-A) aparece no polígono T1.
- OS-0420: 30/100 ha, saldo 70 ha, v2 vigente; selos = selo + selos_extra do registro ("Impedida · ativo bloqueado" +
  "Revisão de saldo pendente · v3"), iguais aos de OS.dc.html e CA-01x-os0420 (DEMO-14). OS-0431 "Falta máquina" conta como impedida.
- Geometria (26/09): dados.GEO_TAL/GEO_PARC, fonte única com o CD-01det (polígono do T1 v3 validado em 12/09; T1-B sem polígono).
  O painel Integrado mostra a linha Geometria onde houver dado; "Próxima ocupação" marca a parcela sem polígono. A T1-B não é desenhada.
- "Criar vistoria" da barra do MIP/MID é um modo (como Medir): clique no talhão cria a vistoria com a mesma função do painel,
  sem duplicar; com talhão(ões) já selecionado(s), cria direto.
  O cenário 60/40 pedido pelo defeito DEMO-14 exige mudar dados.OS (fora deste módulo) — mantido 30/70 para as telas concordarem.
- OS-0419: janela "hoje 20:00–amanhã 10:31" = 1 volta a 62 % (≈14,5 h), a mesma do IR-02/IR-03det, PL-04 e OS.dc.html.
  OS-0418: "24/09 21:00–25/09 11:15" (8,1 mm × 95 ha ÷ 150 L/s ≈ 14,3 h), a mesma do IR-02 e PL-04.
- Satélite (local): Sentinel-2 L2A 10 m, cenas 21/09 (nuvem 4 %, C1 coberto), 16/09 (0 %) e 06/09 (32 %, P2 e T7 cobertos);
  NDVI/NDRE/EVI/NDWI de P1, P2, T7 e C1; T1/T2/T4/T3 sem cultura (solo exposto/colhido). Mancha em T7: 0,4 ha (16/09) → 1,2 ha (21/09).
  Nova vistoria criada pelo mapa = VIS-018 (agronomia.py usa até VIS-017).
- Solo (local): laudos LAU-2037…2052 (2026, 0–20/20–40; T4 = LAU-2043/2044 como agronomia.py) e LAU-1837…1852 (2025).
- MIP: vistorias VIS-011, 013, 014, 015, 016, 017 de agronomia.py + históricas VIS-006 (P1 percevejo) e VIS-008 (T7 ácaro).
- Irrigação: déficits de irrigacao.py (P2 11,2 mm · P1 8,4 mm · T7 ≈10,0 mm estimado, sonda sem dado).
- Custos (local): R$/ha realizado × orçado com abertura insumos/operações/máquinas; T4 +18 % (reparo OM-0233 + substituto).
- Decisões: recibos AP-2201 (OS-0418 v2; a REQ-038 reserva a Ureia só ao liberar), AP-2202 (OS-0420 v3). A fila do agrônomo só tem o que é
  dele: OS-0418 v2, OS-0420 v3 e OS-0430 v1 (dessecação T1-A, revisada na tela O.S.) — a mesma no Mapa, nas Aprovações e na próxima pendência.
  A decisão tomada em IN-02det/IN-02x grava selo, versão e recibo na ordem do cenário compartilhado (igual à revisão da tela O.S.);
  Mapa, Aprovações e O.S. leem esse estado. A próxima pendência percorre a fila em círculo; "Fila vazia" só sem nenhuma pendente.
  Custo dos 30 ha preservados da OS-0420: semente 1.560 kg × R$ 9,50 + KCl 3.600 kg × R$ 2,40 = R$ 23.460.
- Sobras: "Receber sobras"/"Receber devolução" levam ao Estoque do menu (EST.dc.html · etapa Receba devoluções), que grava no cenário.
"""
import json
from engine import (grid,esc,icon,chip,btn,Pt,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,DISP,
                    BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, continuity, HEIGHTS37, PARENT37, LCOR
import dados as D
import dados2 as D2

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
T=lambda: H('true')
def nfb(v,d=0):
    s=f'{v:,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')
    return s

# ---------------------------------------------------------------- utilitários visuais (padrão novo)
def bloco(titulo,desc,corpo,acao='',tone=None):
    bd={'yellow':YEL,'red':RED}.get(tone,LINE)
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; {"border-left: 4px solid "+bd+";" if tone else ""} border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{titulo}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>'
            f'<div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end;">{acao}</div></div>'
            f'<div style="padding: 0 12px 12px;">{corpo}</div></section>')
_IST='display: inline-flex; align-items: center; gap: 6px; text-decoration: none; '
def ilink(text,href,ico,title,primary=False):
    return f'<a href="{href}" title="{esc(title)}" aria-label="{esc(title)}" style="{_IST}{BTN_ST(primary,True)}">{icon(ico,15)}{esc(text)}</a>'
def ifn(text,fn,ico,title,primary=False):
    return f'<button type="button" onClick="{H(fn)}" title="{esc(title)}" aria-label="{esc(title)}" style="{_IST}{BTN_ST(primary,True)}">{icon(ico,15)}{text}</button>'
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
LAYS=['Integrado','Satélite','Solo','MIP/MID','O.S./prazos','Irrigação','Estádio','Colheita/produtividade','Custos']
# filtros da camada ativa (k, rótulo, opções) — o primeiro valor é o padrão
FILT={
 'Integrado':[('mostrar','Mostrar',['Todas as condições','Só pendências'])],
 'Satélite':[('idx','Índice',['NDVI','NDRE','EVI','NDWI']),('dt','Cena',['21/09','16/09','06/09'])],
 'Solo':[('attr','Atributo',['V%','pH','P','K','MO','CTC']),('prof','Profundidade',['0–20 cm','20–40 cm']),('camp','Campanha',['2026','2025'])],
 'MIP/MID':[('alvo','Alvo',['Todos','Mosca-branca','Nematoide','Ácaro','Lagarta-do-cartucho','Mancha-de-phoma','Percevejo']),('per','Período',['7 dias','30 dias'])],
 'O.S./prazos':[('fase','Fase',['Todas','A liberar','Liberadas','Em execução','Em conferência','Encerradas'])],
 'Irrigação':[('vis','Visão',['Balanço hídrico','Programação de hoje'])],
 'Estádio':[('cult','Cultura',['Todas','Soja','Milho','Feijão','Mamão','Café'])],
 'Colheita/produtividade':[('vis','Visão',['Realizado','Previsto']),('safra','Safra',['2026/27','2025/26'])],
 'Custos':[('most','Mostrar',['R$/ha realizado','Desvio do orçado']),('grp','Grupo',['Todos','Insumos','Operações','Máquinas'])],
}
# ordens no mapa = dados.ORDENS (menos OB-0104, do armazém). Tipo, selo, janela, responsável e link de detalhe vêm do registro
# canônico; fase, realizado, saldo e custódia vêm do cenário compartilhado no navegador (cenGet), com o registro como semente.
# Aqui ficam só os campos do mapa: talhões da geometria, complemento do realizado, prazo e a próxima ação da ordem
# (rótulo, destino, tipo: 'dec' = decisão do agrônomo · 'op' = pendência operacional; condição: 'ag' = só com a decisão do agrônomo
# pendente no cenário (selo "Aguardando agrônomo" ou "Revisão de saldo pendente"), 'cust' = só com custódia).
# Decisões do agrônomo = mesma fila da caixa de Aprovações (IN_AG): OS-0418 v2, OS-0420 v3 e OS-0430 v1 (revisão na tela O.S.).
_ORD_MAPA=[  # id, talhões da geometria, complemento do realizado, prazo, ação
 ('OS-0421',['T1','T2'],'','no prazo',None),
 ('OS-0420',['T4'],'','atrasada',('Revisar v3','IN-02x-os0420.dc.html','dec','ag')),
 ('OS-0419',['P2'],'lâmina 10,81 mm','irrigando hoje',None),
 ('OS-0424',['P2'],'','até 3 dias',None),
 ('OS-0422',['P2'],'2 passadas de 6,75 mm','até 3 dias',('Definir janela','IR-02.dc.html','op',None)),
 ('OS-0418',['P1'],'Ureia 12 kg/ha','vence hoje',('Revisar v2','IN-02det.dc.html','dec','ag')),
 ('OS-0417',['P1'],'','até 3 dias',('Receber sobras','EST.dc.html','op','cust')),
 ('OS-0415',['T3'],'','encerrada',None),
 ('OS-0423',['T7'],'estimativa por ET','vence hoje',('Resolver conflito','IR-02.dc.html','op',None)),
 ('OS-0425',['C1'],'','no prazo',None),
 ('OS-0430',['T1'],'T1-A','até 3 dias',('Revisar v1','OS.dc.html','dec','ag')),
 ('OS-0431',['T2'],'','até 3 dias',None),
]
# fila do agrônomo (a mesma na caixa de Aprovações, no Mapa e na "Próxima pendência" das decisões): (O.S., versão, onde decide, rótulo)
IN_AG=[('OS-0418','v2','IN-02det.dc.html','OS-0418 · fertirrigação P1 · v2'),
       ('OS-0420','v3','IN-02x-os0420.dc.html','OS-0420 · revisão de saldo · v3'),
       ('OS-0430','v1','OS.dc.html','OS-0430 · dessecação T1-A · v1')]
# decisões do agrônomo no cenário compartilhado: pendente = selo do agrônomo na ordem; a decisão tomada nas telas IN-02det/IN-02x
# grava selo, versão e recibo na ordem (igual à revisão da tela O.S.), e o Mapa, as Aprovações e a O.S. leem o mesmo estado.
JS_AG=r'''
const IN_AG = '''+json.dumps(IN_AG,ensure_ascii=False)+r''';
function inPendAg(c,id){ const co=c&&c.ordens?c.ordens[id]:null; if(!co||co.etapa==='Encerradas'||co.etapa==='Canceladas') return false;
  return (co.selos||[]).some(s=>/^(Aguardando agrônomo|Revisão de saldo pendente)/.test(s.t)); }
function inDecAg(c,id){ const co=c&&c.ordens?c.ordens[id]:null; if(!co||inPendAg(c,id)) return null; if(co.decAg) return co.decAg;
  const s=(co.selos||[]).map(x=>x.t).join('|');
  if(/Rejeitada/.test(s)) return {k:'rejeitada',mot:(co.osc&&co.osc.rej)||''}; if(/Devolvida/.test(s)) return {k:'devolvida',mot:''};
  return {k:'aprovada',rec:(co.osc&&co.osc.recibo&&co.osc.recibo.id)||''}; }
function inProx(c,id){ const i=IN_AG.findIndex(a=>a[0]===id);
  for(let j=1;j<=IN_AG.length;j++){ const a=IN_AG[(i+j+IN_AG.length)%IN_AG.length]; if(a[0]!==id&&inPendAg(c,a[0])) return ['Próxima pendência: '+a[3],a[2]]; }
  return ['Fila vazia · voltar às Aprovações','IN-02.dc.html']; }
'''
# irrigação só com água: sem agrônomo e sem "política" — o selo é a pendência operacional, com o dono dela (igual a IR-02/IR-03)
IRR_OS={'OS-0419':dict(tipo='Irrigação · água',selos=[]),
        'OS-0422':dict(tipo='Irrigação · água',selos=[['Janela a definir','yellow']],dono='João'),
        'OS-0423':dict(tipo='Irrigação · água por gotejo',selos=[['Conflito · parada da B3','red']],dono='Caio · PCP')}
def _selo_cor(t):
    if t.startswith('Impedida') or t.startswith('Falta máquina') or t.startswith('Conflito'): return 'red'
    return 'green' if t.startswith('Aprovada') else 'yellow'
def _ord_mapa():
    out=[]
    for oid,tal,suf,pz,act in _ORD_MAPA:
        o=D.ORDEM[oid]; ts=([o['selo']] if o['selo'] else [])+list(o.get('selos_extra') or [])
        real=f"{nfb(o.get('realizado') or 0)}/{nfb(o.get('area') or 0)} ha"+(f" · saldo {nfb(o['saldo'])} ha" if o.get('realizado') and o.get('saldo') else '')+(f' · {suf}' if suf else '')
        d=dict(id=oid,tal=tal,tipo=o['tipo'],fase=o['etapa'],selos=[[t,_selo_cor(t)] for t in ts],area=o.get('area') or 0,suf=suf,
               jan=o['janela'],real=real,saldo=o['saldo'] or 0,resp=o['resp'],pz=pz,h=o['detalhe'] or 'OS.dc.html')
        if oid in IRR_OS: d.update(IRR_OS[oid])
        if act: d['act']=dict(t=act[0],h=act[1],k=act[2],c=act[3])
        out.append(d)
    assert {x['id'] for x in out}=={o['id'] for o in D.ORDENS if o['id'].startswith('OS-')}, 'mapa fora do registro de ordens'
    assert not any('política' in json.dumps(x,ensure_ascii=False) for x in out), 'irrigação só com água não usa política/agrônomo'
    return out
ORD=_ord_mapa()
# {OS-xxxx} no rótulo = realizado atual da ordem (cenário) · {?OS-xxxx texto} = texto só enquanto a decisão do agrônomo está pendente.
# Talhão sem condição pior ganha amarelo ("atenção ou decisão pendente") enquanto uma ordem dele aguarda o agrônomo (mesma contagem do cabeçalho).
INTEG={'T1':['ok','OS-0421 · {OS-0421}'],'T2':['red','OS-0431 impedida · Trator T1'],'T4':['red','OS-0420 impedida{?OS-0420 · v3}'],'T3':['gray','OS-0415 encerrada'],
       'P1':['red','mosca-branca > NC'],'P2':['yellow','OS-0422 · janela a definir'],'T7':['red','OS-0423 conflito · mancha 1,2 ha'],'C1':['yellow','OS-0425 · entrega sem saldo']}
SAT={'21/09':dict(nuvem=4,v={'P1':[.84,.42,.58,.18],'P2':[.76,.36,.51,.12],'T7':[.66,.29,.44,.05],'C1':'cloud'},nt={'C1':100,'P1':0,'P2':1,'T7':2},
                  manchas=[dict(t='T7',ha=1.2,val=.38,evo='nova · era 0,4 ha em 16/09',coord='−15,5612 · −54,2987',tipo='reboleira arredondada (praga, doença ou nematoide)')]),
     '16/09':dict(nuvem=0,v={'P1':[.82,.40,.56,.16],'P2':[.73,.34,.49,.10],'T7':[.71,.31,.47,.07],'C1':[.70,.30,.45,.08]},nt={},
                  manchas=[dict(t='T7',ha=0.4,val=.52,evo='nova',coord='−15,5612 · −54,2987',tipo='reboleira arredondada (praga, doença ou nematoide)')]),
     '06/09':dict(nuvem=32,v={'P1':[.78,.37,.52,.14],'P2':'cloud','T7':'cloud','C1':[.72,.31,.46,.09]},nt={'P2':64,'T7':71},manchas=[])}
SEMCULT={'T1':'solo exposto · pré-plantio','T2':'solo exposto · pré-plantio','T4':'semeadura · sem leitura','T3':'colhido 12/09'}
IDX={'NDVI':[[.30,'red','< 0,30 falha'],[.45,'orange','0,30–0,45 fraco'],[.60,'yellow','0,45–0,60 atenção'],[.72,'lime','0,60–0,72 médio'],[.82,'ok','0,72–0,82 bom'],[None,'good','> 0,82 vigor alto']],
     'NDRE':[[.12,'red','< 0,12 falha'],[.20,'orange','0,12–0,20 fraco'],[.27,'yellow','0,20–0,27 atenção'],[.33,'lime','0,27–0,33 médio'],[.40,'ok','0,33–0,40 bom'],[None,'good','> 0,40 vigor alto']],
     'EVI':[[.15,'red','< 0,15 falha'],[.25,'orange','0,15–0,25 fraco'],[.35,'yellow','0,25–0,35 atenção'],[.45,'lime','0,35–0,45 médio'],[.55,'ok','0,45–0,55 bom'],[None,'good','> 0,55 vigor alto']],
     'NDWI':[[0,'orange','< 0 muito seco'],[.05,'yellow','0–0,05 seco'],[.15,'blue','0,05–0,15 adequado'],[None,'navy','≥ 0,15 úmido']]}
SOLO_B={'T1':[48,4.9,11,62,28,8.6],'T2':[55,5.1,14,88,30,9.1],'T4':[41,4.6,7,36,24,7.8],'T3':[62,5.4,19,110,33,10.2],
        'P1':[58,5.3,16,95,31,9.6],'P2':[60,5.4,21,126,34,10.5],'T7':[66,5.8,24,140,36,11.4],'C1':[52,5.0,12,80,29,9.0]}
ATTR={'V%':dict(n='Saturação por bases (V%)',u='%',d=0,m='cálculo SB/CTC',t=[[45,'red','< 45 % baixo'],[55,'yellow','45–55 % médio'],[60,'ok','55–60 % adequado'],[None,'good','≥ 60 % alto']]),
      'pH':dict(n='pH',u='',d=1,m='CaCl₂ 0,01 mol/L',t=[[4.5,'red','< 4,5 baixo'],[5.0,'yellow','4,5–5,0 médio'],[5.5,'ok','5,0–5,5 adequado'],[None,'good','≥ 5,5 alto']]),
      'P':dict(n='Fósforo (P)',u='mg/dm³',d=0,m='Mehlich-1',t=[[8,'red','< 8 baixo'],[12,'yellow','8–12 médio'],[18,'ok','12–18 adequado'],[None,'good','≥ 18 alto']]),
      'K':dict(n='Potássio (K)',u='mg/dm³',d=0,m='Mehlich-1',t=[[40,'red','< 40 baixo'],[80,'yellow','40–80 médio'],[120,'ok','80–120 adequado'],[None,'good','≥ 120 alto']]),
      'MO':dict(n='Matéria orgânica (MO)',u='g/dm³',d=0,m='Walkley-Black',t=[[15,'red','< 15 baixa'],[25,'yellow','15–25 média'],[35,'ok','25–35 adequada'],[None,'good','≥ 35 alta']]),
      'CTC':dict(n='CTC a pH 7',u='cmolc/dm³',d=1,m='soma de bases + H+Al',t=[[4,'red','< 4 baixa'],[8,'yellow','4–8 média'],[12,'ok','8–12 adequada'],[None,'good','≥ 12 alta']])}
def _solo():
    out={}; keys=list(ATTR)
    for camp,dv in (('2026',0),('2025',1)):
        for prof,fac in (('0–20 cm',None),('20–40 cm',1)):
            for i,t in enumerate(TIDS):
                b=SOLO_B[t][:]
                if camp=='2025': b=[b[0]-4,round(b[1]-.1,1),max(3,b[2]-2),b[3]-6,b[4]-1,round(b[5]-.2,1)]
                if fac: b=[b[0]-9,round(b[1]-.3,1),round(b[2]*.4),round(b[3]*.7),round(b[4]*.7),round(b[5]*.85,1)]
                n=(2037 if camp=='2026' else 1837)+i*2+(1 if fac else 0)
                out.setdefault(camp,{}).setdefault(prof,{})[t]=dict(zip(keys,b),lau=f'LAU-{n}',dt=('12/08/2026' if camp=='2026' else '14/08/2025'))
    return out
MIP=[dict(id='VIS-011',t='T4',alvo='Nematoide',txt='Nematoide-de-cisto · reboleiras',res='foco em investigação',c='orange',dt='20/09',d=3,met='trincheira · cistos/200 cm³ · 14/14 pontos',h='AG-01det.dc.html'),
     dict(id='VIS-013',t='P1',alvo='Mosca-branca',txt='Mosca-branca · R5',res='acima do NC · 5,1/4,0',c='red',dt='21/09',d=2,met='pano-de-batida · 12/12 pontos',h='AG-01.dc.html',diag=True),
     dict(id='VIS-014',t='P1',alvo='Ácaro',txt='Ácaro · R5',res='em coleta · 9/14 pontos',c='yellow',dt='22/09',d=1,met='contagem direta · % folíolos',h='AG-01.dc.html'),
     dict(id='VIS-015',t='P2',alvo='Lagarta-do-cartucho',txt='Lagarta-do-cartucho · V10',res='abaixo do limiar',c='ok',dt='21/09',d=2,met='contagem direta · % plantas · 14/14 pontos',h='AG-01.dc.html'),
     dict(id='VIS-016',t='C1',alvo='Mancha-de-phoma',txt='Mancha-de-phoma · granação',res='coleta incompleta · sincronização pendente',c='yellow',dt='22/09',d=1,met='contagem direta · % ramos · 6/12 pontos',h='AG-01.dc.html'),
     dict(id='VIS-006',t='P1',alvo='Percevejo',txt='Percevejo · R3',res='abaixo do NC · 0,8/2,0',c='ok',dt='04/09',d=19,met='pano-de-batida',h='AG-01.dc.html'),
     dict(id='VIS-008',t='T7',alvo='Ácaro',txt='Ácaro-rajado · produção',res='atenção · 3/10 folhas',c='yellow',dt='08/09',d=15,met='contagem direta · % folhas',h='AG-01.dc.html')]
IRR={'bal':{'P1':['yellow','déficit 8,4 mm','sonda ativa · Pivô 1 · 95 ha · 150 L/s'],'P2':['yellow','déficit 11,2 mm','sonda ativa · Pivô 2 · 80 ha · 166 L/s'],
            'T7':['cloud','sonda sem dado · ≈10 mm est.','sonda sem dado desde 20/09 06:00 · Gotejo T7 · 42 ha · 233 L/s']},
     # programação de hoje: blue = liberada hoje · yellow = aguardando decisão (só fertirrigação) · red = pendência operacional (janela ou conflito)
     'prog':{'P2':['blue','OS-0419 · 20:00–10:31','OS-0419 liberada pela necessidade do balanço · 10,81 mm · hoje 20:00–amanhã 10:31 (14,5 h)'],
             'P1':['yellow','OS-0418 · aguarda agrônomo','OS-0418 fertirrigação 24/09 21:00–25/09 11:15 (14,3 h) · produto na água · aguarda o agrônomo'],
             'T7':['red','OS-0423 · Conflito · parada da B3','OS-0423 · conflito com a parada da B3 (14:00–15:00) · dono Caio · PCP']}}
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
LCOR_OP={'ok':('#7FAE68','#FFFFFF'),'good':('#5F8F55','#FFFFFF'),'lime':('#A9C06A','#FFFFFF'),'yellow':('#D4B25A','#FFFFFF'),'orange':('#D98A4E','#FFFFFF'),'red':('#C8553D','#FFFFFF'),'gray':('#C9CFCB','#FFFFFF'),'blue':('#6E9FC6','#FFFFFF'),'navy':('#44739A','#FFFFFF'),'none':('#E4E9DF','#FFFFFF'),'cloud':('#C9CFCB','#FFFFFF'),'purple':('#9B8BC4','#FFFFFF')}
NOME_LAY={'MIP/MID':'Pragas e doenças','O.S./prazos':'Ordens de serviço','Colheita/produtividade':'Colheita e produtividade'}
MDATA=dict(tal={t:dict(ha=TAL[t]['ha'],cult=TAL[t]['cult'],per=PERIM[t]) for t in TIDS},tids=TIDS,lays=LAYS,
           filt={k:[dict(k=a,l=b,o=c) for a,b,c in v] for k,v in FILT.items()},ord=ORD,integ=INTEG,sat=SAT,semcult=SEMCULT,idx=IDX,
           solo=_solo(),attr=ATTR,mip=MIP,irr=IRR,est=EST,col=COL,cus=_cus(),prox=_proxima(),geo=_geo(),lc=LCOR,lcop=LCOR_OP,nome=NOME_LAY)

MAP_JS=r'''
const IDXN=['NDVI','NDRE','EVI','NDWI'];
const SEV=['red','orange','yellow','cloud','lime','ok','good','navy','blue','purple','gray','none'];
const PZC={'atrasada':'red','vence hoje':'orange','até 3 dias':'yellow','no prazo':'ok','irrigando hoje':'blue','encerrada':'gray'};
const FCOR={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray'};
const CCH={red:'red',orange:'orange',yellow:'yellow',cloud:'gray',lime:'green',ok:'green',good:'green',navy:'blue',blue:'blue',purple:'blue',gray:'gray',none:'gray'};
function worstC(cs){ let b='none',bi=99; cs.forEach(c=>{ const i=SEV.indexOf(c); if(i>=0&&i<bi){ bi=i; b=c; } }); return b; }
function thr(v,tt){ for(const x of tt){ if(x[0]===null||v<x[0]) return x[1]; } return 'none'; }
function thrL(v,tt){ for(const x of tt){ if(x[0]===null||v<x[0]) return x[2]; } return ''; }
function lay(self){ return self.state.lay||'Integrado'; }
function flt(self,l){ const d={}; (M.filt[l]||[]).forEach(g=>{ d[g.k]=g.o[0]; }); return Object.assign(d,((self.state.flt||{})[l])||{}); }
function ordsOf(t,fase){ return M.ord.filter(o=>o.tal.indexOf(t)>=0 && (!fase||fase==='Todas'||o.fase===fase)); }
function satVal(dt,t,ix){ const s=M.sat[dt]; const x=s.v[t]; if(x===undefined) return null; if(x==='cloud') return 'cloud'; return x[IDXN.indexOf(ix)]; }
function satPrev(dt,t,ix){ const ds=Object.keys(M.sat); const i=ds.indexOf(dt); for(let j=i+1;j<ds.length;j++){ const v=satVal(ds[j],t,ix); if(typeof v==='number') return [ds[j],v]; } return null; }
function mipRecs(t,f){ return M.mip.filter(r=>r.t===t && (f.alvo==='Todos'||r.alvo===f.alvo) && (f.per==='30 dias'||r.d<=7)); }
function cusVal(t,f){ const c=M.cus[t]; if(f.grp==='Todos') return [c.orc,c.real]; const g=c.g[f.grp]; return [g[0],g[1]]; }
function money(n){ return 'R$ '+nfx(n,0); }
// ---- ordens do mapa = registro + cenário compartilhado (fase, realizado, saldo e custódia iguais às telas O.S., Estoque e App) ----
const ORD0=M.ord;
function mapSc(it){ const m=/saco (\d+) kg/.exec(it.emb||''); return (m&&it.un==='kg')?nfx(it.custodia/Number(m[1]),0)+' sc':nfx(it.custodia,it.custodia%1?1:0)+' '+it.un; }
let MAPC=null;  // cenário lido nesta renderização (decisões do agrônomo)
// turno fechado sem sinal: o consumo ainda está no aparelho; o Mapa vê consumo e área juntos, quando o app envia (igual às telas O.S. e Estoque)
function mapItVis(co,it){ if(typeof CEN_BAIXA_NO_SINAL!=='undefined') return it;
  const q=Math.min((co.ap||[]).filter(a=>a.sinc===false).reduce((s,a)=>s+(Number((a.cons||{})[it.prod])||0),0),it.consumido||0);
  return q>1e-9?Object.assign({},it,{consumido:it.consumido-q,custodia:it.custodia+q}):it; }
function mapOrdsCen(){ let c=null; try{ c=cenGet(); }catch(e){ c=null; } MAPC=c;
  return ORD0.map(o=>{ const co=c&&c.ordens?c.ordens[o.id]:null; const x=Object.assign({},o,{selos:o.selos.slice()});
    let cust=[];
    // selos = os da ordem no cenário (os mesmos da tela O.S.): aprovação, devolução e rejeição do agrônomo aparecem aqui também
    if(co&&co.selos) x.selos=co.selos.map(s=>[s.t,s.c||'yellow']);
    if(co){ x.fase=co.etapa; x.saldo=co.saldo||0; const area=co.area||o.area;
      let real=nfx(co.realizado||0,(co.realizado||0)%1?1:0)+'/'+nfx(area)+' ha'; if(co.realizado>0&&co.saldo>0) real+=' · saldo '+nfx(co.saldo,co.saldo%1?1:0)+' ha';
      if(o.suf) real+=' · '+o.suf;
      const r=co.req&&c.reqs?c.reqs[co.req]:null; cust=r?r.itens.map(i=>mapItVis(co,i)).filter(i=>i.custodia>0.001):[];
      if(cust.length) real+=' · '+cust.map(mapSc).join(' + ')+' em custódia';
      if((co.ap||[]).some(a=>a.sinc===false)) real+=' · apontamento aguardando sinal';
      x.real=real;
      if(!cust.length) x.selos=x.selos.filter(s=>!/^Sobras a receber/i.test(s[0])); }  // sobra recebida no Estoque: igual à tela O.S.
    // conferência bloqueada pelo cenário (mesma regra da tela O.S.): apontamento aguardando sinal ou sobra em custódia → selo e atalho
    let bq='';
    if(co&&co.etapa==='Em conferência'){ try{ bq=cenPodeEncerrar(c,o.id)||''; }catch(e){ bq=''; } x.selos=x.selos.filter(s=>!/^Aguardando sinal do app/.test(s[0]));
      if(/sinal/.test(bq)) x.selos=x.selos.filter(s=>!/^Sobras a receber/i.test(s[0])).concat([['Aguardando sinal do app','yellow']]);
      else if(bq&&!x.selos.some(s=>/^Sobras a receber/i.test(s[0]))) x.selos=x.selos.concat([['Sobras a receber','yellow']]); }
    if(x.fase!=='A liberar') x.selos=x.selos.filter(s=>!/^(Aguardando(?! sinal do app)|Aprovada)/.test(s[0]));
    if(x.fase==='Encerradas'||x.fase==='Canceladas') x.pz='encerrada';
    const a=o.act; x.act=(!a||(a.c==='ag'&&!inPendAg(c,o.id))||(a.c==='cust'&&co&&!cust.length))?null:a;
    if(bq&&!/sinal/.test(bq)&&cust.length&&!x.act) x.act={t:'Receber sobras',h:'EST.dc.html',k:'op',c:'cust'};
    return x; }); }
function realCurto(id){ const o=M.ord.find(x=>x.id===id); return o?o.real.split(' · ')[0]:''; }
// Integrado: condição do talhão + decisão do agrônomo pendente (amarelo quando nada pior acontece no talhão)
function integ(t){ const x=M.integ[t];
  let lb=x[1].replace(/\{\?(OS-\d+)([^}]*)\}/g,(m,id,tx)=>inPendAg(MAPC,id)?tx:'').replace(/\{(OS-\d+)\}/g,(m,id)=>realCurto(id));
  const dec=M.ord.find(o=>o.tal.indexOf(t)>=0&&o.act&&o.act.k==='dec');
  if(dec&&['ok','gray','blue','none'].indexOf(x[0])>=0) return ['yellow',dec.id+' aguarda agrônomo'];
  return [x[0],lb]; }
// ---- classe e rótulo de cada talhão na camada ativa ----
function cls(l,f,t){
  if(l==='Integrado'){ const x=integ(t); if(f.mostrar==='Só pendências' && ['ok','gray','blue','none'].indexOf(x[0])>=0) return {c:'none',l:'sem pendência'}; return {c:x[0],l:x[1]}; }
  if(l==='Satélite'){ const v=satVal(f.dt,t,f.idx); if(v===null) return {c:'gray',l:M.semcult[t]||'sem cultura'}; if(v==='cloud') return {c:'cloud',l:'nuvem · sem leitura'};
    return {c:thr(v,M.idx[f.idx]),l:f.idx+' '+nfx(v,2)}; }
  if(l==='Solo'){ const a=M.attr[f.attr]; const v=M.solo[f.camp][f.prof][t][f.attr]; return {c:thr(v,a.t),l:(f.attr==='V%'?'V ':f.attr+' ')+nfx(v,a.d)+(f.attr==='V%'?' %':'')}; }
  if(l==='MIP/MID'){ const rs=mipRecs(t,f); if(!rs.length) return {c:'none',l:'sem registro'}; const c=worstC(rs.map(r=>r.c)); const r=rs.find(x=>x.c===c); return {c,l:r.alvo+' · '+r.res.split(' · ')[0]}; }
  if(l==='O.S./prazos'){ const os=ordsOf(t,f.fase); if(!os.length) return {c:'none',l:'sem ordem'+(f.fase==='Todas'?'':' na fase')}; const c=worstC(os.map(o=>PZC[o.pz])); const o=os.find(x=>PZC[x.pz]===c);
    return {c,l:o.id+' · '+o.pz+(os.length>1?' · +'+(os.length-1):'')}; }
  if(l==='Irrigação'){ const k=f.vis==='Balanço hídrico'?'bal':'prog'; const x=M.irr[k][t]; if(!x) return {c:'none',l:k==='bal'?'sequeiro':'sem programação'}; return {c:x[0],l:x[1]}; }
  if(l==='Estádio'){ const e=M.est[t]; if(f.cult!=='Todas' && e.cult!==f.cult) return {c:'none',l:e.cult+' · fora do filtro'}; return {c:e.c,l:e.l}; }
  if(l==='Colheita/produtividade'){ const x=((M.col[f.safra]||{})[f.vis]||{})[t]; if(!x) return {c:'none',l:'sem dado'}; return {c:x[0],l:x[1]}; }
  if(l==='Custos'){ const cv=cusVal(t,f); const dv=(cv[1]-cv[0])/cv[0]*100; const c=dv<=0?'ok':(dv<=10?'yellow':'red');
    return {c,l:f.most==='Desvio do orçado'?((dv>0?'+':'−')+nfx(Math.abs(dv),1)+' %'):(money(cv[1])+'/ha')}; }
  return {c:'none',l:''}; }
function PAL(l){ return (l==='Satélite'||l==='Solo')?M.lc:M.lcop; }
function legend(l,f){
  const L=(c,t)=>({t,st:'display:inline-flex;align-items:center;gap:5px;white-space:nowrap;',dot:'width:11px;height:11px;border-radius:3px;flex-shrink:0;'+(c==='cloud'?'background:repeating-linear-gradient(45deg,#C9CFCB 0 3px,#9E9E9E 3px 5px);':'background:'+PAL(l)[c][0]+';')+'border:1px solid '+PAL(l)[c][1]+';'});
  if(l==='Integrado') return [L('ok','em dia'),L('yellow','atenção ou decisão pendente'),L('red','impedida, conflito ou acima do NC'),L('gray','encerrada'),L('none','sem pendência')];
  if(l==='Satélite') return M.idx[f.idx].map(x=>L(x[1],x[2])).concat([L('gray','sem cultura'),L('cloud','nuvem')]);
  if(l==='Solo') return M.attr[f.attr].t.map(x=>L(x[1],x[2]+(M.attr[f.attr].u&&M.attr[f.attr].u!=='%'?' '+M.attr[f.attr].u:'')));
  if(l==='MIP/MID') return [L('red','acima do nível de controle'),L('orange','foco em investigação'),L('yellow','atenção'),L('ok','abaixo do nível'),L('none','sem registro')];
  if(l==='O.S./prazos') return [L('red','atrasada'),L('orange','vence hoje'),L('yellow','até 3 dias'),L('ok','no prazo'),L('blue','irrigando hoje'),L('gray','encerrada'),L('none','sem ordem')];
  if(l==='Irrigação') return f.vis==='Balanço hídrico'?[L('ok','< 6 mm em dia'),L('yellow','6–12 mm déficit'),L('red','≥ 12 mm crítico'),L('cloud','sem dado de sonda'),L('none','sequeiro')]
                                                   :[L('blue','liberada hoje'),L('yellow','aguardando decisão (só fertirrigação)'),L('red','pendência operacional (janela ou conflito)'),L('none','sem programação')];
  if(l==='Estádio') return [L('gray','pré-plantio'),L('ok','vegetativo'),L('purple','reprodutivo'),L('yellow','produção contínua'),L('orange','enchimento/maturação'),L('none','colhido ou fora do filtro')];
  if(l==='Colheita/produtividade') return [L('good','acima da meta'),L('ok','na meta'),L('red','abaixo da meta'),L('lime','previsão'),L('none','sem dado')];
  if(l==='Custos') return [L('ok','dentro do orçado'),L('yellow','até +10 %'),L('red','acima de +10 %')];
  return []; }
function fonte(l,f){
  if(l==='Integrado') return 'O.S. do PCP 23/09 06:40 · satélite 21/09 · vistorias até 22/09';
  if(l==='Satélite') return 'Sentinel-2 L2A · 10 m · cena '+f.dt+' · nuvem '+M.sat[f.dt].nuvem+' % · escala absoluta da fazenda · mancha é indício, não diagnóstico';
  if(l==='Solo') return 'Lab Solo Vale · campanha '+f.camp+' · '+f.prof+' · '+M.attr[f.attr].m+' · 1 ponto/5 ha';
  if(l==='MIP/MID') return 'vistorias do MIP · últimos '+f.per+' · contagem × nível de controle da cultura';
  if(l==='O.S./prazos') return 'O.S. do PCP · 23/09 06:40 · prazo pela janela de cada ordem';
  if(l==='Irrigação') return f.vis==='Balanço hídrico'?'balanço hídrico 23/09 06:00 · sondas P1/P2/T7 · estação Sede':'programação de hoje · lâmina pela necessidade do balanço · liberação pela prontidão operacional';
  if(l==='Estádio') return 'ocupações e fenologia apontadas até 22/09 · variedade por ocupação';
  if(l==='Colheita/produtividade') return 'romaneios conferidos e previsões publicadas · safra '+f.safra;
  if(l==='Custos') return 'custo realizado × orçado · '+f.grp.toLowerCase()+' · fechamento parcial 22/09';
  return ''; }
function strip(self,l,f){ const N=(k,val)=>({k,val}); const tids=M.tids; const area=(ts)=>ts.reduce((a,t)=>a+M.tal[t].ha,0);
  if(l==='Integrado'){ const ab=M.ord.filter(o=>o.fase!=='Encerradas'); return [N('Área',nfx(area(tids))+' ha'),N('Ordens abertas',ab.length),N('Impedidas',M.ord.filter(o=>o.selos.some(s=>/^(Impedida|Falta máquina)/.test(s[0]))).length),N('Decisões pendentes',M.ord.filter(o=>o.act&&o.act.k==='dec').length)]; }
  if(l==='Satélite'){ let s=0,a=0,n=0; tids.forEach(t=>{ const v=satVal(f.dt,t,f.idx); if(typeof v==='number'){ s+=v*M.tal[t].ha; a+=M.tal[t].ha; } if(v==='cloud') n++; });
    const ms=M.sat[f.dt].manchas; return [N(f.idx+' médio (com cultura)',a?nfx(s/a,2):'—'),N('Manchas',ms.length?ms.length+' · '+nfx(ms.reduce((x,m)=>x+m.ha,0),1)+' ha':'nenhuma'),N('Nuvem na cena',M.sat[f.dt].nuvem+' %'),N('Sem leitura',n+(n===1?' talhão':' talhões'))]; }
  if(l==='Solo'){ let s=0; const low=[]; tids.forEach(t=>{ const v=M.solo[f.camp][f.prof][t][f.attr]; s+=v*M.tal[t].ha; if(thr(v,M.attr[f.attr].t)==='red') low.push(t); });
    return [N('Média ponderada',nfx(s/area(tids),M.attr[f.attr].d)+' '+M.attr[f.attr].u),N('Baixo',low.length?low.join(', ')+' · '+nfx(area(low))+' ha':'nenhum'),N('Laudos',tids.length),N('Coleta',M.solo[f.camp][f.prof].T1.dt)]; }
  if(l==='MIP/MID'){ const rs=M.mip.filter(r=>(f.alvo==='Todos'||r.alvo===f.alvo)&&(f.per==='30 dias'||r.d<=7)); return [N('Acima do NC',rs.filter(r=>r.c==='red').length),N('Em investigação',rs.filter(r=>r.c==='orange').length),N('Vistorias no período',rs.length),N('Última',rs.length?rs.map(r=>r.dt).sort((a,b)=>a.split('/').reverse().join('')<b.split('/').reverse().join('')?1:-1)[0]:'—')]; }
  if(l==='O.S./prazos'){ const os=M.ord.filter(o=>f.fase==='Todas'||o.fase===f.fase); return [N('Ordens',os.length),N('Atrasadas',os.filter(o=>o.pz==='atrasada').length),N('Vencem hoje',os.filter(o=>o.pz==='vence hoje').length),N('Saldo a executar',nfx(os.reduce((a,o)=>a+(o.saldo||0),0))+' ha')]; }
  if(l==='Irrigação'){ return [N('Área irrigada','217 ha'),N('Em déficit','3 setores'),N('Programadas hoje','2 ordens'),N('Sem dado de sonda','T7')]; }
  if(l==='Estádio'){ const ts=tids.filter(t=>f.cult==='Todas'||M.est[t].cult===f.cult); const byc=(cs)=>nfx(area(ts.filter(t=>cs.indexOf(M.est[t].c)>=0)))+' ha';
    return [N('Área no filtro',nfx(area(ts))+' ha'),N('Pré-plantio',byc(['gray'])),N('Vegetativo/reprodutivo',byc(['ok','purple'])),N('Produção/maturação',byc(['yellow','orange']))]; }
  if(l==='Colheita/produtividade'){ const d=(M.col[f.safra]||{})[f.vis]||{}; const ks=Object.keys(d); return [N('Talhões com dado',ks.length),N('Acima da meta',ks.filter(t=>d[t][0]==='good').length),N('Na meta',ks.filter(t=>d[t][0]==='ok').length),N('Abaixo da meta',ks.filter(t=>d[t][0]==='red').length)]; }
  if(l==='Custos'){ let o=0,r=0,n=0; tids.forEach(t=>{ const cv=cusVal(t,f); o+=cv[0]*M.tal[t].ha; r+=cv[1]*M.tal[t].ha; if(cv[1]>cv[0]*1.10) n++; });
    return [N('Realizado','R$ '+nfx(r/1000,0)+' mil'),N('Orçado','R$ '+nfx(o/1000,0)+' mil'),N('Desvio',(r>=o?'+':'−')+nfx(Math.abs(r-o)/o*100,1)+' %'),N('Acima de +10 %',n+(n===1?' talhão':' talhões'))]; }
  return []; }
// ---- ações do painel (ícone + rótulo + title) ----
const ICN=['doc','alert','drop','leaf','map','trend','cash','lab','check','calendar','layers'];
function A(t,o){ const a={t,tt:o.tt||t,isH:!!o.h,isF:!!o.fn,h:o.h||'#',fn:o.fn||(()=>{}),
  st:(o.prim?'background:#1E7A4C;color:#fff;border:1px solid #1E7A4C;':'background:#FFFFFF;color:#15201A;border:1px solid #E4E9E5;')+'display:inline-flex;align-items:center;gap:6px;padding:6px 11px;border-radius:9px;font-size:12.5px;font-weight:700;text-decoration:none;white-space:nowrap;cursor:pointer;font-family:inherit;line-height:1.25;'};
  ICN.forEach(n=>{ a['i_'+n]=(o.ic===n); }); return a; }
function CH(t,c){ return {t,st:chipSt(c)}; }
// cria a vistoria de cada talhão (uma por talhão, nunca duplica) — mesma função no painel, no modo da barra e na seleção múltipla
function visPatch(self,ts){ const cur=Object.assign({},self.state.vis||{}); const nov=[], ja=[];
  ts.forEach(t=>{ if(cur[t]){ ja.push(cur[t]+' já está criada para '+t); return; } cur[t]='VIS-0'+(18+Object.keys(cur).length); nov.push(t); });
  const mancha=(t)=>Object.keys(M.sat).some(d=>M.sat[d].manchas.some(m=>m.t===t));
  const ponto=nov.length===1?(' · ponto de vistoria no '+(mancha(nov[0])?'centroide da mancha':'centro do talhão')):(nov.length?' · um ponto de vistoria em cada talhão':'');
  const msg=nov.map(t=>cur[t]+' criada para '+t).concat(ja).join(' · ')+ponto+(nov.length?' · aparece em Monitoramento e vistorias e no app de Marcos.':'')+(ja.length?' · nenhuma vistoria duplicada.':'');
  return {vis:cur,g2toast:msg}; }
function criarVis(self,ts,extra){ self.setState(Object.assign(visPatch(self,ts),extra||{})); }
// ação da ordem: decisão do agrônomo ou pendência operacional (com o atalho para onde se resolve); se o atalho é o próprio destino da ordem, vira a ação única
function ordItem(o){ const a=o.act; const ic=a&&a.k==='dec'?'check':'drop';
  const acts=(a&&a.h===o.h)?[A(a.t,{h:a.h,ic,tt:a.t+' · '+o.id})]:[A('Abrir ordem',{h:o.h,ic:'doc',tt:'Abrir '+o.id})].concat(a?[A(a.t,{h:a.h,ic:a.k==='dec'?'check':'doc',tt:a.t+' · '+o.id})]:[]);
  return {t:o.id+' · '+o.tipo, sub:'Janela '+o.jan+' · '+o.real+' · '+(o.dono?'dono: '+o.dono:o.resp), ch:[CH(o.fase,FCOR[o.fase])].concat(o.selos.map(s=>CH(s[0],s[1]))).concat([CH(o.pz,CCH[PZC[o.pz]])]), acts}; }
function panel(self,l,f,sel){
  const P={title:'',sub:'',ch:[],kv:[],secs:[],note:'',acts:[]};
  if(sel.length>1){ const ha=sel.reduce((a,t)=>a+M.tal[t].ha,0); P.title='Área selecionada · '+sel.length+' talhões'; P.sub=sel.join(' + ')+' · '+nfx(ha)+' ha · camada '+l;
    const vs=self.state.vis||{};
    P.secs.push({t:'Talhões',items:sel.map(t=>{ const c=cls(l,f,t); return {t:t+' · '+M.tal[t].cult+' · '+nfx(M.tal[t].ha)+' ha',sub:'',ch:[CH(c.l,CCH[c.c])].concat(vs[t]?[CH(vs[t],'green')]:[]),acts:[]}; })});
    const os=M.ord.filter(o=>o.tal.some(t=>sel.indexOf(t)>=0)); P.secs.push({t:'Ordens na área selecionada · '+os.length,items:os.map(o=>ordItem(o))});
    P.acts=[A('Criar vistoria nas áreas',{fn:()=>criarVis(self,sel),ic:'alert',prim:true,tt:'Criar uma vistoria por talhão: '+sel.join(', ')}),A('Limpar seleção',{fn:()=>self.setState({tsel:[]}),ic:'map'})]; return P; }
  const t=sel[0], T=M.tal[t], c=cls(l,f,t), e=M.est[t];
  P.title=t+' · '+e.ocup; P.sub=nfx(T.ha)+' ha · '+e.est+' · camada '+l; P.ch=[CH(c.l,CCH[c.c])];
  const vis=(self.state.vis||{})[t];
  const cv=()=>criarVis(self,[t]);
  const visAct=()=>vis?A('Abrir '+vis,{h:'AG-01.dc.html',ic:'alert',prim:true,tt:'Abrir a vistoria criada'}):A('Criar vistoria',{fn:cv,ic:'alert',prim:true,tt:'Criar vistoria com ponto de GPS neste talhão'});
  if(l==='Integrado'||l==='O.S./prazos'){
    const os=ordsOf(t,l==='O.S./prazos'?f.fase:'Todas');
    if(l==='Integrado'){ const sv=satVal('21/09',t,'NDVI'); const mr=mipRecs(t,{alvo:'Todos',per:'7 dias'}); const ib=M.irr.bal[t]; const cu=M.cus[t];
      P.kv=[{l:'Ocupação',t:e.ocup+' · '+e.est},{l:'Satélite 21/09',t:sv===null?(M.semcult[t]||'sem cultura'):(sv==='cloud'?'nuvem · sem leitura':'NDVI '+nfx(sv,2))},
            {l:'MIP',t:mr.length?mr.map(r=>r.alvo+' '+r.res.split(' · ')[0]).join(' · '):'sem registro em 7 dias'},{l:'Irrigação',t:ib?ib[1]:'sequeiro'},{l:'Custo',t:money(cu.real)+'/ha · orçado '+money(cu.orc)}]
        .concat(M.geo[t]?[{l:'Geometria',t:M.geo[t]}]:[]); }
    const its=os.map(o=>ordItem(o));
    P.secs.push({t:(os.length?'Ordens do talhão · '+os.length:'Nenhuma ordem'+(l==='O.S./prazos'&&f.fase!=='Todas'?' na fase '+f.fase:'')),items:its});
    const urg=os.slice().sort((a,b)=>SEV.indexOf(PZC[a.pz])-SEV.indexOf(PZC[b.pz]))[0];
    if(urg&&urg.fase!=='Encerradas'){
      // primário = próximo passo da ordem mais urgente (a ação dela ou abrir a ordem); o item dela não repete o mesmo destino
      const ua=urg.act; const pa=ua?A(ua.t,{h:ua.h,ic:ua.k==='dec'?'check':'drop',prim:true,tt:ua.t+' · '+urg.id+' (a mais urgente do talhão)'}):A('Abrir '+urg.id,{h:urg.h,ic:'doc',prim:true,tt:'Abrir a ordem mais urgente do talhão'});
      its[os.indexOf(urg)].acts=its[os.indexOf(urg)].acts.filter(a=>a.h!==pa.h);
      P.acts=[pa,A('Criar vistoria',{fn:cv,ic:'alert'})]; }
    else P.acts=[visAct(),A('Nova ordem',{h:'OS.dc.html',ic:'doc',tt:'Abrir Ordem de Serviço'})];
    return P; }
  if(l==='Satélite'){ const v=satVal(f.dt,t,f.idx); const nt=(M.sat[f.dt].nt||{})[t]||0;
    if(v===null){ P.kv=[{l:'Leitura',t:(M.semcult[t]||'sem cultura')+' · o índice não indica vigor'},{l:'Cena',t:'Sentinel-2 · '+f.dt}]; P.acts=[A('Ver histórico',{h:'AG-06.dc.html',ic:'trend',tt:'Abrir histórico agronômico'})]; return P; }
    if(v==='cloud'){ P.kv=[{l:'Nuvem no talhão',t:nt+' % · sem cor de condição atual'},{l:'Próxima passagem',t:'26/09 (prevista)'}]; P.note='Nuvem e dado antigo não recebem cor de condição atual. Escolha outra cena no filtro acima.'; P.acts=[A('Ver histórico',{h:'AG-06.dc.html',ic:'trend'})]; return P; }
    const pv=satPrev(f.dt,t,f.idx); const dv=pv?(v-pv[1])/pv[1]*100:null; const ms=M.sat[f.dt].manchas.filter(m=>m.t===t);
    const estado=ms.some(m=>m.ha>1&&m.evo.indexOf('nova')===0)||(dv!==null&&dv<-15)?'Crítico':(ms.length||(dv!==null&&dv<-10)?'Atenção':'Normal');
    P.ch=[CH(f.idx+' '+nfx(v,2)+' · '+thrL(v,M.idx[f.idx]).replace(/^[^a-z]*/,''),CCH[c.c]),CH('Estado: '+estado,estado==='Crítico'?'red':(estado==='Atenção'?'yellow':'green'))];
    P.kv=[{l:'Índice médio',t:f.idx+' '+nfx(v,2)},{l:'Variação',t:pv?((dv>=0?'+':'−')+nfx(Math.abs(dv),0)+' % vs '+pv[0]):'sem cena anterior válida'},{l:'Nuvem no talhão',t:nt+' %'},{l:'Cena',t:'Sentinel-2 L2A · '+f.dt+' · 10 m'}];
    P.secs.push({t:ms.length?'Manchas detectadas · '+ms.length:'Nenhuma mancha nesta cena',items:ms.map(m=>({t:nfx(m.ha,1)+' ha · NDVI '+nfx(m.val,2)+' · '+m.evo,sub:'Centroide '+m.coord+' · tipo provável: '+m.tipo+' · indício para inspeção, não diagnóstico',ch:[CH(nfx(m.ha/T.ha*100,1)+' % do talhão','red')],acts:[]}))});
    P.acts=ms.length?[visAct(),A('Ver histórico',{h:'AG-06.dc.html',ic:'trend',tt:'Abrir histórico agronômico'})]:[A('Ver histórico',{h:'AG-06.dc.html',ic:'trend',prim:true,tt:'Abrir histórico agronômico'})]; return P; }
  if(l==='Solo'){ const s=M.solo[f.camp][f.prof][t];
    P.kv=[{l:'Laudo',t:s.lau+' · Lab Solo Vale'},{l:'Coleta',t:s.dt+' · '+f.prof+' · 1 ponto/5 ha'}];
    P.secs.push({t:'Resultados do laudo',items:Object.keys(M.attr).map(k=>{ const a=M.attr[k]; const val=s[k]; const cc=thr(val,a.t);
      return {t:a.n+': '+nfx(val,a.d)+(a.u?' '+a.u:''),sub:a.m+(k===f.attr?' · atributo no mapa':''),ch:[CH(thrL(val,a.t).split(' ').slice(-1)[0],CCH[cc])],acts:[]}; })});
    P.acts=[A('Ver recomendação',{h:(t==='T4'?'AG-04det.dc.html':'AG-04.dc.html'),ic:'leaf',prim:true,tt:'Abrir a recomendação que usa este laudo'}),A('Abrir análises',{h:'AG-02.dc.html',ic:'lab',tt:'Abrir Análises e amostras'})]; return P; }
  if(l==='MIP/MID'){ const rs=mipRecs(t,f);
    P.secs.push({t:rs.length?'Vistorias no período · '+rs.length:'Sem vistoria no período',items:rs.map(r=>({t:r.id+' · '+r.txt,sub:r.dt+' · '+r.met,ch:[CH(r.res,CCH[r.c])],acts:[A('Abrir vistoria',{h:r.h,ic:'doc',tt:'Abrir '+r.id})]}))});
    const d=rs.find(r=>r.diag); P.acts=d?[A('Criar diagnóstico',{h:'AG-03.dc.html',ic:'leaf',prim:true,tt:'Criar diagnóstico a partir de '+d.id}),A('Criar vistoria',{fn:cv,ic:'alert'})]:[visAct()]; return P; }
  if(l==='Irrigação'){ const b=M.irr.bal[t], pg=M.irr.prog[t];
    if(!b&&!pg){ P.kv=[{l:'Sistema',t:'sequeiro · sem irrigação'}]; P.acts=[A('Ver balanço hídrico',{h:'IR-01.dc.html',ic:'drop'})]; return P; }
    P.kv=[{l:'Balanço 23/09 06:00',t:b?b[1]:'—'},{l:'Sistema',t:b?b[2]:'—'}].concat(pg?[{l:'Hoje',t:pg[2]}]:[]);
    const os=ordsOf(t,'Todas').filter(o=>o.tipo.indexOf('rriga')>=0);
    P.secs.push({t:'Programação · '+os.length,items:os.map(o=>ordItem(o))});
    if(b&&b[0]==='cloud') P.note='Sonda sem dado: o déficit é estimado pela ET e não recebe cor de condição atual.';
    P.acts=[A('Abrir irrigação de hoje',{h:'IR-03.dc.html',ic:'drop',prim:true,tt:'Abrir Ordens de irrigação'}),A('Ver balanço',{h:'IR-01.dc.html',ic:'trend',tt:'Abrir Balanço hídrico'})]; return P; }
  if(l==='Estádio'){ P.kv=[{l:'Ocupação atual',t:e.ocup},{l:'Variedade',t:e.var},{l:'Estádio',t:e.est},{l:'Plantio',t:e.plant},{l:'Colheita',t:e.col}];
    P.secs.push({t:'Próxima ocupação · Safra 2026/27',items:(M.prox[t]||[]).map(x=>({t:x,sub:'',ch:[],acts:[]}))});
    P.acts=[A('Abrir safra',{h:'SAF.dc.html',ic:'calendar',prim:true,tt:'Abrir Planejar safra'}),A('Ver plano',{h:'PA.dc.html',ic:'leaf',tt:'Abrir Planos agronômicos'})]; return P; }
  if(l==='Colheita/produtividade'){ const x=((M.col[f.safra]||{})[f.vis]||{})[t];
    P.kv=[{l:f.vis,t:x?x[1]:'sem dado nesta safra'},{l:'Detalhe',t:x?x[2]:'—'},{l:'Área',t:nfx(T.ha)+' ha'}];
    P.acts=[A(f.vis==='Realizado'?'Ver romaneios':'Ver previsão',{h:f.vis==='Realizado'?'CO-03.dc.html':'CO-01.dc.html',ic:'trend',prim:true})]; return P; }
  if(l==='Custos'){ const cu=M.cus[t]; const dv=(cu.real-cu.orc)/cu.orc*100;
    P.kv=[{l:'Realizado',t:money(cu.real)+'/ha · '+money(cu.real*T.ha/1000)+' mil'},{l:'Orçado',t:money(cu.orc)+'/ha'},{l:'Desvio',t:(dv>=0?'+':'−')+nfx(Math.abs(dv),1)+' %'}];
    P.secs.push({t:'Por grupo (R$/ha)',items:Object.keys(cu.g).map(g=>{ const x=cu.g[g]; const d=(x[1]-x[0])/x[0]*100; return {t:g+': '+money(x[1])+' · orçado '+money(x[0]),sub:'',ch:[CH((d>=0?'+':'−')+nfx(Math.abs(d),1)+' %',d<=0?'green':(d<=10?'yellow':'red'))],acts:[]}; })});
    if(t==='T4') P.note='Desvio puxado por máquinas: reparo da OM-0233 e trator substituto.';
    P.acts=[A('Abrir custos',{h:'GE-03.dc.html',ic:'cash',prim:true,tt:'Abrir Custos e fechamento'})]; return P; }
  return P; }
function MAPVALS(self,v){
  M.ord=mapOrdsCen();
  const st=self.state; const l=lay(self); const f=flt(self,l); const sel=(st.tsel||[]).filter(t=>M.tids.indexOf(t)>=0);
  v.lays=M.lays.map(x=>({t:x,on:x===l?'true':'false',go:()=>self.setState({lay:x,cvis:false}),
    st:'font-family:inherit;font-size:12px;font-weight:700;padding:5px 11px;border-radius:999px;cursor:pointer;white-space:nowrap;'+(x===l?'border:1px solid #15201A;background:#15201A;color:#fff;':'border:1px solid #E4E9E5;background:#FFFFFF;color:#15201A;')}));
  v.flt=(M.filt[l]||[]).map(g=>({l:g.l,opts:g.o.map(o=>({t:o,on:(f[g.k]===o)?'true':'false',go:()=>{ const all=Object.assign({},self.state.flt||{}); all[l]=Object.assign({},all[l]||{},{[g.k]:o}); self.setState({flt:all}); },
    st:'font-family:inherit;font-size:11.8px;font-weight:700;padding:4px 9px;border:0;border-radius:7px;cursor:pointer;white-space:nowrap;'+(f[g.k]===o?'background:#1E7A4C;color:#fff;':'background:transparent;color:#15201A;')}))}));
  v.fonte=fonte(l,f); v.leg=legend(l,f); v.nums=strip(self,l,f); v.lay_t=(M.nome[l]||l); v.hint=v.lay_t+' · clique no talhão para ver detalhes e ações'; const z=st.zoom||1; v.zst='transform:scale('+z+');transform-origin:50% 50%;transition:transform .2s;width:100%;height:100%;'; v.zin=()=>self.setState({zoom:Math.min(2,(self.state.zoom||1)+0.25)}); v.zout=()=>self.setState({zoom:Math.max(1,(self.state.zoom||1)-0.25)});
  // atalho da funcionalidade na barra horizontal; no MIP/MID é o modo "Criar vistoria" (cria de fato, como no painel)
  const FL={'Integrado':['Abrir ordens','OS.dc.html'],'Satélite':['Ver histórico','AG-06.dc.html'],'Solo':['Ver recomendações','AG-04.dc.html'],
    'O.S./prazos':['Abrir ordens','OS.dc.html'],'Irrigação':['Irrigação de hoje','IR-03.dc.html'],'Estádio':['Abrir safra','SAF.dc.html'],'Colheita/produtividade':['Ver previsão','CO-01.dc.html'],'Custos':['Abrir custos','GE-03.dc.html']};
  v.flink=(FL[l]||['',''])[1]; v.flinkt=(FL[l]||['',''])[0]; v.hasFlink=!!FL[l]; v.hasFvis=(l==='MIP/MID');
  const lst=(on)=>'width:96px;box-sizing:border-box;padding:9px 4px;border-radius:12px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;cursor:pointer;font-family:inherit;border:0;'+(on?'background:#1E6B47;color:#FFFFFF;':'background:transparent;color:#4B5A51;');
  M.lays.forEach((x,i)=>{ v['ly'+i+'_st']=lst(x===l); v['ly'+i+'_on']=(x===l)?'true':'false'; v['ly'+i+'_go']=()=>self.setState({lay:x,cvis:false}); });
  const ms=(l==='Satélite')?M.sat[f.dt].manchas:[];
  M.tids.forEach(t=>{ const c=cls(l,f,t); const on=sel.indexOf(t)>=0; const pl=PAL(l); const lc=pl[c.c]||pl.none;
    v['fl_'+t]=c.c==='cloud'?'url(#hatch)':lc[0]; v['fo_'+t]=(c.c==='none'||c.c==='cloud')?'1':'0.88';
    v['sk_'+t]=on?'#15201A':'#FFFFFF'; v['sw_'+t]=on?'6':'4'; v['sub_'+t]=M.tal[t].cult+' · '+nfx(M.tal[t].ha)+' ha'; v['lab_'+t]=c.l; v['al_'+t]=t+': '+c.l;
    const m=ms.find(x=>x.t===t); v['mo_'+t]=m?'1':'0'; v['ml_'+t]=m?(nfx(m.ha,1)+' ha'):'';
    v['tk_'+t]=()=>{ const s=self.state; if(s.medir){ self.setState({g2toast:'Medição · '+t+': '+nfx(M.tal[t].ha)+' ha · perímetro ≈ '+M.tal[t].per+' km (geometria do cadastro).'}); return; }
      if(s.cvis){ criarVis(self,[t],{tsel:[t]}); return; }
      let ss=(s.tsel||[]).slice(); if(s.selm){ const i=ss.indexOf(t); if(i>=0) ss.splice(i,1); else ss.push(t); } else ss=(ss.length===1&&ss[0]===t)?[]:[t]; self.setState({tsel:ss}); };
    v['tkk_'+t]=(e)=>{ if(e&&(e.key==='Enter'||e.key===' ')){ e.preventDefault(); v['tk_'+t](); } }; });
  v.pan_open=sel.length>0; v.pan_close=()=>self.setState({tsel:[]});
  const P=sel.length?panel(self,l,f,sel):{title:'',sub:'',ch:[],kv:[],secs:[],note:'',acts:[]};
  v.pan=P; v.pan_hasnote=!!P.note; v.pan_haskv=P.kv.length>0;
  // barra de funcionalidades
  const rst=(on)=>'display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:10px;cursor:pointer;font-family:inherit;font-size:12px;font-weight:700;color:#15201A;box-shadow:0 1px 3px rgba(21,32,26,.18);'+(on?'border:1px solid #1E7A4C;background:#E4F3E9;':'border:1px solid #E4E9E5;background:#FFFFFF;');
  v.r_selm_st=rst(!!st.selm); v.r_medir_st=rst(!!st.medir); v.r_full_st=rst(!!st.full); v.r_pref_st=rst(!!st.pref); v.r_link_st=rst(false);
  v.r_selm=()=>self.setState({selm:!st.selm,medir:false,cvis:false,g2toast:!st.selm?'Selecionar área: clique nos talhões para somar à seleção; o painel mostra as ordens da área.':'Seleção múltipla desligada.'});
  v.r_medir=()=>self.setState({medir:!st.medir,selm:false,cvis:false,g2toast:!st.medir?'Medir: clique num talhão para ver área e perímetro.':'Medição desligada.'});
  v.r_vis_st='display:inline-flex;align-items:center;gap:6px;padding:5px 10px;border-radius:9px;cursor:pointer;font-family:inherit;font-size:12.5px;font-weight:700;color:#15201A;white-space:nowrap;'+(st.cvis?'border:1px solid #1E7A4C;background:#E4F3E9;':'border:1px solid #E4E9E5;background:#FFFFFF;');
  v.r_vis_on=st.cvis?'true':'false';
  v.r_vis=()=>{ const s=self.state; if(s.cvis){ self.setState({cvis:false,g2toast:'Criar vistoria desligado.'}); return; }
    if(sel.length){ criarVis(self,sel); return; }  // talhão já selecionado: cria direto
    self.setState({cvis:true,selm:false,medir:false,g2toast:'Criar vistoria: clique num talhão para criar a vistoria.'}); };
  v.r_full=()=>self.setState({full:!st.full}); v.full=!!st.full;
  v.r_pref=()=>self.setState({pref:!st.pref,g2toast:!st.pref?'Preferência gravada: o Mapa abre ao entrar (só para você).':'Preferência removida: a entrada volta ao padrão do seu perfil.'});
  v.r_pref_t=st.pref?'Tela inicial ✓':'Usar como inicial';
  v.modo=st.selm?'Selecionar área · clique para somar talhões':(st.medir?'Medir · clique num talhão':(st.cvis?'Criar vistoria · clique num talhão':'')); v.sem_modo=!(st.selm||st.medir||st.cvis); v.has_modo=!!(st.selm||st.medir||st.cvis);
  // filtro Fazenda do topo: só a Santa Rita tem geometria; Boa Vista = estado vazio no lugar do mapa; Todas = Santa Rita + aviso
  const faz=st.mf_faz||'Santa Rita'; const semGeo=(faz==='Boa Vista');
  v.map_on=!semGeo; v.map_vazio=semGeo; v.aviso_bv=(faz==='Todas');
  if(semGeo){ v.nums=[]; v.flt=[]; v.leg=[]; v.fonte='Fazenda Boa Vista · nenhum talhão com geometria'; v.hasFlink=false; v.hasFvis=false; v.pan_open=false; v.has_modo=false; v.sem_modo=false; }
  // estado no cabeçalho (mesmo cálculo dos indicadores)
  const imp=M.ord.filter(o=>o.fase!=='Encerradas'&&o.selos.some(s=>/^(Impedida|Falta máquina)/.test(s[0]))).map(o=>o.id); const nd=M.ord.filter(o=>o.act&&o.act.k==='dec').length;
  const lista=(a)=>a.length>1?a.slice(0,-1).join(', ')+' e '+a[a.length-1]:a.join('');
  v.hs_t=semGeo?'Boa Vista sem talhões desenhados':([imp.length?lista(imp)+(imp.length>1?' impedidas':' impedida'):'',nd?nd+(nd>1?' decisões pendentes':' decisão pendente'):''].filter(Boolean).join(' · ')||'Sem pendências');
  v.hs_st=chipSt(semGeo?'gray':(imp.length?'red':(nd?'yellow':'green')));
}
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
        else:
            cx,cy,r=map(float,geo.split(','))
            g.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" {at}{ev}/>')
            g.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+r*0.7:.0f}" y2="{cy-r*0.7:.0f}" stroke="{H("sk_"+tid)}" stroke-width="2" style="pointer-events: none;"/>')
        if tid=='T7':
            g.append(f'<ellipse cx="650" cy="556" rx="30" ry="20" fill="#E4002B" stroke="#9E0A1F" stroke-width="2" opacity="{H("mo_T7")}" style="pointer-events: none;"/>'
                     f'<foreignObject x="610" y="547" width="80" height="20" opacity="{H("mo_T7")}" style="pointer-events: none;"><div xmlns="http://www.w3.org/1999/xhtml" style="font-family: Manrope, sans-serif; font-size: 12px; font-weight: 800; color: #fff; text-align: center; line-height: 18px;">{H("ml_T7")}</div></foreignObject>')
        g.append(f'<text x="{cx:.0f}" y="{cy+4:.0f}" text-anchor="middle" font-family="Sora, Manrope, sans-serif" font-size="40" font-weight="700" fill="#15201A" stroke="#fff" stroke-width="6" paint-order="stroke" style="pointer-events: none;">{tid}</text>')
        lw=min(260,int(max(p[0] for p in pts)-min(p[0] for p in pts))-16) if tp=='poly' else int(2*r-24)  # rótulo cabe no talhão (quebra em 2 linhas)
        g.append(f'<foreignObject x="{cx-lw/2:.0f}" y="{cy+12:.0f}" width="{lw}" height="20" style="pointer-events: none;"><div xmlns="http://www.w3.org/1999/xhtml" style="{_SUB}">{H("sub_"+tid)}</div></foreignObject>')
        g.append(f'<foreignObject x="{cx-lw/2:.0f}" y="{cy+32:.0f}" width="{lw}" height="46" style="pointer-events: none;"><div xmlns="http://www.w3.org/1999/xhtml" style="{_LBL}">{H("lab_"+tid)}</div></foreignObject>')
    defs=('<defs><pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#C9CFCB"/>'
          '<line x1="0" y1="0" x2="0" y2="10" stroke="#9E9E9E" stroke-width="4"/></pattern>'
          '<pattern id="grade" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0 L0 0 0 40" fill="none" stroke="#D3DDCB" stroke-width="1"/></pattern></defs>') if defs else ''
    return (f'<svg viewBox="0 0 1000 620" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Mapa da fazenda Santa Rita" style="display: block;">'
            + defs + '<rect width="1000" height="620" fill="url(#grade)"/><path d="M0 314 C 250 308, 520 320, 1000 314" stroke="#FFFFFF" stroke-width="10" fill="none" opacity=".9"/>'
            + '<path d="M318 0 L322 620" stroke="#FFFFFF" stroke-width="7" fill="none" opacity=".8"/>' + ''.join(g) + '</svg>')

def _panel_html():
    def actions(lst,a='a'):
        ic=''.join(f'<sc-if value="{H(a+".i_"+n)}" hint-placeholder-val="{F()}">{icon(n,14)}</sc-if>' for n in ['doc','alert','drop','leaf','map','trend','cash','lab','check','calendar','layers'])
        return (f'<sc-for list="{H(lst)}" as="{a}" hint-placeholder-count="2">'
                f'<sc-if value="{H(a+".isH")}" hint-placeholder-val="{T()}"><a href="{H(a+".h")}" title="{H(a+".tt")}" style="{H(a+".st")}">{ic}{H(a+".t")}</a></sc-if>'
                f'<sc-if value="{H(a+".isF")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H(a+".fn")}" title="{H(a+".tt")}" style="{H(a+".st")}">{ic}{H(a+".t")}</button></sc-if></sc-for>')
    return (f'<aside aria-label="{H("pan.title")}" style="width: 356px; flex-shrink: 0; border-left: 1px solid {LINE}; background: {SURF}; display: flex; flex-direction: column; min-height: 0;">'
      f'<div style="display: flex; align-items: flex-start; gap: 8px; padding: 12px 14px 8px;"><div style="flex-grow: 1; min-width: 0;"><h2 style="margin: 0; font-family: {DISP}; font-size: 17px; font-weight: 700; letter-spacing: -.02em;">{H("pan.title")}</h2>'
      f'<div style="font-size: 12.3px; color: {MUTED}; margin-top: 2px;">{H("pan.sub")}</div></div>'
      f'<button type="button" onClick="{H("pan_close")}" aria-label="Fechar painel" title="Fechar painel" style="border: 0; background: {BG}; width: 30px; height: 30px; border-radius: 999px; cursor: pointer; font-size: 17px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
      f'<div style="flex-grow: 1; min-height: 0; overflow-y: auto; padding: 0 14px 10px; display: flex; flex-direction: column; gap: 10px;">'
      f'<div style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H("pan.ch")}" as="c" hint-placeholder-count="1"><span style="{H("c.st")}">{H("c.t")}</span></sc-for></div>'
      f'<sc-if value="{H("pan_haskv")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; border-top: 1px solid {LINE};"><sc-for list="{H("pan.kv")}" as="k" hint-placeholder-count="3">'
      f'<div style="display: flex; gap: 10px; padding: 6px 0; border-bottom: 1px solid {LINE}; font-size: 12.8px;"><span style="width: 118px; flex-shrink: 0; color: {MUTED};">{H("k.l")}</span><b style="font-weight: 700; min-width: 0;">{H("k.t")}</b></div></sc-for></div></sc-if>'
      f'<sc-for list="{H("pan.secs")}" as="s" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 6px;">'
      f'<div style="font-size: 10.5px; font-weight: 800; letter-spacing: .07em; text-transform: uppercase; color: {MUTED}; padding-top: 2px;">{H("s.t")}</div>'
      f'<sc-for list="{H("s.items")}" as="it" hint-placeholder-count="2"><div style="border: 1px solid {LINE}; border-radius: 10px; padding: 8px 10px; display: flex; flex-direction: column; gap: 5px;">'
      f'<div style="font-size: 13px; font-weight: 700; line-height: 1.3;">{H("it.t")}</div>'
      f'<div style="display: flex; flex-wrap: wrap; gap: 4px;"><sc-for list="{H("it.ch")}" as="c" hint-placeholder-count="1"><span style="{H("c.st")}">{H("c.t")}</span></sc-for></div>'
      f'<div style="font-size: 12px; color: {MUTED}; line-height: 1.35;">{H("it.sub")}</div>'
      f'<div style="display: flex; flex-wrap: wrap; gap: 6px;">'
      + actions('it.acts','ia') +
      f'</div></div></sc-for></div></sc-for>'
      f'<sc-if value="{H("pan_hasnote")}" hint-placeholder-val="{F()}"><div style="font-size: 12.3px; color: {YEL}; background: {YELS}; border-radius: 10px; padding: 8px 10px; line-height: 1.4;">{H("pan.note")}</div></sc-if>'
      f'</div><div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 14px; border-top: 1px solid {LINE};">{actions("pan.acts")}</div></aside>')

def _mapcard(h,full=False):
    fgroups=(f'<sc-for list="{H("flt")}" as="g" hint-placeholder-count="2"><span style="display: inline-flex; align-items: center; gap: 6px;">'
             f'<span style="font-size: 11.5px; font-weight: 700; color: {MUTED};">{H("g.l")}</span>'
             f'<span role="group" aria-label="{H("g.l")}" style="display: inline-flex; gap: 2px; padding: 2px; border-radius: 9px; background: {GRAYS};"><sc-for list="{H("g.opts")}" as="o" hint-placeholder-count="3">'
             f'<button type="button" aria-pressed="{H("o.on")}" onClick="{H("o.go")}" style="{H("o.st")}">{H("o.t")}</button></sc-for></span></span></sc-for>')
    nums=(f'<div role="group" aria-label="Indicadores de {H("lay_t")}" style="display: flex; gap: 14px; flex-wrap: wrap;"><sc-for list="{H("nums")}" as="n" hint-placeholder-count="4">'
          f'<span style="white-space: nowrap; font-size: 11.5px; color: {MUTED};">{H("n.k")} <b style="color: {INK}; font-size: 13.5px;">{H("n.val")}</b></span></sc-for></div>')
    tool=lambda ic,t,fn,st,tt: f'<button type="button" onClick="{H(fn)}" title="{tt}" aria-pressed="{H(st.replace("_st","_on"))}" style="{H(st)}">{icon(ic,15,INK)}{t}</button>'
    sq=lambda t,fn,lab: f'<button type="button" onClick="{H(fn)}" aria-label="{lab}" title="{lab}" style="width: 36px; height: 36px; border: 0; border-radius: 10px; background: #FFFFFF; box-shadow: 0 1px 4px rgba(21,32,26,.18); font-family: inherit; font-size: 18px; font-weight: 700; color: {INK}; cursor: pointer;">{t}</button>'
    zoom=(f'<div role="group" aria-label="Zoom" style="position: absolute; right: 12px; top: 56px; display: flex; flex-direction: column; gap: 6px;">'
          + sq('+','zin','Aproximar') + sq('−','zout','Afastar') + '</div>')
    tools=(f'<div role="toolbar" aria-label="Ferramentas do mapa" style="position: absolute; right: 12px; top: 10px; display: flex; gap: 6px;">'
           + tool('grid','Selecionar área','r_selm','r_selm_st','Selecionar vários talhões') + tool('trend','Medir','r_medir','r_medir_st','Medir área e perímetro')
           + (tool('map','Sair da tela cheia','r_full','r_full_st','Sair da tela cheia') if full else tool('map','Tela cheia','r_full','r_full_st','Mapa em tela cheia')) + '</div>')
    return (f'<div style="height: {h}px; min-width: 0; flex-grow: 1; display: flex; flex-direction: column; background: {SURF}; border: 1px solid {LINE}; border-radius: 16px; overflow: hidden;">'
      f'<div style="display: flex; align-items: center; gap: 10px 16px; padding: 10px 12px 8px; flex-wrap: wrap; border-bottom: 1px solid {LINE};">'
      f'<b style="font-size: 14px; white-space: nowrap;">{H("lay_t")}</b>{fgroups}<span style="flex-grow: 1;"></span>{nums}'
      f'<sc-if value="{H("hasFlink")}" hint-placeholder-val="{F()}"><a href="{H("flink")}" style="{_MINI} text-decoration: none; white-space: nowrap;">{H("flinkt")} ›</a></sc-if>'
      f'<sc-if value="{H("hasFvis")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("r_vis")}" aria-pressed="{H("r_vis_on")}" title="Clique no talhão para criar a vistoria" style="{H("r_vis_st")}">{icon("alert",14,INK)}Criar vistoria</button></sc-if>'
      f'<div title="{H("fonte")}" style="flex-basis: 100%; font-size: 11px; color: {MUTED}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{H("fonte")}</div></div>'
      f'<div style="flex-grow: 1; min-height: 0; display: flex;">'
      f'<sc-if value="{H("map_on")}" hint-placeholder-val="{T()}">'
      f'<div style="flex-grow: 1; min-width: 0; position: relative; background: #E3EADB; overflow: hidden;"><div style="{H("zst")}">{_mapsvg(defs=not full)}</div>{tools}{zoom}'
      f'<sc-if value="{H("sem_modo")}" hint-placeholder-val="{T()}"><span style="position: absolute; left: 12px; top: 10px; padding: 7px 12px; border-radius: 10px; background: #FFFFFF; box-shadow: 0 1px 4px rgba(21,32,26,.18); font-size: 12.5px;"><b>{H("lay_t")}</b> <span style="color: {MUTED};">· clique no talhão para ver detalhes e ações</span></span></sc-if>'
      f'<sc-if value="{H("aviso_bv")}" hint-placeholder-val="{F()}"><span role="note" style="position: absolute; left: 12px; top: 50px; padding: 5px 10px; border-radius: 999px; background: {YELS}; color: {YEL}; font-size: 12px; font-weight: 700; box-shadow: 0 1px 3px rgba(21,32,26,.14);">Boa Vista sem geometria</span></sc-if>'
      f'<div style="position: absolute; left: 12px; bottom: 12px; right: 12px; display: flex; flex-wrap: wrap; align-items: center; gap: 4px 12px; padding: 8px 12px; border-radius: 10px; background: rgba(255,255,255,.94); box-shadow: 0 1px 4px rgba(21,32,26,.14); font-size: 11.5px; color: {MUTED};">'
      f'<sc-for list="{H("leg")}" as="x" hint-placeholder-count="5"><span style="{H("x.st")}"><span style="{H("x.dot")}"></span>{H("x.t")}</span></sc-for><span style="flex-grow: 1;"></span><span>Geometria e valores demonstrativos.</span></div>'
      f'<sc-if value="{H("has_modo")}" hint-placeholder-val="{F()}"><span role="status" style="position: absolute; left: 12px; top: 10px; padding: 5px 10px; border-radius: 999px; background: {INK}; color: #fff; font-size: 12px; font-weight: 700;">{H("modo")}</span></sc-if></div></sc-if>'
      f'<sc-if value="{H("map_vazio")}" hint-placeholder-val="{F()}"><section aria-label="Mapa da Boa Vista" style="flex-grow: 1; min-width: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; background: {BG};">'
      f'{icon("map",40,MUTED)}<b style="font-size: 16px;">Nenhum talhão desenhado na Boa Vista</b>'
      f'<a href="CD-01.dc.html" style="{_IST}{BTN_ST(True,True)}">{icon("map",15)}Cadastrar talhões</a></section></sc-if>'
      f'<sc-if value="{H("pan_open")}" hint-placeholder-val="{F()}">{_panel_html()}</sc-if></div>'
      f'</div>')
def _defs_body():
    return ('<pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#C9CFCB"/>'
            '<line x1="0" y1="0" x2="0" y2="10" stroke="#9E9E9E" stroke-width="4"/></pattern>')

def _rail():
    ICON={'Integrado': 'layers', 'Satélite': 'grid', 'Solo': 'lab', 'MIP/MID': 'alert', 'O.S./prazos': 'doc', 'Irrigação': 'drop', 'Estádio': 'leaf', 'Colheita/produtividade': 'Colheita', 'Custos': 'cash'}
    items=[f'<button type="button" role="tab" aria-selected="{H("ly%d_on" % i)}" onClick="{H("ly%d_go" % i)}" title="Mostrar {esc(NOME_LAY.get(t,t))} no mapa" style="{H("ly%d_st" % i)}">'
           f'{icon(ICON[t],20,"currentColor")}<span style="font-size: 11.5px; font-weight: 700; line-height: 1.15; text-align: center;">{esc(NOME_LAY.get(t,t))}</span></button>'
           for i,t in enumerate(MDATA['lays'])]
    return f'<nav role="tablist" aria-orientation="vertical" aria-label="Funcionalidades do mapa" style="display: flex; flex-direction: column; gap: 6px; flex-shrink: 0;">{"".join(items)}</nav>'

def build_in04(HCARD=742):
    import cenario  # cenário compartilhado (fase e realizado das ordens iguais às telas O.S., Estoque e App)
    pref=cenario.js_prefixo()
    fname='IN-04.dc.html'; E._reset_screen(fname)
    HEIGHTS37[fname]=900
    EXTRAJS[0]=pref+JS_COMUM+JS_AG+'const M = '+json.dumps(MDATA,ensure_ascii=False).replace('</','<\\/')+';\n'+MAP_JS+r'''
function EXTRAVALS(self,v){ cenOuvir(self); MAPVALS(self,v); v.r_selm_on=!!self.state.selm?'true':'false'; v.r_medir_on=!!self.state.medir?'true':'false'; v.r_full_on=!!self.state.full?'true':'false'; v.r_pref_on=!!self.state.pref?'true':'false'; v.r_vis_on=!!self.state.cvis?'true':'false'; }
'''
    corpo=f'<div style="display: flex; gap: 12px; align-items: stretch; min-width: 0;">{_rail()}{_mapcard(HCARD)}</div>'
    EXTRA.append(f'<sc-if value="{H("full")}" hint-placeholder-val="{F()}"><div role="dialog" aria-label="Mapa em tela cheia" style="position: fixed; inset: 0; z-index: 55; background: {BG}; padding: 14px; box-sizing: border-box; display: flex; gap: 12px;">{_rail()}{_mapcard(872,full=True)}</div></sc-if>')
    shell37('IN-04','Mapa da fazenda',corpo,primary_html=f'<span style="{H("hs_st")}">{H("hs_t")}</span>')

# =====================================================================================================
# DECISÕES (IN-02det OS-0418 · IN-02x-os0420) — um só padrão com estado
# =====================================================================================================
def decisao(fname,titulo,crumb,cont,corpo_extra,cfg):
    """cfg: dict(oid, vn, fase, rec_id, aprovar, t_rej, devolver(bool), rec_ap, rec_rej, rec_dev, estado0, est_ap, est_rej, sub_rej, desc_dec,
    cond_*/dono_*/prazo_* (texto que a tela O.S. mostra depois da decisão)). A decisão grava no cenário compartilhado (inDecidir);
    o estado, o recibo e a próxima pendência (inProx: a fila do agrônomo, circular) vêm do cenário."""
    import cenario
    PARENT37[fname]='IN-02.dc.html'
    cfg=dict(cfg,cont=list(cont))
    js=cenario.js_prefixo()+JS_COMUM+JS_AG+'const CFG = '+json.dumps(cfg,ensure_ascii=False)+';\n'+r'''
// grava a decisão na ordem do cenário (igual à revisão da tela O.S.: selo, versão e recibo); nunca libera a ordem
function inDecidir(c,k,mot){ const o=c.ordens[CFG.oid]; if(!o) throw new Error('Ordem '+CFG.oid+' não encontrada no cenário.');
  if(!inPendAg(c,CFG.oid)) throw new Error('Decisão já registrada · nada foi duplicado.');
  const at=cenAgora(); o.decAg={v:CFG.vn,k,mot:mot||'',rec:k==='aprovada'?CFG.rec_id:'',at};
  const sel=(o.selos||[]).filter(s=>!/^(Aguardando agrônomo|Revisão de saldo pendente|Devolvida|Aprovada|Rejeitada|v\d+ devolvida)/.test(s.t));
  o.osc=o.osc||{};
  if(CFG.fase==='A liberar'){
    if(k==='aprovada'){ o.aprov=true; o.versao=String(o.versao).replace('em revisão','aprovada'); o.selos=sel.concat([{t:'Aprovada pelo agrônomo',c:'green'}]); o.osc.recibo={id:CFG.rec_id,at,quem:'Ana (agrônoma)'}; }
    else { o.selos=sel.concat([k==='rejeitada'?{t:'Rejeitada',c:'red'}:{t:'Devolvida para ajuste',c:'yellow'}]); if(k==='rejeitada') o.osc.rej=mot; } }
  else { o.versao=CFG['ver_'+k]; o.selos=sel.concat(k==='devolvida'?[{t:CFG.vn+' devolvida para ajuste',c:'yellow'}]:[]); }
  Object.assign(o.osc,{cond:CFG['cond_'+k].replace('{at}',at)+(mot?' Motivo: '+mot+'.':''),dono:CFG['dono_'+k]||'',prazo:CFG['prazo_'+k]||'',fase:o.etapa});
  return {msg:k==='aprovada'?CFG.rec_ap:(k==='rejeitada'?CFG.rec_rej:CFG.rec_dev)}; }
function EXTRAVALS(self,v){ cenOuvir(self); const st=self.state; const c=cenGet(); const dx=inDecAg(c,CFG.oid); const d=dx?dx.k:null;
  v.dec_none=!d; v.dec_done=!!d;
  const est={aprovada:[CFG.est_ap,'green'],rejeitada:[CFG.est_rej,'red'],devolvida:['Devolvida ao emitente','yellow']}[d]||[CFG.estado0,'yellow'];
  v.st_t=est[0]; v.st_st=chipSt(est[1]); const mt=dx&&dx.mot?' Motivo: '+dx.mot+'.':'';
  const ct=d?[est[0]].concat(CFG['ct_'+d]):CFG.cont.slice(1); v.ct_aqui=ct[0]; v.ct_falta=ct[1]; v.ct_prox=ct[2];  // faixa de continuidade segue a decisão
  v.rec_t=d==='aprovada'?(dx.rec&&dx.rec!==CFG.rec_id?'Versão '+CFG.vn+' aprovada na tela Ordem de serviço · recibo '+dx.rec+'.':CFG.rec_ap):(d==='rejeitada'?CFG.rec_rej+mt:(d==='devolvida'?CFG.rec_dev+mt:''));
  const px=inProx(c,CFG.oid); v.prox_t=px[0]; v.prox_h=px[1];
  v.aprovar=()=>{ cenMudar(self,x=>inDecidir(x,'aprovada','')); };
  v.pedir=(k)=>()=>self.setState({mp:k,mot:'',moterr:''});
  v.p_rej=v.pedir('rejeitada'); v.p_dev=v.pedir('devolvida');
  v.mp_open=!!st.mp; v.mp_titulo=st.mp==='rejeitada'?CFG.t_rej:'Devolver para ajuste'; v.mp_bt=st.mp==='rejeitada'?CFG.t_rej:'Devolver para ajuste';
  v.mp_sub=st.mp==='rejeitada'?CFG.sub_rej:'O emitente recebe o motivo e envia nova versão; o histórico é preservado.';
  v.mot=st.mot||''; v.setmot=(e)=>self.setState({mot:e.target.value,moterr:''}); v.moterr=st.moterr||''; v.has_moterr=!!st.moterr;
  v.mp_cancel=()=>{ if((self.state.mot||'').trim() && !self.state.mpw){ self.setState({mpw:true}); return; } self.setState({mp:null,mpw:false}); };
  v.mp_warn=!!st.mpw; v.mp_keep=()=>self.setState({mpw:false}); v.mp_discard=()=>self.setState({mp:null,mpw:false,mot:''});
  v.mp_ok=()=>{ const m=(self.state.mot||'').trim(); if(!m){ self.setState({moterr:'Informe o motivo.'}); return; } const k=self.state.mp;
    cenMudar(self,x=>inDecidir(x,k,m)); self.setState({mp:null,mpw:false,mot:''}); };
  v.prim_st='padding:11px 20px;border-radius:10px;font-size:14px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap;background:#1E7A4C;color:#fff;border:1px solid #1E7A4C;'+(d?'display:none;':'');
}
'''
    EXTRAJS[0]=js
    acoes=(f'<sc-if value="{H("dec_none")}" hint-placeholder-val="{T()}"><div style="display: flex; gap: 8px; flex-wrap: wrap;">'
           + (ifn('Devolver com motivo','p_dev','doc','Devolver ao emitente para ajuste') if cfg.get('devolver') else '')
           + ifn(esc(cfg['t_rej']),'p_rej','alert',cfg['t_rej']+' com motivo') + '</div></sc-if>'
           f'<sc-if value="{H("dec_done")}" hint-placeholder-val="{F()}"><div role="status" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 14px; border-radius: 12px; background: {ACCS}; font-size: 13px; line-height: 1.5;">'
           f'<span><b>Recibo</b> · {H("rec_t")}</span><a href="{H("prox_h")}" style="{_MINI} align-self: flex-start; text-decoration: none; display: inline-flex; gap: 6px; align-items: center;">{icon("check",14)}{H("prox_t")} ›</a></div></sc-if>')
    corpo=(continuity(cont[0],H('ct_aqui'),H('ct_falta'),H('ct_prox')) + corpo_extra
           + bloco('Decisão',cfg['desc_dec'],acoes))
    EXTRA.append(
      f'<sc-if value="{H("mp_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar" onClick="{H("mp_cancel")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="{H("mp_titulo")}" style="position: relative; width: 460px; height: 100vh; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
      f'<h2 style="margin: 0; font-family: {DISP}; font-size: 19px;">{H("mp_titulo")}</h2><div style="font-size: 13px; color: {MUTED};">{H("mp_sub")}</div>'
      f'<label for="mp_mot" style="font-size: 12px; font-weight: 600; color: {MUTED};">Motivo</label>'
      f'<textarea id="mp_mot" value="{H("mot")}" onChange="{H("setmot")}" style="font-family: inherit; font-size: 14px; padding: 9px 11px; border-radius: 10px; border: 1px solid {LINE}; min-height: 90px;"></textarea>'
      f'<sc-if value="{H("has_moterr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("moterr")}</span></sc-if>'
      f'<div style="flex-grow: 1;"></div>'
      f'<sc-if value="{H("mp_warn")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("mp_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H("mp_keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
      f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};"><button type="button" onClick="{H("mp_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" onClick="{H("mp_ok")}" style="{BTN_ST(True,True)}">{H("mp_bt")}</button></div>'
      f'</aside></div></sc-if>')
    prim=(f'<span style="{H("st_st")}">{H("st_t")}</span><button type="button" onClick="{H("aprovar")}" style="{H("prim_st")}">{esc(cfg["aprovar"])}</button>')
    HEIGHTS37[fname]=cfg.get('h',1000)
    shell37('IN-02',titulo,corpo,fname=fname,crumbs_extra=[crumb],primary_html=prim,search=False)

def diff2(esq_t,esq,dir_t,dir_):
    return (f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">'
      f'<div style="border: 1px solid {LINE}; border-radius: 12px; padding: 12px 14px;"><div style="font-size: 11px; font-weight: 800; color: {MUTED}; letter-spacing: .06em;">{esc(esq_t)}</div><div style="font-size: 13px; margin-top: 6px; line-height: 1.6;">{esq}</div></div>'
      f'<div style="border: 1px solid {ACC}; background: {ACCS}; border-radius: 12px; padding: 12px 14px;"><div style="font-size: 11px; font-weight: 800; color: {ACC}; letter-spacing: .06em;">{esc(dir_t)}</div><div style="font-size: 13px; margin-top: 6px; line-height: 1.6;">{dir_}</div></div></div>')

def build_decisoes():
    E._reset_screen('IN-02det.dc.html')
    # ---- OS-0418 · fertirrigação v2 ----
    g=grid([dict(k='prod',l='Produto'),dict(k='dose',l='Dose'),dict(k='qtd',l='Quantidade',t='num',a='r',u='kg'),dict(k='comp',l='Compatibilidade'),dict(k='fonte',l='Fonte')],
           [R('u1',prod='Ureia 45 %',dose='12 kg/ha × 95 ha',qtd=1140,comp=[Pt.chip('Compatível com água de irrigação','green')],fonte='protocolo do plano técnico',
             o=[dict(t='Requisição REQ-038 · Ureia 1.140 kg (reserva ao liberar)',h='EST.dc.html'),dict(t='12 kg/ha × 95 ha = 1.140 kg')])],
           edit=dict(m='origin',title='Produto',fields=[dict(k='prod',l='Produto',ro=True),dict(k='dose',l='Dose',ro=True)]),search=False,total=False,gid='g_d18')
    decisao('IN-02det.dc.html','Decidir · OS-0418 fertirrigação','OS-0418 · v2',
      ('Programação da irrigação · reclassificação','Aguardando agrônomo','decisão · prontidão · liberação','Decidir a versão v2'),
      bloco('Diferenças da versão submetida','Compare as versões: produto na água exige a decisão do agrônomo.',
            diff2('VERSÃO v1 · SÓ ÁGUA','Lâmina 8 mm · sem produtos<br>Lâmina pela necessidade do balanço · liberada pela prontidão, sem agrônomo<br>Sem requisição, custódia ou sobras',
                  'VERSÃO v2 SUBMETIDA · FERTIRRIGAÇÃO','<b>+ Ureia 12 kg/ha</b> na mesma tarefa e mesmo ID (95 ha)<br>Produto na água: <b>passa a exigir o agrônomo</b><br>Após aprovar: requisição REQ-038, custódia e conciliação'))
      + bloco('Produto e compatibilidade','Confira dose, quantidade e compatibilidade; clique na linha para ver a origem.',g),
      dict(oid='OS-0418',vn='v2',fase='A liberar',rec_id='AP-2201',
           aprovar='Aprovar versão v2',t_rej='Rejeitar versão',devolver=True,estado0='Aguardando agrônomo',est_ap='Aprovada · A liberar',est_rej='Rejeitada · A liberar',
           sub_rej='A tarefa não é cancelada: segue A liberar sem autorização para o saldo até nova versão.',
           rec_ap='AP-2201 · versão v2 aprovada por Ana (agrônoma) · a OS-0418 segue A liberar; ao liberar, a REQ-038 reserva a Ureia no Estoque.',
           rec_rej='Versão v2 rejeitada · a OS-0418 segue A liberar, sem autorização para o saldo, até nova versão ou volta a só água (sem agrônomo) · histórico preservado.',
           rec_dev='Versão v2 devolvida a João com o motivo · a OS-0418 segue A liberar.',
           ct_aprovada=['prontidão · liberação na O.S.','Liberar para execução'],ct_rejeitada=['nova versão ou volta a só água','Aguardar nova versão de João'],
           ct_devolvida=['ajuste de João','Aguardar nova versão de João'],
           cond_aprovada='Versão v2 aprovada por Ana (agrônoma) · recibo AP-2201 às {at}. Próximo passo: liberar para execução.',
           cond_devolvida='Devolvida para ajuste · João (irrigante) ajusta e reenvia a v2.',dono_devolvida='João (irrigante)',prazo_devolvida='ajustar e reenviar',
           cond_rejeitada='Versão v2 rejeitada por Ana (agrônoma). A liberação fica bloqueada; a ordem não foi cancelada.',dono_rejeitada='PCP',prazo_rejeitada='ajustar ou cancelar',
           desc_dec='Aprove, devolva ou rejeite só esta versão; aprovar não libera a ordem.',h=900))
    # ---- OS-0420 · revisão de saldo v3 (DEMO-14) ----
    E._reset_screen('IN-02x-os0420.dc.html')
    o=next(x for x in D.OS if x['id']=='OS-0420'); real,saldo,area=o['realizado'],o['saldo'],o['area']
    kcl_v2=saldo*120; kcl_v3=saldo*105.6; eco=(kcl_v2-kcl_v3)*2.40
    g2=grid([dict(k='item',l='Item',w=230),dict(k='v2',l='v2 · vigente',w=190),dict(k='v3',l='v3 · saldo',w=210),dict(k='efe',l='Efeito no saldo',w=230)],
            [R('k1',item='KCl 60 %',v2='120 kg/ha',v3=[Pt.chip('105,6 kg/ha · −12 %','yellow')],efe=f'{nfb(kcl_v2)} → {nfb(kcl_v3,0)} kg · −R$ {nfb(eco,2)}',
               o=[dict(t='REC-014 v2 → v3 · dose revista só no saldo',h='AG-04det.dc.html'),dict(t=f'{saldo} ha × 120 kg/ha = {nfb(kcl_v2)} kg (v2) · {saldo} ha × 105,6 kg/ha = {nfb(kcl_v3,0)} kg (v3) · R$ 2,40/kg')]),
             R('k2',item='Semente de soja 58 W',v2='52 kg/ha',v3=[Pt.mut('sem mudança')],efe=f'{nfb(saldo*52)} kg',o=[dict(t=f'{saldo} ha × 52 kg/ha')]),
             R('k3',item='TS nematicida',v2='100 mL/100 kg de semente',v3=[Pt.mut('sem mudança')],efe=f'{nfb(saldo*52/1000,2)} L',o=[dict(t='bula AGROFIT')])],
            edit=dict(m='origin',title='Item',fields=[dict(k='item',l='Item',ro=True),dict(k='efe',l='Efeito',ro=True)]),search=False,total=False,gid='g_d20')
    g3=grid([dict(k='item',l='Consumo realizado'),dict(k='qtd',l='Quantidade',t='num',a='r',u='kg'),dict(k='preco',l='Preço',t='num',a='r',pre='R$ ',d=2),dict(k='custo',l='Custo',t='num',a='r',pre='R$ ',agg='sum')],
            [R('c1',item='Semente de soja 58 W · 52 kg/ha',qtd=real*52,preco=9.50,custo=real*52*9.50,o=[dict(t='REQ-036 · consumo apontado 18 ha + 12 ha',h='CA-02.dc.html')]),
             R('c2',item='KCl 60 % · 120 kg/ha (v2)',qtd=real*120,preco=2.40,custo=real*120*2.40,o=[dict(t='Apontamentos de 21 e 22/09',h='CA-02.dc.html')])],
            edit=dict(m='origin',title='Consumo',fields=[dict(k='item',l='Item',ro=True)]),search=False,total=True,gid='g_d20c')
    decisao('IN-02x-os0420.dc.html','Decidir · revisão de saldo OS-0420','OS-0420 · v3',
      ('OS-0420 · plantio Soja 58 W · T4','Aguardando agrônomo','decisão · revalidar prontidão · liberar o saldo','Decidir a versão v3'),
      bloco('O que muda na v3','Confira: a v3 vale só para o saldo de 70 ha; os 30 ha realizados ficam na v2.',g2,
            ilink('Abrir ordem','CA-01x-os0420.dc.html','doc','Abrir a OS-0420'))
      + bloco('Custo preservado dos 30 ha realizados','Confira o consumo e o custo já apontados; eles não mudam com a v3.',g3),
      dict(oid='OS-0420',vn='v3',fase='Em execução',rec_id='AP-2202',
           aprovar='Aprovar versão v3',t_rej='Rejeitar versão',devolver=True,estado0='Aguardando agrônomo · saldo pausado',est_ap='v3 aprovada · saldo A liberar',est_rej='Rejeitada · v2 segue',
           sub_rej='O saldo volta a seguir a v2 depois de revalidar a prontidão; os 30 ha realizados não mudam.',
           rec_ap=f'AP-2202 · v3 aprovada por Ana (agrônoma) só para o saldo de {saldo} ha · {real} ha realizados preservados na v2 (R$ 23.460) · o saldo segue A liberar até revalidar a prontidão (Trator T1 em reparo, OM-0233).',
           rec_rej=f'Versão v3 rejeitada · o saldo de {saldo} ha segue a v2 e fica pausado até revalidar a prontidão · histórico preservado.',
           rec_dev='Versão v3 devolvida a Carlos com o motivo · o saldo continua pausado.',
           ct_aprovada=['revalidar prontidão · liberar o saldo','Revalidar a prontidão (PCP)'],ct_rejeitada=['revalidar prontidão · saldo na v2','Revalidar a prontidão (PCP)'],
           ct_devolvida=['v3 ajustada por Carlos','Aguardar a v3 ajustada'],
           ver_aprovada=f'v2 nos {real} ha realizados · v3 aprovada no saldo',ver_rejeitada='v2 aprovada · v3 rejeitada',ver_devolvida='v2 aprovada · v3 devolvida',
           cond_aprovada=f'v3 aprovada por Ana (agrônoma) só no saldo de {saldo} ha · recibo AP-2202 às {{at}}. Próximo passo: revalidar a prontidão (Trator T1 em reparo, OM-0233) e liberar o saldo.',
           dono_aprovada='PCP · Manutenção',prazo_aprovada='Trator 02 a partir de 24/09',
           cond_rejeitada=f'v3 rejeitada por Ana (agrônoma): o saldo de {saldo} ha segue a v2, pausado até revalidar a prontidão.',dono_rejeitada='PCP',prazo_rejeitada='revalidar a prontidão',
           cond_devolvida='v3 devolvida a Carlos (PCP) para ajuste · o saldo continua pausado.',dono_devolvida='Carlos (PCP)',prazo_devolvida='ajustar e reenviar a v3',
           desc_dec='Aprove, devolva ou rejeite a v3; aprovar não libera o saldo: a prontidão é revalidada depois.',h=900))
    # IN-02x-os0422 (exceção de água) deixou de existir: irrigação só com água não passa pelo agrônomo.

# =====================================================================================================
# IN-02 · Aprovações
# =====================================================================================================
# Irrigação só com água não entra aqui (sem agrônomo): a fila do agrônomo tem só a fertirrigação e as decisões agronômicas.
APROV=[  # (id, objeto, tipo, solicitante, alçada, venc, efeito, conflito(t,c)|None, destino, independente)
 ('a1','OS-0418 · fertirrigação P1 · v2','Ordem de serviço','João · irrigante','Agrônomo','vence hoje','Ureia 12 kg/ha · 95 ha · 2 anexos',('Revisão individual','yellow'),'IN-02det.dc.html',False),
 ('a2','OS-0420 · revisão de saldo · v3','Ordem de serviço','Carlos · PCP','Agrônomo','até 2 dias','KCl −12 % só no saldo de 70 ha · 30 ha preservados',('Impedida · OM-0233','red'),'IN-02x-os0420.dc.html',False),
 ('a3','OS-0430 · dessecação T1-A · v1','Ordem de serviço','Carlos · PCP','Agrônomo','até 2 dias','Glifosato 2 L/ha + 2,4-D 1 L/ha · 160 ha',None,'OS.dc.html',False),
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
    import cenario
    AGR={a[0]:a[1].split(' · ')[0] for a in APROV if a[4]=='Agrônomo'}
    assert sorted(AGR.values())==sorted(x[0] for x in IN_AG), 'fila do agrônomo diferente da caixa de Aprovações'
    EXTRAJS[0]=cenario.js_prefixo()+JS_COMUM+JS_AG+'const AGR='+json.dumps(AGR)+';\n'+r'''
// decisões do agrônomo: situação lida do cenário compartilhado (decidida aqui, na tela O.S. ou nas telas de decisão)
function PREVALS(self,v){ cenOuvir(self); const c=cenGet();
  g2rows(self,GRx('g_ap')).forEach(r=>{ const oid=AGR[r.id]; if(!oid) return; if(!r.sit0) r.sit0=r.p.sit; const d=inDecAg(c,oid);
    if(!d){ r.p.sit=r.sit0; r.s.sit='Pendente'; return; }
    const t={aprovada:'Aprovada'+(d.rec?' · '+d.rec:''),rejeitada:'Rejeitada',devolvida:'Devolvida ao emitente'}[d.k];
    r.p.sit=[{k:'chip',t,c:{aprovada:'green',rejeitada:'red',devolvida:'yellow'}[d.k]}]; r.s.sit=t.split(' · ')[0]; }); }
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
     ('f2','OS-0418 · fertirrigação','Santa Rita · P1','Decidir a versão v2','vence hoje','Ana',('Aguardando agrônomo','yellow'),('Decidir','IN-02det.dc.html')),
     ('f3','OS-0420 · revisão de saldo','Santa Rita · T4','Decidir a versão v3 (saldo de 70 ha)','até 3 dias','Ana',('Saldo pausado','yellow'),('Decidir','IN-02x-os0420.dc.html')),
     ('f4','OS-0417 · cobertura','Santa Rita · P1',f'Receber devolução de sobras ({D.REQ["custodia"]} sc)','vence hoje','Rui',None,('Receber devolução','EST.dc.html')),
     ('f5','Fila de expedição','Sede · doca 1','Chamar o próximo apto da fila (T2)','vence hoje','Equipe expedição',('T1 atrasado · prev. 09:10','red'),('Abrir fila','LO-02.dc.html')),
     ('f6','OS-0421 · fungicida','Santa Rita · T1+T2',f'Conferir o apontamento do dia 4 ({D.OS[0]["dias"][3]} ha)','até 3 dias','Paula',None,('Conferir apontamentos','CA-02.dc.html')),
     ('f7','INSP-88 · qualidade','Armazém Sede',f'Decidir o lote {D.LOTE_BLOQ["id"]}','até 3 dias','Equipe qualidade',('Lote bloqueado','red'),('Abrir inspeção','CO-06det.dc.html')),
     ('f8','Amostragem de solo','Santa Rita · T2','Coletar 0–20 cm para a recomendação de plantio','no prazo','Sem responsável',None,('Abrir análises','AG-02.dc.html')),
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
                   ilink('Abrir OM-0233','MA-04det.dc.html','wrench','Abrir a ordem de manutenção do Trator T1')+ilink('Ver app de João','MB-01.dc.html','users','Abrir o app móvel'),tone='yellow'))
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
     ('g6','2026-09-23','Resolver conflito da OS-0423 com a parada da B3','Caio','Alta','irrigação do T7 hoje 14:00–16:00',('Conflito · parada da B3','red'),'23/09 14:00',('Resolver conflito','IR-02.dc.html')),
     ('g2','2026-09-23',f'Receber devolução {D.REQ["id"]} ({D.REQ["custodia"]} sc)','Rui','Alta','custódia zerada para encerrar',None,'24/09',('Receber devolução','EST.dc.html')),
     ('g3','2026-09-24',f'Substituir {OM["ativo"].split(" · ")[0]} na {OM["os_afetada"]} (T4)','Carlos','Alta','início programado',(f'{OM["id"]} em execução','red'),'24/09 06:00',('Reprogramar','PL-05.dc.html')),
     ('g4','2026-09-25',f'Decidir INSP-88 · lote {D.LOTE_BLOQ["id"]}','Equipe qualidade','Normal','liberação comercial',('Lote bloqueado','red'),'25/09',('Abrir origem','CO-06det.dc.html')),
     ('g5','2026-09-26','Amostragem de solo · T2 (0–20 cm)','Sem responsável','Normal','recomendação de plantio',None,'28/09',('Abrir origem','AG-02.dc.html')),
     ('g7','2026-09-24','Definir janela da OS-0422 · Pivô 2 (2 passadas de 6,75 mm)','João','Normal','próximo ciclo de irrigação',('Janela a definir','yellow'),'25/09',('Definir janela','IR-02.dc.html')),
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
    EXTRAJS[0]=JS_COMUM+'const DIAS='+json.dumps(DIAS,ensure_ascii=False)+';\n'+r'''
function PREVALS(self,v){ g2rows(self,GRx('g_ag')).forEach(r=>{ r.p.ob=[{k:'b',t:r.v.ob||''}]; r.s.ob=r.v.ob; if(!r.p.acao) r.p.acao=[{k:'mut',t:'tarefa vinculada'}];
  r.p.pri=[{k:'chip',t:r.v.pri,c:r.v.pri==='Alta'?'red':'gray'}]; if(!r.v.lim){ r.v.lim='—'; } if(!r.p.comp && !r.v.comp) r.p.comp=[{k:'mut',t:'tarefa vinculada'}];
  if(r.v.resp==='Sem responsável'){ r.p.resp=[{k:'mut',t:'sem responsável'}]; } else delete r.p.resp; }); }
function EXTRAVALS(self,v){ const rs=g2rows(self,GRx('g_ag'));
  v.semana=DIAS.map((d,i)=>({t:d[0].slice(8,10)+'/'+d[0].slice(5,7)+' · '+d[1].toUpperCase(), st:'flex:1 1 0;min-width:0;border:1px solid #E4E9E5;border-radius:12px;padding:8px 10px;background:'+(i===0?'#E4F3E9':'#F4F6F3')+';',
    tst:'font-size:11px;font-weight:800;letter-spacing:.05em;color:'+(i===0?'#1E7A4C':'#65736A')+';',
    its:rs.filter(r=>r.v.dt===d[0]).map(r=>({t:r.v.ob, st:'margin-top:6px;font-size:12px;line-height:1.3;padding:5px 8px;border-radius:8px;background:#fff;border-left:3px solid '+(r.v.pri==='Alta'?'#B42318':'#E4E9E5')+';'}))}));
  const alta=rs.filter(r=>r.v.pri==='Alta').length; v.hs_t=rs.length+' compromissos · '+alta+' de prioridade alta'; v.hs_st=chipSt(alta?'yellow':'green'); }
'''
    semana=(f'<div style="display: flex; gap: 10px;"><sc-for list="{H("semana")}" as="d" hint-placeholder-count="5"><div style="{H("d.st")}"><div style="{H("d.tst")}">{H("d.t")}</div>'
            f'<sc-for list="{H("d.its")}" as="i" hint-placeholder-count="1"><div style="{H("i.st")}">{H("i.t")}</div></sc-for></div></sc-for></div>')
    dep=nota(f'Encerrar {B(D.REQ["os"])} depende de receber {D.REQ["custodia"]} sc em custódia {B("ou")} da destinação formal das sobras.<br>'
             f'Iniciar o saldo da {B(OM["os_afetada"])} depende da alocação substituta ({esc(OM["substituto"])}), da decisão da v3 e de nova liberação.')
    corpo=(bloco('Semana de 23 a 27/09','Confira os compromissos da semana; adiar um alerta não muda a data da obrigação.',semana)
           + bloco('Compromissos','Clique na linha para mudar data, responsável ou prioridade; “Abrir” leva ao registro de origem.',g)
           + bloco('Dependências','Resolva estas condições para encerrar e iniciar as ordens.',dep,
                   ilink('Reprogramar no PCP','PL-05.dc.html','calendar','Abrir Impedimentos e reprogramação'),tone='yellow'))
    HEIGHTS37[fname]=1100  # 7 compromissos (conflito da OS-0423 e janela da OS-0422) + Dependências sem corte
    prim=f'<span style="{H("hs_st")}">{H("hs_t")}</span><button type="button" onClick="{H("g_ag_new")}" style="{BTN_ST(True,False)}">Criar tarefa vinculada</button>'
    shell37('IN-03','Agenda e pendências',corpo,primary_html=prim,search=False)

def build():
    build_in01(); build_in02(); build_decisoes(); build_in03(); build_in04()
