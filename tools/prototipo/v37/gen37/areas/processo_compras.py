# -*- coding: utf-8 -*-
"""Suprimentos › Compras (CMP.dc.html) · Suprimentos simplificado (docs/suprimentos-simplificado §2, §4.2, §5; pedido do proprietário de 05/10/2026).
Eram 6 etapas numeradas com 4 avanços que só trocavam de tela e uma cópia da demanda. Agora: 2 seções + 1 detalhe, nas mesmas regras.
  Atenda solicitações (lista mestre: safra, e depois manutenção e beneficiamento, como Origem) → detalhe da solicitação aberto na fase do estado:
  Cote (A cotar: convites por grupo) ou Decida (Em cotação em diante: propostas, escolha, justificativa, alçada e emissão)
  · Acompanhe pedidos (qualquer origem: previsão com versões, confirmação, recebido no Estoque).
Nenhum botão só navega; a primária é a do estado, com o rótulo que confirma o quê e quanto. Quem decide vem do perfil de quem age (menu lateral,
G2_PERFIS do CTL-3): a gestora (Ana) cota e decide até a alçada dela; acima, a Direção (Helena) aprova e emite, devolve ou recusa com motivo.
Quem envia nunca registra a decisão de quem aprova. Mudar uma escolha depois do envio invalida a aprovação (sig).
Dados: dados2 (SAFRAS, SOL_INICIAL + sol_itens(), demanda() com CAL-01, FORNECEDORES, PROPOSTAS, ALCADA, PEDIDOS). Solicitações enviadas pelo Planejar safra
chegam pelo registro compartilhado talhao-os-compras-v1 (localStorage) e pelo endereço #sol=…&saf=…; o andamento e o acompanhamento dos pedidos ficam
no mesmo registro. Pontos de entrada (sem implementar os módulos): solicitações de compra da manutenção (SC, c.scs no cenário, PCM 1c) e pedidos do
cenário (c.pedidos) entram nas mesmas listas por cmpScs e cmpPedidosCen."""
import json, os
from engine import (grid,esc,MUTED,LINE,BG,SURF,ACC,YEL,YELS,RED,REDS,BTN_ST,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, secoes_state, HEIGHTS37
import dados2 as D2
import cenario

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
NOMES=['Atenda solicitações','Acompanhe pedidos']

# ---------------- constantes locais (coerentes com dados2; declaradas em observações) ----------------
PERFIL=dict(nome='Ana',papel='Gestora',nivel='Gerente da fazenda',idx=1)   # alçada da gestora (papel gestor) = 2º nível de dados2.ALCADA; acima, a Direção
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
    safras=[dict(id=s['id'],nome=s['nome'],periodo=s['periodo'],estado=s['estado'],faz=s['fazenda']) for s in D2.SAFRAS]
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
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px; flex-wrap: wrap;"><div style="display: flex; flex-direction: column; gap: 2px; flex: 1 1 220px; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{t}</h3><div style="font-size: 12.8px; color: {MUTED};">{esc(desc)}</div></div>{acao}</div>'
            f'<div style="padding: 0 12px 12px;">{corpo}</div></section>')
def build():
    fname='CMP.dc.html'; E._reset_screen(fname)
    # ---------- Atenda solicitações (lista mestre; a safra vira Origem e filtro) ----------
    g_sol=grid([dict(k='sol',l='Solicitação',w=150),dict(k='sit',l='Situação',w=170),dict(k='falta',l='Falta em',t='date'),dict(k='orig',l='Origem',w=170),
                dict(k='itens',l='Itens',t='num',a='r'),dict(k='val',l='Valor ref.',t='num',a='r',d=2,pre='R$ '),dict(k='quem',l='Quem age',w=150)],
               [],edit=dict(m='pick'),gid='g_sol',total=False,qf=dict(k='sit',cut=' · '))
    # ---------- detalhe · fase Cote: convites por grupo ----------
    g_conv=grid([dict(k='nome',l='Grupo › fornecedor',w=210),dict(k='conv',l='Convite'),dict(k='resp',l='Resposta',w=180),dict(k='homol',l='Homologação',w=190),
                 dict(k='canal',l='Canal'),dict(k='contato',l='Contato',w=190),dict(k='prazo',l='Responder até')],
                [],edit=dict(m='form',title='Convite',leafOnly=False,sub='Escolha se convida, por qual canal e até quando o fornecedor responde. O envio é simulado.',
                     fields=[dict(k='conv',l='Convite',t='sel',opts=['Convidar','Não convidar'],req=True),
                             dict(k='canal',l='Canal',t='sel',opts=['E-mail','WhatsApp'],req=True,cond=dict(k='conv',eq='Convidar'),help='Só os canais autorizados no cadastro do fornecedor.'),
                             dict(k='prazo',l='Prazo de resposta',t='sel',opts=PRAZOS,req=True,cond=dict(k='conv',eq='Convidar'))]),
                tree=True,gid='g_conv',total=False,qf=dict(k='resp',l='resposta'))
    # ---------- detalhe · fase Decida: propostas por grupo e insumo (a escolha, quanto pedir e a justificativa) ----------
    g_cmp=grid([dict(k='nome',l='Grupo › insumo › proposta',w=180),dict(k='venc',l='Escolha',w=190),dict(k='ped',l='A pedir',t='num',a='r'),dict(k='falta',l='Falta em',t='date'),
                dict(k='chega',l='Chega em',t='date'),dict(k='preco',l='Preço',t='num',a='r',d=2,pre='R$ '),dict(k='tot',l='Custo',t='num',a='r',d=2,pre='R$ ',agg='sum')],
               [],edit=dict(m='form',title='Escolha',leafOnly=False,sub='Escolha a proposta e a quantidade a pedir; custo total e pedidos são recalculados.',
                    fields=[dict(k='venc',l='Proposta escolhida',t='sel',opts=[],req=True),
                            dict(k='ped',l='Quantidade a pedir',t='num',req=True,min=0),
                            dict(k='just',l='Justificativa',t='area')]),
               tree=True,gid='g_cmp',total=True)
    # ---------- Acompanhe pedidos (qualquer origem) ----------
    g_ped=grid([dict(k='nome',l='Pedido › item',w=170),dict(k='sit',l='Situação',w=190),dict(k='ae',l='A entregar',t='num',a='r'),dict(k='rec',l='Recebido',t='num',a='r'),
                dict(k='prev',l='Previsão',t='date'),dict(k='falta',l='Falta em',t='date'),dict(k='forn',l='Fornecedor',w=150)],
               [],edit=dict(m='form',title='Pedido',leafOnly=False,sub='',
                    fields=[dict(k='prev',l='Nova previsão de entrega',t='date',cond=dict(k='modo',eq='rep')),
                            dict(k='obs',l='Motivo da reprogramação',t='area',cond=dict(k='modo',eq='rep'),help='Ex.: fornecedor confirmou nova data de embarque.')]),
               tree=True,gid='g_ped',total=False,qf=dict(k='sit',cut=' · '))
    root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    EXTRAJS[0]=(cenario.js_prefixo()+'const CD = '+json.dumps(_cd(),ensure_ascii=False)+';\n'+open(os.path.join(root,'cal01.js'),encoding='utf-8').read()+'\n'+JS)
    # ---------- corpo ----------
    faixa=(f'<sc-if value="{H("det")}" hint-placeholder-val="{F()}"><div role="note" aria-label="Situação da solicitação" style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; padding: 10px 14px; border-radius: 12px; background: {SURF}; border: 1px solid {LINE}; font-size: 13px;">'
           f'<b style="font-size: 15px;">{H("fx_sol")}</b>'
           f'<span style="color: {MUTED};">Veio de</span><a href="{H("fx_orig_h")}" style="color: {ACC}; font-weight: 700; text-decoration: none;">{H("fx_orig")}</a>'
           f'<span aria-hidden="true" style="color: {MUTED};">›</span><span style="color: {MUTED};">Está</span><span style="{H("fx_est_st")}">{H("fx_est")}</span>'
           f'<span aria-hidden="true" style="color: {MUTED};">›</span><span style="color: {MUTED};">Falta</span><b>{H("fx_falta")}</b>'
           f'<span aria-hidden="true" style="color: {MUTED};">›</span><span style="color: {MUTED};">Próxima</span><b>{H("fx_prox")}</b></div></sc-if>')
    alc=(f'<sc-if value="{H("alc_on")}" hint-placeholder-val="{F()}"><div role="note" style="{H("alc_st")}">{H("alc_t")}</div></sc-if>'
         f'<sc-if value="{H("prev_on")}" hint-placeholder-val="{F()}"><div aria-label="Pedidos que serão emitidos" style="display: flex; flex-direction: column; gap: 4px; padding: 8px 12px; border-radius: 10px; border: 1px solid {LINE}; background: {BG}; font-size: 12.8px;">'
         f'<b style="font-size: 12px; letter-spacing: .04em; color: {MUTED};">{H("prev_tit")}</b>'
         f'<sc-for list="{H("prev_pcs")}" as="pc" hint-placeholder-count="3"><div style="display: flex; flex-wrap: wrap; gap: 4px 10px;"><b>{H("pc.id")}</b><span>{H("pc.forn")}</span><span style="color: {MUTED};">{H("pc.its")}</span><span style="flex-grow: 1;"></span><b>{H("pc.val")}</b></div></sc-for></div></sc-if>'
         # decisão negativa da Direção: devolver ou recusar, sempre com motivo; nenhuma das duas emite pedido
         f'<sc-if value="{H("d5_open")}" hint-placeholder-val="{F()}"><div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {SURF}; border: 1px solid {LINE};">'
         f'<div style="font-size: 13px; font-weight: 600;">{H("d5_t")}</div>'
         f'<textarea aria-label="Motivo da decisão" placeholder="Motivo da Direção" value="{H("d5_mot")}" onChange="{H("d5_set")}" style="font-family: inherit; font-size: 13px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; min-height: 54px; resize: vertical;"></textarea>'
         f'<sc-if value="{H("d5_hasErr")}" hint-placeholder-val="{F()}"><span role="alert" style="font-size: 12px; font-weight: 700; color: {RED};">{H("d5_err")}</span></sc-if></div></sc-if>')
    lista=(f'<sc-if value="{H("lista")}" hint-placeholder-val="{H("true")}">'
           + bloco('Solicitações','Toque na solicitação: o detalhe abre na fase em que ela está (cotar ou decidir).',g_sol) + '</sc-if>')
    cote=(f'<sc-if value="{H("cote")}" hint-placeholder-val="{F()}">'
          + bloco('Convites por grupo','Escolha quem convidar, o canal e o prazo; toque no fornecedor para mudar. Só fornecedor homologado no grupo recebe convite.',g_conv) + '</sc-if>')
    decida=(f'<sc-if value="{H("decida")}" hint-placeholder-val="{F()}">'
            + alc + bloco(H('cmp_tit'),'Compare custo total, prazo e se chega antes da falta; toque no insumo ou na proposta para escolher, mudar a quantidade ou justificar.',g_cmp,tit_hole=True)
            + f'<sc-if value="{H("conv_on")}" hint-placeholder-val="{F()}">'+bloco('Convidar outro fornecedor','Marque um homologado ainda não convidado; quem já recebeu não recebe de novo.',g_conv)+'</sc-if></sc-if>')
    s1=f'<div style="display: flex; flex-direction: column; gap: 14px;">{lista}{faixa}{cote}{decida}</div>'
    s2=bloco('Pedidos','De qualquer origem: previsão com as versões anteriores, confirmação e o que o Estoque já recebeu.',g_ped)
    corpo=(f'<sc-if value="{H("s1")}" hint-placeholder-val="{H("true")}">{s1}</sc-if><sc-if value="{H("s2")}" hint-placeholder-val="{F()}">{s2}</sc-if>'
           + E.area_acoes('aa','Ações da solicitação'))
    HEIGHTS37[fname]=1200
    shell37('CMP','Compras',corpo,fname=fname,subtitle='Da solicitação (safra e, depois, manutenção) ao pedido entregue: cote, decida e acompanhe na mesma tela.',
            steps=secoes_state(NOMES,label='Seções de compras'),primary_html=None,ctx=(H('ctx_faz'),'',None),search=False)

JS=r'''
// ===== Compras (lista de solicitações → detalhe na fase do estado · Acompanhe pedidos) =====
function GR(id){ return GRIDS.find(g=>g.id===id); }
try { window.__cmp = { cenGet, cenMudar, cenReset }; } catch (e) {}
function nf(n,d){ return Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:d||0,maximumFractionDigits:d||0}); }
function rs(n){ return 'R$ '+nf(n,2); }
function qt(n,un){ n=Number(n)||0; const d=Math.abs(n-Math.round(n))>1e-9?(un==='L'?1:2):0; return nf(n,d)+' '+un; }
function brd(s){ if(!s) return '—'; const a=String(s).split('-'); return a[2]+'/'+a[1]+'/'+a[0]; }
function addd(s,n){ const d=new Date(s+'T12:00:00'); d.setDate(d.getDate()+n); return d.toISOString().slice(0,10); }
function fnome(id){ const f=CD.forn.find(x=>x.id===id); return f?f.nome:id; }
function toast(self,t){ self.setState({g2toast:t}); }
function pt(a,b){ return String(a).localeCompare(String(b),'pt-BR'); }
// ---------- quem decide (perfil de quem age, G2_PERFIS do CTL-3): a gestora cota e decide até a alçada dela; acima, a Direção ----------
function cmpGestor(PF){ return g2papel(PF,'gestor'); }
function cmpDirecao(PF){ return g2papel(PF,'direcao'); }
// ---------- solicitação da safra aberta: a SOL-2026-07 inicial ou o registro gravado pelo Planejar safra (talhao-os-compras-v1) ----------
const SOL_KEY='talhao-os-compras-v1';
function regLer(){ try{ return JSON.parse(localStorage.getItem(SOL_KEY)||'null')||{v:1,sols:{}}; }catch(e){ return {v:1,sols:{}}; } }
function regGravar(o){ try{ localStorage.setItem(SOL_KEY,JSON.stringify(o)); }catch(e){} }
function solLer(){ return regLer().sols||{}; }
// safras da compra: as do cadastro e as que só existem numa solicitação gravada pelo Planejar safra (safra nova)
function safras(){ const ls=solLer(); return CD.safras.concat(Object.values(ls).filter(r=>r&&r.safra&&!CD.safras.some(s=>s.id===r.safra)).map(r=>({id:r.safra,nome:r.nome||r.safra,periodo:'',estado:'',faz:r.faz||''}))); }
function safNome(id){ const s=safras().find(x=>x.id===id); return s?s.nome:String(id||''); }
function safHref(saf){ return 'SAF.dc.html#saf='+encodeURIComponent(saf)+'&etapa=6'; }   /* o Planejar safra lê também o passo novo (SAF-única) */
const SOLC={}; let SX=null;
function solDe(saf){ if(!saf) return null; const rec=solLer()[saf]; if(!rec&&saf!=='S2627') return null;
  const key=rec?JSON.stringify([rec.id,rec.itens,rec.comp||0]):'ini'; if(SOLC[saf]&&SOLC[saf].key===key) return SOLC[saf]; let x;
  if(!rec) x={safra:saf,nome:safNome(saf),sol:{id:CD.sol.id,enviada:CD.sol.enviada,por:CD.sol.por},itens:CD.itens,dem:CD.dem,ref:CD.ref,comp:0};
  else { const det={}; (rec.det||[]).forEach(d=>{ det[d.nome]=d; }); if(saf==='S2627') CD.dem.forEach(d=>{ if(!det[d.nome]) det[d.nome]=d; });
    const itens=Object.keys(rec.itens||{}).map(n=>{ const d=det[n]||{}; return {nome:n,grupo:d.grupo||'—',un:d.un||'',preco:Number(d.preco)||0,nec:Math.round(Number(rec.itens[n])*100)/100}; })
      .sort((a,b)=>pt(a.grupo,b.grupo)||pt(a.nome,b.nome)); itens.forEach((it,i)=>{ it.i=i; });
    x={safra:saf,nome:rec.nome||safNome(saf),sol:{id:rec.id,enviada:rec.em||rec.at||'',por:rec.por||''},itens,dem:Object.values(det),ref:itens.reduce((a,it)=>a+it.nec*it.preco,0),comp:rec.comp||0}; }
  x.key=key; x.pcIni=CD.pcIni+10*Math.max(0,safras().findIndex(s=>s.id===saf)); x.origem={t:'Planejar safra · '+x.nome,h:safHref(saf)};
  SOLC[saf]=x; return x; }
function sx(self){ SX=solDe(self.state.saf||null); return SX; }
// memória CAL-01 do insumo (a mesma função do Planejar safra)
const OPT={hoje:CD.hojeIso,viavel:CD.viavel};   /* uso antes de hoje = realizado; compra nova chega a partir da data viável */
function calDe(d){ return cal01(d.est,d.evs||[],0,OPT); }
// cada safra guarda o próprio andamento da compra (convites, escolhas, aprovação); trocar de solicitação não mistura processos. O andamento fica no
// registro compartilhado (talhao-os-compras-v1 · proc[safra]), ligado à versão da solicitação: recarregar ou ir à origem e voltar não perde a compra,
// e o Planejar safra mostra o estado. O acompanhamento dos pedidos (previsões com versões, confirmação) fica em ped, de todas as origens.
const PROC=['env','nresp','conv','esc','aprov','dec5']; const PROC_REG=['env','nresp','conv','esc','aprov'];
function procLer(id){ const x=solDe(id); if(!x) return null; const p=(regLer().proc||{})[id]; return (p&&p.key===x.key&&p.sol===x.sol.id)?p:null; }
function procDe(self,id){ const st=self.state; if(id&&id===st.saf) return st; return (st.porSaf||{})[id]||procLer(id)||{}; }
function procGravar(self,m){ const st=self.state; const id=st.saf; if(!id||!SX||SX.safra!==id) return; const snap={sol:SX.sol.id,key:SX.key,comp:SX.comp||0};
  PROC_REG.forEach(k=>{ snap[k]=(st[k]===undefined?null:st[k]); }); snap.estado=estado(SX,m,st).t;
  const js=JSON.stringify(snap); const memo=self._procJs||(self._procJs={}); if(memo[id]===js) return; memo[id]=js;
  const o=regLer(); o.proc=o.proc||{}; o.proc[id]=snap; const r=o.sols&&o.sols[id]; if(r&&r.id===snap.sol&&snap.estado!=='A cotar') r.estado=snap.estado; regGravar(o); }
// acompanhamento dos pedidos (todas as origens): previsão atual, versões anteriores (RF-SUP-012) e confirmação do fornecedor
function pedLer(){ return (regLer().ped||{}); }
function pedPut(id,patch){ const o=regLer(); o.ped=o.ped||{}; o.ped[id]=Object.assign({},o.ped[id]||{},patch); regGravar(o); }
function abrirSol(self,id,extra){ const st=self.state; const patch={saf:id,sec:1,cmp_conv:false,dec5:null};
  if(st.saf!==id){ const bag=Object.assign({},st.porSaf||{}); if(st.saf){ const cur={}; PROC.forEach(k=>{ cur[k]=st[k]; }); bag[st.saf]=cur; }
    const nx=bag[id]||procLer(id)||{}; PROC.forEach(k=>{ patch[k]=(nx[k]===undefined?null:nx[k]); }); if(!patch.nresp) patch.nresp=0; patch.porSaf=bag; }
  self.setState(Object.assign(patch,extra||{}));
  if(patch.env&&(patch.nresp||0)<patch.env.ordem.length) tickResp(self); }   /* respostas que ainda faltavam continuam chegando */
function voltarLista(self,extra){ const st=self.state; const bag=Object.assign({},st.porSaf||{}); if(st.saf){ const cur={}; PROC.forEach(k=>{ cur[k]=st[k]; }); bag[st.saf]=cur; }
  self.setState(Object.assign({saf:null,porSaf:bag,dec5:null,cmp_conv:false},extra||{})); hashSync(null,null); }
function hashSync(id,x){ try{ const h=x?('#sol='+encodeURIComponent(x.sol.id)+'&saf='+encodeURIComponent(id)):''; if(decodeURIComponent(location.hash||'')!==decodeURIComponent(h)) history.replaceState(null,'',location.pathname+location.search+h); }catch(e){} }
function grupos(X){ return [...new Set((X?X.itens:[]).map(x=>x.grupo))].sort(pt); }
function pcIds(pcs){ return !pcs||!pcs.length?'—':(pcs.length===1?pcs[0].id:pcs[0].id+' a '+pcs[pcs.length-1].id); }
function T(t){ return {k:'txt',t:t}; } function B(t){ return {k:'b',t:t}; } function MU(t){ return {k:'mut',t:t}; } function CH(t,c){ return {k:'chip',t:t,c:c}; }
function LK(t,h){ return {k:'link',t:t,h:h}; } function BR(){ return {k:'br',t:''}; }
function aprOf(P){ return (P&&P.aprov&&P.aprov.estado==='aprovada')?P.aprov:null; }
function dm(iso){ return iso?iso.slice(8,10)+'/'+iso.slice(5,7):'—'; }
// falta a partir de (CAL-01): 1ª data em que a projeção do insumo falta para esta solicitação — estoque apto com reservas, outras origens
// e pedidos em aberto na data prevista (a previsão reprogramada em Acompanhe pedidos vale; excl = pedido a desconsiderar; pedidos novos desta solicitação nunca entram)
function faltaDe(X,nome,excl){ const d=(X?X.dem:[]).find(x=>x.nome===nome); if(!d||!d.evs) return null; const px=pedLer();
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
// ---------- modelo da compra de uma solicitação X com o andamento P (convites, escolhas, respostas, aprovação) ----------
function Mx(X,P){ P=P||{}; const G=grupos(X); const conv={}; const env=P.env||null; const nresp=P.nresp||0; const apr0=aprOf(P);
  G.forEach((g,gi)=>{ CD.forn.filter(f=>f.grupos.indexOf(g)>=0).forEach(f=>{ const rid='C_'+gi+'_'+f.id; const s=(P.conv||{})[rid]||{};
    const enviado=!!(env&&env.conv.indexOf(rid)>=0); const cn=f.canais||['E-mail'];
    // depois do envio, quem não recebeu convite só entra se for marcado de novo (convite adicional)
    conv[rid]={rid,g,gi,f,homol:!!f.homologado,conv:f.homologado?(s.conv||(env&&!enviado?'Não convidar':'Convidar')):'—',
      canal:(s.canal&&cn.indexOf(s.canal)>=0)?s.canal:cn[0],prazo:s.prazo||CD.prazoPadrao,enviado,temProp:(CD.props[g]||[]).some(p=>p.f===f.id)}; }); });
  const got={}; if(env) env.ordem.slice(0,nresp).forEach((k,ix)=>{ got[k]=env.horas[ix]; });
  const items=(X?X.itens:[]).map(it=>{ const gi=G.indexOf(it.grupo); const s=(P.esc||{})['I_'+it.i]||{}; const ped=(s.ped!==undefined&&s.ped!==''&&!isNaN(Number(s.ped)))?Number(s.ped):it.nec;
    const falta=faltaDe(X,it.nome,null);
    const props=(CD.props[it.grupo]||[]).filter(p=>got['C_'+gi+'_'+p.f]).map(p=>{ const preco=Math.round(it.preco*p.fator*100)/100; const fr=(p.frete==='FOB')?(CD.fob[it.un]||0):0;
      const chega=addd(CD.hojeIso,p.prazo);
      return {f:p.f,nome:fnome(p.f),preco,prazo:p.prazo,frete:p.frete,pag:p.pag,validade:p.validade,fr,unit:preco+fr,hora:got['C_'+gi+'_'+p.f],chega,late:!!(falta&&chega>falta),
        label:fnome(p.f)+' · '+rs(preco)+'/'+it.un+' · '+p.prazo+' dias · '+p.frete}; }).sort((a,b)=>a.unit-b.unit);
    const low=props.length?props[0]:null;                 /* menor custo total (selo) */
    const ref=props.find(p=>!p.late)||low;                /* menor custo entre as que chegam a tempo: escolha padrão e referência da justificativa */
    let ch=s.f?(props.find(p=>p.f===s.f)||null):null; if(!ch) ch=ref;
    const naoMenor=!!(ch&&(ch.late||(ref&&ch.f!==ref.f&&ch.unit>ref.unit+1e-9))); const just=String(s.just||'');
    return Object.assign({},it,{gi,rid:'I_'+it.i,ped,props,low,ref,ch,falta,naoMenor,just,justPend:naoMenor&&!just.trim(),tot:ch?ped*ch.unit:0}); });
  const byF={}; items.forEach(it=>{ if(!it.ch||!(it.ped>0)) return; (byF[it.ch.f]||(byF[it.ch.f]=[])).push(it); });
  const pcs=CD.forn.filter(f=>byF[f.id]).map((f,ix)=>{ const its=byF[f.id];
    return {id:'PC-'+((X?X.pcIni:CD.pcIni)+ix),f:f.id,nome:f.nome,itens:its,valor:its.reduce((a,x)=>a+x.tot,0),prazo:Math.max.apply(null,its.map(x=>x.ch.prazo)),pag:its[0].ch.pag}; });
  const total=pcs.reduce((a,p)=>a+p.valor,0);
  let ni=CD.alcada.findIndex(a=>a.ate===null||total<=a.ate+1e-9); if(ni<0) ni=CD.alcada.length-1;
  const sig=JSON.stringify(items.map(it=>[it.i,it.ch?it.ch.f:'',Math.round(it.ped*1000)/1000]));
  const invited=Object.values(conv).filter(c=>c.conv==='Convidar');
  const nadic=(env&&!apr0)?Object.values(conv).filter(c=>c.homol&&!c.enviado&&c.conv==='Convidar').length:0;
  const semForn=G.filter(g=>!Object.values(conv).some(c=>c.g===g&&c.homol));
  const faltaMin=items.filter(x=>x.falta&&x.ped>0).map(x=>x.falta).sort()[0]||'';
  return {G,conv,env,nresp,got,items,pcs,total,ni,quem:CD.alcada[ni].quem,dentro:ni<=CD.perfil.idx,sig,nconv:invited.length,nadic,semForn,faltaMin,
    njust:items.filter(x=>x.justPend).length,semProp:items.filter(x=>!x.ch).length,excl:items.filter(x=>x.ch&&!(x.ped>0)).length,
    nlate:items.filter(x=>x.ch&&x.ch.late&&x.ped>0).length,esperadas:env?env.ordem.length:0,ref:X?X.ref:0};
}
function M(self){ sx(self); return Mx(SX,self.state); }
// vocabulário único da situação (o mesmo que o Planejar safra lê do registro): A cotar · Em cotação · Justificar · Pronta para decidir · Aguardando Direção ·
// Devolvida · Recusada · Pedidos emitidos. Também diz quem age e o que falta
function estado(X,m,P){ const a=P.aprov||null; const G=g2quem('gestor'), D=g2quem('direcao');
  if(a&&a.estado==='aprovada') return {t:'Pedidos emitidos',c:'green',quem:'—',falta:'nada: acompanhe os pedidos'};
  if(a&&a.estado==='recusada'&&a.sig===m.sig) return {t:'Recusada',c:'red',quem:G,falta:'necessidade aberta (não contratado)'};
  if(a&&a.estado==='devolvida'&&a.sig===m.sig) return {t:'Devolvida',c:'red',quem:G,falta:'ajustar: '+a.motivo};
  if(a&&a.estado==='pendente'&&a.sig===m.sig) return {t:'Aguardando Direção',c:'yellow',quem:D,falta:'decisão da Direção ('+rs(a.total)+')'};
  if(!m.env) return {t:'A cotar',c:'gray',quem:G,falta:m.nconv+' convites a enviar'};
  if(!m.nresp) return {t:'Em cotação',c:'blue',quem:'fornecedores',falta:'propostas · 0 de '+m.esperadas};
  /* enquanto as respostas chegam, a escolha padrão ainda pode mudar: "Justificar" só depois de todas (antes pedia justificar uma proposta provisória) */
  if(m.nresp<m.esperadas) return {t:'Em cotação',c:'blue',quem:G,falta:m.nresp+' de '+m.esperadas+' respostas'};
  if(m.njust) return {t:'Justificar',c:'red',quem:G,falta:m.njust+(m.njust>1?' escolhas fora do menor custo a tempo':' escolha fora do menor custo a tempo')};
  return {t:'Pronta para decidir',c:'blue',quem:G,falta:m.dentro?'aprovar e emitir':'enviar à Direção (acima de '+rs(CD.alcada[CD.perfil.idx].ate)+')'}; }
// ---------- pontos de entrada (assinatura, sem implementar os módulos) ----------
// Solicitações de compra da manutenção (SC, PCM 1c): o cenário guarda c.scs = {id:{id, tipo, origem:'Manutenção', om, estado, criada, precisa, itens:[{nome,un,qtd,grupo,preco}]}}.
// A linha entra em Atenda solicitações com a Origem "Manutenção · OM-…" e "Falta em" = a data de que a máquina precisa; a cotação usa este mesmo detalhe
// quando o PCM 1c ligar solDe('SC-…'). Hoje a semente não tem SC: nenhuma linha aparece.
function cmpScs(C){ return Object.values((C&&C.scs)||{}).map(sc=>({id:sc.id,origem:(sc.origem||'Manutenção')+(sc.om?' · '+sc.om:''),estado:sc.estado||'A cotar',precisa:sc.precisa||'',
  itens:(sc.itens||[]).length,valor:(sc.itens||[]).reduce((a,i)=>a+(Number(i.qtd)||0)*(Number(i.preco)||0),0)})); }
// Pedidos gravados no cenário (c.pedidos, PCM 1c: {id, sc|sol, forn, itens:[{nome,un,qtd}], prevs:[{prev,motivo,em}], estado}): entram em Acompanhe pedidos
function cmpPedidosCen(C){ return Object.values((C&&C.pedidos)||{}); }
// recebido no Estoque (mesmo cenário, sem redigitar): notas conferidas contra o pedido (movimento recebimento-nf com estRec)
function cmpRecebido(C,pc){ const vis={}; return (C.movs||[]).filter(m=>m.tipo==='recebimento-nf'&&m.estRec&&String(m.estRec.ped||'').split(' · ')[0]===pc).reduce((a,m)=>{ if(vis[m.estRec.id]) return a; vis[m.estRec.id]=1; return a.concat([m.estRec]); },[]); }

// ---------- lista mestre: uma linha por solicitação (Origem: safra; manutenção e beneficiamento quando chegarem) ----------
function linhasSol(self,C,PF){ const out=[];
  safras().forEach(s=>{ const X=solDe(s.id);
    if(X){ const P=procDe(self,s.id); const m=Mx(X,P); const e=estado(X,m,P);
      out.push({id:s.id,v:{sol:X.sol.id,sit:e.t,falta:m.faltaMin,orig:'Safra · '+X.nome,itens:X.itens.length,val:X.ref,quem:e.quem},s:{sol:X.sol.id+' '+X.nome,sit:e.t,orig:'Safra '+X.nome,quem:e.quem,itens:X.itens.length+' insumos'},
        p:{sol:[B(X.sol.id),MU(X.nome)],sit:[CH(e.t,e.c)],falta:m.faltaMin?[T(brd(m.faltaMin))]:[MU('—')],orig:[T('Safra · '+X.nome)],itens:[T(X.itens.length+' insumos')],quem:[T(e.quem)]}}); }
    else if(s.id==='S2526') out.push({id:s.id,v:{sol:CD.sol2526,sit:'Concluída',falta:'',orig:'Safra · '+s.nome,itens:CD.ped2526.length,val:CD.ped2526.reduce((a,p)=>a+p.qtd*p.preco,0),quem:'—'},
      s:{sol:CD.sol2526,sit:'Concluída',orig:'Safra '+s.nome,quem:''},p:{sol:[B(CD.sol2526),MU(s.nome)],sit:[CH('Concluída','gray')],falta:[MU('—')],orig:[T('Safra · '+s.nome)],itens:[T(CD.ped2526.length+' insumos')],quem:[MU('—')]}}); });
  cmpScs(C).forEach(sc=>out.push({id:'SC|'+sc.id,v:{sol:sc.id,sit:sc.estado,falta:sc.precisa,orig:sc.origem,itens:sc.itens,val:sc.valor,quem:g2quem('gestor')},s:{sol:sc.id,sit:sc.estado,orig:sc.origem,quem:g2quem('gestor')},
    p:{sol:[B(sc.id)],sit:[CH(sc.estado,'gray')],falta:sc.precisa?[T(brd(sc.precisa))]:[MU('—')],orig:[T(sc.origem)],itens:[T(sc.itens+(sc.itens===1?' item':' itens'))],quem:[T(g2quem('gestor'))]}}));
  // quem age primeiro: a Direção vê antes o que aguarda ela; a gestora, o que ela move; concluídas por último
  const ord=(r)=>{ const sit=r.v.sit; if(cmpDirecao(PF)) return sit==='Aguardando Direção'?0:2; return ({'Justificar':0,'Devolvida':0,'Pronta para decidir':0,'A cotar':1,'Em cotação':1,'Aguardando Direção':2,'Recusada':3,'Pedidos emitidos':3,'Concluída':4})[sit]||1; };
  return out.sort((a,b)=>(ord(a)-ord(b))||(String(a.v.falta||'9').localeCompare(String(b.v.falta||'9')))); }
// ---------- Acompanhe pedidos: todas as origens, com previsão em versões e o recebido no Estoque ----------
function linhasPed(self,C){ const out=[]; const px=pedLer(); const hoje=CD.hojeIso;
  const sitPed=(prev,falt,ae,rec,conf)=>{ if(!(ae>1e-9)) return CH('Recebido','green'); if(prev&&prev<hoje) return CH('Atrasado','red');
    if(falt&&prev&&prev>falt) return CH('Chega depois da falta','red'); if(rec>1e-9) return CH('Parcial','yellow'); return conf?CH('Confirmado','green'):CH('Aguarda confirmação','blue'); };
  const nfs=(id)=>cmpRecebido(C,id);
  // pedidos emitidos pelas solicitações (andamento de cada safra)
  safras().forEach(s=>{ const X=solDe(s.id); if(!X) return; const P=procDe(self,s.id); const a=aprOf(P); if(!a) return;
    a.pcs.forEach(p=>{ const x=px[p.id]||{}; const prev=x.prev||p.prev; const rcv=nfs(p.id).reduce((t,r)=>t+(Number(r.conf)||0),0); const one=p.itens.length===1;
      const qtd=p.itens.reduce((t,it)=>t+it.ped,0); const ae=one?Math.max(0,p.itens[0].ped-rcv):qtd; const falt=p.itens.map(it=>faltaDe(X,it.nome,null)).filter(Boolean).sort()[0]||'';
      const st=sitPed(prev,falt,ae,rcv,x.conf);
      const r={id:p.id,v:{nome:p.id,sit:st.t,ae:one?ae:'',rec:one?rcv:'',prev,falta:falt,forn:p.nome},s:{nome:p.id+' '+p.nome+' '+X.sol.id,sit:st.t,forn:p.nome},
        p:{nome:[B(p.id),MU(one?p.itens[0].nome:p.itens.length+' insumos')],sit:[st].concat((x.prevs||[]).length?[MU((x.prevs||[]).length+(x.prevs.length>1?' reprogramações':' reprogramação'))]:[]),
           ae:one?[B(qt(ae,p.itens[0].un))]:[MU(p.itens.length+' itens')],rec:one?(rcv>1e-9?[T(qt(rcv,p.itens[0].un))]:[MU('—')]):[MU('—')],forn:[T(p.nome)]},
        ped:{tipo:'sol',id:p.id,X,p,x,orig:X.sol.id+' · '+X.nome}};
      if(!one) r.kids=p.itens.map(it=>({id:p.id+'_'+it.i,ro:true,v:{nome:it.nome,ae:it.ped,rec:0,prev,falta:it.falta||'',forn:p.nome},s:{nome:it.nome},
        p:{nome:[T(it.nome)],sit:[MU('')],ae:[T(qt(it.ped,it.un))],rec:[MU('—')],forn:[MU('')]}}));
      out.push(r); }); });
  // pedidos anteriores em aberto (dados2) e pedidos gravados no cenário (PCM 1c)
  CD.pedidos.forEach(p=>{ const x=px[p.id]||{}; const prev=x.prev||p.prev; const rh=nfs(p.id).reduce((t,r)=>t+(Number(r.conf)||0),0); const rcv=p.rec+rh; const ae=Math.max(0,p.ae-rh);
    const X=solDe('S2627'); const falt=faltaDe(X,p.item,p.id)||''; const st=sitPed(prev,falt,ae,rcv,x.conf!==undefined?x.conf:true);
    out.push({id:p.id,v:{nome:p.id,sit:st.t,ae,rec:rcv,prev,falta:falt,forn:p.forn},s:{nome:p.id+' '+p.forn+' '+p.item,sit:st.t,forn:p.forn},
      p:{nome:[B(p.id),MU(p.item)],sit:[st].concat(p.quar?[MU(nf(p.quar)+' '+p.un+' em quarentena')]:[]).concat((x.prevs||[]).length?[MU((x.prevs||[]).length+(x.prevs.length>1?' reprogramações':' reprogramação'))]:[]),
         ae:ae>1e-9?[B(qt(ae,p.un))]:[MU('—')],rec:rcv>1e-9?[T(qt(rcv,p.un))]:[MU('—')],forn:[T(p.forn)]},ped:{tipo:'base',id:p.id,p,x,orig:'SOL-2026-07 · anterior à cotação',nfprev:p.nfprev}}); });
  cmpPedidosCen(C).forEach(p=>{ if(out.some(r=>r.id===p.id)) return; const its=p.itens||[]; const x=px[p.id]||{}; const prev=x.prev||(p.prevs&&p.prevs.length?p.prevs[p.prevs.length-1].prev:'');
    out.push({id:p.id,ro:true,v:{nome:p.id,sit:p.estado||'Emitido',ae:'',rec:'',prev,falta:'',forn:p.forn||''},s:{nome:p.id,sit:p.estado||'Emitido',forn:p.forn||''},
      p:{nome:[B(p.id),MU((p.sc||p.sol||'')+(its.length?' · '+its.length+(its.length>1?' itens':' item'):''))],sit:[CH(p.estado||'Emitido','gray')],ae:[MU('—')],rec:[MU('—')],forn:[T(p.forn||'—')]},ped:{tipo:'cen',id:p.id,p,x}}); });
  // safra encerrada: entregues (consulta)
  CD.ped2526.forEach(p=>out.push({id:p.id,ro:true,v:{nome:p.id,sit:'Recebido',ae:0,rec:p.qtd,prev:p.prev,falta:'',forn:p.forn},s:{nome:p.id+' '+p.forn+' '+p.item,sit:'Recebido',forn:p.forn},
    p:{nome:[B(p.id),MU(p.item+' · '+CD.sol2526)],sit:[CH('Recebido','green')],ae:[MU('—')],rec:[T(qt(p.qtd,p.un))],forn:[T(p.forn)]},ped:{tipo:'2526',id:p.id,p,x:{}}}));
  const ord={'Atrasado':0,'Chega depois da falta':0,'Aguarda confirmação':1,'Parcial':2,'Confirmado':3,'Recebido':4};
  return out.sort((a,b)=>((ord[a.v.sit]===undefined?3:ord[a.v.sit])-(ord[b.v.sit]===undefined?3:ord[b.v.sit]))||String(a.v.prev||'').localeCompare(String(b.v.prev||''))); }

function PREVALS(self,v){
  cenOuvir(self); const C=cenGet(); self._cen=C; const PF=g2perfil(); sx(self); const m=M(self); self._m=m; const apr=aprOf(self.state);
  GR('g_sol').rows=linhasSol(self,C,PF); GR('g_ped').rows=linhasPed(self,C);
  if(!SX){ ['g_conv','g_cmp'].forEach(g=>{ GR(g).rows=[]; }); return; }
  // ---- Cote · convites ----
  GR('g_conv').rows=m.G.map((g,gi)=>{ const cs=Object.values(m.conv).filter(c=>c.gi===gi); const its=m.items.filter(x=>x.gi===gi);
    const inv=m.env?cs.filter(c=>c.enviado):cs.filter(c=>c.conv==='Convidar'); const nr=inv.filter(c=>m.got[c.rid]).length;
    const npd=m.env?cs.filter(c=>c.homol&&!c.enviado&&c.conv==='Convidar').length:0;
    v['cgt_'+gi]=()=>tog(self,'g_conv','CG'+gi);
    return {id:'CG'+gi,dr:'cgt_'+gi,v:{nome:g},s:{nome:g,homol:'',conv:String(inv.length),resp:''},
      p:{nome:[B(g),MU(its.length+(its.length>1?' insumos':' insumo'))],homol:m.semForn.indexOf(g)>=0?[CH('Sem fornecedor homologado','yellow'),BR(),LK('Cadastrar em Parceiros e fornecedores','CD-05.dc.html')]
           :[MU(cs.filter(c=>c.homol).length+' homologados de '+cs.length)],
         conv:[T(inv.length+(inv.length===1?' convidado':' convidados'))].concat(npd?[MU('+'+npd+' a enviar')]:[]),resp:m.env?(inv.length?[CH(nr+' de '+inv.length+' propostas',nr===inv.length?'green':'yellow')]:[MU('Sem cotação')]):[MU('—')]},
      kids:cs.map(c=>{ const f=c.f; const r={id:c.rid,v:{nome:f.nome,conv:c.conv,canal:c.canal,prazo:c.prazo},s:{nome:f.nome},p:{nome:[B(f.nome)]}};
        if(!c.homol){ r.dr='cnh_'+c.rid; v[r.dr]=()=>toast(self,f.nome+' não é homologado para '+g+': '+f.motivo.toLowerCase()+'. Homologue em Cadastros › Parceiros e fornecedores para poder convidar.');
          r.p.homol=[CH('Não homologado','red'),MU(f.motivo),BR(),LK('Homologar em Parceiros e fornecedores','CD-05.dc.html')]; r.s.homol='Não homologado';
          r.p.conv=[MU('Indisponível')]; r.p.canal=[MU('—')]; r.p.contato=[MU('—')]; r.p.prazo=[MU('—')]; r.p.resp=[MU('—')]; return r; }
        r.p.homol=[CH('Homologado','green')]; r.s.homol='Homologado';
        const on=c.enviado||c.conv==='Convidar'; const dest=c.canal==='WhatsApp'?f.whats:f.email;
        r.p.conv=on?[B('Convidar')]:[MU('Não convidar')]; r.p.canal=on?[T(c.canal)]:[MU('—')]; r.s.canal=c.canal; r.p.contato=on?[T(dest)]:[MU('—')]; r.s.contato=dest; r.p.prazo=[on?T(c.prazo):MU('—')];
        if(m.env){ const h=m.got[c.rid]; const fim=m.nresp>=m.esperadas;
          if(c.enviado){ const em=((m.env.emx||{})[c.rid])||m.env.em;
            r.p.resp=h?[CH('Proposta recebida','green'),MU(h.slice(6))]:(fim?[CH('Sem resposta até agora','yellow'),MU('prazo '+c.prazo)]:[CH('Aguardando resposta','yellow'),MU('até '+c.prazo)]);
            r.dr='cenv_'+c.rid; v[r.dr]=()=>toast(self,'Convite simulado enviado a '+f.nome+' por '+c.canal+' em '+em+' · responder até '+c.prazo+(h?' · proposta recebida '+h:'')+'. Nenhuma mensagem real foi enviada.'); }
          else if(apr){ r.p.resp=[MU('Não convidado')]; r.dr='cenv_'+c.rid; v[r.dr]=()=>toast(self,f.nome+' não foi convidado nesta cotação.'); }
          else r.p.resp=(c.conv==='Convidar')?[CH('Convite adicional a enviar','blue')]:[MU('Não convidado')]; }   /* antes da aprovação: a linha abre o formulário Convite */
        else r.p.resp=[MU(on?'Envio pendente':'—')];
        if(!cmpGestor(PF)&&!r.dr){ r.dr='cnp_'+c.rid; v[r.dr]=()=>toast(self,'Convites: ação de '+g2quem('gestor')+' (compras).'); }
        r.s.resp=((r.p.resp||[])[0]||{}).t||'';   /* filtro rápido por resposta */
        return r; })}; });
  // formulário Convite: só os canais autorizados no cadastro do fornecedor
  const fm3=g2st(self,'g_conv').fm; const FC=GR('g_conv').edit.fields;
  if(fm3&&fm3.rid&&m.conv[fm3.rid]){ const c=m.conv[fm3.rid]; const cn=c.f.canais||['E-mail']; FC[1].opts=cn.slice();
    FC[1].help=cn.length>1?('Canais autorizados no cadastro de '+c.f.nome+'.'):('Só '+cn[0]+': é o único canal autorizado no cadastro de '+c.f.nome+' (Parceiros e fornecedores).'); }
  GR('g_conv').x0=Object.fromEntries(m.G.map((g,gi)=>['CG'+gi,true]));
  // ---- Decida · propostas por grupo e insumo ----
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
      kids:its.map(it=>{ const c=it.ch; const r={id:it.rid,v:{nome:it.nome,ped:it.ped,falta:it.falta||'',chega:c?c.chega:'',preco:c?c.preco:'',tot:it.tot,venc:c?c.label:'',just:it.just},s:{nome:it.nome},
          p:{nome:[B(it.nome)]}};
        r.p.ped=[B(qt(it.ped,it.un))].concat(it.ped<it.nec-1e-9?[MU('de '+qt(it.nec,it.un))]:[]); r.s.ped=qt(it.ped,it.un);
        r.p.falta=it.falta?[T(brd(it.falta))]:[MU('—')]; r.p.chega=c?[(c.late?CH(brd(c.chega),'red'):T(brd(c.chega)))]:[MU('—')];
        r.p.preco=c?[T(rs(c.preco)+'/'+it.un)]:[MU('—')]; r.s.preco=c?rs(c.preco)+'/'+it.un:'';
        if(c){ r.p.venc=[B(c.nome)].concat(it.naoMenor?(it.justPend?[CH('Justificar','red')]:[CH('Justificada','yellow')])
            :(it.low&&c.f===it.low.f?[CH('Menor custo total','green')]:[CH('Menor custo a tempo','green')])).concat(c.late?[CH('Chega depois da falta ('+dm(it.falta)+')','red')]:[]);
          r.s.venc=c.nome; }
        else { r.p.venc=[CH('Sem proposta ainda','gray')]; r.s.venc='Sem proposta'; r.dr='knp_'+it.i;
          const livres=Object.values(m.conv).filter(x=>x.gi===it.gi&&x.homol&&!x.enviado);
          v[r.dr]=()=>toast(self,m.semForn.indexOf(it.grupo)>=0?('Sem fornecedor homologado em '+it.grupo+': '+it.nome+' fica sem cotação. Cadastre e homologue em Parceiros e fornecedores.')
            :'Nenhuma proposta recebida para '+it.nome+' ainda. '+(livres.length?('Aguarde as respostas ou use Convidar outro fornecedor ('+livres.map(x=>x.f.nome).join(' ou ')+').')
            :('Todos os homologados de '+it.grupo+' já foram convidados: aguarde as respostas ou homologue outro fornecedor.'))); }
        if(apr){ r.dr='kap_'+it.i; v[r.dr]=()=>toast(self,'Pedidos emitidos: a escolha de '+it.nome+' está no pedido. Para mudar, cancele o pedido e cote de novo.'); }
        else if(!cmpGestor(PF)&&!r.dr){ r.dr='kng_'+it.i; v[r.dr]=()=>toast(self,'Escolher e justificar: ação de '+g2quem('gestor')+' (compras).'); }
        // painel do insumo: necessidade (bruta − estoque apto − a receber), justificativa e a memória no Planejar safra
        const d=SX.dem.find(x=>x.nome===it.nome); r.o=(d?[{t:'Necessidade = bruta − estoque apto − a receber = '+qt(d.bruta,it.un)+' − '+qt(d.est,it.un)+' − '+qt(d.rec,it.un)+' = '+qt(d.liq,it.un)}]:[])
          .concat(it.naoMenor&&it.just?[{t:'Justificativa: '+it.just}]:[]).concat([{t:'Ver memória no Planejar safra',h:SX.origem.h}]);
        r.kids=it.props.map(p=>{ const k={id:'P_'+it.i+'_'+p.f,ro:true,dr:'kp_'+it.i+'_'+p.f,v:{nome:p.nome,preco:p.preco,chega:p.chega,tot:it.ped*p.unit},s:{nome:p.nome,preco:rs(p.preco)+'/'+it.un},
            p:{nome:[T(p.nome),MU(p.frete+' · '+p.pag)],chega:[(p.late?CH(brd(p.chega),'red'):T(brd(p.chega)))],preco:[T(rs(p.preco)+'/'+it.un)],
               venc:(it.low&&p.f===it.low.f?[CH('Menor custo total','green')]:[]).concat(c&&p.f===c.f?[CH('Escolhida','blue')]:[]).concat(p.late?[CH('Chega depois da falta','red')]:[])}};
          k.s.venc=k.p.venc.map(x=>x.t).join(' ');
          v[k.dr]=apr?(()=>toast(self,'Pedidos emitidos: propostas em consulta.')):(cmpGestor(PF)?(()=>openEsc(self,it.rid,p.f)):(()=>toast(self,'Escolher: ação de '+g2quem('gestor')+' (compras).'))); return k; });
        return r; })}; }):[];
  spc.x0=Object.fromEntries(m.G.map((g,gi)=>['KG'+gi,true]));
}
function openEsc(self,rid,f){ const m=M(self); const it=m.items.find(x=>x.rid===rid); if(!it) return;
  const p=f?it.props.find(x=>x.f===f):null; const base={venc:it.ch?it.ch.label:'',ped:String(it.ped).replace('.',','),just:it.just||''}; const draft=Object.assign({},base); if(p) draft.venc=p.label;
  g2set(self,'g_cmp',{fm:{rid,draft,orig:Object.assign({},base),errs:{},warn:false,ro:false,isNew:false,mode:'form'},fl:null,fmc:null}); }
function enviar(self,PF){ const st=self.state; if(st.env){ toast(self,'Convites já enviados em '+st.env.em+' · nenhum convite duplicado.'); return; }
  if(!cmpGestor(PF)){ toast(self,'Enviar convites: ação de '+g2quem('gestor')+' (compras). Nada foi enviado.'); return; }
  const m=M(self); const sem=m.G.filter(g=>m.semForn.indexOf(g)<0&&!Object.values(m.conv).some(c=>c.g===g&&c.conv==='Convidar'));
  if(sem.length){ toast(self,'Convide ao menos um fornecedor homologado em: '+sem.join(', ')+'.'); return; }
  const inv=Object.values(m.conv).filter(c=>c.conv==='Convidar');
  if(!inv.length){ toast(self,'Nenhum grupo tem fornecedor homologado: cadastre em Parceiros e fornecedores para cotar.'); return; }
  const fora=m.semForn.length?(' Sem cotação (sem fornecedor homologado): '+m.semForn.join(', ')+'.'):'';
  const fila=m.G.map(g=>inv.filter(c=>c.g===g&&c.temProp).map(c=>c.rid)); const ordem=[];
  for(let k=0;fila.some(l=>l.length);k++){ fila.forEach(l=>{ if(l.length) ordem.push(l.shift()); }); }
  const horas=ordem.map((x,ix)=>{ const mm=10*60+52+ix*9; return '23/09 '+String(Math.floor(mm/60)).padStart(2,'0')+':'+String(mm%60).padStart(2,'0'); });
  self.setState({env:{em:'23/09/2026 10:47',n:inv.length,conv:inv.map(c=>c.rid),ordem,horas,por:g2ator(PF,'gestor')},nresp:0,
    g2toast:'Convites simulados: nenhuma mensagem real foi enviada · '+inv.length+' convites em '+(m.G.length-m.semForn.length)+' grupos. As respostas abrem a fase Decida.'+fora});
  tickResp(self); }
// convites adicionais depois do envio (antes dos pedidos emitidos): só os novos; quem já recebeu não recebe de novo
function enviarAdic(self,PF){ const st=self.state; const env=st.env; if(!env) return;
  if(aprOf(st)){ toast(self,'Pedidos emitidos: não há convite adicional. Para cotar de novo, cancele o pedido.'); return; }
  if(!cmpGestor(PF)){ toast(self,'Convites: ação de '+g2quem('gestor')+' (compras).'); return; }
  const m=M(self); const novos=Object.values(m.conv).filter(c=>c.homol&&!c.enviado&&c.conv==='Convidar');
  if(!novos.length){ toast(self,'Nenhum convite adicional marcado: toque num fornecedor homologado ainda não convidado.'); return; }
  const fila=m.G.map(g=>novos.filter(c=>c.g===g&&c.temProp).map(c=>c.rid)); const add=[];
  while(fila.some(l=>l.length)) fila.forEach(l=>{ if(l.length) add.push(l.shift()); });
  const hm=(t)=>{ const x=/(\d{2}):(\d{2})$/.exec(String(t||'')); return x?Number(x[1])*60+Number(x[2]):10*60+47; };
  const f2=(mm)=>String(Math.floor(mm/60)).padStart(2,'0')+':'+String(mm%60).padStart(2,'0');
  const base=Math.max(hm(env.horas[env.horas.length-1]),hm(env.em))+6; const em='23/09/2026 '+f2(base);
  const emx=Object.assign({},env.emx||{}); novos.forEach(c=>{ emx[c.rid]=em; });
  self.setState({env:Object.assign({},env,{n:env.n+novos.length,conv:env.conv.concat(novos.map(c=>c.rid)),ordem:env.ordem.concat(add),
      horas:env.horas.concat(add.map((x,ix)=>'23/09 '+f2(base+5+ix*9))),emx,adic:(env.adic||0)+novos.length}),cmp_conv:false,
    g2toast:'Convites adicionais simulados: nenhuma mensagem real foi enviada · '+novos.length+' para '+[...new Set(novos.map(c=>c.f.nome))].join(', ')+'. Quem já recebeu não recebe de novo.'});
  tickResp(self); }
// Aprovar e emitir: a decisão e a emissão ficam como dois registros com horário (KPI-SUP-04, OTIF), como "Aprovar e liberar" (PRD:2968)
function emitir(self,m,por){ const agora=cenAgora(); const pcs=JSON.parse(JSON.stringify(m.pcs.map(p=>({id:p.id,f:p.f,nome:p.nome,valor:p.valor,prazo:p.prazo,pag:p.pag,prev:addd(CD.hojeIso,p.prazo),
    itens:p.itens.map(it=>({i:it.i,nome:it.nome,grupo:it.grupo,un:it.un,nec:it.nec,ped:it.ped,tot:it.tot,naoMenor:it.naoMenor,just:it.just,ch:it.ch,low:it.low,falta:it.falta}))}))));
  const a0=self.state.aprov;
  self.setState({aprov:{estado:'aprovada',por,em:'23/09/2026',total:m.total,sig:m.sig,pcs,dec:{por,em:'23/09/2026 '+agora},emi:{em:'23/09/2026 '+agora,pcs:pcs.map(p=>p.id)},
      enviada:(a0&&a0.estado==='pendente')?{por:a0.por,em:a0.em}:null},dec5:null,
    g2toast:'Aprovada por '+por+' · emitidos '+pcIds(pcs)+' ('+rs(m.total)+') vinculados à '+SX.nome+', à '+SX.sol.id+' e às propostas escolhidas. Acompanhe em Acompanhe pedidos.'}); }
function podeAprovar(self,m){ if(!m.pcs.length){ toast(self,'Nada a aprovar: escolha propostas com quantidade a pedir.'); return false; }
  if(m.njust){ toast(self,'Justifique '+m.njust+(m.njust>1?' escolhas que não são':' escolha que não é')+' a de menor custo que chega a tempo.'); return false; } return true; }
function aprovar(self,PF){ const st=self.state; const m=M(self); const apr=aprOf(st);
  if(apr){ toast(self,'Pedidos já emitidos em '+apr.em+' · '+pcIds(apr.pcs)+' · nenhum pedido duplicado.'); return; }
  if(!podeAprovar(self,m)) return; const a=st.aprov;
  if(cmpDirecao(PF)){ if(a&&a.estado==='pendente'&&a.sig===m.sig){ emitir(self,m,g2ator(PF,'direcao')); return; }
    toast(self,'A Direção decide o que foi enviado a ela: nada aguarda a Direção nesta solicitação.'); return; }
  if(!cmpGestor(PF)){ toast(self,'Aprovar: ação de '+g2quem('gestor')+' (até '+rs(CD.alcada[CD.perfil.idx].ate)+') ou da Direção. Nada foi aprovado.'); return; }
  if(m.dentro){ emitir(self,m,g2ator(PF,'gestor')); return; }
  self.setState({aprov:{estado:'pendente',sig:m.sig,quem:m.quem,em:'23/09/2026 11:40',total:m.total,por:g2ator(PF,'gestor')},dec5:null,
    g2toast:(a?'Reenviado':'Enviado')+' à '+m.quem+' (simulado · nenhuma mensagem real enviada): '+rs(m.total)+'. Nada é aprovado até a '+m.quem+' decidir.'}); }
// devolução ou recusa da Direção, sempre com motivo; nenhuma das duas emite pedido
function decidir(self,PF){ const st=self.state; const d=st.dec5; const a=st.aprov; const m=M(self);
  if(!d||!a||a.estado!=='pendente'||a.sig!==m.sig){ self.setState({dec5:null}); return; }
  if(!cmpDirecao(PF)){ self.setState({dec5:Object.assign({},d,{err:'Devolver e recusar: decisão da Direção. Nada foi registrado.'})}); return; }
  const mot=String(d.motivo||'').trim(); const dev=(d.tipo==='dev');
  if(!mot){ self.setState({dec5:Object.assign({},d,{err:'Informe o motivo da '+(dev?'devolução':'recusa')+'.'})}); return; }
  const por=g2ator(PF,'direcao');
  self.setState({dec5:null,aprov:Object.assign({},a,{estado:dev?'devolvida':'recusada',motivo:mot,dec:'23/09/2026 14:10',decPor:por}),
    g2toast:dev?('Devolvida por '+por+': '+mot+'. A gestora ajusta e reenvia.')
               :('Recusada por '+por+': '+mot+'. Nada foi contratado; a necessidade da '+SX.sol.id+' continua aberta.')}); }
function hooks(self){ if(self._hk) return; self._hk=true;
  self.g2pick=(gid,rid)=>{ if(gid!=='g_sol') return; if(String(rid).indexOf('SC|')===0){ toast(self,rid.slice(3)+': a cotação da solicitação da manutenção entra por este detalhe quando o PCM 1c a ligar.'); return; }
    const x=solDe(rid); const s=safras().find(z=>z.id===rid);
    if(x){ abrirSol(self,rid,{g2toast:x.sol.id+' aberta · '+x.nome+'.'}); hashSync(rid,x); }
    else if(rid==='S2526'){ self.setState({sec:2,g2toast:(s?s.nome:'Safra 2025/26')+' encerrada: pedidos entregues em Acompanhe pedidos.'}); } };
  self.g2after=(gid,rows,r)=>{ if(!r) return; const st=self.state; const PF=g2perfil();
    if(gid==='g_conv'){ if(!cmpGestor(PF)){ keep(self,gid,r.id,{g2toast:'Convites: ação de '+g2quem('gestor')+'. Nada foi alterado.'}); return; }
      const c=Object.assign({},st.conv||{}); c[r.id]={conv:r.v.conv,canal:r.v.canal,prazo:r.v.prazo}; const adic=!!st.env&&r.v.conv==='Convidar';
      keep(self,gid,r.id,{conv:c,g2toast:'Convite atualizado: '+r.v.nome+(r.v.conv==='Convidar'?(' · '+r.v.canal+' · responder até '+r.v.prazo):' · não será convidado')+'.'+(adic?' Envie com o convite adicional.':'')}); }
    if(gid==='g_cmp'){ if(!cmpGestor(PF)){ keep(self,gid,r.id,{g2toast:'Escolher: ação de '+g2quem('gestor')+'. Nada foi alterado.'}); return; }
      const m=M(self); const it=m.items.find(x=>x.rid===r.id); if(!it) return; const p=it.props.find(x=>x.label===r.v.venc)||it.ch; const e=Object.assign({},st.esc||{});
      e[r.id]={f:p?p.f:'',ped:Number(r.v.ped),just:String(r.v.just||'')}; const ae=st.aprov&&st.aprov.estado;
      keep(self,gid,r.id,{esc:e,g2toast:'Escolha salva: '+it.nome+' · '+(p?p.nome:'')+' · '+qt(Number(r.v.ped),it.un)+'. Custos e pedidos recalculados.'
        +(ae==='pendente'?' O envio à Direção perdeu a validade: reenvie.':(ae==='devolvida'?' Reenvie à '+st.aprov.quem+'.':''))}); } }; }
function EXTRAVALS(self,v){ hooks(self);
  const st=self.state; const PF=g2perfil(); const C=self._cen||cenGet(); sx(self); const m=self._m||M(self); const apr=aprOf(st); const a=st.aprov||null;
  self.g2perfilFecha={dec5:null};   /* trocar o perfil fecha o motivo aberto pela Direção (revisão do CTL-3, achado 1) */
  // ---- endereço: #sol=…&saf=… abre o detalhe (vindo do Planejar safra); #pc=PC-… abre o pedido; SOL de outra safra ou inexistente: abre a da safra ou avisa ----
  const abrirHash=()=>{ let h=''; try{ h=decodeURIComponent(location.hash||''); }catch(e){ h=''; } const ms=/[#&]saf=([^&]+)/.exec(h), mi=/[#&]sol=([^&]+)/.exec(h), mp=/[#&]pc=([^&]+)/.exec(h);
    if(mp){ setTimeout(()=>{ self.setState({sec:2}); setTimeout(()=>{ const r=(GR('g_ped').rows||[]).find(x=>x.id===mp[1]); if(r) g2open(self,GR('g_ped'),r.id,null); },0); },0); return; }
    if(!ms&&!mi) return;
    let sid=ms?ms[1]:null; if(!sid&&mi){ const f=safras().find(z=>{ const y=solDe(z.id); return y&&y.sol.id===mi[1]; }); if(f) sid=f.id; }
    const s=sid?safras().find(z=>z.id===sid):null; const x=s?solDe(s.id):null;
    if(x){ const outra=!!(mi&&mi[1]!==x.sol.id); const msg=outra?(mi[1]+' não é a solicitação da '+x.nome+': aberta a '+x.sol.id+'.'):(x.sol.id+' aberta · origem: '+x.origem.t+'.');
      setTimeout(()=>{ if(self.state.saf!==x.safra) abrirSol(self,x.safra,{g2toast:msg}); else if(outra) toast(self,msg); hashSync(x.safra,x); },0); return; }
    if(s&&s.id==='S2526'){ setTimeout(()=>self.setState({sec:2,g2toast:s.nome+' encerrada: '+CD.sol2526+' concluída, pedidos em Acompanhe pedidos.'}),0); return; }
    setTimeout(()=>self.setState({g2toast:(mi?mi[1]:(s?s.nome:'A safra do endereço'))+(s?' ainda não tem solicitação: envie a demanda no Planejar safra.':' não foi encontrada.')}),0); };
  if(!self.__hashIni){ self.__hashIni=1; abrirHash(); try{ window.addEventListener('hashchange',abrirHash); }catch(e){} }
  // ---- seções: Atenda solicitações (lista ou detalhe) · Acompanhe pedidos ----
  const sec=st.sec||1; v.s1=sec===1; v.s2=sec===2;
  g2secoes(self,v,'stp',2,sec,{},(i)=>{ if(i===1&&self.state.saf) voltarLista(self,{sec:1}); else g2etapa(self,{sec:i}); });
  const nAg=(GR('g_sol').rows||[]).filter(r=>cmpDirecao(PF)?r.v.sit==='Aguardando Direção':(cmpGestor(PF)&&['A cotar','Justificar','Devolvida','Pronta para decidir'].indexOf(r.v.sit)>=0)).length;
  const nPd=(GR('g_ped').rows||[]).filter(r=>['Atrasado','Chega depois da falta','Aguarda confirmação'].indexOf(r.v.sit)>=0).length;
  [[nAg,cmpDirecao(PF)?' aguardando você':' a mover'],[nPd,' a acompanhar']].forEach(([n,t],i)=>{ v['stp'+(i+1)+'_cnt']=n?n+t:''; v['stp'+(i+1)+'_hasCnt']=!!n; });
  // a Direção abre a lista no que aguarda ela ("Aguardando você"), uma vez por perfil
  if(self.__qfPf!==PF.k){ self.__qfPf=PF.k; const qv=g2st(self,'g_sol').qv||''; if(cmpDirecao(PF)&&nAg) setTimeout(()=>g2set(self,'g_sol',{qv:'Aguardando Direção'}),0); else if(qv==='Aguardando Direção') setTimeout(()=>g2set(self,'g_sol',{qv:''}),0); }
  const det=sec===1&&!!SX; v.lista=sec===1&&!SX; v.det=det; const fase=!SX?'':(m.env?'decida':'cote'); v.cote=det&&fase==='cote'; v.decida=det&&fase==='decida';
  v.ctx_faz='Fazenda '+(((safras().find(s=>s.id===st.saf)||{}).faz)||'Santa Rita');
  // ---- detalhe: faixa Veio de → Está → Falta → Próxima ação (um só link de origem) ----
  const e=SX?estado(SX,m,st):{t:'',c:'gray',falta:''}; const stale=!!(a&&a.estado==='pendente'&&a.sig!==m.sig);
  const devA=!!(a&&a.estado==='devolvida'), recA=!!(a&&a.estado==='recusada'); const mud=!!(a&&a.sig!==m.sig);
  v.fx_sol=SX?SX.sol.id:''; v.fx_orig=SX?SX.origem.t:''; v.fx_orig_h=SX?SX.origem.h:'SAF.dc.html'; v.fx_est=e.t;
  v.fx_est_st='display:inline-flex;padding:2px 9px;border-radius:999px;font-weight:700;font-size:12px;'+({green:'background:#E4F3E9;color:#1E7A4C;',red:'background:#FDE8E6;color:#B42318;',yellow:'background:#FFF3D6;color:#8A5A00;',blue:'background:#E3F0FB;color:#1E5F8F;'}[e.c]||'background:#EEF1EE;color:#5B6660;');
  v.fx_falta=stale?'reenviar à Direção (a compra mudou)':e.falta;
  v.cmp_tit=apr?'Pedidos emitidos · propostas escolhidas':'Propostas por grupo e insumo';
  // ---- alçada numa linha e prévia dos pedidos (visível antes do toque que emite) ----
  const limTxt=(ix)=>CD.alcada[ix].ate===null?('acima de '+rs(CD.alcada[ix-1].ate)):('até '+rs(CD.alcada[ix].ate));
  const pcs=apr?apr.pcs:m.pcs; const tot=apr?apr.total:m.total; let niT=CD.alcada.findIndex(x=>x.ate===null||tot<=x.ate+1e-9); if(niT<0) niT=CD.alcada.length-1;
  v.alc_on=v.decida&&m.nresp>0; v.alc_t='Total '+rs(tot)+' · '+pcs.length+(pcs.length===1?' pedido':' pedidos')+' · aprova: '+CD.alcada[niT].quem+' ('+limTxt(niT)+')'
    +(apr?(' · aprovada por '+apr.por+' em '+((apr.dec&&apr.dec.em)||apr.em)+' · emitidos '+pcIds(apr.pcs)):'')+(devA&&!mud?' · devolvida: '+a.motivo:'')+(recA&&!mud?' · recusada: '+a.motivo:'');
  v.alc_st='padding:8px 12px;border-radius:10px;font-size:13px;font-weight:700;'+(apr?'background:#E4F3E9;color:#1E7A4C;':((devA||recA)&&!mud?'background:#FDE8E6;color:#B42318;':'background:#E3F0FB;color:#1E5F8F;'));
  v.prev_on=v.decida&&m.nresp>0&&pcs.length>0; v.prev_tit=apr?'PEDIDOS EMITIDOS':'PEDIDOS QUE SERÃO EMITIDOS';
  v.prev_pcs=pcs.map(p=>({id:p.id,forn:p.nome,its:p.itens.length===1?p.itens[0].nome+' · '+qt(p.itens[0].ped,p.itens[0].un):p.itens.length+' insumos',val:rs(p.valor)}));
  v.conv_on=v.decida&&!!st.cmp_conv&&!apr;
  // ---- devolução ou recusa (Direção): motivo obrigatório ----
  const d5=st.dec5||null; v.d5_open=v.decida&&!!d5; v.d5_t=d5?(d5.tipo==='dev'?'Devolver à gestora: a compra volta para ajuste e precisa ser reenviada.':'Recusar: nada é contratado e a necessidade continua aberta.'):'';
  v.d5_mot=d5?(d5.motivo||''):''; v.d5_err=d5?(d5.err||''):''; v.d5_hasErr=!!(d5&&d5.err);
  v.d5_set=(ev)=>self.setState({dec5:Object.assign({},self.state.dec5,{motivo:ev.target.value,err:''})});
  // ---- formulário Convite: destinatário e escopo que o fornecedor vai ver ----
  const Fv=v.g_conv_F; const fm3=g2st(self,'g_conv').fm; if(Fv&&Fv.open&&fm3&&fm3.rid&&m.conv[fm3.rid]){ const c=m.conv[fm3.rid]; const d=fm3.draft||{};
    const its=m.items.filter(x=>x.gi===c.gi).map(x=>x.nome+' · '+qt(x.nec,x.un)).join('; ');
    const dest=d.conv==='Convidar'?((d.canal==='WhatsApp'?('WhatsApp '+c.f.whats):('e-mail '+c.f.email))+(c.f.contato?' ('+c.f.contato+')':'')):'não será convidado';
    Fv.sub=(m.env&&!c.enviado?'Convite adicional: os demais já receberam em '+m.env.em+'. ':'')+'Destinatário: '+dest+'. Itens do convite ('+c.g+'): '+its+'. O envio é simulado.'; Fv.savel='Salvar convite'; }
  const Fk=v.g_cmp_F; if(Fk&&Fk.open) Fk.savel='Salvar escolha';
  // ---- painel do pedido: confirmar com o fornecedor ou reprogramar (versão nova; a anterior fica guardada) ----
  ePainelPed(self,v,C,PF);
  // ---- área de ações: uma primária, a do estado; "‹ Solicitações" volta à lista (filtro e posição preservados) ----
  const ir=()=>voltarLista(self,{}); let A={};
  if(det){ A.volta={t:'‹ Solicitações',fn:ir,a:'voltar'};
    if(fase==='cote'){ A.prim=cmpGestor(PF)?{t:'Enviar '+m.nconv+(m.nconv===1?' convite':' convites')+' (simulado)',fn:()=>enviar(self,PF),a:'comando'}:null;
      if(!cmpGestor(PF)) A.nota='Cotar: ação de '+g2quem('gestor')+' (compras). Você vê os convites em consulta.'; }
    else if(apr){ A.nota='Pedidos '+pcIds(apr.pcs)+' emitidos: acompanhe a entrega em Acompanhe pedidos.'; A.sec={t:'Acompanhe pedidos ›',fn:()=>voltarLista(self,{sec:2}),a:'abrir'}; }
    else if(v.d5_open){ A.prim={t:d5.tipo==='dev'?'Devolver à gestora':'Recusar a compra',fn:()=>decidir(self,PF),a:'comando'}; A.sec={t:'Voltar à decisão',fn:()=>self.setState({dec5:null}),a:'voltar'}; }
    else if(cmpDirecao(PF)){ if(a&&a.estado==='pendente'&&a.sig===m.sig){ A.prim={t:'Aprovar e emitir '+m.pcs.length+(m.pcs.length===1?' pedido':' pedidos')+' · '+rs(m.total),fn:()=>aprovar(self,PF),a:'comando'};
        A.sec={t:'Devolver',fn:()=>self.setState({dec5:{tipo:'dev',motivo:'',err:''}}),a:'comando'}; A.ctx={t:'Recusar',fn:()=>self.setState({dec5:{tipo:'rec',motivo:'',err:''}})};
        A.nota='Enviada por '+(a.por||g2quem('gestor'))+' em '+a.em+'. Devolver e recusar pedem o motivo.'; }
      else A.nota='Nada aguarda a Direção nesta solicitação ('+e.t.toLowerCase()+').'; }
    else if(!cmpGestor(PF)) A.nota='Decidir a compra: '+g2quem('gestor')+' (até '+rs(CD.alcada[CD.perfil.idx].ate)+') ou a Direção (acima).';
    else if(!m.nresp){ A.nota='Aguardando propostas · 0 de '+m.esperadas+'. As respostas simuladas chegam sozinhas.'; }
    else if(m.nadic){ A.prim={t:'Enviar '+m.nadic+(m.nadic>1?' convites adicionais':' convite adicional')+' (simulado)',fn:()=>enviarAdic(self,PF),a:'comando'}; }
    else if(m.nresp<m.esperadas){ A.nota='Aguardando propostas · '+m.nresp+' de '+m.esperadas+'. As respostas simuladas chegam sozinhas.'; }
    else if(m.njust){ const it=m.items.find(x=>x.justPend); A.prim={t:'Justificar '+m.njust+(m.njust>1?' escolhas':' escolha'),fn:()=>openEsc(self,it.rid,null),a:'resolver'}; }
    else if(a&&a.estado==='pendente'&&a.sig===m.sig){ A.nota='Aguardando a Direção desde '+a.em+' (simulado). Mudar uma escolha invalida o envio.'; }
    else if(devA&&!mud){ const it=m.items.find(x=>x.ch)||m.items[0]; A.prim={t:'Ajustar escolhas',fn:()=>openEsc(self,it.rid,null),a:'resolver'}; A.nota='Devolvida pela Direção: '+a.motivo+'.'; }
    else if(recA&&!mud){ A.nota='Recusada pela Direção: '+a.motivo+'. Nada foi contratado; a necessidade continua aberta.'; A.sec={t:'Ver demanda no Planejar safra ›',fn:()=>{ location.href=SX.origem.h; },a:'abrir'}; }
    else if(m.dentro){ A.prim={t:'Aprovar e emitir '+m.pcs.length+(m.pcs.length===1?' pedido':' pedidos')+' · '+rs(m.total),fn:()=>aprovar(self,PF),a:'comando'}; }
    else A.prim={t:((stale||devA||recA)?'Reenviar à Direção · ':'Enviar à Direção · ')+rs(m.total),fn:()=>aprovar(self,PF),a:'comando'};
    if(fase==='decida'&&!apr&&cmpGestor(PF)&&!v.d5_open&&!A.sec) A.sec={t:st.cmp_conv?'Fechar convites':'Convidar outro fornecedor',fn:()=>self.setState({cmp_conv:!self.state.cmp_conv}),a:'comando'};
  }
  v.fx_prox=A.prim?A.prim.t:(A.nota?A.nota.split('.')[0]:'—');
  g2acoes(v,'aa',A);
  procGravar(self,m);
}
function ePainelPed(self,v,C,PF){ const F=v.g_ped_F; const fm=g2st(self,'g_ped').fm; if(!F||!F.open||!fm) return; const r=(GR('g_ped').rows||[]).find(x=>x.id===fm.rid); if(!r||!r.ped) return;
  const P=r.ped, x=P.x||{}; const modo=(fm.draft||{}).modo||'';
  const nfs=cmpRecebido(C,P.id); const prevs=x.prevs||[];
  const lin=['Origem: '+(P.orig||(P.p&&(P.p.sc||P.p.sol))||'—')+' · fornecedor '+(r.v.forn||'—'),'Previsão atual: '+brd(r.v.prev)+(prevs.length?' · antes: '+prevs.map(z=>brd(z.prev)+' ('+z.motivo+')').join('; '):'')]
    .concat(nfs.length?nfs.map(n=>'Recebido no Estoque: '+n.nf+' · '+qt(n.conf,n.un)+(n.quar?' · '+qt(n.quar,n.un)+' em quarentena aguardando laudo':'')):[])
    .concat(P.nfprev?['Nota prevista: '+P.nfprev]:[]);
  F.title='Pedido · '+P.id; F.sub=lin.join('\n');
  const acts=[]; (nfs.length?nfs:(P.nfprev?[{nf:P.nfprev}]:[])).forEach(n=>acts.push({t:'Ver recebimento '+n.nf+' no Estoque ›',h:'',go:()=>{ location.href='EST.dc.html#nf='+encodeURIComponent(n.nf); }}));
  if(r.ro||P.tipo==='2526'||P.tipo==='cen'){ F.acts=acts; F.hasActs=acts.length>0; return; }
  if(!cmpGestor(PF)){ F.sub+='\nReprogramar e confirmar: ação de '+g2quem('gestor')+' (compras).'; F.acts=acts; F.hasActs=acts.length>0; return; }
  if(modo==='conf'){ F.savel='Confirmar com '+(r.v.forn||'o fornecedor')+' (simulado)'; acts.unshift({t:'Reprogramar '+P.id+' ›',h:'',go:()=>ePedModo(self,'rep')}); }
  else { F.savel='Reprogramar '+P.id; if(P.tipo==='sol'&&!x.conf) acts.unshift({t:'‹ Confirmar com o fornecedor',h:'',go:()=>ePedModo(self,'conf')}); }
  F.acts=acts; F.hasActs=acts.length>0; }
function ePedModo(self,modo){ const fm=g2st(self,'g_ped').fm; if(!fm) return; const d=Object.assign({},fm.draft,{modo}); g2set(self,'g_ped',{fm:Object.assign({},fm,{draft:d,orig:Object.assign({},d),errs:{}})}); }
// abrir o pedido: confirmar (pedido novo sem confirmação) ou reprogramar; recebido e consulta abrem só para ler
const _g2open0=g2open;
g2open=function(self,sp,rid,e){ if(sp.id!=='g_ped') return _g2open0(self,sp,rid,e);
  if(e&&e.target&&e.target.closest&&e.target.closest('a,button,input,select,textarea,label,[data-noedit]')) return;
  const r=g2find(sp.rows||[],rid); if(!r||!r.ped) return; const P=r.ped, x=P.x||{}; const ro=!!r.ro||P.tipo==='2526'||P.tipo==='cen'||r.v.sit==='Recebido'||!cmpGestor(g2perfil());
  const modo=ro?'':((P.tipo==='sol'&&!x.conf)?'conf':'rep'); const d={modo,prev:'',obs:''};
  g2set(self,'g_ped',{fm:{rid,draft:d,orig:Object.assign({},d),errs:{},warn:false,ro,isNew:false,mode:'form'},fl:null,fmc:null}); };
const _g2save0=g2save;
g2save=function(self,sp){ if(sp.id!=='g_ped') return _g2save0(self,sp); const fm=g2st(self,'g_ped').fm; if(!fm||fm.ro) return; const r=(sp.rows||[]).find(x=>x.id===fm.rid); if(!r||!r.ped) return;
  const P=r.ped, x=P.x||{}, d=fm.draft||{}; const PF=g2perfil(); if(!cmpGestor(PF)){ toast(self,'Reprogramar e confirmar: ação de '+g2quem('gestor')+'. Nada foi alterado.'); return; }
  if(d.modo==='conf'){ if(x.conf){ toast(self,P.id+' já confirmado · nada registrado de novo.'); g2set(self,'g_ped',{fm:null}); return; }
    pedPut(P.id,{conf:true,confEm:'23/09/2026 '+cenAgora(),confPor:g2ator(PF,'gestor')}); g2set(self,'g_ped',{fm:null,fl:P.id});
    self.setState({cenrev:Date.now(),g2toast:'Confirmação de '+r.v.forn+' registrada para '+P.id+' (simulada · nenhuma mensagem real enviada) · previsão '+brd(r.v.prev)+'.'}); return; }
  const errs={}; const nv=String(d.prev||''); const mot=String(d.obs||'').trim();
  if(!/^\d{4}-\d{2}-\d{2}$/.test(nv)||nv<CD.hojeIso) errs.prev='Use uma data a partir de hoje (23/09/2026).'; else if(nv===r.v.prev) errs.prev='É a previsão atual: informe a nova data.';
  if(!mot) errs.obs='Informe o motivo: a versão anterior fica guardada com ele (RF-SUP-012).';
  if(Object.keys(errs).length){ g2set(self,'g_ped',{fm:Object.assign({},fm,{errs})}); return; }
  const prevs=(x.prevs||[]).concat([{prev:r.v.prev,motivo:mot,em:'23/09/2026 '+cenAgora(),por:g2ator(PF,'gestor')}]);
  pedPut(P.id,{prev:nv,prevs}); g2set(self,'g_ped',{fm:null,fl:P.id});
  const falt=r.v.falta; self.setState({cenrev:Date.now(),g2toast:'Previsão de '+P.id+' reprogramada para '+brd(nv)+' (versão '+(prevs.length+1)+'; a anterior, '+brd(r.v.prev)+', fica guardada). O Estoque passa a esperar esta data.'
    +(falt&&nv>falt?' Atenção: nova data depois da falta de '+brd(falt)+'.':'')}); };
'''
