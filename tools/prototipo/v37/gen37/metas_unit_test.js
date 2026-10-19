const fs=require('fs'),vm=require('vm'),assert=require('assert');
const box={}; vm.createContext(box);vm.runInContext(fs.readFileSync(__dirname+'/metas.js','utf8'),box);
const c={conf:{metas:{}}}, id='KPI-PCM-05';
function cor(x,m,partial=false,un='%'){const key=m&&m.sentido==='menor'?'custo-desvio':id;c.conf.metas[key]=m;return box.metaAvaliar(c,key,x,un,partial).cor;}
const m={valor:90,atencao:80,sentido:'maior',un:'%',escopo:'organizacao',v:1};
assert.equal(cor(100,null),'gray'); assert.equal(cor(0,m),'red');
assert.equal(cor(80,m),'yellow');assert.equal(cor(90,m),'green');
assert.equal(cor(null,m),'gray');assert.equal(cor(100,m,true),'gray');assert.equal(cor(100,m,false,'h'),'gray');
assert.equal(cor(100,{...m,ativa:false}),'gray');assert.equal(cor(100,{...m,atencao:91}),'gray');
assert.equal(cor(100,{...m,valor:'90'}),'gray');assert.equal(cor(100,{...m,valor:Infinity}),'gray');
assert.equal(cor(0,{valor:0,atencao:5,sentido:'menor',un:'%',escopo:'organizacao'}),'green');
assert.equal(cor(5,{valor:0,atencao:5,sentido:'menor',un:'%',escopo:'organizacao'}),'yellow');
assert.equal(cor(6,{valor:0,atencao:5,sentido:'menor',un:'%',escopo:'organizacao'}),'red');
c.conf.metas[id]=m;box.metaDe(c,id).valor=1;assert.equal(m.valor,90);
assert.equal(box.metaDe(c,'inexistente'),null);assert.equal(cor(100,{...m,escopo:'fazenda'}),'gray');assert.equal(box.metaValida(id,{...m,sentido:'menor',atencao:95}),false);
console.log('PASS: ausência, zero, fronteiras, retirada, unidade, parcial, inválidos e leitura imutável.');
