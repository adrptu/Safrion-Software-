# -*- coding: utf-8 -*-
"""Área Configurações (menu, último grupo; CONF-01, docs/configuracoes/ESPECIFICACAO.md e DECISOES.md).
CF-01 Usuários e alçadas (pessoas do CD-04 com acesso e papéis; alçadas lidas pelos comandos) · CF-04 Auditoria (trilha lida dos registros)
· CF-03 Integrações (demonstração, fila do ERP do cenário). CF-05 Assinatura e cobrança está em areas/assinatura.py (PLAT-01).
CF-02, CF-02det e CF-03det saíram (CONF-D01, CONF-D20). Estado: c.conf do cenário salvo (configuracoes.js, prefixo de toda tela);
nada aqui é digitado à mão nem guarda credencial (ENG-017). Cada tela: uma primária; detalhe = painel modal da linha."""
from engine import grid, section, esc, BTN_ST, INK, MUTED, LINE, BG, SURF, ACC, ACCS, YEL, YELS, RED, REDS, EXTRAJS
import engine as E
import ui37
from ui37 import shell37, HEIGHTS37

H=lambda s: '{{'+s+'}}'

# ===================================== CF-01 · Usuários e alçadas (CONF-01 §3.1) =====================================
# Quem entra e quem decide cada comando, numa tela: pessoas = CD-04 (CONF0), papéis e acesso = c.conf, alçadas = G2_ALCADAS + c.conf (as mesmas
# que os comandos leem). Detalhe = painel da linha (modal; com ele aberto, conta só a primária do painel). Uma primária no cabeçalho, pela ordem:
# Confirmar AL-xx (mudança pendente que o perfil confirma) › Resolver AL-xx (sem titular) › Convidar pessoa.
from areas.assinatura import painel, titulo, injeta, chip_dyn, JS_COMUM as A_JS
import cenario
SEC = BTN_ST(False, True)
PRI = BTN_ST(True, True)
F_ = H('false'); T_ = H('true')
CF1_CSS = ('<style>'
           '.conf-sw{display:flex;flex-direction:column;align-items:flex-start;gap:2px;text-align:left;font-family:inherit;padding:8px 12px;border-radius:12px;border:1px solid #E4E9E5;background:#FFFFFF;color:#15201A;cursor:pointer;min-width:0}'
           '.conf-sw[aria-checked=true]{border-color:#1E7A4C;background:#E4F3E9}.conf-sw:disabled{opacity:.5;cursor:not-allowed}'
           '.conf-swt{font-size:13px;font-weight:800}.conf-sws{font-size:11.5px;color:#65736A;line-height:1.3}'
           '.conf-paps{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}'
           '.conf-lin{display:flex;justify-content:space-between;gap:12px;padding:6px 0;border-bottom:1px solid #E4E9E5;font-size:13px;line-height:1.4}'
           '.conf-lin>span:first-child{color:#65736A;flex-shrink:0;max-width:42%}.conf-lin>span:last-child{text-align:right;min-width:0;overflow-wrap:anywhere}'
           '.conf-esc{font-family:inherit;font-size:13px;font-weight:700;padding:8px 14px;border-radius:999px;border:1px solid #E4E9E5;background:#FFFFFF;color:#15201A;cursor:pointer;text-align:left}'
           '.conf-esc[aria-checked=true]{border-color:#1E7A4C;background:#E4F3E9;color:#1E7A4C}'
           '.conf-prim:disabled{opacity:.5;cursor:not-allowed}'
           '.conf-nota{font-size:12.5px;color:#65736A;line-height:1.45}'
           '@media (max-width:640px){.conf-paps{grid-template-columns:1fr}}'
           '</style>')
CF1_JS = r'''
// ---- CF-01 · Usuários e alçadas: linhas, primária e painéis (estado: c.conf por confLer; gravação: comandos conf* dentro de cenMudar) ----
/* radiogroup pelo teclado (revisão CONF 13/10): setas movem e escolhem; Tab entra só na opção marcada (um ponto de Tab por grupo) */
function cf1Setas(e){ const k=e.key; const d=(k==='ArrowDown'||k==='ArrowRight')?1:((k==='ArrowUp'||k==='ArrowLeft')?-1:0); if(!d) return;
  const g=e.currentTarget; const bs=[...g.querySelectorAll('[role=radio]')]; const i=bs.indexOf(document.activeElement); if(i<0) return;
  e.preventDefault(); const j=(i+d+bs.length)%bs.length; bs[j].click(); bs[j].focus(); setTimeout(()=>{ const n=[...g.querySelectorAll('[role=radio]')][j]; if(n&&document.activeElement!==n) n.focus(); },0); }
function cf1Safe(id){ return String(id).replace(/[^A-Za-z0-9]/g,'_'); }
function cf1Rot(x){ const P=G2_PAPEIS.find(y=>y.k===x); return P?P.t:x; }
function cf1PapT(a){ return a.papeis.map(x=>((G2_PAPEIS.find(y=>y.k===x)||{}).m||x)).join(a.modo==='um'?' ou ':' e '); }
function cf1Nomes(K,a){ return g2perfisDe(K).filter(P=>confPodeA(P,a)).map(P=>P.k); }
function cf1QuemT(K,a){ const L=cf1Nomes(K,a); return cf1PapT(a)+' · '+(L.length?L.join(', '):'sem titular'); }
function cf1Ev(K,id){ return (K.ev||[]).filter(e=>e.alvo===id&&/^alc/.test(e.tipo)); }
function cf1Desde(K,id){ const L=cf1Ev(K,id).filter(e=>e.tipo==='alc'||e.tipo==='alc-conf'); return L.length?L[L.length-1].d:CONF0.alc_desde; }
function cf1PodeConf(K,PF,id){ const pd=K.pend[id]; if(!pd||!PF||PF.k===pd.k) return false; return confPodeA(confAtor(K,PF),g2alcDe(K,'AL-14').conf); }
function cf1Gestor(K,PF){ return confPodeA(confAtor(K,PF),g2alcDe(K,'AL-13')); }
function cf1Lim(a){ if(a.id==='AL-05') return 'até '+a.lim+' % da área da ordem · acima: '+cf1PapT(a.acima);
  if(a.id==='AL-10') return 'até '+a.lim+' · acima: '+cf1PapT(a.acima); return a.lim?String(a.lim):(a.obs&&a.id==='AL-01'?'fora: irrigação só com água (DEC-2609-10)':'—'); }
function cf1Mud(b){ return b.edita==='papel'?'Editável: papel':(b.edita==='lim'?'Editável: limite em %':(b.edita==='acima'?'Editável: excedente':'Fixa: '+b.fixa)); }
// quem pode receber o papel que falta (sem titular): ativos, habilidade do CD-04 primeiro, agrônomo só com CREA válido, nunca o próprio perfil (R3)
const CF1_HAB={conferente:'Conferir',almoxarife:'Almoxarifado',mecanico:'Manutenção de máquinas',agronomo:'Liberar O.S. (agrônomo)'};
function cf1Falta(K,id){ const a=g2alcDe(K,id); const P=g2perfisDe(K); if(!P.some(x=>confPodeA(x,a))) return {nivel:'base',a,papeis:a.modo==='um'?[a.papeis[0]]:a.papeis};
  if(a.acima&&id!=='AL-05'&&!P.some(x=>confPodeA(x,a.acima))) return {nivel:'acima',a:a.acima,papeis:a.acima.modo==='um'?[a.acima.papeis[0]]:a.acima.papeis}; return null; }
// sem candidato (revisão F9): por que ninguém pode receber agora e o caminho (R3: outra pessoa com gestor concede; R4: CREA no CD-04)
function cf1SemCand(K,papeis,PF){ const ag=papeis.indexOf('agronomo')>=0; const at=CONF0.pessoas.filter(p=>(K.pessoas[p.id]||{}).a==='ativo');
  const eu=PF&&at.find(p=>p.k===PF.k&&(!ag||confCrea(p))); const L=[];
  if(eu) L.push('Você ('+eu.k+') pode receber, mas ninguém concede papel a si mesmo (R3): outra pessoa com o papel de gestor concede'+(g2perfisDe(K).some(P=>P.papeis.gestor&&P.k!==eu.k)?'.':'; conceda gestor a outra pessoa antes, no painel dela.'));
  if(ag) L.push('Agrônomo só com CREA válido: cadastre a habilitação em Cadastros › Pessoas e equipes (CD-04) e volte aqui.');
  return L.join(' ')||'Ninguém ativo pode receber: convide ou reative uma pessoa antes.'; }
function cf1Cand(K,papeis,PF){ return CONF0.pessoas.filter(p=>{ const e=K.pessoas[p.id]; return e&&e.a==='ativo'&&(!PF||p.k!==PF.k)&&(papeis.indexOf('agronomo')<0||confCrea(p)); })
  .map(p=>({p,hab:papeis.some(x=>CF1_HAB[x]&&p.hab.indexOf(CF1_HAB[x])>=0)})).sort((x,y)=>(y.hab-x.hab)||x.p.k.localeCompare(y.p.k,'pt-BR')); }
function cf1Abre(self,o){ self.setState(Object.assign({cf1_p:null,cf1_a:null,cf1_cv:false,cf1_err:'',cf1_pp:null,cf1_mud:null,cf1_mot:'',cf1_tit:''},o)); self.__cf1k=confChave('cf1'); }
function cf1Run(self,fn,fecha,fl){ const r=cenMudar(null,fn); if(r.erro){ self.setState({cf1_err:r.erro}); return r; }
  self.__cf1k=confChave('cf1'); self.setState(Object.assign({cenrev:Date.now(),g2toast:r.msg||'',cf1_err:''},fl?confFl(self,fl):{},fecha||{})); return r; }   /* depois de gravar, chave nova (R12) */
function PREVALS(self,v){ cenOuvir(self); const K=confLer(cenGet()); self._cf1={K};
  aGrid('g_pes').rows=CONF0.pessoas.slice().sort((x,y)=>x.k.localeCompare(y.k,'pt-BR')).map(p=>{ const e=K.pessoas[p.id]||{a:'sem',papeis:[]}; const at=e.a==='ativo';
    const dec=at?confDecide(K,p.k):[]; const grp=at?'Com acesso':(e.a==='desativado'?'Desativadas':'Sem acesso'); const pap=e.papeis.map(x=>confRot(x,p));
    return {id:'pe_'+p.id,dr:'cf1_pe_'+cf1Safe(p.id),v:{nome:p.k,pap:pap.join(', '),dec:dec.length,acs:grp},
      s:{nome:p.k+' · '+p.equipe,pap:pap.length?pap.join(', '):(at?'só app de campo':'—'),dec:dec.length?dec.length+' · '+dec.join(', '):'—',acs:grp+' · '+p.k+' · '+confAcessoT(e)},   /* ordena por acesso e depois nome */
      p:{nome:[{k:'b',t:p.k},{k:'mut',t:p.equipe+' · '+p.funcao}],pap:pap.length?pap.map(t=>aCh(t,at?'green':'gray')):[{k:'mut',t:at?'só app de campo':'—'}],
        dec:dec.length?[{k:'b',t:String(dec.length)},{k:'mut',t:dec.join(', ')}]:[{k:'mut',t:'—'}],acs:[aCh(confAcessoT(e),at?'green':(e.a==='desativado'?'gray':'yellow'))]},
      m:{pap:e.papeis.map(x=>({id:x,l:cf1Rot(x)})),acs:[{id:grp,l:grp}]}}; });
  const sem=confSemTitular(K);
  aGrid('g_alc').rows=G2_ALCADAS.map(b=>{ const a=g2alcDe(K,b.id); const pd=K.pend[b.id]; const st=sem.indexOf(b.id)>=0;
    const sit=pd?'Aguarda 2º aprovador':(st?'Sem titular':'Vigente v'+a.v+' desde '+confBr(cf1Desde(K,b.id)));
    const quem=cf1QuemT(K,a)+(a.acima&&b.id!=='AL-05'?' · excedente: '+cf1QuemT(K,a.acima):'');
    const tags=[b.edita?'Editáveis':'Fixas'].concat(pd||st?['Pendências']:[]);
    return {id:'al_'+b.id,dr:'cf1_al_'+cf1Safe(b.id),v:{alc:b.id,quem,lim:cf1Lim(a),sit,mud:cf1Mud(b)},
      s:{alc:b.id+' · '+b.t+' · '+b.cmd,quem,lim:cf1Lim(a),sit,mud:tags.join(', ')},
      p:{alc:[{k:'b',t:b.id+' · '+b.t},{k:'mut',t:b.cmd}],quem:[{k:'txt',t:quem}],lim:[{k:'txt',t:cf1Lim(a)}],sit:[aCh(sit,pd?'yellow':(st?'red':'green'))],mud:[{k:b.edita?'txt':'mut',t:cf1Mud(b)}]},
      m:{mud:tags.map(t=>({id:t,l:t}))}}; }).concat([{id:'al_AL-16',dr:'cf1_al_AL_16',v:{alc:'AL-16'},
      s:{alc:'AL-16 · Aprovar compra de insumos · Compra de insumos',quem:CONF0.compras.map(x=>x.quem).join(' · '),lim:'R$ por compra',sit:'Vigente (lida da Compra de insumos)',mud:'Só leitura'},
      p:{alc:[{k:'b',t:'AL-16 · Aprovar compra de insumos'},{k:'mut',t:'Compra de insumos'}],quem:[{k:'txt',t:CONF0.compras.map(x=>x.quem+(x.ate?' até '+assinR(x.ate):' acima')).join(' · ')}],
        lim:[{k:'txt',t:'R$ por compra'}],sit:[aCh('Vigente · lida da Compra de insumos','green')],mud:[{k:'mut',t:'Só leitura: a Compra de insumos aplica'}]},m:{mud:[{id:'Só leitura',l:'Só leitura'}]}}]); }
function EXTRAVALS(self,v){ const K=self._cf1.K; const st=self.state; const PF=g2perfil(); const c=cenGet(); const sem=confSemTitular(K); const gest=cf1Gestor(K,PF);
  const K1=self.__cf1k||(self.__cf1k=confChave('cf1'));   /* chave e rascunho capturados no desenho: o 2º clique do mesmo desenho repete o mesmo comando (mesmo recibo, R12), nunca outro */
  const npes=confComAcesso(K), nsem=CONF0.pessoas.filter(p=>(K.pessoas[p.id]||{}).a==='sem');
  const pend=Object.keys(K.pend); const pc=pend.find(id=>cf1PodeConf(K,PF,id));
  aSelo(self,v,'cf1_st',sem.length?sem[0]+' sem titular':(pend.length?pend[0]+' aguarda confirmação':npes+' com acesso · '+nsem.length+' sem acesso'),sem.length?'red':(pend.length?'yellow':'gray'));
  // primária única, pela ordem do §3.1
  v.cf1_prim_dis=false; v.cf1_prim_tit='';
  if(pc){ v.cf1_prim_t='Confirmar '+pc; v.cf1_prim_fn=()=>cf1Abre(self,{cf1_a:pc}); }
  else if(sem.length){ v.cf1_prim_t='Resolver '+sem[0]; v.cf1_prim_fn=()=>cf1Abre(self,{cf1_a:sem[0]}); }
  else { v.cf1_prim_t='Convidar pessoa'; v.cf1_prim_fn=()=>cf1Abre(self,{cf1_cv:true});
    if(!gest){ v.cf1_prim_dis=true; v.cf1_prim_tit='Convidar: decisão de '+confQuemA(K,g2alcDe(K,'AL-13')); }
    else if(!nsem.length){ v.cf1_prim_dis=true; v.cf1_prim_tit='Todas as pessoas do cadastro têm acesso'; } }
  if(v.cf1_prim_dis) v.cf1_prim_t=v.cf1_prim_tit;   /* o motivo no próprio rótulo, visível no toque e no leitor de tela (revisão CONF 13/10; convenção do engine) */
  v.cf1_prim_lab=v.cf1_prim_tit||v.cf1_prim_t; v.cf1_setas=cf1Setas;
  CONF0.pessoas.forEach(p=>{ v['cf1_pe_'+cf1Safe(p.id)]=()=>cf1Abre(self,{cf1_p:p.id}); });
  G2_ALCADAS.forEach(b=>{ v['cf1_al_'+cf1Safe(b.id)]=()=>cf1Abre(self,{cf1_a:b.id}); }); v.cf1_al_AL_16=()=>cf1Abre(self,{cf1_a:'AL-16'});
  // atalhos: CF-01.dc.html#pessoa=Caio · #alc=AL-05
  if(!self.__cf1h){ self.__cf1h=1; let h=''; try{ h=decodeURIComponent(location.hash||''); }catch(e){} const m1=/pessoa=([^&]+)/.exec(h), m2=/alc=(AL-\d+)/.exec(h);
    const pp=m1&&confP(m1[1]); if(pp) setTimeout(()=>cf1Abre(self,{cf1_p:pp.id}),0); else if(m2) setTimeout(()=>cf1Abre(self,{cf1_a:m2[1]}),0); }
  v.cf1_err=st.cf1_err||''; v.cf1_terr=!!st.cf1_err;
  // ---- painel Convidar: lista curta de quem está sem acesso (um toque abre a pessoa; o comando fica no painel dela) ----
  aPainel(self,v,'cf1_cvp',!!st.cf1_cv,'Convidar pessoa',()=>self.setState({cf1_cv:false}));
  v.cf1_cvl=nsem.map(p=>({t:p.k+' · '+p.equipe+' · '+p.funcao,go:()=>cf1Abre(self,{cf1_p:p.id})})); v.cf1_cvnada=!nsem.length;
  // ---- painel Pessoa ----
  const p=st.cf1_p?confP(st.cf1_p):null; const e=p?(K.pessoas[p.id]||{a:'sem',papeis:[]}):null;
  aPainel(self,v,'cf1_pp',!!p,p?p.k+' · '+p.equipe:'',()=>self.setState({cf1_p:null,cf1_err:''}));
  if(p){ const at=e.a==='ativo'; const dr=st.cf1_pp||e.papeis; const eu=!!PF&&PF.k===p.k;
    aSelo(self,v,'cf1_pac',confAcessoT(e),at?'green':(e.a==='desativado'?'gray':'yellow'));
    v.cf1_pcad=[{t:'Função (CD-04)',v:p.funcao||'—'},{t:'Habilidades',v:p.hab.join(' · ')||'—'}].concat(p.crea?[{t:'CREA',v:'válido até '+confBr(p.crea)+(confCrea(p)?'':' · vencido')}]:[]).map(x=>Object.assign({st:''},x));
    v.cf1_pcadh='CD-04.dc.html';
    v.cf1_paps=G2_PAPEIS.map(P=>{ const on=dr.indexOf(P.k)>=0; const dc=G2_ALCADAS.filter(b=>{ const a=g2alcDe(K,b.id); return a.papeis.indexOf(P.k)>=0||(a.acima&&a.acima.papeis.indexOf(P.k)>=0); }).map(b=>b.id);
      const semCrea=P.k==='agronomo'&&!confCrea(p)&&!on; const dis=!at||!gest||semCrea;
      return {t:confRot(P.k,p),s:semCrea?'exige CREA válido no CD-04 (lei)':(dc.length?'decide: '+dc.join(', '):'nenhuma alçada'),on:String(on),dis,tit:semCrea?'Agrônomo só com CREA válido no cadastro (lei: receituário e aprovação agronômica)':'',
        go:()=>{ if(dis) return; const cur=(self.state.cf1_pp||e.papeis).slice(); const i=cur.indexOf(P.k); if(i>=0) cur.splice(i,1); else cur.push(P.k); self.setState({cf1_pp:cur,cf1_err:''}); }}; });
    const ganha=dr.filter(x=>e.papeis.indexOf(x)<0), perde=e.papeis.filter(x=>dr.indexOf(x)<0); const mudou=!!(ganha.length||perde.length);
    let semN=[]; if(mudou){ const Kx=confClone(K); Kx.pessoas[p.id]=Object.assign({},e,{papeis:dr}); const s0=confSemTitular(K); semN=confSemTitular(Kx).filter(x=>s0.indexOf(x)<0); }
    v.cf1_ppv=[{t:'Ganha',v:ganha.length?ganha.map(x=>confRot(x,p)).join(', '):'—'},{t:'Perde',v:perde.length?perde.map(x=>confRot(x,p)).join(', '):'—'},
      {t:'Alçadas que ficam sem titular',v:semN.length?semN.join(', ')+' (aviso: resolva em seguida)':'nenhuma',st:semN.length?'color:#B42318;font-weight:700;':''}].map(x=>Object.assign({st:''},x));
    if(eu&&mudou&&!dr.length) v.cf1_ppv.push({t:'Você sem nenhum papel',v:'Ninguém retira todos os próprios papéis: o perfil de demonstração passaria a outra pessoa e o próximo ato sairia em nome dela. Peça a outra pessoa com o papel de gestor.',st:'color:#B42318;font-weight:700;'});   /* revisão CONF 10/10 (CONF-D34) */
    v.cf1_ptpv=mudou; v.cf1_pnota=!gest?'Conceder e retirar papel, convidar e desativar: decisão de '+confQuemA(K,g2alcDe(K,'AL-13'))+'.':(at?(e.papeis.length||dr.length?'':'Sem papel: '+p.k+' só usa o app de campo.'):(e.a==='desativado'?'Acesso desativado: '+p.k+' não aparece no Ver como e não decide. Os registros antigos guardam o nome.':'Sem acesso: o convite é simulado e aceito na hora; nenhuma mensagem real é enviada.'));
    v.cf1_temnota=!!v.cf1_pnota;
    // primária do painel: Salvar papéis (ativo) · Convidar (sem acesso) · Reativar acesso (desativado)
    const dr0=dr.slice();
    const FLP=[['g_pes','pe_'+p.id]];
    if(at){ v.cf1_ppt='Salvar papéis'; v.cf1_ppdis=!gest||!mudou; v.cf1_ppfn=()=>cf1Run(self,c=>confPapeis(c,p.id,dr0,K1,g2perfil()),{cf1_pp:null,cf1_p:null},FLP); }
    else if(e.a==='sem'){ v.cf1_ppt='Convidar (simulado)'; v.cf1_ppdis=!gest; v.cf1_ppfn=()=>cf1Run(self,c=>confConvidar(c,p.id,K1,g2perfil()),{cf1_pp:null,cf1_p:null},FLP); }
    else { v.cf1_ppt='Reativar acesso'; v.cf1_ppdis=!gest; v.cf1_ppfn=()=>cf1Run(self,c=>confAcesso(c,p.id,true,K1,g2perfil()),{cf1_pp:null,cf1_p:null},FLP); }
    v.cf1_pdes=at&&gest&&!eu; v.cf1_pdesfn=()=>cf1Run(self,c=>confAcesso(c,p.id,false,K1,g2perfil()),{cf1_pp:null,cf1_p:null},FLP);   /* revisão F11: ninguém desativa o próprio acesso */
    /* revisão F3: conferência para quem também aponta no app: decidir a duplicidade do próprio apontamento fica com revisão posterior (AL-12) */
    const aponta=Object.values(c.ordens||{}).some(o=>(o.ap||[]).some(a=>g2mesma(a.quem,p.k)))||(!!c.app&&c.app.operador===p.k);
    if(aponta&&dr.indexOf('conferente')>=0) v.cf1_ppv.push({t:'Conferência de quem aponta',v:p.k+' aponta no app: decidir a duplicidade do próprio apontamento fica com revisão posterior (AL-12).',st:'color:#8A5A00;font-weight:700;'});
    const vc=at&&e.papeis.length>0&&!eu; v.cf1_pvc=vc; v.cf1_pvct='Usar o perfil de '+p.k;   /* sem "Ver como" nas telas (proprietário, 14/10) */
    v.cf1_pvcfn=()=>{ G2_PERFIL_MEM=p.k; try{ localStorage.setItem(G2_PERFIL_KEY,p.k); }catch(er){} self.setState({perfil:p.k,g2toast:'Perfil de demonstração: '+((g2pf(p.k)||{}).t||p.k)+' (não é segurança de acesso).'}); };
  } else { v.cf1_paps=[]; v.cf1_ppv=[]; v.cf1_pcad=[]; }
  // ---- painel Alçada ----
  const id=st.cf1_a; const b=id?G2_ALCADAS.find(x=>x.id===id):null; const e16=id==='AL-16';
  aPainel(self,v,'cf1_ap',!!(b||e16),b?b.id+' · '+b.t:(e16?'AL-16 · Aprovar compra de insumos':''),()=>self.setState({cf1_a:null,cf1_err:''}));
  v.cf1_a16=e16; v.cf1_anao16=!!b; v.cf1_a16l=CONF0.compras.map(x=>({t:x.ate?'até '+assinR(x.ate):'acima de '+assinR(CONF0.compras[CONF0.compras.length-2].ate),v:x.quem,st:''}));
  v.cf1_aedit=false; v.cf1_apend=false; v.cf1_asem=false; v.cf1_aprim=false; v.cf1_ades=false; v.cf1_arec=false; v.cf1_aprimtit='';
  if(b){ const a=g2alcDe(K,b.id); const pd=K.pend[b.id]; const falta=cf1Falta(K,b.id);
    v.cf1_adef=[{t:'Comando',v:b.cmd},{t:'Quem decide',v:cf1QuemT(K,a)+(a.acima?' · acima: '+cf1QuemT(K,a.acima):'')},{t:'Valor / limite',v:cf1Lim(a)},
      {t:'Situação',v:pd?'v'+pd.v+' aguarda 2º aprovador':(falta?'Sem titular':'Vigente v'+a.v+' desde '+confBr(cf1Desde(K,b.id))),st:pd?'color:#8A5A00;font-weight:700;':(falta?'color:#B42318;font-weight:700;':'')},
      {t:'Mudança',v:cf1Mud(b)}].concat(b.pend?[{t:'Pendência do proprietário',v:b.pend+' (padrão dos agentes; o proprietário decide)'}]:[]).map(x=>Object.assign({st:''},x));
    v.cf1_aver=[{t:'v1 · '+confBr(CONF0.alc_desde),v:'implantação · '+cf1PapT(G2_ALCADAS.find(x=>x.id===b.id))+(b.lim&&b.id==='AL-05'?' · '+b.lim+' %':'')}].concat(cf1Ev(K,b.id).map(x=>({t:confBr(x.d)+' '+x.at,v:x.t+' · '+x.quem}))).map(x=>Object.assign({st:''},x));
    // ordens afetadas agora, pela mesma função do comando; a ordem de beneficiamento (fam BEN) libera pelo papel de produção, fora da AL-01 (merge CONF × BEN)
    let af=[]; if(b.id==='AL-01') af=Object.values(c.ordens).filter(o=>o.etapa==='A liberar'&&o.fam!=='BEN').map(o=>({t:o.id+' · '+o.talhao,v:o.tipo,h:'OS.dc.html#'+o.id}));
    if(b.id==='AL-05') af=Object.values(c.ordens).filter(o=>o.etapa==='Em execução'&&o.area>0).map(o=>{ const L=cenLimDisp(o.area); return {t:o.id+' · '+cenNum(o.area)+' ha',v:'limite '+L.pct+' % = '+cenNum(L.ha,2)+' ha · saldo '+cenNum(o.saldo)+' ha',h:'OS.dc.html#'+o.id}; });
    if(b.id==='AL-09') af=(c.ajustes||[]).filter(x=>x.estado==='Aguardando gestor').map(x=>({t:(x.inv||x.id)+' · lote '+x.lote,v:cenNum(x.dif)+' '+x.un+' aguardando aprovação',h:'EST.dc.html'}));
    if(b.id==='AL-10') af=(c.confs||[]).filter(x=>x.estado==='Em conferência').map(x=>({t:x.id+' · '+x.os,v:cenConfTxt(x,c),h:'EST.dc.html'}));
    v.cf1_aaf=af; v.cf1_taf=['AL-01','AL-05','AL-09','AL-10'].indexOf(b.id)>=0; v.cf1_aafnada=!af.length; v.cf1_aaft='Ordens e registros afetados agora ('+af.length+')';
    const PFk=confAtor(K,PF); const podeAlt=confPodeA(PFk,g2alcDe(K,'AL-14'));
    if(pd){ v.cf1_apend=true; v.cf1_apendt='v'+pd.v+' proposta por '+pd.por+' em '+confBr(pd.d)+' '+pd.at+': '+confAlcMudT(b,a,pd.mud)+' · motivo: '+pd.motivo+'. Até a confirmação vale a v'+a.v+'.';
      const pode=cf1PodeConf(K,PF,b.id); const pv=pd.v; const FLA=[['g_alc','al_'+b.id]]; v.cf1_aprim=pode; v.cf1_aprimt='Confirmar mudança'; v.cf1_aprimdis=false;
      v.cf1_aprimfn=()=>cf1Run(self,c=>confAlcConfirmar(c,b.id,K1,g2perfil(),pv),{cf1_a:null},FLA);
      v.cf1_apendq=pode?'':(PF&&PF.k===pd.k?'Você propôs: confirma '+confQuemConf(K,pd)+'.':'Confirma ou recusa: '+confQuemConf(K,pd)+'.');
      v.cf1_ades=!!PF&&PF.k===pd.k; v.cf1_adesfn=()=>cf1Run(self,c=>confAlcDesistir(c,b.id,K1,g2perfil(),pv),{cf1_a:null},FLA);
      v.cf1_arec=pode; v.cf1_arecfn=()=>cf1Run(self,c=>confAlcRecusar(c,b.id,K1,g2perfil(),pv),{cf1_a:null},FLA); }
    else if(falta){ v.cf1_asem=true; const cand=cf1Cand(K,falta.papeis,PF); const ptx=falta.papeis.map(x=>(G2_PAPEIS.find(y=>y.k===x)||{}).m||x).join(' e ');
      v.cf1_asemt=b.id+' sem titular: ninguém ativo tem '+ptx+(falta.nivel==='acima'?' (nível acima do limite)':'')+'. '+(cand.length?'Escolha quem recebe o papel.':'Ninguém pode receber agora. '+cf1SemCand(K,falta.papeis,PF));
      const esc=st.cf1_tit&&cand.find(x=>x.p.id===st.cf1_tit)?st.cf1_tit:'';
      v.cf1_acand=cand.map(x=>({t:x.p.k+' · '+x.p.equipe+(x.hab?' · habilidade no CD-04':''),on:String(esc===x.p.id),ti:(esc?esc===x.p.id:x===cand[0])?'0':'-1',go:()=>self.setState({cf1_tit:x.p.id,cf1_err:''})}));
      const pe=esc?confP(esc):null; v.cf1_aprim=gest; v.cf1_aprimt=pe?'Conceder '+ptx+' a '+pe.k:'Conceder '+ptx; v.cf1_aprimdis=!pe;
      v.cf1_aprimtit=pe?'':(cand.length?'Escolha acima quem recebe o papel':'Ninguém pode receber agora: veja o caminho acima');
      v.cf1_aprimfn=()=>{ if(!pe) return; const e2=K.pessoas[pe.id]; cf1Run(self,c=>confPapeis(c,pe.id,e2.papeis.concat(falta.papeis.filter(x=>e2.papeis.indexOf(x)<0)),K1,g2perfil()),{cf1_a:null,cf1_tit:''},[['g_alc','al_'+b.id],['g_pes','pe_'+pe.id]]); };
      v.cf1_asemq=gest?'':'Conceder: decisão de '+confQuemA(K,g2alcDe(K,'AL-13'))+'.'; }
    else if(b.edita){ v.cf1_aedit=true; const cur=a; const mud=st.cf1_mud||{}; let nv=null, erro='';
      try{ nv=Object.keys(mud).length?confAlcNova(b,cur,mud):null; }catch(x){ erro=String(x.message||x); }
      v.cf1_alim=b.edita==='lim'; v.cf1_apap=b.edita!=='lim';
      v.cf1_aopc=(b.opc||[]).map(x=>{ const atual=b.edita==='acima'?cur.acima.papeis.join():cur.papeis.join(); const sel=mud.papel!==undefined?mud.papel:atual;
        return {t:(G2_PAPEIS.find(y=>y.k===x)||{}).t+(x===atual?' (vigente)':''),on:String(sel===x),go:()=>self.setState({cf1_mud:{papel:x},cf1_err:''})}; });
      v.cf1_aoptit=b.edita==='acima'?'Quem aceita o excedente da custódia':'Papel que decide';
      v.cf1_alimv=mud.lim!==undefined?String(mud.lim):String(cur.lim); v.cf1_aset=(ev)=>self.setState({cf1_mud:{lim:ev.target.value},cf1_err:''});
      v.cf1_amot=st.cf1_mot||''; v.cf1_asetm=(ev)=>self.setState({cf1_mot:ev.target.value,cf1_err:''});
      let amplia=false, pv=[]; if(nv){ const n2=Object.assign({},cur,nv); const lv=b.edita==='acima'?'acima':'base';
        const an=cf1Nomes(K,g2alcN(cur,lv)), dp=cf1Nomes(K,g2alcN(n2,lv)); amplia=confAmplia(b,PFk,cur,n2);
        pv=[{t:'Muda',v:confAlcMudT(b,cur,nv)},{t:'Quem ganha',v:dp.filter(x=>an.indexOf(x)<0).join(', ')||'—'},{t:'Quem perde',v:an.filter(x=>dp.indexOf(x)<0).join(', ')||'—'},
          {t:'Quando vale',v:amplia?'aguarda 2º aprovador: amplia o seu poder (outra pessoa com gestor ou direção confirma)':'vale na hora, para os comandos novos',st:amplia?'color:#8A5A00;font-weight:700;':''}];
        if(b.edita==='lim'){ const o=Object.values(c.ordens).filter(x=>x.etapa==='Em execução'&&x.area>0).sort((x,y)=>y.area-x.area)[0];   /* exemplo: a maior ordem em execução */ if(o) pv.push({t:'Exemplo: '+o.id+' ('+cenNum(o.area)+' ha)',v:cenNum(cenQtd(cur.lim/100,o.area),2)+' ha → '+cenNum(cenQtd(n2.lim/100,o.area),2)+' ha'}); } }
      v.cf1_apv=pv.map(x=>Object.assign({st:''},x)); v.cf1_tapv=pv.length>0; v.cf1_aerrm=erro; v.cf1_taerrm=!!erro;
      v.cf1_aprim=podeAlt; v.cf1_aprimt=amplia?'Enviar para confirmação':'Salvar alçada'; v.cf1_aprimdis=!nv||String(st.cf1_mot||'').trim().length<3;
      const mud0=Object.assign({},mud), mot0=st.cf1_mot||'', v0=cur.v; v.cf1_aprimfn=()=>cf1Run(self,c=>confAlcMudar(c,b.id,mud0,mot0,K1,g2perfil(),v0),{cf1_a:null,cf1_mud:null,cf1_mot:''},[['g_alc','al_'+b.id]]);
      v.cf1_aeditq=podeAlt?'':'Alterar alçada: decisão de '+confQuemA(K,g2alcDe(K,'AL-14'))+'.'; }
    v.cf1_temq=!!(v.cf1_apendq||v.cf1_asemq||v.cf1_aeditq); v.cf1_aq=v.cf1_apendq||v.cf1_asemq||v.cf1_aeditq||'';
  } else { v.cf1_adef=[]; v.cf1_aver=[]; v.cf1_aaf=[]; v.cf1_acand=[]; v.cf1_aopc=[]; v.cf1_apv=[]; v.cf1_temq=false; }
}
'''


def _lin(lista):
    return (f'<div><sc-for list="{H(lista)}" as="ln" hint-placeholder-count="3"><div class="conf-lin"><span>{H("ln.t")}</span><span style="{H("ln.st")}">{H("ln.v")}</span></div></sc-for></div>')


def _sc(var, html, ph='false'):
    return f'<sc-if value="{H(var)}" hint-placeholder-val="{H(ph)}">{html}</sc-if>'


def _alerta():
    return _sc('cf1_terr', f'<div role="alert" style="padding: 9px 12px; border-radius: 10px; background: {REDS}; color: {RED}; font-size: 13px; font-weight: 700; line-height: 1.4;">{H("cf1_err")}</div>')


def cf01():
    fname = 'CF-01.dc.html'; E._reset_screen(fname)
    ui37.CAT['CF-01'] = dict(ui37.CAT.get('CF-01', {}), titulo='Usuários e alçadas')
    g_pes = grid([dict(k='nome', l='Pessoa', w=220), dict(k='pap', l='Papéis', w=220, multi=True), dict(k='dec', l='Decide (alçadas)', w=230),
                  dict(k='acs', l='Acesso', w=220, multi=True)], [], gid='g_pes', search=True, total=False, so={'k': 'acs'},
                 qf=dict(k='acs', cut=' · ', todas='Todas as pessoas'), edit=dict(m='ro', title='Pessoa', fields=[]))
    g_alc = grid([dict(k='alc', l='Alçada', w=280), dict(k='quem', l='Quem decide', w=260), dict(k='lim', l='Valor / limite', w=230),
                  dict(k='sit', l='Situação', w=200), dict(k='mud', l='Mudança', w=220, multi=True)], [], gid='g_alc', search=True, total=False,
                 so={'k': 'alc'}, qf=dict(k='mud', sep=', ', todas='Todas as alçadas'), edit=dict(m='ro', title='Alçada', fields=[]))
    nota = lambda t: f'<div class="conf-nota" style="padding: 0 0 10px;">{t}</div>'
    corpo = ('<div style="display: flex; flex-direction: column; gap: 18px;">' + CF1_CSS
             + section('Pessoas', 'Conceda e retire papéis, convide e desative acesso; clique na pessoa para abrir.', '',
                       g_pes)
             + section('Alçadas', 'Confira quem decide cada comando; clique na alçada para ver as versões, as ordens afetadas e mudar o que é editável.', '',
                       g_alc)
             + '</div>')
    # painel Convidar (lista curta)
    cvl = (f'<div style="display: flex; flex-direction: column; gap: 8px;"><sc-for list="{H("cf1_cvl")}" as="cv" hint-placeholder-count="1">'
           f'<button type="button" class="conf-esc" onClick="{H("cv.go")}">{H("cv.t")}</button></sc-for></div>'
           + _sc('cf1_cvnada', f'<div class="conf-nota">Todas as pessoas do cadastro têm acesso.</div>')
           + f'<div class="conf-nota">Escolha a pessoa: o painel dela tem o convite (simulado, aceito na hora; nenhuma mensagem real é enviada). Pessoa nova se cadastra no CD-04.</div>')
    E.EXTRA.append(painel('cf1_cvp', cvl, '', 460, foco=True))
    # painel Pessoa
    corpo_p = (f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">{chip_dyn("cf1_pac")}<a href="{H("cf1_pcadh")}" style="font-size: 12.5px; font-weight: 700; color: {ACC};">Abrir no cadastro</a></div>'
               + _lin('cf1_pcad') + titulo('Papéis (permissão de decidir)')
               + f'<div role="group" aria-label="Papéis" class="conf-paps"><sc-for list="{H("cf1_paps")}" as="pp" hint-placeholder-count="7">'
               f'<button type="button" role="switch" class="conf-sw" aria-checked="{H("pp.on")}" disabled="{H("pp.dis")}" title="{H("pp.tit")}" onClick="{H("pp.go")}">'
               f'<span class="conf-swt">{H("pp.t")}</span><span class="conf-sws">{H("pp.s")}</span></button></sc-for></div>'
               + _sc('cf1_ptpv', titulo('Prévia') + _lin('cf1_ppv'))
               + _sc('cf1_temnota', f'<div class="conf-nota">{H("cf1_pnota")}</div>') + _alerta())
    rod_p = (f'<div style="display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};">'
             + _sc('cf1_pvc', f'<button type="button" onClick="{H("cf1_pvcfn")}" style="{SEC}">{H("cf1_pvct")}</button>')
             + _sc('cf1_pdes', f'<button type="button" onClick="{H("cf1_pdesfn")}" style="{SEC}">Desativar acesso</button>')
             + f'<button type="button" class="conf-prim" disabled="{H("cf1_ppdis")}" onClick="{H("cf1_ppfn")}" style="{PRI}">{H("cf1_ppt")}</button></div>')
    E.EXTRA.append(painel('cf1_pp', corpo_p, rod_p, 520, foco=True))
    # painel Alçada
    corpo_a = (_sc('cf1_a16', titulo('Níveis da Compra de insumos (dados2.ALCADA)') + _lin('cf1_a16l')
                   + '<div class="conf-nota">Só leitura: a Compra de insumos aplica estes níveis. Editar ou ligar a papéis é da frente Suprimentos (CONF-D23).</div>'
                   + f'<div><a href="CMP.dc.html" style="font-size: 13px; font-weight: 700; color: {ACC};">Abrir Compra de insumos</a></div>')
               + _sc('cf1_anao16', titulo('Definição') + _lin('cf1_adef')
                     + _sc('cf1_apend', f'<div role="note" style="padding: 10px 12px; border-radius: 12px; background: {YELS}; color: {YEL}; font-size: 13px; font-weight: 700; line-height: 1.4;">{H("cf1_apendt")}</div>')
                     + _sc('cf1_asem', f'<div role="note" style="padding: 10px 12px; border-radius: 12px; background: {REDS}; color: {RED}; font-size: 13px; font-weight: 700; line-height: 1.4;">{H("cf1_asemt")}</div>'
                           + f'<div role="radiogroup" aria-label="Quem recebe o papel" onKeyDown="{H("cf1_setas")}" style="display: flex; flex-direction: column; gap: 8px;"><sc-for list="{H("cf1_acand")}" as="cd" hint-placeholder-count="3">'
                           f'<button type="button" role="radio" class="conf-esc" aria-checked="{H("cd.on")}" tabIndex="{H("cd.ti")}" onClick="{H("cd.go")}">{H("cd.t")}</button></sc-for></div>')
                     + _sc('cf1_aedit', titulo('Mudar') + _sc('cf1_apap', f'<div style="font-size: 12px; font-weight: 700; color: {MUTED};">{H("cf1_aoptit")}</div>'
                           + f'<div role="radiogroup" aria-label="{H("cf1_aoptit")}" onKeyDown="{H("cf1_setas")}" style="display: flex; flex-wrap: wrap; gap: 8px;"><sc-for list="{H("cf1_aopc")}" as="op" hint-placeholder-count="3">'
                           f'<button type="button" role="radio" class="conf-esc" aria-checked="{H("op.on")}" tabIndex="{H("op.ti")}" onClick="{H("op.go")}">{H("op.t")}</button></sc-for></div>')
                           + _sc('cf1_alim', f'<label for="cf1_lim" style="font-size: 12px; font-weight: 700; color: {MUTED};">Limite (% da área da ordem)</label>'
                                 f'<div style="display: flex; align-items: center; gap: 8px;"><input id="cf1_lim" type="text" inputMode="numeric" value="{H("cf1_alimv")}" onChange="{H("cf1_aset")}" '
                                 f'style="width: 110px; font-family: inherit; font-size: 14px; padding: 9px 11px; border-radius: 10px; border: 1px solid {LINE}; box-sizing: border-box;"><span style="font-size: 13px; color: {MUTED};">%</span></div>')
                           + f'<label for="cf1_mot" style="font-size: 12px; font-weight: 700; color: {MUTED};">Motivo (obrigatório)</label>'
                           f'<textarea id="cf1_mot" value="{H("cf1_amot")}" onChange="{H("cf1_asetm")}" style="font-family: inherit; font-size: 13.5px; padding: 9px 11px; border-radius: 10px; border: 1px solid {LINE}; min-height: 56px; resize: vertical;"></textarea>'
                           + _sc('cf1_taerrm', f'<span role="alert" style="font-size: 12.5px; font-weight: 700; color: {RED};">{H("cf1_aerrm")}</span>')
                           + _sc('cf1_tapv', titulo('Prévia') + _lin('cf1_apv')))
                     + _sc('cf1_taf', titulo(H('cf1_aaft')) + f'<div><sc-for list="{H("cf1_aaf")}" as="af" hint-placeholder-count="3"><div class="conf-lin"><span><a href="{H("af.h")}" style="color: {ACC}; font-weight: 700;">{H("af.t")}</a></span><span>{H("af.v")}</span></div></sc-for></div>'
                           + _sc('cf1_aafnada', '<div class="conf-nota">Nada afetado agora.</div>'))
                     + titulo('Versões') + _lin('cf1_aver')
                     + _sc('cf1_temq', f'<div class="conf-nota" style="font-weight: 700;">{H("cf1_aq")}</div>') + _alerta()))
    rod_a = (f'<div style="display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};">'
             + _sc('cf1_ades', f'<button type="button" onClick="{H("cf1_adesfn")}" style="{SEC}">Desistir da mudança</button>')
             + _sc('cf1_arec', f'<button type="button" onClick="{H("cf1_arecfn")}" style="{SEC}">Recusar mudança</button>')
             + _sc('cf1_aprim', f'<button type="button" class="conf-prim" disabled="{H("cf1_aprimdis")}" title="{H("cf1_aprimtit")}" onClick="{H("cf1_aprimfn")}" style="{PRI}">{H("cf1_aprimt")}</button>') + '</div>')
    E.EXTRA.append(painel('cf1_ap', corpo_a, rod_a, 540, foco=True))
    EXTRAJS[0] = cenario.js_prefixo() + A_JS + CF1_JS
    HEIGHTS37[fname] = 1500
    shell37('CF-01', 'Usuários e alçadas', corpo, fname=fname, search=False,
            subtitle='Quem entra e quem decide cada comando. Pessoas vêm do cadastro; papéis e alçadas valem para o próximo comando, na hora.',
            primary_html=f'<button type="button" class="conf-prim" disabled="{H("cf1_prim_dis")}" title="{H("cf1_prim_lab")}" onClick="{H("cf1_prim_fn")}" style="{BTN_ST(True)}">{H("cf1_prim_t")}</button>',
            footer='O perfil de demonstração mostra a experiência e não é segurança: no software o servidor tira o ator da sessão. '
                   'Pessoas vêm de Cadastros › Pessoas e equipes (nome, função, habilidade e CREA); aqui não se cadastra pessoa. Papel é permissão de decidir; quem tem acesso sem papel só usa o app de campo. '
                   'Os comandos da O.S., do Estoque e do app leem a tabela de alçadas; mudança vale para o próximo comando e nunca reescreve registro antigo.')
    injeta(fname, 'Usuários e alçadas', chip_dyn('cf1_st'))

# ===================================== CF-03 · Integrações (CONF-01 §3.3) =====================================
# O que entra e sai, de onde, e se está em dia. Só demonstração: nenhuma conexão real e nenhuma credencial (ENG-017); o selo nunca some.
# A fila do ERP são os movimentos do cenário que mudam o físico, enviados uma vez por conteúdo; o estornado depois de enviado volta uma vez (R17).
CF3_JS = r'''
// ---- CF-03 · Integrações (simuladas): conexões, fila do ERP lida de c.movs, sincronização idempotente (confSincronizar) ----
function cf3Ult(x){ return x.ult?confBr(x.ult.slice(0,10))+' '+x.ult.slice(11):'—'; }
function PREVALS(self,v){ cenOuvir(self); const c=cenGet(); const X=confConexoes(c); self._cf3={c,X};
  aGrid('g_con').rows=X.map(x=>({id:'cx_'+x.id,dr:'cf3_cx_'+x.id,v:{con:x.t,tl:x.traz,est:x.estado,ult:x.ult?x.ult.slice(0,10):'',pend:x.pend,cred:'Não configurada'},
    s:{con:x.t,tl:'traz: '+x.traz+' · leva: '+x.leva,est:x.estado,pend:(x.pend?'Com pendência':'Sem pendência')+' · '+x.pend,cred:'Não configurada · cofre do ambiente'},
    p:{con:[{k:'b',t:x.t},{k:'mut',t:'Demonstração'}],tl:[{k:'txt',t:'traz: '+x.traz},{k:'mut',t:'leva: '+x.leva}],est:[aCh(x.estado,x.cor)],ult:[{k:x.ult?'txt':'mut',t:x.id==='app'?'pelo sinal do aparelho (simulado)':cf3Ult(x)}],
      pend:x.pend?[{k:'b',t:String(x.pend)},{k:'mut',t:'abra a linha'}]:[{k:'mut',t:'0'}],cred:[{k:'mut',t:'Não configurada · em produção, no cofre do ambiente'}]}})); }
function EXTRAVALS(self,v){ const {c,X}=self._cf3; const st=self.state; const PF=g2perfil(); const erp=X.find(x=>x.id==='erp');
  aSelo(self,v,'cf3_st','Demonstração · nenhuma conexão real','yellow');
  v.cf3_res='Fila do ERP: '+erp.pend+(erp.pend===1?' movimento':' movimentos')+' · app de campo: '+X.find(x=>x.id==='app').estado+' · nenhuma credencial existe nesta demonstração';
  const ch=self.__cf3k||(self.__cf3k=confChave('sinc')); const rid=(self.__cf3n=(self.__cf3n||0)+1);   /* nº deste desenho (CONF-D51) */
  v.cf3_prim_fn=(e)=>{ const u=self.__cf3u; const k1=confRepJanela(u,e,rid)?u.k:ch;   /* duplo clique: o 2º clique repete o mesmo pedido (revisão CONF 13/10) */
    const r=cenMudar(null,k=>confSincronizar(k,k1,g2perfil()));   /* chave do desenho: clique repetido = mesma sincronização (R12) */ if(r.erro){ self.setState({g2toast:r.erro}); return; } if(r.repetido) return;
    self.__cf3u={k:k1,r:rid}; self.__cf3k=confChave('sinc'); self.setState(Object.assign({cenrev:Date.now(),g2toast:r.msg},confFl(self,[['g_con','cx_erp']]))); };
  X.forEach(x=>{ v['cf3_cx_'+x.id]=()=>self.setState({cf3_c:x.id}); });
  const x=st.cf3_c?X.find(y=>y.id===st.cf3_c):null; const K=confLer(c);
  aPainel(self,v,'cf3_cp',!!x,x?x.t:'',()=>self.setState({cf3_c:null}));
  if(x){ aSelo(self,v,'cf3_cest',x.estado,x.cor);
    v.cf3_cl=[{t:'Traz',v:x.traz},{t:'Leva',v:x.leva},{t:'Quem escreve cada objeto',v:x.escritor},{t:'Onde se usa',v:x.onde},
      {t:'Ambiente',v:'Demonstração (dados sintéticos) · homologação e produção só com autorização do proprietário'},
      {t:'Credencial',v:'Não configurada · em produção fica no cofre do ambiente e só aparece mascarada (••••••••)'},
      {t:'Última sincronização',v:x.id==='app'?x.estado:cf3Ult(x)}].map(y=>Object.assign({st:''},y));
    const fila=x.id==='erp'?confErpFila(c):[];
    v.cf3_cpend=x.id==='erp'?fila.map(y=>({t:y.m.id,v:confErpT(y).replace(y.m.id+' · ',''),h:y.m.os?'OS.dc.html#'+y.m.os:'EST.dc.html'}))
      :(x.id==='app'&&x.pend?[{t:x.pend+(x.pend>1?' duplicidades':' duplicidade'),v:'decide a conferência na O.S. (CMD-09)',h:'OS.dc.html'}]:[]);
    v.cf3_tpend=v.cf3_cpend.length>0; v.cf3_npend=!v.cf3_cpend.length;
    v.cf3_csin=(K.ev||[]).filter(e=>e.tipo==='sinc').slice(-5).reverse().map(e=>({t:confBr(e.d)+' '+e.at,v:e.t+' · '+e.quem,st:''}));
    v.cf3_tsin=v.cf3_csin.length>0; v.cf3_nsin=!v.cf3_csin.length; }
  else { v.cf3_cl=[]; v.cf3_cpend=[]; v.cf3_csin=[]; } }
'''


def cf03():
    fname = 'CF-03.dc.html'; E._reset_screen(fname)
    ui37.CAT['CF-03'] = dict(ui37.CAT.get('CF-03', {}), titulo='Integrações')
    g_con = grid([dict(k='con', l='Conexão', w=200), dict(k='tl', l='Traz / leva', w=320), dict(k='est', l='Estado', w=190), dict(k='ult', l='Última sincronização', t='date', w=170),
                  dict(k='pend', l='Pendências', t='num', a='r', w=120), dict(k='cred', l='Credencial', w=200)], [], gid='g_con', search=True, total=False, so={'k': 'con'},
                 qf=dict(k='pend', cut=' · ', todas='Todas'), edit=dict(m='ro', title='Conexão', fields=[]))
    corpo = ('<div style="display: flex; flex-direction: column; gap: 18px;">' + CF1_CSS
             + section('Conexões', 'Confira o que entra e sai e se está em dia; clique na conexão para ver quem escreve cada objeto e as pendências.', '',
                       f'<div class="conf-nota" style="padding: 0 0 10px; font-weight: 700; color: {INK};">{H("cf3_res")}</div>' + g_con)
             + '</div>')
    corpo_c = (f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">{chip_dyn("cf3_cest")}<span class="conf-nota">Demonstração · nenhuma conexão real</span></div>'
               + _lin('cf3_cl') + titulo('Pendências')
               + _sc('cf3_tpend', f'<div><sc-for list="{H("cf3_cpend")}" as="pd" hint-placeholder-count="2"><div class="conf-lin"><span><a href="{H("pd.h")}" style="color: {ACC}; font-weight: 700;">{H("pd.t")}</a></span><span>{H("pd.v")}</span></div></sc-for></div>')
               + _sc('cf3_npend', '<div class="conf-nota">Nada pendente.</div>')
               + titulo('Sincronizações recentes') + _sc('cf3_tsin', _lin('cf3_csin')) + _sc('cf3_nsin', '<div class="conf-nota">Nenhuma sincronização nesta demonstração ainda.</div>'))
    E.EXTRA.append(painel('cf3_cp', corpo_c, '', 520, foco=True))
    EXTRAJS[0] = cenario.js_prefixo() + A_JS + CF3_JS
    HEIGHTS37[fname] = 900
    shell37('CF-03', 'Integrações', corpo, fname=fname, search=False,
            subtitle='O que entra e sai, de onde e se está em dia. Só demonstração: nenhuma conexão real e nenhuma credencial.',
            primary_html=f'<button type="button" class="conf-prim" onClick="{H("cf3_prim_fn")}" style="{BTN_ST(True)}">Sincronizar agora (simulado)</button>',
            footer='Homologação, produção e credenciais reais só com autorização e custo aprovados pelo proprietário (AGENTS §2; ENG-017). '
                   'Sincronizar envia ao ERP cada movimento uma vez por conteúdo: repetir não reenvia; um consumo estornado depois de enviado volta uma vez, como estorno. O app de campo envia pelo próprio aparelho quando há sinal.')
    injeta(fname, 'Integrações', chip_dyn('cf3_st'))

# ===================================== CF-04 · Auditoria (CONF-01 §3.2) =====================================
# Quem fez o quê, quando e com que efeito: confTrilha lê os registros que os comandos já gravam (nada é digitado; nenhum autor é inferido).
# Uma ação: Baixar trilha (CSV) com as linhas filtradas; a exportação vira registro (R15). Detalhe = painel só leitura da linha.
CF4_JS = r'''
// ---- CF-04 · Auditoria: trilha única (confTrilha) com filtros de pessoa, comando e mês; CSV das linhas filtradas ----
const CF4_MES=['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
function cf4Mes(d){ const a=String(d).split('-'); return CF4_MES[Number(a[1])-1]+'/'+a[0]; }
function PREVALS(self,v){ cenOuvir(self); assinOuvir(self); const L=confTrilha(cenGet(),assinLer()); self._cf4={L};
  const EST4=g2estreito();   /* estreito (390 px): só a 1ª coluna fica presa; Quem vai junto de Quando (revisão CONF 13/10, §3.2) */
  const pos={}; L.forEach((r,i)=>{ pos[r.seq]=i; });   /* revisão F1: a coluna Quando ordena pela ordem da trilha (data, gravação, hora), não só pela data */
  aGrid('g_tr').rows=L.slice().reverse().map(r=>{ const q=r.quem||'autor não registrado'; const k=r.quem?r.k:'autor não registrado'; const qd=confBr(r.d)+(r.at?' '+r.at:'');
    return {id:'tr_'+r.uid,dr:'cf4_tr_'+r.seq,v:{qd:r.d+'#'+String(pos[r.seq]).padStart(6,'0'),quem:q,oq:r.oq,obj:r.obj,ef:r.ef,ori:r.origem},s:{qd:cf4Mes(r.d)+' · '+qd,quem:q,oq:r.oq,obj:r.obj,ef:r.ef,ori:r.origem},
      p:{qd:EST4?[{k:'txt',t:qd},{k:'br'},{k:'mut',t:q}]:[{k:'txt',t:qd}],quem:r.quem?[{k:'b',t:q}]:[aCh('autor não registrado','gray')],oq:[{k:'txt',t:r.oq}],obj:r.h?[{k:'link',t:r.obj,h:r.h}]:[{k:'txt',t:r.obj}],ef:[{k:'txt',t:r.ef}],ori:[{k:'mut',t:r.origem}]},
      m:{quem:[{id:k,l:k}],qd:[{id:cf4Mes(r.d),l:cf4Mes(r.d)}]},seq:r.seq}; }); }   /* id da linha = uid (estável); seq só nomeia o gatilho desta pintura */
function EXTRAVALS(self,v){ const L=self._cf4.L; const st=self.state; const PF=g2perfil();
  const vis=new Set((v.g_tr_rows||[]).map(x=>x.id)); const F=L.filter(r=>vis.has('tr_'+r.uid)).reverse();   /* as linhas que a grade mostra, mais recente primeiro */
  const aut=new Set(F.map(r=>r.quem?r.k:'—')); const autAll=new Set(L.map(r=>r.quem?r.k:'—'));
  v.cf4_res=F.length+(F.length===1?' registro':' registros')+(F.length<L.length?' de '+L.length:'')+' · '+aut.size+(aut.size===1?' autor':' autores')+' · lidos dos comandos gravados; nada é digitado aqui';
  L.forEach(r=>{ v['cf4_tr_'+r.seq]=()=>self.setState({cf4_d:r.uid}); });   /* detalhe só leitura da linha, pelo uid: outra aba que grave não troca o registro aberto (revisão CONF 10/10) */
  const g=st.g2&&st.g2.g_tr||{}; const fil=[(g.q||'').trim()?'texto "'+g.q.trim()+'"':'',g.qv?'mês '+g.qv:''].concat(Object.keys(g.f||{}).filter(k=>(g.f[k]||[]).length).map(k=>({quem:'pessoa',oq:'comando',qd:'mês',ori:'origem',obj:'objeto',ef:'efeito'}[k]||k)+': '+g.f[k].join(', '))).filter(Boolean).join(' · ');
  v.cf4_prim_dis=!F.length; v.cf4_prim_tit=F.length?'Baixa as '+F.length+' linhas filtradas em CSV; a exportação fica na trilha':'Nenhum registro para baixar';
  const ch=self.__cf4k||(self.__cf4k=confChave('exp')); const rid=(self.__cf4n=(self.__cf4n||0)+1);   /* nº deste desenho (CONF-D51) */   /* chave do desenho: clique repetido = mesma exportação (R12) */
  v.cf4_prim_fn=(e)=>{ if(!F.length) return; const csv=confCsv(F); const u=self.__cf4u; const rep=confRepJanela(u,e,rid); const n=rep?u.n:F.length; const fx=rep?u.fil:(fil||'sem filtros'); const k1=rep?u.k:ch;
    /* duplo clique: o 2º clique repete o mesmo pedido (mesma chave, mesmo n e filtros) e recebe o mesmo recibo, sem 2º arquivo (revisão CONF 13/10) */
    const r=cenMudar(null,c=>confExportar(c,n,fx,k1,g2perfil())); if(r.erro){ self.setState({g2toast:r.erro}); return; }
    if(r.repetido) return;   /* revisão F16: o 2º clique do mesmo desenho devolve o mesmo recibo e não baixa outro arquivo */
    self.__cf4u={k:k1,n,fil:fx,r:rid}; self.__cf4k=confChave('exp'); try{ window.__confCsv=csv; window.__confCsvN=(window.__confCsvN||0)+1; }catch(e){}
    try{ const b=new Blob(['﻿'+csv],{type:'text/csv;charset=utf-8'}); const a=document.createElement('a'); a.href=URL.createObjectURL(b); a.download='trilha-auditoria-'+CONF0.hoje+'.csv';
      document.body.appendChild(a); a.click(); setTimeout(()=>{ try{ URL.revokeObjectURL(a.href); a.remove(); }catch(e){} },500); }catch(e){}
    const nr=confTrilha(cenGet(),assinLer()).find(x=>x.src===(r.recibo||{}).id); self.setState(Object.assign({cenrev:Date.now(),g2toast:r.msg},nr?confFl(self,[['g_tr','tr_'+nr.uid]]):{})); };
  const d=st.cf4_d?L.find(r=>r.uid===st.cf4_d):null;
  aPainel(self,v,'cf4_dp',!!d,d?d.oq:'',()=>self.setState({cf4_d:null}));
  v.cf4_dl=d?[{t:'Quando',v:confBr(d.d)+(d.at?' '+d.at:'')},{t:'De onde vem a data',v:d.ds},{t:'Quem',v:d.quem||'autor não registrado'},{t:'O quê',v:d.oq},{t:'Objeto',v:d.obj},
    {t:'Antes → depois / efeito',v:d.ef},{t:'Origem',v:d.origem},{t:'Registro de origem',v:d.src||'—'}].map(x=>Object.assign({st:''},x)):[];
  v.cf4_dh=d&&d.h?d.h:'#'; v.cf4_temh=!!(d&&d.h); }
'''


def cf04():
    fname = 'CF-04.dc.html'; E._reset_screen(fname)
    ui37.CAT['CF-04'] = dict(ui37.CAT.get('CF-04', {}), titulo='Auditoria')
    g_tr = grid([dict(k='qd', l='Quando', t='date', w=150, multi=True), dict(k='quem', l='Quem', w=170, multi=True), dict(k='oq', l='O quê', w=230),
                 dict(k='obj', l='Objeto', w=170), dict(k='ef', l='Antes → depois / efeito', w=360), dict(k='ori', l='Origem', w=120)], [], gid='g_tr', search=True,
                total=False, so={'k': 'qd', 'd': True}, qf=dict(k='qd', cut=' · ', todas='Todos', l='mês'), edit=dict(m='ro', title='Registro', fields=[]))
    corpo = ('<div style="display: flex; flex-direction: column; gap: 18px;">' + CF1_CSS
             + section('Trilha de auditoria', 'Filtre por pessoa, comando ou mês; clique no registro para ver a origem. A trilha não se edita.', '',
                       f'<div class="conf-nota" role="status" style="padding: 0 0 10px; font-weight: 700; color: {INK};">{H("cf4_res")}</div>' + g_tr)
             + '</div>')
    corpo_d = (_lin('cf4_dl') + f'<div class="conf-nota">A trilha não se edita: corrija no domínio, por ajuste ou estorno vinculado.</div>')
    rod_d = (f'<div style="display: flex; justify-content: flex-end; gap: 8px; padding-top: 6px; border-top: 1px solid {LINE};">'
             + _sc('cf4_temh', f'<a href="{H("cf4_dh")}" style="text-decoration: none; {SEC}">Abrir no domínio</a>') + '</div>')
    E.EXTRA.append(painel('cf4_dp', corpo_d, rod_d, 500, foco=True))
    EXTRAJS[0] = cenario.js_prefixo() + A_JS + CF4_JS
    HEIGHTS37[fname] = 1100
    shell37('CF-04', 'Auditoria', corpo, fname=fname, search=False,
            subtitle='Quem fez o quê, quando e com que efeito: a trilha lê os registros que os comandos gravam. Nada é digitado aqui.',
            primary_html=f'<button type="button" class="conf-prim" disabled="{H("cf4_prim_dis")}" title="{H("cf4_prim_tit")}" onClick="{H("cf4_prim_fn")}" style="{BTN_ST(True)}">Baixar trilha (CSV)</button>',
            footer='Datas: a do registro; registro do cenário só com hora usa a data operacional da demonstração (26/09/2026); a assinatura usa a data simulada da cobrança.')

def build():
    cf01()
    cf03()
    cf04()
