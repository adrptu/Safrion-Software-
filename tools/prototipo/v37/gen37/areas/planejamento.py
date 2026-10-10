# -*- coding: utf-8 -*-
"""Área Planejamento (módulo OCULTO do menu, preservado) — PL-01 Safras · PL-02 Plano operacional (+det T1-A) · PL-03 Capacidade ·
PL-04 Programação integrada (janela 8.6) · PL-05 Impedimentos (+det DEMO-17) · PL-06 Parcelas e escalonamento (cap. 43).
Módulo não sequencial: sem faixa de etapas. Edição pela linha (motor G2) em todas as tabelas de registros.

observacoes (dados locais coerentes com dados.py / dados2.py / processo_os.py / suprimentos.py / maquinas.py):
- Safras, cultivos, planos, doses e datas vêm de dados2 (SAFRAS, CULTIVOS['S2627'], PLANO['SOJA-AT'], data_atividade).
  Metas: T1-A 64 sc/ha e T1-B 62 sc/ha (dados2); colheita = plantio + 118 dias (atividade a8 do SOJA-AT) → T1-A 10/02, T1-B 20/02.
- DEMO-15/17: OS-0422 e OS-0423 são ordens de água (processo_os.EXTRA_OS / irrigacao). A dessecação do T1-A passa a OS-0430 e o
  plantio do T2 (DEMO-17) passa a OS-0431 (OS-0424/0425 já usadas em Suprimentos/Estoque; OS-0426+ reservadas a novas ordens).
  maquinas.py ainda cita "OS-0423 · plantio T2" → reconciliar para OS-0431.
- DEMO-01: necessidade NEC-028 (REC-014 v2 · plantio T4 · 1ª onda 100 ha de 204 ha) convertida na OS-0420 (30 ha realizados · saldo 70 ha);
  demais necessidades renumeradas no mesmo padrão (NEC-019, NEC-026, NEC-031..034) — antes N-11xx/N-12xx.
- DEMO-02/09: PC-088 em toneladas (100 t · 60 recebidas = 50 aptas + 10 em quarentena · 40 a entregar em 02/10) com origem NEC-028 e
  cobertura da soja (como SU-05). N-1190 (agora NEC-019, adubação pós-colheita do C1) saiu da fila de faltas: aguarda "Decidir pendência".
- DEMO-04: Trator 02 · MF 7719 antes da confirmação do PCP = "Proposto · OS-0420 saldo 70 ha · aguarda PCP" (mesmo rótulo de maquinas.py).
- T4: dados2 prevê plantio 20/10, mas a 1ª onda (100 ha) já está em plantio pela OS-0420 (dados.py) — mostrado como "1ª onda em curso".
- PL-03: carga/capacidade e cenários continuam locais (não derivam de dados2.RECURSOS); OM-0234 = preventiva 250 h do MF 7719 em 28/09 (maquinas.py).
  Sem entrada pelas telas (verificação SAF-C02): "Ver capacidade" no PL-02, no PL-04 e no PL-05 abre a etapa 3 do Planejar safra, a única conta
  de capacidade (capCalc); os números fixos do PL-03 contradiziam a etapa 3. Derivar o PL-03 da etapa 3 ou removê-lo é tarefa própria.
"""
import json, re
from engine import (grid,table,section,kpis,chip,btn,tag,icon,esc,seg,msgbtn,drawer_button,toolrow,prazo,Pt,
                    INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,RED,GRAYS,SH,DISP,BTN_ST,EXTRAJS)
import engine as E
from ui37 import shell37, continuity, HEIGHTS37, PARENT37, etapa, selo
import dados as D
import dados2 as D2

H=lambda s: '{{'+s+'}}'

# ---------------- dados locais coerentes ----------------
CULT={c['local']:c for c in D2.CULTIVOS['S2627']}
T1A, T1B = CULT['T1-A'], CULT['T1-B']
SOJA=D2.PLANO['SOJA-AT']; CICLO=next(a['g']['dias'] for a in SOJA['atividades'] if a['op'].startswith('Colheita'))   # 118 d
OS421=next(o for o in D.OS if o['id']=='OS-0421'); OS420=next(o for o in D.OS if o['id']=='OS-0420')
PC88=next(p for p in D2.PEDIDOS if p['id']=='PC-088')
t=lambda kg: f'{kg/1000:,.0f}'.replace(',', '.')+' t'
OS_DES=dict(id='OS-0430', tipo='Dessecação pré-plantio', talhao='T1-A', area=160)                   # antes OS-0422 (DEMO-15)
OS_DEMO17=dict(id='OS-0431', tipo='Plantio · Soja 58 W', talhao='T2', area=102, janela='amanhã (24/09) 06:00',
               causa='Trator T1 bloqueado pelo PCM (OM-0233)')                                         # antes OS-0423 (DEMO-17)
SUBST='Proposto · OS-0420 saldo 70 ha · aguarda PCP'                                                   # DEMO-04 · rótulo único
NEC28=dict(id='NEC-028', rec='REC-014 v2', area=100, total=204)
KCL_T4=NEC28['area']*0.12*OS420['saldo']/NEC28['area']                                                # 120 kg/ha × 70 ha = 8,4 t

def _n(v,d=0): return f'{v:,.{d}f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
def _br(iso): y,m,d=iso.split('-'); return f'{d}/{m}/{y}'
def _dm(dt): return dt.strftime('%d/%m')
def _datv(c,aid): return D2.data_atividade(c,next(a for a in SOJA['atividades'] if a['id']==aid))
COL_A=_datv(T1A,'a8'); COL_B=_datv(T1B,'a8')                                                          # 10/02 e 20/02/2027
import datetime as _dt
JAN=lambda c: f"{_dm(c-_dt.timedelta(days=5))}–{_dm(c+_dt.timedelta(days=5))}"
META_A, META_B = T1A['meta'], T1B['meta']
_A=T1A['area']*META_A; _B=T1B['area']*META_B                                                           # 10.240 e 9.424 sc
SEMANAS=['25/01','01/02','08/02','15/02','22/02','01/03']
OFERTA=[0,_A//2,_A//2,_B//2,_B//2,0]
DEMANDA=[0,3000,3000,4000,4000,0]                                                                      # entregas contratadas (sc)
SECAGEM=5500                                                                                           # colheita/secagem sc/semana

# ---------------- ações secundárias: ícone + rótulo + title ----------------
def _ic(html,name,title):
    m=re.match(r'^(<(button|a)\b[^>]*?)>(.*)</(button|a)>$',html,re.S)
    return f'{m.group(1)} title="{esc(title)}"><span style="display: inline-flex; align-items: center; gap: 6px;">{icon(name,14)}{m.group(3)}</span></{m.group(4)}>'
def imsg(tx,msg,ic,title,primary=False): return _ic(msgbtn(tx,msg,primary=primary),ic,title)
def idrw(tx,d,ic,title,primary=False): return _ic(drawer_button(tx,d,primary=primary),ic,title)
def ilnk(tx,href,ic,title): return _ic(btn(tx,small=True,href=href),ic,title)
def _nota(txt,state=None):
    bd=f'border-left: 3px solid {YEL}; padding-left: 12px;' if state=='yellow' else ''
    return f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.6; {bd}">{txt}</div>'
def _ficha(pares):   # ficha de leitura (pares rótulo → valor): não é lista de registros, por isso não é grade
    return ''.join(f'<div style="display: grid; grid-template-columns: 220px 1fr; gap: 12px; padding: 9px 2px; border-top: {"0" if i==0 else "1px solid "+LINE}; font-size: 13px; line-height: 1.5;">'
                   f'<div style="color: {MUTED}; font-weight: 600;">{esc(k)}</div><div>{v}</div></div>' for i,(k,v) in enumerate(pares))
def _acoes(*xs): return f'<div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">{"".join(xs)}</div>'
def _pill(tx): return f'<span style="display: inline-block; padding: 2px 9px; border-radius: 10px; font-size: 12px; font-weight: 600; color: {MUTED}; border: 1px solid {LINE}; line-height: 1.4;">{esc(tx)}</span>'
def R(id,v,p=None,s=None,**kw):
    s=dict(s or {})
    for k,pl in (p or {}).items():
        if k not in s: s[k]=' '.join(x['t'] for x in pl if x['k']!='br')
    return dict(id=id,v=v,s=s,p=p or {},**kw)
B,TX,MU,CH,LK,CT,BR=Pt.b,Pt.txt,Pt.mut,Pt.chip,Pt.link,Pt.cta,Pt.br

def _mapa_t1(h=300):
    """T1 dividido em T1-A (norte) e T1-B (sul) — proposta v2; linha tracejada = divisão ainda não vigente."""
    Bc='#1E6FB8'
    s=f'<svg viewBox="0 0 700 {h}" style="width: 100%; height: auto; display: block; border-radius: 10px;" role="img" aria-label="Talhão T1 dividido em T1-A e T1-B">'
    s+=f'<rect x="0" y="0" width="700" height="{h}" fill="#E3EBDD"/>'
    s+=f'<polygon points="30,24 660,30 668,152 26,146" fill="{ACC}" fill-opacity=".30" stroke="{ACC}" stroke-width="3"/>'
    s+=f'<polygon points="26,146 668,152 676,{h-22} 20,{h-28}" fill="{Bc}" fill-opacity=".20" stroke="{Bc}" stroke-width="2"/>'
    s+=f'<line x1="26" y1="146" x2="668" y2="152" stroke="{INK}" stroke-width="2" stroke-dasharray="8 6"/>'
    s+=f'<text x="60" y="80" font-size="22" font-weight="800" fill="{INK}">T1-A · {T1A["area"]} ha</text><text x="60" y="104" font-size="13" fill="{INK}">Soja {T1A["variedade"]} · plantio {_br(T1A["plantio"])[:5]} · colheita {JAN(COL_A)}</text>'
    s+=f'<text x="60" y="206" font-size="22" font-weight="800" fill="{INK}">T1-B · {T1B["area"]} ha</text><text x="60" y="230" font-size="13" fill="{INK}">Soja {T1B["variedade"]} · plantio {_br(T1B["plantio"])[:5]} · colheita {JAN(COL_B)}</text>'
    s+=f'<rect x="470" y="{h-60}" width="196" height="30" rx="8" fill="#fff" fill-opacity=".92"/><text x="482" y="{h-40}" font-size="11.5" font-weight="700" fill="{INK}">- - - divisão proposta (não vigente)</text>'
    return s+'</svg>'

def _curva(w=1120,h=210):
    """barras = oferta semanal; marcador = entregas contratadas; tracejado = capacidade de colheita/secagem."""
    L,Rr,T,Bm=56,16,14,30; iw=w-L-Rr; ih=h-T-Bm; hi=max(max(OFERTA),SECAGEM)*1.12; n=len(SEMANAS); bw=iw/n
    Y=lambda v:T+ih*(1-v/hi)
    s=f'<svg viewBox="0 0 {w} {h}" style="width: 100%; height: auto; display: block;" role="img" aria-label="Oferta semanal de soja por parcela contra entregas e capacidade">'
    for k in range(5):
        v=hi*k/4; y=Y(v); s+=f'<line x1="{L}" y1="{y:.1f}" x2="{w-Rr}" y2="{y:.1f}" stroke="{LINE}"/><text x="{L-6}" y="{y+4:.1f}" text-anchor="end" font-size="10.5" fill="{MUTED}">{_n(v)}</text>'
    for i,(o,d) in enumerate(zip(OFERTA,DEMANDA)):
        x=L+bw*i; cor=ACC if i<3 else '#1E6FB8'
        if o: s+=f'<rect x="{x+bw*.22:.1f}" y="{Y(o):.1f}" width="{bw*.56:.1f}" height="{Y(0)-Y(o):.1f}" rx="4" fill="{cor}" fill-opacity=".75"/><text x="{x+bw/2:.1f}" y="{Y(0)-12:.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="#fff">{_n(o)} sc</text>'
        if d: s+=f'<line x1="{x+bw*.15:.1f}" y1="{Y(d):.1f}" x2="{x+bw*.85:.1f}" y2="{Y(d):.1f}" stroke="{YEL}" stroke-width="3"/>'
        s+=f'<text x="{x+bw/2:.1f}" y="{h-10}" text-anchor="middle" font-size="10.5" fill="{MUTED}">{SEMANAS[i]}</text>'
    s+=f'<line x1="{L}" y1="{Y(SECAGEM):.1f}" x2="{w-Rr}" y2="{Y(SECAGEM):.1f}" stroke="{RED}" stroke-width="1.5" stroke-dasharray="6 5"/><text x="{w-Rr-4}" y="{Y(SECAGEM)-6:.1f}" text-anchor="end" font-size="11" fill="{RED}">capacidade de colheita/secagem {_n(SECAGEM)} sc/semana</text>'
    return s+'</svg>'

# ---------------- painel compartilhado · Manutenções e impacto na produção (DEMO-17) ----------------
def _painel_manut(gid):
    g=grid([dict(k='man',l='Manutenção',w=230),dict(k='jan',l='Janela',w=150),dict(k='prod',l='Produção afetada',w=250),dict(k='sit',l='Situação',w=280),dict(k='ab',l='Abrir')],[
        R('m1',dict(man='Corretiva OM-0233',jan='até teste aprovado',prod=f'OS-0420 saldo {OS420["saldo"]} ha · {OS_DEMO17["id"]} plantio T2'),
          p=dict(man=[B('Corretiva OM-0233'),BR(),MU('Trator T1 · retorno previsto 14h · não confirmado')],
                 prod=[TX(f'OS-0420 saldo {OS420["saldo"]} ha'),BR(),TX(f'{OS_DEMO17["id"]} · plantio T2 · {OS_DEMO17["area"]} ha')],
                 sit=[CH(SUBST,'yellow'),BR(),CH(f'{OS_DEMO17["id"]}: sem substituto confirmado','red')],ab=[LK('Ver ordem','MA.dc.html#om=OM-0233')])),
        R('m2',dict(man='Preventiva 250 h · OM-0234',jan='28/09',prod='OS-0420 saldo · substituto até 27/09'),
          p=dict(man=[B('Preventiva 250 h · OM-0234'),BR(),MU('Trator 02 · MF 7719')],sit=[CH('Conflito · OS-0420','red')],ab=[LK('Ver conflito','PL-05.dc.html')])),
        R('m3',dict(man='Revisão pré-plantio',jan='25/09',prod='nenhuma ordem na janela'),
          p=dict(man=[B('Revisão pré-plantio'),BR(),MU('Plantadeira 24 linhas')],sit=[CH('Sem conflito','green')],ab=[LK('Ver agenda','PL-04.dc.html')])),
      ],edit=dict(m='ro',title='Manutenção × produção',fields=[dict(k='man',l='Manutenção',ro=True),dict(k='jan',l='Janela',ro=True),dict(k='prod',l='Produção afetada',ro=True)]),
      search=False,total=False,gid=gid)
    return section('Manutenções e impacto na produção','Simule a janela da parada e proponha substituição; os conflitos seguem para Impedimentos e reprogramação.',
        [imsg('Simular janela','Janela simulada para a preventiva do MF 7719: 29–30/09 · sem conflito com o saldo da OS-0420 · proposta, nenhuma reserva firme criada.',
              'calendar','Simular outra janela para a preventiva, sem reservar agenda'),
         imsg('Propor substituição',f'Proposta registrada: Trator 02 · MF 7719 para a {OS_DEMO17["id"]} (24/09) e o saldo de {OS420["saldo"]} ha da OS-0420 · aguarda PCP · conflito com a preventiva de 28/09 enviado a Impedimentos e reprogramação (simulado).',
              'truck','Registrar a proposta de substituto para as ordens afetadas pelo Trator T1'),
         ilnk('Abrir impedimentos','PL-05.dc.html','alert','Abrir Impedimentos e reprogramação')],g,state='red')

JS_COMUM=r'''
function pl_G(id){ return GRIDS.find(g=>g.id===id); }
function pl_br(iso){ const a=String(iso||'').split('-'); return a.length===3? a[2]+'/'+a[1]+'/'+a[0] : String(iso||''); }
function pl_dm(dt){ return ('0'+dt.getDate()).slice(-2)+'/'+('0'+(dt.getMonth()+1)).slice(-2); }
'''

def build():
    E.MSGS['Autorizar execução 2026/27']=('Não autorizado: o orçamento revisado da Safra 2026/27 aguarda a Direção. Plano operacional v3 aprovado ✓ · orçamento pendente ✗. '
                                         'Como resolver: cobrar a aprovação em Aprovações; a data de início nunca supre a aprovação.')
    E.MSGS['Publicar plano v4']=('Plano v4 publicado (alçada da agronomia) · 7 necessidades únicas · nenhuma O.S. nova emitida — a O.S. nasce na janela de emissão '
                                 'e consome o saldo da mesma necessidade · NEC-019 continua aguardando a decisão da pendência.')
    E.MSGS['Publicar ajuste do T1-A']=('Ajuste do T1-A publicado na v4 · Cletodim 240 a 0,36 L/ha só neste talhão · padrão 0,45 L/ha intacto · '
                                       f'dessecação de manejo de 05/09 preservada · a {OS_DES["id"]} já emitida (A liberar) só muda se o agrônomo ajustar ao liberar.')
    E.MSGS['Publicar parcelamento e plano']=('Parcelamento v2 publicado · a grade da safra e o plano operacional passam a seguir T1-A/T1-B · histórico do T1 preservado · '
                                             'área de cobrança continua 312 ha · nenhuma O.S. emitida.')

    # ================= PL-01 · Safras, ciclos e metas =================
    HEIGHTS37['PL-01.dc.html']=1300
    cults=D2.CULTIVOS['S2627']; area=sum(c['area'] for c in cults); semplano=[c['local'] for c in cults if not c['plano']]
    ncult=lambda sid: (len(D2.CULTIVOS[sid]), sum(c['area'] for c in D2.CULTIVOS[sid]))
    SIT={'S2627':(CH('Em planejamento · orçamento aguarda Direção','yellow'),LK('Abrir plano','PL-02.dc.html')),
         'S27SF':(CH('Rascunho','gray'),LK('Abrir no Planejar safra','SAF.dc.html')),
         'S2526':(CH('Encerrada','gray'),LK('Abrir fechamento','GE-03.dc.html'))}
    g_saf=grid([dict(k='nome',l='Safra',w=170),dict(k='per',l='Período',w=160),dict(k='faz',l='Fazenda'),dict(k='cult',l='Cultivos · área',w=150),dict(k='sit',l='Situação',w=280),dict(k='ab',l='Abrir')],
       [R(s['id'],dict(nome=s['nome'],per=s['periodo'],faz=s['fazenda'],cult=f'{ncult(s["id"])[0]} cultivos · {_n(ncult(s["id"])[1])} ha'),
          p=dict(nome=[B(s['nome'])],sit=[SIT.get(s['id'],(CH(s['estado'],'yellow'),))[0]],ab=[SIT.get(s['id'],(None,LK('Abrir no Planejar safra','SAF.dc.html')))[1]]),ro=s['ro']) for s in D2.SAFRAS],
       edit=dict(m='form',title='Safra',newTitle='Nova safra',sub='Altere nome, período e fazenda. Cultivos e metas ficam na grade de cultivo.',
                 fields=[dict(k='nome',l='Nome da safra',req=True),dict(k='per',l='Período',req=True,help='Ex.: set/2027 – ago/2028'),
                         dict(k='faz',l='Fazenda',t='sel',opts=['Santa Rita','Boa Vista'],req=True,**{'def':'Santa Rita'}),dict(k='cult',l='Cultivos · área',ro=True)]),
       add='Nova safra',search=False,total=False,gid='g_saf')
    PLN={p['id']:f"{p['nome']} v{p['versao']}" for p in D2.PLANOS}
    rows=[]
    for c in cults:
        pn=PLN.get(c['plano'],'Sem plano')
        p=dict(local=[B(c['local']),BR(),MU(c['tipo'])],plano=[CH(pn,'yellow')] if pn=='Sem plano' else [TX(pn)])
        if c['local']=='T4': p['plant']=[TX(_br(c['plantio'])),BR(),MU(f'1ª onda {NEC28["area"]} ha em curso · OS-0420')]
        if c['cultura'] in ('Café','Mamão Formosa'): p['plant']=[TX(_br(c['plantio'])),BR(),MU('ciclo vinculado · pomar existente')]
        rows.append(R(c['id'],dict(local=c['local'],cult=c['cultura'],var=c['variedade'],area=c['area'],plant=c['plantio'],meta=f"{c['meta']} {c['un_meta']}",plano=pn),p=p))
    g_cult=grid([dict(k='local',l='Talhão/parcela',w=130),dict(k='cult',l='Cultura'),dict(k='var',l='Variedade'),dict(k='area',l='Área',t='num',a='r',u='ha',agg='sum'),
                 dict(k='plant',l='Plantio previsto',t='date',w=200),dict(k='meta',l='Meta (hipótese)'),dict(k='plano',l='Plano',w=220,chips={'Sem plano':'yellow'})],rows,
       edit=dict(m='form',title='Cultivo',sub='Altere variedade, área, plantio previsto, meta e plano. Salvar recalcula só o rascunho; nada é publicado.',
                 fields=[dict(k='local',l='Talhão/parcela',ro=True),dict(k='cult',l='Cultura',ro=True),
                         dict(k='var',l='Variedade',t='sel',opts=['58 W','62 X','Híbrido AG 8700','Formosa','Catuaí 144'],req=True),
                         dict(k='area',l='Área',t='num',u='ha',min=1,max=400,req=True),dict(k='plant',l='Plantio previsto',t='date',req=True,help='A data prevista nunca vira plantio realizado.'),
                         dict(k='meta',l='Meta de produtividade (hipótese)',req=True),dict(k='plano',l='Plano',t='sel',opts=list(PLN.values())+['Sem plano'],req=True)]),
       search=True,total=True,gid='g_cult')
    corpo=(
      kpis([('SAFRAS ABERTAS','2','2026/27 · Safrinha 2027'),('ÁREA PLANEJADA',f'{_n(area)} ha',f'Safra 2026/27 · {len(cults)} cultivos'),
            ('CULTIVOS SEM PLANO',str(len(semplano)),' · '.join(semplano)),('ORÇAMENTO 2026/27','Pendente','aguarda Direção')])
      + section('Safras e períodos','Abra a safra para planejar; autorize a execução só com plano e orçamento aprovados.','',g_saf)
      + section('Grade de cultivo · Safra 2026/27','Defina variedade, área, plantio previsto e plano de cada talhão ou parcela antes de detalhar as operações.',
          [imsg('Vincular ciclo','Ciclo 2026/27 do café vinculado ao pomar C1 (2019) · a ocupação mantém identidade própria · nada é recriado.','leaf','Vincular o ciclo perene ao pomar existente'),
           imsg('Revisar idades','Idades revisadas: C1 pomar 2019 · 7 anos · T7 mamão · 18 meses — atividades por idade recalculadas só no rascunho.','clock','Recalcular atividades por idade das perenes'),
           ilnk('Simular parcelas','PL-06.dc.html','layers','Abrir Parcelas e escalonamento')],g_cult)
      + section('Encerramento do período anterior','Destine as pendências antigas antes de encerrar; o pomar e as ocupações não são recriados.',
          [imsg('Encerrar período','Nenhum período apto a encerrar agora: 2026/27 está em planejamento e 2025/26 já foi encerrada em 30/08 com as pendências destinadas.','check','Encerrar o período com as pendências destinadas')],
          _nota(f'Safra 2025/26 encerrada em 30/08. Pendência destinada: sobra de 14 sc de KCl transferida ao estoque geral (recibo). '
                f'A adubação pós-colheita do café C1 (NEC-019) segue em <b style="color:{INK};">Decidir pendência</b> no plano operacional.'),state='gray')
    )
    EXTRAJS[0]=JS_COMUM+r'''
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_saf'||!r||(r.p&&r.p.sit)) return;
    const nr=g2clone(rows); const x=g2find(nr,r.id); x.p.sit=[{k:'chip',t:'Rascunho · o cálculo já existe no rascunho',c:'gray'}]; x.s.sit='Rascunho';
    x.p.ab=[{k:'link',t:'Abrir no Planejar safra',h:'SAF.dc.html'}]; x.v.cult='0 cultivos'; g2set(self,gid,{rows:nr});
    self.setState({g2toast:'Safra '+x.v.nome+' criada em rascunho · inclua os cultivos na grade'}); };
}'''
    shell37('PL-01','Safras, ciclos e metas',corpo,
      subtitle='Períodos, ciclos e metas por fazenda, talhão e parcela — o cálculo existe desde o rascunho.',
      status=('2026/27 em planejamento','yellow'),primary='Autorizar execução 2026/27',
      footer='Autorizar execução exige plano e orçamento aplicáveis aprovados; a passagem da data nunca supre aprovação (JANELA-01).')

    # ================= PL-02 · Plano operacional =================
    HEIGHTS37['PL-02.dc.html']=1060
    d_des=_dm(_datv(T1A,'a1')); d_pl=_dm(_datv(T1A,'a3')); d_hb=_dm(_datv(T1A,'a5')); d_plB=_dm(_datv(T1B,'a3'))
    tal=lambda: LK('Ver plano do talhão','PL-02det.dc.html')
    ops=[
      R('nec28',dict(parc='T4',atv='Plantio · 1ª onda',area=NEC28['area'],dose='Semente 52 kg/ha + KCl 60% 120 kg/ha',gat='no dia do plantio · 1ª onda 22–28/09',jan='22–28/09',ver='v2',sit='Em execução'),
        p=dict(parc=[B('T4'),BR(),MU('Soja 58 W')],atv=[TX('Plantio · 1ª onda'),BR(),MU(f'{NEC28["id"]} · {NEC28["rec"]} · {NEC28["area"]} de {NEC28["total"]} ha')],
               sit=[CH('Convertida · OS-0420','green'),BR(),MU(f'{OS420["realizado"]} de {NEC28["area"]} ha feitos · saldo {OS420["saldo"]} ha impedido')],
               ab=[LK('Abrir O.S.','OS.dc.html'),BR(),LK('Ver recomendação','AG-04det.dc.html')])),
      R('nec31',dict(parc='T1-A',atv='Dessecação pré-plantio',area=T1A['area'],dose='Glifosato 480 2,0 L/ha + 2,4-D 1,0 L/ha',gat=f'20 dias antes do plantio · DAP −20 · previsto {d_pl} → {d_des}',jan='±5 d',ver='v3',sit='O.S. emitida'),
        p=dict(parc=[B('T1-A'),BR(),MU('Soja 58 W')],atv=[TX('Dessecação pré-plantio'),BR(),MU('NEC-031')],gat=[TX('20 dias antes do plantio · DAP −20'),BR(),MU(f'previsto {d_pl} →'),B(d_des)],
               sit=[CH(f'O.S. emitida · {OS_DES["id"]}','green')],ab=[tal()])),
      R('nec32',dict(parc='T1-A',atv='Plantio e adubação de base',area=T1A['area'],dose='Semente 52 kg/ha + MAP 250 kg/ha',gat=f'no dia do plantio · DAP 0 → {d_pl}',jan='10–20/10',ver='v3',sit='Prevista'),
        p=dict(parc=[B('T1-A'),BR(),MU('Soja 58 W')],atv=[TX('Plantio e adubação de base'),BR(),MU('NEC-032')],gat=[TX('no dia do plantio · DAP 0 →'),B(d_pl)],sit=[CH('Prevista','gray')],ab=[tal()])),
      R('nec33',dict(parc='T1-A',atv='Herbicida pós-emergente',area=T1A['area'],dose='Cletodim 240 0,45 L/ha',gat=f'25 dias após o plantio · DAP +25 → {d_hb}',jan='±3 d',ver='v3',sit='Aguarda plantio real'),
        p=dict(parc=[B('T1-A'),BR(),MU('Soja 58 W')],atv=[TX('Herbicida pós-emergente'),BR(),MU('NEC-033')],dose=[TX('Cletodim 240 0,45 L/ha'),BR(),MU('ajuste local 0,36 em revisão')],
               gat=[TX('25 dias após o plantio · DAP +25 →'),B(d_hb)],sit=[CH('Aguarda plantio real','yellow')],ab=[tal()])),
      R('nec34',dict(parc='T1-B',atv='Plantio escalonado',area=T1B['area'],dose='Semente 52 kg/ha + MAP 250 kg/ha',gat=f'no dia do plantio · DAP 0 → {d_plB}',jan='20–30/10',ver='v3',sit='Prevista'),
        p=dict(parc=[B('T1-B'),BR(),MU('Soja 62 X')],atv=[TX('Plantio escalonado'),BR(),MU('NEC-034')],gat=[TX('no dia do plantio · DAP 0 →'),B(d_plB)],sit=[CH('Prevista','gray')])),
      R('nec26',dict(parc='P1',atv='Fungicida R5',area=95,dose='Fungicida A 0,50 L/ha',gat='21 dias antes da colheita · colheita prevista 20/10 → 29/09',jan='±2 d',ver='v2',sit='Prevista'),
        p=dict(parc=[B('P1'),BR(),MU('Feijão Pérola')],atv=[TX('Fungicida R5'),BR(),MU('NEC-026')],gat=[TX('21 dias antes da colheita · colheita prevista 20/10 →'),B('29/09')],sit=[CH('Prevista','gray')])),
      R('nec19',dict(parc='C1',atv='Adubação pós-colheita',area=38,dose='KCl 60% 150 kg/ha',gat='30 dias após a colheita · colheita real 12/08 → 11/09',jan='±10 d',ver='v2',sit='Vencida',pend='Vencida'),
        p=dict(parc=[B('C1'),BR(),MU('Café Catuaí 144')],atv=[TX('Adubação pós-colheita'),BR(),MU('NEC-019 · ciclo 2025/26')],gat=[TX('30 dias após a colheita · colheita real 12/08 →'),B('11/09')],
               sit=[CH('Vencida · decidir pendência','red'),BR(),MU('sem compra até a decisão')],ab=[{'k':'act','t':'Decidir pendência','fn':'pl_dec:nec19','u':True}])),
    ]
    for r in ops:   # janela sob o gatilho e área sob a parcela (menos colunas, sem rolagem lateral)
        g=r['p'].get('gat') or [TX(r['v']['gat'])]; r['p']['gat']=g+[BR(),MU('janela '+r['v']['jan'])]; r['s']['gat']=r['v']['gat']+' janela '+r['v']['jan']
        pc=r['p']['parc']; pc[-1]=MU(pc[-1]['t']+f" · {r['v']['area']} ha")
    g_op=grid([dict(k='parc',l='Parcela · cultivo',w=120),dict(k='atv',l='Atividade · necessidade',w=170),dict(k='dose',l='Dose/quantidade',w=160),
               dict(k='gat',l='Gatilho por extenso → data',w=210),dict(k='sit',l='Situação',w=200),dict(k='ab',l='Abrir',w=150)],ops,
       edit=dict(m='form',title='Operação',sub='Ajuste dose, gatilho e janela no rascunho v4. Publicar recalcula as necessidades; O.S. emitida só muda pelo ajuste do agrônomo ao liberar (ou ao ajustar o saldo em execução).',
                 fields=[dict(k='parc',l='Parcela',ro=True),dict(k='atv',l='Atividade',ro=True),dict(k='area',l='Área',t='num',u='ha',ro=True),
                         dict(k='dose',l='Dose/quantidade',req=True),dict(k='gat',l='Gatilho por extenso',req=True,help='Ex.: 20 dias antes do plantio · DAP −20. Não digite sinal negativo.'),
                         dict(k='jan',l='Janela',req=True),
                         dict(k='pend',l='Pendência',ro=True,cond=dict(k='pend',eq='Vencida'),help='Operação vencida: consulte o realizado e decida — não há descarte automático.'),
                         dict(k='dec',l='Decisão da pendência',t='sel',opts=['Realizada','Pendente','Não aplicável'],req=True,cond=dict(k='pend',eq='Vencida')),
                         dict(k='evid',l='Evidência (apontamento, foto ou nota)',req=True,cond=dict(k='dec',eq='Realizada')),
                         dict(k='prazo',l='Novo prazo',t='date',req=True,cond=dict(k='dec',eq='Pendente')),
                         dict(k='resp',l='Responsável',t='sel',opts=['Ana (agrônoma)','Paula','Marcos','Carlos'],req=True,cond=dict(k='dec',eq='Pendente')),
                         dict(k='mot',l='Motivo',t='area',req=True,cond=dict(k='dec',eq='Não aplicável'))]),
       search=True,total=False,gid='g_op')
    corpo=(
      section('Operações previstas · Safra 2026/27','Confira cada operação por parcela e data; clique na linha para ajustar dose, gatilho e janela ou decidir a pendência.',
        [idrw('Adicionar operação',dict(title='Nova operação do plano',sub='vínculo a recomendação ou análise é opcional na operação direta',
            fields=[('Talhão/parcela','T1-B'),('Atividade','Dessecação pré-plantio'),('Insumo','Glifosato 480'),('Dose','2,0 L/ha'),
                    ('Gatilho','20 dias antes do plantio · DAP −20'),('Janela','±5 dias'),('Data','05/10/2026')],
            confirm='Adicionar ao plano',done='Operação adicionada ao rascunho v4'),'lista','Incluir uma operação no rascunho v4'),
         ilnk('Gerar sugestões pelas análises','AG-04.dc.html','lab','Abrir recomendações a partir das análises'),
         imsg('Aplicar modelo','Modelo “Soja alta tecnologia v6” aplicado ao rascunho v4 do T2 · 12 operações propostas · exceções locais preservadas · nada publicado.','layers','Aplicar um plano-modelo ao rascunho')],
        g_op)
      + section('Regras do gatilho','Leia o gatilho por extenso; a data prevista nunca vira plantio realizado.',
        _acoes(ilnk('Ver grade de cultivo','PL-01.dc.html','grid','Abrir a grade de cultivo da safra'),
               imsg('Simular antecipação do plantio',f'Simulação: antecipar o plantio do T1-A para 10/10 move 7 operações dependentes · a {OS_DES["id"]} (DAP −20) já emitida é ajustada pelo agrônomo ao liberar · nada muda até publicar.','calendar','Simular antecipação sem alterar o plano'),
               ilnk('Ver capacidade','SAF.dc.html#saf=S2627&passo=operacoes','trend','Abrir a capacidade por mês da Safra 2026/27 em Planejar safra'),
               ilnk('Ver compra de insumos','CMP.dc.html','cart','Abrir Compra de insumos (SOL-2026-07)')),
        _nota(f'“20 dias antes do plantio · DAP −20 · previsto para {d_des}” — o produtor não digita sinal negativo. '
              f'“Dias antes da colheita” e “dias após a colheita” são opções distintas, com a colheita escolhida. '
              f'Operação vencida exige consulta ao realizado e decisão sobre a pendência, não descarte automático.'),state='gray'))
    EXTRAJS[0]=JS_COMUM+r'''
function EXTRAVALS(self,v){
  v.pl_dec=(rid)=>{ const sp=pl_G('g_op'); g2open(self,sp,rid); const st=g2st(self,'g_op'); };
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_op'||!r) return;
    const nr=g2clone(rows); const x=g2find(nr,r.id);
    x.p.gat=[{k:'txt',t:x.v.gat},{k:'br',t:''},{k:'mut',t:'janela '+x.v.jan}]; x.s.gat=x.v.gat+' janela '+x.v.jan;
    if(x.v.pend!=='Vencida'){ g2set(self,gid,{rows:nr,fl:x.id}); return; }
    const d=x.v.dec; let chip, msg;
    if(d==='Realizada'){ chip={k:'chip',t:'Realizada · evidência registrada',c:'green'}; msg='Pendência decidida: Realizada · evidência anexada ao histórico · NEC-019 baixada sem nova compra'; }
    else if(d==='Pendente'){ chip={k:'chip',t:'Pendente · novo prazo '+pl_br(x.v.prazo)+' · '+x.v.resp,c:'yellow'}; msg='Pendência mantida: novo prazo '+pl_br(x.v.prazo)+' com '+x.v.resp+' · a necessidade volta a gerar demanda de KCl'; }
    else { chip={k:'chip',t:'Não aplicável · motivo registrado',c:'gray'}; msg='Pendência encerrada como não aplicável · motivo registrado · nenhuma compra gerada'; }
    x.v.pend='Decidida'; x.v.sit=d; x.s.sit=chip.t; x.p.sit=[chip]; x.p.ab=[]; x.s.ab='';
    g2set(self,gid,{rows:nr,fl:x.id}); self.setState({g2toast:msg}); };
}'''
    shell37('PL-02','Plano operacional',corpo,
      subtitle='Operações por parcela e data com memória de quantidades — planejar não emite O.S.',
      status=('v4 em rascunho · 1 pendência vencida','yellow'),primary='Publicar plano v4',
      footer='Publicação cria necessidades únicas; a O.S. nasce depois, na janela de emissão (8.6), consumindo o saldo da mesma necessidade (JANELA-07).')

    # ---- PL-02det · plano do talhão T1-A com gatilhos (detalhe âncora, cap. 40) ----
    HEIGHTS37['PL-02det.dc.html']=1000; PARENT37['PL-02det.dc.html']='PL-02.dc.html'
    def _q(x): return ((f'{x:.2f}'.rstrip('0') if round(x,1)!=x else f'{x:.1f}').replace('.',',')) if x<10 else _n(x)
    def _prods(a,local=None): return ' + '.join(f"{p['prod'].split(' · ')[0]} {_q(local if (local and i==0) else p['dose'])} {p['un']}/ha" for i,p in enumerate(a['prods'])) or '—'
    trows=[R('man',dict(atv='Dessecação de manejo',gat='40 dias antes do plantio · DAP −40',data='05/09',dl='Glifosato 480 2,0 L/ha',dp='Glifosato 480 2,0 L/ha'),
             p=dict(sit=[CH('Realizada 05/09 · preservada','green')],dp=[MU('igual à local')]),ro=True)]
    for a in SOJA['atividades']:
        dt=_dm(_datv(T1A,a['id'])); g=a['g']['dias']
        gtx=('no dia do plantio · DAP 0' if g==0 else (f'{abs(g)} dia{"s" if abs(g)>1 else ""} antes do plantio · DAP −{abs(g)}' if g<0 else f'{g} dias após o plantio · DAP +{g}'))
        sit={'a1':(f'O.S. emitida · {OS_DES["id"]}','green'),'a5':('Aguarda plantio real','yellow')}.get(a['id'],('Prevista','gray'))
        dl=_prods(a,0.36 if a['id']=='a5' else None)
        p=dict(sit=[CH(*sit)])
        if a['id']=='a5': p['dl']=[B(dl),BR(),MU('ajuste local em revisão')]
        dp=_prods(a); p['dp']=[MU('igual à local')] if dp==dl else [TX(dp.split(' + ')[0])]
        trows.append(R(a['id'],dict(atv=a['nome'],gat=gtx,data=dt,dl=dl,dp=dp),p=p,ro=(a['id']=='a1')))
    g_tal=grid([dict(k='atv',l='Atividade',w=170),dict(k='gat',l='Gatilho por extenso',w=180),dict(k='data',l='Data resultante'),dict(k='sit',l='Estado',w=200),
                dict(k='dl',l='Dose local',w=250),dict(k='dp',l='Dose padrão',w=160)],trows,
       edit=dict(m='form',title='Ajuste local',sub='Vale só para o T1-A; o padrão não muda. Informe o motivo — a comparação com o padrão continua visível.',
                 fields=[dict(k='atv',l='Atividade',ro=True),dict(k='data',l='Data resultante',ro=True,help='Recalculada pela âncora do talhão.'),
                         dict(k='dl',l='Dose local',req=True),dict(k='dp',l='Dose padrão',ro=True),
                         dict(k='mot',l='Motivo do ajuste',t='area',req=True,**{'def':''})]),
       search=False,total=False,gid='g_tal')
    corpo=(
      continuity('Plano operacional','Talhão T1-A · Soja 58 W · plantio previsto '+d_pl,'ajuste local em revisão','Publicar ajuste do T1-A')
      + section('Operações deste talhão',f'Confira a data resultante de cada gatilho contra o plantio previsto em {d_pl}; clique na operação para ajustar a dose local com motivo.','',g_tal)
      + section('Ajuste local × padrão','Compare o custo do ajuste antes de publicar; o realizado e as aprovações ficam intactos.','',
        _nota(f'Herbicida pós-emergente local <b style="color:{INK};">Cletodim 240 0,36 L/ha</b> (padrão 0,45) · motivo: solo arenoso, menor pressão de plantas daninhas · efeito estimado: '
              f'<b style="color:{INK};">−R$ 0,9 mil</b> no talhão ({T1A["area"]} ha × 0,09 L × R$ 62/L) {tag("hipótese de preço")}. Atualizar o padrão depois <b style="color:{INK};">não sobrescreve</b> esta exceção. '
              f'A dessecação de manejo de 05/09 permanece intacta; a {OS_DES["id"]} já emitida só muda de dose se o agrônomo ajustar ao liberar.',state='yellow'),state='yellow')
    )
    shell37('PL-02','Plano do talhão T1-A · gatilhos',corpo,fname='PL-02det.dc.html',crumbs_extra=['T1-A · Soja 58 W'],
      subtitle='Plano por talhão com gatilhos antes, no dia e depois do plantio, resolvidos contra a âncora prevista.',
      status=('Ajuste local em revisão','yellow'),primary='Publicar ajuste do T1-A',
      footer='DAP −20 gera O.S. A liberar (o agrônomo libera) com base prevista antes de existir plantio real (DAP-03); previsão nunca vira plantio realizado.')

    # ================= PL-03 · Capacidade e recursos =================
    HEIGHTS37['PL-03.dc.html']=1900
    maq_cards=[
      ('Trator 02 · MF 7719','Apta','green',SUBST,f'livre hoje · 25/09 reservado ({OS_DES["id"]})','elegível só após confirmação do PCP · preventiva 28/09'),
      ('Trator 03 · JD 6M','Apta','green','Operando · OS-0421 dia 4 de 7','fim previsto 26/09 (dia 7)','reserva futura: dessecação T1-B 05/10'),
      ('Trator T1 · JD 6M 155','Indisponível · bloqueado pelo PCM','red','Parado · oficina (OM-0233)','retorno previsto 14h — aguardando teste','não ofertado como livre'),
      ('Pulverizador 01','Apta com restrição · bico seção 3','yellow',f'Reservado · {OS_DES["id"]} 25/09','elegível sob condição validada','restrição registrada pelo PCM'),
      ('Plantadeira 24 linhas (implemento)','Apta','green',f'Reservada · {OS_DEMO17["id"]} 24/09 · T1-A 15/10','trator livre + implemento reservado ≠ conjunto livre','revisão pré-plantio 25/09'),
      ('Colhedora Axial-Flow 7250','A confirmar','gray','Sem telemetria · checklist de 14/09','informação vencida pela política','não fica verde por falta de notícia'),
    ]
    cards=''.join(
      f'<div style="min-width: 0; background: {SURF}; border: 1px solid {LINE}; border-radius: 12px; padding: 10px 12px;">'
      f'<div style="font-size: 13px; font-weight: 700;">{esc(n)}</div>'
      f'<div style="margin-top: 6px; display: flex; gap: 6px; flex-wrap: wrap; align-items: center;">{chip(cond,k)}{_pill(ocup)}</div>'
      f'<div style="margin-top: 6px; font-size: 12px; color: {MUTED}; line-height: 1.5;">{esc(l1)}{("<br>"+esc(l2)) if l2 else ""}</div></div>'
      for n,cond,k,ocup,l1,l2 in maq_cards)
    CAP=[('trat','Tratores 150+ cv','Plantio soja 910 ha',1180,910,620,120,60,'110 h (OM-0233)',270),
         ('pulv','Pulverizadores','Dessecação + fungicida',520,610,380,180,50,'—',0),
         ('plan','Plantadeiras','Plantio escalonado',430,460,410,50,0,'—',0),
         ('equi','Equipes de campo','Todas',280,300,240,40,20,'—',0),
         ('colh','Colhedoras','Milho P2 (nov)',0,360,0,180,180,'—',None)]
    ORIGC={'trat':[dict(t='Plano operacional: plantio T1-A, T1-B, T2, T4 (1ª onda) e T3 · 910 ha',h='PL-02.dc.html'),dict(t='Capacidade: 4 tratores × 22 dias úteis × 10 h, menos manutenção'),dict(t='Indisponível: Trator T1 parado pela OM-0233',h='MA.dc.html#om=OM-0233')],
           'pulv':[dict(t='Plano operacional: dessecações e fungicidas de outubro',h='PL-02.dc.html'),dict(t='Rendimento 21,6 ha/h · Trator 02 + Pulverizador PJ-3030',h='CD-02.dc.html')],
           'plan':[dict(t='Plano operacional: plantio escalonado T1-A/T1-B e T2',h='PL-02.dc.html'),dict(t='Rendimento 6,8 ha/h · Plantadeira 24 linhas',h='CD-02.dc.html')],
           'equi':[dict(t='Soma das horas de pessoas de todas as operações do mês')],
           'colh':[dict(t='Colheita do milho P2 só em novembro · capacidade ociosa em outubro')]}
    g_cap=grid([dict(k='cls',l='Recurso/classe',w=170),dict(k='op',l='Operação dominante',w=190),dict(k='carga',l='Carga out/26',t='num',a='r',u='h'),dict(k='cap',l='Capacidade líquida',t='num',a='r',u='h'),
                dict(k='ocup',l='Ocupado',t='num',a='r',u='h'),dict(k='livre',l='Livre',t='num',a='r',u='h'),dict(k='sem',l='Sem alocação',t='num',a='r',u='h',zdash=True),
                dict(k='ind',l='Indisponível'),dict(k='def',l='Déficit',w=150)],
       [R(i,dict(cls=c,op=o,carga=cg,cap=cp,ocup=oc,livre=lv,sem=sm,ind=ind,**({'def':df} if df is not None else {})),
          p=dict(cls=[B(c)],**{'def':[CH(f'{df} h','red' if df else 'green')] if df is not None else [CH('Ociosa · realocar','yellow')]}),o=ORIGC[i])
        for i,c,o,cg,cp,oc,lv,sm,ind,df in CAP],
       edit=dict(m='origin',title='Carga × capacidade',fields=[dict(k='cls',l='Recurso/classe',ro=True),dict(k='carga',l='Carga out/26',t='num',u='h',ro=True),
                 dict(k='cap',l='Capacidade líquida',t='num',u='h',ro=True),dict(k='def',l='Déficit',t='num',u='h',ro=True)]),
       search=False,total=False,so=dict(k='carga',d=True),gid='g_cap')
    g_cen=grid([dict(k='cen',l='Cenário',w=260),dict(k='cobre',l='Cobre',t='num',a='r',u='h'),dict(k='custo',l='Custo estimado (hipótese)',t='num',a='r',pre='R$ ',u='mil'),
                dict(k='rest',l='Restrição',w=240),dict(k='cmp',l='Comparação',w=220)],[
        R('c1',dict(cen='Remanejar colhedora ociosa + operador',cobre=60,custo=4,rest='deslocamento 1 dia'),p=dict(cmp=[Pt.tag('reaproveitamento entre setores')])),
        R('c2',dict(cen='2º turno tratores (out)',cobre=190,custo=26,rest='contratar 1 operador'),p=dict(cmp=[CH('Recomendado','green')])),
        R('c3',dict(cen='Aluguel trator 180 cv · 30 d',cobre=80,custo=38,rest='disponível a partir de 05/10',cmp='cobre o restante com o 2º turno')),
        R('c4',dict(cen='Terceirizar plantio (prestador)',cobre=100,custo=42,rest='contrato ativo exigido · a partir de 26/09',cmp='—')),
        R('c5',dict(cen='Aquisição trator novo',cobre=270,custo=620,rest='prazo de entrega 90 d · fora da janela'),p=dict(cmp=[CH('Não atende esta safra','gray')])),
      ],edit=dict(m='form',title='Cenário',sub='Ajuste as hipóteses do cenário. Comparar e publicar não contrata nem compra.',
                  fields=[dict(k='cen',l='Cenário',ro=True),dict(k='cobre',l='Horas cobertas',t='num',u='h',min=0,max=270,req=True),
                          dict(k='custo',l='Custo estimado (hipótese)',t='num',u='R$ mil',min=0,req=True),dict(k='rest',l='Restrição',req=True)]),
       search=False,total=False,gid='g_cen')
    corpo=(
      kpis([('CARGA OUT/26','2.410 h','demanda do plano'),('CAPACIDADE LÍQUIDA','2.640 h','após manutenção'),
            ('DÉFICIT','270 h','tratores 150+ cv'),('OCIOSIDADE OUT/26','180 h','colhedoras')])
      + section('Carga × capacidade por recurso/classe','Compare a carga herdada do plano com a capacidade líquida; clique na classe para ver a origem dos números.',
        [ilnk('Ver rendimentos','CD-02.dc.html','calc','Abrir a tabela de rendimentos das operações')],g_cap,state='red')
      + section('Cenários para o déficit de 270 h','Compare custo e restrição de cada cenário; publicar não contrata nem compra automaticamente.',
        [imsg('Simular turnos e conjuntos','Simulação: 2º turno nos tratores (out) cobre 190 h · custo estimado +R$ 26 mil · restrição: contratar 1 operador habilitado. Nada é alterado.','calc','Simular turnos, equipes e conjuntos'),
         ilnk('Propor cotação','SU-04.dc.html','cart','Abrir a cotação de aluguel ou prestador'),
         imsg('Planejar pessoal','Necessidade de pessoal: 1 operador de trator para o 2º turno de outubro · entra no plano de pessoas ao publicar o cenário.','users','Registrar a necessidade de pessoal'),
         msgbtn('Publicar cenário 2º turno + aluguel','Cenário publicado para a Programação e o Orçamento · não contrata nem compra: a cotação segue em Solicitações e cotações · a agenda real só muda na programação.',primary=True)],g_cen)
      + section('Máquinas agora e na programação','Confira condição, ocupação e elegibilidade separadas: apto não é livre, livre não é elegível.','',
        f'<div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px;">{tag("Livres e aptas 1")}{tag("Operando 1")}{tag("Reservadas 2")}{tag("Com restrição 1")}{tag("Indisponíveis 1")}{tag("A confirmar 1")}</div>'
        f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px;">{cards}</div>'
        + '<div style="height: 8px;"></div>'
        + _nota('Contadores são recortes que se sobrepõem — não somam o total da frota. Última atualização 07:42 · fonte: PCM + eventos da operação.'),state='gray')
      + _painel_manut('g_mi3')
    )
    shell37('PL-03','Capacidade e recursos',corpo,
      subtitle='Carga herdada do plano contra capacidade líquida; déficits com plano de atendimento e quadro compartilhado de máquinas.',
      status=('Déficit 270 h em tratores','red'),
      footer='Uma máquina não ocupa duas frentes no mesmo horário; manutenção não é descontada duas vezes (RECURSO-01 a 10).')

    # ================= PL-04 · Programação integrada (janela 8.6) =================
    HEIGHTS37['PL-04.dc.html']=2050
    OPER=['Marcos','Beto','Carlos','João','Nilton']
    CONJ=['Pulv. 02 + Trator 03','Pulv. 01 + Trator 02','Trator T1 + Plantadeira 24 linhas','Trator 02 + Plantadeira 24 linhas','Pivô 1','Pivô 2','Gotejo T7','Oficina Sede']
    O=lambda i,sub: [B(i),BR(),MU(sub)]
    ords=[
      R('o421',dict(os='OS-0421',jan='24–26/09',rec='Pulv. 02 + Trator 03',oper='Marcos',dur='3 turnos',mat='em custódia ✓',etp='Em execução'),
        p=dict(os=O('OS-0421','fungicida T1+T2'),jan=[TX('24–26/09'),BR(),MU(f'dias 5–7 · saldo {OS421["saldo"]} ha')],sel=[CH(OS421['selo'],'yellow')],etp=[CH('Em execução','green')],ab=[LK('Abrir O.S.','OS.dc.html')])),
      R('o430',dict(os=OS_DES['id'],jan='25/09',rec='Pulv. 01 + Trator 02',oper='Beto',dur='2 turnos',mat='separado ✓',etp='A liberar',sel='—'),
        p=dict(os=O(OS_DES['id'],'dessecação T1-A'),jan=[TX('25/09'),BR(),MU('DAP −20')],etp=[CH('A liberar','gray')],ab=[LK('Abrir O.S.','OS.dc.html')])),
      R('o431',dict(os=OS_DEMO17['id'],jan='24/09 06:00',rec='Trator T1 + Plantadeira 24 linhas',oper='Carlos',dur='2 turnos',mat='sementes previstas',etp='A liberar'),
        p=dict(os=O(OS_DEMO17['id'],'plantio T2'),sel=[CH('Impedida · ativo bloqueado','red')],etp=[CH('A liberar','gray')],ab=[CT('Resolver impedimento','PL-05det.dc.html',True)])),
      R('o419',dict(os='OS-0419',jan='hoje 20:00–amanhã 10:31',rec='Pivô 2',oper='João',dur='14,5 h (1 volta a 62 %)',mat='sem insumo · sem requisição',etp='Liberadas',sel='—'),
        p=dict(os=O('OS-0419','água Pivô 2'),etp=[CH('Liberadas','green')],ab=[LK('Abrir na Irrigação','IR-03det.dc.html')])),
      R('o418',dict(os='OS-0418',jan='24/09 21:00–25/09 11:15',rec='Pivô 1',oper='João',dur='14,3 h',mat='requisição na liberação',etp='A liberar'),
        p=dict(os=O('OS-0418','fertirrigação P1'),sel=[CH('Falta insumo · Ureia 45%','red')],etp=[CH('A liberar','gray')],ab=[LK('Abrir O.S.','OS.dc.html#OS-0418')])),
      R('o422',dict(os='OS-0422',jan='a definir',rec='Pivô 2',oper='João',dur='2 passadas · 18,1 h',mat='sem insumo',etp='A liberar'),
        p=dict(os=O('OS-0422','água Pivô 2 · próximo ciclo'),sel=[CH('Janela a definir','yellow')],etp=[CH('A liberar','gray')],ab=[LK('Abrir na Irrigação','IR-03.dc.html')])),
      R('o423',dict(os='OS-0423',jan='hoje 14:00–16:00',rec='Gotejo T7',oper='João',dur='2 h',mat='sem insumo',etp='A liberar'),
        p=dict(os=O('OS-0423','água gotejo T7'),sel=[CH('Conflito · parada da B3','red')],etp=[CH('A liberar','gray')],ab=[LK('Abrir na Irrigação','IR-03.dc.html')])),
      R('om233',dict(os='OM-0233',jan='hoje',rec='Oficina Sede',oper='Nilton',dur='8 h',mat='peça entregue ✓',etp='Em execução',sel='—'),
        p=dict(os=O('OM-0233','reparo Trator T1'),jan=[TX('hoje'),BR(),MU('oficina')],etp=[CH('Em execução','green')],ab=[LK('Abrir O.M.','MA.dc.html#om=OM-0233')])),
    ]
    SELC={'Conflito · parada da B3':('Conflito','parada da B3 14:00–15:00')}
    for r in ords:   # duração sob a janela, operador sob o conjunto, selo curto com detalhe (sem rolagem lateral)
        v_,p_=r['v'],r['p']; p_['jan']=(p_.get('jan') or [TX(v_['jan'])])+[BR(),MU(v_['dur'])]; p_['rec']=[TX(v_['rec']),BR(),MU(v_['oper'])]
        for k_ in ('jan','rec'): r['s'][k_]=' '.join(x['t'] for x in p_[k_] if x['k']!='br')
        sl=p_.get('sel')
        if sl and sl[0]['t'] in SELC: a_,b_=SELC[sl[0]['t']]; p_['sel']=[CH(a_,'red'),BR(),MU(b_)]
        p_['etp']=p_['etp']+[BR(),MU(v_['mat'])]; r['s']['etp']=v_['etp']+' '+v_['mat']
    g_ord=grid([dict(k='os',l='Ordem',w=150),dict(k='jan',l='Janela · duração',w=140),dict(k='rec',l='Conjunto · operador',w=190),
                dict(k='sel',l='Impedimento · selo',w=200),dict(k='etp',l='Etapa · material',w=180),dict(k='ab',l='Abrir',w=180)],ords,
       edit=dict(m='form',title='Programar',sub='Ajuste janela, conjunto e operador. Programar não libera: a liberação é comando separado e revalida prontidão.',
                 fields=[dict(k='os',l='Ordem',ro=True),dict(k='jan',l='Janela',req=True),dict(k='rec',l='Recurso/conjunto',t='sel',opts=CONJ,req=True),
                         dict(k='oper',l='Operador',t='sel',opts=OPER,req=True),dict(k='dur',l='Duração',req=True),dict(k='etp',l='Etapa',ro=True,help='A etapa muda pelas ações da ordem, nunca pela edição.')]),
       search=True,total=False,gid='g_ord')
    g_maq=grid([dict(k='maq',l='Máquina',w=190),dict(k='cond',l='Condição',w=230),dict(k='ocup',l='Ocupação no período',w=330),dict(k='eleg',l='Elegibilidade',w=300)],[
        R('mf',dict(maq='Trator 02 · MF 7719',ocup=f'livre hoje · 25/09 {OS_DES["id"]} · 28/09 preventiva OM-0234'),p=dict(cond=[CH('Apta','green')],eleg=[CH(SUBST,'yellow')])),
        R('t3',dict(maq='Trator 03 · JD 6M',ocup='operando OS-0421 até 26/09',eleg='—'),p=dict(cond=[CH('Apta','green')])),
        R('t1',dict(maq='Trator T1 · JD 6M 155',ocup='oficina OM-0233 · retorno previsto 14h, não confirmado',eleg='não ofertado'),p=dict(cond=[CH('Indisponível · bloqueado pelo PCM','red')])),
        R('p1',dict(maq='Pulverizador 01',ocup=f'reservado {OS_DES["id"]} 25/09',eleg='elegível sob condição validada'),p=dict(cond=[CH('Apta com restrição','yellow')])),
      ],edit=dict(m='ro',title='Máquina',fields=[dict(k='maq',l='Máquina',ro=True),dict(k='ocup',l='Ocupação no período',ro=True)]),search=False,total=False,gid='g_maq')
    g_pen=grid([dict(k='os',l='Ordem',w=180),dict(k='etp',l='Etapa'),dict(k='sel',l='Selo',w=200),dict(k='pen',l='Pendência',w=330),dict(k='ab',l='Ação',w=150)],[
        R('p417',dict(os='OS-0417 · cobertura P1',pen=f'{D.REQ["custodia"]} sc 50 kg de MAP 11-52 sob custódia de Paula · REQ-031'),
          p=dict(os=[B('OS-0417'),TX('· cobertura P1')],etp=[CH('Em conferência','yellow')],sel=[CH('Sobras a receber','yellow')],ab=[CT('Receber devolução','EST.dc.html')])),
        R('p420',dict(os='OS-0420 · plantio T4',pen=f'saldo {OS420["saldo"]} ha · substituto Trator 02 proposto · aguarda PCP'),
          p=dict(os=[B('OS-0420'),TX('· plantio T4')],etp=[CH('Em execução','green')],sel=[CH('Impedida · ativo bloqueado','red')],ab=[LK('Ver impedimento','PL-05.dc.html')])),
      ],edit=dict(m='ro',title='Pendência',fields=[dict(k='os',l='Ordem',ro=True),dict(k='pen',l='Pendência',ro=True)]),search=False,total=False,gid='g_pen')
    corpo=(
      toolrow(f'<span style="font-size: 13px; font-weight: 700; white-space: nowrap;">Período de trabalho</span>'
              + seg(['Hoje','Próximos 7 dias','Próximos 14 dias'],1)
              + f'<span style="font-size: 12.5px; color: {MUTED}; white-space: nowrap;">23/09 → 29/09 · fuso da fazenda</span>')
      + '<div style="height: 12px;"></div>'
      + kpis([('JÁ EMITIDAS','8','7 O.S. + 1 O.M.'),('NOVAS ELEGÍVEIS','5','prévia de emissão'),('AGUARDANDO DADOS','2','sem previsão confirmada'),('FORA DO PERÍODO','1','não entra na fila')])
      + section('Ordens do período 23–29/09','Prepare, programe e libere em passos separados; clique na ordem para ajustar janela, conjunto e operador.',
        [imsg('Preparar O.S. do período','Prévia: 13 ocorrências no período · 8 já com ordem (recuperadas, sem duplicar) · 5 novas propostas · 2 aguardando dados · itens impedidos não são emitidos como executáveis.','doc','Montar a prévia de emissão do período'),
         imsg('Conferir prontidão',f'Prontidão A liberar: {OS_DES["id"]} pronta (material separado) · Ana (agrônoma) libera · OS-0418 a liberar pelo agrônomo · Ureia sem saldo apto · {OS_DEMO17["id"]} impedida por ativo bloqueado · OS-0422 sem janela e OS-0423 em conflito com a parada da B3 (água não passa pelo agrônomo). Material previsto não significa disponível físico.','check','Conferir prontidão das ordens A liberar'),
         msgbtn('Liberar prontas',f'Liberada 1 de 5 A liberar — {OS_DES["id"]} ✓ liberada por Ana (agrônoma) · OS-0418 continua: Ureia 45 % sem saldo apto (0 kg) · {OS_DEMO17["id"]} continua: ativo bloqueado · OS-0422 continua: janela a definir · OS-0423 continua: conflito com a parada da B3. Resultado por item; versão e prontidão revalidadas.',primary=True)],
        g_ord)
      + section('Máquinas na programação','Confira condição, ocupação e elegibilidade separadas antes de programar.',
        [ilnk('Ver capacidade','SAF.dc.html#saf=S2627&passo=operacoes','grid','Abrir a capacidade por mês da Safra 2026/27 em Planejar safra')],g_maq,state='gray')
      + section('Pendências de outros períodos','Resolva as obrigações que continuam abertas; avançar a janela não esconde nada.','',g_pen,state='yellow')
      + _painel_manut('g_mi4')
    )
    EXTRAJS[0]=JS_COMUM+r'''
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_ord'||!r) return; const nr=g2clone(rows); const x=g2find(nr,r.id);
    x.p.jan=[{k:'txt',t:x.v.jan},{k:'br',t:''},{k:'mut',t:x.v.dur}]; x.p.rec=[{k:'txt',t:x.v.rec},{k:'br',t:''},{k:'mut',t:x.v.oper}];
    x.s.jan=x.v.jan+' '+x.v.dur; x.s.rec=x.v.rec+' '+x.v.oper; g2set(self,gid,{rows:nr,fl:x.id});
    self.setState({g2toast:'Programação de '+x.v.os+' salva · '+x.v.jan+' · '+x.v.rec+' · liberar continua sendo comando separado'}); };
}'''
    shell37('PL-04','Programação integrada',corpo,
      subtitle='Janela móvel de emissão e liberação: o plano projeta tudo, a janela emite pouco e libera menos.',
      status=('1 pronta · 4 com impedimento','yellow'),
      footer='DAP/DAC/calendário mostram âncora prevista ou real; mudança recalcula apenas saldo futuro e o agrônomo ajusta ao liberar, onde cabível (JANELA-01 a 10).')

    # ================= PL-05 · Impedimentos e reprogramação =================
    HEIGHTS37['PL-05.dc.html']=1080
    RESP=['PCP + PCM · Nilton','Suprimentos · Rui','PCP · Carlos','RH + PCP','Qualidade','Ana (agrônoma)']
    PZ=lambda f,d='': [{'k':'chip','t':f+(' · '+d if d else ''),'c':{'vence hoje':'red','até 3 dias':'yellow','no prazo':'green'}[f]}]
    imp=[
      R('i1',dict(causa='Ativo bloqueado',resp='PCP + PCM · Nilton',prazo='vence hoje',alt='substituir por Trator 02 · MF 7719',apr='conservada · conteúdo técnico não mudou'),
        p=dict(causa=[CH('Ativo bloqueado','red')],orig=[TX('Trator T1 · OM-0233'),BR(),MU('pressão hidráulica baixa')],
               afet=[TX(f'{OS_DEMO17["id"]} (antes do 1º início)'),BR(),TX(f'OS-0420 (saldo {OS420["saldo"]} ha)')],imp=[TX(f'{OS_DEMO17["area"]} ha plantio T2'),BR(),TX(f'{OS420["saldo"]} ha plantio T4')],
               alt=[TX('substituir por Trator 02 · MF 7719'),BR(),CH(SUBST,'yellow')],prazo=PZ('vence hoje'),ab=[CT('Propor substituição','PL-05det.dc.html',True)])),
      R('i2',dict(causa='Falta de insumo',resp='Suprimentos · Rui',prazo='no prazo',alt=f'atender a NEC-028 com as {t(PC88["apto"])} aptas',apr='—'),
        p=dict(causa=[CH('Falta de insumo','yellow')],orig=[TX(f'{PC88["id"]} · {PC88["item"]}'),BR(),MU(f'{t(PC88["a_entregar"])} a entregar em {PC88["previsao"][:5]}')],
               afet=[TX(f'NEC-028 · plantio T4 (saldo {OS420["saldo"]} ha)'),BR(),TX('cobertura da soja · DAP +20')],
               imp=[TX(f'{_n(KCL_T4,1)} t para o saldo do T4'),BR(),MU('cobertura a partir de 04/11')],
               alt=[TX(f'atender a NEC-028 com as {t(PC88["apto"])} aptas'),BR(),MU(f'{t(PC88["quarentena"])} em quarentena · {t(PC88["a_entregar"])} para a cobertura')],
               prazo=PZ('no prazo',PC88['previsao'][:5]),ab=[LK('Ver pedido','CMP.dc.html')])),
      R('i3',dict(causa='Chuva na janela',resp='PCP · Carlos',prazo='até 3 dias',alt='manter 25/09 · contingência 28/09',apr='revalidação se mudar requisito'),
        p=dict(causa=[CH('Chuva na janela','yellow')],orig=[TX('previsão 26–27/09')],afet=[TX(f'{OS_DES["id"]} (dessecação T1-A)')],imp=[TX('risco na janela DAP −20')],
               prazo=PZ('até 3 dias'),ab=[LK('Ver na programação','PL-04.dc.html')])),
      R('i4',dict(causa='Pessoas',resp='RH + PCP',prazo='no prazo',alt='2º turno com contratação',apr='—'),
        p=dict(causa=[CH('Pessoas','yellow')],orig=[TX('operador noturno em férias a partir de 28/09')],afet=[TX('plantio T1-B (previsto 25/10)')],imp=[TX('2º turno de outubro sem operador')],
               prazo=PZ('no prazo'),ab=[LK('Ver capacidade','SAF.dc.html#saf=S2627&passo=operacoes')])),
      R('i5',dict(causa='Qualidade',resp='Qualidade',prazo='até 3 dias',alt='reprocesso ou desconto',apr='decisão da qualidade'),
        p=dict(causa=[CH('Qualidade','yellow')],orig=[TX(f'INSP-88 · lote {D.LOTE_BLOQ["id"]}')],afet=[TX('expedição do lote')],imp=[TX(f'{_n(D.LOTE_BLOQ["sc"])} sc bloqueados')],
               prazo=PZ('até 3 dias','25/09'),ab=[LK('Resolver origem','CO-06.dc.html')])),
    ]
    for r in imp:   # origem sob a causa, impacto sob os afetados, aprovação sob a alternativa (sem rolagem lateral)
        p_=r['p']; p_['causa']=p_['causa']+[BR()]+[MU(x['t']) if x['k']!='br' else x for x in p_.pop('orig')]
        p_['afet']=p_['afet']+[BR()]+[MU(x['t']) if x['k']!='br' else x for x in p_.pop('imp')]
        p_['alt']=(p_.get('alt') or [TX(r['v']['alt'])])+([BR(),MU('aprovação: '+r['v']['apr'])] if r['v']['apr']!='—' else [])
        for k_ in ('causa','afet','alt'): r['s'][k_]=' '.join(x['t'] for x in p_[k_] if x['k']!='br')
    g_imp=grid([dict(k='causa',l='Causa · origem',w=170),dict(k='afet',l='Afetados · impacto',w=210),dict(k='resp',l='Responsável',w=140),
                dict(k='prazo',l='Prazo',w=130,chips={'vence hoje':'red','até 3 dias':'yellow','no prazo':'green'}),dict(k='alt',l='Alternativa · aprovação',w=240),dict(k='ab',l='Ação',w=170)],imp,
       edit=dict(m='form',title='Impedimento',sub='Nomeie o dono, o prazo e a alternativa. Resolver reavalia prontidão; não libera restrição técnica nem muda a agenda.',
                 fields=[dict(k='causa',l='Causa',ro=True),dict(k='resp',l='Responsável',t='sel',opts=RESP,req=True),
                         dict(k='prazo',l='Prazo',t='sel',opts=['vence hoje','até 3 dias','no prazo'],req=True),dict(k='alt',l='Alternativa',req=True),dict(k='apr',l='Aprovação',ro=True)]),
       search=True,total=False,gid='g_imp')
    corpo=(
      kpis([('IMPEDIMENTOS ABERTOS','5','fila única'),('ORDENS AFETADAS','3','+ 2 itens do plano · 1 lote'),('VENCEM HOJE','1','com dono nomeado'),('ÁREA PARADA','172 ha','102 + 70 ha, sem dupla contagem')])
      + section('Fila única de impedimentos','Trate cada impedimento com dono, prazo e alternativa; clique na linha para ajustá-los.',
        [imsg('Notificar responsáveis','Notificados 5 donos · alertas do mesmo impedimento agrupados num caso único (simulado · nenhuma mensagem real enviada).','users','Avisar os donos dos impedimentos abertos')],g_imp,state='red')
      + section('O que resolver faz — e não faz','Reprograme só o saldo futuro; o realizado e as aprovações ficam preservados.',
        [idrw('Reprogramar saldo',dict(title='Reprogramar saldo',sub='somente o saldo; realizado e aprovações preservados',
            fields=[('Ordem','OS-0420 · plantio T4'),('Saldo','70 ha'),('Data','26/09/2026'),('Máquina','Trator 02 · MF 7719'),('Motivo','Substituição do ativo bloqueado')],
            confirm='Reprogramar saldo',done='Saldo reprogramado · aguarda nova liberação'),'calendar','Reprogramar o saldo da OS-0420'),
         imsg('Aprovar proposta','Proposta de substituição aprovada · a alocação é confirmada na tela do impedimento; nada inicia automaticamente.','check','Aprovar a proposta de substituição')],
        _nota(f'Resolver compra ou manutenção revalida prontidão; não inicia máquina nem muda a agenda automaticamente. '
              f'A liberação técnica do ativo após teste válido não reassume a agenda antiga — o PCP reconfirma o saldo necessário. '
              f'A adubação pós-colheita do C1 (NEC-019) não entra nesta fila: aguarda a decisão da pendência no plano operacional, sem compra.',state='yellow'),state='yellow')
    )
    EXTRAJS[0]=JS_COMUM+r'''
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_imp'||!r) return; const nr=g2clone(rows); const x=g2find(nr,r.id);
    x.p.alt=[{k:'txt',t:x.v.alt}].concat(x.v.apr&&x.v.apr!=='—'?[{k:'br',t:''},{k:'mut',t:'aprovação: '+x.v.apr}]:[]); x.s.alt=x.v.alt;
    g2set(self,gid,{rows:nr,fl:x.id}); self.setState({g2toast:'Impedimento atualizado · dono '+x.v.resp+' · prazo '+x.v.prazo+' · prontidão reavaliada, nada liberado'}); };
}'''
    shell37('PL-05','Impedimentos e reprogramação',corpo,
      subtitle='Fila única de faltas, chuva, ativo, técnica, pessoas, qualidade e integração — propostas lado a lado.',
      status=('1 vence hoje','red'),
      footer='Impedimento tem dono e prazo; o selo fica na ordem (nunca vira etapa do Kanban).')

    # ---- PL-05det · impedimento com substituição (DEMO-17) ----
    HEIGHTS37['PL-05det.dc.html']=1260; PARENT37['PL-05det.dc.html']='PL-05.dc.html'
    prop=(f'<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">'
      f'<div style="border: 1px solid {ACC}; background: {ACCS}; border-radius: 12px; padding: 12px 14px;">'
      f'<div style="font-size: 11px; font-weight: 700; color: {ACC}; letter-spacing: .06em;">A · SUBSTITUIR POR TRATOR 02 · MF 7719</div>'
      f'<div style="font-size: 13px; margin-top: 6px; line-height: 1.6;">{chip("Apta","green")} {chip("Livre 24/09","green")} {chip("Proposto · aguarda PCP","yellow")}<br>'
      f'Mesma classe e implemento compatível → <b>sem ajuste técnico</b>; o agrônomo só libera de novo<br>Início mantido: 24/09 06:00 · custo estimado +R$ 0,9 mil (deslocamento)<br>'
      f'Uso limitado até 27/09: preventiva 250 h em 28/09 (OM-0234)</div></div>'
      f'<div style="border: 1px solid {LINE}; border-radius: 12px; padding: 12px 14px;">'
      f'<div style="font-size: 11px; font-weight: 700; color: {MUTED}; letter-spacing: .06em;">B · AGUARDAR REPARO DO TRATOR T1</div>'
      f'<div style="font-size: 13px; margin-top: 6px; line-height: 1.6;">{chip("Retorno previsto 14h — aguardando teste","yellow")}<br>'
      f'Capacidade provisória, <b>não confirmada</b><br>Risco: perder 1 dia da janela de plantio · teste reprovado mantém o bloqueio</div></div>'
      f'<div style="border: 1px solid {LINE}; border-radius: 12px; padding: 12px 14px;">'
      f'<div style="font-size: 11px; font-weight: 700; color: {MUTED}; letter-spacing: .06em;">C · TERCEIRIZAR PLANTIO</div>'
      f'<div style="font-size: 13px; margin-top: 6px; line-height: 1.6;">Prestador disponível 26/09 · custo estimado +R$ 4,2 mil<br>Exige contrato ativo e conferência do padrão de plantio<br>2 dias além do plano</div></div></div>')
    corpo=(
      continuity('Inspeção bloqueou o Trator T1',f'{OS_DEMO17["id"]} voltou para A liberar','alocação substituta e nova liberação','Confirmar substituição')
      + section('O impedimento','Confira a ordem afetada e o efeito do bloqueio antes do primeiro início.','',
        _ficha([
          ('Ordem afetada',f'<b>{OS_DEMO17["id"]}</b> · {esc(OS_DEMO17["tipo"])} · {OS_DEMO17["talhao"]} · {OS_DEMO17["area"]} ha · janela {OS_DEMO17["janela"]}'),
          ('Causa',f'{chip("Ativo bloqueado pelo PCM","red")} Pressão hidráulica baixa · inspeção de manutenção · caso OM-0233'),
          ('Efeito na etapa','Retirada de <b>Liberadas</b> para <b>A liberar</b> · nenhum início registrado'),
          ('Instrução técnica',chip('Conservada · v1','green')+' Ana (agrônoma) libera de novo, sem mudar o conteúdo'),
          ('Dono e prazo','PCP (alocação) + PCM (reparo, Nilton) · decidir hoje'),
          ('Outra ordem no mesmo ativo',f'OS-0420 · plantio T4 · em execução · saldo {OS420["saldo"]} ha · substituto Trator 02 proposto, aguarda PCP'),
        ]))
      + section('Propostas lado a lado','Compare as três saídas; a simulação não bloqueia a agenda real até confirmar.','',prop)
      + section('Decisão','Confirme a substituição; a nova liberação é um passo separado, na Programação.','',
        _acoes(msgbtn('Confirmar substituição pelo Trator 02',f'Alocação substituta confirmada · Trator 02 passa a Comprometido · {OS_DEMO17["id"]} · prontidão reavaliada · a ordem segue A liberar até Ana (agrônoma) liberar de novo. Se o equipamento alterasse a aplicação, ela ajusta ao liberar.',primary=True),
               imsg('Aguardar reparo','Registrado: aguardar o teste das 14h · o bloqueio permanece até liberação técnica após teste válido · liberar o ativo não reassume a agenda antiga.','clock','Manter a ordem aguardando o reparo do Trator T1'),
               idrw('Terceirizar',dict(title='Reprogramar com prestador',sub='apenas a agenda; versão executada permanece intacta',
                   fields=[('Ordem',OS_DEMO17['id']),('Data','26/09/2026'),('Responsável','Prestador · plantio terceirizado'),('Motivo','Ativo bloqueado sem substituto interno')],
                   confirm='Reprogramar',done='Reprogramada · responsáveis notificados (simulado)'),'truck','Reprogramar a ordem com prestador terceirizado'))
        + '<div style="height: 12px;"></div>'
        + _nota('A parada do Trator T1 reduz a capacidade da janela <b>uma única vez</b> (já refletida em Capacidade e recursos); o PCP não remove o bloqueio técnico do PCM.',state='yellow')))
    shell37('PL-05',f'Impedimento · {OS_DEMO17["id"]} ativo bloqueado',corpo,fname='PL-05det.dc.html',crumbs_extra=[OS_DEMO17['id']],
      subtitle='Bloqueio do PCM antes do início — substituição avaliada com condição, ocupação e elegibilidade separadas.',
      status=('Decidir hoje','red'),
      footer='DEMO-17 · Apto ≠ livre ≠ elegível (44.11.1). Teste reprovado mantém o bloqueio; CMD-19 libera tecnicamente sem reassumir agenda; CMD-34 confirma a alocação.')

    # ================= PL-06 · Parcelas e escalonamento (cap. 43) =================
    HEIGHTS37['PL-06.dc.html']=1500
    mapa=(f'<div style="display: flex; gap: 12px; align-items: stretch; margin-bottom: 12px;">'
      f'<div style="flex: 1 1 0; min-width: 0;">{_mapa_t1(300)}</div>'
      f'<div style="width: 340px; flex-shrink: 0; display: flex; flex-direction: column; gap: 8px;">'
      f'<div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 12px; padding: 10px 12px; font-size: 12.5px; line-height: 1.6;">'
      f'<b>T1 · 312 ha</b> — proposta v2 de parcelamento<br>'
      f'T1-A · {T1A["area"]} ha · Soja {T1A["variedade"]} · plantio {_br(T1A["plantio"])[:5]}<br>T1-B · {T1B["area"]} ha · Soja {T1B["variedade"]} · plantio {_br(T1B["plantio"])[:5]}<br>'
      f'<div style="display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px;">{chip("Soma 312 ha = talhão ✓","green")}{chip("Sem sobreposição ✓","green")}</div></div>'
      f'<div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 12px; padding: 10px 12px; font-size: 12.5px; line-height: 1.6;">'
      f'{chip("Proposta · não divide a área vigente","yellow")}<br>Parcelas não duplicam hectares de cobrança (312 ha); operações e materiais seguem a parcela correta.</div></div></div>')
    par=[
      R('pA',dict(par='T1-A',geo='polígono norte',area=T1A['area'],ciclo='Safra 2026/27 · soja',var=T1A['variedade'],plant=T1A['plantio'],col=JAN(COL_A),prep=f'dessecação 25/09 ({OS_DES["id"]})'),
        p=dict(par=[B('T1-A')],sit=[CH('Proposta v2','yellow')])),
      R('pB',dict(par='T1-B',geo='polígono sul',area=T1B['area'],ciclo='Safra 2026/27 · soja',var=T1B['variedade'],plant=T1B['plantio'],col=JAN(COL_B),prep='dessecação 05/10'),
        p=dict(par=[B('T1-B')],sit=[CH('Proposta v2','yellow')])),
      R('pT3',dict(par='T3',geo='talhão inteiro',area=96,ciclo='Safra 2026/27 · soja após milho',var='62 X',plant=CULT['T3']['plantio'],col='—'),
        p=dict(par=[B('T3')],prep=[CH('Palhada · liberação pendente','yellow')],sit=[CH('Aguarda liberação','gray')])),
      R('pP1',dict(par='P1',geo='pivô 1',area=95,ciclo='Feijão R5 → soja',var='58 W',plant=CULT['P1']['plantio'],col='feijão 20–30/10',prep='—'),
        p=dict(par=[B('P1')],sit=[CH('Vigente','green')])),
    ]
    for r in par: r['p']['par']=[B(r['v']['par']),BR(),MU(r['v']['geo'])]; r['s']['par']=r['v']['par']+' '+r['v']['geo']
    g_par=grid([dict(k='par',l='Parcela · geometria',w=130),dict(k='area',l='Área',t='num',a='r',u='ha'),dict(k='ciclo',l='Ciclo e ocupação',w=180),
                dict(k='var',l='Variedade'),dict(k='plant',l='Plantio próprio',t='date'),dict(k='col',l='Janela de colheita',w=140),dict(k='prep',l='Preparo/limpeza',w=220),dict(k='sit',l='Situação',w=200)],par,
       edit=dict(m='form',title='Parcela',sub=f'Ajuste variedade e plantio. A janela de colheita é recalculada: plantio + {CICLO} dias (plano Soja alta tecnologia), ±5 dias.',
                 fields=[dict(k='par',l='Parcela',ro=True),dict(k='area',l='Área',t='num',u='ha',ro=True,help='Mudar a área exige nova geometria: use Simular parcelas.'),
                         dict(k='var',l='Variedade',t='sel',opts=['58 W','62 X'],req=True),dict(k='plant',l='Plantio próprio',t='date',req=True),
                         dict(k='col',l='Janela de colheita',ro=True),dict(k='prep',l='Preparo/limpeza')]),
       search=False,total=False,gid='g_par')
    semr=[]
    for i,(s_,o,d) in enumerate(zip(SEMANAS,OFERTA,DEMANDA)):
        if not o: continue
        pa='T1-A' if i<3 else 'T1-B'; pr=T1A if i<3 else T1B
        semr.append(R(f's{i}',dict(sem=s_,of=o,dem=d,sal=o-d,cap=SECAGEM),p=dict(sal=[CH(f'+{_n(o-d)} sc → armazém','green')]),
                      o=[dict(t=f'Oferta: {pa} {pr["area"]} ha × {pr["meta"]} sc/ha = {_n(pr["area"]*pr["meta"])} sc ÷ 2 semanas da janela'),
                         dict(t=f'Entregas contratadas na semana: {_n(d)} sc',h='CO-06.dc.html'),dict(t=f'Capacidade de colheita/secagem: {_n(SECAGEM)} sc/semana')]))
    g_sem=grid([dict(k='sem',l='Semana'),dict(k='of',l='Oferta',t='num',a='r',u='sc',agg='sum'),dict(k='dem',l='Entregas contratadas',t='num',a='r',u='sc',agg='sum'),
                dict(k='sal',l='Saldo',w=190),dict(k='cap',l='Capacidade colheita/secagem',t='num',a='r',u='sc/semana')],semr,
       edit=dict(m='origin',title='Semana',fields=[dict(k='sem',l='Semana',ro=True),dict(k='of',l='Oferta',t='num',u='sc',ro=True),dict(k='dem',l='Entregas contratadas',t='num',u='sc',ro=True)]),
       search=False,total=True,gid='g_sem')
    corpo=(
      section('Mapa e parcelas do talhão','Divida o talhão com soma e sobreposição validadas; clique na parcela para ajustar variedade e plantio.',
        [idrw('Simular parcelas',dict(title='Simular parcelamento',sub='Divida o talhão em quantas parcelas precisar; soma, sobreposição e histórico são validados. No Planejar safra, use Dividir em parcelas.',
            fields=[('Talhão','T1 · 312 ha'),('Número de parcelas','2'),('Variedade A',f'Soja 58 W · {T1A["area"]} ha'),('Variedade B',f'Soja 62 X · {T1B["area"]} ha'),('Data','25/10/2026')],
            confirm='Simular',done='Cenário v2 simulado · área vigente intacta'),'layers','Simular nova divisão do talhão'),
         imsg('Comparar cenários',f'v1 (plantio único 15/10): pico de {_n((_A+_B)//2)} sc/semana, acima da secagem de {_n(SECAGEM)} · v2 (T1-A 15/10, T1-B 25/10): pico de {_n(max(OFERTA))} sc/semana, dentro da capacidade.','trend','Comparar plantio único com plantio escalonado')],
        mapa + g_par)
      + section('Curva semanal · oferta × demanda · soja T1',f'Confira se a oferta de cada semana cabe nas entregas e na secagem; clique na semana para ver a origem.',
        [f'<span style="font-size: 12px; color: {MUTED};">meta {META_A} e {META_B} sc/ha {tag("hipótese")}</span>'],
        _curva()
        + f'<div style="display: flex; gap: 16px; font-size: 12px; color: {MUTED}; margin: 4px 0 10px 56px;"><span><b style="color:{ACC};">■</b> oferta T1-A</span><span><b style="color:#1E6FB8;">■</b> oferta T1-B</span><span><b style="color:{YEL};">━</b> entregas contratadas</span><span><b style="color:{RED};">┅</b> capacidade de colheita/secagem</span></div>'
        + g_sem)
    )
    EXTRAJS[0]=JS_COMUM+r'''
function EXTRAVALS(self,v){
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_par'||!r||!/^\d{4}-\d{2}-\d{2}$/.test(String(r.v.plant))||(r.id!=='pA'&&r.id!=='pB')) return;
    const nr=g2clone(rows); const x=g2find(nr,r.id); const a=String(x.v.plant).split('-'); const c=new Date(+a[0],+a[1]-1,+a[2]+%d);
    const i=new Date(c); i.setDate(c.getDate()-5); const f=new Date(c); f.setDate(c.getDate()+5);
    x.v.col=pl_dm(i)+'–'+pl_dm(f); x.s.col=x.v.col; if(x.p) delete x.p.col;
    g2set(self,gid,{rows:nr,fl:x.id}); self.setState({g2toast:'Parcela '+x.v.par+' salva · colheita recalculada para '+x.v.col+' · curva semanal revalidada ao publicar'}); };
}'''.replace('%d',str(CICLO))
    shell37('PL-06','Parcelas e escalonamento',corpo,
      subtitle='Parcelas com variedade e data próprias escalonam a colheita para caber na demanda e na capacidade.',
      status=('Proposta v2 aguardando aprovação','yellow'),primary='Publicar parcelamento e plano',
      footer='Dividir área valida soma, sobreposição e histórico; replantio respeita a liberação física da parcela (cap. 43, PARC).')
