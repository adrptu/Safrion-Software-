'use strict';
// EX47 · revisão Claude: caso-limite latente. Linha fgrp (faixa da fazenda, 1ª célula com span) com ação que vai para o ⋯:
// a Tabela mostra o ⋯; o modo Cartões (g2cdVals: dat = cells.slice(off, off+n)) engole a célula de ação na fatia de dados?
const fs=require('fs'),vm=require('vm');
const c=vm.createContext({console,setTimeout:()=>0,clearTimeout:()=>{}}); vm.runInContext(fs.readFileSync(process.argv[2]||'g2lib.js','utf8'),c);
const COLS=[{k:'nome',l:'Nome'},{k:'q',l:'Qtd',t:'num',a:'r'},{k:'z',l:'Plano'}];
for(const del of [false,true]){
  const rows=[{id:'fz',fgrp:true,v:{nome:'Fazenda',q:1},p:{nome:[{k:'b',t:'Fazenda'},{k:'act',t:'Conferir fazenda',fn:'conf:fz'}]},kids:[{id:'k1',v:{nome:'K1',q:1}}]}];
  const sp={id:'t',cols:COLS,rows,edit:{m:'none'},total:false,tree:true,x0:{fz:true},rmenu:true,del};
  const self={state:{g2:{t:{}}},setState(){}}; const v={conf(){}};
  c.g2vals(self,sp,v); const rw=v.t_rows.find(r=>r.id==='fz'); const last=rw.cells.at(-1);
  c.g2cdVals(self,sp,v); const cd=v.t_cdg.flatMap(s=>s.cards).find(x=>x.id==='fz');
  console.log(`del=${del}: Tabela ⋯=${!!last.rm} itens=${JSON.stringify((last.rmItems||[]).map(i=>i.t))} · cartão existe=${!!cd} · Cartões ações=${(cd&&cd.acts||[]).length}`);
}
