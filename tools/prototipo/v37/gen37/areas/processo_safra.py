# -*- coding: utf-8 -*-
"""Agrícola › Planejar safra — processo em 6 etapas numa só tela de trabalho (SAF.dc.html)."""
import json, os
from engine import (grid,section,esc,icon,chip,btn,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,SH,DISP,BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, steps_state, HEIGHTS37
import dados2 as D2
import dados as D
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
NOMES=['Escolha a safra','Defina cultivos e planos','Defina os rendimentos','Confira o plano operacional','Dimensione os recursos','Confira a demanda de insumos']
def bloco(titulo,desc,corpo,acao='',tit_hole=False):
    t=titulo if tit_hole else esc(titulo)
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{t}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>{acao}</div>'
            f'<div style="padding: 0 12px 12px;">{corpo}</div></section>')
def kline(hole,st=''):
    return f'<div style="font-size: 13px; color: {MUTED}; {st}"><span style="{H(st) if st and st.startswith("k") else ""}">{H(hole)}</span></div>'
def navpe():
    return (f'<div style="display: flex; align-items: center; gap: 10px; padding-top: 4px;">'
            f'<sc-if value="{H("has_prev")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("prev")}" style="{_MINI} font-size: 13px; padding: 8px 12px;">{H("prev_t")}</button></sc-if>'
            f'<span style="flex-grow: 1;"></span>'
            f'<sc-if value="{H("has_next")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("next")}" style="{_MINI} font-size: 13px; padding: 8px 12px;">{H("next_t")}</button></sc-if></div>')
def build():
    fname='SAF.dc.html'; E._reset_screen(fname)
    meses=D2.MESES
    # ---------- etapa 1 · safras ----------
    g_saf=grid([dict(k='nome',l='Safra'),dict(k='faz',l='Fazenda'),dict(k='n',l='Cultivos',t='num',a='r'),dict(k='area',l='Área',t='num',a='r',u='ha'),dict(k='estado',l='Estado'),dict(k='acao',l='Abrir')],
       [dict(id=s['id'],ro=s['ro'],v=dict(nome=s['nome'],periodo=s['periodo'],faz=s['fazenda'],estado=s['estado']),s={},p={}) for s in D2.SAFRAS],
       edit=dict(m='form',title='Safra',newTitle='Nova safra',sub='Altere nome, período e fazenda. Cultivos e planos ficam nas etapas seguintes.',
                 fields=[dict(k='nome',l='Nome da safra',t='txt',req=True,def_='' ),dict(k='periodo',l='Período',t='txt',req=True,help='Ex.: set/2027 – ago/2028'),
                         dict(k='faz',l='Fazenda',t='sel',opts=['Santa Rita','Boa Vista'],req=True,**{'def':'Santa Rita'}),dict(k='estado',l='Estado',t='sel',opts=['Rascunho','Em planejamento'],**{'def':'Rascunho'})]),
       add=None,gid='g_saf',total=False)
    # ---------- etapa 2 · cultivos por safra ----------
    TALH={t:ha for t,ha,*_ in D.TALHOES}
    CULT_COLS=[dict(k='local',l='Talhão ou parcela',w=180),dict(k='faz',l='Fazenda'),dict(k='cult',l='Cultura'),dict(k='var',l='Variedade'),
               dict(k='area',l='Área',t='num',a='r',u='ha',agg='sum',d=2,dmin=0),dict(k='dt_plantio',l='Plantio',t='num'),dict(k='meta',l='Meta',a='r'),
               dict(k='plano',l='Plano e ajustes',w=170)]
    CULT_FIELDS=[dict(k='talhao',l='Talhão',t='sel',opts=list(TALH),req=True,newOnly=True,**{'def':'T1'},
                      help='Áreas: '+' · '.join(f'{t} {ha} ha' for t,ha in TALH.items())),
                 dict(k='local',l='Parcela',t='txt',help='Em branco: o sistema usa o nome do talhão ou a próxima parcela (ex.: T3-A).'),
                 dict(k='faz',l='Fazenda',ro=True,**{'def':'Santa Rita'}),
                 dict(k='cult',l='Cultura',t='sel',opts=['Soja','Milho','Feijão','Café','Mamão Formosa'],req=True,**{'def':'Soja'}),
                 dict(k='var',l='Variedade',t='txt',req=True),dict(k='area',l='Área',t='num',req=True,min=0.01,max=1000,u='ha'),
                 dict(k='plantio',l='Plantio',t='date',req=True),dict(k='meta',l='Meta de produtividade',t='num',req=True,min=0),
                 dict(k='unm',l='Unidade da meta',t='sel',opts=['sc/ha','t/ha/ano','kg/ha'],req=True,**{'def':'sc/ha'})]
    def talhao_de(c):
        return c['local'] if c['tipo']!='Parcela' else c['local'].rsplit('-',1)[0]
    def cult_rows(k):
        out=[]; grp={}
        for c in D2.CULTIVOS.get(k,[]):
            t=talhao_de(c)
            r=dict(id=c['id'],ro=c['ro'],v=dict(talhao=t,faz=c['fazenda'],local=c['local'],tipo=c['tipo'],cult=c['cultura'],var=c['variedade'],area=c['area'],
                   plantio=c['plantio'],meta=c['meta'],unm=c['un_meta'],plano=c['plano'] or '',colheita=c['colheita'] or ''),s={},p={})
            if c['tipo']=='Parcela':
                if t not in grp:
                    grp[t]=dict(id='grp_'+t,grp=True,dr='div_'+t,ro=c['ro'],v=dict(talhao=t,faz=c['fazenda'],local=t),s={},p={},kids=[]); out.append(grp[t])
                grp[t]['kids'].append(r)
            else: out.append(r)
        return out
    cult_html=''
    for k in ['S2627','S27SF','S2526','NOVA']:
        rows=cult_rows(k)
        ro=(k=='S2526')
        bulk=f'<button type="button" onClick="{H("ap_bulk")}" style="{_MINIP}">Aplicar plano</button>' if not ro else ''
        g=grid(CULT_COLS,rows,edit=dict(m='form',title='Cultivo',newTitle='Novo cultivo',sub='Altere o cultivo e salve. O plano aplicado e os ajustes locais são preservados.',fields=CULT_FIELDS),
               sel=not ro,dele=not ro,add=None,bulk=bulk,gid=f'g_cult_{k}',total=True,tree=True,x0={r['id']:True for r in rows if r.get('kids')})
        cult_html+=f'<sc-if value="{H("cult_"+k)}" hint-placeholder-val="{F()}">{g}</sc-if>'
    # ---------- etapa 3 · rendimentos (uma grade por safra: a edição vale só para a safra aberta; safra encerrada abre só em consulta) ----------
    ops={}
    for c in D2.CONJ: ops.setdefault(c['op'],[]).append(c)
    def rend_rows():
        out=[]
        for i,(op,cs) in enumerate(ops.items()):
            kids=[]
            for c in cs:
                ch=D2.custo_h(c); cha=ch/c['rend']
                calc=bool(c.get('larg'))
                kids.append(dict(id=c['id'],v=dict(nome=c['conj'],op=op,modo=('Largura × velocidade' if calc else 'Informado'),larg=c.get('larg',''),vel=c.get('vel',''),efic=c.get('efic',''),
                     rend=c['rend'],maq=c['maq'],impl=c['impl'],pess=c['pess'],pess_rs=c['pess_rs'],pes_h=c['pess']*c['pess_rs'],
                     custo_h=round(ch,2),custo_ha=round(cha,2),custo_kg=0),s={},p={},rec=dict(c['rec'])))
            out.append(dict(id=f'op{i}',ro=True,v=dict(nome=op),s={},p=dict(nome=[{'k':'b','t':op}]),kids=kids))
        return out
    MODO_CALC=dict(k='modo',eq='Largura × velocidade'); MODO_INF=dict(k='modo',eq='Informado')
    REND_COLS=[dict(k='nome',l='Operação · conjunto',w=220),dict(k='param',l='Largura · velocidade · eficiência',w=190),dict(k='rend',l='Rendimento (ha/h)',t='num',a='r',d=2),
               dict(k='custo_h',l='Custo (R$/h)',t='num',a='r',d=2,w=270),dict(k='custo_ha',l='Custo (R$/ha)',t='num',a='r',d=2),dict(k='custo_kg',l='Custo (R$/kg)',t='num',a='r',d=4,zdash=True,w=110)]
    REND_EDIT=dict(m='form',title='Rendimento',leafOnly=True,sub='Informe como o conjunto trabalha e quanto custa por hora; rendimento e custos por hectare e por quilo são recalculados. Vale só para esta safra.',
            fields=[dict(k='modo',l='Como obter o rendimento',t='sel',opts=['Largura × velocidade','Informado'],req=True,**{'def':'Largura × velocidade'}),
                    dict(k='larg',l='Largura de trabalho',t='num',req=True,min=0.5,max=60,u='m',cond=MODO_CALC),
                    dict(k='vel',l='Velocidade de trabalho',t='num',req=True,min=0.5,max=30,u='km/h',cond=MODO_CALC),
                    dict(k='efic',l='Eficiência de campo',t='num',req=True,min=10,max=100,u='%',cond=MODO_CALC,help='Descontadas manobras, abastecimento e paradas.'),
                    dict(k='rend_c',l='Rendimento efetivo',ro=True,live=True,u='ha/h',cond=MODO_CALC,help='Largura × velocidade ÷ 10 × eficiência.'),
                    dict(k='rend',l='Rendimento efetivo',t='num',req=True,min=0.01,u='ha/h',cond=MODO_INF,help='Use quando não há largura de trabalho (ex.: tratamento de sementes, colheita manual, gotejo).'),
                    dict(k='maq',l='Máquina',t='num',req=True,min=0,u='R$/h',help='Inclua combustível, manutenção e depreciação; o operador entra em Pessoas.'),dict(k='impl',l='Implemento',t='num',min=0,u='R$/h'),
                    dict(k='pess',l='Pessoas na equipe',t='num',req=True,min=0,u='pessoas'),dict(k='pess_rs',l='Custo por pessoa',t='num',min=0,u='R$/h'),
                    dict(k='custo_c',l='Custo por hora',ro=True,live=True,u='R$/h',help='Máquina + implemento + pessoas × custo por pessoa.')])
    rend_html=''
    for k in ['S2627','S27SF','S2526','NOVA']:
        rrows=rend_rows()
        g=grid(REND_COLS,rrows,edit=(dict(REND_EDIT,m='ro') if k=='S2526' else REND_EDIT),tree=True,gid=f'g_rend_{k}',total=False,x0={r['id']:True for r in rrows})
        rend_html+=f'<sc-if value="{H("rend_"+k)}" hint-placeholder-val="{F()}">{g}</sc-if>'
    # ---------- etapa 4 · plano operacional ----------
    g_op=grid([dict(k='nome',l='Atividade',w=200),dict(k='op',l='Operação · data',w=200),dict(k='mes',l='Mês'),dict(k='area',l='Área (ha)',t='num',a='r',agg='sum'),
               dict(k='horas',l='Horas (h)',t='num',a='r',d=1,agg='sum'),dict(k='cop',l='Operação (R$)',t='num',a='r',agg='sum'),dict(k='cins',l='Insumos (R$)',t='num',a='r',agg='sum'),
               dict(k='ctot',l='Total (R$)',t='num',a='r',agg='sum'),dict(k='rha',l='R$/ha',t='num',a='r',d=2)],
       [],edit=dict(m='pick',leafOnly=False),tree=True,gid='g_op',total=True)
    MCOLS=[dict(k='ind',l='Indicador',w=190)]+[dict(k=f'm{i}',l=lab,t='num',a='r') for i,(_,lab) in enumerate(meses)]+[dict(k='tot',l='Total do período',t='num',a='r')]
    g_mat=grid(MCOLS,[],edit=dict(m='none'),search=False,gid='g_mat',total=False,headtools=False)
    # ---------- etapa 5 · recursos ----------
    g_recp=grid([dict(k='nome',l='Recurso'),dict(k='un',l='Unidades',t='num',a='r'),dict(k='jornada',l='Jornada (h/dia)',t='num',a='r'),dict(k='turnos',l='Turnos',t='num',a='r'),dict(k='manut',l='Manutenção (h/mês)',t='num',a='r')],
       [dict(id=r['id'],v=dict(nome=r['nome'],un=r['un'],jornada=r['jornada'],turnos=r['turnos'],manut=r['manut']),s={},p={}) for r in D2.RECURSOS],
       edit=dict(m='form',title='Recurso',sub='A capacidade mensal é unidades × dias úteis × jornada × turnos − manutenção.',
            fields=[dict(k='un',l='Unidades disponíveis',t='num',req=True,min=0,max=50),dict(k='jornada',l='Jornada',t='num',req=True,min=1,max=24,u='h/dia'),
                    dict(k='turnos',l='Turnos por dia',t='num',req=True,min=1,max=3),dict(k='manut',l='Indisponível por manutenção',t='num',req=True,min=0,u='h/mês')]),
       search=False,gid='g_recp',total=False)
    RCOLS=[dict(k='ind',l='Recurso · indicador',w=190)]+[dict(k=f'm{i}',l=lab,t='num',a='r') for i,(_,lab) in enumerate(meses)]+[dict(k='tot',l='Total',t='num',a='r')]
    g_res=grid(RCOLS,[],edit=dict(m='pick',leafOnly=True),tree=True,search=False,gid='g_res',total=False,headtools=False,x0={f'R_{r["id"]}':True for r in D2.RECURSOS})
    g_resd=grid([dict(k='ind',l='Atividade',w=240)]+[dict(k=f'm{i}',l=lab,t='num',a='r',d=1) for i,(_,lab) in enumerate(meses)]+[dict(k='tot',l='Total (h)',t='num',a='r',d=1)],
                [],edit=dict(m='none'),search=False,gid='g_resd',total=False,headtools=False)
    # ---------- etapa 6 · demanda ----------
    g_dem=grid([dict(k='ins',l='Grupo · insumo',w=230),dict(k='uso',l='1º uso',t='num'),dict(k='bruta',l='Demanda bruta',t='num',a='r'),dict(k='est',l='Estoque disponível',t='num',a='r'),dict(k='rec',l='Recebimentos previstos',t='num',a='r'),
                dict(k='liq',l='Necessidade líquida',t='num',a='r'),dict(k='preco',l='Preço (R$/un)',t='num',a='r',d=2),dict(k='valor',l='Valor (R$)',t='num',a='r',d=2,agg='sum'),dict(k='sit',l='Situação')],
       [],edit=dict(m='origin',leafOnly=True,title='Insumo',fields=[dict(k='ins',l='Insumo',t='txt',ro=True),dict(k='un',l='Unidade',t='txt',ro=True)]),tree=True,gid='g_dem',total=True)
    # ---------- JS do processo ----------
    sol0={'S2627':dict(id='SOL-2026-07',at='23/09/2026',itens={n:round(o['liq'],3) for n,o in D2.demanda('S2627').items() if o['liq']>0.001},comp=0)}
    d2=dict(D2.js_data()); d2['sol']=sol0; d2['talhoes']=TALH
    EXTRAJS[0]='const D2 = '+json.dumps(d2,ensure_ascii=False)+';\n'+open(os.path.join(ROOT,'safra.js')).read()+'''
function _safhooks(self){ self.g2after=(gid,rows,r,isNew)=>{ if(gid==='g_saf' && r && String(r.id).indexOf('n')===0 && !self.state.saf){ if(!r.v.estado) r.v.estado='Rascunho'; self.setState({saf:r.id,step:2,g2toast:'Safra criada: '+r.v.nome+'. Defina os cultivos.'}); }
    if(String(gid).indexOf('g_cult_')===0) cultAfter(self,gid,rows,r,isNew);
    if(String(gid).indexOf('g_rend_')===0&&r) rendAfter(self,gid,rows,r); };
  self.g2live=(gid,k,d)=>(String(gid).indexOf('g_rend_')===0?rendLive(k,d):null);
  self.g2check=(gid,rows,r,d,isNew)=>(String(gid).indexOf('g_cult_')===0?cultCheck(self,gid,rows,r,d,isNew):(String(gid).indexOf('g_rend_')===0?rendCheck(d):null));
  self.g2pick=(gid,rid,r)=>{ if(gid==='g_op'){ const pid=String(rid).split('_')[0]; self.setState({atv:(self.state.atv===pid?null:pid)}); } if(gid==='g_res'){ const k=String(rid).replace('R_',''); self.setState({rec:(self.state.rec===k?null:k)}); } }; }
const _EV=EXTRAVALS; EXTRAVALS=function(self,v){ _safhooks(self); _EV(self,v); v.ap_bulk=()=>openApply(self,null); };'''
    # ---------- corpo ----------
    s1=bloco('Escolha a safra','Abra uma safra da lista ou crie uma nova; clique na linha para editar nome e período.',g_saf)
    s2=(f'<div style="font-size: 13px; color: {MUTED};">{H("k2")}</div>'
        + bloco('Cultivos e planos','Defina onde, o quê e quando plantar; divida o talhão em quantas parcelas precisar. Clique na linha para editar e no nome do plano para ajustar as atividades.',cult_html))
    s3=bloco('Rendimentos por operação e conjunto','Clique no conjunto para informar largura, velocidade, eficiência e custos; rendimento e custos por hectare e por quilo são calculados.',rend_html)
    s4=(f'<div style="font-size: 13px; color: {MUTED};">{H("k4")}</div>'
        + bloco('Plano operacional por atividade','Clique numa atividade para ver o detalhamento mensal; expanda para ver cada cultivo.',g_op)
        + bloco(H('mat_titulo'),'Confira indicadores na vertical e meses na horizontal, com o total do período.',g_mat,
                acao=f'<sc-if value="{H("mat_sel")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("mat_todas")}" style="{_MINI}">Ver todas as atividades</button></sc-if>',tit_hole=True))
    dias=' · '.join(f'{lab} {D2.DIAS_UTEIS[k]}' for k,lab in meses)
    s5=(f'<div style="font-size: 13px;"><span style="{H("k5st")}">{H("k5")}</span></div>'
        + bloco('Parâmetros dos recursos','Ajuste unidades, jornada, turnos e manutenção; a capacidade é recalculada.',
                f'<div style="font-size: 12px; color: {MUTED}; padding: 0 4px 8px;">Dias úteis por mês: {dias}</div>'+g_recp)
        + bloco('Demanda × capacidade por mês','Confira faltas em vermelho e sobras em verde; clique num recurso para ver a origem da demanda.',g_res)
        + f'<sc-if value="{H("resd_sel")}" hint-placeholder-val="{F()}">' + bloco(H('resd_titulo'),'Confira as atividades que consomem as horas deste recurso em cada mês.',g_resd,tit_hole=True) + '</sc-if>')
    s6=(f'<div style="font-size: 13px; color: {MUTED};">{H("k6")}</div>'
        + bloco('Demanda de insumos por grupo','Confira a necessidade líquida e envie para cotação; clique num insumo para ver de onde vem a demanda.',g_dem,
                acao=f'<sc-if value="{H("sol_link")}" hint-placeholder-val="{F()}"><a href="CMP.dc.html" style="{_MINI} text-decoration: none;">Abrir em Compra de insumos ›</a></sc-if>'))
    corpo=''.join(f'<sc-if value="{H("s"+str(i))}" hint-placeholder-val="{H("true") if i==1 else F()}"><div style="display: flex; flex-direction: column; gap: 14px;">{s}{navpe()}</div></sc-if>'
                  for i,s in enumerate([s1,s2,s3,s4,s5,s6],1))
    # ---------- painel: aplicar plano ----------
    EXTRA.append(
      f'<sc-if value="{H("ap_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar" onClick="{H("ap_cancel")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="{H("ap_titulo")}" style="position: relative; width: 480px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
      f'<h2 style="margin: 0; font-family: {DISP}; font-size: 19px;">{H("ap_titulo")}</h2><div style="font-size: 13px; color: {MUTED};">Escolha um plano da mesma cultura. Cada cultivo recebe o plano padrão; ajustes locais podem ser feitos depois.</div>'
      f'<div style="display: flex; flex-direction: column; gap: 4px;"><sc-for list="{H("ap_itens")}" as="it" hint-placeholder-count="2"><div style="font-size: 13px; padding: 6px 10px; border-radius: 8px; background: {BG};">{H("it.t")}</div></sc-for></div>'
      f'<sc-if value="{H("ap_mix")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("ap_mixmsg")}</div></sc-if>'
      f'<sc-if value="{H("ap_no_opts")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; color: {RED}; font-weight: 700;">Não há plano publicado para esta cultura. Crie um em Planos agronômicos.</div></sc-if>'
      f'<sc-if value="{H("ap_has_opts")}" hint-placeholder-val="{F()}"><label for="ap_sel" style="font-size: 12px; font-weight: 600; color: {MUTED};">Plano agronômico</label>'
      f'<select id="ap_sel" value="{H("ap_plan")}" onChange="{H("ap_setplan")}" style="font-family: inherit; font-size: 14px; padding: 9px 11px; border-radius: 10px; border: 1px solid {LINE};"><sc-for list="{H("ap_opts")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>'
      f'<sc-if value="{H("ap_haserr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("ap_err")}</span></sc-if></sc-if>'
      f'<div style="flex-grow: 1;"></div>'
      f'<sc-if value="{H("ap_confirm")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.8px; font-weight: 700;">{H("ap_cmsg")}'
      f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("ap_back")}" style="{_MINI}">Voltar</button><button type="button" onClick="{H("ap_yes")}" style="{_MINIP}">Confirmar substituição</button></div></div></sc-if>'
      f'<sc-if value="{H("ap_normal")}" hint-placeholder-val="{H("true")}"><div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};"><button type="button" onClick="{H("ap_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" onClick="{H("ap_apply")}" style="{BTN_ST(True,True)}">Aplicar plano</button></div></sc-if>'
      f'</aside></div></sc-if>')
    # ---------- painel: atividades locais do cultivo (Gatilho → Atividades → Produtos e doses) ----------
    prod_row=(f'<div style="display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1.6fr) 88px 122px 82px 94px 64px; gap: 10px; align-items: center; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 12.5px;">'
              f'<span style="color: {MUTED};">{H("p.grupo")}</span><span style="font-weight: 600;">{H("p.nome")}<sc-if value="{H("p.aj")}" hint-placeholder-val="{F()}"> <span style="display: inline-block; padding: 1px 7px; border-radius: 999px; background: {YELS}; color: {YEL}; font-size: 11px; font-weight: 700;">ajuste local</span></sc-if></span>'
              f'<span style="color: {MUTED}; white-space: nowrap; text-align: right;">{H("p.padrao")}</span>'
              f'<span style="display: flex; align-items: center; gap: 4px; white-space: nowrap;"><input id="{H("p.fid")}" aria-label="Dose local de {H("p.nome")}" value="{H("p.v")}" onChange="{H("p.set")}" readOnly="{H("p.dis")}" style="{H("p.ist")}"><span style="color: {MUTED}; font-size: 11.5px;">{H("p.un")}</span></span>'
              f'<span style="color: {MUTED}; white-space: nowrap; text-align: right;">{H("p.preco")}</span><span style="font-weight: 700; white-space: nowrap; text-align: right;">{H("p.custo")}</span>'
              f'<sc-if value="{H("p.aj")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("p.reset")}" title="Voltar à dose do plano padrão" style="{_MINI} font-size: 11px; padding: 3px 7px;">Restaurar</button></sc-if></div>'
              f'<sc-if value="{H("p.hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 11.5px; color: {RED}; font-weight: 700;">{H("p.err")}</div></sc-if>')
    EXTRA.append(
      f'<sc-if value="{H("lp_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar" onClick="{H("lp_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="{H("lp_titulo")}" style="position: relative; width: 840px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
      f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1;">{H("lp_titulo")}</h2><button type="button" aria-label="Fechar" onClick="{H("lp_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED};">×</button></div>'
      f'<div style="font-size: 13px; color: {MUTED};">{H("lp_sub")}</div>'
      f'<sc-if value="{H("lp_nerr")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">Corrija as doses destacadas; o que você digitou foi mantido.</div></sc-if>'
      f'<sc-for list="{H("lp_grupos")}" as="g" hint-placeholder-count="1"><div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase; padding-top: 4px;">{H("g.t")}</div>'
      f'<sc-for list="{H("g.gats")}" as="t" hint-placeholder-count="2"><div style="border: 1px solid {LINE}; border-radius: 12px; overflow: hidden;">'
      f'<div style="display: flex; align-items: center; gap: 8px; padding: 8px 10px; background: {BG};"><button type="button" class="g2car" aria-label="{H("t.lab")}" onClick="{H("t.tog")}">{H("t.sym")}</button><b style="font-size: 13.5px;">{H("t.t")}</b><span style="font-size: 12px; color: {MUTED};">· {H("t.dt")}</span></div>'
      f'<sc-if value="{H("t.open")}" hint-placeholder-val="{H("true")}"><div style="padding: 4px 12px 10px;"><sc-for list="{H("t.atvs")}" as="a" hint-placeholder-count="1"><div style="padding: 6px 0;">'
      f'<div style="display: flex; align-items: center; gap: 8px;"><button type="button" class="g2car" aria-label="{H("a.lab")}" onClick="{H("a.tog")}">{H("a.sym")}</button><span style="font-size: 13px; font-weight: 700;">{H("a.t")}</span><span style="font-size: 12px; color: {MUTED};">· {H("a.op")}</span></div>'
      f'<sc-if value="{H("a.open")}" hint-placeholder-val="{H("true")}"><div style="padding-left: 30px;"><sc-if value="{H("a.semProd")}" hint-placeholder-val="{F()}"><div style="font-size: 12px; color: {MUTED}; padding: 4px 0;">Sem insumos · só operação</div></sc-if>'
      f'<sc-for list="{H("a.prods")}" as="p" hint-placeholder-count="1">{prod_row}</sc-for></div></sc-if></div></sc-for></div></sc-if></div></sc-for></sc-for>'
      f'<div style="flex-grow: 1;"></div>'
      f'<sc-if value="{H("lp_warn")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("lp_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H("lp_keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
      f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};"><sc-if value="{H("lp_edit")}" hint-placeholder-val="{H("true")}"><button type="button" onClick="{H("lp_close")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" onClick="{H("lp_save")}" style="{BTN_ST(True,True)}">Salvar</button></sc-if>'
      f'<sc-if value="{H("lp_ro")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("lp_discard")}" style="{BTN_ST(False,True)}">Fechar</button></sc-if></div></aside></div></sc-if>')
    # ---------- painel: dividir o talhão em parcelas (sem limite de quantidade) ----------
    DV_COLS='92px 86px 124px minmax(110px,1fr) 138px 70px 90px minmax(140px,1.2fr) 32px'
    lab_row=''.join(f'<span>{x}</span>' for x in ['Parcela','Área (ha)','Cultura','Variedade','Plantio','Meta','Unidade','Plano',''])
    dv_row=(f'<div style="display: grid; grid-template-columns: {DV_COLS}; gap: 8px; align-items: center; padding: 7px 0; border-top: 1px solid {LINE};">'
            f'<input aria-label="Nome da parcela {H("r.lab")}" value="{H("r.local")}" onChange="{H("r.s_local")}" readOnly="{H("r.dis")}" style="{H("r.st_local")}">'
            f'<input aria-label="Área de {H("r.lab")} em hectares" inputMode="decimal" value="{H("r.area")}" onChange="{H("r.s_area")}" readOnly="{H("r.dis")}" style="{H("r.st_area")}">'
            f'<select aria-label="Cultura de {H("r.lab")}" value="{H("r.cult")}" onChange="{H("r.s_cult")}" disabled="{H("r.dis")}" style="{H("r.st_cult")}"><sc-for list="{H("r.oc")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>'
            f'<input aria-label="Variedade de {H("r.lab")}" value="{H("r.var")}" onChange="{H("r.s_var")}" readOnly="{H("r.dis")}" style="{H("r.st_var")}">'
            f'<input type="date" aria-label="Plantio de {H("r.lab")}" value="{H("r.plantio")}" onChange="{H("r.s_plantio")}" readOnly="{H("r.dis")}" style="{H("r.st_plantio")}">'
            f'<input aria-label="Meta de {H("r.lab")}" inputMode="decimal" value="{H("r.meta")}" onChange="{H("r.s_meta")}" readOnly="{H("r.dis")}" style="{H("r.st_meta")}">'
            f'<select aria-label="Unidade da meta de {H("r.lab")}" value="{H("r.unm")}" onChange="{H("r.s_unm")}" disabled="{H("r.dis")}" style="{H("r.st_unm")}"><sc-for list="{H("r.ou")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>'
            f'<span style="{H("r.pst")}">{H("r.plano")}</span>'
            f'<span><sc-if value="{H("r.notAsk")}" hint-placeholder-val="{H("true")}"><button type="button" class="g2del" aria-label="Excluir parcela {H("r.lab")}" title="Excluir parcela" onClick="{H("r.rm")}">×</button></sc-if></span></div>'
            f'<sc-if value="{H("r.ask")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 7px 10px; margin-bottom: 6px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("r.askMsg")}<span style="flex-grow: 1;"></span><button type="button" onClick="{H("r.rmNo")}" style="{_MINI}">Cancelar</button><button type="button" onClick="{H("r.rm")}" style="{_MINI} color: {RED}; border-color: {RED};">Excluir parcela</button></div></sc-if>'
            f'<sc-if value="{H("r.hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 12px; color: {RED}; font-weight: 700; padding: 0 0 6px;">{H("r.errMsg")}</div></sc-if>')
    EXTRA.append(
      f'<sc-if value="{H("dv_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar" onClick="{H("dv_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="{H("dv_titulo")}" onKeyDown="{H("dv_key")}" style="position: relative; width: 1060px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
      f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1;">{H("dv_titulo")}</h2><button type="button" aria-label="Fechar" onClick="{H("dv_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED};">×</button></div>'
      f'<div style="font-size: 13px; color: {MUTED};">Defina quantas parcelas precisar e os dados de cada uma; a soma não pode passar da área do talhão.</div>'
      f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 9px 12px; border-radius: 10px; background: {BG}; font-size: 13px;"><b>{H("dv_n")}</b><span style="color: {MUTED};">{H("dv_resumo")}</span><span role="status" style="{H("dv_selost")}">{H("dv_selo")}</span></div>'
      f'<sc-if value="{H("dv_hasg")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("dv_gerr")}</div></sc-if>'
      f'<div style="overflow-x: auto;"><div style="min-width: 940px;">'
      f'<div style="display: grid; grid-template-columns: {DV_COLS}; gap: 8px; font-size: 10.5px; font-weight: 700; letter-spacing: .03em; text-transform: uppercase; color: {MUTED}; padding-bottom: 4px;">{lab_row}</div>'
      f'<sc-for list="{H("dv_rows")}" as="r" hint-placeholder-count="2">{dv_row}</sc-for></div></div>'
      f'<sc-if value="{H("dv_edit")}" hint-placeholder-val="{H("true")}"><div style="display: flex; gap: 8px; flex-wrap: wrap;"><button type="button" onClick="{H("dv_add")}" style="{_MINI}">+ Adicionar parcela</button><button type="button" onClick="{H("dv_dist")}" style="{_MINI}">Distribuir área igualmente</button></div></sc-if>'
      f'<div style="flex-grow: 1;"></div>'
      f'<sc-if value="{H("dv_warn")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("dv_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H("dv_keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
      f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};"><sc-if value="{H("dv_edit")}" hint-placeholder-val="{H("true")}"><button type="button" onClick="{H("dv_close")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" onClick="{H("dv_save")}" style="{BTN_ST(True,True)}">Salvar divisão</button></sc-if>'
      f'<sc-if value="{H("dv_ro")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("dv_discard")}" style="{BTN_ST(False,True)}">Fechar</button></sc-if></div></aside></div></sc-if>')
    prim=f'<button type="button" onClick="{H("prim_fn")}" style="{H("prim_st")}">{H("prim_t")}</button>'
    HEIGHTS37[fname]=1500
    shell37('SAF','Planejar safra',corpo,fname=fname,subtitle='Escolha a safra e percorra as etapas; cada etapa usa o que foi salvo nas anteriores.',
            steps=steps_state(NOMES),primary_html=prim,ctx=('Fazenda Santa Rita',H('ctx_saf'),None),search=False)
