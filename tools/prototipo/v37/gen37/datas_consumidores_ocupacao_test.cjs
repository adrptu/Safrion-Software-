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

// EX57: o painel Por quê compartilhado por AG-02/SAF também precisa explicar a data ausente.
// Carrega as funções reais do painel e de formatação, sem reimplementar a regra no teste.
c.CEN0={diaOperacional:'2026-10-19'};
vm.runInContext(fs.readFileSync(root+'cenario.js','utf8')+'\n'+fs.readFileSync(root+'producao.js','utf8'),c);
const ui=fs.readFileSync(root+'areas/analise_solo.py','utf8').match(/SOLO_UI_JS=r'''([\s\S]*?)'''/);
assert.ok(ui,'SOLO_UI_JS recuperável');vm.runInContext(ui[1],c);
const casos=[
  [null,{g:{tipo:'DAP'}},'', 'Data: aguarda plantio'],
  [null,{g:{tipo:'DAPC'}},'', 'Data: aguarda colheita'],
  [null,{g:{tipo:'DANC'}},'', 'Data: aguarda colheita'],
  [null,{g:{tipo:'DATA'}},'', 'Data: aguarda data válida'],
  [null,{},'', 'Data: aguarda data válida'],
  ['2026-11-01',{g:{tipo:'DAPC'}},'', 'Data: 01/11/2026'],
  [null,{g:{tipo:'DAPC'}},'atividade encerrada', 'Data: aguarda colheita · não aplicável: atividade encerrada'],
];
for(const [dt,atv,nega,esperado] of casos){
  c.sug={tipo:'ajustar',ef:1,sug:2,padrao:1,un:'kg',dif:10,custo:50,preco:5,dt,atv,nega};
  const antes=JSON.stringify(c.sug);
  assert.deepStrictEqual(run("soEfeito(sug,{area:10,local:'T1'})"),[
    'Dose: 1 kg/ha → 2 kg/ha (padrão 1 kg/ha)',
    'Quantidade no T1 (10 ha): +10 kg',
    'Custo de insumos: +R$ 50 (preço R$ 5/kg)',
    esperado,
  ]);
  assert.equal(JSON.stringify(c.sug),antes,'Apresentar ausência não altera a sugestão');
}
console.log('7/7 painel Por quê: âncora ausente/real, negação, dose/quantidade/custo e imutabilidade');

// Regressão PR136/4313097025: a sugestão real guarda só id/nome/op, sem g.
// Todos os consumidores precisam receber o gatilho da atividade que originou a sugestão.
c.PRDC={un:{Teste:{}}};
vm.runInContext(`var contextoReal={S0:{hoje:'2026-10-19',regra:{v2:{Teste:60},k:{culturas:[]}},gar:{Calcario:{prnt:80}}},
  ls:[{id:'L',tipo:'solo',sit:'Validado',faz:'F',tal:'T',prof:'0–20',idx:{T:{v:5},V:{v:40}}}]};`,c);
for(const [tipo,dt,esperado] of [
  ['DAP',null,'Data: aguarda plantio'],['DAPC',null,'Data: aguarda colheita'],
  ['DANC',null,'Data: aguarda colheita'],['DATA',null,'Data: aguarda data válida'],
  ['DAPC','2026-11-01','Data: 01/11/2026'],
]){
  c.cultivoReal={id:'C',saf:'S',faz:'F',tal:'T',local:'T',cultura:'Teste',area:10,
    plano:{id:'P',versao:1,atividades:[{id:7,nome:'Calagem',op:'Adubação',g:{tipo},
      prods:[{prod:'Calcario',dose:1,un:'t',preco:100}]}]},dt:()=>dt};
  const antes=JSON.stringify(c.cultivoReal);
  const got=run("soloSugestoes(contextoReal,cultivoReal).sug");
  assert.equal(got.length,1,'O caso precisa passar pelo construtor real da calagem');
  c.sugReal=got[0];
  assert.equal(run('soloDataTexto(sugReal.dt,sugReal.atv)'),esperado.slice(6),'O consumidor SAF também recebe a âncora');
  c.sugReal=got[0];const antesSug=JSON.stringify(c.sugReal);
  assert.deepStrictEqual(run('soEfeito(sugReal,cultivoReal)'),[
    'Dose: 1,00 t/ha → 1,25 t/ha (padrão 1,00 t/ha)',
    'Quantidade no T (10 ha): +2,5 t',
    'Custo de insumos: +R$ 250 (preço R$ 100/t)',esperado,
  ]);
  assert.equal(JSON.stringify(c.cultivoReal),antes);
  assert.equal(JSON.stringify(c.sugReal),antesSug);
}
console.log('5/5 sugestão real → painel: ID numérico/texto, DAP/DAPC/DANC/DATA, data válida e valores preservados');
