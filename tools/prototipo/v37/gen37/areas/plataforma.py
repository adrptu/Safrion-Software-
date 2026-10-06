# -*- coding: utf-8 -*-
"""Plataforma (backoffice) da assinatura · PLAT-01 (docs/plataforma-assinaturas/ESPECIFICACAO.md §3.2–3.3). Fora do menu do agricultor
(PRD 57.5); alcançada pelo índice do protótipo. Duas telas irmãs:
BO-02 Assinaturas e cobrança: todas as organizações do mesmo estado (c.assin), a da demonstração medida ao vivo pelo cadastro (assinMedir,
  a mesma do CF-05); primária "Conciliar pagamentos" (eventos simulados do provedor, uma vez cada); detalhe da organização na linha
  (área por fazenda, faturas, eventos, resolver contestação, consulta contratual CF-05). Nunca talhão, cultura, safra, operação ou insumo (R17).
BO-01 Planos e preços: parâmetros de exemplo (a decidir pelo proprietário) e simulação por área calculada no navegador (assinMensalidade).
Saíram (PLAT-D02): BO-01det, BO-02det, BO-03, BO-03det e BO-04 (economia por coorte: volta com 3 coortes de 90 dias, PRD 57.3)."""
from engine import grid, section, esc, BTN_ST, INK, MUTED, LINE, BG, SURF, ACC, YEL, YELS, RED, EXTRAJS
import engine as E
import ui37
from ui37 import shell37, HEIGHTS37, steps_bar
import cenario
import dados_assinatura as DA
from areas.assinatura import CSS, kpis_dyn, painel, linhas, titulo, chip_dyn, injeta, JS_COMUM, SEC, PRI, H, F_, T_

CTX_BO = ('Backoffice da plataforma', None, None); PERFIL_BO = 'Admin plataforma'
PRIV = 'Isolamento: a plataforma vê área e cobrança por organização (e por fazenda na consulta contratual), nunca cultura, safra, operação ou insumo.'


def telas(i):
    return steps_bar([dict(t='Assinaturas e cobrança', href='BO-02.dc.html'), dict(t='Planos e preços', href='BO-01.dc.html')], current=i, label='Telas da plataforma')


BO2_JS = r'''
function boSafe(id){ return String(id).replace(/[^A-Za-z0-9]/g,'_'); }
function boProx(org,A,L){ const h=A.hoje; if(L.e.t==='Cancelada') return 'consulta e exportação até '+assinBr(org.consulta_ate);
  if(L.k.plano==='aval'){ const t=org.trial||{}; return 'avaliação termina '+assinBr(t.fim)+' (dia '+(assinDias(t.inicio,h)+1)+' de '+t.dias+')'; }
  const pd=(org.faturas||[]).find(f=>f.st==='pendente'); if(pd) return 'evento do provedor a conciliar ('+assinComp(pd.comp)+')';
  const ct=(org.faturas||[]).find(f=>f.st==='contestada'); if(ct) return 'contestação de '+assinComp(ct.comp)+' a resolver';
  const ab=assinAberta(org); if(ab){ const d=assinAtraso(ab,h); return d>0?('vencida há '+d+(d===1?' dia':' dias')+((ab.tent||[]).length>=ASSIN_PAR.tentativas?' · '+(ab.tent||[]).length+' tentativas recusadas':'')):('vence '+assinBrC(ab.venc)); }
  return 'próxima fatura '+assinBr(assinMesSeg(h))+(L.ag?' · '+assinPlano(L.ag.plano).nome+' a partir de '+assinBrC(L.ag.desde):''); }
function boFila(A){ return (A.fila||[]).map(ev=>({ev,visto:A.vistos.indexOf(ev.evt)>=0})); }
function PREVALS(self,v){ cenOuvir(self); assinOuvir(self); const A=assinLer(); const cart=assinCarteira(A,ASSIN_CAD0,assinCadSalvo()); self._bo={A,cart};
  aGrid('g_org').rows=cart.linhas.map(L=>{ const o=L.org; const P=assinPlano(L.k.plano)||{}; const ab=L.ab.slice().sort((a,b)=>(a.comp<b.comp?-1:1))[0];
    const fat=ab?(assinComp(ab.comp)+' · '+assinFatEstado(ab,A.hoje)):'—'; const prox=boProx(o,A,L);
    return {id:o.id,dr:'bo_org_'+boSafe(o.id),v:{org:o.nome,plano:P.nome,est:L.e.t,med:L.med,con:L.k.plano==='aval'?'':L.k.ha,mens:L.m?L.m.valor:'',fat:fat,prox:prox},s:{org:o.nome,est:L.e.t},
      p:{org:[{k:'b',t:o.nome},{k:'mut',t:o.demo?'demonstração · medida no cadastro':'medida informada'}],est:[aCh(L.e.t,L.e.c)],
         mens:L.m?[{k:'txt',t:assinR(L.m.valor)}]:[{k:'mut',t:L.e.t==='Cancelada'?'—':'R$ 0,00 (avaliação)'}],
         fat:ab?[aCh(fat,ASSIN_FCOR[assinFatEstado(ab,A.hoje)])]:[{k:'mut',t:'—'}]}}; });
  aGrid('g_fila').rows=boFila(A).map(x=>{ const ev=x.ev; const o=A.orgs[ev.org]||{}; const f=(o.faturas||[]).find(y=>y.id===ev.fat)||{};
    return {id:ev.evt,v:{evt:ev.evt,org:o.nome||ev.org,comp:f.comp?assinComp(f.comp):'—',val:ev.valor,res:ev.ok?'aprovado':'recusado',sit:x.visto?'Conciliado':'A conciliar'},s:{sit:x.visto?'Conciliado':'A conciliar'},
      p:{evt:[{k:'b',t:ev.evt},{k:'mut',t:assinBrC(ev.d)+' · '+ev.forma}],res:[aCh(ev.ok?'aprovado':'recusado · '+ev.motivo,ev.ok?'green':'red')],sit:[aCh(x.visto?'Conciliado':'A conciliar',x.visto?'gray':'yellow')]}}; }); }
function EXTRAVALS(self,v){ const {A,cart}=self._bo; const st=self.state;
  const n=cart.n; const pend=boFila(A).filter(x=>!x.visto).length;
  aSelo(self,v,'bo_st',pend?(pend+(pend===1?' evento a conciliar':' eventos a conciliar')):'Pagamentos conciliados',pend?'yellow':'green');
  v.bo_k0v=assinR(cart.vig); v.bo_k0s=(cart.linhas.filter(L=>L.m).length)+' organizações pagantes · contrato de hoje';
  v.bo_k1v=String(cart.linhas.length); v.bo_k1s=['Ativa','Em atraso','Inadimplente','Em avaliação','Cancelada'].filter(t=>n[t]).map(t=>t+' '+n[t]).join(' · ');
  v.bo_k2v=cart.abertas+' · '+assinR(cart.abertasV); v.bo_k2s='a vencer, vencidas, pendentes ou em contestação';
  v.bo_k3v=assinHa(cart.cobrada); v.bo_k3s='medida '+assinHa(cart.medida)+' · cobrada = mín(medida; contratada)';
  v.bo_conciliar=()=>cenMudar(self,c=>assinConciliar(c,assinChave('con')));
  cart.linhas.forEach(L=>{ v['bo_org_'+boSafe(L.org.id)]=()=>self.setState({bo_org:L.org.id,bo_res:'',bo_cred:'',bo_rchave:assinChave('res'),bo_rerr:''}); });
  // ---- detalhe da organização ----
  const L=st.bo_org?cart.linhas.find(x=>x.org.id===st.bo_org):null;
  aPainel(self,v,'bo_op',!!L,L?L.org.nome:'',()=>self.setState({bo_org:null}));
  if(L){ const o=L.org, P=assinPlano(L.k.plano)||{}; aSelo(self,v,'bo_oest',L.e.t+(L.e.dias?' · '+L.e.dias+(L.e.dias===1?' dia':' dias'):''),L.e.c);
    const lin=[{t:'Plano',v:P.nome+' · contrato v'+L.k.v+' desde '+assinBr(L.k.desde)},{t:'Área contratada',v:L.k.plano==='aval'?assinHa(L.k.ha)+' declarados (avaliação)':assinHa(L.k.ha)},
      {t:'Área medida',v:assinHa(L.med)+(o.demo?' · ao vivo pelo cadastro · '+L.ntal+' talhões':' · informada pela organização (sintética)')},
      {t:'Área cobrada',v:L.m?assinHa(L.m.cobrada):'—'},{t:'Mensalidade vigente',v:L.m?assinR(L.m.valor):'—'},
      {t:'Pagamento',v:o.cartao?'cartão salvo '+o.cartao+' (token simulado) · '+ASSIN_PAR.tentativas+' tentativas em '+ASSIN_PAR.janela_tent+' dias':'sem cartão salvo · paga pela fatura'}];
    if(L.ag) lin.push({t:'Mudança agendada',v:assinPlano(L.ag.plano).nome+' · '+assinHa(L.ag.ha)+' a partir de '+assinBr(L.ag.desde)});
    if(o.cancelada) lin.push({t:'Cancelamento',v:'a pedido em '+assinBr(o.cancelada)+' · consulta e exportação até '+assinBr(o.consulta_ate)+' · nada é apagado'});
    v.bo_olin=lin.map(x=>Object.assign({st:''},x));
    v.bo_tfaz=!!o.demo; v.bo_ofaz=o.demo?cart.porFaz.map(x=>({t:x.faz,v:assinHa(x.ha)+' · '+x.n+(x.n===1?' talhão':' talhões'),st:''})):[];
    v.bo_ofat=(o.faturas||[]).slice().sort((a,b)=>(a.comp<b.comp?1:-1)).map(f=>{ const fe=assinFatEstado(f,A.hoje); return {t:assinComp(f.comp)+' · '+assinR(f.valor),e:fe,
      st:aSeloSt(ASSIN_FCOR[fe]),dot:aSeloDot(ASSIN_FCOR[fe]),evs:aEventos(f).map(x=>x.d+' · '+x.t).join('\n')}; });
    v.bo_tfat=v.bo_ofat.length>0; v.bo_semfat=!v.bo_tfat;
    v.bo_demo=!!o.demo;
    const ct=(o.faturas||[]).find(f=>f.st==='contestada'); v.bo_tct=!!ct;
    if(ct){ v.bo_ct_t='Contestação de '+assinComp(ct.comp)+' ('+assinR(ct.valor)+'): '+ct.contest.motivo+' · aberta em '+assinBrC(ct.contest.d)+'. A régua está congelada.';
      v.bo_dec=[{k:'manter',t:'Manter o valor'},{k:'creditar',t:'Creditar no próximo período'}].map(x=>({t:x.t,on:String(st.bo_res===x.k),go:()=>self.setState({bo_res:x.k,bo_rerr:''})}));
      v.bo_tcred=st.bo_res==='creditar'; v.bo_cred=st.bo_cred||''; v.bo_setcred=(e)=>self.setState({bo_cred:e.target.value,bo_rerr:''});
      v.bo_rerr=st.bo_rerr||''; v.bo_trerr=!!st.bo_rerr;
      v.bo_resolver=()=>{ const r=cenMudar(self,c=>assinResolver(c,o.id,ct.id,self.state.bo_res,self.state.bo_cred,self.state.bo_rchave)); self.setState({bo_rerr:r.erro||'',bo_rchave:r.erro?self.state.bo_rchave:assinChave('res')}); }; }
    else v.bo_dec=[]; }
  else { v.bo_olin=[]; v.bo_ofaz=[]; v.bo_ofat=[]; v.bo_dec=[]; } }
function aSeloSt(c){ const cc=G2C[c]||G2C.gray; return 'display:inline-flex;align-items:center;gap:6px;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:700;white-space:nowrap;color:'+cc[0]+';background:'+cc[1]+';'; }
function aSeloDot(c){ const cc=G2C[c]||G2C.gray; return 'width:6px;height:6px;border-radius:999px;background:'+cc[0]+';'; }
'''

BO1_JS = r'''
const BO1_AREAS=[20,100,149.5,500,1000,5000];
function PREVALS(self,v){ cenOuvir(self); assinOuvir(self);
  aGrid('g_sim').rows=BO1_AREAS.map(ha=>{ const r={id:'s'+String(ha).replace('.','_'),v:{ha:ha},s:{},p:{}}; ASSIN_PAR.planos.filter(x=>x.pago).forEach(P=>{ const m=assinMensalidade(P.id,ha,null,0); r.v[P.id]=m.valor;
      r.p[P.id]=[{k:'txt',t:assinR(m.valor)}].concat(m.minimoAplicado?[{k:'mut',t:'mínimo'}]:[]); }); return r; }); }
function EXTRAVALS(self,v){ const st=self.state; const A=assinLer();
  aPainel(self,v,'bo_sp',!!st.bo_sim,'Simular área',()=>self.setState({bo_sim:false}));
  v.bo_simular=()=>self.setState({bo_sim:true}); v.bo_sha=st.bo_sha===undefined?'2.570,23':st.bo_sha; v.bo_setsha=(e)=>self.setState({bo_sha:e.target.value});
  const ha=assinNum(v.bo_sha); const ok=ha>0&&ha<=ASSIN_PAR.limite_ha;
  v.bo_serr=!(ha>0)?'Informe a área em ha (ex.: 2.570,23).':(ha>ASSIN_PAR.limite_ha?'Acima de '+assinNf(ASSIN_PAR.limite_ha,0,0)+' ha: proposta empresarial, a decidir pelo proprietário.':''); v.bo_tserr=!!v.bo_serr;
  v.bo_sres=ok?ASSIN_PAR.planos.filter(x=>x.pago).map(P=>{ const m=assinMensalidade(P.id,ha,null,0); return {t:P.nome+' · '+assinR(P.preco)+'/ha·mês, mínimo '+assinR(P.minimo),
    v:assinR(m.valor)+'/mês'+(m.minimoAplicado?' (mínimo)':' ('+assinR(P.preco)+' × '+assinHa(ha)+')')+' · '+assinR(cenQtd(m.valor,12))+'/ano',st:''}; }):[];
  const tr=A.orgs.boaesp; v.bo_trial='Avaliação em curso: '+tr.nome+' · '+assinHa(tr.contratos[0].ha)+' declarados · '+assinBr(tr.trial.inicio)+' → '+assinBr(tr.trial.fim)+' · sem cartão · '+tr.trial.dias+' dias.'; }
'''


def bo02():
    fname = 'BO-02.dc.html'; E._reset_screen(fname)
    g_org = grid([dict(k='org', l='Organização', w=200), dict(k='plano', l='Plano', w=110), dict(k='est', l='Estado', w=130),
                  dict(k='med', l='Área medida (ha)', t='num', a='r', d=2, dmin=0), dict(k='con', l='Área contratada (ha)', t='num', a='r', d=2, dmin=0),
                  dict(k='mens', l='Mensalidade (R$)', t='num', a='r', d=2), dict(k='fat', l='Fatura aberta', w=170), dict(k='prox', l='Próximo evento', w=280)],
                 [], gid='g_org', search=True, total=False, qf=dict(k='est', todas='Todas'), edit=dict(m='ro', title='Organização', fields=[]))
    g_fila = grid([dict(k='evt', l='Evento', w=190), dict(k='org', l='Organização', w=170), dict(k='comp', l='Fatura'), dict(k='val', l='Valor (R$)', t='num', a='r', d=2),
                   dict(k='res', l='Resultado', w=240), dict(k='sit', l='Situação', w=130)], [], gid='g_fila', search=True, total=False, qf=dict(k='sit', todas='Todos'),
                  edit=dict(m='none'))
    corpo = ('<div class="assin" style="display: flex; flex-direction: column; gap: 18px;">' + CSS
             + kpis_dyn('bo_k', ['Mensalidades vigentes', 'Organizações', 'Faturas abertas', 'Área cobrada'])
             + section('Organizações', 'Abra a organização para ver plano, área por fazenda, faturas e eventos; resolva a contestação no detalhe.', '', g_org)
             + section('Eventos do provedor (simulado)', 'Concilie para aplicar cada evento uma vez: aprovado paga a fatura, recusado fica registrado e a fatura segue aberta.', '', g_fila)
             + f'<div style="font-size: 12.5px; color: {MUTED};">{esc(PRIV)}</div></div>')
    fat = (f'<div><sc-for list="{H("bo_ofat")}" as="fa" hint-placeholder-count="2"><div style="display: flex; flex-direction: column; gap: 4px; padding: 8px 0; border-bottom: 1px solid {LINE};">'
           f'<div style="display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700;"><span style="flex-grow: 1;">{H("fa.t")}</span><span style="{H("fa.st")}"><span style="{H("fa.dot")}"></span>{H("fa.e")}</span></div>'
           f'<div style="font-size: 12px; color: {MUTED}; white-space: pre-line; line-height: 1.45;">{H("fa.evs")}</div></div></sc-for></div>')
    res = (f'<sc-if value="{H("bo_tct")}" hint-placeholder-val="{F_}"><div style="display: flex; flex-direction: column; gap: 8px; padding: 10px 12px; border-radius: 12px; background: {YELS};">'
           f'<span style="font-size: 13px; font-weight: 700; color: {YEL};">{H("bo_ct_t")}</span>'
           f'<div role="radiogroup" aria-label="Decisão" style="display: flex; flex-wrap: wrap; gap: 8px;"><sc-for list="{H("bo_dec")}" as="dc" hint-placeholder-count="2"><button type="button" role="radio" class="assin-esc" aria-checked="{H("dc.on")}" onClick="{H("dc.go")}">{H("dc.t")}</button></sc-for></div>'
           f'<sc-if value="{H("bo_tcred")}" hint-placeholder-val="{F_}"><div style="display: flex; align-items: center; gap: 8px;"><label for="bo_cred" style="font-size: 12px; font-weight: 700; color: {MUTED};">Crédito</label>'
           f'<span style="font-size: 13px; color: {MUTED};">R$</span><input id="bo_cred" type="text" inputMode="decimal" value="{H("bo_cred")}" onChange="{H("bo_setcred")}" style="width: 140px; font-family: inherit; font-size: 14px; padding: 8px 10px; border-radius: 10px; border: 1px solid {LINE};"></div></sc-if>'
           f'<sc-if value="{H("bo_trerr")}" hint-placeholder-val="{F_}"><span role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("bo_rerr")}</span></sc-if>'
           f'<div><button type="button" onClick="{H("bo_resolver")}" style="{SEC}">Resolver contestação</button></div></div></sc-if>')
    corpo_o = (f'<div>{chip_dyn("bo_oest")}</div>' + linhas('bo_olin')
               + f'<sc-if value="{H("bo_tfaz")}" hint-placeholder-val="{F_}">{titulo("Área por fazenda (consulta contratual)")}{linhas("bo_ofaz")}</sc-if>'
               + res + titulo('Faturas e eventos') + f'<sc-if value="{H("bo_semfat")}" hint-placeholder-val="{F_}"><span style="font-size: 13px; color: {MUTED};">Sem fatura: avaliação sem cobrança.</span></sc-if>' + fat
               + f'<span style="font-size: 11.5px; color: {MUTED};">{esc(PRIV)}</span>')
    rod_o = (f'<sc-if value="{H("bo_demo")}" hint-placeholder-val="{F_}"><div style="display: flex; justify-content: flex-end; padding-top: 10px; border-top: 1px solid {LINE};">'
             f'<a href="CF-05.dc.html" style="text-decoration: none; display: inline-block; {SEC}">Consulta contratual (CF-05) ›</a></div></sc-if>')
    E.EXTRA.append(painel('bo_op', corpo_o, rod_o, 520))
    EXTRAJS[0] = cenario.js_prefixo() + DA.js_cad0() + JS_COMUM + BO2_JS
    HEIGHTS37[fname] = 1150
    shell37('BO-02', 'Assinaturas e cobrança', corpo, fname=fname, ctx=CTX_BO, perfil=PERFIL_BO, steps=telas(1), search=False,
            subtitle='Plataforma · cobrança simulada, nenhum provedor real. Todas as organizações no mesmo estado; a da demonstração é medida ao vivo no cadastro.',
            primary_html=f'<button type="button" onClick="{H("bo_conciliar")}" style="{BTN_ST(True)}">Conciliar pagamentos</button>',
            footer='Fatura só fica Paga por evento do provedor (simulado), aplicado uma vez. Nada é apagado.')
    injeta(fname, 'Assinaturas e cobrança', chip_dyn('bo_st'))


def bo01():
    fname = 'BO-01.dc.html'; E._reset_screen(fname)
    ui37.CAT['BO-01'] = dict(ui37.CAT.get('BO-01', {}), titulo='Planos e preços')
    def fr(P): return (f"satélite {P['sat']} {P['sat_un']} · IA {P['ia']} {P['ia_un']}")
    rows = []
    for P in DA.PLANOS:
        pre = 'R$ 0,00' if not P['pago'] else ('R$ ' + f"{P['preco']:.2f}".replace('.', ','))
        mi = 'R$ 0,00' if not P['pago'] else ('R$ ' + f"{P['minimo']:.2f}".replace('.', ','))
        ano = '—' if not P['pago'] else ('R$ ' + f"{P['preco'] * 12:.2f}".replace('.', ',') + '/ha·ano')
        lim = 'área declarada (480 ha na Boa Esperança)' if P['limite'] is None else f"até {P['limite']:,} ha".replace(',', '.')
        v = dict(plano=P['nome'], mod=', '.join(P['modulos']), lim=lim, usu=P['usuarios'], fr=fr(P), preco=P['preco'], min=P['minimo'], ano=ano,
                 dec=P['dec'] + ' · ' + DA.DECIDIR, obs=P['obs'], pre_t=pre, min_t=mi)
        rows.append(dict(id='p_' + P['id'], v=v, s=dict(preco=pre, min=mi), p=dict(plano=[dict(k='b', t=P['nome'])], preco=[dict(k='txt', t=pre), dict(k='mut', t='exemplo')],
                                                                                  min=[dict(k='txt', t=mi), dict(k='mut', t='exemplo')], dec=[dict(k='chip', t=P['dec'], c='yellow'), dict(k='mut', t='a decidir pelo proprietário')])))
    ro = lambda k, l, t='txt': dict(k=k, l=l, t=t, ro=True)
    g_par = grid([dict(k='plano', l='Plano', w=110), dict(k='mod', l='Módulos', w=320), dict(k='lim', l='Limite de área', w=170), dict(k='usu', l='Usuários'),
                  dict(k='fr', l='Franquias', w=240), dict(k='preco', l='Preço R$/ha·mês', t='num', a='r'), dict(k='min', l='Mínimo R$/mês', t='num', a='r'),
                  dict(k='ano', l='Equivalente R$/ha·ano', a='r'), dict(k='dec', l='Decisão pendente', w=230)], rows, gid='g_par', search=True, total=False,
                 edit=dict(m='ro', title='Plano', fields=[ro('mod', 'Módulos', 'area'), ro('lim', 'Limite de área'), ro('usu', 'Usuários'), ro('fr', 'Franquias'),
                                                         ro('pre_t', 'Preço por ha e mês'), ro('min_t', 'Mínimo por mês'), ro('ano', 'Equivalente por ha e ano'), ro('obs', 'Observação'), ro('dec', 'Decisão pendente')]))
    cols = [dict(k='ha', l='Área (ha)', t='num', a='r', d=2, dmin=0)] + [dict(k=P['id'], l=P['nome'] + ' (R$)', t='num', a='r', d=2) for P in DA.PLANOS if P['pago']]
    g_sim = grid(cols, [], gid='g_sim', search=True, total=False, edit=dict(m='none'))
    texto = (f'<div style="font-size: 13px; color: {INK}; line-height: 1.6;"><b>PRECO-01:</b> R$ 2,00/ha·mês = R$ 24,00/ha·ano. <b>Mínimo:</b> cobra-se o maior entre o mínimo e preço × área (não se soma). '
             f'<b>Mudança:</b> vale do dia 1 do próximo ciclo e nunca retroage. <b>Base (DEC-01):</b> área medida no cadastro, limitada pela contratada. '
             f'<span style="color: {YEL}; font-weight: 700;">Todos os valores são exemplo, a decidir pelo proprietário (DEC-01, DEC-05, DEC-09).</span></div>'
             f'<div style="font-size: 12.5px; color: {MUTED}; padding-top: 6px;">{H("bo_trial")}</div>')
    corpo = ('<div class="assin" style="display: flex; flex-direction: column; gap: 18px;">' + CSS
             + section('Planos e parâmetros', 'Confira o que cada plano inclui e o que falta o proprietário decidir; clique no plano para ver tudo.', '', g_par)
             + section('Simulação por área (PRECO-03)', 'Compare a mensalidade de cada plano por área; os valores são calculados no navegador pela mesma regra do CF-05.', '', g_sim)
             + section('Regras', '', '', texto, state='yellow') + '</div>')
    corpo_s = (f'<div style="display: flex; flex-direction: column; gap: 4px;"><label for="bo_sha" style="font-size: 12px; font-weight: 800; letter-spacing: .06em; color: {MUTED}; text-transform: uppercase;">Área</label>'
               f'<div style="display: flex; align-items: center; gap: 8px;"><input id="bo_sha" type="text" inputMode="decimal" value="{H("bo_sha")}" onChange="{H("bo_setsha")}" style="width: 160px; font-family: inherit; font-size: 14px; padding: 9px 11px; border-radius: 10px; border: 1px solid {LINE};">'
               f'<span style="font-size: 13px; color: {MUTED};">ha</span></div>'
               f'<sc-if value="{H("bo_tserr")}" hint-placeholder-val="{F_}"><span role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("bo_serr")}</span></sc-if></div>'
               + titulo('Mensalidade por plano') + linhas('bo_sres')
               + f'<span style="font-size: 11.5px; color: {MUTED};">Exemplo, a decidir pelo proprietário. Simular não muda nenhum contrato.</span>')
    E.EXTRA.append(painel('bo_sp', corpo_s, '', 460))
    EXTRAJS[0] = cenario.js_prefixo() + JS_COMUM + BO1_JS
    HEIGHTS37[fname] = 1050
    shell37('BO-01', 'Planos e preços', corpo, fname=fname, ctx=CTX_BO, perfil=PERFIL_BO, steps=telas(2), search=False,
            subtitle='Parâmetros de exemplo dos planos (a decidir pelo proprietário) e simulação por área. Nada aqui gera cobrança real.',
            primary_html=f'<button type="button" onClick="{H("bo_simular")}" style="{BTN_ST(True)}">Simular área</button>',
            footer='Versões de plano (criar, aprovar) voltam quando o proprietário decidir DEC-01/05/09.')


def build():
    bo02(); bo01()
