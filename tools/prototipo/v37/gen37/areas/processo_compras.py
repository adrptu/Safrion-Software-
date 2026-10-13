# -*- coding: utf-8 -*-
"""Suprimentos › Compra de insumos — processo em 6 etapas numa só tela de trabalho (CMP.dc.html).
1 Escolha a safra → 2 Confira a demanda → 3 Solicite cotações → 4 Compare propostas → 5 Aprove a compra → 6 Acompanhe a entrega.
Safra, solicitação (SOL-2026-07), convites, propostas, aprovação e pedidos ficam vinculados e visíveis em todas as etapas.

Dados: dados2 (SAFRAS, SOL_INICIAL + sol_itens(), demanda() com CAL-01, FORNECEDORES, PROPOSTAS, ALCADA, PEDIDOS, LOTES) + constantes locais abaixo.
Solicitações enviadas pelo Planejar safra chegam pelo registro compartilhado talhao-os-compras-v1 (localStorage) e pelo endereço #sol=…&saf=…."""
import json, os
from engine import (grid,esc,MUTED,LINE,BG,SURF,ACC,YEL,YELS,RED,REDS,BTN_ST,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, steps_state, HEIGHTS37
import dados2 as D2

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
NOMES=['Escolha a safra','Confira a demanda','Solicite cotações','Compare propostas','Aprove a compra','Acompanhe a entrega']

# ---------------- constantes locais (coerentes com dados2; declaradas em observações) ----------------
PERFIL=dict(nome='Ana',papel='Gestora',nivel='Gerente da fazenda',idx=1)   # alçada do perfil atual = 2º nível de dados2.ALCADA
FRETE_FOB={'kg':0.15,'L':0.40}           # R$ por unidade, frete por conta da fazenda quando a proposta é FOB (estimativa)
PRAZOS=['25/09/2026','26/09/2026','29/09/2026','30/09/2026']
PRAZO_PADRAO='26/09/2026'
MOTIVO_NH={'F07':'Sem e-mail de cotação e documentação fiscal pendente'}
PC_INI=101                              # PC-093…095 já existem em Suprimentos (diesel, filtros); novos pedidos da SOL começam em PC-101
SOL_2526='SOL-2025-06'
PED_2526=[  # compras da safra encerrada (consulta)
 dict(id='PC-061',f='F01',item='MAP 11-52',un='kg',qtd=150000,preco=3.72,previsao='2025-09-18'),
 dict(id='PC-066',f='F05',item='Semente de soja 58 W',un='kg',qtd=32000,preco=9.10,previsao='2025-09-26'),
 dict(id='PC-070',f='F03',item='Fungicida A',un='L',qtd=400,preco=141.0,previsao='2025-11-20'),
]

def nfb(n,d=0):
    s=f"{n:,.{d}f}"; return s.replace(',','X').replace('.',',').replace('X','.')
def _forn(fid): return next((f['nome'] for f in D2.FORNECEDORES if f['id']==fid),fid)
def _iso(br): d,m,a=br.split('/'); return f'{a}-{m}-{d}'
def _br(iso): a,m,d=iso.split('-'); return f'{d}/{m}/{a}'
def _k(s): return s.lower().replace('ó','o').replace('á','a').replace('é','e').replace('í','i')

def _cd():
    dem=D2.demanda('S2627'); sol=D2.sol_itens()
    itens=sorted([dict(nome=n,grupo=o['grupo'],un=o['un'],preco=o['preco_ref'],nec=o['qtd']) for n,o in sol.items()],key=lambda x:(x['grupo'],_k(x['nome'])))
    for i,x in enumerate(itens): x['i']=i
    quar={l['item']:l['quarentena'] for l in D2.LOTES if l['quarentena']}
    # entradas e resultado do CAL-01 por insumo (cal01.js refaz a memória e a data da falta na tela, com as previsões reprogramadas)
    dm=[dict(nome=n,grupo=o['grupo'],un=o['un'],preco=o['preco'],bruta=o['bruta'],real=o['real'],est=o['estoque'],res=o['reservado'],rec=o['receb'],liq=o['liq'],valor=o['valor'],
             falta=o['falta'],quar=quar.get(n,0),evs=o['evs']) for n,o in dem.items()]
    ref=sum(x['nec']*x['preco'] for x in itens)
    safras=[]
    for s in D2.SAFRAS:
        x=dict(id=s['id'],nome=s['nome'],periodo=s['periodo'],estado=s['estado'],faz=s['fazenda'])
        safras.append(x)
    peds=[dict(id=p['id'],f=p['f'],forn=_forn(p['f']),item=p['item'],un=p['un'],qtd=p['qtd'],rec=p['recebido'],apto=p['apto'],quar=p['quarentena'],ae=p['a_entregar'],
               preco=p['preco'],prev=_iso(p['previsao']),estado=p['estado']) for p in D2.PEDIDOS]
    nf_prev={r['pedido']:r['id'] for r in D2.RECEBIMENTOS if r['qtd_conf'] is None}
    for p in peds: p['nfprev']=nf_prev.get(p['id'],'')
    p26=[dict(id=p['id'],f=p['f'],forn=_forn(p['f']),item=p['item'],un=p['un'],qtd=p['qtd'],preco=p['preco'],prev=p['previsao']) for p in PED_2526]
    return dict(hojeIso=_iso(D2.HOJE),viavel=D2.VIAVEL,sol=D2.SOL_INICIAL,itens=itens,dem=dm,ref=ref,safras=safras,sol2526=SOL_2526,
                forn=[dict(id=f['id'],nome=f['nome'],grupos=f['grupos'],email=f['email'],whats=f['whats'],homologado=f['homologado'],motivo=MOTIVO_NH.get(f['id'],''),
                           contato=f.get('contato',''),canais=f.get('canais') or ['E-mail']) for f in D2.FORNECEDORES],
                props=D2.PROPOSTAS,alcada=D2.ALCADA,perfil=PERFIL,fob=FRETE_FOB,prazos=PRAZOS,prazoPadrao=PRAZO_PADRAO,pcIni=PC_INI,pedidos=peds,ped2526=p26)

def bloco(titulo,desc,corpo,acao='',tit_hole=False):
    t=titulo if tit_hole else esc(titulo)
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{t}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>{acao}</div>'
            f'<div style="padding: 0 12px 12px;">{corpo}</div></section>')
def kline(hole):
    return f'<div style="font-size: 13px; line-height: 1.45;"><span style="{H(hole+"st")}">{H(hole)}</span></div>'
def build():
    fname='CMP.dc.html'; E._reset_screen(fname)
    # ---------- etapa 1 · safras e solicitações ----------
    g_saf=grid([dict(k='nome',l='Safra',w=190),dict(k='sol',l='Solicitação de compra',w=270),dict(k='orig',l='Origem',w=190),dict(k='comp',l='Compra',w=230),dict(k='acao',l='Ação')],
               [],edit=dict(m='pick'),search=False,gid='g_saf',total=False)
    # ---------- etapa 2 · demanda da solicitação (mesmas colunas e números do Planejar safra) ----------
    g_dem=grid([dict(k='ins',l='Grupo · insumo',w=220),dict(k='bruta',l='Bruta',t='num',a='r'),dict(k='est',l='Estoque apto',t='num',a='r',w=112),dict(k='rec',l='A receber',t='num',a='r',w=104),
                dict(k='liq',l='Necessidade',t='num',a='r'),dict(k='un',l='Un.'),dict(k='falta',l='Falta a partir de',t='date'),
                dict(k='preco',l='Preço ref.',t='num',a='r',d=2),dict(k='valor',l='Valor (R$)',t='num',a='r',d=2,agg='sum'),
                dict(k='sit',l='Na compra',w=200)],
               [],edit=dict(m='origin',leafOnly=True,title='Insumo',fields=[dict(k='ins',l='Insumo',t='txt',ro=True),dict(k='un',l='Unidade',t='txt',ro=True)]),tree=True,gid='g_dem',total=True,qf=dict(k='sit',cut=' · ',num=True,l='situação na compra'))
    # ---------- etapa 3 · convites por grupo ----------
    g_conv=grid([dict(k='nome',l='Grupo · fornecedor',w=210),dict(k='homol',l='Homologação',w=210),dict(k='conv',l='Convite'),dict(k='canal',l='Canal e contato',w=236),
                 dict(k='prazo',l='Responder até'),dict(k='resp',l='Resposta',w=190)],
                [],edit=dict(m='form',title='Convite',leafOnly=False,sub='Escolha se convida, por qual canal e até quando o fornecedor responde. O envio é simulado.',
                     fields=[dict(k='conv',l='Convite',t='sel',opts=['Convidar','Não convidar'],req=True),
                             dict(k='canal',l='Canal',t='sel',opts=['E-mail','WhatsApp'],req=True,cond=dict(k='conv',eq='Convidar'),help='Só os canais autorizados no cadastro do fornecedor.'),
                             dict(k='prazo',l='Prazo de resposta',t='sel',opts=PRAZOS,req=True,cond=dict(k='conv',eq='Convidar'))]),
                tree=True,gid='g_conv',total=False,qf=dict(k='resp',l='resposta'))
    # ---------- etapa 4 · comparação de propostas ----------
    g_cmp=grid([dict(k='nome',l='Grupo · insumo · proposta',w=165),dict(k='ped',l='A pedir',t='num',a='r'),dict(k='preco',l='Preço (R$)',t='num',a='r',d=2),
                dict(k='prazo',l='Entrega',t='num',a='r',u='dias',w=80),dict(k='frete',l='Frete',w=74),dict(k='pag',l='Pagamento'),dict(k='val',l='Validade'),
                dict(k='tot',l='Custo (R$)',t='num',a='r',d=2,agg='sum'),dict(k='venc',l='Escolha',w=200)],
               [],edit=dict(m='form',title='Escolha',leafOnly=False,sub='Escolha a proposta e a quantidade a pedir; custo total e pedidos são recalculados.',
                    fields=[dict(k='venc',l='Proposta escolhida',t='sel',opts=[],req=True),
                            dict(k='ped',l='Quantidade a pedir',t='num',req=True,min=0),
                            dict(k='just',l='Justificativa',t='area')]),
               tree=True,gid='g_cmp',total=True)
    # ---------- etapa 5 · pedidos a gerar ----------
    g_apr=grid([dict(k='nome',l='Pedido · fornecedor · insumo',w=260),dict(k='qtd',l='Quantidade',t='num',a='r'),dict(k='preco',l='Preço (R$/un)',t='num',a='r',d=2),
                dict(k='prazo',l='Entrega (dias)',t='num',a='r'),dict(k='frete',l='Frete'),dict(k='pag',l='Pagamento'),dict(k='tot',l='Valor (R$)',t='num',a='r',d=2,agg='sum')],
               [],edit=dict(m='origin',leafOnly=False,title='Pedido',fields=[dict(k='nome',l='Pedido ou insumo',t='txt',ro=True)]),tree=True,gid='g_apr',total=True)
    # ---------- etapa 6 · pedidos e entregas ----------
    g_ent=grid([dict(k='nome',l='Pedido · fornecedor · insumo',w=200),dict(k='qtd',l='Pedido',t='num',a='r'),dict(k='rec',l='Recebido',t='num',a='r',w=120),
                dict(k='ae',l='A entregar',t='num',a='r'),dict(k='val',l='Valor (R$)',t='num',a='r',d=2,agg='sum'),
                dict(k='prev',l='Previsão',t='date'),dict(k='sit',l='Situação',w=240),dict(k='acao',l='Ação')],
               [],edit=dict(m='form',title='Pedido',leafOnly=False,sub='Reprograme a previsão de entrega; o Estoque passa a esperar a nova data.',
                    fields=[dict(k='prev',l='Previsão de entrega',t='date',req=True),dict(k='obs',l='Motivo da reprogramação',t='area',help='Ex.: fornecedor confirmou nova data de embarque.')]),
               tree=True,gid='g_ent',total=True,qf=dict(k='sit',cut=' · '))
    root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXTRAJS[0]='const CD = '+json.dumps(_cd(),ensure_ascii=False)+';\n'+open(os.path.join(root,'cal01.js'),encoding='utf-8').read()+'\n'+JS
    # ---------- corpo ----------
    trail=(f'<sc-if value="{H("tr_on")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px; font-size: 12.5px;">'
           f'<span style="font-size: 10.5px; font-weight: 800; letter-spacing: .06em; color: {MUTED};">DOCUMENTOS DA COMPRA</span>'
           f'<sc-for list="{H("trail")}" as="x" hint-placeholder-count="4"><sc-if value="{H("x.sep")}" hint-placeholder-val="{F()}"><span aria-hidden="true" style="color: {MUTED};">›</span></sc-if>'
           f'<span style="{H("x.st")}">{H("x.t")}</span></sc-for>'
           f'<a href="{H("orig_h")}" style="color: {ACC}; font-weight: 700; text-decoration: none; margin-left: 4px;">{H("orig_t")}</a></div></sc-if>')
    alc=(f'<div style="display: flex; flex-direction: column; gap: 6px;">'
         f'<sc-for list="{H("alc")}" as="a" hint-placeholder-count="3"><div style="{H("a.st")}"><span style="min-width: 190px; font-weight: 700;">{H("a.lim")}</span>'
         f'<span style="flex-grow: 1;">{H("a.quem")}</span><sc-if value="{H("a.hasTag")}" hint-placeholder-val="{F()}"><span style="{H("a.tagst")}">{H("a.tag")}</span></sc-if></div></sc-for>'
         f'<div role="note" style="{H("a5st")}">{H("a5")}</div>'
         f'<sc-if value="{H("conf5")}" hint-placeholder-val="{F()}"><div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700;">{H("c5_msg")}'
         f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("c5_no")}" style="{_MINI}">Voltar</button><button type="button" onClick="{H("c5_yes")}" style="{_MINIP}">Confirmar aprovação</button></div></div></sc-if>'
         # decisão negativa da alçada (simulada): devolver ou recusar, sempre com motivo
         f'<sc-if value="{H("d5_on")}" hint-placeholder-val="{F()}"><div style="display: flex; gap: 8px; flex-wrap: wrap;">'
         f'<button type="button" onClick="{H("d5_dev")}" style="{_MINI}">Registrar devolução</button>'
         f'<button type="button" onClick="{H("d5_rec")}" style="{_MINI} color: {RED}; border-color: {RED};">Registrar recusa</button></div></sc-if>'
         f'<sc-if value="{H("d5_open")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
         f'<div style="font-size: 13px; font-weight: 600;">{H("d5_t")}</div>'
         f'<textarea aria-label="Motivo da decisão" placeholder="Motivo informado pela alçada" value="{H("d5_mot")}" onChange="{H("d5_set")}" style="font-family: inherit; font-size: 13px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; min-height: 54px; resize: vertical;"></textarea>'
         f'<sc-if value="{H("d5_hasErr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("d5_err")}</span></sc-if>'
         f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H("d5_no")}" style="{_MINI}">Voltar</button><button type="button" onClick="{H("d5_yes")}" style="{_MINIP}">{H("d5_btn")}</button></div></div></sc-if></div>')
    # UX-ACAO-UNICA-20261003: a ação da etapa (avanço, envio, aprovação, link para o Estoque) sai do cabeçalho do bloco e vai para a
    # área de ações única ao fim do conteúdo (engine.area_acoes + g2acoes); o cabeçalho do bloco fica com os comandos do conteúdo
    acao_bloco=''
    s1=bloco('Safras e solicitações','Abra a compra da safra: clique na linha ou em Abrir compra.',g_saf,acao=acao_bloco)
    s2=kline('k2')+bloco('Demanda da solicitação por grupo','Confira a necessidade por data (estoque apto com reservas e recebimentos na data de uso), quando o insumo começa a faltar e o valor a preço de referência (R$/un); clique num insumo para ver a memória do cálculo.',g_dem,acao=acao_bloco)
    s3=kline('k3')+bloco('Fornecedores homologados por grupo','Escolha quem convidar, o canal e o prazo; clique no fornecedor para alterar.',g_conv,acao=acao_bloco)
    dec4=(f'<sc-if value="{H("dec4_on")}" hint-placeholder-val="{F()}"><div role="alert" style="padding: 8px 12px; border-radius: 10px; font-size: 13px; font-weight: 700; background: {REDS}; color: {RED};">{H("dec4")}</div></sc-if>')
    s4=kline('k4')+dec4+bloco('Propostas por grupo e insumo','Compare custo total, prazo e condições; clique no insumo ou numa proposta para escolher e definir a quantidade.',g_cmp,acao=acao_bloco)
    s5=(kline('k5')+bloco('Alçada de aprovação','Confira quem aprova pelo valor total; navegar entre as etapas não aprova nada.',alc)
        +bloco(H('apr_tit'),'Confira fornecedores, insumos e valores de cada pedido; clique para ver a origem.',g_apr,acao=acao_bloco,tit_hole=True))
    s6=kline('k6')+bloco('Pedidos e entregas','Acompanhe recebido, quarentena e saldo a entregar; clique no pedido para reprogramar a entrega.',g_ent,acao=acao_bloco)
    corpo=trail+''.join(f'<sc-if value="{H("s"+str(i))}" hint-placeholder-val="{H("true") if i==1 else F()}"><div style="display: flex; flex-direction: column; gap: 14px;">{s}</div></sc-if>'
                        for i,s in enumerate([s1,s2,s3,s4,s5,s6],1)) + E.area_acoes('aa','Ações da etapa')
    HEIGHTS37[fname]=1200
    shell37('CMP','Compras',corpo,fname=fname,subtitle='Da solicitação do planejamento ao pedido entregue: cote, compare, aprove e acompanhe na mesma tela.',
            steps=steps_state(NOMES),primary_html=None,ctx=(H('ctx_faz'),H('ctx_saf'),None),search=False)

JS=r'''
// ===== Processo · Compra de insumos (6 etapas numa só tela de trabalho) =====
function GR(id){ return GRIDS.find(g=>g.id===id); }
function nf(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function rs(n){ return 'R$ '+nf(n,2); }
function qt(n,un){ n=Number(n)||0; const d=Math.abs(n-Math.round(n))>1e-9?(un==='L'?1:2):0; return nf(n,d)+' '+un; }
function brd(s){ if(!s) return '—'; const a=String(s).split('-'); return a[2]+'/'+a[1]+'/'+a[0]; }
function addd(s,n){ const d=new Date(s+'T12:00:00'); d.setDate(d.getDate()+n); return d.toISOString().slice(0,10); }
function fnome(id){ const f=CD.forn.find(x=>x.id===id); return f?f.nome:id; }
function toast(self,t){ self.setState({g2toast:t}); }
function pt(a,b){ return String(a).localeCompare(String(b),'pt-BR'); }
// ---------- solicitação da safra aberta: a SOL-2026-07 inicial ou o registro gravado pelo Planejar safra (talhao-os-compras-v1) ----------
const SOL_KEY='talhao-os-compras-v1';
function solLer(){ try{ const o=JSON.parse(localStorage.getItem(SOL_KEY)||'null'); return (o&&o.sols)||{}; }catch(e){ return {}; } }
// safras da compra: as do cadastro e as que só existem numa solicitação gravada pelo Planejar safra (safra nova)
function safras(){ const ls=solLer(); return CD.safras.concat(Object.values(ls).filter(r=>r&&r.safra&&!CD.safras.some(s=>s.id===r.safra)).map(r=>({id:r.safra,nome:r.nome||r.safra,periodo:'',estado:'',faz:r.faz||''}))); }
function safNome(id){ const s=safras().find(x=>x.id===id); return s?s.nome:String(id||''); }
function safHref(saf){ return 'SAF.dc.html#saf='+encodeURIComponent(saf)+'&passo=demanda'; }
const SOLC={}; let SX=null;
function solDe(saf){ if(!saf) return null; const rec=solLer()[saf]; if(!rec&&saf!=='S2627') return null;
  const key=rec?JSON.stringify([rec.id,rec.itens,rec.comp||0]):'ini'; if(SOLC[saf]&&SOLC[saf].key===key) return SOLC[saf]; let x;
  if(!rec) x={safra:saf,nome:safNome(saf),sol:{id:CD.sol.id,enviada:CD.sol.enviada,por:CD.sol.por},itens:CD.itens,dem:CD.dem,ref:CD.ref,comp:0};
  else { const det={}; (rec.det||[]).forEach(d=>{ det[d.nome]=d; }); if(saf==='S2627') CD.dem.forEach(d=>{ if(!det[d.nome]) det[d.nome]=d; });
    const itens=Object.keys(rec.itens||{}).map(n=>{ const d=det[n]||{}; return {nome:n,grupo:d.grupo||'—',un:d.un||'',preco:Number(d.preco)||0,nec:Math.round(Number(rec.itens[n])*100)/100}; })
      .sort((a,b)=>pt(a.grupo,b.grupo)||pt(a.nome,b.nome)); itens.forEach((it,i)=>{ it.i=i; });
    x={safra:saf,nome:rec.nome||safNome(saf),sol:{id:rec.id,enviada:rec.em||rec.at||'',por:rec.por||''},itens,dem:Object.values(det),ref:itens.reduce((a,it)=>a+it.nec*it.preco,0),comp:rec.comp||0}; }
  x.key=key; x.pcIni=CD.pcIni+10*Math.max(0,safras().findIndex(s=>s.id===saf)); x.origem={t:'Planejar safra · '+x.nome+' · demanda de insumos',h:safHref(saf)};
  SOLC[saf]=x; return x; }
function sx(self){ SX=solDe(self.state.saf||null); return SX; }
// memória CAL-01 do insumo (a mesma função do Planejar safra)
const OPT={hoje:CD.hojeIso,viavel:CD.viavel};   // uso antes de hoje = realizado; compra nova chega a partir da data viável
function calDe(d){ return cal01(d.est,d.evs||[],0,OPT); }
// cada safra guarda o próprio andamento da compra (convites, escolhas, aprovação, entregas); trocar de safra não mistura processos.
// O andamento também fica no registro compartilhado (talhao-os-compras-v1 · proc[safra]), ligado à versão da solicitação: recarregar ou ir
// à origem e voltar não perde a compra, e o Planejar safra mostra o estado.
const PROC=['env','nresp','conv','esc','aprov','pcx','dec5']; const PROC_REG=['env','nresp','conv','esc','aprov','pcx'];
function procLer(id){ const x=solDe(id); if(!x) return null; try{ const o=JSON.parse(localStorage.getItem(SOL_KEY)||'null'); const p=o&&o.proc&&o.proc[id];
  return (p&&p.key===x.key&&p.sol===x.sol.id)?p:null; }catch(e){ return null; } }
function procGravar(self,m){ const st=self.state; const id=st.saf; if(!id||!SX||SX.safra!==id) return; const snap={sol:SX.sol.id,key:SX.key,comp:SX.comp||0};
  PROC_REG.forEach(k=>{ snap[k]=(st[k]===undefined?null:st[k]); }); snap.estado=estadoCompra(self,m,id).t;
  const js=JSON.stringify(snap); const memo=self._procJs||(self._procJs={}); if(memo[id]===js) return; memo[id]=js;
  try{ const o=JSON.parse(localStorage.getItem(SOL_KEY)||'null')||{v:1,sols:{}}; o.proc=o.proc||{}; o.proc[id]=snap;
    const r=o.sols&&o.sols[id]; if(r&&r.id===snap.sol&&snap.estado!=='A cotar') r.estado=snap.estado;
    localStorage.setItem(SOL_KEY,JSON.stringify(o)); }catch(e){} }
function trocaSafra(self,id,extra){ const st=self.state; const patch={saf:id,conf5:false};
  if(st.saf!==id){ const bag=Object.assign({},st.porSaf||{}); if(st.saf){ const cur={}; PROC.forEach(k=>{ cur[k]=st[k]; }); bag[st.saf]=cur; }
    const nx=bag[id]||procLer(id)||{}; PROC.forEach(k=>{ patch[k]=(nx[k]===undefined?null:nx[k]); }); if(!patch.nresp) patch.nresp=0; patch.porSaf=bag; }
  self.setState(Object.assign(patch,extra||{}));
  if(patch.env&&(patch.nresp||0)<patch.env.ordem.length) tickResp(self); }   // respostas que ainda faltavam continuam chegando
function hashSync(id,x){ try{ const h=x?('#sol='+encodeURIComponent(x.sol.id)+'&saf='+encodeURIComponent(id)):''; if(decodeURIComponent(location.hash||'')!==decodeURIComponent(h)) history.replaceState(null,'',location.pathname+location.search+h); }catch(e){} }
function grupos(){ return [...new Set((SX?SX.itens:[]).map(x=>x.grupo))].sort(pt); }
function pcIds(pcs){ return !pcs||!pcs.length?'—':(pcs.length===1?pcs[0].id:pcs[0].id+' a '+pcs[pcs.length-1].id); }
function T(t){ return {k:'txt',t:t}; } function B(t){ return {k:'b',t:t}; } function MU(t){ return {k:'mut',t:t}; } function CH(t,c){ return {k:'chip',t:t,c:c}; }
function LK(t,h){ return {k:'link',t:t,h:h}; } function BR(){ return {k:'br',t:''}; }
function fretep(p,it){ return p.frete==='FOB'?[T('FOB'),MU('+'+rs(p.fr*it.ped)+' est.')]:[T('CIF')]; }
function aprOf(st){ return (st.aprov&&st.aprov.estado==='aprovada')?st.aprov:null; }
function dm(iso){ return iso?iso.slice(8,10)+'/'+iso.slice(5,7):'—'; }
// falta a partir de (CAL-01): 1ª data em que a projeção do insumo falta para esta solicitação — estoque apto com reservas, outras origens
// e pedidos em aberto na data prevista (a previsão reprogramada na etapa 6 vale; excl = pedido a desconsiderar; pedidos novos desta solicitação nunca entram)
function faltaDe(st,nome,excl){ const d=(SX?SX.dem:[]).find(x=>x.nome===nome); if(!d||!d.evs) return null; const px=st.pcx||{};
  const evs=d.evs.filter(e=>!(e.tipo==='rec'&&e.ref&&e.ref===excl)).map(e=>(e.tipo==='rec'&&e.ref&&px[e.ref]&&px[e.ref].prev)?Object.assign({},e,{dt:px[e.ref].prev}):e);
  return cal01(d.est,evs,0,OPT).falta; }
// respostas simuladas chegando uma a uma (um único relógio por tela)
function tickResp(self){ if(self._tk) return; self._tk=true;
  const tick=()=>{ const s=self.state; if(!s.env){ self._tk=false; return; } const n=(s.nresp||0)+1; if(n>s.env.ordem.length){ self._tk=false; return; } const done=(n===s.env.ordem.length);
    self.setState(Object.assign({nresp:n},done?{g2toast:'Respostas simuladas: '+n+' propostas recebidas de '+s.env.n+' convites.'}:{})); if(done) self._tk=false; else setTimeout(tick,320); };
  setTimeout(tick,700); }
// grava a edição da linha no estado do processo e devolve a grade às linhas calculadas
function keep(self,gid,rid,patch){ const all=Object.assign({},self.state.g2||{}); all[gid]=Object.assign({},all[gid]||{},{rows:undefined,fm:null,fl:rid}); patch.g2=all; self.setState(patch); }
function tog(self,gid,rid){ const sp=GR(gid); const x=Object.assign({},g2st(self,gid).x||sp.x0||{}); x[rid]=!x[rid]; g2set(self,gid,{x}); }
// ---------- modelo do processo (SOL-2026-07) ----------
function M(self){ sx(self);
  const st=self.state; const G=grupos(); const conv={}; const env=st.env||null; const nresp=st.nresp||0; const apr0=aprOf(st);
  G.forEach((g,gi)=>{ CD.forn.filter(f=>f.grupos.indexOf(g)>=0).forEach(f=>{ const rid='C_'+gi+'_'+f.id; const s=(st.conv||{})[rid]||{};
    const enviado=!!(env&&env.conv.indexOf(rid)>=0); const cn=f.canais||['E-mail'];
    // depois do envio, quem não recebeu convite só entra se for marcado de novo (convite adicional)
    conv[rid]={rid,g,gi,f,homol:!!f.homologado,conv:f.homologado?(s.conv||(env&&!enviado?'Não convidar':'Convidar')):'—',
      canal:(s.canal&&cn.indexOf(s.canal)>=0)?s.canal:cn[0],prazo:s.prazo||CD.prazoPadrao,enviado,temProp:(CD.props[g]||[]).some(p=>p.f===f.id)}; }); });
  const got={}; if(env) env.ordem.slice(0,nresp).forEach((k,ix)=>{ got[k]=env.horas[ix]; });
  const items=(SX?SX.itens:[]).map(it=>{ const gi=G.indexOf(it.grupo); const s=(st.esc||{})['I_'+it.i]||{}; const ped=(s.ped!==undefined&&s.ped!==''&&!isNaN(Number(s.ped)))?Number(s.ped):it.nec;
    const falta=faltaDe(st,it.nome,null);
    const props=(CD.props[it.grupo]||[]).filter(p=>got['C_'+gi+'_'+p.f]).map(p=>{ const preco=Math.round(it.preco*p.fator*100)/100; const fr=(p.frete==='FOB')?(CD.fob[it.un]||0):0;
      const chega=addd(CD.hojeIso,p.prazo);
      return {f:p.f,nome:fnome(p.f),preco,prazo:p.prazo,frete:p.frete,pag:p.pag,validade:p.validade,fr,unit:preco+fr,hora:got['C_'+gi+'_'+p.f],chega,late:!!(falta&&chega>falta),
        label:fnome(p.f)+' · '+rs(preco)+'/'+it.un+' · '+p.prazo+' dias · '+p.frete}; }).sort((a,b)=>a.unit-b.unit);
    const low=props.length?props[0]:null;                 // menor custo total (selo)
    const ref=props.find(p=>!p.late)||low;                // menor custo entre as que chegam a tempo: escolha padrão e referência da justificativa
    let ch=s.f?(props.find(p=>p.f===s.f)||null):null; if(!ch) ch=ref;
    const naoMenor=!!(ch&&(ch.late||(ref&&ch.f!==ref.f&&ch.unit>ref.unit+1e-9))); const just=String(s.just||'');
    return Object.assign({},it,{gi,rid:'I_'+it.i,ped,props,low,ref,ch,falta,naoMenor,just,justPend:naoMenor&&!just.trim(),tot:ch?ped*ch.unit:0}); });
  const byF={}; items.forEach(it=>{ if(!it.ch||!(it.ped>0)) return; (byF[it.ch.f]||(byF[it.ch.f]=[])).push(it); });
  const pcs=CD.forn.filter(f=>byF[f.id]).map((f,ix)=>{ const its=byF[f.id];
    return {id:'PC-'+(SX.pcIni+ix),f:f.id,nome:f.nome,itens:its,valor:its.reduce((a,x)=>a+x.tot,0),prazo:Math.max.apply(null,its.map(x=>x.ch.prazo)),pag:its[0].ch.pag}; });
  const total=pcs.reduce((a,p)=>a+p.valor,0);
  let ni=CD.alcada.findIndex(a=>a.ate===null||total<=a.ate+1e-9); if(ni<0) ni=CD.alcada.length-1;
  const sig=JSON.stringify(items.map(it=>[it.i,it.ch?it.ch.f:'',Math.round(it.ped*1000)/1000]));
  const invited=Object.values(conv).filter(c=>c.conv==='Convidar');
  const nadic=(env&&!apr0)?Object.values(conv).filter(c=>c.homol&&!c.enviado&&c.conv==='Convidar').length:0;
  const semForn=G.filter(g=>!Object.values(conv).some(c=>c.g===g&&c.homol));
  return {G,conv,env,nresp,got,items,pcs,total,ni,quem:CD.alcada[ni].quem,podeAna:ni<=CD.perfil.idx,sig,nconv:invited.length,nadic,semForn,
    njust:items.filter(x=>x.justPend).length,semProp:items.filter(x=>!x.ch).length,excl:items.filter(x=>x.ch&&!(x.ped>0)).length,
    nlate:items.filter(x=>x.ch&&x.ch.late&&x.ped>0).length,esperadas:env?env.ordem.length:0,ref:SX?SX.ref:0};
}
function estadoCompra(self,m,id){ const st=self.state; const b=(id&&id!==st.saf)?((st.porSaf||{})[id]||procLer(id)||{}):null; const a=b?b.aprov:st.aprov;
  if(b){ m={env:b.env||null,nresp:b.nresp||0,sig:a?a.sig:''}; }
  if(a&&a.estado==='aprovada') return CH('Pedidos emitidos · '+pcIds(a.pcs),'green');
  if(a&&a.estado==='pendente') return a.sig===m.sig?CH('Aguardando '+a.quem,'yellow'):CH('Aprovação desatualizada · reenviar','red');
  if(a&&a.estado==='devolvida') return CH('Devolvida pela '+a.quem+' · ajustar','red');
  if(a&&a.estado==='recusada') return CH('Recusada · não contratado','red');
  if(m.env) return CH('Em cotação · '+m.nresp+' de '+m.env.n+' respostas','blue');
  return CH('A cotar','gray'); }
function sitDem(self,m,d,fa){ const apr=aprOf(self.state);
  if(d.liq<=0.001) return [CH('Coberto','green')].concat(d.quar?[MU(nf(d.quar)+' '+d.un+' em quarentena não contam')]:[]).concat(fa?[MU('pedido em aberto chega depois da falta')]:[]);
  const it=m.items.find(x=>x.nome===d.nome); if(!it) return [MU('—')];
  if(apr){ let pc=null, pi=null; apr.pcs.forEach(p=>p.itens.forEach(x=>{ if(x.nome===d.nome){ pc=p; pi=x; } }));
    if(!pc) return [CH('Fora dos pedidos','red')];
    return pi.ped<pi.nec-1e-9?[CH('Parcial · '+pc.id,'yellow'),MU(qt(pi.ped,pi.un)+' de '+qt(pi.nec,pi.un))]:[CH('Pedido '+pc.id,'green')]; }
  const a=self.state.aprov; if(a&&a.estado==='pendente') return [CH('Aguardando aprovação','yellow')];
  if(a&&a.estado==='recusada') return [CH('Não contratado','red'),MU('recusado pela '+a.quem+' · necessidade aberta')];
  if(a&&a.estado==='devolvida') return [CH('Devolvida para ajuste','yellow')];
  if(m.env) return [CH('Em cotação','blue'),MU(it.props.length+(it.props.length===1?' proposta':' propostas'))];
  return [CH('A cotar','gray')]; }
function PREVALS(self,v){
  const st=self.state; const saf=st.saf||null; sx(self); const m=M(self); self._m=m; const apr=aprOf(st);
  // ---- etapa 1 · safras ----
  GR('g_saf').rows=safras().map(s=>{ const on=(saf===s.id); const r={id:s.id,ro:true,v:{nome:s.nome},s:{nome:s.nome},p:{}};
    r.p.nome=[B(s.nome),MU(s.periodo)].concat(on?[CH('Selecionada','blue')]:[]);
    const x=solDe(s.id);
    if(x){ r.p.sol=[B(x.sol.id),MU(x.itens.length+' insumos · '+rs(x.ref)+(x.comp?' · '+x.comp+(x.comp>1?' complementos':' complemento'):'')),BR(),MU('enviada '+x.sol.enviada+' por '+x.sol.por)]; r.s.sol=x.sol.id;
      r.p.orig=[T('Planejar safra · demanda de insumos'),LK('Ver origem',x.origem.h)]; r.s.orig='Planejar safra';
      const e=estadoCompra(self,m,s.id); r.p.comp=[e]; r.s.comp=e.t; r.p.acao=[{k:'act',t:'Abrir compra',fn:'pick:'+s.id}]; }
    else if(s.id==='S2526'){ r.p.sol=[B(CD.sol2526),MU('concluída')]; r.s.sol=CD.sol2526; r.p.orig=[T('Planejar safra · 2025/26')]; r.s.orig='Planejar safra';
      r.p.comp=[CH('Encerrada · '+CD.ped2526.length+' pedidos entregues','gray')]; r.s.comp='Encerrada'; r.p.acao=[{k:'act',t:'Consultar pedidos',fn:'pick:'+s.id}]; }
    else { r.p.sol=[CH('Sem solicitação','yellow'),BR(),MU('Solicitação ainda não enviada pelo planejamento')]; r.s.sol='não enviada'; r.p.orig=[LK('Abrir Planejar safra',safHref(s.id))]; r.s.orig='';
      r.p.comp=[MU('—')]; r.s.comp=''; r.p.acao=[MU('—')]; }
    r.s.acao=''; return r; });
  // ---- etapa 6 · pedidos (também em consulta para a safra encerrada) ----
  const ent=[]; const pcx=st.pcx||{};
  if(SX){
    // aviso (sem bloquear) quando a previsão fica depois da data em que o item falta sem este pedido
    const avFalta=(x,prev0,falt)=>{ if(!falt) return []; if(x.prev&&x.prev>falt) return [CH('Nova data depois da falta de '+dm(falt),'red')];
      if(!x.prev&&prev0>falt) return [CH('Chega depois da falta ('+dm(falt)+')','red')]; return []; };
    (apr?apr.pcs:[]).forEach(p=>{ const x=pcx[p.id]||{}; const prev=x.prev||p.prev; const one=p.itens.length===1;
      const falt=p.itens.map(it=>faltaDe(st,it.nome,null)).filter(Boolean).sort()[0]||null; const av=avFalta(x,p.prev,falt);
      const r={id:p.id,v:{nome:p.id,val:p.valor,prev,obs:x.obs||''},s:{nome:p.id+' '+p.nome},p:{nome:[B(p.id),T(p.nome),BR(),MU(SX.sol.id+' · '+(one?p.itens[0].nome:p.itens.length+' insumos'))]}};
      if(one){ const it=p.itens[0]; Object.assign(r.v,{qtd:it.ped,rec:0,quar:0,ae:it.ped}); r.p.qtd=[T(qt(it.ped,it.un))]; r.p.rec=[MU('—')]; r.p.quar=[MU('—')]; r.p.ae=[B(qt(it.ped,it.un))]; }
      else r.kids=p.itens.map(it=>({id:p.id+'_'+it.i,ro:true,dr:'entp_'+p.id,v:{nome:it.nome,qtd:it.ped,rec:0,quar:0,ae:it.ped,val:it.tot},s:{nome:it.nome},
        p:{qtd:[T(qt(it.ped,it.un))],rec:[MU('—')],quar:[MU('—')],ae:[B(qt(it.ped,it.un))],prev:[T('')],sit:[T('')],acao:[T('')]}}));
      r.p.sit=[x.conf?CH('Confirmado pelo fornecedor','green'):CH('Aguarda confirmação','blue')].concat(av); r.s.sit=(x.conf?'Confirmado':'Emitido')+(av.length?' '+av[0].t:'');
      r.p.acao=x.conf?[LK('Conferir no Estoque','EST.dc.html')]:[{k:'act',t:'Confirmar fornecedor',fn:'pcconf:'+p.id}]; r.s.acao='';
      ent.push(r); });
    CD.pedidos.filter(p=>SX.safra==='S2627'||SX.dem.some(d=>d.nome===p.item)).forEach(p=>{ const x=pcx[p.id]||{}; const t=(n)=>qt(n,p.un);
      const r={id:p.id,v:{nome:p.id,qtd:p.qtd,rec:p.rec,quar:p.quar,ae:p.ae,val:p.qtd*p.preco,prev:x.prev||p.prev,obs:x.obs||''},s:{nome:p.id+' '+p.forn+' '+p.item},
        p:{nome:[B(p.id),T(p.forn),BR(),MU(p.item+' · anterior à '+SX.sol.id)],qtd:[T(t(p.qtd))],rec:p.rec?[T(t(p.rec)),MU(nf(p.apto)+' aptos'+(p.quar?' · '+nf(p.quar)+' em quarentena':''))]:[MU('—')],ae:[B(t(p.ae))]}};
      const av=avFalta(x,p.prev,faltaDe(st,p.item,p.id));
      if(p.estado==='Parcial'){ r.p.sit=[CH('Parcial','yellow')].concat(av).concat([MU(nf(p.rec/1000)+' de '+nf(p.qtd/1000)+' t recebidas · '+nf(p.quar/1000)+' t em quarentena só contam se o laudo aprovar · '+nf(p.ae/1000)+' t a entregar')]); r.p.acao=[LK('Conferir recebimentos','EST.dc.html')]; }
      else { r.p.sit=[CH('Confirmado','green')].concat(av).concat([MU(p.nfprev?(p.nfprev+' prevista para 24/09'):'aguarda embarque')]); r.p.acao=p.nfprev?[LK('Conferir '+p.nfprev,'EST.dc.html')]:[MU('—')]; }
      r.s.sit=p.estado+(av.length?' '+av[0].t:''); r.s.acao=''; ent.push(r); });
  } else if(saf==='S2526'){
    CD.ped2526.forEach(p=>{ ent.push({id:p.id,ro:true,v:{nome:p.id,qtd:p.qtd,rec:p.qtd,quar:0,ae:0,val:p.qtd*p.preco,prev:p.prev},s:{nome:p.id+' '+p.forn+' '+p.item,sit:'Entregue'},
      p:{nome:[B(p.id),T(p.forn),BR(),MU(p.item+' · '+CD.sol2526)],qtd:[T(qt(p.qtd,p.un))],rec:[T(qt(p.qtd,p.un))],quar:[MU('—')],ae:[MU('—')],sit:[CH('Entregue · conciliado','gray')],acao:[MU('—')]}}); }); }
  GR('g_ent').rows=ent; GR('g_ent').x0={}; (apr?apr.pcs:[]).forEach(p=>{ GR('g_ent').x0[p.id]=true; });
  if(!SX){ ['g_dem','g_conv','g_cmp','g_apr'].forEach(g=>{ GR(g).rows=[]; }); return; }
  // ---- etapa 2 · demanda (mesmas linhas e números do Planejar safra) ----
  const byG={}; SX.dem.forEach(d=>{ (byG[d.grupo]||(byG[d.grupo]=[])).push(d); });
  GR('g_dem').rows=Object.keys(byG).sort(pt).map((g,gi)=>{ const its=byG[g].slice().sort((a,b)=>pt(a.nome,b.nome)); const val=its.reduce((a,d)=>a+d.valor,0);
    const fas=its.map(d=>faltaDe(st,d.nome,null)); const fg=fas.filter(Boolean).sort()[0]||'';
    return {id:'DG'+gi,v:{ins:g,valor:val,falta:fg},s:{ins:g},p:{ins:[B(g),MU(its.length+(its.length>1?' insumos':' insumo'))],falta:fg?[MU(brd(fg))]:[MU('')]},
      kids:its.map((d,ix)=>{ const dc=d.un==='L'?1:0; const fa=fas[ix]; const sit=sitDem(self,m,d,fa); const c=calDe(d);
        return {id:'DG'+gi+'_'+ix,ro:true,v:{ins:d.nome,bruta:d.bruta,est:d.est,rec:d.rec,liq:d.liq,un:d.un,falta:fa||'',preco:d.preco,valor:d.valor},s:{sit:sit.map(x=>x.t).join(' ')},
          p:{bruta:[T(nf(d.bruta,dc))].concat(c.real>0.001?[BR(),MU('realizado: '+nf(c.real,dc))]:[]),est:[T(nf(d.est,dc))].concat((d.liq>0.001&&c.antes>0.001)?[BR(),MU('usado antes: '+nf(c.antes,dc))]:(d.res?[BR(),MU('res. '+nf(d.res,dc))]:[])),
             rec:[T(nf(d.rec,dc))].concat(d.liq>0.001&&c.tarde>0.001?[BR(),MU(nf(c.tarde,dc)+' após a falta')]:[]),
             liq:[B(nf(d.liq,dc))],falta:fa?[(d.liq>0.001?B(brd(fa)):CH(brd(fa),'red'))]:[MU('—')],sit},
          o:cal01Memo(c,{un:d.un,res:d.res,quar:d.quar}).map(t=>({t})).concat([{t:'Ver no Planejar safra · demanda de insumos',h:SX.origem.h}])}; })}; });
  GR('g_dem').x0=Object.fromEntries(GR('g_dem').rows.map(r=>[r.id,true]));
  // ---- etapa 3 · convites ----
  GR('g_conv').rows=m.G.map((g,gi)=>{ const cs=Object.values(m.conv).filter(c=>c.gi===gi); const its=m.items.filter(x=>x.gi===gi);
    const inv=m.env?cs.filter(c=>c.enviado):cs.filter(c=>c.conv==='Convidar'); const nr=inv.filter(c=>m.got[c.rid]).length; const ref=its.reduce((a,x)=>a+x.nec*x.preco,0);
    const npd=m.env?cs.filter(c=>c.homol&&!c.enviado&&c.conv==='Convidar').length:0;
    v['cgt_'+gi]=()=>tog(self,'g_conv','CG'+gi);
    return {id:'CG'+gi,dr:'cgt_'+gi,v:{nome:g},s:{nome:g,homol:'',conv:String(inv.length),resp:''},
      p:{nome:[B(g),MU(its.length+(its.length>1?' insumos':' insumo'))],homol:m.semForn.indexOf(g)>=0?[CH('Sem fornecedor homologado','yellow'),BR(),LK('Cadastrar em Parceiros e fornecedores','CD-05.dc.html')]
           :[MU(cs.filter(c=>c.homol).length+' homologados de '+cs.length)],
         conv:[T(inv.length+(inv.length===1?' convidado':' convidados'))].concat(npd?[MU('+'+npd+' a enviar')]:[]),resp:m.env?(inv.length?[CH(nr+' de '+inv.length+' propostas',nr===inv.length?'green':'yellow')]:[MU('Sem cotação')]):[MU('—')]},
      kids:cs.map(c=>{ const f=c.f; const r={id:c.rid,v:{nome:f.nome,conv:c.conv,canal:c.canal,prazo:c.prazo},s:{nome:f.nome},p:{nome:[B(f.nome)]}};
        if(!c.homol){ r.dr='cnh_'+c.rid; v[r.dr]=()=>toast(self,f.nome+' não é homologado para '+g+': '+f.motivo.toLowerCase()+'. Homologue em Cadastros › Parceiros e fornecedores para poder convidar.');
          r.p.homol=[CH('Não homologado','red'),MU(f.motivo),BR(),LK('Homologar em Parceiros e fornecedores','CD-05.dc.html')]; r.s.homol='Não homologado';
          r.p.conv=[MU('Indisponível')]; r.p.canal=[MU('—')]; r.p.prazo=[MU('—')]; r.p.resp=[MU('—')]; return r; }
        r.p.homol=[CH('Homologado','green')]; r.s.homol='Homologado';
        const on=c.enviado||c.conv==='Convidar'; const dest=c.canal==='WhatsApp'?f.whats:f.email;
        r.p.conv=on?[B('Convidar')]:[MU('Não convidar')]; r.p.canal=on?[T(c.canal),MU(dest)]:[MU('—')]; r.s.canal=c.canal+' '+dest; r.p.prazo=[on?T(c.prazo):MU('—')];
        if(m.env){ const h=m.got[c.rid]; const fim=m.nresp>=m.esperadas;
          if(c.enviado){ const em=((m.env.emx||{})[c.rid])||m.env.em;
            r.p.resp=h?[CH('Proposta recebida','green'),MU(h.slice(6))]:(fim?[CH('Sem resposta até agora','yellow'),MU('prazo '+c.prazo)]:[CH('Aguardando resposta','yellow'),MU('até '+c.prazo)]);
            r.dr='cenv_'+c.rid; v[r.dr]=()=>toast(self,'Convite simulado enviado a '+f.nome+' por '+c.canal+' em '+em+' · responder até '+c.prazo+(h?' · proposta recebida '+h:'')+'. Nenhuma mensagem real foi enviada.'); }
          else if(apr){ r.p.resp=[MU('Não convidado')]; r.dr='cenv_'+c.rid; v[r.dr]=()=>toast(self,f.nome+' não foi convidado nesta cotação.'); }
          else r.p.resp=(c.conv==='Convidar')?[CH('Convite adicional a enviar','blue')]:[MU('Não convidado')]; }   // antes da aprovação: a linha abre o formulário Convite
        else r.p.resp=[MU(on?'Envio pendente':'—')];
        r.s.resp=((r.p.resp||[])[0]||{}).t||'';   // filtro rápido por resposta
        return r; })}; });
  // formulário Convite: só os canais autorizados no cadastro do fornecedor
  const fm3=g2st(self,'g_conv').fm; const FC=GR('g_conv').edit.fields;
  if(fm3&&fm3.rid&&m.conv[fm3.rid]){ const c=m.conv[fm3.rid]; const cn=c.f.canais||['E-mail']; FC[1].opts=cn.slice();
    FC[1].help=cn.length>1?('Canais autorizados no cadastro de '+c.f.nome+'.'):('Só '+cn[0]+': é o único canal autorizado no cadastro de '+c.f.nome+' (Parceiros e fornecedores).'); }
  GR('g_conv').x0=Object.fromEntries(m.G.map((g,gi)=>['CG'+gi,true]));
  // ---- etapa 4 · comparação ----
  const spc=GR('g_cmp'); const fm4=g2st(self,'g_cmp').fm;
  if(fm4&&fm4.rid){ const it=m.items.find(x=>x.rid===fm4.rid); if(it){ const FF=spc.edit.fields; FF[0].opts=it.props.map(p=>p.label);
    FF[0].help=it.falta?('Falta a partir de '+brd(it.falta)+': proposta que chega depois exige justificativa.'):'';
    FF[1].max=Math.round(it.nec*100)/100; FF[1].u=it.un; FF[1].help='Necessidade na '+SX.sol.id+': '+qt(it.nec,it.un)+'. Use 0 para não comprar agora.';
    const p=it.props.find(x=>x.label===fm4.draft.venc); FF[2].req=!!(p&&(p.late||(it.ref&&p.f!==it.ref.f&&p.unit>it.ref.unit+1e-9)));
    FF[2].help=FF[2].req?(p.late?('Obrigatória: '+p.nome+' chega em '+brd(p.chega)+', depois da falta de '+brd(it.falta)+'.'):('Obrigatória: a proposta escolhida não é a de menor custo que chega a tempo ('+it.ref.nome+').'))
      :'Opcional quando a escolha é a de menor custo que chega a tempo.'; } }
  spc.rows=m.env?m.G.map((g,gi)=>{ const its=m.items.filter(x=>x.gi===gi); const tot=its.reduce((a,x)=>a+x.tot,0); const fs=new Set(); its.forEach(x=>x.props.forEach(p=>fs.add(p.f)));
    const wins={}; its.forEach(x=>{ if(x.ch) wins[x.ch.nome]=(wins[x.ch.nome]||0)+1; });
    v['kgt_'+gi]=()=>tog(self,'g_cmp','KG'+gi);
    return {id:'KG'+gi,dr:'kgt_'+gi,v:{nome:g,tot},s:{nome:g,venc:''},p:{nome:[B(g),MU(fs.size+(fs.size===1?' fornecedor':' fornecedores'))],
        venc:[MU(Object.keys(wins).map(k=>k+' em '+wins[k]+' de '+its.length).join(' · ')||'sem propostas ainda')]},
      kids:its.map(it=>{ const c=it.ch; const r={id:it.rid,v:{nome:it.nome,ped:it.ped,preco:c?c.preco:'',prazo:c?c.prazo:'',tot:it.tot,venc:c?c.label:'',just:it.just},s:{nome:it.nome},
          p:{nome:[B(it.nome)].concat(it.falta?[BR(),MU('falta a partir de '+dm(it.falta))]:[])}};
        r.p.ped=[B(qt(it.ped,it.un))].concat(it.ped<it.nec-1e-9?[MU('de '+qt(it.nec,it.un))]:[]);
        const tarde=(p)=>p.late?[CH('Chega depois da falta ('+dm(it.falta)+')','red')]:[];
        if(c){ r.p.frete=fretep(c,it); r.p.pag=[T(c.pag)]; r.p.val=[T(c.validade.slice(0,5))]; r.p.prazo=[T(c.prazo+' dias'),BR(),MU('chega '+dm(c.chega))];
          r.p.venc=[B(c.nome)].concat(it.naoMenor?(it.justPend?[CH('Justificativa pendente','red')]:[CH('Justificada','yellow')])
            :(it.low&&c.f===it.low.f?[CH('Menor custo total','green')]:[CH('Menor custo a tempo','green')])).concat(tarde(c));
          r.s.frete=c.frete; r.s.pag=c.pag; r.s.val=c.validade; r.s.venc=c.nome; }
        else { r.p.venc=[CH('Sem proposta ainda','gray')]; r.s.venc='Sem proposta'; r.dr='knp_'+it.i;
          const livres=Object.values(m.conv).filter(x=>x.gi===it.gi&&x.homol&&!x.enviado);
          v[r.dr]=()=>toast(self,m.semForn.indexOf(it.grupo)>=0?('Sem fornecedor homologado em '+it.grupo+': '+it.nome+' fica sem cotação. Cadastre e homologue em Parceiros e fornecedores e convide na etapa 3.')
            :'Nenhuma proposta recebida para '+it.nome+' ainda. '+(livres.length
            ?('Aguarde as respostas ou, na etapa 3 (Solicite cotações), marque '+livres.map(x=>x.f.nome).join(' ou ')+' e use Enviar convites adicionais.')
            :('Todos os homologados de '+it.grupo+' já foram convidados: aguarde as respostas ou homologue outro fornecedor em Parceiros e fornecedores.'))); }
        if(apr){ r.dr='kap_'+it.i; v[r.dr]=()=>toast(self,'Compra aprovada: a escolha de '+it.nome+' está nos pedidos emitidos. Para mudar, cancele o pedido e cote de novo.'); }
        r.kids=it.props.map(p=>{ const k={id:'P_'+it.i+'_'+p.f,ro:true,dr:'kp_'+it.i+'_'+p.f,v:{nome:p.nome,preco:p.preco,prazo:p.prazo,tot:it.ped*p.unit},s:{nome:p.nome,frete:p.frete,pag:p.pag,val:p.validade},
            p:{nome:[T(p.nome),MU(p.hora.slice(6))],prazo:[T(p.prazo+' dias'),BR(),MU('chega '+dm(p.chega))],frete:fretep(p,it),pag:[T(p.pag)],val:[T(p.validade.slice(0,5))],
               venc:(it.low&&p.f===it.low.f?[CH('Menor custo total','green')]:[]).concat(c&&p.f===c.f?[CH('Escolhida','blue')]:[]).concat(tarde(p))}};
          k.s.venc=k.p.venc.map(x=>x.t).join(' ');
          v[k.dr]=apr?(()=>toast(self,'Compra aprovada: propostas em consulta.')):(()=>openEsc(self,it.rid,p.f)); return k; });
        return r; })}; }):[];
  spc.x0=Object.fromEntries(m.G.map((g,gi)=>['KG'+gi,true])); const big=m.items.slice().sort((a,b)=>b.nec*b.preco-a.nec*a.preco)[0]; if(big) spc.x0[big.rid]=true;
  // ---- etapa 5 · pedidos a gerar / emitidos ----
  const pcs=apr?apr.pcs:m.pcs;
  GR('g_apr').rows=(m.env&&m.nresp)?pcs.map(p=>({id:'A_'+p.id,v:{nome:p.id,prazo:p.prazo,pag:p.pag,tot:p.valor},s:{nome:p.id+' · '+p.nome},
      p:{nome:[B(p.id+(apr?'':' (prévia)')),MU(p.nome)],prazo:[T('até '+p.prazo)]},
      o:[{t:'Fornecedor '+p.nome+' · homologado'},{t:SX.nome+' · '+SX.sol.id+' · '+p.itens.length+(p.itens.length>1?' insumos':' insumo')},{t:'Propostas recebidas em 23/09/2026 (simuladas)'}],
      kids:p.itens.map(it=>({id:'A_'+p.id+'_'+it.i,ro:true,v:{nome:it.nome,qtd:it.ped,preco:it.ch.preco,prazo:it.ch.prazo,tot:it.tot},s:{nome:it.nome,frete:it.ch.frete,pag:it.ch.pag},
        p:{qtd:[T(qt(it.ped,it.un))].concat(it.ped<it.nec-1e-9?[MU('de '+qt(it.nec,it.un))]:[]),frete:[T(it.ch.frete)],pag:[T(it.ch.pag)]},
        o:[{t:'Necessidade na '+SX.sol.id+': '+qt(it.nec,it.un)},{t:'Proposta '+it.ch.nome+' · '+rs(it.ch.preco)+'/'+it.un+' · '+it.ch.frete+' · válida até '+it.ch.validade},
           {t:it.naoMenor?('Escolha justificada: '+it.just):((it.low&&it.ch.f===it.low.f)?'Escolha: menor custo total':('Escolha: menor custo que chega a tempo'+(it.low?' ('+it.low.nome+' custa menos, mas chega depois da falta)':'')))},
           {t:'Chega '+brd(it.ch.chega)+(it.falta?' · falta a partir de '+brd(it.falta):' · sem falta prevista')},{t:'Ver origem da demanda no Planejar safra',h:SX.origem.h}]}))})):[];
  GR('g_apr').x0=Object.fromEntries(pcs.map(p=>['A_'+p.id,true]));
}
function openEsc(self,rid,f){ const m=M(self); const it=m.items.find(x=>x.rid===rid); if(!it) return;
  const p=f?it.props.find(x=>x.f===f):null; const base={venc:it.ch?it.ch.label:'',ped:String(it.ped).replace('.',','),just:it.just||''}; const draft=Object.assign({},base); if(p) draft.venc=p.label;
  g2set(self,'g_cmp',{fm:{rid,draft,orig:Object.assign({},base),errs:{},warn:false,ro:false,isNew:false,mode:'form'},fl:null,fmc:null}); }
function pick(self,id){ const s=safras().find(x=>x.id===id); if(!s) return; const x=solDe(id);
  if(x) trocaSafra(self,id,{step:2,g2toast:'Compra aberta: '+s.nome+' · '+x.sol.id+'.'});
  else if(id==='S2526') trocaSafra(self,id,{step:6,g2toast:s.nome+' encerrada: pedidos em consulta.'});
  else trocaSafra(self,id,{step:1,g2toast:s.nome+': solicitação ainda não enviada pelo planejamento.'});
  hashSync(id,x); }
function enviar(self){ const st=self.state; if(st.env){ toast(self,'Convites já enviados em '+st.env.em+' · nenhum convite duplicado.'); return; }
  const m=M(self); const sem=m.G.filter(g=>m.semForn.indexOf(g)<0&&!Object.values(m.conv).some(c=>c.g===g&&c.conv==='Convidar'));
  if(sem.length){ toast(self,'Convide ao menos um fornecedor homologado em: '+sem.join(', ')+'.'); return; }
  const inv=Object.values(m.conv).filter(c=>c.conv==='Convidar');
  if(!inv.length){ toast(self,'Nenhum grupo tem fornecedor homologado: cadastre em Parceiros e fornecedores para cotar.'); return; }
  const fora=m.semForn.length?(' Sem cotação (sem fornecedor homologado): '+m.semForn.join(', ')+'.'):'';
  const fila=m.G.map(g=>inv.filter(c=>c.g===g&&c.temProp).map(c=>c.rid)); const ordem=[];
  for(let k=0;fila.some(l=>l.length);k++){ fila.forEach(l=>{ if(l.length) ordem.push(l.shift()); }); }
  const horas=ordem.map((x,ix)=>{ const mm=10*60+52+ix*9; return '23/09 '+String(Math.floor(mm/60)).padStart(2,'0')+':'+String(mm%60).padStart(2,'0'); });
  self.setState({env:{em:'23/09/2026 10:47',n:inv.length,conv:inv.map(c=>c.rid),ordem,horas},nresp:0,
    g2toast:'Convites simulados: nenhuma mensagem real foi enviada · '+inv.length+' convites em '+(m.G.length-m.semForn.length)+' grupos. Acompanhe as respostas chegando.'+fora});
  tickResp(self); }
// convites adicionais depois do envio (antes da compra aprovada): só os novos; quem já recebeu não recebe de novo
function enviarAdic(self){ const st=self.state; const env=st.env; if(!env) return;
  if(aprOf(st)){ toast(self,'Compra aprovada: não há convite adicional. Para cotar de novo, cancele o pedido.'); return; }
  const m=M(self); const novos=Object.values(m.conv).filter(c=>c.homol&&!c.enviado&&c.conv==='Convidar');
  if(!novos.length){ toast(self,'Nenhum convite adicional marcado: clique num fornecedor homologado ainda não convidado.'); return; }
  const fila=m.G.map(g=>novos.filter(c=>c.g===g&&c.temProp).map(c=>c.rid)); const add=[];
  while(fila.some(l=>l.length)) fila.forEach(l=>{ if(l.length) add.push(l.shift()); });
  const hm=(t)=>{ const x=/(\d{2}):(\d{2})$/.exec(String(t||'')); return x?Number(x[1])*60+Number(x[2]):10*60+47; };
  const f2=(mm)=>String(Math.floor(mm/60)).padStart(2,'0')+':'+String(mm%60).padStart(2,'0');
  const base=Math.max(hm(env.horas[env.horas.length-1]),hm(env.em))+6; const em='23/09/2026 '+f2(base);
  const emx=Object.assign({},env.emx||{}); novos.forEach(c=>{ emx[c.rid]=em; });
  self.setState({env:Object.assign({},env,{n:env.n+novos.length,conv:env.conv.concat(novos.map(c=>c.rid)),ordem:env.ordem.concat(add),
      horas:env.horas.concat(add.map((x,ix)=>'23/09 '+f2(base+5+ix*9))),emx,adic:(env.adic||0)+novos.length}),
    g2toast:'Convites adicionais simulados: nenhuma mensagem real foi enviada · '+novos.length+' para '+[...new Set(novos.map(c=>c.f.nome))].join(', ')+'. Quem já recebeu não recebe de novo.'});
  tickResp(self); }
function emitir(self,m,por){ const pcs=JSON.parse(JSON.stringify(m.pcs.map(p=>({id:p.id,f:p.f,nome:p.nome,valor:p.valor,prazo:p.prazo,pag:p.pag,prev:addd(CD.hojeIso,p.prazo),
    itens:p.itens.map(it=>({i:it.i,nome:it.nome,grupo:it.grupo,un:it.un,nec:it.nec,ped:it.ped,tot:it.tot,naoMenor:it.naoMenor,just:it.just,ch:it.ch,low:it.low,falta:it.falta}))}))));
  self.setState({aprov:{estado:'aprovada',por,em:'23/09/2026',total:m.total,sig:m.sig,pcs},conf5:false,
    g2toast:'Compra aprovada por '+por+' · emitidos '+pcIds(pcs)+' vinculados à '+SX.nome+', à '+SX.sol.id+' e às propostas escolhidas.'}); }
function podeAprovar(self,m){ if(!m.pcs.length){ toast(self,'Nada a aprovar: escolha propostas com quantidade a pedir na etapa 4.'); return false; }
  if(m.njust){ toast(self,'Justifique '+m.njust+(m.njust>1?' escolhas que não são':' escolha que não é')+' a de menor custo que chega a tempo (etapa 4).'); return false; } return true; }
function aprovar(self){ const st=self.state; const m=M(self); const apr=aprOf(st);
  if(apr){ toast(self,'Compra já aprovada em '+apr.em+' · pedidos '+pcIds(apr.pcs)+' · nenhum pedido duplicado.'); return; }
  if(!podeAprovar(self,m)) return;
  if(m.podeAna){ self.setState({conf5:true,dec5:null}); return; }
  const a=st.aprov; if(a&&a.estado==='pendente'&&a.sig===m.sig){ emitir(self,m,a.quem+' (simulado)'); return; }
  if(a&&a.estado==='devolvida'&&a.sig===m.sig){ toast(self,'Devolvida pela '+a.quem+': ajuste escolhas ou quantidades na etapa 4 antes de reenviar.'); return; }
  if(a&&a.estado==='recusada'&&a.sig===m.sig){ toast(self,'Recusada pela '+a.quem+': nada foi contratado. Para uma nova proposta de compra, altere escolhas ou quantidades na etapa 4.'); return; }
  self.setState({aprov:{estado:'pendente',sig:m.sig,quem:m.quem,em:'23/09/2026 11:40',total:m.total},conf5:false,dec5:null,
    g2toast:(a?'Reenviado':'Enviado')+' para aprovação da '+m.quem+' (simulado · nenhuma mensagem real enviada). Nada é aprovado até a '+m.quem+' decidir.'}); }
// devolução ou recusa registrada pela alçada (simulada), sempre com motivo; nenhuma das duas emite pedido
function decidir(self){ const st=self.state; const d=st.dec5; const a=st.aprov; const m=M(self);
  if(!d||!a||a.estado!=='pendente'||a.sig!==m.sig){ self.setState({dec5:null}); return; }
  const mot=String(d.motivo||'').trim(); const dev=(d.tipo==='dev');
  if(!mot){ self.setState({dec5:Object.assign({},d,{err:'Informe o motivo da '+(dev?'devolução':'recusa')+'.'})}); return; }
  self.setState({dec5:null,aprov:Object.assign({},a,{estado:dev?'devolvida':'recusada',motivo:mot,dec:'23/09/2026 14:10'}),
    g2toast:dev?('Devolução da '+a.quem+' registrada (simulado): '+mot+'. Ajuste na etapa 4 e reenvie.')
               :('Recusa da '+a.quem+' registrada (simulado): '+mot+'. Nada foi contratado; a necessidade da '+SX.sol.id+' continua aberta.')}); }
function hooks(self){ if(self._hk) return; self._hk=true;
  self.g2pick=(gid,rid)=>{ if(gid==='g_saf') pick(self,rid); };
  self.g2after=(gid,rows,r)=>{ if(!r) return; const st=self.state;
    if(gid==='g_conv'){ const c=Object.assign({},st.conv||{}); c[r.id]={conv:r.v.conv,canal:r.v.canal,prazo:r.v.prazo}; const adic=!!st.env&&r.v.conv==='Convidar';
      keep(self,gid,r.id,{conv:c,g2toast:'Convite atualizado: '+r.v.nome+(r.v.conv==='Convidar'?(' · '+r.v.canal+' · responder até '+r.v.prazo):' · não será convidado')+'.'+(adic?' Envie com Enviar convites adicionais.':'')}); }
    if(gid==='g_cmp'){ const m=M(self); const it=m.items.find(x=>x.rid===r.id); if(!it) return; const p=it.props.find(x=>x.label===r.v.venc)||it.ch; const e=Object.assign({},st.esc||{});
      e[r.id]={f:p?p.f:'',ped:Number(r.v.ped),just:String(r.v.just||'')}; const ae=st.aprov&&st.aprov.estado;
      keep(self,gid,r.id,{esc:e,g2toast:'Escolha salva: '+it.nome+' · '+(p?p.nome:'')+' · '+qt(Number(r.v.ped),it.un)+'. Custos e pedidos recalculados.'
        +(ae==='pendente'?' A aprovação pendente precisa ser reenviada.':(ae==='devolvida'?' Reenvie à '+st.aprov.quem+' na etapa 5.':''))}); }
    if(gid==='g_ent'){ const x=Object.assign({},st.pcx||{}); const cur=x[r.id]||{}; const base=(GR('g_ent').rows||[]).find(y=>y.id===r.id)||{v:{}};
      if(!r.v.prev||r.v.prev<CD.hojeIso){ const all=Object.assign({},st.g2||{});
        all[gid]=Object.assign({},all[gid]||{},{rows:undefined,fl:null,fm:{rid:r.id,draft:{prev:r.v.prev||'',obs:r.v.obs||''},orig:{prev:base.v.prev||'',obs:base.v.obs||''},errs:{prev:'Use uma data a partir de hoje (23/09/2026).'},warn:false,ro:false,isNew:false,mode:'form'}});
        self.setState({g2:all,g2toast:''}); return; }
      const ap=aprOf(st); const np=ap?ap.pcs.find(p=>p.id===r.id):null; const op=CD.pedidos.find(p=>p.id===r.id);
      const falt=np?(np.itens.map(it=>faltaDe(st,it.nome,null)).filter(Boolean).sort()[0]||null):(op?faltaDe(st,op.item,op.id):null);
      x[r.id]=Object.assign({},cur,{prev:r.v.prev,obs:r.v.obs}); keep(self,gid,r.id,{pcx:x,g2toast:'Previsão de '+r.id+' reprogramada para '+brd(r.v.prev)+'. O Estoque passa a esperar esta data.'
        +(falt&&r.v.prev>falt?' Atenção: nova data depois da falta de '+brd(falt)+'.':'')}); } }; }
const WHYMSG={'Escolha a safra':'Escolha a safra na etapa 1 para abrir esta etapa.','Sem solicitação':'Esta safra ainda não tem solicitação: envie a demanda em Planejar safra › demanda de insumos.',
  'Safra encerrada':'Safra 2025/26 encerrada: só os pedidos (etapa 6) ficam em consulta.','Envie os convites':'Envie os convites na etapa 3 para receber propostas.','Aguarde propostas':'Aguarde as primeiras propostas (simuladas) chegarem.'};
function EXTRAVALS(self,v){ hooks(self);
  const st=self.state; const step=st.step||1; const saf=st.saf||null; sx(self); const m=self._m||M(self); const apr=aprOf(st); const a=st.aprov||null;
  // CMP.dc.html#sol=SOL-2027-02&saf=S27SF (vindo do Planejar safra): abre a mesma solicitação na etapa 2, uma vez e a cada troca de endereço
  // endereço com SOL de outra safra ou inexistente: abre a solicitação que a safra tem e corrige o endereço; safra encerrada abre em consulta;
  // safra sem solicitação gravada fica escolhida na etapa 1, com o próximo passo (Abrir Planejar safra)
  const abrirHash=()=>{ let h=''; try{ h=decodeURIComponent(location.hash||''); }catch(e){ h=''; } const ms=/[#&]saf=([^&]+)/.exec(h), mi=/[#&]sol=([^&]+)/.exec(h); if(!ms&&!mi) return;
    let sid=ms?ms[1]:null; if(!sid&&mi){ const f=safras().find(z=>{ const y=solDe(z.id); return y&&y.sol.id===mi[1]; }); if(f) sid=f.id; }
    const s=sid?safras().find(z=>z.id===sid):null; const x=s?solDe(s.id):null;
    if(x){ const outra=!!(mi&&mi[1]!==x.sol.id);
      const msg=outra?(mi[1]+' não é a solicitação da '+x.nome+': aberta a '+x.sol.id+'.'):('Solicitação '+x.sol.id+' aberta · origem: '+x.nome+' · Planejar safra, demanda de insumos.');
      setTimeout(()=>{ if(self.state.saf!==x.safra) trocaSafra(self,x.safra,{step:2,g2toast:msg}); else if(outra) toast(self,msg); hashSync(x.safra,x); },0); return; }
    if(s&&s.id==='S2526'){ setTimeout(()=>{ if(self.state.saf!==s.id) trocaSafra(self,s.id,{step:6,g2toast:s.nome+' encerrada: '+CD.sol2526+' concluída, pedidos em consulta.'}); },0); return; }
    if(s){ setTimeout(()=>{ trocaSafra(self,s.id,{step:1,g2toast:(mi?mi[1]+' não está gravada neste navegador':s.nome+' ainda não tem solicitação')+': envie a demanda em Planejar safra › demanda de insumos.'}); },0); return; }
    setTimeout(()=>self.setState({g2toast:(mi?mi[1]:'A safra do endereço')+' não foi encontrada: escolha a safra na etapa 1.'}),0); };
  if(!self.__hashIni){ self.__hashIni=1; abrirHash(); try{ window.addEventListener('hashchange',abrirHash); }catch(e){} }
  for(let i=1;i<=6;i++) v['s'+i]=(step===i);
  const whys={}; for(let i=2;i<=6;i++){ if(!saf) whys[i]='Escolha a safra'; else if(saf==='S2526'){ if(i<6) whys[i]='Safra encerrada'; } else if(!SX) whys[i]='Sem solicitação'; }
  if(SX){ if(!m.env){ whys[4]='Envie os convites'; whys[5]='Envie os convites'; } else if(!m.nresp){ whys[4]='Aguarde propostas'; whys[5]='Aguarde propostas'; } }
  const go=(i)=>{ const w=whys[i]; if(w){ toast(self,w==='Sem solicitação'?(safNome(saf)+' ainda não tem solicitação: envie a demanda em Planejar safra › demanda de insumos.'):WHYMSG[w]); return; } g2etapa(self,{step:i,conf5:false}); };
  g2steps(self,v,'stp',6,step,whys);   // só informa (UX-ACAO-UNICA-20261003): avanço e retorno na área de ações
  v.pick=(id)=>pick(self,id);
  const safObj=safras().find(s=>s.id===saf);
  v.ctx_saf=safObj?(safObj.nome+(SX?' · '+SX.sol.id:(saf==='S2526'?' · consulta':' · sem solicitação'))):'Nenhuma safra escolhida';
  v.ctx_faz='Fazenda '+((safObj&&safObj.faz)||'Santa Rita');
  // trilha de documentos
  const pendOk=!!(a&&a.estado==='pendente'&&a.sig===m.sig); const stale=!!(a&&a.estado==='pendente'&&a.sig!==m.sig);
  const devA=!!(a&&a.estado==='devolvida'), recA=!!(a&&a.estado==='recusada'); const mud=!!(a&&a.sig!==m.sig);   // mud: compra alterada depois da decisão
  v.tr_on=!!SX; v.orig_h=SX?SX.origem.h:'SAF.dc.html'; v.orig_t='Ver origem · demanda de insumos ›';
  const pill=(t,ok,sep,bad)=>({t,sep,st:'display:inline-flex;align-items:center;padding:3px 9px;border-radius:999px;font-weight:700;'+(ok?'background:#E4F3E9;color:#1E7A4C;':(bad?'background:#FDE8E6;color:#B42318;':'background:#EEF1EE;color:#5B6660;'))});
  v.trail=!SX?[]:[pill(SX.sol.id+' · '+SX.itens.length+' insumos',true,false),pill(m.env?(m.env.n+' convites enviados'):(m.nconv+' convites a enviar'),!!m.env,true),
    pill(m.nresp+(m.nresp===1?' proposta':' propostas'),m.nresp>0,true),
    pill(apr?('Aprovada · '+apr.por):(pendOk?('Aguardando '+a.quem):(stale?'Aprovação desatualizada':(devA?('Devolvida · '+a.motivo):(recA?('Recusada · '+a.motivo):'Aprovação pendente')))),!!apr,true,devA||recA),
    pill(apr?('Pedidos '+pcIds(apr.pcs)):(recA?'Não contratado':'Pedidos —'),!!apr,true,recA)];
  // resumos por etapa
  const MUT='color:#65736A;'; const WARN='color:#8A5A00;font-weight:700;'; const BAD='color:#B42318;font-weight:700;'; const OK='color:#1E7A4C;font-weight:700;';
  const ncob=SX?SX.dem.filter(d=>d.liq<=0.001).length:0;
  v.k2=SX?(SX.sol.id+' · '+SX.nome+' · enviada em '+SX.sol.enviada+' por '+SX.sol.por+' · '+SX.itens.length+' insumos a comprar · '+rs(SX.ref)+' a preço de referência · '+ncob+' insumos cobertos por estoque e pedidos'):''; v.k2st=MUT;
  if(m.env){ const fim=m.nresp>=m.esperadas; v.k3='Convites simulados: nenhuma mensagem real foi enviada · enviados em '+m.env.em+(m.env.adic?(' · '+m.env.adic+(m.env.adic>1?' adicionais':' adicional')):'')+' · '+m.nresp+' de '+m.env.n+' convites responderam'+(fim?'':' · respostas chegando…')+(m.nadic?(' · '+m.nadic+(m.nadic>1?' convites adicionais a enviar':' convite adicional a enviar')):''); v.k3st=WARN; }
  else { v.k3=m.nconv+' convites prontos em '+(m.G.length-m.semForn.length)+' grupos'+(m.semForn.length?(' · sem fornecedor homologado: '+m.semForn.join(', ')+' (ficam sem cotação)'):'')
      +' · só fornecedores homologados do grupo podem ser convidados · o envio é simulado'; v.k3st=m.semForn.length?WARN:MUT; }
  if(m.env&&m.semForn.length) v.k3+=' · sem cotação: '+m.semForn.join(', ');
  const eco=m.ref-m.total;
  v.k4=m.nresp+(m.nresp===1?' proposta':' propostas')+' · custo total escolhido '+rs(m.total)+(m.total>0&&eco>0?(' · '+rs(eco)+' abaixo da referência'):'')
    +(m.njust?(' · '+m.njust+(m.njust>1?' escolhas sem justificativa':' escolha sem justificativa')):'')+(m.nlate?(' · '+m.nlate+(m.nlate>1?' escolhas chegam':' escolha chega')+' depois da falta'):'')
    +(m.semProp?(' · '+m.semProp+' sem proposta'):'')+(m.excl?(' · '+m.excl+' fora do pedido (quantidade 0)'):'');
  v.k4st=(m.njust?BAD:MUT);
  v.dec4_on=!apr&&(devA||recA);
  v.dec4=devA?('Devolvida pela '+a.quem+' (simulado): '+a.motivo+'. '+(mud?'Compra ajustada: reenvie na etapa 5.':'Ajuste escolhas ou quantidades abaixo e reenvie na etapa 5.'))
    :(recA?('Recusada pela '+a.quem+' (simulado): '+a.motivo+'. Nada foi contratado; para uma nova proposta de compra, altere escolhas ou quantidades e envie de novo na etapa 5.'):'');
  const tot5=apr?apr.total:m.total; const pcs5=apr?apr.pcs:m.pcs;
  let ni5=CD.alcada.findIndex(x=>x.ate===null||tot5<=x.ate+1e-9); if(ni5<0) ni5=CD.alcada.length-1;
  const limTxt=(ix)=>CD.alcada[ix].ate===null?('acima de '+rs(CD.alcada[ix-1].ate)):('até '+rs(CD.alcada[ix].ate));
  v.k5='Valor da compra '+rs(tot5)+' · '+pcs5.length+(pcs5.length===1?' pedido':' pedidos')+' · aprova: '+CD.alcada[ni5].quem+' ('+limTxt(ni5)+')'; v.k5st=MUT;
  v.apr_tit=apr?'Pedidos emitidos':'Pedidos a gerar';
  v.alc=CD.alcada.map((x,ix)=>{ const req=(ix===ni5); const me=(ix===CD.perfil.idx); const tags=[]; if(me) tags.push('Seu perfil · '+CD.perfil.nome); if(req) tags.push('Exigida para '+rs(tot5));
    return {lim:(x.ate===null?'Acima de '+rs(CD.alcada[ix-1].ate):'Até '+rs(x.ate)),quem:x.quem,tag:tags.join(' · '),hasTag:tags.length>0,
      tagst:'padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;'+(req?'background:#1E7A4C;color:#fff;':'background:#EEF1EE;color:#15201A;'),
      st:'display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:10px;font-size:13px;border:1px solid '+(req?'#1E7A4C':'#E4E9E5')+';background:'+(req?'#E4F3E9':'#FFFFFF')+';'}; });
  let a5, a5st='padding:8px 12px;border-radius:10px;font-size:13px;font-weight:700;';
  if(apr){ a5='Aprovada por '+apr.por+' em '+apr.em+' · pedidos '+pcIds(apr.pcs)+' emitidos e vinculados à '+(SX?SX.sol.id:'')+'.'; a5st+='background:#E4F3E9;color:#1E7A4C;'; }
  else if(m.njust){ a5='Justifique '+m.njust+(m.njust>1?' escolhas que não são':' escolha que não é')+' a de menor custo que chega a tempo na etapa 4 antes de aprovar.'; a5st+='background:#FDE8E6;color:#B42318;'; }
  else if(m.podeAna){ a5='Valor dentro da sua alçada ('+CD.perfil.nivel+', '+limTxt(CD.perfil.idx)+'). Aprovar emite '+m.pcs.length+' pedidos vinculados à '+(SX?SX.nome+' e à '+SX.sol.id:'safra')+'.'+(stale?' O envio anterior à Direção perdeu a validade.':''); a5st+='background:#E3F0FB;color:#1E5F8F;'; }
  else if(pendOk){ a5='Aguardando '+a.quem+' desde '+a.em+' (simulado · nenhuma mensagem real enviada). Registre a decisão quando ela chegar: aprovação, devolução ou recusa.'; a5st+='background:#FFF3D6;color:#8A5A00;'; }
  else if(stale){ a5='A compra mudou depois do envio (etapa 4): a aprovação pendente perdeu a validade. Reenvie à '+m.quem+'.'; a5st+='background:#FDE8E6;color:#B42318;'; }
  else if(devA&&!mud){ a5='Devolvida pela '+a.quem+' em '+a.dec+' (simulado): '+a.motivo+'. Ajuste escolhas ou quantidades na etapa 4; depois de qualquer mudança, reenvie.'; a5st+='background:#FDE8E6;color:#B42318;'; }
  else if(devA){ a5='Compra ajustada depois da devolução ('+a.motivo+'). Reenvie à '+m.quem+'.'; a5st+='background:#FFF3D6;color:#8A5A00;'; }
  else if(recA&&!mud){ a5='Recusada pela '+a.quem+' em '+a.dec+' (simulado): '+a.motivo+'. Nada foi contratado; a necessidade da '+(SX?SX.sol.id:'solicitação')+' continua aberta (etapa 2).'; a5st+='background:#FDE8E6;color:#B42318;'; }
  else { a5='Acima da sua alçada ('+CD.perfil.nivel+', '+limTxt(CD.perfil.idx)+'): só a '+m.quem+' aprova '+rs(m.total)+'. Envie para aprovação.'+(recA?' A proposta anterior foi recusada: '+a.motivo+'.':''); a5st+='background:#FFF3D6;color:#8A5A00;'; }
  v.a5=a5; v.a5st=a5st;
  // devolução ou recusa (ações secundárias enquanto a aprovação está pendente)
  const d5=st.dec5||null; v.d5_on=pendOk&&!m.podeAna&&!d5; v.d5_open=pendOk&&!m.podeAna&&!!d5;
  v.d5_t=d5?(d5.tipo==='dev'?('Registre a devolução da '+a.quem+': a compra volta para ajuste na etapa 4 e precisa ser reenviada.'):('Registre a recusa da '+a.quem+': nada é contratado e a necessidade continua aberta.')):'';
  v.d5_btn=d5?(d5.tipo==='dev'?'Confirmar devolução':'Confirmar recusa'):''; v.d5_mot=d5?(d5.motivo||''):''; v.d5_err=d5?(d5.err||''):''; v.d5_hasErr=!!(d5&&d5.err);
  v.d5_set=(e)=>self.setState({dec5:Object.assign({},self.state.dec5,{motivo:e.target.value,err:''})});
  v.d5_dev=()=>self.setState({dec5:{tipo:'dev',motivo:'',err:''},conf5:false}); v.d5_rec=()=>self.setState({dec5:{tipo:'rec',motivo:'',err:''},conf5:false});
  v.d5_no=()=>self.setState({dec5:null}); v.d5_yes=()=>decidir(self);
  v.conf5=!!st.conf5&&!apr&&m.podeAna; v.c5_msg='Aprovar '+rs(m.total)+' e emitir '+m.pcs.length+(m.pcs.length===1?' pedido':' pedidos')+' ('+pcIds(m.pcs)+') como '+CD.perfil.nome+' · '+CD.perfil.nivel+'?';
  v.c5_no=()=>self.setState({conf5:false}); v.c5_yes=()=>{ const mm=M(self); if(aprOf(self.state)){ aprovar(self); return; } if(!podeAprovar(self,mm)||!mm.podeAna) return; emitir(self,mm,CD.perfil.nome+' ('+CD.perfil.nivel+')'); };
  // etapa 6
  if(saf==='S2526'){ v.k6='Safra encerrada · '+CD.ped2526.length+' pedidos entregues e conciliados · somente consulta'; v.k6st=MUT; }
  else if(SX){ const novos=apr?apr.pcs.length:0; const ant=CD.pedidos.filter(p=>SX.safra==='S2627'||SX.dem.some(d=>d.nome===p.item)).length;
    v.k6=(novos?(novos+' pedidos da '+SX.sol.id+' · '):'Nenhum pedido da '+SX.sol.id+' aprovado ainda · ')+ant+' pedidos anteriores em aberto'+(SX.safra==='S2627'?' · PC-088: 10 t de KCl 60% em quarentena não contam como cobertura até o laudo':''); v.k6st=MUT; }
  else { v.k6=''; v.k6st=MUT; }
  v.pcconf=(id)=>{ const s=self.state; const ap=aprOf(s); if(!ap) return; const p=ap.pcs.find(x=>x.id===id); if(!p) return; const x=Object.assign({},s.pcx||{}); const cur=x[id]||{};
    if(cur.conf){ toast(self,id+' já confirmado · nada registrado de novo.'); return; } x[id]=Object.assign({},cur,{conf:true});
    self.setState({pcx:x,g2toast:'Confirmação de '+p.nome+' registrada para '+id+' (simulada · nenhuma mensagem real enviada) · previsão '+brd(cur.prev||p.prev)+'.'}); };
  (apr?apr.pcs:[]).forEach(p=>{ v['entp_'+p.id]=()=>{ const r=(GR('g_ent').rows||[]).find(y=>y.id===p.id); if(r) g2open(self,GR('g_ent'),p.id,null); }; });
  // formulário Convite: destinatário e escopo que o fornecedor vai ver
  const Fv=v.g_conv_F; const fm3=g2st(self,'g_conv').fm; if(Fv&&Fv.open&&fm3&&fm3.rid&&m.conv[fm3.rid]){ const c=m.conv[fm3.rid]; const d=fm3.draft||{};
    const its=m.items.filter(x=>x.gi===c.gi).map(x=>x.nome+' · '+qt(x.nec,x.un)).join('; ');
    const dest=d.conv==='Convidar'?((d.canal==='WhatsApp'?('WhatsApp '+c.f.whats):('e-mail '+c.f.email))+(c.f.contato?' ('+c.f.contato+')':'')):'não será convidado';
    Fv.sub=(m.env&&!c.enviado?'Convite adicional: os demais já receberam em '+m.env.em+'. ':'')+'Destinatário: '+dest+'. Itens do convite ('+c.g+'): '+its+'. O envio é simulado.'; }
  // ---- área de ações (UX-ACAO-UNICA-20261003 · DS-02, DS-33 §74.5.7.1, DS-61): uma primária e uma rota de avanço por etapa ----
  // Retorno secundário nomeia a etapa anterior (na etapa 2 voltar à escolha é o "Trocar safra" do topo). Avançar só troca de etapa:
  // não envia convite nem aprova; envio e aprovação são comandos com verbo próprio. Confirmação aberta assume a tarefa (sem outra primária).
  const CUR=['Escolha da safra','Demanda','Cotações','Propostas','Aprovação','Entregas'];
  const ir=(i)=>({t:'‹ '+CUR[i-1],fn:()=>go(i),to:i,a:'voltar'}), av=(i,t)=>({t:t+' ›',fn:()=>go(i),to:i,a:'avancar'}), cmd=(t,fn)=>({t,fn,a:'comando'});
  let A={};
  if(step===1){ if(saf&&!SX&&saf!=='S2526') A={nota:safNome(saf)+' ainda não tem solicitação de compra: a demanda é enviada no Planejar safra (demanda de insumos).',prim:{t:'Abrir Planejar safra ›',h:safHref(saf),a:'abrir'}}; }
  else if(SX){
    if(step===2) A={prim:av(3,'Solicitar cotações')};
    if(step===3) A=!m.env?{volta:ir(2),nota:'Comparar propostas fica disponível depois do envio dos convites.',prim:cmd('Enviar convites (simulado)',()=>enviar(self))}
      :(m.nadic?{volta:ir(2),prim:cmd('Enviar '+m.nadic+(m.nadic>1?' convites adicionais':' convite adicional')+' (simulado)',()=>enviarAdic(self)),sec:whys[4]?null:av(4,'Comparar propostas'),nota:whys[4]?WHYMSG[whys[4]]:''}
        :(whys[4]?{volta:ir(2),nota:WHYMSG[whys[4]]}:{volta:ir(2),prim:av(4,'Comparar propostas')}));
    if(step===4) A=whys[5]?{volta:ir(3),nota:WHYMSG[whys[5]]}:{volta:ir(3),prim:av(5,'Revisar aprovação')};
    if(step===5){ A={volta:ir(4)};
      if(apr) A.prim=av(6,'Acompanhar entrega');
      else if(v.conf5||v.d5_open) A.nota='Conclua ou cancele a decisão acima.';
      else if(m.podeAna){ A.prim=cmd('Aprovar compra',()=>aprovar(self)); A.sec=av(6,'Acompanhar entregas'); }
      else if(pendOk){ A.prim=cmd('Registrar aprovação da '+m.quem,()=>aprovar(self)); A.sec=av(6,'Acompanhar entregas'); }
      else if(devA&&!mud) A.prim={t:'Ajustar escolhas ›',fn:()=>go(4),to:4,a:'resolver'};
      else if(recA&&!mud) A.prim={t:'Conferir demanda aberta ›',fn:()=>go(2),to:2,a:'resolver'};
      else { A.prim=cmd((stale||devA?'Reenviar à ':'Enviar à ')+m.quem,()=>aprovar(self)); A.sec=av(6,'Acompanhar entregas'); } }
    if(step===6) A={volta:ir(5),prim:{t:'Conferir recebimentos ›',h:'EST.dc.html',a:'abrir'}};
  }
  g2acoes(v,'aa',A);
  procGravar(self,m);
}
const NOMES_=['Escolha a safra','Confira a demanda','Solicite cotações','Compare propostas','Aprove a compra','Acompanhe a entrega'];
'''
