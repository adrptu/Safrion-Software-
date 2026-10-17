# -*- coding: utf-8 -*-
"""Área Campo (módulo OCULTO do menu, preservado) — CA-01 Ordens de campo (+ CA-01det OS-0421 e CA-01x-os0420 OS-0420) ·
CA-02 Apontamentos e conferência · CA-03 Ocorrências (+ CA-03det OC-114) · CA-04 Minhas requisições.
Padrão novo (25/09/2026): descrição imperativa sob cada bloco, edição pela linha (G2), ações secundárias com ícone + rótulo + title,
sem faixa de etapas (módulo não sequencial).

observacoes (dados locais coerentes com dados.py / dados2.py / processo_os.py):
- Ordens = dados.ORDENS (registro canônico, só OS-*): ids, fases, selos (selo + selos_extra), saldos e janelas vêm dali;
  versão vem de processo_os.VERSAO (a mesma da tela Ordem de Serviço). "Voltar" dos detalhes CA-01det e CA-01x-os0420 → OS.dc.html.
- OS-0420: 30 ha realizados preservados na v2 (18 ha conferidos em 21/09 + 12 ha provisórios em 22/09); saldo de 70 ha na v3
  (KCl −12 % só no saldo), ajustada por Ana (agrônoma) em 23/09 e já em vigor. O saldo está parado só pelo Trator T1 (OM-0233), substituto
  Trator 02 a partir de 24/09; não há pendência do agrônomo na OS-0420.
  Mantido 30/100 ha (e não 60/40) porque dados.py, OS.dc.html e AG-04det usam 30/70; ver "prd".
- Instrução da OS-0420 herdada da REC-014 v2 (agronomia.py): KCl 60 % 120 kg/ha (zonas 140/120/95), TS nematicida 100 mL/100 kg de semente,
  semente de soja 58 W 52 kg/ha (plano SOJA-AT) · janela da recomendação 20/09–05/10; janela da ordem 22–28/09.
- Materiais = dados2.REQUISICOES: REQ-031 (OS-0417, MAP 100/70/20/10 sc, custódia de Paula), REQ-035 (OS-0421, Fungicida A 175/160/95 L,
  custódia 65 L com Marcos), REQ-036 (OS-0420, semente 5.200/1.560/1.560 kg), REQ-038 (OS-0418, Ureia 1.140 kg, aguardando liberação).
  Consumo diário de Fungicida A na OS-0421: 25, 25, 25, 20 L (0,50 L/ha da v2).
- Horas do turno do dia 2 da OS-0420: 3,1 h (03:30–06:40) contra 1,8 h previstas (12 ha ÷ 6,8 ha/h, rendimento de plantio em dados2.CONJ).
- Roteiro projetado da OS-0418 após a liberação (DEMO-16): Ureia 45 % 1.140 kg entregues, 1.100 kg consumidos, 40 kg devolvidos;
  lâmina de 6,7 mm já aplicada como água antes da reclassificação fica no balanço hídrico e não é reapontada.
- Nova ocorrência recebe OC-117 em diante.
- Irrigação só com água (26/09, igual à O.S. e a areas/irrigacao.py): sem agrônomo, libera pela prontidão operacional.
  OS-0422 "Janela a definir" (João, irrigante) · OS-0423 "Conflito · parada da B3" (Caio, PCP), estimativa por ET sem bloquear.
"""
import json
from engine import (grid,Pt,kpis,chip,icon,esc,msgbtn,drawer_button,legend,stepper,BTN_ST,EXTRA,EXTRAJS,_MINI,
                    INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,SH,DISP)
import engine as E
from ui37 import shell37, continuity, tabs, HEIGHTS37, PARENT37
import dados as D
import dados2 as D2

H=lambda s: '{{'+s+'}}'
DET0420='CA-01x-os0420.dc.html'
_JAN={o['id']:o['janela'] for o in D.ORDENS}
try:  # irrigação só com água (26/09): tipo, lâmina e nota vêm da mesma fonte da tela Ordem de Serviço
    from areas.processo_os import TIPO as _TIPO, LAM as _LAM, OBS as _OBS
except Exception:
    _TIPO,_LAM,_OBS={},{},{}

FASES=['A liberar','Liberadas','Em execução','Em conferência','Encerradas']
FCOR={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray'}
PRAZO={'OS-0421':'no prazo','OS-0420':'no prazo','OS-0419':'vence hoje','OS-0418':'até 3 dias','OS-0423':'vence hoje'}
PCOR={'atrasada':'red','vence hoje':'orange','até 3 dias':'yellow','no prazo':'green'}
EQUIPE={'OS-0421':'Marcos · Pulverizador PJ-3030 + Trator 03','OS-0420':'Carlos · Plantadeira PD-12 + Trator T1 (bloqueado)',
        'OS-0419':'João · Pivô 2','OS-0418':'João · Pivô 1','OS-0417':'Paula · Distribuidor DA-08','OS-0415':'Marcos · Pulverizador PJ-3030 + Trator 03',
        'OS-0422':'João · Pivô 2','OS-0423':'João · Gotejo T7','OS-0424':'Marcos · Pulverizador PJ-3030 + Trator 03',
        'OS-0425':'Paula · Distribuidor DA-08','OS-0430':'Marcos · Pulverizador PJ-3030 + Trator 03','OS-0431':'Carlos · Plantadeira PD-12 + Trator T1 (bloqueado)'}
EQ_OPTS=['Marcos · Pulverizador PJ-3030 + Trator 03','Carlos · Plantadeira PD-12 + Trator T1 (bloqueado)','Carlos · Plantadeira PD-12 + Trator 02 (substituto)',
         'João · Pivô 1','João · Pivô 2','João · Gotejo T7','Paula · Distribuidor DA-08']
QUEM={'OS-0421':'Turno do dia 4 aguardando conferência · Paula',
      'OS-0420':'OM-0233 · Manutenção · substituto a partir de 24/09 · saldo de 70 ha parado (já na v3)',
      'OS-0419':'Pronta para iniciar hoje às 20:00 · João',
      'OS-0418':'Ana (agrônoma) · liberar (pode ajustar a dose antes) · Ureia 45 % sem saldo apto',
      'OS-0417':'Paula (equipe de campo) devolve 10 sc até 24/09 · Rui recebe no almoxarifado',
      'OS-0422':'João (irrigante) define a janela das 2 passadas',
      'OS-0423':'Caio (PCP) resolve a parada da B3 (14:00–15:00) · estimativa por ET · sonda sem dado'}
PROX={'OS-0421':('Conferir dia 4','CA-02.dc.html'),'OS-0420':('Ver OM-0233','MA.dc.html#om=OM-0233'),
      'OS-0419':('Abrir em Irrigação','IR-03det.dc.html'),'OS-0418':('Liberar','OS.dc.html#OS-0418'),
      'OS-0417':('Ver custódia','CA-04.dc.html'),'OS-0422':('Definir janela','IR-02.dc.html'),'OS-0423':('Resolver conflito','IR-02.dc.html')}
DETALHE={'OS-0421':'CA-01det.dc.html','OS-0420':DET0420}
REALIZ={'OS-0421':'150 conf. + 40 prov. · saldo 160 ha','OS-0420':'18 conf. + 12 prov. · saldo 70 ha parado'}
_RED=('impedid','bloquead','atrasad','conflito','vencid')

def nf(n,d=0):
    s=f'{n:,.{d}f}'
    return s.replace(',','X').replace('.',',').replace('X','.')
def _selos(o):  # selo principal + selos_extra do registro (mesma lista da O.S. e do Mapa)
    ts=([o['selo']] if o.get('selo') else [])+list(o.get('selos_extra') or [])
    return [(t,'red' if any(w in t.lower() for w in _RED) else 'yellow') for t in ts]
def _impedida(o): return any('impedida' in t.lower() or 'falta máquina' in t.lower() for t,_ in _selos(o))
def _eqp(eq):
    pes,_,conj=eq.partition(' · ')
    return [Pt.txt(pes),Pt.br(),Pt.mut(conj)]
_VER={o['id']:o.get('versao') for o in D.OS}
try:  # versão = a mesma da tela Ordem de Serviço (rótulo só "vN", sem "aprovada" nem "emitida")
    from areas.processo_os import VERSAO as _VOS
    _VER.update(_VOS)
except Exception: pass
def _versao(o): return 'v2 · v3 no saldo' if o['id']=='OS-0420' else (_VER.get(o['id']) or 'v1')
def _ordens():  # registro canônico dados.ORDENS (fase, selo, saldo, janela); tipo de água igual ao da O.S.
    os_=[dict(o,tipo=_TIPO.get(o['id'],o['tipo'])) for o in D.ORDENS if o['id'].startswith('OS')]
    return sorted(os_,key=lambda o:(FASES.index(o['etapa']),o['id']))

# ---------- vocabulário visual local ----------
def bloco(titulo,desc,corpo,acao='',tone=None):
    acao=E.recolhe_acoes(titulo,acao)   # MAIS-01 (15/10/2026): uma secundária à vista, as outras no "⋯ Mais ações" do bloco
    desc=''   # 13/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos títulos ... somos minimalistas e essencialistas")
    dot={'yellow':YEL,'red':RED}.get(tone,ACC)
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; box-shadow: {SH}; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: center; gap: 12px; padding: 12px 16px 10px; flex-wrap: wrap;">'
            f'<span style="width: 9px; height: 9px; border-radius: 999px; background: {dot}; flex-shrink: 0; align-self: flex-start; margin-top: 6px;"></span>'
            f'<div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{esc(titulo)}</h3>'
            f'<div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>'
            f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">{acao}</div></div>'
            + (f'<div style="padding: 0 12px 12px; display: flex; flex-direction: column; gap: 10px;">{corpo}</div>' if str(corpo).strip() else '') + '</section>')   # 14/10/2026: sem corpo vazio
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
def nota(html_):
    return f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.6;">{html_}</div>'
def alerta(html_,tone='yellow'):
    c,bg=(YEL,YELS) if tone=='yellow' else (RED,REDS)
    return f'<div role="status" style="padding: 10px 14px; border-radius: 12px; background: {bg}; color: {c}; font-size: 13px; font-weight: 700; line-height: 1.45;">{html_}</div>'
def _kv(pares):
    return ('<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px 18px;">'
            + ''.join(f'<div><div style="font-size: 10.5px; font-weight: 700; letter-spacing: .06em; color: {MUTED};">{esc(k.upper())}</div>'
                      f'<div style="font-size: 13.5px; color: {INK}; margin-top: 3px; line-height: 1.4;">{v}</div></div>' for k,v in pares) + '</div>')

# ---------- CA-01 · Kanban e mapa ----------
def _kanban(ordens):
    cols=''
    for et in FASES:
        os_=[o for o in ordens if o['etapa']==et]
        cards=''
        for o in os_:
            selos=''.join(f'<div style="margin-top: 5px;">{chip(t,c)}</div>' for t,c in _selos(o))
            real=(f' · {nf(o["realizado"])}/{nf(o["area"])} ha' if o.get('area') and o.get('realizado') else (f' · {nf(o["area"])} ha' if o.get('area') else ''))
            inner=(f'<b>{o["id"]}</b> · {esc(o["tipo"].split(" · ")[0])}<br><span style="color:{MUTED};">{esc(o["talhao"])}{real}</span>{selos}')
            st=f'display: block; margin-top: 8px; background: {SURF}; border: 1px solid {LINE}; border-radius: 10px; padding: 8px 10px; font-size: 12px; box-shadow: {SH}; color: {INK}; text-decoration: none;'
            det=DETALHE.get(o['id'])
            cards+=(f'<a href="{det}" title="Abrir {o["id"]}" style="{st}">{inner}</a>' if det else f'<div style="{st}">{inner}</div>')
        cols+=(f'<div style="flex: 1 1 0; min-width: 0; background: {BG}; border: 1px solid {LINE}; border-radius: 12px; padding: 10px;">'
               f'<div style="display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 800; letter-spacing: .05em; color: {MUTED};">{et.upper()} {chip(str(len(os_)),FCOR[et])}</div>{cards}</div>')
    return f'<div style="display: flex; gap: 10px; align-items: flex-start;">{cols}</div>'

def _mapa():
    def box(x,w,fill,stroke,dash,l1,l2,l3,l4=''):
        da=' stroke-dasharray="7 5"' if dash else ''
        return (f'<rect x="{x}" y="20" width="{w}" height="150" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2.5"{da}/>'
                f'<text x="{x+12}" y="46" font-size="13.5" font-weight="800" fill="{INK}">{l1}</text>'
                f'<text x="{x+12}" y="67" font-size="12" font-weight="600" fill="{INK}">{l2}</text>'
                f'<text x="{x+12}" y="86" font-size="11.5" fill="{MUTED}">{l3}</text>'
                + (f'<text x="{x+12}" y="104" font-size="11.5" fill="{MUTED}">{l4}</text>' if l4 else ''))
    def piv(cx,fill,stroke,l1,l2,l3,l4='',l4c=RED):
        return (f'<circle cx="{cx}" cy="95" r="76" fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>'
                f'<text x="{cx}" y="74" text-anchor="middle" font-size="13.5" font-weight="800" fill="{INK}">{l1}</text>'
                f'<text x="{cx}" y="94" text-anchor="middle" font-size="11.5" font-weight="600" fill="{INK}">{l2}</text>'
                f'<text x="{cx}" y="111" text-anchor="middle" font-size="11" fill="{MUTED}">{l3}</text>'
                + (f'<text x="{cx}" y="127" text-anchor="middle" font-size="11" fill="{l4c}" font-weight="700">{l4}</text>' if l4 else ''))
    s=f'<svg viewBox="0 0 1180 190" style="width: 100%; height: auto; display: block;" role="img" aria-label="Mapa das ordens abertas por talhão">'
    s+=f'<rect x="0" y="0" width="1180" height="190" rx="12" fill="#EEF3EA"/>'
    wr=int(316*190/350)
    s+=box(14,320,ACCS,ACC,False,'T1 + T2 · OS-0421','Em execução · 190/350 ha','selo Parcial · dia 4 de 7')
    s+=f'<rect x="16" y="130" width="{wr}" height="38" fill="{ACC}" fill-opacity=".28"/><text x="26" y="154" font-size="11.5" font-weight="700" fill="{ACC}">realizado 190 ha</text><text x="{16+wr+8}" y="154" font-size="11.5" fill="{MUTED}">saldo 160 ha</text>'
    wr2=int(216*30/100)
    s+=box(346,220,REDS,RED,True,'T4 · OS-0420','Em execução · 30/100 ha','Impedida · OM-0233')
    s+=f'<rect x="348" y="130" width="{wr2}" height="38" fill="{RED}" fill-opacity=".18"/><text x="{348+wr2+8}" y="154" font-size="11.5" fill="{MUTED}">saldo 70 ha</text>'
    s+=box(578,112,GRAYS,'#9AA59E',False,'T3 · OS-0415','Encerrada','96/96 ha')
    s+=box(702,130,REDS,RED,True,'T7 · OS-0423','A liberar · 42 ha','Conflito · parada B3','estimativa por ET')
    s+=piv(920,YELS,YEL,'P1 · Pivô 1','OS-0417 em conferência','OS-0418 a liberar')
    s+=piv(1092,ACCS,ACC,'P2 · Pivô 2','OS-0419 liberada · 0/80 ha','OS-0422 a liberar','janela a definir',YEL)
    return s+'</svg>'

# ---------------- CA-01 · Ordens de campo ----------------
def _ca01():
    fname='CA-01.dc.html'; E._reset_screen(fname)
    ordens=_ordens()
    rows=[]
    for o in ordens:
        det=DETALHE.get(o['id'])
        jan=o.get('janela') or _JAN.get(o['id'],'—'); fx=PRAZO.get(o['id']) if o['etapa'] in ('A liberar','Liberadas','Em execução') else None
        selos=_selos(o)
        cond=[Pt.chip(t,c) for t,c in selos] or [Pt.mut('Sem pendência')]
        if o['id'] in QUEM: cond+=[Pt.br(),Pt.mut(QUEM[o['id']])]
        if o['id'] in PROX: cond+=[Pt.br(),Pt.link(PROX[o['id']][0]+' ›',PROX[o['id']][1])]
        real=o.get('realizado') if o.get('area') else None
        rp=([Pt.txt(f'{nf(o["realizado"])} / {nf(o["area"])} ha'),Pt.br(),Pt.mut(REALIZ.get(o['id'],f'saldo {nf(o["saldo"])} ha'))] if o.get('area') else [Pt.mut('—')])
        rows.append(dict(id=o['id'],ro=(o['etapa']=='Encerradas'),
            v=dict(id=o['id'],ativ=f'{o["tipo"]} · {o["talhao"]}',jan=jan,fase=o['etapa'],cond=' · '.join(t for t,_ in selos),eq=EQUIPE[o['id']],real=real),
            s=dict(id=o['id']+' '+_versao(o),ativ=f'{o["tipo"]} {o["talhao"]}',cond=' '.join(t for t,_ in selos)+' '+QUEM.get(o['id'],''),jan=jan),
            p=dict(id=([Pt.link(o['id'],det)] if det else [Pt.b(o['id'])])+[Pt.br(),Pt.mut(_versao(o))],
                   ativ=[Pt.txt(o['tipo']),Pt.br(),Pt.mut(o['talhao']+(f' · {nf(o["area"])} ha' if o.get('area') else '')+(f' · {_LAM[o["id"]]}' if o['id'] in _LAM else ''))],
                   jan=[Pt.txt(jan)]+([Pt.br(),Pt.chip(fx,PCOR[fx])] if fx else []),fase=[Pt.chip(o['etapa'],FCOR[o['etapa']])],
                   cond=cond,real=rp,eq=_eqp(EQUIPE[o['id']]))))
    g_os=grid([dict(k='id',l='O.S.',w=100),dict(k='ativ',l='Atividade · local',w=150),dict(k='jan',l='Janela',w=96),dict(k='fase',l='Fase',chips=FCOR),
               dict(k='cond',l='Condição · próxima ação',w=225),dict(k='real',l='Realizado · saldo',t='num',w=125),dict(k='eq',l='Equipe · conjunto',w=130)],
        rows,edit=dict(m='form',title='Ordem',sub='Ajuste a janela e a equipe da ordem. Trocar a data não troca produto nem área autorizados; ordem encerrada abre só em consulta.',
            fields=[dict(k='id',l='O.S.',ro=True),dict(k='ativ',l='Atividade · local',ro=True),dict(k='fase',l='Fase',ro=True),
                    dict(k='jan',l='Janela',t='txt',req=True,help='Ex.: 24–26/09. A ordem mantém produto, dose e área da versão liberada.'),
                    dict(k='eq',l='Equipe · conjunto',t='sel',opts=EQ_OPTS,req=True,help='Conjunto bloqueado só volta a ser elegível com a manutenção liberada.')]),
        sel=True,gid='g_os',total=False,
        bulk=('<details style="max-width: 100%; white-space: normal;"><summary style="'+BTN_ST(False,True)+'">'+E.seta()+'Conferir caminho de liberação</summary><p>Prévia dos dados da lista ao abrir a tela, sem executar liberação. Confira a prontidão atual na O.S.; com produto, aprove a versão antes de liberar.</p><ul>' + ''.join('<li>'+esc(o['id'])+' · '+esc(o['etapa'])+' · '+esc(' · '.join(t for t,_ in _selos(o)) or 'Conferir prontidão na O.S.')+' · <a href="OS.dc.html#'+esc(o['id'])+'">Abrir O.S. ›</a></li>' for o in ordens if o['etapa']=='A liberar') + '</ul><p>Todas as O.S. a liberar da lista, independentemente da seleção. Nenhuma ordem foi alterada.</p></details>'))
    kan=_kanban(ordens)
    mapa=_mapa()+f'<div style="margin-top: 8px;">{legend([(ACC,"Em execução ou liberada"),(YEL,"Em conferência ou a liberar"),(RED,"Impedida ou em conflito (tracejado)"),("#9AA59E","Encerrada")])}</div>'
    bar,panes=tabs(['Lista','Kanban','Mapa'],[g_os,kan,mapa],active=0,label='Visão das ordens')
    n_lib=sum(1 for o in ordens if o['etapa']=='A liberar'); n_fp=sum(1 for o in ordens if o['etapa']=='A liberar' and o['id'] in _LAM)
    n_ag=sum(1 for o in ordens if o['etapa']=='A liberar' and o['id'] not in _LAM)   # com produto: o agrônomo libera
    n_imp=sum(1 for o in ordens if _impedida(o))
    abertas=[o for o in ordens if o['etapa']!='Encerradas' and o.get('area') and o.get('saldo')]
    saldo=sum(o['saldo'] for o in abertas)
    acoes=E.recolhe_acoes('Ordens da janela de trabalho',[ilink('Conferir apontamentos','CA-02.dc.html','check','Abrir a fila de conferência dos turnos'),
           ilink('Reprogramar saldo','PL-05.dc.html','calendar','Reprogramar o saldo das ordens no PCP')])
    n_out=n_lib-n_ag-n_fp
    corpo=(kpis([('A LIBERAR',str(n_lib),f'{n_ag} com produto · {n_fp} só água'+(f' · {n_out} {"outra" if n_out==1 else "outras"}' if n_out else '')),('EM CONFERÊNCIA','1','sobras a receber'),
                 ('SALDO PARADO','70 ha','OS-0420 · Trator T1 (OM-0233)'),('SALDO ABERTO',f'{nf(saldo)} ha',f'{len(abertas)} ordens')])
           + bloco('Ordens da janela de trabalho','Clique numa ordem para ajustar janela e equipe; use o link da condição para resolver a pendência.',
                   f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">{bar}<span style="flex-grow: 1;"></span>{acoes}</div>{panes}'))
    prim=idrawer('Preparar e emitir período',dict(title='Preparar e emitir período',sub='Emita a necessidade agregada da janela uma única vez, sem duplicar pendências de períodos anteriores.',
             fields=[('Janela','Próximos 7 dias'),('Fazenda','Santa Rita'),('Atividades','Pulverização, plantio, adubação'),('Necessidade agregada','545 ha em 3 ordens')],
             confirm='Emitir ordens do período',done='Emitidas · A liberar (o agrônomo libera)'),'calendar','Emitir as ordens da janela para o agrônomo liberar',primary=True,small=False)
    HEIGHTS37[fname]=1500
    shell37('CA-01','Ordens de campo',corpo,
      subtitle='A liberar → Liberadas → Em execução → Em conferência → Encerradas. Parcial, pausa e impedimento aparecem como selos.',
      status=(f"{sum(1 for o in ordens if o['etapa']=='Em execução')} em execução · {n_imp} impedidas",'red'),primary_html=prim,
      footer='Emitir não autoriza: com produto, o agrônomo libera a ordem e pode ajustar antes; só água libera pela prontidão. Término físico entra automaticamente em Em conferência.')

# ---------------- CA-01det · OS-0421 (350 ha em 7 dias, hoje = dia 4) ----------------
TURNOS=[('20/09',1,50,'Conferido','app · sincronizado'),('21/09',2,50,'Conferido','app · sincronizado'),('22/09',3,50,'Conferido','app · sincronizado'),
        ('23/09 (hoje)',4,40,'Provisório','app · sincronizado 17:40 · encerrado por chuva'),
        ('24/09',5,50,'Previsto',''),('25/09',6,50,'Previsto',''),('26/09',7,60,'Previsto','')]
REQ={r['id']:r for r in D2.REQUISICOES}
APJS=r'''
const CFC={'Conferido':'green','Provisório':'yellow','Previsto':'gray'};
function _apRecalc(rows){ let ac=0,real=0,prev=0; rows.forEach(r=>{ const ha=Number(r.v.ha)||0; const pv=r.v.cf==='Previsto'; ac+=ha; if(pv) prev+=ha; else real+=ha;
  r.v.ac=ac; if(r.s) delete r.s.ac; r.p=r.p||{}; r.p.ac=[{k:pv?'mut':'b',t:(pv?'prev. ':'')+ac.toLocaleString('pt-BR')+' / '+AREA+' ha'}]; }); return {real,prev}; }
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_ap'||!r) return;
    if(r.v.cf==='Conferido'){ r.p.cf=[{k:'chip',t:'Conferido',c:'green'},{k:'br'},{k:'mut',t:'corrigido · original na trilha'}]; }
    const t=_apRecalc(rows); g2set(self,'g_ap',{rows}); const saldo=AREA-t.real, dif=saldo-t.prev;
    const msg='Salvo · acumulado refeito: '+t.real.toLocaleString('pt-BR')+' / '+AREA+' ha · saldo '+saldo.toLocaleString('pt-BR')+' ha'
      +(dif===0?' · os turnos previstos cobrem o saldo.':(dif>0?' · faltam '+dif.toLocaleString('pt-BR')+' ha nos turnos previstos.':' · os previstos excedem o saldo em '+(-dif).toLocaleString('pt-BR')+' ha.'));
    self.setState({g2toast:msg}); };
  const on=!!((self.state.added||{})[DID]); v.v3_on=on;
  v.fichas=()=>self.setState({g2toast:on?FICHAS_REV:FICHAS_V2});
}
'''
def _ca01det():
    fname='CA-01det.dc.html'; E._reset_screen(fname)
    o=next(x for x in D.OS if x['id']=='OS-0421'); area=o['area']
    rows=[]; ac=0
    for dt,d,ha,cf,orig in TURNOS:
        ac+=ha; pv=(cf=='Previsto')
        rows.append(dict(id=f't{d}',v=dict(dt=dt,turno=f'Dia {d} de 7',ha=ha,ac=ac,cf=cf,orig=orig,kind=('Previsto' if pv else 'Apontado'),motivo=''),
            s=dict(orig=orig or '—'),
            p=dict(ac=[Pt.mut(f'prev. {nf(ac)} / {area} ha') if pv else Pt.b(f'{nf(ac)} / {area} ha')],
                   cf=[Pt.chip('Provisório · aguardando conferência','yellow')] if cf=='Provisório' else [Pt.chip(cf,{'Conferido':'green','Previsto':'gray'}[cf])],
                   orig=[Pt.mut(orig or '—')])))
    g_ap=grid([dict(k='dt',l='Data'),dict(k='turno',l='Turno'),dict(k='ha',l='Área do dia',t='num',a='r',u='ha'),dict(k='ac',l='Acumulado',t='num',a='r'),
               dict(k='cf',l='Conferência'),dict(k='orig',l='Origem · sincronização',w=280)],
        rows,edit=dict(m='form',title='Turno',sub='Corrija o apontamento com motivo (o original fica na trilha) ou redistribua os turnos previstos dentro do saldo.',
            fields=[dict(k='turno',l='Turno',ro=True),dict(k='kind',l='Tipo de registro',ro=True),dict(k='cf',l='Conferência',ro=True),
                    dict(k='ha',l='Área do dia',t='num',req=True,min=0,max=200,u='ha',help='Só área real; nunca arredonde nem complete por inferência.'),
                    dict(k='dt',l='Data prevista',t='txt',req=True,cond=dict(k='kind',eq='Previsto')),
                    dict(k='motivo',l='Motivo da correção',t='area',req=True,cond=dict(k='kind',eq='Apontado'),help='A correção gera nova versão do apontamento; o valor original permanece na trilha.')]),
        search=False,gid='g_ap',total=False)
    r=REQ['REQ-035']; pend=r['solicitado']-r['entregue']
    g_mat=grid([dict(k='item',l='Item · lote',w=220),dict(k='sol',l='Solicitado',t='num',a='r',u='L'),dict(k='ent',l='Entregue',t='num',a='r',u='L'),
                dict(k='cons',l='Consumido',t='num',a='r',u='L'),dict(k='cust',l='Em custódia',t='num',a='r',u='L'),dict(k='pend',l='A entregar',t='num',a='r',u='L'),dict(k='resp',l='Custódia de')],
        [dict(id='m1',v=dict(item='Fungicida A · lote F26-02',sol=r['solicitado'],ent=r['entregue'],cons=r['consumido'],cust=r['custodia'],pend=pend,resp='Marcos (equipe de campo)'),
              s={},p=dict(item=[Pt.txt('Fungicida A · lote F26-02'),Pt.br(),Pt.mut('REQ-035 · 0,50 L/ha da v2')],cust=[Pt.b(f'{r["custodia"]} L')]),
              o=[dict(t=f'Requisição REQ-035 · {r["solicitado"]} L para 350 ha (0,50 L/ha da v2)',h='SU-07.dc.html'),
                 dict(t=f'Entregue {r["entregue"]} L pelo almoxarifado à custódia de Marcos · faltam {pend} L'),
                 dict(t=f'Consumo apontado {r["consumido"]} L = 190 ha × 0,50 L/ha (dias 1 a 4: 25, 25, 25 e 20 L)',h='CA-02.dc.html'),
                 dict(t=f'Em custódia = {r["entregue"]} − {r["consumido"]} = {r["custodia"]} L · volta ao estoque só por devolução recebida')])],
        edit=dict(m='origin',title='Custódia',fields=[dict(k='item',l='Item · lote',ro=True),dict(k='ent',l='Entregue',ro=True,u='L'),dict(k='cons',l='Consumido',ro=True,u='L'),dict(k='cust',l='Em custódia',ro=True,u='L')]),
        search=False,gid='g_mat',total=False)
    ajuste=idrawer('Ajustar produtos e doses do saldo',dict(title='Ajustar produtos e doses do saldo',
             sub='Gera a v3 só para o saldo de 160 ha; os 190 ha realizados ficam preservados na v2. Ao liberar, as fichas do saldo passam à v3.',
             fields=[('Ordem','OS-0421 · v2'),('Área alcançada (ha)','160 · saldo'),('Ação do ajuste','Reduzir dose'),('Produto','Fungicida A'),('Nova dose por ha','0,45 L'),('Motivo','')],
             confirm='Ajustar e liberar saldo',done='v3 liberada · saldo de 160 ha'),'leaf','Ajustar e liberar o saldo (agrônomo)')
    DID=E.DRAWN['Ajustar produtos e doses do saldo']
    fichas=(f'<button type="button" onClick="{H("fichas")}" title="Consultar as fichas do caldeiro, do operador e do almoxarife" style="{BTN_ST(False,True)} display: inline-flex; align-items: center; gap: 6px;">{icon("doc",14)}Ver fichas</button>')
    FV2=(f'Fichas da v2 liberada para o saldo de 160 ha · caldeiro: Fungicida A 0,50 L/ha = 80 L · operador: T1+T2, faixas pendentes dos dias 5 a 7 · '
         f'almoxarife: 65 L em custódia de Marcos + 15 L a entregar da REQ-035.')
    FREV=('Fichas do saldo de 160 ha reemitidas na v3 liberada por Ana (agrônoma) · as fichas dos 190 ha realizados permanecem no histórico da v2.')
    banner=(f'<sc-if value="{H("v3_on")}" hint-placeholder-val="{H("false")}">'
            + alerta(f'{chip("v3 liberada no saldo","green")} &nbsp;Saldo de 160 ha na v3 · liberada por Ana (agrônoma). '
                     f'Os 190 ha realizados continuam preservados na v2.') + '</sc-if>')
    corpo=(
      continuity('Plano de safra · janela 20–26/09','Em execução · 190/350 ha','160 ha em 3 turnos','Registrar avanço')
      + banner
      + stepper([('A liberar','done'),('Liberadas','done'),('Em execução','now'),('Em conferência','todo'),('Encerradas','todo')],'')
      + kpis([('AUTORIZADO','350 ha','v2'),('REALIZADO','190 ha','150 conf. + 40 prov.'),('SALDO','160 ha','3 turnos'),('HOJE','Dia 4 de 7','40 ha · chuva')])
      + bloco('Apontamentos de turno','Confira um apontamento por dia na mesma ordem; clique no turno para corrigir com motivo ou redistribuir os previstos.',g_ap,
          imsg('Pausar execução','Pausada por chuva · a ordem ganha o selo Pausada e continua Em execução; "Retomar execução" devolve o saldo de 160 ha sem nova emissão.','clock','Pausar a execução sem mudar a fase')
          + imsg('Finalizar apontamento do turno','Turno do dia 4 finalizado · 40 ha provisórios seguem para conferência. A ordem permanece Em execução — finalizar o turno nunca conclui a ordem.','check','Finalizar o turno de hoje (não conclui a ordem)')
          + imsg('Concluir execução','Indisponível: faltam 160 ha sem término físico nem dispensa autorizada do saldo. Execute o saldo ou peça a dispensa ao PCP; com o término físico a ordem entra sozinha em Em conferência.','alert','Concluir a execução (exige término físico)'))
      + bloco('Materiais em custódia da equipe','Confira o que foi entregue, consumido e está com a equipe; clique na linha para ver a origem do saldo.',g_mat,
          ilink('Requisitar material','SU-07.dc.html','box','Abrir requisições e entregas em Suprimentos') + ilink('Ver consumo e devoluções','CA-04.dc.html','layers','Abrir as requisições da equipe'))
      + bloco('Plano, versão e fichas','Ajuste produtos e doses só no saldo; as fichas do caldeiro, do operador e do almoxarife derivam da versão vigente.',
          nota(f'Recomendação de origem: <b style="color:{INK};">fungicida 1ª aplicação · protocolo do plano técnico · v2 aprovada</b>.'),
          ajuste + fichas + ilink('Ver recomendação','AG-04.dc.html','leaf','Abrir a recomendação de origem') + ilink('Reprogramar saldo','PL-05.dc.html','calendar','Reprogramar o saldo no PCP')))
    EXTRAJS[0]=(f'const AREA={area}; const DID={json.dumps(DID)}; const FICHAS_V2={json.dumps(FV2,ensure_ascii=False)}; const FICHAS_REV={json.dumps(FREV,ensure_ascii=False)};\n'+APJS)
    prim=f'<a href="MB-03.dc.html" style="{BTN_ST(True)} text-decoration: none; display: inline-flex; align-items: center;">Registrar avanço</a>'
    HEIGHTS37[fname]=1480; PARENT37[fname]='OS.dc.html'  # "Voltar" leva à tela de O.S. do menu, não ao CA-01 oculto
    shell37('CA-01','OS-0421 · Fungicida 1ª aplicação',corpo,fname=fname,crumbs_extra=['OS-0421'],primary_html=prim,
      status=('Em execução · Parcial · dia 4 de 7','yellow'),
      subtitle='350 ha em T1+T2 · 7 turnos (50, 50, 50, 40, 50, 50 e 60 ha) · os mesmos acumulados aparecem na conferência, no app e no Kanban.',
      footer='Finalizar o turno não encerra a ordem; conferir um dia não muda a fase. Ajuste de dose só alcança o saldo: o agrônomo ajusta e libera a v3 só para o saldo, e as fichas do saldo passam à v3. '
             'Término físico do escopo (ou dispensa autorizada do saldo) entra automaticamente em Em conferência; nenhum botão pula etapa.')

# ---------------- CA-01x-os0420 · OS-0420 (DEMO-01 / DEMO-14) ----------------
def _ca01x_0420():
    fname=DET0420; E._reset_screen(fname)
    o=next(x for x in D.OS if x['id']=='OS-0420'); area,real,saldo=o['area'],o['realizado'],o['saldo']
    ins=[('Semente de soja 58 W (resistente)','52 kg/ha',area*52,'kg','plano Soja alta tecnologia · decisão do DIA-007'),
         ('KCl 60 %','120 kg/ha · zonas 140 / 120 / 95',area*120,'kg','REC-014 v2 · IAC Boletim 100 · prescrição por zona'),
         ('TS nematicida (abamectina)','100 mL/100 kg de semente',round(area*52/100*0.1,1),'L','REC-014 v2 · bula AGROFIT')]
    g_ins=grid([dict(k='prod',l='Produto',w=230),dict(k='dose',l='Dose da v2',w=200),dict(k='qtd',l='Quantidade para 100 ha',t='num',a='r'),dict(k='v3',l='Saldo de 70 ha na v3',w=220),dict(k='fonte',l='Fonte',w=260)],
        [dict(id=f'i{i}',v=dict(prod=p,dose=d,qtd=q,fonte=f,v3=('KCl −12 % → 105,6 kg/ha · em vigor no saldo' if 'KCl' in p else 'sem mudança')),s={},
              p=dict(qtd=[Pt.txt(f'{nf(q,1 if u=="L" else 0)} {u}')],v3=([Pt.chip('−12 % · 105,6 kg/ha','green'),Pt.br(),Pt.mut('ajustada por Ana (agrônoma) em 23/09')] if 'KCl' in p else [Pt.mut('sem mudança')])),
              o=[dict(t=f'Recomendação REC-014 v2 · {d}',h='AG-04det.dc.html'),dict(t=f'{nf(area)} ha da 1ª onda da necessidade NEC-028 × dose = {nf(q,1 if u=="L" else 0)} {u}'),dict(t=f'Fonte: {f}')])
         for i,(p,d,q,u,f) in enumerate(ins)],
        edit=dict(m='origin',title='Instrução',fields=[dict(k='prod',l='Produto',ro=True),dict(k='dose',l='Dose da v2',ro=True),dict(k='v3',l='Saldo na v3',ro=True)]),
        search=False,gid='g_ins',total=False)
    aps=[('21/09',1,18,'Conferido','app · sincronizado'),('22/09',2,12,'Provisório','offline · sincronizado 12:10 · turno interrompido 06:40 pela quebra do Trator T1')]
    ac=0; arows=[]
    for dt,d,ha,cf,orig in aps:
        ac+=ha
        arows.append(dict(id=f'a{d}',v=dict(dt=dt,turno=f'Dia {d}',ha=ha,ac=ac,cf=cf,orig=orig),s={},
            p=dict(ac=[Pt.b(f'{ac} / {area} ha')],cf=[Pt.chip(cf,'green' if cf=='Conferido' else 'yellow')],orig=[Pt.mut(orig)])))
    g_ap=grid([dict(k='dt',l='Data'),dict(k='turno',l='Turno'),dict(k='ha',l='Área do dia',t='num',a='r',u='ha'),dict(k='ac',l='Acumulado',t='num',a='r'),
               dict(k='cf',l='Conferência'),dict(k='orig',l='Origem · sincronização',w=380)],arows,
        edit=dict(m='ro',title='Turno',fields=[dict(k='turno',l='Turno',ro=True),dict(k='ha',l='Área do dia',ro=True,u='ha'),dict(k='cf',l='Conferência',ro=True),dict(k='orig',l='Origem',ro=True)]),
        search=False,gid='g_ap0420',total=False)
    rq=REQ['REQ-036']; custo=rq['consumido']*9.50
    g_req=grid([dict(k='req',l='Requisição'),dict(k='item',l='Item',w=200),dict(k='sol',l='Solicitado',t='num',a='r',u='kg'),dict(k='ent',l='Entregue',t='num',a='r',u='kg'),
                dict(k='cons',l='Consumido',t='num',a='r',u='kg'),dict(k='cust',l='Em custódia',t='num',a='r',u='kg'),dict(k='custo',l='Custo apontado',t='num',a='r',pre='R$ ')],
        [dict(id='q1',v=dict(req=rq['id'],item=rq['item'],sol=rq['solicitado'],ent=rq['entregue'],cons=rq['consumido'],cust=rq['custodia'],custo=custo),s={},
              p=dict(custo=[Pt.txt('R$ '+nf(custo)),Pt.br(),Pt.mut(f'R$ {nf(custo/real)}/ha realizado')]),
              o=[dict(t=f'{rq["id"]} · {nf(rq["solicitado"])} kg para 100 ha (52 kg/ha)',h='SU-07.dc.html'),
                 dict(t=f'Entregue {nf(rq["entregue"])} kg = {real} ha × 52 kg/ha · o restante só sai com o impedimento resolvido'),
                 dict(t=f'Consumo apontado {nf(rq["consumido"])} kg (18 ha + 12 ha) × R$ 9,50/kg = R$ {nf(custo)}',h='CA-02.dc.html')])],
        edit=dict(m='origin',title='Requisição',fields=[dict(k='req',l='Requisição',ro=True),dict(k='item',l='Item',ro=True),dict(k='cons',l='Consumido',ro=True,u='kg')]),
        search=False,gid='g_req0420',total=False)
    corpo=(
      continuity('REC-014 v2 · necessidade NEC-028','Em execução · Impedida · 30/100 ha','reparo da OM-0233 ou substituto (Trator 02 a partir de 24/09)','Acompanhar OM-0233')
      + alerta(f'{chip("Impedida · ativo bloqueado","red")} &nbsp;Saldo de {saldo} ha parado pelo Trator T1 (OM-0233) · substituto Trator 02 a partir de 24/09. '
               f'O saldo segue na v3 (KCl −12 %), ajustada por Ana (agrônoma) em 23/09; os {real} ha realizados ficam preservados na v2.',tone='red')
      + stepper([('A liberar','done'),('Liberadas','done'),('Em execução','now'),('Em conferência','todo'),('Encerradas','todo')],'')
      + kpis([('AUTORIZADO',f'{area} ha','v2 no realizado · v3 no saldo'),('REALIZADO',f'{real} ha','18 conf. + 12 prov.'),('SALDO',f'{saldo} ha','parado · Trator T1'),('IMPEDIMENTO','OM-0233','Trator T1 bloqueado')])
      + bloco('Instrução herdada da REC-014 v2','Confira produto, dose e janela que a ordem herdou da recomendação; clique no produto para ver a origem.',
          g_ins+nota(f'Janela da recomendação 20/09 a 05/10 · janela da ordem 22–28/09 · T4, 1ª onda de {area} ha dos 204 ha da necessidade NEC-028.'),
          ilink('Ver recomendação','AG-04det.dc.html','leaf','Abrir a REC-014 com versões e memória de cálculo'))
      + bloco('Apontamentos','Confira os turnos já apontados; a correção com histórico é feita na conferência.',g_ap,
          ilink('Conferir apontamentos','CA-02.dc.html','check','Abrir a fila de conferência'))
      + bloco('Impedimento e substituto','Acompanhe o reparo do Trator T1 ou confirme o substituto no PCP para retomar o saldo.',
          nota(f'OC-114 · pressão hidráulica baixa no Trator T1 em 22/09 06:40 → <b style="color:{INK};">OM-0233 em execução</b> (Zé · mecânico). '
               f'Substituto proposto: <b style="color:{INK};">{D.OM["substituto"]}</b>, apto e livre a partir de 24/09 06:00 — elegível só após confirmação do PCP.'),
          ilink('Ver ocorrência','CA-03det.dc.html','alert','Abrir a ocorrência OC-114') + ilink('Reprogramar saldo','PL-05.dc.html','calendar','Confirmar substituto e reprogramar o saldo no PCP'),tone='red')
      + bloco('Ajuste do saldo · v3','Confira o ajuste que Ana (agrônoma) fez no saldo; o realizado continua na v2.',
          nota(f'<b style="color:{INK};">v3 · KCl −12 %</b> no saldo de {saldo} ha (105,6 kg/ha)'   # TXT-02: o resto vai para a dica ⓘ
               + E.dica_i('Sobre a v3',f'v3 em vigor desde 23/09, ajustada por Ana (agrônoma). A v2 continua valendo apenas para os {real} ha já realizados.')),
          imsg('Ver fichas',f'Fichas do saldo de {saldo} ha na v3 (KCl 105,6 kg/ha) · as fichas dos {real} ha realizados permanecem no histórico da v2.','doc','Consultar as fichas do caldeiro, do operador e do almoxarife'))
      + bloco('Materiais e custo','Confira a requisição da ordem e o custo dos hectares realizados; clique na linha para ver a origem.',g_req))
    HEIGHTS37[fname]=1900; PARENT37[fname]='OS.dc.html'  # "Voltar" leva à tela de O.S. do menu, não ao CA-01 oculto
    shell37('CA-01','OS-0420 · Plantio Soja 58 W',corpo,fname=fname,crumbs_extra=['OS-0420'],
      primary='Acompanhar OM-0233',primary_href='MA.dc.html#om=OM-0233',
      status=('Em execução · Impedida','red'),
      subtitle=f'{area} ha no T4 · {real} ha realizados · saldo de {saldo} ha parado até o ativo ser liberado ou substituído.',
      footer='Instrução, versão e realizado vêm da mesma recomendação; o ajuste alcança só o saldo e nunca reescreve o realizado. Impedimento é selo: a ordem segue Em execução e nenhum botão pula etapa.')

# ---------------- CA-02 · Apontamentos e conferência ----------------
FILAJS=r'''
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_fila'||!r) return;
    r.p.real=[{k:'txt',t:Number(r.v.real).toLocaleString('pt-BR')+' ha'},{k:'br'},{k:'mut',t:'corrigido · original na trilha'}];
    r.p.horas=[{k:'txt',t:Number(r.v.horas).toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1})+' h'}];
    g2set(self,'g_fila',{rows}); self.setState({g2toast:'Corrigido com histórico · '+r.v.ap+': nova versão do apontamento; o valor original permanece na trilha e a etapa da ordem não muda.'}); };
}
'''
def _ca02():
    fname='CA-02.dc.html'; E._reset_screen(fname)
    def row(i,ap,det,sub,eq,real,acum,horas,cons,orig,cf,cfc,acao):
        return dict(id=f'f{i}',v=dict(ap=ap,eq=eq,real=real,horas=horas,cons=' '.join(p['t'] for p in cons),orig=' '.join(p['t'] for p in orig),cf=cf,motivo=''),
            s=dict(ap=f'{ap} {sub}'),
            p=dict(ap=[Pt.link(ap,det) if det else Pt.b(ap),Pt.br(),Pt.mut(sub)],real=[Pt.txt(f'{nf(real)} ha'),Pt.br(),Pt.mut(acum)],horas=[Pt.txt(f'{nf(horas,1)} h')] if horas is not None else [Pt.mut('—')],
                   eq=_eqp(eq),cons=cons,orig=orig,cf=[Pt.chip(cf,cfc),Pt.br()]+acao))
    rows=[
     row(1,'OS-0421 · v2','CA-01det.dc.html','Dia 4 · 23/09 · T1','Marcos · PJ-3030 + Trator 03',40,'150 conf. + 40 prov. · saldo 160 ha',7.2,
         [Pt.txt('Fungicida A 20 L'),Pt.br(),Pt.mut('sem sobras')],[Pt.mut('app · sincronizado 17:40')],'A conferir','yellow',
         [Pt.act('Conferir','Conferido o dia 4 · 40 ha confirmados (190/350) · o consumo de 20 L já baixado no apontamento não é repetido. A ordem segue Em execução — conferir um dia não conclui a ordem de 7 dias.')]),
     row(2,'OS-0420 · v2',DET0420,'Dia 2 · 22/09 · T4','Carlos · PD-12 + Trator T1',12,'18 conf. + 12 prov. · saldo 70 ha parado',3.1,
         [Pt.txt('Semente 58 W 624 kg'),Pt.br(),Pt.chip('horas acima do previsto · 1,8 h','yellow')],[Pt.mut('offline · sincronizado 12:10 · sem conflito'),Pt.br(),Pt.mut('turno parado pela quebra do Trator T1')],'A conferir','yellow',
         [Pt.act('Conferir','Conferido · 12 ha confirmados (30/100) · horas acima do previsto registradas como fato. O selo Impedida permanece — conferência não muda impedimento nem etapa.')]),
     row(3,'OS-0421 · v2','CA-01det.dc.html','Dia 3 · 22/09 · T1','Marcos · PJ-3030 + Trator 03',50,'150 conf. · saldo 160 ha',8.4,
         [Pt.txt('Fungicida A 25 L')],[Pt.mut('app · sincronizado')],'Conferido','green',[Pt.link('Ver histórico ›','CA-01det.dc.html')]),
     row(4,'OS-0417 · v1',None,'Final · 21/09 · P1','Paula · Distribuidor DA-08',95,'95 conf. · saldo 0 ha',None,
         [Pt.txt('MAP 100 sc entregues · 70 consumidos'),Pt.br(),Pt.chip('10 sc com Paula a devolver','yellow')],[Pt.mut('almoxarifado · confirmado')],'Divergência de sobras','yellow',
         [Pt.link('Ver custódia ›','CA-04.dc.html')]),
    ]
    g_fila=grid([dict(k='ap',l='Apontamento',w=130),dict(k='eq',l='Equipe · conjunto',w=130),dict(k='real',l='Realizado · acumulado',t='num',w=150),dict(k='horas',l='Horas',t='num',a='r',d=1,u='h'),
                 dict(k='cons',l='Consumos e sobras',w=190),dict(k='orig',l='Origem · sincronização',w=165),dict(k='cf',l='Conferência · ação',w=170)],
        rows,edit=dict(m='form',title='Corrigir apontamento',sub='Corrija realizado e horas informando o motivo. A correção gera nova versão; o valor original permanece na trilha e a etapa da ordem não muda.',
            fields=[dict(k='ap',l='Apontamento',ro=True),dict(k='cf',l='Conferência',ro=True),
                    dict(k='real',l='Realizado do dia',t='num',req=True,min=0,max=200,u='ha'),dict(k='horas',l='Horas de máquina',t='num',min=0,max=24,u='h'),
                    dict(k='motivo',l='Motivo da correção',t='area',req=True,help='Ex.: horímetro lido no fim do turno.')]),
        gid='g_fila',total=False)
    proj=[('23/09 06:00','Água aplicada antes da reclassificação · 6,7 mm no Pivô 1','fica no balanço hídrico; não é reapontada na fertirrigação','João (irrigante) · balanço hídrico'),
          ('liberação','Ana (agrônoma) libera a OS-0418 (v2, com ajuste opcional)','passa a Liberadas; a REQ-038 fica disponível para entrega','Ana (agrônoma)'),
          ('entrega','REQ-038 · Ureia 45 % 1.140 kg com conferência de carga','sai do físico do depósito e passa à custódia de João','Rui (almoxarife) → João'),
          ('início','Início da fertirrigação no Pivô 1','Em execução: a lâmina já aplicada é descontada, sem duplicar apontamentos','João'),
          ('turnos','Consumo apontado 1.100 kg em 95 ha','uma única baixa no apontamento; a conferência não repete a baixa','João · conferência de Paula'),
          ('devolução','40 kg declarados · 40 kg medidos e recebidos','custódia zero','João → Rui (almoxarife)'),
          ('conciliação','1.140 entregues = 1.100 consumidos + 40 devolvidos','Em conferência · pode encerrar','Paula'),
          ('encerramento','Encerrar OS-0418','manual, após a conciliação · sem encerramento automático pela água','PCP')]
    g_proj=grid([dict(k='q',l='Quando',w=130),dict(k='ev',l='Evento',w=320),dict(k='ef',l='Efeito',w=360),dict(k='quem',l='Quem',w=200)],
        [dict(id=f'p{i}',v=dict(q=q,ev=ev,ef=ef,quem=qm),s={},p=dict(ef=[Pt.chip('sem encerramento automático','gray'),Pt.br(),Pt.mut(ef)] if i==len(proj)-1 else [Pt.txt(ef)]))
         for i,(q,ev,ef,qm) in enumerate(proj)],
        edit=dict(m='ro',title='Passo do roteiro',fields=[dict(k='q',l='Quando',ro=True),dict(k='ev',l='Evento',ro=True),dict(k='ef',l='Efeito',ro=True),dict(k='quem',l='Quem',ro=True)]),
        search=False,gid='g_proj',total=False,headtools=False)
    reabrir=idrawer('Reabrir saldo da OS-0417',dict(title='Reabrir saldo para execução',sub='Volta a Em execução preservando o término anterior e a trilha; a instrução do saldo é revalidada pelo responsável competente.',
             fields=[('Ordem','OS-0417 · Adubação de cobertura'),('Motivo','Falha de aplicação em 5 ha detectada na conferência'),('Saldo a reabrir','5 ha'),('Programação','24/09 · turno da manhã'),('Responsável','PCP · Ana')],
             confirm='Reabrir saldo',done='Reaberta · Em execução'),'calendar','Reabrir saldo de ordem em conferência (conferente ou PCP)')
    corpo=(
      kpis([('PROVISÓRIOS','52 ha','aguardam conferência'),('FORA DA TOLERÂNCIA','1','horas · OS-0420'),('SOBRAS A RECEBER','10 sc','OS-0417 · com Paula')])
      + bloco('Fila de conferência diária','Confira previsto contra observado por turno; clique no apontamento para corrigir com histórico.',g_fila,
          imsg('Devolver para esclarecimento','Apontamento do dia 2 da OS-0420 devolvido a Carlos com a pergunta registrada — o fato permanece registrado, nada é apagado.','alert','Devolver o apontamento ao executor com uma pergunta'))
      + bloco('Reabrir saldo para execução','Reabra o saldo quando a conferência encontrar trabalho físico adicional (conferente ou PCP com permissão).',
          '',reabrir,tone='yellow')
      + bloco('Encerramento','Encerre a ordem só com término físico e todas as condições satisfeitas.',
          '',
          imsg('Encerrar OS-0417','Indisponível: 10 sc de MAP 11-52 sob custódia de Paula (equipe de campo) · prazo 24/09. Rui recebe a devolução no almoxarifado; ou documente a destinação competente para encerrar.','check','Encerrar a ordem (exige custódia zero e conferência concluída)'))
      + bloco('Roteiro da OS-0418 após a liberação','Confira como a fertirrigação será liberada, entregue, apontada e conciliada; cenário projetado, a ordem atual segue A liberar.',g_proj,
          ilink('Liberar OS-0418','OS.dc.html#OS-0418','check','Abrir a OS-0418 para o agrônomo liberar (pode ajustar)'),tone='yellow'))
    EXTRAJS[0]=FILAJS
    prim=imsg('Conferir 2 apontamentos','Conferidos 2 de 2 · OS-0421 dia 4: 40 ha confirmados (190/350) · OS-0420 dia 2: 12 ha confirmados (30/100), horas acima do previsto registradas. Nenhuma ordem muda de etapa; o selo Impedida da OS-0420 permanece.',
              'check','Conferir os apontamentos provisórios da fila',primary=True,small=False)
    HEIGHTS37[fname]=1560
    shell37('CA-02','Apontamentos e conferência',corpo,primary_html=prim,
      status=('2 a conferir · 1 divergência','yellow'),
      subtitle='Conferência diária confirma provisórios sem mudar a fase da ordem; consumo recebe um único evento de efeito.',
      footer='Fato permanece registrável fora da tolerância. Conferir um dia não conclui a ordem de vários dias; conferência posterior não repete baixa. '
             'Reabrir saldo: se a liberação não estiver mais vigente, o saldo reaberto recebe o selo Pausada até renovar as condições; correção só documental permanece Em conferência, sem reabrir período contábil nem reescrever fatos. '
             'Concluir execução não encerra a ordem com custódia, divergência ou conferência pendente.')

# ---------------- CA-03 · Ocorrências ----------------
OCJS=r'''
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_oc'||!r) return; let novo=false;
    if(!r.v.oc){ const n=116+rows.filter(x=>String(x.id).indexOf('n')===0).length; r.v.oc='OC-'+n; novo=true; }
    r.p.oc=[{k:'b',t:r.v.oc},{k:'br'},{k:'mut',t:r.v.tipo||''}]; r.s.oc=r.v.oc+' '+(r.v.tipo||'');
    r.p.local=[{k:'txt',t:r.v.local||''},{k:'br'},{k:'mut',t:r.v.inst||''}]; r.s.local=(r.v.local||'')+' '+(r.v.inst||'');
    if(novo){ r.p.prox=[{k:'mut',t:'Encaminhada · '+r.v.dest}]; r.s.prox='Encaminhada'; }
    g2set(self,'g_oc',{rows});
    self.setState({g2toast:novo?(r.v.oc+' registrada · encaminhada a '+r.v.dest+' com responsável.'):('Salvo · '+r.v.oc+' atualizada; o tratamento continua no destino.')}); };
}
'''
def _ca03():
    fname='CA-03.dc.html'; E._reset_screen(fname)
    DEST=['Manutenção · Zé','Agronomia · Ana','PCP · Ana','Irrigação · João','Almoxarifado · Rui']
    TIPOS=['Quebra de máquina','Praga acima do NC','Clima interrompeu','Vazamento no pivô','Falha de aplicação','Acidente ou segurança']
    GRAV={'Grave':'red','Atenção':'yellow','Moderada':'yellow','Leve':'gray'}
    occ=[('OC-114','Quebra de máquina','T4 · OS-0420','22/09 06:40','Pressão hidráulica baixa no Trator T1; plantio parado','Grave','Foto + leitura do painel','Manutenção · Zé',
          [Pt.link('Abrir ocorrência ›','CA-03det.dc.html'),Pt.br(),Pt.mut('OM-0233 já aberta')],False),
         ('OC-115','Praga acima do NC','T2 · bordadura leste','23/09 09:15','Percevejo 3,2/pano nos pontos 4, 5 e 10 da rota','Atenção','Rota W · 3 panos','Agronomia · Ana',
          [Pt.link('Encaminhar à agronomia ›','AG-03.dc.html')],False),
         ('OC-116','Clima interrompeu','T1 · OS-0421','23/09 14:20','Chuva encerrou o turno com 40 ha aplicados','Moderada','Sem evidência','PCP · Ana',
          [Pt.link('Reprogramar saldo ›','PL-05.dc.html')],False),
         ('OC-111','Vazamento no pivô','P2 · Pivô 2','21/09 05:10','Vazamento na torre 3; reparo executado e documentado','Moderada','Foto do reparo','Irrigação · João',
          [Pt.link('Ver tratamento ›','IR-03.dc.html'),Pt.br(),Pt.mut('encerrada')],True)]
    rows=[dict(id=oc,ro=ro,v=dict(oc=oc,tipo=tp,local=lc,inst=it,relato=rl,grav=gv,evid=ev,dest=ds),s=dict(oc=f'{oc} {tp}',local=f'{lc} {it}',prox=' '.join(p['t'] for p in px)),
               p=dict(oc=[Pt.b(oc),Pt.br(),Pt.mut(tp)],local=[Pt.txt(lc),Pt.br(),Pt.mut(it)],grav=[Pt.chip(gv,GRAV[gv])],prox=px)) for oc,tp,lc,it,rl,gv,ev,ds,px,ro in occ]
    g_oc=grid([dict(k='oc',l='Ocorrência',w=130),dict(k='local',l='Local · instante',w=130),dict(k='relato',l='Relato',w=210),
               dict(k='grav',l='Gravidade',chips=GRAV),dict(k='evid',l='Evidência',w=110),dict(k='dest',l='Destino · responsável',w=120),dict(k='prox',l='Próxima ação',w=160)],
        rows,edit=dict(m='form',title='Ocorrência',newTitle='Registrar ocorrência',sub='Registre ou ajuste o relato, a gravidade e o destino. O tratamento acontece no módulo de destino, nunca em cópia paralela.',
            fields=[dict(k='tipo',l='Tipo',t='sel',opts=TIPOS,req=True,**{'def':'Quebra de máquina'}),dict(k='local',l='Local',t='txt',req=True,help='Talhão, ordem, lote ou ativo. Ex.: T1 · OS-0421'),
                    dict(k='inst',l='Instante',t='txt',req=True,**{'def':'23/09 15:05'}),dict(k='relato',l='Relato',t='area',req=True),
                    dict(k='grav',l='Gravidade',t='sel',opts=list(GRAV),req=True,**{'def':'Moderada'}),
                    dict(k='evid',l='Evidência',t='sel',opts=['Foto','Foto + leitura do painel','Rota W · 3 panos','Foto do reparo','Sem evidência'],**{'def':'Foto'}),
                    dict(k='dest',l='Destino · responsável',t='sel',opts=DEST,req=True,**{'def':'Manutenção · Zé'})]),
        sel=True,gid='g_oc',total=False,
        bulk=imsg('Encerrar tratamento','Resultado por item · OC-116 encerrada: saldo reprogramado para 24/09 (destinação documentada) · OC-114 recusada: a OM-0233 ainda está em execução — conclua o reparo ou documente a destinação · OC-115 recusada: aguarda decisão da agronomia.',
                  'check','Encerrar o tratamento das ocorrências selecionadas (resultado por item)'))
    corpo=bloco('Ocorrências vinculadas','Clique numa ocorrência para ajustar relato, gravidade e destino; use a próxima ação para tratar no módulo de destino.',g_oc)
    EXTRAJS[0]=OCJS
    prim=f'<button type="button" onClick="{H("g_oc_new")}" title="Registrar ocorrência (também no app, inclusive sem sinal)" style="{BTN_ST(True)}">Registrar ocorrência</button>'
    HEIGHTS37[fname]=880
    shell37('CA-03','Ocorrências',corpo,primary_html=prim,
      status=('3 em tratamento · 1 grave','red'),
      subtitle='Qualquer papel registra no escopo; o tratamento acontece no módulo de destino, nunca em cópia paralela.',
      footer='Encerrar exige resolução do caso ou destinação documentada. Pedir manutenção de novo pela mesma ocorrência reaproveita o caso aberto.')

# ---------------- CA-03det · OC-114 ----------------
def _ca03det():
    fname='CA-03det.dc.html'; E._reset_screen(fname)
    vinc=[('OS-0420',DET0420,'Plantio Soja 58 W','Ordem de campo',[Pt.chip('Em execução','green'),Pt.chip('Impedida','red')],'30/100 ha · saldo de 70 ha preservado e parado'),
          ('Trator T1','MA.dc.html#ativo=a01','JD 6M 155','Ativo',[Pt.chip('Bloqueado','red')],'não pode ser alocado até a OM-0233 liberar'),
          ('OM-0233','MA.dc.html#om=OM-0233','corretiva hidráulica','Manutenção',[Pt.chip('Em execução','green')],'caso único · 2 registros somados'),
          (D.OM['substituto'],'PL-05.dc.html','substituto proposto','Ativo substituto',[Pt.chip('Apto','green'),Pt.chip('Livre a partir de 24/09 06:00','yellow')],'elegível para a OS-0420 só após confirmação do PCP')]
    g_v=grid([dict(k='reg',l='Registro',w=220),dict(k='tipo',l='Tipo'),dict(k='est',l='Estado',w=240),dict(k='ef',l='Efeito',w=340)],
        [dict(id=f'v{i}',v=dict(reg=f'{r} · {d}',tipo=t,est=' '.join(p['t'] for p in e),ef=ef),s={},p=dict(reg=[Pt.link(r,h),Pt.br(),Pt.mut(d)],est=e))
         for i,(r,h,d,t,e,ef) in enumerate(vinc)],
        edit=dict(m='ro',title='Vínculo',fields=[dict(k='reg',l='Registro',ro=True),dict(k='tipo',l='Tipo',ro=True),dict(k='est',l='Estado',ro=True),dict(k='ef',l='Efeito',ro=True)]),
        search=False,gid='g_vinc',total=False)
    trilha=[('22/09 06:40','Ocorrência registrada no app, sem sinal','Carlos · operador','vinculada a T4, OS-0420 e Trator T1'),
            ('22/09 06:52','Sincronizada sem conflito','app','—'),
            ('22/09 07:05','Encaminhada à Manutenção','Ana · PCP','OS-0420 recebe o selo Impedida'),
            ('22/09 07:10','Manutenção aberta · OM-0233','Zé · mecânico','Trator T1 bloqueado para uso'),
            ('22/09 09:30','Alerta repetido de pressão baixa','telemetria','somado ao mesmo caso'),
            ('23/09 06:05','Novo pedido de manutenção pela ocorrência','Carlos · operador','reaproveitou a OM-0233 · nenhum caso duplicado')]
    g_t=grid([dict(k='q',l='Instante'),dict(k='ev',l='Evento',w=320),dict(k='quem',l='Quem'),dict(k='ef',l='Efeito',w=320)],
        [dict(id=f't{i}',v=dict(q=q,ev=ev,quem=qm,ef=ef),s={},p={}) for i,(q,ev,qm,ef) in enumerate(trilha)],
        edit=dict(m='ro',title='Evento',fields=[dict(k='q',l='Instante',ro=True),dict(k='ev',l='Evento',ro=True),dict(k='quem',l='Quem',ro=True),dict(k='ef',l='Efeito',ro=True)]),
        search=False,gid='g_trilha',total=False)
    corpo=(
      continuity('Apontamento de Carlos · T4 · 22/09','Em tratamento · Manutenção','reparo da OM-0233 e liberação do Trator T1','Acompanhar OM-0233')
      + bloco('Relato','Confira o que foi observado, onde e quando; o relato vem do app de campo.',
          _kv([('Tipo','Quebra de máquina'),('Local','T4 · OS-0420 · Trator T1'),('Instante','22/09/2026 06:40'),('Gravidade',chip('Grave','red')),
               ('Relato','Pressão hidráulica baixa no Trator T1; plantio parado após 12 ha do turno'),('Evidência','foto + leitura do painel (2)'),
               ('Destino','Manutenção · OM-0233'),('Responsável','Zé · mecânico')]),
          imsg('Abrir manutenção','A OM-0233 já está aberta para esta ocorrência — nada foi duplicado; o pedido foi somado ao caso existente.','wrench','Abrir manutenção (reaproveita o caso aberto)')
          + imsg('Encerrar tratamento','Indisponível: a OM-0233 ainda está em execução. Encerre depois do reparo concluído ou documente a destinação competente.','check','Encerrar o tratamento (exige resolução ou destinação)'),tone='red')
      + bloco('Registros ligados','Abra cada registro pelo link; o contexto e o saldo são preservados.',g_v)
      + bloco('Trilha','Confira quem fez cada passo e o efeito; nada é apagado.',g_t))
    HEIGHTS37[fname]=1260; PARENT37[fname]='CA-03.dc.html'
    shell37('CA-03','OC-114 · Quebra do Trator T1',corpo,fname=fname,crumbs_extra=['OC-114'],
      primary='Acompanhar OM-0233',primary_href='MA.dc.html#om=OM-0233',
      status=('Em tratamento · Grave','red'),
      subtitle='Ocorrência do plantio no T4 · a ordem OS-0420 segue impedida até o ativo ser liberado ou substituído.',
      footer='Encerrar a ocorrência ou a ordem não libera o Trator T1: o desbloqueio vem só da OM-0233 concluída e liberada.')

# ---------------- CA-04 · Minhas requisições ----------------
def _ca04():
    fname='CA-04.dc.html'; E._reset_screen(fname)
    OSX={o['id']:o for o in D.OS}
    RESP={'OS-0417':'Paula (equipe de campo)','OS-0421':'Marcos (equipe de campo)','OS-0420':'Carlos (equipe de campo)','OS-0418':'João (irrigação)'}
    LOTE={'REQ-031':'lote M26-07','REQ-035':'lote F26-02','REQ-036':'lote S58-0801','REQ-038':'—'}
    ACAO={'REQ-031':[Pt.cta('Devolver saldo','SU-07det.dc.html',u=True)],
          'REQ-035':[Pt.link('Apontar uso ›','CA-02.dc.html')],
          'REQ-036':[Pt.link('Ver impedimento ›',DET0420)],
          'REQ-038':[Pt.act('Confirmar recebimento','Indisponível: nada foi entregue — a OS-0418 aguarda a liberação pelo agrônomo; a REQ-038 só é separada depois dela. Confirme quando os 1.140 kg chegarem à equipe; só então a custódia passa para vocês.')]}
    rows=[]
    for r in D2.REQUISICOES:
        u=r['un']; uu='sc' if u.startswith('sc') else u
        q=lambda n: [Pt.txt(f'{nf(n)} {uu}')]
        o=OSX.get(r['os'],{})
        dev=(f'{nf(r["dev_declarada"])} · {nf(r["dev_recebida"])} {uu}' if r['dev_declarada'] or r['dev_recebida'] else '—')
        cust=([Pt.b(f'{nf(r["custodia"])} {uu}'),Pt.br(),Pt.chip('com '+RESP[r['os']].split(' ')[0],'yellow')] if r['custodia'] else [Pt.txt(f'0 {uu}'),Pt.br(),Pt.mut('aguardando entrega' if not r['entregue'] else 'sem saldo')])
        orig=[dict(t=f'{r["id"]} · {nf(r["solicitado"])} {uu} de {r["item"]} para a {r["os"]}',h='SU-07.dc.html'),
              dict(t=f'Entregue pelo almoxarifado: {nf(r["entregue"])} {uu}' + (f' · faltam {nf(r["solicitado"]-r["entregue"])} {uu}' if r['solicitado']>r['entregue'] else '')),
              dict(t=f'Consumo apontado na conferência: {nf(r["consumido"])} {uu}',h='CA-02.dc.html'),
              dict(t=f'Devolução declarada {nf(r["dev_declarada"])} · recebida {nf(r["dev_recebida"])} {uu} (só a recebida volta ao estoque)'),
              dict(t=f'Em custódia = {nf(r["entregue"])} − {nf(r["consumido"])} − {nf(r["dev_recebida"])} = {nf(r["custodia"])} {uu} · {RESP[r["os"]]}')]
        rows.append(dict(id=r['id'],v=dict(req=r['id'],os=r['os'],item=r['item'],sol=r['solicitado'],ent=r['entregue'],cons=r['consumido'],dev=dev,cust=r['custodia'],est=r['estado']),
            s=dict(req=f'{r["id"]} {r["os"]} {o.get("tipo","")} {r["estado"]}',acao=' '.join(p['t'] for p in ACAO[r['id']])),
            p=dict(req=[Pt.b(r['id']),Pt.txt(' · '),Pt.link(r['os'],DETALHE[r['os']]) if r['os'] in DETALHE else Pt.txt(r['os']),Pt.br(),Pt.mut(r['estado'])],
                   item=[Pt.txt(r['item']),Pt.br(),Pt.mut(LOTE[r['id']])],sol=q(r['solicitado']),ent=q(r['entregue']),cons=q(r['consumido']),cust=cust,acao=ACAO[r['id']]),
            o=orig))
    g_req=grid([dict(k='req',l='Requisição · ordem',w=150),dict(k='item',l='Item · lote',w=135),dict(k='sol',l='Solicitado',t='num',a='r'),dict(k='ent',l='Entregue',t='num',a='r'),
                dict(k='cons',l='Consumido',t='num',a='r'),dict(k='dev',l='Devolvido decl. · receb.',a='r',w=100),dict(k='cust',l='Em custódia',t='num',a='r'),dict(k='acao',l='Próxima ação',w=150)],
        rows,edit=dict(m='origin',title='Saldo da requisição',fields=[dict(k='req',l='Requisição',ro=True),dict(k='os',l='Ordem',ro=True),dict(k='item',l='Item',ro=True),dict(k='est',l='Situação da ordem',ro=True)]),
        gid='g_req',total=False)
    R=REQ['REQ-031']
    corpo=(
      bloco('Requisições e custódia da equipe','Confira entregue, consumido e em custódia por ordem; clique na linha para ver a origem do saldo.',g_req,
          ilink('Ver em Suprimentos','SU-07.dc.html','box','Abrir o mesmo registro em Requisições e entregas'))
      + bloco('Encerramento bloqueado pela custódia','Devolva as sobras da OS-0417 para liberar o encerramento.',
          nota(f'Balanço da REQ-031: {R["entregue"]} sc entregues − {R["consumido"]} consumidos − {R["dev_recebida"]} recebidos = <b style="color:{INK};">{R["custodia"]} sc com Paula (equipe de campo)</b>, prazo 24/09; Rui recebe no almoxarifado.'),   # é o dado da trava: fica à vista (TEXTO-2, textos_soltos F)
          imsg('Encerrar OS-0417',f'Indisponível: {R["custodia"]} sc de MAP 11-52 sob custódia de Paula (equipe de campo) · prazo 24/09. Declarar devolução não aumenta o utilizável — Rui recebe as {R["custodia"]} sc no almoxarifado, ou documente a destinação competente para liberar o encerramento.',
               'check','Encerrar a ordem (exige custódia zero)'),tone='yellow'))
    prim=idrawer('Solicitar material da ordem',dict(title='Solicitar material da ordem',sub='A requisição nasce da ordem liberada; itens e doses vêm da versão vigente.',
             fields=[('Ordem','OS-0421 · Fungicida 1ª aplicação · v2'),('Item','Fungicida A'),('Quantidade',''),('Necessário em','24/09/2026')],
             confirm='Solicitar material',done='Requisitada · em separação'),'box','Solicitar material para uma ordem liberada',primary=True,small=False)
    HEIGHTS37[fname]=900
    shell37('CA-04','Minhas requisições',corpo,primary_html=prim,
      status=('10 sc e 65 L em custódia','yellow'),
      subtitle='Visão filtrada de Requisições e entregas (Suprimentos) com a custódia da equipe e o saldo por ordem.',
      footer='É o mesmo registro de Suprimentos e do Estoque: consumo é apontado na conferência e devolução é recebida no almoxarifado. '
             'Declarar o retorno não aumenta o estoque utilizável: só a quantidade medida e recebida entra no local e na condição registrados. Sem ajuste automático pela diferença.')

def build():
    _ca01(); _ca01det(); _ca01x_0420(); _ca02(); _ca03(); _ca03det(); _ca04()
