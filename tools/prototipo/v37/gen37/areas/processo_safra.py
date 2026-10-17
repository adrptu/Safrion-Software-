# -*- coding: utf-8 -*-
"""Agrícola › Planejar safra — processo em 4 etapas numa só tela de trabalho (SAF.dc.html): safra, talhões e cultivos, operações e
recursos (etapa única que juntou as antigas 3, 4 e 5, pedido do proprietário de 05/10/2026) e demanda de insumos."""
import json, os
from engine import (grid,section,esc,icon,chip,btn,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,SH,DISP,BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, steps_state, HEIGHTS37
import ui37 as UI
import dados2 as D2
import dados as D
import ocupacao_cen as OCEN
import cenario
import unidprod_ui as UNP
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
NOMES=['Escolha a safra','Defina cultivos e planos','Dimensione operações e recursos','Confira a demanda de insumos']
def bloco(titulo,desc,corpo,acao='',tit_hole=False,desc_hole=False):
    if not desc_hole: desc=''   # 13/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos títulos ... somos minimalistas e essencialistas")
    t=titulo if tit_hole else esc(titulo); desc=desc if desc_hole else esc(desc)
    acao=E.recolhe_acoes(titulo,acao)   # MAIS-01 (15/10/2026): uma secundária à vista, as outras no "⋯ Mais ações" do bloco
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
       edit=dict(m='form',title='Safra',newTitle='Nova safra',sub='Altere nome, início, fim e fazendas. Cultivos e planos ficam nas etapas seguintes, por fazenda.',
                 fields=[dict(k='nome',l='Nome da safra',t='txt',req=True,def_='' ),dict(k='ini',l='Início',t='date',req=True),dict(k='fim',l='Fim',t='date',req=True,help='O fim precisa ser depois do início.'),
                         dict(k='fazs',l='Fazendas',t='multi',opts=OCEN.fazendas(),req=True,**{'def':'Santa Rita'})]),
       add=None,gid='g_saf',total=False,qf=dict(k='faz',l='fazenda',todas='Todas'))   # 14/10 (proprietário: "não dá para escolher ou mudar de fazenda"): chips por fazenda na escolha da safra
    # ---------- etapa 2 · talhões e cultivos (ESPECIFICACAO etapa-2-talhoes) ----------
    # todos os talhões Ativos do CD-01 da fazenda da safra (com o B1 da Boa Vista e os pivôs da Lagoa Grande); a ocupação no tempo sai do
    # serviço único ocupacao.js (ENG-011). Linhas de talhão e de outras safras são só de exibição (safra.js · syncTalhoes); o estado guarda
    # só os cultivos desta safra.
    TAL_FAZ=OCEN.talhoes()
    TALH={t:ha for lst in TAL_FAZ.values() for t,ha in lst}
    TALFAZ={t:f for f,lst in TAL_FAZ.items() for t,_ in lst}
    # TABELAS-FOCO (5983172395): uma variável por coluna; as cinco primeiras respondem onde, quanto e quando; Cultura, Ocupa até, Fim por e
    # Safra logo depois respondem o que ocupa e até quando (§3.1)
    # SAF-TAB (proprietário, 14/10: "muitas colunas, confuso… mais minimalistas"): abre com o que decide a etapa (ess = posição: talhão,
    # cultura, plano, área, plantio); as outras 11 ficam em "Colunas +11" (VISOES-2 §3.6). A Situação sai do padrão e vira ícone antes do
    # talhão só quando pede atenção (sico: Sobreposição, A conferir); Planejado, Livre e Perene não ganham ícone. No celular, as 3 primeiras.
    CULT_COLS=[dict(k='local',l='Talhão ou parcela',w=130,ess=1,pq='onde'),dict(k='sit',l='Situação',w=150,niv0=True,pq='situacao'),dict(k='livre',l='Área livre (ha)',t='num',a='r',d=2,dmin=0,niv0=True,pq='medida'),
               dict(k='desde',l='Livre a partir de',t='num',w=130,niv0=True,pq='quando'),dict(k='area',l='Área (ha)',t='num',a='r',agg='sum',d=2,dmin=0,ess=4,pq='medida'),dict(k='cult',l='Cultura',ess=2,pq='oque'),
               dict(k='ate',l='Ocupa até',t='num',pq='quando'),dict(k='fimpor',l='Fim por',w=150,pq='quando',ajuda='Pelo plano e Colheita informada são previsões. Estimado: ciclo da cultivar ou plano mais longo da cultura (CD-02), sem plano no cultivo. Observado: colheita registrada.'),
               dict(k='saf',l='Safra',w=150,pq='quando'),dict(k='var',l='Variedade',pq='oque'),dict(k='plano',l='Plano agronômico',w=190,ess=3,pq='oque'),dict(k='ver',l='Versão',pq='oque'),dict(k='dt_plantio',l='Plantio',t='num',ess=5,pq='quando'),
               dict(k='meta',l='Meta',t='num',a='r',pq='medida'),dict(k='aj',l='Ajustes locais',t='num',a='r',pq='medida'),dict(k='tipo',l='Tipo',w=120,pq='oque')]
    NUNCA_C=dict(k='modo',eq='__nunca'); PLAN=dict(k='modo',ne='vinc'); VINC=dict(k='modo',eq='vinc')
    # painel "Planejar T1" (§2): contexto herdado no subtítulo; Plano antes do Plantio; Plantio = PlantioMin; Colheita prevista editável só sem
    # plano; meta na unidade escolhida no seletor da tabela (UNID-PROD), Padrão = unidade de mercado da cultura (DEC-0510-03).
    # "Vincular ciclo C1" (R-24) mostra o ciclo travado e pede plano e meta.
    CULT_FIELDS=[dict(k='modo',l='',t='txt',cond=NUNCA_C),dict(k='talhao',l='',t='txt',cond=NUNCA_C),
                 dict(k='cult',l='Cultura',t='sel',dyn=True,opts=[],req=True,cond=PLAN),dict(k='cult',l='Cultura',ro=True,cond=VINC),
                 dict(k='var',l='Variedade',t='txt',req=True,cond=PLAN),dict(k='var',l='Variedade',ro=True,cond=VINC),
                 dict(k='plano',l='Plano agronômico',t='sel',dyn=True,opts=[],
                      help='Planos publicados da cultura escolhida. Trocar o plano descarta os ajustes de insumos deste cultivo.'),
                 dict(k='plantio',l='Plantio',t='date',req=True,cond=PLAN),dict(k='pmin_txt',l='Plantio a partir de',ro=True,live=True,cond=PLAN),
                 dict(k='plantio',l='Plantio real do ciclo',t='date',ro=True,cond=VINC),
                 dict(k='local',l='Parcela',t='txt',cond=PLAN,help='Sugerida pela faixa que libera nesse dia. Área igual à do talhão vira talhão inteiro.'),
                 dict(k='area',l='Área',t='num',req=True,min=0.01,max=5000,u='ha',cond=PLAN),dict(k='area',l='Área do ciclo',ro=True,u='ha',cond=VINC),
                 dict(k='colheita',l='Colheita prevista',t='date',cond=[dict(k='plano',eq=''),PLAN],help='Sem plano: a data que a fazenda prevê. Vazia, o sistema estima pelo ciclo da cultivar (CD-02).'),
                 dict(k='colh_txt',l='Colheita prevista',ro=True,live=True,cond=dict(k='plano',ne='')),
                 dict(k='meta',l='Meta de produtividade',t='num',req=True,min=0),dict(k='unm_txt',l='Unidade da meta',ro=True,live=True,help='A do seletor "Unidade de produtividade" da tabela ao abrir este painel; o Padrão da cultura vem do CD-02 (DEC-0510-03).'),
                 dict(k='ocup_txt',l='Ocupação prevista',ro=True,live=True,cond=PLAN)]
    def talhao_de(c):
        return c['local'] if c['tipo']!='Parcela' else c['local'].rsplit('-',1)[0]
    def cult_rows(k):
        out=[]; grp={}
        for c in D2.CULTIVOS.get(k,[]):
            t=talhao_de(c)
            r=dict(id=c['id'],ro=c['ro'],v=dict(talhao=t,faz=c['fazenda'],local=c['local'],tipo=c['tipo'],cult=c['cultura'],var=c['variedade'],area=c['area'],
                   plantio=c['plantio'],meta=c['meta'],unm=c['un_meta'],plano=c['plano'] or '',colheita=c['colheita'] or '',colheita_real=c.get('colheita_real') or '',
                   ciclo=c.get('ciclo') or '',origem=c.get('origem') or ''),s={},p={})
            if c['tipo']=='Parcela':
                if t not in grp:
                    grp[t]=dict(id='grp_'+t,grp=True,dr='div_'+t,ro=c['ro'],v=dict(talhao=t,faz=c['fazenda'],local=t),s={},p={},kids=[]); out.append(grp[t])
                grp[t]['kids'].append(r)
            else: out.append(r)
        return out
    # SAF-FAZ-3 (B): com várias fazendas, filtro rápido por fazenda logo depois da busca (segmentado, para não confundir com o da Situação)
    FFZ=(f'<sc-if value="{H("ffz_tem")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Fazenda" class="ffz">'
         f'<sc-for list="{H("ffz_l")}" as="fq" hint-placeholder-count="3"><button type="button" aria-pressed="{H("fq.on")}" title="{H("fq.al")}" onClick="{H("fq.go")}">{H("fq.t")}</button></sc-for></div></sc-if>')
    cult_html=''
    for k in ['S2627','S27SF','S2526','LG2627','NOVA']:
        rows=cult_rows(k)
        ro=(k=='S2526')
        # sem caixas de seleção (proprietário, 13/10/2026): o plano entra pela primária "Aplicar plano em N cultivos" (os sem plano) ou pelo
        # "Aplicar plano" / "Reaplicar" da linha; trocar o plano de um cultivo é pelo formulário da linha
        g=grid(CULT_COLS,rows,edit=dict(m='form',title='Cultivo',newTitle='Novo cultivo',sub='Altere o cultivo e o plano agronômico e salve.',fields=CULT_FIELDS),
               sel=False,dele=not ro,add=None,gid=f'g_cult_{k}',qf=dict(k='sit',l='situação',nivel0=True),total=True,tree=True,x0={},menu_linha=True,busca_extra=FFZ,
               sico=dict(k='sit',cores=['red','yellow']),
               tools=f'<sc-if value="{H("us_"+k+"_vis")}" hint-placeholder-val="{F()}">'+UNP.sel_html('us_'+k)+'</sc-if>')   # UNID-PROD: um seletor por tabela (D-U01), só com a Meta à vista (SAF-TAB)
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
               dict(k='custo_kg',l='Custo R$/kg',w=170),dict(k='modo',l='Modo',w=150),
               dict(k='larg',l='Largura (m)',t='num',a='r',d=2,dmin=0),dict(k='vel',l='Velocidade (km/h)',t='num',a='r',d=2,dmin=0),dict(k='efic',l='Eficiência (%)',t='num',a='r',d=1,dmin=0),
               dict(k='part',l='Parte da área (%)',t='num',a='r',d=1,dmin=0,w=150),dict(k='seq',l='Trabalha',w=130),
               dict(k='jan',l='Janela (h por talhão)',t='num',a='r',d=1,dmin=0),dict(k='planos',l='Planos',w=240)]
    NUNCA=dict(k='multi',eq='__nunca')   # campo só de rascunho: guarda contexto do formulário e não aparece
    MULTI=dict(k='multi',eq='sim'); UMA=dict(k='multi',eq='não')
    SEQ_T='Em sequência: divide trator, implemento ou operador'; PAR_T='Ao mesmo tempo, com recursos próprios'
    SO=dict(k='esc',eq='Só esta atividade'); NSO=dict(k='esc',ne='Só esta atividade'); COLH=dict(k='colh',eq='sim')
    REND_EDIT=dict(m='form',title='Rendimento',newTitle='Nova configuração',leafOnly=True,sub='Informe como o conjunto trabalha e quanto custa por hora; rendimento e custo por hectare são recalculados (na colheita, também por quilo). Vale só para esta safra.',
            fields=[dict(k='multi',l='',t='txt',cond=NUNCA),dict(k='base',l='',t='txt',cond=NUNCA),dict(k='colh',l='',t='txt',cond=NUNCA),dict(k='ctx',l='',t='txt',cond=NUNCA),
                    dict(k='opatv',l='Operação · atividade',t='txt',ro=True),
                    dict(k='esc',l='Aplicar em',t='sel',opts=['Todas as atividades da operação','Só esta atividade'],cond=UMA,help='Todas: conjunto, rendimento, custos e diesel vão para as outras atividades desta operação em uso nesta safra. As divididas entre conjuntos e as de planos ainda não aplicados ficam como estão. A janela é de cada atividade.'),
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
                    dict(k='custo_ha_c',l='Custo R$/ha',ro=True,live=True,help='Custo por hora ÷ rendimento (a mesma conta da tabela).'),
                    dict(k='custo_kg_c',l='Custo R$/kg',ro=True,live=True,cond=COLH,help='Por cultura, com a meta de produtividade dos cultivos desta safra; sem média entre culturas.'),
                    dict(k='origem_c',l='Origem',ro=True,live=True,help='"Padrão do cadastro (CD-02)" quando a configuração é igual ao conjunto padrão da operação; senão, "Ajustado nesta safra".'),
                    dict(k='diesel',l='Consumo de diesel',t='num',min=0,max=200,u='L/h',help='Opcional. Estima os litros pelas horas do conjunto; o custo do combustível já está no custo da máquina.'),
                    dict(k='jan',l='Horas disponíveis na janela',t='num',min=0,max=2000,u='h por talhão',cond=MULTI,help='Opcional. Prazo, contado do início da ocorrência, para este conjunto terminar em cada talhão ou parcela; em sequência, cada configuração termina dentro da própria janela, e a janela maior de outra não amplia a dela. A área que não couber fica sem conjunto, à vista na Situação.'),
                    dict(k='jan',l='Horas disponíveis na janela',t='num',min=0,max=2000,u='h por talhão',cond=[UMA,SO],help='Opcional. Prazo, contado do início da ocorrência, para o conjunto terminar em cada talhão ou parcela desta atividade. A área que não couber fica sem conjunto, à vista na Situação.'),
                    dict(k='jan_op',l='Janela por talhão',ro=True,live=True,cond=[UMA,NSO]),
                    dict(k='part',l='Parte da área',t='num',min=0,max=100,u='%',cond=MULTI,help='Vazio = divide pelo rendimento, partindo das mesmas horas para as sem %; a que para na própria janela ou na da sequência passa o resto às outras. Estimativa: não garante término no mesmo horário nem a capacidade máxima. Com %, a parte fixa.'),
                    dict(k='seq',l='Trabalha com as outras configurações',t='sel',opts=[PAR_T,SEQ_T],cond=MULTI,**{'def':PAR_T},help='Mesmo trator do cadastro obriga a sequência; falta de máquina ou pessoa na fazenda faz a estimativa considerar as configurações em sequência.'),
                    dict(k='troca',l='Troca entre configurações',t='num',min=0,max=24,u='h',cond=MULTI,help='Opcional. Tempo para trocar para esta configuração quando trabalham em sequência; entra no tempo decorrido e ocupa a janela. O decorrido estimado começa pela de menor troca; para cumprir os prazos, a de janela menor pode precisar ir antes.'),
                    dict(k='neste_c',l='Neste talhão',ro=True,live=True,t='area',cond=dict(k='ctx',eq='talhao')),
                    dict(k='nesta_c',l='Nesta configuração',ro=True,live=True,cond=dict(k='ctx',eq='cfg'))])
    # uma g_rend por safra: é a fonte das configurações e o formulário Rendimento (EXTRA); a tabela sai do corpo (largura e velocidade só
    # no formulário, padrão adotado da PEND-SAF-01) e a g_op abre a folha certa (safra.js · abrirRend)
    for k in ['S2627','S27SF','S2526','LG2627','NOVA']:
        rrows=rend_rows(k)
        x0={r['id']:True for r in rrows}; x0.update({a['id']:True for r in rrows for a in r['kids'] if a.get('grp')})
        grid(REND_COLS,rrows,edit=(dict(REND_EDIT,m='ro') if k=='S2526' else REND_EDIT),gid=f'g_rend_{k}',total=False,tree=True,x0=x0)
    # ---------- etapa 3 · Dimensione operações e recursos (ESPECIFICACAO etapa-unica-3-4-5 §2-§3) ----------
    # g_op: 9 colunas, uma variável por coluna e a unidade na célula (ha-op na operação, ha nos demais níveis); a árvore é a lista e o
    # formulário Rendimento é o sub-detalhe. Situação: Com pendência · Janela não informada · Cabe na janela (só chips, sem números).
    # Total (proprietário, 13/10/2026): ha-op, horas, R$/ha e custo; o R$/ha e as unidades vêm do e3Op (safra.js), não da soma da grade.
    g_op=grid([dict(k='nome',l='Operação › atividade › talhão',w=172),dict(k='sit',l='Situação',w=164),dict(k='data',l='Data',t='num',w=104),dict(k='conj',l='Conjunto',w=150),
               dict(k='rend',l='Rendimento',t='num',a='r'),dict(k='area',l='Área trabalhada',t='num',a='r',agg='sum',ajuda='ha-op = hectares-operação: cada passada conta; 3 passadas em 10 ha = 30 ha-op (PRD 44.1)'),
               dict(k='horas',l='Horas-conjunto (h)',t='num',a='r',d=1,agg='sum'),
               dict(k='rha',l='Custo R$/ha',t='num',a='r',agg='fn',ajuda='Na linha: custo ÷ área trabalhada. No Total: custo ÷ hectares dos talhões (cada talhão conta uma vez, como no Resumo da safra)'),
               dict(k='custo',l='Custo total',t='num',a='r',agg='sum',ajuda='Máquinas e pessoas, sem insumos. O Total é o Custo de operação do topo')],
       [],edit=dict(m='pick',leafOnly=False),tree=True,gid='g_op',total=True,qf=dict(k='sit',l='situação',nivel0=True),sico_so_icone=True)
    # g_cap: capacidade por mês (recurso × mês, ocupação), uma por safra; recolhida por padrão.
    # Recurso, Maior uso e Mês abrem o formulário do recurso; as células de mês (nr) só filtram (toque na célula com demanda desta safra)
    def cap_cols(mis):
        return ([dict(k='rec',l='Recurso',w=170),dict(k='maior',l='Maior uso',t='num',a='r'),dict(k='mes',l='Mês',t='num')]+
                [dict(k=f'm{i}',l=meses[i][1],t='num',a='r',nr=True) for i in mis])
    # toda g_cap nasce com o calendário inteiro e a capMeses (safra.js) recorta em tempo de execução pelo período gravado: editar o período
    # pela tela acrescenta ou tira meses (verificação SAF-C02; antes, as safras fixas ficavam com as colunas do período do build)
    cap_html=''
    for k in ['S2627','S27SF','S2526','LG2627','NOVA']:
        g=grid(cap_cols(list(range(len(meses)))),[],edit=dict(m='pick',leafOnly=False),search=False,gid=f'g_cap_{k}',total=False,headtools=False)
        cap_html+=f'<sc-if value="{H("cap_"+k)}" hint-placeholder-val="{F()}">{g}</sc-if>'
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
                       [dict(k=perda['k'],l=perda['l'],t='num',req=True,min=perda['min'],max=perda['max'],u='%',help=perda['ajuda']),
                        dict(k='h1_c',l='Horas de uma unidade no mês de maior uso',ro=True,live=True),dict(k='hs_c',l='Horas na safra no calendário',ro=True,live=True),
                        dict(k='prev_c',l='Prévia',ro=True,live=True,t='area',help='Prévia desta safra, somando as safras abertas desta fazenda. Ao salvar, todas as safras são recalculadas.')]),
           search=False,gid=gid,total=False)
    g_recp_maq=recp_grid('g_recp_maq',[r for r in D2.RECURSOS if r['id']!='oper'],'Unidades',
                         dict(k='disp',l='Disponibilidade',min=1,max=100,ajuda='Parte do tempo em que a máquina fica apta: desconta manutenção, quebras e espera por peças. A eficiência de campo já está no rendimento; não desconte de novo.'),
                         'A capacidade mensal é unidades × dias úteis × jornada × turnos × disponibilidade. Necessárias = horas da demanda ÷ horas de uma unidade no mês, arredondado para cima.',True)
    g_recp_pes=recp_grid('g_recp_pes',[r for r in D2.RECURSOS if r['id']=='oper'],'Pessoas',
                         dict(k='abs',l='Absenteísmo',min=0,max=90,ajuda='Horas perdidas com faltas, atestados, afastamentos e férias.'),
                         'A capacidade mensal é pessoas × dias úteis × jornada × (1 − absenteísmo). Necessárias = horas da demanda ÷ horas de uma pessoa no mês, arredondado para cima. Dois turnos pedem mais pessoas, não mais horas por pessoa.',False)
    # ---------- etapa 4 · demanda de insumos ----------
    # TABELAS-FOCO (5983172395): uma variável por coluna; a árvore grupo → insumo continua. A unidade (kg, L) fica junto da quantidade
    # (decisão do proprietário, 05/10/2026: mais intuitivo e filtrar unidade não gera valor). "1º uso" logo depois do insumo (v3.8)
    g_dem=grid([dict(k='grp',l='Grupo',w=130),dict(k='ins',l='Insumo',w=200),dict(k='uso',l='1º uso',t='num'),dict(k='liq',l='Necessidade líquida',t='num',a='r',w=128),dict(k='falta',l='Falta em',t='num',w=110),
                dict(k='valor',l='Valor (R$)',t='num',a='r',d=2,agg='sum'),dict(k='sit',l='Situação'),dict(k='sol',l='Solicitação',w=120),dict(k='comp',l='A complementar',t='num',a='r',w=120),
                dict(k='bruta',l='Demanda bruta',t='num',a='r'),dict(k='real',l='Antes de hoje sem O.S.',t='num',a='r',w=130,ajuda='Uso do plano com data antes de hoje que nenhuma O.S. cobre: fica fora da demanda (histórico do plano). Se ainda vai acontecer, emita a O.S.'),dict(k='est',l='Estoque apto',t='num',a='r',w=118),dict(k='antes',l='Usado antes da compra',t='num',a='r',w=130),
                dict(k='res',l='Reservado',t='num',a='r'),dict(k='rec',l='Recebimentos previstos',t='num',a='r',w=112),dict(k='tarde',l='Recebido após a falta',t='num',a='r',w=130),
                dict(k='cob',l='Coberta em',t='num',w=110),dict(k='preco',l='Preço',t='num',a='r',w=120)],   # preço com a unidade do insumo junto: "R$ 3,90/kg"
       [],edit=dict(m='origin',leafOnly=True,title='Insumo',fields=[dict(k='ins',l='Insumo',t='txt',ro=True),dict(k='un',l='Unidade',t='txt',ro=True)]),tree=True,gid='g_dem',total=True,qf=dict(k='sit',cut=' · ',l='situação'))
    # ---------- JS do processo ----------
    sol0={'S2627':dict(id='SOL-2026-07',at='23/09/2026',em=D2.SOL_INICIAL['enviada'],por=D2.SOL_INICIAL['por'],   # envio original (a atualização grava atu e hist, revisão do CTL-4)
                       itens={n:round(o['liq'],3) for n,o in D2.demanda('S2627').items() if o['liq']>0.001},comp=0)}
    d2=dict(D2.js_data()); d2['sol']=sol0; d2['talhoes']=TALH; d2['talfaz']=TALFAZ; d2['talOrd']=TAL_FAZ; d2['culturas']=OCEN.CULTURAS; d2['unMeta']=OCEN.UN_META; d2['cultivares']=OCEN.cultivares(); d2['folga']=OCEN.FOLGA; d2['conj_opts']=conj_opts; d2['hoje']=D2.HOJE_ISO; d2['viavel']=D2.VIAVEL
    import cenario, dados_solo as DSO
    from areas.analise_solo import SOLO_UI_JS, porque_html
    # análise de solo (SOLO-01): o estado compartilhado (cenario.js + solo.js) e os laudos (SOLO0) entram no Planejar safra; 0 colisões de nome (solo_unit_test)
    # CTL-4: o mesmo cenário compartilhado (O.S., requisições, lotes) entra na demanda (cenDemEntradas/cenOsDem): emitir, liberar, apontar, cancelar ou devolver muda a conta
    # UNID-PROD (D-U14): o conversor único (producao.js) com o prefixo do estado, o mesmo das telas do estado; a tela não chama cenGet nem cenSave
    EXTRA.append('<style>'+UNP.CSS+'</style>')
    EXTRAJS[0]=cenario.js_prefixo()+DSO.js_prefixo()+SOLO_UI_JS+UNP.JS+'\nconst D2 = '+json.dumps(d2,ensure_ascii=False)+';\n'+open(os.path.join(ROOT,'cal01.js')).read()+'\n'+open(os.path.join(ROOT,'ocupacao.js')).read()+'\n'+open(os.path.join(ROOT,'safra_grupo.js')).read()+'\n'+open(os.path.join(ROOT,'safra.js')).read()+'\n'+open(os.path.join(ROOT,'safra_lote.js')).read()+'''
function _safhooks(self){ self.g2after=(gid,rows,r,isNew)=>{ if(gid==='g_saf' && r){ const msg=sgAplicar(self,rows,r,isNew);   /* SAF-FAZ-2: uma sub-safra por fazenda */
      if(isNew && !self.state.saf){ if(!r.v.estado) r.v.estado='Rascunho'; self.setState({saf:r.id,step:2,g2toast:msg||('Safra criada: '+r.v.nome+'. Planeje os talhões livres na tabela.')}); } else if(msg) self.setState({g2toast:msg}); }
    if(String(gid).indexOf('g_cult_')===0) cultAfter(self,gid,rows,r,isNew);
    if(String(gid).indexOf('g_rend_')===0&&r) rendAfter(self,gid,rows,r,isNew);
    if(String(gid).indexOf('g_recp_')===0&&r) recAfter(self,gid,rows,r); };
  self.g2live=(gid,k,d)=>(String(gid).indexOf('g_rend_')===0?rendLive(k,d,self):(String(gid).indexOf('g_cult_')===0?cultLive(self,gid,k,d):(String(gid).indexOf('g_recp_')===0?recLive(self,gid,k,d):null)));
  self.g2draft=(gid,k,d,fm)=>(String(gid).indexOf('g_cult_')===0?cultDraft(self,gid,k,d,fm):null);
  self.g2openDraft=(gid,r,d)=>safOpenDraft(self,gid,r,d); self.g2newDraft=(gid)=>safNovaDraft(self,gid);
  self.g2formSub=(gid,r,fm)=>(String(gid).indexOf('g_cult_')===0?cultSub(self,gid,r,fm):(String(gid).indexOf('g_recp_')===0?recSub(self):null));
  self.g2opts=(gid,k,d,rid)=>(String(gid).indexOf('g_cult_')===0&&k==='plano'?planOpts(d):(String(gid).indexOf('g_cult_')===0&&k==='cult'?cultOpts(d):(String(gid).indexOf('g_rend_')===0&&k==='conj_id'?conjOpts(rid||d.base):null)));
  self.g2formActs=(gid,r,fm)=>(String(gid).indexOf('g_cult_')===0?cultActs(self,gid,r):(String(gid).indexOf('g_rend_')===0?rendActs(self,gid,r):null));
  self.g2check=(gid,rows,r,d,isNew)=>(String(gid).indexOf('g_cult_')===0?cultCheck(self,gid,rows,r,d,isNew):(String(gid).indexOf('g_rend_')===0?(self._conjAntes=(r?String(r.v.conj_id||''):null),opAntes(self,r),rendCheck(self,rows,r,d,isNew)):(String(gid).indexOf('g_recp_')===0?(opAntes(self,r),null):(gid==='g_saf'?Object.assign({},sgChecar(self,rows,r,d,isNew),safCheck(d)):null))));
  self.g2pick=(gid,rid,r)=>{ if(gid==='g_op') abrirRend(self,rid); if(String(gid).indexOf('g_cap_')===0) abrirRec(self,rid); }; }
const _EV=EXTRAVALS; EXTRAVALS=function(self,v){ _safhooks(self); cenOuvir(self); _EV(self,v); };
const _EVR=EXTRAVALS; EXTRAVALS=function(self,v){ _EVR(self,v); v.rendnova=(rid)=>rendNova(self,rid); resumoVals(self,v); safUnidVals(self,v); };   // + Outra configuração e Resumo da safra (etapa 3)'''
    import plano_referencia as PR
    EXTRAJS[0] += PR.js()
    EXTRA.append(PR.painel())
    # ---------- corpo ----------
    # UX-ACAO-UNICA-20261003: o cabeçalho do bloco só tem comandos do próprio conteúdo (criar, adicionar, modo de visão); avanço,
    # retorno e a primária da etapa ficam na área de ações única ao fim do conteúdo (engine.area_acoes, preenchida em safra.js)
    acoes=lambda extra='': f'<span style="display: inline-flex; align-items: center; gap: 8px; flex-wrap: wrap; justify-content: flex-end;">{extra}</span>'
    nova_safra=f'<button type="button" onClick="{H("g_saf_new")}" style="{E.BTN_ST(False,True)}">Criar safra</button>'   # criar é secundário: a tarefa da etapa é escolher
    s1=bloco('Escolha a safra','Clique na safra para continuar de onde parou.',g_saf,acao=nova_safra)
    # SOLO-01 §3.4: "Sugestões pelas análises · N" só com 1 sugestão ou mais (R01, D-29): quem não usa análise não vê nada
    sg_lnk=f'<sc-if value="{H("sg_has")}" hint-placeholder-val="{F()}"><button type="button" id="sg_lnk" class="acoes-lnk" onClick="{H("sg_abrir")}" style="min-height: 28px; white-space: nowrap;">{H("sg_lnk")}</button></sc-if>'
    plt_lnk=f'<sc-if value="{H("plt_tem")}" hint-placeholder-val="{F()}"><button type="button" id="plt-abrir" class="acoes-lnk" aria-haspopup="dialog" onClick="{H("plt_abrir")}" style="min-height: 28px; white-space: nowrap;">Planejar talhões livres…</button></sc-if>'   # SAF-FAZ-3 (C)
    from areas import saf_lote as SLT   # EDL-01 (16/10/2026): "Editar talhões…" da fazenda numa grade só (safra_lote.js)
    s2=bloco('Talhões e cultivos',H('k2'),cult_html,desc_hole=True,acao=plt_lnk+SLT.link()+sg_lnk)   # sem botão: planeja-se pela linha do talhão (Planejar ›, Dividir, Vincular ciclo ›)
    # etapa 3: título com o custo de operação e o link "Resumo da safra"; veredito (role=status) e, fora dele, a linha de capacidade;
    # g_cap recolhida; linha de filtro (só com recurso × mês escolhido); g_op por último (estica e só a área de dados rola)
    custo=(f'<span style="display: inline-flex; align-items: baseline; gap: 6px; flex-wrap: wrap; justify-content: flex-end; font-size: 12.8px; color: {MUTED};">'
           f'<span>Custo de operação <b style="color: {INK};">{H("v3_cop")}</b> · {H("v3_copq")}</span>'
           f'<button type="button" class="acoes-lnk" data-acao="resumo" onClick="{H("rs_abrir")}" style="min-height: 24px;">Resumo da safra</button></span>')
    linha_cap=(f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 0 4px 8px;">'
               f'<span style="flex-grow: 1;"></span><button type="button" class="acoes-lnk g2seta-nome" aria-expanded="{H("v3_capexp")}" onClick="{H("v3_captog")}">{E.seta()}Capacidade por mês</button></div>')
    filtro=(f'<sc-if value="{H("v3_fil")}" hint-placeholder-val="{F()}"><div role="status" tabIndex="-1" id="saf-cap-filtro" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 0 4px 8px; font-size: 12.8px;">'
            f'<span>Mostrando <b>{H("v3_filn")}</b>: {H("v3_filt")}</span><button type="button" onClick="{H("v3_filx")}" style="{_MINI}">Ver todas</button></div></sc-if>')
    # 15/10/2026 (proprietário: "esses avisos e alertas deixe apenas dentro da tabela de forma visual, não fora dela"): o veredito fica para o
    # leitor de tela (role=status, sem ocupar a tela) e os atalhos de recurso saíram; o recurso em falta aparece só como ⚠ na linha (dica com o mês)
    corpo3=(f'<p id="saf-v3-ver" class="acoes-sr" style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; margin: 0;"><span role="status" style="{H("v3_vst")}">{H("v3_ver")}</span></p>'
            + linha_cap + f'<sc-if value="{H("v3_capab")}" hint-placeholder-val="{F()}"><div id="saf-cap" style="padding-bottom: 10px;">{cap_html}</div></sc-if>' + filtro + g_op)
    s3=bloco('Operações e recursos','',corpo3,acao=custo)
    s4=bloco('Demanda de insumos por grupo',H('k6'),g_dem,desc_hole=True,
                acao=f'<span style="display: inline-flex; align-items: center; gap: 8px;"><sc-if value="{H("sol_link")}" hint-placeholder-val="{F()}"><a href="{H("sol_href")}" style="{_MINI} text-decoration: none;">Abrir em Compra de insumos ›</a></sc-if></span>')
    # SAF-FAZ-2: safra de várias fazendas mostra as fazendas dela; um toque troca de fazenda na mesma etapa (cada uma com a própria sub-safra)
    # 16/10/2026 (proprietário: "abaixo de trabalhando em… em fazendas… não falta o símbolo do filtro que é nosso padrão?"): a faixa das fazendas
    # usa a peça comum dos filtros (ui37.faixa_filtros: funil, rótulo e chips), não um desenho próprio; id e nome acessível continuam os mesmos
    sg_chips=(f'<sc-for list="{H("sg_fz")}" as="fz" hint-placeholder-count="2"><button type="button" aria-pressed="{H("fz.on")}" aria-label="{H("fz.al")}" onClick="{H("fz.go")}" style="{_MINI} min-height: 36px;">{H("fz.t")}</button></sc-for>')
    sg_faixa=(f'<sc-if value="{H("sg_tem")}" hint-placeholder-val="{F()}">'
              + UI.faixa_filtros(UI.faixa_campo('Fazendas',sg_chips) + f'<span style="font-size: 12.5px; color: {MUTED}; flex: 1 1 220px;">{H("sg_res")}</span>',
                                 fim=f'<sc-if value="{H("sg_env")}" hint-placeholder-val="{F()}"><button type="button" id="sg-env" onClick="{H("sg_envGo")}" style="{E.BTN_ST(False,True)}">{H("sg_envT")}</button></sc-if>')
                .replace('<div class="mf-tela" role="group" aria-label="Filtros"','<div class="mf-tela" id="saf-fazendas" role="group" aria-label="Fazendas desta safra"',1)
              + '</sc-if>')
    EXTRA.append('<style>#saf-fazendas button[aria-pressed="true"]{background:#E4F3E9!important;border-color:#1E7A4C!important;color:#14532D!important;box-shadow:inset 0 0 0 1px #1E7A4C}</style>')   # a fazenda aberta, como o chip escolhido
    corpo=sg_faixa+''.join(f'<sc-if value="{H("s"+str(i))}" hint-placeholder-val="{H("true") if i==1 else F()}"><div style="display: flex; flex-direction: column; gap: 14px;">{s}</div></sc-if>'
                  for i,s in enumerate([s1,s2,s3,s4],1)) + E.area_acoes('aa','Ações da etapa')
    # ---------- painel: Resumo da safra (§4.3) ----------
    rs_lin=(f'<div style="display: grid; grid-template-columns: minmax(0,1.2fr) 90px minmax(0,1fr) minmax(0,1fr) minmax(0,1.1fr); gap: 8px; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 12.8px; align-items: baseline;">'
            f'<b>{H("rl.cult")}</b><span style="text-align: right;">{H("rl.area")}</span><span style="text-align: right;">{H("rl.cop")}</span><span style="text-align: right;">{H("rl.cins")}</span><span style="text-align: right; font-weight: 700;">{H("rl.rha")}</span>'
            f'<sc-if value="{H("rl.temNota")}" hint-placeholder-val="{F()}"><span style="grid-column: 1 / -1; font-size: 11.8px; color: {MUTED};">{H("rl.nota")}</span></sc-if></div>')
    EXTRA.append(
      f'<sc-if value="{H("rs_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar" onClick="{H("rs_fechar")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="Resumo da safra" onKeyDown="{H("rs_key")}" style="position: relative; width: 620px; max-width: 100%; height: 100%; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
      f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1;">Resumo da safra · {H("rs_saf")}</h2><button type="button" aria-label="Fechar" onClick="{H("rs_fechar")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED};">×</button></div>'
      f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">Custo por cultura</div>'
      f'<div style="display: grid; grid-template-columns: minmax(0,1.2fr) 90px minmax(0,1fr) minmax(0,1fr) minmax(0,1.1fr); gap: 8px; font-size: 10.5px; font-weight: 700; letter-spacing: .03em; text-transform: uppercase; color: {MUTED};">'
      f'<span>Cultura</span><span style="text-align: right;">Área com plano</span><span style="text-align: right;">Custo de operação</span><span style="text-align: right;">Insumos do plano</span><span style="text-align: right;">Custo total R$/ha</span></div>'
      f'<sc-for list="{H("rs_lin")}" as="rl" hint-placeholder-count="3">{rs_lin}</sc-for>'
      f'<div style="font-size: 12.5px; color: {MUTED}; line-height: 1.45;">{H("rs_nota")}</div>'
      f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase; padding-top: 4px;">Trabalho da safra</div>'
      f'<div style="font-size: 13px; line-height: 1.45;">{H("rs_trab")}</div>'
      f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase; padding-top: 4px;">Como a conta é feita</div>'
      f'<ul style="margin: 0; padding-left: 18px; font-size: 12.5px; color: {MUTED}; line-height: 1.5;"><sc-for list="{H("rs_conta")}" as="rc" hint-placeholder-count="3"><li>{H("rc.t")}</li></sc-for></ul>'
      f'<div style="flex-grow: 1;"></div><div style="display: flex; justify-content: flex-end; padding-top: 6px; border-top: 1px solid {LINE};"><button type="button" onClick="{H("rs_fechar")}" style="{BTN_ST(False,True)}">Fechar</button></div>'
      f'</aside></div></sc-if>')
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
      f'<sc-if value="{H("ap_normal")}" hint-placeholder-val="{H("true")}"><div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};"><button type="button" onClick="{H("ap_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" onClick="{H("ap_apply")}" style="{BTN_ST(True,True)}">{H("ap_btn")}</button></div></sc-if>'
      f'</aside></div></sc-if>')
    # ---------- painel: atividades locais do cultivo (Gatilho → Atividades → Produtos e doses) ----------
    prod_row=(f'<div style="display: grid; grid-template-columns: minmax(0,1fr) minmax(0,1.6fr) 88px 122px 82px 94px 150px; gap: 10px; align-items: center; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 12.5px;">'
              f'<span style="color: {MUTED};">{H("p.grupo")}</span><span style="font-weight: 600;">{H("p.nome")}<sc-if value="{H("p.aj")}" hint-placeholder-val="{F()}"> <span style="{H("p.ajSt")}">{H("p.ajT")}</span></sc-if>'
              f'<sc-if value="{H("p.rmv")}" hint-placeholder-val="{F()}"> <span style="display: inline-block; padding: 1px 7px; border-radius: 999px; background: {REDS}; color: {RED}; font-size: 11px; font-weight: 700;">{H("p.rmT")}</span></sc-if>'
              f'<sc-if value="{H("p.novo")}" hint-placeholder-val="{F()}"> <span style="display: inline-block; padding: 1px 7px; border-radius: 999px; background: {ACCS}; color: {ACC}; font-size: 11px; font-weight: 700;">incluído neste talhão</span></sc-if></span>'
              f'<span style="color: {MUTED}; white-space: nowrap; text-align: right;">{H("p.padrao")}</span>'
              f'<span style="display: flex; align-items: center; gap: 4px; white-space: nowrap;"><input id="{H("p.fid")}" aria-label="Dose local de {H("p.nome")}" value="{H("p.v")}" onChange="{H("p.set")}" readOnly="{H("p.dis")}" style="{H("p.ist")}"><span style="color: {MUTED}; font-size: 11.5px;">{H("p.un")}</span></span>'
              f'<span style="color: {MUTED}; white-space: nowrap; text-align: right;">{H("p.preco")}</span><span style="font-weight: 700; white-space: nowrap; text-align: right;">{H("p.custo")}</span>'
              f'<span style="display: flex; gap: 4px; justify-content: flex-end; flex-wrap: wrap;"><sc-if value="{H("p.podeRest")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("p.reset")}" title="Voltar à dose do plano padrão" style="{_MINI} font-size: 11px; padding: 3px 7px;">Restaurar dose</button></sc-if>'
              f'<sc-if value="{H("p.podeRet")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("p.ret")}" aria-label="Retirar {H("p.nome")} deste talhão" style="{_MINI} font-size: 11px; padding: 3px 7px; color: {RED};">Retirar</button></sc-if>'
              f'<sc-if value="{H("p.podeDesf")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("p.desf")}" aria-label="Desfazer a retirada de {H("p.nome")}" style="{_MINI} font-size: 11px; padding: 3px 7px;">Desfazer</button></sc-if></span></div>'
              f'<sc-if value="{H("p.hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 11.5px; color: {RED}; font-weight: 700;">{H("p.err")}</div></sc-if>'
              # SOLO-01 §3.2: sugestão da análise sob a linha do produto, em texto cinza, sem cor de alerta; ações secundárias que preenchem o rascunho
              f'<sc-if value="{H("p.hasSug")}" hint-placeholder-val="{F()}"><div class="so-sug" role="note" style="display: flex; flex-wrap: wrap; align-items: center; gap: 2px 6px; padding: 2px 0 6px; font-size: 12.5px; color: {MUTED}; line-height: 1.5;">'
              f'<span>Análise sugere <b style="color: {INK};">{H("p.sugD")}</b> · {H("p.sugQ")} ·</span>'
              f'<button type="button" id="{H("p.pqId")}" onClick="{H("p.sugPq")}" style="border: 0; background: transparent; padding: 0 2px; color: {ACC}; font-family: inherit; font-size: 12.5px; font-weight: 700; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; min-height: 28px;">Por quê</button><span aria-hidden="true">·</span>'
              f'<button type="button" onClick="{H("p.sugGo")}" style="border: 0; background: transparent; padding: 0 2px; color: {ACC}; font-family: inherit; font-size: 12.5px; font-weight: 700; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; min-height: 28px;">{H("p.sugU")}</button></div></sc-if>')
    EXTRA.append(
      f'<sc-if value="{H("lp_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar" onClick="{H("lp_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="{H("lp_titulo")}" style="position: relative; width: 920px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
      f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1;">{H("lp_titulo")}</h2><button type="button" aria-label="Fechar" onClick="{H("lp_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED};">×</button></div>'
      f'<div style="font-size: 13px; color: {MUTED};">{H("lp_sub")}</div>'
      f'<sc-if value="{H("lp_hasInfo")}" hint-placeholder-val="{F()}"><sc-for list="{H("lp_info")}" as="q" hint-placeholder-count="1"><div style="font-size: 12.5px; color: {MUTED};">{H("q.t")} <a href="{H("q.h")}" style="color: {ACC}; font-weight: 700; text-decoration: none;">Ver laudo ›</a></div></sc-for></sc-if>'
      f'<sc-if value="{H("lp_hasIncSug")}" hint-placeholder-val="{F()}"><sc-for list="{H("lp_incSug")}" as="q" hint-placeholder-count="1"><div class="so-sug" role="note" style="display: flex; flex-wrap: wrap; align-items: center; gap: 2px 6px; padding: 8px 10px; background: {BG}; border-radius: 10px; font-size: 12.5px; color: {MUTED}; line-height: 1.5;">'
      f'<span>Análise sugere <b style="color: {INK};">{H("q.d")}</b> · {H("q.q")} ·</span><button type="button" id="{H("q.pqId")}" onClick="{H("q.pq")}" style="border: 0; background: transparent; padding: 0 2px; color: {ACC}; font-family: inherit; font-size: 12.5px; font-weight: 700; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; min-height: 28px;">Por quê</button><span aria-hidden="true">·</span>'
      f'<button type="button" onClick="{H("q.go")}" style="border: 0; background: transparent; padding: 0 2px; color: {ACC}; font-family: inherit; font-size: 12.5px; font-weight: 700; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; min-height: 28px;">{H("q.u")}</button></div></sc-for></sc-if>'
      f'<sc-if value="{H("lp_hasIncl")}" hint-placeholder-val="{F()}"><div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">Incluída pela análise</div><sc-for list="{H("lp_incl")}" as="q" hint-placeholder-count="1">'
      f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 4px 10px; padding: 8px 10px; border: 1px solid {LINE}; border-radius: 10px; font-size: 12.8px;"><b>{H("q.t")}</b><span style="color: {MUTED};">{H("q.d")}</span>'
      f'<span style="display: inline-block; padding: 1px 7px; border-radius: 999px; background: #E3F0FB; color: #1E5F8F; font-size: 11px; font-weight: 700;">{H("q.chip")}</span><span style="flex-grow: 1;"></span>'
      f'<sc-if value="{H("q.podeDesf")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("q.desf")}" style="{_MINI} font-size: 11px; padding: 3px 7px;">{H("q.desfT")}</button></sc-if></div></sc-for></sc-if>'
      f'<sc-if value="{H("lp_hasCmdErr")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("lp_cmdErr")}</div></sc-if>'
      f'<sc-if value="{H("lp_nerr")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">Corrija os campos destacados; o que você digitou foi mantido.</div></sc-if>'
      f'<sc-for list="{H("lp_grupos")}" as="g" hint-placeholder-count="1"><div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase; padding-top: 4px;">{H("g.t")}</div>'
      f'<sc-for list="{H("g.gats")}" as="t" hint-placeholder-count="2"><div style="border: 1px solid {LINE}; border-radius: 12px; overflow: hidden;">'
      f'<div style="display: flex; align-items: center; gap: 8px; padding: 8px 10px; background: {BG};">{E.seta_abrir(H("t.exp"),H("t.lab"),H("t.tog"))}<b style="font-size: 13.5px;">{H("t.t")}</b><span style="font-size: 12px; color: {MUTED};">· {H("t.dt")}</span></div>'
      f'<sc-if value="{H("t.open")}" hint-placeholder-val="{H("true")}"><div style="padding: 4px 12px 10px;"><sc-for list="{H("t.atvs")}" as="a" hint-placeholder-count="1"><div style="padding: 6px 0;">'
      f'<div style="display: flex; align-items: center; gap: 8px;">{E.seta_abrir(H("a.exp"),H("a.lab"),H("a.tog"))}<span style="font-size: 13px; font-weight: 700;">{H("a.t")}</span><span style="font-size: 12px; color: {MUTED};">· {H("a.op")}</span></div>'
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
            f'<span data-un="meta" style="font-size: 13px; color: {MUTED}; white-space: nowrap;">{H("r.unm")}</span>'   # unidade de mercado da cultura (DEC-0510-03), sem escolha
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
    EXTRA.append(SLT.painel())   # EDL-01 · painel "Editar talhões da <fazenda>"
    # ---------- painéis da análise de solo (SOLO-01): Sugestões pelas análises (lote) e Por quê ----------
    from areas.analise_solo import _overlay, _cabeca
    g_sug=grid([dict(k='tal',l='Talhão',w=110),dict(k='item',l='Atividade · produto',w=190),dict(k='pad',l='Padrão',w=130),dict(k='sug',l='Sugestão',w=140),
                dict(k='dif',l='Diferença no talhão',t='num',a='r',w=150),dict(k='lau',l='Laudo',w=170),dict(k='tipo',l='Tipo',w=100),dict(k='res',l='Resultado',w=170)],[],
               edit=dict(m='none'),sel=True,gid='g_sug',total=False,qf=dict(k='tipo',l='tipo',todas='Todas'))
    pe_sg=(f'<div class="so-pe" style="position: sticky; bottom: -20px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin: 0 -22px -20px; padding: 12px 22px; background: {SURF}; border-top: 1px solid {LINE};">'
           f'<span style="font-size: 12.5px; color: {MUTED};">{H("sg_pe")}</span><span style="flex-grow: 1;"></span><button type="button" onClick="{H("sg_close")}" style="{BTN_ST(False,True)}">{H("sg_closeT")}</button>'
           f'<button type="button" aria-disabled="{H("sg_pdis")}" onClick="{H("sg_pgo")}" style="{BTN_ST(True,True)} {H("sg_pst")}">{H("sg_pt")}</button></div>')
    corpo_sg=(_cabeca('sg_',chip=False)
              + f'<sc-if value="{H("sg_hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("sg_err")}</div></sc-if>'
              + g_sug + f'<div style="flex-grow: 1;"></div>' + pe_sg)
    EXTRA.append(_overlay('sg_',1080,corpo_sg))
    EXTRA.append(porque_html())
    EXTRA.append('<style>@media (max-width:640px){.so-sug button{min-height:44px!important}.so-pan{padding:16px 14px!important}.so-pe{margin:0 -14px -16px!important;padding:12px 14px!important}.so-pe button{min-height:44px}}</style>')
    # SAF-FAZ-3 (A): na faixa "Trabalhando em", as fazendas da safra em chips ✓ e "+ Fazenda" (etapas 1 e 2 com safra escolhida); sem safra, e nas
    # etapas 3 e 4 (por fazenda), a fazenda em texto, como antes. A lista abre no lugar (popover do DS), com área e talhões de cada fazenda
    lab=f'display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; background: {GRAYS}; font-weight: 700; font-size: 11.5px;'
    sfz=(f'<sc-if value="{H("sfz_txt_on")}" hint-placeholder-val="{H("true")}"><span title="Fazenda da safra aberta" style="{lab}">{H("ctx_faz")}</span></sc-if>'
         f'<sc-if value="{H("sfz_chips_on")}" hint-placeholder-val="{F()}"><span role="group" aria-label="Fazendas da safra" id="saf-fz" style="display: inline-flex; align-items: center; gap: 6px; flex-wrap: wrap;">'
         f'<sc-for list="{H("sfz_chips")}" as="fc" hint-placeholder-count="2"><button type="button" class="sfz-chip" aria-haspopup="dialog" aria-label="{H("fc.al")}" onClick="{H("fc.go")}" disabled="{H("fc.dis")}">{H("fc.t")}</button></sc-for>'
         f'<sc-if value="{H("sfz_add")}" hint-placeholder-val="{F()}"><button type="button" id="sfz-add" class="sfz-add" aria-haspopup="dialog" aria-expanded="{H("sfz_exp")}" onClick="{H("sfz_abrir")}">+ Fazenda</button></sc-if></span></sc-if>')
    EXTRA.append('<style>.sfz-chip,.sfz-add{display:inline-flex;align-items:center;gap:4px;padding:4px 11px;min-height:var(--g2-alvo,30px);box-sizing:border-box;border-radius:999px;font-family:inherit;font-size:12px;font-weight:700;cursor:pointer}'
                 '.sfz-chip{border:1px solid #1E7A4C;background:#E4F3E9;color:#14532D}.sfz-chip:disabled{cursor:default}.sfz-add{border:1px dashed #8A968E;background:#FFFFFF;color:#1E7A4C}'
                 '.sfz-chip:not(:disabled):hover,.sfz-add:hover{border-color:#1E7A4C;background:#D7EEDF}'
                 '.ffz{display:inline-flex;border:1px solid #E4E9E5;border-radius:999px;overflow:hidden;background:#FFFFFF}'
                 '.ffz button{border:0;background:transparent;padding:4px 11px;min-height:var(--g2-alvo,0px);font-family:inherit;font-size:12px;font-weight:700;color:#15201A;cursor:pointer;white-space:nowrap}'
                 '.ffz button+button{border-left:1px solid #E4E9E5}.ffz button[aria-pressed="true"]{background:#1E7A4C;color:#FFFFFF}.ffz button[aria-pressed="false"]:hover{background:#E4F3E9}</style>')
    EXTRA.append(
      f'<sc-if value="{H("sfz_pop")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 70;">'
      f'<button type="button" aria-label="Fechar a lista de fazendas" tabIndex="-1" onClick="{H("sfz_fechar")}" style="position: absolute; inset: 0; border: 0; background: transparent; cursor: default;"></button>'
      f'<div role="dialog" id="sfz-pop" aria-label="Fazendas da safra" onKeyDown="{H("sfz_key")}" style="{H("sfz_pos")} position: fixed; max-height: 70vh; overflow-y: auto; box-sizing: border-box; background: #FFFFFF; border: 1px solid {LINE}; border-radius: 12px; box-shadow: 0 12px 28px -12px rgba(21,32,26,.35); padding: 6px; display: flex; flex-direction: column; gap: 2px; z-index: 71;">'
      f'<div style="padding: 6px 8px 4px; font-size: 11.5px; font-weight: 800; letter-spacing: .04em; color: {MUTED}; text-transform: uppercase;">Fazendas da safra</div>'
      f'<sc-for list="{H("sfz_ops")}" as="o" hint-placeholder-count="3"><label class="sfz-op" style="display: flex; align-items: flex-start; gap: 10px; min-height: 44px; box-sizing: border-box; padding: 7px 8px; border-radius: 8px; cursor: pointer;">'
      f'<input type="checkbox" id="{H("o.id")}" checked="{H("o.on")}" onChange="{H("o.tog")}" style="width: 16px; height: 16px; accent-color: {ACC}; margin: 2px 0 0; flex-shrink: 0;">'
      f'<span style="display: flex; flex-direction: column; gap: 1px; min-width: 0;"><b style="font-size: 13.5px; color: {INK};">{H("o.t")}</b><span style="font-size: 12px; color: {MUTED};">{H("o.sub")}</span>'
      f'<sc-if value="{H("o.hasErr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; color: {RED}; font-weight: 700; line-height: 1.4;">{H("o.err")}</span></sc-if></span></label></sc-for>'
      f'<div style="display: flex; justify-content: flex-end; padding: 6px 4px 2px; border-top: 1px solid {LINE};"><button type="button" onClick="{H("sfz_fechar")}" style="{_MINI}">Fechar</button></div>'
      f'</div></div></sc-if>')
    EXTRA.append('<style>.sfz-op:hover{background:#F2F8F4}</style>')
    # SAF-FAZ-3 (C): painel "Planejar talhões livres" — a escolha múltipla mora aqui (sem caixas na tabela, decisão de 13/10); cultura, plano e
    # data uma vez para todos; um cultivo por talhão, pela regra do cultivo único
    fld=lambda lab_,campo,k,ajuda='': (f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="plt_{k}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{lab_}</label>{campo}'
        + (f'<span style="font-size: 11.5px; color: {MUTED};">{ajuda}</span>' if ajuda else '')
        + f'<sc-if value="{H("plt_he_"+k)}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("plt_e_"+k)}</span></sc-if></div>')
    inp=f'font-family: inherit; font-size: 14px; padding: 9px 11px; border-radius: 10px; border: 1px solid {LINE}; background: #FFFFFF; color: {INK}; min-width: 0;'
    EXTRA.append(
      f'<sc-if value="{H("plt_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar" onClick="{H("plt_fechar")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="{H("plt_titulo")}" id="plt-painel" onKeyDown="{H("plt_key")}" style="position: relative; width: 560px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
      f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1;">{H("plt_titulo")}</h2><button type="button" aria-label="Fechar" onClick="{H("plt_fechar")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED};">×</button></div>'
      f'<div style="font-size: 13px; color: {MUTED};">{H("plt_sub")}</div>'
      f'<sc-if value="{H("plt_hasg")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">{H("plt_gerr")}</div></sc-if>'
      f'<div style="display: flex; align-items: center; gap: 12px;"><span style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase; flex-grow: 1;">Talhões livres</span>'
      f'<button type="button" class="acoes-lnk" onClick="{H("plt_todos")}" style="min-height: 28px;">Marcar todos</button><button type="button" class="acoes-lnk" onClick="{H("plt_nenhum")}" style="min-height: 28px;">Desmarcar</button></div>'
      f'<sc-for list="{H("plt_grupos")}" as="g" hint-placeholder-count="2"><div role="group" aria-label="{H("g.cab")}" style="display: flex; flex-direction: column; gap: 6px;">'
      f'<sc-if value="{H("g.multi")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; font-weight: 800; color: {INK}; padding-top: 2px;">{H("g.cab")}</div></sc-if>'
      f'<sc-for list="{H("g.itens")}" as="it" hint-placeholder-count="2"><label style="display: flex; align-items: flex-start; gap: 10px; padding: 8px 10px; min-height: 44px; box-sizing: border-box; border: 1px solid {LINE}; border-radius: 10px; cursor: pointer;">'
      f'<input type="checkbox" id="{H("it.id")}" checked="{H("it.on")}" onChange="{H("it.tog")}" style="width: 16px; height: 16px; accent-color: {ACC}; margin: 2px 0 0; flex-shrink: 0;">'
      f'<span style="display: flex; flex-direction: column; gap: 2px; min-width: 0;"><b style="font-size: 13.5px;">{H("it.t")}</b><span style="font-size: 12.5px; color: {MUTED};">{H("it.txt")}</span>'
      f'<sc-if value="{H("it.hasErr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; color: {RED}; font-weight: 700; line-height: 1.4;">{H("it.err")}</span></sc-if></span></label></sc-for></div></sc-for>'
      f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; padding-top: 6px; border-top: 1px solid {LINE};">'
      + fld('Cultura',f'<select id="plt_cult" value="{H("plt_cult")}" onChange="{H("plt_setCult")}" style="{inp}"><sc-for list="{H("plt_cults")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>','cult')
      + fld('Variedade',f'<input id="plt_var" value="{H("plt_var")}" onChange="{H("plt_setVar")}" autoComplete="off" style="{inp}">','var')
      + fld('Plano agronômico',f'<select id="plt_plano" value="{H("plt_plano")}" onChange="{H("plt_setPlano")}" style="{inp}"><sc-for list="{H("plt_planos")}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>','plano')
      + fld('Plantio',f'<input type="date" id="plt_plantio" value="{H("plt_plantio")}" onChange="{H("plt_setPlantio")}" style="{inp}">','plantio',H('plt_pminT'))
      + fld('Meta de produtividade',f'<span style="display: flex; align-items: center; gap: 6px;"><input id="plt_meta" inputMode="decimal" value="{H("plt_meta")}" onChange="{H("plt_setMeta")}" autoComplete="off" style="{inp} flex: 1 1 auto; width: 100%;"><span style="font-size: 12.5px; color: {MUTED}; white-space: nowrap;">{H("plt_un")}</span></span>','meta')
      + f'</div><div style="flex-grow: 1;"></div>'
      f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};"><button type="button" onClick="{H("plt_fechar")}" style="{BTN_ST(False,True)}">Cancelar</button>'
      f'<button type="button" id="plt-gravar" onClick="{H("plt_salvar")}" style="{BTN_ST(True,True)} {H("plt_btnSt")}">{H("plt_btn")}</button></div>'
      f'</aside></div></sc-if>')
    HEIGHTS37[fname]=1500
    shell37('SAF','Planejar safra',corpo,fname=fname,subtitle='',
            steps=steps_state(NOMES),primary_html=None,  # cartão da faixa leva à etapa (15/10); avanço/retorno/primária também na área de ações
            ctx=(H('ctx_faz'),H('ctx_saf'),None),search=False,mf_ini=sfz,
            mf_fim='')   # 14/10/2026 (proprietário: "tire comparar versões do plano"): a entrada saiu da faixa; o painel (CONTROLE-02) segue no código   # na faixa "Trabalhando em": devolve ao Total a altura que a faixa nova tomou (L1 a 1440 × 1040; diagnóstico 13/10)
