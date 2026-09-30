# -*- coding: utf-8 -*-
"""Agrícola › Ordem de Serviço (OS.dc.html) — gestão das ordens por Lista ou Kanban (abas reais), cinco fases fixas,
selos como condição, painel lateral de consulta (fase, saldo, apontamentos diários na mesma ordem, origem) e "Nova ordem".

observacoes (dados coerentes com dados.py / dados2.py / telas vizinhas):
- Conjunto de ordens = dados.ORDENS (registro canônico, 13 ordens): id, tipo, talhão, área, fase, selo, realizado, saldo,
  janela, responsável e tela de detalhe vêm do registro; aqui só ficam apontamentos, pendência, origem e versão.
- Detalhe = campo "detalhe" do registro (link "Abrir ordem" no painel); sem detalhe, a ordem é consultada só pelo painel.
- Apontamentos: OS-0421 = TURNOS de areas/campo.py (50, 50, 50, 40 → 190/350; previstos 50, 50, 60);
  OS-0420 = 18 ha (21/09, conferido) + 12 ha (22/09, provisório, turno interrompido pela quebra do Trator T1) = 30/100;
  OS-0417 = 32 + 33 + 30 = 95/95 (19–21/09); OS-0415 = 48 + 48 = 96/96 (11–12/09).
- OS-0420: versão vigente v2 com v3 em revisão (saldo pausado) na versão/pendência; selo = o do registro.
- OS-0417: sobras sob custódia de Paula (equipe de campo); Rui só recebe (defeito DEMO-03).
- OS-0424/REQ-039 e OS-0425/REQ-040 = areas/suprimentos.py; OS-0430/OS-0431 = areas/planejamento.py.
- Novas ordens recebem OS-0440, OS-0441… (faixa reservada pelo registro). "Nova ordem" não emite outra ordem para a mesma
  chave cultivo|atividade (dados.ORDENS: OS-0430 = c1|a1, OS-0425 = c9|k1, OS-0431 = c3|a3, OS-0421 = T1-A, T1-B e T2 · a6):
  o erro fica no campo e o botão abre a ordem existente.
- Ação secundária pelo realizado (26/09): sem realizado (A liberar ou Liberadas) → "Cancelar sem execução" com motivo; a ordem
  vai para Canceladas (fora do quadro, chip próprio) e a situação de cada insumo acompanha (reserva liberada, requisição
  cancelada ou nada reservado). O selo do cabeçalho (em execução · impedidas) é recalculado a cada mudança de fase.
  Em execução → "Dispensar saldo" com área, motivo e validação agronômica;
  acima de 20 % da área (alçada AL-05) recusa e exige Direção (OS-0420: 70 ha = 70 %). O realizado nunca é cancelado.
- OS-0431 (DEMO-17): v1 aprovada, retirada de Liberadas pela INSP-105 antes do 1º início; selos "Aprovada pelo agrônomo" +
  "Falta máquina · Trator T1 bloqueado" (dois chips para a lista caber sem rolagem); conta como impedida.
  OS-0420 ganha selos_extra "Revisão de saldo pendente · v3" (igual ao Mapa e ao detalhe).
- Irrigação só com água (26/09, igual a areas/irrigacao.py): OS-0419, OS-0422 e OS-0423 não passam pelo agrônomo; liberar depende da
  prontidão operacional. OS-0422 = 13,5 mm em 2 passadas de 6,75 mm, selo "Janela a definir", dono João (irrigante);
  OS-0423 = 4,0 mm no gotejo T7, selo "Conflito · parada da B3", dono Caio (PCP), estimativa por ET (sonda sem dado, não bloqueia).
  Só a fertirrigação (OS-0418) segue com o agrônomo.
- Filtros do topo (ui37.MACRO: Fazenda e Safra) valem para lista, Kanban, chips de fase e selo do cabeçalho; recorte sem ordens mostra
  uma frase e uma ação ("Ver Santa Rita" ou "Ver todas as safras"). Fazenda/safra de cada ordem = dados.ORDENS (faz, saf).
- Cenário compartilhado (26/09, etapa 2): EXTRAJS[0] = cenario.js_prefixo() + JS da tela. Fase, aprovação, realizado/saldo, apontamentos,
  requisição e insumos vêm de cenGet().ordens/.reqs; cenOuvir(self) redesenha quando Estoque ou App mudam o cenário. Toda ação da O.S.
  grava por cenMudar com funções osc_* (aprovar com recibo, liberar = cenLiberar com reserva por lote, iniciar, apontar, conferência,
  encerrar só com cenPodeEncerrar vazio, cancelar liberando a reserva, dispensar, nova ordem). Liberar é testado numa cópia do cenário:
  o erro de saldo/lote vira o motivo do bloqueio. O bloqueio do encerramento (sinal ou sobra em custódia, com "Receber devolução no
  Estoque") vem do cenário, inclusive o da OS-0417. "Restaurar demonstração" (rodapé do bloco) chama cenReset().
- Verificador v39 (26/09): bloqueio lido do cenário também na lista e no Kanban (liberar sem lote → selo vermelho "Falta insumo · X" +
  Suprimentos, conta como impedida; encerrar com sobra → "Sobras a receber" + Rui (almoxarife); sem sinal → "Aguardando sinal do app").
  Ordem nova leva os insumos da atividade do plano (dose × área, gatilho e conjunto do plano); sem insumo libera sem requisição; requisição
  nova = REQ-041, REQ-042… (osc_reqId, três dígitos, antes de cenLiberar). Selo do cabeçalho com cor calculada (vermelho só com impedidas).
  Coluna Encerradas com o período das ordens da coluna. Ordens de água: lâmina só em Insumos, nota de ET só no Próximo passo.
"""
import json, os
from engine import (grid,esc,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,DISP,BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, HEIGHTS37, tabs
import dados as D
import dados2 as D2
import alocacao as AL

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
T=lambda: H('true')
FASES=['A liberar','Liberadas','Em execução','Em conferência','Encerradas']

# ---------- dados das ordens (projeção única do registro dados.ORDENS para lista, Kanban e painel) ----------
VERSAO={o['id']:o['versao'] for o in D.OS}
# irrigação só com água: sem agrônomo; o sistema programa a lâmina do balanço hídrico e libera pela prontidão operacional
LAM={'OS-0419':'10,81 mm em 1 passada','OS-0422':'13,5 mm em 2 passadas de 6,75 mm','OS-0423':'4,0 mm'}
OBS={'OS-0423':'estimativa por ET · sonda sem dado'}  # nota que não bloqueia
TIPO={'OS-0419':'Irrigação · água'}  # dados.ORDENS ainda diz "água por política" (fora da permissão desta frente)
VERSAO.update({'OS-0419':'v1 · liberada pela prontidão operacional','OS-0422':'v1 · só água · libera pela prontidão','OS-0423':'v1 · só água · libera pela prontidão',
               'OS-0420':'v2 aprovada · v3 em revisão',
               'OS-0424':'v1 aprovada','OS-0425':'plano CAFE-AR · v1 aprovada','OS-0430':'v1 emitida','OS-0431':'REC-014 v2 · v1 aprovada'})
AP={  # (data, dia, ha, situação)
 'OS-0421':[('20/09',1,50,'Conferido'),('21/09',2,50,'Conferido'),('22/09',3,50,'Conferido'),('23/09',4,40,'Provisório'),
            ('24/09',5,50,'Previsto'),('25/09',6,50,'Previsto'),('26/09',7,60,'Previsto')],
 'OS-0420':[('21/09',1,18,'Conferido'),('22/09',2,12,'Provisório')],
 'OS-0417':[('19/09',1,32,'Conferido'),('20/09',2,33,'Conferido'),('21/09',3,30,'Conferido')],
 'OS-0415':[('11/09',1,48,'Conferido'),('12/09',2,48,'Conferido')],
}
NOTA_AP={'OS-0421':'Dia 4 encerrado por chuva às 17:40 · app sincronizado.','OS-0420':'Turno do dia 2 interrompido pela quebra do Trator T1 (OM-0233).'}
COND={
 'OS-0421':'Turno do dia 4 aguardando conferência · Paula.',
 'OS-0420':'Trator T1 bloqueado pela OM-0233 · Manutenção; substituto Trator 02 a partir de 24/09. A v3 (KCl −12 % só no saldo de 70 ha) aguarda Ana (agrônoma): saldo pausado, 30 ha realizados preservados na v2.',
 'OS-0419':'Pronta para iniciar hoje às 20:00 · João.',
 'OS-0418':'Revisão agronômica da v2 (fertirrigação) · Ana (agrônoma) · vence hoje.',
 'OS-0417':'10 sc de MAP 11-52 sob custódia de Paula (equipe de campo) · prazo 24/09. Rui recebe a devolução no almoxarifado.',
 'OS-0415':'Nenhuma · ordem encerrada, somente consulta.',
 'OB-0104':'Ordem conciliada. O lote L27-013 segue bloqueado pela Qualidade (INSP-88 · prazo 25/09).',
 'OS-0422':'Lâmina programada pelo balanço hídrico; a janela precisa sair antes do próximo ciclo.',
 'OS-0423':'Lâmina programada pelo balanço hídrico; o conflito precisa ser resolvido antes das 14:00.',
 'OS-0424':'Fungicida A reservado: 65 L do lote F26-02 (REQ-039 · recibo RS-7741). Próximo passo: Marcos retira no almoxarifado e confirma no app para iniciar em 24/09.',
 'OS-0425':'REQ-040 pede 11.400 kg de NPK 20-05-20; o lote N26-03 tem 8.000 kg · Suprimentos completa a entrega até 15/10.',
 'OS-0430':'Revisão agronômica · Ana (agrônoma). Dessecação a 20 dias do plantio (DAP −20).',
 'OS-0431':'Retirada de Liberadas em 23/09: a INSP-105 bloqueou o Trator T1 (OM-0233) antes do 1º início. Aprovação da v1 preservada. Dono: PCP · prazo: antes de 24/09 06:00 · próxima ação: Confirmar substituto.',
}
ORIG={
 'OS-0421':['Safra 2026/27 · plano de safra, janela 20–26/09','Recomendação: fungicida 1ª aplicação · protocolo do plano técnico · v2 aprovada'],
 'OS-0420':['Safra 2026/27 · plantio Soja 58 W no T4','Recomendação REC-014 v2 · semente e adubação de base'],
 'OS-0419':['Balanço hídrico de 23/09 · Pivô 2 · Milho V10'],
 'OS-0418':['Reclassificação da tarefa de água do Pivô 1 para fertirrigação','Versão v2 em revisão agronômica · aprovação individual'],
 'OS-0417':['Safra 2026/27 · Feijão P1 · adubação de cobertura','Requisição REQ-031 · MAP 11-52: 100 sc entregues, 70 consumidas, 20 devolvidas, 10 a receber'],
 'OS-0415':['Safra 2025/26 · Milho T3 · dessecação pós-colheita'],
 'OB-0104':['Rota de beneficiamento aprovada · Armazém Sede','Lote L27-013 · café beneficiado, 3.690 sc'],
 'OS-0422':['Balanço hídrico de 23/09 · Pivô 2 · Milho V10 · próximo ciclo'],
 'OS-0423':['Balanço hídrico de 23/09 · Gotejo T7 · Mamão'],
 'OS-0424':['Safra 2026/27 · Pivô 2 · pulverização de fungicida','Requisição REQ-039 · Fungicida A, 65 L do lote F26-02'],
 'OS-0425':['Café C1 · plano CAFE-AR · adubação 1ª parcela','Requisição REQ-040 · NPK 20-05-20, 11.400 kg'],
 'OS-0430':['Safra 2026/27 · Soja T1-A · plano SOJA-AT','Dessecação pré-plantio · 160 ha'],
 'OS-0431':['Safra 2026/27 · plantio Soja 58 W no T2','Recomendação REC-014 v2 · semente e adubação de base','Liberada e retirada em 23/09 pela INSP-105'],
}
# atividade de cada ordem (operação, atividade, gatilho, origem do padrão, operação do conjunto em dados2.CONJ)
ATV={
 'OS-0415':('Pulverização','Dessecação pós-colheita','5 dias após a colheita','Recomendação da safra 2025/26','Pulverização'),
 'OS-0417':('Adubação a lanço','Adubação de cobertura','DAP +25','Recomendação de cobertura · Feijão P1','Adubação a lanço'),
 'OS-0418':('Fertirrigação','Fertirrigação de nitrogênio','janela 24/09 21:00–25/09 11:15','Tarefa de água do Pivô 1 reclassificada · v2','Fertirrigação'),
 'OS-0419':('Irrigação','Irrigação · água','déficit hídrico','Balanço hídrico',None),
 'OS-0420':('Plantio','Plantio e adubação de base','DAP 0 · 22/09','Soja alta tecnologia v6 · REC-014 v2','Plantio'),
 'OS-0421':('Pulverização','Fungicida 1ª aplicação','DAP +45','Soja alta tecnologia v6','Pulverização'),
 'OS-0422':('Irrigação','Irrigação do próximo ciclo','déficit 11,2 mm + ETc prevista','Balanço hídrico',None),
 'OS-0423':('Irrigação','Irrigação por gotejo','déficit hídrico','Balanço hídrico',None),
 'OS-0424':('Pulverização','Fungicida','24/09','Safra 2026/27 · Pivô 2','Pulverização'),
 'OS-0425':('Adubação a lanço','Adubação 1ª parcela','data 15/10/2026','Café arábica produção v2','Adubação a lanço'),
 'OS-0430':('Pulverização','Dessecação pré-plantio','DAP −20 · 25/09','Soja alta tecnologia v6','Pulverização'),
 'OS-0431':('Plantio','Plantio e adubação de base','DAP 0 · 24/09','Soja alta tecnologia v6 · REC-014 v2','Plantio'),
 'OB-0104':('Beneficiamento','Beneficiamento de grãos','15–18/09','Rota de beneficiamento aprovada',None),
}
# insumos por ordem: (grupo, produto, dose por ha, unidade, quantidade fixa da ordem ou None = dose × área, situação)
INS={
 'OS-0415':[('Herbicidas','Glifosato 480',2.0,'L',None,'Consumo conferido')],
 'OS-0417':[('Fertilizantes','MAP 11-52',36.84,'kg',3500,'Entregues 100 sc · usadas 70 · devolvidas 20 · 10 sc com Paula')],
 'OS-0418':[('Fertilizantes','Ureia 45%',12.0,'kg',None,'Requisição REQ-038 ao liberar')],
 'OS-0420':[('Sementes','Semente de soja 58 W',52.0,'kg',None,'Entregue · saldo pausado'),('Fertilizantes','MAP 11-52',250.0,'kg',None,'Entregue · saldo pausado')],
 'OS-0421':[('Fungicidas','Fungicida A',0.5,'L',None,'Entregue ao operador'),('Adjuvantes','Adjuvante espalhante',0.25,'L',None,'Entregue ao operador')],
 'OS-0424':[('Fungicidas','Fungicida A',0.8,'L',None,'Reservado 65 L · lote F26-02 · REQ-039')],
 'OS-0425':[('Fertilizantes','NPK 20-05-20',300.0,'kg',None,'REQ-040 · lote N26-03 tem 8.000 kg · faltam 3.400 kg')],
 'OS-0430':[('Herbicidas','Glifosato 480',2.0,'L',None,'Reserva ao liberar'),('Herbicidas','2,4-D 806',1.0,'L',None,'Reserva ao liberar'),('Adjuvantes','Óleo mineral',0.5,'L',None,'Reserva ao liberar')],
 'OS-0431':[('Sementes','Semente de soja 58 W',52.0,'kg',None,'Reserva ao liberar'),('Fertilizantes','MAP 11-52',250.0,'kg',None,'Reserva ao liberar')],
}
SEM_INS={'OS-0419':'Água · 10,81 mm em 1 passada · sem almoxarifado.','OS-0422':'Água · 13,5 mm em 2 passadas de 6,75 mm (limite de 12,0 mm por passada no pivô) · sem almoxarifado.',
         'OS-0423':'Água · 4,0 mm por gotejo em 2 h · sem almoxarifado.','OB-0104':'Ordem de processo: entradas e saídas por etapa do beneficiamento, sem dose por hectare.'}
# impedimento que segura o próximo passo da fase atual: o quê, quem resolve e onde
BLOQ={
 'OS-0431':dict(acao='liberar',t='Liberar bloqueado: Trator T1 em manutenção (OM-0233).',q='PCP confirma a máquina substituta antes de 24/09 06:00.'),
 'OS-0420':dict(acao='apontar',t='Apontamento pausado: v3 em revisão por Ana (agrônoma) e Trator T1 bloqueado (OM-0233).',q='Ana aprova a v3; o Trator 02 assume a partir de 24/09.',h='CA-01x-os0420.dc.html',hl='Abrir a ordem completa'),
 'OS-0422':dict(acao='liberar',tone='yellow',t='Definir janela: as 2 passadas ainda não têm horário.',q='João (irrigante) define a janela na Irrigação.',h='IR-02.dc.html',hl='Definir janela'),
 'OS-0423':dict(acao='liberar',tone='red',t='Resolver conflito: a parada da bomba B3 (14:00–15:00) cai na janela.',q='Caio (PCP) resolve o conflito na Irrigação.',h='IR-02.dc.html',hl='Resolver conflito'),
}
DONO={'OS-0418':('Ana (agrônoma)','vence hoje'),'OS-0420':('Ana (agrônoma) · Manutenção','v3 hoje · OM-0233 até 24/09'),'OS-0421':('Paula','conferir o dia 4 hoje'),
      'OS-0417':('Rui (almoxarife)','24/09'),'OS-0422':('João (irrigante)','definir janela antes do próximo ciclo'),'OS-0423':('Caio (PCP)','resolver conflito hoje antes das 14:00'),
      'OS-0425':('Suprimentos','entrega até 15/10'),'OS-0430':('Ana (agrônoma)','antes de 25/09'),'OS-0431':('PCP','substituto antes de 24/09 06:00')}
LINK={'OS-0417':'CA-02.dc.html'}
AVISO={'OS-0425':'O lote N26-03 cobre 26,7 dos 38 ha; Suprimentos completa a entrega até 15/10.'}
CJ={c['op']:c for c in D2.CONJ}
# cancelamento sem execução: (o que a confirmação avisa, o que o aviso final diz, nova situação do insumo) — só ordens com reserva ou requisição
CANC={'OS-0424':('Libera a reserva de 65 L do lote F26-02 (REQ-039).','Reserva de 65 L do lote F26-02 liberada.','Reserva de 65 L liberada · lote F26-02 · REQ-039'),
      'OS-0425':('Cancela a requisição REQ-040; nada foi entregue.','Requisição REQ-040 cancelada; nada tinha sido entregue.','REQ-040 cancelada · nada entregue')}
_RED=('impedid','bloquead','atrasad','conflito','vencid')
def _selos(o):  # selo principal + selos_extra do registro (mesma lista no Mapa e no detalhe)
    ts=([o['selo']] if o.get('selo') else [])+list(o.get('selos_extra') or [])
    return [dict(t=t,c='red' if any(w in t.lower() for w in _RED) else ('green' if t.startswith('Aprovada') else 'yellow')) for t in ts]
def _chaves(o):  # chave cultivo|atividade do registro: texto (um cultivo) ou lista (ordem que cobre vários cultivos)
    k=o.get('chave'); return list(k) if isinstance(k,(list,tuple)) else ([k] if k else [])
def _ordens():
    out=[]
    for o in D.ORDENS:
        ap=[dict(d=d,dia=n,ha=ha,st=s) for d,n,ha,s in AP.get(o['id'],[])]
        out.append(dict(id=o['id'],tipo=TIPO.get(o['id'],o['tipo']),talhao=o['talhao'],area=o.get('area'),etapa=o['etapa'],selos=_selos(o),
                        faz=o['faz'],saf=o['saf'],agua=o['id'] in LAM,lam=LAM.get(o['id'],''),obs=OBS.get(o['id'],''),
                        realizado=o.get('realizado'),saldo=o.get('saldo'),resp=o['resp'],keys=_chaves(o),
                        aprov=(o['etapa']=='A liberar' and 'aprovada' in VERSAO[o['id']]),canc=CANC.get(o['id']),
                        versao=VERSAO[o['id']],
                        janela=o['janela'],ap=ap,nota=NOTA_AP.get(o['id'],''),cond=COND[o['id']],orig=ORIG[o['id']],
                        link=(LINK.get(o['id']) or o['detalhe'] or ''),dono=DONO.get(o['id'],('',''))[0],prazo=DONO.get(o['id'],('',''))[1],atv=_atv(o),ins=[dict(g=g,p=pr,dose=d,un=u,tot=(t if t is not None else (round(d*(o.get('area') or 0),2))),sit=si) for g,pr,d,u,t,si in INS.get(o['id'],[])],
                        semins=SEM_INS.get(o['id'],''),bloq=(dict(BLOQ[o['id']],fase=o['etapa']) if o['id'] in BLOQ else None),aviso=AVISO.get(o['id'],'')))
    return out
def _conj(oid,conj):  # conjunto = o trator alocado à ordem (alocacao.py, o mesmo de Recursos alocados) + o implemento do rendimento
    maqs=list(dict.fromkeys(a['r'] for a in AL.ALOC if a['os']==oid and a['sit']!='manutenção' and AL.TIPO[a['r']]=='Máquina'))
    if len(maqs)!=1 or ' + ' not in conj or not conj.startswith('Trator') or not AL.NOME[maqs[0]].startswith('Trator'): return conj
    return AL.NOME[maqs[0]]+' + '+conj.split(' + ',1)[1]
def _atv(o):
    op,nome,gat,orig,cop=ATV[o['id']]; c=CJ.get(cop) if cop else None
    return dict(op=op,nome=nome,gat=gat,orig=orig,conj=(_conj(o['id'],c['conj']) if c else ''),rend=(c['rend'] if c else 0))
def _gatilho(g):  # gatilho da atividade do plano no formato das ordens do registro (DAP −20, DAP +45, data 15/10/2026…)
    t,d=g.get('tipo'),g.get('dias')
    if t=='DAP': return 'DAP '+('+' if d>0 else ('−' if d<0 else ''))+str(abs(d))
    if t in ('DANC','DAPC'): return f"{d} dia{'s' if d!=1 else ''} {'antes' if t=='DANC' else 'após'} a colheita"
    if t=='DATA' and g.get('data'): a,m,dd=g['data'].split('-'); return f'data {dd}/{m}/{a}'
    return ''
def _nova_ordem_dados():
    safs=[s for s in D2.SAFRAS if not s['ro']]
    import cenario
    cult={s['id']:[dict(id=c['id'],t=f"{c['local']} · {c['cultura']} {c['variedade']} · {c['area']:g} ha",local=c['local'],area=c['area'],plano=c['plano'],var=c['variedade'])
                   for c in D2.CULTIVOS.get(s['id'],[])] for s in safs}
    # atividade do plano com seus insumos (grupo, produto, dose/ha): a ordem nova leva dose × área, como as ordens do registro
    planos={p['id']:dict(nome=p['nome'],versao=p['versao'],atv=[dict(id=a['id'],nome=a['nome'],op=a['op'],gat=_gatilho(a.get('g') or {}),
                   ins=[dict(g=x['grupo'],p=x['prod'],dose=x['dose'],un=x['un']) for x in a['prods']]) for a in p['atividades']]) for p in D2.PLANOS}
    return dict(safs=[dict(id=s['id'],t=s['nome'],mf=s['nome'].replace('Safra ','')) for s in safs],cult=cult,planos=planos,
                conj={op:dict(conj=c['conj'],rend=c['rend']) for op,c in CJ.items()},emb=cenario.EMB)

JS=r'''
const FASES=['A liberar','Liberadas','Em execução','Em conferência','Encerradas'];
const FCOR={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray','Canceladas':'gray'};
const STCOR={'Conferido':'green','Provisório':'yellow','Previsto':'gray','Aguardando sinal':'yellow'};
const LIM_DISP=0.20;  // alçada AL-05: dispensa de saldo até 20 % da área sem a Direção
function GR(id){ return GRIDS.find(g=>g.id===id); }
function nf(n){ return Number(n||0).toLocaleString('pt-BR'); }
function chipSt(c){ const cc=G2C[c]||G2C.gray; return 'display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';'; }
function dotSt(c){ const cc=G2C[c]||G2C.gray; return 'width:6px;height:6px;border-radius:999px;flex-shrink:0;background:'+cc[0]+';'; }
// ===== O.S. × cenário compartilhado (cenario.js, o mesmo estado do Estoque e do App) =====
// Fase, aprovação, realizado/saldo, apontamentos, requisição e insumos vêm de cenGet(); o que o cenário não tem vem de OSD (registro).
// Gancho de teste/inspeção (o script da tela roda isolado): os testes os_* leem e mudam o cenário na própria página.
try { window.__cen = { cenGet, cenMudar, cenReset, cenLiberar, cenEntregar, cenDevolver, cenConfirmarRecebimento, cenIniciarTurno, cenPausar, cenFecharTurno, cenOcorrencia, cenSinal, cenPodeEncerrar, osc_decidir, osc_liberar, osc_encerrar }; } catch (e) {}
function ords(self){ const c=cenGet(); const ids={};
  const out=OSD.ords.map(b=>{ ids[b.id]=1; return osMerge(b,c.ordens[b.id],c); });
  Object.keys(c.ordens).forEach(k=>{ const co=c.ordens[k]; if(!ids[k]&&co.osc&&co.osc.novo) out.push(osMerge(co.osc.novo,co,c)); });  // emitidas nesta tela
  return out; }
// turno fechado sem sinal: o consumo ainda está no aparelho (fila AP|…); o escritório vê consumo e área juntos, quando o app envia.
// cenFecharTurno já baixa a custódia no aparelho; aqui a requisição exibida devolve essa baixa até o envio (CEN_BAIXA_NO_SINAL desliga).
function osPendCons(co,prod){ if(typeof CEN_BAIXA_NO_SINAL!=='undefined') return 0;
  return (co.ap||[]).filter(a=>a.sinc===false).reduce((s,a)=>s+(Number((a.cons||{})[prod])||0),0); }
function osReqVis(co,r){ if(!r) return r;
  return Object.assign({},r,{itens:r.itens.map(it=>{ const q=Math.min(osPendCons(co,it.prod),it.consumido||0);
    return q>1e-9?Object.assign({},it,{consumido:it.consumido-q,custodia:it.custodia+q,semSinal:q}):it; })}); }
// área apontada no aparelho e ainda não enviada: não entra no realizado, mas conta para o máximo do apontamento pela web
function osApPend(o){ return (o.ap||[]).filter(a=>a.sinc===false).reduce((s,a)=>s+(a.ha||0),0); }
function osMerge(b,co,c){ if(!co) return b;
  const x=co.osc||{}; const r=co.req?osReqVis(co,c.reqs[co.req]||null):null; const mine=(x.cond!==undefined&&x.fase===co.etapa);
  const o=Object.assign({},b,{etapa:co.etapa,aprov:!!co.aprov,ap:co.ap||[],req:co.req||null,reservado:!!co.reservado,selos:co.selos||b.selos||[],versao:co.versao||b.versao,r,recibo:x.recibo||null});
  if(b.area){ o.realizado=co.realizado||0; o.saldo=co.saldo||0; }
  if(co.etapa!==b.etapa){ o.cond=osCondGen(o); o.dono=co.etapa==='Em conferência'?o.resp:''; o.prazo=co.etapa==='Em conferência'?'conferir':''; }
  if(mine){ o.cond=x.cond; o.dono=x.dono||''; o.prazo=x.prazo||''; if(x.rej) o.rej=x.rej; }
  if(x.disp) o.disp=x.disp;
  if(co.etapa==='Canceladas'&&x.insx) o.insx=x.insx;
  // execução com turno no aparelho: o mesmo selo da conferência na lista e no Kanban (o painel e o Mapa dizem "aguardando sinal")
  if(co.etapa==='Em execução'){ o.selos=o.selos.filter(s=>!/^Aguardando sinal/.test(s.t));
    if((co.ap||[]).some(a=>a.sinc===false)) o.selos=o.selos.concat([{t:'Aguardando sinal do app',c:'yellow'}]); }
  // conferência: o encerramento depende do cenário (apontamento aguardando sinal ou sobra em custódia)
  if(co.etapa==='Em conferência'){ o.encM=cenPodeEncerrar(c,co.id);
    if(!o.encM){ o.selos=o.selos.filter(s=>!/Sobras a receber|Aguardando sinal/i.test(s.t)); if(!mine){ o.cond='Apontamentos enviados e nada em custódia. Próximo passo: conferir e encerrar.'; o.dono=o.resp; o.prazo='conferir e encerrar'; } }
    else { const sin=/sinal/.test(o.encM); const t=sin?'Aguardando sinal do app':'Sobras a receber';  // o bloqueio também na lista e no Kanban
      if(!o.selos.some(s=>s.t===t)) o.selos=o.selos.concat([{t,c:'yellow'}]);
      if(sin){ o.dono=o.resp; o.prazo='reconectar o app'; } else if(!/almoxarife/.test(o.dono||'')){ o.dono='Rui (almoxarife)'; o.prazo='receber a devolução'; } } }
  // versão aprovada: o Estoque (reserva por lote) pode segurar a liberação → selo vermelho e dono na lista, no Kanban e no painel
  if(co.etapa==='A liberar'&&co.aprov&&!o.agua&&(co.ins||[]).length){ const e=osLibErro(o,c);
    if(e){ const pr=(/ de (.+?)(?: no Estoque|:)/.exec(e)||[])[1]||''; o.libErr=e;
      o.selos=o.selos.filter(s=>!/^Falta insumo/.test(s.t)).concat([{t:'Falta insumo'+(pr?' · '+pr:''),c:'red'}]);
      o.dono='Suprimentos'; o.prazo='receber o insumo no Estoque';
      o.cond=String(o.cond||'').replace('Próximo passo: liberar para execução.','A liberação aguarda '+(pr||'o insumo')+' no Estoque.'); } }
  return o; }
function osCondGen(o){ const pend=(o.ap||[]).filter(a=>a.sinc===false).length;
  if(o.etapa==='Liberadas') return 'Liberada'+(o.req?' · '+o.req+' reservou os insumos no Estoque':'')+'. Próximo passo: iniciar na janela '+o.janela+'.';
  if(o.etapa==='Em execução') return 'Em execução · '+nf(o.realizado)+' de '+nf(o.area)+' ha'+(pend?' · '+pend+(pend>1?' apontamentos':' apontamento')+' no aparelho aguardando sinal':'')+'. Registre o apontamento de cada turno.';
  if(o.etapa==='Em conferência') return 'Aguardando conferência de apontamentos, consumo e sobras.';
  if(o.etapa==='Encerradas') return 'Nenhuma · ordem encerrada, somente consulta.';
  return o.cond; }
// embalagem: 320 L em "galão 20 L" → "16 × galão 20 L" (só quando fecha em embalagens inteiras)
function osPk(q,emb){ const m=/^(.*?)\s*(\d[\d.]*)\s*(kg|L)\b/.exec(String(emb||'')); if(!m||!(q>1e-9)) return ''; const n=Number(m[2].replace(/\./g,'')); const k=q/n;
  return (n>0&&Math.abs(k-Math.round(k))<1e-6)?Math.round(k)+' × '+emb:''; }
// situação do insumo (uma frase) e trilha reservado → entregue → confirmado no app → consumido → em custódia → devolvido
function osInsSit(o,x,it){ if(o.etapa==='Canceladas') return o.insx||x.sit;
  if(!it||(!o.reservado&&!(it.entregue>0))) return x.sit;
  const un=it.un;
  if(!(it.entregue>0)) return 'Reservado no Estoque · lote '+it.lote+' · '+o.req+(it.solicitado<x.tot-1e-6?' · faltam '+nd(x.tot-it.solicitado)+' '+un:'');
  if(it.custodia>1e-6&&!it.confirmado) return 'Entregue · aguardando confirmação no app';
  if(it.custodia>1e-6) return o.etapa==='Em conferência'?'Sobra em custódia · devolver no Estoque':'Em custódia · '+(it.quem||o.resp)+(it.semSinal?' · consumo no aparelho, aguardando sinal':'');
  const pend=cenSaldoEntregar(it); if(pend>1e-6&&['Liberadas','Em execução'].indexOf(o.etapa)>=0) return 'Entregue '+nd(it.entregue)+' '+un+' · '+nd(pend)+' '+un+' a entregar';
  return it.devolvido>0?'Consumido · sobra devolvida':'Consumido'; }
function osTrilha(o,it){ if(!it||o.etapa==='Canceladas'||(!o.reservado&&!(it.entregue>0))) return [];
  const q=(n)=>nd(n)+' '+it.un; const pk=osPk(it.entregue,it.emb); const ent=it.entregue>0;
  const S=[['Reservado '+q(it.solicitado)+' · lote '+it.lote,1],
    [ent?'Entregue '+q(it.entregue)+(pk?' ('+pk+')':'')+' a '+(it.quem||o.resp):'Entregue',ent?1:0],
    [it.confirmado?'Confirmado no app':(ent?'Aguardando confirmação no app':'Confirmado no app'),it.confirmado?1:(ent?2:0)],
    [it.consumido>0?'Consumido '+q(it.consumido):'Consumido',it.consumido>0?1:0],
    [it.custodia>1e-6?'Em custódia '+q(it.custodia):'Em custódia',it.custodia>1e-6?(o.etapa==='Em conferência'?3:1):0],
    [it.devolvido>0?'Devolvido '+q(it.devolvido):'Devolvido',it.devolvido>0?1:0]];
  const ST=['color:#8A968E;','color:#15201A;font-weight:600;','color:#8A5A00;font-weight:700;','color:#B42318;font-weight:700;'];
  return S.map((s,i)=>({t:(i?'› ':'')+s[0],st:ST[s[1]]})); }
// liberar sem gravar (cópia do cenário): o erro de saldo ou de lote vira o motivo do bloqueio antes do clique
function osLibErro(o,c0){ const c=c0||cenGet(); if(!c.ordens[o.id]) return ''; const k=cenClone(c);
  try { osc_liberar(k,o.id,false,o.janela); return ''; } catch (e) { return String(e.message||e); } }
function osEncBloq(o){ const m=o.encM;
  if(/sinal/.test(m)) return {acao:'encerrar',t:'Encerrar bloqueado: há apontamentos no aparelho aguardando sinal.',q:o.resp+' reconecta o app; o envio é automático e não duplica.'};
  const its=(o.r?o.r.itens:[]).filter(i=>i.custodia>0.001); const quem=its.map(i=>i.quem||o.resp).filter((v,i,a)=>a.indexOf(v)===i).join(', ')||o.resp;
  return {acao:'encerrar',t:'Encerrar bloqueado: sobra em custódia · '+its.map(i=>{ const pk=osPk(i.custodia,i.emb); return i.prod+' '+nd(i.custodia)+' '+i.un+(pk?' ('+pk+')':''); }).join(', ')+' com '+quem+'.',
    q:'Rui (almoxarife) recebe a devolução no Estoque.',h:'EST.dc.html',hl:'Receber devolução no Estoque'}; }
// mudança pela tela: grava no cenário (cenMudar) e redesenha; o erro fica junto ao botão (pa.err) ou vai para onErr
function osRun(self,fn,ok,onErr){ const r=cenMudar(null,fn);
  if(r.erro){ if(onErr) onErr(r.erro); else self.setState({pa:Object.assign({},self.state.pa||{},{err:r.erro})}); return r; }
  self.setState(Object.assign({cenrev:Date.now(),g2toast:r.msg||''},ok||{})); return r; }
// ---------- funções próprias da O.S. sobre o cenário (prefixo osc_; só dentro de cenMudar) ----------
function osc_o(c,id){ const o=c.ordens[id]; if(!o) throw new Error('Ordem '+id+' não encontrada no cenário.'); o.osc=o.osc||{}; return o; }
function osc_txt(o,p){ Object.assign(o.osc,p,{fase:o.etapa}); }
// revisão da versão: aprovar (com recibo), devolver ou rejeitar; nenhuma decisão libera a ordem
function osc_decidir(c,id,k,mot){ const o=osc_o(c,id); if(o.etapa!=='A liberar') throw new Error(id+' não está em A liberar.');
  const sel=(o.selos||[]).filter(x=>!/Aguardando|Devolvida|Aprovada|Rejeitada/.test(x.t)); const vs=String(o.versao).match(/v\d+/g)||['v1']; const vn=vs[vs.length-1];
  if(k==='aprovar'){ const rec={id:'APV-'+id.slice(3)+'-'+vn,at:cenAgora(),quem:'Ana (agrônoma)'};
    o.aprov=true; o.versao=String(o.versao).replace('em revisão','aprovada').replace('emitida','aprovada'); o.selos=sel.concat([{t:'Aprovada pelo agrônomo',c:'green'}]);
    o.osc.recibo=rec; osc_txt(o,{cond:'Versão '+vn+' aprovada por Ana (agrônoma) · recibo '+rec.id+' às '+rec.at+'. Próximo passo: liberar para execução.',dono:'',prazo:''});
    return {msg:'Versão '+vn+' aprovada · recibo '+rec.id+'. '+id+' ainda não foi liberada para execução.'}; }
  if(!mot) throw new Error('Informe o motivo.');
  if(k==='devolver'){ o.selos=sel.concat([{t:'Devolvida para ajuste',c:'yellow'}]); osc_txt(o,{cond:'Devolvida para ajuste: '+mot+' · o PCP ajusta e reenvia.',dono:'PCP',prazo:'ajustar e reenviar'}); return {msg:id+' devolvida para ajuste. Continua em A liberar.'}; }
  o.selos=sel.concat([{t:'Rejeitada',c:'red'}]); osc_txt(o,{rej:mot,cond:'Rejeitada: '+mot+'. A liberação fica bloqueada; a ordem não foi cancelada.',dono:'PCP',prazo:'ajustar ou cancelar'});
  return {msg:id+' rejeitada. A ordem não foi cancelada.'}; }
// liberar: exige a versão aprovada e reserva por lote (cenLiberar); água sem produto libera pela prontidão, sem requisição
function osc_liberar(c,id,agua,jan){ const o=osc_o(c,id);
  if(agua){ if(o.etapa!=='A liberar') throw new Error(id+' não está em A liberar.'); o.etapa='Liberadas'; o.selos=(o.selos||[]).filter(x=>!/Aguardando|Aprovada/.test(x.t));
    return {msg:id+' liberada pela prontidão operacional. Água sem requisição no Estoque.'}; }
  if(!(o.ins||[]).length){  // sem insumo: libera sem requisição (nada a reservar no Estoque)
    if(o.etapa!=='A liberar') throw new Error(id+' não está em A liberar.'); if(!o.aprov) throw new Error('Aprove a versão antes de liberar.');
    o.etapa='Liberadas'; o.selos=(o.selos||[]).filter(x=>!/Aguardando|Aprovada/.test(x.t));
    return {msg:id+' liberada. Sem insumos a reservar: nenhuma requisição no Estoque.'}; }
  const r0=o.req&&c.reqs[o.req];  // requisição aberta antes da aprovação, sem entrega: refeita na liberação, com reserva por lote
  if(r0&&!o.reservado){ r0.itens=r0.itens.filter(i=>i.entregue>0); r0.estado='Reservada'; }
  if(!o.req){ const rid=osc_reqId(c); o.req=rid; c.reqs[rid]={id:rid,os:id,itens:[],estado:'Reservada'}; }  // mesmo formato das existentes (REQ-041)
  return cenLiberar(c,id); }
// próxima requisição: maior número existente + 1, com três dígitos (REQ-040 → REQ-041), sem pular
function osc_reqId(c){ const n=Object.keys(c.reqs||{}).reduce((m,k)=>Math.max(m,parseInt(String(k).replace(/\D/g,''),10)||0),0)+1;
  return 'REQ-'+String(n).padStart(3,'0'); }
// iniciar exige os insumos com o operador: entregues no Estoque e confirmados no app (água e ordem sem insumo não passam por aqui)
function osIniErro(o,r){ const its=((o.ins||[]).length&&r)?r.itens:[]; if(!its.length) return null;
  const q=i=>i.prod+' '+nd(i.custodia>1e-6?i.custodia:cenSaldoEntregar(i))+' '+i.un;
  const fal=its.filter(i=>!(i.consumido>0)&&!(i.custodia>1e-6));
  if(fal.length) return {acao:'iniciar',t:'Iniciar bloqueado: '+r.id+' sem entrega · '+fal.map(q).join(', ')+' a entregar.',q:'Rui (almoxarife) entrega no Estoque; '+(o.resp||'o operador')+' confirma o recebimento no app.',h:'EST.dc.html',hl:'Entregar no Estoque'};
  const nc=its.filter(i=>i.custodia>1e-6&&!i.confirmado);
  if(nc.length){ const quem=nc.map(i=>i.quem||o.resp).filter((v,k,a)=>a.indexOf(v)===k).join(', ');
    return {acao:'iniciar',t:'Iniciar bloqueado: '+nc.map(q).join(', ')+(nc.length>1?' entregues a ':' entregue a ')+quem+', aguardando confirmação no app.',q:quem+' confirma o recebimento no app.',h:'MB-05.dc.html',hl:'Ver no app'}; }
  return null; }
function osc_iniciar(c,id){ const o=osc_o(c,id); if(o.etapa!=='Liberadas') throw new Error(id+' não está liberada.');
  const e=osIniErro(o,o.req&&c.reqs[o.req]); if(e) throw new Error(e.t);
  o.etapa='Em execução';
  return {msg:id+' em execução. Registre o apontamento de cada turno.'}; }
// apontamento pela web: mesma regra do app (consumo = dose × área baixa a custódia; nunca acima do que foi entregue)
function osc_apontar(c,id,d,ha){ const o=osc_o(c,id); if(o.etapa!=='Em execução') throw new Error(id+' não está em execução.');
  if(!(ha>0)) throw new Error('Informe a área feita (maior que 0 ha).'); if(ha>o.saldo+1e-9) throw new Error('Máximo '+cenNum(o.saldo)+' ha: é o saldo da ordem.');
  const pap=osApPend(o); if(ha>o.saldo-pap+1e-9) throw new Error('Máximo '+cenNum(o.saldo-pap)+' ha: '+cenNum(pap)+' ha do app aguardam sinal.');
  const cons={}; (o.ins||[]).forEach(x=>{ cons[x.p]=x.dose*ha; }); const r=o.req&&c.reqs[o.req];
  if(r) for(const it of r.itens){ const q=cons[it.prod]||0; if(q>it.custodia+1e-9) throw new Error('Consumo de '+it.prod+' ('+cenNum(q)+' '+it.un+') acima do que está em custódia ('+cenNum(it.custodia)+' '+it.un+'). Confira a entrega no Estoque.'); }
  if(r) r.itens.forEach(it=>{ const q=cons[it.prod]||0; it.consumido+=q; it.custodia-=q; });
  const feitos=(o.ap||[]).filter(a=>a.st!=='Previsto'); const prev=(o.ap||[]).filter(a=>a.st==='Previsto').slice(1).map((x,i)=>Object.assign({},x,{dia:feitos.length+2+i}));
  const dia=feitos.length+1; o.realizado+=ha; o.saldo=Math.max(0,o.saldo-ha);
  o.ap=feitos.concat([{d,dia,ha,st:'Provisório',cons,origem:'web',sinc:true}]).concat(o.saldo>0?prev:[]);
  const ins=(o.ins||[]).map(x=>x.p+' '+nd(x.dose*ha)+' '+x.un).join(', ');
  return {msg:'Apontamento do dia '+dia+': '+nd(ha)+' ha (provisório)'+(ins?' · usado: '+ins:'')+'. Saldo '+nf(o.saldo)+' ha; a ordem continua em execução.'}; }
function osc_conferencia(c,id){ const o=osc_o(c,id); if(o.etapa!=='Em execução') throw new Error(id+' não está em execução.');
  if(o.area&&o.saldo>0.001) throw new Error('Ainda há '+cenNum(o.saldo)+' ha de saldo.'); o.etapa='Em conferência'; o.selos=[];
  return {msg:id+' enviada para conferência.'}; }
// encerrar: só com apontamentos enviados e nada em custódia (cenPodeEncerrar); os apontamentos passam a conferidos
function osc_encerrar(c,id){ const o=osc_o(c,id); if(o.etapa!=='Em conferência') throw new Error(id+' não está em conferência.');
  const m=cenPodeEncerrar(c,id); if(m) throw new Error('Encerrar bloqueado: '+m);
  o.etapa='Encerradas'; o.selos=[]; (o.ap||[]).forEach(a=>{ if(a.st==='Provisório') a.st='Conferido'; });
  return {msg:id+' encerrada.'}; }
// cancelar sem execução: a reserva ainda não entregue volta ao disponível do lote e a requisição fica cancelada
function osc_cancelar(c,id,mot,cx){ const o=osc_o(c,id);
  if((o.realizado||0)>0||['A liberar','Liberadas'].indexOf(o.etapa)<0) throw new Error('Só ordem sem realizado, em A liberar ou Liberadas, é cancelada sem execução.');
  const r=o.req&&c.reqs[o.req];
  if(r){ if(o.reservado) r.itens.forEach(it=>{ const l=c.lotes[it.prod+'|'+it.lote]; const res=Math.max(0,it.solicitado-it.entregue); if(l&&res>0) l.reservado=Math.max(0,l.reservado-res); }); r.estado='Cancelada'; }
  o.etapa='Canceladas'; o.reservado=false; o.selos=[]; osc_txt(o,{cond:'Cancelada sem execução: '+mot+'. '+cx[1],dono:'',prazo:'',insx:cx[2]});
  return {msg:id+' cancelada sem execução. '+cx[1]}; }
function osc_dispensar(c,id,n,mot){ const o=osc_o(c,id); if(o.etapa!=='Em execução') throw new Error(id+' não está em execução.');
  if(n>o.saldo+0.001) throw new Error('Máximo '+cenNum(o.saldo)+' ha: é o saldo da ordem.');
  const tot=(o.osc.disp||0)+n; o.saldo=Math.max(0,o.saldo-n); o.ap=cortaPrev(o.ap,o.saldo);
  osc_txt(o,{disp:tot,cond:'Saldo de '+nd(n)+' ha dispensado: '+mot+' · validação agronômica registrada. Realizado de '+nf(o.realizado)+' ha preservado.',dono:'',prazo:''});
  return {msg:'Dispensados '+nd(n)+' ha da '+id+' · realizado '+nf(o.realizado)+' ha preservado · saldo '+nf(o.saldo)+' ha.'+(o.saldo<=0.001?' Envie a ordem para conferência.':'')}; }
// nova ordem: entra no cenário em A liberar com os insumos da atividade do plano (dose × área) e sem requisição; os textos da tela ficam em osc.novo
function osc_nova(c,no){ if(c.ordens[no.id]) throw new Error(no.id+' já existe.');
  const ins=(no.ins||[]).map(x=>({p:x.p,dose:x.dose,un:x.un,tot:x.tot,emb:(OSD.nova.emb||{})[x.p]||''}));
  c.ordens[no.id]={id:no.id,tipo:no.tipo,talhao:no.talhao,area:no.area,etapa:'A liberar',versao:no.versao,aprov:false,realizado:0,saldo:no.area,resp:no.resp,ins,req:null,selos:no.selos,ap:[],reservado:false,osc:{novo:no}};
  return {msg:no.id+' emitida em A liberar · enviada ao agrônomo. Não foi liberada para execução.'}; }
// filtros do topo (Fazenda e Safra): lista, Kanban, chips de fase e selo do cabeçalho mostram só as ordens do recorte
function mfFaz(self){ return self.state.mf_faz||'Santa Rita'; }
function mfSaf(self){ return self.state.mf_saf||'Todas'; }
function vis(self){ const f=mfFaz(self), s=mfSaf(self); return ords(self).filter(o=>(f==='Todas'||o.faz===f)&&(s==='Todas'||o.saf===s)); }
function localTxt(o){ return o.talhao+(o.area?' · '+nf(o.area)+' ha':'')+(o.lam?' · '+o.lam:''); }
function acum(o){ let conf=0,prov=0,sem=0; (o.ap||[]).forEach(a=>{ if(a.sinc===false) sem+=a.ha; else if(a.st==='Conferido') conf+=a.ha; else if(a.st==='Provisório') prov+=a.ha; }); return {conf,prov,sem}; }
function realTxt(o){ return o.area? (nf(o.realizado)+' / '+nf(o.area)+' ha') : '—'; }
function pctTxt(o){ return (o.area&&(o.realizado||0)>0)?' · '+Math.round(100*o.realizado/o.area)+' %':''; }
function salTxt(o){ return 'saldo '+nf(o.saldo)+' ha'+(o.disp?' · dispensado '+nf(o.disp)+' ha':''); }
function brd(s){ if(!s) return ''; const a=s.split('-'); return a[2]+'/'+a[1]+'/'+a[0]; }
// canceladas ficam fora da lista e do quadro; aparecem só no chip "Canceladas"
function vendoCanc(self){ return ((((g2st(self,'g_os').f||{}).fase)||[]).indexOf('Canceladas'))>=0; }
function PREVALS(self,v){
  cenOuvir(self);  // Estoque e App (outros quadros) mudam o cenário: a tela redesenha sem recarregar
  const canc=vendoCanc(self); const os=vis(self).filter(o=>o.etapa!=='Canceladas'||canc);
  GR('g_os').rows=os.map(o=>({id:o.id,
    v:{id:o.id,ativ:o.tipo,jan:o.janela,fase:o.etapa,cond:o.selos.map(s=>s.t).join(' · '),real:(o.area?o.realizado:null),resp:o.resp},
    s:{id:o.id,ativ:o.tipo+' '+localTxt(o),cond:(o.selos.length?o.selos.map(s=>s.t).join(' · '):'—')+(o.obs?' '+o.obs:''),real:realTxt(o)+pctTxt(o)+(o.area?' '+salTxt(o):'')},
    p:{id:[{k:'b',t:o.id}],ativ:[{k:'txt',t:o.tipo},{k:'br'},{k:'mut',t:localTxt(o)}],fase:[{k:'chip',t:o.etapa,c:FCOR[o.etapa]}],
       cond:(o.selos.length?o.selos.map(s=>({k:'chip',t:s.t,c:s.c})):[{k:'mut',t:'—'}]).concat(o.obs?[{k:'br'},{k:'mut',t:o.obs}]:[]).concat(o.dono?[{k:'br'},{k:'mut',t:o.dono+' · '+o.prazo}]:[]),
       real:(o.area?[{k:'txt',t:nf(o.realizado)+' / '+nf(o.area)+' ha'+pctTxt(o)},{k:'br'},{k:'mut',t:'saldo '+nf(o.saldo)+' ha'}]
         .concat(o.disp?[{k:'br'},{k:'mut',t:'dispensado '+nf(o.disp)+' ha'}]:[]):[{k:'mut',t:'—'}])}}));
}
// turnos previstos acompanham o saldo depois de uma dispensa (corta do último para o primeiro)
function cortaPrev(ap,sal){ let rest=sal; const prev=(ap||[]).filter(x=>x.st==='Previsto'); const keep={};
  prev.forEach((x,i)=>{ const ha=Math.max(0,Math.min(x.ha,rest)); rest-=ha; keep[i]=ha; });
  let i=-1; return (ap||[]).map(x=>{ if(x.st!=='Previsto') return x; i++; return keep[i]>0?Object.assign({},x,{ha:keep[i]}):null; }).filter(Boolean); }
function nd(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:(d===undefined?2:d)}); }
// período da coluna Encerradas: da primeira à última data (janela e apontamentos feitos) das ordens da coluna
function osPeriodo(cs){ const ds=[]; const add=(d,m)=>ds.push([Number(m),Number(d)]); const z=(n)=>('0'+n).slice(-2);
  cs.forEach(o=>{ const j=String(o.janela||''); const r=/(\d{1,2})–(\d{1,2})\/(\d{2})/.exec(j);
    if(r){ add(r[1],r[3]); add(r[2],r[3]); } else { const s=/(\d{1,2})\/(\d{2})/.exec(j); if(s) add(s[1],s[2]); }
    (o.ap||[]).forEach(a=>{ if(a.st==='Previsto') return; const s=/(\d{1,2})\/(\d{2})/.exec(a.d||''); if(s) add(s[1],s[2]); }); });
  if(!ds.length) return ''; ds.sort((a,b)=>a[0]-b[0]||a[1]-b[1]); const a=ds[0], b=ds[ds.length-1];
  if(a[0]===b[0]&&a[1]===b[1]) return 'em '+z(a[1])+'/'+z(a[0]);
  return 'período '+z(a[1])+(a[0]===b[0]?'':'/'+z(a[0]))+'–'+z(b[1])+'/'+z(b[0]); }
// tela de trabalho da ordem: atividade, insumos e doses, e o botão do próximo passo da fase
function osWork(self,v,o){ const st=self.state; const a=o.atv||{};
  const kv=[['Operação',a.op||'—'],['Atividade',a.nome||o.tipo],['Gatilho',a.gat||'—'],['Local · área',o.talhao+(o.area?' · '+nf(o.area)+' ha':'')],['Janela',o.janela],['Responsável',o.resp]];
  if(a.conj){ kv.push(['Conjunto',a.conj+' · '+nd(a.rend)+' ha/h']); if(o.area) kv.push(['Horas previstas',nd(o.area/a.rend,1)+' h ('+nd((o.saldo||0)/a.rend,1)+' h no saldo)']); }
  kv.push(['Padrão · versão',[a.orig||'—'].concat(String(o.versao).split(' · ').filter(p=>(a.orig||'').indexOf(p)<0)).join(' · ')+(o.recibo?' · recibo '+o.recibo.id:'')]);  // sem repetir a recomendação
  v.pan_atv=kv.map(x=>({l:x[0],v:x[1]}));
  // insumos: usado = consumido pelos apontamentos (cenário); situação e trilha do almoxarifado ao app, por item da requisição
  v.pan_ins=(o.ins||[]).map(x=>{ const it=(o.r&&o.etapa!=='Canceladas')?(o.r.itens.find(i=>i.prod===x.p)||null):null;
    const usado=it?it.consumido:((o.id==='OS-0417')?x.tot:(o.area?x.dose*(o.realizado||0):0)); const tr=osTrilha(o,it);
    return {p:x.p,g:x.g,dose:nd(x.dose)+' '+x.un+'/ha',tot:nd(x.tot)+' '+x.un,usado:(usado?nd(usado)+' '+x.un:'—'),sit:osInsSit(o,x,it),tr,hasTr:tr.length>0}; });
  v.pan_rec=((OSD.aloc||{})[o.id]||[]).map(r=>({t:r.tipo+' · '+r.nome,j:r.janelas,cond:!!r.cond,al:(r.alertas||[]).map(t=>({t})),hasAl:(r.alertas||[]).length>0}));
  v.pan_hasRec=v.pan_rec.length>0;
  const EQ={'Pulverização':{cap:3000,un:'L',vaz:100,nome:'tanque útil 3.000 L · 100 L/ha'},'Adubação a lanço':{cap:3000,un:'kg',nome:'distribuidor 3.000 kg'}}[a.op];
  const areaP=(o.etapa==='Em execução')?(o.saldo||0):(o.area||0);
  let prep=''; if(EQ&&areaP>0&&(o.ins||[]).length){ const ac=EQ.vaz?EQ.cap/EQ.vaz:EQ.cap/(o.ins.reduce((t,x)=>t+x.dose,0)||1); const n=Math.ceil(areaP/ac-1e-9); const ult=areaP-ac*(n-1);
    prep=n+(n>1?' cargas':' carga')+' ('+EQ.nome+'): '+nd(ac,1)+' ha por carga'+(ult<ac-1e-9?'; última '+nd(ult,1)+' ha':'')+' · '+(o.ins||[]).map(x=>x.p+' '+nd(x.dose*ac,1)+' '+x.un+' por carga').join(', ')+(o.etapa==='Em execução'?' (saldo de '+nf(o.saldo)+' ha)':''); }
  v.pan_prep=prep; v.pan_hasPrep=!!prep&&['Liberadas','Em execução'].indexOf(o.etapa)>=0;
  v.pan_fichas=o.id==='OS-0424';
  // retirada: o link ao almoxarifado só enquanto houver saldo a entregar; entregue e confirmado, ficam só as fichas de carga
  const exe=(o.ins||[]).length>0&&['Liberadas','Em execução'].indexOf(o.etapa)>=0;
  v.pan_retLink=exe&&(!o.r||!o.r.itens.length||o.r.itens.some(i=>cenSaldoEntregar(i)>1e-6));
  v.pan_hasRet=exe&&(v.pan_retLink||v.pan_hasPrep||v.pan_fichas); v.pan_retT=v.pan_retLink?'Retirada e fichas de execução':'Fichas de execução';
  v.pan_hasIns=v.pan_ins.length>0; v.pan_semIns=!v.pan_hasIns; v.pan_semInsT=o.semins||'Sem insumos: a atividade é só operação.';
  // próximo passo por fase
  let P; const temIns=(o.ins||[]).length>0;
  if(o.etapa==='A liberar') P=o.rej?{t:'Versão rejeitada: '+o.rej+'. O PCP ajusta a ordem ou a cancela.',btn:'',fn:''}
      :o.agua?{t:'Água sem produto: libere pela prontidão operacional (janela, bomba, energia e sem conflito).',btn:'Liberar para execução',fn:'liberar'}
      :(!o.aprov?{t:'Revise a versão '+o.versao+': atividade, área'+(temIns?', produtos e doses':'')+' abaixo. Aprovar não libera para execução.',btn:'Revisar versão',fn:'revisar'}
      :{t:'Versão aprovada. Libere para execução: '+(temIns?'os insumos são reservados no Estoque.':'sem insumos a reservar.'),btn:'Liberar para execução',fn:'liberar'});
  else if(o.etapa==='Liberadas') P={t:'Confira máquina, equipe e insumos e inicie a execução na janela '+o.janela+'.',btn:'Iniciar execução',fn:'iniciar'};
  else if(o.etapa==='Em execução') P=(o.area&&(o.saldo||0)<=0.001)?{t:'A área toda foi feita. Envie a ordem para conferência.',btn:'Enviar para conferência',fn:'conferencia'}
      :{t:'Registre o apontamento do turno: data e área feita. Os insumos usados são calculados pela dose. Fechar o turno não encerra a ordem.',btn:'Registrar apontamento',fn:'apontar'};
  else if(o.etapa==='Em conferência') P={t:'Confira apontamentos, consumo e sobras e encerre a ordem.',btn:'Conferir e encerrar',fn:'encerrar'};
  else if(o.etapa==='Canceladas') P={t:'Ordem cancelada sem execução: somente consulta.',btn:'',fn:''};
  else P={t:'Ordem encerrada: somente consulta.',btn:'',fn:''};
  // impedimento do próximo passo: do registro (máquina, janela, conflito) ou do cenário (saldo no Estoque; sinal ou sobra no encerramento)
  let b=(o.bloq&&o.bloq.fase===o.etapa&&o.bloq.acao===P.fn)?o.bloq:null;
  if(!b&&P.fn==='liberar'&&!o.agua){ const e=o.libErr||''; if(e) b={acao:'liberar',t:'Liberar bloqueado: '+e.charAt(0).toLowerCase()+e.slice(1),q:'Suprimentos, recebendo o insumo no Estoque.',h:'EST.dc.html',hl:'Ver saldos no Estoque'}; }
  if(!b&&P.fn==='encerrar'&&o.encM) b=osEncBloq(o);
  if(!b&&P.fn==='iniciar'&&!o.agua) b=osIniErro(o,o.r);
  v.pan_dono=(!b&&o.dono)?('Pendência com '+o.dono+' · '+o.prazo):''; v.pan_hasDono=!!v.pan_dono;
  v.pan_pt=P.t; v.pan_pbtn=P.btn; v.pan_hasBtn=!!P.btn&&!b; v.pan_bloq=!!b; v.pan_bt=b?b.t:''; v.pan_bq=b?('Quem resolve: '+b.q):'';
  v.pan_hasBl=!!(b&&b.h); v.pan_bh=(b&&b.h)||'#'; v.pan_bhl=(b&&b.hl)||'';
  if(v.pan_retLink&&b&&b.h==='EST.dc.html'){ v.pan_retLink=false; v.pan_retT='Fichas de execução'; v.pan_hasRet=v.pan_hasPrep||v.pan_fichas; }  // o impedimento já leva ao Estoque: sem link duplicado
  v.pan_aviso=(o.aviso&&o.etapa==='Liberadas')?o.aviso:''; v.pan_hasAviso=!!v.pan_aviso;
  v.pan_obs=o.obs?(o.obs.charAt(0).toUpperCase()+o.obs.slice(1)+' (não bloqueia).'):''; v.pan_hasObs=!!o.obs&&o.etapa==='A liberar';
  const bam=b&&b.tone==='yellow';  // pendência que não é impedimento (ex.: janela a definir) fica amarela
  v.pan_btst='font-size:13px;font-weight:700;line-height:1.45;color:'+(bam?'#8A5A00':'#B42318')+';';
  v.pan_pst='display:flex;flex-direction:column;gap:8px;padding:12px 14px;border-radius:12px;'+(b?(bam?'background:#FFF3D6;border:1px solid #F0D9A0;':'background:#FDE8E6;border:1px solid #F4C7C1;'):(P.btn?'background:#E4F3E9;border:1px solid #BFE0CB;':'background:#F4F6F3;border:1px solid #E4E9E5;'));
  const pa=(st.pa&&st.pa.id===o.id)?st.pa:null;
  const apP=osApPend(o), apMax=Math.max(0,(o.saldo||0)-apP);
  v.pan_go=()=>{ if(P.fn==='apontar'){ const prox=(o.ap||[]).find(x=>x.st==='Previsto'); self.setState({pa:{id:o.id,fn:'apontar',d:'2026-09-26',ha:String(Math.min(apMax,prox?prox.ha:apMax)).replace('.',','),err:''}}); return; } self.setState({pa:{id:o.id,fn:P.fn}}); };
  v.pan_conf=!!pa&&['liberar','iniciar','conferencia','encerrar'].indexOf(pa.fn)>=0; v.pan_apf=!!pa&&pa.fn==='apontar'; v.pan_rev=!!pa&&pa.fn==='revisar'; v.pan_idle=!pa;
  v.pan_canf=!!pa&&pa.fn==='cancelar'; v.pan_disf=!!pa&&pa.fn==='dispensar';
  v.pan_rmot=(pa&&pa.motivo)||''; v.pan_rerr=(pa&&pa.err)||''; v.pan_hasRerr=!!(pa&&pa.err);
  v.pan_setrmot=(e)=>self.setState({pa:Object.assign({},self.state.pa,{motivo:e.target.value,err:''})});
  const decide=(k)=>()=>{ const cur=self.state.pa; const mot=String(cur.motivo||'').trim();
    if(k!=='aprovar'&&!mot){ self.setState({pa:Object.assign({},cur,{err:'Informe o motivo.'})}); return; }
    osRun(self,c=>osc_decidir(c,o.id,k,mot),{pa:null}); };
  v.pan_raprov=decide('aprovar'); v.pan_rdev=decide('devolver'); v.pan_rrej=decide('rejeitar');
  const insTxt=(o.ins||[]).map(x=>x.p+' '+nd(x.tot)+' '+x.un).join(', ');
  v.pan_ct={liberar:o.agua?('Liberar '+o.id+': janela, bomba e energia confirmadas; água sem requisição no Estoque.'):('Liberar '+o.id+' (versão '+o.versao+'): '+(insTxt?'a requisição reserva no Estoque, por lote: '+insTxt+'.':'sem insumos a reservar; nenhuma requisição no Estoque.')),iniciar:'Iniciar '+o.id+' agora, na janela '+o.janela+(o.r&&(o.ins||[]).length?': insumos com '+o.resp+', confirmados no app.':'.'),
    conferencia:'Enviar '+o.id+' para conferência: execução física concluída ('+nf(o.realizado)+' ha).',encerrar:'Encerrar '+o.id+': apontamentos enviados, consumo baixado e nada em custódia.'}[pa?pa.fn:'']||'';
  v.pan_cbtn={liberar:'Confirmar liberação',iniciar:'Confirmar início',conferencia:'Confirmar envio',encerrar:'Confirmar encerramento'}[pa?pa.fn:'']||'';
  v.pan_back=()=>self.setState({pa:null});
  v.pan_yes=()=>{ const F={liberar:c=>osc_liberar(c,o.id,o.agua,o.janela),iniciar:c=>osc_iniciar(c,o.id),conferencia:c=>osc_conferencia(c,o.id),encerrar:c=>osc_encerrar(c,o.id)}[pa.fn];
    if(F) osRun(self,F,{pa:null}); };
  v.pan_ad=pa&&pa.d||''; v.pan_aha=pa&&pa.ha||''; v.pan_aerr=pa&&pa.err||''; v.pan_hasAerr=!!(pa&&pa.err);
  v.pan_asub='Saldo da ordem: '+nf(o.saldo)+' ha'+(apP>0?' · '+nf(apP)+' ha no aparelho aguardando sinal':'');
  v.pan_setad=(e)=>self.setState({pa:Object.assign({},self.state.pa,{d:e.target.value,err:''})}); v.pan_setaha=(e)=>self.setState({pa:Object.assign({},self.state.pa,{ha:e.target.value,err:''})});
  v.pan_asave=()=>{ const cur=self.state.pa; const n=g2num(cur.ha);
    if(!cur.d){ self.setState({pa:Object.assign({},cur,{err:'Informe a data do turno.'})}); return; }
    if(isNaN(n)||n<=0){ self.setState({pa:Object.assign({},cur,{err:'Informe a área feita (maior que 0 ha).'})}); return; }
    if(n>(o.saldo||0)+0.001){ self.setState({pa:Object.assign({},cur,{err:'Máximo '+nf(o.saldo)+' ha: é o saldo da ordem.'})}); return; }
    if(n>apMax+0.001){ self.setState({pa:Object.assign({},cur,{err:'Máximo '+nf(apMax)+' ha: '+nf(apP)+' ha do app aguardam sinal.'})}); return; }
    const d=cur.d.split('-'); osRun(self,c=>osc_apontar(c,o.id,d[2]+'/'+d[1],n),{pa:null}); };
  // ação secundária pelo realizado: sem realizado → cancelar sem execução; em execução → dispensar saldo (nunca cancela fato executado)
  const canCanc=!((o.realizado||0)>0)&&(o.etapa==='A liberar'||o.etapa==='Liberadas');
  const canDisp=o.etapa==='Em execução'&&!!o.area&&(o.saldo||0)>0.001;
  v.pan_hasCanc=canCanc; v.pan_hasDisp=canDisp;
  v.pan_cango=()=>self.setState({pa:{id:o.id,fn:'cancelar',motivo:'',err:''}});
  v.pan_disgo=()=>self.setState({pa:{id:o.id,fn:'dispensar',ha:String(o.saldo).replace('.',','),motivo:'',val:false,err:''}});
  // (confirmação, aviso final, nova situação do insumo): a seção Insumos acompanha o que o aviso diz
  const cx=o.canc||((o.reservado&&insTxt)?['Libera a reserva no Estoque: '+insTxt+'.','Reserva liberada no Estoque: '+insTxt+'.','Reserva liberada no Estoque']:((o.ins||[]).length?['Nenhum insumo foi reservado.','Nenhum insumo estava reservado.','Nada reservado · ordem cancelada']:['','','']));
  v.pan_cct='Cancelar '+o.id+' sem execução: a ordem sai do quadro e fica em Canceladas. '+cx[0];
  v.pan_cansave=()=>{ const cur=self.state.pa; const mot=String(cur.motivo||'').trim();
    if(!mot){ self.setState({pa:Object.assign({},cur,{err:'Informe o motivo do cancelamento.'})}); return; }
    osRun(self,c=>osc_cancelar(c,o.id,mot,cx),{pa:null}); };
  const lim=(o.area||0)*LIM_DISP;
  v.pan_dsub='Até 20 % da área ('+nd(lim,1)+' ha) sem alçada; acima disso, exige Direção. O realizado de '+nf(o.realizado)+' ha fica preservado.';
  v.pan_dval=!!(pa&&pa.val); v.pan_setdval=(e)=>self.setState({pa:Object.assign({},self.state.pa,{val:!!e.target.checked,err:''})});
  v.pan_dissave=()=>{ const cur=self.state.pa; const n=g2num(cur.ha); const mot=String(cur.motivo||'').trim(); const tot=(o.disp||0)+n;
    const err=(m)=>self.setState({pa:Object.assign({},cur,{err:m})});
    if(isNaN(n)||n<=0) return err('Informe a área a dispensar (maior que 0 ha).');
    if(n>(o.saldo||0)+0.001) return err('Máximo '+nf(o.saldo)+' ha: é o saldo da ordem.');
    if(tot>lim+0.001) return err(nd(tot)+' ha = '+nd(100*tot/o.area,1)+' % acima de 20 % · exige Direção.');
    if(!mot) return err('Informe o motivo da dispensa.');
    if(!cur.val) return err('Marque a validação agronômica.');
    osRun(self,c=>osc_dispensar(c,o.id,n,mot),{pa:null}); };
}
function EXTRAVALS(self,v){
  const st=self.state, all=ords(self), os=vis(self);
  all.forEach(o=>{ v['op_'+o.id.replace('-','')]=()=>self.setState({pan:o.id,pa:null}); });
  self.g2pick=(gid,rid)=>{ if(gid==='g_os') self.setState({pan:rid}); };
  const openPan=(id)=>self.setState({pan:id});
  // estado vazio do recorte: uma frase e uma ação que troca o filtro que zerou a tela
  const fz=mfFaz(self), sf=mfSaf(self), semFaz=!all.some(o=>fz==='Todas'||o.faz===fz);
  v.os_vazio=os.length===0; v.os_tem=!v.os_vazio;
  v.os_vt=semFaz?('Nenhuma ordem na '+fz):('Nenhuma ordem na safra '+sf);
  v.os_va=semFaz?'Ver Santa Rita':'Ver todas as safras';
  v.os_vgo=()=>self.setState(semFaz?{mf_faz:'Santa Rita',g2toast:'Fazenda: Santa Rita'}:{mf_saf:'Todas',g2toast:'Safra: Todas'});
  // selo do cabeçalho: recalculado do estado (cancelar, iniciar ou enviar para conferência muda as contagens)
  const nEx=os.filter(o=>o.etapa==='Em execução').length;
  const nIm=os.filter(o=>o.etapa!=='Canceladas'&&o.selos.some(s=>/impedida|falta máquina|falta insumo/i.test(s.t))).length;
  v.os_st=nEx+' em execução · '+(nIm?nIm+' impedida'+(nIm!==1?'s':''):'nenhuma impedida');
  const stc=nIm?'red':(nEx?'green':'gray');  // vermelho só com impedidas (mesma cor do estado nas outras telas)
  v.os_stst=chipSt(stc).replace('padding:2px 9px;','padding:3px 10px;'); v.os_stdot=dotSt(stc);
  // ---- chips de fase (filtro real da grade: mesma chave do filtro da coluna Fase) ----
  const gst=g2st(self,'g_os'); const ff=((gst.f||{}).fase)||[];
  const chip=(t,n,on,fn)=>({t,n,on:on?'true':'false',fn,st:'display:inline-flex;align-items:center;gap:7px;font-family:inherit;font-size:12.5px;font-weight:700;padding:6px 12px;border-radius:999px;cursor:pointer;white-space:nowrap;'+(on?'border:1px solid #15201A;background:#15201A;color:#fff;':'border:1px solid #E4E9E5;background:#FFFFFF;color:#15201A;'),
    nst:'font-size:11.5px;font-weight:800;padding:0 7px;border-radius:999px;'+(on?'background:rgba(255,255,255,.2);color:#fff;':'background:#EEF1EE;color:#15201A;')});
  const setF=(f)=>()=>{ const cur=Object.assign({},g2st(self,'g_os').f||{}); if(f) cur.fase=[f]; else delete cur.fase; g2set(self,'g_os',{f:cur,fmc:null}); };
  v.fchips=[chip('Todas',os.filter(o=>o.etapa!=='Canceladas').length,ff.length===0,setF(null))].concat(FASES.concat(['Canceladas']).map(f=>chip(f,os.filter(o=>o.etapa===f).length,ff.length===1&&ff[0]===f,setF(f))));
  // ---- Kanban: cinco colunas fixas; selos no cartão ----
  v.kb=FASES.map(f=>{ const cs=os.filter(o=>o.etapa===f); const sal=cs.filter(o=>o.area).reduce((s,o)=>s+(o.saldo||0),0);
    return {t:f,n:String(cs.length),nst:chipSt(FCOR[f]),carga:(f==='Encerradas'?osPeriodo(cs):(sal?'saldo '+nf(sal)+' ha':'')),vazio:cs.length===0,
      cards:cs.map(o=>{ const pct=o.area?Math.round(100*(o.realizado||0)/o.area):0;
        const ini=!!o.area&&(o.realizado||0)>0;
        return {id:o.id,tipo:o.tipo,local:localTxt(o),obs:o.obs||'',hasObs:!!o.obs,real:(ini?nf(o.realizado)+'/'+nf(o.area)+' ha · '+pct+' % · '+salTxt(o):(o.area?'':'sem área · ordem de processo')),
          hasReal:!(o.area&&!ini),hasBar:ini,bar:'display:block;height:100%;border-radius:999px;background:'+(o.selos.some(s=>s.c==='red')?'#B42318':'#1E7A4C')+';width:'+pct+'%;',
          selos:o.selos.map(s=>({t:s.t,st:chipSt(s.c).replace('white-space:nowrap;','white-space:normal;line-height:1.3;align-items:baseline;').replace('border-radius:999px;','border-radius:8px;'),dot:dotSt(s.c)+'transform:translateY(-1px);'})),meta:o.resp+' · '+o.janela,dp:(o.dono?o.dono+' · '+o.prazo:''),hasDp:!!o.dono,lab:'Abrir '+o.id+' · '+o.tipo,
          st:'display:flex;flex-direction:column;gap:6px;text-align:left;width:100%;box-sizing:border-box;background:#FFFFFF;border-radius:10px;padding:9px 10px;cursor:pointer;font-family:inherit;color:#15201A;'+(st.pan===o.id?'border:2px solid #1E7A4C;':'border:1px solid #E4E9E5;box-shadow:0 1px 2px rgba(21,32,26,.05);'),
          open:()=>openPan(o.id), key:(e)=>{ if(e&&(e.key==='Enter'||e.key===' ')){ e.preventDefault(); openPan(o.id); } }}; })}; });
  // ---- painel lateral de consulta ----
  const o=st.pan?all.find(x=>x.id===st.pan):null; v.pan_open=!!o;
  const close=()=>self.setState({pan:null});
  v.pan_close=close; v.pan_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); close(); } };
  if(o){ const a=acum(o);
    v.pan_t=o.id+' · '+o.tipo; v.pan_fase=o.etapa; v.pan_fst=chipSt(FCOR[o.etapa]); v.pan_fdot=dotSt(FCOR[o.etapa]);
    v.pan_selos=o.selos.map(s=>({t:s.t,st:chipSt(s.c),dot:dotSt(s.c)}));
    const cur=FASES.indexOf(o.etapa);
    v.pan_steps=FASES.map((f,i)=>({t:f,cur:i===cur?'step':'false',st:'display:flex;flex-direction:column;gap:5px;font-size:11.5px;font-weight:'+(i===cur?'800':'600')+';color:'+(i<=cur?'#15201A':'#8A968E')+';',
      bst:'height:5px;border-radius:999px;background:'+(i<cur?'#9CCBB0':(i===cur?'#1E7A4C':'#E4E9E5'))+';'}));
    const kv=[['Local',o.talhao],['Janela',o.janela],['Responsável',o.resp],['Versão · autorização',o.versao+(o.recibo?' · recibo '+o.recibo.id:'')]];
    if(o.area){ kv.splice(1,0,['Área autorizada',nf(o.area)+' ha'],['Realizado',nf(o.realizado)+' ha'+((a.conf||a.prov)?' ('+nf(a.conf)+' conf. + '+nf(a.prov)+' prov.)':'')+(a.sem?' · '+nf(a.sem)+' ha aguardando sinal':'')],['Saldo',nf(o.saldo)+' ha']); }    v.pan_kv=kv.map(x=>({l:x[0],v:x[1]}));
    // apontamentos: os do app mostram a origem; sem sinal ficam "Aguardando sinal" e não entram no acumulado
    let ac=0; v.pan_ap=(o.ap||[]).map(x=>{ const prev=x.st==='Previsto'; const sem=x.sinc===false; if(!prev&&!sem) ac+=x.ha; const s=sem?'Aguardando sinal':x.st;
      return {d:x.d,dia:'Dia '+x.dia+(x.origem==='app'?' · app':''),ha:(prev?'prev. ':'')+nf(x.ha)+' ha'+(x.h?' · '+nd(x.h,1)+' h':''),ac:(prev?'—':(sem?'não somado':nf(ac)+' / '+nf(o.area)+' ha')),t:s,st:chipSt(STCOR[s]),dot:dotSt(STCOR[s]),rst:prev?'color:#8A968E;':''}; });
    v.pan_hasAp=v.pan_ap.length>0; v.pan_noAp=!v.pan_hasAp;
    v.pan_noApT=o.area?(o.etapa==='A liberar'||o.etapa==='Liberadas'?'Sem apontamentos: a ordem ainda não foi iniciada.':'Sem apontamentos registrados.'):'Ordem de processo: entradas e saídas são registradas por etapa do beneficiamento, não por área.';
    v.pan_acum=!o.area?'':(o.disp?('Realizado '+nf(o.realizado)+' ha · Dispensado '+nf(o.disp)+' ha · Saldo '+nf(o.saldo)+' ha (de '+nf(o.area)+' ha)')
      :('Acumulado '+nf(o.realizado)+' / '+nf(o.area)+' ha · saldo '+nf(o.saldo)+' ha'))+(a.sem?' · '+nf(a.sem)+' ha no aparelho aguardando sinal':''); v.pan_hasAcum=!!o.area&&v.pan_hasAp;
    v.pan_nota=o.nota||''; v.pan_hasNota=!!o.nota;
    v.pan_cond=o.cond; v.pan_orig=o.orig.map(t=>({t}));
    v.pan_link=o.link||'#'; v.pan_hasLink=!!o.link;
    osWork(self,v,o);
  }
  // ---- nova ordem (nasce A liberar; nunca liberada automaticamente) ----
  const nv=st.nv; v.nv_show=!!nv;
  v.nv_open=()=>self.setState({nv:{saf:'',cult:'',atv:'',jan:'',errs:{},warn:false},pan:null});
  if(nv){
    const upd=(patch)=>{ const cur=self.state.nv; const errs=Object.assign({},cur.errs||{}); Object.keys(patch).forEach(k=>delete errs[k]); self.setState({nv:Object.assign({},cur,patch,{errs,warn:false,dup:''})}); };
    // atividade que já tem ordem: o erro fica no campo e o botão abre a ordem existente (nada é emitido)
    v.nv_hasDup=!!nv.dup; v.nv_dupt='Abrir '+(nv.dup||''); v.nv_opendup=()=>self.setState({nv:null,pan:self.state.nv.dup});
    const cults=nv.saf?(OSD.nova.cult[nv.saf]||[]):[]; const c=cults.find(x=>x.id===nv.cult); const pl=c&&c.plano?OSD.nova.planos[c.plano]:null;
    v.nv_safs=[{v:'',t:'Selecione a safra'}].concat(OSD.nova.safs.map(s=>({v:s.id,t:s.t}))); v.nv_saf=nv.saf;
    v.nv_cults=[{v:'',t:nv.saf?'Selecione o cultivo':'Escolha a safra primeiro'}].concat(cults.map(x=>({v:x.id,t:x.t}))); v.nv_cult=nv.cult; v.nv_cultdis=!nv.saf;
    v.nv_atvs=[{v:'',t:(!c?'Escolha o cultivo primeiro':(pl?'Selecione a atividade':'Cultivo sem plano aplicado'))}].concat(pl?pl.atv.map(a=>({v:a.id,t:a.nome+' · '+a.op})):[]); v.nv_atv=nv.atv; v.nv_atvdis=!pl;
    v.nv_noplan=!!c&&!pl; v.nv_jan=nv.jan;
    v.nv_area=c?('Área da ordem: '+nf(c.area)+' ha · '+c.local+(pl?' · plano '+pl.nome+' v'+pl.versao:'')):''; v.nv_hasArea=!!c;
    v.nv_setsaf=(e)=>upd({saf:e.target.value,cult:'',atv:''}); v.nv_setcult=(e)=>upd({cult:e.target.value,atv:''});
    v.nv_setatv=(e)=>upd({atv:e.target.value}); v.nv_setjan=(e)=>upd({jan:e.target.value});
    const E=nv.errs||{}; ['saf','cult','atv','jan'].forEach(k=>{ v['nv_e_'+k]=E[k]||''; v['nv_he_'+k]=!!E[k];
      v['nv_st_'+k]='font-family:inherit;font-size:14px;padding:9px 11px;border-radius:10px;box-sizing:border-box;width:100%;background:#FFFFFF;color:#15201A;border:1px solid '+(E[k]?'#B42318':'#E4E9E5')+';'; });
    v.nv_hasErr=Object.keys(E).length>0; v.nv_warn=!!nv.warn;
    const dirty=!!(nv.saf||nv.cult||nv.atv||nv.jan);
    v.nv_cancel=()=>{ if(dirty && !self.state.nv.warn){ self.setState({nv:Object.assign({},self.state.nv,{warn:true})}); return; } self.setState({nv:null}); };
    v.nv_discard=()=>self.setState({nv:null}); v.nv_keep=()=>self.setState({nv:Object.assign({},self.state.nv,{warn:false})});
    v.nv_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); v.nv_cancel(); } };
    v.nv_save=()=>{ const cur=self.state.nv; const errs={};
      if(!cur.saf) errs.saf='Escolha a safra.';
      if(!cur.cult) errs.cult='Escolha o cultivo.';
      if(cur.cult && !pl) errs.atv='Sem atividade disponível para este cultivo.';
      else if(!cur.atv) errs.atv='Escolha a atividade.';
      if(!cur.jan) errs.jan='Informe o início da janela.';
      const all=ords(self); let dupId='';
      if(!Object.keys(errs).length){ const k=cur.cult+'|'+cur.atv; const dup=all.find(x=>(x.keys||[]).indexOf(k)>=0&&x.etapa!=='Canceladas'); if(dup){ errs.atv='Já existe '+dup.id+' para esta atividade neste cultivo.'; dupId=dup.id; } }
      if(Object.keys(errs).length){ self.setState({nv:Object.assign({},cur,{errs,warn:false,dup:dupId})}); return; }
      const a=pl.atv.find(x=>x.id===cur.atv); const s=OSD.nova.safs.find(x=>x.id===cur.saf);
      const num=440+all.filter(x=>x.novo).length; const id='OS-0'+num;
      // insumos da atividade do plano: dose × área do cultivo (a semente leva a variedade do cultivo); nada é reservado antes de liberar
      const ins=(a.ins||[]).map(x=>({g:x.g,p:x.p.replace(/ · (variedade|híbrido) do cultivo$/,' '+c.var),dose:x.dose,un:x.un,tot:Math.round(x.dose*c.area*100)/100,sit:'Reserva ao liberar'}));
      const cj=(OSD.nova.conj||{})[a.op]||null;
      const no={id,novo:true,keys:[cur.cult+'|'+cur.atv],tipo:(a.op===a.nome?a.nome:a.op+' · '+a.nome),talhao:c.local,area:c.area,etapa:'A liberar',selos:[{t:'Aguardando agrônomo',c:'yellow'}],
        faz:'Santa Rita',saf:s.mf,lam:'',obs:'',agua:false,ins,semins:'',bloq:null,aviso:'',dono:'Ana (agrônoma)',prazo:'revisar a versão',
        atv:{op:a.op,nome:a.nome,gat:a.gat||'',orig:pl.nome+' v'+pl.versao,conj:cj?cj.conj:'',rend:cj?cj.rend:0},
        realizado:0,saldo:c.area,resp:'—',versao:'v1 emitida',janela:'a partir de '+brd(cur.jan),ap:[],nota:'',
        cond:'Revisão agronômica · Ana (agrônoma). Liberar para execução exige a versão aprovada e a prontidão de máquina, equipe e insumos.',
        orig:[s.t+' · cultivo '+c.local+' ('+nf(c.area)+' ha)','Plano '+pl.nome+' v'+pl.versao+' · atividade '+a.nome],link:''};
      osRun(self,c0=>osc_nova(c0,no),{nv:null,pan:id},(e)=>self.setState({g2toast:e})); };
  }
  // ---- restaurar a demonstração (cenário compartilhado com Estoque e App volta ao início) ----
  v.os_rst_no=!st.os_rst; v.os_rst_ask=!!st.os_rst;
  v.os_rst=()=>self.setState({os_rst:true}); v.os_rst_cancel=()=>self.setState({os_rst:false});
  v.os_rst_ok=()=>{ cenReset(); self.setState({os_rst:false,pan:null,pa:null,nv:null,cenrev:Date.now(),g2toast:'Demonstração restaurada: O.S., estoque e app voltaram ao início.'}); };
}
'''

def bloco(titulo,desc,corpo,acao=''):
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: center; gap: 12px; padding: 12px 16px 10px; flex-wrap: wrap;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{esc(titulo)}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>{acao}</div>'
            f'<div style="padding: 0 12px 12px; display: flex; flex-direction: column; gap: 10px;">{corpo}</div></section>')

def _chip_hole(t,st,dot):
    return f'<span style="{H(st)}"><span style="{H(dot)}"></span>{H(t)}</span>'

def _kanban():
    card=(f'<div role="button" tabIndex="0" aria-label="{H("k.lab")}" onClick="{H("k.open")}" onKeyDown="{H("k.key")}" style="{H("k.st")}">'
          f'<div style="display: flex; align-items: baseline; gap: 6px;"><b style="font-size: 13px;">{H("k.id")}</b></div>'
          f'<div style="font-size: 12.5px; font-weight: 600; line-height: 1.3;">{H("k.tipo")}</div>'
          f'<div style="font-size: 12px; color: {MUTED};">{H("k.local")}</div>'
          f'<sc-if value="{H("k.hasBar")}" hint-placeholder-val="{T()}"><span style="display: block; height: 6px; border-radius: 999px; background: {GRAYS}; overflow: hidden;"><span style="{H("k.bar")}"></span></span></sc-if>'
          f'<sc-if value="{H("k.hasReal")}" hint-placeholder-val="{T()}"><div style="font-size: 11.5px; color: {MUTED}; font-variant-numeric: tabular-nums;">{H("k.real")}</div></sc-if>'
          f'<div style="display: flex; flex-wrap: wrap; gap: 4px;"><sc-for list="{H("k.selos")}" as="s" hint-placeholder-count="1">{_chip_hole("s.t","s.st","s.dot")}</sc-for></div>'
          f'<sc-if value="{H("k.hasObs")}" hint-placeholder-val="{F()}"><div style="font-size: 11.5px; color: {MUTED};">{H("k.obs")}</div></sc-if>'
          f'<sc-if value="{H("k.hasDp")}" hint-placeholder-val="{F()}"><div style="font-size: 11.5px; font-weight: 700; color: {INK};">{H("k.dp")}</div></sc-if>'
          f'<div style="font-size: 11.5px; color: {MUTED};">{H("k.meta")}</div></div>')
    col=(f'<div style="flex: 1 1 0; min-width: 0; background: {BG}; border: 1px solid {LINE}; border-radius: 12px; padding: 10px; display: flex; flex-direction: column; gap: 8px;">'
         f'<div style="display: flex; align-items: center; gap: 6px;"><span style="font-size: 11px; font-weight: 800; letter-spacing: .05em; color: {INK}; text-transform: uppercase;">{H("c.t")}</span>'
         f'<span style="{H("c.nst")} padding: 1px 8px; font-size: 11.5px;">{H("c.n")}</span></div>'
         f'<div style="font-size: 11.5px; color: {MUTED}; margin-top: -4px; min-height: 14px;">{H("c.carga")}</div>'
         f'<sc-for list="{H("c.cards")}" as="k" hint-placeholder-count="2">{card}</sc-for>'
         f'<sc-if value="{H("c.vazio")}" hint-placeholder-val="{F()}"><div style="font-size: 12px; color: {MUTED}; padding: 10px 4px; text-align: center; border: 1px dashed {LINE}; border-radius: 10px;">Nenhuma ordem nesta fase</div></sc-if></div>')
    return f'<div role="list" aria-label="Kanban das ordens" style="display: flex; gap: 10px; align-items: flex-start;"><sc-for list="{H("kb")}" as="c" hint-placeholder-count="5">{col}</sc-for></div>'

def _chips():
    return (f'<div role="group" aria-label="Filtrar por fase" style="display: flex; flex-wrap: wrap; gap: 6px;">'
            f'<sc-for list="{H("fchips")}" as="fc" hint-placeholder-count="7"><button type="button" aria-pressed="{H("fc.on")}" onClick="{H("fc.fn")}" style="{H("fc.st")}">{H("fc.t")}<span style="{H("fc.nst")}">{H("fc.n")}</span></button></sc-for></div>')

def _painel():
    lab=lambda t: f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{t}</div>'
    aprow=(f'<div style="display: grid; grid-template-columns: 64px 84px 1fr 1.3fr auto; gap: 8px; align-items: center; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 12.8px; font-variant-numeric: tabular-nums; {H("a.rst")}">'
           f'<span>{H("a.d")}</span><span>{H("a.dia")}</span><span style="text-align: right;">{H("a.ha")}</span><span style="text-align: right; font-weight: 700;">{H("a.ac")}</span>{_chip_hole("a.t","a.st","a.dot")}</div>')
    aphead=(f'<div style="display: grid; grid-template-columns: 64px 84px 1fr 1.3fr auto; gap: 8px; padding: 4px 0; font-size: 10.5px; font-weight: 700; letter-spacing: .04em; color: {MUTED}; text-transform: uppercase;">'
            f'<span>Data</span><span>Turno</span><span style="text-align: right;">Realizado</span><span style="text-align: right;">Acumulado</span><span>Situação</span></div>')
    IC='minmax(0,1.6fr) 96px 110px 110px minmax(0,1.5fr)'
    inshead=(f'<div style="display: grid; grid-template-columns: {IC}; gap: 10px; padding: 4px 0; font-size: 10.5px; font-weight: 700; letter-spacing: .04em; color: {MUTED}; text-transform: uppercase;">'
             f'<span>Produto</span><span style="text-align: right;">Dose</span><span style="text-align: right;">Na ordem</span><span style="text-align: right;">Usado</span><span>Situação</span></div>')
    # linha do insumo + trilha do cenário: reservado › entregue (lote, embalagem, a quem) › confirmado no app › consumido › em custódia › devolvido
    insrow=(f'<div style="display: flex; flex-direction: column; gap: 4px; padding: 7px 0; border-top: 1px solid {LINE};">'
            f'<div style="display: grid; grid-template-columns: {IC}; gap: 10px; align-items: center; font-size: 12.8px; font-variant-numeric: tabular-nums;">'
            f'<span style="min-width: 0;"><b>{H("i.p")}</b><br><span style="font-size: 11.5px; color: {MUTED};">{H("i.g")}</span></span>'
            f'<span style="text-align: right; white-space: nowrap;">{H("i.dose")}</span><span style="text-align: right; white-space: nowrap; font-weight: 700;">{H("i.tot")}</span>'
            f'<span style="text-align: right; white-space: nowrap;">{H("i.usado")}</span><span style="font-size: 12px; color: {MUTED};">{H("i.sit")}</span></div>'
            f'<sc-if value="{H("i.hasTr")}" hint-placeholder-val="{F()}"><div aria-label="Trilha do insumo" style="display: flex; flex-wrap: wrap; gap: 2px 8px; font-size: 11.8px; line-height: 1.4; font-variant-numeric: tabular-nums;">'
            f'<sc-for list="{H("i.tr")}" as="s" hint-placeholder-count="6"><span style="{H("s.st")}">{H("s.t")}</span></sc-for></div></sc-if></div>')
    kvbox=lambda lst: (f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px 18px; padding: 12px 14px; background: {BG}; border-radius: 12px;"><sc-for list="{H(lst)}" as="x" hint-placeholder-count="6"><div style="min-width: 0;">'
             f'<div style="font-size: 10.5px; font-weight: 700; letter-spacing: .05em; color: {MUTED}; text-transform: uppercase;">{H("x.l")}</div><div style="font-size: 13.5px; font-weight: 600; margin-top: 2px;">{H("x.v")}</div></div></sc-for></div>')
    passo=(f'<div role="region" aria-label="Próximo passo" style="{H("pan_pst")}">{lab("Próximo passo")}'
      f'<div style="font-size: 13.5px; line-height: 1.45;">{H("pan_pt")}</div>'
      f'<sc-if value="{H("pan_bloq")}" hint-placeholder-val="{F()}"><div role="alert" style="{H("pan_btst")}">{H("pan_bt")}<br><span style="font-weight: 600;">{H("pan_bq")}</span></div>'
      f'<sc-if value="{H("pan_hasBl")}" hint-placeholder-val="{F()}"><div><a href="{H("pan_bh")}" style="{_MINI} text-decoration: none; display: inline-flex;">{H("pan_bhl")} ›</a></div></sc-if></sc-if>'
      f'<sc-if value="{H("pan_hasObs")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; color: {MUTED};">{H("pan_obs")}</div></sc-if>'
      f'<sc-if value="{H("pan_hasDono")}" hint-placeholder-val="{F()}"><div style="font-size: 12.8px; font-weight: 700;">{H("pan_dono")}</div></sc-if>'
      f'<sc-if value="{H("pan_hasAviso")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; font-weight: 700; color: {YEL}; background: {YELS}; padding: 7px 10px; border-radius: 8px;">{H("pan_aviso")}</div></sc-if>'
      f'<sc-if value="{H("pan_idle")}" hint-placeholder-val="{T()}"><div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">'
      f'<sc-if value="{H("pan_hasBtn")}" hint-placeholder-val="{T()}"><button type="button" onClick="{H("pan_go")}" style="{BTN_ST(True,True)}">{H("pan_pbtn")}</button></sc-if>'
      f'<sc-if value="{H("pan_hasCanc")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("pan_cango")}" title="Cancelar a ordem que ainda não teve execução (exige motivo)" style="{_MINI} color: {RED}; border-color: {RED};">Cancelar sem execução</button></sc-if>'
      f'<sc-if value="{H("pan_hasDisp")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("pan_disgo")}" title="Dispensar parte do saldo sem executar (o realizado fica preservado)" style="{_MINI}">Dispensar saldo</button></sc-if></div></sc-if>'
      f'<sc-if value="{H("pan_canf")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
      f'<div style="font-size: 13px; font-weight: 600; line-height: 1.45;">{H("pan_cct")}</div>'
      f'<textarea aria-label="Motivo do cancelamento" placeholder="Motivo do cancelamento" value="{H("pan_rmot")}" onChange="{H("pan_setrmot")}" style="font-family: inherit; font-size: 13px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; min-height: 54px; resize: vertical;"></textarea>'
      f'<sc-if value="{H("pan_hasRerr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_rerr")}</span></sc-if>'
      f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Voltar</button><button type="button" onClick="{H("pan_cansave")}" style="{_MINI} color: #fff; background: {RED}; border-color: {RED};">Confirmar cancelamento</button></div></div></sc-if>'
      f'<sc-if value="{H("pan_disf")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
      f'<div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end;"><label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {MUTED};">Área a dispensar (ha)<input aria-label="Área a dispensar em hectares" inputMode="decimal" value="{H("pan_aha")}" onChange="{H("pan_setaha")}" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; width: 110px; text-align: right;"></label>'
      f'<span style="font-size: 12px; color: {MUTED}; padding-bottom: 9px; flex: 1 1 260px;">{H("pan_dsub")}</span></div>'
      f'<textarea aria-label="Motivo da dispensa" placeholder="Motivo da dispensa" value="{H("pan_rmot")}" onChange="{H("pan_setrmot")}" style="font-family: inherit; font-size: 13px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; min-height: 54px; resize: vertical;"></textarea>'
      f'<label style="display: flex; gap: 8px; align-items: center; font-size: 13px; font-weight: 600;"><input type="checkbox" aria-label="Validação agronômica" checked="{H("pan_dval")}" onChange="{H("pan_setdval")}" style="width: 16px; height: 16px; accent-color: {ACC}; margin: 0;">Validação agronômica: o agrônomo confirmou a dispensa</label>'
      f'<sc-if value="{H("pan_hasRerr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_rerr")}</span></sc-if>'
      f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Voltar</button><button type="button" onClick="{H("pan_dissave")}" style="{_MINIP}">Confirmar dispensa</button></div></div></sc-if>'
      f'<sc-if value="{H("pan_conf")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE}; font-size: 13px; font-weight: 600; line-height: 1.45;">{H("pan_ct")}'
      f'<sc-if value="{H("pan_hasRerr")}" hint-placeholder-val="{F()}"><span style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_rerr")}</span></sc-if>'
      f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Voltar</button><button type="button" onClick="{H("pan_yes")}" style="{_MINIP}">{H("pan_cbtn")}</button></div></div></sc-if>'
      f'<sc-if value="{H("pan_rev")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
      f'<div style="font-size: 13px; font-weight: 600;">Decida sobre a versão. Devolver ou rejeitar exige motivo; nenhuma decisão libera a ordem.</div>'
      f'<textarea aria-label="Motivo da devolução ou rejeição" placeholder="Motivo (para devolver ou rejeitar)" value="{H("pan_rmot")}" onChange="{H("pan_setrmot")}" style="font-family: inherit; font-size: 13px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; min-height: 54px; resize: vertical;"></textarea>'
      f'<sc-if value="{H("pan_hasRerr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_rerr")}</span></sc-if>'
      f'<div style="display: flex; gap: 8px; flex-wrap: wrap;"><button type="button" onClick="{H("pan_raprov")}" style="{_MINIP}">Aprovar versão</button><button type="button" onClick="{H("pan_rdev")}" style="{_MINI}">Devolver para ajuste</button>'
      f'<button type="button" onClick="{H("pan_rrej")}" style="{_MINI} color: {RED}; border-color: {RED};">Rejeitar</button><span style="flex-grow: 1;"></span><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Voltar</button></div></div></sc-if>'
      f'<sc-if value="{H("pan_apf")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
      f'<div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end;"><label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {MUTED};">Data do turno<input type="date" aria-label="Data do turno" value="{H("pan_ad")}" onChange="{H("pan_setad")}" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE};"></label>'
      f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {MUTED};">Área feita (ha)<input aria-label="Área feita em hectares" inputMode="decimal" value="{H("pan_aha")}" onChange="{H("pan_setaha")}" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; width: 110px; text-align: right;"></label>'
      f'<span style="font-size: 12px; color: {MUTED}; padding-bottom: 9px;">{H("pan_asub")}</span></div>'
      f'<sc-if value="{H("pan_hasAerr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_aerr")}</span></sc-if>'
      f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Cancelar</button><button type="button" onClick="{H("pan_asave")}" style="{_MINIP}">Salvar apontamento</button></div></div></sc-if></div>')
    return (f'<sc-if value="{H("pan_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar painel" onClick="{H("pan_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="{H("pan_t")}" onKeyDown="{H("pan_key")}" style="position: relative; width: 820px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">'
      f'<div style="display: flex; align-items: flex-start; gap: 10px;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em; flex-grow: 1; line-height: 1.3;">{H("pan_t")}</h2>'
      f'<sc-if value="{H("pan_hasLink")}" hint-placeholder-val="{F()}"><a href="{H("pan_link")}" style="{_MINI} text-decoration: none; display: inline-flex; align-items: center; white-space: nowrap;">Abrir ordem completa ›</a></sc-if>'
      f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H("pan_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
      f'<div style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">{_chip_hole("pan_fase","pan_fst","pan_fdot")}<sc-for list="{H("pan_selos")}" as="s" hint-placeholder-count="1">{_chip_hole("s.t","s.st","s.dot")}</sc-for></div>'
      f'<div role="list" aria-label="Fase da ordem" style="display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 6px;"><sc-for list="{H("pan_steps")}" as="p" hint-placeholder-count="5"><div role="listitem" aria-current="{H("p.cur")}" style="{H("p.st")}"><span style="{H("p.bst")}"></span>{H("p.t")}</div></sc-for></div>'
      + passo +
      f'<div style="display: flex; flex-direction: column; gap: 6px;">{lab("Atividade")}{kvbox("pan_atv")}</div>'
      f'<div style="display: flex; flex-direction: column; gap: 2px;">{lab("Insumos e doses")}'
      f'<sc-if value="{H("pan_hasIns")}" hint-placeholder-val="{T()}">{inshead}<sc-for list="{H("pan_ins")}" as="i" hint-placeholder-count="2">{insrow}</sc-for></sc-if>'
      f'<sc-if value="{H("pan_semIns")}" hint-placeholder-val="{F()}"><div style="font-size: 12.8px; color: {MUTED}; padding: 6px 0;">{H("pan_semInsT")}</div></sc-if></div>'
      f'<sc-if value="{H("pan_hasRet")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 6px;">{lab(H("pan_retT"))}'
      f'<sc-if value="{H("pan_hasPrep")}" hint-placeholder-val="{F()}"><div style="font-size: 13px; line-height: 1.45;">{H("pan_prep")}</div></sc-if>'
      f'<div style="display: flex; gap: 8px; flex-wrap: wrap;"><sc-if value="{H("pan_retLink")}" hint-placeholder-val="{T()}"><a href="EST.dc.html" style="{_MINI} text-decoration: none;">Retirar no almoxarifado ›</a></sc-if>'
      f'<sc-if value="{H("pan_fichas")}" hint-placeholder-val="{F()}"><a href="OS-0424-app.dc.html" style="{_MINI} text-decoration: none;">Ficha no app (sem internet) ›</a><a href="OS-0424-ficha.dc.html" style="{_MINI} text-decoration: none;">Ficha impressa ›</a></sc-if></div></div></sc-if>'
      f'<sc-if value="{H("pan_hasRec")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 2px;">{lab("Recursos alocados")}'
      f'<sc-for list="{H("pan_rec")}" as="rc" hint-placeholder-count="3"><div style="display: grid; grid-template-columns: minmax(0,1.2fr) minmax(0,1fr) minmax(0,1.3fr); gap: 10px; align-items: center; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 12.8px;">'
      f'<b>{H("rc.t")}</b><span style="color: {MUTED};">{H("rc.j")}</span><span style="display: flex; flex-wrap: wrap; gap: 4px;"><sc-if value="{H("rc.cond")}" hint-placeholder-val="{F()}"><span style="display: inline-flex; padding: 2px 8px; border-radius: 999px; font-size: 11.5px; font-weight: 700; color: #8A5A00; background: #FFF4D6;">condicional</span></sc-if>'
      f'<sc-for list="{H("rc.al")}" as="al" hint-placeholder-count="1"><span style="display: inline-flex; padding: 2px 8px; border-radius: 999px; font-size: 11.5px; font-weight: 700; color: #B42318; background: #FDE8E6;">{H("al.t")}</span></sc-for></span></div></sc-for></div></sc-if>'
      f'<div style="display: flex; flex-direction: column; gap: 4px;">{lab("Apontamentos diários")}'
      f'<sc-if value="{H("pan_hasAp")}" hint-placeholder-val="{T()}">{aphead}<sc-for list="{H("pan_ap")}" as="a" hint-placeholder-count="4">{aprow}</sc-for>'
      f'<sc-if value="{H("pan_hasAcum")}" hint-placeholder-val="{T()}"><div style="padding: 8px 0 0; border-top: 2px solid {INK}; font-size: 13px; font-weight: 800;">{H("pan_acum")}</div></sc-if>'
      f'<sc-if value="{H("pan_hasNota")}" hint-placeholder-val="{F()}"><div style="font-size: 12px; color: {MUTED};">{H("pan_nota")}</div></sc-if></sc-if>'
      f'<sc-if value="{H("pan_noAp")}" hint-placeholder-val="{F()}"><div style="font-size: 12.8px; color: {MUTED}; padding: 6px 0;">{H("pan_noApT")}</div></sc-if></div>'
      f'<div style="display: flex; flex-direction: column; gap: 4px;">{lab("Situação atual")}<div style="font-size: 13px; line-height: 1.45;">{H("pan_cond")}</div></div>'
      f'<div style="display: flex; flex-direction: column; gap: 4px;">{lab("Origem")}<sc-for list="{H("pan_orig")}" as="og" hint-placeholder-count="2"><div style="font-size: 13px; padding: 5px 0; border-bottom: 1px solid {LINE};">{H("og.t")}</div></sc-for></div>'
      f'</aside></div></sc-if>')

def _form():
    def campo(k,l,ctrl,help_=''):
        return (f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="nv_{k}" style="font-size: 12px; font-weight: 600; color: {MUTED};">{l}</label>{ctrl}'
                f'<sc-if value="{H("nv_he_"+k)}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("nv_e_"+k)}</span></sc-if>'
                + (f'<span style="font-size: 11.5px; color: {MUTED};">{help_}</span>' if help_ else '') + '</div>')
    def sel(k,lst,val,fn,dis=None):
        d=f' disabled="{H(dis)}"' if dis else ''
        return (f'<select id="nv_{k}" value="{H(val)}" onChange="{H(fn)}"{d} style="{H("nv_st_"+k)}"><sc-for list="{H(lst)}" as="o" hint-placeholder-count="2"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select>')
    return (f'<sc-if value="{H("nv_show")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar formulário" onClick="{H("nv_cancel")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" aria-label="Nova ordem" onKeyDown="{H("nv_key")}" style="position: relative; width: 460px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 12px;">'
      f'<div style="display: flex; align-items: flex-start; gap: 10px;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em; flex-grow: 1;">Nova ordem</h2>'
      f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H("nv_cancel")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
      f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">Escolha safra, cultivo e atividade do plano. A ordem nasce em A liberar e vai para a revisão do agrônomo.</div>'
      f'<sc-if value="{H("nv_hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">Corrija os campos destacados; o que você preencheu foi mantido.</div></sc-if>'
      + campo('saf','Safra',sel('saf','nv_safs','nv_saf','nv_setsaf'))
      + campo('cult','Cultivo',sel('cult','nv_cults','nv_cult','nv_setcult','nv_cultdis'))
      + campo('atv','Atividade',sel('atv','nv_atvs','nv_atv','nv_setatv','nv_atvdis'))
      + f'<sc-if value="{H("nv_hasDup")}" hint-placeholder-val="{F()}"><div style="margin-top: -4px;"><button type="button" onClick="{H("nv_opendup")}" title="Abrir a ordem que já existe para esta atividade (nada é emitido)" style="{_MINI}">{H("nv_dupt")}</button></div></sc-if>'
      + f'<sc-if value="{H("nv_noplan")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; color: {YEL}; background: {YELS}; padding: 8px 12px; border-radius: 10px; font-weight: 700;">Este cultivo não tem plano aplicado. <a href="SAF.dc.html" style="color: {ACC};">Aplicar plano em Planejar safra ›</a></div></sc-if>'
      + f'<sc-if value="{H("nv_hasArea")}" hint-placeholder-val="{F()}"><div style="font-size: 12.8px; padding: 8px 12px; border-radius: 10px; background: {BG};">{H("nv_area")}</div></sc-if>'
      + campo('jan','Início da janela',f'<input id="nv_jan" type="date" value="{H("nv_jan")}" onChange="{H("nv_setjan")}" style="{H("nv_st_jan")}">')
      + f'<div style="flex-grow: 1;"></div>'
      f'<sc-if value="{H("nv_warn")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("nv_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H("nv_keep")}" style="{_MINIP}">Continuar editando</button></div></div></sc-if>'
      f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};"><button type="button" onClick="{H("nv_cancel")}" style="{BTN_ST(False,True)}">Cancelar</button>'
      f'<button type="button" onClick="{H("nv_save")}" style="{BTN_ST(True,True)}">Emitir ordem</button></div>'
      f'</aside></div></sc-if>')

def _recursos_tab():
    """Semana do PCP por recurso e dia: ordens e horários, conflitos, manutenção, excesso de jornada e uso."""
    res, conf = AL.semana()
    ck = {(c['r'], c['dia'], c['a']) for c in conf} | {(c['r'], c['dia'], c['b']) for c in conf}
    nconf = len({(c['dia'], c['a'], c['b']) for c in conf if not c['manut']})
    manut = sorted({AL.NOME[a['r']] + ' (' + a['os'] + ')' for a in AL.ALOC if a['sit'] == 'manutenção'})
    acima = [f"{x['nome'].split(' · ')[0]} {d['d'][8:10]}/{d['d'][5:7]} ({str(round(d['h'],1)).replace('.',',')} h)" for x in res for d in x['dias'] if d['acima']]
    ociosos = [x['nome'].split(' · ')[0] for x in res if x['uso'] < 0.2]
    kpi = lambda t, v, c: f'<div style="display: flex; flex-direction: column; gap: 2px; padding: 8px 12px; border-radius: 10px; background: {c}; min-width: 0;"><span style="font-size: 11px; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; color: {MUTED};">{t}</span><span style="font-size: 13px; font-weight: 700;">{v}</span></div>'
    top = (f'<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px;">'
           + kpi('Conflitos', f'{nconf} · mesmo recurso em duas ordens no mesmo horário', REDS if nconf else BG)
           + kpi('Em manutenção', ', '.join(manut) or '—', BG) + kpi('Acima da jornada', ', '.join(acima) or '—', YELS if acima else BG)
           + kpi('Ociosos (uso abaixo de 20 %)', ', '.join(ociosos) or '—', BG) + '</div>')
    cols = f'grid-template-columns: 210px repeat({len(AL.DIAS)}, minmax(118px, 1fr)) 150px;'
    head = (f'<div style="display: grid; {cols} gap: 0; font-size: 10.5px; font-weight: 800; letter-spacing: .04em; text-transform: uppercase; color: {MUTED}; background: {BG}; border-radius: 10px 10px 0 0;">'
            f'<div style="padding: 8px 10px;">Recurso</div>' + ''.join(f'<div style="padding: 8px 6px;">{lab}</div>' for _, lab in AL.DIAS) + '<div style="padding: 8px 10px;">Uso na semana</div></div>')
    body = ''; tipo0 = None
    for x in res:
        if x['tipo'] != tipo0:
            tipo0 = x['tipo']; body += f'<div style="padding: 10px 10px 4px; font-size: 11px; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; color: {MUTED}; border-top: 1px solid {LINE};">{ {"Máquina":"Máquinas","Implemento":"Implementos","Pessoa":"Pessoas"}[tipo0] }</div>'
        cells = ''
        for d in x['dias']:
            its = ''
            for a in d['itens']:
                t = f"{a['os']} {AL.hh(a['ini'])}–{AL.hh(a['fim'])}"
                if a['sit'] == 'manutenção':
                    its += f'<span title="Indisponível: {a["os"]}" style="display: block; font-size: 11.5px; font-weight: 700; padding: 3px 6px; border-radius: 6px; background: {GRAYS}; color: {MUTED};">Manutenção {a["os"]}</span>'; continue
                bad = (x['r'], d['d'], a['os']) in ck
                st = ('background: #FDE8E6; color: #B42318; border: 1px solid #F4C7C1;' if bad else ('background: #FFF4D6; color: #8A5A00; border: 1px dashed #D9B25B;' if a['sit'] == 'condicional' else f'background: {ACCS}; color: {ACC}; border: 1px solid #BFE0CB;'))
                tt = ('Conflito de horário · ' if bad else ('Condicional · ' if a['sit'] == 'condicional' else '')) + 'abrir ' + a['os']
                its += f'<button type="button" onClick="{H("op_" + a["os"].replace("-", ""))}" title="{tt}" style="display: block; width: 100%; text-align: left; font-family: inherit; font-size: 11.5px; font-weight: 700; padding: 3px 6px; border-radius: 6px; cursor: pointer; {st}">{t}</button>'
            hint = (f'<span style="font-size: 11px; color: #8A5A00; font-weight: 700;">{str(round(d["h"],1)).replace(".",",")} h · acima da jornada</span>' if d['acima']
                    else (f'<span style="font-size: 11px; color: {MUTED};">livre</span>' if not d['itens'] else ''))
            cells += f'<div style="padding: 6px; display: flex; flex-direction: column; gap: 3px; border-left: 1px solid {LINE};">{its}{hint}</div>'
        u = round(x['uso'] * 100); cor = '#B42318' if any(d['conf'] for d in x['dias']) else ('#8A968E' if x['uso'] < 0.2 else ('#8A5A00' if x['uso'] > 0.85 else '#1E7A4C'))
        lab = 'conflito' if any(d['conf'] for d in x['dias']) else ('ocioso' if x['uso'] < 0.2 else ('carga alta' if x['uso'] > 0.85 else 'em uso'))
        uso = (f'<div style="padding: 8px 10px; border-left: 1px solid {LINE}; display: flex; flex-direction: column; gap: 4px;"><span style="font-size: 13px; font-weight: 800; color: {cor};">{u} % · {lab}</span>'
               f'<span style="display: block; height: 6px; border-radius: 999px; background: {GRAYS}; overflow: hidden;"><span style="display: block; height: 100%; width: {min(u,100)}%; background: {cor};"></span></span>'
               f'<span style="font-size: 11px; color: {MUTED};">{str(round(x["h"],1)).replace(".",",")} h de {str(round(x["disp"],1)).replace(".",",")} h</span></div>')
        body += f'<div role="row" style="display: grid; {cols} border-top: 1px solid {LINE}; font-size: 12.5px;"><div style="padding: 8px 10px; font-weight: 700;">{esc(x["nome"])}</div>{cells}{uso}</div>'
    legenda = (f'<div style="display: flex; gap: 14px; flex-wrap: wrap; font-size: 11.5px; color: {MUTED};">'
               f'<span><b style="color: {ACC};">■</b> alocação firme</span><span><b style="color: #8A5A00;">▭</b> condicional (depende de aprovação ou liberação)</span>'
               f'<span><b style="color: #B42318;">■</b> conflito de horário</span><span><b style="color: #8A968E;">■</b> manutenção</span></div>')
    return (f'<div style="display: flex; flex-direction: column; gap: 10px;">{top}'
            f'<div role="table" aria-label="Alocação de recursos na semana" style="border: 1px solid {LINE}; border-radius: 10px; overflow-x: auto;">{head}{body}</div>{legenda}</div>')

def _restaurar():
    """Ação discreta no rodapé do bloco: volta o cenário compartilhado (O.S., Estoque e App) ao início, com confirmação."""
    lk=f'border: 0; background: transparent; color: {MUTED}; font-family: inherit; font-size: 12px; font-weight: 600; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; padding: 4px;'
    return (f'<div style="display: flex; justify-content: flex-end; align-items: center; gap: 8px; flex-wrap: wrap;">'
            f'<sc-if value="{H("os_rst_no")}" hint-placeholder-val="{T()}"><button type="button" onClick="{H("os_rst")}" style="{lk}">Restaurar demonstração</button></sc-if>'
            f'<sc-if value="{H("os_rst_ask")}" hint-placeholder-val="{F()}"><span style="font-size: 12px; color: {MUTED};">Volta O.S., estoque e app ao início da demonstração.</span>'
            f'<button type="button" onClick="{H("os_rst_ok")}" style="{_MINI} color: {RED}; border-color: {RED};">Restaurar</button><button type="button" onClick="{H("os_rst_cancel")}" style="{_MINI}">Manter</button></sc-if></div>')

def build():
    import cenario  # aqui dentro: cenario.seed importa este módulo
    fname='OS.dc.html'; E._reset_screen(fname)
    ordens=_ordens()
    g_os=grid([dict(k='id',l='O.S.'),dict(k='ativ',l='Atividade · local',w=200),dict(k='jan',l='Janela',w=110),
               dict(k='fase',l='Fase'),dict(k='cond',l='Condição',w=255),dict(k='real',l='Realizado · saldo',t='num',a='r',w=150),
               dict(k='resp',l='Responsável')],
              [],edit=dict(m='pick'),gid='g_os',total=False)
    lista=_chips()+g_os
    bar,panes=tabs(['Lista','Kanban','Recursos'],[f'<div style="display: flex; flex-direction: column; gap: 10px;">{lista}</div>',_kanban(),_recursos_tab()],active=0,label='Visão das ordens')
    # recorte vazio (Fazenda/Safra do topo): uma frase e uma ação no lugar das visões
    vazio=(f'<sc-if value="{H("os_vazio")}" hint-placeholder-val="{F()}"><div aria-label="Sem ordens no filtro" style="display: flex; align-items: center; justify-content: center; gap: 12px; flex-wrap: wrap; padding: 36px 16px; border: 1px dashed {LINE}; border-radius: 12px;">'
           f'<span style="font-size: 14px; font-weight: 700;">{H("os_vt")}</span><button type="button" onClick="{H("os_vgo")}" style="{_MINIP}">{H("os_va")}</button></div></sc-if>')
    tem=lambda x: f'<sc-if value="{H("os_tem")}" hint-placeholder-val="{T()}">{x}</sc-if>'
    corpo=bloco('Ordens por fase','Clique numa ordem para ver atividade, insumos e doses e seguir para a próxima fase.',vazio+tem(panes)+_restaurar(),acao=tem(bar))
    EXTRA.append(_painel()); EXTRA.append(_form())
    data=dict(ords=ordens,nova=_nova_ordem_dados(),aloc={o['id']:AL.da_ordem(o['id']) for o in ordens})
    # cenário compartilhado (O.S. ↔ Estoque ↔ App) antes do JS da tela
    EXTRAJS[0]=cenario.js_prefixo()+'const OSD = '+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+';\n'+JS
    prim=f'<button type="button" onClick="{H("nv_open")}" style="{BTN_ST(True)}">Nova ordem</button>'
    HEIGHTS37[fname]=1000
    shell37('OS','Ordem de Serviço',corpo,fname=fname,
            subtitle='A liberar → Liberadas → Em execução → Em conferência → Encerradas. Pausa, atraso, parcial e impedimento aparecem como selos.',
            status=(H('os_st'),'red'),primary_html=prim,search=False,
            footer='A fase só muda por evento: liberação, início, término físico e encerramento. Finalizar apontamento do turno não encerra a O.S.')
    _status_dinamico(fname)
    return fname

def _status_dinamico(fname):
    """troca o selo fixo do cabeçalho (shell37 pinta de vermelho) por um selo com a cor calculada na tela (os_stst / os_stdot)."""
    import ui37
    p=os.path.join(E.P,fname); s=open(p,encoding='utf-8').read(); old=ui37.chip(H('os_st'),'red')
    assert s.count(old)==1, 'selo do cabeçalho não encontrado em '+fname
    open(p,'w',encoding='utf-8').write(s.replace(old,f'<span style="{H("os_stst")}"><span style="{H("os_stdot")}"></span>{H("os_st")}</span>'))
