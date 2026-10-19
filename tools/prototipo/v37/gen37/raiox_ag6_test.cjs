const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const c={window:{},MIPD:{prot:{P:{un:'alvos/ponto',crit:'nc',nc:10,chave:'alvo'}},tal:{T:{fase:'demo'}}}};
vm.createContext(c);vm.runInContext(fs.readFileSync(__dirname+'/mip.js','utf8')+fs.readFileSync(__dirname+'/areas/agronomia.py','utf8').split('function ag6Rows')[1].split("'''")[0].replace(/^/,'function ag6Rows'),c);
const s={vis:{V:{id:'V',tal:'T',prot:'P',data:'2026-01-01',est:'concluida',npts:1,pts:[{n:1,v:0,ok:true}],pend:[],dec:{rec:'REC-014'}}},rec:{'REC-014':{vis:'V'}},apl:[]};
const before=JSON.stringify(s);let rows=c.ag6Rows(s,null);assert.equal(rows.length,5);const row=rows.find(x=>x.id==='EF-020');
assert.equal(row.v.res,'Sem leitura pós');assert.match(row.p.rec[2].t,/Pré: 0/);assert.equal(row.p.acao[0].h,'AG-01.dc.html#V');
assert.equal(row.ro,true);assert.equal(row.v.custo,null);assert.equal(JSON.stringify(s),before);
assert.equal(rows.find(x=>x.id==='EF-019').v.res,'Fonte não vinculada');
s.vis.V.dec.rec='REC-999';assert.equal(c.ag6Rows(s,null).find(x=>x.id==='EF-020').v.res,'Fonte não vinculada');
s.vis.V.dec.rec='REC-014';s.vis.V.dec.pos='POS';s.vis.POS={...s.vis.V,id:'POS',pos_de:'V',est:'programada',pts:[{n:1,v:null,ok:true}]};
rows=c.ag6Rows(s,null);assert.equal(rows.find(x=>x.id==='EF-020').v.res,'Leitura pós pendente');
s.vis.POS.est='concluida';s.vis.POS.pts[0].v=2;assert.equal(c.ag6Rows(s,null).find(x=>x.id==='EF-020').v.res,'Histórico indisponível');
console.log('PASS AG06: cinco IDs preservados, vínculo atual, origem navegável, zero, pós pendente/concluído, ausência sem percentual, imutabilidade');

s.vis.V.est='coleta';rows=c.ag6Rows(s,null);assert.equal(rows.find(x=>x.id==='EF-020').v.res,'Leitura pré pendente');
s.vis.V.est='concluida';s.vis.POS.est='programada';rows=c.ag6Rows(s,null);assert.equal(rows.find(x=>x.id==='EF-020').p.acao[0].h,'AG-01.dc.html#POS');
assert.equal(rows.find(x=>x.id==='EF-020').p.acao[0].t,'Conferir leitura pós');
console.log('PASS recuperação: pré incompleta tem prioridade e pós pendente abre a própria fonte');
