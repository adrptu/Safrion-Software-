const fs=require('fs'); global.window={addEventListener(){}}; global.localStorage={getItem(){return null},setItem(){},removeItem(){}};
global.location={pathname:'',search:'',hash:''}; global.history={replaceState(){}};
eval(fs.readFileSync('man_prefix.js','utf8')+'\n;global.__M={manGet,manClone,manGerarTodas,manFalta,manLiberar,manCusto,manLinhas};');
const M=global.__M; const c=M.manClone(M.manGet());
const r=M.manGerarTodas(c); console.log(r.msg);
['OM-0235','OM-0236','OM-0237'].forEach(id=>{ const o=c.oms[id]; console.log(id,o.aid,o.pid,o.serv,o.crit,'jan',o.jan,'tempo',o.tempo,JSON.stringify(o.pecas.map(p=>[p.item,p.qtd,p.un,p.preco])), 'falta',M.manFalta(c,o).map(p=>p.item)); });
const l=M.manLinhas(c).filter(x=>x.s&&(x.x.sit==='Vencida'||x.x.sit==='Vence em breve')); l.forEach(x=>console.log(x.pid,x.aid,x.sid,x.x.sit,x.x.prev, x.om&&x.om.id));
