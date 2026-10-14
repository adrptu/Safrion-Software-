# -*- coding: utf-8 -*-
"""Área Agronomia — no menu: AG-01 Pragas e doenças (MIP/MID) e AG-07 Consulta Agrofit (Agrícola). Ligados ao item Pragas e doenças:
AG-01det Rota e evidências (#VIS-xxx) · AG-03 Diagnósticos (+ AG-03det DIA-007) · AG-04 Recomendações (+ AG-04det REC-014).
AG-02 Análises de solo (menu Agrícola) em areas/analise_solo.py. Módulos ocultos, preservados: AG-05 Biblioteca e planos técnicos · AG-06 Eficácia e histórico.

Pragas e doenças (02/10/2026, pedido do proprietário: autoanálise do MIP/MID): UMA base para o Mapa, o AG-01, o AG-01det, o AG-03/AG-04
e o app (MB-06) — dados_mip.py (protocolos, talhões das duas fazendas, vistorias VIS-006…017 e VIS-051…060, DIA/REC, aplicações) +
mip.js (estado 'talhao-os-mip-v1', resultado contagem × NC, próximo passo, conferência do receituário, O.S. no cenário). AG-01 é lista →
painel da vistoria (#VIS-xxx) → sub-detalhe AG-01det; decidir controle mostra só produtos registrados para cultura × alvo (agrofit_dados,
só leitura) com travas legais (registro, cancelado, dose, nº de aplicações, carência × colheita) e alertas (rotação, reavaliação, estoque,
uso não conferido, coleta incompleta); emitir grava DIA + REC/RA + O.S. em A liberar (OS-0440 em diante; Ana libera na O.S.).
Laudo de solo ou folha não bloqueia o controle de pragas (DIA-009/REC-015 deixaram de ser "bloqueados"). A v3 da REC-014 já vale no saldo
(igual ao Mapa e à O.S.); o TS da REC-014 não tem registro para nematoide-de-cisto: alerta com a ficha e a alternativa (AG-07).

observacoes (dados locais coerentes com dados.py / dados2.py / campo.py / gestao.py):
- OS-0420 = dados.OS: 100 ha, 30 realizados (18 conf. + 12 prov.), saldo 70 ha, impedida por OM-0233.
- REC-014 v2 (30 ha realizados): KCl por zona 140/120/95 kg/ha, TS nematicida 100 mL/100 kg sem., semente 58 W 52 kg/ha; v3 aprovada por Ana
  em 23/09 só no saldo de 70 ha (KCl −12 %: 123/106/84 kg/ha).
- Custo apontado dos 30 ha (igual a gestao.py GE-03): R$ 26.333,28.
- VIS-011: 14 pontos, ponto 11 em recoleta (GPS ±42 m); média válida 13,0 cistos/200 cm³ (NC 15) com reboleiras 04/07/10 → foco.
- Novos registros: VIS-018, DIA-011, REC-019, RA-0142 e PLA-106 em diante.
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
PARC=['T4 · Soja 58 W','T2 · Soja','T1 · Soja','P1 · Feijão','P2 · Milho','C1 · Café (ano-safra)','T7 · Mamão Formosa']

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
            + (f'<div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div>' if desc else '') + '</div>'
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
CADEIA=[('Vistoria','VIS-011','AG-01.dc.html#VIS-011','Foco · reboleiras'),
        ('Diagnóstico','DIA-007','AG-03det.dc.html','Decisão registrada'),
        ('Recomendação','REC-014 v2','AG-04det.dc.html','TS sem registro · saldo travado'),
        ('Necessidade','NEC-028','PL-02.dc.html','Programada · 1ª onda 100 ha'),
        ('O.S.','OS-0420','OS.dc.html#OS-0420',f'Em execução · Impedida · {REAL20}/{AREA20} ha'),
        ('Avaliação','EF-020','AG-06.dc.html','Aguarda leitura pós')]
def cadeia(atual,prox_t,prox_h,vivo=None):
    cells=[]
    for i,(lbl,rid,href,st) in enumerate(CADEIA):
        cur=(rid.split()[0]==atual)
        def _in(seta): return (f'<span style="font-size: 10.5px; font-weight: 700; letter-spacing: .06em; color: {MUTED};">{esc(lbl.upper())}</span>'
               f'<span style="font-size: 13px; font-weight: 800; color: {ACC if seta else INK};">{esc(rid)}{" ›" if seta else ""}</span>'
               f'<span style="font-size: 11.5px; color: {MUTED}; line-height: 1.3;">{esc(st)}</span>')
        box='display: flex; flex-direction: column; gap: 2px; flex: 1 1 0; min-width: 0; padding: 8px 10px; border-radius: 10px; text-decoration: none;'
        lk=f'<a href="{href}" title="Abrir {esc(lbl.lower())} {esc(rid)}" style="{box} background: {SURF}; border: 1px solid {LINE};">{_in(True)}</a>'
        tx=f'<div style="{box} background: {SURF}; border: 1px solid {LINE};">{_in(False)}</div>'
        if cur: cells.append(f'<div aria-current="step" style="{box} background: {SURF}; border: 2px solid {ACC};">{_in(False)}</div>')
        elif prox_h and href==prox_h: cells.append(tx)
        elif vivo and href in vivo: cells.append(f'<sc-if value="{H(vivo[href])}" hint-placeholder-val="{F_()}">{lk}</sc-if><sc-if value="{H(vivo[href]+"Txt")}" hint-placeholder-val="{T_()}">{tx}</sc-if>')
        else: cells.append(lk)
        if i<len(CADEIA)-1: cells.append(f'<span aria-hidden="true" style="color: {MUTED}; align-self: center;">→</span>')
    # sem "Próxima ação" aqui: o primário da tela já nomeia o próximo passo (um destino, um lugar)
    return (f'<nav aria-label="Cadeia da demonstração" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; background: {ACCS}; border: 1px solid {LINE}; border-radius: 12px;">'
            f'<div style="display: flex; align-items: stretch; gap: 6px;">{"".join(cells)}</div></nav>')

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
    ag01(); ag01det()   # Pragas e doenças (MIP/MID): funções próprias, abaixo

    # AG-02 · Análises de solo: areas/analise_solo.py (SOLO-01; menu Agrícola). Os planos de amostragem saíram (D-13): a coleta é operação do plano.

    # ================= AG-03 · Diagnósticos (MIP do estado compartilhado: DIA-007…010 e os novos, DIA-011 em diante) =================
    import cenario, dados_mip as DM
    _menu_mip()
    fname='AG-03.dc.html'; E._reset_screen(fname)
    # a decisão fica na linha de baixo da situação (a grade cabe em 1280 × 800)
    c3=[dict(k='id',l='Diagnóstico',w=90),dict(k='parc',l='Talhão · cultura',w=110),dict(k='evid',l='Evidências',w=140),dict(k='hip',l='Hipótese · causa',w=150),
        dict(k='risco',l='Risco',chips={'alto':'red','médio':'yellow','baixo':'green'}),
        dict(k='sit',l='Situação · decisão',w=150),dict(k='acao',l='Próximo passo',w=160)]
    g3=grid(c3,[],edit=dict(m='form',title='Diagnóstico',newTitle='Criar diagnóstico',
             fields=[F('parc','Talhão · cultura','sel',opts=PARC,req=True,def_='T2 · Soja'),F('evid','Evidências (vistoria · laudo)','txt',req=True,help='Ex.: VIS-017 · LAU-2063'),
                     F('hip','Hipótese · causa','area',req=True),F('meta','Meta','txt',req=True),F('risco','Risco','sel',opts=['baixo','médio','alto'],req=True,def_='médio'),
                     F('acp','Ação proposta','area',req=True),F('resp','Responsável','sel',opts=['Ana','Marcos'],req=True,def_='Ana')]),
             add='Criar diagnóstico',gid='g_dia',total=False)
    EXTRAJS[0]=cenario.js_prefixo()+DM.js_prefixo()+JS_AG01.split('function agRow(')[0]+r'''
const AG3X={'DIA-007':{meta:'plantio na janela 20/09–05/10',evx:'+ LAU-2043/2044'},'DIA-008':{meta:'manter o custo do plano',evx:'abaixo do NC · 08/09'},
  'DIA-009':{meta:'segurar a produtividade no R5',evx:'LAU-2048 (folha) não decide o controle'},'DIA-010':{meta:'proteger a carga pendente',evx:'6 de 12 pontos'}};
const RK={'alto':'red','médio':'yellow','baixo':'green'}; const SC={'Registrada':'green','A decidir':'yellow','Rascunho':'gray'};
function a3Rows(self,v){ const s=mipGet(), c=agC();
  return Object.values(s.dia).sort((a,b)=>(a.id<b.id?-1:1)).map(d=>{ const vv=d.vis?s.vis[d.vis]:null; const t=MIPD.tal[d.tal]||{rot:d.tal||'—',cultura:''}; const x=AG3X[d.id]||{};
    let ac, go=''; const rc=d.rec&&s.rec[d.rec]; const osId=(rc&&rc.os)||((vv&&vv.dec&&vv.dec.dia===d.id&&vv.dec.os)||''); const canc=!!osId&&mipOsFora(c,osId);
    if(d.sit==='A decidir'&&vv){ ac=[{k:'cta',t:'Decidir controle',h:'AG-01.dc.html#'+vv.id+':decidir',u:true}]; go='AG-01.dc.html#'+vv.id; }
    else if(d.id==='DIA-007'){ ac=[{k:'cta',t:'Abrir REC-014',h:'AG-04det.dc.html'}]; go='AG-03det.dc.html'; }
    else if(canc&&vv){ ac=[{k:'cta',t:'Decidir controle',h:'AG-01.dc.html#'+vv.id+':decidir',u:true}]; go='AG-01.dc.html#'+vv.id; }
    else if(osId){ ac=[{k:'cta',t:'Abrir '+osId,h:'OS.dc.html#'+osId}]; go=vv?'AG-01.dc.html#'+vv.id:''; }
    else if(vv){ ac=[{k:'cta',t:'Abrir vistoria',h:'AG-01.dc.html#'+vv.id}]; go='AG-01.dc.html#'+vv.id; }
    else ac=[{k:'mut',t:'complete pela linha'}];
    const dr=go?('a3go_'+d.id):''; if(dr) v[dr]=()=>{ location.href=go; };
    const acp=d.dec||d.acp||(d.sit==='A decidir'?'a decidir':'');
    return Object.assign({id:d.id,ro:d.sit!=='Rascunho',v:{id:d.id,parc:(d.parc||(t.rot+(t.cultura?' · '+t.cultura:''))),evid:d.evid||(vv?vv.id:''),hip:d.hip||'',meta:d.meta||x.meta||'',risco:d.risco||'médio',acp:d.acp||acp,resp:d.por||'Ana'},
      s:{sit:d.sit+' '+(acp||''),acp:acp,evid:(vv?vv.id:(d.evid||''))+' '+(x.evx||'')},
      p:{id:[d.id==='DIA-007'?{k:'link',t:'DIA-007',h:'AG-03det.dc.html'}:{k:'b',t:d.id}],parc:[{k:'txt',t:d.parc||(t.rot+(t.cultura?' · '+t.cultura:''))}],
         evid:vv?[{k:'link',t:vv.id,h:'AG-01.dc.html#'+vv.id}].concat(x.evx?[{k:'br'},{k:'mut',t:x.evx}]:[]):[{k:'txt',t:d.evid||'—'}],
         risco:[{k:'chip',t:d.risco||'médio',c:RK[d.risco||'médio']}],acp:[{k:'txt',t:acp||'—'}],
         sit:[{k:'chip',t:d.sit,c:SC[d.sit]||'gray'}].concat(canc?[{k:'br'},{k:'mut',t:osId+' cancelada · decidir de novo'}]:[{k:'br'},{k:'mut',t:(acp||'—')+(d.em?' · '+mipBr(d.em)+' · '+(d.por||'Ana'):'')}]),acao:ac}},dr?{dr}:{}); }); }
function PREVALS(self,v){ cenOuvir(self); mipOuvir(self); const sp=GRIDS.find(g=>g.id==='g_dia'); sp.rows=a3Rows(self,v); }
function EXTRAVALS(self,v){ const s=mipGet(), c=agC(); const osDe=(d)=>{ const rc=d.rec&&s.rec[d.rec]; const vv=d.vis&&s.vis[d.vis]; return (rc&&rc.os)||((vv&&vv.dec&&vv.dec.dia===d.id&&vv.dec.os)||''); };
  const n=Object.values(s.dia).filter(d=>d.sit==='A decidir'||(d.sit==='Registrada'&&mipOsFora(c,osDe(d)))).length, nr=Object.values(s.dia).filter(d=>d.sit==='Rascunho').length;
  v.a3_st=n?(n+' a decidir'):(nr?nr+' em rascunho':'Em dia'); const cs=agCh(n?'yellow':'green'); v.a3_stst=cs.st; v.a3_stdot=cs.dot;
  // novo diagnóstico (ou rascunho editado): vai para o mesmo estado do MIP, com a numeração única (DIA-011 em diante)
  self.g2after=(gid,rows,r,isNew)=>{ if(gid!=='g_dia') return;
    const r2=mipMudar(self,s=>{ const id=isNew?'DIA-'+String(s.seq.dia++).padStart(3,'0'):r.id; const tal=String(r.v.parc||'').split(' · ')[0];
      s.dia[id]=Object.assign(s.dia[id]||{id,vis:'',tal,sit:'Rascunho',em:MIPD.hoje},{parc:r.v.parc,evid:r.v.evid,hip:r.v.hip,meta:r.v.meta,risco:r.v.risco,acp:r.v.acp,por:r.v.resp});
      return {msg:isNew?(id+' criado em rascunho · a decisão é registrada pelo agrônomo responsável.'):(id+' salvo em rascunho.'),id}; });
    g2set(self,'g_dia',{rows:null,fl:r2.id||null}); }; }
'''
    corpo=bloco('Diagnósticos','',g3)
    HEIGHTS37[fname]=720; PARENT37[fname]='AG-01.dc.html'
    shell37('AG-03','Diagnósticos',corpo,fname=fname,crumbs_extra=['Diagnósticos'],search=False,status=(H('a3_st'),'red'))
    _status_dinamico(fname,'a3')

    # ---- AG-03det · DIA-007 (elo 2 da cadeia) ----
    fname='AG-03det.dc.html'; E._reset_screen(fname)
    cev=[dict(k='reg',l='Evidência'),dict(k='tipo',l='Tipo'),dict(k='data',l='Data',t='date'),dict(k='achado',l='O que mostra',w=380),dict(k='fonte',l='Fonte')]
    gev=grid(cev,[
        R('e1',reg=[Pt.link('VIS-011','AG-01.dc.html#VIS-011')],tipo='Vistoria · trincheira',data='2026-09-15',achado='Média válida 13,0 cistos/200 cm³ (13 pontos; NC 15) com reboleiras nos pontos 04, 07 e 10 (34, 41 e 29) · foco',fonte='MIP Soja v4'),
        R('e2',reg=[Pt.link('LAU-2043','AG-02.dc.html')],tipo='Laudo de solo · 0–20 cm',data='2026-09-12',achado='K trocável 0,08 cmolc/dm³ · CTC 9,2 · participação de K 0,9 % (alvo 3 %)',fonte='Lab Solo Vale · Mehlich-1'),
        R('e3',reg=[Pt.link('LAU-2044','AG-02.dc.html')],tipo='Laudo de solo · 20–40 cm',data='2026-09-12',achado='K trocável 0,06 cmolc/dm³ · sem barreira química',fonte='Lab Solo Vale · Mehlich-1'),
      ],edit=consulta(cev,'Evidência','Evidência vinculada ao diagnóstico; abra o registro de origem pelo link.'),search=False,gid='g_ev',total=False)
    corpo=(
      cadeia('DIA-007','Abrir recomendação REC-014','AG-04det.dc.html')
      + bloco('Decisão técnica','',
          _kv([('Ciclo · talhão','Safra 2026/27 · T4 · 204 ha'),('Cultura · cultivar','Soja · 58 W (resistente)'),('Meta','plantio na janela 20/09–05/10'),('Risco',chip('alto','red')),
               ('Hipótese · causa','Foco de nematoide-de-cisto em reboleiras + K baixo no perfil (0–20 cm)'),('Decisão','Cultivar resistente + TS + K na base (controlar no plantio)'),
               ('Responsável','Ana (RT) · registrada em 17/09'),('Destino','REC-014 v2 · NEC-028')]))
      + bloco('Evidências vinculadas','',gev))
    HEIGHTS37[fname]=900; PARENT37[fname]='AG-03.dc.html'
    shell37('AG-03','Diagnóstico · DIA-007 nematoide T4',corpo,fname=fname,crumbs_extra=['Diagnósticos','DIA-007'],search=False,
      status=('Decisão registrada','green'),
      primary_html=ilink('Abrir recomendação REC-014','AG-04det.dc.html','leaf','Abrir a recomendação que formalizou esta decisão',primary=True,small=False))

    # ================= AG-04 · Recomendações (REC-015 e as do MIP vêm do estado compartilhado) =================
    fname='AG-04.dc.html'; E._reset_screen(fname)
    # talhão na linha de baixo da operação; fonte e RT no detalhe da linha (a grade cabe em 1280 × 800)
    c4=[dict(k='id',l='Recomendação',w=110),dict(k='orig',l='Origem',w=130),dict(k='op',l='Operação · talhão',w=150),
        dict(k='prod',l='Produto · dose · janela',w=170),dict(k='sit',l='Situação',w=160),dict(k='acao',l='Próximo passo')]
    rows4=[
      R('REC-014',ro=True,id=[Pt.link('REC-014','AG-04det.dc.html'),Pt.mut('v2 · v3 no saldo')],parc='T4 · Soja 58 W',orig=[Pt.link('DIA-007','AG-03det.dc.html'),Pt.mut('VIS-011')],
        op='Plantio · nematoide + K',prod=('KCl 60 % por zona + TS nematicida',[Pt.txt('KCl 60 % por zona + TS nematicida'),Pt.br(),Pt.mut('janela: 20/09–05/10')]),jan='20/09–05/10',fonte='IAC Boletim 100 · Ana (RT)',
        sit=[Pt.chip('TS sem registro p/ cisto','red'),Pt.br(),Pt.mut(f'saldo de {SALDO20} ha travado até a v4')],acao=[Pt.cta('Abrir REC-014','AG-04det.dc.html',u=True)]),
      R('REC-016',ro=True,id=[Pt.b('REC-016'),Pt.mut('v1')],parc='T1+T2 · Soja',orig='Protocolo Soja alta tecnologia v6',op='Pulverização · ferrugem asiática',
        prod=('Fungicida A 0,4 L/ha',[Pt.txt('Fungicida A 0,4 L/ha'),Pt.br(),Pt.mut('janela: em execução')]),jan='em execução',fonte='bula AGROFIT · Ana (RT)',
        sit=[Pt.chip('Aprovada','green'),Pt.br(),Pt.mut(f'OS-0421 · {OS21["realizado"]}/{OS21["area"]} ha')],acao=[Pt.cta('Abrir OS-0421','OS.dc.html#OS-0421')]),
      R('REC-017',ro=True,id=[Pt.b('REC-017'),Pt.mut('v2')],parc='P1 · Feijão',orig='OS-0418 reclassificada (água → fertirrigação)',op='Fertirrigação · ureia',
        prod=('Ureia 45 % 12 kg/ha',[Pt.txt('Ureia 45 % 12 kg/ha'),Pt.br(),Pt.mut('janela: esta semana')]),jan='esta semana',fonte='protocolo do plano técnico',
        sit=[Pt.chip('Submetida','yellow'),Pt.br(),Pt.mut('liberação na OS-0418')],acao=[Pt.cta('Liberar OS-0418','OS.dc.html#OS-0418')]),
      # REC-018 (calagem do T2 'aguarda laudo') saiu (SOLO-01, D-14): a calagem do T2 vem do LAU-2063 como sugestão na dose do plano
    ]
    for r_ in rows4:   # operação + talhão (linha de baixo); a versão vai para baixo do número
        r_['p']['op']=[Pt.txt(r_['v']['op']),Pt.br(),Pt.mut(r_['v']['parc'])]; r_['s']['op']=r_['v']['op']+' '+r_['v']['parc']
        if len(r_['p'].get('id',[]))==2: r_['p']['id']=[r_['p']['id'][0],Pt.br(),r_['p']['id'][1]]
    rows4[0]['dr']='a4go_REC-014'
    g4=grid(c4,rows4,edit=dict(m='form',title='Recomendação',
             fields=[F('op','Operação · alvo','sel',opts=['Plantio · nematoide + K','Pulverização · ferrugem asiática','Fertirrigação · ureia'],req=True),
                     F('parc','Talhão','sel',opts=PARC,req=True),F('prod','Produto · dose','txt',req=True),
                     F('jan','Janela','txt',req=True),F('fonte','Fonte','sel',opts=['CQFS-RS/SC','IAC Boletim 100','Embrapa Cerrados','CFSEMG 5ª aproximação'],req=True)]),
             gid='g_rec',total=False)
    EXTRAJS[0]=cenario.js_prefixo()+DM.js_prefixo()+JS_AG01.split('function agRow(')[0]+r'''
// receituários do MIP (REC-015 e os novos) do estado compartilhado; a linha abre a vistoria de origem (o receituário fica no painel dela)
function a4Rec(r,s,c,v){ const vv=s.vis[r.vis]; const t=MIPD.tal[r.tal]||{rot:r.tal,cultura:''}; const p=vv?mipP(vv):{alvo:''}; const canc=r.sit==='Cancelado'; const emit=r.sit==='Receituário emitido'||canc;
  const osc=r.sit==='Receituário emitido'&&mipOsFora(c,r.os);
  const et=r.os?(mipOsEt(c,r.os)||'—'):''; const dr='a4go_'+r.id; v[dr]=()=>{ location.href='AG-01.dc.html#'+r.vis; };
  const prod=emit?(r.nome+' '+mipN(r.dose,3)+' '+r.un+'/ha · '+mipN(r.area,2)+' ha'):'a definir na decisão'; const jan=emit?('a partir de '+mipBr(r.data)):'—';
  return {id:r.id,ro:true,dr,v:{id:r.id,parc:t.rot+' · '+t.cultura,op:'Pulverização · '+p.alvo.toLowerCase(),jan,fonte:emit?('bula AGROFIT · Ana (RT) · '+r.ra):'— · pendente'},
    s:{orig:r.dia+' '+r.vis,op:'Pulverização · '+p.alvo.toLowerCase()+' '+t.rot,prod:prod+' '+jan,sit:canc?'Cancelado':(osc?'O.S. cancelada':(emit?'Receituário emitido':'Rascunho'))},
    p:{id:[{k:'b',t:r.id},{k:'br'},{k:'mut',t:emit?r.ra:'rascunho'}],orig:[{k:'txt',t:r.dia},{k:'br'},{k:'link',t:r.vis,h:'AG-01.dc.html#'+r.vis}],
       op:[{k:'txt',t:'Pulverização · '+p.alvo.toLowerCase()},{k:'br'},{k:'mut',t:t.rot+' · '+t.cultura}],
       prod:[{k:'txt',t:prod},{k:'br'},{k:'mut',t:'janela: '+jan}],
       sit:canc?[{k:'chip',t:'Cancelado',c:'gray'},{k:'br'},{k:'mut',t:(r.motivo||r.os+' cancelada')+(r.subst?' · substituído pelo '+r.subst:'')}]
          :(osc?[{k:'chip',t:'O.S. cancelada',c:'red'},{k:'br'},{k:'mut',t:r.os+' · decidir de novo'}]
          :(emit?[{k:'chip',t:'Receituário emitido',c:'green'},{k:'br'},{k:'mut',t:r.os+' · '+et}]:[{k:'chip',t:'Rascunho',c:'gray'},{k:'br'},{k:'mut',t:'aguarda a decisão do '+r.dia}])),
       acao:canc?[{k:'mut',t:r.subst?'ver '+r.subst:'—'}]:((osc||!emit)?[{k:'cta',t:'Decidir controle',h:'AG-01.dc.html#'+r.vis+':decidir',u:true}]:[{k:'cta',t:'Abrir '+r.os,h:'OS.dc.html#'+r.os}])}}; }
function PREVALS(self,v){ cenOuvir(self); mipOuvir(self); const sp=GRIDS.find(g=>g.id==='g_rec'); if(!sp.base) sp.base=sp.rows.slice();
  const s=mipGet(), c=agC(); const mip=Object.values(s.rec).sort((a,b)=>(a.id<b.id?-1:1)).map(r=>a4Rec(r,s,c,v));
  sp.rows=[sp.base[0]].concat(mip.filter(r=>r.id<'REC-016')).concat(sp.base.slice(1)).concat(mip.filter(r=>r.id>='REC-016')); }
function EXTRAVALS(self,v){ v['a4go_REC-014']=()=>{ location.href='AG-04det.dc.html'; };
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_rec') return; r.p.prod=[{k:'txt',t:r.v.prod},{k:'br'},{k:'mut',t:'janela: '+(r.v.jan||'—')}]; r.s.prod=r.v.prod+' '+(r.v.jan||'');
    r.p.op=[{k:'txt',t:r.v.op||'—'},{k:'br'},{k:'mut',t:r.v.parc||''}]; r.s.op=(r.v.op||'')+' '+(r.v.parc||''); }; }
'''
    corpo=bloco('Recomendações e receituários','',g4,ilink('Ver demanda gerada','PL-02.dc.html','layers','Abrir as necessidades geradas no planejamento'))
    HEIGHTS37[fname]=700; PARENT37[fname]='AG-01.dc.html'
    shell37('AG-04','Recomendações',corpo,fname=fname,crumbs_extra=['Recomendações'],search=False,status=('1 uso sem registro (REC-014)','red'))

    # ---- AG-04det · REC-014 (elo 3): v3 já aprovada no saldo (igual ao Mapa e à O.S.) e conferência Agrofit do TS ----
    fname='AG-04det.dc.html'; E._reset_screen(fname)
    cver=[dict(k='ver',l='Versão'),dict(k='mud',l='O que muda',w=320),dict(k='alc',l='Alcance',w=200),dict(k='sit',l='Situação',w=230),dict(k='data',l='Quando',t='date')]
    gver=grid(cver,[
        R('v1',ver='v1',mud='KCl 100 kg/ha em dose única',alc='—',sit=[Pt.chip('Substituída','gray')],data='2026-09-18'),
        R('v2',ver='v2',mud='Dose por zona (140/120/95 kg/ha) + TS nematicida',alc=f'{REAL20} ha realizados na OS-0420',sit=[Pt.chip(f'Em uso nos {REAL20} ha realizados','green')],data='2026-09-21'),
        R('v3',ver='v3',mud='KCl −12 % → 105,6 kg/ha (zonas 123/106/84)',alc=f'só o saldo de {SALDO20} ha',sit=[Pt.chip('KCl aprovado por Ana','green'),Pt.br(),Pt.chip('TS travado · sem registro','red')],data='2026-09-23'),
      ],edit=consulta(cver,'Versão da recomendação','Histórico de versões: o realizado nunca muda; a versão nova vale só para o saldo.'),search=False,gid='g_ver',total=False)
    cit=[dict(k='prod',l='Produto',w=200),dict(k='un',l='Unidade'),dict(k='sug',l='Dose sugerida',a='r'),dict(k='inf',l='Dose informada',a='r'),dict(k='bula',l='Registro Agrofit',w=260)]
    git=grid(cit,[
        R('i1',prod='KCl 60 %',un='kg/ha',sug='118',inf=[Pt.b('120')],bula=[Pt.mut('fertilizante · fora do Agrofit')],o=[('IAC Boletim 100 · K trocável 0,08 cmolc/dm³','AG-02.dc.html')]),
        R('i2',prod='TS nematicida (abamectina)',un='mL/100 kg sem.',sug='100',inf=[Pt.b('100')],
          bula=[Pt.chip('Sem registro p/ nematoide-de-cisto','red'),Pt.br(),Pt.mut('bula: galhas e lesões · 125 mL/100 kg')],
          o=[('Ficha Abamectina 500 FS · registro só para nematoide-das-galhas e das-lesões',None),
             ('Alternativa registrada para cisto: Pasteuria nishizawae FS · 0,3 L/100 kg de sementes',None)]),
        R('i3',prod='Semente 58 W (resistente)',un='kg/ha',sug='52',inf=[Pt.b('52')],bula=[Pt.mut('semente · fora do Agrofit')],o=[('Decisão do DIA-007 · cultivar resistente','AG-03det.dc.html')]),
      ],edit=dict(m='origin',title='Item da recomendação',sub='Versão aprovada: confira a origem; alteração por nova versão, só para o saldo.',fields=[F('prod','Produto',ro=True),F('inf','Dose informada',ro=True)]),search=False,gid='g_it',total=False)
    cz=[dict(k='zona',l='Zona'),dict(k='area',l='Área',t='num',a='r',u='ha',agg='sum'),dict(k='k',l='K trocável'),dict(k='dose',l='KCl 60 % (v2)',t='num',a='r',u='kg/ha'),dict(k='v3',l='Saldo na v3',t='num',a='r',d=1,u='kg/ha')]
    gz=grid(cz,[
        R('z1',zona='Z1 (reboleiras)',area=62,k='0,05 cmolc/dm³',dose=140,v3=123.2,o=[('LAU-2043 · zona 1 · K 0,05 cmolc/dm³','AG-02.dc.html'),('IAC Boletim 100 · classe muito baixa → 140 kg/ha',None),('v3: 140 × 0,88 = 123,2 kg/ha',None)]),
        R('z2',zona='Z2',area=98,k='0,08 cmolc/dm³',dose=120,v3=105.6,o=[('LAU-2043 · zona 2 · K 0,08 cmolc/dm³','AG-02.dc.html'),('IAC Boletim 100 · classe baixa → 120 kg/ha',None),('v3: 120 × 0,88 = 105,6 kg/ha',None)]),
        R('z3',zona='Z3',area=44,k='0,12 cmolc/dm³',dose=95,v3=83.6,o=[('LAU-2043 · zona 3 · K 0,12 cmolc/dm³','AG-02.dc.html'),('IAC Boletim 100 · classe média → 95 kg/ha',None),('v3: 95 × 0,88 = 83,6 kg/ha',None)]),
      ],edit=dict(m='origin',title='Dose da zona',sub='Dose calculada: confira a origem; para mudar, crie nova versão.',fields=[F('zona','Zona',ro=True),F('dose','KCl 60 % (v2)',ro=True,u='kg/ha'),F('v3','Saldo na v3',ro=True,u='kg/ha')]),
      search=False,gid='g_zon',total=True)
    cex=[dict(k='reg',l='Registro'),dict(k='oque',l='O que é',w=300),dict(k='sit',l='Situação',w=320)]
    gex=grid(cex,[
        R('nec',reg=[Pt.link('NEC-028','PL-02.dc.html')],oque='Necessidade de plantio do T4 · 204 ha · 1ª onda de 100 ha',sit=[Pt.chip('Programada','green')]),
        R('os',reg=[Pt.link('OS-0420','OS.dc.html#OS-0420')],oque=f'{OS20["tipo"]} · {REAL20}/{AREA20} ha · saldo {SALDO20} ha na v3',
          sit=[Pt.chip('Em execução','green'),Pt.chip('Impedida · OM-0233','red')]),
      ],edit=consulta(cex,'Registro vinculado','Destino da recomendação: demanda única, sem duplicar; abra o registro pelo link.'),search=False,gid='g_exe',total=False)
    CUSTO=[('c1','Semente de soja 58 W','REQ-036','SU-07.dc.html','1.560 kg × R$ 9,50',1560*9.5,'Definitivo','green'),
           ('c2','KCl 60 %','REQ-037','SU-07.dc.html','3.600 kg × R$ 2,40',3600*2.4,'Definitivo','green'),
           ('c3','Máquina e equipe · plantio','Apontamentos dias 1 e 2','CA-02.dc.html','6,0 h × R$ 396,00',6*396,'Provisório · 12 ha a conferir','yellow'),
           ('c4','Diesel S10 · Trator T1','Abastecimento','MA.dc.html#vis=ativos&modo=abastecimentos','84 L × R$ 5,92',84*5.92,'Provisório · conciliar tanque','yellow')]
    ccu=[dict(k='item',l='Recurso',w=200),dict(k='orig',l='Origem'),dict(k='qtd',l='Quantidade × preço',w=170),dict(k='custo',l='Custo',t='num',a='r',d=2,pre='R$ ',agg='sum'),dict(k='sit',l='Situação',w=200)]
    gcu=grid(ccu,[R(i,item=it,orig=[Pt.link(o,h)],qtd=q,custo=round(v,2),sit=[Pt.chip(s,c)],o=[(f'{o} · {q}',h),(f'{REAL20} ha realizados na v2 · preservados na v3',None)])
                  for i,it,o,h,q,v,s,c in CUSTO],
        edit=dict(m='origin',title='Custo realizado',sub='Custo apontado nos hectares já plantados; versão nova não altera este valor.',
                  fields=[F('item','Recurso',ro=True),F('qtd','Quantidade × preço',ro=True),F('custo','Custo',ro=True,u='R$')]),
        search=False,gid='g_cus',total=True)
    alerta=(f'<div role="alert" style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border-radius: 10px; background: {REDS}; border: 1px solid #F4C7C1; color: {RED}; font-size: 13px; font-weight: 700; line-height: 1.45;">'
            f'<span>Trava legal: TS nematicida (abamectina) sem registro para soja × nematoide-de-cisto. O saldo de {SALDO20} ha só usa TS registrado: crie a v4.</span>'
            f'<span style="display: flex; gap: 14px; flex-wrap: wrap;"><a href="AG-07.dc.html#abamectina-500-fs" style="color: {RED};">Ficha da abamectina 500 FS ›</a>'
            f'<a href="AG-07.dc.html#pasteuria-nishizawae-fs" style="color: {RED};">Pasteuria nishizawae FS (registrada para cisto) ›</a></span></div>')
    memoria=(f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.7; background: {BG}; border: 1px solid {LINE}; border-radius: 12px; padding: 12px 14px;">'
             f'K trocável 0,08 cmolc/dm³ ({LAUDOS[0]} · Mehlich-1 · 0–20 cm) · CTC 9,2 → participação de K 0,9 % (alvo 3 %)<br>'
             f'IAC Boletim 100 · soja &gt; 3 t/ha esperadas → <b style="color:{INK};">70 kg/ha de K₂O</b> na base ≈ 118 kg/ha de KCl 60 %<br>'
             f'Informado 120 kg/ha (arredondamento do regulador da plantadeira) · desvio +1,7 % registrado</div>')
    corpo=(
      cadeia('REC-014','','')
      + bloco('Itens e registro Agrofit','',alerta+git,tone='red')
      + bloco('Versões','',gver)
      + bloco('Contexto da versão aprovada','',
          _kv([('Origem','DIA-007 · nematoide + K baixo'),('Ciclo · talhão','Safra 2026/27 · T4 · 204 ha'),
               ('Operação','Plantio'),('Janela','20/09 a 05/10'),('Fonte científica','IAC Boletim 100'),('Aprovador (RT)','Ana'),('Aprovada em','21/09/2026 · v3 (KCl) em 23/09'),('Destino','NEC-028 · demanda única')]))
      + bloco('Memória de cálculo','',memoria)
      + bloco('Prescrição espacial por zona','',gz,
          imsg('Gerar prescrição','Prescrição por zona (3 zonas do T4) validada: terminal da plantadeira, unidade kg/ha, coordenadas SIRGAS 2000 e versão v3 do saldo conferidos · pronta para exportar.',
               'map','Validar terminal, unidade, coordenadas e versão e gerar o arquivo da prescrição'))
      + bloco('Execução vinculada','',gex)
      + bloco(f'Custo realizado dos {REAL20} ha','',gcu))
    HEIGHTS37[fname]=2300; PARENT37[fname]='AG-04.dc.html'
    shell37('AG-04','Recomendação · REC-014 plantio T4',corpo,fname=fname,crumbs_extra=['Recomendações','REC-014 · v2'],search=False,
      status=(f'Saldo de {SALDO20} ha travado · TS sem registro','red'),
      primary_html=idrawer('Criar v4 com TS registrado',dict(title='Criar v4 · saldo de 70 ha',sub='Troca o TS sem registro por um produto registrado para soja × nematoide-de-cisto; o realizado na v2 não muda.',
           fields=[('TS registrado para cisto','Pasteuria nishizawae FS'),('Dose','0,3 L/100 kg de sementes'),('KCl','mantém a v3 (105,6 kg/ha)'),('Alcance',f'saldo de {SALDO20} ha'),('Aprovador (RT)','Ana')],
           confirm='Criar v4 para aprovação',done=f'v4 em rascunho com Pasteuria nishizawae FS · Ana aprova; até lá o TS do saldo segue travado.'),
           'leaf','Criar a versão 4 só para o saldo, com TS registrado para nematoide-de-cisto',primary=True,small=False))

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
      footer='Redução observada não equivale a eficácia causal; a EF-020 fecha a cadeia da demonstração quando a OS-0420 tiver leitura pós.')

    ag07()   # AG-07 · Consulta Agrofit (função própria, abaixo)

# ================= Pragas e doenças (MIP/MID) · AG-01 lista + painel + decisão · AG-01det rota e evidências =================
# Uma base só (dados_mip.py + mip.js, estado 'talhao-os-mip-v1'): o Mapa, o AG-01, o AG-01det, o AG-03/AG-04 e o app (MB-06) leem e gravam
# as mesmas vistorias. A decisão do agrônomo (RT) gera DIA + REC/RA + O.S. em A liberar no cenário das O.S. (Ana libera em OS.dc.html).
# AG-01.dc.html#VIS-xxx abre o painel da vistoria e troca a fazenda do filtro; sem hash, a fazenda vem do contexto do Mapa (mapa-ctx).
_LAB=lambda t: f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{t}</div>'
def _ch(t,st,dot): return f'<span style="{H(st)}"><span style="{H(dot)}"></span>{H(t)}</span>'
_BOX_RED=f'font-size: 12.8px; font-weight: 700; line-height: 1.45; color: {RED}; background: {REDS}; padding: 7px 10px; border-radius: 8px;'
_BOX_YEL=f'font-size: 12.8px; font-weight: 600; line-height: 1.45; color: {YEL}; background: {YELS}; padding: 7px 10px; border-radius: 8px;'
_BOX_INF=f'font-size: 12.5px; line-height: 1.45; color: {MUTED};'
_INP=f'font-family: inherit; font-size: 14px; padding: 8px 10px; border-radius: 9px; border: 1px solid {LINE}; background: {SURF}; color: {INK}; box-sizing: border-box;'
_FLD=f'display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 700; color: {MUTED};'
_LNKA=f'font-size: 12.5px; font-weight: 700; color: {ACC}; text-decoration: none; white-space: nowrap;'

def _ag01_painel():
    sec=lambda k,titulo,corpo: (f'<sc-if value="{H("ps_"+k)}" hint-placeholder-val="{T_()}"><section aria-label="{titulo}" style="border: 1px solid {LINE}; border-radius: 12px; padding: 10px 12px 12px; display: flex; flex-direction: column; gap: 8px;">'
                                f'{_LAB(titulo)}{corpo}</section></sc-if>')
    steps=(f'<div role="list" aria-label="Etapas da vistoria" style="display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 6px;">'
           f'<sc-for list="{H("pan_steps")}" as="p" hint-placeholder-count="5"><div role="listitem" aria-current="{H("p.cur")}" style="{H("p.st")}"><span style="{H("p.bst")}"></span>{H("p.t")}</div></sc-for></div>')
    msgs=lambda lst,st,role: f'<sc-for list="{H(lst)}" as="m" hint-placeholder-count="0"><div role="{role}" style="{st}">{H("m.t")}</div></sc-for>'
    # formulário de decisão (dentro do Próximo passo): tipo de decisão · produtos registrados com a conferência · dose, área e data · RT
    prod=(f'<sc-for list="{H("dc_prods")}" as="x" hint-placeholder-count="3"><div style="{H("x.st")}">'
          f'<label style="display: flex; align-items: flex-start; gap: 8px; flex-grow: 1; min-width: 0; cursor: pointer;">'
          f'<input type="radio" name="dc_prod" checked="{H("x.on")}" onChange="{H("x.pick")}" aria-label="{H("x.nome")}" style="margin: 3px 0 0; width: 16px; height: 16px; accent-color: {ACC}; flex-shrink: 0;">'
          f'<span style="display: flex; flex-direction: column; gap: 1px; min-width: 0;"><b style="font-size: 13.5px;">{H("x.nome")}</b><span style="font-size: 12px; color: {MUTED}; line-height: 1.35;">{H("x.sub")}</span></span></label>'
          f'{_ch("x.cht","x.chst","x.chdot")}<a href="{H("x.h")}" target="_blank" rel="noopener" title="Abrir a ficha na Consulta Agrofit (nova aba)" style="{_LNKA}">Ficha ›</a></div></sc-for>')
    campos=(f'<div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end;">'
            f'<sc-if value="{H("dc_temProd")}" hint-placeholder-val="{F_()}"><label style="{_FLD}"><span>Dose ({H("dc_un")}/ha)</span><input id="dc_dose" inputMode="decimal" aria-label="Dose por hectare" value="{H("dc_dose")}" onChange="{H("dc_setdose")}" style="{_INP} width: 110px; text-align: right;"></label></sc-if>'
            f'<label style="{_FLD}"><span>{H("dc_areaL")}</span><input inputMode="decimal" aria-label="Área em hectares" value="{H("dc_area")}" onChange="{H("dc_setarea")}" style="{_INP} width: 100px; text-align: right;"></label>'
            f'<label style="{_FLD}"><span>A partir de</span><input type="date" aria-label="Data da aplicação" value="{H("dc_data")}" onChange="{H("dc_setdata")}" style="{_INP}"></label></div>')
    form=(f'<sc-if value="{H("pan_dec")}" hint-placeholder-val="{F_()}"><div role="group" aria-label="Decisão do agrônomo" style="display: flex; flex-direction: column; gap: 10px; padding: 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
          f'<div role="radiogroup" aria-label="Decisão" style="display: flex; gap: 6px; flex-wrap: wrap;"><sc-for list="{H("dc_kinds")}" as="o" hint-placeholder-count="3">'
          f'<button type="button" role="radio" aria-checked="{H("o.on")}" onClick="{H("o.go")}" style="{H("o.st")}">{H("o.t")}</button></sc-for></div>'
          f'<sc-if value="{H("dc_ctl")}" hint-placeholder-val="{F_()}">'
          f'<sc-if value="{H("dc_semProd")}" hint-placeholder-val="{F_()}"><div role="alert" style="{_BOX_RED}">{H("dc_semT")} <a href="AG-07.dc.html" style="{_LNKA}">Abrir Consulta Agrofit ›</a></div></sc-if>'
          f'<sc-if value="{H("dc_temProd")}" hint-placeholder-val="{F_()}"><div style="display: flex; flex-direction: column; gap: 4px;">{_LAB(H("dc_uso"))}'
          f'<div role="radiogroup" aria-label="Produto registrado" style="display: flex; flex-direction: column; border: 1px solid {LINE}; border-radius: 10px; overflow: hidden;">{prod}</div></div></sc-if>'
          f'{campos}</sc-if>'
          f'<sc-if value="{H("dc_err")}" hint-placeholder-val="{F_()}"><div style="{_BOX_INF}">{H("dc_errT")}</div>{campos.replace(H("dc_temProd"),H("dc_nunca"))}</sc-if>'
          f'<sc-if value="{H("dc_mon")}" hint-placeholder-val="{F_()}"><div style="{_BOX_INF}">{H("dc_monT")}</div>'
          f'<sc-if value="{H("dc_pedeMot")}" hint-placeholder-val="{F_()}"><label style="{_FLD}"><span>{H("dc_motL")}</span><textarea id="dc_mot" aria-label="{H("dc_motL")}" value="{H("dc_mot")}" onChange="{H("dc_setmot")}" placeholder="{H("dc_motPh")}" style="{_INP} min-height: 56px; resize: vertical; width: 100%;"></textarea></label></sc-if></sc-if>'
          + msgs('dc_tr',_BOX_RED,'alert') + msgs('dc_al',_BOX_YEL,'note') + msgs('dc_inf',_BOX_INF,'note')
          + f'<div style="font-size: 12px; color: {MUTED};">{H("dc_rt")}</div>'
          f'<div style="display: flex; gap: 8px; flex-wrap: wrap;"><button type="button" onClick="{H("dc_cancel")}" style="{_MINI}">Cancelar</button>'
          f'<button type="button" onClick="{H("dc_ok")}" disabled="{H("dc_bloq")}" title="{H("dc_okTitle")}" style="{H("dc_okst")}">{H("dc_okt")}</button></div></div></sc-if>')
    passo=(f'<div role="region" aria-label="Próximo passo" style="{H("pan_pst")}">{_LAB("Próximo passo")}'
           f'<div style="font-size: 13.5px; line-height: 1.45;">{H("pan_pt")}</div>' + msgs('pan_al',_BOX_YEL,'note')
           + f'<sc-if value="{H("pan_idle")}" hint-placeholder-val="{T_()}"><div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">'
           f'<sc-if value="{H("pan_hasBtn")}" hint-placeholder-val="{F_()}"><button type="button" id="pan_prim" onClick="{H("pan_go")}" style="{BTN_ST(True,True)}">{H("pan_btn")}</button></sc-if>'
           f'<sc-if value="{H("pan_hasLnk")}" hint-placeholder-val="{F_()}"><a href="{H("pan_lnk")}" id="pan_prim_a" style="{BTN_ST(True,True)} text-decoration: none; display: inline-flex;">{H("pan_lnkt")}</a></sc-if>'
           f'<sc-if value="{H("pan_hasSec")}" hint-placeholder-val="{F_()}"><button type="button" onClick="{H("pan_secgo")}" style="{_MINI}">{H("pan_sect")}</button></sc-if></div></sc-if>'
           + form + '</div>')
    pontos=(f'<div style="display: flex; flex-wrap: wrap; gap: 5px;"><sc-for list="{H("pan_pts")}" as="q" hint-placeholder-count="12"><span title="{H("q.tt")}" style="{H("q.st")}">{H("q.t")}</span></sc-for></div>'
            f'<div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; font-size: 12px; color: {MUTED};"><sc-for list="{H("pan_leg")}" as="l" hint-placeholder-count="4"><span style="display: inline-flex; align-items: center; gap: 5px;"><span style="{H("l.st")}"></span>{H("l.t")}</span></sc-for>'
            f'<span style="flex-grow: 1;"></span><a href="{H("pan_det")}" style="{_LNKA}">Ver rota e evidências ›</a></div>')
    kv=(f'<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px 16px;"><sc-for list="{H("pan_kv")}" as="x" hint-placeholder-count="4"><div style="min-width: 0;">'
        f'<div style="font-size: 10.5px; font-weight: 700; letter-spacing: .05em; color: {MUTED}; text-transform: uppercase;">{H("x.l")}</div><div style="font-size: 13.5px; font-weight: 700; margin-top: 2px;">{H("x.v")}</div></div></sc-for></div>'
        f'<sc-if value="{H("pan_hasBar")}" hint-placeholder-val="{F_()}"><div aria-hidden="true" style="position: relative; height: 8px; border-radius: 999px; background: #E4E9E5; margin-top: 4px;"><div style="{H("pan_barst")}"></div>'
        f'<div style="position: absolute; left: 50%; top: -4px; width: 2px; height: 16px; background: {INK};"></div></div>'
        f'<div style="display: flex; justify-content: space-between; font-size: 11px; color: {MUTED};"><span>0</span><span>NC {H("pan_nc")}</span><span>2 × NC</span></div></sc-if>')
    reg=(f'<sc-for list="{H("pan_reg")}" as="r" hint-placeholder-count="2"><div style="display: flex; align-items: flex-start; gap: 10px; padding: 6px 0; border-top: 1px solid {LINE};">'
         f'<div style="display: flex; flex-direction: column; gap: 1px; flex-grow: 1; min-width: 0;"><span style="font-size: 13px; font-weight: 700;">{H("r.t")}</span><span style="font-size: 12px; color: {MUTED}; line-height: 1.4;">{H("r.sub")}</span></div>'
         f'<sc-if value="{H("r.hasH")}" hint-placeholder-val="{F_()}"><a href="{H("r.h")}" style="{_LNKA}">{H("r.hl")} ›</a></sc-if></div></sc-for>' + msgs('pan_regal',_BOX_YEL,'note') + msgs('pan_regtr',_BOX_RED,'alert'))
    hist=(f'<sc-for list="{H("pan_hist")}" as="x" hint-placeholder-count="3"><div style="display: grid; grid-template-columns: 54px minmax(0, 1fr) auto; gap: 8px; align-items: center; padding: 5px 0; border-top: 1px solid {LINE}; font-size: 12.8px;">'
          f'<span style="color: {MUTED}; font-variant-numeric: tabular-nums;">{H("x.d")}</span><span style="min-width: 0;"><sc-if value="{H("x.hasH")}" hint-placeholder-val="{F_()}"><a href="{H("x.h")}" style="color: {ACC}; font-weight: 700; text-decoration: none;">{H("x.t")}</a></sc-if>'
          f'<sc-if value="{H("x.noH")}" hint-placeholder-val="{T_()}"><b>{H("x.t")}</b></sc-if><span style="color: {MUTED};"> · {H("x.sub")}</span></span>{_ch("x.ch","x.chst","x.chdot")}</div></sc-for>')
    return (f'<sc-if value="{H("pan_open")}" hint-placeholder-val="{F_()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar painel" tabIndex="-1" onClick="{H("pan_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-modal="true" aria-label="{H("pan_t")}" onKeyDown="{H("pan_key")}" style="position: relative; width: 780px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 20px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
      f'<div style="display: flex; align-items: flex-start; gap: 10px;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em; flex-grow: 1; line-height: 1.3;">{H("pan_t")}</h2>'
      f'<button type="button" id="pan_x" aria-label="Fechar" title="Fechar" onClick="{H("pan_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
      f'<div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center;">{_ch("pan_sit","pan_sst","pan_sdot")}<span style="font-size: 12.5px; color: {MUTED};">{H("pan_ssub")}</span></div>'
      f'<div style="font-size: 13px; font-weight: 600; line-height: 1.45;">{H("pan_res")}</div>'
      + steps + passo
      + sec('res','Resultado por alvo',kv)
      + sec('pts','Pontos',pontos)
      + sec('reg','Decisão e receituário',reg)
      + sec('hist','Histórico no talhão',hist)
      + '</aside></div></sc-if>')

def _ag01_programar():
    sel=lambda lab,val,fn,lst,dis=None,idn='': (f'<label style="{_FLD}">{lab}<select{(" id=" + chr(34) + idn + chr(34)) if idn else ""} aria-label="{lab}" value="{H(val)}" onChange="{H(fn)}"'
                                                + (f' disabled="{H(dis)}"' if dis else '') + f' style="{_INP} width: 100%;"><sc-for list="{H(lst)}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label>')
    return (f'<sc-if value="{H("pv_open")}" hint-placeholder-val="{F_()}"><div style="position: fixed; inset: 0; z-index: 62; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar" tabIndex="-1" onClick="{H("pv_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-modal="true" aria-label="Programar vistoria" onKeyDown="{H("pv_key")}" style="position: relative; width: 460px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">'
      f'<div style="display: flex; align-items: center; gap: 10px;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; flex-grow: 1;">Programar vistoria</h2>'
      f'<button type="button" aria-label="Fechar" onClick="{H("pv_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED};">×</button></div>'
      f'<sc-if value="{H("pv_escFaz")}" hint-placeholder-val="{F_()}">{sel("Fazenda","pv_faz","pv_setfaz","pv_fazs")}</sc-if>'
      + sel('Talhão','pv_tal','pv_settal','pv_tals',idn='pv_tal') + sel('Alvo','pv_prot','pv_setprot','pv_prots','pv_semTal')
      + f'<div style="font-size: 12.8px; line-height: 1.5; padding: 9px 11px; border-radius: 10px; background: {BG};">{H("pv_resumo")}</div>'
      f'<label style="{_FLD}">Data<input type="date" aria-label="Data da vistoria" value="{H("pv_data")}" onChange="{H("pv_setdata")}" style="{_INP} width: 100%;"></label>'
      + sel('Responsável','pv_resp','pv_setresp','pv_resps')
      + f'<sc-if value="{H("pv_hasErr")}" hint-placeholder-val="{F_()}"><div role="alert" style="{_BOX_RED}">{H("pv_err")}'
      f'<sc-if value="{H("pv_hasAb")}" hint-placeholder-val="{F_()}"> <button type="button" onClick="{H("pv_abrir")}" style="border: 0; background: transparent; color: {RED}; font-family: inherit; font-weight: 800; text-decoration: underline; cursor: pointer; padding: 0;">Abrir {H("pv_ab")}</button></sc-if></div></sc-if>'
      f'<div style="display: flex; gap: 8px; justify-content: flex-end;"><button type="button" onClick="{H("pv_close")}" style="{_MINI}">Cancelar</button>'
      f'<button type="button" onClick="{H("pv_save")}" style="{_MINIP}">Programar vistoria</button></div></aside></div></sc-if>')

def _ag01_restaurar():
    lk=f'border: 0; background: transparent; color: {MUTED}; font-family: inherit; font-size: 12px; font-weight: 600; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; padding: 4px;'
    return (f'<div style="display: flex; justify-content: flex-end; align-items: center; gap: 8px; flex-wrap: wrap;">'
            f'<sc-if value="{H("rs_no")}" hint-placeholder-val="{T_()}"><button type="button" onClick="{H("rs_ask")}" style="{lk}">Restaurar demonstração</button></sc-if>'
            f'<sc-if value="{H("rs_yes")}" hint-placeholder-val="{F_()}"><span style="font-size: 12px; color: {MUTED};">Volta vistorias, O.S., estoque e app ao início.</span>'
            f'<button type="button" onClick="{H("rs_ok")}" style="{_MINI} color: {RED}; border-color: {RED};">Restaurar</button><button type="button" onClick="{H("rs_cancel")}" style="{_MINI}">Manter</button></sc-if></div>')

JS_AG01=r'''
// ===== AG-01 · Pragas e doenças: lista (estado MIP) → painel da vistoria → decisão/receituário → O.S. em A liberar =====
const AG_STEPS=['Coleta','Resultado','Decisão','Controle','Avaliação'];
function agCh(c){ const cc=G2C[c]||G2C.gray; return {st:'display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';',dot:'width:6px;height:6px;border-radius:999px;flex-shrink:0;background:'+cc[0]+';'}; }
// fazenda: a do contexto do Mapa (mapa-ctx); sem contexto, Lagoa Grande (o mesmo padrão do Mapa). Trocar aqui grava no contexto.
function agCtx(){ try{ return JSON.parse(sessionStorage.getItem('mapa-ctx')||'null')||{}; }catch(e){ return {}; } }
function agFaz(self){ if(self.state.mf_faz) return self.state.mf_faz; if(self.__fz0===undefined) self.__fz0=agCtx().mf_faz||''; return self.__fz0||'Lagoa Grande'; }
function agFazSalvar(self){ const f=self.state.mf_faz; if(!f) return; const x=agCtx(); if(x.mf_faz===f) return;
  const y=Object.assign({},x,{mf_faz:f}); if(x.mf_faz){ y.tsel=[]; y.px=null; } try{ sessionStorage.setItem('mapa-ctx',JSON.stringify(y)); }catch(e){} }
function agC(){ return (typeof cenGet==='function')?cenGet():null; }
function agCor(R,x){ const val=(x===undefined)?R.media:x; if(val===null||val===undefined) return 'gray'; if(R.crit==='presenca') return Number(val)>0?'orange':'green'; return val>=R.nc?'red':(val>=0.8*R.nc?'yellow':'green'); }
function agRow(s,v,c,S){ const R=S.R, p=mipP(v), t=mipT(v), P=mipProx(s,v,c);
  const nx=P.t?(P.h?[{k:'cta',t:P.t,h:P.h,u:S.k==='acima'}]:[{k:'act',t:P.t,fn:'ag_go:'+v.id+'|'+P.fn,u:S.k==='acima'||S.k==='foco'}]):[{k:'mut',t:'—'}];
  const cont=R.crit==='presenca'?(R.val?R.pres:null):(R.pct===null?null:Math.round(R.pct*100));
  return {id:v.id, gk:{tal:t.rot+' · '+t.faz,alvo:p.alvo,sit:S.t,faz:t.faz},
    v:{id:v.id,tal:t.rot,alvo:p.alvo,cont,data:v.data,sit:S.t,prox:P.t||'—'},
    s:{id:v.id,tal:t.rot+' '+(t.cultura+' '+t.fase).trim()+' '+t.faz,alvo:p.alvo+' '+p.met,cont:R.ctxt+(R.crit==='presenca'?' presença':' '+p.un)+' '+R.ptxt,data:mipBrA(v.data)+' '+v.resp,sit:S.t,prox:P.t||'—'},
    p:{id:[{k:'b',t:v.id}],tal:[{k:'b',t:t.rot},{k:'br'},{k:'mut',t:((t.cultura+' '+t.fase).trim()||'sem cultura')+' · '+t.faz}],alvo:[{k:'txt',t:p.alvo},{k:'br'},{k:'mut',t:p.tipo}],
       cont:(R.ctxt==='—'?[{k:'mut',t:'—'}]:[{k:'cn',t:R.ctxt,c:agCor(R)},{k:'br'},{k:'mut',t:R.crit==='presenca'?'presença':p.un}])
         .concat([{k:'br'},{k:'mut',t:R.col+'/'+R.tot+' pontos'+(R.rec?' · '+R.rec+' recoleta':(R.pend?' · '+R.pend+' no aparelho':''))}]),
       data:[{k:'txt',t:mipBrA(v.data)},{k:'br'},{k:'mut',t:v.resp}],
       sit:[{k:'chip',t:S.t,c:S.c}].concat(S.sub?[{k:'br'},{k:'mut',t:S.sub}]:[]),prox:nx}}; }
function agRows(self,v){ const s=mipGet(), c=agC(); const sk=self.state.ag_sit||'';
  const all=Object.values(s.vis).filter(x=>agRec(self,x)).map(x=>({v:x,S:mipSit(s,x,c)})).sort((a,b)=>(a.S.ord-b.S.ord)||(a.v.data<b.v.data?1:-1));
  if(v){ const cnt={}; all.forEach(x=>{ cnt[x.S.k]=(cnt[x.S.k]||0)+1; }); const ST='font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;';
    const ch=(k,t,n)=>({t,n:String(n),on:String(sk===k),go:()=>self.setState({ag_sit:(sk===k&&k)?'':k}),st:ST+(sk===k?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')});
    v.ag_chips=[ch('','Todas',all.length)].concat(MIP_ORD.filter(k=>cnt[k]).map(k=>ch(k,MIP_SIT[k][0],cnt[k]))); }
  const rows=all.filter(x=>!sk||x.S.k===sk).map(x=>agRow(s,x.v,c,x.S));
  const g=self.state.ag_grp||''; if(!g) return rows;
  const gs={}, ord=[]; rows.forEach(r=>{ const k=r.gk[g]; if(!gs[k]){ gs[k]=[]; ord.push(k); } gs[k].push(r); });
  return ord.map(k=>({id:'g:'+k,v:{id:k},s:{id:k},p:{id:[{k:'b',t:k},{k:'mut',t:'· '+gs[k].length+(gs[k].length>1?' vistorias':' vistoria')}]},kids:gs[k]})); }
// Cultura e Talhão na faixa "Filtros desta tela" (proprietário, 13/10/2026: "nas demais telas que isso for bastante essencial e ajudar o usuário"):
// opções = culturas e talhões com vistoria na fazenda do filtro; o Talhão segue a Cultura. Valem para a lista, os chips de situação e o selo.
function agRec(self,x){ const f=agFaz(self), cu=self.state.mf_cult||'Todas', tl=self.state.mf_tal||'', t=MIPD.tal[x.tal]||{};
  return (f==='Todas'||x.faz===f)&&(cu==='Todas'||t.cultura===cu)&&(!tl||x.tal===tl); }
// abrir uma vistoria fora do recorte tira só o filtro que a esconde (a fazenda segue a regra de cada chamada)
function agInclui(self,x){ const t=MIPD.tal[x.tal]||{}, cu=self.state.mf_cult||'Todas', tl=self.state.mf_tal||'', o={};
  if(cu!=='Todas'&&t.cultura!==cu) o.mf_cult='Todas'; if(tl&&x.tal!==tl) o.mf_tal=''; return o; }
function agTopo(self,v){ const s=mipGet(), f=agFaz(self), cu=self.state.mf_cult||'Todas', tl=self.state.mf_tal||'', cs=[], ts=[];
  const rot=k=>(MIPD.tal[k]||{}).rot||k;
  Object.values(s.vis).forEach(x=>{ if(f!=='Todas'&&x.faz!==f) return; const t=MIPD.tal[x.tal]||{}; if(t.cultura&&cs.indexOf(t.cultura)<0) cs.push(t.cultura);
    if((cu==='Todas'||t.cultura===cu)&&ts.indexOf(x.tal)<0) ts.push(x.tal); });
  cs.sort((a,b)=>a.localeCompare(b,'pt-BR')); if(cu!=='Todas'&&cs.indexOf(cu)<0) cs.push(cu);
  if(tl&&ts.indexOf(tl)<0) ts.push(tl); ts.sort((a,b)=>rot(a).localeCompare(rot(b),'pt-BR',{numeric:true}));
  v.mf_cult=cu; v.mf_cult_opts=[{v:'Todas',t:'Todas'}].concat(cs.map(c=>({v:c,t:c})));
  v.mf_setcult=(e)=>self.setState({mf_cult:e.target.value,mf_tal:'',g2toast:'Cultura: '+e.target.value});
  v.mf_tal=tl; v.mf_tal_opts=[{v:'',t:'Todos'}].concat(ts.map(k=>({v:k,t:rot(k)})));
  v.mf_settal=(e)=>self.setState({mf_tal:e.target.value,g2toast:'Talhão: '+(e.target.value?rot(e.target.value):'Todos')});
  // talhão é de uma fazenda só: trocar para outra fazenda tira o talhão do filtro, com aviso pelo nome
  v.mf_setfaz=(e)=>{ const faz=e.target.value, t=MIPD.tal[self.state.mf_tal||'']; const sai=!!t&&faz!=='Todas'&&t.faz!==faz;
    self.setState(Object.assign({mf_faz:faz,g2toast:'Fazenda: '+faz},sai?{mf_tal:'',g2toast:'Fazenda: '+faz+' · o talhão '+t.rot+' ('+t.faz+') saiu do filtro.'}:{})); }; }
// abrir a vistoria pelo hash (#VIS-xxx): painel aberto e fazenda do filtro trocada para a da vistoria
function agHash(self){ let h=''; try{ h=decodeURIComponent(location.hash||''); }catch(e){ h=''; } const m=/^#(VIS-\d+)(?::(decidir|programar))?$/.exec(h); if(!m) return;
  const v=mipGet().vis[m[1]]; if(!v){ self.setState({g2toast:m[1]+' não encontrada.'}); return; }
  // miprev: a navegação por hash na mesma página sempre redesenha com o estado atual (MIP e O.S. podem ter mudado em outra tela)
  const f=agFaz(self); self.setState(Object.assign({pan:v.id,dec:null,pv:null,mf_faz:(f==='Todas'||f===v.faz)?f:v.faz,miprev:Date.now()},agInclui(self,v)));
  // "#VIS-xxx:decidir" (vindo do Mapa) abre direto o formulário da decisão, sem registrar nada
  // "#VIS-xxx:programar" (vistoria atrasada, vindo do sub-detalhe) abre o formulário da próxima vistoria do mesmo talhão × alvo
  const fn=m[2]?mipProx(mipGet(),v,agC()).fn:'';
  if(m[2]==='decidir'&&fn==='decidir'){ agSetHash(v.id); agDecIni(self,v.id); } else if(m[2]==='programar'&&fn==='programar'){ agSetHash(v.id); agPvOpen(self,v.tal,v.prot); } else agFoco(); }
function agIni(self){ if(self.__agIni) return; self.__agIni=1;
  setTimeout(()=>agHash(self),0);
  try{ window.addEventListener('hashchange',()=>agHash(self)); }catch(e){} }
function agFoco(id){ setTimeout(()=>{ const el=document.getElementById(id||'pan_x'); if(el) el.focus(); },60); }
function agGuarda(self){ try{ const a=document.activeElement; if(a&&a!==document.body&&!a.closest('[role=dialog]')) self.__ret=a; }catch(e){} }
function agVolta(self,id){ const el=self.__ret; self.__ret=null; setTimeout(()=>{ try{
    if(el&&el.isConnected){ el.focus(); return; }
    const row=id?[...document.querySelectorAll('[role=row]')].find(r=>(r.innerText||'').trim().indexOf(id)===0):null;
    const alvo=row?(row.getAttribute('tabindex')!==null?row:row.querySelector('[tabindex]')):null; if(alvo){ alvo.focus(); return; }
    const pv=[...document.querySelectorAll('header button')].find(b=>(b.innerText||'').trim()==='Programar vistoria'); if(pv) pv.focus(); }catch(e){} },60); }
function agTrap(e){ if(!e||e.key!=='Tab') return; const box=e.target&&e.target.closest?e.target.closest('[role=dialog]'):null; if(!box) return;
  const f=[...box.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled])')].filter(x=>x.offsetParent!==null&&x.getAttribute('tabindex')!=='-1');
  if(!f.length) return; const a=f[0], z=f[f.length-1];
  if(e.shiftKey&&document.activeElement===a){ e.preventDefault(); z.focus(); } else if(!e.shiftKey&&document.activeElement===z){ e.preventDefault(); a.focus(); } }
function agSetHash(id){ try{ history.replaceState(null,'',location.pathname+location.search+(id?'#'+id:'')); }catch(e){} }
function agOpen(self,id,fn){ agGuarda(self); agSetHash(id); const st={pan:id,dec:null};
  if(fn==='decidir'){ self.setState(st); agDecIni(self,id); return; }
  self.setState(st); agFoco();
  if(fn) agRun(self,id,fn); }
// comandos sem formulário (sincronizar, decidir com parcial, seguir monitorando abaixo do NC, leitura pós)
function agRun(self,id,fn){
  if(fn==='sinc') return mipMudar(self,s=>mipSinc(s,id));
  if(fn==='parcial') return mipMudar(self,s=>mipParcial(s,id));
  if(fn==='monitorar') return mipMudar(self,s=>mipMonitorar(s,id,''));
  if(fn==='pos') return mipMudar(self,s=>mipPos(s,id));
  if(fn==='programar'){ const v=mipGet().vis[id]; return agPvOpen(self,v.tal,v.prot); }
  if(fn==='decidir') return agDecIni(self,id); }
// ---------- formulário de decisão ----------
function agKinds(R,p){ const k=R.k==='incompleta'||R.k==='cancelada'?R.kr:R.k;
  if(p.id==='inspecao') return [['monitorar','Registrar a causa']];
  if(k==='foco'&&R.crit==='presenca') return [['erradicar','Erradicar plantas'],['monitorar','Seguir monitorando']];
  if(k==='foco'&&R.larga) return [['controlar','Controlar o talhão'],['localizado','Controle localizado'],['monitorar','Seguir monitorando']];
  if(k==='foco') return [['localizado','Controle localizado'],['controlar','Controlar o talhão'],['monitorar','Seguir monitorando']];
  return [['controlar','Controlar o talhão'],['localizado','Controle localizado'],['monitorar','Não controlar']]; }
function agDecIni(self,id){ const s=mipGet(), v=s.vis[id], c=agC(); const R=mipRes(v,s), t=mipT(v), p=mipP(v); const K=agKinds(Object.assign({},R,{k:mipSit(s,v,c).k}),p);
  const kind=K[0][0]; const area=kind==='localizado'?Math.max(1,Math.round((R.reb||1)*t.area/v.npts)):(kind==='erradicar'?1:t.area);
  const L=mipElig(v); const data=mipAmanha();
  const ok=L.find(u=>!mipChecks(s,v,{kind,prod:u.id,dose:u.dmin,area,data},c).tr.length)||L[0];
  self.setState({pan:id,dec:{vid:id,kind,prod:ok?ok.id:'',dose:ok?mipN(ok.dmin,3):'',area:mipN(area,2),data,mot:'',err:''}}); agFoco(ok?'dc_dose':'pan_x'); }
function agDec(self,v){ const st=self.state; const d=st.dec; const s=mipGet(); const vv=s.vis[d.vid]; const c=agC(); const R=mipRes(vv,s), t=mipT(vv), p=mipP(vv);
  const up=(patch)=>self.setState({dec:Object.assign({},self.state.dec,patch,{err:''})});
  const K=agKinds(Object.assign({},R,{k:mipSit(s,vv,c).k}),p);
  v.dc_kinds=K.map(k=>({t:k[1],on:String(d.kind===k[0]),go:()=>{ const area=k[0]==='localizado'?Math.max(1,Math.round((R.reb||1)*t.area/vv.npts)):(k[0]==='erradicar'?1:t.area); up({kind:k[0],area:mipN(area,2)}); },
    st:'font-family:inherit;font-size:12.5px;font-weight:700;padding:6px 12px;border-radius:999px;cursor:pointer;'+(d.kind===k[0]?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')}));
  const ctl=d.kind==='controlar'||d.kind==='localizado'; v.dc_ctl=ctl; v.dc_err=d.kind==='erradicar'; v.dc_mon=d.kind==='monitorar'; v.dc_nunca=false;
  const L=mipElig(vv); v.dc_temProd=ctl&&L.length>0; v.dc_semProd=ctl&&!L.length; v.dc_semT=(p.sem||('Sem produto registrado para '+mipCult(t)+' × '+p.alvo.toLowerCase()+' nesta base.'))+' A decisão fica pendente.';
  // registro cancelado continua à vista (trava legal), mas no fim da lista e fora da contagem de registrados
  const nCanc=L.filter(u=>u.sit==='Cancelado').length; v.dc_uso='Registrados para '+mipCult(t)+' × '+p.alvo.toLowerCase()+' · '+(L.length-nCanc)+(nCanc?' · '+nCanc+' cancelado':'');
  const a={kind:d.kind,prod:d.prod,dose:d.dose,area:d.area,data:d.data}; const num=(x)=>Number(String(x).replace(',','.'));
  v.dc_prods=L.slice().sort((a0,b0)=>(a0.sit==='Cancelado'?1:0)-(b0.sit==='Cancelado'?1:0)).map(u=>{ const sel=u.id===d.prod; const k=mipChecks(s,vv,{kind:d.kind,prod:u.id,dose:sel?d.dose:u.dmin,area:d.area,data:d.data},c);
    const TAGS=[[/^Carência/,'Carência × colheita'],[/^Nº máximo/,'Máx. aplicações'],[/^Dose × área dá 0/,'Área pequena · total 0'],[/^Dose/,'Dose fora da bula'],[/^Registro cancelado/,'Cancelado'],[/^Rotação/,'Rotação'],[/^Estoque/,'Sem estoque'],[/^Colheita/,'Colheita suspensa'],[/reavaliação/,'Reavaliação'],[/não conferido/,'Não conferido']];
    const tag=(x)=>{ const m=TAGS.find(q=>q[0].test(x)); return m?m[1]:''; };
    const tt=k.tr.map(tag).filter(Boolean), ta=k.al.map(tag).filter(Boolean); const cc=tt.length?[tt[0],'red']:(ta.length?[ta.slice(0,2).join(' · '),'yellow']:['Conferido','green']); const cs=agCh(cc[1]);
    return {nome:u.nome,on:sel,pick:()=>up({prod:u.id,dose:mipN(u.dmin,3)}),h:'AG-07.dc.html#'+u.id,cht:cc[0],chst:cs.st,chdot:cs.dot,
      sub:u.g+' · '+u.dose+(u.calda?' (calda 1.000 L/ha)':'')+' · carência '+u.cart+(u.mx?' · máx. '+u.mx+' por ciclo':'')+(u.sit!=='Vigente'?' · '+u.sit:''),
      st:'display:flex;align-items:center;gap:10px;padding:8px 10px;border-top:1px solid #E4E9E5;'+(sel?'background:#F4FAF6;box-shadow:inset 3px 0 0 #1E7A4C;':'')}; });
  const u=L.find(x=>x.id===d.prod); v.dc_un=u?u.un:''; v.dc_dose=d.dose; v.dc_area=d.area; v.dc_data=d.data; v.dc_mot=d.mot||'';
  v.dc_areaL=d.kind==='localizado'?'Área do foco (ha)':(d.kind==='erradicar'?'Área do foco (ha)':'Área (ha)');
  v.dc_setdose=(e)=>up({dose:e.target.value}); v.dc_setarea=(e)=>up({area:e.target.value}); v.dc_setdata=(e)=>up({data:e.target.value}); v.dc_setmot=(e)=>up({mot:e.target.value});
  v.dc_errT='O.S. de tratos culturais sem produto: arrancar e destruir as plantas com sintoma e o entorno. Liberação pelo agrônomo na O.S.';
  const prox=mipAdd(vv.data,R.kr==='perto'?3:p.inter); const px=prox<=MIPD.hoje?mipAmanha():prox;
  v.dc_pedeMot=(R.k==='acima'||R.k==='foco'||(R.k==='incompleta'&&(R.kr==='acima'||R.kr==='foco'))||mipSit(s,vv,c).k==='cancelada');
  v.dc_monT='Registra a decisão e programa a próxima vistoria de '+p.alvo.toLowerCase()+' para '+mipBr(px)+(mipAberta(s,vv.tal,vv.prot)?' (já há vistoria aberta).':'.');
  const insp=p.id==='inspecao'; v.dc_motL=insp?'Causa observada':'Motivo para não controlar'; v.dc_motPh=insp?'Ex.: falha de irrigação na linha 4; sem praga':'Ex.: colheita em 10 dias; predadores em alta';
  if(insp) v.dc_monT='Registra a causa e programa nova inspeção para '+mipBr(px)+'. Se for praga ou doença do protocolo, programe a vistoria do alvo.';
  const ck=mipChecks(s,vv,a,c); const extra=[];
  if(d.kind==='monitorar'&&v.dc_pedeMot&&!String(d.mot||'').trim()) extra.push({t:insp?'Informe a causa observada.':'Informe o motivo para não controlar.'});
  v.dc_tr=ck.tr.map(t0=>({t:t0})).concat(extra).concat(d.err?[{t:d.err}]:[]); v.dc_al=ck.al.map(t0=>({t:t0})); v.dc_inf=ck.inf.map(t0=>({t:t0}));
  const bloq=ck.tr.length>0||extra.length>0||(ctl&&!L.length); v.dc_bloq=bloq;
  v.dc_okt=ctl?'Emitir receituário e gerar O.S.':(d.kind==='erradicar'?'Gerar O.S. de erradicação':'Registrar e programar próxima');
  v.dc_okTitle=bloq?'Resolva a trava acima para continuar':v.dc_okt;
  v.dc_okst='font-family:inherit;font-size:12.5px;font-weight:700;padding:7px 14px;border-radius:9px;border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;'+(bloq?'opacity:.45;cursor:not-allowed;':'cursor:pointer;');
  v.dc_rt=ctl?('Responsável técnico: Ana · receituário RA-'+String(s.seq.ra).padStart(4,'0')+' · a O.S. nasce em A liberar; o estoque é reservado ao liberar.'):(d.kind==='erradicar'?'Decisão de Ana (RT) · O.S. em A liberar.':'Decisão de Ana (RT).');
  v.dc_cancel=()=>self.setState({dec:null});
  v.dc_ok=()=>{ const cur=self.state.dec; if(bloq||!cur||self.__emitindo) return; self.__emitindo=true; setTimeout(()=>{ self.__emitindo=false; },400);
    if(cur.kind==='monitorar'){ const r=mipMudar(self,s2=>mipMonitorar(s2,cur.vid,cur.mot)); if(!r.erro) self.setState({dec:null}); else self.setState({dec:Object.assign({},cur,{err:r.erro})}); agFoco(); return; }
    const r=mipEmitir(self,cur.vid,{kind:cur.kind,prod:cur.prod,dose:cur.dose,area:cur.area,data:cur.data});
    if(r.erro){ self.setState({dec:Object.assign({},cur,{err:r.erro}),g2toast:r.erro}); return; } self.setState({dec:null}); agFoco('pan_prim_a'); }; }
// ---------- painel da vistoria ----------
function agPanel(self,v){ const st=self.state; const s=mipGet(), c=agC(); const vv=st.pan?s.vis[st.pan]:null; v.pan_open=!!vv;
  const close=()=>{ const id=self.state.pan; agSetHash(''); self.setState({pan:null,dec:null}); agVolta(self,id); };
  v.pan_close=close; v.pan_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); if(self.state.dec){ self.setState({dec:null}); agFoco(); } else close(); return; } agTrap(e); };
  ['res','pts','reg','hist'].forEach(k=>{ v['ps_'+k]=false; }); v.pan_dec=false; v.pan_idle=true;
  if(!vv) return;
  const P=mipProx(s,vv,c), S=P.S, R=P.R, p=mipP(vv), t=mipT(vv);
  v.pan_t=vv.id+' · '+p.alvo+' · '+t.rot; const cs=agCh(S.c); v.pan_sit=S.t; v.pan_sst=cs.st; v.pan_sdot=cs.dot; v.pan_ssub=S.sub||'';
  v.pan_res=[t.faz,t.rot,((t.cultura+' '+t.fase).trim()||'sem cultura'),mipN(t.area)+' ha',(vv.est==='programada'?'programada para ':'coleta de ')+mipBrA(vv.data),vv.resp,p.ver+(vv.pos_de?' · leitura pós da '+vv.pos_de:'')].join(' · ');
  // etapas: coleta › resultado › decisão › controle › avaliação (só aria-label, sem rótulo visível)
  const cur={programada:0,coleta:0,sinc:0,incompleta:0,acima:2,foco:2,perto:2,abaixo:2,cancelada:2,controle:3,pos:4,avaliacao:4,encerrada:5,atrasada:5}[S.k];
  const pula=vv.dec&&vv.dec.t==='monitorar';
  v.pan_steps=AG_STEPS.map((n,i)=>{ const done=i<cur, now=i===cur, skip=pula&&i>=3;
    return {t:n+(skip?' · não se aplica':''),cur:now?'step':'false',st:'display:flex;flex-direction:column;gap:5px;font-size:11.5px;font-weight:'+(now?'800':'600')+';color:'+((done||now)&&!skip?'#15201A':'#8A968E')+';',
      bst:'height:5px;border-radius:999px;background:'+(skip?'#E4E9E5':(done?'#9CCBB0':(now?'#1E7A4C':'#E4E9E5')))+';'}; });
  // próximo passo (mesma função do Mapa e do app)
  v.pan_pt=P.txt; const al=[];
  if(['acima','foco','perto','abaixo'].indexOf(S.k)>=0&&!vv.dec&&mipDif(vv.data,MIPD.hoje)>=3) al.push({t:'Resultado de '+mipBr(vv.data)+' sem decisão há '+mipDif(vv.data,MIPD.hoje)+' dias.'});
  if(vv.parcial&&!vv.dec) al.push({t:'Decisão com '+R.val+' de '+R.tot+' pontos (coleta incompleta).'});
  if(R.rec&&!vv.dec) al.push({t:R.rec+(R.rec>1?' pontos':' ponto')+' em recoleta (GPS fora da tolerância): fora da média.'});
  const dz=vv.dia&&s.dia[vv.dia]; if(dz&&dz.laudo&&!vv.dec) al.push({t:dz.laudo+' (folha) inconsistente: não decide o controle de pragas; segue no AG-02.'});
  v.pan_al=al;
  const isH=!!P.h, isF=!!P.fn; v.pan_hasBtn=isF; v.pan_hasLnk=isH; v.pan_btn=P.t; v.pan_lnk=P.h||'#'; v.pan_lnkt=P.t;
  v.pan_go=()=>agRun(self,vv.id,P.fn); v.pan_hasSec=!!P.sec; v.pan_sect=P.sec?P.sec.t:''; v.pan_secgo=()=>{ if(P.sec) agRun(self,vv.id,P.sec.fn); };
  const dec=!!(st.dec&&st.dec.vid===vv.id); v.pan_dec=dec; v.pan_idle=!dec;
  v.pan_pst='display:flex;flex-direction:column;gap:8px;padding:12px 14px;border-radius:12px;'+({red:'background:#FDE8E6;border:1px solid #F4C7C1;',orange:'background:#FFF0E3;border:1px solid #F3CFAE;',yellow:'background:#FFF8E6;border:1px solid #F0D9A0;'}[S.c]||'background:#E4F3E9;border:1px solid #BFE0CB;');
  if(dec) agDec(self,v);
  // resultado por alvo
  v.ps_res=vv.est!=='programada'; const nc=R.nc;
  v.pan_kv=(R.crit==='presenca')?[{l:'Critério',v:'presença'},{l:'Pontos com sintoma',v:R.pres+' de '+R.val},{l:'Pontos coletados',v:R.col+' de '+R.tot},{l:'Unidade',v:p.un}]
    :[{l:'Média válida',v:R.media===null?'—':mipN(R.media)+' '+p.un},{l:'Nível de controle',v:mipN(nc)+' '+p.un+' ('+t.fase+')'},{l:'% do NC',v:R.pct===null?'—':mipPct(R.pct)+' %'},{l:'Pontos válidos',v:R.val+' de '+R.tot+(R.rec?' · '+R.rec+' recoleta':'')}];
  if(R.red!==null) v.pan_kv=v.pan_kv.concat([{l:'Redução observada',v:Math.round(R.red*100)+' %'}]);
  v.pan_hasBar=R.crit!=='presenca'&&R.pct!==null; v.pan_nc=mipN(nc)+' '+p.un;
  v.pan_barst='position:absolute;left:0;top:0;bottom:0;border-radius:999px;width:'+Math.min(100,Math.round((R.pct||0)*50))+'%;background:'+({red:'#B42318',yellow:'#C99A2E',green:'#1E7A4C'}[agCor(R)]||'#8A968E')+';';
  // pontos (média só com válidos; recoleta à vista; não coletado vazio)
  v.ps_pts=true; v.pan_det='AG-01det.dc.html#'+vv.id;
  const pend=(vv.pend||[]);
  v.pan_pts=vv.pts.map((q,i)=>{ const nul=q.v===null||q.v===undefined; const pv=nul&&pend.length?pend[vv.pts.filter((x,j)=>j<i&&(x.v===null||x.v===undefined)).length]:undefined;
    const val=nul?pv:q.v; const cor=q.rec?'gray':(val===undefined?'none':agCor(R,val));
    const bg={red:['#FDE8E6','#B42318'],orange:['#FFE8D6','#9A3F00'],yellow:['#FFF3D6','#8A5A00'],green:['#E4F3E9','#1E7A4C'],gray:['#EEF1EE','#5B6660'],none:['#FFFFFF','#8A968E']}[cor];
    return {t:String(q.n).padStart(2,'0')+(val===undefined?'':' · '+mipN(val)),tt:'Ponto '+q.n+(val===undefined?': não coletado':(': '+mipN(val)+' '+p.un+(q.rec?' · recoleta (fora da média)':'')+(nul?' · no aparelho, sem sinal':''))),
      st:'display:inline-flex;align-items:center;padding:3px 8px;border-radius:7px;font-size:12px;font-weight:700;font-variant-numeric:tabular-nums;color:'+bg[1]+';background:'+bg[0]+';border:1px '+(nul&&pv!==undefined?'dashed':'solid')+' '+(cor==='none'?'#E4E9E5':bg[0])+';'+(q.rec?'text-decoration:line-through;':'')}; });
  const sw=(c0,b)=>({st:'width:11px;height:11px;border-radius:3px;background:'+c0+';'+(b?'border:1px solid '+b+';':''),t:''});
  v.pan_leg=R.crit==='presenca'?[Object.assign(sw('#FFE8D6'),{t:'com sintoma'}),Object.assign(sw('#E4F3E9'),{t:'sem sintoma'}),Object.assign(sw('#fff','#E4E9E5'),{t:'não coletado'})]
    :[Object.assign(sw('#FDE8E6'),{t:'≥ NC'}),Object.assign(sw('#FFF3D6'),{t:'≥ 80 % do NC'}),Object.assign(sw('#E4F3E9'),{t:'abaixo'}),Object.assign(sw('#EEF1EE'),{t:'recoleta'}),Object.assign(sw('#fff','#E4E9E5'),{t:'não coletado'})];
  // decisão e receituário (DIA · REC/RA · O.S.) com a conferência do produto usado
  const reg=[], ral=[], rtr=[]; const d=vv.dec;
  if(dz) reg.push({t:dz.id+' · '+dz.sit+(dz.dec?' · '+dz.dec:''),sub:(dz.hip||'')+(dz.em?' · '+mipBrA(dz.em)+' · '+dz.por:'')+(dz.motivo?' · motivo: '+dz.motivo:''),h:dz.id==='DIA-007'?'AG-03det.dc.html':'AG-03.dc.html',hl:'Diagnósticos'});
  if(d&&d.rec==='REC-014'){ reg.push({t:'REC-014 v2 · em uso nos 30 ha realizados · saldo de 70 ha travado',sub:'KCl por zona + TS nematicida (abamectina) + semente 58 W resistente',h:'AG-04det.dc.html',hl:'Abrir REC-014'});
    rtr.push({t:'Trava legal: TS nematicida (abamectina) sem registro para soja × nematoide-de-cisto. O saldo de 70 ha aguarda a v4 com TS registrado (ex.: Pasteuria nishizawae FS).'}); }
  else if(d&&d.rec&&s.rec[d.rec]){ const r=s.rec[d.rec]; reg.push({t:r.id+' · receituário '+r.ra+' · '+r.sit,sub:r.nome+' '+mipN(r.dose,3)+' '+r.un+'/ha · '+mipN(r.area,2)+' ha · a partir de '+mipBr(r.data)+' · Ana (RT)',h:'AG-07.dc.html#'+r.prod,hl:'Ficha do produto'}); }
  else if(d&&d.ra&&d.prod){ const G=MIPD.grupo[d.prod]||{nome:d.prod,g:''}; reg.push({t:'Receituário '+d.ra+' · '+G.nome,sub:G.g+' · decisão de '+mipBrA(d.em)+' · '+d.por+(d.nota?' · '+d.nota:''),h:'AG-07.dc.html#'+d.prod,hl:'Ficha do produto'}); }
  if(d&&d.os){ const et=mipOsEt(c,d.os)||'—'; const dup=P.h==='OS.dc.html#'+d.os;   // o primário já abre a O.S.: o registro não repete o destino
    reg.push({t:d.os+' · '+et,sub:(d.t==='erradicar'?'erradicação de plantas':'controle')+' · '+mipN(d.area||t.area,2)+' ha',h:dup?'':'OS.dc.html#'+d.os,hl:'Abrir '+d.os}); }
  if(d&&d.prod&&d.os){ const k=mipChecks(s,vv,{kind:'controlar',prod:d.prod,dose:(MIPD.agf[t.cultura+'|'+p.chave]||[]).filter(x=>x.id===d.prod).map(x=>d.dose||x.dmin)[0]||1,area:d.area||t.area,data:d.data||mipAmanha(),os:d.os},c);
    k.al.filter(x=>/^Rotação|^Colheita/.test(x)).forEach(x=>ral.push({t:x})); }
  if(d&&d.t==='monitorar') reg.push({t:'Seguir monitorando · '+mipBrA(d.em)+' · '+d.por,sub:(d.prox?'próxima vistoria '+mipBr(d.prox):'')+(d.nota?' · motivo: '+d.nota:''),h:'',hl:''});
  v.pan_reg=reg.map(r=>Object.assign({hasH:!!r.h},r)); v.pan_regal=ral; v.pan_regtr=rtr; v.ps_reg=reg.length>0;
  // histórico do talhão (vistorias e aplicações com o grupo de modo de ação)
  v.pan_hist=mipHist(s,vv.tal,c).filter(x=>x.t.indexOf(vv.id+' ')!==0).slice(0,8).map(x=>{ const cs2=agCh(x.c); return Object.assign({},x,{d:mipBr(x.d),hasH:!!x.h,noH:!x.h,chst:cs2.st,chdot:cs2.dot}); });
  v.ps_hist=v.pan_hist.length>0; }
// ---------- programar vistoria (talhão → alvo do protocolo → data → responsável) ----------
function agPvOpen(self,tal,prot){ if(!self.state.pan) agGuarda(self); const s=mipGet(); const f=agFaz(self); const faz=tal?MIPD.tal[tal].faz:(f==='Todas'||f==='Boa Vista'?'Santa Rita':f);
  const tals=Object.keys(MIPD.tal).filter(k=>MIPD.tal[k].faz===faz&&(MIPD.prots[k]||[]).length); const t0=tal||tals[0]||'';
  self.setState({pv:{faz,tal:t0,prot:prot||(t0?mipProtPadrao(s,t0):''),data:mipAmanha(),resp:(MIPD.resp[faz]||[''])[0],err:'',ab:''},pan:null,dec:null}); agFoco('pv_tal'); }
function agPv(self,v){ const pv=self.state.pv; v.pv_open=!!pv; const fecha=()=>{ self.setState({pv:null}); agVolta(self,''); };
  v.pv_close=fecha; v.pv_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); fecha(); return; } agTrap(e); };
  if(!pv) return; const s=mipGet(); const up=(p)=>self.setState({pv:Object.assign({},self.state.pv,p,{err:'',ab:''})});
  v.pv_escFaz=agFaz(self)==='Todas'||agFaz(self)==='Boa Vista'; v.pv_faz=pv.faz; v.pv_fazs=['Santa Rita','Lagoa Grande'].map(x=>({v:x,t:x}));
  v.pv_setfaz=(e)=>{ const faz=e.target.value; const t0=Object.keys(MIPD.tal).find(k=>MIPD.tal[k].faz===faz&&(MIPD.prots[k]||[]).length)||''; up({faz,tal:t0,prot:t0?mipProtPadrao(s,t0):'',resp:(MIPD.resp[faz]||[''])[0]}); };
  v.pv_tals=Object.keys(MIPD.tal).filter(k=>MIPD.tal[k].faz===pv.faz&&(MIPD.prots[k]||[]).length).map(k=>{ const t=MIPD.tal[k]; return {v:k,t:t.rot+' · '+t.cultura+' '+t.fase+' · '+mipN(t.area)+' ha'}; });
  v.pv_tal=pv.tal; v.pv_settal=(e)=>{ const t=e.target.value; up({tal:t,prot:mipProtPadrao(s,t)}); };
  v.pv_semTal=!pv.tal; v.pv_prots=(MIPD.prots[pv.tal]||[]).map(k=>({v:k,t:MIPD.prot[k].alvo+' · '+MIPD.prot[k].tipo.toLowerCase()})); v.pv_prot=pv.prot; v.pv_setprot=(e)=>up({prot:e.target.value});
  const p=MIPD.prot[pv.prot], t=MIPD.tal[pv.tal];
  v.pv_resumo=(p&&t)?(p.ver+' · '+p.met+' · '+p.un+' · '+(p.crit==='nc'?'NC '+mipN(mipNC(p,t))+' '+p.un:'critério presença')+' · '+mipPontos(pv.prot,t.area)+' pontos · a cada '+p.inter+' dias'):'Escolha o talhão.';
  v.pv_data=pv.data; v.pv_setdata=(e)=>up({data:e.target.value}); v.pv_resps=(MIPD.resp[pv.faz]||[]).map(x=>({v:x,t:x})); v.pv_resp=pv.resp; v.pv_setresp=(e)=>up({resp:e.target.value});
  v.pv_hasErr=!!pv.err; v.pv_err=pv.err; v.pv_hasAb=!!pv.ab; v.pv_ab=pv.ab; v.pv_abrir=()=>{ const id=self.state.pv.ab; self.setState({pv:null}); agOpen(self,id); };
  v.pv_save=()=>{ const cur=self.state.pv; if(cur.data&&cur.data<MIPD.hoje){ self.setState({pv:Object.assign({},cur,{err:'Data no passado: programe a partir de hoje ('+mipBr(MIPD.hoje)+').'})}); return; }
    const r=mipMudar(null,s2=>mipNovaVis(s2,cur.tal,cur.prot,cur.data,cur.resp,'ag01'));
    if(r.erro){ const m=/^(VIS-\d+) já está aberta/.exec(r.erro); self.setState({pv:Object.assign({},cur,{err:r.erro,ab:m?m[1]:''})}); return; }
    agSetHash(r.id); self.setState(Object.assign({pv:null,pan:r.id,miprev:Date.now(),g2toast:r.msg,mf_faz:(agFaz(self)==='Todas'?'Todas':MIPD.tal[cur.tal].faz)},agInclui(self,{tal:cur.tal}))); agFoco(); }; }
function PREVALS(self,v){ cenOuvir(self); mipOuvir(self); agIni(self); v.mf_faz=agFaz(self); agFazSalvar(self); agTopo(self,v);
  const sp=GRIDS.find(g=>g.id==='g_vis'); sp.rows=agRows(self,v);
  const x0={}; sp.rows.forEach(r=>{ if(r.kids) x0[r.id]=true; }); sp.x0=x0; }
function EXTRAVALS(self,v){ const st=self.state; const s=mipGet(), c=agC(), f=agFaz(self);
  self.g2pick=(gid,rid)=>{ if(gid==='g_vis'&&/^VIS-/.test(rid)) agOpen(self,rid); };
  v.ag_go=(arg)=>{ const a=String(arg).split('|'); agOpen(self,a[0],a[1]); };
  v.ag_grp=st.ag_grp||''; v.ag_grpOn=!!st.ag_grp; v.ag_setgrp=(e)=>{ self.setState({ag_grp:e.target.value}); g2set(self,'g_vis',{x:null}); };
  v.pv_new=()=>agPvOpen(self);
  agPanel(self,v); agPv(self,v);
  // selo do cabeçalho: acima do NC sem decisão e focos a confirmar no recorte da faixa (fazenda, cultura e talhão)
  const vs=Object.values(s.vis).filter(x=>agRec(self,x)).map(x=>mipSit(s,x,c).k);
  const na=vs.filter(k=>k==='acima').length, nf=vs.filter(k=>k==='foco').length, ns=vs.filter(k=>k==='sinc'||k==='incompleta').length;
  v.ag_st=[na?na+' acima do NC sem decisão':'',nf?nf+(nf>1?' focos a confirmar':' foco a confirmar'):'',(!na&&!nf&&ns)?ns+' coleta a completar':''].filter(Boolean).join(' · ')||'Em dia';
  const cs=agCh(na?'red':((nf||ns)?'yellow':'green')); v.ag_stst=cs.st; v.ag_stdot=cs.dot;
  // restaurar a demonstração (vistorias + O.S., estoque e app)
  v.rs_no=!st.rs; v.rs_yes=!!st.rs; v.rs_ask=()=>self.setState({rs:true}); v.rs_cancel=()=>self.setState({rs:false});
  v.rs_ok=()=>{ mipReset(); if(typeof cenReset==='function') cenReset(); agSetHash(''); self.setState({rs:false,pan:null,dec:null,pv:null,miprev:Date.now(),cenrev:Date.now(),g2toast:'Demonstração restaurada: vistorias, O.S., estoque e app voltaram ao início.'}); }; }
'''

def _status_dinamico(fname,pref):
    """troca o selo fixo do cabeçalho por um selo com cor calculada na tela (<pref>_st / _stst / _stdot)."""
    import os, ui37
    p=os.path.join(E.P,fname); s=open(p,encoding='utf-8').read(); old=ui37.chip(H(pref+'_st'),'red')
    assert s.count(old)==1, 'selo do cabeçalho não encontrado em '+fname
    open(p,'w',encoding='utf-8').write(s.replace(old,f'<span style="{H(pref+"_stst")}"><span style="{H(pref+"_stdot")}"></span>{H(pref+"_st")}</span>'))

def _menu_mip():
    """AG-01det, AG-03 e AG-04 (+ detalhes) pertencem ao item Pragas e doenças (MIP/MID) do menu; AG-01 tem o filtro Fazenda no topo."""
    import ui37
    for f in ('AG-03.dc.html','AG-03det.dc.html','AG-04.dc.html','AG-04det.dc.html'): ui37.MENU_OF.setdefault(f,'AG-01.dc.html')
    ui37.MACRO.setdefault('AG-01.dc.html',dict(faz='filtro',cult='filtro',tal='filtro'))   # 13/10: Cultura e Talhão (vistoria é por talhão e cultura)

def ag01():
    import cenario, dados_mip as DM
    DM.verificar()
    _menu_mip()
    fname='AG-01.dc.html'; E._reset_screen(fname)
    # "Pontos" fica na linha de baixo da contagem (coletados/total e recoleta): a grade cabe em 1280 × 800 sem cortar o Próximo passo
    cols=[dict(k='id',l='Vistoria',w=80),dict(k='tal',l='Talhão · cultura',w=130),dict(k='alvo',l='Alvo',w=124),dict(k='cont',l='Contagem × NC',t='num',w=130),
          dict(k='data',l='Data',t='date',w=90),dict(k='sit',l='Situação',w=140),dict(k='prox',l='Próximo passo',w=170)]
    grp=(f'<label style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; color: {MUTED};">Agrupar'
         f'<select aria-label="Agrupar vistorias por" value="{H("ag_grp")}" onChange="{H("ag_setgrp")}" style="font-family: inherit; font-size: 12px; font-weight: 700; padding: 4px 8px; border-radius: 8px; border: 1px solid {LINE}; background: {SURF}; color: {INK};">'
         + ''.join(f'<option value="{k}">{t}</option>' for k,t in (('','Nenhum'),('tal','Talhão'),('alvo','Alvo'),('sit','Situação'),('faz','Fazenda'))) + '</select></label>')
    g=grid(cols,[],edit=dict(m='pick',leafOnly=True),tree=True,gid='g_vis',total=False,tools=grp)
    # filtro rápido por situação, na ordem de gravidade (acima do NC primeiro), com a contagem do recorte da faixa
    chips=(f'<div role="group" aria-label="Filtrar por situação" style="display: flex; flex-wrap: wrap; gap: 6px;"><sc-for list="{H("ag_chips")}" as="q" hint-placeholder-count="5">'
           f'<button type="button" aria-pressed="{H("q.on")}" onClick="{H("q.go")}" style="{H("q.st")}">{H("q.t")} <span style="opacity: .75;">{H("q.n")}</span></button></sc-for></div>')
    corpo=bloco('Vistorias','',f'<div style="display: flex; flex-direction: column; gap: 10px; min-height: 0; flex: 1 1 auto;">{chips}{g}</div>'+_ag01_restaurar())
    EXTRA.append(_ag01_painel()); EXTRA.append(_ag01_programar())
    EXTRAJS[0]=cenario.js_prefixo()+DM.js_prefixo()+JS_AG01
    prim=f'<button type="button" onClick="{H("pv_new")}" style="{BTN_ST(True)} display: inline-flex; align-items: center; gap: 6px;">{icon("calendar",15)}Programar vistoria</button>'
    HEIGHTS37[fname]=1000
    shell37('AG-01','Pragas e doenças',corpo,fname=fname,status=(H('ag_st'),'red'),primary_html=prim,search=False)
    _status_dinamico(fname,'ag')
    # "Expandir tudo" da grade só aparece com as vistorias agrupadas
    import os, re
    p=os.path.join(E.P,fname); s=open(p,encoding='utf-8').read()
    m=re.search(r'<button type="button" onClick="\{\{g_vis_xtog\}\}".*?</button>',s,re.S); assert m, 'botão Expandir tudo não encontrado'
    s=s[:m.start()]+f'<sc-if value="{H("ag_grpOn")}" hint-placeholder-val="{F_()}">'+m.group(0)+'</sc-if>'+s[m.end():]
    open(p,'w',encoding='utf-8').write(s)

JS_AG01DET=r'''
// ===== AG-01det · Rota e evidências da vistoria (#VIS-xxx; padrão VIS-011): rota em W, pontos, série do alvo e fotos =====
function dtVid(self){ let h=''; try{ h=decodeURIComponent(location.hash||''); }catch(e){ h=''; } const m=/^#(VIS-\d+)$/.exec(h); const s=mipGet();
  return (m&&s.vis[m[1]])?m[1]:'VIS-011'; }
function dtIni(self){ if(self.__dt) return; self.__dt=1; try{ window.addEventListener('hashchange',()=>self.setState({dtrev:Date.now()})); }catch(e){} }
function dtCor(R,x,rec){ if(rec) return ['#C9CFCB','#5B6660']; if(x===null||x===undefined) return ['#FFFFFF','#8A968E']; if(R.crit==='presenca') return Number(x)>0?['#D98A4E','#FFFFFF']:['#7FAE68','#FFFFFF'];
  return x>=R.nc?['#C8553D','#FFFFFF']:(x>=0.8*R.nc?['#D4B25A','#FFFFFF']:['#7FAE68','#FFFFFF']); }
function dtGps(t,i,n){ const fr=n>1?i/(n-1):0.5; const dx=(-0.6+1.2*fr)*t.r, dy=((i%2)?-0.35:0.35)*t.r; const lat=t.ll[0]+dy/111320, lon=t.ll[1]+dx/(111320*Math.cos(t.ll[0]*Math.PI/180));
  const f=(x)=>(x<0?'−':'')+Math.abs(x).toFixed(4).replace('.',','); return f(lat)+' · '+f(lon); }
function PREVALS(self,v){ mipOuvir(self); cenOuvir(self); dtIni(self); const s=mipGet(), c=(typeof cenGet==='function')?cenGet():null; const vid=dtVid(self); const vv=s.vis[vid];
  const R=mipRes(vv,s), p=mipP(vv), t=mipT(vv), S=mipSit(s,vv,c), P=mipProx(s,vv,c); const n=vv.npts;
  v.dt_t=vid+' · '+p.alvo+' · '+t.rot; v.dt_res=[t.faz,t.rot,((t.cultura+' '+t.fase).trim()||'sem cultura'),mipN(t.area)+' ha',p.ver,p.met,(vv.est==='programada'?'programada para ':'coleta de ')+mipBrA(vv.data)+' · '+vv.resp].join(' · ');
  const cs=agCh(S.c); v.dt_sit=S.t; v.dt_sst=cs.st; v.dt_sdot=cs.dot; v.dt_ssub=S.sub||''; v.dt_back='AG-01.dc.html#'+vid; v.dt_isDemo=vid==='VIS-011';
  v.dt_kpi=[{l:'Pontos válidos',v:R.val+' de '+R.tot,s:R.rec?R.rec+' em recoleta':(R.falt?R.falt+' sem coleta':'GPS e hora')},
    R.crit==='presenca'?{l:'Pontos com sintoma',v:String(R.pres),s:'critério presença'}:{l:'Média válida',v:R.media===null?'—':mipN(R.media),s:p.un+' · NC '+mipN(R.nc)},
    R.crit==='presenca'?{l:'Plantas com sintoma',v:String(vv.pts.reduce((a,x)=>a+(Number(x.v)||0),0)),s:p.un}:{l:'Pontos ≥ NC',v:String(vv.pts.filter(x=>x.v!==null&&!x.rec&&x.v>=R.nc).length),s:R.reb?R.reb+' de reboleira (≥ 2 × NC)':'nenhuma reboleira'},
    {l:'Evidências',v:(R.col*2)+' fotos',s:'2 por ponto coletado'}];
  // rota em W: pontos alternam as duas metades do talhão, da esquerda para a direita
  const pos=vv.pts.map((q,i)=>{ const x=60+(n>1?i*(880/(n-1)):440); const y=(i%2)?70:230; return [x,y]; });
  v.dt_line=pos.map(q=>q[0]+','+q[1]).join(' ');
  v.dt_dots=vv.pts.map((q,i)=>{ const k=dtCor(R,q.v,q.rec); return {t:String(q.n).padStart(2,'0'),tt:'Ponto '+q.n+(q.v===null||q.v===undefined?': não coletado':': '+mipN(q.v)+' '+p.un+(q.rec?' · recoleta':'')),
    st:'position:absolute;left:'+(pos[i][0]/10)+'%;top:'+(pos[i][1]/3)+'%;transform:translate(-50%,-50%);width:26px;height:26px;border-radius:999px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;background:'+k[0]+';color:'+k[1]+';border:2.5px solid #fff;box-shadow:0 1px 3px rgba(21,32,26,.3);'+((q.v===null||q.v===undefined)?'border:2px dashed #8A968E;':'')}; });
  // tabela de pontos
  const sp=GRIDS.find(g=>g.id==='g_pts'); const ncl=(x,rec)=>rec?'recoleta':(x===null||x===undefined?'não coletado':(R.crit==='presenca'?(Number(x)>0?'com sintoma':'sem sintoma'):(x>=R.nc?'acima do NC':(x>=0.8*R.nc?'perto do NC':'abaixo do NC'))));
  const NCC={'acima do NC':'red','perto do NC':'yellow','abaixo do NC':'green','recoleta':'gray','não coletado':'gray','com sintoma':'orange','sem sintoma':'green'};
  sp.rows=vv.pts.map((q,i)=>{ const col=!(q.v===null||q.v===undefined); const k=ncl(q.v,q.rec); const gm=q.gm||(col?3+(i%4):null);
    return {id:'p'+q.n,v:{pt:String(q.n).padStart(2,'0'),gps:col?(q.gps||dtGps(t,i,n)):'—',hora:col?(q.h||('0'+(7+Math.floor((28+i*8)/60))).slice(-2)+':'+('0'+((28+i*8)%60)).slice(-2)):'—',cont:col?q.v:null,nc:k,fotos:col?2:0},
      s:{nc:k,qual:col?(q.rec?'GPS ±'+gm+' m · fora do talhão':'GPS ±'+gm+' m'):'aguarda coleta'},
      p:{cont:col?[{k:'cn',t:mipN(q.v),c:q.rec?'gray':NCC[k]}]:[{k:'mut',t:'—'}],nc:[{k:'chip',t:k,c:NCC[k]}],qual:[{k:'chip',t:col?(q.rec?'GPS ±'+gm+' m · fora do talhão':'GPS ±'+gm+' m · ok'):'aguarda coleta',c:col?(q.rec?'red':'green'):'gray'}]}}; });
  v.dt_un=p.un; v.dt_nct=R.crit==='presenca'?'Critério presença':'× NC '+mipN(R.nc);
  // série do alvo no talhão (mesmo método e unidade)
  v.dt_serie=Object.values(s.vis).filter(x=>x.tal===vv.tal&&x.prot===vv.prot&&x.est==='concluida').sort((a,b)=>(a.data<b.data?-1:1)).map(x=>{ const r=mipRes(x,s);
    const w=r.crit==='presenca'?(r.val?Math.round(100*r.pres/r.val):0):Math.min(100,Math.round((r.pct||0)*50)); const k=dtCor(r,r.crit==='presenca'?r.pres:r.media,false);
    return {d:mipBrA(x.data),id:x.id,on:x.id===vid?'true':'false',t:r.ctxt+(r.crit==='presenca'?'':' '+p.un),bst:'display:block;height:10px;border-radius:999px;background:'+k[0]+';width:'+Math.max(2,w)+'%;',h:'AG-01det.dc.html#'+x.id,fw:x.id===vid?'800':'600'}; });
  v.dt_hasSerie=v.dt_serie.length>0;
  // fotos: pontos acima do NC (ou com sintoma) e os de recoleta
  v.dt_fotos=vv.pts.filter(q=>q.v!==null&&q.v!==undefined&&(q.rec||(R.crit==='presenca'?q.v>0:q.v>=R.nc))).slice(0,6).map(q=>({t:'Ponto '+String(q.n).padStart(2,'0'),s:mipN(q.v)+' '+p.un+(q.rec?' · recoleta':''),g:q.gps||dtGps(t,q.n-1,n)}));
  v.dt_hasFotos=v.dt_fotos.length>0; v.dt_semFotos=!v.dt_hasFotos;
  // próximo passo: comando sem formulário roda aqui; decidir e programar abrem o formulário no AG-01; link vai ao destino (nunca igual ao Voltar)
  const run={sinc:x=>mipSinc(x,vid),parcial:x=>mipParcial(x,vid),monitorar:x=>mipMonitorar(x,vid,''),pos:x=>mipPos(x,vid)}[P.fn];
  v.dt_pt=P.t; v.dt_ptxt=P.txt; v.dt_hasBtn=!!(P.t&&run); v.dt_go=()=>{ if(run) mipMudar(self,run); };
  v.dt_hasLnk=!!(P.t&&!run); v.dt_ph=P.h||('AG-01.dc.html#'+vid+(P.fn?':'+P.fn:''));
  v.dt_cadOsTxt=!!(v.dt_hasLnk&&v.dt_ph==='OS.dc.html#OS-0420'); v.dt_cadOs=!v.dt_cadOsTxt; }
'''

def ag01det():
    import cenario, dados_mip as DM
    _menu_mip()
    fname='AG-01det.dc.html'; E._reset_screen(fname)
    cp=[dict(k='pt',l='Ponto'),dict(k='gps',l='GPS'),dict(k='hora',l='Hora'),dict(k='cont',l='Contagem',t='num',a='r'),dict(k='nc',l='× NC'),dict(k='fotos',l='Fotos',t='num',a='r'),dict(k='qual',l='Qualidade',w=220)]
    gp=grid(cp,[],edit=dict(m='none'),search=False,gid='g_pts',total=False)
    kpi=(f'<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px;"><sc-for list="{H("dt_kpi")}" as="k" hint-placeholder-count="4">'
         f'<div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; padding: 12px 14px;"><div style="font-size: 10.5px; font-weight: 700; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{H("k.l")}</div>'
         f'<div style="font-family: {DISP}; font-size: 22px; font-weight: 700; margin-top: 2px;">{H("k.v")}</div><div style="font-size: 12px; color: {MUTED};">{H("k.s")}</div></div></sc-for></div>')
    rota=(f'<div style="position: relative; width: 100%; height: 300px; border-radius: 10px; overflow: hidden; background: #E3EBDD;" role="img" aria-label="Rota em W da vistoria">'
          f'<svg viewBox="0 0 1000 300" preserveAspectRatio="none" style="position: absolute; inset: 0; width: 100%; height: 100%;"><rect x="14" y="14" width="972" height="272" rx="18" fill="#B5E61D" fill-opacity=".45" stroke="#fff" stroke-width="3"/>'
          f'<polyline points="{H("dt_line")}" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="6 5" opacity=".55"/></svg>'
          f'<sc-for list="{H("dt_dots")}" as="d" hint-placeholder-count="14"><span title="{H("d.tt")}" style="{H("d.st")}">{H("d.t")}</span></sc-for></div>')
    leg=legend([('#7FAE68','abaixo do NC'),('#D4B25A','perto do NC'),('#C8553D','acima do NC'),('#D98A4E','com sintoma'),('#C9CFCB','recoleta')])
    serie=(f'<sc-if value="{H("dt_hasSerie")}" hint-placeholder-val="{T_()}"><div style="display: flex; flex-direction: column; gap: 6px;"><sc-for list="{H("dt_serie")}" as="x" hint-placeholder-count="2">'
           f'<div aria-current="{H("x.on")}" style="display: grid; grid-template-columns: 90px 80px minmax(0, 1fr) 150px; gap: 10px; align-items: center; font-size: 13px;">'
           f'<span style="color: {MUTED};">{H("x.d")}</span><a href="{H("x.h")}" style="color: {ACC}; font-weight: {H("x.fw")}; text-decoration: none;">{H("x.id")}</a>'
           f'<span style="display: block; background: #EEF1EE; border-radius: 999px;"><span style="{H("x.bst")}"></span></span><span style="font-weight: 700; text-align: right; font-variant-numeric: tabular-nums;">{H("x.t")}</span></div></sc-for></div></sc-if>')
    fotos=(f'<sc-if value="{H("dt_hasFotos")}" hint-placeholder-val="{T_()}"><div style="display: flex; gap: 10px; flex-wrap: wrap;"><sc-for list="{H("dt_fotos")}" as="f" hint-placeholder-count="3">'
           f'<div style="flex: 1 1 160px; max-width: 220px; border: 1px solid {LINE}; border-radius: 12px; overflow: hidden; background: {BG};">'
           f'<div style="height: 84px; background: linear-gradient(135deg, {ACCS}, {GRAYS}); display: flex; align-items: center; justify-content: center;">{icon("map",26,MUTED)}</div>'
           f'<div style="padding: 8px 10px; font-size: 11.5px; color: {MUTED};"><b style="color: {INK};">{H("f.t")}</b> · {H("f.s")}<br>GPS {H("f.g")}</div></div></sc-for></div></sc-if>'
           f'<sc-if value="{H("dt_semFotos")}" hint-placeholder-val="{F_()}"><div style="font-size: 13px; color: {MUTED};">Sem ponto acima do NC ou em recoleta.</div></sc-if>')
    cab=(f'<div style="display: flex; flex-direction: column; gap: 6px;"><div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">'
         f'<h2 style="margin: 0; font-family: {DISP}; font-size: 18px; font-weight: 700;">{H("dt_t")}</h2>{_ch("dt_sit","dt_sst","dt_sdot")}<span style="font-size: 12.5px; color: {MUTED};">{H("dt_ssub")}</span></div>'
         f'<div style="font-size: 13px; color: {MUTED};">{H("dt_res")}</div><div style="font-size: 13px; line-height: 1.45;"><b>Próximo passo:</b> {H("dt_ptxt")}</div></div>')
    corpo=(cab + f'<sc-if value="{H("dt_isDemo")}" hint-placeholder-val="{F_()}">' + cadeia('VIS-011','','',vivo={'OS.dc.html#OS-0420':'dt_cadOs'}) + '</sc-if>'
      + kpi
      + bloco('Rota em W e pontos','',rota+leg+gp)
      + bloco('Série do alvo no talhão','',serie)
      + bloco('Evidências com GPS e hora','',fotos))
    EXTRAJS[0]=cenario.js_prefixo()+DM.js_prefixo()+JS_AG01.split('// ---------- formulário de decisão')[0].split('function agRow(')[0]+JS_AG01DET
    prim=(f'<sc-if value="{H("dt_hasLnk")}" hint-placeholder-val="{T_()}"><a href="{H("dt_ph")}" style="{BTN_ST(True)} display: inline-flex; align-items: center; gap: 6px; text-decoration: none;">{icon("leaf",15)}{H("dt_pt")}</a></sc-if>'
          f'<sc-if value="{H("dt_hasBtn")}" hint-placeholder-val="{F_()}"><button type="button" onClick="{H("dt_go")}" style="{BTN_ST(True)} display: inline-flex; align-items: center; gap: 6px;">{icon("leaf",15)}{H("dt_pt")}</button></sc-if>')
    HEIGHTS37[fname]=1500; PARENT37[fname]='AG-01.dc.html'
    shell37('AG-01','Rota e evidências',corpo,fname=fname,crumbs_extra=['Rota e evidências'],primary_html=prim,search=False)
    import os
    p=os.path.join(E.P,fname); s=open(p,encoding='utf-8').read()
    old='<a href="AG-01.dc.html" aria-label="Voltar"'; assert s.count(old)==1, 'voltar do AG-01det não encontrado'
    open(p,'w',encoding='utf-8').write(s.replace(old,f'<a href="{H("dt_back")}" aria-label="Voltar"'))

# ================= AG-07 · Consulta Agrofit (menu Agrícola, antes de Planos agronômicos) =================
# Base REAL (02/10/2026): os 4.409 produtos formulados com registro ativo nos dados abertos do AGROFIT/MAPA (CC-BY), processados por
# dados_agrofit/processar.py em JSON servidos ao lado da página (a página busca './agrofit_*.json'; funciona sem internet externa).
# Carga: meta → índice (lista pronta) → 6 fatias de usos por cultura em segundo plano (busca por praga, filtro de alvo, usos da ficha,
# rotação) → LMR da ANVISA ao abrir a primeira ficha. Todos os arquivos têm o mesmo "versao"; divergência = base em troca no servidor
# (recarrega uma vez, depois erro com "Tentar de novo").
# Listagem: grade G2 (ordenar e filtrar no cabeçalho, agrupar) com render incremental (50 linhas + "Mostrar mais"); busca sem acento
# em produto, registro, ingrediente, grupo químico, titular, classe e modo de ação, e — palavra a palavra — num MESMO uso (cultura e
# alvo juntos). Filtros: Cultura (combobox, culturas da fazenda primeiro; "Todas as culturas" do AGROFIT vale para qualquer cultura),
# Praga-alvo (aparece com a cultura), Classe por componente (+ Biológico) e Orgânicos.
# Ficha (painel lateral): uso (cultura × alvo) → "Usar na O.S." (CTL-5 · RL-E3: a consulta não emite receituário; leva produto da fazenda,
# cultura e alvo ao "Ajustar antes de liberar" da ordem A liberar escolhida, onde a liberação confere a regra legal única e grava a aprovação);
# usos registrados; rotação (mesma cultura × alvo, OUTRO MODO DE AÇÃO pelo código IRAC/FRAC/HRAC de referência de cada ingrediente,
# agrofit_dados.GRUPO_RESIST; multissítio já presente não conta como rotação); LMR ANVISA da cultura (vermelho só se NÃO autorizado);
# na fazenda (ao vivo, pelo cenário); referência conferida em bula (agrofit_dados, mesma combinação de ingredientes); registro; link oficial.
# Links: AG-07.dc.html#reg-<NR_REGISTRO> abre a ficha; os antigos AG-07.dc.html#<id da ficha da fazenda> (O.S., MIP) abrem a lista
# filtrada pelo mesmo ingrediente (ou a ficha, quando só há um registro) com a faixa "Da fazenda" e a referência conferida (dose,
# carência, alertas) logo abaixo dela.
import os as _os, shutil as _sh
AGF_ID='g_agf'
AGF_CULTURAS=['Soja','Milho','Feijão','Café','Mamão']
# Praga-alvo (pedido do proprietário, 09/10/2026: "na consulta agrofit tem que aparecer colunas das pragas alvo"): com a cultura escolhida a
# lista tem uma linha por USO na cultura (produto × praga-alvo, como no AGROFIT), lida dos usos registrados (agrofit_usos_cultura_*.json) e dos
# alvos do agrofit_indice.json (nada inventado): Praga-alvo (nomes comuns; coluna multivalorada, o filtro marca o nome) e Nome científico, uma
# variável por coluna, com filtro e ordenação no cabeçalho; "Cultura do uso" separa o uso registrado na cultura do uso em "Todas as culturas".
# Sem cultura, a lista continua com uma linha por produto (AGF_COLS_P, as 6 colunas do desenho).
AGF_COLS_P=[dict(k='prod',l='Produto · registro',w=170),dict(k='ing',l='Ingrediente ativo · grupo químico',w=180),dict(k='cls',l='Classe · modo de ação',w=130),
            dict(k='cult',l='Culturas',t='num',w=115),dict(k='alvo',l='Alvos',t='num',w=125,multi=True),dict(k='tox',l='Tox · amb',w=120),dict(k='faz',l='Na fazenda',t='num',w=125)]
# Alvos (proprietário, 13/10/2026: "coloque coluna dos alvos na planilha/modos de visão"): sem cultura, cada produto mostra quantos alvos tem
# registrados e os mais frequentes (nomes comuns do AGROFIT, lidos dos usos); o filtro do cabeçalho escolhe pelo nome do alvo.
AGF_COLS_U=[dict(k='prod',l='Produto · registro',w=170),dict(k='alvo',l='Praga-alvo',w=170,multi=True),dict(k='cien',l='Nome científico',w=160),
            dict(k='ucul',l='Cultura do uso',w=110),dict(k='ing',l='Ingrediente ativo · grupo químico',w=180),dict(k='cls',l='Classe · modo de ação',w=130),
            dict(k='tox',l='Tox · amb',w=120),dict(k='faz',l='Na fazenda',t='num',w=125)]
AGF_DIR=_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),'dados_agrofit','site')
# arquivos que a página busca (publicar ao lado de AG-07.dc.html); os de produto e de técnicos ficam só no servidor
def agf_arquivos():
    meta=json.load(open(_os.path.join(AGF_DIR,'agrofit_meta.json'),encoding='utf-8'))
    n=meta['contagens']['fatias_cultura']
    return ['agrofit_meta.json','agrofit_indice.json','agrofit_lmr.json']+[f'agrofit_usos_cultura_{i}.json' for i in range(n)]

def _nd(x):
    s=('%.3f'%float(x)).rstrip('0').rstrip('.')
    return s.replace('.',',')

def agf_dados():
    """Dados embutidos: fichas da fazenda (referência conferida em bula + elo Na fazenda), grupos de resistência por ingrediente e
    planos que usam cada ficha. A base real vem dos JSON (fetch)."""
    import agrofit_dados as A
    import dados2 as D2
    ind=json.load(open(_os.path.join(AGF_DIR,'agrofit_indice.json'),encoding='utf-8'))
    falta=A.confere_agrofit(ind)
    assert not falta, f'AGROFIT_INGREDIENTES com nome ausente do índice real: {falta}'
    nome2id={n:p['id'] for p in A.PRODUTOS for n in p['nomes_fazenda']}
    planos={}
    for pl in D2.PLANOS:
        for a in pl['atividades']:
            for x in a['prods']:
                pid=nome2id.get(x['prod'])
                if pid: planos.setdefault(pid,[]).append(dict(id=pl['id'],nome=pl['nome'],atv=a['nome'],dose=f"{_nd(x['dose'])} {x['un']}/ha"))
    K=('id','nome','nomes_fazenda','ingrediente','concentracao','formulacao','classe','grupos','grupo','grupo_nome','situacao','situacao_nota',
       'avisos','alertas_fazenda','refs_fazenda')
    ref=[]
    for p in A.PRODUTOS:
        d={k:p[k] for k in K}
        d['usos']=[{k:u[k] for k in ('cultura','alvo','dose','carencia','max_aplic','intervalo','conferido')} for u in p['usos']]
        d['agrofit']=A.AGROFIT_INGREDIENTES[p['id']]; d['conc']=A.conc_num(p); d['sem']=A.SEM_REGISTRO.get(p['id'],'')
        ref.append(d)
    # grupo de resistência (IRAC/FRAC/HRAC) de TODOS os ingredientes químicos: a rotação compara o código, não o rótulo do AGROFIT
    gref=[[[_agf_norm(n) for n in ns],c] for ns,c in A.GRUPO_RESIST]
    lac=A.lacunas_resist(ind)
    if lac: print(f'AVISO AG-07: {len(lac)} ingrediente(s) químico(s) sem código IRAC/FRAC/HRAC (rotação cai no grupo químico): {lac[:12]}')
    # produtos que a O.S. aceita no "Incluir produto" (o mesmo catálogo da tela O.S.: plano + lotes): "Usar na O.S." só oferece estes (CTL-5)
    from areas.processo_os import _nova_ordem_dados, _ordens
    osp=sorted({x['p'] for x in _nova_ordem_dados()['prods']})
    osop={o['id']:o['atv']['op'] for o in _ordens()}   # operação de cada ordem do registro (ordem nova: osc.novo.atv.op): "Usar na O.S." só em pulverização (CTL-5, S3-1)
    return dict(ref=ref,osp=osp,osop=osop,grupos={k:list(v) for k,v in A.GRUPOS_RESIST.items()},grupo_ref=gref,gq_gen=[_agf_norm(g) for g in A.GQ_GENERICOS],
                planos=planos,culturas=AGF_CULTURAS,consulta=A.CONSULTA['data'],oficial=A.CONSULTA['link'])

def _agf_norm(s):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c)).strip()

_LAB=lambda t: f'<span style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{t}</span>'

def _agf_fonte(link):
    return (f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 12.8px; color: {MUTED}; margin-top: -4px;">'
            f'<span>{H("agf_fonte")}</span>'
            f'<a href="{link}" target="_blank" rel="noopener" style="color: {ACC}; font-weight: 700; text-decoration: none;">Abrir no AGROFIT oficial ›</a></div>')

def _agf_filtros():
    chips=(f'<div role="group" aria-label="Filtrar por classe" style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px;">'
           f'<span style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase; min-width: 58px;">Classe</span>'
           f'<sc-for list="{H("agf_clsL")}" as="qc" hint-placeholder-count="6"><button type="button" aria-pressed="{H("qc.on")}" title="{H("qc.lab")}" onClick="{H("qc.go")}" style="{H("qc.st")}">'
           f'{H("qc.t")} <span style="opacity: .75;">{H("qc.n")}</span></button></sc-for>'
           f'<sc-if value="{H("agf_temClsO")}" hint-placeholder-val="{T_()}"><select aria-label="Outras classes" value="{H("agf_clsO")}" onChange="{H("agf_setClsO")}" style="{H("agf_clsOSt")}">'
           f'<sc-for list="{H("agf_clsOs")}" as="o" hint-placeholder-count="4"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></sc-if></div>')
    # um campo de busca por tela (proprietário, 13/10/2026: "quero somente 1 campo de busca por tela. 2 fica confuso"): Cultura e Praga-alvo
    # viram listas de escolha (sem digitar); a busca de texto da tela é só a da lista. Culturas da fazenda primeiro.
    SELF=f'font-family: inherit; font-size: 14px; padding: 8px 10px; border-radius: 9px; border: 1px solid {LINE}; background: {SURF}; color: {INK}; max-width: 100%; min-height: 44px;'   # alvo de 44 px (NAV-2CB-TOQUE-01)
    cul=(f'<div style="display: flex; flex-direction: column; gap: 4px;">{_LAB("Cultura")}<select aria-label="Cultura" value="{H("agf_culV")}" onChange="{H("agf_setCul")}" style="{SELF} width: 250px;">'
         f'<option value="">{H("agf_cul0")}</option>'
         f'<optgroup label="Na fazenda"><sc-for list="{H("agf_culFaz")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></optgroup>'
         f'<optgroup label="Outras culturas"><sc-for list="{H("agf_culOut")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></optgroup></select></div>')
    alvo=(f'<sc-if value="{H("agf_temCul")}" hint-placeholder-val="{F_()}"><div style="display: flex; flex-direction: column; gap: 4px;">{_LAB("Praga-alvo")}'
          f'<select aria-label="Praga-alvo" value="{H("agf_alV")}" onChange="{H("agf_setAl")}" style="{SELF} width: 330px;"><sc-for list="{H("agf_alOpts")}" as="o" hint-placeholder-count="3">'
          f'<option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></div></sc-if>')   # o mesmo rótulo da coluna (revisão de 10/10, A6)
    org=(f'<div style="display: flex; flex-direction: column; gap: 4px;">{_LAB("Orgânicos")}<button type="button" aria-pressed="{H("agf_orgOn")}" onClick="{H("agf_orgTog")}" '
         f'title="Mostrar só produtos marcados como aprovados para agricultura orgânica no AGROFIT" style="{H("agf_orgSt")}">Aprovados para orgânicos <span style="opacity: .75;">{H("agf_orgN")}</span></button></div>')
    faixa=lambda cond,bg,t,d,bt,go: (f'<sc-if value="{H(cond)}" hint-placeholder-val="{F_()}"><div role="status" style="display: flex; align-items: baseline; flex-wrap: wrap; gap: 4px 10px; '
         f'padding: 9px 12px; border-radius: 10px; font-size: 13px; line-height: 1.45; {H(bg)}"><b>{H(t)}</b><span style="flex: 1 1 320px;">{H(d)}</span>'
         f'<button type="button" onClick="{H(go)}" style="{_MINI}">{bt}</button></div></sc-if>')
    uso=(f'<sc-if value="{H("agf_uLoad")}" hint-placeholder-val="{F_()}"><div role="status" style="font-size: 12.5px; color: {MUTED};">Carregando culturas e alvos dos usos registrados… '
         f'a busca por praga e o filtro de alvo entram em instantes.</div></sc-if>'
         f'<sc-if value="{H("agf_uErro")}" hint-placeholder-val="{F_()}"><div role="alert" style="display: flex; flex-direction: row; align-items: center; gap: 10px; flex-wrap: wrap; font-size: 12.8px; font-weight: 600; color: {RED};">'
         f'Os usos registrados (culturas e alvos) não carregaram: {H("agf_uErrT")}<button type="button" onClick="{H("agf_uRetry")}" style="{_MINI}">Tentar de novo</button></div></sc-if>')
    td=(f'<sc-if value="{H("agf_hasTD")}" hint-placeholder-val="{F_()}"><div role="status" style="display: flex; align-items: baseline; flex-wrap: wrap; gap: 4px 12px; font-size: 12.8px; line-height: 1.45; color: {MUTED};">'
        f'<span>{H("agf_tdT")}</span><button type="button" onClick="{H("agf_tdTog")}" style="border: 0; background: transparent; padding: 0; font-family: inherit; font-size: 12.8px; font-weight: 700; color: {ACC}; cursor: pointer;">{H("agf_tdBt")} ›</button></div></sc-if>')
    # link antigo da O.S./MIP (#<ficha da fazenda>): quem chega quer conferir dose, carência e alertas do produto da fazenda → a referência
    # conferida aparece aqui, antes da lista dos registros com o mesmo ingrediente
    refc=(f'<sc-if value="{H("agf_hasRefC")}" hint-placeholder-val="{F_()}"><div role="region" aria-label="Referência conferida em bula" style="display: flex; flex-direction: column; gap: 8px;">'
          f'{_LAB("Referência conferida em bula · dose, carência e alertas da fazenda")}'
          f'<span style="font-size: 12.8px; color: {MUTED}; line-height: 1.45;">Conferida em bula pública de produto com os mesmos ingredientes ativos; a bula de cada registro abaixo está no AGROFIT oficial.</span>'
          + _agf_cref('agf_rc') + '</div></sc-if>')
    return (f'<div style="display: flex; flex-direction: column; gap: 10px;">'
            f'<div style="display: flex; flex-wrap: wrap; align-items: flex-start; gap: 10px 16px;">{cul}{alvo}{org}</div>{td}{chips}{uso}'
            + faixa('agf_hasRef','agf_refSt','agf_refT','agf_refD','Mostrar todos os produtos','agf_refX') + refc
            + faixa('agf_hasMiss','agf_missSt','agf_missT','agf_missD','Fechar aviso','agf_missX') + '</div>')

def _agf_tools():
    sel=(f'font-family: inherit; font-size: 12px; font-weight: 700; padding: 4px 8px; border-radius: 999px; border: 1px solid {LINE}; '
         f'background: {SURF}; color: {INK}; cursor: pointer; max-width: 100%; min-width: 0; text-overflow: ellipsis;')   # encolhe no estreito (390 px)
    return (f'<label style="display: inline-flex; flex-wrap: wrap; align-items: center; gap: 6px; max-width: 100%; min-width: 0; font-size: 12px; font-weight: 700; color: {MUTED};">Agrupar por'
            f'<select aria-label="Agrupar por" value="{H("agf_gb")}" onChange="{H("agf_setgb")}" style="{sel}">'
            f'<sc-for list="{H("agf_gbs")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label>'
            f'<sc-if value="{H("agf_grouped")}" hint-placeholder-val="{F_()}"><button type="button" class="g2xtog" onClick="{H(AGF_ID+"_xtog")}">'   # expandir/recolher global: texto discreto (v3.1)
            f'{E.seta_xtog(H(AGF_ID+"_xup"),H(AGF_ID+"_xdown"))}{H(AGF_ID+"_xlab")}</button></sc-if>')

def _agf_estados():
    """carregando (com o tamanho da base) e erro com "Tentar de novo"; a lista só aparece com o índice carregado."""
    return (f'<sc-if value="{H("agf_loading")}" hint-placeholder-val="{T_()}"><div role="status" aria-live="polite" style="flex: 0 0 auto; display: flex; flex-direction: column; gap: 10px; padding: 18px; '
            f'background: {SURF}; border: 1px solid {LINE}; border-radius: 14px;"><b style="font-size: 14px;">{H("agf_loadT")}</b>'
            f'<span style="font-size: 12.8px; color: {MUTED};">Os arquivos ficam no próprio site e são lidos uma vez por sessão.</span>'
            f'<div style="height: 6px; border-radius: 999px; background: {BG}; overflow: hidden;"><div style="width: 40%; height: 100%; background: {ACC}; opacity: .55;"></div></div></div></sc-if>'
            f'<sc-if value="{H("agf_erro")}" hint-placeholder-val="{F_()}"><div role="alert" style="flex: 0 0 auto; display: flex; flex-direction: row; align-items: center; gap: 12px; flex-wrap: wrap; padding: 16px 18px; '
            f'background: {REDS}; border: 1px solid #F4C7C1; border-radius: 14px; color: {RED}; font-size: 13.5px; font-weight: 600;">'
            f'<span style="flex: 1 1 auto; min-width: 280px;">Não foi possível carregar a base do AGROFIT: {H("agf_errT")}.</span>'
            f'<button type="button" onClick="{H("agf_retry")}" style="{BTN_ST(True,True)}">Tentar de novo</button></div></sc-if>')

def _agf_mais():
    return (f'<sc-if value="{H("agf_temMais")}" hint-placeholder-val="{F_()}"><div style="display: flex; align-items: center; justify-content: center; gap: 12px; padding: 2px 0 6px;">'
            f'<span style="font-size: 12.5px; color: {MUTED}; font-variant-numeric: tabular-nums;">{H("agf_maisT")}</span>'
            f'<button type="button" onClick="{H("agf_mais")}" style="{_MINI}">Mostrar mais {H("agf_maisN")}</button></div></sc-if>')

def _agf_cref(lst):
    """Cartões da referência conferida em bula (usos com dose e carência, avisos, alertas da fazenda): ficha e faixa \"Da fazenda\"."""
    chp=lambda t,st,dot: f'<span style="{H(st)}"><span style="{H(dot)}"></span>{H(t)}</span>'
    MUT=f'font-size: 12.8px; color: {MUTED}; line-height: 1.45;'
    TH=f'font-size: 10.5px; font-weight: 700; letter-spacing: .04em; color: {MUTED}; text-transform: uppercase;'
    UT='minmax(0,.7fr) minmax(0,1.6fr) minmax(0,1.1fr) minmax(0,.9fr) 64px minmax(0,.8fr)'
    return (f'<sc-for list="{H(lst)}" as="c" hint-placeholder-count="1"><div style="display: flex; flex-direction: column; gap: 6px; padding: 10px 12px; border: 1px solid {LINE}; border-radius: 12px;">'
          f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px;"><b style="font-size: 13.5px;">{H("c.t")}</b><span style="{MUT}">{H("c.sub")}</span>'
          f'<sc-for list="{H("c.chips")}" as="k" hint-placeholder-count="1">{chp("k.t","k.st","k.dot")}</sc-for></div>'
          f'<div style="font-size: 12.8px;"><b>{H("c.g")}</b> <span style="color: {MUTED};">{H("c.gn")}</span></div>'
          f'<div role="table" aria-label="Usos conferidos" style="display: flex; flex-direction: column;"><div role="row" style="display: grid; grid-template-columns: {UT}; gap: 10px; padding: 4px 0; {TH}">'
          f'<span role="columnheader">Cultura</span><span role="columnheader">Alvo</span><span role="columnheader">Dose</span><span role="columnheader">Carência</span><span role="columnheader" style="text-align: right;">Máx.</span><span role="columnheader">Intervalo</span></div>'
          f'<sc-for list="{H("c.usos")}" as="u" hint-placeholder-count="2"><div role="row" style="display: grid; grid-template-columns: {UT}; gap: 10px; align-items: start; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 12.5px; line-height: 1.4;">'
          f'<span role="cell"><b>{H("u.c")}</b></span><span role="cell">{H("u.a")}<sc-if value="{H("u.nc")}" hint-placeholder-val="{F_()}"> <span style="padding: 0 6px; border-radius: 999px; font-size: 11px; font-weight: 700; color: {YEL}; background: {YELS};">não conferido</span></sc-if></span>'
          f'<span role="cell">{H("u.d")}</span><span role="cell">{H("u.car")}</span><span role="cell" style="text-align: right;">{H("u.max")}</span><span role="cell">{H("u.int")}</span></div></sc-for></div>'
          f'<sc-for list="{H("c.avisos")}" as="w" hint-placeholder-count="0"><div style="font-size: 12.5px; line-height: 1.45;">• {H("w.t")}</div></sc-for>'
          f'<sc-for list="{H("c.alertas")}" as="al" hint-placeholder-count="0"><div style="padding: 6px 10px; border-radius: 8px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 600; line-height: 1.45;"><b>{H("al.ref")}</b> {H("al.t")}</div></sc-for>'
          f'</div></sc-for>')

def _agf_painel(link):
    lab=lambda t: f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{t}</div>'
    sub=lambda t: f'<div style="font-size: 12.5px; font-weight: 800; color: {INK}; padding-top: 4px;">{t}</div>'
    chp=lambda t,st,dot: f'<span style="{H(st)}"><span style="{H(dot)}"></span>{H(t)}</span>'
    def sec(titulo,corpo,rot=None):
        return (f'<section aria-label="{titulo}" style="display: flex; flex-direction: column; gap: 8px; padding-top: 14px; border-top: 1px solid {LINE};">'
                f'{lab(rot or titulo)}{corpo}</section>')
    LK=f'color: {ACC}; font-weight: 700; text-decoration: none; font-size: 13px; white-space: nowrap;'
    BL=f'border: 0; background: transparent; padding: 0; font-family: inherit; font-size: 13px; font-weight: 700; color: {ACC}; cursor: pointer; text-align: left;'
    MUT=f'font-size: 12.8px; color: {MUTED}; line-height: 1.45;'
    TH=f'font-size: 10.5px; font-weight: 700; letter-spacing: .04em; color: {MUTED}; text-transform: uppercase;'
    SEL=f'font-family: inherit; font-size: 13px; padding: 7px 10px; border-radius: 9px; border: 1px solid {LINE}; background: {SURF}; color: {INK}; min-width: 0; max-width: 100%;'
    def tabela(rot,tpl,cab,lst,var,celulas,n=2):
        head=''.join(f'<span role="columnheader" style="{"text-align: right;" if r else ""}">{c}</span>' for c,r in cab)
        return (f'<div role="table" aria-label="{rot}" style="display: flex; flex-direction: column;">'
                f'<div role="row" style="display: grid; grid-template-columns: {tpl}; gap: 10px; padding: 4px 0; {TH}">{head}</div>'
                f'<sc-for list="{H(lst)}" as="{var}" hint-placeholder-count="{n}"><div role="row" style="display: grid; grid-template-columns: {tpl}; gap: 10px; '
                f'align-items: start; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 12.8px; line-height: 1.4; font-variant-numeric: tabular-nums;">{celulas}</div></sc-for></div>')
    cel=lambda x,r=False,b=False: (f'<span role="cell" style="min-width: 0;{" text-align: right;" if r else ""}">' + (f'<b>{x}</b>' if b else x) + '</span>')
    se=lambda c,corpo,ph='false': f'<sc-if value="{H(c)}" hint-placeholder-val="{{{{{ph}}}}}">{corpo}</sc-if>'
    # próximo passo: uso (cultura × alvo) → "Usar na O.S." (CTL-5 · RL-E3): a consulta não emite receituário; o produto da fazenda, a cultura e o
    # alvo vão para o "Ajustar antes de liberar" da ordem A liberar escolhida (só as da cultura), onde a liberação confere a regra legal única
    passo=(f'<div role="region" aria-label="Próximo passo" style="display: flex; flex-direction: column; gap: 10px; padding: 12px 14px; background: {BG}; border-radius: 12px;">'
           f'<div style="display: flex; flex-wrap: wrap; align-items: flex-end; gap: 10px 12px;">'
           f'<label style="display: flex; flex-direction: column; gap: 4px; flex: 1 1 200px; min-width: 0; font-size: 12px; font-weight: 600; color: {MUTED};">Cultura'
           f'<select aria-label="Cultura do uso" value="{H("af_cul")}" onChange="{H("af_setcul")}" style="{SEL}"><sc-for list="{H("af_culs")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label>'
           f'<label style="display: flex; flex-direction: column; gap: 4px; flex: 2 1 260px; min-width: 0; font-size: 12px; font-weight: 600; color: {MUTED};">Praga-alvo'
           f'<select aria-label="Alvo do uso" value="{H("af_alvo")}" onChange="{H("af_setalvo")}" disabled="{H("af_alvoDis")}" style="{SEL}"><sc-for list="{H("af_alvos")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label></div>'
           f'<div style="display: flex; flex-wrap: wrap; align-items: flex-end; gap: 10px 12px;">'
           + se('af_hasPf',f'<label style="display: flex; flex-direction: column; gap: 4px; flex: 1 1 200px; min-width: 0; font-size: 12px; font-weight: 600; color: {MUTED};">Produto da fazenda'
                f'<select aria-label="Produto da fazenda" value="{H("af_pf")}" onChange="{H("af_setpf")}" style="{SEL}"><sc-for list="{H("af_pfs")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label>')
           + f'<label style="display: flex; flex-direction: column; gap: 4px; flex: 2 1 260px; min-width: 0; font-size: 12px; font-weight: 600; color: {MUTED};">Ordem A liberar'
           f'<select aria-label="Ordem A liberar" value="{H("af_ord")}" onChange="{H("af_setord")}" disabled="{H("af_ordDis")}" style="{SEL}"><sc-for list="{H("af_ords")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label>'
           f'<button type="button" onClick="{H("af_usar")}" disabled="{H("af_usarDis")}" title="Abrir a ordem em Ajustar antes de liberar com este produto incluído" style="{BTN_ST(True,True)} {H("af_usarSt")}">Usar na O.S.</button></div>'
           + f'<div role="status" style="{MUT}">{H("af_dica")}</div></div>')
    # usos registrados (por cultura; com a cultura escolhida, os alvos dela)
    usos=(f'<input type="search" aria-label="Filtrar usos por cultura ou alvo" placeholder="Filtrar cultura ou alvo…" value="{H("af_q")}" onChange="{H("af_setq")}" '
          f'style="font-family: inherit; font-size: 13px; padding: 7px 10px; border: 1px solid {LINE}; border-radius: 9px; max-width: 340px;">'
          + se('af_usosLoad',f'<div role="status" style="{MUT}">Carregando os usos registrados…</div>')
          + f'<div role="table" aria-label="{H("af_usosL")}" style="display: flex; flex-direction: column;">'
          f'<div role="row" style="display: grid; grid-template-columns: {H("af_usosTpl")}; gap: 10px; padding: 4px 8px; {TH}">'
          f'<sc-for list="{H("af_usosCab")}" as="h" hint-placeholder-count="3"><span role="columnheader" aria-sort="{H("h.sort")}" style="min-width: 0;">'
          f'<button type="button" onClick="{H("h.go")}" title="{H("h.tt")}" style="border: 0; background: transparent; padding: 0; font: inherit; color: inherit; letter-spacing: inherit; text-transform: inherit; cursor: pointer; text-align: left;">{H("h.l")} <span aria-hidden="true" style="{H("h.ast")}">{H("h.seta")}</span></button></span></sc-for>'
          f'<span role="columnheader" aria-label="Ação"></span></div>'
          f'<sc-for list="{H("af_usos")}" as="u" hint-placeholder-count="3"><div role="row" style="display: grid; grid-template-columns: {H("af_usosTpl")}; gap: 10px; align-items: baseline; padding: 7px 8px; border-top: 1px solid {LINE}; font-size: 12.8px; line-height: 1.4; {H("u.st")}">'
          f'<sc-for list="{H("u.cs")}" as="x" hint-placeholder-count="3"><span role="cell" style="min-width: 0; overflow-wrap: anywhere; {H("x.st")}">{H("x.t")}</span></sc-for>'
          f'<span role="cell"><button type="button" onClick="{H("u.go")}" aria-label="{H("u.lab")}" style="{BL} font-size: 12.5px; white-space: nowrap;">{H("u.bt")} ›</button></span></div></sc-for></div>'
          + se('af_usosVazio',f'<div style="{MUT}">Nenhum uso com “{H("af_q")}”.</div>')
          + se('af_usosMais',f'<button type="button" onClick="{H("af_usosTodos")}" style="{BL}">Mostrar todos ({H("af_usosN")}) ›</button>'))
    # rotação: mesma cultura × alvo, outro grupo químico (e outro grupo de resistência quando conhecido)
    rot=(se('af_rotHint',f'<div style="{MUT}">{H("af_rotHintT")}</div>','true')
         + se('af_hasRot',f'<div style="font-size: 13px; line-height: 1.45;">{H("af_rotRes")}</div>'
              f'<div role="list" aria-label="Alternativas de outro modo de ação" style="display: flex; flex-direction: column;">'
              f'<sc-for list="{H("af_rotG")}" as="r" hint-placeholder-count="2"><div role="listitem" style="display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1.6fr); gap: 10px; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 12.8px; line-height: 1.4;">'
              f'<span style="min-width: 0;"><b>{H("r.t")}</b><br><span style="color: {MUTED};">{H("r.n")}</span></span><span style="display: flex; flex-wrap: wrap; gap: 4px 14px; align-items: baseline;">'
              f'<sc-for list="{H("r.ps")}" as="a" hint-placeholder-count="2"><button type="button" onClick="{H("a.go")}" title="{H("a.lab")}" style="{BL} font-size: 12.8px;">{H("a.t")} ›</button></sc-for>'
              f'<span style="color: {MUTED};">{H("r.mais")}</span></span></div></sc-for></div>'
              f'<div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;"><button type="button" onClick="{H("af_rotVer")}" style="{BL}">Ver todos para este alvo na lista ›</button>'
              f'<span style="{MUT}">{H("af_rotNota")}</span></div>'))
    # LMR ANVISA da cultura escolhida
    LT='minmax(0,1.1fr) minmax(0,2fr)'
    lmr=(se('af_lmrHint',f'<div style="{MUT}">{H("af_lmrHintT")}</div>','true')
         + se('af_lmrErro',f'<div role="alert" style="display: flex; flex-direction: row; align-items: center; gap: 10px; font-size: 12.8px; font-weight: 600; color: {RED};">{H("af_lmrErrT")}<button type="button" onClick="{H("af_lmrRetry")}" style="{_MINI}">Tentar de novo</button></div>')
         + se('af_hasLmr',tabela('LMR ANVISA',LT,[('Ingrediente ativo',0),('Limite máximo de resíduo',0)],'af_lmr','m',
              cel(H('m.t'),b=True)+f'<span role="cell" style="min-width: 0; {H("m.st")}">{H("m.v")}</span>',1)
              + f'<div style="{MUT}">Fonte: monografias da ANVISA (dados abertos), LMR vigente em {H("af_lmrRef")}.</div>'))
    # na fazenda (ao vivo): mesmo ingrediente ativo de produtos da fazenda
    LTF='minmax(0,1.3fr) minmax(0,.8fr) minmax(0,1.2fr) repeat(3, minmax(0,.9fr))'
    lotes=tabela('Estoque por lote',LTF,[('Produto da fazenda',0),('Lote',0),('Local',0),('Físico',1),('Reservado',1),('Disponível',1)],'af_lotes','l',
        cel(H('l.prod'),b=True)+cel(H('l.lote'))+cel(H('l.local'))+cel(H('l.fis'),r=True)+cel(H('l.res'),r=True)+cel(H('l.disp'),r=True,b=True),1)
    faz=(se('af_fora',f'<div style="{MUT}">Nenhum produto da fazenda tem este ingrediente ativo (estoque, planos e ordens de serviço).</div>')
         + se('af_hasFaz',f'<div style="font-size: 13px; line-height: 1.45;">{H("af_fazT")}</div>'
           + se('af_hasLotes',f'{sub("Estoque por lote")}{lotes}<div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; font-size: 13px; font-weight: 800;">{H("af_lotTot")}'
                f'<a href="EST.dc.html" style="{LK}">Abrir no Estoque ›</a></div>')
           + se('af_semLotes',f'{sub("Estoque por lote")}<div style="{MUT}">Sem lote no Estoque.</div>')
           + se('af_hasPlanos',f'{sub("Planos agronômicos")}<sc-for list="{H("af_planos")}" as="pl" hint-placeholder-count="1"><div style="display: grid; grid-template-columns: 110px minmax(0,1fr) auto; gap: 10px; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 12.8px; align-items: baseline;">'
                f'<a href="PA.dc.html" title="Abrir Planos agronômicos" style="{LK}">{H("pl.id")} ›</a><span>{H("pl.t")}</span><span style="white-space: nowrap; font-variant-numeric: tabular-nums;">{H("pl.dose")}</span></div></sc-for>')
           + se('af_hasOs',f'{sub("Ordens de serviço em andamento")}<sc-for list="{H("af_os")}" as="o" hint-placeholder-count="1"><div style="display: grid; grid-template-columns: 110px minmax(0,1fr) auto auto; gap: 10px; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 12.8px; align-items: center;">'
                f'<a href="{H("o.h")}" title="Abrir {H("o.id")} na Ordem de Serviço" style="{LK}">{H("o.id")} ›</a><span>{H("o.t")}</span>{chp("o.et","o.st","o.dot")}'
                f'<span style="white-space: nowrap; text-align: right; font-variant-numeric: tabular-nums;">{H("o.dose")}</span></div></sc-for>')
           + se('af_hasRefs',f'{sub("Recomendação e ordem registradas")}<sc-for list="{H("af_refsF")}" as="rf" hint-placeholder-count="1"><div style="display: grid; grid-template-columns: 110px minmax(0,1fr); gap: 10px; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 12.8px; align-items: baseline;">'
                f'<a href="{H("rf.h")}" style="{LK}">{H("rf.ref")} ›</a><span>{H("rf.t")}</span></div></sc-for>')))
    # referência conferida em bula (agrofit_dados): mesma combinação de ingredientes
    refb=(f'<div style="{MUT}">Doses e carências conferidas em bula pública de produto com os mesmos ingredientes ativos: não são a bula deste registro. '
          f'Use para comparar; a dose segue a bula do produto escolhido.</div>'+_agf_cref('af_cref'))
    # registro e composição (como no AGROFIT) + link oficial e a nota da bula
    IT='minmax(0,1.3fr) minmax(0,1.1fr) minmax(0,.8fr) minmax(0,1fr)'
    reg_=(f'<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px 18px; padding: 12px 14px; background: {BG}; border-radius: 12px;">'
          f'<sc-for list="{H("af_kv")}" as="x" hint-placeholder-count="6"><div style="min-width: 0;"><div style="{TH}">{H("x.l")}</div>'
          f'<div style="font-size: 13.2px; font-weight: 600; margin-top: 2px; line-height: 1.4; overflow-wrap: anywhere;">{H("x.v")}</div></div></sc-for></div>'
          + tabela('Ingredientes ativos',IT,[('Ingrediente ativo',0),('Grupo químico (AGROFIT)',0),('Concentração',0),('Grupo de resistência (referência)',0)],'af_ings','g',
                   cel(H('g.t'),b=True)+cel(H('g.g'))+cel(H('g.c'))+cel(H('g.r')),1)
          + f'<div style="{MUT}">{H("af_resNota")}</div>'
          f'<div style="display: flex; flex-direction: column; gap: 4px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.8px; font-weight: 600; line-height: 1.45;">'
          f'<span>{H("af_bula")}</span><a href="{link}" target="_blank" rel="noopener" style="{LK}">Abrir no AGROFIT oficial ›</a></div>')
    NAV=(f'width: 30px; height: 30px; border-radius: 8px; border: 1px solid {LINE}; background: {SURF}; color: {INK}; cursor: pointer; font-size: 16px; line-height: 1; padding: 0;')
    return (f'<sc-if value="{H("af_open")}" hint-placeholder-val="{F_()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" tabIndex="-1" aria-label="Fechar ficha" onClick="{H("af_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-modal="true" aria-label="Ficha · {H("af_t")}" style="position: relative; width: 860px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; '
      f'box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">'
      f'<div style="display: flex; align-items: flex-start; gap: 10px;"><div style="display: flex; flex-direction: column; gap: 3px; flex-grow: 1; min-width: 0;">'
      f'<h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em; line-height: 1.3;">{H("af_t")}</h2>'
      f'<div style="{MUT}">{H("af_sub")}</div>' + se('af_hasMarcas',f'<div style="{MUT}">{H("af_marcas")}</div>') + '</div>'
      f'<sc-if value="{H("af_hasNav")}" hint-placeholder-val="{F_()}"><div style="display: flex; align-items: center; gap: 6px; flex-shrink: 0;">'
      f'<button type="button" aria-label="Produto anterior" title="Produto anterior" disabled="{H("af_prevDis")}" onClick="{H("af_prev")}" style="{NAV} {H("af_prevSt")}">‹</button>'
      f'<span style="font-size: 12px; font-weight: 600; color: {MUTED}; white-space: nowrap; font-variant-numeric: tabular-nums;">{H("af_pos")}</span>'
      f'<button type="button" aria-label="Próximo produto" title="Próximo produto" disabled="{H("af_nextDis")}" onClick="{H("af_next")}" style="{NAV} {H("af_nextSt")}">›</button></div></sc-if>'
      f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H("af_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
      f'<div style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;"><sc-for list="{H("af_chips")}" as="c" hint-placeholder-count="3">{chp("c.t","c.st","c.dot")}</sc-for></div>'
      + passo + sec('Usos registrados',usos,H('af_usosT')) + sec('Rotação',rot,H('af_rotT')) + sec('LMR ANVISA',lmr,H('af_lmrT'))
      + sec('Na fazenda',faz) + se('af_hasCref',sec('Referência conferida em bula',refb)) + sec('Registro e composição',reg_)
      + '</aside></div></sc-if>')

AGF_JS=r'''
// ===== AG-07 · Consulta Agrofit: registros reais (dados abertos AGROFIT/MAPA) =====
function GR(id){ return GRIDS.find(g=>g.id===id); }
const AGC=new Intl.Collator('pt-BR',{numeric:true,sensitivity:'base'});
const AGX={st:'',err:'',tries:0,meta:null,I:null,P:[],reg:{},ord:[],uSt:'',uErr:'',U:null,PU:null,pairs:null,UA:{},lSt:'',lErr:'',L:null,rev:0,
  vk:null,vis:null,gk:null,grows:null,leaf:{},FK:{},fazCul:[],culItems:[],uleaf:{},UH:{},AT:{},uvk:null,uvis:null,retRid:''};
const AG_REF={}; AGF.ref.forEach(r=>{ AG_REF[r.id]=r; });
const AG_FAZ=['Com saldo disponível','Sem saldo disponível','Fora da fazenda'];
const AG_FASE={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow'};
const AG_QST='font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;';
const AG_GB=[{v:'',t:'Nenhum'},{v:'cls',t:'Classe'},{v:'moa',t:'Modo de ação (IRAC/FRAC/HRAC)'},{v:'gq',t:'Grupo químico'},{v:'ing',t:'Ingrediente ativo'},{v:'tit',t:'Titular'},
  {v:'tox',t:'Classificação toxicológica'},{v:'faz',t:'Na fazenda'}];
const AG_TIPO={D:'planta daninha',P:'praga',O:'doença'};
const AG_TOXC={vermelha:'red',amarela:'yellow',azul:'blue',verde:'green'};
const AG_LIM=50, AG_PASSO=100;
const AG_CLS_PRI=['Herbicida','Inseticida','Fungicida','Acaricida','Nematicida','Biológico'];
function agNf(n,d){ return Number(n||0).toLocaleString('pt-BR',{maximumFractionDigits:d===undefined?2:d}); }
function agUni(a){ const s=new Set(); return a.filter(x=>{ if(s.has(x)) return false; s.add(x); return true; }); }
function agChip(t,c){ const cc=G2C[c]||G2C.gray; return {t:t, st:'display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';',
  dot:'width:6px;height:6px;border-radius:999px;flex-shrink:0;background:'+cc[0]+';'}; }
function agTick(self){ AGX.rev++; self.setState({agf_rev:AGX.rev}); }
function agDataArq(){ const f=((AGX.meta||{}).fontes||{}).formulados||{}; const d=new Date(f.last_modified||AGX.meta.processado_em); if(isNaN(d)) return '';
  try{ return d.toLocaleDateString('pt-BR',{timeZone:'America/Sao_Paulo'}); }catch(e){ return d.toLocaleDateString('pt-BR'); } }
function agDiasArq(){ const f=((AGX.meta||{}).fontes||{}).formulados||{}; const d=new Date(f.last_modified||''); return isNaN(d)?0:Math.floor((Date.now()-d.getTime())/864e5); }
function agMB(n){ return agNf(n/1048576,1)+' MB'; }
// LMR: valor + tipo + ato; 999 é código da tabela da ANVISA, não limite (11 entradas no arquivo de 02/10/2026)
function agLmrT(e,L,curto){ const tp=(L.tipos||{})[e[1]]||e[1], x=e[0], tem=x!==null&&x!==undefined, s999=tem&&Number(x)>=999;
  const v=s999?'Valor 999 na tabela da ANVISA: código, não é limite numérico; confira a monografia':(tem?(agNf(x,4)+' mg/kg · '+tp):tp);
  if(curto) return (s999?'valor 999 (código, sem limite numérico)':v)+(e[2]?'':' · não autorizado');
  return v+(e[2]?'':' · NÃO autorizado na monografia')+' · '+((L.atos||[])[e[3]]||'')+(e[4]?(' · desde '+String(e[4]).split('-').reverse().join('/')):''); }
function agCulK(x){ return g2norm(x).replace(/[-\s]+/g,' ').trim(); }          // 'Pinhão manso' = 'Pinhão-manso'
function agCulT(x){ return g2norm(x).split(/[-\s(]+/)[0]; }                     // 'Feijão-caupi' ~ 'Feijão'; 'Tomate (Rasteiro)' ~ 'Tomate'
// ---------- carga: meta → índice (lista pronta) → usos por cultura (segundo plano) → LMR (na 1ª ficha) ----------
function agJ(nome,v){ return fetch(nome+(v?('?v='+encodeURIComponent(v)):''),{cache:v?'default':'no-cache'})
  .then(r=>{ if(!r.ok) throw new Error(nome+' respondeu HTTP '+r.status); return r.json(); })
  .then(j=>{ if(v&&j.versao!==v){ const e=new Error('versão diferente em '+nome); e.versao=true; throw e; } return j; }); }
function agCarregar(self){ if(AGX.st==='carregando'||AGX.st==='ok') return; AGX.st='carregando'; AGX.err=''; agTick(self);
  agJ('agrofit_meta.json').then(m=>{ AGX.meta=m; agTick(self); return agJ('agrofit_indice.json',m.versao); })
    .then(I=>{ agPrep(I); AGX.st='ok'; agTick(self); agHashAplica(self); agUsosCarregar(self); })
    .catch(e=>{ if(e&&e.versao&&AGX.tries<1){ AGX.tries++; AGX.st=''; agCarregar(self); return; }
      AGX.st='erro'; AGX.err=(e&&e.versao)?'a base foi trocada no servidor durante o carregamento':((e&&e.message)||String(e)); agTick(self); }); }
function agUsosCarregar(self){ if(AGX.uSt==='carregando'||AGX.uSt==='ok') return; AGX.uSt='carregando'; AGX.uErr=''; agTick(self);
  const m=AGX.meta, n=((m.contagens||{}).fatias_cultura)||0, fs=[]; for(let i=0;i<n;i++) fs.push(agJ('agrofit_usos_cultura_'+i+'.json',m.versao));
  Promise.all(fs).then(arr=>{ if(!arr.length) throw new Error('meta sem fatias de usos'); agPrepUsos(arr); AGX.uSt='ok'; agTick(self); })
    .catch(e=>{ AGX.uSt='erro'; AGX.uErr=(e&&e.versao)?'a base foi trocada no servidor durante o carregamento':((e&&e.message)||String(e)); agTick(self); }); }
function agLmrCarregar(self){ if(AGX.lSt==='carregando'||AGX.lSt==='ok'||!AGX.meta) return; AGX.lSt='carregando'; AGX.lErr='';
  agJ('agrofit_lmr.json',AGX.meta.versao).then(L=>{ AGX.L=L; AGX.lSt='ok'; agTick(self); })
    .catch(e=>{ AGX.lSt='erro'; AGX.lErr=(e&&e.message)||String(e); agTick(self); }); }
// ---------- preparo do índice ----------
function agPrep(I){ AGX.I=I; const F={}; I.campos.forEach((c,i)=>{ F[c]=i; });
  const IG=I.ingredientes, GQ=I.gruposQuimicos, CL=I.classes, TD=I.todasCulturas;
  // grupo de resistência (referência da base conferida, agrofit_dados): nome exato ou nome seguido de sal/éster/cepa
  const casa=(n,pt)=>n===pt||(n.indexOf(pt)===0&&!/[a-z0-9]/.test(n.charAt(pt.length)));
  AGX.REFC=IG.map(x=>{ const n=g2norm(x[0]).trim(); return AGF.grupo_ref.filter(g=>g[0].some(pt=>casa(n,pt))).map(g=>g[1]); });
  const gen=new Set(AGF.gq_gen||[]); AGX.GQG=GQ.map(g=>gen.has(g2norm(g).trim()));
  AGX.P=I.produtos.map((r,i)=>{ const ing=r[F.ingredientes]||[], ids=ing.map(x=>x[0]), cls=r[F.classes]||[], marcas=r[F.marcas]||[];
    const gq=agUni(ids.map(id=>IG[id]?IG[id][1]:null).filter(g=>g!==null&&g!==undefined));
    const codes=agUni([].concat.apply([],ids.map(id=>AGX.REFC[id]||[]))).sort(AGC.compare);   // ordem canônica: FRAC 3 < FRAC 7 < FRAC 11 < FRAC M1
    const p={i:i,reg:String(r[F.registro]),marcas:marcas,nome:marcas[0]||('Registro '+r[F.registro]),form:r[F.formulacao],ing:ing,ids:ids,
      key:ids.slice().sort((a,b)=>a-b).join(','),tit:r[F.titular],cls:cls,modo:r[F.modo],tox:r[F.tox],amb:r[F.amb],org:r[F.organico],
      cul:r[F.culturas]||[],nUsos:r[F.nUsos]||0,nAlvos:r[F.nAlvos]||0,gq:gq,codes:codes};
    p.rot=agRotKeys(ids);
    p.comp=agUni(cls.map(c=>CL[c][1])); p.bio=cls.some(c=>CL[c][2]===1);
    p.ingT=ids.map(id=>IG[id]?IG[id][0]:'?').join(' + '); p.gqT=gq.map(g=>GQ[g]).join(' + ');
    p.moaT=codes.join(' + '); p.moaN=codes.map(k=>(AGF.grupos[k]||[k])[0]).join(' + ');
    p.titT=I.titulares[p.tit]||''; p.titC=p.titT.replace(/\s*[-–]\s*[^-–]*\/\s*[A-Z]{2}\s*$/,'').trim()||p.titT;
    p.modoT=(p.modo!==null&&p.modo>=0)?(I.modos[p.modo]||''):''; p.clsT=agUni(cls.map(c=>CL[c][0])).join(', ');
    p.todas=p.cul.indexOf(TD)>=0; p.culSet=new Set(p.cul);
    const fo=I.formulacoes[p.form]||['',''];
    p.hay=g2norm([p.reg,marcas.join(' '),p.ingT,p.gqT,p.moaT,p.moaN,p.titT,p.clsT,p.comp.join(' '),p.bio?'biologico':'',p.modoT,fo[0],fo[1]].join(' '));
    return p; });
  AGX.reg={}; AGX.P.forEach(p=>{ AGX.reg[p.reg]=p.i; });
  AGX.ord=AGX.P.map(p=>p.i).sort((a,b)=>AGC.compare(AGX.P[a].nome,AGX.P[b].nome)||AGC.compare(AGX.P[a].reg,AGX.P[b].reg));
  // culturas da fazenda primeiro, depois A–Z; as especiais ("não informada" etc.) no fim
  const cn={}; I.culturas.forEach((c,id)=>{ cn[g2norm(c[0])]=id; }); AGX.fazCul=AGF.culturas.map(n=>cn[g2norm(n)]).filter(x=>x!==undefined);
  AGX.culCmp=(a,b)=>{ const fa=AGX.fazCul.indexOf(a), fb=AGX.fazCul.indexOf(b); if(fa!==fb) return (fa<0?99:fa)-(fb<0?99:fb);
    const ea=I.culturas[a][6]?1:0, eb=I.culturas[b][6]?1:0; if(ea!==eb) return ea-eb; return AGC.compare(I.culturas[a][0],I.culturas[b][0]); };
  AGX.culItems=I.culturas.map((c,id)=>id).sort(AGX.culCmp).map(id=>{ const c=I.culturas[id], faz=AGX.fazCul.indexOf(id)>=0;
    return {v:String(id),t:c[0],sub:(faz?'Cultura da fazenda · ':'')+(id===TD?'vale para qualquer cultura · ':'')+agNf(c[3])+' produtos · '+agNf(c[4])+' usos',k:c[1]||''}; });
  // fichas da fazenda (agrofit_dados) pela combinação exata de ingredientes, casada pelo NOME (sem acento e sem caixa)
  const inm={}; IG.forEach((x,id)=>{ inm[g2norm(x[0]).trim()]=id; }); AGX.FK={};
  AGF.ref.forEach(r=>{ const ids=r.agrofit.map(n=>inm[g2norm(n).trim()]); r.ids=ids.filter(x=>x!==undefined);
    r.key=(r.ids.length&&r.ids.length===r.agrofit.length)?r.ids.slice().sort((a,b)=>a-b).join(','):''; if(r.key) (AGX.FK[r.key]=AGX.FK[r.key]||[]).push(r); });
  AGX.leaf={}; AGX.uleaf={}; AGX.UH={}; AGX.AT={}; AGX.vk=null; AGX.uvk=null; AGX.gk=null; }
// rotação por MODO DE AÇÃO: código IRAC/FRAC/HRAC de referência de cada ingrediente (AGF.grupo_ref cobre todos os químicos do arquivo).
// Sem código, vale o grupo químico do AGROFIT; rótulo que não indica modo de ação (biológico, extrato, inorgânico) → o próprio ingrediente.
// Código "UN" (modo de ação desconhecido) não une produtos. s = chaves de sítio específico; m = multissítio (FRAC M).
function agRotKeys(ids){ const IG=AGX.I.ingredientes, s=new Set(), m=new Set();
  ids.forEach(id=>{ const cs=(AGX.REFC[id]||[]).filter(k=>!/\bUN|N-UN/.test(k));
    if(cs.length){ cs.forEach(k=>(/^FRAC M/.test(k)?m:s).add('c'+k)); return; }
    const g=IG[id]?IG[id][1]:null; s.add((g!==null&&g!==undefined&&!AGX.GQG[g])?('q'+g):('i'+id)); });
  return {s:s,m:m}; }
// q NÃO é rotação de p quando repete um modo de ação de sítio específico de p, ou quando só traz multissítio que p já tem
// (Armero = protioconazol + mancozebe → mancozebe sozinho não é rotação; clorotalonil, ou azoxistrobina + mancozebe, é).
function agMesmo(p,q){ const P=p.rot, Q=q.rot; for(const k of Q.s) if(P.s.has(k)) return true;
  if(!Q.s.size){ if(!P.s.size){ for(const k of Q.m) if(P.m.has(k)) return true; return false; } for(const k of Q.m) if(!P.m.has(k)) return false; return Q.m.size>0; }
  return false; }
function agPrepUsos(arr){ const U={}; arr.forEach(s=>{ Object.keys(s.culturas).forEach(k=>{ U[k]=s.culturas[k]; }); });
  const PU=AGX.P.map(()=>[]), pairs=[];
  Object.keys(U).forEach(k=>{ const c=Number(k); U[k].forEach(x=>{ pairs.push({c:c,a:x[0],ps:x[1],h:null}); x[1].forEach(pi=>{ if(PU[pi]) PU[pi].push([c,x[0]]); }); }); });
  AGX.U=U; AGX.PU=PU; AGX.pairs=pairs; AGX.UA={}; AGX.uleaf={}; AGX.leaf={}; AGX.vk=null; AGX.uvk=null; AGX.gk=null; agPrepH(pairs); }   // leaf: a coluna Alvos ganha os nomes
// texto pesquisável dos ~280 mil usos montado em fatias de ~12 ms logo após a carga (a 1ª busca não paga a montagem)
function agPrepH(pairs){ let i=0; const passo=()=>{ if(AGX.pairs!==pairs) return; const t0=Date.now();
    while(i<pairs.length){ agPairH(pairs[i++]); if((i&511)===0&&Date.now()-t0>12) break; } if(i<pairs.length) setTimeout(passo,0); };
  setTimeout(passo,0); }
function agUA(c){ c=Number(c); if(AGX.UA[c]) return AGX.UA[c]; const m=new Map(); ((AGX.U||{})[String(c)]||[]).forEach(x=>{ m.set(x[0],x[1]); }); return (AGX.UA[c]=m); }
function agPairH(pr){ if(pr.h===null){ const I=AGX.I, al=I.alvos[pr.a]||['',[]]; pr.h=g2norm(I.culturas[pr.c][0]+' '+al[0]+' '+(al[1]||[]).join(' ')); } return pr.h; }
function agAlvoT(a,curto){ const al=AGX.I.alvos[a]||['',[],'',0]; const cs=al[1]||[]; if(!al[0]&&!cs.length) return '(alvo não informado)';
  if(curto) return cs.length?cs[0]:al[0]; return (cs.length?cs.slice(0,3).join(', ')+' · ':'')+al[0]; }
function agToxT(p,longo){ const t=AGX.I.tox[p.tox]; if(!t) return '—'; const s=t[0].split(' – '); if(longo) return t[0];
  const h=s[0].replace(/^Categoria /,'Cat. ').replace(/^Não classificado$/,'Não classificado'); const r=s[1]?s[1].replace(/ \(classificação anterior\)$/,''):'';
  return r?(h+(/anterior/.test(t[0])?' (ant.)':'')+' · '+r.charAt(0).toLowerCase()+r.slice(1)):h; }
function agAmbT(p,longo){ const a=AGX.I.amb[p.amb]; if(!a) return 'Amb. não informada'; if(longo) return a[0]; const s=a[0].split(' – ');
  return s.length>1?('Amb. '+a[1]+' · '+s[1].replace(/ ao meio ambiente$/,'').toLowerCase()):('Amb. · '+a[0].replace(/ ao meio ambiente$/,'').toLowerCase()); }
// ---------- filtros (cache pela chave dos filtros) ----------
function agVis(st){ const q=st.agf_q||'', cul=st.agf_cul||'', al=st.agf_alvo||'', cls=st.agf_cls||'', org=!!st.agf_org, ref=st.agf_ref||'', semTD=!!st.agf_semTD;
  const k=[q,cul,al,cls,org,ref,semTD,AGX.uSt].join('|'); if(AGX.vk===k) return AGX.vis;
  const P=AGX.P, TD=AGX.I.todasCulturas, uOk=AGX.uSt==='ok', r=ref?AG_REF[ref]:null;
  const ws=g2norm(q).split(/\s+/).filter(Boolean).slice(0,30), ALL=ws.length?(Math.pow(2,ws.length)-1):0;
  // "Todas as culturas" (em geral biológicos, registrados por alvo) vale para qualquer cultura, salvo se a pessoa pedir só os específicos
  let S=null; if(cul!==''&&al!==''&&uOk){ S=new Set((agUA(cul).get(Number(al))||[]).concat(semTD?[]:(agUA(TD).get(Number(al))||[]))); }
  const pre=[], pm={}; let incomp=false;
  AGX.ord.forEach(i=>{ const p=P[i];
    if(r&&p.key!==r.key) return; if(cul!==''&&!(p.culSet.has(Number(cul))||(p.todas&&!semTD))) return; if(S&&!S.has(i)) return;
    if(!ws.length){ pre.push(i); return; }
    let m=0; ws.forEach((w,b)=>{ if(p.hay.indexOf(w)>=0) m+=Math.pow(2,b); });
    if(m===ALL) pre.push(i); else { pm[i]=m; incomp=true; } });
  // palavras que não estão no produto têm de estar TODAS num mesmo uso (cultura e alvo juntos), dentro dos filtros de cultura/alvo
  if(incomp&&uOk){ const ok=new Set(); AGX.pairs.forEach(pr=>{ if(cul!==''&&pr.c!==Number(cul)&&(semTD||pr.c!==TD)) return; if(al!==''&&pr.a!==Number(al)) return;
      const h=agPairH(pr); let m=0; ws.forEach((w,b)=>{ if(h.indexOf(w)>=0) m+=Math.pow(2,b); }); if(!m) return;
      pr.ps.forEach(i=>{ const x=pm[i]; if(x!==undefined&&!ok.has(i)&&((x|m)===ALL)) ok.add(i); }); });
    if(ok.size){ const inPre=new Set(pre); AGX.ord.forEach(i=>{ if(ok.has(i)&&!inPre.has(i)) pre.push(i); }); const pos={}; AGX.ord.forEach((i,j)=>{ pos[i]=j; }); pre.sort((a,b)=>pos[a]-pos[b]); } }
  const okCls=(p)=>!cls||(cls==='Biológico'?p.bio:p.comp.indexOf(cls)>=0);
  const ids=pre.filter(i=>okCls(P[i])&&(!org||P[i].org==='S'));
  const cnt={}; let bio=0; pre.forEach(i=>{ const p=P[i]; if(org&&p.org!=='S') return; p.comp.forEach(c=>{ cnt[c]=(cnt[c]||0)+1; }); if(p.bio) bio++; });
  const orgN=pre.filter(i=>okCls(P[i])&&P[i].org==='S').length;
  const semCls=pre.filter(i=>!org||P[i].org==='S').length;
  const nTD=cul!==''?ids.filter(i=>!P[i].culSet.has(Number(cul))).length:0;
  AGX.vis={ids:ids,pre:pre,cnt:cnt,bio:bio,orgN:orgN,semCls:semCls,nTD:nTD,semUsos:incomp&&!uOk}; AGX.vk=k; return AGX.vis; }
// ---------- na fazenda (ao vivo): mesmo ingrediente ativo das fichas da fazenda ----------
function agFaz(p,c){ const refs=AGX.FK[p.key]||[]; if(!refs.length) return null;
  const nf=agUni([].concat.apply([],refs.map(r=>r.nomes_fazenda)));
  const L=Object.values(c.lotes||{}).filter(l=>nf.indexOf(l.prod)>=0);
  const por=nf.map(n=>{ const ls=L.filter(l=>l.prod===n); return {n:n,L:ls,disp:ls.reduce((a,l)=>a+cenDisp(l),0),un:ls.length?ls[0].un:''}; });
  const os=Object.values(c.ordens||{}).filter(o=>o.etapa!=='Encerradas'&&o.etapa!=='Canceladas'&&(o.ins||[]).some(x=>nf.indexOf(x.p)>=0));
  const pl=[].concat.apply([],refs.map(r=>AGF.planos[r.id]||[])); const rf=[].concat.apply([],refs.map(r=>r.refs_fazenda||[]));
  const disp=por.reduce((a,x)=>a+x.disp,0);
  return {refs:refs,nf:nf,L:L,por:por,disp:disp,os:os,pl:pl,rf:rf,cat:disp>0?AG_FAZ[0]:AG_FAZ[1]}; }
// alvos de um produto (todas as culturas), do mais frequente nos usos ao menos frequente; null enquanto os usos carregam
function agAlvosP(p){ const PU=AGX.PU&&AGX.PU[p.i]; if(!PU) return null; const n=new Map(); PU.forEach(x=>n.set(x[1],(n.get(x[1])||0)+1));
  return Array.from(n.keys()).sort((a,b)=>(n.get(b)-n.get(a))||AGC.compare(agAlvoT(a,true),agAlvoT(b,true))); }
function agLeaf(p){ let L=AGX.leaf[p.i]; if(L) return L; const I=AGX.I;
  const cs=p.cul.slice().sort(AGX.culCmp).map(c=>I.culturas[c][0]); const n=p.cul.length;
  const cT=n===1?cs[0]:(agNf(n)+' culturas'), cM=n===1?'1 cultura':(cs.slice(0,3).join(', ')+(n>3?' +'+(n-3):''));
  const as=agAlvosP(p), na=as?as.length:p.nAlvos, aT=agNf(na)+(na===1?' alvo':' alvos');
  const aM=as?(as.slice(0,3).map(a=>agAlvoT(a,true)).join(', ')+(as.length>3?' +'+(as.length-3):'')):'nomes em instantes';
  const tox=agToxT(p), amb=agAmbT(p);
  const gm=(p.gqT||'grupo químico não informado')+(p.moaT?(' · '+p.moaT):'');
  L={id:p.reg, dr:'agf_op_'+p.reg, v:{cult:n,alvo:na,faz:null}, s:{prod:p.nome+' · '+p.reg, ing:p.ingT+' · '+gm, cls:p.clsT+' · '+(p.modoT||'—'), alvo:aT, tox:tox+' · '+amb, faz:AG_FAZ[2]},
    m:{alvo:(as||[]).map(a=>({id:String(a),l:agAlvoT(a,true)}))},
    p:{prod:[{k:'b',t:p.nome},{k:'br'},{k:'mut',t:'Reg. '+p.reg+' · '+p.titC}], ing:[{k:'txt',t:p.ingT},{k:'br'},{k:'mut',t:gm}],
       cls:[{k:'txt',t:p.clsT},{k:'br'},{k:'mut',t:p.modoT||'modo de ação não informado'}], cult:[{k:'txt',t:cT},{k:'br'},{k:'mut',t:cM}],
       alvo:[{k:'txt',t:aT},{k:'br'},{k:'mut',t:aM}], tox:[{k:'txt',t:tox},{k:'br'},{k:'mut',t:amb}], faz:[{k:'mut',t:'—'}]}};
  return (AGX.leaf[p.i]=L); }
function agLeafFaz(L,F){ if(!F){ L.v.faz=null; L.s.faz=AG_FAZ[2]; L.p.faz=[{k:'mut',t:'—'}]; return; }
  const com=F.por.filter(x=>x.L.length), x0=com[0]||F.por[0]; L.v.faz=F.disp; L.s.faz=F.cat;
  const fz=[{k:'txt',t:x0.n+(F.por.length>1?' +'+(F.por.length-1):'')},{k:'br'}];
  fz.push(x0.L.length?{k:'mut',t:agNf(x0.disp)+' '+x0.un+' disponíveis'}:{k:'mut',t:'sem lote'}); L.p.faz=fz; }
// ---------- Praga-alvo (09/10): com a cultura escolhida, uma linha por USO na cultura (produto × praga-alvo), como no AGROFIT ----------
// Praga-alvo = nomes comuns do AGROFIT (r.m.alvo: o filtro da coluna marca o nome, não um pedaço de texto); Nome científico na sua coluna;
// Cultura do uso = a cultura escolhida ou "Todas as culturas". Sem cultura (ou com os usos ainda carregando), uma linha por produto.
let AG_COLS_P=null;
function agModoUso(st){ return (st.agf_cul||'')!==''&&AGX.uSt==='ok'; }
function agUH(c,a){ const k=c+'|'+a; let h=AGX.UH[k]; if(h===undefined){ const I=AGX.I, al=I.alvos[a]||['',[]]; h=AGX.UH[k]=g2norm(I.culturas[c][0]+' '+al[0]+' '+(al[1]||[]).join(' ')); } return h; }
function agAT(a){ let t=AGX.AT[a]; if(t===undefined) t=AGX.AT[a]=agAlvoT(a,true); return t; }
function agUsoLeaf(p,c,a){ const k=p.i+'|'+c+'|'+a; let L=AGX.uleaf[k]; if(L) return L;
  const I=AGX.I, P0=agLeaf(p), al=I.alvos[a]||['',[],'',0], cs=al[1]||[], com=cs.join(', '), ci=al[0]||'', cn=I.culturas[c][0], id=p.reg+'@'+c+'@'+a;
  L={id:id, dr:'agf_op_'+id, pi:p.i, uc:c, ua:a, v:{faz:P0.v.faz}, m:{alvo:cs.map(n=>({id:n,l:n}))},
    s:Object.assign({},P0.s,{alvo:com,cien:ci,ucul:cn}),
    p:Object.assign({},P0.p,{alvo:[{k:com?'txt':'mut',t:com||(ci?'—':'não informado')}],cien:[{k:ci?'txt':'mut',t:ci||'—'}],ucul:[{k:'txt',t:cn}]})};
  return (AGX.uleaf[k]=L); }
// usos visíveis: os produtos que passam nos filtros da lista (agVis) × os alvos deles na cultura (e em "Todas as culturas", salvo "só os de");
// a busca vale palavra a palavra no produto OU na praga-alvo do MESMO uso (cultura, nome científico e nomes comuns)
// os chips de classe e de orgânicos contam usos (a mesma unidade da lista), com os demais filtros
function agVisUso(st){ const V=agVis(st), k=AGX.vk; if(AGX.uvk===k&&AGX.uvis) return AGX.uvis;
  const I=AGX.I, TD=I.todasCulturas, cul=Number(st.agf_cul), al=st.agf_alvo||'', semTD=!!st.agf_semTD, cls=st.agf_cls||'', org=!!st.agf_org;
  const ws=g2norm(st.agf_q||'').split(/\s+/).filter(Boolean).slice(0,30), ok=new Set(V.pre), por={};
  [cul].concat(cul!==TD&&!semTD?[TD]:[]).forEach(c=>agUA(c).forEach((ps,a)=>{ if(al!==''&&a!==Number(al)) return; ps.forEach(i=>{ if(ok.has(i)) (por[i]=por[i]||[]).push([c,a]); }); }));
  const okCls=(p)=>!cls||(cls==='Biológico'?p.bio:p.comp.indexOf(cls)>=0);
  const rows=[], cnt={}, pool=[]; let bio=0, orgN=0, semCls=0;
  V.pre.forEach(i=>{ const L=por[i]; if(!L) return; const p=AGX.P[i];
    L.sort((x,y)=>((x[0]===cul?0:1)-(y[0]===cul?0:1))||AGC.compare(agAT(x[1]),agAT(y[1])));
    const M=ws.length?L.filter(x=>ws.every(w=>p.hay.indexOf(w)>=0||agUH(x[0],x[1]).indexOf(w)>=0)):L; if(!M.length) return; const n=M.length; pool.push([i,M]);
    if(!org||p.org==='S'){ p.comp.forEach(c=>{ cnt[c]=(cnt[c]||0)+n; }); if(p.bio) bio+=n; semCls+=n; }
    if(okCls(p)&&p.org==='S') orgN+=n;
    if(okCls(p)&&(!org||p.org==='S')) M.forEach(x=>rows.push(agUsoLeaf(p,x[0],x[1]))); });
  AGX.uvis={rows:rows,nCul:rows.filter(r=>r.uc===cul).length,cnt:cnt,bio:bio,orgN:orgN,semCls:semCls,pool:pool}; AGX.uvk=k; return AGX.uvis; }
// chips de classe e de orgânicos com os FILTROS DAS COLUNAS (revisão de 10/10, A5): com filtro de coluna, a contagem é sobre as linhas que
// passam nele (a mesma unidade da lista: uso ou produto), cada chip sem o próprio filtro (classe: com orgânicos; orgânicos: com a classe).
// Sem filtro de coluna, valem as contagens de agVis/agVisUso. Em cache pela chave dos filtros.
function agChipsCol(st,gs){ const f=(gs&&gs.f)||{}; if(!Object.keys(f).some(k=>(f[k]||[]).length)) return null;
  const mu=agModoUso(st), V=agVis(st), U=mu?agVisUso(st):null, cls=st.agf_cls||'', org=!!st.agf_org;
  const k=AGX.vk+'#'+(mu?'u':'p')+'#'+JSON.stringify(f); if(AGX.cck===k&&AGX.ccv) return AGX.ccv;
  const sp=GR(AGF_G), added=st.added||{}, okCls=(p)=>!cls||(cls==='Biológico'?p.bio:p.comp.indexOf(cls)>=0), cnt={}; let bio=0, semCls=0, orgN=0;
  const conta=(r,p)=>{ if(!g2match(r,sp,{f:f},null,added)) return; if(!org||p.org==='S'){ p.comp.forEach(c=>{ cnt[c]=(cnt[c]||0)+1; }); if(p.bio) bio++; semCls++; } if(okCls(p)&&p.org==='S') orgN++; };
  if(mu) U.pool.forEach(([i,M])=>{ const p=AGX.P[i]; M.forEach(x=>conta(agUsoLeaf(p,x[0],x[1]),p)); });
  else V.pre.forEach(i=>{ const p=AGX.P[i]; conta(agLeaf(p),p); });
  AGX.ccv={cnt:cnt,bio:bio,semCls:semCls,orgN:orgN}; AGX.cck=k; return AGX.ccv; }
// total de usos da cultura (com "Todas as culturas", salvo "só os de"): o "de N usos em <cultura>" da contagem
function agUsoTot(st){ const TD=AGX.I.todasCulturas, cul=Number(st.agf_cul); let n=0;
  [cul].concat(cul!==TD&&!st.agf_semTD?[TD]:[]).forEach(c=>agUA(c).forEach(ps=>{ n+=ps.length; })); return n; }
// trocar de modo (cultura sim/não) tira filtro e ordenação das colunas que só existem no outro modo
function agColsLimpa(self,mu){ const ks=(mu?AGF_COLS_U:(AG_COLS_P||[])).map(c=>c.k); const gs=g2st(self,AGF_G), f=Object.assign({},gs.f||{}); let mud=false;
  Object.keys(f).forEach(k=>{ if(ks.indexOf(k)<0){ delete f[k]; mud=true; } }); const so=gs.so&&gs.so.k&&ks.indexOf(gs.so.k)<0?{}:gs.so;
  if(mud||so!==gs.so) g2set(self,AGF_G,{f:f,so:so}); }
function agGKeys(p,gb,F){ const I=AGX.I; switch(gb){
  case 'cls': return p.comp.length?p.comp:['(classe não informada)'];
  case 'gq': return p.gq.length?p.gq.map(g=>I.gruposQuimicos[g]):['(grupo químico não informado)'];
  case 'moa': return p.codes.length?p.codes.map(k=>k+' · '+((AGF.grupos[k]||[''])[0])):['(sem código de referência: biológico, extrato, óleo…)'];
  case 'ing': return agUni(p.ids.map(id=>I.ingredientes[id]?I.ingredientes[id][0]:'?'));
  case 'tit': return [p.titT||'(titular não informado)'];
  case 'tox': return [agToxT(p,true)];
  case 'faz': return [F?F.cat:AG_FAZ[2]]; } return []; }
function agGOrd(gb){ const I=AGX.I; if(gb==='faz') return (a,b)=>AG_FAZ.indexOf(a)-AG_FAZ.indexOf(b);
  if(gb==='tox'){ const o=I.tox.map(t=>t[0]); return (a,b)=>o.indexOf(a)-o.indexOf(b); } return (a,b)=>AGC.compare(a,b); }
// ---------- combobox (cultura e alvo): lista na ordem dada sem digitar; digitando, começa-com primeiro ----------
function agAc(self,chave,itens,escolhido,pick,o){ o=o||{}; const ac=self.state.g2ac||{}; const meu=ac.k===chave; const sel=itens.find(x=>x.v===escolhido);
  const q=meu?(ac.q||''):(sel?sel.t:''); const ws=g2norm(q).split(/\s+/).filter(Boolean); const aberto=meu&&!!ac.open; const dig=meu&&!!ac.dig&&ws.length>0;
  let res=[]; if(aberto){ res=dig?itens.filter(x=>{ const t=x.h||(x.h=g2norm(x.t+' '+(x.sub||'')+' '+(x.k||''))); return ws.every(w=>t.indexOf(w)>=0); }):itens.slice();
    if(dig){ const ini=(x)=>g2norm(x.t).indexOf(ws[0])===0?0:1; res=res.map((x,j)=>[x,j]).sort((a,b)=>(ini(a[0])-ini(b[0]))||(a[1]-b[1])).map(x=>x[0]); }
    res=res.slice(0,o.max||80); }
  const i=Math.min(Math.max(meu?(ac.i||0):0,0),Math.max(res.length-1,0)); const id=('ac-'+chave).replace(/[^A-Za-z0-9_-]/g,'_');
  const escolher=(x)=>{ self.setState({g2ac:{k:chave,q:x.t,open:false,i:0}}); pick(x.v); };
  return {acId:id+'-in', acLid:id+'-lista', acQ:q, acPh:o.ph||'Buscar', acAberto:aberto&&res.length>0, acVazio:aberto&&dig&&!res.length,
    acVazioT:'Nada com “'+q+'”.', acExp:String(aberto&&res.length>0), acAtivo:(aberto&&res.length)?(id+'-o'+i):'',
    acSt:'font-family:inherit;font-size:13px;padding:7px 10px;border-radius:9px;box-sizing:border-box;width:100%;background:#fff;color:#15201A;border:1px solid '+(escolhido?'#1E7A4C':'#E4E9E5')+';',
    acItens:res.map((x,j)=>({t:x.t, sub:x.sub||'', id:id+'-o'+j, on:String(j===i), segura:(e)=>e.preventDefault(), pick:()=>escolher(x),
      st:'display:flex;flex-direction:column;align-items:flex-start;gap:1px;width:100%;text-align:left;padding:7px 10px;border:0;border-radius:8px;cursor:pointer;font-family:inherit;font-size:13px;color:#15201A;background:'+(j===i?'#E4F3E9':'transparent')+';'})),
    acSet:(e)=>{ self.setState({g2ac:{k:chave,q:e.target.value,open:true,i:0,dig:true}}); if(escolhido) pick(''); },
    acFoco:()=>{ const cur=self.state.g2ac||{}; if(cur.k!==chave||!cur.open) self.setState({g2ac:{k:chave,q:q,open:true,i:0,dig:false}}); },
    acSai:()=>{ setTimeout(()=>{ const cur=self.state.g2ac||{}; if(cur.k===chave&&cur.open) self.setState({g2ac:Object.assign({},cur,{open:false})}); },150); },
    acTecla:(e)=>{ if(e.key==='ArrowDown'||e.key==='ArrowUp'){ e.preventDefault(); if(!aberto){ self.setState({g2ac:{k:chave,q:q,open:true,i:0,dig:false}}); return; } if(!res.length) return;
        const n=(i+(e.key==='ArrowDown'?1:-1)+res.length)%res.length; self.setState({g2ac:Object.assign({},ac,{i:n})});
        setTimeout(()=>{ try{ const el=document.getElementById(id+'-o'+n); if(el&&el.scrollIntoView) el.scrollIntoView({block:'nearest'}); }catch(er){} },0); }
      else if(e.key==='Enter'){ if(aberto&&res.length){ e.preventDefault(); e.stopPropagation(); escolher(res[i]); } }
      else if(e.key==='Escape'){ if(aberto){ e.preventDefault(); e.stopPropagation(); self.setState({g2ac:Object.assign({},ac,{open:false})}); } } } }; }
// filtros da lista: qualquer troca volta às primeiras linhas
function agSetF(self,o){ self.setState(Object.assign({agf_lim:AG_LIM},o)); }
// ---------- ficha, foco e hash ----------
let AG_RET=null;
function agHash(){ try{ return decodeURIComponent((location.hash||'').slice(1)); }catch(e){ return ''; } }
function agSetHash(h){ try{ if(h){ if(location.hash!=='#'+h) history.replaceState(null,'','#'+h); } else if(location.hash) history.replaceState(null,'',location.pathname+location.search); }catch(e){} }
function agFoc(el){ return Array.prototype.slice.call(el.querySelectorAll('a[href],button,input,select,textarea,[tabindex]'))
  .filter(x=>!x.disabled&&x.tabIndex>=0&&x.getClientRects().length>0); }
function agOpen(self,reg,o){ const pi=AGX.reg[reg]; if(pi===undefined) return; const st=self.state, p=AGX.P[pi]; AGX.retRid=(o&&o.rid)||'';
  if(!st.agf){ try{ AG_RET=document.activeElement; }catch(e){ AG_RET=null; } }
  // cultura e alvo da ficha: os da lista quando o registro os tem. Uso em "Todas as culturas" vale para a cultura da lista (ex.: Mamão),
  // que fica escolhida: a O.S. precisa da cultura real do talhão.
  let cul='', al=''; const lc=st.agf_cul||'', TD=AGX.I.todasCulturas;
  if(lc!==''){ if(p.culSet.has(Number(lc))||p.todas) cul=lc; }
  else if(p.cul.length===1) cul=String(p.cul[0]);
  const la=(o&&o.a!==undefined)?String(o.a):(st.agf_alvo||''); if(cul!==''&&la!==''&&AGX.PU&&AGX.PU[pi].some(x=>(String(x[0])===cul||(p.todas&&x[0]===TD))&&String(x[1])===la)) al=la;
  self.setState({agf:reg,af_cul:cul,af_alvo:al,af_q:'',af_all:false,af_uso_so:{},af_pf:'',af_ord:'',agf_miss:''}); agSetHash('reg-'+reg);
  setTimeout(()=>{ try{ const a=document.querySelector('aside[aria-label^="Ficha"]'); if(a){ a.scrollTop=0; const b=a.querySelector('button[aria-label="Fechar"]'); if(b&&!a.contains(document.activeElement)) b.focus(); } }catch(e){} },30); }
function agClose(self){ const reg=self.state.agf; self.setState({agf:null}); agSetHash(self.state.agf_ref||'');
  const rid=AGX.retRid; AGX.retRid='';
  setTimeout(()=>{ try{ const p=AGX.P[AGX.reg[reg]]; const lin=(rid&&Array.prototype.slice.call(document.querySelectorAll('main [role=row].g2ed')).find(r=>r.getAttribute('data-rid')===rid))
      ||(p&&Array.prototype.slice.call(document.querySelectorAll('main [role=row].g2ed')).find(r=>{ const c=r.querySelector('[role=cell]'); return c&&c.innerText.split('\n')[0].trim()===p.nome; }));
    const alvo=lin||((AG_RET&&AG_RET.isConnected&&AG_RET!==document.body)?AG_RET:document.querySelector('main input[type=search]')); AG_RET=null; if(alvo) alvo.focus(); }catch(e){} },30); }
function agTeclas(self,e){ const st=self.state; if(!st.agf) return;
  if(e.key==='Escape'){ if(e.defaultPrevented) return; e.preventDefault(); agClose(self); return; }
  if(e.key!=='Tab') return; const dlg=document.querySelector('aside[aria-label^="Ficha"]'); if(!dlg) return;
  const f=agFoc(dlg); if(!f.length) return; const a=document.activeElement, i=f.indexOf(a);
  if(!dlg.contains(a)){ e.preventDefault(); (e.shiftKey?f[f.length-1]:f[0]).focus(); }
  else if(e.shiftKey&&i<=0){ e.preventDefault(); f[f.length-1].focus(); }
  else if(!e.shiftKey&&i===f.length-1){ e.preventDefault(); f[0].focus(); } }
// #reg-<registro> abre a ficha; #<id da ficha da fazenda> (links antigos da O.S. e do MIP) filtra pelo mesmo ingrediente
function agHashAplica(self){ if(AGX.st!=='ok') return; const h=agHash(), st=self.state;
  if(!h){ if(st.agf) self.setState({agf:null}); return; }
  if(h.indexOf('reg-')===0){ const reg=h.slice(4); if(AGX.reg[reg]!==undefined){ if(st.agf!==reg) agOpen(self,reg); } else self.setState({agf:null,agf_miss:reg}); return; }
  const r=AG_REF[h]; if(!r) return;
  g2set(self,AGF_G,{f:{},aq:'',x:null,so:null});
  agSetF(self,{agf_ref:h,agf_cul:'',agf_alvo:'',agf_cls:'',agf_org:false,agf_q:'',agf_miss:'',agf:null});
  const ps=r.key?AGX.P.filter(p=>p.key===r.key):[]; if(ps.length===1) setTimeout(()=>agOpen(self,ps[0].reg),0); }
// cartão da referência conferida (ficha e faixa "Da fazenda"); p = registro aberto (marca "mesma concentração"), cn = cultura escolhida primeiro
function agCref(r,p,cn){ const mc=!!p&&r.conc.length===r.ids.length&&r.ids.every((id,j)=>{ const x=p.ing.find(y=>y[0]===id); return x&&Math.abs(Number(x[1])-r.conc[j])<1e-6; });
  const chips=[agChip(r.situacao,r.situacao==='Vigente'?'green':(r.situacao==='Cancelado'?'red':'yellow'))].concat(mc?[agChip('mesma concentração','blue')]:[]);
  const us=r.usos.slice().sort((a,b)=>((b.cultura===cn)-(a.cultura===cn)));
  return {t:r.nome,sub:r.ingrediente+' · '+r.concentracao+' · '+r.formulacao,chips:chips,g:r.grupos.length?r.grupo:'Sem grupo',gn:r.grupo_nome,
    usos:us.map(u=>({c:u.cultura,a:u.alvo,nc:!u.conferido,d:u.dose,car:u.carencia,max:String(u.max_aplic),int:u.intervalo||'—'})),
    avisos:(r.avisos||[]).map(t=>({t:t})),alertas:(r.alertas_fazenda||[]).map(a=>({ref:a.ref,t:a.texto}))}; }
// ---------- uso na O.S. (CTL-5 · RL-E3) ----------
// ordens A liberar da cultura: a cultura de cada talhão da ordem pela mesma regra da trava legal (carCult, dados_carencia)
try{ window.__agx={AGX,AG_REF,agAlvoT,agOsCand}; }catch(e){}   // inspeção nos testes (ctl5_test, agrofit_test), como window.__cen
// e de operação que aplica defensivo (carOpDef, dados_carencia: pulverização ou tratamento de sementes; revisão do CTL-5, S3-1)
function agOsOp(o){ const n=o&&o.osc&&o.osc.novo; return (n&&n.atv&&n.atv.op)||((AGF.osop||{})[o.id])||''; }
function agOsCand(c,cn){ return Object.values((c&&c.ordens)||{}).filter(o=>o.etapa==='A liberar'&&/^OS-/.test(o.id)&&carOpDef(agOsOp(o))&&carTals(o.talhao).some(t=>carCult(o,t.tid)===cn))
  .sort((a,b)=>AGC.compare(a.id,b.id)); }
// ---------- render ----------
function PREVALS(self,v){
  cenOuvir(self);
  if(!self.__agIni){ self.__agIni=1; setTimeout(()=>agCarregar(self),0);
    try{ document.addEventListener('keydown',(e)=>agTeclas(self,e)); }catch(e){}
    try{ window.addEventListener('hashchange',()=>agHashAplica(self)); }catch(e){} }
  const st=self.state, sp=GR(AGF_G), gs=g2st(self,AGF_G), c=cenGet(), ok=AGX.st==='ok';
  // estado da base: cabeçalho, fonte, carregando, erro
  const m=AGX.meta; const nP=m?((m.contagens||{}).registros||0):0, dt=m?agDataArq():'';
  v.agf_ok=ok; v.agf_loading=AGX.st===''||AGX.st==='carregando'; v.agf_erro=AGX.st==='erro'; v.agf_errT=AGX.err||'';
  v.agf_retry=()=>{ AGX.st=''; AGX.tries=0; agCarregar(self); };
  const tam=m?Object.keys(m.arquivos||{}).filter(f=>/^agrofit_(meta|indice)/.test(f)).reduce((a,f)=>a+m.arquivos[f],0):0;
  v.agf_loadT='Carregando a base do AGROFIT'+(m?(' · '+agNf(nP)+' produtos com registro · '+agMB(tam)):'')+'…';
  v.agf_fonte='Fonte: AGROFIT/MAPA · dados abertos (CC-BY) · '+(m?('arquivo de '+dt+' · '+agNf(nP)+' produtos com registro'):(AGX.st==='erro'?'base indisponível':'carregando…'));
  const sc=AGX.st==='erro'?agChip('Base indisponível','red'):(!ok?agChip('Carregando a base','gray'):(agDiasArq()>7?agChip('Base de '+dt+' · desatualizada','yellow'):agChip('Base atualizada · '+dt,'green')));
  v.agf_stT=sc.t; v.agf_stSt=sc.st; v.agf_stDot=sc.dot;
  v.agf_clsL=[]; v.agf_clsOs=[]; v.agf_temClsO=false; v.agf_hasTD=false; v.agf_gbs=AG_GB; v.agf_gb=st.agf_gb||''; v.agf_grouped=!!st.agf_gb; v.agf_temCul=false; v.agf_hasRef=false; v.agf_hasMiss=false; v.agf_hasRefC=false; v.agf_rc=[];
  v.agf_uLoad=ok&&AGX.uSt==='carregando'; v.agf_uErro=ok&&AGX.uSt==='erro'; v.agf_uErrT=AGX.uErr||''; v.agf_uRetry=()=>{ AGX.uSt=''; agUsosCarregar(self); };
  v.agf_setgb=(e)=>{ self.setState({agf_gb:e.target.value,agf_lim:AG_LIM}); g2set(self,AGF_G,{x:null}); };
  sp.lim=st.agf_lim||AG_LIM;
  if(!AG_COLS_P) AG_COLS_P=sp.cols.slice();
  const mu=ok&&agModoUso(st); sp.cols=mu?AGF_COLS_U:AG_COLS_P; v.agf_ncol=sp.cols.length;
  if(!ok){ sp.rows=[]; sp.tree=false; v.agf_culV=''; v.agf_cul0='Carregando culturas…'; v.agf_culFaz=[]; v.agf_culOut=[]; v.agf_setCul=()=>{}; v.agf_alV=''; v.agf_alOpts=[]; v.agf_setAl=()=>{};
    v.agf_orgOn='false'; v.agf_orgN=''; v.agf_orgSt=''; return; }
  const I=AGX.I, TD=I.todasCulturas, cul=st.agf_cul||'', al=st.agf_alvo||'', cls=st.agf_cls||'', gb=st.agf_gb||'';
  const V=agVis(st);
  // filtros: cultura (lista: as da fazenda primeiro), praga-alvo (lista, com a cultura), classe por componente (+ Biológico), orgânicos
  const cOpt=x=>({v:x.v,t:Number(x.v)===TD?'Registro em "Todas as culturas"':x.t}), naFaz=x=>AGX.fazCul.indexOf(Number(x.v))>=0;
  v.agf_culV=cul; v.agf_cul0='Todas as culturas'; v.agf_culFaz=AGX.culItems.filter(naFaz).map(cOpt); v.agf_culOut=AGX.culItems.filter(x=>!naFaz(x)).map(cOpt);
  v.agf_setCul=(e)=>{ const x=e.target.value; agColsLimpa(self,x!==''); agSetF(self,{agf_cul:x,agf_alvo:''}); };
  v.agf_temCul=cul!=='';
  const semTD=!!st.agf_semTD, cn0=cul!==''?I.culturas[Number(cul)][0]:''; v.agf_hasTD=cul!==''&&Number(cul)!==TD&&(V.nTD>0||semTD);
  const VU=mu?agVisUso(st):null; if(mu&&Number(cul)!==TD) v.agf_hasTD=semTD||VU.rows.length>VU.nCul;
  v.agf_tdT=semTD?('Só registros específicos de '+cn0+'; os com uso em "Todas as culturas" (em geral biológicos, registrados por alvo) estão fora.')
    :(mu?(agNf(VU.nCul)+(VU.nCul===1?' uso registrado em ':' usos registrados em ')+cn0+' + '+agNf(VU.rows.length-VU.nCul)+' em "Todas as culturas" (em geral biológicos, registrados por alvo; valem para qualquer cultura).')
    :(agNf(V.ids.length-V.nTD)+' com registro em '+cn0+' + '+agNf(V.nTD)+' com uso em "Todas as culturas" (em geral biológicos, registrados por alvo; valem para qualquer cultura).'));
  v.agf_tdBt=semTD?'Incluir "Todas as culturas"':('Ver só os de '+cn0); v.agf_tdTog=()=>agSetF(self,{agf_semTD:!semTD});
  let alItems=[]; if(cul!==''&&AGX.uSt==='ok'){ const mm=new Map(); agUA(cul).forEach((ps,a)=>{ mm.set(a,{n:ps.length,todas:false}); });
      if(Number(cul)!==TD&&!st.agf_semTD) agUA(TD).forEach((ps,a)=>{ const x=mm.get(a); if(x) x.n+=ps.length; else mm.set(a,{n:ps.length,todas:true}); });
      alItems=Array.from(mm.keys()).sort((a,b)=>(mm.get(b).n-mm.get(a).n)||AGC.compare(agAlvoT(a,true),agAlvoT(b,true))).map(a=>{ const x=mm.get(a), ali=I.alvos[a]||['',[],'',0];
        const t=agAlvoT(a,true); return {v:String(a),t:t+((ali[0]&&ali[0]!==t)?' · '+ali[0]:'')+' ('+agNf(x.n)+')'}; }); }
  if(al!==''&&!alItems.some(x=>x.v===al)) alItems.push({v:al,t:agAlvoT(al,true)+' (0)'});   // escolha sem produtos continua à vista para poder ser trocada
  v.agf_alV=al; v.agf_alOpts=[{v:'',t:AGX.uSt==='ok'?('Todos os alvos ('+agNf(alItems.length)+')'):'Carregando alvos…'}].concat(alItems);
  v.agf_setAl=(e)=>agSetF(self,{agf_alvo:e.target.value});
  const chip=(t,n,on,go,lab)=>({t:t,n:agNf(n),on:String(!!on),go:go,lab:lab,st:AG_QST+(on?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')});
  // classes principais em chips (contagem com os demais filtros); as outras num seletor compacto
  const CN=agChipsCol(st,g2st(self,AGF_G))||(mu?VU:V), nCls=(k)=>k==='Biológico'?CN.bio:(CN.cnt[k]||0);
  v.agf_clsL=[chip('Todas',CN.semCls,!cls,()=>agSetF(self,{agf_cls:''}),'Mostrar todas as classes')]
    .concat(AG_CLS_PRI.map(k=>chip(k,nCls(k),cls===k,()=>agSetF(self,{agf_cls:cls===k?'':k}),cls===k?'Mostrar todas as classes':'Mostrar só '+k)));
  const outras=Object.keys(CN.cnt).filter(k=>AG_CLS_PRI.indexOf(k)<0).sort((a,b)=>(CN.cnt[b]-CN.cnt[a])||AGC.compare(a,b)); if(cls&&AG_CLS_PRI.indexOf(cls)<0&&outras.indexOf(cls)<0) outras.push(cls);
  const oOn=cls&&AG_CLS_PRI.indexOf(cls)<0; v.agf_temClsO=outras.length>0; v.agf_clsO=oOn?cls:'';
  v.agf_clsOs=[{v:'',t:'Outras classes'}].concat(outras.map(k=>({v:k,t:k+' · '+agNf(nCls(k))})));
  v.agf_setClsO=(e)=>agSetF(self,{agf_cls:e.target.value});
  v.agf_clsOSt=AG_QST+'padding:4px 8px;'+(oOn?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;');
  const org=!!st.agf_org; v.agf_orgOn=String(org); v.agf_orgN=agNf(CN.orgN); v.agf_orgTog=()=>agSetF(self,{agf_org:!org});
  v.agf_orgSt=AG_QST+(org?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')+'padding:6px 12px;';
  // faixa "Da fazenda" (link antigo #<id da ficha>) e aviso de registro fora do arquivo (#reg-<n>)
  const r=st.agf_ref?AG_REF[st.agf_ref]:null;
  if(r){ const n=V.ids.length, tot=r.key?AGX.P.filter(p=>p.key===r.key).length:0; v.agf_hasRef=true; v.agf_refT='Da fazenda: '+r.nome;
    v.agf_refD=tot?(r.ingrediente+' → '+agNf(tot)+(tot===1?' produto registrado':' produtos registrados')+' com '+(r.ids.length>1?'os mesmos ingredientes ativos':'o mesmo ingrediente ativo')+(n!==tot?(' ('+agNf(n)+' com os filtros)'):'')+'. Dose, carência e alertas: na referência conferida logo abaixo.')
      :(r.situacao==='Cancelado'?('Nenhum registro ativo no AGROFIT com '+r.ingrediente+'. '+(r.situacao_nota||'')):(r.sem?(r.ingrediente+': '+r.sem):('Nenhum produto com exatamente '+r.ingrediente+' no arquivo de '+dt+'.')));
    v.agf_refSt=tot?'background:#E4F3E9;color:#15201A;':'background:#FFF3D6;color:#8A5A00;';
    v.agf_refX=()=>{ agSetF(self,{agf_ref:''}); agSetHash(''); };
    v.agf_hasRefC=(r.usos||[]).length>0; v.agf_rc=v.agf_hasRefC?[agCref(r,null,'')]:[]; }
  if(st.agf_miss){ v.agf_hasMiss=true; v.agf_missT='Registro nº '+st.agf_miss+' não está no arquivo de '+dt;
    v.agf_missD='O AGROFIT publica só registros ativos: o produto pode ter sido cancelado ou suspenso. Confira no AGROFIT oficial.';
    v.agf_missSt='background:#FFF3D6;color:#8A5A00;'; v.agf_missX=()=>{ self.setState({agf_miss:''}); agSetHash(''); }; }
  // linhas da grade: folhas em cache; "Na fazenda" ao vivo só nos registros com ingrediente de produto da fazenda
  const P=AGX.P, Fz={}; V.ids.forEach(i=>{ const p=P[i]; if(AGX.FK[p.key]){ Fz[i]=agFaz(p,c); agLeafFaz(agLeaf(p),Fz[i]); } });
  // por uso: a coluna "Na fazenda" da linha segue a do produto (ao vivo, pelo cenário)
  const base=mu?VU.rows:V.ids.map(i=>agLeaf(P[i]));
  if(mu) base.forEach(r=>{ if(Fz[r.pi]!==undefined){ const L=agLeaf(P[r.pi]); r.v.faz=L.v.faz; r.s.faz=L.s.faz; r.p.faz=L.p.faz; } });
  if(!gb){ sp.tree=false; sp.x0={}; sp.rows=base; }
  else { const gk=AGX.vk+'#'+gb+'#'+(mu?'u':'p')+'#'+(gb==='faz'?(c.rev||0):''); if(AGX.gk!==gk){ const G={};
      base.forEach(r=>{ const i=mu?r.pi:AGX.reg[r.id]; agGKeys(P[i],gb,Fz[i]).forEach(k=>{ (G[k]=G[k]||[]).push(r); }); });
      const ks2=Object.keys(G).sort(agGOrd(gb));
      AGX.grows=ks2.map((k,j)=>{ const its=G[k], n=its.length; return {id:'G~'+j, dr:'agf_gx_'+j, v:{}, s:{prod:k}, p:{prod:[{k:'b',t:k},{k:'mut',t:agNf(n)+(mu?(n>1?' usos':' uso'):(n>1?' produtos':' produto'))}]},
          kids:its.map(r=>Object.assign({},r,{id:r.id+'~'+j}))}; }); AGX.gk=gk; }
    sp.tree=true; sp.x0={}; sp.rows=AGX.grows; }
}
// render incremental: a grade ordena e filtra o conjunto inteiro; só as primeiras linhas viram DOM ("Mostrar mais" amplia)
if(typeof g2flat==='function'){ const AG_FLAT0=g2flat; g2flat=function(sp,st,rows,mask,added){ const out=AG_FLAT0(sp,st,rows,mask,added);
  if(sp.id===AGF_G){ sp.nflat=out.length; sp.nfolhas=out.filter(x=>!x.has).length; if(sp.lim&&out.length>sp.lim) return out.slice(0,sp.lim); } return out; }; }
// ordenação da grade com Collator e chaves em cache (4.409 linhas)
if(typeof g2sort==='function'){ const AG_SORT0=g2sort; g2sort=function(arr,sp,st){ if(sp.id!==AGF_G) return AG_SORT0(arr,sp,st);
  const so=st.so||sp.so; if(!so||!so.k) return arr; const cc=sp.cols.find(x=>x.k===so.k); if(!cc) return arr; const d=so.d?-1:1;
  const kx=(r)=>{ if(so.k==='faz') return g2key(r,cc); const ck='__k_'+so.k; if(r[ck]===undefined){ r[ck]=g2key(r,cc); } return r[ck]; };   // "Na fazenda" muda ao vivo
  return arr.slice().sort((a,b)=>{ const x=kx(a), y=kx(b); if(x===null&&y===null) return 0; if(x===null) return 1; if(y===null) return -1;
    if(typeof x==='number'&&typeof y==='number') return (x-y)*d; return AGC.compare(String(x),String(y))*d; }); }; }
function EXTRAVALS(self,v){
  const st=self.state, sp=GR(AGF_G), gs=g2st(self,AGF_G), G=AGF_G, ok=AGX.st==='ok';
  // busca própria (sem acento; cultura e alvo no mesmo uso) no lugar da busca da grade
  v[G+'_q']=st.agf_q||''; v[G+'_setq']=(e)=>agSetF(self,{agf_q:e.target.value});
  const mu=ok&&agModoUso(st);
  v[G+'_all']=mu?(agNf(agUsoTot(st))+' usos em '+AGX.I.culturas[Number(st.agf_cul)][0]):(agNf(ok?AGX.P.length:0)+' produtos');
  const fil=Object.keys(gs.f||{}).some(k=>(gs.f[k]||[]).length);
  if(ok){ const V=agVis(st); if(!fil) v[G+'_count']=agNf(mu?agVisUso(st).rows.length:V.ids.length);
    else { const added=st.added||{}, ids=new Set(); const walk=(l)=>l.forEach(r=>{ if(r.kids) walk(r.kids); else if(g2match(r,sp,gs,null,added)) ids.add(String(r.id).split('~')[0]); }); walk(sp.rows||[]); v[G+'_count']=agNf(ids.size); } }
  else v[G+'_count']='0';
  v[G+'_filtered']=fil||!!(st.agf_q||st.agf_cul||st.agf_alvo||st.agf_cls||st.agf_org||st.agf_ref||st.agf_semTD);
  v[G+'_clear']=()=>{ g2set(self,G,{q:'',f:{},qv:'',aq:''}); agSetF(self,{agf_q:'',agf_cul:'',agf_alvo:'',agf_cls:'',agf_org:false,agf_ref:'',agf_semTD:false}); if(st.agf_ref) agSetHash(''); };
  // mais linhas
  const lim=sp.lim||AG_LIM, nf=sp.nflat||0; v.agf_temMais=ok&&nf>lim; v.agf_maisN=agNf(Math.min(AG_PASSO,nf-lim));
  v.agf_maisT='Mostrando '+agNf(Math.min(lim,nf))+' de '+agNf(nf)+(st.agf_gb?' linhas':(mu?' usos':' produtos')); v.agf_mais=()=>self.setState({agf_lim:lim+AG_PASSO});
  // abrir ficha e abrir/fechar grupo só nas linhas desenhadas
  (v[G+'_rows']||[]).forEach(rw=>{ const s=String(rw.id); if(s.indexOf('G~')===0){ const j=s.slice(2); v['agf_gx_'+j]=()=>{ const x=Object.assign({},g2st(self,G).x||sp.x0||{}); x[s]=!x[s]; g2set(self,G,{x:x}); }; }
    else { const id0=s.split('~')[0], q=id0.split('@'); v['agf_op_'+id0]=q.length===3?(()=>agOpen(self,q[0],{a:q[2],rid:s})):(()=>agOpen(self,q[0])); } });
  // menu ▾ da coluna: no máximo 300 valores (a busca do menu acha os demais)
  const fm=v[G+'_fm']; if(fm&&fm.open&&fm.vals&&fm.vals.length>300) fm.vals=fm.vals.slice(0,300);
  agFichaVals(self,v);
}
function agFichaVals(self,v){ const st=self.state; const pi=(st.agf&&AGX.st==='ok')?AGX.reg[st.agf]:undefined; const p=pi!==undefined?AGX.P[pi]:null;
  ['af_chips','af_culs','af_alvos','af_usos','af_usosCab','af_rotG','af_lmr','af_lotes','af_planos','af_os','af_refsF','af_cref','af_kv','af_ings'].forEach(k=>{ v[k]=[]; });
  v.af_open=!!p; v.af_close=()=>agClose(self); if(!p) return;
  if(!AGX.lSt) setTimeout(()=>agLmrCarregar(self),0);
  const I=AGX.I, TD=I.todasCulturas, c=cenGet(), uOk=AGX.uSt==='ok', cul=st.af_cul||'', al=st.af_alvo||'', dt=agDataArq();
  const cn=cul!==''?I.culturas[Number(cul)][0]:'', an=al!==''?agAlvoT(Number(al),true):'';
  v.af_t=p.nome; v.af_sub='Registro MAPA nº '+p.reg+' · '+(p.titT||'titular não informado');
  v.af_hasMarcas=p.marcas.length>1; v.af_marcas='Também comercializado como '+p.marcas.slice(1).join(', ');
  const tx=I.tox[p.tox]; v.af_chips=[agChip('Registro ativo','green')].concat(p.comp.map(k=>agChip(k,'gray')))
    .concat(tx?[agChip(agToxT(p),AG_TOXC[tx[2]]||'gray')]:[]).concat([agChip(agAmbT(p),'gray')]).concat(p.org==='S'?[agChip('Aprovado para orgânicos','green')]:[]);
  // posição na lista filtrada e navegação
  const ids=agVis(st).ids, i=ids.indexOf(pi); v.af_hasNav=i>=0&&ids.length>1; v.af_pos=agNf(i+1)+' de '+agNf(ids.length);
  v.af_prevDis=i<=0; v.af_nextDis=i<0||i>=ids.length-1; v.af_prevSt=v.af_prevDis?'opacity:.4;cursor:default;':''; v.af_nextSt=v.af_nextDis?'opacity:.4;cursor:default;':'';
  v.af_prev=()=>{ if(i>0) agOpen(self,AGX.P[ids[i-1]].reg); }; v.af_next=()=>{ if(i>=0&&i<ids.length-1) agOpen(self,AGX.P[ids[i+1]].reg); };
  // uso: cultura × alvo → O.S. Registro em "Todas as culturas": a ficha oferece as culturas da fazenda (e a da lista), porque a
  // ordem é de um talhão com cultura real; os alvos vêm do uso em "Todas as culturas".
  const cs=p.cul.slice().sort(AGX.culCmp), isTD=cul!==''&&Number(cul)===TD, viaTD=cul!==''&&!isTD&&!p.culSet.has(Number(cul));
  const extra=p.todas?agUni(AGX.fazCul.concat(cul!==''?[Number(cul)]:[])).filter(id=>id!==TD&&!p.culSet.has(id)):[];
  const opC=[]; cs.forEach(id=>{ opC.push({v:String(id),t:I.culturas[id][0]+(id===TD?' (escolha abaixo a cultura do talhão)':'')});
    if(id===TD) extra.forEach(x=>opC.push({v:String(x),t:I.culturas[x][0]+' · pelo uso em “Todas as culturas”'})); });
  v.af_cul=cul; v.af_culs=[{v:'',t:'Escolha a cultura ('+agNf(cs.length)+')'}].concat(opC);
  v.af_setcul=(e)=>self.setState({af_cul:e.target.value,af_alvo:'',af_all:false,af_uso_so:{}});
  const PU=uOk?AGX.PU[pi]:[]; const meus=cul!==''?agUni(PU.filter(x=>x[0]===Number(cul)||(p.todas&&!isTD&&x[0]===TD)).map(x=>x[1])):[];
  const alSort=(a,b)=>AGC.compare(agAlvoT(a,true),agAlvoT(b,true)); meus.sort(alSort);
  v.af_alvo=al; v.af_alvoDis=cul===''||!uOk; v.af_setalvo=(e)=>self.setState({af_alvo:e.target.value});
  // uso na O.S. (CTL-5 · RL-E3): leva produto da fazenda, cultura e alvo ao "Ajustar antes de liberar" da ordem; a consulta não emite receituário
  const F=agFaz(p,c), nf=F?F.nf.filter(n=>(AGF.osp||[]).indexOf(n)>=0):[], pf=nf.length===1?nf[0]:(nf.indexOf(st.af_pf)>=0?st.af_pf:'');
  // alvo × referência conferida da fazenda (carAlvoRef, a mesma regra da trava da O.S.; revisão do CTL-5, S3-3): a O.S. grava o alvo como a
  // referência o escreve, e só alvo coberto por ela liga "Usar na O.S." (a lista continua com todos os alvos do registro, para a consulta)
  const refDe=(n,a)=>{ const x=I.alvos[a]||['',[]]; for(const t of (x[1]||[]).concat(x[0]?[x[0]]:[])){ const r=carAlvoRef(CARD.prod[n],cn,t); if(r) return r; } return ''; };
  const cob=nf.length&&cul!==''&&!isTD?meus.filter(a=>nf.some(n=>!!refDe(n,a))):[], marca=cob.length>0&&cob.length<meus.length;
  v.af_alvos=[{v:'',t:!uOk?'Carregando alvos…':(cul===''?'Escolha a cultura primeiro':('Escolha o alvo ('+agNf(meus.length)+')'))}]
    .concat(meus.map(a=>({v:String(a),t:agAlvoT(a,true)+' · '+((I.alvos[a]||[''])[0]||'—')+(marca&&cob.indexOf(a)>=0?' · na referência da fazenda':'')})));
  const ar=(al!==''&&pf)?refDe(pf,Number(al)):'', refAl=((((CARD.prod[pf]||{}).usos||{})[cn]||{}).al)||[];
  v.af_hasPf=nf.length>1; v.af_pf=pf; v.af_pfs=[{v:'',t:'Escolha o produto ('+agNf(nf.length)+')'}].concat(nf.map(n=>({v:n,t:n}))); v.af_setpf=(e)=>self.setState({af_pf:e.target.value});
  const cand=(cul!==''&&!isTD)?agOsCand(c,cn):[], ord=cand.some(o=>o.id===st.af_ord)?st.af_ord:(cand.length===1?cand[0].id:'');
  v.af_ord=ord; v.af_ordDis=!cand.length; v.af_setord=(e)=>self.setState({af_ord:e.target.value});
  v.af_ords=[{v:'',t:cul===''||isTD?'Escolha a cultura primeiro':(cand.length?'Escolha a ordem ('+agNf(cand.length)+')':'Nenhuma ordem de pulverização A liberar em '+cn)}]
    .concat(cand.map(o=>({v:o.id,t:o.id+' · '+o.tipo+' · '+o.talhao})));
  // quem age (perfil de demonstração; CTL-3): incluir produto na O.S. é decisão do agrônomo; sem o papel, o botão fica desligado e diz quem decide
  const PF=g2perfil(), agr=g2papel(PF,'agronomo');
  const pode=cul!==''&&!isTD&&al!==''&&uOk&&!!pf&&!!ar&&!!ord&&agr; v.af_usarDis=!pode; v.af_usarSt=pode?'':'opacity:.45;cursor:not-allowed;';
  v.af_usar=()=>{ if(!pode) return; try{ location.href='OS.dc.html#'+ord+':usar='+[pf,cn,ar].map(encodeURIComponent).join('|'); }catch(e){} };
  v.af_dica=!uOk?'Carregando os usos registrados…':(cul===''?'Escolha a cultura e o alvo do uso registrado para usar o produto numa O.S.'
    :(isTD?'Uso registrado em “Todas as culturas”: escolha no campo Cultura a cultura do talhão (ex.: '+(extra.slice(0,2).map(x=>I.culturas[x][0]).join(', ')||'Soja')+').'
    :(al===''?((viaTD?'Registro sem uso específico em '+cn+': vale o uso em “Todas as culturas”. ':'')+'Escolha o alvo.'+(marca?' Os marcados “na referência da fazenda” podem ir para a O.S.':''))
    :(!nf.length?(F?('A fazenda tem '+F.nf.join(', ')+' só como referência de bula (sem lote nem plano): cadastre o produto para usá-lo numa O.S.')
      :'Sem produto da fazenda com este ingrediente ativo: cadastre o produto para usá-lo numa O.S.')
    :(!pf?'Escolha o produto da fazenda.'
    :(!ar?(an+' não está na referência conferida de '+pf+' em '+cn.toLowerCase()+(refAl.length?' ('+refAl.join('; ')+')':' (sem uso nesta cultura)')+': a O.S. só grava alvo da referência.'+(cob.length?' Escolha um alvo marcado “na referência da fazenda”.':''))
    :(!cand.length?'Nenhuma ordem de pulverização A liberar em '+cn.toLowerCase()+'. A ordem nasce do plano (Nova ordem, na O.S.) ou da vistoria (Pragas e doenças).'
    :(!ord?'Escolha a ordem A liberar.'
    :(!agr?'Incluir '+pf+' na '+ord+' é decisão de '+g2quem('agronomo')+'; o perfil '+PF.t+' só consulta.'
    :'Abre a '+ord+' em Ajustar antes de liberar com '+pf+' incluído para '+ar+'. A agrônoma informa a dose; ao liberar, a O.S. confere registro, dose e nº de aplicações e grava a aprovação. Esta consulta não emite receituário.')))))))));
  // usos registrados
  const fq=g2norm(st.af_q||'').split(/\s+/).filter(Boolean), casa=(t)=>fq.every(w=>t.indexOf(w)>=0);
  v.af_q=st.af_q||''; v.af_setq=(e)=>self.setState({af_q:e.target.value,af_all:false}); v.af_usosLoad=!uOk;
  v.af_usosT='Usos registrados · '+agNf(cs.length)+(cs.length===1?' cultura':' culturas')+' · '+agNf(p.nUsos)+(p.nUsos===1?' uso':' usos');
  // tabela de usos, uma variável por coluna (09/10): com a cultura, os alvos dela (Praga-alvo = nomes comuns · Nome científico · Tipo);
  // sem cultura, as culturas do registro (Cultura · Nº de alvos · Alvos). Ordenação no cabeçalho (af_uso_so); filtro no campo acima.
  let rows=[]; const MU='color:#5B6660;';
  const so=st.af_uso_so||{}, cab=(ks)=>ks.map(([k,l])=>{ const on=so.k===k; return {l:l,sort:on?(so.d?'descending':'ascending'):'none',seta:on?(so.d?'▼':'▲'):'⇅',ast:on?'color:#1E7A4C;font-size:9px;':'color:#B7C1BA;font-size:9px;',
      tt:'Ordenar por '+l.toLowerCase(),go:()=>self.setState({af_uso_so:!on?{k:k,d:false}:(!so.d?{k:k,d:true}:{})})}; });
  const ordena=(L,key)=>{ if(!so.k) return L; const d=so.d?-1:1; return L.slice().sort((x,y)=>{ const a=key(x,so.k), b=key(y,so.k); if(a===''&&b==='') return 0; if(a==='') return 1; if(b==='') return -1;
      return (typeof a==='number'&&typeof b==='number'?(a-b):AGC.compare(String(a),String(b)))*d; }); };
  if(uOk&&cul!==''){ v.af_usosL='Alvos em '+cn; v.af_usosTpl='minmax(0,1.2fr) minmax(0,1.1fr) minmax(0,.7fr) auto';
    v.af_usosCab=cab([['com','Praga-alvo'],['ci','Nome científico'],['tipo','Tipo']]);
    const ali=(a)=>I.alvos[a]||['',[],'',0], kA=(a,k)=>k==='com'?(ali(a)[1]||[]).join(', '):(k==='ci'?(ali(a)[0]||''):(AG_TIPO[ali(a)[2]]||''));
    rows=ordena(meus.filter(a=>!fq.length||casa(g2norm(cn+' '+agAlvoT(a)))),kA).map(a=>{ const x=ali(a), on=String(a)===al, com=(x[1]||[]).join(', ');
      return {cs:[{t:com||(x[0]?'—':'não informado'),st:com?'font-weight:700;':MU},{t:x[0]||'—',st:x[0]?'font-style:italic;':MU},{t:AG_TIPO[x[2]]||'—',st:MU}],
        bt:on?'Escolhido':'Escolher',lab:'Escolher o alvo '+agAlvoT(a,true),st:on?'background:#E4F3E9;border-radius:8px;':'',go:()=>self.setState({af_alvo:String(a)})}; }); }
  else if(uOk){ v.af_usosL='Culturas do registro'; v.af_usosTpl='minmax(0,1fr) minmax(0,.6fr) minmax(0,1.6fr) auto';
    v.af_usosCab=cab([['cul','Cultura'],['n','Nº de alvos'],['alvos','Alvos']]); const por={}; PU.forEach(x=>{ (por[x[0]]=por[x[0]]||[]).push(x[1]); });
    const L=cs.map(cid=>{ const as=(por[cid]||[]).slice().sort(alSort), nm=I.culturas[cid][0]; let mt=as;
        if(fq.length){ if(casa(g2norm(nm))) mt=as; else { mt=as.filter(a=>casa(g2norm(nm+' '+agAlvoT(a)))); if(!mt.length) return null; } }
        return {cid:cid,nm:nm,as:as,mt:mt}; }).filter(Boolean);
    rows=ordena(L,(x,k)=>k==='cul'?x.nm:(k==='n'?x.as.length:x.mt.map(a=>agAlvoT(a,true)).join(', '))).map(x=>({
        cs:[{t:x.nm,st:'font-weight:700;'},{t:agNf(x.as.length),st:'font-variant-numeric:tabular-nums;'},{t:x.mt.slice(0,4).map(a=>agAlvoT(a,true)).join(', ')+(x.mt.length>4?' +'+agNf(x.mt.length-4):''),st:MU}],
        bt:'Escolher',lab:'Escolher a cultura '+x.nm,st:'',go:()=>self.setState({af_cul:String(x.cid),af_alvo:(fq.length&&x.mt.length===1)?String(x.mt[0]):'',af_q:'',af_all:false,af_uso_so:{}})})); }
  else { v.af_usosL='Usos registrados'; v.af_usosTpl='minmax(0,1fr) auto'; v.af_usosCab=[]; }
  v.af_usosN=agNf(rows.length); v.af_usosMais=!st.af_all&&rows.length>40; v.af_usosTodos=()=>self.setState({af_all:true});
  v.af_usos=st.af_all?rows:rows.slice(0,40); v.af_usosVazio=uOk&&fq.length>0&&!rows.length;
  // rotação: mesma cultura × alvo, OUTRO MODO DE AÇÃO (código IRAC/FRAC/HRAC de referência por ingrediente; ver agRotKeys)
  const podeRot=cul!==''&&al!==''&&uOk;
  v.af_rotT=podeRot?('Rotação · '+cn+' × '+an):'Rotação'; v.af_rotHint=!podeRot; v.af_rotHintT=!uOk?'Carregando os usos registrados…':'Escolha a cultura e o alvo para ver os registros de outro modo de ação para o mesmo alvo.';
  v.af_hasRot=false;
  if(podeRot){ const cand=new Set((agUA(cul).get(Number(al))||[]).concat(Number(cul)!==TD?(agUA(TD).get(Number(al))||[]):[])); cand.delete(pi);
    const alt=[], mesmo=[]; cand.forEach(q=>{ const Q=AGX.P[q]; (agMesmo(p,Q)?mesmo:alt).push(Q); });
    const gr={}; alt.forEach(Q=>{ const k=Q.codes.length?(Q.moaT+' · '+Q.moaN):((Q.gqT||'grupo químico não informado')+' · sem código de referência'); (gr[k]=gr[k]||[]).push(Q); });
    const gks=Object.keys(gr).sort((a,b)=>(gr[b].length-gr[a].length)||AGC.compare(a,b));
    v.af_hasRot=true; const ms=mesmo.length?(' · '+agNf(mesmo.length)+' do mesmo modo de ação (não é rotação)'):'';
    v.af_rotRes=alt.length?(agNf(alt.length)+(alt.length===1?' registro':' registros')+' de outro modo de ação em '+agNf(gks.length)+(gks.length===1?' grupo':' grupos')+' para '+cn+' × '+an+ms+'.')
      :('Nenhum registro de outro modo de ação para '+cn+' × '+an+ms+'.');
    v.af_rotG=gks.slice(0,12).map(k=>{ const L=gr[k].slice().sort((a,b)=>AGC.compare(a.nome,b.nome)); return {t:k,n:agNf(L.length)+(L.length===1?' produto':' produtos'),
      ps:L.slice(0,4).map(Q=>({t:Q.nome,lab:'Abrir a ficha de '+Q.nome+' (registro '+Q.reg+')',go:()=>agOpen(self,Q.reg)})),mais:L.length>4?('+'+agNf(L.length-4)):''}; });
    if(gks.length>12) v.af_rotG.push({t:'+ '+agNf(gks.length-12)+' grupos',n:'na lista',ps:[],mais:''});
    v.af_rotNota='Modo de ação pelo código IRAC/FRAC/HRAC de referência de cada ingrediente (o AGROFIT publica só o grupo químico); sem código, vale o grupo químico. Multissítio (FRAC M) que o produto já tem não conta como rotação; multissítio novo conta.';
    v.af_rotVer=()=>{ g2set(self,AGF_G,{f:{},x:null}); agSetF(self,{agf_cul:cul,agf_alvo:al,agf_q:'',agf_cls:'',agf_org:false,agf_ref:'',agf_gb:'moa',agf:null}); agSetHash(''); }; }
  // LMR ANVISA da cultura
  v.af_lmrT=cul!==''?('LMR ANVISA · '+cn):'LMR ANVISA'; v.af_lmrHint=cul===''||AGX.lSt!=='ok'; v.af_hasLmr=false; v.af_lmrErro=AGX.lSt==='erro'&&cul!=='';
  v.af_lmrErrT='O LMR da ANVISA não carregou: '+(AGX.lErr||''); v.af_lmrRetry=()=>{ AGX.lSt=''; agLmrCarregar(self); };
  v.af_lmrHintT=cul===''?'Escolha a cultura para ver o limite máximo de resíduo de cada ingrediente.':(AGX.lSt==='erro'?'':'Carregando o LMR da ANVISA…');
  if(cul!==''&&AGX.lSt==='ok'){ const L=AGX.L, can=I.culturas[Number(cul)][2]; v.af_hasLmr=true; v.af_lmrRef=(L.referencia||'').split('-').reverse().join('/');
    // vermelho só quando a monografia diz NÃO autorizado; ausência da cultura nos dados abertos é texto neutro (o uso é registrado no MAPA)
    v.af_lmr=p.ids.map(id=>{ const ig=I.ingredientes[id]||['?',null,null], mono=ig[2]?L.monografias[ig[2]]:null; let t='', bad=false;
      if(Number(cul)===TD) t='Uso em "Todas as culturas": o LMR é por cultura; escolha a cultura do talhão.';
      else if(!ig[2]) t='Sem monografia da ANVISA nos dados abertos.';
      else if(!can) t='Cultura sem correspondência na tabela da ANVISA; confira a monografia.';
      else if(!mono) t='Monografia '+ig[2]+' sem LMR vigente nos dados abertos.';
      else { const ks=Object.keys(mono[2]), nk=agCulK(can); let k=mono[2][can]?can:ks.find(x=>agCulK(x)===nk); const e=k?mono[2][k]:null;
        if(!e){ const rel=ks.filter(x=>agCulT(x)===agCulT(can));
          t='Sem LMR de '+can+' nos dados abertos da ANVISA (monografia '+ig[2]+'); confira a monografia.'
            +(rel.length?(' A monografia traz '+rel.slice(0,2).map(x=>x+': '+agLmrT(mono[2][x],L,true)).join('; ')+'.'):''); }
        else { t=agLmrT(e,L)+(k!==can?(' · registrado como “'+k+'”'):''); bad=!e[2]; } }
      return {t:ig[0],v:t,st:bad?'color:#B42318;font-weight:700;':''}; }); }
  // na fazenda (ao vivo)
  v.af_fora=!F; v.af_hasFaz=!!F;
  if(F){ v.af_fazT='Mesmo ingrediente ativo de '+F.nf.join(', ')+' (a fazenda registra o produto pelo nome, sem a marca).';
    v.af_lotes=F.L.slice().sort((a,b)=>cenDisp(b)-cenDisp(a)).map(l=>({prod:l.prod,lote:l.lote,local:l.local,fis:agNf(l.fisico)+' '+l.un,res:agNf(l.reservado)+' '+l.un,disp:agNf(cenDisp(l))+' '+l.un}));
    v.af_hasLotes=F.L.length>0; v.af_semLotes=!F.L.length; v.af_lotTot='Disponível: '+F.por.filter(x=>x.L.length).map(x=>x.n+' '+agNf(x.disp)+' '+x.un).join(' · ');
    v.af_planos=F.pl.map(x=>({id:x.id,t:x.nome+' · '+x.atv,dose:x.dose})); v.af_hasPlanos=F.pl.length>0;
    v.af_os=F.os.map(o=>{ const x=(o.ins||[]).find(y=>F.nf.indexOf(y.p)>=0)||{}; const ch=agChip(o.etapa,AG_FASE[o.etapa]||'gray');
      return {id:o.id,h:'OS.dc.html#'+o.id,t:o.tipo+' · '+o.talhao+' · '+x.p,et:ch.t,st:ch.st,dot:ch.dot,dose:agNf(x.dose)+' '+(x.un||'')+'/ha'}; }); v.af_hasOs=F.os.length>0;
    v.af_refsF=F.rf.map(x=>({ref:x.ref,h:x.href,t:x.texto})); v.af_hasRefs=F.rf.length>0; }
  else { v.af_hasLotes=false; v.af_semLotes=false; v.af_hasPlanos=false; v.af_hasOs=false; v.af_hasRefs=false; }
  // referência conferida em bula (mesma combinação de ingredientes)
  const refs=AGX.FK[p.key]||[]; v.af_hasCref=refs.length>0;
  v.af_cref=refs.map(r=>agCref(r,p,cn));
  // registro e composição
  const fo=I.formulacoes[p.form]||['','']; const og=(I.organicos||{})[p.org]||p.org;
  v.af_kv=[{l:'Registro MAPA',v:p.reg},{l:'Marca comercial',v:p.marcas.join(', ')||'—'},{l:'Titular do registro',v:p.titT||'—'},
    {l:'Formulação',v:(fo[0]?fo[0]+' · ':'')+(fo[1]||'—')},{l:'Classe',v:p.clsT||'—'},{l:'Modo de ação (texto do AGROFIT)',v:p.modoT||'não informado'},
    {l:'Classificação toxicológica',v:agToxT(p,true)},{l:'Classe ambiental',v:agAmbT(p,true)},
    {l:'Agricultura orgânica (AGROFIT)',v:og+(p.org==='O'?' (valor sem significado documentado na fonte)':'')},{l:'Situação',v:'Registro ativo no arquivo de '+dt}];
  v.af_ings=p.ing.map(x=>{ const ig=I.ingredientes[x[0]]||['?',null]; const cds=AGX.REFC[x[0]]||[];
    return {t:ig[0],g:(ig[1]!==null&&ig[1]!==undefined)?I.gruposQuimicos[ig[1]]:'—',c:(x[1]!==null&&x[1]!==undefined?agNf(x[1],3):'—')+' '+(x[2]||''),
      r:cds.length?cds.map(k=>k+' · '+((AGF.grupos[k]||[''])[0])).join(' + '):'—'}; });
  v.af_resNota='O AGROFIT informa o grupo químico, não o grupo de resistência; o código IRAC/FRAC/HRAC acima é referência das classificações públicas, por ingrediente ativo (sem código: biológico, extrato, óleo ou modo de ação desconhecido).';
  v.af_bula='Dose, carência, intervalo de reentrada e nº de aplicações: na bula do produto (não estão nos dados abertos). No AGROFIT oficial, consulte o registro nº '+p.reg+'.';
}
'''

def ag07():
    import cenario  # aqui dentro: cenario.seed importa areas.processo_os
    import agrofit_dados as A
    fname='AG-07.dc.html'; E._reset_screen(fname)
    dados=agf_dados(); link=A.CONSULTA['link']
    # 6 colunas; larguras máximas (texto quebra) para a grade inteira caber em 1280 px com o menu aberto (contêiner de ~956 px)
    # com a cultura escolhida, as 8 colunas por uso (AGF_COLS_U): a página troca sp.cols e o número de trilhas da grade (agf_ncol, _agf_pos)
    cols=[dict(c) for c in AGF_COLS_P]
    g=grid(cols,[],edit=dict(m='ro',title='',fields=[]),gid=AGF_ID,total=False,tools=_agf_tools())
    corpo=_agf_estados()+f'<sc-if value="{H("agf_ok")}" hint-placeholder-val="{F_()}">'+bloco('Produtos fitossanitários com registro','',_agf_filtros()+g+_agf_mais())+'</sc-if>'
    EXTRA.append(_agf_painel(link))
    import dados_carencia as DCAR   # local e cultura das ordens (Usar na O.S.): a mesma regra da trava legal da O.S.
    EXTRAJS[0]=(cenario.js_prefixo()+DCAR.js_local()+'const AGF = '+json.dumps(dados,ensure_ascii=False).replace('</','<\\/')+';\nconst AGF_G = '+json.dumps(AGF_ID)+';\n'
                +'const AGF_COLS_U = '+json.dumps([E._col_un(dict(c)) for c in AGF_COLS_U],ensure_ascii=False)+';\n'+AGF_JS)
    HEIGHTS37[fname]=900
    shell37('AG-07','Consulta Agrofit',corpo,fname=fname,status=(H('agf_stT'),'gray'),cont=_agf_fonte(link),search=False)
    _agf_pos(fname)
    _agf_copia()
    return fname

def _agf_copia():
    """JSON da base ao lado da página: project/ (publicação) e _render/ (servidor local dos testes)."""
    raiz=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    for dst in (E.P,_os.path.join(raiz,'_render')):
        if not _os.path.isdir(dst): continue
        for f in agf_arquivos(): _sh.copyfile(_os.path.join(AGF_DIR,f),_os.path.join(dst,f))

def _agf_pos(fname):
    """placeholder da busca (procura também cultura e alvo), anel de foco e selo do cabeçalho com a cor calculada na tela."""
    import re
    from engine import chip as _chip
    p=_os.path.join(E.P,fname); s=open(p,encoding='utf-8').read()
    alvo='value="{{'+AGF_ID+'_q}}"'
    pat=re.compile(r'min-width: 160px;(">(?:(?!<label).)*?<input type="search" aria-label=")\{\{'+AGF_ID+r'_qlab\}\}(" placeholder=")Buscar…("\s*'+re.escape(alvo)+')',re.S)   # o rótulo vem do g2 (um campo de busca por tela)
    s,n=pat.subn(r'min-width: min(380px, 100%);" class="agf-busca\1Buscar produto, registro, ingrediente, titular, cultura ou praga\2Buscar produto, ingrediente, titular, cultura ou praga…\3',s)
    assert n==1, 'busca da grade não encontrada em '+fname
    assert s.count('</style>')>=1; s=s.replace('</style>','.agf-busca:focus-within{outline:2px solid #1E7A4C;outline-offset:1px}</style>',1)
    old=_chip(H('agf_stT'),'gray'); assert s.count(old)==1, 'selo do cabeçalho não encontrado em '+fname
    s=s.replace(old,f'<span role="status" style="{H("agf_stSt")}"><span style="{H("agf_stDot")}"></span>{H("agf_stT")}</span>')
    # uma linha por uso (cultura escolhida) tem 8 colunas; por produto, 6: o número de trilhas da grade vem da página (agf_ncol)
    tpl=f'grid-template-columns: var(--g2cols, repeat({len(AGF_COLS_P)}, auto));'
    assert s.count(tpl)==1, 'trilhas da grade não encontradas em '+fname
    s=s.replace(tpl,'grid-template-columns: var(--g2cols, repeat('+H('agf_ncol')+', auto));')
    open(p,'w',encoding='utf-8').write(s)
