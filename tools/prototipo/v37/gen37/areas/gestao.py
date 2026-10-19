# -*- coding: utf-8 -*-
"""Área Gestão (módulo OCULTO do menu, preservado) — GE-01 Visão gerencial · GE-02 Orçamento e previsões (+GE-02det, DEMO-12) ·
GE-03 Custos e fechamento · GE-04 Contas a pagar e caixa · GE-05 Contas a receber · GE-06 Indicadores operacionais (+GE-06det) ·
GE-07 Planos de ação · GE-08 Crédito e garantias (DEMO-10, CRE-0102).
Padrão novo (25/09/2026): descrição imperativa sob cada bloco, edição pela linha (G2: formulário tipado nos registros editáveis,
consulta nos históricos, origem nos indicadores calculados), ações secundárias com ícone + rótulo + title, sem faixa de etapas
(módulo não sequencial). Ações de processo mudam a própria linha e recusam repetição.

observacoes (dados locais coerentes com dados.py / dados2.py / comercial.py / suprimentos.py / campo.py):
- Exemplo aritmético do cap. 51 (DEMO-12) ancorado na OS-0409 (fungicida no feijão P1, encerrada): V1 100 ha·op × 2,0 L/ha × R$ 20/L = R$ 4.000;
  V2 R$ 4.851; real 120 ha·op × 2,2 L/ha × R$ 22/L = R$ 5.808. OS-0409 também é usada com outro sentido em irrigacao.py (água 42 ha)
  e mobile.py (colheita milho T3) — conflito de identificador a reconciliar fora deste módulo.
- Resultado por cultura refeito sobre a previsão V2: soja 814 ha × 63 sc/ha = 51.280 sc × R$ 121/sc; milho 176 ha × 170 sc/ha × R$ 61/sc
  (preço do PV-029); feijão 95 ha × 50 sc/ha × R$ 385/sc; mamão 42 ha × 45 t/ha × R$ 2,60/kg médio A+B; café 38 ha × 38 sc/ha × R$ 2.480/sc
  (preço do CT-198). Custos somam R$ 14,68 mi = custo total da V2 (GE-02). ROIC = margem × (1 − 34%) ÷ capital com terra.
- Cronograma de caixa ganhou jul–set/27 para fechar com o custo total de cada versão (V1 14,25 · V2 14,68 mi).
- GE-03 inclui a OS-0420 (DEMO-01): REQ-036 semente 58 W 1.560 kg (30 ha × 52 kg/ha) × R$ 9,50; REQ-037 KCl 3.600 kg (30 ha × 120 kg/ha,
  de suprimentos.py) × R$ 2,40; apontamento 6,0 h de plantio × R$ 396/h (conjunto r2 de dados2: 180 + 140 + 2 × 38); diesel 84 L do Trator T1.
  OS-0421: REQ-035 Fungicida A 95 L × R$ 145; 190 ha ÷ 21,6 ha/h = 8,8 h × R$ 313/h (conjunto r1).
- PC-088 (dados.CANON["PC088"]): Fertisul, KCl 60% 100 t × R$ 2,33 = R$ 233.000 · NF 4501 (60 t recebidas) · título único,
  sem barter (28 d → 17/10). GE-05 cita PV-031 (dados.CANON["PV031"]) como próximo faturamento da Frutas Real.
- NF 8790 (R$ 96.000, vence hoje) passou a Agro Norte · pedido PC-084 de defensivos (local); diesel NF 5531 passou a Ipiranga Agro
  (fornecedor do CT-2026-03 em suprimentos.py); sementes = PC-090 Coop. Vale 20 t × R$ 9,30 = R$ 186.000 (previsão; título nasce na
  conferência da NF 4533). CT-77 (antecipação, local) re-ancorado na venda VD-2101 de logistica.py: R$ 100.000 abatidos nas retiradas.
- GE-05 refeito sobre comercial.py (DEMO-08): PV-029 R$ 244.000 (4.000 sc × R$ 61) vencido 4 d; PV-027 em 2 títulos de 3,0 t × R$ 2,95/kg
  (FAT-2088 e FAT-2096), o 2º com "Crédito solicitado · RC-12 · 300 kg" (R$ 885); PV-026/VG-117 9,4 t × R$ 3,00/kg com recusa de 0,4 t
  (RC-15, R$ 1.200); PV-030 8.000 sc × R$ 128 recebidos. Crédito emitido recebe o nº CR-031 (local). GE-05 aceita ?caso=RC-12 para abrir
  filtrado pelo caso (VE-06 deve passar esse parâmetro no link "Emitir solicitação de crédito").
- Novo caso de ação recebe AC-104 em diante; proposta de parâmetro permanece prévia sem envio.
"""
import json, os
from engine import (grid,Pt,kpis,chip,tag,icon,esc,msgbtn,drawer_button,stepper,BTN_ST,EXTRA,EXTRAJS,_MINI,
                    INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,SH,DISP)
import engine as E
from ui37 import shell37, continuity, HEIGHTS37, PARENT37
import dados as D
import dados2 as D2

H=lambda s: '{{'+s+'}}'
OS_ORC='OS-0409'   # fungicida · feijão P1 (95 ha + reaplicação de 25 ha após chuva) · encerrada
SOJA_V2_SC=51280   # previsão V2 de soja 26/27 (GE-02, GE-08, VE-05)
PED={p['id']:p for p in D2.PEDIDOS}; FOR={f['id']:f['nome'] for f in D2.FORNECEDORES}
REQ={r['id']:r for r in D2.REQUISICOES}
PC88=PED['PC-088']; PC88_VAL=round(PC88['qtd']*PC88['preco'])
PC90=PED['PC-090']; PC90_VAL=round(PC90['qtd']*PC90['preco'])

def nf(n,d=0):
    s=f'{n:,.{d}f}'
    return s.replace(',','X').replace('.',',').replace('X','.')
def rs(n,d=0): return 'R$ '+nf(n,d)
def mi(mil): return 'R$ '+nf(mil/1000,2)+' mi'

# ---------- vocabulário visual local (igual ao dos módulos adaptados) ----------
def bloco(titulo,desc,corpo,acao='',tone=None):
    acao=E.recolhe_acoes(titulo,acao)   # MAIS-01 (15/10/2026): uma secundária à vista, as outras no "⋯ Mais ações" do bloco
    desc=''   # 13/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos títulos ... somos minimalistas e essencialistas")
    dot={'yellow':YEL,'red':RED,'gray':'#9AA59E'}.get(tone,ACC)
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; box-shadow: {SH}; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: center; gap: 12px; padding: 12px 16px 10px; flex-wrap: wrap;">'
            f'<span style="width: 9px; height: 9px; border-radius: 999px; background: {dot}; flex-shrink: 0; align-self: flex-start; margin-top: 6px;"></span>'
            f'<div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{esc(titulo)}</h3>'
            f'<div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>'
            f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">{acao}</div></div>'
            f'<div style="padding: 0 12px 12px; display: flex; flex-direction: column; gap: 10px;">{corpo}</div></section>')
def _iconize(html_,text,ic,title):
    html_=html_.replace('style="','style="display: inline-flex; align-items: center; gap: 6px; ',1)
    html_=html_.replace('<button type="button" ',f'<button type="button" title="{esc(title or text)}" ',1)
    return html_.replace('>'+esc(text)+'</button>','>'+icon(ic,14)+esc(text)+'</button>',1)
def ilink(text,href,ic,title=None,primary=False):
    return (f'<a href="{href}" title="{esc(title or text)}" style="{BTN_ST(primary,True)} display: inline-flex; align-items: center; gap: 6px; text-decoration: none;">'
            f'{icon(ic,14)}{esc(text)}</a>')
def imsg(text,msg,ic,title=None,primary=False,small=True):
    return _iconize(msgbtn(text,msg,primary,small),text,ic,title)
def idrawer(text,d,ic,title=None,primary=False,small=True):
    b=drawer_button(text,d,primary,small)
    b=b.replace('style="','style="display: inline-flex; align-items: center; gap: 6px; ',1)
    b=b.replace('<button type="button" ',f'<button type="button" title="{esc(title or text)}" ',1)
    return b.replace('">{{',f'">{icon(ic,14)}{{{{',1)
def ibtn(text,hole,ic,title=None,primary=False,small=True):
    """botão de processo (JS da tela): muda o estado da própria tela."""
    return (f'<button type="button" onClick="{H(hole)}" title="{esc(title or text)}" style="{BTN_ST(primary,small)} display: inline-flex; align-items: center; gap: 6px;">'
            f'{icon(ic,14 if small else 15)}{esc(text)}</button>')
def nota(html_):
    return f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.55;">{html_}</div>'
def kv(pares):
    # SEP-20261015 (e): pares rótulo → valor separados pelo espaço, sem linha entre eles
    return ('<div style="display: grid; grid-template-columns: 200px minmax(0, 1fr); gap: 0; font-size: 13px;">'
            + ''.join(f'<div style="padding: 5px 4px; color: {MUTED}; font-weight: 600;">{esc(k)}</div>'
                      f'<div style="padding: 5px 4px;">{v}</div>' for k,v in pares) + '</div>')
def R(rid,v=None,p=None,s=None,ro=False,o=None,kids=None):
    """linha G2: v = dados, p = exibição rica, s = texto p/ busca/filtro (preenchido a partir de p quando faltar)."""
    v=dict(v or {}); p=dict(p or {}); s=dict(s or {})
    for k,parts in p.items():
        if k not in s: s[k]=' '.join(x.get('t','') for x in parts if x.get('t')).strip()
    d=dict(id=rid,v=v,p=p,s=s,ro=ro)
    if o: d['o']=[(dict(t=t,h=h) if h else dict(t=t)) for t,h in o]
    if kids is not None: d['kids']=kids
    return d
C=lambda k,l,**kw: dict(k=k,l=l,**kw)
F=lambda k,l,**kw: dict(k=k,l=l,**kw)
b,t_,mut,br,link,cta=Pt.b,Pt.txt,Pt.mut,Pt.br,Pt.link,Pt.cta
def ch(t,c='gray'): return Pt.chip(t,c)
def jact(t,fn,u=False):
    """ação de processo na linha: fn 'nome:arg' chama v.nome(arg) no clique (resolvido tarde, depois de EXTRAVALS)."""
    return {'k':'act','t':t,'fn':fn,'u':u}

JS_BASE=r'''
function gsetRow(self,gid,rid,fn){ const sp=GRIDS.find(g=>g.id===gid); if(!sp) return; const rows=g2clone(g2rows(self,sp)); const r=g2find(rows,rid); if(r){ r.p=Object.assign({},r.p||{}); r.s=Object.assign({},r.s||{}); fn(r); } g2set(self,gid,{rows:rows,fl:rid}); }
function gtxt(parts){ return parts.filter(p=>p.t).map(p=>p.t).join(' '); }
function brl(n){ return 'R$ '+Number(n).toLocaleString('pt-BR',{maximumFractionDigits:0}); }
function undate(r,keys){ keys.forEach(k=>{ if(r.s) r.s[k]=r.v[k]; }); }
'''

# =====================================================================================
# GE-01 · Visão gerencial
# =====================================================================================
RESULT=[ # cultura, área ha, volume, unidade, preço (R$/un), receita R$ mil, custo R$ mil, capital com terra R$ mil
 ('Soja',814,SOJA_V2_SC,'sc',121.0,SOJA_V2_SC*121/1000,5845.0,36600),
 ('Milho',176,29920,'sc',61.0,29920*61/1000,1290.0,7900),
 ('Feijão (pivô)',95,4750,'sc',385.0,4750*385/1000,1310.0,5200),
 ('Mamão Formosa',42,1890000,'kg',2.60,1890000*2.60/1000,3690.0,4100),
 ('Café',38,1444,'sc',2480.0,1444*2480/1000,2545.0,3900),
]
CAUSA={'Soja':('Plantio T4 impedido · OM-0233','red'),'Feijão (pivô)':('Pulverização +R$ 1.808','yellow'),'Café':('Lote L27-013 bloqueado','red')}
IR=0.34
def _ge01():
    fname='GE-01.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1180
    rows=[]; trec=tcus=tcap=0
    for cult,ha,vol,un,pr,rec,cus,cap in RESULT:
        mar=rec-cus; roic=mar*(1-IR)/cap*100; cu=cus*1000/vol; trec+=rec; tcus+=cus; tcap+=cap
        vtx=(nf(vol/1000,0)+' t' if un=='kg' else nf(vol)+' sc')
        cutx=('R$ '+nf(cu,2)+'/kg') if un=='kg' else ('R$ '+nf(cu,2)+'/sc')
        c=CAUSA.get(cult)
        rows.append(R(cult,v=dict(cult=cult,ha=ha,rec=round(rec/1000,2),mar=round(mar/1000,2),roic=round(roic,1),cap=round(cap/1000,1)),
            p=dict(cult=[b(cult),br(),mut(vtx+' · previsão V2')],cu=[t_(cutx)],causa=[ch(*c)] if c else [mut('—')]),s=dict(cu=cutx),
            o=[(f'Receita = {vtx} × R$ {nf(pr,2)}/{un} = {mi(rec)}',None),
               (f'Custo = {mi(cus)} da previsão V2 · composição documento a documento','GE-03.dc.html'),
               (f'Margem = receita − custo = {mi(mar)} · custo unitário {cutx}',None),
               (f'ROIC com terra = margem × (1 − 34%) ÷ capital {mi(cap)} = {nf(roic,1)}% · a visão sem terra exclui o valor da terra do capital',None),
               ('Premissas da versão V2 (rendimento e preço)','GE-02.dc.html')]))
    tmar=trec-tcus; troic=tmar*(1-IR)/tcap*100
    g_res=grid([C('cult','Cultura',w=190),C('ha','Área',t='num',a='r',u='ha',agg='sum'),C('rec','Receita',t='num',a='r',d=2,pre='R$ ',u='mi',agg='sum'),
                C('mar','Margem',t='num',a='r',d=2,pre='R$ ',u='mi',agg='sum'),C('cu','Custo unitário',a='r'),C('cap','Capital com terra',t='num',a='r',d=1,pre='R$ ',u='mi',agg='sum'),
                C('roic','ROIC',t='num',a='r',d=1,u='%'),C('causa','Causa prioritária',w=230)],
        sorted(rows,key=lambda r:-r['v']['rec']),edit=dict(m='origin',title='Resultado',fields=[F('ha','Área',ro=True,u='ha'),F('rec','Receita',ro=True,u='R$ mi'),F('mar','Margem',ro=True,u='R$ mi'),F('roic','ROIC com terra',ro=True,u='%')]),
        so={'k':'rec','d':True},gid='g_res',total=True)
    g_cau=grid([C('desvio','Desvio',w=240),C('onde','Onde',w=200),C('efeito','Efeito',w=210),C('orig','Origem do dado'),C('prox','Próxima ação')],
        [R('d1',v=dict(desvio='Custo de pulverização acima do orçado'),p=dict(desvio=[b('Custo de pulverização acima do orçado')],onde=[t_('Feijão · P1'),br(),mut(OS_ORC)],
             efeito=[ch('+R$ 1.808 vs. base V1','red')],orig=[Pt.tag('apontamentos + preço de compra')],prox=[cta('Abrir origem do desvio','GE-02det.dc.html',True)]),
           o=[(f'{OS_ORC} · 120 ha·op × 2,2 L/ha × R$ 22/L = R$ 5.808 contra R$ 4.000 da base V1','GE-02det.dc.html'),('Apontamentos da O.S.','CA-02.dc.html')]),
         R('d2',p=dict(desvio=[b('Plantio parado por ativo bloqueado')],onde=[t_('Soja · T4'),br(),mut('OS-0420 · 30 de 100 ha')],
             efeito=[ch('70 ha de saldo com janela em risco','yellow')],orig=[Pt.tag('OM-0233 · Trator T1')],prox=[cta('Criar ação','GE-07.dc.html')]),
           o=[('OM-0233 · Trator T1 bloqueado · substituto a partir de 24/09','MA.dc.html#om=OM-0233'),('OS-0420 · saldo de 70 ha pausado','CA-01.dc.html')]),
         R('d3',p=dict(desvio=[b('Lote de café bloqueado para venda')],onde=[t_('Armazém Sede'),br(),mut(D.LOTE_BLOQ['id'])],
             efeito=[ch(f'{nf(D.LOTE_BLOQ["sc"])} sc retidas até a inspeção','red')],orig=[Pt.tag('INSP-88')],prox=[cta('Abrir lote','CO-06det.dc.html')]),
           o=[(f'{D.LOTE_BLOQ["id"]} · {D.LOTE_BLOQ["inspecao"]}','CO-06det.dc.html'),('CT-198 e PV-028 dependem do lote','VE-05.dc.html')])],
        edit=dict(m='origin',title='Desvio',fields=[F('desvio','Desvio',ro=True)]),search=False,gid='g_cau',total=False)
    corpo=(kpis([('RECEITA PREVISTA 26/27',mi(trec),'5 culturas · V2'),('MARGEM PROJETADA',mi(tmar),f'{nf(tmar/trec*100,1)}%'),
                 ('ROIC CONSOLIDADO',f'{nf(troic,1)}%','com terra'),('QUALIDADE DOS DADOS','96%','até 22/09')])
        + bloco('Resultado por cultura · grupo consolidado','Confira receita, margem e retorno por cultura; clique numa cultura para ver como cada número é calculado.',g_res,
                acao=ilink('Comparar cenário','GE-02.dc.html','trend','Comparar a previsão V2 com a base V1 e os cenários'))
        + bloco('Causas prioritárias do período','Abra a origem de cada desvio até o documento que o sustenta.',g_cau,tone='yellow'))
    shell37('GE-01','Visão gerencial',corpo,
      subtitle='Grupo › empresa › fazenda › cultura — resultado, capital e causas com documento de origem (DRE/DFC/ROIC por cultura e consolidado).',
      primary='Abrir composição do resultado',primary_href='GE-03.dc.html',
      footer='Qualidade dos dados acompanha cada número: valor não conciliado aparece como provisório, nunca escondido.')

# =====================================================================================
# GE-02 · Orçamento e previsões  +  GE-02det
# =====================================================================================
def _ge02():
    fname='GE-02.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=960
    ver_rows=[
      R('V1',ro=True,v=dict(ver='V1 · base aprovada',prem='rendimento 62 sc/ha · câmbio 5,20',vol=50470,preco=118,custo=14.25,pico='R$ 6,1 mi · fev/27',aprov='Direção · 12/08'),
        p=dict(ver=[b('V1 · base aprovada')],estado=[ch('Aprovada · preservada','green'),br(),mut('Direção · 12/08')]),s=dict(estado='Aprovada · preservada')),
      R('V2',ro=True,v=dict(ver='V2 · previsão corrente',prem='rendimento 63 sc/ha · preços atualizados',vol=SOJA_V2_SC,preco=121,custo=14.68,pico='R$ 6,4 mi · fev/27',aprov='Controladoria · 20/09'),
        p=dict(ver=[b('V2 · previsão corrente')],estado=[ch('Publicada ao planejamento','green'),br(),mut('Controladoria · 20/09')]),s=dict(estado='Publicada ao planejamento')),
      R('C1',v=dict(ver='C1 · seca out/nov',prem='rendimento −8% · irrigação +20%',vol=47180,preco=126,custo=14.91,pico='R$ 7,0 mi · mar/27',aprov='—'),
        p=dict(estado=[ch('Cenário · rascunho','gray')]),s=dict(estado='Cenário · rascunho')),
    ]
    g_ver=grid([C('ver','Versão',w=190),C('prem','Premissas',w=210),C('vol','Volume soja',t='num',a='r',u='sc'),C('preco','Preço soja (R$/sc)',t='num',a='r',d=2),
                C('custo','Custo total',t='num',a='r',d=2,pre='R$ ',u='mi'),C('pico','Pico de caixa'),C('estado','Estado · aprovação',w=220)],
        ver_rows,edit=dict(m='form',title='Versão',newTitle='Criar cenário',
            sub='Ajuste as premissas do cenário em rascunho. Versões aprovadas ou publicadas abrem em consulta: revisar gera versão nova com aprovador e vigência.',
            fields=[F('ver','Nome do cenário',t='txt',req=True,help='Ex.: C2 · seca em out/nov'),F('prem','Premissa alterada',t='area',req=True,help='Ex.: rendimento soja −8%'),
                    F('vol','Volume soja',t='num',req=True,min=0,u='sc'),F('preco','Preço médio soja',t='num',req=True,min=1,u='R$/sc'),
                    F('custo','Custo total',t='num',req=True,min=0,u='R$ mi')]),
        add=None,gid='g_ver',total=False)
    cx=[('q1','out–dez/26',5.90,6.20,'insumos de plantio'),('q2','jan–mar/27',4.80,4.90,'defensivos e colheita da soja'),
        ('q3','abr–jun/27',2.10,2.10,'beneficiamento e frete'),('q4','jul–set/27',1.45,1.48,'colheita do café e armazenagem')]
    g_cx=grid([C('tri','Trimestre'),C('v1','Desembolso V1',t='num',a='r',d=2,pre='R$ ',u='mi',agg='sum'),C('v2','Desembolso V2',t='num',a='r',d=2,pre='R$ ',u='mi',agg='sum'),
               C('dif','Diferença',t='num',a='r',d=2,pre='R$ ',u='mi',agg='sum',zdash=True),C('comp','Maior componente',w=240)],
        [R(i,v=dict(tri=tr,v1=a,v2=bb,dif=round(bb-a,2),comp=cp),o=[(f'V1 {nf(a,2)} mi · V2 {nf(bb,2)} mi · componentes com quantidade × preço',None),('Composição de custos','GE-03.dc.html')]) for i,tr,a,bb,cp in cx],
        edit=dict(m='origin',title='Trimestre',fields=[F('tri','Trimestre',ro=True),F('v1','Desembolso V1',ro=True,u='R$ mi'),F('v2','Desembolso V2',ro=True,u='R$ mi')]),
        search=False,gid='g_cx',total=True)
    EXTRAJS[0]=JS_BASE+r'''
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{ if(gid!=='g_ver'||!r) return;
  if(String(r.id).indexOf('n')===0){ const n=rows.filter(x=>String(x.id).indexOf('n')===0).length; r.v.aprov='—'; r.v.pico='a calcular'; r.p.estado=[{k:'chip',t:'Cenário · rascunho',c:'gray'}]; r.s.estado='Cenário · rascunho';
    self.setState({g2toast:'Cenário '+r.v.ver+' criado em rascunho · parte da V2; a base V1 não muda.'}); }
  else self.setState({g2toast:'Cenário '+r.v.ver+' salvo · premissas atualizadas; V1 e V2 permanecem como estão.'}); }; }'''
    corpo=(
      bloco('Versões em paralelo','Compare a base aprovada com a previsão corrente e os cenários; clique num cenário em rascunho para ajustar as premissas.',g_ver,
            acao=ibtn('Criar cenário','g_ver_new','layers','Criar um cenário a partir da V2 sem alterar a base')
                 +imsg('Recalcular previsão','Previsão V2 recalculada com preços de compra e apontamentos até 22/09 · nenhum número da base V1 alterado.','calc','Recalcular a V2 com os fatos até hoje'))
      + bloco('Cronograma de caixa por versão','Confira o desembolso trimestral de cada versão; o total fecha com o custo total da versão.',g_cx)
      + bloco('Publicação','Submeta a revisão à Direção e publique a previsão para planejamento, programação e compras.',
          '<div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">'
          + E.recolhe_acoes('Publicação',[imsg('Submeter orçamento revisado','Submetido à Direção · +R$ 180 mil em defensivos · aparece em Aprovações para decisão.','doc','Enviar a revisão para a Direção decidir')
          ,imsg('Publicar previsão V2','Previsão V2 publicada para planejamento, programação e compras · consumidores passam a ler a nova versão; histórico mantém as anteriores.','check','Publicar a V2 aos consumidores')
          ,imsg('Autorizar versão','Bloqueado · só a alçada Direção autoriza a versão — a submissão já está na caixa de Aprovações.','users','Autorizar a versão (alçada da Direção)')])
          + '</div>',tone='gray'))
    shell37('GE-02','Orçamento e previsões',corpo,
      subtitle='Orçado original, revisado e realizado em quantidade, preço e custo — total, por ha e por unidade, com ponte de variações que concilia ao total.',
      status=('V2 publicada · 1 cenário em rascunho','green'),
      primary='Comparar base × previsão × real',primary_href='GE-02det.dc.html',
      footer='Base V1 aprovada permanece imutável; revisão gera versão nova com aprovador e vigência (cap. 51). '
             'Autorizar versão: só a Direção, pela caixa de Aprovações.')

    # ---- GE-02det · V1 × V2 × real com decomposição (DEMO-12) ----
    fname='GE-02det.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1000; PARENT37[fname]='GE-02.dc.html'
    def gr(rid,nome,v1,v2,real,dif,difc,fonte,orig):
        return R(rid,v=dict(g=nome,v1=v1,v2=v2,real=real),p=dict(g=[b(nome)],real=[b(real)],dif=[ch(dif,difc)] if difc else [t_(dif)],fonte=[Pt.tag(fonte)]),o=orig)
    g_cmp=grid([C('g','Grandeza',w=170),C('v1','Orçado V1'),C('v2','Previsão V2'),C('real','Real (encerrada)'),C('dif','Diferença V1→real'),C('fonte','Fonte')],
      [gr('a','Área tratada','100 ha·operação','110 ha·operação','120 ha·operação','+20 ha·op',None,'apontamentos',[(f'{OS_ORC} · 95 ha do P1 + 25 ha reaplicados após chuva','CA-02.dc.html')]),
       gr('c','Consumo unitário','2,0 L/ha','2,1 L/ha','2,2 L/ha','+10% vs. base','yellow','apontamentos',[('264 L ÷ 120 ha·op = 2,2 L/ha','CA-02.dc.html')]),
       gr('p','Preço do produto','R$ 20,00/L','R$ 21,00/L','R$ 22,00/L','+R$ 2,00/L',None,'recebimento NF 8842',[('NF 8842 · 05/09 · R$ 22,00/L','SU-06.dc.html')]),
       gr('v','Volume total','200 L','231 L','264 L','+64 L',None,'requisições',[('Requisições da OS-0409 · 264 L retirados','SU-07.dc.html')]),
       gr('t','Custo total','R$ 4.000','R$ 4.851','R$ 5.808','+R$ 1.808','red','lançamento de custo',[('264 L × R$ 22,00 = R$ 5.808','GE-03.dc.html')]),
       gr('h','Custo por ha tratado','R$ 40,00/ha','R$ 44,10/ha','R$ 48,40/ha','+R$ 8,40/ha',None,'cálculo',[('R$ 5.808 ÷ 120 ha·op = R$ 48,40/ha',None),('Indicador de custo de pulverização','GE-06det.dc.html')])],
      edit=dict(m='origin',title='Grandeza',fields=[F('v1','Orçado V1',ro=True),F('v2','Previsão V2',ro=True),F('real','Real',ro=True)]),search=False,gid='g_cmp',total=False)
    ponte=(f'<div style="display: flex; gap: 10px; align-items: stretch; text-align: center; font-size: 12.5px;">'
      +''.join(f'<div style="flex: 1 1 0; border: 1px solid {LINE}; border-radius: 12px; padding: 10px; background: {bg};">'
               f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .05em; color: {MUTED};">{t}</div>'
               f'<div style="font-size: 17px; font-weight: 800; margin-top: 4px; color: {cor};">{v}</div>'
               f'<div style="color: {MUTED}; margin-top: 2px;">{s}</div></div>'
        for t,v,s,cor,bg in [('ORÇADO V1','R$ 4.000','100 ha·op × 2 L/ha × R$ 20/L',INK,SURF),('+ VOLUME','+R$ 800','120 ha·op no padrão orçado',INK,GRAYS),
                             ('+ CONSUMO','+R$ 480','2,2 L/ha vs. 2,0 L/ha','#8A5A00','#FFF7E0'),('+ PREÇO','+R$ 528','R$ 22/L vs. R$ 20/L','#8A5A00','#FFF7E0'),
                             ('= REAL','R$ 5.808','264 L · dif. total +R$ 1.808',RED,'#FDECEE')])
      +'</div>'
      + nota(f'Orçamento flexível para os 120 ha·op ao padrão original = <b style="color:{INK};">R$ 4.800</b>; desvio contra essa base = <b style="color:{INK};">R$ 1.008</b>.'))
    prop=imsg('Conferir proposta de parâmetro', 'Prévia · nada foi alterado. O envio de um novo parâmetro para revisão agronômica ainda não está disponível neste protótipo. Consulte os documentos de origem; nenhum consumo, versão ou aprovação foi alterado.', 'leaf', 'Ver disponibilidade da proposta de parâmetro')
    estado=nota('Prévia de análise · não há envio de proposta para revisão agronômica nesta tela.')
    EXTRAJS[0]=JS_BASE
    corpo=(
      continuity('Orçamento · versões da safra 26/27',f'Comparação V1 × V2 × real — fungicida no feijão P1 ({OS_ORC})','entender causa e decidir parâmetro','Criar ação do desvio')
      + bloco('Orçado V1 × previsão V2 × real','Compare quantidade, consumo e preço de cada grandeza; clique numa linha para ver a origem do número.',g_cmp)
      + bloco('Ponte de variações','Confira a ponte: R$ 800 volume + R$ 480 consumo + R$ 528 preço = R$ 1.808.',ponte)
      + bloco('Decisão sobre a causa','Proponha o novo parâmetro com vigência futura ou abra os documentos para investigar.',estado,
              acao=prop+ilink('Abrir documentos de origem','GE-06det.dc.html','doc','Abrir o indicador com documentos de origem')
                   +ilink('Ver apontamentos da O.S.','CA-02.dc.html','check',f'Abrir os apontamentos da {OS_ORC}')))
    shell37('GE-02','Comparar · V1 × V2 × real',corpo,fname=fname,crumbs_extra=[OS_ORC],
      subtitle='Decomposição do desvio em quantidade, consumo e preço — base aprovada preservada.',
      status=('Desvio de +R$ 1.808 na operação','yellow'),
      primary='Criar ação do desvio',primary_href='GE-07.dc.html',
      footer='Base preservada: proposta de parâmetro tem vigência futura e passa por revisão; nada recalcula versões aprovadas (cap. 51). '
             'A matemática explica o desvio, mas não prova desperdício: pode ser ajuste técnico autorizado, condição operacional ou erro de registro a investigar.')

# =====================================================================================
# GE-03 · Custos e fechamento
# =====================================================================================
RATEIOS=['direto','por horímetro','por ativo','por h apontada','por área','por tonelada transportada','Sem versão de rateio']
def _ge03():
    fname='GE-03.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1040
    r36=REQ['REQ-036']; r35=REQ['REQ-035']
    L=[ # id, origem(doc), href, componente, dimensões, qtd×preço texto, valor, rateio, estado, cor, ro
     ('nf8842','NF 8842 · recebimento','SU-06.dc.html','Defensivo · fungicida',f'Feijão · P1 · {OS_ORC}','264 L × R$ 22,00',264*22,'direto','Definitivo','green',True),
     ('req35','REQ-035 · OS-0421','SU-07.dc.html','Defensivo · Fungicida A','Soja · T1+T2 · OS-0421',f'{r35["consumido"]} L × R$ 145,00',r35['consumido']*145,'direto','Definitivo','green',True),
     ('ap21','Apontamento · OS-0421','CA-02.dc.html','Máquina e equipe · pulverização','Soja · T1+T2 · OS-0421','8,8 h × R$ 313,00',round(8.8*313),'por horímetro','Definitivo','green',True),
     ('req36','REQ-036 · OS-0420','SU-07.dc.html','Semente · soja 58 W','Soja · T4 · OS-0420 (30 ha)',f'{nf(r36["consumido"])} kg × R$ 9,50',r36['consumido']*9.5,'direto','Definitivo','green',True),
     ('req37','REQ-037 · OS-0420','SU-07.dc.html','Fertilizante · KCl 60%','Soja · T4 · OS-0420 (30 ha)','3.600 kg × R$ 2,40',3600*2.4,'direto','Definitivo','green',True),
     ('ap20','Apontamento · OS-0420','CA-02.dc.html','Máquina e equipe · plantio','Soja · T4 · OS-0420 (30 ha)','6,0 h × R$ 396,00',round(6*396),'por horímetro','Provisório · 12 ha a conferir','yellow',False),
     ('die20','Abastecimento · Trator T1','MA.dc.html#vis=ativos&modo=abastecimentos','Diesel S10','Soja · T4 · OS-0420','84 L × R$ 5,92',round(84*5.92,2),'direto','Provisório · conciliar tanque','yellow',False),
     ('om233','OM-0233','MA.dc.html#om=OM-0233','Manutenção corretiva','Máquinas · Trator T1','peças + 6,5 h',18400,'por ativo','Provisório · aguarda NF','yellow',False),
     ('frete','Romaneio de frete','LO-04.dc.html','Frete de insumos','comum · 3 entregas','12,4 t × R$ 118,00',round(12.4*118),'Sem versão de rateio','Bloqueia fechamento','red',False),
     ('folha','Folha 09/26',None,'Mão de obra operacional','rateio por apontamento','—',None,'por h apontada','Definitivo','green',True),
    ]
    rows=[]; prov=0
    for rid,doc,href,comp,dim,qp,val,rat,est,cor,ro in L:
        if cor!='green' and val: prov+=val
        p=dict(doc=[link(doc,href)] if href else [Pt.tag(doc)],est=[ch(est,cor)])
        if rat=='Sem versão de rateio': p['rat']=[ch(rat,'red')]
        o=[(f'{doc} · {comp}',href)] if href else [('Folha 09/26 · rateada pelas horas apontadas',None)]
        if rid.endswith('20'): o.append(('Ordem OS-0420 · plantio T4 · 30 de 100 ha','CA-01.dc.html'))
        rows.append(R(rid,ro=ro,v=dict(comp=comp,dim=dim,qp=qp,val=val if val is not None else '',rat=rat,obs=''),p=p,s=dict(est=est),o=o))
    g_lan=grid([C('doc','Origem (documento)',w=190),C('comp','Componente',w=170),C('dim','Dimensões',w=185),C('qp','Qtd × preço',a='r'),
                C('val','Valor',t='num',a='r',pre='R$ ',zdash=True),C('rat','Rateio'),C('est','Estado',w=200)],
        rows,edit=dict(m='form',title='Lançamento',sub='Corrija dimensões e rateio do lançamento provisório. Lançamento definitivo abre em consulta: correção só por estorno + relançamento.',
            fields=[F('comp','Componente',ro=True),F('qp','Qtd × preço',ro=True),F('dim','Dimensões',t='txt',req=True,help='Natureza · centro · cultura · talhão · operação · ativo'),
                    F('rat','Rateio',t='sel',opts=RATEIOS,req=True),F('obs','Observação',t='area',help='Motivo da correção; fica na trilha do lançamento.')]),
        gid='g_lan',total=False)
    EXTRAJS[0]=JS_BASE+r'''
function EXTRAVALS(self,v){ const dz=!!self.state.dz;
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_lan'||!r) return; if(r.v.rat==='Sem versão de rateio'){ r.p.rat=[{k:'chip',t:r.v.rat,c:'red'}]; }
    else if(r.id==='frete'){ r.p.est=[{k:'chip',t:'Rateio versionado · v1',c:'green'}]; r.s.est='Rateio versionado'; self.setState({frt:true}); }
    self.setState({g2toast:'Lançamento corrigido · nova versão registrada; o original fica na trilha.'}); };
  const frt=!!self.state.frt; const pend=[]; if(!frt) pend.push('frete sem versão de rateio'); if(!dz) pend.push('diesel sem conciliação de tanque');
  v.fech_hint=pend.length?('Fechar está bloqueado: '+pend.join(' e ')+'.'):'Pendências tratadas: a revisão e o fechamento estão liberados.';
  v.fechar=()=>{ if(self.state.fch){ self.setState({g2toast:'Competência 09/2026 já fechada · nenhum lançamento novo entra; correção só por estorno + relançamento.'}); return; }
    if(pend.length){ self.setState({g2toast:'Bloqueado · '+pend.length+' pendência(s) obrigatória(s): '+pend.join(' e ')+' — trate e o fechamento libera.'}); return; }
    self.setState({fch:true,g2toast:'Competência 09/2026 fechada · exportação ao ERP na fila; reabrir exige motivo e aprovação.'}); };
  v.conc_diesel=()=>{ if(dz){ self.setState({g2toast:'Diesel já conciliado · medição 22/09 · nada lançado de novo.'}); return; }
    gsetRow(self,'g_lan','die20',r=>{ r.ro=true; r.p.est=[{k:'chip',t:'Definitivo · conciliado',c:'green'}]; r.s.est='Definitivo'; });
    self.setState({dz:true,g2toast:'Conciliado · medição do tanque em 22/09 confere com os abastecimentos apontados (dif. 0,7%, dentro da tolerância de 1%) · lançamento vira definitivo.'}); }; }'''
    fech=(stepper([('Coleta e apontamentos','done'),('Conciliações','now'),('Rateios versionados','now'),('Revisão e fechamento','todo'),('Exportação ERP','todo')],'')
          + f'<div role="status" style="font-size: 13.5px; font-weight: 700; color: {INK};">{H("fech_hint")}</div>')
    # LEVE-1 (proprietário 19/10): sai o botão "Conferir reabertura de 08/2026" (prévia sem efeito: "nada foi alterado")
    corpo=(kpis([('COMPETÊNCIA','09/2026','fecha 05/10'),('LANÇAMENTOS','1.412','98% com doc.'),
                 ('PROVISÓRIOS',rs(prov),f'{sum(1 for x in L if x[9]!="green")} lançamentos'),('CONCILIAÇÃO ERP','OK até 21/09','14 na fila')])
        + bloco('Composição de custos · setembro/2026','Confira cada lançamento até o documento de origem; clique num lançamento provisório para corrigir dimensões ou rateio.',g_lan,
                acao=imsg('Exportar para ERP','Exportação simulada · 1.402 lançamentos definitivos enviados ao ERP designado; provisórios ficam retidos até a conciliação.','doc','Exportar os lançamentos definitivos ao ERP'))
        + bloco('Fechamento da competência','Trate as pendências obrigatórias e feche; parâmetro futuro não recalcula período fechado sem revisão autorizada.',fech,
                acao=ibtn('Conciliar diesel do tanque','conc_diesel','fuel','Conciliar a medição do tanque com os abastecimentos apontados'),tone='red'))
    shell37('GE-03','Custos e fechamento',corpo,
      subtitle='Composição por natureza, centro, cultura, ciclo, talhão, operação e ativo — total, R$/ha e R$/unidade com denominador e conciliação explícitos.',
      status=('2 pendências bloqueiam o fechamento','red'),
      primary_html=ibtn('Fechar competência 09/2026','fechar','check','Fechar a competência (exige as pendências tratadas)',primary=True,small=False),
      footer='Correção nunca apaga: estorno + relançamento preservam o histórico e o rastro até o documento (cap. 51).')

# =====================================================================================
# GE-04 · Contas a pagar e caixa
# =====================================================================================
CONTAS=['Banco Terra · movimento','Coop Crédito · conta safra','Caixa interno']
def _ge04():
    fname='GE-04.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1200
    c=D.CRE; forn88=FOR[PC88['f']]; forn90=FOR[PC90['f']]
    def T(rid,cred,doc,sub,venc_iso,prz,prz_det,princ,pago,conc,cor,acao,ro=False,o=None,prog='',conta=CONTAS[0]):
        return R(rid,ro=ro,v=dict(cred=cred,venc=venc_iso,princ=princ,prog=prog,conta=conta,obs=''),
                 p=dict(cred=[b(cred),br(),Pt.tag(doc)],orig=[mut(sub)],venc=[Pt.chip(prz,{'vence hoje':'orange','atrasada':'red','até 3 dias':'yellow','no prazo':'green'}[prz])]+([br(),mut(prz_det)] if prz_det else []),
                        princ=[t_(rs(princ)),br(),mut(pago)],conc=[ch(conc.split('|')[0],cor)]+([br(),mut(conc.split('|')[1])] if '|' in conc else [])+([br()]+acao if acao else [])),
                 s=dict(cred=f'{cred} {doc}',venc=venc_iso,prog=prog,conc=conc.replace('|',' · ')),o=o)
    rows=[
      T('agn','Agro Norte','NF 8790 · 2/3','PC-084 · defensivos safra 26/27','2026-09-23','vence hoje','',96000,'0 / R$ 96.000','Proposto · aguarda alçada','yellow',
        [cta('Abrir aprovação','IN-02.dc.html')],o=[('NF 8790 · parcela 2 de 3 · alçada do Gerente da fazenda (até R$ 300 mil)','IN-02.dc.html')],prog='2026-09-23'),
      T('ipi','Ipiranga Agro','NF 5531','diesel S10 · CT-2026-03 · tanque sede','2026-09-23','vence hoje','',62000,'0 / R$ 62.000','Aguardando banco|remessa enviada','yellow',
        [jact('Importar retorno','retorno:ipi')],o=[('Contrato CT-2026-03 · diesel','SU-05.dc.html')],prog='2026-09-23'),
      T('fer',forn88,f'NF 4501 · {PC88["id"]}',f'{PC88["item"]} · {nf(PC88["qtd"]/1000)} t × R$ 2,33/kg · título único, sem barter','2026-10-17','no prazo','17/10',PC88_VAL,f'0 / {rs(PC88_VAL)}','Aprovado na alçada','green',
        [cta('Abrir pedido','SU-05.dc.html')],o=[(f'Pedido {PC88["id"]} · {forn88} · {nf(PC88["qtd"]/1000)} t × R$ 2,33/kg = {rs(PC88_VAL)}','SU-05.dc.html'),
          (f'Título único de {rs(PC88_VAL)} · sem barter · 28 dias após a NF 4501 (19/09)',None)],prog='2026-10-17'),
      T('hid','Oficina HidroMec','NF 1203','OM-0233 · corretiva do Trator T1','2026-10-05','no prazo','05/10',18400,'0 / R$ 18.400','A propor|NF conferida','gray',
        [jact('Propor pagamento','propor:hid')],o=[('OM-0233 · manutenção corretiva','MA.dc.html#om=OM-0233')]),
      T('sem',forn90,f'{PC90["id"]} · NF 4533 a conferir',f'{PC90["item"]} · {nf(PC90["qtd"]/1000)} t × R$ 9,30/kg','2027-04-30','no prazo','safra · 30/04/27',PC90_VAL,f'previsão · {rs(PC90_VAL)}','Previsão|título nasce na conferência','gray',
        [cta('Abrir pedido','SU-05.dc.html')],ro=True,o=[(f'Pedido {PC90["id"]} · entrega prevista {PC90["previsao"]}','SU-05.dc.html')]),
      T('coo','Cooperativa Central','CT-77 · antecipação','venda VD-2101 · milho 111 t · abate nas retiradas','2026-10-30','no prazo','30/10',101800,'R$ 100.000 recebidos','Crédito vinculado|abate nas retiradas','green',
        [cta('Ver retiradas','LO-01.dc.html')],ro=True,o=[('Antecipação aprovada criou crédito vinculado: R$ 100.000 + R$ 1.800 de encargos, abatidos nas 3 retiradas da VD-2101','LO-01.dc.html')]),
      T('cre','Banco Terra',f'{c["id"]} · parc. 1','crédito de custeio · 1ª liberação','2026-12-15','no prazo','15/12',300000,f'0 / liberado {c["liberado"]}','Conciliado','green',
        [cta('Abrir crédito','GE-08.dc.html')],ro=True,o=[(f'{c["id"]} · liberação da 1ª parcela é fato financeiro próprio','GE-08.dc.html')]),
    ]
    g_tit=grid([C('cred','Credor · documento',w=180),C('orig','Origem',w=185),C('venc','Vencimento',t='date',w=130),C('princ','Principal · pago / saldo',t='num',a='r',pre='R$ ',w=170),
                C('prog','Programado',t='date'),C('conc','Conciliação · próxima ação',w=200)],
        rows,edit=dict(m='form',title='Título',sub='Programe data e conta de saída. Credor, valor e vencimento vêm do ERP designado; título conciliado ou previsão abre em consulta.',
            fields=[F('cred','Credor',ro=True),F('princ','Principal',t='num',ro=True,u='R$'),F('venc','Vencimento',t='date',ro=True),
                    F('prog','Pagamento programado',t='date',req=True,help='Não antes do vencimento sem desconto negociado.'),F('conta','Conta de saída',t='sel',opts=CONTAS,req=True),
                    F('obs','Observação',t='area')]),
        so={'k':'venc','d':False},gid='g_tit',total=False)
    EXTRAJS[0]=JS_BASE+r'''
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_tit'||!r) return; undate(r,['prog']); self.setState({g2toast:'Programação salva · pagamento em '+(r.v.prog||'').split('-').reverse().join('/')+' pela conta '+r.v.conta+'; nada é pago antes da remessa e do retorno do banco.'}); };
  v.remessa=()=>{ if(self.state.rem){ self.setState({g2toast:'Remessa REM-2609-02 já enviada · mesmo recibo devolvido · nada reenviado ao banco.'}); return; }
    gsetRow(self,'g_tit','fer',r=>{ r.p.conc=[{k:'chip',t:'Aguardando banco',c:'yellow'},{k:'br',t:''},{k:'mut',t:'remessa REM-2609-02'}]; r.s.conc='Aguardando banco'; });
    self.setState({rem:true,g2toast:'Remessa REM-2609-02 enviada · Fertisul PC-088 (título único de R$ 233.000, programado para 17/10) fica “Aguardando banco” — nada aparece pago antes do retorno. NF 8790 não entrou: ainda aguarda a alçada.'}); };
  v.retorno=()=>{ if(self.state.ret){ self.setState({g2toast:'Retorno já importado · NF 5531 liquidada · nada lançado de novo.'}); return; }
    gsetRow(self,'g_tit','ipi',r=>{ r.ro=true; r.p.princ=[{k:'txt',t:'R$ 62.000'},{k:'br',t:''},{k:'mut',t:'R$ 62.000 / 0'}]; r.p.conc=[{k:'chip',t:'Liquidado · conciliado',c:'green'},{k:'br',t:''},{k:'mut',t:'1 divergência de R$ 12,40'}]; r.s.conc='Liquidado'; });
    self.setState({ret:true,g2toast:'Retorno importado · NF 5531 (R$ 62.000) liquidada e conciliada com o extrato; 1 divergência de R$ 12,40 aberta para tratamento.'}); };
  v.propor=(rid)=>{ const pr=Object.assign({},self.state.prop||{}); if(pr[rid]){ self.setState({g2toast:'Pagamento já proposto · aguarda a alçada · nada duplicado.'}); return; }
    pr[rid]=1; gsetRow(self,'g_tit',rid,r=>{ r.p.conc=[{k:'chip',t:'Proposto · aguarda alçada',c:'yellow'},{k:'br',t:''},{k:'cta',t:'Abrir aprovação',h:'IN-02.dc.html'}]; r.s.conc='Proposto'; });
    self.setState({prop:pr,g2toast:'Pagamento proposto · NF 1203 (R$ 18.400) entra na alçada do Gestor de suprimentos (até R$ 50 mil) · aparece em Aprovações.'}); }; }'''
    corpo=(kpis([('CAIXA HOJE','R$ 1,84 mi','2 contas'),('VENCE HOJE','R$ 158 mil','2 títulos'),
                 ('AGUARDANDO BANCO','R$ 62 mil','1 remessa'),('SALDO PROJETADO 30 D','R$ 1,31 mi','cenário V2')])
        + bloco('Títulos a pagar','Confira cada título até a origem; clique num título em aberto para programar data e conta de saída.',g_tit,
                acao=ibtn('Importar retorno do banco','retorno','doc','Importar o retorno bancário e conciliar as liquidações'))
        + nota(f'{PC88["id"]}: título único de {rs(PC88_VAL)}, sem barter. '
               f'Antecipação da Cooperativa Central (CT-77) criou <b style="color:{INK};">crédito vinculado</b> abatido nas retiradas.'))
    shell37('GE-04','Contas a pagar e caixa',corpo,
      subtitle='Títulos e previsões com vencimento, parcelas, origem e antecipações — saldo de caixa por cenário do orçamento.',
      status=('R$ 158 mil vencem hoje · 1 aguarda alçada','yellow'),
      primary_html=ibtn('Enviar remessa ao banco','remessa','cash','Enviar ao banco os títulos aprovados na alçada',primary=True,small=False),
      footer='Todo título rastreia à origem (pedido, O.S., contrato); conciliação bancária fecha o ciclo antes de qualquer “pago”. '
             'Fonte oficial: ERP designado; aqui se propõe, aprova e concilia, e a liquidação vem confirmada do banco. A mesma obrigação nunca conta duas vezes; o sistema não finge recebimento de venda futura.')

# =====================================================================================
# GE-05 · Contas a receber (DEMO-08: RC-12 · PV-027)
# =====================================================================================
CANAIS=['Telefone','E-mail','WhatsApp','Portal do cliente']
def _ge05():
    fname='GE-05.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1250
    pv27=round(3000*2.95); rc12=round(300*2.95); pv26=round(9400*3.00); rc15=round(400*3.00); pv29=4000*61; pv30=8000*128; pv31_t=D.PREVISAO['futuras_A']; pv31=round(pv31_t*1000*3.05)
    def T(rid,doc,ped,det_orig,venc,prz,det,val,saldo,div,divc,caso,cdet,ro=False,o=None,cob=''):
        return R(rid,ro=ro,v=dict(tit=doc,venc=venc,val=val,saldo=saldo,cob=cob,canal='E-mail',obs=''),
                 p=dict(tit=[b(doc)],orig=[link(ped,'VE-04.dc.html'),br(),mut(det_orig)],
                        venc=[Pt.chip(prz,{'vence hoje':'orange','atrasada':'red','até 3 dias':'yellow','no prazo':'green','recebido':'gray'}[prz])]+([br(),mut(det)] if det else []),
                        div=([ch(div,divc),br(),link(caso,'VE-06.dc.html'),mut(' · '+cdet)] if div else [mut('—')])),s=dict(venc=venc,cob=cob),o=o)
    def CL(cid,nome,kids):
        return R(cid,ro=True,v=dict(tit=nome,val=sum(k['v']['val'] for k in kids),saldo=sum(k['v']['saldo'] for k in kids)),p=dict(tit=[b(nome)],orig=[mut(f'{len(kids)} título(s)')]),kids=kids)
    cli=[
      CL('atb','Atacado Bom Preço',[T('f2090','FAT-2090','PV-029','milho 4.000 sc × R$ 61','2026-09-19','atrasada','4 d',pv29,pv29,
          'Aguarda evidências','yellow','RC-14','150 sc ardidos',o=[('Pedido PV-029 · entregue em 05/09 · CIF 14 d','VE-04.dc.html'),('Caso RC-14 · grãos ardidos','VE-06.dc.html')],cob='2026-09-24')]),
      CL('rhb','Rede Hortifrúti BA',[
          T('f2088','FAT-2088','PV-027','entrega 1/2 · mamão A 3,0 t','2026-10-05','no prazo','05/10',pv27,pv27,'','','','',
            o=[('Pedido PV-027 · 6,0 t × R$ 2,95/kg · CIF 21 d · entrega 1 de 2 em 14/09','VE-04.dc.html')]),
          T('f2096','FAT-2096','PV-027','entrega 2/2 · mamão A 3,0 t','2026-10-11','no prazo','11/10',pv27,pv27,'Crédito solicitado','red','RC-12',f'300 kg · {rs(rc12)}',
            o=[('Pedido PV-027 · entrega 2 de 2 em 20/09 · o pedido original não muda','VE-04.dc.html'),
               (f'Caso RC-12 · retorno de 300 kg do lote L26-118 recebido bloqueado · crédito de 300 kg × R$ 2,95/kg = {rs(rc12)}','VE-06.dc.html')])]),
      CL('frr','Frutas Real',[T('f2112','FAT-2112','PV-026','VG-117 · mamão A 9,4 t','2026-10-20','no prazo','20/10',pv26,pv26,'Recusa 0,4 t · a definir','yellow','RC-15',rs(rc15),
          o=[('Viagem VG-117 · 9,0 t aceitas e 0,4 t recusadas por avaria (OC-77)','LO-03.dc.html'),('Caso RC-15 · recusa parcial','VE-06.dc.html'),
             (f'Próximo faturamento: PV-031 · mamão Formosa classe A · {nf(pv31_t,1)} t × R$ 3,05/kg = {rs(pv31)} · título nasce no faturamento','VE-04.dc.html')])]),
      CL('cgs','Coop Grão Sul',[T('f2079','FAT-2079','PV-030','soja 8.000 sc × R$ 128 · contra entrega','2026-09-15','recebido','15/09 · conciliado',pv30,0,
          'Retorno a caminho','yellow','RC-13','900 sc · umidade',ro=True,o=[('Recebido e conciliado com o extrato de 15/09',None),('Caso RC-13 · umidade acima do padrão','VE-06.dc.html')])]),
    ]
    tot_aberto=pv29+2*pv27+pv26
    g_rec=grid([C('tit','Cliente · título',w=190),C('orig','Pedido · entrega',w=205),C('venc','Vencimento',t='date',w=130),C('val','Valor',t='num',a='r',pre='R$ ',agg='sum'),
                C('saldo','Saldo',t='num',a='r',pre='R$ ',agg='sum',zdash=True),C('div','Divergência · caso',w=195),C('cob','Próxima cobrança',t='date')],
        cli,edit=dict(m='form',leafOnly=True,title='Título',sub='Registre a próxima cobrança autorizada. Valor e vencimento vêm do faturamento; divergência se trata pelo caso, nunca editando o pedido original. Título recebido abre em consulta.',
            fields=[F('tit','Título',ro=True),F('val','Valor',t='num',ro=True,u='R$'),F('cob','Próxima cobrança',t='date',req=True),F('canal','Canal autorizado',t='sel',opts=CANAIS,req=True),
                    F('obs','Registro da cobrança',t='area',help='O que foi combinado; fica no histórico do título.')]),
        tree=True,gid='g_rec',total=True)
    EXTRAJS[0]=JS_BASE+r'''
function PREVALS(self,v){ if(!self._q0){ self._q0=1; try{ const m=/[?&#]caso=([A-Za-z0-9-]+)/.exec((location.search||'')+(location.hash||'')); if(m){ const q=m[1].toUpperCase(); setTimeout(()=>g2set(self,'g_rec',{q:q}),0); } }catch(e){} } }
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_rec'||!r) return; undate(r,['cob']); self.setState({g2toast:'Cobrança registrada no histórico do '+r.v.tit+' · '+r.v.canal+' · próxima em '+(r.v.cob||'').split('-').reverse().join('/')+' · simulado, nenhuma mensagem real enviada.'}); };
  const ok=!!self.state.cr; v.cr_on=ok; v.cr_off=!ok;
  v.credito=()=>{ if(ok){ self.setState({g2toast:'Crédito CR-031 já emitido para o RC-12 · mesmo recibo devolvido · nada lançado de novo.'}); return; }
    const sp=GRIDS.find(g=>g.id==='g_rec'); const rows=g2clone(g2rows(self,sp)); const r=g2find(rows,'f2096'), pa=g2find(rows,'rhb');
    r.v.saldo=CR_SALDO; r.p.div=[{k:'chip',t:'Crédito emitido · CR-031',c:'green'},{k:'br',t:''},{k:'link',t:'RC-12',h:'VE-06.dc.html'},{k:'mut',t:' · '+brl(CR_VAL)}]; r.s.div='Crédito emitido CR-031 RC-12';
    pa.v.saldo=pa.v.saldo-CR_VAL; g2set(self,'g_rec',{rows:rows,fl:'f2096'});
    self.setState({cr:true,g2toast:'Crédito CR-031 de '+brl(CR_VAL)+' emitido contra o FAT-2096 · vinculado ao RC-12 e ao PV-027 · saldo do título passa a '+brl(CR_SALDO)+' · o pedido original permanece como vendido; a destinação física do lote L26-118 segue com a Qualidade.'}); }; }'''
    EXTRAJS[0]=f'const CR_VAL={rc12}, CR_SALDO={pv27-rc12};\n'+EXTRAJS[0]
    caso=(f'<sc-if value="{H("cr_off")}" hint-placeholder-val="{H("true")}">'
          + kv([('Caso',f'<b>RC-12</b> · maturação avançada · 4 fotos + laudo do cliente · <a href="VE-06.dc.html" style="color: {ACC}; font-weight: 700; text-decoration: none;">abrir caso ›</a>'),
                ('Pedido · título',f'<a href="VE-04.dc.html" style="color: {ACC}; font-weight: 700; text-decoration: none;">PV-027</a> · Rede Hortifrúti BA · entrega 2/2 · FAT-2096 ({rs(pv27)})'),
                ('Crédito solicitado',f'<b>{rs(rc12)}</b> = 300 kg × R$ 2,95/kg · retorno do lote L26-118 recebido bloqueado (não volta ao vendável)')])
          + '</sc-if>'
          + f'<sc-if value="{H("cr_on")}" hint-placeholder-val="{H("false")}"><div role="status" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 10px 14px; border-radius: 12px; background: {ACCS}; color: {ACC}; font-size: 13px; font-weight: 700;">'
          + chip('Crédito emitido','green') + f'<span>CR-031 · {rs(rc12)} contra o FAT-2096 · vínculo ao RC-12 e ao PV-027 · saldo do título {rs(pv27-rc12)}</span></div></sc-if>')
    cobr=idrawer('Registrar cobrança autorizada',dict(title='Cobrança ao cliente',sub='registro com canal e autorização — não altera o título',
            fields=[('Cliente','Atacado Bom Preço'),('Título','FAT-2090 · PV-029'),('Canal','telefone + e-mail'),('Acordo proposto','pagar até 26/09 e separar os 150 sc do RC-14')],
            confirm='Registrar cobrança',done='Cobrança registrada no histórico do título'),'users','Registrar a cobrança do título vencido (simulado, nenhuma mensagem real enviada)')
    corpo=(kpis([('CARTEIRA EM ABERTO',rs(tot_aberto),'4 títulos'),('VENCIDOS',rs(pv29),'PV-029 · 4 d'),
                 ('CRÉDITOS SOLICITADOS','1',f'RC-12 · {rs(rc12)}'),('RECEBIDO NO MÊS',mi(pv30/1000),'conciliado')])
        + bloco('Crédito solicitado pelo caso RC-12','Confira o título do PV-027 e emita o crédito vinculado ao caso, sem editar o pedido original.',caso,tone='red')
        + bloco('Carteira por cliente e título','Confira cada título até pedido, entrega e caso; clique num título em aberto para registrar a próxima cobrança.',g_rec,
                acao=cobr+imsg('Conciliar recebimentos do extrato','Conciliado o extrato de 23/09 · nenhum recebimento do FAT-2090 (PV-029) — título segue vencido há 4 dias; divergências continuam vinculadas aos casos, sem editar pedidos.','check','Conciliar o extrato bancário com os títulos')))
    shell37('GE-05','Contas a receber',corpo,
      subtitle='Recebíveis por cliente, título e parcela — ligados a pedido, faturamento, entrega e devolução.',
      status=(f'{rs(pv29)} vencidos · 1 crédito a emitir','yellow'),
      primary_html=ibtn('Emitir crédito do RC-12','credito','cash','Emitir o crédito de R$ 885 contra o FAT-2096, vinculado ao caso RC-12',primary=True,small=False),
      footer='Desconto, devolução e baixa deixam vínculo próprio; o pedido original permanece como foi vendido.')

# =====================================================================================
# GE-06 · Indicadores operacionais  +  GE-06det
# =====================================================================================
def _ge06():
    fname='GE-06.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1110
    perda=D.PACKING["descarte"]/D.PACKING["entrada"]*100
    lam=nf(D.PIVO["lamina_aplicada"],2)  # irrigação só com água: a referência é a lâmina do balanço hídrico (sem política nem autorização)
    def K(rid,proc,ind,form,per,meta,real,rc,fonte,causa,cc,acao,o):
        return R(rid,v=dict(ind=ind,proc=proc,form=form,per=per,meta=meta,causa=causa),p=dict(ind=[b(ind)],form=[t_(form),br(),mut(fonte)],meta=[t_(meta),br(),mut(per)],real=[ch(real,rc)],acao=acao),s=dict(meta=f'{meta} {per}'),o=o)
    kr=[K('k1','Agronômico','Custo de pulverização','R$ ÷ ha tratado (apontado)','set/26','R$ 40,00/ha','R$ 48,40/ha ↑','red','apontamentos · 100%','consumo +10% · preço +10%','yellow',
          [cta('Detalhar','GE-06det.dc.html',True)],[(f'R$ 5.808 ÷ 120 ha·op ({OS_ORC})','GE-06det.dc.html'),('Responsável: Ana (gestora) · meta da base V1',None)]),
        K('k2','Programação','Ritmo de plantio','ha plantados ÷ dia útil','janela out/26','35 ha/dia','em risco ↓','yellow','programação · 100%','OS-0420 impedida · OM-0233','red',
          [cta('Ver ações','GE-07.dc.html')],[('OS-0420 · 30 de 100 ha · saldo pausado','CA-01.dc.html'),('OM-0233 · Trator T1','MA.dc.html#om=OM-0233')]),
        K('k3','Campo','Aderência ao programado','O.S. no dia previsto ÷ total','últimos 30 d','≥ 90%','86% ↓','yellow','ordens de campo · 100%','reprogramações por chuva',None,
          [cta('Ver ordens','CA-01.dc.html')],[('Ordens de campo dos últimos 30 dias','CA-01.dc.html')]),
        K('k4','Beneficiamento','Perda no beneficiamento','descarte ÷ entrada (t)','set/26','≤ 4%',f'{nf(perda,0)}% ↑','yellow','packing · 100%','classificação classe B alta',None,
          [cta('Ver packing','CO-05.dc.html')],[(f'{nf(D.PACKING["descarte"],1)} t descartadas ÷ {nf(D.PACKING["entrada"],1)} t de entrada','CO-05.dc.html'),('Caso AC-097 em verificação','GE-07.dc.html')]),
        K('k5','Irrigação','Uso de água no pivô 2','mm aplicados ÷ mm programados pelo balanço','OS-0419 · balanço 23/09','≤ 100%',f'{lam} de {lam} mm','green','telemetria · 100%','—',None,
          [cta('Ver irrigação','IR-03.dc.html')],[(f'Pivô 2 a {D.PIVO["percent"]}% da volta · {lam} mm aplicados','IR-03.dc.html')])]
    g_ind=grid([C('ind','Indicador',w=170),C('proc','Processo'),C('form','Fórmula · fonte',w=190),C('meta','Meta · período',a='r'),C('real','Realizado · tendência',a='r'),
                C('causa','Causa apontada',w=180),C('acao','Ação')],
        kr,edit=dict(m='origin',title='Indicador',fields=[F('form','Fórmula',ro=True),F('per','Período',ro=True),F('meta','Meta',ro=True)]),gid='g_ind',total=False)
    def A(rid,at,disp,dc,ut,mtbf,mttr,cus,href,o):
        return R(rid,v=dict(at=at,ut=ut,mtbf=mtbf,mttr=mttr,cus=cus),p=dict(at=[link(at,href)],disp=[ch(disp,dc)]),o=o)
    g_atv=grid([C('at','Ativo · classe',w=210),C('disp','Disponibilidade'),C('ut','Utilização',a='r'),C('mtbf','MTBF',a='r'),C('mttr','MTTR',a='r'),C('cus','Custo/h realizado',a='r')],
        [A('t1','Trator T1 · JD 6M 155','62% · bloqueado','red','—','184 h','9,5 h','R$ 158/h','MA.dc.html#ativo=a01',[('OM-0233 · pressão hidráulica baixa · bloqueio CMD-18','MA.dc.html#om=OM-0233')]),
         A('t2','Trator 02 · MF 7719','97%','green','81%','412 h','2,1 h','R$ 141/h','MA.dc.html#ativo=a02',[('Horímetro e paradas do mês','MA.dc.html#ativo=a02')]),
         A('pv','Pulverizador PJ-3030','94%','green','76%','367 h','3,4 h','R$ 96/h','MA.dc.html#ativo=a05',[('Horímetro e paradas do mês','MA.dc.html#ativo=a05')]),
         A('p2','Pivô 2','99%','green',f'{D.PIVO["percent"]}% da volta','—','—','R$ 38/h','IR-01.dc.html',[('Telemetria do pivô','IR-01.dc.html')])],
        edit=dict(m='origin',title='Ativo',fields=[F('ut','Utilização',ro=True),F('mtbf','MTBF',ro=True),F('mttr','MTTR',ro=True),F('cus','Custo/h realizado',ro=True)]),search=False,gid='g_atv',total=False)
    corpo=(bloco('Painéis por processo','Confira meta, realizado e causa de cada indicador; clique num indicador para ver fórmula e origem.',g_ind)
        + bloco('Desempenho dos ativos','Compare disponibilidade, utilização e confiabilidade; clique num ativo para ver a origem dos números.',g_atv,tone='yellow')
        + bloco('Parâmetros','Proponha nova versão de parâmetro a partir do aprendizado, nunca edite o cadastro em silêncio.',
                '<div style="display: flex; gap: 10px; flex-wrap: wrap;">'+ilink('Propor parâmetro agronômico','AG-05.dc.html','leaf','Abrir a biblioteca agronômica para propor nova versão')
                +ilink('Propor regra ou alçada','CF-01.dc.html#alc=AL-01','users','Abrir as alçadas em Configurações › Usuários e alçadas')+'</div>',tone='gray'))
    shell37('GE-06','Indicadores operacionais',corpo,
      subtitle='Meta, tendência, composição e diferenças entre previsto e realizado — cada número com fórmula, fonte e denominador.',
      status=('4 indicadores fora da meta','yellow'),
      primary='Abrir plano de ação',primary_href='GE-07.dc.html',
      footer='Disponibilidade, utilização, produtividade e eficiência são conceitos distintos e assim permanecem nos painéis (cap. 53).')

    # ---- GE-06det · indicador → causas → documentos → O.S. ----
    fname='GE-06det.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1080; PARENT37[fname]='GE-06.dc.html'
    # 14/10/2026 (proprietário: "reduza ou elimine ... os demais soltos pela tela"): fórmula e fonte (método) foram para a dica ⓘ da tela
    ficha=kv([('Unidade · denominador','R$/ha · 120 ha·operação (95 ha do P1 + 25 ha reaplicados)'),
              ('Período',f'set/2026 · {OS_ORC} (encerrada)'),
              ('Cobertura','100% dos apontamentos sincronizados · 0 conflitos'),('Meta · responsável','R$ 40,00/ha (base V1 aprovada) · Ana (gestora)')])
    g_cau=grid([C('causa','Causa',w=220),C('ef','Efeito',a='r'),C('ev','Evidência'),C('hip','Hipótese a validar',w=300)],
        [R('c1',v=dict(causa='Área tratada acima do plano',ef='+R$ 800',ev='120 vs. 100 ha·op'),p=dict(hip=[ch('reaplicação de 25 ha após chuva — checar','yellow')]),o=[('R$ 20/L × 2 L/ha × 20 ha·op = R$ 800','CA-02.dc.html')]),
         R('c2',v=dict(causa='Consumo unitário +10%',ef='+R$ 480',ev='2,2 vs. 2,0 L/ha'),p=dict(hip=[ch('calda ajustada pelo agrônomo — validar','yellow')]),o=[('R$ 20/L × 0,2 L/ha × 120 ha·op = R$ 480','CA-02.dc.html')]),
         R('c3',v=dict(causa='Preço do produto +10%',ef='+R$ 528',ev='R$ 22 vs. R$ 20/L'),p=dict(hip=[ch('compra fora do contrato? — conferir pedido','yellow')]),o=[('R$ 2/L × 264 L = R$ 528','SU-06.dc.html')])],
        edit=dict(m='origin',title='Causa',fields=[F('ef','Efeito',ro=True),F('ev','Evidência',ro=True)]),search=False,gid='g_cau',total=False)
    g_doc=grid([C('doc','Documento',w=220),C('sust','O que sustenta',w=300),C('dt','Data'),C('ab','Abrir')],
        [R('o1',v=dict(sust='ordem encerrada · 95 ha + reaplicação de 25 ha',dt='08–12/09'),p=dict(doc=[Pt.tag(f'{OS_ORC} · pulverização')],ab=[cta('Abrir ordens','CA-01.dc.html')])),
         R('o2',v=dict(sust='ha tratados e calda por turno',dt='08–12/09'),p=dict(doc=[Pt.tag('Apontamentos da O.S.')],ab=[cta('Abrir apontamentos','CA-02.dc.html')])),
         R('o3',v=dict(sust='264 L retirados do estoque',dt='08–12/09'),p=dict(doc=[Pt.tag('Requisições')],ab=[cta('Abrir requisições','SU-07.dc.html')])),
         R('o4',v=dict(sust='preço real R$ 22,00/L',dt='05/09'),p=dict(doc=[Pt.tag('Recebimento NF 8842')],ab=[cta('Abrir recebimento','SU-06.dc.html')]))],
        edit=dict(m='ro',title='Documento',fields=[F('sust','O que sustenta',ro=True),F('dt','Data',ro=True)]),search=False,gid='g_doc',total=False)
    corpo=(continuity('Indicadores · painel agronômico','Custo de pulverização por ha tratado — R$ 48,40 vs. meta R$ 40,00','causa confirmada e ação com dono','Abrir plano de ação')
        + bloco('Ficha do indicador','Confira fórmula, denominador e fonte antes de usar o número.',ficha)
        + bloco('Causas com decomposição','Confira as causas: volume +R$ 800 · consumo +R$ 480 · preço +R$ 528 = +R$ 1.808.',g_cau,tone='yellow')
        + bloco('Documentos de origem','Abra cada documento para chegar à O.S. que sustenta o número.',g_doc,tone='gray'))
    shell37('GE-06','Detalhar · custo de pulverização',corpo,fname=fname,crumbs_extra=[OS_ORC],
      subtitle='Indicador abre causas e documentos de origem — o gestor chega à O.S. em dois cliques.',
      status=('21% acima da meta','red'),
      primary='Abrir plano de ação',primary_href='GE-07.dc.html',
      footer='O índice explica o desvio; a decisão (ação, parâmetro ou nada) é humana e fica registrada em Planos de ação. '
             'Fórmula: custo total da operação ÷ ha efetivamente tratados (apontados). Fonte: lançamentos de custo documento a documento + apontamentos da O.S.')

# =====================================================================================
# GE-07 · Planos de ação
# =====================================================================================
PESSOAS=['Ana','Rui','Marcos','Paula','João','Carlos','PCP','Equipe irrigação']
ORIGENS=['Custo de pulverização · feijão P1','Sensores · sonda P1','OM-0233 · Trator T1','Perda no beneficiamento','Aderência ao programado','Ritmo de plantio · OS-0420','Outro indicador ou ocorrência']
ESTC={'Em curso':'yellow','Aguardando peça':'yellow','Em verificação':'green','Encerrado':'gray','Aberto':'yellow'}
def _ge07():
    fname='GE-07.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=900
    reab=drawer_button('Reabrir caso',dict(title='Reabrir caso encerrado',sub='reabrir exige motivo; o caso volta a Em curso e todo o histórico permanece',
            fields=[('Caso','AC-090 · atraso de liberação de O.S.'),('Motivo','aderência voltou a 84% em set/26'),('Evidência','painel de aderência · últimos 30 d')],
            confirm='Reabrir caso',done='Caso reaberto'))
    RDID=E.DRAWN['Reabrir caso']
    def A(cid,tit,orig,origp,hip,acao,dono,prazo,est,acts,ro=False,o=None):
        return R(cid,ro=ro,v=dict(tit=tit,orig=orig,hip=hip,acao=acao,dono=dono,prazo=prazo,evid=''),
                 p=dict(caso=[b(cid),br(),mut(tit)],orig=[Pt.tag(origp)],hip=[t_(hip),br(),mut('ação: '+acao)],est=[ch(est,ESTC.get(est,'gray'))],act=acts),s=dict(caso=f'{cid} {tit}',est=est,prazo=prazo,hip=f'{hip} {acao}'),o=o)
    rows=[
      A('AC-101','custo de pulverização',ORIGENS[0],'R$ 48,40/ha · feijão P1','consumo +10% e compra fora do contrato','validar calda com agrônomo · negociar contrato de fungicida','Ana','2026-09-30','Em curso',
        [cta('Propor mudança','GE-02det.dc.html')],o=[('Indicador: R$ 48,40/ha contra meta R$ 40,00/ha','GE-06det.dc.html')]),
      A('AC-102','leitura suspeita sonda P1',ORIGENS[1],'sensores · salto de 18 p.p.','sensor descalibrado','inspecionar e recalibrar; excluir do balanço até lá','Equipe irrigação','2026-09-26','Em curso',
        [Pt.act('Verificar resultado','Ainda sem resultado: a recalibração da sonda P1 está prevista para 26/09 · o caso segue em curso e a sonda fora do balanço.')],o=[('Balanço hídrico · sonda P1','IR-01.dc.html')]),
      A('AC-103','recorrência hidráulica T1',ORIGENS[2],'OM-0233','mangueira fora de especificação','trocar especificação da peça e revisar preventiva','PCP','2026-10-10','Aguardando peça',
        [cta('Ver OM-0233','MA.dc.html#om=OM-0233')],o=[('OM-0233 · pressão hidráulica baixa','MA.dc.html#om=OM-0233')]),
      A('AC-097','perda no beneficiamento',ORIGENS[3],'descarte 5%','regulagem da classificadora','regulagem feita · medir por 2 semanas','Rui','2026-10-04','Em verificação',
        [Pt.act('Verificar resultado','Verificado · descarte caiu de 5% para 3,8% em 2 semanas — caso elegível a encerramento com evidência anexada.'),br(),jact('Encerrar com evidência','encerrar:AC-097')],o=[('Perda no beneficiamento · packing','CO-05.dc.html')]),
      A('AC-090','atraso de liberação de O.S.',ORIGENS[4],'aderência 86%','prontidão conferida tarde','checagem de prontidão na véspera','Marcos','2026-09-15','Encerrado',
        [jact('Reabrir com motivo',RDID+'_open')],ro=True,o=[('Aderência ao programado','GE-06.dc.html')]),
    ]
    g_ac=grid([C('caso','Caso',w=150),C('orig','Origem · indicador',w=155),C('hip','Hipótese · ação definida',w=220),C('dono','Dono',w=110),
               C('prazo','Prazo',t='date'),C('est','Estado',chips=ESTC),C('act','Ação',w=180)],
        rows,edit=dict(m='form',title='Caso',newTitle='Criar ação',sub='Ajuste hipótese, ação, dono e prazo. Estado muda só pela verificação e pelo encerramento; caso encerrado abre em consulta.',
            fields=[F('tit','Título do caso',t='txt',req=True),F('orig','Origem · indicador',t='sel',opts=ORIGENS,req=True,**{'def':ORIGENS[0]}),F('hip','Hipótese de causa',t='area',req=True),
                    F('acao','Ação definida',t='area',req=True),F('dono','Dono',t='sel',opts=PESSOAS,req=True,**{'def':'Ana'}),F('prazo','Prazo',t='date',req=True),
                    F('evid','Evidência esperada',t='area',help='Como o resultado será verificado no indicador.')]),
        so={'k':'prazo','d':False},gid='g_ac',total=False)
    EXTRAJS[0]=JS_BASE+'''
const RDID='''+json.dumps(RDID)+r''';
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_ac'||!r) return; undate(r,['prazo']);
    let id=r.id; if(String(r.id).indexOf('n')===0){ const n=rows.filter(x=>String(x.id).indexOf('n')===0).length; id='AC-'+(103+n); r.v.__id=id; r.p.est=[{k:'chip',t:'Aberto',c:'yellow'}]; r.s.est='Aberto'; r.p.act=[{k:'mut',t:'verificar no prazo'}]; }
    else id=r.v.__id||r.id;
    r.p.caso=[{k:'b',t:id},{k:'br',t:''},{k:'mut',t:r.v.tit}]; r.s.caso=id+' '+r.v.tit; r.p.orig=[{k:'tag',t:r.v.orig}]; r.s.orig=r.v.orig;
    r.p.hip=[{k:'txt',t:r.v.hip},{k:'br',t:''},{k:'mut',t:'ação: '+r.v.acao}]; r.s.hip=r.v.hip+' '+r.v.acao;
    self.setState({g2toast:(String(r.id).indexOf('n')===0?'Caso '+id+' criado e atribuído a '+r.v.dono:'Caso '+id+' atualizado')+' · prazo '+(r.v.prazo||'').split('-').reverse().join('/')+'.'}); };
  v.encerrar=(cid)=>{ const e=Object.assign({},self.state.enc||{}); if(e[cid]){ self.setState({g2toast:cid+' já encerrado · reabrir exige motivo.'}); return; }
    e[cid]=1; gsetRow(self,'g_ac',cid,r=>{ r.ro=true; r.p.est=[{k:'chip',t:'Encerrado',c:'gray'}]; r.s.est='Encerrado'; r.p.act=[{k:'mut',t:'evidência: 5% → 3,8%'}]; });
    self.setState({enc:e,g2toast:'Encerrado com evidência: descarte 5% → 3,8% em 2 semanas · reabrir exige motivo e mantém todo o histórico do caso.'}); };
  const add=v[RDID+'_add']; v[RDID+'_add']=()=>{ add(); gsetRow(self,'g_ac','AC-090',r=>{ r.ro=false; r.p.est=[{k:'chip',t:'Em curso',c:'yellow'}]; r.s.est='Em curso'; r.p.act=[{k:'mut',t:'reaberto · motivo registrado'}]; });
    self.setState({g2toast:'AC-090 reaberto com motivo · volta a Em curso; o encerramento anterior e a evidência ficam no histórico.'}); }; }'''
    corpo=bloco('Casos de melhoria e desvios','Acompanhe cada caso do indicador à verificação; clique num caso aberto para ajustar hipótese, ação, dono e prazo.',g_ac)
    shell37('GE-07','Planos de ação',corpo,
      subtitle='Do indicador à ação com dono e prazo — e da ação de volta ao indicador para provar o resultado.',
      status=('3 casos em curso · 1 em verificação','yellow'),
      primary_html=f'<button type="button" onClick="{H("g_ac_new")}" style="{BTN_ST(True)} display: inline-flex; align-items: center; gap: 6px;">{icon("check",15)}Criar ação</button>',
      footer='Aprendizado vira proposta de nova versão de parâmetro com diferença visível — nunca muda cadastro a partir de um único apontamento.')

# =====================================================================================
# GE-08 · Crédito e garantias (DEMO-10)
# =====================================================================================
def _ge08():
    fname='GE-08.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1150
    c=D.CRE
    penhor=round(SOJA_V2_SC*0.30); cpr=6900; comp=(penhor+cpr)/SOJA_V2_SC*100
    def K(cid,fin,cred,val,gar,cet,est,cor,acao,ro=True,o=None):
        return R(cid,ro=ro,v=dict(fin=fin,cred=cred,val=val,gar=gar,cet=cet),p=dict(sol=[b(cid)],est=[ch(est,cor)],acao=acao),s=dict(sol=cid,est=est),o=o)
    rows=[
      K(c['id'],'custeio safra 26/27','Banco Terra',850,'penhor de 30% da soja','14,2% a.a.',c['estado'],'yellow',[mut('—')],
        o=[(f'Liberado {c["liberado"]} de {c["valor"]} · 1ª parcela é título em Contas a pagar','GE-04.dc.html'),('Dossiê de crédito','GE-08.dc.html#vis=dossie')]),
      K('CRE-0098','trator MF 7719','Coop Crédito',780,'alienação do bem','11,9% a.a.','Contratado · em serviço','green',[cta('Ver título','GE-04.dc.html')]),
      K('CRE-0095','barter defensivos','Agroquímica Delta',820,f'CPR física · {nf(cpr)} sc','troca 5,8 sc/ha','Contratado · entrega na colheita','green',[cta('Ver CPR','VE-05.dc.html')],
        o=[(f'CPR de {nf(cpr)} sc de soja 26/27 · obrigação física em Contratos','VE-05.dc.html')]),
      K('CRE-0104','armazém — estudo','—',1200,'a definir','—','Rascunho de solicitação','gray',[mut('clique para preparar')],ro=False),
    ]
    g_cre=grid([C('sol','Solicitação'),C('fin','Finalidade',w=135),C('cred','Credor'),C('val','Valor',t='num',a='r',pre='R$ ',u='mil'),C('gar','Garantia',w=135),
                C('cet','Custo (CET)',a='r'),C('est','Estado',w=255),C('acao','Ação')],
        rows,edit=dict(m='form',title='Solicitação',sub='Prepare a solicitação em rascunho. Solicitação aprovada ou contratada abre em consulta: cada liberação é um fato financeiro próprio.',
            fields=[F('fin','Finalidade',t='txt',req=True),F('cred','Credor',t='sel',opts=['—','Banco Terra','Coop Crédito','Fundo Agro Invest'],req=True),
                    F('val','Valor',t='num',req=True,min=1,u='R$ mil'),F('gar','Garantia',t='sel',opts=['a definir','CPR + penhor de safra','CPR financeira','Aval','Hipoteca'],req=True)]),
        gid='g_cre',total=False)
    doss=[R('d1',v=dict(blk='Produção e áreas',cont='talhões, safras, produtividade 3 anos',aut='Banco Terra; Coop Crédito',prz='2026-12-31'),p=dict(blk=[b('Produção e áreas')],st=[ch('Autorizado','green')])),
          R('d2',v=dict(blk='Fluxo de caixa',cont='projeção V2 por trimestre',aut='Banco Terra',prz='2026-12-31'),p=dict(blk=[b('Fluxo de caixa')],st=[ch('Autorizado','green')])),
          R('d3',v=dict(blk='Compromissos e garantias',cont='contratos, barter e penhores vigentes',aut='Banco Terra',prz='2026-12-31'),
            p=dict(blk=[b('Compromissos e garantias')],st=[ch('Aguardando autorização da Direção','yellow'),br(),jact('Autorizar bloco','autorizar:d3')]))]
    g_dos=grid([C('blk','Bloco do dossiê',w=190),C('cont','Conteúdo',w=260),C('aut','Autorizado para',w=200),C('prz','Prazo de acesso',t='date'),C('st','Consentimento',w=260)],
        doss,edit=dict(m='form',title='Bloco do dossiê',sub='Ajuste quem acessa e até quando. O credor só vê o bloco com consentimento confirmado; mudar o acesso registra novo consentimento.',
            fields=[F('cont','Conteúdo',ro=True),F('aut','Autorizado para',t='multi',opts=['Banco Terra','Coop Crédito','Fundo Agro Invest'],req=True),F('prz','Prazo de acesso',t='date',req=True)]),
        search=False,gid='g_dos',total=False)
    # ---- Documentos para crédito (proprietário, 16/10/2026: "documentos para credito podemos deixar tudo separado em outro lugar para nao
    # perder foco e produtividade"): CAR, matrícula, módulos fiscais, contrato de arrendamento e a pendência dos documentos saíram do cadastro
    # da fazenda (CD-01) e vivem aqui, uma linha por documento e fazenda (ou parceiro), na grade do motor com Tabela | Cartões. Fonte: os mesmos
    # dados sintéticos de dados_cad.FAZENDAS (nada se perde) e a condição documental do CRE-0102 (certidão exigida pelo Banco Terra).
    # Outorga de água e restrição ambiental ficam no CD-01 (a Irrigação usa a outorga: CTL-5)
    import dados_cad as DC
    TIPOS_DOC=['CAR','Matrícula','Certidão de matrícula atualizada','Contrato de arrendamento','CCIR','ITR','Outro']
    def _fz(f): return f['nome']
    # revisão do Codex 6220145128 (S2): o documento da fazenda leva o id estável dela (fid); no navegador, credito_docs.js migra o cadastro salvo
    # antes da mudança, segue o nome, a posse e as fazendas do cadastro atual e grava as edições do Crédito (as linhas abaixo são o seed)
    docs=[]
    for f in DC.FAZENDAS:
        docs.append(dict(id='dc_car_'+f['id'],tipo='CAR',fid=f['id'],tit=_fz(f),num=f.get('car',''),val='',exig='',mf=f.get('mf',''),pend=''))
        docs.append(dict(id='dc_mat_'+f['id'],tipo='Matrícula',fid=f['id'],tit=_fz(f),num=f.get('matr',''),val='',exig='',pend=''))
        if f.get('posse') and f['posse']!='Própria':
            docs.append(dict(id='dc_arr_'+f['id'],tipo='Contrato de arrendamento',fid=f['id'],tit=_fz(f),num=f.get('arrend',''),val=f.get('fim',''),exig='',
                             custo=f.get('custo',''),pend=f.get('pend','')))
    docs.append(dict(id='dc_cert_SR',tipo='Certidão de matrícula atualizada',fid='SR',tit='Santa Rita',num='',val='',exig=f'Banco Terra · {c["id"]}',pend='Condição da aprovação: validade de 90 dias'))
    CRED_SEED_FAZ=[dict(id=f['id'],nome=f['nome'],posse=f.get('posse',''),fim=f.get('fim',''),sit=f.get('sit','')) for f in DC.FAZENDAS]
    CRED_JS=(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'credito_docs.js'),encoding='utf-8').read()
             +'\nconst CRED_SEED_FAZ='+json.dumps(CRED_SEED_FAZ,ensure_ascii=False)+', CRED_SEED_DOCS='+json.dumps(docs,ensure_ascii=False)+';\n')
    g_doc=grid([C('tipo','Documento',w=230),C('est','Situação',w=200),C('tit','Fazenda ou parceiro'),C('num','Número ou registro',w=260),C('val','Validade',t='date'),C('exig','Exigido por',w=170)],
        [R(d['id'],v=d) for d in docs],gid='g_doc',total=False,cartoes=True,qf=dict(k='est',todas='Todos'),
        edit=dict(m='form',title='Documento',newTitle='Incluir documento',sub='Documento que o credor pede para analisar ou liberar o crédito. Não bloqueia o planejamento.',
            fields=[F('tipo','Documento',t='sel',opts=TIPOS_DOC,req=True),F('tit','Fazenda ou parceiro',t='sel',opts=[_fz(f) for f in DC.FAZENDAS],dyn=True,req=True),
                    F('num','Número ou registro',t='txt',req=False,help='Em branco, o documento fica pendente.'),
                    F('mf','Módulos fiscais',t='num',req=False,min=0,cond=dict(k='tipo',eq='CAR'),help='Do recibo do CAR.'),
                    F('custo','Valor do arrendamento',t='num',req=False,min=0,u='sc/ha/ano',cond=dict(k='tipo',eq='Contrato de arrendamento')),
                    F('val','Validade ou fim',t='date',req=False),
                    F('pend','Pendência',t='txt',req=False,help='O que falta no documento (ex.: contrato sem registro em cartório).')]))
    doc=imsg('Conferir envio ao credor', 'Prévia · nada foi alterado. Anexar arquivo e enviá-lo ao credor ainda não está disponível neste protótipo. O cadastro de documentos abaixo permite registrar os dados; isso não envia arquivo, não confirma aceite do credor e não libera parcela.', 'doc', 'Ver disponibilidade do envio do documento')
    # CRE-BANCO F1: avaliações declaradas da ficha comum; não são dossiês nem autorização.
    dc=dict(k='oper',eq='Atualizar declaração')
    g_ficha=grid([C('nome','Bem'),C('situacao','Situação'),C('valor','Valor declarado',a='r',t='num'),
                  C('origem','Origem'),C('confirmacao','Última confirmação')],[],gid='g_ficha',total=False,cartoes=True,qf=dict(k='situacao',todas='Todos'),
        edit=dict(m='form',title='Bem e avaliação',newTitle='Incluir bem',sub='Ficha do grupo · dados de demonstração. Salvar não envia dados a um credor.',
            fields=[F('oper','O que fazer',t='sel',opts=['Atualizar declaração','Confirmar vigência'],**{'def':'Atualizar declaração'},req=True),
                    F('resumo','Declaração atual',t='area',ro=True),F('confirmacao','Confirmações de vigência',t='area',ro=True),
                    F('nome','Bem',t='txt',req=True,cond=dc),F('tipo','Tipo do valor',t='sel',opts=['Avaliação de mercado','Valor contábil','Declaração do produtor'],req=True,cond=dc),
                    F('valor','Valor declarado (R$)',t='txt',cond=dc,help='Ex.: 850.000,50. Em branco, fica pendente; zero é um valor declarado.'),
                    F('data','Data original da declaração',t='date',cond=dc),F('responsavel','Responsável pela declaração original',t='txt',cond=dc),
                    F('fonte','Fonte do valor',t='txt',cond=dc,help='Ex.: laudo de avaliação ou declaração do produtor.'),
                    F('hist','Versões anteriores',t='area',ro=True)]))
    # o painel do motor vai para EXTRA (engine._g2form), fora do HTML da grade: o rótulo "Salvar declaração | Confirmar vigência" entra lá
    i_fm=next(i for i,x in enumerate(EXTRA) if '{{g_ficha_F.save}}' in x)
    assert EXTRA[i_fm].count('>Salvar</button>')==1
    EXTRA[i_fm]=EXTRA[i_fm].replace('>Salvar</button>','>'+H('cre_ficha_salvar_rotulo')+'</button>')
    EXTRAJS[0]=JS_BASE+CRED_JS+'''
const LIB='''+json.dumps(c['liberado'])+''', VAL='''+json.dumps(c['valor'])+r''', HOJE_DOC='2026-09-23', HOJE_FICHA='2026-10-16';
// Cadastro documental: situação deriva dos dados; não há envio nem aceite do credor nesta prévia.
function docSit(self,V){
  if(!String(V.num||'').trim()) return ['Pendente','yellow']; if(V.pend) return ['Pendente','yellow'];
  if(V.val&&V.val<HOJE_DOC) return ['Vencido','red']; return [V.tipo==='Contrato de arrendamento'?'Vigente':'Registrado','green']; }
function PREVALS(self,v){
  const ficha=GRIDS.find(g=>g.id==='g_ficha');
  if(ficha){try{ficha.rows=credFichaLer().items.map(r=>credFichaLinha(r,HOJE_FICHA));self._fichaErr='';}catch(e){self._fichaErr=e.message;}
    const pode=!!g2umPapel(g2perfil(),['direcao','financeiro']);
    g2rows(self,ficha).forEach(r=>{r.ro=!pode;});
  }
  const sp=GRIDS.find(g=>g.id==='g_doc'); if(!sp) return;
  // 1ª montagem: migra o cadastro salvo antes da mudança e monta as linhas pelo cadastro atual (fazendas pelo id estável) e pelo que o
  // Crédito gravou (credito_docs.js); as fazendas ficam em self._credFz para o seletor e para gravar a edição
  if(!self._credIni){ self._credIni=1; credMigrar(); self._credFz=credFazendas(CRED_SEED_FAZ); sp.rows=credDocs(self._credFz,CRED_SEED_DOCS).map(r=>({id:r.id,v:r.v,s:{},p:{}})); }
  g2rows(self,sp).forEach(r=>{ const V=r.v; V.id=r.id; const S=docSit(self,V); r.p=r.p||{}; r.s=r.s||{}; r.s.tit=V.tit||''; r.s.val=V.val||'';
    r.p.tipo=[{k:'b',t:V.tipo}]; r.s.tipo=V.tipo; r.p.est=[{k:'chip',t:S[0],c:S[1]}].concat(V.pend?[{k:'mut',t:V.pend}]:[]); r.s.est=S[0];
    const det=[V.num||'',V.mf?String(V.mf).replace('.',',')+' módulos fiscais':'',V.custo?String(V.custo).replace('.',',')+' sc/ha/ano':''].filter(Boolean).join(' · ');
    r.p.num=[det?{k:'txt',t:det}:{k:'mut',t:'a informar'}]; r.s.num=det; r.p.exig=[V.exig?{k:'txt',t:V.exig}:{k:'mut',t:'—'}]; r.s.exig=V.exig||''; }); }
function EXTRAVALS(self,v){
  const hv=(String(location.hash).match(/vis=([a-z]+)/)||[])[1]||'', VIS=['contratos','liberacoes','dossie','documentos','ficha'], vis=VIS.indexOf(hv)>=0?hv:'';
  VIS.forEach(k=>{ v['cv_'+k]=!vis||vis===k; });
  v.cv_ficha=vis==='ficha'; v.cv_ficha_nao=!v.cv_ficha; // entrada pela área de Documentos; não altera o conjunto legado sem recorte
  v.cre_ficha_sem_papel=!g2umPapel(g2perfil(),['direcao','financeiro']);
  v.cre_ficha_erro=!!self._fichaErr;v.cre_ficha_motivo=self._fichaErr||'';
  v.cre_ficha_vazia=!self._fichaErr&&!(g2rows(self,GRIDS.find(g=>g.id==='g_ficha'))||[]).length; if(v.cre_ficha_vazia||v.cre_ficha_erro) v.g_ficha_empty=false;
  v.cre_ficha_vazia_motivo=v.cre_ficha_sem_papel?'Nenhum bem na ficha ainda. A direção pode incluir o primeiro.':'Nenhum bem na ficha ainda. Use “Incluir bem” para declarar o primeiro.';
  v.cre_ficha_novo=()=>{if(v.cre_ficha_sem_papel){self.setState({g2toast:'Somente a direção pode alterar a ficha nesta demonstração.'});return;}g2new(self,GRIDS.find(g=>g.id==='g_ficha'));};
  v.cre_ficha_reler=()=>self.setState({});
  const fmF=g2st(self,'g_ficha').fm, FF=v.g_ficha_F;
  v.cre_ficha_salvar_rotulo=fmF&&fmF.draft.oper==='Confirmar vigência'?'Confirmar vigência':'Salvar declaração';
  if(FF&&FF.fields&&fmF&&fmF.isNew)FF.fields=FF.fields.filter(f=>!['oper','resumo','confirmacao','hist'].some(k=>f.fid==='fx_g_ficha_'+k));
  if(FF&&FF.fields)FF.fields.forEach(f=>{if(f.fid==='fx_g_ficha_valor')f.im='decimal';});
  self.g2openDraft=(gid,r,d)=>{if(gid!=='g_ficha')return d;
    try{const atual=credFichaLer().items.find(x=>x.id===r.id);if(atual){const linha=credFichaLinha(atual,HOJE_FICHA);Object.assign(r,linha);Object.keys(d).forEach(k=>{d[k]=String(linha.v[k]??'');});d.valor=atual.valor===null?'':credFichaDinheiro(atual.valor).slice(3);d._fichaRev=atual.rev;}}
    catch(e){self._fichaErr=e.message;}return d;};
  self.g2newDraft=(gid,d)=>gid==='g_ficha'?{_fichaRev:0}:{};
  if(!self.__creHash){ self.__creHash=true; addEventListener('hashchange',()=>self.setState({}),false); }
  v.cre_hint='liberado '+LIB+' de '+VAL+' · condição documental pendente; envio e aceite do credor ainda não disponíveis nesta prévia';
  v.lib2=()=>self.setState({g2toast:'Prévia · nada foi alterado. Condição documental pendente; envio e aceite do credor ainda não disponíveis. Nenhuma parcela liberada.'});
  // gravação no ponto transacional do motor (revisão do Codex 6221423767, S2): o documento só vale como salvo se o navegador gravou; falhou
  // (ou é mudança de tipo/fazenda de documento automático), o motor desfaz o comando e reabre o formulário com o rascunho e o motivo
  self.g2persist=(gid)=>{
    if(gid==='g_ficha'&&self._fichaCmd){const cmd=self._fichaCmd;self._fichaCmd=null;
      try{const salvo=credFichaSalvar(cmd.id,cmd.d,cmd.rev,g2perfil(),HOJE_FICHA);
        const rs=g2clone(g2rows(self,GRIDS.find(g=>g.id==='g_ficha'))), i=rs.findIndex(x=>x.id===salvo.id), linha=credFichaLinha(salvo,HOJE_FICHA);
        if(i<0)rs.push(linha);else rs[i]=linha;g2set(self,'g_ficha',{rows:rs});
        self.setState({g2toast:cmd.d.oper==='Confirmar vigência'?'Vigência confirmada · declaração original preservada.':'Ficha salva neste navegador · nada enviado ao credor.'});return '';
      }catch(e){return e.message;}}
    if(gid!=='g_doc'||!self._docPend)return '';const r=self._docPend;self._docPend=null;return credSalvarDoc(r,self._credFz||[],CRED_SEED_DOCS);};
  // documento automático: tipo e fazenda fixos no formulário (só leitura, com o motivo) e recusados ao salvar
  self.g2check=(gid,cur,row,d,isNovo)=>{
    if(gid==='g_ficha'){
      if(!g2umPapel(g2perfil(),['direcao','financeiro']))return {[isNovo?'nome':'oper']:'Somente a direção pode alterar a ficha nesta demonstração.'};
      const e=credFichaErros(d,row&&row.v?Object.assign({},row.v,{valor:row.v.valor===''?null:row.v.valor}):null,HOJE_FICHA);
      if(!Object.keys(e).length)self._fichaCmd={id:row&&row.id,d:Object.assign({},d),rev:Number(d._fichaRev)||0};return e;
    }
    if(gid!=='g_doc'||isNovo||!row||!credAuto(row.id)) return {}; const e={};
    if(String(d.tipo||'')!==String(row.v.tipo||'')) e.tipo=CRED_FIXO; if(String(d.tit||'')!==String(row.v.tit||'')) e.tit=CRED_FIXO; return e; };
  const FD=v.g_doc_F, fmD=g2st(self,'g_doc').fm;
  if(FD&&FD.open&&fmD&&fmD.rid&&credAuto(fmD.rid)) (FD.fields||[]).forEach(f=>{ if(f.fid==='fx_g_doc_tipo'||f.fid==='fx_g_doc_tit'){ f.dis=true; f.ist=String(f.ist||'').replace('background:#FFFFFF','background:#F4F6F3');
    if(!f.err&&f.fid==='fx_g_doc_tit'){ f.help='Documento automático da fazenda: o tipo e a fazenda não mudam aqui. Para outro documento, use "Incluir documento".'; f.hasHelp=true; } } });   // o motivo uma vez, sob os dois campos fixos
  // seletor "Fazenda ou parceiro" (opções dinâmicas do motor): as fazendas ativas do cadastro atual, inclusive as criadas no CD-01, pelo nome de hoje
  self.g2opts=(gid,k,d)=>{ if(gid!=='g_doc'||k!=='tit') return null; const ns=(self._credFz||[]).filter(f=>f.sit!=='Inativa'&&f.nome).map(f=>f.nome);
    if(d&&d.tit&&ns.indexOf(d.tit)<0) ns.push(d.tit); return [{v:'',t:'Escolha…'}].concat(ns.map(n=>({v:n,t:n}))); };
  v.autorizar=()=>{ if(self.state.aut){ self.setState({g2toast:'Bloco já autorizado · consentimento registrado uma vez.'}); return; }
    gsetRow(self,'g_dos','d3',r=>{ r.p.st=[{k:'chip',t:'Autorizado pela Direção',c:'green'}]; r.s.st='Autorizado'; });
    self.setState({aut:true,g2toast:'Autorizado pela Direção · Banco Terra acessa “Compromissos e garantias” até 31/12/2026, só para análise do '+'''+json.dumps(c['id'])+r'''+'.'}); };
  self.g2after=(gid,rows,r)=>{ if(!r) return;
    if(gid==='g_ficha'&&self._fichaCmd){self._fichaCmd.id=r.id;return;}
    if(gid==='g_dos'){ undate(r,['prz']); self.setState({g2toast:'Acesso do bloco '+r.v.blk+' atualizado · novo consentimento registrado; o credor vê após confirmar.'}); }
    if(gid==='g_cre'){ self.setState({g2toast:'Rascunho '+r.id+' salvo · nada é enviado ao credor sem convite confirmado.'}); }
    if(gid==='g_doc'){ undate(r,['val']); self._docPend=r; self.setState({g2toast:'Salvo: '+r.v.tipo+' · '+r.v.tit+' · '+docSit(self,Object.assign({id:r.id},r.v))[0].toLowerCase()+'.'}); } }; }'''
    # 14/10/2026 (proprietário: "coloque os submenus de crédito como os demais"): a tela de entrada do Crédito abre uma visão por cartão
    # (GE-08.dc.html#vis=contratos|liberacoes|dossie), como a Manutenção; os indicadores ficam em todas; sem visão no endereço, tudo
    CV=lambda k: f'<sc-if value="{H("cv_"+k)}" hint-placeholder-val="{H("true")}">'
    acomp=(stepper([('Solicitação','done'),('Dossiê','done'),('Propostas','done'),('Aprovação do credor','done'),('Condição documental','now'),('Liberações','todo'),('Serviço da dívida','todo')],'')
           + f'<div role="status" style="font-size: 13.5px; color: {MUTED};">{H("cre_hint")}</div>'
           + nota(f'Garantias sob controle: penhor de 30% da soja ({nf(penhor)} sc) + CPR de {nf(cpr)} sc (barter CRE-0095) = '
                  f'<b style="color:{INK};">{nf(comp,0)}% da soja prevista (V2 · {nf(SOJA_V2_SC)} sc) comprometida</b>.'))
    ficha=(f'<p style="color:{MUTED}; margin:0;">Ficha do grupo · valores declarados · referência da demonstração: 16/10/2026.</p>'
        + f'<sc-if value="{H("cre_ficha_sem_papel")}"><p role="note">Consulta: somente a direção pode alterar ou confirmar valores. O papel financeiro ainda não está disponível nesta demonstração.</p></sc-if>'
        + f'<sc-if value="{H("cre_ficha_erro")}"><p role="alert">{H("cre_ficha_motivo")}</p>'
        + ibtn('Tentar novamente','cre_ficha_reler','doc')+'</sc-if>'+g_ficha
        + f'<sc-if value="{H("cre_ficha_vazia")}"><p role="status" style="color:{MUTED}; margin:0; font-size: 13px;">{H("cre_ficha_vazia_motivo")}</p></sc-if>')
    corpo=(CV('ficha')+bloco('Ficha do grupo · Bens e avaliações','',ficha,
              acao=ilink('Ver documentos','GE-08.dc.html#vis=documentos','doc'))+'</sc-if>'
        + f'<sc-if value="{H("cv_ficha_nao")}">'
        + kpis([('DÍVIDA ATIVA · 3 CONTRATOS','R$ 1,90 mi',''),('SERVIÇO DA DÍVIDA 26/27','R$ 610 mil','pico jul/27'),
                 ('CAPACIDADE LIVRE NO PERÍODO','R$ 480 mil',''),('A LIBERAR · '+c['id'],'R$ 550 mil','condicionado')])
        + '</sc-if>'
        + CV('contratos') + bloco('Solicitações e contratos','Compare propostas e acompanhe cada contrato; clique numa solicitação em rascunho para prepará-la.',g_cre,
                acao=imsg('Comparar propostas',f'Comparadas 2 propostas do {c["id"]} por CET/CETCR e valor presente com premissas declaradas · Banco Terra 14,2% a.a. vs. Coop Crédito 13,8% a.a. + tarifa.','scale','Comparar propostas por CET/CETCR e valor presente'))
        + '</sc-if>' + CV('liberacoes') + bloco(f'Acompanhamento do {c["id"]}','Cumpra a condição documental para liberar as próximas parcelas; o pedido não aparece pago nem liberado antes do fato financeiro.',acomp,
                acao=doc+ibtn('Registrar liberação da 2ª parcela','lib2','cash','Registrar a 2ª liberação (exige a condição documental aceita)'),tone='yellow')
        + '</sc-if>' + CV('dossie') + bloco('Dossiê e consentimento','Autorize cada bloco com finalidade e prazo; clique num bloco para ajustar quem acessa.',g_dos,tone='gray') + '</sc-if>'
        + CV('documentos') + bloco('Documentos para crédito','CAR, matrícula, contrato de arrendamento e certidões que o credor pede, por fazenda.',g_doc,
                acao=f'<button type="button" onClick="{H("g_doc_new")}" style="{BTN_ST(False,True)} display: inline-flex; align-items: center; gap: 6px;">{__import__("areas.processo_planos",fromlist=["MAIS"]).MAIS(14)}Incluir documento</button>'+ilink('Bens e avaliações','GE-08.dc.html#vis=ficha','doc'),tone='gray') + '</sc-if>')
    shell37('GE-08','Crédito e garantias',corpo,
      subtitle='Solicitações, dossiês autorizados, propostas, decisões, contratos, liberações e serviço da dívida.',
      status=(f'{c["id"]} · condição documental pendente','yellow'),
      primary_html=CV('ficha')+f'<button type="button" disabled="{H("cre_ficha_sem_papel")}" onClick="{H("cre_ficha_novo")}" style="{BTN_ST(True,True)}">Incluir bem</button></sc-if>',
      footer='Capacidade usa caixa disponível ao serviço da dívida por período; CET/CETCR sempre com método e premissas declarados. '
             'O mesmo saco nunca garante dois contratos.')

def build():
    _ge01(); _ge02(); _ge03(); _ge04(); _ge05(); _ge06(); _ge07(); _ge08()

