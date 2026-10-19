// N-1 composição (Claude, integrador do PR #113): leitura segura, migração única e migração ao abrir.
// Usa mip.js e o trecho de persistência de cenario.js reais; o armazenamento é um Map sintético.
// Contraprova: MIP_JS=<mip.js anterior> node n1_composicao_test.cjs deve reprovar C1, C3 e C5.
const fs=require('fs'),vm=require('vm');
const mip=fs.readFileSync(process.env.MIP_JS||__dirname+'/mip.js','utf8').split('// ---------- datas (iso')[0];
const CJ=fs.readFileSync(__dirname+'/cenario.js','utf8').split('\n');
// trecho de persistência (linhas 6 a 44) + a marca de migração de Compras que o cenReset chama desde o C-3/C-4 (PR #114)
const cen=CJ.slice(5,44).join('\n')+'\n'+CJ.filter(l=>/^const CEN_COMP_ANTIGA=|^function cenCompMarcar\(/.test(l)).join('\n');
const LEG='talhao-os-mip-v1', CEN='talhao-os-cenario-v1', MARCA=LEG+':migrado';
function env(mode={}){
  const seed={v:1,rev:0,vis:{S1:{id:'S1'}},dia:{},rec:{},seq:{dia:1,rec:1,ra:1},apl:[]};
  const cseed={v:1,rev:4,ordens:{}};
  const legado={v:1,rev:7,vis:{L1:{id:'L1'}},dia:{},rec:{},seq:{dia:1,rec:1,ra:1},apl:[]};
  const disk=new Map([[CEN,JSON.stringify(cseed)]]);
  if(mode.legado!==false) disk.set(LEG,mode.legadoRuim?'{ruim':JSON.stringify(legado));
  const writes=[];
  const ls={getItem:k=>{if(mode.bloqueado)throw Error('SecurityError');return disk.has(k)?disk.get(k):null;},
    setItem:(k,v)=>{if(mode.bloqueado)throw Error('SecurityError');writes.push(k);disk.set(k,v);},
    removeItem:k=>{if(k===LEG)throw Error('a cópia antiga nunca é apagada');disk.delete(k);}};
  const b={MIP0:seed,CEN0:cseed,localStorage:ls};
  vm.createContext(b);vm.runInContext(cen+'\n'+mip,b);
  return {disk,writes,run:s=>vm.runInContext(s,b)};
}
let ok=0,falhas=0;
function caso(nome,f){ try{ f(); ok++; console.log('OK    '+nome); }catch(e){ falhas++; console.log('FALHA '+nome+': '+(e.message||e)); } }
function exige(c,m){ if(!c) throw new Error(m); }
caso('C1 cópia antiga ilegível: a leitura não derruba a tela, mostra o aviso e nenhuma vistoria; gravar segue recusado e a cópia fica igual',()=>{
  const x=env({legadoRuim:true}); let s; try{ s=x.run('mipGet()'); }catch(e){ throw new Error('mipGet lançou: '+e.message); }
  exige(Object.keys(s.vis).length===0,'mostrou vistorias');
  exige(/ilegíveis/.test(x.run('typeof mipErro==="function"?mipErro():""')),'sem aviso');
  const r=x.run("mipMudar(null,s=>{s.vis.V9={id:'V9'};return {msg:'ok'}})"); exige(r.erro,'gravou com a cópia ilegível');
  exige(x.disk.get(LEG)==='{ruim','a cópia antiga mudou'); exige(x.writes.length===0,'houve gravação');
});
caso('C2 armazenamento bloqueado: a leitura mostra a semente sem erro',()=>{
  const x=env({bloqueado:true}); let s; try{ s=x.run('mipGet()'); }catch(e){ throw new Error('mipGet lançou: '+e.message); }
  exige(s.vis.S1,'não mostrou a semente');
});
caso('C3 migração única: depois de migrar, recomeçar o cenário (Restaurar demonstração em outra tela) volta à semente, não à cópia antiga',()=>{
  const x=env(); const r=x.run("mipMudar(null,s=>{s.vis.N1={id:'N1'};return {msg:'ok'}})"); exige(!r.erro,r.erro);
  exige(JSON.parse(x.disk.get(CEN)).mip.vis.L1,'não migrou a cópia antiga');
  x.run('cenReset()');   // Restaurar demonstração em outra tela (Estoque, O.S., app)
  const s=x.run('mipGet()'); exige(!s.vis.L1&&s.vis.S1,'a cópia antiga voltou depois de recomeçar o cenário');
});
caso('C4 Restaurar demonstração com a cópia antiga ilegível: grava a semente e preserva a cópia sem alteração',()=>{
  const x=env({legadoRuim:true}); const r=x.run('mipReset()'); exige(!r.erro,'restaurar recusou: '+r.erro);
  const c=JSON.parse(x.disk.get(CEN)); exige(c.mip&&c.mip.vis.S1,'o cenário não ficou com a semente');
  exige(x.disk.get(LEG)==='{ruim','a cópia antiga mudou'); exige(!x.run('mipErro()'),'o aviso continuou depois de restaurar');
});
caso('C5 abrir uma tela de Pragas e doenças migra a cópia antiga uma vez (mipOuvir), sem gravar de novo na segunda tela',()=>{
  const x=env(); x.run('mipOuvir({setState(){}})');
  const c=JSON.parse(x.disk.get(CEN)); exige(c.mip&&c.mip.vis.L1&&c.mip.migradoDe&&c.mip.migradoDe.rev===7,'não migrou ao abrir');
  exige(x.disk.has(MARCA),'sem a marca de migração'); const n=x.writes.length;
  x.run('mipOuvir({setState(){}})'); exige(x.writes.length===n,'gravou de novo na segunda tela');
});
caso('C6 abrir com a cópia antiga ilegível não grava nada e mantém o aviso',()=>{
  const x=env({legadoRuim:true}); x.run('mipOuvir({setState(){}})'); exige(x.writes.length===0,'gravou'); x.run('mipGet()');
  exige(/ilegíveis/.test(x.run('mipErro()')),'sem aviso');
});
caso('C7 sem cópia antiga: abrir não grava (a primeira gravação real leva a semente ao cenário)',()=>{
  const x=env({legado:false}); x.run('mipOuvir({setState(){}})'); exige(x.writes.length===0,'gravou ao abrir sem cópia antiga');
});
console.log('RESULTADO: '+ok+' ok · '+falhas+' falhas');
process.exitCode=falhas?1:0;
