# -*- coding: utf-8 -*-
"""Suprimentos › Estoque (EST.dc.html) · Suprimentos simplificado (docs/suprimentos-simplificado; pedido do proprietário de 05/10/2026:
"simplifique também o fluxo do processo e botões de ação que resolvam tudo em menos telas").
4 seções em qualquer ordem (eram 6), cada uma com o contador neutro do que espera ação:
  Atenda requisições (entrega, devolução e consumo em conferência no mesmo registro) · Receba e inspecione (nota prevista e parcela em quarentena,
  com laudo) · Faça contagens (cega; ajuste decidido pela gestora) · Confira saldos (Lotes | Movimentos | Produção, só consulta).
A linha identifica, o painel resolve (SUP §2.3): nenhuma linha de grade carrega botão de comando; o painel do registro tem uma primária com o rótulo
que confirma o quê, quanto, lote e para quem, e um comando com chave de quem inicia (toque duplo não repete; mudança de outra tela é conflito).
Endereços: #sec=<seção ou apelido>, #req=, #os=, #nf=, #lote= (abrir nunca muda o cenário). Sem endereço, abre pelo perfil de quem age (menu lateral,
G2_PERFIS do CTL-3): contador com contagem atribuída → Faça contagens; gestora → 1ª seção com decisão dela; almoxarife → 1ª com pendência.
Regras e leitura do cenário em est.js (o mesmo arquivo da tela e dos testes em node); mudanças só por cenMudar. Os registros de base (notas, pedidos,
contagens antigas) vêm de dados2; locais e pessoas da fonte única (dados_cad)."""
import json, os
from engine import (grid,esc,INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,DISP,BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, secoes_state, HEIGHTS37
import dados2 as D2
import dados_cad as DC
import cenario

HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
NOMES=['Atenda requisições','Receba e inspecione','Faça contagens','Confira saldos']
# apelidos de endereço (#sec=…): os nomes das 6 seções antigas e os usados pela BEN e pelo PCM levam à seção nova; desconhecido → regra sem endereço
SEC={'requisicoes':1,'requisições':1,'entregas':1,'devolucoes':1,'devoluções':1,'atenda':1,'recebimentos':2,'receba':2,'inspecao':2,'laudos':2,
     'contagens':3,'contagem':3,'saldos':4,'lotes':4,'movimentos':4,'producao':4,'produção':4}
SEC_MODO={'movimentos':'movs','producao':'prod','produção':'prod','lotes':'lotes','saldos':'lotes'}

# ---------------- constantes locais (coerentes com dados2/cenário) ----------------
LOCAL_REC={'KCl 60%':'Galpão 2','Semente de soja 58 W':'Câmara fria','Semente de soja 62 X':'Câmara fria'}
# mesma palavra para a mesma pessoa em toda a tela: Rui é o almoxarife que entrega e recebe (cenario.js) e também conta
CONTADORES=['Paula (almoxarife)','Rui (almoxarife)']
CONDS=['Apta · volta ao disponível','Bloqueada para inspeção · vai para quarentena']
DIVS=['Sem divergência','Falta','Sobra','Avaria','Item diferente do pedido']
RESULTADOS=['Aprovado','Reprovado']
CAUSA_BASE={'INV-2609':'Sacaria rasgada na pilha 3'}
SEM_VALIDADE=['Fertilizantes','Corretivos','Embalagens']    # grupos recebidos sem validade de lote (caixa do packing: BEN-D23)
CONTADOR_BASE={'INV-2609':'Rui (almoxarife)','INV-2610':'Paula (almoxarife)'}
# O.S. impedida (selo "Impedida" no cenário): a ordem de manutenção que impede vem do registro da manutenção
IMPED={'OS-0420':dict(selo='O.S. impedida · OM-0233',
                      txt='OS-0420 impedida pela OM-0233 (Trator T1 bloqueado): entregue quando o ativo for liberado ou substituído na O.S.')}
# locais estocáveis de insumo, da fonte única (dados_cad.LOCAIS; com Packing e Armazém Sede); tanque e silo têm controle próprio (diesel, grão).
# Packing (l8): guarda as caixas do beneficiamento (CX26-01 e a NF 7731, BEN-D23); a fruta em processo fica no estado da Produção, não aqui
TIPOS_ESTOQUE=('Galpão','Almoxarifado','Câmara fria','Armazém','Packing')

def _forn(fid): return next((f['nome'] for f in D2.FORNECEDORES if f['id']==fid),fid)
# pedidos e notas que o Estoque recebe: os de Compras (dados2) e os de caixa do packing (dados_ben, BEN-D23: a compra de caixa é do BEN-2,
# por isso o pedido não vem de Compras; cmp=False marca o pedido que Compras não lista)
def _pedidos():
    import dados_ben as DB
    return [dict(p,cmp=True) for p in D2.PEDIDOS]+[dict(p,cmp=False) for p in DB.PEDIDOS_CX]
def _notas():
    import dados_ben as DB
    return list(D2.RECEBIMENTOS)+list(DB.NFS_CX)
def _ped_label(p): return f"{p['id']} · {p['item']} · {_forn(p['f'])}"

def bloco(titulo,desc,corpo,acao=''):
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px; flex-wrap: wrap;"><div style="display: flex; flex-direction: column; gap: 2px; flex: 1 1 220px; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{esc(titulo)}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>{acao}</div>'
            f'<div style="padding: 0 12px 12px;">{corpo}</div></section>')
def navpe():
    lk=f'border: 0; background: transparent; color: {MUTED}; font-family: inherit; font-size: 12px; font-weight: 600; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; padding: 4px;'
    return (f'<div style="display: flex; align-items: center; gap: 10px; padding-top: 4px;">'
            f'<span style="flex-grow: 1;"></span>'
            f'<sc-if value="{H("est_rst_no")}" hint-placeholder-val="{H("true")}"><button type="button" onClick="{H("est_rst")}" style="{lk}">Restaurar demonstração</button></sc-if>'
            f'<sc-if value="{H("est_rst_ask")}" hint-placeholder-val="{F()}"><span style="font-size: 12px; color: {MUTED};">Volta O.S., estoque e app ao início da demonstração.</span>'
            f'<button type="button" onClick="{H("est_rst_ok")}" style="{_MINI} color: {RED}; border-color: {RED};">Restaurar</button><button type="button" onClick="{H("est_rst_cancel")}" style="{_MINI}">Manter</button></sc-if>'
            + '</div>')
def chips(lista,rotulo):
    return (f'<div role="group" aria-label="{esc(rotulo)}" style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px;">'
            f'<sc-for list="{H(lista)}" as="ch" hint-placeholder-count="3"><button type="button" aria-pressed="{H("ch.on")}" onClick="{H("ch.go")}" style="{H("ch.st")}">{H("ch.t")}</button></sc-for></div>')

def _dados_js():
    PS=_pedidos()
    peds=[dict(id=p['id'],item=p['item'],un=p['un'],grupo=p.get('grupo',''),forn=_forn(p['f']),a_entregar=p['a_entregar'],label=_ped_label(p),cmp=p['cmp']) for p in PS]
    recs=[]
    for r in _notas():
        p=next(x for x in PS if x['id']==r['pedido']); prev='previsto' in r['data']
        recs.append(dict(id='r'+r['id'].split()[-1],nf=r['id'],data=('previsto '+r['data'].split()[0]) if prev else r['data'],ped=_ped_label(p),item=r['item'],un=r['un'],
                         qtd_nf=r['qtd_nf'],conf=r['qtd_conf'],apto=r['apto'],quar=r['quarentena'],lote=r['lote'],val='',local=r.get('local') or LOCAL_REC.get(r['item'],'Galpão 2'),
                         div='Sem divergência',obs=('Laudo de umidade pendente' if r['quarentena'] else ''),ok=r['qtd_conf'] is not None))
    chave={l['lote']:l['item']+'|'+l['lote'] for l in D2.LOTES}
    conts=[dict(id=c['id'],key=chave[c['lote']],sis=(c['sistema'] if c['contado'] is not None else None),cont=c['contado'],
                contador=CONTADOR_BASE.get(c['id'],CONTADORES[0]),causa=CAUSA_BASE.get(c['id'],''),aj=None,hist=[]) for c in D2.CONTAGENS]
    locais=[dict(id=l[0],nome=l[1],faz=l[2],tipo=l[3]) for l in DC.LOCAIS]   # id: o local da ordem de beneficiamento (o.ben.local) aponta o id
    pessoas=[p['nome'] for p in DC.PESSOAS]
    return dict(hoje=D2.HOJE,pedidos=peds,recs=recs,contagens=conts,conds=CONDS,contadores=CONTADORES,sem_validade=SEM_VALIDADE,imped=IMPED,
                locais=locais,tipos_estoque=list(TIPOS_ESTOQUE),pessoas=pessoas,sec=SEC,sec_modo=SEC_MODO,nomes=NOMES,divs=DIVS,resultados=RESULTADOS)

def build():
    fname='EST.dc.html'; E._reset_screen(fname)
    # ---------- Atenda requisições · requisição › item (funde as antigas "Entregue por O.S." e "Receba devoluções"; sem coluna de ação) ----------
    # uma variável por coluna; a quantidade leva a unidade junto ("65 L"); fase, solicitado, entregue, consumido, embalagem e detalhe vão para o painel
    # só as colunas essenciais (proprietário, 10/10): identificação (requisição e O.S.), situação, os números que decidem (a entregar, em custódia) e
    # quem retira ou devolve; o lote vai para o painel ("Separe:" e a conta do item) e continua achável pela busca
    g_req=grid([dict(k='req',l='Requisição › item',w=190),dict(k='sit',l='Situação',w=200),dict(k='ent',l='A entregar',t='num',a='r'),dict(k='cust',l='Em custódia',t='num',a='r'),
                dict(k='com',l='Com quem'),dict(k='os',l='O.S.')],
        [],edit=dict(m='form',title='',sub='',
            fields=[dict(k='quemr',l='Recebedor',t='sel',dyn=True,cond=dict(k='modo',eq='req'),help='Herdado do responsável da O.S.; troque se outra pessoa retira.'),
                    dict(k='qtd',l='Quantidade a entregar',t='num',min=0.001,cond=dict(k='modo',eq='ent')),
                    dict(k='quem',l='Recebedor',t='sel',dyn=True,cond=dict(k='modo',eq='ent')),
                    dict(k='dqtd',l='Quantidade conferida',t='num',min=0.001,cond=dict(k='modo',eq='dev')),
                    dict(k='cond',l='Condição',t='sel',opts=CONDS,cond=dict(k='modo',eq='dev')),
                    dict(k='obs',l='Observação',t='area',cond=dict(k='modo',eq='dev'),help='Obrigatória quando bloqueada para inspeção.'),
                    dict(k='mot',l='Motivo da recusa',t='area',cond=dict(k='modo',eq='rec'),help='O relato fica no histórico com o porquê; o saldo não muda.')]),
        tree=True,gid='g_req',total=False,qf=dict(k='sit',cut=' · '))
    # ---------- Receba e inspecione · nota prevista e parcela em quarentena (só trabalho do almoxarife e da gestora; o pedido fica em Compras) ----------
    # colunas essenciais (10/10): documento › item (a nota e o que ela traz; na parcela, o item e o lote), situação, os números que decidem (na nota,
    # em quarentena) e a previsão; o pedido e o fornecedor vão para o painel da nota e da parcela e continuam achados pela busca. A coluna Item
    # repetia a identificação (o rótulo "Documento › item" mostrava o pedido): saiu, e a célula do documento passou a mostrar o item
    g_rec=grid([dict(k='doc',l='Documento › item',w=230),dict(k='sit',l='Situação',w=150),dict(k='qtd_nf',l='Na nota',t='num',a='r'),
                dict(k='quar',l='Em quarentena',t='num',a='r'),dict(k='prev',l='Previsão',t='date')],
        [],edit=dict(m='form',title='',newTitle='Registrar NF recebida',sub='',
            fields=[dict(k='ped',l='Pedido',t='sel',dyn=True,cond=dict(k='modo',eq='nf')),
                    dict(k='nf',l='Nota fiscal',t='txt',cond=dict(k='modo',eq='nf'),help='Documento já lançado não cria segunda entrada.'),
                    dict(k='qtd_nf',l='Quantidade na nota',t='num',min=0.01,cond=dict(k='modo',eq='nf')),
                    dict(k='conf',l='Quantidade conferida',t='num',min=0,cond=dict(k='modo',eq='nf')),
                    dict(k='quar',l='Em quarentena',t='num',min=0,cond=dict(k='modo',eq='nf'),help='Começa em 0; o que ficar aqui só sai com o laudo.'),
                    dict(k='apto',l='Apta (calculada)',t='num',ro=True,live=True,cond=dict(k='modo',eq='nf'),help='Conferida − quarentena: entra no disponível.'),
                    dict(k='lote',l='Lote',t='txt',cond=dict(k='modo',eq='nf')),
                    dict(k='val',l='Validade do lote',t='txt',live=True,cond=dict(k='modo',eq='nf'),help='Mês/ano (ex.: 06/2027). Lote vencido entra todo em quarentena.'),
                    dict(k='local',l='Local',t='sel',dyn=True,cond=dict(k='modo',eq='nf')),
                    dict(k='div',l='Divergência',t='sel',opts=DIVS,cond=dict(k='modo',eq='nf')),
                    dict(k='obs',l='Motivo da quarentena ou da divergência',t='area',cond=dict(k='modo',eq='nf'),help='Obrigatório quando houver quarentena ou divergência.'),
                    dict(k='laudo',l='Nº do laudo',t='txt',cond=dict(k='modo',eq='laudo')),
                    dict(k='res',l='Resultado',t='sel',dyn=True,cond=dict(k='modo',eq='laudo')),
                    dict(k='dest',l='Destino (reprovado)',t='txt',cond=dict(k='modo',eq='laudo'),help='Ex.: devolver ao fornecedor, descartar com laudo.')]),
        gid='g_rec',total=False,qf=dict(k='sit',cut=' · '))
    # ---------- Faça contagens · contagem cega (sistema e diferença só depois de salvar) ----------
    # colunas essenciais (10/10): o que contar e onde (item, lote, local), a situação e a diferença que a gestora decide; o contado fica no painel
    g_cnt=grid([dict(k='inv',l='Contagem'),dict(k='sit',l='Situação',w=170),dict(k='prod',l='Item',w=160),dict(k='lote',l='Lote'),dict(k='local',l='Local'),
                dict(k='dif',l='Diferença',t='num',a='r')],
        [],edit=dict(m='form',title='',sub='',
            fields=[dict(k='cont',l='Quantidade contada',t='num',min=0,cond=dict(k='modo',eq='contar')),
                    dict(k='causa',l='Causa da diferença',t='area',cond=dict(k='modo',eq='causa'),help='Obrigatória: vai com o ajuste para a gestora.')]),
        gid='g_cnt',total=False,qf=dict(k='sit',cut=' · '))
    # ---------- Confira saldos · Lotes (uma linha por lote), Movimentos (trilha) e Produção (produto acabado da Colheita) ----------
    # colunas essenciais (10/10): o que tenho (físico) e o que posso usar (disponível), com a validade; reservado e bloqueado explicam a diferença e
    # ficam no painel do lote, com a O.S. de cada reserva e a parcela em quarentena ("Registrar laudo ›"), onde se age sobre eles
    g_lot=grid([dict(k='prod',l='Item',w=170),dict(k='lote',l='Lote'),dict(k='fis',l='Físico',t='num',a='r'),dict(k='disp',l='Disponível',t='num',a='r'),
                dict(k='vali',l='Validade',t='date')],
        [],edit=dict(m='origin',title='Lote',fields=[]),gid='g_lot',total=False,tools=chips('est_locs','Filtrar por local'))
    # colunas essenciais (10/10): quando, o quê, documento, item, quanto e quem fez (CTL-3); o lote vai para o painel do movimento, e a trilha de um
    # lote inteiro é o extrato do painel do lote (Confira saldos › Lotes)
    g_mov=grid([dict(k='hora',l='Data e hora',w=90),dict(k='tipo',l='Movimento',w=170),dict(k='doc',l='Documento'),dict(k='item',l='Item',w=170),
                dict(k='qtd',l='Quantidade',t='num',a='r'),dict(k='quem',l='Quem',w=150)],
        [],edit=dict(m='origin',title='Movimento',fields=[]),gid='g_mov',total=False,qf=dict(k='tipo',sep=' · ',todas='Todos'))
    # ---------- JS: cenário compartilhado + regras do Estoque (est.js) + tela ----------
    EXTRAJS[0]=cenario.js_prefixo()+'const E2 = '+json.dumps(_dados_js(),ensure_ascii=False).replace('</','<\\/')+';\n'+JS
    # ---------- corpo ----------
    # celular (≤ 700 px): o selo da Situação quebra linha para Requisição e Situação ficarem à vista sem rolar a grade (SUP §2.4, AC-SUP-12)
    # (10/10: vale para as 5 grades, para a Situação e o Movimento ficarem à vista com as colunas essenciais)
    E.EXTRA.append('<style>@media (max-width:700px){[role=table] [role=row] [role=cell]:nth-child(2) span{white-space:normal!important}}</style>')
    # o rótulo da primária confirma o quê, quanto, lote e para quem (SUP §2.3) e pode ser longo: no painel ele quebra linha em vez de vazar pela
    # esquerda da gaveta (o toque caía no fundo que fecha o painel: roteiro do BEN R6, 09/10; est_fila casos 5 e 12). Só nesta página; o estilo
    # comum do botão (BTN_ST) não muda
    E.EXTRA.append('<style>aside[role=dialog] button{white-space:normal!important;overflow-wrap:anywhere}</style>')
    s1=bloco('Requisições das O.S.','Toque na requisição: o painel mostra a conta, o que separar e a ação (entregar, receber a sobra ou conciliar o consumo).',f'<div class="est-req">{g_req}</div>')
    nf_btn=f'<button type="button" onClick="{H("est_nf_new")}" style="{_MINI}">Registrar NF recebida</button>'
    s2=bloco('Notas e parcelas em quarentena','Confira a nota contra o pedido e o material; a parcela em quarentena só sai com o laudo, documento por documento.',g_rec,nf_btn)
    cl=(f'<div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;"><label style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; color: {MUTED};">Local'
        f'<select aria-label="Local a contar" value="{H("cl_v")}" onChange="{H("cl_set")}" style="font-family: inherit; font-size: 12px; padding: 4px 8px; border-radius: 8px; border: 1px solid {LINE};">'
        f'<sc-for list="{H("cl_opts")}" as="o" hint-placeholder-count="3"><option value="{H("o.v")}">{H("o.t")}</option></sc-for></select></label>'
        f'<button type="button" onClick="{H("cl_go")}" style="{_MINI}">Contar local</button></div>')
    s3=bloco('Contagens','Conte sem ver o saldo; a diferença vai à gestora com a causa. Se a gestora também contou, a decisão dela vale e fica revisão independente pendente.',g_cnt,cl)
    # Produção (ponto de entrada; só leitura): resumo do físico por produto, lido de c.producao; a grade, a qualidade e as ações ficam na Colheita
    vazio_prod=(f'<div style="display: flex; flex-direction: column; gap: 6px; padding: 4px;">'
                f'<sc-if value="{H("prod_nada")}" hint-placeholder-val="{F()}"><div style="font-size: 13px; color: {MUTED};">Nenhum produto colhido em estoque nesta fazenda.</div></sc-if>'
                f'<sc-for list="{H("prod_lin")}" as="pl" hint-placeholder-count="2"><div style="display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; font-size: 13.4px;">'
                f'<b>{H("pl.prod")}</b><span>{H("pl.txt")}</span><span style="color: {MUTED}; font-size: 12.5px;">{H("pl.lotes")}</span></div></sc-for>'
                f'<div style="padding-top: 4px;"><a href="PROD.dc.html" style="{_MINI} text-decoration: none;">Abrir Estoque de produto ›</a></div></div>')
    s4=(chips('est_modos','Modo de Confira saldos')
        + f'<sc-if value="{H("m_lotes")}" hint-placeholder-val="{H("true")}">'+bloco('Saldos por lote','Físico − reservado − bloqueado = disponível; toque no lote para ver reservas, custódias, parcelas e o extrato.',g_lot)+'</sc-if>'
        + f'<sc-if value="{H("m_movs")}" hint-placeholder-val="{F()}">'+bloco('Movimentos','Cada movimento do estoque, da web e do app, com quem agiu.',
              f'<sc-if value="{H("mov_tem")}" hint-placeholder-val="{H("true")}">{g_mov}</sc-if>'
              f'<sc-if value="{H("mov_nada")}" hint-placeholder-val="{F()}"><div style="padding: 14px 4px; font-size: 13px; color: {MUTED};">Nenhum movimento desde o início da demonstração.</div></sc-if>')+'</sc-if>'
        + f'<sc-if value="{H("m_prod")}" hint-placeholder-val="{F()}">'+bloco('Produção','Físico do produto colhido, na unidade da cultura. Qualidade, reserva e disponível ficam em Produção › Estoque de produto.',vazio_prod)+'</sc-if>')
    secoes=''.join(f'<sc-if value="{H("s"+str(i))}" hint-placeholder-val="{H("true") if i==1 else F()}"><div style="display: flex; flex-direction: column; gap: 14px;">{s}{navpe()}</div></sc-if>'
                   for i,s in enumerate([s1,s2,s3,s4],1))
    vazio=(f'<sc-if value="{H("est_vazio")}" hint-placeholder-val="{F()}"><div style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; padding: 28px 24px; display: flex; align-items: center; gap: 8px; font-size: 14px;">'
           f'<span>Nenhum estoque na Boa Vista</span><span style="color: {MUTED};">·</span>'
           f'<button type="button" onClick="{H("est_versr")}" style="border: 0; background: transparent; color: {ACC}; font-family: inherit; font-size: 14px; font-weight: 700; cursor: pointer; padding: 0;">Ver Santa Rita</button></div></sc-if>')
    corpo=vazio+f'<sc-if value="{H("est_tem")}" hint-placeholder-val="{H("true")}">{secoes}</sc-if>'
    HEIGHTS37[fname]=1180
    shell37('EST','Estoque',corpo,fname=fname,subtitle='Atenda requisições, receba e inspecione, conte e confira saldos; cada movimento atualiza O.S., Compras e app.',
            steps=secoes_state(NOMES,label='Seções do estoque'),primary_html=None,ctx=('Fazenda Santa Rita','Todos os depósitos',None),search=False)   # trabalho paralelo: seções em qualquer ordem, não etapas (UX-ACAO-UNICA-20261003)

JS_TELA=r'''
// ===== Estoque · tela (4 seções; a linha identifica, o painel do registro resolve) =====
function GR(id){ return GRIDS.find(g=>g.id===id); }
// Gancho de teste/inspeção (o script da tela roda isolado): os testes est_* leem e mudam o cenário na própria página.
try { window.__cen = { cenGet, cenMudar, cenReset, cenLiberar, cenEntregar, cenDevolver, cenReceber, cenLaudo, cenContar, cenAprovarAjuste, cenConfirmarRecebimento, cenIniciarTurno, cenFecharTurno,
  cenSinal, cenPodeEncerrar, cenConciliar, cenVer, cenDisp, cenQuar, cenResTot, estEntregarReq, estFila, estContadores, estAbertura, estProducao }; } catch (e) {}
function efaz(self){ return self.state.mf_faz||'Santa Rita'; }
function eAlvo(rid){ const a=String(rid||'').split('|'); return {t:a[0],a:a[1]||'',b:a.slice(2).join('|')}; }
function eNovaChave(m){ return 'EST-'+m+'-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,7); }
function eRecebedores(C){ const s=new Set(E2.pessoas||[]); Object.values(C.ordens||{}).forEach(o=>{ if(o.resp) s.add(o.resp); }); return [...s].sort((a,b)=>a.localeCompare(b,'pt-BR')); }

// ---------- painel do registro: modo, alvo e rascunho; a chave do comando nasce aqui (quem inicia) ----------
// g_req: req (Entregar REQ inteira) · ent (Entregar parte) · dev (Registrar devolução) · conc (Aceitar/Aprovar consumo) · rec (Recusar relato) · cons (consulta)
function eReqItem(C,rid,prod){ return eitens(C).find(x=>x.rid===rid&&x.it.prod===prod)||null; }
function eReqLinha(C,rid){ return estFila(C,'Todas').find(y=>y.rid===rid)||null; }
function eConf(C,id){ return (C.confs||[]).find(k=>k.id===id)||null; }
function ePodeConc(C,k,PF){ return estSitCf(C,k)==='Aguardando gestora'?g2papel(PF,'gestor'):!!g2umPapel(PF,['almoxarife','gestor']); }
function eDevOk(x){ return x.it.custodia>1e-9&&!x.sinal&&!x.cf; }
function eModoReq(C,rid,PF){ const a=eAlvo(rid);
  if(a.t==='K') return {modo:'conc',k:a.a};
  if(a.t==='S'){ const k=(C.confs||[]).find(z=>z.os===a.a&&!z.req&&z.estado==='Em conferência'); return k?{modo:'conc',k:k.id}:{modo:'cons',os:a.a}; }
  if(a.t==='I'){ const x=eReqItem(C,a.a,a.b); if(!x) return {modo:'cons',rid:a.a};
    if(x.parte>1e-9) return {modo:'ent',rid:a.a,prod:a.b}; if(x.cf) return {modo:'conc',k:x.cf.id}; if(eDevOk(x)) return {modo:'dev',rid:a.a,prod:a.b}; return {modo:'cons',rid:a.a,prod:a.b}; }
  const L=eReqLinha(C,a.a); if(!L) return {modo:'cons',rid:a.a};
  if(L.inteira) return {modo:'req',rid:a.a};
  const xp=L.itens.find(x=>x.parte>1e-9); if(xp) return {modo:'ent',rid:a.a,prod:xp.it.prod};
  const kc=L.confs.find(k=>ePodeConc(C,k,PF))||L.confs[0]; if(kc) return {modo:'conc',k:kc.id};
  const xd=L.itens.find(x=>eDevOk(x)&&x.sit==='Sobra a receber')||L.itens.find(eDevOk); if(xd) return {modo:'dev',rid:a.a,prod:xd.it.prod};
  return {modo:'cons',rid:a.a}; }
function eDraftReq(C,al){ const d={modo:al.modo};
  if(al.modo==='req'){ const L=eReqLinha(C,al.rid); d.quemr=(L&&L.quem)||''; }
  if(al.modo==='ent'){ const x=eReqItem(C,al.rid,al.prod); d.qtd=''; d.quem=x?x.quem:''; }
  if(al.modo==='dev'){ d.dqtd=''; d.cond=E2.conds[0]; d.obs=''; }   /* devolução digitada, em branco: conferir é de propósito (PRD 42.4; CMD-45) */
  if(al.modo==='rec') d.mot='';
  return d; }
function eLocalPadrao(p){ const nome=p?p.item:''; return {'KCl 60%':'Galpão 2','Semente de soja 58 W':'Câmara fria','Semente de soja 62 X':'Câmara fria'}[nome]||'Galpão 2'; }
function eParcela(C,key,doc){ return estParcelas(C,'Todas').find(p=>p.key===key&&p.doc===doc)||null; }
function eDraftRec(C,al){ const d={modo:al.modo};
  if(al.modo==='nf'){ const b=al.rec||null; const ab=epeds(C).filter(x=>x.a_entregar>0); const ped=b?b.ped:((ab[0]||E2.pedidos[0]||{}).label||''); const p=epedBase(ped);
    Object.assign(d,{ped,nf:b?b.nf:'',qtd_nf:b&&b.qtd_nf!=null?String(b.qtd_nf).replace('.',','):'',conf:'',quar:'0',apto:'',lote:b?b.lote:'',val:'',
      local:b?b.local:eLocalPadrao(p),div:'Sem divergência',obs:''}); }
  if(al.modo==='laudo'){ const p=eParcela(C,al.key,al.doc); d.laudo=''; d.res=(p&&p.venc)?'Reprovado':'Aprovado'; d.dest=''; }
  return d; }
function eModoRec(C,rid,PF){ const a=eAlvo(rid);
  if(a.t==='N'){ const r=erecs(C).find(x=>x.id===a.a); if(!r) return {modo:'cons'}; return r.ok?{modo:'cons',rec:r}:{modo:'nf',rec:r}; }
  if(a.t==='P'){ const ps=String(rid).split('|'); const key=ps[1]+'|'+ps[2], doc=ps.slice(3).join('|'); const p=eParcela(C,key,doc); if(!p) return {modo:'cons',key,doc};   /* a chave do lote já tem "|" (produto|lote) */
    return (!p.laudo&&g2papel(PF,'gestor'))?{modo:'laudo',key,doc}:{modo:'cons',key,doc}; }
  return {modo:'cons'}; }
function eModoCnt(C,rid,PF){ const rec=einvRec(C,rid); if(!rec) return {modo:'cons',inv:rid}; const s=estInvSit(C,rec); const lote=rec.grupo||'';
  if(s==='A contar'||s==='Recontar') return {modo:'contar',inv:rid,lote}; if(s==='Informar causa') return {modo:'causa',inv:rid,lote};
  if(s==='Aguardando gestora') return g2papel(PF,'gestor')?{modo:'aprov',inv:rid}:{modo:'aguarda',inv:rid}; return {modo:'cons',inv:rid}; }
const ERO={cons:1,aguarda:1};
// consumo em conferência: sem o papel da decisão (excedente → gestora; coberto → almoxarife ou gestora) o painel é consulta, com "Recusar relato"
function eRoConc(C,al,PF){ const k=eConf(C,al.k); if(!k||k.estado!=='Em conferência') return true; let p; try{ p=cenConcPrevia(C,k.id); }catch(e){ return true; } if(p.erro) return true; return !ePodeConc(C,k,PF); }
function eFm(C,gid,rid,al,isNew){ const d=gid==='g_req'?eDraftReq(C,al):(gid==='g_rec'?eDraftRec(C,al):{modo:al.modo,cont:'',causa:''});
  const obj=gid==='g_req'?(al.k||al.rid||''):(gid==='g_rec'?(al.key||''):(al.inv?((einvRec(C,al.inv)||{}).key||''):''));
  const ro=!!ERO[al.modo]||(gid==='g_req'&&al.modo==='conc'&&eRoConc(C,al,g2perfil()));
  return {rid,draft:d,orig:Object.assign({},d),errs:{},warn:false,ro,isNew:!!isNew,mode:'form',al,chave:eNovaChave(al.modo),obj,ver:obj?cenVer(C,obj):undefined}; }
// um painel por vez: abrir o registro de uma grade fecha o painel das outras (o endereço pode trocar de seção)
function eSoUm(self,gid){ const all=Object.assign({},self.state.g2||{}); ['g_req','g_rec','g_cnt','g_lot','g_mov'].forEach(g=>{ if(g!==gid&&all[g]&&all[g].fm) all[g]=Object.assign({},all[g],{fm:null}); }); return all; }
// abre o painel de um registro: um único setState (a tela junta a seção e a fazenda do endereço no mesmo patch)
function ePatch(self,gid,rid,al,isNew,extra){ const all=eSoUm(self,gid); all[gid]=Object.assign({},all[gid]||{},{fm:eFm(cenGet(),gid,rid,al,isNew),fl:null,fmc:null});
  return Object.assign({g2:all},extra||{}); }
function eAbrir(self,gid,rid,al,isNew,extra){ self.setState(ePatch(self,gid,rid,al,isNew,extra)); }
const EMODO={g_req:eModoReq,g_rec:eModoRec,g_cnt:eModoCnt};
const _g2open0=g2open;
g2open=function(self,sp,rid,e){ if(!EMODO[sp.id]) return _g2open0(self,sp,rid,e);
  if(e&&e.target&&e.target.closest&&e.target.closest('a,button,input,select,textarea,label,[data-noedit]')) return;
  const C=cenGet(); eAbrir(self,sp.id,rid,EMODO[sp.id](C,rid,g2perfil())); };
// trocar de modo no mesmo painel (ação secundária): só navega, nunca executa; a chave nova nasce com o novo modo
function eModo(self,gid,al){ const fm=g2st(self,gid).fm; if(!fm) return; eAbrir(self,gid,fm.rid,al); }

// ---------- validação e gravação (erro junto ao campo; o preenchido é mantido) ----------
function enum_(d,k){ return eblank(d[k])?NaN:g2num(d[k]); }
const ESTV={};
ESTV.g_req=(self,fm)=>{ const e={}, d=fm.draft, al=fm.al||{}, C=cenGet();
  if(al.modo==='req'){ if(eblank(d.quemr)) e.quemr='Informe quem recebe.'; }
  if(al.modo==='ent'){ const x=eReqItem(C,al.rid,al.prod); const n=enum_(d,'qtd'); if(eblank(d.quem)) e.quem='Informe quem recebe.';
    if(isNaN(n)||!(n>0)) e.qtd='Informe a quantidade a entregar.';
    else if(x&&n>x.pend+1e-9) e.qtd='Acima do saldo a entregar: '+eq(x.pend,x.un)+' ('+econta(x)+').';
    else if(x&&n>x.ent+1e-9) e.qtd='Acima do reservado para a '+x.rid+': '+eq(x.ent,x.un)+'. Entregue só o que a liberação reservou.';
    else if(x&&n>x.livreReq+1e-9) e.qtd='Lote insuficiente: o lote '+x.it.lote+' tem '+eq(x.livreReq,x.un)+' para a '+x.rid+'.'; }
  if(al.modo==='dev'){ const x=eReqItem(C,al.rid,al.prod); const n=enum_(d,'dqtd');
    if(x&&x.sinal){ e.dqtd='Apontamento de '+x.os+' no aparelho, aguardando sinal: receba a sobra depois do envio.'; return e; }
    if(x&&x.cf){ e.dqtd='Consumo em conferência ('+x.cf.id+'): aceite ou recuse o relato antes de receber devolução.'; return e; }
    if(isNaN(n)||!(n>0)) e.dqtd='Informe a quantidade conferida (o que voltou de fato).';
    else if(x&&n>x.it.custodia+1e-9) e.dqtd='Acima da custódia: só '+eq(x.it.custodia,x.un)+' estão com '+x.quem+'.';
    if(d.cond!==E2.conds[0]&&!String(d.obs||'').trim()) e.obs='Descreva a condição (ex.: embalagem aberta).'; }
  if(al.modo==='rec'&&!String(d.mot||'').trim()) e.mot='Informe o motivo da recusa.';
  return e; };
ESTV.g_rec=(self,fm)=>{ const C=cenGet(); const e={}, d=fm.draft, al=fm.al||{};
  if(al.modo==='laudo'){ if(!String(d.laudo||'').trim()) e.laudo='Informe o nº do laudo. Sem laudo a parcela continua bloqueada.'; return e; }
  if(al.modo!=='nf') return e;
  const n=(k)=>enum_(d,k); const conf=n('conf'), quar=eblank(d.quar)?0:n('quar'), qnf=n('qtd_nf'); const p=epeds(C).find(x=>x.id===elotId(d.ped)); const un=p?p.un:'';
  if(!String(d.nf||'').trim()) e.nf='Informe a nota fiscal.';
  if(isNaN(qnf)||!(qnf>0)) e.qtd_nf='Informe a quantidade na nota.';
  if(isNaN(conf)) e.conf='Informe a quantidade conferida.';
  if(!String(d.lote||'').trim()) e.lote='Informe o lote.';
  if(!isNaN(conf)&&!isNaN(quar)&&quar>conf+1e-6) e.quar='A quarentena não passa da conferida ('+eq(conf,un)+').';
  if(!isNaN(conf)&&!isNaN(qnf)&&Math.abs(conf-qnf)>1e-6&&d.div==='Sem divergência') e.div='A conferida difere da nota em '+eq(Math.abs(conf-qnf),un)+': indique a divergência.';
  if(p&&!isNaN(conf)&&conf>p.a_entregar+1e-6&&d.div!=='Sobra') e.conf='Acima do saldo do pedido '+p.id+' ('+eq(p.a_entregar,un)+' a entregar): registre como sobra.';
  if(((!isNaN(quar)&&quar>0)||(d.div&&d.div!=='Sem divergência'))&&!String(d.obs||'').trim()) e.obs='Informe o motivo da quarentena ou da divergência.';
  const nfn=String(d.nf||'').replace(/\D/g,''); if(nfn){ const dup=erecs(C).find(r=>r.ok&&r.id!==(al.rec?al.rec.id:'')&&String(r.nf||'').replace(/\D/g,'')===nfn); if(dup) e.nf=dup.nf+' já foi lançada: documento duplicado não cria segunda entrada.'; }
  const lt=String(d.lote||'').trim(); const outro=Object.values(C.lotes).find(l=>l.lote===lt&&p&&l.prod!==p.item); if(outro) e.lote='O lote '+lt+' é de '+outro.prod+'. Use outro código de lote.';
  if(!efert(d.ped)){ const vv=String(d.val||'').trim(); const apto=(isNaN(conf)?0:conf)-(isNaN(quar)?0:quar);
    if(!vv) e.val='Informe a validade do lote (mês/ano, ex.: 06/2027).';
    else if(!/^(0[1-9]|1[0-2])\/\d{4}$/.test(vv)) e.val='Use mês/ano com 4 dígitos no ano (ex.: 06/2027).';
    else if(p&&cenValidadeConflito(C.lotes[p.item+'|'+lt],vv)) e.val=cenValidadeConflito(C.lotes[p.item+'|'+lt],vv);
    else if(eval_(vv)<ehojeYM()){ if(apto>1e-9) e.quar='Lote vencido em '+vv+': registre toda a quantidade em quarentena (apta = 0).';
      if(!String(d.obs||'').trim()) e.obs='Informe o motivo (lote vencido em '+vv+').'; } }
  return e; };
ESTV.g_cnt=(self,fm)=>{ const e={}, d=fm.draft, al=fm.al||{};
  if(al.modo==='contar'){ const n=enum_(d,'cont'); if(isNaN(n)||n<0) e.cont='Informe a quantidade contada.'; }
  if(al.modo==='causa'&&!String(d.causa||'').trim()) e.causa='Informe a causa da diferença.';
  return e; };
function eComprovante(self,gid,fm,r){ const all=Object.assign({},self.state.g2||{}); all[gid]=Object.assign({},all[gid]||{},{fm:Object.assign({},fm,{ro:true,rcb:r.msg||'',errs:{},warn:false})});
  self.setState({g2:all,cenrev:Date.now(),g2toast:(r.repetido?'Já registrado: ':'')+(r.msg||'Registrado.')}); }
function eErro(self,gid,fm,campo,msg){ g2set(self,gid,{fm:Object.assign({},fm,{errs:{[campo]:msg},warn:false})}); }
const ESAVE={};
ESAVE.g_req=(self,fm)=>{ const d=fm.draft, al=fm.al||{}, PF=g2perfil(); const cmd=(nome,payload)=>({chave:fm.chave,nome,obj:fm.obj,ver:fm.ver,payload});
  if(al.modo==='req'){ const q=d.quemr; const rot=estRotuloReq(cenGet(),al.rid,q);
    return [cenMudar(null,c=>estEntregarReq(c,al.rid,q,PF),cmd('entregar-req',rot.itens)),'quemr']; }
  if(al.modo==='ent'){ const n=g2num(d.qtd); return [cenMudar(null,c=>estEntregar(c,al.rid,al.prod,n,d.quem,PF),cmd('entregar',[al.prod,n,d.quem])),'qtd']; }
  if(al.modo==='dev'){ const n=g2num(d.dqtd), apto=d.cond===E2.conds[0], obs=String(d.obs||'').trim();
    return [cenMudar(null,c=>estDevolver(c,al.rid,al.prod,n,apto,obs,PF),cmd('devolver',[al.prod,n,apto,obs])),'dqtd']; }
  if(al.modo==='conc') return [cenMudar(null,c=>cenConciliar(c,al.k,true,undefined,PF),cmd('conciliar',[al.k,true])),'_'];
  if(al.modo==='rec'){ const m=String(d.mot||'').trim(); return [cenMudar(null,c=>cenConciliar(c,al.k,false,m,PF),cmd('conciliar',[al.k,false,m])),'mot']; }
  return [{erro:'Consulta: nada a registrar.'},'_']; };
ESAVE.g_rec=(self,fm)=>{ const d=fm.draft, al=fm.al||{}, PF=g2perfil(); const cmd=(nome,payload)=>({chave:fm.chave,nome,obj:fm.obj,ver:fm.ver,payload});
  if(al.modo==='laudo'){ const num=String(d.laudo||'').trim(), res=d.res, dest=String(d.dest||'').trim();
    return [cenMudar(null,c=>cenLaudo(c,al.key,al.doc,num,res,PF,dest),cmd('laudo',[al.key,al.doc,num,res,dest])),'laudo']; }
  const p=epedBase(d.ped)||{}; const n=k=>eblank(d[k])?0:g2num(d[k]); const nfv=String(d.nf||'').trim();
  const id=(al.rec&&al.rec.id)||('r'+(nfv.replace(/\D/g,'')||String(Date.now()).slice(-6))); const base=E2.recs.find(b=>b.id===id)||{};
  const conf=n('conf'), quar=n('quar');
  const rec={id,nf:nfv,data:base.data||'',ped:d.ped,item:p.item,un:p.un,qtd_nf:n('qtd_nf'),conf,apto:Math.max(0,conf-quar),quar,lote:String(d.lote||'').trim(),
    val:efert(d.ped)?'—':String(d.val||'').trim(),local:d.local,div:d.div||'Sem divergência',obs:String(d.obs||'').trim()};
  return [cenMudar(null,c=>estReceber(c,rec,PF),cmd('receber',[rec.nf,rec.conf,rec.quar,rec.lote])),'lote']; };
ESAVE.g_cnt=(self,fm)=>{ const d=fm.draft, al=fm.al||{}, PF=g2perfil(); const C=cenGet(); const rec=einvRec(C,al.inv); const cmd=(nome,payload)=>({chave:fm.chave,nome,obj:fm.obj,ver:fm.ver,payload});
  if(al.modo==='contar'){ const n=g2num(d.cont); const contador=g2ator(PF,'almoxarife'); return [cenMudar(null,c=>estContar(c,al.inv,rec.key,n,contador,'',PF),cmd('contar',[al.inv,n,contador])),'cont']; }
  if(al.modo==='causa'){ const causa=String(d.causa||'').trim(); return [cenMudar(null,c=>estCausa(c,al.inv,causa),cmd('causa',[al.inv,causa])),'causa']; }
  if(al.modo==='aprov') return [cenMudar(null,c=>estAprovar(c,al.inv,PF),cmd('aprovar',[al.inv])),'_'];
  return [{erro:'Consulta: nada a registrar.'},'_']; };
function efields(sp,fm){ const e={}; (sp.edit.fields||[]).forEach(f=>{ if(f.ro||(f.cond&&String(fm.draft[f.cond.k])!==String(f.cond.eq))) return; const val=String(fm.draft[f.k]===undefined?'':fm.draft[f.k]).trim();
  if(f.t==='num'&&val){ const n=g2num(val); if(isNaN(n)){ e[f.k]='Use um número (ex.: 12,5).'; return; } if(f.min!==undefined&&n<f.min) e[f.k]=(f.min>0?'Informe um valor maior que zero.':'Não use valor negativo.'); } }); return e; }
const _g2save0=g2save;
g2save=function(self,sp){ const fm=g2st(self,sp.id).fm; if(!fm||fm.ro||!ESAVE[sp.id]) return _g2save0(self,sp);
  const e=Object.assign({},ESTV[sp.id]?(ESTV[sp.id](self,fm)||{}):{},efields(sp,fm));
  if(Object.keys(e).length){ g2set(self,sp.id,{fm:Object.assign({},fm,{errs:e,warn:false})}); return; }
  const out=ESAVE[sp.id](self,fm)||[{},'_']; const r=out[0]||{};
  if(r.erro){ if(out[1]==='_') self.setState({g2toast:r.erro}); else eErro(self,sp.id,fm,out[1],r.erro); return; }
  // contagem com diferença: o mesmo painel pede a causa (sem fechar); demais: comprovante no mesmo registro, a primária some
  if(sp.id==='g_cnt'&&(fm.al||{}).modo==='contar'){ const C=cenGet(); const rec=einvRec(C,fm.al.inv); if(rec&&estInvSit(C,rec)==='Informar causa'){
      const all=Object.assign({},self.state.g2||{}); all[sp.id]=Object.assign({},all[sp.id]||{},{fm:eFm(C,sp.id,fm.rid,{modo:'causa',inv:fm.al.inv,lote:fm.al.lote})});
      self.setState({g2:all,cenrev:Date.now(),g2toast:r.msg||''}); return; } }
  eComprovante(self,sp.id,fm,r); };
// as grades desta tela são sempre recalculadas do cenário (nada fica preso no estado local da grade)
const ECEN={g_req:1,g_rec:1,g_lot:1,g_cnt:1,g_mov:1};
const _g2rows0=g2rows;
g2rows=function(self,sp){ return ECEN[sp.id]?sp.rows:_g2rows0(self,sp); };

// ---------- linhas (uma variável por coluna; unidade junto do valor; sem comando na linha) ----------
const SCOR={'O.S. impedida':'red','Aguarda liberação':'gray','Lote insuficiente':'red','Reserva parcial':'yellow','A entregar':'blue','Aguarda confirmação no app':'yellow',
  'Consumo em conferência':'yellow','Aguardando gestora':'yellow','Sobra a receber':'yellow','Em uso':'gray','Concluída':'green','Nota prevista':'blue','A conferir':'blue','Aguarda laudo':'yellow',
  'Reprovada':'red','Vencida':'red','Conferida':'green','A contar':'blue','Recontar':'blue','Informar causa':'yellow','Ajustada':'green','Em estoque':'green'};
function eChip(t){ const b=Object.keys(SCOR).find(k=>String(t).indexOf(k)===0); return {k:'chip',t,c:SCOR[b]||'gray'}; }
function eLnkOS(os){ return {k:'link',t:os,h:'OS.dc.html#'+os}; }
function eSoma(xs,f){ const us=[...new Set(xs.map(x=>x.un))]; if(us.length!==1) return null; return {q:xs.reduce((a,x)=>a+f(x),0),un:us[0]}; }
function eRowsReq(C,faz){ const F=estFila(C,faz); const x0={};
  const rows=F.map(L=>{ const its=L.itens; const id=L.semReq?'S|'+L.os:'R|'+L.rid; const ent=eSoma(its,x=>x.ent), cu=eSoma(its,x=>x.it.custodia);
    const lot=[...new Set(its.map(x=>x.it.lote))]; const r={id,v:{req:L.semReq?L.os+' · sem requisição':L.rid,sit:L.sit,ent:ent?ent.q:'',cust:cu?cu.q:'',com:L.quem,os:L.os,lote:lot.join(', ')},s:{},p:{}};
    r.p.req=L.semReq?[{k:'b',t:L.os},{k:'mut',t:'sem requisição'}]:[{k:'b',t:L.rid}].concat(its.length===1?[{k:'mut',t:its[0].it.prod}]:[{k:'mut',t:its.length+' itens'}]);
    r.s.req=L.semReq?L.os+' sem requisição':L.rid+' '+its.map(x=>x.it.prod+' '+x.it.lote).join(' ');   /* o lote saiu da grade (10/10) e segue na busca */
    r.p.sit=[eChip(L.sit)]; r.s.sit=L.sit;
    r.p.ent=ent?[{k:ent.q>1e-9?'b':'mut',t:ent.q>1e-9?eq(ent.q,ent.un):'—'}]:[{k:'mut',t:'por item'}];   /* unidades diferentes não se somam: a quantidade fica nas linhas dos itens */ r.s.ent=ent&&ent.q>1e-9?eq(ent.q,ent.un):'';
    r.p.cust=cu?[{k:cu.q>1e-9?'txt':'mut',t:cu.q>1e-9?eq(cu.q,cu.un):'—'}]:[{k:'mut',t:'—'}]; r.s.cust=cu&&cu.q>1e-9?eq(cu.q,cu.un):'';
    r.p.com=L.quem?[{k:'txt',t:L.quem}]:[{k:'mut',t:'—'}]; r.s.com=L.quem; r.p.os=[eLnkOS(L.os)]; r.s.os=L.os;
    r.p.lote=lot.length?[{k:'txt',t:lot.join(', ')}]:[{k:'mut',t:'—'}]; r.s.lote=lot.join(', ');
    /* consumo em conferência da própria requisição também vira linha filha (o relato e quem decide à vista, sem abrir o painel) */
    const kids=(its.length>1?its.map(x=>eRowItem(C,x)):[]).concat(L.confs.filter(k=>L.fora.indexOf(k)<0).map(k=>eRowFora(C,k,false))).concat(L.fora.map(k=>eRowFora(C,k,true)));
    if(kids.length){ r.kids=kids; if(L.acao) x0[id]=true; }
    return r; });
  return {rows,x0}; }
function eRowItem(C,x){ const it=x.it; const r={id:'I|'+x.rid+'|'+it.prod,v:{req:it.prod,sit:x.sit,ent:x.ent,cust:it.custodia,com:x.quem,os:x.os,lote:it.lote},s:{},p:{}};
  r.p.req=[{k:'txt',t:it.prod}]; r.s.req=it.prod+' '+it.lote; r.p.sit=[eChip(x.sit)]; r.s.sit=x.sit;
  r.p.ent=x.ent>1e-9?[{k:'b',t:eq(x.ent,x.un)}]:[{k:'mut',t:'—'}]; r.s.ent=x.ent>1e-9?eq(x.ent,x.un):'';
  r.p.cust=it.custodia>1e-9?[{k:'txt',t:eq(it.custodia,x.un)}]:[{k:'mut',t:'—'}]; r.s.cust=it.custodia>1e-9?eq(it.custodia,x.un):'';
  r.p.com=[{k:'txt',t:x.quem||'—'}]; r.s.com=x.quem; r.p.os=[eLnkOS(x.os)]; r.s.os=x.os; r.p.lote=[{k:'txt',t:it.lote}]; r.s.lote=it.lote; return r; }
function eRowFora(C,k,fora){ if(fora===undefined) fora=true; const s=estSitCf(C,k); const rot=fora?'fora da requisição':'consumo relatado';
  const r={id:'K|'+k.id,v:{req:k.prod+' · '+rot,sit:s,ent:'',cust:'',com:k.quem,os:k.os,lote:fora?'':k.lote},s:{},p:{}};
  r.p.req=[{k:'txt',t:k.prod},{k:'mut',t:rot}]; r.s.req=k.prod+' '+rot+(fora?'':' '+k.lote); r.p.sit=[eChip(s),{k:'mut',t:k.id}]; r.s.sit=s;
  r.p.ent=[{k:'mut',t:'—'}]; r.p.cust=[{k:'mut',t:'—'}]; r.s.ent=''; r.s.cust=''; r.p.com=[{k:'txt',t:k.quem||'—'}]; r.s.com=k.quem||''; r.p.os=[eLnkOS(k.os)]; r.s.os=k.os; r.p.lote=fora?[{k:'mut',t:'—'}]:[{k:'txt',t:k.lote}]; r.s.lote=fora?'':k.lote; return r; }
function eRowsRec(C,faz){ const PD=epeds(C); const out=[];
  estNotas(C,faz).forEach(x=>{ const p=PD.find(y=>y.id===elotId(x.ped)); const prev=/previsto/.test(String(x.data||''));
    if(x.ok&&!x.hoje) return;   /* nota conferida antes de hoje: história no Movimentos e em Acompanhe pedidos */
    const sit=x.ok?'Conferida':(prev?'Nota prevista':'A conferir'); const dt=eiso(x.data);   /* nota que já chegou (NF 7731 das caixas, BEN-D23) espera a conferência */
    out.push({id:'N|'+x.id,v:{doc:x.nf+' ('+(p?p.id:'')+')',sit,item:x.item,qtd_nf:x.qtd_nf,quar:x.ok?(Number(x.quar)||0):'',prev:prev?dt:'',forn:p?p.forn:''},
      s:{doc:x.nf+' '+x.item+' '+(p?p.id+' '+p.forn:''),sit,item:x.item,qtd_nf:eq(x.qtd_nf,x.un),quar:x.ok&&x.quar?eq(x.quar,x.un):'',prev:prev&&dt?edmy(dt):'',forn:p?p.forn:''},
      p:{doc:[{k:'b',t:x.nf},{k:'mut',t:'› '+x.item}],sit:[eChip(sit)],item:[{k:'txt',t:x.item}],qtd_nf:[{k:'txt',t:eq(x.qtd_nf,x.un)}],quar:x.ok&&x.quar?[{k:'txt',t:eq(x.quar,x.un)}]:[{k:'mut',t:'—'}],
         prev:prev&&dt?[{k:'txt',t:edmy(dt)}]:[{k:'mut',t:'—'}],forn:[{k:'txt',t:p?p.forn:'—'}]}}); });
  estParcelas(C,faz).forEach(pc=>{ const sit=pc.laudo?'Reprovada':(pc.venc?'Vencida · aguarda laudo':'Aguarda laudo'); const b=erecs(C).find(x=>x.nf===pc.doc); const p=b?PD.find(y=>y.id===elotId(b.ped)):null;
    const req=/^REQ-/.test(pc.doc); const docT=pc.doc+(pc.ped?' ('+pc.ped+')':(p?' ('+p.id+')':''));
    out.push({id:'P|'+pc.key+'|'+pc.doc,v:{doc:docT,sit,item:pc.prod,qtd_nf:b?b.qtd_nf:'',quar:pc.qtd,prev:'',forn:p?p.forn:''},
      s:{doc:docT+' '+pc.prod+' '+pc.lote+(p?' '+p.forn:''),sit,item:pc.prod,qtd_nf:b?eq(b.qtd_nf,b.un):'',quar:eq(pc.qtd,pc.un),prev:'',forn:p?p.forn:(req?'devolução':'')},
      p:{doc:[{k:'b',t:pc.doc},{k:'mut',t:'› '+pc.prod+' · '+pc.lote+(req?' · devolução':'')}],sit:[eChip(sit)],item:[{k:'txt',t:pc.prod}],qtd_nf:b?[{k:'txt',t:eq(b.qtd_nf,b.un)}]:[{k:'mut',t:'—'}],
         quar:[{k:'b',t:eq(pc.qtd,pc.un)}],prev:[{k:'mut',t:'—'}],forn:[{k:p?'txt':'mut',t:p?p.forn:(req?'devolução da O.S.':'—')}]}}); });
  return out; }
function eRowsCnt(C,faz){ return estContagens(C,faz).map(rec=>{ const l=C.lotes[rec.key]; const un=l?l.un:''; const s=estInvSit(C,rec); const has=econtou(rec); const d=has?rec.cont-rec.sis:null;
  const r={id:rec.id,v:{inv:rec.id,sit:s,prod:l?l.prod:'',lote:l?l.lote:'',local:l?l.local:'',cont:has?rec.cont:'',dif:d===null?'':d},s:{inv:rec.id,sit:s,prod:l?l.prod:'',lote:l?l.lote:'',local:l?l.local:'',cont:has?eq(rec.cont,un):'',dif:d===null?'':(Math.abs(d)<1e-9?'0':esig(d,un))},p:{}};
  r.p.inv=[{k:'b',t:rec.id}]; r.p.sit=[eChip(s)].concat((s==='A contar'||s==='Recontar')&&rec.contador?[{k:'mut',t:'atribuída a '+String(rec.contador).split(' ')[0]}]:[]);
  r.p.prod=[{k:'txt',t:l?l.prod:''}]; r.p.lote=[{k:'txt',t:l?l.lote:''}]; r.p.local=[{k:'txt',t:l?l.local:''}];
  r.p.cont=has?[{k:'txt',t:eq(rec.cont,un)}]:[{k:'mut',t:'a contar'}]; r.p.dif=d===null?[{k:'mut',t:'—'}]:[{k:'chip',t:(Math.abs(d)<1e-9?'0':esig(d,un)),c:(Math.abs(d)<1e-9?'green':'red')}];
  r.o=has?(rec.hist||[]).map(h=>({t:'Contagem anterior: '+eq(h.cont,un)+' por '+h.contador+' · diferença '+esig(h.dif,un)+(h.causa?' · causa: '+h.causa:'')})):[]; return r; }); }
// contagem cega também na consulta: quem tem contagem aberta atribuída do lote não vê físico nem disponível (SUP §3; AC-SUP-08)
function eCego(C,key,PF){ return einvs(C).some(r=>r.key===key&&!econtou(r)&&g2mesma(PF.k,r.contador)); }
function eRowsLot(C,faz,loc,PF){ const INV=einvs(C); return elotes(C).filter(l=>estNaFaz(estFazLocal(l.local),faz)&&(!loc||l.local===loc)).sort((a,b)=>a.prod.localeCompare(b.prod,'pt-BR')||a.lote.localeCompare(b.lote)).map(l=>{
  const un=l.un; const venc=evenc(l); const cego=eCego(C,l.key,PF); const vl=l.validade&&l.validade!=='—'?l.validade:'';
  const r={id:'L|'+l.key,v:{prod:l.prod,lote:l.lote,fis:cego?'':l.fisico,res:l.reservado,blq:l.quarentena,disp:cego?'':cenDisp(l),vali:eym(vl)},s:{prod:l.prod,lote:l.lote,vali:vl},p:{}};
  /* estado à vista na linha: o Bloqueado saiu da grade (10/10) e a quarentena vira selo, como o Vencido (estado sempre visível, AGENTS §4); a quantidade
     fica na conta do painel e o selo não diz número (contagem cega) */
  r.p.prod=[{k:'txt',t:l.prod}].concat(venc?[{k:'chip',t:'Vencido',c:'red'}]:[]).concat(!venc&&l.quarentena>1e-9?[{k:'chip',t:'Em quarentena',c:'yellow'}]:[]); r.p.lote=[{k:'txt',t:l.lote}];
  r.p.fis=cego?[{k:'mut',t:'— (contagem aberta)'}]:[{k:'txt',t:eq(l.fisico,un)}]; r.s.fis=cego?'':eq(l.fisico,un);
  r.p.res=l.reservado>1e-9?[{k:'txt',t:eq(l.reservado,un)}]:[{k:'mut',t:'—'}]; r.s.res=l.reservado>1e-9?eq(l.reservado,un):'';
  r.p.blq=l.quarentena>1e-9?[{k:'chip',t:eq(l.quarentena,un),c:'yellow'}]:[{k:'mut',t:'—'}]; r.s.blq=l.quarentena>1e-9?eq(l.quarentena,un):'';
  r.p.disp=cego?[{k:'mut',t:'— (contagem aberta)'}]:[{k:'b',t:eq(cenDisp(l),un)}]; r.s.disp=cego?'':eq(cenDisp(l),un);
  r.p.vali=[{k:vl?'txt':'mut',t:vl||'—'}];
  // painel (consulta): a conta do disponível, local, reservas e custódias por O.S., parcelas com "Registrar laudo ›" e o extrato
  const its=eitens(C).filter(x=>x.it.prod===l.prod&&x.it.lote===l.lote);
  r.o=(cego?[{t:'Contagem aberta atribuída a você neste lote: físico e disponível ficam ocultos até contar.'}]:[{t:'Disponível = físico − reservado − bloqueado = '+eq(l.fisico,un)+' − '+eq(l.reservado,un)+' − '+eq(l.quarentena,un)+' = '+eq(cenDisp(l),un)}])
    .concat([{t:'Local: '+l.local+(vl?' · validade '+vl:'')+(venc?' · vencido, não volta ao disponível':'')}])
    .concat(its.filter(x=>x.resP>1e-9).map(x=>({t:'Reservado para a '+x.rid+' ('+x.os+'): '+eq(x.resP,un),h:'#req='+x.rid})))
    .concat(its.filter(x=>x.it.custodia>1e-9).map(x=>({t:'Em custódia (fora do depósito): '+x.rid+' · '+x.os+' · '+eq(x.it.custodia,un)+' com '+x.quem,h:'#req='+x.rid})))
    .concat((C.confs||[]).filter(k=>k.estado==='Em conferência'&&k.prod===l.prod&&k.lote===l.lote&&k.relatado-cenConfCust(C,k)>1e-9).map(k=>({t:'Exposição: '+eq(k.relatado-cenConfCust(C,k),un)+' em conferência ('+k.id+') podem sair deste lote se a gestora aceitar',h:'#req='+(k.req||'')})))
    .concat(cenQuar(cenClone(l)).map(p=>({t:(p.laudo?'Parcela reprovada ('+p.laudo.num+'): ':'Registrar laudo da parcela ')+p.doc+' · '+eq(p.qtd,un)+(p.motivo?' · '+p.motivo:''),h:'#nf='+encodeURIComponent(p.doc)})))
    .concat((C.movs||[]).filter(m=>m.prod===l.prod&&m.lote===l.lote).map(m=>({t:m.at+' · '+emovTxt(m)})))
    .concat(INV.filter(x=>x.key===l.key&&econtou(x)&&Math.abs(x.cont-x.sis)>1e-9&&!(eajuste(C,x)&&eajuste(C,x).estado==='Aprovado')).map(x=>({t:'Ajuste '+x.id+' '+esig(x.cont-x.sis,un)+' aguardando a gestora · não aplicado ao saldo'})));
  return r; }); }
function eRowsMov(C){ const SEM=esemSinal(C), APPI=eappItens(C), AJU={}; (C.movs||[]).forEach(m=>{ if(m.aj) AJU[m.aj]=true; }); const dia=String(E2.hoje).slice(0,5);
  return (C.movs||[]).slice().reverse().map(m=>{ const app=m.origem==='app'; const sem=!!SEM[m.id];
    const li=APPI[m.id]||null; const tp=emovTipo(m); const dc=emovDoc(C,m,AJU); const dd=m.req||(dc&&dc.doc)||'';
    const r={id:m.id,v:{hora:dia+' '+(m.at||''),tipo:tp,doc:dd,item:m.prod||'',lote:m.lote||'',qtd:'',quem:m.quem||''},s:{hora:dia+' '+(m.at||''),tipo:tp+(sem?' · Aguardando sinal':''),doc:dd,lote:m.lote||'',quem:m.quem||''},p:{}};
    r.p.hora=[{k:'txt',t:dia+' '+(m.at||'')}]; r.p.tipo=[{k:'txt',t:tp}].concat(sem?[{k:'chip',t:'Aguardando sinal',c:'yellow'}]:[]);
    r.p.doc=dd?[{k:'b',t:dd}]:[{k:'mut',t:'—'}]; r.p.lote=m.lote?[{k:'txt',t:m.lote}]:[{k:'mut',t:'—'}]; r.p.quem=[{k:'txt',t:m.quem||'—'}];
    const lin=(a)=>a.reduce((o,p,i)=>o.concat(i?[{k:'br'},p]:[p]),[]);
    r.p.item=m.prod?[{k:'txt',t:m.prod}]:(li&&li.length?lin(li.map(x=>({k:'txt',t:x.prod}))):(m.det?[{k:'mut',t:m.det}]:[{k:'mut',t:'—'}]));
    r.s.item=m.prod||(li?li.map(x=>x.prod).join(', '):'')||m.det||'';
    if(li&&li.length){ r.p.qtd=lin(li.map(x=>({k:'txt',t:eq(x.qtd,x.un)}))); r.s.qtd=li.map(x=>eq(x.qtd,x.un)).join(', '); const us=[...new Set(li.map(x=>x.un))]; r.v.qtd=us.length===1?li.reduce((a,x)=>a+(Number(x.qtd)||0),0):NaN; }
    else { const q=emovQtd(m); const mq=String(q||'').match(/^([+−-]?[\d.]+(?:,\d+)?)\s*(\S*)/); if(mq){ r.v.qtd=Number(mq[1].replace(/\./g,'').replace(',','.').replace('−','-').replace('+','')); r.p.qtd=[{k:'txt',t:mq[1]+(mq[2]?' '+mq[2]:'')}]; r.s.qtd=r.p.qtd[0].t; }
      else { r.p.qtd=[{k:'mut',t:'—'}]; r.s.qtd=''; } }
    const cond=m.tipo==='devolucao'?(m.apto?'apta':'bloqueada para inspeção'):(m.tipo==='recebimento-nf'?(m.apto?'apto':'em quarentena'):(m.tipo==='reserva'?'reservados':''));
    r.o=[{t:'Registro '+m.id+' · '+(app?'app':'web')+(cond?' · '+cond:'')}].concat(m.os?[{t:(m.req?'Requisição '+m.req+' da ':'Ordem ')+m.os,h:'OS.dc.html#'+m.os}]:[])
      .concat(sem?[{t:'Registrado no aparelho às '+m.at+'; chega ao servidor quando o app tiver sinal.'}]:[]).concat(m.obs?[{t:'Observação: '+m.obs}]:[]).concat(m.rev?[{t:m.rev}]:[]);
    return r; }); }
function PREVALS(self,v){
  cenOuvir(self); const C=cenGet(); self._cen=C; const PF=g2perfil(); const faz=efaz(self);
  const vazio=(faz==='Boa Vista'); v.est_vazio=vazio; v.est_tem=!vazio; v.est_versr=()=>self.setState({mf_faz:'Santa Rita',g2toast:'Fazenda: Santa Rita'});
  const R=eRowsReq(C,faz); GR('g_req').rows=R.rows; GR('g_req').x0=R.x0;
  GR('g_rec').rows=eRowsRec(C,faz); GR('g_cnt').rows=eRowsCnt(C,faz);
  GR('g_lot').rows=eRowsLot(C,faz,self.state.est_loc||'',PF); GR('g_mov').rows=eRowsMov(C);
  v.mov_tem=GR('g_mov').rows.length>0; v.mov_nada=!v.mov_tem; const PRL=estProducao(C,faz); v.prod_lin=PRL.map(p=>({prod:p.prod,txt:p.txt,lotes:p.lotes+(p.lotes>1?' lotes':' lote')})); v.prod_nada=!PRL.length;
  // opções dinâmicas dos painéis: recebedor (pessoas do cadastro e responsáveis das O.S.), pedido aberto, local da fazenda, resultado do laudo
  self.g2opts=(gid,k,draft)=>{ const o=x=>({v:x,t:x});
    if(gid==='g_req'&&(k==='quemr'||k==='quem')) return eRecebedores(C).map(o);
    if(gid==='g_rec'&&k==='ped'){ const ab=epeds(C).filter(x=>x.a_entregar>0||x.label===draft.ped); return ab.map(x=>({v:x.label,t:x.label+' · '+eq(x.a_entregar,x.un)+' a entregar'})); }
    if(gid==='g_rec'&&k==='local'){ const fz=faz==='Todas'?'':faz; return (E2.locais||[]).filter(l=>(E2.tipos_estoque||[]).indexOf(l.tipo)>=0&&(!fz||l.faz===fz||l.nome===draft.local)).map(l=>o(l.nome)); }
    if(gid==='g_rec'&&k==='res'){ const fm=g2st(self,'g_rec').fm; const al=(fm&&fm.al)||{}; const p=eParcela(C,al.key,al.doc); return (p&&p.venc?['Reprovado']:E2.resultados).map(o); }
    return []; };
  // unidade dos campos de quantidade = unidade do item (nunca "kg" fixo)
  const fq=GR('g_req').edit.fields, fmQ=g2st(self,'g_req').fm; if(fmQ&&fmQ.al){ const x=fmQ.al.prod?eReqItem(C,fmQ.al.rid,fmQ.al.prod):null; const u=x?x.un:'';
    fq.forEach(f=>{ if(f.k==='qtd'||f.k==='dqtd') f.u=u; });
    const fd=fq.find(f=>f.k==='dqtd'); fd.help=x?('Esperado: '+eq(x.it.custodia,x.un)+' com '+x.quem+'. Digite o que voltou de fato.'):''; const fe=fq.find(f=>f.k==='qtd'); fe.help=x?('Até '+eq(Math.min(x.ent,x.livreReq),x.un)+': '+econta(x)+'.'):''; }
  const fr=GR('g_rec').edit.fields, fmR=g2st(self,'g_rec').fm; if(fmR&&fmR.draft){ const p=epedBase(fmR.draft.ped); const u=p?p.un:''; fr.forEach(f=>{ if(['qtd_nf','conf','quar','apto'].indexOf(f.k)>=0) f.u=u; });
    const fV=fr.find(f=>f.k==='val'); const fe=efert(fmR.draft.ped); fV.ro=fe; fV.help=fe?'Fertilizantes, corretivos e embalagens: sem validade de lote.':'Mês/ano (ex.: 06/2027). Lote vencido entra todo em quarentena.'; }
  const fc=GR('g_cnt').edit.fields, fmC=g2st(self,'g_cnt').fm; if(fmC&&fmC.al){ const rec=einvRec(C,fmC.al.inv); const l=rec&&C.lotes[rec.key]; fc[0].u=l?l.un:''; }
}
function EXTRAVALS(self,v){
  const st=self.state; const C=self._cen||cenGet(); const PF=g2perfil(); const faz=efaz(self);
  // trocar o perfil (menu lateral) reabre pelo papel e fecha os painéis montados para o perfil anterior (revisão do CTL-3, achado 1)
  const g2f=Object.assign({},st.g2||{}); ['g_req','g_rec','g_cnt','g_lot','g_mov'].forEach(g=>{ if(g2f[g]) g2f[g]=Object.assign({},g2f[g],{fm:null}); });
  self.g2perfilFecha={step:undefined,g2:g2f};
  self.g2live=(gid,k,d)=>{ if(gid==='g_rec'&&k==='val'&&efert(d.ped)) return 'Sem validade';
    if(gid==='g_rec'&&k==='apto'){ const a=enum_(d,'conf'), q=eblank(d.quar)?0:enum_(d,'quar'); return isNaN(a)?'':String(Math.max(0,a-(isNaN(q)?0:q))).replace('.',','); } return undefined; };
  // ---- endereço (#sec, #req, #os, #nf, #lote): abre o lugar certo; nunca grava nada ----
  const abrirHash=()=>{ let h=''; try{ h=decodeURIComponent(location.hash||''); }catch(e){ h=''; } if(!h) return; const C0=cenGet(), P0=g2perfil();
    const m=(k)=>{ const x=new RegExp('[#&]'+k+'=([^&]+)').exec(h); return x?x[1]:''; };
    const sec=m('sec').toLowerCase(), req=m('req'), os=m('os'), nf=m('nf'), lote=m('lote'); let patch=null;
    const fz=(f)=>{ const cur=self.state.mf_faz||'Santa Rita'; return (f&&cur!=='Todas'&&cur!==f)?{mf_faz:f}:{}; };
    if(req&&C0.reqs[req]){ const o=C0.ordens[C0.reqs[req].os]||{}; patch=ePatch(self,'g_req','R|'+req,eModoReq(C0,'R|'+req,P0),false,Object.assign({step:1},fz(estFazOrd(o)))); }
    else if(os&&C0.ordens[os]){ const o=C0.ordens[os]; const rid=o.req&&C0.reqs[o.req]?'R|'+o.req:'S|'+os; patch=ePatch(self,'g_req',rid,eModoReq(C0,rid,P0),false,Object.assign({step:1},fz(estFazOrd(o)))); }
    else if(nf){ const pcs=estParcelas(C0,'Todas'); const pc=pcs.find(p=>p.doc===nf&&!p.laudo)||pcs.find(p=>p.doc===nf); const rc=erecs(C0).find(x=>x.nf===nf);
      if(pc){ const rid='P|'+pc.key+'|'+pc.doc; patch=ePatch(self,'g_rec',rid,eModoRec(C0,rid,P0),false,Object.assign({step:2},fz(estFazLocal(pc.local)))); }
      else if(rc){ const rid='N|'+rc.id; patch=ePatch(self,'g_rec',rid,eModoRec(C0,rid,P0),false,Object.assign({step:2},fz(estFazLocal(rc.local)))); } }
    else if(lote){ const k=Object.keys(C0.lotes).find(x=>C0.lotes[x].lote===lote); if(k){ const all=eSoUm(self,'g_lot'); all.g_lot=Object.assign({},all.g_lot||{},{fm:{rid:'L|'+k,draft:{},orig:{},errs:{},warn:false,ro:true,isNew:false,mode:'origin'},fl:null});
      patch=Object.assign({g2:all,step:4,est_modo:'lotes',est_loc:''},fz(estFazLocal(C0.lotes[k].local))); } }
    else if(sec){ const n=E2.sec[sec]; if(n) patch=Object.assign({step:n},n===4&&E2.sec_modo[sec]?{est_modo:E2.sec_modo[sec]}:{}); }   /* desconhecido: regra sem endereço, sem gravar */
    if(patch) setTimeout(()=>self.setState(patch),0); };
  if(!self.__hashIni){ self.__hashIni=1; abrirHash(); try{ window.addEventListener('hashchange',abrirHash); }catch(e){} }
  // ---- seção: escolhida, do endereço, ou a abertura pelo perfil (calculada uma vez por perfil e fazenda; abrir não muda o cenário) ----
  if(self.__abPf!==PF.k||self.__abFaz!==faz){ self.__abPf=PF.k; self.__abFaz=faz; self.__ab=estAbertura(C,PF.k,faz); }
  const step=st.step||self.__ab||1; const N=4;
  for(let i=1;i<=N;i++) v['s'+i]=(step===i);
  g2secoes(self,v,'stp',N,step,{},(i)=>g2etapa(self,{step:i}));
  const K=estContadores(C,faz); [K.req,K.rec,K.cnt,''].forEach((t,i)=>{ v['stp'+(i+1)+'_cnt']=t; v['stp'+(i+1)+'_hasCnt']=!!t; });
  // ---- Confira saldos: modos e chips de local (fonte única, da fazenda do filtro) ----
  const modo=st.est_modo||'lotes'; v.m_lotes=modo==='lotes'; v.m_movs=modo==='movs'; v.m_prod=modo==='prod';
  const CH='font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;';
  const chs=(on)=>CH+(on?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;');
  v.est_modos=[['lotes','Lotes'],['movs','Movimentos'],['prod','Produção']].map(([k,t])=>({t,on:String(modo===k),st:chs(modo===k),go:()=>self.setState({est_modo:k})}));
  const loc=st.est_loc||''; const fzl=faz==='Todas'?'':faz;
  const locs=(E2.locais||[]).filter(l=>(E2.tipos_estoque||[]).indexOf(l.tipo)>=0&&(!fzl||l.faz===fzl)).map(l=>l.nome);
  v.est_locs=[''].concat(locs).map(lc=>({t:lc||'Todos os locais',on:String(loc===lc),st:chs(loc===lc),go:()=>self.setState({est_loc:lc})}));
  // ---- Contar local: uma contagem cega por lote do local, atribuída a quem age; o painel anda por "Contar o próximo" ----
  const clv=(st.cl_v&&locs.indexOf(st.cl_v)>=0)?st.cl_v:(locs[0]||''); v.cl_v=clv; v.cl_opts=locs.map(x=>({v:x,t:x})); v.cl_set=(e)=>self.setState({cl_v:e.target.value});
  v.cl_go=()=>{ const quem=g2ator(PF,'almoxarife'); const ids=[];
    const r=cenMudar(null,c=>{ const ls=Object.keys(c.lotes).filter(k=>c.lotes[k].local===clv); if(!ls.length) throw new Error('Nenhum lote em '+clv+'.');
      ls.forEach(k=>{ const id=enovoInv(c); ids.push(id); eput(c,{id,key:k,sis:null,cont:null,contador:quem,causa:'',aj:null,hist:[],grupo:'CL-'+clv}); });
      return {msg:'Contar '+clv+': '+ls.length+(ls.length>1?' lotes':' lote')+' para '+quem+', sem ver o saldo.'}; });
    if(r.erro){ self.setState({g2toast:r.erro}); return; } eAbrir(self,'g_cnt',ids[0],{modo:'contar',inv:ids[0],lote:'CL-'+clv},false,{step:3,cenrev:Date.now(),g2toast:r.msg}); };
  v.est_nf_new=()=>eAbrir(self,'g_rec',null,{modo:'nf'},true);
  // ---- textos, rótulo da primária e ações secundárias de cada painel (o painel aberto assume a tarefa: uma primária) ----
  ePainelReq(self,v,C,PF); ePainelRec(self,v,C,PF); ePainelCnt(self,v,C,PF);
  const Fl=v.g_lot_F; if(Fl&&Fl.open){ Fl.title='Lote · '+String((g2st(self,'g_lot').fm||{}).rid||'').split('|').pop(); Fl.sub='Consulta: o saldo muda só por movimento (receber, entregar, devolver, contar).'; }
  const Fm=v.g_mov_F; const fmM=g2st(self,'g_mov').fm; if(Fm&&Fm.open&&fmM){ const m=(C.movs||[]).find(x=>x.id===fmM.rid); if(m){ Fm.title='Movimento · '+m.id; Fm.sub=(m.prod?m.prod+(m.lote?' · lote '+m.lote:'')+': ':'')+emovTxt(m)+(esemSinal(C)[m.id]?' · aguardando sinal.':'.');   /* o lote saiu da grade (10/10) */ } }
  // restaurar a demonstração (cenário compartilhado volta ao início)
  v.est_rst_ask=!!st.est_rst; v.est_rst_no=!st.est_rst;
  v.est_rst=()=>self.setState({est_rst:true}); v.est_rst_cancel=()=>self.setState({est_rst:false});
  v.est_rst_ok=()=>{ cenReset(); self.__abPf=undefined; self.setState({est_rst:false,g2:{},est_loc:'',est_modo:'lotes',step:undefined,cenrev:Date.now(),g2toast:'Demonstração restaurada: O.S., estoque e app voltaram ao início.'}); };
}
function eActs(lista){ return lista.filter(Boolean).map(a=>({t:a.t,h:a.h||'',go:a.go})); }
function ePainelReq(self,v,C,PF){ const F=v.g_req_F; const fm=g2st(self,'g_req').fm; if(!F||!F.open||!fm||!fm.al) return; const al=fm.al, d=fm.draft||{};
  const k=al.k?eConf(C,al.k):null; const rid=al.rid||(k&&k.req)||''; const L=rid?eReqLinha(C,rid):null; const o=L?L.o:(k?C.ordens[k.os]||{}:{});
  const modo=(nm,x)=>()=>eModo(self,'g_req',Object.assign({modo:nm},x));
  const acts=[]; const conta=(x)=>x.it.prod+' (lote '+x.it.lote+'): solicitado '+eq(x.it.solicitado,x.un)+' · entregue '+eq(x.it.entregue,x.un)+' · consumido '+eq(x.it.consumido,x.un)+(x.it.devolvido>1e-9?' · devolvido '+eq(x.it.devolvido,x.un):'')+' · em custódia '+eq(x.it.custodia,x.un)+(cenAtiva(x.o)?' · a entregar '+eq(x.pend,x.un):'');   /* O.S. fora de Liberadas/Em execução não recebe entrega: sem "a entregar" */
  const prox=()=>{ const n=estFila(C,efaz(self)).find(y=>y.acao&&y.rid&&y.rid!==rid&&(y.entregar||y.sobra||y.confs.length)); return n?{t:'Próxima: '+n.rid+' ›',go:()=>{ try{ location.hash='#req='+n.rid; }catch(e){} }}:null; };
  if(fm.rcb){ F.title='Comprovante · '+(rid||al.k||''); F.sub=fm.rcb; F.acts=eActs([prox()]); F.hasActs=F.acts.length>0; F.origins=[]; F.hasOrigins=false; return; }
  const cab=(rid?rid+' · ':'')+(o.id||'')+(o.etapa?' '+o.etapa:'');
  if(L) L.itens.forEach(x=>{ if(!(al.modo==='ent'&&al.prod===x.it.prod)&&x.parte>1e-9) acts.push({t:'Entregar parte de '+x.it.prod+' ›',go:modo('ent',{rid,prod:x.it.prod})});
    if(!(al.modo==='dev'&&al.prod===x.it.prod)&&eDevOk(x)) acts.push({t:'Registrar devolução de '+x.it.prod+' ›',go:modo('dev',{rid,prod:x.it.prod})}); });
  if(L&&L.inteira&&al.modo!=='req') acts.unshift({t:'‹ Entregar a '+rid+' inteira',go:modo('req',{rid})});
  if(L) L.confs.forEach(c2=>{ if(!((al.modo==='conc'||al.modo==='rec')&&al.k===c2.id)) acts.push({t:'Conciliar '+c2.id+' ('+c2.prod+') ›',go:modo('conc',{k:c2.id})}); });
  let sub=[], savel='', ro=!!fm.ro;
  if(al.modo==='req'&&L){ const R=estRotuloReq(C,rid,d.quemr); F.title='Requisição · '+cab;
    sub=L.itens.map(conta).concat(['Separe:'].concat(R.separe.map(t=>'· '+t)));
    L.itens.filter(x=>/^Reserva parcial/.test(x.sit)).forEach(x=>{ const tot=((o.ins||[]).find(i=>i.p===x.it.prod)||{}).tot; sub.push(x.os+' pede '+eq(tot||x.pend,x.un)+' de '+x.it.prod+'; a '+rid+' reservou '+eq(x.it.solicitado,x.un)+': a falta fica com Compras (pedido ou solicitação).'); });
    savel=R.rotulo; }
  else if(al.modo==='ent'&&eReqItem(C,rid,al.prod)){ const x=eReqItem(C,rid,al.prod); F.title='Entregar parte · '+rid+' › '+al.prod; const n=enum_(d,'qtd');
    sub=[conta(x),'Separe: '+x.it.lote+(x.l&&x.l.validade&&x.l.validade!=='—'?' · val. '+x.l.validade:'')+(x.l?' · '+x.l.local:'')+(x.insuf?' · lote insuficiente: o lote tem '+eq(x.livreReq,x.un)+' para esta requisição':''),'A O.S. só inicia com a mistura completa entregue e confirmada no app (ESTOS-03).'];
    savel='Entregar '+(n>0?eq(n,x.un)+' de ':'parte de ')+x.it.prod+' (lote '+x.it.lote+')'+(d.quem?' a '+d.quem:''); }
  else if(al.modo==='dev'&&eReqItem(C,rid,al.prod)){ const x=eReqItem(C,rid,al.prod); F.title='Devolução · '+rid+' › '+al.prod; const n=enum_(d,'dqtd');
    sub=[conta(x),'Em custódia: '+eq(x.it.custodia,x.un)+' de '+x.it.prod+' com '+x.quem+' ('+x.os+(x.o.etapa?' '+x.o.etapa.toLowerCase():'')+').','Confira e digite o que voltou: só o conferido volta ao lote '+x.it.lote+(cenAindaRetira(x.o)?' e à reserva da '+rid:'')+'; bloqueada vai para quarentena até o laudo.'];
    savel='Registrar devolução'+(n>0?' · '+eq(n,x.un):'')+' de '+x.it.prod; }
  else if(al.modo==='conc'||al.modo==='rec'){ F.title=(al.modo==='rec'?'Recusar relato · ':'Consumo em conferência · ')+(k?k.id:al.k);
    if(!k||k.estado!=='Em conferência'){ ro=true; sub=['Este consumo não está mais em conferência.']; }
    else { let p; try{ p=cenConcPrevia(C,k.id); }catch(e){ p={erro:String(e.message||e)}; } const exc=estSitCf(C,k)==='Aguardando gestora';
      sub=[k.prod+': '+cenConfTxt(k,C)+' · relatado por '+k.quem+' ('+k.os+(k.req?' · '+k.req:' · sem requisição')+(k.lote==='—'?' · fora da requisição':'')+').', p.erro?p.erro:p.txt];
      if(al.modo==='rec'){ savel='Recusar relato '+k.id; acts.unshift({t:'‹ Voltar ao aceite',go:modo('conc',{k:k.id})}); }
      else { acts.unshift({t:'Recusar relato '+k.id+' ›',go:modo('rec',{k:k.id})});
        if(p.erro){ ro=true; sub.push('Conte o lote ou recuse o relato.'); }
        else if(exc&&!g2papel(PF,'gestor')){ ro=true; sub.push('O que passa da custódia sai do lote: aceite de '+g2quem('gestor')+' (padrão 2). Você pode recusar o relato com o motivo.'); }
        else if(!exc&&!g2umPapel(PF,['almoxarife','gestor'])){ ro=true; sub.push('Aceite de '+g2quemUm(['almoxarife','gestor'])+'.'); }
        else savel=exc?('Aprovar consumo · '+eq(p.falta,k.un)+' além da custódia'):('Aceitar consumo · '+eq(k.relatado,k.un)+' de '+k.prod); } } }
  else { F.title='Requisição · '+cab; const x0=L&&L.itens[0]; const mot=x0?(x0.bloq||x0.motivo):''; sub=(L?L.itens.map(conta):[]).concat(mot?[mot]:[]).concat(L&&L.sit==='Concluída'?['Nada a entregar nem a receber.']:[]); ro=true; }
  if(ro!==!!fm.ro){ setTimeout(()=>{ const f2=g2st(self,'g_req').fm; if(f2&&f2.chave===fm.chave&&!!f2.ro!==ro) g2set(self,'g_req',{fm:Object.assign({},f2,{ro})}); },0); }
  F.sub=sub.join('\n'); F.savel=savel||'Registrar'; F.acts=eActs(acts); F.hasActs=F.acts.length>0; F.origins=[]; F.hasOrigins=false; }
function ePainelRec(self,v,C,PF){ const F=v.g_rec_F; const fm=g2st(self,'g_rec').fm; if(!F||!F.open||!fm||!fm.al) return; const al=fm.al, d=fm.draft||{};
  if(fm.rcb){ F.title='Comprovante'; F.sub=fm.rcb; F.acts=[]; F.hasActs=false; return; }
  if(al.modo==='nf'){ F.title=fm.isNew?'Registrar NF recebida':('Conferir '+((al.rec||{}).nf||'')); F.sub='Confira a nota contra o pedido e o material: só a parte apta entra no disponível; a quarentena vira parcela da nota e sai com o laudo.';
    const pd=!fm.isNew&&al.rec?epedBase(al.rec.ped):null; if(pd) F.sub=pd.id+' · '+pd.forn+' · '+eq(pd.a_entregar,pd.un)+' de '+pd.item+' a entregar.\n'+F.sub;   /* o fornecedor saiu da grade (10/10) */
    F.savel=fm.isNew?'Registrar NF'+(d.nf?' '+d.nf:''):('Conferir '+((al.rec||{}).nf||'NF')); return; }
  if(al.modo==='laudo'||al.modo==='cons'){ const pc=al.key?eParcela(C,al.key,al.doc):null;
    if(pc){ F.title='Parcela '+pc.doc+' › '+pc.lote; const L=C.lotes[pc.key];
      const b0=erecs(C).find(x=>x.nf===pc.doc); const pd=b0?epedBase(b0.ped):null;   /* origem da parcela: pedido e fornecedor (saíram da grade, 10/10) */
      F.sub=[pc.prod+': '+eq(pc.qtd,pc.un)+' em quarentena'+(pc.motivo?' · '+pc.motivo:'')+(pc.por?' · registrada por '+pc.por:''),'Origem: '+pc.doc+(pd?' · '+pd.id+' · '+pd.forn:(/^REQ-/.test(pc.doc)?' · devolução da O.S.':'')),'Lote '+pc.lote+' · '+pc.local+(L&&L.validade&&L.validade!=='—'?' · validade '+L.validade:'')+(pc.venc?' · vencido: não volta ao disponível':'')]
        .concat(pc.laudo?['Laudo '+pc.laudo.num+' reprovado por '+pc.laudo.por+(pc.laudo.destino?' · destino: '+pc.laudo.destino:'')]:[])
        .concat(al.modo==='cons'&&!pc.laudo?['Laudo: decisão de '+g2quem('gestor')+'. O laudo libera só esta parcela.']:[]).join('\n');
      if(al.modo==='laudo') F.savel=d.res==='Reprovado'?'Manter bloqueada · laudo reprovado':('Liberar parcela · '+eq(pc.qtd,pc.un));
      F.acts=eActs([{t:'Ver o lote '+pc.lote+' em Confira saldos ›',go:()=>{ try{ location.hash='#lote='+pc.lote; }catch(e){} }}]); F.hasActs=true; return; }
    const r=al.rec; if(r){ F.title='Nota '+r.nf; const pd=epedBase(r.ped); F.sub=(pd?pd.id+' · '+pd.forn+' · ':'')+'Conferida: '+eq(r.conf,r.un)+' de '+r.item+' no lote '+r.lote+(r.quar?' · '+eq(r.quar,r.un)+' em quarentena (parcela da nota)':'')+'. Documento já lançado não cria segunda entrada.'; } } }
function ePainelCnt(self,v,C,PF){ const F=v.g_cnt_F; const fm=g2st(self,'g_cnt').fm; if(!F||!F.open||!fm||!fm.al) return; const al=fm.al;
  const rec=einvRec(C,al.inv)||{}; const l=C.lotes[rec.key]||{}; const un=l.un||''; const aj=eajuste(C,rec); const quem=g2ator(PF,'almoxarife');
  const nxt=()=>{ if(!al.lote) return null; return einvs(C).find(r=>r.grupo===al.lote&&r.id!==al.inv&&!econtou(r))||null; };
  F.title='Contagem '+(rec.id||al.inv)+' · '+(l.lote||'')+' · '+(l.prod||'');
  if(fm.rcb){ F.sub=fm.rcb; const n=nxt(); F.acts=eActs([n?{t:'Contar o próximo: '+n.id+' ('+(C.lotes[n.key]||{}).lote+') ›',go:()=>eAbrir(self,'g_cnt',n.id,{modo:'contar',inv:n.id,lote:al.lote})}:null]); F.hasActs=F.acts.length>0; return; }
  const acts=[];
  if(al.modo==='contar'){ F.sub=['Contagem cega: informe só o que contou, na unidade do lote ('+un+'). O sistema e a diferença aparecem depois de salvar.','Local '+(l.local||'')+' · contador: '+quem+(rec.contador&&!g2mesma(quem,rec.contador)?' (atribuída a '+rec.contador+')':'')]
      .concat((rec.hist||[]).length?['Recontagem: quem contou antes não reconta.']:[]).join('\n'); F.savel='Salvar contagem'; }
  else if(al.modo==='causa'){ const dif=rec.cont-rec.sis; F.sub=['Contado '+eq(rec.cont,un)+' · sistema na data '+eq(rec.sis,un)+' · diferença '+esig(dif,un)+'.','Informe a causa: o ajuste vai à gestora; o saldo não muda até a aprovação.'].concat(aj&&aj.afeta&&aj.afeta.length?['Atinge a reserva da '+aj.afeta.join(', ')+'.']:[]).join('\n');
    F.savel='Enviar ajuste à gestora'; acts.push({t:'Pedir recontagem',go:()=>eRecontar(self,al.inv)}); }
  else if(al.modo==='aprov'||al.modo==='aguarda'){ const dif=rec.cont-rec.sis; const afeta=(aj&&aj.afeta)||[];
    F.sub=['Contado '+eq(rec.cont,un)+' por '+rec.contador+' · sistema '+eq(rec.sis,un)+' · diferença '+esig(dif,un)+'.','Causa: '+(rec.causa||'—')+'.']
      .concat(afeta.length?['Afeta a reserva da '+afeta.join(', ')+': depois do ajuste, a requisição fica "Lote insuficiente" e só entrega parte.']:[])
      .concat(al.modo==='aguarda'?['Aprova: '+g2quem('gestor')+'.']:(g2mesma(PF.k,rec.contador)?['Você contou: a decisão fica registrada como sua, com revisão independente pendente (ninguém mais revisou).']:[])).join('\n');
    F.savel='Aprovar ajuste · '+esig(dif,un); acts.push({t:'Pedir recontagem',go:()=>eRecontar(self,al.inv)}); }
  else { F.sub=(rec.cont!=null?'Contado '+eq(rec.cont,un)+' · sistema '+eq(rec.sis,un)+(aj&&aj.estado==='Aprovado'?' · ajuste aprovado por '+aj.por+(aj.rev?' · '+aj.rev:''):''):'Consulta')+'.'; }
  F.acts=eActs(acts); F.hasActs=F.acts.length>0; }
function eRecontar(self,inv){ const r=cenMudar(null,c=>estRecontar(c,inv)); if(r.erro){ self.setState({g2toast:r.erro}); return; }
  eAbrir(self,'g_cnt',inv,{modo:'contar',inv},false,{cenrev:Date.now(),g2toast:r.msg}); }
'''
JS=open(os.path.join(HERE,'est.js'),encoding='utf-8').read()+'\n'+JS_TELA
