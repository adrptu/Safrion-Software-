# -*- coding: utf-8 -*-
"""Área Configurações (módulo OCULTO do menu, preservado; não sequencial → sem faixa de etapas).
CF-01 Usuários e permissões · CF-02 Alçadas e regras (+ CF-02det AL-05) · CF-03 Integrações e sincronização
(+ CF-03det reconciliação do ERP e conflito offline) · CF-04 Auditoria e parâmetros. CF-05 Assinatura e cobrança está em areas/assinatura.py (PLAT-01).
Padrão v3.7-processos: descrição imperativa sob cada bloco, edição pela linha (G2), ícone + rótulo + title nas ações secundárias.

observacoes (dados locais coerentes com dados.py / dados2.py / telas vizinhas):
- Pessoas: Ana = gestora e agrônoma RT; Caio = PCP; Marcos = operador da OS-0421; João = irrigação; Paula = conferência;
  Rui = estoque (autor da contagem INV-2609 em EST); Beto = convite pendente (IN-02); Davi = acesso revogado.
- DEMO-11 unificado em 40 ha = dia 4 da OS-0421 (dados.OS[0]['dias'][3]); APT-1187, identidade local c9e2-…-4f1a e recibo
  REC-7741 = os mesmos de MB-03 (areas/mobile.py). Relato sobreposto do tablet de Paula: identidade 7b31-…-09d2 (local).
- Divergência de MAP 11-52 no Galpão 2 = dados2.CONTAGENS INV-2609 (90.000 kg → 89.400 kg = −600 kg = −12 sc 50 kg).
- Devolução REQ-031 = dados2.REQUISICOES (20 sc recebidas). NF 4412 (título rejeitado por unidade) é dado local do conector.
"""
import json
from engine import (grid,section,kpis,chip,btn,tag,icon,esc,msgbtn,drawer_button,toolrow,Pt,
                    INK,MUTED,LINE,BG,SURF,ACC,ACCS,YEL,YELS,RED,REDS,GRAY,GRAYS,SH,DISP,BTN_ST,EXTRAJS)
import engine as E
from ui37 import shell37, continuity, HEIGHTS37, PARENT37
import dados as D
import dados2 as D2

H=lambda s: '{{'+s+'}}'
def n0(v): return f'{v:,.0f}'.replace(',','.')
OS0,OS1,OS2,OS3=D.OS[0],D.OS[1],D.OS[2],D.OS[3]
# DEMO-11 · mesmo fato do app (MB-03): dia 4 da OS-0421
APT=dict(id='APT-1187',os=OS0['id'],dia=4,ha=OS0['dias'][3],uuid='c9e2-…-4f1a',recibo='REC-7741')
APT_B=dict(uuid='7b31-…-09d2',disp='Tablet de Paula · conferência')
INV=next(c for c in D2.CONTAGENS if c['id']=='INV-2609')
INV_DIF_KG=INV['contado']-INV['sistema']                       # −600 kg
INV_DIF_SC=INV_DIF_KG//50                                      # −12 sc 50 kg
REQ=next(r for r in D2.REQUISICOES if r['id']=='REQ-031')

# ---------------- helpers ----------------
REV_OK='Vigente · aceita proposta de revisão'
T_UN='Unidade não mapeada · corrija e reprocesse'
T_SB='Sobreposto · decida o conflito'
def C(k,l,**kw): return dict(k=k,l=l,**kw)
def plain(parts): return ' '.join(p['t'] for p in parts if p.get('k')!='br').strip()
def R(id,ro=False,o=None,v=None,extra=None,**cells):
    """linha G2: str/número → v (editável); lista de partes → p (exibição rica, busca por texto)."""
    r=dict(id=id,v=dict(v or {}),s={},p={})
    for k,x in cells.items():
        if isinstance(x,list): r['p'][k]=x; r['s'][k]=plain(x)
        else: r['v'][k]=x
    if ro: r['ro']=True
    if o: r['o']=[dict(t=t,h=h) if h else dict(t=t) for t,h in o]
    if extra: r.update(extra)
    return r
def two(a,b): return [Pt.b(a),Pt.br(),Pt.mut(b)]
def ch(t,c): return [Pt.chip(t,c)]
def fn(t,f,u=False): return {'k':'act','t':t,'fn':f,'u':u}
def ic(html,name,title=None):
    """Ação secundária com ícone + rótulo + title (acessível)."""
    t=f' title="{esc(title)}"' if title else ''
    svg=icon(name,14)
    html=html.replace('display: inline-block;','display: inline-flex; align-items: center; gap: 6px;',1)
    if html.startswith('<a '): return html.replace('<a ',f'<a{t} ',1).replace('">',f'">{svg}',1)
    return html.replace('<button ',f'<button{t} ',1).replace('style="',f'style="display: inline-flex; align-items: center; gap: 6px; ',1).replace('">',f'">{svg}',1)
def nota(txt,state='gray'):
    cor={'gray':MUTED,'yellow':'#8A5A00','red':'#9E0A1F'}[state]
    return f'<div style="font-size: 13px; color: {cor}; line-height: 1.55; padding-top: 10px;">{txt}</div>'
def B(t): return f'<b style="color:{INK};">{t}</b>'
PRIM_A=f'text-decoration: none; display: inline-block; {BTN_ST(True)}'
def prim_dyn():
    """botão primário dinâmico: executa (prim_btn) ou navega (prim_lnk) conforme o estado."""
    return (f'<sc-if value="{H("prim_btn")}" hint-placeholder-val="{H("true")}"><button type="button" onClick="{H("prim_fn")}" style="{BTN_ST(True)}">{H("prim_t")}</button></sc-if>'
            f'<sc-if value="{H("prim_lnk")}" hint-placeholder-val="{H("false")}"><a href="{H("prim_h")}" style="{PRIM_A}">{H("prim_t")}</a></sc-if>')
JS_BASE='''
function GR(id){ return GRIDS.find(g=>g.id===id); }
function setRow(self,gid,rid,fn){ const sp=GR(gid); const rows=g2clone(g2rows(self,sp)); const r=g2find(rows,rid); if(r) fn(r); g2set(self,gid,{rows}); return r; }
function getRow(self,gid,rid){ return g2find(g2rows(self,GR(gid)),rid); }
function isNew(r){ return r && String(r.id).indexOf('n')===0 && !r.v.__ok; }
function CH(t,c){ return {k:'chip',t:t,c:c}; }
function MU(t){ return {k:'mut',t:t}; }
const BR={k:'br',t:''};
function PROP(r,keys){ const ch=[]; keys.forEach(k=>{ const o=r.v['o_'+k]; if(o===undefined) return; const n=r.v[k];
  if(String(o)!==String(n)){ r.p[k]=[{k:'txt',t:String(o)},BR,CH('proposto: '+(String(n)===''?'—':n),'yellow')]; r.s[k]=String(o); ch.push(k); }
  else { delete r.p[k]; r.s[k]=String(o); } }); return ch; }
function pl(n,s,p){ return n+' '+(n===1?s:p); }
'''

def build():
    # ================= CF-01 · Usuários e permissões =================
    fname='CF-01.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1400
    PAPEIS=['Gestora · agrônoma RT','PCP','Operador · pulverização','Operador · irrigação','Operador','Conferente (delegação de Ana)','Estoque']
    ESCOPOS=['Santa Rita + Boa Vista','Santa Rita','Santa Rita · T1+T2','Santa Rita · pivôs','Boa Vista']
    AUTH=['senha + 2º fator','PIN no dispositivo']
    def usr(rid,nome,email,papel,escopo,vig,auth,sess,sit,acao,ro=False):
        sitp=sit+[Pt.br()]+acao
        return R(rid,ro=ro,v=dict(nome=nome,email=email,o_papel=papel,o_escopo=escopo,o_vig=vig,o_auth=auth,sess=sess),extra=dict(sit0=sitp,acao0=acao),
                 ident=two(nome,email),papel=papel,escopo=escopo,vig=vig,auth=auth,sit=sitp)
    visao=lambda p: Pt.act('Simular visão',f'Visão de {p} aplicada em demonstração — não representa segurança real; o servidor continua a autoridade das permissões.')
    usrs=[
      usr('u_ana','Ana Souza','ana@fazsantarita.com.br','Gestora · agrônoma RT','Santa Rita + Boa Vista','sem prazo','senha + 2º fator','2 ativas',ch('Ativo','green'),[visao('Ana (gestora)')]),
      usr('u_caio','Caio Martins','caio@fazsantarita.com.br','PCP','Santa Rita','sem prazo','senha + 2º fator','1 ativa',ch('Ativo','green'),[visao('Caio (PCP)')]),
      usr('u_marcos','Marcos Lima','marcos@fazsantarita.com.br','Operador · pulverização','Santa Rita · T1+T2','até 30/06/2027','PIN no dispositivo','1 offline',ch('Offline · pacote válido','yellow'),[visao('Marcos (operador): só ordens liberadas do seu escopo')]),
      usr('u_joao','João Prado','joao@fazsantarita.com.br','Operador · irrigação','Santa Rita · pivôs','até 30/06/2027','PIN no dispositivo','1 ativa',ch('Ativo','green'),[visao('João (irrigação)')]),
      usr('u_paula','Paula Neri','paula@fazsantarita.com.br','Conferente (delegação de Ana)','Santa Rita','delegação até 30/09','senha + 2º fator','1 ativa',ch('Delegação vence em 5 dias','yellow'),[fn('Revogar delegação','revoga:u_paula',True)]),
      usr('u_beto','Beto Ramos','beto@fazsantarita.com.br','Operador','Santa Rita','—','PIN no dispositivo','—',ch('Convite pendente · aprovação','yellow'),[Pt.cta('Acompanhar aprovação','IN-02.dc.html')]),
      usr('u_davi','Davi Melo','davi@fazsantarita.com.br','Operador','Santa Rita','encerrada 15/09','—','0',ch('Revogado','gray'),[Pt.cta('Ver trilha','CF-04.dc.html')],ro=True),
    ]
    g_usr=grid([C('ident','Identidade',w=200),C('papel','Papel',w=170),C('escopo','Escopo',w=150),C('vig','Vigência',w=130),C('auth','Autenticação',w=130),
                C('sit','Situação · ação',w=240)],usrs,
       edit=dict(m='form',title='Usuário',newTitle='Convidar usuário',
         sub='Mudança de papel, escopo, vigência ou autenticação fica pendente: vale depois da aprovação do gestor e entra na trilha com o aprovador.',
         fields=[dict(k='nome',l='Nome',t='txt',req=True),dict(k='email',l='E-mail',t='email',req=True),
                 dict(k='papel',l='Papel',t='sel',req=True,opts=PAPEIS,**{'def':'Operador'}),
                 dict(k='escopo',l='Escopo',t='sel',req=True,opts=ESCOPOS,**{'def':'Santa Rita'}),
                 dict(k='vig',l='Vigência',t='txt',req=True,help='Ex.: até 30/06/2027 ou sem prazo',**{'def':'até 30/06/2027'}),
                 dict(k='auth',l='Autenticação',t='sel',req=True,opts=AUTH,**{'def':'PIN no dispositivo'})]),
       add='Convidar usuário',gid='g_usr',total=False)
    devs=[
      R('d_marcos',ro=True,v=dict(pac='Válido até 25/09'),disp=two('Celular · MB-03','Marcos Lima'),ult='hoje 06:10',
        pacote=[Pt.chip(f'Sincronizado · {APT["id"]} recibo {APT["recibo"]}','green'),Pt.br(),Pt.mut('pacote válido até 25/09 · agora offline')],
        acao=[fn('Encerrar sessão','encerra:d_marcos')]),
      R('d_paula',ro=True,disp=two('Tablet · conferência','Paula Neri'),ult='hoje 07:30',
        pacote=[Pt.chip('Sincronizado · 1 conflito em reconciliação','red')],acao=[Pt.cta('Ver conflito','CF-03det.dc.html',True)]),
      R('d_rui',ro=True,disp=two('Tablet · balança','Rui'),ult='hoje 07:05',pacote=ch('Sincronizado','green'),acao=[fn('Encerrar sessão','encerra:d_rui')]),
      R('d_ana',ro=True,disp=two('Notebook · escritório','Ana Souza'),ult='agora',pacote=ch('Sincronizado','green'),acao=[Pt.mut('sessão atual')]),
    ]
    g_dev=grid([C('disp','Dispositivo · usuário',w=200),C('ult','Último sincronismo'),C('pacote','Pacote offline',w=300),C('acao','Ação')],devs,
       edit=dict(m='ro',title='Dispositivo',fields=[dict(k='disp',l='Dispositivo · usuário',ro=True),dict(k='ult',l='Último sincronismo',ro=True),dict(k='pacote',l='Pacote offline',ro=True)]),
       search=False,gid='g_dev',total=False)
    EXTRAJS[0]=JS_BASE+'''
function EXTRAVALS(self,v){
  const U=g2rows(self,GR('g_usr'));
  const conv=U.filter(r=>String(r.s.sit||'').indexOf('Convite pendente')===0).length;
  const alt=U.filter(r=>String(r.s.sit||'').indexOf('Alteração pendente')===0).length;
  v.k_conv=String(conv); v.k_conv_u=alt?pl(alt,'alteração pendente','alterações pendentes'):'aguardando aprovação do gestor';
  v.st_t=pl(conv,'convite pendente','convites pendentes')+(alt?' · '+pl(alt,'alteração','alterações'):'');
  v.revoga=(rid)=>{ const r0=getRow(self,'g_usr',rid); if(!r0||String(r0.s.sit).indexOf('revogada')>=0) return;
    setRow(self,'g_usr',rid,r=>{ r.acao0=[{k:'cta',t:'Ver trilha',h:'CF-04.dc.html'}]; r.p.sit=[CH('Delegação revogada','gray'),BR].concat(r.acao0); r.s.sit='Delegação revogada'; r.sit0=r.p.sit; r.ro=true; });
    self.setState({g2toast:'Delegação de Ana para Paula revogada no servidor · sessões com a delegação encerradas · conferências já feitas são preservadas.'}); };
  v.encerra=(rid)=>{ setRow(self,'g_dev',rid,r=>{ r.p.pacote=[CH('Sessão encerrada','gray'),BR,MU('novo login exige credencial e 2º fator')]; r.s.pacote='Sessão encerrada'; r.p.acao=[MU('encerrada agora')]; });
    self.setState({g2toast:'Sessão encerrada no servidor · dispositivo offline é suspenso ao expirar o pacote — fatos capturados são preservados.'}); };
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_usr'||!r) return;
    r.p.ident=[{k:'b',t:r.v.nome},BR,MU(r.v.email)]; r.s.ident=r.v.nome+' '+r.v.email;
    if(isNew(r)){ r.v.__ok=1; ['papel','escopo','vig','auth'].forEach(k=>{ r.v['o_'+k]=r.v[k]; }); r.v.sess='—';
      r.acao0=[{k:'cta',t:'Acompanhar aprovação',h:'IN-02.dc.html'}]; r.p.sit=[CH('Convite pendente · aprovação','yellow'),BR].concat(r.acao0); r.s.sit='Convite pendente · aprovação'; r.sit0=r.p.sit;
      self.setState({g2toast:'Convite enviado a '+r.v.email+' · acesso pendente de aprovação do gestor (aparece em Aprovações).'}); return; }
    const chg=PROP(r,['papel','escopo','vig','auth']);
    if(chg.length){ r.p.sit=[CH('Alteração pendente · aprovação do gestor','yellow'),BR].concat(r.acao0||[]); r.s.sit='Alteração pendente · aprovação do gestor';
      self.setState({g2toast:'Alteração proposta para '+r.v.nome+' · vale depois da aprovação do gestor · aprovador registrado na trilha.'}); }
    else { r.p.sit=r.sit0; r.s.sit=(r.sit0&&r.sit0[0])?r.sit0[0].t:''; self.setState({g2toast:'Nada mudou no acesso de '+r.v.nome+'.'}); } };
}'''
    corpo=(
      kpis([('USUÁRIOS ATIVOS','18','em 2 fazendas'),('CONVITES PENDENTES',H('k_conv'),H('k_conv_u')),
            ('SESSÕES E DISPOSITIVOS','23','1 offline com pacote válido'),('DELEGAÇÕES VIGENTES','2','com prazo e escopo')])
      + section('Usuários','Convide pessoas e ajuste papel, escopo e vigência; clique na linha para editar.','',g_usr)
      + section('Sessões e dispositivos','Encerre sessões no servidor e confira pacotes offline e conflitos de sincronização.',
        [ic(msgbtn('Revisar acessos','Campanha de revisão aberta · 12 acessos para reconfirmar até 30/09 · donos notificados (simulado · nenhuma mensagem real enviada) — não reconfirmado é suspenso, não apagado.'),'users','Abrir campanha de revisão de acessos')],
        g_dev))
    shell37('CF-01','Usuários e permissões',corpo,fname=fname,
      subtitle='Usuários, papéis, escopos, credenciais e sessões — visão de demonstração por persona não representa segurança real.',
      status=(H('st_t'),'yellow'),
      footer='Servidor é autoridade das permissões; alteração de perfil registra aprovador (FO-39) e entra na trilha CF-04.')

    # ================= CF-02 · Alçadas e regras (fecha A-01) =================
    fname='CF-02.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1240
    DONOS=['Liberador do domínio · Caio (PCP)','Responsável do domínio · Ana (Gestora)','Gerencial · Ana + validação agronômica do RT',
           'Conferente ou PCP com permissão específica · Paula/Caio','Supervisor de expedição · Rui','Aprovador competente por objeto · Ana (agrônoma RT)','Direção']
    def alc(rid,cmd,idl,nv,dono,lim,nota_,fonte,vig,acao):
        return R(rid,v=dict(idl=idl,fonte=fonte,o_dono=dono,o_lim=lim,o_vig=vig,classe='Obrigatória',motivo='',rv=REV_OK),extra=dict(nv=nv,cmd0=cmd),
                 cmd=[Pt.b(cmd),Pt.br(),Pt.mut(f'{idl} · {fonte}')],dono=dono,lim=lim,classe=[Pt.tag('Obrigatória'),Pt.br(),Pt.mut(nota_)],vig=vig,acao=acao)
    alcs=[
      alc('al01','Liberar ordem','AL-01 v4','v5','Liberador do domínio · Caio (PCP)','até R$ 80 mil por ordem; acima, Direção','exige versão aprovada vigente e evento de liberação','cap. 8.2 · 41.3','até 31/07/2027',[]),
      alc('al04','Cancelar sem execução','AL-04 v2','v3','Responsável do domínio · Ana (Gestora)','qualquer valor · conclusão só com custódia zero','materiais pendentes não são apagados','cap. 8.2.1','até 31/07/2027',[]),
      alc('al05','Dispensar saldo','AL-05 v2','v3','Gerencial · Ana + validação agronômica do RT','saldo até 20% da área da ordem; acima, Direção','decisão técnica aplicável','cap. 8.2.1 · 42.3','até 31/07/2027',[Pt.cta('Ver alçada','CF-02det.dc.html')]),
      alc('al06','Reabrir saldo','AL-06 v1','v2','Conferente ou PCP com permissão específica · Paula/Caio','só ordens Em conferência · histórico preservado','não reabre período contábil','cap. 8.2.1','até 31/07/2027',[]),
      alc('al08','Reordenar fila logística','AL-08 v1','v2','Supervisor de expedição · Rui','caminhão presente e apto + motivo registrado','promessa original preservada','cap. 50','até 31/07/2027',[Pt.cta('Ver fila','LO-02.dc.html')]),
      alc('al02','Decidir revisão','AL-02 v3','v4','Aprovador competente por objeto · Ana (agrônoma RT)','sem teto financeiro · competência por domínio','rejeitar não cancela a ordem','cap. 8.2.1 · 41','até 31/07/2027',[Pt.cta('Ver caixa','IN-02.dc.html')]),
    ]
    # AL-05 já tem v3 em revisão: abre em consulta (a decisão fica no detalhe)
    alcs[2]['ro']=True; alcs[2]['v']['rv']='v3 já em revisão · decida no detalhe da alçada'; alcs[2]['p']['cmd']+= [Pt.br(),Pt.chip('v3 em revisão','yellow')]; alcs[2]['s']['cmd']+=' v3 em revisão'
    PROP_FIELDS=lambda lim_l: [dict(k='rv',l='Revisão',t='txt',ro=True),dict(k='dono',l='Dono (quem decide)',t='sel',req=True,opts=DONOS),dict(k='lim',l=lim_l,t='area',req=True),
                               dict(k='classe',l='Classe de bloqueio',t='txt',ro=True,help='Classe obrigatória não pode virar exceção livre.'),
                               dict(k='vig',l='Vigência',t='txt',req=True,help='Ex.: até 31/07/2027'),
                               dict(k='motivo',l='Motivo da revisão',t='area',req=True,cond=dict(k='rv',eq=REV_OK))]
    g_alc=grid([C('cmd','Comando · alçada · fonte',w=200),C('dono','Dono (quem decide)',w=200),C('lim','Valor / limite',w=210),C('classe','Classe de bloqueio',w=210),
                C('vig','Vigência',w=110),C('acao','Abrir')],alcs,
       edit=dict(m='form',title='Propor revisão',sub='Salvar cria uma nova versão em revisão: a versão vigente continua valendo até a aprovação registrada do aprovador competente.',
                 fields=PROP_FIELDS('Valor / limite')),
       gid='g_alc',total=False)
    def pol(rid,idl,nome,nv,escopo,lim,aprov,dono,vig,sit,acao,ro=False,rv=None):
        return R(rid,ro=ro,v=dict(idl=idl,o_lim=lim,o_aprov=aprov,o_vig=vig,motivo='',rv=(rv or REV_OK)),extra=dict(nv=nv,sit0=sit,acao0=acao),
                 regra=two(idl,f'{nome} · dono: {dono}'),escopo=escopo,lim=lim,aprov=aprov,vig=vig,sit=sit+([Pt.br()]+acao if acao else []))
    PA=D.POLITICA_AGUA; lam=str(PA['lamina_max']).replace('.',',')
    pols=[
      # política de água: identificador, versão, dono e validade de dados.POLITICA_AGUA (a mesma da ficha do pivô e do app; revisão de 10/10, A3)
      pol('pa07',f'{PA["id"]} {PA["versao"]}','limites de irrigação (só água)','v'+str(int(PA['versao'].lstrip('v'))+1),f'{D.PIVO["id"]} + pivô 1 + gotejo T7',f'lâmina ≤ {lam} mm por passada · intervalo ≥ {PA["intervalo_min"]}','Gestor · sem aprovação por evento',PA['autor'],f'até {PA["validade"]}',ch('Vigente','green'),[]),
      pol('pe04','PE-04','estoque Diesel S10','v1','tanque Sede','mínimo do tanque 40%','Gestor','Rui','—',ch('Aguardando aprovação','yellow'),
          [Pt.act('Publicar','Publicação bloqueada · PE-04 é classe Obrigatória e ainda não tem aprovação do gestor nem teste de exemplo. Como resolver: simule os casos e aprove em Aprovações; depois publique.')],ro=True,rv='Aguardando aprovação do gestor'),
      pol('al05p','AL-05 v2','dispensar saldo','v3','ordens agrícolas','saldo até 20% da área','Gerencial + agronômica','Ana','até 31/07/2027',ch('Vigente · v3 proposta','yellow'),[Pt.cta('Ver alçada','CF-02det.dc.html')],ro=True,rv='v3 já em revisão · decida no detalhe da alçada'),
      pol('tl01','TL-01','tolerância de compras','v1','contratos de insumos','por contrato/item · ±10% é só HIPÓTESE, sem padrão','Compras + contraparte','—','—',ch('Sem padrão autorizado','gray'),[]),
    ]
    g_pol=grid([C('regra','Regra/ID · proprietário',w=220),C('escopo','Escopo',w=150),C('lim','Limites',w=210),C('aprov','Aprovadores',w=150),C('vig','Vigência',w=100),C('sit','Situação · ação',w=220)],pols,
       edit=dict(m='form',title='Propor revisão',sub='Salvar cria uma nova versão em revisão; publicar exige aprovação registrada e ao menos um teste de exemplo.',
                 fields=[dict(k='rv',l='Revisão',t='txt',ro=True),dict(k='lim',l='Limites',t='area',req=True),dict(k='aprov',l='Aprovadores',t='sel',req=True,opts=['Agrônomo RT','Gestor','Gerencial + agronômica','Compras + contraparte','Direção']),
                         dict(k='vig',l='Vigência',t='txt',req=True,help='Ex.: até 30/11'),dict(k='motivo',l='Motivo da revisão',t='area',req=True,cond=dict(k='rv',eq=REV_OK))]),
       gid='g_pol',total=False)
    EXTRAJS[0]=JS_BASE+'''
function EXTRAVALS(self,v){
  const A=g2rows(self,GR('g_alc')), P=g2rows(self,GR('g_pol'));
  const rev=1+A.filter(r=>r.v.__rev).length+P.filter(r=>r.v.__rev).length;
  v.k_rev=String(rev); v.st_t=pl(rev,'em revisão','em revisão');
  v.k_rev_u=(A.concat(P).filter(r=>r.v.__rev).map(r=>String(r.v.idl).split(' ')[0]+' '+r.nv).concat(['AL-05 v3'])).join(' · ');
  self.g2after=(gid,rows,r)=>{ if(!r||(gid!=='g_alc'&&gid!=='g_pol')) return;
    const chg=PROP(r,gid==='g_alc'?['dono','lim','vig']:['lim','aprov','vig']);
    const nome=r.v.idl;
    if(!chg.length){ self.setState({g2toast:'Nada mudou em '+nome+' · nenhuma revisão criada.'}); return; }
    r.v.__rev=1;
    if(gid==='g_alc'){ r.p.cmd=[{k:'b',t:r.cmd0},BR,MU(r.v.idl+' · '+r.v.fonte),BR,CH(r.nv+' em revisão','yellow')]; r.s.cmd=r.cmd0+' '+r.v.idl+' '+r.nv+' em revisão'; }
    else { r.p.sit=[CH(r.nv+' em revisão · Aprovações','yellow'),BR,MU('vigente continua valendo')].concat(r.acao0&&r.acao0.length?[BR].concat(r.acao0):[]); r.s.sit=r.nv+' em revisão'; }
    self.setState({g2toast:'Revisão '+nome.split(' ')[0]+' '+r.nv+' criada em revisão · aguardando aprovação em Aprovações — a versão vigente continua valendo.'}); };
}
function plain2(ps){ return (ps||[]).filter(p=>p.k!=='br').map(p=>p.t).join(' '); }'''
    corpo=(
      kpis([('POLÍTICAS VIGENTES','14','com dono e vigência'),('EM REVISÃO',H('k_rev'),H('k_rev_u')),
            ('VENCEM EM 60 DIAS','0','nenhuma no período'),('BLOQUEIOS OBRIGATÓRIOS','6','não viram exceção livre')])
      + section('Alçadas dos comandos da ordem','Confira quem decide cada comando e até que limite; clique na linha para propor revisão.',
        [ic(btn('Ver objetos afetados',small=True,href='OS.dc.html'),'lista','Abrir as ordens de serviço que dependem destas alçadas')],g_alc)
      + section('Registro central de políticas','Revise versão, limites e vigência de cada política; clique na linha para propor revisão.',
        [ic(msgbtn('Simular casos','Simulados 6 casos de exemplo · 5 conforme · 1 bloqueado: dispensa de 30% do saldo excede o limite de 20% e exigiria Direção — resultado por caso.'),'calc','Rodar os testes de exemplo das políticas'),
         ic(btn('Aprovar pendentes',small=True,href='IN-02.dc.html'),'check','Abrir a caixa de Aprovações')],
        g_pol + nota(f'Publique só política com dono, aprovador, fonte e teste de exemplo: restrição {B("Obrigatória")} não vira exceção livre. '
                     f'PE-04 está bloqueada para publicação até a aprovação do gestor.','yellow'),state='yellow'))
    shell37('CF-02','Alçadas e regras',corpo,fname=fname,
      subtitle='Registro central de políticas com testes de exemplo, versão, proprietário e vigência — é a fonte que os comandos citam ao bloquear ou exigir alçada.',
      status=(H('st_t'),'yellow'),
      footer='Liberar (CMD-06), cancelar (CMD-46), dispensar saldo (CMD-47), reabrir (CMD-48) e reordenar fila (CMD-37) só executam dentro da alçada vigente registrada aqui.')

    # ---- CF-02det · detalhe da alçada AL-05 (dispensar saldo) ----
    fname='CF-02det.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1180; PARENT37[fname]='CF-02.dc.html'
    g_def=grid([C('campo','Campo',w=170),C('vig','Valor vigente (v2)',w=330),C('prop','Proposta (v3 · em revisão)',w=300)],[
        R('f1',campo='Dono da decisão',vig='Gerencial · Ana (Gestora)',prop='sem mudança'),
        R('f2',campo='Validação técnica',vig='Agronômica · agrônomo RT, registrada à parte (obrigatória em atividade agrícola)',prop='sem mudança'),
        R('f3',campo='Valor / limite',vig=[Pt.txt('saldo até '),Pt.b('20%'),Pt.txt(' da área da ordem; acima, Direção')],prop=[Pt.txt('saldo até '),Pt.b('25%'),Pt.txt(' da área da ordem')]),
        R('f4',campo='Classe de bloqueio',vig=[Pt.tag('Obrigatória')],prop=[Pt.tag('Obrigatória')]),
        R('f5',campo='Fonte',vig='cap. 8.2.1 · 42.3',prop='idem + motivo de revisão'),
        R('f6',campo='Vigência',vig='até 31/07/2027',prop='a partir de 01/11/2026, se aprovada')],
       edit=dict(m='none'),search=False,gid='g_def',total=False)
    pct1=round(100*OS1['saldo']/OS1['area'])
    g_tst=grid([C('caso','Caso',w=180),C('ent','Entrada',w=280),C('esp','Resultado esperado',w=280),C('sit','Situação')],[
        R('t1',caso='Dispensa pequena',ent=[Pt.link(OS0['id'],'OS.dc.html'),Pt.txt(f' · dispensar 10 ha de {OS0["area"]} ha (3%)')],esp='permitida na alçada gerencial + validação técnica',sit=ch('Conforme','green'),
          o=[(f'10 ÷ {OS0["area"]} ha = 3% ≤ 20% → alçada gerencial',None),(f'{OS0["id"]} · {OS0["realizado"]} ha realizados preservados','OS.dc.html')]),
        R('t2',caso='Dispensa acima do limite',ent=[Pt.link(OS1['id'],'OS.dc.html'),Pt.txt(f' · dispensar {OS1["saldo"]} ha de {OS1["area"]} ha ({pct1}%)')],esp='bloqueada · excede 20% — exige Direção',sit=ch('Bloqueio correto','green'),
          o=[(f'{OS1["saldo"]} ÷ {OS1["area"]} ha = {pct1}% > 20% → Direção',None),(f'{OS1["id"]} · {OS1["realizado"]} ha realizados preservados','OS.dc.html')]),
        R('t3',caso='Sem trabalho iniciado',ent='ordem sem nenhum apontamento',esp='recusada · usar Cancelar sem execução',sit=ch('Bloqueio correto','green'),o=[('Nenhum apontamento → CMD-46, não CMD-47',None)]),
        R('t4',caso='Sem validação técnica',ent='dispensa agrícola sem decisão agronômica',esp='recusada · decisão técnica aplicável ausente',sit=ch('Bloqueio correto','green'),o=[('Atividade agrícola exige validação do agrônomo RT',None)])],
       edit=dict(m='origin',title='Teste',fields=[dict(k='caso',l='Caso',ro=True),dict(k='esp',l='Resultado esperado',ro=True)]),search=False,gid='g_tst',total=False)
    g_obj=grid([C('obj','Objeto',w=300),C('cond','Condição',w=420),C('abrir','Abrir')],[
        R('o1',obj=[Pt.b(OS1['id']),Pt.txt(' · plantio · selo Impedida ('+D.OM['id']+')')],cond=f'eventual dispensa do saldo de {OS1["saldo"]} ha passaria por AL-05 · {OS1["realizado"]} ha realizados preservados',abrir=[Pt.cta('Abrir ordem','OS.dc.html')]),
        R('o2',obj=[Pt.b('Reprogramações')],cond='dispensa registrada aparece com realizado, dispensado e motivo',abrir=[Pt.cta('Abrir painel','PL-05.dc.html')])],
       edit=dict(m='ro',title='Objeto afetado',fields=[dict(k='obj',l='Objeto',ro=True),dict(k='cond',l='Condição',ro=True)]),search=False,gid='g_obj',total=False)
    g_v3=grid([C('ver','Versão'),C('mud','Mudança proposta',w=300),C('por','Proposta por'),C('sit','Situação',w=240)],[
        R('v3',v=dict(dec='Aprovar e publicar (vigência 01/11/2026)',motivo='',ori=''),ver=[Pt.b('AL-05 v3')],mud='limite gerencial de 20% para 25% do saldo · replantios frequentes',por='Ana · 18/09',
          sit=ch('Em revisão · aguardando decisão','yellow'))],
       edit=dict(m='form',title='Decidir',sub='Aprovar aqui tem o mesmo efeito e recibo de aprovar em Aprovações. Relógio e caminho não mudam a regra: a v2 vale até a vigência da v3.',
         fields=[dict(k='dec',l='Decisão',t='sel',req=True,opts=['Aprovar e publicar (vigência 01/11/2026)','Devolver para ajuste']),
                 dict(k='motivo',l='Motivo da devolução',t='area',req=True,cond=dict(k='dec',eq='Devolver para ajuste')),
                 dict(k='ori',l='Orientação ao proprietário',t='area',cond=dict(k='dec',eq='Devolver para ajuste'),help='Ex.: manter 20% e tratar replantio caso a caso pela Direção')]),
       search=False,gid='g_v3',total=False)
    EXTRAJS[0]=JS_BASE+'''
function EXTRAVALS(self,v){
  const r3=getRow(self,'g_v3','v3'); const d=r3&&r3.v.__ok?r3.v.__ok:0;
  v.st_t=d===1?'v3 aprovada · vigência 01/11':(d===2?'v3 devolvida · v2 vigente':'v3 em revisão');
  v.c_aqui=d===1?'AL-05 v2 vigente · v3 aprovada':(d===2?'AL-05 v2 vigente · v3 devolvida':'AL-05 v2 · vigente');
  v.c_falta=d===1?'nada · v2 vale até 31/10':(d===2?'ajuste da proposta pelo proprietário':'decisão sobre a revisão v3 proposta');
  v.c_prox=d?'Voltar ao registro de políticas':'Aprovar ou devolver a v3';
  v.prim_t=d?'Voltar ao registro de políticas':'Decidir a v3'; v.prim_btn=!d; v.prim_lnk=!!d; v.prim_h='CF-02.dc.html';
  v.prim_fn=()=>g2open(self,GR('g_v3'),'v3',null);
  self.g2after=(gid,rows,r)=>{ if(gid!=='g_v3'||!r) return; r.ro=true;
    if(String(r.v.dec).indexOf('Aprovar')===0){ r.v.__ok=1; r.p.sit=[CH('Aprovada · vigente a partir de 01/11/2026','green'),BR,MU('aprovador registrado na trilha')]; r.s.sit='Aprovada';
      self.setState({g2toast:'AL-05 v3 aprovada e publicada · vigência 01/11/2026 · aprovador registrado na trilha — v2 segue valendo até lá.'}); }
    else { r.v.__ok=2; r.p.sit=[CH('Devolvida ao proprietário','gray'),BR,MU(r.v.motivo)]; r.s.sit='Devolvida';
      self.setState({g2toast:'Proposta v3 devolvida ao proprietário da política · v2 permanece vigente.'}); } };
}'''
    corpo=(
      continuity('Alçadas e regras · registro de políticas',H('c_aqui'),H('c_falta'),H('c_prox'))
      + section('Definição da alçada','Compare a versão vigente com a proposta antes de decidir.','',g_def)
      + section('Testes de exemplo','Confira os casos que a publicação exige; clique no caso para ver o cálculo.','',g_tst)
      + section('Objetos afetados hoje','Abra as ordens em que esta alçada é condição de comando.','',g_obj)
      + section('Decisão sobre a v3','Aprove ou devolva a proposta; clique na linha para decidir.','',g_v3,state='yellow'))
    shell37('CF-02','Alçada AL-05 · Dispensar saldo',corpo,fname=fname,crumbs_extra=['AL-05'],
      subtitle='Detalhe da alçada com testes de exemplo, objetos afetados e revisão versionada.',
      status=(H('st_t'),'yellow'),primary_html=prim_dyn(),
      footer='Dispensar saldo (CMD-47) preserva realizado e histórico; se nenhum trabalho iniciou, o caminho é CMD-46 — a alçada não converte um comando no outro.')

    # ================= CF-03 · Integrações e sincronização =================
    fname='CF-03.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1240
    RESPS=['TI · Décio','Agronomia · Ana','Estoque · Rui','Gestor · Ana']
    g_con=grid([C('con','Conector / escopo',w=180),C('fonte','Fonte oficial (escritor)',w=280),C('est','Estado · erros',w=200),C('ult','Atualização · evento',w=140),
                C('resp','Responsável',w=130),C('acao','Ação')],[
        R('c_sk',v=dict(),con=two('Sankhya','financeiro + estoque'),fonte='ERP escreve títulos e posição fiscal; plataforma escreve ordens e fatos de campo',
          est=[Pt.chip('Simulado · demonstração','yellow'),Pt.br(),Pt.mut('2 erros na fila')],ult=[Pt.txt('23/09 06:40'),Pt.br(),Pt.mut('EVT-99182')],resp='TI · Décio',acao=[Pt.cta('Conciliar','CF-03det.dc.html',True)]),
        R('c_tt',con=two('TOTVS Protheus','fiscal'),fonte='ERP/base fiscal é autoridade; agrícola recebe estados oficiais',est=[Pt.chip('Homologação pendente','gray'),Pt.br(),Pt.mut('sem escrita até homologar')],ult='—',resp='TI · Décio',
          acao=[Pt.act('Ver escritores','Escritor oficial: ERP grava fiscal e títulos; plataforma grava ordens e fatos de campo — conector em homologação não recebe escrita até ser homologado.')]),
        R('c_em',con=two('Estação meteorológica','clima'),fonte='estação é fonte; plataforma só lê',est=[Pt.chip('Simulado · demonstração','yellow'),Pt.br(),Pt.mut('0 erros')],ult=[Pt.txt('23/09 06:00'),Pt.br(),Pt.mut('EVT-99170')],resp='Agronomia · Ana',
          acao=[Pt.cta('Ver leituras','IR-04.dc.html')])],
       edit=dict(m='form',title='Conector',sub='Troque o responsável pelos erros deste conector. Credenciais e destinos só mudam no ambiente autorizado e nunca aparecem aqui.',
         fields=[dict(k='resp',l='Responsável',t='sel',req=True,opts=RESPS),dict(k='fonte',l='Fonte oficial (escritor)',t='area',ro=True),dict(k='est',l='Estado',ro=True)]),
       search=False,gid='g_con',total=False)
    g_err=grid([C('item','Item · direção',w=220),C('erro','Erro / estado',w=250),C('ct','Correlação · tentativas',w=180),C('resp','Responsável',w=130),C('acao','Ação')],[
        R('e_nf',v=dict(tipo=T_UN,unid_pl='sc 50 kg',unid_erp='',motivo='De-para ausente na carga inicial'),item=two('Título NF 4412','R$ 18.400 · linha 1 · plataforma → ERP'),erro=ch('Rejeitado · unidade não mapeada','red'),corr='EVT-99182',
          ct=[Pt.txt('EVT-99182'),Pt.br(),Pt.mut('3 tentativas · espera progressiva')],resp='TI · Décio',acao=[Pt.mut('clique para corrigir')]),
        R('e_dev',ro=True,v=dict(tipo='Aguardando aceite · consulte por chave'),item=two(f'Devolução {REQ["id"]}',f'{REQ["dev_recebida"]} sc · {REQ["item"]} · plataforma → ERP'),erro=ch('Enviado · aguardando aceite','yellow'),corr='EVT-99188',ct=[Pt.txt('EVT-99188'),Pt.br(),Pt.mut('1 tentativa')],resp='Estoque · Rui',
          acao=[fn('Consultar por chave','consulta:e_dev')]),
        R('e_map',ro=True,v=dict(tipo='Divergência de saldo · decida na contagem'),item=two(f'Saldo {INV["item"]}',f'{INV["local"]} · {INV["id"]} · reconciliação'),erro=ch(f'Divergência · {INV_DIF_SC} sc ({n0(INV_DIF_KG)} kg)','red'),corr='REC-0142',ct=[Pt.txt('REC-0142')],resp='Gestor · Ana',
          acao=[Pt.cta('Abrir contagem','EST.dc.html')])],
       edit=dict(m='form',title='Item',sub='Corrija a unidade e salve para reprocessar: a mesma correlação é reutilizada — nada duplica.',
         fields=[dict(k='tipo',l='Pendência',t='txt',ro=True),dict(k='corr',l='Correlação',t='txt',ro=True),
                 dict(k='unid_pl',l='Unidade na plataforma',t='txt',ro=True,cond=dict(k='tipo',eq=T_UN)),dict(k='unid_erp',l='Unidade no ERP',t='sel',req=True,opts=['SC50','SC','KG'],help='De-para ausente na carga inicial.',cond=dict(k='tipo',eq=T_UN)),
                 dict(k='motivo',l='Motivo',t='txt',req=True,cond=dict(k='tipo',eq=T_UN))]),
       gid='g_err',total=False)
    g_off=grid([C('disp','Dispositivo',w=170),C('pend','Registro',w=210),C('idr','Identidade · recibo',w=150),C('comp','Comportamento verificado',w=270),C('sit','Situação · ação',w=210)],[
        R('o_m',ro=True,disp=two('Celular de Marcos','MB-03'),pend=[Pt.b(APT['id']),Pt.txt(f' · {APT["os"]} dia {APT["dia"]} · {APT["ha"]} ha')],idr=[Pt.txt(APT['uuid']),Pt.br(),Pt.mut(APT['recibo'])],
          comp=f'reenvio duplo devolveu o MESMO recibo {APT["recibo"]} · efeito único',sit=ch('Deduplicado','green')),
        R('o_p',ro=True,disp=two('Tablet de Paula','conferência'),pend=[Pt.txt(f'fato sobreposto · mesmos {APT["ha"]} ha de {APT["os"]}')],idr=[Pt.txt(APT_B['uuid']),Pt.br(),Pt.mut('sem recibo · retido')],
          comp=f'ambos os relatos preservados · nada somado como 2 execuções',sit=[Pt.chip('Reconciliação pendente','red'),Pt.br(),Pt.cta('Ver conflito','CF-03det.dc.html',True)])],
       edit=dict(m='ro',title='Registro offline',fields=[dict(k='disp',l='Dispositivo',ro=True),dict(k='pend',l='Registro',ro=True),dict(k='idr',l='Identidade · recibo',ro=True),dict(k='comp',l='Comportamento',ro=True)]),
       search=False,gid='g_off',total=False)
    EXTRAJS[0]=JS_BASE+'''
function EXTRAVALS(self,v){
  const E=g2rows(self,GR('g_err')); const nerr=E.filter(r=>(r.p.erro||[]).some(p=>p.c==='red')).length;
  v.k_err=String(nerr); v.st_t=pl(nerr,'erro','erros')+' · 1 conflito';
  v.consulta=(rid)=>{ const r0=getRow(self,'g_err',rid); if(r0&&r0.v.__ok){ self.setState({g2toast:'Já consultado · ERP registrou o movimento; nada reenviado.'}); return; }
    setRow(self,'g_err',rid,r=>{ r.v.__ok=1; r.p.erro=[CH('Aceito pelo ERP','green'),BR,MU('confirmado por consulta de chave')]; r.s.erro='Aceito pelo ERP'; r.p.acao=[MU('sem reenvio')]; r.s.acao='sem reenvio'; });
    self.setState({g2toast:'Consulta por chave: o ERP registrou o movimento · estado Aceito — sem reenvio (timeout não presume falha).'}); };
  self.g2after=(gid,rows,r)=>{ if(!r) return;
    if(gid==='g_con'){ self.setState({g2toast:'Responsável do conector atualizado · mudança registrada na trilha.'}); return; }
    if(gid!=='g_err') return;
    if(r.v.unid_erp==='SC50'){ r.v.__ok=1; r.ro=true; r.p.erro=[CH('Aceito · reprocessado','green'),BR,MU('de-para sc 50 kg → SC50')]; r.s.erro='Aceito · reprocessado'; r.p.ct=[{k:'txt',t:'EVT-99182'},BR,MU('4 tentativas · mesma correlação')]; r.p.acao=[MU('efeito único')]; r.s.acao='efeito único';
      self.setState({g2toast:'Item reprocessado · aceito pelo ERP · recibo EVT-99182 reutilizado — efeito único, sem duplicar título.'}); }
    else { r.p.erro=[CH('Rejeitado · '+r.v.unid_erp+' não é sc 50 kg no ERP','red')]; r.s.erro='Rejeitado'; r.p.ct=[{k:'txt',t:'EVT-99182'},BR,MU('4 tentativas · espera progressiva')];
      self.setState({g2toast:'ERP rejeitou de novo: '+r.v.unid_erp+' não corresponde a sc 50 kg · nada duplicado — use SC50.'}); } };
}'''
    corpo=(
      kpis([('CONECTORES','3','1 em homologação'),('FILA DE SAÍDA','12','eventos · 0 perdidos'),
            ('ERROS A TRATAR',H('k_err'),'com dono'),('DISPOSITIVOS OFFLINE','1',f'{APT["id"]} com recibo')])
      + section('Conectores','Confira quem escreve cada objeto e o estado de cada conector; clique na linha para trocar o responsável.',
        [ic(msgbtn('Configurar em ambiente autorizado','Configuração aberta somente no ambiente de homologação autorizado · credenciais de menor privilégio ficam no cofre e nunca aparecem em registros.'),'wrench','Abrir a configuração no ambiente autorizado'),
         ic(msgbtn('Testar conexão','Teste executado no simulador · resposta em 340 ms · selo Simulado mantido — teste não homologa integração.'),'check','Testar a conexão no simulador')],g_con)
      + section('Fila de erros e reconciliação','Corrija e reprocesse os itens rejeitados; reprocessar não duplica efeito.',
        [ic(msgbtn('Exportar diagnóstico sem segredo','Diagnóstico exportado · 128 eventos · credenciais, tokens e endereços internos omitidos — a exportação entrou na trilha de auditoria.'),'doc','Exportar diagnóstico sem credenciais')],g_err,state='red')
      + section('Dispositivos offline','Confira reenvios e fatos sobrepostos; o mesmo fato aplica uma vez.','',g_off,state='red'))
    shell37('CF-03','Integrações e sincronização',corpo,fname=fname,
      subtitle='Conectores, fonte oficial por objeto, filas, falhas e reconciliação — resposta de transporte não comprova efetivação do documento.',
      status=(H('st_t'),'red'),
      primary='Conciliar pendências',primary_href='CF-03det.dc.html',
      footer='Conector conectado não é sinônimo de entidades sincronizadas (ERP-01); DEV/HML/PROD têm destinos e chaves isolados (cap. 66).')

    # ---- CF-03det · reconciliação do ERP (simulado) + conflito de sincronização offline ----
    fname='CF-03det.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1040; PARENT37[fname]='CF-03.dc.html'
    g_rec=grid([C('doc','Documento / linha',w=200),C('corr','Correlação'),C('plat','Plataforma',w=180),C('erp','ERP (Sankhya)',w=160),C('dif','Diferença',w=180),C('est','Estado',w=220)],[
        R('nf',v=dict(tipo=T_UN,unid_pl='sc 50 kg',unid_erp='',motivo='De-para ausente na carga inicial'),doc=two('Título NF 4412','linha 1'),corr='EVT-99182',plat='R$ 18.400 · sc 50 kg',erp='—',dif=ch('Unidade não mapeada','red'),
          est=[Pt.chip('Rejeitado','red'),Pt.br(),Pt.mut('clique para corrigir e reprocessar')]),
        R('dev',ro=True,v=dict(tipo='Aguardando aceite · consulte por chave'),doc=two(f'Devolução {REQ["id"]}',REQ['item']),corr='EVT-99188',plat=f'{REQ["dev_recebida"]} sc recebidas',erp='sem confirmação',dif=ch('A confirmar','yellow'),
          est=[Pt.chip('Enviado · aguardando aceite','yellow'),Pt.br(),fn('Consultar por chave','consulta:dev')])],
       edit=dict(m='form',title='Item',sub='Corrija a unidade e salve para reprocessar: a correlação EVT-99182 é reutilizada — nada duplica.',
         fields=[dict(k='tipo',l='Pendência',t='txt',ro=True),dict(k='corr',l='Correlação',t='txt',ro=True),
                 dict(k='unid_pl',l='Unidade na plataforma',t='txt',ro=True,cond=dict(k='tipo',eq=T_UN)),dict(k='unid_erp',l='Unidade no ERP',t='sel',req=True,opts=['SC50','SC','KG'],cond=dict(k='tipo',eq=T_UN)),
                 dict(k='motivo',l='Motivo',t='txt',req=True,cond=dict(k='tipo',eq=T_UN))]),
       search=False,gid='g_rec',total=False)
    g_syn=grid([C('rel','Relato · dispositivo',w=200),C('idl','Identidade local',w=120),C('rec','Recibo',w=160),C('area','Área',t='num',a='r',u='ha'),C('srv','Servidor',w=220),C('est','Estado',w=220)],[
        R('a',ro=True,v=dict(tipo='Aceito com recibo · efeito único'),rel=two(f'Relato A · {APT["id"]}','Celular de Marcos · MB-03'),idl=APT['uuid'],rec=[Pt.b(APT['recibo']),Pt.br(),Pt.mut('2 reenvios · mesmo recibo')],area=APT['ha'],
          srv=f'aceito uma vez · conta {APT["ha"]} ha no dia {APT["dia"]}',est=ch('Confirmado','green')),
        R('b',v=dict(tipo=T_SB,dec='Duplicidade de captura · contar uma vez',motivo=''),rel=two('Relato B · captura do tablet','Tablet de Paula · conferência'),idl=APT_B['uuid'],rec=[Pt.mut('sem recibo · retido')],area=APT['ha'],
          srv=f'sobrepõe os {APT["ha"]} ha já aceitos · não somar',est=[Pt.chip('Em reconciliação','red'),Pt.br(),Pt.mut('clique para decidir')])],
       edit=dict(m='form',title='Relato',sub='Relógio do aparelho não define vencedor e fases confirmadas não regridem. Os dois relatos ficam preservados; a decisão entra na trilha.',
         fields=[dict(k='tipo',l='Situação do relato',t='txt',ro=True),dict(k='rel',l='Relato · dispositivo',ro=True),dict(k='idl',l='Identidade local',ro=True),dict(k='srv',l='Servidor',ro=True),
                 dict(k='dec',l='Decisão',t='sel',req=True,opts=['Duplicidade de captura · contar uma vez','Fato distinto · enviar à conferência da O.S.'],cond=dict(k='tipo',eq=T_SB)),
                 dict(k='motivo',l='Motivo',t='area',req=True,help='Ex.: mesma passada registrada por dois dispositivos',cond=dict(k='tipo',eq=T_SB))]),
       search=False,gid='g_syn',total=False)
    EXTRAJS[0]=JS_BASE+f'''
const APTID='{APT["id"]}', HA={APT["ha"]}, OSID='{APT["os"]}';
''' + '''
function EXTRAVALS(self,v){
  const nf=getRow(self,'g_rec','nf'), dv=getRow(self,'g_rec','dev'), b=getRow(self,'g_syn','b');
  const pend=[]; if(!(nf&&nf.v.__ok)) pend.push(['NF 4412','Corrigir e reprocessar a NF 4412',()=>g2open(self,GR('g_rec'),'nf',null)]);
  if(!(dv&&dv.v.__ok)) pend.push(['aceite REQ-031','Consultar a devolução por chave',()=>v.consulta('dev')]);
  if(!(b&&b.v.__ok)) pend.push(['conflito offline','Decidir o conflito offline',()=>g2open(self,GR('g_syn'),'b',null)]);
  const nerp=(!(nf&&nf.v.__ok)?1:0)+(!(dv&&dv.v.__ok)?1:0);
  v.st_t=pend.length?('Simulado · '+pl(pend.length,'pendência','pendências')):'Simulado · conciliado';
  v.c_aqui=pend.length?(pl(nerp,'item','itens')+' no ERP · '+(b&&b.v.__ok?'conflito decidido':'1 conflito')):'tudo conciliado';
  v.c_falta=pend.length?pend.map(p=>p[0]).join(' · '):'nada pendente';
  v.c_prox=pend.length?pend[0][1]:'Conferir a trilha de auditoria';
  v.prim_t=v.c_prox; v.prim_btn=pend.length>0; v.prim_lnk=!pend.length; v.prim_h='CF-04.dc.html'; v.prim_fn=pend.length?pend[0][2]:(()=>{});
  v.consulta=(rid)=>{ const r0=getRow(self,'g_rec',rid); if(r0&&r0.v.__ok) return;
    setRow(self,'g_rec',rid,r=>{ r.v.__ok=1; r.v.erp=r.v.plat; r.p.erp=[{k:'txt',t:String(r.v.plat||'20 sc')}]; r.s.erp='20 sc'; r.p.dif=[CH('Sem diferença','green')]; r.s.dif='Sem diferença';
      r.p.est=[CH('Aceito','green'),BR,MU('confirmado por consulta de chave')]; r.s.est='Aceito'; });
    self.setState({g2toast:'Consulta por chave: o ERP registrou a devolução · estado Aceito — sem reenvio (timeout não presume falha).'}); };
  self.g2after=(gid,rows,r)=>{ if(!r) return;
    if(gid==='g_rec'){ if(r.v.unid_erp==='SC50'){ r.v.__ok=1; r.ro=true; r.p.erp=[{k:'txt',t:'R$ 18.400 · SC50'}]; r.s.erp='R$ 18.400 SC50'; r.p.dif=[CH('Sem diferença','green')]; r.s.dif='Sem diferença';
        r.p.est=[CH('Aceito · reprocessado','green'),BR,MU('EVT-99182 reutilizado · efeito único')]; r.s.est='Aceito';
        self.setState({g2toast:'Reprocessado com de-para sc 50 kg → SC50 · aceito pelo ERP · correlação EVT-99182 preservada — sem duplicar título.'}); }
      else { r.p.est=[CH('Rejeitado de novo','red'),BR,MU(r.v.unid_erp+' não é sc 50 kg no ERP')]; r.s.est='Rejeitado';
        self.setState({g2toast:'ERP rejeitou de novo: '+r.v.unid_erp+' não corresponde a sc 50 kg · nada duplicado — use SC50.'}); } return; }
    if(gid==='g_syn'){ r.v.__ok=1; r.ro=true; const dup=String(r.v.dec).indexOf('Duplicidade')===0;
      r.p.est=[CH(dup?'Decidido · relatos preservados':'Decidido · enviado à conferência','green'),BR,MU(dup?'relato B guardado como duplicidade':'conferência da '+OSID+' decide a área')]; r.s.est='Decidido';
      r.p.srv=dup?[{k:'txt',t:'conta '+HA+' ha uma vez · '+APTID+' mantém o recibo'}]:[{k:'txt',t:'não somado até a conferência · '+APTID+' mantém o recibo'}]; r.s.srv='decidido';
      r.p.rec=[MU('sem recibo · preservado como relato')];
      self.setState({g2toast:dup?('Conflito decidido · '+HA+' ha permanecem contados uma vez · relato do tablet preservado como duplicidade — decisão na trilha de auditoria.')
                                :('Conflito decidido · relato do tablet enviado à conferência da '+OSID+' sem somar área — os dois relatos ficam preservados.')}); } };
}'''
    corpo=(
      continuity('Integrações',H('c_aqui'),H('c_falta'),H('c_prox'))
      + section('Reconciliação · Sankhya (ERP simulado)','Compare plataforma e ERP por documento e linha; clique no item rejeitado para corrigir e reprocessar.','',
        g_rec + nota(f'Em timeout após possível gravação externa, o conector {B("consulta por chave antes de reenviar")}. '
                     'Eventos duplicados ou fora de ordem não duplicam pedido, movimento ou liquidação; queda do ERP não apaga apontamento agrícola aceito.'),state='yellow')
      + section(f'Sincronização offline · {APT["os"]} dia {APT["dia"]}',f'Decida o fato sobreposto; os dois relatos ficam preservados e os {APT["ha"]} ha contam uma vez.','',g_syn,state='red'))
    shell37('CF-03','Reconciliação e sincronização',corpo,fname=fname,crumbs_extra=['Pendências'],
      subtitle='Itens do conector ERP e conflitos entre dispositivos offline, em blocos separados — reprocessar não duplica efeito; fato sobreposto exige decisão humana.',
      status=(H('st_t'),'yellow'),primary_html=prim_dyn(),
      footer='Selo Simulado permanece em toda a tela: demonstração não recebe selo de integração homologada (ERP-01, ERP-03).')

    # ================= CF-04 · Auditoria e parâmetros =================
    fname='CF-04.dc.html'; E._reset_screen(fname); HEIGHTS37[fname]=1380
    trail=[
      ('23/09 06:40',[Pt.link(OS2['id'],'IR-03det.dc.html'),Pt.txt(' · irrigação')],'Serviço · balanço hídrico','A liberar → Liberadas','água sem produto pela necessidade da cultura','liberação automática pela prontidão, sem aprovação'),
      ('22/09 17:12',[Pt.link(OS3['id'],'OS.dc.html'),Pt.txt(' · v1 → v2')],'João · app','só água → fertirrigação (+ Ureia 12 kg/ha)','produto adicionado na mesma tarefa','liberação da água não vale para o saldo com produto · revisão individual do agrônomo'),
      ('22/09 16:05',[Pt.link(f'Contagem {INV["id"]}','EST.dc.html'),Pt.txt(f' · {INV["local"]}')],'Rui · contagem cega',f'{n0(INV["sistema"])} kg → {n0(INV["contado"])} kg {INV["item"]} ({n0(INV_DIF_KG)} kg · {INV_DIF_SC} sc)','divergência de contagem','ajuste aguardando aprovação do gestor · saldo não alterado'),
      ('22/09 09:20',[Pt.b('Fila de expedição · 23/09')],'Rui · alçada AL-08','T2 2º → 1º da fila','T1 atrasado · T2 presente e apto','promessa original de T1 preservada · T4 antecipado mantém a vez'),
      ('20/09 11:02',[Pt.b('Limites de irrigação'),Pt.txt(' · Pivô 2')],'Ana · gestora','lâmina máx. por passada 11 → 12 mm','ajuste do percentímetro','vale para a próxima programação'),
      ('15/09 15:44',[Pt.b('Acesso · Davi Melo')],'Ana · gestora','Ativo → Revogado','desligamento','sessões encerradas · histórico preservado'),
    ]
    g_tr=grid([C('inst','Instante (BRT)',w=100),C('obj','Objeto / versão',w=190),C('aut','Autor / origem',w=150),C('ad','Antes → depois · motivo',w=290),C('efe','Efeito',w=260)],
       [R(f't{i}',ro=True,inst=a,obj=b,aut=c,ad=[Pt.txt(d),Pt.br(),Pt.mut('motivo: '+e)],mot=e,efe=f) for i,(a,b,c,d,e,f) in enumerate(trail)],
       edit=dict(m='ro',title='Evento da trilha',fields=[dict(k='inst',l='Instante (BRT)',ro=True),dict(k='obj',l='Objeto / versão',ro=True),dict(k='aut',l='Autor / origem',ro=True),
                 dict(k='ad',l='Antes → depois · motivo',ro=True),dict(k='mot',l='Motivo',ro=True),dict(k='efe',l='Efeito',ro=True)]),
       so={'k':'inst','d':True},gid='g_tr',total=False)
    g_par=grid([C('par','Parâmetro',w=200),C('val','Valor',w=300),C('fonte','Fonte'),C('sit','Situação')],[
        R('p1',ro=True,par='Fuso horário do registro',val='America/Sao_Paulo (BRT)',fonte='cap. 12',sit=ch('Vigente','green')),
        R('p2',ro=True,par='Retenção da trilha',val='permanente · exportação autorizada por papel',fonte='cap. 30',sit=ch('Vigente','green')),
        R('p3',ro=True,par='Unidades de exibição',val='pt-BR · ha, sc 50 kg, mm, R$ mil, t',fonte='cap. 6',sit=ch('Vigente','green'))],
       edit=dict(m='ro',title='Parâmetro',fields=[dict(k='par',l='Parâmetro',ro=True),dict(k='val',l='Valor',ro=True),dict(k='fonte',l='Fonte',ro=True)]),
       search=False,gid='g_par',total=False)
    lam_ap=str(D.PIVO['lamina_aplicada']).replace('.',','); exh=str(round(D.PIVO['volta_62_h'],1)).replace('.',',')
    g_doc=grid([C('tipo','Tipo'),C('proc','Processo',w=180),C('gar','O que garante',w=320),C('ex','Exemplo',w=220),C('abrir','Abrir')],[
        R('d1',ro=True,tipo=[Pt.tag('FL')],proc='Uma ordem, vários dias',gar='apontamentos diários acumulam na mesma ordem; fechar o turno não conclui',
          ex=f'{OS0["id"]} · {OS0["realizado"]} de {OS0["area"]} ha · dia 4 ({APT["ha"]} ha)',abrir=[Pt.cta('Ver exemplo','OS.dc.html')]),
        R('d2',ro=True,tipo=[Pt.tag('RN')],proc='Água sem produto',gar='libera pela prontidão, sem agrônomo, requisição ou custódia; adicionar produto reclassifica a mesma ordem para o agrônomo',ex=f'{OS2["id"]} · {OS3["id"]}',abrir=[Pt.cta('Ver exemplo','IR-03.dc.html')]),
        R('d3',ro=True,tipo=[Pt.tag('CAL')],proc='Lâmina aplicada no pivô',gar='percentímetro e tempo definem a lâmina, sem duplicar água aplicada',
          ex=f'{D.PIVO["id"]} · {D.PIVO["percent"]}% → {lam_ap} mm em {exh} h/volta',abrir=[Pt.cta('Ver exemplo','IR-01.dc.html')])],
       edit=dict(m='ro',title='Documentação',fields=[dict(k='proc',l='Processo',ro=True),dict(k='gar',l='O que garante',ro=True),dict(k='ex',l='Exemplo',ro=True)]),
       search=False,gid='g_doc',total=False)
    corpo=(
      section('Trilha de decisões','Filtre por objeto, autor ou período no cabeçalho; clique no evento para ver o registro completo.',
        [ic(msgbtn('Exportar autorizado','Exportação registrada · 1.240 eventos no escopo do seu papel · a própria exportação entrou na trilha.'),'doc','Exportar a trilha no escopo do seu papel'),
         drawer_button('Solicitar correção pelo domínio',dict(title='Solicitar correção de um fato',sub='A trilha não se edita: a correção nasce no domínio do objeto, como ajuste/estorno vinculado ao documento de origem.',
           fields=[('Objeto',f'Contagem {INV["id"]} · {INV["local"]}'),('Motivo','Contagem lançada no depósito errado'),('Encaminhar para','Rui (estoque)')],
           confirm='Enviar solicitação',done='Solicitação enviada ao dono do domínio · fato original preservado · correção sairá como ajuste vinculado'),primary=True)],g_tr)
      + section('Parâmetros globais','Consulte fonte e vigência; mudar parâmetro não reescreve fatos passados.','',g_par)
      + section('Documentação de processos','Abra o exemplo navegável de cada fluxo, regra e cálculo.',
        [ic(btn('Consultar política',small=True,href='CF-02.dc.html'),'doc','Abrir o registro central de políticas')],g_doc))
    shell37('CF-04','Auditoria e parâmetros',corpo,fname=fname,
      subtitle='Histórico de decisões, parâmetros globais, retenção e documentação — quem fez o quê, quando, por quê e com que efeito.',
      status=('Trilha íntegra','green'),
      footer='Consulta não edita fato: correção acontece no domínio, por ajuste/estorno vinculado ao documento de origem.')
    # CF-05 (Assinatura e cobrança) saiu daqui em 06/10/2026: areas/assinatura.py, no menu Configurações (PLAT-01). CF-05det virou o detalhe da fatura.
