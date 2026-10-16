(()=>{
let fail=0,total=0;
const test=(t,f)=>{total++;try{cenReset();f();console.log('OK '+t);}catch(e){fail++;console.log('FALHA '+t+': '+e.message);}};
const exigir=(c,m)=>{if(!c)throw Error(m);};
test('data do cenário conserva data operacional da configuração e produção',()=>exigir(CEN_DIA_OP===DATA_CANONICA&&CEN_DIA_OP===DATA_PRODUCAO,JSON.stringify({cenario:CEN_DIA_OP,config:DATA_CANONICA,producao:DATA_PRODUCAO})));
test('Estoque usa a mesma data operacional sem reaproveitar data do planejamento',()=>exigir(eiso(E2.hoje)===DATA_CANONICA,'Estoque='+E2.hoje+' configuração='+DATA_CANONICA));
test('novo turno e apontamento preservam 26/09, sem antecipar três dias',()=>{
 const c=cenGet();cenIniciarTurno(c,'OS-0421');const d=c.app.turno.d,chave=c.app.turno.chave;
 cenFecharTurno(c,1,1,undefined,'',[]);const ap=c.ordens['OS-0421'].ap.find(a=>a.chave===chave);
 exigir(d==='26/09'&&ap&&ap.d==='26/09',JSON.stringify({turno:d,ap:ap&&ap.d}));
});
console.log('RESULTADO '+(total-fail)+'/'+total);if(fail)process.exitCode=1;
})();
