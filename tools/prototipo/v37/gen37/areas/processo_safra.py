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
def bloco(titulo,desc,corpo,acao='',tit_hole=False,desc_hole=False):
    t=titulo if tit_hole else esc(titulo); desc=desc if desc_hole else esc(desc)
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{t}</h3><div style="font-size: 12.8px; color: {MUTED};">{desc}</div></div>{acao}</div>'
            f'<div style="padding: 0 12px 12px;">{corpo}</div></section>')
def kline(hole,st=''):
    return f'<div style="font-size: 13px; color: {MUTED}; {st}"><span style="{H(st) if st and st.startswith("k") else ""}">{H(hole)}</span></div>'
def build():
    fname='SAF.dc.html'; E._reset_screen(fname)
    meses=D2.MESES
    # ---------- etapa 1 · safras ----------
    g_saf=grid([dict(k='nome',l='Safra'),dict(k='faz',l='Fazenda'),dict(k='n',l='Cultivos',t='num',a='r'),dict(k='area',l='Área',t='num',a='r',u='ha'),dict(k='estado',l='Estado'),dict(k='acao',l='Próximo passo',w=290)],
       [dict(id=s['id'],ro=s['ro'],v=dict(nome=s['nome'],ini=s['ini'],fim=s['fim'],periodo=s['periodo'],faz=s['fazenda'],estado=s['estado']),s={},p={}) for s in D2.SAFRAS],
       edit=dict(m='form',title='Safra',newTitle='Nova safra',sub='Altere nome, início, fim e fazenda. Cultivos e planos ficam nas etapas seguintes.',
                 fields=[dict(k='nome',l='Nome da safra',t='txt',req=True,def_='' ),dict(k='ini',l='Início',t='date',req=True),dict(k='fim',l='Fim',t='date',req=True,help='O fim precisa ser depois do início.'),
                         dict(k='faz',l='Fazenda',t='sel',opts=['Santa Rita','Boa Vista'],req=True,**{'def':'Santa Rita'}),dict(k='estado',l='Estado',t='sel',opts=['Rascunho','Em planejamento'],**{'def':'Rascunho'})]),
       add=None,gid='g_saf',total=False)
    # ---------- etapa 2 · cultivos por safra ----------
    TALH={t:ha for t,ha,*_ in D.TALHOES}
    import dados_lagoa_safra as DL
    TALFAZ={t:'Santa Rita' for t in TALH}; TALFAZ.update(DL.TALFAZ); TALH.update(DL.TALHOES)   # pivôs da Lagoa Grande
    # TABELAS-FOCO (5983172395): uma variável por coluna (tipo, área livre, unidade da meta, versão e ajustes separados)
    # o plano (e a ação Aplicar plano) fica à vista: logo depois da variedade
    CULT_COLS=[dict(k='local',l='Talhão ou parcela',w=130),dict(k='tipo',l='Tipo',w=120),dict(k='cult',l='Cultura'),dict(k='var',l='Variedade'),
               dict(k='plano',l='Plano agronômico',w=190),dict(k='ver',l='Versão'),dict(k='area',l='Área (ha)',t='num',a='r',agg='sum',d=2,dmin=0),dict(k='dt_plantio',l='Plantio',t='num'),
               dict(k='meta',l='Meta',t='num',a='r'),dict(k='unm',l='Unidade da meta',w=110),dict(k='livre',l='Área livre (ha)',t='num',a='r',d=2,dmin=0),dict(k='aj',l='Ajustes locais',t='num',a='r')]
    CULT_FIELDS=[dict(k='talhao',l='Talhão',t='sel',opts=list(TALH),req=True,newOnly=True,**{'def':'T1'},
                      help='Áreas: '+' · '.join(f'{t} '+format(ha,'g').replace('.',',')+' ha' for t,ha in TALH.items())),
                 dict(k='local',l='Parcela',t='txt',help='Em branco: o sistema usa o nome do talhão ou a próxima parcela (ex.: T3-A).'),
                 dict(k='faz',l='Fazenda',ro=True,**{'def':'Santa Rita'}),
                 dict(k='cult',l='Cultura',t='sel',opts=['Soja','Milho','Feijão','Café','Mamão Formosa'],req=True,**{'def':'Soja'}),
                 dict(k='var',l='Variedade',t='txt',req=True),dict(k='area',l='Área',t='num',req=True,min=0.01,max=1000,u='ha'),
                 dict(k='plantio',l='Plantio',t='date',req=True),dict(k='meta',l='Meta de produtividade',t='num',req=True,min=0),
                 dict(k='unm',l='Unidade da meta',t='sel',opts=['sc/ha','t/ha/ano','kg/ha'],req=True,**{'def':'sc/ha'}),
                 dict(k='plano',l='Plano agronômico',t='sel',dyn=True,opts=[],
                      help='Planos publicados da cultura escolhida. Trocar o plano descarta os ajustes de insumos deste cultivo.')]
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
    for k in ['S2627','S27SF','S2526','LG2627','NOVA']:
        rows=cult_rows(k)
        ro=(k=='S2526')
        bulk=f'<button type="button" onClick="{H("ap_bulk")}" style="{_MINIP}">Aplicar plano</button>' if not ro else ''
        g=grid(CULT_COLS,rows,edit=dict(m='form',title='Cultivo',newTitle='Novo cultivo',sub='Altere o cultivo e o plano agronômico e salve.',fields=CULT_FIELDS),
               sel=not ro,dele=not ro,add=None,bulk=bulk,gid=f'g_cult_{k}',qf=dict(k='cult'),total=True,tree=True,x0={r['id']:True for r in rows if r.get('kids')})
        cult_html+=f'<sc-if value="{H("cult_"+k)}" hint-placeholder-val="{F()}">{g}</sc-if>'
    # ---------- etapa 3 · rendimentos (uma grade por safra: a edição vale só para a safra aberta; safra encerrada abre só em consulta) ----------
    ops={}
    for c in D2.CONJ: ops.setdefault(c['op'],[]).append(c)
    import dados_cad as DC
    from areas.cad_ativos_pessoas import PREQ   # potência mínima (cv) exigida pelo implemento, a mesma regra do cadastro de máquinas
    AT_N={a['nome']:a for a in DC.ATIVOS}; TRAT=[a for a in DC.ATIVOS if a['classe']=='Trator']
    conj_opts={}
    for _k,tr,impl,_op,rid in DC.CONJUNTOS:
        c=next((x for x in D2.CONJ if x['id']==rid),None); im=AT_N.get(impl) if impl else None
        if not c or not tr.startswith('Trator') or not im: continue
        atual=AT_N[tr]['id']; pmin=PREQ.get(im['id'],0)
        conj_opts[rid]=dict(pmin=pmin,impl=im['nome'],atual=atual+'+'+im['id'],
            opts=[dict(id=t['id']+'+'+im['id'],nome=(c['conj'] if t['id']==atual else f"{t['nome']} {t['modelo']} + {im['nome']}"),pot=t['pot'],maq=t['custo_h'],impl=im['custo_h'])
                  for t in TRAT if t['pot']>=pmin])
    for c in D2.CONJ:
        if c['id'] not in conj_opts: conj_opts[c['id']]=dict(pmin=0,impl='',atual=c['id'],opts=[dict(id=c['id'],nome=c['conj'],pot=0,maq=c['maq'],impl=c['impl'])])
    # atividades de cada operação nos planos publicados (a mesma operação pode ter rendimento e conjunto diferentes por atividade)
    ATV={}
    for _pl in D2.PLANOS:
        for _a in _pl['atividades']: ATV.setdefault(_a['op'],{}).setdefault(_a['nome'],[]).append(_pl['nome'])
    def rend_v(c,atv,pls,op,base_id):
        # rendimento pelos parâmetros, com a precisão toda (12 m × 7 km/h × 81 % = 6,804 ha/h; o cadastro guarda 6,8): salvar sem mudar não altera horas
        ch=D2.custo_h(c); calc=bool(c.get('larg')); cid=conj_opts.get(c['id'],{}).get('atual',c['id']) if c.get('conj_id') is None else c['conj_id']; rend=D2.rend_efetivo(c)
        return dict(atv=atv,opatv=op+' · '+atv,planos=', '.join(pls),nome=c['conj'],conj_id=cid,op=op,base=base_id,
                    modo=('Largura × velocidade' if calc else 'Informado'),larg=c.get('larg',''),vel=c.get('vel',''),efic=c.get('efic',''),
                    rend=rend,maq=c['maq'],impl=c['impl'],pess=c['pess'],pess_rs=c['pess_rs'],pes_h=c['pess']*c['pess_rs'],
                    custo_h=round(ch,2),custo_ha=ch/rend,diesel=c.get('diesel',''),jan='',part='',seq='',troca='',multi='não')
    def rend_rows(k):
        # árvore: operação → atividade · conjunto; o rendimento e o custo ficam na atividade (cada uma pode usar outro conjunto).
        # Atividade com duas ou mais configurações (D2.cfgs_rend) vira grupo atividade → configurações; com uma só fica linha.
        out=[]
        for op,cs in ops.items():
            c=cs[0]; kids=[]
            for i,(atv,pls) in enumerate((ATV.get(op) or {op:[]}).items()):
                cfs=D2.cfgs_rend(k,op,atv); aid=f"{c['id']}.{i+1}"
                if len(cfs)==1:
                    kids.append(dict(id=aid,v=rend_v(cfs[0],atv,pls,op,c['id']),s={},p={},rec=dict(cfs[0]['rec']))); continue
                ks=[]
                for j,cf in enumerate(cfs):
                    v=rend_v(cf,atv,pls,op,c['id']); v['multi']='sim'; v['seq']='Ao mesmo tempo, com recursos próprios'
                    ks.append(dict(id=f'{aid}.{j+1}',v=v,s={},p={},rec=dict(cf.get('rec') or {})))
                kids.append(dict(id='atv_'+aid,grp=True,ro=True,v=dict(atv=atv,op=op,opatv=op+' · '+atv,planos=', '.join(pls)),s={},p={},kids=ks))
            out.append(dict(id='op_'+c['id'],grp=True,ro=True,v=dict(atv=op,op=op),s={},p={},kids=kids))
        return out
    MODO_CALC=dict(k='modo',eq='Largura × velocidade'); MODO_INF=dict(k='modo',eq='Informado')
    # TABELAS-FOCO (5983172395): uma variável por coluna; a árvore operação → atividade → configuração continua
    # colunas de foco primeiro (rendimento e custos); como o rendimento se obtém e a divisão da área vêm depois
    REND_COLS=[dict(k='op',l='Operação',w=160),dict(k='atv',l='Atividade',w=200),dict(k='nome',l='Conjunto',w=260),
               dict(k='rend',l='Rendimento (ha/h)',t='num',a='r',d=2),dict(k='custo_h',l='Custo (R$/h)',t='num',a='r',d=2),dict(k='custo_ha',l='Custo (R$/ha)',t='num',a='r',d=2),
               dict(k='custo_kg',l='Custo (R$/kg)',w=150),dict(k='modo',l='Modo',w=150),
               dict(k='larg',l='Largura (m)',t='num',a='r',d=2,dmin=0),dict(k='vel',l='Velocidade (km/h)',t='num',a='r',d=2,dmin=0),dict(k='efic',l='Eficiência (%)',t='num',a='r',d=1,dmin=0),
               dict(k='part',l='Parte da área (%)',t='num',a='r',d=1,dmin=0,w=150),dict(k='seq',l='Trabalha',w=130),
               dict(k='jan',l='Janela (h por talhão)',t='num',a='r',d=1,dmin=0),dict(k='planos',l='Planos',w=240)]
    NUNCA=dict(k='multi',eq='__nunca')   # campo só de rascunho: guarda contexto do formulário e não aparece
    MULTI=dict(k='multi',eq='sim'); UMA=dict(k='multi',eq='não')
    SEQ_T='Em sequência: divide trator, implemento ou operador'; PAR_T='Ao mesmo tempo, com recursos próprios'
    REND_EDIT=dict(m='form',title='Rendimento',newTitle='Nova configuração',leafOnly=True,sub='Informe como o conjunto trabalha e quanto custa por hora; rendimento e custo por hectare são recalculados (na colheita, também por quilo). Vale só para esta safra.',
            fields=[dict(k='multi',l='',t='txt',cond=NUNCA),dict(k='base',l='',t='txt',cond=NUNCA),
                    dict(k='opatv',l='Operação · atividade',t='txt',ro=True),
                    dict(k='esc',l='Aplicar em',t='sel',opts=['Todas as atividades da operação','Só esta atividade'],cond=UMA,help='Todas: conjunto, rendimento e custos vão para as outras atividades da mesma operação nesta safra (as divididas entre conjuntos ficam como estão).'),
                    dict(k='conj_id',l='Conjunto',t='sel',dyn=True,opts=[],help='Do cadastro, só tratores com a potência que o implemento exige (trocar usa os custos por hora do cadastro). Por classe ou prestador: planeja sem escolher patrimônio; o prestador traz máquina, operador e diesel.'),
                    dict(k='nome',l='Descrição do conjunto',t='txt',req=True,cond=dict(k='conj_id',eq='classe'),help='Ex.: Trator 100–140 cv + plantadeira 12 linhas. A O.S. escolhe a máquina depois.'),
                    dict(k='nome',l='Prestador e equipamento',t='txt',req=True,cond=dict(k='conj_id',eq='prestador'),help='Ex.: Prestador · plantadeira 12 linhas. A tarifa por hora do prestador vai em Máquina; não usa máquinas nem pessoas da fazenda.'),
                    dict(k='modo',l='Como obter o rendimento',t='sel',opts=['Largura × velocidade','Informado'],req=True,**{'def':'Largura × velocidade'}),
                    dict(k='larg',l='Largura de trabalho',t='num',req=True,min=0.5,max=60,u='m',cond=MODO_CALC),
                    dict(k='vel',l='Velocidade de trabalho',t='num',req=True,min=0.5,max=30,u='km/h',cond=MODO_CALC),
                    dict(k='efic',l='Eficiência de campo',t='num',req=True,min=10,max=100,u='%',cond=MODO_CALC,help='Descontadas manobras, abastecimento e paradas no campo. Manutenção e quebras entram na disponibilidade da máquina.'),
                    dict(k='rend_c',l='Rendimento efetivo',ro=True,live=True,u='ha/h',cond=MODO_CALC,help='Largura × velocidade ÷ 10 × eficiência.'),
                    dict(k='rend',l='Rendimento efetivo',t='num',req=True,min=0.01,u='ha/h',cond=MODO_INF,help='Use quando não há largura de trabalho (ex.: tratamento de sementes, colheita manual, gotejo).'),
                    dict(k='maq',l='Máquina',t='num',req=True,min=0,u='R$/h',help='Inclua combustível, manutenção e depreciação; o operador entra em Pessoas.'),dict(k='impl',l='Implemento',t='num',min=0,u='R$/h'),
                    dict(k='pess',l='Pessoas na equipe',t='num',req=True,min=0,u='pessoas'),dict(k='pess_rs',l='Custo por pessoa',t='num',min=0,u='R$/h'),
                    dict(k='custo_c',l='Custo por hora',ro=True,live=True,u='R$/h',help='Máquina + implemento + pessoas × custo por pessoa.'),
                    dict(k='diesel',l='Consumo de diesel',t='num',min=0,max=200,u='L/h',help='Opcional. Estima os litros pelas horas do conjunto; o custo do combustível já está no custo da máquina.'),
                    dict(k='jan',l='Horas disponíveis na janela',t='num',min=0,max=2000,u='h por talhão',help='Opcional. Prazo, contado do início da ocorrência, para este conjunto terminar em cada talhão ou parcela; em sequência, cada configuração termina dentro da própria janela, e a janela maior de outra não amplia a dela. A área que não couber fica sem conjunto, à vista no plano operacional.'),
                    dict(k='part',l='Parte da área',t='num',min=0,max=100,u='%',cond=MULTI,help='Vazio = divide pelo rendimento, partindo das mesmas horas para as sem %; a que para na própria janela ou na da sequência passa o resto às outras. Estimativa: não garante término no mesmo horário nem a capacidade máxima. Com %, a parte fica fixa.'),
                    dict(k='seq',l='Trabalha com as outras configurações',t='sel',opts=[PAR_T,SEQ_T],cond=MULTI,**{'def':PAR_T},help='Mesmo trator do cadastro obriga a sequência; falta de máquina ou pessoa na fazenda faz a estimativa considerar as configurações em sequência.'),
                    dict(k='troca',l='Troca entre configurações',t='num',min=0,max=24,u='h',cond=MULTI,help='Opcional. Tempo para trocar para esta configuração quando trabalham em sequência; entra no tempo decorrido e ocupa a janela. O decorrido estimado começa pela de menor troca; para cumprir os prazos, a de janela menor pode precisar ir antes.')])
    rend_html=''
    for k in ['S2627','S27SF','S2526','LG2627','NOVA']:
        rrows=rend_rows(k)
        x0={r['id']:True for r in rrows}; x0.update({a['id']:True for r in rrows for a in r['kids'] if a.get('grp')})
        g=grid(REND_COLS,rrows,edit=(dict(REND_EDIT,m='ro') if k=='S2526' else REND_EDIT),gid=f'g_rend_{k}',total=False,tree=True,x0=x0)
        rend_html+=f'<sc-if value="{H("rend_"+k)}" hint-placeholder-val="{F()}">{g}</sc-if>'
    # ---------- etapa 4 · plano operacional ----------
    # TABELAS-FOCO: a 1ª coluna é a árvore (cada linha é uma entidade do seu nível: operação › atividade › cultivo › configuração);
    # gatilho (regra da atividade) e data (da ocorrência) separados; parte, janela e talhão em colunas próprias
    g_op=grid([dict(k='nome',l='Operação › atividade › cultivo',w=280),dict(k='gat',l='Gatilho',w=120),dict(k='data',l='Data',t='num',w=100),dict(k='mes',l='Mês'),dict(k='area',l='Área (ha)',t='num',a='r',agg='sum',d=2,dmin=0),
               dict(k='horas',l='Horas-conjunto (h)',t='num',a='r',d=1,agg='sum'),dict(k='dec',l='Decorrido (h)',t='num',a='r',d=1),
               dict(k='cop',l='Operação (R$)',t='num',a='r',agg='sum'),dict(k='cins',l='Insumos (R$)',t='num',a='r',agg='sum'),
               dict(k='ctot',l='Total (R$)',t='num',a='r',agg='sum'),dict(k='rha',l='R$/ha',t='num',a='r',d=2),dict(k='diesel',l='Diesel (L)',t='num',a='r',agg='sum'),
               dict(k='part',l='Parte da área (%)',t='num',a='r',w=140),dict(k='jan',l='Janela (h por talhão)',t='num',a='r',w=140),dict(k='tal',l='Talhão',w=90)],
       [],edit=dict(m='pick',leafOnly=False),tree=True,gid='g_op',total=True)
    MCOLS=[dict(k='ind',l='Indicador',w=190)]+[dict(k=f'm{i}',l=lab,t='num',a='r') for i,(_,lab) in enumerate(meses)]+[dict(k='tot',l='Total do período',t='num',a='r')]
    g_mat=grid(MCOLS,[],edit=dict(m='none'),search=False,gid='g_mat',total=False,headtools=False)
    # ---------- etapa 5 · recursos ----------
    # recursos em duas classes, cada uma com a sua grade: máquinas e implementos × pessoas ('oper')
    # perdas: máquinas usam disponibilidade (%, multiplica); pessoas usam absenteísmo (%, desconta)
    # turnos só valem para máquinas: cada pessoa trabalha a sua jornada; dois turnos pedem mais pessoas, não mais horas por pessoa
    def recp_grid(gid,rs,unid,perda,sub,turnos):
        cT=[dict(k='turnos',l='Turnos',t='num',a='r')] if turnos else []
        fT=[dict(k='turnos',l='Turnos por dia',t='num',req=True,min=1,max=3)] if turnos else []
        return grid([dict(k='nome',l='Recurso'),dict(k='un',l=unid,t='num',a='r'),dict(k='jornada',l='Jornada (h/dia)',t='num',a='r')]+cT+[dict(k=perda['k'],l=perda['l']+' (%)',t='num',a='r',d=1,dmin=0),
                     dict(k='pico',l='Necessárias no pico',t='num',a='r'),dict(k='mpico',l='Mês do pico')],
           [dict(id=r['id'],v={**dict(nome=r['nome'],un=r['un'],jornada=r['jornada']),**({'turnos':r['turnos']} if turnos else {}),perda['k']:r[perda['k']]},s={},p={}) for r in rs],
           edit=dict(m='form',title='Recurso',sub=sub,
                fields=[dict(k='un',l=unid+' que você tem',t='num',req=True,min=0,max=50),dict(k='jornada',l='Jornada',t='num',req=True,min=1,max=24,u='h/dia')]+fT+
                       [dict(k=perda['k'],l=perda['l'],t='num',req=True,min=perda['min'],max=perda['max'],u='%',help=perda['ajuda'])]),
           search=False,gid=gid,total=False)
    g_recp_maq=recp_grid('g_recp_maq',[r for r in D2.RECURSOS if r['id']!='oper'],'Unidades',
                         dict(k='disp',l='Disponibilidade',min=1,max=100,ajuda='Parte do tempo em que a máquina fica apta: desconta manutenção, quebras e espera por peças. A eficiência de campo já está no rendimento; não desconte de novo.'),
                         'A capacidade mensal é unidades × dias úteis × jornada × turnos × disponibilidade. Necessárias = horas da demanda ÷ horas de uma unidade no mês, arredondado para cima.',True)
    g_recp_pes=recp_grid('g_recp_pes',[r for r in D2.RECURSOS if r['id']=='oper'],'Pessoas',
                         dict(k='abs',l='Absenteísmo',min=0,max=90,ajuda='Horas perdidas com faltas, atestados, afastamentos e férias.'),
                         'A capacidade mensal é pessoas × dias úteis × jornada × (1 − absenteísmo). Necessárias = horas da demanda ÷ horas de uma pessoa no mês, arredondado para cima. Dois turnos pedem mais pessoas, não mais horas por pessoa.',False)
    RCOLS=[dict(k='ind',l='Recurso · indicador',w=190)]+[dict(k=f'm{i}',l=lab,t='num',a='r') for i,(_,lab) in enumerate(meses)]+[dict(k='tot',l='Total',t='num',a='r')]
    g_res=grid(RCOLS,[],edit=dict(m='pick',leafOnly=False),tree=True,search=False,gid='g_res',total=False,headtools=False,x0={f'R_{r["id"]}':True for r in D2.RECURSOS})
    g_resd=grid([dict(k='ind',l='Atividade',w=240)]+[dict(k=f'm{i}',l=lab,t='num',a='r',d=1) for i,(_,lab) in enumerate(meses)]+[dict(k='tot',l='Total (h)',t='num',a='r',d=1)],
                [],edit=dict(m='none'),search=False,gid='g_resd',total=False,headtools=False)
    # ---------- etapa 6 · demanda ----------
    # TABELAS-FOCO (5983172395): uma variável por coluna; a unidade varia por insumo e tem coluna própria; a árvore grupo → insumo continua
    # "1º uso" logo depois do insumo (v3.8); depois o essencial da compra (necessidade, unidade, falta, valor, situação)
    g_dem=grid([dict(k='grp',l='Grupo',w=130),dict(k='ins',l='Insumo',w=200),dict(k='uso',l='1º uso',t='num'),dict(k='liq',l='Necessidade líquida',t='num',a='r',w=128),dict(k='un',l='Unidade',w=80),dict(k='falta',l='Falta em',t='num',w=110),
                dict(k='valor',l='Valor (R$)',t='num',a='r',d=2,agg='sum'),dict(k='sit',l='Situação'),dict(k='sol',l='Solicitação',w=120),
                dict(k='bruta',l='Demanda bruta',t='num',a='r'),dict(k='real',l='Já realizado',t='num',a='r'),dict(k='est',l='Estoque apto',t='num',a='r',w=118),dict(k='antes',l='Usado antes da compra',t='num',a='r',w=130),
                dict(k='res',l='Reservado',t='num',a='r'),dict(k='rec',l='Recebimentos previstos',t='num',a='r',w=112),dict(k='tarde',l='Recebido após a falta',t='num',a='r',w=130),
                dict(k='cob',l='Coberta em',t='num',w=110),dict(k='preco',l='Preço (R$/un)',t='num',a='r',d=2)],
       [],edit=dict(m='origin',leafOnly=True,title='Insumo',fields=[dict(k='ins',l='Insumo',t='txt',ro=True),dict(k='un',l='Unidade',t='txt',ro=True)]),tree=True,gid='g_dem',total=True,qf=dict(k='sit',cut=' · ',l='situação'))
    # ---------- JS do processo ----------
    sol0={'S2627':dict(id='SOL-2026-07',at='23/09/2026',itens={n:round(o['liq'],3) for n,o in D2.demanda('S2627').items() if o['liq']>0.001},comp=0)}
    d2=dict(D2.js_data()); d2['sol']=sol0; d2['talhoes']=TALH; d2['talfaz']=TALFAZ; d2['conj_opts']=conj_opts; d2['hoje']=D2.HOJE_ISO; d2['viavel']=D2.VIAVEL
    EXTRAJS[0]='const D2 = '+json.dumps(d2,ensure_ascii=False)+';\n'+open(os.path.join(ROOT,'cal01.js')).read()+'\n'+open(os.path.join(ROOT,'safra.js')).read()+'''
function _safhooks(self){ self.g2after=(gid,rows,r,isNew)=>{ if(gid==='g_saf' && r && String(r.id).indexOf('n')===0 && !self.state.saf){ if(!r.v.estado) r.v.estado='Rascunho'; self.setState({saf:r.id,step:2,g2toast:'Safra criada: '+r.v.nome+'. Defina os cultivos.'}); }
    if(String(gid).indexOf('g_cult_')===0) cultAfter(self,gid,rows,r,isNew);
    if(String(gid).indexOf('g_rend_')===0&&r) rendAfter(self,gid,rows,r,isNew); };
  self.g2live=(gid,k,d)=>(String(gid).indexOf('g_rend_')===0?rendLive(k,d):null);
  self.g2opts=(gid,k,d,rid)=>(String(gid).indexOf('g_cult_')===0&&k==='plano'?planOpts(d):(String(gid).indexOf('g_rend_')===0&&k==='conj_id'?conjOpts(rid||d.base):null));
  self.g2formActs=(gid,r,fm)=>(String(gid).indexOf('g_cult_')===0?cultActs(self,gid,r):(String(gid).indexOf('g_rend_')===0?rendActs(self,gid,r):null));
  self.g2check=(gid,rows,r,d,isNew)=>(String(gid).indexOf('g_cult_')===0?cultCheck(self,gid,rows,r,d,isNew):(String(gid).indexOf('g_rend_')===0?(self._conjAntes=(r?String(r.v.conj_id||''):null),rendCheck(self,rows,r,d,isNew)):(gid==='g_saf'?safCheck(d):null)));
  self.g2pick=(gid,rid,r)=>{ if(gid==='g_op'){ const pid=String(rid).split('_')[0]; self.setState({atv:pid,opv:'mes'}); } if(gid==='g_res'){ const k=String(rid).replace('R_','').replace(/_(d|c|n|u)$/,''); self.setState({rec:(self.state.rec===k?null:k)}); } }; }
const _EV=EXTRAVALS; EXTRAVALS=function(self,v){ _safhooks(self); _EV(self,v); v.ap_bulk=()=>openApply(self,null); };
const _EVR=EXTRAVALS; EXTRAVALS=function(self,v){ _EVR(self,v); v.rendnova=(rid)=>rendNova(self,rid); };   // + Outra configuração (etapa 3)'''
    # ---------- corpo ----------
    # UX-ACAO-UNICA-20261003: o cabeçalho do bloco só tem comandos do próprio conteúdo (criar, adicionar, modo de visão); avanço,
    # retorno e a primária da etapa ficam na área de ações única ao fim do conteúdo (engine.area_acoes, preenchida em safra.js)
    acoes=lambda extra='': f'<span style="display: inline-flex; align-items: center; gap: 8px; flex-wrap: wrap; justify-content: flex-end;">{extra}</span>'
    nova_safra=f'<button type="button" onClick="{H("g_saf_new")}" style="{E.BTN_ST(False,True)}">Nova safra</button>'   # criar é secundário: a tarefa da etapa é escolher
    # Adicionar cultivo: uma instância, junto da lista; secundário, e primário só na lista vazia (aí é a única ação da etapa)
    add_cult=(f'<sc-if value="{H("add_sec")}" hint-placeholder-val="{F()}"><button type="button" data-acao="adicionar" onClick="{H("add_fn")}" style="{E.BTN_ST(False,True)}">Adicionar cultivo</button></sc-if>'
              f'<sc-if value="{H("add_prim")}" hint-placeholder-val="{F()}"><button type="button" data-acao="adicionar" onClick="{H("add_fn")}" style="{E.BTN_ST(True,True)}">Adicionar cultivo</button></sc-if>')
    s1=bloco('Escolha a safra','Clique na safra para continuar de onde parou.',g_saf,acao=nova_safra)
    s2=bloco('Cultivos e planos',H('k2'),cult_html,acao=acoes(add_cult),desc_hole=True)
    s3=bloco('Rendimentos por operação e atividade','Clique numa atividade para ajustar conjunto e rendimento; no formulário, “+ Outra configuração” divide a área dela entre conjuntos diferentes.',rend_html,acao=acoes())   # texto da REND (rendNova)
    # uma visão por vez, no mesmo lugar: por operação (operação → atividade → cultivo) ou por mês (indicadores × meses)
    seg=(f'<div role="group" aria-label="Modo de visão" style="display: inline-flex; flex-shrink: 0; padding: 3px; gap: 2px; border-radius: 999px; background: {BG}; border: 1px solid {LINE};">'
         f'<button type="button" aria-pressed="{H("vis_op")}" onClick="{H("ver_op")}" style="{H("vis_op_st")}">Por operação</button>'
         f'<button type="button" aria-pressed="{H("vis_mes")}" onClick="{H("ver_mes")}" style="{H("vis_mes_st")}">Por mês</button></div>')
    filtro=(f'<sc-if value="{H("mat_sel")}" hint-placeholder-val="{F()}"><div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 0 4px 8px; font-size: 12.8px;">'
            f'<span style="color: {MUTED};">Mostrando só</span><b>{H("mat_nome")}</b><button type="button" onClick="{H("mat_todas")}" style="{_MINI}">Ver todas as operações</button></div></sc-if>')
    s4=bloco(H('op_titulo'),H('k4'),
                f'<sc-if value="{H("vis_op")}" hint-placeholder-val="{H("true")}">{g_op}</sc-if><sc-if value="{H("vis_mes")}" hint-placeholder-val="{F()}">{filtro}{g_mat}</sc-if>',
                acao=acoes(seg),tit_hole=True,desc_hole=True)
    dias=' · '.join(f'{lab} {D2.DIAS_UTEIS[k]}' for k,lab in meses)
    # uma visão por vez: classe (máquinas e implementos | pessoas) × modo (parâmetros | por mês)
    def seg2(aria,a_on,a_go,a_st,a_t,b_on,b_go,b_st,b_t):
        return (f'<div role="group" aria-label="{aria}" style="display: inline-flex; flex-shrink: 0; padding: 3px; gap: 2px; border-radius: 999px; background: {BG}; border: 1px solid {LINE};">'
                f'<button type="button" aria-pressed="{H(a_on)}" onClick="{H(a_go)}" style="{H(a_st)}">{a_t}</button>'
                f'<button type="button" aria-pressed="{H(b_on)}" onClick="{H(b_go)}" style="{H(b_st)}">{b_t}</button></div>')
    rec_ctl=(f'<div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end;">'
             + seg2('Classe de recurso','cl_maq','ver_maq','cl_maq_st','Máquinas e implementos','cl_pes','ver_pes','cl_pes_st','Pessoas')
             + seg2('Modo de visão dos recursos','vis_par','ver_par','vis_par_st','Parâmetros','vis_rmes','ver_rmes','vis_rmes_st','Por mês') + '</div>')
    s5=(f'<div style="font-size: 13px;"><span style="{H("k5st")}">{H("k5")}</span></div>'
        + bloco(H('rec_titulo'),H('rec_sub'),
                f'<sc-if value="{H("vis_par")}" hint-placeholder-val="{H("true")}"><div style="font-size: 12px; color: {MUTED}; padding: 0 4px 8px;">Dias úteis por mês: {dias}</div>'
                f'<sc-if value="{H("cl_maq")}" hint-placeholder-val="{H("true")}">{g_recp_maq}</sc-if><sc-if value="{H("cl_pes")}" hint-placeholder-val="{F()}">{g_recp_pes}</sc-if></sc-if>'
                f'<sc-if value="{H("vis_rmes")}" hint-placeholder-val="{F()}">{g_res}'
                f'<sc-if value="{H("resd_sel")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 4px; padding: 14px 4px 6px;"><b style="font-size: 14px;">{H("resd_titulo")}</b>'
                f'<span style="font-size: 12.8px; color: {MUTED};">Atividades que consomem as horas deste recurso em cada mês.</span></div>{g_resd}</sc-if></sc-if>',
                acao=acoes(rec_ctl),tit_hole=True,desc_hole=True))
    s6=bloco('Demanda de insumos por grupo',H('k6'),g_dem,desc_hole=True,
                acao=f'<span style="display: inline-flex; align-items: center; gap: 8px;"><sc-if value="{H("sol_link")}" hint-placeholder-val="{F()}"><a href="{H("sol_href")}" style="{_MINI} text-decoration: none;">Abrir em Compra de insumos ›</a></sc-if></span>')
    corpo=''.join(f'<sc-if value="{H("s"+str(i))}" hint-placeholder-val="{H("true") if i==1 else F()}"><div style="display: flex; flex-direction: column; gap: 14px;">{s}</div></sc-if>'
                  for i,s in enumerate([s1,s2,s3,s4,s5,s6],1)) + E.area_acoes('aa','Ações da etapa')
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
    prod_row=(f'<div style="display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1.6fr) 88px 122px 82px 94px 150px; gap: 10px; align-items: center; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 12.5px;">'
              f'<span style="color: {MUTED};">{H("p.grupo")}</span><span style="font-weight: 600;">{H("p.nome")}<sc-if value="{H("p.aj")}" hint-placeholder-val="{F()}"> <span style="display: inline-block; padding: 1px 7px; border-radius: 999px; background: {YELS}; color: {YEL}; font-size: 11px; font-weight: 700;">dose deste talhão</span></sc-if>'
              f'<sc-if value="{H("p.rmv")}" hint-placeholder-val="{F()}"> <span style="display: inline-block; padding: 1px 7px; border-radius: 999px; background: {REDS}; color: {RED}; font-size: 11px; font-weight: 700;">retirado deste talhão</span></sc-if>'
              f'<sc-if value="{H("p.novo")}" hint-placeholder-val="{F()}"> <span style="display: inline-block; padding: 1px 7px; border-radius: 999px; background: {ACCS}; color: {ACC}; font-size: 11px; font-weight: 700;">incluído neste talhão</span></sc-if></span>'
              f'<span style="color: {MUTED}; white-space: nowrap; text-align: right;">{H("p.padrao")}</span>'
              f'<span style="display: flex; align-items: center; gap: 4px; white-space: nowrap;"><input id="{H("p.fid")}" aria-label="Dose local de {H("p.nome")}" value="{H("p.v")}" onChange="{H("p.set")}" readOnly="{H("p.dis")}" style="{H("p.ist")}"><span style="color: {MUTED}; font-size: 11.5px;">{H("p.un")}</span></span>'
              f'<span style="color: {MUTED}; white-space: nowrap; text-align: right;">{H("p.preco")}</span><span style="font-weight: 700; white-space: nowrap; text-align: right;">{H("p.custo")}</span>'
              f'<span style="display: flex; gap: 4px; justify-content: flex-end; flex-wrap: wrap;"><sc-if value="{H("p.podeRest")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("p.reset")}" title="Voltar à dose do plano padrão" style="{_MINI} font-size: 11px; padding: 3px 7px;">Restaurar dose</button></sc-if>'
              f'<sc-if value="{H("p.podeRet")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("p.ret")}" aria-label="Retirar {H("p.nome")} deste talhão" style="{_MINI} font-size: 11px; padding: 3px 7px; color: {RED};">Retirar</button></sc-if>'
              f'<sc-if value="{H("p.podeDesf")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("p.desf")}" aria-label="Desfazer a retirada de {H("p.nome")}" style="{_MINI} font-size: 11px; padding: 3px 7px;">Desfazer</button></sc-if></span></div>'
              f'<sc-if value="{H("p.hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 11.5px; color: {RED}; font-weight: 700;">{H("p.err")}</div></sc-if>')
    EXTRA.append(
      f'<sc-if value="{H("lp_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar" onClick="{H("lp_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="{H("lp_titulo")}" style="position: relative; width: 920px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
      f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1;">{H("lp_titulo")}</h2><button type="button" aria-label="Fechar" onClick="{H("lp_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED};">×</button></div>'
      f'<div style="font-size: 13px; color: {MUTED};">{H("lp_sub")}</div>'
      f'<sc-if value="{H("lp_nerr")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">Corrija os campos destacados; o que você digitou foi mantido.</div></sc-if>'
      f'<sc-for list="{H("lp_grupos")}" as="g" hint-placeholder-count="1"><div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase; padding-top: 4px;">{H("g.t")}</div>'
      f'<sc-for list="{H("g.gats")}" as="t" hint-placeholder-count="2"><div style="border: 1px solid {LINE}; border-radius: 12px; overflow: hidden;">'
      f'<div style="display: flex; align-items: center; gap: 8px; padding: 8px 10px; background: {BG};"><button type="button" class="g2car" aria-label="{H("t.lab")}" onClick="{H("t.tog")}">{H("t.sym")}</button><b style="font-size: 13.5px;">{H("t.t")}</b><span style="font-size: 12px; color: {MUTED};">· {H("t.dt")}</span></div>'
      f'<sc-if value="{H("t.open")}" hint-placeholder-val="{H("true")}"><div style="padding: 4px 12px 10px;"><sc-for list="{H("t.atvs")}" as="a" hint-placeholder-count="1"><div style="padding: 6px 0;">'
      f'<div style="display: flex; align-items: center; gap: 8px;"><button type="button" class="g2car" aria-label="{H("a.lab")}" onClick="{H("a.tog")}">{H("a.sym")}</button><span style="font-size: 13px; font-weight: 700;">{H("a.t")}</span><span style="font-size: 12px; color: {MUTED};">· {H("a.op")}</span></div>'
      f'<sc-if value="{H("a.open")}" hint-placeholder-val="{H("true")}"><div style="padding-left: 30px;"><sc-if value="{H("a.semProd")}" hint-placeholder-val="{F()}"><div style="font-size: 12px; color: {MUTED}; padding: 4px 0;">Sem insumos · só operação</div></sc-if>'
      f'<sc-for list="{H("a.prods")}" as="p" hint-placeholder-count="1">{prod_row}</sc-for>'
      f'<sc-if value="{H("a.podeIncl")}" hint-placeholder-val="{F()}"><div style="padding-top: 6px;"><button type="button" onClick="{H("a.incl")}" style="{_MINI} font-size: 12px;">+ Incluir insumo nesta atividade</button></div></sc-if>'
      f'<sc-if value="{H("a.pkOpen")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px; padding: 8px 10px; margin-top: 6px; border-radius: 10px; background: {BG};">'
      f'<label for="{H("a.acId")}" style="font-size: 12px; font-weight: 700; color: {MUTED};">Insumo a incluir</label>'
      + E.ac_campo('a.','Insumo a incluir','300px') +
      f'<button type="button" onClick="{H("a.pkOk")}" style="{_MINIP}">Incluir</button><button type="button" onClick="{H("a.pkNo")}" style="{_MINI}">Cancelar</button>'
      f'<sc-if value="{H("a.pkHasErr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("a.pkErr")}</span></sc-if>'
      f'<span style="flex-basis: 100%; font-size: 11.5px; color: {MUTED};">Depois de incluir, informe a dose por hectare na nova linha.</span></div></sc-if>'
      f'</div></sc-if></div></sc-for></div></sc-if></div></sc-for></sc-for>'
      f'<div style="flex-grow: 1;"></div>'
      f'<sc-if value="{H("lp_warn")}" hint-placeholder-val="{F()}"><div role="alert" class="saida" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("lp_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H("lp_keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
      f'<div class="pe-form" style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};"><sc-if value="{H("lp_edit")}" hint-placeholder-val="{H("true")}"><button type="button" onClick="{H("lp_close")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" onClick="{H("lp_save")}" style="{BTN_ST(True,True)}">Salvar</button></sc-if>'
      f'<sc-if value="{H("lp_ro")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("lp_discard")}" style="{BTN_ST(False,True)}">Fechar</button></sc-if></div></aside></div></sc-if>')
    # ---------- painel: dividir o talhão em parcelas (sem limite de quantidade) ----------
    DV_COLS='92px 86px 124px minmax(110px,1fr) 138px 70px 90px minmax(140px,1.2fr) 32px'
    lab_row=''.join(f'<span>{x}</span>' for x in ['Parcela','Área (ha)','Cultura','Variedade','Plantio','Meta','Unidade','Plano agronômico',''])
    dv_row=(f'<div style="display: grid; grid-template-columns: {DV_COLS}; gap: 8px; align-items: center; padding: 7px 0; border-top: 1px solid {LINE};">'
            f'<input aria-label="Nome da parcela {H("r.lab")}" value="{H("r.local")}" onChange="{H("r.s_local")}" readOnly="{H("r.dis")}" style="{H("r.st_local")}">'
            f'<input aria-label="Área de {H("r.lab")} em hectares" inputMode="decimal" value="{H("r.area")}" onChange="{H("r.s_area")}" readOnly="{H("r.dis")}" style="{H("r.st_area")}">'
            f'<select aria-label="Cultura de {H("r.lab")}" value="{H("r.cult")}" onChange="{H("r.s_cult")}" disabled="{H("r.dis")}" style="{H("r.st_cult")}"><sc-for list="{H("r.oc")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>'
            f'<input aria-label="Variedade de {H("r.lab")}" value="{H("r.var")}" onChange="{H("r.s_var")}" readOnly="{H("r.dis")}" style="{H("r.st_var")}">'
            f'<input type="date" aria-label="Plantio de {H("r.lab")}" value="{H("r.plantio")}" onChange="{H("r.s_plantio")}" readOnly="{H("r.dis")}" style="{H("r.st_plantio")}">'
            f'<input aria-label="Meta de {H("r.lab")}" inputMode="decimal" value="{H("r.meta")}" onChange="{H("r.s_meta")}" readOnly="{H("r.dis")}" style="{H("r.st_meta")}">'
            f'<select aria-label="Unidade da meta de {H("r.lab")}" value="{H("r.unm")}" onChange="{H("r.s_unm")}" disabled="{H("r.dis")}" style="{H("r.st_unm")}"><sc-for list="{H("r.ou")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>'
            f'<span style="display: flex; flex-direction: column; gap: 3px; min-width: 0;"><select aria-label="Plano agronômico de {H("r.lab")}" value="{H("r.planoId")}" onChange="{H("r.s_plano")}" disabled="{H("r.dis")}" style="{H("r.st_plano")}"><sc-for list="{H("r.op")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>'
            f'<sc-if value="{H("r.temNota")}" hint-placeholder-val="{F()}"><span style="{H("r.pst")}">{H("r.plano")}</span></sc-if></span>'
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
      f'<sc-if value="{H("dv_warn")}" hint-placeholder-val="{F()}"><div role="alert" class="saida" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("dv_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H("dv_keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
      f'<div class="pe-form" style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};"><sc-if value="{H("dv_edit")}" hint-placeholder-val="{H("true")}"><button type="button" onClick="{H("dv_close")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" onClick="{H("dv_save")}" style="{BTN_ST(True,True)}">Salvar divisão</button></sc-if>'
      f'<sc-if value="{H("dv_ro")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("dv_discard")}" style="{BTN_ST(False,True)}">Fechar</button></sc-if></div></aside></div></sc-if>')
    HEIGHTS37[fname]=1500
    shell37('SAF','Planejar safra',corpo,fname=fname,subtitle='',
            steps=steps_state(NOMES),primary_html=None,  # faixa só informa; avanço/retorno/primária na área de ações (UX-ACAO-UNICA-20261003)
            ctx=(H('ctx_faz'),H('ctx_saf'),None),search=False)
