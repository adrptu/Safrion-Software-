# -*- coding: utf-8 -*-
"""Regressão focal SINT-C03 (comentário 5974993475) e PRE-REV-20261004: regra única de quantidade de insumo (quantidade.py ⇄
cenQtd/cenQtdTrecho do cenario.js), o apontamento com custódia e todo produtor de total de insumo (O.S., MIP, fertirrigação).
Roda o JS real do protótipo (cenario.js + núcleo da O.S. + mip.js + irrigacao_estado.js) no jsc (macOS) ou node (Linux), sem navegador.
Uso (de gen37/): python3 quantidade_test.py"""
import json, os, random, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import quantidade as Q, cenario, dados_mip, dados_irrigacao
from areas.processo_os import JS_NUCLEO
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MOTOR, PRELUDIO = ([JSC], '') if os.path.exists(JSC) else (['node'], 'globalThis.print=(...a)=>console.log(...a);\n')
OK = []
def chk(nome, cond, info=''):
    OK.append(bool(cond)); print(('OK    ' if cond else 'FALHOU ') + nome + ('' if cond else ' · ' + str(info)[:500]), flush=True)

# grade determinística: doses do protótipo × áreas com 2 casas, com empates (…,5 no 3º decimal) forçados
r = random.Random(20261004)
doses = [0.1, 0.25, 0.3, 0.4, 0.5, 1, 1.5, 2.5, 3, 20, 25, 30, 40, 45, 50, 150, 400, 1850, 2000]
areas = [62.25, 62.79, 30.55, 31.7, 0.01, 0.05, 48.47, 50.63, 73.18] + [round(r.uniform(0.01, 200), 2) for _ in range(400)]
casos = [(d, a) for d in doses for a in areas] + [(1e-7, 28.7), (2.5e-7, 62.25), (1e21, 2), (123456789.123, 98765.43), (0.005, 1), (0.004, 1)]
py = [Q.qtd(d, a) for d, a in casos]

JS = r"""
const R={};
// 1 · igualdade com o Python
R.grade=CASOS.map(([d,a])=>{ try{ return cenQtd(d,a); }catch(e){ return 'ERRO '+e.message; } });
// 2 · osc_apontar EXATO do núcleo da O.S., com custódia = total (quantidade da área da ordem)
function fixture(area){ const tot=cenQtd(0.5,area); return {tot,c:{ordens:{DEMO:{id:'DEMO',etapa:'Em execução',area,saldo:area,realizado:0,ap:[],req:'REQ-DEMO',
  ins:[{p:'Produto sintético',dose:0.5,un:'L',tot}]}},reqs:{'REQ-DEMO':{itens:[{prod:'Produto sintético',un:'L',custodia:tot,consumido:0}]}}}}; }
function apontar(area,partes){ const f=fixture(area); const out={area,tot:f.tot,erros:[],n:0};
  for(const h of partes){ try{ osc_apontar(f.c,'DEMO',(24+out.n)+'/09',h); out.n++; } /* CTL-2 · A: um trecho por dia (o mesmo dia com outra chave fica em conferência de duplicidade) */ catch(e){ out.erros.push(e.message); } }
  const o=f.c.ordens.DEMO, it=f.c.reqs['REQ-DEMO'].itens[0];
  Object.assign(out,{custodia:it.custodia,consumido:it.consumido,saldo:o.saldo,realizado:o.realizado,somaAp:o.ap.reduce((s,a)=>s+(a.cons['Produto sintético']||0),0)}); return out; }
R.apontar=[apontar(62.25,[62.25]),apontar(62.79,[62.79]),apontar(62.25,[30.55,31.7]),apontar(62.25,[20.01,20.02,22.22]),apontar(73.18,[0.05,36.5,36.63])];
// 3 · turno do app (cenFecharTurno) em dois trechos, mesma custódia
function turno(area,partes){ const f=fixture(area); const c=f.c; c.app={online:true,fila:[],turno:null,operador:'Teste'}; c.movs=[]; const out={area,tot:f.tot,erros:[]};
  for(const h of partes){ try{ c.app.turno={os:'DEMO',ini:'08:00'}; cenFecharTurno(c,h,4,{},'',[]); }catch(e){ out.erros.push(e.message); } }
  const it=c.reqs['REQ-DEMO'].itens[0]; Object.assign(out,{custodia:it.custodia,consumido:it.consumido,saldo:c.ordens.DEMO.saldo}); return out; }
R.turno=[turno(62.25,[62.25]),turno(62.25,[30.55,31.7])];
// 6 · a trava de custódia continua: consumo acima do que está em custódia é recusado, sem gravar nada (web e app)
function recusa(){ const f=fixture(62.25); const it=f.c.reqs['REQ-DEMO'].itens[0]; it.custodia=31.12;   // custódia menor que o consumo 31,13
  const w={}; try{ osc_apontar(f.c,'DEMO','24/09',62.25); w.erro=''; }catch(e){ w.erro=e.message; }
  Object.assign(w,{ap:f.c.ordens.DEMO.ap.length,custodia:it.custodia,consumido:it.consumido,realizado:f.c.ordens.DEMO.realizado});
  const g=fixture(62.25); const c=g.c; const it2=c.reqs['REQ-DEMO'].itens[0]; it2.custodia=31.12; c.app={online:true,fila:[],turno:{os:'DEMO',ini:'08:00'},operador:'Teste'}; c.movs=[];
  const a={}; try{ cenFecharTurno(c,62.25,4,{},'',[]); a.erro=''; }catch(e){ a.erro=e.message; }
  Object.assign(a,{ap:c.ordens.DEMO.ap.length,custodia:it2.custodia,consumido:it2.consumido}); return {web:w,app:a}; }
R.recusa=recusa();
// 4 · sementes da Lagoa em execução: o saldo restante consome exatamente a custódia de cada item
R.lagoa=['OS-0506','OS-0507'].map(id=>{ const c=JSON.parse(JSON.stringify(CEN0)); const o=c.ordens[id]; const r=c.reqs[o.req]; let erro='';
  try{ osc_apontar(c,id,'24/09',o.saldo); }catch(e){ erro=e.message; }
  return {id,erro,saldo:o.saldo,custodias:r.itens.map(i=>i.custodia),consumido_vs_total:r.itens.map(i=>[i.consumido,i.solicitado])}; });

// 16 · calda: divisão fracionária e conversão após arredondamento por origem.
R.calda=[];
{
 const savedAloc=AL0.aloc,aid=AL0.ativo.PJ,savedAtivo=CEN_PREP_ATIVOS[aid];
 try {
  AL0.aloc=[{r:'PJ',os:'CALDA',dia:'2026-09-29',ini:6,fim:7}];
  CEN_PREP_ATIVOS[aid]=Object.assign({},savedAtivo,{tanque:2000});
  for(const area of [49.31,0,0.01,40]) {
   const o={id:'CALDA',versao:1,saldo:area,instrucao:{versao:1,vazao:150},ins:[{p:'demo',dose:.5,un:'L'}]},c={ordens:{CALDA:o}},antes=JSON.stringify(c);
   const p=cenPreparoOrdem(c,o);
   R.calda.push({tipo:'individual',area,ok:p.ok,intacto:antes===JSON.stringify(c),esperado:cenQtd(.5,area),
    soma:p.cargas.reduce((s,k)=>s+k.prods[0].q,0),qs:p.cargas.map(k=>k.prods[0].q),cheia:p.produtos&&p.produtos[0].q});
  }
 } finally {AL0.aloc=savedAloc;CEN_PREP_ATIVOS[aid]=savedAtivo;}
 for(const unidades of [['L','L','L'],['L','mL','L'],['kg','g','kg']]) {
  const c=cenClone(CEN0),ids=['OS-0590','OS-0591','OS-0592'],ars=[49.31,.01,13.34];
  ids.forEach((id,i)=>{const o=c.ordens[id];o.area=o.saldo=ars[i];o.ins[0].un=unidades[i];o.ins[0].dose=i===1&&['mL','g'].includes(unidades[i])?500:.5;
   o.ins[0].tot=cenQtd(o.ins[0].dose,o.area);o.loteFicha.volumeHa=150;o.loteFicha.tanqueUtil=2000;});
  const antes=JSON.stringify(c),p=cenGrupoPrevia(c,ids,'Caio');
  R.calda.push({tipo:'grupo',unidades,intacto:antes===JSON.stringify(c),ok:true,esperado:p.produtos[0].q,
   soma:p.cargas.reduce((s,k)=>s+k.produtos[0].q,0),qs:p.cargas.map(k=>k.produtos[0].q)});
 }
}

print(JSON.stringify(R));
"""
# 7/8 · produtores de total fora da O.S.: MIP (mipEmitir) e fertirrigação (irrReclassTudo), percorrendo liberar → entregar → confirmar →
# iniciar → apontar o saldo → conferência, como na tela. localStorage em memória (a tela grava no navegador).
LS = ('const __LS={};globalThis.localStorage={getItem:k=>(k in __LS?__LS[k]:null),setItem:(k,v)=>{__LS[k]=String(v)},'
      'removeItem:k=>{delete __LS[k]}};\n')
JS_FLUXO = r"""
(()=>{   // escopo próprio: os prefixos das telas já declaram nomes curtos
function fluxo(c,id,res){ const o=c.ordens[id]; res.area=o.area; res.tot=o.ins[0].tot; res.regra=cenQtd(o.ins[0].dose,o.area);
  const passo=(n,f)=>{ try{ f(); }catch(e){ res.erro=n+': '+e.message; throw e; } };
  // o assunto aqui é a custódia, não a falta de estoque: completa o lote antes de liberar (só no teste)
  (o.ins||[]).forEach(x=>{ const l=cenLote(c,x.p); if(l&&cenDisp(l)<x.tot) l.fisico+=x.tot; });
  try{ passo('liberar',()=>osc_liberar(c,id,false,'','Ana'));   /* CTL-3: quem aprova e libera */
    const rq=c.reqs[o.req]; for(const it of rq.itens){ const q=cenSaldoEntregar(it); if(q>1e-9) passo('entregar',()=>cenEntregar(c,o.req,it.prod,q,'X','Rui')); }
    passo('confirmar',()=>cenConfirmarRecebimento(c,o.req)); passo('iniciar',()=>osc_iniciar(c,id));
    passo('apontar o saldo',()=>osc_apontar(c,id,'20/10',o.saldo)); passo('conferência',()=>osc_conferencia(c,id));
    /* desde a v56 (CONTROLE-02 fatia 1) encerrar exige a conferência diária de cada dia apontado: o teste confere como Paula (conferente) */
    if(typeof cdConferir==='function') (o.ap||[]).forEach(a=>passo('conferir o dia '+a.dia,()=>cdConferir(c,id,a.dia,'conferir','apontamento conferido no teste',cdReferencia(c,id,a.dia),G2_PERFIS.find(p=>p.k==='Paula')))); }catch(e){}
  const it=o.req&&c.reqs[o.req]&&c.reqs[o.req].itens[0]; res.custodia=it?it.custodia:null; res.etapa=o.etapa; return res; }
const R={mip:[],fert:[],area:[]};
const s0=mipGet(); const maior=a=>a.tr.filter(x=>/Área maior/.test(x));
// formulário "Decidir controle" (agDecIni real do AG-01), em toda vistoria da Lagoa: o que ele preenche passa nas checagens de área
// AGRO-02: o formulário abre sem produto nem dose (vazio); para a checagem de área chegar ao fim, o teste escolhe explicitamente
// o 1º registrado não cancelado e digita a dose mínima da bula, como o RT faria
if(typeof agDecIni==='function') for(const v of Object.values(s0.vis).filter(v=>/^PV/.test(v.tal))){ const t=mipT(v); let st=null;
  agDecIni({state:{},setState:x=>{ st=x; }},v.id); const d=st.dec;
  const u=(d.kind==='controlar'||d.kind==='localizado')?mipElig(v).find(x=>x.sit!=='Cancelado'):null;
  const ck=(ar)=>mipChecks(mipGet(),v,{kind:d.kind,prod:u?u.id:'',dose:u?String(u.dmin):'',area:ar,data:d.data},cenGet());
  R.area.push({vis:v.id,kind:d.kind,form:d.area,vazio:d.prod===''&&d.dose==='',trava:maior(ck(d.area)),antes:d.kind==='controlar'&&maior(ck(mipN(t.area,1))).length>0}); }
// emissão pelo MIP: área do talhão e a maior área em que 3 casas ficariam ABAIXO da regra única (o caso que recusava o apontamento)
const tres=(dose,ar)=>Math.round(dose*ar*1000)/1000;
const sobe=(dose,max)=>{ for(let k=0;k<400;k++){ const ar=Math.round(max*100-k)/100; if(ar<=0) break; if(tres(dose,ar)<cenQtd(dose,ar)) return ar; } return null; };
const vis=Object.values(s0.vis).filter(v=>/^PV/.test(v.tal)&&!v.dec&&mipElig(v).length);
for(const v of vis){ const t=mipT(v);
  for(const u of mipElig(v)){ if(u.sit==='Cancelado') continue; for(const [dose,area] of [[u.dmin,t.area],[u.dmax,t.area],[u.dmin,sobe(u.dmin,t.area)]]){ if(!area) continue; cenReset(); mipReset();
    if(!cenLote(cenGet(),u.nome)){ R.semLote=(R.semLote||0)+1; continue; }   // produto sem lote no Estoque: a liberação recusa (outra trava)
    const a={kind:'controlar',prod:u.id,dose:String(dose),area:String(area),data:'2026-10-20',nota:''}; const res={vis:v.id,prod:u.nome,dose,sobe:tres(dose,area)<cenQtd(dose,area)};
    const k=mipChecks(mipGet(),mipGet().vis[v.id],a,cenGet()); if(k.tr.length){ res.trava=k.tr; R.mip.push(res); continue; }
    const r=mipEmitir(null,v.id,Object.assign({ator:'Ana',chave:'TESTE-'+v.id+'-'+u.id+'-'+dose+'-'+area,dver:((mipGet().vis[v.id].dec||{}).ver||0)+1},a));   /* N-1: autor, chave e versão como a tela */ if(r.erro){ res.erro='emitir: '+r.erro; R.mip.push(res); continue; } const c=cenGet();
    const id=Object.keys(c.ordens).find(x=>c.ordens[x].osc&&c.ordens[x].osc.novo&&(c.ordens[x].osc.novo.keys||[]).indexOf('mip|'+v.id+'|'+v.prot)>=0);
    R.mip.push(fluxo(c,id,res)); } } }
const i0=irrGet(); const ords=Object.keys(i0.ordens).filter(k=>['A liberar','Liberadas','Em execução'].indexOf(i0.ordens[k].etapa)>=0&&!i0.ordens[k].fert);
for(const id of ords){ for(const dose of [1,7,12,50]){ cenReset(); irrReset(); const res={id,dose};
  const r=irrReclassTudo(null,id,{prod:'Nitrato de cálcio',dose,mot:'teste'}); if(r.erro){ res.recusa=r.erro; R.fert.push(res); continue; }
  res.msg=r.msg; R.fert.push(fluxo(cenGet(),id,res)); } }
// v2 com passada em curso (avanço com 2 casas): a O.S. recebe o que falta (2 casas, irrAreaV2, a mesma conta da prévia) e v1 + v2 = área do setor
R.parc=[]; for(const id of ords.filter(k=>i0.ordens[k].etapa==='Liberadas')){ for(const cob of [20.27,0.05,20.275]){ cenReset(); irrReset(); const res={id,cob};   // 20,275: avanço digitado com 3 casas (PRE-REV Z4)
  try{ const s=irrGet(); irrIniciar(s,id); irrAvanco(s,id,Math.min(cob,s.setores[s.ordens[id].setor].ha)); irrSave(s); }catch(e){ res.recusa=e.message; R.parc.push(res); continue; }
  const r=irrReclassTudo(null,id,{prod:'Nitrato de cálcio',dose:12,mot:'teste'}); if(r.erro){ res.recusa=r.erro; R.parc.push(res); continue; }
  const s1=irrGet(), o1=s1.ordens[id], x1=s1.setores[o1.setor]; res.ha=x1.ha; res.v1=o1.fert.v1; res.prev=irrAreaV2(x1,{cob:o1.fert.v1});
  R.parc.push(fluxo(cenGet(),id,res)); } }
// 11 · borda (PRE-REV Z1/Z2/Z5): a liberação reserva exatamente a regra única; total 0 com dose > 0 é recusado; o aviso do MIP usa o lote da liberação
const lib=(dose,area,fis)=>{ const c={ordens:{X:{id:'X',etapa:'A liberar',area,saldo:area,realizado:0,ap:[],ins:[{p:'P',dose,un:'L',tot:cenQtd(dose,area)}]}},reqs:{},
    lotes:{'P|L1':{prod:'P',lote:'L1',fisico:fis,reservado:0,quarentena:0}},movs:[]}; try{ cenLiberar(c,'X'); return 'ok'; }catch(e){ return e.message; } };
R.borda={exato:lib(0.5,49.31,cenQtd(0.5,49.31)),falta:lib(0.5,49.31,cenQtd(0.5,49.31)-0.01),zero:lib(0.0001,49.31,100),zero2:lib(1e-7,49.31,100)};
const vb=Object.values(s0.vis).find(v=>/^PV/.test(v.tal)&&!v.dec&&mipElig(v).length); const ub=mipElig(vb)[0], tb=mipT(vb), nb=cenQtd(ub.dmin,tb.area);
const avi=(lotes)=>{ cenReset(); const c=cenGet(); Object.keys(c.lotes).forEach(k=>{ if(c.lotes[k].prod===ub.nome) delete c.lotes[k]; }); lotes.forEach((q,i)=>{ c.lotes[ub.nome+'|B'+i]={prod:ub.nome,lote:'B'+i,fisico:q,reservado:0,quarentena:0}; });
  return mipChecks(mipGet(),vb,{kind:'controlar',prod:ub.id,dose:String(ub.dmin),area:String(tb.area),data:'2026-10-20'},c).al.filter(x=>/aguarda a compra/.test(x)).length; };
R.borda.mip={um_lote_exato:avi([nb]),dois_lotes_sem_um_que_cubra:avi([Math.round(nb*60)/100,Math.round(nb*60)/100])};
// 12 · rodada 4 (PRE-REV Y1–Y6): trava do ajuste do núcleo, término com 2 casas, v2 de 0 ha, MIP com total 0, rótulo "Total 0"
const aj=(fis,d,ar)=>osc_ajFalta({lotes:{'P|L1':{prod:'P',lote:'L1',fisico:fis,reservado:0,quarentena:0}}},'P','L',d,ar);
R.r4={aj:[aj(cenQtd(0.5,49.31),0.5,49.31),aj(cenQtd(0.5,49.31)-0.01,0.5,49.31),aj(100,0.0001,49.31),aj(100,0.4,0.01),aj(100,0.5,0.01)]};
// Fixture de tempo/medição: o teste de quantidade termina no fim previsto e fornece uma leitura sintética explícita.
// O comando de produção mantém as travas de término antecipado e hidrômetro obrigatório.
function terminarNoFim(s,id,cob){
  const o=irrO(s,id), p=irrPassAtual(o);
  s.agora=Math.max(s.agora,irrFimP(o,p));
  return irrTerminar(s,id,cob,Math.round(p.lam*irr2(cob)*10*100)/100);
}
const idL=ords.find(k=>i0.ordens[k].etapa==='Liberadas'); const term=(cob)=>{ irrReset(); const s=irrGet(); irrIniciar(s,idL); try{ terminarNoFim(s,idL,cob); }catch(e){ return 'ERRO '+e.message; }
  return irrO(s,idL).passadas.find(p=>p.st==='Parcial'||p.st==='Feita').cob; };
R.r4.term=[term(20.275),term(0.004)];
R.tempo={};
{ irrReset(); const s=irrGet(); irrIniciar(s,idL); const before=JSON.stringify(s);
  try{ irrTerminar(s,idL,20.28,100); R.tempo.cedo='aceitou'; }catch(e){ R.tempo.cedo=e.message; }
  R.tempo.intacto=JSON.stringify(s)===before;
  const o=irrO(s,idL); s.agora=Math.max(s.agora,irrFimP(o,irrPassAtual(o))); const atFim=JSON.stringify(s);
  try{ irrTerminar(s,idL,20.28,null); R.tempo.semMedicao='aceitou'; }catch(e){ R.tempo.semMedicao=e.message; }
  R.tempo.semBaixa=JSON.stringify(s)===atFim;
}

{ cenReset(); irrReset(); const s=irrGet(); irrIniciar(s,idL); irrAvanco(s,idL,s.setores[s.ordens[idL].setor].ha); irrSave(s);
  R.r4.v2cheia=irrReclassTudo(null,idL,{prod:'Nitrato de cálcio',dose:12,mot:'teste'}).erro||'criada'; }
{ cenReset(); mipReset(); const k=mipChecks(mipGet(),vb,{kind:'localizado',prod:ub.id,dose:String(ub.dmin),area:'0,01',data:'2026-10-20'},cenGet()); R.r4.mip0=k.tr.filter(x=>/dá 0/.test(x)).length; }
{ cenReset(); const c=cenGet(); c.ordens.Z0={id:'Z0',etapa:'A liberar',area:10,saldo:10,realizado:0,ap:[],ins:[{p:ub.nome,dose:0.0001,un:ub.un,tot:0}]};
  const o=osMerge({id:'Z0',etapa:'A liberar',area:10,ins:[],selos:[],agua:false,dono:'Ana (agrônoma)',cond:'Pronta. Próximo passo: liberar para execução.'},c.ordens.Z0,c);
  R.r4.rotulo=[o.selos.map(x=>x.t).join(','),o.dono,o.prazo];
  // 13 · rodada 5 (PRE-REV X1/X2/X5): o painel diz o agrônomo e não o Estoque; ajuste sem liberar recusa total 0; v2 com outra passada
  let px=null; try{ px=osProx(o); }catch(e){ px={erro:e.message}; } R.r5={prox:JSON.stringify(px||{})};
  try{ osc_ajustar(c,'Z0',9,{[ub.nome]:0.0001},'',[],[],false,'Ana'); /* muda a área: grava versão nova */ R.r5.ajSemLib='gravou'; }catch(e){ R.r5.ajSemLib=e.message; } }
{ irrReset(); const s=irrGet(); const id2=Object.keys(s.ordens).find(k=>s.ordens[k].passadas.length>1&&['Liberadas'].indexOf(s.ordens[k].etapa)>=0);
  if(id2){ irrIniciar(s,id2); const o2=s.ordens[id2], x2=s.setores[o2.setor], p2=irrPassAtual(o2); p2.cob=x2.ha; R.r5.multi=irrV2Zero(o2,x2,p2,12); } else R.r5.multi='sem ordem de 2 passadas'; }
// 14 · rodada 6 (PRE-REV U1–U5): crédito de avanço pequeno; v2 com passada em curso e outra programada; número não finito; dose da v2
R.r6={};
{ const fim=(c,id)=>{ fluxo(c,id,{}); osc_encerrar(c,id); return c.ordens[id].etapa; };
  const def=(av)=>{ cenReset(); irrReset(); let s=irrGet(); irrIniciar(s,'OS-0602'); if(av>0) irrAvanco(s,'OS-0602',av); irrSave(s);
    const k=irrReclassTudo(null,'OS-0602',{prod:'Nitrato de cálcio',dose:12,mot:'teste'}); if(k.erro) return 'ERRO '+k.erro; const c=cenGet(); const et=fim(c,'OS-0602'); cenSave(c);
    s=irrGet(); return [et,irrDef(s,'PV08'),!!irrFaixaCob(s,'PV08')]; };
  R.r6.u1=[def(0),def(0.03),def(0.06)];
  cenReset(); irrReset(); let s=irrGet(); irrIniciar(s,'OS-0604'); irrAvanco(s,'OS-0604',24.47); irrSave(s);
  R.r6.u2=irrReclassTudo(null,'OS-0604',{prod:'Nitrato de cálcio',dose:12,mot:'teste'}).erro||'criada';
  cenReset(); irrReset(); s=irrGet(); const d0=irrDef(s,'PV18'); irrIniciar(s,'OS-0604'); terminarNoFim(s,'OS-0604',24.47); irrSave(s);
  const k=irrReclassTudo(null,'OS-0604',{prod:'Nitrato de cálcio',dose:12.25,mot:'teste'}); s=irrGet(); const f=s.ordens['OS-0604'].fert;
  R.r6.u5=k.msg||k.erro; R.r6.guia={erro:k.erro||'',area:f&&f.area,ha:s.setores.PV18.ha,lamHa:f&&f.lamHa,lam2:s.ordens['OS-0604'].passadas[1].lam,d0};
  if(!k.erro){ const c=cenGet(); R.r6.guia.et=fim(c,'OS-0604'); cenSave(c); R.r6.guia.d1=irrDef(irrGet(),'PV18'); } }
{ cenReset(); mipReset(); const sem=(d,a)=>{ try{ return mipChecks(mipGet(),vb,{kind:'controlar',prod:ub.id,dose:d,area:a,data:'2026-10-20'},cenGet()).tr.join(' | '); }catch(e){ return 'LANÇOU '+e.message; } };
  R.r6.u3={dose:sem('1e999',String(tb.area)),area:sem(String(ub.dmin),'1e999'),inf:sem('Infinity','1'),
    aj:(()=>{ try{ return osc_ajFalta({lotes:{}},'P','L',Infinity,10); }catch(e){ return 'LANÇOU '+e.message; } })()}; }
print(JSON.stringify(R));
})();
"""

def roda(src):
    f = tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8'); f.write(src); f.close()
    p = subprocess.run(MOTOR + [f.name], capture_output=True, text=True, timeout=300); os.unlink(f.name)
    if p.returncode != 0: print((p.stderr or p.stdout)[-1500:]); sys.exit(1)
    return json.loads(p.stdout.strip().splitlines()[-1])
R = roda(PRELUDIO + cenario.perfis_js() + cenario.js_prefixo() + JS_NUCLEO + '\nconst CASOS=' + json.dumps(casos) + ';\n' + JS)
import areas.agronomia as AG
DOM = 'globalThis.document={getElementById:()=>null,querySelector:()=>null};globalThis.setTimeout=()=>0;\n'   # agFoco sem tela
F = roda(PRELUDIO + LS + DOM + cenario.perfis_js() + cenario.js_prefixo() + JS_NUCLEO + dados_mip.js_prefixo() + dados_irrigacao.js_prefixo() + AG.JS_AG01 + JS_FLUXO)

dif = [(c, a, b) for c, a, b in zip(casos, py, R['grade']) if a != b]
empates = [c for c in casos if (round(c[0] * c[1] * 1000) % 10 == 5)]
chk(f'1 regra única: Python qtd = JS cenQtd em {len(casos)} casos ({len(empates)} com empate no 3º decimal; notação exponencial e valores extremos sem erro); 0,5 × 62,25 = 31,13 (meio para cima)',
    not dif and Q.qtd(0.5, 62.25) == 31.13 and Q.qtd(0.5, 62.79) == 31.4, dif[:5])
a = R['apontar']
chk('2 SINT-C03: apontamento cheio de 62,25 ha e de 62,79 ha passa; custódia 0; consumido = total; saldo 0',
    all(not x['erros'] and x['n'] == 1 and abs(x['custodia']) < 1e-9 and abs(x['consumido'] - x['tot']) < 1e-9 and x['saldo'] == 0 for x in a[:2]), a[:2])
chk('3 apontamentos parciais (2 e 3 trechos, inclusive 0,05 ha) conservam o total: soma dos consumos = total, custódia 0, realizado = área',
    all(not x['erros'] and abs(x['somaAp'] - x['tot']) < 1e-9 and abs(x['custodia']) < 1e-9 and abs(x['realizado'] - x['area']) < 1e-6 for x in a[2:]), a[2:])
t = R['turno']
chk('4 turno do app (cenFecharTurno), inteiro e em 2 trechos: consumo padrão pela mesma regra, custódia 0, saldo 0',
    all(not x['erros'] and abs(x['custodia']) < 1e-9 and abs(x['consumido'] - x['tot']) < 1e-9 and x['saldo'] < 1e-9 for x in t), t)
lg = R['lagoa']
chk('5 sementes da Lagoa (OS-0506 e OS-0507): apontar o saldo restante consome exatamente a custódia (0 em cada item), sem erro',
    all(not x['erro'] and x['saldo'] < 1e-9 and all(abs(cu) < 1e-9 for cu in x['custodias']) for x in lg), lg)
w, a = R['recusa']['web'], R['recusa']['app']
chk('6 trava de custódia executada: 31,13 contra 31,12 em custódia é recusado na web e no app, sem apontamento nem baixa (sem tolerância nova)',
    'acima do que está em custódia' in w['erro'] and w['ap'] == 0 and w['custodia'] == 31.12 and w['consumido'] == 0 and w['realizado'] == 0
    and 'acima do que está com você' in a['erro'] and a['ap'] == 0 and a['custodia'] == 31.12 and a['consumido'] == 0, R['recusa'])
ok = lambda x: not x.get('erro') and not x.get('trava') and x['tot'] == x['regra'] and abs(x['custodia']) < 1e-9 and x['etapa'] == 'Em conferência'
m = F['mip']
ne = sum(1 for x in m if x['sobe'])
chk(f'7 MIP → O.S. ({len(m)} emissões nos pivôs da Lagoa, doses da bula; {ne} em que o total antigo de 3 casas ficaria abaixo do consumo; '
    f'{F.get("semLote", 0)} sem lote no Estoque, fora): total = regra única; liberar, entregar, iniciar e apontar o saldo zeram a custódia e levam à '
    'conferência', len(m) >= 6 and ne >= 2 and all(map(ok, m)), [x for x in m if not ok(x)][:4])
fe = F['fert']; fa = [x for x in fe if 'recusa' not in x]
pc = [x for x in F['parc'] if 'recusa' not in x]
PREV = open(os.path.join(HERE, 'areas', 'irrigacao.py'), encoding='utf-8').read()   # a prévia da tela usa a mesma função e a mesma regra
prev_ok = 'const area=irrAreaV2(x,pa);' in PREV and "irrN(cenQtd(n,area),2)" in PREV
okp = lambda x: prev_ok and ok(x) and abs(x['v1'] + x['area'] - x['ha']) < 1e-9 and x['area'] == x['prev'] and round(x['area'], 2) == x['area']
chk(f'8 fertirrigação → O.S. ({len(fa)} v2 de {len(fe)} tentativas, 1 a 50 kg/ha; {len(pc)} com passada em curso): total = regra única, com 2 casas na '
    'mensagem; com passada em curso, a O.S. recebe o que falta com 2 casas (= prévia) e v1 + v2 = área do setor; o saldo apontado zera a custódia',
    len(fa) >= 8 and all(map(ok, fa)) and all(re.search(r'requisição de [0-9.]+(,[0-9]{1,2})? kg', x['msg']) for x in fa) and len(pc) >= 2 and all(map(okp, pc)),
    [x for x in fa if not ok(x)][:4] or [x for x in pc if not okp(x)][:4] or [x['msg'][-90:] for x in fa][:2])
ar = F['area']
na = sum(1 for x in ar if x['antes'])
chk(f'9 "Decidir controle" (agDecIni em {len(ar)} vistorias da Lagoa): abre sem produto nem dose e a área que o formulário preenche nunca passa do talhão '
    f'(com 1 casa, {na} travariam)', len(ar) >= 8 and na >= 1 and all(x['vazio'] for x in ar) and not any(x['trava'] for x in ar), [x for x in ar if x['trava'] or not x['vazio']])
# 10 · varredura de todo o gen37 (JS e JS embutido nos .py, sem testes): produto dose × área fora da regra única. Exceções nomeadas, que não
#      são quantidade de custódia: custo (dose × preço), carga do tanque e demanda do planejamento (CAL-01, exata por desenho).
import glob
PROD = re.compile(r'(?:\b[\w.]*dose\s*\*\s*[\w.(\[\'\]]+|[\w.)\]]+\s*\*\s*[\w.]*\.dose\b|\bd\s*\*\s*(?:ar|ajA)\b'
                  r'|\b(?:[\w.]*area|ar|ajA)\s*\*\s*(?:[\w.]*dose|d)\b|c\[\'area\'\]\s*\*\s*\w*dose)')   # nos dois sentidos (PRE-REV Z5)
EXC = {('areas/inicio.py', 'x.dose*p'): 'custo por ha', ('areas/processo_os.py', 'x.dose*ac'): 'carga do tanque', ('areas/processo_planos.py', 'x.dose*x.preco'): 'custo',
       ('areas/suprimentos.py', "dose*c['area']"): 'demanda do planejamento', ('dados2.py', "dose*c['area']"): 'demanda do planejamento',
       ('safra.js', 'dose*area'): 'demanda do planejamento (CAL-01)',
       ('cal01.js', 'p.dose*ar'): 'demanda do planejamento (CAL-01; CTL-4 DEM-01: a parte do plano sem O.S. saiu do safra.js para demFazenda)'}
bd = F['borda']
chk('11 borda: a liberação reserva com estoque igual à regra única e recusa com 0,01 a menos; dose > 0 com total 0 é recusada; o aviso de compra do MIP usa o lote da liberação',
    bd['exato'] == 'ok' and 'Saldo insuficiente' in bd['falta'] and 'dá 0' in bd['zero'] and 'dá 0' in bd['zero2']
    and bd['mip']['um_lote_exato'] == 0 and bd['mip']['dois_lotes_sem_um_que_cubra'] == 1, bd)
r4 = F['r4']
chk('12 rodada 4: a trava do ajuste do núcleo libera no limite e recusa 0,01 a menos e total 0; o término guarda 20,275 como 20,28 e recusa 0,004; '
    'a v2 com o setor já coberto é recusada com a causa; o MIP trava total 0; a O.S. com total 0 diz "Total 0" e fica com o agrônomo',
    r4['aj'][0] == '' and 'Estoque' in r4['aj'][1] and 'dá 0' in r4['aj'][2] and 'dá 0' in r4['aj'][3] and r4['aj'][4] == ''
    and r4['term'][0] == 20.28 and str(r4['term'][1]).startswith('ERRO') and 'já cobriu o setor' in r4['v2cheia'] and r4['mip0'] == 1
    and r4['rotulo'][0].startswith('Total 0 · ') and 'Falta insumo' not in r4['rotulo'][0] and r4['rotulo'][1] == 'Ana (agrônoma)' and r4['rotulo'][2] == 'ajustar dose ou área', r4)
r5 = F['r5']
chk('13 rodada 5: com total 0, o painel da O.S. aponta o agrônomo (sem Suprimentos nem link do Estoque); "Salvar ajuste" sem liberar recusa total 0; '
    'com outra passada programada, a v2 recusada manda adicionar os produtos às próximas passadas',
    'Ana (agrônoma)' in r5['prox'] and 'Suprimentos' not in r5['prox'] and 'EST.dc.html' not in r5['prox'] and 'dá 0' in r5['ajSemLib']
    and 'próximas passadas' in r5['multi'], r5)
r6 = F['r6']; IRP = open(os.path.join(HERE, 'areas', 'irrigacao.py'), encoding='utf-8').read(); IRJ = open(os.path.join(HERE, 'irrigacao_estado.js'), encoding='utf-8').read()
u1 = r6['u1']; g = r6['guia']
chk('14 rodada 6: avanço de 0,03 e 0,06 ha seguido da v2 encerrada credita o pivô como o avanço 0 (U1); v2 com passada em curso e outra programada é '
    'recusada com a orientação (U2), e pelo término a v2 cobre o setor com a lâmina da passada seguinte e credita; dose ou área 1e999/Infinity vira trava '
    'sem lançar, no MIP e no ajuste (U3); textos com 2 casas no IR-03det e na trilha (U4) e dose da v2 com até 3 casas (U5)',
    all(isinstance(x, list) and x[0] == 'Encerradas' for x in u1) and abs(u1[1][1] - u1[0][1]) < 0.01 and abs(u1[2][1] - u1[0][1]) < 0.01 and not u1[1][2] and not u1[2][2]
    and 'está em curso e há outra programada' in r6['u2'] and 'próximas passadas' in r6['u2']
    and not g['erro'] and abs(g['area'] - g['ha']) < 1e-9 and abs(g['lamHa'] - g['lam2']) < 1e-6 and g.get('et') == 'Encerradas' and g['d1'] < g['d0'] - 1
    and 'Informe a dose' in r6['u3']['dose'] and 'Informe a área' in r6['u3']['area'] and 'Informe a dose' in r6['u3']['inf'] and 'LANÇOU' not in json.dumps(r6['u3'])
    and 'inválida' in r6['u3']['aj']
    and "irrN(pa.cob,1)" not in IRP and "irrN(cob,1)" not in IRP and "' nos ' + irrN(x.ha, 2, 0)" in IRJ and '12,25 kg/ha' in r6['u5'], r6)
EXC_LINHAS = {
    ('areas/custo_dominio.py', "const prHa=(o.ins||[]).reduce((s,x)=>{ const p=cusPreco(D,x.p); if(p===null){ r.pend.push('Sem preço: '+x.p+' (não somado)'); return s; } return s+x.dose*p; },0);"): 'custo por hectare: dose × preço; extraído do Mapa',
    ('cenario.js', "if (!(o.ins||[]).length || o.ins.some(x=>typeof x.dose!=='number'||!Number.isFinite(x.dose)||x.dose<0||!Number.isFinite(x.dose*area)||!Number.isFinite(x.dose*(tanque/vazao)))) return fail('Dose não informada · conferir instrução');"): 'validação de finitude do preparo, sem baixa de custódia',
}
chk('15 guardas de término: cedo e sem hidrômetro recusam sem alterar o estado',
    'Antes do fim previsto' in F['tempo']['cedo'] and F['tempo']['intacto'] and 'volume medido' in F['tempo']['semMedicao'] and F['tempo']['semBaixa'], F['tempo'])
chk('16 calda: cargas fecham a regra única, sem quantidade negativa, nas unidades originais e convertidas; prévia não altera cenário',
    all(x['ok'] and x['intacto'] and abs(x['soma']-x['esperado'])<1e-9 and all(q>=0 for q in x['qs']) for x in R['calda'])
    and R['calda'][0]['qs']==[6.67,6.66,6.67,4.66] and R['calda'][0]['cheia']==6.67
    and R['calda'][1]['qs']==[], R['calda'])
crus = []
for fn in sorted(glob.glob(os.path.join(HERE, '*.js')) + glob.glob(os.path.join(HERE, '*.py')) + glob.glob(os.path.join(HERE, 'areas', '*.py'))):
    rel = os.path.relpath(fn, HERE)
    if re.search(r'(_test|test|_unit|verif_)', os.path.basename(fn)): continue
    for i, ln in enumerate(open(fn, encoding='utf-8'), 1):
        for mm in PROD.finditer(ln):
            if (rel, mm.group(0)) not in EXC and (rel, ln.strip()) not in EXC_LINHAS: crus.append((rel, i, mm.group(0)))
tots = re.findall(r'tot\s*:\s*(?:Math\.round|Number\(|[^,}]*toFixed)', ''.join(open(os.path.join(HERE, n), encoding='utf-8').read() for n in ('mip.js', 'irrigacao_estado.js', 'cenario.js')) + JS_NUCLEO)
chk(f'10 varredura de todo o gen37: nenhum dose × área fora da regra única (exceções nomeadas: {len(EXC)} expressões e {len(EXC_LINHAS)} linhas exatas) e nenhum tot: arredondado por conta própria',
    not crus and not tots, [crus[:6], tots])
print(f'RESULTADO: {sum(OK)}/{len(OK)}')
sys.exit(0 if all(OK) else 1)

