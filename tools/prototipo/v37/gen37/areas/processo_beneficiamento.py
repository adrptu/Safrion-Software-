# -*- coding: utf-8 -*-
"""Agrícola › Beneficiamento (BEN.dc.html; cartão próprio desde 13/10/2026, BEN-D39) · BEN-1 packing de mamão (docs/beneficiamento/ESPECIFICACAO.md v2; adaptações em
docs/beneficiamento/DECISOES.md §12). Uma tela de trabalho: as ordens de processo (Lista e Kanban de 5 fases) e o painel da ordem com
o próximo passo, uma ação primária por estado, balanço, saídas, entradas, caixas, etapas, recursos e histórico.
Planejar (nova ordem, autorizar rota e liberar), executar (iniciar, registrar e estornar saídas, concluir) e controlar (justificar,
conferir, fechar) ficam na ordem; a decisão do lote (resultado, liberar, bloquear, reclassificar, destinar) e a reserva ficam no
Estoque de produto (PROD), o mesmo lugar dos lotes da Colheita: sem segundo estoque de produto e sem segunda reserva.
Regras, contas e comandos: ben.js (ben*), sobre producao.js e cenario.js; esta área só monta a tela. Quem age vem do perfil (g2perfil).
A casca, o painel, os cartões do celular e o restaurar são os da Produção (areas/producao.py); o Kanban é o da O.S. (mesmo componente)."""
from engine import (grid, esc, INK, MUTED, LINE, BG, SURF, ACC, BTN_ST, EXTRAJS, _MINI)
import engine as E
from areas.producao import (bloco, cartoes, _shell, _js, IF, H)
from areas.processo_os import _kanban


def build():
    fname = 'BEN.dc.html'; E._reset_screen(fname)
    g_ob = grid([dict(k='id', l='Ordem', w=150), dict(k='prod', l='Produto', w=200), dict(k='fase', l='Fase', w=140), dict(k='cond', l='Condição', w=200, multi=True),
                 dict(k='ep', l='Em processo', t='num', a='r', w=130), dict(k='nx', l='Próximo passo', w=230), dict(k='quem', l='Quem resolve', w=200)],
                [], edit=dict(m='pick'), gid='g_ob', total=False, qf=dict(k='fase', l='Fase', todas='Todas'),
                cartoes=False)   # Lista | Kanban próprios: o Kanban já cumpre o papel dos cartões (15/10/2026)
    EXTRAJS[0] = _js(BEN_JS)
    vis = (f'<div class="pr-vis" role="group" aria-label="Visão das ordens"><button type="button" aria-pressed="{H("vl_on")}" onClick="{H("vl_go")}">Lista</button>'
           f'<button type="button" aria-pressed="{H("vk_on")}" onClick="{H("vk_go")}">Kanban</button></div>')
    nova = f'<button type="button" onClick="{H("nova_go")}" style="{_MINI}">Criar ordem</button>'
    kb = (f'<style>@media (max-width:479px){{.bn-kb>div{{flex-direction:column!important}}.bn-kb>div>div{{width:100%!important}}}}</style>'
          f'<div class="bn-kb" style="overflow-x: auto;">{_kanban()}</div>')
    # o aviso (role=status) segue o posicionamento único do g2lib (g2toastLugar, UX-BEN35-AVISO-01); a regra local da rodada 3 (I-g4), que o
    # mandava ao topo com o painel aberto e cobria o cabeçalho do painel, saiu
    corpo = (bloco('Ordens de beneficiamento', 'Da matéria-prima recebida ao produto beneficiado: entradas, saídas pesadas, embalagens e balanço na mesma ordem. Clique numa ordem para o próximo passo.',
                   IF('vl', g_ob + cartoes('cards_ob'), d=True) + IF('vk', kb), acao=f'<div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">{vis}{nova}</div>'))
    _shell('BEN', 'Beneficiamento', 'Processe as ordens: autorize a rota, registre as saídas pesadas, confira o balanço e feche. Fechar não libera o lote: a Qualidade libera.',
           corpo, fname, 1100,
           'Massa pesada não se cria; embalagem não é produto; correção é estorno com motivo. Os lotes embalados vão para o Estoque de produto em inspeção (R-A07, R-C01, R-A15, R-E01).')


BEN_JS = r'''
/* ===== Beneficiamento · tela (BEN.dc.html): monta a tela e chama os comandos de ben.js em benMudar (recibo repetido não grava) ===== */
const PR_GRIDS={g_ob:1};
const _g2rows0=g2rows; g2rows=function(self,sp){ return PR_GRIDS[sp.id]?sp.rows:_g2rows0(self,sp); };
const BN_FCOR={'A liberar':'gray','Liberadas':'blue','Em execução':'green','Em conferência':'yellow','Encerradas':'gray','Canceladas':'gray'};
/* repetição do toque (rodada 1 da integração, S3): o 2º toque de um toque duplo cai no botão que o 1º fez aparecer (Autorizar → Iniciar;
   Criar ordem → Autorizar). Até BN_REP_MS depois de uma ação do painel, ou com o contador de cliques do navegador em 2 ou mais, o toque é
   absorvido: o aviso repete o recibo do 1º toque e nada roda. Dano evitado: iniciar o processo (ou liberar a ordem) sem a pessoa decidir */
const BN_REP_MS=400;
function bnAgora(){ return typeof performance!=='undefined'&&performance.now?performance.now():Date.now(); }
function bnGuarda(self,fn,mudo){ return (e)=>{ const u=self._bnUlt||null; const t=bnAgora();
  if((e&&e.detail>=2)||(u&&t-u.t<BN_REP_MS)){ if(u&&u.msg&&!mudo) self.setState({g2toast:/^Já feito/.test(u.msg)?u.msg:'Já feito: '+u.msg,pr_err:''}); return; }
  self._bnUlt={t,msg:''}; return fn(e); }; }
function bnRun(self,fn,ok){ const r=benMudar(fn); self._bnUlt={t:bnAgora(),msg:r.erro?(/^Já feito/.test(r.erro)?r.erro:''):(r.msg||'')};
  /* toque repetido (duplo toque, outra aba): o efeito já existe; o retorno é aviso, não erro, e não apaga o aviso do primeiro toque */
  if(r.erro&&/^Já feito/.test(r.erro)){ self.setState({g2toast:r.erro,pr_err:''}); return r; }
  if(r.erro){ self.setState({pr_err:r.erro,g2toast:''}); return r; }
  self.setState(Object.assign({cenrev:Date.now(),g2toast:r.msg||'Registrado.',pr_err:'',pr_ferr:null,bn_rasc:null},ok||{})); bnFocoTitulo(); return r; }
/* depois de um comando que muda a fase ou fecha um formulário, o foco vai ao título do painel (tabindex −1, não acionável): o Enter seguinte
   não aciona a primária nova (rodada 3, I-g2: "Autorizar" virava "Iniciar processo" no mesmo botão, a um Enter) */
function bnFocoTitulo(){ setTimeout(()=>{ try{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); const h=a&&a.querySelector('h2');
  if(h){ h.setAttribute('tabindex','-1'); h.focus({preventScroll:true}); } }catch(e){} },0); }
/* tecla segurada (auto-repetição, e.repeat) não aciona botão no BEN: o clique do Enter sai a cada keydown repetido (rodada 3, I-g1). Só em botão:
   num campo de texto, segurar o Espaço é digitação */
function bnRepete(){ if(window.__bnRep) return; window.__bnRep=1; try{ window.addEventListener('keydown',(e)=>{ if(!e.repeat||(e.key!=='Enter'&&e.key!==' ')) return;
  const t=e.target; if(t&&t.closest&&t.closest('button,[role=button]')){ e.preventDefault(); e.stopPropagation(); } },true); }catch(e){} }
/* rascunho (rodada 3, I-h1): Esc, o X, o fundo e o Voltar com campo digitado não descartam; o aviso "Rascunho não salvo" oferece Continuar
   editando ou Descartar, e um 2º Esc com o aviso à vista descarta. Só campo digitado conta (número ou texto): escolher por toque não pede
   confirmação. Reabrir o rascunho preenchido é vetado (seria "último valor" de quantidade e bruto, AGENTS §3.3) */
const BN_DIG=/^(cx|br|kg|tk|mo|tj|mc|qx|mr|mt|cx_\d+)$/;
function bnSujo(self){ const F=self.state.pr_form||{}; return Object.keys(F).some(k=>BN_DIG.test(k)&&String(F[k]==null?'':F[k]).trim()!==''); }
/* o aviso vale para o rascunho de quando apareceu: digitar de novo o tira (a pessoa voltou a editar) */
function bnRascOn(self){ const r=self.state.bn_rasc; return !!r&&r.f===JSON.stringify(self.state.pr_form||{})&&bnSujo(self); }
function bnRasc(self,m){ self.setState({bn_rasc:{m,f:JSON.stringify(self.state.pr_form||{})}}); }
function bnVolta(self,fn){ return ()=>{ if(bnSujo(self)&&!bnRascOn(self)){ bnRasc(self,'voltar'); return; } self.setState({bn_rasc:null}); fn(); }; }
/* condição dos ativos: a da Manutenção, que vive no cenário único (c.man, PCM 1a); a chave antiga 'talhao-os-manutencao-v1' não é mais gravada.
   Integração COMP (PCM × BEN): lida da chave antiga, a ordem mostrava a condição da semente ("Apto") com a linha bloqueada na Manutenção */
function bnMan(){ try{ const c=cenGet(); return c&&c.man||null; }catch(e){ return null; } }
function bnProdTxt(o){ const r=benRota(o.ben.rota); return r?r.ent.split(' · ')[0]:''; }
function bnQtdTxt(o){ const e=benKg(benEntrada(o)); return o.etapa==='A liberar'||o.etapa==='Liberadas'||o.etapa==='Canceladas'?'entrada '+e:(o.etapa==='Em execução'?'em processo '+benKg(benEmProc(o))+' de '+e:'processado '+e); }
function bnRow(c,o){ const r=benRota(o.ben.rota); const nx=benProx(c,o); const ss=benSelos(c,o); const ep=benEmProc(o); const pr=bnProdTxt(o);
  return {id:o.id,ro:true,m:{cond:ss.map(s=>({id:s.t,l:s.t}))},v:{id:o.id,prod:pr,fase:o.etapa,cond:ss.map(s=>s.t).join(' | '),ep,nx:nx.t,quem:nx.quem||''},
    s:{id:o.id,prod:pr,fase:o.etapa,cond:ss.map(s=>s.t).join(' | '),ep:benKg(ep),nx:nx.t,quem:nx.quem||''},
    p:{id:[{k:'b',t:o.id}],prod:[{k:'txt',t:pr}],   /* uma variável por coluna (R-G04): rota, local e janela ficam no painel e no cartão do Kanban */
       fase:[{k:'chip',t:o.etapa,c:BN_FCOR[o.etapa]||'gray'}],cond:ss.length?ss.map(s=>({k:'chip',t:s.t,c:s.c})):[{k:'mut',t:'—'}],
       ep:[{k:prCmp(ep,0)>0?'b':'mut',t:benKg(ep)}],nx:[{k:'txt',t:nx.t}],quem:[{k:'mut',t:nx.quem||'—'}]}}; }
/* Kanban: o mesmo componente da O.S. (5 fases; condição é selo, nunca coluna) */
function bnKanban(self,c,ords){ return BEN_FASES.map(f=>{ const os=ords.filter(o=>o.etapa===f); const kg=prSoma(os.map(o=>benEntrada(o)));
  return {t:f,n:String(os.length),nst:prChs(os.length?'gray':'gray'),carga:os.length?benKg(kg)+' de entrada':'',vazio:!os.length,
    cards:os.map(o=>{ const nx=benProx(c,o); const cur=(self.state.pr_sel||{}).id===o.id;
      return {lab:o.id+' · '+o.etapa,open:()=>self.g2pick('g_ob',o.id),key:(e)=>{ if(e&&(e.key==='Enter'||e.key===' ')){ e.preventDefault(); self.g2pick('g_ob',o.id); } },
        st:'display:flex;flex-direction:column;gap:5px;padding:10px;border-radius:10px;background:#FFFFFF;cursor:pointer;border:1px solid '+(cur?'#1E7A4C':'#E4E9E5')+';',
        id:o.id,tipo:bnProdTxt(o)+' · '+benRotaTxt(benRota(o.ben.rota)),local:o.talhao+' · '+prBr(o.ben.ini)+'–'+prBr(o.ben.fim),hasBar:false,bar:'',
        hasReal:true,real:bnQtdTxt(o).replace(/^./,x=>x.toUpperCase()),selos:benSelos(c,o).map(s=>({t:s.t,st:prChs(s.c),dot:prDot(s.c)})),
        hasObs:false,obs:'',hasDp:true,dp:nx.t,meta:nx.quem||''}; })}; }); }
function PREVALS(self,v){ cenOuvir(self); prTopo(self,v); const c=cenGet(); self._c=c;
  self.g2pick=(gid,rid)=>(self._bnUlt={t:bnAgora(),msg:''},self.setState({pr_sel:{g:gid,id:rid},pr_pan:{g:gid,id:rid},pr_form:null,pr_err:'',pr_ferr:null,pr_modo:null,pr_ch:null,bn_sub:null,bn_rasc:null}));
  const ords=benOrdens(c).filter(o=>prFazOk(self,o.ben.faz)); self._ords=ords;
  const ord=o=>(BEN_FASES.indexOf(o.etapa)+1||BEN_FASES.length+1)*1000+Number(o.id.replace(/\D/g,''));   /* Canceladas (fora do quadro, BEN-D22) por último */
  GR('g_ob').rows=ords.slice().sort((a,b)=>ord(a)-ord(b)).map(o=>bnRow(c,o)); }
/* ---------- formulários do painel ---------- */
function bnFldOpts(self,k,l,opts,h,multi,def){ const val=prFval(self,k,def||''); const sel=multi?val.split(',').filter(Boolean):[val];
  return {id:'pf_'+k,l,isTxt:false,isOpts:true,isSel:false,v:val,u:'',im:'',ph:'',hasH:!!h,h:h||'',hasE:false,e:'',st:'',set:()=>{},
    opts:opts.map(x=>{ const on=sel.indexOf(x.v)>=0; return {t:x.t,v:x.v,on:String(on),st:prPill(on),go:()=>{ let nv=x.v; if(multi){ const a=sel.filter(y=>y!==x.v); if(!on) a.push(x.v); nv=a.join(','); } prFset(self,k,nv); }}; })}; }
function bnNovaForm(self,c,pre){ const aptos=benLotesAptos(c).filter(L=>prFazOk(self,L.faz)); const P=prP(c);
  const def=pre&&aptos.some(L=>L.id===pre)?pre:''; const sel=prFval(self,'lt',def).split(',').filter(x=>P.lotes[x]);
  const fs=[bnFldOpts(self,'lt','Lotes de entrada',aptos.map(L=>({v:L.id,t:L.id+' · '+benKg(prFis(c,L.id))+' · '+((PRDC.locais[L.local]||{}).nome||L.local)+' · '+L.faz})),
    aptos.length?'Só lotes elegíveis: recebidos ou liberados, fora de outra ordem e sem reserva. A ordem leva o lote inteiro (o saldo ao lado).':'Nenhum lote elegível sem ordem: os lotes em inspeção, bloqueados ou já numa ordem não entram.',true)];
  /* lote inteiro (BEN-D17): a quantidade é o saldo físico do lote, sem campo a digitar */
  let tot=0, ok=true; const ents=sel.map(id=>{ const fis=prFis(c,id); if(prCmp(fis,0)>0) tot=prSoma([tot,fis]); else ok=false; return {lote:id,kg:fis}; });
  const prods=sel.map(id=>P.lotes[id].prod).filter((x,i,a)=>a.indexOf(x)===i); const ks=prods.length===1?benRotasPara(prods[0]):[]; let rk='';
  if(ks.length>1){ fs.push(bnFldOpts(self,'rota','Rota',ks.map(k=>({v:k,t:benRotaTxt(benRota(k))})),'Versões aprovadas para '+prods[0]+'.')); rk=prFval(self,'rota',''); } else rk=ks[0]||'';
  const r=benRota(rk); const pad=r&&ok?benCaixasPadrao(c,tot,r):{sug:0,livre:0,cx:0}; const sug=pad.sug;
  /* valor inicial: a necessidade da rota (benCaixasPadrao, BEN-D23), nunca reduzida ao livre; acima do livre o aviso vem antes do toque,
     com a saída (nota a conferir e quem confere): a ordem nasce e a liberação fica impedida até o Estoque receber as caixas */
  if(r){ const vx=prNum(prFval(self,'cx_'+sug,String(pad.cx)));
    const ac=Number.isInteger(vx)&&vx>pad.livre?' Acima das '+benUn(pad.livre)+' livres no Estoque: a liberação fica impedida até o Estoque receber as caixas ('+benCaixasVem(c)+').':'';
    fs.push(prFld(self,'cx_'+sug,'Caixas',{t:'txt',im:'numeric',v:String(pad.cx),u:'un',h:'Sugestão: ⌈'+benKg(tot)+' × '+prFmtT(prMul(r.par.frac_vend,100),2)+' % previstos ÷ '+prFmtT(BENC.cx.massa,3)+' kg por caixa⌉ = '+sug+' un ('+benRotaTxt(r)+', sintético).'+ac+' Confirme ou ajuste: '+BENC.cx.item+'.'})); }
  const hj=prHoje(), am=prDiaMais(prHoje(),1); fs.push(bnFldOpts(self,'ini','Início',[{v:hj,t:'Hoje '+prBr(hj)},{v:am,t:'Amanhã '+prBr(am)}],'Janela de 2 dias a partir do início.',false,hj));
  const rotaTxt=r?('Rota: '+benRotaTxt(r)+' (única versão aprovada para '+r.ent+': '+r.aprov.quem+', '+prBr(r.aprov.em)+'). '):'';
  const go=()=>{ if(!(self.state.pr_pan&&self.state.pr_pan.g==='nova')) return;   /* toque num formulário já fechado (duplo toque): nada a fazer, o aviso do 1º fica */
    if(!sel.length){ self.setState({pr_err:'Escolha ao menos um lote de entrada.'}); return; } const cx=prFval(self,'cx_'+sug,String(pad.cx));
    const rr=bnRun(self,x=>benNova(x,{lotes:ents,rota:rk,cx:prNumOk(cx)?prNum(cx):cx,ini:prFval(self,'ini',hj),chave:self.state.pr_ch||prChave('W-BNN')},g2perfil()),{pr_form:null,pr_ch:null,pr_pan:null});
    /* a ordem criada fica selecionada e aberta, com o próximo passo dela (rodada 1, S3): antes o painel fechava e o cabeçalho apontava outra ordem */
    if(!rr.erro&&rr.id) self.setState({pr_sel:{g:'g_ob',id:rr.id},pr_pan:{g:'g_ob',id:rr.id},pr_modo:null,bn_sub:null}); };
  return {title:'Nova ordem de beneficiamento',chip:['Rascunho','gray'],sub:'Entradas recebidas na Colheita (fruta de campo em processo); a rota vem do produto e do estágio.',
    form:{t:'Nova ordem · '+benProdQ(),h:rotaTxt+'Criar não reserva nada: as entradas e as caixas são reservadas na liberação.',fields:fs},err:self.state.pr_err,prim:{t:'Criar ordem',go}}; }
function bnSaidaForm(self,c,o){ const r=benRota(o.ben.rota); const conf=o.etapa==='Em conferência'; const sub=self.state.bn_sub||null;   /* sub: relançar o registro estornado (fluxo, classe e destino herdados) */
  const f0=sub?sub.fluxo:(conf?'Perda identificada':''); const fl=prFval(self,'fl',f0); const def=r.saidas.find(s=>s.fluxo===fl)||null; const fs=[];
  fs.push(bnFldOpts(self,'fl','Fluxo',(conf&&!sub?r.saidas.filter(s=>s.fluxo==='Perda identificada'):r.saidas).map(s=>({v:s.fluxo,t:s.fluxo})),
    conf?(sub?'Relança '+sub.id+' (estornado) com os dados certos.':'Em conferência entra só perda identificada pesada; outra saída substitui um registro estornado.'):'Produto vai para o lote da classe; outro destino e descarte saem do vendável; perda só com pesagem.'));
  let prev='';
  if(def&&def.fluxo==='Produto'){ fs.push(bnFldOpts(self,'cl','Classe',def.classes.map(x=>({v:x,t:x})),'')); fs.push(prFld(self,'cx','Caixas',{t:'txt',im:'numeric',u:'un'})); fs.push(prFld(self,'br','Bruto sem pallet',{t:'txt',u:'kg',h:'Caixas cheias pesadas antes da paletização ('+benRotaTxt(r)+').'}));
    const cx=prNum(prFval(self,'cx','')), br=prNum(prFval(self,'br',''));
    if(Number.isInteger(cx)&&cx>0&&isFinite(br)&&br>0){ const t=benTara(cx,0,r); const l=prSub(br,t); prev='Tara '+cx+' × '+prFmtT(BENC.cx.tara,3)+' kg = '+benKg(t)+' (cadastro da caixa); líquido '+benKg(l)+(prCmp(l,0)>0?' = '+prFmtT(prDiv(l,cx),3)+' kg por caixa de '+prFmtT(BENC.cx.massa,3)+' kg':'')+'.'; } }
  else if(def&&def.fluxo==='Perda identificada'){ fs.push(bnFldOpts(self,'ca','Causa',def.causas.map(x=>({v:x,t:x})),'')); fs.push(prFld(self,'kg','Peso pesado',{t:'txt',u:'kg'}));
    fs.push(prFld(self,'tk','Ticket da balança',{t:'txt',im:'text',ph:'ex.: TK-5560',h:'Balança e hora: '+r.par.balanca+', agora. Sem pesagem não é perda identificada.'})); }
  else if(def){ fs.push(bnFldOpts(self,'de','Destino',def.destinos.map(x=>({v:x,t:x})),'')); fs.push(prFld(self,'kg','Peso',{t:'txt',u:'kg'})); }
  if(conf) fs.push(prFld(self,'mo','Motivo da correção',{t:'txt',im:'text',ph:'ex.: perda pesada na esteira'}));
  const T=benCxTot(c,o);
  const go=()=>{ if(self.state.pr_modo!=='saida') return;   /* formulário já fechado pelo 1º toque */
    const k={fluxo:fl,classe:prFval(self,'cl',''),destino:prFval(self,'de',''),causa:prFval(self,'ca',''),cx:prFval(self,'cx',''),bruto:prFval(self,'br',''),kg:prFval(self,'kg',''),
      ticket:prFval(self,'tk',''),motivo:prFval(self,'mo',''),subst:sub?sub.id:'',chave:self.state.pr_ch||prChave('W-BNS'),ver:self.state.bn_ver};
    ['cx','bruto','kg'].forEach(x=>{ if(prNumOk(k[x])) k[x]=prNum(k[x]); });
    bnRun(self,x=>benSaida(x,o.id,k,g2perfil()),{pr_form:null,pr_ch:null,pr_modo:null,bn_sub:null,bn_ver:null}); };
  return {fields:fs,go,h:(prev?prev+' ':'')+(T.n?'Caixas em custódia: '+benCustTxt(c,o)+'.':'')}; }
/* ---------- painel da ordem ---------- */
function bnPainel(self,c,o){ const r=benRota(o.ben.rota); const b=benBal(o); const nx=benProx(c,o); const modo=self.state.pr_modo||''; const it=benReqItem(c,o); const at=o.etapa;
  const verAgora=()=>self.setState({bn_ver:o.ver});
  const sec=[], secs=[];
  /* impedimentos (A liberar): todas as causas juntas, cada uma com dono e atalho que só navega */
  if(at==='A liberar'){ const im=benImpedimentos(c,o);
    secs.push({t:'Impedimentos da liberação',rows:im.map(x=>({c:[[x.t,'red'],x.dono?'resolve: '+x.dono:'',x.link?x.link.why:''].filter(Boolean),
      a:x.ret?{t:'Retirar '+x.lote+' da ordem',go:()=>bnRun(self,y=>benRetirar(y,o.id,x.lote,g2perfil(),{ver:o.ver,chave:'W-BNR-'+o.id+'-v'+o.ver+'-'+x.lote}),{})}:null,l:x.link?{t:x.link.t,h:x.link.h}:null})),vazio:'Nenhum: a ordem pode ser autorizada e liberada.'}); }
  /* balanço (R-F01, R-F02; §7): nunca editável; razão sempre sobre o processado. Antes do Iniciar não há diferença nem recuperação;
     em execução, o que falta registrar é "em processo" e a diferença só é apurada no Concluir (um alarme antes disso seria falso) */
  const nIni=at==='A liberar'||at==='Liberadas'; const ep=benEmProc(o); const aberto=prCmp(ep,0)>0;
  const bal=[{c:[[nIni?'Entrada a processar':(aberto?'Entrada':'Entrada processada'),'b'],benKg(b.proc),o.ben.ent.length+(o.ben.ent.length>1?' lotes':' lote')]}];
  if(nIni) bal.push({c:[['Diferença e recuperação','b'],['apuradas com as saídas pesadas, depois do Iniciar','mut']]});
  else {
  Object.keys(b.cls).sort().forEach(k=>bal.push({c:[['Produto '+k,'b'],benKg(b.cls[k]),benPct(b.pp(b.cls[k]))]}));
  if(prCmp(b.outro,0)>0) bal.push({c:[['Outro destino','b'],benKg(b.outro),benPct(b.pp(b.outro))]});
  if(prCmp(b.desc,0)>0) bal.push({c:[['Descarte','b'],benKg(b.desc),benPct(b.pp(b.desc))]});
  if(prCmp(b.perda,0)>0) bal.push({c:[['Perdas identificadas','b'],benKg(b.perda),benPct(b.pp(b.perda))]});
  const dentro=b.dentro, jok=benJustOk(o,b);
  if(aberto){ bal.push({c:[['Em processo','b'],benKg(ep),'ainda não registrado: no envio para conferência vira diferença']}); bal.push({c:[['Diferença','b'],['apurada no envio para conferência','mut']]}); }
  else bal.push({c:[['Diferença','b'],[benKg(b.dif)+' ('+benPct(b.pct)+')',dentro||jok?'ok':'red'],'faixa ± '+benKg(b.faixa)+' ('+prFmtT(prMul(r.par.tol_pesado,100),2)+' % · '+benRotaTxt(r)+', sintético)',
    dentro?(b.ganho?'ganho aparente dentro da faixa':'dentro da faixa'):(jok?'justificada':(b.ganho?'ganho aparente acima da faixa':'acima da faixa'))]});
  bal.push({c:[['Recuperação comercial','b'],benPct(b.rec)+(aberto?' até agora':''),'prevista '+prFmtT(prMul(r.par.frac_vend,100),2)+' % (sintético)'+(o.ben.conc&&prCmp(b.rec,prMul(r.par.frac_vend,100))<0?' · abaixo da prevista (aviso)':'')]}); }
  (o.ben.just||[]).filter(j=>!j.caida).forEach(j=>bal.push({c:[['Diferença justificada','b'],benKg(j.dif),j.motivo+': '+j.texto,j.quem]}));
  if(o.ben.corr) bal.push({c:[['Corrigido na conferência','b'],benKg(o.ben.corr.antes)+' → '+benKg(o.ben.corr.depois),o.ben.corr.motivo,o.ben.corr.pend?['aguarda '+benQuem('gestor'),'red']:('confirmado por '+((o.ben.corr.conf||{}).quem||''))]});
  if(o.ben.conf) bal.push({c:[['Conferido','b'],o.ben.conf.quem,prBr(o.ben.conf.em.slice(0,10))+' '+o.ben.conf.em.slice(11)]});
  secs.push({t:'Balanço de massa',rows:bal});
  /* saídas, descartes e perdas: o estornado fica riscado, nunca some */
  const podeEst=at==='Em execução'||at==='Em conferência';
  secs.push({t:'Saídas, descartes e perdas',rows:(o.ben.sai||[]).map(s=>({c:[[s.id,'b'],s.fluxo+(s.classe?' '+s.classe:'')+(s.destino?' · '+s.destino:'')+(s.causa?' · '+s.causa:''),s.lote||'',
      benKg(s.kg),s.cx?s.cx+' cx · bruto '+benKg(s.bruto)+' − tara '+benKg(s.tara):'',(s.ev.ticket?'ticket '+s.ev.ticket+' · ':'')+'pesado '+s.at+' · '+String(s.quem).split(' ')[0]+(s.subst?' · substitui '+s.subst:''),
      s.estorno?['Estornado: '+s.estorno.motivo+' ('+String(s.estorno.quem).split(' ')[0]+')','red']:['Válido','ok']].filter(Boolean),
      a:(podeEst&&!s.estorno)?{t:'Estornar '+s.id,go:()=>self.setState({pr_modo:'estorno:'+s.id,pr_form:null,pr_err:'',pr_ch:prChave('W-BNE'),bn_ver:o.ver})}:null})),vazio:'Nenhum registro ainda.'});
  /* entradas */
  secs.push({t:'Entradas',rows:o.ben.ent.map(e=>{ const L=prP(c).lotes[e.lote]; const S=L?prSaldos(c,L):null;
    return {c:[[e.lote,'b'],benKg(e.kg),L?L.prod.split(' · ')[1]||'':'',S?(S.esgotado?'esgotado':S.q):'',L&&L.faz!=='Santa Rita'?L.faz:''].filter(Boolean),l:{t:'Ver no Estoque de produto',h:'PROD.dc.html#'+e.lote}}; })});
  /* caixas (requisição): lida da REQ */
  /* uma linha por requisição e lote (BEN-REV-20261009-03): o complemento em outro lote aparece com a REQ e o lote dele */
  const LC=benLinhas(c,o);
  if(LC.length) secs.push({t:'Caixas · '+LC.map(x=>x.rid).join(' e '),rows:LC.map(x=>({c:[[LC.length>1?x.rid+' · '+x.it.lote:x.it.prod,'b'],'solicitado '+benUn(x.it.solicitado),'entregue '+benUn(x.it.entregue),'usado '+benUn(x.it.consumido),['em custódia '+benUn(x.it.custodia),x.it.custodia>1e-9&&at==='Em conferência'?'red':''],'devolvido '+benUn(x.it.devolvido)],l:{t:'Abrir no Estoque',h:'EST.dc.html'}}))});
  else if((o.ins||[]).length) secs.push({t:'Caixas',rows:[{c:[[o.ins[0].p,'b'],benUn(o.ins[0].tot)+' a reservar na liberação','sugestão '+o.ben.cxSug+' un']}]});
  /* etapas da rota (a mesma função da trava do Fechar) */
  /* etapa pendente só é alerta (vermelho) quando já impede o Fechar, na conferência; antes disso é o que falta fazer */
  secs.push({t:'Etapas · '+benRotaTxt(r),rows:benEtapas(c,o).map(e=>({c:[[e.nome,'b'],e.pert,[e.sit,e.sit==='Cumprida'?'ok':(e.sit==='Pendente'&&at==='Em conferência'?'red':'mut')],e.ev]}))});
  /* recursos: condição do ativo lida da Manutenção (só exibição no BEN-1) e horas pela capacidade */
  const hr=benHoras(o); const ca=benCondAtivo(bnMan(),(r.ativos||[])[0]);
  if(hr) secs.push({t:'Recursos',rows:[{c:[[hr.ativo.nome,'b'],[ca.t+' na Manutenção',ca.k==='ok'?'ok':'red'],prFmtT(hr.ativo.kgh,0)+' kg/h',prFmt(hr.h,2)+' h de linha','equipe '+hr.equipe+' · '+prFmt(hr.hh,2)+' HH','estimado pela capacidade'].concat(ca.msg?[ca.msg]:[]),l:ca.k==='ok'?null:{t:'Ver na Manutenção',h:'MA.dc.html#ativo='+(r.ativos||[])[0]}}]});   /* tela única da Manutenção (PCM): o ativo, não a MA-01 */
  /* lotes gerados (Encerradas) */
  if(at==='Encerradas'){ const I=o.ben.insp&&benB(c).insp[o.ben.insp]; const ls=Object.values(prP(c).lotes).filter(L=>L.benef===o.id);
    secs.unshift({t:'Lotes gerados',rows:ls.map(L=>{ const S=prSaldos(c,L); return {c:[[L.id,'b'],L.prod.split(' · ')[1]+' '+L.classe,benKg(S.fis)+' · '+(L.cx||0)+' cx',[S.esgotado?'esgotado':S.q,S.q==='Liberado'?'ok':''],I?I.id+' · prazo '+prBr(I.prazo)+' · '+I.resp:''],l:{t:'Abrir no Estoque de produto',h:'PROD.dc.html#'+L.id}}; })}); }
  secs.push({t:'Histórico',rows:(o.ben.hist||[]).slice().reverse().map(h=>({c:[[prBr(h.d)+' '+h.at,'b'],h.quem,h.ev,h.det,h.mov||''].filter(Boolean)}))});
  const kv=[{l:'Unidade',v:benUnidTxt(o)},{l:'Rota',v:benRotaTxt(r)+' · aprovada por '+r.aprov.quem+' em '+prBr(r.aprov.em)},{l:'Versão da ordem',v:o.versao},{l:'Entrada',v:benKg(b.proc)},{l:'Diferença',v:(nIni||aberto?'apurada no envio para conferência':benKg(b.dif))+' · faixa ± '+benKg(b.faixa)},
    {l:'Caixas em custódia',v:it?benCustTxt(c,o):'—'},{l:'Responsável',v:benProdQ()}];
  /* quem age é o perfil (CTL-3): se o perfil escolhido não registra o passo, o painel diz quem registra antes do toque */
  const PAP={liberar:'producao',iniciar:'producao',saida:'producao',concluir:'producao',confirmar:'gestor',conferir:'conferente',fechar:'producao',
    justificar:benAlcada(o,b.dif).passa?'gestor':['producao','gestor']}[nx.acao]; const pf=g2perfil();
  const semPapel=PAP&&!(Array.isArray(PAP)?g2umPapel(pf,PAP):g2papel(pf,PAP)) ? ' Seu perfil ('+pf.k+') não registra este passo: escolha '+(Array.isArray(PAP)?g2quemUm(PAP):g2quem(PAP))+' no seletor de perfil.' : '';
  const lc=PRDC.locais[o.ben.local]||{}; const onde=lc.faz&&lc.faz!==o.ben.faz?o.talhao+' ('+lc.faz+') · fruta da '+o.ben.faz:o.talhao+' · '+o.ben.faz;   /* BEN-D18: onde a linha roda e de quem é a fruta */
  const PPx={title:o.id+' · '+bnProdTxt(o)+' · '+benRotaTxt(r),chip:[at,BN_FCOR[at]||'gray'],sub:onde+' · janela '+prBr(o.ben.ini)+'–'+prBr(o.ben.fim)+' · '+benProdQ(),
    next:nx.t+(nx.quem?' · '+nx.quem:'')+(nx.nota?'. '+nx.nota:'')+semPapel,nred:!!nx.red||!!semPapel,kv,secs,err:self.state.pr_err,sec};
  /* cancelada (BEN-D22): só consulta; o motivo fica no próximo passo, e as entradas (livres para outra ordem) e o histórico seguem à vista */
  if(at==='Canceladas'){ const k0=o.ben.canc||{}; const tot=(o.ins||[]).reduce((a,x)=>a+(x.tot||0),0);
    PPx.kv=[{l:'Unidade',v:benUnidTxt(o)},{l:'Rota',v:benRotaTxt(r)},{l:'Versão da ordem',v:o.versao},{l:'Entrada',v:benKg(b.proc)+' · não processada'},{l:'Caixas',v:tot?benUn(tot)+' · não reservadas':'—'},
      {l:'Cancelada por',v:(k0.quem||'—')+(k0.em?' · '+prBr(k0.em.slice(0,10))+' '+k0.em.slice(11):'')}];
    PPx.secs=secs.filter(s=>s.t==='Entradas'||s.t==='Histórico'); return PPx; }
  /* modos do painel: formulário de saída, estorno, justificativa, reabertura */
  if(modo==='saida'){ const f=bnSaidaForm(self,c,o); PPx.form={t:(self.state.bn_sub?'Relançar '+self.state.bn_sub.id:'Registrar saída')+' · '+benProdQ(),h:f.h,fields:f.fields}; PPx.prim={t:'Registrar',go:f.go}; return PPx; }
  if(modo.indexOf('estorno:')===0){ const sid=modo.slice(8); const s=o.ben.sai.find(x=>x.id===sid)||{};
    PPx.form={t:'Estornar '+sid+' · '+benProdQ(),h:'O registro fica riscado com o motivo; '+(s.cx?benUn(s.cx)+' de caixa voltam à custódia; ':'')+'em seguida abre o relançamento com os mesmos fluxo, classe e destino (cancele se não houver).',
      fields:[bnFldOpts(self,'me','Motivo',BEN_MOT_EST.map(x=>({v:x,t:x})),'')].concat(prFval(self,'me','')==='Outro'?[prFld(self,'mt','Descreva',{t:'txt',im:'text'})]:[])};
    PPx.prim={t:'Confirmar estorno de '+sid,go:()=>{ if(self.state.pr_modo!==modo) return; const r1=bnRun(self,x=>benEstornar(x,o.id,sid,prFval(self,'me',''),prFval(self,'mt',''),g2perfil(),{chave:self.state.pr_ch,ver:self.state.bn_ver}),{pr_form:null,pr_ch:null});
      if(!r1.erro&&!r1.nada) self.setState({pr_modo:'saida',bn_sub:{id:sid,fluxo:s.fluxo},pr_form:{fl:s.fluxo,cl:s.classe||'',de:s.destino||'',ca:s.causa||''},pr_ch:prChave('W-BNS'),bn_ver:(benO(cenGet(),o.id)||{}).ver}); }};
    PPx.sec=[{t:'Manter registro',go:bnVolta(self,()=>self.setState({pr_modo:null,pr_err:''}))}]; PPx.closeHide=true; return PPx; }
  if(modo==='just'){ const al=benAlcada(o,b.dif);
    PPx.form={t:'Justificar diferença',h:'Diferença '+benKg(b.dif)+' ('+benPct(b.pct)+') fora da faixa de '+benKg(b.faixa)+'. Alçada do responsável de produção: '+benKg(al.lim)+' ('+prFmtT(r.par.alcada_pct,2)+' % do processado, teto '+prFmtT(r.par.alcada_kg,0)+' kg; vale o menor)'+(al.passa?': '+al.msg+', decide '+benQuem('gestor')+'.':'.'),
      fields:[bnFldOpts(self,'mj','Motivo',BEN_MOT_JUST.map(x=>({v:x,t:x})),''),prFld(self,'tj','Justificativa',{t:'txt',im:'text',ph:'ex.: fruta mole retirada sem pesar'})]};
    PPx.prim={t:'Justificar diferença',go:()=>self.state.pr_modo==='just'&&bnRun(self,x=>benJustificar(x,o.id,prFval(self,'mj',''),prFval(self,'tj',''),g2perfil(),{chave:self.state.pr_ch,ver:self.state.bn_ver}),{pr_form:null,pr_ch:null,pr_modo:null})};
    PPx.sec=[{t:'Voltar',go:bnVolta(self,()=>self.setState({pr_modo:null,pr_err:''}))}]; PPx.closeHide=true; return PPx; }
  if(modo==='cancelar'){ const ls=o.ben.ent.map(e=>e.lote).join(', ');
    PPx.form={t:'Cancelar a '+o.id+' · '+benProdQ(),h:'A ordem ainda não foi liberada: nada foi reservado. Ela sai do quadro para Canceladas, com o motivo no histórico, e '+ls+(o.ben.ent.length>1?' voltam':' volta')+' a abrir ordem.',
      fields:[prFld(self,'mc','Motivo',{t:'txt',im:'text',ph:'ex.: caixas insuficientes no Estoque'})]};
    PPx.prim={t:'Confirmar cancelamento da '+o.id,go:()=>self.state.pr_modo==='cancelar'&&bnRun(self,x=>benCancelar(x,o.id,prFval(self,'mc',''),g2perfil(),{chave:self.state.pr_ch,ver:self.state.bn_ver}),{pr_form:null,pr_ch:null,pr_modo:null})};
    PPx.sec=[{t:'Voltar',go:bnVolta(self,()=>self.setState({pr_modo:null,pr_err:''}))}]; PPx.closeHide=true; return PPx; }
  /* pedir mais caixas (rodada 1, S3): complemento da ordem. A sugestão é a falta pelo planejado (benFaltaCx: caixas da rota ainda não usadas,
     até o teto do kg aberto, menos custódia e a entregar; rodada 3, C-1); sem falta o campo vem vazio e a estimativa pelo kg é só texto */
  if(modo==='caixas'){ const TC=benCxTot(c,o); const cu=TC.cust, pe=TC.pend; const ne=benCaixas(ep,r); const fx=benFaltaCx(c,o); const sx=fx>0?String(fx):'';
    PPx.form={t:'Pedir mais caixas · '+benProdQ(),h:'Complemento da '+o.req+': o Estoque reserva'+(it?' no '+it.lote:'')+' e entrega no balcão; as caixas viram custódia da ordem. Sem caixa livre bastante nesse lote, o pedido usa os outros lotes, uma requisição por lote (a devolução volta a cada lote). Em custódia '+benUn(cu)+' · a entregar '+benUn(pe)+'. '
      +(fx>0?'Faltam '+benUn(fx)+' pelo planejado (caixas da rota ainda não usadas, até o teto de '+benKg(benKgAberto(o))+' a registrar).':'Sugestão: nada falta pelo planejado. Estimativa pelo kg em processo, só como referência: ⌈'+benKg(ep)+' × '+prFmtT(prMul(r.par.frac_vend,100),2)+' % ÷ '+prFmtT(BENC.cx.massa,3)+' kg⌉ = '+ne+' un.')+' Confirme ou ajuste.',
      fields:[prFld(self,'qx','Caixas',{t:'txt',im:'numeric',v:sx,u:'un'})]};
    PPx.prim={t:'Pedir caixas',go:()=>self.state.pr_modo==='caixas'&&bnRun(self,x=>benComplementar(x,o.id,prNum(prFval(self,'qx',sx)),g2perfil(),{chave:self.state.pr_ch,ver:self.state.bn_ver}),{pr_form:null,pr_ch:null,pr_modo:null})};
    PPx.sec=[{t:'Voltar',go:bnVolta(self,()=>self.setState({pr_modo:null,pr_err:''}))}]; PPx.closeHide=true; return PPx; }
  if(modo==='reabrir'){ PPx.form={t:'Reabrir execução · '+benProdQ(),h:'Volta a Em execução: a declaração do envio para conferência, a conferência e a justificativa caem. Para corrigir um registro, estorne na conferência.',fields:[prFld(self,'mr','Motivo',{t:'txt',im:'text',ph:'ex.: faltou registrar a classe B do turno da tarde'})]};
    PPx.prim={t:'Reabrir execução',go:()=>self.state.pr_modo==='reabrir'&&bnRun(self,x=>benReabrir(x,o.id,prFval(self,'mr',''),g2perfil()),{pr_form:null,pr_modo:null})}; PPx.sec=[{t:'Voltar',go:bnVolta(self,()=>self.setState({pr_modo:null,pr_err:''}))}]; PPx.closeHide=true; return PPx; }
  /* recusa de um comando sem formulário aberto (autorizar, concluir, conferir, fechar): a causa fica no painel, junto da ação */
  if(self.state.pr_err&&!modo) PPx.form={t:'Não gravado',h:'Nada foi alterado. Resolva a causa e toque de novo.',fields:[],aviso:true};   /* aviso, não formulário: o rodapé fecha com "Fechar" */
  /* uma ação primária por estado (§5.3); secundárias à esquerda */
  const abreSaida=()=>self.setState({pr_modo:'saida',pr_form:null,pr_err:'',pr_ch:prChave('W-BNS'),bn_sub:null,bn_ver:o.ver});
  const k={ver:o.ver};
  if(nx.acao==='liberar') PPx.prim={t:'Autorizar rota e liberar',go:()=>bnRun(self,x=>benAutorizarLiberar(x,o.id,g2perfil(),k),{})};
  else if(nx.acao==='iniciar') PPx.prim={t:'Iniciar processo',go:()=>bnRun(self,x=>benIniciar(x,o.id,g2perfil(),k),{})};
  else if(nx.acao==='saida') PPx.prim={t:'Registrar saída',go:abreSaida};
  else if(nx.acao==='concluir'){ PPx.prim={t:'Enviar para conferência',go:()=>bnRun(self,x=>benConcluir(x,o.id,g2perfil(),k),{})}; sec.push({t:'+ Registrar saída',go:abreSaida}); }
  else if(nx.acao==='justificar'){ PPx.prim={t:'Justificar diferença',go:()=>self.setState({pr_modo:'just',pr_form:null,pr_err:'',pr_ch:prChave('W-BNJ'),bn_ver:o.ver})}; }
  else if(nx.acao==='confirmar') PPx.prim={t:'Confirmar correção',go:()=>bnRun(self,x=>benConfirmarCorrecao(x,o.id,g2perfil()),{})};
  else if(nx.acao==='conferir') PPx.prim={t:'Conferir balanço',go:()=>bnRun(self,x=>benConferir(x,o.id,g2perfil(),k),{})};
  else if(nx.acao==='fechar') PPx.prim={t:'Fechar processo',go:()=>bnRun(self,x=>benFechar(x,o.id,g2perfil(),k),{})};
  /* A liberar é rascunho (nada reservado): quem cria pode cancelar, com motivo (BEN-D22) */
  if(at==='A liberar') sec.push({t:'Cancelar a ordem',go:()=>self.setState({pr_modo:'cancelar',pr_form:null,pr_err:'',pr_ch:prChave('W-BNC'),bn_ver:o.ver})});
  if((at==='Em execução'||(at==='Liberadas'&&benFaltaCx(c,o)>0))&&o.req) sec.push({t:'Pedir mais caixas',go:()=>self.setState({pr_modo:'caixas',pr_form:null,pr_err:'',pr_ch:prChave('W-BNX'),bn_ver:o.ver})});
  if(at==='Em conferência'){ sec.push({t:'Reabrir execução',go:()=>self.setState({pr_modo:'reabrir',pr_form:null,pr_err:''})}); if(!o.ben.conf) sec.push({t:'+ Registrar perda',go:abreSaida}); }
  return PPx; }
function EXTRAVALS(self,v){ prRst(self,v); const c=self._c||cenGet(); const st=self.state; const ords=self._ords||[];
  const vis=st.bn_vis||'l'; v.vl=vis==='l'; v.vk=vis==='k'; v.vl_on=String(vis==='l'); v.vk_on=String(vis==='k'); v.vl_go=()=>self.setState({bn_vis:'l'}); v.vk_go=()=>self.setState({bn_vis:'k'});
  v.kb=bnKanban(self,c,ords);
  v.nova_go=()=>self.setState({pr_pan:{g:'nova'},pr_sel:null,pr_form:null,pr_err:'',pr_modo:null,pr_ch:prChave('W-BNN'),bn_rasc:null});
  v.cards_ob=prCards(self,v,'g_ob',id=>{ const o=c.ordens[id]; if(!benEh(o)) return null; const nx=benProx(c,o);
    return prCard({t1:o.id+' · '+bnProdTxt(o),num:benKg(benEntrada(o)),t2:benRotaTxt(benRota(o.ben.rota))+' · '+o.talhao+' · '+bnQtdTxt(o),chip:[o.etapa,BN_FCOR[o.etapa]||'gray'],nx:nx.t+(nx.quem?' · '+nx.quem:''),go:()=>self.g2pick('g_ob',id)}); });
  /* sem primária no cabeçalho (rodada 1, S4; BOT-01 e BOT-08): ela só abria o painel da ordem (navegação) e repetia o verde do painel com
     o mesmo verbo; a decisão fica no painel, e a lista diz o próximo passo de cada ordem */
  prPrim(v,null);
  const n=f=>ords.filter(x=>x.etapa===f).length; const imp=ords.filter(x=>benSelos(c,x).some(s=>s.c==='red')).length; const ap=benLotesAptos(c).filter(L=>prFazOk(self,L.faz)).length;
  prStatus(v,[n('A liberar')?n('A liberar')+' a liberar':'',n('Em execução')?n('Em execução')+' em execução':'',n('Em conferência')?n('Em conferência')+' em conferência':'',ap?ap+(ap>1?' lotes a beneficiar':' lote a beneficiar'):''].filter(Boolean).join(' · ')||'nada a processar',imp?'red':(n('A liberar')||n('Em conferência')?'yellow':'green'));
  const pan=st.pr_pan; let PP=null;
  if(pan&&pan.g==='nova') PP=bnNovaForm(self,c,pan.lote||'');
  else if(pan&&c.ordens[pan.id]&&benEh(c.ordens[pan.id])) PP=bnPainel(self,c,c.ordens[pan.id]);
  /* toda ação do painel (primária, secundárias, ações das linhas e o fechar) passa pela guarda da repetição */
  /* rascunho à vista (I-h1): o aviso no lugar do erro e as duas saídas no rodapé (o fechar genérico some: Descartar já é a saída) */
  if(PP&&bnRascOn(self)){ const voltar=st.bn_rasc.m==='voltar';
    PP.err='Rascunho não salvo: os valores digitados se perdem. Continuar editando ou Descartar?'; PP.closeHide=true;
    PP.sec=[{t:'Continuar editando',go:()=>{ self.setState({bn_rasc:null}); setTimeout(()=>{ try{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); const f=a&&a.querySelector('input,select,textarea'); if(f) f.focus(); }catch(e){} },0); }},
      {t:'Descartar',go:()=>voltar?self.setState({bn_rasc:null,pr_modo:null,pr_form:null,pr_err:''}):self.setState({bn_rasc:null,pr_pan:null,pr_form:null,pr_err:'',pr_ferr:null,pr_modo:null})}]; }
  if(PP){ if(PP.prim&&PP.prim.go) PP.prim.go=bnGuarda(self,PP.prim.go); (PP.sec||[]).forEach(b=>{ b.go=bnGuarda(self,b.go); });
    (PP.secs||[]).forEach(s=>(s.rows||[]).forEach(r=>{ if(r.a&&r.a.go) r.a.go=bnGuarda(self,r.a.go); })); }
  prPainel(self,v,PP);
  /* fechar: o toque logo depois de uma ação é absorvido calado (toque duplo na linha cai no fundo do painel); o Esc (sem evento) fecha sempre */
  if(PP){ const fc=v.pp_close, fg=bnGuarda(self,fc,true); const fz=(e)=>e?fg(e):fc();
    v.pp_close=(e)=>{ if(bnSujo(self)&&!bnRascOn(self)){ bnRasc(self,'fechar'); return; } if(self.state.bn_rasc) self.setState({bn_rasc:null}); fz(e); };
    /* sem formulário (ou depois de uma recusa) o fechar do rodapé volta à lista: "Fechar" ao lado de "Fechar processo" repetia o verbo (S4) */
    if(!(PP.form&&!PP.form.aviso)) v.pp_closeT='Voltar à lista'; }
  self._bnFecha=v.pp_close;
  /* foco do painel (teclado, rodada 1): ao abrir uma ordem (ou a ordem nova), o foco entra no painel pelo "Fechar" do topo, para a leitura
     começar do título; ao fechar, volta para quem abriu. Sem isso o foco ficava fora do painel (Tab percorria a página) ou, depois do
     "Criar ordem", parava em "Autorizar rota e liberar" (o mesmo botão, reaproveitado), a um Enter de liberar */
  /* o botão com o foco pode sumir depois de uma ação (o painel se refaz): o foco volta ao painel, não ao início da página; e o Esc fecha o
     painel mesmo sem foco dentro dele */
  if(PP) setTimeout(()=>{ try{ const ae=document.activeElement; if(ae&&ae!==document.body) return; const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length);
    const b=a&&a.querySelector('button[aria-label="Fechar"]'); if(b) b.focus({preventScroll:true}); }catch(e){} },0);
  if(!self.__bnEsc){ self.__bnEsc=1; try{ window.addEventListener('keydown',(e)=>{ if(e.key!=='Escape'||e.defaultPrevented||!self.state.pr_pan) return; const ae=document.activeElement;
    if(ae&&ae.closest&&ae.closest('aside[role=dialog],[role=dialog]')) return; e.preventDefault(); if(self._bnFecha) self._bnFecha(); else self.setState({pr_pan:null,pr_form:null,pr_err:'',pr_ferr:null,pr_modo:null}); }); }catch(e){} }
  const pn=st.pr_pan, pk=PP&&pn?(pn.g+'|'+(pn.id||'')):'';
  if(pk!==(self._bnPk||'')){ const ant=self._bnPk||''; self._bnPk=pk;
    if(pk){ self._bnVoltaId=pn.id||''; if(!ant){ try{ const ae=document.activeElement; self._bnVolta=ae&&ae!==document.body&&!(ae.closest&&ae.closest('aside[role=dialog]'))?ae:null; }catch(e){ self._bnVolta=null; } }
      setTimeout(()=>{ try{ const a=[...document.querySelectorAll('aside[role=dialog]')].find(x=>x.getClientRects().length); const b=a&&(a.querySelector('button[aria-label="Fechar"]')||a.querySelector('button,[href],input')); if(b) b.focus({preventScroll:true}); }catch(e){} },0); }
    else { const v0=self._bnVolta, vid=self._bnVoltaId||''; self._bnVolta=null;
      /* a linha da mesma ordem primeiro (a lista reordena depois de cancelar e o nó de quem abriu passa a mostrar outra ordem); senão quem
         abriu; senão "+ Nova ordem" */
      setTimeout(()=>{ try{ if(document.querySelector('aside[role=dialog]')) return; const vis=x=>!!x&&x.isConnected&&x.getClientRects().length>0;
        const lin=vid&&[...document.querySelectorAll('[role=row][data-rid]')].find(x=>x.getAttribute('data-rid')===vid&&vis(x));
        const nv=[...document.querySelectorAll('main button')].find(x=>x.innerText.trim()==='+ Nova ordem'&&vis(x));
        const alvo=lin||(vis(v0)?v0:nv); if(alvo) alvo.focus({preventScroll:true}); }catch(e){} },0); } } }
/* entrada por link: BEN.dc.html#OB-0110 abre a ordem; #nova=L39-131 abre a ordem nova com o lote (vindo do Estoque de produto) */
function bnHash(self){ if(self.__bnh) return; self.__bnh=1; const ab=()=>{ let h=''; try{ h=decodeURIComponent(location.hash||'').slice(1); }catch(e){} const c=cenGet();
  if(/^nova=/.test(h)){ const id=h.slice(5); setTimeout(()=>self.setState({pr_pan:{g:'nova',lote:id},pr_sel:null,pr_form:{lt:id},pr_err:'',pr_modo:null,pr_ch:prChave('W-BNN')}),0); }
  else if(benEh((c.ordens||{})[h])) setTimeout(()=>self.g2pick('g_ob',h),0); }; ab(); try{ window.addEventListener('hashchange',ab); }catch(e){} }
const _EXV=EXTRAVALS; EXTRAVALS=function(self,v){ bnHash(self); bnRepete(); _EXV(self,v); };
/* gancho de teste, como na O.S. e no Estoque: o teste lê o cenário pelo cenGet quando nada foi gravado ainda */
try { window.__cen = { cenGet, cenMudar, cenReset }; } catch (e) {}
'''
