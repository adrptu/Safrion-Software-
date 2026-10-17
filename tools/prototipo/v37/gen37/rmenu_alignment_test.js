'use strict';
// EX47 · revisão Claude do PR #93: sonda Node sobre o g2lib.js completo (sem mocks de funções do motor).
// Uso: node sonda_rmenu_alinhamento.js <g2lib HEAD> <g2lib base>
// Mede, em rmenu × del × sel × modo árvore, para linhas normal/ro/livre/fora/nosel/fgrp/xdel/filho, com e sem ações:
//  A1 alinhamento: soma dos spans das células de cada linha == _ncols (trilhas da grade);
//  A2 ações alcançáveis: toda ação não-navegação sai da célula e está no ⋯ (rmenu) ou fica na célula (sem rmenu); navegação fica na célula;
//  A3 Excluir só com del e linha permitida; nunca sem del; xdel só no item Excluir;
//  A4 sem controle vazio: ⋯ só com itens; célula estrutural sem botão (isDel=false, sem trash/rm);
//  A5 confirmação: cf obsoleto não pergunta em grade sem exclusão nem em linha protegida;
//  A6 caminho antigo (sem rmenu): células idênticas às da base (JSON, sem funções), com e sem del/sel;
//  A7 Cartões (g2cdVals): ações do cartão = células com isDel; nenhuma célula estrutural vira ação; o ⋯ da Tabela aparece no cartão.
const fs=require('fs'),vm=require('vm'),path=require('path');
const [HEAD,BASE]=[process.argv[2],process.argv[3]];
function ctx(f){ const c=vm.createContext({console,setTimeout:()=>0,clearTimeout:()=>{}}); vm.runInContext(fs.readFileSync(f,'utf8'),c); return c; }
const CH=ctx(HEAD), CB=BASE?ctx(BASE):null;
const act=(t,fn)=>({k:'act',t,fn}); const nav=(t,fn)=>({k:'act',t:t+' ›',fn,lk:true});
function mkRows(){ return [
  {id:'a',v:{nome:'A normal',q:1},p:{nome:[{k:'b',t:'A normal'},act('Conferir','conf:a'),nav('Abrir','ir:a')]}},
  {id:'b',v:{nome:'B sem ação',q:2}},
  {id:'c',ro:true,v:{nome:'C ro',q:3},p:{z:[act('Reaplicar','conf:c')]}},
  {id:'d',ro:true,v:{nome:'D ro sem ação',q:4}},
  {id:'e',livre:true,v:{nome:'E livre',q:5},p:{nome:[{k:'b',t:'E livre'},act('Planejar','conf:e')]}},
  {id:'f',fora:true,v:{nome:'F fora',q:6}},
  {id:'g',nosel:true,v:{nome:'G nosel',q:7},p:{nome:[{k:'b',t:'G nosel'},act('Voltar a planejar','conf:g')]}},
  {id:'x',xdel:'xd',v:{nome:'X outra fazenda',q:8},p:{nome:[{k:'b',t:'X outra fazenda'},act('Dividir','conf:x')]}},
  {id:'fz',fgrp:true,nosel:true,ro:true,v:{nome:'Fazenda',q:9},p:{nome:[{k:'b',t:'Fazenda'},nav('Planejar talhões livres','ir:fz')]},
   kids:[{id:'k1',v:{nome:'K1 filho',q:1},p:{nome:[{k:'b',t:'K1 filho'},act('Aplicar plano','conf:k1')]}},{id:'k2',fora:true,v:{nome:'K2 fora',q:1}}]},
]; }
const COLS=[{k:'nome',l:'Nome'},{k:'q',l:'Qtd',t:'num',a:'r',agg:'sum'},{k:'z',l:'Plano'}];
function render(C,o,state){ let called=[];
  const sp=Object.assign({id:'t',cols:COLS,rows:mkRows(),edit:{m:'none'},total:true,tree:true,so:{}},o);
  // TAB-12 (17/10/2026): a faixa fz nasce recolhida; a sonda a abre como a seta abriria (st.x), para medir as linhas filhas
  const self={state:{g2:{t:Object.assign({x:{fz:true}},state||{})}},setState(x){Object.assign(this.state,x);}};
  const v={conf:x=>called.push('conf:'+x),ir:x=>called.push('ir:'+x),xd:x=>called.push('xd:'+x)};
  C.g2vals(self,sp,v); return {v,sp,self,called}; }
const span=c=>{ const m=/grid-column:span (\d+)/.exec(c.st||''); return m?+m[1]:1; };
const isNav=p=>p&&p.k==='act'&&/›\s*$/.test(String(p.t||''));
let ok=0, falhas=[]; const chk=(n,c,d)=>{ if(c) ok++; else { falhas.push(n+' · '+String(JSON.stringify(d)).slice(0,300)); } };
function allRows(rs){ const out=[]; const w=l=>(l||[]).forEach(r=>{ out.push(r); w(r.kids); }); w(rs); return out; }
const RAW=allRows(mkRows()); const byId=Object.fromEntries(RAW.map(r=>[r.id,r]));
for(const rmenu of [false,true]) for(const del of [false,true]) for(const sel of [false,true]){
  const tag=`rmenu=${rmenu} del=${del} sel=${sel}`;
  const {v}=render(CH,{rmenu,del,sel});
  const n=v.t_ncols; chk(tag+' A1 _ncols',n===COLS.length+(sel?1:0)+((rmenu||del)?1:0),n);
  const vis=v.t_rows; chk(tag+' linhas visíveis (fgrp aberto, filhos)',vis.length===RAW.length,vis.map(r=>r.id));
  for(const rw of vis){ const r=byId[rw.id]; const tg=tag+' '+rw.id;
    const soma=rw.cells.reduce((a,c)=>a+span(c),0); chk(tg+' A1 alinhamento',soma===n,{soma,n,cells:rw.cells.length});
    const last=rw.cells[rw.cells.length-1]; const temCol=(rmenu||del);
    const acts=Object.values(r.p||{}).flat().filter(p=>p&&p.k==='act');
    const naoNav=acts.filter(p=>!isNav(p)), navs=acts.filter(isNav);
    const partsT=rw.cells.filter(c=>c.isData).flatMap(c=>(c.parts||[]).map(p=>String(p.t||'')));
    const protegida=!!(r.livre||r.fora||r.nosel||r.ro);
    if(rmenu){
      for(const p of navs) chk(tg+' A2 navegação fica na célula',partsT.includes(p.t),{p:p.t,partsT});
      for(const p of naoNav) chk(tg+' A2 ação no ⋯',!partsT.includes(p.t)&&last.rm&&(last.rmItems||[]).some(i=>i.t===p.t),{p:p.t,last:{rm:last.rm,its:(last.rmItems||[]).map(i=>i.t)}});
      const temExc=!!(last.rm&&(last.rmItems||[]).some(i=>i.t==='Excluir'));
      chk(tg+' A3 Excluir só com del e linha permitida',temExc===(del&&!protegida),{temExc,del,protegida});
      if(last.rm) chk(tg+' A4 ⋯ com itens',(last.rmItems||[]).length>0,last.rmItems);
      else chk(tg+' A4 célula estrutural sem controle',!last.isDel&&!last.trash&&!last.rm&&!last.isData&&!last.isSel,last);
      if(last.rm) chk(tg+' A4 rótulo do ⋯',last.rmLabel==='Mais ações de '+r.v.nome,last.rmLabel);
    } else {
      for(const p of acts) chk(tg+' A2 sem rmenu a ação fica na célula',partsT.includes(p.t),{p:p.t,partsT});
      if(del){ const trash=!!last.trash; chk(tg+' A3 lixeira legada (como na base)',trash===!(r.livre||r.fora||r.nosel),{trash}); }
    }
    if(!temCol) chk(tg+' sem coluna de ações, a última célula é de dado',!!last.isData,last);
  }
  // A5: cf obsoleto em cada linha
  for(const r of RAW){ const {v:v2}=render(CH,{rmenu,del,sel},{cf:r.id}); const rw=v2.t_rows.find(x=>x.id===r.id); const last=rw.cells[rw.cells.length-1];
    const protegida=!!(r.livre||r.fora||r.nosel||r.ro);
    const esperado=rmenu?(del&&!protegida):(del&&!(r.livre||r.fora||r.nosel));
    chk(tag+' '+r.id+' A5 pergunta "Excluir?" só onde excluir é permitido',!!last.asking===esperado,{asking:last.asking,esperado}); }
  // A6: caminho antigo idêntico à base
  if(CB&&!rmenu){ const b=render(CB,{rmenu,del,sel}).v; const s=x=>JSON.stringify({n:x.t_ncols,rows:x.t_rows.map(r=>({id:r.id,cls:r.cls,cells:r.cells}))});
    chk(tag+' A6 caminho antigo idêntico à base',s(v)===s(b),'difere'); }
  // A7: Cartões
  CH.g2cdVals({state:{g2:{t:{x:{fz:true}}}},setState(){}},Object.assign({id:'t',cols:COLS,rows:mkRows(),edit:{m:'none'},total:true,tree:true,so:{}},{rmenu,del,sel}),v);
  const cards=[]; (v.t_cdg||[]).forEach(s=>s.cards.forEach(cd=>{ cards.push(cd); (cd.kids||[]).forEach(k=>cards.push(k)); }));
  for(const cd of cards){ const rw=vis.find(x=>x.id===cd.id); const last=rw.cells[rw.cells.length-1];
    chk(tag+' '+cd.id+' A7 cartão sem ação estrutural',(cd.acts||[]).every(c=>c.isDel),cd.acts);
    if(last.rm||last.trash) chk(tag+' '+cd.id+' A7 a ação da Tabela está no cartão',(cd.acts||[]).length===1,{acts:(cd.acts||[]).length,rm:last.rm,trash:last.trash}); }
}
// chamada parametrizada e xdel
try{ const R=render(CH,{rmenu:true,del:false}); const ita=R.v.t_rows.find(r=>r.id==='a').cells.at(-1).rmItems; ita[0].fn(); chk('chamada parametrizada conf:a',R.called.includes('conf:a'),R.called);
  const itx=R.v.t_rows.find(r=>r.id==='x').cells.at(-1).rmItems.map(i=>i.t); chk('xdel sem del: só Dividir, sem Excluir',JSON.stringify(itx)==='["Dividir"]',itx);
  const R2=render(CH,{rmenu:true,del:true}); const its2=R2.v.t_rows.find(r=>r.id==='x').cells.at(-1).rmItems; its2.at(-1).fn(); chk('xdel com del: Excluir chama a grade da linha',its2.at(-1).t==='Excluir'&&R2.called.includes('xd:x'),R2.called); } catch(e){ chk('chamada/xdel sem exceção',false,String(e)); }
// base × HEAD com rmenu e del: onde muda
if(CB){ const h=render(CH,{rmenu:true,del:true}).v, b=render(CB,{rmenu:true,del:true}).v; const dif=[];
  h.t_rows.forEach((r,i)=>{ const x=JSON.stringify(r.cells.at(-1)), y=JSON.stringify(b.t_rows[i].cells.at(-1)); if(x!==y) dif.push({id:r.id,head:JSON.parse(x),base:JSON.parse(y)}); });
  console.log('rmenu+del: linhas cuja célula de ação muda da base para o HEAD:',dif.map(d=>d.id+' base['+(d.base.trash?'lixeira':d.base.rm?'⋯':'vazia')+'] → HEAD['+(d.head.trash?'lixeira':d.head.rm?'⋯':'vazia')+']').join(', ')||'nenhuma'); }
// A1 retornado: nenhuma ação em qualquer linha => sem coluna; filtros podem mudar isso.
for(const sel of [false,true]) for(const ro of [false,true]){
 const rows=[{id:'vazio',ro,v:{nome:'Só consulta',q:1}}];
 const R=render(CH,{rmenu:true,del:false,sel,rows});
 chk('sem ações: flag falsa',R.v.t_acoes===false,R.v.t_acoes);
 chk('sem ações: trilhas sem coluna extra',R.v.t_ncols===COLS.length+Number(sel),R.v.t_ncols);
 R.v.t_rows.forEach(r=>chk('sem ações: spans alinhados',r.cells.reduce((a,c)=>a+span(c),0)===R.v.t_ncols,r.cells));
}
const filtered=render(CH,{rmenu:true,del:false},{q:'D ro sem ação'});
chk('filtro só consulta remove coluna',filtered.v.t_acoes===false&&filtered.v.t_rows.length===1,filtered.v.t_acoes);
const empty=render(CH,{rmenu:true,del:false,rows:[]});
chk('grade vazia sem coluna de ações',empty.v.t_acoes===false&&empty.v.t_ncols===COLS.length,empty.v.t_ncols);
console.log(`sonda EX47: ${ok} OK, ${falhas.length} falhas`); falhas.slice(0,40).forEach(f=>console.log('FALHA '+f));
process.exit(falhas.length?1:0);

