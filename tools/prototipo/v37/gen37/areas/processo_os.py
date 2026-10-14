# -*- coding: utf-8 -*-
"""Agrícola › Ordem de Serviço (OS.dc.html) — gestão das ordens por Lista ou Kanban (abas reais), cinco fases fixas,
selos como condição, painel lateral de consulta (fase, saldo, apontamentos diários na mesma ordem, origem) e "Nova ordem".

observacoes (dados coerentes com dados.py / dados2.py / telas vizinhas):
- Irrigação só com água (OS-0419, OS-0422, OS-0423) fica no módulo Irrigação (IR-03 Ordens de irrigação), sem misturar com as O.S. de
  operações agrícolas (pedido do proprietário, 01/10/2026). A fertirrigação (OS-0418) continua aqui: leva produto, requisição e liberação do agrônomo.
- Conjunto de ordens = dados.ORDENS (registro canônico, 13 ordens): id, tipo, talhão, área, fase, selo, realizado, saldo,
  janela, responsável e tela de detalhe vêm do registro; aqui só ficam apontamentos, pendência, origem e versão.
- Detalhe = campo "detalhe" do registro (link "Abrir ordem" no painel); sem detalhe, a ordem é consultada só pelo painel.
- Apontamentos: OS-0421 = TURNOS de areas/campo.py (50, 50, 50, 40 → 190/350; previstos 50, 50, 60);
  OS-0420 = 18 ha (21/09, conferido) + 12 ha (22/09, provisório, turno interrompido pela quebra do Trator T1) = 30/100;
  OS-0417 = 32 + 33 + 30 = 95/95 (19–21/09); OS-0415 = 48 + 48 = 96/96 (11–12/09).
- OS-0420: 30 ha na v2; saldo de 70 ha na v3, ajustada pela agrônoma; pausa só pelo Trator T1; selo = o do registro.
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
- OS-0431 (DEMO-17): v1, retirada de Liberadas pela INSP-105 antes do 1º início; selo "Falta máquina · Trator T1 bloqueado";
  conta como impedida.
- Irrigação só com água (26/09, igual a areas/irrigacao.py): OS-0419, OS-0422 e OS-0423 não passam pelo agrônomo; liberar depende da
  prontidão operacional. OS-0422 = 13,5 mm em 2 passadas de 6,75 mm, selo "Janela a definir", dono João (irrigante);
  OS-0423 = 4,0 mm no gotejo T7, selo "Conflito · parada da B3", dono Caio (PCP), estimativa por ET (sonda sem dado, não bloqueia).
  Só a fertirrigação (OS-0418) é liberada pelo agrônomo, que pode ajustar antes.
- Filtros do topo (ui37.MACRO: Fazenda e Safra) valem para lista, Kanban, chips de fase e selo do cabeçalho; recorte sem ordens mostra
  uma frase e uma ação ("Ver Santa Rita" ou "Ver todas as safras"). Fazenda/safra de cada ordem = dados.ORDENS (faz, saf).
- Cenário compartilhado (26/09, etapa 2): EXTRAJS[0] = cenario.js_prefixo() + JS da tela. Fase, realizado/saldo, apontamentos,
  requisição e insumos vêm de cenGet().ordens/.reqs; cenOuvir(self) redesenha quando Estoque ou App mudam o cenário. Toda ação da O.S.
  grava por cenMudar com funções osc_* (liberar (agrônomo, pode ajustar antes) = cenLiberar com reserva por lote, iniciar, apontar, conferência,
  encerrar só com cenPodeEncerrar vazio, cancelar liberando a reserva, dispensar, nova ordem). Liberar é testado numa cópia do cenário:
  o erro de saldo/lote vira o motivo do bloqueio. O bloqueio do encerramento (sinal ou sobra em custódia, com "Receber devolução no
  Estoque") vem do cenário, inclusive o da OS-0417. "Restaurar demonstração" (rodapé do bloco) chama cenReset().
- Verificador v39 (26/09): bloqueio lido do cenário também na lista e no Kanban (liberar sem lote → selo vermelho "Falta insumo · X" +
  Suprimentos, conta como impedida; encerrar com sobra → "Sobras a receber" + Rui (almoxarife); sem sinal → "Aguardando sinal do app").
  Ordem nova leva os insumos da atividade do plano (dose × área, gatilho e conjunto do plano); sem insumo libera sem requisição; requisição
  nova = REQ-041, REQ-042… (osc_reqId, três dígitos, antes de cenLiberar). Selo do cabeçalho com cor calculada (vermelho só com impedidas).
  Coluna Encerradas com o período das ordens da coluna. Ordens de água: lâmina só em Insumos, nota de ET só no Próximo passo.
- O.S. sem revisão (01/10, pedido do proprietário): não há aprovar, devolver ou rejeitar versão nem recibo APV-. Em A liberar com
  produto o agrônomo libera ("Liberar para execução") ou ajusta antes ("Ajustar antes de liberar": tira ou inclui produto, muda dose e área →
  "Salvar e liberar" = osc_ajustar, que grava a versão seguinte com a linha de histórico em Origem e libera no mesmo comando).
  A checagem do Estoque vale desde a abertura: a OS-0418 (Ureia 45 % sem lote) já nasce impedida. Versão é só "vN" (osVn).
  05/10 (Frente F; padrão adotado, o proprietário pode mudar): a confirmação é o "Aprovar e liberar" do PRD 41.3 e grava na Origem dois
  registros separados, vN aprovada (CMD-42) e vN liberada (CMD-06), com quem, hora, área e doses. Água só com água não grava CMD-42.
  05/10 (Frente E1, RN-016/RF-EXT-002): liberar e ajustar (também "Salvar ajuste") passam pela regra legal única do AG-01 (cenUsoLegal: registro,
  situação, dose da bula, nº de aplicações) antes de qualquer gravação; a recusa não grava CMD-42. Alertas aparecem na confirmação.
- Consulta Agrofit (01/10): no "Ajustar antes de liberar", produto com ficha em agrofit_dados (nome exato da fazenda) ganha o atalho
  "Agrofit ›" para AG-07.dc.html#<id> em nova aba (o formulário fica aberto) e o "Incluir produto" mostra classe e grupo de ação.
"""
import json, os, re
import quantidade as _QTD   # regra única de quantidade de insumo (SINT-C03)
from engine import (grid,visoes,esc,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,DISP,BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP)
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
_vsem=lambda s: re.sub(r'\b(v\d+) (?:aprovada|em revisão|emitida)\b',r'\1',str(s))  # O.S. sem revisão (01/10): versão é só vN ("rota aprovada" da OB-0104 fica)
VERSAO={o['id']:_vsem(o['versao']) for o in D.OS}
# irrigação só com água: sem agrônomo; o sistema programa a lâmina do balanço hídrico e libera pela prontidão operacional
LAM={'OS-0419':'10,81 mm em 1 passada','OS-0422':'13,5 mm em 2 passadas de 6,75 mm','OS-0423':'4,0 mm'}
OBS={'OS-0423':'estimativa por ET · sonda sem dado'}  # nota que não bloqueia
TIPO={'OS-0419':'Irrigação · água'}  # dados.ORDENS ainda diz "água por política" (fora da permissão desta frente)
VERSAO.update({'OS-0419':'v1 · liberada pela prontidão operacional','OS-0422':'v1 · só água · libera pela prontidão','OS-0423':'v1 · só água · libera pela prontidão',
               'OS-0420':'v3 no saldo de 70 ha (KCl −12 %) · 30 ha na v2',
               'OS-0424':'v1','OS-0425':'plano CAFE-AR · v1','OS-0430':'v1','OS-0431':'REC-014 v2 · v1'})
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
 'OS-0420':'Trator T1 bloqueado pela OM-0233 · Manutenção; substituto Trator 02 a partir de 24/09. Saldo de 70 ha na v3 (KCl −12 %), ajustada por Ana (agrônoma) em 23/09; 30 ha realizados preservados na v2.',
 'OS-0419':'Pronta para iniciar hoje às 20:00 · João.',
 'OS-0418':'Fertirrigação v2 · Ana (agrônoma) confere, ajusta se precisar e libera · vence hoje. Próximo passo: liberar para execução.',
 'OS-0417':'10 sc de MAP 11-52 sob custódia de Paula (equipe de campo) · prazo 24/09. Rui recebe a devolução no almoxarifado.',
 'OS-0415':'Nenhuma · ordem encerrada, somente consulta.',
 'OB-0104':'Ordem conciliada. O lote L27-013 segue bloqueado pela Qualidade (INSP-88 · prazo 25/09).',
 'OS-0422':'Lâmina programada pelo balanço hídrico; a janela precisa sair antes do próximo ciclo.',
 'OS-0423':'Lâmina programada pelo balanço hídrico; o conflito precisa ser resolvido antes das 14:00.',
 'OS-0424':'Fungicida A reservado: 65 L do lote F26-02 (REQ-039 · recibo RS-7741). Próximo passo: Marcos retira no almoxarifado e confirma no app para iniciar em 24/09.',
 'OS-0425':'REQ-040 pede 11.400 kg de NPK 20-05-20; o lote N26-03 tem 8.000 kg · Suprimentos completa a entrega até 15/10.',
 'OS-0430':'Ana (agrônoma) confere, ajusta se precisar e libera. Dessecação a 20 dias do plantio (DAP −20). Próximo passo: liberar para execução.',
 'OS-0431':'Retirada de Liberadas em 23/09: a INSP-105 bloqueou o Trator T1 (OM-0233) antes do 1º início. Dono: PCP · prazo: antes de 24/09 06:00 · próxima ação: Confirmar substituto.',
}
ORIG={
 'OS-0421':['Safra 2026/27 · plano de safra, janela 20–26/09','Recomendação: fungicida 1ª aplicação · protocolo do plano técnico · v2 aprovada'],
 'OS-0420':['Safra 2026/27 · plantio Soja 58 W no T4','Recomendação REC-014 v2 · semente e adubação de base'],
 'OS-0419':['Balanço hídrico de 23/09 · Pivô 2 · Milho V10'],
 'OS-0418':['Reclassificação da tarefa de água do Pivô 1 para fertirrigação','Versão v2 · liberação com Ana (agrônoma)'],
 'OS-0417':['Safra 2026/27 · Feijão P1 · adubação de cobertura','Requisição REQ-031 · MAP 11-52: 100 sc entregues, 70 consumidas, 20 devolvidas, 10 a receber'],
 'OS-0415':['Safra 2025/26 · Milho T3 · dessecação pós-colheita'],
 'OB-0104':['Rota de beneficiamento aprovada · Armazém Sede','Lote L27-013 · café beneficiado, 3.690 sc'],
 'OS-0422':['Balanço hídrico de 23/09 · Pivô 2 · Milho V10 · próximo ciclo'],
 'OS-0423':['Balanço hídrico de 23/09 · Gotejo T7 · Mamão'],
 'OS-0424':['Safra 2026/27 · T1-B · pulverização de fungicida','Requisição REQ-039 · Fungicida A, 65 L do lote F26-02'],
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
 'OS-0424':('Pulverização','Fungicida','24/09','Safra 2026/27 · T1-B','Pulverização'),
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
 'OS-0424':[('Fungicidas','Fungicida A',0.5,'L',None,'Reservado 65 L · lote F26-02 · REQ-039')],
 'OS-0425':[('Fertilizantes','NPK 20-05-20',300.0,'kg',None,'REQ-040 · lote N26-03 tem 8.000 kg · faltam 3.400 kg')],
 'OS-0430':[('Herbicidas','Glifosato 480',2.0,'L',None,'Reserva ao liberar'),('Herbicidas','2,4-D 806',1.0,'L',None,'Reserva ao liberar'),('Adjuvantes','Óleo mineral',0.5,'L',None,'Reserva ao liberar')],
 'OS-0431':[('Sementes','Semente de soja 58 W',52.0,'kg',None,'Reserva ao liberar'),('Fertilizantes','MAP 11-52',250.0,'kg',None,'Reserva ao liberar')],
}
SEM_INS={'OS-0419':'Água · 10,81 mm em 1 passada · sem almoxarifado.','OS-0422':'Água · 13,5 mm em 2 passadas de 6,75 mm (limite de 12,0 mm por passada no pivô) · sem almoxarifado.',
         'OS-0423':'Água · 4,0 mm por gotejo em 2 h · sem almoxarifado.','OB-0104':'Ordem de processo: entradas e saídas por etapa do beneficiamento, sem dose por hectare.'}
# impedimento que segura o próximo passo da fase atual: o quê, quem resolve e onde
BLOQ={
 'OS-0431':dict(acao='liberar',aid='a01',t='Liberar bloqueado: Trator T1 bloqueado (OM-0233).',q='PCP confirma a máquina substituta antes de 24/09 06:00.'),   # aid: condição única (c.man), S3
 'OS-0420':dict(acao='apontar',aid='a01',t='Apontamento pausado: Trator T1 bloqueado (OM-0233).',q='O Trator 02 assume a partir de 24/09.',h='CA-01x-os0420.dc.html',hl='Abrir a ordem completa'),
 'OS-0422':dict(acao='liberar',tone='yellow',t='Definir janela: as 2 passadas ainda não têm horário.',q='João (irrigante) define a janela na Irrigação.',h='IR-02.dc.html',hl='Definir janela'),
 'OS-0423':dict(acao='liberar',tone='red',t='Resolver conflito: a parada da bomba B3 (14:00–15:00) cai na janela.',q='Caio (PCP) resolve o conflito na Irrigação.',h='IR-02.dc.html',hl='Resolver conflito'),
}
DONO={'OS-0418':('Ana (agrônoma)','vence hoje'),'OS-0420':('Manutenção','OM-0233 até 24/09'),'OS-0421':('Paula','conferir o dia 4 hoje'),
      'OS-0417':('Rui (almoxarife)','24/09'),'OS-0422':('João (irrigante)','definir janela antes do próximo ciclo'),'OS-0423':('Caio (PCP)','resolver conflito hoje antes das 14:00'),
      'OS-0425':('Suprimentos','entrega até 15/10'),'OS-0430':('Ana (agrônoma)','antes de 25/09'),'OS-0431':('PCP','substituto antes de 24/09 06:00')}
SEM_LINK={'OS-0417','OB-0104'}   # CA-02 e CO-06det são ocultas e fixas (Frente F): o painel já traz passo, impedimento e dono
AVISO={'OS-0425':'O lote N26-03 cobre 26,7 dos 38 ha; Suprimentos completa a entrega até 15/10.'}
CJ={c['op']:c for c in D2.CONJ}
# cancelamento sem execução: (o que a confirmação avisa, o que o aviso final diz, nova situação do insumo) — só ordens com reserva ou requisição
CANC={'OS-0424':('Libera a reserva de 65 L do lote F26-02 (REQ-039).','Reserva de 65 L do lote F26-02 liberada.','Reserva de 65 L liberada · lote F26-02 · REQ-039'),
      'OS-0425':('Cancela a requisição REQ-040; nada foi entregue.','Requisição REQ-040 cancelada; nada tinha sido entregue.','REQ-040 cancelada · nada entregue')}
_RED=('impedid','bloquead','atrasad','conflito','vencid')
_SEM_SELO=('Aguardando agrônomo','Aprovada pelo agrônomo','Revisão de saldo pendente','Devolvida para ajuste','Rejeitada')  # O.S. sem revisão (01/10): quem libera vem pela linha de dono
def _selos(o):  # selo principal + selos_extra do registro (mesma lista no Mapa e no detalhe)
    ts=[t for t in ([o['selo']] if o.get('selo') else [])+list(o.get('selos_extra') or []) if not t.startswith(_SEM_SELO)]
    return [dict(t=t,c='red' if any(w in t.lower() for w in _RED) else 'yellow') for t in ts]
def _chaves(o):  # chave cultivo|atividade do registro: texto (um cultivo) ou lista (ordem que cobre vários cultivos)
    k=o.get('chave'); return list(k) if isinstance(k,(list,tuple)) else ([k] if k else [])
def _ordens():
    out=[]
    for o in D.ORDENS+D.ORDENS_LG:
        if o['id'] in LAM: continue   # irrigação só com água fica no módulo Irrigação (IR-03), fora das O.S. de operações agrícolas (01/10)
        ap=[dict(d=d,dia=n,ha=ha,st=s) for d,n,ha,s in AP.get(o['id'],[])]
        out.append(dict(id=o['id'],tipo=TIPO.get(o['id'],o['tipo']),talhao=o['talhao'],talhoes=o.get('talhoes',[]),local=o.get('local',''),ini=o.get('ini',''),fim=o.get('fim',''),area=o.get('area'),etapa=o['etapa'],selos=_selos(o),
                        faz=o['faz'],saf=o['saf'],agua=o['id'] in LAM,obs=OBS.get(o['id'],''),
                        realizado=o.get('realizado'),saldo=o.get('saldo'),resp=o['resp'],keys=_chaves(o),
                        canc=CANC.get(o['id']),
                        versao=VERSAO[o['id']],
                        janela=o['janela'],ap=ap,nota=NOTA_AP.get(o['id'],''),cond=COND[o['id']],orig=ORIG[o['id']],
                        link=('' if o['id'] in SEM_LINK else (o['detalhe'] or '')),dono=DONO.get(o['id'],('',''))[0],prazo=DONO.get(o['id'],('',''))[1],atv=_atv(o),ins=[dict(g=g,p=pr,dose=d,un=u,tot=(t if t is not None else _QTD.qtd(d,o.get('area') or 0)),sit=si) for g,pr,d,u,t,si in INS.get(o['id'],[])],
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
    cult={s['id']:[dict(id=c['id'],t=f"{c['local']} · {c['cultura']} {c['variedade']} · "+format(c['area'],'g').replace('.',',')+" ha",local=c['local'],area=c['area'],plano=c['plano'],var=c['variedade'],cultura=c['cultura'])
                   for c in D2.CULTIVOS.get(s['id'],[])] for s in safs}
    # atividade do plano com seus insumos (grupo, produto, dose/ha): a ordem nova leva dose × área, como as ordens do registro
    planos={p['id']:dict(nome=p['nome'],versao=p['versao'],atv=[dict(id=a['id'],nome=a['nome'],op=a['op'],gat=_gatilho(a.get('g') or {}),
                   ins=[dict(g=x['grupo'],p=x['prod'],dose=x['dose'],un=x['un']) for x in a['prods']]) for a in p['atividades']]) for p in D2.PLANOS}
    prods={}
    for pl in D2.PLANOS:
        for a in pl['atividades']:
            for x in a['prods']: prods.setdefault(x['prod'],dict(p=x['prod'],un=x['un'],g=x['grupo']))
    for l in cenario.seed()['lotes'].values(): prods.setdefault(l['prod'],dict(p=l['prod'],un=l['un'],g=''))
    # A-05 (colheita, 06/10): a ordem nova herda a fazenda da safra e o rótulo de safra do filtro do topo ('Safra Mamão 2026/27' → '2026/27');
    # antes nascia na Santa Rita com saf 'Mamão 2026/27' e sumia do filtro Lagoa Grande · 2026/27
    import re as _re
    _mf=lambda n: (_re.search(r'\d{4}/\d{2}',n).group(0) if _re.search(r'\d{4}/\d{2}',n) and not n.startswith('Safrinha') else n.replace('Safra ',''))
    return dict(safs=[dict(id=s['id'],t=s['nome'],mf=_mf(s['nome']),faz=s.get('fazenda','Santa Rita')) for s in safs],cult=cult,planos=planos,
                conj={op:dict(conj=c['conj'],rend=c['rend']) for op,c in CJ.items()},emb=cenario.EMB,prods=sorted(prods.values(),key=lambda x:x['p']))

JS_NUCLEO=r'''
// ===== núcleo da O.S. (dados do registro + cenário compartilhado, próximo passo e comandos osc_*): usado pela tela O.S. e pelo Mapa =====
function nf(n){ return Number(n||0).toLocaleString('pt-BR'); }
// projeção única das ordens (registro OSD + cenário c): a tela O.S., o Mapa e o Painel Agrícola (agrPainelRef) leem a mesma; não muda c
function osProjecao(c){ const ids={};
  const out=OSD.ords.map(b=>{ ids[b.id]=1; return osMerge(b,c.ordens[b.id],c); });
  Object.keys(c.ordens).forEach(k=>{ const co=c.ordens[k]; if(!ids[k]&&co.osc&&co.osc.novo) out.push(osMerge(co.osc.novo,co,c)); });  // emitidas nesta tela
  return out; }
function ords(self){ return osProjecao(cenGet()); }
// projeção só do estado (Painel): c.ordens decide quais ordens existem; o registro OSD só dá a base de cada uma (mesmo osMerge).
// Estado vazio = []; ordem do registro fora do estado não volta; ordem do estado sem base (nem registro nem emissão) ou sem id/etapa = null.
// pula(id): ordens fora do escopo de quem lê (ex.: beneficiamento OB-), descartadas antes de procurar a base.
function osProjecaoEstado(c,pula){ const E=c&&c.ordens; if(!E||typeof E!=='object'||Array.isArray(E)) return null;
  const reg={}; OSD.ords.forEach(b=>{ reg[b.id]=b; }); const out=[];
  for(const k of Object.keys(E)){ const co=E[k]; if(!co||typeof co.id!=='string'||co.id!==k||typeof co.etapa!=='string') return null;
    if(pula&&pula(k)) continue; const b=reg[k]||(co.osc&&co.osc.novo)||null; if(!b) return null; out.push(osMerge(b,co,c)); }
  return out; }
// impedida: o selo da projeção (o mesmo do cabeçalho da O.S. e do Painel Agrícola)
const OS_IMP_RE=/impedida|falta máquina|falta insumo/i;
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
  const o=Object.assign({},b,{etapa:co.etapa,ap:co.ap||[],req:co.req||null,reservado:!!co.reservado,selos:co.selos||b.selos||[],versao:co.versao||b.versao,r});
  // ajustada ao liberar (osc_ajustar): área e doses do cenário; a linha de histórico entra na Origem
  if(x.aj&&x.aj.length){ o.area=co.area; o.ajv=x.aj[x.aj.length-1].v; o.orig=(b.orig||[]).concat(x.aj.map(a=>a.t));
    o.ins=(co.ins||[]).map(y=>{ const i=(b.ins||[]).find(z=>z.p===y.p); return Object.assign({g:y.g||''},i||{},{p:y.p,dose:y.dose,un:y.un,tot:y.tot,d0:i?i.dose:undefined}); }); }
  if(x.ev&&x.ev.length) o.orig=(o.orig||[]).concat(x.ev.map(e=>e.t));   // aprovação (CMD-42) e liberação (CMD-06) na Origem
  (co.ap||[]).forEach(a=>{ (a.revAnt||[]).forEach(r=>{ o.orig=(o.orig||[]).concat(['Dia '+a.dia+' · '+CEN_DIV+' '+r.dec.toLowerCase()+' por '+r.quem+' às '+r.at+': '+r.txt+' · reaberta: '+r.reaberta]); });
    if(a.rev) o.orig=(o.orig||[]).concat(['Dia '+a.dia+' · '+CEN_DIV+' '+a.rev.dec.toLowerCase()+' por '+a.rev.quem+' às '+a.rev.at+': '+a.rev.txt]); });   // B-R8 (revisão reaberta fica no histórico)
  { const vn=osVn(o.versao); const ap=co.etapa==='A liberar'?osAprovada({osc:x},vn):null;   /* R13: aprovada e ainda não liberada (selo na lista, no Kanban e no painel) */
    o.aprov=ap; if(ap){ o.selos=(o.selos||[]).filter(s=>!/^Aprovada v\d+/.test(s.t)).concat([{t:'Aprovada '+vn+' · aguarda liberação',c:'yellow'}]); o.dono=g2alcQuem('AL-01'); o.prazo='liberar a '+vn; } }
  if(b.area){ o.realizado=co.realizado||0; o.saldo=co.saldo||0; }
  let esp=false, passo='';   /* V55-COMP-02: as regras abaixo que calculam uma pendência específica (dono e prazo dela) marcam esp; o passo da liberação vai junto ao osManCond */
  if(co.etapa!==b.etapa){ o.cond=osCondGen(o); o.dono=co.etapa==='Em conferência'?o.resp:''; o.prazo=co.etapa==='Em conferência'?'conferir':''; }
  if(mine){ o.cond=x.cond; o.dono=x.dono||''; o.prazo=x.prazo||''; }
  if(co.etapa==='A liberar'&&o.cond) o.cond=osCondLib(o.cond);   /* revisão CONF F14: quem aprova e quem libera pela alçada vigente */
  if(x.disp) o.disp=x.disp;
  if(co.etapa==='Canceladas'&&x.insx) o.insx=x.insx;
  if(co.etapa==='Canceladas'){ const cu=r?r.itens.filter(i=>(i.custodia||0)>1e-6):[];   // custódia de ordem cancelada: some só com a devolução no Estoque
    if(cu.length){ o.dono=CEN_CONC_RESP(); o.prazo='receber a devolução'; o.selos=(o.selos||[]).filter(s=>s.t!=='Custódia a devolver').concat([{t:'Custódia a devolver',c:'yellow'}]); }
    else if(mine&&x.dono===CEN_CONC_RESP()){ o.dono=''; o.prazo=''; o.selos=(o.selos||[]).filter(s=>s.t!=='Custódia a devolver'); } }
  // execução com turno no aparelho: o mesmo selo da conferência na lista e no Kanban (o painel e o Mapa dizem "aguardando sinal")
  if(co.etapa==='Em execução'){ o.selos=o.selos.filter(s=>!/^Aguardando sinal/.test(s.t));
    if((co.ap||[]).some(a=>a.sinc===false)) o.selos=o.selos.concat([{t:'Aguardando sinal do app',c:'yellow'}]);
    const fz=((co.saldo||0)-osApPend(co)>0.001)&&cenIniFalta(co,r);   // componente esgotado com área a fazer (regra única de início)
    if(fz&&fz.k==='rever'){ o.selos=o.selos.concat([{t:'Insumo esgotado · '+fz.its.map(i=>i.prod).join(', '),c:'red'}]); o.dono=OS_AGRO(); o.prazo='decidir a área restante';
      o.esg={acao:'apontar',t:'Apontar bloqueado: '+fz.t,q:fz.q}; esp=true; }
    const dpx=(co.ap||[]).filter(a=>a.st===CEN_AP_DUP); if(dpx.length){ o.dono=CEN_CONF_AP(); o.prazo='decidir se o dia '+dpx.map(a=>a.dia).join(', ')+' é outro turno'; esp=true; }   // duplicidade retida: decide a conferência (CMD-09)
    else if(!o.esg&&cenDivAbertas(co).length){ o.dono=OS_AGRO(); o.prazo='revisar a divergência de dose do dia '+cenDivAbertas(co).map(a=>a.dia).join(', '); esp=true; } }   // B-R8: revisão técnica pendente
  if(['Em execução','Em conferência'].includes(co.etapa)&&(co.ap||[]).some(a=>a.conferenciaDia?.caso?.estado==='Em conferência')) o.selos=o.selos.filter(s=>s.t!=='Divergência diária pendente').concat([{t:'Divergência diária pendente',c:'yellow'}]);
  // conferência: o encerramento depende do cenário (apontamento aguardando sinal ou sobra em custódia)
  if(co.etapa==='Em conferência'){ o.encM=cenPodeEncerrar(c,co.id)||cdPendente(c,co.id); esp=!!o.encM;   /* bloqueio do encerramento: carga, divergência, sinal, duplicidade ou sobra */
    if(!o.encM){ o.selos=o.selos.filter(s=>!/Sobras a receber|Aguardando sinal|Conferência diária pendente/i.test(s.t)); if(!mine){ o.cond='Apontamentos enviados e nada em custódia. Próximo passo: conferir e encerrar.'; o.dono=o.resp; o.prazo='conferir e encerrar'; } }
    else if(/^Conferência diária pendente/.test(o.encM)){ o.dono=CEN_CONF_AP(); o.prazo='rever a conferência diária'; o.selos=o.selos.filter(s=>s.t!=='Conferência diária pendente').concat([{t:'Conferência diária pendente',c:'yellow'}]); }
    else if(/^Carga a pesar/.test(o.encM)){ const t=osEncSelo(o.encM);   /* colheita (R-18): carga a pesar ou no aparelho; quem recebe pesa em Agrícola › Recebimento */
      if(!o.selos.some(s=>s.t===t)) o.selos=o.selos.concat([{t,c:'yellow'}]); o.dono=(typeof prRec==='function'?prRec(prFazDaOS(c,co)):'Recebimento'); o.prazo='pesar e receber a carga'; }
    else if(o.encM.indexOf(CEN_DIV)===0){ o.dono=OS_AGRO(); o.prazo='revisar a divergência de dose'; }   /* B-R8: o selo vem do cenário (cenSeloDiv) */
    else { const sin=/sinal/.test(o.encM); const t=osEncSelo(o.encM);  // o bloqueio também na lista e no Kanban
      if(!o.selos.some(s=>s.t===t)) o.selos=o.selos.concat([{t,c:'yellow'}]);
      if(sin){ o.dono=o.resp; o.prazo='reconectar o app'; } else if(/duplicidade/.test(o.encM)){ o.dono=CEN_CONF_AP(); o.prazo='decidir a duplicidade'; } else if(!/almoxarife/.test(o.dono||'')){ o.dono=cenAlmox(); o.prazo='receber a devolução'; } } }
  // A liberar: o Estoque (reserva por lote) pode segurar a liberação desde a abertura → selo vermelho e dono na lista, no Kanban e no painel
  if(co.etapa==='A liberar'&&!o.agua&&(co.ins||[]).length){ const e=osLibErro(o,c); esp=!!e;
    const z=e&&/Dose × área de (.+?) dá 0/.exec(e);   // total 0: quem resolve é o agrônomo, não o Estoque (PRE-REV Y3)
    const lg=!z&&!!e&&e===osUsoErro(c,co);   // regra legal (Frente E): quem resolve é o agrônomo
    if(lg){ const pr=((co.ins||[]).find(x=>osUsoItem(c,co,x))||{}).p||''; o.libErr=e; o.legal=true;
      o.selos=o.selos.filter(s=>!/^Falta insumo|^Total 0|^Fora do registro/.test(s.t)).concat([{t:'Fora do registro · '+pr,c:'red'}]); o.dono=OS_AGRO(); o.prazo='ajustar produto ou dose';
      passo='Próximo passo: ajustar antes de liberar.'; o.cond=String(o.cond||'').replace('Próximo passo: liberar para execução.',passo); }
    else if(z){ o.libErr=e; o.total0=true; o.selos=o.selos.filter(s=>!/^Falta insumo|^Total 0/.test(s.t)).concat([{t:'Total 0 · '+z[1],c:'red'}]); o.dono=OS_AGRO(); o.prazo='ajustar dose ou área';
      passo='Dose × área de '+z[1]+' dá 0. Próximo passo: ajustar antes de liberar.'; o.cond=String(o.cond||'').replace('Próximo passo: liberar para execução.',passo); }
    else if(e){ const pr=(/ de (.+?)(?: no Estoque|:)/.exec(e)||[])[1]||''; o.libErr=e;
      o.selos=o.selos.filter(s=>!/^Falta insumo/.test(s.t)).concat([{t:'Falta insumo'+(pr?' · '+pr:''),c:'red'}]);
      o.dono='Suprimentos'; o.prazo='receber o insumo no Estoque';
      passo='A liberação aguarda '+(pr||'o insumo')+' no Estoque.'; o.cond=String(o.cond||'').replace('Próximo passo: liberar para execução.',passo); } }
  /* SOLO-01 (R20, A21): O.S. em A liberar com dose diferente do uso da análise gravado para a mesma chave cultivo|atividade|produto → selo
     "Plano mudou pela análise"; vem do aceite do cenário, sem recalcular a regra, e some quando a dose da O.S. fica igual à do plano */
  o.planoMudou=null; if(co.etapa==='A liberar'&&!o.agua&&typeof soloAcDaChave==='function'){ const pm=[];
    (b.keys||[]).forEach(k=>(o.ins||[]).forEach(y=>{ const ac=soloAcDaChave(c,k,y.p); if(ac&&(ac.dose==='-'||Math.abs(Number(ac.dose)-Number(y.dose))>1e-9)) pm.push({p:y.p,un:y.un,ac,os:y.dose}); }));
    o.selos=o.selos.filter(s=>!/^Plano mudou/.test(s.t));
    if(pm.length){ const x=pm[0]; o.planoMudou=pm; o.selos=o.selos.concat([{t:'Plano mudou pela análise · '+(x.ac.dose==='-'?'retirar '+x.p:cenNum(x.ac.dose,4)+' '+x.un+'/ha (O.S. '+cenNum(x.os,4)+')'),c:'yellow'}]); } }
  carMerge(o,co,c);   // carência e destino (MAPA-CARENCIA-LMR-20261003 · dados_carencia.JS)
  if(o.carB||o.carE||(o.carCol&&(co.etapa==='Em execução'||co.etapa==='Em conferência'))) esp=true;   /* carMerge deu a pendência ao agrônomo (dono e prazo) */
  osManCond(o,b,c,esp,passo);   /* condição única do ativo (PCM simplificado S3): o bloqueio da máquina vem de c.man, o mesmo da Manutenção e do CD-03 */
  return o; }
/* S3 · F107/F108: ordem que depende de um ativo da Manutenção (bloq.aid) lê a condição única do cenário; bloqueado → impedimento com o dono e o
   link para a OM que trata (MA#om=); apto (CMD-19) → o impedimento sai e a ordem volta à reprogramação do PCP (impedimento derivado: PCMS-A05, Bloco 2) */
function osManCond(o,b,c,esp,passo){ if(!b||!b.bloq||!b.bloq.aid) return; const a=((c&&c.man&&c.man.ativos)||{})[b.bloq.aid]; if(!a) return;
  if(a.cond==='Bloqueado'){ const om=a.condInfo&&a.condInfo.om; o.bloq=Object.assign({},b.bloq,{t:String(b.bloq.t).replace(/\(OM-\d+\)/,'('+(om||'sem ordem que trate')+')')},
      b.bloq.h?{}:{h:'MA.dc.html#'+(om?'om='+om:'ativo='+a.id),hl:om?('Acompanhar '+om):('Abrir '+a.nome+' na Manutenção')}); return; }   /* o link próprio do bloqueio (ex.: ordem completa) fica */
  o.bloq=null; o.selos=(o.selos||[]).filter(s=>!/bloquead|Falta máquina/i.test(s.t));
  /* revisão 09/10 (A5): com a máquina apta sai só o impedimento; o dono volta ao normal da fase. A reprogramação pelo PCP vale uma vez, antes de liberar
     (A liberar); em execução, conferência ou encerrada a ordem segue com o dono da fase (dano evitado: ordem em andamento "com o PCP" para sempre) */
  /* V55-COMP-02: com pendência específica já calculada pelas regras do osMerge (esp: saldo ou lote, lei, total 0, insumo esgotado, duplicidade,
     divergência de dose, bloqueio do encerramento, carência), a máquina apta tira só o impedimento: o dono e o prazo ficam os da pendência e o
     texto troca só a parte da máquina (reprogramar segue como atividade paralela). Ativo apto não encerra a revisão agronômica. Sem pendência
     específica, o padrão de antes: PCP antes de liberar; o dono da fase depois */
  const h=(a.condHist||[]).slice(-1)[0]||{}; const desde=a.nome+' '+a.cond.toLowerCase()+' desde '+String(h.em||'').split('-').reverse().slice(0,2).join('/')+(h.om?' ('+h.om+')':'');
  if(o.etapa==='A liberar'){ o.cond=desde+' · o PCP reprograma a máquina da ordem (O.S. › Recursos); depois '+OS_AGRO()+' confere e libera. Próximo passo: liberar para execução.';
    if(esp){ if(passo) o.cond=o.cond.replace('Próximo passo: liberar para execução.',passo); return; }
    o.dono='PCP'; o.prazo='reprogramar antes de liberar'; return; }
  o.cond=osCondGen(Object.assign({},o,{cond:desde+'.'})); if(esp) return;
  o.dono=o.etapa==='Em conferência'?o.resp:''; o.prazo=o.etapa==='Em conferência'?'conferir':''; }
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
function osInsSit(o,x,it){ if(o.etapa==='Canceladas'){ const ic=o.r&&o.r.itens.find(i=>i.prod===x.p);
    if(ic&&ic.custodia>1e-6) return 'Ordem cancelada · '+nd(ic.custodia)+' '+ic.un+' em custódia com '+(ic.quem||o.resp)+' · receber devolução no Estoque';
    if(ic&&ic.devolvido>0&&ic.entregue>0) return 'Ordem cancelada · '+nd(ic.devolvido)+' '+ic.un+' devolvidos ao Estoque';
    return o.insx||x.sit; }
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
  try { osc_libEfeito(k,o.id,false,o.janela); return ''; } catch (e) { return String(e.message||e); } }   /* o motivo do Estoque, da lei ou da carência; não o perfil */
function osEncBloq(o){ const m=o.encM;
  if(/^Conferência diária pendente/.test(m)) return {acao:'encerrar',t:'Encerrar bloqueado: '+m,q:CEN_CONF_AP()+' resolve na conferência do dia, nos Apontamentos da O.S.'};
  if(String(m).indexOf(CEN_DIV)===0) return {acao:'encerrar',t:'Encerrar bloqueado: divergência de consumo/dose em revisão técnica · '+cenDivAbertas(o).map(a=>'dia '+a.dia+' · '+a.div.map(cenDivTxt).join('; ')).join(' | ')+'.',
    q:OS_AGRO()+', na linha do apontamento: aceita com motivo ou registra a correção ou reaplicação.'};   /* B-R8 */
  if(/^Carga a pesar/.test(m)){ const g=(/CG-\d+/.exec(m)||[''])[0]; return {acao:'encerrar',t:'Encerrar bloqueado: '+m.replace(/\.$/,'')+'.',q:(o.dono||'Recebimento')+' pesa e recebe a carga (registrada por engano: descarta com motivo na mesma tela); a produção do talhão só fecha com ela.',h:'CARGA.dc.html'+(g?'#'+g:''),hl:'Pesar a carga'}; }   /* colheita (R-18) */
  if(/^Carga no aparelho/.test(m)) return {acao:'encerrar',t:'Encerrar bloqueado: '+m.replace(/\.$/,'')+'.',q:(typeof prResp==='function'?prResp(o):o.resp)+' reconecta o app; a carga entra uma vez e vai para a pesagem.'};   /* colheita sem sinal (revisão A-11): não é o recebimento que resolve */
  if(/sinal/.test(m)) return {acao:'encerrar',t:'Encerrar bloqueado: há apontamentos no aparelho aguardando sinal.',q:o.resp+' reconecta o app; o envio é automático e não duplica.'};
  if(/duplicidade/.test(m)) return {acao:'encerrar',t:'Encerrar bloqueado: '+m,q:CEN_CONF_AP()+' decide na linha do apontamento: mesmo turno conta uma vez; outro turno soma.'};
  const its=(o.r?o.r.itens:[]).filter(i=>i.custodia>0.001); const quem=its.map(i=>i.quem||o.resp).filter((v,i,a)=>a.indexOf(v)===i).join(', ')||o.resp;
  return {acao:'encerrar',t:'Encerrar bloqueado: sobra em custódia · '+its.map(i=>{ const pk=osPk(i.custodia,i.emb); return i.prod+' '+nd(i.custodia)+' '+i.un+(pk?' ('+pk+')':''); }).join(', ')+' com '+quem+'.',
    q:cenAlmox()+' recebe a devolução no Estoque.',h:'EST.dc.html',hl:'Receber devolução no Estoque'}; }
// selo do bloqueio do encerramento: o nome (osEncSelo, o mesmo em osMerge) e a dica com quem resolve (osSeloDica) saem do mesmo bloqueio que o
// painel e o comando mostram (osEncBloq, fonte única; revisão DS, achado 6). Outro selo, ou o mesmo antes da conferência: '' (vale o dicionário
// do g2lib). Como a do dicionário, é visual no selo; o teclado e o leitor de tela a recebem na linha ou no cartão focado (g2dicaSelo).
function osEncSelo(m){ return /^Conferência diária pendente/.test(m)?'Conferência diária pendente':/^Carga a pesar/.test(m)?'Carga a pesar':(/sinal/.test(m)?'Aguardando sinal do app':(/duplicidade/.test(m)?'Apontamento em conferência':'Sobras a receber')); }
function osSeloDica(o,t){ if(!o.encM||osEncSelo(o.encM)!==t) return ''; const b=osEncBloq(o); return b.t+' Próximo passo: '+b.q; }
// mudança pela tela: grava no cenário (cenMudar) e redesenha; o erro fica junto ao botão (pa.err) ou vai para onErr
function osRun(self,fn,ok,onErr){ const r=cenMudar(null,fn);
  if(r.erro){ if(onErr) onErr(r.erro); else self.setState({pa:Object.assign({},self.state.pa||{},{err:r.erro})}); return r; }
  self.setState(Object.assign({cenrev:Date.now(),g2toast:r.msg||''},ok||{})); return r; }
// ---------- funções próprias da O.S. sobre o cenário (prefixo osc_; só dentro de cenMudar) ----------
function osc_o(c,id){ const o=c.ordens[id]; if(!o) throw new Error('Ordem '+id+' não encontrada no cenário.'); o.osc=o.osc||{}; return o; }
function osc_txt(o,p){ Object.assign(o.osc,p,{fase:o.etapa}); }
// Aprovar e liberar numa só confirmação (PRD 41.3; padrão adotado em 05/10, o proprietário pode mudar): a O.S. agrícola grava dois
// registros separados na trilha da ordem: aprovação da versão (CMD-42, agrônomo) e liberação (CMD-06). Água só com água (DEC-2609-10)
// não grava CMD-42; manutenção (manLiberar) e beneficiamento não passam por osc_liberar.
// quem aprova (AL-02, CMD-42) e o papel liberador (AL-01, CMD-06) vêm da alçada vigente (G2_ALCADAS + c.conf; CONF-01 R7), não de nome fixo.
// AL-01 = gestor é o padrão dos agentes (PEND-OS-01, 05/10/2026); o proprietário muda em Configurações › Usuários e alçadas (CONF-D10)
function OS_AGRO(){ return g2alcQuem('AL-02'); }   // "Ana (agrônoma)" no seed
function OS_LIB(){ return g2alc('AL-01').papeis; }   // ['gestor'] no seed
// quem confere e libera, pela alçada vigente (revisão CONF F14): o texto do registro (seed e ordem nova) é trocado na tela; mesma pessoa nas duas
// alçadas → "Ana (agrônoma) confere, ajusta se precisar e libera"; pessoas diferentes → "… e aprova; Caio (PCP) libera"
const OS_COND_LIB=['Ana (agrônoma) confere, ajusta se precisar e libera','o agrônomo confere, ajusta se precisar e libera'];   /* seed e ordem nova; v2 da irrigação (irrReclassCen) */
function osLibQuemT(){ const A=g2perfis().filter(P=>g2papel(P,g2alc('AL-02').papeis)), L=g2perfis().filter(P=>g2papel(P,OS_LIB()));
  if(A.length===1&&L.length===1&&A[0].k===L[0].k) return OS_AGRO()+' confere, ajusta se precisar e libera';
  return OS_AGRO()+' confere, ajusta se precisar e aprova; '+g2alcQuem('AL-01')+' libera'; }
function osCondLib(t){ const q=osLibQuemT(); return OS_COND_LIB.reduce((s,x)=>s.split(x).join(q),String(t||'')); }
function osVn(s){ return (String(s||'').match(/\bv\d+\b/g)||['v1']).pop(); }   // versão da ordem: o último vN (fonte única: tela, Mapa e registro)
function osEsc(o){ return cenNum(o.area)+' ha · '+((o.ins||[]).length?o.ins.map(x=>x.p+' '+cenNum(x.dose,4)+' '+x.un+'/ha'+(x.alvo?' para '+x.alvo:'')).join(', '):'sem insumos'); }   /* escopo da versão aprovada */
// aprovação (CMD-42) da versão vigente ainda sem liberação: a ordem segue em A liberar com o selo "Aprovada vN · aguarda liberação" (R13)
function osAprovada(o,vn){ const ev=(o.osc||o.oscx||{}).ev||[]; return ev.find(e=>e.cmd==='CMD-42'&&e.v===vn)||null; }
function osc_aprovLib(o,qa,ql){ const hr=cenAgora(), vn=osVn(o.versao); const ap=qa?null:osAprovada(o,vn);   /* qa/ql: quem aprovou e quem liberou (perfil conferido em osLibPor); qa nulo: a versão já tinha CMD-42 */
  o.osc.ev=(o.osc.ev||[]).concat((qa?[{cmd:'CMD-42',v:vn,por:qa,at:hr,t:vn+' aprovada por '+qa+' às '+hr+' · '+osEsc(o)+' (CMD-42)'}]:[]).concat([
    {cmd:'CMD-06',v:vn,por:ql,at:hr,t:vn+' liberada por '+ql+' às '+hr+(o.reservado&&o.req?' · '+o.req+' reservada no Estoque':'')+' (CMD-06)'}]));
  return qa?' '+vn+' aprovada por '+qa+' e liberada por '+ql+'.':' '+vn+' liberada por '+ql+(ap?'; aprovada antes por '+ap.por+' às '+ap.at:'')+'.'; }   /* o próximo passo fica só no painel (osCondGen) */
// CTL-3 · ATOR: quem aprova (CMD-42, AL-02) e quem libera (CMD-06, AL-01) vêm do perfil de quem age, conferido no cadastro antes de qualquer
// gravação (PRD 41.3 l.6864: "o usuário possuir ambas as permissões"; CMD-06 l.2777). Dano evitado: liberação gravada em nome de quem não decidiu.
// CONF-01 R13 (papéis em pessoas diferentes): quem tem só o AL-01 libera só versão já aprovada e grava só o CMD-06; com a versão já aprovada,
// quem tem os dois grava só o CMD-06. A aprovação de uma versão nunca libera outra (a versão vem de osVn, a mesma do registro).
function osLibPor(ator,id,vn,o){ const hasA=g2papel(ator,g2alc('AL-02').papeis), hasL=g2papel(ator,OS_LIB()); const ap=o?osAprovada(o,vn):null;
  if(hasL&&!hasA){ if(!ap) throw new Error('Aprovação agronômica da '+vn+' da '+id+' pendente: decisão de '+g2alcQuem('AL-02')+'. Nada foi alterado.');
    return [null,cenExigeAlc(ator,'AL-01','Liberar a '+id+' (CMD-06)')]; }
  return [(ap&&hasA)?null:cenExigeAlc(ator,'AL-02','Aprovar a '+vn+' da '+id+' (CMD-42)'),cenExigeAlc(ator,'AL-01','Liberar a '+id+' (CMD-06)')]; }
function osLibTxt(PF,o){ const q=(id)=>{ const a=g2alc(id); return g2papel(PF,a.papeis)?g2ator(PF,a.papeis):g2alcQuem(id); };   /* sem o papel, nomeia quem decide (revisão do CTL-3, achado 1) */
  const ap=o&&o.aprov; if(ap) return q('AL-01')+' libera a '+ap.v+' aprovada por '+ap.por;   /* versão já aprovada (R13): só o CMD-06 */
  return q('AL-02')+' aprova esta versão e '+q('AL-01')+' libera'; }   /* confirmação (O.S. e Mapa) */
// aprovar sem liberar (R13, quem tem só o AL-02): confere a regra legal e o total > 0 antes de gravar e grava só o CMD-42; fica em A liberar
function osc_aprovar(c,id,ator){ const o=osc_o(c,id); const vn=osVn(o.versao); const qa=cenExigeAlc(ator,'AL-02','Aprovar a '+vn+' da '+id+' (CMD-42)');
  if(o.etapa!=='A liberar') throw new Error(id+' não está em A liberar.');
  if(!(o.ins||[]).length&&osSoAgua(o)) throw new Error(id+' é irrigação só com água: libera pela prontidão, sem aprovação agronômica (DEC-2609-10).');
  const ap=osAprovada(o,vn); if(ap) throw new Error('A '+vn+' da '+id+' já está aprovada por '+ap.por+' às '+ap.at+': nada foi gravado de novo.');
  { const z0=(o.ins||[]).find(x=>x.dose>0&&!(x.tot>0)); if(z0) throw new Error('Dose × área de '+z0.p+' dá 0 '+z0.un+': aumente a dose ou a área.'); }
  { const e=osUsoErro(c,o); if(e) throw new Error(e); }   /* regra legal (RN-016), a mesma da liberação */
  const hr=cenAgora(); o.osc.ev=(o.osc.ev||[]).concat([{cmd:'CMD-42',v:vn,por:qa,at:hr,t:vn+' aprovada por '+qa+' às '+hr+' · '+osEsc(o)+' (CMD-42)'}]);
  return {msg:vn+' da '+id+' aprovada por '+qa+' (CMD-42). Fica em A liberar: '+g2alcQuem('AL-01')+' libera para execução e reserva os insumos.'+osUsoAtencao(c,id)}; }
// água só com água (DEC-2609-10) é decidida pela ordem (cadastro de irrigação), não pelo sinal da tela: sem isso o sinal liberaria sem CMD-42
function osSoAgua(o){ return (typeof OSD!=='undefined'&&(OSD.ords||[]).some(b=>b.id===o.id&&b.agua))||/^Irrigação/i.test(String(o.tipo||'')); }
// liberar (agrônomo aprova e liberador libera; pode ajustar antes): reserva por lote (cenLiberar); água sem produto libera pela prontidão, sem requisição
function osc_liberar(c,id,agua,jan,ator){ const o=osc_o(c,id);
  if(agua&&!osSoAgua(o)) throw new Error(id+' não é irrigação só com água: exige aprovação agronômica.');
  const q=agua?null:osLibPor(ator,id,osVn(o.versao),o);
  /* só água (DEC-2609-10): sem aprovação agronômica, mas o CMD-06 tem autor (revisão CONF 13/10): perfil ativo de quem age, conferido antes de gravar,
     e o registro em o.osc.ev (a trilha lê). Sem alçada própria: a AL-01 deixa a água fora (prontidão operacional). Dano evitado: ordem liberada sem autor. */
  const qw=agua?cenQuem(ator===undefined?g2perfil():ator,[],'Liberar a '+id+' (CMD-06, irrigação só com água)'):'';
  const r=osc_libEfeito(c,id,agua,jan); if(q) r.msg+=osc_aprovLib(o,q[0],q[1]);
  if(qw){ const vn=osVn(o.versao), hr=cenAgora(); o.osc.ev=(o.osc.ev||[]).concat([{cmd:'CMD-06',v:vn,por:qw,at:hr,t:vn+' liberada por '+qw+' às '+hr+' · irrigação só com água, sem aprovação agronômica (DEC-2609-10) (CMD-06)'}]);
    r.msg=r.msg.replace(/ liberada pela prontidão operacional\./,' liberada pela prontidão operacional por '+qw+'.'); }
  return r; }
// efeito da liberação, sem o registro de quem decide: só osc_liberar (que grava CMD-42/CMD-06) e a prévia osLibErro (na cópia) o chamam
function osc_libEfeito(c,id,agua,jan){ const o=osc_o(c,id);
  { const cb=carBloqColheita(c,o,'liberar'); if(cb) throw new Error(cb.t); }   // carência (MAPA-CARENCIA-LMR-20261003)
  if(agua){ if(o.etapa!=='A liberar') throw new Error(id+' não está em A liberar.');
    if((o.ins||[]).length) throw new Error(id+' tem produto: exige aprovação agronômica.');   /* o comando não confia no sinal da tela (CTL-1 rev. 3) */
    o.etapa='Liberadas';
    return {msg:id+' liberada pela prontidão operacional. Água sem requisição no Estoque.'}; }
  let r;
  if(!(o.ins||[]).length){  // sem insumo: libera sem requisição (nada a reservar no Estoque)
    if(o.etapa!=='A liberar') throw new Error(id+' não está em A liberar.');
    o.etapa='Liberadas';
    r={msg:id+' liberada. Sem insumos a reservar: nenhuma requisição no Estoque.'}; }
  else { if(!o.ins.some(x=>x.dose>0&&!(x.tot>0))){ const e=osUsoErro(c,o); if(e) throw new Error(e); }   /* regra legal (Frente E1 · RN-016) antes de qualquer gravação; total 0 o cenLiberar recusa */
    const r0=o.req&&c.reqs[o.req];  // requisição aberta antes da liberação, sem entrega: refeita na liberação, com reserva por lote
    if(r0&&!o.reservado){ r0.itens=r0.itens.filter(i=>i.entregue>0); r0.estado='Reservada'; }
    if(!o.req){ const rid=osc_reqId(c); o.req=rid; c.reqs[rid]={id:rid,os:id,itens:[],estado:'Reservada'}; }  // mesmo formato das existentes (REQ-041)
    r=cenLiberar(c,id); }
  return r; }
// ajustar antes de liberar (agrônomo): tirar produto, incluir produto, mudar dose e área; grava a versão seguinte (vN → vN+1) com a
// linha de histórico, recalcula o total (dose × área) e libera no mesmo comando. Erro de saldo/lote desfaz tudo (cenMudar não grava).
// rem = produtos que saem; add = [{p,dose,un,g}] produtos incluídos (do catálogo).
// trava do "Salvar e liberar" do ajuste, a mesma regra da liberação: total pela regra única, 0 recusado, estoque do lote que a liberação reserva
function osc_ajFalta(c,p,un,d,ar){ if(!isFinite(d)||!isFinite(ar)) return 'Dose ou área inválida: informe um número.';   /* não finito antes da conta (PRE-REV U3) */
  const l=cenLote(c,p), dp=l?cenDisp(l):0, need=cenQtd(d,ar);
  if(!(need>0)) return 'Dose × área dá 0 '+un+': aumente a dose ou a área.';
  return need>dp+1e-9?('Estoque: '+cenNum(dp)+' '+un+' disponíveis'+(l?' no lote '+l.lote:'')+' para '+cenNum(need)+' '+un+'. Baixe a dose ou a área, ou troque o produto.'):''; }
function osc_ajustar(c,id,area,doses,jan,rem,add,lib,ator){ const o=osc_o(c,id); const qa=cenExigeAlc(ator,'AL-02','Ajustar a '+id+' (nova versão)');   /* dose e área: decisão do agrônomo (AL-02) */
  if(o.etapa!=='A liberar') throw new Error(id+' não está em A liberar.');
  rem=rem||[]; add=add||[]; o.ins=o.ins||[]; lib=lib!==false;   // lib=false: grava a versão sem liberar (liberação impedida por outro motivo)
  if(!(area>0)) throw new Error('Informe a área maior que 0 ha.'); if(area>o.area+1e-9) throw new Error('Máximo '+cenNum(o.area)+' ha: é a área da ordem.');
  rem.forEach(p=>{ if(!o.ins.some(x=>x.p===p)) throw new Error(p+' não está na ordem.'); });
  add.forEach(a=>{ if(!(a.dose>0)) throw new Error('Informe a dose de '+a.p+' maior que 0 '+a.un+'/ha.');
    if(o.ins.some(x=>x.p===a.p)&&rem.indexOf(a.p)<0) throw new Error(a.p+' já está na ordem: mude a dose na linha dele.'); });
  const ch=[]; if(Math.abs(area-o.area)>1e-9) ch.push('área '+cenNum(o.area)+' → '+cenNum(area)+' ha');
  if(rem.length){ o.ins=o.ins.filter(x=>rem.indexOf(x.p)<0); rem.forEach(p=>ch.push('tirado '+p)); }
  o.ins.forEach(x=>{ const d=(doses||{})[x.p]; if(d===undefined) return; if(!(d>0)) throw new Error('Informe a dose de '+x.p+' maior que 0 '+x.un+'/ha.');
    if(Math.abs(d-x.dose)>1e-9){ ch.push(x.p+' '+cenNum(x.dose,4)+' → '+cenNum(d,4)+' '+x.un+'/ha'); x.dose=d; } });
  add.forEach(a=>{ const x={g:a.g||'',p:a.p,dose:a.dose,un:a.un,tot:0,emb:(typeof OSD!=='undefined'&&OSD.nova&&(OSD.nova.emb||{})[a.p])||''}; if(a.alvo) x.alvo=String(a.alvo);   /* alvo vindo da Consulta Agrofit (CTL-5) */
    o.ins.push(x); ch.push('incluído '+a.p+' '+cenNum(a.dose,4)+' '+a.un+'/ha'+(a.alvo?' para '+a.alvo:'')); });
  if(!ch.length){ if(!lib) throw new Error('Nada foi ajustado.'); const r=osc_liberar(c,id,false,jan,ator); return {msg:'Nada foi ajustado; '+r.msg}; }
  o.area=area; o.saldo=Math.max(0,area-(o.realizado||0)); o.ins.forEach(x=>{ x.tot=cenQtd(x.dose,area); });   /* regra única (SINT-C03) */
  { const z0=o.ins.find(x=>x.dose>0&&!(x.tot>0)); if(z0) throw new Error('Dose × área de '+z0.p+' dá 0 '+z0.un+': aumente a dose ou a área.'); }   /* nem sem liberar (PRE-REV X2) */
  { const e=osUsoErro(c,o); if(e) throw new Error(e); }   /* regra legal, também em Salvar ajuste (Frente E) */
  const s=String(o.versao||''); const re=/\bv(\d+)\b/g; let m=null, k; while((k=re.exec(s))) m=k;
  const vn=m?'v'+(Number(m[1])+1):'v2'; o.versao=m?s.slice(0,m.index)+vn+s.slice(m.index+m[0].length):(s?s+' · ':'')+vn;
  const hr=cenAgora(); o.osc.aj=(o.osc.aj||[]).concat([{v:vn,at:hr,por:qa,t:vn+' ajustada por '+qa+' às '+hr+(lib?' ao liberar':'')+': '+ch.join('; ')}]);
  if(!lib) return {msg:id+' ajustada para '+vn+'. A liberação continua impedida.'+osUsoAtencao(c,id)};
  const r=osc_liberar(c,id,false,jan,ator);
  return {msg:String(r.msg).replace(id+' liberada.',id+' ajustada para '+vn+' e liberada.')+osUsoAtencao(c,id)}; }   /* alertas também no Salvar e liberar (CTL-1 rev. 1) */
// regra legal na O.S. (liberar e ajustar): a mesma do AG-01 (cenUsoLegal), por produto × cultura de cada talhão (ou parcela) da ordem.
// Fertilizante, corretivo, semente, muda e adjuvante ficam fora do registro de agrotóxico; uso só com dose por semente (TS) não é comparado
// por ha. Produto fora de todo cadastro conta como agrotóxico, salvo se o plano o classifica (grupo) como outra coisa.
function osUsoItem(c,o,x,al){ const P=CARD.prod[x.p]; if(P?(!P.defn||P.adj):(x.g&&!/^(Herbicida|Fungicida|Inseticida|Acaricida|Nematicida)/.test(x.g))) return '';
  const ts=carTals(o.talhao); if(!ts.length) return x.p+': o talhão '+(o.talhao||'da ordem')+' não está no cadastro; o registro é por cultura.';
  for(const t of ts){ const cu=carCult(o,t.tid); const u=P?(P.usos||{})[cu]:null;   /* cultura do cultivo da ordem nova (outra safra); senão a do talhão */
    if(u&&!(u.fx||[]).length){ if(/tratamento de sementes/i.test(o.tipo||'')) continue;   /* uso só TS: só em ordem de tratamento de sementes (CTL-1 rev. 2) */
      return x.p+' em '+carNome(t.tid)+(t.parc?' ('+t.parc+')':'')+': registro em '+String(cu).toLowerCase()+' só para tratamento de sementes.'; }
    const us=((u&&u.fx)||[]).map(f=>Object.assign({sit:P.sit},f));
    const ap=carNap(c,t.tid,t.parc,x.p,o); const R=cenUsoLegal(us,String(cu||'a cultura').toLowerCase(),x.dose,x.un,ap.length,ap);
    if(al) R.al.forEach(a=>{ const s=x.p+': '+a.charAt(0).toLowerCase()+a.slice(1); if(al.indexOf(s)<0) al.push(s); });
    if(R.tr.length) return x.p+' '+nd(x.dose)+' '+x.un+'/ha em '+carNome(t.tid)+(t.parc?' ('+t.parc+')':'')+': '+R.tr[0].charAt(0).toLowerCase()+R.tr[0].slice(1);
    /* alvo (vindo da Consulta Agrofit) × referência conferida, a mesma regra do AG-07 (carAlvoRef); dano evitado: aprovação (CMD-42) gravada para
       alvo fora da bula conferida (CTL-5, revisão S3-3) */
    if(x.alvo&&u&&!carAlvoRef(P,cu,x.alvo)) return x.p+' em '+carNome(t.tid)+(t.parc?' ('+t.parc+')':'')+': '+x.alvo+' não está na referência conferida em '+String(cu).toLowerCase()+' ('+(u.al||[]).join('; ')+'). Escolha na Consulta Agrofit um alvo da referência.'; }
  return ''; }
function osUsoErro(c,o,al){ for(const x of (o.ins||[])){ const e=osUsoItem(c,o,x,al); if(e) return e; } return ''; }
function osUsoAtencao(c,id){ const co=c.ordens[id], al=[]; if(co) osUsoErro(c,co,al); return al.length?' Atenção (não bloqueia): '+al.join(' '):''; }   /* alertas na confirmação (O.S. e Mapa) */
// próxima requisição: maior número existente + 1, com três dígitos (REQ-040 → REQ-041), sem pular
function osc_reqId(c){ const n=Object.keys(c.reqs||{}).reduce((m,k)=>Math.max(m,parseInt(String(k).replace(/\D/g,''),10)||0),0)+1;
  return 'REQ-'+String(n).padStart(3,'0'); }
// iniciar exige os insumos com o operador: entregues no Estoque e confirmados no app (água e ordem sem insumo não passam por aqui)
function osIniErro(o,r){ const f=cenIniFalta(o,r); if(!f) return null;   // regra única (cenario.js), a mesma do app
  const L={entregar:['EST.dc.html','Entregar no Estoque'],confirmar:['MB-05.dc.html','Ver no app']}[f.k]||[];
  return {acao:'iniciar',t:'Iniciar bloqueado: '+f.t,q:f.q,h:L[0],hl:L[1]}; }
function osc_iniciar(c,id){ const o=osc_o(c,id); if(o.etapa!=='Liberadas') throw new Error(id+' não está liberada.');
  { const cb=carBloqColheita(c,o,'iniciar'); if(cb) throw new Error(cb.t); }   // carência (MAPA-CARENCIA-LMR-20261003)
  const e=osIniErro(o,o.req&&c.reqs[o.req]); if(e) throw new Error(e.t);
  o.etapa='Em execução';
  return {msg:id+' em execução. Registre o apontamento de cada turno.'}; }
// apontamento pela web (O.S. e Mapa): o mesmo comando do app (cenApontar); cons/est vêm do formulário (osApIns), chave do formulário aberto
function osc_apontar(c,id,d,ha,cons,est,chave){ const R=cenApontar(c,{os:id,d,ha,cons,est,chave,origem:'web'}); const o=c.ordens[id]; const ap=R.ap;
  if(R.repetido) return {msg:'Apontamento do dia '+ap.dia+' já registrado ('+nd(ap.ha)+' ha): nada foi somado de novo.'};
  if(R.dup.length) return {msg:'Apontamento do dia '+ap.dia+' ('+nd(ha)+' ha em '+d+') em conferência: já há '+cenApDupTxt(R.dup)+' nesta data. Nada foi somado nem baixado; '+CEN_CONF_AP()+' decide se é outro turno.'};
  const un=p=>((o.ins||[]).find(x=>x.p===p)||{}).un||''; const ins=Object.keys(ap.cons||{}).map(p=>p+' '+nd(ap.cons[p])+' '+un(p)).join(', ');
  return {msg:'Apontamento do dia '+ap.dia+': '+nd(ha)+' ha (provisório)'+(ins?' · usado: '+ins:'')+'. Saldo '+nf(o.saldo)+' ha; a ordem continua em execução.'+cenDivMsg(ap)
    +(R.ks.length?' Consumo em conferência: '+R.ks.map(k=>cenConfTxt(k,c)).join('; ')+' · '+cenConcQuem(c,R.ks)+'.':'')}; }
function osc_apDecidir(c,id,dia,modo,us,ator){ return cenApDecidir(c,id,dia,modo,ator,us); }   /* CMD-09 (quem confere): 'anterior' | 'este' | 'somar'; us = usado informado na conferência */
// linhas de consumo do formulário (O.S. e Mapa), a mesma regra do MB-03: com o operador, sugere dose × área do trecho (editável, estimativa);
// fora da requisição nada está em custódia: vazio = 0. q = o que vai ao comando; est = sugestão não editada.
function osApIns(c,o,ha,ced){ const r=o.req&&c.reqs[o.req]; const pend=osApPend(o);
  return (o.ins||[]).map((x,i)=>{ const it=r&&r.itens.find(y=>y.prod===x.p); const ed=(ced||{})[x.p]; const vazio=ed===undefined||String(ed).trim()==='';
    const sug=(ha>0&&it&&isFinite(ha))?cenQtdTrecho(x.dose,(o.realizado||0)+pend,ha):null; const tem=it?it.custodia:0;
    const q=!vazio?g2num(ed):(it?(ed===undefined?sug:NaN):0);
    const warn=(q>tem+1e-9)?(ed===undefined?'Sugestão acima do que está em custódia ('+nd(tem)+' '+x.un+'): informe quanto foi usado.':'Acima da custódia ('+nd(tem)+' '+x.un+'): o consumo vai para conferência com '+CEN_CONC_RESP()+'.'):'';
    return {p:x.p,un:x.un,fid:'ap_c'+i,lab:'Usado de '+x.p+' ('+x.un+')',v:ed!==undefined?ed:(sug!==null?String(sug).replace('.',','):''),q,est:ed===undefined,warn,hasWarn:!!warn,
      hint:it?nd(x.dose)+' '+x.un+'/ha × área · em custódia '+nd(tem)+' '+x.un:(r?'Fora da '+r.id+' · nada em custódia':'Sem requisição · nada em custódia')}; }); }
function osApColeta(L){ const cons={},est=[]; let erro='';
  L.forEach(x=>{ if(erro) return; if(isNaN(x.q)||x.q<0){ erro='Informe o usado de '+x.p+' em '+x.un+' (0 se não usou).'; return; } cons[x.p]=x.q; if(x.est) est.push(x.p); });
  return {cons,est,erro}; }
// aviso no formulário (não trava): o mesmo critério do servidor (cenApDup) para a data escolhida, antes de salvar
function osApDupAviso(c,o,d){ const co=c.ordens[o.id]; if(!co||!/^\d\d\/\d\d$/.test(d||'')) return '';
  const l=cenApDup(co,{d,parc:null,chave:'?',origem:'web'}); return l.length?'Já há '+cenApDupTxt(l)+' em '+d+'. Se for outro turno, salve: ele fica em conferência com '+CEN_CONF_AP()+' e só soma depois da decisão.':''; }
// enviar para conferência (CMD-08) e encerrar (CMD-10) gravam quem agiu e a hora em o.osc.fim, uma linha por ato (revisão CONF 10/10, R14):
// ator = perfil de quem age (Ver como; omitido, o da sessão); sem perfil ativo, recusa sem gravar. Não há alçada própria (o PRD diz "regra
// autorizada"): o que segura o encerramento são os requisitos locais (cenPodeEncerrar). Dano evitado: ordem encerrada sem autor rastreável.
function osc_fim(o,cmd,ator,acao){ const quem=cenQuem(ator===undefined?g2perfil():ator,[],acao); o.osc.fim=(o.osc.fim||[]).concat([{cmd,por:quem,at:cenAgora()}]); return quem; }
function osc_conferencia(c,id,ator){ const o=osc_o(c,id); if(o.etapa!=='Em execução') throw new Error(id+' não está em execução.');
  if(o.area&&o.saldo>0.001) throw new Error('Ainda há '+cenNum(o.saldo)+' ha de saldo.'); const quem=osc_fim(o,'CMD-08',ator,'Enviar a '+id+' para conferência (CMD-08)'); o.etapa='Em conferência'; o.selos=[]; cenSeloDiv(c,id);   /* B-R8: a revisão pendente segue visível */
  return {msg:id+' enviada para conferência por '+quem+'.'}; }
// encerrar: só com apontamentos enviados e nada em custódia (cenPodeEncerrar); os apontamentos passam a conferidos
function osc_encerrar(c,id,ator){ const o=osc_o(c,id); if(o.etapa!=='Em conferência') throw new Error(id+' não está em conferência.');
  const m=cenPodeEncerrar(c,id)||cdPendente(c,id); if(m) throw new Error('Encerrar bloqueado: '+m);
  const quem=osc_fim(o,'CMD-10',ator,'Encerrar a '+id+' (CMD-10)'); o.etapa='Encerradas'; o.selos=[]; (o.ap||[]).forEach(a=>{ if(a.st==='Provisório') a.st='Conferido'; });
  return {msg:id+' encerrada por '+quem+'.'}; }
// cancelar sem execução: a reserva ainda não entregue volta ao disponível do lote e a requisição fica cancelada
// CMD-46 (AL-04: responsável do domínio, o gestor; revisão do CTL-3, achado 4): grava quem cancelou e a hora. Dano evitado: ordem aprovada e
// liberada desfeita, com a reserva solta, sem decisão competente e sem autor
// textos do cancelamento lidos da requisição (revisão do 853a6a8, achado 7, S3): com material entregue e ainda não devolvido, nunca "nada tinha sido
// entregue" — a custódia fica com quem recebeu, visível na O.S., e o próximo passo é receber a devolução no Estoque (a demanda já a conta como
// suprimento, cenOsSup). Sem custódia, o texto da tela (cx: confirmação, aviso final, situação do insumo) vale como antes.
function osc_cancCust(c,id){ const o=c.ordens[id]; const r=o&&o.req&&c.reqs[o.req]; return r?r.itens.filter(i=>(i.custodia||0)>1e-6):[]; }
function osc_cancTxt(c,id,cx){ cx=cx||['','','']; const o=c.ordens[id]; const r=o&&o.req&&c.reqs[o.req]; const cu=osc_cancCust(c,id);
  if(!cu.length){ const dv=r?r.itens.filter(i=>(i.entregue||0)>1e-6):[]; if(!dv.length) return cx;   // entregue e já devolvido: o texto não diz "nada entregue"
    const t=dv.map(i=>cenNum(i.entregue)+' '+i.un+' de '+i.prod).join(', ');
    return ['Cancela a requisição '+r.id+'; o que foi entregue ('+t+') já voltou ao Estoque.','Requisição '+r.id+' cancelada; o que foi entregue ('+t+') já tinha voltado ao Estoque.',r.id+' cancelada · entregue e devolvido']; }
  const quem=cu.map(i=>i.quem||o.resp).filter((v,k,a)=>v&&a.indexOf(v)===k).join(', ')||'o operador';
  const ct=cu.map(i=>cenNum(i.custodia)+' '+i.un+' de '+i.prod).join(', '); const um=cu.length===1;
  const sl=o.reservado?r.itens.map(i=>{ const l=c.lotes[i.prod+'|'+i.lote]; const q=l?Math.min(l.reservado||0,Math.max(0,i.solicitado-i.entregue)):0; return q>1e-6?cenNum(q)+' '+i.un+' de '+i.prod:''; }).filter(Boolean).join(', '):'';
  return ['Cancela a requisição '+r.id+(sl?' e libera a reserva não entregue ('+sl+')':'')+'. '+ct+(um?' já entregue fica':' já entregues ficam')+' em custódia com '+quem+' até a devolução no Estoque.',
    'Requisição '+r.id+' cancelada'+(sl?'; reserva não entregue liberada ('+sl+')':'')+'. '+ct+(um?' entregue segue':' entregues seguem')+' em custódia com '+quem+': receba a devolução no Estoque.',
    r.id+' cancelada · '+ct+' em custódia · receber devolução']; }
function osc_cancelar(c,id,mot,cx,ator){ const o=osc_o(c,id); const quem=cenExigeAlc(ator,'AL-04','Cancelar a '+id+' sem execução (CMD-46)');
  if((o.realizado||0)>0||['A liberar','Liberadas'].indexOf(o.etapa)<0) throw new Error('Só ordem sem realizado, em A liberar ou Liberadas, é cancelada sem execução.');
  { const cg=osCargasVivas(c,id); if(cg.length) throw new Error('Cancelar recusado: a '+id+' tem carga '+cg.map(g=>g.id+' '+String(g.st).toLowerCase()).join(', ')+'. Colheita com carga é fato executado: estorne a carga recebida ou descarte a carga a pesar (com motivo) em Agrícola › Recebimento antes de cancelar.'); }
  cx=osc_cancTxt(c,id,cx); const cust=osc_cancCust(c,id).length>0; const r=o.req&&c.reqs[o.req];
  if(r){ if(o.reservado) r.itens.forEach(it=>{ const l=c.lotes[it.prod+'|'+it.lote]; const res=Math.max(0,it.solicitado-it.entregue); if(l&&res>0) l.reservado=Math.max(0,l.reservado-res); }); r.estado='Cancelada'; }
  const hr=cenAgora(); o.etapa='Canceladas'; o.reservado=false; o.selos=[]; osc_txt(o,{canPor:quem,canEm:hr,cond:'Cancelada sem execução por '+quem+' às '+hr+': '+mot+'. '+cx[1],dono:cust?CEN_CONC_RESP():'',prazo:cust?'receber a devolução':'',insx:cx[2]});
  return {msg:(id+' cancelada sem execução. '+cx[1]).trim()+' Cancelada por '+quem+'.'}; }
/* cargas da O.S. de colheita que ainda contam (revisão A-04): a pesar (com ou sem sinal) ou recebidas; estornada e descartada não */
function osCargasVivas(c,id){ return (typeof prCargasOS==='function')?prCargasOS(c,id).filter(g=>g.st==='A pesar'||g.st==='Recebida'):[]; }
// alçada AL-05 (regra única: comando e texto da tela, CONF-01 R11): limite em ha = cenQtd(limite/100, área da ordem), decimal; acima, o nível acima
function osLimDisp(o){ return cenLimDisp(o&&o.area); }
// chave de quem inicia (o painel, ao abrir; ENG-021): a mesma chave não dispensa de novo (cenIdem; revisão CONF 13/10)
function osc_dispensar(c,id,n,mot,ator,chave){ return cenIdem(c,chave,JSON.stringify(['CMD-47',id,Number(n),String(mot||''),(g2pf(ator)||{}).k||'']),'Dispensa',()=>osc_dispensar0(c,id,n,mot,ator)); }
function osc_dispensar0(c,id,n,mot,ator){ const o=osc_o(c,id); let quem=cenExigeAlc(ator,'AL-05','Dispensar saldo da '+id);   /* CMD-47 · AL-05: alçada gerencial e validação agronômica */
  if(o.etapa!=='Em execução') throw new Error(id+' não está em execução.');
  { const dp=(o.ap||[]).filter(a=>a.st===CEN_AP_DUP); if(dp.length) throw new Error('Apontamento em conferência de duplicidade (dia '+dp.map(a=>a.dia).join(', ')+'): '+CEN_CONF_AP()+' decide antes de dispensar o saldo.'); }
  const pap=osApPend(o); if(n>o.saldo-pap+0.001) throw new Error('Máximo '+cenNum(Math.max(0,o.saldo-pap))+' ha: é o saldo da ordem'+(pap?' descontando '+cenNum(pap)+' ha ainda no aparelho.':'.'));
  const tot=(o.osc.disp||0)+n; const L=osLimDisp(o);
  if(o.area>0&&tot>L.ha+1e-9){ const ac=g2alcN(g2alc('AL-05'),'acima');   /* acima do limite: só o nível acima (direção e agrônomo); sem titular, recusa como antes */
    if(!g2papel(ator,ac.papeis)) throw new Error(nd(tot)+' ha = '+nd(100*tot/o.area,1)+' % acima de '+L.pct+' % · exige Direção.'); quem=g2ator(ator,ac.papeis); }
  o.saldo=Math.max(0,o.saldo-n); o.ap=cortaPrev(o.ap,o.saldo);
  const hr=cenAgora(); o.osc.disps=(o.osc.disps||[]).concat([{ha:n,tot,por:quem,at:hr,mot}]);   /* uma linha por CMD-47 (a trilha não perde a 1ª dispensa) */
  osc_txt(o,{disp:tot,dispPor:quem,dispEm:hr,cond:'Saldo de '+nd(n)+' ha dispensado: '+mot+' · decisão gerencial e validação agronômica de '+quem+' às '+hr+'. Realizado de '+nf(o.realizado)+' ha preservado.',dono:'',prazo:''});
  return {msg:'Dispensados '+nd(n)+' ha da '+id+' por '+quem+' · realizado '+nf(o.realizado)+' ha preservado · saldo '+nf(o.saldo)+' ha.'+(o.saldo<=0.001?' Envie a ordem para conferência.':'')}; }
// nova ordem: entra no cenário em A liberar com os insumos da atividade do plano (dose × área) e sem requisição; os textos da tela ficam em osc.novo
/* origem da dose (R21): ordem nova guarda a origem; ajustada pelo agrônomo (dose diferente da do registro) diz a versão; senão o padrão do plano */
function osOrigem(o,x){ if(o.ajv&&(x.d0===undefined||Math.abs(Number(x.d0)-Number(x.dose))>1e-9)) return 'ajustado pelo agrônomo na O.S. '+o.ajv;
  if(x.orig) return x.orig;
  const m=/^(.*) v(\d+)$/.exec(String((o.atv||{}).orig||'')); const pl=m&&typeof OSD!=='undefined'&&OSD.nova?Object.values(OSD.nova.planos).find(q=>q.nome===m[1]):null; return pl?'padrão do plano v'+m[2]:''; }
function osc_nova(c,no){ if(c.ordens[no.id]) throw new Error(no.id+' já existe.');
  const ins=(no.ins||[]).map(x=>({g:x.g||'',p:x.p,dose:x.dose,un:x.un,tot:x.tot,emb:(OSD.nova.emb||{})[x.p]||'',orig:x.orig||''}));   /* g: o grupo vai junto (A4: corretivo fora da trava de agrotóxico) */
  c.ordens[no.id]={id:no.id,tipo:no.tipo,talhao:no.talhao,area:no.area,etapa:'A liberar',versao:no.versao,realizado:0,saldo:no.area,resp:no.resp,ins,req:null,selos:no.selos,ap:[],reservado:false,osc:{novo:no}};
  return {msg:no.id+' emitida em A liberar. Não foi liberada: '+osLibQuemT()+' para execução.'}; }
function nvAtvs(c,pl){ const plO={id:c.plano,versao:pl.versao,atividades:pl.atv.map(a=>({id:a.id,nome:a.nome,op:a.op,gat:a.gat,prods:(a.ins||[]).map(x=>({grupo:x.g,prod:x.p,dose:x.dose,un:x.un}))}))};
  const SA=soloAtividades({id:c.id,plano:plO},{},((cenGet().solo)||{}).aceites||{});
  return SA.atvs.map(x=>({id:String(x.a.id),nome:x.a.nome,op:x.a.op,gat:x.incl?('data '+soloBr(x.a.g.data)):(x.a.gat||''),incl:!!x.incl,laudo:x.ac?x.ac.laudo:'',
    ins:x.prods.filter(q=>q.dose!=='-').map(q=>({g:q.p.grupo,p:q.p.prod,dose:Number(q.dose),un:q.p.un,orig:q.orig==='análise'?'pela análise · '+q.ac.laudo:'padrão do plano v'+pl.versao}))})); }
function cortaPrev(ap,sal){ let rest=sal; const prev=(ap||[]).filter(x=>x.st==='Previsto'); const keep={};
  prev.forEach((x,i)=>{ const ha=Math.max(0,Math.min(x.ha,rest)); rest-=ha; keep[i]=ha; });
  let i=-1; return (ap||[]).map(x=>{ if(x.st!=='Previsto') return x; i++; return keep[i]>0?Object.assign({},x,{ha:keep[i]}):null; }).filter(Boolean); }
function nd(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:0,maximumFractionDigits:(d===undefined?2:d)}); }
// período da coluna Encerradas: da primeira à última data (janela e apontamentos feitos) das ordens da coluna
// próximo passo da fase e o impedimento dele (registro: máquina, janela, conflito · cenário: saldo no Estoque, entrega, sinal ou sobra)
// mesmo cálculo na tela de trabalho da O.S. e no painel do Mapa
function osProx(o,PF){
  let P; const temIns=(o.ins||[]).length>0;
  // A liberar: o agrônomo libera; com produto, pode ajustar dose e área antes (secundário P.sec, fn 'ajustar')
  if(o.etapa==='A liberar') P=o.agua?{t:'Água sem produto: libere pela prontidão operacional (janela, bomba, energia e sem conflito).',btn:'Liberar para execução',fn:'liberar'}
      :temIns?{t:'O agrônomo confere atividade, área, produtos e doses abaixo e libera; se precisar, ajusta antes de liberar. Os insumos são reservados no Estoque.',btn:'Liberar para execução',fn:'liberar',sec:{btn:'Ajustar antes de liberar',fn:'ajustar'}}
      :{t:'O agrônomo confere atividade e área abaixo e libera; se precisar, inclui produto ou ajusta a área antes. Sem insumos a reservar.',btn:'Liberar para execução',fn:'liberar',sec:{btn:'Ajustar antes de liberar',fn:'ajustar'}};
  else if(o.etapa==='Liberadas') P={t:'Confira máquina, equipe e insumos e inicie a execução na janela '+o.janela+'.',btn:'Iniciar execução',fn:'iniciar'};
  else if(o.etapa==='Em execução') P=(o.area&&(o.saldo||0)<=0.001)?{t:'A área toda foi feita. Envie a ordem para conferência.',btn:'Enviar para conferência',fn:'conferencia'}
      :{t:'Registre o apontamento do turno: data e área feita. Os insumos usados são calculados pela dose. Fechar o turno não encerra a ordem.',btn:'Registrar apontamento',fn:'apontar'};
  else if(o.etapa==='Em conferência') P={t:'Confira apontamentos, consumo e sobras e encerre a ordem.',btn:'Conferir e encerrar',fn:'encerrar'};
  else if(o.etapa==='Canceladas') P={t:'Ordem cancelada sem execução: somente consulta.',btn:'',fn:''};
  else P={t:'Ordem encerrada: somente consulta.',btn:'',fn:''};
  /* SOLO-01 (D-08, A14): com o plano mudado pela análise, o texto diz o que mudou; o primário de ajustar vem depois do impedimento (revisão A6) */
  const pm=(o.etapa==='A liberar'&&temIns&&!o.agua&&o.planoMudou)?o.planoMudou[0]:null;
  if(pm) P=Object.assign({},P,{t:'O plano mudou pela análise ('+pm.ac.laudo+'): '+(pm.ac.dose==='-'?'retirar '+pm.p:pm.p+' '+cenNum(pm.ac.dose,4)+' '+pm.un+'/ha')+'; a O.S. tem '+cenNum(pm.os,4)+' '+pm.un+'/ha. O agrônomo ajusta antes de liberar ou libera com a dose da O.S.'});
  // impedimento do próximo passo: do registro (máquina, janela, conflito) ou do cenário (saldo no Estoque; sinal ou sobra no encerramento)
  let b=(o.bloq&&o.bloq.fase===o.etapa&&o.bloq.acao===P.fn)?o.bloq:null;
  if(!b&&P.fn==='liberar'&&!o.agua){ const e=o.libErr||''; if(e) b=o.legal?{acao:'liberar',t:'Liberar bloqueado: '+e,q:OS_AGRO()+', ajustando produto ou dose antes de liberar.',legal:true}:o.total0?{acao:'liberar',t:'Liberar bloqueado: '+e.charAt(0).toLowerCase()+e.slice(1),q:OS_AGRO()+', ajustando a dose ou a área antes de liberar.',total0:true}
      :{acao:'liberar',t:'Liberar bloqueado: '+e.charAt(0).toLowerCase()+e.slice(1),q:'Suprimentos, recebendo o insumo no Estoque.',h:'EST.dc.html',hl:'Ver saldos no Estoque'}; }
  if(!b&&P.fn==='encerrar'&&o.encM) b=osEncBloq(o);
  if(!b&&o.etapa==='Canceladas'){ const cu=o.r?o.r.itens.filter(i=>(i.custodia||0)>1e-6):[];   /* revisão do 853a6a8, achado 7: a custódia não fica sem destino */
    if(cu.length) b={acao:'',tone:'yellow',h:'EST.dc.html',hl:'Receber devolução',t:'Custódia a devolver: '+cu.map(i=>nd(i.custodia)+' '+i.un+' de '+i.prod+' com '+(i.quem||o.resp)).join(', ')+'.',
      q:CEN_CONC_RESP()+' recebe a devolução no Estoque; até lá o material conta como suprimento na demanda de insumos.'}; }
  if(!b&&P.fn==='iniciar'&&!o.agua) b=osIniErro(o,o.r);
  if(!b&&P.fn==='apontar'&&o.esg) b=o.esg;   // componente esgotado: Dispensar saldo segue no painel
  if(!b&&(P.fn==='liberar'||P.fn==='iniciar')&&o.carB) b=Object.assign({},o.carB,{acao:P.fn});   // carência (MAPA-CARENCIA-LMR-20261003)
  const LP=g2alc('AL-02').papeis.concat(OS_LIB().filter(x=>g2alc('AL-02').papeis.indexOf(x)<0));   /* CTL-3 · ATOR: sem os dois papéis (AL-02 e AL-01), a tela diz quem decide; o comando recusa do mesmo jeito */
  /* revisão CONF F4: quem só aprova (AL-02, R13) aprova mesmo com a liberação impedida por estoque ou máquina (osc_aprovar não depende disso);
     só a regra legal, o total 0 e a carência seguram a aprovação. O impedimento segue no texto, para a liberação depois. */
  let espera=null; if(b&&P.fn==='liberar'&&!o.agua&&PF&&!b.legal&&!b.total0&&!o.carB&&!o.aprov&&g2papel(PF,g2alc('AL-02').papeis)&&!g2papel(PF,OS_LIB())){ espera=b; b=null; }
  if(!b&&P.fn==='liberar'&&!o.agua&&PF){ const hasA=g2papel(PF,g2alc('AL-02').papeis), hasL=g2papel(PF,OS_LIB()), vn=osVn(o.versao), ap=o.aprov||null;
    if(hasA&&hasL){ if(ap) P=Object.assign({},P,{t:'Aprovada '+vn+' por '+ap.por+'. Confira máquina, janela e insumos e libere; os insumos são reservados no Estoque.',sec:null}); }   /* versão já aprovada: só o CMD-06 */
    else if(hasA){ /* CONF-01 R13: só o AL-02 aprova (CMD-42) e a ordem fica em A liberar; o liberador libera depois */
      if(!ap) P=Object.assign({},P,{t:'Confira atividade, área, produtos e doses e aprove a '+vn+'; se precisar, ajuste antes. '+g2alcQuem('AL-01')+' libera depois e reserva os insumos no Estoque.'
        +(espera?' A liberação aguarda: '+String(espera.t).replace(/^Liberar bloqueado: /,'').replace(/\.$/,'')+' ('+String(espera.q||'').replace(/\.$/,'')+').':''),btn:'Aprovar '+vn,fn:'aprovar',sec:P.sec?{btn:'Ajustar antes de aprovar',fn:'ajustar'}:null});
      else b={acao:'liberar',t:'Aprovada '+vn+' por '+ap.por+': aguarda liberação.',q:g2alcQuem('AL-01')+' libera para execução; o perfil '+PF.t+' aprova, não libera.',tone:'yellow',papel:true}; }
    else if(hasL){ if(!ap) b={acao:'liberar',t:'Aprovação agronômica da '+vn+' pendente: decisão de '+g2alcQuem('AL-02')+'.',q:g2alcQuem('AL-02')+' aprova esta versão; depois '+g2ator(PF,OS_LIB())+' libera.',tone:'yellow',papel:true};
      else P=Object.assign({},P,{t:'Aprovada '+vn+' por '+ap.por+'. Confira máquina, janela e insumos e libere; os insumos são reservados no Estoque.',sec:null}); }
    else b={acao:'liberar',t:'Liberar para execução: decisão de '+(g2quem(LP)||g2alcQuem('AL-02')+' e '+g2alcQuem('AL-01'))+'.',q:OS_AGRO()+' aprova esta versão e '+g2alcQuem('AL-01')+' libera; o perfil '+PF.t+' não tem esses papéis.',tone:'yellow',papel:true}; }
  /* SOLO-01 · revisão A6: plano mudado e quem age é agrônomo (ou sem perfil, nos testes) → primário "Ajustar antes de liberar". "Liberar com a dose
     da O.S." só fica como secundário quando nada impede liberar; o impedimento (estoque, regra legal, carência, total 0, papel) continua visível e
     não esconde o ajuste (keep). Sem o papel de agrônomo, o passo segue liberar com o impedimento de quem decide. Dano evitado: botão sem efeito e
     uma liberação oferecida que o comando recusa. */
  if(pm&&(!PF||(g2papel(PF,g2alc('AL-02').papeis)&&g2papel(PF,OS_LIB())))){   /* v57 (CONF R13): só quem aprova e libera; quem só aprova segue o "Aprovar vN" */ P={t:P.t,btn:'Ajustar antes de liberar',fn:'ajustar',sec:b?null:{btn:'Liberar com '+cenNum(pm.os,4)+' '+pm.un+'/ha',fn:'liberar'}};
    if(b) b=Object.assign({},b,{keep:true}); }
  return {P,b}; }
'''
JS=r'''
const FASES=['A liberar','Liberadas','Em execução','Em conferência','Encerradas'];
const FCOR={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray','Canceladas':'gray'};
const STCOR={'Conferido':'green','Provisório':'yellow','Previsto':'gray','Aguardando sinal':'yellow',[CEN_AP_DUP]:'yellow',[CEN_AP_DESC]:'gray'};
function GR(id){ return GRIDS.find(g=>g.id===id); }
function chipSt(c){ const cc=G2C[c]||G2C.gray; return 'display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';'; }
function dotSt(c){ const cc=G2C[c]||G2C.gray; return 'width:6px;height:6px;border-radius:999px;flex-shrink:0;background:'+cc[0]+';'; }
// ===== O.S. × cenário compartilhado (cenario.js, o mesmo estado do Estoque e do App) =====
// Fase, realizado/saldo, apontamentos, requisição e insumos vêm de cenGet(); o que o cenário não tem vem de OSD (registro).
// Gancho de teste/inspeção (o script da tela roda isolado): os testes os_* leem e mudam o cenário na própria página.
try { window.__cen = { cenGet, cenMudar, cenReset, cenLiberar, cenEntregar, cenDevolver, cenConfirmarRecebimento, cenIniciarTurno, cenPausar, cenFecharTurno, cenOcorrencia, cenSinal, cenPodeEncerrar, osc_liberar, osc_ajustar, osc_encerrar, osc_apontar, osc_dispensar, osc_cancelar, osc_apDecidir, osc_conferencia, cenDivRever }; } catch (e) {}
// filtros do topo (Fazenda e Safra): lista, Kanban, chips de fase e selo do cabeçalho mostram só as ordens do recorte
function mfFaz(self){ return self.state.mf_faz||'Santa Rita'; }
function mfSaf(self){ return self.state.mf_saf||'Todas'; }
function mfCult(self){ return self.state.mf_cult||'Todas'; }   // 13/10: Cultura no filtro principal (cultura do cultivo de cada talhão da ordem)
function osCults(o){ return o.culturas||(o.cultura?[o.cultura]:[]); }
function vis(self,semCult){ const f=mfFaz(self), s=mfSaf(self), cu=semCult?'Todas':mfCult(self); return ords(self).filter(o=>(f==='Todas'||o.faz===f)&&(s==='Todas'||o.saf===s)&&(cu==='Todas'||osCults(o).indexOf(cu)>=0)); }
function localTxt(o){ return o.talhao+(o.area?' · '+nf(o.area)+' ha':''); }
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
  // TABELAS-FOCO (5983172395): uma variável por coluna; Talhão é vínculo estruturado (fazenda|ID), filtrado por pertinência
  g2keep(self,'g_os',{topo:true,v});   /* VISOES-1 §2.3: Fazenda e Safra do topo voltam junto com os filtros da grade */
  const todas=mfFaz(self)==='Todas';
  const tals=(o)=>(o.talhoes||[]).map(t=>({id:o.faz+'|'+t.id,l:todas?t.nome+' · '+o.faz:t.nome}));
  // troca de fazenda/safra: o talhão escolhido fora do novo recorte sai do filtro, com aviso (nunca muda fazenda/safra para "caber")
  const ctx=mfFaz(self)+'|'+mfSaf(self)+'|'+mfCult(self); if(self.__osCtx!==undefined&&self.__osCtx!==ctx){ const st0=g2st(self,'g_os'), ft=((st0.f||{}).tal)||[];
    if(ft.length){ const ok=new Set(); os.forEach(o=>tals(o).forEach(t=>ok.add(t.id))); const fica=ft.filter(k=>k==='(vazio)'||ok.has(k)), sai=ft.filter(k=>fica.indexOf(k)<0);
      if(sai.length){ const f=Object.assign({},st0.f||{}); if(fica.length) f.tal=fica; else delete f.tal; const all=Object.assign({},self.state.g2||{}); all.g_os=Object.assign({},st0,{f}); self.state.g2=all;
        g2keepGrava(self,'g_os');
        self.__osMsg='Talhão fora de '+(mfFaz(self)==='Todas'?'todas as fazendas':mfFaz(self))+(mfSaf(self)==='Todas'?'':' · '+mfSaf(self))+(mfCult(self)==='Todas'?'':' · '+mfCult(self))+': '+sai.map(k=>{ const id=k.split('|')[1]; const t=ords(self).map(o=>(o.talhoes||[]).find(x=>x.id===id)).find(Boolean); return t&&t.nome?t.nome:id; }).join(', ')+' saiu do filtro.'; } } }   /* o nome que a pessoa escolheu ("Pivô 4"), não o ID */
  self.__osCtx=ctx;
  const nfx=(x)=>x===null||x===undefined||x===''?null:x;
  // o texto de pendência mistura próxima ação e prazo ("entrega até 15/10"); na tabela vira duas colunas (uma variável por coluna)
  const pzx=(t)=>{ t=String(t||''); const m=t.match(/(?:vence\s+)?(?:hoje\s*)?(?:(?:até|antes de|antes das|em)\s+)?(?:\d{2}\/\d{2}(?:\s+\d{2}:\d{2})?|\d{2}:\d{2})|(?:vence\s+)?hoje/);
    if(!m) return [t.trim(),'']; return [(t.slice(0,m.index)+' '+t.slice(m.index+m[0].length)).replace(/\s+/g,' ').trim(), m[0].replace(/^vence\s+/,'').trim()]; };
  const base=os.map(o=>{ const tl=tals(o), sel=o.selos.map(x=>({id:x.t,l:x.t}));
   return {id:o.id,
    m:{tal:tl,sit:sel},
    v:{id:o.id,ativ:o.tipo,tal:'',local:o.local||'',area:nfx(o.area),ini:o.ini||'',fim:o.fim||'',fase:o.etapa,sit:'',obs:o.obs||'',dono:o.dono||'',acao:pzx(o.prazo)[0],prazo:pzx(o.prazo)[1],
       real:(o.area?o.realizado:null),saldo:(o.area?o.saldo:null),disp:(o.disp||null),prog:(o.area?Math.round(1000*(o.realizado||0)/o.area)/10:null),resp:o.resp},
    s:{id:o.id,tal:tl.map(t=>t.l).join(', '),sit:sel.map(x=>x.l).join(' · ')},
    p:{id:[{k:'b',t:o.id}],tal:(tl.length?tl.map(t=>({k:'txt',t:t.l})).reduce((a,x,i)=>a.concat(i?[{k:'br'},x]:[x]),[]):[{k:'mut',t:'—'}]),
       fase:[{k:'chip',t:o.etapa,c:FCOR[o.etapa],de:1}],sit:(o.selos.length?o.selos.map(x=>({k:'chip',t:x.t,c:x.c,de:1,dv:osSeloDica(o,x.t)})):[{k:'mut',t:'—'}])}}; });   /* de: dica de estado (g2lib G2_DICAS); dv: a do bloqueio do encerramento (osSeloDica) */
  // Agrupar por talhão (TABELAS-FOCO item 7, TF06): a mesma O.S. aparece em cada talhão vinculado, com a mesma identidade; o grupo conta
  // O.S. distintas e soma a área das O.S. vinculadas (não é área física do talhão); o total geral conta cada O.S. uma vez (abaixo, os_gtot)
  /* VISOES-1: a Tabela agrupada é a visão "agrupada" do seletor (o mesmo painel da Lista); os grupos começam abertos ao entrar nela */
  const agr=g2visao(self,'g_os')==='agrupada';
  if(agr!==!!self.__osAgrX){ self.__osAgrX=agr; const x={}; if(agr) base.forEach(r=>(r.m.tal.length?r.m.tal:[{id:'(vazio)'}]).forEach(t=>{ x['grp@'+t.id]=true; }));
    const all=Object.assign({},self.state.g2||{}); all.g_os=Object.assign({},all.g_os||{},{x}); self.state.g2=all; }
  if(agr){ const stG=g2st(self,'g_os'), ft=((stG.f||{}).tal)||[]; const gs={}, ord=[];
    // revisão VISOES-1, achado C1 (S2): o grupo nasce só das O.S. do recorte (fase, busca e filtros de coluna, o mesmo g2match do Total):
    // antes ele somava todas as O.S. do talhão e o subtotal desmentia o Total na mesma tela
    base.filter(r=>g2match(r,GR('g_os'),stG)).forEach(r=>{ const ms=r.m.tal.length?r.m.tal:[{id:'(vazio)',l:'Sem talhão'}];
      ms.forEach(t=>{ if(ft.length&&ft.indexOf(t.id)<0) return; if(!gs[t.id]){ gs[t.id]={t,kids:[]}; ord.push(t.id); } gs[t.id].kids.push(Object.assign({},r,{id:r.id+'@'+t.id})); }); });
    ord.sort((a,b)=>gs[a].t.l.localeCompare(gs[b].t.l,'pt-BR',{numeric:true}));
    GR('g_os').rows=ord.map(k=>{ const g=gs[k], n=g.kids.length, ar=g.kids.reduce((a,x)=>a+(Number(x.v.area)||0),0);
      return {id:'grp@'+k,ro:true,m:{tal:(k==='(vazio)'?[]:[g.t]),sit:[]},kids:g.kids,
        v:{id:g.t.l,ativ:'',tal:'',area:ar||null},s:{id:g.t.l,tal:g.t.l},
        p:{id:[{k:'b',t:g.t.l}],ativ:[{k:'mut',t:n+(n>1?' O.S. vinculadas · área somada das O.S.':' O.S. vinculada · área da O.S.')}],area:(ar?[{k:'txt',t:nf(ar)}]:[{k:'mut',t:'—'}])}}; });
  } else GR('g_os').rows=base;
  self.__osBase=base;
}
// turnos previstos acompanham o saldo depois de uma dispensa (corta do último para o primeiro)
function osPeriodo(cs){ const ds=[]; const add=(d,m)=>ds.push([Number(m),Number(d)]); const z=(n)=>('0'+n).slice(-2);
  cs.forEach(o=>{ const j=String(o.janela||''); const r=/(\d{1,2})–(\d{1,2})\/(\d{2})/.exec(j);
    if(r){ add(r[1],r[3]); add(r[2],r[3]); } else { const s=/(\d{1,2})\/(\d{2})/.exec(j); if(s) add(s[1],s[2]); }
    (o.ap||[]).forEach(a=>{ if(a.st==='Previsto') return; const s=/(\d{1,2})\/(\d{2})/.exec(a.d||''); if(s) add(s[1],s[2]); }); });
  if(!ds.length) return ''; ds.sort((a,b)=>a[0]-b[0]||a[1]-b[1]); const a=ds[0], b=ds[ds.length-1];
  if(a[0]===b[0]&&a[1]===b[1]) return 'em '+z(a[1])+'/'+z(a[0]);
  return 'período '+z(a[1])+(a[0]===b[0]?'':'/'+z(a[0]))+'–'+z(b[1])+'/'+z(b[0]); }
// painel por fase: aberto só o que faz a ordem andar nesta fase; o resto fica recolhido com uma linha de resumo
function panSecs(self,v,o){ const f=o.etapa; const sx=((self.state.psx||{})[o.id])||{}; const a=o.atv||{};
  const DEF={'A liberar':['ins','rec'],'Liberadas':['ins','rec'],'Em execução':['ap','ins'],'Em conferência':['ap','ins'],'Encerradas':['ap'],'Canceladas':['sit','ins']}[f]||['ins'];
  const ins=v.pan_ins||[], rec=v.pan_rec||[], nal=rec.reduce((t,r)=>t+(r.al||[]).length,0), nap=(o.ap||[]).length, cond=String(o.cond||'');
  const sum={atv:[a.op,a.nome||o.tipo,a.conj].filter(Boolean).join(' · '),
    ins:ins.length?(ins.length+(ins.length>1?' insumos':' insumo')+' · '+ins.map(x=>x.p).slice(0,2).join(', ')+(ins.length>2?'…':'')):'sem insumos',
    rec:rec.length+(rec.length>1?' recursos':' recurso')+(nal?' · '+nal+(nal>1?' conflitos':' conflito'):' · sem conflito'),
    ap:nap?(nap+(nap>1?' turnos':' turno')+(o.area?' · '+nf(o.realizado||0)+' / '+nf(o.area)+' ha':'')):'sem apontamentos',
    sit:cond.length>90?cond.slice(0,90)+'…':cond, ori:(o.orig||[]).length+((o.orig||[]).length>1?' registros':' registro')};
  const show={atv:true,ins:true,rec:rec.length>0,ap:nap>0||['Em execução','Em conferência','Encerradas'].indexOf(f)>=0,sit:!!cond,ori:(o.orig||[]).length>0};
  Object.keys(sum).forEach(k=>{ const open=(sx[k]!==undefined)?!!sx[k]:DEF.indexOf(k)>=0;
    v['psx_'+k]=open; v['psx_'+k+'_c']=!open; v['psx_'+k+'_ex']=open?'true':'false'; v['psx_'+k+'_sum']=sum[k]; v['psx_'+k+'_show']=show[k];
    // registro síncrono das seções abertas: cliques seguidos (antes do novo desenho) não se sobrescrevem
    v['psx_'+k+'_tog']=()=>{ const all=self.__psx||(self.__psx=JSON.parse(JSON.stringify(self.state.psx||{}))); const cur=all[o.id]||(all[o.id]={});
      const now=(cur[k]!==undefined)?!!cur[k]:DEF.indexOf(k)>=0; cur[k]=!now; self.setState({psx:JSON.parse(JSON.stringify(all))}); }; });
  // resumo do topo: onde, quanto, quando, quem e o avanço da área
  v.pan_res=[String(o.talhao||'').split(' · ')[0]+(o.area?' · '+nf(o.area)+' ha':''),o.janela?'janela '+o.janela:'',o.resp].filter(Boolean).join(' · ');   // a lâmina e o detalhe ficam nas seções
  const pct=o.area?Math.round(100*(o.realizado||0)/o.area):0; v.pan_hasProg=!!o.area&&(o.realizado||0)>0;
  v.pan_prog=nf(o.realizado||0)+' / '+nf(o.area||0)+' ha · '+pct+' %'+(o.saldo?' · saldo '+nf(o.saldo)+' ha':''); v.pan_progst='height:6px;border-radius:999px;background:#1E7A4C;width:'+Math.min(100,pct)+'%;'; }
// tela de trabalho da ordem: atividade, insumos e doses, e o botão do próximo passo da fase
function osWork(self,v,o){ const st=self.state; const a=o.atv||{}; const PF=g2perfil();   /* quem age (perfil de demonstração; CTL-3) */
  const kv=[['Operação',a.op||'—'],['Atividade',a.nome||o.tipo],['Gatilho',a.gat||'—'],['Local · área',o.talhao+(o.area?' · '+nf(o.area)+' ha':'')],['Janela',o.janela],['Responsável',o.resp]];
  if(a.conj){ kv.push(['Conjunto',a.conj+' · '+nd(a.rend)+' ha/h']); if(o.area) kv.push(['Horas previstas',nd(o.area/a.rend,1)+' h ('+nd((o.saldo||0)/a.rend,1)+' h no saldo)']); }
  const vp=String(o.versao).split(' · ').filter(p=>(a.orig||'').indexOf(p)<0); if(o.ajv&&vp.indexOf(o.ajv)<0) vp.push(o.ajv);  // ajustada ao liberar: a versão nova sempre aparece
  kv.push(['Padrão · versão',[a.orig||'—'].concat(vp).join(' · ')]);  // sem repetir a recomendação
  v.pan_atv=kv.map(x=>({l:x[0],v:x[1]}));
  // insumos: usado = consumido pelos apontamentos (cenário); situação e trilha do almoxarifado ao app, por item da requisição
  v.pan_ins=(o.ins||[]).map(x=>{ const it=(o.r&&o.etapa!=='Canceladas')?(o.r.itens.find(i=>i.prod===x.p)||null):null;
    const usado=it?it.consumido:((o.id==='OS-0417')?x.tot:(o.area?cenQtd(x.dose,o.realizado||0):0)); const tr=osTrilha(o,it);
    const og=osOrigem(o,x);
    return {p:x.p,g:(x.g||'')+(og?((x.g?' · ':'')+og):''),dose:nd(x.dose)+' '+x.un+'/ha',tot:nd(x.tot)+' '+x.un,usado:(usado?nd(usado)+' '+x.un:'—'),sit:osInsSit(o,x,it),tr,hasTr:tr.length>0}; });
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
  // próximo passo por fase e impedimento (osProx, o mesmo do Mapa)
  const pb=osProx(o,PF); const P=pb.P; let b=pb.b;
  v.pan_dono=(!b&&o.dono)?('Pendência com '+o.dono+' · '+o.prazo):''; v.pan_hasDono=!!v.pan_dono;
  v.pan_pt=P.t; v.pan_pbtn=P.btn; v.pan_hasBtn=!!P.btn&&(!b||!!b.keep); v.pan_bloq=!!b; v.pan_bt=b?b.t:''; v.pan_bq=b?('Quem resolve: '+b.q):'';
  v.pan_hasBl=!!(b&&b.h); v.pan_bh=(b&&b.h)||'#'; v.pan_bhl=(b&&b.hl)||'';
  carOsVals(self,v,o,b);   // carência: Rever programação da colheita (MAPA-CARENCIA-LMR-20261003)
  if(v.pan_retLink&&b&&b.h==='EST.dc.html'){ v.pan_retLink=false; v.pan_retT='Fichas de execução'; v.pan_hasRet=v.pan_hasPrep||v.pan_fichas; }  // o impedimento já leva ao Estoque: sem link duplicado
  v.pan_aviso=(o.aviso&&o.etapa==='Liberadas')?o.aviso:''; v.pan_hasAviso=!!v.pan_aviso;
  v.pan_obs=o.obs?(o.obs.charAt(0).toUpperCase()+o.obs.slice(1)+' (não bloqueia).'):''; v.pan_hasObs=!!o.obs&&o.etapa==='A liberar';
  const bam=b&&b.tone==='yellow';  // pendência que não é impedimento (ex.: janela a definir) fica amarela
  v.pan_btst='font-size:13px;font-weight:700;line-height:1.45;color:'+(bam?'#8A5A00':'#B42318')+';';
  v.pan_pst='display:flex;flex-direction:column;gap:8px;padding:12px 14px;border-radius:12px;'+(b?(bam?'background:#FFF3D6;border:1px solid #F0D9A0;':'background:#FDE8E6;border:1px solid #F4C7C1;'):(P.btn?'background:#E4F3E9;border:1px solid #BFE0CB;':'background:#F4F6F3;border:1px solid #E4E9E5;'));
  const pa=(st.pa&&st.pa.id===o.id)?st.pa:null;
  const apP=osApPend(o), apMax=Math.max(0,(o.saldo||0)-apP);
  v.pan_go=()=>{ if(P.fn==='ajustar'){ v.pan_ajgo(); return; } if(P.fn==='apontar'){ const prox=(o.ap||[]).find(x=>x.st==='Previsto'); self.setState({pa:{id:o.id,fn:'apontar',d:CEN_DIA_OP,ha:String(Math.min(apMax,prox?prox.ha:apMax)).replace('.',','),ced:{},chave:'W-'+o.id+'-'+Date.now(),err:''}}); return; } self.setState({pa:{id:o.id,fn:P.fn}}); };
  // confirmação e formulários de decisão só com o papel: aberto por outro perfil (troca no seletor ou em outra aba), não aparece (achado 1)
  const DSP=g2alc('AL-05').papeis, agr=g2papel(PF,DSP), gest=g2papel(PF,g2alc('AL-04').papeis), AGR=g2papel(PF,g2alc('AL-02').papeis);   /* dispensa (CMD-47; AL-05); cancelar (CMD-46; AL-04); ajustar (AL-02): da alçada vigente */
  const paOk=!!pa&&({ajustar:AGR,dispensar:agr,cancelar:gest,aprovar:AGR}[pa.fn]!==false)&&!(pa.fn==='liberar'&&b&&b.papel)&&!(pa.fn==='aprovar'&&P.fn!=='aprovar');
  v.pan_conf=paOk&&['liberar','aprovar','iniciar','conferencia','encerrar'].indexOf(pa.fn)>=0; v.pan_apf=paOk&&pa.fn==='apontar'; v.pan_ajf=paOk&&pa.fn==='ajustar'; v.pan_idle=!paOk;
  v.pan_canf=paOk&&pa.fn==='cancelar'; v.pan_disf=paOk&&pa.fn==='dispensar';
  v.pan_rmot=(pa&&pa.motivo)||''; v.pan_rerr=(pa&&pa.err)||''; v.pan_hasRerr=!!(pa&&pa.err);
  v.pan_setrmot=(e)=>self.setState({pa:Object.assign({},self.state.pa,{motivo:e.target.value,err:''})});
  // ajustar antes de liberar (secundário do passo A liberar com produto, também na confirmação): dose por insumo e área → osc_ajustar
  v.pan_hasAj=!!P.sec&&AGR; v.pan_hasAjc=v.pan_hasAj&&!b&&!!pa&&pa.fn==='liberar'; v.pan_ajbtn=P.sec?P.sec.btn:'';
  v.pan_secgo=()=>{ if(P.sec&&P.sec.fn==='liberar') self.setState({pa:{id:o.id,fn:'liberar'}}); else v.pan_ajgo(); };   /* SOLO-01: com o plano mudado, o secundário libera com a dose da O.S. */
  if(o.planoMudou&&pa&&pa.fn==='liberar') v.pan_hasAjc=false;
  const ajAp=AGR&&!g2papel(PF,OS_LIB());   /* CONF-01 R13: quem só aprova grava a versão nova e aprova (CMD-42) no mesmo comando; não libera */
  const ajLib=!ajAp&&(!b||b.h==='EST.dc.html'||!!b.total0||!!b.legal);   // falta no Estoque: o ajuste pode resolver e libera; máquina, janela ou conflito: só grava a versão
  const vcur=osVn(o.versao); const vnx='v'+(Number(vcur.slice(1))+1);
  v.pan_ajsbtn=ajAp?'Salvar e aprovar '+vnx:(ajLib?'Salvar e liberar':'Salvar ajuste');
  // us = produto vindo do "Usar na O.S." do AG-07 ({p,cul,alvo}): entra como incluído, dose em branco (nunca o último valor)
  // SOLO-01: com o plano mudado pela análise, o ajuste abre com a dose do plano (ou o produto a retirar marcado), não com a da O.S.
  const pmD=(p)=>((o.planoMudou||[]).find(z=>z.p===p)||null);
  const ajAbrir=(us)=>{ const ds={}, rm={}; (o.ins||[]).forEach(x=>{ const z=pmD(x.p); if(z&&z.ac.dose==='-') rm[x.p]=true; ds[x.p]=nd(z&&z.ac.dose!=='-'?z.ac.dose:x.dose,4); }); let add=[], qerr='', foco='aj_d0';
    if(us&&us.p){ const x=((OSD.nova&&OSD.nova.prods)||[]).find(y=>y.p===us.p), i=(o.ins||[]).findIndex(y=>y.p===us.p);
      if(i>=0){ qerr=us.p+' já está na ordem: mude a dose na linha dele.'; foco='aj_d'+i; }
      else if(!x) qerr=us.p+': produto não encontrado no cadastro da fazenda.';
      else { add=[{p:x.p,un:x.un,g:x.g,dose:'',alvo:us.alvo,cul:us.cul}]; foco='aj_n0'; } }
    /* chegada da Consulta Agrofit: a mensagem diz o que mudou e a linha incluída fica destacada (.g2flash) por 1,5 s (revisão do CTL-5, S4-2) */
    const vem=us&&us.p?{g2toast:'Vindo da Consulta Agrofit: '+(add.length?(us.p+' incluído na '+o.id+' para '+us.alvo+(us.cul?' em '+String(us.cul).toLowerCase():'')+'. Informe a dose e salve.'):qerr),ajFlash:add.length?us.p:''}:{};
    self.setState(Object.assign({pa:{id:o.id,fn:'ajustar',area:nd(o.area,4),doses:ds,rem:rm,add,q:'',qerr,errs:{},err:''}},vem));
    if(vem.ajFlash) setTimeout(()=>{ if(self.state.ajFlash===vem.ajFlash) self.setState({ajFlash:''}); },1500);
    setTimeout(()=>{ const el=document.getElementById(foco)||document.getElementById('aj_d0')||document.getElementById('aj_area'); if(el) el.focus(); },60); };
  v.pan_ajgo=()=>ajAbrir(null);
  if(self.__ajAuto===o.id){ self.__ajAuto=null; const us=(self.__usar&&self.__usar.id===o.id)?self.__usar:null; self.__usar=null;   /* OS.dc.html#OS-0430:ajustar (Mapa) ou :usar= (AG-07) */
    if(us&&!carOpDef(a.op)) setTimeout(()=>self.setState({g2toast:o.id+' é '+o.tipo+' ('+(a.op||'operação sem defensivo')+'): produto da Consulta Agrofit só entra em ordem de pulverização ou de tratamento de sementes. Nada foi incluído.'}),0);   /* CTL-5, S3-1 */
    else if(v.pan_hasAj&&!pa) setTimeout(()=>ajAbrir(us),0);
    else if(us) setTimeout(()=>self.setState({g2toast:o.etapa!=='A liberar'?(o.id+' está em '+o.etapa+': '+us.p+' não foi incluído. Só ordem A liberar recebe produto novo.')
      :('Incluir '+us.p+' na '+o.id+' é decisão de '+OS_AGRO()+'. Nada foi incluído.')}),0); }
  const ajE=(pa&&pa.errs)||{}; const ajA=(pa&&pa.fn==='ajustar')?g2num(pa.area):NaN;
  const ajSt=(e)=>'font-family:inherit;font-size:14px;padding:7px 9px;border-radius:8px;width:110px;box-sizing:border-box;text-align:right;background:#FFFFFF;color:#15201A;border:1px solid '+(e?'#B42318':'#E4E9E5')+';';
  v.pan_ajt='Tire, inclua ou mude a dose dos produtos e a área da '+vcur+'. '+(ajAp?'Salvar e aprovar grava a '+vnx+' e a aprova (CMD-42); '+g2alcQuem('AL-01')+' libera depois.':(ajLib?'Salvar e liberar grava a '+vnx+' e libera para execução, reservando no Estoque o total ajustado.':'Salvar ajuste grava a '+vnx+'; a liberação continua impedida: '+String(b.t).replace(/^Liberar bloqueado: /,'')+'.'));
  const ajRem=(pa&&pa.rem)||{}; const ajAdd=(pa&&pa.add)||[];
  const ajPa=(p)=>Object.assign({},self.state.pa,{qerr:'',confVazio:false},p,{err:''});
  const prodN=(x)=>String(x||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
  const cenC=cenGet(); const lote=(p)=>cenLote(cenC,p); const disp=(p)=>{ const l=lote(p); return l?cenDisp(l):0; };   // o mesmo lote que a liberação reserva
  const naOrdem=(p)=>(o.ins||[]).some(x=>x.p===p&&!ajRem[p])||ajAdd.some(a=>a.p===p);
  // Consulta Agrofit (AG-07): classe e grupo de ação no "Incluir produto" e atalho "Agrofit ›" na linha do produto (nome exato da fazenda)
  const agf=(p)=>(OSD.agf||{})[p]; const agfT=(p)=>{ const a=agf(p); return a?(a.cl+(a.g?' · '+a.g:'')+' · '):''; }; const agfH=(p)=>{ const a=agf(p); return a?'AG-07.dc.html#'+a.id:''; };
  v.pan_ajopts=((OSD.nova&&OSD.nova.prods)||[]).filter(x=>!naOrdem(x.p)).map(x=>({p:x.p,d:disp(x.p),t:agfT(x.p)+(disp(x.p)>0?nd(disp(x.p))+' '+x.un+' disponíveis':'sem saldo no Estoque')}))
    .sort((a,b)=>((b.d>0)-(a.d>0))||a.p.localeCompare(b.p,'pt-BR'));
  v.pan_ajq=(pa&&pa.q)||''; v.pan_ajqerr=(pa&&pa.qerr)||''; v.pan_hasAjqerr=!!(pa&&pa.qerr);
  v.pan_setajq=(e)=>self.setState({pa:ajPa({q:e.target.value,qerr:''})});
  v.pan_ajinc=()=>{ const cur=self.state.pa; const q=prodN(cur.q); if(!q){ self.setState({pa:ajPa({qerr:'Digite o nome do produto e escolha na lista.'})}); return; }
    const L=(OSD.nova&&OSD.nova.prods)||[]; let x=L.find(y=>prodN(y.p)===q); let m=[]; if(!x){ m=L.filter(y=>prodN(y.p).indexOf(q)>=0); if(m.length===1) x=m[0]; }
    if(!x&&m.length>1){ self.setState({pa:ajPa({qerr:'Mais de um produto com "'+cur.q.trim()+'": '+m.slice(0,4).map(y=>y.p).join(', ')+(m.length>4?'…':'')+'. Escolha um na lista.'})}); return; }
    if(!x){ self.setState({pa:ajPa({qerr:'Produto não encontrado no cadastro: escolha um da lista.'})}); return; }
    if((cur.rem||{})[x.p]){ const r=Object.assign({},cur.rem); delete r[x.p]; self.setState({pa:ajPa({rem:r,q:'',qerr:''})}); return; }
    if((o.ins||[]).some(y=>y.p===x.p)||(cur.add||[]).some(a=>a.p===x.p)){ self.setState({pa:ajPa({qerr:x.p+' já está na ordem: mude a dose na linha dele.'})}); return; }
    const ni=(cur.add||[]).length; self.setState({pa:ajPa({add:(cur.add||[]).concat([{p:x.p,un:x.un,g:x.g,dose:''}]),q:'',qerr:''})});
    setTimeout(()=>{ const el=document.getElementById('aj_n'+ni); if(el) el.focus(); },60); };
  v.pan_ajqkey=(e)=>{ if(e&&e.key==='Enter'){ e.preventDefault(); v.pan_ajinc(); } };
  v.pan_ajadd=ajAdd.map((a,i)=>{ const d=g2num(a.dose); const e=ajE['+'+a.p]||'';
    return {p:a.p,cls:(self.state.ajFlash&&self.state.ajFlash===a.p)?'g2flash':'',agf:agfH(a.p),hasAgf:!!agf(a.p),fid:'aj_n'+i,lab:'Dose de '+a.p+' ('+a.un+'/ha)',un:a.un+'/ha',v:a.dose,st:ajSt(e),err:e,hasErr:!!e,
      hasAlvo:!!a.alvo,alvoT:a.alvo?('para '+a.alvo+(a.cul?' em '+String(a.cul).toLowerCase():'')+' · Consulta Agrofit'):'',tot:((d>0&&ajA>0&&isFinite(d)&&isFinite(ajA))?'na ordem '+nd(cenQtd(d,ajA))+' '+a.un+' · ':'')+(ajLib?'disponível '+nd(disp(a.p))+' '+a.un:''),
      set:(ev)=>{ const cur=self.state.pa; const er=Object.assign({},cur.errs); delete er['+'+a.p]; const ad=cur.add.map(y=>y.p===a.p?Object.assign({},y,{dose:ev.target.value}):y); self.setState({pa:ajPa({add:ad,errs:er})}); },
      rm:()=>{ const cur=self.state.pa; self.setState({pa:ajPa({add:cur.add.filter(y=>y.p!==a.p)})}); }}; });
  v.pan_hasAjadd=ajAdd.length>0;
  v.pan_ajarea=(pa&&pa.area)||''; v.pan_ajast=ajSt(ajE._area); v.pan_ajaerr=ajE._area||''; v.pan_hasAjaerr=!!ajE._area;
  v.pan_setajarea=(e)=>{ const cur=self.state.pa; const er=Object.assign({},cur.errs); delete er._area; self.setState({pa:Object.assign({},cur,{area:e.target.value,errs:er,err:''})}); };
  v.pan_ajins=(o.ins||[]).map((x,i)=>{ const s=(pa&&pa.doses&&pa.doses[x.p])||''; const d=g2num(s); const e=ajE[x.p]||''; const out=!!ajRem[x.p];
    const rz=(d>0&&x.dose>0)?d/x.dose:1; const warn=(!out&&!e&&(rz>1.5||rz<0.5))?('Dose '+nd(rz,1)+'× a da '+vcur+' ('+nd(x.dose)+' '+x.un+'/ha). Confira antes de salvar.'):'';
    return {p:x.p,agf:agfH(x.p),hasAgf:!!agf(x.p),fid:'aj_d'+i,lab:'Dose de '+x.p+' ('+x.un+'/ha)',un:x.un+'/ha',v:s,st:ajSt(e),err:e,hasErr:!!e&&!out,warn,hasWarn:!!warn,
      tot:(pmD(x.p)?'O.S. '+nd(x.dose,4)+' → plano '+(pmD(x.p).ac.dose==='-'?'retirar':nd(pmD(x.p).ac.dose,4))+' (análise · '+pmD(x.p).ac.laudo+') · ':'')+(out?'sai da ordem':(((d>0&&ajA>0&&isFinite(d)&&isFinite(ajA))?'na ordem '+nd(cenQtd(d,ajA))+' '+x.un+' · ':'')+(ajLib?'disponível '+nd(disp(x.p))+' '+x.un:''))),
      out,keep:!out,pst:out?'text-decoration:line-through;color:#6B7A71;':'',tirT:out?'Desfazer':'Tirar',tirTt:out?'Manter '+x.p+' na ordem':'Tirar '+x.p+' da ordem',
      tir:()=>{ const cur=self.state.pa; const r=Object.assign({},cur.rem); if(r[x.p]) delete r[x.p]; else r[x.p]=true; const er=Object.assign({},cur.errs); delete er[x.p]; self.setState({pa:ajPa({rem:r,errs:er})}); },
      set:(ev)=>{ const cur=self.state.pa; const er=Object.assign({},cur.errs); delete er[x.p]; const ds=Object.assign({},cur.doses); ds[x.p]=ev.target.value;
        self.setState({pa:Object.assign({},cur,{doses:ds,errs:er,err:''})}); }}; });
  v.pan_hasAjs2=ajLib&&!!o.planoMudou;   /* SOLO-01 (AC-SOLO-14): grava a versão com a dose do plano sem liberar (estoque ainda não cobre) */
  v.pan_ajsave2=()=>ajSalvar(false); v.pan_ajsave=()=>ajSalvar(ajLib);
  const ajSalvar=(LIB)=>{ const cur=self.state.pa; const errs={}; const ar=g2num(cur.area); const ds={};
    if(isNaN(ar)||ar<=0) errs._area='Informe a área maior que 0 ha.'; else if(ar>(o.area||0)+1e-9) errs._area='Máximo '+nf(o.area)+' ha: é a área da ordem. Informe até '+nf(o.area)+' ha.';
    const rem=Object.keys(cur.rem||{}).filter(p=>cur.rem[p]); const add=[];
    (o.ins||[]).forEach(x=>{ if(rem.indexOf(x.p)>=0) return; const d=g2num((cur.doses||{})[x.p]); if(!(d>0&&isFinite(d))) errs[x.p]='Informe a dose maior que 0 '+x.un+'/ha.'; else ds[x.p]=d; });
    (cur.add||[]).forEach(a=>{ const d=g2num(a.dose); if(!(d>0&&isFinite(d))) errs['+'+a.p]='Informe a dose maior que 0 '+a.un+'/ha.'; else add.push({p:a.p,dose:d,un:a.un,g:a.g,alvo:a.alvo||''}); });
    if(prodN(cur.q)){ self.setState({pa:Object.assign({},cur,{errs,err:'',qerr:'Clique em Incluir para adicionar "'+cur.q.trim()+'" ou apague o texto.'})}); return; }
    if(!isNaN(ar)&&ar>0){ const co=cenC.ordens[o.id]; const ck=(p,un,d,k,g,alvo)=>{ if(errs[k]) return; const m=(co?osUsoItem(cenC,co,{p,un,dose:d,g,alvo}):'')||(LIB?osc_ajFalta(cenC,p,un,d,ar):''); if(m) errs[k]=m; };   /* o mesmo do núcleo (PRE-REV Y6); regra legal com a ordem do cenário (Frente E) */
      (o.ins||[]).forEach(x=>{ if(ds[x.p]!==undefined) ck(x.p,x.un,ds[x.p],x.p,x.g,x.alvo); }); add.forEach(a=>ck(a.p,a.un,a.dose,'+'+a.p,a.g,a.alvo)); }
    if(Object.keys(errs).length){ self.setState({pa:Object.assign({},cur,{errs,err:''})}); return; }
    if((o.ins||[]).length&&rem.length===(o.ins||[]).length&&!add.length&&!cur.confVazio){
      self.setState({pa:Object.assign({},cur,{errs,confVazio:true,err:'A ordem fica sem nenhum produto. Clique em '+v.pan_ajsbtn+' de novo para confirmar, ou inclua um produto.'})}); return; }
    if(ajAp){ osRun(self,c=>{ const r1=osc_ajustar(c,o.id,ar,ds,o.janela,rem,add,false,g2perfil()); const r2=osc_aprovar(c,o.id,g2perfil());   /* mesmo cenMudar: os dois ou nada */
      return {msg:String(r1.msg).replace(' A liberação continua impedida.','')+' '+r2.msg}; },{pa:null}); return; }
    osRun(self,c=>osc_ajustar(c,o.id,ar,ds,o.janela,rem,add,LIB,g2perfil()),{pa:null}); };
  const insTxt=(o.ins||[]).map(x=>x.p+' '+nd(x.tot)+' '+x.un).join(', ');
  v.pan_ct={aprovar:'Aprovar '+o.id+' (versão '+osVn(o.versao)+'): ao confirmar, '+g2ator(PF,g2alc('AL-02').papeis)+' aprova '+osEsc(o)+' (CMD-42). A ordem fica em A liberar; '+g2alcQuem('AL-01')+' libera e reserva os insumos.'+osUsoAtencao(cenC,o.id),
    liberar:o.agua?('Liberar '+o.id+': janela, bomba e energia confirmadas; água sem requisição no Estoque.'):('Liberar '+o.id+' (versão '+osVn(o.versao)+'): ao confirmar, '+osLibTxt(PF,o)+'; '+(insTxt?'a requisição reserva no Estoque, por lote: '+insTxt+'.':'sem insumos a reservar, nenhuma requisição no Estoque.')+osUsoAtencao(cenC,o.id)),iniciar:'Iniciar '+o.id+' agora, na janela '+o.janela+(o.r&&(o.ins||[]).length?': insumos com '+o.resp+', confirmados no app.':'.'),
    conferencia:'Enviar '+o.id+' para conferência: execução física concluída ('+nf(o.realizado)+' ha).',encerrar:'Encerrar '+o.id+': apontamentos enviados, consumo baixado e nada em custódia.'}[pa?pa.fn:'']||'';
  v.pan_cbtn={aprovar:'Confirmar aprovação',liberar:'Confirmar liberação',iniciar:'Confirmar início',conferencia:'Confirmar envio',encerrar:'Confirmar encerramento'}[pa?pa.fn:'']||'';
  v.pan_back=()=>self.setState({pa:null});
  v.pan_yes=()=>{ const F={aprovar:c=>osc_aprovar(c,o.id,g2perfil()),liberar:c=>osc_liberar(c,o.id,o.agua,o.janela,g2perfil()),iniciar:c=>osc_iniciar(c,o.id),conferencia:c=>osc_conferencia(c,o.id,g2perfil()),encerrar:c=>osc_encerrar(c,o.id,g2perfil())}[pa.fn];
    if(F) osRun(self,F,{pa:null}); };
  v.pan_ad=pa&&pa.d||''; v.pan_aha=pa&&pa.ha||''; v.pan_aerr=pa&&pa.err||''; v.pan_hasAerr=!!(pa&&pa.err);
  v.pan_asub='Saldo da ordem: '+nf(o.saldo)+' ha'+(apP>0?' · '+nf(apP)+' ha no aparelho aguardando sinal':'');
  v.pan_setad=(e)=>self.setState({pa:Object.assign({},self.state.pa,{d:e.target.value,err:''})}); v.pan_setaha=(e)=>self.setState({pa:Object.assign({},self.state.pa,{ha:e.target.value,err:''})});
  // consumo real (AP-04): uma linha por insumo, a mesma regra do MB-03; o operador é herdado (quem está com os insumos) e aparece no formulário
  const apf=!!pa&&pa.fn==='apontar'; const apL=apf?osApIns(cenC,o,g2num(pa.ha),pa.ced):[];
  v.pan_acons=apL.map(x=>({lab:x.lab,v:x.v,hint:x.hint,warn:x.warn,hasWarn:x.hasWarn,fid:x.fid,set:(e)=>{ const cur=self.state.pa; if(!cur) return; self.setState({pa:Object.assign({},cur,{ced:Object.assign({},cur.ced,{[x.p]:e.target.value}),err:''})}); }}));
  v.pan_hasAcons=apL.length>0;
  { const rq=o.req&&cenC.reqs[o.req]; const qm=rq&&(rq.itens.find(i=>i.quem)||{}).quem; const com=!!rq&&rq.itens.some(i=>i.custodia>1e-6);   // o mesmo quem do cenApontar
    v.pan_aquem='Turno de '+(qm||o.resp||'—')+(com?' · quem está com os insumos':' · responsável da ordem'); }
  v.pan_adup=apf?osApDupAviso(cenC,o,cenDdMm(pa.d)):''; v.pan_hasAdup=!!v.pan_adup;   // aviso antes de salvar (não trava): o mesmo critério do servidor
  v.pan_asave=()=>{ const cur=self.state.pa; if(!cur) return; const n=g2num(cur.ha);
    if(!cur.d){ self.setState({pa:Object.assign({},cur,{err:'Informe a data do turno.'})}); return; }
    if(isNaN(n)||n<=0){ self.setState({pa:Object.assign({},cur,{err:'Informe a área feita (maior que 0 ha).'})}); return; }
    if(n>(o.saldo||0)+0.001){ self.setState({pa:Object.assign({},cur,{err:'Máximo '+nf(o.saldo)+' ha: é o saldo da ordem.'})}); return; }
    if(n>apMax+0.001){ self.setState({pa:Object.assign({},cur,{err:'Máximo '+nf(apMax)+' ha: '+nf(apP)+' ha do app aguardam sinal.'})}); return; }
    const col=osApColeta(osApIns(cenGet(),o,n,cur.ced)); if(col.erro){ self.setState({pa:Object.assign({},cur,{err:col.erro})}); return; }
    const d=cur.d.split('-'); osRun(self,c=>osc_apontar(c,o.id,d[2]+'/'+d[1],n,col.cons,col.est,cur.chave),{pa:null}); };   // chave do formulário aberto: duplo clique não soma (OSDIA-03)
  // ação secundária pelo realizado: sem realizado → cancelar sem execução; em execução → dispensar saldo (nunca cancela fato executado)
  const canCanc=!((o.realizado||0)>0)&&(o.etapa==='A liberar'||o.etapa==='Liberadas')&&!osCargasVivas(cenGet(),o.id).length;   // carga de colheita é execução (revisão A-04)
  const canDisp=o.etapa==='Em execução'&&!!o.area&&(o.saldo||0)>0.001;
  v.pan_hasCanc=canCanc&&gest; v.pan_hasDisp=canDisp&&agr;   /* sem o papel: a ação secundária vira o texto de quem decide (uma das duas, nunca juntas) */
  v.pan_dispQ=(canDisp&&!agr)?('Dispensar saldo: decisão de '+g2alcQuem('AL-05')+'.'):((canCanc&&!gest)?('Cancelar sem execução: decisão de '+g2alcQuem('AL-04')+'.'):''); v.pan_hasDispQ=!!v.pan_dispQ;
  v.pan_cango=()=>self.setState({pa:{id:o.id,fn:'cancelar',motivo:'',err:''}});
  v.pan_disgo=()=>self.setState({pa:{id:o.id,fn:'dispensar',ha:String(apMax).replace('.',','),motivo:'',err:'',chave:'W-DSP-'+o.id+'-'+Date.now().toString(36)+Math.random().toString(36).slice(2,6)}});   /* chave gerada ao abrir (ENG-021) */
  // (confirmação, aviso final, nova situação do insumo): a seção Insumos acompanha o que o aviso diz
  const cx=o.canc||((o.reservado&&insTxt)?['Libera a reserva no Estoque: '+insTxt+'.','Reserva liberada no Estoque: '+insTxt+'.','Reserva liberada no Estoque']:((o.ins||[]).length?['Nenhum insumo foi reservado.','Nenhum insumo estava reservado.','Nada reservado · ordem cancelada']:['','','']));
  const cxv=osc_cancTxt(cenGet(),o.id,cx);   /* com material entregue: a confirmação diz o que fica em custódia (revisão do 853a6a8, achado 7) */
  v.pan_cct='Cancelar '+o.id+' sem execução: a ordem sai do quadro e fica em Canceladas. '+cxv[0];
  v.pan_cansave=()=>{ const cur=self.state.pa; const mot=String(cur.motivo||'').trim();
    if(!mot){ self.setState({pa:Object.assign({},cur,{err:'Informe o motivo do cancelamento.'})}); return; }
    osRun(self,c=>osc_cancelar(c,o.id,mot,cx,g2perfil()),{pa:null}); };
  const lim=osLimDisp(o);   /* a mesma função do comando (AL-05 vigente, decimal) */
  v.pan_dsub='Até '+lim.pct+' % da área ('+nd(lim.ha,2)+' ha) sem alçada; acima disso, exige Direção. O realizado de '+nf(o.realizado)+' ha fica preservado.';
  v.pan_dval=agr?('Decisão gerencial e validação agronômica: '+g2ator(PF,DSP)+', registradas ao confirmar.'):'';
  v.pan_dissave=()=>{ const cur=self.state.pa; const n=g2num(cur.ha); const mot=String(cur.motivo||'').trim();
    const err=(m)=>self.setState({pa:Object.assign({},cur,{err:m})});
    if(isNaN(n)||n<=0) return err('Informe a área a dispensar (maior que 0 ha).');
    if(n>apMax+0.001) return err('Máximo '+nf(apMax)+' ha: é o saldo da ordem'+(apP>0?' descontando '+nf(apP)+' ha ainda no aparelho.':'.'));
    if(!mot) return err('Informe o motivo da dispensa.');
    osRun(self,c=>osc_dispensar(c,o.id,n,mot,g2perfil(),cur.chave),{pa:null}); };
}
function EXTRAVALS(self,v){
  self.g2perfilFecha={pa:null,dvr:null,cdAtivo:null};   /* trocar o perfil fecha a confirmação e os formulários de decisão (liberar, ajustar, dispensar, cancelar, revisão de dose) */
  const st=self.state, all=ords(self), os=vis(self);
  // OS.dc.html#OS-0420 (vindo do Mapa ou de outra tela): abre a ordem na tela de trabalho, uma vez
  // #OS-0430:ajustar (vindo do Mapa) abre o formulário de ajuste; ordem de outra fazenda troca o filtro Fazenda para a dela
  // #tal=Santa Rita|T1 (entrada pelo Mapa ou por outra tela): herda o talhão no filtro, com a fazenda dele à vista no filtro do topo
  const abrirHash=()=>{ let h=''; try{ h=decodeURIComponent(location.hash||''); }catch(e){ h=''; }
    const tm=/^#tal=([^|]+)\|(.+)$/.exec(h); if(tm){ const k=tm[1]+'|'+tm[2]; const ex=ords(self).some(o=>o.faz===tm[1]&&(o.talhoes||[]).some(t=>t.id===tm[2])); if(!ex) return;
      const f=Object.assign({},g2st(self,'g_os').f||{}); f.tal=[k]; const st={}; if(mfFaz(self)!=='Todas'&&mfFaz(self)!==tm[1]) st.mf_faz=tm[1];
      /* revisão VISOES-1, achado A1: a Safra guardada na sessão (g2keep) não esvazia a entrada pelo endereço; sem ordem do talhão nela, volta a Todas, com aviso */
      const sf=mfSaf(self); if(sf!=='Todas'&&!ords(self).some(o=>o.faz===tm[1]&&o.saf===sf&&(o.talhoes||[]).some(t=>t.id===tm[2]))){ st.mf_saf='Todas'; st.g2toast='Safra: Todas (o talhão '+tm[2]+' não tem ordem na '+sf+')'; }
      setTimeout(()=>{ g2set(self,'g_os',{f,fmc:null}); if(Object.keys(st).length) self.setState(st); },0); return; }
    const nm=/^#nova:([^:]+):([^:]+):(\d{4}-\d{2}-\d{2})$/.exec(h); if(nm){ const sf=OSD.nova.safs.find(x=>(OSD.nova.cult[x.id]||[]).some(k=>k.id===nm[1])); if(!sf) return;   /* Programar colheita (Produção › Previsão e colheita): só preenche; Ana confirma Emitir */
      const st={nv:{saf:sf.id,cult:nm[1],atv:nm[2],jan:nm[3],errs:{},warn:false,pre:true},pan:null}; if(mfFaz(self)!=='Todas'&&sf.faz&&sf.faz!==mfFaz(self)) st.mf_faz=sf.faz; setTimeout(()=>self.setState(st),0); return; }
    const m=/^#(O[SB]-\d+)(?::(ajustar|usar=(.*)))?$/.exec(h); if(!m) return;   /* :usar= vem do "Usar na O.S." do AG-07 (CTL-5) */
    const oh=ords(self).find(o=>o.id===m[1]); if(!oh) return; const f=mfFaz(self); const st={pan:oh.id,pa:null}; if(f!=='Todas'&&oh.faz&&oh.faz!==f) st.mf_faz=oh.faz;
    /* revisão VISOES-1, achado A1: a ordem pedida aparece na lista atrás do painel; a Safra guardada que a esconde passa à safra dela, com aviso */
    const sf=mfSaf(self); if(sf!=='Todas'&&oh.saf!==sf){ st.mf_saf=oh.saf||'Todas'; st.g2toast='Safra: '+st.mf_saf+(oh.saf?' (a da '+oh.id+')':''); }
    if(m[2]) self.__ajAuto=oh.id;
    if(m[3]!==undefined){ const u=m[3].split('|'); self.__usar={id:oh.id,p:u[0]||'',cul:u[1]||'',alvo:u[2]||''};   /* "Usar na O.S." do AG-07: produto, cultura e alvo */
      try{ history.replaceState(null,'','#'+oh.id); }catch(e){} }   /* o link é consumido: recarregar não inclui de novo */
    setTimeout(()=>self.setState(st),0); };
  if(!self.__hashIni){ self.__hashIni=1; abrirHash(); try{ window.addEventListener('hashchange',abrirHash); }catch(e){} }
  all.forEach(o=>{ v['op_'+o.id.replace('-','')]=()=>self.setState({pan:o.id,pa:null}); });
  self.g2pick=(gid,rid)=>{ if(gid==='g_os'&&String(rid).indexOf('grp@')!==0) self.setState({pan:String(rid).split('@')[0]}); };
  // agrupar por talhão: liga/desliga; grupos começam abertos; total geral de O.S. distintas (cada O.S. uma vez)
  const osVis=g2visao(self,'g_os'); v.os_agr=osVis==='agrupada';   /* VISOES-1: agrupar é a visão Tabela agrupada do seletor */
  { const spB=GR('g_os'), stB=g2st(self,'g_os'); const dist=(self.__osBase||[]).filter(r=>g2match(r,spB,stB)); const ar=dist.reduce((a,r)=>a+(Number(r.v.area)||0),0);
    self.__osDist=dist.length; if(v.os_agr){ v.g_os_count=dist.length; v.g_os_all=(self.__osBase||[]).length; }   // contador da grade = O.S. distintas, não grupos
    v.os_gtot='Total: '+dist.length+(dist.length===1?' O.S.':' O.S. distintas')+' · '+nf(ar)+' ha (cada O.S. contada uma vez; os grupos se sobrepõem quando a O.S. tem mais de um talhão)'; }
  const openPan=(id)=>self.setState({pan:id});
  // estado vazio do recorte: uma frase e uma ação que troca o filtro que zerou a tela
  const fz=mfFaz(self), sf=mfSaf(self), semFaz=!all.some(o=>fz==='Todas'||o.faz===fz);
  const cu=mfCult(self), soCult=cu!=='Todas'&&vis(self,true).length>0;   /* zerou só pela Cultura: a ação devolve todas as culturas */
  v.os_vazio=os.length===0; v.os_tem=!v.os_vazio;
  v.os_vt=soCult?('Nenhuma ordem de '+cu.toLowerCase()+' neste recorte'):(semFaz?('Nenhuma ordem na '+fz):('Nenhuma ordem na safra '+sf));
  v.os_va=soCult?'Ver todas as culturas':(semFaz?'Ver Santa Rita':'Ver todas as safras');
  v.os_vgo=()=>self.setState(soCult?{mf_cult:'Todas',g2toast:'Cultura: Todas'}:(semFaz?{mf_faz:'Santa Rita',g2toast:'Fazenda: Santa Rita'}:{mf_saf:'Todas',g2toast:'Safra: Todas'}));
  // selo do cabeçalho: recalculado do estado (cancelar, iniciar ou enviar para conferência muda as contagens)
  const nEx=os.filter(o=>o.etapa==='Em execução').length;
  const nIm=os.filter(o=>o.etapa!=='Canceladas'&&o.selos.some(s=>OS_IMP_RE.test(s.t))).length;
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
  // UX-ACAO-UNICA-20261003 (DS-33 §74.5.7.1, DS-40): Lista e Kanban são o mesmo trabalho e partilham os filtros (fase pelos chips,
  // colunas e busca da lista). Antes o Kanban ignorava o filtro (reproduzido: Liberadas → lista 2 ordens, Kanban 10). O filtro ativo
  // fica escrito no Kanban, com "Limpar filtros"; Recursos (recurso × dia) diz que o filtro não se aplica, sem descartá-lo em silêncio.
  const spO=GR('g_os'), stO=g2st(self,'g_os'); const filtrando=g2filtering(stO);
  const osRows=self.__osBase||spO.rows||[];   // linhas canônicas (no agrupado, spO.rows são os grupos)
  const okId=filtrando?new Set(osRows.filter(r=>g2match(r,spO,stO)).map(r=>r.id)):null; const osK=okId?os.filter(o=>okId.has(o.id)):os;
  const fDesc=[].concat(((stO.f||{}).fase||[]).length?['fase '+((stO.f||{}).fase||[]).join(', ')]:[])
    .concat(Object.keys(stO.f||{}).filter(k=>k!=='fase'&&((stO.f||{})[k]||[]).length).map(k=>{ const c=spO.cols.find(x=>x.k===k); const vs=(stO.f||{})[k]||[];
      return (c?c.l.toLowerCase():k)+(k==='tal'?' '+vs.map(x=>x==='(vazio)'?'sem talhão':x.split('|')[1]).join(', '):' ('+vs.length+')'); }))
    .concat((stO.q||'').trim()?['busca “'+(stO.q||'').trim()+'”']:[]).join(' · ');
  v.kb_filtro=filtrando&&(self.__osDist||0)>0; v.kb_nota='Filtro da lista aplicado: '+fDesc+' · '+osK.filter(o=>FASES.indexOf(o.etapa)>=0).length+' de '+os.filter(o=>FASES.indexOf(o.etapa)>=0).length+' ordens';
  v.os_limpar=()=>g2set(self,'g_os',{f:{},q:'',fmc:null});
  // Carga por recurso (TABELAS-FOCO; revisão VISOES-1, achados A5 e C3): os blocos, o estado e a faixa "Sem alocação" contam o MESMO recorte
  // da lista (Fazenda e Safra do topo + filtro da grade). Os blocos da irrigação só com água (do módulo Irrigação, fora da lista) seguem a
  // Fazenda e a Safra e somem com filtro da grade, como antes. Conflitos, manutenção e uso continuam da semana inteira.
  const recR=(self.__osBase||[]).filter(r=>g2match(r,spO,stO)), recIds=new Set(recR.map(r=>r.id));
  const escD=[mfFaz(self)==='Todas'?'todas as fazendas':mfFaz(self)].concat(mfSaf(self)==='Todas'?[]:['safra '+mfSaf(self)]).join(' · ');
  const rDesc=escD+(filtrando?' no filtro da lista ('+fDesc+')':'');
  const extOk=(id)=>{ const x=RC_EXT[id]; return !!x&&!filtrando&&(mfFaz(self)==='Todas'||mfFaz(self)===x[0])&&(mfSaf(self)==='Todas'||mfSaf(self)===x[1]); };
  v.rc_nota='A carga por recurso mostra a semana do PCP por recurso e dia: só os blocos das ordens de '+rDesc+'; conflitos, manutenção e uso continuam da semana inteira.';
  g2visaoTenta(self,'g_os','carga',()=>{ RC_OS.forEach(id=>{ v['rcv_'+id.replace('-','')]=recIds.has(id)||extOk(id); }); });   /* VISOES-1 §2.8: a falha desta visão não derruba a Lista */
  // §2.8 "Parcial": ordens do recorte que pedem recurso (a liberar, liberadas, em execução) e não têm bloco na semana; cada ID abre o mesmo painel
  const semAl=recR.filter(r=>RC_OS.indexOf(r.id)<0&&['A liberar','Liberadas','Em execução'].indexOf(r.v.fase)>=0).map(r=>r.id);
  const nAl=recR.filter(r=>RC_OS.indexOf(r.id)>=0).length;
  v.rc_semtem=nAl>0&&semAl.length>0; v.rc_semt='Sem alocação ('+semAl.length+')'; v.rc_sem=semAl.map(id=>({id,lab:'Abrir '+id+' (sem alocação na semana do PCP)',go:()=>openPan(id)}));
  /* VISOES-1 §2.8 · estado em toda visão (vazio de contexto continua sem seletor: os_vazio): cenário ilegível, vazio de filtro e vazio por regra */
  { const nDist=self.__osDist||0, nKb=osK.filter(o=>FASES.indexOf(o.etapa)>=0).length;
    const nCanc=vendoCanc(self)?0:os.filter(o=>o.etapa==='Canceladas').length;
    const ord=(n)=>n+(n===1?' ordem':' ordens'), lista=()=>g2visaoIr(self,'g_os','lista','fallback');
    self.g2visaoFoco=()=>self.state.pan||'';
    self.g2visaoEstado=(gid,k)=>{
      if(typeof cenIlegivel==='function'&&cenIlegivel()) return {tipo:'cenario',texto:'O cenário gravado neste navegador não pôde ser lido: a tela mostra a demonstração inicial. Nada foi apagado; o gravado fica guardado à parte ao recomeçar.',
        acao:'Recomeçar a demonstração',fn:()=>{ cenReset(); self.setState({cenrev:Date.now(),g2toast:'Demonstração recomeçada; o cenário ilegível ficou guardado à parte.'}); }};
      if(filtrando&&nDist===0) return {tipo:'vazio',texto:'Nenhuma ordem no filtro: '+fDesc+'.',acao:'Limpar filtros',fn:v.os_limpar};
      /* revisão VISOES-1, achado A2: recorte só com canceladas (fora da lista e do quadro por regra) diz o motivo em toda visão */
      if(!filtrando&&nDist===0&&nCanc>0) return {tipo:'regra',texto:'Só há ordens canceladas neste recorte ('+escD+'): '+ord(nCanc)+'.',acao:'Ver canceladas',fn:setF('Canceladas')};
      if(k==='kanban'&&nDist>0&&nKb===0) return {tipo:'regra',texto:'Canceladas ficam fora do quadro: '+ord(nDist)+' no filtro.',acao:'Ver em lista',fn:lista};
      if(k==='calendario'&&nDist>0&&nKb===0) return {tipo:'regra',texto:'Canceladas ficam fora do calendário: '+ord(nDist)+' no filtro.',acao:'Ver em lista',fn:lista};
      /* VISOES-2: semana sem ordem do recorte (há ordem em outra semana): diz e leva à próxima (ou à anterior) */
      if(k==='calendario'&&self.__cal&&nKb>0&&self.__cal.n===0&&self.__cal.sem===0){ const C=self.__cal, d=C.prox||C.ant;
        return {tipo:'regra',texto:'Nenhuma ordem do recorte nesta semana.',acao:d?(C.prox?'Ir para a semana de ':'Voltar para a semana de ')+brd(d).slice(0,5):'Ver em lista',fn:d?()=>C.ir(d):lista}; }
      if(k==='carga'&&nDist>0&&nAl===0) return {tipo:'regra',texto:'Nenhuma ordem de '+rDesc+' tem alocação na semana do PCP: '+ord(nDist)+'.',acao:'Ver em lista',fn:lista};
      return null; }; }
  // ---- Talhão (TABELAS-FOCO): seletor na barra da coleção, fora das abas; o mesmo estado do filtro da coluna Talhão (f.tal) ----
  { const spc=spO.cols.find(c=>c.k==='tal'); const tcnt={}, tlab={};
    osRows.forEach(r=>g2fkeys(r,spc).forEach(k=>{ tcnt[k]=(tcnt[k]||0)+1; if(!tlab[k]){ const x=(g2mem(r,spc)||[]).find(y=>y.id===k); tlab[k]=x?x.l:'Sem talhão'; } }));
    const tsel=((stO.f||{}).tal)||[]; const tq=self.state.ost_q||''; const tqn=g2norm(tq);
    const tks=Object.keys(tcnt).sort((a,b)=>tlab[a].localeCompare(tlab[b],'pt-BR',{numeric:true}));
    const setT=(arr)=>{ const f=Object.assign({},g2st(self,'g_os').f||{}); if(arr.length) f.tal=arr; else delete f.tal; self.__osMsg=''; g2set(self,'g_os',{f,fmc:null}); };
    const nome=(k)=>tlab[k]||(k==='(vazio)'?'Sem talhão':k.split('|')[1]);
    v.ost_open=!!self.state.ost_open; v.ost_q=tq; v.ost_on=tsel.length?'true':'false';
    /* faixa "Filtros desta tela" (13/10): Talhão é este mesmo filtro (f.tal), escolhido numa lista; Cultura, os cultivos do recorte de Fazenda e Safra */
    v.mf_tal=tsel.length===1?tsel[0]:(tsel.length?'__v':''); v.mf_tal_opts=[{v:'',t:'Todos'}].concat(tsel.length>1?[{v:'__v',t:tsel.length+' talhões'}]:[]).concat(tks.map(k=>({v:k,t:nome(k)})));
    v.mf_settal=(e)=>{ const x=e.target.value; if(x==='__v') return; setT(x?[x]:[]); self.setState({g2toast:'Talhão: '+(x?nome(x):'Todos')}); };
    { const cs=[]; vis(self,true).forEach(o=>osCults(o).forEach(c=>{ if(cs.indexOf(c)<0) cs.push(c); })); cs.sort((a,b)=>a.localeCompare(b,'pt-BR')); const cu=mfCult(self); if(cu!=='Todas'&&cs.indexOf(cu)<0) cs.push(cu);
      v.mf_cult=cu; v.mf_cult_opts=[{v:'Todas',t:'Todas'}].concat(cs.map(c=>({v:c,t:c}))); v.mf_setcult=(e)=>self.setState({mf_cult:e.target.value,g2toast:'Cultura: '+e.target.value}); }
    v.ost_btn='Talhão: '+(tsel.length?tsel.map(nome).join(', '):'Todos');
    v.ost_btnst='display:inline-flex;align-items:center;gap:6px;font-family:inherit;font-size:12.5px;font-weight:700;padding:6px 12px;border-radius:999px;cursor:pointer;white-space:nowrap;max-width:100%;overflow:hidden;text-overflow:ellipsis;'
      +(tsel.length?'border:1px solid #1E7A4C;background:#E4F3E9;color:#14532D;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;');
    { const ps=self.state.ost_pos; v.ost_popst=ps?('left:'+ps.l+'px;width:'+ps.w+'px;'):'left:0;width:min(320px, calc(100vw - 32px));'; }
    v.ost_toggle=()=>{ const ab=!self.state.ost_open; self.setState({ost_open:ab,ost_q:'',ost_pos:null}); if(ab) setTimeout(()=>{ const q=document.getElementById('ost_q'); const d=q&&q.closest('[role=dialog]'); if(d){ const m=document.querySelector('main'), lo=(m?m.getBoundingClientRect().left:0)+8, hi=innerWidth-8; const r=d.getBoundingClientRect();   // celular: cabe entre o menu e a borda
      if(r.right>hi){ const dx=Math.max(0,Math.min(r.right-hi, r.left-lo)); self.setState({ost_pos:{l:-Math.round(dx),w:Math.round(Math.min(r.width,hi-lo))}}); } } if(q) q.focus({preventScroll:true}); },0); };   // abre com o foco na pesquisa
    v.ost_fecha=()=>{ self.setState({ost_open:false}); setTimeout(()=>{ const b=document.getElementById('ost_btn'); if(b) b.focus(); },0); };
    v.ost_setq=(e)=>self.setState({ost_q:e.target.value});
    v.ost_key=(e)=>{ if(e.key==='Escape'){ e.preventDefault(); e.stopPropagation(); v.ost_fecha(); } };
    v.ost_vals=tks.filter(k=>!tqn||g2norm(nome(k)).indexOf(tqn)>=0).map(k=>({t:nome(k),n:String(tcnt[k]),on:tsel.indexOf(k)>=0,
      tog:()=>{ const a=tsel.slice(); const i=a.indexOf(k); if(i>=0) a.splice(i,1); else a.push(k); setT(a); }}));
    v.ost_semres=!v.ost_vals.length; v.ost_todos=()=>setT([]); v.ost_limpa=tsel.length>0;
    v.ost_conta=tsel.length?(osK.length+(osK.length===1?' ordem':' ordens')+' no filtro'):'';
    v.os_tmsg=self.__osMsg||''; v.os_temmsg=!!self.__osMsg; }
  v.kb=[]; g2visaoTenta(self,'g_os','kanban',()=>{ v.kb=FASES.map(f=>{ const cs=osK.filter(o=>o.etapa===f); const sal=cs.filter(o=>o.area).reduce((s,o)=>s+(o.saldo||0),0);
    return {t:f,n:String(cs.length),nst:chipSt(FCOR[f]),carga:(f==='Encerradas'?osPeriodo(cs):(sal?'saldo '+nf(sal)+' ha':'')),vazio:cs.length===0,
      cards:cs.map(o=>{ const pct=o.area?Math.round(100*(o.realizado||0)/o.area):0;
        const ini=!!o.area&&(o.realizado||0)>0;
        return {id:o.id,tipo:o.tipo,local:localTxt(o),obs:o.obs||'',hasObs:!!o.obs,real:(ini?nf(o.realizado)+'/'+nf(o.area)+' ha · '+pct+' % · '+salTxt(o):(o.area?'':'sem área · ordem de processo')),
          hasReal:!(o.area&&!ini),hasBar:ini,bar:'display:block;height:100%;border-radius:999px;background:'+(o.selos.some(s=>s.c==='red')?'#B42318':'#1E7A4C')+';width:'+pct+'%;',
          selos:o.selos.map(s=>({t:s.t,dica:osSeloDica(o,s.t)||g2dicaDe(s.t),st:chipSt(s.c).replace('white-space:nowrap;','white-space:normal;line-height:1.3;align-items:baseline;').replace('border-radius:999px;','border-radius:8px;'),dot:dotSt(s.c)+'transform:translateY(-1px);'})),meta:o.resp+' · '+o.janela,dp:(o.dono?o.dono+' · '+o.prazo:''),hasDp:!!o.dono,lab:'Abrir '+o.id+' · '+o.tipo,
          st:'display:flex;flex-direction:column;gap:6px;text-align:left;width:100%;box-sizing:border-box;background:#FFFFFF;border-radius:10px;padding:9px 10px;cursor:pointer;font-family:inherit;color:#15201A;'+(st.pan===o.id?'border:2px solid #1E7A4C;':'border:1px solid #E4E9E5;box-shadow:0 1px 2px rgba(21,32,26,.05);'),
          open:()=>openPan(o.id), key:(e)=>{ if(e&&(e.key==='Enter'||e.key===' ')){ e.preventDefault(); openPan(o.id); } }}; })}; }); });
  /* VISOES-2 (F2a) · Calendário, só leitura: a semana de segunda a domingo com o mesmo recorte do Kanban (filtros, busca, Talhão; Canceladas
     fora); a ordem aparece em cada dia da sua janela; sem início, na faixa "Sem data"; o clique abre o mesmo painel. Programar fica no detalhe. */
  v.cal=[]; v.cal_sem=[]; self.__cal=null; g2visaoTenta(self,'g_os','calendario',()=>{ const hoje=(typeof CEN_DIA_OP!=='undefined'?CEN_DIA_OP:'2026-09-26'); const seg0=g2segunda(hoje);
    const seg=self.state.cal_seg||seg0; const dias=g2semana(seg); const cs=osK.filter(o=>FASES.indexOf(o.etapa)>=0); const DS=['seg','ter','qua','qui','sex','sáb','dom'];
    const card=o=>({id:o.id,tipo:o.tipo,local:localTxt(o),fase:o.etapa,fst:chipSt(FCOR[o.etapa]),fdot:dotSt(FCOR[o.etapa]),open:()=>openPan(o.id),
      lab:'Abrir '+o.id+' · '+o.tipo+' · '+o.etapa+(o.ini?' · janela '+brd(o.ini)+(o.fim&&o.fim!==o.ini?' a '+brd(o.fim):''):' · sem data')});
    const naSem=new Set();
    v.cal=dias.map((d,i)=>{ const ds=cs.filter(o=>g2noDia(o.ini,o.fim,d)); ds.forEach(o=>naSem.add(o.id)); const ehHoje=d===hoje;
      return {d,t:DS[i]+' '+d.slice(8,10)+'/'+d.slice(5,7)+(ehHoje?' · hoje':''),hoje:ehHoje?'true':'false',vazio:ds.length===0,vz:ds.length===0?'true':'false',nt:ds.length?String(ds.length):'',ords:ds.map(card)}; });
    v.cal_sem=cs.filter(o=>!o.ini).map(card); v.cal_temsem=v.cal_sem.length>0;
    v.cal_tit=brd(dias[0]).slice(0,5)+' a '+brd(dias[6]); v.cal_n=naSem.size+(naSem.size===1?' ordem':' ordens')+' nesta semana'+(v.cal_sem.length?' · '+v.cal_sem.length+' sem data':'');
    v.cal_naoHoje=seg!==seg0;
    v.cal_prev=()=>self.setState({cal_seg:g2somaDias(seg,-7)}); v.cal_next=()=>self.setState({cal_seg:g2somaDias(seg,7)}); v.cal_hoje=()=>self.setState({cal_seg:null});
    /* semana vazia: a próxima com ordem do recorte (a janela que começa ou ainda corre depois do domingo) */
    const prox=cs.filter(o=>o.ini&&((o.fim&&o.fim>=o.ini?o.fim:o.ini)>dias[6])).map(o=>o.ini>dias[6]?o.ini:g2somaDias(dias[6],1)).sort()[0]||'';
    const ant=cs.filter(o=>o.ini&&o.ini<dias[0]).map(o=>o.ini).sort().reverse()[0]||'';
    self.__cal={n:naSem.size,sem:v.cal_sem.length,prox,ant,ir:(d)=>self.setState({cal_seg:g2segunda(d)})}; });
  // ---- painel lateral de consulta ----
  const o=st.pan?all.find(x=>x.id===st.pan):null; v.pan_open=!!o;
  const close=()=>self.setState({pan:null});
  v.pan_close=close; v.pan_key=(e)=>{ if(e&&e.key==='Escape'){ e.preventDefault(); close(); } };
  if(o){ const a=acum(o);
    v.pan_t=o.id+' · '+o.tipo; v.pan_fase=o.etapa; v.pan_fst=chipSt(FCOR[o.etapa]); v.pan_fdot=dotSt(FCOR[o.etapa]);
    v.pan_selos=o.selos.map(s=>({t:s.t,dica:osSeloDica(o,s.t)||g2dicaDe(s.t),st:chipSt(s.c),dot:dotSt(s.c)}));
    const cur=FASES.indexOf(o.etapa);
    v.pan_steps=FASES.map((f,i)=>({t:f,cur:i===cur?'step':'false',st:'display:flex;flex-direction:column;gap:5px;font-size:11.5px;font-weight:'+(i===cur?'800':'600')+';color:'+(i<=cur?'#15201A':'#8A968E')+';',
      bst:'height:5px;border-radius:999px;background:'+(i<cur?'#9CCBB0':(i===cur?'#1E7A4C':'#E4E9E5'))+';'}));
    const kv=[['Local',o.talhao],['Janela',o.janela],['Responsável',o.resp],['Versão',o.versao]];
    if(o.area){ kv.splice(1,0,['Área autorizada',nf(o.area)+' ha'],['Realizado',nf(o.realizado)+' ha'+((a.conf||a.prov)?' ('+nf(a.conf)+' conf. + '+nf(a.prov)+' prov.)':'')+(a.sem?' · '+nf(a.sem)+' ha aguardando sinal':'')],['Saldo',nf(o.saldo)+' ha']); }    v.pan_kv=kv.map(x=>({l:x[0],v:x[1]}));
    // apontamentos: os do app mostram a origem; sem sinal ficam "Aguardando sinal" e não entram no acumulado
    // duplicidade (AP-06/07): o retido não soma e mostra as três saídas de Paula (CMD-09); "vale este" só contra um relato já somado
    const cg=cenGet(), cgo=cg.ordens[o.id]; const apus=st.apus&&st.apus.id===o.id?st.apus:{id:o.id};
    const usOf=(dia)=>{ const u=apus[dia]||{}; const r={}; Object.keys(u).forEach(p=>{ const n=g2num(u[p]); if(String(u[p]).trim()!==''&&!isNaN(n)) r[p]=n; }); return r; };
    const apDec=(dia,modo)=>osRun(self,c=>osc_apDecidir(c,o.id,dia,modo,usOf(dia),g2perfil()),{apus:null},(e)=>self.setState({g2toast:e}));
    const CONF=g2papel(g2perfil(),g2alc('AL-12').papeis);   /* CMD-09: as três saídas só para quem confere (AL-12; CTL-3 · ATOR) */
    /* B-R8: divergência de consumo/dose na linha do apontamento; a revisão técnica (aceitar com motivo ou registrar a correção) só com o papel agronomo */
    const AGRd=g2papel(g2perfil(),g2alc('AL-02').papeis); const dvr=(st.dvr&&st.dvr.id===o.id)?st.dvr:{id:o.id};
    const dvSet=(dia,patch)=>{ const cur=(self.state.dvr&&self.state.dvr.id===o.id)?self.state.dvr:{id:o.id}; self.setState({dvr:Object.assign({},cur,{[dia]:Object.assign({},cur[dia]||{},patch)})}); };
    /* DOM-REV-20261009-01 (S3): gravar a revisão de um dia limpa só o rascunho desse dia; o dos outros dias da mesma ordem fica,
       e o foco vai para o próximo dia ainda em revisão (quem usa o teclado continua de onde estava) */
    const dvGo=(dia,dec)=>{ const cur=(self.state.dvr&&self.state.dvr.id===o.id)?self.state.dvr:{id:o.id}; const t=(cur[dia]||{}).t||'';
      const resto=Object.assign({},cur); delete resto[dia];
      const r=osRun(self,c=>cenDivRever(c,o.id,dia,dec,t,g2perfil()),{dvr:resto},(e)=>dvSet(dia,{err:e}));
      if(!r.erro) setTimeout(()=>{ const el=document.querySelector('aside[role=dialog] textarea[id^="dv_"]'); if(el) el.focus(); },60); };
    let ac=0; v.pan_ap=(o.ap||[]).map(x=>{ const prev=x.st==='Previsto'; const sem=x.sinc===false; const som=!prev&&cenApSomado(x); if(som) ac+=x.ha; const s=sem?'Aguardando sinal':x.st;
      const dup=x.st===CEN_AP_DUP&&!!cgo; const viv=dup?cenApDupVivos(cgo,x):[]; const de=viv.map(a=>a.dia).join(', ');
      const K=viv.length===1&&cenApSomado(viv[0])?viv[0]:null; const uso=K?cenApUsoK(cg,cgo,K):'';
      const fal=dup?cenApDecCons(cgo,x,cenApDecBase(cg,cgo,null),null).falta:[];
      const usx=fal.map(f=>({lab:'Usado de '+f.p+' ('+f.un+')',v:(apus[x.dia]||{})[f.p]||'',hint:'Estimativa '+nd(f.q)+' '+f.un+' passa da custódia ('+nd(f.cust)+' '+f.un+'): informe o usado'+(x.quem?' com '+x.quem:''),
        set:(e)=>{ const cur=self.state.apus&&self.state.apus.id===o.id?self.state.apus:{id:o.id}; self.setState({apus:Object.assign({},cur,{[x.dia]:Object.assign({},cur[x.dia]||{},{[f.p]:e.target.value})})}); }}));
      const dv=!prev&&x.st!==CEN_AP_DESC&&(x.div||[]).length>0, dvAb=dv&&som&&!x.rev, dvS=dvr[x.dia]||{};   /* guardado como duplicidade nunca soma: sem divergência (revisão DOM achado 6) */
      const dvQ=(dvAb&&!AGRd)?'Revisão técnica pendente: decisão de '+g2alcQuem('AL-02')+' (aceitar com motivo ou registrar a correção).':((dv&&!som&&!x.rev)?'A revisão técnica abre quando o apontamento somar.':'');
      return {div:dv,divT:dv?CEN_DIV+' · '+x.div.map(cenDivTxt).join('; '):'',hasRev:dv&&!!x.rev,revT:x.rev?'Revisão técnica: '+x.rev.dec.toLowerCase()+' por '+x.rev.quem+' às '+x.rev.at+' · '+x.rev.txt+(x.rev.rp?' · '+x.rev.rp:''):'',
        divQ:dvQ,hasDivQ:!!dvQ,dvPode:dvAb&&AGRd,dvfid:'dv_'+x.dia,dvlab:'Motivo ou correção decidida · dia '+x.dia,dvv:dvS.t||'',dverr:dvS.err||'',hasDverr:!!dvS.err,
        dvset:(e)=>dvSet(x.dia,{t:e.target.value,err:''}),dvAc:()=>dvGo(x.dia,'aceitar'),dvCo:()=>dvGo(x.dia,'corrigir'),
        d:x.d,dia:'Dia '+x.dia+(x.origem==='app'?' · app':''),ha:(prev?'prev. ':'')+nf(x.ha)+' ha'+(x.h?' · '+nd(x.h,1)+' h':''),ac:(prev?'—':(!som?'não somado':nf(ac)+' / '+nf(o.area)+' ha')),t:s,st:chipSt(STCOR[s]),dot:dotSt(STCOR[s]),rst:prev?'color:#8A968E;':'',
        dup,dupT:!dup?'':(viv.length?'Mesma data e talhão do dia '+de+'. É outro turno? Quem decide: '+CEN_CONF_AP()+'.':'O dia '+(x.dupDe||[]).join(', ')+' já não vale: este só pode ser somado como outro turno. Quem decide: '+CEN_CONF_AP()+'.')
          +(uso?' "Vale este" indisponível: '+uso+'.':''),
        vant:'Mesmo turno: vale o dia '+de,hasAnt:viv.length>0,hasEste:!!K&&!uso,usx,hasUs:CONF&&usx.length>0,pode:CONF,
        ant:()=>apDec(x.dia,'anterior'),este:()=>apDec(x.dia,'este'),somar:()=>apDec(x.dia,'somar')}; });
    v.pan_ap.forEach((linha,i)=>Object.assign(linha,cdLinha(self,o,(o.ap||[])[i])));
    v.pan_hasAp=v.pan_ap.length>0; v.pan_noAp=!v.pan_hasAp;
    v.pan_noApT=o.area?(o.etapa==='A liberar'||o.etapa==='Liberadas'?'Sem apontamentos: a ordem ainda não foi iniciada.':'Sem apontamentos registrados.'):'Ordem de processo: entradas e saídas são registradas por etapa do beneficiamento, não por área.';
    v.pan_acum=!o.area?'':(o.disp?('Realizado '+nf(o.realizado)+' ha · Dispensado '+nf(o.disp)+' ha · Saldo '+nf(o.saldo)+' ha (de '+nf(o.area)+' ha)')
      :('Acumulado '+nf(o.realizado)+' / '+nf(o.area)+' ha · saldo '+nf(o.saldo)+' ha'))+(a.sem?' · '+nf(a.sem)+' ha no aparelho aguardando sinal':''); v.pan_hasAcum=!!o.area&&v.pan_hasAp;
    v.pan_nota=o.nota||''; v.pan_hasNota=!!o.nota;
    v.pan_cond=o.cond; v.pan_orig=o.orig.map(t=>({t}));
    v.pan_link=o.link||'#'; v.pan_hasLink=!!o.link;
    osWork(self,v,o); panSecs(self,v,o);
    if(v.pan_ap.some(a=>a.cdAberto)){v.pan_hasBtn=false;v.pan_hasAj=false;v.pan_hasAjc=false;}
  }
  // ---- nova ordem (nasce A liberar; nunca liberada automaticamente) ----
  const nv=st.nv; v.nv_show=!!nv;
  v.nv_open=()=>self.setState({nv:{saf:'',cult:'',atv:'',jan:'',errs:{},warn:false},pan:null});
  if(nv){
    const upd=(patch)=>{ const cur=self.state.nv; const errs=Object.assign({},cur.errs||{}); Object.keys(patch).forEach(k=>delete errs[k]); self.setState({nv:Object.assign({},cur,patch,{errs,warn:false,dup:''})}); };
    // atividade que já tem ordem: o erro fica no campo e o botão abre a ordem existente (nada é emitido)
    v.nv_hasDup=!!nv.dup; v.nv_dupt='Abrir '+(nv.dup||''); v.nv_opendup=()=>self.setState({nv:null,pan:self.state.nv.dup});
    const cults=nv.saf?(OSD.nova.cult[nv.saf]||[]):[]; const c=cults.find(x=>x.id===nv.cult); const pl=c&&c.plano?OSD.nova.planos[c.plano]:null;
    /* SOLO-01: as atividades do cultivo com a dose efetiva (uso da análise gravado no cenário) e as incluídas pela análise (calagem, gessagem);
       a retirada pela análise do único insumo tira a atividade (solo.js soloAtividades, a mesma regra do Planejar safra) */
    const atvs=(c&&pl)?nvAtvs(c,pl):[];
    v.nv_safs=[{v:'',t:'Selecione a safra'}].concat(OSD.nova.safs.map(s=>({v:s.id,t:s.t}))); v.nv_saf=nv.saf;
    v.nv_cults=[{v:'',t:nv.saf?'Selecione o cultivo':'Escolha a safra primeiro'}].concat(cults.map(x=>({v:x.id,t:x.t}))); v.nv_cult=nv.cult; v.nv_cultdis=!nv.saf;
    v.nv_atvs=[{v:'',t:(!c?'Escolha o cultivo primeiro':(pl?'Selecione a atividade':'Cultivo sem plano aplicado'))}].concat(atvs.map(a=>({v:a.id,t:a.nome+' · '+a.op+(a.incl?' (incluída pela análise · '+a.laudo+')':'')}))); v.nv_atv=nv.atv; v.nv_atvdis=!pl;
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
      const a0=pl&&atvs.find(x=>x.id===cur.atv); const kc=(typeof PRDC!=='undefined'&&PRDC.cult[cur.cult])||null; const semana=!!(kc&&kc.semanal&&a0&&/^Colheita/.test(a0.op)&&cur.jan);
      const sw=semana?prSem(cur.jan):''; const sn=semana?prSemN(sw):0;   /* R-18: perene de fruta, uma O.S. de colheita por cultivo e semana (com o ano: a safra cruza o ano, revisão A-19) */
      const semDe=(x)=>{ const co=cenGet().ordens[x.id]; return co?prSemDaOS(co):(new RegExp('semana '+sn+'\\b').test(String(x.tipo||''))?sw:''); };
      if(!Object.keys(errs).length){ const k=semana?cur.cult+'|'+sw:cur.cult+'|'+cur.atv;
        /* SOLO-01 · revisão A1: calagem ou gessagem incluída pela análise tem uma O.S. por cultivo, de qualquer laudo (cultivo|solo:<laudo>:cal);
           a do laudo novo não emite outra: ajusta-se a dose na que existe. Dano evitado: corrigir o talhão duas vezes */
        const tc=(/^solo:[^:]+:(cal|ges)$/.exec(cur.atv)||[])[1]||'';
        const dup=all.find(x=>x.etapa!=='Canceladas'&&((x.keys||[]).indexOf(k)>=0||(tc&&(x.keys||[]).some(q=>soloKCorr(q,cur.cult,tc)))||(semana&&x.talhao===c.local&&/^Colheita/.test(String(x.tipo||''))&&semDe(x)===sw)));
        if(dup){ const dk=tc&&(dup.keys||[]).indexOf(k)<0; errs.atv='Já existe '+dup.id+(semana?' para a colheita da semana '+sn+' neste talhão.':(dk?' para a '+(tc==='ges'?'gessagem':'calagem')+' deste cultivo (incluída pelo '+String((dup.keys||[]).find(q=>soloKCorr(q,cur.cult,tc))).split(':')[1]+'): ajuste a dose nela.':' para esta atividade neste cultivo.')); dupId=dup.id; } }
      if(Object.keys(errs).length){ self.setState({nv:Object.assign({},cur,{errs,warn:false,dup:dupId})}); return; }
      const a=atvs.find(x=>x.id===cur.atv); const s=OSD.nova.safs.find(x=>x.id===cur.saf);
      const num=440+all.filter(x=>x.novo).length; const id='OS-0'+num;
      // insumos da atividade do plano: dose × área do cultivo (a semente leva a variedade do cultivo); nada é reservado antes de liberar
      const ins=(a.ins||[]).map(x=>({g:x.g,p:x.p.replace(/ · (variedade|híbrido) do cultivo$/,' '+c.var),dose:x.dose,un:x.un,tot:cenQtd(x.dose,c.area),sit:'Reserva ao liberar',orig:x.orig}));
      const cj=(OSD.nova.conj||{})[a.op]||null;
      const no={id,novo:true,jan:cur.jan,keys:[semana?cur.cult+'|'+sw:cur.cult+'|'+cur.atv],tipo:semana?'Colheita · semana '+sn:(a.op===a.nome?a.nome:a.op+' · '+a.nome),talhao:c.local,area:c.area,etapa:'A liberar',selos:[],
        faz:s.faz||'Santa Rita',saf:s.mf,cult:c.id,cultura:c.cultura||'',obs:'',agua:false,ins,semins:'',bloq:null,aviso:'',dono:OS_AGRO(),prazo:'liberar',
        atv:{op:a.op,nome:a.nome,gat:a.gat||'',orig:a.incl?('Análise de solo · '+a.laudo):(pl.nome+' v'+pl.versao),conj:cj?cj.conj:'',rend:cj?cj.rend:0},
        realizado:0,saldo:c.area,resp:'—',versao:'v1',janela:'a partir de '+brd(cur.jan),ap:[],nota:'',
        cond:'Ana (agrônoma) confere, ajusta se precisar e libera; liberar exige a prontidão de máquina, equipe e insumos. Próximo passo: liberar para execução.',
        orig:[s.t+' · cultivo '+c.local+' ('+nf(c.area)+' ha)',a.incl?(a.nome+' incluída pela análise · '+a.laudo+' (Planejar safra) · plano '+pl.nome+' v'+pl.versao):('Plano '+pl.nome+' v'+pl.versao+' · atividade '+a.nome)],link:''};
      osRun(self,c0=>osc_nova(c0,no),{nv:null,pan:id},(e)=>self.setState({g2toast:e})); };
  }
  // ---- restaurar a demonstração (cenário compartilhado com Estoque e App volta ao início) ----
  v.os_rst_no=!st.os_rst; v.os_rst_ask=!!st.os_rst;
  v.os_rst=()=>self.setState({os_rst:true}); v.os_rst_cancel=()=>self.setState({os_rst:false});
  v.os_rst_ok=()=>{ cenReset(); self.setState({os_rst:false,pan:null,pa:null,nv:null,cenrev:Date.now(),g2toast:'Demonstração restaurada: O.S., estoque e app voltaram ao início.'}); };
}
'''

def bloco(titulo,desc,corpo,acao=''):
    desc=''   # 13/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos títulos ... somos minimalistas e essencialistas")
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: center; gap: 12px; padding: 12px 16px 10px; flex-wrap: wrap;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{esc(titulo)}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>{acao}</div>'
            f'<div style="padding: 0 12px 12px; display: flex; flex-direction: column; gap: 10px;">{corpo}</div></section>')

def _chip_hole(t,st,dot,dica=None):   # selo de estado: a dica (significado e próximo passo) vem do dicionário único do g2lib (DS-DICA-20261009)
    # ou, com dica, do texto que a tela montou (selo do bloqueio do encerramento: osSeloDica, revisão DS, achado 6)
    at=f'data-dica="{H(dica)}"' if dica else f'data-dica-de="{H(t)}"'
    return f'<span {at} style="{H(st)}"><span style="{H(dot)}"></span>{H(t)}</span>'

def _kanban(celular_rola=False):
    """Quadro das 5 fases. celular_rola (O.S., revisão VISOES-1 achado B6): até 640 px cada coluna guarda 148 px e o quadro rola na horizontal,
    em vez de 5 colunas de ~45 px com títulos e cartões encobertos (a página não rola de lado). A Manutenção (MA) usa o quadro sem isso."""
    card=(f'<div role="button" tabIndex="0" aria-label="{H("k.lab")}" onClick="{H("k.open")}" onKeyDown="{H("k.key")}" style="{H("k.st")}">'
          f'<div style="display: flex; align-items: baseline; gap: 6px;"><b style="font-size: 13px;">{H("k.id")}</b></div>'
          f'<div style="font-size: 12.5px; font-weight: 600; line-height: 1.3;">{H("k.tipo")}</div>'
          f'<div style="font-size: 12px; color: {MUTED};">{H("k.local")}</div>'
          f'<sc-if value="{H("k.hasBar")}" hint-placeholder-val="{T()}"><span style="display: block; height: 6px; border-radius: 999px; background: {GRAYS}; overflow: hidden;"><span style="{H("k.bar")}"></span></span></sc-if>'
          f'<sc-if value="{H("k.hasReal")}" hint-placeholder-val="{T()}"><div style="font-size: 11.5px; color: {MUTED}; font-variant-numeric: tabular-nums;">{H("k.real")}</div></sc-if>'
          f'<div style="display: flex; flex-wrap: wrap; gap: 4px;"><sc-for list="{H("k.selos")}" as="s" hint-placeholder-count="1">{_chip_hole("s.t","s.st","s.dot","s.dica")}</sc-for></div>'
          f'<sc-if value="{H("k.hasObs")}" hint-placeholder-val="{F()}"><div style="font-size: 11.5px; color: {MUTED};">{H("k.obs")}</div></sc-if>'
          f'<sc-if value="{H("k.hasDp")}" hint-placeholder-val="{F()}"><div style="font-size: 11.5px; font-weight: 700; color: {INK};">{H("k.dp")}</div></sc-if>'
          f'<div style="font-size: 11.5px; color: {MUTED};">{H("k.meta")}</div></div>')
    col=(f'<div class="os-kbcol" style="flex: 1 1 0; min-width: 0; background: {BG}; border: 1px solid {LINE}; border-radius: 12px; padding: 10px; display: flex; flex-direction: column; gap: 8px;">'
         f'<div style="display: flex; align-items: center; gap: 6px;"><span data-dica-de="{H("c.t")}" style="font-size: 11px; font-weight: 800; letter-spacing: .05em; color: {INK}; text-transform: uppercase;">{H("c.t")}</span>'
         f'<span style="{H("c.nst")} padding: 1px 8px; font-size: 11.5px;">{H("c.n")}</span></div>'
         f'<div style="font-size: 11.5px; color: {MUTED}; margin-top: -4px; min-height: 14px;">{H("c.carga")}</div>'
         f'<sc-for list="{H("c.cards")}" as="k" hint-placeholder-count="2">{card}</sc-for>'
         f'<sc-if value="{H("c.vazio")}" hint-placeholder-val="{F()}"><div style="font-size: 12px; color: {MUTED}; padding: 10px 4px; text-align: center; border: 1px dashed {LINE}; border-radius: 10px;">Nenhuma ordem nesta fase</div></sc-if></div>')
    rola = ('<style>@media (max-width:640px){.os-kb{overflow-x:auto;padding-bottom:6px}.os-kb .os-kbcol{flex:0 0 148px!important;min-width:148px!important}}</style>'
            if celular_rola else '')
    return rola + f'<div role="list" aria-label="Kanban das ordens" class="{"os-kb" if celular_rola else ""}" style="display: flex; gap: 10px; align-items: flex-start;"><sc-for list="{H("kb")}" as="c" hint-placeholder-count="5">{col}</sc-for></div>'

def _culturas_da(o):
    sid=next((s['id'] for s in D2.SAFRAS if s.get('fazenda')==o.get('faz') and str(s.get('nome','')).endswith(str(o.get('saf','')))),None)
    cs=D2.CULTIVOS.get(sid,[]) if sid else []; out=[]
    for t in (o.get('talhoes') or []):
        tid=str(t.get('id','')); alvo={tid}|({'Pivô '+str(int(tid[2:]))} if tid.startswith('PV') and tid[2:].isdigit() else set())
        for c in cs:
            l=c['local']
            if (l in alvo or any(l.startswith(a+'-') or a.startswith(l+'-') for a in alvo)) and c['cultura'] not in out: out.append(c['cultura'])
    return out

def _notas_tal():
    """avisos que eram do seletor de Talhão da barra (subiu para a faixa "Filtros desta tela" em 13/10): o total de O.S. distintas na Tabela
    agrupada (os grupos se sobrepõem) e o aviso de talhão que saiu do filtro ao trocar Fazenda, Safra ou Cultura."""
    return (f'<sc-if value="{H("os_agr")}" hint-placeholder-val="{F()}"><span role="note" style="font-size: 12px; color: {MUTED};">{H("os_gtot")}</span></sc-if>'
            f'<sc-if value="{H("os_temmsg")}" hint-placeholder-val="{F()}"><span role="status" style="font-size: 12px; font-weight: 700; color: #8A5A00;">{H("os_tmsg")}</span></sc-if>')

def _chips():
    return (f'<div role="group" aria-label="Filtrar por fase" style="display: flex; flex-wrap: wrap; gap: 6px;">'
            f'<sc-for list="{H("fchips")}" as="fc" hint-placeholder-count="7"><button type="button" aria-pressed="{H("fc.on")}" onClick="{H("fc.fn")}" style="{H("fc.st")}">{H("fc.t")}<span style="{H("fc.nst")}">{H("fc.n")}</span></button></sc-for></div>')

_LNK='border: 0; background: transparent; padding: 4px 2px; font-family: inherit; font-size: 12.5px; font-weight: 700; color: #4B5A51; text-decoration: underline; text-underline-offset: 3px; cursor: pointer;'
_LNKB=('font-family: inherit; font-size: 12.5px; font-weight: 700; color: #15201A; background: transparent; border: 0; padding: 4px 2px; cursor: pointer; '
       'text-decoration: underline; text-underline-offset: 3px; white-space: nowrap;')   # ação de texto dentro da linha (Tirar/Desfazer)
def _painel():
    lab=lambda t: f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{t}</div>'
    sv_dn='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex-shrink: 0;"><path d="M6 9l6 6 6-6"/></svg>'
    sv_rt='<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex-shrink: 0;"><path d="M9 6l6 6-6 6"/></svg>'
    # seção recolhível: título + uma linha de resumo; abre por padrão só o que faz a ordem andar na fase (panSecs)
    def sec(k,titulo,corpo):
        return (f'<sc-if value="{H("psx_"+k+"_show")}" hint-placeholder-val="{T()}"><section aria-label="{titulo}" style="border: 1px solid {LINE}; border-radius: 12px;">'
          f'<button type="button" onClick="{H("psx_"+k+"_tog")}" aria-expanded="{H("psx_"+k+"_ex")}" style="display: flex; align-items: center; gap: 8px; width: 100%; padding: 9px 12px; border: 0; background: transparent; cursor: pointer; font-family: inherit; text-align: left; color: {INK};">'
          f'<sc-if value="{H("psx_"+k)}" hint-placeholder-val="{F()}">{sv_dn}</sc-if><sc-if value="{H("psx_"+k+"_c")}" hint-placeholder-val="{T()}">{sv_rt}</sc-if>'
          f'<span style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase; flex-shrink: 0;">{titulo}</span>'
          f'<sc-if value="{H("psx_"+k+"_c")}" hint-placeholder-val="{T()}"><span style="font-size: 12.5px; color: {MUTED}; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{H("psx_"+k+"_sum")}</span></sc-if></button>'
          f'<sc-if value="{H("psx_"+k)}" hint-placeholder-val="{F()}"><div style="padding: 0 12px 12px; display: flex; flex-direction: column; gap: 6px;">{corpo}</div></sc-if></section></sc-if>')
    aprow=(f'<div style="display: grid; grid-template-columns: 64px 84px 1fr 1.3fr auto; gap: 8px; align-items: center; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 12.8px; font-variant-numeric: tabular-nums; {H("a.rst")}">'
           f'<span>{H("a.d")}</span><span>{H("a.dia")}</span><span style="text-align: right;">{H("a.ha")}</span><span style="text-align: right; font-weight: 700;">{H("a.ac")}</span>{_chip_hole("a.t","a.st","a.dot")}</div>'
           f'<sc-if value="{H("a.dup")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Decidir duplicidade" style="display: flex; flex-direction: column; gap: 6px; padding: 0 0 8px;">'
           f'<span style="font-size: 12.5px; color: #8A5A00; font-weight: 600;">{H("a.dupT")}</span>'
           f'<sc-if value="{H("a.hasUs")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 6px;"><sc-for list="{H("a.usx")}" as="u" hint-placeholder-count="1">'
           f'<label style="display: grid; grid-template-columns: minmax(0,1fr) 96px; gap: 2px 10px; align-items: center; font-size: 12px; font-weight: 600; color: {MUTED};"><span>{H("u.lab")}</span>'
           f'<input aria-label="{H("u.lab")}" inputMode="decimal" value="{H("u.v")}" onChange="{H("u.set")}" style="font-family: inherit; font-size: 14px; padding: 6px 9px; border-radius: 8px; border: 1px solid {LINE}; text-align: right; grid-row: span 2;">'
           f'<span style="font-weight: 400; font-size: 11.5px;">{H("u.hint")}</span></label></sc-for></div></sc-if>'
           f'<sc-if value="{H("a.pode")}" hint-placeholder-val="{T()}"><div style="display: flex; gap: 6px; flex-wrap: wrap;">'
           f'<sc-if value="{H("a.hasAnt")}" hint-placeholder-val="{T()}"><button type="button" onClick="{H("a.ant")}" style="{_MINI}">{H("a.vant")}</button></sc-if>'
           f'<sc-if value="{H("a.hasEste")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("a.este")}" style="{_MINI}">Mesmo turno: vale este</button></sc-if>'
           f'<button type="button" onClick="{H("a.somar")}" style="{_MINI}">Outro turno: somar</button></div></sc-if></div></sc-if>'
           # B-R8: divergência de consumo/dose (planejado × informado) e a revisão técnica do agrônomo na mesma linha
           f'<sc-if value="{H("a.div")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Revisão técnica da dose" style="display: flex; flex-direction: column; gap: 6px; padding: 0 0 8px;">'
           f'<span style="font-size: 12.5px; color: {RED}; font-weight: 700; line-height: 1.4;">{H("a.divT")}</span>'
           f'<sc-if value="{H("a.hasRev")}" hint-placeholder-val="{F()}"><span style="font-size: 12.5px; color: {MUTED}; line-height: 1.4;">{H("a.revT")}</span></sc-if>'
           f'<sc-if value="{H("a.hasDivQ")}" hint-placeholder-val="{F()}"><span style="font-size: 12.5px; color: #8A5A00; font-weight: 600; line-height: 1.4;">{H("a.divQ")}</span></sc-if>'
           f'<sc-if value="{H("a.dvPode")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 6px;">'
           f'<textarea id="{H("a.dvfid")}" aria-label="{H("a.dvlab")}" placeholder="Motivo para aceitar, ou a correção/reaplicação decidida" value="{H("a.dvv")}" onChange="{H("a.dvset")}" style="font-family: inherit; font-size: 13px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; min-height: 48px; resize: vertical; box-sizing: border-box; width: 100%;"></textarea>'
           f'<sc-if value="{H("a.hasDverr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("a.dverr")}</span></sc-if>'
           f'<div style="display: flex; gap: 6px; flex-wrap: wrap;"><button type="button" onClick="{H("a.dvAc")}" style="{_MINI}">Aceitar com motivo</button>'
           f'<button type="button" onClick="{H("a.dvCo")}" style="{_MINI}">Registrar correção</button></div></div></sc-if></div></sc-if>')
    aprow += _CD.linha_html()
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
      f'{_car_rev_html()}'   # carência: Rever programação (MAPA-CARENCIA-LMR-20261003)
      f'<sc-if value="{H("pan_hasObs")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; color: {MUTED};">{H("pan_obs")}</div></sc-if>'
      f'<sc-if value="{H("pan_hasDono")}" hint-placeholder-val="{F()}"><div style="font-size: 12.8px; font-weight: 700;">{H("pan_dono")}</div></sc-if>'
      f'<sc-if value="{H("pan_hasAviso")}" hint-placeholder-val="{F()}"><div style="font-size: 12.5px; font-weight: 700; color: {YEL}; background: {YELS}; padding: 7px 10px; border-radius: 8px;">{H("pan_aviso")}</div></sc-if>'
      f'<sc-if value="{H("pan_idle")}" hint-placeholder-val="{T()}"><div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">'
      f'<sc-if value="{H("pan_hasBtn")}" hint-placeholder-val="{T()}"><button type="button" onClick="{H("pan_go")}" style="{BTN_ST(True,True)}">{H("pan_pbtn")}</button></sc-if>'
      f'<sc-if value="{H("pan_hasAj")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("pan_secgo")}" title="Mudar dose ou área antes de liberar (gera a versão seguinte)" style="{_MINI}">{H("pan_ajbtn")}</button></sc-if>'
      f'<span style="flex-grow: 1;"></span>'
      f'<sc-if value="{H("pan_hasDisp")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("pan_disgo")}" title="Dispensar parte do saldo sem executar (o realizado fica preservado)" style="{_LNK}">Dispensar saldo</button></sc-if>'
      f'<sc-if value="{H("pan_hasDispQ")}" hint-placeholder-val="{F()}"><span style="font-size: 12px; color: {MUTED};">{H("pan_dispQ")}</span></sc-if>'
      f'<sc-if value="{H("pan_hasCanc")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("pan_cango")}" title="Cancelar a ordem que ainda não teve execução (exige motivo)" style="{_LNK} color: {RED};">Cancelar sem execução</button></sc-if></div></sc-if>'
      f'<sc-if value="{H("pan_canf")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
      f'<div style="font-size: 13px; font-weight: 600; line-height: 1.45;">{H("pan_cct")}</div>'
      f'<textarea aria-label="Motivo do cancelamento" placeholder="Motivo do cancelamento" value="{H("pan_rmot")}" onChange="{H("pan_setrmot")}" style="font-family: inherit; font-size: 13px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; min-height: 54px; resize: vertical;"></textarea>'
      f'<sc-if value="{H("pan_hasRerr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_rerr")}</span></sc-if>'
      f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Voltar</button><button type="button" onClick="{H("pan_cansave")}" style="{_MINI} color: #fff; background: {RED}; border-color: {RED};">Confirmar cancelamento</button></div></div></sc-if>'
      f'<sc-if value="{H("pan_disf")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
      f'<div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end;"><label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {MUTED};">Área a dispensar (ha)<input aria-label="Área a dispensar em hectares" inputMode="decimal" value="{H("pan_aha")}" onChange="{H("pan_setaha")}" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; width: 110px; text-align: right;"></label>'
      f'<span style="font-size: 12px; color: {MUTED}; padding-bottom: 9px; flex: 1 1 260px;">{H("pan_dsub")}</span></div>'
      f'<textarea aria-label="Motivo da dispensa" placeholder="Motivo da dispensa" value="{H("pan_rmot")}" onChange="{H("pan_setrmot")}" style="font-family: inherit; font-size: 13px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; min-height: 54px; resize: vertical;"></textarea>'
      f'<span style="font-size: 13px; font-weight: 600;">{H("pan_dval")}</span>'
      f'<sc-if value="{H("pan_hasRerr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_rerr")}</span></sc-if>'
      f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Voltar</button><button type="button" onClick="{H("pan_dissave")}" style="{_MINIP}">Confirmar dispensa</button></div></div></sc-if>'
      f'<sc-if value="{H("pan_conf")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE}; font-size: 13px; font-weight: 600; line-height: 1.45;">{H("pan_ct")}'
      f'<sc-if value="{H("pan_hasRerr")}" hint-placeholder-val="{F()}"><span style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_rerr")}</span></sc-if>'
      f'<div style="display: flex; gap: 8px; flex-wrap: wrap;"><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Voltar</button>'
      f'<sc-if value="{H("pan_hasAjc")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("pan_ajgo")}" style="{_MINI}">{H("pan_ajbtn")}</button></sc-if>'
      f'<button type="button" onClick="{H("pan_yes")}" style="{_MINIP}">{H("pan_cbtn")}</button></div></div></sc-if>'
      # ajustar antes de liberar: dose por insumo e área (erro junto ao campo); Salvar e liberar grava a versão seguinte e libera
      f'<sc-if value="{H("pan_ajf")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Ajustar antes de liberar" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
      f'<div style="font-size: 13px; font-weight: 600; line-height: 1.45;">{H("pan_ajt")}</div>'
      f'<div style="display: flex; flex-direction: column; gap: 3px;"><div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"><label for="aj_area" style="font-size: 12.8px; font-weight: 700; flex: 1 1 180px; min-width: 0;">Área da ordem</label>'
      f'<input id="aj_area" aria-label="Área da ordem (ha)" inputMode="decimal" value="{H("pan_ajarea")}" onChange="{H("pan_setajarea")}" style="{H("pan_ajast")}"><span style="font-size: 12px; color: {MUTED}; min-width: 44px;">ha</span><span style="min-width: 120px;"></span><span aria-hidden="true" style="{_LNKB} min-width: 64px; visibility: hidden;">Desfazer</span></div>'
      f'<sc-if value="{H("pan_hasAjaerr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_ajaerr")}</span></sc-if></div>'
      f'<sc-for list="{H("pan_ajins")}" as="d" hint-placeholder-count="2"><div style="display: flex; flex-direction: column; gap: 3px;"><div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">'
      f'<span style="flex: 1 1 180px; min-width: 0; display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap;"><label for="{H("d.fid")}" style="font-size: 12.8px; font-weight: 700; {H("d.pst")}">{H("d.p")}</label>'
      f'<sc-if value="{H("d.hasAgf")}" hint-placeholder-val="{F()}"><a href="{H("d.agf")}" target="_blank" rel="noopener" title="Ver a ficha no Consulta Agrofit" style="font-size: 12px; font-weight: 700; color: {ACC}; text-decoration: none; white-space: nowrap;">Agrofit ›</a></sc-if></span>'
      f'<sc-if value="{H("d.keep")}" hint-placeholder-val="{T()}"><input id="{H("d.fid")}" aria-label="{H("d.lab")}" inputMode="decimal" value="{H("d.v")}" onChange="{H("d.set")}" style="{H("d.st")}"><span style="font-size: 12px; color: {MUTED}; min-width: 44px;">{H("d.un")}</span></sc-if>'
      f'<span style="font-size: 12px; color: {MUTED}; min-width: 120px; text-align: right; font-variant-numeric: tabular-nums;">{H("d.tot")}</span>'
      f'<button type="button" onClick="{H("d.tir")}" title="{H("d.tirTt")}" aria-label="{H("d.tirTt")}" style="{_LNKB} min-width: 64px; text-align: left;">{H("d.tirT")}</button></div>'
      f'<sc-if value="{H("d.hasWarn")}" hint-placeholder-val="{F()}"><span role="status" style="font-size: 12px; font-weight: 700; color: {YEL};">{H("d.warn")}</span></sc-if>'
      f'<sc-if value="{H("d.hasErr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("d.err")}</span></sc-if></div></sc-for>'
      f'<sc-for list="{H("pan_ajadd")}" as="n" hint-placeholder-count="0"><div class="{H("n.cls")}" style="display: flex; flex-direction: column; gap: 3px;"><div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">'
      f'<span style="flex: 1 1 180px; min-width: 0; display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap;"><label for="{H("n.fid")}" style="font-size: 12.8px; font-weight: 700;">{H("n.p")} <span style="font-size: 11px; font-weight: 800; color: {ACC};">incluído</span></label>'
      f'<sc-if value="{H("n.hasAlvo")}" hint-placeholder-val="{F()}"><span style="font-size: 12px; color: {MUTED};">{H("n.alvoT")}</span></sc-if>'
      f'<sc-if value="{H("n.hasAgf")}" hint-placeholder-val="{F()}"><a href="{H("n.agf")}" target="_blank" rel="noopener" title="Ver a ficha no Consulta Agrofit" style="font-size: 12px; font-weight: 700; color: {ACC}; text-decoration: none; white-space: nowrap;">Agrofit ›</a></sc-if></span>'
      f'<input id="{H("n.fid")}" aria-label="{H("n.lab")}" inputMode="decimal" value="{H("n.v")}" onChange="{H("n.set")}" style="{H("n.st")}"><span style="font-size: 12px; color: {MUTED}; min-width: 44px;">{H("n.un")}</span>'
      f'<span style="font-size: 12px; color: {MUTED}; min-width: 120px; text-align: right; font-variant-numeric: tabular-nums;">{H("n.tot")}</span>'
      f'<button type="button" onClick="{H("n.rm")}" title="Tirar o produto incluído" aria-label="Tirar {H("n.p")}" style="{_LNKB} min-width: 64px; text-align: left;">Tirar</button></div>'
      f'<sc-if value="{H("n.hasErr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("n.err")}</span></sc-if></div></sc-for>'
      f'<div style="display: flex; flex-direction: column; gap: 3px; padding-top: 4px; border-top: 1px dashed {LINE};"><div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">'
      f'<input id="aj_inc" list="aj_prods" aria-label="Incluir produto" placeholder="Incluir produto…" value="{H("pan_ajq")}" onChange="{H("pan_setajq")}" onKeyDown="{H("pan_ajqkey")}" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; flex: 1 1 200px; min-width: 0; background: #FFFFFF; color: {INK};">'
      f'<datalist id="aj_prods"><sc-for list="{H("pan_ajopts")}" as="q" hint-placeholder-count="3"><option value="{H("q.p")}">{H("q.t")}</option></sc-for></datalist>'
      f'<button type="button" onClick="{H("pan_ajinc")}" style="{_MINI}">Incluir</button></div>'
      f'<sc-if value="{H("pan_hasAjqerr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_ajqerr")}</span></sc-if></div>'
      f'<sc-if value="{H("pan_hasRerr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_rerr")}</span></sc-if>'
      f'<div class="acoes-form" role="group" aria-label="Ações do ajuste"><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Voltar</button><span class="acoes-esp"></span><sc-if value="{H("pan_hasAjs2")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("pan_ajsave2")}" style="{_MINI}">Salvar ajuste</button></sc-if><button type="button" onClick="{H("pan_ajsave")}" style="{_MINIP}">{H("pan_ajsbtn")}</button></div></div></sc-if>'
      f'<sc-if value="{H("pan_apf")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
      f'<div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end;"><label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {MUTED};">Data do turno<input type="date" aria-label="Data do turno" value="{H("pan_ad")}" onChange="{H("pan_setad")}" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE};"></label>'
      f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {MUTED};">Área feita (ha)<input aria-label="Área feita em hectares" inputMode="decimal" value="{H("pan_aha")}" onChange="{H("pan_setaha")}" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; width: 110px; text-align: right;"></label>'
      f'<span style="font-size: 12px; color: {MUTED}; padding-bottom: 9px;">{H("pan_asub")}</span></div>'
      f'<span style="font-size: 12.5px; color: {INK}; font-weight: 600;">{H("pan_aquem")}</span>'
      f'<sc-if value="{H("pan_hasAdup")}" hint-placeholder-val="{F()}"><span role="status" style="font-size: 12px; font-weight: 600; color: #8A5A00;">{H("pan_adup")}</span></sc-if>'
      f'<sc-if value="{H("pan_hasAcons")}" hint-placeholder-val="{T()}"><div style="display: flex; flex-direction: column; gap: 6px;"><sc-for list="{H("pan_acons")}" as="x" hint-placeholder-count="2">'
      f'<label style="display: grid; grid-template-columns: minmax(0,1fr) 96px; gap: 2px 10px; align-items: center; font-size: 12px; font-weight: 600; color: {MUTED};"><span>{H("x.lab")}</span>'
      f'<input aria-label="{H("x.lab")}" inputMode="decimal" value="{H("x.v")}" onChange="{H("x.set")}" style="font-family: inherit; font-size: 14px; padding: 6px 9px; border-radius: 8px; border: 1px solid {LINE}; text-align: right; grid-row: span 2;">'
      f'<span style="font-weight: 400; font-size: 11.5px;">{H("x.hint")}</span></label>'
      f'<sc-if value="{H("x.hasWarn")}" hint-placeholder-val="{F()}"><span role="status" style="font-size: 12px; font-weight: 600; color: #8A5A00;">{H("x.warn")}</span></sc-if></sc-for></div></sc-if>'
      f'<sc-if value="{H("pan_hasAerr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("pan_aerr")}</span></sc-if>'
      f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("pan_back")}" style="{_MINI}">Cancelar</button><button type="button" onClick="{H("pan_asave")}" style="{_MINIP}">Salvar apontamento</button></div></div></sc-if></div>')
    return (f'<sc-if value="{H("pan_open")}" hint-placeholder-val="{F()}"><div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar painel" onClick="{H("pan_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside role="dialog" data-foco="1" aria-label="{H("pan_t")}" onKeyDown="{H("pan_key")}" style="position: relative; width: 820px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">'
      f'<div style="display: flex; align-items: flex-start; gap: 10px;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; font-weight: 700; letter-spacing: -.02em; flex-grow: 1; line-height: 1.3;">{H("pan_t")}</h2>'
      f'<sc-if value="{H("pan_hasLink")}" hint-placeholder-val="{F()}"><a href="{H("pan_link")}" style="{_MINI} text-decoration: none; display: inline-flex; align-items: center; white-space: nowrap;">Abrir ordem completa ›</a></sc-if>'
      f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H("pan_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
      f'<div style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">{_chip_hole("pan_fase","pan_fst","pan_fdot")}<sc-for list="{H("pan_selos")}" as="s" hint-placeholder-count="1">{_chip_hole("s.t","s.st","s.dot","s.dica")}</sc-for></div>'
      f'<div style="display: flex; flex-direction: column; gap: 5px;"><div style="font-size: 13px; font-weight: 600;">{H("pan_res")}</div>'
      f'<sc-if value="{H("pan_hasProg")}" hint-placeholder-val="{F()}"><div style="display: flex; align-items: center; gap: 10px;"><div style="flex-grow: 1; height: 6px; border-radius: 999px; background: #E4E9E5; overflow: hidden;"><div style="{H("pan_progst")}"></div></div>'
      f'<span style="font-size: 12px; color: {MUTED}; white-space: nowrap; font-variant-numeric: tabular-nums;">{H("pan_prog")}</span></div></sc-if></div>'
      f'<div role="list" aria-label="Fase da ordem" style="display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 6px;"><sc-for list="{H("pan_steps")}" as="p" hint-placeholder-count="5"><div role="listitem" aria-current="{H("p.cur")}" style="{H("p.st")}"><span style="{H("p.bst")}"></span>{H("p.t")}</div></sc-for></div>'
      + passo
      + sec('ins','Insumos e doses',f'<sc-if value="{H("pan_hasIns")}" hint-placeholder-val="{T()}">{inshead}<sc-for list="{H("pan_ins")}" as="i" hint-placeholder-count="2">{insrow}</sc-for></sc-if>'
      f'<sc-if value="{H("pan_semIns")}" hint-placeholder-val="{F()}"><div style="font-size: 12.8px; color: {MUTED}; padding: 6px 0;">{H("pan_semInsT")}</div></sc-if>'
      f'<sc-if value="{H("pan_hasRet")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 6px; padding-top: 6px;">{lab(H("pan_retT"))}'
      f'<sc-if value="{H("pan_hasPrep")}" hint-placeholder-val="{F()}"><div style="font-size: 13px; line-height: 1.45;">{H("pan_prep")}</div></sc-if>'
      f'<div style="display: flex; gap: 8px; flex-wrap: wrap;"><sc-if value="{H("pan_retLink")}" hint-placeholder-val="{T()}"><a href="EST.dc.html" style="{_MINI} text-decoration: none;">Retirar no almoxarifado ›</a></sc-if>'
      f'<sc-if value="{H("pan_fichas")}" hint-placeholder-val="{F()}"><a href="OS-0424-app.dc.html" style="{_MINI} text-decoration: none;">Ficha no app (sem internet) ›</a><a href="OS-0424-ficha.dc.html" style="{_MINI} text-decoration: none;">Ficha impressa ›</a></sc-if></div></div></sc-if>')
      + sec('ap','Apontamentos diários',f'<sc-if value="{H("pan_hasAp")}" hint-placeholder-val="{T()}">{aphead}<sc-for list="{H("pan_ap")}" as="a" hint-placeholder-count="4">{aprow}</sc-for>'
      f'<sc-if value="{H("pan_hasAcum")}" hint-placeholder-val="{T()}"><div style="padding: 8px 0 0; border-top: 2px solid {INK}; font-size: 13px; font-weight: 800;">{H("pan_acum")}</div></sc-if>'
      f'<sc-if value="{H("pan_hasNota")}" hint-placeholder-val="{F()}"><div style="font-size: 12px; color: {MUTED};">{H("pan_nota")}</div></sc-if></sc-if>'
      f'<sc-if value="{H("pan_noAp")}" hint-placeholder-val="{F()}"><div style="font-size: 12.8px; color: {MUTED}; padding: 6px 0;">{H("pan_noApT")}</div></sc-if>')
      + sec('rec','Recursos alocados',f'<sc-for list="{H("pan_rec")}" as="rc" hint-placeholder-count="3"><div style="display: grid; grid-template-columns: minmax(0,1.2fr) minmax(0,1fr) minmax(0,1.3fr); gap: 10px; align-items: center; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 12.8px;">'
      f'<b>{H("rc.t")}</b><span style="color: {MUTED};">{H("rc.j")}</span><span style="display: flex; flex-wrap: wrap; gap: 4px;"><sc-if value="{H("rc.cond")}" hint-placeholder-val="{F()}"><span style="display: inline-flex; padding: 2px 8px; border-radius: 999px; font-size: 11.5px; font-weight: 700; color: #8A5A00; background: #FFF4D6;">condicional</span></sc-if>'
      f'<sc-for list="{H("rc.al")}" as="al" hint-placeholder-count="1"><span style="display: inline-flex; padding: 2px 8px; border-radius: 999px; font-size: 11.5px; font-weight: 700; color: #B42318; background: #FDE8E6;">{H("al.t")}</span></sc-for></span></div></sc-for>')
      + sec('atv','Atividade',kvbox("pan_atv"))
      + sec('sit','Situação atual',f'<div style="font-size: 13px; line-height: 1.45;">{H("pan_cond")}</div>')
      + sec('ori','Origem',f'<sc-for list="{H("pan_orig")}" as="og" hint-placeholder-count="2"><div style="font-size: 13px; padding: 5px 0; border-bottom: 1px solid {LINE};">{H("og.t")}</div></sc-for>') +
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
      f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45;">Escolha safra, cultivo e atividade do plano. A ordem nasce em A liberar; o agrônomo libera e pode ajustar antes.</div>'
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

def _rcv(os_id, html):   # bloco de uma ordem em Recursos: some quando a ordem está fora do recorte da lista (TABELAS-FOCO)
    return f'<sc-if value="{H("rcv_" + os_id.replace("-", ""))}" hint-placeholder-val="{T()}">{html}</sc-if>'
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
                if a['os'] in LAM:   # irrigação só com água: é do módulo Irrigação (01/10), o bloco leva para lá
                    hr = 'IR-03det.dc.html' if a['os'] == 'OS-0419' else 'IR-03.dc.html'
                    its += _rcv(a['os'], f'<a href="{hr}" title="Irrigação · abrir {a["os"]} no módulo Irrigação" style="display: block; font-size: 11.5px; font-weight: 700; padding: 3px 6px; border-radius: 6px; text-decoration: none; background: #E8F0F8; color: #2F5F8A; border: 1px solid #C9DBEC;">{esc(t)} · irrigação</a>'); continue
                its += _rcv(a['os'], f'<button type="button" onClick="{H("op_" + a["os"].replace("-", ""))}" title="{tt}" style="display: block; width: 100%; text-align: left; font-family: inherit; font-size: 11.5px; font-weight: 700; padding: 3px 6px; border-radius: 6px; cursor: pointer; {st}">{t}</button>')
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
               f'<span><b style="color: {ACC};">■</b> alocação firme</span><span><b style="color: #8A5A00;">▭</b> condicional (depende da liberação)</span>'
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
    # TABELAS-FOCO (5983172395): uma variável de negócio por coluna, valor tipado (data ISO, número) e Talhão/Situação multivalorados
    g_os=grid([dict(k='id',l='O.S.'),dict(k='ativ',l='Atividade',w=190),dict(k='tal',l='Talhão',multi=True,w=120),dict(k='local',l='Local',w=110,zdash=True),
               dict(k='area',l='Área (ha)',t='num',a='r',d=2,zdash=False),dict(k='ini',l='Início',t='date'),dict(k='fim',l='Fim',t='date'),
               dict(k='fase',l='Fase'),dict(k='sit',l='Situação',multi=True,w=200),dict(k='obs',l='Observação',w=200),
               dict(k='dono',l='Quem resolve'),dict(k='acao',l='Próxima ação',w=150),dict(k='prazo',l='Prazo'),
               dict(k='real',l='Realizado (ha)',t='num',a='r',d=2),dict(k='saldo',l='Saldo (ha)',t='num',a='r',d=2),
               dict(k='disp',l='Dispensado (ha)',t='num',a='r',d=2,zdash=True),dict(k='prog',l='Progresso (%)',t='num',a='r',d=1),
               dict(k='resp',l='Responsável')],   # sem coluna Lâmina: a O.S. só com água saiu para a Irrigação (01/10), onde a lâmina tem colunas próprias (IR-03); aqui ela ficava sempre vazia
              [],edit=dict(m='pick'),gid='g_os',total=False,tree=True,vazio=False)   # vazio de filtro: estado comum das visões (VISOES-1 §2.8)
    # barra da coleção (DS-33 §74.5.7.1): filtros rápidos no começo, seletor de visão no fim; vale para Lista e Kanban (mesmo filtro)
    kb_nota=(f'<sc-if value="{H("kb_filtro")}" hint-placeholder-val="{F()}"><div role="note" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 12.5px; color: {MUTED}; margin-bottom: 8px;">'
             f'<span>{H("kb_nota")}</span><button type="button" onClick="{H("os_limpar")}" style="{_MINI}">Limpar filtros</button></div></sc-if>')
    rc_nota=f'<div role="note" style="font-size: 12.5px; color: {MUTED}; margin-bottom: 8px;">{H("rc_nota")}</div>'
    # revisão VISOES-1, achado C3 (§2.8 "Parcial"): ordens do recorte sem bloco na semana do PCP, cada uma abre o mesmo painel
    rc_nota+=(f'<sc-if value="{H("rc_semtem")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Ordens do recorte sem alocação na semana do PCP" '
              f'style="display: flex; align-items: center; gap: 6px 8px; flex-wrap: wrap; font-size: 12.5px; margin-bottom: 8px;"><b>{H("rc_semt")}</b>'
              f'<sc-for list="{H("rc_sem")}" as="s" hint-placeholder-count="2"><button type="button" onClick="{H("s.go")}" style="{_MINI}">{H("s.id")}</button></sc-for></div></sc-if>')
    # VISOES-1 (proprietário, 10/10/2026): seletor por ícone; Lista e Tabela agrupada na mesma grade (o agrupamento é estado da grade),
    # Kanban e Carga por recurso migram sem mudança de regra. Visões válidas: visoes.py (fonte única; O.S. sem Mapa: DEC-2609-09)
    bar,panes=visoes('g_os','os',{'lista':g_os,'agrupada':'lista','kanban':kb_nota+_kanban(celular_rola=True),'calendario':kb_nota+_calendario(),'carga':rc_nota+_recursos_tab()},rotulo='Visão das ordens')
    colbar=(f'<div class="os-colbar" style="display: flex; align-items: flex-start; gap: 10px; flex-wrap: wrap;"><div style="flex: 1 1 320px; min-width: 0; display: flex; flex-direction: column; gap: 8px;">{_chips()}{_notas_tal()}</div>'   # o Talhão subiu para a faixa "Filtros desta tela" (13/10); os avisos dele ficam aqui
            f'<div style="flex: 0 0 auto; margin-left: auto;">{bar}</div></div>')
    # recorte vazio (Fazenda/Safra do topo): uma frase e uma ação no lugar das visões
    vazio=(f'<sc-if value="{H("os_vazio")}" hint-placeholder-val="{F()}"><div aria-label="Sem ordens no filtro" style="display: flex; align-items: center; justify-content: center; gap: 12px; flex-wrap: wrap; padding: 36px 16px; border: 1px dashed {LINE}; border-radius: 12px;">'
           f'<span style="font-size: 14px; font-weight: 700;">{H("os_vt")}</span><button type="button" onClick="{H("os_vgo")}" style="{_MINIP}">{H("os_va")}</button></div></sc-if>')
    tem=lambda x: f'<sc-if value="{H("os_tem")}" hint-placeholder-val="{T()}">{x}</sc-if>'
    corpo=bloco('Ordens por fase','Clique numa ordem para ver atividade, insumos e doses e seguir para a próxima fase.',
                vazio+tem(f'<div style="display: flex; flex-direction: column; gap: 10px;">{colbar}{panes}</div>')+_restaurar(),
                acao=f'<span style="display: inline-flex; align-items: center; gap: 10px;"><button type="button" onClick="{H("nv_open")}" style="padding: 7px 14px; border-radius: 9px; font-size: 13px; font-weight: 700; font-family: inherit; cursor: pointer; white-space: nowrap; background: {ACC}; color: #fff; border: 1px solid {ACC}; flex-shrink: 0;">Nova ordem</button></span>')
    EXTRA.append(_painel()); EXTRA.append(_form())
    # cultura de cada ordem (13/10, filtro Cultura): a do cultivo de cada talhão da ordem na safra dela (D2.SAFRAS e D2.CULTIVOS, fonte do Planejar safra)
    for o in ordens: o['culturas']=_culturas_da(o)
    data=dict(ords=ordens,nova=_nova_ordem_dados(),aloc={o['id']:AL.da_ordem(o['id']) for o in ordens},agf=_agf_fichas())
    # cenário compartilhado (O.S. ↔ Estoque ↔ App) antes do JS da tela
    # blocos da Carga de ordens fora da lista da O.S. (irrigação só com água, do módulo Irrigação): Fazenda e Safra delas, para seguirem o recorte do topo
    rc_ext={o['id']:[o['faz'],o['saf']] for o in D.ORDENS if o['id'] in {a['os'] for a in AL.ALOC if a['sit']!='manutenção'} and o['id'] not in {x['id'] for x in ordens}}
    EXTRAJS[0]=cenario.js_prefixo()+'const OSD = '+json.dumps(data,ensure_ascii=False).replace('</','<\\/')+';\n'+'const RC_EXT = '+json.dumps(rc_ext,ensure_ascii=False)+';\n'+'const RC_OS = '+json.dumps(sorted({a['os'] for a in AL.ALOC if a['sit']!='manutenção'}))+';\n'+JS_NUCLEO+JS
    prim=f'<button type="button" onClick="{H("nv_open")}" style="{BTN_ST(True)}">Nova ordem</button>'
    HEIGHTS37[fname]=1000
    shell37('OS','Ordem de Serviço',corpo,fname=fname,
            subtitle='A liberar → Liberadas → Em execução → Em conferência → Encerradas. Pausa, atraso, parcial e impedimento aparecem como selos.',
            status=(H('os_st'),'red'),primary_html=None,search=False,  # "Nova ordem" mora no bloco Ordens por fase
            footer='A fase só muda por evento: liberação, início, término físico e encerramento. Finalizar apontamento do turno não encerra a O.S.')
    _status_dinamico(fname)
    return fname

def _calendario():
    """VISOES-2 (F2a) · Calendário das ordens, só leitura: semana de segunda a domingo com ‹ › e Hoje; cada dia lista as ordens da janela;
    faixa "Sem data"; abaixo de 900 px vira agenda por dia (só os dias com ordem). Sem arrastar: programar fica no detalhe (DESENHO §2.9)."""
    css = ('<style>.oscal{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:8px}'
           '.oscal-dia{display:flex;flex-direction:column;gap:6px;min-width:0;padding:8px;border:1px solid #E4E9E5;border-radius:12px;background:#FBFCFA;min-height:140px}'
           '.oscal-dia[data-hoje=true]{border-color:#1E7A4C;background:#F2F8F4}'
           '.oscal-dt{display:flex;justify-content:space-between;gap:6px;font-size:12px;font-weight:800;color:#4B5A51;text-transform:capitalize}'
           '.oscal-o{display:flex;flex-direction:column;align-items:flex-start;gap:3px;text-align:left;width:100%;box-sizing:border-box;padding:7px 8px;border:1px solid #E4E9E5;'
           'border-radius:10px;background:#FFFFFF;cursor:pointer;font-family:inherit;color:#15201A;min-height:44px;min-width:0;overflow-wrap:anywhere}'
           '@media (hover:hover){.oscal-o:hover{border-color:#1E7A4C;background:#F2F8F4}}.oscal-o:focus-visible{outline:2px solid #1E7A4C;outline-offset:1px}'
           '@media (max-width:900px){.oscal{grid-template-columns:1fr}.oscal-dia{min-height:0}.oscal-dia[data-vazio=true]{display:none}}</style>')
    cab = (f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 8px;">'
           f'<button type="button" aria-label="Semana anterior" onClick="{H("cal_prev")}" style="{_MINI}">‹</button>'
           f'<b style="font-size: 14px;" aria-live="polite">{H("cal_tit")}</b>'
           f'<button type="button" aria-label="Próxima semana" onClick="{H("cal_next")}" style="{_MINI}">›</button>'
           f'<sc-if value="{H("cal_naoHoje")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("cal_hoje")}" style="{_MINI}">Hoje</button></sc-if>'
           f'<span style="font-size: 12.5px; color: {MUTED};">{H("cal_n")}</span></div>')
    sem = (f'<sc-if value="{H("cal_temsem")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Sem data" style="display: flex; align-items: center; gap: 6px 8px; flex-wrap: wrap; '
           f'padding: 8px 10px; margin-bottom: 8px; border: 1px dashed {LINE}; border-radius: 10px; font-size: 12.5px;"><b>Sem data</b>'
           f'<sc-for list="{H("cal_sem")}" as="o" hint-placeholder-count="1"><button type="button" aria-label="{H("o.lab")}" onClick="{H("o.open")}" style="{_MINI}">{H("o.id")} · {H("o.tipo")}</button></sc-for></div></sc-if>')
    dias = (f'<div class="oscal" role="list" aria-label="Semana das ordens"><sc-for list="{H("cal")}" as="d" hint-placeholder-count="7">'
            f'<div class="oscal-dia" role="listitem" data-hoje="{H("d.hoje")}" data-vazio="{H("d.vz")}" aria-label="{H("d.t")}"><div class="oscal-dt"><span>{H("d.t")}</span><span>{H("d.nt")}</span></div>'
            f'<sc-for list="{H("d.ords")}" as="o" hint-placeholder-count="1"><button type="button" class="oscal-o" aria-label="{H("o.lab")}" onClick="{H("o.open")}">'
            f'<b style="font-size: 12.5px;">{H("o.id")}</b><span style="font-size: 12px; line-height: 1.3;">{H("o.tipo")}</span>'
            f'<span style="font-size: 11.5px; color: {MUTED};">{H("o.local")}</span><span style="{H("o.fst")}"><span style="{H("o.fdot")}"></span>{H("o.fase")}</span></button></sc-for>'
            f'<sc-if value="{H("d.vazio")}" hint-placeholder-val="{F()}"><span style="font-size: 12px; color: {MUTED};">sem ordem</span></sc-if></div></sc-for></div>')
    return css + cab + sem + dias

def _agf_fichas():
    """Nome usado na fazenda → ficha do Consulta Agrofit (AG-07): id, classe e grupo de ação. Fertilizante, semente e muda ficam fora."""
    import agrofit_dados as A
    return {n:dict(id=p['id'],cl=p['classe'],g=(p['grupo'] if p['grupos'] else '')) for p in A.PRODUTOS for n in p['nomes_fazenda']}

def _status_dinamico(fname):
    """troca o selo fixo do cabeçalho (shell37 pinta de vermelho) por um selo com a cor calculada na tela (os_stst / os_stdot)."""
    import ui37
    p=os.path.join(E.P,fname); s=open(p,encoding='utf-8').read(); old=ui37.chip(H('os_st'),'red')
    assert s.count(old)==1, 'selo do cabeçalho não encontrado em '+fname
    open(p,'w',encoding='utf-8').write(s.replace(old,f'<span style="{H("os_stst")}"><span style="{H("os_stdot")}"></span>{H("os_st")}</span>'))
# ---- Fazenda Lagoa Grande: tabelas das ordens (dados_lagoa_safra.py) ----
import dados_lagoa_safra as _DL
VERSAO.update({_k:_vsem(_v) for _k,_v in _DL.VERSAO.items()}); COND.update(_DL.COND); ORIG.update(_DL.ORIG); ATV.update(_DL.ATV); INS.update(_DL.INS); SEM_INS.update(_DL.SEM_INS); BLOQ.update(_DL.BLOQ); DONO.update(_DL.DONO)
for _k,_v in _DL.AP.items(): AP[_k]=_v

# ===================== Carência e destino (MAPA-CARENCIA-LMR-20261003) =====================
# Motor puro e regras em dados_carencia.py (CARD + JS), anexado ao núcleo: a tela O.S. e o Mapa usam os mesmos cálculos.
# Colheita: liberar/iniciar impedidos no comando enquanto a carência corre (motivo e dono); registrar colheita feita nunca é impedido.
# Aplicação: aviso preventivo (não bloqueia) quando a carência cai na janela de colheita do talhão ou no mamão em produção.
import conferencia_diaria as _CD
JS_NUCLEO += _CD.js_nucleo()
JS += _CD.js_ui()

import dados_carencia as _DCAR
JS_NUCLEO += _DCAR.js_nucleo()
JS += r"""
// carência: Rever programação da colheita impedida (nova data de início ≥ fim da carência) → carc_janela no cenário
function carOsVals(self,v,o,b){ const cb=(b&&b.car&&b.fim&&carEhColheita(o)&&(o.etapa==='A liberar'||o.etapa==='Liberadas'))?b:null; v.car_rev=!!cb;
  const st=(self.state.carj&&self.state.carj.id===o.id)?self.state.carj:null; v.car_rev_d=st?st.d:(cb?cb.fim:''); v.car_rev_min=CARD.hoje;
  v.car_rev_err=(st&&st.err)||''; v.car_rev_hasErr=!!v.car_rev_err; v.car_rev_t=cb?'Carência até '+carAte(cb.fim)+': a colheita pode começar em '+carBr(cb.fim)+' ou depois.':'';
  v.car_rev_set=(e)=>self.setState({carj:{id:o.id,d:e.target.value,err:''}});
  v.car_rev_go=()=>{ const cur=(self.state.carj&&self.state.carj.id===o.id)?self.state.carj.d:(cb?cb.fim:''); osRun(self,c=>carc_janela(c,o.id,cur),{carj:null},(e)=>self.setState({carj:{id:o.id,d:cur,err:e}})); };
  carOsBula(self,v,o,b); }
// carência sem prazo conhecido (uso não achado, não conferida na bula ou produto fora do cadastro): o agrônomo registra a carência conferida
// na bula do produto comercial (carc_bula) na colheita impedida ou na própria O.S. da aplicação; a pendência some e o prazo passa a contar
function carOsBula(self,v,o,b){ let bt=(b&&b.car&&(b.pk==='regra'||b.pk==='bula')&&b.p)?{p:b.p,cult:b.cult}:null;
  if(!bt&&!carEhColheita(o)){ const c=cenGet(); carTals(o.talhao).forEach(x=>{ if(bt) return; const p=carEstado(c,x.tid).pend.find(q=>q.os===o.id&&(q.k==='regra'||q.k==='bula')&&q.p); if(p) bt={p:p.p,cult:p.cult}; }); }
  v.car_bula=!!bt; const st=(self.state.carb&&bt&&self.state.carb.k===bt.p+'|'+bt.cult)?self.state.carb:null;
  v.car_bula_t=bt?'Carência de '+bt.p+' em '+String(bt.cult||'').toLowerCase()+': confira na bula do produto comercial e registre os dias.':'';
  v.car_bula_d=st?st.d:''; v.car_bula_err=(st&&st.err)||''; v.car_bula_hasErr=!!v.car_bula_err; v.car_bula_st=v.pan_hasBtn?CAR_MINI:CAR_MINIP;
  v.car_bula_set=(e)=>self.setState({carb:{k:bt.p+'|'+bt.cult,d:e.target.value,err:''}});
  v.car_bula_go=()=>{ const d=(self.state.carb&&self.state.carb.k===bt.p+'|'+bt.cult)?self.state.carb.d:''; osRun(self,c=>carc_bula(c,bt.p,bt.cult,d),{carb:null},(e)=>self.setState({carb:{k:bt.p+'|'+bt.cult,d,err:e}})); }; }
"""
JS = JS.replace('// carência sem prazo conhecido (uso', 'const CAR_MINI='+json.dumps(_MINI)+', CAR_MINIP='+json.dumps(_MINIP)+';\n// carência sem prazo conhecido (uso',1)
def _car_rev_html():
    inp=f'font-family: inherit; font-size: 13px; padding: 7px 10px; border: 1px solid {LINE}; border-radius: 9px; background: #fff; box-sizing: border-box; max-width: 100%;'
    return (f'<sc-if value="{H("car_rev")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Rever programação da colheita" style="display: flex; flex-direction: column; gap: 6px;">'
            f'<div style="font-size: 12.5px; color: {MUTED};">{H("car_rev_t")}</div><div style="display: flex; flex-wrap: wrap; align-items: flex-end; gap: 8px;">'
            f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 700;">Nova data de início<input type="date" min="{H("car_rev_min")}" value="{H("car_rev_d")}" onChange="{H("car_rev_set")}" style="{inp}"></label>'
            f'<button type="button" onClick="{H("car_rev_go")}" style="{_MINIP}">Rever programação</button></div>'
            f'<sc-if value="{H("car_rev_hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("car_rev_err")}</div></sc-if></div></sc-if>'
            f'<sc-if value="{H("car_bula")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Registrar carência conferida na bula" style="display: flex; flex-direction: column; gap: 6px;">'
            f'<div style="font-size: 12.5px; color: {MUTED};">{H("car_bula_t")}</div><div style="display: flex; flex-wrap: wrap; align-items: flex-end; gap: 8px;">'
            f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 700;">Carência na bula (dias)<input type="text" inputmode="numeric" value="{H("car_bula_d")}" onChange="{H("car_bula_set")}" style="{inp} width: 9em;"></label>'
            f'<button type="button" onClick="{H("car_bula_go")}" style="{H("car_bula_st")}">Registrar carência conferida</button></div>'
            f'<sc-if value="{H("car_bula_hasErr")}" hint-placeholder-val="{F()}"><div role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("car_bula_err")}</div></sc-if></div></sc-if>')
