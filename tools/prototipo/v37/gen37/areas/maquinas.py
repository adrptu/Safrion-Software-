# -*- coding: utf-8 -*-
"""Máquinas (módulo OCULTO do menu, preservado) — processo sequencial por links:
MA-01 Confira os ativos › MA-02 Registre inspeções › MA-03 Planeje a manutenção › MA-04 Execute as ordens (+ MA-04det OM-0233)
› MA-05 Acompanhe abastecimentos (cap. 47, 53–54).

observacoes (dados locais coerentes com dados.py / dados2.py / processo_os.py / planejamento.py):
- Ativos, ordens de manutenção, casos e lançamentos continuam locais (não existem em dados/dados2); OM-0233, Trator T1, OS-0420
  (30 ha feitos, saldo 70 ha) e o substituto Trator 02 · MF 7719 vêm de dados.OM / dados.OS.
- Substituição antes da confirmação do PCP usa um único rótulo: "Proposto · OS-0420 saldo 70 ha · aguarda PCP" (defeito DEMO-04).
- DEMO-17: a inspeção INSP-105 (checklist da manutenção, 23/09 07:10) executa o bloqueio do T1 antes do início e propaga o
  impedimento para a OS-0431 (plantio Soja 58 W · T2 · 102 ha, retirada de Liberadas → A liberar), como em planejamento.py
  (OS_DEMO17). IDs conforme dados.ORDENS (OS-0423 é o gotejo T7, não o plantio T2).
- MF 7719: revisão 250 h contada da última revisão (2.793 h) → vence em 3.043 h ≈ 28/09 a 11 h/dia (antes 29/09, incoerente).
- Pareto 30 d (MA-02): Bomba do Pivô 2 (SM-0152/OM-0228, 4,0 h) conta só em Hidráulico; Elétrico usa OB-0104 (sensor da
  esteira do Packing, 4,0 h) + sensores do pulverizador (2,0 h). Total 40,0 h sem dupla contagem.
- Custo da OM-0233 = peças R$ 4,1 mil + horas de oficina × R$ 320/h (hipótese), recalculado a cada tarefa salva.
"""
import json, re
from engine import (grid,table,section,kpis,chip,btn,icon,esc,msgbtn,drawer_button,stepper,Pt,
                    INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,RED,GRAYS,BTN_ST,EXTRAJS,_MINI)
import engine as E
from ui37 import shell37, steps_bar, continuity, HEIGHTS37, PARENT37
import dados as D

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
ETAPAS=[('Confira os ativos','MA-01.dc.html',''),('Registre inspeções','MA-02.dc.html',''),
        ('Planeje a manutenção','MA-03.dc.html','Conflito de janela'),('Execute as ordens','MA-04.dc.html','T1 bloqueado'),
        ('Acompanhe abastecimentos','MA-05.dc.html','')]
def faixa(i):
    return steps_bar([dict(t=t,href=h,why=w,tip=(t+(' · '+w if w else ''))) for t,h,w in ETAPAS],current=i)
SUBST='Proposto · OS-0420 saldo 70 ha · aguarda PCP'
OS420=next(o for o in D.OS if o['id']=='OS-0420')
OS431=D.ORDEM['OS-0431']

# ---------- botões com ícone + rótulo + title ----------
def _ic(html,name,title):
    m=re.match(r'^(<(button|a)\b[^>]*?)>(.*)</(button|a)>$',html,re.S)
    return f'{m.group(1)} title="{esc(title)}"><span style="display: inline-flex; align-items: center; gap: 6px;">{icon(name,14)}{m.group(3)}</span></{m.group(4)}>'
def imsg(t,msg,ic,title,primary=False): return _ic(msgbtn(t,msg,primary=primary),ic,title)
def idrw(t,d,ic,title,primary=False): return _ic(drawer_button(t,d,primary=primary),ic,title)
def ilnk(t,href,ic,title): return _ic(btn(t,small=True,href=href),ic,title)
def sbtn(t,fn,ic,title,primary=False):
    return (f'<button type="button" onClick="{H(fn)}" title="{esc(title)}" style="{BTN_ST(primary,True)}">'
            f'<span style="display: inline-flex; align-items: center; gap: 6px;">{icon(ic,14)}{esc(t)}</span></button>')
def acoes(*xs): return ''.join(xs)

JSBASE=r'''
function ma_G(id){ return GRIDS.find(g=>g.id===id); }
function ma_R(self,id){ return g2rows(self,ma_G(id)); }
function ma_nf(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function ma_chip(t,c){ return {k:'chip',t:t,c:c}; }
'''

E.MSGS['Confirmar 2 paradas']=('Confirmadas 2 de 3 · Plantadeira (25/09) e Bomba do Pivô 2 (01/10) viram ordens em rascunho (A liberar) · '
                              'MF 7719 segue proposta: janela 28/09 em conflito com a OS-0420 — simule outra janela em Manutenções e impacto na produção')
E.DRAWERS['Planejar e autorizar ordem']=dict(title='Planejar e autorizar ordem de manutenção',
    sub='Autorização é da manutenção; liberar para a oficina é passo seguinte e separado.',
    fields=[('Ordem','OM-0234 · Trator 02 · MF 7719'),('Serviço','Preventiva 250 h'),('Janela preferida','29/09 a 30/09 (fora da OS-0420)'),
            ('Mecânico','Zé (mecânico)'),('Peças','kit filtros + óleo 16 L'),('Duração estimada (h)','5')],
    confirm='Autorizar ordem',done='OM-0234 autorizada para 29/09 · segue em A liberar até a liberação do serviço')

# =====================================================================================
def ma01():
    fn='MA-01.dc.html'; HEIGHTS37[fn]=1000
    AT=[
     dict(id='t1',nome=D.OM['ativo'],cat='Trator',local='Oficina Sede',hor=4312,cond='Bloqueado',ag='Agenda retirada',agc='gray',
          prox='Corretiva em execução',proxs='OM-0233 · OS-0420 · OS-0431',util=58,resp='Zé (mecânico)',motb='Pressão hidráulica baixa · SM-0147 e INSP-105'),
     dict(id='t2',nome=D.OM['substituto'],cat='Trator',local='Santa Rita, T4',hor=2988,cond='Apto',ag=SUBST,agc='yellow',
          prox='Preventiva 250 h · 28/09 · em conflito',proxs='OM-0234 · OS-0420',util=71,resp='Zé (mecânico)'),
     dict(id='pulv',nome='Pulverizador · Uniport 3030',cat='Pulverizador',local='T1',hor=1542,cond='Apto',ag='Comprometido · OS-0421',agc='gray',
          prox='Troca de óleo por análise',proxs='OS-0421 · OM-0230',util=83,resp='Zé (mecânico)'),
     dict(id='plant',nome='Plantadeira 24 linhas',cat='Implemento',local='Galpão 1',hor=886,cond='Apto',ag='Livre',agc='green',
          prox='Vencida 20/09 · proposta 25/09',proxs='NC-0912',util=12,resp='PCM'),
     dict(id='colh',nome='Colhedora · S680',cat='Colhedora',local='Galpão 2',hor=3107,cond='Apto',ag='Livre',agc='green',
          prox='Revisão 500 h · 15/10',proxs='SM-0150 · OM-0221',util=19,resp='PCM'),
     dict(id='bomba',nome='Bomba do Pivô 2',cat='Irrigação (fixo)',local='P2',hor=8914,cond='Restrito · monitorado',ag='Comprometido · OS-0419',agc='gray',
          prox='Inspeção hoje 14:00',proxs='OM-0228 · OS-0419',util=55,resp='Equipe elétrica',motr='Pressão baixa recorrente · operar só com monitoramento'),
     dict(id='pack',nome='Packing linha 1',cat='Beneficiamento (fixo)',local='Armazém Sede',hor=12301,cond='Apto',ag='Livre',agc='green',
          prox='Mensal · 01/10',proxs='OB-0104 (encerrada)',util=44,resp='PCM'),
     dict(id='silo',nome='Silo e secador 1',cat='Armazenagem (fixo)',local='Armazém Sede',hor=1940,cond='Apto',ag='Livre',agc='green',
          prox='Calendário · 10/10',proxs='sem ordem vinculada',util=30,resp='PCM'),
    ]
    LK=dict(t1='MA-04det.dc.html',t2='MA-04.dc.html',pulv='MA-04.dc.html',plant='MA-02.dc.html',colh='MA-02.dc.html',bomba='MA-04.dc.html')
    rows=[]
    for a in AT:
        v={k:a.get(k,'') for k in ('nome','cat','local','hor','cond','ag','agc','prox','proxs','util','resp','motr','motb')}
        v['lk']=LK.get(a['id'],'')
        rows.append(dict(id=a['id'],v=v,s={},p={}))
    g_at=grid([dict(k='ativo',l='Ativo · local · horímetro',w=195),
               dict(k='cond',l='Condição técnica',chips={'Apto':'green','Restrito · monitorado':'yellow','Bloqueado':'red'}),
               dict(k='agenda',l='Agenda',w=330),dict(k='eleg',l='Elegível p/ tarefa'),dict(k='prox',l='Próxima manutenção · ordens',w=170),
               dict(k='util',l='Uso 30 d',t='num',a='r',u='%')],rows,
       edit=dict(m='form',title='Ativo',sub='Restrinja ou libere o ativo com motivo e responsável. O Trator T1 só é liberado pela OM-0233, com teste aprovado.',
            fields=[dict(k='local',l='Local',t='sel',opts=['Oficina Sede','Santa Rita, T4','T1','P2','Galpão 1','Galpão 2','Armazém Sede'],req=True),
                    dict(k='hor',l='Horímetro',t='num',u='h',ro=True,help='Vem dos apontamentos e abastecimentos; troca de contador exige evento próprio.'),
                    dict(k='cond',l='Condição técnica',t='sel',opts=['Apto','Restrito · monitorado','Bloqueado'],req=True),
                    dict(k='motr',l='Motivo da restrição',t='area',req=True,cond=dict(k='cond',eq='Restrito · monitorado')),
                    dict(k='motb',l='Motivo do bloqueio',t='area',req=True,cond=dict(k='cond',eq='Bloqueado')),
                    dict(k='resp',l='Responsável técnico',t='sel',opts=['Zé (mecânico)','Rui','Equipe elétrica','PCM'],req=True)]),
       gid='g_at',total=False)
    UT=[('Tratores',2,800,[('Trator T1 · JD 6M 155',360,58),('Trator 02 · MF 7719',440,71)]),
        ('Pulverizadores',1,515,[('Pulverizador · Uniport 3030',515,83)]),
        ('Colheita e implementos',2,192,[('Plantadeira 24 linhas',74,12),('Colhedora · S680',118,19)]),
        ('Fixos (irrigação, beneficiamento, armazenagem)',3,800,[('Bomba do Pivô 2',341,55),('Packing linha 1',273,44),('Silo e secador 1',186,30)])]
    g_ut=grid([dict(k='grupo',l='Grupo/classe',w=300),dict(k='n',l='Ativos',t='num',a='r'),dict(k='ht',l='Horas trabalhadas 30 d',t='num',a='r',u='h'),
               dict(k='hd',l='Horas disponíveis 30 d',t='num',a='r',u='h'),dict(k='ut',l='Utilização',t='num',a='r',u='%')],
       [dict(id=f'u{i}',v=dict(grupo=g,n=n,ht=ht,hd=n*620,ut=round(ht*100/(n*620))),s={},p={},
             o=[dict(t=f'{nm} · {h} h de 620 h ({u}%)') for nm,h,u in its]+[dict(t=f'Soma: {ht} h ÷ ({n} × 620 h) — nunca média de médias')]) for i,(g,n,ht,its) in enumerate(UT)],
       edit=dict(m='origin',title='Utilização do grupo',fields=[dict(k='grupo',l='Grupo',ro=True),dict(k='ut',l='Utilização',t='num',u='%',ro=True)]),
       search=False,gid='g_ut',total=False)
    sel=(f'<label style="display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; font-weight: 700; color: {MUTED};">Tarefa'
         f'<select aria-label="Tarefa para calcular a elegibilidade" title="Escolha a tarefa para calcular a elegibilidade" value="{H("tar_v")}" onChange="{H("tar_set")}" '
         f'style="font-family: inherit; font-size: 12.5px; font-weight: 600; padding: 6px 8px; border: 1px solid {LINE}; border-radius: 8px; background: {SURF}; color: {INK};">'
         f'<option value="pl">Plantio Soja 58 W · OS-0420</option><option value="pu">Pulverização fungicida · OS-0421</option><option value="no">Sem tarefa</option></select></label>')
    corpo=(kpis([('ATIVOS APTOS',H('k_aptos'),'condição técnica'),('BLOQUEADOS · RESTRITOS',H('k_br'),H('k_brd')),
                 ('LIVRES HOJE',H('k_livres'),'sem compromisso de agenda'),('ELEGÍVEIS P/ TAREFA',H('k_eleg'),H('k_elegd'))])
      + section('Quadro de ativos','Escolha a tarefa para ver quem é elegível; clique na linha para restringir ou liberar com motivo.',
                [sel,ilnk('Ver agenda','PL-04.dc.html','calendar','Abrir a agenda compartilhada com o PCP')],g_at)
      + section('Utilização por grupo','Confira horas somadas sobre horas disponíveis; clique no grupo para ver os ativos que formam a taxa.','',g_ut,state='gray'))
    EXTRAJS[0]=JSBASE+r'''
const MA_ELEG={pl:{t1:1,t2:1,plant:1},pu:{pulv:1},no:{}};
const MA_TAR={pl:'plantio Soja 58 W · OS-0420',pu:'pulverização fungicida · OS-0421',no:'escolha uma tarefa'};
function PREVALS(self,v){ const tar=self.state.tar||'pl'; const rows=ma_R(self,'g_at');
  let ap=0,br=[],liv=0,el=0;
  rows.forEach(r=>{ const x=r.v; const c=x.cond||'Apto';
    r.p.ativo=[{k:'b',t:x.nome},{k:'br',t:''},{k:'mut',t:x.cat+' · '+x.local+' · '+ma_nf(x.hor)+' h'}]; r.s.ativo=x.nome+' · '+x.cat+' · '+x.local;
    r.p.cond=[ma_chip(c,c==='Apto'?'green':(c==='Bloqueado'?'red':'yellow'))]; r.s.cond=c;
    const ag=(c==='Bloqueado')?['Agenda retirada','gray']:[x.ag,x.agc]; r.p.agenda=[ma_chip(ag[0],ag[1])]; r.s.agenda=ag[0];
    let e; if(tar==='no') e=['—',null]; else if(c==='Bloqueado') e=['Não elegível','red']; else if((MA_ELEG[tar]||{})[r.id]) e=['Elegível','green']; else e=['Não elegível','gray'];
    r.p.eleg=e[1]?[ma_chip(e[0],e[1])]:[{k:'mut',t:'—'}]; r.s.eleg=e[0];
    r.p.prox=[{k:'txt',t:x.prox},{k:'br',t:''},(x.lk?{k:'link',t:x.proxs,h:x.lk}:{k:'mut',t:x.proxs})]; r.s.prox=x.prox+' '+x.proxs;
    if(c==='Apto') ap++; else br.push(x.nome.split(' · ')[0]+(c==='Bloqueado'?' (bloqueado)':' (restrito)'));
    if(ag[0]==='Livre') liv++; if(e[0]==='Elegível') el++; });
  v.k_aptos=ap+' de '+rows.length; v.k_br=String(br.length); v.k_brd=br.join(' · ')||'nenhum';
  v.k_livres=String(liv); v.k_eleg=String(el); v.k_elegd=MA_TAR[tar]; }
function EXTRAVALS(self,v){ v.tar_v=self.state.tar||'pl'; v.tar_set=(e)=>self.setState({tar:e.target.value});
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_at'||!r) return; const c=r.v.cond;
    if(r.id==='t1' && c!=='Bloqueado'){ r.v.cond='Bloqueado'; r.s.cond='Bloqueado';
      self.setState({g2toast:'Trator T1 continua Bloqueado: a liberação só sai da OM-0233, com teste aprovado e decisão de aptidão. Local e responsável foram salvos.'}); return; }
    if(c==='Bloqueado') self.setState({g2toast:r.v.nome+' bloqueado · motivo e responsável registrados · alocações que usam o ativo ficam impedidas e o PCP é avisado (simulado)'});
    else if(c.indexOf('Restrito')===0) self.setState({g2toast:r.v.nome+' restrito · uso só com monitoramento · alocações afetadas avisadas (simulado)'});
    else self.setState({g2toast:'Salvo · '+r.v.nome+' Apto'}); }; }
'''
    shell37('MA-01','Ativos e disponibilidade',corpo,
      subtitle='Frota, implementos, bomba, packing e silo — condição técnica única e agenda compartilhada com o PCP.',
      status=('1 bloqueado · 1 restrito','red'),primary='Registrar inspeção',primary_href='MA-02.dc.html',steps=faixa(1),
      footer='Apto (condição técnica) ≠ livre (agenda) ≠ elegível (perfil da tarefa); o substituto só fica comprometido depois da confirmação do PCP.')

# =====================================================================================
def ma02():
    fn='MA-02.dc.html'; HEIGHTS37[fn]=1000
    abrir=[Pt.cta('Abrir ordem','MA-04det.dc.html',True)]
    CS=[
     dict(id='c1',caso='INSP-105',tipo='Checklist da manutenção',om='OM-0233',ativo=D.OM['ativo'],sint='Pré-uso 23/09 07:10: pressão hidráulica abaixo da faixa · bloqueio executado antes do início',
          crit='Alta',cont=4312,evid='checklist + manômetro',rec='Bloqueado',resp='Zé (mecânico)',pa=abrir),
     dict(id='c2',caso='SM-0147',tipo='Falha em campo',om='OM-0233',ativo=D.OM['ativo'],sint=D.OM['causa']+' · parou aos 30 ha da OS-0420',
          crit='Alta',cont=4312,evid='telemetria + foto',rec='Bloqueado',resp='PCM',pa=abrir),
     dict(id='c3',caso='SM-0152',tipo='Alerta agregado',om='OM-0228',ativo='Bomba do Pivô 2',sint='Pressão baixa 3× esta noite · caso único, sem ordem duplicada',
          crit='Alta',cont=8914,evid='3 leituras de telemetria',rec='Restrito · monitorado',resp='PCM',pa=[Pt.link('Ver OM-0228','MA-04.dc.html')]),
     dict(id='c4',caso='INSP-104',tipo='Checklist do operador',om='',ativo=D.OM['substituto'],sint='Vazamento leve em mangueira',
          crit='Média',cont=2988,evid='foto',rec='Apto · reparo na preventiva',resp='Mecânico',
          pa=[{'k':'act','t':'Vincular à OM-0234','fn':'vinc:c4'},Pt.br(),Pt.act('Triar achado','Triado: criticidade Média · reparo entra na preventiva · condição Apto mantida')],
          pb=[Pt.link('Ver OM-0234','MA-04.dc.html')]),
     dict(id='c5',caso='SM-0150',tipo='Solicitação',om='',ativo='Colhedora · S680',sint='Ruído intermitente no elevador',
          crit='Baixa',cont=3107,evid='áudio do operador',rec='A definir na triagem',resp='PCM',
          pa=[Pt.act('Triar solicitação','Triada: criticidade Baixa · inspeção na próxima parada · colhedora segue Apta'),Pt.br(),Pt.cta('Criar ordem','MA-04.dc.html')]),
     dict(id='c6',caso='NC-0912',tipo='Checklist do operador',om='',ativo='Plantadeira 24 linhas',sint='Disco de corte com desgaste',
          crit='Média',cont=886,evid='foto',rec='Apto com troca programada',resp='PCM',pa=[Pt.cta('Criar ordem','MA-04.dc.html')]),
    ]
    rows=[dict(id=c['id'],v={k:c[k] for k in ('caso','tipo','om','ativo','sint','crit','cont','evid','rec','resp')},s={},p={},pa=c['pa'],pb=c.get('pb')) for c in CS]
    ATV=[D.OM['ativo'],D.OM['substituto'],'Pulverizador · Uniport 3030','Plantadeira 24 linhas','Colhedora · S680','Bomba do Pivô 2','Packing linha 1','Silo e secador 1']
    REC=['Bloqueado','Restrito · monitorado','Apto · reparo na preventiva','Apto com troca programada','A definir na triagem']
    g_cs=grid([dict(k='caso',l='Caso',w=130),dict(k='ativo',l='Ativo',w=120),dict(k='sint',l='Sintoma / achado',w=210),
               dict(k='crit',l='Criticidade',chips={'Alta':'red','Média':'yellow','Baixa':'gray'}),dict(k='ce',l='Contador · evidência',w=120),
               dict(k='rr',l='Condição recomendada · responsável',w=165),dict(k='acao',l='Ação',w=150)],rows,
       edit=dict(m='form',title='Caso',newTitle='Registrar inspeção (checklist)',
            sub='Ajuste o achado, a criticidade e a condição recomendada. Sintoma repetido agrega ao caso; não crie ordem nova por alerta idêntico.',
            fields=[dict(k='ativo',l='Ativo',t='sel',opts=['']+ATV,req=True,help='Escolha o ativo inspecionado.'),
                    dict(k='tipo',l='Origem',t='sel',opts=['Checklist do operador','Checklist da manutenção','Solicitação','Falha em campo','Alerta agregado'],req=True,**{'def':'Checklist do operador'}),
                    dict(k='sint',l='Sintoma / achado',t='area',req=True),
                    dict(k='crit',l='Criticidade',t='sel',opts=['Alta','Média','Baixa'],req=True,**{'def':'Média'}),
                    dict(k='cont',l='Contador',t='num',u='h',min=0),dict(k='evid',l='Evidência',t='txt',req=True,help='Foto, áudio, telemetria ou checklist.'),
                    dict(k='rec',l='Condição recomendada',t='sel',opts=REC,req=True,**{'def':'A definir na triagem'}),
                    dict(k='resp',l='Responsável',t='sel',opts=['PCM','Mecânico','Zé (mecânico)','Equipe elétrica'],req=True,**{'def':'PCM'})]),
       gid='g_cs',total=False)
    PA=[('Hidráulico',4,3,18.5,46,46,['SM-0147 e INSP-105 · Trator T1 · 14,0 h','INSP-104 · MF 7719 · 0,5 h','SM-0152 / OM-0228 · Bomba do Pivô 2 (3 alertas agregados num caso) · 4,0 h']),
        ('Rodado / rolamentos',2,2,14.0,35,81,['OM-0221 · Colhedora S680 · rolamento · 14,0 h','NC-0912 · Plantadeira · disco · 0 h (sem parada)']),
        ('Elétrico / sensores',2,2,6.0,15,96,['OB-0104 · Packing linha 1 · sensor da esteira · 4,0 h','Sensores do pulverizador · 2,0 h']),
        ('Outros',2,2,1.5,4,100,['Pequenos ajustes · 1,5 h'])]
    g_pa=grid([dict(k='item',l='Item/sistema',w=220),dict(k='ach',l='Achados',t='num',a='r'),dict(k='atv',l='Ativos afetados',t='num',a='r'),
               dict(k='hp',l='Horas paradas',t='num',a='r',u='h',d=1),dict(k='pct',l='% das horas paradas',t='num',a='r',u='%'),dict(k='acum',l='Acumulado',t='num',a='r',u='%')],
       [dict(id=f'p{i}',v=dict(item=it,ach=a,atv=n,hp=hp,pct=pc,acum=ac),s={},p={},o=[dict(t=x) for x in orig]+[dict(t='Base: 40,0 h paradas em 30 d')]) for i,(it,a,n,hp,pc,ac,orig) in enumerate(PA)],
       edit=dict(m='origin',title='Não conformidades',fields=[dict(k='item',l='Item/sistema',ro=True),dict(k='hp',l='Horas paradas',t='num',u='h',ro=True)]),
       search=False,gid='g_pa',total=False,so=dict(k='hp',d=True))
    g_ct=grid([dict(k='os',l='Ordem de campo',w=230),dict(k='ef',l='Efeito'),dict(k='tr',l='Tratamento',w=320),dict(k='ab',l='Abrir')],
       [dict(id='o1',v=dict(os=f'OS-0420 · {OS420["tipo"]} · {OS420["talhao"]} · {OS420["area"]} ha',tr=f'{OS420["realizado"]} ha feitos preservados · {D.OM["substituto"]}: {SUBST}'),s={},
             p=dict(os=[Pt.b('OS-0420'),Pt.br(),Pt.mut(f'{OS420["tipo"]} · {OS420["talhao"]} · {OS420["area"]} ha')],ef=[Pt.chip('Impedida · ativo bloqueado','red')],ab=[Pt.link('Abrir O.S.','OS.dc.html')])),
        dict(id='o2',v=dict(os=f'OS-0431 · {OS431["tipo"]} · {OS431["talhao"]} · {OS431["area"]} ha',tr='Bloqueio executado antes do 1º início (INSP-105) · substituição a propor em Planeje a manutenção'),s={},
             p=dict(os=[Pt.b('OS-0431'),Pt.br(),Pt.mut(f'{OS431["tipo"]} · {OS431["talhao"]} · {OS431["area"]} ha')],ef=[Pt.chip('Retirada de Liberadas → A liberar','red')],ab=[Pt.link('Ver impedimento','PL-05det.dc.html')]))],
       edit=dict(m='ro',title='Ordem afetada',fields=[dict(k='os',l='Ordem',ro=True),dict(k='tr',l='Tratamento',ro=True)]),search=False,gid='g_ct',total=False)
    corpo=(kpis([('ABERTAS',H('k_ab'),'fila por risco e prazo'),('ALTA CRITICIDADE',H('k_alta'),'resposta imediata'),
                 ('BLOQUEIO OU RESTRIÇÃO',H('k_br'),'recomendado ou em vigor'),('SEM ORDEM',H('k_so'),'aguardam triagem ou vínculo')])
      + section('Fila de falhas, alertas e inspeções','Trie cada caso e vincule a uma ordem; clique no caso para ajustar criticidade e condição recomendada.',
          [sbtn('Registrar inspeção','g_cs_new','doc','Registrar achado de checklist com criticidade e evidência'),
           idrw('Bloquear ativo',dict(title='Bloquear ativo',
             sub='Ato técnico com motivo e responsável; as ordens de campo que usam o ativo ficam impedidas e o PCP é avisado.',
             fields=[('Ativo','Colhedora · S680'),('Motivo','Ruído no elevador com risco de quebra'),('Responsável técnico','Zé (mecânico)'),('Caso de origem','SM-0150')],
             confirm='Bloquear ativo',done='Colhedora bloqueada · nenhuma ordem de campo afetada hoje · PCP avisado (simulado)'),'alert','Bloquear ativo com motivo e responsável técnico')],g_cs)
      + section('Contingência do bloqueio','Acompanhe as ordens de campo que o bloqueio do Trator T1 deixou impedidas.','',g_ct,state='red')
      + section('Não conformidades por item (Pareto 30 d)','Priorize a resposta pelo item que mais parou máquina; clique no item para ver os achados.','',g_pa,state='yellow'))
    EXTRAJS[0]=JSBASE+r'''
function PREVALS(self,v){ const rows=ma_R(self,'g_cs'); let alta=0,br=0,so=0;
  rows.forEach(r=>{ const x=r.v; if(!r.pa) r.pa=[{k:'cta',t:'Criar ordem',h:'MA-04.dc.html'}];
    r.p.caso=[{k:'b',t:x.caso},{k:'br',t:''},{k:'mut',t:(x.tipo||'').toLowerCase()+(x.om?' · caso '+x.om:'')}]; r.s.caso=x.caso+' '+x.tipo;
    r.p.acao=(x.om && r.pb)?r.pb:r.pa; r.s.acao='';
    r.p.ce=[{k:'txt',t:(x.cont!==''&&x.cont!==undefined&&x.cont!==null)?ma_nf(x.cont)+' h':'—'},{k:'br',t:''},{k:'mut',t:x.evid||'—'}]; r.s.ce=x.evid||'';
    const rc=(x.rec==='Bloqueado')?'red':(String(x.rec).indexOf('Restrito')===0?'yellow':null);
    r.p.rr=[rc?ma_chip(x.rec,rc):{k:'txt',t:x.rec},{k:'br',t:''},{k:'mut',t:x.resp}]; r.s.rr=x.rec+' '+x.resp;
    r.p.crit=[ma_chip(x.crit,x.crit==='Alta'?'red':(x.crit==='Média'?'yellow':'gray'))]; r.s.crit=x.crit;
    if(x.crit==='Alta') alta++; if(x.rec==='Bloqueado'||String(x.rec).indexOf('Restrito')===0) br++; if(!x.om) so++; });
  v.k_ab=String(rows.length); v.k_alta=String(alta); v.k_br=String(br); v.k_so=String(so); }
function EXTRAVALS(self,v){
  v.vinc=(id)=>{ const r=ma_R(self,'g_cs').find(x=>x.id===id); if(!r||r.v.om) return; r.v.om='OM-0234';
    self.setState({g2toast:'Achado '+r.v.caso+' vinculado à OM-0234 (preventiva do MF 7719) · nenhuma ordem nova criada'}); };
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_cs'||!r) return;
    if(!r.v.caso){ const n=rows.filter(x=>String(x.v.caso||'').indexOf('NC-')===0).length; r.v.caso='NC-'+String(912+n).padStart(4,'0'); r.v.om='';
      self.setState({g2toast:'Achado '+r.v.caso+' registrado · entrou na fila por risco · crie ou vincule uma ordem'}); }
    else self.setState({g2toast:'Caso '+r.v.caso+' salvo · fila reordenada por risco'}); }; }
'''
    shell37('MA-02','Solicitações e inspeções',corpo,
      subtitle='Triagem única de falhas, alertas e checklists — cada achado nasce vinculado à ocorrência de origem.',
      status=('3 de alta criticidade','red'),primary='Criar ordem de manutenção',primary_href='MA-04.dc.html',steps=faixa(2),
      footer='Bloquear ativo é ato técnico com motivo e responsável; alertas idênticos agregam ao caso, nunca duplicam ordem.')

# =====================================================================================
def ma03():
    fn='MA-03.dc.html'; HEIGHTS37[fn]=1000
    PL=[
     dict(id='t1',mod='JD 6M 155',atv='Trator T1',serv='Revisão 250 h',fonte='Fabricante · 250 h',cont='4.312 h',venc=('Suspenso · T1 bloqueado','red'),
          jan='após liberação técnica',pecas='kit filtros + óleo 18 L',lk=('Abrir ordem','MA-04det.dc.html',False)),
     dict(id='mf',mod='MF 7719',atv='Trator 02',serv='Revisão 250 h',fonte='Fabricante · 250 h',cont='2.988 h · última revisão 2.793 h',venc=('28/09 · 3.043 h (11 h/dia)',''),
          jan='28/09',pecas='kit filtros + óleo 16 L',lk=('Ver conflito','PL-05.dc.html',True)),
     dict(id='pu',mod='Uniport 3030',atv='Pulverizador',serv='Troca do óleo hidráulico',fonte='Condição · análise de óleo',cont='1.542 h',venc=('aguardando laudo (coleta 21/09)',''),
          jan='—',pecas='óleo 40 L + análise',lk=('Abrir ficha','CD-03.dc.html',False)),
     dict(id='bo',mod='Bomba do Pivô 2',atv='irrigação',serv='Preventiva elétrica + vedação',fonte='Calendário · mensal',cont='8.914 h',venc=('01/10',''),
          jan='01/10 (pivô parado)',pecas='kit vedação · eletricista',lk=('Ver agenda','PL-04.dc.html',False)),
     dict(id='pl',mod='Plantadeira 24 linhas',atv='implemento',serv='Revisão pré-plantio',fonte='Calendário · antes da safra',cont='886 h',venc=('Vencida 20/09','red'),
          jan='25/09',pecas='discos + graxa',lk=('Ver agenda','PL-04.dc.html',False)),
    ]
    rows=[dict(id=x['id'],v=dict(mod=x['mod'],atv=x['atv'],serv=x['serv'],fonte=x['fonte'],cont=x['cont'],venc=x['venc'][0],vc=x['venc'][1],jan=x['jan'],pecas=x['pecas'],
                               lkt=x['lk'][0],lkh=x['lk'][1],lku=x['lk'][2]),s={},p={}) for x in PL]
    g_pl=grid([dict(k='mod',l='Modelo / ativo',w=150),dict(k='serv',l='Serviço · fonte e intervalo',w=190),dict(k='venc',l='Contador · vencimento projetado',w=200),
               dict(k='jan',l='Janela sugerida',w=150),dict(k='pecas',l='Peças e recursos',w=150),dict(k='acao',l='Ação')],rows,
       edit=dict(m='form',title='Versão do plano',sub='Salvar gera nova versão e recalcula a previsão. Antecipação e extensão seguem fabricante, criticidade e política validada — sem percentual fixo.',
            fields=[dict(k='serv',l='Serviço',t='txt',req=True),dict(k='fonte',l='Fonte · intervalo',t='txt',req=True,help='Ex.: Fabricante · 250 h; Calendário · mensal; Condição · análise de óleo.'),
                    dict(k='cont',l='Contador',t='txt',ro=True),dict(k='venc',l='Vencimento projetado',t='txt',ro=True,help='Calculado pela carga projetada do PCP.'),
                    dict(k='jan',l='Janela preferida',t='txt',req=True),dict(k='pecas',l='Peças e recursos',t='txt',req=True)]),
       gid='g_pl',total=False)
    g_mi=grid([dict(k='man',l='Manutenção',w=240),dict(k='jan',l='Janela',w=180),dict(k='prod',l='Produção afetada',w=260),dict(k='sit',l='Situação',w=280),dict(k='ab',l='Abrir')],[],
       edit=dict(m='ro',title='Manutenção × produção',fields=[dict(k='man',l='Manutenção',ro=True),dict(k='jan',l='Janela',ro=True),dict(k='prod',l='Produção afetada',ro=True)]),
       search=False,gid='g_mi',total=False)
    corpo=(kpis([('VENCIDAS','1','plantadeira'),('VENCEM EM 10 DIAS','2','carga do PCP'),
                 ('PARADAS PROPOSTAS','3','a confirmar'),('CONFLITOS COM A PRODUÇÃO',H('k_conf'),H('k_confd'))])
      + section('Previsão de paradas','Confira o vencimento projetado pela carga do PCP; clique na linha para editar a versão do plano.',
          [imsg('Simular paradas','Simulação: 3 paradas propostas (Plantadeira 25/09, MF 7719 28/09, Bomba 01/10) · nenhuma reserva firme criada','calc','Simular paradas sem reservar agenda'),
           imsg('Revisar impacto','Impacto: MF 7719 em 28/09 conflita com a OS-0420 (substituto proposto do T1) · demais paradas sem conflito','alert','Revisar o impacto das paradas na produção'),
           ilnk('Gerar ordens em rascunho','MA-04.dc.html','doc','Abrir as ordens em rascunho (A liberar)')],g_pl)
      + section('Manutenções e impacto na produção','Simule a janela da parada e proponha substituição; os conflitos seguem para o PCP em Impedimentos.',
          [sbtn('Simular janela','mi_sim','calendar','Simular outra janela para a preventiva do MF 7719, sem reservar agenda'),
           sbtn('Propor substituição','mi_prop','truck','Registrar proposta de substituto para as ordens afetadas pelo Trator T1'),
           f'<sc-if value="{H("mi_link")}" hint-placeholder-val="{F()}">{ilnk("Abrir impedimentos","PL-05.dc.html","alert","Abrir Impedimentos e reprogramação (PCP)")}</sc-if>'],g_mi,state='red')
      + section('Rascunhos e pendências','Resolva o conflito antes de liberar; a revisão vencida continua listada até ser feita.','',
          f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.6;"><b style="color: {INK};">OM-0234</b> (MF 7719 · revisão 250 h) está em rascunho com janela 28/09 em conflito — só será liberada depois de resolvido o conflito. '
          f'Confirmar paradas gera ordens em A liberar; liberar é ação separada.</div>',state='yellow'))
    EXTRAJS[0]=JSBASE+r'''
function PREVALS(self,v){ const sim=!!self.state.mi_sim, prop=!!self.state.mi_prop; const L=(t,h)=>({k:'link',t:t,h:h});
  const mfr=ma_R(self,'g_pl').find(r=>r.id==='mf'); const mfJan=mfr?String(mfr.v.jan):'28/09'; const mfConf=(mfJan.indexOf('28/09')>=0)&&!sim;
  ma_R(self,'g_pl').forEach(r=>{ const x=r.v;
    r.p.mod=[{k:'b',t:x.mod},{k:'br',t:''},{k:'mut',t:x.atv}]; r.s.mod=x.mod+' '+x.atv;
    r.p.serv=[{k:'txt',t:x.serv},{k:'br',t:''},{k:'mut',t:x.fonte}]; r.s.serv=x.serv+' '+x.fonte;
    r.p.venc=[{k:'mut',t:x.cont},{k:'br',t:''},x.vc?ma_chip(x.venc,x.vc):{k:'txt',t:x.venc}]; r.s.venc=x.venc;
    const conf=(r.id==='mf' && mfConf);
    r.p.jan=conf?[{k:'txt',t:x.jan},{k:'br',t:''},ma_chip('Conflito · OS-0420','red')]:((r.id==='mf'&&sim&&mfJan.indexOf('28/09')>=0)?[{k:'txt',t:x.jan},{k:'br',t:''},ma_chip('Simulada 29–30/09','yellow')]:[{k:'txt',t:x.jan}]); r.s.jan=x.jan;
    r.p.acao=[{k:'cta',t:(r.id==='mf'&&!conf)?'Ver agenda':x.lkt,h:(r.id==='mf'&&!conf)?'PL-04.dc.html':x.lkh,u:conf&&x.lku}]; r.s.acao=''; });
  ma_G('g_mi').rows=[
   {id:'m1',v:{man:'Corretiva OM-0233 · Trator T1',jan:'até teste aprovado',prod:'OS-0420 saldo 70 ha · OS-0431 102 ha'},s:{},
    p:{man:[{k:'b',t:'Corretiva OM-0233'},{k:'br',t:''},{k:'mut',t:'Trator T1 · retorno previsto 24/09 12:00'}],prod:[{k:'txt',t:'OS-0420 saldo 70 ha'},{k:'br',t:''},{k:'txt',t:'OS-0431 · plantio T2 · 102 ha'}],
       sit:prop?[ma_chip('Proposto · MF 7719 para as duas · aguarda PCP','yellow'),{k:'br',t:''},{k:'mut',t:'conflito com a preventiva de 28/09 enviado a Impedimentos'}]
               :[ma_chip('OS-0420: Proposto · saldo 70 ha · aguarda PCP','yellow'),{k:'br',t:''},ma_chip('OS-0431: sem substituto','red')],
       ab:[L('Abrir ordem','MA-04det.dc.html')]}},
   {id:'m2',v:{man:'Preventiva 250 h · MF 7719 (OM-0234)',jan:sim?'29–30/09 (simulada)':mfJan,prod:'OS-0420 saldo · substituto até 28/09'},s:{},
    p:{man:[{k:'b',t:'Preventiva 250 h · OM-0234'},{k:'br',t:''},{k:'mut',t:'Trator 02 · MF 7719'}],
       sit:mfConf?[ma_chip('Conflito · OS-0420','red')]:[ma_chip(sim?'Sem conflito na simulação':'Sem conflito','green'),{k:'br',t:''},{k:'mut',t:'confirme a parada para gerar a reserva'}],
       ab:[L('Ver conflito','PL-05.dc.html')]}},
   {id:'m3',v:{man:'Revisão pré-plantio · Plantadeira 24 linhas',jan:'25/09',prod:'nenhuma ordem na janela'},s:{},p:{sit:[ma_chip('Sem conflito','green')],ab:[L('Ver agenda','PL-04.dc.html')]}},
   {id:'m4',v:{man:'Preventiva elétrica · Bomba do Pivô 2',jan:'01/10 (pivô parado)',prod:'OS-0419 termina 24/09 10:31'},s:{},p:{sit:[ma_chip('Sem conflito','green')],ab:[L('Ver agenda','PL-04.dc.html')]}}];
  const cf=[]; if(mfConf) cf.push('MF 7719 × OS-0420'); if(!prop) cf.push('OS-0431 sem substituto');
  v.k_conf=String(cf.length); v.k_confd=cf.join(' · ')||'propostas aguardam PCP'; }
function EXTRAVALS(self,v){ v.mi_link=!!self.state.mi_prop;
  v.mi_sim=()=>{ const st=self.state; self.setState({mi_sim:true,g2toast:st.mi_sim?'Janela já simulada: 29–30/09 para a preventiva do MF 7719 · sem conflito':'Janela simulada para a preventiva do MF 7719: 29–30/09 · sem conflito com a OS-0420 · proposta, nenhuma reserva firme'}); };
  v.mi_prop=()=>{ const st=self.state; self.setState({mi_prop:true,g2toast:st.mi_prop?'Proposta já registrada · aguarda PCP em Impedimentos e reprogramação':'Proposta registrada: Trator 02 · MF 7719 para OS-0431 (24/09) e saldo da OS-0420 · aguarda PCP · conflitos enviados a Impedimentos e reprogramação (simulado)'}); };
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_pl'||!r) return;
    if(r.id==='mf'){ if(String(r.v.jan).indexOf('28/09')>=0){ self.setState({g2toast:'Nova versão salva · janela 28/09 continua em conflito com a OS-0420'}); }
      else self.setState({g2toast:'Nova versão salva · janela '+r.v.jan+' fora da OS-0420 · previsão recalculada'}); return; }
    self.setState({g2toast:'Nova versão do plano salva · previsão recalculada pela carga do PCP'}); }; }
'''
    shell37('MA-03','Plano de manutenção',corpo,
      subtitle='Biblioteca por modelo e plano aplicado por ativo — previsão por horas, tempo e condição, integrada à janela do PCP.',
      status=('1 vencida · 2 conflitos','red'),primary='Confirmar 2 paradas',steps=faixa(3),
      footer='Simular abre proposta; confirmar paradas compromete a agenda; antecipação e extensão seguem fabricante, criticidade e política — sem percentual universal.')

# =====================================================================================
OMS=[  # ordens de manutenção — 5 etapas canônicas; condições viram selo
 dict(id='OM-0233',ativo=D.OM['ativo'],serv='Corretiva · pressão hidráulica',crit='Alta',jan='hoje',ret='24/09 12:00',etapa='Em execução',
      tec='Zé (mecânico)',horas='6,5 h',tar='3 de 4 · falta teste',pecas='bomba hidr. 1 un · mangueira 2 un',teste='Reprovado 09:00',testec='red',
      cond='Bloqueado',condc='red',selo='Ativo bloqueado'),
 dict(id='OM-0234',ativo=D.OM['substituto'],serv='Preventiva 250 h (do plano)',crit='Média',jan='28/09',ret='28/09 17:00',etapa='A liberar',
      tec='—',horas='—',tar='0 de 5',pecas='kit filtros + óleo 16 L (a reservar)',teste='',testec='',cond='Apto',condc='green',selo='Janela em conflito'),
 dict(id='OM-0228',ativo='Bomba do Pivô 2',serv='Inspeção corretiva · pressão baixa',crit='Alta',jan='hoje 14:00',ret='hoje 17:00',etapa='Liberadas',
      tec='Equipe elétrica',horas='—',tar='0 de 3',pecas='—',teste='',testec='',cond='Restrito · monitorado',condc='yellow',selo=''),
 dict(id='OM-0230',ativo='Pulverizador · Uniport 3030',serv='Preventiva 500 h',crit='Média',jan='20/09',ret='liberado 21/09',etapa='Em conferência',
      tec='Zé (mecânico)',horas='9,0 h',tar='6 de 6',pecas='2 filtros não usados',teste='Aprovado',testec='green',cond='Apto',condc='green',selo='Sobras a resolver'),
 dict(id='OM-0221',ativo='Colhedora · S680',serv='Corretiva · rolamento',crit='Média',jan='12/09',ret='liberado 13/09',etapa='Encerradas',
      tec='Terceiro (Agrícola Center)',horas='14,0 h',tar='4 de 4',pecas='rolamento 2 un',teste='Aprovado',testec='green',cond='Apto',condc='green',selo=''),
]
def ma04():
    fn='MA-04.dc.html'; HEIGHTS37[fn]=1000
    rows=[dict(id=o['id'],ro=(o['etapa']=='Encerradas'),v={k:o[k] for k in o if k!='id'}|{'om':o['id']},s={},p={}) for o in OMS]
    hist=Pt.act('Ver histórico','OM-0221 encerrada em 13/09 · custo R$ 3,8 mil (preços de demonstração) · rolamento antigo sucateado com responsável')
    g_om=grid([dict(k='om',l='Ordem · ativo',w=130),dict(k='serv',l='Serviço · criticidade',w=150),dict(k='jan',l='Janela · retorno',w=115),dict(k='etapa',l='Etapa · selo',w=150),
               dict(k='tec',l='Equipe · tarefas · peças',w=150),dict(k='cond',l='Teste · condição do ativo',w=160),dict(k='acao',l='Ação',w=130)],rows,
       edit=dict(m='form',title='Ordem',sub='Ajuste janela, retorno previsto, equipe e criticidade. A etapa avança pelas ações da ordem, nunca pela edição.',
            fields=[dict(k='crit',l='Criticidade',t='sel',opts=['Alta','Média','Baixa'],req=True),dict(k='jan',l='Janela',t='txt',req=True),
                    dict(k='ret',l='Previsão de retorno',t='txt',req=True),
                    dict(k='tec',l='Equipe',t='sel',opts=['—','Zé (mecânico)','Rui','Equipe elétrica','Terceiro (Agrícola Center)'],req=True),
                    dict(k='etapa',l='Etapa',t='txt',ro=True)]),
       gid='g_om',total=False)
    corpo=(kpis([('A LIBERAR',H('k_al'),H('k_ald')),('EM EXECUÇÃO',H('k_ex'),H('k_exd')),('EM CONFERÊNCIA',H('k_co'),H('k_cod')),
                 ('RETORNO DO TRATOR T1','24/09 12:00','se o teste for aprovado')])
      + section('Ordens de manutenção','Acompanhe cada ordem pelas cinco etapas; clique na linha para ajustar janela, equipe e criticidade.',
          [imsg('Liberar serviço','Nenhuma ordem liberada: OM-0234 tem janela em conflito com a OS-0420 — simule outra janela em Planeje a manutenção e libere de novo',
                'check','Liberar para a oficina as ordens autorizadas e sem conflito')],g_om))
    EXTRAJS[0]=JSBASE+'const MA_HIST='+json.dumps(hist,ensure_ascii=False)+';\n'+r'''
const MA_ETC={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray'};
function PREVALS(self,v){ const rows=ma_R(self,'g_om'); const n={}; const ids={};
  rows.forEach(r=>{ const x=r.v; n[x.etapa]=(n[x.etapa]||0)+1; (ids[x.etapa]=ids[x.etapa]||[]).push(r.id);
    r.p.om=[{k:'b',t:r.id},{k:'br',t:''},{k:'mut',t:x.ativo}]; r.s.om=r.id+' '+x.ativo;
    r.p.serv=[{k:'txt',t:x.serv},{k:'br',t:''},ma_chip(x.crit,x.crit==='Alta'?'red':(x.crit==='Média'?'yellow':'gray'))]; r.s.serv=x.serv;
    r.p.jan=[{k:'txt',t:x.jan},{k:'br',t:''},{k:'mut',t:(String(x.ret).indexOf('liberado')===0?x.ret:'retorno '+x.ret)}]; r.s.jan=x.jan;
    r.p.etapa=[ma_chip(x.etapa,MA_ETC[x.etapa]||'gray')].concat(x.selo?[{k:'br',t:''},ma_chip(x.selo,/bloque|conflito/i.test(x.selo)?'red':'yellow')]:[]); r.s.etapa=x.etapa+(x.selo?' · '+x.selo:'');
    r.p.tec=[{k:'txt',t:x.tec+(x.horas&&x.horas!=='—'?' · '+x.horas:'')},{k:'br',t:''},{k:'mut',t:'tarefas '+x.tar},{k:'br',t:''},{k:'mut',t:x.pecas}]; r.s.tec=x.tec;
    r.p.cond=(x.teste?[ma_chip(x.teste,x.testec),{k:'br',t:''}]:[]).concat([ma_chip(x.cond,x.condc)]); r.s.cond=x.cond;
    let a;
    if(r.id==='OM-0233') a=[{k:'cta',t:'Abrir ordem',h:'MA-04det.dc.html',u:true}];
    else if(r.id==='OM-0234') a=[{k:'cta',t:'Ver conflito',h:'PL-05.dc.html'}];
    else if(x.etapa==='Liberadas') a=[{k:'act',t:'Iniciar serviço',fn:'ini:'+r.id}];
    else if(x.etapa==='Em conferência' && x.selo) a=[{k:'act',t:'Resolver sobras',fn:'sob:'+r.id}];
    else if(x.etapa==='Em conferência') a=[{k:'act',t:'Encerrar ordem',fn:'enc:'+r.id}];
    else if(x.etapa==='Encerradas') a=[MA_HIST];
    else a=[{k:'mut',t:'em execução · aponte no app da oficina'}];
    r.p.acao=a; r.s.acao=''; });
  const L=(e)=>(ids[e]||[]).join(' · ')||'nenhuma';
  v.k_al=String(n['A liberar']||0); v.k_ald=L('A liberar'); v.k_ex=String(n['Em execução']||0); v.k_exd=L('Em execução');
  v.k_co=String(n['Em conferência']||0); v.k_cod=L('Em conferência'); }
function EXTRAVALS(self,v){ const find=(id)=>ma_R(self,'g_om').find(r=>r.id===id);
  v.ini=(id)=>{ const r=find(id); if(!r||r.v.etapa!=='Liberadas') return; r.v.etapa='Em execução'; r.v.tar='0 de 3 · em andamento';
    self.setState({g2toast:id+' Em execução · '+r.v.tec+' apontando · '+r.v.ativo.split(' · ')[0]+' segue '+r.v.cond.toLowerCase()+' até o teste'}); };
  v.sob=(id)=>{ const r=find(id); if(!r) return; r.v.selo=''; r.v.pecas='2 filtros devolvidos · recibo AL-0412';
    self.setState({g2toast:'Sobras da '+id+' devolvidas ao Almoxarifado Sede com recibo · ordem elegível para encerrar'}); };
  v.enc=(id)=>{ const r=find(id); if(!r) return; r.v.etapa='Encerradas'; r.ro=true;
    self.setState({g2toast:id+' encerrada · custo fechado na safra 2026/27 · aptidão do ativo já decidida à parte'}); }; }
'''
    shell37('MA-04','Ordens de manutenção',corpo,
      subtitle='Serviços, peças, terceiros e testes sobre o mesmo registro — A liberar → Liberadas → Em execução → Em conferência → Encerradas.',
      status=('1 bloqueio ativo','red'),primary='Planejar e autorizar ordem',steps=faixa(4),
      footer='Concluir serviço leva a Em conferência e não libera o ativo; teste e aptidão são decisões técnicas separadas do encerramento de custo.')

# =====================================================================================
def ma04det():
    fn='MA-04det.dc.html'; HEIGHTS37[fn]=1000; PARENT37[fn]='MA-04.dc.html'
    g_ib=grid([dict(k='obj',l='Objeto afetado',w=170),dict(k='ef',l='Efeito',w=230),dict(k='tr',l='Tratamento',w=260),dict(k='sit',l='Situação',w=210),dict(k='ab',l='Abrir')],[],
       edit=dict(m='ro',title='Impacto do bloqueio',fields=[dict(k='obj',l='Objeto',ro=True),dict(k='tr',l='Tratamento',ro=True)]),search=False,gid='g_ib',total=False)
    TK=[('k1','Substituir bomba hidráulica','Concluída',4.0,'bomba hidr. 1 un'),('k2','Trocar mangueiras de alta pressão','Concluída',1.5,'mangueira 2 un'),
        ('k3','Reaperto e sangria do circuito','Concluída',1.0,'—')]
    g_tk=grid([dict(k='tarefa',l='Tarefa',w=260),dict(k='sit',l='Situação',chips={'Concluída':'green','Em andamento':'yellow','Refazer':'red','Pendente':'gray'}),
               dict(k='horas',l='Horas',t='num',a='r',u='h',d=1,agg='sum'),dict(k='pecas',l='Peças aplicadas',w=200)],
       [dict(id=i,v=dict(tarefa=t,sit=s,horas=h,pecas=pc),s={},p={}) for i,t,s,h,pc in TK],
       edit=dict(m='form',title='Tarefa',sub='Aponte situação, horas e peças. Apontar não conclui a ordem; o teste é registrado em Teste e aptidão.',
            fields=[dict(k='sit',l='Situação',t='sel',opts=['Pendente','Em andamento','Concluída','Refazer'],req=True),
                    dict(k='horas',l='Horas',t='num',u='h',min=0,max=24,req=True),dict(k='pecas',l='Peças aplicadas',t='txt')]),
       search=False,gid='g_tk',total=True)
    g_te=grid([dict(k='teste',l='Teste',w=230),dict(k='quando',l='Quando'),dict(k='res',l='Resultado'),dict(k='ef',l='Efeito',w=340)],[],
       edit=dict(m='ro',title='Teste',fields=[dict(k='teste',l='Teste',ro=True),dict(k='quando',l='Quando',ro=True),dict(k='ef',l='Efeito',ro=True)]),search=False,gid='g_te',total=False)
    g_sb=grid([dict(k='item',l='Item',w=260),dict(k='dest',l='Destinação',chips={'A definir':'red'},w=230),dict(k='resp',l='Responsável')],
       [dict(id='s1',v=dict(item='Bomba hidráulica usada (recuperável)',dest='A definir',resp='Almoxarifado Sede'),s={},p=dict(dest=[Pt.chip('A definir','red')])),
        dict(id='s2',v=dict(item='Mangueiras usadas · 2 un',dest='Sucatear com responsável',resp='Almoxarifado Sede'),s={},p={})],
       edit=dict(m='form',title='Destinar sobra',sub='Peça recuperável não vira sucata sem registro; toda destinação tem responsável.',
            fields=[dict(k='item',l='Item',t='txt',ro=True),
                    dict(k='dest',l='Destinação',t='sel',opts=['A definir','Enviar para recondicionamento','Devolver ao almoxarifado','Sucatear com responsável'],req=True),
                    dict(k='resp',l='Responsável',t='sel',opts=['Almoxarifado Sede','Zé (mecânico)','PCM'],req=True)]),
       search=False,gid='g_sb',total=False)
    stp=lambda now,hint: stepper([(e,('done' if i<now else ('now' if i==now else 'todo'))) for i,e in enumerate(['A liberar','Liberadas','Em execução','Em conferência','Encerradas'])],hint)
    corpo=(continuity('SM-0147 falha em campo · INSP-105 bloqueio',H('c_aqui'),H('c_falta'),H('c_prox'))
      + f'<sc-if value="{H("stp2")}" hint-placeholder-val="{H("true")}">'+stp(2,'Corretiva autorizada pela manutenção · término físico leva a Em conferência; encerrar custo ≠ liberar ativo.')+'</sc-if>'
      + f'<sc-if value="{H("stp3")}" hint-placeholder-val="{F()}">'+stp(3,'Serviço concluído · resolva as sobras e encerre o custo; a aptidão do ativo é decisão à parte.')+'</sc-if>'
      + f'<sc-if value="{H("stp4")}" hint-placeholder-val="{F()}">'+stp(4,'Ordem encerrada · custo fechado na safra; o ativo volta pela fila de reprogramação.')+'</sc-if>'
      + section('Impacto do bloqueio','Confira as ordens de campo impedidas e como cada uma será tratada.','',g_ib,state='red')
      + section('Execução na oficina','Aponte tarefas, horas e peças; clique na tarefa para atualizar.',
          [imsg('Registrar avanço e peças','Avanço registrado · mangueira 2 un baixadas da requisição · bomba antiga marcada como recuperável','wrench','Registrar avanço e baixar peças da requisição'),
           imsg('Finalizar apontamento do turno','Turno de Zé fechado · a ordem continua Em execução — finalizar o turno nunca conclui a ordem','clock','Fechar o turno do mecânico sem concluir a ordem')],g_tk)
      + section('Teste e aptidão','Registre o teste do reparo e, com teste aprovado, defina a aptidão do ativo.',
          [sbtn('Registrar teste do reparo','t_reg','check','Registrar a 2ª tentativa do teste de pressão em carga'),
           sbtn('Definir aptidão do ativo','t_apt','check','Decidir a aptidão do Trator T1 (exige teste aprovado)'),
           sbtn('Concluir serviço','t_con','wrench','Levar a ordem a Em conferência (exige teste aprovado)')],g_te,state='yellow')
      + section('Sobras e encerramento','Dê destino às sobras e encerre o custo quando o serviço estiver em conferência.',
          [sbtn('Encerrar ordem','t_enc','doc','Encerrar o custo da ordem (exige serviço concluído e sobras destinadas)')],
          g_sb+f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.6; padding-top: 10px;">{H("custo")}</div>'))
    prim=(f'<span style="{H("st_st")}">{H("st_t")}</span>'
          f'<sc-if value="{H("prim_btn")}" hint-placeholder-val="{H("true")}"><button type="button" onClick="{H("prim_fn")}" style="{BTN_ST(True)}">{H("prim_t")}</button></sc-if>'
          f'<sc-if value="{H("prim_lnk")}" hint-placeholder-val="{F()}"><a href="MA-04.dc.html" style="text-decoration: none; display: inline-block; {BTN_ST(True)}">Voltar às ordens</a></sc-if>')
    EXTRAJS[0]=JSBASE+'const MA_SAFRA='+json.dumps(D.SAFRA)+';\n'+r'''
function ma_st(self){ const s=self.state; return {t2:!!s.t2,apto:!!s.apto,con:!!s.con,enc:!!s.enc,sob:ma_R(self,'g_sb').every(r=>r.v.dest&&r.v.dest!=='A definir')}; }
function PREVALS(self,v){ const S=ma_st(self);
  // tarefa do teste acompanha o estado do teste
  const tk=ma_R(self,'g_tk'); let t4=tk.find(r=>r.id==='k4');
  if(!t4){ t4={id:'k4',v:{tarefa:'Teste de pressão em carga',sit:'Refazer',horas:0,pecas:'—'},s:{},p:{}}; tk.push(t4); }
  if(S.t2 && !t4.done){ t4.done=true; t4.v.sit='Concluída'; t4.v.horas=0.5; }
  tk.forEach(r=>{ if(r.id==='k4') return; const c=r.v.sit; r.p.sit=[ma_chip(c,{'Concluída':'green','Em andamento':'yellow','Refazer':'red'}[c]||'gray')]; r.s.sit=c; });
  t4.p.sit=(t4.v.sit==='Refazer')?[ma_chip('Refazer · reprovado 09:00','red')]:[ma_chip(t4.v.sit,t4.v.sit==='Concluída'?'green':(t4.v.sit==='Pendente'?'gray':'yellow'))].concat(S.t2?[{k:'mut',t:'aprovado 14:20'}]:[]); t4.s.sit=t4.v.sit;
  ma_G('g_te').rows=[
   {id:'e1',v:{teste:'Pressão em carga · 1ª tentativa',quando:'23/09 09:00',ef:'bloqueio mantido · retrabalho autorizado na própria ordem'},s:{res:'Reprovado'},p:{res:[ma_chip('Reprovado','red')]}},
   {id:'e2',v:{teste:'Pressão em carga · 2ª tentativa',quando:S.t2?'23/09 14:20':'a registrar',ef:S.t2?(S.apto?'aptidão definida · Trator T1 apto':'pressão dentro da faixa · decisão de aptidão habilitada'):'aprovado → habilita a decisão de aptidão'},
    s:{res:S.t2?'Aprovado':'Pendente'},p:{res:[S.t2?ma_chip('Aprovado','green'):ma_chip('Pendente','yellow')]}}];
  const L=(t,h)=>({k:'link',t:t,h:h});
  ma_G('g_ib').rows=[
   {id:'b1',v:{obj:'OS-0420 · plantio T4 · 100 ha',tr:'Substituto Trator 02 · MF 7719: Proposto · OS-0420 saldo 70 ha · aguarda PCP'},s:{},
    p:{obj:[{k:'b',t:'OS-0420'},{k:'br',t:''},{k:'mut',t:'Plantio · Soja 58 W · T4 · 100 ha'}],ef:[ma_chip('Impedida · ativo bloqueado','red')],
       sit:S.apto?[ma_chip('Impedimento removido','yellow'),{k:'br',t:''},{k:'mut',t:'saldo 70 ha aguarda reprogramação do PCP'}]:[{k:'txt',t:'30 ha feitos preservados · saldo 70 ha pausado'}],ab:[L('Abrir O.S.','OS.dc.html')]}},
   {id:'b2',v:{obj:'OS-0431 · plantio T2 · 102 ha',tr:'Bloqueio executado antes do 1º início (INSP-105) · substituição proposta em Planeje a manutenção'},s:{},
    p:{obj:[{k:'b',t:'OS-0431'},{k:'br',t:''},{k:'mut',t:'Plantio · Soja 58 W · T2 · 102 ha'}],ef:[ma_chip('Retirada de Liberadas → A liberar','red')],
       sit:S.apto?[ma_chip('Continua A liberar','yellow'),{k:'br',t:''},{k:'mut',t:'reprogramação pelo PCP'}]:[{k:'txt',t:'A liberar · aguarda ativo ou substituto'}],ab:[L('Ver impedimento','PL-05det.dc.html')]}},
   {id:'b3',v:{obj:'Agenda do Trator T1',tr:'Liberar o ativo não reassume a agenda antiga — volta pela fila de reprogramação'},s:{},
    p:{obj:[{k:'b',t:'Agenda do Trator T1'}],ef:[ma_chip(S.apto?'Apto':'Retirada',S.apto?'green':'gray')].concat(S.apto?[{k:'br',t:''},{k:'mut',t:'agenda antiga não reassumida'}]:[]),
       sit:[{k:'txt',t:S.apto?'na fila de reprogramação do PCP':'capacidade reduzida contada uma vez'}],ab:[L('Ver impedimentos','PL-05.dc.html')]}}]; }
function EXTRAVALS(self,v){ const S=ma_st(self); const T=(m,p)=>self.setState(Object.assign({g2toast:m},p||{}));
  const hrs=ma_R(self,'g_tk').reduce((a,r)=>a+(Number(r.v.horas)||0),0); const custo=4.1+hrs*0.32;
  v.custo='Custo até agora: R$ '+ma_nf(custo,1)+' mil na safra '+MA_SAFRA+' — peças R$ 4,1 mil · '+ma_nf(hrs,1)+' h de oficina a R$ 320/h (hipótese de custo-hora) · sem terceiros. Retrabalho fora do escopo criaria ordem vinculada, preservando esta.';
  const falta=[]; if(!S.t2) falta.push('teste aprovado'); if(!S.apto) falta.push('aptidão'); if(!S.con) falta.push('concluir serviço'); if(!S.sob) falta.push('sobras'); if(!S.enc && S.con && S.sob) falta.push('encerrar custo');
  v.c_aqui=S.enc?'Encerradas · custo fechado':(S.con?'Em conferência':'Em execução')+(S.apto?' · Trator T1 apto':' · Trator T1 bloqueado');
  v.c_falta=falta.join(' · ')||'nada';
  const nx=!S.t2?['Registrar teste do reparo','t_reg']:(!S.apto?['Definir aptidão do ativo','t_apt']:(!S.con?['Concluir serviço','t_con']:(!S.sob?['Resolver sobras','t_sob']:(!S.enc?['Encerrar ordem','t_enc']:null))));
  v.c_prox=nx?nx[0]:'Voltar às ordens'; v.prim_btn=!!nx; v.prim_lnk=!nx; v.prim_t=nx?nx[0]:''; v.prim_fn=()=>{ if(nx) v[nx[1]](); };
  v.stp2=!S.con; v.stp3=S.con&&!S.enc; v.stp4=S.enc;
  const st=S.enc?['Encerrada · ativo apto','green']:(S.apto?[(S.con?'Em conferência':'Em execução')+' · ativo apto','green']:[(S.con?'Em conferência':'Em execução')+' · bloqueio ativo','red']);
  const C={green:['#1E7A4C','#E4F3E9'],red:['#B42318','#FDE8E6']}[st[1]];
  v.st_t=st[0]; v.st_st='display:inline-flex;align-items:center;padding:4px 11px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;margin-right:6px;color:'+C[0]+';background:'+C[1]+';';
  v.t_reg=()=>{ if(self.state.t2){ T('2ª tentativa já registrada · aprovada às 14:20'); return; }
    T('Teste 2 registrado · pressão dentro da faixa · aprovado · decisão de aptidão habilitada',{t2:true}); };
  v.t_apt=()=>{ const s=self.state; if(!s.t2){ T('Indisponível agora: a aptidão exige teste aprovado — registre a 2ª tentativa do teste de pressão'); return; }
    if(s.apto){ T('Trator T1 já está apto · aguarda a fila de reprogramação do PCP'); return; }
    T('Trator T1 apto · liberação técnica registrada · agenda antiga não reassumida · volta pela fila de reprogramação',{apto:true}); };
  v.t_con=()=>{ const s=self.state; if(!s.t2){ T('Indisponível agora: o teste de pressão está pendente — com teste aprovado, concluir leva a ordem a Em conferência'); return; }
    if(s.con){ T('Serviço já concluído · ordem Em conferência'); return; }
    T('Serviço concluído · OM-0233 em Em conferência · '+(s.apto?'ativo já apto':'o ativo segue bloqueado até a decisão de aptidão'),{con:true}); };
  v.t_sob=()=>{ g2open(self,ma_G('g_sb'),'s1',null); };
  v.t_enc=()=>{ const s=self.state; const Z=ma_st(self); if(s.enc){ T('OM-0233 já encerrada'); return; }
    const f=[]; if(!s.t2) f.push('teste aprovado'); if(!s.con) f.push('concluir o serviço (Em conferência)'); if(!Z.sob) f.push('destinar a bomba hidráulica usada');
    if(f.length){ T('Indisponível agora: falta '+f.join(' e ')+' para encerrar'); return; }
    T('OM-0233 encerrada · custo fechado na safra '+MA_SAFRA+' · aptidão do ativo decidida à parte',{enc:true}); };
  self.g2after=(gid,rows,r)=>{ if(gid==='g_sb'&&r){ const ok=rows.every(x=>x.v.dest!=='A definir'); T(r.v.dest==='A definir'?'Sobra ainda sem destino':'Destinação registrada: '+r.v.item+' → '+r.v.dest.toLowerCase()+(ok?' · sobras resolvidas':'')); }
    if(gid==='g_tk'&&r){ T('Tarefa salva · horas e custo da ordem recalculados'); } }; }
'''
    shell37('MA-04','Ordem OM-0233 · Trator T1',corpo,fname=fn,crumbs_extra=['OM-0233'],
      subtitle='Corretiva por pressão hidráulica baixa — o bloqueio só cai com teste aprovado e decisão de aptidão.',
      primary_html=prim,steps=faixa(4),
      footer='O bloqueio deixa a OS-0420 e a OS-0431 impedidas; teste reprovado mantém o bloqueio; a liberação técnica não reassume a agenda antiga.')

# =====================================================================================
def ma05():
    fn='MA-05.dc.html'; HEIGHTS37[fn]=1000
    AB=[('AB-1042','Trator 02 · MF 7719','Sede · D-118','nível 38%',180,'23/09 06:40','2.988 h','Beto','foto',('Tanque cheio · 14,2 L/h','green'),
         Pt.act('Conferir contador','AB-1042 conferido: 2.988 h coerente com o apontamento de ontem (+11 h)')),
        ('AB-1041','Pulverizador · Uniport 3030','Comboio CB-01 · D-117','nível 62%',240,'23/09 05:50','1.542 h','João','foto',('Estimada · 18,9 L/h','yellow'),
         Pt.act('Conferir contador','AB-1041 conferido: 1.542 h coerente com o apontamento da OS-0421 · taxa segue estimada (sem tanque cheio)')),
        ('AB-1039','Colhedora · S680','Sede · D-117','nível 52%',310,'22/09 18:10','3.107 h','Beto','foto',('12,1 L/h · +23%','yellow'),
         Pt.cta('Investigar desvio','MA-02.dc.html',True)),
        ('AB-1037','Trator 02 · MF 7719','Sede · D-117','',320,'22/09 06:35','2.977 h','Beto','foto',('Estornado','gray'),
         Pt.act('Ver estorno','Estorno ES-0088 vinculado (23/09) · volume digitado errado · original preservado no histórico'))]
    g_ab=grid([dict(k='id',l='Lançamento'),dict(k='ativo',l='Ativo',w=130),dict(k='tq',l='Tanque/lote · nível após',w=130),dict(k='vol',l='Volume',t='num',a='r',u='L'),
               dict(k='dt',l='Data · horímetro'),dict(k='op',l='Operador · evidência'),dict(k='met',l='Método / taxa'),dict(k='acao',l='Ação')],
       [dict(id=a[0],v=dict(id=a[0],ativo=a[1],tq=a[2],vol=a[4],dt=a[5],op=a[7],met=a[9][0]),s=dict(tq=a[2],dt=a[5],op=a[7],met=a[9][0]),
             p=dict(id=[Pt.b(a[0])],tq=[Pt.txt(a[2])]+([Pt.br(),Pt.mut(a[3])] if a[3] else []),dt=[Pt.txt(a[5]),Pt.br(),Pt.mut(a[6])],
                    op=[Pt.txt(a[7]),Pt.br(),Pt.mut(a[8])],met=[Pt.chip(*a[9])],acao=[a[10]])) for a in AB],
       edit=dict(m='ro',title='Lançamento',fields=[dict(k='ativo',l='Ativo',ro=True),dict(k='tq',l='Tanque/lote',ro=True),dict(k='vol',l='Volume',t='num',u='L',ro=True),
                                                   dict(k='dt',l='Data',ro=True),dict(k='met',l='Método / taxa',ro=True)]),
       gid='g_ab',total=False,so=dict(k='dt',d=True))
    CO=[('Trator 02 · MF 7719',512,36.0,14.2,('Reconciliado','green'),'−2%',['AB-1042 · 180 L · tanque cheio','AB-1037 estornado → relançado 332 L','Horas: apontamentos de 17 a 23/09']),
        ('Pulverizador · Uniport 3030',710,37.5,18.9,('Estimado','yellow'),'+4%',['AB-1041 · 240 L · sem tanque cheio','AB-1036 · 470 L','Horas: apontamentos da OS-0421']),
        ('Colhedora · S680',340,28.1,12.1,('Reconciliado','green'),'+23% · investigar',['AB-1039 · 310 L · tanque cheio','AB-1033 · 30 L (complemento)','Referência: média 9,8 L/h'])]
    g_co=grid([dict(k='ativo',l='Ativo',w=220),dict(k='lit',l='Litros no período',t='num',a='r',u='L'),dict(k='hr',l='Horas trabalhadas',t='num',a='r',u='h',d=1),
               dict(k='tx',l='Taxa',t='num',a='r',u='L/h',d=1),dict(k='met',l='Método'),dict(k='dv',l='Desvio vs. referência')],
       [dict(id=f'co{i}',v=dict(ativo=c[0],lit=c[1],hr=c[2],tx=c[3],met=c[4][0],dv=c[5]),s=dict(met=c[4][0],dv=c[5]),
             p=dict(met=[Pt.chip(*c[4])],dv=[Pt.chip(c[5],'yellow')] if 'investigar' in c[5] else [Pt.txt(c[5])]),
             o=[dict(t=x) for x in c[6]]+[dict(t=f'Taxa = {c[1]} L ÷ {str(c[2]).replace(".",",")} h')]) for i,c in enumerate(CO)],
       edit=dict(m='origin',title='Consumo',fields=[dict(k='ativo',l='Ativo',ro=True),dict(k='tx',l='Taxa',t='num',u='L/h',ro=True)]),
       search=False,gid='g_co',total=False)
    corpo=(kpis([('ABASTECIDO HOJE','420 L','2 registros'),('TANQUE SEDE','38%','mín. proposto 40% (em aprovação)'),
                 ('CONSUMO MF 7719','14,2 L/h','reconciliado'),('DESVIOS ABERTOS','1','Colhedora +23%')])
      + section('Lançamentos por ativo e tanque','Registre abastecimentos com contador e evidência; corrija sempre com estorno vinculado.',
          [idrw('Registrar abastecimento',dict(title='Registrar abastecimento',
             sub='Mesmo formulário do app do abastecedor; evidência e contador obrigatórios.',
             fields=[('Ativo','Trator 02 · MF 7719'),('Tanque/lote','Tanque Sede · Diesel S10 · lote D-118'),('Volume (L)','180'),
                     ('Data','23/09/2026'),('Horímetro','2.988'),('Nível do tanque após (%)','38'),('Operador','Beto'),('Evidência','foto_bomba.jpg')],
             confirm='Registrar abastecimento',done='Lançamento AB-1043 registrado · saldo do tanque atualizado'),'fuel','Registrar novo abastecimento',primary=True),
           idrw('Corrigir com estorno',dict(title='Corrigir lançamento com estorno',
             sub='O lançamento original fica no histórico; o estorno e o novo lançamento ficam vinculados.',
             fields=[('Lançamento','AB-1041'),('Motivo','Lote do comboio errado (D-117 → D-118)'),('Tanque/lote','Comboio CB-01 · D-118'),('Responsável','PCM')],
             confirm='Estornar e relançar',done='Estorno ES-0089 e lançamento AB-1044 vinculados a AB-1041'),'doc','Corrigir um lançamento com estorno vinculado'),
           ilnk('Abrir no app','MB-09.dc.html','fuel','Abrir o formulário do abastecedor no app')],g_ab)
      + section('Consumo reconciliado por ativo (7 d)','Confira a taxa pelo método; clique no ativo para ver os lançamentos de origem.','',g_co,state='yellow'))
    shell37('MA-05','Abastecimentos e desempenho',corpo,
      subtitle='Lançamentos por ativo/tanque com contadores e evidência; consumo vira indicador só depois de reconciliado.',
      status=('1 desvio a investigar','yellow'),steps=faixa(5),
      footer='Litros abastecidos ≠ consumo do intervalo: taxa exata só com tanque cheio ou reconciliação; desvio confirmado abre caso em Registre inspeções.')

def build():
    ma01(); ma02(); ma03(); ma04(); ma04det(); ma05()
