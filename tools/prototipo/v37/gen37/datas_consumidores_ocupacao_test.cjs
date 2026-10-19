const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=__dirname+'/';
const c=vm.createContext({});vm.runInContext(fs.readFileSync(root+'datas_atividade.js','utf8')+'\n'+fs.readFileSync(root+'ocupacao.js','utf8'),c);
const run=s=>JSON.parse(JSON.stringify(vm.runInContext(s,c)));
vm.runInContext(`var pl={id:'P',cultura:'Teste',atividades:[{nome:'Após',op:'Adubação',g:{tipo:'DAPC',dias:2}},{nome:'Antes',op:'Adubação',g:{tipo:'DANC',dias:3}}]};var ctx=ocCtx({Teste:'Anual'},[],[pl]);var plantio=ocDia('2026-10-01');`,c);
assert.deepStrictEqual(run("ocAtividades(ctx,plantio,'P')"),[['Após','DAPC',null],['Antes','DANC',null]]);
assert.deepStrictEqual(run("ocDatasValidas(ctx,plantio,'P',plantio,plantio+365)"),[[],[]]);
assert.equal(run("ocFimEstimado(ctx,'Teste','',plantio)"),null);
assert.deepStrictEqual(run("ocAtividades(ctx,plantio,'P',ocDia('2026-11-01')).map(x=>ocIso(x[2]))"),['2026-11-03','2026-10-29']);
vm.runInContext("pl.atividades.push({nome:'Colher',op:'Colheita',g:{tipo:'DATA',data:'2026-11-01'}})",c);
assert.deepStrictEqual(run("ocAtividades(ctx,plantio,'P').map(x=>ocIso(x[2]))"),['2026-11-03','2026-10-29','2026-11-01']);
vm.runInContext("var pend=[];ocDatasValidas(ctx,plantio,'P',plantio,plantio+365,null,pend)",c);
assert.deepStrictEqual(run('pend'),[]);
vm.runInContext("pl.atividades.pop();ocDatasValidas(ctx,plantio,'P',plantio,plantio+365,null,pend)",c);
assert.deepStrictEqual(run('pend'),[['ancora_ausente','Após','DAPC'],['ancora_ausente','Antes','DANC']]);
console.log('7/7 ocupação: ausência não vira plantio/zero; âncora informada/plano canônica');

vm.runInContext(fs.readFileSync(root+'solo.js','utf8'),c);
assert.equal(run("soloDataTexto(null,{g:{tipo:'DAPC'}})"),'aguarda colheita');
assert.equal(run("soloDataTexto(null,{g:{tipo:'DAP'}})"),'aguarda plantio');
assert.equal(run("soloDataTexto(null,{g:{tipo:'DATA'}})"),'aguarda data válida');
assert.equal(run("soloDataTexto('2026-11-01',{g:{tipo:'DAPC'}})"),'01/11/2026');
console.log('4/4 rótulos de análise do solo preservam data ou explicam ausência');

vm.runInContext("var o=ocMk(ctx,{id:'c',saf:'S',faz:'F',faixa:'T',tipo:'Talhão inteiro',area:1,cult:'Teste',plantio:'2026-10-01',plano:'P'},{id:'S',ini:'2026-01-01',fim:'2026-12-31'})",c);
assert.equal(run('o.fim'),null);
assert.equal(run('o.classe'),'semdata');
assert.equal(run('ocP(ctx,o)'),100000000);
console.log('3/3 plano sem âncora não inventa fim nem liberação confirmada');

vm.runInContext("var known=ocMk(ctx,{id:'c',saf:'S',faz:'F',faixa:'T',tipo:'Talhão inteiro',area:1,cult:'Teste',plantio:'2026-10-01',plano:'P',colheita:'2026-11-01'},{id:'S',ini:'2026-01-01',fim:'2026-12-31'})",c);
assert.equal(run('known.classe'),'plano');
assert.equal(run('ocIso(known.fim)'),'2026-11-03');
console.log('2/2 informar âncora restaura fim canônico do plano');
