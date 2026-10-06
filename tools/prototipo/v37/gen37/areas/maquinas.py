# -*- coding: utf-8 -*-
"""Manutenção — Planos de manutenção (PM.dc.html, 3 etapas como os Planos agronômicos) e o processo MA-01..MA-05 por links:
MA-01 Confira os ativos › MA-02 Registre inspeções › MA-03 Programe as preventivas (Vencimentos e paradas) › MA-04 Execute as ordens
(+ MA-04det OM-0233) › MA-05 Acompanhe abastecimentos (cap. 47, 53–54).

Pedido do proprietário (02/10/2026): cadastro dos planos de manutenção periódica que giram as preventivas.
- Planos (PM): serviços com gatilhos h/km/dias ("o que vencer primeiro"), tolerância, checklist, peças do estoque, tempo e especialidade;
  edição vira rascunho v(n+1); publicar cria a versão; ordens abertas seguem na versão em que nasceram.
- Cenário compartilhado (dados_manutencao.JS, localStorage 'talhao-os-manutencao-v1'): o mesmo cálculo de vencimento alimenta PM,
  MA-01 (próxima manutenção), MA-03 (vencimentos) e MA-04 (ordens); MA-05 grava a leitura do contador; concluir a OM fecha o ciclo.
- MA-03 deixou de se chamar "Plano de manutenção" (virou "Vencimentos e paradas") para não haver dois itens de menu com o mesmo nome.
- Identidade dos ativos = CD-03 (dados_cad.ATIVOS) + Comboio CB-01; a colhedora é a Axial-Flow 7250 (antes "S680", cadastro paralelo).
Passo 4 (03/10): telas sem subtítulo, resumo de seção ou rodapé explicativo; grades cabem em 1.280 px; F5 reabre plano (#PM-xx) e
ordem (#OM-xxxx); painéis prendem Tab e fecham com Esc de qualquer lugar; MA-03 move a OM-0234 para fora do conflito e grava a proposta.
observacoes: OM-0233, Trator T1, OS-0420 (30 ha feitos, saldo 70 ha), OS-0431 e INSP-105 continuam como em dados.py/planejamento.py;
MF 7719 vence em 3.043 h ≈ 28/09 (11 h/dia); custo-hora de oficina R$ 320/h (hipótese).
"""
import json, re, os
from engine import (grid,kpis,chip,btn,icon,esc,msgbtn,drawer_button,stepper,Pt,section,
                    INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAYS,DISP,BTN_ST,EXTRA,EXTRAJS,_MINI,_MINIP)
import engine as E
from ui37 import shell37, steps_bar, steps_state, continuity, HEIGHTS37, PARENT37
import dados as D
import dados_manutencao as DM

H=lambda s: '{{'+s+'}}'
F=lambda: H('false')
T=lambda: H('true')
def IF(cond,html,dflt=False): return f'<sc-if value="{H(cond)}" hint-placeholder-val="{T() if dflt else F()}">{html}</sc-if>'
def FOR(lst,as_,html,n=2): return f'<sc-for list="{H(lst)}" as="{as_}" hint-placeholder-count="{n}">{html}</sc-for>'

ETAPAS=[('Confira os ativos','MA-01.dc.html',''),('Registre inspeções','MA-02.dc.html',''),
        ('Programe as preventivas','MA-03.dc.html','Conflito de janela'),('Execute as ordens','MA-04.dc.html','T1 bloqueado'),
        ('Acompanhe abastecimentos','MA-05.dc.html','')]
def faixa(i):
    return steps_bar([dict(t=t,href=h,why=w,tip=(t+(' · '+w if w else ''))) for t,h,w in ETAPAS],current=i,label='Telas da manutenção')   # telas irmãs (trabalho paralelo): navegação, não etapas
SUBST='Proposto · OS-0420 saldo 70 ha · aguarda PCP'
OS420=next(o for o in D.OS if o['id']=='OS-0420')
OS431=D.ORDEM['OS-0431']

# identidade única dos ativos (CD-03 + CB-01): nome exibido = nome · modelo para tratores (como D.OM['ativo'] e D.OM['substituto'])
def nome(aid):
    a=DM.ATIVOS[aid]; return a['nome']+(' · '+a['modelo'] if a['classe']=='Trator' else '')
COLH=nome('a08'); PULV=nome('a05'); PLANT=nome('a06'); BOMBA2=nome('a11'); PACK=nome('a13'); SILO=nome('a14')
assert nome('a01')==D.OM['ativo'] and nome('a02')==D.OM['substituto'], 'identidade dos tratores divergiu de dados.OM'

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
function ma_chipSt(c){ const k=G2C[c]||G2C.gray; return 'display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+k[0]+';background:'+k[1]+';'; }
function ma_dotSt(c){ const k=G2C[c]||G2C.gray; return 'width:6px;height:6px;border-radius:999px;flex-shrink:0;background:'+k[0]+';'; }
// painel modal: Tab e Shift+Tab giram dentro do painel; foco fora dele volta para dentro
function ma_focaveis(root){ return root?[...root.querySelectorAll('button,a[href],input,select,textarea,[tabindex]:not([tabindex="-1"])')].filter(x=>!x.disabled&&x.getClientRects().length):[]; }
function ma_trap(e,root){ if(!e||e.key!=='Tab'||!root) return; const f=ma_focaveis(root); if(!f.length) return; const a=document.activeElement;
  if(!root.contains(a)){ e.preventDefault(); f[0].focus(); return; }
  if(e.shiftKey&&(a===f[0]||a===root)){ e.preventDefault(); f[f.length-1].focus(); } else if(!e.shiftKey&&a===f[f.length-1]){ e.preventDefault(); f[0].focus(); } }
// Esc e Tab valem também com o foco fora do painel aberto (get() devolve {root, close} do painel aberto ou null)
function ma_modalDoc(self,get){ if(self.__maModal) return; self.__maModal=true;
  try{ document.addEventListener('keydown',(e)=>{ const m=get(); if(!m||!m.root) return; if(m.root.contains(e.target)) return;
    if(e.key==='Escape'){ e.preventDefault(); m.close(); } else if(e.key==='Tab') ma_trap(e,m.root); }); }catch(err){} }
'''
# linha de vencimento (MA-03 e PM): mesmas partes de célula nas duas telas
JSVENC=r'''
function ma_linhaVenc(c,l,servComPlano){ const a=l.a, x=l.x, s=l.s;
  if(!s) return {id:l.vk+'#',v:{prox:null},s:{ativo:manNome(a),serv:'—',sit:x.sit},p:{ativo:[{k:'b',t:a.nome},{k:'br',t:''},{k:'mut',t:a.modelo}],serv:[{k:'mut',t:'—'}],
    leit:[{k:'txt',t:manLeitTxt(a)},{k:'br',t:''},{k:'mut',t:'marco '+manBr(l.ref.data)}],prox:[{k:'mut',t:'—'}],sit:[{k:'chip',t:x.sit,c:'gray'}],acao:[{k:'mut',t:'—'}]}};
  const g=x.gats[x.prim]||{};
  const sv=servComPlano?[{k:'link',t:l.p.id+' · '+s.nome,h:'PM.dc.html#'+l.p.id},{k:'br',t:''},{k:'mut',t:manGatTxt(s)}]:[{k:'b',t:s.nome},{k:'br',t:''},{k:'mut',t:manGatTxt(s)}];
  const ult='última '+manBr(l.ref.data)+((l.ref.leit!==null&&l.ref.leit!==undefined&&a.un)?' · '+manQ(l.ref.leit,a.un):'')+(l.ref.om?' · '+l.ref.om:'');
  const px=[{k:'txt',t:manProxTxt(c,x)}].concat(manPrimTxt(x)?[{k:'br',t:''},{k:'mut',t:manPrimTxt(x)}]:[]);
  const sl=[{k:'chip',t:manSitTxt(c,x),c:MAN_SITC[x.sit]||'gray'}].concat(manSelosLinha(c,l).map(z=>({k:'chip',t:z.t,c:z.c})))
    .concat(a.suspeita?[{k:'br',t:''},{k:'link',t:'Confirmar leitura',h:'MA-05.dc.html'}]:[]);
  let ac; if(l.om) ac=[{k:'link',t:l.om.id+' · '+l.om.etapa,h:'MA-04.dc.html#'+l.om.id}].concat(manFalta(c,l.om).length?[{k:'br',t:''},{k:'chip',t:'Falta peça',c:'red'}]:[]);
  else if(l.dup) ac=[{k:'link',t:l.dup.id+' · '+l.dup.etapa,h:'MA-04.dc.html#'+l.dup.id},{k:'br',t:''},{k:'mut',t:'pelo '+l.dup.pid}];
  else if(manDevida(l)) ac=[{k:'act',t:'Gerar ordem',fn:'gerar:'+l.vk+'#'+l.sid}]; else ac=[{k:'mut',t:'—'}];
  return {id:l.vk+'#'+l.sid,v:{prox:(g.dd===undefined?null:g.dd)},s:{ativo:manNome(a),serv:l.p.id+' '+s.nome,leit:manLeitTxt(a)+' '+ult,prox:manProxTxt(c,x),sit:x.sit,acao:l.om?l.om.id:''},
    p:{ativo:[{k:'b',t:a.nome},{k:'br',t:''},{k:'mut',t:a.modelo}],serv:sv,leit:[{k:'txt',t:manLeitTxt(a)},{k:'br',t:''},{k:'mut',t:ult}],prox:px,sit:sl,acao:ac}}; }
function ma_gerarV(self,v){ v.gerar=(arg)=>{ const i=arg.lastIndexOf('#'); const vk=arg.slice(0,i), sid=arg.slice(i+1); manMudar(self,c=>manGerar(c,vk,sid)); }; }
'''
# larguras para caber em 1.280 px (área da grade ≈ 944 px; cada coluna soma ≈ 16 px de respiro)
VENC_COLS=[dict(k='ativo',l='Ativo',w=130),dict(k='serv',l='Serviço',w=160),dict(k='leit',l='Leitura · última',w=150),
           dict(k='prox',l='Próximo vencimento',t='num',w=130),dict(k='sit',l='Situação',w=160),dict(k='acao',l='Ordem',w=115)]

def _restaurar(pre='ma'):
    """Ação discreta: volta o cenário da manutenção (planos, vencimentos, ordens e leituras) ao início, com confirmação."""
    lk=f'border: 0; background: transparent; color: {MUTED}; font-family: inherit; font-size: 12px; font-weight: 600; cursor: pointer; text-decoration: underline; text-underline-offset: 3px; padding: 4px;'
    return (f'<div style="display: flex; justify-content: flex-end; align-items: center; gap: 8px; flex-wrap: wrap;">'
            + IF(f'{pre}_rst_no',f'<button type="button" onClick="{H(pre+"_rst")}" style="{lk}">Restaurar demonstração</button>',True)
            + IF(f'{pre}_rst_ask',f'<span style="font-size: 12px; color: {MUTED};">Volta planos, vencimentos, ordens e leituras ao início.</span>'
                 f'<button type="button" onClick="{H(pre+"_rst_ok")}" style="{_MINI} color: {RED}; border-color: {RED};">Restaurar</button><button type="button" onClick="{H(pre+"_rst_cancel")}" style="{_MINI}">Manter</button>')
            + '</div>')
JSRST=r'''
function ma_rstV(self,v,pre){ const ask=!!self.state[pre+'_ask']; v[pre+'_rst_no']=!ask; v[pre+'_rst_ask']=ask;
  v[pre+'_rst']=()=>self.setState({[pre+'_ask']:true}); v[pre+'_rst_cancel']=()=>self.setState({[pre+'_ask']:false});
  v[pre+'_rst_ok']=()=>{ manReset(self); const z={[pre+'_ask']:false,pan:null,pav:false}; self.setState(z); }; }
'''

def _status_dyn(fname,hole):
    """troca o selo fixo do cabeçalho por um selo com a cor calculada na tela (hole_st / hole_dot)."""
    import ui37
    p=os.path.join(E.P,fname); s=open(p,encoding='utf-8').read(); old=ui37.chip(H(hole),'red')
    assert s.count(old)==1, 'selo do cabeçalho não encontrado em '+fname
    open(p,'w',encoding='utf-8').write(s.replace(old,f'<span style="{H(hole+"_st")}"><span style="{H(hole+"_dot")}"></span>{H(hole)}</span>'))

# =====================================================================================
def ma01():
    fn='MA-01.dc.html'; HEIGHTS37[fn]=1000
    AG={'a01':('Agenda retirada','gray'),'a02':(SUBST,'yellow'),'a05':('Comprometido · OS-0421','gray'),
        'a11':('Comprometido · OS-0419','gray'),'a12':('Comprometido · OS-0423','gray')}
    UTIL={'a01':360,'a02':440,'a03':300,'a04':120,'a05':515,'a06':74,'a07':40,'a08':118,'a09':60,'a10':25,
          'a15':330,'a11':341,'a12':280,'a13':273,'a14':186,'cb01':210}   # horas trabalhadas em 30 d
    RESP={'a01':'Zé (mecânico)','a02':'Zé (mecânico)','a05':'Zé (mecânico)','a11':'Equipe elétrica','a15':'Equipe elétrica','a12':'Equipe elétrica'}
    rows=[]
    for aid in DM.ORDEM_ATIVOS:
        a=DM.ATIVOS[aid]; ag=AG.get(aid,('Livre','green'))
        v=dict(nome=nome(aid),cat=a['classe'],local=a['local'],hor=(a['leit']['val'] if a['leit'] else ''),un=a['un'],cond=a['cond'],
               ag=ag[0],agc=ag[1],util=round(UTIL[aid]*100/620),resp=RESP.get(aid,'PCM'),motr='',motb='')
        if aid=='a01': v['motb']='Pressão hidráulica baixa · SM-0147 e INSP-105'
        if aid=='a11': v['motr']='Pressão baixa recorrente · operar só com monitoramento'
        rows.append(dict(id=aid,v=v,s={},p={}))
    LOCAIS=sorted({DM.ATIVOS[x]['local'] for x in DM.ORDEM_ATIVOS})
    g_at=grid([dict(k='ativo',l='Ativo · local · contador',w=170),
               dict(k='cond',l='Condição',chips={'Apto':'green','Restrito · monitorado':'yellow','Bloqueado':'red'}),
               dict(k='agenda',l='Agenda',w=170),dict(k='eleg',l='Elegível'),dict(k='prox',l='Próxima manutenção',w=160),
               dict(k='util',l='Uso 30 d',t='num',a='r',u='%')],rows,
       edit=dict(m='form',title='Ativo',sub='O Trator T1 só é liberado pela OM-0233, com teste aprovado.',
            fields=[dict(k='local',l='Local',t='sel',opts=LOCAIS,req=True),
                    dict(k='hor',l='Contador',t='num',ro=True,help='Vem dos abastecimentos, apontamentos e telemetria; troca de contador exige evento próprio.'),
                    dict(k='cond',l='Condição técnica',t='sel',opts=['Apto','Restrito · monitorado','Bloqueado'],req=True),
                    dict(k='motr',l='Motivo da restrição',t='area',req=True,cond=dict(k='cond',eq='Restrito · monitorado')),
                    dict(k='motb',l='Motivo do bloqueio',t='area',req=True,cond=dict(k='cond',eq='Bloqueado')),
                    dict(k='resp',l='Responsável técnico',t='sel',opts=['Zé (mecânico)','Rui','Equipe elétrica','PCM'],req=True)]),
       gid='g_at',total=False,qf=dict(k='cond',l='condição técnica'))
    UT=[('Tratores',['a01','a02','a03','a04']),('Pulverizadores',['a05']),('Colheita e implementos',['a06','a08','a07','a10']),
        ('Fixos (irrigação, beneficiamento, armazenagem)',['a15','a11','a12','a13','a09','a14']),('Veículos',['cb01'])]
    utrows=[]
    for i,(g,ids) in enumerate(UT):
        n=len(ids); ht=sum(UTIL[x] for x in ids)
        utrows.append(dict(id=f'u{i}',v=dict(grupo=g,n=n,ht=ht,hd=n*620,ut=round(ht*100/(n*620))),s={},p={},
             o=[dict(t=f'{nome(x)} · {UTIL[x]} h de 620 h ({round(UTIL[x]*100/620)}%)') for x in ids]+[dict(t=f'Soma: {ht} h ÷ ({n} × 620 h) — nunca média de médias')]))
    g_ut=grid([dict(k='grupo',l='Grupo/classe',w=300),dict(k='n',l='Ativos',t='num',a='r'),dict(k='ht',l='Horas trabalhadas 30 d',t='num',a='r',u='h'),
               dict(k='hd',l='Horas disponíveis 30 d',t='num',a='r',u='h'),dict(k='ut',l='Utilização',t='num',a='r',u='%')],utrows,
       edit=dict(m='origin',title='Utilização do grupo',fields=[dict(k='grupo',l='Grupo',ro=True),dict(k='ut',l='Utilização',t='num',u='%',ro=True)]),
       search=False,gid='g_ut',total=False)
    sel=(f'<label style="display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; font-weight: 700; color: {MUTED};">Tarefa'
         f'<select aria-label="Tarefa para calcular a elegibilidade" title="Escolha a tarefa para calcular a elegibilidade" value="{H("tar_v")}" onChange="{H("tar_set")}" '
         f'style="font-family: inherit; font-size: 12.5px; font-weight: 600; padding: 6px 8px; border: 1px solid {LINE}; border-radius: 8px; background: {SURF}; color: {INK};">'
         f'<option value="pl">Plantio Soja 58 W · OS-0420</option><option value="pu">Pulverização fungicida · OS-0421</option><option value="no">Sem tarefa</option></select></label>')
    corpo=(kpis([('ATIVOS APTOS',H('k_aptos'),'condição técnica'),('BLOQUEADOS · RESTRITOS',H('k_br'),H('k_brd')),
                 ('MANUTENÇÃO VENCIDA',H('k_ven'),H('k_vend')),('ELEGÍVEIS P/ TAREFA',H('k_eleg'),H('k_elegd'))])
      + section('Quadro de ativos','',
                [sel],g_at)
      + section('Utilização por grupo','','',g_ut,state='gray'))
    EXTRAJS[0]=DM.js_prefixo()+JSBASE+r'''
const MA_ELEG={pl:{a01:1,a02:1,a06:1},pu:{a05:1}};
const MA_TAR={pl:'plantio Soja 58 W · OS-0420',pu:'pulverização fungicida · OS-0421',no:'escolha uma tarefa'};
// próxima manutenção do ativo: corretiva aberta primeiro; depois o vencimento mais urgente dos planos (ou "Sem plano")
function ma_prox(c,aid){ const ord={'Vencida':0,'Vence em breve':1,'Em dia':2}; const parts=[]; let s='';
  Object.values(c.oms).filter(o=>o.aid===aid&&o.tipo!=='Preventiva'&&['A liberar','Liberadas','Em execução'].indexOf(o.etapa)>=0).forEach(o=>{
    parts.push({k:'link',t:o.id+' · '+(o.tipo==='Corretiva'?'corretiva ':'')+o.etapa.toLowerCase(),h:o.det||('MA-04.dc.html#'+o.id)}); parts.push({k:'br',t:''}); s+=o.id+' '; });
  const a=c.ativos[aid]; if(a&&a.suspeita){ parts.push({k:'chip',t:'Leitura a confirmar',c:'yellow'}); parts.push({k:'link',t:'Confirmar',h:'MA-05.dc.html'}); parts.push({k:'br',t:''}); s+='Leitura a confirmar '; }
  const ls=manLinhas(c).filter(l=>l.aid===aid&&l.s);
  if(!ls.length){ const vl=manLinhas(c).find(l=>l.aid===aid);
    if(vl){ parts.push({k:'chip',t:'Aguarda publicar',c:'gray'}); parts.push({k:'link',t:vl.pid,h:'PM.dc.html#'+vl.pid}); return {p:parts,s:s+'Aguarda publicar'}; }
    // plano criado (aplica-se ao ativo) mas ainda sem vínculo: o próximo passo é vincular, não criar outro plano
    const pc=a?Object.values(c.planos).find(p=>p.estado!=='Inativo'&&manCabe(c,p,a)):null;
    if(pc){ parts.push({k:'chip',t:'Sem vínculo',c:'gray'}); parts.push({k:'link',t:'Vincular · '+pc.id,h:'PM.dc.html#'+pc.id}); return {p:parts,s:s+'Sem vínculo'}; }
    parts.push({k:'chip',t:'Sem plano',c:'gray'}); parts.push({k:'link',t:'Criar plano',h:'PM.dc.html#novo:'+aid}); return {p:parts,s:s+'Sem plano'}; }
  if(ls.every(l=>l.x.sit==='Plano inativo')){ parts.push({k:'chip',t:'Plano inativo',c:'gray'}); parts.push({k:'link',t:ls[0].pid,h:'PM.dc.html#'+ls[0].pid}); return {p:parts,s:s+'Plano inativo'}; }
  const k=(l)=>{ const o=ord[l.x.sit]; return o===undefined?3:o; }; const dd=(l)=>{ const g=l.x.gats[l.x.prim]; return g?g.dd:Infinity; };
  ls.sort((a,b)=>(k(a)-k(b))||(dd(a)-dd(b))); const l=ls[0];
  parts.push({k:'chip',t:l.x.sit,c:MAN_SITC[l.x.sit]||'gray'}); parts.push({k:'txt',t:l.s.nome+' · '+manProxTxt(c,l.x)});
  if(l.om){ parts.push({k:'br',t:''}); parts.push({k:'link',t:l.om.id+' · '+l.om.etapa.toLowerCase(),h:'MA-04.dc.html#'+l.om.id}); }
  return {p:parts,s:s+l.x.sit+' '+l.s.nome}; }
function PREVALS(self,v){ manOuvir(self); const c=manGet(); const tar=self.state.tar||'pl'; const rows=ma_R(self,'g_at');
  let ap=0,br=[],ven=[],el=0;
  rows.forEach(r=>{ const x=r.v; const cn=x.cond||'Apto'; const at=c.ativos[r.id];
    if(at&&at.leit) x.hor=at.leit.val;   // contador = última leitura do cenário (abastecimento, OM, telemetria)
    r.p.ativo=[{k:'b',t:x.nome},{k:'br',t:''},{k:'mut',t:x.cat+' · '+x.local+' · '+(x.hor!==''&&x.hor!==undefined&&x.hor!==null?ma_nf(x.hor)+' '+x.un:'sem contador')}]; r.s.ativo=x.nome+' · '+x.cat+' · '+x.local;
    r.p.cond=[ma_chip(cn,cn==='Apto'?'green':(cn==='Bloqueado'?'red':'yellow'))]; r.s.cond=cn;
    const ag=(cn==='Bloqueado')?['Agenda retirada','gray']:[x.ag,x.agc]; const ai=String(ag[0]).indexOf(' · ');
    r.p.agenda=ai>0?[ma_chip(ag[0].slice(0,ai),ag[1]),{k:'br',t:''},{k:'mut',t:ag[0].slice(ai+3)}]:[ma_chip(ag[0],ag[1])]; r.s.agenda=ag[0];
    let e; if(tar==='no') e=['—',null]; else if(cn==='Bloqueado') e=['Não elegível','red']; else if((MA_ELEG[tar]||{})[r.id]) e=['Elegível','green']; else e=['Não elegível','gray'];
    r.p.eleg=e[1]?[ma_chip(e[0],e[1])]:[{k:'mut',t:'—'}]; r.s.eleg=e[0];
    const px=ma_prox(c,r.id); r.p.prox=px.p; r.s.prox=px.s;
    if(cn==='Apto') ap++; else br.push(x.nome.split(' · ')[0]+(cn==='Bloqueado'?' (bloqueado)':' (restrito)'));
    if(px.s.indexOf('Vencida')>=0) ven.push(x.nome.split(' · ')[0]); if(e[0]==='Elegível') el++; });
  v.k_aptos=ap+' de '+rows.length; v.k_br=String(br.length); v.k_brd=br.join(' · ')||'nenhum';
  v.k_ven=String(ven.length); v.k_vend=ven.join(' · ')||'nenhuma'; v.k_eleg=String(el); v.k_elegd=MA_TAR[tar]; }
function EXTRAVALS(self,v){ v.tar_v=self.state.tar||'pl'; v.tar_set=(e)=>self.setState({tar:e.target.value});
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_at'||!r) return; const cn=r.v.cond;
    if(r.id==='a01' && cn!=='Bloqueado'){ r.v.cond='Bloqueado'; r.s.cond='Bloqueado';
      self.setState({g2toast:'Trator T1 continua Bloqueado: a liberação só sai da OM-0233, com teste aprovado e decisão de aptidão. Local e responsável foram salvos.'}); return; }
    if(cn==='Bloqueado') self.setState({g2toast:r.v.nome+' bloqueado · motivo e responsável registrados · alocações que usam o ativo ficam impedidas e o PCP é avisado (simulado)'});
    else if(cn.indexOf('Restrito')===0) self.setState({g2toast:r.v.nome+' restrito · uso só com monitoramento · alocações afetadas avisadas (simulado)'});
    else self.setState({g2toast:'Salvo · '+r.v.nome+' Apto'}); }; }
'''
    shell37('MA-01','Ativos e disponibilidade',corpo,
      status=('1 bloqueado · 1 restrito','red'),primary='Registrar inspeção',primary_href='MA-02.dc.html',steps=faixa(1))

# =====================================================================================
def ma02():
    fn='MA-02.dc.html'; HEIGHTS37[fn]=1000
    abrir=[Pt.cta('Abrir ordem','MA-04det.dc.html',True)]
    CS=[
     dict(id='c1',caso='INSP-105',tipo='Checklist da manutenção',om='OM-0233',ativo=D.OM['ativo'],sint='Pré-uso 23/09 07:10: pressão hidráulica abaixo da faixa · bloqueio executado antes do início',
          crit='Alta',cont=4312,evid='checklist + manômetro',rec='Bloqueado',resp='Zé (mecânico)',pa=abrir),
     dict(id='c2',caso='SM-0147',tipo='Falha em campo',om='OM-0233',ativo=D.OM['ativo'],sint=D.OM['causa']+' · parou aos 30 ha da OS-0420',
          crit='Alta',cont=4312,evid='telemetria + foto',rec='Bloqueado',resp='PCM',pa=abrir),
     dict(id='c3',caso='SM-0152',tipo='Alerta agregado',om='OM-0228',ativo=BOMBA2,sint='Pressão baixa 3× esta noite · caso único, sem ordem duplicada',
          crit='Alta',cont=8914,evid='3 leituras de telemetria',rec='Restrito · monitorado',resp='PCM',pa=[Pt.link('Ver OM-0228','MA-04.dc.html#OM-0228')]),
     dict(id='c4',caso='INSP-104',tipo='Checklist do operador',om='',ativo=D.OM['substituto'],sint='Vazamento leve em mangueira',
          crit='Média',cont=2988,evid='foto',rec='Apto · reparo na preventiva',resp='Mecânico',
          pa=[{'k':'act','t':'Vincular à OM-0234','fn':'vinc:c4'},Pt.br(),Pt.act('Triar achado','Triado: criticidade Média · reparo entra na preventiva · condição Apto mantida')],
          pb=[Pt.link('Ver OM-0234','MA-04.dc.html#OM-0234')]),
     dict(id='c5',caso='SM-0150',tipo='Solicitação',om='',ativo=COLH,sint='Ruído intermitente no elevador',
          crit='Baixa',cont=2150,evid='áudio do operador',rec='A definir na triagem',resp='PCM',
          pa=[Pt.act('Triar solicitação','Triada: criticidade Baixa · inspeção na próxima parada · colhedora segue Apta'),Pt.br(),Pt.cta('Criar ordem','MA-04.dc.html')]),
     dict(id='c6',caso='NC-0912',tipo='Checklist do operador',om='',ativo=PLANT,sint='Disco de corte com desgaste',
          crit='Média',cont=886,evid='foto',rec='Apto com troca programada',resp='PCM',pa=[Pt.cta('Criar ordem','MA-04.dc.html')]),
    ]
    rows=[dict(id=c['id'],v={k:c[k] for k in ('caso','tipo','om','ativo','sint','crit','cont','evid','rec','resp')},s={},p={},pa=c['pa'],pb=c.get('pb')) for c in CS]
    ATV=[nome(x) for x in DM.ORDEM_ATIVOS]
    REC=['Bloqueado','Restrito · monitorado','Apto · reparo na preventiva','Apto com troca programada','A definir na triagem']
    g_cs=grid([dict(k='caso',l='Caso',w=120),dict(k='ativo',l='Ativo',w=120),dict(k='sint',l='Sintoma · contador · evidência',w=200),
               dict(k='crit',l='Criticidade',chips={'Alta':'red','Média':'yellow','Baixa':'gray'}),
               dict(k='rr',l='Condição recomendada · responsável',w=150),dict(k='acao',l='Ação',w=135)],rows,
       edit=dict(m='form',title='Caso',newTitle='Registrar inspeção (checklist)',
            sub='Sintoma repetido agrega ao caso; não crie ordem nova por alerta idêntico.',
            fields=[dict(k='ativo',l='Ativo',t='sel',opts=['']+ATV,req=True,help='Escolha o ativo inspecionado.'),
                    dict(k='tipo',l='Origem',t='sel',opts=['Checklist do operador','Checklist da manutenção','Solicitação','Falha em campo','Alerta agregado'],req=True,**{'def':'Checklist do operador'}),
                    dict(k='sint',l='Sintoma / achado',t='area',req=True),
                    dict(k='crit',l='Criticidade',t='sel',opts=['Alta','Média','Baixa'],req=True,**{'def':'Média'}),
                    dict(k='cont',l='Contador',t='num',u='h',min=0),dict(k='evid',l='Evidência',t='txt',req=True,help='Foto, áudio, telemetria ou checklist.'),
                    dict(k='rec',l='Condição recomendada',t='sel',opts=REC,req=True,**{'def':'A definir na triagem'}),
                    dict(k='resp',l='Responsável',t='sel',opts=['PCM','Mecânico','Zé (mecânico)','Equipe elétrica'],req=True,**{'def':'PCM'})]),
       gid='g_cs',total=False)
    PA=[('Hidráulico',4,3,18.5,46,46,['SM-0147 e INSP-105 · Trator T1 · 14,0 h','INSP-104 · MF 7719 · 0,5 h','SM-0152 / OM-0228 · Bomba do Pivô 2 (3 alertas agregados num caso) · 4,0 h']),
        ('Rodado / rolamentos',2,2,14.0,35,81,['OM-0221 · Colhedora Axial-Flow 7250 · rolamento · 14,0 h','NC-0912 · Plantadeira · disco · 0 h (sem parada)']),
        ('Elétrico / sensores',2,2,6.0,15,96,['OB-0104 · Packing linha 1 · sensor da esteira · 4,0 h','Sensores do pulverizador · 2,0 h']),
        ('Outros',2,2,1.5,4,100,['Pequenos ajustes · 1,5 h'])]
    g_pa=grid([dict(k='item',l='Item/sistema',w=220),dict(k='ach',l='Achados',t='num',a='r'),dict(k='atv',l='Ativos afetados',t='num',a='r'),
               dict(k='hp',l='Horas paradas',t='num',a='r',u='h',d=1),dict(k='pct',l='% das horas paradas',t='num',a='r',u='%'),dict(k='acum',l='Acumulado',t='num',a='r',u='%')],
       [dict(id=f'p{i}',v=dict(item=it,ach=a,atv=n,hp=hp,pct=pc,acum=ac),s={},p={},o=[dict(t=x) for x in orig]+[dict(t='Base: 40,0 h paradas em 30 d')]) for i,(it,a,n,hp,pc,ac,orig) in enumerate(PA)],
       edit=dict(m='origin',title='Não conformidades',fields=[dict(k='item',l='Item/sistema',ro=True),dict(k='hp',l='Horas paradas',t='num',u='h',ro=True)]),
       search=False,gid='g_pa',total=False,so=dict(k='hp',d=True))
    g_ct=grid([dict(k='os',l='Ordem de campo',w=230),dict(k='ef',l='Efeito'),dict(k='tr',l='Tratamento',w=320),dict(k='ab',l='Abrir')],
       [dict(id='o1',v=dict(os=f'OS-0420 · {OS420["tipo"]} · {OS420["talhao"]} · {OS420["area"]} ha',tr=f'{OS420["realizado"]} ha feitos preservados · {D.OM["substituto"]}: {SUBST}'),s={},
             p=dict(os=[Pt.b('OS-0420'),Pt.br(),Pt.mut(f'{OS420["tipo"]} · {OS420["talhao"]} · {OS420["area"]} ha')],ef=[Pt.chip('Impedida · ativo bloqueado','red')],ab=[Pt.link('Abrir O.S.','OS.dc.html#OS-0420')])),
        dict(id='o2',v=dict(os=f'OS-0431 · {OS431["tipo"]} · {OS431["talhao"]} · {OS431["area"]} ha',tr='Bloqueio executado antes do 1º início (INSP-105) · substituição a propor em Vencimentos e paradas'),s={},
             p=dict(os=[Pt.b('OS-0431'),Pt.br(),Pt.mut(f'{OS431["tipo"]} · {OS431["talhao"]} · {OS431["area"]} ha')],ef=[Pt.chip('Retirada de Liberadas → A liberar','red')],ab=[Pt.link('Abrir O.S.','OS.dc.html#OS-0431')]))],
       edit=dict(m='ro',title='Ordem afetada',fields=[dict(k='os',l='Ordem',ro=True),dict(k='tr',l='Tratamento',ro=True)]),search=False,gid='g_ct',total=False)
    corpo=(kpis([('ABERTAS',H('k_ab'),'fila por risco e prazo'),('ALTA CRITICIDADE',H('k_alta'),'resposta imediata'),
                 ('BLOQUEIO OU RESTRIÇÃO',H('k_br'),'recomendado ou em vigor'),('SEM ORDEM',H('k_so'),'aguardam triagem ou vínculo')])
      + section('Fila de falhas, alertas e inspeções','',
          [sbtn('Registrar inspeção','g_cs_new','doc','Registrar achado de checklist com criticidade e evidência'),
           idrw('Bloquear ativo',dict(title='Bloquear ativo',
             sub='Ato técnico com motivo e responsável; as ordens de campo que usam o ativo ficam impedidas e o PCP é avisado.',
             fields=[('Ativo',COLH),('Motivo','Ruído no elevador com risco de quebra'),('Responsável técnico','Zé (mecânico)'),('Caso de origem','SM-0150')],
             confirm='Bloquear ativo',done='Colhedora bloqueada · nenhuma ordem de campo afetada hoje · PCP avisado (simulado)'),'alert','Bloquear ativo com motivo e responsável técnico')],g_cs)
      + section('Contingência do bloqueio','','',g_ct,state='red')
      + section('Não conformidades por item (Pareto 30 d)','','',g_pa,state='yellow'))
    EXTRAJS[0]=DM.js_prefixo()+JSBASE+r'''
function PREVALS(self,v){ manOuvir(self); const c=manGet(); const rows=ma_R(self,'g_cs'); let alta=0,br=0,so=0;
  rows.forEach(r=>{ const om=(c.ach||{})[r.v.caso]; if(om&&c.oms[om]) r.v.om=om; });
  // NC-0912 (disco de corte): com a preventiva da plantadeira aberta, o achado entra nela em vez de virar ordem nova
  const opl=Object.values(c.oms).find(o=>o.aid==='a06'&&o.tipo==='Preventiva'&&['A liberar','Liberadas','Em execução'].indexOf(o.etapa)>=0);
  const c6=rows.find(r=>r.id==='c6'); if(c6){ if(opl&&!c6.v.om) c6.pa=[{k:'act',t:'Vincular à '+opl.id,fn:'vincp:c6|'+opl.id}]; if(c6.v.om) c6.pb=[{k:'link',t:'Ver '+c6.v.om,h:'MA-04.dc.html#'+c6.v.om}]; }
  rows.forEach(r=>{ const x=r.v; if(!r.pa) r.pa=[{k:'cta',t:'Criar ordem',h:'MA-04.dc.html'}];
    r.p.caso=[{k:'b',t:x.caso},{k:'br',t:''},{k:'mut',t:(x.tipo||'').toLowerCase()+(x.om?' · caso '+x.om:'')}]; r.s.caso=x.caso+' '+x.tipo;
    r.p.acao=(x.om && r.pb)?r.pb:r.pa; r.s.acao='';
    r.p.sint=[{k:'txt',t:x.sint||'—'},{k:'br',t:''},{k:'mut',t:((x.cont!==''&&x.cont!==undefined&&x.cont!==null)?ma_nf(x.cont)+' h · ':'')+(x.evid||'—')}]; r.s.sint=(x.sint||'')+' '+(x.evid||'');
    const rc=(x.rec==='Bloqueado')?'red':(String(x.rec).indexOf('Restrito')===0?'yellow':null);
    r.p.rr=[rc?ma_chip(x.rec,rc):{k:'txt',t:x.rec},{k:'br',t:''},{k:'mut',t:x.resp}]; r.s.rr=x.rec+' '+x.resp;
    r.p.crit=[ma_chip(x.crit,x.crit==='Alta'?'red':(x.crit==='Média'?'yellow':'gray'))]; r.s.crit=x.crit;
    if(x.crit==='Alta') alta++; if(x.rec==='Bloqueado'||String(x.rec).indexOf('Restrito')===0) br++; if(!x.om) so++; });
  v.k_ab=String(rows.length); v.k_alta=String(alta); v.k_br=String(br); v.k_so=String(so); }
function ma_vincAch(self,r,om,msg){ if(!r||r.v.om) return; manMudar(self,c=>{ const o=c.oms[om]; if(!o) throw new Error(om+' não existe mais; gere a preventiva de novo.');
    c.ach=c.ach||{}; c.ach[r.v.caso]=om; (o.achados=o.achados||[]).push({caso:r.v.caso,t:r.v.sint}); r.v.om=om; return {msg}; }); }
function EXTRAVALS(self,v){
  v.vincp=(arg)=>{ const a=arg.split('|'); const r=ma_R(self,'g_cs').find(x=>x.id===a[0]); if(!r) return;
    ma_vincAch(self,r,a[1],'Achado '+r.v.caso+' vinculado à '+a[1]+' (revisão pré-plantio) · a troca dos discos já está no checklist · nenhuma ordem nova criada'); };
  v.vinc=(id)=>{ const r=ma_R(self,'g_cs').find(x=>x.id===id); if(!r) return;
    ma_vincAch(self,r,'OM-0234','Achado '+r.v.caso+' vinculado à OM-0234 (preventiva do MF 7719) · nenhuma ordem nova criada'); };
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_cs'||!r) return;
    if(!r.v.caso){ const n=rows.filter(x=>String(x.v.caso||'').indexOf('NC-')===0).length; r.v.caso='NC-'+String(912+n).padStart(4,'0'); r.v.om='';
      self.setState({g2toast:'Achado '+r.v.caso+' registrado · entrou na fila por risco · crie ou vincule uma ordem'}); }
    else self.setState({g2toast:'Caso '+r.v.caso+' salvo · fila reordenada por risco'}); }; }
'''
    shell37('MA-02','Solicitações e inspeções',corpo,
      status=('3 de alta criticidade','red'),primary='Criar ordem de manutenção',primary_href='MA-04.dc.html',steps=faixa(2))

# =====================================================================================
def ma03():
    """Vencimentos e paradas: cada ativo × serviço dos planos publicados, com o que vence primeiro; gera as preventivas e trata o impacto na produção."""
    fn='MA-03.dc.html'; HEIGHTS37[fn]=1000
    g_vc=grid(VENC_COLS,[],edit=dict(m='none'),gid='g_vc',total=False,so=dict(k='prox',d=False),qf=dict(k='sit',l='situação'))
    g_mi=grid([dict(k='man',l='Manutenção',w=210),dict(k='jan',l='Janela',w=120),dict(k='prod',l='Produção afetada',w=200),dict(k='sit',l='Situação',w=210),dict(k='ab',l='Abrir')],[],
       edit=dict(m='ro',title='Manutenção × produção',fields=[dict(k='man',l='Manutenção',ro=True),dict(k='jan',l='Janela',ro=True),dict(k='prod',l='Produção afetada',ro=True)]),
       search=False,gid='g_mi',total=False)
    corpo=(kpis([('VENCIDAS',H('k_ven'),H('k_vend')),('VENCEM EM BREVE',H('k_bre'),H('k_bred')),
                 ('SEM ORDEM',H('k_sem'),H('k_semd')),('CONFLITOS COM A PRODUÇÃO',H('k_conf'),H('k_confd'))])
      # UX-ACAO-UNICA v3 (uma instância por efeito): o atalho geral "Planos de manutenção" do bloco repetia o destino da trilha
      # "Manutenção" (PM.dc.html); cada linha já abre o plano que gera aquele vencimento (ação do registro) e o menu traz a lista
      + section('Vencimentos por ativo e serviço','',[],g_vc+_restaurar())
      + section('Manutenções e impacto na produção','',
          [IF('mi_podeMover',sbtn(H('mi_movt'),'mi_mover','calendar','Mover a preventiva do MF 7719 para depois da OS-0420, dentro da tolerância do plano')),
           IF('mi_podeProp',sbtn('Propor substituição','mi_prop','truck','Registrar proposta de substituto para as ordens afetadas pelo Trator T1'),True)],g_mi,state='red'))
    prim=(IF('prim_gera',f'<button type="button" onClick="{H("prim_fn")}" style="{BTN_ST(True)}">{H("prim_t")}</button>',True)
          + IF('prim_ver',f'<a href="MA-04.dc.html" style="text-decoration: none; display: inline-block; {BTN_ST(True)}">Ver ordens de manutenção</a>'))
    EXTRAJS[0]=DM.js_prefixo()+JSBASE+JSVENC+JSRST+r'''
// janela da OM-0234 depois da OS-0420 e dentro da tolerância do serviço (vencimento + tolerância, projetado pelo ritmo)
function ma_mover(c){ const o=c.oms['OM-0234']; if(!o||o.etapa!=='A liberar'||!o.conflito) return null;
  const l=manLinhas(c,o.pid).find(x=>x.aid===o.aid&&x.sid===o.sid); if(!l) return null; const g=l.x.gats.find(y=>y.u!=='d'); const a=l.a;
  const alvo=manAdd(c.hoje,6); if(!g||!a.leit||!a.ritmo) return null;
  const lim=g.due+g.tol; const dl=manAdd(a.leit.data,Math.floor((lim-a.leit.val)/a.ritmo)); return {alvo,lim,dl,ok:manDias(alvo,dl)>=1}; }
function PREVALS(self,v){ manOuvir(self); const c=manGet(); const prop=!!c.prop; const L=(t,h)=>({k:'link',t:t,h:h});
  const ls=manLinhas(c).filter(l=>l.s); ma_G('g_vc').rows=ls.map(l=>ma_linhaVenc(c,l,true));
  const ven=ls.filter(l=>l.x.sit==='Vencida'), bre=ls.filter(l=>l.x.sit==='Vence em breve'), sem=ls.filter(l=>manDevida(l)&&!l.om&&!l.dup);
  const nm=(l)=>l.a.nome; v.k_ven=String(ven.length); v.k_vend=ven.map(nm).join(' · ')||'nenhuma'; v.k_bre=String(bre.length); v.k_bred=bre.map(nm).join(' · ')||'janela em até '+c.horiz+' dias';
  v.k_sem=String(sem.length); v.k_semd=sem.length?sem.map(nm).join(' · '):'todas com ordem';
  const o34=c.oms['OM-0234']; const conf=!!o34&&o34.etapa==='A liberar'&&!!o34.conflito; const acc=!!o34&&!!o34.conflitoAceito&&o34.etapa!=='Encerradas';
  const rows=[
   {id:'m1',v:{man:'Corretiva OM-0233 · Trator T1',jan:'até teste aprovado',prod:'OS-0420 saldo 70 ha · OS-0431 102 ha'},s:{},
    p:{man:[{k:'b',t:'Corretiva OM-0233'},{k:'br',t:''},{k:'mut',t:'Trator T1 · retorno previsto 24/09 12:00'}],prod:[{k:'txt',t:'OS-0420 saldo 70 ha'},{k:'br',t:''},{k:'txt',t:'OS-0431 · plantio T2 · 102 ha'}],
       sit:prop?[ma_chip('Proposto · aguarda PCP','yellow'),{k:'br',t:''},{k:'mut',t:'MF 7719 para OS-0420 e OS-0431'}]
               :[ma_chip('Proposto · aguarda PCP','yellow'),{k:'br',t:''},{k:'mut',t:'OS-0420 saldo 70 ha'},{k:'br',t:''},ma_chip('OS-0431 sem substituto','red')],
       ab:[L('Abrir ordem','MA-04det.dc.html')]}}];
  if(o34) rows.push({id:'m2',v:{man:'Preventiva 250 h · MF 7719 (OM-0234)',jan:o34.jan,prod:'OS-0420 saldo · substituto até 28/09'},s:{},
    p:{man:[{k:'b',t:'Preventiva 250 h · OM-0234'},{k:'br',t:''},{k:'mut',t:'Trator 02 · MF 7719 · '+o34.etapa.toLowerCase()}],
       jan:[{k:'txt',t:o34.jan}].concat(o34.janAnt?[{k:'br',t:''},{k:'mut',t:'antes '+o34.janAnt}]:[]),
       sit:conf?[ma_chip('Conflito · OS-0420','red')]:(acc?[ma_chip('Conflito aceito','yellow'),{k:'br',t:''},{k:'mut',t:'PCP avisado'}]:[ma_chip('Sem conflito','green')]),
       ab:[L('Abrir OM-0234','MA-04.dc.html#OM-0234')]}});
  Object.values(c.oms).filter(o=>o.tipo==='Preventiva'&&o.id!=='OM-0234'&&['A liberar','Liberadas','Em execução'].indexOf(o.etapa)>=0).forEach(o=>{ const a=c.ativos[o.aid];
    rows.push({id:'g'+o.id,v:{man:o.serv+' · '+a.nome+' ('+o.id+')',jan:o.jan,prod:o.aid==='a11'?'OS-0419 termina 24/09 10:31':'nenhuma ordem de campo na janela'},s:{},
      p:{man:[{k:'b',t:o.serv+' · '+o.id},{k:'br',t:''},{k:'mut',t:manNome(a)+' · '+o.etapa.toLowerCase()}],sit:[ma_chip('Sem conflito','green')],ab:[L('Abrir '+o.id,'MA-04.dc.html#'+o.id)]}}); });
  ma_G('g_mi').rows=rows;
  const cf=[]; if(conf) cf.push('MF 7719 × OS-0420'); if(!prop) cf.push('OS-0431 sem substituto');
  v.k_conf=String(cf.length); v.k_confd=cf.join(' · ')||'propostas aguardam PCP';
  // primária pelo estado: gerar o que falta; sem nada a gerar, ir às ordens
  v.prim_gera=sem.length>0; v.prim_ver=!sem.length; v.prim_t='Gerar '+sem.length+(sem.length>1?' ordens preventivas':' ordem preventiva');
  v.prim_fn=()=>manMudar(self,c2=>manGerarTodas(c2));
  const sc=ven.length?'red':(bre.length?'yellow':'green');
  v.st_ma=(ven.length?ven.length+(ven.length>1?' vencidas':' vencida'):(bre.length?bre.length+' vence'+(bre.length>1?'m':'')+' em breve':'Preventivas em dia'))+(sem.length?' · '+sem.length+' sem ordem':'');
  v.st_ma_st=ma_chipSt(sc).replace('padding:2px 9px;','padding:3px 10px;'); v.st_ma_dot=ma_dotSt(sc);
  const mv=ma_mover(c); v.mi_podeMover=!!(mv&&mv.ok); v.mi_movt=mv?('Mover OM-0234 para '+manBr(mv.alvo)):'';
  v.mi_podeProp=!prop; }
function EXTRAVALS(self,v){ ma_gerarV(self,v); ma_rstV(self,v,'ma');
  v.mi_mover=()=>manMudar(self,c=>{ const mv=ma_mover(c); if(!mv) return {nada:true,msg:'A OM-0234 não tem conflito de janela a resolver.'};
    if(!mv.ok) throw new Error('Fora da tolerância: a Revisão 250 h aceita até '+manQ(mv.lim,'h')+' ≈ '+manBr(mv.dl)+'.');
    const o=c.oms['OM-0234']; o.janAnt=o.jan; o.jan=manBr(mv.alvo); o.ret=manBr(mv.alvo)+' 17:00'; o.conflito=null;
    return {msg:'OM-0234 movida para '+manBr(mv.alvo)+' · dentro da tolerância (até '+manQ(mv.lim,'h')+' ≈ '+manBr(mv.dl)+') · sem conflito com a OS-0420.'}; });
  v.mi_prop=()=>manMudar(self,c=>{ if(c.prop) return {nada:true,msg:'Proposta já registrada · aguarda PCP em Impedimentos e reprogramação.'}; c.prop=true;
    return {msg:'Proposta registrada: Trator 02 · MF 7719 para OS-0431 (24/09) e saldo da OS-0420 · aguarda PCP em Impedimentos e reprogramação (simulado).'}; }); }
'''
    shell37('MA-03','Vencimentos e paradas',corpo,
      status=(H('st_ma'),'red'),primary_html=prim,steps=faixa(3))
    _status_dyn(fn,'st_ma')

# =====================================================================================
MA04_JS=r'''
const MA_ETC={'A liberar':'gray','Liberadas':'green','Em execução':'green','Em conferência':'yellow','Encerradas':'gray'};
// próximo passo da ordem pela fase: verbo + quem resolve; trava só por falta de peça
function ma_passo(c,o){
  if(o.det) return {t:'Corretiva acompanhada na ordem completa: teste do reparo, aptidão do ativo, sobras e encerramento.',lnk:o.det,lnkt:'Abrir ordem completa'};
  const f=manFalta(c,o);
  if(o.etapa==='A liberar'){ if(f.length){ const bt='Falta peça: '+f.map(p=>p.nome+' ('+ma_nf(Math.max(0,c.itens[p.item].saldo-c.itens[p.item].reservado))+' de '+ma_nf(p.qtd)+' '+p.un+')').join(', ');
      // falta de peça: solicitar a compra; com a SC enviada, registrar o recebimento (simulado no almoxarifado) e liberar
      if(!o.sc) return {t:'Solicite a compra; a ordem libera quando a peça chegar.',bloq:bt,bq:'Quem resolve: Suprimentos.',btn:'Solicitar compra',fn:'sc'};
      return {t:'Registre o recebimento quando a peça chegar.',bloq:bt,bq:o.sc.id+' enviada em '+manBr(o.sc.data)+' · Suprimentos.',btn:'Registrar recebimento',fn:'rec'}; }
    return {t:'Libere o serviço para a oficina; as peças ficam reservadas no estoque.',btn:'Liberar serviço',fn:'lib'}; }
  if(o.etapa==='Liberadas') return {t:'Inicie quando o ativo chegar à oficina.',btn:'Iniciar serviço',fn:'ini'};
  if(o.etapa==='Em execução') return {t:'Responda o checklist, informe a leitura do contador e conclua.',btn:'Concluir serviço',fn:'con'};
  if(o.etapa==='Em conferência'){ if((o.pecas||[]).some(p=>p.sob>0)) return {t:'Devolva as sobras ao almoxarifado com recibo.',btn:'Resolver sobras',fn:'sob'};
    return {t:'Confira peças e horas e encerre o custo.',btn:'Encerrar ordem',fn:'enc'}; }
  return {t:'Ordem encerrada · custo '+manRS(o.custo||manCusto(c,o))+'.'}; }
function ma_abrir(self,id){ const r=document.activeElement; if(!self.state.pan) self.__omRet=(r&&r!==document.body&&!(r.closest&&r.closest('#om-painel')))?r:null; self.setState({pan:id,pav:false,pavl:false,pl:'',ph:'',pa:{}}); manHash(id); setTimeout(()=>{ const e=document.getElementById('om-painel'); if(e) e.focus(); },0); }
function ma_exec(self,id,fn,forcar){
  if(fn==='lib'){ const r=manMudar(self,c=>manLiberar(c,id,forcar)); if(r.aviso) self.setState({pan:id,pav:true}); else if(!r.erro) self.setState({pav:false}); return r; }
  if(fn==='sc') return manMudar(self,c=>manSolicitar(c,id));
  if(fn==='rec') return manMudar(self,c=>manReceber(c,id));
  if(fn==='ini') return manMudar(self,c=>manIniciar(c,id));
  if(fn==='con'){ const st=self.state; const r=manMudar(self,c=>manConcluir(c,id,st.pl,st.ph,forcar,st.pa||{}));
    if(r.avisoLeit) self.setState({pan:id,pavl:true}); else if(!r.erro) self.setState({pl:'',ph:'',pa:{},pavl:false}); return r; }
  if(fn==='sob') return manMudar(self,c=>manSobras(c,id));
  if(fn==='enc') return manMudar(self,c=>manEncerrar(c,id)); }
function PREVALS(self,v){ manOuvir(self); const c=manGet(); const os=Object.values(c.oms);
  os.sort((a,b)=>(MAN_FASES.indexOf(a.etapa)-MAN_FASES.indexOf(b.etapa))||a.id.localeCompare(b.id));
  ma_G('g_om').rows=os.map(o=>{ const a=c.ativos[o.aid]; const sel=manSelos(c,o); const nk=o.chk.filter(t=>t.r).length; const pr=ma_passo(c,o);
    let ac; if(o.det) ac=[{k:'cta',t:'Abrir ordem completa',h:o.det,u:true}];
    else if(pr.bloq) ac=[{k:'act',t:'Ver falta de peça',fn:'abrir:'+o.id}];
    else if(pr.btn) ac=[{k:'act',t:pr.btn,fn:'acao:'+o.id}];
    else ac=[{k:'mut',t:manRS(o.custo||manCusto(c,o))}];
    const np=(o.pecas||[]).length;
    return {id:o.id,v:{},s:{om:o.id+' '+manNome(a),serv:o.serv+' '+o.tipo,jan:o.jan,fase:o.etapa,chk:nk+' de '+o.chk.length,acao:''},
      p:{om:[{k:'b',t:o.id},{k:'br',t:''},{k:'mut',t:manNome(a)}],
         serv:[{k:'txt',t:o.serv},{k:'br',t:''},{k:'tag',t:o.tipo}].concat(o.crit==='Alta'?[ma_chip('Alta','red')]:[]).concat([{k:'mut',t:o.pid?(o.pid+' v'+o.ver):String(o.origem).split(' · ')[0]}]),
         jan:[{k:'txt',t:o.jan}],
         fase:[ma_chip(o.etapa,MA_ETC[o.etapa]||'gray')].concat(sel.length?[{k:'br',t:''}]:[]).concat(sel.map(z=>ma_chip(z.t,z.c))),
         chk:[{k:'txt',t:'checklist '+nk+' de '+o.chk.length},{k:'br',t:''},{k:'mut',t:np?(np+(np>1?' peças':' peça')):'sem peças'}],
         acao:ac}}; });
  const n={}, ids={}; os.forEach(o=>{ n[o.etapa]=(n[o.etapa]||0)+1; (ids[o.etapa]=ids[o.etapa]||[]).push(o.id); });
  const Ls=(e)=>(ids[e]||[]).join(' · ')||'nenhuma';
  v.k_al=String(n['A liberar']||0); v.k_ald=Ls('A liberar'); v.k_ex=String(n['Em execução']||0); v.k_exd=Ls('Em execução');
  v.k_co=String(n['Em conferência']||0); v.k_cod=Ls('Em conferência'); }
function EXTRAVALS(self,v){ const c=manGet(); const st=self.state; ma_rstV(self,v,'ma');
  if(!self.__hashIni){ self.__hashIni=1; const ab=()=>{ const h=decodeURIComponent((location.hash||'').slice(1)); if(manGet().oms[h]) setTimeout(()=>ma_abrir(self,h),0); }; ab(); try{ window.addEventListener('hashchange',ab); }catch(e){} }
  self.g2pick=(gid,rid)=>{ if(gid==='g_om') ma_abrir(self,rid); };
  v.abrir=(id)=>ma_abrir(self,id);
  v.acao=(id)=>{ const o=manGet().oms[id]; if(!o) return; const pr=ma_passo(manGet(),o); if(pr.fn==='con'||pr.fn==='sc'||pr.fn==='rec'){ ma_abrir(self,id); return; } ma_exec(self,id,pr.fn,false); };
  // chips de fase: filtro real da coluna Fase
  const os=Object.values(c.oms); const gst=g2st(self,'g_om'); const ff=((gst.f||{}).fase)||[];
  const chip=(t,nn,on,fn)=>({t,n:String(nn),on:on?'true':'false',fn,st:'display:inline-flex;align-items:center;gap:7px;font-family:inherit;font-size:12.5px;font-weight:700;padding:6px 12px;border-radius:999px;cursor:pointer;white-space:nowrap;'+(on?'border:1px solid #15201A;background:#15201A;color:#fff;':'border:1px solid #E4E9E5;background:#FFFFFF;color:#15201A;'),
    nst:'font-size:11.5px;font-weight:800;padding:0 7px;border-radius:999px;'+(on?'background:rgba(255,255,255,.2);color:#fff;':'background:#EEF1EE;color:#15201A;')});
  const setF=(f)=>()=>{ const cur=Object.assign({},g2st(self,'g_om').f||{}); if(f) cur.fase=[f]; else delete cur.fase; g2set(self,'g_om',{f:cur,fmc:null}); };
  v.fchips=[chip('Todas',os.length,ff.length===0,setF(null))].concat(MAN_FASES.map(f=>chip(f,os.filter(o=>o.etapa===f).length,ff.length===1&&ff[0]===f,setF(f))));
  // painel lateral da ordem
  const o=st.pan?c.oms[st.pan]:null; v.pan_open=!!o;
  const close=()=>{ self.setState({pan:null,pav:false,pavl:false}); manHash(''); setTimeout(()=>{ const r=self.__omRet; self.__omRet=null; if(r&&document.contains(r)) r.focus(); },0); }; v.pan_close=close;
  self.__omClose=close; ma_modalDoc(self,()=>self.state.pan?{root:document.getElementById('om-painel'),close:()=>self.__omClose()}:null);
  v.pan_key=(e)=>{ if(!e) return; if(e.key==='Escape'){ e.preventDefault(); close(); } else ma_trap(e,document.getElementById('om-painel')); };
  if(!o){ v.pan_t=''; return; }
  const a=c.ativos[o.aid]; const pr=ma_passo(c,o);
  v.pan_t=o.id+' · '+manNome(a); v.pan_sub=o.tipo+' · '+o.serv;
  v.pan_fase=o.etapa; v.pan_fst=ma_chipSt(MA_ETC[o.etapa]||'gray'); v.pan_fdot=ma_dotSt(MA_ETC[o.etapa]||'gray');
  v.pan_selos=manSelos(c,o).map(z=>({t:z.t,st:ma_chipSt(z.c),dot:ma_dotSt(z.c)}));
  const cur=MAN_FASES.indexOf(o.etapa);
  v.pan_steps=MAN_FASES.map((f,i)=>({t:f,cur:i===cur?'step':'false',st:'display:flex;flex-direction:column;gap:5px;font-size:11.5px;font-weight:'+(i===cur?'800':'600')+';color:'+(i<=cur?'#15201A':'#8A968E')+';',
    bst:'height:5px;border-radius:999px;background:'+(i<cur?'#9CCBB0':(i===cur?'#1E7A4C':'#E4E9E5'))+';'}));
  v.pan_pt=pr.t; v.pan_hasBtn=!!pr.btn; v.pan_pbtn=pr.btn||''; v.pan_go=()=>ma_exec(self,o.id,pr.fn,false);
  v.pan_bloq=!!pr.bloq; v.pan_bt=pr.bloq||''; v.pan_bq=pr.bq||''; v.pan_bh=pr.bh||'#'; v.pan_bhl=pr.bhl||'';
  v.pan_av=!!st.pav&&o.etapa==='A liberar'&&!!o.conflito; v.pan_avt=o.conflito?o.conflito.t+'.':''; v.pan_avgo=()=>ma_exec(self,o.id,'lib',true); v.pan_avno=()=>self.setState({pav:false});
  // leitura implausível na conclusão: aviso a confirmar (concluir mesmo assim ou corrigir)
  const plv=(st.pavl&&o.etapa==='Em execução'&&a)?manPlaus(c,a,manNum(st.pl)):''; v.pan_avl=!!plv; v.pan_avlt=plv?plv+'.':'';
  v.pan_avlgo=()=>ma_exec(self,o.id,'con',true); v.pan_avlno=()=>{ self.setState({pavl:false}); setTimeout(()=>{ const e=document.getElementById('om-leitura'); if(e){ e.focus(); if(e.select) e.select(); } },0); };
  v.pan_idle=!v.pan_av&&!v.pan_avl; v.pan_hasLnk=!!pr.lnk; v.pan_lnk=pr.lnk||'#'; v.pan_lnkt=pr.lnkt||'';
  // checklist: Feito · Não feito · Não se aplica (os dois últimos com motivo); só se responde com a ordem Em execução
  const ed=o.etapa==='Em execução'&&!o.det; const R=['Feito','Não feito','Não se aplica'];
  v.pan_chk=o.chk.map((t,i)=>({n:String(i+1),t:t.t,ed,ro:!ed,
    opts:R.map(r=>({t:r,on:String(t.r===r),lab:r+' · '+t.t,go:()=>manMudar(self,c2=>manResp(c2,o.id,i,t.r===r?'':r,undefined,g2perfil())),
      st:'font-family:inherit;font-size:12px;font-weight:700;padding:4px 9px;border-radius:8px;cursor:pointer;white-space:nowrap;'+(t.r===r?(r==='Feito'?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #8A5A00;background:#FFF3D6;color:#8A5A00;'):'border:1px solid #E4E9E5;background:#fff;color:#15201A;')})),
    r:t.r||'Sem resposta',rst:ma_chipSt(t.r==='Feito'?'green':(t.r?'yellow':'gray')),rdot:ma_dotSt(t.r==='Feito'?'green':(t.r?'yellow':'gray')),
    por:t.por?('por '+t.por+(t.em?' às '+t.em:'')):'',hasPor:!!t.por,mot:t.mot||'',hasMotIn:ed&&!!t.r&&t.r!=='Feito',hasMotTx:!ed&&!!t.mot,motlab:'Motivo · '+t.t,
    setmot:(e)=>{ const val=e.target.value; manMudar(self,c2=>manResp(c2,o.id,i,t.r,val,g2perfil())); }}));
  const nr=o.chk.filter(t=>t.r).length; v.pan_chkn=nr+' de '+o.chk.length+' respondidas';
  // execução: leitura do contador e horas (obrigatória a leitura para concluir)
  v.pan_exEd=ed; v.pan_hasCont=!!(a&&a.un); v.pan_unl=a&&a.un==='km'?'Leitura do odômetro (km)':'Leitura do horímetro (h)';
  v.pan_leit=st.pl||''; v.pan_setleit=(e)=>self.setState({pl:e.target.value,pavl:false}); v.pan_horas=st.ph||''; v.pan_sethoras=(e)=>self.setState({ph:e.target.value});
  v.pan_hph='previsto '+ma_nf(o.tempo,1)+' h'; v.pan_ult=a&&a.leit?('Última: '+manLeitTxt(a)+' · '+a.leit.origem):'';
  v.pan_exRo=!!o.exec; v.pan_exkv=o.exec?[{l:'Concluída em',v:manBr(o.exec.data)},{l:'Leitura',v:(o.exec.leit!==null&&o.exec.leit!==undefined&&a&&a.un)?manQ(o.exec.leit,a.un):'—'},{l:'Horas',v:ma_nf(o.exec.horas,1)+' h'}]:[];
  // peças: planejado · reservado/aplicado/sobra · saldo
  v.pan_pecas=(o.pecas||[]).map(p=>{ const it=p.item?c.itens[p.item]:null; const disp=it?it.saldo-it.reservado:null; let s,cc;
    if(p.sob>0){ s='sobra '+ma_nf(p.sob)+' '+p.un+' a devolver'; cc='yellow'; }
    else if(p.dev){ s='aplicado '+ma_nf(p.apl)+' · devolvido '+ma_nf(p.dev)+' '+p.un; cc='green'; }
    else if(p.apl){ s='aplicado '+ma_nf(p.apl,1)+' '+p.un; cc='green'; }
    else if(p.res){ s='reservado '+ma_nf(p.res,1)+' '+p.un; cc='green'; }
    else if(it&&disp<p.qtd){ s='falta · saldo '+ma_nf(Math.max(0,disp),1)+' '+p.un; cc='red'; }
    else if(it){ s='disponível · saldo '+ma_nf(disp,1)+' '+p.un; cc='gray'; } else { s='—'; cc='gray'; }
    // em execução: quantidade realmente aplicada (vazio = planejado; menos que o planejado vira sobra a devolver)
    const i=(o.pecas||[]).indexOf(p); const pa=(st.pa||{})[i];
    return {nome:p.nome,q:ma_nf(p.qtd,1)+' '+p.un,s,st:ma_chipSt(cc),dot:ma_dotSt(cc),ed:ed,ro:!ed,av:pa===undefined?'':pa,aph:ma_nf(p.qtd,1),alab:'Aplicado · '+p.nome+' ('+p.un+')',un:p.un,
      aset:(e)=>{ const n=Object.assign({},self.state.pa||{}); n[i]=e.target.value; self.setState({pa:n}); }}; });
  v.pan_temPecas=v.pan_pecas.length>0; v.pan_semPecas=!v.pan_temPecas;
  v.pan_kv=[{l:'Tipo',v:o.tipo},{l:'Criticidade',v:o.crit},{l:'Janela',v:o.jan},{l:'Especialidade',v:o.esp},{l:'Tempo estimado',v:ma_nf(o.tempo,1)+' h'},
            {l:'Custo',v:o.etapa==='Encerradas'?manRS(o.custo||manCusto(c,o)):'no encerramento'}];
  v.pan_ach=(o.achados||[]).map(x=>({t:x.caso+' · '+x.t})); v.pan_temAch=v.pan_ach.length>0;
  v.pan_orig=o.origem; v.pan_hasPl=!!o.pid; v.pan_plh='PM.dc.html#'+(o.pid||''); v.pan_plt=o.pid?('Abrir '+o.pid+' · a ordem segue na v'+o.ver):''; }
'''

def _painel_om():
    lab=lambda t: f'<div style="font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">{t}</div>'
    chip_h=lambda t,st,dot: f'<span style="{H(st)}"><span style="{H(dot)}"></span>{H(t)}</span>'
    kvbox=lambda lst: (f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px 18px; padding: 12px 14px; background: {BG}; border-radius: 12px;">'
                       + FOR(lst,'x',f'<div style="min-width: 0;"><div style="font-size: 10.5px; font-weight: 700; letter-spacing: .05em; color: {MUTED}; text-transform: uppercase;">{H("x.l")}</div><div style="font-size: 13.5px; font-weight: 600; margin-top: 2px;">{H("x.v")}</div></div>',6) + '</div>')
    passo=(f'<div role="region" aria-label="Próximo passo" style="display: flex; flex-direction: column; gap: 8px; padding: 12px 14px; border-radius: 12px; border: 1px solid {LINE}; background: {ACCS};">{lab("Próximo passo")}'
           f'<div style="font-size: 13.5px; line-height: 1.45;">{H("pan_pt")}</div>'
           + IF('pan_bloq',f'<div role="alert" style="padding: 8px 10px; border-radius: 8px; background: {REDS}; color: {RED}; font-size: 12.8px; font-weight: 700;">{H("pan_bt")}<br><span style="font-weight: 600;">{H("pan_bq")}</span></div>')
           + IF('pan_av',f'<div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.8px; font-weight: 700;">{H("pan_avt")}'
                f'<div style="display: flex; gap: 8px; flex-wrap: wrap;"><button type="button" onClick="{H("pan_avgo")}" style="{_MINIP}">Liberar mesmo assim</button>'
                f'<a href="MA-03.dc.html" style="{_MINI} text-decoration: none; display: inline-flex;">Mover a janela ›</a><button type="button" onClick="{H("pan_avno")}" style="{_MINI}">Voltar</button></div></div>')
           + IF('pan_avl',f'<div role="alert" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.8px; font-weight: 700;">{H("pan_avlt")}'
                f'<div style="display: flex; gap: 8px; flex-wrap: wrap;"><button type="button" onClick="{H("pan_avlno")}" style="{_MINIP}">Corrigir leitura</button>'
                f'<button type="button" onClick="{H("pan_avlgo")}" style="{_MINI}">Concluir com esta leitura</button></div></div>')
           + IF('pan_idle',IF('pan_hasBtn',f'<div><button type="button" onClick="{H("pan_go")}" style="{BTN_ST(True,True)}">{H("pan_pbtn")}</button></div>'),True)
           + IF('pan_hasLnk',f'<div><a href="{H("pan_lnk")}" style="text-decoration: none; display: inline-block; {BTN_ST(True,True)}">{H("pan_lnkt")} ›</a></div>')
           + '</div>')
    chkrow=(f'<div style="display: flex; flex-direction: column; gap: 6px; padding: 8px 0; border-top: 1px solid {LINE};">'
            f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;"><span style="font-size: 12px; font-weight: 800; color: {MUTED}; width: 18px;">{H("t.n")}</span>'
            f'<span style="font-size: 13px; font-weight: 600; flex: 1 1 200px; min-width: 0;">{H("t.t")}</span>'
            + IF('t.ed',f'<span role="group" aria-label="{H("t.t")}" style="display: inline-flex; gap: 4px;">'+FOR('t.opts','b',f'<button type="button" aria-pressed="{H("b.on")}" aria-label="{H("b.lab")}" onClick="{H("b.go")}" style="{H("b.st")}">{H("b.t")}</button>',3)+'</span>')
            + IF('t.ro',chip_h('t.r','t.rst','t.rdot')) + IF('t.hasPor',f'<span style="font-size: 12px; color: {MUTED};">{H("t.por")}</span>') + '</div>'
            + IF('t.hasMotIn',f'<input aria-label="{H("t.motlab")}" placeholder="Motivo (obrigatório)" value="{H("t.mot")}" onChange="{H("t.setmot")}" style="margin-left: 28px; font-family: inherit; font-size: 13px; padding: 6px 9px; border-radius: 8px; border: 1px solid {LINE};">')
            + IF('t.hasMotTx',f'<span style="margin-left: 28px; font-size: 12.5px; color: {MUTED};">Motivo: {H("t.mot")}</span>') + '</div>')
    chk=(f'<section aria-label="Checklist" style="display: flex; flex-direction: column; gap: 4px;"><div style="display: flex; align-items: center; gap: 10px;">{lab("Checklist")}'
         f'<span style="font-size: 12px; color: {MUTED}; flex-grow: 1;">{H("pan_chkn")}</span>'
         + '</div>'
         + FOR('pan_chk','t',chkrow,5) + '</section>')
    exe=(IF('pan_exEd',f'<section aria-label="Execução" style="display: flex; flex-direction: column; gap: 8px;">{lab("Execução")}<div style="display: flex; gap: 14px; flex-wrap: wrap; align-items: flex-end;">'
            + IF('pan_hasCont',f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {MUTED};">{H("pan_unl")}'
                 f'<input id="om-leitura" inputMode="decimal" value="{H("pan_leit")}" onChange="{H("pan_setleit")}" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; width: 150px; text-align: right;"></label>')
            + f'<label style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; color: {MUTED};">Horas de oficina'
              f'<input inputMode="decimal" placeholder="{H("pan_hph")}" value="{H("pan_horas")}" onChange="{H("pan_sethoras")}" style="font-family: inherit; font-size: 14px; padding: 7px 9px; border-radius: 8px; border: 1px solid {LINE}; width: 130px; text-align: right;"></label></div>'
            + IF('pan_hasCont',f'<span style="font-size: 12px; color: {MUTED};">{H("pan_ult")}</span>') + '</section>')
         + IF('pan_exRo',f'<section aria-label="Execução" style="display: flex; flex-direction: column; gap: 8px;">{lab("Execução")}'+kvbox('pan_exkv')+'</section>'))
    pecas=(f'<section aria-label="Peças" style="display: flex; flex-direction: column; gap: 4px;">{lab("Peças e lubrificantes")}'
           + IF('pan_temPecas',FOR('pan_pecas','p',f'<div style="display: grid; grid-template-columns: minmax(0, 1fr) 90px auto; gap: 10px; align-items: center; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 12.8px;">'
                f'<b style="font-weight: 600;">{H("p.nome")}</b><span style="text-align: right; font-variant-numeric: tabular-nums;">{H("p.q")}</span>'
                + IF('p.ro',chip_h("p.s","p.st","p.dot"),True)
                + IF('p.ed',f'<label style="display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; color: {MUTED};">Aplicado'
                     f'<input aria-label="{H("p.alab")}" inputMode="decimal" placeholder="{H("p.aph")}" value="{H("p.av")}" onChange="{H("p.aset")}" style="font-family: inherit; font-size: 13px; padding: 5px 8px; border-radius: 8px; border: 1px solid {LINE}; width: 80px; text-align: right;">{H("p.un")}</label>')
                + '</div>',3))
           + IF('pan_semPecas',f'<span style="font-size: 12.5px; color: {MUTED};">Sem peças nesta ordem.</span>') + '</section>')
    orig=(f'<section aria-label="Origem" style="display: flex; flex-direction: column; gap: 8px;">{lab("Origem")}<div style="font-size: 13px; font-weight: 600;">{H("pan_orig")}</div>'
          + IF('pan_temAch',FOR('pan_ach','x',f'<div style="font-size: 12.8px;">Achado vinculado: {H("x.t")}</div>',1))
          + kvbox('pan_kv') + IF('pan_hasPl',f'<div><a href="{H("pan_plh")}" style="color: {ACC}; font-weight: 700; text-decoration: none; font-size: 13px;">{H("pan_plt")} ›</a></div>') + '</section>')
    steps=(f'<div role="list" aria-label="Fases da ordem" style="display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 6px;">'
           + FOR('pan_steps','s',f'<div role="listitem" aria-current="{H("s.cur")}" style="{H("s.st")}"><span style="{H("s.bst")}"></span>{H("s.t")}</div>',5) + '</div>')
    return IF('pan_open',
      f'<div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
      f'<button type="button" aria-label="Fechar" tabIndex="-1" onClick="{H("pan_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
      f'<aside id="om-painel" tabIndex="-1" role="dialog" aria-modal="true" aria-label="{H("pan_t")}" onKeyDown="{H("pan_key")}" style="position: relative; width: 760px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px; outline: none;">'
      f'<div style="display: flex; gap: 10px; align-items: flex-start;"><div style="flex-grow: 1; min-width: 0;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; letter-spacing: -.02em;">{H("pan_t")}</h2>'
      f'<div style="font-size: 13px; color: {MUTED}; margin-top: 2px;">{H("pan_sub")}</div></div>'
      f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H("pan_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
      f'<div style="display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">{chip_h("pan_fase","pan_fst","pan_fdot")}' + FOR('pan_selos','s',chip_h('s.t','s.st','s.dot'),1) + '</div>'
      + steps + passo + chk + exe + pecas + orig + '</aside></div>')

def ma04():
    fn='MA-04.dc.html'; HEIGHTS37[fn]=1000
    g_om=grid([dict(k='om',l='Ordem · ativo',w=140),dict(k='serv',l='Serviço · tipo',w=170),dict(k='jan',l='Janela',w=80),dict(k='fase',l='Fase · selos',w=170),
               dict(k='chk',l='Checklist · peças',w=115),dict(k='acao',l='Ação',w=140)],[],edit=dict(m='pick'),gid='g_om',total=False)
    chips=(f'<div role="group" aria-label="Filtrar por fase" style="display: flex; flex-wrap: wrap; gap: 6px;">'
           + FOR('fchips','fc',f'<button type="button" aria-pressed="{H("fc.on")}" onClick="{H("fc.fn")}" style="{H("fc.st")}">{H("fc.t")}<span style="{H("fc.nst")}">{H("fc.n")}</span></button>',6) + '</div>')
    corpo=(kpis([('A LIBERAR',H('k_al'),H('k_ald')),('EM EXECUÇÃO',H('k_ex'),H('k_exd')),('EM CONFERÊNCIA',H('k_co'),H('k_cod')),
                 ('RETORNO DO TRATOR T1','24/09 12:00','se o teste for aprovado')])
      + section('Ordens de manutenção','',
          [ilnk('Vencimentos e paradas','MA-03.dc.html','calendar','Gerar as preventivas que vencem')],
          f'<div style="display: flex; flex-direction: column; gap: 10px;">{chips}{g_om}</div>'+_restaurar()))
    EXTRA.append(_painel_om())
    EXTRAJS[0]=DM.js_prefixo()+JSBASE+JSRST+MA04_JS
    shell37('MA-04','Ordens de manutenção',corpo,
      status=('1 bloqueio ativo','red'),steps=faixa(4))

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
      + section('Impacto do bloqueio','','',g_ib,state='red')
      + section('Execução na oficina','',
          [imsg('Registrar avanço e peças','Avanço registrado · mangueira 2 un baixadas da requisição · bomba antiga marcada como recuperável','wrench','Registrar avanço e baixar peças da requisição'),
           imsg('Finalizar apontamento do turno','Turno de Zé fechado · a ordem continua Em execução — finalizar o turno nunca conclui a ordem','clock','Fechar o turno do mecânico sem concluir a ordem')],g_tk)
      + section('Teste e aptidão','',
          [sbtn('Registrar teste do reparo','t_reg','check','Registrar a 2ª tentativa do teste de pressão em carga'),
           sbtn('Definir aptidão do ativo','t_apt','check','Decidir a aptidão do Trator T1 (exige teste aprovado)'),
           sbtn('Concluir serviço','t_con','wrench','Levar a ordem a Em conferência (exige teste aprovado)')],g_te,state='yellow')
      + section('Sobras e encerramento','',
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
       sit:S.apto?[ma_chip('Impedimento removido','yellow'),{k:'br',t:''},{k:'mut',t:'saldo 70 ha aguarda reprogramação do PCP'}]:[{k:'txt',t:'30 ha feitos preservados · saldo 70 ha pausado'}],ab:[L('Abrir O.S.','OS.dc.html#OS-0420')]}},
   {id:'b2',v:{obj:'OS-0431 · plantio T2 · 102 ha',tr:'Bloqueio executado antes do 1º início (INSP-105) · substituição proposta em Vencimentos e paradas'},s:{},
    p:{obj:[{k:'b',t:'OS-0431'},{k:'br',t:''},{k:'mut',t:'Plantio · Soja 58 W · T2 · 102 ha'}],ef:[ma_chip('Retirada de Liberadas → A liberar','red')],
       sit:S.apto?[ma_chip('Continua A liberar','yellow'),{k:'br',t:''},{k:'mut',t:'reprogramação pelo PCP'}]:[{k:'txt',t:'A liberar · aguarda ativo ou substituto'}],ab:[L('Abrir O.S.','OS.dc.html#OS-0431')]}},
   {id:'b3',v:{obj:'Agenda do Trator T1',tr:'Liberar o ativo não reassume a agenda antiga — volta pela fila de reprogramação'},s:{},
    p:{obj:[{k:'b',t:'Agenda do Trator T1'}],ef:[ma_chip(S.apto?'Apto':'Retirada',S.apto?'green':'gray')].concat(S.apto?[{k:'br',t:''},{k:'mut',t:'agenda antiga não reassumida'}]:[]),
       sit:[{k:'txt',t:S.apto?'na fila de reprogramação do PCP':'capacidade reduzida contada uma vez'}],ab:[{k:'mut',t:'—'}]}}]; }
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
      primary_html=prim,steps=faixa(4))

# =====================================================================================
def ma05():
    fn='MA-05.dc.html'; HEIGHTS37[fn]=1000
    T2=nome('a02')
    AB=[('AB-1042',T2,'Sede · D-118','nível 38%',180,'23/09 06:40',2988,'h','Beto','foto',('Tanque cheio · 14,2 L/h','green'),
         Pt.act('Conferir contador','AB-1042 conferido: 2.988 h coerente com o apontamento de ontem (+11 h)')),
        ('AB-1041',PULV,'Comboio CB-01 · D-117','nível 62%',240,'23/09 05:50',1542,'h','João','foto',('Estimada · 18,9 L/h','yellow'),
         Pt.act('Conferir contador','AB-1041 conferido: 1.542 h coerente com o apontamento da OS-0421 · taxa segue estimada (sem tanque cheio)')),
        ('AB-1039',COLH,'Sede · D-117','nível 52%',310,'22/09 18:10',2150,'h','Beto','foto',('12,1 L/h · +23%','yellow'),
         Pt.cta('Investigar desvio','MA-02.dc.html',True)),
        ('AB-1037',T2,'Sede · D-117','',320,'22/09 06:35',2977,'h','Beto','foto',('Estornado','gray'),
         Pt.act('Ver estorno','Estorno ES-0088 vinculado (23/09) · volume digitado errado · original preservado no histórico'))]
    CONTS=[nome(x) for x in DM.ORDEM_ATIVOS if DM.ATIVOS[x]['un']]
    g_ab=grid([dict(k='id',l='Lançamento · operador',w=110),dict(k='ativo',l='Ativo',w=110),dict(k='tq',l='Tanque/lote · nível após',w=110),dict(k='vol',l='Volume',t='num',a='r',u='L'),
               dict(k='dt',l='Data · contador'),dict(k='met',l='Método / taxa'),dict(k='acao',l='Ação',w=130)],
       [dict(id=a[0],ro=True,v=dict(id=a[0],ativo=a[1],tq=a[2],vol=a[4],dt=a[5],op=a[8],met=a[10][0],cont=a[6],evid=a[9]),s=dict(id=a[0]+' '+a[8]+' '+a[9],tq=a[2],dt=a[5],met=a[10][0]),
             p=dict(id=[Pt.b(a[0]),Pt.br(),Pt.mut(a[8]+' · '+a[9])],tq=[Pt.txt(a[2])]+([Pt.br(),Pt.mut(a[3])] if a[3] else []),dt=[Pt.txt(a[5]),Pt.br(),Pt.mut(f'{a[6]:,} {a[7]}'.replace(',','.'))],
                    met=[Pt.chip(*a[10])],acao=[a[11]])) for a in AB],
       edit=dict(m='form',title='Lançamento',newTitle='Registrar abastecimento',
            sub='Corrija sempre com estorno vinculado.',
            fields=[dict(k='ativo',l='Ativo',t='sel',opts=['']+CONTS,req=True),
                    dict(k='tq',l='Tanque/lote',t='sel',opts=['','Sede · D-118','Comboio CB-01 · D-118'],req=True),
                    dict(k='vol',l='Volume',t='num',u='L',min=1,max=2000,req=True),
                    dict(k='cont',l='Contador',t='num',min=0,req=True,help='Horímetro (h) ou odômetro (km) do ativo no abastecimento.'),
                    dict(k='op',l='Operador',t='sel',opts=['','Beto','João','Marcos'],req=True),
                    dict(k='evid',l='Evidência',t='txt',req=True,help='Foto da bomba e do painel.')]),
       gid='g_ab',total=False,so=dict(k='dt',d=True))
    CO=[(T2,512,36.0,14.2,('Reconciliado','green'),'−2%',['AB-1042 · 180 L · tanque cheio','AB-1037 estornado → relançado 332 L','Horas: apontamentos de 17 a 23/09']),
        (PULV,710,37.5,18.9,('Estimado','yellow'),'+4%',['AB-1041 · 240 L · sem tanque cheio','AB-1036 · 470 L','Horas: apontamentos da OS-0421']),
        (COLH,340,28.1,12.1,('Reconciliado','green'),'+23% · investigar',['AB-1039 · 310 L · tanque cheio','AB-1033 · 30 L (complemento)','Referência: média 9,8 L/h'])]
    g_co=grid([dict(k='ativo',l='Ativo',w=220),dict(k='lit',l='Litros no período',t='num',a='r',u='L'),dict(k='hr',l='Horas trabalhadas',t='num',a='r',u='h',d=1),
               dict(k='tx',l='Taxa',t='num',a='r',u='L/h',d=1),dict(k='met',l='Método'),dict(k='dv',l='Desvio vs. referência')],
       [dict(id=f'co{i}',v=dict(ativo=c[0],lit=c[1],hr=c[2],tx=c[3],met=c[4][0],dv=c[5]),s=dict(met=c[4][0],dv=c[5]),
             p=dict(met=[Pt.chip(*c[4])],dv=[Pt.chip(c[5],'yellow')] if 'investigar' in c[5] else [Pt.txt(c[5])]),
             o=[dict(t=x) for x in c[6]]+[dict(t=f'Taxa = {c[1]} L ÷ {str(c[2]).replace(".",",")} h')]) for i,c in enumerate(CO)],
       edit=dict(m='origin',title='Consumo',fields=[dict(k='ativo',l='Ativo',ro=True),dict(k='tx',l='Taxa',t='num',u='L/h',ro=True)]),
       search=False,gid='g_co',total=False)
    corpo=(kpis([('ABASTECIDO HOJE',H('k_hoje'),H('k_hojed')),('TANQUE SEDE','38%','mín. proposto 40% (em aprovação)'),
                 ('CONSUMO MF 7719','14,2 L/h','reconciliado'),('DESVIOS ABERTOS','1','Colhedora +23%')])
      + section('Lançamentos por ativo e tanque','',
          [sbtn('Registrar abastecimento','g_ab_new','fuel','Registrar novo abastecimento com contador e evidência',primary=True),
           idrw('Corrigir com estorno',dict(title='Corrigir lançamento com estorno',
             sub='O lançamento original fica no histórico; o estorno e o novo lançamento ficam vinculados.',
             fields=[('Lançamento','AB-1041'),('Motivo','Lote do comboio errado (D-117 → D-118)'),('Tanque/lote','Comboio CB-01 · D-118'),('Responsável','PCM')],
             confirm='Estornar e relançar',done='Estorno ES-0089 e lançamento AB-1044 vinculados a AB-1041'),'doc','Corrigir um lançamento com estorno vinculado')],g_ab)
      + section('Consumo reconciliado por ativo (7 d)','','',g_co,state='yellow'))
    EXTRAJS[0]=DM.js_prefixo()+JSBASE+'const MA_AID='+json.dumps({nome(x):x for x in DM.ORDEM_ATIVOS},ensure_ascii=False)+';\n'+r'''
function PREVALS(self,v){ manOuvir(self); const c=manGet(); const G=ma_G('g_ab'); if(!self.__ab0) self.__ab0=G.rows.slice();
  // leitura a confirmar (menor que a anterior ou acima do possível): Confirmar ou Descartar no próprio lançamento
  const pend=[]; G.rows=self.__ab0.concat(c.abast.map(x=>{ const a=c.ativos[x.aid]; const sp=!!(a&&a.suspeita&&a.suspeita.ab===x.id); if(sp) pend.push(x.id);
    const met=sp?[ma_chip('Leitura a confirmar','yellow'),{k:'br',t:''},{k:'mut',t:a.suspeita.tipo==='menor'?'menor que a anterior':'acima do possível'}]
      :(x.res?[ma_chip(x.res,x.res==='Leitura descartada'||x.res==='Substituída'?'gray':'green')]:[ma_chip('Estimada','yellow')]);
    const ac=sp?[{k:'act',t:a.suspeita.tipo==='menor'?'Confirmar troca':'Confirmar leitura',fn:'lok:'+x.aid},{k:'br',t:''},{k:'act',t:'Descartar',fn:'ldesc:'+x.aid,lk:true}]:[{k:'mut',t:'—'}];
    return {id:x.id,ro:true,v:{id:x.id,ativo:x.ativo,tq:x.tq,vol:x.vol,dt:x.dt,op:x.op,met:sp?'Leitura a confirmar':(x.res||'Estimada'),cont:x.cont,evid:x.evid},s:{id:x.id+' '+x.op+' '+x.evid,tq:x.tq,dt:x.dt,met:sp?'Leitura a confirmar':(x.res||'Estimada')},
      p:{id:[{k:'b',t:x.id},{k:'br',t:''},{k:'mut',t:x.op+' · '+x.evid}],tq:[{k:'txt',t:x.tq}],dt:[{k:'txt',t:x.dt},{k:'br',t:''},{k:'mut',t:ma_nf(x.cont)+' '+x.un}],met,acao:ac}}; }));
  const hj=G.rows.filter(r=>String(r.v.dt).indexOf('23/09')===0&&r.v.met!=='Estornado');
  v.k_hoje=ma_nf(hj.reduce((s,r)=>s+Number(r.v.vol||0),0))+' L'; v.k_hojed=hj.length+(hj.length>1?' registros':' registro');
  v.k_conf=String(pend.length); v.k_confd=pend.join(' · ')||'nenhuma'; }
function EXTRAVALS(self,v){
  v.lok=(aid)=>manMudar(self,c=>manLeituraOk(c,aid)); v.ldesc=(aid)=>manMudar(self,c=>manLeituraDescartar(c,aid));
  self.g2after=(gid,rows,r,isNew)=>{ if(gid!=='g_ab'||!r||!isNew) return; const aid=MA_AID[r.v.ativo]; let id='';
    manMudar(self,c=>{ id='AB-'+(1043+c.abast.length); const a=c.ativos[aid]; const d=new Date(); const hh=('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2);
      const m=manLeitura(c,aid,Number(r.v.cont),'Abastecimento '+id,id);
      c.abast.push({id,ativo:r.v.ativo,aid,tq:r.v.tq,vol:r.v.vol,cont:r.v.cont,un:a?a.un:'',op:r.v.op,evid:r.v.evid,dt:'23/09 '+hh,sus:m.sus||''});
      return {msg:'Lançamento '+id+' registrado · '+m.msg}; });
    g2set(self,'g_ab',{rows:null,fl:id}); }; }
'''
    shell37('MA-05','Abastecimentos e desempenho',corpo,
      status=('1 desvio a investigar','yellow'),steps=faixa(5))

# =====================================================================================
# Planos de manutenção (PM.dc.html) — espelho dos Planos agronômicos: 1 Escolha o plano · 2 Edite os serviços · 3 Publique a versão
PM_N=['Escolha o plano','Edite os serviços','Publique a versão']
PM_JS=r'''
const PM_N=['Escolha o plano','Edite os serviços','Publique a versão'];
const PM_GR=['Tratores','Pulverizadores','Plantadeiras','Colhedoras','Implementos','Irrigação','Beneficiamento','Armazenagem','Veículos'];
const PM_CC={green:['#1E7A4C','#E4F3E9'],yellow:['#8A5A00','#FFF3D6'],red:['#B42318','#FDE8E6'],gray:['#5B6660','#EEF1EE']};
function pmChip(c){ const k=PM_CC[c]||PM_CC.gray; return 'display:inline-flex;align-items:center;padding:2px 9px;border-radius:999px;font-size:11.5px;font-weight:700;white-space:nowrap;color:'+k[0]+';background:'+k[1]+';'; }
const PM_QCH='font-family:inherit;font-size:12px;font-weight:700;padding:4px 11px;border-radius:999px;cursor:pointer;';
const PM_IN='font-family:inherit;font-size:13.5px;padding:8px 10px;border-radius:9px;box-sizing:border-box;width:100%;background:#fff;color:#15201A;';
const PM_BASE={exec:'Data e leitura da execução',prog:'Vencimento programado'};
function pmPlans(c){ return c.ordemPlanos.map(id=>c.planos[id]).filter(Boolean); }
function pmEst(p){ if(p.estado==='Inativo') return ['Inativo','gray']; if(!p.versao) return ['Rascunho v1','yellow']; if(p.rasc) return ['Rascunho v'+p.rasc.v+' em edição','yellow']; return ['Publicado','green']; }
function pmVincs(c,pid){ return Object.keys(c.vinc).filter(k=>k.split('|')[0]===pid); }
function pmSemPlano(c){ return c.ordem.map(id=>c.ativos[id]).filter(a=>a&&!Object.keys(c.vinc).some(k=>k.split('|')[1]===a.id)&&!pmPlans(c).some(p=>p.estado!=='Inativo'&&manCabe(c,p,a))); }
function pmCands(c,p){ return c.ordem.map(id=>c.ativos[id]).filter(a=>a&&manCabe(c,p,a)&&!c.vinc[p.id+'|'+a.id]); }
function pmUnits(c,p){ const u={n:0}; c.ordem.forEach(id=>{ const a=c.ativos[id]; if(a&&(manCabe(c,p,a)||c.vinc[p.id+'|'+a.id])){ u.n++; if(a.un) u[a.un]=1; } }); return u; }
function pmNum(x){ const t=String(x===undefined||x===null?'':x).trim(); if(!t) return null; const n=Number(t.replace(/\./g,'').replace(',','.')); return isNaN(n)?NaN:n; }
function pmFoco(id,alt){ setTimeout(()=>{ const e=document.getElementById(id)||(alt&&document.getElementById(alt)); if(e) e.focus(); },0); }
// devolve o foco a quem abriu o painel (Esc, Fechar ou Descartar)
function pmRet(self){ const r=document.activeElement; if(!self.state.sv&&!self.state.np&&!self.state.vk) self.__pmRet=(r&&r!==document.body&&!(r.closest&&r.closest('aside')))?r:null; }
function pmBack(self){ setTimeout(()=>{ const r=self.__pmRet; self.__pmRet=null; if(r&&document.contains(r)) r.focus(); },0); }
function pmSit(c,p){ if(p.estado==='Inativo') return {t:'Inativo · não gera vencimentos',c:'gray'}; if(!p.versao) return {t:'Publique para gerar vencimentos',c:'gray'};
  const ls=manLinhas(c,p.id).filter(l=>l.s); if(!ls.length) return {t:'Sem ativos vinculados',c:'gray'};
  const n={}; ls.forEach(l=>{ n[l.x.sit]=(n[l.x.sit]||0)+1; });
  const T={'Vencida':['vencida','vencidas'],'Vence em breve':['vence em breve','vencem em breve'],'Em dia':['em dia','em dia']}; const ord=['Vencida','Vence em breve','Em dia'];
  const w=ord.find(k=>n[k]); return {t:ord.filter(k=>n[k]).map(k=>n[k]+' '+T[k][n[k]>1?1:0]).join(' · '),c:MAN_SITC[w]||'gray'}; }
function pmOpen(self,id){ self.setState({pid:id,step:2,del:null,disc:false,inat:false,xs:{},tkd:{},pcd:{},sv:null,np:null,vk:null}); manHash(id); }
function pmStep(self,i){ g2etapa(self,{step:i,del:null,disc:false,inat:false});   // conteúdo novo começa no topo, foco no título (UX-ACAO-UNICA)
  manHash(i>1&&self.state.pid?self.state.pid:''); }
// edição grava no rascunho v(n+1); plano ainda sem versão publicada edita a própria v1
function pmEdit(self,pid,fn){ return manMudar(self,c=>{ const p=c.planos[pid]; const novo=!!p.versao&&!p.rasc; if(novo) p.rasc={v:p.versao+1,servicos:manClone(p.servicos)};
  const r=fn(c,p,manWork(p))||{}; const fim=novo?(' Rascunho v'+p.rasc.v+' criado; a v'+p.versao+' publicada e as ordens abertas não mudam.'):(p.versao?' Gravado no rascunho v'+p.rasc.v+'.':' Gravado na v1 (rascunho).');
  return {msg:(r.msg||'Salvo.')+fim,st:r.st}; }); }
function pmDiff(c,p){ const out=[]; const w=manWork(p); const nt=(s)=>s.tarefas.length+(s.tarefas.length===1?' tarefa':' tarefas');
  if(!p.versao){ w.forEach(s=>out.push({k:'Incluído',c:'green',n:s.nome,t:manGatTxt(s)+' · '+nt(s)})); return out; }
  if(!p.rasc) return out; const pub={}; p.servicos.forEach(s=>{ pub[s.id]=s; }); const seen={};
  const pn=(x)=>{ const it=c.itens[x.item]||{nome:x.item,un:''}; return it.nome+' '+manN(x.qtd,1)+' '+it.un; };
  w.forEach(s=>{ seen[s.id]=1; const o=pub[s.id]; if(!o){ out.push({k:'Incluído',c:'green',n:s.nome,t:manGatTxt(s)+' · '+nt(s)}); return; }
    const ch=[]; if(o.nome!==s.nome) ch.push('nome: '+o.nome+' → '+s.nome); if(manGatTxt(o)!==manGatTxt(s)) ch.push(manGatTxt(o)+' → '+manGatTxt(s));
    if(manTolTxt(o)!==manTolTxt(s)) ch.push('tolerância: '+(manTolTxt(o)||'—')+' → '+(manTolTxt(s)||'—'));
    if((o.base||'exec')!==(s.base||'exec')) ch.push('próximo ciclo conta de: '+PM_BASE[s.base||'exec'].toLowerCase());
    if((o.cumpre||[]).join()!==(s.cumpre||[]).join()) ch.push('cumpre também: '+((s.cumpre||[]).map(id=>(w.find(x=>x.id===id)||{}).nome).filter(Boolean).join(', ')||'nenhum'));
    if(Number(o.tempo)!==Number(s.tempo)) ch.push('tempo: '+manN(o.tempo,1)+' → '+manN(s.tempo,1)+' h'); if(o.esp!==s.esp) ch.push('especialidade: '+o.esp+' → '+s.esp);
    s.tarefas.forEach(t=>{ if(o.tarefas.indexOf(t)<0) ch.push('inclui tarefa “'+t+'”'); }); o.tarefas.forEach(t=>{ if(s.tarefas.indexOf(t)<0) ch.push('retira tarefa “'+t+'”'); });
    const om={}; (o.pecas||[]).forEach(x=>{ om[x.item]=x; }); const sm={}; (s.pecas||[]).forEach(x=>{ sm[x.item]=x; });
    (s.pecas||[]).forEach(x=>{ const y=om[x.item]; if(!y) ch.push('inclui '+pn(x)); else if(Number(y.qtd)!==Number(x.qtd)) ch.push(pn(y)+' → '+manN(x.qtd,1)); });
    (o.pecas||[]).forEach(y=>{ if(!sm[y.item]) ch.push('retira '+pn(y)); });
    if(ch.length) out.push({k:'Alterado',c:'yellow',n:s.nome,t:ch.join(' · ')}); });
  p.servicos.forEach(o=>{ if(!seen[o.id]) out.push({k:'Excluído',c:'red',n:o.nome,t:manGatTxt(o)}); });
  return out; }
function pmCard(self,c,p,sel){ const e=pmEst(p); const si=pmSit(c,p); const nv=pmVincs(c,p.id).length;
  return {nome:p.nome,id:p.id,ver:p.versao?('v'+p.versao):'sem versão publicada',est:e[0],est_st:pmChip(e[1]),apl:p.id+' · '+manAplTxt(c,p),
    svs:manWork(p).map(s=>({t:s.nome,tip:manGatTxt(s)})),sit:si.t,sit_st:'font-weight:700;color:'+(PM_CC[si.c]||PM_CC.gray)[0]+';',
    nat:nv?(nv+(nv>1?' ativos vinculados':' ativo vinculado')):'nenhum ativo vinculado',
    st:'display:flex;flex-direction:column;gap:8px;padding:12px 15px;border-radius:12px;background:#fff;text-align:left;font-family:inherit;color:#15201A;min-width:0;width:100%;box-sizing:border-box;cursor:pointer;'+(p.id===sel?'border:1px solid #1E7A4C;box-shadow:0 0 0 1px #1E7A4C;':'border:1px solid #E4E9E5;'),
    lab:'Abrir plano '+p.id+' · '+p.nome,open:()=>pmOpen(self,p.id)}; }
// ---------- campos dos painéis ----------
function pmFld(self,v,pre,k,isChk){ const st=self.state[pre]; const e=(st.errs||{})[k]||'';
  v[pre+'_'+k]=st.d[k]; v[pre+'_e'+k]=e; v[pre+'_he'+k]=!!e; v[pre+'_st'+k]=PM_IN+'border:1px solid '+(e?'#B42318':'#E4E9E5')+';';
  v[pre+'_set'+k]=(ev)=>{ const cur=self.state[pre]; if(!cur) return; const val=isChk?!!ev.target.checked:ev.target.value; const d=Object.assign({},cur.d,{[k]:val}); const er=Object.assign({},cur.errs||{}); delete er[k];
    self.setState({[pre]:Object.assign({},cur,{d,errs:er,warn:false})}); }; }
function pmHashFim(self){ if((location.hash||'').indexOf('#novo:')===0) manHash(self.state.pid&&(self.state.step||1)>1?self.state.pid:''); }
function pmPanel(self,v,pre,o){ const st=self.state[pre]; v[pre+'_open']=!!st; if(!st){ v[pre+'_titulo']=''; v[pre+'_sub']=''; return false; }
  const fim=()=>{ self.setState({[pre]:null}); pmHashFim(self); pmBack(self); };
  const close=()=>{ const cur=self.state[pre]; if(cur&&JSON.stringify(cur.d)!==cur.orig&&!cur.warn){ self.setState({[pre]:Object.assign({},cur,{warn:true})}); return; } fim(); };
  self['__pmClose_'+pre]=close; ma_modalDoc(self,()=>{ const q=['sv','np','vk'].find(x=>self.state[x]); return q?{root:document.getElementById(q+'-painel'),close:()=>self['__pmClose_'+q]()}:null; });
  v[pre+'_titulo']=o.titulo; v[pre+'_sub']=o.sub; v[pre+'_close']=close;
  v[pre+'_key']=(e)=>{ if(!e) return; if(e.key==='Escape'){ e.preventDefault(); close(); } else ma_trap(e,document.getElementById(pre+'-painel')); };
  v[pre+'_save']=o.save; v[pre+'_warn']=!!st.warn; v[pre+'_discard']=fim; v[pre+'_keep']=()=>self.setState({[pre]:Object.assign({},self.state[pre],{warn:false})});
  v[pre+'_nerr']=Object.keys(st.errs||{}).length>0; return true; }
// ---------- serviço (gatilhos, tolerância, base, cumpre também, tempo, especialidade) ----------
function pmSvOpen(self,c,p,sid){ pmRet(self); const s=sid?manWork(p).find(x=>x.id===sid):null; const g=s?s.gat:{}, t=s?(s.tol||{}):{};
  const f=(n)=>(n===undefined||n===null||n==='')?'':String(n).replace('.',',');
  const d={nome:s?s.nome:'',h:f(g.h),km:f(g.km),d:f(g.d),th:f(t.h),tkm:f(t.km),td:f(t.d),base:s?(s.base||'exec'):'exec',cumpre:s?(s.cumpre||[]).slice():[],tempo:s?f(s.tempo):'',esp:s?s.esp:''};
  self.setState({sv:{pid:p.id,sid:sid||null,d,orig:JSON.stringify(d),errs:{},warn:false},np:null,vk:null}); pmFoco('sv_nome'); }
function pmSvSave(self){ const st=self.state.sv; const d=st.d; const errs={}; const c=manGet(); const p=c.planos[st.pid]; const U=pmUnits(c,p);
  if(!String(d.nome).trim()) errs.nome='Informe o nome do serviço.'; else if(manWork(p).some(x=>x.id!==st.sid&&x.nome.toLowerCase()===String(d.nome).trim().toLowerCase())) errs.nome='Já existe um serviço com este nome no plano.';
  else { const dup=pmVincs(c,p.id).map(k=>{ const aid=k.split('|')[1]; const x=manDupServ(c,p.id,aid,[String(d.nome).trim()]); return x?(manNome(c.ativos[aid])+' já faz '+x.s+' pelo '+x.pid+'.'):''; }).find(Boolean); if(dup) errs.nome=dup; }
  const g={}, t={}; [['h','th'],['km','tkm'],['d','td']].forEach(([k,tk])=>{ const n=pmNum(d[k]), m=pmNum(d[tk]);
    if(n!==null){ if(isNaN(n)||n<=0) errs[k]='Maior que zero.'; else g[k]=n; }
    if(m!==null){ if(isNaN(m)||m<0) errs[tk]='Zero ou mais.'; else if(!n) { if(m>0) errs[tk]='Informe o intervalo.'; } else if(m>=n) errs[tk]='Menor que o intervalo.'; else t[k]=m; } });
  if(!Object.keys(g).length&&!errs.h&&!errs.km&&!errs.d) errs.h='Informe ao menos um gatilho: horas, km ou dias.';
  if(g.km&&U.n&&!U.km) errs.km='Nenhum ativo deste plano tem odômetro.';
  if(g.h&&U.n&&!U.h) errs.h='Nenhum ativo deste plano tem horímetro.';
  const tempo=pmNum(d.tempo); if(tempo===null||isNaN(tempo)||tempo<=0) errs.tempo='Informe o tempo em horas.';
  if(!d.esp) errs.esp='Escolha a especialidade.';
  if(Object.keys(errs).length){ self.setState({sv:Object.assign({},st,{errs,warn:false})}); return; }
  pmEdit(self,p.id,(c2,p2,w)=>{ let s=st.sid?w.find(x=>x.id===st.sid):null; const novo=!s;
    if(novo){ const n=w.reduce((m,x)=>Math.max(m,Number(String(x.id).slice(1))||0),0)+1; s={id:'s'+n,tarefas:[],pecas:[]}; w.push(s); }
    Object.assign(s,{nome:String(d.nome).trim(),gat:g,tol:t,base:d.base||'exec',cumpre:d.cumpre.filter(id=>id!==s.id&&w.some(x=>x.id===id)),tempo,esp:d.esp});
    const xs=Object.assign({},self.state.xs||{}); xs[s.id]=true;
    return {msg:(novo?'Serviço incluído: ':'Serviço salvo: ')+s.nome+' · '+manGatTxt(s)+'.',st:{sv:null,xs,flash:s.id}}; }); }
// ---------- novo plano ----------
// pid = editar nome e "Aplica-se a" de um plano existente (os vínculos ficam)
function pmNovo(self,c,aid,pid){ pmRet(self); const a=aid?c.ativos[aid]:null; const p=pid?c.planos[pid]:null;
  const d=p?{nome:p.nome,tipo:p.aplica.t,modelo:p.aplica.t==='modelo'?p.aplica.v[0]:'',ativos:p.aplica.t==='ativos'?p.aplica.v.slice():[],base:''}
           :{nome:a?(a.nome+' · preventiva'):'',tipo:a?'ativos':'modelo',modelo:'',ativos:a?[a.id]:[],base:''};
  self.setState({np:{pid:pid||null,d,orig:JSON.stringify(d),errs:{},warn:false},sv:null,vk:null}); pmFoco('np_nome'); }
// outro plano ativo que já cobre o modelo ou os ativos escolhidos (aviso, não trava)
function pmCobertos(c,d,pid){ const as=d.tipo==='modelo'?c.ordem.map(x=>c.ativos[x]).filter(a=>a&&a.modelo===d.modelo):(d.ativos||[]).map(x=>c.ativos[x]).filter(Boolean); const out=[];
  as.forEach(a=>{ pmPlans(c).forEach(p=>{ if(p.id===pid||p.estado==='Inativo') return; if(manCabe(c,p,a)||c.vinc[p.id+'|'+a.id]){ const t=a.nome+' já está no '+p.id; if(out.indexOf(t)<0) out.push(t); } }); });
  return out; }
function pmNpSave(self){ const st=self.state.np, d=st.d, errs={}; const c=manGet();
  if(!String(d.nome).trim()) errs.nome='Informe o nome do plano.'; else if(pmPlans(c).some(x=>x.id!==st.pid&&x.nome.toLowerCase()===String(d.nome).trim().toLowerCase())) errs.nome='Já existe um plano com este nome.';
  if(d.tipo==='modelo'&&!d.modelo) errs.modelo='Escolha o modelo.'; if(d.tipo==='ativos'&&!d.ativos.length) errs.ativos='Marque ao menos um ativo.';
  if(Object.keys(errs).length){ self.setState({np:Object.assign({},st,{errs,warn:false})}); return; }
  if(st.pid){ manMudar(self,c2=>{ const p=c2.planos[st.pid]; if(!p) throw new Error('Plano não encontrado.'); p.nome=String(d.nome).trim(); p.aplica={t:d.tipo,v:d.tipo==='modelo'?[d.modelo]:d.ativos.slice()};
      const as=d.tipo==='modelo'?c2.ordem.map(x=>c2.ativos[x]).filter(a=>a.modelo===d.modelo):d.ativos.map(x=>c2.ativos[x]); if(as[0]) p.grupo=as[0].grupo;
      const nv=pmCands(c2,p).length; return {msg:p.id+' salvo · '+manAplTxt(c2,p)+(nv?' · '+nv+(nv>1?' ativos a vincular':' ativo a vincular'):'')+'.',st:{np:null}}; }); pmBack(self); return; }
  const r=manMudar(self,c2=>{ const id='PM-'+String(c2.seqpm).padStart(2,'0'); c2.seqpm++; const base=d.base?c2.planos[d.base]:null;
    const as=d.tipo==='modelo'?c2.ordem.map(x=>c2.ativos[x]).filter(a=>a.modelo===d.modelo):d.ativos.map(x=>c2.ativos[x]);
    c2.planos[id]={id,nome:String(d.nome).trim(),grupo:(as[0]||{}).grupo||'Implementos',aplica:{t:d.tipo,v:d.tipo==='modelo'?[d.modelo]:d.ativos.slice()},estado:'Ativo',versao:0,
      servicos:base?manClone(manWork(base)):[],rasc:null,hist:[]}; c2.ordemPlanos.push(id);
    return {msg:'Plano '+id+' criado em rascunho v1'+(base?' com os serviços de '+base.id:'')+' · inclua os serviços, vincule os ativos e publique.',st:{np:null,pid:id,step:2,gf:'',xs:{}},id}; });
  if(r&&r.id) manHash(r.id); }
// ---------- vincular ativo (marco inicial) ----------
function pmVkOpen(self,c,p,aid){ pmRet(self); const cs=pmCands(c,p); if(!cs.length){ self.setState({g2toast:'Todos os ativos deste plano já estão vinculados.'}); return; } const a0=aid||((cs[0]||{}).id)||''; const d={aid:a0,data:'',leit:'',sem:false};
  self.setState({vk:{pid:p.id,d,orig:JSON.stringify(d),errs:{},warn:false},sv:null,np:null}); pmFoco('vk_data','vk-painel'); }
function pmVkSave(self){ const st=self.state.vk, d=st.d, errs={}; const c=manGet(); const a=c.ativos[d.aid];
  if(!a) errs.aid='Escolha o ativo.';
  if(a&&!d.sem){ if(!d.data) errs.data='Informe a data ou marque sem histórico.'; else if(d.data>c.hoje) errs.data='A data não pode ser futura.';
    if(a.un){ const n=pmNum(d.leit); if(n===null||isNaN(n)) errs.leit='Informe a leitura na última execução.'; else if(n<0) errs.leit='Zero ou mais.'; else if(a.leit&&n>a.leit.val) errs.leit='Maior que a leitura atual ('+manLeitTxt(a)+').'; } }
  if(a&&!errs.aid){ const p=c.planos[st.pid]; const dup=manDupServ(c,st.pid,a.id,manWork(p).concat(manPub(p)).map(s=>s.nome)); if(dup) errs.aid=manNome(a)+' já faz '+dup.s+' pelo '+dup.pid+'; um serviço por ativo evita ordem em dobro.'; }
  if(Object.keys(errs).length){ self.setState({vk:Object.assign({},st,{errs,warn:false})}); return; }
  manMudar(self,c2=>{ const a2=c2.ativos[d.aid]; const m=d.sem?{data:c2.hoje,leit:(a2.leit?a2.leit.val:null),om:null,est:true}:{data:d.data,leit:a2.un?pmNum(d.leit):null,om:null,est:false};
    c2.vinc[st.pid+'|'+d.aid]={marco:m,ult:{}}; const ls=manLinhas(c2,st.pid).filter(l=>l.aid===d.aid&&l.s);
    return {msg:manNome(a2)+' vinculado ao '+st.pid+(m.est?' com marco estimado (hoje)':'')+(ls.length?' · '+ls.map(l=>l.s.nome+': '+l.x.sit.toLowerCase()).join(' · '):' · os vencimentos começam quando o plano for publicado')+'.',st:{vk:null}}; }); }
// ---------- publicar ----------
function pmPub(self){ const pid=self.state.pid; manMudar(self,c=>{ const p=c.planos[pid]; if(!p) throw new Error('Escolha um plano.'); if(p.versao&&!p.rasc) return {nada:true,msg:'Nada a publicar: edite os serviços na etapa 2.'};
  const w=manWork(p); if(!w.length) throw new Error('Inclua ao menos um serviço antes de publicar.');
  const sg=w.find(s=>!Object.keys(s.gat||{}).length); if(sg) throw new Error('“'+sg.nome+'” está sem gatilho.');
  const sk=w.find(s=>!s.tarefas.length); if(sk) throw new Error('“'+sk.nome+'” está sem tarefas no checklist.');
  const nv=p.versao?p.rasc.v:1; if(p.rasc){ p.servicos=p.rasc.servicos; p.rasc=null; } p.versao=nv; const h=String(c.hoje).split('-'); p.hist.unshift({v:nv,at:h[2]+'/'+h[1]+'/'+h[0]});
  const ab=Object.values(c.oms).filter(o=>o.pid===pid&&['A liberar','Liberadas','Em execução'].indexOf(o.etapa)>=0);
  const ls=manLinhas(c,pid).filter(l=>l.s); const dv=ls.filter(l=>manDevida(l)&&!l.om);
  return {msg:pid+' v'+nv+' publicada'+(ab.length?' · '+ab.map(o=>o.id+' segue na v'+o.ver).join(', '):'')+' · '+(ls.length?(dv.length?dv.length+(dv.length>1?' vencimentos sem ordem':' vencimento sem ordem'):'vencimentos recalculados pela v'+nv):'vincule os ativos para gerar vencimentos')+'.',st:{step:2}}; }); }
// ---------- etapa 2: serviço na linha + checklist e peças editáveis na expansão ----------
function pmPcSet(self,sid,patch){ const n=Object.assign({},self.state.pcd||{}); n[sid]=Object.assign({item:'',q:'',err:''},n[sid]||{},patch); self.setState({pcd:n}); }
function pmTkAdd(self,p,s){ const tk=(self.state.tkd||{})[s.id]||{v:''}; const t=String(tk.v||'').trim(); const set=(o)=>{ const n=Object.assign({},self.state.tkd||{}); n[s.id]=o; self.setState({tkd:n}); };
  if(!t){ set({v:'',err:'Escreva a tarefa.'}); return; } if(s.tarefas.some(x=>x.toLowerCase()===t.toLowerCase())){ set({v:t,err:'Esta tarefa já está no checklist.'}); return; }
  const r=pmEdit(self,p.id,(c2,p2,w)=>{ w.find(y=>y.id===s.id).tarefas.push(t); return {msg:'Tarefa incluída em '+s.nome+': '+t+'.'}; }); if(!r.erro){ set({v:'',err:''}); pmFoco('pm-tk-'+s.id); } }
function pmPcAdd(self,p,s){ const d=(self.state.pcd||{})[s.id]||{item:'',q:''}; const n=pmNum(d.q);
  if(!d.item){ pmPcSet(self,s.id,{err:'Escolha o item do estoque.'}); return; } if(n===null||isNaN(n)||n<=0){ pmPcSet(self,s.id,{err:'Informe a quantidade, maior que zero.'}); return; }
  const it=manGet().itens[d.item]; const r=pmEdit(self,p.id,(c2,p2,w)=>{ w.find(y=>y.id===s.id).pecas.push({item:d.item,qtd:n}); return {msg:'Peça incluída em '+s.nome+': '+it.nome+' '+manN(n,1)+' '+it.un+'.'}; });
  if(!r.erro) pmPcSet(self,s.id,{item:'',q:'',err:''}); }
function pmSvV(self,c,p,s,pub){ const xs=self.state.xs||{}; const open=!!xs[s.id]; const del=self.state.del===s.id; const o=pub[s.id];
  let chg=''; if(p.rasc&&p.versao){ if(!o) chg='Novo'; else if(JSON.stringify(o)!==JSON.stringify(s)) chg='Alterado'; }
  const w=manWork(p); const cum=(s.cumpre||[]).map(id=>(w.find(x=>x.id===id)||{}).nome).filter(Boolean);
  const tk=(self.state.tkd||{})[s.id]||{v:'',err:''}; const pc=(self.state.pcd||{})[s.id]||{item:'',q:'',err:''}; const ja={}; (s.pecas||[]).forEach(x=>{ ja[x.item]=1; });
  const np=(s.pecas||[]).length; const nv=p.rasc?p.rasc.v:p.versao+1;
  return {nome:s.nome,chg,hasChg:!!chg,chgst:pmChip(chg==='Novo'?'green':'yellow'),gat:manGatTxt(s)+(Object.keys(s.gat||{}).length>1?' · o que vencer primeiro':''),tol:manTolTxt(s)||'sem tolerância',
    cum:cum.length?('cumpre também '+cum.join(', ')):'',hasCum:!!cum.length,cont:s.tarefas.length+(s.tarefas.length===1?' tarefa':' tarefas')+' · '+np+(np===1?' peça':' peças'),
    tempo:manN(s.tempo,1)+' h · '+s.esp,open:String(open),isOpen:open,sym:open?'▾':'▸',lab:(open?'Recolher checklist e peças de ':'Mostrar checklist e peças de ')+s.nome,
    tog:()=>{ const n=Object.assign({},self.state.xs||{}); n[s.id]=!open; self.setState({xs:n}); },edit:()=>pmSvOpen(self,manGet(),p,s.id),
    rst:self.state.flash===s.id?'background:#E4F3E9;':'',asking:del,notAsking:!del,ask:()=>self.setState({del:s.id}),no:()=>self.setState({del:null}),
    yes:()=>pmEdit(self,p.id,(c2,p2,w2)=>{ const i=w2.findIndex(x=>x.id===s.id); if(i>=0) w2.splice(i,1); w2.forEach(x=>{ x.cumpre=(x.cumpre||[]).filter(id=>id!==s.id); }); return {msg:'Serviço excluído: '+s.nome+'.',st:{del:null}}; }),
    dlab:'Excluir serviço '+s.nome,delmsg:'Excluir “'+s.nome+'”'+(p.versao?' do rascunho v'+nv+'? A v'+p.versao+' publicada e as ordens abertas não mudam.':'?'),
    did:'pm-det-'+s.id,dlab2:'Checklist e peças de '+s.nome,ntar:String(s.tarefas.length),
    tarefas:s.tarefas.map((t,i)=>({t,n:String(i+1),rlab:'Retirar tarefa '+t,rm:()=>pmEdit(self,p.id,(c2,p2,w2)=>{ w2.find(y=>y.id===s.id).tarefas.splice(i,1); return {msg:'Tarefa retirada: '+t+'.'}; })})),
    semTar:!s.tarefas.length,tkid:'pm-tk-'+s.id,tklab:'Nova tarefa de '+s.nome,tkv:tk.v,tkerr:tk.err||'',tkHasErr:!!tk.err,
    tkset:(e)=>{ const n=Object.assign({},self.state.tkd||{}); n[s.id]={v:e.target.value,err:''}; self.setState({tkd:n}); },
    tkkey:(e)=>{ if(e.key==='Enter'){ e.preventDefault(); pmTkAdd(self,p,s); } },tkadd:()=>pmTkAdd(self,p,s),
    pecas:(s.pecas||[]).map((x,i)=>{ const it=c.itens[x.item]||{nome:x.item,un:'',saldo:0,reservado:0}; const disp=it.saldo-it.reservado;
      return {nome:it.nome,q:manN(x.qtd,1)+' '+it.un,saldo:(disp>=x.qtd?'saldo ':'falta · saldo ')+manN(disp,1)+' '+it.un,st:pmChip(disp>=x.qtd?'gray':'red'),rlab:'Retirar peça '+it.nome,
        rm:()=>pmEdit(self,p.id,(c2,p2,w2)=>{ w2.find(z=>z.id===s.id).pecas.splice(i,1); return {msg:'Peça retirada: '+it.nome+'.'}; })}; }),
    semPecas:!np,temPecas:!!np,
    pcopts:[{v:'',t:'Item do estoque'}].concat(Object.keys(c.itens).filter(k=>!ja[k]).map(k=>({v:k,t:c.itens[k].nome+' ('+c.itens[k].un+')'}))),
    pcitem:pc.item,pcq:pc.q,pcerr:pc.err||'',pcHasErr:!!pc.err,pcun:(pc.item&&c.itens[pc.item])?c.itens[pc.item].un:'',
    pcsetitem:(e)=>{ pmPcSet(self,s.id,{item:e.target.value,err:''}); if(e.target.value) pmFoco('pm-pcq-'+s.id); },pcsetq:(e)=>pmPcSet(self,s.id,{q:e.target.value,err:''}),
    pckey:(e)=>{ if(e.key==='Enter'){ e.preventDefault(); pmPcAdd(self,p,s); } },pcadd:()=>pmPcAdd(self,p,s),pcid:'pm-pc-'+s.id,pcqid:'pm-pcq-'+s.id,pclab:'Peça para '+s.nome,pcqlab:'Quantidade da peça para '+s.nome}; }
function pmS2(self,v,c,p){ const st=self.state; const e=pmEst(p); v.p_nome=p.id+' · '+p.nome; v.p_est=e[0]; v.p_est_st=pmChip(e[1]);
  const nv=pmVincs(c,p.id).length; v.p_meta=manAplTxt(c,p)+' · '+(p.versao?'v'+p.versao+' em vigor':'sem versão publicada')+' · '+nv+(nv===1?' ativo vinculado':' ativos vinculados');
  const inatFaz=()=>manMudar(self,c2=>{ c2.planos[p.id].estado='Inativo'; return {msg:p.id+' inativo · para de gerar vencimentos; nada foi apagado e as ordens abertas seguem.',st:{inat:false}}; });
  // inativar com vencida, vencendo ou ordem aberta pede confirmação (a pendência some dos indicadores)
  const dv=manLinhas(c,p.id).filter(l=>l.s&&manDevida(l)); const oa=Object.values(c.oms).filter(o=>o.pid===p.id&&manAberta(o)&&o.etapa!=='Em conferência');
  v.p_podeInat=p.estado!=='Inativo'&&!!p.versao&&!st.inat; v.p_inat=()=>{ if(dv.length||oa.length) self.setState({inat:true}); else inatFaz(); };
  v.inat_ask=!!st.inat&&p.estado!=='Inativo'; v.inat_t=p.id+' tem '+[dv.length?dv.map(l=>l.a.nome+' · '+l.s.nome+' '+l.x.sit.toLowerCase()).join(', '):'',oa.length?oa.map(o=>o.id).join(', ')+(oa.length>1?' abertas':' aberta'):''].filter(Boolean).join(' e ')+'. Inativar tira o plano dos vencimentos.';
  v.inat_yes=inatFaz; v.inat_no=()=>self.setState({inat:false}); v.p_edit=()=>pmNovo(self,manGet(),null,p.id);
  v.ban_i=p.estado==='Inativo'; v.ban_reat=()=>manMudar(self,c2=>{ const pp=c2.planos[p.id]; const nomes=manPub(pp).map(x=>x.nome);
    const dup=pmVincs(c2,p.id).map(k=>{ const aid=k.split('|')[1]; const x=manDupServ(c2,p.id,aid,nomes); return x?(manNome(c2.ativos[aid])+' já faz '+x.s+' pelo '+x.pid):''; }).find(Boolean);
    if(dup) throw new Error('Não reativado: '+dup+'.'); pp.estado='Ativo'; return {msg:p.id+' reativado · vencimentos recalculados.'}; });
  v.ban_r=!!p.rasc&&!v.ban_i; v.ban_t=p.rasc?('Rascunho v'+p.rasc.v+' em edição · vencimentos e ordens seguem a v'+p.versao+' até publicar.'):'';
  v.ban_n=!p.versao&&!v.ban_i;
  v.nodisc=!st.disc; v.disc=!!st.disc; v.disc_ask=()=>self.setState({disc:true}); v.disc_no=()=>self.setState({disc:false});
  v.disc_t='Descartar o rascunho'+(p.rasc?' v'+p.rasc.v:'')+'? A v'+p.versao+' publicada continua valendo.';
  v.disc_yes=()=>manMudar(self,c2=>{ c2.planos[p.id].rasc=null; return {msg:'Rascunho descartado · '+p.id+' segue na v'+p.versao+'.',st:{disc:false}}; });
  v.ban_pub=()=>pmStep(self,3);
  const pub={}; p.servicos.forEach(s=>{ pub[s.id]=s; }); const w=manWork(p);
  v.svs=w.map(s=>pmSvV(self,c,p,s,pub)); v.sv_vazio=!w.length; v.sv_tem=!!w.length;
  const xa=w.length>0&&w.every(s=>(st.xs||{})[s.id]); v.x_lab=xa?'Recolher tudo':'Expandir tudo'; v.x_up=xa; v.x_down=!xa;
  v.x_tog=()=>{ const n={}; if(!xa) w.forEach(s=>{ n[s.id]=true; }); self.setState({xs:n}); };
  v.vk_go=()=>pmVkOpen(self,manGet(),p,null); v.vk_pode=pmCands(c,p).length>0&&p.estado!=='Inativo'; }
function pmS3(self,v,c,p){ const nv=p.versao?(p.rasc?p.rasc.v:null):1; v.s3_has=!!nv; v.s3_none=!nv;
  v.dif_tit=p.versao?('Alterações do rascunho v'+nv+' em relação à v'+p.versao):'Primeira versão do plano (v1)';
  v.dif=pmDiff(c,p).map(d=>({k:d.k,st:pmChip(d.c),n:d.n,t:d.t})); v.dif_vazio=!!nv&&!v.dif.length;
  const ab=Object.values(c.oms).filter(o=>o.pid===p.id&&['A liberar','Liberadas','Em execução'].indexOf(o.etapa)>=0);
  v.oab=ab.map(o=>({id:o.id,h:'MA-04.dc.html#'+o.id,t:manNome(c.ativos[o.aid])+' · '+o.serv,f:o.etapa,fst:pmChip(o.etapa==='A liberar'?'gray':'green'),ver:'nasceu na v'+o.ver+' · segue na v'+o.ver})); v.tem_oab=ab.length>0;
  const na=pmVincs(c,p.id).length;
  v.imp=nv?(na?('Vencimentos de '+na+(na>1?' ativos':' ativo')+' passam à v'+nv+'.'):'Nenhum ativo vinculado.'):'';
  v.hist=(p.rasc?[{t:'v'+p.rasc.v,at:'rascunho em edição',st:'Rascunho',stst:pmChip('yellow')}]:(!p.versao?[{t:'v1',at:'rascunho em edição',st:'Rascunho',stst:pmChip('yellow')}]:[]))
    .concat((p.hist||[]).map(h=>({t:'v'+h.v,at:'publicada em '+h.at,st:h.v===p.versao?'Em vigor':'Substituída',stst:pmChip(h.v===p.versao?'green':'gray')}))); }
function pmSvP(self,v,c){ const st=self.state.sv; const p=st?c.planos[st.pid]:null;
  if(!pmPanel(self,v,'sv',{titulo:st&&st.sid?'Editar serviço':'Incluir serviço',sub:p?(p.id+' · '+(p.versao?'grava no rascunho v'+(p.rasc?p.rasc.v:p.versao+1)+'; a v'+p.versao+' e as ordens abertas não mudam.':'grava na v1 em rascunho.')):'',save:()=>pmSvSave(self)})){ v.sv_bases=[]; v.sv_esps=[]; v.sv_cum=[]; return; }
  ['nome','h','km','d','th','tkm','td','base','tempo','esp'].forEach(k=>pmFld(self,v,'sv',k));
  v.sv_bases=[{v:'exec',t:PM_BASE.exec},{v:'prog',t:PM_BASE.prog}]; v.sv_esps=[{v:'',t:'Escolha a especialidade'}].concat(c.esp.map(x=>({v:x,t:x})));
  const w=p?manWork(p):[]; v.sv_cum=w.filter(x=>x.id!==st.sid).map(x=>({t:x.nome,on:st.d.cumpre.indexOf(x.id)>=0,lab:'Cumpre também '+x.nome,
    tog:()=>{ const cur=self.state.sv; const cu=cur.d.cumpre.slice(); const i=cu.indexOf(x.id); if(i>=0) cu.splice(i,1); else cu.push(x.id); self.setState({sv:Object.assign({},cur,{d:Object.assign({},cur.d,{cumpre:cu}),warn:false})}); }}));
  v.sv_temCum=v.sv_cum.length>0; const U=p?pmUnits(c,p):{n:0};
  v.sv_ghelp=U.n?('Ativos deste plano: '+[U.h?'horímetro (h)':'',U.km?'odômetro (km)':''].filter(Boolean).join(' e ')+((!U.h&&!U.km)?'sem contador · use dias':'')+'. Tolerância do fabricante ou da política.'):'Tolerância do fabricante ou da política.'; }
function pmNpP(self,v,c){ const st=self.state.np; const ed=!!(st&&st.pid);
  if(!pmPanel(self,v,'np',{titulo:ed?'Editar plano':'Novo plano de manutenção',sub:ed?st.pid:'Nasce em rascunho v1.',save:()=>pmNpSave(self)})){ v.np_tipos=[]; v.np_mods=[]; v.np_atvs=[]; v.np_bases=[]; v.np_avs=[]; return; }
  v.np_novo=!ed; const cob=pmCobertos(c,st.d,st.pid); v.np_avs=cob.map(t=>({t})); v.np_temAv=cob.length>0;
  ['nome','tipo','modelo','base'].forEach(k=>pmFld(self,v,'np',k));
  v.np_tipos=[{v:'modelo',t:'Modelo (todos os ativos do modelo)'},{v:'ativos',t:'Ativos específicos'}];
  const mods=[]; c.ordem.forEach(id=>{ const m=c.ativos[id].modelo; if(mods.indexOf(m)<0) mods.push(m); });
  v.np_mods=[{v:'',t:'Escolha o modelo'}].concat(mods.map(m=>({v:m,t:m+' · '+c.ordem.map(id=>c.ativos[id]).filter(a=>a.modelo===m).map(a=>a.nome).join(', ')})));
  v.np_isMod=st.d.tipo==='modelo'; v.np_isAtv=st.d.tipo==='ativos';
  v.np_atvs=c.ordem.map(id=>c.ativos[id]).map(a=>({t:manNome(a),on:st.d.ativos.indexOf(a.id)>=0,
    tog:()=>{ const cur=self.state.np; const l=cur.d.ativos.slice(); const i=l.indexOf(a.id); if(i>=0) l.splice(i,1); else l.push(a.id); const er=Object.assign({},cur.errs||{}); delete er.ativos; self.setState({np:Object.assign({},cur,{d:Object.assign({},cur.d,{ativos:l}),errs:er,warn:false})}); }}));
  const e=(st.errs||{}).ativos||''; v.np_eativos=e; v.np_heativos=!!e;
  v.np_bases=[{v:'',t:'Plano em branco'}].concat(pmPlans(c).map(x=>({v:x.id,t:'Copiar serviços de '+x.id+' · '+x.nome}))); }
function pmVkP(self,v,c){ const st=self.state.vk; const p=st?c.planos[st.pid]:null;
  if(!pmPanel(self,v,'vk',{titulo:'Vincular ativo',sub:p?(p.id+' · '+p.nome+' · o marco é a última execução do serviço.'):'',save:()=>pmVkSave(self)})){ v.vk_ativos=[]; return; }
  ['aid','data','leit'].forEach(k=>pmFld(self,v,'vk',k)); pmFld(self,v,'vk','sem',true);
  const cs=pmCands(c,p); v.vk_temCand=cs.length>0; v.vk_semCand=!cs.length;
  v.vk_ativos=cs.map(a=>({v:a.id,t:manNome(a)})); const a=c.ativos[st.d.aid];
  v.vk_hasCont=!!(a&&a.un)&&!st.d.sem; v.vk_un=a&&a.un?a.un:''; v.vk_isData=!st.d.sem;
  v.vk_ult=a?(a.leit?('Leitura atual: '+manLeitTxt(a)+' · '+a.leit.origem):'Ativo sem contador: só gatilhos por dias.'):''; }
function PREVALS(self,v){ manOuvir(self); const c=manGet(); const G=ma_G('g_pv'); const p=self.state.pid?c.planos[self.state.pid]:null;
  if(!p){ G.rows=[]; v.pv_tem=false; return; }
  const rows=manLinhas(c,p.id).map(l=>ma_linhaVenc(c,l,false));
  pmCands(c,p).forEach(a=>rows.push({id:'cand-'+a.id,v:{prox:null},s:{ativo:manNome(a),sit:'Sem vínculo'},p:{ativo:[{k:'b',t:a.nome},{k:'br',t:''},{k:'mut',t:a.modelo}],serv:[{k:'mut',t:'—'}],
    leit:[{k:'txt',t:manLeitTxt(a)}],prox:[{k:'mut',t:'—'}],sit:[{k:'chip',t:'Sem vínculo',c:'gray'}],acao:[{k:'act',t:'Vincular ativo',fn:'pvinc:'+a.id}]}}));
  G.rows=rows; v.pv_tem=rows.length>0; v.pv_vazio=!rows.length; }
function EXTRAVALS(self,v){ const c=manGet(); const st=self.state; const step=st.step||1; const p=st.pid?c.planos[st.pid]:null; ma_gerarV(self,v); ma_rstV(self,v,'pm');
  if(!self.__hashIni){ self.__hashIni=1; const ab=()=>{ const h=decodeURIComponent((location.hash||'').slice(1)); const cc=manGet();
      if(cc.planos[h]) setTimeout(()=>pmOpen(self,h),0); else if(h.indexOf('novo:')===0&&cc.ativos[h.slice(5)]) setTimeout(()=>pmNovo(self,cc,h.slice(5)),0); };
    ab(); try{ window.addEventListener('hashchange',ab); }catch(e){} }
  for(let i=1;i<=3;i++) v['s'+i]=(step===i);
  const nv=p?(p.versao?(p.rasc?p.rasc.v:null):1):null;
  const whys={}; if(!p){ whys[2]='Escolha um plano'; whys[3]='Escolha um plano'; } else if(!nv) whys[3]='Nada a publicar';
  g2steps(self,v,'stp',3,step,whys);   // só informa (UX-ACAO-UNICA-20261003): avanço e retorno na área de ações
  const ps=pmPlans(c); const gs=PM_GR.filter(g=>ps.some(x=>x.grupo===g)); ps.forEach(x=>{ if(gs.indexOf(x.grupo)<0) gs.push(x.grupo); });
  const gf=gs.indexOf(st.gf)>=0?st.gf:'';
  const ch=(t,n,on,go,lab)=>({t,n:String(n),on:String(!!on),go,lab,st:PM_QCH+(on?'border:1px solid #1E7A4C;background:#1E7A4C;color:#fff;':'border:1px solid #E4E9E5;background:#fff;color:#15201A;')});
  v.pm_qf=[ch('Todos',ps.length,!gf,()=>self.setState({gf:''}),'Mostrar todos os planos')].concat(gs.map(g=>ch(g,ps.filter(x=>x.grupo===g).length,gf===g,()=>self.setState({gf:gf===g?'':g}),gf===g?'Mostrar todos os planos':'Mostrar só '+g)));
  v.lib=gs.filter(g=>!gf||g===gf).map(g=>{ const cs=ps.filter(x=>x.grupo===g); return {t:g,n:cs.length+(cs.length>1?' planos':' plano'),cards:cs.map(x=>pmCard(self,c,x,st.pid))}; });
  const sp=pmSemPlano(c); v.tem_sem=sp.length>0; v.sem_n=sp.length+(sp.length>1?' ativos sem plano':' ativo sem plano'); v.sem=sp.map(a=>({t:a.nome,lab:'Criar plano para '+a.nome,go:()=>pmNovo(self,manGet(),a.id)}));
  if(p){ pmS2(self,v,c,p); pmS3(self,v,c,p); } else { v.svs=[]; v.dif=[]; v.hist=[]; v.oab=[]; }
  v.pvinc=(aid)=>{ const cc=manGet(); const pp=cc.planos[self.state.pid]; if(pp) pmVkOpen(self,cc,pp,aid); };
  pmSvP(self,v,c); pmNpP(self,v,c); pmVkP(self,v,c);
  // ---- área de ações (UX-ACAO-UNICA-20261003 · DS-02, DS-33 §74.5.7.1, DS-61): uma primária e uma rota de avanço por etapa ----
  v.pm_novo=()=>pmNovo(self,manGet(),null); v.pm_incl=()=>{ const cc=manGet(); const pp=cc.planos[self.state.pid]; if(pp) pmSvOpen(self,cc,pp,null); };
  const ir=(i,t)=>({t:'‹ '+t,fn:()=>pmStep(self,i),to:i,a:'voltar'});
  let A={};
  if(step>1&&!p) A={nota:'Nenhum plano aberto: abra um plano da biblioteca.',prim:{t:'‹ Biblioteca de planos',fn:()=>pmStep(self,1),to:1,a:'voltar'}};
  else if(step===2) A={volta:ir(1,'Biblioteca de planos'),prim:{t:(nv?'Revisar e publicar':'Ver versões e ordens')+' ›',fn:()=>pmStep(self,3),to:3,a:'avancar'}};
  else if(step===3) A=nv?{volta:ir(2,'Serviços do plano'),prim:{t:'Publicar v'+nv,fn:()=>pmPub(self),a:'comando'}}
                       :{volta:ir(2,'Serviços do plano'),nota:'Nada a publicar: salvar uma alteração nos serviços cria o rascunho da próxima versão.'};
  g2acoes(v,'aa',A);
  v.go2=()=>pmStep(self,2); }
'''
PM_CSS=('.pm-sv{border:1px solid #E4E9E5;border-radius:12px;background:#fff}'
        '.pm-sv-linha{display:grid;grid-template-columns:30px minmax(0,1.1fr) minmax(0,1.6fr) 130px 160px 34px;gap:10px;align-items:center;padding:8px 10px;font-size:13px}'
        '.pm-sv-det{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px;padding:10px 14px 14px 50px;border-top:1px solid #E4E9E5}'
        '.pm-nome{border:0;background:transparent;padding:0;font-family:inherit;font-size:13.5px;font-weight:800;color:#15201A;cursor:pointer;text-align:left;text-decoration:underline;text-decoration-color:#C9D3CC;text-underline-offset:3px}'
        '.pm-nome:hover{color:#1E7A4C}.pm-x{width:26px;height:26px;border:0;border-radius:6px;background:transparent;cursor:pointer;color:#8A968E;font-size:16px;line-height:1;flex-shrink:0}'
        '.pm-x:hover{background:#FDE8E6;color:#B42318}.pm-sv-linha button:focus-visible,.pm-x:focus-visible,.pm-nome:focus-visible{outline:2px solid #1E7A4C;outline-offset:2px}')
LBL=f'font-size: 12px; font-weight: 600; color: {MUTED};'
SEC=f'font-size: 11px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;'
ERRS=f'font-size: 12px; font-weight: 700; color: {RED};'
LNK=f'border: 0; background: transparent; padding: 4px 2px; font-family: inherit; font-size: 12.5px; font-weight: 700; color: #4B5A51; text-decoration: underline; text-underline-offset: 3px; cursor: pointer;'

def _bloco(titulo,desc,corpo,acao='',hole=False):
    t=titulo if hole else esc(titulo); d=desc if hole else esc(desc)
    return (f'<section style="background: {SURF}; border: 1px solid {LINE}; border-radius: 14px; display: flex; flex-direction: column; min-width: 0;">'
            f'<div style="display: flex; align-items: flex-start; gap: 10px; padding: 12px 16px 10px;"><div style="display: flex; flex-direction: column; gap: 2px; flex-grow: 1; min-width: 0;">'
            f'<h3 style="margin: 0; font-size: 15px; font-weight: 800; letter-spacing: -.01em;">{t}</h3>'+(f'<div style="font-size: 12.8px; color: {MUTED};">{d}</div>' if d else '')+f'</div>{acao}</div>'
            f'<div style="padding: 0 16px 14px; display: flex; flex-direction: column; gap: 10px;">{corpo}</div></section>')

def _aside(pre,corpo,w=520):
    """Painel lateral com Salvar/Cancelar e aviso de alterações não salvas (holes {pre}_open/_close/_key/_save/_warn/_discard/_keep/_nerr/_titulo/_sub)."""
    return IF(f'{pre}_open',
        f'<div style="position: fixed; inset: 0; z-index: 60; display: flex; justify-content: flex-end;">'
        f'<button type="button" aria-label="Fechar" tabIndex="-1" onClick="{H(pre+"_close")}" style="position: absolute; inset: 0; border: 0; background: rgba(21,32,26,.32); cursor: pointer;"></button>'
        f'<aside id="{pre}-painel" tabIndex="-1" role="dialog" aria-modal="true" aria-label="{H(pre+"_titulo")}" onKeyDown="{H(pre+"_key")}" style="outline: none; position: relative; width: {w}px; max-width: 100%; height: 100vh; overflow-y: auto; background: {SURF}; box-shadow: -12px 0 40px -12px rgba(21,32,26,.35); padding: 22px 24px; box-sizing: border-box; display: flex; flex-direction: column; gap: 14px;">'
        f'<div style="display: flex; gap: 10px; align-items: flex-start;"><h2 style="margin: 0; font-family: {DISP}; font-size: 19px; flex-grow: 1; letter-spacing: -.02em;">{H(pre+"_titulo")}</h2>'
        f'<button type="button" aria-label="Fechar" title="Fechar" onClick="{H(pre+"_close")}" style="border: 0; background: {BG}; width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 18px; color: {MUTED}; flex-shrink: 0;">×</button></div>'
        f'<div style="font-size: 13px; color: {MUTED}; line-height: 1.45; margin-top: -6px;">{H(pre+"_sub")}</div>'
        + IF(f'{pre}_nerr',f'<div role="alert" style="padding: 8px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">Corrija os campos destacados; o que você preencheu foi mantido.</div>')
        + corpo + '<div style="flex-grow: 1;"></div>'
        + IF(f'{pre}_warn',f'<div role="alert" class="saida" style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">Há alterações não salvas.'
             f'<div style="display: flex; gap: 8px;"><button type="button" onClick="{H(pre+"_discard")}" style="{_MINI}">Descartar alterações</button><button type="button" onClick="{H(pre+"_keep")}" style="{_MINIP}">Continuar editando</button></div></div>')
        + f'<div class="pe-form" style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 8px; border-top: 1px solid {LINE};">'
          f'<button type="button" onClick="{H(pre+"_close")}" style="{BTN_ST(False,True)}">Cancelar</button><button type="button" onClick="{H(pre+"_save")}" style="{BTN_ST(True,True)}">Salvar</button></div>'
        f'</aside></div>')

def _err(pre,k): return IF(f'{pre}_he{k}',f'<span role="alert" style="{ERRS}">{H(pre+"_e"+k)}</span>')
def _inp(pre,k,rot,typ='text',num=False,w=None,suf=''):
    inp=(f'<input id="{pre}_{k}" type="{typ}" value="{H(pre+"_"+k)}" onChange="{H(pre+"_set"+k)}"'+(' inputMode="decimal"' if num else '')
         +f' style="{H(pre+"_st"+k)}{(" width: "+w+";") if w else ""}{" text-align: right;" if num else ""}">')
    if suf: inp=f'<span style="display: inline-flex; align-items: center; gap: 6px;">{inp}<span style="font-size: 12.5px; color: {MUTED}; white-space: nowrap;">{suf}</span></span>'
    return f'<div style="display: flex; flex-direction: column; gap: 4px; min-width: 0;"><label for="{pre}_{k}" style="{LBL}">{rot}</label>{inp}{_err(pre,k)}</div>'
def _sel(pre,k,rot,lst):
    return (f'<div style="display: flex; flex-direction: column; gap: 4px; min-width: 0;"><label for="{pre}_{k}" style="{LBL}">{rot}</label>'
            f'<select id="{pre}_{k}" value="{H(pre+"_"+k)}" onChange="{H(pre+"_set"+k)}" style="{H(pre+"_st"+k)}">'
            + FOR(lst,'o',f'<option value="{H("o.v")}">{H("o.t")}</option>',3) + '</select>' + _err(pre,k) + '</div>')
def _checks(lst,rotulo):
    return (f'<div role="group" aria-label="{rotulo}" style="display: flex; flex-wrap: wrap; gap: 6px;">'
            + FOR(lst,'o',f'<label style="display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px; border: 1px solid {LINE}; border-radius: 999px; font-size: 12.5px; cursor: pointer;">'
                  f'<input type="checkbox" checked="{H("o.on")}" onChange="{H("o.tog")}" style="accent-color: {ACC}; margin: 0;">{H("o.t")}</label>',4) + '</div>')

def pm():
    fname='PM.dc.html'; E._reset_screen(fname)
    EXTRA.append('<style>'+PM_CSS+'</style>')
    # UX-ACAO-UNICA-20261003: Novo plano e Incluir serviço são secundários junto da lista/seção (primário só na lista vazia); avançar,
    # voltar e publicar ficam na área de ações única ao fim do conteúdo (engine.area_acoes + g2acoes)
    acao=f'<button type="button" onClick="{H("pm_novo")}" style="{E.BTN_ST(False,True)}">Novo plano</button>'
    incl=(IF('sv_tem',f'<button type="button" data-acao="adicionar" onClick="{H("pm_incl")}" style="{E.BTN_ST(False,True)}">Incluir serviço</button>')
          + IF('sv_vazio',f'<button type="button" data-acao="adicionar" onClick="{H("pm_incl")}" style="{E.BTN_ST(True,True)}">Incluir serviço</button>'))
    # ---------- etapa 1 · biblioteca por classe (cards) + ativos sem plano ----------
    card=(f'<button type="button" onClick="{H("c.open")}" aria-label="{H("c.lab")}" style="{H("c.st")}">'
          f'<span style="display: flex; align-items: flex-start; gap: 8px; width: 100%;"><b style="font-size: 14.5px; flex-grow: 1; line-height: 1.3;">{H("c.nome")}</b>'
          f'<span style="font-size: 12px; font-weight: 700; color: {MUTED}; white-space: nowrap; padding-top: 2px;">{H("c.ver")}</span></span>'
          f'<span style="display: flex; width: 100%;"><span style="{H("c.est_st")}">{H("c.est")}</span></span>'
          f'<span style="font-size: 12.5px; color: {MUTED};">{H("c.apl")}</span>'
          f'<span style="display: flex; flex-wrap: wrap; gap: 4px;">'
          + FOR('c.svs','g',f'<span title="{H("g.tip")}" style="display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: 11.5px; font-weight: 600; color: {INK}; border: 1px solid {LINE};">{H("g.t")}</span>',2) + '</span>'
          f'<span style="display: flex; flex-direction: column; gap: 1px; width: 100%; border-top: 1px solid {LINE}; padding-top: 8px; font-size: 12.5px;"><span style="{H("c.sit_st")}">{H("c.sit")}</span>'
          f'<span style="font-size: 11.5px; color: {MUTED};">{H("c.nat")}</span></span></button>')
    lib=(f'<div style="display: flex; flex-wrap: wrap; gap: 16px 18px; align-items: flex-start;">'
         + FOR('lib','cu',f'<div style="display: flex; flex-direction: column; gap: 8px; padding-top: 4px; min-width: 0; max-width: 100%;"><div style="{SEC}">{H("cu.t")} <span style="font-weight: 600; letter-spacing: 0; text-transform: none;">· {H("cu.n")}</span></div>'
               f'<div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: stretch;">' + FOR('cu.cards','c',f'<div style="display: flex; width: 320px; max-width: 100%;">{card}</div>',2) + '</div></div>',3)
         + '</div>')
    qf=(f'<div role="group" aria-label="Filtrar planos por classe" style="display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 4px;">'
        + FOR('pm_qf','qc',f'<button type="button" aria-pressed="{H("qc.on")}" title="{H("qc.lab")}" onClick="{H("qc.go")}" style="{H("qc.st")}">{H("qc.t")} <span style="opacity: .75;">{H("qc.n")}</span></button>',6) + '</div>')
    sem=IF('tem_sem',f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 10px 12px; border: 1px dashed {LINE}; border-radius: 12px;">'
           f'<span style="font-size: 12.5px; font-weight: 800;">{H("sem_n")}</span>'
           + FOR('sem','a',f'<button type="button" onClick="{H("a.go")}" aria-label="{H("a.lab")}" title="{H("a.lab")}" style="{_MINI}">{H("a.t")} · Criar plano</button>',4) + '</div>')
    s1=_bloco('Biblioteca de planos por classe','',qf+sem+lib+_restaurar('pm'),acao=acao)
    # ---------- etapa 2 · plano aberto ----------
    tk=(f'<li style="display: flex; align-items: center; gap: 8px; padding: 5px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
        f'<span style="font-size: 12px; font-weight: 800; color: {MUTED}; width: 18px; flex-shrink: 0;">{H("t.n")}</span><span style="flex-grow: 1; min-width: 0;">{H("t.t")}</span>'
        f'<button type="button" class="pm-x" aria-label="{H("t.rlab")}" title="Retirar tarefa" onClick="{H("t.rm")}">×</button></li>')
    pc=(f'<div style="display: grid; grid-template-columns: minmax(0, 1fr) 70px auto 26px; gap: 8px; align-items: center; padding: 5px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
        f'<span style="min-width: 0;">{H("p.nome")}</span><span style="text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap;">{H("p.q")}</span><span style="{H("p.st")}">{H("p.saldo")}</span>'
        f'<button type="button" class="pm-x" aria-label="{H("p.rlab")}" title="Retirar peça" onClick="{H("p.rm")}">×</button></div>')
    inl=f'font-family: inherit; font-size: 13px; padding: 6px 9px; border-radius: 8px; border: 1px solid {LINE}; box-sizing: border-box; background: #fff; color: {INK};'
    det=(f'<div class="pm-sv-det" id="{H("s.did")}" role="region" aria-label="{H("s.dlab2")}">'
         f'<div style="display: flex; flex-direction: column; gap: 4px; min-width: 0;"><div style="{SEC}">Checklist · {H("s.ntar")}</div>'
         f'<ol style="margin: 0; padding: 0; list-style: none;">' + FOR('s.tarefas','t',tk,4) + '</ol>'
         + IF('s.semTar',f'<span style="font-size: 12.5px; color: {RED}; font-weight: 700;">Sem tarefas · inclua o checklist antes de publicar.</span>')
         + f'<div style="display: flex; gap: 6px; padding-top: 6px;"><input id="{H("s.tkid")}" aria-label="{H("s.tklab")}" placeholder="Nova tarefa" value="{H("s.tkv")}" onChange="{H("s.tkset")}" onKeyDown="{H("s.tkkey")}" style="{inl} flex-grow: 1; min-width: 0;">'
           f'<button type="button" onClick="{H("s.tkadd")}" style="{_MINI}">Incluir tarefa</button></div>' + IF('s.tkHasErr',f'<span role="alert" style="{ERRS}">{H("s.tkerr")}</span>') + '</div>'
         f'<div style="display: flex; flex-direction: column; gap: 4px; min-width: 0;"><div style="{SEC}">Peças e lubrificantes do estoque</div>'
         + IF('s.temPecas',FOR('s.pecas','p',pc,2)) + IF('s.semPecas',f'<span style="font-size: 12.5px; color: {MUTED};">Sem peças.</span>')
         + f'<div style="display: flex; gap: 6px; padding-top: 6px; flex-wrap: wrap; align-items: center;"><select id="{H("s.pcid")}" aria-label="{H("s.pclab")}" value="{H("s.pcitem")}" onChange="{H("s.pcsetitem")}" style="{inl} flex: 1 1 180px; min-width: 0;">'
           + FOR('s.pcopts','o',f'<option value="{H("o.v")}">{H("o.t")}</option>',4) + '</select>'
           f'<input id="{H("s.pcqid")}" aria-label="{H("s.pcqlab")}" placeholder="Qtd" inputMode="decimal" value="{H("s.pcq")}" onChange="{H("s.pcsetq")}" onKeyDown="{H("s.pckey")}" style="{inl} width: 70px; text-align: right;">'
           f'<span style="font-size: 12px; color: {MUTED}; min-width: 18px;">{H("s.pcun")}</span><button type="button" onClick="{H("s.pcadd")}" style="{_MINI}">Incluir peça</button></div>'
         + IF('s.pcHasErr',f'<span role="alert" style="{ERRS}">{H("s.pcerr")}</span>') + '</div></div>')
    svrow=(f'<div class="pm-sv" style="{H("s.rst")}"><div class="pm-sv-linha">'
           f'<button type="button" class="g2car" aria-label="{H("s.lab")}" title="{H("s.lab")}" aria-expanded="{H("s.open")}" aria-controls="{H("s.did")}" onClick="{H("s.tog")}">{H("s.sym")}</button>'
           f'<span style="display: flex; flex-direction: column; gap: 3px; min-width: 0; align-items: flex-start;"><button type="button" class="pm-nome" onClick="{H("s.edit")}" title="Editar gatilhos, tolerância, tempo e especialidade">{H("s.nome")}</button>'
           + IF('s.hasChg',f'<span style="{H("s.chgst")}">{H("s.chg")}</span>') + '</span>'
           f'<span style="display: flex; flex-direction: column; gap: 2px; min-width: 0;"><b style="font-weight: 700;">{H("s.gat")}</b><span style="font-size: 12px; color: {MUTED};">{H("s.tol")}</span>'
           + IF('s.hasCum',f'<span style="font-size: 12px; color: {MUTED};">{H("s.cum")}</span>') + '</span>'
           f'<span style="font-size: 12.5px; color: {MUTED};">{H("s.cont")}</span><span style="font-size: 12.5px;">{H("s.tempo")}</span>'
           + IF('s.notAsking',f'<button type="button" class="g2del" aria-label="{H("s.dlab")}" title="Excluir serviço" onClick="{H("s.ask")}">{E._TRASH}</button>',True)
           + IF('s.asking','<span></span>') + '</div>'
           + IF('s.asking',f'<div role="alert" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 8px 12px; background: {REDS}; color: {RED}; font-size: 12.5px; font-weight: 700;">'
                f'<span style="flex-grow: 1;">{H("s.delmsg")}</span><button type="button" onClick="{H("s.yes")}" style="{_MINI} color: {RED}; border-color: {RED};">Excluir serviço</button><button type="button" onClick="{H("s.no")}" style="{_MINI}">Manter</button></div>')
           + IF('s.isOpen',det) + '</div>')
    head2=(f'<div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;"><h2 style="margin: 0; font-family: {DISP}; font-size: 20px; letter-spacing: -.02em;">{H("p_nome")}</h2>'
           f'<span style="{H("p_est_st")}">{H("p_est")}</span><span style="font-size: 13px; color: {MUTED};">{H("p_meta")}</span><span style="flex-grow: 1;"></span>'
           + f'<button type="button" onClick="{H("p_edit")}" title="Nome e Aplica-se a" style="{LNK}">Editar plano</button>'
           + IF('p_podeInat',f'<button type="button" onClick="{H("p_inat")}" title="Para de gerar vencimentos; nada é apagado" style="{LNK}">Inativar plano</button>') + '</div>'
           + IF('inat_ask',f'<div role="alert" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 10px 14px; border-radius: 12px; background: {REDS}; color: {RED}; font-size: 13px; font-weight: 700;">'
                f'<span style="flex-grow: 1; min-width: 0;">{H("inat_t")}</span><button type="button" onClick="{H("inat_yes")}" style="{_MINI} color: {RED}; border-color: {RED};">Inativar mesmo assim</button>'
                f'<button type="button" onClick="{H("inat_no")}" style="{_MINI}">Manter ativo</button></div>'))
    ban=(IF('ban_r',f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 10px 14px; border-radius: 12px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700;">'
            f'<span style="flex-grow: 1; min-width: 0;">{H("ban_t")}</span>'
            + IF('nodisc',f'<button type="button" onClick="{H("disc_ask")}" style="{_MINI}">Descartar rascunho</button>',True)
            + IF('disc',f'<span role="alert" style="flex-basis: 100%; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; color: {RED};"><span style="flex-grow: 1;">{H("disc_t")}</span>'
                 f'<button type="button" onClick="{H("disc_yes")}" style="{_MINI} color: {RED}; border-color: {RED};">Descartar rascunho</button><button type="button" onClick="{H("disc_no")}" style="{_MINI}">Manter</button></span>')
            + '</div>')
         + IF('ban_n',f'<div style="display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 12px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700;">'
              f'<span style="flex-grow: 1;">Rascunho v1 · publique para o plano gerar vencimentos.</span></div>')
         + IF('ban_i',f'<div style="display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-radius: 12px; background: {GRAYS}; color: {INK}; font-size: 13px; font-weight: 700;">'
              f'<span style="flex-grow: 1;">Plano inativo · não gera vencimentos; as ordens abertas seguem.</span><button type="button" onClick="{H("ban_reat")}" style="{_MINI}">Reativar plano</button></div>'))
    xbtn=f'<button type="button" class="g2xtog" onClick="{H("x_tog")}" style="flex-shrink: 0;">{E.seta_xtog(H("x_up"),H("x_down"))}{H("x_lab")}</button>'
    svs=(IF('sv_tem',f'<div style="display: flex; flex-direction: column; gap: 8px;">' + FOR('svs','s',svrow,2) + '</div>')
         + IF('sv_vazio',f'<div style="display: flex; align-items: center; gap: 10px; padding: 14px; border: 1px dashed {LINE}; border-radius: 12px; font-size: 13px;">'
              f'<span style="flex-grow: 1;">Nenhum serviço ainda.</span></div>'))
    g_pv=grid(VENC_COLS,[],edit=dict(m='none'),gid='g_pv',total=False,so=dict(k='prox',d=False),qf=dict(k='sit',l='situação'))
    s2=(head2 + ban
        + _bloco('Serviços do plano','',svs,
                 acao=f'<span style="display: inline-flex; gap: 8px; align-items: center;">{IF("sv_tem",xbtn)}{incl}</span>')
        + _bloco('Ativos vinculados e vencimentos','',g_pv,
                 acao=IF('vk_pode',f'<button type="button" onClick="{H("vk_go")}" style="{_MINI} font-size: 13px; padding: 7px 12px;">Vincular ativo</button>')))
    # ---------- etapa 3 · publicar ----------
    dif=(FOR('dif','d',f'<div style="display: grid; grid-template-columns: 86px minmax(0, 1fr); gap: 10px; align-items: baseline; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
                       f'<span><span style="{H("d.st")}">{H("d.k")}</span></span><span><b>{H("d.n")}</b> <span style="color: {MUTED};">· {H("d.t")}</span></span></div>',2)
         + IF('dif_vazio',f'<div style="font-size: 13px; color: {MUTED};">O rascunho está igual à versão publicada.</div>'))
    oab=(FOR('oab','o',f'<div style="display: grid; grid-template-columns: 90px minmax(0, 1fr) 120px minmax(0, 1fr); gap: 10px; align-items: center; padding: 7px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
                     f'<a href="{H("o.h")}" style="color: {ACC}; font-weight: 800; text-decoration: none;">{H("o.id")}</a><span>{H("o.t")}</span><span><span style="{H("o.fst")}">{H("o.f")}</span></span><span style="color: {MUTED};">{H("o.ver")}</span></div>',1))
    s3=(IF('s3_has',_bloco(H('dif_tit'),H('imp'),dif,hole=True))
        + IF('s3_none',_bloco('Nada a publicar','',f'<div style="font-size: 13px; color: {MUTED};">Salvar uma alteração nos serviços cria o rascunho da próxima versão.</div>'))
        + IF('tem_oab',_bloco('Ordens abertas · seguem a versão em que nasceram','',oab))
        + _bloco('Versões','',
                 FOR('hist','h',f'<div style="display: grid; grid-template-columns: 48px 200px 110px; gap: 10px; align-items: center; padding: 6px 0; border-top: 1px solid {LINE}; font-size: 13px;">'
                                f'<b>{H("h.t")}</b><span style="color: {MUTED};">{H("h.at")}</span><span><span style="{H("h.stst")}">{H("h.st")}</span></span></div>',2)))
    corpo=''.join(f'<sc-if value="{H("s"+str(i))}" hint-placeholder-val="{T() if i==1 else F()}"><div style="display: flex; flex-direction: column; gap: 14px;">{s}</div></sc-if>'
                  for i,s in enumerate([s1,s2,s3],1)) + E.area_acoes('aa','Ações da etapa')
    # ---------- painéis: serviço · novo plano · vincular ativo ----------
    tri=lambda a,b,c: f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px;">{a}{b}{c}</div>'
    sv_body=(_inp('sv','nome','Nome do serviço')
             + f'<div style="{SEC}">Gatilhos · o que vencer primeiro</div>'
             + tri(_inp('sv','h','A cada (h)',num=True),_inp('sv','km','A cada (km)',num=True),_inp('sv','d','A cada (dias)',num=True))
             + tri(_inp('sv','th','Tolerância ± h',num=True),_inp('sv','tkm','Tolerância ± km',num=True),_inp('sv','td','Tolerância ± dias',num=True))
             + f'<span style="font-size: 11.5px; color: {MUTED}; margin-top: -6px;">{H("sv_ghelp")}</span>'
             + _sel('sv','base','Próximo ciclo conta de','sv_bases')
             + IF('sv_temCum',f'<div style="display: flex; flex-direction: column; gap: 6px;"><span style="{LBL}">Cumpre também (uma ordem fecha os dois ciclos)</span>'+_checks('sv_cum','Serviços cumpridos junto')+'</div>')
             + f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">{_inp("sv","tempo","Tempo estimado (h)",num=True)}{_sel("sv","esp","Especialidade","sv_esps")}</div>')
    EXTRA.append(_aside('sv',sv_body,w=560))
    np_body=(_inp('np','nome','Nome do plano') + _sel('np','tipo','Aplica-se a','np_tipos')
             + IF('np_isMod',_sel('np','modelo','Modelo','np_mods'))
             + IF('np_isAtv',f'<div style="display: flex; flex-direction: column; gap: 6px;"><span style="{LBL}">Ativos</span>'+_checks('np_atvs','Ativos do plano')+_err('np','ativos')+'</div>')
             + IF('np_temAv',f'<div style="padding: 8px 12px; border-radius: 10px; background: {YELS}; color: {YEL}; font-size: 12.5px; font-weight: 700;">'
                  + FOR('np_avs','a',f'<div>{H("a.t")}</div>',1) + '</div>')
             + IF('np_novo',_sel('np','base','Começar de','np_bases'),True))
    EXTRA.append(_aside('np',np_body,w=520))
    vk_body=(IF('vk_temCand',_sel('vk','aid','Ativo','vk_ativos')
                + f'<span style="font-size: 12px; color: {MUTED}; margin-top: -6px;">{H("vk_ult")}</span>'
                + IF('vk_isData',_inp('vk','data','Data da última execução',typ='date'),True)
                + IF('vk_hasCont',_inp('vk','leit','Leitura na última execução',num=True,w='160px',suf=H('vk_un')))
                + f'<label style="display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600;"><input type="checkbox" checked="{H("vk_sem")}" onChange="{H("vk_setsem")}" style="width: 16px; height: 16px; accent-color: {ACC}; margin: 0;">'
                  f'Sem histórico: usar hoje e a leitura atual (marco estimado)</label>')
             + IF('vk_semCand',f'<div style="font-size: 13px; color: {MUTED};">Todos os ativos deste plano já estão vinculados.</div>'))
    EXTRA.append(_aside('vk',vk_body,w=480))
    EXTRAJS[0]=DM.js_prefixo()+JSBASE+JSVENC+JSRST+PM_JS
    HEIGHTS37[fname]=1500
    shell37('PM','Planos de manutenção',corpo,fname=fname,
            steps=steps_state(PM_N),primary_html=None,search=False)   # faixa só informa; avanço/retorno/publicar na área de ações (UX-ACAO-UNICA-20261003)
    return fname

def build():
    pm(); ma01(); ma02(); ma03(); ma04(); ma04det(); ma05()
