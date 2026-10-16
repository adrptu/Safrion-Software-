# -*- coding: utf-8 -*-
"""Suprimentos › Estoque — processo em 6 etapas numa só tela de trabalho (EST.dc.html).
1 Confira recebimentos → 2 Entregue por O.S. → 3 Receba devoluções → 4 Confira saldos → 5 Faça contagens → 6 Acompanhe movimentos.
Saldos, lotes, reservas, requisições, entregas, devoluções, contagens e movimentos vêm do cenário compartilhado (cenario.js/cenario.py,
o mesmo estado das telas O.S. e App) e só mudam por cenMudar. Os registros de base (notas, pedidos, contagens antigas) vêm de dados2.
Funções próprias da tela que mexem no cenário têm prefixo est (estReceber, estEntregar, estContar, estRecontar, estAprovar, estCausa)."""
import json
from engine import (grid,esc,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,DISP,BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, secoes_state, HEIGHTS37
import ui37
import dados2 as D2
import cenario

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
NOMES=['Confira recebimentos','Entregue por O.S.','Receba devoluções','Confira saldos','Faça contagens','Acompanhe movimentos']

# ---------------- constantes locais (coerentes com dados2/cenário) ----------------
LOCAIS=['Galpão 1','Galpão 2','Câmara fria','Almox. defensivos','Packing']   # Packing: caixas do beneficiamento (CX26-01, NF 7731 · BEN-D23)
LOCAL_REC={'KCl 60%':'Galpão 2','Semente de soja 58 W':'Câmara fria','Semente de soja 62 X':'Câmara fria'}
PESSOAS=['Paula','Marcos','Carlos','João','Igor']   # Igor: quem executa a ordem de beneficiamento recebe as caixas no balcão (BEN-D13 → BEN-D23)
# mesma palavra para a mesma pessoa em toda a tela: Rui é o almoxarife que entrega e recebe (cenario.js) e também conta
# contador do inventário (revisão CONF F6): sem lista fixa; quem conta vem das pessoas ativas com o papel almoxarife (estContadores, JS)
CONDS=['Apta · volta ao disponível','Bloqueada para inspeção · vai para quarentena']
DIVS=['Sem divergência','Falta','Sobra','Avaria','Item diferente do pedido']
CAUSA_BASE={'INV-2609':'Sacaria rasgada na pilha 3'}
SEM_VALIDADE=['Fertilizantes','Corretivos','Embalagens']    # grupos recebidos sem validade de lote (caixa do packing: BEN-D23)
CONTADOR_BASE={'INV-2609':'Rui (almoxarife)','INV-2610':'Paula (almoxarife)'}
# O.S. impedida (selo "Impedida" no cenário): a ordem de manutenção que impede vem do registro da manutenção
IMPED={'OS-0420':dict(selo='O.S. impedida · OM-0233',
                      txt='OS-0420 impedida pela OM-0233 (Trator T1 bloqueado): entregue quando o ativo for liberado ou substituído na O.S.')}

def _forn(fid): return next((f['nome'] for f in D2.FORNECEDORES if f['id']==fid),fid)
# pedidos e notas que o Estoque recebe: os de Compras (dados2) e os de caixa do packing (dados_ben, BEN-D23: a compra de caixa é do BEN-2,
# por isso o pedido não vem de Compras e a linha não leva o atalho "Ver pedido")
def _pedidos():
    import dados_ben as DB
    return [dict(p,cmp=True) for p in D2.PEDIDOS]+[dict(p,cmp=False) for p in DB.PEDIDOS_CX]
def _notas():
    import dados_ben as DB
    return list(D2.RECEBIMENTOS)+list(DB.NFS_CX)
def _ped_label(p): return f"{p['id']} · {p['item']} · {_forn(p['f'])}"

def bloco(titulo,desc,corpo,acao=''):
    desc=''   # 13/10/2026 (proprietário: "reduza ou elimine todas essas descrições abaixo dos títulos ... somos minimalistas e essencialistas")
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{esc(titulo)}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>{acao}</div>'
            f'<div style="padding: 0 12px 12px;">{corpo}</div></section>')
def kline(hole):
    return f'<div style="font-size: 13px; color: {MUTED};">{H(hole)}</div>'
def navpe():
    lk=f'border: 0; background: transparent; color: {MUTED}; font-family: inherit; font-size: 12px; font-weight: 600; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; padding: 4px;'
    return (f'<div style="display: flex; align-items: center; gap: 10px; padding-top: 4px;">'
            f'<span style="flex-grow: 1;"></span>'
            f'<sc-if value="{H("est_rst_no")}" hint-placeholder-val="{H("true")}"><button type="button" onClick="{H("est_rst")}" style="{lk}">Restaurar demonstração</button></sc-if>'
            f'<sc-if value="{H("est_rst_ask")}" hint-placeholder-val="{F()}"><span style="font-size: 12px; color: {MUTED};">Volta O.S., estoque e app ao início da demonstração.</span>'
            f'<button type="button" onClick="{H("est_rst_ok")}" style="{_MINI} color: {RED}; border-color: {RED};">Restaurar</button><button type="button" onClick="{H("est_rst_cancel")}" style="{_MINI}">Manter</button></sc-if>'
            + '</div>')

def _dados_js():
    PS=_pedidos()
    peds=[dict(id=p['id'],item=p['item'],un=p['un'],grupo=p.get('grupo',''),forn=_forn(p['f']),a_entregar=p['a_entregar'],label=_ped_label(p),cmp=p['cmp']) for p in PS]
    recs=[]
    for r in _notas():
        p=next(x for x in PS if x['id']==r['pedido']); prev='previsto' in r['data']
        recs.append(dict(id='r'+r['id'].split()[-1],nf=r['id'],data=('previsto '+r['data'].split()[0]) if prev else r['data'],ped=_ped_label(p),forn=_forn(p['f']),item=r['item'],un=r['un'],
                         qtd_nf=r['qtd_nf'],conf=r['qtd_conf'],apto=r['apto'],quar=r['quarentena'],lote=r['lote'],val='',local=r.get('local') or LOCAL_REC.get(r['item'],'Galpão 2'),
                         div='Sem divergência',obs=('Laudo de umidade pendente' if r['quarentena'] else ''),ok=r['qtd_conf'] is not None))
    chave={l['lote']:l['item']+'|'+l['lote'] for l in D2.LOTES}
    conts=[dict(id=c['id'],key=chave[c['lote']],sis=(c['sistema'] if c['contado'] is not None else None),cont=c['contado'],
                contador=CONTADOR_BASE.get(c['id'],''),causa=CAUSA_BASE.get(c['id'],''),aj=None,hist=[]) for c in D2.CONTAGENS]
    return dict(hoje='/'.join(reversed(cenario.DIA_OP.split('-'))),pedidos=peds,recs=recs,contagens=conts,conds=CONDS,sem_validade=SEM_VALIDADE,imped=IMPED,locais=LOCAIS)

def build():
    fname='EST.dc.html'; E._reset_screen(fname)
    # ---------- etapa 1 · recebimentos (linhas: notas de base + recebimentos gravados no cenário) ----------
    ped_opts=[_ped_label(p) for p in _pedidos()]
    # larguras (w) contidas: pedido, item e situação quebram em linhas e a grade cabe em 1440 px sem rolagem horizontal
    # TABELAS-FOCO (5983172395): uma variável por coluna em todas as etapas; a unidade fica junto da quantidade ("60.000 kg"):
    # decisão do proprietário de 05/10/2026 (mais intuitivo; filtrar unidade não gera valor). O valor tipado (v) continua número para ordenar
    g_rec=grid([dict(k='nf',l='Nota fiscal',w=100),dict(k='data',l='Data da nota',t='date',w=110),dict(k='cfd',l='Conferida em',t='date',w=110),dict(k='ped',l='Pedido',w=110),dict(k='forn',l='Fornecedor',w=130),dict(k='item',l='Item',w=170),dict(k='lote',l='Lote'),
                dict(k='qtd_nf',l='Na nota',t='num',a='r'),dict(k='conf',l='Conferida',t='num',a='r'),dict(k='apto',l='Apta',t='num',a='r'),
                dict(k='quar',l='Quarentena',t='num',a='r'),dict(k='sit',l='Situação',w=150),dict(k='divg',l='Divergência',w=150),dict(k='vali',l='Validade',t='date')],
        [],edit=dict(m='form',title='Recebimento',newTitle='Registrar recebimento',sub='Confira a nota contra o pedido e o material. Só a parte apta entra no disponível.',
            fields=[dict(k='ped',l='Pedido',t='sel',opts=ped_opts,req=True,**{'def':ped_opts[0]}),
                    dict(k='nf',l='Nota fiscal',t='txt',req=True,help='Documento já lançado não cria segunda entrada.'),
                    dict(k='qtd_nf',l='Quantidade na nota',t='num',req=True,min=0.01,u='kg'),
                    dict(k='conf',l='Quantidade conferida',t='num',req=True,min=0,u='kg'),
                    dict(k='apto',l='Apta para uso',t='num',req=True,min=0,u='kg'),
                    dict(k='quar',l='Em quarentena',t='num',req=True,min=0,u='kg',help='Fica fora do disponível até a inspeção liberar.',**{'def':'0'}),
                    dict(k='lote',l='Lote',t='txt',req=True),
                    dict(k='val',l='Validade do lote',t='txt',live=True,help='Mês/ano (ex.: 06/2027). Lote vencido entra todo em quarentena.'),
                    dict(k='local',l='Local',t='sel',opts=LOCAIS,req=True,**{'def':'Galpão 2'}),
                    dict(k='div',l='Divergência',t='sel',opts=DIVS,req=True,**{'def':'Sem divergência'}),
                    dict(k='obs',l='Motivo da quarentena ou da divergência',t='area',help='Obrigatório quando houver quarentena ou divergência.')]),
        gid='g_rec',total=False,qf=dict(k='sit',cut=' · '))
    # ---------- etapa 2 · entregas por O.S. (uma linha por item de requisição) ----------
    g_ent=grid([dict(k='req',l='Requisição'),dict(k='os',l='O.S.'),dict(k='fase',l='Fase da O.S.'),dict(k='item',l='Item',w=170),dict(k='lote',l='Lote'),dict(k='emb',l='Embalagem',w=120),
                dict(k='sol',l='Solicitado',t='num',a='r'),dict(k='ent',l='Entregue',t='num',a='r'),dict(k='pend',l='A entregar',t='num',a='r',w=110),
                dict(k='pk',l='A entregar em embalagens',w=150),dict(k='sit',l='Situação',w=170),dict(k='det',l='Detalhe',w=230)],
        [],edit=dict(m='form',title='Entrega',sub='',
            fields=[dict(k='lote',l='Lote reservado',t='txt',ro=True),dict(k='qtd',l='Quantidade a entregar',t='num',req=True,min=0.001),
                    dict(k='quem',l='Entregar a',t='sel',opts=PESSOAS,req=True)]),
        gid='g_ent',total=False,qf=dict(k='sit',cut=' · '))
    # ---------- etapa 3 · custódia e devoluções ----------
    g_dev=grid([dict(k='req',l='Requisição'),dict(k='os',l='O.S.'),dict(k='item',l='Item'),dict(k='lote',l='Lote'),dict(k='ent',l='Entregue',t='num',a='r'),dict(k='cons',l='Consumido',t='num',a='r'),
                dict(k='dev',l='Devolvido',t='num',a='r'),dict(k='cust',l='Em custódia',t='num',a='r'),dict(k='com',l='Com quem'),dict(k='enc',l='Encerramento da O.S.',w=200),dict(k='det',l='Detalhe',w=220)],
        [],edit=dict(m='form',title='Receber devolução',sub='',
            fields=[dict(k='qtd',l='Quantidade conferida',t='num',req=True,min=0.001),dict(k='cond',l='Condição',t='sel',dyn=True,req=True),
                    dict(k='obs',l='Observação',t='area',help='Obrigatória quando bloqueada para inspeção.')]),
        gid='g_dev',total=False)
    # ---------- etapa 4 · saldos por item e lote, com filtro por local ----------
    chips=(f'<span style="font-size: 12px; font-weight: 700; color: {MUTED};">Local</span>'
           f'<sc-for list="{H("est_locs")}" as="lc" hint-placeholder-count="5"><button type="button" aria-pressed="{H("lc.on")}" onClick="{H("lc.go")}" style="{H("lc.st")}">{H("lc.t")}</button></sc-for>')
    # árvore item › lote: cada linha é uma entidade do seu nível (item ou lote), com o item em coluna própria para filtrar
    g_lot=grid([dict(k='nome',l='Item › lote',w=170),dict(k='prod',l='Item',w=150),dict(k='local',l='Local'),dict(k='fis',l='Físico',t='num',a='r'),dict(k='res',l='Reservado',t='num',a='r'),
                dict(k='blq',l='Bloqueado',t='num',a='r',w=170),dict(k='disp',l='Disponível',t='num',a='r'),dict(k='expo',l='Em conferência',t='num',a='r'),dict(k='cust',l='Em custódia (fora do depósito)',t='num',a='r'),
                dict(k='cos',l='O.S. com custódia'),dict(k='sitl',l='Situação do lote',w=140),dict(k='vali',l='Validade',t='date')],
        [],edit=dict(m='origin',leafOnly=False,title='Saldo',fields=[dict(k='nome',l='Item ou lote',t='txt',ro=True),dict(k='local',l='Local',t='txt',ro=True)]),
        tree=True,gid='g_lot',total=False,tools=chips)
    # ---------- etapa 5 · contagens (cegas) ----------
    g_cnt=grid([dict(k='inv',l='Contagem'),dict(k='aj',l='Ajuste'),dict(k='prod',l='Item',w=160),dict(k='lote',l='Lote'),dict(k='local',l='Local'),dict(k='sis',l='Sistema na data de corte',t='num',a='r'),
                dict(k='cont',l='Contado',t='num',a='r'),dict(k='dif',l='Diferença',t='num',a='r'),dict(k='sit',l='Situação',w=230),dict(k='acao',l='Ação',w=120)],
        [],edit=dict(m='form',title='Contagem',newTitle='Nova contagem',sub='',
            fields=[dict(k='lote',l='Item · lote',t='sel',opts=[],req=True),dict(k='cont',l='Quantidade contada',t='num',req=True,min=0),
                    dict(k='contador',l='Contador',t='sel',dyn=True,opts=[],req=True),
                    dict(k='causa',l='Causa da diferença',t='area',help='Obrigatória para aprovar o ajuste quando houver diferença.')]),
        gid='g_cnt',total=False,qf=dict(k='sit',cut=' · '),tools=f'<sc-if value="{H("cnt_add")}" hint-placeholder-val="{F()}"><button type="button" onClick="{H("g_cnt_new")}" style="{_MINI}">+ Nova contagem</button></sc-if>')
    # ---------- etapa 6 · movimentos (trilha do cenário) ----------
    g_mov=grid([dict(k='hora',l='Hora',w=70),dict(k='mid',l='Registro'),dict(k='tipo',l='Movimento',w=150),dict(k='cond',l='Condição'),dict(k='doc',l='Documento'),dict(k='os',l='O.S.'),
                dict(k='item',l='Item',w=180),dict(k='lote',l='Lote'),dict(k='qtd',l='Quantidade',t='num',a='r'),dict(k='quem',l='Quem',w=150),dict(k='orig',l='Origem',w=90),dict(k='sinal',l='Sinal do app')],
        [],edit=dict(m='origin',title='Movimento',fields=[dict(k='tipo',l='Movimento',t='txt',ro=True),dict(k='quem',l='Quem',t='txt',ro=True)]),
        gid='g_mov',total=False,qf=dict(k='tipo',cut=' · ',todas='Todos'))
    # ---------- JS: cenário compartilhado + processo ----------
    # v55: com o Beneficiamento fora da navegação (ui37.BEN_PUBLICADO=False) o Estoque não aponta a tela oculta: o retorno da devolução guiada
    # ("Voltar à OB-…", rodada 3) só existe com a tela publicada; o endereço vem desta constante, como o PR_BEN_H de Cargas e Estoque de produto
    EXTRAJS[0]=cenario.js_prefixo()+'const E2 = '+json.dumps(_dados_js(),ensure_ascii=False).replace('</','<\\/')+';\n'+'const EST_BEN_H='+json.dumps('BEN.dc.html' if ui37.BEN_PUBLICADO else '')+';\n'+JS
    # ---------- corpo ----------
    acao_bloco=f'<button type="button" onClick="{H("prim_fn")}" style="{H("prim_st")}">{H("prim_t")}</button>'   # ação da etapa no bloco onde age
    s1=kline('k1')+bloco('Recebimentos','Confira a nota contra o pedido e o material; clique na linha para conferir.',g_rec,acao=acao_bloco)
    s2=kline('k2')+bloco('Entregas por O.S.','Entregue por item, do lote reservado, só para O.S. liberada ou em execução.',g_ent,acao=acao_bloco)
    volta=(f'<sc-if value="{H("dev_volta_on")}" hint-placeholder-val="{F()}"><a href="{H("dev_volta_h")}" style="align-self: flex-start; color: {ACC}; font-weight: 700; text-decoration: none; font-size: 13px;">{H("dev_volta_t")}</a></sc-if>')   # retorno à ordem pedinte (BEN, rodada 3)
    s3=kline('k3')+volta+bloco('Custódia e devoluções','Confira a sobra e receba: apta volta ao disponível, bloqueada vai para quarentena.',g_dev,acao=acao_bloco)
    # liberar quarentena: o pedido nasce na linha do lote (gestor); o nº do laudo é digitado aqui, junto da confirmação
    libq=(f'<sc-if value="{H("lib_on")}" hint-placeholder-val="{F()}"><div role="group" aria-label="Liberar quarentena com laudo" style="display: flex; flex-wrap: wrap; align-items: flex-end; gap: 10px; padding: 10px 12px; border-radius: 10px; background: {YELS}; border: 1px solid {LINE};">'
          f'<span style="font-size: 13px; font-weight: 600; flex: 1 1 280px;">{H("lib_t")}</span>'
          f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {MUTED};">Nº do laudo ou relatório de inspeção'
          f'<input id="est-laudo" value="{H("lib_laudo")}" onChange="{H("lib_setlaudo")}" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; width: 220px;"></label>'
          f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {MUTED};">Motivo, se o laudo reprovar'
          f'<input id="est-laudo-mot" value="{H("lib_mot")}" onChange="{H("lib_setmot")}" placeholder="ex.: germinação abaixo do padrão" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; width: 240px;"></label>'
          f'<button type="button" onClick="{H("lib_ok")}" style="{_MINIP}">Liberar com o laudo</button><button type="button" onClick="{H("lib_rep")}" style="{_MINI}">Reprovar com o laudo</button><button type="button" onClick="{H("libno")}" style="{_MINI}">Manter bloqueado</button>'
          f'<sc-if value="{H("lib_hasErr")}" hint-placeholder-val="{F()}"><span role="alert" style="flex-basis: 100%; font-size: 12px; font-weight: 700; color: {RED};">{H("lib_err")}</span></sc-if></div></sc-if>')
    s4=kline('k4')+libq+bloco('Saldos por lote e local','Confira físico, reservado, bloqueado e disponível; clique num lote para ver os movimentos.',g_lot,acao=acao_bloco)
    s5=kline('k5')+bloco('Contagens','Conte sem ver o saldo; a diferença vira ajuste para o gestor aprovar.',g_cnt,acao=acao_bloco)
    s6=kline('k6')+bloco('Movimentos','Acompanhe cada movimento de estoque, da web e do app.',
                         f'<sc-if value="{H("mov_tem")}" hint-placeholder-val="{H("true")}">{g_mov}</sc-if>'
                         f'<sc-if value="{H("mov_nada")}" hint-placeholder-val="{F()}"><div style="padding: 14px 4px; font-size: 13px; color: {MUTED};">Nenhum movimento desde o início da demonstração.</div></sc-if>',acao=acao_bloco)
    etapas=''.join(f'<sc-if value="{H("s"+str(i))}" hint-placeholder-val="{H("true") if i==1 else F()}"><div style="display: flex; flex-direction: column; gap: 14px;">{s}{navpe()}</div></sc-if>'
                   for i,s in enumerate([s1,s2,s3,s4,s5,s6],1))
    vazio=(f'<sc-if value="{H("est_vazio")}" hint-placeholder-val="{F()}"><div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; padding: 28px 24px; display: flex; align-items: center; gap: 8px; font-size: 14px;">'
           f'<span>Nenhum estoque na Boa Vista</span><span style="color: {MUTED};">·</span>'
           f'<button type="button" onClick="{H("est_versr")}" style="border: 0; background: transparent; color: {ACC}; font-family: inherit; font-size: 14px; font-weight: 700; cursor: pointer; padding: 0;">Ver Santa Rita</button></div></sc-if>')
    corpo=vazio+f'<sc-if value="{H("est_tem")}" hint-placeholder-val="{H("true")}">{etapas}</sc-if>'
    prim=f'<button type="button" onClick="{H("prim_fn")}" style="{H("prim_st")}">{H("prim_t")}</button>'
    HEIGHTS37[fname]=1180
    shell37('EST','Estoque',corpo,fname=fname,subtitle='Receba, entregue por O.S., receba devoluções e conte; cada movimento atualiza saldos, O.S. e app.',
            steps=secoes_state(NOMES,label='Seções do estoque'),primary_html=None,ctx=('Fazenda Santa Rita','Todos os depósitos',None),search=False)   # trabalho paralelo: seções em qualquer ordem, não etapas (UX-ACAO-UNICA-20261003)

JS=r'''
// ===== Processo · Estoque (6 etapas numa só tela; lê e muda o cenário compartilhado com O.S. e App) =====
function GR(id){ return GRIDS.find(g=>g.id===id); }
// Gancho de teste/inspeção (o script da tela roda isolado): os testes est_* leem e mudam o cenário na própria página.
try { window.__cen = { cenGet, cenMudar, cenReset, cenLiberar, cenEntregar, cenDevolver, cenReceber, cenLiberarQuarentena, cenReprovarQuarentena, cenContar, cenAprovarAjuste, cenConfirmarRecebimento, cenIniciarTurno, cenFecharTurno, cenSinal, cenPodeEncerrar, cenConciliar }; } catch (e) {}
function nf(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function eq(n,un){ n=Number(n)||0; const d=Math.abs(n-Math.round(n))<1e-6?0:(Math.abs(n*10-Math.round(n*10))<1e-6?1:2); return nf(n,d)+(un?' '+un:''); }
function esig(n,un){ return (n>0?'+':(n<0?'−':''))+eq(Math.abs(n),un); }
function eblank(x){ return x===null||x===undefined||String(x).trim()===''; }
function elotId(s){ return String(s||'').split(' · ')[0].trim(); }
// datas tipadas (TABELAS-FOCO): ISO no valor (ordena), dd/mm/aaaa ou mm/aaaa no texto; "previsto 24/09" usa o ano de hoje
function eiso(s){ const t=String(s||'').replace(/^previsto /,'').replace(/ \(previsto\)$/,'').trim(); let m=/^(\d{2})\/(\d{2})\/(\d{4})$/.exec(t); if(m) return m[3]+'-'+m[2]+'-'+m[1];
  m=/^(\d{2})\/(\d{2})$/.exec(t); return m?String(E2.hoje).split('/')[2]+'-'+m[2]+'-'+m[1]:''; }
function edmy(iso){ const a=String(iso||'').split('-'); return a.length===3?a[2]+'/'+a[1]+'/'+a[0]:'—'; }
function eym(s){ const m=/^(\d{2})\/(\d{4})$/.exec(String(s||'')); return m?m[2]+'-'+m[1]:''; }
function eval_(s){ const m=/^(\d{2})\/(\d{4})$/.exec(String(s||'')); return m?Number(m[2])*100+Number(m[1]):999999; }
function ereqN(id){ return Number(String(id||'').replace(/\D/g,''))||0; }
const EOK=['Liberadas','Em execução'];
const FCOR={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray'};
const EFASE={'A liberar':'a liberar','Liberadas':'liberada','Em execução':'em execução','Em conferência':'em conferência','Encerradas':'encerrada'};
// embalagem: "galão 20 L" → 16 galões
function eemb(emb){ const m=/^(.*?)\s*(\d[\d.]*)\s*(kg|L)\b/.exec(String(emb||'')); return m?{nome:m[1].trim(),n:Number(m[2].replace(/\./g,'')),un:m[3]}:null; }
function eplur(nome,k){ if(k===1) return nome; return nome.split(' ').map((w,i,a)=>i<a.length-1?w:(/ão$/.test(w)?w.replace(/ão$/,'ões'):w+'s')).join(' '); }
function epk(q,emb){ const e=eemb(emb); if(!e||!(q>1e-9)||!(e.n>0)) return ''; const w=Math.floor(q/e.n+1e-9), r=q-w*e.n; if(!w) return 'menos de 1 '+e.nome; return w+' '+eplur(e.nome,w)+(r>1e-6?' + '+eq(r,e.un):''); }

// ---------- leitura do cenário ----------
// reserva feita para o item (na liberação da O.S. ou no início da demonstração); só ela pode ser consumida pela entrega
function eresTot(c,rid,prod){ return cenResTot(c,rid,prod); }
// turno fechado sem sinal: o consumo ainda está no aparelho; o Estoque vê consumo e custódia mudarem só quando o app envia
// (cenFecharTurno já baixou a custódia no aparelho; o item exibido devolve essa baixa até o envio · CEN_BAIXA_NO_SINAL desliga)
function epCons(o,prod){ if(typeof CEN_BAIXA_NO_SINAL!=='undefined') return 0;
  return (o.ap||[]).filter(a=>a.sinc===false).reduce((s,a)=>s+(Number((a.cons||{})[prod])||0),0); }
function eitem(c,r,it0){ const o=c.ordens[r.os]||{}; const sq=Math.min(epCons(o,it0.prod),it0.consumido||0);
  const it=sq>1e-9?Object.assign({},it0,{consumido:it0.consumido-sq,custodia:it0.custodia+sq}):it0;
  const l=c.lotes[it.prod+'|'+it.lote]||null; const pend=cenSaldoEntregar(it);
  const imp=(o.selos||[]).find(s=>/impedida/i.test(s.t||'')); const im=E2.imped[r.os]||null;
  const bloq=(imp?(im?im.txt:(r.os+' '+String(imp.t).toLowerCase())):'')||estValidadeErro(l); const selo=imp?(im?im.selo:'O.S. impedida'):'';
  const pode=!bloq&&EOK.indexOf(o.etapa)>=0;
  let motivo=bloq;
  if(!motivo&&!pode) motivo=(o.etapa==='A liberar')?(r.os+' aguarda a liberação na O.S. (agrônomo)'):(r.os+' '+(EFASE[o.etapa]||String(o.etapa||'').toLowerCase())+': sem nova entrega');
  const resP=l?Math.max(0,Math.min(l.reservado,eresTot(c,r.id,it.prod)-it.entregue)):0;
  const sinal=(o.ap||[]).some(a=>a.sinc===false);  // apontamento no aparelho: a sobra só é conferida depois do envio
  const cf=cenConfAbertas(c,r.os).find(k=>k.req===r.id&&k.prod===it.prod)||null;
  /* linha de caixa de ordem do beneficiamento (rodada 3, BEN-D33): benDevPadrao orienta o estado da linha; a quantidade
     recebida e a condição dependem da conferência física, sem pré-preenchimento */
  const ben=typeof benEh==='function'&&benEh(o); const dp=ben&&it0.custodia>1e-9?benDevPadrao(c,o,it0,r.id):0;
  return {id:r.id+'|'+it.prod, rid:r.id, os:r.os, o, it, l, un:it.un, pend, pode, bloq, selo, motivo, resP, livre:l?cenDisp(l)+resP:0, quem:it.quem||o.resp||'', sinal, cf, ben, dp, dpart:edispPartes(c,r.id,it)}; }
// o que saiu do "a entregar" sem reposição (campo interno dispensado; a palavra não aparece na tela: a O.S. já usa "dispensar" para a área):
// a sobra devolvida (movimento de devolução apta com a parte livre), a avaria (devolução bloqueada) e a reserva baixada no Fechar
function edispPartes(c,rid,it){ if(!((it.dispensado||0)>1e-9)) return []; const mv=(c.movs||[]).filter(m=>m.req===rid&&m.prod===it.prod); const S=f=>mv.filter(f).reduce((a,m)=>a+(m.sobra!==undefined?m.sobra:m.qtd),0);
  return [[S(m=>m.tipo==='devolucao'&&m.apto&&m.sobra>0),'devolvido como sobra'],[S(m=>m.tipo==='devolucao'&&!m.apto),'avariado'],[S(m=>m.tipo==='reserva-baixa'),'baixado no Fechar']].filter(x=>x[0]>1e-9); }
// sobra de caixas da ordem do beneficiamento, com a conta (texto da linha e do formulário de Receba devoluções; rodada 3, I-c3)
function esobTxt(c,o){ const T=benCxTot(c,o), um=benCxUsoMax(o), kg=benKgAberto(o), s=benCxSobra(c,o);
  return 'Sobra da '+o.id+': '+eq(s,'un')+' = '+eq(T.cust,'un')+' em custódia − '+eq(um,'un')+' que a '+o.id+' ainda embala ('+benKg(kg)+' ÷ '+prFmtT(BENC.cx.massa,0)+' kg por caixa)'; }
// consumo em conferência (CONC-07): relatado × custódia, quem concilia e as duas decisões do almoxarife (CMD-50)
function ecfCel(k,c,ask,PF){ const h=[{k:'chip',t:'Consumo em conferência',c:'yellow'},{k:'mut',t:k.id+' · '+cenConfTxt(k,c)+' · '+k.resp}];
  const exc=k.relatado-cenConfCust(c,k)>1e-9;   /* o excedente da custódia sai do lote: aceite do gestor (padrão 2) */
  const AL=g2alc('AL-10'), AX=g2alcN(AL,'acima'), pode=exc?g2papel(PF,AX.papeis):!!g2umPapel(PF,AL.papeis);   /* coberto pela custódia: almoxarife ou gestor; acima: nível acima da AL-10 (CONF-01 R7) */
  if(ask!==k.id||!pode) return h.concat(pode?[{k:'act',t:'Aceitar consumo',fn:'cfa:'+k.id}]:[{k:'mut',t:'aceite: '+g2alcQuem('AL-10',exc?'acima':'base')}]).concat([{k:'act',t:'Recusar relato',fn:'cfr:'+k.id}]);
  let p; try{ p=cenConcPrevia(c,k.id); }catch(e){ p={erro:String(e.message||e)}; }
  if(p.erro) return h.concat([{k:'mut',t:p.erro},{k:'act',t:'Recusar relato',fn:'cfr:'+k.id},{k:'act',t:'Voltar',fn:'cfno:x'}]);
  return h.concat([{k:'txt',t:p.txt},{k:'act',t:'Confirmar aceite',fn:'cfok:'+k.id},{k:'act',t:'Voltar',fn:'cfno:x'}]); }
function eitens(c){ const out=[]; Object.keys(c.reqs||{}).sort((a,b)=>ereqN(a)-ereqN(b)).forEach(k=>{ const r=c.reqs[k]; (r.itens||[]).forEach(it=>out.push(eitem(c,r,it))); }); return out; }
function econta(x){ return eq(x.it.solicitado,x.un)+' solicitado'+(x.dpart||[]).map(p=>' − '+eq(p[0],x.un)+' '+p[1]).join('')+' − '+eq(x.it.consumido,x.un)+' consumido − '+eq(x.it.custodia,x.un)+' em custódia'; }
function elotes(c){ return Object.keys(c.lotes).map(k=>Object.assign({key:k},c.lotes[k])); }
function eitemDisp(c,prod){ return Object.values(c.lotes).filter(l=>l.prod===prod).reduce((a,l)=>a+cenDisp(l),0); }
function elotLbl(l){ return l.lote+' · '+l.prod+' · '+l.local; }
function elotKey(c,lbl){ const a=String(lbl||'').split(' · '); const k=(a[1]||'').trim()+'|'+(a[0]||'').trim(); return c.lotes[k]?k:null; }
// recebimentos: notas de base + recebimentos gravados (movimento recebimento-nf com os dados da conferência)
function erecs(c){ const mv={}; (c.movs||[]).forEach(m=>{ if(m.tipo==='recebimento-nf'&&m.estRec&&!mv[m.estRec.id]) mv[m.estRec.id]=m.estRec; });
  const out=E2.recs.map(b=>mv[b.id]?Object.assign({},b,mv[b.id],{ok:true,hoje:true}):b);
  Object.keys(mv).forEach(k=>{ if(!E2.recs.some(b=>b.id===k)) out.push(Object.assign({},mv[k],{ok:true,hoje:true})); }); return out; }
function epedBase(lbl){ const id=elotId(lbl); return E2.pedidos.find(p=>p.id===id)||null; }
function epeds(c){ const RC=erecs(c); return E2.pedidos.map(p=>{ const x=Object.assign({},p); RC.forEach(r=>{ if(r.hoje&&elotId(r.ped)===p.id) x.a_entregar=Math.max(0,x.a_entregar-(Number(r.conf)||0)); }); return x; }); }
function efert(lbl){ const p=epedBase(lbl); return !!(p&&E2.sem_validade.indexOf(p.grupo)>=0); }
// contagens: registros de base + os gravados no cenário (c.estInv)
function einvs(c){ const S=c.estInv||{}; const out=E2.contagens.map(b=>S[b.id]||b); Object.keys(S).sort().forEach(k=>{ if(!E2.contagens.some(b=>b.id===k)) out.push(S[k]); }); return out; }
function einvRec(c,id){ const r=einvs(c).find(x=>x.id===id); return r?cenClone(r):null; }
function eput(c,rec){ c.estInv=c.estInv||{}; c.estInv[rec.id]=rec; }
function eajuste(c,rec){ return rec&&rec.aj?((c.ajustes||[]).find(a=>a.id===rec.aj)||null):null; }
function econtou(rec){ return !!rec&&rec.cont!==null&&rec.cont!==undefined&&rec.cont!==''; }
function enovoInv(c){ let n=2612; const ids=einvs(c).map(x=>x.id); while(ids.indexOf('INV-'+n)>=0) n++; return 'INV-'+n; }
const MTIPO={'reserva':'Reserva','reserva-baixa':'Reserva baixada no Fechar','entrega':'Entrega','recebimento':'Recebimento confirmado no app','consumo':'Consumo apontado no app','devolucao':'Devolução',
  'recebimento-nf':'Recebimento de nota','inspecao':'Quarentena liberada','inspecao-reprovada':'Qualidade reprovada','contagem':'Contagem sem diferença','ajuste':'Ajuste de inventário'};
function emovQtd(m){ const u=m.un||''; switch(m.tipo){ case 'entrega': return '−'+eq(m.qtd,u); case 'devolucao': case 'recebimento-nf': return '+'+eq(m.qtd,u);
  case 'ajuste': return esig(m.qtd,u); case 'reserva': return eq(m.qtd,u)+' reservados'; case 'reserva-baixa': return eq(m.qtd,u)+' baixados da reserva'; case 'inspecao': return eq(m.qtd,u)+' liberados'; default: return ''; } }
function emovTxt(m){ const u=m.un||'';
  if(m.tipo==='reserva') return 'reserva '+m.req+' → '+m.os+': '+eq(m.qtd,u)+' reservados'+(m.det?' ('+m.det+')':'');
  if(m.tipo==='reserva-baixa') return 'reserva baixada '+m.req+' → '+m.os+': '+eq(m.qtd,u)+' não entregues (Fechar)';
  if(m.tipo==='entrega') return 'entrega '+m.req+' → '+m.os+': −'+eq(m.qtd,u)+' ('+m.quem+')';
  if(m.tipo==='devolucao') return 'devolução '+m.req+' ('+m.os+'): +'+eq(m.qtd,u)+(m.apto?' apta':' bloqueada para inspeção');
  if(m.tipo==='recebimento-nf') return 'recebimento '+m.doc+': +'+eq(m.qtd,u)+(m.apto?' apto':' em quarentena')+(m.val&&m.val!=='—'?' · validade '+m.val:'');
  if(m.tipo==='inspecao') return 'quarentena liberada '+(m.doc?'com o laudo '+m.doc+' por '+m.quem:'após inspeção')+': '+eq(m.qtd,u)+' passam a disponível'+(m.rev?' · '+m.rev:'');
  if(m.tipo==='inspecao-reprovada') return 'qualidade reprovada com o laudo '+(m.doc||'—')+' por '+m.quem+(m.motivo?' ('+m.motivo+')':'')+': '+eq(m.qtd,u)+' segregados para devolução ao fornecedor'+(m.rev?' · '+m.rev:'');
  if(m.tipo==='contagem') return 'contagem '+(m.doc?m.doc+' ':'')+'sem diferença';
  if(m.tipo==='ajuste') return 'ajuste de inventário '+(m.doc?m.doc+' ':'')+'aprovado por '+(m.quem||'gestor')+': '+esig(m.qtd,u)+(m.rev?' · '+m.rev:'');
  return emovTipo(m); }
// consumo: o canal do apontamento (app ou web) ou o aceite do almoxarife (conf = o caso conciliado)
function emovTipo(m){ if(m.tipo==='consumo'&&m.origem!=='app') return typeof m.conf==='string'?'Consumo aceito na conferência':'Consumo apontado na web'; return MTIPO[m.tipo]||m.tipo; }
// lote vencido: validade (mês/ano) anterior ao mês de hoje; entra todo em quarentena e não volta ao disponível
function evenc(l){ return cenLoteVencido(l,eiso(E2.hoje)); }
function estValidadeEntradaErro(l){ return evenc(l)?'Lote '+l.lote+' vencido em '+l.validade+': receba em quarentena, sem quantidade apta para uso.':''; }
// Um mesmo lote não pode misturar entradas com validades diferentes, nem pela quarentena.
function estValidadeConflito(l,val){ if(!l) return ''; const normal=v=>String(v||'').trim().replace(/^—$/,'');
  const atual=normal(l.validade), recebida=normal(val); return atual===recebida?'':'A validade informada difere da registrada no lote '+l.lote+' ('+(atual||'sem validade')+'). Confira o lote e a validade no documento antes de receber; o estoque foi preservado.'; }
function estValidadeErro(l){ return evenc(l)?'Lote '+l.lote+' vencido em '+l.validade+': não pode ser entregue. Revise a reserva com o responsável pela O.S.; o físico permanece no estoque.':''; }
// consumo apontado no app: "Glifosato 480 10, 2,4-D 806 5" (cenFecharTurno) → itens com a unidade da requisição ou da O.S.
function econsDet(c,m){ const r=m.req&&c.reqs[m.req]; const o=c.ordens[m.os]||{};
  return String(m.det||'').split(', ').map(s=>{ const x=/^(.*)\s(-?[\d.]+(?:,\d+)?)$/.exec(s.trim()); if(!x) return null; const prod=x[1];
    const it=r&&r.itens.find(i=>i.prod===prod); const ins=(o.ins||[]).find(i=>i.p===prod);
    return {prod,qtd:Number(x[2].replace(/\./g,'').replace(',','.')),un:(it&&it.un)||(ins&&ins.un)||''}; }).filter(Boolean); }
// itens de cada movimento do app: a confirmação vale só para o que estava entregue e ainda sem confirmação naquele momento
// (mesma regra de cenConfirmarRecebimento, refeita pela trilha); usa m.itens quando o cenário gravar a lista no movimento
function eappItens(c){ const st={}, out={};
  const S=(rid,prod)=>{ const k=rid+'|'+prod; if(!st[k]){ const r0=CEN0.reqs[rid]; const i0=r0&&r0.itens.find(i=>i.prod===prod); st[k]={cust:i0?i0.custodia:0,conf:!!(i0&&i0.confirmado)}; } return st[k]; };
  (c.movs||[]).forEach(m=>{
    if(m.tipo==='entrega'){ const s=S(m.req,m.prod); s.cust+=m.qtd; s.conf=false; }
    else if(m.tipo==='devolucao'){ S(m.req,m.prod).cust-=m.qtd; }
    else if(m.tipo==='consumo'){ const cs=econsDet(c,m); out[m.id]=cs; if(m.req) cs.forEach(x=>{ S(m.req,x.prod).cust-=x.qtd; }); }
    else if(m.tipo==='recebimento'){ const r=c.reqs[m.req]; const l=[];
      (r?r.itens:[]).forEach(it=>{ const s=S(m.req,it.prod); if(s.cust>1e-9&&!s.conf){ l.push({prod:it.prod,qtd:s.cust,un:it.un}); s.conf=true; } });
      out[m.id]=Array.isArray(m.itens)?m.itens:l; } });
  return out; }
// consumo sem sinal: o apontamento é enviado por cenSinal (fila AP|…); o movimento fica pendente só enquanto a O.S. tiver apontamento sem envio
function esemSinal(c){ const sem={}, porOS={};
  (c.movs||[]).forEach(m=>{ if(m.sinc!==false) return; if(m.tipo==='consumo') (porOS[m.os]=porOS[m.os]||[]).push(m.id); else sem[m.id]=true; });
  Object.keys(porOS).forEach(os=>{ const o=c.ordens[os]||{}; const n=(o.ap||[]).filter(a=>a.sinc===false).length; const ids=porOS[os]; ids.slice(Math.max(0,ids.length-n)).forEach(id=>{ sem[id]=true; }); });
  return sem; }
// documento do ajuste aprovado fora desta tela: o ajuste do cenário com o mesmo lote e a mesma diferença
function emovDoc(c,m,usados){ if(m.doc||m.tipo!=='ajuste') return m.doc?{doc:m.doc,aj:m.aj||''}:null;
  const aj=(c.ajustes||[]).find(a=>a.estado==='Aprovado'&&a.prod===m.prod&&a.lote===m.lote&&Math.abs(a.dif-m.qtd)<1e-9&&!usados[a.id]); if(!aj) return null;
  usados[aj.id]=true; return {doc:aj.inv||aj.id,aj:aj.inv?aj.id:''}; }

// ---------- mudanças no cenário (sempre dentro de cenMudar) ----------
// Recebimento: a parte apta e a parte em quarentena entram no mesmo lote (cenReceber); os dados da conferência ficam no movimento.
// chave: do formulário de quem confere (ENG-021); o mesmo formulário enviado 2× não recebe de novo (cenIdem; revisão CONF 13/10)
const EST_ITEM_DIFERENTE='Item diferente do pedido: não confirme como o produto comprado. Confira o item com o fornecedor e corrija o pedido antes de receber. Nada entrou no estoque.';
// A identidade vem do documento de origem; trocar o pedido não pode rebatizar a nota.
function estRecIdentidadeErro(c,d){
  const p=epedBase(d.ped), num=x=>String(x||'').replace(/\D/g,'');
  const notas=E2.recs.concat(erecs(c));
  const origem=notas.find(r=>r.id===d.id)||notas.find(r=>num(r.nf)&&num(r.nf)===num(d.nf));
  if(!p) return (d.ped||(origem&&origem.ped))?'Escolha um pedido válido para conferir a nota. Nada foi gravado.':'';
  const nf=origem||d, fornecedor=nf.forn||(origem&&epedBase(origem.ped)||{}).forn;
  const dif=[];
  if(nf.item&&nf.item!==p.item) dif.push('item '+nf.item+' ≠ '+p.item);
  if(nf.un&&nf.un!==p.un) dif.push('unidade '+nf.un+' ≠ '+p.un);
  if(fornecedor&&fornecedor!==p.forn) dif.push('fornecedor '+fornecedor+' ≠ '+p.forn);
  if(d.item&&d.item!==p.item) dif.push('item informado difere do pedido');
  if(d.un&&d.un!==p.un) dif.push('unidade informada difere do pedido');
  if(d.forn&&d.forn!==p.forn) dif.push('fornecedor informado difere do pedido');
  if(dif.length) return 'Item diferente do pedido: '+dif.join('; ')+'. Confira a nota e o pedido de origem; nada foi gravado.';
  if(origem&&origem.ped&&elotId(origem.ped)!==p.id) return 'Esta nota já está vinculada ao '+elotId(origem.ped)+'. Mantenha o pedido de origem; nada foi gravado.';
  if(origem&&num(origem.nf)!==num(d.nf)) return 'Mantenha a nota fiscal de origem '+origem.nf+'; nada foi gravado.';
  return '';
}
function estReceber(c,d,ator,chave){
  // Quarentena também guarda a identidade do produto: não pode mascarar um item diferente.
  if(d.div==='Item diferente do pedido') throw new Error(EST_ITEM_DIFERENTE);
  const identidade=estRecIdentidadeErro(c,d); if(identidade) throw new Error(identidade);
  return cenIdem(c,chave,JSON.stringify(['estReceber',d,(g2pf(ator)||{}).k||'']),'Recebimento '+(d.nf||''),()=>estReceber0(c,d,ator)); }
function estReceber0(c,d,ator){   /* ator: quem confere (perfil); o movimento grava quem agiu (revisão do CTL-3, achado 4) */ const n0=c.movs.length; const antes=eitemDisp(c,d.item);
  const validadeErro=estValidadeEntradaErro({lote:d.lote,validade:d.val})||estValidadeEntradaErro(c.lotes[d.item+'|'+d.lote]);
  if(d.apto>0&&validadeErro) throw new Error(validadeErro);
  const conflito=estValidadeConflito(c.lotes[d.item+'|'+d.lote],d.val); if(conflito) throw new Error(conflito);
  if(d.apto>0) cenReceber(c,d.item,d.lote,d.apto,d.un,d.local,d.val,d.nf,true,ator);
  if(d.quar>0) cenReceber(c,d.item,d.lote,d.quar,d.un,d.local,d.val,d.nf,false,ator);
  if(c.movs.length===n0) throw new Error('Nada conferido para entrar no estoque.');
  c.movs.slice(n0).forEach(m=>{ m.val=d.val; }); c.movs[n0].estRec=d;
  return {msg:'Recebimento '+d.nf+' conferido: '+eq(d.conf,d.un)+' de '+d.item+' no lote '+d.lote+(d.val&&d.val!=='—'?' (validade '+d.val+')':'')+'. Disponível '+eq(antes,d.un)+' → '+eq(eitemDisp(c,d.item),d.un)+(d.quar?'; '+eq(d.quar,d.un)+' em quarentena ficam fora do disponível.':'.')}; }
// Entrega: só a reserva desta requisição é baixada (regra única no cenEntregar, rodada 3); a nova entrega aguarda a confirmação no app.
function estEntregar(c,rid,prod,qtd,quem,ator,chave){ return cenIdem(c,chave,JSON.stringify(['estEntregar',rid,prod,Number(qtd),quem||'',(g2pf(ator)||{}).k||'']),'Entrega',()=>estEntregar0(c,rid,prod,qtd,quem,ator)); }
function estEntregar0(c,rid,prod,qtd,quem,ator){ const r0=c.reqs[rid]; const it0=r0&&r0.itens.find(i=>i.prod===prod); const l=it0&&c.lotes[prod+'|'+it0.lote];
  const validadeErro=estValidadeErro(l); if(validadeErro) throw new Error(validadeErro);   // EST-1 (Codex): lote vencido não sai
  const r=cenEntregar(c,rid,prod,qtd,quem,ator); it0.confirmado=false; return r; }   // a reserva própria é baixada no cenEntregar0 (BEN rodada 3, I-d3)
function estDevolver(c,rid,prod,qtd,apto,obs,ator,chave){
  if(typeof apto!=='boolean') throw new Error('Escolha a condição do material conferido.');
  if(!apto&&!String(obs||'').trim()) throw new Error('Descreva a condição do material bloqueado.');
  return cenIdem(c,chave,JSON.stringify(['estDevolver',rid,prod,Number(qtd),apto,obs||'',(g2pf(ator)||{}).k||'']),'Devolução',()=>estDevolver0(c,rid,prod,qtd,apto,obs,ator));
}
function estDevolver0(c,rid,prod,qtd,apto,obs,ator){
  const req0=c.reqs[rid],it0=req0&&req0.itens.find(i=>i.prod===prod);
  const validadeErro=estValidadeEntradaErro(it0&&c.lotes[prod+'|'+it0.lote]);
  if(apto&&validadeErro) throw new Error(validadeErro);
  const r=cenDevolver(c,rid,prod,qtd,apto,ator); if(obs) c.movs[c.movs.length-1].obs=obs;
  const req=c.reqs[rid]; const o=c.ordens[req.os]||{}; const it=req.itens.find(i=>i.prod===prod); const pe=cenPodeEncerrar(c,req.os);
  return {msg:r.msg+' Custódia de '+prod+' na '+req.os+': '+eq(it.custodia+qtd,it.un)+' → '+eq(it.custodia,it.un)+(o.etapa==='Em conferência'&&!pe?' · encerramento liberado.':'.')}; }
// contador do inventário (revisão CONF F6): pessoas com acesso Ativo e o papel almoxarife em Configurações, em ordem alfabética; nunca uma lista
// fixa (pessoa desativada não conta) nem valor padrão (o fato sairia em nome de quem não contou)
function estContadores(){ return g2perfis().filter(p=>g2papel(p,'almoxarife')).map(p=>g2ator(p,'almoxarife')).sort((a,b)=>a.localeCompare(b,'pt-BR')); }
function estContOpts(d){ const L=estContadores(); const cur=String((d||{}).contador||'');
  return [{v:'',t:L.length?'Escolha quem contou':'Almoxarife sem titular: conceda em Configurações'}].concat(L.map(x=>({v:x,t:x}))).concat(cur&&L.indexOf(cur)<0?[{v:cur,t:cur+' (registro)'}]:[]); }
function estContar(c,inv,key,contado,contador,causa,ator){ const l=c.lotes[key]; if(!l) throw new Error('Escolha o lote contado.');
  { const L=estContadores(); if(L.indexOf(contador)<0) throw new Error('Contador: escolha quem contou entre as pessoas com acesso e o papel de almoxarife ('+(L.join(', ')||'almoxarife sem titular: conceda em Configurações › Usuários e alçadas')+'). Nada foi gravado.'); }
  const rec=einvRec(c,inv)||{id:inv,key,hist:[]}; const sis=l.fisico; const n0=(c.ajustes||[]).length;
  const m0=c.movs.length; const rc=cenContar(c,key,contado); const aj=(c.ajustes||[]).length>n0?c.ajustes[c.ajustes.length-1]:null; const reg=ator?g2ator(ator,'almoxarife'):''; if(aj){ aj.inv=inv; aj.causa=causa; aj.contador=contador; aj.reg=reg; }   /* reg: quem registrou (perfil) */
  c.movs.slice(m0).forEach(m=>{ if(m.tipo==='contagem'){ m.doc=inv; m.quem=contador; } });   // contagem sem diferença: documento e contador na trilha
  Object.assign(rec,{key,sis,cont:contado,contador,reg,causa,aj:aj?aj.id:null}); eput(c,rec); const d=contado-sis;
  return {msg:Math.abs(d)<1e-9?('Contagem '+inv+' conferida: sem diferença.'):('Contagem '+inv+' registrada: diferença '+esig(d,l.un)+' · '+aj.id+' aguarda o gestor. O saldo não muda até aprovar'+(causa?'.':' · informe a causa antes da aprovação.')+(rc.alerta?' Se aprovado: '+rc.alerta:''))}; }
function estCausa(c,inv,causa){ const rec=einvRec(c,inv); rec.causa=causa; const aj=eajuste(c,rec); if(aj) aj.causa=causa; eput(c,rec);
  return {msg:'Causa da diferença de '+inv+' registrada'+(causa?': '+causa:'')+'. Quantidade e contador seguem travados; o ajuste aguarda aprovação.'}; }
function estRecontar(c,inv,ator){ const rec=einvRec(c,inv); if(!econtou(rec)) throw new Error(inv+' ainda não foi contada.');   /* ator: quem pede a recontagem (gravado no ajuste recusado, trilha CF-04) */
  const aj=eajuste(c,rec); if(aj&&aj.estado==='Aprovado') throw new Error('Ajuste '+inv+' já aprovado: não há recontagem.');
  if(aj&&aj.estado==='Aguardando gestor') cenAprovarAjuste(c,aj.id,false,ator);
  rec.hist=(rec.hist||[]).concat([{cont:rec.cont,contador:rec.contador,causa:rec.causa||'',dif:rec.cont-rec.sis}]);
  const outro=estContadores().find(x=>x!==rec.contador)||'';   /* sem outro almoxarife ativo: o formulário pede quem conta (a regra do outro contador segue) */
  Object.assign(rec,{cont:null,sis:null,causa:'',contador:outro,reg:'',aj:null}); eput(c,rec);
  return {msg:'Recontagem de '+inv+' aberta: outro contador conta sem ver o saldo; a contagem anterior fica registrada na origem da linha.'}; }
// Aprovar (A4; contrato do PR #47, comentário 6147474674): quem decide é o motor (cenAprovarAjuste: papel do gestor, contagem atual e valor contado).
// Contagem desatualizada (movimento físico ou de qualidade do lote depois dela) é recusada sem mudar nada; a diferença nunca é aplicada sobre um físico que mudou.
function estAprovar(c,inv,ator){ const rec=einvRec(c,inv); const l=rec&&c.lotes[rec.key]; if(!l||!econtou(rec)) throw new Error('Nada a aprovar nesta contagem.');
  const d=rec.cont-rec.sis; if(Math.abs(d)<1e-9) throw new Error('Nada a aprovar nesta contagem.');
  if(!String(rec.causa||'').trim()) throw new Error('Informe a causa da diferença de '+inv+' na contagem antes de aprovar o ajuste.');
  let aj=eajuste(c,rec); if(aj&&aj.estado==='Aprovado') throw new Error('Ajuste '+inv+' já aprovado · nada aplicado de novo.');
  const antes=l.fisico;
  if(!aj){ aj=cenAjusteNovo(c,rec.key,rec.sis,rec.cont,0,''); aj.inv=inv; aj.contador=rec.contador; aj.reg=rec.reg||''; rec.aj=aj.id; }   /* contagem de base (INV-2609): feita antes da demonstração, marcador no início da trilha */
  aj.causa=rec.causa; const m0=c.movs.length; const ra=cenAprovarAjuste(c,aj.id,true,ator); eput(c,rec);
  c.movs.slice(m0).forEach(m=>{ if(m.tipo==='ajuste'){ m.doc=inv; m.aj=aj.id; } });   // documento do ajuste na trilha de movimentos
  return {msg:'Ajuste '+inv+' ('+aj.id+') aprovado por '+aj.por+': '+esig(d,l.un)+' no lote '+l.lote+'. Físico '+eq(antes,l.un)+' → '+eq(l.fisico,l.un)+'.'+(aj.rev?' Fica '+aj.rev+'.':'')+(ra.alerta?' '+ra.alerta:'')}; }
/* contagem pendente desatualizada (A4): a lista de movimentos do motor, ou null se ainda vale; a contagem de base (sem ajuste) tem o marcador no início da trilha */
function evelha(c,rec){ if(!econtou(rec)||Math.abs(rec.cont-rec.sis)<1e-9) return null; const aj=eajuste(c,rec); if(aj) return aj.estado==='Aguardando gestor'?cenContagemVelha(c,aj):null;
  const l=c.lotes[rec.key]; return l?cenContagemVelha(c,{key:rec.key,prod:l.prod,lote:l.lote,un:l.un,sistema:rec.sis,mv:0}):null; }

// ---------- validação dos formulários (erro junto ao campo; o preenchido é mantido) ----------
const ESTV={};
ESTV.g_rec=(self,fm)=>{ const C=cenGet(); const e={}, d=fm.draft; const n=(k)=>g2num(d[k]); const conf=n('conf'), apto=n('apto'), quar=eblank(d.quar)?0:n('quar'), qnf=n('qtd_nf');
  const p=epeds(C).find(x=>x.id===elotId(d.ped)); const u=(p&&p.un)||'kg';
  if(d.div==='Item diferente do pedido') e.div=EST_ITEM_DIFERENTE;
  const identidade=estRecIdentidadeErro(C,Object.assign({},d,{id:fm.rid||d.id}));
  if(identidade){ e.ped=identidade; delete e.div; }
  if(!isNaN(conf)&&!isNaN(apto)&&!isNaN(quar)&&Math.abs(apto+quar-conf)>1e-6) e.apto='Apta + quarentena deve somar a conferida ('+eq(conf,u)+').';
  if(!isNaN(conf)&&!isNaN(qnf)&&Math.abs(conf-qnf)>1e-6&&d.div==='Sem divergência') e.div='A conferida difere da nota em '+eq(Math.abs(conf-qnf),u)+': indique a divergência.';
  if(p&&!isNaN(conf)&&conf>p.a_entregar+1e-6&&d.div!=='Sobra') e.conf='Acima do saldo do pedido '+p.id+' ('+eq(p.a_entregar,u)+' a entregar): registre como sobra.';
  if(((!isNaN(quar)&&quar>0)||(d.div&&d.div!=='Sem divergência'))&&!String(d.obs||'').trim()) e.obs='Informe o motivo da quarentena ou da divergência.';
  const nfn=String(d.nf||'').replace(/\D/g,''); if(nfn){ const dup=erecs(C).find(r=>r.id!==fm.rid&&String(r.nf||'').replace(/\D/g,'')===nfn); if(dup) e.nf=dup.nf+' já foi lançada: documento duplicado não cria segunda entrada.'; }
  const lt=String(d.lote||'').trim(); const outro=Object.values(C.lotes).find(l=>l.lote===lt&&p&&l.prod!==p.item); if(outro) e.lote='O lote '+lt+' é de '+outro.prod+'. Use outro código de lote.';
  if(!efert(d.ped)){ const vv=String(d.val||'').trim();
    if(!vv) e.val='Informe a validade do lote (mês/ano, ex.: 06/2027).';
    else if(!/^(0[1-9]|1[0-2])\/\d{4}$/.test(vv)) e.val='Use mês/ano com 4 dígitos no ano (ex.: 06/2027).';
    else if(evenc({validade:vv})){ if(!isNaN(apto)&&apto>1e-9) e.apto=estValidadeEntradaErro({lote:lt,validade:vv});
      if(!String(d.obs||'').trim()) e.obs='Informe o motivo (lote vencido em '+vv+').'; } }
  const conflito=p&&estValidadeConflito(C.lotes[p.item+'|'+lt],efert(d.ped)?'—':d.val); if(conflito&&!e.val) e.val=conflito;
  return e; };
ESTV.g_ent=(self,fm)=>{ const e={}; const x=eitens(cenGet()).find(y=>y.id===fm.rid); if(!x) return e; const n=g2num(fm.draft.qtd); if(isNaN(n)) return e;
  if(n>x.pend+1e-9) e.qtd='Acima do saldo a entregar: '+eq(x.pend,x.un)+' ('+econta(x)+').';
  else if(x.l&&n>x.livre+1e-9) e.qtd='Acima do livre no lote '+x.l.lote+': '+eq(x.livre,x.un)+' (físico '+eq(x.l.fisico,x.un)+' − bloqueado '+eq(x.l.quarentena,x.un)+' − reservado para outras O.S. '+eq(Math.max(0,x.l.reservado-x.resP),x.un)+').';
  return e; };
ESTV.g_dev=(self,fm)=>{ const e={}; const x=eitens(cenGet()).find(y=>y.id===fm.rid); if(!x) return e; const n=g2num(fm.draft.qtd);
  if(eblank(fm.draft.qtd)||!Number.isFinite(n)||!(n>0)) e.qtd='Informe a quantidade que conferiu, maior que zero.';
  if(E2.conds.indexOf(fm.draft.cond)<0) e.cond='Escolha a condição do material conferido.';
  if(x.sinal){ e.qtd='Apontamento de '+x.os+' no aparelho, aguardando sinal: receba a sobra depois do envio.'; return e; }
  if(x.cf){ e.qtd='Consumo em conferência ('+x.cf.id+'): aceite ou recuse o relato antes de receber devolução.'; return e; }
  if(!isNaN(n)&&n>x.it.custodia+1e-9) e.qtd='Acima da custódia: só '+eq(x.it.custodia,x.un)+' estão com '+x.quem+'.';
  if(fm.draft.cond===E2.conds[0]&&evenc(x.l)) e.cond=estValidadeEntradaErro(x.l);
  if(fm.draft.cond===E2.conds[1]&&!String(fm.draft.obs||'').trim()) e.obs='Descreva a condição (ex.: embalagem aberta).';
  return e; };
ESTV.g_cnt=(self,fm)=>{ const e={}; const C=cenGet(); if(!elotKey(C,fm.draft.lote)){ e.lote='Escolha o lote contado.'; return e; }
  const rec=fm.rid?einvRec(C,fm.rid):null; const h=(rec&&rec.hist)||[]; const ant=h.length?h[h.length-1]:null;
  if(ant&&!econtou(rec)&&fm.draft.contador===ant.contador) e.contador='Recontagem exige outro contador: '+ant.contador+' fez a contagem anterior.';
  return e; };
// ---------- gravação: cada formulário vira uma mudança no cenário ----------
const ESAVE={}, ECAMPO={g_rec:'lote',g_ent:'qtd',g_dev:'qtd',g_cnt:'cont'};
// chave do formulário aberto (ENG-021): nasce no 1º envio e fica no próprio formulário; reenvio e duplo clique do mesmo formulário usam a mesma chave
function eChave(fm,p){ if(!fm.chave) fm.chave='W-'+p+'-'+Date.now().toString(36)+Math.random().toString(36).slice(2,6); return fm.chave; }
ESAVE.g_rec=(self,fm)=>{ const d=fm.draft; const identidade=estRecIdentidadeErro(cenGet(),Object.assign({},d,{id:fm.rid||d.id})); if(identidade) return {erro:identidade}; const p=epedBase(d.ped); if(!p) return {erro:'Escolha um pedido válido para conferir a nota.'}; const n=k=>eblank(d[k])?0:g2num(d[k]); const nfv=String(d.nf||'').trim();
  const id=fm.rid||('r'+(nfv.replace(/\D/g,'')||String(Date.now()).slice(-6))); const base=erecs(cenGet()).find(b=>b.id===id)||{};
  const rec={id,nf:nfv,data:base.data||'',ped:d.ped,forn:base.forn||p.forn,item:base.item||p.item,un:base.un||p.un,qtd_nf:n('qtd_nf'),conf:n('conf'),apto:n('apto'),quar:n('quar'),lote:String(d.lote||'').trim(),
    val:efert(d.ped)?'—':String(d.val||'').trim(),local:d.local,div:d.div||'Sem divergência',obs:String(d.obs||'').trim()};
  const r=cenMudar(null,c=>estReceber(c,rec,g2perfil(),eChave(fm,'REC'))); r.fl=id; return r; };
ESAVE.g_ent=(self,fm)=>{ const x=eitens(cenGet()).find(y=>y.id===fm.rid); if(!x) return {erro:'Requisição não encontrada.'};
  return cenMudar(null,c=>estEntregar(c,x.rid,x.it.prod,g2num(fm.draft.qtd),fm.draft.quem,g2perfil(),eChave(fm,'ENT'))); };
ESAVE.g_dev=(self,fm)=>{ const salvo=fm.chave&&(cenGet().recibos||{})[fm.chave]; const erros=salvo?{}:ESTV.g_dev(self,fm); if(Object.keys(erros).length) return {erro:erros.qtd||erros.cond||erros.obs}; const C=cenGet(); const x=eitens(C).find(y=>y.id===fm.rid); if(!x) return {erro:'Requisição não encontrada.'};
  /* atalho guiado (EST.dc.html#dev=…, rodada 3, I-c5): se a sobra ou a fase da ordem mudou depois que o formulário abriu (outra aba), recusa sem
     escrita, diz o que mudou e pede nova conferência da quantidade. A versão vai no endereço só como contexto: uma saída de Produto sobe a versão sem mudar a
     sobra (−caixas e −kg). Dano evitado: devolver caixas que a ordem voltou a precisar */
  /* revisão A8 (S2): a revalidação vale para todo caminho de abertura (lista, primária e #dev): o que a pessoa viu ao abrir (self._estDevVi:
     sobra, fase e entregue − devolvido da linha) é conferido no Salvar. entregue − devolvido muda com outra devolução ou entrega gravada, não
     com a saída de Produto. Dano evitado: a aba velha aberta pela lista gravava de novo a sobra já recebida (custódia 869 → 730 → 591) */
  const D=self._estDev; const V=self._estDevVi&&self._estDevVi.id===x.id?self._estDevVi:null; if(!salvo&&V&&x.ben){ const sob=benCxSobra(C,x.o), et=x.o.etapa, mv=x.it.entregue-x.it.devolvido;
    if(sob!==V.sob||et!==V.etapa||Math.abs(mv-V.mov)>1e-9){ const t='A '+x.os+' mudou depois que você abriu ('+[sob!==V.sob?'sobra '+eq(V.sob)+' → '+eq(sob,'un'):'',et!==V.etapa?V.etapa+' → '+et:'',
        Math.abs(mv-V.mov)>1e-9?'outra devolução ou entrega gravada na '+x.rid+': custódia '+eq(x.it.custodia,x.un):''].filter(Boolean).join('; ')+'): nada foi gravado. Confira novamente a quantidade e a condição e salve de novo.';
      V.sob=sob; V.etapa=et; V.mov=mv; if(D&&D.rid===x.rid){ D.sob=sob; D.etapa=et; } return {erro:t,draft:{qtd:'',cond:''}}; } }
  const r=cenMudar(null,c=>estDevolver(c,x.rid,x.it.prod,g2num(fm.draft.qtd),fm.draft.cond===E2.conds[0],String(fm.draft.obs||'').trim(),g2perfil(),eChave(fm,'DEV')));
  if(!r.erro&&D&&D.rid===x.rid){ self._estDev=null; if(D.para) self.setState({est_volta:D.para}); try{ history.replaceState(null,'',location.pathname); }catch(e){} }
  return r; };
ESAVE.g_cnt=(self,fm)=>{ const d=fm.draft; const C=cenGet(); const rec=fm.rid?einvRec(C,fm.rid):null; const causa=String(d.causa||'').trim();
  if(econtou(rec)) return cenMudar(null,c=>estCausa(c,rec.id,causa));
  const key=elotKey(C,d.lote); const inv=rec?rec.id:enovoInv(C); const r=cenMudar(null,c=>estContar(c,inv,key,g2num(d.cont),d.contador,causa,g2perfil())); r.fl=inv; return r; };
function efields(sp,fm){ const e={}; (sp.edit.fields||[]).forEach(f=>{ if(f.ro||(f.newOnly&&!fm.isNew)) return; const val=String(fm.draft[f.k]===undefined?'':fm.draft[f.k]).trim();
  if(f.req&&!val){ e[f.k]='Informe '+f.l.toLowerCase()+'.'; return; }
  if(f.t==='num'&&val){ const n=g2num(val); if(isNaN(n)){ e[f.k]='Use um número (ex.: 12,5).'; return; } if(f.min!==undefined&&n<f.min) e[f.k]=(f.min>0?'Informe um valor maior que zero.':'Não use valor negativo.'); } }); return e; }
const _g2save0=g2save;
g2save=function(self,sp){ const fm=g2st(self,sp.id).fm; if(!fm||fm.ro||!ESAVE[sp.id]) return _g2save0(self,sp);
  const e=Object.assign({},ESTV[sp.id]?(ESTV[sp.id](self,fm)||{}):{},efields(sp,fm));
  if(Object.keys(e).length){ g2set(self,sp.id,{fm:Object.assign({},fm,{errs:e,warn:false})}); return; }
  const r=ESAVE[sp.id](self,fm)||{};
  if(r.erro){ g2set(self,sp.id,{fm:Object.assign({},fm,{errs:{[ECAMPO[sp.id]]:r.erro},warn:false},r.draft?{draft:Object.assign({},fm.draft,r.draft)}:{})}); return; }
  g2set(self,sp.id,{fm:null,fl:r.fl||fm.rid}); self.setState({cenrev:Date.now(),g2toast:r.msg||'Salvo.'}); };
// as grades desta tela são sempre recalculadas do cenário (nada fica preso no estado local da grade)
const ECEN={g_rec:1,g_ent:1,g_dev:1,g_lot:1,g_cnt:1,g_mov:1};
const _g2rows0=g2rows;
g2rows=function(self,sp){ return ECEN[sp.id]?sp.rows:_g2rows0(self,sp); };

function elotRow(c,l,ask,INV,GEST){ const un=l.un; const venc=evenc(l);
  const mv=(c.movs||[]).filter(m=>m.prod===l.prod&&m.lote===l.lote).map(m=>({t:m.at+' · '+emovTxt(m)}));
  const pend=INV.filter(x=>x.key===l.key&&econtou(x)&&Math.abs(x.cont-x.sis)>1e-9&&!(eajuste(c,x)&&eajuste(c,x).estado==='Aprovado')).map(x=>({t:'Ajuste '+x.id+' '+esig(x.cont-x.sis,un)+' aguardando aprovação · não aplicado ao saldo'}));
  // lote vencido não volta ao disponível: sem "Liberar após inspeção"
  const qrep=Math.min(l.quarentena||0,l.quarRep||0), qpen=(l.quarentena||0)-qrep;   // reprovado: segregado para devolução ao fornecedor (revisão do 853a6a8, achado 2)
  const rps=qrep>1e-9?cenRepsLote(c,l,qrep):[];   /* cada laudo com a sua quantidade, do histórico do lote (revisão do 16fb55e, ajuste 2) */
  const blq=l.quarentena>1e-9?[{k:'chip',t:eq(l.quarentena,un),c:'yellow'}].concat(qrep>1e-9?[{k:'chip',t:'Reprovado · '+eq(qrep,un)+' · '+(rps.length>1?'laudos '+rps.map(r=>(r.laudo||'—')+' '+eq(r.q,un)).join(' + '):'laudo '+((rps[0]||l.rep||{}).laudo||'—')),c:'red'}]:[])
    .concat((venc||!(qpen>1e-9))?[]:(!GEST?[{k:'mut',t:'aguarda laudo · '+g2alcQuem('AL-11')+' libera ou reprova'}]:(ask===l.key?[{k:'mut',t:'informe o laudo acima'},{k:'act',t:'Manter',fn:'libno:x'}]:[{k:'act',t:'Liberar após inspeção',fn:'libq:'+l.key}]))):[{k:'mut',t:'—'}];
  return {id:'L|'+l.key,ro:true,v:{nome:l.lote,prod:l.prod,un,local:l.local,fis:l.fisico,res:l.reservado,blq:l.quarentena,disp:cenDisp(l),expo:'',cust:'',cos:'',val:l.validade,vali:eym(l.validade),sitl:(venc?'Vencido':(l.quarentena>1e-9?'Em quarentena':'Disponível'))},
    s:{nome:l.lote,prod:l.prod,un,vali:(l.validade&&l.validade!=='—'?l.validade:''),sitl:(venc?'Vencido':(l.quarentena>1e-9?'Em quarentena':'Disponível'))},
    p:{prod:[{k:'mut',t:l.prod}],fis:[{k:'txt',t:eq(l.fisico,un)}],res:l.reservado>1e-9?[{k:'txt',t:eq(l.reservado,un)}]:[{k:'mut',t:'—'}],blq,disp:[{k:'b',t:eq(cenDisp(l),un)}],expo:[{k:'mut',t:''}],cust:[{k:'mut',t:''}],cos:[{k:'mut',t:''}],
       vali:[{k:(l.validade&&l.validade!=='—')?'txt':'mut',t:l.validade||'—'}],
       sitl:[venc?{k:'chip',t:'Vencido',c:'red'}:(l.quarentena>1e-9?{k:'chip',t:'Em quarentena',c:'yellow'}:{k:'txt',t:'Disponível'})].concat(venc?[{k:'mut',t:'não volta ao disponível'}]:[])
         .concat(cenSemFisico(l)>1e-9?[{k:'chip',t:'Reserva sem físico · '+eq(cenSemFisico(l),un),c:'red'},{k:'mut',t:'confere: '+g2quem('almoxarife')}]:[])},
    o:(mv.length?mv:[{t:'Sem movimentos desde o início da demonstração.'}]).concat(pend).concat(cenSemFisico(l)>1e-9?[{t:cenSemFisicoTxt(c,l,cenSemFisico(l))}]:[])}; }

function PREVALS(self,v){
  self.g2opts=(gid,k,d)=>(gid==='g_dev'&&k==='cond')?[{v:'',t:'Escolha a condição'}].concat(E2.conds.map(t=>({v:t,t}))):(gid==='g_cnt'&&k==='contador')?estContOpts(d):null;   /* contador: pessoas ativas com o papel almoxarife (revisão CONF F6) */
  cenOuvir(self); const C=cenGet(); self._cen=C; const PF=g2perfil(), GEST=g2papel(PF,g2alc('AL-11').papeis), GAJ=g2papel(PF,g2alc('AL-09').papeis);   /* quem age; quarentena (AL-11) e ajuste (AL-09) pela alçada vigente */
  const vazio=(v.mf_faz==='Boa Vista'); v.est_vazio=vazio; v.est_tem=!vazio; v.est_versr=()=>self.setState({mf_faz:'Santa Rita',g2toast:'Fazenda: Santa Rita'});
  const IT=eitens(C); const INV=einvs(C);
  // ---- etapa 1: recebimentos ----
  const RC=erecs(C), PD=epeds(C); let npend=0;
  GR('g_rec').rows=RC.map(x=>{ const ok=!!x.ok; if(!ok) npend++; const p=PD.find(y=>y.id===elotId(x.ped)); const quar=ok?(Number(x.quar)||0):0;
    const l=C.lotes[x.item+'|'+x.lote]; const vl=x.val&&x.val!=='—'?x.val:'';
    const prev=/previsto/.test(String(x.data||'')); const dt=eiso(x.data); const cf=ok&&x.hoje?eiso(E2.hoje):'';   // data da nota (ou prevista) × data da conferência
    const r={id:x.id,ro:ok,v:{nf:x.nf,data:dt,cfd:cf,vali:eym(vl),ped:x.ped,forn:p?p.forn:'',item:x.item,un:x.un||'kg',qtd_nf:x.qtd_nf,conf:ok?x.conf:'',apto:ok?x.apto:'',quar:ok?x.quar:'',lote:x.lote,val:vl,local:x.local,div:x.div||'Sem divergência',obs:x.obs||''},s:{},p:{}};
    r.p.nf=[{k:'b',t:x.nf}]; r.s.nf=x.nf; r.s.data=dt?edmy(dt):''; r.p.data=[{k:dt?'txt':'mut',t:dt?edmy(dt):'—'}];
    r.s.cfd=cf?edmy(cf):''; r.p.cfd=[{k:cf?'txt':'mut',t:cf?edmy(cf):'—'}];
    r.p.ped=p?[{k:'b',t:p.id}].concat(p.cmp?[{k:'link',t:'Ver pedido',h:'CMP.dc.html'}]:[]):[{k:'mut',t:'—'}]; r.s.ped=p?p.id:''; r.s.forn=p?p.forn:''; r.p.forn=[{k:'txt',t:p?p.forn:'—'}];
    r.p.item=[{k:'txt',t:x.item}]; r.s.item=x.item; r.s.lote=x.lote; r.s.vali=vl; r.p.vali=[{k:vl?'txt':'mut',t:vl||'—'}];
    ['qtd_nf','conf','apto','quar'].forEach(f=>{ const q=r.v[f]; r.p[f]=(q===''||q===null||q===undefined)?[{k:'mut',t:'—'}]:[{k:'txt',t:eq(q,r.v.un)}]; });
    // nota que ainda não chegou fica "Prevista"; conferida com lote vencido fica "Vencido" (não volta ao disponível)
    let sit; if(!ok) sit=prev?{k:'chip',t:'Prevista',c:'gray'}:{k:'chip',t:'A conferir',c:'yellow'};
    else if(quar>0&&l&&l.quarentena>1e-9&&evenc(l)) sit={k:'chip',t:'Vencido',c:'red'};
    else if(quar>0&&l&&l.quarentena>1e-9) sit={k:'chip',t:'Aguarda laudo',c:'yellow'};
    else if(quar>0) sit={k:'chip',t:'Quarentena liberada',c:'green'}; else sit={k:'chip',t:'Conferido',c:'green'};
    const dv=ok&&x.div&&x.div!=='Sem divergência'; r.p.sit=[sit]; r.s.sit=sit.t; r.v.divg=dv?x.div:''; r.p.divg=dv?[{k:'chip',t:x.div,c:'red'}]:[{k:'mut',t:'—'}]; r.s.divg=dv?x.div:''; return r; });
  const fmR=g2st(self,'g_rec').fm; const fV=GR('g_rec').edit.fields.find(f=>f.k==='val');
  const origemR=fmR&&RC.find(r=>r.id===fmR.rid);
  GR('g_rec').edit.fields.forEach(f=>{ if(f.k==='ped'||f.k==='nf'){ f.ro=!!origemR; f.help=origemR?'Vínculo da nota de origem. Confira este documento; não troque o pedido.':(f.k==='nf'?'Documento já lançado não cria segunda entrada.':''); } });
  if(fmR){ const fe=efert(fmR.draft.ped); fV.ro=fe; fV.help=fe?'Fertilizantes, corretivos e embalagens: sem validade de lote.':'Mês/ano (ex.: 06/2027). Lote vencido entra todo em quarentena.';
    const pu=(epedBase(fmR.draft.ped)||{}).un||'kg'; GR('g_rec').edit.fields.forEach(f=>{ if(['qtd_nf','conf','apto','quar'].indexOf(f.k)>=0) f.u=pu; }); }   /* a unidade é a do pedido (caixa em un) */
  // ---- etapa 2: entregas por O.S. ----
  let nent=0,nag=0,ncons=0,nimp=0;
  const eord=x=>(x.pode&&x.l&&x.pend>1e-9)?0:(x.pode?1:2);
  GR('g_ent').rows=IT.slice().sort((a,b)=>(eord(a)-eord(b))||(ereqN(a.rid)-ereqN(b.rid))).map(x=>{ const u=x.un, it=x.it, o=x.o; const ag=it.custodia>1e-9&&!it.confirmado&&!x.ben;
    if(eord(x)===0) nent++; if(ag) nag++; if(x.bloq) nimp++; else if(!x.pode) ncons++;
    const r={id:x.id,ro:eord(x)!==0,v:{req:x.rid,os:x.os,un:u,emb:it.emb||'',fase:o.etapa||'',item:it.prod,sol:it.solicitado,ent:it.entregue,pend:x.pend,
      lote:x.l?(x.l.lote+' · '+x.l.local+(x.l.validade&&x.l.validade!=='—'?' · validade '+x.l.validade:'')):'Sem lote no estoque',qtd:x.pend>1e-9?x.pend:'',quem:x.quem},s:{},p:{}};
    r.p.req=[{k:'b',t:x.rid}]; r.s.req=x.rid; r.p.os=[{k:'link',t:x.os,h:'OS.dc.html'}]; r.s.os=x.os;
    r.p.fase=[{k:'chip',t:o.etapa||'—',c:FCOR[o.etapa]||'gray'}]; r.s.fase=o.etapa||'';
    r.p.item=[{k:'txt',t:it.prod}]; r.s.item=it.prod; r.s.lote=x.l?x.l.lote:'sem lote'; r.p.lote=[{k:x.l?'txt':'mut',t:x.l?x.l.lote:'sem lote'}];
    r.s.emb=it.emb||''; r.p.emb=[{k:it.emb?'txt':'mut',t:it.emb||'—'}];
    r.p.sol=[{k:'txt',t:eq(it.solicitado,u)}]; r.p.ent=[{k:'txt',t:eq(it.entregue,u)}];
    const pk=x.pode?epk(x.pend,it.emb):''; r.v.pk=pk; r.s.pk=pk; r.p.pk=pk?[{k:'txt',t:pk}]:[{k:'mut',t:'—'}];
    r.p.pend=x.pend>1e-9?[x.pode?{k:'b',t:eq(x.pend,u)}:{k:'txt',t:eq(x.pend,u)}]:[{k:'mut',t:'—'}];
    let sit,sub='';
    if(x.bloq){ sit={k:'chip',t:'Bloqueada',c:'red'}; sub=x.bloq; }
    else if(!x.pode){ sit={k:'chip',t:'O.S. '+(EFASE[o.etapa]||String(o.etapa||'').toLowerCase())+' · sem nova entrega',c:'gray'}; sub=(o.etapa==='A liberar'?x.motivo:(x.pend>1e-9?econta(x):'')); }   // saldo sem nova entrega: a conta fica à vista (Entregue inclui o que voltou)
    else if(!x.l) sit={k:'chip',t:'Sem lote no estoque',c:'red'};
    else if(x.pend<=1e-9) sit={k:'chip',t:'Entrega completa',c:'green'};
    else if(it.entregue>0) sit={k:'chip',t:'Parcial',c:'yellow'}; else sit={k:'chip',t:'A entregar',c:'gray'};
    if(x.pode&&x.l&&x.pend>1e-9) sub=(x.livre<x.pend-1e-9?'lote cobre só '+eq(x.livre,u)+' dos '+eq(x.pend,u):(it.entregue>0?'faltam '+eq(x.pend,u):''));
    const tot=((o.ins||[]).find(i=>i.p===it.prod)||{}).tot; const solO=IT.filter(y=>y.os===x.os&&y.it.prod===it.prod).reduce((a,y)=>a+y.it.solicitado,0); if(x.pode&&tot&&tot>solO+1e-9) sub=(sub?sub+' · ':'')+'O.S. pede '+eq(tot,u)+', reservado '+eq(it.solicitado,u);
    // situação (chips do estado) e detalhe (o porquê, com quantidades) em colunas próprias
    r.p.sit=[sit].concat(ag?[{k:'chip',t:'Aguardando confirmação no app',c:'yellow'}]:[]).concat(x.selo?[{k:'chip',t:x.selo,c:'yellow'}]:[]);
    r.s.sit=sit.t+(ag?' · Aguardando confirmação no app':''); r.v.det=sub; r.s.det=sub; r.p.det=sub?[{k:'txt',t:sub}]:[{k:'mut',t:'—'}]; return r; });
  const fmE=g2st(self,'g_ent').fm; if(fmE&&fmE.rid){ const x=IT.find(y=>y.id===fmE.rid); if(x){ const fs=GR('g_ent').edit.fields; const pk=epk(x.pend,x.it.emb);
      fs[1].u=x.un; fs[1].help='A entregar: '+eq(x.pend,x.un)+' = '+econta(x)+'.'+(pk?' Em '+x.it.emb+': '+pk+'.':''); } }
  // ---- etapa 3: custódia e devoluções ----
  const custs=[];
  GR('g_dev').rows=IT.filter(x=>x.it.entregue>1e-9||x.it.custodia>1e-9).sort((a,b)=>((b.it.custodia>1e-9)-(a.it.custodia>1e-9))||(ereqN(a.rid)-ereqN(b.rid))).map(x=>{
    const u=x.un, it=x.it, o=x.o; const cu=it.custodia>1e-9; if(cu) custs.push(x);
    const r={id:x.id,ro:!cu||x.sinal||!!x.cf,v:{req:x.rid,os:x.os,item:it.prod,lote:it.lote,un:u,com:cu?x.quem:'',ent:it.entregue,cons:it.consumido,dev:it.devolvido,cust:it.custodia,qtd:'',cond:'',obs:''},s:{},p:{}};
    r.p.req=[{k:'b',t:x.rid}]; r.s.req=x.rid; r.p.os=[{k:'link',t:x.os,h:'OS.dc.html'}]; r.s.os=x.os;
    r.p.item=[{k:'txt',t:it.prod}]; r.s.item=it.prod; r.s.lote=it.lote;
    r.p.ent=[{k:'txt',t:eq(it.entregue,u)}]; r.p.cons=[{k:'txt',t:eq(it.consumido,u)}]; r.p.dev=[{k:'txt',t:eq(it.devolvido,u)}];
    r.p.cust=cu?[{k:'b',t:eq(it.custodia,u)}]:[{k:'mut',t:'—'}]; r.s.com=cu?x.quem:''; r.p.com=cu?[{k:'txt',t:x.quem}]:[{k:'mut',t:'—'}];
    let pe=''; try{ pe=cenPodeEncerrar(C,x.os); }catch(err){ pe=''; }
    const cOS=IT.filter(y=>y.os===x.os&&y.it.custodia>1e-9).map(y=>eq(y.it.custodia,y.un)).join(' + ');
    let enc,es='';
    if(x.cf){ r.p.enc=ecfCel(x.cf,C,self.state.est_cfask,PF); r.s.enc='Consumo em conferência '+x.cf.id; r.p.det=[{k:'mut',t:'—'}]; r.s.det=''; return r; }
    if(o.etapa==='Em conferência'){ if(pe){ enc={k:'chip',t:'Bloqueado',c:'red'}; es=cOS?cOS+' em custódia':pe; } else { enc={k:'chip',t:'Pode encerrar',c:'green'}; es='custódia zero'; } }
    else if(cu&&x.sinal){ enc={k:'chip',t:'Aguardando sinal do app',c:'yellow'}; es='consumo no aparelho · receba a sobra depois do envio'; }
    else if(cu&&x.ben){ enc=x.dp>0?{k:'chip',t:'Sobra a receber',c:'yellow'}:{k:'chip',t:'Em uso na ordem',c:'gray'}; es=x.dp>0?esobTxt(C,o):('a '+x.os+' ainda embala '+benKg(benKgAberto(o))+' (até '+eq(benCxUsoMax(o),u)+')'); }
    else if(cu){ enc={k:'chip',t:'Em uso na O.S.',c:'gray'}; es='O.S. '+(EFASE[o.etapa]||String(o.etapa||'').toLowerCase()); }
    else enc={k:'chip',t:'Sem custódia',c:'gray'};
    r.p.enc=[enc]; r.s.enc=enc.t; r.v.det=es; r.s.det=es; r.p.det=es?[{k:'txt',t:es}]:[{k:'mut',t:'—'}]; return r; });
  const CFS=cenConfAbertas(C); CFS.filter(k=>!IT.some(x=>x.rid===k.req&&x.it.prod===k.prod)).forEach(k=>GR('g_dev').rows.push({id:'CF|'+k.id,ro:true,
    v:{req:k.req||'—',os:k.os,item:k.prod,lote:'',un:k.un||'',com:'',ent:0,cons:0,dev:0,cust:0,qtd:'',cond:'',obs:''},s:{req:(k.req||''),os:k.os,item:k.prod,lote:'fora da requisição',enc:'Consumo em conferência '+k.id,det:''},
    p:{req:[{k:'b',t:k.req||'sem requisição'}],os:[{k:'link',t:k.os,h:'OS.dc.html'}],item:[{k:'txt',t:k.prod}],lote:[{k:'mut',t:'fora da requisição'}],ent:[{k:'mut',t:'—'}],cons:[{k:'mut',t:'—'}],dev:[{k:'mut',t:'—'}],cust:[{k:'mut',t:'—'}],com:[{k:'mut',t:'—'}],det:[{k:'mut',t:'—'}],enc:ecfCel(k,C,self.state.est_cfask,PF)}}));
  const fmD=g2st(self,'g_dev').fm; if(fmD&&fmD.rid){ const x=IT.find(y=>y.id===fmD.rid); if(x){ const fs=GR('g_dev').edit.fields; fs[0].u=x.un; fs[0].help='Em custódia: '+eq(x.it.custodia,x.un)+' com '+x.quem+'.'; if(x.ben){ const sobra=benSobraLinhas(C,x.o).find(y=>y.rid===x.rid); fs[0].help+=' '+esobTxt(C,x.o)+'. Sobra desta linha: '+eq(sobra?sobra.qtd:0,x.un)+'. Informe a quantidade e a condição conferidas fisicamente.'; } } }
  // ---- etapa 4: saldos por lote e local ----
  const loc=self.state.est_loc||''; const LS=elotes(C).filter(l=>!loc||l.local===loc); const itens=[]; LS.forEach(l=>{ if(itens.indexOf(l.prod)<0) itens.push(l.prod); });
  const quarTxt=[], inspTxt=[], vencTxt=[]; const x0={}; const ask=self.state.libask;
  const eexp=(pr)=>{ const g={}; CFS.filter(k=>k.prod===pr).forEach(k=>{ const kk=(k.req||'')+'|'+k.os; g[kk]=g[kk]||{rel:0,cu:cenConfCust(C,k),ids:[]}; g[kk].rel+=k.relatado; g[kk].ids.push(k.id); });
    return Object.values(g).reduce((a,x)=>({q:a.q+Math.max(0,x.rel-x.cu),ids:a.ids.concat(x.ids)}),{q:0,ids:[]}); };
  GR('g_lot').rows=itens.map(pr=>{ const ls=LS.filter(l=>l.prod===pr); const un=ls[0].un; const S=f=>ls.reduce((a,l)=>a+f(l),0);
    const cr=IT.filter(x=>x.it.prod===pr&&x.it.custodia>1e-9); const ck=cr.reduce((a,x)=>a+x.it.custodia,0);
    const fis=S(l=>l.fisico), blq=S(l=>l.quarentena), res=S(l=>l.reservado), dp=S(cenDisp); if(blq>1e-9) quarTxt.push(pr+' '+eq(blq,un));
    const bv=S(l=>evenc(l)?l.quarentena:0); if(blq-bv>1e-9) inspTxt.push(pr+' '+eq(blq-bv,un)); if(bv>1e-9) vencTxt.push(pr+' '+eq(bv,un));
    const id='I|'+pr; x0[id]=true; const locs=[...new Set(ls.map(l=>l.local))].join(', '); const ex=eexp(pr);
    const o=[{t:'Disponível: '+eq(dp,un)+'. Soma do saldo livre dos lotes não vencidos. Em cada lote: físico − reservado − bloqueado, com mínimo de zero.'}]
      .concat(cr.map(x=>({t:'Em custódia (fora do depósito, não soma no físico): '+x.rid+' · '+x.os+' · '+eq(x.it.custodia,un)+' com '+x.quem,h:'OS.dc.html'})))
      .concat(ex.q>1e-9?[{t:'Em conferência (exposição, fora do saldo até a decisão): '+ex.ids.join(', ')+' · '+eq(ex.q,un)+' além da custódia'}]:[]);
    const cos=cr.map(x=>x.os).join(', ');
    return {id,v:{nome:pr,prod:pr,un,local:locs,fis,res,blq,disp:dp,expo:ex.q>1e-9?ex.q:'',cust:ck,cos,val:''},s:{nome:pr,prod:pr,local:locs,un,cos},
      p:{nome:[{k:'b',t:pr},{k:'mut',t:ls.length+(ls.length>1?' lotes':' lote')}],prod:[{k:'mut',t:pr}],fis:[{k:'txt',t:eq(fis,un)}],res:res>1e-9?[{k:'txt',t:eq(res,un)}]:[{k:'mut',t:'—'}],
         blq:blq>1e-9?[{k:'chip',t:eq(blq,un),c:'yellow'}]:[{k:'mut',t:'—'}],disp:[{k:'b',t:eq(dp,un)}],expo:ex.q>1e-9?[{k:'txt',t:eq(ex.q,un)}]:[{k:'mut',t:'—'}],
         cust:ck>1e-9?[{k:'txt',t:eq(ck,un)}]:[{k:'mut',t:'—'}],cos:cos?[{k:'txt',t:cos}]:[{k:'mut',t:'—'}],vali:[{k:'mut',t:''}],sitl:[{k:'mut',t:''}]},o,
      kids:ls.map(l=>elotRow(C,l,ask,INV,GEST))}; });
  GR('g_lot').x0=x0;
  // ---- etapa 5: contagens ----
  let nacontar=0,naprov=0,nvelha=0;
  const cntOpts=elotes(C).map(elotLbl);
  GR('g_cnt').rows=INV.map(rec=>{ const l=C.lotes[rec.key]; const un=l?l.un:''; const has=econtou(rec); const d=has?rec.cont-rec.sis:null; const aj=eajuste(C,rec); const apr=!!(aj&&aj.estado==='Aprovado'); const vel=apr?null:evelha(C,rec);
    const r={id:rec.id,ro:apr||(d!==null&&Math.abs(d)<1e-9),v:{inv:rec.id,aj:aj?aj.id:'',prod:l?l.prod:'',un,lote:l?elotLbl(l):rec.key,local:l?l.local:'',sis:has?rec.sis:'',cont:has?rec.cont:'',dif:d===null?'':d,contador:rec.contador||'',causa:rec.causa||''},s:{},p:{}};
    // contagens anteriores ficam na origem da linha, visíveis só depois da nova contagem (a recontagem também é cega)
    r.o=has?(rec.hist||[]).map(h=>({t:'Contagem anterior: '+eq(h.cont,un)+' por '+h.contador+' · diferença '+esig(h.dif,un)+(h.causa?' · causa: '+h.causa:'')})):[];
    r.p.inv=[{k:'b',t:rec.id}]; r.s.inv=rec.id; r.s.aj=aj?aj.id:''; r.p.aj=aj?[{k:'txt',t:aj.id}]:[{k:'mut',t:'—'}];
    r.p.prod=[{k:'txt',t:l?l.prod:''}]; r.s.prod=l?l.prod:''; r.p.lote=[{k:'txt',t:l?l.lote:''}]; r.s.lote=l?l.lote:'';
    r.p.sis=has?[{k:'txt',t:eq(rec.sis,un)}]:[{k:'mut',t:'oculto até contar'}]; r.s.sis=has?eq(rec.sis,un):'oculto até contar';
    r.p.cont=has?[{k:'txt',t:eq(rec.cont,un)}]:[{k:'mut',t:'a contar'}];
    r.p.dif=d===null?[{k:'mut',t:'—'}]:[{k:'chip',t:(Math.abs(d)<1e-9?'0':esig(d,un)),c:(Math.abs(d)<1e-9?'green':'red')}];
    let sit; if(d===null){ sit={k:'chip',t:'A contar',c:'gray'}; nacontar++; } else if(Math.abs(d)<1e-9) sit={k:'chip',t:'Conferido',c:'green'};
    else if(apr) sit={k:'chip',t:'Ajuste aprovado',c:'green'}; else if(vel) { sit={k:'chip',t:'Desatualizada',c:'red'}; nvelha++; } else { sit={k:'chip',t:'Ajuste aguardando aprovação',c:'yellow'}; naprov++; }
    const semCausa=(d!==null&&Math.abs(d)>1e-9&&!apr&&!String(rec.causa||'').trim());
    r.p.sit=[sit].concat(vel?[{k:'mut',t:'contagem anterior a '+(vel.length?vel.length+(vel.length===1?' movimento':' movimentos')+' do lote':'mudança do físico')+' · reconte'}]:[]).concat(semCausa&&!vel?[{k:'mut',t:'informe a causa'}]:[]).concat(apr?[{k:'mut',t:'aplicado ao saldo'}]:[]).concat(apr&&aj.rev?[{k:'mut',t:aj.rev}]:[]); r.s.sit=sit.t;
    r.p.acao=(d!==null&&Math.abs(d)>1e-9&&!apr)?[{k:'act',t:'Recontar',fn:'recont:'+rec.id}].concat(vel?[]:GAJ?[{k:'act',t:'Aprovar ajuste',fn:'aprova:'+rec.id}]:[{k:'mut',t:'aprova: '+g2alcQuem('AL-09')}]):[]; r.s.acao=''; return r; });
  const fmC=g2st(self,'g_cnt').fm; const fsC=GR('g_cnt').edit.fields; fsC[0].opts=cntOpts; fsC[0].def=cntOpts[0]||''; fsC[0].ro=!!(fmC&&!fmC.isNew);
  // contagem salva fica travada (quantidade e contador); só a causa continua editável
  const rC=fmC&&fmC.rid?GR('g_cnt').rows.find(x=>x.id===fmC.rid):null; const trav=!!(rC&&!eblank(rC.v.cont));
  fsC[1].ro=trav; fsC[2].ro=trav; fsC[1].help=trav?'Travada depois de salvar: para conferir de novo, use Recontar na linha.':'';
  // ---- etapa 6: movimentos ----
  let nsin=0; const SEM=esemSinal(C), APPI=eappItens(C), AJU={}; (C.movs||[]).forEach(m=>{ if(m.aj) AJU[m.aj]=true; });
  GR('g_mov').rows=(C.movs||[]).slice().reverse().map(m=>{ const app=m.origem==='app'; const sem=!!SEM[m.id]; if(sem) nsin++;
    // itens do app (confirmação e consumo): um por linha, com a quantidade e a unidade na coluna Quantidade
    const li=APPI[m.id]||null; const q=li?li.map(x=>eq(x.qtd,x.un)).join(', '):emovQtd(m); const tp=emovTipo(m);
    const dc=emovDoc(C,m,AJU);
    // TABELAS-FOCO: registro, condição, documento, O.S., item, lote, quantidade, unidade e sinal em colunas próprias (itens do app: um por linha dentro da célula)
    const cond=m.tipo==='devolucao'?(m.apto?'apta':'bloqueada'):(m.tipo==='recebimento-nf'?(m.apto?'apto':'em quarentena'):'');
    const r={id:m.id,v:{hora:m.at,mid:m.id,tipo:tp,cond,doc:m.req||(dc&&dc.doc)||'',os:m.os||'',item:m.prod||'',lote:m.lote||'',qtd:'',un:'',quem:m.quem||'',orig:app?'App':'Web',sinal:sem?'Aguardando sinal':''},s:{},p:{}};
    r.p.hora=[{k:'b',t:m.at||''}]; r.s.hora=m.at||''; r.s.mid=m.id; r.s.cond=cond; r.p.cond=cond?[{k:'txt',t:cond}]:[{k:'mut',t:'—'}];
    r.p.tipo=[{k:'txt',t:tp}]; r.s.tipo=tp;
    const dd=m.req||(dc&&dc.doc)||''; r.p.doc=dd?[{k:'b',t:dd}].concat(!m.req&&dc&&dc.aj?[{k:'mut',t:dc.aj}]:[]):[{k:'mut',t:'—'}]; r.s.doc=[dd,!m.req&&dc&&dc.aj].filter(Boolean).join(' ');
    r.p.os=m.os?[{k:'link',t:m.os,h:'OS.dc.html'}]:[{k:'mut',t:'—'}]; r.s.os=m.os||'';
    const lin=(a)=>a.reduce((o,p,i)=>o.concat(i?[{k:'br'},p]:[p]),[]);
    r.p.lote=m.lote?[{k:'txt',t:m.lote}]:[{k:'mut',t:'—'}]; r.s.lote=m.lote||'';
    r.p.item=m.prod?[{k:'txt',t:m.prod}]:(li&&li.length?lin(li.map(x=>({k:'txt',t:x.prod}))):(m.det?[{k:'mut',t:m.det}]:[{k:'mut',t:'—'}]));
    if(Array.isArray(m.conf)){ const ks=(C.confs||[]).filter(k=>m.conf.indexOf(k.id)>=0); r.p.item=(li&&li.length?r.p.item.concat([{k:'br'}]):[]).concat(ks.map(k=>({k:'mut',t:k.prod+' '+eq(k.relatado,k.un)+' em conferência ('+k.id+')'}))); }
    r.s.item=m.prod||(li?li.map(x=>x.prod).join(', '):'')||m.det||'';
    // quantidade com a unidade junto (decisão do proprietário, 05/10/2026); v.qtd numérico ordena; vários itens do app → uma linha por item
    if(li&&li.length){ r.p.qtd=lin(li.map(x=>({k:'txt',t:eq(x.qtd,x.un)}))); r.s.qtd=li.map(x=>eq(x.qtd,x.un)).join(', ');
      // valor para ordenar: a soma quando todos os itens têm a mesma unidade; com unidades diferentes não há soma (NaN: vai para o fim)
      const us=[...new Set(li.map(x=>x.un))]; r.v.qtd=us.length===1?li.reduce((a,x)=>a+(Number(x.qtd)||0),0):NaN;
      if(li.length===1) r.v.qtd=li[0].qtd; }
    else { const mq=String(q||'').match(/^([+−-]?[\d.]+(?:,\d+)?)\s*(.*)$/); if(mq){ const ut=String(mq[2]||'').split(' '), u0=ut[0]||'', resto=ut.slice(1).join(' ');   // "320 L reservados": unidade L, condição reservados
        r.v.qtd=Number(mq[1].replace(/\./g,'').replace(',','.').replace('−','-').replace('+','')); r.v.un=u0; r.p.qtd=[{k:'txt',t:mq[1]+(u0?' '+u0:'')}]; r.s.qtd=r.p.qtd[0].t;
        if(resto&&!cond){ r.v.cond=resto; r.s.cond=resto; r.p.cond=[{k:'txt',t:resto}]; } }
      else { r.p.qtd=q?[{k:'txt',t:q}]:[{k:'mut',t:'—'}]; r.s.qtd=q; } }
    r.p.orig=[{k:'chip',t:app?'App':'Web',c:app?'blue':'gray'}]; r.s.orig=app?'App':'Web'; r.p.sinal=sem?[{k:'chip',t:'Aguardando sinal',c:'yellow'}]:[{k:'mut',t:'—'}]; r.s.sinal=sem?'Aguardando sinal':'';
    r.o=(m.os?[{t:(m.req?'Requisição '+m.req+' da ':'Ordem ')+m.os,h:'OS.dc.html'}]:[]).concat(sem?[{t:'Registrado no aparelho às '+m.at+'; chega ao servidor quando o app tiver sinal.'}]:[]).concat(m.obs?[{t:'Observação: '+m.obs}]:[]);
    return r; });
  // filtro e busca das quantidades leem o mesmo texto da célula, com a unidade ("60.000 kg"); a ordenação usa o número (v)
  const esq=(rows,fs)=>(rows||[]).forEach(r=>{ fs.forEach(f=>{ const c=((r.p||{})[f]||[])[0]; if(c&&(r.s||{})[f]===undefined){ r.s=r.s||{}; r.s[f]=(c.k==='mut'||c.t==='—')?'':c.t; } }); esq(r.kids,fs); });   // '—' na célula = vazio no filtro
  esq(GR('g_rec').rows,['qtd_nf','conf','apto','quar']); esq(GR('g_ent').rows,['sol','ent','pend']); esq(GR('g_dev').rows,['ent','cons','dev','cust']);
  esq(GR('g_lot').rows,['fis','res','blq','disp','expo','cust']); esq(GR('g_cnt').rows,['cont','dif']);
  v.mov_tem=GR('g_mov').rows.length>0; v.mov_nada=!v.mov_tem;
  // ---- resumos por etapa ----
  const pdTxt=PD.filter(p=>p.a_entregar>0).map(p=>p.id+' '+eq(p.a_entregar,p.un));
  v.k1=(npend?npend+(npend>1?' notas a conferir':' nota a conferir'):'Nenhuma nota a conferir')+' · '+(quarTxt.length?'em quarentena: '+quarTxt.join(', '):'nenhum lote em quarentena')+' · pedidos com saldo a entregar: '+(pdTxt.join(', ')||'nenhum');
  v.k2=nent+(nent===1?' item a entregar':' itens a entregar')+' · '+nag+' aguardando confirmação no app · '+ncons+' só consulta (O.S. fora de Liberadas e Em execução)'
    +(nimp?' · '+nimp+(nimp===1?' bloqueado por O.S. impedida':' bloqueados por O.S. impedida'):'');
  v.k3=(CFS.length?'Consumo em conferência: '+CFS.map(k=>k.os+' · '+cenConfTxt(k,C)).join(' · ')+' · '+CFS[0].resp+' confere ou recusa o relato; '+g2alcQuem('AL-10','acima')+' aceita o excedente · ':'')+(custs.length?('Em custódia: '+custs.map(x=>x.rid+' '+eq(x.it.custodia,x.un)+' de '+x.it.prod+' com '+x.quem+' ('+x.os+')').join(' · ')):'Nenhum material em custódia. Todas as O.S. podem conciliar materiais.');
  v.k4=(inspTxt.length?'Bloqueado para inspeção: '+inspTxt.join(', '):(vencTxt.length?'Nenhum lote aguardando inspeção':'Nenhum lote bloqueado'))
    +(vencTxt.length?' · vencido, fora do disponível: '+vencTxt.join(', '):'')+' · custódia fica fora do depósito e não soma no físico';
  v.k5=nacontar+(nacontar===1?' contagem a fazer':' contagens a fazer')+' · '+naprov+(naprov===1?' ajuste aguardando aprovação':' ajustes aguardando aprovação')+(nvelha?' · '+nvelha+(nvelha===1?' contagem desatualizada a recontar':' contagens desatualizadas a recontar'):'');
  v.k6=(C.movs||[]).length+((C.movs||[]).length===1?' movimento':' movimentos')+' desde o início da demonstração · '+nsin+' aguardando sinal do app';
}
/* atalho da devolução guiada (rodada 3, I-c1): EST.dc.html#dev=<REQ>&para=<OB pedinte>&ver=<versão>&sob=<sobra> abre Receba devoluções com o
   formulário da linha aberto; a sobra e a fase de quando abriu ficam para a revalidação no Salvar (BEN-D13 superada só para #dev) */
function estDevHash(self){ if(self.__estDevH) return; self.__estDevH=1; const ab=()=>{ let h=''; try{ h=decodeURIComponent(location.hash||'').slice(1); }catch(e){} if(!/^dev=/.test(h)) return;
    const q={}; h.split('&').forEach(kv=>{ const i=kv.indexOf('='); if(i>0) q[kv.slice(0,i)]=kv.slice(i+1); }); const C=cenGet(); const r=C.reqs[q.dev]; const it=r&&r.itens.find(i=>i.prod===BENC.cx.item); const o=r&&C.ordens[r.os];
    if(!it||!o) return; self._estDev={rid:q.dev,para:q.para||'',ver:q.ver||'',sob:q.sob!==undefined&&q.sob!==''&&isFinite(Number(q.sob))?Number(q.sob):benCxSobra(C,o),etapa:o.etapa};
    setTimeout(()=>{ g2etapa(self,{step:3,est_volta:null}); setTimeout(()=>g2open(self,GR('g_dev'),q.dev+'|'+it.prod,null),60); },0); };
  ab(); try{ window.addEventListener('hashchange',ab); }catch(e){} }
function EXTRAVALS(self,v){ estDevHash(self);
  self.g2perfilFecha={est_cfask:null,libask:null,lib_laudo:'',lib_mot:'',lib_err:''};   /* trocar o perfil fecha o aceite do consumo e o laudo da quarentena (com o motivo) */
  v.dev_volta_on=!!self.state.est_volta&&!!EST_BEN_H; v.dev_volta_h=EST_BEN_H?EST_BEN_H+'#'+(self.state.est_volta||''):'#'; v.dev_volta_t='Voltar à '+(self.state.est_volta||'');
  const st=self.state; const step=st.step||1; const N=6; const C=self._cen||cenGet();
  self.g2live=(gid,k,d)=>{ if(gid==='g_rec'&&k==='val'&&efert(d.ped)) return 'Sem validade'; return undefined; };
  for(let i=1;i<=N;i++) v['s'+i]=(step===i);
  // seções do Estoque (UX-ACAO-UNICA-20261003): trabalho paralelo, navegação em qualquer ordem pela faixa de seções (único caminho);
  // sem setas e sem "ir para a próxima seção" como ação principal: a ação do bloco é o próximo trabalho da própria seção, ou nenhuma
  g2secoes(self,v,'stp',N,step,{},(i)=>g2etapa(self,{step:i}));
  const IT=eitens(C); let prim;
  if(v.est_vazio) prim=['Ver Santa Rita',v.est_versr];
  else if(step===1){ const r=GR('g_rec').rows.find(x=>!x.ro); prim=r?['Conferir '+r.v.nf,()=>g2open(self,GR('g_rec'),r.id,null)]:['Registrar recebimento',()=>v.g_rec_new&&v.g_rec_new()]; }
  else if(step===2){ const r=GR('g_ent').rows.find(x=>!x.ro); prim=r?['Entregar '+r.v.req+' · '+r.v.item,()=>g2open(self,GR('g_ent'),r.id,null)]:null; }
  else if(step===3){ const D=self._estDev; const xs=IT.filter(y=>y.it.custodia>1e-9&&!y.sinal&&!y.cf&&!(y.ben&&!(y.dp>0))).sort((a,b)=>((D&&a.rid===D.rid?0:1)-(D&&b.rid===D.rid?0:1))||((a.o.etapa==='Em conferência'?0:1)-(b.o.etapa==='Em conferência'?0:1))||(ereqN(a.rid)-ereqN(b.rid))); const x=xs[0];
    prim=x?['Receber devolução da '+x.rid,()=>g2open(self,GR('g_dev'),x.id,null)]:null; }
  else if(step===4) prim=null;   // saldos: consulta (sem primária)
  else if(step===5){ const r=GR('g_cnt').rows.find(x=>eblank(x.v.cont)); prim=r?['Contar '+r.v.inv,()=>g2open(self,GR('g_cnt'),r.id,null)]:['Nova contagem',()=>v.g_cnt_new&&v.g_cnt_new()]; v.cnt_add=!!r; }
  else prim=null;   // movimentos: consulta
  v.prim_t=prim?prim[0]:''; v.prim_fn=prim?prim[1]:(()=>{});
  v.prim_st='padding:7px 14px;border-radius:9px;font-size:13px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap;background:#1E7A4C;color:#fff;border:1px solid #1E7A4C;flex-shrink:0;'+((v.est_vazio||!prim)?'display:none;':'');   // sem estoque: o próximo passo é o link do estado vazio
  // filtro por local (etapa 4)
  const loc=st.est_loc||''; const CH='font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;';
  v.est_locs=[''].concat(E2.locais).map(lc=>({t:lc||'Todos os locais',on:String(loc===lc),st:CH+(loc===lc?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;'),go:()=>self.setState({est_loc:lc})}));
  // liberar quarentena do lote após inspeção (confirmação na linha; repetir não soma de novo)
  // (gestor, com o nº do laudo; sem laudo ou sem papel nada muda e o erro fica no painel, com o laudo digitado preservado)
  const lk=st.libask; const lq=lk&&C.lotes[lk]; v.lib_on=!!(lq&&lq.quarentena>1e-9)&&g2papel(g2perfil(),g2alc('AL-11').papeis);   /* aberto por outro perfil: não aparece (achado 1) */
  const lqp=lq?(lq.quarentena||0)-Math.min(lq.quarentena||0,lq.quarRep||0):0;
  v.lib_t=v.lib_on?('Liberar '+eq(lqp,lq.un)+' do lote '+lq.lote+' ('+lq.prod+'): informe o laudo que aprova o material. Se o laudo reprovar, use "Reprovar com o laudo": o material fica segregado para devolução ao fornecedor e a falta deixa de ser condicionada.'):'';
  v.lib_mot=st.lib_mot||''; v.lib_setmot=(e)=>self.setState({lib_mot:e.target.value,lib_err:''});
  v.lib_rep=()=>{ const k=self.state.libask; const r=cenMudar(null,c=>cenReprovarQuarentena(c,k,self.state.lib_laudo,self.state.lib_mot,g2perfil()));
    if(r.erro){ self.setState({lib_err:r.erro}); return; } self.setState({libask:null,lib_laudo:'',lib_mot:'',lib_err:'',cenrev:Date.now(),g2toast:r.msg}); };
  v.lib_laudo=st.lib_laudo||''; v.lib_setlaudo=(e)=>self.setState({lib_laudo:e.target.value,lib_err:''}); v.lib_err=st.lib_err||''; v.lib_hasErr=!!st.lib_err;
  /* laudo e motivo são do lote aberto: abrir outro lote, manter bloqueado ou decidir limpam os dois (revisão do 16fb55e, ajuste 3; dano evitado:
     gravar em um lote o motivo digitado para outro) */
  v.libq=(k)=>{ self.setState({libask:k,lib_laudo:'',lib_mot:'',lib_err:''}); setTimeout(()=>{ const e=document.getElementById('est-laudo'); if(e) e.focus(); },0); };
  v.libno=()=>self.setState({libask:null,lib_laudo:'',lib_mot:'',lib_err:''});
  v.lib_ok=()=>{ const k=self.state.libask; const c0=cenGet(); const l0=c0.lotes[k]; const antes=l0?eitemDisp(c0,l0.prod):0;
    const r=cenMudar(null,c=>{ const lv=c.lotes[k]; if(evenc(lv)) throw new Error('Lote '+lv.lote+' vencido em '+lv.validade+': fica bloqueado e não volta ao disponível.');
      const r=cenLiberarQuarentena(c,k,self.state.lib_laudo,g2perfil()); const L=c.lotes[k]; return {msg:r.msg+' Disponível de '+L.prod+': '+eq(antes,L.un)+' → '+eq(eitemDisp(c,L.prod),L.un)+'.'}; });
    if(r.erro){ self.setState({lib_err:r.erro}); return; }
    self.setState({libask:null,lib_laudo:'',lib_mot:'',lib_err:'',cenrev:Date.now(),g2toast:r.msg}); };
  // aprovar ajuste (causa obrigatória; aplica uma vez) e recontar (outro contador, contagem cega)
  v.aprova=(id)=>{ const rec=einvRec(cenGet(),id);
    if(rec&&econtou(rec)&&!String(rec.causa||'').trim()){ g2open(self,GR('g_cnt'),id,null); self.setState({g2toast:'Informe a causa da diferença de '+id+' na contagem antes de aprovar o ajuste.'}); return; }
    cenMudar(self,c=>estAprovar(c,id,g2perfil())); };
  v.recont=(id)=>{ const r=cenMudar(self,c=>estRecontar(c,id,g2perfil())); if(r.erro) return; const c1=cenGet(); const rec=einvRec(c1,id); const l=c1.lotes[rec.key];
    const draft={lote:l?elotLbl(l):'',cont:'',contador:rec.contador,causa:''};
    g2set(self,'g_cnt',{fm:{rid:id,draft,orig:Object.assign({},draft),errs:{},warn:false,ro:false,isNew:false,mode:'form'},fl:null,fmc:null}); };
  v.cfa=(id)=>self.setState({est_cfask:id}); v.cfno=()=>self.setState({est_cfask:null});
  v.cfok=(id)=>{ const r=cenMudar(self,c=>cenConciliar(c,id,true,undefined,g2perfil())); if(!r.erro) self.setState({est_cfask:null}); };
  v.cfr=(id)=>{ cenMudar(self,c=>cenConciliar(c,id,false,'registro sem fato físico',g2perfil())); self.setState({est_cfask:null}); };
  // restaurar a demonstração (cenário compartilhado volta ao início)
  v.est_rst_ask=!!st.est_rst; v.est_rst_no=!st.est_rst;
  v.est_rst=()=>self.setState({est_rst:true}); v.est_rst_cancel=()=>self.setState({est_rst:false});
  v.est_rst_ok=()=>{ cenReset(); self.setState({est_rst:false,g2:{},libask:null,lib_laudo:'',lib_mot:'',est_loc:'',cenrev:Date.now(),g2toast:'Demonstração restaurada: O.S., estoque e app voltaram ao início.'}); };
  // textos do formulário conforme o registro aberto
  const Fr=v.g_rec_F; if(Fr&&Fr.open&&Fr.ro) Fr.sub='Recebimento conferido: consulta. Documento já lançado não cria segunda entrada; a quarentena é liberada no lote, em Confira saldos.';
  const Fe=v.g_ent_F; const fmE=g2st(self,'g_ent').fm; if(Fe&&Fe.open&&fmE){ const x=IT.find(y=>y.id===fmE.rid); if(x){
      const bq=String(x.bloq).replace(/\.$/,'');
      if(x.bloq) Fe.sub=x.it.entregue>0?('Bloqueada: '+bq+'. Nova entrega só com a O.S. apta; o que já foi entregue continua registrado.'):('Bloqueada: '+bq+'. Só O.S. liberada ou em execução recebe material; nada foi entregue.');
      else if(!x.pode) Fe.sub='Consulta: '+x.motivo+'. Entregue só para O.S. liberada ou em execução; sobras e custódia ficam em Receba devoluções.';
      else if(!x.l) Fe.sub='Sem lote de '+x.it.prod+' no estoque: receba a nota antes de entregar.';
      else if(x.pend<=1e-9) Fe.sub='Entrega completa: '+econta(x)+' = 0. Sobras e custódia ficam em Receba devoluções.';
      else Fe.sub='Entregue '+x.it.prod+' à '+x.os+' ('+(x.o.tipo||'')+'), do lote '+x.l.lote+(x.it.emb?' em '+x.it.emb:'')+'. O material fica com quem recebe e aguarda a confirmação no app.'; } }
  const Fd=v.g_dev_F; const fmD=g2st(self,'g_dev').fm;
  /* revisão A8: o que a pessoa viu ao abrir o formulário de devolução de uma linha do BEN, por qualquer caminho (no #dev, a sobra e a fase do endereço) */
  if(!fmD) self._estDevVi=null; else { const xv=IT.find(y=>y.id===fmD.rid); if(xv&&xv.ben&&!(self._estDevVi&&self._estDevVi.id===fmD.rid)){ const D0=self._estDev&&self._estDev.rid===xv.rid?self._estDev:null;
    self._estDevVi={id:fmD.rid,sob:D0?D0.sob:benCxSobra(C,xv.o),etapa:D0?D0.etapa:xv.o.etapa,mov:xv.it.entregue-xv.it.devolvido}; } }
  if(Fd&&Fd.open&&fmD){ const x=IT.find(y=>y.id===fmD.rid); if(x){
      const D=self._estDev&&self._estDev.rid===x.rid?self._estDev:null; const sb=x.ben&&x.it.custodia>1e-9?benCxSobra(C,x.o):0;
      /* revisão A7: o texto segue a fase (conferida: a custódia volta ao lote e o que passar da sobra fica reservado só até o Fechar; não é "tudo registrado" nem "caixas em uso") */
      const cfx=x.ben&&x.o.etapa==='Em conferência'&&!!(x.o.ben&&x.o.ben.conf);
      const bt=!x.ben||x.it.custodia<=1e-9?'':(x.dp>0&&x.dp>=x.it.custodia-1e-9&&x.o.etapa==='Em conferência'&&sb<x.dp?(cfx?' '+x.os+' conferida: a custódia inteira volta ao lote '+x.it.lote+(sb>0?'; '+eq(sb,x.un)+' ficam livres (sobra) e o resto fica reservado':' e fica reservada')+' à '+x.os+' até o Fechar.'
          :' '+x.os+' com tudo registrado (conferência): a custódia inteira volta ao lote '+x.it.lote+'; o que passar da sobra ('+eq(sb,x.un)+') fica reservado à '+x.os+' até o Fechar.')
        :(sb>0?' '+esobTxt(C,x.o).replace('Sobra da '+x.os+':','Sobra da '+x.os+(D&&D.para?' para a '+D.para:'')+':')+'. Apta, volta livre ao lote '+x.it.lote+'; o que passar de '+eq(sb,x.un)+' volta reservado à '+x.os+(cfx?' até o Fechar.':' (caixas em uso).')
        :' A '+x.os+' ainda embala '+benKg(benKgAberto(x.o))+' (até '+eq(benCxUsoMax(x.o),x.un)+') e não tem sobra: o que for devolvido volta reservado à '+x.os+' (caixas em uso) no lote '+x.it.lote+'.'));
      Fd.sub=(x.it.custodia<=1e-9?'Sem material em custódia neste item.':x.sinal?('Em custódia: '+eq(x.it.custodia,x.un)+' de '+x.it.prod+' com '+x.quem+' ('+x.os+'). O apontamento do turno está no aparelho, aguardando sinal: receba a sobra depois do envio.'):('Em custódia: '+eq(x.it.custodia,x.un)+' de '+x.it.prod+' com '+x.quem+' ('+x.os+'). Confira e receba: só o conferido volta ao lote '+x.it.lote+'.'))+bt; } }
  const Fc=v.g_cnt_F; const fmC=g2st(self,'g_cnt').fm; if(Fc&&Fc.open&&fmC){ const rc=fmC.rid?GR('g_cnt').rows.find(x=>x.id===fmC.rid):null;
    Fc.sub=fmC.ro?'Contagem encerrada: consulta.':((rc&&!eblank(rc.v.cont))?'Contagem registrada: quantidade e contador ficam travados. Informe a causa da diferença; para conferir de novo, use Recontar na linha.'
      :'Contagem cega: informe só o que contou. A diferença para o sistema aparece depois de salvar e vira ajuste para aprovação.'); }
  const Fl=v.g_lot_F; if(Fl&&Fl.open) Fl.sub='Saldo calculado pelos movimentos abaixo. Para mudar, receba, entregue, devolva ou conte.';
  const Fm=v.g_mov_F; const fmM=g2st(self,'g_mov').fm; if(Fm&&Fm.open&&fmM){ const m=(C.movs||[]).find(x=>x.id===fmM.rid); if(m) Fm.sub='Movimento '+m.id+' registrado '+(m.origem==='app'?'no app':'na web')+' às '+m.at+(esemSinal(C)[m.id]?' · aguardando sinal.':'.'); }
}
'''

