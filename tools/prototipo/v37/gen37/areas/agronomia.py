# -*- coding: utf-8 -*-
"""Área Agronomia (módulo OCULTO do menu, preservado) — AG-01 Monitoramento e vistorias (+ AG-01det VIS-011) · AG-02 Análises e amostras ·
AG-03 Diagnósticos (+ AG-03det DIA-007) · AG-04 Recomendações (+ AG-04det REC-014 com a decisão da v3) · AG-05 Biblioteca e planos técnicos ·
AG-06 Eficácia e histórico · AG-07 Bulas e registros (AGROFIT).
Padrão novo (25/09/2026): descrição imperativa sob cada bloco, edição pela linha (G2), ações secundárias com ícone + rótulo + title,
sem faixa de etapas (módulo não sequencial). Cadeia DEMO-01 navegável nos dois sentidos: VIS-011 → DIA-007 → REC-014 → NEC-028 → OS-0420 → EF-020.

observacoes (dados locais coerentes com dados.py / dados2.py / campo.py / gestao.py):
- OS-0420 = dados.OS: 100 ha, 30 realizados (18 conf. + 12 prov.), saldo 70 ha, impedida por OM-0233. Mantido 30/70 (não 60/40) porque
  dados.py, campo.py (CA-01x-os0420), gestao.py e OS.dc.html usam 30/70.
- REC-014 v2 (versão vigente da OS-0420): KCl 60 % 120 kg/ha (zonas 140/120/95), TS nematicida 100 mL/100 kg sem., semente 58 W 52 kg/ha
  (REQ-036: 5.200 kg para 100 ha). v3 proposta em 23/09: KCl −12 % só no saldo de 70 ha (105,6 kg/ha; zonas 123/106/84).
- Custo apontado dos 30 ha (igual a gestao.py GE-03): semente 1.560 kg × R$ 9,50; KCl 3.600 kg × R$ 2,40; máquina e equipe 6,0 h × R$ 396;
  diesel 84 L × R$ 5,92 → R$ 26.333,28.
- Datas da cadeia: laudos LAU-2043/2044 12/09 · VIS-011 15/09 · DIA-007 17/09 · REC-014 v1 18/09, v2 aprovada 21/09 · v3 proposta 23/09.
- VIS-011 com os 14 pontos (reboleiras 04/07/10 = 34/41/29 cistos/200 cm³; 11 fora do talhão em recoleta); 2 fotos por ponto = 28.
- DIA-008 passa a citar VIS-012 (vistoria anterior do P2); VIS-015 é a nova coleta do P2, abaixo do limiar.
- EF-019 (dessecação T3, OS-0415 em 10–12/09): pré 08/09 · pós 22/09. EF-020 custo da intervenção R$ 328/ha (KCl 288 + TS 40).
- Novos registros recebem VIS-018, DIA-011, PLA-106 e v1 em diante.
"""
import json
from engine import (grid,Pt,kpis,chip,tag,icon,esc,msgbtn,drawer_button,legend,linechart,BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP,
                    INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAY,GRAYS,SH,DISP)
import engine as E
from ui37 import shell37, HEIGHTS37, PARENT37
import dados as D

H=lambda s: '{{'+s+'}}'
F_=lambda: H('false'); T_=lambda: H('true')
DET0420='CA-01x-os0420.dc.html'   # detalhe da OS-0420 gerado por campo.py
OS20=next(o for o in D.OS if o['id']=='OS-0420'); OS21=next(o for o in D.OS if o['id']=='OS-0421')
AREA20,REAL20,SALDO20=OS20['area'],OS20['realizado'],OS20['saldo']
LAUDOS=('LAU-2043','LAU-2044')

def nf(n,d=0):
    s=f'{n:,.{d}f}'
    return s.replace(',','X').replace('.',',').replace('X','.')

# ---------- vocabulário visual local ----------
def bloco(titulo,desc,corpo,acao='',tone=None):
    dot={'yellow':YEL,'red':RED,'gray':GRAY}.get(tone,ACC)
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
def ilink(text,href,ic,title=None,primary=False,small=True):
    return (f'<a href="{href}" title="{esc(title or text)}" style="{BTN_ST(primary,small)} display: inline-flex; align-items: center; gap: 6px; text-decoration: none;">'
            f'{icon(ic,14)}{esc(text)}</a>')
def imsg(text,msg,ic,title=None,primary=False,small=True):
    return _iconize(msgbtn(text,msg,primary,small),text,ic,title)
def idrawer(text,d,ic,title=None,primary=False,small=True):
    b=drawer_button(text,d,primary,small)
    b=b.replace('style="','style="display: inline-flex; align-items: center; gap: 6px; ',1)
    b=b.replace('<button type="button" ',f'<button type="button" title="{esc(title or text)}" ',1)
    return b.replace('">{{',f'">{icon(ic,14)}{{{{',1)
def nota(html_):
    return f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.6;">{html_}</div>'
def _kv(pares,n=4):
    return (f'<div style="display: grid; grid-template-columns: repeat({n}, minmax(0, 1fr)); gap: 12px 18px; padding: 2px 4px;">'
            + ''.join(f'<div><div style="font-size: 10.5px; font-weight: 700; letter-spacing: .06em; color: {MUTED};">{esc(k.upper())}</div>'
                      f'<div style="font-size: 13.5px; color: {INK}; margin-top: 3px; line-height: 1.4;">{v}</div></div>' for k,v in pares) + '</div>')

# ---------- grade: linhas e campos ----------
def _plain(parts): return ' '.join(p.get('t','') for p in parts if p.get('k')!='br').strip()
def R(_rid,ro=False,o=None,**cells):
    """linha G2: str/número → v; lista de partes → p (+ s para busca/consulta); tupla (valor, partes) → v ordenável + p exibido."""
    r=dict(id=_rid,v={},s={},p={})
    for k,val in cells.items():
        if isinstance(val,tuple): r['v'][k]=val[0]; r['p'][k]=val[1]; r['s'][k]=_plain(val[1])
        elif isinstance(val,list): r['p'][k]=val; r['s'][k]=_plain(val)
        else: r['v'][k]=val
    if ro: r['ro']=True
    if o: r['o']=[dict(t=t,h=h) for t,h in o]
    return r
def F(k,l,t='txt',**kw):
    d=dict(k=k,l=l,t=t)
    if 'def_' in kw: kw['def']=kw.pop('def_')
    d.update(kw); return d
def consulta(cols,title,sub='',m='ro',skip=()):
    return dict(m=m,title=title,sub=sub,fields=[dict(k=c['k'],l=c['l'],ro=True) for c in cols if c['k'] not in skip])

# ---------- cadeia da demonstração (DEMO-01), navegável nos dois sentidos ----------
CADEIA=[('Vistoria','VIS-011','AG-01det.dc.html','Revisada'),
        ('Diagnóstico','DIA-007','AG-03det.dc.html','Decisão registrada'),
        ('Recomendação','REC-014 v2','AG-04det.dc.html','Aprovada · v3 em decisão'),
        ('Necessidade','NEC-028','PL-02.dc.html','Programada · 1ª onda 100 ha'),
        ('O.S.','OS-0420',DET0420,f'Em execução · Impedida · {REAL20}/{AREA20} ha'),
        ('Avaliação','EF-020','AG-06.dc.html','Aguarda leitura pós')]
def cadeia(atual,prox_t,prox_h):
    cells=[]
    for i,(lbl,rid,href,st) in enumerate(CADEIA):
        cur=(rid.split()[0]==atual)
        inner=(f'<span style="font-size: 10.5px; font-weight: 700; letter-spacing: .06em; color: {MUTED};">{esc(lbl.upper())}</span>'
               f'<span style="font-size: 13px; font-weight: 800; color: {ACC if not cur else INK};">{esc(rid)}{"" if cur else " ›"}</span>'
               f'<span style="font-size: 11.5px; color: {MUTED}; line-height: 1.3;">{esc(st)}</span>')
        box='display: flex; flex-direction: column; gap: 2px; flex: 1 1 0; min-width: 0; padding: 8px 10px; border-radius: 10px; text-decoration: none;'
        if cur: cells.append(f'<div aria-current="step" style="{box} background: {SURF}; border: 2px solid {ACC};">{inner}</div>')
        else: cells.append(f'<a href="{href}" title="Abrir {esc(lbl.lower())} {esc(rid)}" style="{box} background: {SURF}; border: 1px solid {LINE};">{inner}</a>')
        if i<len(CADEIA)-1: cells.append(f'<span aria-hidden="true" style="color: {MUTED}; align-self: center;">→</span>')
    return (f'<nav aria-label="Cadeia da demonstração" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; background: {ACCS}; border: 1px solid {LINE}; border-radius: 12px;">'
            f'<div style="display: flex; align-items: stretch; gap: 6px;">{"".join(cells)}</div>'
            f'<div style="font-size: 12.5px; color: {MUTED};">Cada elo abre o registro · <b style="color: {INK};">Próxima ação:</b> '
            f'<a href="{prox_h}" style="color: {ACC}; font-weight: 700; text-decoration: none;">{esc(prox_t)} ›</a></div></nav>')

def mapa_vis011(h=300):
    """Rota em W da VIS-011 (T4): reboleiras de nematoide nos pontos 04, 07 e 10; ponto 11 fora do talhão (recoleta)."""
    cor={4:RED,7:RED,10:RED,3:YEL,9:YEL,11:GRAY}
    pos=[(70,55),(170,115),(270,55),(370,115),(470,55),(570,115),(630,55),
         (630,175),(530,232),(430,175),(330,232),(230,175),(130,232),(70,175)]
    s=f'<svg viewBox="0 0 700 {h}" style="width: 100%; height: {h}px; display: block; border-radius: 10px;" role="img" aria-label="Rota em W da vistoria VIS-011 no T4">'
    s+=f'<rect x="0" y="0" width="700" height="{h}" fill="#E3EBDD"/><polygon points="20,18 680,22 690,{h-18} 14,{h-22}" fill="#B5E61D" fill-opacity=".55" stroke="#fff" stroke-width="3"/>'
    s+='<polyline points="'+' '.join(f'{x},{y}' for x,y in pos)+f'" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="6 5" opacity=".6"/>'
    for i,(x,y) in enumerate(pos,1):
        c=cor.get(i,ACC)
        s+=f'<circle cx="{x}" cy="{y}" r="13" fill="{c}" stroke="#fff" stroke-width="2.5"/><text x="{x}" y="{y+4}" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">{i:02d}</text>'
    return s+'</svg>'

# ---------- JS comum: novos registros recebem número e estado inicial ----------
JS_NOVO='''
function agNovo(self,rows,r,idk,pref,base,parts,msg){
  if(String(r.id).indexOf('n')!==0 || r.v[idk]) return false;
  const n=base+rows.filter(x=>String(x.id).indexOf('n')===0).length-1; const id=pref+String(n);
  r.v[idk]=id; r.s[idk]=id; r.p[idk]=[{k:'b',t:id}];
  for(const k in (parts||{})){ r.p[k]=parts[k]; r.s[k]=parts[k].map(x=>x.t||'').join(' '); }
  self.setState({g2toast:msg.replace('{id}',id)}); return true; }
'''

def build():
    # ================= AG-01 · Monitoramento e vistorias =================
    fname='AG-01.dc.html'; E._reset_screen(fname)
    PARC=['T4 · Soja 58 W','T2 · Soja','T1 · Soja','P1 · Feijão','P2 · Milho','C1 · Café (ano-safra)','T7 · Mamão Formosa']
    ALVOS=['Nematoide-de-cisto','Mosca-branca','Ácaro','Lagarta-do-cartucho','Mancha-de-phoma','Daninhas pré-plantio','Percevejo-marrom','Ferrugem asiática']
    PROT=['MIP Soja v4','MIP Feijão v2','MIP Milho v3','Café v1']
    MET=['trincheira · cistos/200 cm³','pano-de-batida · adultos/batida','contagem direta · % folíolos','contagem direta · % plantas','contagem direta · % ramos','caminhamento · plantas/m²']
    c1=[dict(k='id',l='Vistoria'),dict(k='parc',l='Ciclo · parcela',w=110),dict(k='alvo',l='Alvo · estádio',w=140),dict(k='prot',l='Protocolo · método',w=150),
        dict(k='data',l='Data',t='date'),dict(k='amos',l='Amostras · qualidade',w=140),dict(k='sit',l='Situação',w=150),dict(k='acao',l='Próxima ação')]
    rows1=[
      R('VIS-011',ro=True,id=[Pt.link('VIS-011','AG-01det.dc.html')],parc='T4 · Soja 58 W',alvo=('Nematoide-de-cisto',[Pt.txt('Nematoide-de-cisto'),Pt.br(),Pt.mut('pré-plantio')]),est='pré-plantio',prot=('MIP Soja v4',[Pt.tag('MIP Soja v4'),Pt.br(),Pt.mut('trincheira · cistos/200 cm³')]),
        met='trincheira · cistos/200 cm³',resp='Marcos',data='2026-09-15',amos=[Pt.txt('14/14 pontos · 28 fotos'),Pt.br(),Pt.mut('ponto 11 em recoleta')],
        sit=[Pt.chip('Revisada','green'),Pt.br(),Pt.mut('virou DIA-007')],acao=[Pt.cta('Abrir vistoria','AG-01det.dc.html')]),
      R('VIS-013',ro=True,id=[Pt.b('VIS-013')],parc='P1 · Feijão',alvo=('Mosca-branca',[Pt.txt('Mosca-branca'),Pt.br(),Pt.mut('R5')]),est='R5',prot=('MIP Feijão v2',[Pt.tag('MIP Feijão v2'),Pt.br(),Pt.mut('pano-de-batida · adultos/batida')]),
        met='pano-de-batida · adultos/batida',resp='Marcos',data='2026-09-18',amos=[Pt.txt('12/12 pontos · GPS ok')],
        sit=[Pt.chip('Acima do NC','red'),Pt.br(),Pt.mut('5,1/4,0 · em DIA-009')],acao=[Pt.cta('Abrir diagnóstico','AG-03.dc.html',u=True)]),
      R('VIS-014',id=[Pt.b('VIS-014')],parc='P1 · Feijão',alvo=('Ácaro',[Pt.txt('Ácaro'),Pt.br(),Pt.mut('R5')]),est='R5',prot=('MIP Feijão v2',[Pt.tag('MIP Feijão v2'),Pt.br(),Pt.mut('contagem direta · % folíolos')]),
        met='contagem direta · % folíolos',resp='Marcos',data='2026-09-25',amos=[Pt.txt('9/14 pontos'),Pt.br(),Pt.mut('próximo: ponto 10')],
        sit=[Pt.chip('Coleta em campo','green')],acao=[Pt.cta('Coletar ponto 10','MB-06.dc.html')]),
      R('VIS-015',id=[Pt.b('VIS-015')],parc='P2 · Milho',alvo=('Lagarta-do-cartucho',[Pt.txt('Lagarta-do-cartucho'),Pt.br(),Pt.mut('V10')]),est='V10',prot=('MIP Milho v3',[Pt.tag('MIP Milho v3'),Pt.br(),Pt.mut('contagem direta · % plantas')]),
        met='contagem direta · % plantas',resp='Marcos',data='2026-09-22',amos=[Pt.txt('14/14 pontos · GPS ok')],
        sit=[Pt.chip('Coleta completa','green'),Pt.br(),Pt.mut('abaixo do limiar')],
        acao=[Pt.act('Concluir coleta','VIS-015 concluída · abaixo do limiar: o manejo preventivo do plano técnico permanece; nada é cancelado automaticamente.')]),
      R('VIS-016',id=[Pt.b('VIS-016')],parc='C1 · Café (ano-safra)',alvo=('Mancha-de-phoma',[Pt.txt('Mancha-de-phoma'),Pt.br(),Pt.mut('granação')]),est='granação',prot=('Café v1',[Pt.tag('Café v1'),Pt.br(),Pt.mut('contagem direta · % ramos')]),
        met='contagem direta · % ramos',resp='João',data='2026-09-24',amos=[Pt.txt('6/12 pontos'),Pt.br(),Pt.mut('no dispositivo de João')],
        sit=[Pt.chip('Sincronizar','yellow'),Pt.br(),Pt.mut('pacote offline pendente')],
        acao=[Pt.act('Sincronizar agora','Pacote offline de João aplicado · 6 pontos e 12 fotos entraram na VIS-016 · sem conflito de versão.')]),
      R('VIS-017',id=[Pt.b('VIS-017')],parc='T2 · Soja',alvo=('Daninhas pré-plantio',[Pt.txt('Daninhas pré-plantio'),Pt.br(),Pt.mut('—')]),est='—',prot=('MIP Soja v4',[Pt.tag('MIP Soja v4'),Pt.br(),Pt.mut('caminhamento · plantas/m²')]),
        met='caminhamento · plantas/m²',resp='Marcos',data='2026-09-26',amos=[Pt.txt('0/16 pontos')],
        sit=[Pt.chip('Programada','yellow'),Pt.br(),Pt.mut('coleta até 26/09')],acao=[Pt.cta('Coletar','MB-06.dc.html')]),
    ]
    g1=grid(c1,rows1,edit=dict(m='form',title='Vistoria',newTitle='Programar vistoria',
             sub='Programe ou ajuste a vistoria; ela entra na rota do vistoriador e o app coleta ponto a ponto com GPS e fotos. Vistoria revisada fica em consulta.',
             fields=[F('parc','Ciclo · parcela','sel',opts=PARC,req=True,def_='T2 · Soja'),F('alvo','Alvo','sel',opts=ALVOS,req=True,def_='Percevejo-marrom'),
                     F('est','Estádio','sel',opts=['—','pré-plantio','V4','V10','R1','R3','R5','granação'],req=True,def_='—'),
                     F('prot','Protocolo','sel',opts=PROT,req=True,def_='MIP Soja v4'),F('met','Método · unidade','sel',opts=MET,req=True,def_='pano-de-batida · adultos/batida'),
                     F('data','Data','date',req=True),F('resp','Responsável','sel',opts=['Marcos','João','Ana','Paula'],req=True,def_='Marcos')]),
             add='Programar vistoria',gid='g_vis',so=dict(k='data',d=True),total=False)
    EXTRAJS[0]=JS_NOVO+'''
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{ if(gid!=='g_vis') return;
  r.p.alvo=[{k:'txt',t:r.v.alvo},{k:'br'},{k:'mut',t:r.v.est||'—'}]; r.s.alvo=r.v.alvo+' '+(r.v.est||'');
  r.p.prot=[{k:'tag',t:r.v.prot},{k:'br'},{k:'mut',t:r.v.met||''}]; r.s.prot=r.v.prot+' '+(r.v.met||'');
  if(!agNovo(self,rows,r,'id','VIS-0',18,
  {sit:[{k:'chip',t:'Programada',c:'gray'}],amos:[{k:'mut',t:'0 pontos · aguarda coleta'}],acao:[{k:'cta',t:'Coletar',h:'MB-06.dc.html'}]},
  '{id} programada · entrou na rota do vistoriador; o app coleta ponto a ponto.')) self.setState({g2toast:'Vistoria salva · rota atualizada.'}); }; }'''
    corpo=bloco('Vistorias por ciclo e parcela','Acompanhe as coletas e siga a próxima ação; clique na linha para ajustar a vistoria.',g1)
    HEIGHTS37[fname]=780
    shell37('AG-01','Monitoramento e vistorias',corpo,fname=fname,
      subtitle='Rotas, alvos e vistorias por ciclo e parcela; o detalhe mostra pontos, evidências e série temporal.',
      status=('1 sincronização pendente','yellow'),
      primary_html=ilink('Coletar próximo ponto','MB-06.dc.html','map','Abrir o app na VIS-014, ponto 10',primary=True,small=False),
      footer='O próximo ponto avança dentro da rota; abaixo do limiar não cancela o manejo preventivo; critério por presença não divide por zero.')

    # ---- AG-01det · VIS-011 ----
    fname='AG-01det.dc.html'; E._reset_screen(fname)
    PTS=[(1,'−17,840 · −50,615','07:28',4),(2,'−17,841 · −50,614','07:35',6),(3,'−17,842 · −50,613','07:42',12),(4,'−17,843 · −50,611','07:55',34),
         (5,'−17,843 · −50,610','08:02',5),(6,'−17,844 · −50,610','08:08',7),(7,'−17,845 · −50,609','08:15',41),(8,'−17,846 · −50,608','08:26',3),
         (9,'−17,847 · −50,607','08:37',13),(10,'−17,848 · −50,606','08:48',29),(11,'−17,849 · −50,604','09:02',9),(12,'−17,850 · −50,603','09:10',5),
         (13,'−17,850 · −50,602','09:20',4),(14,'−17,851 · −50,601','09:30',6)]
    reb=[c for n,_,_,c in PTS if c>15]; media=sum(reb)/len(reb)
    def _cor(c): return 'red' if c>15 else ('yellow' if c>=10 else 'green')
    prow=[]
    for n,gps,hr,c in PTS:
        q=[Pt.chip('GPS ±42 m · fora do talhão','red')] if n==11 else [Pt.chip('OK','green')]
        ac=[Pt.act('Marcar recoleta','Ponto 11 devolvido à rota de amanhã · a contagem dele fica fora da média até a nova coleta; o original é preservado.')] if n==11 else []
        prow.append(R(f'p{n}',pt=f'{n:02d}',gps=gps,hora=hr,cont=(c,[{'k':'cn','t':str(c),'c':('gray' if n==11 else _cor(c))}]),nc=('recoleta' if n==11 else ('acima do NC' if c>15 else ('atenção' if c>=10 else 'abaixo do NC'))),
                      fotos=2,qual=q,acao=ac))
    cp=[dict(k='pt',l='Ponto'),dict(k='gps',l='GPS'),dict(k='hora',l='Hora'),dict(k='cont',l='Cistos/200 cm³',t='num',a='r'),
        dict(k='nc',l='× NC 15',chips={'acima do NC':'red','atenção':'yellow','abaixo do NC':'green','recoleta':'gray'}),dict(k='fotos',l='Fotos',t='num',a='r'),dict(k='qual',l='Qualidade'),dict(k='acao',l='Ação')]
    for r in prow: r['p']['nc']=[Pt.chip(r['v']['nc'],{'acima do NC':'red','atenção':'yellow','abaixo do NC':'green','recoleta':'gray'}[r['v']['nc']])]; r['s']['nc']=r['v']['nc']
    gp=grid(cp,prow,edit=consulta(cp,'Ponto da vistoria','Evidência de campo: o original não se altera; posição fora do talhão volta para recoleta.',skip=('acao',)),
            search=False,gid='g_pts',total=False)
    fotos=''.join(
      f'<div style="flex: 1 1 0; min-width: 0; border: 1px solid {LINE}; border-radius: 12px; overflow: hidden; background: {BG};">'
      f'<div style="height: 84px; background: linear-gradient(135deg, {ACCS}, {GRAYS}); display: flex; align-items: center; justify-content: center;">{icon("map",26,MUTED)}</div>'
      f'<div style="padding: 8px 10px; font-size: 11.5px; color: {MUTED};"><b style="color:{INK};">{p}</b> · {h}<br>GPS {g}</div></div>'
      for p,h,g in [('Ponto 04','07:55','−17,843 · −50,611 (±4 m)'),('Ponto 07','08:15','−17,845 · −50,609 (±3 m)'),
                    ('Ponto 07 · raiz','08:17','−17,845 · −50,609 (±3 m)'),('Ponto 11','09:02','−17,849 · −50,604 (±42 m · fora do talhão)')])
    serie=linechart([5,8,14,22,round(media)],w=1100,h=210,labels=[(0,'mai'),(1,'jun'),(2,'jul'),(3,'ago'),(4,'set')],unit='cistos/200 cm³').replace('Série de preços','Série de cistos nas reboleiras do T4')
    corpo=(
      cadeia('VIS-011','Abrir diagnóstico DIA-007','AG-03det.dc.html')
      + kpis([('PONTOS','14/14','1 em recoleta'),('MÉDIA NAS REBOLEIRAS',f'{round(media)}','cistos/200 cm³ · NC 15'),('REBOLEIRAS',str(len(reb)),'pontos 04, 07, 10'),('EVIDÊNCIAS','28 fotos','GPS e hora')])
      + bloco('Rota em W e pontos','Confira cada ponto contra o nível de controle; clique na linha para ver a evidência completa.',
          mapa_vis011()+gp,legend([(ACC,'abaixo do NC'),(YEL,'atenção'),(RED,'acima do NC'),(GRAY,'recoleta')]))
      + bloco('Série temporal do alvo','Compare com as vistorias anteriores no mesmo método e unidade; a decisão fica no diagnóstico.',
          serie + nota(f'Média dos pontos de reboleira (04, 07, 10) em cada vistoria · NC 15 cistos/200 cm³ (MIP Soja v4).'))
      + bloco('Evidências com GPS e hora','Confira as fotos originais; o ponto 11 volta para recoleta pela linha da tabela.',
          f'<div style="display: flex; gap: 10px;">{fotos}</div>'))
    HEIGHTS37[fname]=1700; PARENT37[fname]='AG-01.dc.html'
    shell37('AG-01','Vistoria · VIS-011 nematoide T4',corpo,fname=fname,crumbs_extra=['VIS-011'],
      subtitle='T4 · Soja 58 W · pré-plantio · MIP Soja v4 · trincheira · coleta de 15/09 por Marcos, revisada por Ana.',
      status=('Revisada · 1 ponto em recoleta','yellow'),
      primary_html=ilink('Abrir diagnóstico DIA-007','AG-03det.dc.html','leaf','Abrir a decisão técnica que nasceu desta vistoria',primary=True,small=False),
      footer='Contagem acima do NC sugere diagnóstico; a decisão técnica é registrada no DIA-007, nunca na vistoria.')

    # ================= AG-02 · Análises e amostras =================
    fname='AG-02.dc.html'; E._reset_screen(fname)
    c2=[dict(k='id',l='Laudo · amostra'),dict(k='local',l='Local · área representada',w=170),dict(k='prof',l='Profund.'),dict(k='data',l='Data',t='date'),
        dict(k='lab',l='Laboratório',w=120),dict(k='met',l='Método · extrator',w=120),dict(k='val',l='Validação',w=150),dict(k='acao',l='Próxima ação',w=150)]
    rows2=[
      R('LAU-2043',ro=True,id=[Pt.b('LAU-2043'),Pt.mut('solo')],local='T4 · 204 ha · composta por zona (3 zonas)',prof='0–20 cm',data='2026-09-12',lab='Lab Solo Vale',met='Mehlich-1',
        val=[Pt.chip('Validado','green')],acao=[Pt.cta('Abrir diagnóstico','AG-03det.dc.html')]),
      R('LAU-2044',ro=True,id=[Pt.b('LAU-2044'),Pt.mut('solo')],local='T4 · 204 ha · composta por zona (3 zonas)',prof='20–40 cm',data='2026-09-12',lab='Lab Solo Vale',met='Mehlich-1',
        val=[Pt.chip('Validado','green')],acao=[Pt.cta('Abrir diagnóstico','AG-03det.dc.html')]),
      R('LAU-2048',ro=True,id=[Pt.b('LAU-2048'),Pt.mut('folha')],local='P1 · 95 ha · terço médio R5',prof='—',data='2026-09-18',lab='Agrolab',met='digestão nítrico-perclórica',
        val=[Pt.chip('Inconsistente','red'),Pt.br(),Pt.mut('K sem unidade')],acao=[Pt.mut('corrija o K no painel abaixo')]),
      R('LAU-2050',ro=True,id=[Pt.b('LAU-2050'),Pt.mut('solo')],local='C1 · 38 ha · composta',prof='0–20 cm',data='2026-09-19',lab='Agrolab',met='Resina',
        val=[Pt.chip('Aguardando validação','yellow')],
        acao=[Pt.act('Validar dados','LAU-2050 validado por Ana · original preservado ao lado dos valores extraídos · liberado para diagnóstico.')]),
      R('PLA-104',id=[Pt.b('PLA-104'),Pt.mut('plano')],local='T2 · 298 ha · grade 16 pontos',prof='0–20 cm',data='2026-09-26',lab='Lab Solo Vale',met='Mehlich-1',
        val=[Pt.chip('Coleta até 26/09','yellow')],acao=[Pt.cta('Coletar','MB-06.dc.html')]),
      R('PLA-105',id=[Pt.b('PLA-105'),Pt.mut('plano')],local='C1 · 38 ha · nematoide',prof='0–20 cm',data='2026-09-30',lab='Embrapa Solos (convênio)',met='extração de cistos',
        val=[Pt.chip('Planejada','gray')],acao=[Pt.cta('Coletar','MB-06.dc.html')]),
    ]
    g2=grid(c2,rows2,edit=dict(m='form',title='Amostra',newTitle='Planejar coleta',
             sub='Planeje a coleta por grade ou zona; a amostra composta representa a área declarada, sem resolução espacial inventada. Laudo recebido fica em consulta.',
             fields=[F('local','Local · área representada','txt',req=True,help='Ex.: T2 · 298 ha · grade 16 pontos'),F('prof','Profundidade','sel',opts=['0–20 cm','20–40 cm','0–10 cm','40–60 cm'],req=True,def_='0–20 cm'),
                     F('data','Data','date',req=True),F('lab','Laboratório','sel',opts=['Lab Solo Vale','Agrolab','Embrapa Solos (convênio)'],req=True,def_='Lab Solo Vale'),
                     F('met','Método · extrator','sel',opts=['Mehlich-1','Resina','DTPA','extração de cistos','digestão nítrico-perclórica'],req=True,def_='Mehlich-1')]),
             add='Planejar coleta',gid='g_lau',so=dict(k='data',d=True),total=False)
    c2e=[dict(k='atr',l='Atributo'),dict(k='val',l='Valor',t='num',a='r',d=1),dict(k='un',l='Unidade',chips={'sem unidade':'red'}),dict(k='ld',l='LD')]
    ext=[R('N',atr='N',val=48.2,un='g/kg',ld='0,1'),R('P',atr='P',val=3.1,un='g/kg',ld='0,1'),
         R('K',atr='K',val=17.4,un=('sem unidade',[Pt.chip('sem unidade','red')]),ld='—'),R('B',atr='B',val=42,un='mg/kg',ld='1')]
    g2e=grid(c2e,ext,edit=dict(m='form',title='Valor extraído',sub='Corrija o valor ou a unidade lida pelo OCR; o PDF original não se altera e o laudo volta para validação humana.',
             fields=[F('val','Valor','num',req=True,min=0),F('un','Unidade','sel',opts=['sem unidade','g/kg','mg/kg','dag/kg'],req=True),F('ld','Limite de detecção','txt')]),
             search=False,gid='g_ext',total=False)
    EXTRAJS[0]=JS_NOVO+'''
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{
  if(gid==='g_lau') agNovo(self,rows,r,'id','PLA-',106,{val:[{k:'chip',t:'Planejada',c:'gray'}],acao:[{k:'cta',t:'Coletar',h:'MB-06.dc.html'}]},'{id} planejado · pontos enviados ao app do coletor.');
  if(gid==='g_ext' && r.id==='K' && r.v.un && r.v.un!=='sem unidade'){
    const sp=GRIDS.find(g=>g.id==='g_lau'); const x=g2find(g2rows(self,sp),'LAU-2048');
    if(x){ x.p.val=[{k:'chip',t:'Aguardando validação',c:'yellow'}]; x.s.val='Aguardando validação'; x.p.acao=[{k:'mut',t:'mapeamento salvo · aguarda validação humana'}]; x.s.acao=''; }
    self.setState({g2toast:'K corrigido para '+r.v.un+' · mapeamento salvo para o Agrolab · LAU-2048 volta à validação humana; a REC-015 segue bloqueada até validar.'}); } }; }'''
    orig=(f'<div style="border: 1px solid {LINE}; border-radius: 12px; padding: 12px 14px; background: {BG};"><div style="font-size: 11px; font-weight: 700; color: {MUTED}; letter-spacing: .06em;">ORIGINAL · PDF DO LABORATÓRIO</div>'
          f'<div style="height: 150px; margin-top: 8px; border: 1px dashed {LINE}; border-radius: 8px; display: flex; align-items: center; justify-content: center; gap: 6px; color: {MUTED}; font-size: 12.5px;">{icon("doc",18,MUTED)}laudo_agrolab_P1_folha.pdf · pág. 1/2</div></div>')
    corpo=(
      bloco('Planos de amostragem, amostras e laudos','Planeje coletas e acompanhe a validação; clique na linha para ajustar um plano ou consultar o laudo.',g2,
          idrawer('Importar laudo',dict(title='Importar laudo',sub='O original fica ao lado dos valores extraídos; OCR nunca aprova o laudo.',
             fields=[('Laboratório','Lab Solo Vale'),('Arquivo do laudo (PDF)',''),('Talhão','T2 · 298 ha'),('Profundidade','0–20 cm'),('Mapeamento de colunas','Lab Solo Vale · padrão v3')],
             confirm='Importar e abrir prévia',done='Prévia aberta · erros por linha destacados'),'doc','Importar o PDF do laboratório e abrir a prévia com erros por linha',primary=True))
      + bloco('Original ao lado do extraído · LAU-2048','Compare o PDF com os valores extraídos e corrija a unidade do K pela linha.',
          f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-items: start;">{orig}{g2e}</div>',tone='red'))
    HEIGHTS37[fname]=980
    shell37('AG-02','Análises e amostras',corpo,fname=fname,
      subtitle='Planos de amostragem, amostras e laudos com método, extrator, profundidade e limite de detecção.',
      status=('1 laudo inconsistente','yellow'),
      footer='OCR não aprova laudo; o original é preservado; inconsistência bloqueia só a recomendação dependente (REC-015), não a fazenda.')

    # ================= AG-03 · Diagnósticos =================
    fname='AG-03.dc.html'; E._reset_screen(fname)
    c3=[dict(k='id',l='Diagnóstico',w=120),dict(k='parc',l='Ciclo · parcela',w=110),dict(k='evid',l='Evidências',w=140),dict(k='hip',l='Hipótese · causa',w=160),
        dict(k='risco',l='Risco',chips={'alto':'red','médio':'yellow','baixo':'green'}),dict(k='acp',l='Ação proposta',w=150),
        dict(k='sit',l='Situação',w=120),dict(k='acao',l='Próxima ação')]
    rk=lambda t:(t,[Pt.chip(t,{'alto':'red','médio':'yellow','baixo':'green'}[t])])
    rows3=[
      R('DIA-007',ro=True,id=[Pt.link('DIA-007','AG-03det.dc.html')],parc='T4 · Soja 58 W',evid=[Pt.link('VIS-011','AG-01det.dc.html'),Pt.br(),Pt.mut('+ LAU-2043/2044')],
        hip='Reboleiras de nematoide + K baixo no perfil (0–20)',meta='plantio na janela 20/09–05/10',risco=rk('alto'),acp='Cultivar resistente + TS nematicida + K na base',resp='Ana',
        sit=[Pt.chip('Registrada','green')],acao=[Pt.cta('Abrir REC-014','AG-04det.dc.html')]),
      R('DIA-009',id=[Pt.b('DIA-009')],parc='P1 · Feijão',evid=[Pt.txt('VIS-013 +'),Pt.link('LAU-2048','AG-02.dc.html'),Pt.br(),Pt.mut('laudo inconsistente')],
        hip='Mosca-branca acima do NC; nutrição a confirmar',meta='segurar produtividade no R5',risco=rk('alto'),acp='Inseticida seletivo após laudo foliar válido',resp='Ana',
        sit=[Pt.chip('Bloqueado','red'),Pt.br(),Pt.mut('falta evidência válida')],acao=[Pt.cta('Solicitar evidência','AG-02.dc.html',u=True)]),
      R('DIA-010',id=[Pt.b('DIA-010'),Pt.br(),Pt.tag('Emergência MIP')],parc='C1 · Café (ano-safra)',evid=[Pt.txt('VIS-016'),Pt.br(),Pt.mut('parcial · 6 pontos')],
        hip='Mancha-de-phoma em expansão na granação',meta='proteger a carga pendente',risco=rk('alto'),acp='Intervir já; não depende de laudo de solo',resp='Ana',
        sit=[Pt.chip('A decidir','yellow')],
        acao=[Pt.act('Registrar decisão','Decisão registrada no DIA-010: intervenção imediata autorizada tecnicamente · segue para recomendação com dose formalizada.')]),
      R('DIA-008',ro=True,id=[Pt.b('DIA-008')],parc='P2 · Milho',evid=[Pt.txt('VIS-012'),Pt.br(),Pt.mut('abaixo do limiar · 08/09')],
        hip='Lagarta-do-cartucho abaixo do NC',meta='manter o custo do plano',risco=rk('baixo'),acp='Manter monitoramento semanal',resp='Marcos',
        sit=[Pt.chip('Sem intervenção','gray')],acao=[Pt.cta('Comparar cenário','PL-02.dc.html')]),
    ]
    g3=grid(c3,rows3,edit=dict(m='form',title='Diagnóstico',newTitle='Criar diagnóstico',
             sub='Reúna as evidências e registre a interpretação e a decisão; dose e produto são formalizados na recomendação. Decisão registrada fica em consulta (alterar cria nova versão).',
             fields=[F('parc','Ciclo · parcela','sel',opts=PARC,req=True,def_='T2 · Soja'),F('evid','Evidências (vistoria · laudo)','txt',req=True,help='Ex.: VIS-017 · PLA-104'),
                     F('hip','Hipótese · causa','area',req=True),F('meta','Meta','txt',req=True),F('risco','Risco','sel',opts=['baixo','médio','alto'],req=True,def_='médio'),
                     F('acp','Ação proposta','area',req=True),F('resp','Responsável','sel',opts=['Ana','Marcos'],req=True,def_='Ana')]),
             add='Criar diagnóstico',gid='g_dia',total=False)
    EXTRAJS[0]=JS_NOVO+'''
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{ if(gid==='g_dia') agNovo(self,rows,r,'id','DIA-0',11,
  {sit:[{k:'chip',t:'Rascunho',c:'gray'}],acao:[{k:'mut',t:'registre a decisão na linha'}]},'{id} criado em rascunho · a decisão é registrada pelo agrônomo responsável.'); }; }'''
    corpo=bloco('Decisões técnicas por ciclo e parcela','Registre interpretação e decisão com evidência vinculada; clique na linha para completar um diagnóstico.',g3)
    HEIGHTS37[fname]=680
    shell37('AG-03','Diagnósticos',corpo,fname=fname,
      subtitle='Decisões técnicas por ciclo e parcela com solo, folha, vistoria, histórico e contexto econômico.',
      status=('1 aguardando evidência','yellow'),
      footer='Diagnóstico descreve interpretação e decisão; doses ficam na recomendação; emergência MIP não espera laudo de solo irrelevante.')

    # ---- AG-03det · DIA-007 (elo 2 da cadeia) ----
    fname='AG-03det.dc.html'; E._reset_screen(fname)
    cev=[dict(k='reg',l='Evidência'),dict(k='tipo',l='Tipo'),dict(k='data',l='Data',t='date'),dict(k='achado',l='O que mostra',w=380),dict(k='fonte',l='Fonte')]
    gev=grid(cev,[
        R('e1',reg=[Pt.link('VIS-011','AG-01det.dc.html')],tipo='Vistoria · trincheira',data='2026-09-15',achado='3 reboleiras (pontos 04, 07, 10) com 34, 41 e 29 cistos/200 cm³ · NC 15',fonte='MIP Soja v4'),
        R('e2',reg=[Pt.link('LAU-2043','AG-02.dc.html')],tipo='Laudo de solo · 0–20 cm',data='2026-09-12',achado='K trocável 0,08 cmolc/dm³ · CTC 9,2 · participação de K 0,9 % (alvo 3 %)',fonte='Lab Solo Vale · Mehlich-1'),
        R('e3',reg=[Pt.link('LAU-2044','AG-02.dc.html')],tipo='Laudo de solo · 20–40 cm',data='2026-09-12',achado='K trocável 0,06 cmolc/dm³ · sem barreira química',fonte='Lab Solo Vale · Mehlich-1'),
      ],edit=consulta(cev,'Evidência','Evidência vinculada ao diagnóstico; abra o registro de origem pelo link.'),search=False,gid='g_ev',total=False)
    corpo=(
      cadeia('DIA-007','Abrir recomendação REC-014','AG-04det.dc.html')
      + bloco('Decisão técnica','Confira a interpretação registrada; dose e produto estão na recomendação.',
          _kv([('Ciclo · parcela','Safra 2026/27 · T4 · 204 ha'),('Cultura · cultivar','Soja · 58 W (resistente)'),('Meta','plantio na janela 20/09–05/10'),('Risco',chip('alto','red')),
               ('Hipótese · causa','Reboleiras de nematoide-de-cisto + K baixo no perfil (0–20 cm)'),('Ação proposta','Cultivar resistente + TS nematicida + K na base'),
               ('Responsável','Ana (RT) · registrada em 17/09'),('Destino','<a href="AG-04det.dc.html" style="color: '+ACC+'; font-weight: 700; text-decoration: none;">REC-014 v2 ›</a>')]))
      + bloco('Evidências vinculadas','Abra cada evidência na origem; clique na linha para ver o resumo.',gev))
    HEIGHTS37[fname]=900; PARENT37[fname]='AG-03.dc.html'
    shell37('AG-03','Diagnóstico · DIA-007 nematoide T4',corpo,fname=fname,crumbs_extra=['DIA-007'],
      subtitle='Interpretação da VIS-011 com os laudos do T4; a decisão virou a recomendação REC-014.',
      status=('Decisão registrada','green'),
      primary_html=ilink('Abrir recomendação REC-014','AG-04det.dc.html','leaf','Abrir a recomendação que formalizou esta decisão',primary=True,small=False),
      footer='Alterar uma decisão registrada cria nova versão do diagnóstico; a recomendação aprovada não muda sozinha.')

    # ================= AG-04 · Recomendações =================
    fname='AG-04.dc.html'; E._reset_screen(fname)
    c4=[dict(k='id',l='Recomendação'),dict(k='parc',l='Parcela',w=100),dict(k='orig',l='Origem',w=130),dict(k='op',l='Operação · alvo',w=120),
        dict(k='prod',l='Produto · dose · janela',w=150),dict(k='fonte',l='Fonte · aprovador',w=110),dict(k='sit',l='Situação',w=140),dict(k='acao',l='Ação')]
    rows4=[
      R('REC-014',ro=True,id=[Pt.link('REC-014','AG-04det.dc.html'),Pt.mut('v2')],parc='T4 · Soja 58 W',orig=[Pt.link('DIA-007','AG-03det.dc.html'),Pt.mut('VIS-011')],
        op='Plantio · nematoide + K',prod=('KCl 60 % 120 kg/ha + TS nematicida',[Pt.txt('KCl 60 % 120 kg/ha + TS nematicida'),Pt.br(),Pt.mut('janela: 20/09–05/10')]),jan='20/09–05/10',fonte='IAC Boletim 100 · Ana (RT)',
        sit=[Pt.chip('Aprovada','green'),Pt.br(),Pt.chip('v3 em decisão','yellow')],acao=[Pt.cta('Decidir v3','AG-04det.dc.html',u=True)]),
      R('REC-016',ro=True,id=[Pt.b('REC-016'),Pt.mut('v1')],parc='T1+T2 · Soja',orig='Protocolo Soja alta tecnologia v6',op='Pulverização · ferrugem asiática',
        prod=('Fungicida A 0,4 L/ha',[Pt.txt('Fungicida A 0,4 L/ha'),Pt.br(),Pt.mut('janela: em execução')]),jan='em execução',fonte='bula AGROFIT · Ana (RT)',
        sit=[Pt.chip('Aprovada','green'),Pt.br(),Pt.mut(f'OS-0421 · {OS21["realizado"]}/{OS21["area"]} ha')],acao=[Pt.cta('Ver execução','CA-01det.dc.html')]),
      R('REC-017',ro=True,id=[Pt.b('REC-017'),Pt.mut('v2')],parc='P1 · Feijão',orig='OS-0418 reclassificada (água → fertirrigação)',op='Fertirrigação · ureia',
        prod=('Ureia 45 % 12 kg/ha',[Pt.txt('Ureia 45 % 12 kg/ha'),Pt.br(),Pt.mut('janela: esta semana')]),jan='esta semana',fonte='protocolo do plano técnico',
        sit=[Pt.chip('Submetida','yellow'),Pt.br(),Pt.mut('aguarda agrônomo')],acao=[Pt.cta('Revisar v2','IN-02det.dc.html')]),
      R('REC-015',ro=True,id=[Pt.b('REC-015'),Pt.mut('v1')],parc='P1 · Feijão',orig=[Pt.txt('DIA-009 (VIS-013)')],op='Inseticida · mosca-branca',
        prod=('a definir após laudo',[Pt.txt('a definir após laudo'),Pt.br(),Pt.mut('janela: —')]),jan='—',fonte='— · pendente',
        sit=[Pt.chip('Bloqueada','red'),Pt.br(),Pt.mut('laudo foliar inconsistente')],acao=[Pt.cta('Corrigir laudo','AG-02.dc.html',u=True)]),
      R('REC-018',id=[Pt.b('REC-018'),Pt.mut('rascunho')],parc='T2 · Soja',orig='PLA-104 · coleta do T2 em 26/09',op='Calagem · saturação por bases',
        prod=('Calcário PRNT 80 · dose por zona',[Pt.txt('Calcário PRNT 80 · dose por zona'),Pt.br(),Pt.mut('janela: pré-plantio · até 20/10')]),dose='',jan='pré-plantio · até 20/10',fonte='CQFS-RS/SC',
        sit=[Pt.chip('Rascunho','gray'),Pt.br(),Pt.mut('aguarda laudo do T2')],acao=[]),
    ]
    g4=grid(c4,rows4,edit=dict(m='form',title='Recomendação',
             sub='Edite o rascunho; o cálculo sugere a dose e registra a memória. Recomendação submetida ou aprovada fica em consulta: alterar cria nova versão só para o saldo.',
             fields=[F('op','Operação · alvo','sel',opts=['Calagem · saturação por bases','Gessagem','Plantio · nematoide + K','Pulverização · ferrugem asiática','Inseticida · mosca-branca','Fertirrigação · ureia'],req=True),
                     F('parc','Parcela','sel',opts=PARC,req=True),F('prod','Produto · dose','txt',req=True),
                     F('dose','Dose informada','num',min=0,max=10,u='t/ha',help='Sugerida 2,1 t/ha (aguarda laudo); o desvio fica registrado.'),
                     F('jan','Janela','txt',req=True),F('fonte','Fonte','sel',opts=['CQFS-RS/SC','IAC Boletim 100','Embrapa Cerrados','CFSEMG 5ª aproximação'],req=True)]),
             gid='g_rec',total=False)
    EXTRAJS[0]='''
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{ if(gid!=='g_rec') return; r.p.prod=[{k:'txt',t:r.v.prod},{k:'br'},{k:'mut',t:'janela: '+(r.v.jan||'—')}]; r.s.prod=r.v.prod+' '+(r.v.jan||''); }; }'''
    corpo=bloco('Recomendações por origem e destino','Siga a origem de cada recomendação e decida as pendentes; aprovar gera uma única necessidade no planejamento.',g4,
        ilink('Ver demanda gerada','PL-02.dc.html','layers','Abrir as necessidades geradas no planejamento'))
    HEIGHTS37[fname]=760
    shell37('AG-04','Recomendações',corpo,fname=fname,
      subtitle='Origem, produto, dose, janela, fonte e aprovador; o detalhe traz cálculo, prescrição, versões e execução.',
      status=('2 aguardam decisão · 1 bloqueada','yellow'),
      footer='Submeter congela a versão; alteração pós-aprovação cria versão só para o saldo futuro; dose fixa em vez de taxa variável é opção técnica.')

    # ---- AG-04det · REC-014 (elo 3 + decisão da v3 do saldo · DEMO-14) ----
    fname='AG-04det.dc.html'; E._reset_screen(fname)
    cver=[dict(k='ver',l='Versão'),dict(k='mud',l='O que muda',w=320),dict(k='alc',l='Alcance',w=200),dict(k='sit',l='Situação',w=210),dict(k='data',l='Quando',t='date')]
    gver=grid(cver,[
        R('v1',ver='v1',mud='KCl 100 kg/ha em dose única',alc='—',sit=[Pt.chip('Substituída','gray')],data='2026-09-18'),
        R('v2',ver='v2',mud='Dose por zona (140/120/95 kg/ha) + TS nematicida',alc=f'{REAL20} ha realizados na OS-0420',sit=[Pt.chip('Aprovada · em uso','green')],data='2026-09-21'),
        R('v3',ver='v3 (proposta)',mud='KCl −12 % → 105,6 kg/ha (zonas 123/106/84)',alc=f'só o saldo de {SALDO20} ha',sit=[Pt.chip('Aguardando decisão','yellow')],data='2026-09-23'),
      ],edit=consulta(cver,'Versão da recomendação','Histórico de versões: o realizado nunca muda; a proposta vale só para o saldo.'),search=False,gid='g_ver',total=False)
    cit=[dict(k='prod',l='Produto',w=200),dict(k='un',l='Unidade'),dict(k='sug',l='Dose sugerida',a='r'),dict(k='inf',l='Dose informada',a='r'),dict(k='desv',l='Desvio',a='r'),dict(k='fonte',l='Fonte',w=280)]
    git=grid(cit,[
        R('i1',prod='KCl 60 %',un='kg/ha',sug='118',inf=[Pt.b('120')],desv='+1,7 %',fonte='IAC Boletim 100 · K trocável 0,08 cmolc/dm³'),
        R('i2',prod='TS nematicida (abamectina)',un='mL/100 kg sem.',sug='100',inf=[Pt.b('100')],desv='0 %',fonte='bula AGROFIT · reboleiras da VIS-011'),
        R('i3',prod='Semente 58 W (resistente)',un='kg/ha',sug='52',inf=[Pt.b('52')],desv='0 %',fonte='plano Soja alta tecnologia · decisão do DIA-007'),
      ],edit=consulta(cit,'Item da recomendação','Versão aprovada: altere por nova versão, que vale só para o saldo.'),search=False,gid='g_it',total=False)
    cz=[dict(k='zona',l='Zona'),dict(k='area',l='Área',t='num',a='r',u='ha',agg='sum'),dict(k='k',l='K trocável'),dict(k='dose',l='KCl 60 % (v2)',t='num',a='r',u='kg/ha'),dict(k='v3',l='Saldo na v3',t='num',a='r',d=1,u='kg/ha')]
    gz=grid(cz,[
        R('z1',zona='Z1 (reboleiras)',area=62,k='0,05 cmolc/dm³',dose=140,v3=123.2,o=[('LAU-2043 · zona 1 · K 0,05 cmolc/dm³','AG-02.dc.html'),('IAC Boletim 100 · classe muito baixa → 140 kg/ha',None),('v3: 140 × 0,88 = 123,2 kg/ha',None)]),
        R('z2',zona='Z2',area=98,k='0,08 cmolc/dm³',dose=120,v3=105.6,o=[('LAU-2043 · zona 2 · K 0,08 cmolc/dm³','AG-02.dc.html'),('IAC Boletim 100 · classe baixa → 120 kg/ha',None),('v3: 120 × 0,88 = 105,6 kg/ha',None)]),
        R('z3',zona='Z3',area=44,k='0,12 cmolc/dm³',dose=95,v3=83.6,o=[('LAU-2043 · zona 3 · K 0,12 cmolc/dm³','AG-02.dc.html'),('IAC Boletim 100 · classe média → 95 kg/ha',None),('v3: 95 × 0,88 = 83,6 kg/ha',None)]),
      ],edit=dict(m='origin',title='Dose da zona',sub='Dose calculada: confira a origem; para mudar, crie nova versão.',fields=[F('zona','Zona',ro=True),F('dose','KCl 60 % (v2)',ro=True,u='kg/ha'),F('v3','Saldo na v3',ro=True,u='kg/ha')]),
      search=False,gid='g_zon',total=True)
    cex=[dict(k='reg',l='Registro'),dict(k='oque',l='O que é',w=300),dict(k='sit',l='Situação',w=300)]
    gex=grid(cex,[
        R('nec',reg=[Pt.link('NEC-028','PL-02.dc.html')],oque='Necessidade de plantio do T4 · 204 ha · 1ª onda de 100 ha',sit=[Pt.chip('Programada','green')]),
        R('os',reg=[Pt.link('OS-0420',DET0420)],oque=f'{OS20["tipo"]} · {REAL20}/{AREA20} ha · saldo {SALDO20} ha',
          sit=[Pt.chip('Em execução','green'),Pt.chip('Impedida · OM-0233','red'),Pt.chip('v3 em revisão · saldo pausado','yellow')]),
      ],edit=consulta(cex,'Registro vinculado','Destino da recomendação: demanda única, sem duplicar; abra o registro pelo link.'),search=False,gid='g_exe',total=False)
    CUSTO=[('c1','Semente de soja 58 W','REQ-036','SU-07.dc.html','1.560 kg × R$ 9,50',1560*9.5,'Definitivo','green'),
           ('c2','KCl 60 %','REQ-037','SU-07.dc.html','3.600 kg × R$ 2,40',3600*2.4,'Definitivo','green'),
           ('c3','Máquina e equipe · plantio','Apontamentos dias 1 e 2','CA-02.dc.html','6,0 h × R$ 396,00',6*396,'Provisório · 12 ha a conferir','yellow'),
           ('c4','Diesel S10 · Trator T1','Abastecimento','MA-05.dc.html','84 L × R$ 5,92',84*5.92,'Provisório · conciliar tanque','yellow')]
    tot_custo=sum(c[5] for c in CUSTO)
    ccu=[dict(k='item',l='Recurso',w=200),dict(k='orig',l='Origem'),dict(k='qtd',l='Quantidade × preço',w=170),dict(k='custo',l='Custo',t='num',a='r',d=2,pre='R$ ',agg='sum'),dict(k='sit',l='Situação',w=200)]
    gcu=grid(ccu,[R(i,item=it,orig=[Pt.link(o,h)],qtd=q,custo=round(v,2),sit=[Pt.chip(s,c)],o=[(f'{o} · {q}',h),(f'{REAL20} ha realizados na v2 · preservados se a v3 for aprovada',None)])
                  for i,it,o,h,q,v,s,c in CUSTO],
        edit=dict(m='origin',title='Custo realizado',sub='Custo apontado nos hectares já plantados; nenhuma decisão sobre a v3 altera este valor.',
                  fields=[F('item','Recurso',ro=True),F('qtd','Quantidade × preço',ro=True),F('custo','Custo',ro=True,u='R$')]),
        search=False,gid='g_cus',total=True)
    DEC_MSG={
      'aprovada':('v3 aprovada por Ana (RT)',f'Vale só para o saldo de {SALDO20} ha (KCl 105,6 kg/ha; zonas 123/106/84). Os {REAL20} ha realizados ficam na v2 com custo apontado de R$ {nf(tot_custo,2)}. '
                  f'A OS-0420 continua Em execução com o selo Impedida: o saldo de {SALDO20} ha só é liberado depois de revalidar a prontidão (OM-0233 ou Trator 02 substituto).',
                  'Revalidar prontidão no PCP','PL-05.dc.html','green'),
      'devolvida':('v3 devolvida ao PCP com pergunta',f'O saldo de {SALDO20} ha segue pausado e as fichas futuras continuam revogadas. A v2 vale só para os {REAL20} ha realizados até a nova proposta.',
                  'Acompanhar resposta no PCP','PL-05.dc.html','yellow'),
      'rejeitada':('v3 rejeitada por Ana (RT)',f'O saldo de {SALDO20} ha volta para a v2 (KCl 120 kg/ha). O selo de revisão sai da OS-0420; o saldo só é liberado depois de revalidar a prontidão (OM-0233 ou substituto).',
                  'Revalidar prontidão no PCP','PL-05.dc.html','yellow')}
    EXTRAJS[0]='const AGDEC='+json.dumps({k:dict(t=a,x=b,pt=c,ph=d,c=e) for k,(a,b,c,d,e) in DEC_MSG.items()},ensure_ascii=False)+''';
const AGCHIP={aprovada:[{k:'chip',t:'Aprovada · vale para o saldo de 70 ha',c:'green'}],devolvida:[{k:'chip',t:'Devolvida ao PCP',c:'yellow'}],rejeitada:[{k:'chip',t:'Rejeitada',c:'gray'}]};
function PREVALS(self,v){ const d=self.state.dec||'';
  const gv=GRIDS.find(g=>g.id==='g_ver'); const r3=gv.rows.find(r=>r.id==='v3'); const r2=gv.rows.find(r=>r.id==='v2');
  r3.p.sit = d ? AGCHIP[d] : [{k:'chip',t:'Aguardando decisão',c:'yellow'}]; r3.s.sit=r3.p.sit[0].t; r3.v.ver = d==='aprovada' ? 'v3' : 'v3 (proposta)';
  r2.p.sit = d==='aprovada' ? [{k:'chip',t:'Em uso nos 30 ha realizados',c:'green'}] : [{k:'chip',t:'Aprovada · em uso',c:'green'}]; r2.s.sit=r2.p.sit[0].t;
  const ge=GRIDS.find(g=>g.id==='g_exe'); const ro=ge.rows.find(r=>r.id==='os');
  ro.p.sit=[{k:'chip',t:'Em execução',c:'green'},{k:'chip',t:'Impedida · OM-0233',c:'red'}].concat(d==='devolvida'||!d ? [{k:'chip',t:'v3 em revisão · saldo pausado',c:'yellow'}] : [{k:'chip',t:'Saldo aguarda prontidão',c:'yellow'}]);
  ro.s.sit=ro.p.sit.map(x=>x.t).join(' '); }
function EXTRAVALS(self,v){ const d=self.state.dec||''; const ask=self.state.decAsk||'';
  v.dv_pend=!d; v.dv_done=!!d; v.dv_ask_rej=(ask==='rej'); v.dv_ask_dev=(ask==='dev'); v.dv_noask=!d && !ask;
  const m=d?AGDEC[d]:null; v.dv_rt=m?m.t:''; v.dv_rx=m?m.x:''; v.dv_pt=m?m.pt:''; v.dv_ph=m?m.ph:'#';
  v.dv_rst='display: flex; flex-direction: column; gap: 6px; padding: 12px 14px; border-radius: 12px; font-size: 13px; line-height: 1.5; '+(m&&m.c==='green'?'background: #E4F3E9; color: #15201A; border: 1px solid #1E7A4C;':'background: #FFF3D6; color: #15201A; border: 1px solid #8A5A00;');
  const dec=(k,msg)=>{ if(self.state.dec) return; self.setState({dec:k,decAsk:null,g2toast:msg}); };
  v.dv_aprovar=()=>dec('aprovada','v3 aprovada · vale só para o saldo de 70 ha · recibo registrado.');
  v.dv_rej=()=>self.setState({decAsk:'rej'}); v.dv_dev=()=>self.setState({decAsk:'dev'}); v.dv_cancel=()=>self.setState({decAsk:null});
  v.dv_rej_ok=()=>dec('rejeitada','v3 rejeitada · o saldo volta para a v2 · recibo registrado.');
  v.dv_dev_ok=()=>dec('devolvida','v3 devolvida ao PCP · pergunta registrada · saldo segue pausado.'); }'''
    confirm=lambda hole,txt,ok,okfn: (f'<sc-if value="{H(hole)}" hint-placeholder-val="{F_()}"><div role="alert" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.8px; font-weight: 700;">{esc(txt)}'
                                      f'<span style="flex-grow: 1;"></span><button type="button" onClick="{H("dv_cancel")}" style="{_MINI}">Voltar</button><button type="button" onClick="{H(okfn)}" style="{_MINIP}">{esc(ok)}</button></div></sc-if>')
    acoes_dec=(f'<sc-if value="{H("dv_noask")}" hint-placeholder-val="{T_()}"><div style="display: flex; gap: 8px; flex-wrap: wrap;">'
               f'<button type="button" onClick="{H("dv_dev")}" title="Devolver a v3 ao PCP com uma pergunta; o saldo segue pausado" style="{BTN_ST(False,True)} display: inline-flex; align-items: center; gap: 6px;">{icon("clock",14)}Devolver com pergunta</button>'
               f'<button type="button" onClick="{H("dv_rej")}" title="Rejeitar a v3; o saldo volta para a v2" style="{BTN_ST(False,True)} display: inline-flex; align-items: center; gap: 6px; color: {RED};">{icon("alert",14)}Rejeitar v3</button></div></sc-if>')
    recibo=(f'<sc-if value="{H("dv_done")}" hint-placeholder-val="{F_()}"><div role="status" style="{H("dv_rst")}"><b>Recibo · {H("dv_rt")}</b><span>{H("dv_rx")}</span>'
            f'<span><b>Próxima pendência:</b> <a href="{H("dv_ph")}" style="color: {ACC}; font-weight: 700; text-decoration: none;">{H("dv_pt")} ›</a></span></div></sc-if>')
    decisao=(nota(f'A v3 muda só o saldo de <b style="color:{INK};">{SALDO20} ha</b>; os <b style="color:{INK};">{REAL20} ha</b> já plantados ficam na v2. Aprove pelo botão principal, ou devolva ou rejeite aqui.')
             + gver
             + f'<sc-if value="{H("dv_pend")}" hint-placeholder-val="{T_()}">{acoes_dec}'
             + confirm('dv_ask_dev','Devolver a v3 ao PCP com a pergunta "confirmar custo do KCl no saldo"? O saldo segue pausado.','Confirmar devolução','dv_dev_ok')
             + confirm('dv_ask_rej',f'Rejeitar a v3? O saldo de {SALDO20} ha volta para a v2 (KCl 120 kg/ha).','Confirmar rejeição','dv_rej_ok')
             + '</sc-if>' + recibo)
    memoria=(f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.7; background: {BG}; border: 1px solid {LINE}; border-radius: 12px; padding: 12px 14px;">'
             f'K trocável 0,08 cmolc/dm³ ({LAUDOS[0]} · Mehlich-1 · 0–20 cm) · CTC 9,2 → participação de K 0,9 % (alvo 3 %)<br>'
             f'IAC Boletim 100 · soja &gt; 3 t/ha esperadas → <b style="color:{INK};">70 kg/ha de K₂O</b> na base ≈ 118 kg/ha de KCl 60 %<br>'
             f'Informado 120 kg/ha (arredondamento do regulador da plantadeira) · desvio +1,7 % registrado</div>')
    corpo=(
      cadeia('REC-014','Revalidar prontidão no PCP (depois de decidir a v3)','PL-05.dc.html')
      + bloco('Versões e decisão da v3','Decida a proposta para o saldo; o realizado nunca muda.',decisao,tone='yellow')
      + bloco('Contexto da versão aprovada','Confira origem, janela, fonte e destino da v2.',
          _kv([('Origem','<a href="AG-03det.dc.html" style="color: '+ACC+'; font-weight: 700; text-decoration: none;">DIA-007 ›</a> nematoide + K baixo'),('Ciclo · parcela','Safra 2026/27 · T4 · 204 ha'),
               ('Operação','Plantio'),('Janela','20/09 a 05/10'),('Fonte científica','IAC Boletim 100'),('Aprovador (RT)','Ana'),('Aprovada em','21/09/2026'),('Destino','NEC-028 · demanda única')]))
      + bloco('Itens · dose informada × sugerida','Confira a dose que o cálculo sugeriu e a que o agrônomo informou; o desvio fica registrado.',git)
      + bloco('Memória de cálculo','Reproduza o cálculo pela entrada, tabela e resultado.',memoria)
      + bloco('Prescrição espacial por zona','Confira a dose de cada zona e exporte para o terminal; dose fixa é opção técnica, não aprovação adicional.',gz,
          imsg('Gerar prescrição','Prescrição por zona (3 zonas do T4) validada: terminal da plantadeira, unidade kg/ha, coordenadas SIRGAS 2000 e versão v2 conferidos · pronta para exportar.',
               'map','Validar terminal, unidade, coordenadas e versão e gerar o arquivo da prescrição'))
      + bloco('Execução vinculada','Abra a necessidade e a ordem geradas por esta recomendação.',gex)
      + bloco(f'Custo realizado dos {REAL20} ha','Confira o custo apontado nos hectares já plantados; clique na linha para ver a origem.',gcu))
    prim=(f'<sc-if value="{H("dv_pend")}" hint-placeholder-val="{T_()}"><button type="button" onClick="{H("dv_aprovar")}" title="Aprovar a v3 só para o saldo de {SALDO20} ha" style="{BTN_ST(True)} display: inline-flex; align-items: center; gap: 6px;">{icon("check",15)}Aprovar v3 do saldo</button></sc-if>'
          f'<sc-if value="{H("dv_done")}" hint-placeholder-val="{F_()}"><a href="{H("dv_ph")}" style="{BTN_ST(True)} display: inline-flex; align-items: center; gap: 6px; text-decoration: none;">{icon("calendar",15)}{H("dv_pt")}</a></sc-if>')
    HEIGHTS37[fname]=2640; PARENT37[fname]='AG-04.dc.html'
    shell37('AG-04','Recomendação · REC-014 plantio T4',corpo,fname=fname,crumbs_extra=['REC-014 · v2'],
      subtitle='Origem no DIA-007, memória de cálculo, prescrição por zona e destino na NEC-028 e na OS-0420.',
      status=('Aprovada · OS-0420 impedida','red'),primary_html=prim,
      footer='A instrução da OS-0420 herda produto, dose e janela desta versão; alteração pós-aprovação vale só para o saldo.')

    # ================= AG-05 · Biblioteca agronômica e planos técnicos =================
    fname='AG-05.dc.html'; E._reset_screen(fname)
    c5=[dict(k='id',l='Item · tipo',w=170),dict(k='esc',l='Escopo (cultura · região · fase)',w=130),dict(k='ref',l='Referência',w=120),dict(k='gat',l='Unidade · gatilhos',w=120),
        dict(k='val',l='Validade · revisão',w=110),dict(k='apr',l='Aprovador técnico',w=80),dict(k='sit',l='Situação',w=110),dict(k='acao',l='Ação')]
    rows5=[
      R('soja',ro=True,id=[Pt.b('Soja alta tecnologia v6'),Pt.br(),Pt.tag('plano-modelo')],tipo='plano-modelo',esc='Soja · Cerrado · fases 1–5',ref='Embrapa + histórico próprio',gat='DAP por atividade',
        val='safra 26/27 · rev. 08/26',apr='Ana (RT)',sit=[Pt.chip('Publicado','green')],acao=[Pt.cta('Simular','PL-02.dc.html')]),
      R('mip',ro=True,id=[Pt.b('MIP Soja v4'),Pt.br(),Pt.tag('protocolo')],tipo='protocolo',esc='Soja · Cerrado · V4–R6',ref='Embrapa Cerrados',gat='NC por alvo · pano-de-batida',
        val='safra 26/27 · rev. 07/26',apr='Ana (RT)',sit=[Pt.chip('Publicado','green')],
        acao=[Pt.act('Comparar','v3 → v4: NC do percevejo mantido; incluído nematoide-de-cisto com NC 15 cistos/200 cm³ · diferenças listadas por adoção; ajustes locais intactos.')]),
      R('iac',ro=True,id=[Pt.b('IAC Boletim 100 · K e P'),Pt.br(),Pt.tag('tabela')],tipo='tabela',esc='Soja · Sudeste/Cerrado',ref='IAC · edição 100',gat='kg/ha por classe de teor',
        val='indeterminada · conferida 09/26',apr='Ana (RT)',sit=[Pt.chip('Vigente','green')],acao=[Pt.cta('Ver uso','AG-04det.dc.html')]),
      R('feij',id=[Pt.b('Feijão pivô v3'),Pt.br(),Pt.tag('plano-modelo')],tipo='plano-modelo',esc='Feijão · pivô · fases 1–5',ref='CQFS + histórico',gat='DAP + lâmina por fase',
        val='proposta · rev. 09/26',apr='—',sit=[Pt.chip('Em validação','yellow')],
        acao=[Pt.act('Validar','Checagem: fonte ok, escopo ok, unidades ok · v3 apta a publicar; a publicação não reescreve os planos em execução.')]),
      R('lim',id=[Pt.b('Limiar mosca-branca em café'),Pt.br(),Pt.tag('protocolo')],tipo='protocolo',esc='Café · —',ref='sem fonte anexada',gat='—',val='—',apr='—',
        sit=[Pt.chip('Inativo','red'),Pt.br(),Pt.mut('sem fonte validada')],acao=[Pt.mut('anexe a fonte na linha')]),
      R('mam',ro=True,id=[Pt.b('Mamão Formosa v3'),Pt.br(),Pt.tag('plano perene')],tipo='plano perene',esc='Mamão · irrigado (gotejo) · produção',ref='histórico próprio + Ceasa',gat='idade, fenologia e eventos',
        val='contínua · rev. 06/26',apr='Ana (RT)',sit=[Pt.chip('Publicado','green')],acao=[Pt.cta('Simular','PL-02.dc.html')]),
    ]
    g5=grid(c5,rows5,edit=dict(m='form',title='Item da biblioteca',newTitle='Criar versão',
             sub='Crie ou ajuste a versão em rascunho; publicar mostra as diferenças para cada adoção e nunca reescreve planos em execução. Item publicado fica em consulta.',
             fields=[F('tipo','Tipo','sel',opts=['plano-modelo','protocolo','tabela','plano perene'],req=True,def_='plano-modelo'),
                     F('esc','Escopo (cultura · região · fase)','txt',req=True,help='Ex.: Soja · Cerrado · fases 1–5'),F('ref','Referência','txt',req=True),
                     F('gat','Unidade · gatilhos','txt',req=True),F('val','Validade · revisão','txt',req=True),F('apr','Aprovador técnico','sel',opts=['—','Ana (RT)'],def_='—')]),
             add='Criar versão',gid='g_bib',total=False)
    EXTRAJS[0]='''
function EXTRAVALS(self,v){ self.g2after=(gid,rows,r)=>{ if(gid!=='g_bib') return;
  if(String(r.id).indexOf('n')===0 && !r.v.id){ const n=rows.filter(x=>String(x.id).indexOf('n')===0).length; const nm='Nova versão '+n+' · rascunho';
    r.v.id=nm; r.s.id=nm; r.p.id=[{k:'b',t:nm},{k:'br'},{k:'tag',t:r.v.tipo}]; r.p.sit=[{k:'chip',t:'Rascunho',c:'gray'}]; r.s.sit='Rascunho'; r.p.acao=[{k:'mut',t:'valide antes de publicar'}]; r.s.acao='';
    self.setState({g2toast:'Versão criada em rascunho · a publicação não reescreve planos em execução.'}); return; }
  if(r.id==='lim' && r.v.ref && r.v.ref!=='sem fonte anexada'){ r.p.sit=[{k:'chip',t:'Em validação',c:'yellow'},{k:'br'},{k:'mut',t:'segue inativo até validar'}]; r.s.sit='Em validação'; r.p.acao=[{k:'mut',t:'aguarda validação técnica'}]; r.s.acao='';
    self.setState({g2toast:'Referência anexada · limiar em validação técnica (segue inativo até validar).'}); } }; }'''
    corpo=bloco('Biblioteca por cultura, região e fase','Mantenha modelos, tabelas e protocolos versionados; clique na linha para ajustar um rascunho ou anexar a referência.',g5,
        idrawer('Importar referência',dict(title='Importar referência',sub='Tabela ou boletim com fonte e escopo; sem isso o limiar fica inativo.',
           fields=[('Tabela','IAC Boletim 100'),('Escopo (cultura · região)','Soja · Sudeste'),('Arquivo (PDF)',''),('Validade','indeterminada')],
           confirm='Importar referência',done='Referência importada · aguardando validação técnica'),'doc','Importar tabela ou boletim com fonte e escopo')
        + imsg('Publicar','Nada a publicar ainda: o Feijão pivô v3 está em validação. Depois de validado, publicar envia as diferenças às 4 adoções ativas, preserva ajustes locais e não muda planos em execução.',
               'layers','Publicar a versão validada para as adoções'))
    HEIGHTS37[fname]=840
    shell37('AG-05','Biblioteca e planos técnicos',corpo,fname=fname,
      subtitle='Operações técnicas por cultura, região e fase; o modelo é versionado e alterar mostra diferenças para cada adoção.',
      status=('1 em validação · 1 inativo','yellow'),
      footer='Modelo publicado não reescreve planos em execução; limiar sem fonte e escopo validados fica inativo; ajustes locais não são apagados.')

    # ================= AG-06 · Eficácia e histórico =================
    fname='AG-06.dc.html'; E._reset_screen(fname)
    c6=[dict(k='id',l='Avaliação'),dict(k='rec',l='Recomendação → execução',w=170),dict(k='met',l='Método pré/pós',w=130),dict(k='datas',l='Datas',w=130),
        dict(k='res',l='Resultado',w=150),dict(k='conf',l='Confiança',chips={'Alta':'green','Média':'yellow','Baixa':'yellow'}),
        dict(k='custo',l='Custo',t='num',a='r'),dict(k='acao',l='Ação')]
    rs=lambda n:(n,[Pt.txt(f'R$ {n}/ha')])
    rows6=[
      R('EF-021',id=[Pt.b('EF-021')],rec=[Pt.link('REC-016','AG-04.dc.html'),Pt.txt('→'),Pt.link('OS-0421','CA-01det.dc.html'),Pt.br(),Pt.mut('fungicida T1+T2')],
        met='% folíolos com ferrugem',datas='pré 19/09 · pós 27/09 (7 DAA)',res=[Pt.chip('Pós em 27/09','yellow')],conf='—',custo=rs(96),acao=[Pt.cta('Programar pós','AG-01.dc.html')]),
      R('EF-020',id=[Pt.b('EF-020')],rec=[Pt.link('REC-014','AG-04det.dc.html'),Pt.txt('→'),Pt.link('OS-0420',DET0420),Pt.br(),Pt.mut('plantio T4')],
        met='cistos/200 cm³ (pré = VIS-011)',datas='pré 15/09 · pós em V4',res=[Pt.chip('Sem leitura pós','red'),Pt.br(),Pt.mut('O.S. impedida')],conf='—',custo=rs(328),acao=[Pt.cta('Ver O.S.',DET0420)]),
      R('EF-019',ro=True,id=[Pt.b('EF-019')],rec=[Pt.txt('REC-012 →'),Pt.link('OS-0415','CA-01.dc.html'),Pt.br(),Pt.mut('dessecação T3')],
        met='% cobertura verde',datas='pré 08/09 · pós 22/09',res=[Pt.chip('Controle 96 %','green')],conf='Alta',custo=rs(82),acao=[Pt.cta('Abrir aplicação','CA-01.dc.html')]),
      R('EF-018',id=[Pt.b('EF-018')],rec=[Pt.txt('REC-011 → inseticida P2')],met='lagartas/m',datas='pré 02/09 · pós 16/09',
        res=[Pt.chip('Redução 62 %','yellow'),Pt.br(),Pt.mut('observada · chuva de 48 mm')],conf='Baixa',custo=rs(54),
        acao=[Pt.act('Registrar parecer','Parecer registrado: redução observada não atribuída ao produto (chuva de 48 mm entre pré e pós) · o caso entra no histórico sem crédito de eficácia causal.')]),
      R('EF-017',ro=True,id=[Pt.b('EF-017')],rec=[Pt.txt('REC-009 → herbicida T2')],met='plantas/m²',datas='pré 10/08 · pós 24/08 · recorrência 05/09',
        res=[Pt.chip('Recorreu','red'),Pt.br(),Pt.mut('alvo voltou em 12 dias')],conf='Alta',custo=rs(61),acao=[Pt.cta('Propor revisão','AG-05.dc.html',u=True)]),
    ]
    for r in rows6:
        if r['v'].get('conf') in ('Alta','Baixa'):
            r['p']['conf']=[Pt.chip(r['v']['conf'],'green' if r['v']['conf']=='Alta' else 'yellow')]
    g6=grid(c6,rows6,edit=dict(m='form',title='Avaliação de eficácia',
             sub='Compare a leitura pós com a pré no mesmo método e unidade; redução observada não é eficácia causal. Avaliação concluída fica em consulta.',
             fields=[F('met','Método pré/pós','txt',req=True),F('datas','Datas','txt',req=True,help='Ex.: pré 19/09 · pós 27/09 (7 DAA)'),
                     F('conf','Confiança','sel',opts=['—','Alta','Média','Baixa'],req=True),F('parecer','Parecer técnico','area')]),
             gid='g_ef',total=False)
    c6b=[dict(k='tipo',l='Economia'),dict(k='val',l='Valor',t='num',a='r',pre='R$ ',u='mil',agg='sum'),dict(k='oque',l='O que entra',w=420),dict(k='sit',l='Situação',w=190)]
    g6b=grid(c6b,[
        R('ev',tipo=[Pt.b('Efetivamente evitada')],val=41,oque='2 aplicações dispensadas por contagem abaixo do NC confirmada no ciclo (P2 e T3)',sit=[Pt.chip('Janela do alvo encerrada','green')],
          o=[('P2 · Milho · inseticida para lagarta dispensado (VIS-012 e VIS-015 abaixo do NC) · R$ 25 mil','AG-01.dc.html'),('T3 · aplicação dispensada · contagem abaixo do NC · R$ 16 mil',None)]),
        R('ad',tipo=[Pt.b('Adiada')],val=18,oque='1 aplicação no C1 aguardando nova contagem de bicho-mineiro em 02/10',sit=[Pt.chip('Pode voltar como custo','yellow')],
          o=[('C1 · Café · inseticida para bicho-mineiro adiado até a contagem de 02/10 · R$ 18 mil',None)]),
      ],edit=dict(m='origin',title='Economia estimada',sub='Estimativa a custo orçado; adiar não é evitar.',fields=[F('oque','O que entra',ro=True),F('sit','Situação',ro=True)]),
      search=False,gid='g_eco',total=False)
    corpo=(
      bloco('Intervenção × observação posterior','Compare a recomendação executada com a leitura pós e registre o parecer; clique na linha para completar a avaliação.',g6,
          ilink('Abrir aplicações','CA-01.dc.html','lista','Abrir as ordens de campo executadas')
          + ilink('Propor melhoria','GE-07.dc.html','trend','Levar um desvio recorrente para melhoria contínua'))
      + bloco('Economia adiada × efetivamente evitada','Separe o que foi evitado do que só foi adiado; clique na linha para ver a origem.',g6b))
    HEIGHTS37[fname]=900
    shell37('AG-06','Eficácia e histórico',corpo,fname=fname,
      subtitle='Intervenções comparadas com observações posteriores: desvio, recorrência, confiança e custo por hectare.',
      status=('1 pós vence em 27/09','yellow'),
      primary_html=ilink('Programar avaliação','AG-01.dc.html','calendar','Programar a vistoria de leitura pós',primary=True,small=False),
      footer='Redução observada não equivale a eficácia causal; a EF-020 fecha a cadeia da demonstração quando a OS-0420 tiver leitura pós.')

    # ================= AG-07 · Bulas e registros (AGROFIT) =================
    fname='AG-07.dc.html'; E._reset_screen(fname)
    c7=[dict(k='prod',l='Produto · ingrediente',w=170),dict(k='reg',l='Registro MAPA · situação',w=150),dict(k='moa',l='Modo de ação',w=130),dict(k='alvo',l='Cultura · alvo',w=130),
        dict(k='dose',l='Dose · formulação',w=120),dict(k='car',l='Carência · reentrada · aplic. máx.',w=120),dict(k='acao',l='Ação')]
    rows7=[
      R('fa',prod=[Pt.b('Fungicida A'),Pt.br(),Pt.mut('protioconazol + trifloxistrobina')],reg=[Pt.txt('8412'),Pt.br(),Pt.chip('Vigente','green')],moa='Triazol + estrobilurina (G1+C3)',
        alvo='Soja · ferrugem asiática',dose=[Pt.txt('0,4 L/ha'),Pt.br(),Pt.mut('SC')],car=[Pt.txt('30 d · 24 h'),Pt.br(),Pt.mut('máx. 2/safra')],acao=[Pt.cta('Recomendar','AG-04.dc.html')]),
      R('ts',prod=[Pt.b('TS Nemat'),Pt.br(),Pt.mut('abamectina')],reg=[Pt.txt('11207'),Pt.br(),Pt.chip('Vigente','green')],moa='Avermectina (6)',
        alvo='Soja · nematoide-de-cisto',dose=[Pt.txt('100 mL/100 kg sem.'),Pt.br(),Pt.mut('TS')],car=[Pt.txt('— · 24 h'),Pt.br(),Pt.mut('máx. 1/safra (TS)')],acao=[Pt.cta('Ver na REC-014','AG-04det.dc.html')]),
      R('ib',prod=[Pt.b('Inseticida B'),Pt.br(),Pt.mut('acefato')],reg=[Pt.txt('6120'),Pt.br(),Pt.chip('Vigente','green')],moa='Organofosforado (1B)',
        alvo='Feijão · mosca-branca',dose=[Pt.txt('1,0 kg/ha'),Pt.br(),Pt.mut('SP')],car=[Pt.txt('14 d · 24 h'),Pt.br(),Pt.mut('máx. 2/ciclo')],
        acao=[Pt.act('Comparar','Comparação: Inseticida B × outro produto registrado para mosca-branca no feijão — dose, carência, modo de ação e nº de aplicações lado a lado; equivalência exige decisão técnica.')]),
      R('hc',prod=[Pt.b('Herbicida C'),Pt.br(),Pt.mut('glifosato 480')],reg=[Pt.txt('3327'),Pt.br(),Pt.chip('Em reavaliação','yellow')],moa='EPSPS (G9)',
        alvo='Soja · daninhas folha larga',dose=[Pt.txt('2,0 L/ha'),Pt.br(),Pt.mut('SL')],car=[Pt.txt('— · 6 h'),Pt.br(),Pt.mut('máx. 2/safra')],
        acao=[Pt.act('Ver bula','Bula oficial aberta (PDF do AGROFIT) · situação: em reavaliação — uso permitido conforme o rótulo vigente; alerta anexado ao receituário.')]),
      R('pe',prod=[Pt.b('Produto E'),Pt.br(),Pt.mut('protioconazol + trifloxistrobina')],reg=[Pt.txt('9834'),Pt.br(),Pt.chip('Vigente','green')],moa='Triazol + estrobilurina (G1+C3)',
        alvo='Soja · ferrugem asiática',dose=[Pt.txt('0,5 L/ha'),Pt.br(),Pt.mut('EC')],car=[Pt.txt('30 d · 24 h'),Pt.br(),Pt.mut('máx. 2/safra')],
        acao=[Pt.act('Comparar','Mesmo ingrediente, mas NÃO é substituto automático: formulação (EC × SC) e dose (0,5 × 0,4 L/ha) diferem · a troca exige nova validação técnica na recomendação.')]),
      R('if',prod=[Pt.b('Inseticida F'),Pt.br(),Pt.mut('paration metílico')],reg=[Pt.txt('2201'),Pt.br(),Pt.chip('Registro cancelado','red')],moa='Organofosforado (1B)',
        alvo='—',dose=[Pt.txt('—'),Pt.br(),Pt.mut('EC')],car=[Pt.txt('—'),Pt.br(),Pt.mut('máx. —')],acao=[Pt.chip('Uso bloqueado','red')]),
    ]
    g7=grid(c7,rows7,edit=consulta(c7,'Ficha oficial',f'Dados do AGROFIT (consulta de 20/09, cache de 3 dias): consulta apenas; a situação é conferida de novo no uso.',skip=('acao',)),
            gid='g_bula',total=False)
    corpo=(
      kpis([('PRODUTOS NA BASE','412','sincronizados do AGROFIT'),('REGISTROS VIGENTES','396','situação conferida no uso'),
            ('EM REAVALIAÇÃO','14','uso permitido com alerta'),('CACHE','3 dias','consulta 20/09 · vigente')])
      + bloco('Produtos por ingrediente, cultura e alvo','Busque e filtre pelas colunas; clique na linha para abrir a ficha oficial.',g7,
          imsg('Atualizar fonte','Base AGROFIT reconsultada agora · 2 fichas mudaram de situação (1 em reavaliação, 1 cancelada) · idade do cache zerada.','clock','Reconsultar o AGROFIT e zerar a idade do cache')))
    prim=idrawer('Preparar receituário',dict(title='Preparar receituário agronômico',sub='Documento técnico específico da aplicação, com identificação e assinatura do RT.',
           fields=[('Produto','Fungicida A · protioconazol + trifloxistrobina'),('Cultura','Soja'),('Alvo','Ferrugem asiática'),('Talhão','T1 · 312 ha'),('Dose','0,4 L/ha'),('Responsável técnico','Ana'),('Recomendação vinculada','REC-016')],
           confirm='Emitir receituário',done='Receituário emitido · assinado pelo RT · anexado à recomendação'),'doc','Preparar o receituário da aplicação com assinatura do RT',primary=True,small=False)
    HEIGHTS37[fname]=900
    shell37('AG-07','Bulas e registros',corpo,fname=fname,
      subtitle='Base AGROFIT por produto, ingrediente, modo de ação, cultura e alvo: ficha oficial, restrições e situação do registro.',
      status=('14 em reavaliação','yellow'),primary_html=prim,
      footer='Produto equivalente por ingrediente não é substituto automático; o uso nasce de um diagnóstico e de uma recomendação aprovada.')
