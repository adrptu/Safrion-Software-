const fs=require('fs'),vm=require('vm'),assert=require('assert');
const src=fs.readFileSync(__dirname+'/robot.html','utf8');
const code=src.slice(src.indexOf('const ENT_SRC'),src.indexOf('const LABENT'));
const ctx={topDlg:d=>d.dialog,dTitle:(_,d)=>d?.title||'',vis:()=>true};vm.createContext(ctx);vm.runInContext(code,ctx);
const target=(raw,h,t)=>ctx.expectedTarget({getAttribute:()=>raw},{h,t});
assert.equal(target(null,'OS.dc.html#OS-0502','Abrir').id,'OS-0502');
assert.equal(target(null,'OS.dc.html#OS-0502','OS-0503').id,'');
assert.equal(target(null,'OS.dc.html','Abrir').id,'');
assert.equal(target('{"t":"os","id":"OS-0502"}','OS.dc.html#OS-0503','Abrir').id,'OS-0502');
assert.equal(target(null,'X#RA-0012','Abrir').id,'RA-0012');
assert.equal(target(null,'X#CMD-0012','CMD-0012 EX-0012 DEC-0012').id,'');
assert(ctx.exactId('Registro OS-0502 aberto','OS-0502'));assert(!ctx.exactId('OS-05020','OS-0502'));
assert(!ctx.exactId('XOS-0502','OS-0502'));
const doc=(title,rows=[])=>({dialog:title?{title}:null,querySelector:()=>null,querySelectorAll:()=>rows.map(innerText=>({innerText}))});
assert(!ctx.arrival(doc('OS-0503'),{id:'OS-0502'}).abriu);
assert(ctx.arrival(doc('OS-0502'),{id:'OS-0502'}).abriu);
assert(!ctx.arrival(doc(null),{id:'OS-0502'}).destacou);
assert(ctx.arrival(doc(null,['OS-0502 selecionada']),{id:'OS-0502'}).destacou);
console.log('PASS 13 contraprovas do oráculo JS real: alvo errado/ambíguo/ausente, prefixos, igualdade e painel/seleção. Sem navegador.');

assert.equal(target(null,'EST.dc.html?de=OS.dc.html%23OS-0502#ent=REQ-039','Abrir').id,'REQ-039');
assert.equal(target(null,'MA.dc.html?de=OS.dc.html%23OS-0420#vis=ordens','Abrir').id,'');
const page=doc(null);page.querySelector=()=>({innerText:'Registro OS-0502'});assert(ctx.arrival(page,{id:'OS-0502'}).abriu);
page.dialog={title:''};assert(!ctx.arrival(page,{id:'OS-0502'}).abriu);
console.log('PASS A2/A3: query de não fornece alvo; h1 somente sem diálogo.');

assert(!ctx.exactId('OS-0502/2','OS-0502'));assert(!ctx.exactId('PC-0012 · da OS-0502','OS-0502'));assert.equal(target(null,'EST#dev=saldo&para=OS-0502','Abrir').id,'');console.log('PASS A10 limites e entidade primária');
